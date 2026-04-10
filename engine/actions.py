from engine.card import CsataEgyseg
from engine.board_utils import (
    _is_board_entity,
    _object_name,
    _object_type,
    is_zenit_entity,
    log_zone_write,
    set_zone_slot,
)
from engine.triggers import trigger_engine
from utils.logger import naplo
from utils.text import normalize_lookup_text


class ActionLibrary:
    @staticmethod
    def first_empty_slot(player, zone_name):
        zone = getattr(player, zone_name, None)
        if zone is None:
            return None
        for index, item in enumerate(zone):
            if item is None:
                return index
        return None

    @staticmethod
    def move_entity_between_zones(owner, from_zone, from_index, to_zone, to_index, reason, exhausted=None):
        source_zone = getattr(owner, from_zone, None)
        target_zone = getattr(owner, to_zone, None)
        if source_zone is None or target_zone is None:
            return False
        if from_index < 0 or from_index >= len(source_zone):
            return False
        if to_index < 0 or to_index >= len(target_zone):
            return False

        entity = source_zone[from_index]
        if not _is_board_entity(entity):
            return False
        if target_zone[to_index] is not None:
            return False

        set_zone_slot(owner, to_zone, to_index, entity, f"move:{reason}")
        set_zone_slot(owner, from_zone, from_index, None, f"move:{reason}")
        if exhausted is not None:
            entity.kimerult = exhausted
        trigger_engine.dispatch("on_position_changed", source=entity.lap, owner=owner, payload={"from": from_zone, "to": to_zone})
        if from_zone == "zenit" and to_zone == "horizont":
            trigger_engine.dispatch(
                "on_move_zenit_to_horizont",
                source=entity,
                owner=owner,
                target=entity,
                payload={"from": from_zone, "to": to_zone, "index": to_index, "reason": reason},
            )
        naplo.ir(f"{entity.lap.nev} atkerult {from_zone} -> {to_zone} ({reason})")
        return True

    @staticmethod
    def _all_units(player):
        result = []
        for zone_name in ("horizont", "zenit"):
            zone = getattr(player, zone_name)
            for index, unit in enumerate(zone):
                if _is_board_entity(unit):
                    result.append((zone_name, index, unit))
        return result

    @staticmethod
    def _units_in_zone(player, zone_name):
        return [
            (current_zone, index, unit)
            for current_zone, index, unit in ActionLibrary._all_units(player)
            if current_zone == zone_name
        ]

    @staticmethod
    def targets_for_key(owner, opponent, target_key, source=None, lane_index=None):
        key = normalize_lookup_text(target_key)
        source_unit = source if _is_board_entity(source) else None

        if key == "self":
            return [(None, None, source_unit)] if source_unit is not None else []

        if key == "own_entity":
            return ActionLibrary._all_units(owner)
        if key == "other_own_entity":
            return [item for item in ActionLibrary._all_units(owner) if item[2] is not source_unit]
        if key == "own_horizont_entity":
            return ActionLibrary._units_in_zone(owner, "horizont")
        if key == "own_zenit_entity":
            return ActionLibrary._units_in_zone(owner, "zenit")
        if key == "own_entities":
            return ActionLibrary._all_units(owner)
        if key == "own_horizont_entities":
            return ActionLibrary._units_in_zone(owner, "horizont")
        if key == "own_zenit_entities":
            return ActionLibrary._units_in_zone(owner, "zenit")

        if key == "enemy_entity":
            return ActionLibrary._all_units(opponent)
        if key == "enemy_horizont_entity":
            return ActionLibrary._units_in_zone(opponent, "horizont")
        if key == "enemy_zenit_entity":
            return ActionLibrary._units_in_zone(opponent, "zenit")
        if key == "enemy_entities":
            return ActionLibrary._all_units(opponent)
        if key == "enemy_horizont_entities":
            return ActionLibrary._units_in_zone(opponent, "horizont")
        if key == "enemy_zenit_entities":
            return ActionLibrary._units_in_zone(opponent, "zenit")

        if key == "opposing_entity" and opponent is not None and lane_index is not None:
            if 0 <= lane_index < len(getattr(opponent, "horizont", [])):
                front = opponent.horizont[lane_index]
                if _is_board_entity(front):
                    return [("horizont", lane_index, front)]
            if 0 <= lane_index < len(getattr(opponent, "zenit", [])):
                back = opponent.zenit[lane_index]
                if _is_board_entity(back):
                    return [("zenit", lane_index, back)]

        return []

    @staticmethod
    def select_target_for_key(owner, opponent, target_key, source=None, lane_index=None, weakest=False):
        targets = ActionLibrary.targets_for_key(
            owner,
            opponent,
            target_key,
            source=source,
            lane_index=lane_index,
        )
        if not targets:
            return None
        if weakest:
            return min(targets, key=lambda item: (item[2].akt_hp, item[2].akt_tamadas))
        return max(targets, key=lambda item: (item[2].akt_tamadas, item[2].akt_hp))

    @staticmethod
    def select_target(player, prefer_enemy=True, exhausted_only=False, weakest=False):
        units = ActionLibrary._all_units(player)
        if exhausted_only:
            units = [item for item in units if item[2].kimerult]
        if not units:
            return None
        if weakest:
            return min(units, key=lambda item: (item[2].akt_hp, item[2].akt_tamadas))
        return max(units, key=lambda item: (item[2].akt_tamadas, item[2].akt_hp))

    @staticmethod
    def exhaust_target(target, reason):
        target.kimerult = True
        naplo.ir(f"{target.lap.nev} kimerult ({reason})")
        return True

    @staticmethod
    def grant_keyword(target, keyword, temporary=False):
        attr = "temp_granted_keywords" if temporary else "granted_keywords"
        values = set(getattr(target, attr, set()) or set())
        values.add(normalize_lookup_text(keyword))
        setattr(target, attr, values)
        return True

    @staticmethod
    def ready_unit(target, reason="", owner=None, source=None):
        was_exhausted = bool(getattr(target, "kimerult", False))
        target.kimerult = False
        if was_exhausted:
            trigger_engine.dispatch(
                "on_ready_from_exhausted",
                source=source or target,
                owner=owner or getattr(target, "owner", None),
                target=target,
                payload={"reason": reason},
            )
        if reason:
            naplo.ir(f"{target.lap.nev} ujra aktivalodott ({reason})")
        return True

    @staticmethod
    def return_target_to_hand(owner, zone_name, index, reason):
        zone = getattr(owner, zone_name)
        unit = zone[index]
        if not _is_board_entity(unit):
            if unit is not None:
                naplo.ir(
                    f"[DEBUG:RETURN_TO_HAND_SKIPPED] {getattr(owner, 'nev', 'ismeretlen')} | {zone_name}[{index}] | tipus={_object_type(unit)} | nev={_object_name(unit)} | reason={reason}"
                )
            return False
        owner.kez.append(unit.lap)
        set_zone_slot(owner, zone_name, index, None, f"return_to_hand:{reason}")
        trigger_engine.dispatch("on_position_changed", source=unit.lap, owner=owner, payload={"from": zone_name, "to": "kez"})
        naplo.ir(f"{unit.lap.nev} visszakerult kezbe ({reason})")
        return True

    @staticmethod
    def move_target_to_zenit(owner, zone_name, index, reason):
        if zone_name != "horizont":
            return False
        front = owner.horizont[index]
        if not _is_board_entity(front):
            return False
        if getattr(front, "position_lock_awakenings", 0) > 0:
            naplo.ir(f"{front.lap.nev} nem valthat poziciot ({reason})")
            return False

        back = owner.zenit[index]
        if back is None:
            set_zone_slot(owner, "zenit", index, front, f"move_to_zenit:{reason}")
            set_zone_slot(owner, "horizont", index, None, f"move_to_zenit:{reason}")
        elif is_zenit_entity(back):
            set_zone_slot(owner, "horizont", index, back, f"swap_from_zenit:{reason}")
            set_zone_slot(owner, "zenit", index, front, f"swap_to_zenit:{reason}")
        else:
            log_zone_write(owner, "zenit", index, back, f"blocked_swap_non_entity:{reason}")
            naplo.ir(
                f"[DEBUG:MOVE_TO_ZENIT_BLOCKED] {getattr(owner, 'nev', 'ismeretlen')} | horizont[{index}] -> zenit[{index}] | tipus={_object_type(back)} | nev={_object_name(back)} | reason={reason}"
            )
            return False

        trigger_engine.dispatch("on_position_changed", source=front.lap, owner=owner, payload={"from": "horizont", "to": "zenit"})
        naplo.ir(f"{front.lap.nev} a Zenitbe kerult ({reason})")
        return True

    @staticmethod
    def move_target_to_horizont(owner, zone_name, index, reason, exhausted=True):
        if zone_name != "zenit":
            return False
        return ActionLibrary.move_entity_between_zones(
            owner,
            "zenit",
            index,
            "horizont",
            index,
            reason,
            exhausted=exhausted,
        )

    @staticmethod
    def revive_from_graveyard(owner, predicate, to_hand=True, reason="revive"):
        matches = [card for card in owner.temeto if predicate(card)]
        if not matches:
            return False
        card = matches[0]
        owner.temeto.remove(card)
        if to_hand:
            owner.kez.append(card)
            dest = "kez"
        else:
            for i in range(6):
                if owner.horizont[i] is None:
                    revived = CsataEgyseg(card)
                    revived.owner = owner
                    set_zone_slot(owner, "horizont", i, revived, f"revive_from_graveyard:{reason}")
                    dest = "horizont"
                    break
            else:
                owner.temeto.append(card)
                return False
        naplo.ir(f"{card.nev} visszatert a {dest} zonaba ({reason})")
        return True

    @staticmethod
    def search_deck_by_predicate(owner, predicate, to_hand=True, reason="search deck"):
        matches = [card for card in owner.pakli if predicate(card)]
        if not matches:
            return False
        card = matches[0]
        owner.pakli.remove(card)
        if to_hand:
            owner.kez.append(card)
            naplo.ir(f"{owner.nev} megtalalta ezt a lapot a pakliban: {card.nev} ({reason})")
        return True

    @staticmethod
    def search_graveyard_by_predicate(owner, predicate, to_hand=True, reason="search graveyard"):
        return ActionLibrary.revive_from_graveyard(owner, predicate, to_hand=to_hand, reason=reason)

    @staticmethod
    def inspect_top_card(owner, reason):
        if not owner.pakli:
            return False
        card = owner.pakli[-1]
        naplo.ir(f"Pakli teteje ({reason}): {card.nev}")
        return True

    @staticmethod
    def inspect_opponent_hand(opponent, reason):
        hand_names = ", ".join(card.nev for card in opponent.kez) or "-"
        naplo.ir(f"Ellenfel kez ({reason}): {hand_names}")
        return True

    @staticmethod
    def prohibit_attack_or_block(target, reason):
        setattr(target, "cannot_attack_until_turn_end", True)
        setattr(target, "cannot_block_until_turn_end", True)
        naplo.ir(f"{target.lap.nev} ebben a korben nem tamadhat es nem blokkolhat ({reason})")
        return True
