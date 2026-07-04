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
                "realm": "IGNIS_OLD",
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
        self.assertEqual(report["summary"]["checked_values"], 7)
        self.assertEqual(report["summary"]["matches_total"], 3)
        self.assertEqual(report["summary"]["normalization_allowed"], 1)
        self.assertEqual(report["summary"]["requires_audit"], 2)
        self.assertEqual(report["summary"]["unknown_or_unmapped"], 4)

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

        deck_realm_row = _find_row(rows, "deck", "DECK-001", "realm")
        self.assertEqual(deck_realm_row["canonical_value"], "audit_required")
        self.assertFalse(deck_realm_row["normalization_allowed"])
        self.assertTrue(deck_realm_row["requires_audit"])

        self.assertFalse(any(row["value"] == "UnknownClan" for row in rows))

    def test_structured_runtime_fields_are_audited_with_controlled_tokenization(self):
        reporter = _load_module()
        cards = [
            {
                "card_id": "CARD-STRUCTURED-001",
                "card_type": "entity",
                "realm": "ignis",
                "clan": "KnownClan",
                "species": "Human_Old",
                "class": "Warrior_Old",
                "recognized_zone": "lane, horizont",
                "keywords": ["celerity_old", "unknown_keyword"],
                "trigger": "on_summon; none",
                "target": "enemy_spell, self",
                "effect_tags": ["return_to_board, damage", "tutor; unknown_effect"],
                "duration": "until_turn_end; instant",
                "condition": "once_per_turn, none",
                "interpretation_status": "tiszta",
            }
        ]
        normalization_aliases = {
            "normalization_aliases": [
                _alias("race", "Human_Old", "human"),
                _alias("class", "Warrior_Old", "warrior"),
                _alias("zone", "lane", "current"),
                _alias("keyword", "celerity_old", "celerity"),
                _alias("trigger", "on_summon", "audit_required", allowed=False, audit=True),
                _alias("target", "enemy_spell", "enemy_incantation_or_ritual"),
                _alias("effect_tag", "return_to_board", "return_to_domain"),
                _alias("effect_tag", "tutor", "search"),
                _alias("duration", "until_turn_end", "until_end_of_turn"),
                _alias("condition", "once_per_turn", "if_once_per_turn_available"),
                _alias("interpretation_status", "tiszta", "passive_or_simple"),
            ]
        }

        report = reporter.build_normalization_audit_report(cards, [], normalization_aliases)

        self.assertEqual(report["summary"]["checked_objects"], 1)
        self.assertEqual(report["summary"]["checked_values"], 22)
        self.assertEqual(report["summary"]["matches_total"], 11)
        self.assertEqual(report["summary"]["normalization_allowed"], 10)
        self.assertEqual(report["summary"]["requires_audit"], 1)
        self.assertEqual(report["summary"]["unknown_or_unmapped"], 11)
        self.assertEqual(report["summary"]["field_matches"]["effect_tags"], 2)
        self.assertEqual(report["summary"]["lookup_group_matches"]["effect_tag"], 2)

        rows = report["normalization_audit"]
        self.assertTrue(all(row["applied"] is False for row in rows))
        self.assertEqual(_find_row(rows, "card", "CARD-STRUCTURED-001", "species", "Human_Old")["lookup_group"], "race")
        self.assertEqual(_find_row(rows, "card", "CARD-STRUCTURED-001", "class", "Warrior_Old")["canonical_value"], "warrior")
        self.assertEqual(_find_row(rows, "card", "CARD-STRUCTURED-001", "effect_tags", "return_to_board")["canonical_value"], "return_to_domain")
        self.assertEqual(_find_row(rows, "card", "CARD-STRUCTURED-001", "effect_tags", "tutor")["canonical_value"], "search")
        self.assertTrue(_find_row(rows, "card", "CARD-STRUCTURED-001", "trigger", "on_summon")["requires_audit"])
        self.assertEqual(_find_row(rows, "card", "CARD-STRUCTURED-001", "duration", "until_turn_end")["canonical_value"], "until_end_of_turn")
        self.assertEqual(_find_row(rows, "card", "CARD-STRUCTURED-001", "condition", "once_per_turn")["canonical_value"], "if_once_per_turn_available")
        self.assertFalse(any(row["value"] == "unknown_keyword" for row in rows))
        self.assertFalse(any(row["value"] == "unknown_effect" for row in rows))


def _alias(lookup_group, alias_value, canonical_value, allowed=True, audit=False):
    return {
        "lookup_group": lookup_group,
        "alias_value": alias_value,
        "canonical_value": canonical_value,
        "normalization_allowed": allowed,
        "requires_audit": audit,
        "notes": "test fixture alias",
    }


def _find_row(rows, object_type, object_id, field, value=None):
    for row in rows:
        if (
            row["object_type"] == object_type
            and row["object_id"] == object_id
            and row["field"] == field
            and (value is None or row["value"] == value)
        ):
            return row
    raise AssertionError("missing row: %s %s %s %s" % (object_type, object_id, field, value))


if __name__ == "__main__":
    unittest.main()
