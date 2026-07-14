"""Hidden-information-safe player snapshot projection for the minimal engine.

This module projects the current two-player smoke state. It does not apply
rules, mutate state, or expose the authoritative card instance registry.
"""

from __future__ import annotations

from copy import deepcopy

try:
    from card_instance import card_instance_to_object_reference
except ModuleNotFoundError:
    from .card_instance import card_instance_to_object_reference


PLAYER_VISIBLE_SNAPSHOT_SCHEMA_VERSION = "engine-player-visible-snapshot-v1"

VISIBILITY_POLICY = {
    "model": "minimal_visibility_projection_v0",
    "deck": "count_only",
    "own_hand": "owner_visible",
    "opponent_hand": "count_only",
    "discard": "public",
    "board": "not_implemented",
}

_REQUIRED_METADATA_VALUES = {
    "source": "python.engine.player_visible_snapshot",
    "rules_scope": "minimal_draw_end_turn_smoke",
    "runtime_decision": "reference_smoke_backend_candidate",
    "hidden_information_model": "minimal_visibility_projection_v0",
    "player_visible_snapshot_model": "stable_minimal_v1",
    "debug_snapshot_source": False,
    "card_instance_model": "minimal_registry_v0",
    "board_model": "not_implemented",
}

_REQUIRED_SNAPSHOT_FIELDS = (
    "schema_version",
    "contract_type",
    "snapshot_type",
    "visibility_mode",
    "player_id",
    "match_id",
    "state_version",
    "turn",
    "turn_number",
    "phase",
    "active_player_id",
    "priority_player_id",
    "players",
    "visibility_policy",
    "legal_action_summary",
    "event_log_summary",
    "diagnostics_summary",
    "metadata",
)

_REQUIRED_PLAYER_FIELDS = (
    "player_id",
    "relation",
    "is_viewer",
    "deck_count",
    "hand_count",
    "discard_count",
    "zones",
)

_REQUIRED_ZONE_FIELDS = (
    "zone",
    "count",
    "visibility_mode",
    "redacted",
    "objects",
    "metadata",
)

_ZONE_NAMES = ("deck", "hand", "discard")


def create_player_visible_snapshot(state, player_id, legal_actions=None, diagnostics=None):
    """Create a new player-visible projection without mutating engine state."""

    try:
        state.get_player(player_id)
    except Exception as exc:
        raise PlayerVisibleSnapshotError("Unknown player_id: %s" % player_id) from exc

    actions = list(legal_actions or [])
    invariant_errors = list(diagnostics or [])
    snapshot = {
        "schema_version": PLAYER_VISIBLE_SNAPSHOT_SCHEMA_VERSION,
        "contract_type": "engine_player_visible_snapshot",
        "snapshot_type": "player_visible_snapshot",
        "visibility_mode": "player",
        "player_id": player_id,
        "match_id": state.match_id,
        "state_version": state.state_version,
        "turn": state.turn_number,
        "turn_number": state.turn_number,
        "phase": state.phase,
        "active_player_id": state.active_player_id,
        "priority_player_id": state.active_player_id,
        "players": [_project_player(state, player, player_id) for player in state.players],
        "visibility_policy": deepcopy(VISIBILITY_POLICY),
        "legal_action_summary": _legal_action_summary(actions, state.state_version),
        "event_log_summary": _event_log_summary(state.event_log),
        "diagnostics_summary": {
            "invariant_errors": len(invariant_errors),
            "blocking_errors": len(invariant_errors),
            "warnings": 0,
            "hand_deck_invariants_ok": _hand_deck_invariants_ok(invariant_errors),
            "draw_preconditions_ok": all(bool(player.deck_card_instance_ids) for player in state.players),
        },
        "metadata": {
            "source": "python.engine.player_visible_snapshot",
            "rules_scope": "minimal_draw_end_turn_smoke",
            "runtime_decision": "reference_smoke_backend_candidate",
            "hidden_information_model": "minimal_visibility_projection_v0",
            "player_visible_snapshot_model": "stable_minimal_v1",
            "debug_snapshot_source": False,
            "card_instance_model": "minimal_registry_v0",
            "board_model": "not_implemented",
            "card_id_overlap_guard": False,
        },
    }
    return deepcopy(snapshot)


