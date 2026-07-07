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


class TestMinimalEngineSession(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_session_resolves_end_turn_through_action_request_gate(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-SESSION-TEST-001")

        self.assertEqual(state.match_id, "ENGINE-SESSION-TEST-001")
        self.assertEqual(state.active_player_id, "P1")
        self.assertEqual(state.state_version, 0)
        self.assertEqual(session.get_diagnostics(), [])

        initial_snapshot = session.get_debug_snapshot()
        self.assertEqual(initial_snapshot["snapshot_type"], "debug_snapshot")
        self.assertEqual(initial_snapshot["visibility_mode"], "debug")
        self.assertEqual(initial_snapshot["match_id"], state.match_id)
        self.assertEqual(initial_snapshot["state_version"], 0)
        self.assertEqual(initial_snapshot["legal_action_summary"]["state_version"], 0)
        self.assertEqual(initial_snapshot["event_log_summary"]["event_count"], 0)
        self.assertIsNone(initial_snapshot["event_log_summary"]["last_event_sequence"])
        player_snapshot = session.get_player_snapshot("P1")
        self.assertIsNot(player_snapshot, initial_snapshot)
        self.assertEqual(player_snapshot["snapshot_type"], "player_visible_snapshot")
        self.assertEqual(player_snapshot["visibility_mode"], "player")
        self.assertEqual(player_snapshot["player_id"], "P1")
        self.assertEqual(player_snapshot["match_id"], state.match_id)
        self.assertEqual(player_snapshot["state_version"], 0)
        self.assertFalse(player_snapshot["metadata"]["debug_snapshot_source"])
        self.assertEqual(player_snapshot["metadata"]["hidden_information_model"], "not_implemented")
        self.assertNotIn("deck_id", player_snapshot["players"][0])

        legal_actions = session.list_legal_actions()
        self.assertEqual(len(legal_actions), 1)
        self.assertEqual(legal_actions[0]["action_type"], "end_turn")
        self.assertTrue(legal_actions[0]["enabled"])

        request = session.build_action_request(legal_actions[0])
        validation = session.validate_action_request(request)
        response = session.submit_action_request(request)

        self.assertTrue(validation["valid"])
        json.dumps(response, ensure_ascii=False)
        self.assertEqual(response["schema_version"], "minimal-action-response-v0")
        self.assertEqual(response["contract_type"], "action_response")
        self.assertEqual(response["response_type"], "minimal_action_response")
        self.assertEqual(response["match_id"], state.match_id)
        self.assertEqual(response["player_id"], "P1")
        self.assertEqual(response["action_id"], legal_actions[0]["action_id"])
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(response["action_type"], "end_turn")
        self.assertEqual(response["new_event_count"], 1)
        self.assertEqual(response["event_count"], 1)
        self.assertEqual(response["state_version_before"], 0)
        self.assertEqual(response["state_version_after"], 1)
        self.assertEqual(response["new_event_sequences"], [1])
        self.assertEqual(response["diagnostics"], [])
        self.assertEqual(response["diagnostics_summary"]["count"], 0)
        self.assertTrue(response["invariants_ok"])
        self.assertEqual(response["metadata"]["rules_scope"], "minimal_end_turn_smoke")
        self.assertEqual(session.get_last_action_response(), response)
        self.assertEqual(len(session.get_action_response_history()), 1)
        self.assertEqual(session.get_event_log()[0]["action_type"], "end_turn")
        self.assertEqual(session.get_event_log()[0]["event_sequence"], 1)
        self.assertEqual(session.get_event_log()[0]["state_version"], 1)
        self.assertEqual(state.active_player_id, "P2")
        self.assertEqual(state.state_version, 1)

        post_snapshot = session.get_debug_snapshot()
        self.assertEqual(post_snapshot["active_player_id"], "P2")
        self.assertEqual(post_snapshot["state_version"], 1)
        self.assertEqual(post_snapshot["legal_action_summary"]["state_version"], 1)
        self.assertEqual(post_snapshot["event_log_summary"]["event_count"], 1)
        self.assertEqual(post_snapshot["event_log_summary"]["last_event_type"], "action_resolved")
        self.assertEqual(post_snapshot["event_log_summary"]["last_event_sequence"], 1)
        post_player_snapshot = session.get_player_snapshot("P1")
        self.assertEqual(post_player_snapshot["snapshot_type"], "player_visible_snapshot")
        self.assertEqual(post_player_snapshot["active_player_id"], "P2")
        self.assertEqual(post_player_snapshot["state_version"], 1)
        self.assertEqual(post_player_snapshot["event_log_summary"]["event_count"], 1)
        self.assertEqual(post_player_snapshot["event_log_summary"]["last_event_sequence"], 1)
        self.assertEqual(post_player_snapshot["metadata"]["hidden_information_model"], "not_implemented")

        report = session.export_smoke_report()
        json.dumps(report, ensure_ascii=False)
        self.assertEqual(report["report_type"], "minimal_engine_session")
        self.assertIn("not a final Python-runtime decision", report["runtime_decision_note"])
        self.assertEqual(report["player_snapshot_summary"]["snapshot_type"], "player_visible_snapshot")
        self.assertEqual(report["player_snapshot_summary"]["hidden_information_model"], "not_implemented")
        self.assertEqual(report["match"]["state_version"], 1)
        self.assertEqual(report["events"]["event_count"], 1)
        self.assertEqual(report["events"]["last_event_sequence"], 1)
        self.assertEqual(report["diagnostics"]["count"], 0)
        self.assertEqual(report["response_history_count"], 1)
        self.assertEqual(report["transition_summary"]["contract_type"], "transition_summary")
        self.assertEqual(report["transition_summary"]["response_count"], 1)
        self.assertEqual(report["transition_summary"]["accepted_response_count"], 1)
        self.assertEqual(report["transition_summary"]["rejected_response_count"], 0)
        self.assertEqual(report["debug_session_state_summary"]["contract_type"], "debug_session_state")
        self.assertEqual(report["debug_session_state_summary"]["response_count"], 1)
        self.assertEqual(report["debug_session_state_summary"]["replay_support"], "not_implemented")

    def test_step_returns_same_action_response_contract(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-SESSION-STEP-TEST-001")
        request = session.build_action_request(session.list_legal_actions()[0])

        response = session.step(request)

        json.dumps(response, ensure_ascii=False)
        self.assertEqual(response["contract_type"], "action_response")
        self.assertEqual(response["response_type"], "minimal_action_response")
        self.assertEqual(response["match_id"], state.match_id)
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(response["state_version_before"], 0)
        self.assertEqual(response["state_version_after"], 1)
        self.assertEqual(response["new_event_count"], 1)
        self.assertEqual(response["new_event_sequences"], [1])
        self.assertEqual(response["events"][0]["event_sequence"], 1)

    def test_session_requires_create_match_before_use(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)

        with self.assertRaises(self.session_module.MinimalEngineSessionError):
            session.get_debug_snapshot()


if __name__ == "__main__":
    unittest.main()
