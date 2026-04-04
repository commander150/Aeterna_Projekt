import unittest
from unittest.mock import patch

from engine.player import Jatekos


class DummyCard:
    def __init__(self, nev, birodalom="Solaris", aura_koltseg=1, egyseg_e=True):
        self.nev = nev
        self.birodalom = birodalom
        self.aura_koltseg = aura_koltseg
        self.egyseg_e = egyseg_e
        self.magnitudo = 1
        self.tamadas = 1
        self.eletero = 1
        self.kartyatipus = "Entitás" if egyseg_e else "Varázslat"
        self.kepesseg = ""


class TestJatekosFizetes(unittest.TestCase):
    def _make_player(self):
        pool = [DummyCard(f"Lap{i}", birodalom="Solaris") for i in range(8)]

        with patch("engine.player.random.choice", side_effect=lambda seq: seq[0]), patch(
            "engine.player.random.shuffle", side_effect=lambda seq: None
        ):
            return Jatekos("T1", "Solaris", pool)

    def test_unit_payment_uses_free_sources(self):
        p = self._make_player()
        p.osforras = [
            {"lap": DummyCard("F1", "Solaris"), "hasznalt": False},
            {"lap": DummyCard("F2", "Solaris"), "hasznalt": False},
        ]
        lap = DummyCard("Uj Egyseg", "Solaris", aura_koltseg=2, egyseg_e=True)

        ok = p.fizet(lap)

        self.assertTrue(ok)
        self.assertTrue(p.osforras[0]["hasznalt"])
        self.assertTrue(p.osforras[1]["hasznalt"])

    def test_spell_allows_aether_with_penalty(self):
        p = self._make_player()
        p.osforras = [
            {"lap": DummyCard("Sajat", "Solaris"), "hasznalt": False},
            {"lap": DummyCard("Aether1", "Aether"), "hasznalt": False},
            {"lap": DummyCard("Aether2", "Aether"), "hasznalt": False},
        ]

        lap = DummyCard("Solaris Spell", "Solaris", aura_koltseg=2, egyseg_e=False)

        ok = p.fizet(lap)

        self.assertTrue(ok)
        self.assertTrue(p.osforras[0]["hasznalt"])
        self.assertTrue(p.osforras[1]["hasznalt"])
        self.assertTrue(p.osforras[2]["hasznalt"])

    def test_spell_fails_if_penalized_cost_not_reachable(self):
        p = self._make_player()
        p.osforras = [
            {"lap": DummyCard("Aether", "Aether"), "hasznalt": False},
        ]

        lap = DummyCard("Solaris Spell", "Solaris", aura_koltseg=2, egyseg_e=False)

        ok = p.fizet(lap)

        self.assertFalse(ok)
        self.assertFalse(p.osforras[0]["hasznalt"])


if __name__ == "__main__":
    unittest.main()
