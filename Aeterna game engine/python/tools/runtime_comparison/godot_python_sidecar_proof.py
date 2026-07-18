"""Independent Godot-to-Python sidecar raw-byte integration proof."""

from __future__ import annotations

import argparse
import base64
import binascii
import ctypes
import json
import os
import socket
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

from tools.runtime_comparison.canonical_json import canonical_json_bytes, sha256_bytes
from tools.runtime_comparison.python_reference_fixture import (
    RuntimeComparisonFixtureError,
    run_python_reference_fixture,
)
from tools.runtime_comparison.python_sidecar_server import (
    DEFAULT_FIXTURE_ROOT,
    resolve_fixture_path,
)
from tools.runtime_comparison.sidecar_protocol import (
    PROTOCOL_VERSION,
    SidecarProtocolError,
    validate_response,
    validate_startup_handshake,
)


PROOF_PREFIX = "AETERNA_GODOT_PYTHON_SIDECAR_PROOF_V1="
PROOF_SCHEMA_VERSION = "aeterna-godot-python-sidecar-proof-v1"
RESULT_SCHEMA_VERSION = "aeterna-godot-python-sidecar-proof-result-v1"
FIXTURE_REQUEST_PATH = "minimal_draw_end_turn_v1/fixture.json"
EXPECTED_RESULT_SHA256 = "650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d"

PYTHON_PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENGINE_ROOT = PYTHON_PROJECT_ROOT.parent
REPOSITORY_ROOT = ENGINE_ROOT.parent
GODOT_PROJECT_ROOT = ENGINE_ROOT / "Godot"
TEMP_ROOT = REPOSITORY_ROOT / "TEMP"
GODOT_PROOF_SCRIPT = "res://scripts/debug/python_sidecar_integration_smoke_test.gd"

_REQUIRED_PROOF_FIELDS = {
    "schema_version",
    "success",
    "protocol_version",
    "python_executable",
    "godot_pid",
    "sidecar_pid",
    "host",
    "port",
    "startup_ok",
    "startup_raw_text",
    "port_projection",
    "pythonpath_restored",
    "bytecode_environment_restored",
    "tcp_connected",
    "health_ok",
    "fixture_ok",
    "shutdown_ok",
    "process_stopped",
    "listener_check_requested",
    "listener_closed",
    "sidecar_exit_code",
    "stdout_remainder_empty",
    "stderr_empty",
    "forced_kill_used",
    "raw_fixture_response_body_base64",
    "raw_fixture_response_body_sha256",
    "raw_fixture_response_body_bytes",
    "raw_fixture_text_equal",
    "raw_fixture_bytes_equal",
    "raw_fixture_base64_roundtrip_equal",
    "failure_stage",
    "diagnostic_codes",
}
_BOOLEAN_PROOF_FIELDS = {
    "success",
    "startup_ok",
    "pythonpath_restored",
    "bytecode_environment_restored",
    "tcp_connected",
    "health_ok",
    "fixture_ok",
    "shutdown_ok",
    "process_stopped",
    "listener_check_requested",
    "listener_closed",
    "stdout_remainder_empty",
    "stderr_empty",
    "forced_kill_used",
    "raw_fixture_text_equal",
    "raw_fixture_bytes_equal",
    "raw_fixture_base64_roundtrip_equal",
}


class GodotPythonSidecarProofError(Exception):
    """Stable proof failure without leaking subprocess implementation details."""

    def __init__(self, code, message):
        self.code = str(code)
        self.message = str(message)
        super().__init__("%s: %s" % (self.code, self.message))


