import importlib
import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
ENGINE_EVENT_PATH = ENGINE_DIR / "engine_event.py"
TURN_TRANSITION_PATH = ENGINE_DIR / "turn_transition.py"
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"
INVARIANTS_PATH = AI_VS_AI_DIR / "state_invariants.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_PYTHON_DIR), str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestMinimalTurnTransitionEvent(unittest.TestCase):
    def setUp(self):
        self.engine_event = _load_module("engine_event", ENGINE_EVENT_PATH)
        self.turn_transition = _load_module("turn_transition", TURN_TRANSITION_PATH)
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_helper_creates_valid_record_and_reports_invalid_inputs(self):
        metadata = {
            "semantic_event_type": "end_turn_resolved",
            "authority": "rules_kernel",
            "turn_model": "minimal_alternating_players",
            "applied": True,
            "details": {"labels": ["end_turn"]},
        }
        original_metadata = deepcopy(metadata)

        record = _turn_transition_record(self.turn_transition, metadata=metadata)
        roundtrip = json.loads(json.dumps(record, ensure_ascii=False))

        self.assertEqual(
            set(record),
            {
                "schema_version",
                "contract_type",
                "event_type",
                "previous_active_player_id",
                "next_active_player_id",
                "previous_priority_player_id",
                "next_priority_player_id",
                "turn_number_before",
                "turn_number_after",
                "phase_before",
                "phase_after",
                "source_action_id",
                "source_action_type",
                "state_version",
                "event_sequence",
                "metadata",
            },
        )
        self.assertEqual(record["schema_version"], "minimal-turn-transition-record-v0")
        self.assertEqual(record["contract_type"], "turn_transition")
        self.assertEqual(record["event_type"], "turn_transition")
        self.assertEqual(roundtrip, record)
        self.assertEqual(metadata, original_metadata)
        self.assertIsNot(record["metadata"], metadata)
        self.assertIsNot(record["metadata"]["details"], metadata["details"])
        self.assertIsNot(record["metadata"]["details"]["labels"], metadata["details"]["labels"])
        self.assertTrue(self.turn_transition.validate_turn_transition_record(record)["valid"])

        invalid_cases = (
            ("FIELD_MISSING", _remove_source_action_id),
            ("CONTRACT_TYPE_INVALID", _set_wrong_contract_type),
            ("ACTIVE_PLAYER_TRANSITION_INVALID", _set_same_active_player),
            ("TURN_NUMBER_TRANSITION_INVALID", _set_invalid_turn_increment),
            ("SOURCE_ACTION_TYPE_INVALID", _set_wrong_source_action_type),
            ("TURN_NUMBER_INVALID", _set_bool_turn_number),
            ("STATE_VERSION_INVALID", _set_bool_state_version),
            ("EVENT_SEQUENCE_INVALID", _set_bool_event_sequence),
        )
        for expected_code, mutate in invalid_cases:
            with self.subTest(expected_code=expected_code):
                invalid = deepcopy(record)
                mutate(invalid)

                result = self.turn_transition.validate_turn_transition_record(invalid)

                self.assertFalse(result["valid"])
                self.assertIn(expected_code, _error_codes(result))

        for invalid in (None, [], "transition"):
            with self.subTest(non_dict=invalid):
                result = self.turn_transition.validate_turn_transition_record(invalid)

                json.dumps(result, ensure_ascii=False)
                self.assertFalse(result["valid"])
                self.assertIn("RECORD_NOT_DICT", _error_codes(result))

    def test_wrapper_uses_generic_envelope_and_deep_copies_complete_record(self):
        record = _turn_transition_record(self.turn_transition)
        record["metadata"]["details"] = {"labels": ["turn"]}
        original = deepcopy(record)

        event = self.turn_transition.turn_transition_to_event(
            record,
            event_index=0,
            turn_number=1,
            player_id="P1",
            action_type="end_turn",
        )
        roundtrip = json.loads(json.dumps(event, ensure_ascii=False))

        self.assertEqual(event["schema_version"], "minimal-engine-event-v0")
        self.assertEqual(event["contract_type"], "engine_event")
        self.assertEqual(event["event_index"], 0)
        self.assertEqual(event["event_sequence"], 1)
        self.assertEqual(event["event_type"], "turn_transition")
        self.assertEqual(event["player_id"], "P1")
        self.assertEqual(event["action_type"], "end_turn")
        self.assertEqual(event["turn_number"], 1)
        self.assertEqual(event["state_version"], 1)
        self.assertEqual(event["payload"], record)
        self.assertEqual(roundtrip, event)
        self.assertEqual(record, original)
        self.assertIsNot(event["payload"], record)
        self.assertIsNot(event["payload"]["metadata"], record["metadata"])
        self.assertEqual(event["event_sequence"], event["payload"]["event_sequence"])
        self.assertEqual(event["state_version"], event["payload"]["state_version"])
        self.assertEqual(event["event_type"], event["payload"]["event_type"])
        self.assertTrue(self.engine_event.validate_engine_event_envelope(event)["valid"])
        self.assertTrue(self.turn_transition.validate_turn_transition_record(event["payload"])["valid"])

        event["payload"]["metadata"]["details"]["labels"].append("mutated")
        self.assertEqual(record, original)

    def test_p1_to_p2_end_turn_emits_one_typed_transition(self):
        session = self._create_session("TURN-TRANSITION-P1-P2-001")

        response = _end_turn(session)

        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertTrue(response["invariants_ok"])
        self.assertEqual(response["new_event_count"], 1)
        self.assertEqual(response["new_event_sequences"], [1])
        self.assertEqual(len(response["events"]), 1)
        self.assertEqual(len(session.state.event_log), 1)
        self.assertEqual(session.state.active_player_id, "P2")
        self.assertEqual(session.state.turn_number, 1)
        self.assertEqual(session.state.state_version, 1)

        event = response["events"][0]
        payload = event["payload"]
        self.assertEqual(event, session.state.event_log[0])
        self.assertEqual(event["contract_type"], "engine_event")
        self.assertEqual(event["event_type"], "turn_transition")
        self.assertEqual(event["player_id"], "P1")
        self.assertEqual(event["action_type"], "end_turn")
        self.assertEqual(event["turn_number"], 1)
        self.assertEqual(event["state_version"], 1)
        self.assertNotIn("previous_player_id", event)
        self.assertNotIn("next_player_id", event)
        self.assertEqual(payload["previous_active_player_id"], "P1")
        self.assertEqual(payload["next_active_player_id"], "P2")
        self.assertEqual(payload["previous_priority_player_id"], "P1")
        self.assertEqual(payload["next_priority_player_id"], "P2")
        self.assertEqual(payload["turn_number_before"], 1)
        self.assertEqual(payload["turn_number_after"], 1)
        self.assertEqual(payload["phase_before"], "main")
        self.assertEqual(payload["phase_after"], "main")
        self.assertEqual(payload["source_action_type"], "end_turn")
        self.assertEqual(payload["metadata"]["semantic_event_type"], "end_turn_resolved")
        self.assertEqual(payload["metadata"]["authority"], "rules_kernel")
        self.assertEqual(payload["metadata"]["turn_model"], "minimal_alternating_players")
        self.assertTrue(payload["metadata"]["applied"])
        self.assertEqual(session.get_diagnostics(), [])

    def test_p2_to_p1_end_turn_increments_turn_and_event_sequence(self):
        session = self._create_session("TURN-TRANSITION-P2-P1-001")
        first_response = _end_turn(session)

        second_response = _end_turn(session)

        self.assertTrue(first_response["accepted"])
        self.assertTrue(second_response["accepted"])
        self.assertEqual(session.state.active_player_id, "P1")
        self.assertEqual(session.state.turn_number, 2)
        self.assertEqual(session.state.state_version, 2)
        self.assertEqual(second_response["new_event_sequences"], [2])
        self.assertEqual(len(session.state.event_log), 2)
        event = second_response["events"][0]
        payload = event["payload"]
        self.assertEqual(event["event_index"], 1)
        self.assertEqual(event["event_sequence"], 2)
        self.assertEqual(event["player_id"], "P2")
        self.assertEqual(event["turn_number"], 2)
        self.assertEqual(payload["previous_active_player_id"], "P2")
        self.assertEqual(payload["next_active_player_id"], "P1")
        self.assertEqual(payload["turn_number_before"], 1)
        self.assertEqual(payload["turn_number_after"], 2)
        self.assertEqual(session.get_diagnostics(), [])

    def test_mixed_typed_event_log_summaries_and_player_visibility(self):
        session = self._create_session("TURN-TRANSITION-MIXED-001")

        draw_response = _draw(session)
        end_turn_response = _end_turn(session)
        transition_summary = session.get_transition_summary()
        debug_export = session.export_debug_session_state()
        player_snapshot = session.get_player_snapshot("P2")

        self.assertEqual(draw_response["events"][0]["event_type"], "zone_move")
        self.assertEqual(end_turn_response["events"][0]["event_type"], "turn_transition")
        self.assertEqual([event["event_type"] for event in session.state.event_log], ["zone_move", "turn_transition"])
        self.assertEqual([event["event_sequence"] for event in session.state.event_log], [1, 2])
        self.assertEqual([event["state_version"] for event in session.state.event_log], [1, 2])
        self.assertEqual(transition_summary["event_count"], 2)
        self.assertEqual(transition_summary["last_event_sequence"], 2)
        self.assertEqual(debug_export["debug_snapshot"]["event_log_summary"]["last_event_type"], "turn_transition")
        self.assertEqual(debug_export["last_action_response"]["events"][0]["event_type"], "turn_transition")
        json.dumps(debug_export, ensure_ascii=False)
        player_json = json.dumps(player_snapshot, ensure_ascii=False)
        self.assertNotIn('"payload"', player_json)
        self.assertNotIn("previous_active_player_id", player_json)
        self.assertEqual(session.get_diagnostics(), [])

        next_player_session = self._create_session("TURN-TRANSITION-END-THEN-DRAW-001")
        _end_turn(next_player_session)
        next_draw_response = _draw(next_player_session)
        self.assertEqual(next_draw_response["player_id"], "P2")
        self.assertEqual(
            [event["event_type"] for event in next_player_session.state.event_log],
            ["turn_transition", "zone_move"],
        )
        self.assertEqual(next_player_session.get_diagnostics(), [])

    def test_typed_transition_invariants_report_corrupted_contracts(self):
        cases = (
            ("TURN_TRANSITION_PAYLOAD_INVALID", _remove_payload_source_action_id),
            ("TURN_TRANSITION_ENVELOPE_MISMATCH", _mismatch_payload_sequence),
            ("TURN_TRANSITION_ENVELOPE_MISMATCH", _mismatch_payload_state_version),
            ("TURN_TRANSITION_PLAYER_UNKNOWN", _set_unknown_transition_player),
            ("TURN_TRANSITION_PRIORITY_INVALID", _set_wrong_transition_priority),
            ("TURN_TRANSITION_TURN_NUMBER_INVALID", _set_wrong_transition_turn_number),
            ("TURN_TRANSITION_PHASE_INVALID", _set_wrong_transition_phase),
            ("TURN_TRANSITION_RESULT_STATE_MISMATCH", _set_wrong_result_state),
        )
        for expected_code, mutate in cases:
            with self.subTest(expected_code=expected_code, mutation=mutate.__name__):
                session = self._create_session("TURN-TRANSITION-INVARIANT-%s" % mutate.__name__)
                _end_turn(session)
                mutate(session.state, session.state.event_log[0])

                errors = self.invariants.validate_state_invariants(session.state, self.runtime_package)

                self.assertIn(expected_code, [error["code"] for error in errors])

    def test_helper_imports_from_engine_namespace(self):
        imported = importlib.import_module("engine.turn_transition")

        self.assertTrue(callable(imported.create_turn_transition_record))
        self.assertTrue(callable(imported.validate_turn_transition_record))
        self.assertTrue(callable(imported.turn_transition_to_event))

    def _create_session(self, match_id):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id=match_id)
        return session


