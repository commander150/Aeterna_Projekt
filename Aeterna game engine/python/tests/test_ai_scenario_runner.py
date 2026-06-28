import importlib.util
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
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


class TestAIScenarioRunner(unittest.TestCase):
    def setUp(self):
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.scenario_config = _load_module("scenario_config", SCENARIO_CONFIG_PATH)
        self.scenario_runner = _load_module("scenario_runner", SCENARIO_RUNNER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_default_scenario_runs_end_turn_smoke(self):
        config = self._runtime_compatible_default_config()

        summary = self.scenario_runner.run_scenario(config, self.runtime_package)

        self.assertTrue(summary["completed"])
        self.assertEqual(summary["result"], "completed")
        self.assertEqual(summary["scenario_id"], config.scenario_id)
        self.assertEqual(summary["match_id"], config.match_id)
        self.assertEqual(summary["steps_run"], 6)
        self.assertEqual(summary["event_count"], 6)
        self.assertEqual(summary["rejected_actions"], 0)
        self.assertEqual(summary["invariant_errors"], [])
        self.assertEqual([event["event_index"] for event in summary["event_log"]], list(range(6)))
        self.assertEqual({event["action_type"] for event in summary["event_log"]}, {"end_turn"})

    def test_six_end_turns_have_deterministic_final_state(self):
        config = self._runtime_compatible_default_config()

        summary = self.scenario_runner.run_scenario(config, self.runtime_package)

        self.assertEqual(summary["turn_number"], 4)
        self.assertEqual(summary["final_active_player_id"], "P1")
        self.assertEqual(
            [event["player_id"] for event in summary["event_log"]],
            ["P1", "P2", "P1", "P2", "P1", "P2"],
        )

    def test_unknown_deck_returns_invalid_config_summary(self):
        config = replace(self._runtime_compatible_default_config(), deck_id_b="MISSING-DECK")

        summary = self.scenario_runner.run_scenario(config, self.runtime_package)

        self.assertFalse(summary["completed"])
        self.assertEqual(summary["result"], "invalid_config")
        self.assertEqual(summary["steps_run"], 0)
        self.assertEqual(summary["event_count"], 0)
        self.assertIn("DECK_ID_UNKNOWN", [error["code"] for error in summary["invariant_errors"]])

    def test_no_enabled_action_fails_when_config_requires_it(self):
        config = self._runtime_compatible_default_config()

        with patch.object(self.scenario_runner, "list_legal_actions", return_value=[]):
            summary = self.scenario_runner.run_scenario(config, self.runtime_package)

        self.assertFalse(summary["completed"])
        self.assertEqual(summary["result"], "failed_no_enabled_action")
        self.assertEqual(summary["steps_run"], 0)
        self.assertEqual(summary["event_count"], 0)
        self.assertEqual(summary["rejected_actions"], 0)
        self.assertEqual(summary["invariant_errors"], [])

    def test_runner_does_not_modify_runtime_package_registries(self):
        config = self._runtime_compatible_default_config()
        before = self.runtime_package.count_summary()

        self.scenario_runner.run_scenario(config, self.runtime_package)

        self.assertEqual(self.runtime_package.count_summary(), before)

    def _runtime_compatible_default_config(self):
        config = self.scenario_config.default_end_turn_smoke_config()
        deck_id_a, deck_id_b = _pick_two_decks(self.runtime_package)
        return replace(config, deck_id_a=deck_id_a, deck_id_b=deck_id_b)


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
