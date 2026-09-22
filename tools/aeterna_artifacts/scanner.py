"""Repository discovery for Markdown files with native AETERNA metadata."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
from typing import Iterable

from .metadata import parse_metadata
from .model import ArtifactRecord, Diagnostic, ScanResult, Scope, Severity
from .scopes import classify_scope
from .validation import validate_metadata


_ARTIFACT_KEY = re.compile(r"(?m)^[ \t]*artifact_id[ \t]*:")
_H1 = re.compile(r"^#[ \t]+(.+?)[ \t]*$")
_EXCLUDED_ROOTS = frozenset({".git", ".venv", "temp", "learning", "archive"})
_GENERATED_DIRECTORY = ("aeterna dokumentációk", "generated")


def _front_matter_end(lines: list[str]) -> int | None:
    if not lines or lines[0].rstrip(" \t") != "---":
        return None
    return next(
        (index for index in range(1, len(lines)) if lines[index].rstrip(" \t") == "---"),
        None,
    )


def _is_managed_candidate(text: str) -> bool:
    lines = text.removeprefix("\ufeff").splitlines()
    if not lines or lines[0].rstrip(" \t") != "---":
        return False
    closing = _front_matter_end(lines)
    candidate_lines = lines[1:closing] if closing is not None else lines[1:]
    return _ARTIFACT_KEY.search("\n".join(candidate_lines)) is not None


def _extract_title(text: str) -> str | None:
    lines = text.removeprefix("\ufeff").splitlines()
    closing = _front_matter_end(lines)
    if closing is None:
        return None
    for line in lines[closing + 1:]:
        match = _H1.fullmatch(line)
        if match and match.group(1).strip():
            return match.group(1).strip()
    return None


def _excluded(parts: tuple[str, ...]) -> bool:
    folded = tuple(part.casefold() for part in parts)
    if folded and folded[0] in _EXCLUDED_ROOTS:
        return True
    return folded[:2] == _GENERATED_DIRECTORY


def _with_path(diagnostic: Diagnostic, path: str) -> Diagnostic:
    return Diagnostic(
        diagnostic.code,
        diagnostic.severity,
        f"{path}: {diagnostic.message}",
        diagnostic.field,
    )


def _path_is_registry_safe(path: str) -> bool:
    posix = PurePosixPath(path)
    windows = PureWindowsPath(path)
    return (
        bool(path)
        and "\\" not in path
        and not posix.is_absolute()
        and not windows.is_absolute()
        and not windows.drive
        and ".." not in posix.parts
    )


def validate_record_set(records: Iterable[ArtifactRecord]) -> tuple[Diagnostic, ...]:
    """Validate repository-wide identity and registry path invariants."""
    materialized = tuple(records)
    diagnostics: list[Diagnostic] = []

    by_id: dict[str, list[str]] = {}
    by_folded_path: dict[str, list[str]] = {}
    for record in materialized:
        by_id.setdefault(record.artifact_id, []).append(record.path)
        by_folded_path.setdefault(record.path.casefold(), []).append(record.path)
        if not _path_is_registry_safe(record.path):
            diagnostics.append(Diagnostic(
                "DOC_INVALID_REGISTRY_PATH",
                Severity.ERROR,
                f"Registry path must be repository-relative POSIX form: {record.path!r}.",
                "path",
            ))

    for artifact_id, paths in sorted(by_id.items()):
        if len(paths) > 1:
            diagnostics.append(Diagnostic(
                "DOC_DUPLICATE_ARTIFACT_ID",
                Severity.ERROR,
                f"Duplicate artifact ID {artifact_id}: {', '.join(sorted(paths))}.",
                "artifact_id",
            ))

    for paths in sorted(by_folded_path.values(), key=lambda values: values[0].casefold()):
        unique_paths = sorted(set(paths))
        if len(unique_paths) > 1:
            diagnostics.append(Diagnostic(
                "DOC_PATH_CASE_COLLISION",
                Severity.ERROR,
                f"Case-insensitive path collision: {', '.join(unique_paths)}.",
                "path",
            ))

    return tuple(diagnostics)


def _record_from_text(text: str, path: str) -> tuple[ArtifactRecord | None, tuple[Diagnostic, ...]]:
    parsed = parse_metadata(text)
    if parsed.metadata is None:
        return None, tuple(_with_path(item, path) for item in parsed.diagnostics)

    diagnostics = tuple(
        _with_path(item, path) for item in validate_metadata(parsed.metadata)
    )
    if any(item.severity in {Severity.ERROR, Severity.BLOCKING} for item in diagnostics):
        return None, diagnostics

    title = _extract_title(text)
    if title is None:
        return None, diagnostics + (Diagnostic(
            "DOC_TITLE_MISSING",
            Severity.ERROR,
            f"{path}: Managed Markdown artifact has no H1 title after front matter.",
            "title",
        ),)

    fields = parsed.metadata.fields
    record = ArtifactRecord(
        artifact_id=fields["artifact_id"],  # type: ignore[arg-type]
        kind=fields["kind"],  # type: ignore[arg-type]
        type=fields["type"],  # type: ignore[arg-type]
        version=fields.get("version") if isinstance(fields.get("version"), str) else None,
        lifecycle=fields["lifecycle"],  # type: ignore[arg-type]
        integration=fields["integration"],  # type: ignore[arg-type]
        authority=fields["authority"],  # type: ignore[arg-type]
        generated=fields["generated"],  # type: ignore[arg-type]
        depends_on=tuple(fields.get("depends_on", [])),  # type: ignore[arg-type]
        supersedes=tuple(fields.get("supersedes", [])),  # type: ignore[arg-type]
        path=path,
        scope=classify_scope(path),
        title=title,
    )
    return record, diagnostics


def scan_repository(repository_root: str | Path) -> ScanResult:
    """Discover valid, managed ACTIVE Markdown artifacts without writing files."""
    root = Path(repository_root)
    if not root.exists():
        raise FileNotFoundError(f"Repository root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository root is not a directory: {root}")
    root = root.resolve()

    records: list[ArtifactRecord] = []
    diagnostics: list[Diagnostic] = []
    for current, directory_names, file_names in os.walk(root):
        current_path = Path(current)
        relative_directory = current_path.relative_to(root)
        relative_parts = () if relative_directory == Path(".") else relative_directory.parts
        directory_names[:] = sorted(
            (
                name for name in directory_names
                if not _excluded(relative_parts + (name,))
            ),
            key=str.casefold,
        )
        for file_name in sorted(file_names, key=str.casefold):
            if Path(file_name).suffix.casefold() != ".md":
                continue
            source_path = current_path / file_name
            relative_path = source_path.relative_to(root).as_posix()
            if _excluded(tuple(PurePosixPath(relative_path).parts)):
                continue
            try:
                text = source_path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as exc:
                diagnostics.append(Diagnostic(
                    "DOC_SCAN_READ_ERROR",
                    Severity.ERROR,
                    f"{relative_path}: Cannot read UTF-8 Markdown: {exc}",
                ))
                continue
            if not _is_managed_candidate(text):
                continue
            record, record_diagnostics = _record_from_text(text, relative_path)
            diagnostics.extend(record_diagnostics)
            if record is not None:
                records.append(record)

    records.sort(key=lambda item: item.artifact_id)
    diagnostics.extend(validate_record_set(records))
    return ScanResult(tuple(records), tuple(diagnostics))
