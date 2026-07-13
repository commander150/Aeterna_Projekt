import importlib.util
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
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


class TestAIRulesKernel(unittest.TestCase):
    def setUp(self):
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.kernel = _load_module("rules_kernel", KERNEL_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        self.deck_id_a, self.deck_id_b = _pick_two_decks(self.runtime_package)

    def test_create_initial_match_state_from_runtime_package_decks(self):
        state = self.kernel.create_initial_match_state(
            self.runtime_package,
            self.deck_id_a,
            self.deck_id_b,
        )

        self.assertEqual(state.match_id, "AI-SMOKE-001")
        self.assertEqual(state.turn_number, 1)
        self.assertEqual(state.active_player_id, "P1")
        self.assertEqual(state.phase, "main")
        self.assertEqual([player.player_id for player in state.players], ["P1", "P2"])
        self.assertEqual(state.players[0].deck_id, self.deck_id_a)
        self.assertEqual(state.players[1].deck_id, self.deck_id_b)
        self.assertGreater(len(state.players[0].deck_card_instance_ids), 0)
        self.assertGreater(len(state.players[1].deck_card_instance_ids), 0)
        expected_instance_count = sum(len(player.deck_card_instance_ids) for player in state.players)
        self.assertEqual(len(state.card_instances), expected_instance_count)
        self.assertEqual(state.event_log, [])

    def test_list_legal_actions_enables_only_active_player_minimal_actions(self):
        state = self.kernel.create_initial_match_state(self.runtime_package, self.deck_id_a, self.deck_id_b)

        active_actions = self.kernel.list_legal_actions(state, "P1")
        inactive_actions = self.kernel.list_legal_actions(state, "P2")

        self.assertEqual([action["action_type"] for action in active_actions], ["end_turn", "draw_card"])
        self.assertTrue(all(action["player_id"] == "P1" for action in active_actions))
        self.assertTrue(all(action["enabled"] for action in active_actions))

        self.assertEqual([action["action_type"] for action in inactive_actions], ["end_turn", "draw_card"])
        self.assertTrue(all(action["player_id"] == "P2" for action in inactive_actions))
        self.assertTrue(all(action["enabled"] is False for action in inactive_actions))
        self.assertTrue(all(action["reason"] == "not_active_player" for action in inactive_actions))

    def test_apply_end_turn_switches_active_player_and_logs_event(self):
        state = self.kernel.create_initial_match_state(self.runtime_package, self.deck_id_a, self.deck_id_b)

        first_action = self.kernel.list_legal_actions(state, "P1")[0]
        first_response = self.kernel.apply_action(state, first_action)

        self.assertTrue(first_response["ok"])
        self.assertEqual(state.active_player_id, "P2")
        self.assertEqual(state.turn_number, 1)
        self.assertEqual(len(state.event_log), 1)
        self.assertEqual(state.event_log[0]["event_index"], 0)
        self.assertEqual(state.event_log[0]["event_type"], "action_resolved")
        self.assertEqual(state.event_log[0]["player_id"], "P1")
        self.assertEqual(state.event_log[0]["action_type"], "end_turn")
        self.assertEqual(state.event_log[0]["turn_number"], 1)

        second_action = self.kernel.list_legal_actions(state, "P2")[0]
        self.kernel.apply_action(state, second_action)

        self.assertEqual(state.active_player_id, "P1")
        self.assertEqual(state.turn_number, 2)
        self.assertEqual(len(state.event_log), 2)
        self.assertEqual(state.event_log[1]["event_index"], 1)
        self.assertEqual(state.event_log[1]["player_id"], "P2")
        self.assertEqual(state.event_log[1]["turn_number"], 2)

    def test_apply_draw_card_moves_one_card_and_logs_event(self):
        state = self.kernel.create_initial_match_state(self.runtime_package, self.deck_id_a, self.deck_id_b)
        player = state.get_player("P1")
        draw_action = [action for action in self.kernel.list_legal_actions(state, "P1") if action["action_type"] == "draw_card"][0]
        original_deck_count = len(player.deck_card_instance_ids)
        original_hand_count = len(player.hand_card_instance_ids)
        drawn_card_instance_id = player.deck_card_instance_ids[0]
        drawn_card_id = state.get_card_id(drawn_card_instance_id)

        response = self.kernel.apply_action(state, draw_action)

        self.assertTrue(response["ok"])
        self.assertEqual(len(player.deck_card_instance_ids), original_deck_count - 1)
        self.assertEqual(len(player.hand_card_instance_ids), original_hand_count + 1)
        self.assertEqual(player.hand_card_instance_ids[-1], drawn_card_instance_id)
        self.assertNotIn(drawn_card_instance_id, player.deck_card_instance_ids)
        self.assertEqual(state.state_version, 1)
        self.assertEqual(state.active_player_id, "P1")
        self.assertEqual(state.event_log[0]["event_type"], "card_drawn")
        self.assertEqual(state.event_log[0]["action_type"], "draw_card")
        self.assertEqual(state.event_log[0]["card_instance_id"], drawn_card_instance_id)
        self.assertEqual(state.event_log[0]["card_id"], drawn_card_id)
        self.assertEqual(state.event_log[0]["from_zone"], "deck")
        self.assertEqual(state.event_log[0]["to_zone"], "hand")

    def test_invalid_actions_raise_clear_errors(self):
        state = self.kernel.create_initial_match_state(self.runtime_package, self.deck_id_a, self.deck_id_b)

        inactive_action = self.kernel.list_legal_actions(state, "P2")[0]
        with self.assertRaisesRegex(self.kernel.RulesKernelError, "not enabled"):
            self.kernel.apply_action(state, inactive_action)

        with self.assertRaisesRegex(self.kernel.RulesKernelError, "Unsupported action_type"):
            self.kernel.apply_action(
                state,
                {
                    "action_id": "unknown:P1",
                    "action_type": "play_card",
                    "player_id": "P1",
                    "enabled": True,
                },
            )

        with self.assertRaisesRegex(self.kernel.RulesKernelError, "not active"):
            self.kernel.apply_action(
                state,
                {
                    "action_id": "end_turn:bad",
                    "action_type": "end_turn",
                    "player_id": "P2",
                    "enabled": True,
                },
            )

    def test_unknown_deck_id_raises_clear_error(self):
        with self.assertRaisesRegex(self.kernel.RulesKernelError, "Unknown deck_id"):
            self.kernel.create_initial_match_state(self.runtime_package, "NOPE", self.deck_id_b)


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
