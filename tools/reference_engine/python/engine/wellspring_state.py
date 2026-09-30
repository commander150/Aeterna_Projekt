"""Isolated Wellspring membership and base resource summary contracts.

These helpers do not integrate Wellspring into MatchState or PlayerState and
do not implement Inflow, payment, activity mutation, or gameplay events.
"""

from __future__ import annotations

from copy import deepcopy

try:
    from card_instance import (
        CANONICAL_HIDDEN_VISIBILITY,
        SUPPORTED_ACTIVITY_STATES,
        validate_card_instance_record,
    )
except ModuleNotFoundError:
    from .card_instance import (
        CANONICAL_HIDDEN_VISIBILITY,
        SUPPORTED_ACTIVITY_STATES,
        validate_card_instance_record,
    )


PLAYER_WELLSPRING_STATE_SCHEMA_VERSION = "minimal-player-wellspring-state-v0"
WELLSPRING_RESOURCE_SUMMARY_SCHEMA_VERSION = "minimal-wellspring-resource-summary-v0"
WELLSPRING_RESOURCE_MODEL = "base-wellspring-count-and-activity-v0"
WELLSPRING_ZONE = "wellspring"
WELLSPRING_VISIBILITY_MODE = CANONICAL_HIDDEN_VISIBILITY

_REQUIRED_STATE_FIELDS = (
    "schema_version",
    "contract_type",
    "player_id",
    "zone",
    "visibility_mode",
    "wellspring_card_instance_ids",
    "card_count",
    "metadata",
)
_REQUIRED_SUMMARY_FIELDS = (
    "schema_version",
    "contract_type",
    "resource_model",
    "player_id",
    "wellspring_card_count",
    "magnitude",
    "active_source_count",
    "exhausted_source_count",
    "available_aura",
    "typed_aura",
    "metadata",
)
_STATE_METADATA = {
    "source": "python.engine.wellspring_state",
    "resource_model": WELLSPRING_RESOURCE_MODEL,
    "cards_face_down": True,
    "gameplay_order_significant": False,
    "serialization_order_stable": True,
    "magnitude_model": "card_count",
    "aura_model": "active_card_count",
    "typed_aura_model": "not_implemented",
    "payment_model": "not_implemented",
    "match_state_integration": "not_implemented",
    "inflow_action_integration": "not_implemented",
}
_SUMMARY_METADATA = {
    "source": "python.engine.wellspring_state",
    "resource_model": WELLSPRING_RESOURCE_MODEL,
    "magnitude_derived_from": "wellspring_card_count",
    "available_aura_derived_from": "active_source_count",
    "typed_aura_model": "not_implemented",
    "payment_legality": "not_implemented",
    "resonance_included": False,
    "temporary_aura_included": False,
    "aura_burn_included": False,
    "magnitude_overrides_included": False,
    "state_mutation": False,
}


def create_empty_player_wellspring_state(player_id):
    """Create a validated empty Wellspring contract for one player."""

    return create_player_wellspring_state(player_id, [], {})


def create_player_wellspring_state(player_id, card_instance_ids, card_instances):
    """Create a detached Wellspring membership contract from registry IDs."""

    _require_card_instance_registry(card_instances, "create player Wellspring state")
    ids = deepcopy(card_instance_ids) if isinstance(card_instance_ids, list) else card_instance_ids
    record = {
        "schema_version": PLAYER_WELLSPRING_STATE_SCHEMA_VERSION,
        "contract_type": "player_wellspring_state",
        "player_id": player_id,
        "zone": WELLSPRING_ZONE,
        "visibility_mode": WELLSPRING_VISIBILITY_MODE,
        "wellspring_card_instance_ids": ids,
        "card_count": len(ids) if isinstance(ids, list) else None,
        "metadata": deepcopy(_STATE_METADATA),
    }
    validation = validate_player_wellspring_state(record, card_instances)
    if not validation.get("valid"):
        raise WellspringStateError(
            "Cannot create player Wellspring state: %s" % _first_error_code(validation),
            validation.get("errors", []),
        )
    return deepcopy(record)


