import unittest

from engine.effect_diagnostics_v2 import (
    _trigger_on_burst_with_diagnostics,
    _trigger_on_death_with_diagnostics,
    _trigger_on_play_with_diagnostics,
    _trigger_on_trap_with_diagnostics,
    install_effect_diagnostics,
    is_effect_diagnostics_installed,
)
from engine.effects import EffectEngine


class TestEffectDiagnosticsInstall(unittest.TestCase):
    def test_install_effect_diagnostics_is_idempotent_and_registers_effectengine_adapters(self):
        first = install_effect_diagnostics()
        second = install_effect_diagnostics()

        self.assertIn(first, (True, False))
        self.assertFalse(second)
        self.assertTrue(is_effect_diagnostics_installed())
        self.assertIs(EffectEngine.get_trigger_adapter("on_play"), _trigger_on_play_with_diagnostics)
        self.assertIs(EffectEngine.get_trigger_adapter("trap"), _trigger_on_trap_with_diagnostics)
        self.assertIs(EffectEngine.get_trigger_adapter("burst"), _trigger_on_burst_with_diagnostics)
        self.assertIs(EffectEngine.get_trigger_adapter("death"), _trigger_on_death_with_diagnostics)
        self.assertTrue(EffectEngine.has_trigger_adapter("on_play"))
        self.assertTrue(EffectEngine.has_trigger_adapter("trap"))
        self.assertTrue(EffectEngine.has_trigger_adapter("burst"))
        self.assertTrue(EffectEngine.has_trigger_adapter("death"))


if __name__ == "__main__":
    unittest.main()
