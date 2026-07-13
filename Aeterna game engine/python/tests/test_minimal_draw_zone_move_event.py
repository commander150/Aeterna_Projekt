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
CARD_INSTANCE_PATH = ENGINE_DIR / "card_instance.py"
ZONE_MOVE_PATH = ENGINE_DIR / "zone_move.py"
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


class TestMinimalDrawZoneMoveEvent(unittest.TestCase):
    def setUp(self):
        self.card_instance = _load_module("card_instance", CARD_INSTANCE_PATH)
        self.zone_move = _load_module("zone_move", ZONE_MOVE_PATH)
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_zone_move_to_event_copies_complete_record_and_context(self):
        record = _sample_zone_move_record(self.zone_move, self.card_instance)
        record["metadata"]["details"] = {"labels": ["draw"]}
        original = deepcopy(record)

        event = self.zone_move.zone_move_to_event(
            record,
            event_index=0,
            turn_number=1,
            player_id="P1",
            action_type="draw_card",
        )

        json.dumps(event, ensure_ascii=False)
        self.assertEqual(
            set(event),
            {
                "schema_version",
                "contract_type",
                "event_index",
                "event_sequence",
                "event_type",
                "player_id",
                "action_type",
                "turn_number",
                "state_version",
                "payload",
            },
        )
        self.assertEqual(event["schema_version"], "minimal-engine-event-v0")
        self.assertEqual(event["contract_type"], "engine_event")
        self.assertEqual(event["event_index"], 0)
        self.assertEqual(event["event_sequence"], 1)
        self.assertEqual(event["event_type"], "zone_move")
        self.assertEqual(event["player_id"], "P1")
        self.assertEqual(event["action_type"], "draw_card")
        self.assertEqual(event["turn_number"], 1)
        self.assertEqual(event["state_version"], 1)
        self.assertEqual(event["payload"], record)
        self.assertIsNot(event["payload"], record)
        self.assertIsNot(event["payload"]["metadata"], record["metadata"])
        self.assertEqual(record, original)

        event["payload"]["metadata"]["details"]["labels"].append("mutated")
        self.assertEqual(record, original)

    def test_successful_draw_writes_one_canonical_zone_move_event(self):
        session = self._create_session("ENGINE-DRAW-ZONE-MOVE-TEST-001")
        state = session.state
        player = state.get_player("P1")
        draw_action = _find_draw_action(session)
        drawn_instance_id = player.deck_card_instance_ids[0]
        instance_before = deepcopy(state.get_card_instance(drawn_instance_id))

        response = session.step(session.build_action_request(draw_action))

        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertTrue(response["invariants_ok"])
        self.assertEqual(response["new_event_count"], 1)
        self.assertEqual(response["new_event_sequences"], [1])
        self.assertEqual(len(response["events"]), 1)
        self.assertEqual(len(state.event_log), 1)

        event = response["events"][0]
        payload = event["payload"]
        self.assertEqual(event, state.event_log[0])
        self.assertEqual(event["contract_type"], "engine_event")
        self.assertEqual(event["event_type"], "zone_move")
        self.assertEqual(event["action_type"], "draw_card")
        self.assertEqual(event["player_id"], "P1")
        self.assertEqual(event["event_index"], 0)
        self.assertEqual(event["event_sequence"], 1)
        self.assertEqual(event["turn_number"], 1)
        self.assertEqual(event["state_version"], 1)
        for legacy_field in (
            "card_instance_id",
            "card_id",
            "from_zone",
            "from_zone_index",
            "to_zone",
            "to_zone_index",
        ):
            self.assertNotIn(legacy_field, event)

        self.assertEqual(payload["schema_version"], "minimal-zone-move-record-v0")
        self.assertEqual(payload["contract_type"], "zone_move")
        self.assertEqual(payload["event_type"], "zone_move")
        self.assertEqual(payload["card_instance_id"], drawn_instance_id)
        self.assertEqual(payload["card_id"], instance_before["card_id"])
        self.assertEqual(payload["owner_player_id"], "P1")
        self.assertEqual(payload["controller_player_id"], "P1")
        self.assertEqual(payload["from_zone"], "deck")
        self.assertEqual(payload["from_zone_index"], 0)
        self.assertEqual(payload["to_zone"], "hand")
        self.assertEqual(payload["to_zone_index"], 0)
        self.assertEqual(payload["source_action_id"], draw_action["action_id"])
        self.assertEqual(payload["source_action_type"], "draw_card")
        self.assertEqual(payload["visibility_before"], "owner_only")
        self.assertEqual(payload["visibility_after"], "owner_only")
        self.assertEqual(payload["metadata"]["zone_operation"], "draw_card")
        self.assertEqual(payload["metadata"]["semantic_event_type"], "card_drawn")
        self.assertEqual(payload["metadata"]["authority"], "rules_kernel")
        self.assertTrue(payload["metadata"]["applied"])
        self.assertEqual(event["event_sequence"], payload["event_sequence"])
        self.assertEqual(event["state_version"], payload["state_version"])
        self.assertEqual(event["event_type"], payload["event_type"])
        self.assertTrue(self.zone_move.validate_zone_move_record(payload)["valid"])
        self.assertEqual(session.get_diagnostics(), [])

    def test_response_summaries_debug_export_and_player_visibility_stay_consistent(self):
        session = self._create_session("ENGINE-DRAW-ZONE-MOVE-SUMMARY-TEST-001")
        state = session.state
        p1 = state.get_player("P1")
        drawn_instance_id = p1.deck_card_instance_ids[0]
        drawn_card_id = state.get_card_id(drawn_instance_id)

        response = _draw(session)
        transition_summary = session.get_transition_summary()
        debug_export = session.export_debug_session_state()
        opponent_snapshot = session.get_player_snapshot("P2")

        json.dumps(response, ensure_ascii=False)
        json.dumps(debug_export, ensure_ascii=False)
        json.dumps(opponent_snapshot, ensure_ascii=False)
        self.assertEqual(response["events"][0]["event_type"], "zone_move")
        self.assertEqual(response["new_event_count"], 1)
        self.assertEqual(response["new_event_sequences"], [1])
        self.assertEqual(transition_summary["event_count"], 1)
        self.assertEqual(transition_summary["last_event_sequence"], 1)
        self.assertEqual(debug_export["last_action_response"]["events"][0]["event_type"], "zone_move")
        self.assertEqual(debug_export["debug_snapshot"]["event_log_summary"]["last_event_type"], "zone_move")
        self.assertEqual(debug_export["debug_snapshot"]["event_log_summary"]["last_event_sequence"], 1)

        player_json = json.dumps(opponent_snapshot, ensure_ascii=False)
        self.assertNotIn('"payload"', player_json)
        self.assertNotIn(drawn_instance_id, player_json)
        self.assertNotIn(drawn_card_id, player_json)
        self.assertTrue(
            all(card_instance_id not in player_json for card_instance_id in p1.deck_card_instance_ids)
        )

    def test_typed_event_invariants_report_corrupted_zone_move_contracts(self):
        cases = (
            ("ZONE_MOVE_PAYLOAD_INVALID", self._remove_payload_field),
            ("ZONE_MOVE_ENVELOPE_MISMATCH", self._mismatch_payload_sequence),
            ("ZONE_MOVE_ENVELOPE_MISMATCH", self._mismatch_payload_state_version),
            ("ZONE_MOVE_INSTANCE_UNKNOWN", self._set_unknown_instance),
            ("ZONE_MOVE_CARD_ID_MISMATCH", self._set_wrong_card_id),
            ("ZONE_MOVE_RESULT_ZONE_MISMATCH", self._set_wrong_result_zone),
            ("ZONE_MOVE_RESULT_INDEX_MISMATCH", self._set_wrong_result_index),
            ("ENGINE_EVENT_SEQUENCE_INVALID", self._set_wrong_envelope_sequence),
            ("ENGINE_EVENT_CONTRACT_INVALID", self._set_wrong_action_type),
        )
        for expected_code, mutate in cases:
            with self.subTest(expected_code=expected_code, mutation=mutate.__name__):
                session = self._create_session("ENGINE-DRAW-ZONE-MOVE-INVARIANT-%s" % mutate.__name__)
                _draw(session)
                mutate(session.state.event_log[0])

                errors = self.invariants.validate_state_invariants(session.state, self.runtime_package)

                self.assertIn(expected_code, [error["code"] for error in errors])

    def _create_session(self, match_id):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id=match_id)
        return session

    @staticmethod
    def _remove_payload_field(event):
        event["payload"].pop("to_zone")

    @staticmethod
    def _mismatch_payload_sequence(event):
        event["payload"]["event_sequence"] += 10

    @staticmethod
    def _mismatch_payload_state_version(event):
        event["payload"]["state_version"] += 10

    @staticmethod
    def _set_unknown_instance(event):
        event["payload"]["card_instance_id"] = "ci_UNKNOWN_9999"

    @staticmethod
    def _set_wrong_card_id(event):
        event["payload"]["card_id"] = "UNKNOWN-CARD"

    @staticmethod
    def _set_wrong_result_zone(event):
        event["payload"]["to_zone"] = "discard"

    @staticmethod
    def _set_wrong_result_index(event):
        event["payload"]["to_zone_index"] = 99

    @staticmethod
    def _set_wrong_envelope_sequence(event):
        event["event_sequence"] = 99

    @staticmethod
    def _set_wrong_action_type(event):
        event["action_type"] = "invalid_action"


