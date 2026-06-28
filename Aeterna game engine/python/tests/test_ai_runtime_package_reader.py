import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
SCRIPT_PATH = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai" / "runtime_package_reader.py"


def _load_reader_module():
    spec = importlib.util.spec_from_file_location("runtime_package_reader", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["runtime_package_reader"] = module
    spec.loader.exec_module(module)
    return module


class TestAIRuntimePackageReader(unittest.TestCase):
    def setUp(self):
        self.reader = _load_reader_module()

    def test_loads_godot_runtime_package_for_ai_smoke(self):
        package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)
        summary = package.count_summary()

        self.assertGreater(summary["cards_count"], 0)
        self.assertGreater(summary["decks_count"], 0)
        self.assertGreater(summary["lookup_records_count"], 0)
        self.assertGreater(summary["lookup_groups_count"], 0)
        self.assertEqual(summary["deck_reference_error_count"], 0)

        if "IGN-HAM-001" in package.cards_by_id:
            self.assertEqual(package.get_card("IGN-HAM-001")["card_id"], "IGN-HAM-001")
        if "DECK-IGN-HAM-TEST-001" in package.decks_by_id:
            deck = package.get_deck("DECK-IGN-HAM-TEST-001")
        else:
            deck = next(iter(package.decks_by_id.values()))
        self.assertTrue(deck.get("card_entries"))
        first_entry = deck["card_entries"][0]
        self.assertIn(first_entry["card_id"], package.cards_by_id)

    def test_missing_required_file_raises_clear_error(self):
        temp_dir = _make_temp_dir()
        try:
            _write_json(temp_dir / "manifest.json", {"package_id": "test"})
            with self.assertRaisesRegex(self.reader.RuntimePackageReadError, "missing required files"):
                self.reader.load_runtime_package(temp_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_deck_reference_validation_reports_unknown_card_id(self):
        temp_dir = _make_temp_dir()
        try:
            _write_minimal_runtime_package(temp_dir, deck_card_id="MISSING-CARD")

            package = self.reader.load_runtime_package(temp_dir)
            errors = package.validate_deck_card_refs()

            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0]["code"], "DECK_CARD_NOT_FOUND")
            self.assertEqual(errors[0]["deck_id"], "DECK-001")
            self.assertEqual(errors[0]["card_id"], "MISSING-CARD")
            self.assertEqual(package.count_summary()["deck_reference_error_count"], 1)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_get_unknown_card_or_deck_raises_clear_error(self):
        temp_dir = _make_temp_dir()
        try:
            _write_minimal_runtime_package(temp_dir, deck_card_id="CARD-001")
            package = self.reader.load_runtime_package(temp_dir)

            with self.assertRaisesRegex(self.reader.RuntimePackageReadError, "Unknown card_id"):
                package.get_card("NOPE")
            with self.assertRaisesRegex(self.reader.RuntimePackageReadError, "Unknown deck_id"):
                package.get_deck("NOPE")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def _make_temp_dir():
    return Path(tempfile.gettempdir()) / ("aeterna_ai_runtime_package_reader_%s" % uuid.uuid4().hex)


def _write_minimal_runtime_package(package_dir, deck_card_id):
    package_dir.mkdir(parents=True, exist_ok=True)
    _write_json(package_dir / "manifest.json", {"package_id": "test.package"})
    _write_jsonl(
        package_dir / "cards.jsonl",
        [
            {
                "card_id": "CARD-001",
                "name_hu": "Teszt lap",
                "card_type": "Entitas",
                "realm": "IGNIS",
            }
        ],
    )
    _write_jsonl(
        package_dir / "decks.jsonl",
        [
            {
                "deck_id": "DECK-001",
                "card_entries": [{"card_id": deck_card_id, "count": 1}],
            }
        ],
    )
    _write_json(
        package_dir / "lookups.json",
        {
            "lookups": [
                {"lookup_group": "card_type", "value": "Entitas"},
                {"lookup_group": "realm", "value": "IGNIS"},
            ]
        },
    )


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    unittest.main()
