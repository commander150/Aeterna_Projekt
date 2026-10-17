from __future__ import annotations

import json
import subprocess
import sys
import unittest

from .helpers import RepositoryFixture, markdown
from tools.aeterna_document_workflow.planner import build_update_plan
from tools.aeterna_document_workflow.content import inspect_markdown


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def _run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "tools.aeterna_document_workflow.cli", *arguments],
            cwd=self.fixture.root.parent.parent.parent.parent,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_resolve_and_impact_end_to_end(self) -> None:
        resolve = self._run(
            "resolve", "AET-DOC-TARGET", "--repo", str(self.fixture.root), "--json"
        )
        self.assertEqual(0, resolve.returncode, resolve.stderr)
        self.assertEqual("project/planning/TARGET.md", json.loads(resolve.stdout)["path"])
        impact = self._run(
            "impact", "AET-DOC-TARGET", "--repo", str(self.fixture.root),
            "--transitive", "--json",
        )
        self.assertEqual(0, impact.returncode, impact.stderr)
        self.assertEqual(3, len(json.loads(impact.stdout)["transitive_reverse_dependents"]))

    def test_inspect_update_baseline_exposes_production_fingerprint_read_only(self) -> None:
        before = self.fixture.tracked_bytes()
        result = self._run(
            "inspect-update-baseline", "AET-DOC-TARGET", "--repo", str(self.fixture.root)
        )
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        snapshot = inspect_markdown(self.fixture.target)
        self.assertEqual("aeterna-document-update-baseline/0.1", payload["schema_version"])
        self.assertEqual("AET-DOC-TARGET", payload["artifact_id"])
        self.assertEqual("project/planning/TARGET.md", payload["path"])
        self.assertEqual(self.fixture.head, payload["head"])
        self.assertEqual(snapshot.sha256, payload["sha256"])
        self.assertEqual(snapshot.metadata_fingerprint, payload["metadata_fingerprint"])
        self.assertEqual(dict(snapshot.metadata.fields), payload["metadata"])
        self.assertTrue(payload["worktree_clean"])
        self.assertTrue(payload["staging_empty"])
        self.assertEqual(before, self.fixture.tracked_bytes())

    def test_plan_update_end_to_end_and_unknown_command_rejected(self) -> None:
        candidate = self.fixture.candidate(markdown("AET-DOC-TARGET", "Target", body="Changed."))
        manifest = self.fixture.manifest(candidate)
        before = self.fixture.tracked_bytes()
        result = self._run(
            "plan-update", "--repo", str(self.fixture.root), "--manifest", str(manifest)
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("aeterna-document-update-plan/0.1", json.loads(result.stdout)["schema_version"])
        self.assertEqual(before, self.fixture.tracked_bytes())
        rejected = self._run("apply")
        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("required", rejected.stderr)

    def test_structured_cli_failure_exit_code(self) -> None:
        result = self._run(
            "resolve", "AET-DOC-UNKNOWN", "--repo", str(self.fixture.root), "--json"
        )
        self.assertEqual(1, result.returncode)
        payload = json.loads(result.stderr)
        self.assertEqual("ARTIFACT_UNKNOWN", payload["diagnostics"][0]["code"])

    def test_apply_and_verify_review_end_to_end(self) -> None:
        candidate = self.fixture.candidate(markdown("AET-DOC-TARGET", "Target", body="CLI apply."))
        manifest = self.fixture.manifest(candidate)
        plan = build_update_plan(self.fixture.root, manifest)
        plan_path = candidate.parent / "plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        review_dir = candidate.parent / "cli-review"
        applied = self._run(
            "apply", str(plan_path), "--repo", str(self.fixture.root),
            "--review-dir", str(review_dir),
        )
        self.assertEqual(0, applied.returncode, applied.stderr)
        payload = json.loads(applied.stdout)
        self.assertEqual("PASS", payload["status"])
        verified = self._run("verify-review", payload["review_json"])
        self.assertEqual(0, verified.returncode, verified.stderr)
        self.assertEqual("PASS", json.loads(verified.stdout)["status"])

    def test_governance_cli_requires_interactive_confirmation(self) -> None:
        candidate = self.fixture.candidate(
            markdown("AET-DOC-TARGET", "Target", body="Governance meaning changed.")
        )
        manifest = self.fixture.manifest(candidate, change_class="semantic-governance-change")
        plan = build_update_plan(self.fixture.root, manifest)
        plan_path = candidate.parent / "governance-plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        before = self.fixture.tracked_bytes()
        result = self._run(
            "apply-governance", str(plan_path), "--repo", str(self.fixture.root),
            "--review-dir", str(candidate.parent / "governance-review"),
        )
        self.assertEqual(1, result.returncode)
        self.assertEqual(
            "SEMANTIC_GOVERNANCE_APPLY_BLOCKED",
            json.loads(result.stderr)["diagnostics"][0]["code"],
        )
        self.assertEqual(before, self.fixture.tracked_bytes())


if __name__ == "__main__":
    unittest.main()
