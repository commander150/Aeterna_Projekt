import importlib.util
import sys
import unittest
from dataclasses import replace
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
EVENT_LOG_SUMMARY_PATH = AI_VS_AI_DIR / "event_log_summary.py"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"
SCENARIO_CONFIG_PATH = AI_VS_AI_DIR / "scenario_config.py"
SCENARIO_RUNNER_PATH = AI_VS_AI_DIR / "scenario_runner.py"


def _load_module(module_name, path):
    ai_vs_ai_dir = str(AI_VS_AI_DIR)
    if ai_vs_ai_dir not in sys.path:
        sys.path.insert(0, ai_vs_ai_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestAIEventLogSummary(unittest.TestCase):
    def setUp(self):
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.scenario_config = _load_module("scenario_config", SCENARIO_CONFIG_PATH)
        self.scenario_runner = _load_module("scenario_runner", SCENARIO_RUNNER_PATH)
        self.event_log_summary = _load_module("event_log_summary", EVENT_LOG_SUMMARY_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_builds_deterministic_summary_from_default_scenario(self):
        result = self._run_default_scenario()

        summary = self.event_log_summary.build_scenario_summary(result)

        self.assertEqual(summary["scenario_id"], "end_turn_smoke")
        self.assertEqual(summary["match_id"], "AI-SCENARIO-END-TURN-001")
        self.assertTrue(summary["completed"])
        self.assertEqual(summary["result"], "completed")
        self.assertEqual(summary["steps_run"], 6)
        self.assertEqual(summary["event_count"], 6)
        self.assertEqual(summary["turn_number"], 4)
        self.assertEqual(summary["final_active_player_id"], "P1")
        self.assertEqual(summary["rejected_actions"], 0)
        self.assertEqual(summary["invariant_error_count"], 0)
        self.assertEqual(summary["event_type_counts"], {"end_turn": 6})
        self.assertEqual(summary["player_action_counts"], {"P1": 3, "P2": 3})

    def test_formats_default_scenario_summary_text(self):
        result = self._run_default_scenario()

        text = self.event_log_summary.format_scenario_summary(result)

        self.assertIn("AI SMOKE SUMMARY", text)
        self.assertIn("scenario_id: end_turn_smoke", text)
        self.assertIn("result: completed", text)
        self.assertIn("steps_run: 6", text)
        self.assertIn("event_count: 6", text)
        self.assertIn("event_type_counts: end_turn=6", text)
        self.assertIn("player_action_counts: P1=3, P2=3", text)
        event_lines = [line for line in text.splitlines() if ". turn=" in line]
        self.assertEqual(len(event_lines), 6)
        self.assertEqual(event_lines[0], "1. turn=1 player=P1 action=end_turn")
        self.assertEqual(event_lines[-1], "6. turn=4 player=P2 action=end_turn")

    def test_formatter_is_deterministic(self):
        result = self._run_default_scenario()

        first = self.event_log_summary.format_scenario_summary(result)
        second = self.event_log_summary.format_scenario_summary(result)

        self.assertEqual(first, second)

    def test_summarize_alias_matches_build_summary(self):
        result = self._run_default_scenario()

        self.assertEqual(
            self.event_log_summary.summarize_scenario_result(result),
            self.event_log_summary.build_scenario_summary(result),
        )

    def test_invalid_result_reports_clear_error(self):
        with self.assertRaisesRegex(self.event_log_summary.EventLogSummaryError, "Missing scenario result fields"):
            self.event_log_summary.format_scenario_summary({"scenario_id": "broken"})

        with self.assertRaisesRegex(self.event_log_summary.EventLogSummaryError, "event_log must be a list"):
            broken = dict(self._run_default_scenario())
            broken["event_log"] = "not-a-list"
            self.event_log_summary.build_scenario_summary(broken)

    def _run_default_scenario(self):
        runtime_package = self.runtime_package
        deck_id_a, deck_id_b = _pick_two_decks(runtime_package)
        config = replace(
            self.scenario_config.default_end_turn_smoke_config(),
            deck_id_a=deck_id_a,
            deck_id_b=deck_id_b,
        )
        return self.scenario_runner.run_scenario(config, runtime_package)


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
