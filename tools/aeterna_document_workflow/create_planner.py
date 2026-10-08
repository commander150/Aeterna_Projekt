"""Deterministic, read-only CREATE plan construction."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re

from tools.aeterna_artifacts.generation import (
    DOCUMENT_INDEX_PATH,
    REGISTRY_PATH,
    GenerationBlockedError,
    build_generated_content,
)
from tools.aeterna_artifacts.model import Severity
from tools.aeterna_artifacts.scanner import validate_record_set

from .create_preflight import run_create_preflight
from .impact import build_impact
from .model import WorkflowError, fail
from .review import plan_semantic_digest


CREATE_PLAN_SCHEMA = "aeterna-document-create-plan/0.1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_HIGH_RISK_AUTHORITIES = frozenset({
    "canonical-rules",
    "project-direction",
    "document-governance",
    "technical-contract",
})


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _generated_preview(root: Path, records: tuple[object, ...]) -> tuple[dict[str, object], dict[str, bytes]]:
    try:
        rendered = build_generated_content(records)
    except GenerationBlockedError as exc:
        raise WorkflowError(exc.diagnostics, 1) from exc
    rendered_bytes = {
        REGISTRY_PATH.as_posix(): rendered.registry.encode("utf-8"),
        DOCUMENT_INDEX_PATH.as_posix(): rendered.document_index.encode("utf-8"),
    }
    outputs: list[dict[str, object]] = []
    for relative, expected in rendered_bytes.items():
        try:
            current = (root / relative).read_bytes()
        except FileNotFoundError:
            current = None
        except OSError as exc:
            fail("GENERATED_READ_ERROR", f"{root / relative}: {exc}", exit_code=2)
        outputs.append({
            "path": relative,
            "status": "UNCHANGED" if current == expected else "WOULD_CHANGE",
            "current_sha256": _sha256(current) if current is not None else None,
            "rendered_sha256": _sha256(expected),
        })
    return {"mode": "IN_MEMORY_READ_ONLY", "outputs": outputs}, rendered_bytes


def build_create_plan(repository_root: str | Path, manifest_path: str | Path) -> dict[str, object]:
    context = run_create_preflight(repository_root, manifest_path)
    overlay = tuple(sorted(
        (*context.scan.artifacts, context.candidate_record),
        key=lambda item: (item.artifact_id, item.path),
    ))
    diagnostics = validate_record_set(overlay)
    blocking = tuple(item for item in diagnostics if item.severity in {Severity.ERROR, Severity.BLOCKING})
    if blocking:
        raise WorkflowError(blocking, 1)
    generated, rendered_bytes = _generated_preview(context.git.root, overlay)
    expected_changes: list[dict[str, object]] = [{
        "operation": "DOCUMENT_CREATE",
        "path": context.target_path,
    }]
    for output in generated["outputs"]:
        if output["status"] == "WOULD_CHANGE":
            expected_changes.append({
                "operation": "GENERATED_UPDATE",
                "path": output["path"],
            })
    fields = dict(context.candidate.metadata.fields)
    risk = "HIGH" if context.manifest.declared_authority in _HIGH_RISK_AUTHORITIES else "NORMAL"
    plan: dict[str, object] = {
        "schema_version": CREATE_PLAN_SCHEMA,
        "operation": "create",
        "artifact_id": context.manifest.artifact_id,
        "repository": {
            "root": str(context.git.root),
            "fingerprint": f"git:{context.git.head}",
            "baseline_artifact_count": len(context.scan.artifacts),
            "baseline_artifact_set_identity": context.baseline_artifact_set_identity,
            "expected_artifact_count_after": len(overlay),
        },
        "baseline": {
            "branch": context.git.branch,
            "head": context.git.head,
            "worktree_clean": not context.git.worktree_entries,
            "staging_empty": not context.git.staged_paths,
        },
        "target": {
            "declared_path": context.target_path,
            "scope": context.candidate_record.scope.value,
            "parent_directory_exists": True,
            "parent_directory_real": True,
            "absent": True,
            "collision_result": "PASS",
        },
        "candidate": {
            "original_path": context.manifest.candidate_path,
            "resolved_path": str(context.candidate.path.resolve()),
            "sha256": context.candidate.sha256,
            "metadata": fields,
            "metadata_fingerprint": context.candidate.metadata_fingerprint,
            "title": context.candidate_record.title,
            "canonical_path": context.target_path,
            "byte_convention": {
                "encoding": context.candidate.encoding,
                "bom": context.candidate.bom,
                "newline": context.candidate.newline,
            },
        },
        "authority": {
            "declared_authority": context.manifest.declared_authority,
            "risk": risk,
        },
        "version": {"initial_version": context.manifest.initial_version},
        "impact": build_impact(overlay, context.manifest.artifact_id, include_transitive=True),
        "generated": generated,
        "preconditions": list(context.preconditions) + [
            {"name": "candidate_overlay_valid", "expected": True, "observed": True, "result": "PASS"},
            {"name": "dependency_graph_valid", "expected": True, "observed": True, "result": "PASS"},
            {
                "name": "expected_artifact_count_after",
                "expected": len(context.scan.artifacts) + 1,
                "observed": len(overlay),
                "result": "PASS",
            },
        ],
        "expected_changes": expected_changes,
    }
    plan["plan_semantic_sha256"] = plan_semantic_digest(plan)
    return validate_create_plan_integrity(plan)


def validate_create_plan_integrity(plan: object) -> dict[str, object]:
    if not isinstance(plan, dict):
        fail("CREATE_PLAN_INVALID", "CREATE plan must be a JSON object.")
    if plan.get("schema_version") != CREATE_PLAN_SCHEMA or plan.get("operation") != "create":
        fail("CREATE_PLAN_SCHEMA_INVALID", "Unsupported CREATE plan schema or operation.")
    digest = plan.get("plan_semantic_sha256")
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
        fail("CREATE_PLAN_INTEGRITY_MISMATCH", "CREATE plan semantic digest is missing or malformed.", exit_code=3)
    if digest != plan_semantic_digest(plan):
        fail("CREATE_PLAN_INTEGRITY_MISMATCH", "CREATE plan semantic digest does not match content.", exit_code=3)
    forbidden_root = {
        "change",
        "metadata_delta",
        "resolved_artifact",
        "baseline_sha256",
        "metadata_fingerprint",
        "version_intent",
        "proposed_version",
    }
    if forbidden_root.intersection(plan):
        fail("CREATE_PLAN_UPDATE_FIELD_PRESENT", "CREATE plan contains UPDATE-only fields.")
    baseline = plan.get("baseline")
    version = plan.get("version")
    if not isinstance(baseline, dict) or {"sha256", "metadata_fingerprint"}.intersection(baseline):
        fail("CREATE_PLAN_UPDATE_FIELD_PRESENT", "CREATE baseline contains target-specific UPDATE fields.")
    if not isinstance(version, dict) or set(version) != {"initial_version"}:
        fail("CREATE_PLAN_VERSION_INVALID", "CREATE plan must contain only explicit initial_version semantics.")
    return plan
