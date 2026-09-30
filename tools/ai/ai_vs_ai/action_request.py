"""Action request gate for AI smoke tests.

The bot chooses a legal action, then sends an explicit request. This module
validates that request against the legal action list before the rules kernel is
allowed to mutate match state.
"""

from __future__ import annotations

from copy import deepcopy

try:
    from rules_kernel import apply_action
except ModuleNotFoundError:
    from .rules_kernel import apply_action


def create_action_request(
    match_id,
    player_id,
    action,
    expected_state_version=None,
    request_id=None,
    payload=None,
):
    action_id = action.get("action_id")
    request = {
        "request_id": (
            request_id
            if request_id is not None
            else "request:%s:%s" % (match_id, action_id)
        ),
        "match_id": match_id,
        "player_id": player_id,
        "action_id": action_id,
        "action_type": action.get("action_type"),
        "payload": deepcopy(payload) if payload is not None else {},
    }
    if expected_state_version is not None:
        request["expected_state_version"] = expected_state_version
    return request


def validate_action_request(request, legal_actions, state):
    normalized = dict(request or {})
    if normalized.get("match_id") != state.match_id:
        return _validation_result(False, "match_id_mismatch", normalized)

    if normalized.get("player_id") != state.active_player_id:
        return _validation_result(False, "player_not_active", normalized)

    legal_action = _find_legal_action(normalized.get("action_id"), legal_actions)
    if legal_action is None:
        return _validation_result(False, "unknown_action_id", normalized)

    if legal_action.get("enabled") is not True:
        if legal_action.get("reason") == "deck_empty":
            return _validation_result(False, "deck_empty", normalized, legal_action)
        return _validation_result(False, "action_not_enabled", normalized, legal_action)

    if normalized.get("action_type") != legal_action.get("action_type"):
        return _validation_result(False, "action_type_mismatch", normalized, legal_action)

    return _validation_result(True, None, normalized, legal_action)


def resolve_action_request(state, request, legal_actions):
    validation = validate_action_request(request, legal_actions, state)
    request_id = (request or {}).get("request_id")
    if not validation["valid"]:
        expose_state_version = validation["reason"] != "match_id_mismatch"
        state_version = getattr(state, "state_version", None) if expose_state_version else None
        diagnostics = []
        if validation["reason"] == "match_id_mismatch":
            diagnostics.append(
                {
                    "code": "MATCH_ID_MISMATCH",
                    "severity": "error",
                    "category": "request_validation",
                    "retry_policy": "use_active_match",
                }
            )
        return {
            "request_id": request_id,
            "accepted": False,
            "reason": validation["reason"],
            "events": [],
            "event_count": 0,
            "diagnostics": diagnostics,
            "state_version_before": state_version,
            "state_version_after": state_version,
            "new_event_sequences": [],
        }

    before_event_count = len(state.event_log)
    state_version_before = getattr(state, "state_version", None)
    result = apply_action(state, validation["legal_action"])
    state_version_after = getattr(state, "state_version", None)
    events = list(state.event_log[before_event_count:])
    return {
        "request_id": request_id,
        "accepted": True,
        "reason": None,
        "events": events,
        "event_count": len(events),
        "diagnostics": [],
        "state_version_before": state_version_before,
        "state_version_after": state_version_after,
        "new_event_sequences": [event.get("event_sequence") for event in events],
        "action": result.get("action"),
    }


def _find_legal_action(action_id, legal_actions):
    for action in list(legal_actions or []):
        if action.get("action_id") == action_id:
            return dict(action)
    return None


def _validation_result(valid, reason, request, legal_action=None):
    return {
        "valid": valid,
        "reason": reason,
        "request": dict(request or {}),
        "legal_action": dict(legal_action) if legal_action is not None else None,
    }
