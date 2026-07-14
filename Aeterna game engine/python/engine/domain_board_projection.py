"""Public Domain board projection for the minimal player snapshot.

This module only projects validated static topology, occupancy, and card
instance state. It does not mutate MatchState or implement board gameplay.
"""

from __future__ import annotations

from copy import deepcopy

try:
    from card_instance import (
        OBJECT_REFERENCE_SCHEMA_VERSION,
        card_instance_to_object_reference,
    )
    from domain_occupancy import DOMAIN_OCCUPANCY_MODEL
except ModuleNotFoundError:
    from .card_instance import (
        OBJECT_REFERENCE_SCHEMA_VERSION,
        card_instance_to_object_reference,
    )
    from .domain_occupancy import DOMAIN_OCCUPANCY_MODEL

try:
    from state_invariants import validate_state_invariants
except ModuleNotFoundError:
    from tools.ai_vs_ai.state_invariants import validate_state_invariants


PLAYER_VISIBLE_DOMAIN_BOARD_SCHEMA_VERSION = "minimal-player-visible-domain-board-v0"
DOMAIN_BOARD_MODEL = "minimal-public-domain-board-v0"

_CURRENT_COUNT = 6
_DOMAIN_SLOT_COUNT = 12
_TOPOLOGY_MODEL = "base_game_six_current_v0"
_SOURCE = "python.engine.domain_board_projection"

_REQUIRED_BOARD_FIELDS = (
    "schema_version",
    "contract_type",
    "board_model",
    "visibility_mode",
    "current_count",
    "players",
    "metadata",
)
_REQUIRED_PLAYER_FIELDS = (
    "player_id",
    "current_count",
    "occupied_slot_count",
    "empty_slot_count",
    "currents",
    "metadata",
)
_REQUIRED_CURRENT_FIELDS = (
    "current_id",
    "current_index",
    "horizon",
    "zenith",
    "seal_position",
    "metadata",
)
_REQUIRED_SLOT_FIELDS = (
    "position_id",
    "player_id",
    "current_index",
    "position_type",
    "row",
    "occupancy_state",
    "occupied",
    "occupant",
    "visibility",
    "metadata",
)
_REQUIRED_SEAL_FIELDS = (
    "position_id",
    "player_id",
    "current_index",
    "position_type",
    "visibility",
    "state_model",
)
_SEAL_FORBIDDEN_FIELDS = {
    "occupancy_state",
    "occupied",
    "occupant",
    "occupant_card_instance_id",
    "card_instance_id",
    "object_reference",
    "hp",
    "broken",
    "targetable",
    "targetability",
}


def create_player_visible_domain_board(state):
    """Build a detached public board projection from a valid MatchState."""

    state_errors = validate_state_invariants(state)
    if state_errors:
        raise DomainBoardProjectionError(
            "Cannot project a player-visible Domain board from invalid state.",
            errors=state_errors,
        )

    players = sorted(state.players, key=lambda player: str(player.player_id))
    board = {
        "schema_version": PLAYER_VISIBLE_DOMAIN_BOARD_SCHEMA_VERSION,
        "contract_type": "player_visible_domain_board",
        "board_model": DOMAIN_BOARD_MODEL,
        "visibility_mode": "public",
        "current_count": _CURRENT_COUNT,
        "players": [_project_player_domain(state, player.player_id) for player in players],
        "metadata": {
            "source": _SOURCE,
            "topology_model": _TOPOLOGY_MODEL,
            "occupancy_model": DOMAIN_OCCUPANCY_MODEL,
            "object_reference_model": OBJECT_REFERENCE_SCHEMA_VERSION,
            "seal_state_model": "not_implemented",
            "gameplay_mutation_model": "not_implemented",
            "public_information_only": True,
        },
    }
    validation = validate_player_visible_domain_board(board)
    if not validation.get("valid"):
        raise DomainBoardProjectionError(
            "Generated player-visible Domain board failed contract validation.",
            errors=validation.get("errors", []),
        )
    return deepcopy(board)


