from __future__ import annotations

from utils.text import normalize_lookup_text, repair_mojibake


TRIGGER_ALIASES = {
    # Spreadsheet shorthand -> engine event names
    "on_manifest_phase": "on_manifestation_phase",
    "on_death": "on_destroyed",
    "death": "on_destroyed",
    "on_enemy_spell_played": "on_enemy_spell_played",
    "on_enemy_summon": "on_enemy_summon",
    "on_breach_phase": "on_breach_phase",
    "on_combat_phase_start": "on_combat_phase_start",
    "on_combat_damage_dealt": "on_combat_damage_dealt",
    "on_first_combat_survived": "on_first_combat_survived",
}


def parse_semicolon_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        items = value
    else:
        text = repair_mojibake(str(value)).replace("|", ";")
        if ";" not in text and "," in text:
            text = text.replace(",", ";")
        items = text.split(";")
    result = []
    for item in items:
        cleaned = repair_mojibake(str(item)).strip()
        if cleaned:
            result.append(cleaned)
    return result


def normalize_metadata_value(value):
    return repair_mojibake(str(value)).strip() if value is not None else ""


def normalize_trigger_value(value):
    normalized = normalize_lookup_text(value)
    return TRIGGER_ALIASES.get(normalized, normalized)


def normalized_metadata_list(value, *, field_name=None):
    items = [normalize_lookup_text(item) for item in parse_semicolon_list(value)]
    if field_name == "trigger":
        return [normalize_trigger_value(item) for item in items]
    return items


def has_effect_tag(card, tag):
    tags = set(getattr(card, "effect_tags_normalized", []) or [])
    return normalize_lookup_text(tag) in tags


def has_keyword(card, keyword):
    keywords = set(getattr(card, "keywords_normalized", []) or [])
    return normalize_lookup_text(keyword) in keywords


def has_trigger(card, trigger):
    triggers = set(getattr(card, "triggers_normalized", []) or [])
    return normalize_trigger_value(trigger) in triggers


def has_target(card, target):
    targets = set(getattr(card, "targets_normalized", []) or [])
    return normalize_lookup_text(target) in targets
