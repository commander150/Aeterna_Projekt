import csv
import io
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import xlsx_export


class TestXlsxExport(unittest.TestCase):
    def setUp(self):
        self.headers = xlsx_export.load_headers(("név", "pont", "megjegyzés"))
        self.records = list(
            xlsx_export.iter_records(
                [
                    ("Árvíztűrő", 12.0, None),
                    ("Második", 5.5, "rendben"),
                ],
                self.headers,
            )
        )

    def test_replaces_empty_cells_with_none(self):
        self.assertEqual(self.records[0], {"név": "Árvíztűrő", "pont": 12, "megjegyzés": "none"})
        self.assertEqual(self.records[1]["pont"], 5.5)

    def test_converts_whole_number_floats_to_integers(self):
        self.assertEqual(xlsx_export.normalize_value(5.0), 5)
        self.assertIsInstance(xlsx_export.normalize_value(5.0), int)
        self.assertEqual(xlsx_export.normalize_value(5.5), 5.5)

    def test_writes_jsonl_with_utf8_characters(self):
        output = io.StringIO()
        count = xlsx_export.write_jsonl(output, self.records)
        records = [json.loads(line) for line in output.getvalue().splitlines()]

        self.assertEqual(count, 2)
        self.assertEqual(records[0]["név"], "Árvíztűrő")

    def test_writes_tsv_with_header(self):
        output = io.StringIO(newline="")
        count = xlsx_export.write_tsv(output, self.headers, self.records)
        rows = list(csv.reader(io.StringIO(output.getvalue()), delimiter="\t"))

        self.assertEqual(count, 2)
        self.assertEqual(rows[0], ["név", "pont", "megjegyzés"])
        self.assertEqual(rows[1], ["Árvíztűrő", "12", "none"])
        self.assertEqual(rows[2], ["Második", "5.5", "rendben"])

    def test_builds_default_output_name_from_source_and_sheet(self):
        path = xlsx_export.default_output_path(Path("Munkaforrás.xlsx"), "Első/Lap", "jsonl")

        self.assertEqual(path.name, "Munkaforrás__Első_Lap.jsonl")
        self.assertEqual(path.parent, xlsx_export.DEFAULT_OUTPUT_DIR)

    def test_menu_selects_numbered_option(self):
        answers = iter(["hibás", "2"])
        messages = []

        result = xlsx_export.choose_from_menu(
            "Teszt",
            ("első", "második"),
            input_func=lambda _: next(answers),
            print_func=messages.append,
        )

        self.assertEqual(result, "második")
        self.assertIn("Érvénytelen választás. Adj meg egy sorszámot.", messages)

    def test_menu_can_exit(self):
        result = xlsx_export.choose_from_menu(
            "Teszt",
            ("első",),
            input_func=lambda _: "0",
            print_func=lambda _: None,
        )

        self.assertIsNone(result)

    @patch("xlsx_export.SOURCE_DIR")
    def test_finds_xlsx_files_only_in_source_directory(self, source_dir):
        source_dir.glob.return_value = [
            Path("source/b.xlsx"),
            Path("source/~$temporary.xlsx"),
            Path("source/a.xlsx"),
        ]

        result = xlsx_export.find_xlsx_files()

        source_dir.glob.assert_called_once_with("*.xlsx")
        self.assertEqual([path.name for path in result], ["a.xlsx", "b.xlsx"])

    @patch("xlsx_export.SOURCE_DIR")
    def test_rejects_source_outside_source_directory(self, source_dir):
        source_dir.resolve.return_value = Path("C:/tool/source")

        with self.assertRaisesRegex(xlsx_export.ExportError, "ebben a mappában"):
            xlsx_export.validate_source_path(Path("C:/other/file.xlsx"))

    @patch("xlsx_export.load_workbook")
    def test_lists_sheets_in_read_only_data_only_mode(self, load_workbook):
        workbook = MagicMock()
        workbook.sheetnames = ["Adatok", "Másik lap"]
        load_workbook.return_value = workbook

        result = xlsx_export.list_sheets("source.xlsx")

        self.assertEqual(result, ["Adatok", "Másik lap"])
        load_workbook.assert_called_once_with("source.xlsx", read_only=True, data_only=True)
        workbook.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