def validate_player_visible_domain_board(board):
    """Return structured diagnostics without raising for normal bad input."""

    errors = []
    normalized = board if isinstance(board, dict) else {}
    if not isinstance(board, dict):
        errors.append(_error("BOARD_NOT_DICT", "player-visible Domain board must be a dict."))

    for field_name in _REQUIRED_BOARD_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required board field is missing.", field=field_name))

    if normalized.get("schema_version") != PLAYER_VISIBLE_DOMAIN_BOARD_SCHEMA_VERSION:
        errors.append(
            _error(
                "SCHEMA_VERSION_INVALID",
                "schema_version must identify the player-visible Domain board contract.",
                actual=normalized.get("schema_version"),
            )
        )
    if normalized.get("contract_type") != "player_visible_domain_board":
        errors.append(_error("CONTRACT_TYPE_INVALID", "contract_type is invalid."))
    if normalized.get("board_model") != DOMAIN_BOARD_MODEL:
        errors.append(_error("BOARD_MODEL_INVALID", "board_model is invalid."))
    if normalized.get("visibility_mode") != "public":
        errors.append(_error("VISIBILITY_INVALID", "board visibility must be public."))
    if normalized.get("current_count") != _CURRENT_COUNT:
        errors.append(_error("CURRENT_COUNT_INVALID", "board current_count must be 6."))
    _validate_board_metadata(normalized.get("metadata"), errors)

    players = normalized.get("players")
    if not isinstance(players, list) or len(players) != 2:
        errors.append(_error("PLAYERS_INVALID", "players must contain exactly two projections."))
        players = players if isinstance(players, list) else []

    player_ids = []
    current_ids = set()
    position_ids = set()
    occupant_instance_ids = set()
    for player_index, player in enumerate(players):
        _validate_player_projection(
            player,
            player_index,
            player_ids,
            current_ids,
            position_ids,
            occupant_instance_ids,
            errors,
        )

    duplicates = _duplicates(player_ids)
    if duplicates:
        errors.append(
            _error("PLAYER_ID_DUPLICATE", "board player IDs must be unique.", player_ids=duplicates)
        )

    return {"valid": len(errors) == 0, "errors": errors}


def _project_player_domain(state, player_id):
    topology = state.domain_topologies[player_id]
    occupancy = state.domain_occupancies[player_id]
    positions_by_id = {position["position_id"]: position for position in topology["positions"]}
    slots_by_position_id = {slot["position_id"]: slot for slot in occupancy["slots"]}
    currents = []
    occupied_slot_count = 0

    for current in sorted(topology["currents"], key=lambda record: record["current_index"]):
        horizon = _project_slot(
            state,
            slots_by_position_id[current["horizon_position_id"]],
        )
        zenith = _project_slot(
            state,
            slots_by_position_id[current["zenith_position_id"]],
        )
        occupied_slot_count += int(horizon["occupied"]) + int(zenith["occupied"])
        seal = positions_by_id[current["seal_position_id"]]
        currents.append(
            {
                "current_id": current["current_id"],
                "current_index": current["current_index"],
                "horizon": horizon,
                "zenith": zenith,
                "seal_position": {
                    "position_id": seal["position_id"],
                    "player_id": seal["player_id"],
                    "current_index": seal["current_index"],
                    "position_type": "seal",
                    "visibility": "public",
                    "state_model": "not_implemented",
                },
                "metadata": {
                    "ordered": True,
                    "positionally_linked_seal": True,
                },
            }
        )

    return {
        "player_id": player_id,
        "current_count": _CURRENT_COUNT,
        "occupied_slot_count": occupied_slot_count,
        "empty_slot_count": _DOMAIN_SLOT_COUNT - occupied_slot_count,
        "currents": currents,
        "metadata": {
            "visibility": "public",
            "domain_slot_count": _DOMAIN_SLOT_COUNT,
            "seal_position_count": _CURRENT_COUNT,
        },
    }


