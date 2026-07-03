import importlib.util
import io
import sys
import unittest
from pathlib import Path

from openpyxl import Workbook


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "runtime_legacy_aliases_reader.py"
)


def _load_reader_module():
    spec = importlib.util.spec_from_file_location("runtime_legacy_aliases_reader", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["runtime_legacy_aliases_reader"] = module
    spec.loader.exec_module(module)
    return module


class TestRuntimeLegacyAliasesReader(unittest.TestCase):
    def setUp(self):
        self.reader = _load_reader_module()

    def test_reads_legacy_aliases_and_marks_audit_required_rows(self):
        workbook_bytes = _build_workbook(
            [
                _alias_row("Card_Type", "tactic", "ritual", "runtime_normalization; audit", 10.0),
                _alias_row("card type", "spell", "audit_required", "runtime_normalization", 20),
                _alias_row("Realm", "", "ignis", "runtime_normalization", 30),
                _alias_row("Effect-Tag", "direct damage", None, "runtime_normalization, audit", 40.0),
            ]
        )

        result = self.reader.load_runtime_legacy_aliases_from_xlsx(workbook_bytes)

        self.assertEqual(result["summary"]["records_read"], 4)
        self.assertEqual(result["summary"]["aliases_loaded"], 3)
        self.assertEqual(result["summary"]["skipped_empty_value"], 1)
        self.assertEqual(result["summary"]["requires_audit_count"], 2)
        self.assertEqual(result["summary"]["normalization_allowed_count"], 1)

        normal_alias = result["aliases"][0]
        self.assertEqual(normal_alias["lookup_group"], "card_type")
        self.assertEqual(normal_alias["alias_value"], "tactic")
        self.assertEqual(normal_alias["canonical_value"], "ritual")
        self.assertEqual(normal_alias["used_for"], ["runtime_normalization", "audit"])
        self.assertEqual(normal_alias["sort_order"], 10)
        self.assertFalse(normal_alias["requires_audit"])
        self.assertTrue(normal_alias["normalization_allowed"])

        audit_alias = result["aliases"][1]
        self.assertEqual(audit_alias["lookup_group"], "card_type")
        self.assertEqual(audit_alias["canonical_value"], "audit_required")
        self.assertTrue(audit_alias["requires_audit"])
        self.assertFalse(audit_alias["normalization_allowed"])

        missing_canonical_alias = result["aliases"][2]
        self.assertEqual(missing_canonical_alias["lookup_group"], "effect_tag")
        self.assertEqual(missing_canonical_alias["used_for"], ["runtime_normalization", "audit"])
        self.assertEqual(missing_canonical_alias["canonical_value"], "none")
        self.assertTrue(missing_canonical_alias["requires_audit"])
        self.assertFalse(missing_canonical_alias["normalization_allowed"])

    def test_missing_legacy_alias_sheet_is_error(self):
        workbook = Workbook()
        workbook.active.title = "RUNTIME_CORE"
        workbook_bytes = io.BytesIO()
        workbook.save(workbook_bytes)
        workbook_bytes.seek(0)
        workbook.close()

        with self.assertRaises(self.reader.RuntimeLegacyAliasesReaderError):
            self.reader.load_runtime_legacy_aliases_from_xlsx(workbook_bytes)


def _build_workbook(rows):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "RUNTIME_LEGACY_ALIAS"
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
    for row in rows:
        sheet.append(row)

    workbook_bytes = io.BytesIO()
    workbook.save(workbook_bytes)
    workbook_bytes.seek(0)
    workbook.close()
    return workbook_bytes


def _alias_row(group, value, canonical_value, used_for, sort_order):
    return [
        group,
        value,
        value,
        "legacy",
        canonical_value,
        used_for,
        sort_order,
        "test",
        "in-memory fixture",
    ]


if __name__ == "__main__":
    unittest.main()
