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


if __name__ == "__main__":
    unittest.main()
