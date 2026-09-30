"""Isolated Domain occupancy contracts for future board-state work.

The helpers model empty or structurally occupied horizon/zenith slots. They do
not mutate topology, access MatchState, validate a card registry, or implement
gameplay transitions.
"""

from __future__ import annotations

from copy import deepcopy

try:
    from domain_position import (
        create_domain_position_id,
        validate_domain_position_reference,
        validate_player_domain_topology,
    )
except ModuleNotFoundError:
    from .domain_position import (
        create_domain_position_id,
        validate_domain_position_reference,
        validate_player_domain_topology,
    )


DOMAIN_POSITION_OCCUPANCY_SCHEMA_VERSION = "minimal-domain-position-occupancy-v0"
PLAYER_DOMAIN_OCCUPANCY_SCHEMA_VERSION = "minimal-player-domain-occupancy-v0"
DOMAIN_OCCUPANCY_MODEL = "single_card_instance_per_domain_position_v0"
SUPPORTED_OCCUPANCY_STATES = ("empty", "occupied")
SUPPORTED_DOMAIN_POSITION_TYPES = ("horizon", "zenith")

_TOPOLOGY_MODEL = "base_game_six_current_v0"
_REQUIRED_POSITION_FIELDS = (
    "schema_version",
    "contract_type",
    "position_id",
    "player_id",
    "current_index",
    "position_type",
    "row",
    "occupancy_state",
    "occupant_object_type",
    "occupant_card_instance_id",
    "visibility",
    "metadata",
)
_REQUIRED_PLAYER_FIELDS = (
    "schema_version",
    "contract_type",
    "player_id",
    "topology_schema_version",
    "topology_model",
    "occupancy_model",
    "slot_count",
    "slots",
    "metadata",
)
_FORBIDDEN_RUNTIME_OR_GAMEPLAY_FIELDS = {
    "card_id",
    "card_instance",
    "card_instances",
    "object_reference",
    "objects",
    "occupants",
    "match_state",
    "event",
    "events",
    "event_log",
    "action",
    "actions",
    "legal_action",
    "legal_actions",
    "gameplay_legality",
    "attackable",
    "attackability",
    "targetable",
    "targetability",
    "hp",
    "controller_id",
    "controller_player_id",
    "ability",
    "abilities",
    "seal_state",
}
_FORBIDDEN_CONTRACT_TYPES = {
    "card_instance_record",
    "object_reference",
    "match_state",
    "engine_event",
    "action_request",
    "action_response",
}


def create_empty_domain_position_occupancy(position_reference):
    """Create one empty occupancy slot from a canonical Domain position."""

    validation = validate_domain_position_reference(position_reference)
    if not validation.get("valid"):
        raise DomainOccupancyError(
            "Invalid Domain position reference: %s" % _first_error_code(validation)
        )
    position_type = position_reference.get("position_type")
    if position_type not in SUPPORTED_DOMAIN_POSITION_TYPES:
        raise DomainOccupancyError("Seal positions are not supported as Domain occupancy slots.")
    if position_reference.get("area") != "domain":
        raise DomainOccupancyError("Domain occupancy slots require area=domain.")

    return {
        "schema_version": DOMAIN_POSITION_OCCUPANCY_SCHEMA_VERSION,
        "contract_type": "domain_position_occupancy",
        "position_id": position_reference["position_id"],
        "player_id": position_reference["player_id"],
        "current_index": position_reference["current_index"],
        "position_type": position_type,
        "row": position_reference["row"],
        "occupancy_state": "empty",
        "occupant_object_type": None,
        "occupant_card_instance_id": None,
        "visibility": "public",
        "metadata": {
            "source": "python.engine.domain_occupancy",
            "occupancy_model": DOMAIN_OCCUPANCY_MODEL,
            "capacity": 1,
            "topology_model": _TOPOLOGY_MODEL,
            "mutation_api": "not_implemented",
            "gameplay_integration": "not_implemented",
            "seal_position_supported": False,
        },
    }


