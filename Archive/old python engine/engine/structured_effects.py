from __future__ import annotations

from engine.actions import ActionLibrary
from engine.board_utils import _is_board_entity, is_zenit_entity
from engine.card_metadata import has_effect_tag, has_keyword, has_target, has_trigger, has_zone, has_duration
from engine.keyword_registry import KEYWORD_DEFINITIONS
from engine.triggers import trigger_engine
from engine.logging_utils import log_block_reason
from utils.logger import naplo
from utils.text import normalize_lookup_text

STRUCTURED_STATUS_RESOLVED = "resolved"
STRUCTURED_STATUS_PARTIAL = "partial"
STRUCTURED_STATUS_DEFERRED = "deferred"
STRUCTURED_STATUS_NOT_APPLICABLE = "not_applicable"
STRUCTURED_STATUS_MISSING = "missing"
STRUCTURED_STATUS_FALLBACK_USED = "fallback_used"
STRUCTURED_STATUS_NO_STRUCTURED = "no_structured"


TAG_ALIASES = {
    "laphuzas": "draw",
    "draw": "draw",
    "sebzes": "damage",
    "damage": "damage",
    "deal_damage": "damage",
    "megsemmisites": "destroy",
    "destroy": "destroy",
    "kimerites": "exhaust",
    "exhaust": "exhaust",
    "ready": "ready",
    "visszaallitas": "reactivate",
    "reactivate": "reactivate",
    "atk_buff": "atk_buff",
    "atk_mod": "atk_buff",
    "grant_attack": "atk_buff",
    "grant_temp_attack": "atk_buff",
    "hp_buff": "hp_buff",
    "hp_mod": "hp_buff",
    "grant_hp": "hp_buff",
    "grant_max_hp": "hp_buff",
    "grant_keyword": "grant_keyword",
    "gyogyitas": "heal",
    "heal": "heal",
    "poziciocsere": "swap_position",
    "swap": "swap_position",
    "mozgatas_zenitbe": "move_to_zenit",
    "move_zenit": "move_to_zenit",
    "move_to_zenit": "move_to_zenit",
    "mozgatas_horizontra": "move_to_horizon",
    "move_horizont": "move_to_horizon",
    "move_to_horizon": "move_to_horizon",
    "tamadassemlegesites": "cancel_attack",
    "sebzessemlegesites": "cancel_damage",
    "damage_prevention": "cancel_damage",
    "felallastiltas": "no_ready",
    "paklitetejere": "put_on_deck_top",
    "visszavetelkezbe": "return_to_hand",
    "return_to_hand": "return_to_hand",
    "counterspell": "counterspell",
    "attack_or_block_restrict": "attack_restrict",
    "attack_restrict": "attack_restrict",
    "block_restrict": "block_restrict",
    "graveyard_recursion": "graveyard_recursion",
    "summon": "summon",
    "summon_token": "summon_token",
    "return_to_deck": "return_to_deck",
    "deck_bottom": "deck_bottom",
    "move_to_source": "move_to_source",
    "resource_gain": "resource_gain",
    "cost_mod": "cost_mod",
    "ability_lock": "ability_lock",
    "position_lock": "position_lock",
    "source_manipulation": "source_manipulation",
    "search_deck": "draw",
    "sacrifice": "destroy",
    "revive": "move_to_horizon",
    "deck_manipulation": "put_on_deck_top",
    "immunitas": "immunity",
    "celozhatatlan": "untargetable",
    "tamadastiltas": "cannot_attack",
    "pecsetsebzes": "seal_damage",
}


SUPPORTED_EFFECT_TAGS = tuple(sorted(set(TAG_ALIASES.values())))

PASSIVE_KEYWORDS = {
    "aegis",
    "oltalom",
    "ethereal",
    "legies",
    "celerity",
    "gyorsasag",
    "bane",
    "metely",
    "sundering",
    "hasitas",
    "harmonize",
    "harmonizalas",
    "resonance",
    "rezonancia",
    "clarion",
    "riado",
    "burst",
    "echo",
    "visszhang",
    "taunt",
}

PASSIVE_STATUS_HINTS = {
    "passziv_vagy_egyszeru",
    "passziv_kulcsszo",
    "passive_static_ignored",
    "static_not_explicitly_simulated",
}

TRIGGER_HINTS = {
    "on_play": {"on_play", "riado", "clarion", "summon", "megidez", "megidezeskor", "kijatszas"},
    "trap": {"trap", "reaction", "reakcio", "aktivalas", "amikor_tamad", "spell_targeted", "on_attack_declared"},
    "burst": {"burst", "reakcio", "pecsettores", "seal_break"},
    "death": {"on_destroyed", "destroyed", "death", "halal", "echo", "visszhang", "uressegbe_kerul"},
    "on_summon": {"on_summon", "summon", "megidez", "clarion", "riado"},
    "on_attack_declared": {"on_attack_declared", "attack", "tamadas"},
    "on_damage_taken": {"on_damage_taken", "damage_taken", "sebzest_kap"},
    "on_manifestation_phase": {"on_manifestation_phase", "manifestation", "manifestacio"},
    "on_awakening_phase": {"on_awakening_phase", "awakening", "ebredes"},
    "on_turn_start": {"on_turn_start", "turn_start", "kor_eleje"},
    "on_turn_end": {"on_turn_end", "turn_end", "kor_vege"},
    "on_position_changed": {"on_position_changed", "position_changed", "helyet_cserel", "poziciot_valt"},
}


