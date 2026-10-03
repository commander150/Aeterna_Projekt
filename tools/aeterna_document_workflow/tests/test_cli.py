from __future__ import annotations

import json
import subprocess
import sys
import unittest

from .helpers import RepositoryFixture, markdown
from tools.aeterna_document_workflow.planner import build_update_plan


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


if __name__ == "__main__":
    unittest.main()
