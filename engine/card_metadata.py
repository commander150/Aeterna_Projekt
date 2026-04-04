from __future__ import annotations

from utils.text import normalize_lookup_text, repair_mojibake


def parse_semicolon_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        items = value
    else:
        text = repair_mojibake(str(value)).replace("|", ";")
        items = text.split(";")
    result = []
    for item in items:
        cleaned = repair_mojibake(str(item)).strip()
        if cleaned:
            result.append(cleaned)
    return result


def normalize_metadata_value(value):
    return repair_mojibake(str(value)).strip() if value is not None else ""


def normalized_metadata_list(value):
    return [normalize_lookup_text(item) for item in parse_semicolon_list(value)]


def has_effect_tag(card, tag):
    tags = set(getattr(card, "effect_tags_normalized", []) or [])
    return normalize_lookup_text(tag) in tags


def has_keyword(card, keyword):
    keywords = set(getattr(card, "keywords_normalized", []) or [])
    return normalize_lookup_text(keyword) in keywords


def has_trigger(card, trigger):
    triggers = set(getattr(card, "triggers_normalized", []) or [])
    return normalize_lookup_text(trigger) in triggers


def has_target(card, target):
    targets = set(getattr(card, "targets_normalized", []) or [])
    return normalize_lookup_text(target) in targets