def _project_slot(state, slot):
    occupied = slot["occupancy_state"] == "occupied"
    occupant = None
    if occupied:
        record = state.card_instances[slot["occupant_card_instance_id"]]
        occupant = card_instance_to_object_reference(record)
    return {
        "position_id": slot["position_id"],
        "player_id": slot["player_id"],
        "current_index": slot["current_index"],
        "position_type": slot["position_type"],
        "row": slot["row"],
        "occupancy_state": slot["occupancy_state"],
        "occupied": occupied,
        "occupant": deepcopy(occupant),
        "visibility": "public",
        "metadata": {
            "source": _SOURCE,
            "capacity": 1,
            "occupancy_model": DOMAIN_OCCUPANCY_MODEL,
        },
    }


def _validate_player_projection(
    player,
    player_index,
    player_ids,
    current_ids,
    position_ids,
    occupant_instance_ids,
    errors,
):
    if not isinstance(player, dict):
        errors.append(
            _error("PLAYERS_INVALID", "player projection must be a dict.", player_index=player_index)
        )
        return
    for field_name in _REQUIRED_PLAYER_FIELDS:
        if field_name not in player:
            errors.append(
                _error(
                    "FIELD_MISSING",
                    "required player field is missing.",
                    player_index=player_index,
                    field=field_name,
                )
            )

    player_id = player.get("player_id")
    if not _is_non_empty_string(player_id):
        errors.append(_error("PLAYERS_INVALID", "player_id must be non-empty.", player_index=player_index))
    else:
        player_ids.append(player_id)
    if player.get("current_count") != _CURRENT_COUNT:
        errors.append(
            _error("CURRENT_COUNT_INVALID", "player current_count must be 6.", player_index=player_index)
        )

    occupied_count = player.get("occupied_slot_count")
    empty_count = player.get("empty_slot_count")
    if not _is_non_negative_integer(occupied_count) or not _is_non_negative_integer(empty_count):
        errors.append(
            _error(
                "SLOT_PROJECTION_INVALID",
                "occupied and empty slot counts must be non-negative integers.",
                player_index=player_index,
            )
        )
    elif occupied_count + empty_count != _DOMAIN_SLOT_COUNT:
        errors.append(
            _error(
                "SLOT_OCCUPANCY_MISMATCH",
                "occupied and empty slot counts must total 12.",
                player_index=player_index,
            )
        )

    metadata = player.get("metadata")
    if (
        not isinstance(metadata, dict)
        or metadata.get("visibility") != "public"
        or metadata.get("domain_slot_count") != _DOMAIN_SLOT_COUNT
        or metadata.get("seal_position_count") != _CURRENT_COUNT
    ):
        errors.append(_error("METADATA_INVALID", "player board metadata is invalid.", player_index=player_index))

    currents = player.get("currents")
    if not isinstance(currents, list) or len(currents) != _CURRENT_COUNT:
        errors.append(
            _error("CURRENT_COUNT_INVALID", "currents must contain exactly six records.", player_index=player_index)
        )
        currents = currents if isinstance(currents, list) else []

    current_indexes = []
    actual_occupied_count = 0
    for current_record_index, current in enumerate(currents):
        occupied_in_current = _validate_current_projection(
            current,
            player_id,
            player_index,
            current_record_index,
            current_ids,
            position_ids,
            occupant_instance_ids,
            errors,
        )
        if isinstance(current, dict) and _is_integer(current.get("current_index")):
            current_indexes.append(current["current_index"])
        actual_occupied_count += occupied_in_current

    if sorted(current_indexes) != list(range(1, _CURRENT_COUNT + 1)):
        errors.append(
            _error(
                "CURRENT_INDEX_SET_INVALID",
                "current indexes must be exactly 1 through 6.",
                player_index=player_index,
                actual=sorted(current_indexes),
            )
        )
    if _is_non_negative_integer(occupied_count) and occupied_count != actual_occupied_count:
        errors.append(
            _error(
                "SLOT_OCCUPANCY_MISMATCH",
                "occupied_slot_count must match projected slots.",
                player_index=player_index,
                expected=actual_occupied_count,
                actual=occupied_count,
            )
        )
    expected_empty_count = _DOMAIN_SLOT_COUNT - actual_occupied_count
    if _is_non_negative_integer(empty_count) and empty_count != expected_empty_count:
        errors.append(
            _error(
                "SLOT_OCCUPANCY_MISMATCH",
                "empty_slot_count must match projected slots.",
                player_index=player_index,
                expected=expected_empty_count,
                actual=empty_count,
            )
        )


