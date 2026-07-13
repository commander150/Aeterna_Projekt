import importlib
import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
ENGINE_EVENT_PATH = ENGINE_DIR / "engine_event.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_PYTHON_DIR), str(ENGINE_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestMinimalEngineEventEnvelope(unittest.TestCase):
    def setUp(self):
        self.engine_event = _load_module("engine_event", ENGINE_EVENT_PATH)

    def test_create_valid_event_deep_copies_payload_and_round_trips(self):
        payload = {
            "contract_type": "example_payload",
            "metadata": {"labels": ["draw", "zone_move"]},
            "items": [{"id": 1}],
        }
        original = deepcopy(payload)

        event = self.engine_event.create_engine_event_envelope(
            event_type="example_event",
            event_index=0,
            event_sequence=1,
            player_id="P1",
            action_type="example_action",
            turn_number=1,
            state_version=1,
            payload=payload,
        )
        roundtrip = json.loads(json.dumps(event, ensure_ascii=False))

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
        self.assertEqual(event["event_type"], "example_event")
        self.assertEqual(event["player_id"], "P1")
        self.assertEqual(event["action_type"], "example_action")
        self.assertEqual(event["turn_number"], 1)
        self.assertEqual(event["state_version"], 1)
        self.assertEqual(roundtrip, event)
        self.assertEqual(payload, original)
        self.assertIsNot(event["payload"], payload)
        self.assertIsNot(event["payload"]["metadata"], payload["metadata"])
        self.assertIsNot(event["payload"]["metadata"]["labels"], payload["metadata"]["labels"])
        self.assertIsNot(event["payload"]["items"], payload["items"])

        event["payload"]["metadata"]["labels"].append("mutated")
        event["payload"]["items"][0]["id"] = 99
        self.assertEqual(payload, original)

        validation = self.engine_event.validate_engine_event_envelope(event)
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["errors"], [])

    def test_optional_player_and_action_context_are_valid(self):
        event = _valid_event(self.engine_event)
        event["player_id"] = None
        event["action_type"] = None

        result = self.engine_event.validate_engine_event_envelope(event)

        self.assertTrue(result["valid"])

    def test_invalid_contract_and_missing_field_are_reported(self):
        invalid_contract = _valid_event(self.engine_event)
        invalid_contract["contract_type"] = "wrong_contract"
        missing_field = _valid_event(self.engine_event)
        missing_field.pop("player_id")

        contract_result = self.engine_event.validate_engine_event_envelope(invalid_contract)
        missing_result = self.engine_event.validate_engine_event_envelope(missing_field)

        self.assertIn("CONTRACT_TYPE_INVALID", _error_codes(contract_result))
        self.assertIn("FIELD_MISSING", _error_codes(missing_result))

    def test_empty_string_fields_are_reported(self):
        for field_name in ("schema_version", "event_type", "player_id", "action_type"):
            with self.subTest(field_name=field_name):
                event = _valid_event(self.engine_event)
                event[field_name] = "  "

                result = self.engine_event.validate_engine_event_envelope(event)

                self.assertIn("FIELD_EMPTY", _error_codes(result))

    def test_event_index_and_sequence_validation_rejects_bool(self):
        invalid_values = (
            ("event_index", -1, "EVENT_INDEX_INVALID"),
            ("event_index", True, "EVENT_INDEX_INVALID"),
            ("event_sequence", 0, "EVENT_SEQUENCE_INVALID"),
            ("event_sequence", True, "EVENT_SEQUENCE_INVALID"),
        )
        for field_name, value, expected_code in invalid_values:
            with self.subTest(field_name=field_name, value=value):
                event = _valid_event(self.engine_event)
                event[field_name] = value

                result = self.engine_event.validate_engine_event_envelope(event)

                self.assertIn(expected_code, _error_codes(result))

    def test_turn_state_and_payload_validation(self):
        invalid_values = (
            ("turn_number", 0, "TURN_NUMBER_INVALID"),
            ("turn_number", True, "TURN_NUMBER_INVALID"),
            ("state_version", 0, "STATE_VERSION_INVALID"),
            ("state_version", True, "STATE_VERSION_INVALID"),
            ("payload", [], "PAYLOAD_INVALID"),
        )
        for field_name, value, expected_code in invalid_values:
            with self.subTest(field_name=field_name, value=value):
                event = _valid_event(self.engine_event)
                event[field_name] = value

                result = self.engine_event.validate_engine_event_envelope(event)

                self.assertIn(expected_code, _error_codes(result))

    def test_non_dict_input_returns_structured_errors_without_exception(self):
        for invalid in (None, [], "event"):
            with self.subTest(invalid=invalid):
                result = self.engine_event.validate_engine_event_envelope(invalid)

                json.dumps(result, ensure_ascii=False)
                self.assertFalse(result["valid"])
                self.assertIn("RECORD_NOT_DICT", _error_codes(result))
                self.assertIn("FIELD_MISSING", _error_codes(result))

    def test_helper_imports_from_engine_namespace(self):
        imported = importlib.import_module("engine.engine_event")

        self.assertTrue(callable(imported.create_engine_event_envelope))
        self.assertTrue(callable(imported.validate_engine_event_envelope))


def _valid_event(engine_event):
    return engine_event.create_engine_event_envelope(
        event_type="example_event",
        event_index=0,
        event_sequence=1,
        player_id="P1",
        action_type="example_action",
        turn_number=1,
        state_version=1,
        payload={"value": "example"},
    )


def _error_codes(result):
    return {error["code"] for error in result["errors"]}


if __name__ == "__main__":
    unittest.main()
