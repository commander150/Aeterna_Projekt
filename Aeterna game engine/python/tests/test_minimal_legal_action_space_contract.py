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


def _fake_ui_choose_from_action_space(action_space):
    return action_space["actions"][0]


def _fake_bot_choose_from_action_space(action_space):
    enabled_actions = [action for action in action_space["actions"] if action.get("enabled") is True]
    return sorted(enabled_actions, key=lambda action: action["action_id"])[0]


class TestMinimalLegalActionSpaceContract(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_get_action_space_returns_json_compatible_contract(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-ACTION-SPACE-TEST-001")

        action_space = session.get_action_space()

        json.dumps(action_space, ensure_ascii=False)
        self.assertEqual(action_space["schema_version"], "minimal-legal-action-space-v0")
        self.assertEqual(action_space["contract_type"], "legal_action_space")
        self.assertEqual(action_space["match_id"], state.match_id)
        self.assertEqual(action_space["player_id"], "P1")
        self.assertEqual(action_space["state_version"], 0)
        self.assertEqual(action_space["turn"], 1)
        self.assertEqual(action_space["phase"], "main")
        self.assertEqual(action_space["active_player_id"], "P1")
        self.assertEqual(action_space["priority_player_id"], "P1")
        self.assertGreaterEqual(action_space["enabled_action_count"], 1)
        self.assertEqual(action_space["disabled_action_count"], 0)
        self.assertEqual(action_space["metadata"]["rules_scope"], "minimal_end_turn_smoke")

        actions = action_space["actions"]
        self.assertGreaterEqual(len(actions), 1)
        end_turn = actions[0]
        self.assertEqual(end_turn["action_type"], "end_turn")
        self.assertTrue(end_turn["enabled"])
        self.assertIsNone(end_turn["disabled_reason"])
        self.assertIn("action_id", end_turn)
        self.assertIn("player_id", end_turn)
        self.assertEqual(end_turn["request_template"]["action_type"], "end_turn")
        self.assertEqual(end_turn["request_template"]["player_id"], "P1")
        self.assertEqual(end_turn["request_template"]["payload"], {})
        self.assertIn("action_id", end_turn["request_template"]["required_fields"])

    def test_inactive_player_action_space_reports_disabled_reason(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-ACTION-SPACE-DISABLED-TEST-001")

        action_space = session.get_action_space("P2")

        json.dumps(action_space, ensure_ascii=False)
        self.assertEqual(action_space["player_id"], "P2")
        self.assertEqual(action_space["enabled_action_count"], 0)
        self.assertEqual(action_space["disabled_action_count"], 1)
        self.assertFalse(action_space["actions"][0]["enabled"])
        self.assertEqual(action_space["actions"][0]["disabled_reason"], "not_active_player")

    def test_fake_ui_uses_action_space_then_step_response_contract(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-ACTION-SPACE-FAKE-UI-TEST-001")
        action_space = session.get_action_space()

        action = _fake_ui_choose_from_action_space(action_space)
        request = session.build_action_request(action)
        response = session.step(request)

        json.dumps(response, ensure_ascii=False)
        self.assertEqual(response["contract_type"], "action_response")
        self.assertEqual(response["response_type"], "minimal_action_response")
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(response["action_type"], "end_turn")
        self.assertEqual(response["new_event_sequences"], [1])

    def test_fake_bot_uses_action_space_then_step_response_contract(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-ACTION-SPACE-FAKE-BOT-TEST-001")
        action_space = session.get_action_space()

        action = _fake_bot_choose_from_action_space(action_space)
        request = session.build_action_request(action)
        response = session.step(request)

        json.dumps(response, ensure_ascii=False)
        self.assertEqual(response["contract_type"], "action_response")
        self.assertEqual(response["response_type"], "minimal_action_response")
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(response["action_type"], "end_turn")
        self.assertEqual(response["new_event_sequences"], [1])


if __name__ == "__main__":
    unittest.main()
