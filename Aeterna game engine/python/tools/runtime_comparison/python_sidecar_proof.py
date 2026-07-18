"""Deterministic in-memory direct-reference versus sidecar fixture proof."""

from __future__ import annotations

import argparse
import os
import socket
import sys

from tools.runtime_comparison.canonical_json import canonical_json_bytes, sha256_bytes
from tools.runtime_comparison.python_reference_fixture import (
    RuntimeComparisonFixtureError,
    run_python_reference_fixture,
)
from tools.runtime_comparison.python_sidecar_client import PythonSidecarClientError
from tools.runtime_comparison.python_sidecar_process import (
    PythonSidecarProcess,
    PythonSidecarProcessError,
)
from tools.runtime_comparison.python_sidecar_server import (
    DEFAULT_FIXTURE_ROOT,
    RUNTIME_CANDIDATE,
    resolve_fixture_path,
)
from tools.runtime_comparison.sidecar_protocol import (
    MAX_FRAME_SIZE,
    PROTOCOL_VERSION,
    SidecarProtocolError,
)


PROOF_RESULT_SCHEMA_VERSION = "aeterna-python-sidecar-proof-result-v1"
PROOF_RESULT_CONTRACT_TYPE = "python_sidecar_fixture_proof_result"
FIXTURE_REQUEST_PATH = "minimal_draw_end_turn_v1/fixture.json"


class PythonSidecarProofError(Exception):
    def __init__(self, code, message):
        self.code = str(code)
        self.message = str(message)
        super().__init__("%s: %s" % (self.code, self.message))


def run_python_sidecar_fixture_proof(fixture_path):
    """Run the same fixture directly and through a separate sidecar process."""

    try:
        resolved_fixture = resolve_fixture_path(fixture_path, DEFAULT_FIXTURE_ROOT)
    except SidecarProtocolError as exc:
        raise PythonSidecarProofError(exc.code, exc.message) from None

    reference_result = run_python_reference_fixture(resolved_fixture)
    reference_bytes = canonical_json_bytes(reference_result)
    reference_sha256 = sha256_bytes(reference_bytes)

    with PythonSidecarProcess() as sidecar:
        separate_process = sidecar.pid != os.getpid()
        health_response = sidecar.client.health("sidecar_req_0001_health")
        fixture_response = sidecar.client.run_runtime_comparison_fixture(
            "sidecar_req_0002_fixture",
            str(fixture_path),
        )
        candidate_result = fixture_response["result"]
        candidate_bytes = canonical_json_bytes(candidate_result)
        candidate_sha256 = sha256_bytes(candidate_bytes)
        semantic_match = reference_result == candidate_result
        canonical_match = reference_bytes == candidate_bytes
        shutdown_response = sidecar.shutdown("sidecar_req_0003_shutdown")
        process_exit_code = sidecar.exit_code
        process_stopped = not sidecar.is_alive
        stdout_clean = sidecar.stdout_remainder == ""
        stderr_clean = sidecar.stderr_text == ""
        listener_closed = _listener_is_closed(sidecar.host, sidecar.port)

    diagnostics = []
    checks = (
        (separate_process, "SIDECAR_PROCESS_BOUNDARY_FAILED"),
        (health_response["result"].get("status") == "ready", "SIDECAR_HEALTH_FAILED"),
        (semantic_match, "SIDECAR_SEMANTIC_MISMATCH"),
        (canonical_match, "SIDECAR_CANONICAL_MISMATCH"),
        (reference_sha256 == candidate_sha256, "SIDECAR_HASH_MISMATCH"),
        (shutdown_response["result"].get("status") == "shutting_down", "SIDECAR_SHUTDOWN_FAILED"),
        (process_exit_code == 0, "SIDECAR_EXIT_CODE_INVALID"),
        (process_stopped, "SIDECAR_PROCESS_STILL_RUNNING"),
        (listener_closed, "SIDECAR_LISTENER_STILL_OPEN"),
        (stdout_clean, "SIDECAR_STDOUT_NOT_CLEAN"),
        (stderr_clean, "SIDECAR_STDERR_NOT_CLEAN"),
    )
    for passed, code in checks:
        if not passed:
            diagnostics.append(
                {
                    "code": code,
                    "blocking": True,
                    "message": "Python sidecar proof check failed.",
                }
            )

    result = {
        "schema_version": PROOF_RESULT_SCHEMA_VERSION,
        "contract_type": PROOF_RESULT_CONTRACT_TYPE,
        "fixture_id": reference_result["fixture_identity"]["fixture_id"],
        "runtime_candidate": RUNTIME_CANDIDATE,
        "protocol": {
            "protocol_version": PROTOCOL_VERSION,
            "transport": "ipv4_loopback_tcp",
            "framing": "uint32_big_endian_length_prefixed_utf8_json_object",
            "maximum_frame_bytes": MAX_FRAME_SIZE,
        },
        "health_check": {
            "ok": health_response["ok"],
            "result": health_response["result"],
        },
        "fixture_check": {
            "ok": fixture_response["ok"],
            "result_schema_version": candidate_result.get("schema_version"),
            "dictionary_equal": semantic_match,
            "canonical_bytes_equal": canonical_match,
        },
        "semantic_match": semantic_match,
        "canonical_match": canonical_match,
        "reference_sha256": reference_sha256,
        "candidate_sha256": candidate_sha256,
        "process_boundary": {"separate_process": separate_process},
        "lifecycle": {
            "startup_succeeded": True,
            "health_succeeded": health_response["ok"],
            "fixture_succeeded": fixture_response["ok"],
            "shutdown_succeeded": shutdown_response["ok"],
            "process_exit_code": process_exit_code,
            "process_stopped": process_stopped,
            "listener_closed": listener_closed,
            "startup_stdout_only": stdout_clean,
            "stderr_empty": stderr_clean,
        },
        "diagnostics": diagnostics,
        "success": not diagnostics,
    }
    canonical_json_bytes(result)
    return result


def _listener_is_closed(host, port):
    try:
        connection = socket.create_connection((host, port), timeout=0.25)
    except OSError:
        return True
    connection.close()
    return False


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise PythonSidecarProofError(
            "SIDECAR_PROOF_CLI_INVALID",
            "Python sidecar proof CLI arguments are invalid.",
        )


def _build_parser():
    parser = _ArgumentParser(
        description="Compare a direct Python fixture run with a loopback sidecar run."
    )
    parser.add_argument("--fixture", required=True, help="Fixture-root-relative fixture.json path.")
    return parser


def main(argv=None):
    try:
        arguments = _build_parser().parse_args(argv)
        result = run_python_sidecar_fixture_proof(arguments.fixture)
    except (
        PythonSidecarProofError,
        PythonSidecarProcessError,
        PythonSidecarClientError,
        RuntimeComparisonFixtureError,
    ) as exc:
        code = getattr(exc, "code", "SIDECAR_PROOF_FAILED")
        message = getattr(exc, "message", "Python sidecar proof could not run.")
        print("%s: %s" % (code, message), file=sys.stderr)
        return 2
    except (OSError, ValueError):
        print(
            "SIDECAR_PROOF_TECHNICAL_ERROR: Python sidecar proof could not run.",
            file=sys.stderr,
        )
        return 2
    sys.stdout.write(canonical_json_bytes(result).decode("utf-8"))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "FIXTURE_REQUEST_PATH",
    "PROOF_RESULT_CONTRACT_TYPE",
    "PROOF_RESULT_SCHEMA_VERSION",
    "PythonSidecarProofError",
    "main",
    "run_python_sidecar_fixture_proof",
]
