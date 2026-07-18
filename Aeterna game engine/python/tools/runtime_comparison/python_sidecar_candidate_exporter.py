"""Export validated comparison artifacts from a separate Python sidecar."""

from __future__ import annotations

import argparse
import os
import platform
import socket
import subprocess
import sys
from copy import deepcopy
from pathlib import Path, PurePosixPath

from tools.runtime_comparison.artifact_validator import (
    ArtifactValidatorInputError,
    validate_runtime_comparison_artifacts,
)
from tools.runtime_comparison.canonical_json import (
    CanonicalJsonError,
    canonical_json_bytes,
    sha256_bytes,
)
from tools.runtime_comparison.python_sidecar_client import PythonSidecarClientError
from tools.runtime_comparison.python_sidecar_process import (
    PythonSidecarProcess,
    PythonSidecarProcessError,
)
from tools.runtime_comparison.runtime_comparison_artifact_builder import (
    CANONICAL_ARTIFACT_PATHS,
    FIXTURE_ID,
    RuntimeComparisonArtifactBuildError,
    build_artifact_package,
    preflight_output_directory,
    validate_fixture_result,
    write_atomic_artifact_package,
)
from tools.runtime_comparison.sidecar_protocol import MAX_FRAME_SIZE, PROTOCOL_VERSION


CANDIDATE_EXPORT_SCHEMA_VERSION = "aeterna-python-sidecar-candidate-export-result-v1"
CANDIDATE_EXPORT_CONTRACT_TYPE = "python_sidecar_candidate_export_result"
RUNTIME_CANDIDATE = "python_sidecar_headless"
FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "runtime_comparison" / "fixtures"
FIXTURE_REQUEST_PATH = "minimal_draw_end_turn_v1/fixture.json"

_KNOWN_DEVIATION_CODES = (
    "no_transport_authentication",
    "no_tls",
    "no_reconnect",
    "no_request_multiplexing",
    "single_client_proof_server",
    "no_os_process_sandbox",
    "no_production_service_installation",
    "no_release_hardening",
)
_KNOWN_DEVIATION_DESCRIPTIONS = {
    "no_transport_authentication": "The loopback proof transport has no authentication.",
    "no_tls": "The loopback proof transport does not use TLS.",
    "no_reconnect": "The proof client does not reconnect after transport failure.",
    "no_request_multiplexing": "The proof transport handles requests sequentially.",
    "single_client_proof_server": "The proof server accepts one client workflow at a time.",
    "no_os_process_sandbox": "The sidecar proof does not add an OS process sandbox.",
    "no_production_service_installation": "The sidecar is not installed as a production service.",
    "no_release_hardening": "The sidecar proof has not received release hardening.",
}


class PythonSidecarCandidateExportError(Exception):
    """Stable candidate export failure with a CLI exit category."""

    def __init__(self, code, message, details=None, *, category="export"):
        self.code = str(code)
        self.message = str(message)
        self.details = deepcopy(details or {})
        self.category = str(category)
        try:
            canonical_json_bytes(self.to_dict())
        except CanonicalJsonError as exc:
            raise ValueError("Candidate export error details must be canonical JSON-compatible.") from exc
        super().__init__("%s: %s" % (self.code, self.message))

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "details": deepcopy(self.details),
            "category": self.category,
        }


