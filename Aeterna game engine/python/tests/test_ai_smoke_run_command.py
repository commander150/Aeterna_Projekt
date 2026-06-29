import importlib.util
import io
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
RUN_COMMAND_PATH = AI_VS_AI_DIR / "run_ai_smoke_scenario.py"


def _load_module(module_name, path):
    ai_vs_ai_dir = str(AI_VS_AI_DIR)
    if ai_vs_ai_dir not in sys.path:
        sys.path.insert(0, ai_vs_ai_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestAISmokeRunCommand(unittest.TestCase):
    def setUp(self):
        self.run_command = _load_module("run_ai_smoke_scenario", RUN_COMMAND_PATH)

    def test_main_prints_default_smoke_summary_and_returns_zero(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = self.run_command.main(
            ["--runtime-package-dir", str(GODOT_RUNTIME_PACKAGE_DIR)],
            stdout=stdout,
            stderr=stderr,
        )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertIn("AI SMOKE SUMMARY", output)
        self.assertIn("scenario_id: end_turn_smoke", output)
        self.assertIn("result: completed", output)
        self.assertIn("steps_run: 6", output)
        self.assertIn("event_count: 6", output)
        self.assertIn("event_type_counts: end_turn=6", output)
        self.assertIn("player_action_counts: P1=3, P2=3", output)
        self.assertIn("EVENTS", output)

    def test_run_default_smoke_uses_default_runtime_package_path(self):
        text = self.run_command.run_default_smoke()

        self.assertIn("AI SMOKE SUMMARY", text)
        self.assertIn("event_count: 6", text)

    def test_main_reports_error_and_nonzero_exit_code(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = self.run_command.main(
            ["--runtime-package-dir", str(ENGINE_PYTHON_DIR / "missing-runtime-package")],
            stdout=stdout,
            stderr=stderr,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("AI smoke scenario failed:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
