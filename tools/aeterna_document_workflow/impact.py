"""Deterministic dependency impact reports."""

from __future__ import annotations

from typing import Iterable

from tools.aeterna_artifacts.model import ArtifactRecord
from tools.aeterna_artifacts.scanner import analyze_dependency_graph


def _dependent_payload(record: ArtifactRecord) -> dict[str, object]:
    return {
        "artifact_id": record.artifact_id,
        "path": record.path,
        "generated": record.generated,
        "impact": "STALE" if record.generated else "REVIEW_RECOMMENDED",
    }


def build_impact(
    records: Iterable[ArtifactRecord],
    artifact_id: str,
    *,
    include_transitive: bool,
) -> dict[str, object]:
    ordered = tuple(sorted(records, key=lambda item: item.artifact_id))
    by_id = {record.artifact_id: record for record in ordered}
    graph = analyze_dependency_graph(ordered)
    reverse_ids = graph.reverse_for(artifact_id)
    transitive_ids = graph.transitive_dependents(artifact_id) if include_transitive else ()
    return {
        "artifact_id": artifact_id,
        "forward_dependencies": list(graph.forward_for(artifact_id)),
        "direct_reverse_dependencies": [
            _dependent_payload(by_id[item]) for item in reverse_ids
        ],
        "transitive_reverse_dependents": [
            _dependent_payload(by_id[item]) for item in transitive_ids
        ],
        "graph_diagnostics": {
            "missing_targets": [list(item) for item in graph.missing_targets],
            "self_dependencies": list(graph.self_dependencies),
            "cycles": [list(item) for item in graph.cycles],
        },
    }
