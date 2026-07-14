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

try:
    from turn_transition import validate_turn_transition_record
except ModuleNotFoundError:
    from engine.turn_transition import validate_turn_transition_record

try:
    from domain_position import validate_player_domain_topology
except ModuleNotFoundError:
    from engine.domain_position import validate_player_domain_topology

try:
    from domain_occupancy import validate_player_domain_occupancy
except ModuleNotFoundError:
    from engine.domain_occupancy import validate_player_domain_occupancy

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

    errors.extend(_validate_domain_topologies(state, player_ids))
    errors.extend(
        _validate_domain_occupancies(
            state,
            player_ids,
            normalized_registry,
            zone_occurrences,
        )
    )

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
            {
                "active_player_id": getattr(state, "active_player_id", None),
                "turn_number": getattr(state, "turn_number", None),
                "phase": getattr(state, "phase", None),
                "state_version": getattr(state, "state_version", None),
            },
        )
    )
    return errors


def _validate_domain_topologies(state, player_ids):
    errors = []
    if not hasattr(state, "domain_topologies"):
        return [
            _error(
                "DOMAIN_TOPOLOGIES_MISSING",
                "MatchState must contain a domain_topologies registry.",
            )
        ]

    topologies = getattr(state, "domain_topologies", None)
    if not isinstance(topologies, dict):
        return [
            _error(
                "DOMAIN_TOPOLOGIES_INVALID",
                "domain_topologies must be a dict keyed by player_id.",
                actual_type=type(topologies).__name__,
            )
        ]

    expected_player_ids = {player_id for player_id in player_ids if player_id}
    actual_player_ids = set(topologies)
    missing_player_ids = sorted(expected_player_ids - actual_player_ids, key=str)
    unexpected_player_ids = sorted(actual_player_ids - expected_player_ids, key=str)
    if missing_player_ids or unexpected_player_ids:
        errors.append(
            _error(
                "DOMAIN_TOPOLOGY_PLAYER_SET_MISMATCH",
                "domain_topologies keys must exactly match MatchState player IDs.",
                missing_player_ids=missing_player_ids,
                unexpected_player_ids=unexpected_player_ids,
            )
        )
    for player_id in missing_player_ids:
        errors.append(
            _error(
                "DOMAIN_TOPOLOGY_MISSING",
                "player is missing a Domain topology.",
                player_id=player_id,
            )
        )
    for player_id in unexpected_player_ids:
        errors.append(
            _error(
                "DOMAIN_TOPOLOGY_UNEXPECTED",
                "Domain topology does not belong to a MatchState player.",
                player_id=player_id,
            )
        )

    position_id_owners = {}
    current_id_owners = {}
    for player_id, topology in topologies.items():
        validation = validate_player_domain_topology(topology)
        topology_errors = list(validation.get("errors") or [])
        if not validation.get("valid"):
            errors.append(
                _error(
                    "DOMAIN_TOPOLOGY_RECORD_INVALID",
                    "player Domain topology failed contract validation.",
                    player_id=player_id,
                    topology_errors=topology_errors,
                )
            )
        if not isinstance(topology, dict):
            continue
        if topology.get("player_id") != player_id:
            errors.append(
                _error(
                    "DOMAIN_TOPOLOGY_PLAYER_MISMATCH",
                    "topology player_id must match its registry key.",
                    registry_player_id=player_id,
                    topology_player_id=topology.get("player_id"),
                )
            )

        runtime_leaks = [
            topology_error
            for topology_error in topology_errors
            if topology_error.get("code") == "UNEXPECTED_RUNTIME_STATE_FIELD"
        ]
        if runtime_leaks:
            errors.append(
                _error(
                    "DOMAIN_RUNTIME_STATE_LEAK",
                    "static Domain topology cannot contain runtime card or occupancy state.",
                    player_id=player_id,
                    topology_errors=runtime_leaks,
                )
            )

        for position in topology.get("positions", []) or []:
            if isinstance(position, dict) and _is_non_empty_string(position.get("position_id")):
                position_id_owners.setdefault(position["position_id"], []).append(player_id)
        for current in topology.get("currents", []) or []:
            if isinstance(current, dict) and _is_non_empty_string(current.get("current_id")):
                current_id_owners.setdefault(current["current_id"], []).append(player_id)

    position_collisions = _identifier_collisions(position_id_owners)
    if position_collisions:
        errors.append(
            _error(
                "DOMAIN_POSITION_ID_COLLISION",
                "Domain position IDs must be globally unique within MatchState.",
                collisions=position_collisions,
            )
        )
    current_collisions = _identifier_collisions(current_id_owners)
    if current_collisions:
        errors.append(
            _error(
                "DOMAIN_CURRENT_ID_COLLISION",
                "Domain current IDs must be globally unique within MatchState.",
                collisions=current_collisions,
            )
        )
    return errors


