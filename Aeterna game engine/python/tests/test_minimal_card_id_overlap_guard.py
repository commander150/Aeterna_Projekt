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


class TestMinimalCardIdOverlapGuard(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_draw_precondition_and_action_space_report_overlap_risk(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-CARD-ID-OVERLAP-GUARD-TEST-001")
        player = state.get_player("P1")
        player.deck_card_ids = ["DUPLICATE-CARD-ID", "DUPLICATE-CARD-ID"]
        original_deck = list(player.deck_card_ids)
        original_hand = list(player.hand)
        original_events = list(state.event_log)
        original_state_version = state.state_version

        precondition = session.get_draw_precondition("P1")
        action_space = session.get_action_space()
        draw_action = _find_action(action_space, "draw_card")
        response = session.step(session.build_action_request(draw_action))
        debug_snapshot = session.get_debug_snapshot()
        debug_export = session.export_debug_session_state()

        json.dumps(precondition, ensure_ascii=False)
        json.dumps(action_space, ensure_ascii=False)
        json.dumps(response, ensure_ascii=False)
        json.dumps(debug_export, ensure_ascii=False)

        self.assertFalse(precondition["can_draw"])
        self.assertEqual(precondition["reason"], "minimal_card_id_overlap_risk")
        self.assertEqual(precondition["deck_count"], 2)
        self.assertEqual(precondition["hand_count"], 0)
        self.assertEqual(precondition["metadata"]["card_instance_model"], "not_implemented")
        self.assertTrue(precondition["metadata"]["card_id_overlap_guard"])

        self.assertFalse(draw_action["enabled"])
        self.assertEqual(draw_action["disabled_reason"], "minimal_card_id_overlap_risk")
        self.assertFalse(response["accepted"])
        self.assertFalse(response["success"])
        self.assertEqual(response["reason"], "minimal_card_id_overlap_risk")
        self.assertEqual(response["state_version_before"], original_state_version)
        self.assertEqual(response["state_version_after"], original_state_version)
        self.assertEqual(response["new_event_count"], 0)
        self.assertEqual(response["new_event_sequences"], [])

        self.assertEqual(player.deck_card_ids, original_deck)
        self.assertEqual(player.hand, original_hand)
        self.assertEqual(state.event_log, original_events)
        self.assertEqual(state.state_version, original_state_version)

        self.assertEqual(
            debug_snapshot["players"][0]["zone_summary"]["draw_precondition"]["reason"],
            "minimal_card_id_overlap_risk",
        )
        self.assertFalse(debug_snapshot["diagnostics_summary"]["draw_preconditions_ok"])
        self.assertEqual(debug_snapshot["metadata"]["card_instance_model"], "not_implemented")
        self.assertTrue(debug_snapshot["metadata"]["card_id_overlap_guard"])
        self.assertEqual(debug_export["debug_snapshot"]["metadata"]["card_instance_model"], "not_implemented")
        self.assertTrue(debug_export["debug_snapshot"]["metadata"]["card_id_overlap_guard"])

    def test_empty_deck_reason_stays_deck_empty(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-CARD-ID-OVERLAP-GUARD-EMPTY-DECK-TEST-001")
        player = state.get_player("P1")
        player.deck_card_ids = []

        precondition = session.get_draw_precondition("P1")
        draw_action = _find_action(session.get_action_space(), "draw_card")

        self.assertFalse(precondition["can_draw"])
        self.assertEqual(precondition["reason"], "deck_empty")
        self.assertFalse(draw_action["enabled"])
        self.assertEqual(draw_action["disabled_reason"], "deck_empty")


def _find_action(action_space, action_type):
    matches = [action for action in action_space["actions"] if action["action_type"] == action_type]
    if not matches:
        raise AssertionError("Missing action_type in action space: %s" % action_type)
    return matches[0]


if __name__ == "__main__":
    unittest.main()