def validate_domain_position_occupancy(record):
    """Validate one slot record without consulting runtime card state."""

    errors = []
    normalized = record if isinstance(record, dict) else {}
    if not isinstance(record, dict):
        errors.append(_error("RECORD_NOT_DICT", "Domain position occupancy must be a dict."))

    for field_name in _REQUIRED_POSITION_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if normalized.get("schema_version") != DOMAIN_POSITION_OCCUPANCY_SCHEMA_VERSION:
        errors.append(
            _error(
                "SCHEMA_VERSION_INVALID",
                "schema_version must identify the minimal Domain occupancy contract.",
                actual=normalized.get("schema_version"),
            )
        )
    if normalized.get("contract_type") != "domain_position_occupancy":
        errors.append(
            _error(
                "CONTRACT_TYPE_INVALID",
                "contract_type must be domain_position_occupancy.",
                actual=normalized.get("contract_type"),
            )
        )
    for field_name in ("position_id", "player_id"):
        if not _is_non_empty_string(normalized.get(field_name)):
            errors.append(_error("FIELD_EMPTY", "field must be a non-empty string.", field=field_name))

    current_index = normalized.get("current_index")
    current_index_valid = _is_integer(current_index) and 1 <= current_index <= 6
    if not current_index_valid:
        errors.append(
            _error(
                "CURRENT_INDEX_INVALID",
                "current_index must be an integer from 1 through 6.",
                actual=current_index,
            )
        )

    position_type = normalized.get("position_type")
    position_type_valid = position_type in SUPPORTED_DOMAIN_POSITION_TYPES
    if position_type == "seal":
        errors.append(
            _error(
                "SEAL_POSITION_NOT_SUPPORTED",
                "seal positions are not card occupancy slots.",
            )
        )
    elif not position_type_valid:
        errors.append(
            _error(
                "POSITION_TYPE_INVALID",
                "position_type must be horizon or zenith.",
                actual=position_type,
            )
        )

    if position_type_valid and normalized.get("row") != position_type:
        errors.append(
            _error(
                "ROW_INVALID",
                "row must match the horizon or zenith position type.",
                expected=position_type,
                actual=normalized.get("row"),
            )
        )

    player_id = normalized.get("player_id")
    if _is_non_empty_string(player_id) and current_index_valid and position_type_valid:
        expected_position_id = create_domain_position_id(player_id, current_index, position_type)
        if normalized.get("position_id") != expected_position_id:
            errors.append(
                _error(
                    "POSITION_ID_MISMATCH",
                    "position_id must identify the canonical player/current/row position.",
                    expected=expected_position_id,
                )
            )

    occupancy_state = normalized.get("occupancy_state")
    if occupancy_state not in SUPPORTED_OCCUPANCY_STATES:
        errors.append(
            _error(
                "OCCUPANCY_STATE_INVALID",
                "occupancy_state must be empty or occupied.",
                actual=occupancy_state,
            )
        )

    occupant_object_type = normalized.get("occupant_object_type")
    occupant_card_instance_id = normalized.get("occupant_card_instance_id")
    if occupant_object_type not in (None, "card_instance"):
        errors.append(
            _error(
                "OCCUPANT_OBJECT_TYPE_INVALID",
                "occupant_object_type must be card_instance or null.",
                actual=occupant_object_type,
            )
        )
    if occupancy_state == "empty":
        if occupant_object_type is not None or occupant_card_instance_id is not None:
            errors.append(
                _error(
                    "EMPTY_OCCUPANCY_HAS_OCCUPANT",
                    "empty occupancy cannot carry occupant identity.",
                )
            )
    elif occupancy_state == "occupied":
        if occupant_object_type != "card_instance":
            errors.append(
                _error(
                    "OCCUPANT_OBJECT_TYPE_INVALID",
                    "occupied occupancy requires occupant_object_type=card_instance.",
                    actual=occupant_object_type,
                )
            )
        if not _is_non_empty_string(occupant_card_instance_id):
            errors.append(
                _error(
                    "OCCUPIED_OCCUPANCY_MISSING_OCCUPANT",
                    "occupied occupancy requires a non-empty card instance ID.",
                )
            )

    if normalized.get("visibility") != "public":
        errors.append(_error("VISIBILITY_INVALID", "Domain occupancy visibility must be public."))

    _validate_position_metadata(normalized.get("metadata"), errors)
    unexpected_paths = _find_unexpected_fields(normalized, "occupancy")
    if unexpected_paths:
        errors.append(
            _error(
                "UNEXPECTED_GAMEPLAY_FIELD",
                "occupancy contract contains runtime or gameplay data outside its scope.",
                fields=unexpected_paths,
            )
        )
    return {"valid": len(errors) == 0, "errors": errors}