def _identifier_collisions(identifier_owners):
    return [
        {"identifier": identifier, "player_ids": list(player_ids)}
        for identifier, player_ids in sorted(identifier_owners.items(), key=lambda item: str(item[0]))
        if len(player_ids) > 1
    ]


def _validate_domain_occupancies(state, player_ids, card_instances, zone_occurrences):
    errors = []
    if not hasattr(state, "domain_occupancies"):
        return [
            _error(
                "DOMAIN_OCCUPANCIES_MISSING",
                "MatchState must contain a domain_occupancies registry.",
            )
        ]

    occupancies = getattr(state, "domain_occupancies", None)
    if not isinstance(occupancies, dict):
        return [
            _error(
                "DOMAIN_OCCUPANCIES_INVALID",
                "domain_occupancies must be a dict keyed by player_id.",
                actual_type=type(occupancies).__name__,
            )
        ]

    expected_player_ids = {player_id for player_id in player_ids if player_id}
    actual_player_ids = set(occupancies)
    missing_player_ids = sorted(expected_player_ids - actual_player_ids, key=str)
    unexpected_player_ids = sorted(actual_player_ids - expected_player_ids, key=str)
    if missing_player_ids or unexpected_player_ids:
        errors.append(
            _error(
                "DOMAIN_OCCUPANCY_PLAYER_SET_MISMATCH",
                "domain_occupancies keys must exactly match MatchState player IDs.",
                missing_player_ids=missing_player_ids,
                unexpected_player_ids=unexpected_player_ids,
            )
        )
    for player_id in missing_player_ids:
        errors.append(
            _error(
                "DOMAIN_OCCUPANCY_MISSING",
                "player is missing a Domain occupancy state.",
                player_id=player_id,
            )
        )
    for player_id in unexpected_player_ids:
        errors.append(
            _error(
                "DOMAIN_OCCUPANCY_UNEXPECTED",
                "Domain occupancy state does not belong to a MatchState player.",
                player_id=player_id,
            )
        )

    topologies = getattr(state, "domain_topologies", None)
    normalized_topologies = topologies if isinstance(topologies, dict) else {}
    domain_occurrences = {}
    topology_relation_error_codes = {
        "TOPOLOGY_INVALID",
        "PLAYER_ID_MISMATCH",
        "TOPOLOGY_SCHEMA_MISMATCH",
        "TOPOLOGY_MODEL_INVALID",
        "POSITION_SET_MISMATCH",
        "SEAL_SLOT_UNEXPECTED",
        "SLOT_PLAYER_MISMATCH",
        "SLOT_CURRENT_MISMATCH",
        "SLOT_POSITION_TYPE_MISMATCH",
    }

    for player_id, occupancy in occupancies.items():
        topology = normalized_topologies.get(player_id)
        validation = validate_player_domain_occupancy(occupancy, topology)
        occupancy_errors = list(validation.get("errors") or [])
        if not validation.get("valid"):
            errors.append(
                _error(
                    "DOMAIN_OCCUPANCY_RECORD_INVALID",
                    "player Domain occupancy failed contract validation.",
                    player_id=player_id,
                    occupancy_errors=occupancy_errors,
                )
            )
        if any(
            occupancy_error.get("code") in topology_relation_error_codes
            for occupancy_error in occupancy_errors
        ):
            errors.append(
                _error(
                    "DOMAIN_OCCUPANCY_TOPOLOGY_MISMATCH",
                    "Domain occupancy does not match its player topology.",
                    player_id=player_id,
                    occupancy_errors=occupancy_errors,
                )
            )

        if not isinstance(occupancy, dict):
            continue
        if occupancy.get("player_id") != player_id:
            errors.append(
                _error(
                    "DOMAIN_OCCUPANCY_PLAYER_MISMATCH",
                    "occupancy player_id must match its registry key.",
                    registry_player_id=player_id,
                    occupancy_player_id=occupancy.get("player_id"),
                )
            )

        topology_position_records = topology.get("positions") if isinstance(topology, dict) else []
        if not isinstance(topology_position_records, list):
            topology_position_records = []
        topology_positions = {
            position.get("position_id"): position
            for position in topology_position_records
            if isinstance(position, dict) and _is_non_empty_string(position.get("position_id"))
        }
        occupancy_slots = occupancy.get("slots")
        if not isinstance(occupancy_slots, list):
            occupancy_slots = []
        for slot_index, slot in enumerate(occupancy_slots):
            if not isinstance(slot, dict) or slot.get("occupancy_state") != "occupied":
                continue

            position_id = slot.get("position_id")
            position = topology_positions.get(position_id)
            is_seal_position = slot.get("position_type") == "seal" or (
                isinstance(position, dict) and position.get("position_type") == "seal"
            )
            if is_seal_position:
                errors.append(
                    _error(
                        "DOMAIN_OCCUPANT_SEAL_POSITION_INVALID",
                        "seal positions cannot contain Domain card occupants.",
                        player_id=player_id,
                        slot_index=slot_index,
                        position_id=position_id,
                    )
                )
            elif not (
                isinstance(position, dict)
                and position.get("area") == "domain"
                and position.get("position_type") in {"horizon", "zenith"}
            ):
                errors.append(
                    _error(
                        "DOMAIN_OCCUPANT_POSITION_INVALID",
                        "occupied slot must identify a horizon or zenith topology position.",
                        player_id=player_id,
                        slot_index=slot_index,
                        position_id=position_id,
                    )
                )

            card_instance_id = slot.get("occupant_card_instance_id")
            if not _is_non_empty_string(card_instance_id):
                continue
            occurrence = {
                "player_id": player_id,
                "zone": "domain",
                "zone_index": None,
                "position_id": position_id,
            }
            zone_occurrences.setdefault(card_instance_id, []).append(occurrence)
            domain_occurrences.setdefault(card_instance_id, []).append(occurrence)

            card_instance = card_instances.get(card_instance_id)
            if not isinstance(card_instance, dict):
                errors.append(
                    _error(
                        "DOMAIN_OCCUPANT_INSTANCE_UNKNOWN",
                        "occupied Domain slot must refer to a registry card instance.",
                        player_id=player_id,
                        position_id=position_id,
                        card_instance_id=card_instance_id,
                    )
                )
                continue
            if card_instance.get("zone") != "domain":
                errors.append(
                    _error(
                        "DOMAIN_OCCUPANT_ZONE_MISMATCH",
                        "occupied Domain instance must have registry zone=domain.",
                        player_id=player_id,
                        position_id=position_id,
                        card_instance_id=card_instance_id,
                        actual_zone=card_instance.get("zone"),
                    )
                )
            if card_instance.get("zone_index") is not None:
                errors.append(
                    _error(
                        "DOMAIN_OCCUPANT_ZONE_INDEX_INVALID",
                        "Domain card instance zone_index must be null.",
                        player_id=player_id,
                        position_id=position_id,
                        card_instance_id=card_instance_id,
                        actual_zone_index=card_instance.get("zone_index"),
                    )
                )
            if card_instance.get("visibility") != "public":
                errors.append(
                    _error(
                        "DOMAIN_OCCUPANT_VISIBILITY_INVALID",
                        "Domain card instance visibility must be public.",
                        player_id=player_id,
                        position_id=position_id,
                        card_instance_id=card_instance_id,
                        actual_visibility=card_instance.get("visibility"),
                    )
                )

            controller_player_id = card_instance.get("controller_player_id")
            if controller_player_id not in expected_player_ids:
                errors.append(
                    _error(
                        "DOMAIN_OCCUPANT_CONTROLLER_UNKNOWN",
                        "Domain card instance controller must be a MatchState player.",
                        player_id=player_id,
                        position_id=position_id,
                        card_instance_id=card_instance_id,
                        controller_player_id=controller_player_id,
                    )
                )
            elif controller_player_id != player_id:
                errors.append(
                    _error(
                        "DOMAIN_OCCUPANT_CONTROLLER_MISMATCH",
                        "Domain card instance controller must match the occupancy player.",
                        player_id=player_id,
                        position_id=position_id,
                        card_instance_id=card_instance_id,
                        controller_player_id=controller_player_id,
                    )
                )

    for card_instance_id, occurrences in domain_occurrences.items():
        if len(occurrences) > 1:
            errors.append(
                _error(
                    "DOMAIN_OCCUPANT_INSTANCE_DUPLICATE",
                    "card instance can occupy only one Domain slot globally.",
                    card_instance_id=card_instance_id,
                    occurrences=occurrences,
                )
            )

    for registry_key, card_instance in card_instances.items():
        if isinstance(card_instance, dict) and card_instance.get("zone") == "domain":
            if not domain_occurrences.get(registry_key):
                errors.append(
                    _error(
                        "DOMAIN_CARD_INSTANCE_UNBOUND",
                        "Domain-zoned registry card instance must occupy exactly one Domain slot.",
                        card_instance_id=registry_key,
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
                    "card_instance_id must occur in exactly one authoritative zone.",
                    card_instance_id=card_instance_id,
                    occurrences=occurrences,
                )
            )

    for card_instance_id in card_instances:
        if not zone_occurrences.get(card_instance_id):
            errors.append(
                _error(
                    "CARD_INSTANCE_ORPHANED",
                    "registry card instance must occur in exactly one authoritative zone.",
                    card_instance_id=card_instance_id,
                )
            )
    return errors