def export_python_sidecar_candidate_artifacts(
    fixture_path,
    output_directory,
    *,
    replace=False,
):
    """Run the fixture through TCP and atomically export a valid candidate."""

    fixture_request_path = _normalize_fixture_request_path(fixture_path)
    try:
        target = preflight_output_directory(output_directory, replace=replace)
    except RuntimeComparisonArtifactBuildError as exc:
        _raise_candidate_error(exc)

    candidate_result, lifecycle = _run_sidecar_fixture(fixture_request_path)
    build_identifier, build_deviation = _resolve_build_identifier()
    deviations = _candidate_known_deviations()
    if build_deviation is not None:
        deviations.append(build_deviation)

    try:
        validate_fixture_result(candidate_result)
        planned_files, manifest = build_artifact_package(
            candidate_result,
            runtime_candidate=RUNTIME_CANDIDATE,
            implementation_language="python",
            runtime_version=platform.python_version(),
            operating_system=platform.system().lower() or "unknown",
            architecture=platform.machine().lower() or "unknown",
            build_identifier=build_identifier,
            known_deviations=deviations,
            implementation_specific={
                "exporter_id": "python_sidecar_candidate_exporter_v1",
                "fixture_result_schema_version": candidate_result["schema_version"],
                "process_model": "separate_python_process",
                "transport_protocol": PROTOCOL_VERSION,
                "transport_scope": "ipv4_loopback",
                "frame_prefix_bytes": 4,
                "frame_byte_order": "big_endian",
                "maximum_frame_bytes": MAX_FRAME_SIZE,
                "lifecycle_sequence": "health_fixture_shutdown",
            },
        )

        def validate_staging(staging):
            try:
                validation = validate_runtime_comparison_artifacts(
                    staging,
                    expected_fixture_id=FIXTURE_ID,
                )
            except ArtifactValidatorInputError as exc:
                raise RuntimeComparisonArtifactBuildError(
                    "candidate_validation_failed",
                    "Candidate artifact validation could not run.",
                    {"validator_code": exc.code},
                ) from exc
            if not validation.get("valid"):
                raise RuntimeComparisonArtifactBuildError(
                    "candidate_validation_failed",
                    "Candidate artifact validation failed.",
                    {
                        "error_count": validation.get("summary", {}).get("error_count", 0),
                    },
                )
            return validation

        validation = write_atomic_artifact_package(
            target,
            planned_files,
            manifest,
            replace=replace,
            package_validator=validate_staging,
        )
    except RuntimeComparisonArtifactBuildError as exc:
        _raise_candidate_error(exc)

    result = {
        "schema_version": CANDIDATE_EXPORT_SCHEMA_VERSION,
        "contract_type": CANDIDATE_EXPORT_CONTRACT_TYPE,
        "fixture_id": manifest["fixture_id"],
        "runtime_candidate": RUNTIME_CANDIDATE,
        "transport_protocol": PROTOCOL_VERSION,
        "canonical_artifacts": deepcopy(manifest["canonical_artifacts"]),
        "manifest_sha256": sha256_bytes(planned_files["run_manifest.json"]),
        "lifecycle": lifecycle,
        "validation": _validation_summary(validation),
        "success": True,
    }
    canonical_json_bytes(result)
    return result


def _normalize_fixture_request_path(fixture_path):
    try:
        raw = os.fspath(fixture_path)
    except TypeError as exc:
        raise PythonSidecarCandidateExportError(
            "SIDECAR_CANDIDATE_FIXTURE_INPUT_INVALID",
            "Fixture path must be a path string.",
            category="technical",
        ) from exc
    if not isinstance(raw, str) or not raw:
        raise PythonSidecarCandidateExportError(
            "SIDECAR_CANDIDATE_FIXTURE_INPUT_INVALID",
            "Fixture path must be a non-empty path string.",
            category="technical",
        )

    root = FIXTURE_ROOT.resolve()
    native_path = Path(raw)
    try:
        if native_path.is_absolute():
            resolved = native_path.resolve(strict=True)
            relative = resolved.relative_to(root)
        else:
            normalized = raw.replace("\\", "/")
            if ":" in normalized:
                raise ValueError("drive-qualified path")
            pure = PurePosixPath(normalized)
            if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
                raise ValueError("unsafe relative path")
            resolved = root.joinpath(*pure.parts).resolve(strict=True)
            relative = resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise PythonSidecarCandidateExportError(
            "SIDECAR_CANDIDATE_FIXTURE_INPUT_INVALID",
            "Fixture must be an existing file inside the runtime comparison fixture root.",
            category="technical",
        ) from exc
    if not resolved.is_file() or relative.name != "fixture.json":
        raise PythonSidecarCandidateExportError(
            "SIDECAR_CANDIDATE_FIXTURE_INPUT_INVALID",
            "Fixture must name an allowed fixture.json file.",
            category="technical",
        )
    return relative.as_posix()


