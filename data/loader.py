import os
from openpyxl import load_workbook
from engine.card_metadata import (
    normalize_condition_value,
    normalize_status_value,
    normalized_metadata_list,
)
from utils.text import normalize_lookup_text
from utils.logger import naplo
from engine.card import Kartya


HEADER_ALIASES = {
    "kartya_nev": "kartya_nev",
    "tipus": "kartyatipus",
    "kartyatipus": "kartyatipus",
    "birodalom": "birodalom",
    "klan": "klan",
    "faj": "faj",
    "kaszt": "kaszt",
    "magnitudo": "magnitudo",
    "aura": "aura_koltseg",
    "aura_koltseg": "aura_koltseg",
    "atk": "tamadas",
    "tamadas": "tamadas",
    "hp": "eletero",
    "eletero": "eletero",
    "kepesseg": "kepesseg",
    "kepesseg_canonical": "kepesseg_canonical",
    "zona_felismerve": "zona_felismerve",
    "kulcsszavak_felismerve": "kulcsszavak_felismerve",
    "trigger_felismerve": "trigger_felismerve",
    "celpont_felismerve": "celpont_felismerve",
    "hatascimkek": "hatascimkek",
    "idotartam_felismerve": "idotartam_felismerve",
    "feltetel_felismerve": "feltetel_felismerve",
    "gepi_leiras": "gepi_leiras",
    "ertelmezesi_statusz": "ertelmezesi_statusz",
    "engine_megjegyzes": "engine_megjegyzes",
}

STANDARD_COLUMN_ORDER = [
    "kartya_nev",
    "kartyatipus",
    "birodalom",
    "klan",
    "faj",
    "kaszt",
    "magnitudo",
    "aura_koltseg",
    "tamadas",
    "eletero",
    "kepesseg",
    "kepesseg_canonical",
    "zona_felismerve",
    "kulcsszavak_felismerve",
    "trigger_felismerve",
    "celpont_felismerve",
    "hatascimkek",
    "idotartam_felismerve",
    "feltetel_felismerve",
    "gepi_leiras",
    "ertelmezesi_statusz",
    "engine_megjegyzes",
]

LIST_FIELDS = {
    "zona_felismerve",
    "kulcsszavak_felismerve",
    "trigger_felismerve",
    "celpont_felismerve",
    "hatascimkek",
}

INTEGER_FIELDS = {
    "magnitudo",
    "aura_koltseg",
    "tamadas",
    "eletero",
}

REQUIRED_TEXT_FIELDS = {
    "kartya_nev",
    "kartyatipus",
    "birodalom",
    "kepesseg",
}

ALLOWED_ZONES = {
    "horizont", "zenit", "dominium", "graveyard", "hand", "deck", "source", "seal_row", "aeternal", "lane",
}

ALLOWED_KEYWORDS = {
    "aegis", "bane", "burst", "celerity", "clarion", "echo", "ethereal", "harmonize", "resonance", "sundering", "taunt",
}

ALLOWED_TRIGGERS = {
    "static", "on_play", "on_summon", "on_enemy_summon", "on_enemy_zenit_summon", "on_death", "on_destroyed",
    "on_attack_declared", "on_attack_hits", "on_combat_damage_dealt", "on_combat_damage_taken",
    "on_block_survived", "on_damage_survived", "on_enemy_spell_target", "on_enemy_spell_or_ritual_played",
    "on_enemy_spell_played", "on_spell_targeted",
    "on_enemy_extra_draw", "on_enemy_third_draw_in_turn", "on_turn_end", "on_next_own_awakening",
    "on_influx_phase", "on_heal", "on_enemy_ability_activated", "on_enemy_multiple_draws",
    "on_enemy_horizont_threshold", "on_move_zenit_to_horizont", "on_leave_board", "on_spell_cast_by_owner",
    "on_position_swap", "on_entity_enters_horizont", "on_source_placement", "on_seal_break", "on_bounce",
    "on_trap_triggered", "on_ready_from_exhausted", "on_stat_gain", "on_gain_keyword", "on_discard",
    "on_enemy_card_played", "on_enemy_second_summon_in_turn", "on_start_of_turn",
    "on_manifestation_phase", "on_awakening_phase",
}

