"""Semantic integrity and ignored review evidence for document updates."""

from __future__ import annotations

import hashlib
import copy
import json
from pathlib import Path
import re

from .model import fail


PLAN_SCHEMA = "aeterna-document-update-plan/0.1"
REVIEW_SCHEMA = "aeterna-document-update-review/0.1"
CREATE_PLAN_SCHEMA = "aeterna-document-create-plan/0.1"
CREATE_REVIEW_SCHEMA = "aeterna-document-create-review/0.1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_UPDATE_REVIEW_SECTIONS = frozenset({
    "schema_version",
    "operation_id",
    "operation",
    "plan_semantic_sha256",
    "baseline",
    "artifact",
    "change",
    "hashes",
    "byte_conventions",
    "dependency_impact",
    "generated_outputs",
    "validation",
    "tests",
    "transaction",
    "rollback",
    "scope",
    "git",
    "deviations",
    "final_status",
    "review_semantic_sha256",
})
_CREATE_REVIEW_SECTIONS = frozenset({
    "schema_version",
    "operation_id",
    "operation",
    "plan_semantic_sha256",
    "baseline",
    "target",
    "artifact",
    "candidate",
    "version",
    "authority",
    "dependency_impact",
    "generated_outputs",
    "hashes",
    "validation",
    "tests",
    "transaction",
    "rollback",
    "post_create",
    "scope",
    "git",
    "deviations",
    "final_status",
    "review_semantic_sha256",
})


