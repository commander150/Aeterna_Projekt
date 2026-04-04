import unittest

from engine.card import Kartya, CsataEgyseg


class TestKartyaModel(unittest.TestCase):
    def test_numeric_fields_are_cleanly_converted(self):
        row = [
            "Teszt Lap", "Entitás", "Solaris", "-", "Ember", "Harcos",
            "3", "2", "5", "7", "Gyorsaság"
        ]

        card = Kartya(row)

        self.assertEqual(card.magnitudo, 3)
        self.assertEqual(card.aura_koltseg, 2)
        self.assertEqual(card.tamadas, 5)
        self.assertEqual(card.eletero, 7)
        self.assertTrue(card.egyseg_e)

    def test_invalid_numeric_values_fallback_to_zero(self):
        row = [
            "Hibas Szam", "Varázslat", "Aether", "-", "-", "-",
            "nemszam", None, "", "1x", "-"
        ]

        card = Kartya(row)

        self.assertEqual(card.magnitudo, 0)
        self.assertEqual(card.aura_koltseg, 0)
        self.assertEqual(card.tamadas, 0)
        self.assertEqual(card.eletero, 0)

    def test_celerity_unit_starts_not_exhausted(self):
        card = Kartya([
            "Villamharcos", "Entitás", "Solaris", "-", "-", "-",
            1, 1, 2, 2, "Celerity"
        ])

        unit = CsataEgyseg(card)
        self.assertFalse(unit.kimerult)


if __name__ == "__main__":
    unittest.main()
