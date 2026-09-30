"""Minimal typed turn-transition contract helpers."""

from __future__ import annotations

from copy import deepcopy

try:
    from engine_event import create_engine_event_envelope
except ModuleNotFoundError:
    from .engine_event import create_engine_event_envelope


TURN_TRANSITION_SCHEMA_VERSION = "minimal-turn-transition-record-v0"

_REQUIRED_TURN_TRANSITION_FIELDS = (
    "schema_version",
    "contract_type",
    "event_type",
    "previous_active_player_id",
    "next_active_player_id",
    "previous_priority_player_id",
    "next_priority_player_id",
    "turn_number_before",
    "turn_number_after",
    "phase_before",
    "phase_after",
    "source_action_id",
    "source_action_type",
    "state_version",
    "event_sequence",
    "metadata",
)


def create_turn_transition_record(
    previous_active_player_id,
    next_active_player_id,
    previous_priority_player_id,
    next_priority_player_id,
    turn_number_before,
    turn_number_after,
    phase_before,
    phase_after,
    source_action_id,
    source_action_type,
    state_version,
    event_sequence,
    metadata=None,
):
    """Create a JSON-compatible typed TurnTransition record."""

    return {
        "schema_version": TURN_TRANSITION_SCHEMA_VERSION,
        "contract_type": "turn_transition",
        "event_type": "turn_transition",
        "previous_active_player_id": previous_active_player_id,
        "next_active_player_id": next_active_player_id,
        "previous_priority_player_id": previous_priority_player_id,
        "next_priority_player_id": next_priority_player_id,
        "turn_number_before": turn_number_before,
        "turn_number_after": turn_number_after,
        "phase_before": phase_before,
        "phase_after": phase_after,
        "source_action_id": source_action_id,
        "source_action_type": source_action_type,
        "state_version": state_version,
        "event_sequence": event_sequence,
        "metadata": deepcopy(metadata or {}),
    }


def validate_turn_transition_record(record):
    """Validate a TurnTransition record without raising for normal invalid input."""

    errors = []
    normalized = record if isinstance(record, dict) else {}

    if not isinstance(record, dict):
        errors.append(_error("RECORD_NOT_DICT", "turn transition record must be a dict."))

    for field_name in _REQUIRED_TURN_TRANSITION_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if normalized.get("contract_type") != "turn_transition":
        errors.append(
            _error(
                "CONTRACT_TYPE_INVALID",
                "contract_type must be turn_transition.",
                actual=normalized.get("contract_type"),
            )
        )

    if normalized.get("event_type") != "turn_transition":
        errors.append(
            _error(
                "EVENT_TYPE_INVALID",
                "event_type must be turn_transition.",
                actual=normalized.get("event_type"),
            )
        )

    for field_name in (
        "schema_version",
        "previous_active_player_id",
        "next_active_player_id",
        "previous_priority_player_id",
        "next_priority_player_id",
        "phase_before",
        "phase_after",
        "source_action_id",
    ):
        if not _is_non_empty_string(normalized.get(field_name)):
            errors.append(_error("FIELD_EMPTY", "field must be a non-empty string.", field=field_name))

    previous_player_id = normalized.get("previous_active_player_id")
    next_player_id = normalized.get("next_active_player_id")
    if previous_player_id == next_player_id:
        errors.append(
            _error(
                "ACTIVE_PLAYER_TRANSITION_INVALID",
                "previous and next active player must differ.",
            )
        )

    turn_number_before = normalized.get("turn_number_before")
    turn_number_after = normalized.get("turn_number_after")
    before_valid = _is_positive_integer(turn_number_before)
    after_valid = _is_positive_integer(turn_number_after)
    if not before_valid:
        errors.append(
            _error(
                "TURN_NUMBER_INVALID",
                "turn_number_before must be a positive integer.",
                field="turn_number_before",
            )
        )
    if not after_valid:
        errors.append(
            _error(
                "TURN_NUMBER_INVALID",
                "turn_number_after must be a positive integer.",
                field="turn_number_after",
            )
        )
    if before_valid and after_valid and turn_number_after not in (turn_number_before, turn_number_before + 1):
        errors.append(
            _error(
                "TURN_NUMBER_TRANSITION_INVALID",
                "turn_number_after must equal turn_number_before or increment it by one.",
                turn_number_before=turn_number_before,
                turn_number_after=turn_number_after,
            )
        )

    if normalized.get("source_action_type") != "end_turn":
        errors.append(
            _error(
                "SOURCE_ACTION_TYPE_INVALID",
                "source_action_type must be end_turn.",
                actual=normalized.get("source_action_type"),
            )
        )

    if not _is_positive_integer(normalized.get("state_version")):
        errors.append(_error("STATE_VERSION_INVALID", "state_version must be a positive integer."))

    if not _is_positive_integer(normalized.get("event_sequence")):
        errors.append(_error("EVENT_SEQUENCE_INVALID", "event_sequence must be a positive integer."))

    if not isinstance(normalized.get("metadata"), dict):
        errors.append(_error("METADATA_INVALID", "metadata must be a dict."))

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


def turn_transition_to_event(record, event_index=None, turn_number=None, player_id=None, action_type=None):
    """Wrap a complete TurnTransition record in a generic engine-event envelope."""

    normalized = record if isinstance(record, dict) else {}
    return create_engine_event_envelope(
        event_type="turn_transition",
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


def _is_positive_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _error(code, message, **details):
    error = {
        "code": code,
        "message": message,
    }
    error.update(details)
    return error


__all__ = [
    "TURN_TRANSITION_SCHEMA_VERSION",
    "create_turn_transition_record",
    "validate_turn_transition_record",
    "turn_transition_to_event",
]