def _turn_transition_record(turn_transition, metadata=None):
    return turn_transition.create_turn_transition_record(
        previous_active_player_id="P1",
        next_active_player_id="P2",
        previous_priority_player_id="P1",
        next_priority_player_id="P2",
        turn_number_before=1,
        turn_number_after=1,
        phase_before="main",
        phase_after="main",
        source_action_id="end_turn:1:P1",
        source_action_type="end_turn",
        state_version=1,
        event_sequence=1,
        metadata=metadata
        or {
            "semantic_event_type": "end_turn_resolved",
            "authority": "rules_kernel",
            "turn_model": "minimal_alternating_players",
            "applied": True,
        },
    )


def _find_action(session, action_type):
    return next(action for action in session.get_action_space()["actions"] if action["action_type"] == action_type)


def _end_turn(session):
    return session.step(session.build_action_request(_find_action(session, "end_turn")))


def _draw(session):
    return session.step(session.build_action_request(_find_action(session, "draw_card")))


def _error_codes(result):
    return {error["code"] for error in result["errors"]}


def _remove_source_action_id(record):
    record.pop("source_action_id")


def _set_wrong_contract_type(record):
    record["contract_type"] = "wrong_contract"


def _set_same_active_player(record):
    record["next_active_player_id"] = record["previous_active_player_id"]


def _set_invalid_turn_increment(record):
    record["turn_number_after"] = record["turn_number_before"] + 2


def _set_wrong_source_action_type(record):
    record["source_action_type"] = "draw_card"


def _set_bool_turn_number(record):
    record["turn_number_before"] = True


def _set_bool_state_version(record):
    record["state_version"] = True


def _set_bool_event_sequence(record):
    record["event_sequence"] = True


def _remove_payload_source_action_id(state, event):
    event["payload"].pop("source_action_id")


def _mismatch_payload_sequence(state, event):
    event["payload"]["event_sequence"] += 10


def _mismatch_payload_state_version(state, event):
    event["payload"]["state_version"] += 10


def _set_unknown_transition_player(state, event):
    event["payload"]["previous_active_player_id"] = "PX"


def _set_wrong_transition_priority(state, event):
    event["payload"]["next_priority_player_id"] = "P1"


def _set_wrong_transition_turn_number(state, event):
    event["payload"]["turn_number_after"] += 1


def _set_wrong_transition_phase(state, event):
    event["payload"]["phase_after"] = "combat"


def _set_wrong_result_state(state, event):
    state.active_player_id = "P1"


if __name__ == "__main__":
    unittest.main()
