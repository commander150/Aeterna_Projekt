import os
import unittest
from unittest.mock import patch
from uuid import uuid4

from simulation.config import SimulationConfig
from simulation import test_launcher


class TestTestLauncher(unittest.TestCase):
    def _workspace_temp_path(self, filename):
        base_dir = os.path.join(os.getcwd(), "test_logs_workspace", "launcher_tests")
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, f"{uuid4().hex}_{filename}")

    def test_build_config_from_profile_uses_profile_defaults(self):
        config = test_launcher.build_config_from_profile("smoke_random")

        self.assertIsInstance(config, SimulationConfig)
        self.assertEqual(config.games, 3)
        self.assertIsNone(config.random_seed)
        self.assertIsNone(config.player1_realm)
        self.assertIsNone(config.player2_realm)
        self.assertTrue(config.random_realm_fallback)

    def test_build_config_from_profile_applies_overrides(self):
        config = test_launcher.build_config_from_profile(
            "seeded_matchup",
            overrides={
                "games": "7",
                "random_seed": "222",
                "player1_realm": "Ignis",
                "player2_realm": "Ignis",
            },
        )

        self.assertEqual(config.games, 7)
        self.assertEqual(config.random_seed, 222)
        self.assertEqual(config.player1_realm, "Ignis")
        self.assertEqual(config.player2_realm, "Ignis")
        self.assertFalse(config.random_realm_fallback)

    def test_save_and_load_last_settings_roundtrip(self):
        path = self._workspace_temp_path("last_settings_roundtrip.json")
        payload = {
            "profile_name": "repeated_matchup",
            "overrides": {"games": 10, "random_seed": 211},
        }

        saved = test_launcher.save_last_settings(payload, path)
        loaded = test_launcher.load_last_settings(path)

        self.assertTrue(saved)
        self.assertEqual(loaded, payload)

    def test_launch_interactive_replays_last_settings(self):
        settings_path = self._workspace_temp_path("last_settings_replay.json")
        test_launcher.save_last_settings(
            {
                "profile_name": "seeded_matchup",
                "overrides": {"games": 4, "random_seed": 123},
            },
            settings_path,
        )

        with patch("simulation.test_launcher.create_logger") as create_logger_mock, patch(
            "simulation.test_launcher.futtat_szimulaciot"
        ) as runner_mock:
            config = test_launcher.launch_interactive(
                input_func=lambda _: "r",
                print_func=lambda *_: None,
                settings_path=settings_path,
                xlsx_path="cards.xlsx",
                base_dir=".",
            )

        self.assertIsInstance(config, SimulationConfig)
        self.assertEqual(config.games, 4)
        self.assertEqual(config.random_seed, 123)
        create_logger_mock.assert_called_once()
        runner_mock.assert_called_once()

    def test_launch_non_interactive_uses_profile_and_overrides(self):
        settings_path = self._workspace_temp_path("cli_profile_run.json")

        with patch("simulation.test_launcher.create_logger") as create_logger_mock, patch(
            "simulation.test_launcher.futtat_szimulaciot"
        ) as runner_mock:
            config = test_launcher.launch_non_interactive(
                profile_name="seeded_matchup",
                overrides={"games": 6, "random_seed": 999, "player2_realm": "Ignis"},
                xlsx_path="cards.xlsx",
                base_dir=".",
                settings_path=settings_path,
            )

        self.assertIsInstance(config, SimulationConfig)
        self.assertEqual(config.games, 6)
        self.assertEqual(config.random_seed, 999)
        self.assertEqual(config.player1_realm, "Ignis")
        self.assertEqual(config.player2_realm, "Ignis")
        create_logger_mock.assert_called_once()
        runner_mock.assert_called_once()

    def test_launch_non_interactive_replays_last_run(self):
        settings_path = self._workspace_temp_path("cli_last_run.json")
        test_launcher.save_last_settings(
            {
                "profile_name": "repeated_matchup",
                "overrides": {"games": 9, "random_seed": 456, "player1_realm": "Ignis", "player2_realm": "Aqua"},
            },
            settings_path,
        )

        with patch("simulation.test_launcher.create_logger") as create_logger_mock, patch(
            "simulation.test_launcher.futtat_szimulaciot"
        ) as runner_mock:
            config = test_launcher.launch_non_interactive(
                use_last_run=True,
                xlsx_path="cards.xlsx",
                base_dir=".",
                settings_path=settings_path,
            )

        self.assertIsInstance(config, SimulationConfig)
        self.assertEqual(config.games, 9)
        self.assertEqual(config.random_seed, 456)
        create_logger_mock.assert_called_once()
        runner_mock.assert_called_once()

    def test_main_without_cli_arguments_falls_back_to_interactive(self):
        with patch("simulation.test_launcher.launch_interactive", return_value="interactive") as interactive_mock:
            result = test_launcher.main(
                argv=[],
                input_func=lambda _: "q",
                print_func=lambda *_: None,
                settings_path=self._workspace_temp_path("main_interactive.json"),
            )

        self.assertEqual(result, "interactive")
        interactive_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
