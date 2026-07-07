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


class TestMinimalSessionResponseHistory(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_response_history_tracks_rejected_then_accepted_contracts(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-RESPONSE-HISTORY-TEST-001")

        self.assertIsNone(session.get_last_action_response())
        self.assertEqual(session.get_action_response_history(), [])

        rejected_request = {
            "request_id": "request:history-rejected",
            "match_id": state.match_id,
            "player_id": "P1",
            "action_id": "missing-action",
            "action_type": "end_turn",
        }
        rejected = session.step(rejected_request)

        json.dumps(rejected, ensure_ascii=False)
        self.assertFalse(rejected["accepted"])
        self.assertFalse(rejected["success"])
        self.assertEqual(rejected["reason"], "unknown_action_id")
        self.assertEqual(rejected["state_version_before"], 0)
        self.assertEqual(rejected["state_version_after"], 0)
        self.assertEqual(rejected["new_event_count"], 0)
        self.assertEqual(rejected["new_event_sequences"], [])
        self.assertEqual(session.get_event_log(), [])

        valid_request = session.build_action_request(session.get_action_space()["actions"][0])
        accepted = session.step(valid_request)

        json.dumps(accepted, ensure_ascii=False)
        self.assertTrue(accepted["accepted"])
        self.assertTrue(accepted["success"])
        self.assertEqual(accepted["state_version_before"], 0)
        self.assertEqual(accepted["state_version_after"], 1)
        self.assertEqual(accepted["new_event_sequences"], [1])

        history = session.get_action_response_history()
        json.dumps(history, ensure_ascii=False)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["contract_type"], "action_response")
        self.assertEqual(history[0]["reason"], "unknown_action_id")
        self.assertFalse(history[0]["accepted"])
        self.assertTrue(history[1]["accepted"])
        self.assertEqual(history[1]["new_event_sequences"], [1])

        last = session.get_last_action_response()
        json.dumps(last, ensure_ascii=False)
        self.assertEqual(last, history[1])
        self.assertTrue(last["accepted"])

    def test_response_history_accessors_do_not_expose_internal_list(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-RESPONSE-HISTORY-COPY-TEST-001")
        rejected_request = {
            "request_id": "request:copy-test",
            "match_id": state.match_id,
            "player_id": "P1",
            "action_id": "missing-action",
            "action_type": "end_turn",
        }
        session.step(rejected_request)

        external_history = session.get_action_response_history()
        external_history.append({"contract_type": "external_mutation"})
        external_history[0]["reason"] = "mutated_outside"
        external_last = session.get_last_action_response()
        external_last["reason"] = "last_mutated_outside"

        internal_history = session.get_action_response_history()
        self.assertEqual(len(internal_history), 1)
        self.assertEqual(internal_history[0]["reason"], "unknown_action_id")
        self.assertEqual(session.get_last_action_response()["reason"], "unknown_action_id")

    def test_create_match_resets_response_history(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-RESPONSE-HISTORY-RESET-TEST-001")
        session.step(
            {
                "request_id": "request:before-reset",
                "match_id": state.match_id,
                "player_id": "P1",
                "action_id": "missing-action",
                "action_type": "end_turn",
            }
        )
        self.assertEqual(len(session.get_action_response_history()), 1)

        session.create_match(match_id="ENGINE-RESPONSE-HISTORY-RESET-TEST-002")

        self.assertIsNone(session.get_last_action_response())
        self.assertEqual(session.get_action_response_history(), [])


if __name__ == "__main__":
    unittest.main()
