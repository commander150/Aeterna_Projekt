import json
import os
import tempfile
import unittest

from openpyxl import Workbook

from data.loader import kartyak_betoltese, load_card_rows_jsonl


def _runtime_row(card_id, name, card_type, **overrides):
    row = {
        "Card_ID": card_id,
        "Kártya név": name,
        "Típus": card_type,
        "Birodalom": "Ignis",
        "Klán": "Hamvaskez",
        "Faj": "none",
        "Kaszt": "none",
        "Magnitudó": "1.0",
        "Aura": 1.0,
        "ATK": "none",
        "HP": "none",
        "Képesség": "Teszt kepesseg",
        "Képesség_Canonical": "test effect",
        "Zóna_Felismerve": "dominium",
        "Kulcsszavak_Felismerve": "none",
        "Trigger_Felismerve": "blank",
        "Célpont_Felismerve": "blank",
        "Hatáscímkék": "blank",
        "Időtartam_Felismerve": "instant",
        "Feltétel_Felismerve": "none",
        "Gépi_Leírás": "Runtime loader smoke row",
        "Értelmezési_Státusz": "structured",
        "Engine_Megjegyzés": "none",
        "Set_ID": "CORE01",
        "Rarity": "C",
        "Treatment": "NF",
        "Art_Variant": "A1",
        "Print_Status": "P1",
        "Version": "V1",
        "Play_Legal_Status": "CORE01_candidate",
    }
    row.update(overrides)
    return row


