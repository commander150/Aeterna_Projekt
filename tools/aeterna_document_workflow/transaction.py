"""Controlled transaction and sole governed repository write authority."""

from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import errno
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import uuid
from typing import Iterator

from tools.aeterna_artifacts.generation import DOCUMENT_INDEX_PATH, REGISTRY_PATH, build_generated_content
from tools.aeterna_artifacts.model import Diagnostic, Severity
from tools.aeterna_artifacts.scanner import scan_repository

from .git_state import (
    capture_git_state,
    git_changed_paths,
    git_content_matches_head,
    git_diff_check,
    git_path_is_ignored,
    git_path_is_tracked,
)
from .governance_approval import (
    GovernanceApproval,
    approval_binding,
    approval_review,
    confirm_governance_apply,
    confirm_governance_gui,
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


_ACTIVE_APPLY_ROOT: ContextVar[str | None] = ContextVar("active_aeterna_apply_root", default=None)


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


def durable_apply_state_root(root: Path) -> Path:
    """Use this checkout's Git administration directory, never disposable TEMP."""
    root = root.resolve()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--absolute-git-dir"], cwd=root,
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
    except OSError as exc:
        fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", f"Cannot identify repository Git administration directory: {exc}")
    if result.returncode or not result.stdout.strip():
        fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", "Cannot identify repository Git administration directory.")
    git_dir = Path(result.stdout.strip()).resolve()
    if os.stat(root).st_dev != os.stat(git_dir).st_dev:
        fail("TRANSACTION_VOLUME_MISMATCH", "Durable Apply state and repository targets must share a volume.")
    state_root = git_dir / "aeterna_document_workflow"
    if state_root.exists():
        attributes = getattr(state_root.lstat(), "st_file_attributes", 0)
        if not state_root.is_dir() or state_root.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", "Durable Apply state directory must be a plain directory.")
    return state_root


def durable_transaction_parent(root: Path) -> Path:
    state_root = durable_apply_state_root(root)
    transaction_parent = state_root / "transactions"
    if transaction_parent.exists():
        attributes = getattr(transaction_parent.lstat(), "st_file_attributes", 0)
        if not transaction_parent.is_dir() or transaction_parent.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            fail("TRANSACTION_ROOT_BLOCKED", "Durable transaction directory must be a plain directory.")
    return transaction_parent


def _same_volume(root: Path, transaction_parent: Path) -> bool:
    return os.stat(root).st_dev == os.stat(transaction_parent.parent).st_dev


def _check_legacy_transaction_evidence(root: Path) -> None:
    parent = root / "TEMP/aeterna_document_workflow/transactions"
    if not os.path.lexists(parent):
        return
    validate_ignored_temp_path(root, parent, "APPLY_LOCK_INFRASTRUCTURE_ERROR")
    if not parent.is_dir():
        fail("APPLY_RECOVERY_REQUIRED", "Previous TEMP transaction evidence is not a directory.", exit_code=3)
    try:
        for child in parent.iterdir():
            if child.is_symlink() or not child.is_dir():
                fail("APPLY_RECOVERY_REQUIRED", "Previous TEMP transaction evidence is incomplete.", exit_code=3)
            journal = json.loads((child / "journal.json").read_text(encoding="utf-8"))
            if (not isinstance(journal, dict) or journal.get("operation_id") != child.name
                    or not isinstance(journal.get("states"), list)
                    or not journal["states"] or journal["states"][-1] not in {"COMMITTED_TO_WORKTREE", "ROLLED_BACK"}):
                fail("APPLY_RECOVERY_REQUIRED", "Previous TEMP transaction requires recovery review.", exit_code=3)
    except (OSError, ValueError, UnicodeError, KeyError, TypeError):
        fail("APPLY_RECOVERY_REQUIRED", "Previous TEMP transaction evidence is missing or invalid.", exit_code=3)


def _lock_byte(fd: int) -> None:
    os.lseek(fd, 0, os.SEEK_SET)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    elif os.name == "posix":
        import fcntl

        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    else:
        fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", "Exclusive Apply locking is unsupported on this platform.")


def _unlock_byte(fd: int) -> None:
    os.lseek(fd, 0, os.SEEK_SET)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(fd, fcntl.LOCK_UN)


def _lock_record(fd: int) -> dict[str, object]:
    os.lseek(fd, 1, os.SEEK_SET)
    data = os.read(fd, max(0, os.fstat(fd).st_size - 1))
    record = json.loads(data.decode("utf-8"))
    if not isinstance(record, dict) or record.get("schema") != "aeterna-apply-lock/0.1":
        raise ValueError("Invalid Apply lock record.")
    return record


def _write_lock_record(fd: int, status: str, operation_id: str) -> None:
    record = {
        "schema": "aeterna-apply-lock/0.1",
        "status": status,
        "operation_id": operation_id,
        "pid": os.getpid(),
        "updated_utc": datetime.now(timezone.utc).isoformat(),
    }
    data = json.dumps(record, sort_keys=True).encode("utf-8")
    os.lseek(fd, 1, os.SEEK_SET)
    written = 0
    while written < len(data):
        count = os.write(fd, data[written:])
        if count <= 0:
            raise OSError("Apply lock record write did not progress.")
        written += count
    os.ftruncate(fd, 1 + len(data))
    os.fsync(fd)


@contextmanager
def repository_apply_lock(repository_root: str | Path) -> Iterator[None]:
    """Serialize CREATE and UPDATE across processes; retain crash evidence."""
    root = Path(repository_root).resolve()
    state_root = durable_apply_state_root(root)
    lock_path = state_root / "apply.lock"
    legacy_path = root / "TEMP/aeterna_document_workflow/apply.lock"
    try:
        state_root.mkdir(parents=True, exist_ok=True)
        if durable_apply_state_root(root) != state_root:
            fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", "Repository Git administration directory changed.")
        flags = os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        if os.path.lexists(lock_path):
            info = lock_path.lstat()
            if not stat.S_ISREG(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
                fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", "Durable Apply marker must be a plain file.")
        try:
            fd = os.open(lock_path, flags | os.O_CREAT | os.O_EXCL, 0o600)
            created = True
        except FileExistsError:
            fd = os.open(lock_path, flags)
            created = False
    except OSError as exc:
        fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", f"Cannot open repository Apply lock: {exc}")
    operation_id = uuid.uuid4().hex
    locked = False
    legacy_fd: int | None = None
    legacy_locked = False
    try:
        try:
            _lock_byte(fd)
            locked = True
        except OSError as exc:
            if exc.errno in {errno.EACCES, errno.EAGAIN} or getattr(exc, "winerror", None) == 33:
                fail("APPLY_ALREADY_IN_PROGRESS", "Another governed Apply holds the repository lock.", exit_code=3)
            fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", f"Cannot acquire repository Apply lock: {exc}")
        try:
            if not created and _lock_record(fd).get("status") != "RELEASED":
                fail("APPLY_RECOVERY_REQUIRED", "Previous Apply may have been interrupted; inspect retained transaction evidence.", exit_code=3)
        except (ValueError, UnicodeError):
            fail("APPLY_RECOVERY_REQUIRED", "Apply lock record is incomplete or invalid; inspect retained transaction evidence.", exit_code=3)
        except OSError as exc:
            fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", f"Cannot read repository Apply lock record: {exc}")
        transaction_parent = state_root / "transactions"
        if created and os.path.lexists(transaction_parent):
            info = transaction_parent.lstat()
            if not stat.S_ISDIR(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
                fail("APPLY_RECOVERY_REQUIRED", "Durable transaction evidence path is invalid.", exit_code=3)
            if any(transaction_parent.iterdir()):
                fail("APPLY_RECOVERY_REQUIRED", "Durable Apply marker is missing while transaction evidence exists.", exit_code=3)
        if created:
            try:
                _write_lock_record(fd, "RELEASED", operation_id)
            except OSError as exc:
                fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", f"Cannot initialize durable Apply marker: {exc}")
        # A previous version used TEMP. Hold its lock as well during migration so
        # an existing process cannot be bypassed; never remove or rewrite it.
        if os.path.lexists(legacy_path):
            validate_ignored_temp_path(root, legacy_path, "APPLY_LOCK_INFRASTRUCTURE_ERROR")
            try:
                legacy_fd = os.open(legacy_path, flags)
                _lock_byte(legacy_fd)
                legacy_locked = True
            except OSError as exc:
                if exc.errno in {errno.EACCES, errno.EAGAIN} or getattr(exc, "winerror", None) == 33:
                    fail("APPLY_ALREADY_IN_PROGRESS", "Previous TEMP-based Apply holds the repository lock.", exit_code=3)
                fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", f"Cannot inspect previous TEMP-based Apply lock: {exc}")
            try:
                if _lock_record(legacy_fd).get("status") != "RELEASED":
                    fail("APPLY_RECOVERY_REQUIRED", "Previous TEMP-based Apply is not released; inspect its recovery evidence.", exit_code=3)
            except (ValueError, UnicodeError):
                fail("APPLY_RECOVERY_REQUIRED", "Previous TEMP-based Apply marker is invalid; inspect its recovery evidence.", exit_code=3)
            except OSError as exc:
                fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", f"Cannot read previous TEMP-based Apply marker: {exc}")
        _check_legacy_transaction_evidence(root)
        try:
            _write_lock_record(fd, "ACTIVE", operation_id)
        except OSError as exc:
            fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", f"Cannot record active Apply lock: {exc}")
        completed = False
        token = _ACTIVE_APPLY_ROOT.set(str(root))
        try:
            yield
            completed = True
        except WorkflowError as exc:
            completed = all(item.code != "ROLLBACK_VERIFICATION_FAILED" for item in exc.diagnostics)
            raise
        finally:
            _ACTIVE_APPLY_ROOT.reset(token)
            if completed:
                try:
                    _write_lock_record(fd, "RELEASED", operation_id)
                except OSError as exc:
                    fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", f"Cannot record released Apply lock: {exc}")
    finally:
        try:
            if legacy_fd is not None:
                try:
                    if legacy_locked:
                        _unlock_byte(legacy_fd)
                finally:
                    os.close(legacy_fd)
            if locked:
                try:
                    _unlock_byte(fd)
                except OSError as exc:
                    fail("APPLY_LOCK_INFRASTRUCTURE_ERROR", f"Cannot release repository Apply lock: {exc}")
        finally:
            os.close(fd)


def require_repository_apply_lock(root: Path) -> None:
    if _ACTIVE_APPLY_ROOT.get() != str(root.resolve()):
        fail("APPLY_LOCK_REQUIRED", "Governed repository writes require the shared Apply lock.")


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
    data = (json.dumps({"operation_id": operation_id, "states": states}, indent=2) + "\n").encode("utf-8")
    pending = path.with_name(path.name + ".pending")
    _write_synced_bytes(pending, data)
    os.replace(pending, path)


def _write_synced_bytes(path: Path, data: bytes) -> None:
    with path.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def execute_transaction(
    root: Path,
    transaction_root: Path,
    operation_id: str,
    targets: tuple[tuple[str, bytes], ...],
    pre_write_validate: object,
    post_validate: object,
    finalize: object,
    injection: FailureInjection | None = None,
    *,
    create_parents: bool = True,
) -> TransactionResult:
    require_repository_apply_lock(root)
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
            existed = os.path.lexists(target)
            original = target.read_bytes() if existed else b""
            baseline[relative] = (existed, _sha256(original) if existed else None)
            if existed:
                _write_synced_bytes(backups / f"{index}.bin", original)
            _write_synced_bytes(prepared / f"{index}.bin", data)
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
            if create_parents:
                target.parent.mkdir(parents=True, exist_ok=True)
            elif not target.parent.is_dir():
                raise RuntimeError(f"Governed target parent is not an existing directory: {relative}")
            existed, _ = baseline[relative]
            if not existed and os.path.lexists(target):
                raise RuntimeError(f"Previously absent governed target appeared before write: {relative}")
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
        restore_copies = transaction_root / "restore"
        for index in reversed(range(writes)):
            relative, _ = ordered[index]
            target = root / relative
            existed, _ = baseline[relative]
            try:
                if existed:
                    restore_copies.mkdir(exist_ok=True)
                    restore_copy = restore_copies / f"{index}.bin"
                    shutil.copyfile(backups / f"{index}.bin", restore_copy)
                    with restore_copy.open("rb+") as stream:
                        os.fsync(stream.fileno())
                    os.replace(restore_copy, target)
                elif os.path.lexists(target):
                    target.unlink()
            except Exception as restore_exc:
                rollback_error = restore_exc
        hashes_restored = all(
            (os.path.lexists(root / relative) == existed)
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
    expected_git_paths: tuple[str, ...] | None = None,
    normalized_unchanged_generated: tuple[str, ...] = (),
    governance_approval: dict[str, object] | None = None,
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
        "scope": {
            "expected_changed_paths": [item["path"] for item in plan["expected_changes"]],
            "actual_changed_paths": list(changed_paths),
            "planned_write_paths": [item["path"] for item in plan["expected_changes"]],
            "expected_git_changed_paths": list(expected_git_paths) if expected_git_paths is not None else None,
            "actual_git_changed_paths": list(changed_paths),
            "git_normalized_unchanged_generated_paths": list(normalized_unchanged_generated),
        },
        "git": {"staging_empty": not capture_git_state(root).staged_paths, "diff_check": git_diff_check(root)},
        "deviations": deviations,
        "final_status": status,
    }
    if plan["change"]["class"] == "semantic-governance-change":
        payload["repository"] = {"root": plan["repository"]["root"]}
        payload["version"] = plan["version"]
        payload["governance_approval"] = governance_approval or approval_review(
            approval_binding(plan, root, operation_id),
        )
    return finalize_review(payload)


def apply_plan(
    plan_path: str | Path,
    repository_root: str | Path,
    review_directory: str | Path,
    *,
    injection: FailureInjection | None = None,
) -> dict[str, object]:
    with repository_apply_lock(repository_root):
        return _apply_plan_under_lock(
            plan_path, repository_root, review_directory, injection=injection,
        )


def apply_governance_plan(
    plan_path: str | Path,
    repository_root: str | Path,
    review_directory: str | Path,
    *,
    injection: FailureInjection | None = None,
) -> dict[str, object]:
    """Separate, terminal-confirmed UPDATE entrypoint; ordinary Apply stays closed."""
    with repository_apply_lock(repository_root):
        return _apply_plan_under_lock(
            plan_path, repository_root, review_directory,
            injection=injection, governance_interactive=True,
        )


def apply_governance_gui_plan(
    plan_path: str | Path, repository_root: str | Path, review_directory: str | Path,
) -> dict[str, object]:
    """Use the same production transaction with a process-local GUI challenge."""
    with repository_apply_lock(repository_root):
        return _apply_plan_under_lock(
            plan_path, repository_root, review_directory,
            governance_interactive=True, governance_gui=True,
        )


def _apply_plan_under_lock(
    plan_path: str | Path,
    repository_root: str | Path,
    review_directory: str | Path,
    *,
    injection: FailureInjection | None = None,
    governance_interactive: bool = False,
    governance_gui: bool = False,
) -> dict[str, object]:
    root = Path(repository_root).resolve()
    require_repository_apply_lock(root)
    plan = load_plan(plan_path)
    review_dir = validate_ignored_temp_path(root, Path(review_directory), "REVIEW_DIRECTORY_BLOCKED")
    if plan.get("schema_version") == "aeterna-document-create-plan/0.1":
        if governance_interactive:
            fail("SEMANTIC_GOVERNANCE_APPLY_BLOCKED", "Governance approval is only for UPDATE plans.")
        from .create_transaction import _apply_create_plan_under_lock

        return _apply_create_plan_under_lock(plan, root, review_dir, injection=injection)
    operation_id = uuid.uuid4().hex
    proposed_transaction_root: Path | None = None
    expected_git_paths: tuple[str, ...] | None = None
    normalized_unchanged_generated: tuple[str, ...] = ()
    approval: GovernanceApproval | None = None

    def approval_evidence() -> dict[str, object] | None:
        if approval is None or approval.binding != approval_binding(plan, root, operation_id):
            return None
        return approval.review()

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
            expected_git_paths,
            normalized_unchanged_generated,
            approval_evidence(),
        )
        write_review_files(review_dir, review)

    try:
        validate_candidate_location(root, plan)
        high_risk = plan["change"]["class"] == "semantic-governance-change"
        if high_risk and not governance_interactive:
            fail("SEMANTIC_GOVERNANCE_APPLY_BLOCKED", "High-risk semantic governance plans cannot be applied.")
        if governance_interactive and not high_risk:
            fail("SEMANTIC_GOVERNANCE_APPLY_BLOCKED", "Governance approval requires a high-risk UPDATE plan.")
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
        normalized_unchanged_generated = tuple(sorted(
            relative for relative, data in prepared.target_bytes
            if relative in generated_whitelist and git_content_matches_head(root, relative, data)
        ))
        expected_git_paths = tuple(sorted(
            relative for relative in expected if relative not in normalized_unchanged_generated
        ))
        transaction_parent = durable_transaction_parent(root)
        proposed_transaction_root = transaction_parent / operation_id
        if not _same_volume(root, transaction_parent):
            fail("TRANSACTION_VOLUME_MISMATCH", "Transaction and repository targets must share a volume.")
        transaction_root = proposed_transaction_root
        if high_risk:
            approval = (confirm_governance_gui if governance_gui else confirm_governance_apply)(plan, root, operation_id)
    except WorkflowError as exc:
        blocked_review(exc, str(proposed_transaction_root) if proposed_transaction_root else "")
        raise

    def pre_write_validate() -> None:
        second = recompute_prepared_update(root, plan)
        if second.plan != plan or second.target_bytes != prepared.target_bytes:
            fail("PREWRITE_RECOMPUTATION_MISMATCH", "Pre-write recomputation drifted.", exit_code=3)
        if approval is not None:
            approval.consume(plan, root, operation_id)

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
        git_paths = git_changed_paths(root)
        state = capture_git_state(root)
        normalized_still_unchanged = all(
            git_content_matches_head(root, relative, data)
            for relative, data in prepared.target_bytes
            if relative in normalized_unchanged_generated
        )
        if (
            current_path not in git_paths
            or git_paths != expected_git_paths
            or state.worktree_entries != expected_git_paths
            or state.staged_paths
            or not normalized_still_unchanged
            or not git_diff_check(root)
        ):
            raise RuntimeError("Post-write Git scope validation failed.")

    review_paths: tuple[Path, Path] | None = None
    def finalize(result: TransactionResult) -> None:
        nonlocal review_paths
        review = _review_payload(
            plan, operation_id, "PASS", result, git_changed_paths(root), [],
            expected_git_paths, normalized_unchanged_generated,
            approval_evidence(),
        )
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
            expected_git_paths,
            normalized_unchanged_generated,
            approval_evidence(),
        )
        write_review_files(review_dir, review)
        diagnostic = Diagnostic(
            "TRANSACTION_PREPARATION_FAILED",
            Severity.ERROR,
            str(exc.cause),
        )
        raise WorkflowError((diagnostic,), 2) from exc
    except TransactionExecutionError as exc:
        review = _review_payload(
            plan, operation_id, "FAIL", exc.result, git_changed_paths(root),
            [str(exc.cause)], expected_git_paths, normalized_unchanged_generated,
            approval_evidence(),
        )
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
