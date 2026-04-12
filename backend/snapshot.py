from __future__ import annotations

from engine.board_utils import is_trap, is_zenit_entity


def _as_int(value, default=None):
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _card_type_flags(card):
    card_type = str(getattr(card, "kartyatipus", "") or "")
    return {
        "is_entity": bool(getattr(card, "egyseg_e", "entit" in card_type.lower())),
        "is_trap": bool(getattr(card, "jel_e", "jel" in card_type.lower())),
        "is_field": bool(getattr(card, "sik_e", "sik" in card_type.lower())),
        "is_spell": bool(getattr(card, "spell_e", any(token in card_type.lower() for token in ("ige", "ritual", "rituale")))),
    }


def export_card_ref(card):
    if card is None:
        return None

    return {
        "name": getattr(card, "nev", None),
        "card_type": getattr(card, "kartyatipus", None),
        "realm": getattr(card, "birodalom", None),
        "clan": getattr(card, "klan", None),
        "magnitude": _as_int(getattr(card, "magnitudo", None), default=0),
        "aura_cost": _as_int(getattr(card, "aura_koltseg", None), default=0),
        **_card_type_flags(card),
    }


def export_unit_state(unit, zone_name=None, lane_index=None):
    if unit is None:
        return None

    card = getattr(unit, "lap", None)
    exhausted = bool(getattr(unit, "kimerult", False))
    face_down = bool(getattr(unit, "face_down", False))
    hidden = bool(getattr(unit, "hidden", False) or face_down)

    return {
        "kind": "entity",
        "zone": zone_name,
        "lane": lane_index,
        "position": {
            "zone": zone_name,
            "lane": lane_index,
        },
        "current_attack": _as_int(getattr(unit, "akt_tamadas", getattr(card, "tamadas", None)), default=0),
        "current_hp": _as_int(getattr(unit, "akt_hp", getattr(card, "eletero", None)), default=0),
        "exhausted": exhausted,
        "active": not exhausted,
        "face_down": face_down,
        "hidden": hidden,
        "card": export_card_ref(card),
    }


def _export_zone_object(obj, zone_name, lane_index):
    if obj is None:
        return {
            "kind": "empty",
            "zone": zone_name,
            "lane": lane_index,
            "position": {
                "zone": zone_name,
                "lane": lane_index,
            },
        }

    if is_zenit_entity(obj) or hasattr(obj, "lap"):
        return export_unit_state(obj, zone_name=zone_name, lane_index=lane_index)

    card = obj
    face_down = bool(zone_name == "zenit" and is_trap(obj))
    hidden = bool(face_down or getattr(card, "hidden", False))
    return {
        "kind": "card",
        "zone": zone_name,
        "lane": lane_index,
        "position": {
            "zone": zone_name,
            "lane": lane_index,
        },
        "face_down": face_down,
        "hidden": hidden,
        "card": export_card_ref(card),
    }


def export_player_state(player):
    hand = list(getattr(player, "kez", []) or [])
    deck = list(getattr(player, "pakli", []) or [])
    graveyard = list(getattr(player, "temeto", []) or [])
    seals = list(getattr(player, "pecsetek", []) or [])
    sources = list(getattr(player, "osforras", []) or [])
    horizont = list(getattr(player, "horizont", []) or [])
    zenit = list(getattr(player, "zenit", []) or [])

    source_cards = []
    for source in sources:
        if isinstance(source, dict):
            source_cards.append(export_card_ref(source.get("lap")))
        else:
            source_cards.append(export_card_ref(getattr(source, "lap", None) or source))

    return {
        "name": getattr(player, "nev", None),
        "realm": getattr(player, "birodalom", None),
        "deck_size": len(deck),
        "hand_size": len(hand),
        "graveyard_size": len(graveyard),
        "seal_count": len(seals),
        "source_count": len(sources),
        "overflow_defeat": bool(getattr(player, "overflow_vereseg", False)),
        "hand_cards": [export_card_ref(card) for card in hand],
        "source_cards": source_cards,
        "horizont": [_export_zone_object(obj, "horizont", index) for index, obj in enumerate(horizont)],
        "zenit": [_export_zone_object(obj, "zenit", index) for index, obj in enumerate(zenit)],
    }


def _detect_active_player_name(game):
    state = getattr(game, "state", None)
    candidate = getattr(state, "active_player", None)
    if candidate is None:
        candidate = getattr(game, "active_player", None)
    if candidate is None:
        return None
    return getattr(candidate, "nev", candidate)


def _detect_phase(game):
    state = getattr(game, "state", None)
    phase = getattr(state, "phase", None)
    if phase is not None:
        return phase
    return getattr(game, "phase", None)


def _detect_winner_name(game):
    state = getattr(game, "state", None)
    state_winner = getattr(state, "winner", None)
    if state_winner is not None:
        return getattr(state_winner, "nev", state_winner)

    overflow = getattr(game, "_overflow_gyoztes", None)
    if callable(overflow):
        winner = overflow()
        if winner:
            return getattr(winner, "nev", winner)

    p1 = getattr(game, "p1", None)
    p2 = getattr(game, "p2", None)
    if getattr(p1, "overflow_vereseg", False):
        return getattr(p2, "nev", None)
    if getattr(p2, "overflow_vereseg", False):
        return getattr(p1, "nev", None)
    return None


def _detect_victory_reason(game, winner_name):
    state = getattr(game, "state", None)
    state_reason = getattr(state, "victory_reason", None)
    if state_reason:
        return state_reason

    if winner_name is None:
        return None

    p1 = getattr(game, "p1", None)
    p2 = getattr(game, "p2", None)
    if getattr(p1, "overflow_vereseg", False) or getattr(p2, "overflow_vereseg", False):
        return "overflow"
    if p1 is not None and len(getattr(p1, "pecsetek", []) or []) == 0:
        return "seal_break_finish"
    if p2 is not None and len(getattr(p2, "pecsetek", []) or []) == 0:
        return "seal_break_finish"
    return "unknown"


def export_match_snapshot(game):
    state = getattr(game, "state", None)
    winner_name = _detect_winner_name(game)
    turn = _as_int(getattr(game, "kor", getattr(getattr(game, "state", None), "kor", None)), default=0)
    log_metrics = dict(getattr(game, "log_metrics", {}) or {})
    match_finished = bool(getattr(state, "match_finished", False) or winner_name is not None)

    return {
        "turn": turn,
        "active_player": _detect_active_player_name(game),
        "phase": _detect_phase(game),
        "match_finished": match_finished,
        "winner": winner_name,
        "victory_reason": _detect_victory_reason(game, winner_name),
        "p1": export_player_state(getattr(game, "p1", None)),
        "p2": export_player_state(getattr(game, "p2", None)),
        "log_metrics": log_metrics,
    }
