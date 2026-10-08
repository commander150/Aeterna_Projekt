from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from tools.aeterna_artifacts.scanner import scan_repository
from tools.aeterna_document_workflow import path_policy
from tools.aeterna_document_workflow.create_planner import build_create_plan
from tools.aeterna_document_workflow.model import WorkflowError
from tools.aeterna_document_workflow.planner import build_update_plan
from tools.aeterna_document_workflow.review import (
    finalize_review,
    plan_semantic_digest,
    verify_review_file,
    verify_review_payload,
)
from tools.aeterna_document_workflow.transaction import FailureInjection, apply_plan

from .helpers import RepositoryFixture, markdown


class CreateApplyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def _materialize(
        self,
        *,
        target_path: str = "project/planning/NEW.md",
        data: bytes | None = None,
    ) -> tuple[bytes, dict[str, object], Path, Path, Path]:
        candidate_data = data or markdown(
            "AET-DOC-NEW",
            "New Document",
            version="0.1",
            depends_on=("AET-DOC-TARGET",),
        )
        candidate = self.fixture.candidate(candidate_data, "create.md")
        manifest = self.fixture.create_manifest(candidate, target_path=target_path)
        plan = build_create_plan(self.fixture.root, manifest)
        plan_path = candidate.parent / "create-plan.json"
        plan_path.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return candidate_data, plan, plan_path, candidate.parent / "review", self.fixture.root / target_path

    def _assert_rollback(
        self,
        review_dir: Path,
        target: Path,
        before: dict[str, bytes],
        *,
        verified: bool,
    ) -> dict[str, object]:
        self.assertFalse(os.path.lexists(target))
        self.assertEqual(before, self.fixture.tracked_bytes())
        self.assertEqual("", self.fixture.git("status", "--short"))
        review = verify_review_file(review_dir / "review.json")
        self.assertEqual("FAIL", review["final_status"])
        self.assertTrue(review["rollback"]["performed"])
        self.assertEqual(verified, review["rollback"]["verified"])
        self.assertTrue(review["rollback"]["new_target_absent"])
        self.assertEqual(0, review["post_create"]["final_artifact_count"] - review["post_create"]["baseline_artifact_count"])
        return review

    def test_success_creates_exact_untracked_target_and_create_review(self) -> None:
        candidate_data, plan, plan_path, review_dir, target = self._materialize()
        baseline_count = len(scan_repository(self.fixture.root).artifacts)

        result = apply_plan(plan_path, self.fixture.root, review_dir)

        self.assertEqual("PASS", result["status"])
        self.assertEqual(candidate_data, target.read_bytes())
        self.assertEqual(baseline_count + 1, len(scan_repository(self.fixture.root).artifacts))
        self.assertEqual(
            sorted(item["path"] for item in plan["expected_changes"]),
            sorted(result["changed_paths"]),
        )
        self.assertEqual("project/planning/NEW.md", self.fixture.git("ls-files", "--others", "--exclude-standard"))
        self.assertEqual("", self.fixture.git("diff", "--cached", "--name-only"))
        review = verify_review_file(result["review_json"])
        self.assertEqual("aeterna-document-create-review/0.1", review["schema_version"])
        self.assertEqual("create", review["operation"])
        self.assertEqual("PASS", review["final_status"])
        self.assertEqual("PASS", review["git"]["target_direct_text_check"])
        self.assertEqual({"executed_during_apply": []}, review["tests"])
        self.assertFalse(review["rollback"]["performed"])
        self.assertIn("AETERNA DOCUMENT CREATE REVIEW", Path(result["review_text"]).read_text(encoding="utf-8"))

    def test_cli_apply_and_verify_review_support_create_schema(self) -> None:
        _, _, plan_path, review_dir, target = self._materialize()
        project_root = Path(__file__).resolve().parents[3]
        applied = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.aeterna_document_workflow.cli",
                "apply",
                str(plan_path),
                "--repo",
                str(self.fixture.root),
                "--review-dir",
                str(review_dir),
            ],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(0, applied.returncode, applied.stderr)
        result = json.loads(applied.stdout)
        self.assertEqual("PASS", result["status"])
        self.assertTrue(target.is_file())
        verified = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.aeterna_document_workflow.cli",
                "verify-review",
                result["review_json"],
            ],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(0, verified.returncode, verified.stderr)
        self.assertEqual("aeterna-document-create-review/0.1", json.loads(verified.stdout)["schema_version"])

    def test_failure_after_target_write_rolls_back(self) -> None:
        before = self.fixture.tracked_bytes()
        _, _, plan_path, review_dir, target = self._materialize()
        with self.assertRaises(WorkflowError) as caught:
            apply_plan(plan_path, self.fixture.root, review_dir, injection=FailureInjection(fail_after_write=1))
        self.assertEqual(4, caught.exception.exit_code)
        review = self._assert_rollback(review_dir, target, before, verified=True)
        self.assertEqual("NOT_RUN", review["validation"]["post_write"])

    def test_failure_after_registry_write_rolls_back(self) -> None:
        before = self.fixture.tracked_bytes()
        _, plan, plan_path, review_dir, target = self._materialize()
        self.assertGreaterEqual(len(plan["expected_changes"]), 2)
        with self.assertRaises(WorkflowError) as caught:
            apply_plan(plan_path, self.fixture.root, review_dir, injection=FailureInjection(fail_after_write=2))
        self.assertEqual(4, caught.exception.exit_code)
        review = self._assert_rollback(review_dir, target, before, verified=True)
        self.assertEqual("NOT_RUN", review["validation"]["post_write"])

    def test_failure_after_index_write_rolls_back(self) -> None:
        before = self.fixture.tracked_bytes()
        _, plan, plan_path, review_dir, target = self._materialize()
        self.assertEqual(3, len(plan["expected_changes"]))
        with self.assertRaises(WorkflowError) as caught:
            apply_plan(plan_path, self.fixture.root, review_dir, injection=FailureInjection(fail_after_write=3))
        self.assertEqual(4, caught.exception.exit_code)
        review = self._assert_rollback(review_dir, target, before, verified=True)
        self.assertEqual("NOT_RUN", review["validation"]["post_write"])

    def test_post_validation_failure_rolls_back(self) -> None:
        before = self.fixture.tracked_bytes()
        _, _, plan_path, review_dir, target = self._materialize()
        with self.assertRaises(WorkflowError) as caught:
            apply_plan(plan_path, self.fixture.root, review_dir, injection=FailureInjection(fail_post_validation=True))
        self.assertEqual(4, caught.exception.exit_code)
        review = self._assert_rollback(review_dir, target, before, verified=True)
        self.assertEqual("FAIL", review["validation"]["post_write"])

    def test_rollback_verification_failure_uses_exit_five(self) -> None:
        before = self.fixture.tracked_bytes()
        _, _, plan_path, review_dir, target = self._materialize()
        injection = FailureInjection(fail_after_write=1, fail_rollback_verification=True)
        with self.assertRaises(WorkflowError) as caught:
            apply_plan(plan_path, self.fixture.root, review_dir, injection=injection)
        self.assertEqual(5, caught.exception.exit_code)
        self.assertEqual("ROLLBACK_VERIFICATION_FAILED", caught.exception.diagnostics[0].code)
        review = self._assert_rollback(review_dir, target, before, verified=False)
        self.assertEqual("NOT_RUN", review["validation"]["post_write"])

    def test_update_review_schema_and_payload_remain_unchanged(self) -> None:
        candidate = self.fixture.candidate(
            markdown("AET-DOC-TARGET", "Target", body="Updated body."),
            "update.md",
        )
        manifest = self.fixture.manifest(candidate)
        plan = build_update_plan(self.fixture.root, manifest)
        plan_path = candidate.parent / "update-plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8", newline="\n")
        result = apply_plan(plan_path, self.fixture.root, candidate.parent / "update-review")
        review = verify_review_file(result["review_json"])
        self.assertEqual("aeterna-document-update-review/0.1", review["schema_version"])
        self.assertEqual("update", review["operation"])
        self.assertEqual({"executed_during_apply": []}, review["tests"])
        self.assertNotIn("post_create", review)

    def test_head_branch_dirty_staging_and_untracked_drift_block_before_write(self) -> None:
        mutations = {
            "head": lambda: (
                (self.fixture.root / ".gitignore").write_text("TEMP/\n# changed\n", encoding="utf-8"),
                self.fixture.git("add", ".gitignore"),
                self.fixture.git("commit", "-m", "new head"),
            ),
            "branch": lambda: self.fixture.git("checkout", "-b", "other"),
            "dirty": lambda: self.fixture.target.write_bytes(self.fixture.target.read_bytes() + b"dirty\n"),
            "staging": lambda: (
                self.fixture.target.write_bytes(self.fixture.target.read_bytes() + b"staged\n"),
                self.fixture.git("add", "project/planning/TARGET.md"),
            ),
            "untracked": lambda: (self.fixture.root / "unexpected.txt").write_text("unexpected", encoding="utf-8"),
        }
        for index, (name, mutate) in enumerate(mutations.items()):
            with self.subTest(name=name):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                _, _, plan_path, review_dir, target = self._materialize()
                mutate()
                with self.assertRaises(WorkflowError):
                    apply_plan(plan_path, self.fixture.root, review_dir)
                self.assertFalse(os.path.lexists(target))
                review = verify_review_file(review_dir / "review.json")
                self.assertEqual("BLOCKED", review["final_status"])
                self.assertFalse(review["transaction"]["write_started"])

    def test_candidate_byte_and_metadata_drift_block_before_write(self) -> None:
        for index, name in enumerate(("bytes", "metadata")):
            with self.subTest(name=name):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                _, plan, plan_path, review_dir, target = self._materialize()
                candidate = Path(plan["candidate"]["resolved_path"])
                if name == "bytes":
                    candidate.write_bytes(candidate.read_bytes() + b"changed\n")
                else:
                    candidate.write_bytes(candidate.read_bytes().replace(b'version: "0.1"', b'version: "0.2"'))
                with self.assertRaises(WorkflowError):
                    apply_plan(plan_path, self.fixture.root, review_dir)
                self.assertFalse(os.path.lexists(target))
                self.assertEqual("BLOCKED", verify_review_file(review_dir / "review.json")["final_status"])

    def test_candidate_moved_outside_temp_policy_blocks_before_write(self) -> None:
        candidate_data, plan, plan_path, review_dir, target = self._materialize()
        moved = self.fixture.root / "moved.md"
        moved.write_bytes(candidate_data)
        (self.fixture.root / ".git" / "info" / "exclude").write_text("/moved.md\n", encoding="utf-8")
        plan["candidate"]["resolved_path"] = str(moved)
        plan["candidate"]["original_path"] = "moved.md"
        plan["plan_semantic_sha256"] = plan_semantic_digest(plan)
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        with self.assertRaises(WorkflowError) as caught:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("CREATE_CANDIDATE_PATH_BLOCKED", caught.exception.diagnostics[0].code)
        self.assertFalse(os.path.lexists(target))

    def test_target_appearance_and_missing_parent_block_without_directory_creation(self) -> None:
        _, _, plan_path, review_dir, target = self._materialize()
        target.mkdir()
        (self.fixture.root / ".git" / "info" / "exclude").write_text(
            "/project/planning/NEW.md/\n", encoding="utf-8"
        )
        with self.assertRaises(WorkflowError):
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertTrue(target.is_dir())

        self.fixture.close()
        self.fixture = RepositoryFixture()
        empty_parent = self.fixture.root / "project" / "newdocs"
        empty_parent.mkdir()
        _, _, plan_path, review_dir, target = self._materialize(target_path="project/newdocs/NEW.md")
        empty_parent.rmdir()
        with self.assertRaises(WorkflowError) as caught:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("CREATE_TARGET_PARENT_MISSING", caught.exception.diagnostics[0].code)
        self.assertFalse(empty_parent.exists())
        self.assertFalse(os.path.lexists(target))

    def test_apply_time_case_and_unicode_collisions_block_before_write(self) -> None:
        cases = (
            ("case", "project/planning/CASE.md", "project/planning/case.md"),
            ("unicode", "project/planning/CAFÉ.md", "project/planning/CAFE\u0301.md"),
        )
        for index, (name, target_path, collision_path) in enumerate(cases):
            with self.subTest(name=name):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                _, _, plan_path, review_dir, target = self._materialize(target_path=target_path)
                collision = self.fixture.root / collision_path
                collision.mkdir()
                exclude = "/" + collision_path + "/\n"
                (self.fixture.root / ".git" / "info" / "exclude").write_text(exclude, encoding="utf-8")
                with self.assertRaises(WorkflowError) as caught:
                    apply_plan(plan_path, self.fixture.root, review_dir)
                self.assertIn(
                    caught.exception.diagnostics[0].code,
                    {"CREATE_TARGET_NOT_ABSENT", "CREATE_TARGET_COLLISION"},
                )
                self.assertFalse(target.is_file())

    def test_parent_reparse_policy_is_rechecked_at_apply_time(self) -> None:
        _, _, plan_path, review_dir, target = self._materialize()
        real_check = path_policy._has_reparse_component

        def parent_blocked(root: Path, path: Path) -> bool:
            if path == target.parent:
                return True
            return real_check(root, path)

        with patch.object(path_policy, "_has_reparse_component", side_effect=parent_blocked):
            with self.assertRaises(WorkflowError) as caught:
                apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("CREATE_TARGET_PARENT_BLOCKED", caught.exception.diagnostics[0].code)
        self.assertFalse(os.path.lexists(target))

    def test_artifact_set_dependency_and_generated_preview_drift_block(self) -> None:
        mutations = {
            "artifact-set": lambda: self.fixture.target.write_bytes(
                self.fixture.target.read_bytes().replace(b'version: "1.0"', b'version: "1.1"')
            ),
            "dependency": lambda: self.fixture.target.write_bytes(
                self.fixture.target.read_bytes().replace(b"depends_on: []", b"depends_on:\n  - AET-DOC-TRANSITIVE")
            ),
            "generated": lambda: (self.fixture.root / "project/generated/DOCUMENT_INDEX.md").write_bytes(b"drift\n"),
        }
        assume_path = {
            "artifact-set": "project/planning/TARGET.md",
            "dependency": "project/planning/TARGET.md",
            "generated": "project/generated/DOCUMENT_INDEX.md",
        }
        for index, (name, mutate) in enumerate(mutations.items()):
            with self.subTest(name=name):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                _, _, plan_path, review_dir, target = self._materialize()
                self.fixture.git("update-index", "--assume-unchanged", assume_path[name])
                mutate()
                self.assertEqual("", self.fixture.git("status", "--short"))
                with self.assertRaises(WorkflowError):
                    apply_plan(plan_path, self.fixture.root, review_dir)
                self.assertFalse(os.path.lexists(target))
                self.assertEqual("BLOCKED", verify_review_file(review_dir / "review.json")["final_status"])

    def test_plan_digest_and_expected_changes_tampering_are_rejected(self) -> None:
        _, plan, plan_path, review_dir, target = self._materialize()
        plan["artifact_id"] = "AET-DOC-TAMPERED"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        with self.assertRaises(WorkflowError) as digest_error:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("CREATE_PLAN_INTEGRITY_MISMATCH", digest_error.exception.diagnostics[0].code)
        self.assertFalse(review_dir.exists())
        self.assertFalse(os.path.lexists(target))

    def test_unknown_apply_plan_schema_is_rejected_before_mutation(self) -> None:
        _, plan, plan_path, review_dir, target = self._materialize()
        plan["schema_version"] = "aeterna-document-unknown-plan/0.1"
        plan["plan_semantic_sha256"] = plan_semantic_digest(plan)
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        with self.assertRaises(WorkflowError) as caught:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("PLAN_SCHEMA_INVALID", caught.exception.diagnostics[0].code)
        self.assertFalse(review_dir.exists())
        self.assertFalse(os.path.lexists(target))

        self.fixture.close()
        self.fixture = RepositoryFixture()
        _, plan, plan_path, review_dir, target = self._materialize()
        plan["expected_changes"] = list(reversed(plan["expected_changes"]))
        plan["plan_semantic_sha256"] = plan_semantic_digest(plan)
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        with self.assertRaises(WorkflowError) as changes_error:
            apply_plan(plan_path, self.fixture.root, review_dir)
        self.assertEqual("CREATE_PLAN_STRUCTURE_INVALID", changes_error.exception.diagnostics[0].code)
        self.assertFalse(review_dir.exists())
        self.assertFalse(os.path.lexists(target))

    def test_create_review_verifier_rejects_tampering_and_inconsistent_status(self) -> None:
        _, _, plan_path, review_dir, _ = self._materialize()
        result = apply_plan(plan_path, self.fixture.root, review_dir)
        review = verify_review_file(result["review_json"])

        tampered = copy.deepcopy(review)
        tampered["operation"] = "update"
        tampered = finalize_review(tampered)
        with self.assertRaises(WorkflowError) as operation_error:
            verify_review_payload(tampered)
        self.assertEqual("REVIEW_OPERATION_INVALID", operation_error.exception.diagnostics[0].code)

        inconsistent = copy.deepcopy(review)
        inconsistent["rollback"]["performed"] = True
        inconsistent = finalize_review(inconsistent)
        with self.assertRaises(WorkflowError) as status_error:
            verify_review_payload(inconsistent)
        self.assertEqual("REVIEW_STATUS_INCONSISTENT", status_error.exception.diagnostics[0].code)

        unknown = copy.deepcopy(review)
        unknown["schema_version"] = "unknown-review/0.1"
        unknown = finalize_review(unknown)
        with self.assertRaises(WorkflowError) as schema_error:
            verify_review_payload(unknown)
        self.assertEqual("REVIEW_SCHEMA_INVALID", schema_error.exception.diagnostics[0].code)

        malformed_hash = copy.deepcopy(review)
        generated = malformed_hash["hashes"]["generated"]
        next(iter(generated.values()))["final_sha256"] = "bad"
        malformed_hash = finalize_review(malformed_hash)
        with self.assertRaises(WorkflowError) as hash_error:
            verify_review_payload(malformed_hash)
        self.assertEqual("REVIEW_HASH_INVALID", hash_error.exception.diagnostics[0].code)

    def test_candidate_trailing_whitespace_is_blocked_before_write(self) -> None:
        data = markdown("AET-DOC-NEW", "New Document", version="0.1").replace(
            b"Baseline body.", b"Baseline body. "
        )
        candidate = self.fixture.candidate(data, "create.md")
        manifest = self.fixture.create_manifest(candidate)
        with self.assertRaises(WorkflowError) as caught:
            build_create_plan(self.fixture.root, manifest)
        self.assertEqual("CREATE_CANDIDATE_TRAILING_WHITESPACE", caught.exception.diagnostics[0].code)
        self.assertFalse((self.fixture.root / "project/planning/NEW.md").exists())


if __name__ == "__main__":
    unittest.main()
