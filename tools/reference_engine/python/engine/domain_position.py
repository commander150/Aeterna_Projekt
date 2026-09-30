"""Static Domain topology and position-reference contracts.

The helpers describe the base game's six-current combat-field structure. They
do not hold runtime occupancy, mutate MatchState, or implement gameplay rules.
"""

from __future__ import annotations


DOMAIN_POSITION_SCHEMA_VERSION = "minimal-domain-position-v0"
DOMAIN_TOPOLOGY_SCHEMA_VERSION = "minimal-player-domain-topology-v0"
ACTIVE_CURRENT_COUNT = 6
DOMAIN_POSITION_TYPES = ("horizon", "zenith", "seal")
DOMAIN_ROWS = ("horizon", "zenith")

_TOPOLOGY_MODEL = "base_game_six_current_v0"

_REQUIRED_POSITION_FIELDS = (
    "schema_version",
    "contract_type",
    "position_id",
    "player_id",
    "area",
    "current_index",
    "position_type",
    "row",
    "linked_current_id",
    "visibility",
    "metadata",
)

_REQUIRED_TOPOLOGY_FIELDS = (
    "schema_version",
    "contract_type",
    "player_id",
    "current_count",
    "row_count",
    "rows",
    "currents",
    "positions",
    "metadata",
)

_REQUIRED_CURRENT_FIELDS = (
    "current_id",
    "current_index",
    "horizon_position_id",
    "zenith_position_id",
    "seal_position_id",
    "metadata",
)

_FORBIDDEN_RUNTIME_FIELDS = {
    "card_instance_id",
    "card_id",
    "occupant",
    "occupancy",
    "objects",
    "controller",
    "controller_player_id",
    "attackable",
    "attackability",
    "targetable",
    "targetability",
    "seal_state",
    "hp",
    "face_up",
    "face_down",
    "gameplay_legality",
}


def create_domain_position_id(player_id, current_index, position_type):
    """Return a deterministic static position identifier."""

    _validate_position_identity_input(player_id, current_index, position_type)
    return "%s_%s" % (_create_current_id(player_id, current_index), position_type)


def create_domain_position_reference(player_id, current_index, position_type):
    """Create one JSON-compatible static Domain position reference."""

    position_id = create_domain_position_id(player_id, current_index, position_type)
    area = "seal_layer" if position_type == "seal" else "domain"
    row = None if position_type == "seal" else position_type
    return {
        "schema_version": DOMAIN_POSITION_SCHEMA_VERSION,
        "contract_type": "domain_position_reference",
        "position_id": position_id,
        "player_id": player_id,
        "area": area,
        "current_index": current_index,
        "position_type": position_type,
        "row": row,
        "linked_current_id": _create_current_id(player_id, current_index),
        "visibility": "public",
        "metadata": {
            "source": "python.engine.domain_position",
            "topology_model": _TOPOLOGY_MODEL,
            "current_count": ACTIVE_CURRENT_COUNT,
            "static_topology": True,
            "occupancy_model": "not_implemented",
        },
    }


