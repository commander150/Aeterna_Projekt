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


class TestMinimalRejectedActionResponseContract(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_unknown_action_id_returns_rejected_response_without_state_change(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-REJECTED-ACTION-TEST-001")
        event_count_before = len(session.get_event_log())
        state_version_before = state.state_version
        request = {
            "request_id": "request:unknown-action",
            "match_id": state.match_id,
            "player_id": "P1",
            "action_id": "missing-action",
            "action_type": "end_turn",
        }

        response = session.step(request)

        self._assert_rejected_contract(response, reason="unknown_action_id")
        self.assertEqual(response["state_version_before"], state_version_before)
        self.assertEqual(response["state_version_after"], state_version_before)
        self.assertEqual(state.state_version, state_version_before)
        self.assertEqual(len(session.get_event_log()), event_count_before)
        self.assertEqual(state.active_player_id, "P1")

        valid_request = session.build_action_request(session.get_action_space()["actions"][0])
        valid_response = session.step(valid_request)
        self.assertTrue(valid_response["accepted"])
        self.assertTrue(valid_response["success"])
        self.assertEqual(valid_response["state_version_before"], 0)
        self.assertEqual(valid_response["state_version_after"], 1)
        self.assertEqual(valid_response["new_event_sequences"], [1])

    def test_wrong_player_returns_rejected_response_without_state_change(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-REJECTED-WRONG-PLAYER-TEST-001")
        action = session.get_action_space()["actions"][0]
        request = {
            "request_id": "request:wrong-player",
            "match_id": state.match_id,
            "player_id": "P2",
            "action_id": action["action_id"],
            "action_type": action["action_type"],
        }

        response = session.step(request)

        self._assert_rejected_contract(response, reason="player_not_active")
        self.assertEqual(response["state_version_before"], 0)
        self.assertEqual(response["state_version_after"], 0)
        self.assertEqual(state.state_version, 0)
        self.assertEqual(session.get_event_log(), [])

    def _assert_rejected_contract(self, response, reason):
        self.assertIsInstance(response, dict)
        json.dumps(response, ensure_ascii=False)
        self.assertEqual(response["schema_version"], "minimal-action-response-v0")
        self.assertEqual(response["contract_type"], "action_response")
        self.assertEqual(response["response_type"], "minimal_action_response")
        self.assertFalse(response["accepted"])
        self.assertFalse(response["success"])
        self.assertEqual(response["reason"], reason)
        self.assertEqual(response["new_event_count"], 0)
        self.assertEqual(response["event_count"], 0)
        self.assertEqual(response["new_event_sequences"], [])
        self.assertEqual(response["events"], [])
        self.assertEqual(response["diagnostics_summary"]["count"], 0)
        self.assertTrue(response["invariants_ok"])


if __name__ == "__main__":
    unittest.main()
