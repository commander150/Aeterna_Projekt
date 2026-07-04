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

        temp_dir = Path(tempfile.gettempdir()) / ("aeterna_fixture_runtime_package_%s" % uuid.uuid4().hex)
        try:
            output_dir = Path(temp_dir) / "fixture_runtime_package"
            result = builder.build_package(output_dir)

            self.assertEqual(result["output_dir"], output_dir)
            self.assertTrue(output_dir.is_dir())

            expected_files = {
                "manifest.json",
                "cards.jsonl",
                "decks.jsonl",
                "lookups.json",
                "aliases.json",
                "normalization_aliases.json",
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
            diagnostics = json.loads((output_dir / "diagnostics.json").read_text(encoding="utf-8"))["diagnostics"]
            self.assertEqual(diagnostics[0]["code"], "MANUAL_REVIEW_PLACEHOLDER")
            normalization_aliases = json.loads(
                (output_dir / "normalization_aliases.json").read_text(encoding="utf-8")
            )
            self.assertEqual(normalization_aliases["normalization_aliases"], [])
            self.assertEqual(normalization_aliases["summary"]["records_loaded"], 0)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self.assertFalse(temp_dir.exists(), "Sample runtime package test temp cleanup left directory: %s" % temp_dir)

    def test_build_package_accepts_optional_export_runtime_cards_input(self):
        builder = _load_builder_module()

        temp_dir = Path(tempfile.gettempdir()) / ("aeterna_fixture_runtime_package_%s" % uuid.uuid4().hex)
        try:
            export_cards_path = temp_dir / "EXPORT_RUNTIME.jsonl"
            output_dir = temp_dir / "fixture_runtime_package"
            temp_dir.mkdir(parents=True)
            _write_jsonl(export_cards_path, _fixture_export_records_for_builder(builder._fixture_cards()))

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

        temp_dir = Path(tempfile.gettempdir()) / ("aeterna_fixture_runtime_package_%s" % uuid.uuid4().hex)
        try:
            export_decks_path = temp_dir / "PRODUCT_DECKLISTS.jsonl"
            export_lookups_path = temp_dir / "LOOKUPS_RUNTIME.jsonl"
            output_dir = temp_dir / "fixture_runtime_package"
            temp_dir.mkdir(parents=True)
            _write_jsonl(
                export_decks_path,
                [
                    _fixture_decklist_row("SMP-IGN-001", 2),
                    _fixture_decklist_row("SMP-IGN-002", 2),
                    _fixture_decklist_row("SMP-IGN-003", 1),
                ],
            )
            _write_jsonl(export_lookups_path, _fixture_lookup_rows_for_builder())

            result = builder.build_package(
                output_dir,
                export_runtime_decks_path=export_decks_path,
                export_runtime_lookups_path=export_lookups_path,
            )

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
            self.assertEqual(manifest["source_files"][1]["type"], "lookups_runtime_jsonl")
            self.assertEqual(manifest["source_files"][2]["type"], "product_decklists_jsonl")
            self.assertEqual(manifest["source_files"][2]["summary"]["decks_loaded"], 1)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self.assertFalse(temp_dir.exists(), "Export runtime decks build test temp cleanup left directory: %s" % temp_dir)

    def test_build_package_accepts_optional_export_runtime_lookups_input(self):
        builder = _load_builder_module()

        temp_dir = Path(tempfile.gettempdir()) / ("aeterna_fixture_runtime_package_%s" % uuid.uuid4().hex)
        try:
            export_lookups_path = temp_dir / "LOOKUPS_RUNTIME.jsonl"
            output_dir = temp_dir / "fixture_runtime_package"
            temp_dir.mkdir(parents=True)
            _write_jsonl(export_lookups_path, _fixture_lookup_rows_for_builder())

            result = builder.build_package(output_dir, export_runtime_lookups_path=export_lookups_path)

            self.assertEqual(result["output_dir"], output_dir)
            self.assertFalse(result["validation_summary"]["blocking"])
            lookups = json.loads((output_dir / "lookups.json").read_text(encoding="utf-8"))["lookups"]
            self.assertIn({"lookup_group": "realm", "value": "Ignis"}, _lookup_key_values(lookups))
            self.assertIn({"lookup_group": "card_type", "value": "Entitas"}, _lookup_key_values(lookups))

            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_files"][1]["type"], "lookups_runtime_jsonl")
            self.assertEqual(manifest["source_files"][1]["summary"]["lookups_loaded"], len(_fixture_lookup_rows_for_builder()))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self.assertFalse(temp_dir.exists(), "Export runtime lookups build test temp cleanup left directory: %s" % temp_dir)

    def test_export_derived_build_does_not_include_sample_manual_review_diagnostic(self):
        builder = _load_builder_module()

        temp_dir = Path(tempfile.gettempdir()) / ("aeterna_fixture_runtime_package_%s" % uuid.uuid4().hex)
        try:
            export_cards_path = temp_dir / "EXPORT_RUNTIME.jsonl"
            export_decks_path = temp_dir / "PRODUCT_DECKLISTS.jsonl"
            export_lookups_path = temp_dir / "LOOKUPS_RUNTIME.jsonl"
            output_dir = temp_dir / "fixture_runtime_package"
            temp_dir.mkdir(parents=True)
            _write_jsonl(export_cards_path, _fixture_export_records_for_builder(builder._fixture_cards()))
            _write_jsonl(export_decks_path, [_fixture_decklist_row(card["card_id"], 1) for card in builder._fixture_cards()])
            _write_jsonl(export_lookups_path, _fixture_lookup_rows_for_builder())

            result = builder.build_package(
                output_dir,
                export_runtime_cards_path=export_cards_path,
                export_runtime_decks_path=export_decks_path,
                export_runtime_lookups_path=export_lookups_path,
            )

            self.assertFalse(result["validation_summary"]["blocking"])
            diagnostics = json.loads((output_dir / "diagnostics.json").read_text(encoding="utf-8"))["diagnostics"]
            self.assertEqual(diagnostics, [])
            report = (output_dir / "build_report.md").read_text(encoding="utf-8")
            self.assertIn("Warningok szama: 0", report)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self.assertFalse(temp_dir.exists(), "Export-derived build test temp cleanup left directory: %s" % temp_dir)


def _fixture_export_records_for_builder(fixture_cards):
    mapper = _load_mapper_module()
    records = []
    for card in fixture_cards:
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


def _fixture_decklist_row(card_id, count):
    return {
        "Product_ID": "TEST-CORE01-IGNIS",
        "Deck_ID": "DECK-IGN-HAM-TEST-001",
        "Card_ID": card_id,
        "Darabszám": count,
    }


def _fixture_lookup_rows_for_builder():
    return [
        _lookup_row("Card_Type", "Entitas"),
        _lookup_row("Card_Type", "Ige"),
        _lookup_row("Card_Type", "Rituale"),
        _lookup_row("Card_Type", "Jel"),
        _lookup_row("Card_Type", "Sik"),
        _lookup_row("Realm", "Ignis"),
        _lookup_row("Realm", "IGNIS"),
    ]


def _lookup_row(group, value):
    return {
        "Lookup_Group": group,
        "Value": value,
        "Label_HU": value,
        "Status": "active",
        "Canonical_Value": value,
        "Used_For": "runtime_validation",
        "Sort_Order": 10,
        "Source": "test",
        "Notes": "temporary test fixture",
    }


def _lookup_key_values(lookups):
    return [{"lookup_group": item["lookup_group"], "value": item["value"]} for item in lookups]


if __name__ == "__main__":
    unittest.main()
