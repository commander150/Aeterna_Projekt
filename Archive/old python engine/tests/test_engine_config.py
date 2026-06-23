import unittest

from engine.config import EngineConfig, set_active_engine_config
from engine.effects_expansions import handle_expansion_gate


class TestEngineConfig(unittest.TestCase):
    def test_core_only_turns_everything_off(self):
        config = EngineConfig(
            run_mode="core_only",
            expansion_modules={"advanced_keywords": True},
            expansion_flags={"keyword_stealth": True},
        )

        self.assertFalse(config.is_module_enabled("advanced_keywords"))
        self.assertFalse(config.is_flag_enabled("keyword_stealth"))

    def test_full_mode_turns_everything_on(self):
        config = EngineConfig(run_mode="full_expansion_all_on")

        self.assertTrue(config.is_module_enabled("advanced_keywords"))
        self.assertTrue(config.is_flag_enabled("keyword_stealth"))

    def test_disabled_expansion_is_skipped_cleanly(self):
        set_active_engine_config(EngineConfig(run_mode="core_only"))
        self.assertTrue(handle_expansion_gate("Teszt lap", "Stealth"))


if __name__ == "__main__":
    unittest.main()