def _validate_current_projection(
    current,
    player_id,
    player_index,
    current_record_index,
    current_ids,
    position_ids,
    occupant_instance_ids,
    errors,
):
    if not isinstance(current, dict):
        errors.append(
            _error(
                "CURRENT_COUNT_INVALID",
                "current projection must be a dict.",
                player_index=player_index,
                current_record_index=current_record_index,
            )
        )
        return 0
    for field_name in _REQUIRED_CURRENT_FIELDS:
        if field_name not in current:
            errors.append(
                _error(
                    "FIELD_MISSING",
                    "required current field is missing.",
                    player_index=player_index,
                    current_record_index=current_record_index,
                    field=field_name,
                )
            )

    current_index = current.get("current_index")
    current_id = current.get("current_id")
    if not _is_integer(current_index) or not 1 <= current_index <= _CURRENT_COUNT:
        errors.append(
            _error(
                "CURRENT_INDEX_SET_INVALID",
                "current_index must be an integer from 1 through 6.",
                player_index=player_index,
                current_record_index=current_record_index,
            )
        )
    expected_current_id = None
    if _is_non_empty_string(player_id) and _is_integer(current_index):
        expected_current_id = "domain_%s_current_%02d" % (player_id, current_index)
    if not _is_non_empty_string(current_id) or (
        expected_current_id is not None and current_id != expected_current_id
    ):
        errors.append(
            _error(
                "CURRENT_POSITION_LINK_INVALID",
                "current_id must identify its player and current index.",
                player_index=player_index,
                current_record_index=current_record_index,
                expected=expected_current_id,
                actual=current_id,
            )
        )
    elif current_id in current_ids:
        errors.append(_error("CURRENT_ID_DUPLICATE", "current IDs must be unique.", current_id=current_id))
    else:
        current_ids.add(current_id)

    metadata = current.get("metadata")
    if (
        not isinstance(metadata, dict)
        or metadata.get("ordered") is not True
        or metadata.get("positionally_linked_seal") is not True
    ):
        errors.append(
            _error(
                "METADATA_INVALID",
                "current metadata must declare ordered linked seals.",
                player_index=player_index,
                current_record_index=current_record_index,
            )
        )

    occupied_count = 0
    for position_type in ("horizon", "zenith"):
        slot = current.get(position_type)
        if _validate_slot_projection(
            slot,
            player_id,
            current_index,
            position_type,
            player_index,
            current_record_index,
            position_ids,
            occupant_instance_ids,
            errors,
        ):
            occupied_count += 1
    _validate_seal_projection(
        current.get("seal_position"),
        player_id,
        current_index,
        player_index,
        current_record_index,
        position_ids,
        errors,
    )
    return occupied_count