def _normalized_tags(card):
    raw_tags = list(getattr(card, "effect_tags_normalized", []) or [])
    normalized = []
    for tag in raw_tags:
        normalized.append(TAG_ALIASES.get(tag, tag))
    return normalized


def _canonical_text(card):
    return getattr(card, "canonical_text", "") or getattr(card, "kepesseg", "")


def _extract_number(text, fallback=1):
    digits = "".join(ch if ch.isdigit() else " " for ch in text)
    for part in digits.split():
        try:
            return int(part)
        except ValueError:
            continue
    return fallback


def _enemy_units(player, zone_name=None):
    if player is None:
        return []
    units = []
    for current_zone in ("horizont", "zenit"):
        if zone_name is not None and current_zone != zone_name:
            continue
        zone = getattr(player, current_zone, [])
        for index, unit in enumerate(zone):
            if _is_board_entity(unit):
                units.append((current_zone, index, unit))
    return units


def _allied_units(player, zone_name=None):
    return _enemy_units(player, zone_name=zone_name)


def _pick_unit(units, weakest=False):
    if not units:
        return None
    if weakest:
        return min(units, key=lambda item: (item[2].akt_hp, item[2].akt_tamadas))
    return max(units, key=lambda item: (item[2].akt_tamadas, item[2].akt_hp))


def _selection_belongs_to_player(player, zone_name, item):
    if player is None:
        return False
    if zone_name == "osforras":
        return any(isinstance(entry, dict) and entry.get("lap") is item for entry in getattr(player, "osforras", []))
    if zone_name in {"kez", "pakli", "temeto"}:
        return item in getattr(player, zone_name, [])
    if zone_name in {"horizont", "zenit"}:
        return any(unit is item for _, _, unit in _allied_units(player, zone_name))
    return False


def _selection_owner(source_player, target_player, selection):
    if selection is None:
        return None
    zone_name, _, item = selection
    if _selection_belongs_to_player(source_player, zone_name, item):
        return source_player
    if _selection_belongs_to_player(target_player, zone_name, item):
        return target_player
    return getattr(item, "owner", None) or target_player or source_player


def _select_target_by_metadata(card, source_player, target_player, *, keys, source=None, weakest=False, lane_index=None):
    for key in keys:
        if has_target(card, key):
            return ActionLibrary.select_target_for_key(
                source_player,
                target_player,
                key,
                source=source,
                lane_index=lane_index,
                weakest=weakest,
            )
    return None


def _select_targets_by_metadata(card, source_player, target_player, *, keys, source=None, lane_index=None):
    for key in keys:
        if has_target(card, key):
            return ActionLibrary.targets_for_key(
                source_player,
                target_player,
                key,
                source=source,
                lane_index=lane_index,
            )
    return []


def _extract_keyword_name(text):
    normalized = normalize_lookup_text(text)
    for keyword_key, definition in KEYWORD_DEFINITIONS.items():
        if keyword_key in normalized:
            return keyword_key
        if any(normalize_lookup_text(alias) in normalized for alias in definition.aliases):
            return keyword_key
    return ""


def _find_matching_tag(card, name):
    return name in _normalized_tags(card)


def _has_structured_seal_or_player_target(card):
    return any(
        has_target(card, key)
        for key in ("pecset", "enemy_seal", "enemy_seals", "own_seal", "own_seals", "jatekos", "opponent", "wards")
    )


def _has_structured_entity_damage_target(card):
    return any(
        has_target(card, key)
        for key in (
            "opposing_entity",
            "enemy_entity",
            "enemy_entities",
            "enemy_horizont_entity",
            "enemy_horizont_entities",
            "enemy_zenit_entity",
            "enemy_zenit_entities",
        )
    )


def build_result(status, **extra):
    result = {"status": status}
    result["resolved"] = status in {
        STRUCTURED_STATUS_RESOLVED,
        STRUCTURED_STATUS_PARTIAL,
        STRUCTURED_STATUS_FALLBACK_USED,
    }
    result["partial"] = status == STRUCTURED_STATUS_PARTIAL
    result["deferred"] = status == STRUCTURED_STATUS_DEFERRED
    result["not_applicable"] = status == STRUCTURED_STATUS_NOT_APPLICABLE
    result.update(extra)
    return result


