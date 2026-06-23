import unittest
from types import SimpleNamespace

from simulation.deck_presets import get_deck_preset, list_deck_presets, resolve_deck_preset_cards


class TestDeckPresets(unittest.TestCase):
    def test_known_preset_can_be_loaded(self):
        preset = get_deck_preset("ignis_tempo_test")

        self.assertEqual(preset["realm"], "Ignis")
        self.assertEqual(len(preset["cards"]), 40)

    def test_unknown_preset_raises_clear_error(self):
        with self.assertRaises(ValueError) as ctx:
            get_deck_preset("nincs_ilyen_preset")

        message = str(ctx.exception)
        self.assertIn("Ismeretlen deck preset", message)
        self.assertIn("ignis_tempo_test", message)

    def test_resolve_deck_preset_cards_returns_resolved_card_objects(self):
        full_pool = [
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

        resolved = resolve_deck_preset_cards("ignis_tempo_test", full_pool)

        self.assertEqual(resolved["realm"], "Ignis")
        self.assertEqual(len(resolved["cards"]), 40)
        self.assertTrue(all(getattr(card, "birodalom", None) == "Ignis" for card in resolved["cards"]))

    def test_list_deck_presets_exposes_summary_metadata(self):
        presets = list_deck_presets()

        self.assertIn("aqua_control_test", presets)
        self.assertEqual(presets["ventus_tempo_test"]["realm"], "Ventus")


if __name__ == "__main__":
    unittest.main()
