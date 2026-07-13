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

try:
    from zone_move import validate_zone_move_record
except ModuleNotFoundError:
    from engine.zone_move import validate_zone_move_record

try:
    from engine_event import validate_engine_event_envelope
except ModuleNotFoundError:
    from engine.engine_event import validate_engine_event_envelope

_LEGACY_DRAW_ENVELOPE_FIELDS = (
    "card_instance_id",
    "card_id",
    "from_zone",
    "from_zone_index",
    "to_zone",
    "to_zone_index",
)


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

    errors.extend(
        _validate_event_log(
            getattr(state, "event_log", []) or [],
            set(player_ids),
            normalized_registry,
        )
    )
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


def _validate_event_log(event_log, player_ids, card_instances):
    errors = []
    for index, event in enumerate(list(event_log or [])):
        if not isinstance(event, dict):
            errors.append(
                _error(
                    "ENGINE_EVENT_CONTRACT_INVALID",
                    "event log entry must be a dict.",
                    event_index=index,
                    actual_type=type(event).__name__,
                )
            )
            continue

        event_index = event.get("event_index")
        if not _is_integer(event_index) or event_index != index:
            errors.append(
                _error(
                    "EVENT_INDEX_INVALID",
                    "event_index must match event_log position.",
                    expected_index=index,
                    actual_index=event.get("event_index"),
                )
            )

        event_sequence = event.get("event_sequence")
        if not _is_integer(event_sequence) or event_sequence != index + 1:
            errors.append(
                _error(
                    "ENGINE_EVENT_SEQUENCE_INVALID",
                    "event_sequence must match the one-based event log position.",
                    event_index=index,
                    expected_sequence=index + 1,
                    actual_sequence=event_sequence,
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

        payload = event.get("payload")
        is_engine_event = event.get("contract_type") == "engine_event" or event.get("event_type") == "zone_move"
        is_zone_move = event.get("event_type") == "zone_move" or (
            isinstance(payload, dict) and payload.get("event_type") == "zone_move"
        )
        if is_engine_event:
            errors.extend(_validate_engine_event_contract(event, index))
        if is_zone_move:
            errors.extend(_validate_zone_move_engine_event(event, index, card_instances))
    return errors


def _validate_engine_event_contract(event, event_index):
    errors = []
    envelope_validation = validate_engine_event_envelope(event)
    if not envelope_validation.get("valid"):
        errors.append(
            _error(
                "ENGINE_EVENT_CONTRACT_INVALID",
                "runtime engine event must use the canonical engine-event envelope.",
                event_index=event_index,
                envelope_errors=envelope_validation.get("errors", []),
            )
        )
    return errors


def _validate_zone_move_engine_event(event, event_index, card_instances):
    errors = []
    forbidden_fields = [field_name for field_name in _LEGACY_DRAW_ENVELOPE_FIELDS if field_name in event]
    contract_invalid = (
        forbidden_fields
        or event.get("event_type") != "zone_move"
        or event.get("action_type") != "draw_card"
    )
    if contract_invalid:
        errors.append(
            _error(
                "ENGINE_EVENT_CONTRACT_INVALID",
                "ZoneMove runtime event must use the canonical engine-event envelope.",
                event_index=event_index,
                forbidden_fields=forbidden_fields,
                contract_type=event.get("contract_type"),
                event_type=event.get("event_type"),
                action_type=event.get("action_type"),
                state_version=event.get("state_version"),
            )
        )

    payload = event.get("payload")
    if not isinstance(payload, dict):
        errors.append(
            _error(
                "ZONE_MOVE_PAYLOAD_INVALID",
                "ZoneMove engine event payload must be a ZoneMove record dict.",
                event_index=event_index,
                actual_type=type(payload).__name__,
            )
        )
        return errors

    payload_validation = validate_zone_move_record(payload)
    if not payload_validation.get("valid"):
        errors.append(
            _error(
                "ZONE_MOVE_PAYLOAD_INVALID",
                "ZoneMove engine event payload failed contract validation.",
                event_index=event_index,
                payload_errors=payload_validation.get("errors", []),
            )
        )

    for field_name in ("event_sequence", "state_version", "event_type"):
        if event.get(field_name) != payload.get(field_name):
            errors.append(
                _error(
                    "ZONE_MOVE_ENVELOPE_MISMATCH",
                    "ZoneMove envelope field must match its payload.",
                    event_index=event_index,
                    field=field_name,
                    envelope_value=event.get(field_name),
                    payload_value=payload.get(field_name),
                )
            )

    if event.get("action_type") != payload.get("source_action_type"):
        errors.append(
            _error(
                "ZONE_MOVE_ENVELOPE_MISMATCH",
                "engine action_type must match ZoneMove source_action_type.",
                event_index=event_index,
                field="action_type",
                envelope_value=event.get("action_type"),
                payload_value=payload.get("source_action_type"),
            )
        )

    card_instance_id = payload.get("card_instance_id")
    card_instance = card_instances.get(card_instance_id)
    if not isinstance(card_instance, dict):
        errors.append(
            _error(
                "ZONE_MOVE_INSTANCE_UNKNOWN",
                "ZoneMove payload must refer to a registry card instance.",
                event_index=event_index,
                card_instance_id=card_instance_id,
            )
        )
        return errors

    if payload.get("card_id") != card_instance.get("card_id"):
        errors.append(
            _error(
                "ZONE_MOVE_CARD_ID_MISMATCH",
                "ZoneMove card_id must match the registry card instance.",
                event_index=event_index,
                card_instance_id=card_instance_id,
                payload_card_id=payload.get("card_id"),
                registry_card_id=card_instance.get("card_id"),
            )
        )

    if payload.get("to_zone") != card_instance.get("zone"):
        errors.append(
            _error(
                "ZONE_MOVE_RESULT_ZONE_MISMATCH",
                "ZoneMove destination must match the current registry zone.",
                event_index=event_index,
                card_instance_id=card_instance_id,
                payload_to_zone=payload.get("to_zone"),
                registry_zone=card_instance.get("zone"),
            )
        )

    if payload.get("to_zone_index") != card_instance.get("zone_index"):
        errors.append(
            _error(
                "ZONE_MOVE_RESULT_INDEX_MISMATCH",
                "ZoneMove destination index must match the current registry zone index.",
                event_index=event_index,
                card_instance_id=card_instance_id,
                payload_to_zone_index=payload.get("to_zone_index"),
                registry_zone_index=card_instance.get("zone_index"),
            )
        )
    return errors


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _error(code, message, **details):
    error = {"code": code, "message": message}
    error.update(details)
    return error
