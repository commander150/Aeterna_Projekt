import io
import json
import secrets
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.runtime_comparison import python_sidecar_candidate_proof as proof_module
from tools.runtime_comparison.canonical_json import canonical_json_bytes, sha256_bytes
from tools.runtime_comparison.python_sidecar_candidate_exporter import (
    PythonSidecarCandidateExportError,
)
from tools.runtime_comparison.python_sidecar_candidate_proof import (
    PROOF_RESULT_CONTRACT_TYPE,
    PROOF_RESULT_SCHEMA_VERSION,
    run_python_sidecar_candidate_artifact_proof,
)


PYTHON_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = PYTHON_DIR.parent
PROJECT_ROOT = ENGINE_DIR.parent
PROJECT_TEMP = PROJECT_ROOT / "TEMP"
FIXTURE_DIR = ENGINE_DIR / "runtime_comparison" / "fixtures" / "minimal_draw_end_turn_v1"
FIXTURE_REQUEST_PATH = "minimal_draw_end_turn_v1/fixture.json"
TRACKED_ORACLE = FIXTURE_DIR / "expected" / "python_reference_v1"


class TestPythonSidecarCandidateProof(unittest.TestCase):
    def setUp(self):
        PROJECT_TEMP.mkdir(parents=True, exist_ok=True)
        self.temp_root = PROJECT_TEMP / (
            "runtime_comparison_sidecar_proof_test_" + secrets.token_hex(8)
        )
        self.temp_root.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_proof_is_successful_deterministic_and_path_safe(self):
        output_a = self.temp_root / "proof_a"
        output_b = self.temp_root / "proof_b"

        first = run_python_sidecar_candidate_artifact_proof(
            FIXTURE_REQUEST_PATH,
            TRACKED_ORACLE,
            output_a,
        )
        second = run_python_sidecar_candidate_artifact_proof(
            FIXTURE_REQUEST_PATH,
            TRACKED_ORACLE,
            output_b,
        )

        self.assertEqual(first, second)
        first_bytes = canonical_json_bytes(first)
        self.assertEqual(first_bytes, canonical_json_bytes(second))
        self.assertEqual(sha256_bytes(first_bytes), sha256_bytes(canonical_json_bytes(second)))
        self.assertEqual(first["schema_version"], PROOF_RESULT_SCHEMA_VERSION)
        self.assertEqual(first["contract_type"], PROOF_RESULT_CONTRACT_TYPE)
        self.assertEqual(first["fixture_id"], "minimal_draw_end_turn_v1")
        self.assertEqual(first["runtime_candidate"], "python_sidecar_headless")
        self.assertEqual(first["transport_protocol"], "aeterna-python-sidecar-protocol-v1")
        self.assertTrue(first["success"])
        self.assertEqual(first["outcome"], "success")
        self.assertEqual(first["diagnostics"], [])
        self.assertEqual(first["canonical_artifact_count"], 9)
        self.assertEqual(first["equal_canonical_artifact_count"], 9)
        self.assertTrue(first["validation"]["valid"])
        self.assertEqual(first["validation"]["artifact_count_present"], 10)
        self.assertEqual(first["validation"]["canonical_integrity_valid_count"], 9)
        self.assertTrue(first["comparison"]["comparable"])
        self.assertTrue(first["comparison"]["semantic_match"])
        self.assertTrue(first["comparison"]["canonical_match"])
        self.assertTrue(first["comparison"]["match"])
        self.assertEqual(first["comparison"]["manifest_status"], "allowed_difference")
        self.assertEqual(
            set(first["comparison"]["allowed_difference_codes"]),
            {
                "RUNTIME_CANDIDATE_DIFFERENCE",
                "BUILD_IDENTIFIER_DIFFERENCE",
                "IMPLEMENTATION_SPECIFIC_DIFFERENCE",
                "DECLARED_KNOWN_DEVIATION_DIFFERENCE",
            },
        )
        forbidden = {"pid", "port", "timestamp", "hostname", "username", "user"}
        self.assertFalse(forbidden & _nested_keys(first))
        serialized = first_bytes.decode("utf-8")
        self.assertNotIn(str(PROJECT_ROOT), serialized)
        self.assertNotIn(str(self.temp_root), serialized)

    def test_proof_cli_exit_codes_are_stable(self):
        output = self.temp_root / "cli_success"
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            success_code = proof_module.main(
                [
                    "--fixture",
                    FIXTURE_REQUEST_PATH,
                    "--reference",
                    str(TRACKED_ORACLE),
                    "--candidate-output",
                    str(output),
                ]
            )
        self.assertEqual(success_code, 0)
        self.assertTrue(json.loads(stdout.getvalue())["success"])
        self.assertEqual(stderr.getvalue(), "")

        mismatch = {
            "success": False,
            "outcome": "comparison_mismatch",
            "diagnostics": [{"code": "SYNTHETIC_MISMATCH"}],
        }
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.object(
            proof_module,
            "run_python_sidecar_candidate_artifact_proof",
            return_value=mismatch,
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            mismatch_code = proof_module.main(
                [
                    "--fixture",
                    FIXTURE_REQUEST_PATH,
                    "--reference",
                    str(TRACKED_ORACLE),
                    "--candidate-output",
                    str(self.temp_root / "mismatch"),
                ]
            )
        self.assertEqual(mismatch_code, 1)
        self.assertEqual(json.loads(stdout.getvalue()), mismatch)
        self.assertEqual(stderr.getvalue(), "")

        stdout = io.StringIO()
        stderr = io.StringIO()
        export_error = PythonSidecarCandidateExportError(
            "SIDECAR_CANDIDATE_VALIDATION_FAILED",
            "Synthetic export failure.",
        )
        with patch.object(
            proof_module,
            "run_python_sidecar_candidate_artifact_proof",
            side_effect=export_error,
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            export_code = proof_module.main(
                [
                    "--fixture",
                    FIXTURE_REQUEST_PATH,
                    "--reference",
                    str(TRACKED_ORACLE),
                    "--candidate-output",
                    str(self.temp_root / "export_failure"),
                ]
            )
        self.assertEqual(export_code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("SIDECAR_CANDIDATE_VALIDATION_FAILED", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            input_code = proof_module.main([])
        self.assertEqual(input_code, 3)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("SIDECAR_CANDIDATE_PROOF_CLI_INVALID", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())


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


if __name__ == "__main__":
    unittest.main()
