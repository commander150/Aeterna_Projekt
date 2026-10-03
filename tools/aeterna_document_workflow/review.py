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
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REVIEW_SECTIONS = frozenset({
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
    return validate_plan_integrity(payload)


def finalize_review(payload: dict[str, object]) -> dict[str, object]:
    result = dict(payload)
    result["review_semantic_sha256"] = review_semantic_digest(result)
    return result


def verify_review_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        fail("REVIEW_INVALID", "Review must be a JSON object.")
    missing = sorted(_REVIEW_SECTIONS - set(payload))
    if missing:
        fail("REVIEW_SECTION_MISSING", f"Missing review sections: {', '.join(missing)}.")
    if payload.get("schema_version") != REVIEW_SCHEMA:
        fail("REVIEW_SCHEMA_INVALID", "Unsupported review schema.")
    for field in ("plan_semantic_sha256", "review_semantic_sha256"):
        value = payload.get(field)
        if not isinstance(value, str) or not _SHA256.fullmatch(value):
            fail("REVIEW_HASH_INVALID", f"Invalid {field}.")
    hashes = payload.get("hashes")
    if not isinstance(hashes, dict) or any(
        value is not None and (not isinstance(value, str) or not _SHA256.fullmatch(value))
        for key, value in hashes.items() if key.endswith("sha256")
    ):
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
    lines = [
        "AETERNA DOCUMENT UPDATE REVIEW",
        f"status: {payload['final_status']}",
        f"operation_id: {payload['operation_id']}",
        f"artifact_id: {payload['artifact']['artifact_id']}",
        f"plan_semantic_sha256: {payload['plan_semantic_sha256']}",
        f"review_semantic_sha256: {payload['review_semantic_sha256']}",
        "changed_paths:",
        *[f"- {path}" for path in payload["scope"]["actual_changed_paths"]],
    ]
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return json_path, text_path
