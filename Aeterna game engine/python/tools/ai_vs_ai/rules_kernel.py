"""Minimal rules kernel for AI smoke work.

This is not the AETERNA rules engine. It only proves the first contract-first
loop: runtime package -> match state -> legal actions -> action resolve -> log.
"""

from __future__ import annotations

try:
    from match_state import MatchState, PlayerState
    from runtime_package_reader import RuntimePackageReadError
except ModuleNotFoundError:
    from .match_state import MatchState, PlayerState
    from .runtime_package_reader import RuntimePackageReadError


class RulesKernelError(Exception):
    """Raised when the minimal rules kernel rejects an operation."""


def create_initial_match_state(runtime_package, deck_id_a, deck_id_b, match_id="AI-SMOKE-001"):
    _ensure_valid_runtime_package_deck_refs(runtime_package)
    deck_a = _get_deck_or_raise(runtime_package, deck_id_a)
    deck_b = _get_deck_or_raise(runtime_package, deck_id_b)

    return MatchState(
        match_id=match_id,
        turn_number=1,
        active_player_id="P1",
        players=[
            PlayerState(player_id="P1", deck_id=deck_id_a, deck_card_ids=_expand_deck_card_ids(deck_a)),
            PlayerState(player_id="P2", deck_id=deck_id_b, deck_card_ids=_expand_deck_card_ids(deck_b)),
        ],
        phase="main",
        event_log=[],
    )


def list_legal_actions(state, player_id=None):
    player_id = player_id or state.active_player_id
    enabled = player_id == state.active_player_id
    action = {
        "action_id": "end_turn:%s:%s" % (state.turn_number, player_id),
        "action_type": "end_turn",
        "player_id": player_id,
        "enabled": enabled,
    }
    if not enabled:
        action["reason"] = "not_active_player"
    return [action]


def apply_action(state, action):
    action_type = action.get("action_type")
    if action_type != "end_turn":
        raise RulesKernelError("Unsupported action_type: %s" % action_type)
    if not action.get("enabled", False):
        raise RulesKernelError("Action is not enabled: %s" % action.get("action_id"))

    player_id = action.get("player_id")
    if player_id != state.active_player_id:
        raise RulesKernelError("Action player is not active: %s" % player_id)

    previous_player_id = state.active_player_id
    next_player_id = state.get_inactive_player_id()
    state.active_player_id = next_player_id
    if previous_player_id == "P2" and next_player_id == "P1":
        state.turn_number += 1

    event = {
        "event_index": len(state.event_log),
        "event_type": "action_resolved",
        "player_id": previous_player_id,
        "action_type": "end_turn",
        "turn_number": state.turn_number,
    }
    state.event_log.append(event)
    return {
        "ok": True,
        "action": dict(action),
        "event": event,
        "state": state,
    }


def _ensure_valid_runtime_package_deck_refs(runtime_package):
    errors = runtime_package.validate_deck_card_refs()
    if errors:
        first = errors[0]
        raise RulesKernelError(
            "Runtime package has invalid deck card references; first error: deck_id=%s card_id=%s"
            % (first.get("deck_id"), first.get("card_id"))
        )


def _get_deck_or_raise(runtime_package, deck_id):
    try:
        return runtime_package.get_deck(deck_id)
    except RuntimePackageReadError as exc:
        raise RulesKernelError("Unknown deck_id: %s" % deck_id) from exc


def _expand_deck_card_ids(deck):
    card_ids = []
    for entry in deck.get("card_entries", []) or []:
        count = int(entry.get("count") or 0)
        card_ids.extend([entry.get("card_id")] * count)
    return card_ids
