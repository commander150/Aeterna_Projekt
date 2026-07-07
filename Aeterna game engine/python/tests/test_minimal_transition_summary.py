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


class TestMinimalTransitionSummary(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_transition_summary_counts_initial_rejected_and_accepted_paths(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-TRANSITION-SUMMARY-TEST-001")

        initial = session.get_transition_summary()
        json.dumps(initial, ensure_ascii=False)
        self.assertEqual(initial["schema_version"], "minimal-transition-summary-v0")
        self.assertEqual(initial["contract_type"], "transition_summary")
        self.assertEqual(initial["match_id"], state.match_id)
        self.assertEqual(initial["state_version"], 0)
        self.assertEqual(initial["turn"], 1)
        self.assertEqual(initial["phase"], "main")
        self.assertEqual(initial["active_player_id"], "P1")
        self.assertEqual(initial["priority_player_id"], "P1")
        self.assertEqual(initial["event_count"], 0)
        self.assertIsNone(initial["last_event_sequence"])
        self.assertEqual(initial["response_count"], 0)
        self.assertEqual(initial["accepted_response_count"], 0)
        self.assertEqual(initial["rejected_response_count"], 0)
        self.assertIsNone(initial["last_response_type"])
        self.assertIsNone(initial["last_response_accepted"])
        self.assertIsNone(initial["last_response_success"])
        self.assertIsNone(initial["last_response_reason"])

        session.step(
            {
                "request_id": "request:transition-rejected",
                "match_id": state.match_id,
                "player_id": "P1",
                "action_id": "missing-action",
                "action_type": "end_turn",
            }
        )

        rejected = session.get_transition_summary()
        json.dumps(rejected, ensure_ascii=False)
        self.assertEqual(rejected["state_version"], 0)
        self.assertEqual(rejected["event_count"], 0)
        self.assertIsNone(rejected["last_event_sequence"])
        self.assertEqual(rejected["response_count"], 1)
        self.assertEqual(rejected["accepted_response_count"], 0)
        self.assertEqual(rejected["rejected_response_count"], 1)
        self.assertEqual(rejected["last_response_type"], "minimal_action_response")
        self.assertFalse(rejected["last_response_accepted"])
        self.assertFalse(rejected["last_response_success"])
        self.assertEqual(rejected["last_response_reason"], "unknown_action_id")

        valid_request = session.build_action_request(session.get_action_space()["actions"][0])
        session.step(valid_request)

        accepted = session.get_transition_summary()
        json.dumps(accepted, ensure_ascii=False)
        self.assertEqual(accepted["state_version"], 1)
        self.assertEqual(accepted["event_count"], 1)
        self.assertEqual(accepted["last_event_sequence"], 1)
        self.assertEqual(accepted["response_count"], 2)
        self.assertEqual(accepted["accepted_response_count"], 1)
        self.assertEqual(accepted["rejected_response_count"], 1)
        self.assertEqual(accepted["last_response_type"], "minimal_action_response")
        self.assertTrue(accepted["last_response_accepted"])
        self.assertTrue(accepted["last_response_success"])
        self.assertIsNone(accepted["last_response_reason"])

    def test_transition_summary_is_new_dict_each_time(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-TRANSITION-SUMMARY-MUTATION-TEST-001")

        external_summary = session.get_transition_summary()
        external_summary["response_count"] = 999
        external_summary["metadata"]["rules_scope"] = "mutated_outside"

        internal_summary = session.get_transition_summary()
        self.assertEqual(internal_summary["response_count"], 0)
        self.assertEqual(internal_summary["metadata"]["rules_scope"], "minimal_end_turn_smoke")


if __name__ == "__main__":
    unittest.main()
