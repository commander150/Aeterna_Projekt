from __future__ import annotations

import unittest

from tools.aeterna_artifacts.model import Scope
from tools.aeterna_artifacts.scopes import classify_scope


class ScopeClassifierTests(unittest.TestCase):
    def test_active_scope(self) -> None:
        self.assertIs(
            Scope.ACTIVE,
            classify_scope("Aeterna dokumentációk/example.md"),
        )

    def test_learning_scope(self) -> None:
        self.assertIs(Scope.LEARNING, classify_scope("learning/example.md"))

    def test_archive_scope(self) -> None:
        self.assertIs(Scope.ARCHIVE, classify_scope("Archive/foo.md"))

    def test_case_insensitive_learning_scope(self) -> None:
        self.assertIs(Scope.LEARNING, classify_scope("LEARNING/example.md"))

    def test_case_insensitive_archive_scope(self) -> None:
        self.assertIs(Scope.ARCHIVE, classify_scope("archive/foo.md"))

    def test_windows_separator(self) -> None:
        self.assertIs(Scope.ARCHIVE, classify_scope(r"Archive\foo.md"))

    def test_posix_separator(self) -> None:
        self.assertIs(Scope.LEARNING, classify_scope("learning/example.md"))

    def test_absolute_path_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            classify_scope(r"C:\repository\Archive\foo.md")

    def test_parent_traversal_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            classify_scope("Archive/../foo.md")


if __name__ == "__main__":
    unittest.main()
