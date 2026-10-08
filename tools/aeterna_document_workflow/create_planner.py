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

from .create_preflight import run_create_preflight, run_create_preflight_manifest
from .impact import build_impact
from .model import CreateManifest, CreatePreflightContext, PreparedCreate, WorkflowError, fail
from .review import plan_semantic_digest


CREATE_PLAN_SCHEMA = "aeterna-document-create-plan/0.1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_HIGH_RISK_AUTHORITIES = frozenset({
    "canonical-rules",
    "project-direction",
    "document-governance",
    "technical-contract",
})
_CREATE_PLAN_KEYS = frozenset({
    "schema_version",
    "operation",
    "artifact_id",
    "repository",
    "baseline",
    "target",
    "candidate",
    "authority",
    "version",
    "impact",
    "generated",
    "preconditions",
    "expected_changes",
    "plan_semantic_sha256",
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


def _prepare_create_context(context: CreatePreflightContext) -> PreparedCreate:
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
    validated = validate_create_plan_integrity(plan)
    target_bytes: list[tuple[str, bytes]] = [
        (context.target_path, context.candidate.data),
    ]
    target_bytes.extend(
        (str(item["path"]), rendered_bytes[str(item["path"])])
        for item in expected_changes[1:]
    )
    return PreparedCreate(validated, tuple(target_bytes))


def build_create_plan(repository_root: str | Path, manifest_path: str | Path) -> dict[str, object]:
    return _prepare_create_context(run_create_preflight(repository_root, manifest_path)).plan


def prepare_create(
    repository_root: str | Path,
    manifest: CreateManifest,
    manifest_path: str | Path,
) -> PreparedCreate:
    return _prepare_create_context(
        run_create_preflight_manifest(repository_root, manifest, manifest_path)
    )


def manifest_from_create_plan(plan: dict[str, object]) -> tuple[CreateManifest, Path]:
    candidate = plan["candidate"]
    baseline = plan["baseline"]
    target = plan["target"]
    authority = plan["authority"]
    version = plan["version"]
    resolved = Path(str(candidate["resolved_path"]))
    original = Path(str(candidate["original_path"]))
    if not original.parts:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE candidate original_path is empty.")
    anchor = resolved
    for _ in original.parts:
        anchor = anchor.parent
    manifest_path = anchor / "recomputed-create-manifest.json"
    return CreateManifest(
        artifact_id=str(plan["artifact_id"]),
        target_path=str(target["declared_path"]),
        candidate_path=str(candidate["original_path"]),
        expected_branch=str(baseline["branch"]),
        expected_head=str(baseline["head"]),
        candidate_sha256=str(candidate["sha256"]),
        candidate_metadata_fingerprint=str(candidate["metadata_fingerprint"]),
        candidate_metadata=dict(candidate["metadata"]),
        candidate_byte_convention=dict(candidate["byte_convention"]),
        declared_authority=str(authority["declared_authority"]),
        initial_version=str(version["initial_version"]),
    ), manifest_path


def recompute_prepared_create(
    repository_root: str | Path,
    plan: dict[str, object],
) -> PreparedCreate:
    validate_create_plan_integrity(plan)
    root = Path(repository_root).resolve()
    repository = plan["repository"]
    planned_root = Path(str(repository["root"])).resolve()
    if planned_root != root:
        fail("REPOSITORY_ROOT_MISMATCH", "CREATE plan repository root does not match apply root.", exit_code=3)
    manifest, manifest_path = manifest_from_create_plan(plan)
    return prepare_create(root, manifest, manifest_path)


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
    if set(plan) != _CREATE_PLAN_KEYS:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE plan must contain the exact CREATE 0.1 field set.")
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
    repository = plan.get("repository")
    target = plan.get("target")
    candidate = plan.get("candidate")
    authority = plan.get("authority")
    generated = plan.get("generated")
    expected_changes = plan.get("expected_changes")
    if not isinstance(repository, dict) or set(repository) != {
        "root",
        "fingerprint",
        "baseline_artifact_count",
        "baseline_artifact_set_identity",
        "expected_artifact_count_after",
    }:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE repository section is invalid.")
    if not isinstance(baseline, dict) or set(baseline) != {
        "branch", "head", "worktree_clean", "staging_empty"
    }:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE baseline section is invalid.")
    if not isinstance(target, dict) or set(target) != {
        "declared_path", "scope", "parent_directory_exists", "parent_directory_real", "absent", "collision_result"
    }:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE target section is invalid.")
    if not isinstance(candidate, dict) or set(candidate) != {
        "original_path", "resolved_path", "sha256", "metadata", "metadata_fingerprint",
        "title", "canonical_path", "byte_convention",
    }:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE candidate section is invalid.")
    if not isinstance(authority, dict) or set(authority) != {"declared_authority", "risk"}:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE authority section is invalid.")
    if not isinstance(generated, dict) or set(generated) != {"mode", "outputs"}:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE generated section is invalid.")
    if not isinstance(candidate["metadata"], dict) or candidate.get("byte_convention") != {
        "encoding": "UTF-8", "bom": False, "newline": "LF"
    }:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE candidate metadata or byte convention is invalid.")
    hash_fields = (
        candidate.get("sha256"),
        candidate.get("metadata_fingerprint"),
        repository.get("baseline_artifact_set_identity"),
    )
    if any(not isinstance(value, str) or not _SHA256.fullmatch(value) for value in hash_fields):
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE plan contains a malformed hash.")
    baseline_count = repository.get("baseline_artifact_count")
    final_count = repository.get("expected_artifact_count_after")
    if not isinstance(baseline_count, int) or final_count != baseline_count + 1:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE artifact counts are inconsistent.")
    if target.get("absent") is not True or target.get("parent_directory_exists") is not True \
            or target.get("parent_directory_real") is not True or target.get("collision_result") != "PASS":
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE target invariants must be satisfied in the plan.")
    outputs = generated.get("outputs")
    if not isinstance(outputs, list) or any(not isinstance(item, dict) for item in outputs):
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE generated outputs are invalid.")
    if not isinstance(expected_changes, list) or not expected_changes:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE expected_changes must be non-empty.")
    expected_paths = [str(target["declared_path"])] + [
        str(item.get("path")) for item in outputs if item.get("status") == "WOULD_CHANGE"
    ]
    expected_operations = ["DOCUMENT_CREATE"] + ["GENERATED_UPDATE"] * (len(expected_paths) - 1)
    if any(not isinstance(item, dict) or set(item) != {"operation", "path"} for item in expected_changes):
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE expected change entries are invalid.")
    if [item["path"] for item in expected_changes] != expected_paths \
            or [item["operation"] for item in expected_changes] != expected_operations:
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE expected_changes do not match target and generated preview.")
    if candidate.get("canonical_path") != target.get("declared_path"):
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE candidate canonical path differs from target.")
    if not isinstance(plan.get("preconditions"), list) or not isinstance(plan.get("impact"), dict):
        fail("CREATE_PLAN_STRUCTURE_INVALID", "CREATE preconditions or impact section is invalid.")
    return plan
