"""Bridge to the canonical export modules under their permanent data-tool owner."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
from types import ModuleType


TOOL_ROOT = Path("tools/data")
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