def run_godot_python_sidecar_proof(
    godot_executable,
    fixture_path=FIXTURE_REQUEST_PATH,
    *,
    timeout=30.0,
    diagnostics_directory=None,
    run_label="proof_run",
):
    """Run direct Python and Godot-launched sidecar paths, then compare bytes."""

    executable = _validate_godot_executable(godot_executable)
    fixture_request_path, resolved_fixture = _resolve_fixture(fixture_path)
    timeout = _positive_timeout(timeout)
    reference_result = run_python_reference_fixture(resolved_fixture)
    reference_bytes = canonical_json_bytes(reference_result)
    reference_sha256 = sha256_bytes(reference_bytes)

    if diagnostics_directory is None:
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="godot_python_sidecar_proof_",
            dir=TEMP_ROOT,
        ) as temporary:
            return _run_proof_process(
                executable,
                fixture_request_path,
                reference_result,
                reference_bytes,
                reference_sha256,
                timeout,
                Path(temporary),
                run_label,
                preserve_diagnostics=False,
            )

    diagnostics = Path(diagnostics_directory).resolve()
    diagnostics.mkdir(parents=True, exist_ok=True)
    return _run_proof_process(
        executable,
        fixture_request_path,
        reference_result,
        reference_bytes,
        reference_sha256,
        timeout,
        diagnostics,
        run_label,
        preserve_diagnostics=True,
    )


def validate_godot_proof_metadata(proof):
    """Validate the lossless metadata envelope emitted by the Godot process."""

    if not isinstance(proof, dict) or not _REQUIRED_PROOF_FIELDS.issubset(proof):
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_SHAPE_INVALID",
            "Godot sidecar proof fields are incomplete.",
        )
    for key, value in proof.items():
        if isinstance(value, bool) or isinstance(value, str):
            continue
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            continue
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_VALUE_INVALID",
            "Godot sidecar proof contains a non-lossless metadata value.",
        )
    if proof["schema_version"] != PROOF_SCHEMA_VERSION:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_SCHEMA_UNSUPPORTED",
            "Godot sidecar proof schema is unsupported.",
        )
    if proof["protocol_version"] != PROTOCOL_VERSION:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_PROTOCOL_MISMATCH",
            "Godot sidecar proof protocol does not match Python.",
        )
    for field in _BOOLEAN_PROOF_FIELDS:
        if type(proof[field]) is not bool:
            raise GodotPythonSidecarProofError(
                "GODOT_SIDECAR_PROOF_VALUE_INVALID",
                "Godot sidecar proof boolean metadata is invalid.",
            )
    if not isinstance(proof["diagnostic_codes"], list) or any(
        not isinstance(item, str) for item in proof["diagnostic_codes"]
    ):
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_DIAGNOSTICS_INVALID",
            "Godot sidecar proof diagnostic_codes is invalid.",
        )
    return proof


def decode_raw_fixture_response(proof):
    """Decode and validate the exact fixture response body carried by proof."""

    validate_godot_proof_metadata(proof)
    try:
        raw_body = base64.b64decode(
            proof["raw_fixture_response_body_base64"],
            validate=True,
        )
    except (binascii.Error, ValueError):
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_RAW_BODY_BASE64_INVALID",
            "Godot fixture response body is not valid Base64.",
        ) from None
    if not raw_body:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_RAW_BODY_EMPTY",
            "Godot fixture response body is empty.",
        )
    if len(raw_body) != _positive_int_string(
        proof["raw_fixture_response_body_bytes"],
        "raw_fixture_response_body_bytes",
    ):
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_RAW_BODY_LENGTH_MISMATCH",
            "Godot fixture response byte count does not match the decoded body.",
        )
    if sha256_bytes(raw_body) != proof["raw_fixture_response_body_sha256"]:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_RAW_BODY_HASH_MISMATCH",
            "Godot fixture response SHA-256 does not match the decoded body.",
        )
    try:
        raw_text = raw_body.decode("utf-8", errors="strict")
        response = json.loads(raw_text)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_RAW_BODY_JSON_INVALID",
            "Godot fixture response body is not strict UTF-8 JSON.",
        ) from None
    try:
        validate_response(
            response,
            expected_request_id="godot_req_0002_fixture",
            expected_command="run_runtime_comparison_fixture",
        )
    except SidecarProtocolError as exc:
        raise GodotPythonSidecarProofError(exc.code, exc.message) from None
    return raw_body, response


