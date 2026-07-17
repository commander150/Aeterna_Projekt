import io
import json
import secrets
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.runtime_comparison.canonical_json import (
    canonical_json_bytes,
    canonical_jsonl_bytes,
    sha256_bytes,
)
from tools.runtime_comparison import python_reference_exporter as exporter


PYTHON_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = PYTHON_DIR.parent
PROJECT_ROOT = ENGINE_DIR.parent
PROJECT_TEMP = PROJECT_ROOT / "TEMP"
FIXTURE_DIR = ENGINE_DIR / "runtime_comparison" / "fixtures" / "minimal_draw_end_turn_v1"
FIXTURE_PATH = FIXTURE_DIR / "fixture.json"
TRACKED_ORACLE = FIXTURE_DIR / "expected" / "python_reference_v1"


class TestPythonReferenceExporter(unittest.TestCase):
    def setUp(self):
        PROJECT_TEMP.mkdir(parents=True, exist_ok=True)
        self.temp_root = PROJECT_TEMP / (
            "runtime_comparison_exporter_test_" + secrets.token_hex(8)
        )
        self.temp_root.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_exports_exact_complete_canonical_artifact_set_and_manifest(self):
        output = self.temp_root / "complete"

        returned_manifest = exporter.export_python_reference_artifacts(FIXTURE_PATH, output)

        self.assertEqual(_file_names(output), sorted(exporter.REQUIRED_OUTPUT_PATHS))
        self.assertNotIn("comparison_report.md", _file_names(output))
        self.assertNotIn("comparison_report.json", _file_names(output))
        self.assertEqual(returned_manifest, _read_json(output / "run_manifest.json"))
        self.assertEqual(_temporary_siblings(output), [])
        self._assert_canonical_files(output)
        self._assert_manifest(output)
        self._assert_semantics(output)

    def test_two_clean_exports_are_byte_identical(self):
        output_a = self.temp_root / "clean_a"
        output_b = self.temp_root / "clean_b"

        exporter.export_python_reference_artifacts(FIXTURE_PATH, output_a)
        exporter.export_python_reference_artifacts(FIXTURE_PATH, output_b)

        for relative_path in exporter.CANONICAL_ARTIFACT_PATHS:
            self.assertEqual(
                (output_a / relative_path).read_bytes(),
                (output_b / relative_path).read_bytes(),
                relative_path,
            )
        manifest_a = _read_json(output_a / "run_manifest.json")
        manifest_b = _read_json(output_b / "run_manifest.json")
        self.assertEqual(manifest_a["canonical_artifacts"], manifest_b["canonical_artifacts"])
        self.assertEqual(
            (output_a / "run_manifest.json").read_bytes(),
            (output_b / "run_manifest.json").read_bytes(),
        )

    def test_tracked_oracle_matches_a_fresh_export(self):
        self.assertTrue(TRACKED_ORACLE.is_dir())
        fresh = self.temp_root / "fresh"

        exporter.export_python_reference_artifacts(FIXTURE_PATH, fresh)

        self.assertEqual(_file_names(TRACKED_ORACLE), sorted(exporter.REQUIRED_OUTPUT_PATHS))
        for relative_path in exporter.CANONICAL_ARTIFACT_PATHS:
            self.assertEqual(
                (TRACKED_ORACLE / relative_path).read_bytes(),
                (fresh / relative_path).read_bytes(),
                relative_path,
            )
        tracked_manifest = _read_json(TRACKED_ORACLE / "run_manifest.json")
        fresh_manifest = _read_json(fresh / "run_manifest.json")
        self.assertEqual(
            tracked_manifest["canonical_artifacts"],
            fresh_manifest["canonical_artifacts"],
        )
        self._assert_manifest(TRACKED_ORACLE)

    def test_existing_output_requires_replace_and_replace_preserves_sibling(self):
        output = self.temp_root / "replace_target"
        output.mkdir()
        sentinel = output / "old.txt"
        sentinel.write_text("old", encoding="utf-8")
        sibling = self.temp_root / "sibling.txt"
        sibling.write_text("keep", encoding="utf-8")

        with self.assertRaises(exporter.PythonReferenceExportError) as context:
            exporter.export_python_reference_artifacts(FIXTURE_PATH, output)
        self.assertEqual(context.exception.code, "output_exists")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "old")

        exporter.export_python_reference_artifacts(FIXTURE_PATH, output, replace=True)

        self.assertFalse(sentinel.exists())
        self.assertEqual(sibling.read_text(encoding="utf-8"), "keep")
        self.assertEqual(_file_names(output), sorted(exporter.REQUIRED_OUTPUT_PATHS))
        self.assertEqual(_temporary_siblings(output), [])

    def test_staging_validation_failure_leaves_no_target_or_staging(self):
        output = self.temp_root / "invalid_stage"
        original_write_bytes = Path.write_bytes

        def corrupt_events(path, data):
            if path.name == "events.jsonl":
                data = b"{}\n"
            return original_write_bytes(path, data)

        with patch.object(Path, "write_bytes", corrupt_events):
            with self.assertRaises(exporter.PythonReferenceExportError) as context:
                exporter.export_python_reference_artifacts(FIXTURE_PATH, output)

        self.assertEqual(context.exception.code, "staging_validation_failed")
        self.assertFalse(output.exists())
        self.assertEqual(_temporary_siblings(output), [])

    def test_staging_write_failure_leaves_existing_target_unchanged(self):
        output = self.temp_root / "write_failure"
        output.mkdir()
        sentinel = output / "old.txt"
        sentinel.write_text("old", encoding="utf-8")
        original_write_bytes = Path.write_bytes

        def fail_on_responses(path, data):
            if path.name == "responses.jsonl":
                raise OSError("simulated write failure")
            return original_write_bytes(path, data)

        with patch.object(Path, "write_bytes", fail_on_responses):
            with self.assertRaises(exporter.PythonReferenceExportError) as context:
                exporter.export_python_reference_artifacts(FIXTURE_PATH, output, replace=True)

        self.assertEqual(context.exception.code, "staging_write_failed")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "old")
        self.assertEqual(_temporary_siblings(output), [])

    def test_invalid_fixture_fails_before_output_is_created(self):
        output = self.temp_root / "invalid_fixture_output"

        with self.assertRaises(exporter.PythonReferenceExportError) as context:
            exporter.export_python_reference_artifacts(self.temp_root / "missing.json", output)

        self.assertEqual(context.exception.code, "fixture_run_failed")
        self.assertFalse(output.exists())
        self.assertEqual(_temporary_siblings(output), [])
        json.dumps(context.exception.to_dict(), ensure_ascii=False)

    def test_cli_success_and_known_failures_have_stable_exit_codes(self):
        output = self.temp_root / "cli_output"
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            success_code = exporter.main(
                ["--fixture", str(FIXTURE_PATH), "--output", str(output)]
            )
        self.assertEqual(success_code, 0)
        self.assertIn("canonical_artifact_count: 9", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exists_code = exporter.main(
                ["--fixture", str(FIXTURE_PATH), "--output", str(output)]
            )
        self.assertNotEqual(exists_code, 0)
        self.assertIn("output_exists", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            invalid_code = exporter.main(
                [
                    "--fixture",
                    str(self.temp_root / "missing.json"),
                    "--output",
                    str(self.temp_root / "missing_output"),
                ]
            )
        self.assertNotEqual(invalid_code, 0)
        self.assertIn("fixture_run_failed", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def _assert_canonical_files(self, output):
        for relative_path in exporter.REQUIRED_OUTPUT_PATHS:
            data = (output / relative_path).read_bytes()
            self.assertFalse(data.startswith(b"\xef\xbb\xbf"), relative_path)
            self.assertNotIn(b"\r", data, relative_path)
            self.assertTrue(data.endswith(b"\n"), relative_path)
            self.assertFalse(data.endswith(b"\n\n"), relative_path)
            text = data.decode("utf-8")
            if relative_path.endswith(".jsonl"):
                records = [json.loads(line) for line in text.splitlines()]
                self.assertTrue(records, relative_path)
                self.assertTrue(all(isinstance(record, dict) for record in records))
                self.assertEqual(data, canonical_jsonl_bytes(records), relative_path)
            else:
                document = json.loads(text)
                self.assertIsInstance(document, dict)
                self.assertEqual(data, canonical_json_bytes(document), relative_path)

    def _assert_manifest(self, output):
        manifest = _read_json(output / "run_manifest.json")
        self.assertEqual(
            manifest["schema_version"],
            "aeterna-runtime-comparison-run-manifest-v1",
        )
        self.assertEqual(manifest["contract_type"], "runtime_comparison_run_manifest")
        self.assertEqual(manifest["oracle_id"], "python_reference")
        self.assertEqual(manifest["oracle_version"], 1)
        self.assertEqual(manifest["runtime_candidate"], "python_reference")
        self.assertEqual(manifest["implementation_language"], "python")
        records = manifest["canonical_artifacts"]
        self.assertEqual(
            [record["path"] for record in records],
            list(exporter.CANONICAL_ARTIFACT_PATHS),
        )
        self.assertNotIn("run_manifest.json", [record["path"] for record in records])
        for record in records:
            data = (output / record["path"]).read_bytes()
            self.assertEqual(record["byte_size"], len(data))
            self.assertEqual(record["sha256"], sha256_bytes(data))
            self.assertEqual(record["comparison_level"], "canonical_bytes")
        mapping = manifest["contract_schema_mapping"]
        self.assertEqual(mapping["fixture"], "aeterna-runtime-comparison-fixture-v1")
        self.assertEqual(mapping["canonical_match_state"], "aeterna-canonical-match-state-v1")
        self.assertEqual(mapping["card_instance"], "minimal-card-instance-record-v1")
        self.assertEqual(mapping["action_space"], "minimal-legal-action-space-v0")
        self.assertEqual(mapping["action_request"], "minimal-action-request-unversioned")
        self.assertEqual(mapping["action_response"], "minimal-action-response-v0")
        self.assertEqual(mapping["engine_event"], "minimal-engine-event-v0")
        self.assertEqual(mapping["player_visible_snapshot"], "engine-player-visible-snapshot-v2")
        self.assertEqual(mapping["run_manifest"], exporter.RUN_MANIFEST_SCHEMA_VERSION)
        self.assertTrue(
            any(
                item["code"] == "ACTION_REQUEST_SCHEMA_VERSION_NOT_EMBEDDED"
                for item in manifest["known_deviations"]
            )
        )
        forbidden_keys = {"timestamp", "pid", "hostname", "username", "user"}
        self.assertFalse(forbidden_keys & set(_nested_keys(manifest)))
        self.assertFalse(any(_looks_like_absolute_path(value) for value in _scalar_values(manifest)))

    def _assert_semantics(self, output):
        initial = _read_json(output / "initial_state.json")
        requests = _read_jsonl(output / "requests.jsonl")
        responses = _read_jsonl(output / "responses.jsonl")
        checkpoints = _read_jsonl(output / "legal_actions.jsonl")
        events = _read_jsonl(output / "events.jsonl")
        player_1 = _read_json(output / "snapshot_player_1.json")
        player_2 = _read_json(output / "snapshot_player_2.json")
        final = _read_json(output / "final_debug_state.json")
        diagnostics = _read_json(output / "diagnostics.json")

        self.assertEqual(initial["state_version"], 0)
        self.assertEqual(len(requests), 4)
        self.assertEqual(len(responses), 4)
        self.assertEqual([item["accepted"] for item in responses], [True, False, True, True])
        self.assertEqual(
            [(item["state_version_before"], item["state_version_after"]) for item in responses],
            [(0, 1), (1, 1), (1, 2), (2, 3)],
        )
        self.assertEqual(len(checkpoints), 4)
        self.assertEqual([item["state_version"] for item in checkpoints], [0, 1, 2, 3])
        self.assertEqual([item["event_sequence"] for item in events], [1, 2, 3])
        self.assertEqual(
            [item["event_type"] for item in events],
            ["zone_move", "turn_transition", "zone_move"],
        )
        self.assertEqual(player_1["player_id"], "player_1")
        self.assertEqual(player_2["player_id"], "player_2")
        self.assertEqual(final["active_player_id"], "player_2")
        self.assertEqual(final["priority_player_id"], "player_2")
        self.assertEqual(diagnostics["result"], "passed")
        self.assertTrue(diagnostics["fixture_validation"]["passed"])
        self.assertTrue(diagnostics["invariant_validation"]["passed"])
        self.assertTrue(diagnostics["hidden_information_validation"]["passed"])
        self.assertTrue(diagnostics["determinism_validation"]["passed"])
        self.assertTrue(diagnostics["stale_immutability_validation"]["passed"])
        self.assertEqual(diagnostics["runner_diagnostics"]["blocking_error_count"], 0)


def _file_names(directory):
    return sorted(path.name for path in directory.iterdir() if path.is_file())


def _temporary_siblings(output):
    if not output.parent.exists():
        return []
    prefixes = (".%s.staging-" % output.name, ".%s.backup-" % output.name)
    return sorted(path.name for path in output.parent.iterdir() if path.name.startswith(prefixes))


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _nested_keys(value):
    keys = []
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.append(key)
            keys.extend(_nested_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.extend(_nested_keys(nested))
    return keys


def _scalar_values(value):
    values = []
    if isinstance(value, dict):
        for nested in value.values():
            values.extend(_scalar_values(nested))
    elif isinstance(value, list):
        for nested in value:
            values.extend(_scalar_values(nested))
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
