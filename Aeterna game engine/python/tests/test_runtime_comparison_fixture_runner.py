import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from engine.minimal_engine_session import MinimalEngineSession
from tools.ai_vs_ai.runtime_package_reader import load_runtime_package
from tools.runtime_comparison.canonical_json import canonical_json_bytes, sha256_bytes
from tools.runtime_comparison import python_reference_fixture as fixture_runner


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
FIXTURE_DIR = (
    ENGINE_PYTHON_DIR.parent
    / "runtime_comparison"
    / "fixtures"
    / "minimal_draw_end_turn_v1"
)
FIXTURE_PATH = FIXTURE_DIR / "fixture.json"
RUNTIME_PACKAGE_DIR = FIXTURE_DIR / "runtime_package"

REQUEST_FIELDS = {
    "request_id",
    "match_id",
    "player_id",
    "action_id",
    "action_type",
    "expected_state_version",
    "payload",
}


class TestRuntimeComparisonRequestContract(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.runtime_package = load_runtime_package(RUNTIME_PACKAGE_DIR)

    def test_explicit_request_id_and_payload_are_preserved_without_input_mutation(self):
        session = self._create_session()
        action_space = session.get_action_space("player_1")
        action = _action(action_space, "draw_card")
        action_before = deepcopy(action)
        payload = {}
        payload_before = deepcopy(payload)

        request = session.build_action_request(
            action,
            player_id="player_1",
            request_id="fixture_explicit_request_id",
            expected_state_version=0,
            payload=payload,
        )

        self.assertEqual(set(request), REQUEST_FIELDS)
        self.assertEqual(request["request_id"], "fixture_explicit_request_id")
        self.assertEqual(request["match_id"], self.fixture["match_id"])
        self.assertEqual(request["expected_state_version"], 0)
        self.assertEqual(request["payload"], {})
        self.assertEqual(action, action_before)
        self.assertEqual(payload, payload_before)
        self.assertIsNot(request["payload"], payload)

        request_before = deepcopy(request)
        response = session.step(request)

        self.assertEqual(request, request_before)
        self.assertTrue(response["accepted"])
        self.assertIsNone(response["reason"])
        self.assertEqual(response["events"][0]["event_type"], "zone_move")
        self.assertEqual(response["diagnostics"], [])

    def test_automatic_request_id_is_only_used_when_id_is_absent(self):
        session = self._create_session()
        action = _action(session.get_action_space("player_1"), "end_turn")

        automatic = session.build_action_request(action)
        explicit_empty = session.build_action_request(action, request_id="")

        self.assertEqual(
            automatic["request_id"],
            "request:%s:%s" % (self.fixture["match_id"], action["action_id"]),
        )
        self.assertEqual(explicit_empty["request_id"], "")
        rejected = session.step(explicit_empty)
        self.assertFalse(rejected["accepted"])
        self.assertEqual(rejected["reason"], "invalid_request")

    def test_match_id_mismatch_is_rejected_without_state_or_version_leak(self):
        session = self._create_session()
        action = _action(session.get_action_space("player_1"), "end_turn")
        request = session.build_action_request(
            action,
            request_id="fixture_match_mismatch",
            expected_state_version=999,
            payload={},
        )
        request["match_id"] = "ANOTHER-MATCH"
        request_before = deepcopy(request)
        state_before = session.export_canonical_match_state()
        state_bytes_before = canonical_json_bytes(state_before)

        response = session.step(request)

        state_after = session.export_canonical_match_state()
        self.assertEqual(request, request_before)
        self.assertEqual(state_after, state_before)
        self.assertEqual(canonical_json_bytes(state_after), state_bytes_before)
        self.assertFalse(response["accepted"])
        self.assertFalse(response["success"])
        self.assertEqual(response["reason"], "match_id_mismatch")
        self.assertEqual(response["match_id"], "ANOTHER-MATCH")
        self.assertIsNone(response["state_version_before"])
        self.assertIsNone(response["state_version_after"])
        self.assertEqual(response["events"], [])
        self.assertEqual(response["new_event_sequences"], [])
        self.assertIsNone(response["invariants_ok"])
        self.assertEqual(
            response["diagnostics"],
            [
                {
                    "code": "MATCH_ID_MISMATCH",
                    "severity": "error",
                    "category": "request_validation",
                    "retry_policy": "use_active_match",
                }
            ],
        )
        self.assertNotIn("expected_state_version", response["diagnostics"][0])
        self.assertNotIn("current_state_version", response["diagnostics"][0])
        self.assertNotIn("legal_actions", response)
        self.assertEqual(session.get_event_log(), [])
        self.assertEqual(len(session.get_action_response_history()), 1)

    def test_stale_rejection_has_canonical_diagnostic_and_is_immutable(self):
        session = self._create_session()
        draw_action = _action(session.get_action_space("player_1"), "draw_card")
        accepted = session.step(
            session.build_action_request(
                draw_action,
                request_id="fixture_setup_draw",
                expected_state_version=0,
                payload={},
            )
        )
        self.assertTrue(accepted["accepted"])

        end_turn = _action(session.get_action_space("player_1"), "end_turn")
        stale_request = session.build_action_request(
            end_turn,
            request_id="fixture_stale_request",
            expected_state_version=0,
            payload={},
        )
        request_before = deepcopy(stale_request)
        state_before = session.export_canonical_match_state()
        state_hash_before = sha256_bytes(canonical_json_bytes(state_before))

        response = session.step(stale_request)

        state_after = session.export_canonical_match_state()
        self.assertEqual(stale_request, request_before)
        self.assertEqual(state_after, state_before)
        self.assertEqual(sha256_bytes(canonical_json_bytes(state_after)), state_hash_before)
        self.assertFalse(response["accepted"])
        self.assertEqual(response["reason"], "stale_state_version")
        self.assertEqual(response["state_version_before"], 1)
        self.assertEqual(response["state_version_after"], 1)
        self.assertEqual(response["events"], [])
        self.assertEqual(
            response["diagnostics"],
            [
                {
                    "code": "STALE_STATE_VERSION",
                    "severity": "error",
                    "category": "request_validation",
                    "expected_state_version": 0,
                    "current_state_version": 1,
                    "retry_policy": "refresh_projection",
                }
            ],
        )
        self.assertTrue(response["invariants_ok"])

    def test_runtime_orders_active_and_inactive_action_spaces_canonically(self):
        session = self._create_session()
        for player_id, enabled_count in (("player_1", 2), ("player_2", 0)):
            with self.subTest(player_id=player_id):
                raw_actions = session.list_legal_actions(player_id)
                action_space = session.get_action_space(player_id)
                expected_order = [("end_turn", 100), ("draw_card", 200)]
                self.assertEqual(
                    [(item["action_type"], item["order_rank"]) for item in raw_actions],
                    expected_order,
                )
                self.assertEqual(
                    [(item["action_type"], item["order_rank"]) for item in action_space["actions"]],
                    expected_order,
                )
                self.assertEqual(action_space["enabled_action_count"], enabled_count)
                self.assertTrue(
                    all(
                        set(action["request_template"]["required_fields"]) == REQUEST_FIELDS
                        for action in action_space["actions"]
                    )
                )

        stale_request = session.build_action_request(
            _action(session.get_action_space("player_1"), "end_turn"),
            request_id=fixture_runner.REQUEST_IDS["stale_end_turn_player_1"],
            expected_state_version=1,
            payload={},
        )
        valid_request = session.build_action_request(
            _action(session.get_action_space("player_1"), "end_turn"),
            request_id=fixture_runner.REQUEST_IDS["end_turn_player_1"],
            expected_state_version=0,
            payload={},
        )
        self.assertNotEqual(stale_request["request_id"], valid_request["request_id"])

    def _create_session(self):
        session = MinimalEngineSession(self.runtime_package)
        session.create_match(
            deck_id_a=self.fixture["deck_ids"][0],
            deck_id_b=self.fixture["deck_ids"][1],
            match_id=self.fixture["match_id"],
            player_ids=tuple(self.fixture["player_ids"]),
            starting_hand_size=self.fixture["starting_hand_size"],
        )
        return session


class TestRuntimeComparisonFixtureRunner(unittest.TestCase):
    def test_full_step_plan_produces_canonical_in_memory_result(self):
        fixture_files_before = _relative_file_inventory(FIXTURE_DIR)
        fixture_document_before = FIXTURE_PATH.read_bytes()

        result = fixture_runner.run_python_reference_fixture(FIXTURE_PATH)

        json.dumps(result, ensure_ascii=False)
        canonical_json_bytes(result)
        self.assertEqual(result["schema_version"], "aeterna-python-reference-fixture-run-v1")
        self.assertEqual(result["result_type"], "python_reference_fixture_run")
        self.assertEqual(result["fixture_identity"]["fixture_id"], "minimal_draw_end_turn_v1")
        self.assertEqual(result["initial_canonical_state"]["state_version"], 0)
        self.assertEqual(result["initial_canonical_state"]["event_log"], [])
        self.assertEqual(result["final_canonical_state"]["state_version"], 3)
        self.assertEqual(result["final_canonical_state"]["active_player_id"], "player_2")
        self.assertEqual(result["final_canonical_state"]["priority_player_id"], "player_2")

        self.assertEqual(
            [request["request_id"] for request in result["requests"]],
            [
                "fixture_req_001_draw_player_1",
                "fixture_req_002_stale_end_turn_player_1",
                "fixture_req_003_end_turn_player_1",
                "fixture_req_004_draw_player_2",
            ],
        )
        self.assertTrue(all(set(request) == REQUEST_FIELDS for request in result["requests"]))
        self.assertTrue(all(request["payload"] == {} for request in result["requests"]))
        self.assertEqual(
            [request["expected_state_version"] for request in result["requests"]],
            [0, 0, 1, 2],
        )
        self.assertEqual(
            [response["accepted"] for response in result["responses"]],
            [True, False, True, True],
        )
        self.assertTrue(all(isinstance(item["events"], list) for item in result["responses"]))
        self.assertTrue(all(isinstance(item["diagnostics"], list) for item in result["responses"]))
        self.assertTrue(all("reason" in item for item in result["responses"]))

        self.assertEqual(
            [event["event_sequence"] for event in result["events"]],
            [1, 2, 3],
        )
        self.assertEqual(
            [event["event_type"] for event in result["events"]],
            ["zone_move", "turn_transition", "zone_move"],
        )
        self.assertEqual(
            [item["state_version"] for item in result["legal_action_checkpoints"]],
            [0, 1, 2, 3],
        )
        self.assertTrue(all(item["state_unchanged"] for item in result["legal_action_checkpoints"]))
        self.assertTrue(
            all(
                [action["order_rank"] for action in item["action_space"]["actions"]]
                == [100, 200]
                for item in result["legal_action_checkpoints"]
            )
        )

        self._assert_snapshot(result["snapshot_player_1"], "player_1", "player_2")
        self._assert_snapshot(result["snapshot_player_2"], "player_2", "player_1")
        self.assertTrue(result["visibility_checks"]["all_passed"])
        self.assertEqual(result["run_summary"]["state_version_path"], [0, 1, 1, 2, 3])
        self.assertEqual(result["run_summary"]["event_count"], 3)
        self.assertEqual(result["run_summary"]["invariant_error_count"], 0)
        self.assertTrue(result["run_summary"]["completed"])
        self.assertEqual(_relative_file_inventory(FIXTURE_DIR), fixture_files_before)
        self.assertEqual(FIXTURE_PATH.read_bytes(), fixture_document_before)

    def test_stale_immutability_covers_full_canonical_state_components(self):
        result = fixture_runner.run_python_reference_fixture(FIXTURE_PATH)
        immutability = result["stale_immutability"]

        self.assertEqual(
            immutability["canonical_state_sha256_before"],
            immutability["canonical_state_sha256_after"],
        )
        self.assertTrue(immutability["canonical_state_unchanged"])
        self.assertTrue(immutability["input_request_unchanged"])
        self.assertEqual(
            set(immutability["components"]),
            {
                "registry",
                "player_zone_lists",
                "topology",
                "occupancy",
                "event_log",
                "active_player",
                "priority_player",
                "state_version",
            },
        )
        self.assertTrue(all(immutability["components"].values()))

    def test_two_clean_runs_are_structurally_and_byte_deterministic(self):
        first = fixture_runner.run_python_reference_fixture(FIXTURE_PATH)
        second = fixture_runner.run_python_reference_fixture(FIXTURE_PATH)
        first_bytes = canonical_json_bytes(first)
        second_bytes = canonical_json_bytes(second)

        self.assertEqual(first, second)
        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual(sha256_bytes(first_bytes), sha256_bytes(second_bytes))

    def test_missing_and_invalid_fixture_inputs_have_stable_errors(self):
        missing_path = FIXTURE_DIR / "missing_fixture.json"
        with self.assertRaises(fixture_runner.RuntimeComparisonFixtureError) as missing_context:
            fixture_runner.run_python_reference_fixture(missing_path)
        self.assertEqual(missing_context.exception.code, "FIXTURE_NOT_FOUND")
        self.assertEqual(missing_context.exception.step_id, "load_fixture")

        base_fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        invalid_cases = (
            ("schema_version", "unsupported-schema", "FIXTURE_SCHEMA_INVALID"),
            ("fixture_id", "other_fixture", "FIXTURE_ID_INVALID"),
        )
        for field_name, invalid_value, expected_code in invalid_cases:
            with self.subTest(field_name=field_name):
                document = deepcopy(base_fixture)
                document[field_name] = invalid_value
                path = FIXTURE_DIR / "mocked_invalid_fixture.json"
                with patch.object(Path, "is_file", return_value=True), patch.object(
                    Path,
                    "read_text",
                    return_value=json.dumps(document),
                ):
                    with self.assertRaises(fixture_runner.RuntimeComparisonFixtureError) as context:
                        fixture_runner.run_python_reference_fixture(path)
                self.assertEqual(context.exception.code, expected_code)
                json.dumps(context.exception.to_dict(), ensure_ascii=False)
                self.assertNotIn(str(FIXTURE_DIR), json.dumps(context.exception.to_dict()))

    def test_missing_action_has_stable_fixture_error(self):
        original_get_action_space = fixture_runner.MinimalEngineSession.get_action_space

        def without_draw(session, player_id=None):
            action_space = original_get_action_space(session, player_id)
            action_space["actions"] = [
                action for action in action_space["actions"] if action["action_type"] != "draw_card"
            ]
            return action_space

        with patch.object(
            fixture_runner.MinimalEngineSession,
            "get_action_space",
            without_draw,
        ):
            with self.assertRaises(fixture_runner.RuntimeComparisonFixtureError) as context:
                fixture_runner.run_python_reference_fixture(FIXTURE_PATH)

        self.assertEqual(context.exception.code, "ACTION_NOT_FOUND")
        self.assertEqual(context.exception.step_id, "step_1_draw_player_1")

    def test_step_assertion_failure_has_stable_fixture_error(self):
        original_step = fixture_runner.MinimalEngineSession.step

        def reject_first_draw(session, request):
            if request.get("request_id") == "fixture_req_001_draw_player_1":
                return {
                    "accepted": False,
                    "success": False,
                    "reason": "forced_test_rejection",
                    "events": [],
                    "diagnostics": [],
                }
            return original_step(session, request)

        with patch.object(
            fixture_runner.MinimalEngineSession,
            "step",
            reject_first_draw,
        ):
            with self.assertRaises(fixture_runner.RuntimeComparisonFixtureError) as context:
                fixture_runner.run_python_reference_fixture(FIXTURE_PATH)

        self.assertEqual(context.exception.code, "STEP_ASSERTION_FAILED")
        self.assertEqual(context.exception.step_id, "step_1_draw_player_1")

    def _assert_snapshot(self, snapshot, viewer_id, opponent_id):
        self.assertEqual(snapshot["snapshot_type"], "player_visible_snapshot")
        self.assertEqual(snapshot["visibility_mode"], "player")
        self.assertEqual(snapshot["player_id"], viewer_id)
        players = {item["player_id"]: item for item in snapshot["players"]}
        self.assertEqual(len(players[viewer_id]["zones"]["hand"]["objects"]), 2)
        self.assertEqual(players[opponent_id]["zones"]["hand"]["objects"], [])
        self.assertTrue(all(item["zones"]["deck"]["objects"] == [] for item in players.values()))
        self.assertNotIn("card_instances", snapshot)
        self.assertNotIn("event_log", snapshot)
        self.assertNotIn("debug_snapshot", snapshot)
        self.assertNotIn("source", snapshot["metadata"])


def _action(action_space, action_type):
    return next(
        action
        for action in action_space["actions"]
        if action["action_type"] == action_type and action["enabled"] is True
    )


def _relative_file_inventory(root):
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    )


if __name__ == "__main__":
    unittest.main()
