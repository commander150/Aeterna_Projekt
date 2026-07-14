import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
RUN_COMMAND_PATH = AI_VS_AI_DIR / "run_minimal_ai_vs_ai_episode.py"


def _load_module(module_name, path):
    for module_dir in (str(AI_VS_AI_DIR), str(ENGINE_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestMinimalAIVsAIEpisodeCommand(unittest.TestCase):
    def setUp(self):
        self.run_command = _load_module("run_minimal_ai_vs_ai_episode", RUN_COMMAND_PATH)

    def test_json_mode_prints_valid_episode_without_file_output(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = self.run_command.main(
            [
                "--runtime-package-dir",
                str(GODOT_RUNTIME_PACKAGE_DIR),
                "--max-steps",
                "3",
                "--json",
            ],
            stdout=stdout,
            stderr=stderr,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        episode = json.loads(stdout.getvalue())
        self.assertEqual(episode["schema_version"], "minimal-ai-vs-ai-episode-v1")
        self.assertEqual(episode["contract_type"], "minimal_ai_vs_ai_episode")
        self.assertEqual(episode["max_steps"], 3)
        self.assertLessEqual(episode["steps_run"], 3)
        self.assertGreater(len(episode["trajectory"]), 0)
        self.assertTrue(episode["trajectory_validation"]["valid"])
        self.assertTrue(all(step["contract_type"] == "minimal_episode_step" for step in episode["trajectory"]))
        self.assertIn("draw_card", [step["selected_action_type"] for step in episode["trajectory"]])
        for observation in (episode["initial_observation"], episode["final_observation"]):
            self.assertEqual(
                observation["player_snapshot"]["schema_version"],
                "engine-player-visible-snapshot-v1",
            )
            self.assertEqual(observation["player_snapshot"]["player_id"], observation["player_id"])
            self.assertNotIn("debug_snapshot", observation)

    def test_text_mode_prints_short_summary(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = self.run_command.main(
            ["--runtime-package-dir", str(GODOT_RUNTIME_PACKAGE_DIR), "--max-steps", "2"],
            stdout=stdout,
            stderr=stderr,
        )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertIn("MINIMAL AI VS AI EPISODE", output)
        self.assertIn("steps_run:", output)
        self.assertIn("action_counts:", output)


if __name__ == "__main__":
    unittest.main()
