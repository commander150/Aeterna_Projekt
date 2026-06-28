import importlib.util
import sys
import unittest
from dataclasses import replace
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"
SCENARIO_CONFIG_PATH = AI_VS_AI_DIR / "scenario_config.py"


def _load_module(module_name, path):
    ai_vs_ai_dir = str(AI_VS_AI_DIR)
    if ai_vs_ai_dir not in sys.path:
        sys.path.insert(0, ai_vs_ai_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestAIScenarioConfig(unittest.TestCase):
    def setUp(self):
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.scenario_config = _load_module("scenario_config", SCENARIO_CONFIG_PATH)

    def test_default_end_turn_smoke_config_is_valid(self):
        config = self.scenario_config.default_end_turn_smoke_config()

        self.assertEqual(config.scenario_id, "end_turn_smoke")
        self.assertEqual(config.match_id, "AI-SCENARIO-END-TURN-001")
        self.assertEqual(config.deck_id_a, "DECK-IGN-HAM-TEST-001")
        self.assertEqual(config.deck_id_b, "DECK-IGN-LAN-TEST-001")
        self.assertEqual(config.max_steps, 6)
        self.assertEqual(config.max_turns, 5)
        self.assertEqual(config.seed, 1)
        self.assertEqual(config.expected_event_types, ())
        self.assertTrue(config.fail_on_no_enabled_action)
        self.assertEqual(self.scenario_config.validate_scenario_config(config), [])

    def test_empty_scenario_id_reports_error(self):
        config = replace(self.scenario_config.default_end_turn_smoke_config(), scenario_id="")

        errors = self.scenario_config.validate_scenario_config(config)

        self.assert_error_code(errors, "SCENARIO_ID_MISSING")

    def test_empty_match_id_reports_error(self):
        config = replace(self.scenario_config.default_end_turn_smoke_config(), match_id="")

        errors = self.scenario_config.validate_scenario_config(config)

        self.assert_error_code(errors, "MATCH_ID_MISSING")

    def test_empty_deck_ids_report_errors(self):
        config = replace(self.scenario_config.default_end_turn_smoke_config(), deck_id_a="", deck_id_b="")

        errors = self.scenario_config.validate_scenario_config(config)

        self.assert_error_code(errors, "DECK_ID_A_MISSING")
        self.assert_error_code(errors, "DECK_ID_B_MISSING")

    def test_invalid_max_steps_reports_error(self):
        config = replace(self.scenario_config.default_end_turn_smoke_config(), max_steps=0)

        errors = self.scenario_config.validate_scenario_config(config)

        self.assert_error_code(errors, "MAX_STEPS_INVALID")

    def test_invalid_max_turns_reports_error(self):
        config = replace(self.scenario_config.default_end_turn_smoke_config(), max_turns=0)

        errors = self.scenario_config.validate_scenario_config(config)

        self.assert_error_code(errors, "MAX_TURNS_INVALID")

    def test_none_max_turns_is_valid(self):
        config = replace(self.scenario_config.default_end_turn_smoke_config(), max_turns=None)

        errors = self.scenario_config.validate_scenario_config(config)

        self.assertEqual(errors, [])

    def test_invalid_seed_reports_error(self):
        config = replace(self.scenario_config.default_end_turn_smoke_config(), seed="1")

        errors = self.scenario_config.validate_scenario_config(config)

        self.assert_error_code(errors, "SEED_INVALID")

    def test_invalid_expected_event_types_reports_error(self):
        invalid_container = replace(self.scenario_config.default_end_turn_smoke_config(), expected_event_types="event")
        invalid_value = replace(self.scenario_config.default_end_turn_smoke_config(), expected_event_types=("ok", ""))

        container_errors = self.scenario_config.validate_scenario_config(invalid_container)
        value_errors = self.scenario_config.validate_scenario_config(invalid_value)

        self.assert_error_code(container_errors, "EXPECTED_EVENT_TYPES_INVALID")
        self.assert_error_code(value_errors, "EXPECTED_EVENT_TYPE_INVALID")

    def test_invalid_fail_on_no_enabled_action_reports_error(self):
        config = replace(self.scenario_config.default_end_turn_smoke_config(), fail_on_no_enabled_action="yes")

        errors = self.scenario_config.validate_scenario_config(config)

        self.assert_error_code(errors, "FAIL_ON_NO_ENABLED_ACTION_INVALID")

    def test_runtime_package_validation_accepts_existing_decks(self):
        runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        deck_id_a, deck_id_b = _pick_two_decks(runtime_package)
        config = replace(
            self.scenario_config.default_end_turn_smoke_config(),
            deck_id_a=deck_id_a,
            deck_id_b=deck_id_b,
        )

        errors = self.scenario_config.validate_scenario_config(config, runtime_package)

        self.assertEqual(errors, [])
        self.assertTrue(self.scenario_config.assert_scenario_config(config, runtime_package))

    def test_runtime_package_validation_rejects_unknown_deck(self):
        runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        deck_id_a, _ = _pick_two_decks(runtime_package)
        config = replace(
            self.scenario_config.default_end_turn_smoke_config(),
            deck_id_a=deck_id_a,
            deck_id_b="MISSING-DECK",
        )

        errors = self.scenario_config.validate_scenario_config(config, runtime_package)

        self.assert_error_code(errors, "DECK_ID_UNKNOWN")
        with self.assertRaisesRegex(self.scenario_config.ScenarioConfigError, "DECK_ID_UNKNOWN"):
            self.scenario_config.assert_scenario_config(config, runtime_package)

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
