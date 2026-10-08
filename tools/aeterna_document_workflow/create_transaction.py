"""Transactional execution of an immutable, human-materialized CREATE plan."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import uuid

from tools.aeterna_artifacts.generation import (
    DOCUMENT_INDEX_PATH,
    REGISTRY_PATH,
    build_generated_content,
)
from tools.aeterna_artifacts.model import Diagnostic, Severity
from tools.aeterna_artifacts.scanner import scan_repository

from .content import inspect_markdown_bytes
from .create_planner import recompute_prepared_create
from .git_state import capture_git_state, git_diff_check, git_path_is_tracked
from .model import WorkflowError, fail
from .resolver import resolve_artifact
from .review import CREATE_REVIEW_SCHEMA, finalize_review, write_review_files
from .transaction import (
    FailureInjection,
    TransactionExecutionError,
    TransactionPreparationError,
    TransactionResult,
    execute_transaction,
    validate_ignored_temp_path,
)


_GENERATED_PATHS = frozenset({REGISTRY_PATH.as_posix(), DOCUMENT_INDEX_PATH.as_posix()})


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha256(path: Path) -> str | None:
    if not os.path.lexists(path) or not path.is_file() or path.is_symlink():
        return None
    return _sha256(path.read_bytes())


def _has_trailing_whitespace(data: bytes) -> bool:
    return any(line.endswith((b" ", b"\t")) for line in data.splitlines())


def _artifact_count(root: Path) -> int | None:
    try:
        return len(scan_repository(root).artifacts)
    except Exception:
        return None


def _create_review_payload(
    plan: dict[str, object],
    operation_id: str,
    status: str,
    transaction: TransactionResult,
    actual_paths: tuple[str, ...],
    deviations: list[str],
    *,
    recomputed: str,
    post_validation: str,
) -> dict[str, object]:
    root = Path(str(plan["repository"]["root"]))
    target_path = str(plan["target"]["declared_path"])
    target = root / target_path
    candidate = plan["candidate"]
    generated_hashes: dict[str, object] = {}
    for output in plan["generated"]["outputs"]:
        if output["status"] == "WOULD_CHANGE":
            relative = str(output["path"])
            generated_hashes[relative] = {
                "planned_rendered_sha256": output["rendered_sha256"],
                "final_sha256": _file_sha256(root / relative),
            }
    state = capture_git_state(root)
    direct_text_check = (
        "PASS"
        if status == "PASS" and target.is_file() and not _has_trailing_whitespace(target.read_bytes())
        else "NOT_RUN"
    )
    payload = {
        "schema_version": CREATE_REVIEW_SCHEMA,
        "operation_id": operation_id,
        "operation": "create",
        "plan_semantic_sha256": plan["plan_semantic_sha256"],
        "baseline": {
            **plan["baseline"],
            "artifact_count": plan["repository"]["baseline_artifact_count"],
            "artifact_set_identity": plan["repository"]["baseline_artifact_set_identity"],
        },
        "target": {
            "declared_path": target_path,
            "pre_write_absence": plan["target"]["absent"],
        },
        "artifact": {
            "artifact_id": plan["artifact_id"],
            "final_target_path": target_path,
            "metadata": candidate["metadata"],
            "title": candidate["title"],
        },
        "candidate": {
            "sha256": candidate["sha256"],
            "byte_convention": candidate["byte_convention"],
        },
        "version": plan["version"],
        "authority": plan["authority"],
        "dependency_impact": plan["impact"],
        "generated_outputs": plan["generated"],
        "hashes": {
            "candidate_sha256": candidate["sha256"],
            "final_target_sha256": _file_sha256(target),
            "generated": generated_hashes,
        },
        "validation": {
            "plan_integrity": "PASS",
            "recomputed_create_plan_match": recomputed,
            "post_write": post_validation,
        },
        "tests": {"executed_during_apply": []},
        "transaction": {
            "root": transaction.root,
            "state": transaction.states[-1],
            "states": list(transaction.states),
            "write_started": transaction.write_started,
            "writes_completed": transaction.writes_completed,
        },
        "rollback": {
            "performed": transaction.rollback_performed,
            "verified": transaction.rollback_verified,
            "original_hashes_restored": transaction.original_hashes_restored,
            "new_target_absent": not os.path.lexists(target),
        },
        "post_create": {
            "baseline_artifact_count": plan["repository"]["baseline_artifact_count"],
            "final_artifact_count": _artifact_count(root),
        },
        "scope": {
            "expected_paths": [item["path"] for item in plan["expected_changes"]],
            "actual_paths": list(actual_paths),
            "expected_untracked_target": target_path,
        },
        "git": {
            "staging_empty": not state.staged_paths,
            "diff_check": git_diff_check(root),
            "target_direct_text_check": direct_text_check,
        },
        "deviations": deviations,
        "final_status": status,
    }
    return finalize_review(payload)


def apply_create_plan(
    plan: dict[str, object],
    root: Path,
    review_dir: Path,
    *,
    injection: FailureInjection | None = None,
) -> dict[str, object]:
    operation_id = uuid.uuid4().hex
    proposed_transaction_root = root / "TEMP/aeterna_document_workflow/transactions" / operation_id

    def worktree_paths() -> tuple[str, ...]:
        return capture_git_state(root).worktree_entries

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
        review = _create_review_payload(
            plan,
            operation_id,
            "BLOCKED",
            blocked,
            worktree_paths(),
            [str(exc)],
            recomputed="BLOCKED",
            post_validation="NOT_RUN",
        )
        write_review_files(review_dir, review)

    try:
        prepared = recompute_prepared_create(root, plan)
        if prepared.plan != plan:
            fail(
                "CREATE_PLAN_RECOMPUTATION_MISMATCH",
                "Recomputed semantic CREATE plan differs from supplied plan.",
                exit_code=3,
            )
        expected = tuple(str(item["path"]) for item in plan["expected_changes"])
        actual = tuple(path for path, _ in prepared.target_bytes)
        if expected != actual:
            fail(
                "CREATE_EXPECTED_CHANGES_MISMATCH",
                "Recomputed CREATE transaction target set differs from plan.",
                exit_code=3,
            )
        target_path = str(plan["target"]["declared_path"])
        if not actual or actual[0] != target_path:
            fail("CREATE_TRANSACTION_ORDER_INVALID", "CREATE document must be the first transaction target.")
        for relative in actual[1:]:
            if relative not in _GENERATED_PATHS:
                fail("CREATE_TRANSACTION_PATH_BLOCKED", f"Unexpected CREATE transaction path: {relative}.")
        for relative in actual:
            try:
                (root / relative).absolute().relative_to(root)
            except ValueError:
                fail("CREATE_TRANSACTION_PATH_BLOCKED", f"CREATE path escaped repository: {relative}.")
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
        second = recompute_prepared_create(root, plan)
        if second.plan != plan or second.target_bytes != prepared.target_bytes:
            fail(
                "CREATE_PREWRITE_RECOMPUTATION_MISMATCH",
                "Immediate CREATE pre-write recomputation drifted.",
                exit_code=3,
            )

    def post_validate() -> None:
        scan = scan_repository(root)
        if scan.diagnostics or len(scan.artifacts) != plan["repository"]["expected_artifact_count_after"]:
            raise RuntimeError("Post-CREATE artifact scan failed.")
        resolved = resolve_artifact(root, str(plan["artifact_id"])).record
        metadata = plan["candidate"]["metadata"]
        expected_record = {
            "artifact_id": plan["artifact_id"],
            "kind": metadata["kind"],
            "type": metadata["type"],
            "version": metadata["version"],
            "lifecycle": metadata["lifecycle"],
            "integration": metadata["integration"],
            "authority": metadata["authority"],
            "generated": metadata["generated"],
            "depends_on": tuple(metadata["depends_on"]),
            "supersedes": tuple(metadata["supersedes"]),
            "path": target_path,
            "title": plan["candidate"]["title"],
        }
        observed_record = {
            key: getattr(resolved, key)
            for key in expected_record
        }
        if observed_record != expected_record:
            raise RuntimeError("Post-CREATE artifact identity or metadata mismatch.")
        target_data = (root / target_path).read_bytes()
        if target_data != prepared.target_bytes[0][1]:
            raise RuntimeError("Post-CREATE target bytes differ from candidate.")
        snapshot = inspect_markdown_bytes(target_data, root / target_path)
        if {
            "encoding": snapshot.encoding,
            "bom": snapshot.bom,
            "newline": snapshot.newline,
        } != {"encoding": "UTF-8", "bom": False, "newline": "LF"}:
            raise RuntimeError("Post-CREATE target byte convention mismatch.")
        if _has_trailing_whitespace(target_data):
            raise RuntimeError("Post-CREATE target contains trailing whitespace.")
        for relative, data in prepared.target_bytes:
            if (root / relative).read_bytes() != data:
                raise RuntimeError(f"Post-CREATE byte mismatch: {relative}")
        rendered = build_generated_content(scan.artifacts)
        if (root / REGISTRY_PATH).read_bytes() != rendered.registry.encode("utf-8") \
                or (root / DOCUMENT_INDEX_PATH).read_bytes() != rendered.document_index.encode("utf-8"):
            raise RuntimeError("Post-CREATE generated output mismatch.")
        state = capture_git_state(root)
        if state.worktree_entries != tuple(sorted(expected)):
            raise RuntimeError("Post-CREATE worktree scope differs from immutable plan.")
        if state.staged_paths or git_path_is_tracked(root, target_path):
            raise RuntimeError("Post-CREATE target or staging policy failed.")
        if not git_diff_check(root):
            raise RuntimeError("Post-CREATE tracked diff check failed.")

    review_paths: tuple[Path, Path] | None = None

    def finalize(result: TransactionResult) -> None:
        nonlocal review_paths
        review = _create_review_payload(
            plan,
            operation_id,
            "PASS",
            result,
            worktree_paths(),
            [],
            recomputed="PASS",
            post_validation="PASS",
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
            create_parents=False,
        )
    except WorkflowError as exc:
        blocked_review(exc, str(transaction_root))
        raise
    except TransactionPreparationError as exc:
        review = _create_review_payload(
            plan,
            operation_id,
            "FAIL",
            exc.result,
            worktree_paths(),
            [str(exc.cause)],
            recomputed="PASS",
            post_validation="NOT_RUN",
        )
        write_review_files(review_dir, review)
        diagnostic = Diagnostic("TRANSACTION_PREPARATION_FAILED", Severity.ERROR, str(exc.cause))
        raise WorkflowError((diagnostic,), 2) from exc
    except TransactionExecutionError as exc:
        post_validation = "FAIL" if "POST_VALIDATING" in exc.result.states else "NOT_RUN"
        review = _create_review_payload(
            plan,
            operation_id,
            "FAIL",
            exc.result,
            worktree_paths(),
            [str(exc.cause)],
            recomputed="PASS",
            post_validation=post_validation,
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
        "changed_paths": list(worktree_paths()),
        "review_json": str(review_paths[0]),
        "review_text": str(review_paths[1]),
    }
