import importlib.util
import io
import sys
import unittest
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
TOOLS_ENGINE_DIR = ENGINE_PYTHON_DIR / "tools" / "engine"
RUN_COMMAND_PATH = TOOLS_ENGINE_DIR / "run_minimal_engine_smoke.py"


def _load_module(module_name, path):
    for module_dir in (str(TOOLS_ENGINE_DIR), str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestEngineMinimalSmokeCommand(unittest.TestCase):
    def setUp(self):
        self.run_command = _load_module("run_minimal_engine_smoke", RUN_COMMAND_PATH)

    def test_main_prints_minimal_engine_smoke_report_and_returns_zero(self):
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
        self.assertIn("MINIMAL ENGINE SMOKE REPORT", output)
        self.assertIn("initial_legal_action_count: 1", output)
        self.assertIn("request_valid: true", output)
        self.assertIn("action_resolved: true", output)
        self.assertIn("action_type: end_turn", output)
        self.assertIn("initial_event_count: 0", output)
        self.assertIn("post_event_count: 1", output)
        self.assertIn("last_event_type: action_resolved", output)
        self.assertIn("invariants_ok: true", output)
        self.assertIn("diagnostics_count: 0", output)

    def test_run_minimal_engine_smoke_returns_snapshots_and_event_log(self):
        result = self.run_command.run_minimal_engine_smoke(GODOT_RUNTIME_PACKAGE_DIR)

        self.assertEqual(result["initial_snapshot"]["snapshot_type"], "debug_snapshot")
        self.assertEqual(result["post_snapshot"]["snapshot_type"], "debug_snapshot")
        self.assertEqual(result["initial_snapshot"]["event_log_summary"]["event_count"], 0)
        self.assertEqual(result["post_snapshot"]["event_log_summary"]["event_count"], 1)
        self.assertEqual(result["event_log"][0]["action_type"], "end_turn")
        self.assertTrue(result["request_valid"])
        self.assertTrue(result["action_response"]["accepted"])
        self.assertTrue(result["invariants_ok"])

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
        self.assertIn("Minimal engine smoke failed:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