def create_empty_player_domain_occupancy(topology):
    """Create twelve empty horizon/zenith slots from a valid topology."""

    validation = validate_player_domain_topology(topology)
    if not validation.get("valid"):
        raise DomainOccupancyError("Invalid player Domain topology: %s" % _first_error_code(validation))

    position_type_order = {
        position_type: index
        for index, position_type in enumerate(SUPPORTED_DOMAIN_POSITION_TYPES)
    }
    supported_positions = [
        position
        for position in topology["positions"]
        if position.get("position_type") in SUPPORTED_DOMAIN_POSITION_TYPES
        and position.get("area") == "domain"
    ]
    supported_positions.sort(
        key=lambda position: (
            position["current_index"],
            position_type_order[position["position_type"]],
        )
    )
    slots = [
        create_empty_domain_position_occupancy(position)
        for position in supported_positions
    ]
    return {
        "schema_version": PLAYER_DOMAIN_OCCUPANCY_SCHEMA_VERSION,
        "contract_type": "player_domain_occupancy",
        "player_id": topology["player_id"],
        "topology_schema_version": topology["schema_version"],
        "topology_model": _TOPOLOGY_MODEL,
        "occupancy_model": DOMAIN_OCCUPANCY_MODEL,
        "slot_count": len(slots),
        "slots": slots,
        "metadata": {
            "source": "python.engine.domain_occupancy",
            "static_topology_reference": True,
            "slot_capacity": 1,
            "seal_state_model": "not_implemented",
            "mutation_api": "not_implemented",
            "play_card_integration": "not_implemented",
            "match_state_integration": "not_implemented",
            "four_current_variant_active": False,
        },
    }


