from __future__ import annotations

from utils.text import normalize_lookup_text, repair_mojibake


STANDARD_EMPTY_VALUES = {"", "blank", "none", "-", "n/a"}

TRIGGER_ALIASES = {
    "death": "on_death",
    "on_destroyed": "on_death",
    "on_spell_targeted": "on_enemy_spell_target",
    "on_ready": "on_ready_from_exhausted",
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
    "deal_damage": "damage",
    "pecsetsebzes": "seal_damage",
    "laphuzas": "draw",
    "huzas": "draw",
    "gyogyitas": "heal",
    "megsemmisites": "destroy",
    "pusztitas": "destroy",
    "visszavetelkezbe": "return_to_hand",
    "kezbe_vetel": "return_to_hand",
    "mozgatas_horizontra": "move_horizont",
    "move_to_horizon": "move_horizont",
    "move_to_horizont": "move_horizont",
    "mozgatas_zenitbe": "move_zenit",
    "move_to_zenit": "move_zenit",
    "poziciocsere": "choice",
    "atk_buff": "atk_mod",
    "grant_attack": "atk_mod",
    "grant_temp_attack": "atk_mod",
    "hp_buff": "hp_mod",
    "grant_hp": "hp_mod",
    "grant_max_hp": "hp_mod",
    "keyword_adas": "grant_keyword",
    "kulcsszoadas": "grant_keyword",
    "aura_modositas": "cost_mod",
    "kimerites": "exhaust",
    "tamadastiltas": "attack_restrict",
    "blokktiltas": "block_restrict",
    "sebzessemlegesites": "damage_prevention",
    "stat_protection": "damage_prevention",
    "reactivate": "ready",
    "return_to_deck_bottom": "deck_bottom",
    "reflect_damage": "damage_bonus",
    "retaliation_damage": "damage_bonus",
}

DURATION_ALIASES = {
    "kor_vegeig": "until_turn_end",
    "a_kor_vegeig": "until_turn_end",
    "until_end_of_turn": "until_turn_end",
    "until_turn_end": "until_turn_end",
    "kovetkezo_kor_vegeig": "until_next_own_turn_end",
    "until_end_of_next_turn": "until_next_own_turn_end",
    "until_end_of_next_own_turn": "until_next_own_turn_end",
    "until_next_own_turn_end": "until_next_own_turn_end",
    "harc_vegeig": "during_combat",
    "harc_idejere": "during_combat",
    "until_end_of_combat": "during_combat",
    "during_combat": "during_combat",
    "allando": "until_match_end",
    "permanent": "until_match_end",
    "until_match_end": "until_match_end",
    "statikus": "static_while_on_board",
    "static": "static_while_on_board",
    "static_while_on_board": "static_while_on_board",
    "while_active": "while_active",
    "azonnali": "instant",
    "instant": "instant",
    "next_own_awakening": "next_own_awakening",
    "next_own_turn_start": "next_own_turn_start",
    "until_next_enemy_turn": "until_next_enemy_turn",
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

STANDARD_FIELD_VALUES = {
    "zone": {
        "horizont", "zenit", "dominium", "graveyard", "hand", "deck", "source", "seal_row", "aeternal", "lane", "blank",
    },
    "keyword": {
        "aegis", "bane", "burst", "celerity", "clarion", "echo", "ethereal", "harmonize", "resonance", "sundering", "taunt", "blank",
    },
    "trigger": {
        "static", "on_summon", "on_death", "on_attack_declared", "on_attack_hits", "on_combat_damage_dealt",
        "on_combat_damage_taken", "on_block_survived", "on_damage_survived", "on_enemy_spell_target",
        "on_enemy_spell_or_ritual_played", "on_enemy_summon", "on_enemy_zenit_summon", "on_enemy_extra_draw",
        "on_enemy_third_draw_in_turn", "on_turn_end", "on_next_own_awakening", "on_influx_phase", "on_heal",
        "on_enemy_ability_activated", "on_enemy_multiple_draws", "on_enemy_horizont_threshold",
        "on_move_zenit_to_horizont", "on_leave_board", "on_spell_cast_by_owner", "on_position_swap",
        "on_entity_enters_horizont", "on_source_placement", "on_seal_break", "on_bounce", "on_trap_triggered",
        "on_ready_from_exhausted", "on_stat_gain", "on_gain_keyword", "on_destroy", "on_discard",
        "on_enemy_card_played", "on_enemy_second_summon_in_turn", "on_start_of_turn", "blank",
    },
    "target": {
        "self", "own_entity", "other_own_entity", "enemy_entity", "own_horizont_entity", "enemy_horizont_entity",
        "own_zenit_entity", "enemy_zenit_entity", "own_entities", "enemy_entities", "own_horizont_entities",
        "enemy_horizont_entities", "own_zenit_entities", "enemy_zenit_entities", "own_seal", "enemy_seal",
        "own_seals", "enemy_seals", "own_aeternal", "enemy_aeternal", "own_hand", "enemy_hand", "own_deck",
        "own_graveyard_entity", "enemy_spell", "enemy_spell_or_ritual", "enemy_hand_card", "enemy_face_down_trap",
        "own_face_down_trap", "own_graveyard", "opponent", "lane", "source_card", "own_source_card",
        "enemy_source_card", "opposing_entity", "blank",
    },
    "effect_tag": {
        "damage", "seal_damage", "draw", "heal", "reveal", "atk_mod", "hp_mod", "exhaust", "summon", "destroy",
        "discard", "counterspell", "redirect", "cost_mod", "resource_gain", "resource_drain", "resource_acceleration",
        "resource_spend", "move_horizont", "move_zenit", "graveyard_recursion", "graveyard_replacement",
        "grant_keyword", "type_change", "stat_reset", "trap_immunity", "damage_immunity", "damage_bonus",
        "damage_prevention", "overflow_damage", "stat_protection", "sacrifice", "free_cast", "tutor",
        "untargetable", "return_to_hand", "summon_token", "attack_restrict", "summon_restrict", "block_restrict",
        "control_change", "ready", "return_to_deck", "deck_bottom", "move_to_source", "source_manipulation",
        "cleanse", "copy_stats", "copy_keywords", "position_lock", "attack_nullify", "ability_lock",
        "random_discard", "choice", "blank",
    },
    "duration": {
        "instant", "during_combat", "until_turn_end", "until_next_own_turn_end", "until_next_enemy_turn",
        "until_match_end", "static_while_on_board", "while_active", "next_own_awakening", "next_own_turn_start", "blank",
    },
}

LEGACY_INTERNAL_VALUES = {
    "trigger": {"on_play", "on_destroyed", "on_ready", "on_burst", "on_enemy_manifestation_start", "on_graveyard_recursion", "on_infusion_phase", "on_lane_filled"},
    "effect_tag": {"grant_attack", "grant_temp_attack", "grant_hp", "grant_max_hp", "reactivate", "move_to_horizon", "move_to_zenit", "deal_damage", "reflect_damage", "retaliation_damage"},
    "duration": {"until_end_of_turn", "until_end_of_next_own_turn", "until_end_of_combat", "permanent", "static"},
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