def _effect_class(card):
    normalized_keywords = set(getattr(card, "keywords_normalized", []) or [])
    normalized_triggers = set(getattr(card, "triggers_normalized", []) or [])
    normalized_tags = set(_normalized_tags(card))
    normalized_status = normalize_lookup_text(getattr(card, "interpretation_status", ""))
    normalized_type = normalize_lookup_text(getattr(card, "kartyatipus", ""))
    text = normalize_lookup_text(_canonical_text(card))
    is_spell_like = any(token in normalized_type for token in ("ige", "rituale", "ritual", "varazslat"))
    has_active_text = any(
        token in text
        for token in (
            "valassz",
            "huzz",
            "lapot",
            "okoz",
            "sebz",
            "kap ",
            "kapsz",
            "kap+",
            "vedd vissza",
            "tavolits el",
            "pusztitsd el",
            "elpusztit",
            "megsemmisit",
            "helyezd",
        )
    )

    if normalized_status in PASSIVE_STATUS_HINTS:
        if is_spell_like and has_active_text and not normalized_triggers:
            return "on_play"
        return "passive_static"

    if normalized_tags:
        if normalized_triggers:
            return "mixed"
        if normalized_tags.issubset(PASSIVE_KEYWORDS):
            return "passive_static"
        return "on_play"

    if normalized_triggers:
        joined = " ".join(sorted(normalized_triggers))
        if any(term in joined for term in ("manifest", "ebredes", "awakening", "turn_end", "turn_start")):
            return "continuous_aura"
        if any(term in joined for term in ("tamad", "attack", "spell", "target", "halal", "death", "burst", "reakcio")):
            return "triggered_reaction"
        return "triggered_reaction"

    if normalized_keywords and normalized_keywords.issubset(PASSIVE_KEYWORDS):
        return "passive_static"

    if any(token in text for token in ("amig", "[horizont]", "[zenit]", "while ")):
        return "continuous_aura"
    return "on_play"


def is_passive_structured_card(card):
    return _effect_class(card) in {"passive_static", "continuous_aura"}


def should_defer_structured(card, category):
    effect_class = _effect_class(card)
    if effect_class in {"passive_static", "continuous_aura"}:
        return False

    normalized_triggers = set(getattr(card, "triggers_normalized", []) or [])
    if not normalized_triggers:
        return False

    accepted = TRIGGER_HINTS.get(category, set())
    if any(trigger in accepted for trigger in normalized_triggers):
        return False

    joined = " ".join(sorted(normalized_triggers))
    if category == "on_play" and any(trigger in joined for trigger in ("on_play", "clarion", "riado", "summon", "megidez")):
        return False
    return not any(hint in joined for hint in accepted)


def _resolve_draw(card, source_player, context):
    if not _find_matching_tag(card, "draw"):
        return False
    amount = max(1, _extract_number(_canonical_text(card), 1))
    success = False
    for _ in range(amount):
        success |= bool(source_player.huzas(extra=True))
    if success:
        naplo.ir(f"Structured effect: {card.nev} -> {amount} lap huzas.")
    return success


def _resolve_damage(card, source_player, target_player, context):
    if not _find_matching_tag(card, "damage"):
        return False
    from engine.effects import EffectEngine

    amount = max(1, _extract_number(_canonical_text(card), 1))
    text = normalize_lookup_text(_canonical_text(card))
    lane_index = context.get("lane_index") if isinstance(context, dict) else None
    has_invalid_seal_target = _has_structured_seal_or_player_target(card)
    has_entity_target = _has_structured_entity_damage_target(card)

    if _find_matching_tag(card, "seal_damage") and not has_entity_target:
        return EffectEngine._deal_direct_seal_damage(
            card.nev,
            amount,
            source_player,
            target_player,
            "Structured",
            lane_index=lane_index,
        )
    if has_invalid_seal_target:
        EffectEngine._record_rule_diagnostic(
            source_player,
            "SEAL_RULE_BLOCKED",
            card.nev,
            "Structured",
            "structured_damage_not_valid_for_seal_or_player"
            if not _find_matching_tag(card, "seal_damage")
            else "mixed_damage_and_seal_targeting_requires_review",
            review_needed=True,
        )
        if not has_entity_target:
            naplo.ir(
                f"Structured effect: {card.nev} damage-je nem torhet Pecsetet, es nem alakul at kozvetlen Pecset-sebzesre."
            )
            return False
        naplo.ir(
            f"Structured effect: {card.nev} vegyes entity/seal celzast hasznal; a damage csak ervenyes HP-celpontokra fut le."
        )

    cel = _select_target_by_metadata(
        card,
        source_player,
        target_player,
        keys=("opposing_entity", "enemy_horizont_entity", "enemy_zenit_entity", "enemy_entity"),
        source=context.get("source_unit") if isinstance(context, dict) else None,
        lane_index=lane_index,
    )
    if cel is None:
        prefer_zone = "horizont" if has_zone(card, "horizont") else None
        if has_zone(card, "zenit"):
            prefer_zone = "zenit"
        cel = EffectEngine._select_enemy_target(target_player, text, prefer_zone)
    if cel is None:
        log_block_reason("TARGET", f"{card.nev} | structured_damage | no_valid_target")
        naplo.ir(f"Structured effect: {card.nev} -> nincs ervenyes sebzes-celpont.")
        return False
    EffectEngine._deal_damage_to_target(card.nev, amount, cel, target_player, "Structured", source_player)
    return True


