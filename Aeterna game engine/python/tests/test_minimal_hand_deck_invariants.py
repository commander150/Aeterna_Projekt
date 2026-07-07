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
INVARIANTS_PATH = AI_VS_AI_DIR / "state_invariants.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestMinimalHandDeckInvariants(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_initial_state_has_minimal_hand_deck_zone_contract(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-HAND-DECK-INVARIANTS-TEST-001")

        for player in state.players:
            self.assertIsInstance(player.deck_card_ids, list)
            self.assertIsInstance(player.hand, list)
            self.assertIsInstance(player.discard, list)
            self.assertGreater(len(player.deck_card_ids), 0)
            self.assertEqual(len(player.hand), 0)
            self.assertEqual(len(player.discard), 0)
            self.assertEqual(set(player.deck_card_ids).intersection(set(player.hand)), set())

        self.assertEqual(session.get_diagnostics(), [])
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])

    def test_snapshots_and_debug_export_include_zone_summaries(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-HAND-DECK-SNAPSHOT-TEST-001")

        debug_snapshot = session.get_debug_snapshot()
        player_snapshot = session.get_player_snapshot("P1")
        debug_export = session.export_debug_session_state()

        json.dumps(debug_snapshot, ensure_ascii=False)
        json.dumps(player_snapshot, ensure_ascii=False)
        json.dumps(debug_export, ensure_ascii=False)
        self.assertTrue(debug_snapshot["diagnostics_summary"]["hand_deck_invariants_ok"])
        self.assertTrue(player_snapshot["diagnostics_summary"]["hand_deck_invariants_ok"])
        self.assertGreater(debug_snapshot["players"][0]["zone_summary"]["deck_count"], 0)
        self.assertEqual(debug_snapshot["players"][0]["zone_summary"]["hand_count"], 0)
        self.assertGreater(player_snapshot["players"][0]["zone_summary"]["deck_count"], 0)
        self.assertEqual(player_snapshot["players"][0]["zone_summary"]["hand_count"], 0)
        self.assertEqual(player_snapshot["metadata"]["hidden_information_model"], "not_implemented")
        self.assertTrue(debug_export["debug_snapshot"]["diagnostics_summary"]["hand_deck_invariants_ok"])

    def test_end_turn_keeps_hand_deck_invariants_and_action_space_minimal(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id="ENGINE-HAND-DECK-END-TURN-TEST-001")

        action_space = session.get_action_space()
        action_types = [action["action_type"] for action in action_space["actions"]]
        self.assertEqual(action_types, ["end_turn", "draw_card"])

        request = session.build_action_request(action_space["actions"][0])
        response = session.step(request)

        self.assertTrue(response["accepted"])
        self.assertEqual(session.get_diagnostics(), [])
        post_snapshot = session.get_debug_snapshot()
        self.assertTrue(post_snapshot["diagnostics_summary"]["hand_deck_invariants_ok"])
        post_action_types = [action["action_type"] for action in session.get_action_space()["actions"]]
        self.assertEqual(post_action_types, ["end_turn", "draw_card"])


if __name__ == "__main__":
    unittest.main()
