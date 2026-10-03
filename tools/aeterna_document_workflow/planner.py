"""Deterministic, read-only update plan construction."""

from __future__ import annotations

from pathlib import Path

from tools.aeterna_artifacts.generation import (
    DOCUMENT_INDEX_PATH,
    REGISTRY_PATH,
    GenerationBlockedError,
    build_generated_content,
)
from tools.aeterna_artifacts.model import Severity
from tools.aeterna_artifacts.scanner import validate_record_set

from .adapters import body_diff, metadata_differences
from .impact import build_impact
from .model import WorkflowError, fail
from .preflight import run_preflight
from .resolver import record_payload


_PROTECTED_FIELDS = frozenset({
    "artifact_id",
    "path",
    "authority",
    "kind",
    "type",
    "generated",
    "supersedes",
})
_EXPLICIT_MUTABLE_FIELDS = frozenset({
    "version",
    "lifecycle",
    "integration",
    "depends_on",
})


def _validate_change_contract(context: object) -> tuple[tuple[dict[str, object], ...], list[dict[str, object]]]:
    manifest = context.manifest
    actual = metadata_differences(context.baseline, context.candidate)
    declared = tuple(
        {"field": item.field, "old": item.old, "new": item.new}
        for item in manifest.metadata_delta
    )
    declared_fields = [item["field"] for item in declared]
    if len(declared_fields) != len(set(declared_fields)):
        fail("METADATA_DELTA_DUPLICATE", "Each metadata field may be declared once.")
    protected = sorted(
        item["field"] for item in (*actual, *declared)
        if item["field"] in _PROTECTED_FIELDS
    )
    if protected:
        fail(
            "PROTECTED_FIELD_CHANGE",
            f"Protected metadata/path change rejected: {', '.join(sorted(set(protected)))}.",
            field=protected[0],
            severity=Severity.BLOCKING,
        )
    unsupported = sorted(
        item["field"] for item in actual
        if item["field"] not in _EXPLICIT_MUTABLE_FIELDS
    )
    if unsupported:
        fail(
            "METADATA_CHANGE_NOT_ALLOWED",
            f"Metadata changes are not allowed for: {', '.join(unsupported)}.",
            severity=Severity.BLOCKING,
        )
    normalized_actual = tuple(sorted(actual, key=lambda item: str(item["field"])))
    normalized_declared = tuple(sorted(declared, key=lambda item: str(item["field"])))
    if normalized_actual != normalized_declared:
        fail(
            "METADATA_DELTA_MISMATCH",
            "Declared metadata_delta does not exactly match the candidate.",
            severity=Severity.BLOCKING,
        )

    body_changes = body_diff(context.baseline, context.candidate)
    body_changed = bool(body_changes)
    change_class = manifest.change_class
    if change_class in {"body-only", "reference-only"} and actual:
        fail("CHANGE_CLASS_MISMATCH", f"{change_class} requires unchanged metadata.")
    if change_class == "metadata-only" and body_changed:
        fail("CHANGE_CLASS_MISMATCH", "metadata-only requires unchanged body bytes.")
    if change_class == "metadata+body" and (not actual or not body_changed):
        fail("CHANGE_CLASS_MISMATCH", "metadata+body requires both declared metadata and body changes.")
    if change_class == "reference-only" and not body_changed:
        fail("CHANGE_CLASS_MISMATCH", "reference-only requires enumerated body changes.")
    return normalized_actual, body_changes


def _generated_preview(root: Path, records: tuple[object, ...]) -> dict[str, object]:
    try:
        rendered = build_generated_content(records)
    except GenerationBlockedError as exc:
        raise WorkflowError(exc.diagnostics, 1) from exc
    outputs = (
        (REGISTRY_PATH, rendered.registry.encode("utf-8")),
        (DOCUMENT_INDEX_PATH, rendered.document_index.encode("utf-8")),
    )
    items: list[dict[str, object]] = []
    for relative, expected in outputs:
        path = root / relative
        try:
            current = path.read_bytes()
        except FileNotFoundError:
            current = None
        except OSError as exc:
            fail("GENERATED_READ_ERROR", f"{path}: {exc}", exit_code=2)
        items.append({
            "path": relative.as_posix(),
            "status": "UNCHANGED" if current == expected else "WOULD_CHANGE",
        })
    return {"outputs": items, "mode": "IN_MEMORY_READ_ONLY"}


