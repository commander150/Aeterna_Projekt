"""Fail-closed read-only preconditions for update planning."""

from __future__ import annotations

import json
from pathlib import Path

from tools.aeterna_artifacts.model import Scope, Severity

from .adapters import candidate_record
from .content import inspect_markdown
from .git_state import capture_git_state
from .model import MetadataDelta, PreflightContext, UpdateManifest, fail
from .resolver import resolve_artifact


_CHANGE_CLASSES = frozenset({
    "body-only",
    "metadata-only",
    "metadata+body",
    "reference-only",
    "semantic-governance-change",
})
_VERSION_INTENTS = frozenset({"git-only", "minor", "major"})


def _required_string(payload: dict[str, object], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value:
        fail("MANIFEST_FIELD_INVALID", f"Manifest field must be a non-empty string: {name}", field=name)
    return value


def load_manifest(path: str | Path) -> UpdateManifest:
    manifest_path = Path(path).resolve()
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail("MANIFEST_READ_ERROR", f"{manifest_path}: {exc}", exit_code=2)
    if not isinstance(payload, dict):
        fail("MANIFEST_INVALID", "Manifest must be a JSON object.")
    schema = payload.get("schema_version")
    if schema is not None and schema != "aeterna-document-update-manifest/0.1":
        fail("MANIFEST_SCHEMA_UNSUPPORTED", f"Unsupported manifest schema: {schema}")
    change_class = _required_string(payload, "change_class")
    if change_class not in _CHANGE_CLASSES:
        fail("CHANGE_CLASS_INVALID", f"Unsupported change class: {change_class}", field="change_class")
    version_intent = _required_string(payload, "version_intent")
    if version_intent not in _VERSION_INTENTS:
        fail("VERSION_INTENT_INVALID", f"Unsupported version intent: {version_intent}", field="version_intent")
    raw_delta = payload.get("metadata_delta", [])
    if not isinstance(raw_delta, list):
        fail("METADATA_DELTA_INVALID", "metadata_delta must be a list.", field="metadata_delta")
    deltas: list[MetadataDelta] = []
    for index, item in enumerate(raw_delta):
        if not isinstance(item, dict) or not isinstance(item.get("field"), str):
            fail("METADATA_DELTA_INVALID", f"Invalid metadata_delta entry at index {index}.")
        if "old" not in item or "new" not in item:
            fail("METADATA_DELTA_INVALID", f"metadata_delta[{index}] requires old and new.")
        deltas.append(MetadataDelta(str(item["field"]), item["old"], item["new"]))
    proposed = payload.get("proposed_version")
    if proposed is not None and not isinstance(proposed, str):
        fail("PROPOSED_VERSION_INVALID", "proposed_version must be a string or null.")
    return UpdateManifest(
        artifact_id=_required_string(payload, "artifact_id"),
        expected_branch=_required_string(payload, "expected_branch"),
        expected_head=_required_string(payload, "expected_head"),
        expected_path=_required_string(payload, "expected_path"),
        baseline_sha256=_required_string(payload, "baseline_sha256"),
        metadata_fingerprint=_required_string(payload, "metadata_fingerprint"),
        change_class=change_class,
        version_intent=version_intent,
        candidate_path=_required_string(payload, "candidate_path"),
        candidate_sha256=_required_string(payload, "candidate_sha256"),
        metadata_delta=tuple(deltas),
        proposed_version=proposed,
    )


def _gate(name: str, expected: object, observed: object) -> dict[str, object]:
    return {
        "name": name,
        "expected": expected,
        "observed": observed,
        "result": "PASS" if expected == observed else "FAIL",
    }


def run_preflight(
    repository_root: str | Path,
    manifest_path: str | Path,
) -> PreflightContext:
    requested_root = Path(repository_root).resolve()
    manifest_file = Path(manifest_path).resolve()
    manifest = load_manifest(manifest_file)
    git = capture_git_state(requested_root)
    gates: list[dict[str, object]] = []

    checks = (
        ("repository_root", str(requested_root), str(git.root), "REPOSITORY_ROOT_MISMATCH"),
        ("branch", manifest.expected_branch, git.branch, "EXPECTED_BRANCH_MISMATCH"),
        ("head", manifest.expected_head, git.head, "EXPECTED_HEAD_MISMATCH"),
        ("worktree_clean", True, not git.worktree_entries, "WORKTREE_DIRTY"),
        ("staging_empty", True, not git.staged_paths, "STAGING_NOT_EMPTY"),
    )
    for name, expected, observed, code in checks:
        gates.append(_gate(name, expected, observed))
        if expected != observed:
            fail(code, f"Precondition {name} expected {expected!r}, observed {observed!r}.", exit_code=3)

    resolved = resolve_artifact(git.root, manifest.artifact_id)
    record = resolved.record
    gates.extend((
        _gate("fresh_scan_diagnostics", 0, len(resolved.scan.diagnostics)),
        _gate("artifact_resolution_count", 1, 1),
        _gate("artifact_id", manifest.artifact_id, record.artifact_id),
    ))
    policy = (
        ("path", manifest.expected_path, record.path, "EXPECTED_PATH_MISMATCH"),
        ("scope", Scope.ACTIVE, record.scope, "ARTIFACT_SCOPE_BLOCKED"),
        ("kind", "document", record.kind, "ARTIFACT_KIND_BLOCKED"),
        ("generated", False, record.generated, "GENERATED_ARTIFACT_BLOCKED"),
        ("markdown", True, record.path.casefold().endswith(".md"), "ARTIFACT_FORMAT_BLOCKED"),
        ("lifecycle", "active", record.lifecycle, "ARTIFACT_LIFECYCLE_BLOCKED"),
    )
    for name, expected, observed, code in policy:
        gates.append(_gate(name, expected.value if isinstance(expected, Scope) else expected, observed.value if isinstance(observed, Scope) else observed))
        if expected != observed:
            exit_code = 3 if name == "path" else 1
            fail(code, f"Artifact precondition {name} failed.", exit_code=exit_code)

    baseline = inspect_markdown(git.root / record.path)
    baseline_checks = (
        ("baseline_sha256", manifest.baseline_sha256, baseline.sha256, "BASELINE_HASH_MISMATCH"),
        ("metadata_fingerprint", manifest.metadata_fingerprint, baseline.metadata_fingerprint, "METADATA_FINGERPRINT_MISMATCH"),
    )
    for name, expected, observed, code in baseline_checks:
        gates.append(_gate(name, expected, observed))
        if expected != observed:
            fail(code, f"Precondition {name} mismatch.", exit_code=3)

    candidate_path = Path(manifest.candidate_path)
    if not candidate_path.is_absolute():
        candidate_path = (manifest_file.parent / candidate_path).resolve()
    candidate = inspect_markdown(candidate_path)
    gates.append(_gate("candidate_sha256", manifest.candidate_sha256, candidate.sha256))
    if manifest.candidate_sha256 != candidate.sha256:
        fail("CANDIDATE_HASH_MISMATCH", "Candidate SHA-256 does not match manifest.", exit_code=3)
    for name, expected, observed, code in (
        ("candidate_encoding", baseline.encoding, candidate.encoding, "CANDIDATE_ENCODING_DRIFT"),
        ("candidate_bom", baseline.bom, candidate.bom, "CANDIDATE_BOM_DRIFT"),
        ("candidate_newline", baseline.newline, candidate.newline, "CANDIDATE_NEWLINE_DRIFT"),
    ):
        gates.append(_gate(name, expected, observed))
        if expected != observed:
            fail(code, f"Candidate {name} must preserve the baseline convention.")
    protected_fields = (
        "artifact_id",
        "authority",
        "kind",
        "type",
        "generated",
        "supersedes",
    )
    baseline_fields = baseline.metadata.fields
    candidate_fields = candidate.metadata.fields
    changed_protected = [
        field for field in protected_fields
        if baseline_fields.get(field) != candidate_fields.get(field)
    ]
    if changed_protected:
        fail(
            "PROTECTED_FIELD_CHANGE",
            f"Protected metadata change rejected: {', '.join(changed_protected)}.",
            field=changed_protected[0],
            severity=Severity.BLOCKING,
        )
    proposed_record = candidate_record(candidate, record)
    gates.append(_gate("candidate_metadata_valid", True, True))
    return PreflightContext(
        manifest_file,
        manifest,
        git,
        resolved,
        baseline,
        candidate,
        proposed_record,
        tuple(gates),
    )
