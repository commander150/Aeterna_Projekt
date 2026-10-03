from __future__ import annotations

import unittest

from tools.aeterna_document_workflow.impact import build_impact
from tools.aeterna_document_workflow.model import WorkflowError
from tools.aeterna_document_workflow.resolver import resolve_artifact

from .helpers import RepositoryFixture, markdown


class ResolverImpactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_unique_resolve_and_unknown_failure(self) -> None:
        resolved = resolve_artifact(self.fixture.root, "AET-DOC-TARGET")
        self.assertEqual("project/planning/TARGET.md", resolved.record.path)
        with self.assertRaises(WorkflowError) as caught:
            resolve_artifact(self.fixture.root, "AET-DOC-UNKNOWN")
        self.assertEqual("ARTIFACT_UNKNOWN", caught.exception.diagnostics[0].code)

    def test_duplicate_blocks_resolution(self) -> None:
        self.fixture._write("project/other/DUPLICATE.md", markdown("AET-DOC-TARGET", "Duplicate"))
        with self.assertRaises(WorkflowError) as caught:
            resolve_artifact(self.fixture.root, "AET-DOC-TARGET")
        self.assertIn("DOC_DUPLICATE_ARTIFACT_ID", {item.code for item in caught.exception.diagnostics})

    def test_any_scan_error_blocks_resolution(self) -> None:
        self.fixture._write(
            "project/other/BROKEN.md",
            markdown("AET-DOC-BROKEN", "Broken", depends_on=("AET-DOC-MISSING",)),
        )
        with self.assertRaises(WorkflowError) as caught:
            resolve_artifact(self.fixture.root, "AET-DOC-TARGET")
        self.assertIn("DOC_DEPENDENCY_MISSING", {item.code for item in caught.exception.diagnostics})

    def test_impact_labels_reverse_and_transitive_dependencies(self) -> None:
        resolved = resolve_artifact(self.fixture.root, "AET-DOC-TARGET")
        report = build_impact(resolved.scan.artifacts, "AET-DOC-TARGET", include_transitive=True)
        direct = {item["artifact_id"]: item["impact"] for item in report["direct_reverse_dependencies"]}
        self.assertEqual("REVIEW_RECOMMENDED", direct["AET-DOC-DEPENDENT"])
        self.assertEqual("STALE", direct["AET-GEN-DERIVED"])
        self.assertEqual(
            ["AET-DOC-DEPENDENT", "AET-DOC-TRANSITIVE", "AET-GEN-DERIVED"],
            [item["artifact_id"] for item in report["transitive_reverse_dependents"]],
        )


if __name__ == "__main__":
    unittest.main()
