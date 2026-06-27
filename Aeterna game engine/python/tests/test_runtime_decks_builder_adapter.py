import importlib.util
import json
import shutil
import tempfile
import uuid
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "runtime_decks_builder_adapter.py"
)


def _load_adapter_module():
    spec = importlib.util.spec_from_file_location("runtime_decks_builder_adapter", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestRuntimeDecksBuilderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = _load_adapter_module()
        self.temp_dir = Path(tempfile.gettempdir()) / ("runtime_decks_builder_adapter_%s" % uuid.uuid4().hex)
        self.temp_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.assertFalse(self.temp_dir.exists(), "Deck adapter temp cleanup left directory: %s" % self.temp_dir)

    def test_loads_product_decklists_jsonl_as_runtime_decks(self):
        input_path = self.temp_dir / "PRODUCT_DECKLISTS.jsonl"
        _write_jsonl(
            input_path,
            [
                _decklist_row("TEST-CORE01-IGNIS", "DECK-IGN-HAM-TEST-001", "IGN-HAM-001", 4.0),
                _decklist_row("TEST-CORE01-IGNIS", "DECK-IGN-HAM-TEST-001", "IGN-HAM-002", 2.0),
            ],
        )

        result = self.adapter.load_builder_decks_from_product_decklists_jsonl(input_path)

        self.assertEqual(result["summary"]["records_read"], 2)
        self.assertEqual(result["summary"]["decks_loaded"], 1)
        deck = result["decks"][0]
        self.assertEqual(deck["deck_id"], "DECK-IGN-HAM-TEST-001")
        self.assertEqual(deck["product_id"], "TEST-CORE01-IGNIS")
        self.assertEqual(deck["realm"], "IGNIS")
        self.assertEqual(deck["deck_type"], "test_deck")
        self.assertEqual(deck["card_count"], 6)
        self.assertEqual(
            deck["card_entries"],
            [{"card_id": "IGN-HAM-001", "count": 4}, {"card_id": "IGN-HAM-002", "count": 2}],
        )

    def test_duplicate_card_entries_are_summed(self):
        input_path = self.temp_dir / "PRODUCT_DECKLISTS.jsonl"
        _write_jsonl(
            input_path,
            [
                _decklist_row("TEST-CORE01-IGNIS", "DECK-IGN-HAM-TEST-001", "IGN-HAM-001", 1),
                _decklist_row("TEST-CORE01-IGNIS", "DECK-IGN-HAM-TEST-001", "IGN-HAM-001", 3),
            ],
        )

        result = self.adapter.load_builder_decks_from_product_decklists_jsonl(input_path)

        self.assertEqual(result["decks"][0]["card_entries"], [{"card_id": "IGN-HAM-001", "count": 4}])
        self.assertEqual(result["decks"][0]["card_count"], 4)


def _decklist_row(product_id, deck_id, card_id, count):
    return {
        "Product_ID": product_id,
        "Deck_ID": deck_id,
        "Card_ID": card_id,
        "Darabszám": count,
    }


def _write_jsonl(path, records):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    unittest.main()
