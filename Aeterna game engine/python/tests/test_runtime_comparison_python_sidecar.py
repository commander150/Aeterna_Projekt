import io
import json
import os
import socket
import subprocess
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.runtime_comparison.canonical_json import canonical_json_bytes, sha256_bytes
from tools.runtime_comparison import python_reference_fixture as fixture_runner
from tools.runtime_comparison import python_sidecar_proof as proof_module
from tools.runtime_comparison import python_sidecar_server as server_module
from tools.runtime_comparison.python_sidecar_client import PythonSidecarClientError
from tools.runtime_comparison.python_sidecar_process import PythonSidecarProcess
from tools.runtime_comparison.python_sidecar_proof import (
    PROOF_RESULT_CONTRACT_TYPE,
    PROOF_RESULT_SCHEMA_VERSION,
    run_python_sidecar_fixture_proof,
)
from tools.runtime_comparison.sidecar_protocol import (
    PROTOCOL_VERSION,
    REQUEST_SCHEMA_VERSION,
    RESPONSE_SCHEMA_VERSION,
    SUPPORTED_COMMANDS,
    read_frame,
    send_frame,
    validate_response,
)


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ENGINE_PYTHON_DIR.parent / "runtime_comparison" / "fixtures"
FIXTURE_RELATIVE_PATH = "minimal_draw_end_turn_v1/fixture.json"
FIXTURE_PATH = FIXTURE_ROOT / "minimal_draw_end_turn_v1" / "fixture.json"
CLIENT_MODULE_PATH = (
    ENGINE_PYTHON_DIR
    / "tools"
    / "runtime_comparison"
    / "python_sidecar_client.py"
)