def _recommend(change_class: str) -> str:
    if change_class == "semantic-governance-change":
        return "major"
    if change_class == "reference-only":
        return "git-only"
    return "minor"


def build_update_plan(
    repository_root: str | Path,
    manifest_path: str | Path,
) -> dict[str, object]:
    context = run_preflight(repository_root, manifest_path)
    metadata_delta, body_changes = _validate_change_contract(context)
    current = context.resolved.record
    candidate = context.candidate_record
    overlay = tuple(
        candidate if item.artifact_id == current.artifact_id else item
        for item in context.resolved.scan.artifacts
    )
    diagnostics = validate_record_set(overlay)
    blocking = tuple(
        item for item in diagnostics
        if item.severity in {Severity.ERROR, Severity.BLOCKING}
    )
    if blocking:
        raise WorkflowError(blocking, 1)
    generated = _generated_preview(context.git.root, overlay)
    impact = build_impact(overlay, current.artifact_id, include_transitive=True)
    recommended = _recommend(context.manifest.change_class)
    expected_changes: list[dict[str, str]] = [
        {"operation": "DOCUMENT_UPDATE", "path": current.path}
    ]
    expected_changes.extend(
        {"operation": "GENERATED_UPDATE", "path": item["path"]}
        for item in generated["outputs"]
        if item["status"] == "WOULD_CHANGE"
    )
    candidate_path = Path(context.manifest.candidate_path)
    return {
        "schema_version": "aeterna-document-update-plan/0.1",
        "operation": "update",
        "artifact_id": current.artifact_id,
        "repository": {
            "root": str(context.git.root),
            "fingerprint": f"git:{context.git.head}",
        },
        "baseline": {
            "branch": context.git.branch,
            "head": context.git.head,
            "worktree_clean": not context.git.worktree_entries,
            "staging_empty": not context.git.staged_paths,
            "sha256": context.baseline.sha256,
            "metadata_fingerprint": context.baseline.metadata_fingerprint,
            "byte_convention": {
                "encoding": context.baseline.encoding,
                "bom": context.baseline.bom,
                "newline": context.baseline.newline,
            },
        },
        "resolved_artifact": record_payload(current),
        "candidate": {
            "path": candidate_path.as_posix(),
            "sha256": context.candidate.sha256,
            "metadata_fingerprint": context.candidate.metadata_fingerprint,
            "byte_convention": {
                "encoding": context.candidate.encoding,
                "bom": context.candidate.bom,
                "newline": context.candidate.newline,
            },
        },
        "change": {
            "class": context.manifest.change_class,
            "risk": "HIGH" if context.manifest.change_class == "semantic-governance-change" else "NORMAL",
            "body_changed": bool(body_changes),
            "body_diff": body_changes,
            "protected_fields": "PASS",
        },
        "metadata_delta": list(metadata_delta),
        "version": {
            "current_version": current.version,
            "recommended_intent": recommended,
            "declared_intent": context.manifest.version_intent,
            "mismatch": recommended != context.manifest.version_intent,
            "proposed_version": context.manifest.proposed_version,
        },
        "impact": impact,
        "generated": generated,
        "preconditions": list(context.preconditions) + [
            {
                "name": "candidate_overlay_valid",
                "expected": True,
                "observed": True,
                "result": "PASS",
            },
            {
                "name": "dependency_graph_valid",
                "expected": True,
                "observed": True,
                "result": "PASS",
            },
        ],
        "expected_changes": expected_changes,
    }
