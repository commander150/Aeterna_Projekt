"""Read-only CLI. Exit codes: 0 success, 1 invalid metadata, 2 technical error.

metadata prints parsed YAML and validates it; validate prints JSON diagnostics.
scope prints the scope for a repository-relative path, without reading a file.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys

from .metadata import read_metadata
from .model import Diagnostic, Severity
from .scopes import classify_scope
from .validation import validate_metadata


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AETERNA read-only artifact metadata tooling (PILOT-1).")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("metadata", "Read and validate front matter; print YAML."),
        ("validate", "Validate one artifact; print JSON diagnostics."),
        ("scope", "Classify a repository-relative path."),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("path")
    args = parser.parse_args(argv)

    if args.command == "scope":
        try:
            print(classify_scope(args.path).value)
        except ValueError as exc:
            diagnostic = Diagnostic("SCOPE_PATH_INVALID", Severity.ERROR, str(exc))
            print(json.dumps([asdict(diagnostic)]), file=sys.stderr)
            return 2
        return 0

    result = read_metadata(args.path)
    diagnostics = result.diagnostics
    if result.metadata is not None:
        diagnostics += validate_metadata(result.metadata)
        if args.command == "metadata":
            import yaml

            print(yaml.safe_dump(dict(result.metadata.fields), allow_unicode=True, sort_keys=False), end="")
    stream = sys.stderr if args.command == "metadata" else sys.stdout
    print(json.dumps([asdict(item) for item in diagnostics], ensure_ascii=True), file=stream)
    if any(item.code in {"METADATA_READ_ERROR", "DEPENDENCY_MISSING"} for item in diagnostics):
        return 2
    return int(any(item.severity in {Severity.ERROR, Severity.BLOCKING} for item in diagnostics))


if __name__ == "__main__":
    raise SystemExit(main())
