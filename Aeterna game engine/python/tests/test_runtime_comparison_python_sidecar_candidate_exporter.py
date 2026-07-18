import io
import json
import os
import secrets
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from tools.runtime_comparison import python_reference_fixture as fixture_runner
from tools.runtime_comparison import python_sidecar_candidate_exporter as exporter
from tools.runtime_comparison import runtime_comparison_artifact_builder as artifact_builder
from tools.runtime_comparison.artifact_comparator import compare_runtime_comparison_artifacts
from tools.runtime_comparison.artifact_validator import validate_runtime_comparison_artifacts
from tools.runtime_comparison.canonical_json import canonical_json_bytes, sha256_bytes
from tools.runtime_comparison.python_sidecar_candidate_exporter import (
    PythonSidecarCandidateExportError,
    export_python_sidecar_candidate_artifacts,
)


PYTHON_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = PYTHON_DIR.parent
PROJECT_ROOT = ENGINE_DIR.parent
PROJECT_TEMP = PROJECT_ROOT / "TEMP"
FIXTURE_DIR = ENGINE_DIR / "runtime_comparison" / "fixtures" / "minimal_draw_end_turn_v1"
FIXTURE_PATH = FIXTURE_DIR / "fixture.json"
FIXTURE_REQUEST_PATH = "minimal_draw_end_turn_v1/fixture.json"
TRACKED_ORACLE = FIXTURE_DIR / "expected" / "python_reference_v1"
TRACKED_CANDIDATE = FIXTURE_DIR / "candidates" / "python_sidecar_headless_v1"
EXPECTED_DEVIATIONS = {
    "no_transport_authentication",
    "no_tls",
    "no_reconnect",
    "no_request_multiplexing",
    "single_client_proof_server",
    "no_os_process_sandbox",
    "no_production_service_installation",
    "no_release_hardening",
}


class TestPythonSidecarCandidateExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid_result, cls.valid_lifecycle = exporter._run_sidecar_fixture(
            FIXTURE_REQUEST_PATH
        )

    def setUp(self):
        PROJECT_TEMP.mkdir(parents=True, exist_ok=True)
        self.temp_root = PROJECT_TEMP / (
            "runtime_comparison_sidecar_candidate_test_" + secrets.token_hex(8)
        )
        self.temp_root.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_complete_candidate_manifest_validation_comparison_and_provenance(self):
        output = self.temp_root / "complete"
        oracle_before = _directory_snapshot(TRACKED_ORACLE)
        original_read_bytes = Path.read_bytes

        def reject_oracle_reads(path):
            if TRACKED_ORACLE in path.parents:
                raise AssertionError("candidate exporter must not read oracle artifact bytes")
            return original_read_bytes(path)

        with patch.object(
            fixture_runner,
            "run_python_reference_fixture",
            side_effect=AssertionError("parent fixture runner must not execute"),
        ), patch.object(Path, "read_bytes", reject_oracle_reads):
            result = export_python_sidecar_candidate_artifacts(FIXTURE_PATH, output)

        self.assertTrue(result["success"])
        self.assertEqual(_file_names(output), sorted(artifact_builder.REQUIRED_OUTPUT_PATHS))
        self.assertEqual(_temporary_siblings(output), [])
        self.assertFalse(
            {"comparison_report.md", "comparison_report.json", "proof_result.json"}
            & set(_file_names(output))
        )
        self._assert_manifest(output)
        self._assert_exact_oracle_artifacts(output)
        self._assert_no_transport_metadata(output)

        validation = validate_runtime_comparison_artifacts(
            output,
            expected_fixture_id="minimal_draw_end_turn_v1",
        )
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["errors"], [])
        self.assertEqual(validation["summary"]["artifact_count_present"], 10)
        self.assertEqual(
            sum(
                item["integrity_valid"]
                for item in validation["artifact_results"]
                if item["path"] in artifact_builder.CANONICAL_ARTIFACT_PATHS
            ),
            9,
        )

        comparison = compare_runtime_comparison_artifacts(
            TRACKED_ORACLE,
            output,
            expected_fixture_id="minimal_draw_end_turn_v1",
        )
        self._assert_oracle_match(comparison)
        self.assertEqual(oracle_before, _directory_snapshot(TRACKED_ORACLE))
        self.assertTrue(result["lifecycle"]["separate_process"])
        self.assertEqual(result["lifecycle"]["process_exit_code"], 0)
        self.assertTrue(result["lifecycle"]["listener_closed"])
        self.assertFalse(result["lifecycle"]["forced_termination_used"])

    def test_two_new_sidecar_exports_are_deterministic(self):
        output_a = self.temp_root / "deterministic_a"
        output_b = self.temp_root / "deterministic_b"

        first = export_python_sidecar_candidate_artifacts(FIXTURE_REQUEST_PATH, output_a)
        second = export_python_sidecar_candidate_artifacts(FIXTURE_REQUEST_PATH, output_b)

        self.assertEqual(first, second)
        self.assertEqual(canonical_json_bytes(first), canonical_json_bytes(second))
        for relative_path in artifact_builder.CANONICAL_ARTIFACT_PATHS:
            self.assertEqual(
                (output_a / relative_path).read_bytes(),
                (output_b / relative_path).read_bytes(),
                relative_path,
            )
        self.assertEqual(
            (output_a / "run_manifest.json").read_bytes(),
            (output_b / "run_manifest.json").read_bytes(),
        )
        self.assertEqual(_temporary_siblings(output_a), [])
        self.assertEqual(_temporary_siblings(output_b), [])

    def test_import_boundary_has_no_engine_fixture_runner_or_reference_exporter(self):
        candidate_source = Path(exporter.__file__).read_text(encoding="utf-8")
        builder_source = Path(artifact_builder.__file__).read_text(encoding="utf-8")
        combined = candidate_source + builder_source

        self.assertNotIn("python_reference_fixture", combined)
        self.assertNotIn("python_reference_exporter", combined)
        self.assertNotIn("MinimalEngineSession", combined)
        self.assertNotIn("tools.ai_vs_ai", combined)
        self.assertNotIn("rules_kernel", combined)

    def test_existing_output_requires_replace_and_replace_preserves_sibling(self):
        output = self.temp_root / "replace_target"
        output.mkdir()
        sentinel = output / "old.txt"
        sentinel.write_text("old", encoding="utf-8")
        sibling = self.temp_root / "sibling.txt"
        sibling.write_text("keep", encoding="utf-8")

        with self.assertRaises(PythonSidecarCandidateExportError) as raised:
            export_python_sidecar_candidate_artifacts(FIXTURE_PATH, output)
        self.assertEqual(raised.exception.code, "output_exists")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "old")

        with patch.object(
            exporter,
            "_run_sidecar_fixture",
            return_value=(deepcopy(self.valid_result), deepcopy(self.valid_lifecycle)),
        ):
            export_python_sidecar_candidate_artifacts(FIXTURE_PATH, output, replace=True)
        self.assertFalse(sentinel.exists())
        self.assertEqual(sibling.read_text(encoding="utf-8"), "keep")
        self.assertEqual(_temporary_siblings(output), [])

    def test_lifecycle_and_invalid_result_failures_leave_no_output(self):
        cases = (
            "SIDECAR_CANDIDATE_STARTUP_FAILED",
            "SIDECAR_CANDIDATE_FIXTURE_FAILED",
            "SIDECAR_CANDIDATE_SHUTDOWN_FAILED",
        )
        for index, code in enumerate(cases):
            output = self.temp_root / ("lifecycle_failure_%s" % index)
            error = PythonSidecarCandidateExportError(code, "Synthetic lifecycle failure.")
            with self.subTest(code=code), patch.object(
                exporter,
                "_run_sidecar_fixture",
                side_effect=error,
            ):
                with self.assertRaises(PythonSidecarCandidateExportError):
                    export_python_sidecar_candidate_artifacts(FIXTURE_PATH, output)
            self.assertFalse(output.exists())
            self.assertEqual(_temporary_siblings(output), [])

        invalid_output = self.temp_root / "invalid_result"
        with patch.object(
            exporter,
            "_run_sidecar_fixture",
            return_value=({}, deepcopy(self.valid_lifecycle)),
        ):
            with self.assertRaises(PythonSidecarCandidateExportError) as raised:
                export_python_sidecar_candidate_artifacts(FIXTURE_PATH, invalid_output)
        self.assertEqual(raised.exception.code, "artifact_contract_invalid")
        self.assertFalse(invalid_output.exists())
        self.assertEqual(_temporary_siblings(invalid_output), [])

    def test_staging_write_and_validator_failures_are_atomic(self):
        valid_run = patch.object(
            exporter,
            "_run_sidecar_fixture",
            return_value=(deepcopy(self.valid_result), deepcopy(self.valid_lifecycle)),
        )
        output = self.temp_root / "write_failure"
        original_write_bytes = Path.write_bytes

        def fail_responses(path, data):
            if path.name == "responses.jsonl":
                raise OSError("synthetic staging write failure")
            return original_write_bytes(path, data)

        with valid_run, patch.object(Path, "write_bytes", fail_responses):
            with self.assertRaises(PythonSidecarCandidateExportError) as raised:
                export_python_sidecar_candidate_artifacts(FIXTURE_PATH, output)
        self.assertEqual(raised.exception.code, "staging_write_failed")
        self.assertFalse(output.exists())
        self.assertEqual(_temporary_siblings(output), [])

        invalid_validation = {
            "valid": False,
            "summary": {"error_count": 1},
            "errors": [{"code": "SYNTHETIC"}],
        }
        output = self.temp_root / "validator_failure"
        with patch.object(
            exporter,
            "_run_sidecar_fixture",
            return_value=(deepcopy(self.valid_result), deepcopy(self.valid_lifecycle)),
        ), patch.object(
            exporter,
            "validate_runtime_comparison_artifacts",
            return_value=invalid_validation,
        ):
            with self.assertRaises(PythonSidecarCandidateExportError) as raised:
                export_python_sidecar_candidate_artifacts(FIXTURE_PATH, output)
        self.assertEqual(raised.exception.code, "candidate_validation_failed")
        self.assertFalse(output.exists())
        self.assertEqual(_temporary_siblings(output), [])

    def test_promotion_failure_restores_existing_target(self):
        output = self.temp_root / "promotion_failure"
        output.mkdir()
        sentinel = output / "old.txt"
        sentinel.write_text("old", encoding="utf-8")
        real_replace = artifact_builder.os.replace

        def fail_staging_promotion(source, destination):
            source_path = Path(source)
            destination_path = Path(destination)
            if ".%s.staging-" % output.name in source_path.name and destination_path == output:
                raise OSError("synthetic promotion failure")
            return real_replace(source, destination)

        with patch.object(
            exporter,
            "_run_sidecar_fixture",
            return_value=(deepcopy(self.valid_result), deepcopy(self.valid_lifecycle)),
        ), patch.object(artifact_builder.os, "replace", fail_staging_promotion):
            with self.assertRaises(PythonSidecarCandidateExportError) as raised:
                export_python_sidecar_candidate_artifacts(FIXTURE_PATH, output, replace=True)

        self.assertEqual(raised.exception.code, "target_replace_failed")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "old")
        self.assertEqual(_temporary_siblings(output), [])

    def test_tracked_candidate_is_valid_read_only_and_matches_fresh_sidecar(self):
        self.assertTrue(TRACKED_CANDIDATE.is_dir())
        tracked_before = _directory_snapshot(TRACKED_CANDIDATE)
        fresh = self.temp_root / "fresh_for_tracked"

        export_python_sidecar_candidate_artifacts(FIXTURE_REQUEST_PATH, fresh)
        validation = validate_runtime_comparison_artifacts(
            TRACKED_CANDIDATE,
            expected_fixture_id="minimal_draw_end_turn_v1",
        )
        comparison = compare_runtime_comparison_artifacts(
            TRACKED_ORACLE,
            TRACKED_CANDIDATE,
            expected_fixture_id="minimal_draw_end_turn_v1",
        )

        self.assertTrue(validation["valid"])
        self._assert_oracle_match(comparison)
        for relative_path in artifact_builder.CANONICAL_ARTIFACT_PATHS:
            self.assertEqual(
                (TRACKED_CANDIDATE / relative_path).read_bytes(),
                (fresh / relative_path).read_bytes(),
                relative_path,
            )
        self.assertEqual(tracked_before, _directory_snapshot(TRACKED_CANDIDATE))

    def test_exporter_cli_exit_codes_are_stable(self):
        output = self.temp_root / "cli_success"
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            success_code = exporter.main(
                ["--fixture", FIXTURE_REQUEST_PATH, "--output", str(output)]
            )
        self.assertEqual(success_code, 0)
        self.assertTrue(json.loads(stdout.getvalue())["success"])
        self.assertEqual(stderr.getvalue(), "")

        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exists_code = exporter.main(
                ["--fixture", FIXTURE_REQUEST_PATH, "--output", str(output)]
            )
        self.assertEqual(exists_code, 1)
        self.assertIn("output_exists", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            input_code = exporter.main(
                ["--fixture", "missing/fixture.json", "--output", str(self.temp_root / "missing")]
            )
        self.assertEqual(input_code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("SIDECAR_CANDIDATE_FIXTURE_INPUT_INVALID", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def _assert_manifest(self, output):
        manifest = _read_json(output / "run_manifest.json")
        self.assertEqual(manifest["schema_version"], "aeterna-runtime-comparison-run-manifest-v1")
        self.assertEqual(manifest["contract_type"], "runtime_comparison_run_manifest")
        self.assertEqual(manifest["oracle_id"], "python_reference")
        self.assertEqual(manifest["oracle_version"], 1)
        self.assertEqual(manifest["runtime_candidate"], "python_sidecar_headless")
        self.assertEqual(manifest["implementation_language"], "python")
        self.assertEqual(
            [item["path"] for item in manifest["canonical_artifacts"]],
            list(artifact_builder.CANONICAL_ARTIFACT_PATHS),
        )
        implementation = manifest["implementation_specific"]
        self.assertEqual(implementation["process_model"], "separate_python_process")
        self.assertEqual(implementation["transport_protocol"], "aeterna-python-sidecar-protocol-v1")
        self.assertEqual(implementation["transport_scope"], "ipv4_loopback")
        self.assertEqual(implementation["frame_prefix_bytes"], 4)
        self.assertEqual(implementation["frame_byte_order"], "big_endian")
        self.assertEqual(implementation["maximum_frame_bytes"], 8388608)
        self.assertEqual(implementation["lifecycle_sequence"], "health_fixture_shutdown")
        deviation_codes = {item["code"] for item in manifest["known_deviations"]}
        self.assertTrue(EXPECTED_DEVIATIONS <= deviation_codes)
        forbidden = {"pid", "port", "timestamp", "hostname", "username", "user"}
        self.assertFalse(forbidden & _nested_keys(manifest))
        self.assertFalse(any(_looks_like_absolute_path(value) for value in _scalar_values(manifest)))

    def _assert_exact_oracle_artifacts(self, output):
        for relative_path in artifact_builder.CANONICAL_ARTIFACT_PATHS:
            candidate_bytes = (output / relative_path).read_bytes()
            oracle_bytes = (TRACKED_ORACLE / relative_path).read_bytes()
            self.assertEqual(candidate_bytes, oracle_bytes, relative_path)
            self.assertEqual(sha256_bytes(candidate_bytes), sha256_bytes(oracle_bytes))

    def _assert_no_transport_metadata(self, output):
        forbidden = {"pid", "port", "protocol_version", "transport_protocol"}
        for relative_path in artifact_builder.CANONICAL_ARTIFACT_PATHS:
            value = _read_artifact(output / relative_path)
            self.assertFalse(forbidden & _nested_keys(value), relative_path)

    def _assert_oracle_match(self, comparison):
        self.assertTrue(comparison["comparable"])
        self.assertTrue(comparison["semantic_match"])
        self.assertTrue(comparison["canonical_match"])
        self.assertTrue(comparison["match"])
        records = {item["path"]: item for item in comparison["artifact_comparisons"]}
        for relative_path in artifact_builder.CANONICAL_ARTIFACT_PATHS:
            self.assertEqual(records[relative_path]["status"], "equal")
            self.assertTrue(records[relative_path]["byte_equal"])
            self.assertTrue(records[relative_path]["semantic_equal"])
        self.assertEqual(records["run_manifest.json"]["status"], "allowed_difference")
        self.assertTrue(
            {
                "RUNTIME_CANDIDATE_DIFFERENCE",
                "BUILD_IDENTIFIER_DIFFERENCE",
                "IMPLEMENTATION_SPECIFIC_DIFFERENCE",
                "DECLARED_KNOWN_DEVIATION_DIFFERENCE",
            }
            <= {item["code"] for item in comparison["allowed_differences"]}
        )


def _file_names(directory):
    return sorted(path.name for path in directory.iterdir() if path.is_file())


def _temporary_siblings(output):
    if not output.parent.exists():
        return []
    prefixes = (".%s.staging-" % output.name, ".%s.backup-" % output.name)
    return sorted(path.name for path in output.parent.iterdir() if path.name.startswith(prefixes))


def _directory_snapshot(root):
    return {
        path.relative_to(root).as_posix(): {
            "bytes": path.read_bytes(),
            "mtime_ns": path.stat().st_mtime_ns,
        }
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_artifact(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines()]
    return json.loads(text)


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


def _scalar_values(value):
    values = []
    if isinstance(value, dict):
        for item in value.values():
            values.extend(_scalar_values(item))
    elif isinstance(value, list):
        for item in value:
            values.extend(_scalar_values(item))
    else:
        values.append(value)
    return values


def _looks_like_absolute_path(value):
    if not isinstance(value, str):
        return False
    return Path(value).is_absolute() or (
        len(value) >= 3
        and value[0].isalpha()
        and value[1] == ":"
        and value[2] in {"/", "\\"}
    )


if __name__ == "__main__":
    unittest.main()
