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


class TestMinimalDebugSessionExport(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_initial_debug_session_export_is_json_compatible(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-DEBUG-EXPORT-INITIAL-TEST-001")

        exported = session.export_debug_session_state()

        json.dumps(exported, ensure_ascii=False)
        self.assertEqual(exported["schema_version"], "minimal-debug-session-state-v0")
        self.assertEqual(exported["contract_type"], "debug_session_state")
        self.assertEqual(exported["match_id"], state.match_id)
        self.assertEqual(exported["debug_snapshot"]["snapshot_type"], "debug_snapshot")
        self.assertEqual(exported["action_space"]["contract_type"], "legal_action_space")
        self.assertEqual(exported["transition_summary"]["contract_type"], "transition_summary")
        self.assertEqual(
            exported["engine_context_summary"]["metadata"]["player_visible_snapshot_model"],
            "stable_minimal_v2",
        )
        self.assertEqual(
            exported["engine_context_summary"]["metadata"]["board_model"],
            "minimal-public-domain-board-v0",
        )
        self.assertEqual(
            exported["engine_context_summary"]["metadata"]["hidden_information_model"],
            "minimal_visibility_projection_v0",
        )
        self.assertIsNone(exported["last_action_response"])
        self.assertEqual(exported["transition_summary"]["response_count"], 0)
        self.assertEqual(exported["transition_summary"]["event_count"], 0)
        self.assertEqual(exported["diagnostics_summary"]["count"], 0)
        self.assertEqual(exported["metadata"]["rules_scope"], "minimal_end_turn_smoke")
        self.assertEqual(exported["metadata"]["runtime_decision"], "not_final")
        self.assertEqual(exported["metadata"]["replay_support"], "not_implemented")
        self.assertTrue(exported["metadata"]["replay_future_candidate"])

    def test_accepted_action_updates_debug_session_export(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-DEBUG-EXPORT-ACCEPTED-TEST-001")
        request = session.build_action_request(session.get_action_space()["actions"][0])
        session.step(request)

        exported = session.export_debug_session_state()

        json.dumps(exported, ensure_ascii=False)
        self.assertEqual(exported["debug_snapshot"]["state_version"], 1)
        self.assertEqual(exported["action_space"]["state_version"], 1)
        self.assertEqual(exported["transition_summary"]["state_version"], 1)
        self.assertEqual(exported["transition_summary"]["response_count"], 1)
        self.assertEqual(exported["transition_summary"]["event_count"], 1)
        self.assertEqual(exported["transition_summary"]["accepted_response_count"], 1)
        self.assertEqual(exported["transition_summary"]["rejected_response_count"], 0)
        self.assertTrue(exported["last_action_response"]["accepted"])
        self.assertEqual(exported["last_action_response"]["new_event_sequences"], [1])

    def test_rejected_action_updates_debug_session_export_without_state_change(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-DEBUG-EXPORT-REJECTED-TEST-001")
        session.step(
            {
                "request_id": "request:debug-export-rejected",
                "match_id": state.match_id,
                "player_id": "P1",
                "action_id": "missing-action",
                "action_type": "end_turn",
            }
        )

        exported = session.export_debug_session_state()

        json.dumps(exported, ensure_ascii=False)
        self.assertEqual(exported["debug_snapshot"]["state_version"], 0)
        self.assertEqual(exported["action_space"]["state_version"], 0)
        self.assertEqual(exported["transition_summary"]["state_version"], 0)
        self.assertEqual(exported["transition_summary"]["response_count"], 1)
        self.assertEqual(exported["transition_summary"]["event_count"], 0)
        self.assertEqual(exported["transition_summary"]["accepted_response_count"], 0)
        self.assertEqual(exported["transition_summary"]["rejected_response_count"], 1)
        self.assertFalse(exported["last_action_response"]["accepted"])
        self.assertEqual(exported["last_action_response"]["reason"], "unknown_action_id")

    def test_debug_session_export_does_not_expose_internal_state(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-DEBUG-EXPORT-MUTATION-TEST-001")

        exported = session.export_debug_session_state()
        exported["transition_summary"]["response_count"] = 999
        exported["metadata"]["replay_support"] = "mutated_outside"

        fresh_export = session.export_debug_session_state()
        self.assertEqual(fresh_export["transition_summary"]["response_count"], 0)
        self.assertEqual(fresh_export["metadata"]["replay_support"], "not_implemented")


if __name__ == "__main__":
    unittest.main()
