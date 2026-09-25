"""TRANSITIONAL_TOOLING_BRIDGE to the existing canonical export modules.

The low-level implementation currently lives below
``Aeterna game engine/python/tools/canonical_export``.  This adapter discovers
that directory from the repository root, imports it as a namespace package,
and exposes the existing modules without copying their implementation.  It is
intentionally small so it can disappear when those modules move to their
permanent owner.
"""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
from types import ModuleType


TOOL_ROOT = Path("Aeterna game engine/python/tools")
MODULE_NAMES = (
    "canonical_export.canonical_workbook_exporter",
    "canonical_export.canonical_package_set",
    "canonical_export.canonical_validation_execution",
    "canonical_export.canonical_validation_rules",
    "canonical_export.canonical_validation_stage",
)


def load_existing_modules(repository_root: Path) -> dict[str, ModuleType]:
    """Load the existing modules through one repository-relative bridge."""

    root = repository_root.resolve()
    tool_root = (root / TOOL_ROOT).resolve()
    try:
        tool_root.relative_to(root)
    except ValueError as exc:
        raise ValueError("Canonical tooling root escapes the repository.") from exc
    if not tool_root.is_dir():
        raise FileNotFoundError(f"Canonical tooling root is missing: {TOOL_ROOT.as_posix()}")

    tool_root_text = str(tool_root)
    if tool_root_text not in sys.path:
        sys.path.insert(0, tool_root_text)
    return {
        name.rsplit(".", 1)[-1]: importlib.import_module(name)
        for name in MODULE_NAMES
    }

