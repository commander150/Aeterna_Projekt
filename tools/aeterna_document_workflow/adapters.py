"""Pure format-adapter boundary for the Markdown MVP."""

from __future__ import annotations

from dataclasses import replace
import difflib
import re

from tools.aeterna_artifacts.model import ArtifactRecord, Severity
from tools.aeterna_artifacts.validation import validate_metadata

from .model import ContentSnapshot, WorkflowError, fail


_H1 = re.compile(r"^#[ \t]+(.+?)[ \t]*$")


def candidate_record(
    snapshot: ContentSnapshot,
    current: ArtifactRecord,
) -> ArtifactRecord:
    diagnostics = validate_metadata(snapshot.metadata)
    blocking = tuple(
        item for item in diagnostics
        if item.severity in {Severity.ERROR, Severity.BLOCKING}
    )
    if blocking:
        raise WorkflowError(blocking, 1)
    fields = snapshot.metadata.fields
    title = next(
        (
            match.group(1).strip()
            for line in snapshot.body_bytes.decode("utf-8").splitlines()
            if (match := _H1.fullmatch(line)) and match.group(1).strip()
        ),
        None,
    )
    if title is None:
        fail("TITLE_MISSING", "Candidate Markdown must contain a non-empty H1 title.")
    return replace(
        current,
        artifact_id=str(fields["artifact_id"]),
        kind=str(fields["kind"]),
        type=str(fields["type"]),
        version=fields.get("version") if isinstance(fields.get("version"), str) else None,
        lifecycle=str(fields["lifecycle"]),
        integration=str(fields["integration"]),
        authority=str(fields["authority"]),
        generated=bool(fields["generated"]),
        depends_on=tuple(fields.get("depends_on", ())),
        supersedes=tuple(fields.get("supersedes", ())),
        title=title,
    )


def metadata_differences(
    baseline: ContentSnapshot,
    candidate: ContentSnapshot,
) -> tuple[dict[str, object], ...]:
    old = dict(baseline.metadata.fields)
    new = dict(candidate.metadata.fields)
    return tuple(
        {"field": field, "old": old.get(field), "new": new.get(field)}
        for field in sorted(set(old) | set(new))
        if old.get(field) != new.get(field) or (field in old) != (field in new)
    )


def body_diff(baseline: ContentSnapshot, candidate: ContentSnapshot) -> list[dict[str, object]]:
    old = baseline.body_bytes.decode("utf-8").splitlines()
    new = candidate.body_bytes.decode("utf-8").splitlines()
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    return [
        {
            "operation": tag,
            "old_start": old_start + 1,
            "old_end": old_end,
            "new_start": new_start + 1,
            "new_end": new_end,
            "old_lines": old[old_start:old_end],
            "new_lines": new[new_start:new_end],
        }
        for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes()
        if tag != "equal"
    ]
