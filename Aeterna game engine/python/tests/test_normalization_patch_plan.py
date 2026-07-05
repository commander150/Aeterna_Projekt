import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "normalization_patch_plan.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("normalization_patch_plan", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestNormalizationPatchPlan(unittest.TestCase):
    def test_builds_ready_patches_and_blocks_ambiguous_preview_items(self):
        planner = _load_module()
        preview_report = {
            "normalization_preview": [
                _preview("CARD-001", "duration", "until_turn_end", "until_end_of_turn", "until_turn_end; instant"),
                _preview("CARD-001", "duration", "instant", "immediate", "until_turn_end; instant"),
                _preview(
                    "CARD-002",
                    "effect_tags",
                    "return_to_board",
                    "return_to_domain",
                    ["return_to_board, damage", "tutor; unknown"],
                    lookup_group="effect_tag",
                ),
                _preview(
                    "CARD-002",
                    "effect_tags",
                    "tutor",
                    "search",
                    ["return_to_board, damage", "tutor; unknown"],
                    lookup_group="effect_tag",
                ),
                _preview("CARD-003", "duration", "until_turn_end", "until_end_of_turn", "until_turn_end"),
                _preview("CARD-003", "duration", "until_turn_end", "end_of_turn", "until_turn_end"),
                _preview("CARD-004", "duration", "until_turn_end", "until_end_of_turn", "until_turn_end", preview_value=None),
                _preview(
                    "CARD-005",
                    "trigger",
                    "on_summon",
                    "audit_required",
                    "on_summon",
                    allowed=False,
                    audit=True,
                    status="manual_audit_required",
                ),
            ]
        }

        plan = planner.build_normalization_patch_plan(preview_report)

        self.assertEqual(plan["summary"]["preview_items_input"], 8)
        self.assertEqual(plan["summary"]["patches_ready"], 2)
        self.assertEqual(plan["summary"]["blocked_or_ambiguous"], 3)
        self.assertEqual(plan["summary"]["applied"], 0)
        self.assertEqual(plan["summary"]["field_patch_counts"], {"duration": 1, "effect_tags": 1})
        self.assertEqual(plan["summary"]["object_type_patch_counts"], {"card": 2})

        duration_patch = _find_patch(plan["patch_plan"], "CARD-001", "duration")
        self.assertEqual(duration_patch["planned_value"], "until_end_of_turn; immediate")
        self.assertEqual(duration_patch["status"], "ready")
        self.assertFalse(duration_patch["applied"])
        self.assertEqual(len(duration_patch["changes"]), 2)

        list_patch = _find_patch(plan["patch_plan"], "CARD-002", "effect_tags")
        self.assertEqual(list_patch["planned_value"], ["return_to_domain, damage", "search; unknown"])
        self.assertFalse(list_patch["applied"])

        blocked_reasons = {row["object_id"]: row["reason"] for row in plan["blocked_or_ambiguous"]}
        self.assertEqual(blocked_reasons["CARD-003"], "conflicting_preview_values")
        self.assertEqual(blocked_reasons["CARD-004"], "unresolved_preview_value")
        self.assertEqual(blocked_reasons["CARD-005"], "unsupported_preview_status")
        self.assertFalse(any(row["object_id"] == "CARD-005" for row in plan["patch_plan"]))

    def test_empty_preview_report_returns_empty_plan(self):
        planner = _load_module()

        plan = planner.build_normalization_patch_plan({})

        self.assertEqual(plan["patch_plan"], [])
        self.assertEqual(plan["blocked_or_ambiguous"], [])
        self.assertEqual(plan["summary"]["preview_items_input"], 0)
        self.assertEqual(plan["summary"]["patches_ready"], 0)
        self.assertEqual(plan["summary"]["applied"], 0)


def _preview(
    object_id,
    field,
    matched,
    canonical,
    original,
    lookup_group="duration",
    allowed=True,
    audit=False,
    status="safe_preview",
    preview_value="placeholder",
):
    return {
        "object_type": "card",
        "object_id": object_id,
        "field": field,
        "lookup_group": lookup_group,
        "original_value": original,
        "matched_value": matched,
        "canonical_value": canonical,
        "preview_value": preview_value,
        "normalization_allowed": allowed,
        "requires_audit": audit,
        "applied": False,
        "preview_status": status,
        "notes": "test fixture",
    }


def _find_patch(rows, object_id, field):
    for row in rows:
        if row["object_id"] == object_id and row["field"] == field:
            return row
    raise AssertionError("missing patch for %s %s" % (object_id, field))


if __name__ == "__main__":
    unittest.main()