def _run_proof_process(
    executable,
    fixture_request_path,
    reference_result,
    reference_bytes,
    reference_sha256,
    timeout,
    diagnostics,
    run_label,
    *,
    preserve_diagnostics,
):
    label = _safe_run_label(run_label)
    godot_log = diagnostics / (label + "_godot.log")
    command = [
        str(executable),
        "--headless",
        "--path",
        str(GODOT_PROJECT_ROOT),
        "--log-file",
        str(godot_log),
        "--script",
        GODOT_PROOF_SCRIPT,
        "--",
        "--fixture=" + fixture_request_path,
    ]
    environment = os.environ.copy()
    environment["AETERNA_PYTHON_EXECUTABLE"] = str(Path(sys.executable).resolve())
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    process = subprocess.Popen(
        command,
        cwd=GODOT_PROJECT_ROOT,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=creationflags,
    )
    timed_out = False
    try:
        stdout_bytes, stderr_bytes = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        _terminate_process_tree(process)
        stdout_bytes, stderr_bytes = process.communicate(timeout=5)

    if preserve_diagnostics:
        _write_bytes(diagnostics / (label + "_stdout.txt"), stdout_bytes)
        _write_bytes(diagnostics / (label + "_stderr.txt"), stderr_bytes)
        _write_text(
            diagnostics / "commands.txt",
            (diagnostics / "commands.txt").read_text(encoding="utf-8")
            + subprocess.list2cmdline(command)
            + "\n"
            if (diagnostics / "commands.txt").exists()
            else subprocess.list2cmdline(command) + "\n",
        )

    if timed_out:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_TIMEOUT",
            "Godot sidecar proof process timed out.",
        )
    try:
        stdout_text = stdout_bytes.decode("utf-8", errors="strict")
        stderr_text = stderr_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_OUTPUT_UTF8_INVALID",
            "Godot proof output is not valid UTF-8.",
        ) from None

    proof_lines = [
        line
        for line in stdout_text.splitlines()
        if line.startswith(PROOF_PREFIX)
    ]
    if len(proof_lines) != 1:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_LINE_INVALID",
            "Godot output must contain exactly one sidecar proof line.",
        )
    try:
        proof_text = base64.b64decode(
            proof_lines[0][len(PROOF_PREFIX) :],
            validate=True,
        ).decode("utf-8", errors="strict")
        proof = json.loads(proof_text)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_PAYLOAD_INVALID",
            "Godot sidecar proof payload is not valid Base64 UTF-8 JSON.",
        ) from None
    validate_godot_proof_metadata(proof)

    startup = _parse_startup_text(proof["startup_raw_text"])
    godot_pid = _positive_int_string(proof["godot_pid"], "godot_pid")
    sidecar_pid = _positive_int_string(proof["sidecar_pid"], "sidecar_pid")
    port = _positive_int_string(proof["port"], "port")
    sidecar_exit_code = _integer_string(proof["sidecar_exit_code"], "sidecar_exit_code")
    raw_body, response = decode_raw_fixture_response(proof)
    candidate_result = response["result"]
    candidate_bytes = canonical_json_bytes(candidate_result)
    candidate_sha256 = sha256_bytes(candidate_bytes)
    dictionary_equal = candidate_result == reference_result
    canonical_bytes_equal = candidate_bytes == reference_bytes
    listener_closed = _listener_is_closed("127.0.0.1", port)
    sidecar_process_stopped = not _process_is_running(sidecar_pid)
    process_boundary = (
        process.pid == godot_pid
        and len({os.getpid(), godot_pid, sidecar_pid}) == 3
    )

    checks = {
        "godot_exit_zero": process.returncode == 0,
        "godot_stderr_empty": stderr_text == "",
        "godot_proof_success": proof["success"] is True,
        "startup_valid": startup["port"] == port,
        "python_executable_equal": _same_path(
            proof["python_executable"],
            sys.executable,
        ),
        "transport_lifecycle_complete": all(
            proof[field] is True
            for field in (
                "startup_ok",
                "pythonpath_restored",
                "bytecode_environment_restored",
                "tcp_connected",
                "health_ok",
                "fixture_ok",
                "shutdown_ok",
                "process_stopped",
                "listener_check_requested",
                "listener_closed",
                "stdout_remainder_empty",
                "stderr_empty",
                "raw_fixture_text_equal",
                "raw_fixture_bytes_equal",
                "raw_fixture_base64_roundtrip_equal",
            )
        ) and proof["forced_kill_used"] is False,
        "sidecar_exit_zero": sidecar_exit_code == 0,
        "listener_closed_independent": listener_closed,
        "sidecar_process_stopped_independent": sidecar_process_stopped,
        "three_separate_processes": process_boundary,
        "dictionary_equal": dictionary_equal,
        "canonical_bytes_equal": canonical_bytes_equal,
        "result_sha_equal": reference_sha256 == candidate_sha256,
        "expected_result_sha": reference_sha256 == EXPECTED_RESULT_SHA256,
    }
    diagnostic_codes = [
        "GODOT_SIDECAR_" + name.upper() + "_FAILED"
        for name, passed in checks.items()
        if not passed
    ]
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "success": not diagnostic_codes,
        "fixture_path": fixture_request_path,
        "protocol_version": PROTOCOL_VERSION,
        "reference_sha256": reference_sha256,
        "candidate_sha256": candidate_sha256,
        "expected_result_sha256": EXPECTED_RESULT_SHA256,
        "dictionary_equal": dictionary_equal,
        "canonical_bytes_equal": canonical_bytes_equal,
        "raw_fixture_response_body_base64": base64.b64encode(raw_body).decode("ascii"),
        "raw_fixture_response_body_bytes": len(raw_body),
        "raw_fixture_response_body_sha256": sha256_bytes(raw_body),
        "processes": {
            "harness_pid": os.getpid(),
            "godot_pid": godot_pid,
            "sidecar_pid": sidecar_pid,
            "three_separate_processes": process_boundary,
        },
        "lifecycle": {
            "godot_exit_code": process.returncode,
            "sidecar_exit_code": sidecar_exit_code,
            "godot_stderr_empty": stderr_text == "",
            "sidecar_stdout_remainder_empty": proof["stdout_remainder_empty"],
            "sidecar_stderr_empty": proof["stderr_empty"],
            "forced_kill_used": proof["forced_kill_used"],
            "sidecar_process_stopped": sidecar_process_stopped,
            "listener_closed": listener_closed,
            "host": "127.0.0.1",
            "port": port,
        },
        "raw_preservation": {
            "parsed_text_equal": proof["raw_fixture_text_equal"],
            "utf8_bytes_equal": proof["raw_fixture_bytes_equal"],
            "base64_roundtrip_equal": proof["raw_fixture_base64_roundtrip_equal"],
        },
        "checks": checks,
        "diagnostic_codes": diagnostic_codes,
        "godot_proof_metadata": _proof_metadata_without_raw_body(proof),
    }
    canonical_json_bytes(result)

    if preserve_diagnostics:
        _write_bytes(diagnostics / (label + "_raw_fixture_response_body.bin"), raw_body)
        _write_text(
            diagnostics / (label + "_raw_fixture_response_body.sha256"),
            sha256_bytes(raw_body) + "\n",
        )
        _write_json(
            diagnostics / (label + "_decoded_proof_metadata.json"),
            _proof_metadata_without_raw_body(proof),
        )
        _write_json(
            diagnostics / (label + "_process.json"),
            {
                "command": command,
                "harness_pid": os.getpid(),
                "godot_pid": godot_pid,
                "sidecar_pid": sidecar_pid,
                "godot_exit_code": process.returncode,
                "sidecar_exit_code": sidecar_exit_code,
                "listener_closed": listener_closed,
                "sidecar_process_stopped": sidecar_process_stopped,
            },
        )
        _write_json(diagnostics / (label + "_result_summary.json"), result)
    return result


