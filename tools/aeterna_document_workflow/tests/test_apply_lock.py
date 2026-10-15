"""Cross-process exclusion for the shared governed CREATE/UPDATE Apply entrypoint."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

from tools.aeterna_document_workflow import transaction
from tools.aeterna_document_workflow.create_planner import build_create_plan
from tools.aeterna_document_workflow.create_transaction import apply_create_plan
from tools.aeterna_document_workflow.model import WorkflowError
from tools.aeterna_document_workflow.planner import build_update_plan
from tools.aeterna_document_workflow.transaction import FailureInjection, apply_plan

from .helpers import RepositoryFixture, markdown


_PAUSED_APPLY = """
from pathlib import Path
import sys
from tools.aeterna_document_workflow import transaction

real_execute = transaction.execute_transaction
def paused_execute(*args, **kwargs):
    Path(sys.argv[4]).write_text('READY', encoding='ascii')
    if sys.stdin.readline() != 'go\\n':
        raise RuntimeError('Test release signal was lost.')
    return real_execute(*args, **kwargs)

transaction.execute_transaction = paused_execute
transaction.apply_plan(sys.argv[1], sys.argv[2], sys.argv[3])
print('APPLY_PASS', flush=True)
"""


_PAUSED_AFTER_WRITE = """
from pathlib import Path
import sys
from tools.aeterna_document_workflow import transaction

real_replace = transaction.os.replace
paused = False
def pause_after_first_write(source, destination):
    global paused
    real_replace(source, destination)
    if not paused and Path(source).parent.name == 'prepared':
        paused = True
        Path(sys.argv[4]).write_text('WRITTEN', encoding='ascii')
        sys.stdin.readline()

