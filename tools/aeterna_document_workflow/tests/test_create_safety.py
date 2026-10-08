from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tools.aeterna_artifacts.model import ArtifactRecord, ScanResult, Scope
from tools.aeterna_artifacts.scanner import scan_repository
from tools.aeterna_document_workflow.create_planner import build_create_plan
from tools.aeterna_document_workflow.model import WorkflowError
from tools.aeterna_document_workflow.path_policy import (
    FilesystemEntry,
    detect_path_collisions,
    validate_target_syntax,
)

from .helpers import RepositoryFixture, markdown


class CreateSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def _manifest(self, **overrides: object) -> Path:
        candidate = self.fixture.candidate(markdown("AET-DOC-NEW", "New", version="0.1"), "create.md")
        return self.fixture.create_manifest(candidate, **overrides)

    def _error(self, manifest: Path) -> str:
        with self.assertRaises(WorkflowError) as caught:
            build_create_plan(self.fixture.root, manifest)
        return caught.exception.diagnostics[0].code

    def test_allowed_target_roots(self) -> None:
        accepted = (
            "project/planning/NEW.md",
            "data/specifications/NEW.md",
            "design/concepts/NEW.md",
            "src/engine/docs/NEW.md",
        )
        for path in accepted:
            with self.subTest(path=path):
                self.assertTrue(validate_target_syntax(path))

    def test_target_path_syntax_and_scope_rejection_matrix(self) -> None:
        rejected = (
            "",
            "/project/NEW.md",
            "C:/project/NEW.md",
            "project\\NEW.md",
            "project//NEW.md",
            "project/./NEW.md",
            "project/../NEW.md",
            "project/NEW\0.md",
            "project/NEW:stream.md",
            "project/CON.md",
            "project/folder./NEW.md",
            "project/folder /NEW.md",
            "project/NEW.txt",
            "Archive/NEW.md",
            "learning/NEW.md",
            "TEMP/NEW.md",
            "project/generated/NEW.md",
            "tools/NEW.md",
            "src/other/NEW.md",
            ".git/NEW.md",
            ".venv/NEW.md",
            "rules/NEW.md",
        )
        for path in rejected:
            with self.subTest(path=path):
                with self.assertRaises(WorkflowError):
                    validate_target_syntax(path)

    def test_collision_policy_detects_exact_case_unicode_and_file_directory(self) -> None:
        self.assertEqual(
            ("EXACT",),
            detect_path_collisions("design/NEW.md", (FilesystemEntry("design/NEW.md", False),)),
        )
        self.assertEqual(
            ("CASE_INSENSITIVE",),
            detect_path_collisions("design/NEW.md", (FilesystemEntry("design/new.md", False),)),
        )
        unicode_collision = detect_path_collisions(
            "design/Café.md",
            (FilesystemEntry("design/Cafe\u0301.md", False),),
        )
        self.assertIn("UNICODE_NORMALIZATION", unicode_collision)
        self.assertIn(
            "FILE_DIRECTORY",
            detect_path_collisions(
                "design/folder/NEW.md",
                (FilesystemEntry("design/folder", False),),
            ),
        )
        self.assertIn(
            "FILE_DIRECTORY",
            detect_path_collisions(
                "design/NEW.md",
                (FilesystemEntry("design/NEW.md/child", False),),
            ),
        )

    def test_missing_file_and_reparse_parent_are_blocked(self) -> None:
        manifest = self._manifest(target_path="project/missing/NEW.md")
        self.assertEqual("CREATE_TARGET_PARENT_MISSING", self._error(manifest))

        self.fixture.close()
        self.fixture = RepositoryFixture()
        parent = self.fixture.root / "project/PARENT"
        parent.write_text("file", encoding="utf-8")
        self.fixture.git("add", "project/PARENT")
        self.fixture.git("commit", "-m", "file parent")
        manifest = self._manifest(target_path="project/PARENT/NEW.md")
        self.assertEqual("CREATE_TARGET_PARENT_BLOCKED", self._error(manifest))

        self.fixture.close()
        self.fixture = RepositoryFixture()
        manifest = self._manifest()
        with patch("tools.aeterna_document_workflow.path_policy._has_reparse_component", return_value=True):
            self.assertEqual("CREATE_TARGET_PARENT_BLOCKED", self._error(manifest))

    def test_existing_target_forms_are_blocked_without_overwrite(self) -> None:
        existing = self.fixture.root / "project/planning/NEW.md"
        existing.write_text("existing", encoding="utf-8")
        self.fixture.git("add", "project/planning/NEW.md")
        self.fixture.git("commit", "-m", "existing target")
        manifest = self._manifest()
        self.assertEqual("CREATE_TARGET_NOT_ABSENT", self._error(manifest))

        self.fixture.close()
        self.fixture = RepositoryFixture()
        ignore = self.fixture.root / ".gitignore"
        ignore.write_text("TEMP/\nproject/planning/IGNORED.md\n", encoding="utf-8", newline="\n")
        self.fixture.git("add", ".gitignore")
        self.fixture.git("commit", "-m", "ignore target")
        (self.fixture.root / "project/planning/IGNORED.md").write_text("ignored", encoding="utf-8")
        manifest = self._manifest(target_path="project/planning/IGNORED.md")
        self.assertEqual("CREATE_TARGET_NOT_ABSENT", self._error(manifest))

    def test_candidate_location_policy_blocks_escape_nonignored_and_reparse(self) -> None:
        manifest = self._manifest(candidate_path="../../project/planning/TARGET.md")
        self.assertEqual("CREATE_CANDIDATE_PATH_BLOCKED", self._error(manifest))

        self.fixture.close()
        self.fixture = RepositoryFixture()
        manifest = self._manifest()
        real_reparse = __import__(
            "tools.aeterna_document_workflow.path_policy",
            fromlist=["_has_reparse_component"],
        )._has_reparse_component

        def candidate_only(root: Path, path: Path) -> bool:
            return path.name == "create.md" or real_reparse(root, path)

        with patch("tools.aeterna_document_workflow.path_policy._has_reparse_component", side_effect=candidate_only):
            self.assertEqual("CREATE_CANDIDATE_PATH_BLOCKED", self._error(manifest))

        self.fixture.close()
        self.fixture = RepositoryFixture()
        manifest = self._manifest()
        with patch("tools.aeterna_document_workflow.path_policy.git_path_is_ignored", return_value=False):
            self.assertEqual("CREATE_CANDIDATE_PATH_BLOCKED", self._error(manifest))

    def test_baseline_git_guards_remain_strict(self) -> None:
        scenarios = ("branch", "head", "dirty", "untracked", "staged")
        for index, scenario in enumerate(scenarios):
            with self.subTest(scenario=scenario):
                if index:
                    self.fixture.close()
                    self.fixture = RepositoryFixture()
                manifest = self._manifest()
                payload = json.loads(manifest.read_text(encoding="utf-8"))
                if scenario == "branch":
                    payload["expected_branch"] = "other"
                    manifest.write_text(json.dumps(payload), encoding="utf-8")
                elif scenario == "head":
                    payload["expected_head"] = "0" * 40
                    manifest.write_text(json.dumps(payload), encoding="utf-8")
                elif scenario == "dirty":
                    self.fixture.target.write_bytes(self.fixture.target.read_bytes() + b"dirty\n")
                elif scenario == "untracked":
                    (self.fixture.root / "UNTRACKED.txt").write_text("x", encoding="utf-8")
                else:
                    self.fixture.target.write_bytes(self.fixture.target.read_bytes() + b"staged\n")
                    self.fixture.git("add", "project/planning/TARGET.md")
                self.assertIn(
                    self._error(manifest),
                    {"EXPECTED_BRANCH_MISMATCH", "EXPECTED_HEAD_MISMATCH", "WORKTREE_DIRTY", "STAGING_NOT_EMPTY"},
                )

    def test_baseline_scan_diagnostics_and_dependency_cycle_block(self) -> None:
        invalid = markdown("AET-DOC-BROKEN", "Broken").replace(b"lifecycle: active", b"lifecycle: invalid")
        path = self.fixture.root / "project/planning/BROKEN.md"
        path.write_bytes(invalid)
        self.fixture.git("add", "project/planning/BROKEN.md")
        self.fixture.git("commit", "-m", "invalid metadata")
        manifest = self._manifest()
        self.assertEqual("LIFECYCLE_INVALID", self._error(manifest))

        self.fixture.close()
        self.fixture = RepositoryFixture()
        self.fixture.target.write_bytes(
            markdown("AET-DOC-TARGET", "Target", depends_on=("AET-DOC-DEPENDENT",))
        )
        dependent = self.fixture.root / "project/governance/DEPENDENT.md"
        dependent.write_bytes(
            markdown("AET-DOC-DEPENDENT", "Dependent", depends_on=("AET-DOC-TARGET",))
        )
        self.fixture.git("add", "project/planning/TARGET.md", "project/governance/DEPENDENT.md")
        self.fixture.git("commit", "-m", "dependency cycle")
        manifest = self._manifest()
        self.assertEqual("DOC_DEPENDENCY_CYCLE", self._error(manifest))

    def test_case_equivalent_artifact_id_collision_is_explicitly_blocked(self) -> None:
        manifest = self._manifest()
        scan = scan_repository(self.fixture.root)
        fake = ArtifactRecord(
            artifact_id="aet-doc-new",
            kind="document",
            type="reference",
            version="1.0",
            lifecycle="active",
            integration="current",
            authority="reference",
            generated=False,
            depends_on=(),
            supersedes=(),
            path="project/planning/fake.md",
            scope=Scope.ACTIVE,
            title="Fake",
        )
        synthetic = ScanResult((*scan.artifacts, fake), ())
        with patch("tools.aeterna_document_workflow.create_preflight.scan_repository", return_value=synthetic):
            self.assertEqual("CREATE_ARTIFACT_ID_COLLISION", self._error(manifest))


if __name__ == "__main__":
    unittest.main()
