"""State invariant checks for AI smoke tests.

This module is intentionally small. It validates the minimal MatchState shape
that the headless AI smoke runner will need, without checking game systems that
do not exist yet.
"""

from __future__ import annotations

try:
    from card_instance import validate_card_instance_record
except ModuleNotFoundError:
    from engine.card_instance import validate_card_instance_record


class StateInvariantError(Exception):
    """Raised when MatchState invariant checks fail."""


def validate_state_invariants(state, runtime_package=None):
    errors = []
    players = list(getattr(state, "players", []) or [])
    player_ids = [getattr(player, "player_id", None) for player in players]
    card_instances = getattr(state, "card_instances", None)
    normalized_registry = card_instances if isinstance(card_instances, dict) else {}
    zone_occurrences = {}

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
        errors.extend(_validate_player_zones(player, normalized_registry, zone_occurrences))
        if runtime_package is not None and deck_id:
            errors.extend(_validate_player_deck_id(player, runtime_package))

    if not isinstance(card_instances, dict):
        errors.append(
            _error(
                "CARD_INSTANCE_REGISTRY_INVALID",
                "card_instances must be a dict keyed by card_instance_id.",
                actual_type=type(card_instances).__name__,
            )
        )
    else:
        errors.extend(_validate_card_instance_registry(card_instances, set(player_ids), runtime_package))
        errors.extend(_validate_zone_occurrences(card_instances, zone_occurrences))

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


def _validate_player_deck_id(player, runtime_package):
    errors = []
    player_id = getattr(player, "player_id", None)
    deck_id = getattr(player, "deck_id", None)
    decks_by_id = getattr(runtime_package, "decks_by_id", {}) or {}

    if deck_id not in decks_by_id:
        errors.append(
            _error(
                "DECK_UNKNOWN",
                "player deck_id must exist in runtime package.",
                player_id=player_id,
                deck_id=deck_id,
            )
        )

    return errors


def _validate_player_zones(player, card_instances, zone_occurrences):
    errors = []
    player_id = getattr(player, "player_id", None)
    zones = (
        ("deck", getattr(player, "deck_card_instance_ids", None)),
        ("hand", getattr(player, "hand_card_instance_ids", None)),
        ("discard", getattr(player, "discard_card_instance_ids", None)),
    )

    for zone_name, zone in zones:
        if zone is None:
            errors.append(
                _error(
                    "PLAYER_ZONE_MISSING",
                    "player zone list must not be None.",
                    player_id=player_id,
                    zone=zone_name,
                )
            )
            continue
        elif not isinstance(zone, list):
            errors.append(
                _error(
                    "PLAYER_ZONE_INVALID",
                    "player zone must be a list.",
                    player_id=player_id,
                    zone=zone_name,
                    actual_type=type(zone).__name__,
                )
            )
            continue

        for zone_index, card_instance_id in enumerate(zone):
            zone_occurrences.setdefault(card_instance_id, []).append(
                {
                    "player_id": player_id,
                    "zone": zone_name,
                    "zone_index": zone_index,
                }
            )
            card_instance = card_instances.get(card_instance_id)
            if not isinstance(card_instance, dict):
                errors.append(
                    _error(
                        "PLAYER_ZONE_INSTANCE_UNKNOWN",
                        "player zone entry must refer to a registry card instance.",
                        player_id=player_id,
                        zone=zone_name,
                        zone_index=zone_index,
                        card_instance_id=card_instance_id,
                    )
                )
                continue

            if card_instance.get("zone") != zone_name:
                errors.append(
                    _error(
                        "CARD_INSTANCE_ZONE_MISMATCH",
                        "registry zone must match the containing player zone.",
                        player_id=player_id,
                        card_instance_id=card_instance_id,
                        expected_zone=zone_name,
                        actual_zone=card_instance.get("zone"),
                    )
                )
            if card_instance.get("zone_index") != zone_index:
                errors.append(
                    _error(
                        "CARD_INSTANCE_ZONE_INDEX_MISMATCH",
                        "registry zone_index must match the containing list index.",
                        player_id=player_id,
                        card_instance_id=card_instance_id,
                        expected_zone_index=zone_index,
                        actual_zone_index=card_instance.get("zone_index"),
                    )
                )
            if card_instance.get("owner_player_id") != player_id:
                errors.append(
                    _error(
                        "CARD_INSTANCE_OWNER_MISMATCH",
                        "minimal player zone must contain an instance owned by that player.",
                        player_id=player_id,
                        card_instance_id=card_instance_id,
                        owner_player_id=card_instance.get("owner_player_id"),
                    )
                )
    return errors


def _validate_card_instance_registry(card_instances, player_ids, runtime_package):
    errors = []
    cards_by_id = None
    if runtime_package is not None:
        cards_by_id = getattr(runtime_package, "cards_by_id", {}) or {}
    for registry_key, card_instance in card_instances.items():
        if not isinstance(card_instance, dict):
            errors.append(
                _error(
                    "CARD_INSTANCE_RECORD_INVALID",
                    "card instance registry value must be a valid record dict.",
                    card_instance_id=registry_key,
                    record_errors=validate_card_instance_record(card_instance).get("errors", []),
                )
            )
            continue

        card_instance_id = card_instance.get("card_instance_id")
        if registry_key != card_instance_id:
            errors.append(
                _error(
                    "CARD_INSTANCE_REGISTRY_KEY_MISMATCH",
                    "registry key must match record card_instance_id.",
                    registry_key=registry_key,
                    card_instance_id=card_instance_id,
                )
            )

        record_validation = validate_card_instance_record(card_instance)
        if not record_validation.get("valid"):
            errors.append(
                _error(
                    "CARD_INSTANCE_RECORD_INVALID",
                    "card instance record failed contract validation.",
                    card_instance_id=registry_key,
                    record_errors=record_validation.get("errors", []),
                )
            )

        card_id = card_instance.get("card_id")
        if cards_by_id is not None and card_id not in cards_by_id:
            errors.append(
                _error(
                    "CARD_INSTANCE_CARD_UNKNOWN",
                    "card instance card_id must exist in runtime package cards.",
                    card_instance_id=registry_key,
                    card_id=card_id,
                )
            )

        owner_player_id = card_instance.get("owner_player_id")
        if owner_player_id not in player_ids:
            errors.append(
                _error(
                    "CARD_INSTANCE_OWNER_UNKNOWN",
                    "card instance owner_player_id must refer to a player.",
                    card_instance_id=registry_key,
                    owner_player_id=owner_player_id,
                )
            )

        controller_player_id = card_instance.get("controller_player_id")
        if controller_player_id is not None and controller_player_id not in player_ids:
            errors.append(
                _error(
                    "CARD_INSTANCE_CONTROLLER_UNKNOWN",
                    "card instance controller_player_id must refer to a player or be null.",
                    card_instance_id=registry_key,
                    controller_player_id=controller_player_id,
                )
            )
    return errors


def _validate_zone_occurrences(card_instances, zone_occurrences):
    errors = []
    for card_instance_id, occurrences in zone_occurrences.items():
        if len(occurrences) > 1:
            errors.append(
                _error(
                    "CARD_INSTANCE_MULTIPLE_ZONES",
                    "card_instance_id must occur in exactly one player zone.",
                    card_instance_id=card_instance_id,
                    occurrences=occurrences,
                )
            )

    for card_instance_id in card_instances:
        if not zone_occurrences.get(card_instance_id):
            errors.append(
                _error(
                    "CARD_INSTANCE_ORPHANED",
                    "registry card instance must occur in exactly one player zone.",
                    card_instance_id=card_instance_id,
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