ALLOWED_TARGETS = {
    "self", "own_entity", "other_own_entity", "enemy_entity", "own_horizont_entity", "enemy_horizont_entity",
    "own_zenit_entity", "enemy_zenit_entity", "own_entities", "enemy_entities", "own_horizont_entities",
    "enemy_horizont_entities", "own_zenit_entities", "enemy_zenit_entities", "own_seal", "enemy_seal",
    "own_seals", "enemy_seals", "own_aeternal", "enemy_aeternal", "own_hand", "enemy_hand", "own_deck",
    "own_graveyard_entity", "enemy_spell", "enemy_spell_or_ritual", "enemy_hand_card", "enemy_face_down_trap",
    "own_face_down_trap", "own_graveyard", "opponent", "lane", "source_card", "own_source_card",
    "enemy_source_card", "opposing_entity",
}

ALLOWED_EFFECT_TAGS = {
    "damage", "deal_damage", "heal", "draw", "discard", "destroy", "return_to_hand", "seal_damage",
    "move_horizont", "move_zenit", "exhaust", "grant_keyword", "cost_mod", "graveyard_recursion",
    "damage_prevention", "attack_restrict", "block_restrict", "once_per_turn", "grant_attack",
    "grant_temp_attack", "grant_hp", "grant_max_hp", "swap_position", "reactivate", "immunity",
}

ALLOWED_DURATIONS = {
    "until_end_of_turn", "until_end_of_next_own_turn", "until_end_of_combat", "permanent", "static", "instant",
}


def _normalize_header_name(header):
    normalized = normalize_lookup_text(header)
    normalized = normalized.replace(" ", "_")
    return HEADER_ALIASES.get(normalized, normalized)


def _row_to_mapping(headers, row):
    mapping = {}
    for index, header in enumerate(headers):
        if not header:
            continue
        mapping[header] = row[index] if index < len(row) else None
    return mapping


def _normalize_scalar(field_name, value):
    if value is None:
        return "" if field_name not in INTEGER_FIELDS else 0

    if field_name in INTEGER_FIELDS:
        try:
            if str(value).strip() == "":
                return 0
            return int(float(value))
        except Exception:
            return 0

    text = str(value).strip()
    normalized = normalize_lookup_text(text)
    if normalized in {"blank", "none", "-", ""}:
        return ""
    if field_name == "idotartam_felismerve":
        durations = normalized_metadata_list(text, field_name="duration")
        return ", ".join(durations)
    if field_name == "feltetel_felismerve":
        return normalize_condition_value(text)
    if field_name == "ertelmezesi_statusz":
        return normalize_status_value(text)
    return text


def _normalize_list_value(field_name, value):
    if value is None:
        return ""
    if field_name == "zona_felismerve":
        items = normalized_metadata_list(value, field_name="zone")
    elif field_name == "kulcsszavak_felismerve":
        items = normalized_metadata_list(value)
    elif field_name == "trigger_felismerve":
        items = normalized_metadata_list(value, field_name="trigger")
    elif field_name == "celpont_felismerve":
        items = normalized_metadata_list(value, field_name="target")
    elif field_name == "hatascimkek":
        items = normalized_metadata_list(value, field_name="effect_tag")
    else:
        items = normalized_metadata_list(value)
    return ", ".join(items)


def _split_normalized_csv(value):
    if not value:
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def normalize_row_mapping(mapping):
    normalized = {}
    for field_name in STANDARD_COLUMN_ORDER:
        value = mapping.get(field_name)
        if field_name in LIST_FIELDS:
            normalized[field_name] = _normalize_list_value(field_name, value)
        else:
            normalized[field_name] = _normalize_scalar(field_name, value)
    return normalized


