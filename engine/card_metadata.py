from __future__ import annotations

from utils.text import normalize_lookup_text, repair_mojibake


STANDARD_EMPTY_VALUES = {"", "blank", "none", "-", "n/a"}

TRIGGER_ALIASES = {
    "on_manifest_phase": "on_manifestation_phase",
    "on_death": "on_destroyed",
    "death": "on_destroyed",
    "on_enemy_spell_played": "on_enemy_spell_played",
    "on_enemy_summon": "on_enemy_summon",
    "on_breach_phase": "on_breach_phase",
    "on_combat_phase_start": "on_combat_phase_start",
    "on_combat_damage_dealt": "on_combat_damage_dealt",
    "on_first_combat_survived": "on_first_combat_survived",
    "on_spell_targeted": "on_enemy_spell_target",
}

ZONE_ALIASES = {
    "seal": "seal_row",
    "sealrow": "seal_row",
    "wards": "seal_row",
    "pecset": "seal_row",
    "pecsetek": "seal_row",
    "eternal": "aeternal",
    "player": "aeternal",
    "forras": "source",
    "kez": "hand",
    "temeto": "graveyard",
    "pakli": "deck",
}

TARGET_ALIASES = {
    "self_entity": "self",
    "self unit": "self",
    "sajat_entitas": "own_entity",
    "masik_sajat_entitas": "other_own_entity",
    "ellenseges_entitas": "enemy_entity",
    "pecset": "enemy_seal",
    "pecsetek": "enemy_seals",
    "ellenseges_pecset": "enemy_seal",
    "sajat_pecset": "own_seal",
    "jatekos": "opponent",
    "opponent_player": "opponent",
}

EFFECT_TAG_ALIASES = {
    "sebzes": "damage",
    "pecsetsebzes": "seal_damage",
    "laphuzas": "draw",
    "huzas": "draw",
    "gyogyitas": "heal",
    "megsemmisites": "destroy",
    "pusztitas": "destroy",
    "visszavetelkezbe": "return_to_hand",
    "kezbe_vetel": "return_to_hand",
    "mozgatas_horizontra": "move_horizont",
    "mozgatas_zenitbe": "move_zenit",
    "poziciocsere": "swap_position",
    "atk_buff": "grant_attack",
    "atk_mod": "grant_attack",
    "hp_buff": "grant_hp",
    "hp_mod": "grant_hp",
    "keyword_adas": "grant_keyword",
    "kulcsszoadas": "grant_keyword",
    "aura_modositas": "cost_mod",
    "kimerites": "exhaust",
    "tamadastiltas": "attack_restrict",
    "blokktiltas": "block_restrict",
    "sebzessemlegesites": "damage_prevention",
    "summon_token": "summon",
    "counterspell": "counterspell",
    "stat_protection": "damage_prevention",
    "damage_immunity": "damage_prevention",
    "ready": "reactivate",
}

DURATION_ALIASES = {
    "kor_vegeig": "until_end_of_turn",
    "a_kor_vegeig": "until_end_of_turn",
    "until_end_of_turn": "until_end_of_turn",
    "until_turn_end": "until_end_of_turn",
    "kovetkezo_kor_vegeig": "until_end_of_next_own_turn",
    "until_end_of_next_turn": "until_end_of_next_own_turn",
    "until_next_own_turn_end": "until_end_of_next_own_turn",
    "harc_vegeig": "until_end_of_combat",
    "harc_idejere": "until_end_of_combat",
    "until_end_of_combat": "until_end_of_combat",
    "during_combat": "until_end_of_combat",
    "allando": "permanent",
    "permanent": "permanent",
    "until_match_end": "permanent",
    "statikus": "static",
    "static": "static",
    "static_while_on_board": "static",
    "while_active": "static",
    "azonnali": "instant",
    "instant": "instant",
}

CONDITION_ALIASES = {
    "none": "",
    "blank": "",
}

STATUS_ALIASES = {
    "structured": "structured",
    "passziv_kulcsszo": "passziv_kulcsszo",
    "passziv_vagy_egyszeru": "passziv_vagy_egyszeru",
    "structured_deferred": "structured_deferred",
    "structured_partial": "structured_partial",
    "fallback_text_resolved": "fallback_text_resolved",
    "runtime_supported": "runtime_supported",
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
    if value is None:
        return ""
    cleaned = repair_mojibake(str(value)).strip()
    if normalize_lookup_text(cleaned) in STANDARD_EMPTY_VALUES:
        return ""
    return cleaned


def normalize_trigger_value(value):
    normalized = normalize_lookup_text(value)
    return TRIGGER_ALIASES.get(normalized, normalized)


def normalize_zone_value(value):
    normalized = normalize_lookup_text(value)
    return ZONE_ALIASES.get(normalized, normalized)


def normalize_target_value(value):
    normalized = normalize_lookup_text(value)
    return TARGET_ALIASES.get(normalized, normalized)


def normalize_effect_tag_value(value):
    normalized = normalize_lookup_text(value)
    return EFFECT_TAG_ALIASES.get(normalized, normalized)


def normalize_duration_value(value):
    normalized = normalize_lookup_text(value)
    return DURATION_ALIASES.get(normalized, normalized)


def normalize_condition_value(value):
    normalized = normalize_lookup_text(value)
    return CONDITION_ALIASES.get(normalized, normalized)


def normalize_status_value(value):
    normalized = normalize_lookup_text(value)
    return STATUS_ALIASES.get(normalized, normalized)


def normalized_metadata_list(value, *, field_name=None):
    items = [normalize_lookup_text(item) for item in parse_semicolon_list(value)]
    result = []
    for item in items:
        if item in STANDARD_EMPTY_VALUES:
            continue
        if field_name == "trigger":
            normalized = normalize_trigger_value(item)
        elif field_name == "zone":
            normalized = normalize_zone_value(item)
        elif field_name == "target":
            normalized = normalize_target_value(item)
        elif field_name == "effect_tag":
            normalized = normalize_effect_tag_value(item)
        elif field_name == "duration":
            normalized = normalize_duration_value(item)
        else:
            normalized = item
        if normalized and normalized not in result:
            result.append(normalized)
    return result


def has_effect_tag(card, tag):
    tags = set(getattr(card, "effect_tags_normalized", []) or [])
    normalized = normalize_effect_tag_value(tag)
    return normalized in tags or normalize_lookup_text(tag) in tags


def has_keyword(card, keyword):
    keywords = set(getattr(card, "keywords_normalized", []) or [])
    return normalize_lookup_text(keyword) in keywords


def has_trigger(card, trigger):
    triggers = set(getattr(card, "triggers_normalized", []) or [])
    return normalize_trigger_value(trigger) in triggers


def has_target(card, target):
    targets = set(getattr(card, "targets_normalized", []) or [])
    normalized = normalize_target_value(target)
    return normalized in targets or normalize_lookup_text(target) in targets


def has_zone(card, zone):
    zones = set(getattr(card, "zones_normalized", []) or [])
    normalized = normalize_zone_value(zone)
    return normalized in zones or normalize_lookup_text(zone) in zones


def has_duration(card, duration):
    durations = set(getattr(card, "durations_normalized", []) or [])
    normalized = normalize_duration_value(duration)
    return normalized in durations or normalize_lookup_text(duration) in durations


def has_condition(card, condition):
    conditions = set(getattr(card, "conditions_normalized", []) or [])
    normalized = normalize_condition_value(condition)
    return normalized in conditions or normalize_lookup_text(condition) in conditions