def validate_player_visible_snapshot(snapshot):
    """Return structured validation errors for a player-visible snapshot."""

    errors = []
    normalized = snapshot if isinstance(snapshot, dict) else {}
    if not isinstance(snapshot, dict):
        errors.append(_error("SNAPSHOT_NOT_DICT", "player-visible snapshot must be a dict."))

    for field_name in _REQUIRED_SNAPSHOT_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if normalized.get("schema_version") != PLAYER_VISIBLE_SNAPSHOT_SCHEMA_VERSION:
        errors.append(
            _error(
                "SCHEMA_VERSION_INVALID",
                "schema_version must identify the canonical player-visible snapshot.",
                actual=normalized.get("schema_version"),
            )
        )
    if normalized.get("contract_type") != "engine_player_visible_snapshot":
        errors.append(_error("CONTRACT_TYPE_INVALID", "contract_type is invalid."))
    if normalized.get("snapshot_type") != "player_visible_snapshot":
        errors.append(_error("SNAPSHOT_TYPE_INVALID", "snapshot_type is invalid."))
    if normalized.get("visibility_mode") != "player":
        errors.append(_error("VISIBILITY_MODE_INVALID", "visibility_mode must be player."))

    viewer_player_id = normalized.get("player_id")
    if not _is_non_empty_string(viewer_player_id):
        errors.append(_error("VIEWER_PLAYER_INVALID", "player_id must be a non-empty string."))
    if not _is_non_empty_string(normalized.get("match_id")):
        errors.append(_error("FIELD_VALUE_INVALID", "match_id must be a non-empty string.", field="match_id"))
    if not _is_non_negative_integer(normalized.get("state_version")):
        errors.append(
            _error("FIELD_VALUE_INVALID", "state_version must be a non-negative integer.", field="state_version")
        )
    for field_name in ("turn", "turn_number"):
        if not _is_positive_integer(normalized.get(field_name)):
            errors.append(
                _error("FIELD_VALUE_INVALID", "turn field must be a positive integer.", field=field_name)
            )
    if (
        _is_positive_integer(normalized.get("turn"))
        and _is_positive_integer(normalized.get("turn_number"))
        and normalized.get("turn") != normalized.get("turn_number")
    ):
        errors.append(_error("FIELD_VALUE_INVALID", "turn and turn_number must match.", field="turn"))
    for field_name in ("phase", "active_player_id", "priority_player_id"):
        if not _is_non_empty_string(normalized.get(field_name)):
            errors.append(
                _error("FIELD_VALUE_INVALID", "field must be a non-empty string.", field=field_name)
            )

    if normalized.get("visibility_policy") != VISIBILITY_POLICY:
        errors.append(_error("VISIBILITY_POLICY_INVALID", "visibility_policy is invalid."))
    for field_name in ("legal_action_summary", "event_log_summary", "diagnostics_summary", "metadata"):
        if not isinstance(normalized.get(field_name), dict):
            errors.append(_error("FIELD_TYPE_INVALID", "field must be a dict.", field=field_name))
    metadata = normalized.get("metadata")
    if isinstance(metadata, dict):
        for field_name, expected_value in _REQUIRED_METADATA_VALUES.items():
            if metadata.get(field_name) != expected_value:
                errors.append(
                    _error(
                        "FIELD_VALUE_INVALID",
                        "snapshot metadata value is invalid.",
                        field="metadata.%s" % field_name,
                        expected=expected_value,
                        actual=metadata.get(field_name),
                    )
                )

    players = normalized.get("players")
    if not isinstance(players, list) or len(players) != 2:
        errors.append(_error("PLAYERS_INVALID", "players must contain exactly two projections."))
        players = players if isinstance(players, list) else []

    visible_instance_ids = set()
    relations = []
    player_ids = []
    self_player_ids = []
    for player_index, player in enumerate(players):
        if not isinstance(player, dict):
            errors.append(
                _error("PLAYERS_INVALID", "player projection must be a dict.", player_index=player_index)
            )
            continue
        for field_name in _REQUIRED_PLAYER_FIELDS:
            if field_name not in player:
                errors.append(
                    _error(
                        "FIELD_MISSING",
                        "required player projection field is missing.",
                        player_index=player_index,
                        field=field_name,
                    )
                )

        projected_player_id = player.get("player_id")
        if not _is_non_empty_string(projected_player_id):
            errors.append(
                _error("PLAYERS_INVALID", "projected player_id must be non-empty.", player_index=player_index)
            )
        else:
            player_ids.append(projected_player_id)

        relation = player.get("relation")
        if relation not in {"self", "opponent"}:
            errors.append(
                _error("PLAYER_RELATION_INVALID", "relation must be self or opponent.", player_index=player_index)
            )
        else:
            relations.append(relation)
            if relation == "self":
                self_player_ids.append(projected_player_id)

        expected_is_viewer = relation == "self"
        if not isinstance(player.get("is_viewer"), bool) or player.get("is_viewer") != expected_is_viewer:
            errors.append(
                _error("PLAYER_RELATION_INVALID", "is_viewer must match relation.", player_index=player_index)
            )

        for count_field in ("deck_count", "hand_count", "discard_count"):
            if not _is_non_negative_integer(player.get(count_field)):
                errors.append(
                    _error(
                        "ZONE_PROJECTION_INVALID",
                        "player zone count must be a non-negative integer.",
                        player_index=player_index,
                        field=count_field,
                    )
                )

        _validate_zones(player, player_index, visible_instance_ids, errors)

    if len(set(player_ids)) != len(player_ids):
        errors.append(_error("PLAYERS_INVALID", "player projection IDs must be unique."))
    if relations.count("self") != 1 or relations.count("opponent") != 1:
        errors.append(_error("PLAYER_RELATION_INVALID", "exactly one self and one opponent are required."))
    if len(self_player_ids) != 1 or self_player_ids[0] != viewer_player_id:
        errors.append(_error("VIEWER_PLAYER_INVALID", "viewer player_id must match the self projection."))

    return {"valid": len(errors) == 0, "errors": errors}


