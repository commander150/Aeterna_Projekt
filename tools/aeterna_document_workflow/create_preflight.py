"""Fail-closed preflight for read-only CREATE planning."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from tools.aeterna_artifacts.model import ArtifactRecord, Scope, Severity
from tools.aeterna_artifacts.scanner import scan_repository
from tools.aeterna_artifacts.validation import validate_metadata

from .content import inspect_markdown_bytes
from .git_state import capture_git_state
from .model import CreateManifest, CreatePreflightContext, WorkflowError, fail
from .path_policy import inspect_target, validate_candidate_path


CREATE_MANIFEST_SCHEMA = "aeterna-document-create-manifest/0.1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_H1 = re.compile(r"^#(?:[ \t]+(.*))?$")
_METADATA_KEYS = frozenset({
    "artifact_id",
    "kind",
    "type",
    "version",
    "lifecycle",
    "integration",
    "authority",
    "generated",
    "depends_on",
    "supersedes",
})
_MANIFEST_KEYS = frozenset({
    "schema_version",
    "artifact_id",
    "target_path",
    "candidate_path",
    "expected_branch",
    "expected_head",
    "candidate_sha256",
    "candidate_metadata_fingerprint",
    "candidate_metadata",
    "candidate_byte_convention",
    "declared_authority",
    "initial_version",
})
_BYTE_CONVENTION = {"encoding": "UTF-8", "bom": False, "newline": "LF"}


def _required_string(payload: dict[str, object], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value:
        fail("CREATE_MANIFEST_FIELD_INVALID", f"CREATE manifest field must be a non-empty string: {name}.", field=name)
    return value


def load_create_manifest(path: str | Path) -> CreateManifest:
    manifest_path = Path(path).resolve()
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail("CREATE_MANIFEST_READ_ERROR", f"{manifest_path}: {exc}", exit_code=2)
    if not isinstance(payload, dict):
        fail("CREATE_MANIFEST_INVALID", "CREATE manifest must be a JSON object.")
    keys = frozenset(payload)
    if keys != _MANIFEST_KEYS:
        missing = sorted(_MANIFEST_KEYS - keys)
        unknown = sorted(keys - _MANIFEST_KEYS)
        fail(
            "CREATE_MANIFEST_STRUCTURE_INVALID",
            f"CREATE manifest exact field set required; missing={missing}, unknown={unknown}.",
        )
    if payload.get("schema_version") != CREATE_MANIFEST_SCHEMA:
        fail("CREATE_MANIFEST_SCHEMA_UNSUPPORTED", "Unsupported CREATE manifest schema.")
    candidate_metadata = payload.get("candidate_metadata")
    if not isinstance(candidate_metadata, dict) or any(not isinstance(key, str) for key in candidate_metadata):
        fail("CREATE_MANIFEST_FIELD_INVALID", "candidate_metadata must be a string-keyed object.", field="candidate_metadata")
    byte_convention = payload.get("candidate_byte_convention")
    if not isinstance(byte_convention, dict) or byte_convention != _BYTE_CONVENTION:
        fail(
            "CREATE_BYTE_CONVENTION_INVALID",
            "candidate_byte_convention must be exactly UTF-8, BOM false, LF.",
            field="candidate_byte_convention",
        )
    candidate_sha256 = _required_string(payload, "candidate_sha256")
    fingerprint = _required_string(payload, "candidate_metadata_fingerprint")
    if not _SHA256.fullmatch(candidate_sha256) or not _SHA256.fullmatch(fingerprint):
        fail("CREATE_MANIFEST_HASH_INVALID", "CREATE manifest hashes must be lowercase SHA-256 values.")
    return CreateManifest(
        artifact_id=_required_string(payload, "artifact_id"),
        target_path=_required_string(payload, "target_path"),
        candidate_path=_required_string(payload, "candidate_path"),
        expected_branch=_required_string(payload, "expected_branch"),
        expected_head=_required_string(payload, "expected_head"),
        candidate_sha256=candidate_sha256,
        candidate_metadata_fingerprint=fingerprint,
        candidate_metadata=dict(candidate_metadata),
        candidate_byte_convention=dict(byte_convention),
        declared_authority=_required_string(payload, "declared_authority"),
        initial_version=_required_string(payload, "initial_version"),
    )


def _gate(name: str, expected: object, observed: object) -> dict[str, object]:
    return {
        "name": name,
        "expected": expected,
        "observed": observed,
        "result": "PASS" if expected == observed else "FAIL",
    }


def _artifact_set_identity(records: tuple[ArtifactRecord, ...]) -> str:
    payload = [
        {
            "artifact_id": record.artifact_id,
            "kind": record.kind,
            "type": record.type,
            "version": record.version,
            "lifecycle": record.lifecycle,
            "integration": record.integration,
            "authority": record.authority,
            "generated": record.generated,
            "depends_on": list(record.depends_on),
            "supersedes": list(record.supersedes),
            "path": record.path,
            "scope": record.scope.value,
            "title": record.title,
        }
        for record in sorted(records, key=lambda item: (item.artifact_id, item.path))
    ]
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _candidate_title(body: bytes) -> str:
    matches = [match for line in body.decode("utf-8").splitlines() if (match := _H1.fullmatch(line))]
    if not matches:
        fail("CREATE_H1_MISSING", "CREATE candidate must contain exactly one non-empty H1.")
    if len(matches) != 1:
        fail("CREATE_H1_MULTIPLE", "CREATE candidate must contain exactly one H1.")
    title = (matches[0].group(1) or "").strip()
    if not title:
        fail("CREATE_H1_EMPTY", "CREATE candidate H1 cannot be empty.")
    return title


def run_create_preflight(
    repository_root: str | Path,
    manifest_path: str | Path,
) -> CreatePreflightContext:
    manifest_file = Path(manifest_path).resolve()
    manifest = load_create_manifest(manifest_file)
    root = Path(repository_root).resolve()
    git = capture_git_state(root)
    gates: list[dict[str, object]] = []
    for name, expected, observed, code in (
        ("repository_root", str(root), str(git.root), "REPOSITORY_ROOT_MISMATCH"),
        ("branch", manifest.expected_branch, git.branch, "EXPECTED_BRANCH_MISMATCH"),
        ("head", manifest.expected_head, git.head, "EXPECTED_HEAD_MISMATCH"),
        ("worktree_clean", True, not git.worktree_entries, "WORKTREE_DIRTY"),
        ("staging_empty", True, not git.staged_paths, "STAGING_NOT_EMPTY"),
    ):
        gates.append(_gate(name, expected, observed))
        if expected != observed:
            fail(code, f"CREATE precondition {name} expected {expected!r}, observed {observed!r}.", exit_code=3)

    scan = scan_repository(git.root)
    gates.append(_gate("fresh_scan_diagnostics", 0, len(scan.diagnostics)))
    if scan.diagnostics:
        raise WorkflowError(scan.diagnostics, 1)

    target = inspect_target(git.root, manifest.target_path)
    candidate_path = validate_candidate_path(
        git.root,
        manifest_file,
        manifest.candidate_path,
        manifest.target_path,
    )
    try:
        candidate_data = candidate_path.read_bytes()
    except OSError as exc:
        fail("CONTENT_READ_ERROR", f"{candidate_path}: {exc}", exit_code=2)
    observed_sha = hashlib.sha256(candidate_data).hexdigest()
    gates.append(_gate("candidate_sha256", manifest.candidate_sha256, observed_sha))
    if observed_sha != manifest.candidate_sha256:
        fail("CREATE_CANDIDATE_HASH_MISMATCH", "CREATE candidate SHA-256 does not match manifest.", exit_code=3)
    candidate = inspect_markdown_bytes(candidate_data, candidate_path)
    observed_convention = {
        "encoding": candidate.encoding,
        "bom": candidate.bom,
        "newline": candidate.newline,
    }
    gates.append(_gate("candidate_byte_convention", _BYTE_CONVENTION, observed_convention))
    if observed_convention != _BYTE_CONVENTION:
        fail("CREATE_CANDIDATE_BYTE_CONVENTION", "CREATE candidate must be UTF-8 without BOM and use LF.")

    fields = dict(candidate.metadata.fields)
    keys = frozenset(fields)
    if keys != _METADATA_KEYS:
        fail(
            "CREATE_METADATA_KEY_SET_INVALID",
            f"CREATE candidate exact metadata key set required; missing={sorted(_METADATA_KEYS - keys)}, unknown={sorted(keys - _METADATA_KEYS)}.",
        )
    diagnostics = validate_metadata(candidate.metadata)
    blocking = tuple(item for item in diagnostics if item.severity in {Severity.ERROR, Severity.BLOCKING})
    if blocking:
        raise WorkflowError(blocking, 1)
    if fields["kind"] != "document":
        fail("CREATE_KIND_BLOCKED", "CREATE candidate kind must be document.", field="kind")
    if fields["generated"] is not False:
        fail("CREATE_GENERATED_BLOCKED", "CREATE candidate generated must be false.", field="generated")
    if fields["lifecycle"] != "active":
        fail("CREATE_LIFECYCLE_BLOCKED", "CREATE candidate lifecycle must be active.", field="lifecycle")
    if fields["integration"] not in {"current", "pending_integration"}:
        fail("CREATE_INTEGRATION_BLOCKED", "CREATE candidate integration is not supported.", field="integration")
    if fields["supersedes"] != []:
        fail("CREATE_SUPERSEDES_BLOCKED", "CREATE candidate supersedes must be an empty list.", field="supersedes")
    dependencies = fields["depends_on"]
    if not isinstance(dependencies, list):
        fail("CREATE_DEPENDS_ON_INVALID", "CREATE candidate depends_on must be an explicit list.", field="depends_on")
    if len(dependencies) != len(set(dependencies)):
        fail("CREATE_DEPENDS_ON_DUPLICATE", "CREATE candidate dependencies must be unique.", field="depends_on")

    if fields != dict(manifest.candidate_metadata):
        fail("CREATE_CANDIDATE_METADATA_MISMATCH", "Manifest candidate_metadata does not exactly match native metadata.", exit_code=3)
    if candidate.metadata_fingerprint != manifest.candidate_metadata_fingerprint:
        fail("CREATE_METADATA_FINGERPRINT_MISMATCH", "CREATE candidate metadata fingerprint does not match manifest.", exit_code=3)
    if manifest.artifact_id != fields["artifact_id"]:
        fail("CREATE_ARTIFACT_ID_MISMATCH", "Manifest and candidate artifact IDs must match exactly.")
    if manifest.declared_authority != fields["authority"]:
        fail("CREATE_AUTHORITY_MISMATCH", "Manifest declared_authority must match candidate authority.")
    if manifest.initial_version != fields["version"]:
        fail("CREATE_INITIAL_VERSION_MISMATCH", "Manifest initial_version must match candidate version.")
    if any(record.artifact_id.casefold() == manifest.artifact_id.casefold() for record in scan.artifacts):
        fail("CREATE_ARTIFACT_ID_COLLISION", "CREATE artifact ID already exists or is case-equivalent.")

    title = _candidate_title(candidate.body_bytes)
    record = ArtifactRecord(
        artifact_id=str(fields["artifact_id"]),
        kind=str(fields["kind"]),
        type=str(fields["type"]),
        version=str(fields["version"]),
        lifecycle=str(fields["lifecycle"]),
        integration=str(fields["integration"]),
        authority=str(fields["authority"]),
        generated=False,
        depends_on=tuple(dependencies),
        supersedes=(),
        path=target.relative_path,
        scope=Scope.ACTIVE,
        title=title,
    )
    baseline_identity = _artifact_set_identity(scan.artifacts)
    gates.extend((
        _gate("candidate_inside_repository_temp", True, True),
        _gate("candidate_git_ignored", True, True),
        _gate("candidate_is_not_target", True, True),
        _gate("candidate_metadata_exact", True, True),
        _gate("candidate_h1_count", 1, 1),
        _gate("target_scope", "ACTIVE", target.scope.value),
        _gate("parent_directory_exists", True, target.parent_exists),
        _gate("parent_directory_real", True, target.parent_real),
        _gate("target_absent", True, target.absent),
        _gate("target_collision_count", 0, len(target.collisions)),
    ))
    return CreatePreflightContext(
        manifest_file,
        manifest,
        git,
        scan,
        baseline_identity,
        candidate,
        record,
        target.relative_path,
        tuple(gates),
    )
