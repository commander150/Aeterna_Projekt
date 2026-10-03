from __future__ import annotations

import unittest

from tools.aeterna_document_workflow.git_state import capture_git_state

from .helpers import RepositoryFixture


class GitStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_branch_head_and_clean_state(self) -> None:
        state = capture_git_state(self.fixture.root)
        self.assertEqual("main", state.branch)
        self.assertEqual(self.fixture.head, state.head)
        self.assertTrue(state.clean)

    def test_dirty_tracked_and_untracked_are_classified(self) -> None:
        self.fixture.target.write_bytes(self.fixture.target.read_bytes() + b"dirty\n")
        state = capture_git_state(self.fixture.root)
        self.assertFalse(state.clean)
        self.assertTrue(state.worktree_entries)
        self.fixture.git("checkout", "--", "project/planning/TARGET.md")
        self.fixture._write("outside.txt", b"untracked\n")
        self.assertFalse(capture_git_state(self.fixture.root).clean)

    def test_staging_is_classified(self) -> None:
        self.fixture.target.write_bytes(self.fixture.target.read_bytes() + b"staged\n")
        self.fixture.git("add", "project/planning/TARGET.md")
        state = capture_git_state(self.fixture.root)
        self.assertEqual(("project/planning/TARGET.md",), state.staged_paths)
        self.assertFalse(state.clean)


if __name__ == "__main__":
    unittest.main()