def validate_domain_position_reference(record):
    """Validate one position reference without raising for normal bad input."""

    errors = []
    normalized = record if isinstance(record, dict) else {}
    if not isinstance(record, dict):
        errors.append(_error("RECORD_NOT_DICT", "domain position reference must be a dict."))

    for field_name in _REQUIRED_POSITION_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if normalized.get("schema_version") != DOMAIN_POSITION_SCHEMA_VERSION:
        errors.append(
            _error(
                "SCHEMA_VERSION_INVALID",
                "schema_version must identify the minimal Domain position contract.",
                actual=normalized.get("schema_version"),
            )
        )
    if normalized.get("contract_type") != "domain_position_reference":
        errors.append(
            _error(
                "CONTRACT_TYPE_INVALID",
                "contract_type must be domain_position_reference.",
                actual=normalized.get("contract_type"),
            )
        )
    for field_name in ("position_id", "player_id", "area", "position_type", "linked_current_id", "visibility"):
        if not _is_non_empty_string(normalized.get(field_name)):
            errors.append(_error("FIELD_EMPTY", "field must be a non-empty string.", field=field_name))

    current_index = normalized.get("current_index")
    current_index_valid = _is_integer(current_index) and 1 <= current_index <= ACTIVE_CURRENT_COUNT
    if not current_index_valid:
        errors.append(
            _error(
                "CURRENT_INDEX_INVALID",
                "current_index must be an integer from 1 through 6.",
                actual=current_index,
            )
        )

    position_type = normalized.get("position_type")
    position_type_valid = position_type in DOMAIN_POSITION_TYPES
    if not position_type_valid:
        errors.append(
            _error(
                "POSITION_TYPE_INVALID",
                "position_type must be horizon, zenith, or seal.",
                actual=position_type,
            )
        )

    if position_type_valid:
        expected_area = "seal_layer" if position_type == "seal" else "domain"
        expected_row = None if position_type == "seal" else position_type
        if normalized.get("area") != expected_area:
            errors.append(
                _error("AREA_INVALID", "area does not match position_type.", expected=expected_area)
            )
        if normalized.get("row") != expected_row:
            errors.append(_error("ROW_INVALID", "row does not match position_type.", expected=expected_row))

    player_id = normalized.get("player_id")
    identity_input_valid = _is_non_empty_string(player_id) and current_index_valid and position_type_valid
    if identity_input_valid:
        expected_position_id = create_domain_position_id(player_id, current_index, position_type)
        expected_current_id = _create_current_id(player_id, current_index)
        if normalized.get("position_id") != expected_position_id:
            errors.append(
                _error(
                    "POSITION_ID_MISMATCH",
                    "position_id must derive from player, current, and position type.",
                    expected=expected_position_id,
                )
            )
        if normalized.get("linked_current_id") != expected_current_id:
            errors.append(
                _error(
                    "LINKED_CURRENT_ID_MISMATCH",
                    "linked_current_id must derive from player and current.",
                    expected=expected_current_id,
                )
            )

    if normalized.get("visibility") != "public":
        errors.append(_error("VISIBILITY_INVALID", "Domain positions must be public."))

    metadata = normalized.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(_error("METADATA_INVALID", "metadata must be a dict."))
    else:
        expected_metadata = {
            "source": "python.engine.domain_position",
            "topology_model": _TOPOLOGY_MODEL,
            "current_count": ACTIVE_CURRENT_COUNT,
            "static_topology": True,
            "occupancy_model": "not_implemented",
        }
        for field_name, expected_value in expected_metadata.items():
            if metadata.get(field_name) != expected_value:
                errors.append(
                    _error(
                        "TOPOLOGY_MODEL_INVALID",
                        "position metadata does not match the static six-current model.",
                        field="metadata.%s" % field_name,
                        expected=expected_value,
                        actual=metadata.get(field_name),
                    )
                )

    forbidden = sorted(field_name for field_name in _FORBIDDEN_RUNTIME_FIELDS if field_name in normalized)
    if forbidden:
        errors.append(
            _error(
                "UNEXPECTED_RUNTIME_STATE_FIELD",
                "position reference cannot contain runtime state fields.",
                fields=forbidden,
            )
        )

    return {"valid": len(errors) == 0, "errors": errors}


def create_player_domain_topology(player_id):
    """Create the complete static six-current topology for one player."""

    if not _is_non_empty_string(player_id):
        raise DomainPositionError("player_id must be a non-empty string.")

    currents = []
    positions = []
    for current_index in range(1, ACTIVE_CURRENT_COUNT + 1):
        position_ids = {}
        for position_type in DOMAIN_POSITION_TYPES:
            position = create_domain_position_reference(player_id, current_index, position_type)
            positions.append(position)
            position_ids[position_type] = position["position_id"]
        currents.append(
            {
                "current_id": _create_current_id(player_id, current_index),
                "current_index": current_index,
                "horizon_position_id": position_ids["horizon"],
                "zenith_position_id": position_ids["zenith"],
                "seal_position_id": position_ids["seal"],
                "metadata": {
                    "positionally_linked_seal": True,
                    "ordered": True,
                },
            }
        )

    return {
        "schema_version": DOMAIN_TOPOLOGY_SCHEMA_VERSION,
        "contract_type": "player_domain_topology",
        "player_id": player_id,
        "current_count": ACTIVE_CURRENT_COUNT,
        "row_count": len(DOMAIN_ROWS),
        "rows": list(DOMAIN_ROWS),
        "currents": currents,
        "positions": positions,
        "metadata": {
            "source": "python.engine.domain_position",
            "topology_model": _TOPOLOGY_MODEL,
            "static_topology": True,
            "domain_scope": "combat_field_structure",
            "full_play_area_model": False,
            "occupancy_model": "not_implemented",
            "four_current_variant_active": False,
        },
    }


