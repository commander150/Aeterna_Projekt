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
ENVIRONMENT_PATH = ENGINE_DIR / "minimal_engine_environment.py"
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


class TestMinimalEngineContextSummary(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.environment_module = _load_module("minimal_engine_environment", ENVIRONMENT_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_initial_context_summary_is_json_compatible_and_current(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-CONTEXT-SUMMARY-INITIAL-001")

        summary = session.get_engine_context_summary()
        roundtrip = json.loads(json.dumps(summary, ensure_ascii=False))

        self.assertEqual(roundtrip["schema_version"], "minimal-engine-context-summary-v0")
        self.assertEqual(roundtrip["contract_type"], "engine_context_summary")
        self.assertEqual(roundtrip["match_id"], state.match_id)
        self.assertEqual(roundtrip["state_version"], state.state_version)
        self.assertEqual(roundtrip["turn"], 1)
        self.assertEqual(roundtrip["phase"], "main")
        self.assertEqual(roundtrip["active_player_id"], "P1")
        self.assertEqual(roundtrip["priority_player_id"], "P1")
        self.assertEqual(roundtrip["expected_state_version"], state.state_version)
        self.assertEqual(roundtrip["event_count"], 0)
        self.assertIsNone(roundtrip["last_event_sequence"])
        self.assertEqual(roundtrip["response_count"], 0)
        self.assertEqual(roundtrip["accepted_response_count"], 0)
        self.assertEqual(roundtrip["rejected_response_count"], 0)
        self.assertEqual(roundtrip["enabled_action_count"], 2)
        self.assertEqual(roundtrip["disabled_action_count"], 0)
        self.assertTrue(roundtrip["metadata"]["expected_state_version_supported"])
        self.assertEqual(roundtrip["metadata"]["context_model"], "minimal")
        self.assertEqual(roundtrip["metadata"]["player_visible_snapshot_model"], "stable_minimal_v1")
        self.assertEqual(
            roundtrip["metadata"]["hidden_information_model"],
            "minimal_visibility_projection_v0",
        )

    def test_context_summary_read_is_read_only(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-CONTEXT-SUMMARY-READONLY-001")
        before_state_version = state.state_version
        before_event_count = len(session.get_event_log())
        before_history_count = len(session.get_action_response_history())

        summary = session.get_engine_context_summary()

        json.dumps(summary, ensure_ascii=False)
        self.assertEqual(state.state_version, before_state_version)
        self.assertEqual(len(session.get_event_log()), before_event_count)
        self.assertEqual(len(session.get_action_response_history()), before_history_count)

    def test_context_summary_updates_after_accepted_action(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-CONTEXT-SUMMARY-ACCEPTED-001")
        request = session.build_action_request(session.get_action_space()["actions"][0])

        response = session.step(request)
        summary = session.get_engine_context_summary()

        self.assertTrue(response["accepted"])
        self.assertEqual(state.state_version, 1)
        self.assertEqual(summary["state_version"], 1)
        self.assertEqual(summary["expected_state_version"], 1)
        self.assertEqual(summary["event_count"], 1)
        self.assertEqual(summary["last_event_sequence"], 1)
        self.assertEqual(summary["response_count"], 1)
        self.assertEqual(summary["accepted_response_count"], 1)
        self.assertEqual(summary["rejected_response_count"], 0)
        self.assertTrue(summary["last_response_accepted"])
        self.assertTrue(summary["last_response_success"])
        self.assertIsNone(summary["last_response_reason"])
        self.assertEqual(summary["enabled_action_count"], 2)

    def test_context_summary_updates_after_stale_rejected_action_without_events(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-CONTEXT-SUMMARY-STALE-001")
        request = session.build_action_request(session.get_action_space()["actions"][0])
        accepted = session.step(request)
        stale_request = dict(request)
        stale_request["request_id"] = "request:context-summary-stale"
        event_count_before = len(session.get_event_log())
        state_version_before = state.state_version

        rejected = session.step(stale_request)
        summary = session.get_engine_context_summary()

        self.assertTrue(accepted["accepted"])
        self.assertFalse(rejected["accepted"])
        self.assertEqual(rejected["reason"], "stale_state_version")
        self.assertEqual(state.state_version, state_version_before)
        self.assertEqual(len(session.get_event_log()), event_count_before)
        self.assertEqual(summary["state_version"], state_version_before)
        self.assertEqual(summary["event_count"], event_count_before)
        self.assertEqual(summary["last_event_sequence"], 1)
        self.assertEqual(summary["response_count"], 2)
        self.assertEqual(summary["accepted_response_count"], 1)
        self.assertEqual(summary["rejected_response_count"], 1)
        self.assertFalse(summary["last_response_accepted"])
        self.assertFalse(summary["last_response_success"])
        self.assertEqual(summary["last_response_reason"], "stale_state_version")

    def test_debug_export_contains_context_summary(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-CONTEXT-SUMMARY-EXPORT-001")

        exported = session.export_debug_session_state()

        json.dumps(exported, ensure_ascii=False)
        self.assertIn("engine_context_summary", exported)
        self.assertEqual(exported["engine_context_summary"]["contract_type"], "engine_context_summary")
        self.assertEqual(exported["engine_context_summary"]["state_version"], exported["transition_summary"]["state_version"])
        self.assertEqual(exported["engine_context_summary"]["expected_state_version"], exported["action_space"]["state_version"])

    def test_environment_observation_contains_context_summary(self):
        environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)

        observation = environment.reset(match_id="ENGINE-CONTEXT-SUMMARY-OBSERVATION-001")

        json.dumps(observation, ensure_ascii=False)
        self.assertIn("engine_context_summary", observation)
        self.assertEqual(observation["engine_context_summary"]["contract_type"], "engine_context_summary")
        self.assertEqual(observation["engine_context_summary"]["state_version"], observation["state_version"])
        self.assertEqual(observation["engine_context_summary"]["enabled_action_count"], 2)


if __name__ == "__main__":
    unittest.main()
