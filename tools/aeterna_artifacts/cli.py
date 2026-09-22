"""Artifact tooling CLI. Exit codes: 0 success, 1 invalid data, 2 technical error.

metadata prints parsed YAML and validates it; validate prints JSON diagnostics.
scope and scan are read-only. generate writes only the two generated views.
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


def _diagnostics_data(diagnostics: tuple[Diagnostic, ...]) -> list[dict[str, object]]:
    return [asdict(item) for item in diagnostics]


def _has_errors(diagnostics: tuple[Diagnostic, ...]) -> bool:
    return any(item.severity in {Severity.ERROR, Severity.BLOCKING} for item in diagnostics)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AETERNA artifact metadata tooling.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("metadata", "Read and validate front matter; print YAML."),
        ("validate", "Validate one artifact; print JSON diagnostics."),
        ("scope", "Classify a repository-relative path."),
        ("scan", "Discover managed artifacts without writing files."),
        ("generate", "Generate the registry and document index."),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("path")
    args = parser.parse_args(argv)

    if args.command == "scope":
        try:
            print(classify_scope(args.path).value)
        except ValueError as exc:
            diagnostic = Diagnostic("SCOPE_PATH_INVALID", Severity.ERROR, str(exc))
            print(json.dumps([asdict(diagnostic)], ensure_ascii=False), file=sys.stderr)
            return 2
        return 0

    if args.command == "scan":
        from .scanner import scan_repository

        try:
            result = scan_repository(args.path)
        except (OSError, ValueError) as exc:
            diagnostic = Diagnostic("DOC_SCAN_EXECUTION_ERROR", Severity.ERROR, str(exc))
            print(json.dumps([asdict(diagnostic)], ensure_ascii=False), file=sys.stderr)
            return 2
        print(json.dumps({
            "artifact_count": len(result.artifacts),
            "artifact_ids": [item.artifact_id for item in result.artifacts],
            "diagnostics": _diagnostics_data(result.diagnostics),
        }, ensure_ascii=False, indent=2))
        return int(_has_errors(result.diagnostics))

    if args.command == "generate":
        from .generation import generate_repository

        try:
            result = generate_repository(args.path)
        except (OSError, ValueError) as exc:
            diagnostic = Diagnostic("DOC_GENERATION_EXECUTION_ERROR", Severity.ERROR, str(exc))
            print(json.dumps([asdict(diagnostic)], ensure_ascii=False), file=sys.stderr)
            return 2
        print(json.dumps({
            "artifact_count": len(result.artifacts),
            "artifact_ids": [item.artifact_id for item in result.artifacts],
            "written_paths": list(result.written_paths),
            "diagnostics": _diagnostics_data(result.diagnostics),
        }, ensure_ascii=False, indent=2))
        return int(_has_errors(result.diagnostics))

    result = read_metadata(args.path)
    diagnostics = result.diagnostics
    if result.metadata is not None:
        diagnostics += validate_metadata(result.metadata)
        if args.command == "metadata":
            import yaml

            print(yaml.safe_dump(dict(result.metadata.fields), allow_unicode=True, sort_keys=False), end="")
    stream = sys.stderr if args.command == "metadata" else sys.stdout
    print(json.dumps(_diagnostics_data(diagnostics), ensure_ascii=True), file=stream)
    if any(item.code in {"METADATA_READ_ERROR", "DEPENDENCY_MISSING"} for item in diagnostics):
        return 2
    return int(_has_errors(diagnostics))


if __name__ == "__main__":
    raise SystemExit(main())
