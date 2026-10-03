"""Strict, byte-preserving inspection of managed Markdown documents."""

from __future__ import annotations

import codecs
import hashlib
import json
from pathlib import Path

from tools.aeterna_artifacts.metadata import parse_metadata

from .model import ContentSnapshot, fail


def canonical_metadata_bytes(fields: object) -> bytes:
    """Serialize parsed native values with sorted keys and compact JSON."""
    try:
        text = json.dumps(
            fields,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        fail("METADATA_CANONICALIZATION_ERROR", str(exc), exit_code=2)
    return text.encode("utf-8")


def metadata_fingerprint(fields: object) -> str:
    return hashlib.sha256(canonical_metadata_bytes(fields)).hexdigest()


def inspect_markdown_bytes(data: bytes, path: str | Path = "<memory>") -> ContentSnapshot:
    target = Path(path)
    bom = data.startswith(codecs.BOM_UTF8)
    payload = data[len(codecs.BOM_UTF8):] if bom else data
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        fail("CONTENT_UTF8_INVALID", f"{target}: {exc}")

    without_crlf = payload.replace(b"\r\n", b"")
    if b"\r" in without_crlf:
        fail("CONTENT_LONE_CR", f"{target}: lone CR is not allowed.")
    crlf_count = payload.count(b"\r\n")
    lf_count = without_crlf.count(b"\n")
    if crlf_count and lf_count:
        fail("CONTENT_NEWLINE_MIXED", f"{target}: mixed LF and CRLF newlines.")
    newline = "CRLF" if crlf_count else "LF" if lf_count else "NONE"

    parsed = parse_metadata(text)
    if parsed.metadata is None:
        raise_failure = parsed.diagnostics[0] if parsed.diagnostics else None
        fail(
            raise_failure.code if raise_failure else "METADATA_INVALID",
            f"{target}: {raise_failure.message if raise_failure else 'Invalid metadata.'}",
        )

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n \t") != "---":
        fail("METADATA_MISSING", f"{target}: missing front matter.")
    closing = next(
        (index for index in range(1, len(lines)) if lines[index].rstrip("\r\n \t") == "---"),
        None,
    )
    if closing is None:
        fail("METADATA_UNCLOSED", f"{target}: missing front matter boundary.")
    prefix = "".join(lines[: closing + 1]).encode("utf-8")
    body = "".join(lines[closing + 1:]).encode("utf-8")
    fields = dict(parsed.metadata.fields)
    return ContentSnapshot(
        path=target,
        sha256=hashlib.sha256(data).hexdigest(),
        encoding="UTF-8",
        bom=bom,
        newline=newline,
        front_matter_end=len(codecs.BOM_UTF8) * int(bom) + len(prefix),
        body_bytes=body,
        metadata=parsed.metadata,
        metadata_fingerprint=metadata_fingerprint(fields),
    )


def inspect_markdown(path: str | Path) -> ContentSnapshot:
    target = Path(path)
    try:
        data = target.read_bytes()
    except OSError as exc:
        fail("CONTENT_READ_ERROR", f"{target}: {exc}", exit_code=2)
    return inspect_markdown_bytes(data, target)
