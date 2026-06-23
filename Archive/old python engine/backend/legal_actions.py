from __future__ import annotations


def _available_aura(player):
    if player is None:
        return 0
    aura_fn = getattr(player, "elerheto_aura", None)
    if callable(aura_fn):
        return aura_fn()
    return 0


def _effective_cost(player, card):
    if player is None or card is None:
        return None
    cost_fn = getattr(player, "effektiv_aura_koltseg", None)
    if callable(cost_fn):
        return cost_fn(card)
    return getattr(card, "aura_koltseg", None)


def _meets_basic_play_requirements(player, card):
    if player is None or card is None:
        return False
    if _available_aura(player) < (_effective_cost(player, card) or 0):
        return False
    if getattr(card, "magnitudo", 0) > len(getattr(player, "osforras", []) or []):
        return False
    return True


def _empty_lanes(zone):
    if zone is None:
        return []
    return [index for index, item in enumerate(zone) if item is None]


def _active_trap_count(player):
    zenit = getattr(player, "zenit", []) or []
    count = 0
    for item in zenit:
        if item is None:
            continue
        if getattr(item, "jel_e", False) or ("jel" in str(getattr(item, "kartyatipus", "") or "").lower()):
            count += 1
    return count


def _player_name(player):
    return getattr(player, "nev", None)


def _is_active_player(game, player):
    state = getattr(game, "state", None)
    active_player = getattr(state, "active_player", None)
    if active_player is None:
        return True
    return active_player is player or _player_name(active_player) == _player_name(player)


def _is_action_phase(game):
    state = getattr(game, "state", None)
    phase = getattr(state, "phase", None)
    if phase is None:
        return True
    return phase == "play"


def get_legal_actions_for_player(game, player):
    if game is None or player is None:
        return []
    state = getattr(game, "state", None)
    if bool(getattr(state, "match_finished", False)):
        return []
    if not _is_active_player(game, player):
        return []
    if not _is_action_phase(game):
        return []

    actions = [
        {
            "action_type": "end_turn",
            "player": _player_name(player),
            "reason": "default_progression",
        }
    ]

    hand = list(getattr(player, "kez", []) or [])
    horizon_lanes = _empty_lanes(getattr(player, "horizont", None))
    zenit_lanes = _empty_lanes(getattr(player, "zenit", None))
    active_traps = _active_trap_count(player)

    for card in hand:
        if not _meets_basic_play_requirements(player, card):
            continue

        if getattr(card, "egyseg_e", False):
            for lane in horizon_lanes:
                actions.append(
                    {
                        "action_type": "play_entity",
                        "player": _player_name(player),
                        "card_name": getattr(card, "nev", None),
                        "zone": "horizont",
                        "lane": lane,
                        "source": "hand",
                    }
                )
            for lane in zenit_lanes:
                actions.append(
                    {
                        "action_type": "play_entity",
                        "player": _player_name(player),
                        "card_name": getattr(card, "nev", None),
                        "zone": "zenit",
                        "lane": lane,
                        "source": "hand",
                    }
                )
            continue

        if getattr(card, "jel_e", False):
            if active_traps >= 2:
                continue
            for lane in zenit_lanes:
                actions.append(
                    {
                        "action_type": "play_trap",
                        "player": _player_name(player),
                        "card_name": getattr(card, "nev", None),
                        "zone": "zenit",
                        "lane": lane,
                        "source": "hand",
                    }
                )

    return actions
