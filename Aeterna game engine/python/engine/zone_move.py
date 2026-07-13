"""Minimal zone move contract and engine-event helpers.

This module describes zone movement without applying it. The rules kernel may
use the helpers to record an already-applied transition in the runtime log.
"""

from __future__ import annotations

try:
    from engine_event import ENGINE_EVENT_SCHEMA_VERSION, create_engine_event_envelope
except ModuleNotFoundError:
    from .engine_event import ENGINE_EVENT_SCHEMA_VERSION, create_engine_event_envelope


ZONE_MOVE_SCHEMA_VERSION = "minimal-zone-move-record-v0"

_REQUIRED_ZONE_MOVE_FIELDS = (
    "schema_version",
    "contract_type",
    "event_type",
    "card_instance_id",
    "card_id",
    "owner_player_id",
    "controller_player_id",
    "from_zone",
    "from_zone_index",
    "to_zone",
    "to_zone_index",
    "source_action_id",
    "source_action_type",
    "state_version",
    "event_sequence",
    "visibility_before",
    "visibility_after",
    "metadata",
)

def create_zone_move_record(
    card_instance_id,
    card_id,
    owner_player_id,
    controller_player_id,
    from_zone,
    from_zone_index,
    to_zone,
    to_zone_index,
    source_action_id,
    source_action_type,
    state_version,
    event_sequence,
    visibility_before,
    visibility_after,
    metadata=None,
):
    """Create a JSON-compatible ZoneMove record without applying it."""

    return {
        "schema_version": ZONE_MOVE_SCHEMA_VERSION,
        "contract_type": "zone_move",
        "event_type": "zone_move",
        "card_instance_id": card_instance_id,
        "card_id": card_id,
        "owner_player_id": owner_player_id,
        "controller_player_id": controller_player_id,
        "from_zone": from_zone,
        "from_zone_index": from_zone_index,
        "to_zone": to_zone,
        "to_zone_index": to_zone_index,
        "source_action_id": source_action_id,
        "source_action_type": source_action_type,
        "state_version": state_version,
        "event_sequence": event_sequence,
        "visibility_before": visibility_before,
        "visibility_after": visibility_after,
        "metadata": dict(metadata or {}),
    }


def validate_zone_move_record(record):
    """Validate a ZoneMove record and return diagnostics-friendly output."""

    errors = []
    normalized = record if isinstance(record, dict) else {}

    if not isinstance(record, dict):
        errors.append(_error("RECORD_NOT_DICT", "zone move record must be a dict."))

    for field_name in _REQUIRED_ZONE_MOVE_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if normalized.get("contract_type") != "zone_move":
        errors.append(
            _error(
                "CONTRACT_TYPE_INVALID",
                "contract_type must be zone_move.",
                actual=normalized.get("contract_type"),
            )
        )

    if normalized.get("event_type") != "zone_move":
        errors.append(
            _error(
                "EVENT_TYPE_INVALID",
                "event_type must be zone_move.",
                actual=normalized.get("event_type"),
            )
        )

    for field_name in (
        "card_instance_id",
        "card_id",
        "owner_player_id",
        "from_zone",
        "to_zone",
        "source_action_id",
        "source_action_type",
        "visibility_before",
        "visibility_after",
    ):
        if not _is_non_empty_string(normalized.get(field_name)):
            errors.append(_error("FIELD_EMPTY", "field must be a non-empty string.", field=field_name))

    controller_player_id = normalized.get("controller_player_id")
    if controller_player_id is not None and not _is_non_empty_string(controller_player_id):
        errors.append(
            _error(
                "CONTROLLER_PLAYER_ID_INVALID",
                "controller_player_id must be a non-empty string or null.",
            )
        )

    for field_name in ("from_zone_index", "to_zone_index"):
        value = normalized.get(field_name)
        if value is not None and not _is_integer(value):
            errors.append(
                _error(
                    "ZONE_INDEX_INVALID",
                    "zone index must be an integer or null.",
                    field=field_name,
                )
            )

    for field_name in ("state_version", "event_sequence"):
        if not _is_integer(normalized.get(field_name)):
            errors.append(
                _error(
                    "SEQUENCE_INVALID",
                    "state/event sequence field must be an integer.",
                    field=field_name,
                )
            )

    if not isinstance(normalized.get("metadata"), dict):
        errors.append(_error("METADATA_INVALID", "metadata must be a dict."))

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


def zone_move_to_event(record, event_index=None, turn_number=None, player_id=None, action_type=None):
    """Wrap a complete, copied ZoneMove record in an engine-event envelope."""

    normalized = record if isinstance(record, dict) else {}
    return create_engine_event_envelope(
        event_type="zone_move",
        event_index=event_index,
        event_sequence=normalized.get("event_sequence"),
        player_id=player_id,
        action_type=action_type,
        turn_number=turn_number,
        state_version=normalized.get("state_version"),
        payload=normalized,
    )


def _is_non_empty_string(value):
    return isinstance(value, str) and value.strip() != ""


def _is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _error(code, message, **details):
    error = {
        "code": code,
        "message": message,
    }
    error.update(details)
    return error


__all__ = [
    "create_zone_move_record",
    "validate_zone_move_record",
    "zone_move_to_event",
]