def validate_row_mapping(mapping, row_index=None, sheet_name=None):
    issues = []
    for field_name in STANDARD_COLUMN_ORDER:
        if field_name not in mapping:
            issues.append(f"hianyzo_oszlop:{field_name}")
    for field_name in REQUIRED_TEXT_FIELDS:
        if not str(mapping.get(field_name, "")).strip():
            issues.append(f"ures_kotelezo_mezo:{field_name}")
    if mapping.get("kartyatipus") and normalize_lookup_text(mapping["kartyatipus"]) == "entitas":
        if int(mapping.get("eletero", 0) or 0) <= 0:
            issues.append("entitas_hp_hianyzik")
    enum_checks = (
        ("zona_felismerve", ALLOWED_ZONES),
        ("kulcsszavak_felismerve", ALLOWED_KEYWORDS),
        ("trigger_felismerve", ALLOWED_TRIGGERS),
        ("celpont_felismerve", ALLOWED_TARGETS),
        ("hatascimkek", ALLOWED_EFFECT_TAGS),
        ("idotartam_felismerve", ALLOWED_DURATIONS),
    )
    for field_name, allowed in enum_checks:
        for token in _split_normalized_csv(mapping.get(field_name, "")):
            if normalize_lookup_text(token) not in allowed:
                issues.append(f"ismeretlen_ertek:{field_name}:{token}")
    if normalize_lookup_text(mapping.get("kartyatipus", "")) == "entitas":
        suspicious_targets = {"enemy_spell", "enemy_spell_or_ritual", "own_hand", "enemy_hand"}
        for token in _split_normalized_csv(mapping.get("celpont_felismerve", "")):
            if normalize_lookup_text(token) in suspicious_targets:
                issues.append(f"gyanus_target_tipus_kombinacio:{token}")
    if mapping.get("idotartam_felismerve") and not mapping.get("hatascimkek"):
        issues.append("idotartam_hatascimke_nelkul")
    prefix = []
    if sheet_name:
        prefix.append(f"sheet={sheet_name}")
    if row_index is not None:
        prefix.append(f"row={row_index}")
    location = " ".join(prefix)
    return [f"{location} {issue}".strip() for issue in issues]


def load_card_rows_xlsx(fajl_utvonal):
    if not os.path.exists(fajl_utvonal):
        raise FileNotFoundError(fajl_utvonal)

    wb = load_workbook(fajl_utvonal, data_only=True)
    rows = []
    validation_issues = []

    for lap_nev in wb.sheetnames:
        sheet = wb[lap_nev]
        raw_headers = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
        headers = [_normalize_header_name(value) for value in raw_headers]

        if len(headers) != len(STANDARD_COLUMN_ORDER):
            validation_issues.append(
                f"sheet={lap_nev} helytelen_oszlopszam: vart={len(STANDARD_COLUMN_ORDER)} kapott={len(headers)}"
            )

        for expected in STANDARD_COLUMN_ORDER:
            if expected not in headers:
                validation_issues.append(f"sheet={lap_nev} hianyzo_oszlop:{expected}")

        for row_index, sor in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if not sor or not sor[0]:
                continue

            first_cell = normalize_lookup_text(str(sor[0]).strip()) if sor[0] is not None else ""
            third_cell = normalize_lookup_text(str(sor[2]).strip()) if len(sor) > 2 and sor[2] is not None else ""
            if first_cell in {"kartya_nev", "kartya nev"} or third_cell == "birodalom":
                continue

            sor_mapping = _row_to_mapping(headers, sor)
            normalized = normalize_row_mapping(sor_mapping)
            normalized["_sheet"] = lap_nev
            normalized["_row_index"] = row_index
            normalized["_validation_issues"] = validate_row_mapping(normalized, row_index=row_index, sheet_name=lap_nev)
            validation_issues.extend(normalized["_validation_issues"])
            rows.append(normalized)

    return rows, validation_issues


def kartyak_betoltese_xlsx(fajl_utvonal):
    if not os.path.exists(fajl_utvonal):
        naplo.ir(f"HIBA: Nem talalhato a kartyafajl itt: {fajl_utvonal}")
        return []

    naplo.ir(f"Excel betoltese: {fajl_utvonal}")
    rows, validation_issues = load_card_rows_xlsx(fajl_utvonal)
    osszes_kartya = [Kartya(row) for row in rows]

    if validation_issues:
        naplo.ir(f"[VALIDATION] {len(validation_issues)} figyelmeztetes a cards.xlsx betoltes soran.")
        for issue in validation_issues[:20]:
            naplo.ir(f"[VALIDATION] {issue}")
        if len(validation_issues) > 20:
            naplo.ir(f"[VALIDATION] ... tovabbi {len(validation_issues) - 20} figyelmeztetes")

    naplo.ir(f"Sikeresen betoltve {len(osszes_kartya)} kartya.")
    return osszes_kartya
