from engine.card import CsataEgyseg
from engine.triggers import trigger_engine
from utils.logger import naplo


class ActionLibrary:
    @staticmethod
    def _all_units(player):
        result = []
        for zone_name in ("horizont", "zenit"):
            zone = getattr(player, zone_name)
            for index, unit in enumerate(zone):
                if isinstance(unit, CsataEgyseg):
                    result.append((zone_name, index, unit))
        return result

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
        naplo.ir(f"🧊 {target.lap.nev} kimerült ({reason})")
        return True

    @staticmethod
    def return_target_to_hand(owner, zone_name, index, reason):
        zone = getattr(owner, zone_name)
        unit = zone[index]
        if not isinstance(unit, CsataEgyseg):
            return False
        owner.kez.append(unit.lap)
        zone[index] = None
        trigger_engine.dispatch("on_position_changed", source=unit.lap, owner=owner, payload={"from": zone_name, "to": "kez"})
        naplo.ir(f"↩️ {unit.lap.nev} visszakerült kézbe ({reason})")
        return True

    @staticmethod
    def move_target_to_zenit(owner, zone_name, index, reason):
        if zone_name != "horizont":
            return False
        front = owner.horizont[index]
        if not isinstance(front, CsataEgyseg):
            return False
        if getattr(front, "position_lock_awakenings", 0) > 0:
            naplo.ir(f"⛔ {front.lap.nev} nem válthat pozíciót ({reason})")
            return False
        if owner.zenit[index] is None:
            owner.zenit[index] = front
            owner.horizont[index] = None
        else:
            owner.horizont[index], owner.zenit[index] = owner.zenit[index], owner.horizont[index]
        trigger_engine.dispatch("on_position_changed", source=front.lap, owner=owner, payload={"from": "horizont", "to": "zenit"})
        naplo.ir(f"🔁 {front.lap.nev} a Zenitbe került ({reason})")
        return True

    @staticmethod
    def revive_from_graveyard(owner, predicate, to_hand=True, reason="revive"):
        matches = [card for card in owner.temeto if predicate(card)]
        if not matches:
            return False
        card = matches[0]
        owner.temeto.remove(card)
        if to_hand:
            owner.kez.append(card)
            dest = "kéz"
        else:
            for i in range(6):
                if owner.horizont[i] is None:
                    owner.horizont[i] = CsataEgyseg(card)
                    owner.horizont[i].owner = owner
                    dest = "horizont"
                    break
            else:
                owner.temeto.append(card)
                return False
        naplo.ir(f"♻️ {card.nev} visszatért a {dest} zónába ({reason})")
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
            naplo.ir(f"🔎 {owner.nev} megtalálta ezt a lapot a pakliban: {card.nev} ({reason})")
        return True

    @staticmethod
    def search_graveyard_by_predicate(owner, predicate, to_hand=True, reason="search graveyard"):
        return ActionLibrary.revive_from_graveyard(owner, predicate, to_hand=to_hand, reason=reason)

    @staticmethod
    def inspect_top_card(owner, reason):
        if not owner.pakli:
            return False
        card = owner.pakli[-1]
        naplo.ir(f"👁️ Pakli teteje ({reason}): {card.nev}")
        return True

    @staticmethod
    def inspect_opponent_hand(opponent, reason):
        hand_names = ", ".join(card.nev for card in opponent.kez) or "-"
        naplo.ir(f"👁️ Ellenfél kéz ({reason}): {hand_names}")
        return True

    @staticmethod
    def prohibit_attack_or_block(target, reason):
        setattr(target, "cannot_attack_until_turn_end", True)
        setattr(target, "cannot_block_until_turn_end", True)
        naplo.ir(f"🚫 {target.lap.nev} ebben a körben nem támadhat és nem blokkolhat ({reason})")
        return True
