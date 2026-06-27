"""Prepare runtime deck records from PRODUCT_DECKLISTS-style JSONL."""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path


def load_builder_decks_from_product_decklists_jsonl(input_path):
    """Return builder-compatible deck records from PRODUCT_DECKLISTS JSONL rows."""
    grouped = OrderedDict()
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
            deck_id = _value(row, "Deck_ID")
            product_id = _value(row, "Product_ID")
            card_id = _value(row, "Card_ID")
            count = _number(row, "Darabszám", default=0)

            if _is_blank(deck_id) or _is_blank(card_id):
                diagnostics.append(
                    _diagnostic(
                        "MISSING_DECKLIST_FIELD",
                        line_number,
                        "PRODUCT_DECKLISTS row is missing Deck_ID or Card_ID.",
                        blocking=True,
                    )
                )
                continue

            deck = grouped.setdefault(
                deck_id,
                {
                    "deck_id": deck_id,
                    "product_id": product_id,
                    "name_hu": deck_id,
                    "realm": _infer_realm(product_id, deck_id),
                    "deck_type": _infer_deck_type(deck_id),
                    "card_entries": OrderedDict(),
                    "valid": True,
                    "diagnostics": [],
                },
            )
            if deck["product_id"] == "none" and product_id != "none":
                deck["product_id"] = product_id
            entry = deck["card_entries"].setdefault(
                card_id,
                {
                    "card_id": card_id,
                    "count": 0,
                },
            )
            entry["count"] += count

    decks = []
    for deck in grouped.values():
        entries = list(deck["card_entries"].values())
        deck["card_entries"] = entries
        deck["card_count"] = sum(entry.get("count", 0) for entry in entries)
        decks.append(deck)

    return {
        "decks": decks,
        "summary": {
            "records_read": records_read,
            "decks_loaded": len(decks),
            "diagnostics": diagnostics,
            "error_count": sum(1 for item in diagnostics if item.get("severity") == "error"),
        },
    }


def _value(row, key):
    value = row.get(key)
    if _is_blank(value):
        return "none"
    if isinstance(value, str):
        return value.strip()
    return value


def _number(row, key, default=0):
    value = row.get(key)
    if _is_blank(value):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    if isinstance(value, str):
        text = value.strip().replace(",", ".")
        try:
            number = float(text)
        except ValueError:
            return default
        return int(number) if number.is_integer() else number
    return default


def _is_blank(value):
    return value is None or (isinstance(value, str) and value.strip() == "")


def _infer_deck_type(deck_id):
    text = str(deck_id).upper()
    if "STARTER" in text:
        return "starter"
    if "TEST" in text:
        return "test_deck"
    return "export_deck"


def _infer_realm(product_id, deck_id):
    text = f"{product_id} {deck_id}".upper()
    realm_codes = {
        "IGN": "Ignis",
        "AQU": "Aqua",
        "TER": "Terra",
        "LUX": "Lux",
        "UMB": "Umbra",
        "VEN": "Ventus",
        "AET": "Aether",
    }
    for code, realm in realm_codes.items():
        if code in text or realm in text:
            return realm
    return "none"


def _diagnostic(code, line_number, message, blocking):
    return {
        "severity": "error",
        "code": code,
        "line_number": line_number,
        "message": message,
        "blocking": blocking,
    }