def validate_player_wellspring_state(record, card_instances=None):
    """Validate a Wellspring state, optionally against a card registry."""

    errors = []
    normalized = record if isinstance(record, dict) else {}
    if not isinstance(record, dict):
        errors.append(_error("WELLSPRING_NOT_DICT", "player Wellspring state must be a dict."))

    for field_name in _REQUIRED_STATE_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if normalized.get("schema_version") != PLAYER_WELLSPRING_STATE_SCHEMA_VERSION:
        errors.append(
            _error(
                "SCHEMA_VERSION_INVALID",
                "schema_version must identify the minimal player Wellspring state.",
                actual=normalized.get("schema_version"),
            )
        )
    if normalized.get("contract_type") != "player_wellspring_state":
        errors.append(
            _error(
                "CONTRACT_TYPE_INVALID",
                "contract_type must be player_wellspring_state.",
                actual=normalized.get("contract_type"),
            )
        )
    player_id = normalized.get("player_id")
    if not _is_non_empty_string(player_id):
        errors.append(_error("PLAYER_ID_INVALID", "player_id must be a non-empty string."))
    if normalized.get("zone") != WELLSPRING_ZONE:
        errors.append(_error("ZONE_INVALID", "zone must be wellspring."))
    if normalized.get("visibility_mode") != WELLSPRING_VISIBILITY_MODE:
        errors.append(
            _error(
                "VISIBILITY_MODE_INVALID",
                "visibility_mode must use the canonical hidden visibility.",
                expected=WELLSPRING_VISIBILITY_MODE,
                actual=normalized.get("visibility_mode"),
            )
        )

    instance_ids = normalized.get("wellspring_card_instance_ids")
    if not isinstance(instance_ids, list):
        errors.append(_error("INSTANCE_IDS_INVALID", "wellspring_card_instance_ids must be a list."))
        instance_ids = []
    else:
        for index, card_instance_id in enumerate(instance_ids):
            if not _is_non_empty_string(card_instance_id):
                errors.append(
                    _error(
                        "INSTANCE_IDS_INVALID",
                        "each card instance ID must be a non-empty string.",
                        index=index,
                    )
                )
        duplicates = _duplicates(
            card_instance_id
            for card_instance_id in instance_ids
            if _is_non_empty_string(card_instance_id)
        )
        if duplicates:
            errors.append(
                _error(
                    "INSTANCE_ID_DUPLICATE",
                    "Wellspring card instance IDs must be unique.",
                    duplicate_ids=duplicates,
                )
            )

    card_count = normalized.get("card_count")
    if not _is_non_negative_integer(card_count) or card_count != len(instance_ids):
        errors.append(
            _error(
                "CARD_COUNT_MISMATCH",
                "card_count must be a non-negative integer matching the ID list length.",
                expected=len(instance_ids),
                actual=card_count,
            )
        )

    _validate_metadata(normalized.get("metadata"), _STATE_METADATA, errors, state_metadata=True)

    if card_instances is not None:
        _validate_registry_relationship(instance_ids, player_id, card_instances, errors)

    return {"valid": len(errors) == 0, "errors": errors}


def create_wellspring_resource_summary(wellspring_state, card_instances):
    """Derive base Magnitude and available Aura without storing resource state."""

    _require_card_instance_registry(card_instances, "create Wellspring resource summary")
    validation = validate_player_wellspring_state(wellspring_state, card_instances)
    if not validation.get("valid"):
        raise WellspringStateError(
            "Cannot summarize invalid player Wellspring state: %s" % _first_error_code(validation),
            validation.get("errors", []),
        )

    instance_ids = list(wellspring_state["wellspring_card_instance_ids"])
    active_source_count = sum(
        1 for card_instance_id in instance_ids
        if card_instances[card_instance_id].get("activity_state") == "active"
    )
    exhausted_source_count = sum(
        1 for card_instance_id in instance_ids
        if card_instances[card_instance_id].get("activity_state") == "exhausted"
    )
    card_count = len(instance_ids)
    summary = {
        "schema_version": WELLSPRING_RESOURCE_SUMMARY_SCHEMA_VERSION,
        "contract_type": "wellspring_resource_summary",
        "resource_model": WELLSPRING_RESOURCE_MODEL,
        "player_id": wellspring_state["player_id"],
        "wellspring_card_count": card_count,
        "magnitude": card_count,
        "active_source_count": active_source_count,
        "exhausted_source_count": exhausted_source_count,
        "available_aura": active_source_count,
        "typed_aura": None,
        "metadata": deepcopy(_SUMMARY_METADATA),
    }
    summary_validation = validate_wellspring_resource_summary(summary)
    if not summary_validation.get("valid"):
        raise WellspringStateError(
            "Generated Wellspring resource summary is invalid: %s"
            % _first_error_code(summary_validation),
            summary_validation.get("errors", []),
        )
    return deepcopy(summary)


