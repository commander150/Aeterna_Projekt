"""Canonical JSON, JSONL, and SHA-256 helpers for runtime comparison.

JSON is UTF-8 without BOM, uses lexicographically sorted object keys, two-space
indentation, LF line endings, and exactly one final newline. JSONL contains one
compact object per LF-terminated line. An empty JSONL input produces ``b""``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


class CanonicalJsonError(ValueError):
    """Raised when input cannot satisfy the canonical JSON contract."""


def canonical_json_bytes(value):
    """Serialize one JSON value to exact canonical UTF-8 bytes."""

    text = _dumps(value, indent=2, separators=(",", ": ")) + "\n"
    return text.encode("utf-8")


def canonical_json_text(value):
    """Serialize one JSON value to canonical text with one final LF."""

    return canonical_json_bytes(value).decode("utf-8")


def write_canonical_json(path, value):
    """Write canonical JSON only after the complete payload serializes."""

    output = canonical_json_bytes(value)
    target = Path(path)
    target.write_bytes(output)
    return target


def canonical_jsonl_bytes(records):
    """Serialize object records to compact JSONL; empty input returns b""."""

    lines = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise CanonicalJsonError(
                "JSONL record %s must be an object, got %s."
                % (index, type(record).__name__)
            )
        lines.append(_dumps(record, indent=None, separators=(",", ":")))
    if not lines:
        return b""
    return ("\n".join(lines) + "\n").encode("utf-8")


def write_canonical_jsonl(path, records):
    """Write canonical JSONL only after every record serializes."""

    output = canonical_jsonl_bytes(records)
    target = Path(path)
    target.write_bytes(output)
    return target


def sha256_bytes(data):
    """Return lowercase SHA-256 hexadecimal text for exact bytes."""

    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("data must be bytes-like.")
    return hashlib.sha256(bytes(data)).hexdigest()


def sha256_file(path):
    """Return lowercase SHA-256 hexadecimal text for a binary file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dumps(value, indent, separators):
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=indent,
            separators=separators,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise CanonicalJsonError("Value is not canonical JSON-compatible: %s" % exc) from exc


__all__ = [
    "CanonicalJsonError",
    "canonical_json_bytes",
    "canonical_json_text",
    "canonical_jsonl_bytes",
    "write_canonical_json",
    "write_canonical_jsonl",
    "sha256_bytes",
    "sha256_file",
]
