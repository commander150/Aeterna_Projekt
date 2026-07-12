"""Minimal card instance record helpers.

This module is a small contract helper for the future Card_ID /
card_instance_id split. It does not mutate MatchState, does not touch zones,
and is not wired into draw_card yet.
"""

from __future__ import annotations


RECORD_SCHEMA_VERSION = "minimal-card-instance-record-v0"
OBJECT_REFERENCE_SCHEMA_VERSION = "minimal-object-reference-v0"

_REQUIRED_RECORD_FIELDS = (
    "schema_version",
    "contract_type",
    "card_instance_id",
    "card_id",
    "owner_player_id",
    "controller_player_id",
    "zone",
    "zone_index",
    "visibility",
    "created_sequence",
    "zone_sequence",
    "metadata",
)


def create_card_instance_id(player_id, sequence):
    """Return a deterministic card instance id for smoke/test setup."""

    return "ci_%s_%04d" % (str(player_id), int(sequence))


def create_card_instance_record(
    card_instance_id,
    card_id,
    owner_player_id,
    controller_player_id,
    zone,
    zone_index,
    visibility,
    created_sequence,
    zone_sequence,
    metadata=None,
):
    """Create a JSON-compatible card instance record dict."""

    return {
        "schema_version": RECORD_SCHEMA_VERSION,
        "contract_type": "card_instance_record",
        "card_instance_id": card_instance_id,
        "card_id": card_id,
        "owner_player_id": owner_player_id,
        "controller_player_id": controller_player_id,
        "zone": zone,
        "zone_index": zone_index,
        "visibility": visibility,
        "created_sequence": created_sequence,
        "zone_sequence": zone_sequence,
        "metadata": dict(metadata or {}),
    }


def validate_card_instance_record(record):
    """Validate a card instance record and return diagnostics-friendly output."""

    errors = []
    normalized = record if isinstance(record, dict) else {}

    if not isinstance(record, dict):
        errors.append(_error("RECORD_NOT_DICT", "card instance record must be a dict."))

    for field_name in _REQUIRED_RECORD_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if normalized.get("contract_type") != "card_instance_record":
        errors.append(
            _error(
                "CONTRACT_TYPE_INVALID",
                "contract_type must be card_instance_record.",
                actual=normalized.get("contract_type"),
            )
        )

    for field_name in ("card_instance_id", "card_id", "owner_player_id", "zone", "visibility"):
        if not _is_non_empty_string(normalized.get(field_name)):
            errors.append(_error("FIELD_EMPTY", "field must be a non-empty string.", field=field_name))

    zone_index = normalized.get("zone_index")
    if zone_index is not None and not isinstance(zone_index, int):
        errors.append(_error("ZONE_INDEX_INVALID", "zone_index must be an integer or null."))

    for field_name in ("created_sequence", "zone_sequence"):
        if not isinstance(normalized.get(field_name), int):
            errors.append(_error("SEQUENCE_INVALID", "sequence field must be an integer.", field=field_name))

    if not isinstance(normalized.get("metadata"), dict):
        errors.append(_error("METADATA_INVALID", "metadata must be a dict."))

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


def card_instance_to_object_reference(record):
    """Create a minimal ObjectReference dict for a card instance record."""

    normalized = dict(record or {})
    card_instance_id = normalized.get("card_instance_id")
    return {
        "schema_version": OBJECT_REFERENCE_SCHEMA_VERSION,
        "contract_type": "object_reference",
        "object_type": "card_instance",
        "object_id": card_instance_id,
        "card_instance_id": card_instance_id,
        "card_id": normalized.get("card_id"),
        "zone": normalized.get("zone"),
        "zone_sequence": normalized.get("zone_sequence"),
        "controller_player_id": normalized.get("controller_player_id"),
        "visibility": normalized.get("visibility"),
        "metadata": {
            "source": "python.engine.card_instance",
            "reference_scope": "minimal_card_instance_helper",
        },
    }


def _is_non_empty_string(value):
    return isinstance(value, str) and value.strip() != ""


def _error(code, message, **details):
    error = {
        "code": code,
        "message": message,
    }
    error.update(details)
    return error


__all__ = [
    "create_card_instance_id",
    "create_card_instance_record",
    "validate_card_instance_record",
    "card_instance_to_object_reference",
]
