import unittest

from data.loader import normalize_row_mapping, validate_row_mapping
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

    def test_new_22_column_metadata_fields_are_mapped_correctly(self):
        row = {
            "kartya_nev": "Teszt Aura",
            "kartyatipus": "Ige",
            "birodalom": "Ignis",
            "klan": "Hamvaskezű",
            "magnitudo": 2,
            "aura_koltseg": 1,
            "kepesseg": "Adj +2 ATK-t.",
            "kepesseg_canonical": "target allied entity gains +2 atk until end of turn",
            "zona_felismerve": "horizont, zenit",
            "kulcsszavak_felismerve": "Burst, Clarion",
            "trigger_felismerve": "on_play, on_spell_targeted",
            "celpont_felismerve": "own_entity, enemy_spell",
            "hatascimkek": "atk_buff, damage",
            "idotartam_felismerve": "kor_vegeig",
            "feltetel_felismerve": "none",
            "gepi_leiras": "Simple buff spell",
            "ertelmezesi_statusz": "structured",
            "engine_megjegyzes": "teszt",
        }

        card = Kartya(row)

        self.assertEqual(card.canonical_text, "target allied entity gains +2 atk until end of turn")
        self.assertEqual(card.zones_normalized, ["horizont", "zenit"])
        self.assertEqual(card.keywords_normalized, ["burst", "clarion"])
        self.assertEqual(card.triggers_normalized, ["on_play", "on_enemy_spell_target"])
        self.assertEqual(card.targets_normalized, ["own_entity", "enemy_spell"])
        self.assertEqual(card.effect_tags_normalized, ["grant_attack", "damage"])
        self.assertEqual(card.durations_normalized, ["until_end_of_turn"])
        self.assertEqual(card.machine_description, "Simple buff spell")
        self.assertEqual(card.engine_notes, "teszt")

    def test_loader_normalization_handles_blank_none_and_lists(self):
        row = normalize_row_mapping(
            {
                "kartya_nev": "Teszt",
                "kartyatipus": "Ige",
                "birodalom": "Ignis",
                "klan": "blank",
                "faj": None,
                "kaszt": "none",
                "magnitudo": "2",
                "aura_koltseg": "",
                "tamadas": None,
                "eletero": "1x",
                "kepesseg": "Valami",
                "kepesseg_canonical": "blank",
                "zona_felismerve": "horizont; zenit | blank",
                "kulcsszavak_felismerve": "Burst, Clarion",
                "trigger_felismerve": "on_play; none",
                "celpont_felismerve": "own_entity, blank",
                "hatascimkek": "damage; draw",
                "idotartam_felismerve": "none",
                "feltetel_felismerve": "blank",
                "gepi_leiras": None,
                "ertelmezesi_statusz": "structured",
                "engine_megjegyzes": "none",
            }
        )

        self.assertEqual(row["klan"], "")
        self.assertEqual(row["magnitudo"], 2)
        self.assertEqual(row["aura_koltseg"], 0)
        self.assertEqual(row["eletero"], 0)
        self.assertEqual(row["zona_felismerve"], "horizont, zenit")
        self.assertEqual(row["kulcsszavak_felismerve"], "burst, clarion")

    def test_loader_validation_flags_missing_required_fields(self):
        issues = validate_row_mapping(
            {
                "kartya_nev": "",
                "kartyatipus": "Entitas",
                "birodalom": "Ignis",
                "klan": "",
                "faj": "",
                "kaszt": "",
                "magnitudo": 1,
                "aura_koltseg": 1,
                "tamadas": 1,
                "eletero": 0,
                "kepesseg": "",
                "kepesseg_canonical": "",
                "zona_felismerve": "",
                "kulcsszavak_felismerve": "",
                "trigger_felismerve": "",
                "celpont_felismerve": "",
                "hatascimkek": "",
                "idotartam_felismerve": "",
                "feltetel_felismerve": "",
                "gepi_leiras": "",
                "ertelmezesi_statusz": "",
                "engine_megjegyzes": "",
            },
            row_index=2,
            sheet_name="Teszt",
        )

        self.assertTrue(any("ures_kotelezo_mezo:kartya_nev" in issue for issue in issues))
        self.assertTrue(any("ures_kotelezo_mezo:kepesseg" in issue for issue in issues))
        self.assertTrue(any("entitas_hp_hianyzik" in issue for issue in issues))

    def test_loader_validation_flags_unknown_enum_values(self):
        issues = validate_row_mapping(
            {
                "kartya_nev": "Teszt",
                "kartyatipus": "Ige",
                "birodalom": "Ignis",
                "klan": "",
                "faj": "",
                "kaszt": "",
                "magnitudo": 1,
                "aura_koltseg": 1,
                "tamadas": 0,
                "eletero": 0,
                "kepesseg": "Teszt",
                "kepesseg_canonical": "",
                "zona_felismerve": "horizont, valami",
                "kulcsszavak_felismerve": "burst, valami",
                "trigger_felismerve": "on_play, valami",
                "celpont_felismerve": "enemy_entity, rossz",
                "hatascimkek": "damage, rossz",
                "idotartam_felismerve": "rossz",
                "feltetel_felismerve": "",
                "gepi_leiras": "",
                "ertelmezesi_statusz": "",
                "engine_megjegyzes": "",
            },
            row_index=3,
            sheet_name="Teszt",
        )

        self.assertTrue(any("ismeretlen_ertek:zona_felismerve:valami" in issue for issue in issues))
        self.assertTrue(any("ismeretlen_ertek:kulcsszavak_felismerve:valami" in issue for issue in issues))
        self.assertTrue(any("ismeretlen_ertek:hatascimkek:rossz" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
