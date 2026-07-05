import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "tools" / "runtime_package" / "normalization_apply.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("normalization_apply", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestNormalizationApply(unittest.TestCase):
    def test_ready_patch_updates_card_field(self):
        module = _load_module()
        cards = [{"card_id": "CARD-1", "duration": "kor vege"}]
        decks = []

        report = module.apply_normalization_patch_plan(
            cards,
            decks,
            _patch_plan([_patch("card", "CARD-1", "duration", "kor vege", "until_end_of_turn")]),
            enabled=True,
        )

        self.assertEqual(cards[0]["duration"], "until_end_of_turn")
        self.assertEqual(report["summary"]["applied"], 1)
        self.assertEqual(report["summary"]["conflicts"], 0)
        self.assertTrue(report["applied_patches"][0]["applied"])

    def test_ready_patch_updates_deck_field(self):
        module = _load_module()
        cards = []
        decks = [{"deck_id": "DECK-1", "realm": "Ignis"}]

        report = module.apply_normalization_patch_plan(
            cards,
            decks,
            _patch_plan([_patch("deck", "DECK-1", "realm", "Ignis", "IGNIS")]),
            enabled=True,
        )

        self.assertEqual(decks[0]["realm"], "IGNIS")
        self.assertEqual(report["summary"]["applied"], 1)

    def test_original_value_mismatch_is_conflict_and_does_not_mutate(self):
        module = _load_module()
        cards = [{"card_id": "CARD-1", "duration": "current"}]

        report = module.apply_normalization_patch_plan(
            cards,
            [],
            _patch_plan([_patch("card", "CARD-1", "duration", "old", "new")]),
            enabled=True,
        )

        self.assertEqual(cards[0]["duration"], "current")
        self.assertEqual(report["summary"]["applied"], 0)
        self.assertEqual(report["summary"]["conflicts"], 1)
        self.assertEqual(report["skipped_patches"][0]["reason"], "original_value_mismatch")

    def test_missing_object_is_conflict(self):
        module = _load_module()

        report = module.apply_normalization_patch_plan(
            [],
            [],
            _patch_plan([_patch("card", "MISSING", "duration", "old", "new")]),
            enabled=True,
        )

        self.assertEqual(report["summary"]["conflicts"], 1)
        self.assertEqual(report["skipped_patches"][0]["reason"], "missing_object")

    def test_missing_field_is_conflict(self):
        module = _load_module()
        cards = [{"card_id": "CARD-1"}]

        report = module.apply_normalization_patch_plan(
            cards,
            [],
            _patch_plan([_patch("card", "CARD-1", "duration", "old", "new")]),
            enabled=True,
        )

        self.assertEqual(report["summary"]["conflicts"], 1)
        self.assertEqual(report["skipped_patches"][0]["reason"], "missing_field")

    def test_null_planned_value_is_conflict(self):
        module = _load_module()
        cards = [{"card_id": "CARD-1", "duration": "old"}]

        report = module.apply_normalization_patch_plan(
            cards,
            [],
            _patch_plan([_patch("card", "CARD-1", "duration", "old", None)]),
            enabled=True,
        )

        self.assertEqual(cards[0]["duration"], "old")
        self.assertEqual(report["summary"]["conflicts"], 1)
        self.assertEqual(report["skipped_patches"][0]["reason"], "missing_planned_value")

    def test_disabled_mode_does_not_mutate(self):
        module = _load_module()
        cards = [{"card_id": "CARD-1", "duration": "old"}]

        report = module.apply_normalization_patch_plan(
            cards,
            [],
            _patch_plan([_patch("card", "CARD-1", "duration", "old", "new")]),
            enabled=False,
        )

        self.assertEqual(cards[0]["duration"], "old")
        self.assertFalse(report["summary"]["enabled"])
        self.assertEqual(report["summary"]["patches_input"], 1)
        self.assertEqual(report["summary"]["applied"], 0)

    def test_conflict_blocks_all_patches(self):
        module = _load_module()
        cards = [
            {"card_id": "CARD-1", "duration": "old"},
            {"card_id": "CARD-2", "duration": "current"},
        ]

        report = module.apply_normalization_patch_plan(
            cards,
            [],
            _patch_plan(
                [
                    _patch("card", "CARD-1", "duration", "old", "new"),
                    _patch("card", "CARD-2", "duration", "old", "new"),
                ]
            ),
            enabled=True,
        )

        self.assertEqual(cards[0]["duration"], "old")
        self.assertEqual(cards[1]["duration"], "current")
        self.assertEqual(report["summary"]["applied"], 0)
        self.assertEqual(report["summary"]["conflicts"], 1)


def _patch_plan(patches, blocked=None):
    return {
        "patch_plan": patches,
        "blocked_or_ambiguous": blocked or [],
        "summary": {
            "patches_ready": len(patches),
            "blocked_or_ambiguous": len(blocked or []),
            "applied": 0,
        },
    }


def _patch(object_type, object_id, field, original_value, planned_value):
    return {
        "object_type": object_type,
        "object_id": object_id,
        "field": field,
        "original_value": original_value,
        "planned_value": planned_value,
        "status": "ready",
        "applied": False,
        "changes": [],
    }


if __name__ == "__main__":
    unittest.main()