def _resolve_destroy(card, source_player, target_player, context):
    if not _find_matching_tag(card, "destroy"):
        return False
    from engine.effects import EffectEngine

    cel = _select_target_by_metadata(
        card,
        source_player,
        target_player,
        keys=("opposing_entity", "enemy_horizont_entity", "enemy_zenit_entity", "enemy_entity"),
        source=context.get("source_unit") if isinstance(context, dict) else None,
        lane_index=context.get("lane_index") if isinstance(context, dict) else None,
    )
    if cel is None:
        cel = EffectEngine._select_enemy_target(target_player, normalize_lookup_text(_canonical_text(card)))
    if cel is None:
        log_block_reason("TARGET", f"{card.nev} | structured_destroy | no_valid_target")
        naplo.ir(f"Structured effect: {card.nev} -> nincs megsemmisitheto celpont.")
        return False
    return EffectEngine._destroy_target(cel, source_player, target_player, "Structured")


def _resolve_exhaust(card, source_player, target_player, context):
    if not _find_matching_tag(card, "exhaust"):
        return False
    cel = _select_target_by_metadata(
        card,
        source_player,
        target_player,
        keys=("opposing_entity", "enemy_horizont_entity", "enemy_zenit_entity", "enemy_entity"),
        source=context.get("source_unit") if isinstance(context, dict) else None,
        lane_index=context.get("lane_index") if isinstance(context, dict) else None,
    )
    if cel is None:
        prefer_zone = "horizont" if has_zone(card, "horizont") or has_target(card, "enemy_horizont_entity") else "horizont"
        if has_zone(card, "zenit") or has_target(card, "enemy_zenit_entity"):
            prefer_zone = "zenit"
        units = _enemy_units(target_player, prefer_zone)
        cel = _pick_unit(units)
    if cel is None:
        log_block_reason("TARGET", f"{card.nev} | structured_exhaust | no_valid_target")
        naplo.ir(f"Structured effect: {card.nev} -> nincs kimeritheto celpont.")
        return False
    _, _, unit = cel
    unit.kimerult = True
    naplo.ir(f"Structured effect: {card.nev} -> {unit.lap.nev} kimerult.")
    return True


def _resolve_reactivate(card, source_player, context):
    if not (_find_matching_tag(card, "reactivate") or _find_matching_tag(card, "ready")):
        return False
    source_unit = context.get("source_unit") if isinstance(context, dict) else None
    cel = _select_target_by_metadata(
        card,
        source_player,
        None,
        keys=("other_own_entity", "own_horizont_entity", "own_zenit_entity", "own_entity", "self"),
        source=source_unit,
    )
    if cel is None or not cel[2].kimerult:
        units = [item for item in _allied_units(source_player) if item[2].kimerult]
        cel = _pick_unit(units)
    if cel is None:
        log_block_reason("TARGET", f"{card.nev} | structured_ready | no_valid_target")
        naplo.ir(f"Structured effect: {card.nev} -> nincs ujraaktiválható celpont.")
        return False
    return ActionLibrary.ready_unit(
        cel[2],
        f"Structured: {card.nev}",
        owner=source_player,
        source=source_unit or cel[2],
    )


def _resolve_buff(card, source_player, context):
    text = _canonical_text(card)
    did = False
    source_unit = context.get("source_unit") if isinstance(context, dict) else None
    cel = _select_target_by_metadata(
        card,
        source_player,
        None,
        keys=("other_own_entity", "own_horizont_entity", "own_zenit_entity", "own_entity", "self"),
        source=source_unit,
    )
    if cel is None:
        cel = _pick_unit(_allied_units(source_player))
    if cel is None:
        return False
    _, _, unit = cel
    if _find_matching_tag(card, "atk_buff"):
        amount = max(1, _extract_number(text, 1))
        unit.akt_tamadas += amount
        if has_duration(card, "until_end_of_combat"):
            unit.temp_atk_bonus_until_combat_end = getattr(unit, "temp_atk_bonus_until_combat_end", 0) + amount
        else:
            unit.temp_atk_bonus_until_turn_end = getattr(unit, "temp_atk_bonus_until_turn_end", 0) + amount
        naplo.ir(f"Structured effect: {card.nev} -> {unit.lap.nev} +{amount} ATK.")
        did = True
    if _find_matching_tag(card, "hp_buff"):
        amount = max(1, _extract_number(text, 1))
        unit.bonus_max_hp = getattr(unit, "bonus_max_hp", 0) + amount
        unit.akt_hp += amount
        naplo.ir(f"Structured effect: {card.nev} -> {unit.lap.nev} +{amount} HP.")
        did = True
    return did


def _resolve_grant_keyword(card, source_player, context):
    if not _find_matching_tag(card, "grant_keyword"):
        return False
    keyword_name = _extract_keyword_name(_canonical_text(card))
    if not keyword_name:
        return False
    source_unit = context.get("source_unit") if isinstance(context, dict) else None
    cel = _select_target_by_metadata(
        card,
        source_player,
        None,
        keys=("other_own_entity", "own_horizont_entity", "own_zenit_entity", "own_entity", "self"),
        source=source_unit,
    )
    if cel is None:
        cel = _pick_unit(_allied_units(source_player))
    if cel is None:
        return False
    temporary = has_duration(card, "until_turn_end") or has_duration(card, "during_combat")
    ActionLibrary.grant_keyword(
        cel[2],
        keyword_name,
        temporary=temporary,
        owner=source_player,
        source=source_unit or cel[2],
    )
    naplo.ir(f"Structured effect: {card.nev} -> {cel[2].lap.nev} megkapta a(z) {keyword_name} kulcsszot.")
    return True