def validate_player_domain_occupancy(occupancy, topology):
    """Validate player occupancy against its canonical static topology."""

    errors = []
    normalized = occupancy if isinstance(occupancy, dict) else {}
    normalized_topology = topology if isinstance(topology, dict) else {}
    if not isinstance(occupancy, dict):
        errors.append(_error("OCCUPANCY_NOT_DICT", "player Domain occupancy must be a dict."))

    topology_validation = validate_player_domain_topology(topology)
    topology_valid = topology_validation.get("valid") is True
    if not topology_valid:
        errors.append(
            _error(
                "TOPOLOGY_INVALID",
                "topology must be a valid player_domain_topology contract.",
                topology_errors=topology_validation.get("errors", []),
            )
        )

    for field_name in _REQUIRED_PLAYER_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if normalized.get("schema_version") != PLAYER_DOMAIN_OCCUPANCY_SCHEMA_VERSION:
        errors.append(
            _error(
                "SCHEMA_VERSION_INVALID",
                "schema_version must identify the player Domain occupancy contract.",
                actual=normalized.get("schema_version"),
            )
        )
    if normalized.get("contract_type") != "player_domain_occupancy":
        errors.append(
            _error(
                "CONTRACT_TYPE_INVALID",
                "contract_type must be player_domain_occupancy.",
                actual=normalized.get("contract_type"),
            )
        )

    topology_player_id = normalized_topology.get("player_id")
    if normalized.get("player_id") != topology_player_id:
        errors.append(
            _error(
                "PLAYER_ID_MISMATCH",
                "occupancy player_id must match topology player_id.",
                occupancy_player_id=normalized.get("player_id"),
                topology_player_id=topology_player_id,
            )
        )
    if normalized.get("topology_schema_version") != normalized_topology.get("schema_version"):
        errors.append(
            _error(
                "TOPOLOGY_SCHEMA_MISMATCH",
                "topology_schema_version must match the supplied topology.",
            )
        )
    if normalized.get("topology_model") != _TOPOLOGY_MODEL:
        errors.append(_error("TOPOLOGY_MODEL_INVALID", "topology_model is not supported."))
    if normalized.get("occupancy_model") != DOMAIN_OCCUPANCY_MODEL:
        errors.append(_error("OCCUPANCY_MODEL_INVALID", "occupancy_model is not supported."))

    slot_count = normalized.get("slot_count")
    if not _is_integer(slot_count) or slot_count != 12:
        errors.append(_error("SLOT_COUNT_INVALID", "slot_count must be exactly 12."))
    slots = normalized.get("slots")
    if not isinstance(slots, list) or len(slots) != 12:
        errors.append(_error("SLOTS_INVALID", "slots must contain exactly twelve records."))
        slots = slots if isinstance(slots, list) else []

    _validate_player_metadata(normalized.get("metadata"), errors)

    expected_positions = {
        position.get("position_id"): position
        for position in normalized_topology.get("positions", []) or []
        if isinstance(position, dict)
        and position.get("position_type") in SUPPORTED_DOMAIN_POSITION_TYPES
        and position.get("area") == "domain"
        and _is_non_empty_string(position.get("position_id"))
    }
    seal_position_ids = {
        position.get("position_id")
        for position in normalized_topology.get("positions", []) or []
        if isinstance(position, dict)
        and position.get("position_type") == "seal"
        and _is_non_empty_string(position.get("position_id"))
    }

    position_ids = []
    occupied_instance_ids = []
    type_counts = {
        current_index: {position_type: 0 for position_type in SUPPORTED_DOMAIN_POSITION_TYPES}
        for current_index in range(1, 7)
    }
    for slot_index, slot in enumerate(slots):
        validation = validate_domain_position_occupancy(slot)
        if not validation.get("valid"):
            errors.append(
                _error(
                    "SLOT_RECORD_INVALID",
                    "slot failed the Domain position occupancy contract.",
                    slot_index=slot_index,
                    slot_errors=validation.get("errors", []),
                )
            )
        if not isinstance(slot, dict):
            continue

        position_id = slot.get("position_id")
        if _is_non_empty_string(position_id):
            position_ids.append(position_id)
            if position_id in seal_position_ids:
                errors.append(
                    _error(
                        "SEAL_SLOT_UNEXPECTED",
                        "seal positions cannot appear in Domain card occupancy.",
                        slot_index=slot_index,
                        position_id=position_id,
                    )
                )

        expected_position = (
            expected_positions.get(position_id) if _is_non_empty_string(position_id) else None
        )
        if slot.get("player_id") != topology_player_id:
            errors.append(
                _error(
                    "SLOT_PLAYER_MISMATCH",
                    "slot player_id must match topology player_id.",
                    slot_index=slot_index,
                )
            )
        if expected_position is not None:
            if slot.get("current_index") != expected_position.get("current_index"):
                errors.append(
                    _error(
                        "SLOT_CURRENT_MISMATCH",
                        "slot current_index must match its topology position.",
                        slot_index=slot_index,
                    )
                )
            if (
                slot.get("position_type") != expected_position.get("position_type")
                or slot.get("row") != expected_position.get("row")
            ):
                errors.append(
                    _error(
                        "SLOT_POSITION_TYPE_MISMATCH",
                        "slot row and position_type must match its topology position.",
                        slot_index=slot_index,
                    )
                )

        current_index = slot.get("current_index")
        position_type = slot.get("position_type")
        if (
            _is_integer(current_index)
            and current_index in type_counts
            and position_type in SUPPORTED_DOMAIN_POSITION_TYPES
        ):
            type_counts[current_index][position_type] += 1
        occupant_id = slot.get("occupant_card_instance_id")
        if slot.get("occupancy_state") == "occupied" and _is_non_empty_string(occupant_id):
            occupied_instance_ids.append(occupant_id)

    duplicate_position_ids = _duplicates(position_ids)
    if duplicate_position_ids:
        errors.append(
            _error(
                "POSITION_ID_DUPLICATE",
                "occupancy position IDs must be unique.",
                position_ids=duplicate_position_ids,
            )
        )
    actual_position_ids = set(position_ids)
    expected_position_ids = set(expected_positions)
    if actual_position_ids != expected_position_ids:
        errors.append(
            _error(
                "POSITION_SET_MISMATCH",
                "occupancy slots must exactly cover topology horizon/zenith positions.",
                missing_position_ids=sorted(expected_position_ids - actual_position_ids),
                extra_position_ids=sorted(actual_position_ids - expected_position_ids),
            )
        )
    if any(
        counts[position_type] != 1
        for counts in type_counts.values()
        for position_type in SUPPORTED_DOMAIN_POSITION_TYPES
    ):
        errors.append(
            _error(
                "POSITION_SET_MISMATCH",
                "each current must contain one horizon and one zenith occupancy slot.",
                current_type_counts=type_counts,
            )
        )

    duplicate_occupants = _duplicates(occupied_instance_ids)
    if duplicate_occupants:
        errors.append(
            _error(
                "OCCUPANT_INSTANCE_DUPLICATE",
                "one card instance cannot occupy multiple Domain positions.",
                card_instance_ids=duplicate_occupants,
            )
        )

    unexpected_paths = _find_unexpected_fields(normalized, "player_occupancy")
    if unexpected_paths:
        errors.append(
            _error(
                "UNEXPECTED_RUNTIME_STATE_FIELD",
                "player occupancy contains runtime or gameplay data outside its scope.",
                fields=unexpected_paths,
            )
        )
    return {"valid": len(errors) == 0, "errors": errors}


