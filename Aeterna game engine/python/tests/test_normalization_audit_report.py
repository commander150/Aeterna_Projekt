import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "runtime_package"
    / "normalization_audit_report.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("normalization_audit_report", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestNormalizationAuditReport(unittest.TestCase):
    def test_reports_legacy_alias_matches_without_applying_normalization(self):
        reporter = _load_module()
        cards = [
            {
                "card_id": "CARD-001",
                "card_type": "Entitás",
                "realm": "IGNIS_OLD",
                "clan": "Hamvaskez",
            },
            {
                "card_id": "CARD-002",
                "card_type": "entity",
                "realm": "ignis",
                "clan": "UnknownClan",
            },
        ]
        decks = [
            {
                "deck_id": "DECK-001",
                "realm": "ignis",
                "deck_type": "starter_old",
            }
        ]
        normalization_aliases = {
            "normalization_aliases": [
                {
                    "lookup_group": "card_type",
                    "alias_value": "Entitás",
                    "canonical_value": "entity",
                    "normalization_allowed": True,
                    "requires_audit": False,
                    "notes": "Safe preview card type alias.",
                },
                {
                    "lookup_group": "realm",
                    "alias_value": "IGNIS_OLD",
                    "canonical_value": "audit_required",
                    "normalization_allowed": False,
                    "requires_audit": True,
                    "notes": "Realm alias needs manual audit.",
                },
                {
                    "lookup_group": "deck_type",
                    "alias_value": "starter_old",
                    "canonical_value": "starter",
                    "normalization_allowed": True,
                    "requires_audit": False,
                    "notes": "Deck type legacy alias.",
                },
            ]
        }

        report = reporter.build_normalization_audit_report(cards, decks, normalization_aliases)

        self.assertEqual(report["summary"]["checked_objects"], 3)
        self.assertEqual(report["summary"]["checked_values"], 8)
        self.assertEqual(report["summary"]["matches_total"], 3)
        self.assertEqual(report["summary"]["normalization_allowed"], 2)
        self.assertEqual(report["summary"]["requires_audit"], 1)
        self.assertEqual(report["summary"]["unknown_or_unmapped"], 5)

        rows = report["normalization_audit"]
        self.assertEqual({row["match_type"] for row in rows}, {"legacy_alias"})
        self.assertTrue(all(row["applied"] is False for row in rows))

        card_type_row = _find_row(rows, "card", "CARD-001", "card_type")
        self.assertEqual(card_type_row["canonical_value"], "entity")
        self.assertTrue(card_type_row["normalization_allowed"])
        self.assertFalse(card_type_row["requires_audit"])
        self.assertEqual(card_type_row["suggested_action"], "safe_normalization_preview")

        realm_row = _find_row(rows, "card", "CARD-001", "realm")
        self.assertEqual(realm_row["canonical_value"], "audit_required")
        self.assertFalse(realm_row["normalization_allowed"])
        self.assertTrue(realm_row["requires_audit"])
        self.assertEqual(realm_row["suggested_action"], "manual_audit_required")

        deck_type_row = _find_row(rows, "deck", "DECK-001", "deck_type")
        self.assertEqual(deck_type_row["canonical_value"], "starter")
        self.assertTrue(deck_type_row["normalization_allowed"])
        self.assertFalse(deck_type_row["requires_audit"])

        self.assertFalse(any(row["value"] == "UnknownClan" for row in rows))


def _find_row(rows, object_type, object_id, field):
    for row in rows:
        if row["object_type"] == object_type and row["object_id"] == object_id and row["field"] == field:
            return row
    raise AssertionError("missing row: %s %s %s" % (object_type, object_id, field))


if __name__ == "__main__":
    unittest.main()
