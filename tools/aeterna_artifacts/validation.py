"""Deterministic, single-artifact metadata validation for contract v0.1."""

from __future__ import annotations

import re

from .model import ArtifactMetadata, Diagnostic, Severity

CONTROLLED_VALUES: dict[str, frozenset[str]] = {
    "kind": frozenset({"document", "data-source", "generated-output", "package", "blueprint"}),
    "type": frozenset({
        "governance", "roadmap", "project-plan", "checkpoint", "status", "architecture",
        "specification", "contract", "workflow", "decision-log", "open-questions",
        "design-guide", "template", "reference", "index", "blueprint",
    }),
    "lifecycle": frozenset({"draft", "active", "deprecated", "historical"}),
    "integration": frozenset({"current", "pending_integration", "recovery_candidate"}),
    "authority": frozenset({
        "canonical-rules", "project-direction", "document-governance",
        "technical-architecture", "technical-contract", "technical-status",
        "operational-workflow", "canonical-card-data", "canonical-technical-schema",
        "design-guidance", "reference", "derived", "historical",
    }),
}

_ID_PATTERN = re.compile(r"AET-(?:DOC|DATA|SOURCE|GEN|PKG|BP)-[A-Z0-9]+(?:-[A-Z0-9]+)*")


def is_valid_artifact_id(value: object) -> bool:
    """Validate the lexical PILOT-1 ID grammar.

    The logical name contains one or more uppercase ASCII alphanumeric tokens,
    separated by single hyphens. Semantic governance rules, such as whether a
    token represents a version or lifecycle state, are outside PILOT-1.
    """
    return isinstance(value, str) and _ID_PATTERN.fullmatch(value) is not None


def validate_metadata(metadata: ArtifactMetadata) -> tuple[Diagnostic, ...]:
    """Validate fields only; no repository lookup, graph checking or mutation.

    A manually edited document is kind=document with generated=false. Its
    version must be a nonblank string; quote numeric-looking versions in YAML.
    If version is supplied for another artifact it must also be a nonblank string.
    Optional relationship fields must be YAML lists when present (null is invalid).
    """
    fields = metadata.fields
    diagnostics: list[Diagnostic] = []

    def error(code: str, field: str, message: str) -> None:
        diagnostics.append(Diagnostic(code, Severity.ERROR, message, field))

    artifact_id = fields.get("artifact_id")
    if artifact_id is None or artifact_id == "":
        error("ARTIFACT_ID_REQUIRED", "artifact_id", "artifact_id is required.")
    elif not is_valid_artifact_id(artifact_id):
        error("ARTIFACT_ID_INVALID", "artifact_id", "Invalid stable artifact ID.")

    for field, allowed in CONTROLLED_VALUES.items():
        value = fields.get(field)
        if not isinstance(value, str) or value not in allowed:
            error(f"{field.upper()}_INVALID", field, f"Expected one of: {', '.join(sorted(allowed))}.")

    generated = fields.get("generated")
    if not isinstance(generated, bool):
        error("GENERATED_INVALID", "generated", "generated must be a boolean.")
    version_required = fields.get("kind") == "document" and generated is False
    if version_required or "version" in fields:
        version = fields.get("version")
        if not isinstance(version, str) or not version.strip():
            error("VERSION_INVALID", "version", "version must be a nonblank string.")

    for field in ("depends_on", "supersedes"):
        if field not in fields:
            continue
        references = fields[field]
        if not isinstance(references, list):
            error(f"{field.upper()}_INVALID", field, "Expected a list of artifact IDs.")
            continue
        for index, reference in enumerate(references):
            location = f"{field}[{index}]"
            if not is_valid_artifact_id(reference):
                error(f"{field.upper()}_ID_INVALID", location, "Invalid referenced artifact ID.")
            elif reference == artifact_id:
                error(f"{field.upper()}_SELF", location, "An artifact cannot reference itself here.")

    return tuple(diagnostics)
