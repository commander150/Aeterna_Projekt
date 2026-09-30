"""Canonical minimal AI episode trajectory contract helpers.

The helpers preserve transition contracts for smoke and diagnostics tooling.
They do not apply gameplay rules and do not provide replay reconstruction.
"""

from __future__ import annotations

from copy import deepcopy


EPISODE_STEP_SCHEMA_VERSION = "minimal-episode-step-v0"

_REQUIRED_EPISODE_STEP_FIELDS = (
    "schema_version",
    "contract_type",
    "step_index",
    "acting_player_id",
    "observation_before",
    "selected_action",
    "action_request",
    "action_response",
    "new_events",
    "observation_after",
    "state_version_before",
    "state_version_after",
    "new_event_sequences",
    "accepted",
    "success",
    "reason",
    "metadata",
)

_DEFAULT_METADATA = {
    "source": "python.engine.minimal_engine_environment",
    "trajectory_model": "full_transition_v0",
    "replay_ready": False,
    "rules_scope": "minimal_draw_end_turn_smoke",
}


def create_episode_step_record(
    step_index,
    acting_player_id,
    observation_before,
    selected_action,
    action_request,
    action_response,
    observation_after,
    metadata=None,
):
    """Create a copied, JSON-compatible record for one environment step."""

    selected_action_copy = deepcopy(selected_action)
    action_response_copy = deepcopy(action_response)
    metadata_copy = deepcopy(_DEFAULT_METADATA)
    if isinstance(metadata, dict):
        metadata_copy.update(deepcopy(metadata))
    elif metadata is not None:
        metadata_copy = deepcopy(metadata)
    new_events = deepcopy(action_response_copy.get("events", [])) if isinstance(action_response_copy, dict) else []
    new_event_sequences = (
        deepcopy(action_response_copy.get("new_event_sequences", []))
        if isinstance(action_response_copy, dict)
        else []
    )

    return {
        "schema_version": EPISODE_STEP_SCHEMA_VERSION,
        "contract_type": "minimal_episode_step",
        "step_index": step_index,
        "acting_player_id": acting_player_id,
        "observation_before": deepcopy(observation_before),
        "selected_action": selected_action_copy,
        "action_request": deepcopy(action_request),
        "action_response": action_response_copy,
        "new_events": new_events,
        "observation_after": deepcopy(observation_after),
        "state_version_before": action_response_copy.get("state_version_before"),
        "state_version_after": action_response_copy.get("state_version_after"),
        "new_event_sequences": new_event_sequences,
        "accepted": action_response_copy.get("accepted"),
        "success": action_response_copy.get("success"),
        "reason": action_response_copy.get("reason"),
        "selected_action_type": selected_action_copy.get("action_type"),
        "selected_action_id": selected_action_copy.get("action_id"),
        "metadata": metadata_copy,
    }


