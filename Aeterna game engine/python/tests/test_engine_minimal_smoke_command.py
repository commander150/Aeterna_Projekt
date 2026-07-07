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
        self.assertIn("initial_state_version: 0", output)
        self.assertIn("initial_legal_action_count: 1", output)
        self.assertIn("request_valid: true", output)
        self.assertIn("action_resolved: true", output)
        self.assertIn("action_type: end_turn", output)
        self.assertIn("post_state_version: 1", output)
        self.assertIn("initial_event_count: 0", output)
        self.assertIn("post_event_count: 1", output)
        self.assertIn("last_event_sequence: 1", output)
        self.assertIn("last_event_type: action_resolved", output)
        self.assertIn("invariants_ok: true", output)
        self.assertIn("diagnostics_count: 0", output)

    def test_structured_smoke_report_is_json_compatible(self):
        report = self.run_command.build_minimal_engine_smoke_report(GODOT_RUNTIME_PACKAGE_DIR)

        json.dumps(report, ensure_ascii=False)
        self.assertEqual(report["schema_version"], "minimal-engine-smoke-report-v0")
        self.assertEqual(report["report_type"], "minimal_engine_smoke")
        self.assertIn("not a final runtime decision", report["runtime_decision_note"])
        self.assertEqual(report["initial_snapshot_summary"]["snapshot_type"], "debug_snapshot")
        self.assertEqual(report["post_action_snapshot_summary"]["snapshot_type"], "debug_snapshot")
        self.assertEqual(report["initial_action_space"]["contract_type"], "legal_action_space")
        self.assertEqual(report["initial_action_space"]["enabled_action_count"], 1)
        self.assertEqual(report["initial_action_space"]["actions"][0]["action_type"], "end_turn")
        self.assertEqual(report["match"]["initial_state_version"], 0)
        self.assertEqual(report["match"]["post_state_version"], 1)
        self.assertEqual(report["action_response"]["schema_version"], "minimal-action-response-v0")
        self.assertEqual(report["action_response"]["contract_type"], "action_response")
        self.assertEqual(report["action_response"]["response_type"], "minimal_action_response")
        self.assertEqual(report["action_response"]["state_version_before"], 0)
        self.assertEqual(report["action_response"]["state_version_after"], 1)
        self.assertEqual(report["action_response"]["new_event_count"], 1)
        self.assertEqual(report["action_response"]["new_event_sequences"], [1])
        self.assertEqual(report["initial_snapshot_summary"]["event_log_summary"]["event_count"], 0)
        self.assertGreaterEqual(
            report["post_action_snapshot_summary"]["event_log_summary"]["event_count"],
            report["initial_snapshot_summary"]["event_log_summary"]["event_count"],
        )
        self.assertTrue(report["action_response"]["request_valid"])
        self.assertTrue(report["action_response"]["accepted"])
        self.assertTrue(report["action_response"]["success"])
        self.assertEqual(report["action_response"]["action_type"], "end_turn")
        self.assertEqual(report["action_response"]["diagnostics_summary"]["count"], 0)
        self.assertEqual(report["events"]["event_log"][0]["action_type"], "end_turn")
        self.assertEqual(report["events"]["event_log"][0]["event_sequence"], 1)
        self.assertEqual(report["events"]["last_event_sequence"], 1)
        self.assertEqual(report["events"]["post_event_count"], 1)
        self.assertTrue(report["invariants"]["ok"])
        self.assertEqual(report["diagnostics"]["count"], 0)
        self.assertEqual(report["response_history_count"], 1)

    def test_legacy_run_function_returns_structured_report(self):
        result = self.run_command.run_minimal_engine_smoke(GODOT_RUNTIME_PACKAGE_DIR)

        self.assertEqual(result["report_type"], "minimal_engine_smoke")
        self.assertTrue(result["action_response"]["accepted"])

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
