import io
import json
import secrets
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools.runtime_comparison.artifact_validator import (
    ArtifactValidatorInputError,
    REQUIRED_ARTIFACT_PATHS,
    main,
    validate_runtime_comparison_artifacts,
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


class TestRuntimeComparisonArtifactValidator(unittest.TestCase):
    def setUp(self):
        PROJECT_TEMP.mkdir(parents=True, exist_ok=True)
        self.temp_root = PROJECT_TEMP / (
            "runtime_comparison_validator_test_" + secrets.token_hex(8)
        )
        self.temp_root.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_valid_tracked_oracle_is_deterministic_and_complete(self):
        before = _directory_snapshot(TRACKED_ORACLE)

        first = validate_runtime_comparison_artifacts(
            TRACKED_ORACLE,
            expected_fixture_id="minimal_draw_end_turn_v1",
        )
        second = validate_runtime_comparison_artifacts(
            TRACKED_ORACLE,
            expected_fixture_id="minimal_draw_end_turn_v1",
        )

        self.assertTrue(first["valid"])
        self.assertEqual(first["errors"], [])
        self.assertEqual(first, second)
        self.assertEqual(before, _directory_snapshot(TRACKED_ORACLE))
        self.assertEqual(
            [item["path"] for item in first["artifact_results"]],
            list(REQUIRED_ARTIFACT_PATHS),
        )
        self.assertTrue(
            all(item["canonical_bytes_valid"] for item in first["artifact_results"])
        )
        self.assertTrue(all(item["integrity_valid"] for item in first["artifact_results"]))
        self.assertEqual(
            [warning["code"] for warning in first["warnings"]],
            [
                "REQUEST_CONTRACT_UNVERSIONED",
                "BUILD_IDENTIFIER_NOT_EXTERNALLY_VERIFIED",
                "KNOWN_DEVIATION_DECLARED",
            ],
        )
        first_bytes = canonical_json_bytes(first)
        self.assertEqual(first_bytes, canonical_json_bytes(second))
        self.assertEqual(sha256_bytes(first_bytes), sha256_bytes(canonical_json_bytes(second)))

    def test_validation_is_read_only_for_valid_and_invalid_inputs(self):
        valid = self._copy_oracle("valid_read_only")
        before_valid = _directory_snapshot(self.temp_root)
        validate_runtime_comparison_artifacts(valid)
        self.assertEqual(before_valid, _directory_snapshot(self.temp_root))

        invalid = self._copy_oracle("invalid_read_only")
        (invalid / "events.jsonl").write_bytes(
            (invalid / "events.jsonl").read_bytes() + b"{}\n"
        )
        before_invalid = _directory_snapshot(self.temp_root)
        result = validate_runtime_comparison_artifacts(invalid)
        self.assertFalse(result["valid"])
        self.assertEqual(before_invalid, _directory_snapshot(self.temp_root))

    def test_missing_extra_file_and_extra_directory_are_blocking(self):
        cases = (
            ("missing", lambda path: (path / "events.jsonl").unlink(), "ARTIFACT_MISSING"),
            (
                "extra_file",
                lambda path: (path / "extra.txt").write_text("extra", encoding="utf-8"),
                "ARTIFACT_UNEXPECTED",
            ),
            (
                "extra_directory",
                lambda path: (path / "nested").mkdir(),
                "ARTIFACT_NOT_REGULAR_FILE",
            ),
        )
        for name, mutate, expected_code in cases:
            with self.subTest(name=name):
                artifact_dir = self._copy_oracle(name)
                mutate(artifact_dir)
                before = _directory_snapshot(artifact_dir)
                result = validate_runtime_comparison_artifacts(artifact_dir)
                self.assertIn(expected_code, _codes(result))
                self.assertEqual(before, _directory_snapshot(artifact_dir))

    def test_independent_hash_and_size_mismatches(self):
        artifact_changed = self._copy_oracle("artifact_changed")
        target = artifact_changed / "initial_state.json"
        target.write_bytes(target.read_bytes() + b" ")
        changed_result = validate_runtime_comparison_artifacts(artifact_changed)
        self.assertIn("ARTIFACT_SIZE_MISMATCH", _codes(changed_result))
        self.assertIn("ARTIFACT_HASH_MISMATCH", _codes(changed_result))

        size_changed = self._copy_oracle("manifest_size")
        _mutate_json(
            size_changed,
            "run_manifest.json",
            lambda value: value["canonical_artifacts"][0].__setitem__(
                "byte_size", value["canonical_artifacts"][0]["byte_size"] + 1
            ),
        )
        self.assertIn(
            "ARTIFACT_SIZE_MISMATCH",
            _codes(validate_runtime_comparison_artifacts(size_changed)),
        )

        hash_changed = self._copy_oracle("manifest_hash")
        _mutate_json(
            hash_changed,
            "run_manifest.json",
            lambda value: value["canonical_artifacts"][0].__setitem__("sha256", "0" * 64),
        )
        self.assertIn(
            "ARTIFACT_HASH_MISMATCH",
            _codes(validate_runtime_comparison_artifacts(hash_changed)),
        )

    def test_rejects_noncanonical_json_and_jsonl_bytes(self):
        cases = (
            (
                "bom",
                "initial_state.json",
                lambda data: b"\xef\xbb\xbf" + data,
                "ARTIFACT_BOM_PRESENT",
            ),
            (
                "crlf",
                "initial_state.json",
                lambda data: data.replace(b"\n", b"\r\n"),
                "ARTIFACT_LINE_ENDING_INVALID",
            ),
            (
                "indentation",
                "initial_state.json",
                lambda data: (
                    json.dumps(json.loads(data), ensure_ascii=False, sort_keys=True, indent=4)
                    + "\n"
                ).encode("utf-8"),
                "ARTIFACT_CANONICAL_BYTES_MISMATCH",
            ),
            (
                "key_order",
                "initial_state.json",
                _reverse_root_key_bytes,
                "ARTIFACT_CANONICAL_BYTES_MISMATCH",
            ),
            (
                "missing_final_lf",
                "initial_state.json",
                lambda data: data.rstrip(b"\n"),
                "ARTIFACT_LINE_ENDING_INVALID",
            ),
            (
                "jsonl_blank",
                "requests.jsonl",
                lambda data: data.splitlines(keepends=True)[0]
                + b"\n"
                + b"".join(data.splitlines(keepends=True)[1:]),
                "ARTIFACT_JSONL_RECORD_INVALID",
            ),
            (
                "invalid_json",
                "initial_state.json",
                lambda data: b"{invalid}\n",
                "ARTIFACT_JSON_PARSE_FAILED",
            ),
            (
                "jsonl_non_object",
                "requests.jsonl",
                lambda data: b"[]\n" + b"".join(data.splitlines(keepends=True)[1:]),
                "ARTIFACT_JSONL_RECORD_INVALID",
            ),
        )
        for name, relative_path, mutate, expected_code in cases:
            with self.subTest(name=name):
                artifact_dir = self._copy_oracle(name)
                path = artifact_dir / relative_path
                path.write_bytes(mutate(path.read_bytes()))
                result = validate_runtime_comparison_artifacts(artifact_dir)
                self.assertIn(expected_code, _codes(result))

    def test_rejects_manifest_contract_and_path_corruption(self):
        cases = (
            (
                "self_hash",
                lambda value: value["canonical_artifacts"][0].__setitem__(
                    "path", "run_manifest.json"
                ),
                "MANIFEST_ARTIFACT_PATH_INVALID",
            ),
            (
                "duplicate",
                lambda value: value["canonical_artifacts"][1].__setitem__(
                    "path", value["canonical_artifacts"][0]["path"]
                ),
                "ARTIFACT_MANIFEST_ENTRY_DUPLICATED",
            ),
            (
                "traversal",
                lambda value: value["canonical_artifacts"][0].__setitem__(
                    "path", "../initial_state.json"
                ),
                "MANIFEST_ARTIFACT_PATH_INVALID",
            ),
            (
                "absolute",
                lambda value: value["canonical_artifacts"][0].__setitem__(
                    "path", r"C:\artifact\initial_state.json"
                ),
                "MANIFEST_ARTIFACT_PATH_INVALID",
            ),
            (
                "schema",
                lambda value: value.__setitem__("schema_version", "wrong-schema"),
                "MANIFEST_CONTRACT_INVALID",
            ),
            (
                "mapping",
                lambda value: value.pop("contract_schema_mapping"),
                "MANIFEST_SCHEMA_MAPPING_INVALID",
            ),
        )
        for name, mutate, expected_code in cases:
            with self.subTest(name=name):
                artifact_dir = self._copy_oracle("manifest_" + name)
                _mutate_json(artifact_dir, "run_manifest.json", mutate)
                result = validate_runtime_comparison_artifacts(artifact_dir)
                self.assertIn(expected_code, _codes(result))
                if name == "absolute":
                    self.assertNotIn(
                        r"C:\artifact",
                        canonical_json_bytes(result).decode("utf-8"),
                    )

    def test_rejects_state_corruption(self):
        def reverse_players(value):
            value["players"].reverse()

        def unknown_zone_reference(value):
            value["players"][0]["hand_card_instance_ids"][0] = "unknown_instance"

        def duplicate_card_instance(value):
            value["card_instances"][1]["card_instance_id"] = value["card_instances"][0][
                "card_instance_id"
            ]

        def wrong_final_active(value):
            value["active_player_id"] = "player_1"

        def event_gap(value):
            value["event_log"][1]["event_sequence"] = 7

        cases = (
            ("player_order", "initial_state.json", reverse_players, "STATE_PLAYER_ORDER_INVALID"),
            (
                "zone_reference",
                "initial_state.json",
                unknown_zone_reference,
                "STATE_ZONE_REFERENCE_INVALID",
            ),
            (
                "duplicate_instance",
                "initial_state.json",
                duplicate_card_instance,
                "STATE_ZONE_REFERENCE_INVALID",
            ),
            (
                "final_active",
                "final_debug_state.json",
                wrong_final_active,
                "FINAL_STATE_SEMANTICS_INVALID",
            ),
            (
                "event_gap",
                "final_debug_state.json",
                event_gap,
                "STATE_EVENT_SEQUENCE_INVALID",
            ),
        )
        for name, relative_path, mutate, expected_code in cases:
            with self.subTest(name=name):
                artifact_dir = self._copy_oracle("state_" + name)
                _mutate_json(artifact_dir, relative_path, mutate)
                result = validate_runtime_comparison_artifacts(artifact_dir)
                self.assertIn(expected_code, _codes(result))

    def test_rejects_request_and_response_corruption(self):
        request_cases = (
            (
                "duplicate_request",
                lambda rows: rows[1].__setitem__("request_id", rows[0]["request_id"]),
                "REQUEST_ID_DUPLICATED",
            ),
            ("request_order", lambda rows: rows.reverse(), "REQUEST_ID_SEQUENCE_INVALID"),
            (
                "missing_payload",
                lambda rows: rows[0].pop("payload"),
                "REQUEST_CONTRACT_INVALID",
            ),
        )
        for name, mutate, expected_code in request_cases:
            with self.subTest(name=name):
                artifact_dir = self._copy_oracle(name)
                _mutate_jsonl(artifact_dir, "requests.jsonl", mutate)
                result = validate_runtime_comparison_artifacts(artifact_dir)
                self.assertIn(expected_code, _codes(result))

        response_cases = (
            (
                "accepted_order",
                lambda rows: rows[1].__setitem__("accepted", True),
                "RESPONSE_ACCEPTANCE_SEQUENCE_INVALID",
            ),
            (
                "stale_diagnostic",
                lambda rows: rows[1]["diagnostics"][0].__setitem__("code", "WRONG"),
                "STALE_DIAGNOSTIC_INVALID",
            ),
            (
                "version_path",
                lambda rows: rows[3].__setitem__("state_version_after", 4),
                "RESPONSE_STATE_VERSION_PATH_INVALID",
            ),
            (
                "response_id",
                lambda rows: rows[0].__setitem__("request_id", "wrong_request"),
                "RESPONSE_REQUEST_ID_MISMATCH",
            ),
        )
        for name, mutate, expected_code in response_cases:
            with self.subTest(name=name):
                artifact_dir = self._copy_oracle(name)
                _mutate_jsonl(artifact_dir, "responses.jsonl", mutate)
                result = validate_runtime_comparison_artifacts(artifact_dir)
                self.assertIn(expected_code, _codes(result))

    def test_rejects_event_and_legal_action_corruption(self):
        event_cases = (
            (
                "event_type",
                lambda rows: rows[0].__setitem__("event_type", "turn_transition"),
                "EVENT_TYPE_SEQUENCE_INVALID",
            ),
            (
                "event_sequence",
                lambda rows: rows[1].__setitem__("event_sequence", 8),
                "EVENT_SEQUENCE_INVALID",
            ),
        )
        for name, mutate, expected_code in event_cases:
            with self.subTest(name=name):
                artifact_dir = self._copy_oracle(name)
                _mutate_jsonl(artifact_dir, "events.jsonl", mutate)
                result = validate_runtime_comparison_artifacts(artifact_dir)
                self.assertIn(expected_code, _codes(result))

        final_mismatch = self._copy_oracle("final_event_mismatch")
        _mutate_json(
            final_mismatch,
            "final_debug_state.json",
            lambda value: value["event_log"][0].__setitem__("turn_number", 2),
        )
        self.assertIn(
            "EVENT_FINAL_STATE_MISMATCH",
            _codes(validate_runtime_comparison_artifacts(final_mismatch)),
        )

        legal_cases = (
            (
                "rank",
                lambda rows: rows[0]["action_space"]["actions"][0].__setitem__(
                    "order_rank", 999
                ),
                "LEGAL_ACTION_RANK_INVALID",
            ),
            (
                "order",
                lambda rows: rows[0]["action_space"]["actions"].reverse(),
                "LEGAL_ACTION_ORDER_INVALID",
            ),
            (
                "checkpoint_version",
                lambda rows: rows[2].__setitem__("state_version", 9),
                "LEGAL_ACTION_STATE_VERSION_INVALID",
            ),
        )
        for name, mutate, expected_code in legal_cases:
            with self.subTest(name=name):
                artifact_dir = self._copy_oracle("legal_" + name)
                _mutate_jsonl(artifact_dir, "legal_actions.jsonl", mutate)
                result = validate_runtime_comparison_artifacts(artifact_dir)
                self.assertIn(expected_code, _codes(result))

    def test_rejects_structured_hidden_information_leaks(self):
        def opponent_hand_card(value):
            value["players"][1]["zones"]["hand"]["objects"] = [
                {"card_id": "FIXTURE-CARD-P2-001"}
            ]

        def opponent_hand_instance(value):
            value["players"][1]["zones"]["hand"]["objects"] = [
                {"card_instance_id": "ci_player_2_0001"}
            ]

        def deck_card(value):
            value["metadata"]["leak"] = "FIXTURE-CARD-P1-003"

        def deck_instance(value):
            value["metadata"]["leak"] = "ci_player_1_0003"

        def registry(value):
            value["card_instances"] = []

        def event_log(value):
            value["event_log"] = []

        def source_module(value):
            value["metadata"]["source_module"] = "python.fake"

        cases = (
            ("opponent_card", opponent_hand_card, "SNAPSHOT_OPPONENT_HAND_LEAK"),
            ("opponent_instance", opponent_hand_instance, "SNAPSHOT_OPPONENT_HAND_LEAK"),
            ("deck_card", deck_card, "SNAPSHOT_DECK_INFORMATION_LEAK"),
            ("deck_instance", deck_instance, "SNAPSHOT_DECK_INFORMATION_LEAK"),
            ("registry", registry, "SNAPSHOT_INTERNAL_STATE_LEAK"),
            ("event_log", event_log, "SNAPSHOT_INTERNAL_STATE_LEAK"),
            (
                "source_module",
                source_module,
                "SNAPSHOT_IMPLEMENTATION_METADATA_LEAK",
            ),
        )
        for name, mutate, expected_code in cases:
            with self.subTest(name=name):
                artifact_dir = self._copy_oracle("snapshot_" + name)
                _mutate_json(artifact_dir, "snapshot_player_1.json", mutate)
                result = validate_runtime_comparison_artifacts(artifact_dir)
                self.assertIn(expected_code, _codes(result))

    def test_rejects_diagnostics_failures_and_prohibited_data(self):
        def hidden_false(value):
            value["hidden_information_validation"]["passed"] = False

        def stale_false(value):
            value["stale_immutability_validation"]["passed"] = False

        def blocking(value):
            value["runner_diagnostics"]["blocking_error_count"] = 1

        def absolute_path(value):
            value["debug_path"] = r"C:\private\trace.txt"

        def stack_trace(value):
            value["stack_trace"] = "Traceback: private details"

        cases = (
            ("hidden_false", hidden_false, "DIAGNOSTICS_BLOCKING_FAILURE"),
            ("stale_false", stale_false, "DIAGNOSTICS_BLOCKING_FAILURE"),
            ("blocking", blocking, "DIAGNOSTICS_BLOCKING_FAILURE"),
            ("absolute_path", absolute_path, "DIAGNOSTICS_PROHIBITED_DATA"),
            ("stack_trace", stack_trace, "DIAGNOSTICS_PROHIBITED_DATA"),
        )
        for name, mutate, expected_code in cases:
            with self.subTest(name=name):
                artifact_dir = self._copy_oracle("diagnostics_" + name)
                _mutate_json(artifact_dir, "diagnostics.json", mutate)
                result = validate_runtime_comparison_artifacts(artifact_dir)
                self.assertIn(expected_code, _codes(result))

    def test_cli_exit_codes_and_canonical_stdout(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(
                [
                    "--input",
                    str(TRACKED_ORACLE),
                    "--expected-fixture-id",
                    "minimal_draw_end_turn_v1",
                ]
            )
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        parsed = json.loads(stdout.getvalue())
        self.assertTrue(parsed["valid"])
        self.assertEqual(stdout.getvalue().encode("utf-8"), canonical_json_bytes(parsed))

        invalid = self._copy_oracle("cli_invalid")
        (invalid / "events.jsonl").unlink()
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(["--input", str(invalid)])
        self.assertEqual(exit_code, 1)
        self.assertFalse(json.loads(stdout.getvalue())["valid"])
        self.assertEqual(stderr.getvalue(), "")
        self.assertNotIn("Traceback", stdout.getvalue())

        missing = self.temp_root / "missing_directory"
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(["--input", str(missing)])
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("ARTIFACT_DIRECTORY_MISSING", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_technical_input_errors_are_distinct_from_validation_results(self):
        missing = self.temp_root / "missing"
        with self.assertRaises(ArtifactValidatorInputError) as context:
            validate_runtime_comparison_artifacts(missing)
        self.assertEqual(context.exception.code, "ARTIFACT_DIRECTORY_MISSING")

        file_input = self.temp_root / "file.txt"
        file_input.write_text("not a directory", encoding="utf-8")
        with self.assertRaises(ArtifactValidatorInputError) as context:
            validate_runtime_comparison_artifacts(file_input)
        self.assertEqual(context.exception.code, "ARTIFACT_DIRECTORY_NOT_DIRECTORY")

    def _copy_oracle(self, name):
        target = self.temp_root / name
        shutil.copytree(TRACKED_ORACLE, target)
        return target


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


def _reverse_root_key_bytes(data):
    value = json.loads(data)
    reversed_value = {key: value[key] for key in reversed(list(value))}
    return (
        json.dumps(reversed_value, ensure_ascii=False, sort_keys=False, indent=2) + "\n"
    ).encode("utf-8")


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


def _codes(result):
    return {issue["code"] for issue in result["errors"]}


if __name__ == "__main__":
    unittest.main()
