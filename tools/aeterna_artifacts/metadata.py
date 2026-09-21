"""Read UTF-8 Markdown front matter without interpreting or changing its body."""

from __future__ import annotations

from pathlib import Path

from .model import ArtifactMetadata, Diagnostic, ParseResult, Severity


def _failure(code: str, message: str) -> ParseResult:
    return ParseResult(diagnostics=(Diagnostic(code, Severity.ERROR, message),))


def parse_metadata(text: str) -> ParseResult:
    """Parse an initial, line-delimited YAML block using yaml.safe_load.

    Delimiters must be exactly '---' (optional trailing spaces/tabs). Leading
    blank lines are not front matter. A single initial UTF-8 BOM is tolerated.
    """
    lines = text.removeprefix("\ufeff").splitlines()
    if not lines or lines[0].rstrip(" \t") != "---":
        return _failure("METADATA_MISSING", "No YAML front matter at start of file.")
    closing = next(
        (i for i in range(1, len(lines)) if lines[i].rstrip(" \t") == "---"),
        None,
    )
    if closing is None:
        return _failure("METADATA_UNCLOSED", "Missing closing front matter delimiter.")

    # Lazy import keeps CLI help, scope and pure validation usable without YAML.
    try:
        import yaml
    except ImportError:
        return _failure("DEPENDENCY_MISSING", "PyYAML is required to parse metadata.")
    try:
        data = yaml.safe_load("\n".join(lines[1:closing]))
    except (yaml.YAMLError, RecursionError) as exc:
        return _failure("METADATA_YAML_INVALID", f"Invalid YAML: {exc}")
    if not isinstance(data, dict) or any(not isinstance(key, str) for key in data):
        return _failure("METADATA_MAPPING_REQUIRED", "Front matter must be a string-keyed mapping.")
    return ParseResult(metadata=ArtifactMetadata(data))


def read_metadata(path: str | Path) -> ParseResult:
    """Only read the given file; report I/O and decoding failures structurally."""
    try:
        text = Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError, ValueError) as exc:
        return _failure("METADATA_READ_ERROR", f"Cannot read UTF-8 metadata: {exc}")
    return parse_metadata(text)
