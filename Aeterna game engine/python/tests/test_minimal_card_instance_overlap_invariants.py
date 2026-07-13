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


class TestMinimalCardInstanceOverlapInvariants(unittest.TestCase):
    def setUp(self):
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.invariants = _load_module("state_invariants", INVARIANTS_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_duplicate_card_ids_are_legal_distinct_instances(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-CARD-INSTANCE-OVERLAP-TEST-001")
        player = state.get_player("P1")
        first_instance_id, second_instance_id = player.deck_card_instance_ids[:2]

        self.assertNotEqual(first_instance_id, second_instance_id)
        self.assertEqual(state.get_card_id(first_instance_id), state.get_card_id(second_instance_id))
        self.assertTrue(session.get_draw_precondition("P1")["can_draw"])

        first_response = _draw(session)
        second_response = _draw(session)

        json.dumps(first_response, ensure_ascii=False)
        json.dumps(second_response, ensure_ascii=False)
        self.assertTrue(first_response["accepted"])
        self.assertTrue(second_response["accepted"])
        self.assertEqual(first_response["events"][0]["card_instance_id"], first_instance_id)
        self.assertEqual(second_response["events"][0]["card_instance_id"], second_instance_id)
        self.assertEqual(first_response["events"][0]["card_id"], second_response["events"][0]["card_id"])
        self.assertEqual(session.get_diagnostics(), [])
        self.assertEqual(session.get_debug_snapshot()["metadata"]["card_instance_model"], "minimal_registry_v0")
        self.assertFalse(session.get_debug_snapshot()["metadata"]["card_id_overlap_guard"])

    def test_same_instance_in_multiple_zones_is_an_invariant_error(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(match_id="ENGINE-CARD-INSTANCE-ZONE-OVERLAP-TEST-001")
        player = state.get_player("P1")
        card_instance_id = player.deck_card_instance_ids[0]
        player.hand_card_instance_ids.append(card_instance_id)

        errors = self.invariants.validate_state_invariants(state, self.runtime_package)

        self.assertIn("CARD_INSTANCE_MULTIPLE_ZONES", [error["code"] for error in errors])


def _draw(session):
    draw_action = next(
        action for action in session.get_action_space()["actions"] if action["action_type"] == "draw_card"
    )
    return session.step(session.build_action_request(draw_action))


if __name__ == "__main__":
    unittest.main()