def get_domain_position_occupancy(occupancy, position_id):
    """Return a detached slot copy for one supported Domain position."""

    if not isinstance(occupancy, dict):
        raise DomainOccupancyError("player Domain occupancy must be a dict.")
    if not _is_non_empty_string(position_id):
        raise DomainOccupancyError("position_id must be a non-empty string.")
    for slot in occupancy.get("slots", []) or []:
        if isinstance(slot, dict) and slot.get("position_id") == position_id:
            return deepcopy(slot)
    raise DomainOccupancyError("Unknown or unsupported Domain occupancy position_id: %s" % position_id)


def _validate_position_metadata(metadata, errors):
    expected = {
        "source": "python.engine.domain_occupancy",
        "occupancy_model": DOMAIN_OCCUPANCY_MODEL,
        "capacity": 1,
        "topology_model": _TOPOLOGY_MODEL,
        "mutation_api": "not_implemented",
        "gameplay_integration": "not_implemented",
        "seal_position_supported": False,
    }
    _validate_metadata(metadata, expected, errors, "position")


def _validate_player_metadata(metadata, errors):
    expected = {
        "source": "python.engine.domain_occupancy",
        "static_topology_reference": True,
        "slot_capacity": 1,
        "seal_state_model": "not_implemented",
        "mutation_api": "not_implemented",
        "play_card_integration": "not_implemented",
        "match_state_integration": "not_implemented",
        "four_current_variant_active": False,
    }
    _validate_metadata(metadata, expected, errors, "player")


def _validate_metadata(metadata, expected, errors, scope):
    if not isinstance(metadata, dict):
        errors.append(_error("METADATA_INVALID", "%s metadata must be a dict." % scope))
        return
    for field_name, expected_value in expected.items():
        actual_value = metadata.get(field_name)
        if field_name in {"capacity", "slot_capacity"}:
            valid = _is_integer(actual_value) and actual_value == expected_value
        else:
            valid = actual_value == expected_value
        if not valid:
            errors.append(
                _error(
                    "METADATA_INVALID",
                    "%s metadata value is invalid." % scope,
                    field="metadata.%s" % field_name,
                    expected=expected_value,
                    actual=actual_value,
                )
            )


def _find_unexpected_fields(value, path):
    matches = []
    if isinstance(value, dict):
        for key, nested in value.items():
            nested_path = "%s.%s" % (path, key)
            if key in _FORBIDDEN_RUNTIME_OR_GAMEPLAY_FIELDS:
                matches.append(nested_path)
            if (
                key == "contract_type"
                and isinstance(nested, str)
                and nested in _FORBIDDEN_CONTRACT_TYPES
            ):
                matches.append(nested_path)
            matches.extend(_find_unexpected_fields(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            matches.extend(_find_unexpected_fields(nested, "%s[%s]" % (path, index)))
    return sorted(set(matches))


def _first_error_code(validation):
    errors = validation.get("errors") or []
    return errors[0].get("code", "unknown") if errors else "unknown"


def _duplicates(values):
    seen = set()
    duplicates = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def _is_non_empty_string(value):
    return isinstance(value, str) and value.strip() != ""


def _is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _error(code, message, **details):
    error = {"code": code, "message": message}
    error.update(details)
    return error


class DomainOccupancyError(ValueError):
    """Raised when an occupancy contract cannot be safely constructed or read."""


__all__ = [
    "DOMAIN_POSITION_OCCUPANCY_SCHEMA_VERSION",
    "PLAYER_DOMAIN_OCCUPANCY_SCHEMA_VERSION",
    "DOMAIN_OCCUPANCY_MODEL",
    "SUPPORTED_OCCUPANCY_STATES",
    "SUPPORTED_DOMAIN_POSITION_TYPES",
    "DomainOccupancyError",
    "create_empty_domain_position_occupancy",
    "validate_domain_position_occupancy",
    "create_empty_player_domain_occupancy",
    "validate_player_domain_occupancy",
    "get_domain_position_occupancy",
]
