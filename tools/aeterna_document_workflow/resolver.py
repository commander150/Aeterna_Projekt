"""Fresh-scan artifact resolution without generated-registry authority."""

from __future__ import annotations

from pathlib import Path

from tools.aeterna_artifacts.model import Severity
from tools.aeterna_artifacts.scanner import scan_repository

from .model import ResolvedArtifact, WorkflowError, fail


def resolve_artifact(repository_root: str | Path, artifact_id: str) -> ResolvedArtifact:
    root = Path(repository_root).resolve()
    if not root.is_dir():
        fail("REPOSITORY_NOT_FOUND", f"Repository root does not exist: {root}", exit_code=2)
    scan = scan_repository(root)
    blocking = tuple(
        item for item in scan.diagnostics
        if item.severity in {Severity.ERROR, Severity.BLOCKING}
    )
    if blocking:
        raise WorkflowError(blocking, 1)
    matches = tuple(record for record in scan.artifacts if record.artifact_id == artifact_id)
    if not matches:
        fail("ARTIFACT_UNKNOWN", f"Unknown artifact ID: {artifact_id}", field="artifact_id")
    if len(matches) != 1:
        fail(
            "ARTIFACT_RESOLUTION_AMBIGUOUS",
            f"Artifact ID must resolve exactly once: {artifact_id}",
            field="artifact_id",
        )
    candidate = (root / matches[0].path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        fail("ARTIFACT_PATH_ESCAPE", f"Resolved path escapes repository: {matches[0].path}")
    return ResolvedArtifact(root, matches[0], scan)


def record_payload(record: object) -> dict[str, object]:
    return {
        "artifact_id": record.artifact_id,
        "path": record.path,
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
    }
