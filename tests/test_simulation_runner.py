import unittest
from types import SimpleNamespace

from simulation.runner import _resolve_player_setup, _valassz_birodalmat
from simulation.config import SimulationConfig


class TestSimulationRunnerRealmNormalization(unittest.TestCase):
    def test_valassz_birodalmat_accepts_lowercase_realm(self):
        result = _valassz_birodalmat("terra", ["Aether", "Terra", "Ventus"], random_fallback=False)

        self.assertEqual(result, "Terra")

    def test_valassz_birodalmat_accepts_uppercase_realm(self):
        result = _valassz_birodalmat("VENTUS", ["Aether", "Terra", "Ventus"], random_fallback=False)

        self.assertEqual(result, "Ventus")

    def test_valassz_birodalmat_keeps_canonical_realm(self):
        result = _valassz_birodalmat("Terra", ["Aether", "Terra", "Ventus"], random_fallback=False)

        self.assertEqual(result, "Terra")

    def test_valassz_birodalmat_unknown_realm_raises_clear_error(self):
        with self.assertRaises(ValueError) as ctx:
            _valassz_birodalmat("ismeretlen", ["Aether", "Terra", "Ventus"], random_fallback=False)

        message = str(ctx.exception)
        self.assertIn("kert birodalom nem elerheto", message)
        self.assertIn("Aether, Terra, Ventus", message)

    def test_resolve_player_setup_uses_preset_realm_and_fixed_deck(self):
        config = SimulationConfig(player1_deck_preset="ignis_tempo_test")
        cards = [
            SimpleNamespace(nev="Hamvaskezű Újonc", birodalom="Ignis"),
            SimpleNamespace(nev="Lángoló Öklű Bajnok", birodalom="Ignis"),
            SimpleNamespace(nev="Parázsfarkas", birodalom="Ignis"),
            SimpleNamespace(nev="Ignis Csonttörő", birodalom="Ignis"),
            SimpleNamespace(nev="Vörösréz Pajzsos", birodalom="Ignis"),
            SimpleNamespace(nev="Hamvaskezű Seregvezér", birodalom="Ignis"),
            SimpleNamespace(nev="Tűzvihar Bajnoka", birodalom="Ignis"),
            SimpleNamespace(nev="Élő Meteor", birodalom="Ignis"),
            SimpleNamespace(nev="A Főnix Könnye", birodalom="Ignis"),
            SimpleNamespace(nev="Tünde Pyromanta", birodalom="Ignis"),
        ]

        setup = _resolve_player_setup(config, "player1", ["Ignis", "Aqua"], cards)

        self.assertEqual(setup["realm"], "Ignis")
        self.assertEqual(setup["preset_name"], "ignis_tempo_test")
        self.assertEqual(len(setup["deck"]), 40)

    def test_resolve_player_setup_rejects_mismatched_preset_and_realm(self):
        config = SimulationConfig(player1_realm="Aqua", player1_deck_preset="ignis_tempo_test")
        cards = [
            SimpleNamespace(nev="Hamvaskezű Újonc", birodalom="Ignis"),
            SimpleNamespace(nev="Lángoló Öklű Bajnok", birodalom="Ignis"),
            SimpleNamespace(nev="Parázsfarkas", birodalom="Ignis"),
            SimpleNamespace(nev="Ignis Csonttörő", birodalom="Ignis"),
            SimpleNamespace(nev="Vörösréz Pajzsos", birodalom="Ignis"),
            SimpleNamespace(nev="Hamvaskezű Seregvezér", birodalom="Ignis"),
            SimpleNamespace(nev="Tűzvihar Bajnoka", birodalom="Ignis"),
            SimpleNamespace(nev="Élő Meteor", birodalom="Ignis"),
            SimpleNamespace(nev="A Főnix Könnye", birodalom="Ignis"),
            SimpleNamespace(nev="Tünde Pyromanta", birodalom="Ignis"),
        ]

        with self.assertRaises(ValueError) as ctx:
            _resolve_player_setup(config, "player1", ["Ignis", "Aqua"], cards)

        self.assertIn("nem egyezik a preset realmjevel", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
