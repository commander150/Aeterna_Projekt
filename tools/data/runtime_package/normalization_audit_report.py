"""Diagnostics-only normalization audit for runtime package data.

This module previews where legacy alias values appear in runtime cards/decks.
It never mutates the input records and never applies normalization.
"""

from __future__ import annotations


FIELD_RULES = {
    "card": (
        {"field": "card_type", "lookup_group": "card_type", "tokenize": False},
        {"field": "realm", "lookup_group": "realm", "tokenize": False},
        {"field": "clan", "lookup_group": "clan", "tokenize": False},
        {"field": "species", "lookup_group": "race", "tokenize": False},
        {"field": "class", "lookup_group": "class", "tokenize": False},
        {"field": "recognized_zone", "lookup_group": "zone", "tokenize": True},
        {"field": "keywords", "lookup_group": "keyword", "tokenize": False},
        {"field": "trigger", "lookup_group": "trigger", "tokenize": True},
        {"field": "target", "lookup_group": "target", "tokenize": True},
        {"field": "effect_tags", "lookup_group": "effect_tag", "tokenize": True},
        {"field": "duration", "lookup_group": "duration", "tokenize": True},
        {"field": "condition", "lookup_group": "condition", "tokenize": True},
        {"field": "interpretation_status", "lookup_group": "interpretation_status", "tokenize": False},
    ),
    "deck": (
        {"field": "realm", "lookup_group": "realm", "tokenize": False},
    ),
}


def build_normalization_audit_report(cards, decks, normalization_aliases_payload):
    """Return a diagnostics-only normalization audit report payload."""
    aliases = _extract_aliases(normalization_aliases_payload)
    alias_index = _build_alias_index(aliases)
    audit_rows = []
    checked_objects = 0
    checked_values = 0

    for card in cards or []:
        if not isinstance(card, dict):
            continue
        checked_objects += 1
        checked_values += _audit_object(
            audit_rows,
            object_type="card",
            object_id=card.get("card_id", ""),
            record=card,
            alias_index=alias_index,
        )

    for deck in decks or []:
        if not isinstance(deck, dict):
            continue
        checked_objects += 1
        checked_values += _audit_object(
            audit_rows,
            object_type="deck",
            object_id=deck.get("deck_id", ""),
            record=deck,
            alias_index=alias_index,
        )

    allowed_count = sum(1 for row in audit_rows if row["normalization_allowed"])
    requires_audit_count = sum(1 for row in audit_rows if row["requires_audit"])
    field_matches = _count_by_key(audit_rows, "field")
    lookup_group_matches = _count_by_key(audit_rows, "lookup_group")

    return {
        "normalization_audit": audit_rows,
        "summary": {
            "checked_objects": checked_objects,
            "checked_values": checked_values,
            "matches_total": len(audit_rows),
            "normalization_allowed": allowed_count,
            "requires_audit": requires_audit_count,
            "unknown_or_unmapped": checked_values - len(audit_rows),
            "field_matches": field_matches,
            "lookup_group_matches": lookup_group_matches,
        },
    }


def _extract_aliases(normalization_aliases_payload):
    if isinstance(normalization_aliases_payload, dict):
        aliases = normalization_aliases_payload.get("normalization_aliases", [])
        if isinstance(aliases, list):
            return aliases
    if isinstance(normalization_aliases_payload, list):
        return normalization_aliases_payload
    return []


def _build_alias_index(aliases):
    index = {}
    for alias in aliases:
        if not isinstance(alias, dict):
            continue
        lookup_group = str(alias.get("lookup_group", "")).strip()
        alias_value = str(alias.get("alias_value", "")).strip()
        if not lookup_group or not alias_value:
            continue
        index.setdefault((lookup_group, alias_value), alias)
    return index


def _audit_object(audit_rows, object_type, object_id, record, alias_index):
    checked_values = 0
    for rule in FIELD_RULES[object_type]:
        field = rule["field"]
        lookup_group = rule["lookup_group"]
        original_value = record.get(field)
        values = _iter_values(original_value, tokenize=rule["tokenize"])
        for value in values:
            checked_values += 1
            alias = alias_index.get((lookup_group, value))
            if alias is None:
                continue
            requires_audit = bool(alias.get("requires_audit", False))
            normalization_allowed = bool(alias.get("normalization_allowed", False))
            audit_rows.append(
                {
                    "object_type": object_type,
                    "object_id": str(object_id),
                    "field": field,
                    "original_value": original_value,
                    "value": value,
                    "lookup_group": lookup_group,
                    "match_type": "legacy_alias",
                    "canonical_value": str(alias.get("canonical_value", "")),
                    "normalization_allowed": normalization_allowed,
                    "requires_audit": requires_audit,
                    "suggested_action": "manual_audit_required" if requires_audit else "safe_normalization_preview",
                    "applied": False,
                    "notes": str(alias.get("notes", "")),
                }
            )
    return checked_values


def _iter_values(value, tokenize):
    if value is None:
        return []
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(_iter_values(item, tokenize=tokenize))
        return values
    text = str(value).strip()
    if not text:
        return []
    if not tokenize:
        return [text]
    return [token for token in _split_tokens(text) if token]


def _split_tokens(text):
    normalized = text.replace(";", ",")
    return [part.strip() for part in normalized.split(",") if part.strip()]


def _count_by_key(rows, key):
    counts = {}
    for row in rows:
        value = row.get(key, "")
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))
