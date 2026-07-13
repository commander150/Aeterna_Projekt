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
CARD_INSTANCE_PATH = ENGINE_DIR / "card_instance.py"
ENGINE_EVENT_PATH = ENGINE_DIR / "engine_event.py"
ZONE_MOVE_PATH = ENGINE_DIR / "zone_move.py"
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_PYTHON_DIR), str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _card_instance_record(card_instance_module):
    return card_instance_module.create_card_instance_record(
        card_instance_id=card_instance_module.create_card_instance_id("P1", 1),
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


def _zone_move_record(zone_move_module, card_instance_module):
    instance = _card_instance_record(card_instance_module)
    return zone_move_module.create_zone_move_record(
        card_instance_id=instance["card_instance_id"],
        card_id=instance["card_id"],
        owner_player_id=instance["owner_player_id"],
        controller_player_id=instance["controller_player_id"],
        from_zone=instance["zone"],
        from_zone_index=instance["zone_index"],
        to_zone="hand",
        to_zone_index=0,
        source_action_id="draw_card:1:0:P1",
        source_action_type="draw_card",
        state_version=1,
        event_sequence=1,
        visibility_before=instance["visibility"],
        visibility_after="owner_only",
        metadata={
            "zone_operation": "move_top_or_selected_card",
            "authority": "rules_kernel",
            "applied": True,
        },
    )


class TestMinimalZoneMoveRecord(unittest.TestCase):
    def setUp(self):
        self.card_instance = _load_module("card_instance", CARD_INSTANCE_PATH)
        self.engine_event = _load_module("engine_event", ENGINE_EVENT_PATH)
        self.zone_move = _load_module("zone_move", ZONE_MOVE_PATH)

    def test_create_zone_move_record_contains_required_fields(self):
        record = _zone_move_record(self.zone_move, self.card_instance)

        self.assertEqual(record["schema_version"], "minimal-zone-move-record-v0")
        self.assertEqual(record["contract_type"], "zone_move")
        self.assertEqual(record["event_type"], "zone_move")
        self.assertEqual(record["card_instance_id"], "ci_P1_0001")
        self.assertEqual(record["card_id"], "IGN-HAM-001")
        self.assertEqual(record["owner_player_id"], "P1")
        self.assertEqual(record["controller_player_id"], "P1")
        self.assertEqual(record["from_zone"], "deck")
        self.assertEqual(record["from_zone_index"], 0)
        self.assertEqual(record["to_zone"], "hand")
        self.assertEqual(record["to_zone_index"], 0)
        self.assertEqual(record["source_action_id"], "draw_card:1:0:P1")
        self.assertEqual(record["source_action_type"], "draw_card")
        self.assertEqual(record["state_version"], 1)
        self.assertEqual(record["event_sequence"], 1)
        self.assertEqual(record["visibility_before"], "owner_only")
        self.assertEqual(record["visibility_after"], "owner_only")
        self.assertTrue(record["metadata"]["applied"])

    def test_zone_move_record_is_json_compatible(self):
        record = _zone_move_record(self.zone_move, self.card_instance)

        roundtrip = json.loads(json.dumps(record, ensure_ascii=False))

        self.assertEqual(roundtrip, record)

    def test_validate_zone_move_record_accepts_valid_record(self):
        record = _zone_move_record(self.zone_move, self.card_instance)

        result = self.zone_move.validate_zone_move_record(record)

        json.dumps(result, ensure_ascii=False)
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_validate_zone_move_record_reports_invalid_record_without_exception(self):
        invalid = {
            "contract_type": "wrong_contract",
            "event_type": "wrong_event",
            "card_instance_id": "",
            "card_id": "",
            "owner_player_id": "",
            "controller_player_id": [],
            "from_zone": "",
            "from_zone_index": "0",
            "to_zone": "",
            "to_zone_index": False,
            "source_action_id": "",
            "source_action_type": "",
            "state_version": "1",
            "event_sequence": None,
            "visibility_before": "",
            "visibility_after": "",
            "metadata": [],
        }

        result = self.zone_move.validate_zone_move_record(invalid)

        json.dumps(result, ensure_ascii=False)
        self.assertFalse(result["valid"])
        self.assertNotEqual(result["errors"], [])
        error_codes = {error["code"] for error in result["errors"]}
        self.assertIn("FIELD_MISSING", error_codes)
        self.assertIn("CONTRACT_TYPE_INVALID", error_codes)
        self.assertIn("EVENT_TYPE_INVALID", error_codes)
        self.assertIn("ZONE_INDEX_INVALID", error_codes)
        self.assertIn("SEQUENCE_INVALID", error_codes)
        self.assertIn("METADATA_INVALID", error_codes)

    def test_zone_move_to_event_is_json_compatible(self):
        record = _zone_move_record(self.zone_move, self.card_instance)
        original = deepcopy(record)

        event = self.zone_move.zone_move_to_event(
            record,
            event_index=0,
            turn_number=1,
            player_id="P1",
            action_type="draw_card",
        )
        roundtrip = json.loads(json.dumps(event, ensure_ascii=False))

        self.assertEqual(roundtrip["schema_version"], "minimal-engine-event-v0")
        self.assertEqual(roundtrip["contract_type"], "engine_event")
        self.assertEqual(roundtrip["event_index"], 0)
        self.assertEqual(roundtrip["event_type"], "zone_move")
        self.assertEqual(roundtrip["event_sequence"], 1)
        self.assertEqual(roundtrip["player_id"], "P1")
        self.assertEqual(roundtrip["action_type"], "draw_card")
        self.assertEqual(roundtrip["turn_number"], 1)
        self.assertEqual(roundtrip["state_version"], 1)
        self.assertEqual(roundtrip["payload"], record)
        self.assertNotIn("card_instance_id", roundtrip)
        self.assertNotIn("card_id", roundtrip)
        self.assertNotIn("from_zone", roundtrip)
        self.assertNotIn("to_zone", roundtrip)
        self.assertEqual(record, original)
        self.assertIsNot(event["payload"], record)
        self.assertIsNot(event["payload"]["metadata"], record["metadata"])
        self.assertTrue(self.engine_event.validate_engine_event_envelope(event)["valid"])
        self.assertTrue(self.zone_move.validate_zone_move_record(event["payload"])["valid"])

    def test_zone_move_uses_card_instance_identity(self):
        instance = _card_instance_record(self.card_instance)
        record = _zone_move_record(self.zone_move, self.card_instance)

        result = self.zone_move.validate_zone_move_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["card_instance_id"], instance["card_instance_id"])
        self.assertEqual(record["card_id"], instance["card_id"])
        self.assertEqual(record["owner_player_id"], instance["owner_player_id"])
        self.assertEqual(record["controller_player_id"], instance["controller_player_id"])

    def test_helper_imports_from_engine_namespace(self):
        imported = importlib.import_module("engine.zone_move")

        self.assertTrue(callable(imported.create_zone_move_record))
        self.assertTrue(callable(imported.validate_zone_move_record))
        self.assertTrue(callable(imported.zone_move_to_event))

    def test_helper_does_not_touch_session_state_or_history(self):
        session_module = _load_module("minimal_engine_session", SESSION_PATH)
        reader = _load_module("runtime_package_reader", READER_PATH)
        runtime_package = reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        session = session_module.MinimalEngineSession(runtime_package)
        state = session.create_match(match_id="ENGINE-ZONE-MOVE-HELPER-ISOLATION-001")
        player = state.get_player("P1")
        original_state_version = state.state_version
        original_event_log = list(state.event_log)
        original_history = session.get_action_response_history()
        original_deck = list(player.deck_card_instance_ids)
        original_hand = list(player.hand_card_instance_ids)
        original_registry = json.loads(json.dumps(state.card_instances, ensure_ascii=False))

        record = _zone_move_record(self.zone_move, self.card_instance)
        validation = self.zone_move.validate_zone_move_record(record)
        event = self.zone_move.zone_move_to_event(
            record,
            event_index=0,
            turn_number=1,
            player_id="P1",
            action_type="draw_card",
        )

        self.assertTrue(validation["valid"])
        self.assertEqual(event["payload"]["card_instance_id"], record["card_instance_id"])
        self.assertEqual(state.state_version, original_state_version)
        self.assertEqual(state.event_log, original_event_log)
        self.assertEqual(session.get_action_response_history(), original_history)
        self.assertEqual(player.deck_card_instance_ids, original_deck)
        self.assertEqual(player.hand_card_instance_ids, original_hand)
        self.assertEqual(state.card_instances, original_registry)


if __name__ == "__main__":
    unittest.main()
