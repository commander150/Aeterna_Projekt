import importlib.util
import json
import shutil
import sys
import tempfile
import uuid
import unittest
from pathlib import Path

from openpyxl import Workbook


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "tools" / "xlsx_export" / "xlsx_export.py"


def load_exporter_module():
    spec = importlib.util.spec_from_file_location("xlsx_export_smoke_target", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


xlsx_export = load_exporter_module()


class TestXlsxExportSmoke(unittest.TestCase):
    def test_profile_export_with_explicit_source_and_output_dirs(self):
        temp_root = Path(tempfile.gettempdir()) / ("xlsx_export_smoke_tmp_%s" % uuid.uuid4().hex)
        try:
            source_dir = temp_root / "source"
            output_dir = temp_root / "output"
            source_dir.mkdir(parents=True)
            output_dir.mkdir(parents=True)
            xlsx_path = source_dir / "sample_lookups.xlsx"
            self._write_minimal_lookups_workbook(xlsx_path)

            exit_code = xlsx_export.main(
                [
                    str(xlsx_path),
                    "--profile",
                    "lookups_runtime",
                    "--source-dir",
                    str(source_dir),
                    "--output-dir",
                    str(output_dir),
                ]
            )

            output_path = output_dir / "LOOKUPS_RUNTIME.jsonl"
            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.is_file())

            lines = [line for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertGreaterEqual(len(lines), 1)

            rows = [json.loads(line) for line in lines]
            self.assertEqual(rows[0]["Lookup_Group"], "card_type")
            self.assertEqual(rows[0]["Value"], "Entitas")
            self.assertIsInstance(rows[0]["Sort_Order"], int)
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)
        self.assertFalse(temp_root.exists(), "XLSX exporter smoke temp cleanup left directory: %s" % temp_root)

    def _write_minimal_lookups_workbook(self, xlsx_path):
        workbook = Workbook()
        try:
            sheet = workbook.active
            sheet.title = "5A. LOOKUPS_RUNTIME"
            sheet.append(
                [
                    "Lookup_Group",
                    "Value",
                    "Label_HU",
                    "Status",
                    "Canonical_Value",
                    "Used_For",
                    "Sort_Order",
                    "Source",
                    "Notes",
                ]
            )
            sheet.append(
                [
                    "card_type",
                    "Entitas",
                    "Entitas",
                    "active",
                    None,
                    "cards.card_type",
                    10.0,
                    "smoke_fixture",
                    "temporary smoke fixture",
                ]
            )
            workbook.save(xlsx_path)
        finally:
            workbook.close()


if __name__ == "__main__":
    unittest.main()
