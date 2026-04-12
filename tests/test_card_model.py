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
            "trigger_felismerve": "on_spell_targeted, on_destroyed",
            "celpont_felismerve": "own_entity, enemy_spell",
            "hatascimkek": "grant_attack, damage",
            "idotartam_felismerve": "until_end_of_turn",
            "feltetel_felismerve": "none",
            "gepi_leiras": "Simple buff spell",
            "ertelmezesi_statusz": "structured",
            "engine_megjegyzes": "teszt",
        }

        card = Kartya(row)

        self.assertEqual(card.canonical_text, "target allied entity gains +2 atk until end of turn")
        self.assertEqual(card.zones_normalized, ["horizont", "zenit"])
        self.assertEqual(card.keywords_normalized, ["burst", "clarion"])
        self.assertEqual(card.triggers_normalized, ["on_enemy_spell_target", "on_death"])
        self.assertEqual(card.targets_normalized, ["own_entity", "enemy_spell"])
        self.assertEqual(card.effect_tags_normalized, ["atk_mod", "damage"])
        self.assertEqual(card.durations_normalized, ["until_turn_end"])
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
                "trigger_felismerve": "on_destroyed; none",
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
        self.assertEqual(row["trigger_felismerve"], "on_death")
        self.assertEqual(row["idotartam_felismerve"], "")

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
                "trigger_felismerve": "on_destroyed, valami",
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

        self.assertTrue(any("unknown_enum_value:zona_felismerve:valami" in issue for issue in issues))
        self.assertTrue(any("unknown_enum_value:kulcsszavak_felismerve:valami" in issue for issue in issues))
        self.assertTrue(any("unknown_enum_value:hatascimkek:rossz" in issue for issue in issues))

    def test_loader_validation_distinguishes_alias_from_legacy_internal(self):
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
                "zona_felismerve": "pecset",
                "kulcsszavak_felismerve": "burst",
                "trigger_felismerve": "on_destroyed, on_play",
                "celpont_felismerve": "enemy_entity",
                "hatascimkek": "grant_attack, damage",
                "idotartam_felismerve": "until_end_of_turn",
                "feltetel_felismerve": "",
                "gepi_leiras": "",
                "ertelmezesi_statusz": "",
                "engine_megjegyzes": "",
            },
            row_index=4,
            sheet_name="Teszt",
        )

        self.assertTrue(any("alias_normalizable:zona_felismerve:pecset->seal_row" in issue for issue in issues))
        self.assertTrue(any("legacy_internal_value:trigger_felismerve:on_play" in issue for issue in issues))
        self.assertTrue(any("alias_normalizable:hatascimkek:grant_attack->atk_mod" in issue for issue in issues))
        self.assertTrue(any("alias_normalizable:idotartam_felismerve:until_end_of_turn->until_turn_end" in issue for issue in issues))

    def test_loader_validation_does_not_flag_keyword_only_static_entity_duration(self):
        issues = validate_row_mapping(
            {
                "kartya_nev": "Hamvaskezu Ujonc",
                "kartyatipus": "Entitas",
                "birodalom": "Ignis",
                "klan": "Hamvaskezu",
                "faj": "",
                "kaszt": "",
                "magnitudo": 2,
                "aura_koltseg": 2,
                "tamadas": 2,
                "eletero": 2,
                "kepesseg": "Celerity",
                "kepesseg_canonical": "",
                "zona_felismerve": "horizont",
                "kulcsszavak_felismerve": "celerity",
                "trigger_felismerve": "static",
                "celpont_felismerve": "",
                "hatascimkek": "",
                "idotartam_felismerve": "static_while_on_board",
                "feltetel_felismerve": "",
                "gepi_leiras": "",
                "ertelmezesi_statusz": "",
                "engine_megjegyzes": "",
            },
            row_index=5,
            sheet_name="Teszt",
        )

        self.assertFalse(any("suspicious_field_combination:idotartam_hatascimke_nelkul" in issue for issue in issues))

    def test_loader_validation_still_flags_duration_without_effect_tag_for_non_keyword_case(self):
        issues = validate_row_mapping(
            {
                "kartya_nev": "Teszt Aura",
                "kartyatipus": "Ige",
                "birodalom": "Ignis",
                "klan": "",
                "faj": "",
                "kaszt": "",
                "magnitudo": 1,
                "aura_koltseg": 1,
                "tamadas": 0,
                "eletero": 0,
                "kepesseg": "Valami tartos",
                "kepesseg_canonical": "",
                "zona_felismerve": "",
                "kulcsszavak_felismerve": "",
                "trigger_felismerve": "on_cast",
                "celpont_felismerve": "",
                "hatascimkek": "",
                "idotartam_felismerve": "until_turn_end",
                "feltetel_felismerve": "",
                "gepi_leiras": "",
                "ertelmezesi_statusz": "",
                "engine_megjegyzes": "",
            },
            row_index=6,
            sheet_name="Teszt",
        )

        self.assertTrue(any("suspicious_field_combination:idotartam_hatascimke_nelkul" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