def _resolve_heal(card, source_player, context):
    if not _find_matching_tag(card, "heal"):
        return False
    amount = max(1, _extract_number(_canonical_text(card), 1))
    units = _allied_units(source_player)
    multi_targets = _select_targets_by_metadata(
        card,
        source_player,
        None,
        keys=("own_horizont_entities", "own_zenit_entities", "own_entities"),
        source=context.get("source_unit") if isinstance(context, dict) else None,
        lane_index=context.get("lane_index") if isinstance(context, dict) else None,
    )
    if multi_targets:
        units = multi_targets
    if multi_targets or has_target(card, "osszes_sajat") or has_target(card, "minden_sajat"):
        healed = 0
        for _, _, unit in units:
            healed += ActionLibrary.heal_unit(unit, amount, f"Structured: {card.nev}", owner=source_player, source=context.get("source_unit") if isinstance(context, dict) else None)
        if healed > 0:
            naplo.ir(f"Structured effect: {card.nev} -> osszesen {healed} HP gyogyitas.")
            return True
        return False

    cel = _pick_unit(units, weakest=True)
    if cel is None:
        return False
    _, _, unit = cel
    healed = ActionLibrary.heal_unit(unit, amount, f"Structured: {card.nev}", owner=source_player, source=context.get("source_unit") if isinstance(context, dict) else None)
    if healed > 0:
        naplo.ir(f"Structured effect: {card.nev} -> {unit.lap.nev} gyogyult {healed} HP-t.")
        return True
    return False


def _resolve_swap(card, source_player, target_player, context):
    if not _find_matching_tag(card, "swap_position"):
        return False
    if target_player is None:
        return False
    for index in range(len(target_player.horizont)):
        if not _is_board_entity(source_player.horizont[index]):
            continue
        front = target_player.horizont[index]
        back = target_player.zenit[index]
        if not (_is_board_entity(front) and is_zenit_entity(back)):
            continue
        target_player.horizont[index], target_player.zenit[index] = back, front
        trigger_engine.dispatch("on_position_changed", source=front.lap, owner=target_player, payload={"from": "horizont", "to": "zenit"})
        trigger_engine.dispatch("on_position_changed", source=back.lap, owner=target_player, payload={"from": "zenit", "to": "horizont"})
        trigger_engine.dispatch(
            "on_position_swap",
            source=front,
            owner=target_player,
            target=back,
            payload={"index": index, "reason": card.nev},
        )
        naplo.ir(f"Structured effect: {card.nev} -> poziciocsere tortent a {index + 1}. aramlatban.")
        return True
    return False


def _resolve_move_to_zenit(card, source_player, target_player, context):
    if not _find_matching_tag(card, "move_to_zenit"):
        return False
    from engine.effects import EffectEngine

    cel = _select_target_by_metadata(
        card,
        source_player,
        target_player,
        keys=("enemy_horizont_entity", "enemy_entity", "opposing_entity"),
        source=context.get("source_unit") if isinstance(context, dict) else None,
        lane_index=context.get("lane_index") if isinstance(context, dict) else None,
    )
    if cel is None:
        prefer_zone = "horizont" if has_zone(card, "horizont") or not has_zone(card, "zenit") else "zenit"
        cel = EffectEngine._select_enemy_target(target_player, prefer_zone, prefer_zone)
    if cel is None:
        return False
    zone_name, index, _ = cel
    return ActionLibrary.move_target_to_zenit(target_player, zone_name, index, card.nev)


def _resolve_move_to_horizont(card, source_player, target_player, context):
    if not _find_matching_tag(card, "move_to_horizon"):
        return False
    cel = _select_target_by_metadata(
        card,
        source_player,
        target_player,
        keys=("enemy_zenit_entity",),
        source=context.get("source_unit") if isinstance(context, dict) else None,
        lane_index=context.get("lane_index") if isinstance(context, dict) else None,
    )
    if cel is not None:
        _, index, _ = cel
        if target_player.horizont[index] is None:
            return ActionLibrary.move_target_to_horizont(target_player, "zenit", index, card.nev, exhausted=True)
    units = _enemy_units(target_player, "zenit")
    for _, index, unit in units:
        if target_player.horizont[index] is None:
            return ActionLibrary.move_target_to_horizont(target_player, "zenit", index, card.nev, exhausted=True)
    return False


def _resolve_position_change(card, source_player, target_player, context):
    for handler in (
        lambda: _resolve_swap(card, source_player, target_player, context),
        lambda: _resolve_move_to_zenit(card, source_player, target_player, context),
        lambda: _resolve_move_to_horizont(card, source_player, target_player, context),
    ):
        if handler():
            return True
    return False


