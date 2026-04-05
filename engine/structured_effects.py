from __future__ import annotations

from engine.actions import ActionLibrary
from engine.board_utils import _is_board_entity, is_zenit_entity
from engine.card_metadata import has_effect_tag, has_keyword, has_target, has_trigger
from engine.triggers import trigger_engine
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
    "megsemmisites": "destroy",
    "destroy": "destroy",
    "kimerites": "exhaust",
    "exhaust": "exhaust",
    "visszaallitas": "reactivate",
    "reactivate": "reactivate",
    "atk_buff": "atk_buff",
    "atk_mod": "atk_buff",
    "hp_buff": "hp_buff",
    "hp_mod": "hp_buff",
    "gyogyitas": "heal",
    "heal": "heal",
    "poziciocsere": "swap_position",
    "swap": "swap_position",
    "mozgatas_zenitbe": "move_to_zenit",
    "move_zenit": "move_to_zenit",
    "mozgatas_horizontra": "move_to_horizon",
    "move_horizont": "move_to_horizon",
    "tamadassemlegesites": "cancel_attack",
    "sebzessemlegesites": "cancel_damage",
    "felallastiltas": "no_ready",
    "paklitetejere": "put_on_deck_top",
    "visszavetelkezbe": "return_to_hand",
    "attack_or_block_restrict": "cannot_attack",
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


def _find_matching_tag(card, name):
    return name in _normalized_tags(card)


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
    if _find_matching_tag(card, "seal_damage") or has_target(card, "pecset") or has_target(card, "jatekos") or has_target(card, "wards"):
        return EffectEngine._deal_direct_seal_damage(card.nev, amount, source_player, target_player, "Structured")

    prefer_zone = "horizont" if has_target(card, "horizont") else None
    cel = EffectEngine._select_enemy_target(target_player, text, prefer_zone)
    if cel is None:
        naplo.ir(f"Structured effect: {card.nev} -> nincs ervenyes sebzes-celpont.")
        return False
    EffectEngine._deal_damage_to_target(card.nev, amount, cel, target_player, "Structured", source_player)
    return True


def _resolve_destroy(card, source_player, target_player, context):
    if not _find_matching_tag(card, "destroy"):
        return False
    from engine.effects import EffectEngine

    cel = EffectEngine._select_enemy_target(target_player, normalize_lookup_text(_canonical_text(card)))
    if cel is None:
        naplo.ir(f"Structured effect: {card.nev} -> nincs megsemmisitheto celpont.")
        return False
    return EffectEngine._destroy_target(cel, source_player, target_player, "Structured")


def _resolve_exhaust(card, source_player, target_player, context):
    if not _find_matching_tag(card, "exhaust"):
        return False
    units = _enemy_units(target_player, "horizont")
    cel = _pick_unit(units)
    if cel is None:
        naplo.ir(f"Structured effect: {card.nev} -> nincs kimeritheto celpont.")
        return False
    _, _, unit = cel
    unit.kimerult = True
    naplo.ir(f"Structured effect: {card.nev} -> {unit.lap.nev} kimerult.")
    return True


def _resolve_reactivate(card, source_player, context):
    if not _find_matching_tag(card, "reactivate"):
        return False
    units = [item for item in _allied_units(source_player) if item[2].kimerult]
    cel = _pick_unit(units)
    if cel is None:
        naplo.ir(f"Structured effect: {card.nev} -> nincs ujraaktiválható celpont.")
        return False
    return source_player.ujraaktivalt_egyseget(cel[2], f"Structured: {card.nev}")


def _resolve_buff(card, source_player, context):
    text = _canonical_text(card)
    did = False
    cel = _pick_unit(_allied_units(source_player))
    if cel is None:
        return False
    _, _, unit = cel
    if _find_matching_tag(card, "atk_buff"):
        amount = max(1, _extract_number(text, 1))
        unit.akt_tamadas += amount
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


