"""State invariant checks for AI smoke tests.

This module is intentionally small. It validates the minimal MatchState shape
that the headless AI smoke runner will need, without checking game systems that
do not exist yet.
"""

from __future__ import annotations


class StateInvariantError(Exception):
    """Raised when MatchState invariant checks fail."""


def validate_state_invariants(state, runtime_package=None):
    errors = []
    players = list(getattr(state, "players", []) or [])
    player_ids = [getattr(player, "player_id", None) for player in players]

    if not getattr(state, "match_id", None):
        errors.append(_error("MATCH_ID_MISSING", "match_id must not be empty."))

    if _as_int(getattr(state, "turn_number", None)) < 1:
        errors.append(_error("TURN_NUMBER_INVALID", "turn_number must be >= 1."))

    if len(players) != 2:
        errors.append(_error("PLAYER_COUNT_INVALID", "AI smoke MatchState must have exactly two players."))

    for index, player in enumerate(players):
        player_id = getattr(player, "player_id", None)
        deck_id = getattr(player, "deck_id", None)
        if not player_id:
            errors.append(_error("PLAYER_ID_MISSING", "player_id must not be empty.", player_index=index))
        if not deck_id:
            errors.append(_error("DECK_ID_MISSING", "deck_id must not be empty.", player_id=player_id))
        if runtime_package is not None and deck_id:
            errors.extend(_validate_player_deck_refs(player, runtime_package))

    active_player_id = getattr(state, "active_player_id", None)
    if active_player_id not in player_ids:
        errors.append(
            _error(
                "ACTIVE_PLAYER_UNKNOWN",
                "active_player_id must refer to one of the players.",
                active_player_id=active_player_id,
            )
        )

    if not getattr(state, "phase", None):
        errors.append(_error("PHASE_MISSING", "phase must not be empty."))

    errors.extend(_validate_event_log(getattr(state, "event_log", []) or [], set(player_ids)))
    return errors


def assert_state_invariants(state, runtime_package=None):
    errors = validate_state_invariants(state, runtime_package)
    if errors:
        codes = ", ".join(error["code"] for error in errors)
        raise StateInvariantError("State invariant check failed: %s" % codes)
    return True


def _validate_player_deck_refs(player, runtime_package):
    errors = []
    player_id = getattr(player, "player_id", None)
    deck_id = getattr(player, "deck_id", None)
    decks_by_id = getattr(runtime_package, "decks_by_id", {}) or {}
    cards_by_id = getattr(runtime_package, "cards_by_id", {}) or {}

    if deck_id not in decks_by_id:
        errors.append(
            _error(
                "DECK_UNKNOWN",
                "player deck_id must exist in runtime package.",
                player_id=player_id,
                deck_id=deck_id,
            )
        )

    for card_index, card_id in enumerate(list(getattr(player, "deck_card_ids", []) or [])):
        if card_id not in cards_by_id:
            errors.append(
                _error(
                    "PLAYER_DECK_CARD_UNKNOWN",
                    "player deck_card_ids must exist in runtime package cards.",
                    player_id=player_id,
                    deck_id=deck_id,
                    card_id=card_id,
                    card_index=card_index,
                )
            )
    return errors


def _validate_event_log(event_log, player_ids):
    errors = []
    for index, event in enumerate(list(event_log or [])):
        event_index = _as_int(event.get("event_index"))
        if event_index != index:
            errors.append(
                _error(
                    "EVENT_INDEX_INVALID",
                    "event_index must match event_log position.",
                    expected_index=index,
                    actual_index=event.get("event_index"),
                )
            )

        if _as_int(event.get("turn_number")) < 1:
            errors.append(
                _error(
                    "EVENT_TURN_NUMBER_INVALID",
                    "event turn_number must be >= 1.",
                    event_index=index,
                    turn_number=event.get("turn_number"),
                )
            )

        event_player_id = event.get("player_id")
        if event_player_id is not None and event_player_id not in player_ids:
            errors.append(
                _error(
                    "EVENT_PLAYER_UNKNOWN",
                    "event player_id must refer to one of the players.",
                    event_index=index,
                    player_id=event_player_id,
                )
            )
    return errors


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _error(code, message, **details):
    error = {"code": code, "message": message}
    error.update(details)
    return error