def validate_player_domain_topology(topology):
    """Validate the complete static topology without raising for bad input."""

    errors = []
    normalized = topology if isinstance(topology, dict) else {}
    if not isinstance(topology, dict):
        errors.append(_error("TOPOLOGY_NOT_DICT", "player Domain topology must be a dict."))

    for field_name in _REQUIRED_TOPOLOGY_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if normalized.get("schema_version") != DOMAIN_TOPOLOGY_SCHEMA_VERSION:
        errors.append(
            _error(
                "SCHEMA_VERSION_INVALID",
                "schema_version must identify the minimal player Domain topology.",
                actual=normalized.get("schema_version"),
            )
        )
    if normalized.get("contract_type") != "player_domain_topology":
        errors.append(
            _error(
                "CONTRACT_TYPE_INVALID",
                "contract_type must be player_domain_topology.",
                actual=normalized.get("contract_type"),
            )
        )

    player_id = normalized.get("player_id")
    if not _is_non_empty_string(player_id):
        errors.append(_error("PLAYER_ID_INVALID", "player_id must be a non-empty string."))
    if normalized.get("current_count") != ACTIVE_CURRENT_COUNT:
        errors.append(_error("CURRENT_COUNT_INVALID", "current_count must be 6."))
    if normalized.get("row_count") != len(DOMAIN_ROWS):
        errors.append(_error("ROW_COUNT_INVALID", "row_count must be 2."))
    if normalized.get("rows") != list(DOMAIN_ROWS):
        errors.append(_error("ROWS_INVALID", "rows must be horizon followed by zenith."))

    currents = normalized.get("currents")
    if not isinstance(currents, list) or len(currents) != ACTIVE_CURRENT_COUNT:
        errors.append(_error("CURRENTS_INVALID", "currents must contain exactly six records."))
        currents = currents if isinstance(currents, list) else []
    positions = normalized.get("positions")
    expected_position_count = ACTIVE_CURRENT_COUNT * len(DOMAIN_POSITION_TYPES)
    if not isinstance(positions, list) or len(positions) != expected_position_count:
        errors.append(_error("POSITIONS_INVALID", "positions must contain exactly 18 records."))
        positions = positions if isinstance(positions, list) else []

    _validate_topology_metadata(normalized.get("metadata"), errors)

    forbidden_paths = _find_forbidden_runtime_fields(normalized)
    if forbidden_paths:
        errors.append(
            _error(
                "UNEXPECTED_RUNTIME_STATE_FIELD",
                "topology cannot contain runtime state fields.",
                fields=forbidden_paths,
            )
        )

    position_by_id = {}
    position_ids = []
    position_counts = {
        current_index: {position_type: 0 for position_type in DOMAIN_POSITION_TYPES}
        for current_index in range(1, ACTIVE_CURRENT_COUNT + 1)
    }
    for position_index, position in enumerate(positions):
        validation = validate_domain_position_reference(position)
        if not validation.get("valid"):
            errors.append(
                _error(
                    "POSITION_RECORD_INVALID",
                    "position failed its contract validation.",
                    position_index=position_index,
                    position_errors=validation.get("errors", []),
                )
            )
        if not isinstance(position, dict):
            continue
        position_id = position.get("position_id")
        if _is_non_empty_string(position_id):
            position_ids.append(position_id)
            position_by_id.setdefault(position_id, position)
        if _is_non_empty_string(player_id) and position.get("player_id") != player_id:
            errors.append(
                _error(
                    "POSITION_PLAYER_MISMATCH",
                    "position player_id must match topology player_id.",
                    position_index=position_index,
                )
            )
        current_index = position.get("current_index")
        position_type = position.get("position_type")
        if current_index in position_counts and position_type in DOMAIN_POSITION_TYPES:
            position_counts[current_index][position_type] += 1

    duplicate_position_ids = _duplicates(position_ids)
    if duplicate_position_ids:
        errors.append(
            _error(
                "POSITION_ID_DUPLICATE",
                "position IDs must be unique.",
                position_ids=duplicate_position_ids,
            )
        )

    current_ids = []
    current_indexes = []
    referenced_position_ids = []
    for current_record_index, current in enumerate(currents):
        if not isinstance(current, dict):
            errors.append(
                _error(
                    "CURRENTS_INVALID",
                    "current record must be a dict.",
                    current_record_index=current_record_index,
                )
            )
            continue
        for field_name in _REQUIRED_CURRENT_FIELDS:
            if field_name not in current:
                errors.append(
                    _error(
                        "FIELD_MISSING",
                        "required current field is missing.",
                        current_record_index=current_record_index,
                        field=field_name,
                    )
                )

        current_index = current.get("current_index")
        current_id = current.get("current_id")
        if _is_integer(current_index):
            current_indexes.append(current_index)
        if _is_non_empty_string(current_id):
            current_ids.append(current_id)

        if _is_non_empty_string(player_id) and _is_integer(current_index):
            if 1 <= current_index <= ACTIVE_CURRENT_COUNT:
                expected_current_id = _create_current_id(player_id, current_index)
                if current_id != expected_current_id:
                    errors.append(
                        _error(
                            "CURRENT_POSITION_LINK_INVALID",
                            "current_id must derive from player and current index.",
                            current_record_index=current_record_index,
                            expected=expected_current_id,
                        )
                    )
                for position_type in DOMAIN_POSITION_TYPES:
                    field_name = "%s_position_id" % position_type
                    linked_position_id = current.get(field_name)
                    referenced_position_ids.append(linked_position_id)
                    expected_position_id = create_domain_position_id(player_id, current_index, position_type)
                    linked_position = position_by_id.get(linked_position_id)
                    if linked_position_id != expected_position_id or linked_position is None:
                        errors.append(
                            _error(
                                "CURRENT_POSITION_LINK_INVALID",
                                "current position link must reference its canonical position.",
                                current_record_index=current_record_index,
                                field=field_name,
                                expected=expected_position_id,
                            )
                        )
                    elif (
                        linked_position.get("current_index") != current_index
                        or linked_position.get("position_type") != position_type
                    ):
                        errors.append(
                            _error(
                                "POSITION_CURRENT_MISMATCH",
                                "linked position must match current index and position type.",
                                current_record_index=current_record_index,
                                field=field_name,
                            )
                        )

        current_metadata = current.get("metadata")
        if (
            not isinstance(current_metadata, dict)
            or current_metadata.get("positionally_linked_seal") is not True
            or current_metadata.get("ordered") is not True
        ):
            errors.append(
                _error(
                    "METADATA_INVALID",
                    "current metadata must declare ordered linked seals.",
                    current_record_index=current_record_index,
                )
            )

    if sorted(current_indexes) != list(range(1, ACTIVE_CURRENT_COUNT + 1)):
        errors.append(
            _error(
                "CURRENT_INDEX_SET_INVALID",
                "current indexes must be exactly 1 through 6.",
                actual=sorted(current_indexes),
            )
        )
    duplicate_current_ids = _duplicates(current_ids)
    if duplicate_current_ids:
        errors.append(
            _error(
                "CURRENT_ID_DUPLICATE",
                "current IDs must be unique.",
                current_ids=duplicate_current_ids,
            )
        )

    for current_index, type_counts in position_counts.items():
        if any(type_counts[position_type] != 1 for position_type in DOMAIN_POSITION_TYPES):
            errors.append(
                _error(
                    "POSITION_CURRENT_MISMATCH",
                    "each current must contain one horizon, zenith, and seal position.",
                    current_index=current_index,
                    counts=type_counts,
                )
            )

    if set(referenced_position_ids) != set(position_ids):
        errors.append(
            _error(
                "CURRENT_POSITION_LINK_INVALID",
                "current links must cover exactly the canonical position set.",
            )
        )

    return {"valid": len(errors) == 0, "errors": errors}