def _validate_slot_projection(
    slot,
    player_id,
    current_index,
    expected_position_type,
    player_index,
    current_record_index,
    position_ids,
    occupant_instance_ids,
    errors,
):
    if not isinstance(slot, dict):
        errors.append(
            _error(
                "SLOT_PROJECTION_INVALID",
                "%s slot must be a dict." % expected_position_type,
                player_index=player_index,
                current_record_index=current_record_index,
            )
        )
        return False
    for field_name in _REQUIRED_SLOT_FIELDS:
        if field_name not in slot:
            errors.append(
                _error(
                    "FIELD_MISSING",
                    "required slot field is missing.",
                    player_index=player_index,
                    current_record_index=current_record_index,
                    position_type=expected_position_type,
                    field=field_name,
                )
            )
    if "occupant_card_instance_id" in slot:
        errors.append(
            _error(
                "SLOT_PROJECTION_INVALID",
                "slot projection cannot expose occupant_card_instance_id separately.",
                player_index=player_index,
                current_record_index=current_record_index,
            )
        )

    position_id = slot.get("position_id")
    _track_position_id(position_id, position_ids, errors)
    expected_position_id = None
    if _is_non_empty_string(player_id) and _is_integer(current_index):
        expected_position_id = "domain_%s_current_%02d_%s" % (
            player_id,
            current_index,
            expected_position_type,
        )
    if (
        slot.get("player_id") != player_id
        or slot.get("current_index") != current_index
        or slot.get("position_type") != expected_position_type
        or slot.get("row") != expected_position_type
        or (expected_position_id is not None and position_id != expected_position_id)
    ):
        errors.append(
            _error(
                "CURRENT_POSITION_LINK_INVALID",
                "slot must match its player, current, and row.",
                player_index=player_index,
                current_record_index=current_record_index,
                position_type=expected_position_type,
            )
        )

    if slot.get("visibility") != "public":
        errors.append(_error("VISIBILITY_INVALID", "Domain slot visibility must be public."))
    metadata = slot.get("metadata")
    if (
        not isinstance(metadata, dict)
        or metadata.get("source") != _SOURCE
        or metadata.get("capacity") != 1
        or isinstance(metadata.get("capacity"), bool)
        or metadata.get("occupancy_model") != DOMAIN_OCCUPANCY_MODEL
    ):
        errors.append(_error("METADATA_INVALID", "Domain slot metadata is invalid."))

    occupancy_state = slot.get("occupancy_state")
    occupied = slot.get("occupied")
    occupant = slot.get("occupant")
    if occupancy_state not in {"empty", "occupied"} or not isinstance(occupied, bool):
        errors.append(_error("SLOT_PROJECTION_INVALID", "slot occupancy fields are invalid."))
        return False
    if occupancy_state == "empty":
        if occupied is not False or occupant is not None:
            errors.append(
                _error("SLOT_OCCUPANCY_MISMATCH", "empty slot must have occupied=false and occupant=null.")
            )
        return False
    if occupied is not True or not isinstance(occupant, dict):
        errors.append(
            _error("SLOT_OCCUPANCY_MISMATCH", "occupied slot must have occupied=true and an occupant.")
        )
        return True
    _validate_object_reference(occupant, player_id, occupant_instance_ids, errors)
    return True


def _validate_object_reference(reference, player_id, occupant_instance_ids, errors):
    card_instance_id = reference.get("card_instance_id") if isinstance(reference, dict) else None
    valid = (
        isinstance(reference, dict)
        and reference.get("schema_version") == OBJECT_REFERENCE_SCHEMA_VERSION
        and reference.get("contract_type") == "object_reference"
        and reference.get("object_type") == "card_instance"
        and _is_non_empty_string(reference.get("object_id"))
        and _is_non_empty_string(card_instance_id)
        and reference.get("object_id") == card_instance_id
        and _is_non_empty_string(reference.get("card_id"))
        and _is_integer(reference.get("zone_sequence"))
        and isinstance(reference.get("metadata"), dict)
    )
    if not valid:
        errors.append(_error("OBJECT_REFERENCE_INVALID", "occupied slot ObjectReference is invalid."))
    if isinstance(reference, dict) and reference.get("zone") != "domain":
        errors.append(_error("OBJECT_REFERENCE_ZONE_INVALID", "occupant ObjectReference zone must be domain."))
    if isinstance(reference, dict) and reference.get("visibility") != "public":
        errors.append(_error("VISIBILITY_INVALID", "occupant ObjectReference visibility must be public."))
    if isinstance(reference, dict) and reference.get("controller_player_id") != player_id:
        errors.append(
            _error(
                "OBJECT_REFERENCE_CONTROLLER_MISMATCH",
                "occupant controller must match the projected Domain player.",
                expected=player_id,
                actual=reference.get("controller_player_id"),
            )
        )
    if _is_non_empty_string(card_instance_id):
        if card_instance_id in occupant_instance_ids:
            errors.append(
                _error(
                    "OCCUPANT_INSTANCE_DUPLICATE",
                    "one card instance cannot occupy multiple projected slots.",
                    card_instance_id=card_instance_id,
                )
            )
        occupant_instance_ids.add(card_instance_id)