def _parse_startup_text(text):
    try:
        startup = json.loads(text)
        validate_startup_handshake(startup)
    except (json.JSONDecodeError, SidecarProtocolError):
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_STARTUP_INVALID",
            "Godot proof did not preserve a valid startup handshake.",
        ) from None
    return startup


def _resolve_fixture(fixture_path):
    try:
        resolved = resolve_fixture_path(fixture_path, DEFAULT_FIXTURE_ROOT)
    except SidecarProtocolError as exc:
        raise GodotPythonSidecarProofError(exc.code, exc.message) from None
    relative = resolved.relative_to(DEFAULT_FIXTURE_ROOT.resolve()).as_posix()
    return relative, resolved


def _validate_godot_executable(value):
    try:
        path = Path(value).resolve(strict=True)
    except (OSError, TypeError, ValueError):
        raise GodotPythonSidecarProofError(
            "GODOT_EXECUTABLE_INVALID",
            "Godot executable must be an existing file.",
        ) from None
    if not path.is_file():
        raise GodotPythonSidecarProofError(
            "GODOT_EXECUTABLE_INVALID",
            "Godot executable must be an existing file.",
        )
    return path


def _positive_timeout(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_TIMEOUT_INVALID",
            "Godot proof timeout must be positive.",
        )
    return float(value)


