import importlib.util
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
ACTION_REQUEST_PATH = AI_VS_AI_DIR / "action_request.py"
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


class TestAIActionRequest(unittest.TestCase):
    def setUp(self):
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.kernel = _load_module("rules_kernel", KERNEL_PATH)
        self.policy = _load_module("bot_policy", BOT_POLICY_PATH)
        self.action_request = _load_module("action_request", ACTION_REQUEST_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        self.deck_id_a, self.deck_id_b = _pick_two_decks(self.runtime_package)

    def test_valid_end_turn_request_is_accepted_and_mutates_state(self):
        state = self._create_state()
        legal_actions = self.kernel.list_legal_actions(state, "P1")
        chosen = self.policy.choose_action(legal_actions, "P1")
        request = self.action_request.create_action_request(state.match_id, "P1", chosen)

        response = self.action_request.resolve_action_request(state, request, legal_actions)

        self.assertEqual(
            request,
            {
                "request_id": "request:AI-SMOKE-001:%s" % chosen["action_id"],
                "match_id": "AI-SMOKE-001",
                "player_id": "P1",
                "action_id": chosen["action_id"],
                "action_type": "end_turn",
            },
        )
        self.assertTrue(response["accepted"])
        self.assertIsNone(response["reason"])
        self.assertEqual(response["event_count"], 1)
        self.assertEqual(response["events"][0]["event_type"], "turn_transition")
        self.assertEqual(state.active_player_id, "P2")
        self.assertEqual(len(state.event_log), 1)

    def test_wrong_player_request_is_rejected_without_state_change(self):
        state = self._create_state()
        legal_actions = self.kernel.list_legal_actions(state, "P1")
        request = {
            "request_id": "request:wrong-player",
            "match_id": state.match_id,
            "player_id": "P2",
            "action_id": legal_actions[0]["action_id"],
            "action_type": "end_turn",
        }

        response = self.action_request.resolve_action_request(state, request, legal_actions)

        self.assert_rejected_without_state_change(response, state, "player_not_active")

    def test_unknown_action_id_is_rejected_without_state_change(self):
        state = self._create_state()
        legal_actions = self.kernel.list_legal_actions(state, "P1")
        request = {
            "request_id": "request:unknown-action",
            "match_id": state.match_id,
            "player_id": "P1",
            "action_id": "missing-action",
            "action_type": "end_turn",
        }

        response = self.action_request.resolve_action_request(state, request, legal_actions)

        self.assert_rejected_without_state_change(response, state, "unknown_action_id")

    def test_disabled_action_is_rejected_without_state_change(self):
        state = self._create_state()
        legal_actions = self.kernel.list_legal_actions(state, "P2")
        request = {
            "request_id": "request:disabled-action",
            "match_id": state.match_id,
            "player_id": "P1",
            "action_id": legal_actions[0]["action_id"],
            "action_type": "end_turn",
        }

        response = self.action_request.resolve_action_request(state, request, legal_actions)

        self.assert_rejected_without_state_change(response, state, "action_not_enabled")

    def test_action_type_mismatch_is_rejected_without_state_change(self):
        state = self._create_state()
        legal_actions = self.kernel.list_legal_actions(state, "P1")
        request = {
            "request_id": "request:type-mismatch",
            "match_id": state.match_id,
            "player_id": "P1",
            "action_id": legal_actions[0]["action_id"],
            "action_type": "play_card",
        }

        response = self.action_request.resolve_action_request(state, request, legal_actions)

        self.assert_rejected_without_state_change(response, state, "action_type_mismatch")

    def test_validation_result_is_deterministic(self):
        state = self._create_state()
        legal_actions = self.kernel.list_legal_actions(state, "P1")
        request = {
            "request_id": "request:deterministic",
            "match_id": state.match_id,
            "player_id": "P1",
            "action_id": legal_actions[0]["action_id"],
            "action_type": "end_turn",
        }

        first = self.action_request.validate_action_request(request, legal_actions, state)
        second = self.action_request.validate_action_request(request, legal_actions, state)

        self.assertEqual(first, second)

    def _create_state(self):
        return self.kernel.create_initial_match_state(self.runtime_package, self.deck_id_a, self.deck_id_b)

    def assert_rejected_without_state_change(self, response, state, reason):
        self.assertFalse(response["accepted"])
        self.assertEqual(response["reason"], reason)
        self.assertEqual(response["events"], [])
        self.assertEqual(response["event_count"], 0)
        self.assertEqual(state.active_player_id, "P1")
        self.assertEqual(state.turn_number, 1)
        self.assertEqual(state.event_log, [])


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
