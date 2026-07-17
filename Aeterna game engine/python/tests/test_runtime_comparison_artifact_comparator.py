import io
import json
import secrets
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools.runtime_comparison import artifact_comparator as comparator
from tools.runtime_comparison.artifact_comparator import (
    MAX_MISMATCHES_PER_ARTIFACT,
    compare_runtime_comparison_artifacts,
    main,
)
from tools.runtime_comparison.canonical_json import (
    canonical_json_bytes,
    canonical_jsonl_bytes,
    sha256_bytes,
)


PYTHON_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = PYTHON_DIR.parent
PROJECT_ROOT = ENGINE_DIR.parent
PROJECT_TEMP = PROJECT_ROOT / "TEMP"
TRACKED_ORACLE = (
    ENGINE_DIR
    / "runtime_comparison"
    / "fixtures"
    / "minimal_draw_end_turn_v1"
    / "expected"
    / "python_reference_v1"
)


class TestRuntimeComparisonArtifactComparator(unittest.TestCase):
    def setUp(self):
        PROJECT_TEMP.mkdir(parents=True, exist_ok=True)
        self.temp_root = PROJECT_TEMP / (
            "runtime_comparison_comparator_test_" + secrets.token_hex(8)
        )
        self.temp_root.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_self_comparison_matches_with_stable_warning(self):
        before = _directory_snapshot(TRACKED_ORACLE)

        result = compare_runtime_comparison_artifacts(
            TRACKED_ORACLE,
            TRACKED_ORACLE,
            expected_fixture_id="minimal_draw_end_turn_v1",
        )

        self.assertTrue(result["comparable"])
        self.assertTrue(result["semantic_match"])
        self.assertTrue(result["canonical_match"])
        self.assertTrue(result["match"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(
            [warning["code"] for warning in result["warnings"]],
            ["SELF_COMPARISON", "REQUEST_CONTRACT_UNVERSIONED"],
        )
        self.assertEqual(
            [item["status"] for item in result["artifact_comparisons"]],
            ["equal"] * 10,
        )
        serialized = canonical_json_bytes(result).decode("utf-8")
        self.assertNotIn(str(PROJECT_ROOT), serialized)
        self.assertNotIn(str(TRACKED_ORACLE), serialized)
        self.assertEqual(before, _directory_snapshot(TRACKED_ORACLE))

    def test_identical_copy_matches_without_self_warning(self):
        candidate = self._copy_oracle("identical_candidate")

        result = compare_runtime_comparison_artifacts(TRACKED_ORACLE, candidate)

        self.assertTrue(result["match"])
        self.assertNotIn("SELF_COMPARISON", _warning_codes(result))
        self.assertEqual(result["summary"]["equal_artifact_count"], 10)
        self.assertEqual(result["allowed_differences"], [])

    def test_allowed_manifest_identity_differences_do_not_block_match(self):
        candidate = self._copy_oracle("allowed_manifest_candidate")

        def mutate(manifest):
            manifest["runtime_candidate"] = "candidate_runtime"
            manifest["implementation_language"] = "candidate_language"
            manifest["runtime_version"] = "candidate-version"
            manifest["operating_system"] = "candidate-os"
            manifest["architecture"] = "candidate-architecture"
            manifest["build_identifier"] = "candidate-build"
            manifest["implementation_specific"] = {"adapter": "candidate"}

        _mutate_json(candidate, "run_manifest.json", mutate)

        result = compare_runtime_comparison_artifacts(TRACKED_ORACLE, candidate)

        self.assertTrue(result["validation"]["candidate"]["valid"])
        self.assertTrue(result["comparable"])
        self.assertTrue(result["semantic_match"])
        self.assertTrue(result["canonical_match"])
        self.assertTrue(result["match"])
        self.assertEqual(
            {item["code"] for item in result["allowed_differences"]},
            {
                "RUNTIME_CANDIDATE_DIFFERENCE",
                "IMPLEMENTATION_LANGUAGE_DIFFERENCE",
                "RUNTIME_VERSION_DIFFERENCE",
                "OPERATING_SYSTEM_DIFFERENCE",
                "ARCHITECTURE_DIFFERENCE",
                "BUILD_IDENTIFIER_DIFFERENCE",
                "IMPLEMENTATION_SPECIFIC_DIFFERENCE",
            },
        )
        self.assertEqual(
            _artifact_result(result, "run_manifest.json")["status"],
            "allowed_difference",
        )

    def test_invalid_reference_and_candidate_stop_comparison(self):
        invalid_reference = self._copy_oracle("invalid_reference")
        path = invalid_reference / "events.jsonl"
        path.write_bytes(path.read_bytes() + b" ")
        result = compare_runtime_comparison_artifacts(
            invalid_reference, TRACKED_ORACLE
        )
        self.assertFalse(result["comparable"])
        self.assertFalse(result["match"])
        self.assertIn("REFERENCE_PACKAGE_INVALID", _error_codes(result))
        self.assertEqual(result["semantic_mismatches"], [])

        invalid_candidate = self._copy_oracle("invalid_candidate")
        (invalid_candidate / "events.jsonl").unlink()
        result = compare_runtime_comparison_artifacts(
            TRACKED_ORACLE, invalid_candidate
        )
        self.assertFalse(result["comparable"])
        self.assertFalse(result["match"])
        self.assertIn("CANDIDATE_PACKAGE_INVALID", _error_codes(result))
        self.assertEqual(result["semantic_mismatches"], [])

        both_invalid = self._copy_oracle("both_invalid_reference")
        both_candidate = self._copy_oracle("both_invalid_candidate")
        (both_invalid / "requests.jsonl").unlink()
        (both_candidate / "responses.jsonl").unlink()
        result = compare_runtime_comparison_artifacts(both_invalid, both_candidate)
        self.assertEqual(
            _error_codes(result) & {
                "REFERENCE_PACKAGE_INVALID",
                "CANDIDATE_PACKAGE_INVALID",
            },
            {"REFERENCE_PACKAGE_INVALID", "CANDIDATE_PACKAGE_INVALID"},
        )

    def test_manifest_compatibility_blockers_are_explicit(self):
        cases = (
            (
                "fixture_id",
                self._change_fixture_id,
                "FIXTURE_ID_MISMATCH",
            ),
            (
                "oracle_version",
                lambda directory: _mutate_json(
                    directory,
                    "run_manifest.json",
                    lambda value: value.__setitem__("oracle_version", 2),
                ),
                "ORACLE_VERSION_MISMATCH",
            ),
            (
                "comparison_profile",
                lambda directory: _mutate_json(
                    directory,
                    "run_manifest.json",
                    lambda value: value.__setitem__(
                        "comparison_profile", "candidate-profile"
                    ),
                ),
                "COMPARISON_PROFILE_MISMATCH",
            ),
            (
                "canonicalization_profile",
                lambda directory: _mutate_json(
                    directory,
                    "run_manifest.json",
                    lambda value: value.__setitem__(
                        "canonicalization_profile", "candidate-canonicalization"
                    ),
                ),
                "CANONICALIZATION_PROFILE_MISMATCH",
            ),
            (
                "schema_mapping",
                lambda directory: _mutate_json(
                    directory,
                    "run_manifest.json",
                    lambda value: value["contract_schema_mapping"].__setitem__(
                        "action_response", "candidate-response-v1"
                    ),
                ),
                "CONTRACT_SCHEMA_MAPPING_MISMATCH",
            ),
            (
                "unsupported_level",
                lambda directory: _mutate_json(
                    directory,
                    "run_manifest.json",
                    lambda value: value["canonical_artifacts"][0].__setitem__(
                        "comparison_level", "unknown-level"
                    ),
                ),
                "COMPARISON_LEVEL_UNSUPPORTED",
            ),
        )
        for name, mutate, expected_code in cases:
            with self.subTest(name=name):
                candidate = self._copy_oracle("compatibility_" + name)
                mutate(candidate)
                result = compare_runtime_comparison_artifacts(
                    TRACKED_ORACLE, candidate
                )
                self.assertFalse(result["comparable"])
                self.assertFalse(result["match"])
                self.assertIn(expected_code, _error_codes(result))

    def test_validator_valid_semantic_mismatches_have_precise_pointers(self):
        cases = (
            (
                "initial",
                self._change_initial_metadata,
                "initial_state.json",
                "/semantic_metadata/candidate_note",
            ),
            (
                "request",
                self._change_request_action_id,
                "requests.jsonl",
                "/0/action_id",
            ),
            (
                "response",
                self._change_response_metadata,
                "responses.jsonl",
                "/0/metadata/candidate_note",
            ),
            (
                "legal",
                self._change_legal_ordering_label,
                "legal_actions.jsonl",
                "/0/canonical_action_ordering",
            ),
            (
                "event",
                self._change_event_semantic_metadata,
                "events.jsonl",
                "/0/payload/semantic_metadata/candidate_note",
            ),
            (
                "snapshot",
                self._change_snapshot_metadata,
                "snapshot_player_1.json",
                "/metadata/candidate_note",
            ),
            (
                "final",
                self._change_final_metadata,
                "final_debug_state.json",
                "/semantic_metadata/candidate_note",
            ),
        )
        for name, mutate, artifact_path, pointer in cases:
            with self.subTest(name=name):
                candidate = self._copy_oracle("semantic_" + name)
                mutate(candidate)
                result = compare_runtime_comparison_artifacts(
                    TRACKED_ORACLE, candidate
                )
                self.assertTrue(result["validation"]["candidate"]["valid"])
                self.assertTrue(result["comparable"])
                self.assertFalse(result["semantic_match"])
                self.assertFalse(result["canonical_match"])
                self.assertFalse(result["match"])
                self.assertIn(
                    (artifact_path, pointer),
                    {
                        (item["artifact_path"], item["json_pointer"])
                        for item in result["semantic_mismatches"]
                    },
                )

    def test_core_trajectory_corruption_is_rejected_by_validation_gate(self):
        cases = (
            (
                "initial_active_player",
                "initial_state.json",
                "json",
                lambda value: value.__setitem__("active_player_id", "player_2"),
            ),
            (
                "request_action_type",
                "requests.jsonl",
                "jsonl",
                lambda value: value[0].__setitem__("action_type", "end_turn"),
            ),
            (
                "response_accepted",
                "responses.jsonl",
                "jsonl",
                lambda value: value[1].__setitem__("accepted", True),
            ),
            (
                "legal_rank",
                "legal_actions.jsonl",
                "jsonl",
                lambda value: value[0]["action_space"]["actions"][0].__setitem__(
                    "order_rank", 999
                ),
            ),
            (
                "final_zone",
                "final_debug_state.json",
                "json",
                lambda value: value["players"][0]["hand_card_instance_ids"].pop(),
            ),
        )
        for name, artifact_path, format_name, mutate in cases:
            with self.subTest(name=name):
                candidate = self._copy_oracle("gate_" + name)
                if format_name == "json":
                    _mutate_json(candidate, artifact_path, mutate)
                else:
                    _mutate_jsonl(candidate, artifact_path, mutate)
                _refresh_manifest_entries(candidate, [artifact_path])
                result = compare_runtime_comparison_artifacts(
                    TRACKED_ORACLE, candidate
                )
                self.assertFalse(result["validation"]["candidate"]["valid"])
                self.assertFalse(result["comparable"])
                self.assertIn("CANDIDATE_PACKAGE_INVALID", _error_codes(result))
                self.assertEqual(result["semantic_mismatches"], [])

    def test_semantic_diff_is_explicitly_json_type_sensitive(self):
        cases = (
            ({"value": True}, {"value": 1}, "/value", "type_mismatch"),
            ({"value": False}, {"value": 0}, "/value", "type_mismatch"),
            ({"value": None}, {}, "/value", "field_missing"),
            ({"value": 1}, {"value": "1"}, "/value", "type_mismatch"),
            ({"value": []}, {"value": {}}, "/value", "type_mismatch"),
        )
        for reference, candidate, pointer, mismatch_type in cases:
            with self.subTest(reference=reference, candidate=candidate):
                diff = comparator._semantic_diff(
                    reference, candidate, "synthetic.json"
                )
                self.assertEqual(diff["mismatch_count"], 1)
                self.assertEqual(diff["details"][0]["json_pointer"], pointer)
                self.assertEqual(diff["details"][0]["mismatch_type"], mismatch_type)

    def test_ordering_is_distinct_and_package_order_corruption_is_invalid(self):
        diff = comparator._semantic_diff(
            {"items": ["a", "b"]},
            {"items": ["b", "a"]},
            "synthetic.json",
        )
        self.assertIn(
            ("/items", "ordering_mismatch"),
            {
                (item["json_pointer"], item["mismatch_type"])
                for item in diff["details"]
            },
        )

        candidate = self._copy_oracle("request_order_invalid")
        _mutate_jsonl(candidate, "requests.jsonl", lambda rows: rows.reverse())
        _refresh_manifest_entries(candidate, ["requests.jsonl"])
        result = compare_runtime_comparison_artifacts(TRACKED_ORACLE, candidate)
        self.assertFalse(result["comparable"])
        self.assertIn("CANDIDATE_PACKAGE_INVALID", _error_codes(result))

    def test_semantic_level_byte_policy_does_not_weaken_validator(self):
        semantic_value = {"a": 1, "b": 2}
        canonical = canonical_json_bytes(semantic_value)
        noncanonical = b'{"b": 2, "a": 1}\n'
        self.assertNotEqual(canonical, noncanonical)
        self.assertEqual(json.loads(canonical), json.loads(noncanonical))
        diff = comparator._semantic_diff(
            json.loads(canonical), json.loads(noncanonical), "synthetic.json"
        )
        self.assertEqual(diff["mismatch_count"], 0)

        candidate = self._copy_oracle("semantic_level_gate")
        _mutate_json(
            candidate,
            "run_manifest.json",
            lambda value: value["canonical_artifacts"][0].__setitem__(
                "comparison_level", "semantic"
            ),
        )
        result = compare_runtime_comparison_artifacts(TRACKED_ORACLE, candidate)
        self.assertFalse(result["validation"]["candidate"]["valid"])
        self.assertFalse(result["comparable"])

    def test_diff_details_are_truncated_but_total_count_is_preserved(self):
        candidate = self._copy_oracle("truncated_candidate")

        def mutate(value):
            for index in range(MAX_MISMATCHES_PER_ARTIFACT + 25):
                value["semantic_metadata"]["candidate_%03d" % index] = index

        _mutate_json(candidate, "initial_state.json", mutate)
        _refresh_manifest_entries(candidate, ["initial_state.json"])

        result = compare_runtime_comparison_artifacts(TRACKED_ORACLE, candidate)

        record = _artifact_result(result, "initial_state.json")
        self.assertTrue(result["validation"]["candidate"]["valid"])
        self.assertTrue(record["details_truncated"])
        self.assertEqual(record["mismatch_count"], 125)
        self.assertEqual(
            len(
                [
                    item
                    for item in result["semantic_mismatches"]
                    if item["artifact_path"] == "initial_state.json"
                ]
            ),
            MAX_MISMATCHES_PER_ARTIFACT,
        )
        self.assertIn("COMPARISON_DETAILS_TRUNCATED", _warning_codes(result))

    def test_comparison_result_is_deterministic_and_canonical(self):
        candidate = self._copy_oracle("deterministic_candidate")
        self._change_initial_metadata(candidate)

        first = compare_runtime_comparison_artifacts(TRACKED_ORACLE, candidate)
        second = compare_runtime_comparison_artifacts(TRACKED_ORACLE, candidate)

        self.assertEqual(first, second)
        first_bytes = canonical_json_bytes(first)
        self.assertEqual(first_bytes, canonical_json_bytes(second))
        self.assertEqual(sha256_bytes(first_bytes), sha256_bytes(canonical_json_bytes(second)))

    def test_comparator_is_read_only_for_match_mismatch_and_invalid(self):
        cases = []
        matching = self._copy_oracle("readonly_match")
        cases.append(matching)
        mismatching = self._copy_oracle("readonly_mismatch")
        self._change_initial_metadata(mismatching)
        cases.append(mismatching)
        invalid = self._copy_oracle("readonly_invalid")
        (invalid / "events.jsonl").unlink()
        cases.append(invalid)

        for candidate in cases:
            with self.subTest(candidate=candidate.name):
                before_reference = _directory_snapshot(TRACKED_ORACLE)
                before_candidate = _directory_snapshot(candidate)
                before_root = _directory_snapshot(self.temp_root)
                compare_runtime_comparison_artifacts(TRACKED_ORACLE, candidate)
                self.assertEqual(before_reference, _directory_snapshot(TRACKED_ORACLE))
                self.assertEqual(before_candidate, _directory_snapshot(candidate))
                self.assertEqual(before_root, _directory_snapshot(self.temp_root))

    def test_cli_exit_codes_and_stdout_contract(self):
        exit_code, stdout, stderr = _run_main(
            ["--reference", str(TRACKED_ORACLE), "--candidate", str(TRACKED_ORACLE)]
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")
        result = json.loads(stdout)
        self.assertTrue(result["match"])
        self.assertEqual(stdout.encode("utf-8"), canonical_json_bytes(result))

        mismatch = self._copy_oracle("cli_mismatch")
        self._change_initial_metadata(mismatch)
        exit_code, stdout, stderr = _run_main(
            ["--reference", str(TRACKED_ORACLE), "--candidate", str(mismatch)]
        )
        self.assertEqual(exit_code, 1)
        self.assertTrue(json.loads(stdout)["comparable"])
        self.assertEqual(stderr, "")
        self.assertNotIn("Traceback", stdout)

        invalid = self._copy_oracle("cli_invalid")
        (invalid / "events.jsonl").unlink()
        exit_code, stdout, stderr = _run_main(
            ["--reference", str(TRACKED_ORACLE), "--candidate", str(invalid)]
        )
        self.assertEqual(exit_code, 2)
        self.assertFalse(json.loads(stdout)["comparable"])
        self.assertEqual(stderr, "")

        missing = self.temp_root / "missing"
        exit_code, stdout, stderr = _run_main(
            ["--reference", str(TRACKED_ORACLE), "--candidate", str(missing)]
        )
        self.assertEqual(exit_code, 3)
        self.assertEqual(stdout, "")
        self.assertIn("CANDIDATE_INPUT_ARTIFACT_DIRECTORY_MISSING", stderr)
        self.assertNotIn("Traceback", stderr)

    def _copy_oracle(self, name):
        target = self.temp_root / name
        shutil.copytree(TRACKED_ORACLE, target)
        return target

    def _change_fixture_id(self, directory):
        _mutate_json(
            directory,
            "diagnostics.json",
            lambda value: value["fixture_validation"].__setitem__(
                "fixture_id", "candidate_fixture"
            ),
        )
        _refresh_manifest_entries(directory, ["diagnostics.json"])
        _mutate_json(
            directory,
            "run_manifest.json",
            lambda value: value.__setitem__("fixture_id", "candidate_fixture"),
        )

    def _change_initial_metadata(self, directory):
        _mutate_json(
            directory,
            "initial_state.json",
            lambda value: value["semantic_metadata"].__setitem__(
                "candidate_note", "different"
            ),
        )
        _refresh_manifest_entries(directory, ["initial_state.json"])

    def _change_request_action_id(self, directory):
        _mutate_jsonl(
            directory,
            "requests.jsonl",
            lambda value: value[0].__setitem__(
                "action_id", "candidate_draw_action"
            ),
        )
        _refresh_manifest_entries(directory, ["requests.jsonl"])

    def _change_response_metadata(self, directory):
        _mutate_jsonl(
            directory,
            "responses.jsonl",
            lambda value: value[0]["metadata"].__setitem__(
                "candidate_note", "different"
            ),
        )
        _refresh_manifest_entries(directory, ["responses.jsonl"])

    def _change_legal_ordering_label(self, directory):
        _mutate_jsonl(
            directory,
            "legal_actions.jsonl",
            lambda value: value[0].__setitem__(
                "canonical_action_ordering", "candidate_ordering_label"
            ),
        )
        _refresh_manifest_entries(directory, ["legal_actions.jsonl"])

    def _change_event_semantic_metadata(self, directory):
        _mutate_jsonl(
            directory,
            "events.jsonl",
            lambda value: value[0]["payload"]["semantic_metadata"].__setitem__(
                "candidate_note", "different"
            ),
        )
        _mutate_jsonl(
            directory,
            "responses.jsonl",
            lambda value: value[0]["events"][0]["payload"]["metadata"].__setitem__(
                "candidate_note", "different"
            ),
        )
        _mutate_json(
            directory,
            "final_debug_state.json",
            lambda value: value["event_log"][0]["payload"][
                "semantic_metadata"
            ].__setitem__("candidate_note", "different"),
        )
        _refresh_manifest_entries(
            directory,
            ["events.jsonl", "responses.jsonl", "final_debug_state.json"],
        )

    def _change_snapshot_metadata(self, directory):
        _mutate_json(
            directory,
            "snapshot_player_1.json",
            lambda value: value["metadata"].__setitem__(
                "candidate_note", "different"
            ),
        )
        _refresh_manifest_entries(directory, ["snapshot_player_1.json"])

    def _change_final_metadata(self, directory):
        _mutate_json(
            directory,
            "final_debug_state.json",
            lambda value: value["semantic_metadata"].__setitem__(
                "candidate_note", "different"
            ),
        )
        _refresh_manifest_entries(directory, ["final_debug_state.json"])


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _mutate_json(directory, relative_path, mutate):
    path = directory / relative_path
    value = _read_json(path)
    mutate(value)
    path.write_bytes(canonical_json_bytes(value))


def _mutate_jsonl(directory, relative_path, mutate):
    path = directory / relative_path
    value = _read_jsonl(path)
    mutate(value)
    path.write_bytes(canonical_jsonl_bytes(value))


def _refresh_manifest_entries(directory, relative_paths):
    manifest_path = directory / "run_manifest.json"
    manifest = _read_json(manifest_path)
    by_path = {record["path"]: record for record in manifest["canonical_artifacts"]}
    for relative_path in relative_paths:
        data = (directory / relative_path).read_bytes()
        by_path[relative_path]["byte_size"] = len(data)
        by_path[relative_path]["sha256"] = sha256_bytes(data)
    manifest_path.write_bytes(canonical_json_bytes(manifest))


def _directory_snapshot(directory):
    result = {}
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory).as_posix()
        if path.is_file():
            stat = path.stat()
            result[relative] = {
                "bytes": path.read_bytes(),
                "mtime_ns": stat.st_mtime_ns,
                "type": "file",
            }
        elif path.is_dir():
            result[relative] = {"type": "directory"}
        else:
            result[relative] = {"type": "other"}
    return result


def _artifact_result(result, path):
    return next(item for item in result["artifact_comparisons"] if item["path"] == path)


def _error_codes(result):
    return {item["code"] for item in result["errors"]}


def _warning_codes(result):
    return {item["code"] for item in result["warnings"]}


def _run_main(arguments):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = main(arguments)
    return exit_code, stdout.getvalue(), stderr.getvalue()


if __name__ == "__main__":
    unittest.main()
