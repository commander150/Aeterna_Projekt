"""Generic minimal engine-event envelope helpers.

The envelope is gameplay-agnostic. ``player_id`` and ``action_type`` may be
``None`` for future system events, but present string values must be non-empty.
"""

from __future__ import annotations

from copy import deepcopy


ENGINE_EVENT_SCHEMA_VERSION = "minimal-engine-event-v0"

_REQUIRED_ENGINE_EVENT_FIELDS = (
    "schema_version",
    "contract_type",
    "event_index",
    "event_sequence",
    "event_type",
    "player_id",
    "action_type",
    "turn_number",
    "state_version",
    "payload",
)


def create_engine_event_envelope(
    event_type,
    event_index,
    event_sequence,
    player_id,
    action_type,
    turn_number,
    state_version,
    payload,
):
    """Create a JSON-compatible engine-event envelope from contract data."""

    return {
        "schema_version": ENGINE_EVENT_SCHEMA_VERSION,
        "contract_type": "engine_event",
        "event_index": event_index,
        "event_sequence": event_sequence,
        "event_type": event_type,
        "player_id": player_id,
        "action_type": action_type,
        "turn_number": turn_number,
        "state_version": state_version,
        "payload": deepcopy(payload),
    }


def validate_engine_event_envelope(record):
    """Validate an engine-event envelope without raising for normal invalid input."""

    errors = []
    normalized = record if isinstance(record, dict) else {}

    if not isinstance(record, dict):
        errors.append(_error("RECORD_NOT_DICT", "engine event record must be a dict."))

    for field_name in _REQUIRED_ENGINE_EVENT_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if normalized.get("contract_type") != "engine_event":
        errors.append(
            _error(
                "CONTRACT_TYPE_INVALID",
                "contract_type must be engine_event.",
                actual=normalized.get("contract_type"),
            )
        )

    for field_name in ("schema_version", "event_type"):
        if not _is_non_empty_string(normalized.get(field_name)):
            errors.append(_error("FIELD_EMPTY", "field must be a non-empty string.", field=field_name))

    for field_name in ("player_id", "action_type"):
        value = normalized.get(field_name)
        if value is not None and not _is_non_empty_string(value):
            errors.append(
                _error(
                    "FIELD_EMPTY",
                    "field must be a non-empty string or null.",
                    field=field_name,
                )
            )

    event_index = normalized.get("event_index")
    if not _is_integer(event_index) or event_index < 0:
        errors.append(_error("EVENT_INDEX_INVALID", "event_index must be a non-negative integer."))

    event_sequence = normalized.get("event_sequence")
    if not _is_integer(event_sequence) or event_sequence < 1:
        errors.append(_error("EVENT_SEQUENCE_INVALID", "event_sequence must be a positive integer."))

    turn_number = normalized.get("turn_number")
    if not _is_integer(turn_number) or turn_number < 1:
        errors.append(_error("TURN_NUMBER_INVALID", "turn_number must be a positive integer."))

    state_version = normalized.get("state_version")
    if not _is_integer(state_version) or state_version < 1:
        errors.append(_error("STATE_VERSION_INVALID", "state_version must be a positive integer."))

    if not isinstance(normalized.get("payload"), dict):
        errors.append(_error("PAYLOAD_INVALID", "payload must be a dict."))

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


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
    "ENGINE_EVENT_SCHEMA_VERSION",
    "create_engine_event_envelope",
    "validate_engine_event_envelope",
]
