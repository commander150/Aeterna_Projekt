"""Map XLSX exporter runtime card rows to runtime package card records."""

from __future__ import annotations


REQUIRED_FIELDS = ("Card_ID", "Kártya név", "Típus", "Birodalom")

FIELD_MAP = {
    "Card_ID": "card_id",
    "Kártya név": "name_hu",
    "Típus": "card_type",
    "Birodalom": "realm",
    "Klán": "clan",
    "Faj": "species",
    "Kaszt": "class",
    "Magnitudó": "magnitude",
    "Aura": "aura_cost",
    "ATK": "atk",
    "HP": "hp",
    "Képesség": "text_hu",
    "Képesség_Canonical": "structured_ability",
    "Zóna_Felismerve": "recognized_zone",
    "Kulcsszavak_Felismerve": "keywords",
    "Trigger_Felismerve": "trigger",
    "Célpont_Felismerve": "target",
    "Hatáscímkék": "effect_tags",
    "Időtartam_Felismerve": "duration",
    "Feltétel_Felismerve": "condition",
    "Gépi_Leírás": "machine_description",
    "Értelmezési_Státusz": "interpretation_status",
    "Engine_Megjegyzés": "engine_notes",
}

NUMERIC_OUTPUT_FIELDS = {"magnitude", "aura_cost", "atk", "hp"}
LIST_OUTPUT_FIELDS = {"keywords", "effect_tags"}
NONE_VALUE = "none"


def map_export_runtime_card(export_record):
    """Return a runtime package card record from one exporter card row."""
    diagnostics = []
    runtime_card = {}

    for source_field, target_field in FIELD_MAP.items():
        raw_value = export_record.get(source_field)
        if target_field in NUMERIC_OUTPUT_FIELDS:
            runtime_card[target_field] = normalize_number(raw_value)
        elif target_field in LIST_OUTPUT_FIELDS:
            runtime_card[target_field] = normalize_list(raw_value)
        else:
            runtime_card[target_field] = normalize_scalar(raw_value)

    for source_field in REQUIRED_FIELDS:
        if is_blank(export_record.get(source_field)):
            diagnostics.append(
                {
                    "severity": "error",
                    "code": "MISSING_REQUIRED_FIELD",
                    "source_field": source_field,
                    "target_field": FIELD_MAP[source_field],
                    "message_hu": "Hiányzó kötelező exporter mező.",
                    "blocking": True,
                }
            )

    runtime_card["mapping_status"] = "error" if diagnostics else "ok"
    runtime_card["diagnostics"] = diagnostics
    return runtime_card


def is_blank(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().casefold() in {"", "none", "blank", "null"}
    return False


def normalize_scalar(value):
    if is_blank(value):
        return NONE_VALUE
    if isinstance(value, str):
        return value.strip()
    return value


def normalize_number(value):
    if is_blank(value):
        return NONE_VALUE
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    if isinstance(value, str):
        text = value.strip()
        try:
            number = float(text)
        except ValueError:
            return text
        return int(number) if number.is_integer() else number
    return value


def normalize_list(value):
    if is_blank(value):
        return []
    if isinstance(value, list):
        return [normalize_scalar(item) for item in value if not is_blank(item)]
    if isinstance(value, tuple):
        return [normalize_scalar(item) for item in value if not is_blank(item)]
    if isinstance(value, str):
        return [part.strip() for part in value.split(";") if not is_blank(part)]
    return [value]
