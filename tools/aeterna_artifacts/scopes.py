"""Lexical scope classification; no filesystem access or path resolution."""

from __future__ import annotations

from pathlib import PurePath, PureWindowsPath

from .model import Scope


def classify_scope(path: str | PurePath) -> Scope:
    """Classify a repository-relative path using Windows separators and casing.

    Dot components are normalized. Parent traversal and rooted/drive-qualified
    paths are rejected: callers must supply an unambiguous repository-relative
    path. Only the first component determines scope.
    """
    relative = PureWindowsPath(path)
    if relative.drive or relative.root or ".." in relative.parts:
        raise ValueError("Expected a repository-relative path without '..'.")
    first = relative.parts[0].casefold() if relative.parts else ""
    return {"archive": Scope.ARCHIVE, "learning": Scope.LEARNING}.get(first, Scope.ACTIVE)