def _validate_seal_projection(
    seal,
    player_id,
    current_index,
    player_index,
    current_record_index,
    position_ids,
    errors,
):
    if not isinstance(seal, dict):
        errors.append(
            _error(
                "SEAL_PROJECTION_INVALID",
                "seal_position must be a dict.",
                player_index=player_index,
                current_record_index=current_record_index,
            )
        )
        return
    for field_name in _REQUIRED_SEAL_FIELDS:
        if field_name not in seal:
            errors.append(
                _error(
                    "FIELD_MISSING",
                    "required seal field is missing.",
                    player_index=player_index,
                    current_record_index=current_record_index,
                    field=field_name,
                )
            )

    position_id = seal.get("position_id")
    _track_position_id(position_id, position_ids, errors)
    expected_position_id = None
    if _is_non_empty_string(player_id) and _is_integer(current_index):
        expected_position_id = "domain_%s_current_%02d_seal" % (player_id, current_index)
    forbidden = sorted(field_name for field_name in _SEAL_FORBIDDEN_FIELDS if field_name in seal)
    if (
        seal.get("player_id") != player_id
        or seal.get("current_index") != current_index
        or seal.get("position_type") != "seal"
        or seal.get("visibility") != "public"
        or seal.get("state_model") != "not_implemented"
        or (expected_position_id is not None and position_id != expected_position_id)
        or forbidden
    ):
        errors.append(
            _error(
                "SEAL_PROJECTION_INVALID",
                "seal projection must remain a static public position reference.",
                player_index=player_index,
                current_record_index=current_record_index,
                forbidden_fields=forbidden,
            )
        )


def _validate_board_metadata(metadata, errors):
    expected = {
        "source": _SOURCE,
        "topology_model": _TOPOLOGY_MODEL,
        "occupancy_model": DOMAIN_OCCUPANCY_MODEL,
        "object_reference_model": OBJECT_REFERENCE_SCHEMA_VERSION,
        "seal_state_model": "not_implemented",
        "gameplay_mutation_model": "not_implemented",
        "public_information_only": True,
    }
    if not isinstance(metadata, dict):
        errors.append(_error("METADATA_INVALID", "board metadata must be a dict."))
        return
    for field_name, expected_value in expected.items():
        if metadata.get(field_name) != expected_value:
            errors.append(
                _error(
                    "METADATA_INVALID",
                    "board metadata value is invalid.",
                    field="metadata.%s" % field_name,
                    expected=expected_value,
                    actual=metadata.get(field_name),
                )
            )


def _track_position_id(position_id, position_ids, errors):
    if not _is_non_empty_string(position_id):
        errors.append(_error("CURRENT_POSITION_LINK_INVALID", "position_id must be non-empty."))
    elif position_id in position_ids:
        errors.append(
            _error("POSITION_ID_DUPLICATE", "position IDs must be unique.", position_id=position_id)
        )
    else:
        position_ids.add(position_id)


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


def _is_non_negative_integer(value):
    return _is_integer(value) and value >= 0


def _error(code, message, **details):
    error = {"code": code, "message": message}
    error.update(details)
    return error


class DomainBoardProjectionError(ValueError):
    """Raised when a public board cannot be projected safely."""

    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = deepcopy(list(errors or []))


__all__ = [
    "PLAYER_VISIBLE_DOMAIN_BOARD_SCHEMA_VERSION",
    "DOMAIN_BOARD_MODEL",
    "DomainBoardProjectionError",
    "create_player_visible_domain_board",
    "validate_player_visible_domain_board",
]
