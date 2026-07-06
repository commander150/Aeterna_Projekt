import importlib.util
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
FACADE_PATH = ENGINE_DIR / "minimal_engine.py"
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


class TestEngineMinimalSmokeFacade(unittest.TestCase):
    def setUp(self):
        self.engine = _load_module("minimal_engine", FACADE_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        self.deck_id_a, self.deck_id_b = _pick_two_decks(self.runtime_package)

    def test_facade_resolves_minimal_end_turn_request(self):
        state = self.engine.create_match(
            self.runtime_package,
            self.deck_id_a,
            self.deck_id_b,
            match_id="ENGINE-FACADE-SMOKE-001",
        )

        self.assertEqual(state.active_player_id, "P1")
        self.assertEqual(state.turn_number, 1)
        self.assertEqual(self.engine.validate_invariants(state, self.runtime_package), [])

        legal_actions = self.engine.get_legal_actions(state)
        self.assertEqual(len(legal_actions), 1)
        self.assertEqual(legal_actions[0]["action_type"], "end_turn")
        self.assertTrue(legal_actions[0]["enabled"])

        request = self.engine.build_action_request(state, legal_actions[0])
        validation = self.engine.validate_request(state, request, legal_actions)
        response = self.engine.resolve_request(state, request, legal_actions)

        self.assertTrue(validation["valid"])
        self.assertTrue(response["accepted"])
        self.assertEqual(response["event_count"], 1)
        self.assertEqual(self.engine.event_log(state)[0]["action_type"], "end_turn")
        self.assertEqual(state.active_player_id, "P2")
        self.assertEqual(self.engine.validate_invariants(state, self.runtime_package), [])


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
    raise AssertionError("The runtime package must contain at least two decks for engine smoke tests.")


if __name__ == "__main__":
    unittest.main()