def _project_player(state, player, viewer_player_id):
    is_viewer = player.player_id == viewer_player_id
    hand_visibility = "owner_visible" if is_viewer else "count_only"
    return {
        "player_id": player.player_id,
        "relation": "self" if is_viewer else "opponent",
        "is_viewer": is_viewer,
        "deck_count": len(player.deck_card_instance_ids),
        "hand_count": len(player.hand_card_instance_ids),
        "discard_count": len(player.discard_card_instance_ids),
        "zones": {
            "deck": _project_zone(state, "deck", player.deck_card_instance_ids, "count_only"),
            "hand": _project_zone(state, "hand", player.hand_card_instance_ids, hand_visibility),
            "discard": _project_zone(state, "discard", player.discard_card_instance_ids, "public"),
        },
    }


def _project_zone(state, zone_name, card_instance_ids, visibility_mode):
    visible = visibility_mode in {"owner_visible", "public"}
    objects = []
    if visible:
        for card_instance_id in card_instance_ids:
            record = state.get_card_instance(card_instance_id)
            objects.append(card_instance_to_object_reference(record))
    return {
        "zone": zone_name,
        "count": len(card_instance_ids),
        "visibility_mode": visibility_mode,
        "redacted": not visible,
        "objects": objects,
        "metadata": {
            "ordered": visible,
            "authority": "engine",
        },
    }


