import unittest

from engine.card import Kartya, CsataEgyseg
from engine.card_metadata import has_effect_tag, has_keyword, has_trigger, parse_semicolon_list
from engine.structured_effects import resolve_structured_effect


def make_player(name="P1"):
    class _Player:
        def __init__(self):
            self.nev = name
            self.birodalom = "Aether"
            self.pakli = []
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

        def ujraaktivalt_egyseget(self, egyseg, forras=""):
            if egyseg is None or not egyseg.kimerult:
                return False
            egyseg.kimerult = False
            return True

        def jelol_overflow_vereseget(self, gyoztes_nev):
            self.overflow_vereseg = True
            self.overflow_gyoztes_nev = gyoztes_nev

    return _Player()


class TestStructuredEffects(unittest.TestCase):
    def test_parse_semicolon_list(self):
        self.assertEqual(parse_semicolon_list("Sebzes; LapHuzas ;"), ["Sebzes", "LapHuzas"])

    def test_card_loads_structured_fields(self):
        card = Kartya(
            {
                "kartya_nev": "Teszt Lap",
                "tipus": "Ige",
                "birodalom": "Aether",
                "kepesseg": "Flavor text",
                "kepesseg_canonical": "Okozz 2 sebzest.",
                "kulcsszavak_felismerve": "Burst; Echo",
                "trigger_felismerve": "on_play; on_destroyed",
                "celpont_felismerve": "Horizont; Pecset",
                "hatascimkek": "Sebzes; PecsetSebzes",
                "ertelmezesi_statusz": "structured",
            }
        )

        self.assertEqual(card.canonical_text, "Okozz 2 sebzest.")
        self.assertTrue(has_keyword(card, "burst"))
        self.assertTrue(has_trigger(card, "on_play"))
        self.assertTrue(has_effect_tag(card, "sebzes"))

    def test_card_loads_new_sheet_layout_without_canonical_column(self):
        card = Kartya(
            {
                "kartya_nev": "Teszt Entitas",
                "tipus": "Entitas",
                "birodalom": "Lux",
                "magnitudo": 3,
                "aura": 2,
                "atk": 4,
                "hp": 5,
                "kepesseg": "[HORIZONT] Oltalom",
                "kulcsszavak_felismerve": "Oltalom",
                "trigger_felismerve": "",
                "celpont_felismerve": "",
                "hatascimkek": "",
                "ertelmezesi_statusz": "passziv_kulcsszo",
            }
        )

        self.assertEqual(card.kartyatipus, "Entitas")
        self.assertTrue(card.egyseg_e)
        self.assertEqual(card.aura_koltseg, 2)
        self.assertEqual(card.tamadas, 4)
        self.assertEqual(card.eletero, 5)


    def test_trigger_aliases_are_normalized_from_sheet_values(self):
        card = Kartya(
            {
                "kartya_nev": "Alias Teszt",
                "kartyatipus": "Entitas",
                "trigger_felismerve": "on_spell_targeted; on_destroyed",
            }
        )

        self.assertTrue(has_trigger(card, "on_enemy_spell_target"))
        self.assertTrue(has_trigger(card, "on_destroyed"))

    def test_structured_damage_hits_enemy_unit(self):
        card = Kartya(
            {
                "kartya_nev": "Structured Sebzes",
                "kartyatipus": "Ige",
                "kepesseg": "-",
                "kepesseg_canonical": "Okozz 2 sebzest egy ellenseges Horizont Entitasnak.",
                "hatascimkek": "Sebzes",
                "celpont_felismerve": "Horizont",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(Kartya({"kartya_nev": "Celpont", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertIsNone(enemy.horizont[0])

    def test_structured_seal_damage_breaks_seal(self):
        card = Kartya(
            {
                "kartya_nev": "Structured Pecset",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Okozz 1 kozvetlen sebzest az ellenfel Pecsetjenek.",
                "hatascimkek": "Sebzes; PecsetSebzes",
                "celpont_felismerve": "Pecset",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.pecsetek = [Kartya({"kartya_nev": "Pecset", "kartyatipus": "Pecset", "magnitudo": 1})]

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertEqual(len(enemy.pecsetek), 0)

    def test_structured_move_to_zenit_does_not_bounce_back_to_horizon_same_resolution(self):
        card = Kartya(
            {
                "kartya_nev": "Viz alatti Borton",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Mozgasd az ellenseges Horizont Entitast a Zenitbe.",
                "hatascimkek": "Kimerites; Mozgatas_Horizontra; Mozgatas_Zenitbe",
                "celpont_felismerve": "enemy_entity; Horizont; Zenit",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        target = CsataEgyseg(Kartya({"kartya_nev": "Celpont", "kartyatipus": "Entitas", "tamadas": 2, "eletero": 3}))
        enemy.horizont[0] = target
        enemy.zenit[0] = None

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertIsNone(enemy.horizont[0])
        self.assertIs(enemy.zenit[0], target)
        self.assertTrue(enemy.zenit[0].kimerult)

    def test_structured_damage_prefers_zone_from_recognized_zone_metadata(self):
        card = Kartya(
            {
                "kartya_nev": "Zenit Csapas",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Okozz 2 sebzest egy ellenseges Zenit Entitasnak.",
                "hatascimkek": "Sebzes",
                "zona_felismerve": "zenit",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(Kartya({"kartya_nev": "Front", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 5}))
        enemy.zenit[0] = CsataEgyseg(Kartya({"kartya_nev": "Back", "kartyatipus": "Entitas", "tamadas": 1, "eletero": 2}))

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertIsNotNone(enemy.horizont[0])
        self.assertIsNone(enemy.zenit[0])


if __name__ == "__main__":
    unittest.main()