def _positive_int_string(value, name):
    parsed = _integer_string(value, name)
    if parsed <= 0:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_INTEGER_INVALID",
            "%s must be a positive integer string." % name,
        )
    return parsed


def _integer_string(value, name):
    if not isinstance(value, str) or not value or value.strip() != value:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_INTEGER_INVALID",
            "%s must be an integer string." % name,
        )
    try:
        parsed = int(value, 10)
    except ValueError:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_INTEGER_INVALID",
            "%s must be an integer string." % name,
        ) from None
    if str(parsed) != value:
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_INTEGER_INVALID",
            "%s must use canonical decimal notation." % name,
        )
    return parsed


def _listener_is_closed(host, port):
    for _attempt in range(5):
        try:
            connection = socket.create_connection((host, port), timeout=0.2)
        except OSError:
            return True
        connection.close()
    return False


def _process_is_running(pid):
    if os.name == "nt":
        from ctypes import wintypes

        process_query_limited_information = 0x1000
        still_active = 259
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel32.GetExitCodeProcess.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.OpenProcess(process_query_limited_information, False, pid)
        if not handle:
            return False
        try:
            exit_code = wintypes.DWORD()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return False
            return exit_code.value == still_active
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _terminate_process_tree(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    else:
        process.kill()


def _same_path(left, right):
    return os.path.normcase(str(Path(left).resolve())) == os.path.normcase(
        str(Path(right).resolve())
    )


def _proof_metadata_without_raw_body(proof):
    metadata = deepcopy(proof)
    metadata.pop("raw_fixture_response_body_base64", None)
    return metadata


def _safe_run_label(value):
    if not isinstance(value, str) or not value or any(
        character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
        for character in value
    ):
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_RUN_LABEL_INVALID",
            "Godot proof run label is invalid.",
        )
    return value


def _write_bytes(path, value):
    Path(path).write_bytes(value)


def _write_text(path, value):
    Path(path).write_text(value, encoding="utf-8", newline="\n")


def _write_json(path, value):
    _write_bytes(path, canonical_json_bytes(value) + b"\n")


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise GodotPythonSidecarProofError(
            "GODOT_SIDECAR_PROOF_CLI_INVALID",
            "Godot sidecar proof CLI arguments are invalid.",
        )


def _build_parser():
    parser = _ArgumentParser(description="Run the Godot-to-Python sidecar integration proof.")
    parser.add_argument("--godot-executable", required=True)
    parser.add_argument("--fixture", default=FIXTURE_REQUEST_PATH)
    parser.add_argument("--diagnostics-dir")
    parser.add_argument("--run-label", default="proof_run")
    return parser


def main(argv=None):
    try:
        arguments = _build_parser().parse_args(argv)
        result = run_godot_python_sidecar_proof(
            arguments.godot_executable,
            arguments.fixture,
            diagnostics_directory=arguments.diagnostics_dir,
            run_label=arguments.run_label,
        )
    except (
        GodotPythonSidecarProofError,
        RuntimeComparisonFixtureError,
        OSError,
        subprocess.SubprocessError,
    ) as exc:
        code = getattr(exc, "code", "GODOT_SIDECAR_PROOF_TECHNICAL_ERROR")
        message = getattr(exc, "message", "Godot sidecar proof could not run.")
        print("%s: %s" % (code, message), file=sys.stderr)
        return 2
    sys.stdout.write(canonical_json_bytes(result).decode("utf-8"))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "EXPECTED_RESULT_SHA256",
    "FIXTURE_REQUEST_PATH",
    "GodotPythonSidecarProofError",
    "PROOF_PREFIX",
    "decode_raw_fixture_response",
    "main",
    "run_godot_python_sidecar_proof",
    "validate_godot_proof_metadata",
]