def _validate_event_log(event_log, player_ids, card_instances, current_state):
    errors = []
    events = list(event_log or [])
    turn_transition_indexes = [
        index for index, event in enumerate(events) if _event_has_type(event, "turn_transition")
    ]
    latest_turn_transition_index = turn_transition_indexes[-1] if turn_transition_indexes else None

    for index, event in enumerate(events):
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
        payload_event_type = payload.get("event_type") if isinstance(payload, dict) else None
        is_engine_event = event.get("contract_type") == "engine_event" or event.get("event_type") in {
            "zone_move",
            "turn_transition",
        } or payload_event_type in {"zone_move", "turn_transition"}
        is_zone_move = event.get("event_type") == "zone_move" or (
            payload_event_type == "zone_move"
        )
        is_turn_transition = event.get("event_type") == "turn_transition" or (
            payload_event_type == "turn_transition"
        )
        if is_engine_event:
            errors.extend(_validate_engine_event_contract(event, index))
        if is_zone_move:
            errors.extend(_validate_zone_move_engine_event(event, index, card_instances))
        if is_turn_transition:
            errors.extend(
                _validate_turn_transition_engine_event(
                    event,
                    index,
                    player_ids,
                    current_state,
                    is_latest_transition=index == latest_turn_transition_index,
                    is_latest_event=index == len(events) - 1,
                )
            )
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