class TestRuntimeComparisonPythonSidecar(unittest.TestCase):
    def test_startup_health_shutdown_and_stdout_contract(self):
        before = _directory_snapshot(FIXTURE_ROOT)
        sidecar = PythonSidecarProcess()

        with sidecar:
            self.assertNotEqual(sidecar.pid, os.getpid())
            self.assertEqual(
                set(sidecar.startup),
                {"schema_version", "status", "protocol_version", "host", "port"},
            )
            self.assertEqual(sidecar.startup["host"], "127.0.0.1")
            self.assertTrue(1 <= sidecar.startup["port"] <= 65535)

            health = sidecar.client.health("health_startup_test")
            self.assertEqual(health["request_id"], "health_startup_test")
            self.assertEqual(health["command"], "health")
            self.assertTrue(health["ok"])
            self.assertEqual(health["result"]["status"], "ready")
            self.assertEqual(health["result"]["protocol_version"], PROTOCOL_VERSION)
            self.assertEqual(
                health["result"]["supported_commands"],
                list(SUPPORTED_COMMANDS),
            )
            self.assertEqual(
                health["result"]["supported_request_schema"],
                REQUEST_SCHEMA_VERSION,
            )
            self.assertEqual(
                health["result"]["supported_response_schema"],
                RESPONSE_SCHEMA_VERSION,
            )
            self.assertEqual(
                health["result"]["runtime_candidate"],
                "python_sidecar_headless",
            )
            self.assertFalse(
                {"pid", "port", "timestamp", "path"}
                & _nested_keys(health["result"])
            )
            port = sidecar.port
            shutdown = sidecar.shutdown("shutdown_startup_test")
            self.assertEqual(shutdown["result"], {"status": "shutting_down"})

        self.assertEqual(sidecar.exit_code, 0)
        self.assertFalse(sidecar.is_alive)
        self.assertTrue(sidecar.shutdown_succeeded)
        self.assertEqual(sidecar.stdout_remainder, "")
        self.assertEqual(sidecar.stderr_text, "")
        self.assertTrue(_listener_is_closed(port))
        self.assertEqual(before, _directory_snapshot(FIXTURE_ROOT))

    def test_fixture_result_matches_direct_reference_without_transport_metadata(self):
        before = _directory_snapshot(FIXTURE_ROOT)
        reference = fixture_runner.run_python_reference_fixture(FIXTURE_PATH)

        with PythonSidecarProcess() as sidecar:
            sidecar.client.health("fixture_health")
            response = sidecar.client.run_runtime_comparison_fixture(
                "fixture_run",
                FIXTURE_RELATIVE_PATH,
            )
            candidate = response["result"]
            sidecar.shutdown("fixture_shutdown")

        self.assertEqual(candidate, reference)
        self.assertEqual(canonical_json_bytes(candidate), canonical_json_bytes(reference))
        self.assertEqual(
            sha256_bytes(canonical_json_bytes(candidate)),
            sha256_bytes(canonical_json_bytes(reference)),
        )
        for key in (
            "legal_action_checkpoints",
            "events",
            "snapshot_player_1",
            "snapshot_player_2",
            "final_canonical_state",
        ):
            self.assertEqual(candidate[key], reference[key])
        self.assertFalse(
            {"pid", "port", "timestamp", "protocol_version"}
            & _nested_keys(candidate)
        )
        self.assertEqual(before, _directory_snapshot(FIXTURE_ROOT))

    def test_duplicate_request_and_fixture_path_failures_are_stable(self):
        sidecar = PythonSidecarProcess()
        with sidecar:
            sidecar.client.health("reused_request")
            with self.assertRaises(PythonSidecarClientError) as duplicate:
                sidecar.client.health("reused_request")
            self.assertEqual(duplicate.exception.code, "SIDECAR_REQUEST_ID_REUSED")

            cases = (
                ("absolute", "C:/fixture.json", "SIDECAR_FIXTURE_PATH_INVALID"),
                ("posix_absolute", "/fixture.json", "SIDECAR_FIXTURE_PATH_INVALID"),
                ("traversal", "../fixture.json", "SIDECAR_FIXTURE_PATH_INVALID"),
                ("unknown", "missing/fixture.json", "SIDECAR_FIXTURE_NOT_FOUND"),
            )
            for request_id, fixture_path, code in cases:
                with self.subTest(code=code):
                    with self.assertRaises(PythonSidecarClientError) as raised:
                        sidecar.client.run_runtime_comparison_fixture(
                            request_id,
                            fixture_path,
                        )
                    self.assertEqual(raised.exception.code, code)
                    self.assertNotIn("Traceback", raised.exception.message)
            sidecar.shutdown("path_error_shutdown")

        self.assertEqual(sidecar.stderr_text, "")

    def test_health_dispatch_does_not_call_fixture_runner(self):
        request = {
            "schema_version": REQUEST_SCHEMA_VERSION,
            "protocol_version": PROTOCOL_VERSION,
            "request_id": "health_no_fixture",
            "command": "health",
            "payload": {},
        }
        with patch.object(server_module, "run_python_reference_fixture") as runner:
            response, should_shutdown = server_module._dispatch_request(
                request,
                FIXTURE_ROOT,
            )

        runner.assert_not_called()
        self.assertTrue(response["ok"])
        self.assertFalse(should_shutdown)

    def test_raw_request_validation_and_unknown_command_return_error_envelopes(self):
        sidecar = PythonSidecarProcess()
        with sidecar:
            connection = sidecar.client._connection
            base = {
                "schema_version": REQUEST_SCHEMA_VERSION,
                "protocol_version": PROTOCOL_VERSION,
                "request_id": "raw_request",
                "command": "health",
                "payload": {},
            }
            cases = []
            bad_protocol = dict(base, request_id="bad_protocol", protocol_version="wrong")
            cases.append((bad_protocol, "SIDECAR_PROTOCOL_VERSION_UNSUPPORTED", "bad_protocol", "health"))
            bad_schema = dict(base, request_id="bad_schema", schema_version="wrong")
            cases.append((bad_schema, "SIDECAR_REQUEST_SCHEMA_UNSUPPORTED", "bad_schema", "health"))
            missing_id = dict(base)
            del missing_id["request_id"]
            cases.append((missing_id, "SIDECAR_REQUEST_SHAPE_INVALID", "", "health"))
            bad_payload = dict(base, request_id="bad_payload", payload=[])
            cases.append((bad_payload, "SIDECAR_PAYLOAD_INVALID", "bad_payload", "health"))
            unknown_command = dict(base, request_id="unknown_command", command="execute_module")
            cases.append((unknown_command, "SIDECAR_COMMAND_UNSUPPORTED", "unknown_command", "execute_module"))

            for request, code, response_id, response_command in cases:
                with self.subTest(code=code):
                    send_frame(connection, request)
                    response = read_frame(connection)
                    validate_response(
                        response,
                        expected_request_id=response_id,
                        expected_command=response_command,
                    )
                    self.assertFalse(response["ok"])
                    self.assertEqual(response["error"]["code"], code)
            sidecar.shutdown("raw_validation_shutdown")

        self.assertEqual(sidecar.stderr_text, "")

    def test_client_has_no_engine_import_and_parent_monkeypatch_does_not_reach_child(self):
        source = CLIENT_MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("python_reference_fixture", source)
        self.assertNotIn("MinimalEngineSession", source)
        self.assertNotIn("tools.ai_vs_ai", source)

        with patch.object(
            fixture_runner,
            "run_python_reference_fixture",
            side_effect=AssertionError("parent fixture runner must not be called"),
        ):
            with PythonSidecarProcess() as sidecar:
                self.assertNotEqual(sidecar.pid, os.getpid())
                response = sidecar.client.run_runtime_comparison_fixture(
                    "isolated_fixture",
                    FIXTURE_RELATIVE_PATH,
                )
                self.assertTrue(response["result"]["run_summary"]["completed"])
                sidecar.shutdown("isolated_shutdown")

    def test_public_proof_is_deterministic_across_two_new_processes(self):
        before = _directory_snapshot(FIXTURE_ROOT)

        first = run_python_sidecar_fixture_proof(FIXTURE_RELATIVE_PATH)
        second = run_python_sidecar_fixture_proof(FIXTURE_RELATIVE_PATH)

        self.assertEqual(first, second)
        self.assertEqual(canonical_json_bytes(first), canonical_json_bytes(second))
        self.assertEqual(
            sha256_bytes(canonical_json_bytes(first)),
            sha256_bytes(canonical_json_bytes(second)),
        )
        self.assertTrue(first["success"])
        self.assertTrue(first["semantic_match"])
        self.assertTrue(first["canonical_match"])
        self.assertEqual(first["reference_sha256"], first["candidate_sha256"])
        self.assertTrue(first["process_boundary"]["separate_process"])
        self.assertEqual(first["diagnostics"], [])
        self.assertFalse({"pid", "port", "timestamp"} & _nested_keys(first))
        serialized = canonical_json_bytes(first).decode("utf-8")
        self.assertNotIn(str(ENGINE_PYTHON_DIR.parent), serialized)
        self.assertEqual(before, _directory_snapshot(FIXTURE_ROOT))

    def test_context_manager_exception_and_forced_stop_leave_no_process_or_port(self):
        graceful = PythonSidecarProcess()
        with self.assertRaisesRegex(RuntimeError, "synthetic"):
            with graceful:
                graceful_port = graceful.port
                raise RuntimeError("synthetic")
        self.assertFalse(graceful.is_alive)
        self.assertEqual(graceful.exit_code, 0)
        self.assertTrue(graceful.shutdown_succeeded)
        self.assertTrue(_listener_is_closed(graceful_port))

        forced = PythonSidecarProcess()
        forced.start()
        forced_port = forced.port
        forced.client.close()
        forced.stop()
        self.assertFalse(forced.is_alive)
        self.assertTrue(forced.terminate_used)
        self.assertTrue(_listener_is_closed(forced_port))

    def test_kill_fallback_is_explicitly_implemented(self):
        sidecar = PythonSidecarProcess(shutdown_timeout=0.01)
        fake_process = _KillFallbackProcess()
        sidecar.process = fake_process

        sidecar._force_stop()

        self.assertTrue(sidecar.terminate_used)
        self.assertTrue(sidecar.kill_used)
        self.assertTrue(fake_process.terminated)
        self.assertTrue(fake_process.killed)

    def test_server_cli_rejects_non_loopback_hosts_and_invalid_ports(self):
        cases = (
            (["--host", "localhost", "--port", "0"], "SIDECAR_HOST_NOT_ALLOWED"),
            (["--host", "0.0.0.0", "--port", "0"], "SIDECAR_HOST_NOT_ALLOWED"),
            (["--host", "::", "--port", "0"], "SIDECAR_HOST_NOT_ALLOWED"),
            (["--host", "127.0.0.1", "--port", "65536"], "SIDECAR_PORT_INVALID"),
            (["--host", "127.0.0.1", "--port", "invalid"], "SIDECAR_SERVER_CLI_INVALID"),
        )
        for argv, code in cases:
            with self.subTest(code=code):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    exit_code = server_module.main(argv)
                self.assertEqual(exit_code, 2)
                self.assertEqual(stdout.getvalue(), "")
                self.assertIn(code, stderr.getvalue())
                self.assertNotIn("Traceback", stderr.getvalue())

    def test_proof_cli_exit_codes_and_canonical_stdout(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = proof_module.main(["--fixture", FIXTURE_RELATIVE_PATH])
        result = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertTrue(result["success"])
        self.assertEqual(result["schema_version"], PROOF_RESULT_SCHEMA_VERSION)
        self.assertEqual(result["contract_type"], PROOF_RESULT_CONTRACT_TYPE)
        self.assertEqual(stdout.getvalue().encode("utf-8"), canonical_json_bytes(result))

        mismatch = {"success": False, "diagnostics": [{"code": "MISMATCH"}]}
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.object(proof_module, "run_python_sidecar_fixture_proof", return_value=mismatch):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = proof_module.main(["--fixture", FIXTURE_RELATIVE_PATH])
        self.assertEqual(exit_code, 1)
        self.assertEqual(json.loads(stdout.getvalue()), mismatch)
        self.assertEqual(stderr.getvalue(), "")

        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = proof_module.main(["--fixture", "C:/fixture.json"])
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("SIDECAR_FIXTURE_PATH_INVALID", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())


def _directory_snapshot(root):
    return {
        path.relative_to(root).as_posix(): {
            "bytes": path.read_bytes(),
            "mtime_ns": path.stat().st_mtime_ns,
        }
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _nested_keys(value):
    keys = set()
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(key)
            keys.update(_nested_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(_nested_keys(item))
    return keys


def _listener_is_closed(port):
    try:
        connection = socket.create_connection(("127.0.0.1", port), timeout=0.25)
    except OSError:
        return True
    connection.close()
    return False


class _KillFallbackProcess:
    def __init__(self):
        self.returncode = None
        self.terminated = False
        self.killed = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True

    def kill(self):
        self.killed = True
        self.returncode = 0

    def wait(self, timeout=None):
        if self.returncode is None:
            raise subprocess.TimeoutExpired("sidecar", timeout)
        return self.returncode


if __name__ == "__main__":
    unittest.main()