class TestRuntimeJsonlLoader(unittest.TestCase):
    def _write_jsonl(self, rows):
        handle = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".jsonl")
        try:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            return handle.name
        finally:
            handle.close()

    def _write_xlsx(self):
        headers = [
            "Kártya név",
            "Típus",
            "Birodalom",
            "Klán",
            "Faj",
            "Kaszt",
            "Magnitudó",
            "Aura",
            "ATK",
            "HP",
            "Képesség",
            "Képesség_Canonical",
            "Zóna_Felismerve",
            "Kulcsszavak_Felismerve",
            "Trigger_Felismerve",
            "Célpont_Felismerve",
            "Hatáscímkék",
            "Időtartam_Felismerve",
            "Feltétel_Felismerve",
            "Gépi_Leírás",
            "Értelmezési_Státusz",
            "Engine_Megjegyzés",
        ]
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "CARDS_MASTER"
        sheet.append(headers)
        sheet.append(
            [
                "XLSX Fallback Entitas",
                "Entitas",
                "Ignis",
                "Hamvaskez",
                "none",
                "none",
                1,
                1,
                1,
                2,
                "Teszt",
                "test",
                "dominium",
                "none",
                "blank",
                "blank",
                "blank",
                "blank",
                "none",
                "Fallback row",
                "structured",
                "none",
            ]
        )
        handle = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        path = handle.name
        handle.close()
        workbook.save(path)
        return path

    def test_runtime_jsonl_smoke_covers_card_types_and_validation(self):
        rows = [
            _runtime_row(
                "IGN-HAM-001",
                "Egyszeru Entitas",
                "Entitas",
                **{"ATK": "2.0", "HP": 3.0, "Időtartam_Felismerve": "blank"},
            ),
            _runtime_row(
                "IGN-HAM-002",
                "Triggered Entitas",
                "Entitas",
                **{
                    "ATK": 1.0,
                    "HP": "4.0",
                    "Trigger_Felismerve": "on_death",
                    "Célpont_Felismerve": "enemy_entity",
                    "Hatáscímkék": "damage",
                    "Időtartam_Felismerve": "instant",
                },
            ),
            _runtime_row(
                "IGN-HAM-003",
                "Egyszeru Ige",
                "Ige",
                **{"Hatáscímkék": "draw", "Collector_Number": "CORE01-IGN-HAM-003"},
            ),
            _runtime_row(
                "IGN-HAM-004",
                "Burst Ige",
                "Ige",
                **{
                    "Zóna_Felismerve": "burst",
                    "Kulcsszavak_Felismerve": "none",
                    "Trigger_Felismerve": "on_enemy_spell_or_ritual_played",
                    "Célpont_Felismerve": "enemy_spell_or_ritual",
                    "Hatáscímkék": "counterspell",
                },
            ),
            _runtime_row(
                "IGN-HAM-005",
                "Rituale",
                "Rituale",
                **{"Aura": "2.0", "Hatáscímkék": "resource_gain"},
            ),
            _runtime_row(
                "IGN-HAM-006",
                "Vedojel",
                "Jel",
                **{
                    "Trigger_Felismerve": "on_enemy_summon",
                    "Célpont_Felismerve": "enemy_entity",
                    "Hatáscímkék": "exhaust",
                },
            ),
            _runtime_row(
                "IGN-HAM-007",
                "Probater",
                "Sik",
                **{"Zóna_Felismerve": "aeternal", "Időtartam_Felismerve": "while_active", "Hatáscímkék": "resource_gain"},
            ),
            _runtime_row(
                "IGN-HAM-008",
                "Token Letrehozo",
                "Ige",
                **{"Hatáscímkék": "summon_token", "Célpont_Felismerve": "own_entity"},
            ),
            _runtime_row(
                "IGN-HAM-009",
                "None Stat Ige",
                "Ige",
                **{"ATK": "none", "HP": "none", "Hatáscímkék": "damage", "Rarity": "X"},
            ),
            _runtime_row(
                "IGN-HAM-010",
                "Tobb Structured Ertek",
                "Ige",
                **{
                    "Zóna_Felismerve": "dominium; hand",
                    "Trigger_Felismerve": "on_death; on_turn_end",
                    "Célpont_Felismerve": "enemy_entity; own_entity",
                    "Hatáscímkék": "damage; draw",
                    "Kulcsszavak_Felismerve": "burst; clarion",
                    "Időtartam_Felismerve": "instant",
                },
            ),
        ]
        path = self._write_jsonl(rows)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))

        loaded_rows, warnings = load_card_rows_jsonl(path)
        cards = kartyak_betoltese(path)

        self.assertEqual(len(loaded_rows), len(rows))
        self.assertEqual(len(cards), len(rows))
        self.assertEqual(len({row["card_id"] for row in loaded_rows}), len(rows))
        self.assertTrue(all(row.get("generated_print_id") for row in loaded_rows))
        self.assertEqual(loaded_rows[0]["magnitudo"], 1)
        self.assertEqual(loaded_rows[0]["aura_koltseg"], 1)
        self.assertEqual(loaded_rows[0]["tamadas"], 2)
        self.assertEqual(loaded_rows[0]["eletero"], 3)
        self.assertEqual(loaded_rows[8]["tamadas"], 0)
        self.assertEqual(loaded_rows[8]["eletero"], 0)
        self.assertEqual(cards[2].collector_number, "CORE01-IGN-HAM-003")
        self.assertEqual(cards[0].collector_number, "")
        self.assertIn("burst", cards[3].keywords_normalized)
        self.assertEqual(cards[9].zones_normalized, ["dominium", "hand"])
        self.assertEqual(cards[9].effect_tags_normalized, ["damage", "draw"])
        self.assertFalse(any("duplicate_card_id" in warning for warning in warnings))
        self.assertTrue(any("unknown_runtime_enum_value:rarity:X" in warning for warning in warnings))

    def test_generic_loader_keeps_xlsx_fallback_working(self):
        path = self._write_xlsx()
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))

        cards = kartyak_betoltese(path)

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].nev, "XLSX Fallback Entitas")
        self.assertEqual(cards[0].magnitudo, 1)
        self.assertEqual(cards[0].eletero, 2)


if __name__ == "__main__":
    unittest.main()
