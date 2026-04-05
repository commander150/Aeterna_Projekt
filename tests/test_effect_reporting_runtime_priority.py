import unittest
from unittest.mock import patch

from engine.card import CsataEgyseg, Kartya
from engine.effect_diagnostics_v2 import (
    _trigger_on_burst_with_diagnostics,
    _trigger_on_play_with_diagnostics,
)
from stats.analyzer import stats


class _Player:
    def __init__(self):
        self.nev = "P"
        self.birodalom = "Aether"
        self.pakli = [Kartya({"kartya_nev": "Lap", "tipus": "Ige"})]
        self.kez = []
        self.osforras = []
        self.temeto = []
        self.horizont = [None] * 6
        self.zenit = [None] * 6
        self.pecsetek = []
        self.rezonancia_aura = 0
        self.extra_huzas_ebben_a_korben = 0
        self.ideiglenes_aura_ebben_a_korben = 0
        self.ujraaktivalt_egysegek_ebben_a_korben = 0
        self.kell_tamadnia_kovetkezo_korben = False
        self.overflow_vereseg = False
        self.overflow_gyoztes_nev = None

    def huzas(self, extra=False, trigger_watch=True):
        if not self.pakli:
            return False
        self.kez.append(self.pakli.pop())
        return True


class TestEffectReportingRuntimePriority(unittest.TestCase):
    def setUp(self):
        stats.effect_outcomes = {"on_play": {}, "trap": {}, "burst": {}, "death": {}}
        stats.structured_metrics = {key: 0 for key in stats.structured_metrics}

    def test_runtime_handler_priority_skips_structured_for_buborek_pajzs(self):
        card = Kartya(
            {
                "kartya_nev": "Buborék-pajzs",
                "tipus": "Ige",
                "kepesseg": "Egy célpont Entitásod nem kaphat sebzést Rituálékból és Igékből a kör végéig.",
                "structured_data_available": True,
            }
        )
        owner = _Player()
        enemy = _Player()
        protected = CsataEgyseg(Kartya({"kartya_nev": "Vedett", "tipus": "Entitas", "tamadas": 2, "eletero": 4}))
        owner.horizont[0] = protected

        with patch("engine.effect_diagnostics_v2._run_structured", side_effect=AssertionError("structured should be skipped")):
            _trigger_on_play_with_diagnostics(card, owner, enemy)

        self.assertTrue(protected.spell_damage_immunity_until_turn_end)
        outcome = stats.effect_outcomes["on_play"][(card.nev, card.kepesseg)]
        self.assertEqual(outcome["status"], "runtime_supported")
        self.assertEqual(stats.structured_metrics["attempted"], 0)

    def test_runtime_handler_priority_skips_structured_for_langok_vedelme_burst(self):
        card = Kartya(
            {
                "kartya_nev": "Lángok Védelme",
                "tipus": "Ige",
                "kepesseg": "Válassz egy saját Entitást. Az adott kör végéig nem kaphat sebzést ellenséges Rituálékból vagy Igékből. Reakció (Burst): Ingyen elsüthető.",
                "structured_data_available": True,
            }
        )
        owner = _Player()
        enemy = _Player()
        protected = CsataEgyseg(Kartya({"kartya_nev": "Vedett", "tipus": "Entitas", "tamadas": 2, "eletero": 4}))
        owner.horizont[0] = protected

        with patch("engine.effect_diagnostics_v2._run_structured", side_effect=AssertionError("structured should be skipped")):
            result = _trigger_on_burst_with_diagnostics(card, owner, enemy)

        self.assertTrue(result)
        self.assertTrue(protected.enemy_spell_damage_immunity_until_turn_end)
        outcome = stats.effect_outcomes["burst"][(card.nev, card.kepesseg)]
        self.assertEqual(outcome["status"], "runtime_supported")
        self.assertEqual(stats.structured_metrics["attempted"], 0)


if __name__ == "__main__":
    unittest.main()
