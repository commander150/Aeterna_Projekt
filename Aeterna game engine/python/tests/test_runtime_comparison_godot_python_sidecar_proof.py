import os
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from tools.runtime_comparison.canonical_json import canonical_json_bytes, sha256_bytes
from tools.runtime_comparison.godot_python_sidecar_proof import (
    EXPECTED_RESULT_SHA256,
    FIXTURE_REQUEST_PATH,
    GodotPythonSidecarProofError,
    decode_raw_fixture_response,
    run_godot_python_sidecar_proof,
    validate_godot_proof_metadata,
)
from tools.runtime_comparison.sidecar_protocol import validate_response


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
TEMP_ROOT = REPOSITORY_ROOT / "TEMP"
GODOT_EXECUTABLE_ENV = "AETERNA_GODOT_EXECUTABLE"


class TestGodotPythonSidecarProofMetadata(unittest.TestCase):
    def test_metadata_validator_rejects_missing_and_non_lossless_values(self):
        proof = _minimal_metadata_fixture()
        self.assertIs(validate_godot_proof_metadata(proof), proof)

        missing = deepcopy(proof)
        del missing["fixture_ok"]
        with self.assertRaises(GodotPythonSidecarProofError) as raised:
            validate_godot_proof_metadata(missing)
        self.assertEqual(raised.exception.code, "GODOT_SIDECAR_PROOF_SHAPE_INVALID")

        non_lossless = deepcopy(proof)
        non_lossless["port"] = 1234
        with self.assertRaises(GodotPythonSidecarProofError) as raised:
            validate_godot_proof_metadata(non_lossless)
        self.assertEqual(raised.exception.code, "GODOT_SIDECAR_PROOF_VALUE_INVALID")


@unittest.skipUnless(
    os.environ.get(GODOT_EXECUTABLE_ENV),
    "Set AETERNA_GODOT_EXECUTABLE to run the Godot 4.7.1 integration proof.",
)
class TestRuntimeComparisonGodotPythonSidecarProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        cls._temporary = tempfile.TemporaryDirectory(
            prefix="godot_sidecar_integration_test_",
            dir=TEMP_ROOT,
        )
        diagnostics = Path(cls._temporary.name)
        executable = os.environ[GODOT_EXECUTABLE_ENV]
        cls.first = run_godot_python_sidecar_proof(
            executable,
            diagnostics_directory=diagnostics,
            run_label="proof_run_1",
        )
        cls.second = run_godot_python_sidecar_proof(
            executable,
            diagnostics_directory=diagnostics,
            run_label="proof_run_2",
        )

    @classmethod
    def tearDownClass(cls):
        cls._temporary.cleanup()

    def test_raw_body_round_trip_and_fixture_envelope(self):
        proof = dict(
            self.first["godot_proof_metadata"],
            raw_fixture_response_body_base64=self.first[
                "raw_fixture_response_body_base64"
            ],
        )
        raw_body, response = decode_raw_fixture_response(proof)
        self.assertEqual(len(raw_body), self.first["raw_fixture_response_body_bytes"])
        self.assertEqual(
            sha256_bytes(raw_body),
            self.first["raw_fixture_response_body_sha256"],
        )
        validate_response(
            response,
            expected_request_id="godot_req_0002_fixture",
            expected_command="run_runtime_comparison_fixture",
        )
        self.assertTrue(response["ok"])

    def test_reference_candidate_and_canonical_bytes_match(self):
        self.assertTrue(self.first["success"])
        self.assertTrue(self.first["dictionary_equal"])
        self.assertTrue(self.first["canonical_bytes_equal"])
        self.assertEqual(self.first["reference_sha256"], EXPECTED_RESULT_SHA256)
        self.assertEqual(self.first["candidate_sha256"], EXPECTED_RESULT_SHA256)
        self.assertEqual(self.first["diagnostic_codes"], [])

    def test_three_processes_and_graceful_lifecycle_are_independently_checked(self):
        processes = self.first["processes"]
        self.assertEqual(
            len(
                {
                    processes["harness_pid"],
                    processes["godot_pid"],
                    processes["sidecar_pid"],
                }
            ),
            3,
        )
        self.assertTrue(processes["three_separate_processes"])
        lifecycle = self.first["lifecycle"]
        self.assertEqual(lifecycle["godot_exit_code"], 0)
        self.assertEqual(lifecycle["sidecar_exit_code"], 0)
        self.assertTrue(lifecycle["sidecar_process_stopped"])
        self.assertTrue(lifecycle["listener_closed"])
        self.assertTrue(lifecycle["godot_stderr_empty"])
        self.assertTrue(lifecycle["sidecar_stdout_remainder_empty"])
        self.assertTrue(lifecycle["sidecar_stderr_empty"])
        self.assertFalse(lifecycle["forced_kill_used"])
        metadata = self.first["godot_proof_metadata"]
        self.assertTrue(metadata["pythonpath_restored"])
        self.assertTrue(metadata["bytecode_environment_restored"])

    def test_two_real_godot_runs_preserve_identical_candidate_bytes(self):
        self.assertTrue(self.second["success"])
        self.assertEqual(
            self.first["raw_fixture_response_body_base64"],
            self.second["raw_fixture_response_body_base64"],
        )
        self.assertEqual(self.first["candidate_sha256"], self.second["candidate_sha256"])
        self.assertEqual(
            canonical_json_bytes(self.first["raw_preservation"]),
            canonical_json_bytes(self.second["raw_preservation"]),
        )
        self.assertNotEqual(
            self.first["processes"]["godot_pid"],
            self.second["processes"]["godot_pid"],
        )
        self.assertNotEqual(
            self.first["processes"]["sidecar_pid"],
            self.second["processes"]["sidecar_pid"],
        )


def _minimal_metadata_fixture():
    fields = {
        "schema_version": "aeterna-godot-python-sidecar-proof-v1",
        "success": True,
        "protocol_version": "aeterna-python-sidecar-protocol-v1",
        "python_executable": "C:/Python/python.exe",
        "godot_pid": "1",
        "sidecar_pid": "2",
        "host": "127.0.0.1",
        "port": "1234",
        "startup_ok": True,
        "startup_raw_text": "{}",
        "port_projection": "finite_integral_transport_port_to_int",
        "pythonpath_restored": True,
        "bytecode_environment_restored": True,
        "tcp_connected": True,
        "health_ok": True,
        "fixture_ok": True,
        "shutdown_ok": True,
        "process_stopped": True,
        "listener_check_requested": True,
        "listener_closed": True,
        "sidecar_exit_code": "0",
        "stdout_remainder_empty": True,
        "stderr_empty": True,
        "forced_kill_used": False,
        "raw_fixture_response_body_base64": "e30=",
        "raw_fixture_response_body_sha256": "hash",
        "raw_fixture_response_body_bytes": "2",
        "raw_fixture_text_equal": True,
        "raw_fixture_bytes_equal": True,
        "raw_fixture_base64_roundtrip_equal": True,
        "failure_stage": "",
        "diagnostic_codes": [],
    }
    return fields


if __name__ == "__main__":
    unittest.main()
