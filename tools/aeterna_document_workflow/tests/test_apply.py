from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tools.aeterna_artifacts.scanner import scan_repository
from tools.aeterna_document_workflow import transaction
from tools.aeterna_document_workflow.content import inspect_markdown
from tools.aeterna_document_workflow.git_state import capture_git_state
from tools.aeterna_document_workflow.model import PreparedUpdate, WorkflowError, fail
from tools.aeterna_document_workflow.planner import build_update_plan
from tools.aeterna_document_workflow.review import (
    finalize_review,
    plan_semantic_digest,
    review_semantic_digest,
    verify_review_file,
)
from tools.aeterna_document_workflow.transaction import FailureInjection, apply_plan

from .helpers import RepositoryFixture, markdown


class ApplyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def _materialize(self, data: bytes, **options: object) -> tuple[dict[str, object], Path, Path]:
        candidate = self.fixture.candidate(data)
        manifest = self.fixture.manifest(candidate, **options)
        plan = build_update_plan(self.fixture.root, manifest)
        plan_path = candidate.parent / "plan.json"
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        return plan, plan_path, candidate.parent / "review"

    def _assert_blocked_review(self, review_dir: Path) -> dict[str, object]:
        review = verify_review_file(review_dir / "review.json")
        self.assertEqual("BLOCKED", review["final_status"])
        self.assertFalse(review["transaction"]["write_started"])
        self.assertEqual(0, review["transaction"]["writes_completed"])
        return review

    def test_body_only_apply_changes_one_path_and_review_verifies(self) -> None:
        baseline = inspect_markdown(self.fixture.target)
        registry = (self.fixture.root / "project/generated/artifacts_registry.json").read_bytes()
        index = (self.fixture.root / "project/generated/DOCUMENT_INDEX.md").read_bytes()
        _, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", body="Applied body.")
        )

        result = apply_plan(plan_path, self.fixture.root, review_dir)

        self.assertEqual(["project/planning/TARGET.md"], result["changed_paths"])
        self.assertEqual(baseline.front_matter_bytes, inspect_markdown(self.fixture.target).front_matter_bytes)
        self.assertEqual(registry, (self.fixture.root / "project/generated/artifacts_registry.json").read_bytes())
        self.assertEqual(index, (self.fixture.root / "project/generated/DOCUMENT_INDEX.md").read_bytes())
        review = verify_review_file(result["review_json"])
        self.assertEqual("PASS", review["final_status"])
        self.assertEqual("", self.fixture.git("diff", "--cached", "--name-only"))

    def test_metadata_apply_changes_document_and_both_generated_views(self) -> None:
        _, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", version="1.1"),
            change_class="metadata-only",
            version_intent="minor",
            proposed_version="1.1",
            metadata_delta=[{"field": "version", "old": "1.0", "new": "1.1"}],
        )

        result = apply_plan(plan_path, self.fixture.root, review_dir)

        self.assertEqual(
            [
                "project/generated/DOCUMENT_INDEX.md",
                "project/generated/artifacts_registry.json",
                "project/planning/TARGET.md",
            ],
            result["changed_paths"],
        )
        self.assertEqual((), scan_repository(self.fixture.root).diagnostics)
        review = verify_review_file(result["review_json"])
        self.assertEqual("PASS", review["final_status"])
        self.assertEqual(result["changed_paths"], review["scope"]["actual_git_changed_paths"])
        self.assertEqual(result["changed_paths"], review["scope"]["expected_git_changed_paths"])
        self.assertEqual([], review["scope"]["git_normalized_unchanged_generated_paths"])

    def test_generated_byte_writes_can_be_git_unchanged_after_normalization(self) -> None:
        generated_paths = (
            "project/generated/artifacts_registry.json",
            "project/generated/DOCUMENT_INDEX.md",
        )
        for index, mode in enumerate(("true", "input", "attributes")):
            with self.subTest(mode=mode):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                if mode == "attributes":
                    self.fixture.git("config", "core.autocrlf", "false")
                    (self.fixture.root / ".gitattributes").write_text(
                        "project/generated/* text\n", encoding="utf-8", newline="\n"
                    )
                    self.fixture.git("add", ".gitattributes")
                    self.fixture.git("commit", "-m", "normalize generated files")
                else:
                    self.fixture.git("config", "core.autocrlf", mode)
                for relative in generated_paths:
                    path = self.fixture.root / relative
                    original = path.read_bytes()
                    self.assertNotIn(b"\r\n", original)
                    path.write_bytes(original.replace(b"\n", b"\r\n"))
                self.assertTrue(capture_git_state(self.fixture.root).clean)

                candidate_data = markdown("AET-DOC-TARGET", "Target", body="Changed body.")
                plan, plan_path, review_dir = self._materialize(candidate_data)
                planned = [item["path"] for item in plan["expected_changes"]]
                self.assertEqual(3, len(planned))
                result = apply_plan(plan_path, self.fixture.root, review_dir)

                canonical = "project/planning/TARGET.md"
                self.assertEqual([canonical], result["changed_paths"])
                self.assertEqual(
                    [canonical],
                    [line.split()[-1] for line in self.fixture.git("status", "--short").splitlines()],
                )
                self.assertEqual(candidate_data, self.fixture.target.read_bytes())
                review = verify_review_file(result["review_json"])
                self.assertEqual("PASS", review["final_status"])
                self.assertEqual(3, review["transaction"]["writes_completed"])
                self.assertEqual(planned, review["scope"]["planned_write_paths"])
                self.assertEqual([canonical], review["scope"]["expected_git_changed_paths"])
                self.assertEqual([canonical], review["scope"]["actual_git_changed_paths"])
                self.assertEqual(
                    sorted(generated_paths),
                    review["scope"]["git_normalized_unchanged_generated_paths"],
                )
                self.assertEqual("", self.fixture.git("diff", "--cached", "--name-only"))

    def test_unexpected_git_change_after_write_is_blocked(self) -> None:
        for index, mode in enumerate(("tracked", "untracked")):
            with self.subTest(mode=mode):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                before = self.fixture.tracked_bytes()
                _, plan_path, review_dir = self._materialize(
                    markdown("AET-DOC-TARGET", "Target", body="Changed body.")
                )
                unrelated = self.fixture.root / (
                    "project/governance/DEPENDENT.md" if mode == "tracked" else "UNEXPECTED.txt"
                )
                original_execute = transaction.execute_transaction

                def inject_unexpected_change(*args: object, **kwargs: object) -> object:
                    call = list(args)
                    post_validate = call[5]

                    def changed_post_validate() -> None:
                        if mode == "tracked":
                            unrelated.write_bytes(unrelated.read_bytes() + b"Unexpected body.\n")
                        else:
                            unrelated.write_bytes(b"Unexpected untracked file.\n")
                        post_validate()

                    call[5] = changed_post_validate
                    return original_execute(*call, **kwargs)

                with patch.object(transaction, "execute_transaction", side_effect=inject_unexpected_change):
                    with self.assertRaises(WorkflowError) as caught:
                        apply_plan(plan_path, self.fixture.root, review_dir)
                self.assertEqual("ROLLBACK_VERIFICATION_FAILED", caught.exception.diagnostics[0].code)
                review = verify_review_file(review_dir / "review.json")
                self.assertEqual("FAIL", review["final_status"])
                self.assertIn("Post-write Git scope validation failed", review["deviations"][0])
                self.assertFalse(review["rollback"]["verified"])
                self.assertEqual(before["project/planning/TARGET.md"], self.fixture.target.read_bytes())
                self.assertTrue(unrelated.exists())

    def test_corrupt_generated_bytes_after_write_trigger_verified_rollback(self) -> None:
        before = self.fixture.tracked_bytes()
        _, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", version="1.1"),
            change_class="metadata-only",
            version_intent="minor",
            proposed_version="1.1",
            metadata_delta=[{"field": "version", "old": "1.0", "new": "1.1"}],
        )
        generated = self.fixture.root / "project/generated/artifacts_registry.json"
        original_execute = transaction.execute_transaction

        def inject_corruption(*args: object, **kwargs: object) -> object:
            call = list(args)
            post_validate = call[5]

            def corrupt_post_validate() -> None:
                generated.write_bytes(generated.read_bytes() + b"corrupt")
                post_validate()

            call[5] = corrupt_post_validate
            return original_execute(*call, **kwargs)

        with patch.object(transaction, "execute_transaction", side_effect=inject_corruption):
            with self.assertRaises(WorkflowError) as caught:
                apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual(4, caught.exception.exit_code)
        self.assertEqual(before, self.fixture.tracked_bytes())
        self.assertEqual("", self.fixture.git("status", "--short"))
        review = verify_review_file(review_dir / "review.json")
        self.assertEqual("FAIL", review["final_status"])
        self.assertTrue(review["rollback"]["verified"])
        self.assertIn("Post-write byte mismatch", review["deviations"][0])

    def test_success_retains_raw_backups_and_committed_journal(self) -> None:
        before = self.fixture.tracked_bytes()
        plan, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", version="1.1"),
            change_class="metadata-only",
            version_intent="minor",
            proposed_version="1.1",
            metadata_delta=[{"field": "version", "old": "1.0", "new": "1.1"}],
        )

        result = apply_plan(plan_path, self.fixture.root, review_dir)

        review = verify_review_file(result["review_json"])
        transaction_root = Path(review["transaction"]["root"])
        self.assertEqual("COMMITTED_TO_WORKTREE", review["transaction"]["state"])
        self.assertEqual("PASS", review["final_status"])
        self.assertTrue((transaction_root / "backups").is_dir())
        self.assertTrue((transaction_root / "prepared").is_dir())
        journal = json.loads((transaction_root / "journal.json").read_text(encoding="utf-8"))
        self.assertEqual("COMMITTED_TO_WORKTREE", journal["states"][-1])
        for index, item in enumerate(plan["expected_changes"]):
            self.assertEqual(before[item["path"]], (transaction_root / "backups" / f"{index}.bin").read_bytes())
        status = self.fixture.git("status", "--short", "--untracked-files=all").splitlines()
        self.assertEqual(
            sorted(item["path"] for item in plan["expected_changes"]),
            sorted(line.split(maxsplit=1)[1] for line in status),
        )
        self.assertFalse(any("TEMP/" in line for line in status))

    def test_reference_only_apply_uses_exact_declared_line(self) -> None:
        _, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", body="See NEW.md."),
            change_class="reference-only",
            reference_changes=[{
                "old_line_number": 4,
                "new_line_number": 4,
                "old_line": "Baseline body.",
                "new_line": "See NEW.md.",
            }],
        )
        result = apply_plan(plan_path, self.fixture.root, review_dir)
        review = verify_review_file(result["review_json"])
        self.assertTrue(review["change"]["reference_change_declaration_complete"])
        self.assertEqual(["project/planning/TARGET.md"], result["changed_paths"])

    def test_failure_injections_restore_original_bytes(self) -> None:
        injections = (
            FailureInjection(fail_after_write=1),
            FailureInjection(fail_after_write=2),
            FailureInjection(fail_post_validation=True),
        )
        for index, injection in enumerate(injections):
            with self.subTest(injection=injection):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                before = self.fixture.tracked_bytes()
                _, plan_path, review_dir = self._materialize(
                    markdown("AET-DOC-TARGET", "Target", version="1.1"),
                    change_class="metadata-only",
                    version_intent="minor",
                    proposed_version="1.1",
                    metadata_delta=[{"field": "version", "old": "1.0", "new": "1.1"}],
                )
                with self.assertRaises(WorkflowError) as caught:
                    apply_plan(plan_path, self.fixture.root, review_dir, injection=injection)
                self.assertEqual(4, caught.exception.exit_code)
                self.assertEqual(before, self.fixture.tracked_bytes())
                self.assertEqual("", self.fixture.git("status", "--short"))
                review = verify_review_file(review_dir / "review.json")
                self.assertTrue(review["rollback"]["performed"])
                self.assertTrue(review["rollback"]["verified"])

    def test_rollback_touches_only_successfully_written_targets(self) -> None:
        for completed_writes in (1, 2):
            with self.subTest(completed_writes=completed_writes):
                if completed_writes == 2:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                plan, plan_path, review_dir = self._materialize(
                    markdown("AET-DOC-TARGET", "Target", version="1.1"),
                    change_class="metadata-only",
                    version_intent="minor",
                    proposed_version="1.1",
                    metadata_delta=[{"field": "version", "old": "1.0", "new": "1.1"}],
                )
                expected = [item["path"] for item in plan["expected_changes"]]
                rollback_destinations: list[str] = []
                real_replace = transaction.os.replace

                def observe_replace(source: object, destination: object) -> None:
                    source_path = Path(source)
                    destination_path = Path(destination)
                    if source_path.parent.name == "restore":
                        rollback_destinations.append(
                            destination_path.resolve().relative_to(self.fixture.root).as_posix()
                        )
                    real_replace(source, destination)

                with patch.object(transaction.os, "replace", side_effect=observe_replace):
                    with self.assertRaises(WorkflowError):
                        apply_plan(
                            plan_path,
                            self.fixture.root,
                            review_dir,
                            injection=FailureInjection(fail_after_write=completed_writes),
                        )

                self.assertEqual(list(reversed(expected[:completed_writes])), rollback_destinations)
                self.assertTrue(set(expected[completed_writes:]).isdisjoint(rollback_destinations))
                review = verify_review_file(review_dir / "review.json")
                self.assertEqual(completed_writes, review["transaction"]["writes_completed"])

    def test_rollback_verification_failure_uses_exit_five(self) -> None:
        _, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", body="Changed.")
        )
        with self.assertRaises(WorkflowError) as caught:
            apply_plan(
                plan_path,
                self.fixture.root,
                review_dir,
                injection=FailureInjection(fail_after_write=1, fail_rollback_verification=True),
            )
        self.assertEqual(5, caught.exception.exit_code)
        review = verify_review_file(review_dir / "review.json")
        self.assertFalse(review["rollback"]["verified"])

    def test_semantic_governance_apply_is_blocked_without_writes(self) -> None:
        before = self.fixture.tracked_bytes()
        _, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", body="Governance meaning changed."),
            change_class="semantic-governance-change",
        )
        with self.assertRaises(WorkflowError) as caught:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual(1, caught.exception.exit_code)
        self.assertEqual(before, self.fixture.tracked_bytes())
        self._assert_blocked_review(review_dir)

    def test_plan_integrity_and_recomputation_block_stale_inputs(self) -> None:
        plan, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", body="Changed.")
        )
        tampered = dict(plan)
        tampered["artifact_id"] = "AET-DOC-OTHER"
        plan_path.write_text(json.dumps(tampered), encoding="utf-8")
        with self.assertRaises(WorkflowError) as integrity:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("PLAN_INTEGRITY_MISMATCH", integrity.exception.diagnostics[0].code)

        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        Path(plan["candidate"]["resolved_path"]).write_bytes(b"changed after plan")
        with self.assertRaises(WorkflowError) as stale:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual(3, stale.exception.exit_code)

    def test_apply_stale_head_dirty_worktree_and_staging_block_before_write(self) -> None:
        scenarios = ("head", "dirty", "staged")
        for index, scenario in enumerate(scenarios):
            with self.subTest(scenario=scenario):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                before = self.fixture.tracked_bytes()
                _, plan_path, review_dir = self._materialize(
                    markdown("AET-DOC-TARGET", "Target", body="Changed.")
                )
                if scenario == "head":
                    self.fixture.git("commit", "--allow-empty", "-m", "advance head")
                elif scenario == "dirty":
                    self.fixture.target.write_bytes(self.fixture.target.read_bytes() + b"dirty\n")
                    before = self.fixture.tracked_bytes()
                else:
                    self.fixture.target.write_bytes(self.fixture.target.read_bytes() + b"staged\n")
                    self.fixture.git("add", "project/planning/TARGET.md")
                    before = self.fixture.tracked_bytes()
                with self.assertRaises(WorkflowError) as caught:
                    apply_plan(plan_path, self.fixture.root, review_dir)
                self.assertEqual(3, caught.exception.exit_code)
                self.assertEqual(before, self.fixture.tracked_bytes())
                self._assert_blocked_review(review_dir)

    def test_review_semantic_digest_excludes_instance_identity(self) -> None:
        _, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", body="Changed.")
        )
        result = apply_plan(plan_path, self.fixture.root, review_dir)
        review = json.loads(Path(result["review_json"]).read_text(encoding="utf-8"))
        equivalent = dict(review)
        equivalent["operation_id"] = "different-instance"
        equivalent["transaction"] = dict(review["transaction"])
        equivalent["transaction"]["root"] = "different/instance/root"
        equivalent = finalize_review(equivalent)
        self.assertEqual(review["review_semantic_sha256"], equivalent["review_semantic_sha256"])
        self.assertEqual(equivalent["review_semantic_sha256"], review_semantic_digest(equivalent))

    def test_candidate_review_and_recomputed_target_policies_fail_closed(self) -> None:
        before = self.fixture.tracked_bytes()
        plan, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", body="Changed.")
        )
        tracked_candidate = dict(plan)
        tracked_candidate["candidate"] = dict(plan["candidate"])
        tracked_candidate["candidate"]["resolved_path"] = str(
            self.fixture.root / "project/governance/DEPENDENT.md"
        )
        tracked_candidate["plan_semantic_sha256"] = plan_semantic_digest(tracked_candidate)
        plan_path.write_text(json.dumps(tracked_candidate), encoding="utf-8")
        with self.assertRaises(WorkflowError) as candidate_error:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("CANDIDATE_LOCATION_BLOCKED", candidate_error.exception.diagnostics[0].code)
        self.assertEqual(before, self.fixture.tracked_bytes())
        self._assert_blocked_review(review_dir)

        tampered_targets = dict(plan)
        tampered_targets["expected_changes"] = list(plan["expected_changes"]) + [
            {"operation": "DOCUMENT_UPDATE", "path": "project/governance/DEPENDENT.md"}
        ]
        tampered_targets["plan_semantic_sha256"] = plan_semantic_digest(tampered_targets)
        plan_path.write_text(json.dumps(tampered_targets), encoding="utf-8")
        with self.assertRaises(WorkflowError) as recomputed:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("PLAN_RECOMPUTATION_MISMATCH", recomputed.exception.diagnostics[0].code)
        self._assert_blocked_review(review_dir)

        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        with self.assertRaises(WorkflowError) as review_error:
            apply_plan(plan_path, self.fixture.root, self.fixture.root / "project/reviews")
        self.assertEqual("REVIEW_DIRECTORY_BLOCKED", review_error.exception.diagnostics[0].code)

    def test_expected_changes_and_transaction_path_rejections_write_blocked_reviews(self) -> None:
        plan, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", body="Changed.")
        )
        prepared = transaction.recompute_prepared_update(self.fixture.root, plan)
        mismatch = PreparedUpdate(plan, ())
        with patch.object(transaction, "recompute_prepared_update", return_value=mismatch):
            with self.assertRaises(WorkflowError) as expected_error:
                apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("EXPECTED_CHANGES_MISMATCH", expected_error.exception.diagnostics[0].code)
        self._assert_blocked_review(review_dir)

        blocked_path = "Archive/blocked.md"
        path_plan = dict(plan)
        path_plan["expected_changes"] = [{"operation": "DOCUMENT_UPDATE", "path": blocked_path}]
        path_plan["plan_semantic_sha256"] = plan_semantic_digest(path_plan)
        plan_path.write_text(json.dumps(path_plan), encoding="utf-8")
        path_prepared = PreparedUpdate(path_plan, ((blocked_path, prepared.target_bytes[0][1]),))
        with patch.object(transaction, "recompute_prepared_update", return_value=path_prepared):
            with self.assertRaises(WorkflowError) as path_error:
                apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("TRANSACTION_PATH_BLOCKED", path_error.exception.diagnostics[0].code)
        self._assert_blocked_review(review_dir)

    def test_transaction_root_volume_and_prewrite_rejections_write_blocked_reviews(self) -> None:
        plan, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", body="Changed.")
        )
        def reject_transaction_root(root: Path) -> Path:
            fail("TRANSACTION_ROOT_BLOCKED", "Injected transaction root rejection.")

        with patch.object(transaction, "durable_transaction_parent", side_effect=reject_transaction_root):
            with self.assertRaises(WorkflowError) as root_error:
                apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("TRANSACTION_ROOT_BLOCKED", root_error.exception.diagnostics[0].code)
        self._assert_blocked_review(review_dir)

        with patch.object(transaction, "_same_volume", return_value=False):
            with self.assertRaises(WorkflowError) as volume_error:
                apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("TRANSACTION_VOLUME_MISMATCH", volume_error.exception.diagnostics[0].code)
        self._assert_blocked_review(review_dir)

        prepared = transaction.recompute_prepared_update(self.fixture.root, plan)
        drifted = PreparedUpdate(plan, ((prepared.target_bytes[0][0], b"drift"),))
        with patch.object(
            transaction,
            "recompute_prepared_update",
            side_effect=(prepared, drifted),
        ):
            with self.assertRaises(WorkflowError) as prewrite_error:
                apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("PREWRITE_RECOMPUTATION_MISMATCH", prewrite_error.exception.diagnostics[0].code)
        self._assert_blocked_review(review_dir)

    def test_preparation_failure_is_exit_two_without_governed_writes_or_rollback(self) -> None:
        before = self.fixture.tracked_bytes()
        _, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", body="Changed.")
        )
        real_replace = transaction.os.replace
        governed_replaces: list[tuple[object, object]] = []

        def observe_replace(source: object, destination: object) -> None:
            governed_replaces.append((source, destination))
            real_replace(source, destination)

        with patch.object(transaction, "_journal", side_effect=OSError("injected journal failure")):
            with patch.object(transaction.os, "replace", side_effect=observe_replace):
                with self.assertRaises(WorkflowError) as caught:
                    apply_plan(plan_path, self.fixture.root, review_dir)

        self.assertEqual(2, caught.exception.exit_code)
        self.assertEqual("TRANSACTION_PREPARATION_FAILED", caught.exception.diagnostics[0].code)
        self.assertEqual([], governed_replaces)
        self.assertEqual(before, self.fixture.tracked_bytes())
        review = verify_review_file(review_dir / "review.json")
        self.assertEqual("FAIL", review["final_status"])
        self.assertFalse(review["transaction"]["write_started"])
        self.assertEqual(0, review["transaction"]["writes_completed"])
        self.assertFalse(review["rollback"]["performed"])

    def test_plan_json_key_order_does_not_change_integrity(self) -> None:
        plan, plan_path, review_dir = self._materialize(
            markdown("AET-DOC-TARGET", "Target", body="Changed.")
        )
        reordered = {key: plan[key] for key in reversed(tuple(plan))}
        plan_path.write_text(json.dumps(reordered, separators=(",", ":")), encoding="utf-8")
        result = apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("PASS", result["status"])


if __name__ == "__main__":
    unittest.main()