def _sample_zone_move_record(zone_move, card_instance):
    instance = card_instance.create_card_instance_record(
        card_instance_id=card_instance.create_card_instance_id("P1", 1),
        card_id="IGN-HAM-001",
        owner_player_id="P1",
        controller_player_id="P1",
        zone="deck",
        zone_index=0,
        visibility="owner_only",
        created_sequence=1,
        zone_sequence=1,
        metadata={"source": "unit_test"},
    )
    return zone_move.create_zone_move_record(
        card_instance_id=instance["card_instance_id"],
        card_id=instance["card_id"],
        owner_player_id=instance["owner_player_id"],
        controller_player_id=instance["controller_player_id"],
        from_zone="deck",
        from_zone_index=0,
        to_zone="hand",
        to_zone_index=0,
        source_action_id="draw_card:1:0:P1",
        source_action_type="draw_card",
        state_version=1,
        event_sequence=1,
        visibility_before="owner_only",
        visibility_after="owner_only",
        metadata={
            "zone_operation": "draw_card",
            "semantic_event_type": "card_drawn",
            "authority": "rules_kernel",
            "applied": True,
        },
    )


def _find_draw_action(session):
    return next(action for action in session.get_action_space()["actions"] if action["action_type"] == "draw_card")


def _draw(session):
    return session.step(session.build_action_request(_find_draw_action(session)))


if __name__ == "__main__":
    unittest.main()
