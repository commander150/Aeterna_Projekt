import importlib.util
import json
import shutil
import tempfile
import uuid
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "tools" / "runtime_package" / "build_sample_runtime_package.py"
MAPPER_PATH = Path(__file__).resolve().parents[1] / "tools" / "runtime_package" / "runtime_card_mapper.py"


def _load_builder_module():
    spec = importlib.util.spec_from_file_location("build_sample_runtime_package", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_mapper_module():
    spec = importlib.util.spec_from_file_location("runtime_card_mapper", MAPPER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestBuildSampleRuntimePackage(unittest.TestCase):
    def test_build_sample_runtime_package_smoke(self):
        builder = _load_builder_module()

        temp_dir = Path(tempfile.gettempdir()) / ("aeterna_sample_runtime_package_%s" % uuid.uuid4().hex)
        try:
            output_dir = Path(temp_dir) / "sample_runtime_package"
            result = builder.build_package(output_dir)

            self.assertEqual(result["output_dir"], output_dir)
            self.assertTrue(output_dir.is_dir())

            expected_files = {
                "manifest.json",
                "cards.jsonl",
                "decks.jsonl",
                "lookups.json",
                "aliases.json",
                "ability_registry.json",
                "engine_support.json",
                "diagnostics.json",
                "build_report.md",
            }
            self.assertEqual({path.name for path in output_dir.iterdir()}, expected_files)

            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            manifest_files = {item["path"] for item in manifest["files"]}
            self.assertEqual(manifest_files, expected_files)
            self.assertFalse(manifest["validation_summary"]["blocking"])

            cards = [
                json.loads(line)
                for line in (output_dir / "cards.jsonl").read_text(encoding="utf-8").splitlines()
                if line
            ]
            decks = [
                json.loads(line)
                for line in (output_dir / "decks.jsonl").read_text(encoding="utf-8").splitlines()
                if line
            ]

            self.assertGreaterEqual(len(cards), 5)
            self.assertGreaterEqual(len(decks), 1)
            self.assertTrue(all(isinstance(card["magnitude"], int) for card in cards))
            self.assertTrue(all(isinstance(card["keywords"], list) for card in cards))

            card_ids = {card["card_id"] for card in cards}
            for deck in decks:
                for entry in deck["card_entries"]:
                    self.assertIn(entry["card_id"], card_ids)

            report = (output_dir / "build_report.md").read_text(encoding="utf-8")
            self.assertIn("Kartyak szama: 5", report)
            self.assertIn("Paklik szama: 1", report)
            self.assertIn("Warningok szama: 1", report)
            self.assertIn("Blocking hibak szama: 0", report)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self.assertFalse(temp_dir.exists(), "Sample runtime package test temp cleanup left directory: %s" % temp_dir)

    def test_build_package_accepts_optional_export_runtime_cards_input(self):
        builder = _load_builder_module()

        temp_dir = Path(tempfile.gettempdir()) / ("aeterna_sample_runtime_package_%s" % uuid.uuid4().hex)
        try:
            export_cards_path = temp_dir / "EXPORT_RUNTIME.jsonl"
            output_dir = temp_dir / "sample_runtime_package"
            temp_dir.mkdir(parents=True)
            _write_jsonl(export_cards_path, _sample_export_records_for_builder(builder._sample_cards()))

            result = builder.build_package(output_dir, export_runtime_cards_path=export_cards_path)

            self.assertEqual(result["output_dir"], output_dir)
            self.assertFalse(result["validation_summary"]["blocking"])
            cards = [
                json.loads(line)
                for line in (output_dir / "cards.jsonl").read_text(encoding="utf-8").splitlines()
                if line
            ]
            self.assertEqual(len(cards), 5)
            self.assertTrue(all(card["runtime_status"] == "mapped_from_export" for card in cards))
            self.assertTrue(all(card["engine_support_status"] == "not_evaluated" for card in cards))

            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_files"][0]["type"], "in_code_fixture")
            self.assertEqual(manifest["source_files"][1]["type"], "export_runtime_cards_jsonl")
            self.assertEqual(manifest["source_files"][1]["summary"]["records_loaded"], 5)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self.assertFalse(temp_dir.exists(), "Export runtime cards build test temp cleanup left directory: %s" % temp_dir)

    def test_build_package_accepts_optional_export_runtime_decks_input(self):
        builder = _load_builder_module()

        temp_dir = Path(tempfile.gettempdir()) / ("aeterna_sample_runtime_package_%s" % uuid.uuid4().hex)
        try:
            export_decks_path = temp_dir / "PRODUCT_DECKLISTS.jsonl"
            output_dir = temp_dir / "sample_runtime_package"
            temp_dir.mkdir(parents=True)
            _write_jsonl(
                export_decks_path,
                [
                    _sample_decklist_row("SMP-IGN-001", 2),
                    _sample_decklist_row("SMP-IGN-002", 2),
                    _sample_decklist_row("SMP-IGN-003", 1),
                ],
            )

            result = builder.build_package(output_dir, export_runtime_decks_path=export_decks_path)

            self.assertEqual(result["output_dir"], output_dir)
            self.assertFalse(result["validation_summary"]["blocking"])
            decks = [
                json.loads(line)
                for line in (output_dir / "decks.jsonl").read_text(encoding="utf-8").splitlines()
                if line
            ]
            self.assertEqual(len(decks), 1)
            self.assertEqual(decks[0]["deck_id"], "DECK-IGN-HAM-TEST-001")
            self.assertEqual(decks[0]["card_count"], 5)

            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_files"][1]["type"], "product_decklists_jsonl")
            self.assertEqual(manifest["source_files"][1]["summary"]["decks_loaded"], 1)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self.assertFalse(temp_dir.exists(), "Export runtime decks build test temp cleanup left directory: %s" % temp_dir)


def _sample_export_records_for_builder(sample_cards):
    mapper = _load_mapper_module()
    records = []
    for card in sample_cards:
        values_by_target = {
            "card_id": card["card_id"],
            "name_hu": card["name_hu"],
            "card_type": card["card_type"],
            "realm": card["realm"],
            "clan": card["clan"],
            "species": "none",
            "class": "none",
            "magnitude": card["magnitude"],
            "aura_cost": card["aura_cost"],
            "atk": card["atk"],
            "hp": card["hp"],
            "text_hu": "Sample exporter text.",
            "structured_ability": "sample_module()",
            "recognized_zone": "none",
            "keywords": ";".join(card["keywords"]),
            "trigger": "none",
            "target": "none",
            "effect_tags": "sample",
            "duration": "none",
            "condition": "none",
            "machine_description": "Sample exporter machine text.",
            "interpretation_status": card["interpretation_status"],
            "engine_notes": "Builder optional input test.",
        }
        records.append(
            {
                source_field: values_by_target[target_field]
                for source_field, target_field in mapper.FIELD_MAP.items()
            }
        )
    return records


def _write_jsonl(path, records):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def _sample_decklist_row(card_id, count):
    return {
        "Product_ID": "TEST-CORE01-IGNIS",
        "Deck_ID": "DECK-IGN-HAM-TEST-001",
        "Card_ID": card_id,
        "Darabszám": count,
    }


if __name__ == "__main__":
    unittest.main()