def _resolve_combat_control(card, source_player, target_player, context):
    did = False
    attacker = context.get("tamado_egyseg") if isinstance(context, dict) else None
    source_unit = context.get("source_unit") if isinstance(context, dict) else None
    if _find_matching_tag(card, "cancel_attack") and attacker is not None:
        naplo.ir(f"Structured effect: {card.nev} -> tamadas semlegesitve.")
        did = True
    if _find_matching_tag(card, "no_ready") and attacker is not None:
        attacker.extra_exhausted_turns = getattr(attacker, "extra_exhausted_turns", 0) + 1
        did = True
    restrict_targets = _select_targets_by_metadata(
        card,
        source_player,
        target_player,
        keys=(
            "enemy_horizont_entities",
            "enemy_entities",
            "enemy_horizont_entity",
            "enemy_entity",
            "own_horizont_entities",
            "own_zenit_entities",
            "own_entities",
            "own_horizont_entity",
            "own_zenit_entity",
            "own_entity",
            "self",
        ),
        source=source_unit,
        lane_index=context.get("lane_index") if isinstance(context, dict) else None,
    )
    if not restrict_targets and attacker is not None:
        restrict_targets = [(None, None, attacker)]
    if _find_matching_tag(card, "attack_restrict"):
        for _, _, unit in restrict_targets:
            did |= ActionLibrary.restrict_attack(unit, f"Structured: {card.nev}")
    if _find_matching_tag(card, "block_restrict"):
        for _, _, unit in restrict_targets:
            did |= ActionLibrary.restrict_block(unit, f"Structured: {card.nev}")
    return did


