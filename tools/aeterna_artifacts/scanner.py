"""Repository discovery for Markdown files with native AETERNA metadata."""

from __future__ import annotations

from dataclasses import dataclass
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
_GENERATED_DIRECTORY = ("project", "generated")


@dataclass(frozen=True)
class DependencyGraph:
    """Deterministic dependency relationships derived from artifact records."""

    forward: tuple[tuple[str, tuple[str, ...]], ...]
    reverse: tuple[tuple[str, tuple[str, ...]], ...]
    missing_targets: tuple[tuple[str, str], ...]
    self_dependencies: tuple[str, ...]
    cycles: tuple[tuple[str, ...], ...]

    def forward_for(self, artifact_id: str) -> tuple[str, ...]:
        return dict(self.forward).get(artifact_id, ())

    def reverse_for(self, artifact_id: str) -> tuple[str, ...]:
        return dict(self.reverse).get(artifact_id, ())

    def transitive_dependents(self, artifact_id: str) -> tuple[str, ...]:
        seen: set[str] = set()
        pending = list(self.reverse_for(artifact_id))
        while pending:
            dependent = pending.pop(0)
            if dependent in seen:
                continue
            seen.add(dependent)
            pending.extend(
                item for item in self.reverse_for(dependent) if item not in seen
            )
        return tuple(sorted(seen))


def _canonical_cycle(nodes: list[str]) -> tuple[str, ...]:
    core = nodes[:-1]
    rotations = [tuple(core[index:] + core[:index]) for index in range(len(core))]
    canonical = min(rotations)
    return canonical + (canonical[0],)


def analyze_dependency_graph(records: Iterable[ArtifactRecord]) -> DependencyGraph:
    """Build a deterministic graph and report missing, self and cyclic edges."""
    materialized = tuple(sorted(records, key=lambda item: (item.artifact_id, item.path)))
    known_ids = {record.artifact_id for record in materialized}
    forward_map: dict[str, set[str]] = {artifact_id: set() for artifact_id in known_ids}
    missing: set[tuple[str, str]] = set()
    self_dependencies: set[str] = set()
    for record in materialized:
        for dependency in record.depends_on:
            forward_map[record.artifact_id].add(dependency)
            if dependency == record.artifact_id:
                self_dependencies.add(record.artifact_id)
            if dependency not in known_ids:
                missing.add((record.artifact_id, dependency))

    reverse_map: dict[str, set[str]] = {artifact_id: set() for artifact_id in known_ids}
    for source, dependencies in forward_map.items():
        for dependency in dependencies:
            if dependency in reverse_map:
                reverse_map[dependency].add(source)

    state: dict[str, int] = {artifact_id: 0 for artifact_id in known_ids}
    stack: list[str] = []
    cycles: set[tuple[str, ...]] = set()

    def visit(artifact_id: str) -> None:
        state[artifact_id] = 1
        stack.append(artifact_id)
        for dependency in sorted(forward_map[artifact_id]):
            if dependency not in state or dependency == artifact_id:
                continue
            if state[dependency] == 0:
                visit(dependency)
            elif state[dependency] == 1:
                start = stack.index(dependency)
                cycles.add(_canonical_cycle(stack[start:] + [dependency]))
        stack.pop()
        state[artifact_id] = 2

    for artifact_id in sorted(known_ids):
        if state[artifact_id] == 0:
            visit(artifact_id)

    return DependencyGraph(
        forward=tuple(
            (artifact_id, tuple(sorted(forward_map[artifact_id])))
            for artifact_id in sorted(forward_map)
        ),
        reverse=tuple(
            (artifact_id, tuple(sorted(reverse_map[artifact_id])))
            for artifact_id in sorted(reverse_map)
        ),
        missing_targets=tuple(sorted(missing)),
        self_dependencies=tuple(sorted(self_dependencies)),
        cycles=tuple(sorted(cycles)),
    )


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

    graph = analyze_dependency_graph(materialized)
    for source, target in graph.missing_targets:
        diagnostics.append(Diagnostic(
            "DOC_DEPENDENCY_MISSING",
            Severity.ERROR,
            f"Missing dependency target {target} referenced by {source}.",
            "depends_on",
        ))
    for artifact_id in graph.self_dependencies:
        diagnostics.append(Diagnostic(
            "DOC_DEPENDENCY_SELF",
            Severity.ERROR,
            f"Artifact {artifact_id} depends on itself.",
            "depends_on",
        ))
    for cycle in graph.cycles:
        diagnostics.append(Diagnostic(
            "DOC_DEPENDENCY_CYCLE",
            Severity.ERROR,
            f"Dependency cycle: {' -> '.join(cycle)}.",
            "depends_on",
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
