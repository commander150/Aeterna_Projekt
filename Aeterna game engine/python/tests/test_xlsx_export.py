import csv
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "tools" / "xlsx_export" / "xlsx_export.py"


def load_exporter_module():
    spec = importlib.util.spec_from_file_location("xlsx_export", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


xlsx_export = load_exporter_module()


class TestXlsxExport(unittest.TestCase):
    def setUp(self):
        self.headers = xlsx_export.load_headers(("nĂ©v", "pont", "megjegyzĂ©s"))
        self.records = list(
            xlsx_export.iter_records(
                [
                    ("ĂrvĂ­ztĹ±rĹ‘", 12.0, None),
                    ("MĂˇsodik", 5.5, "rendben"),
                ],
                self.headers,
            )
        )

    def test_skips_empty_cells(self):
        self.assertEqual(self.records[0], {"nĂ©v": "ĂrvĂ­ztĹ±rĹ‘", "pont": 12})
        self.assertEqual(self.records[1]["pont"], 5.5)

    def test_converts_whole_number_floats_to_integers(self):
        self.assertEqual(xlsx_export.normalize_value(5.0), 5)
        self.assertIsInstance(xlsx_export.normalize_value(5.0), int)
        self.assertEqual(xlsx_export.normalize_value(5.5), 5.5)

    def test_literal_none_is_not_empty(self):
        self.assertFalse(xlsx_export.is_empty_value("none"))
        self.assertFalse(xlsx_export.is_empty_value(" NONE "))
        self.assertTrue(xlsx_export.is_empty_value("   "))

    def test_writes_jsonl_with_utf8_characters(self):
        output = io.StringIO()
        count = xlsx_export.write_jsonl(output, self.records)
        records = [json.loads(line) for line in output.getvalue().splitlines()]

        self.assertEqual(count, 2)
        self.assertEqual(records[0]["nĂ©v"], "ĂrvĂ­ztĹ±rĹ‘")

    def test_writes_tsv_with_header(self):
        output = io.StringIO(newline="")
        count = xlsx_export.write_tsv(output, self.headers, self.records)
        rows = list(csv.reader(io.StringIO(output.getvalue()), delimiter="\t"))

        self.assertEqual(count, 2)
        self.assertEqual(rows[0], ["nĂ©v", "pont", "megjegyzĂ©s"])
        self.assertEqual(rows[1], ["ĂrvĂ­ztĹ±rĹ‘", "12", ""])
        self.assertEqual(rows[2], ["MĂˇsodik", "5.5", "rendben"])

    def test_builds_default_output_name_from_source_and_sheet(self):
        path = xlsx_export.default_output_path(Path("MunkaforrĂˇs.xlsx"), "ElsĹ‘/Lap", "jsonl")

        self.assertEqual(path.name, "MunkaforrĂˇs__ElsĹ‘_Lap.jsonl")
        self.assertEqual(path.parent, xlsx_export.DEFAULT_OUTPUT_DIR)

    def test_resolves_runtime_profile_options(self):
        profile, sheet_name, output_path, output_format = xlsx_export.resolve_export_options(
            "runtime_cards",
            None,
            None,
            None,
        )

        self.assertEqual(profile.name, "runtime_cards")
        self.assertEqual(sheet_name, "7. EXPORT_RUNTIME")
        self.assertEqual(output_path.name, "EXPORT_RUNTIME.jsonl")
        self.assertEqual(output_format, "jsonl")

    def test_runtime_cards_accepts_exact_hungarian_headers_without_warning(self):
        warnings = []
        profile = xlsx_export.PROFILES["runtime_cards"]

        headers = xlsx_export.load_headers(
            (
                "Card_ID",
                "Kártya név",
                "Típus",
                "Birodalom",
                "Magnitudó",
                "Aura",
                "ATK",
                "HP",
                "Set_ID",
                "Collector_Number",
            ),
            profile=profile,
            warnings=warnings,
        )
        xlsx_export.validate_profile_headers(headers, profile, warnings)

        self.assertEqual(warnings, [])
        self.assertIn("Kártya név", headers)
        self.assertIn("Típus", headers)
        self.assertIn("Magnitudó", headers)

    def test_runtime_cards_accepts_alias_headers(self):
        warnings = []
        profile = xlsx_export.PROFILES["runtime_cards"]

        headers = xlsx_export.load_headers(
            ("Card_ID", "Kartya nev", "Tipus", "Birodalom", "Magnitudo", "Aura", "Set_ID", "Collector_Number"),
            profile=profile,
            warnings=warnings,
        )
        xlsx_export.validate_profile_headers(headers, profile, warnings)
        records = list(
            xlsx_export.iter_records(
                [("CARD-001", "Sample", "Entitas", "Ignis", 1.0, 2.0, "SET", 1.0)],
                headers,
                profile=profile,
                warnings=warnings,
            )
        )

        self.assertGreaterEqual(len(warnings), 3)
        self.assertEqual(records[0]["Kártya név"], "Sample")
        self.assertEqual(records[0]["Típus"], "Entitas")
        self.assertEqual(records[0]["Magnitudó"], 1)

    def test_decklists_accepts_exact_count_header_without_warning(self):
        warnings = []
        profile = xlsx_export.PROFILES["decklists"]

        headers = xlsx_export.load_headers(
            ("Product_ID", "Deck_ID", "Card_ID", "Darabszám"),
            profile=profile,
            warnings=warnings,
        )
        xlsx_export.validate_profile_headers(headers, profile, warnings)

        self.assertEqual(warnings, [])
        self.assertIn("Darabszám", headers)

    def test_decklists_accepts_count_alias_header(self):
        warnings = []
        profile = xlsx_export.PROFILES["decklists"]

        headers = xlsx_export.load_headers(
            ("Product_ID", "Deck_ID", "Card_ID", "Darabszam"),
            profile=profile,
            warnings=warnings,
        )
        xlsx_export.validate_profile_headers(headers, profile, warnings)
        records = list(
            xlsx_export.iter_records(
                [("PRODUCT-001", "DECK-001", "CARD-001", 2.0)],
                headers,
                profile=profile,
                warnings=warnings,
            )
        )

        self.assertGreaterEqual(len(warnings), 1)
        self.assertEqual(records[0]["Darabszám"], 2)

    def test_required_field_still_errors_without_alias_match(self):
        warnings = []
        profile = xlsx_export.PROFILES["runtime_cards"]
        headers = xlsx_export.load_headers(
            ("Card_ID", "Card_Name", "Típus", "Birodalom", "Magnitudó", "Aura", "Set_ID", "Collector_Number"),
            profile=profile,
            warnings=warnings,
        )

        with self.assertRaises(xlsx_export.ExportError):
            xlsx_export.validate_profile_headers(headers, profile, warnings)

    def test_unknown_extra_header_does_not_block_export(self):
        warnings = []
        profile = xlsx_export.PROFILES["runtime_cards"]
        headers = xlsx_export.load_headers(
            (
                "Card_ID",
                "Kártya név",
                "Típus",
                "Birodalom",
                "Magnitudó",
                "Aura",
                "Set_ID",
                "Collector_Number",
                "Extra_Header",
            ),
            profile=profile,
            warnings=warnings,
        )
        xlsx_export.validate_profile_headers(headers, profile, warnings)
        records = list(
            xlsx_export.iter_records(
                [("CARD-001", "Sample", "Entitas", "Ignis", 1.0, 2.0, "SET", 1.0, "extra")],
                headers,
                profile=profile,
                warnings=warnings,
            )
        )

        self.assertEqual(records[0]["Extra_Header"], "extra")

    def test_generic_sheet_requires_manual_sheet_format_and_output(self):
        with self.assertRaises(xlsx_export.ExportError):
            xlsx_export.resolve_export_options("generic_sheet", "Adatok", None, "jsonl")

    def test_profile_warnings_for_missing_required_field(self):
        warnings = []
        profile = xlsx_export.ExportProfile(
            name="teszt",
            sheet_name="Adatok",
            output_filename="teszt.jsonl",
            output_format="jsonl",
            required_fields=("id",),
            number_fields=("pont",),
        )

        records = list(xlsx_export.iter_records([(None, "nemszĂˇm")], ("id", "pont"), profile=profile, warnings=warnings))

        self.assertEqual(records, [{"pont": "nemszĂˇm"}])
        self.assertIn("id", warnings[0])
        self.assertIn("pont", warnings[1])

    def test_lookups_profiles_keep_literal_none_values(self):
        cases = [
            ("lookups_runtime", "Race"),
            ("lookups_runtime", "Keyword"),
            ("lookups_runtime", "Trigger"),
            ("lookups_print_product", "Reprint_Of"),
            ("lookups_workflow_audit", "Audit_Status"),
            ("lookups_design_catalog", "Generation_Profile"),
        ]
        headers = xlsx_export.LOOKUPS_FIELDS

        for profile_name, lookup_group in cases:
            with self.subTest(profile=profile_name, lookup_group=lookup_group):
                warnings = []
                profile = xlsx_export.PROFILES[profile_name]
                records = list(
                    xlsx_export.iter_records(
                        [(lookup_group, "none", "none", "active", "none", "runtime_validation", 999.0, "CARDS_MASTER", "teszt")],
                        headers,
                        profile=profile,
                        warnings=warnings,
                    )
                )

                self.assertEqual(warnings, [])
                self.assertEqual(len(records), 1)
                self.assertEqual(set(records[0]), set(xlsx_export.LOOKUPS_FIELDS))
                self.assertEqual(records[0]["Value"], "none")
                self.assertEqual(records[0]["Label_HU"], "none")
                self.assertEqual(records[0]["Canonical_Value"], "none")
                self.assertEqual(records[0]["Sort_Order"], 999)

    def test_lookups_profiles_skip_truly_empty_value_with_warning(self):
        warnings = []
        profile = xlsx_export.PROFILES["lookups_runtime"]

        records = list(
            xlsx_export.iter_records(
                [("Race", None, "Race", "active", None, "runtime_validation", 10.0, "CARDS_MASTER", "teszt")],
                xlsx_export.LOOKUPS_FIELDS,
                profile=profile,
                warnings=warnings,
            )
        )

        self.assertEqual(records, [])
        self.assertIn("Value", warnings[0])

    def test_lookups_profiles_fill_empty_canonical_value_from_value(self):
        warnings = []
        profile = xlsx_export.PROFILES["lookups_runtime"]

        records = list(
            xlsx_export.iter_records(
                [("Race", "Ember", "Ember", "active", None, "runtime_validation", 10.0, "CARDS_MASTER", "teszt")],
                xlsx_export.LOOKUPS_FIELDS,
                profile=profile,
                warnings=warnings,
            )
        )

        self.assertEqual(warnings, [])
        self.assertEqual(records[0]["Canonical_Value"], "Ember")

    def test_literal_none_is_allowed_in_optional_number_fields(self):
        warnings = []
        profile = xlsx_export.ExportProfile(
            name="teszt",
            sheet_name="Adatok",
            output_filename="teszt.jsonl",
            output_format="jsonl",
            number_fields=("pont",),
        )

        records = list(xlsx_export.iter_records([("none",)], ("pont",), profile=profile, warnings=warnings))

        self.assertEqual(records, [{"pont": "none"}])
        self.assertEqual(warnings, [])

    def test_menu_selects_numbered_option(self):
        answers = iter(["hibĂˇs", "2"])
        messages = []

        result = xlsx_export.choose_from_menu(
            "Teszt",
            ("elsĹ‘", "mĂˇsodik"),
            input_func=lambda _: next(answers),
            print_func=messages.append,
        )

        self.assertEqual(result, "mĂˇsodik")
        self.assertTrue(any("sorsz" in message for message in messages))

    def test_menu_can_exit(self):
        result = xlsx_export.choose_from_menu(
            "Teszt",
            ("elsĹ‘",),
            input_func=lambda _: "0",
            print_func=lambda _: None,
        )

        self.assertIsNone(result)

    @patch("xlsx_export.DEFAULT_SOURCE_DIR")
    def test_finds_xlsx_files_only_in_source_directory(self, source_dir):
        source_dir.glob.return_value = [
            Path("source/b.xlsx"),
            Path("source/~$temporary.xlsx"),
            Path("source/a.xlsx"),
        ]

        result = xlsx_export.find_xlsx_files()

        source_dir.glob.assert_called_once_with("*.xlsx")
        self.assertEqual([path.name for path in result], ["a.xlsx", "b.xlsx"])

    def test_rejects_source_outside_source_directory(self):
        source_dir = Path("C:/tool/source")

        with self.assertRaises(xlsx_export.ExportError):
            xlsx_export.validate_source_path(Path("C:/other/file.xlsx"), source_dir=source_dir)

    @patch("xlsx_export.load_workbook")
    def test_lists_sheets_in_read_only_data_only_mode(self, load_workbook):
        workbook = MagicMock()
        workbook.sheetnames = ["Adatok", "MĂˇsik lap"]
        load_workbook.return_value = workbook

        result = xlsx_export.list_sheets("source.xlsx")

        self.assertEqual(result, ["Adatok", "MĂˇsik lap"])
        load_workbook.assert_called_once_with("source.xlsx", read_only=True, data_only=True)
        workbook.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
