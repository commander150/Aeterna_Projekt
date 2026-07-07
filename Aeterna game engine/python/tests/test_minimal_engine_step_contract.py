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


def _fake_ui_submit_first_action(session):
    action_space = session.get_action_space()
    request = session.build_action_request(action_space["actions"][0])
    return session.step(request)


def _fake_bot_submit_first_action(session):
    action_space = session.get_action_space()
    enabled_actions = [action for action in action_space["actions"] if action.get("enabled") is True]
    request = session.build_action_request(enabled_actions[0])
    return session.step(request)


class TestMinimalEngineStepContract(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_step_returns_json_compatible_action_response_contract(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-STEP-CONTRACT-TEST-001")
        legal_actions = session.list_legal_actions()
        request = session.build_action_request(legal_actions[0])

        response = session.step(request)

        self.assertIsInstance(response, dict)
        json.dumps(response, ensure_ascii=False)
        self.assertEqual(response["schema_version"], "minimal-action-response-v0")
        self.assertEqual(response["contract_type"], "action_response")
        self.assertEqual(response["response_type"], "minimal_action_response")
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(response["action_type"], "end_turn")
        self.assertEqual(response["state_version_before"], 0)
        self.assertEqual(response["state_version_after"], 1)
        self.assertGreaterEqual(response["new_event_count"], 1)
        self.assertEqual(response["new_event_sequences"], [1])
        self.assertEqual(response["events"][0]["event_sequence"], 1)
        self.assertTrue(response["invariants_ok"])

    def test_fake_ui_uses_the_same_step_response_contract(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-STEP-FAKE-UI-TEST-001")

        response = _fake_ui_submit_first_action(session)

        json.dumps(response, ensure_ascii=False)
        self.assertEqual(response["contract_type"], "action_response")
        self.assertEqual(response["response_type"], "minimal_action_response")
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(response["action_type"], "end_turn")
        self.assertEqual(response["new_event_sequences"], [1])

    def test_fake_bot_uses_the_same_step_response_contract(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-STEP-FAKE-BOT-TEST-001")

        response = _fake_bot_submit_first_action(session)

        json.dumps(response, ensure_ascii=False)
        self.assertEqual(response["contract_type"], "action_response")
        self.assertEqual(response["response_type"], "minimal_action_response")
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(response["action_type"], "end_turn")
        self.assertEqual(response["new_event_sequences"], [1])


if __name__ == "__main__":
    unittest.main()