def validate_episode_step_record(record):
    """Validate one episode step without raising for normal invalid input."""

    errors = []
    normalized = record if isinstance(record, dict) else {}

    if not isinstance(record, dict):
        errors.append(_error("STEP_RECORD_INVALID", "episode step record must be a dict."))

    for field_name in _REQUIRED_EPISODE_STEP_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if not _is_non_empty_string(normalized.get("schema_version")):
        errors.append(
            _error("STEP_RECORD_INVALID", "schema_version must be a non-empty string.", field="schema_version")
        )

    if normalized.get("contract_type") != "minimal_episode_step":
        errors.append(
            _error(
                "STEP_RECORD_INVALID",
                "contract_type must be minimal_episode_step.",
                field="contract_type",
                actual=normalized.get("contract_type"),
            )
        )

    if not _is_non_negative_integer(normalized.get("step_index")):
        errors.append(_error("STEP_INDEX_INVALID", "step_index must be a non-negative integer."))

    if not _is_non_empty_string(normalized.get("acting_player_id")):
        errors.append(
            _error("ACTING_PLAYER_MISMATCH", "acting_player_id must be a non-empty string.")
        )

    for field_name in (
        "observation_before",
        "selected_action",
        "action_request",
        "action_response",
        "observation_after",
    ):
        if not isinstance(normalized.get(field_name), dict):
            errors.append(
                _error("STEP_RECORD_INVALID", "embedded contract must be a dict.", field=field_name)
            )

    if not isinstance(normalized.get("new_events"), list):
        errors.append(_error("STEP_RECORD_INVALID", "new_events must be a list.", field="new_events"))

    metadata = normalized.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(_error("STEP_RECORD_INVALID", "metadata must be a dict.", field="metadata"))
    else:
        for metadata_field, expected_value in _DEFAULT_METADATA.items():
            if metadata.get(metadata_field) != expected_value:
                errors.append(
                    _error(
                        "STEP_RECORD_INVALID",
                        "canonical trajectory metadata value is invalid.",
                        field="metadata.%s" % metadata_field,
                        expected=expected_value,
                        actual=metadata.get(metadata_field),
                    )
                )

    before = normalized.get("state_version_before")
    after = normalized.get("state_version_after")
    before_valid = _is_non_negative_integer(before)
    after_valid = _is_non_negative_integer(after)
    if not before_valid:
        errors.append(
            _error("RESPONSE_STATE_VERSION_MISMATCH", "state_version_before must be a non-negative integer.")
        )
    if not after_valid:
        errors.append(
            _error("RESPONSE_STATE_VERSION_MISMATCH", "state_version_after must be a non-negative integer.")
        )
    if before_valid and after_valid and after < before:
        errors.append(
            _error(
                "RESPONSE_STATE_VERSION_MISMATCH",
                "state_version_after cannot be lower than state_version_before.",
                state_version_before=before,
                state_version_after=after,
            )
        )

    event_sequences = normalized.get("new_event_sequences")
    if not isinstance(event_sequences, list):
        errors.append(
            _error("NEW_EVENTS_MISMATCH", "new_event_sequences must be a list.")
        )
    else:
        for sequence_index, sequence in enumerate(event_sequences):
            if not _is_positive_integer(sequence):
                errors.append(
                    _error(
                        "NEW_EVENTS_MISMATCH",
                        "event sequence must be a positive integer.",
                        sequence_index=sequence_index,
                    )
                )

    for field_name in ("accepted", "success"):
        if not isinstance(normalized.get(field_name), bool):
            errors.append(
                _error("RESPONSE_SUMMARY_MISMATCH", "response summary field must be bool.", field=field_name)
            )

    reason = normalized.get("reason")
    if reason is not None and not isinstance(reason, str):
        errors.append(
            _error("RESPONSE_SUMMARY_MISMATCH", "reason must be a string or null.", field="reason")
        )

    observation_before = normalized.get("observation_before")
    observation_after = normalized.get("observation_after")
    selected_action = normalized.get("selected_action")
    action_request = normalized.get("action_request")
    action_response = normalized.get("action_response")
    new_events = normalized.get("new_events")

    if isinstance(observation_before, dict) and observation_before.get("state_version") != before:
        errors.append(
            _error(
                "OBSERVATION_STATE_VERSION_MISMATCH",
                "observation_before state version must match the step.",
                observation="before",
            )
        )

    if isinstance(observation_after, dict) and observation_after.get("state_version") != after:
        errors.append(
            _error(
                "OBSERVATION_STATE_VERSION_MISMATCH",
                "observation_after state version must match the step.",
                observation="after",
            )
        )

    if isinstance(action_request, dict):
        request_state_version = action_request.get("expected_state_version")
        if not _is_non_negative_integer(request_state_version) or request_state_version != before:
            errors.append(
                _error(
                    "REQUEST_STATE_VERSION_MISMATCH",
                    "action request expected state version must match the step.",
                )
            )

    if isinstance(action_response, dict):
        if (
            not _is_non_negative_integer(action_response.get("state_version_before"))
            or not _is_non_negative_integer(action_response.get("state_version_after"))
            or not isinstance(action_response.get("accepted"), bool)
            or not isinstance(action_response.get("success"), bool)
            or action_response.get("state_version_before") != before
            or action_response.get("state_version_after") != after
        ):
            errors.append(
                _error(
                    "RESPONSE_STATE_VERSION_MISMATCH",
                    "action response state versions must match the step.",
                )
            )
        if (
            action_response.get("accepted") != normalized.get("accepted")
            or action_response.get("success") != normalized.get("success")
            or action_response.get("reason") != normalized.get("reason")
            or action_response.get("new_event_sequences") != event_sequences
        ):
            errors.append(
                _error(
                    "RESPONSE_SUMMARY_MISMATCH",
                    "action response summary fields must match the step.",
                )
            )
        if isinstance(new_events, list) and action_response.get("events") != new_events:
            errors.append(
                _error("NEW_EVENTS_MISMATCH", "action response events must match new_events.")
            )

    if isinstance(selected_action, dict) and isinstance(action_request, dict):
        if (
            selected_action.get("action_id") != action_request.get("action_id")
            or selected_action.get("action_type") != action_request.get("action_type")
        ):
            errors.append(
                _error("ACTION_REQUEST_MISMATCH", "selected action must match the action request.")
            )

    if isinstance(selected_action, dict) and selected_action.get("player_id") != normalized.get(
        "acting_player_id"
    ):
        errors.append(
            _error("ACTING_PLAYER_MISMATCH", "acting player must match the selected action player.")
        )

    if isinstance(observation_before, dict) and isinstance(selected_action, dict):
        action_space = observation_before.get("action_space")
        observation_actions = action_space.get("actions") if isinstance(action_space, dict) else None
        if isinstance(observation_actions, list) and selected_action not in observation_actions:
            errors.append(
                _error(
                    "ACTION_REQUEST_MISMATCH",
                    "selected action must be present in observation_before action space.",
                )
            )

    if isinstance(action_request, dict) and action_request.get("player_id") != normalized.get("acting_player_id"):
        errors.append(
            _error("ACTING_PLAYER_MISMATCH", "acting player must match the action request player.")
        )

    if (
        isinstance(observation_before, dict)
        and observation_before.get("player_id") != normalized.get("acting_player_id")
    ):
        errors.append(
            _error("ACTING_PLAYER_MISMATCH", "acting player must match observation_before player.")
        )

    if isinstance(new_events, list) and isinstance(event_sequences, list):
        extracted_sequences = [
            event.get("event_sequence") if isinstance(event, dict) else None for event in new_events
        ]
        if extracted_sequences != event_sequences:
            errors.append(
                _error("NEW_EVENTS_MISMATCH", "new event sequences must match new_events.")
            )

    if isinstance(selected_action, dict):
        if "selected_action_type" in normalized and normalized.get("selected_action_type") != selected_action.get(
            "action_type"
        ):
            errors.append(
                _error("ACTION_REQUEST_MISMATCH", "selected_action_type must derive from selected_action.")
            )
        if "selected_action_id" in normalized and normalized.get("selected_action_id") != selected_action.get(
            "action_id"
        ):
            errors.append(
                _error("ACTION_REQUEST_MISMATCH", "selected_action_id must derive from selected_action.")
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


def validate_episode_trajectory(records):
    """Validate step contracts plus state and event continuity."""

    if not isinstance(records, list):
        return {
            "valid": False,
            "errors": [_error("TRAJECTORY_NOT_LIST", "episode trajectory must be a list.")],
        }

    errors = []
    previous_state_version_after = None
    previous_event_sequence = None

    for record_index, record in enumerate(records):
        validation = validate_episode_step_record(record)
        if not validation.get("valid"):
            errors.append(
                _error(
                    "STEP_RECORD_INVALID",
                    "trajectory contains an invalid step record.",
                    record_index=record_index,
                    step_errors=deepcopy(validation.get("errors", [])),
                )
            )
            for step_error in validation.get("errors", []):
                copied_error = deepcopy(step_error)
                copied_error.setdefault("record_index", record_index)
                errors.append(copied_error)

        normalized = record if isinstance(record, dict) else {}
        step_index = normalized.get("step_index")
        if step_index != record_index:
            errors.append(
                _error(
                    "STEP_INDEX_SEQUENCE_INVALID",
                    "step_index values must increase continuously from zero.",
                    record_index=record_index,
                    step_index=step_index,
                )
            )

        state_version_before = normalized.get("state_version_before")
        state_version_after = normalized.get("state_version_after")
        if record_index > 0 and state_version_before != previous_state_version_after:
            errors.append(
                _error(
                    "STATE_VERSION_CONTINUITY_INVALID",
                    "step state versions must be continuous.",
                    record_index=record_index,
                    expected=previous_state_version_after,
                    actual=state_version_before,
                )
            )
        previous_state_version_after = state_version_after

        event_sequences = normalized.get("new_event_sequences")
        if isinstance(event_sequences, list):
            for sequence in event_sequences:
                if _is_positive_integer(sequence):
                    if previous_event_sequence is not None and sequence <= previous_event_sequence:
                        errors.append(
                            _error(
                                "EVENT_SEQUENCE_CONTINUITY_INVALID",
                                "event sequences must increase strictly across the trajectory.",
                                record_index=record_index,
                                previous=previous_event_sequence,
                                actual=sequence,
                            )
                        )
                    previous_event_sequence = sequence

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


def _is_non_empty_string(value):
    return isinstance(value, str) and value.strip() != ""


def _is_non_negative_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


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
    "EPISODE_STEP_SCHEMA_VERSION",
    "create_episode_step_record",
    "validate_episode_step_record",
    "validate_episode_trajectory",
]
