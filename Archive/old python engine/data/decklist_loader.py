import json
import os
import re
from collections import defaultdict

from utils.text import normalize_lookup_text


DECK_SIZE = 40

HEADER_ALIASES = {
    "product_id": "product_id",
    "deck_id": "deck_id",
    "szabalyi_kartya_id": "card_id",
    "card_id": "card_id",
    "kartya_nev": "card_name",
    "card_name": "card_name",
    "darabszam": "quantity",
    "quantity": "quantity",
    "szerep_a_pakliban": "deck_role",
    "deck_role": "deck_role",
    "megjegyzes": "notes",
    "notes": "notes",
}

DECKLIST_FIELDS = (
    "product_id",
    "deck_id",
    "card_id",
    "card_name",
    "quantity",
    "deck_role",
    "notes",
)


def normalize_deck_card_id(value):
    text = str(value).strip() if value is not None else ""
    if not text or normalize_lookup_text(text) in {"blank", "none", "-"}:
        return ""

    text = text.upper()
    if text.startswith("AET-"):
        candidate = text.removeprefix("AET-")
        if re.fullmatch(r"[A-Z0-9]+-[A-Z0-9]+-[0-9]{3}", candidate):
            return candidate
    return text


def _normalize_header_name(header):
    normalized = normalize_lookup_text(header)
    normalized = normalized.replace(" ", "_")
    return HEADER_ALIASES.get(normalized, normalized)


def _to_int(value):
    try:
        if value is None or str(value).strip() == "":
            return 0
        return int(float(value))
    except Exception:
        return 0


def normalize_decklist_row(raw_mapping, line_number=None):
    normalized_input = {
        _normalize_header_name(key): value
        for key, value in raw_mapping.items()
    }
    row = {field_name: normalized_input.get(field_name, "") for field_name in DECKLIST_FIELDS}
    row["card_id"] = normalize_deck_card_id(row.get("card_id"))
    row["quantity"] = _to_int(row.get("quantity"))
    row["_line_number"] = line_number
    return row


def load_decklist_rows_jsonl(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    rows = []
    warnings = []
    with open(file_path, "r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                raw_mapping = json.loads(line)
            except json.JSONDecodeError as exc:
                warnings.append(f"line={line_number} invalid_json:{exc.msg}")
                continue
            if not isinstance(raw_mapping, dict):
                warnings.append(f"line={line_number} invalid_jsonl_row:not_object")
                continue

            row = normalize_decklist_row(raw_mapping, line_number=line_number)
            if not row["deck_id"]:
                warnings.append(f"line={line_number} missing_deck_id")
            if not row["card_id"]:
                warnings.append(f"line={line_number} missing_card_id")
            if row["quantity"] <= 0:
                warnings.append(f"line={line_number} invalid_quantity:{row['quantity']}")
            rows.append(row)
    return rows, warnings


def group_decklist_rows(rows):
    decks = defaultdict(list)
    for row in rows:
        decks[row.get("deck_id") or ""].append(row)
    return dict(decks)


def _runtime_card_index(runtime_cards):
    index = {}
    for card in runtime_cards or []:
        card_id = ""
        if isinstance(card, dict):
            card_id = card.get("card_id") or card.get("Card_ID") or ""
        else:
            card_id = getattr(card, "card_id", "")
        normalized = normalize_deck_card_id(card_id)
        if normalized:
            index[normalized] = card
    return index


def validate_decklists(rows, runtime_cards=None, expected_deck_size=DECK_SIZE):
    decks = group_decklist_rows(rows)
    card_index = _runtime_card_index(runtime_cards)
    warnings = []
    missing_card_ids = []
    non_40_decks = []
    deck_reports = []

    for deck_id in sorted(decks):
        deck_rows = decks[deck_id]
        total_quantity = sum(row.get("quantity", 0) for row in deck_rows)
        if total_quantity != expected_deck_size:
            warnings.append(f"deck={deck_id} deck_size_warning:expected={expected_deck_size}:actual={total_quantity}")
            non_40_decks.append({"deck_id": deck_id, "size": total_quantity})

        deck_missing = []
        for row in deck_rows:
            card_id = row.get("card_id", "")
            if card_index and card_id and card_id not in card_index:
                warnings.append(
                    f"deck={deck_id} line={row.get('_line_number')} missing_card_id:{card_id}"
                )
                deck_missing.append(card_id)
                missing_card_ids.append(card_id)

        deck_reports.append(
            {
                "deck_id": deck_id,
                "product_ids": sorted({row.get("product_id") for row in deck_rows if row.get("product_id")}),
                "rows": len(deck_rows),
                "total_quantity": total_quantity,
                "missing_card_ids": sorted(set(deck_missing)),
            }
        )

    return {
        "decks": deck_reports,
        "warnings": warnings,
        "non_40_decks": non_40_decks,
        "missing_card_ids": sorted(set(missing_card_ids)),
    }


def load_and_validate_decklists(file_path, runtime_cards=None, expected_deck_size=DECK_SIZE):
    rows, load_warnings = load_decklist_rows_jsonl(file_path)
    report = validate_decklists(rows, runtime_cards=runtime_cards, expected_deck_size=expected_deck_size)
    report["rows"] = rows
    report["warnings"] = load_warnings + report["warnings"]
    return report
