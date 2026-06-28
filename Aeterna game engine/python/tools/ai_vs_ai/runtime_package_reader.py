"""Read runtime package data for future AI-vs-AI smoke tests.

This module intentionally stays small: it loads package records and validates
deck card references, but it does not implement rules, bots, or action logic.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


REQUIRED_FILES = ("manifest.json", "cards.jsonl", "decks.jsonl", "lookups.json")


class RuntimePackageReadError(Exception):
    """Raised when a runtime package cannot be read safely."""


@dataclass
class RuntimePackage:
    package_dir: Path
    manifest: dict
    cards_by_id: dict
    decks_by_id: dict
    lookups: list

    def get_card(self, card_id):
        try:
            return self.cards_by_id[card_id]
        except KeyError as exc:
            raise RuntimePackageReadError("Unknown card_id: %s" % card_id) from exc

    def get_deck(self, deck_id):
        try:
            return self.decks_by_id[deck_id]
        except KeyError as exc:
            raise RuntimePackageReadError("Unknown deck_id: %s" % deck_id) from exc

    def validate_deck_card_refs(self):
        errors = []
        for deck_id, deck in self.decks_by_id.items():
            for index, entry in enumerate(deck.get("card_entries", []) or []):
                card_id = entry.get("card_id")
                if card_id not in self.cards_by_id:
                    errors.append(
                        {
                            "code": "DECK_CARD_NOT_FOUND",
                            "deck_id": deck_id,
                            "card_id": card_id,
                            "entry_index": index,
                        }
                    )
        return errors

    def count_summary(self):
        deck_reference_errors = self.validate_deck_card_refs()
        lookup_groups = {
            item.get("lookup_group")
            for item in self.lookups
            if item.get("lookup_group")
        }
        return {
            "cards_count": len(self.cards_by_id),
            "decks_count": len(self.decks_by_id),
            "lookup_records_count": len(self.lookups),
            "lookup_groups_count": len(lookup_groups),
            "deck_reference_error_count": len(deck_reference_errors),
        }


def load_runtime_package(package_dir):
    package_dir = Path(package_dir)
    _ensure_required_files(package_dir)

    manifest = _read_json(package_dir / "manifest.json")
    cards = _read_jsonl(package_dir / "cards.jsonl")
    decks = _read_jsonl(package_dir / "decks.jsonl")
    lookups_payload = _read_json(package_dir / "lookups.json")
    lookups = lookups_payload.get("lookups")
    if not isinstance(lookups, list):
        raise RuntimePackageReadError("lookups.json must contain a 'lookups' list.")

    return RuntimePackage(
        package_dir=package_dir,
        manifest=manifest,
        cards_by_id=_index_by_required_id(cards, "card_id", "cards.jsonl"),
        decks_by_id=_index_by_required_id(decks, "deck_id", "decks.jsonl"),
        lookups=lookups,
    )


def _ensure_required_files(package_dir):
    if not package_dir.is_dir():
        raise RuntimePackageReadError("Runtime package directory not found: %s" % package_dir)
    missing = [filename for filename in REQUIRED_FILES if not (package_dir / filename).is_file()]
    if missing:
        raise RuntimePackageReadError("Runtime package is missing required files: %s" % ", ".join(missing))


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimePackageReadError("Invalid JSON in %s: %s" % (path, exc)) from exc
    except OSError as exc:
        raise RuntimePackageReadError("Cannot read %s: %s" % (path, exc)) from exc


def _read_jsonl(path):
    records = []
    try:
        with Path(path).open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise RuntimePackageReadError(
                        "Invalid JSONL in %s at line %s: %s" % (path, line_number, exc)
                    ) from exc
                if not isinstance(record, dict):
                    raise RuntimePackageReadError(
                        "Invalid JSONL in %s at line %s: row must be an object." % (path, line_number)
                    )
                records.append(record)
    except OSError as exc:
        raise RuntimePackageReadError("Cannot read %s: %s" % (path, exc)) from exc
    return records


def _index_by_required_id(records, field_name, source_name):
    indexed = {}
    for index, record in enumerate(records):
        object_id = record.get(field_name)
        if not object_id:
            raise RuntimePackageReadError("%s row %s is missing %s." % (source_name, index, field_name))
        if object_id in indexed:
            raise RuntimePackageReadError("%s contains duplicate %s: %s" % (source_name, field_name, object_id))
        indexed[object_id] = record
    return indexed