def _canonical_sha256(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def plan_semantic_digest(plan: dict[str, object]) -> str:
    semantic = dict(plan)
    semantic.pop("plan_semantic_sha256", None)
    return _canonical_sha256(semantic)


def review_semantic_digest(review: dict[str, object]) -> str:
    semantic = copy.deepcopy(review)
    semantic.pop("review_semantic_sha256", None)
    semantic.pop("operation_id", None)
    semantic.pop("timestamp", None)
    transaction = semantic.get("transaction")
    if isinstance(transaction, dict):
        transaction.pop("root", None)
    return _canonical_sha256(semantic)


def _hash_values_valid(value: object) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.endswith("sha256") and item is not None \
                    and (not isinstance(item, str) or not _SHA256.fullmatch(item)):
                return False
            if not _hash_values_valid(item):
                return False
    elif isinstance(value, list):
        return all(_hash_values_valid(item) for item in value)
    return True


def validate_plan_integrity(plan: object) -> dict[str, object]:
    if not isinstance(plan, dict):
        fail("PLAN_INVALID", "Plan must be a JSON object.")
    if plan.get("schema_version") != PLAN_SCHEMA:
        fail("PLAN_SCHEMA_INVALID", "Unsupported plan schema.")
    digest = plan.get("plan_semantic_sha256")
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
        fail("PLAN_INTEGRITY_MISMATCH", "Plan semantic digest is missing or malformed.", exit_code=3)
    if digest != plan_semantic_digest(plan):
        fail("PLAN_INTEGRITY_MISMATCH", "Plan semantic digest does not match plan content.", exit_code=3)
    return plan


def load_plan(path: str | Path) -> dict[str, object]:
    target = Path(path)
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail("PLAN_READ_ERROR", f"{target}: {exc}", exit_code=2)
    if isinstance(payload, dict) and payload.get("schema_version") == CREATE_PLAN_SCHEMA:
        from .create_planner import validate_create_plan_integrity

        return validate_create_plan_integrity(payload)
    return validate_plan_integrity(payload)


def finalize_review(payload: dict[str, object]) -> dict[str, object]:
    result = dict(payload)
    result["review_semantic_sha256"] = review_semantic_digest(result)
    return result


def verify_review_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        fail("REVIEW_INVALID", "Review must be a JSON object.")
    schema = payload.get("schema_version")
    if schema == REVIEW_SCHEMA:
        required = _UPDATE_REVIEW_SECTIONS
        expected_operation = "update"
    elif schema == CREATE_REVIEW_SCHEMA:
        required = _CREATE_REVIEW_SECTIONS
        expected_operation = "create"
    else:
        fail("REVIEW_SCHEMA_INVALID", "Unsupported review schema.")
    missing = sorted(required - set(payload))
    if missing:
        fail("REVIEW_SECTION_MISSING", f"Missing review sections: {', '.join(missing)}.")
    if payload.get("operation") != expected_operation:
        fail("REVIEW_OPERATION_INVALID", "Review operation does not match schema.")
    for field in ("plan_semantic_sha256", "review_semantic_sha256"):
        value = payload.get(field)
        if not isinstance(value, str) or not _SHA256.fullmatch(value):
            fail("REVIEW_HASH_INVALID", f"Invalid {field}.")
    hashes = payload.get("hashes")
    if not isinstance(hashes, dict) or not _hash_values_valid(hashes):
        fail("REVIEW_HASH_INVALID", "Review content hash is malformed.")
    if payload["review_semantic_sha256"] != review_semantic_digest(payload):
        fail("REVIEW_INTEGRITY_MISMATCH", "Review semantic digest does not match content.")
    status = payload.get("final_status")
    transaction = payload.get("transaction")
    rollback = payload.get("rollback")
    if status not in {"PASS", "BLOCKED", "FAIL"}:
        fail("REVIEW_STATUS_INVALID", "Invalid final_status.")
    if not isinstance(transaction, dict) or not isinstance(rollback, dict):
        fail("REVIEW_TRANSACTION_INVALID", "Transaction and rollback must be objects.")
    if status == "PASS" and (transaction.get("state") != "COMMITTED_TO_WORKTREE" or rollback.get("performed")):
        fail("REVIEW_STATUS_INCONSISTENT", "PASS review has inconsistent transaction state.")
    if status == "FAIL" and transaction.get("write_started") and not rollback.get("performed"):
        fail("REVIEW_STATUS_INCONSISTENT", "Failed written transaction must record rollback.")
    if status == "BLOCKED" and (transaction.get("write_started") or rollback.get("performed")):
        fail("REVIEW_STATUS_INCONSISTENT", "BLOCKED review cannot record writes or rollback.")
    if rollback.get("verified") and not rollback.get("performed"):
        fail("REVIEW_STATUS_INCONSISTENT", "Verified rollback must have been performed.")
    if schema == CREATE_REVIEW_SCHEMA:
        for section in (
            "baseline", "target", "artifact", "candidate", "version", "authority",
            "dependency_impact", "generated_outputs", "validation", "post_create",
            "scope", "git", "tests",
        ):
            if not isinstance(payload.get(section), dict):
                fail("REVIEW_SECTION_INVALID", f"CREATE review section must be an object: {section}.")
        if status == "PASS" and payload["post_create"].get("final_artifact_count") \
                != payload["post_create"].get("baseline_artifact_count", -1) + 1:
            fail("REVIEW_STATUS_INCONSISTENT", "PASS CREATE review artifact counts are inconsistent.")
        if rollback.get("performed") and transaction.get("write_started") and status != "FAIL":
            fail("REVIEW_STATUS_INCONSISTENT", "CREATE rollback is only valid for failed written transactions.")
    return payload


def verify_review_file(path: str | Path) -> dict[str, object]:
    target = Path(path)
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail("REVIEW_READ_ERROR", f"{target}: {exc}", exit_code=2)
    return verify_review_payload(payload)


def write_review_files(review_dir: Path, payload: dict[str, object]) -> tuple[Path, Path]:
    review_dir.mkdir(parents=True, exist_ok=True)
    json_path = review_dir / "review.json"
    text_path = review_dir / "review.txt"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    heading = (
        "AETERNA DOCUMENT CREATE REVIEW"
        if payload.get("schema_version") == CREATE_REVIEW_SCHEMA
        else "AETERNA DOCUMENT UPDATE REVIEW"
    )
    changed_paths = (
        payload["scope"]["actual_paths"]
        if payload.get("schema_version") == CREATE_REVIEW_SCHEMA
        else payload["scope"]["actual_changed_paths"]
    )
    lines = [
        heading,
        f"status: {payload['final_status']}",
        f"operation_id: {payload['operation_id']}",
        f"artifact_id: {payload['artifact']['artifact_id']}",
        f"plan_semantic_sha256: {payload['plan_semantic_sha256']}",
        f"review_semantic_sha256: {payload['review_semantic_sha256']}",
        "changed_paths:",
        *[f"- {path}" for path in changed_paths],
    ]
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return json_path, text_path