def validate_wellspring_resource_summary(record):
    """Validate a computed base Wellspring resource summary."""

    errors = []
    normalized = record if isinstance(record, dict) else {}
    if not isinstance(record, dict):
        errors.append(_error("SUMMARY_NOT_DICT", "Wellspring resource summary must be a dict."))

    for field_name in _REQUIRED_SUMMARY_FIELDS:
        if field_name not in normalized:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))

    if normalized.get("schema_version") != WELLSPRING_RESOURCE_SUMMARY_SCHEMA_VERSION:
        errors.append(_error("SCHEMA_VERSION_INVALID", "summary schema_version is invalid."))
    if normalized.get("contract_type") != "wellspring_resource_summary":
        errors.append(_error("CONTRACT_TYPE_INVALID", "contract_type must be wellspring_resource_summary."))
    if normalized.get("resource_model") != WELLSPRING_RESOURCE_MODEL:
        errors.append(_error("RESOURCE_MODEL_INVALID", "resource_model is not supported."))
    if not _is_non_empty_string(normalized.get("player_id")):
        errors.append(_error("PLAYER_ID_INVALID", "player_id must be a non-empty string."))

    count_fields = (
        "wellspring_card_count",
        "magnitude",
        "active_source_count",
        "exhausted_source_count",
        "available_aura",
    )
    valid_counts = {}
    for field_name in count_fields:
        value = normalized.get(field_name)
        valid_counts[field_name] = _is_non_negative_integer(value)
        if not valid_counts[field_name]:
            errors.append(
                _error(
                    "COUNT_INVALID",
                    "resource counts must be non-negative integers.",
                    field=field_name,
                    actual=value,
                )
            )

    if valid_counts.get("magnitude") and valid_counts.get("wellspring_card_count"):
        if normalized["magnitude"] != normalized["wellspring_card_count"]:
            errors.append(_error("MAGNITUDE_MISMATCH", "magnitude must equal wellspring_card_count."))
    if all(valid_counts.get(field_name) for field_name in (
        "active_source_count",
        "exhausted_source_count",
        "wellspring_card_count",
    )):
        if (
            normalized["active_source_count"] + normalized["exhausted_source_count"]
            != normalized["wellspring_card_count"]
        ):
            errors.append(
                _error(
                    "ACTIVITY_COUNT_MISMATCH",
                    "active and exhausted counts must sum to wellspring_card_count.",
                )
            )
    if valid_counts.get("available_aura") and valid_counts.get("active_source_count"):
        if normalized["available_aura"] != normalized["active_source_count"]:
            errors.append(
                _error(
                    "AVAILABLE_AURA_MISMATCH",
                    "available_aura must equal active_source_count.",
                )
            )

    if normalized.get("typed_aura") is not None:
        errors.append(
            _error(
                "TYPED_AURA_NOT_SUPPORTED",
                "typed_aura must remain null in the base Wellspring model.",
            )
        )
    _validate_metadata(normalized.get("metadata"), _SUMMARY_METADATA, errors, state_metadata=False)
    return {"valid": len(errors) == 0, "errors": errors}


def get_wellspring_card_instance_ids(wellspring_state):
    """Return a detached ID list from a valid isolated Wellspring contract."""

    validation = validate_player_wellspring_state(wellspring_state)
    if not validation.get("valid"):
        raise WellspringStateError(
            "Cannot read invalid player Wellspring state: %s" % _first_error_code(validation),
            validation.get("errors", []),
        )
    return deepcopy(wellspring_state["wellspring_card_instance_ids"])


