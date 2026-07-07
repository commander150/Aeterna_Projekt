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


class TestMinimalDrawPreconditions(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_initial_draw_precondition_is_visible_and_read_only(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-DRAW-PRECONDITION-TEST-001")
        player = state.get_player("P1")
        original_deck = list(player.deck_card_ids)
        original_hand = list(player.hand)
        original_events = list(state.event_log)
        original_state_version = state.state_version

        precondition = session.get_draw_precondition("P1")

        json.dumps(precondition, ensure_ascii=False)
        self.assertEqual(precondition["player_id"], "P1")
        self.assertTrue(precondition["can_draw"])
        self.assertEqual(precondition["reason"], "ok")
        self.assertEqual(precondition["deck_count"], len(original_deck))
        self.assertEqual(precondition["hand_count"], len(original_hand))
        self.assertEqual(precondition["metadata"]["rules_scope"], "minimal_end_turn_smoke")
        self.assertEqual(player.deck_card_ids, original_deck)
        self.assertEqual(player.hand, original_hand)
        self.assertEqual(state.event_log, original_events)
        self.assertEqual(state.state_version, original_state_version)

        debug_snapshot = session.get_debug_snapshot()
        player_snapshot = session.get_player_snapshot("P1")
        debug_export = session.export_debug_session_state()
        self.assertTrue(debug_snapshot["diagnostics_summary"]["draw_preconditions_ok"])
        self.assertTrue(player_snapshot["diagnostics_summary"]["draw_preconditions_ok"])
        self.assertTrue(debug_export["debug_snapshot"]["diagnostics_summary"]["draw_preconditions_ok"])
        self.assertEqual(debug_snapshot["players"][0]["zone_summary"]["draw_precondition"]["reason"], "ok")
        self.assertEqual(player_snapshot["players"][0]["zone_summary"]["draw_precondition"]["reason"], "ok")
        self.assertEqual(player_snapshot["metadata"]["hidden_information_model"], "not_implemented")

    def test_draw_precondition_does_not_create_draw_action(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-DRAW-PRECONDITION-ACTION-SPACE-TEST-001")

        session.get_draw_precondition("P1")
        action_types = [action["action_type"] for action in session.get_action_space()["actions"]]

        self.assertEqual(action_types, ["end_turn"])
        self.assertNotIn("draw", action_types)

    def test_draw_precondition_remains_available_after_end_turn(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-DRAW-PRECONDITION-END-TURN-TEST-001")
        request = session.build_action_request(session.get_action_space()["actions"][0])
        response = session.step(request)

        self.assertTrue(response["accepted"])
        for player_id in ("P1", "P2"):
            precondition = session.get_draw_precondition(player_id)
            json.dumps(precondition, ensure_ascii=False)
            self.assertTrue(precondition["can_draw"])
            self.assertEqual(precondition["reason"], "ok")

        action_types = [action["action_type"] for action in session.get_action_space()["actions"]]
        self.assertEqual(action_types, ["end_turn"])
        self.assertNotIn("draw", action_types)

    def test_empty_deck_precondition_reports_deck_empty_without_state_mutation(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-DRAW-PRECONDITION-EMPTY-DECK-TEST-001")
        player = state.get_player("P1")
        player.deck_card_ids = []
        original_hand = list(player.hand)
        original_events = list(state.event_log)
        original_state_version = state.state_version

        precondition = session.get_draw_precondition("P1")

        self.assertFalse(precondition["can_draw"])
        self.assertEqual(precondition["reason"], "deck_empty")
        self.assertEqual(precondition["deck_count"], 0)
        self.assertEqual(precondition["hand_count"], len(original_hand))
        self.assertEqual(player.hand, original_hand)
        self.assertEqual(state.event_log, original_events)
        self.assertEqual(state.state_version, original_state_version)
        self.assertFalse(session.get_debug_snapshot()["diagnostics_summary"]["draw_preconditions_ok"])

    def test_unknown_player_precondition_is_explicit(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-DRAW-PRECONDITION-UNKNOWN-PLAYER-TEST-001")

        precondition = session.get_draw_precondition("PX")

        self.assertEqual(precondition["player_id"], "PX")
        self.assertFalse(precondition["can_draw"])
        self.assertEqual(precondition["reason"], "player_unknown")
        self.assertEqual(precondition["deck_count"], 0)
        self.assertEqual(precondition["hand_count"], 0)


if __name__ == "__main__":
    unittest.main()
