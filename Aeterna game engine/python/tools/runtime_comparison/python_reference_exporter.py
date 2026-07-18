"""Versioned canonical artifact exporter for the Python comparison oracle."""

from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

from .canonical_json import CanonicalJsonError, canonical_json_bytes
from .python_reference_fixture import (
    RuntimeComparisonFixtureError,
    run_python_reference_fixture,
)
from .runtime_comparison_artifact_builder import (
    CANONICAL_ARTIFACT_PATHS,
    DIAGNOSTICS_SCHEMA_VERSION,
    REQUIRED_OUTPUT_PATHS,
    RUN_MANIFEST_SCHEMA_VERSION,
    RuntimeComparisonArtifactBuildError,
    build_artifact_package,
    preflight_output_directory,
    validate_fixture_result,
    write_atomic_artifact_package,
)


class PythonReferenceExportError(Exception):
    """Stable exporter failure with JSON-compatible, path-safe details."""

    def __init__(self, code, message, details=None):
        self.code = str(code)
        self.message = str(message)
        self.details = deepcopy(details or {})
        try:
            canonical_json_bytes(self.to_dict())
        except CanonicalJsonError as exc:
            raise ValueError("Exporter error details must be canonical JSON-compatible.") from exc
        super().__init__("%s: %s" % (self.code, self.message))

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "details": deepcopy(self.details),
        }


def export_python_reference_artifacts(fixture_path, output_directory, *, replace=False):
    """Run the fixed fixture and atomically export its versioned artifacts."""

    try:
        target = preflight_output_directory(output_directory, replace=replace)
    except RuntimeComparisonArtifactBuildError as exc:
        _raise_export_error(exc)

    first_result = _run_fixture(fixture_path)
    second_result = _run_fixture(fixture_path)
    try:
        deterministic = canonical_json_bytes(first_result) == canonical_json_bytes(second_result)
    except CanonicalJsonError as exc:
        raise PythonReferenceExportError(
            "artifact_contract_invalid",
            "Fixture result is not canonical JSON-compatible.",
        ) from exc
    if not deterministic:
        raise PythonReferenceExportError(
            "artifact_contract_invalid",
            "Two clean fixture runs produced different canonical results.",
            {"check": "runner_determinism"},
        )

    build_identifier, build_deviation = _resolve_build_identifier()
    known_deviations = () if build_deviation is None else (build_deviation,)
    try:
        validate_fixture_result(first_result)
        planned_files, manifest = build_artifact_package(
            first_result,
            runtime_candidate="python_reference",
            implementation_language="python",
            runtime_version=platform.python_version(),
            operating_system=platform.system().lower() or "unknown",
            architecture=platform.machine().lower() or "unknown",
            build_identifier=build_identifier,
            known_deviations=known_deviations,
            implementation_specific={
                "exporter_id": "python_reference_exporter_v1",
                "fixture_result_schema_version": first_result["schema_version"],
            },
        )
        write_atomic_artifact_package(
            target,
            planned_files,
            manifest,
            replace=replace,
        )
    except RuntimeComparisonArtifactBuildError as exc:
        _raise_export_error(exc)
    return deepcopy(manifest)


def _run_fixture(fixture_path):
    try:
        return run_python_reference_fixture(fixture_path)
    except RuntimeComparisonFixtureError as exc:
        raise PythonReferenceExportError(
            "fixture_run_failed",
            "Python reference fixture execution failed.",
            {"fixture_error": exc.to_dict()},
        ) from None
    except Exception:
        raise PythonReferenceExportError(
            "fixture_run_failed",
            "Python reference fixture execution failed.",
        ) from None


def _resolve_build_identifier():
    repository_root = Path(__file__).resolve().parents[4]
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        value = completed.stdout.strip().lower()
        if completed.returncode == 0 and len(value) == 40 and all(
            char in "0123456789abcdef" for char in value
        ):
            return value, None
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown", {
        "code": "BUILD_IDENTIFIER_UNAVAILABLE",
        "blocking": False,
        "description": "The source Git commit could not be resolved during export.",
    }


def _raise_export_error(error):
    raise PythonReferenceExportError(
        error.code,
        error.message,
        error.details,
    ) from error


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export canonical Python runtime comparison artifacts.")
    parser.add_argument("--fixture", required=True, help="Path to the comparison fixture.json file.")
    parser.add_argument("--output", required=True, help="Output directory to create.")
    parser.add_argument("--replace", action="store_true", help="Replace only the explicit output directory.")
    args = parser.parse_args(argv)
    try:
        manifest = export_python_reference_artifacts(
            args.fixture,
            args.output,
            replace=args.replace,
        )
    except PythonReferenceExportError as exc:
        print("%s: %s" % (exc.code, exc.message), file=sys.stderr)
        return 1
    print("Python reference artifacts exported.")
    print("fixture_id: %s" % manifest["fixture_id"])
    print("oracle_version: %s" % manifest["oracle_version"])
    print("canonical_artifact_count: %s" % len(manifest["canonical_artifacts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CANONICAL_ARTIFACT_PATHS",
    "DIAGNOSTICS_SCHEMA_VERSION",
    "PythonReferenceExportError",
    "REQUIRED_OUTPUT_PATHS",
    "RUN_MANIFEST_SCHEMA_VERSION",
    "export_python_reference_artifacts",
    "main",
]
