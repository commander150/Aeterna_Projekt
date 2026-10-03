"""Controlled transaction and sole governed repository write authority."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid

from tools.aeterna_artifacts.generation import DOCUMENT_INDEX_PATH, REGISTRY_PATH, build_generated_content
from tools.aeterna_artifacts.model import Diagnostic, Severity
from tools.aeterna_artifacts.scanner import scan_repository

from .git_state import (
    capture_git_state,
    git_changed_paths,
    git_diff_check,
    git_path_is_ignored,
    git_path_is_tracked,
)
from .model import WorkflowError, fail
from .planner import recompute_prepared_update
from .resolver import resolve_artifact
from .review import (
    REVIEW_SCHEMA,
    finalize_review,
    load_plan,
    write_review_files,
)


@dataclass(frozen=True)
class FailureInjection:
    fail_after_write: int | None = None
    fail_post_validation: bool = False
    fail_rollback_verification: bool = False


@dataclass(frozen=True)
class TransactionResult:
    operation_id: str
    root: str
    states: tuple[str, ...]
    write_started: bool
    writes_completed: int
    rollback_performed: bool
    rollback_verified: bool
    original_hashes_restored: bool


class TransactionExecutionError(Exception):
    def __init__(self, result: TransactionResult, cause: Exception) -> None:
        super().__init__(str(cause))
        self.result = result
        self.cause = cause
        self.exit_code = 4 if result.rollback_verified else 5


class TransactionPreparationError(Exception):
    def __init__(self, result: TransactionResult, cause: Exception) -> None:
        super().__init__(str(cause))
        self.result = result
        self.cause = cause
        self.exit_code = 2


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _relative_inside(root: Path, path: Path, code: str) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        fail(code, f"Path must remain inside repository: {path}")


def _has_reparse_component(root: Path, path: Path) -> bool:
    current = root.resolve()
    try:
        relative = path.absolute().relative_to(current)
    except ValueError:
        return True
    for part in relative.parts:
        current = current / part
        if not current.exists():
            continue
        attributes = getattr(current.lstat(), "st_file_attributes", 0)
        if attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            return True
    return False


def validate_ignored_temp_path(root: Path, path: Path, code: str) -> Path:
    resolved = path.resolve()
    relative = _relative_inside(root, resolved, code)
    parts = Path(relative).parts
    if not parts or parts[0].casefold() != "temp":
        fail(code, "Path must resolve below repository TEMP.")
    if _has_reparse_component(root, path):
        fail(code, "Symlink/reparse path is not allowed.")
    if git_path_is_tracked(root, relative) or not git_path_is_ignored(root, relative):
        fail(code, "TEMP path must be untracked and ignored.")
    return resolved


def validate_candidate_location(root: Path, plan: dict[str, object]) -> Path:
    candidate = Path(plan["candidate"]["resolved_path"]).resolve()
    current = (root / plan["resolved_artifact"]["path"]).resolve()
    if candidate == current:
        fail("CANDIDATE_LOCATION_BLOCKED", "Candidate cannot be the current managed artifact.")
    try:
        relative = candidate.relative_to(root).as_posix()
    except ValueError:
        return candidate
    if _has_reparse_component(root, candidate):
        fail("CANDIDATE_LOCATION_BLOCKED", "Repository candidate cannot use symlink/reparse paths.")
    if not relative.casefold().startswith("temp/"):
        fail("CANDIDATE_LOCATION_BLOCKED", "Repository-local candidate must be below TEMP.")
    if git_path_is_tracked(root, relative) or not git_path_is_ignored(root, relative):
        fail("CANDIDATE_LOCATION_BLOCKED", "Candidate must be untracked and ignored.")
    return candidate


def _journal(path: Path, operation_id: str, states: list[str]) -> None:
    path.write_text(
        json.dumps({"operation_id": operation_id, "states": states}, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def execute_transaction(
    root: Path,
    transaction_root: Path,
    operation_id: str,
    targets: tuple[tuple[str, bytes], ...],
    pre_write_validate: object,
    post_validate: object,
    finalize: object,
    injection: FailureInjection | None = None,
) -> TransactionResult:
    injection = injection or FailureInjection()
    states = ["PREPARING"]
    backups = transaction_root / "backups"
    prepared = transaction_root / "prepared"
    journal = transaction_root / "journal.json"
    baseline: dict[str, tuple[bool, str | None]] = {}
    ordered = tuple(targets)
    try:
        backups.mkdir(parents=True, exist_ok=False)
        prepared.mkdir(parents=True, exist_ok=False)
        for index, (relative, data) in enumerate(ordered):
            target = root / relative
            existed = target.exists()
            original = target.read_bytes() if existed else b""
            baseline[relative] = (existed, _sha256(original) if existed else None)
            if existed:
                (backups / f"{index}.bin").write_bytes(original)
            (prepared / f"{index}.bin").write_bytes(data)
        states.append("PREPARED")
        _journal(journal, operation_id, states)
        pre_write_validate()
        states.append("WRITING")
        _journal(journal, operation_id, states)
    except WorkflowError:
        raise
    except Exception as exc:
        states.append("PREPARATION_FAILED")
        result = TransactionResult(
            operation_id,
            str(transaction_root),
            tuple(states),
            False,
            0,
            False,
            False,
            False,
        )
        raise TransactionPreparationError(result, exc) from exc
    writes = 0
    try:
        for index, (relative, _) in enumerate(ordered):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(prepared / f"{index}.bin", target)
            writes += 1
            if injection.fail_after_write == writes:
                raise RuntimeError(f"Injected failure after governed write {writes}.")
        states.append("POST_VALIDATING")
        _journal(journal, operation_id, states)
        if injection.fail_post_validation:
            raise RuntimeError("Injected post-write validation failure.")
        post_validate()
        result = TransactionResult(operation_id, str(transaction_root), tuple(states + ["COMMITTED_TO_WORKTREE"]), True, writes, False, False, False)
        finalize(result)
        states.append("COMMITTED_TO_WORKTREE")
        _journal(journal, operation_id, states)
        return TransactionResult(operation_id, str(transaction_root), tuple(states), True, writes, False, False, False)
    except Exception as exc:
        states.append("ROLLING_BACK")
        _journal(journal, operation_id, states)
        rollback_error: Exception | None = None
        for index in reversed(range(writes)):
            relative, _ = ordered[index]
            target = root / relative
            existed, _ = baseline[relative]
            try:
                if existed:
                    os.replace(backups / f"{index}.bin", target)
                elif target.exists():
                    target.unlink()
            except Exception as restore_exc:
                rollback_error = restore_exc
        hashes_restored = all(
            ((root / relative).exists() == existed)
            and (not existed or _sha256((root / relative).read_bytes()) == digest)
            for relative, (existed, digest) in baseline.items()
        )
        status_restored = capture_git_state(root).clean
        verified = (
            hashes_restored
            and status_restored
            and rollback_error is None
            and not injection.fail_rollback_verification
        )
        states.append("ROLLED_BACK" if verified else "ROLLBACK_FAILED")
        _journal(journal, operation_id, states)
        result = TransactionResult(operation_id, str(transaction_root), tuple(states), writes > 0, writes, True, verified, hashes_restored)
        cause = rollback_error or exc
        raise TransactionExecutionError(result, cause) from cause


def _review_payload(
    plan: dict[str, object],
    operation_id: str,
    status: str,
    transaction: TransactionResult,
    changed_paths: tuple[str, ...],
    deviations: list[str],
) -> dict[str, object]:
    target = plan["resolved_artifact"]["path"]
    root = Path(plan["repository"]["root"])
    final_hash = _sha256((root / target).read_bytes()) if (root / target).exists() else None
    payload = {
        "schema_version": REVIEW_SCHEMA,
        "operation_id": operation_id,
        "operation": "update",
        "plan_semantic_sha256": plan["plan_semantic_sha256"],
        "baseline": plan["baseline"],
        "artifact": {"artifact_id": plan["artifact_id"], "path": target},
        "change": plan["change"],
        "hashes": {"baseline_sha256": plan["baseline"]["sha256"], "candidate_sha256": plan["candidate"]["sha256"], "final_sha256": final_hash},
        "byte_conventions": {"baseline": plan["baseline"]["byte_convention"], "candidate": plan["candidate"]["byte_convention"]},
        "dependency_impact": plan["impact"],
        "generated_outputs": plan["generated"],
        "validation": {"plan_integrity": "PASS", "recomputed_plan_match": "PASS" if status != "BLOCKED" else "BLOCKED"},
        "tests": {"executed_during_apply": []},
        "transaction": {"root": transaction.root, "state": transaction.states[-1], "states": list(transaction.states), "write_started": transaction.write_started, "writes_completed": transaction.writes_completed},
        "rollback": {"performed": transaction.rollback_performed, "verified": transaction.rollback_verified, "original_hashes_restored": transaction.original_hashes_restored},
        "scope": {"expected_changed_paths": [item["path"] for item in plan["expected_changes"]], "actual_changed_paths": list(changed_paths)},
        "git": {"staging_empty": not capture_git_state(root).staged_paths, "diff_check": git_diff_check(root)},
        "deviations": deviations,
        "final_status": status,
    }
    return finalize_review(payload)


def apply_plan(
    plan_path: str | Path,
    repository_root: str | Path,
    review_directory: str | Path,
    *,
    injection: FailureInjection | None = None,
) -> dict[str, object]:
    root = Path(repository_root).resolve()
    plan = load_plan(plan_path)
    review_dir = validate_ignored_temp_path(root, Path(review_directory), "REVIEW_DIRECTORY_BLOCKED")
    operation_id = uuid.uuid4().hex
    proposed_transaction_root = root / "TEMP/aeterna_document_workflow/transactions" / operation_id

    def blocked_review(exc: WorkflowError, transaction_root: str = "") -> None:
        blocked = TransactionResult(
            operation_id,
            transaction_root,
            ("PREPARED",),
            False,
            0,
            False,
            False,
            False,
        )
        review = _review_payload(
            plan,
            operation_id,
            "BLOCKED",
            blocked,
            git_changed_paths(root),
            [str(exc)],
        )
        write_review_files(review_dir, review)

    try:
        validate_candidate_location(root, plan)
        if plan["change"]["class"] == "semantic-governance-change":
            fail("SEMANTIC_GOVERNANCE_APPLY_BLOCKED", "High-risk semantic governance plans cannot be applied.")
        prepared = recompute_prepared_update(root, plan)
        if prepared.plan != plan:
            fail("PLAN_RECOMPUTATION_MISMATCH", "Recomputed semantic plan differs from supplied plan.", exit_code=3)
        expected = tuple(item["path"] for item in plan["expected_changes"])
        actual = tuple(path for path, _ in prepared.target_bytes)
        if expected != actual:
            fail("EXPECTED_CHANGES_MISMATCH", "Recomputed transaction target set differs from plan.", exit_code=3)
        generated_whitelist = {REGISTRY_PATH.as_posix(), DOCUMENT_INDEX_PATH.as_posix()}
        current_path = plan["resolved_artifact"]["path"]
        for relative in actual:
            folded = Path(relative).parts[0].casefold()
            if folded in {"archive", "learning"} or (relative != current_path and relative not in generated_whitelist):
                fail("TRANSACTION_PATH_BLOCKED", f"Governed target is outside the allowed set: {relative}")
            _relative_inside(root, root / relative, "TRANSACTION_PATH_BLOCKED")
        transaction_parent = validate_ignored_temp_path(
            root,
            root / "TEMP/aeterna_document_workflow/transactions",
            "TRANSACTION_ROOT_BLOCKED",
        )
        proposed_transaction_root = transaction_parent / operation_id
        if transaction_parent.drive.casefold() != root.drive.casefold():
            fail("TRANSACTION_VOLUME_MISMATCH", "Transaction and repository targets must share a volume.")
        transaction_root = proposed_transaction_root
    except WorkflowError as exc:
        blocked_review(exc, str(proposed_transaction_root))
        raise

    def pre_write_validate() -> None:
        second = recompute_prepared_update(root, plan)
        if second.plan != plan or second.target_bytes != prepared.target_bytes:
            fail("PREWRITE_RECOMPUTATION_MISMATCH", "Pre-write recomputation drifted.", exit_code=3)

    def post_validate() -> None:
        scan = scan_repository(root)
        if len(scan.artifacts) != plan["repository"]["artifact_count"] or any(item.severity in {Severity.ERROR, Severity.BLOCKING} for item in scan.diagnostics):
            raise RuntimeError("Post-write artifact scan failed.")
        resolved = resolve_artifact(root, plan["artifact_id"])
        if resolved.record.path != current_path:
            raise RuntimeError("Post-write artifact identity/path changed.")
        for relative, data in prepared.target_bytes:
            if (root / relative).read_bytes() != data:
                raise RuntimeError(f"Post-write byte mismatch: {relative}")
        rendered = build_generated_content(scan.artifacts)
        if (root / REGISTRY_PATH).read_bytes() != rendered.registry.encode("utf-8") or (root / DOCUMENT_INDEX_PATH).read_bytes() != rendered.document_index.encode("utf-8"):
            raise RuntimeError("Post-write generated output mismatch.")
        if git_changed_paths(root) != tuple(sorted(expected)) or capture_git_state(root).staged_paths or not git_diff_check(root):
            raise RuntimeError("Post-write Git scope validation failed.")

    review_paths: tuple[Path, Path] | None = None
    def finalize(result: TransactionResult) -> None:
        nonlocal review_paths
        review = _review_payload(plan, operation_id, "PASS", result, git_changed_paths(root), [])
        review_paths = write_review_files(review_dir, review)

    try:
        result = execute_transaction(
            root,
            transaction_root,
            operation_id,
            prepared.target_bytes,
            pre_write_validate,
            post_validate,
            finalize,
            injection,
        )
    except WorkflowError as exc:
        blocked_review(exc, str(transaction_root))
        raise
    except TransactionPreparationError as exc:
        review = _review_payload(
            plan,
            operation_id,
            "FAIL",
            exc.result,
            git_changed_paths(root),
            [str(exc.cause)],
        )
        write_review_files(review_dir, review)
        diagnostic = Diagnostic(
            "TRANSACTION_PREPARATION_FAILED",
            Severity.ERROR,
            str(exc.cause),
        )
        raise WorkflowError((diagnostic,), 2) from exc
    except TransactionExecutionError as exc:
        review = _review_payload(plan, operation_id, "FAIL", exc.result, git_changed_paths(root), [str(exc.cause)])
        write_review_files(review_dir, review)
        diagnostic = Diagnostic(
            "ROLLBACK_VERIFICATION_FAILED" if exc.exit_code == 5 else "TRANSACTION_FAILED_ROLLED_BACK",
            Severity.ERROR,
            str(exc.cause),
        )
        raise WorkflowError((diagnostic,), exc.exit_code) from exc
    assert review_paths is not None
    return {
        "status": "PASS",
        "operation_id": operation_id,
        "artifact_id": plan["artifact_id"],
        "changed_paths": list(git_changed_paths(root)),
        "review_json": str(review_paths[0]),
        "review_text": str(review_paths[1]),
    }
