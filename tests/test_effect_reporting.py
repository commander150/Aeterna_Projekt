import unittest

from engine.card import Kartya
from engine.card_metadata import parse_semicolon_list
from engine.structured_effects import STRUCTURED_STATUS_DEFERRED, resolve_structured_effect
from stats.analyzer import Statisztika


class _Player:
    def __init__(self):
        self.nev = 'P'
        self.birodalom = 'Aether'
        self.pakli = [Kartya({'kartya_nev': 'Lap', 'tipus': 'Ige'})]
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


class TestEffectReporting(unittest.TestCase):
    def test_parse_semicolon_list_supports_commas(self):
        self.assertEqual(parse_semicolon_list('draw, hp_mod, move_horizont'), ['draw', 'hp_mod', 'move_horizont'])

    def test_instant_spell_not_marked_deferred_without_triggers(self):
        card = Kartya({
            'kartya_nev': 'Isteni Feny',
            'tipus': 'Ige',
            'kepesseg': 'Huzz 1 lapot.',
            'hatascimkek': 'draw, hp_mod, move_horizont',
            'ertelmezesi_statusz': 'elso_koros_gepi_ertelmezes',
        })
        result = resolve_structured_effect(card, _Player(), _Player(), {'category': 'on_play'})
        self.assertNotEqual(result.get('status'), STRUCTURED_STATUS_DEFERRED)

    def test_outcome_precedence_keeps_runtime_over_missing(self):
        stats = Statisztika()
        stats.rogzit_effekt_kimenetet('on_play', 'Szentjanosbogar-Raj', 'Echo text', 'missing_implementation')
        stats.rogzit_effekt_kimenetet('on_play', 'Szentjanosbogar-Raj', 'Echo text', 'runtime_supported')
        outcome = stats.effect_outcomes['on_play'][('Szentjanosbogar-Raj', 'Echo text')]
        self.assertEqual(outcome['status'], 'runtime_supported')


if __name__ == '__main__':
    unittest.main()
