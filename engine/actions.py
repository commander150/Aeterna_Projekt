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
    def _collection_targets(player, collection_name, predicate=None):
        collection = getattr(player, collection_name, None)
        if collection is None:
            return []
        result = []
        for index, item in enumerate(collection):
            if predicate is not None and not predicate(item):
                continue
            result.append((collection_name, index, item))
        return result

    @staticmethod
    def _source_targets(player):
        collection = getattr(player, "osforras", None)
        if collection is None:
            return []
        result = []
        for index, item in enumerate(collection):
            if isinstance(item, dict):
                card = item.get("lap")
            else:
                card = getattr(item, "lap", None) or item
            if card is None:
                continue
            result.append(("osforras", index, card))
        return result

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
        if getattr(entity, "position_lock_awakenings", 0) > 0:
            naplo.ir(f"{entity.lap.nev} nem valthat poziciot ({reason})")
            return False
        if target_zone[to_index] is not None:
            return False

        set_zone_slot(owner, to_zone, to_index, entity, f"move:{reason}")
        set_zone_slot(owner, from_zone, from_index, None, f"move:{reason}")
        if exhausted is not None:
            entity.kimerult = exhausted
        trigger_engine.dispatch("on_position_changed", source=entity.lap, owner=owner, payload={"from": from_zone, "to": to_zone})
        if to_zone == "horizont":
            trigger_engine.dispatch(
                "on_entity_enters_horizont",
                source=entity,
                owner=owner,
                target=entity,
                payload={"from": from_zone, "to": to_zone, "index": to_index, "reason": reason},
            )
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
        if key == "own_hand":
            return ActionLibrary._collection_targets(owner, "kez")
        if key == "own_deck":
            return ActionLibrary._collection_targets(owner, "pakli")
        if key == "own_graveyard":
            return ActionLibrary._collection_targets(owner, "temeto")
        if key == "own_graveyard_entity":
            return ActionLibrary._collection_targets(
                owner,
                "temeto",
                predicate=lambda card: "entitas" in normalize_lookup_text(getattr(card, "kartyatipus", "")),
            )
        if key == "own_source_card":
            return ActionLibrary._source_targets(owner)

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
        if key == "enemy_hand":
            return ActionLibrary._collection_targets(opponent, "kez")
        if key == "enemy_hand_card":
            return ActionLibrary._collection_targets(opponent, "kez")
        if key == "enemy_source_card":
            return ActionLibrary._source_targets(opponent)
        if key == "enemy_spell" and source is not None and opponent is not None:
            card_type = normalize_lookup_text(getattr(source, "kartyatipus", ""))
            if any(token in card_type for token in ("ige", "rituale", "ritual")):
                return [("spell_stack", 0, source)]
        if key == "enemy_spell_or_ritual" and source is not None and opponent is not None:
            card_type = normalize_lookup_text(getattr(source, "kartyatipus", ""))
            if any(token in card_type for token in ("ige", "rituale", "ritual")):
                return [("spell_stack", 0, source)]

        if key == "opposing_entity" and opponent is not None and lane_index is not None:
            if 0 <= lane_index < len(getattr(opponent, "horizont", [])):
                front = opponent.horizont[lane_index]
                if _is_board_entity(front):
                    return [("horizont", lane_index, front)]
            if 0 <= lane_index < len(getattr(opponent, "zenit", [])):
                back = opponent.zenit[lane_index]
                if _is_board_entity(back):
                    return [("zenit", lane_index, back)]
        if key == "lane" and lane_index is not None:
            return [("lane", lane_index, lane_index)]

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
        if not _is_board_entity(targets[0][2]):
            return targets[0]
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
    def abilities_locked(target):
        return bool(getattr(target, "abilities_locked_until_turn_end", False))

    @staticmethod
    def exhaust_target(target, reason):
        target.kimerult = True
        naplo.ir(f"{target.lap.nev} kimerult ({reason})")
        return True

    @staticmethod
    def grant_keyword(target, keyword, temporary=False, owner=None, source=None):
        attr = "temp_granted_keywords" if temporary else "granted_keywords"
        values = set(getattr(target, attr, set()) or set())
        normalized_keyword = normalize_lookup_text(keyword)
        already_had = normalized_keyword in values
        values.add(normalized_keyword)
        setattr(target, attr, values)
        if not already_had:
            trigger_engine.dispatch(
                "on_gain_keyword",
                source=source or target,
                owner=owner or getattr(target, "owner", None),
                target=target,
                payload={"keyword": normalized_keyword, "temporary": temporary},
            )
        return True

    @staticmethod
    def restrict_attack(target, reason):
        target.cannot_attack_until_turn_end = True
        if reason:
            naplo.ir(f"{target.lap.nev} ebben a korben nem tamadhat ({reason})")
        return True

    @staticmethod
    def restrict_block(target, reason):
        target.cannot_block_until_turn_end = True
        if reason:
            naplo.ir(f"{target.lap.nev} ebben a korben nem blokkolhat ({reason})")
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
    def heal_unit(target, amount, reason="", owner=None, source=None):
        if amount <= 0 or not _is_board_entity(target):
            return 0
        max_hp = getattr(target.lap, "eletero", 0) + getattr(target, "bonus_max_hp", 0)
        before = getattr(target, "akt_hp", 0)
        target.akt_hp = min(max_hp, before + amount)
        healed = max(0, target.akt_hp - before)
        if healed > 0:
            trigger_engine.dispatch(
                "on_heal",
                source=source or target,
                owner=owner or getattr(target, "owner", None),
                target=target,
                payload={"amount": healed, "reason": reason},
            )
            if reason:
                naplo.ir(f"{target.lap.nev} gyogyult {healed} HP-t ({reason})")
        return healed

    @staticmethod
    def grant_untargetable(target, reason="", owner=None, source=None):
        if not _is_board_entity(target):
            return False
        from engine.targeting import TargetingEngine

        state = TargetingEngine.target_state(target)
        target.targeting_state_override = state
        state.untargetable = True
        if reason:
            naplo.ir(f"{target.lap.nev} nem celozhato ({reason})")
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
        from engine.targeting import TargetingEngine

        valid, _ = TargetingEngine.validate(unit, "return_to_hand")
        if not valid:
            naplo.ir(f"{unit.lap.nev} nem kuldheto vissza kezbe ({reason})")
            return False
        owner.kez.append(unit.lap)
        set_zone_slot(owner, zone_name, index, None, f"return_to_hand:{reason}")
        trigger_engine.dispatch("on_position_changed", source=unit.lap, owner=owner, payload={"from": zone_name, "to": "kez"})
        trigger_engine.dispatch("on_bounce", source=unit.lap, owner=owner, target=unit, payload={"from": zone_name, "to": "kez", "reason": reason})
        naplo.ir(f"{unit.lap.nev} visszakerult kezbe ({reason})")
        return True

    @staticmethod
    def discard_from_hand(owner, index, reason):
        hand = getattr(owner, "kez", None)
        if hand is None or not (0 <= index < len(hand)):
            return False
        card = hand.pop(index)
        owner.temeto.append(card)
        trigger_engine.dispatch("on_position_changed", source=card, owner=owner, payload={"from": "kez", "to": "temeto"})
        trigger_engine.dispatch("on_discard", source=card, owner=owner, target=owner, payload={"from": "kez", "to": "temeto", "reason": reason})
        naplo.ir(f"{card.nev} eldobva ({reason})")
        return True

    @staticmethod
    def move_target_to_zenit(owner, zone_name, index, reason):
        if zone_name != "horizont":
            return False
        front = owner.horizont[index]
        if not _is_board_entity(front):
            return False
        from engine.targeting import TargetingEngine

        valid, _ = TargetingEngine.validate(front, "spell")
        if not valid:
            naplo.ir(f"{front.lap.nev} nem mozgathato a Zenitbe ({reason})")
            return False
        if getattr(front, "position_lock_awakenings", 0) > 0:
            naplo.ir(f"{front.lap.nev} nem valthat poziciot ({reason})")
            return False

        back = owner.zenit[index]
        if _is_board_entity(back) and getattr(back, "position_lock_awakenings", 0) > 0:
            naplo.ir(f"{back.lap.nev} nem valthat poziciot ({reason})")
            return False
        if back is None:
            set_zone_slot(owner, "zenit", index, front, f"move_to_zenit:{reason}")
            set_zone_slot(owner, "horizont", index, None, f"move_to_zenit:{reason}")
        elif is_zenit_entity(back):
            set_zone_slot(owner, "horizont", index, back, f"swap_from_zenit:{reason}")
            set_zone_slot(owner, "zenit", index, front, f"swap_to_zenit:{reason}")
            trigger_engine.dispatch(
                "on_position_swap",
                source=front,
                owner=owner,
                target=back,
                payload={"index": index, "reason": reason},
            )
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
    def summon_card_to_horizont(owner, card, lane_index=None, reason="summon", exhausted=True, payload=None):
        if owner is None or card is None:
            return None
        if lane_index is None:
            lane_index = ActionLibrary.first_empty_slot(owner, "horizont")
        if lane_index is None:
            return None
        if owner.horizont[lane_index] is not None:
            return None

        for collection_name in ("kez", "pakli", "temeto"):
            collection = getattr(owner, collection_name, None)
            if isinstance(collection, list) and card in collection:
                collection.remove(card)
                break

        unit = CsataEgyseg(card)
        unit.owner = owner
        unit.kimerult = exhausted
        set_zone_slot(owner, "horizont", lane_index, unit, f"summon:{reason}")
        summon_payload = {"zone": "horizont"}
        if isinstance(payload, dict):
            summon_payload.update(payload)
        trigger_engine.dispatch("on_summon", source=unit, owner=owner, payload=summon_payload)
        trigger_engine.dispatch(
            "on_entity_enters_horizont",
            source=unit,
            owner=owner,
            target=unit,
            payload={"from": "external", "to": "horizont", "index": lane_index, "reason": reason},
        )
        naplo.ir(f"{unit.lap.nev} a Horizontra kerult ({reason})")
        return unit

    @staticmethod
    def move_target_to_deck(owner, zone_name, index, reason, to_bottom=False):
        zone = getattr(owner, zone_name, None)
        if zone is None or not (0 <= index < len(zone)):
            return False
        item = zone[index]
        if item is None:
            return False
        from engine.targeting import TargetingEngine

        if _is_board_entity(item):
            valid, _ = TargetingEngine.validate(item, "spell")
            if not valid:
                naplo.ir(f"{item.lap.nev} nem mozgathato pakliba ({reason})")
                return False
        card = item.lap if _is_board_entity(item) else item
        if zone_name == "osforras":
            zone.pop(index)
        elif zone_name in {"kez", "pakli", "temeto"}:
            zone.pop(index)
        else:
            zone[index] = None
        if to_bottom:
            owner.pakli.insert(0, card)
            destination = "pakli_alja"
        else:
            owner.pakli.append(card)
            destination = "pakli_teteje"
        trigger_engine.dispatch("on_position_changed", source=card, owner=owner, payload={"from": zone_name, "to": destination})
        naplo.ir(f"{card.nev} visszakerult a {destination} ({reason})")
        return True

    @staticmethod
    def move_target_to_source(owner, zone_name, index, reason):
        zone = getattr(owner, zone_name, None)
        if zone is None or not (0 <= index < len(zone)):
            return False
        item = zone[index]
        if item is None:
            return False
        from engine.targeting import TargetingEngine

        if _is_board_entity(item):
            valid, _ = TargetingEngine.validate(item, "spell")
            if not valid:
                naplo.ir(f"{item.lap.nev} nem mozgathato osforrasba ({reason})")
                return False
        card = item.lap if _is_board_entity(item) else item
        if zone_name == "osforras":
            zone.pop(index)
        elif zone_name in {"kez", "pakli", "temeto"}:
            zone.pop(index)
        else:
            zone[index] = None
        owner.osforras.append({"lap": card, "hasznalt": False})
        trigger_engine.dispatch("on_position_changed", source=card, owner=owner, payload={"from": zone_name, "to": "osforras"})
        trigger_engine.dispatch(
            "on_source_placement",
            source=card,
            owner=owner,
            target=owner,
            payload={"from": zone_name, "to": "osforras", "reason": reason},
        )
        naplo.ir(f"{card.nev} az osforrasok koze kerult ({reason})")
        return True

    @staticmethod
    def grant_resource(owner, amount, reason):
        gained = 0
        for _ in range(max(0, amount)):
            if not getattr(owner, "pakli", None):
                break
            card = owner.pakli.pop()
            owner.osforras.append({"lap": card, "hasznalt": False})
            trigger_engine.dispatch(
                "on_source_placement",
                source=card,
                owner=owner,
                target=owner,
                payload={"from": "pakli", "to": "osforras", "reason": reason},
            )
            gained += 1
        if gained > 0:
            naplo.ir(f"{owner.nev} {gained} osforrast kapott ({reason})")
        return gained

    @staticmethod
    def apply_cost_mod(owner, amount, scope="entity", reason=""):
        if amount <= 0:
            return False
        normalized_scope = normalize_lookup_text(scope)
        if normalized_scope == "trap":
            owner.kovetkezo_jel_kedvezmeny = getattr(owner, "kovetkezo_jel_kedvezmeny", 0) + amount
        elif normalized_scope == "machine":
            owner.kovetkezo_gepezet_kedvezmeny = getattr(owner, "kovetkezo_gepezet_kedvezmeny", 0) + amount
        else:
            owner.kovetkezo_entitas_kedvezmeny = getattr(owner, "kovetkezo_entitas_kedvezmeny", 0) + amount
        if reason:
            naplo.ir(f"{owner.nev} {amount} koltsegcsokkentest kapott ({reason}, {normalized_scope})")
        return True

    @staticmethod
    def lock_abilities(target, reason="", owner=None, source=None):
        if not _is_board_entity(target):
            return False
        target.abilities_locked_until_turn_end = True
        markers = set(getattr(target, "negative_spell_markers", set()) or set())
        markers.add("ability_lock")
        target.negative_spell_markers = markers
        if reason:
            naplo.ir(f"{target.lap.nev} kepessegei le vannak tiltva a kor vegeig ({reason})")
        return True

    @staticmethod
    def lock_position(target, awakenings=1, reason="", owner=None, source=None):
        if not _is_board_entity(target):
            return False
        target.position_lock_awakenings = max(awakenings, getattr(target, "position_lock_awakenings", 0))
        markers = set(getattr(target, "negative_spell_markers", set()) or set())
        markers.add("position_lock")
        target.negative_spell_markers = markers
        if reason:
            naplo.ir(f"{target.lap.nev} addig nem valthat poziciot ({reason})")
        return True

    @staticmethod
    def summon_token_to_horizont(owner, lane_index, name, atk, hp, race="Token", realm="Semleges", exhausted=True):
        from types import SimpleNamespace

        token_card = SimpleNamespace(
            nev=name,
            kartyatipus="Entitas",
            birodalom=realm,
            klan="",
            faj=race,
            kaszt="",
            magnitudo=1,
            aura_koltseg=0,
            tamadas=atk,
            eletero=hp,
            kepesseg="",
            egyseg_e=True,
            jel_e=False,
            reakcio_e=False,
        )
        return ActionLibrary.summon_card_to_horizont(
            owner,
            token_card,
            lane_index=lane_index,
            reason=f"token:{name}",
            exhausted=exhausted,
            payload={"token": True},
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
            revived = ActionLibrary.summon_card_to_horizont(
                owner,
                card,
                lane_index=ActionLibrary.first_empty_slot(owner, "horizont"),
                reason=f"revive_from_graveyard:{reason}",
                exhausted=False,
                payload={"revived": True},
            )
            if revived is None:
                owner.temeto.append(card)
                return False
            dest = "horizont"
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
        ActionLibrary.restrict_attack(target, "")
        ActionLibrary.restrict_block(target, "")
        naplo.ir(f"{target.lap.nev} ebben a korben nem tamadhat es nem blokkolhat ({reason})")
        return True