def _resolve_heal(card, source_player, context):
    if not _find_matching_tag(card, "heal"):
        return False
    amount = max(1, _extract_number(_canonical_text(card), 1))
    units = _allied_units(source_player)
    if has_target(card, "osszes_sajat") or has_target(card, "minden_sajat"):
        healed = 0
        for _, _, unit in units:
            max_hp = getattr(unit.lap, "eletero", 0) + getattr(unit, "bonus_max_hp", 0)
            before = unit.akt_hp
            unit.akt_hp = min(max_hp, unit.akt_hp + amount)
            healed += max(0, unit.akt_hp - before)
        if healed > 0:
            naplo.ir(f"Structured effect: {card.nev} -> osszesen {healed} HP gyogyitas.")
            return True
        return False

    cel = _pick_unit(units, weakest=True)
    if cel is None:
        return False
    _, _, unit = cel
    max_hp = getattr(unit.lap, "eletero", 0) + getattr(unit, "bonus_max_hp", 0)
    before = unit.akt_hp
    unit.akt_hp = min(max_hp, unit.akt_hp + amount)
    if unit.akt_hp > before:
        naplo.ir(f"Structured effect: {card.nev} -> {unit.lap.nev} gyogyult {unit.akt_hp - before} HP-t.")
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
        naplo.ir(f"Structured effect: {card.nev} -> poziciocsere tortent a {index + 1}. aramlatban.")
        return True
    return False


def _resolve_move_to_zenit(card, source_player, target_player, context):
    if not _find_matching_tag(card, "move_to_zenit"):
        return False
    from engine.effects import EffectEngine

    cel = EffectEngine._select_enemy_target(target_player, "horizont", "horizont")
    if cel is None:
        return False
    zone_name, index, _ = cel
    return ActionLibrary.move_target_to_zenit(target_player, zone_name, index, card.nev)


def _resolve_move_to_horizont(card, source_player, target_player, context):
    if not _find_matching_tag(card, "move_to_horizon"):
        return False
    units = _enemy_units(target_player, "zenit")
    for _, index, unit in units:
        if target_player.horizont[index] is None:
            return ActionLibrary.move_entity_between_zones(target_player, "zenit", index, "horizont", index, card.nev, exhausted=True)
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
    if _find_matching_tag(card, "cancel_attack") and attacker is not None:
        naplo.ir(f"Structured effect: {card.nev} -> tamadas semlegesitve.")
        did = True
    if _find_matching_tag(card, "no_ready") and attacker is not None:
        attacker.extra_exhausted_turns = getattr(attacker, "extra_exhausted_turns", 0) + 1
        did = True
    if _find_matching_tag(card, "cannot_attack") and attacker is not None:
        attacker.cannot_attack_until_turn_end = True
        did = True
    return did


def _resolve_misc_state(card, source_player, target_player, context):
    did = False
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
        units = _enemy_units(target_player) if target_player is not None else _allied_units(source_player)
        cel = _pick_unit(units)
        if cel is not None:
            did |= ActionLibrary.return_target_to_hand(target_player or source_player, cel[0], cel[1], card.nev)
    if _find_matching_tag(card, "immunity"):
        cel = _pick_unit(_allied_units(source_player), weakest=True)
        if cel is not None:
            cel[2].damage_immunity_until_turn_end = True
            naplo.ir(f"Structured effect: {card.nev} -> {cel[2].lap.nev} sebzesimmunitas a kor vegeig.")
            did = True
    if _find_matching_tag(card, "untargetable"):
        cel = _pick_unit(_allied_units(source_player))
        if cel is not None:
            state = getattr(cel[2], "targeting_state_override", None)
            if state is None:
                from engine.targeting import TargetingEngine
                state = TargetingEngine.target_state(cel[2])
            state.spell_negate = True
            naplo.ir(f"Structured effect: {card.nev} -> {cel[2].lap.nev} nem celozhato.")
            did = True
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