def _resolve_misc_state(card, source_player, target_player, context):
    did = False
    spell_target = _select_target_by_metadata(
        card,
        source_player,
        target_player,
        keys=("enemy_spell_or_ritual", "enemy_spell"),
        source=context.get("spell_card") if isinstance(context, dict) else None,
    )
    if _find_matching_tag(card, "counterspell") and (spell_target is not None or context.get("spell_card") is not None):
        context["cancelled_spell"] = True
        naplo.ir(f"Structured effect: {card.nev} -> varazslat semlegesitve.")
        did = True
    if _find_matching_tag(card, "put_on_deck_top"):
        units = _enemy_units(target_player, "horizont")
        cel = _pick_unit(units)
        if cel is not None:
            zone_name, index, unit = cel
            target_player.pakli.append(unit.lap)
            getattr(target_player, zone_name)[index] = None
            naplo.ir(f"Structured effect: {card.nev} -> {unit.lap.nev} a pakli tetejere kerult.")
            did = True
    if _find_matching_tag(card, "return_to_hand"):
        source_unit = context.get("source_unit") if isinstance(context, dict) else None
        cel = _select_target_by_metadata(
            card,
            source_player,
            target_player,
            keys=(
                "other_own_entity",
                "own_horizont_entity",
                "own_zenit_entity",
                "own_entity",
                "enemy_horizont_entity",
                "enemy_zenit_entity",
                "enemy_entity",
                "self",
            ),
            source=source_unit,
            lane_index=context.get("lane_index") if isinstance(context, dict) else None,
        )
        if cel is None:
            units = _enemy_units(target_player) if target_player is not None else _allied_units(source_player)
            cel = _pick_unit(units)
        if cel is not None:
            target_owner = _selection_owner(source_player, target_player, cel)
            did |= ActionLibrary.return_target_to_hand(target_owner, cel[0], cel[1], card.nev)
    if _find_matching_tag(card, "immunity"):
        cel = _pick_unit(_allied_units(source_player), weakest=True)
        if cel is not None:
            cel[2].damage_immunity_until_turn_end = True
            naplo.ir(f"Structured effect: {card.nev} -> {cel[2].lap.nev} sebzesimmunitas a kor vegeig.")
            did = True
    if _find_matching_tag(card, "untargetable"):
        cel = _select_target_by_metadata(
            card,
            source_player,
            None,
            keys=("own_horizont_entity", "own_zenit_entity", "own_entity", "self"),
            source=context.get("source_unit") if isinstance(context, dict) else None,
        )
        if cel is None:
            cel = _pick_unit(_allied_units(source_player))
        if cel is not None:
            did |= ActionLibrary.grant_untargetable(cel[2], f"Structured: {card.nev}", owner=source_player, source=context.get("source_unit") if isinstance(context, dict) else None)
    if _find_matching_tag(card, "graveyard_recursion"):
        grave_target = _select_target_by_metadata(card, source_player, None, keys=("own_graveyard_entity",))
        if grave_target is not None:
            card_to_revive = grave_target[2]
            to_hand = has_target(card, "own_hand") or has_zone(card, "hand")
            if card_to_revive in getattr(source_player, "temeto", []):
                source_player.temeto.remove(card_to_revive)
                if to_hand:
                    source_player.kez.append(card_to_revive)
                    did = True
                else:
                    did |= ActionLibrary.summon_card_to_horizont(
                        source_player,
                        card_to_revive,
                        lane_index=ActionLibrary.first_empty_slot(source_player, "horizont"),
                        reason=f"revive:{card.nev}",
                        exhausted=False,
                        payload={"revived": True, "structured": True},
                    ) is not None
            else:
                did |= ActionLibrary.revive_from_graveyard(
                    source_player,
                    lambda grave_card: "entitas" in normalize_lookup_text(getattr(grave_card, "kartyatipus", "")),
                    to_hand=to_hand,
                    reason=card.nev,
                )
        else:
            to_hand = has_target(card, "own_hand") or has_zone(card, "hand")
            did |= ActionLibrary.revive_from_graveyard(
                source_player,
                lambda grave_card: "entitas" in normalize_lookup_text(getattr(grave_card, "kartyatipus", "")),
                to_hand=to_hand,
                reason=card.nev,
            )
    if _find_matching_tag(card, "summon"):
        summon_card = context.get("summon_card")
        lane_index = context.get("lane_index") if isinstance(context, dict) else None
        if summon_card is not None:
            did |= ActionLibrary.summon_card_to_horizont(
                source_player,
                summon_card,
                lane_index=lane_index,
                reason=card.nev,
                exhausted=context.get("summon_exhausted", True),
                payload={"structured": True},
            ) is not None
    if _find_matching_tag(card, "summon_token"):
        amount = max(1, _extract_number(_canonical_text(card), 1))
        lane = context.get("lane_index") if isinstance(context, dict) else None
        summoned = 0
        for _ in range(amount):
            if lane is None:
                lane = ActionLibrary.first_empty_slot(source_player, "horizont")
            if lane is None:
                break
            token = ActionLibrary.summon_token_to_horizont(
                source_player,
                lane,
                context.get("token_name", "Token"),
                context.get("token_atk", 1),
                context.get("token_hp", 1),
                race=context.get("token_race", "Token"),
                realm=getattr(source_player, "birodalom", "Semleges"),
                exhausted=context.get("summon_exhausted", True),
            )
            if token is None:
                break
            summoned += 1
            lane = None
        if summoned > 0:
            naplo.ir(f"Structured effect: {card.nev} -> {summoned} token a Horizontra kerult.")
            did = True
    if _find_matching_tag(card, "return_to_deck") or _find_matching_tag(card, "deck_bottom"):
        cel = _select_target_by_metadata(
            card,
            source_player,
            target_player,
            keys=(
                "own_hand",
                "enemy_hand",
                "enemy_hand_card",
                "own_graveyard",
                "own_graveyard_entity",
                "own_source_card",
                "enemy_source_card",
                "own_horizont_entity",
                "own_zenit_entity",
                "enemy_horizont_entity",
                "enemy_zenit_entity",
            ),
            source=context.get("spell_card") if isinstance(context, dict) else None,
            lane_index=context.get("lane_index") if isinstance(context, dict) else None,
        )
        if cel is not None:
            zone_name, index, _ = cel
            owner = _selection_owner(source_player, target_player, cel)
            did |= ActionLibrary.move_target_to_deck(
                owner,
                zone_name,
                index,
                card.nev,
                to_bottom=_find_matching_tag(card, "deck_bottom"),
            )
    if _find_matching_tag(card, "move_to_source"):
        cel = _select_target_by_metadata(
            card,
            source_player,
            target_player,
            keys=("own_hand", "own_graveyard", "own_graveyard_entity", "own_horizont_entity", "own_zenit_entity"),
            source=context.get("source_unit") if isinstance(context, dict) else None,
        )
        if cel is not None:
            did |= ActionLibrary.move_target_to_source(source_player, cel[0], cel[1], card.nev)
        elif getattr(source_player, "temeto", None):
            did |= ActionLibrary.move_target_to_source(source_player, "temeto", 0, card.nev)
    if _find_matching_tag(card, "source_manipulation"):
        cel = _select_target_by_metadata(
            card,
            source_player,
            target_player,
            keys=("own_hand", "own_graveyard", "own_graveyard_entity", "own_horizont_entity", "own_zenit_entity"),
            source=context.get("source_unit") if isinstance(context, dict) else None,
            lane_index=context.get("lane_index") if isinstance(context, dict) else None,
        )
        if cel is not None:
            did |= ActionLibrary.move_target_to_source(source_player, cel[0], cel[1], card.nev)
    if _find_matching_tag(card, "ability_lock"):
        cel = _select_target_by_metadata(
            card,
            source_player,
            target_player,
            keys=(
                "opposing_entity",
                "enemy_horizont_entity",
                "enemy_zenit_entity",
                "enemy_entity",
                "own_horizont_entity",
                "own_zenit_entity",
                "own_entity",
                "self",
            ),
            source=context.get("source_unit") if isinstance(context, dict) else None,
            lane_index=context.get("lane_index") if isinstance(context, dict) else None,
        )
        if cel is None and has_target(card, "lane"):
            cel = ActionLibrary.select_target_for_key(
                source_player,
                target_player,
                "opposing_entity",
                lane_index=context.get("lane_index") if isinstance(context, dict) else None,
            )
        if cel is not None:
            did |= ActionLibrary.lock_abilities(
                cel[2],
                f"Structured: {card.nev}",
                owner=_selection_owner(source_player, target_player, cel),
                source=context.get("source_unit") if isinstance(context, dict) else None,
            )
    if _find_matching_tag(card, "position_lock"):
        cel = _select_target_by_metadata(
            card,
            source_player,
            target_player,
            keys=(
                "opposing_entity",
                "enemy_horizont_entity",
                "enemy_zenit_entity",
                "enemy_entity",
                "own_horizont_entity",
                "own_zenit_entity",
                "own_entity",
                "self",
            ),
            source=context.get("source_unit") if isinstance(context, dict) else None,
            lane_index=context.get("lane_index") if isinstance(context, dict) else None,
        )
        if cel is None and has_target(card, "lane"):
            cel = ActionLibrary.select_target_for_key(
                source_player,
                target_player,
                "opposing_entity",
                lane_index=context.get("lane_index") if isinstance(context, dict) else None,
            )
        if cel is not None:
            did |= ActionLibrary.lock_position(
                cel[2],
                awakenings=max(1, _extract_number(_canonical_text(card), 1)),
                reason=f"Structured: {card.nev}",
                owner=_selection_owner(source_player, target_player, cel),
                source=context.get("source_unit") if isinstance(context, dict) else None,
            )
    if _find_matching_tag(card, "resource_gain"):
        amount = max(1, _extract_number(_canonical_text(card), 1))
        did |= ActionLibrary.grant_resource(source_player, amount, card.nev) > 0
    if _find_matching_tag(card, "cost_mod"):
        amount = max(1, _extract_number(_canonical_text(card), 1))
        scope = context.get("cost_mod_scope", "entity")
        did |= ActionLibrary.apply_cost_mod(source_player, amount, scope=scope, reason=card.nev)
    return did


