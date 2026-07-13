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
ENVIRONMENT_PATH = ENGINE_DIR / "minimal_engine_environment.py"
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


class TestMinimalEngineEnvironment(unittest.TestCase):
    def setUp(self):
        self.environment_module = _load_module("minimal_engine_environment", ENVIRONMENT_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_reset_observation_and_bot_choice_are_json_compatible(self):
        environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)

        observation = environment.reset(match_id="MINIMAL-ENV-RESET-TEST-001")

        json.dumps(observation, ensure_ascii=False)
        self.assertEqual(observation["contract_type"], "minimal_engine_observation")
        self.assertEqual(observation["match_id"], "MINIMAL-ENV-RESET-TEST-001")
        self.assertEqual(observation["player_id"], "P1")
        self.assertEqual(observation["state_version"], 0)
        self.assertEqual(observation["transition_summary"]["response_count"], 0)
        action_types = [action["action_type"] for action in observation["action_space"]["actions"]]
        self.assertEqual(action_types, ["end_turn", "draw_card"])

        bot = self.environment_module.DeterministicMinimalBotPolicy()
        chosen = bot.choose_action(observation)
        self.assertEqual(chosen["action_type"], "draw_card")
        self.assertTrue(chosen["enabled"])

    def test_step_uses_session_and_updates_zone_counts(self):
        environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)
        observation = environment.reset(match_id="MINIMAL-ENV-STEP-TEST-001")
        player = environment.session.state.get_player("P1")
        initial_deck_count = len(player.deck_card_instance_ids)
        initial_hand_count = len(player.hand_card_instance_ids)
        action = self.environment_module.DeterministicMinimalBotPolicy().choose_action(observation)
        request = environment.session.build_action_request(action)

        response = environment.step(request)

        json.dumps(response, ensure_ascii=False)
        self.assertTrue(response["accepted"])
        self.assertTrue(response["success"])
        self.assertEqual(response["action_type"], "draw_card")
        self.assertEqual(len(player.deck_card_instance_ids), initial_deck_count - 1)
        self.assertEqual(len(player.hand_card_instance_ids), initial_hand_count + 1)
        self.assertEqual(environment.session.get_transition_summary()["event_count"], 1)

    def test_run_episode_returns_json_compatible_trajectory_summary(self):
        environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)

        episode = environment.run_episode(max_steps=4, match_id="MINIMAL-ENV-EPISODE-TEST-001")

        json.dumps(episode, ensure_ascii=False)
        self.assertEqual(episode["contract_type"], "minimal_ai_vs_ai_episode")
        self.assertEqual(episode["match_id"], "MINIMAL-ENV-EPISODE-TEST-001")
        self.assertEqual(episode["max_steps"], 4)
        self.assertLessEqual(episode["steps_run"], 4)
        self.assertGreater(len(episode["trajectory"]), 0)
        self.assertEqual(episode["steps_run"], len(episode["trajectory"]))
        self.assertIn("draw_card", [step["selected_action_type"] for step in episode["trajectory"]])
        self.assertTrue(
            set(step["selected_action_type"] for step in episode["trajectory"]).issubset({"draw_card", "end_turn"})
        )
        self.assertEqual(episode["transition_summary"]["response_count"], episode["steps_run"])
        self.assertEqual(episode["diagnostics_summary"]["count"], 0)
        self.assertEqual(episode["metadata"]["replay_support"], "not_implemented")


if __name__ == "__main__":
    unittest.main()
