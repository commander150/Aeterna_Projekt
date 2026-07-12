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


class TestMinimalExpectedStateVersionGuard(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_matching_expected_state_version_allows_step(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-EXPECTED-VERSION-MATCH-001")
        action = session.get_action_space()["actions"][0]
        request = session.build_action_request(action)

        self.assertEqual(request["expected_state_version"], 0)
        response = session.step(request)

        json.dumps(response, ensure_ascii=False)
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(response["reason"], None)
        self.assertEqual(response["state_version_before"], 0)
        self.assertEqual(response["state_version_after"], 1)
        self.assertEqual(response["new_event_sequences"], [1])
        self.assertEqual(state.state_version, 1)

    def test_stale_expected_state_version_rejects_without_mutation(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-EXPECTED-VERSION-STALE-001")
        request = session.build_action_request(session.get_action_space()["actions"][0])
        accepted = session.step(request)
        self.assertTrue(accepted["accepted"])
        self.assertEqual(state.state_version, 1)

        stale_request = dict(request)
        stale_request["request_id"] = "request:stale-version"
        event_count_before = len(session.get_event_log())
        response = session.step(stale_request)

        json.dumps(response, ensure_ascii=False)
        self.assertFalse(response["accepted"])
        self.assertFalse(response["success"])
        self.assertEqual(response["reason"], "stale_state_version")
        self.assertEqual(response["state_version_before"], 1)
        self.assertEqual(response["state_version_after"], 1)
        self.assertEqual(response["new_event_count"], 0)
        self.assertEqual(response["event_count"], 0)
        self.assertEqual(response["new_event_sequences"], [])
        self.assertEqual(response["events"], [])
        self.assertTrue(response["invariants_ok"])
        self.assertEqual(state.state_version, 1)
        self.assertEqual(len(session.get_event_log()), event_count_before)
        self.assertEqual(state.active_player_id, "P2")

    def test_stale_rejection_is_recorded_in_response_history(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-EXPECTED-VERSION-HISTORY-001")
        action = session.get_action_space()["actions"][0]
        stale_request = session.build_action_request(action)
        stale_request["expected_state_version"] = state.state_version + 1

        response = session.step(stale_request)
        history = session.get_action_response_history()

        self.assertFalse(response["accepted"])
        self.assertEqual(response["reason"], "stale_state_version")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], response)
        self.assertEqual(session.get_event_log(), [])

    def test_action_space_request_templates_include_current_state_version(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-EXPECTED-VERSION-ACTION-SPACE-001")

        initial_space = session.get_action_space()
        json.dumps(initial_space, ensure_ascii=False)
        self.assertEqual(initial_space["state_version"], 0)
        self.assertTrue(
            all(action["request_template"]["expected_state_version"] == 0 for action in initial_space["actions"])
        )

        response = session.step(session.build_action_request(initial_space["actions"][0]))
        self.assertTrue(response["accepted"])

        next_space = session.get_action_space()
        json.dumps(next_space, ensure_ascii=False)
        self.assertEqual(next_space["state_version"], 1)
        self.assertTrue(all(action["request_template"]["expected_state_version"] == 1 for action in next_space["actions"]))

    def test_request_without_expected_state_version_keeps_existing_behavior(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-EXPECTED-VERSION-ABSENT-001")
        action = session.get_action_space()["actions"][0]
        request = {
            "request_id": "request:no-expected-state-version",
            "match_id": state.match_id,
            "player_id": "P1",
            "action_id": action["action_id"],
            "action_type": action["action_type"],
        }

        response = session.step(request)

        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(response["state_version_before"], 0)
        self.assertEqual(response["state_version_after"], 1)
        self.assertEqual(response["new_event_sequences"], [1])


if __name__ == "__main__":
    unittest.main()
