import importlib.util
import json
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
CARD_INSTANCE_PATH = ENGINE_DIR / "card_instance.py"
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _sample_record(card_instance_module):
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
        metadata={
            "source": "unit_test",
        },
    )


class TestMinimalCardInstanceRecord(unittest.TestCase):
    def setUp(self):
        self.card_instance = _load_module("card_instance", CARD_INSTANCE_PATH)

    def test_create_card_instance_id_is_deterministic(self):
        first = self.card_instance.create_card_instance_id("P1", 1)
        second = self.card_instance.create_card_instance_id("P1", 1)
        different_sequence = self.card_instance.create_card_instance_id("P1", 2)

        self.assertEqual(first, "ci_P1_0001")
        self.assertEqual(first, second)
        self.assertNotEqual(first, different_sequence)

    def test_create_card_instance_record_contains_required_fields(self):
        record = _sample_record(self.card_instance)

        self.assertEqual(record["schema_version"], "minimal-card-instance-record-v1")
        self.assertEqual(record["contract_type"], "card_instance_record")
        self.assertEqual(record["card_instance_id"], "ci_P1_0001")
        self.assertEqual(record["card_id"], "IGN-HAM-001")
        self.assertEqual(record["owner_player_id"], "P1")
        self.assertEqual(record["controller_player_id"], "P1")
        self.assertEqual(record["zone"], "deck")
        self.assertEqual(record["zone_index"], 0)
        self.assertEqual(record["visibility"], "owner_only")
        self.assertEqual(record["created_sequence"], 1)
        self.assertEqual(record["zone_sequence"], 1)
        self.assertIsNone(record["activity_state"])
        self.assertEqual(record["metadata"]["source"], "unit_test")

    def test_record_is_json_compatible(self):
        record = _sample_record(self.card_instance)

        roundtrip = json.loads(json.dumps(record, ensure_ascii=False))

        self.assertEqual(roundtrip, record)

    def test_validate_card_instance_record_accepts_valid_record(self):
        record = _sample_record(self.card_instance)

        result = self.card_instance.validate_card_instance_record(record)

        json.dumps(result, ensure_ascii=False)
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_validate_card_instance_record_reports_invalid_record_without_exception(self):
        invalid = {
            "contract_type": "wrong_contract",
            "card_instance_id": "",
            "card_id": "",
            "owner_player_id": "",
            "zone": "",
            "zone_index": "0",
            "visibility": "",
            "created_sequence": "1",
            "zone_sequence": None,
            "metadata": [],
        }

        result = self.card_instance.validate_card_instance_record(invalid)

        json.dumps(result, ensure_ascii=False)
        self.assertFalse(result["valid"])
        self.assertNotEqual(result["errors"], [])
        self.assertTrue(any(error["code"] == "CONTRACT_TYPE_INVALID" for error in result["errors"]))
        self.assertTrue(any(error["code"] == "FIELD_MISSING" for error in result["errors"]))
        self.assertTrue(any(error["code"] == "ZONE_INDEX_INVALID" for error in result["errors"]))
        self.assertTrue(any(error["code"] == "METADATA_INVALID" for error in result["errors"]))

    def test_card_instance_to_object_reference_is_json_compatible(self):
        record = _sample_record(self.card_instance)

        reference = self.card_instance.card_instance_to_object_reference(record)
        roundtrip = json.loads(json.dumps(reference, ensure_ascii=False))

        self.assertEqual(roundtrip["schema_version"], "minimal-object-reference-v0")
        self.assertEqual(roundtrip["contract_type"], "object_reference")
        self.assertEqual(roundtrip["object_type"], "card_instance")
        self.assertEqual(roundtrip["object_id"], record["card_instance_id"])
        self.assertEqual(roundtrip["card_instance_id"], record["card_instance_id"])
        self.assertEqual(roundtrip["card_id"], record["card_id"])
        self.assertEqual(roundtrip["zone"], "deck")
        self.assertEqual(roundtrip["zone_sequence"], 1)
        self.assertEqual(roundtrip["controller_player_id"], "P1")
        self.assertEqual(roundtrip["visibility"], "owner_only")
        self.assertNotIn("activity_state", roundtrip)

    def test_helper_import_does_not_touch_session_state(self):
        session_module = _load_module("minimal_engine_session", SESSION_PATH)
        reader = _load_module("runtime_package_reader", READER_PATH)
        runtime_package = reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        session = session_module.MinimalEngineSession(runtime_package)
        state = session.create_match(match_id="ENGINE-CARD-INSTANCE-HELPER-ISOLATION-001")
        original_state_version = state.state_version
        original_event_log = list(state.event_log)
        original_history = session.get_action_response_history()
        player = state.get_player("P1")
        original_deck = list(player.deck_card_instance_ids)
        original_hand = list(player.hand_card_instance_ids)
        original_registry = json.loads(json.dumps(state.card_instances, ensure_ascii=False))

        record = _sample_record(self.card_instance)
        reference = self.card_instance.card_instance_to_object_reference(record)
        validation = self.card_instance.validate_card_instance_record(record)

        self.assertTrue(validation["valid"])
        self.assertEqual(reference["object_id"], record["card_instance_id"])
        self.assertEqual(state.state_version, original_state_version)
        self.assertEqual(state.event_log, original_event_log)
        self.assertEqual(session.get_action_response_history(), original_history)
        self.assertEqual(player.deck_card_instance_ids, original_deck)
        self.assertEqual(player.hand_card_instance_ids, original_hand)
        self.assertEqual(state.card_instances, original_registry)


if __name__ == "__main__":
    unittest.main()
