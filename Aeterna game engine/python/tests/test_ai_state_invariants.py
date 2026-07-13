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
INVARIANTS_PATH = AI_VS_AI_DIR / "state_invariants.py"
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


class TestAIStateInvariants(unittest.TestCase):
    def setUp(self):
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.kernel = _load_module("rules_kernel", KERNEL_PATH)
        self.policy = _load_module("bot_policy", BOT_POLICY_PATH)
        self.action_request = _load_module("action_request", ACTION_REQUEST_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        self.deck_id_a, self.deck_id_b = _pick_two_decks(self.runtime_package)

    def test_valid_initial_state_has_no_invariant_errors(self):
        state = self._create_state()

        errors = self.invariants.validate_state_invariants(state, self.runtime_package)

        self.assertEqual(errors, [])
        self.assertTrue(self.invariants.assert_state_invariants(state, self.runtime_package))

    def test_valid_state_after_one_end_turn_has_no_invariant_errors(self):
        state = self._create_state()

        self._resolve_end_turn_for(state, "P1")

        self.assertEqual(state.active_player_id, "P2")
        self.assertEqual(len(state.event_log), 1)
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])

    def test_valid_state_after_two_end_turns_has_no_invariant_errors(self):
        state = self._create_state()

        self._resolve_end_turn_for(state, "P1")
        self._resolve_end_turn_for(state, "P2")

        self.assertEqual(state.active_player_id, "P1")
        self.assertEqual(state.turn_number, 2)
        self.assertEqual(len(state.event_log), 2)
        self.assertEqual(self.invariants.validate_state_invariants(state, self.runtime_package), [])

    def test_invalid_active_player_id_reports_error(self):
        state = self._create_state()
        state.active_player_id = "NO_PLAYER"

        errors = self.invariants.validate_state_invariants(state, self.runtime_package)

        self.assert_error_code(errors, "ACTIVE_PLAYER_UNKNOWN")
        with self.assertRaisesRegex(self.invariants.StateInvariantError, "ACTIVE_PLAYER_UNKNOWN"):
            self.invariants.assert_state_invariants(state, self.runtime_package)

    def test_invalid_turn_number_reports_error(self):
        state = self._create_state()
        state.turn_number = 0

        errors = self.invariants.validate_state_invariants(state, self.runtime_package)

        self.assert_error_code(errors, "TURN_NUMBER_INVALID")

    def test_invalid_deck_id_reports_error_when_runtime_package_is_given(self):
        state = self._create_state()
        state.players[0].deck_id = "MISSING-DECK"

        errors = self.invariants.validate_state_invariants(state, self.runtime_package)

        self.assert_error_code(errors, "DECK_UNKNOWN")

    def test_invalid_instance_card_ref_reports_error_when_runtime_package_is_given(self):
        state = self._create_state()
        card_instance_id = state.players[0].deck_card_instance_ids[0]
        state.card_instances[card_instance_id]["card_id"] = "MISSING-CARD"

        errors = self.invariants.validate_state_invariants(state, self.runtime_package)

        self.assert_error_code(errors, "CARD_INSTANCE_CARD_UNKNOWN")

    def test_invalid_event_index_reports_error(self):
        state = self._create_state()
        self._resolve_end_turn_for(state, "P1")
        state.event_log[0]["event_index"] = 99

        errors = self.invariants.validate_state_invariants(state, self.runtime_package)

        self.assert_error_code(errors, "EVENT_INDEX_INVALID")

    def test_invalid_event_player_id_reports_error(self):
        state = self._create_state()
        self._resolve_end_turn_for(state, "P1")
        state.event_log[0]["player_id"] = "NO_PLAYER"

        errors = self.invariants.validate_state_invariants(state, self.runtime_package)

        self.assert_error_code(errors, "EVENT_PLAYER_UNKNOWN")

    def test_invalid_event_turn_number_reports_error(self):
        state = self._create_state()
        self._resolve_end_turn_for(state, "P1")
        state.event_log[0]["turn_number"] = 0

        errors = self.invariants.validate_state_invariants(state, self.runtime_package)

        self.assert_error_code(errors, "EVENT_TURN_NUMBER_INVALID")

    def _create_state(self):
        return self.kernel.create_initial_match_state(self.runtime_package, self.deck_id_a, self.deck_id_b)

    def _resolve_end_turn_for(self, state, player_id):
        legal_actions = self.kernel.list_legal_actions(state, player_id)
        chosen = self.policy.choose_action(legal_actions, player_id)
        request = self.action_request.create_action_request(state.match_id, player_id, chosen)
        response = self.action_request.resolve_action_request(state, request, legal_actions)
        self.assertTrue(response["accepted"])
        return response

    def assert_error_code(self, errors, code):
        self.assertIn(code, [error["code"] for error in errors])


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