def _validate_registry_relationship(instance_ids, player_id, card_instances, errors):
    if not isinstance(card_instances, dict):
        errors.append(_error("INSTANCE_RECORD_INVALID", "card_instances must be a registry dict."))
        return
    for zone_index, card_instance_id in enumerate(instance_ids):
        if not _is_non_empty_string(card_instance_id):
            continue
        card_instance = card_instances.get(card_instance_id)
        if not isinstance(card_instance, dict):
            errors.append(
                _error(
                    "INSTANCE_UNKNOWN",
                    "Wellspring instance ID must exist in the registry.",
                    card_instance_id=card_instance_id,
                )
            )
            continue

        record_validation = validate_card_instance_record(card_instance)
        if not record_validation.get("valid"):
            errors.append(
                _error(
                    "INSTANCE_RECORD_INVALID",
                    "Wellspring card instance failed record validation.",
                    card_instance_id=card_instance_id,
                    record_errors=record_validation.get("errors", []),
                )
            )
        if card_instance.get("card_instance_id") != card_instance_id:
            errors.append(
                _error(
                    "INSTANCE_RECORD_INVALID",
                    "registry key must match card_instance_id.",
                    card_instance_id=card_instance_id,
                    record_card_instance_id=card_instance.get("card_instance_id"),
                )
            )
        if card_instance.get("zone") != WELLSPRING_ZONE:
            errors.append(
                _error(
                    "INSTANCE_ZONE_MISMATCH",
                    "Wellspring member record must have zone=wellspring.",
                    card_instance_id=card_instance_id,
                    actual_zone=card_instance.get("zone"),
                )
            )
        if card_instance.get("zone_index") != zone_index:
            errors.append(
                _error(
                    "INSTANCE_ZONE_INDEX_MISMATCH",
                    "Wellspring member zone_index must match list position.",
                    card_instance_id=card_instance_id,
                    expected=zone_index,
                    actual=card_instance.get("zone_index"),
                )
            )
        if card_instance.get("controller_player_id") != player_id:
            errors.append(
                _error(
                    "INSTANCE_CONTROLLER_MISMATCH",
                    "Wellspring member controller must match player_id.",
                    card_instance_id=card_instance_id,
                    expected=player_id,
                    actual=card_instance.get("controller_player_id"),
                )
            )
        if card_instance.get("activity_state") not in SUPPORTED_ACTIVITY_STATES:
            errors.append(
                _error(
                    "INSTANCE_ACTIVITY_INVALID",
                    "Wellspring member must be active or exhausted.",
                    card_instance_id=card_instance_id,
                    actual=card_instance.get("activity_state"),
                )
            )
        if card_instance.get("visibility") != CANONICAL_HIDDEN_VISIBILITY:
            errors.append(
                _error(
                    "INSTANCE_VISIBILITY_INVALID",
                    "Wellspring member must use canonical hidden visibility.",
                    card_instance_id=card_instance_id,
                    expected=CANONICAL_HIDDEN_VISIBILITY,
                    actual=card_instance.get("visibility"),
                )
            )


def _require_card_instance_registry(card_instances, operation):
    if not isinstance(card_instances, dict):
        errors = [_error("INSTANCE_RECORD_INVALID", "card_instances must be a registry dict.")]
        raise WellspringStateError("Cannot %s: INSTANCE_RECORD_INVALID" % operation, errors)


def _validate_metadata(metadata, expected, errors, state_metadata):
    if not isinstance(metadata, dict):
        errors.append(_error("METADATA_INVALID", "metadata must be a dict."))
        return
    unsupported_summary_fields = {
        "typed_aura_model",
        "payment_legality",
        "resonance_included",
        "temporary_aura_included",
        "aura_burn_included",
        "magnitude_overrides_included",
        "state_mutation",
    }
    unsupported_state_fields = {"typed_aura_model", "payment_model"}
    unsupported_fields = unsupported_state_fields if state_metadata else unsupported_summary_fields
    for field_name, expected_value in expected.items():
        actual_value = metadata.get(field_name)
        if actual_value != expected_value:
            code = (
                "UNSUPPORTED_RESOURCE_LAYER_INCLUDED"
                if field_name in unsupported_fields
                else "METADATA_INVALID"
            )
            errors.append(
                _error(
                    code,
                    "Wellspring metadata value is invalid.",
                    field="metadata.%s" % field_name,
                    expected=expected_value,
                    actual=actual_value,
                )
            )


def _duplicates(values):
    seen = set()
    duplicates = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def _first_error_code(validation):
    errors = validation.get("errors") or []
    return errors[0].get("code", "unknown") if errors else "unknown"


def _is_non_empty_string(value):
    return isinstance(value, str) and value.strip() != ""


def _is_non_negative_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _error(code, message, **details):
    error = {"code": code, "message": message}
    error.update(details)
    return error


class WellspringStateError(ValueError):
    """Raised when an isolated Wellspring contract cannot be safely built or read."""

    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = deepcopy(list(errors or []))


__all__ = [
    "PLAYER_WELLSPRING_STATE_SCHEMA_VERSION",
    "WELLSPRING_RESOURCE_SUMMARY_SCHEMA_VERSION",
    "WELLSPRING_RESOURCE_MODEL",
    "WELLSPRING_ZONE",
    "WELLSPRING_VISIBILITY_MODE",
    "WellspringStateError",
    "create_empty_player_wellspring_state",
    "create_player_wellspring_state",
    "validate_player_wellspring_state",
    "create_wellspring_resource_summary",
    "validate_wellspring_resource_summary",
    "get_wellspring_card_instance_ids",
]