def _validate_zones(player, player_index, visible_instance_ids, errors):
    zones = player.get("zones")
    if not isinstance(zones, dict) or set(zones) != set(_ZONE_NAMES):
        errors.append(
            _error(
                "ZONE_PROJECTION_INVALID",
                "zones must contain exactly deck, hand, and discard.",
                player_index=player_index,
            )
        )
        zones = zones if isinstance(zones, dict) else {}

    relation = player.get("relation")
    for zone_name in _ZONE_NAMES:
        zone = zones.get(zone_name)
        if not isinstance(zone, dict):
            errors.append(
                _error(
                    "ZONE_PROJECTION_INVALID",
                    "zone projection must be a dict.",
                    player_index=player_index,
                    zone=zone_name,
                )
            )
            continue
        for field_name in _REQUIRED_ZONE_FIELDS:
            if field_name not in zone:
                errors.append(
                    _error(
                        "FIELD_MISSING",
                        "required zone projection field is missing.",
                        player_index=player_index,
                        zone=zone_name,
                        field=field_name,
                    )
                )
        if zone.get("zone") != zone_name:
            errors.append(
                _error(
                    "ZONE_PROJECTION_INVALID",
                    "zone field must match its projection key.",
                    player_index=player_index,
                    zone=zone_name,
                )
            )

        count = zone.get("count")
        count_field = "%s_count" % zone_name
        if not _is_non_negative_integer(count) or count != player.get(count_field):
            errors.append(
                _error(
                    "ZONE_PROJECTION_INVALID",
                    "zone count must match the player summary.",
                    player_index=player_index,
                    zone=zone_name,
                )
            )
        objects = zone.get("objects")
        if not isinstance(objects, list):
            errors.append(
                _error(
                    "ZONE_PROJECTION_INVALID",
                    "zone objects must be a list.",
                    player_index=player_index,
                    zone=zone_name,
                )
            )
            objects = []
        if not isinstance(zone.get("metadata"), dict):
            errors.append(
                _error(
                    "ZONE_PROJECTION_INVALID",
                    "zone metadata must be a dict.",
                    player_index=player_index,
                    zone=zone_name,
                )
            )
        else:
            metadata = zone["metadata"]
            if not isinstance(metadata.get("ordered"), bool) or metadata.get("authority") != "engine":
                errors.append(
                    _error(
                        "ZONE_PROJECTION_INVALID",
                        "zone metadata must declare ordered and engine authority.",
                        player_index=player_index,
                        zone=zone_name,
                    )
                )

        expected_visibility = _expected_zone_visibility(relation, zone_name)
        if zone.get("visibility_mode") != expected_visibility:
            errors.append(
                _error(
                    "ZONE_VISIBILITY_INVALID",
                    "zone visibility does not match the policy.",
                    player_index=player_index,
                    zone=zone_name,
                    expected=expected_visibility,
                    actual=zone.get("visibility_mode"),
                )
            )

        if expected_visibility == "count_only":
            if isinstance(zone.get("metadata"), dict) and zone["metadata"].get("ordered") is not False:
                errors.append(
                    _error(
                        "ZONE_VISIBILITY_INVALID",
                        "count-only zones cannot expose ordering.",
                        player_index=player_index,
                        zone=zone_name,
                    )
                )
            if zone.get("redacted") is not True:
                errors.append(
                    _error(
                        "ZONE_VISIBILITY_INVALID",
                        "count-only zones must be redacted.",
                        player_index=player_index,
                        zone=zone_name,
                    )
                )
            if objects:
                errors.append(
                    _error(
                        "HIDDEN_ZONE_OBJECTS_EXPOSED",
                        "count-only zones cannot expose objects.",
                        player_index=player_index,
                        zone=zone_name,
                    )
                )
        else:
            if isinstance(zone.get("metadata"), dict) and zone["metadata"].get("ordered") is not True:
                errors.append(
                    _error(
                        "ZONE_VISIBILITY_INVALID",
                        "visible minimal zones must preserve their canonical order.",
                        player_index=player_index,
                        zone=zone_name,
                    )
                )
            if zone.get("redacted") is not False:
                errors.append(
                    _error(
                        "ZONE_VISIBILITY_INVALID",
                        "visible zones cannot be redacted.",
                        player_index=player_index,
                        zone=zone_name,
                    )
                )
            if _is_non_negative_integer(count) and count != len(objects):
                errors.append(
                    _error(
                        "VISIBLE_ZONE_COUNT_MISMATCH",
                        "visible zone count must equal object count.",
                        player_index=player_index,
                        zone=zone_name,
                    )
                )
            for object_index, object_reference in enumerate(objects):
                _validate_object_reference(
                    object_reference,
                    zone_name,
                    player_index,
                    object_index,
                    visible_instance_ids,
                    errors,
                )


