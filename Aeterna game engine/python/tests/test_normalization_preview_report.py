import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "normalization_preview_report.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("normalization_preview_report", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestNormalizationPreviewReport(unittest.TestCase):
    def test_builds_safe_preview_and_skips_manual_audit_rows(self):
        previewer = _load_module()
        audit_report = {
            "normalization_audit": [
                {
                    "object_type": "card",
                    "object_id": "CARD-001",
                    "field": "duration",
                    "lookup_group": "duration",
                    "original_value": "until_turn_end; instant",
                    "value": "until_turn_end",
                    "canonical_value": "until_end_of_turn",
                    "normalization_allowed": True,
                    "requires_audit": False,
                    "notes": "duration preview",
                },
                {
                    "object_type": "card",
                    "object_id": "CARD-001",
                    "field": "effect_tags",
                    "lookup_group": "effect_tag",
                    "original_value": ["return_to_board, damage", "tutor; unknown_effect"],
                    "value": "tutor",
                    "canonical_value": "search",
                    "normalization_allowed": True,
                    "requires_audit": False,
                    "notes": "list preview",
                },
                {
                    "object_type": "card",
                    "object_id": "CARD-001",
                    "field": "trigger",
                    "lookup_group": "trigger",
                    "original_value": "on_summon",
                    "value": "on_summon",
                    "canonical_value": "audit_required",
                    "normalization_allowed": False,
                    "requires_audit": True,
                    "notes": "manual audit",
                },
            ]
        }

        report = previewer.build_normalization_preview_report(audit_report)

        self.assertEqual(report["summary"]["audit_matches_total"], 3)
        self.assertEqual(report["summary"]["preview_items"], 2)
        self.assertEqual(report["summary"]["skipped_requires_audit"], 1)
        self.assertEqual(report["summary"]["applied"], 0)
        self.assertEqual(report["summary"]["field_preview_counts"]["duration"], 1)
        self.assertEqual(report["summary"]["lookup_group_preview_counts"]["effect_tag"], 1)

        duration_preview = _find_preview(report["normalization_preview"], "duration")
        self.assertEqual(duration_preview["original_value"], "until_turn_end; instant")
        self.assertEqual(duration_preview["matched_value"], "until_turn_end")
        self.assertEqual(duration_preview["canonical_value"], "until_end_of_turn")
        self.assertEqual(duration_preview["preview_value"], "until_end_of_turn; instant")
        self.assertEqual(duration_preview["preview_status"], "safe_preview")
        self.assertFalse(duration_preview["applied"])

        effect_preview = _find_preview(report["normalization_preview"], "effect_tags")
        self.assertEqual(
            effect_preview["preview_value"],
            ["return_to_board, damage", "search; unknown_effect"],
        )
        self.assertEqual(effect_preview["preview_status"], "safe_preview")
        self.assertFalse(effect_preview["applied"])

        skipped = report["skipped"]
        self.assertEqual(len(skipped), 1)
        self.assertEqual(skipped[0]["field"], "trigger")
        self.assertEqual(skipped[0]["preview_status"], "manual_audit_required")
        self.assertFalse(skipped[0]["applied"])

    def test_empty_audit_report_returns_empty_preview(self):
        previewer = _load_module()

        report = previewer.build_normalization_preview_report({})

        self.assertEqual(report["normalization_preview"], [])
        self.assertEqual(report["skipped"], [])
        self.assertEqual(report["summary"]["audit_matches_total"], 0)
        self.assertEqual(report["summary"]["preview_items"], 0)
        self.assertEqual(report["summary"]["skipped_requires_audit"], 0)
        self.assertEqual(report["summary"]["applied"], 0)


def _find_preview(rows, field):
    for row in rows:
        if row["field"] == field:
            return row
    raise AssertionError("missing preview row for field: %s" % field)


if __name__ == "__main__":
    unittest.main()
