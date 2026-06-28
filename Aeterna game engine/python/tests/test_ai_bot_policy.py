import importlib.util
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
BOT_POLICY_PATH = AI_VS_AI_DIR / "bot_policy.py"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"
KERNEL_PATH = AI_VS_AI_DIR / "rules_kernel.py"


def _load_module(module_name, path):
    ai_vs_ai_dir = str(AI_VS_AI_DIR)
    if ai_vs_ai_dir not in sys.path:
        sys.path.insert(0, ai_vs_ai_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestAIBotPolicy(unittest.TestCase):
    def setUp(self):
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.kernel = _load_module("rules_kernel", KERNEL_PATH)
        self.policy = _load_module("bot_policy", BOT_POLICY_PATH)

    def test_chooses_active_player_enabled_end_turn_from_rules_kernel_actions(self):
        runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        deck_id_a, deck_id_b = _pick_two_decks(runtime_package)
        state = self.kernel.create_initial_match_state(runtime_package, deck_id_a, deck_id_b)
        legal_actions = self.kernel.list_legal_actions(state, "P1")

        chosen = self.policy.choose_action(legal_actions, "P1")

        self.assertEqual(chosen["action_type"], "end_turn")
        self.assertEqual(chosen["player_id"], "P1")
        self.assertTrue(chosen["enabled"])
        self.assertEqual(state.active_player_id, "P1")
        self.assertEqual(state.event_log, [])

    def test_does_not_choose_disabled_action(self):
        legal_actions = [
            {"action_id": "end_turn:P1", "action_type": "end_turn", "player_id": "P1", "enabled": False}
        ]

        with self.assertRaisesRegex(self.policy.BotPolicyError, "No enabled legal action"):
            self.policy.choose_action(legal_actions, "P1")

    def test_does_not_choose_other_players_action(self):
        legal_actions = [
            {"action_id": "end_turn:P2", "action_type": "end_turn", "player_id": "P2", "enabled": True}
        ]

        with self.assertRaisesRegex(self.policy.BotPolicyError, "No enabled legal action"):
            self.policy.choose_action(legal_actions, "P1")

    def test_raises_when_no_enabled_action_exists(self):
        with self.assertRaisesRegex(self.policy.BotPolicyError, "No enabled legal action"):
            self.policy.choose_action([], "P1")

    def test_uses_action_type_priority(self):
        legal_actions = [
            {"action_id": "z-end", "action_type": "end_turn", "player_id": "P1", "enabled": True},
            {"action_id": "m-activate", "action_type": "activate", "player_id": "P1", "enabled": True},
            {"action_id": "x-play", "action_type": "play_card", "player_id": "P1", "enabled": True},
        ]

        chosen = self.policy.choose_action(legal_actions, "P1")

        self.assertEqual(chosen["action_id"], "x-play")
        self.assertEqual(chosen["action_type"], "play_card")

    def test_breaks_same_priority_ties_by_action_id(self):
        legal_actions = [
            {"action_id": "b-action", "action_type": "end_turn", "player_id": "P1", "enabled": True},
            {"action_id": "a-action", "action_type": "end_turn", "player_id": "P1", "enabled": True},
        ]

        chosen = self.policy.choose_action(legal_actions, "P1")

        self.assertEqual(chosen["action_id"], "a-action")


def _pick_two_decks(runtime_package):
    preferred = ["DECK-IGN-HAM-TEST-001", "DECK-IGN-LAN-TEST-001"]
    available = sorted(runtime_package.decks_by_id)
    selected = [deck_id for deck_id in preferred if deck_id in runtime_package.decks_by_id]
    if len(selected) >= 2:
        return selected[0], selected[1]
    for deck_id in available:
        if deck_id not in selected:
            selected.append(deck_id)
        if len(selected) == 2:
            return selected[0], selected[1]
    raise AssertionError("The runtime package must contain at least two decks for AI smoke tests.")


if __name__ == "__main__":
    unittest.main()
