"""Models and structured failures for the read-only document workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

from tools.aeterna_artifacts.model import (
    ArtifactMetadata,
    ArtifactRecord,
    Diagnostic,
    ScanResult,
    Severity,
)


class WorkflowError(Exception):
    """A categorized failure suitable for stable CLI exit handling."""

    def __init__(self, diagnostics: tuple[Diagnostic, ...], exit_code: int) -> None:
        super().__init__(diagnostics[0].message if diagnostics else "Workflow failed.")
        self.diagnostics = diagnostics
        self.exit_code = exit_code


def fail(
    code: str,
    message: str,
    *,
    exit_code: int = 1,
    field: str | None = None,
    severity: Severity = Severity.ERROR,
) -> NoReturn:
    raise WorkflowError((Diagnostic(code, severity, message, field),), exit_code)


@dataclass(frozen=True)
class ResolvedArtifact:
    root: Path
    record: ArtifactRecord
    scan: ScanResult


@dataclass(frozen=True)
class GitState:
    root: Path
    branch: str
    head: str
    worktree_entries: tuple[str, ...]
    staged_paths: tuple[str, ...]

    @property
    def clean(self) -> bool:
        return not self.worktree_entries and not self.staged_paths


@dataclass(frozen=True)
class ContentSnapshot:
    path: Path
    sha256: str
    encoding: str
    bom: bool
    newline: str
    front_matter_end: int
    body_bytes: bytes
    metadata: ArtifactMetadata
    metadata_fingerprint: str


@dataclass(frozen=True)
class MetadataDelta:
    field: str
    old: object
    new: object


@dataclass(frozen=True)
class UpdateManifest:
    artifact_id: str
    expected_branch: str
    expected_head: str
    expected_path: str
    baseline_sha256: str
    metadata_fingerprint: str
    change_class: str
    version_intent: str
    candidate_path: str
    candidate_sha256: str
    metadata_delta: tuple[MetadataDelta, ...]
    proposed_version: str | None


@dataclass(frozen=True)
class PreflightContext:
    manifest_path: Path
    manifest: UpdateManifest
    git: GitState
    resolved: ResolvedArtifact
    baseline: ContentSnapshot
    candidate: ContentSnapshot
    candidate_record: ArtifactRecord
    preconditions: tuple[dict[str, object], ...]
