"""Prepare runtime lookup records from LOOKUPS_RUNTIME-style JSONL."""

from __future__ import annotations

import json
from pathlib import Path


LOOKUP_GROUP_ALIASES = {
    "card_type": "card_type",
    "cardtype": "card_type",
    "card type": "card_type",
    "card_type": "card_type",
    "Card_Type": "card_type",
    "Realm": "realm",
    "realm": "realm",
}


def load_builder_lookups_from_runtime_lookups_jsonl(input_path):
    """Return builder-compatible lookup records from LOOKUPS_RUNTIME JSONL rows."""
    lookups = []
    diagnostics = []
    records_read = 0

    with Path(input_path).open("r", encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                diagnostics.append(_diagnostic("INVALID_JSON", line_number, str(exc), blocking=True))
                continue

            records_read += 1
            lookup_group = _canonical_lookup_group(_value(row, "Lookup_Group"))
            value = _value(row, "Value")
            if lookup_group == "none" or value == "none":
                diagnostics.append(
                    _diagnostic(
                        "MISSING_LOOKUP_FIELD",
                        line_number,
                        "LOOKUPS_RUNTIME row is missing Lookup_Group or Value.",
                        blocking=True,
                    )
                )
                continue

            lookups.append(
                {
                    "lookup_group": lookup_group,
                    "value": value,
                    "label_hu": _value(row, "Label_HU", default=value),
                    "status": _value(row, "Status", default="active"),
                    "canonical_value": _value(row, "Canonical_Value", default=value),
                    "used_for": _list_value(row, "Used_For"),
                }
            )

    return {
        "lookups": lookups,
        "summary": {
            "records_read": records_read,
            "lookups_loaded": len(lookups),
            "diagnostics": diagnostics,
            "error_count": sum(1 for item in diagnostics if item.get("severity") == "error"),
        },
    }


def _canonical_lookup_group(value):
    text = _value({"value": value}, "value")
    return LOOKUP_GROUP_ALIASES.get(text, LOOKUP_GROUP_ALIASES.get(text.casefold(), text))


def _value(row, key, default="none"):
    value = row.get(key, default)
    if value is None:
        return default
    if isinstance(value, str):
        text = value.strip()
        return text if text else default
    return value


def _list_value(row, key):
    value = _value(row, key)
    if value == "none":
        return []
    if isinstance(value, list):
        return [item for item in value if item not in (None, "")]
    if isinstance(value, str):
        return [part.strip() for part in value.replace(",", ";").split(";") if part.strip()]
    return [value]


def _diagnostic(code, line_number, message, blocking):
    return {
        "severity": "error",
        "code": code,
        "line_number": line_number,
        "message": message,
        "blocking": blocking,
    }
