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
        self.assertEqual(parse_semicolon_list("Sebzés; LapHúzás ;"), ["Sebzés", "LapHúzás"])

    def test_card_loads_structured_fields(self):
        card = Kartya(
            {
                "kartya_nev": "Teszt Lap",
                "kartyatipus": "Ige",
                "birodalom": "Aether",
                "kepesseg": "Flavor text",
                "kepesseg_canonical": "Okozz 2 sebzést.",
                "kulcsszavak_felismerve": "Burst; Echo",
                "trigger_felismerve": "on_play; on_destroyed",
                "celpont_felismerve": "Horizont; Pecsét",
                "hatascimkek": "Sebzés; PecsétSebzés",
                "ertelmezesi_statusz": "structured",
            }
        )

        self.assertEqual(card.canonical_text, "Okozz 2 sebzést.")
        self.assertTrue(has_keyword(card, "burst"))
        self.assertTrue(has_trigger(card, "on_play"))
        self.assertTrue(has_effect_tag(card, "sebzes"))

    def test_structured_damage_hits_enemy_unit(self):
        card = Kartya(
            {
                "kartya_nev": "Structured Sebzes",
                "kartyatipus": "Ige",
                "kepesseg": "-",
                "kepesseg_canonical": "Okozz 2 sebzést egy ellenséges Horizont Entitásnak.",
                "hatascimkek": "Sebzés",
                "celpont_felismerve": "Horizont",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.horizont[0] = CsataEgyseg(Kartya({"kartya_nev": "Celpont", "kartyatipus": "Entitás", "tamadas": 1, "eletero": 2}))

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertIsNone(enemy.horizont[0])

    def test_structured_seal_damage_breaks_seal(self):
        card = Kartya(
            {
                "kartya_nev": "Structured Pecsét",
                "kartyatipus": "Ige",
                "kepesseg_canonical": "Okozz 1 közvetlen sebzést az ellenfél Pecsétjének.",
                "hatascimkek": "Sebzés; PecsétSebzés",
                "celpont_felismerve": "Pecsét",
            }
        )
        owner = make_player("Caster")
        enemy = make_player("Enemy")
        enemy.pecsetek = [Kartya({"kartya_nev": "Pecsét", "kartyatipus": "Pecsét", "magnitudo": 1})]

        result = resolve_structured_effect(card, owner, enemy, {"category": "on_play"})

        self.assertTrue(result["resolved"])
        self.assertEqual(len(enemy.pecsetek), 0)


if __name__ == "__main__":
    unittest.main()