def _validate_turn_transition_engine_event(
    event,
    event_index,
    player_ids,
    current_state,
    is_latest_transition,
    is_latest_event,
):
    errors = []
    payload = event.get("payload")
    if not isinstance(payload, dict):
        errors.append(
            _error(
                "TURN_TRANSITION_PAYLOAD_INVALID",
                "TurnTransition engine event payload must be a typed record dict.",
                event_index=event_index,
                actual_type=type(payload).__name__,
            )
        )
        return errors

    payload_validation = validate_turn_transition_record(payload)
    if not payload_validation.get("valid"):
        errors.append(
            _error(
                "TURN_TRANSITION_PAYLOAD_INVALID",
                "TurnTransition engine event payload failed contract validation.",
                event_index=event_index,
                payload_errors=payload_validation.get("errors", []),
            )
        )

    envelope_pairs = (
        ("event_sequence", "event_sequence"),
        ("state_version", "state_version"),
        ("event_type", "event_type"),
        ("action_type", "source_action_type"),
        ("player_id", "previous_active_player_id"),
        ("turn_number", "turn_number_after"),
    )
    for envelope_field, payload_field in envelope_pairs:
        if event.get(envelope_field) != payload.get(payload_field):
            errors.append(
                _error(
                    "TURN_TRANSITION_ENVELOPE_MISMATCH",
                    "TurnTransition envelope field must match its payload.",
                    event_index=event_index,
                    envelope_field=envelope_field,
                    payload_field=payload_field,
                    envelope_value=event.get(envelope_field),
                    payload_value=payload.get(payload_field),
                )
            )

    for forbidden_field in ("previous_player_id", "next_player_id"):
        if forbidden_field in event:
            errors.append(
                _error(
                    "TURN_TRANSITION_ENVELOPE_MISMATCH",
                    "TurnTransition details must remain inside the typed payload.",
                    event_index=event_index,
                    forbidden_field=forbidden_field,
                )
            )

    transition_player_fields = (
        "previous_active_player_id",
        "next_active_player_id",
        "previous_priority_player_id",
        "next_priority_player_id",
    )
    for field_name in transition_player_fields:
        player_id = payload.get(field_name)
        if not isinstance(player_id, str) or player_id not in player_ids:
            errors.append(
                _error(
                    "TURN_TRANSITION_PLAYER_UNKNOWN",
                    "TurnTransition player must exist in MatchState.",
                    event_index=event_index,
                    field=field_name,
                    player_id=player_id,
                )
            )

    previous_player_id = payload.get("previous_active_player_id")
    next_player_id = payload.get("next_active_player_id")
    if previous_player_id == next_player_id or (previous_player_id, next_player_id) not in {
        ("P1", "P2"),
        ("P2", "P1"),
    }:
        errors.append(
            _error(
                "TURN_TRANSITION_ACTIVE_PLAYER_INVALID",
                "minimal turn transition must alternate P1 and P2.",
                event_index=event_index,
                previous_active_player_id=previous_player_id,
                next_active_player_id=next_player_id,
            )
        )

    if (
        payload.get("previous_priority_player_id") != previous_player_id
        or payload.get("next_priority_player_id") != next_player_id
    ):
        errors.append(
            _error(
                "TURN_TRANSITION_PRIORITY_INVALID",
                "minimal priority player must follow the active player transition.",
                event_index=event_index,
                previous_priority_player_id=payload.get("previous_priority_player_id"),
                next_priority_player_id=payload.get("next_priority_player_id"),
            )
        )

    turn_number_before = payload.get("turn_number_before")
    turn_number_after = payload.get("turn_number_after")
    expected_turn_number_after = None
    if _is_integer(turn_number_before):
        if (previous_player_id, next_player_id) == ("P1", "P2"):
            expected_turn_number_after = turn_number_before
        elif (previous_player_id, next_player_id) == ("P2", "P1"):
            expected_turn_number_after = turn_number_before + 1
    if expected_turn_number_after is None or turn_number_after != expected_turn_number_after:
        errors.append(
            _error(
                "TURN_TRANSITION_TURN_NUMBER_INVALID",
                "turn number must follow the minimal P1/P2 transition rule.",
                event_index=event_index,
                turn_number_before=turn_number_before,
                turn_number_after=turn_number_after,
                expected_turn_number_after=expected_turn_number_after,
            )
        )

    if payload.get("phase_before") != "main" or payload.get("phase_after") != "main":
        errors.append(
            _error(
                "TURN_TRANSITION_PHASE_INVALID",
                "minimal turn transition phases must remain main.",
                event_index=event_index,
                phase_before=payload.get("phase_before"),
                phase_after=payload.get("phase_after"),
            )
        )

    if is_latest_transition:
        mismatches = []
        result_pairs = (
            ("active_player_id", payload.get("next_active_player_id")),
            ("turn_number", payload.get("turn_number_after")),
            ("phase", payload.get("phase_after")),
        )
        if is_latest_event:
            result_pairs += (("state_version", payload.get("state_version")),)
        for state_field, payload_value in result_pairs:
            if current_state.get(state_field) != payload_value:
                mismatches.append(
                    {
                        "field": state_field,
                        "state_value": current_state.get(state_field),
                        "payload_value": payload_value,
                    }
                )
        if mismatches:
            errors.append(
                _error(
                    "TURN_TRANSITION_RESULT_STATE_MISMATCH",
                    "latest TurnTransition result must match the current MatchState.",
                    event_index=event_index,
                    mismatches=mismatches,
                )
            )
    return errors


def _event_has_type(event, event_type):
    if not isinstance(event, dict):
        return False
    if event.get("event_type") == event_type:
        return True
    payload = event.get("payload")
    return isinstance(payload, dict) and payload.get("event_type") == event_type


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _is_non_empty_string(value):
    return isinstance(value, str) and value.strip() != ""


def _error(code, message, **details):
    error = {"code": code, "message": message}
    error.update(details)
    return error
