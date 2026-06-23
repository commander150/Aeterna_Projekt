import json
import os
import tempfile
import unittest
from types import SimpleNamespace

from data.decklist_loader import (
    group_decklist_rows,
    load_and_validate_decklists,
    load_decklist_rows_jsonl,
    normalize_deck_card_id,
    validate_decklists,
)


class TestDecklistLoader(unittest.TestCase):
    def _write_jsonl(self, rows):
        handle = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".jsonl")
        try:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            return handle.name
        finally:
            handle.close()

    def test_normalize_deck_card_id_handles_legacy_aet_prefix(self):
        self.assertEqual(normalize_deck_card_id("AET-IGN-HAM-001"), "IGN-HAM-001")
        self.assertEqual(normalize_deck_card_id("IGN-HAM-001"), "IGN-HAM-001")
        self.assertEqual(normalize_deck_card_id("none"), "")

    def test_decklist_jsonl_loads_groups_and_normalizes_quantity(self):
        path = self._write_jsonl(
            [
                {
                    "Product_ID": "TEST-PRODUCT",
                    "Deck_ID": "TEST-DECK",
                    "Szabályi_Kártya_ID": "AET-IGN-HAM-001",
                    "Kártya_Név": "Teszt Entitas",
                    "Darabszám": "1.0",
                    "Szerep_A_Pakliban": "core",
                    "Megjegyzés": "none",
                },
                {
                    "Product_ID": "TEST-PRODUCT",
                    "Deck_ID": "TEST-DECK",
                    "Szabályi_Kártya_ID": "IGN-HAM-002",
                    "Kártya_Név": "Teszt Ige",
                    "Darabszám": 39.0,
                    "Szerep_A_Pakliban": "core",
                    "Megjegyzés": "none",
                },
            ]
        )
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))

        rows, warnings = load_decklist_rows_jsonl(path)
        grouped = group_decklist_rows(rows)

        self.assertEqual(warnings, [])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["card_id"], "IGN-HAM-001")
        self.assertEqual(rows[0]["quantity"], 1)
        self.assertEqual(rows[1]["quantity"], 39)
        self.assertEqual(list(grouped), ["TEST-DECK"])

    def test_decklist_validation_links_runtime_cards_and_reports_size_and_missing_ids(self):
        rows = [
            {
                "product_id": "TEST-PRODUCT",
                "deck_id": "DECK-40",
                "card_id": "IGN-HAM-001",
                "card_name": "Teszt Entitas",
                "quantity": 20,
            },
            {
                "product_id": "TEST-PRODUCT",
                "deck_id": "DECK-40",
                "card_id": "IGN-HAM-002",
                "card_name": "Teszt Ige",
                "quantity": 20,
            },
            {
                "product_id": "TEST-PRODUCT",
                "deck_id": "DECK-41",
                "card_id": "IGN-HAM-001",
                "card_name": "Teszt Entitas",
                "quantity": 40,
            },
            {
                "product_id": "TEST-PRODUCT",
                "deck_id": "DECK-41",
                "card_id": "IGN-HAM-999",
                "card_name": "Hianyzo Lap",
                "quantity": 1,
            },
        ]
        runtime_cards = [
            SimpleNamespace(card_id="IGN-HAM-001", nev="Teszt Entitas"),
            SimpleNamespace(card_id="IGN-HAM-002", nev="Teszt Ige"),
        ]

        report = validate_decklists(rows, runtime_cards=runtime_cards)

        deck_reports = {item["deck_id"]: item for item in report["decks"]}
        self.assertEqual(deck_reports["DECK-40"]["total_quantity"], 40)
        self.assertEqual(deck_reports["DECK-41"]["total_quantity"], 41)
        self.assertEqual(report["non_40_decks"], [{"deck_id": "DECK-41", "size": 41}])
        self.assertEqual(report["missing_card_ids"], ["IGN-HAM-999"])
        self.assertTrue(any("deck_size_warning:expected=40:actual=41" in warning for warning in report["warnings"]))
        self.assertTrue(any("missing_card_id:IGN-HAM-999" in warning for warning in report["warnings"]))

    def test_load_and_validate_decklists_connects_jsonl_to_runtime_cards(self):
        path = self._write_jsonl(
            [
                {
                    "Product_ID": "TEST-PRODUCT",
                    "Deck_ID": "DECK-40",
                    "Szabályi_Kártya_ID": "AET-IGN-HAM-001",
                    "Kártya_Név": "Teszt Entitas",
                    "Darabszám": 20,
                    "Szerep_A_Pakliban": "core",
                    "Megjegyzés": "none",
                },
                {
                    "Product_ID": "TEST-PRODUCT",
                    "Deck_ID": "DECK-40",
                    "Szabályi_Kártya_ID": "IGN-HAM-002",
                    "Kártya_Név": "Teszt Ige",
                    "Darabszám": "20.0",
                    "Szerep_A_Pakliban": "core",
                    "Megjegyzés": "none",
                },
            ]
        )
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        runtime_cards = [
            {"card_id": "IGN-HAM-001", "kartya_nev": "Teszt Entitas"},
            {"card_id": "IGN-HAM-002", "kartya_nev": "Teszt Ige"},
        ]

        report = load_and_validate_decklists(path, runtime_cards=runtime_cards)

        self.assertEqual(len(report["rows"]), 2)
        self.assertEqual(report["decks"][0]["total_quantity"], 40)
        self.assertEqual(report["warnings"], [])
        self.assertEqual(report["missing_card_ids"], [])


if __name__ == "__main__":
    unittest.main()