def _validate_object_reference(
    object_reference,
    zone_name,
    player_index,
    object_index,
    visible_instance_ids,
    errors,
):
    if not isinstance(object_reference, dict):
        errors.append(
            _error(
                "OBJECT_REFERENCE_INVALID",
                "visible object reference must be a dict.",
                player_index=player_index,
                zone=zone_name,
                object_index=object_index,
            )
        )
        return
    card_instance_id = object_reference.get("card_instance_id")
    if (
        object_reference.get("contract_type") != "object_reference"
        or object_reference.get("object_type") != "card_instance"
        or not _is_non_empty_string(card_instance_id)
        or object_reference.get("object_id") != card_instance_id
        or not _is_non_empty_string(object_reference.get("card_id"))
        or not isinstance(object_reference.get("zone_sequence"), int)
        or isinstance(object_reference.get("zone_sequence"), bool)
        or not isinstance(object_reference.get("metadata"), dict)
    ):
        errors.append(
            _error(
                "OBJECT_REFERENCE_INVALID",
                "visible card instance reference is invalid.",
                player_index=player_index,
                zone=zone_name,
                object_index=object_index,
            )
        )
    if object_reference.get("zone") != zone_name:
        errors.append(
            _error(
                "OBJECT_REFERENCE_ZONE_MISMATCH",
                "object reference zone must match the projection zone.",
                player_index=player_index,
                zone=zone_name,
                object_index=object_index,
            )
        )
    if _is_non_empty_string(card_instance_id):
        if card_instance_id in visible_instance_ids:
            errors.append(
                _error(
                    "VISIBLE_OBJECT_DUPLICATE",
                    "visible card_instance_id cannot appear more than once.",
                    card_instance_id=card_instance_id,
                )
            )
        visible_instance_ids.add(card_instance_id)


def _expected_zone_visibility(relation, zone_name):
    if zone_name == "deck":
        return "count_only"
    if zone_name == "discard":
        return "public"
    return "owner_visible" if relation == "self" else "count_only"


def _legal_action_summary(legal_actions, state_version):
    return {
        "state_version": state_version,
        "action_count": len(legal_actions),
        "enabled_count": sum(1 for action in legal_actions if action.get("enabled") is True),
        "disabled_count": sum(1 for action in legal_actions if action.get("enabled") is not True),
        "action_types": sorted(
            {str(action.get("action_type", "")) for action in legal_actions if action.get("action_type")}
        ),
    }


def _event_log_summary(events):
    return {
        "event_count": len(events),
        "last_event_type": str(events[-1].get("event_type", "")) if events else None,
        "last_event_sequence": events[-1].get("event_sequence") if events else None,
    }


def _hand_deck_invariants_ok(errors):
    zone_error_codes = {
        "PLAYER_ZONE_MISSING",
        "PLAYER_ZONE_INVALID",
        "CARD_INSTANCE_REGISTRY_INVALID",
        "CARD_INSTANCE_REGISTRY_KEY_MISMATCH",
        "CARD_INSTANCE_RECORD_INVALID",
        "PLAYER_ZONE_INSTANCE_UNKNOWN",
        "CARD_INSTANCE_MULTIPLE_ZONES",
        "CARD_INSTANCE_ZONE_MISMATCH",
        "CARD_INSTANCE_ZONE_INDEX_MISMATCH",
        "CARD_INSTANCE_OWNER_MISMATCH",
        "CARD_INSTANCE_CARD_UNKNOWN",
        "CARD_INSTANCE_OWNER_UNKNOWN",
        "CARD_INSTANCE_CONTROLLER_UNKNOWN",
        "CARD_INSTANCE_ORPHANED",
    }
    return not any(error.get("code") in zone_error_codes for error in errors)


def _is_non_empty_string(value):
    return isinstance(value, str) and value.strip() != ""


def _is_non_negative_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_positive_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _error(code, message, **details):
    error = {"code": code, "message": message}
    error.update(details)
    return error


class PlayerVisibleSnapshotError(Exception):
    """Raised when a player snapshot cannot be projected from engine state."""


__all__ = [
    "PLAYER_VISIBLE_SNAPSHOT_SCHEMA_VERSION",
    "VISIBILITY_POLICY",
    "PlayerVisibleSnapshotError",
    "create_player_visible_snapshot",
    "validate_player_visible_snapshot",
]