def _validate_position_identity_input(player_id, current_index, position_type):
    if not _is_non_empty_string(player_id):
        raise DomainPositionError("player_id must be a non-empty string.")
    if not _is_integer(current_index) or not 1 <= current_index <= ACTIVE_CURRENT_COUNT:
        raise DomainPositionError("current_index must be an integer from 1 through 6.")
    if position_type not in DOMAIN_POSITION_TYPES:
        raise DomainPositionError("position_type must be horizon, zenith, or seal.")


def _create_current_id(player_id, current_index):
    return "domain_%s_current_%02d" % (player_id, current_index)


def _validate_topology_metadata(metadata, errors):
    if not isinstance(metadata, dict):
        errors.append(_error("METADATA_INVALID", "topology metadata must be a dict."))
        return
    expected_metadata = {
        "source": "python.engine.domain_position",
        "topology_model": _TOPOLOGY_MODEL,
        "static_topology": True,
        "domain_scope": "combat_field_structure",
        "full_play_area_model": False,
        "occupancy_model": "not_implemented",
        "four_current_variant_active": False,
    }
    for field_name, expected_value in expected_metadata.items():
        if metadata.get(field_name) != expected_value:
            errors.append(
                _error(
                    "METADATA_INVALID",
                    "topology metadata value is invalid.",
                    field="metadata.%s" % field_name,
                    expected=expected_value,
                    actual=metadata.get(field_name),
                )
            )


def _find_forbidden_runtime_fields(value, path="topology"):
    matches = []
    if isinstance(value, dict):
        for key, nested in value.items():
            nested_path = "%s.%s" % (path, key)
            if key in _FORBIDDEN_RUNTIME_FIELDS:
                matches.append(nested_path)
            matches.extend(_find_forbidden_runtime_fields(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            matches.extend(_find_forbidden_runtime_fields(nested, "%s[%s]" % (path, index)))
    return matches


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


class DomainPositionError(ValueError):
    """Raised when a static Domain position cannot be constructed."""


__all__ = [
    "DOMAIN_POSITION_SCHEMA_VERSION",
    "DOMAIN_TOPOLOGY_SCHEMA_VERSION",
    "ACTIVE_CURRENT_COUNT",
    "DOMAIN_POSITION_TYPES",
    "DOMAIN_ROWS",
    "DomainPositionError",
    "create_domain_position_id",
    "create_domain_position_reference",
    "validate_domain_position_reference",
    "create_player_domain_topology",
    "validate_player_domain_topology",
]
