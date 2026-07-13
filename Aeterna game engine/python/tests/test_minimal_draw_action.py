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


class TestMinimalDrawAction(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_draw_card_moves_one_card_and_updates_contracts(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-DRAW-ACTION-TEST-001")
        player = state.get_player("P1")
        initial_deck_count = len(player.deck_card_instance_ids)
        initial_hand_count = len(player.hand_card_instance_ids)
        initial_snapshot = session.get_debug_snapshot()
        draw_action = _find_action(session.get_action_space(), "draw_card")

        self.assertGreater(initial_deck_count, 0)
        self.assertEqual(initial_hand_count, 0)
        self.assertTrue(draw_action["enabled"])
        self.assertEqual(draw_action["request_template"]["action_type"], "draw_card")
        self.assertEqual(draw_action["request_template"]["payload"], {})

        request = session.build_action_request(draw_action)
        json.dumps(request, ensure_ascii=False)
        response = session.step(request)

        json.dumps(response, ensure_ascii=False)
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(response["action_type"], "draw_card")
        self.assertEqual(response["state_version_before"], 0)
        self.assertEqual(response["state_version_after"], 1)
        self.assertEqual(response["new_event_count"], 1)
        self.assertEqual(response["new_event_sequences"], [1])
        self.assertTrue(response["invariants_ok"])

        drawn_card_instance_id = response["events"][0]["card_instance_id"]
        drawn_card_id = response["events"][0]["card_id"]
        self.assertEqual(len(player.deck_card_instance_ids), initial_deck_count - 1)
        self.assertEqual(len(player.hand_card_instance_ids), initial_hand_count + 1)
        self.assertNotIn(drawn_card_instance_id, player.deck_card_instance_ids)
        self.assertIn(drawn_card_instance_id, player.hand_card_instance_ids)
        self.assertEqual(player.hand_card_instance_ids[-1], drawn_card_instance_id)
        self.assertEqual(state.get_card_id(drawn_card_instance_id), drawn_card_id)
        self.assertEqual(state.state_version, 1)
        self.assertEqual(state.active_player_id, "P1")
        self.assertEqual(session.get_diagnostics(), [])

        event = response["events"][0]
        self.assertEqual(event["event_type"], "card_drawn")
        self.assertEqual(event["action_type"], "draw_card")
        self.assertEqual(event["player_id"], "P1")
        self.assertEqual(event["from_zone"], "deck")
        self.assertEqual(event["from_zone_index"], 0)
        self.assertEqual(event["to_zone"], "hand")
        self.assertEqual(event["to_zone_index"], 0)
        self.assertEqual(event["event_sequence"], 1)
        self.assertEqual(event["state_version"], 1)

        post_snapshot = session.get_debug_snapshot()
        self.assertEqual(initial_snapshot["players"][0]["zone_summary"]["deck_count"], initial_deck_count)
        self.assertEqual(initial_snapshot["players"][0]["zone_summary"]["hand_count"], initial_hand_count)
        self.assertEqual(post_snapshot["players"][0]["zone_summary"]["deck_count"], initial_deck_count - 1)
        self.assertEqual(post_snapshot["players"][0]["zone_summary"]["hand_count"], initial_hand_count + 1)
        self.assertTrue(post_snapshot["diagnostics_summary"]["draw_preconditions_ok"])
        self.assertTrue(post_snapshot["diagnostics_summary"]["hand_deck_invariants_ok"])

        exported = session.export_debug_session_state()
        json.dumps(exported, ensure_ascii=False)
        self.assertEqual(exported["last_action_response"]["action_type"], "draw_card")
        self.assertEqual(exported["last_action_response"]["new_event_sequences"], [1])
        self.assertEqual(exported["transition_summary"]["event_count"], 1)

        end_turn_action = _find_action(session.get_action_space(), "end_turn")
        end_turn_response = session.step(session.build_action_request(end_turn_action))
        self.assertTrue(end_turn_response["accepted"])
        self.assertEqual(end_turn_response["action_type"], "end_turn")
        self.assertEqual(end_turn_response["new_event_sequences"], [2])

    def test_empty_deck_draw_is_rejected_without_mutating_state(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-DRAW-ACTION-EMPTY-DECK-TEST-001")
        player = state.get_player("P1")
        _empty_deck(state, player)
        original_hand = list(player.hand_card_instance_ids)
        original_events = list(state.event_log)
        original_state_version = state.state_version
        action_space = session.get_action_space()
        draw_action = _find_action(action_space, "draw_card")

        self.assertFalse(draw_action["enabled"])
        self.assertEqual(draw_action["disabled_reason"], "deck_empty")
        response = session.step(session.build_action_request(draw_action))

        json.dumps(response, ensure_ascii=False)
        self.assertFalse(response["accepted"])
        self.assertFalse(response["success"])
        self.assertEqual(response["reason"], "deck_empty")
        self.assertEqual(response["action_type"], "draw_card")
        self.assertEqual(response["state_version_before"], original_state_version)
        self.assertEqual(response["state_version_after"], original_state_version)
        self.assertEqual(response["new_event_count"], 0)
        self.assertEqual(response["new_event_sequences"], [])
        self.assertEqual(player.deck_card_instance_ids, [])
        self.assertEqual(player.hand_card_instance_ids, original_hand)
        self.assertEqual(state.event_log, original_events)
        self.assertEqual(state.state_version, original_state_version)

        end_turn_action = _find_action(session.get_action_space(), "end_turn")
        end_turn_response = session.step(session.build_action_request(end_turn_action))
        self.assertTrue(end_turn_response["accepted"])
        self.assertEqual(end_turn_response["action_type"], "end_turn")


def _find_action(action_space, action_type):
    matches = [action for action in action_space["actions"] if action["action_type"] == action_type]
    if not matches:
        raise AssertionError("Missing action_type in action space: %s" % action_type)
    return matches[0]


def _empty_deck(state, player):
    for card_instance_id in player.deck_card_instance_ids:
        state.card_instances.pop(card_instance_id)
    player.deck_card_instance_ids = []


if __name__ == "__main__":
    unittest.main()