transaction.os.replace = pause_after_first_write
transaction.apply_plan(sys.argv[1], sys.argv[2], sys.argv[3])
"""


class CrossProcessApplyLockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()
        self.children: list[subprocess.Popen[str]] = []

    def tearDown(self) -> None:
        for child in self.children:
            if child.poll() is None:
                child.kill()
                child.communicate(timeout=10)
        self.fixture.close()

    def _update(self, fixture: RepositoryFixture | None = None) -> tuple[Path, Path]:
        fixture = fixture or self.fixture
        candidate = fixture.candidate(markdown("AET-DOC-TARGET", "Target", body="Lock test body."))
        plan = build_update_plan(fixture.root, fixture.manifest(candidate))
        plan_path = candidate.parent / "update-plan.json"
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        return plan_path, candidate.parent / "update-review"

    def _create(self) -> tuple[Path, Path]:
        candidate = self.fixture.candidate(markdown("AET-DOC-NEW", "New", version="0.1"), "new.md")
        plan = build_create_plan(self.fixture.root, self.fixture.create_manifest(candidate))
        plan_path = candidate.parent / "create-plan.json"
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        return plan_path, candidate.parent / "create-review"

    def _paused_apply(self, plan_path: Path, review_dir: Path, script: str = _PAUSED_APPLY) -> subprocess.Popen[str]:
        ready = plan_path.parent / "apply-ready.signal"
        child = subprocess.Popen(
            [sys.executable, "-c", script, str(plan_path), str(self.fixture.root), str(review_dir), str(ready)],
            cwd=Path(__file__).resolve().parents[3],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.children.append(child)
        deadline = time.monotonic() + 30
        while not ready.exists() and time.monotonic() < deadline:
            if child.poll() is not None:
                out, err = child.communicate()
                self.fail(f"First Apply exited before synchronization: {out} {err}")
            time.sleep(0.02)
        self.assertTrue(ready.exists(), "First Apply did not reach the synchronized write boundary.")
        return child

    def _release(self, child: subprocess.Popen[str]) -> None:
        out, err = child.communicate("go\n", timeout=90)
        self.assertEqual(0, child.returncode, f"First Apply failed: {out} {err}")
        self.assertIn("APPLY_PASS", out)

    def _blocked_process(self, plan_path: Path, review_dir: Path) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "tools.aeterna_document_workflow.cli", "apply", str(plan_path),
             "--repo", str(self.fixture.root), "--review-dir", str(review_dir)],
            cwd=Path(__file__).resolve().parents[3], capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(3, result.returncode, result.stderr)
        self.assertEqual("ERROR", json.loads(result.stderr)["status"])
        self.assertEqual("APPLY_ALREADY_IN_PROGRESS", json.loads(result.stderr)["diagnostics"][0]["code"])
        self.assertFalse((review_dir / "review.json").exists())

    def test_two_processes_block_second_update_without_writing_then_release(self) -> None:
        plan_path, review_dir = self._update()
        baseline = self.fixture.target.read_bytes()
        first = self._paused_apply(plan_path, review_dir)
        self._blocked_process(plan_path, plan_path.parent / "blocked-review")
        self.assertEqual(baseline, self.fixture.target.read_bytes())
        self.assertEqual("", self.fixture.git("status", "--short"))
        self._release(first)
        self.assertIn(b"Lock test body.", self.fixture.target.read_bytes())
        self.assertEqual("", self.fixture.git("diff", "--cached", "--name-only"))

    def test_update_lock_blocks_create_but_not_another_repository(self) -> None:
        update_path, update_review = self._update()
        create_path, create_review = self._create()
        first = self._paused_apply(update_path, update_review)
        self._blocked_process(create_path, create_review)
        self.assertFalse((self.fixture.root / "project/planning/NEW.md").exists())
        other = RepositoryFixture()
        try:
            other_plan, other_review = self._update(other)
            self.assertEqual("PASS", apply_plan(other_plan, other.root, other_review)["status"])
        finally:
            other.close()
        self._release(first)

    def test_preflight_error_and_verified_rollback_release_lock(self) -> None:
        plan_path, review_dir = self._update()
        candidate = plan_path.parent / "candidate.md"
        original = candidate.read_bytes()
        candidate.write_bytes(b"changed after planning")
        with self.assertRaises(WorkflowError):
            apply_plan(plan_path, self.fixture.root, review_dir)
        lock_path = transaction.durable_apply_state_root(self.fixture.root) / "apply.lock"
        self.assertEqual("RELEASED", json.loads(lock_path.read_bytes()[1:])["status"])
        candidate.write_bytes(original)
        with self.assertRaises(WorkflowError) as failure:
            apply_plan(plan_path, self.fixture.root, plan_path.parent / "rollback-review",
                       injection=FailureInjection(fail_after_write=1))
        self.assertEqual("TRANSACTION_FAILED_ROLLED_BACK", failure.exception.diagnostics[0].code)
        self.assertEqual("RELEASED", json.loads(lock_path.read_bytes()[1:])["status"])
        self.assertEqual("", self.fixture.git("status", "--short"))
        self.assertEqual("PASS", apply_plan(plan_path, self.fixture.root, plan_path.parent / "retry-review")["status"])

    def test_process_interruption_requires_manual_recovery(self) -> None:
        plan_path, review_dir = self._update()
        first = self._paused_apply(plan_path, review_dir)
        first.kill()
        first.communicate(timeout=10)
        lock_path = transaction.durable_apply_state_root(self.fixture.root) / "apply.lock"
        self.assertEqual("ACTIVE", json.loads(lock_path.read_bytes()[1:])["status"])
        self.assertEqual("", self.fixture.git("status", "--short"))
        with self.assertRaises(WorkflowError) as failure:
            apply_plan(plan_path, self.fixture.root, plan_path.parent / "after-crash-review")
        self.assertEqual("APPLY_RECOVERY_REQUIRED", failure.exception.diagnostics[0].code)

    def test_interruption_after_first_write_preserves_durable_backup_and_blocks(self) -> None:
        plan_path, review_dir = self._update()
        original = self.fixture.target.read_bytes()
        first = self._paused_apply(plan_path, review_dir, _PAUSED_AFTER_WRITE)
        first.kill()
        first.communicate(timeout=10)
        self.assertNotEqual(original, self.fixture.target.read_bytes())
        state_root = transaction.durable_apply_state_root(self.fixture.root)
        self.assertEqual("ACTIVE", json.loads((state_root / "apply.lock").read_bytes()[1:])["status"])
        operation_dirs = tuple((state_root / "transactions").iterdir())
        self.assertEqual(1, len(operation_dirs))
        self.assertEqual(original, (operation_dirs[0] / "backups" / "0.bin").read_bytes())
        self.assertEqual("WRITING", json.loads((operation_dirs[0] / "journal.json").read_text(
            encoding="utf-8"))["states"][-1])
        with self.assertRaises(WorkflowError) as blocked:
            apply_plan(plan_path, self.fixture.root, plan_path.parent / "after-write-crash-review")
        self.assertEqual("APPLY_RECOVERY_REQUIRED", blocked.exception.diagnostics[0].code)

    def test_failed_rollback_retains_recovery_barrier(self) -> None:
        plan_path, review_dir = self._update()
        with self.assertRaises(WorkflowError) as failure:
            apply_plan(
                plan_path, self.fixture.root, review_dir,
                injection=FailureInjection(fail_after_write=1, fail_rollback_verification=True),
            )
        self.assertEqual("ROLLBACK_VERIFICATION_FAILED", failure.exception.diagnostics[0].code)
        review = json.loads((review_dir / "review.json").read_text(encoding="utf-8"))
        transaction_root = Path(review["transaction"]["root"])
        self.assertTrue((transaction_root / "journal.json").is_file())
        self.assertTrue((transaction_root / "backups" / "0.bin").is_file())
        self.assertTrue(transaction_root.is_relative_to(transaction.durable_apply_state_root(self.fixture.root)))
        with self.assertRaises(WorkflowError) as blocked:
            apply_plan(plan_path, self.fixture.root, plan_path.parent / "after-rollback-review")
        self.assertEqual("APPLY_RECOVERY_REQUIRED", blocked.exception.diagnostics[0].code)

    def test_direct_create_uses_shared_lock_and_low_level_write_requires_it(self) -> None:
        with self.assertRaises(WorkflowError) as failure:
            transaction.execute_transaction(
                self.fixture.root, self.fixture.root / "TEMP" / "unlocked", "unlocked", (),
                lambda: None, lambda: None, lambda _result: None,
            )
        self.assertEqual("APPLY_LOCK_REQUIRED", failure.exception.diagnostics[0].code)
        create_path, review_dir = self._create()
        plan = json.loads(create_path.read_text(encoding="utf-8"))
        self.assertEqual("PASS", apply_create_plan(plan, self.fixture.root, review_dir)["status"])
        self.assertEqual("RELEASED", json.loads(
            (transaction.durable_apply_state_root(self.fixture.root) / "apply.lock").read_bytes()[1:]
        )["status"])
        review = json.loads((review_dir / "review.json").read_text(encoding="utf-8"))
        self.assertTrue(Path(review["transaction"]["root"]).is_relative_to(
            transaction.durable_apply_state_root(self.fixture.root)
        ))

    def test_completed_update_recovery_evidence_survives_disposable_temp(self) -> None:
        plan_path, review_dir = self._update()
        self.assertEqual("PASS", apply_plan(plan_path, self.fixture.root, review_dir)["status"])
        review = json.loads((review_dir / "review.json").read_text(encoding="utf-8"))
        transaction_root = Path(review["transaction"]["root"])
        self.assertTrue(transaction_root.is_relative_to(transaction.durable_apply_state_root(self.fixture.root)))
        disposable_runtime = self.fixture.root / "TEMP/aeterna_document_workflow"
        if disposable_runtime.exists():
            shutil.rmtree(disposable_runtime)
        self.assertTrue((transaction_root / "journal.json").is_file())
        self.assertTrue((transaction_root / "backups" / "0.bin").is_file())
        self.assertEqual("RELEASED", json.loads((transaction.durable_apply_state_root(
            self.fixture.root) / "apply.lock").read_bytes()[1:])["status"])

    def test_legacy_temp_marker_is_preserved_and_active_marker_blocks(self) -> None:
        plan_path, review_dir = self._update()
        legacy = self.fixture.root / "TEMP/aeterna_document_workflow/apply.lock"
        legacy.parent.mkdir(parents=True)
        record = {"schema": "aeterna-apply-lock/0.1", "status": "ACTIVE"}
        active_bytes = b"\0" + json.dumps(record).encode("utf-8")
        legacy.write_bytes(active_bytes)
        with self.assertRaises(WorkflowError) as blocked:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("APPLY_RECOVERY_REQUIRED", blocked.exception.diagnostics[0].code)
        self.assertEqual(active_bytes, legacy.read_bytes())
        self.assertEqual("", self.fixture.git("status", "--short"))
        record["status"] = "RELEASED"
        released_bytes = b"\0" + json.dumps(record).encode("utf-8")
        legacy.write_bytes(released_bytes)
        self.assertEqual("PASS", apply_plan(plan_path, self.fixture.root, review_dir)["status"])
        self.assertEqual(released_bytes, legacy.read_bytes())

    def test_missing_durable_marker_with_transaction_evidence_blocks(self) -> None:
        plan_path, review_dir = self._update()
        orphan = transaction.durable_transaction_parent(self.fixture.root) / "orphan"
        orphan.mkdir(parents=True)
        (orphan / "journal.json").write_text('{"states":["WRITING"]}', encoding="utf-8")
        with self.assertRaises(WorkflowError) as blocked:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("APPLY_RECOVERY_REQUIRED", blocked.exception.diagnostics[0].code)
        self.assertEqual("", self.fixture.git("status", "--short"))
        with self.assertRaises(WorkflowError) as still_blocked:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("APPLY_RECOVERY_REQUIRED", still_blocked.exception.diagnostics[0].code)

    def test_missing_legacy_transaction_journal_blocks_without_marker(self) -> None:
        plan_path, review_dir = self._update()
        orphan = self.fixture.root / "TEMP/aeterna_document_workflow/transactions/orphan"
        orphan.mkdir(parents=True)
        with self.assertRaises(WorkflowError) as blocked:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("APPLY_RECOVERY_REQUIRED", blocked.exception.diagnostics[0].code)
        self.assertTrue(orphan.is_dir())

    def test_lock_infrastructure_failure_is_distinct_from_contention(self) -> None:
        plan_path, review_dir = self._update()
        with patch.object(transaction, "_lock_byte", side_effect=OSError(5, "injected I/O failure")):
            with self.assertRaises(WorkflowError) as failure:
                apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("APPLY_LOCK_INFRASTRUCTURE_ERROR", failure.exception.diagnostics[0].code)
        self.assertEqual("", self.fixture.git("status", "--short"))
