"""Deterministic, read-only update plan construction and recomputation."""

from __future__ import annotations

from pathlib import Path

from tools.aeterna_artifacts.generation import DOCUMENT_INDEX_PATH, REGISTRY_PATH, GenerationBlockedError, build_generated_content
from tools.aeterna_artifacts.model import Severity
from tools.aeterna_artifacts.scanner import validate_record_set

from .adapters import body_diff, metadata_differences
from .impact import build_impact
from .model import MetadataDelta, PreparedUpdate, ReferenceChange, UpdateManifest, WorkflowError, fail
from .preflight import load_manifest, run_preflight_manifest
from .resolver import record_payload
from .review import plan_semantic_digest


_PROTECTED_FIELDS = frozenset({"artifact_id", "path", "authority", "kind", "type", "generated", "supersedes"})
_EXPLICIT_MUTABLE_FIELDS = frozenset({"version", "lifecycle", "integration", "depends_on"})


def _validate_version(
    context: object,
    actual_delta: tuple[dict[str, object], ...],
    declared_delta: tuple[dict[str, object], ...],
) -> None:
    intent = context.manifest.version_intent
    current = context.resolved.record.version
    candidate = context.candidate_record.version
    proposed = context.manifest.proposed_version
    actual_versions = [item for item in actual_delta if item["field"] == "version"]
    declared_versions = [item for item in declared_delta if item["field"] == "version"]
    if intent == "git-only":
        if candidate != current or actual_versions or declared_versions:
            fail("VERSION_INTENT_CONFLICT", "git-only cannot change document version.")
        if proposed not in {None, current}:
            fail("PROPOSED_VERSION_MISMATCH", "git-only proposed_version must be null or current.")
        return
    if not declared_versions:
        fail("VERSION_DELTA_REQUIRED", f"{intent} requires an explicit version delta.")
    if proposed is None:
        fail("VERSION_DELTA_REQUIRED", f"{intent} requires proposed_version.")
    if candidate != proposed or declared_versions[0]["new"] != proposed:
        fail("PROPOSED_VERSION_MISMATCH", "Candidate, delta and proposed version must match.")
    if current == proposed or declared_versions[0]["old"] != current:
        fail("VERSION_INTENT_CONFLICT", "Version delta must change the baseline version.")


def _validate_reference_changes(context: object) -> tuple[dict[str, object], ...]:
    declared = tuple({
        "old_line_number": item.old_line_number,
        "new_line_number": item.new_line_number,
        "old_line": item.old_line,
        "new_line": item.new_line,
    } for item in context.manifest.reference_changes)
    if context.manifest.change_class != "reference-only":
        if declared:
            fail("REFERENCE_CHANGE_UNEXPECTED", "reference_changes are valid only for reference-only.")
        return ()
    old_lines = context.baseline.body_bytes.decode("utf-8").splitlines()
    new_lines = context.candidate.body_bytes.decode("utf-8").splitlines()
    if len(old_lines) != len(new_lines):
        fail("REFERENCE_CHANGE_AMBIGUOUS", "Reference-only permits exact same-line-count replacements.")
    actual = tuple({
        "old_line_number": index + 1,
        "new_line_number": index + 1,
        "old_line": old,
        "new_line": new,
    } for index, (old, new) in enumerate(zip(old_lines, new_lines)) if old != new)
    if not actual:
        fail("CHANGE_CLASS_MISMATCH", "reference-only requires a body change.")
    identities = {(item["old_line_number"], item["new_line_number"]) for item in declared}
    if len(declared) != len(identities):
        fail("REFERENCE_CHANGE_INVALID", "Reference line declarations must be unique.")
    if tuple(sorted(declared, key=lambda item: item["old_line_number"])) != actual:
        fail("REFERENCE_CHANGE_DECLARATION_INCOMPLETE", "Changed reference lines are not exactly declared.")
    return actual


