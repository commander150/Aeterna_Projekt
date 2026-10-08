"""Fail-closed path and filesystem policy for read-only CREATE planning."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import stat
import unicodedata
from typing import Iterable

from tools.aeterna_artifacts.model import Scope

from .git_state import git_path_is_ignored, git_path_is_tracked
from .model import fail


_WINDOWS_RESERVED = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{number}" for number in range(1, 10)}
    | {f"lpt{number}" for number in range(1, 10)}
)


@dataclass(frozen=True)
class FilesystemEntry:
    path: str
    is_directory: bool


@dataclass(frozen=True)
class TargetInspection:
    relative_path: str
    absolute_path: Path
    scope: Scope
    parent_exists: bool
    parent_real: bool
    absent: bool
    collisions: tuple[str, ...]


def _has_reparse_component(root: Path, path: Path) -> bool:
    canonical_root = root.resolve()
    try:
        relative = path.absolute().relative_to(canonical_root)
    except ValueError:
        return True
    current = canonical_root
    for part in relative.parts:
        current = current / part
        if not os.path.lexists(current):
            continue
        try:
            attributes = getattr(current.lstat(), "st_file_attributes", 0)
        except OSError:
            return True
        if current.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            return True
    return False


def validate_candidate_path(
    root: Path,
    manifest_path: Path,
    candidate_path: str,
    target_path: str,
) -> Path:
    candidate = Path(candidate_path)
    windows = PureWindowsPath(candidate_path)
    if candidate.is_absolute() or windows.is_absolute() or windows.drive:
        fail("CREATE_CANDIDATE_PATH_BLOCKED", "CREATE candidate path must be relative to its manifest.")
    if ".." in windows.parts:
        fail("CREATE_CANDIDATE_PATH_BLOCKED", "CREATE candidate path cannot escape through '..'.")
    unresolved = manifest_path.parent / candidate
    if _has_reparse_component(root, unresolved):
        fail("CREATE_CANDIDATE_PATH_BLOCKED", "CREATE candidate cannot use symlink/reparse components.")
    try:
        resolved = unresolved.resolve(strict=True)
    except OSError as exc:
        fail("CONTENT_READ_ERROR", f"{unresolved}: {exc}", exit_code=2)
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        fail("CREATE_CANDIDATE_PATH_BLOCKED", "CREATE candidate must resolve inside the repository.")
    parts = PurePosixPath(relative).parts
    if not parts or parts[0].casefold() != "temp":
        fail("CREATE_CANDIDATE_PATH_BLOCKED", "CREATE candidate must resolve below repository TEMP.")
    if not resolved.is_file():
        fail("CREATE_CANDIDATE_PATH_BLOCKED", "CREATE candidate must be a regular file.")
    if git_path_is_tracked(root, relative) or not git_path_is_ignored(root, relative):
        fail("CREATE_CANDIDATE_PATH_BLOCKED", "CREATE candidate must be untracked and Git-ignored.")
    target = root.joinpath(*PurePosixPath(target_path).parts)
    if resolved == target.absolute():
        fail("CREATE_CANDIDATE_IS_TARGET", "CREATE candidate cannot be the canonical target.")
    return resolved


def validate_target_syntax(value: str) -> tuple[str, ...]:
    if not value:
        fail("CREATE_TARGET_PATH_INVALID", "CREATE target path cannot be empty.", field="target_path")
    if "\0" in value or "\\" in value or ":" in value:
        fail("CREATE_TARGET_PATH_INVALID", "CREATE target contains a forbidden character.", field="target_path")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    parts = value.split("/")
    if posix.is_absolute() or windows.is_absolute() or windows.drive:
        fail("CREATE_TARGET_PATH_INVALID", "CREATE target must be repository-relative.", field="target_path")
    if any(part in {"", ".", ".."} for part in parts):
        fail("CREATE_TARGET_PATH_INVALID", "CREATE target has an empty, dot or parent component.", field="target_path")
    if value != unicodedata.normalize("NFC", value):
        fail("CREATE_TARGET_PATH_INVALID", "CREATE target must already use NFC normalization.", field="target_path")
    for part in parts:
        if part.endswith((".", " ")):
            fail("CREATE_TARGET_PATH_INVALID", "CREATE target component has a trailing dot or space.", field="target_path")
        basename = part.split(".", 1)[0].casefold()
        if basename in _WINDOWS_RESERVED:
            fail("CREATE_TARGET_PATH_INVALID", f"Windows reserved target component: {part}.", field="target_path")
    if not value.endswith(".md"):
        fail("CREATE_TARGET_PATH_INVALID", "CREATE target extension must be exactly .md.", field="target_path")
    folded = tuple(part.casefold() for part in parts)
    allowed = folded[0] in {"project", "data", "design"} or folded[:3] == ("src", "engine", "docs")
    if not allowed or folded[:2] == ("project", "generated"):
        fail("CREATE_TARGET_SCOPE_BLOCKED", f"CREATE target root is not allowed: {value}.", field="target_path")
    return tuple(parts)


def filesystem_inventory(root: Path) -> tuple[FilesystemEntry, ...]:
    entries: list[FilesystemEntry] = []
    errors: list[OSError] = []

    def onerror(error: OSError) -> None:
        errors.append(error)

    for current, directories, files in os.walk(root, topdown=True, followlinks=False, onerror=onerror):
        current_path = Path(current)
        directories.sort(key=str.casefold)
        files.sort(key=str.casefold)
        for name in directories:
            path = current_path / name
            entries.append(FilesystemEntry(path.relative_to(root).as_posix(), True))
        for name in files:
            path = current_path / name
            entries.append(FilesystemEntry(path.relative_to(root).as_posix(), False))
    if errors:
        fail("CREATE_FILESYSTEM_INVENTORY_ERROR", str(errors[0]), exit_code=2)
    return tuple(entries)


def detect_path_collisions(
    target_path: str,
    inventory: Iterable[FilesystemEntry],
) -> tuple[str, ...]:
    target_nfc = unicodedata.normalize("NFC", target_path)
    target_fold = target_path.casefold()
    target_nfc_fold = target_nfc.casefold()
    collisions: set[str] = set()
    for entry in inventory:
        existing = entry.path
        existing_nfc = unicodedata.normalize("NFC", existing)
        if existing == target_path:
            collisions.add("EXACT")
        elif existing_nfc == target_nfc:
            collisions.add("UNICODE_NORMALIZATION")
        elif existing.casefold() == target_fold:
            collisions.add("CASE_INSENSITIVE")
        elif existing_nfc.casefold() == target_nfc_fold:
            collisions.add("UNICODE_CASEFOLD")
        existing_parts = existing_nfc.casefold().split("/")
        target_parts = target_nfc_fold.split("/")
        if not entry.is_directory and len(existing_parts) < len(target_parts) and target_parts[: len(existing_parts)] == existing_parts:
            collisions.add("FILE_DIRECTORY")
        if len(target_parts) < len(existing_parts) and existing_parts[: len(target_parts)] == target_parts:
            collisions.add("FILE_DIRECTORY")
    return tuple(sorted(collisions))


def inspect_target(root: Path, target_path: str) -> TargetInspection:
    parts = validate_target_syntax(target_path)
    canonical_root = root.resolve()
    target = canonical_root.joinpath(*parts)
    parent = target.parent
    parent_exists = parent.exists()
    parent_real = (
        parent_exists
        and parent.is_dir()
        and not _has_reparse_component(canonical_root, parent)
    )
    if not parent_exists:
        fail("CREATE_TARGET_PARENT_MISSING", f"CREATE target parent does not exist: {parent}.")
    if not parent_real:
        fail("CREATE_TARGET_PARENT_BLOCKED", f"CREATE target parent is not a real directory: {parent}.")
    absent = not os.path.lexists(target)
    if not absent or git_path_is_tracked(canonical_root, target_path):
        fail("CREATE_TARGET_NOT_ABSENT", f"CREATE target must be completely absent: {target_path}.")
    collisions = detect_path_collisions(target_path, filesystem_inventory(canonical_root))
    if collisions:
        fail("CREATE_TARGET_COLLISION", f"CREATE target collision: {', '.join(collisions)}.")
    return TargetInspection(
        target_path,
        target,
        Scope.ACTIVE,
        parent_exists,
        parent_real,
        absent,
        collisions,
    )