def resolve_structured_effect(card, source_player, target_player=None, context=None):
    context = context or {}
    tags = _normalized_tags(card)
    if not tags:
        return build_result(STRUCTURED_STATUS_NO_STRUCTURED, mode="no_structured")

    category = context.get("category", "on_play")
    effect_class = _effect_class(card)

    if effect_class in {"passive_static", "continuous_aura"}:
        return build_result("passive_static_ignored", mode="structured", effect_class=effect_class)

    if should_defer_structured(card, category):
        return build_result(STRUCTURED_STATUS_DEFERRED, mode="structured", effect_class=effect_class)

    handlers = (
        lambda: _resolve_draw(card, source_player, context),
        lambda: _resolve_damage(card, source_player, target_player, context),
        lambda: _resolve_destroy(card, source_player, target_player, context),
        lambda: _resolve_exhaust(card, source_player, target_player, context),
        lambda: _resolve_reactivate(card, source_player, context),
        lambda: _resolve_buff(card, source_player, context),
        lambda: _resolve_grant_keyword(card, source_player, context),
        lambda: _resolve_heal(card, source_player, context),
        lambda: _resolve_position_change(card, source_player, target_player, context),
        lambda: _resolve_combat_control(card, source_player, target_player, context),
        lambda: _resolve_misc_state(card, source_player, target_player, context),
    )

    did_any = False
    for handler in handlers:
        try:
            did_any |= bool(handler())
        except Exception:
            continue

    unsupported_tags = [tag for tag in tags if tag not in SUPPORTED_EFFECT_TAGS]

    if did_any:
        if unsupported_tags:
            return build_result(
                STRUCTURED_STATUS_PARTIAL,
                mode="structured",
                effect_class=effect_class,
                unsupported_tags=unsupported_tags,
            )
        return build_result(STRUCTURED_STATUS_RESOLVED, mode="structured", effect_class=effect_class)

    status = normalize_lookup_text(getattr(card, "interpretation_status", ""))
    if status in {"structured_partial", "partial", "reszleges"}:
        return build_result(STRUCTURED_STATUS_PARTIAL, mode="structured", effect_class=effect_class)
    if status in {"deferred", "trigger_waiting", "structured_deferred"}:
        return build_result(STRUCTURED_STATUS_DEFERRED, mode="structured", effect_class=effect_class)
    if status in {"not_applicable", "nincs_celpont"}:
        return build_result(STRUCTURED_STATUS_NOT_APPLICABLE, mode="structured", effect_class=effect_class)
    return build_result(STRUCTURED_STATUS_MISSING, mode="structured", effect_class=effect_class)


def get_structured_status(card):
    status = normalize_lookup_text(getattr(card, "interpretation_status", ""))
    if status:
        if status in PASSIVE_STATUS_HINTS:
            if _effect_class(card) == "on_play":
                return "missing_implementation"
            return "passive_static_ignored"
        if status in {"structured_partial", "partial", "reszleges"}:
            return "structured_partial"
        if status in {"deferred", "trigger_waiting", "structured_deferred"}:
            return "structured_deferred"
        if status in {"not_applicable", "nincs_celpont"}:
            return "not_applicable"
        return status
    if is_passive_structured_card(card):
        return "static_not_explicitly_simulated"
    if should_defer_structured(card, "on_play"):
        return "structured_deferred"
    if getattr(card, "effect_tags", None):
        return "structured_partial"
    return "missing_implementation"