def _run_sidecar_fixture(fixture_request_path):
    sidecar = PythonSidecarProcess()
    try:
        sidecar.start()
        separate_process = sidecar.pid != os.getpid()
        health_response = sidecar.client.health("candidate_req_0001_health")
        health_result = health_response.get("result") or {}
        if (
            health_result.get("status") != "ready"
            or health_result.get("protocol_version") != PROTOCOL_VERSION
            or health_result.get("runtime_candidate") != RUNTIME_CANDIDATE
        ):
            raise PythonSidecarCandidateExportError(
                "SIDECAR_CANDIDATE_HEALTH_INVALID",
                "Python sidecar health response is not compatible with the candidate exporter.",
            )
        fixture_response = sidecar.client.run_runtime_comparison_fixture(
            "candidate_req_0002_fixture",
            fixture_request_path,
        )
        candidate_result = deepcopy(fixture_response.get("result"))
        shutdown_response = sidecar.shutdown("candidate_req_0003_shutdown")
        listener_closed = _listener_is_closed(sidecar.host, sidecar.port)
        lifecycle = {
            "startup_succeeded": True,
            "health_succeeded": health_response.get("ok") is True,
            "fixture_succeeded": fixture_response.get("ok") is True,
            "shutdown_succeeded": (
                shutdown_response.get("ok") is True
                and (shutdown_response.get("result") or {}).get("status") == "shutting_down"
            ),
            "process_exit_code": sidecar.exit_code,
            "process_stopped": not sidecar.is_alive,
            "listener_closed": listener_closed,
            "stdout_clean": sidecar.stdout_remainder == "",
            "stderr_clean": sidecar.stderr_text == "",
            "separate_process": separate_process,
            "forced_termination_used": sidecar.terminate_used or sidecar.kill_used,
        }
        if not all(
            (
                lifecycle["health_succeeded"],
                lifecycle["fixture_succeeded"],
                lifecycle["shutdown_succeeded"],
                lifecycle["process_exit_code"] == 0,
                lifecycle["process_stopped"],
                lifecycle["listener_closed"],
                lifecycle["stdout_clean"],
                lifecycle["stderr_clean"],
                lifecycle["separate_process"],
                not lifecycle["forced_termination_used"],
            )
        ):
            raise PythonSidecarCandidateExportError(
                "SIDECAR_CANDIDATE_LIFECYCLE_INCOMPLETE",
                "Python sidecar lifecycle did not complete cleanly.",
            )
        return candidate_result, lifecycle
    except PythonSidecarCandidateExportError:
        raise
    except (PythonSidecarProcessError, PythonSidecarClientError) as exc:
        raise PythonSidecarCandidateExportError(
            "SIDECAR_CANDIDATE_LIFECYCLE_FAILED",
            "Python sidecar candidate lifecycle failed.",
            {"sidecar_code": exc.code},
        ) from exc
    finally:
        sidecar.stop()


def _candidate_known_deviations():
    return [
        {
            "code": code,
            "blocking": False,
            "description": _KNOWN_DEVIATION_DESCRIPTIONS[code],
        }
        for code in _KNOWN_DEVIATION_CODES
    ]


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


def _validation_summary(validation):
    artifact_results = validation.get("artifact_results") or []
    canonical_integrity_count = sum(
        item.get("path") in CANONICAL_ARTIFACT_PATHS and item.get("integrity_valid") is True
        for item in artifact_results
    )
    summary = validation.get("summary") or {}
    return {
        "valid": validation.get("valid") is True,
        "error_count": summary.get("error_count", 0),
        "warning_count": summary.get("warning_count", 0),
        "artifact_count_present": summary.get("artifact_count_present", 0),
        "canonical_integrity_valid_count": canonical_integrity_count,
        "semantic_check_count": summary.get("semantic_check_count", 0),
        "semantic_check_failed_count": summary.get("semantic_check_failed_count", 0),
        "warning_codes": sorted({item.get("code", "") for item in validation.get("warnings", [])}),
    }


def _listener_is_closed(host, port):
    try:
        connection = socket.create_connection((host, port), timeout=0.25)
    except OSError:
        return True
    connection.close()
    return False


def _raise_candidate_error(error):
    raise PythonSidecarCandidateExportError(
        error.code,
        error.message,
        error.details,
    ) from error


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise PythonSidecarCandidateExportError(
            "SIDECAR_CANDIDATE_CLI_INVALID",
            "Python sidecar candidate exporter CLI arguments are invalid.",
            category="technical",
        )


def _build_parser():
    parser = _ArgumentParser(description="Export a validated Python sidecar candidate package.")
    parser.add_argument("--fixture", required=True, help="Fixture-root-relative fixture.json path.")
    parser.add_argument("--output", required=True, help="Candidate output directory to create.")
    parser.add_argument("--replace", action="store_true", help="Replace only the explicit output directory.")
    return parser


def main(argv=None):
    try:
        arguments = _build_parser().parse_args(argv)
        result = export_python_sidecar_candidate_artifacts(
            arguments.fixture,
            arguments.output,
            replace=arguments.replace,
        )
    except PythonSidecarCandidateExportError as exc:
        print("%s: %s" % (exc.code, exc.message), file=sys.stderr)
        return 2 if exc.category == "technical" else 1
    except (OSError, ValueError):
        print(
            "SIDECAR_CANDIDATE_TECHNICAL_ERROR: Candidate export could not run.",
            file=sys.stderr,
        )
        return 2
    sys.stdout.write(canonical_json_bytes(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CANDIDATE_EXPORT_CONTRACT_TYPE",
    "CANDIDATE_EXPORT_SCHEMA_VERSION",
    "FIXTURE_REQUEST_PATH",
    "FIXTURE_ROOT",
    "PythonSidecarCandidateExportError",
    "RUNTIME_CANDIDATE",
    "export_python_sidecar_candidate_artifacts",
    "main",
]