def _validate_change_contract(context: object) -> tuple[tuple[dict[str, object], ...], list[dict[str, object]], tuple[dict[str, object], ...]]:
    actual = metadata_differences(context.baseline, context.candidate)
    declared = tuple({"field": item.field, "old": item.old, "new": item.new} for item in context.manifest.metadata_delta)
    fields = [item["field"] for item in declared]
    if len(fields) != len(set(fields)):
        fail("METADATA_DELTA_DUPLICATE", "Each metadata field may be declared once.")
    protected = sorted(item["field"] for item in (*actual, *declared) if item["field"] in _PROTECTED_FIELDS)
    if protected:
        fail("PROTECTED_FIELD_CHANGE", f"Protected metadata/path change rejected: {', '.join(sorted(set(protected)))}.", field=protected[0], severity=Severity.BLOCKING)
    unsupported = sorted(item["field"] for item in actual if item["field"] not in _EXPLICIT_MUTABLE_FIELDS)
    if unsupported:
        fail("METADATA_CHANGE_NOT_ALLOWED", f"Metadata changes are not allowed for: {', '.join(unsupported)}.")
    normalized_actual = tuple(sorted(actual, key=lambda item: str(item["field"])))
    normalized_declared = tuple(sorted(declared, key=lambda item: str(item["field"])))
    _validate_version(context, normalized_actual, normalized_declared)
    if normalized_actual != normalized_declared:
        fail("METADATA_DELTA_MISMATCH", "Declared metadata_delta does not exactly match candidate.")
    body_changes = body_diff(context.baseline, context.candidate)
    body_changed = bool(body_changes)
    change_class = context.manifest.change_class
    front_matter_same = context.baseline.front_matter_bytes == context.candidate.front_matter_bytes
    if change_class in {"body-only", "reference-only"} and (actual or not front_matter_same or not body_changed):
        fail("CHANGE_CLASS_MISMATCH", f"{change_class} requires identical front matter and changed body.")
    if change_class == "metadata-only" and (body_changed or not actual):
        fail("CHANGE_CLASS_MISMATCH", "metadata-only requires unchanged body and explicit metadata delta.")
    if change_class == "metadata+body" and (not actual or not body_changed):
        fail("CHANGE_CLASS_MISMATCH", "metadata+body requires metadata and body changes.")
    reference_changes = _validate_reference_changes(context)
    return normalized_actual, body_changes, reference_changes


def _generated_preview(root: Path, records: tuple[object, ...]) -> tuple[dict[str, object], dict[str, bytes]]:
    try:
        rendered = build_generated_content(records)
    except GenerationBlockedError as exc:
        raise WorkflowError(exc.diagnostics, 1) from exc
    rendered_bytes = {
        REGISTRY_PATH.as_posix(): rendered.registry.encode("utf-8"),
        DOCUMENT_INDEX_PATH.as_posix(): rendered.document_index.encode("utf-8"),
    }
    items: list[dict[str, object]] = []
    for relative, expected in rendered_bytes.items():
        try:
            current = (root / relative).read_bytes()
        except FileNotFoundError:
            current = None
        except OSError as exc:
            fail("GENERATED_READ_ERROR", f"{root / relative}: {exc}", exit_code=2)
        items.append({"path": relative, "status": "UNCHANGED" if current == expected else "WOULD_CHANGE"})
    return {"outputs": items, "mode": "IN_MEMORY_READ_ONLY"}, rendered_bytes


def _recommend(change_class: str) -> str:
    return "major" if change_class == "semantic-governance-change" else "git-only" if change_class == "reference-only" else "minor"


