"""Deterministic registry and document-index generation for managed artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from .model import ArtifactRecord, Diagnostic, Severity
from .scanner import scan_repository, validate_record_set


REGISTRY_PATH = Path("Aeterna dokumentációk/generated/artifacts_registry.json")
DOCUMENT_INDEX_PATH = Path("Aeterna dokumentációk/generated/DOCUMENT_INDEX.md")


@dataclass(frozen=True)
class GeneratedContent:
    registry: str
    document_index: str


@dataclass(frozen=True)
class GenerationResult:
    artifacts: tuple[ArtifactRecord, ...]
    diagnostics: tuple[Diagnostic, ...]
    written_paths: tuple[str, ...] = ()


class GenerationBlockedError(ValueError):
    def __init__(self, diagnostics: tuple[Diagnostic, ...]) -> None:
        super().__init__("Artifact generation blocked by validation diagnostics.")
        self.diagnostics = diagnostics


def _record_dict(record: ArtifactRecord) -> dict[str, object]:
    return {
        "artifact_id": record.artifact_id,
        "title": record.title,
        "kind": record.kind,
        "type": record.type,
        "version": record.version,
        "lifecycle": record.lifecycle,
        "integration": record.integration,
        "authority": record.authority,
        "generated": record.generated,
        "depends_on": list(record.depends_on),
        "supersedes": list(record.supersedes),
        "scope": record.scope.value,
        "path": record.path,
    }


def _table_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def build_generated_content(records: Iterable[ArtifactRecord]) -> GeneratedContent:
    """Build and validate both outputs entirely in memory."""
    ordered = tuple(sorted(records, key=lambda item: item.artifact_id))
    diagnostics = validate_record_set(ordered)
    if any(item.severity in {Severity.ERROR, Severity.BLOCKING} for item in diagnostics):
        raise GenerationBlockedError(diagnostics)

    payload = {
        "registry_schema_version": "0.1",
        "source_model": "native-artifact-metadata",
        "artifacts": [_record_dict(record) for record in ordered],
    }
    registry = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    lines = [
        "# AETERNA Document Index",
        "",
        "> GENERATED FILE — DO NOT EDIT MANUALLY.",
        "> Source: native artifact metadata.",
        "",
        "| Artifact ID | Title | Type | Version | Lifecycle | Integration | Authority | Path |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for record in ordered:
        values = (
            record.artifact_id,
            record.title,
            record.type,
            record.version,
            record.lifecycle,
            record.integration,
            record.authority,
            f"`{record.path}`",
        )
        lines.append("| " + " | ".join(_table_text(value) for value in values) + " |")
    document_index = "\n".join(lines) + "\n"

    if "\r" in registry or "\r" in document_index:
        raise ValueError("Generated outputs must contain LF line endings only.")
    if not registry.endswith("\n") or registry.endswith("\n\n"):
        raise ValueError("Registry must end with exactly one newline.")
    if not document_index.endswith("\n") or document_index.endswith("\n\n"):
        raise ValueError("Document index must end with exactly one newline.")
    json.loads(registry)
    return GeneratedContent(registry, document_index)


def _write_outputs(repository_root: Path, content: GeneratedContent) -> tuple[str, ...]:
    output_directory = repository_root / REGISTRY_PATH.parent
    output_directory.mkdir(parents=True, exist_ok=True)
    targets = (
        (repository_root / REGISTRY_PATH, content.registry),
        (repository_root / DOCUMENT_INDEX_PATH, content.document_index),
    )
    for target, text in targets:
        with target.open("w", encoding="utf-8", newline="\n") as output:
            output.write(text)
    return (REGISTRY_PATH.as_posix(), DOCUMENT_INDEX_PATH.as_posix())


def generate_repository(repository_root: str | Path) -> GenerationResult:
    """Scan, validate, render, then write only the two generated outputs."""
    root = Path(repository_root).resolve()
    scan = scan_repository(root)
    if any(item.severity in {Severity.ERROR, Severity.BLOCKING} for item in scan.diagnostics):
        return GenerationResult(scan.artifacts, scan.diagnostics)
    content = build_generated_content(scan.artifacts)
    written_paths = _write_outputs(root, content)
    return GenerationResult(scan.artifacts, scan.diagnostics, written_paths)
