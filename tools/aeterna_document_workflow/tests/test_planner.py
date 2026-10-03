from __future__ import annotations

import json
import unittest

from tools.aeterna_document_workflow.model import WorkflowError
from tools.aeterna_document_workflow.planner import build_update_plan

from .helpers import RepositoryFixture, markdown


class PlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def _plan(self, data: bytes, **manifest_options: object) -> dict[str, object]:
        candidate = self.fixture.candidate(data)
        manifest = self.fixture.manifest(candidate, **manifest_options)
        return build_update_plan(self.fixture.root, manifest)

    def _error(self, data: bytes, **manifest_options: object) -> WorkflowError:
        candidate = self.fixture.candidate(data)
        manifest = self.fixture.manifest(candidate, **manifest_options)
        with self.assertRaises(WorkflowError) as caught:
            build_update_plan(self.fixture.root, manifest)
        return caught.exception

    def test_body_only_plan_is_deterministic_and_generated_unchanged(self) -> None:
        data = markdown("AET-DOC-TARGET", "Target", body="Changed body.")
        candidate = self.fixture.candidate(data)
        manifest = self.fixture.manifest(candidate)
        before = self.fixture.tracked_bytes()
        first = build_update_plan(self.fixture.root, manifest)
        second = build_update_plan(self.fixture.root, manifest)
        self.assertEqual(first, second)
        self.assertEqual("aeterna-document-update-plan/0.1", first["schema_version"])
        self.assertTrue(first["change"]["body_changed"])
        self.assertEqual(
            {"UNCHANGED"},
            {item["status"] for item in first["generated"]["outputs"]},
        )
        self.assertEqual(before, self.fixture.tracked_bytes())
        self.assertEqual("", self.fixture.git("status", "--short"))

    def test_metadata_only_explicit_delta_reports_generated_change(self) -> None:
        data = markdown("AET-DOC-TARGET", "Target", version="1.1")
        plan = self._plan(
            data,
            change_class="metadata-only",
            metadata_delta=[{"field": "version", "old": "1.0", "new": "1.1"}],
        )
        self.assertFalse(plan["change"]["body_changed"])
        self.assertEqual(
            {"WOULD_CHANGE"},
            {item["status"] for item in plan["generated"]["outputs"]},
        )

    def test_metadata_and_body_class(self) -> None:
        data = markdown("AET-DOC-TARGET", "Target", version="1.1", body="Changed.")
        plan = self._plan(
            data,
            change_class="metadata+body",
            metadata_delta=[{"field": "version", "old": "1.0", "new": "1.1"}],
        )
        self.assertEqual("metadata+body", plan["change"]["class"])

    def test_reference_only_enumerates_body_changes(self) -> None:
        data = markdown("AET-DOC-TARGET", "Target", body="See [new](new.md).")
        plan = self._plan(data, change_class="reference-only", version_intent="git-only")
        self.assertTrue(plan["change"]["body_diff"])
        self.assertEqual("git-only", plan["version"]["recommended_intent"])

    def test_semantic_governance_change_is_high_risk(self) -> None:
        data = markdown("AET-DOC-TARGET", "Target", body="New governing rule.")
        plan = self._plan(
            data,
            change_class="semantic-governance-change",
            version_intent="major",
        )
        self.assertEqual("HIGH", plan["change"]["risk"])
        self.assertEqual("major", plan["version"]["recommended_intent"])

    def test_protected_artifact_id_and_authority_changes_are_rejected(self) -> None:
        cases = (
            (markdown("AET-DOC-OTHER", "Target"), "artifact_id", "AET-DOC-TARGET", "AET-DOC-OTHER"),
            (markdown("AET-DOC-TARGET", "Target", authority="other-authority"), "authority", "project-direction", "other-authority"),
        )
        for data, field, old, new in cases:
            with self.subTest(field=field):
                error = self._error(
                    data,
                    change_class="metadata-only",
                    metadata_delta=[{"field": field, "old": old, "new": new}],
                )
                self.assertEqual("PROTECTED_FIELD_CHANGE", error.diagnostics[0].code)

    def test_declared_path_change_is_rejected(self) -> None:
        error = self._error(
            markdown("AET-DOC-TARGET", "Target"),
            change_class="metadata-only",
            metadata_delta=[{
                "field": "path",
                "old": "project/planning/TARGET.md",
                "new": "project/planning/MOVED.md",
            }],
        )
        self.assertEqual("PROTECTED_FIELD_CHANGE", error.diagnostics[0].code)

    def test_dependency_missing_and_cycle_are_rejected(self) -> None:
        cases = (
            (("AET-DOC-MISSING",), "DOC_DEPENDENCY_MISSING"),
            (("AET-DOC-TRANSITIVE",), "DOC_DEPENDENCY_CYCLE"),
        )
        for dependencies, code in cases:
            with self.subTest(code=code):
                error = self._error(
                    markdown("AET-DOC-TARGET", "Target", depends_on=dependencies),
                    change_class="metadata-only",
                    metadata_delta=[{
                        "field": "depends_on",
                        "old": [],
                        "new": list(dependencies),
                    }],
                )
                self.assertIn(code, {item.code for item in error.diagnostics})

    def test_candidate_and_baseline_concurrency_guards(self) -> None:
        data = markdown("AET-DOC-TARGET", "Target", body="Changed.")
        cases = (
            ({"candidate_sha256": "0" * 64}, "CANDIDATE_HASH_MISMATCH"),
            ({"baseline_sha256": "0" * 64}, "BASELINE_HASH_MISMATCH"),
            ({"metadata_fingerprint": "0" * 64}, "METADATA_FINGERPRINT_MISMATCH"),
            ({"expected_head": "0" * 40}, "EXPECTED_HEAD_MISMATCH"),
        )
        for overrides, code in cases:
            with self.subTest(code=code):
                error = self._error(data, **overrides)
                self.assertEqual(code, error.diagnostics[0].code)
                self.assertEqual(3, error.exit_code)

    def test_dirty_and_staged_repositories_block_planning(self) -> None:
        candidate = self.fixture.candidate(markdown("AET-DOC-TARGET", "Target", body="Changed."))
        manifest = self.fixture.manifest(candidate)
        self.fixture.target.write_bytes(self.fixture.target.read_bytes() + b"dirty\n")
        with self.assertRaises(WorkflowError) as dirty:
            build_update_plan(self.fixture.root, manifest)
        self.assertEqual("WORKTREE_DIRTY", dirty.exception.diagnostics[0].code)
        self.fixture.git("checkout", "--", "project/planning/TARGET.md")
        self.fixture.target.write_bytes(self.fixture.target.read_bytes() + b"staged\n")
        self.fixture.git("add", "project/planning/TARGET.md")
        with self.assertRaises(WorkflowError) as staged:
            build_update_plan(self.fixture.root, manifest)
        self.assertEqual("STAGING_NOT_EMPTY", staged.exception.diagnostics[0].code)
        self.assertEqual(3, staged.exception.exit_code)

    def test_newline_drift_is_rejected(self) -> None:
        error = self._error(
            markdown("AET-DOC-TARGET", "Target", body="Changed.", newline="\r\n")
        )
        self.assertEqual("CANDIDATE_NEWLINE_DRIFT", error.diagnostics[0].code)

    def test_metadata_delta_must_be_exact(self) -> None:
        error = self._error(
            markdown("AET-DOC-TARGET", "Target", version="1.1"),
            change_class="metadata-only",
        )
        self.assertEqual("METADATA_DELTA_MISMATCH", error.diagnostics[0].code)


if __name__ == "__main__":
    unittest.main()