def prepare_update(repository_root: str | Path, manifest: UpdateManifest, manifest_path: str | Path) -> PreparedUpdate:
    context = run_preflight_manifest(repository_root, manifest, manifest_path)
    metadata_delta, body_changes, reference_changes = _validate_change_contract(context)
    current = context.resolved.record
    candidate = context.candidate_record
    overlay = tuple(candidate if item.artifact_id == current.artifact_id else item for item in context.resolved.scan.artifacts)
    diagnostics = validate_record_set(overlay)
    blocking = tuple(item for item in diagnostics if item.severity in {Severity.ERROR, Severity.BLOCKING})
    if blocking:
        raise WorkflowError(blocking, 1)
    generated, rendered_bytes = _generated_preview(context.git.root, overlay)
    targets: list[tuple[str, bytes]] = [(current.path, context.candidate.data)]
    for item in generated["outputs"]:
        if item["status"] == "WOULD_CHANGE":
            targets.append((item["path"], rendered_bytes[item["path"]]))
    expected_changes = [{"operation": "DOCUMENT_UPDATE" if path == current.path else "GENERATED_UPDATE", "path": path} for path, _ in targets]
    recommended = _recommend(manifest.change_class)
    plan: dict[str, object] = {
        "schema_version": "aeterna-document-update-plan/0.1",
        "operation": "update",
        "artifact_id": current.artifact_id,
        "repository": {"root": str(context.git.root), "fingerprint": f"git:{context.git.head}", "artifact_count": len(context.resolved.scan.artifacts)},
        "baseline": {
            "branch": context.git.branch, "head": context.git.head,
            "worktree_clean": not context.git.worktree_entries, "staging_empty": not context.git.staged_paths,
            "sha256": context.baseline.sha256, "metadata_fingerprint": context.baseline.metadata_fingerprint,
            "byte_convention": {"encoding": context.baseline.encoding, "bom": context.baseline.bom, "newline": context.baseline.newline},
        },
        "resolved_artifact": record_payload(current),
        "candidate": {
            "original_path": manifest.candidate_path, "resolved_path": str(context.candidate.path.resolve()),
            "sha256": context.candidate.sha256, "metadata_fingerprint": context.candidate.metadata_fingerprint,
            "byte_convention": {"encoding": context.candidate.encoding, "bom": context.candidate.bom, "newline": context.candidate.newline},
        },
        "change": {
            "class": manifest.change_class, "risk": "HIGH" if manifest.change_class == "semantic-governance-change" else "NORMAL",
            "body_changed": bool(body_changes), "body_diff": body_changes, "protected_fields": "PASS",
            "reference_changes": list(reference_changes),
            "reference_change_declaration_complete": manifest.change_class != "reference-only" or bool(reference_changes),
        },
        "metadata_delta": list(metadata_delta),
        "version": {
            "current_version": current.version, "recommended_intent": recommended,
            "declared_intent": manifest.version_intent, "mismatch": recommended != manifest.version_intent,
            "proposed_version": manifest.proposed_version,
        },
        "impact": build_impact(overlay, current.artifact_id, include_transitive=True),
        "generated": generated,
        "preconditions": list(context.preconditions) + [
            {"name": "candidate_overlay_valid", "expected": True, "observed": True, "result": "PASS"},
            {"name": "dependency_graph_valid", "expected": True, "observed": True, "result": "PASS"},
            {"name": "version_consistency", "expected": True, "observed": True, "result": "PASS"},
        ],
        "expected_changes": expected_changes,
    }
    plan["plan_semantic_sha256"] = plan_semantic_digest(plan)
    return PreparedUpdate(plan, tuple(targets))


def build_update_plan(repository_root: str | Path, manifest_path: str | Path) -> dict[str, object]:
    path = Path(manifest_path).resolve()
    return prepare_update(repository_root, load_manifest(path), path).plan


def manifest_from_plan(plan: dict[str, object]) -> UpdateManifest:
    try:
        candidate, baseline = plan["candidate"], plan["baseline"]
        resolved, change, version = plan["resolved_artifact"], plan["change"], plan["version"]
        return UpdateManifest(
            artifact_id=str(plan["artifact_id"]), expected_branch=str(baseline["branch"]), expected_head=str(baseline["head"]),
            expected_path=str(resolved["path"]), baseline_sha256=str(baseline["sha256"]), metadata_fingerprint=str(baseline["metadata_fingerprint"]),
            change_class=str(change["class"]), version_intent=str(version["declared_intent"]), candidate_path=str(candidate["original_path"]),
            candidate_sha256=str(candidate["sha256"]),
            metadata_delta=tuple(MetadataDelta(str(item["field"]), item["old"], item["new"]) for item in plan["metadata_delta"]),
            proposed_version=version.get("proposed_version"),
            reference_changes=tuple(ReferenceChange(item["old_line_number"], item["new_line_number"], item["old_line"], item["new_line"]) for item in change.get("reference_changes", [])),
            resolved_candidate_path=str(candidate["resolved_path"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        fail("PLAN_STRUCTURE_INVALID", f"Cannot reconstruct planning input: {exc}", exit_code=3)


def recompute_prepared_update(repository_root: str | Path, plan: dict[str, object]) -> PreparedUpdate:
    manifest = manifest_from_plan(plan)
    anchor = Path(manifest.resolved_candidate_path or ".").parent / "recomputed-manifest.json"
    return prepare_update(repository_root, manifest, anchor)
