from __future__ import annotations

from engine.actions import ActionLibrary
from engine.board_utils import _is_board_entity, is_zenit_entity
from engine.card_metadata import has_effect_tag, has_keyword, has_target, has_trigger
from engine.triggers import trigger_engine
from utils.logger import naplo
from utils.text import normalize_lookup_text


TAG_ALIASES = {
    "laphuzas": "draw",
    "draw": "draw",
    "sebzes": "damage",
    "megsemmisites": "destroy",
    "kimerites": "exhaust",
    "visszaallitas": "reactivate",
    "atk_buff": "atk_buff",
    "hp_buff": "hp_buff",
    "gyogyitas": "heal",
    "poziciocsere": "swap_position",
    "mozgatas_zenitbe": "move_to_zenit",
    "mozgatas_horizontra": "move_to_horizon",
    "tamadassemlegesites": "cancel_attack",
    "sebzessemlegesites": "cancel_damage",
    "felallastiltas": "no_ready",
    "paklitetejere": "put_on_deck_top",
    "visszavetelkezbe": "return_to_hand",
    "immunitas": "immunity",
    "celozhatatlan": "untargetable",
    "tamadastiltas": "cannot_attack",
    "pecsetsebzes": "seal_damage",
}


SUPPORTED_EFFECT_TAGS = tuple(sorted(set(TAG_ALIASES.values())))


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
    tags = _normalized_tags(card)
    if not tags:
        return {"resolved": False, "mode": "no_structured"}

    handlers = (
        lambda: _resolve_draw(card, source_player, context or {}),
        lambda: _resolve_damage(card, source_player, target_player, context or {}),
        lambda: _resolve_destroy(card, source_player, target_player, context or {}),
        lambda: _resolve_exhaust(card, source_player, target_player, context or {}),
        lambda: _resolve_reactivate(card, source_player, context or {}),
        lambda: _resolve_buff(card, source_player, context or {}),
        lambda: _resolve_heal(card, source_player, context or {}),
        lambda: _resolve_swap(card, source_player, target_player, context or {}),
        lambda: _resolve_move_to_zenit(card, source_player, target_player, context or {}),
        lambda: _resolve_move_to_horizont(card, source_player, target_player, context or {}),
        lambda: _resolve_combat_control(card, source_player, target_player, context or {}),
        lambda: _resolve_misc_state(card, source_player, target_player, context or {}),
    )

    did_any = False
    for handler in handlers:
        try:
            did_any |= bool(handler())
        except Exception:
            continue

    if did_any:
        return {"resolved": True, "mode": "structured", "partial": False}

    status = normalize_lookup_text(getattr(card, "interpretation_status", ""))
    partial = status in {"partial", "reszleges", "structured_partial"}
    return {"resolved": partial, "mode": "structured", "partial": partial}


def is_passive_structured_card(card):
    if getattr(card, "keywords", None):
        if not getattr(card, "effect_tags", None) and not getattr(card, "triggers", None):
            return True
    return False


def get_structured_status(card):
    status = normalize_lookup_text(getattr(card, "interpretation_status", ""))
    if status:
        return status
    if is_passive_structured_card(card):
        return "passziv_kulcsszo"
    if getattr(card, "effect_tags", None):
        return "structured_partial"
    return "missing_implementation"

