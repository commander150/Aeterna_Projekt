from __future__ import annotations

import unittest

from tools.aeterna_document_workflow.model import WorkflowError
from tools.aeterna_document_workflow.planner import build_update_plan

from .helpers import RepositoryFixture, markdown


class HardeningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def _error(self, data: bytes, **options: object) -> str:
        candidate = self.fixture.candidate(data)
        manifest = self.fixture.manifest(candidate, **options)
        with self.assertRaises(WorkflowError) as caught:
            build_update_plan(self.fixture.root, manifest)
        return caught.exception.diagnostics[0].code

    def test_version_intent_negative_matrix(self) -> None:
        cases = (
            ({"version_intent": "git-only", "metadata_delta": [{"field": "version", "old": "1.0", "new": "1.1"}]}, "VERSION_INTENT_CONFLICT"),
            ({"version_intent": "minor", "metadata_delta": [{"field": "version", "old": "1.0", "new": "1.1"}]}, "VERSION_DELTA_REQUIRED"),
            ({"version_intent": "minor", "proposed_version": "1.2", "metadata_delta": [{"field": "version", "old": "1.0", "new": "1.1"}]}, "PROPOSED_VERSION_MISMATCH"),
            ({"version_intent": "minor", "proposed_version": "1.1", "metadata_delta": []}, "VERSION_DELTA_REQUIRED"),
            ({"version_intent": "major", "proposed_version": "2.0", "metadata_delta": [{"field": "version", "old": "1.0", "new": "1.1"}]}, "PROPOSED_VERSION_MISMATCH"),
            ({"version_intent": "major", "metadata_delta": [{"field": "version", "old": "1.0", "new": "1.1"}]}, "VERSION_DELTA_REQUIRED"),
            ({"version_intent": "minor", "proposed_version": "1.1", "metadata_delta": [{"field": "version", "old": "1.0", "new": "1.2"}]}, "PROPOSED_VERSION_MISMATCH"),
        )
        for options, code in cases:
            with self.subTest(code=code, options=options):
                self.assertEqual(
                    code,
                    self._error(
                        markdown("AET-DOC-TARGET", "Target", version="1.1"),
                        change_class="metadata-only",
                        **options,
                    ),
                )

    def test_major_version_consistency_success(self) -> None:
        candidate = self.fixture.candidate(markdown("AET-DOC-TARGET", "Target", version="2.0"))
        manifest = self.fixture.manifest(
            candidate,
            change_class="metadata-only",
            version_intent="major",
            proposed_version="2.0",
            metadata_delta=[{"field": "version", "old": "1.0", "new": "2.0"}],
        )
        plan = build_update_plan(self.fixture.root, manifest)
        self.assertEqual("major", plan["version"]["declared_intent"])

    def test_reference_only_exact_declaration_and_rejections(self) -> None:
        candidate = self.fixture.candidate(markdown("AET-DOC-TARGET", "Target", body="See NEW.md."))
        valid = [{
            "old_line_number": 4,
            "new_line_number": 4,
            "old_line": "Baseline body.",
            "new_line": "See NEW.md.",
        }]
        manifest = self.fixture.manifest(candidate, change_class="reference-only", reference_changes=valid)
        plan = build_update_plan(self.fixture.root, manifest)
        self.assertTrue(plan["change"]["reference_change_declaration_complete"])

        bad_declarations = (
            [],
            [{**valid[0], "old_line": "wrong"}],
            [{**valid[0], "new_line": "wrong"}],
        )
        for declarations in bad_declarations:
            with self.subTest(declarations=declarations):
                self.assertEqual(
                    "REFERENCE_CHANGE_DECLARATION_INCOMPLETE",
                    self._error(
                        markdown("AET-DOC-TARGET", "Target", body="See NEW.md."),
                        change_class="reference-only",
                        reference_changes=declarations,
                    ),
                )

    def test_reference_only_insert_delete_is_ambiguous(self) -> None:
        self.assertEqual(
            "REFERENCE_CHANGE_AMBIGUOUS",
            self._error(
                markdown("AET-DOC-TARGET", "Target", body="First.\nSecond."),
                change_class="reference-only",
                reference_changes=[],
            ),
        )


if __name__ == "__main__":
    unittest.main()
