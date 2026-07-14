"""Structural Entity-to-Domain placement option contracts.

This module only projects source eligibility and own-Domain occupancy. It does
not implement full play legality, mutate state, or integrate with actions.
"""

from __future__ import annotations

from copy import deepcopy

try:
    from card_instance import card_instance_to_object_reference
except ModuleNotFoundError:
    from .card_instance import card_instance_to_object_reference

try:
    from domain_occupancy import (
        get_domain_position_occupancy,
        validate_player_domain_occupancy,
    )
except ModuleNotFoundError:
    from .domain_occupancy import (
        get_domain_position_occupancy,
        validate_player_domain_occupancy,
    )

try:
    from domain_position import (
        create_domain_position_id,
        validate_player_domain_topology,
    )
except ModuleNotFoundError:
    from .domain_position import (
        create_domain_position_id,
        validate_player_domain_topology,
    )

try:
    from state_invariants import validate_state_invariants
except ModuleNotFoundError:
    from tools.ai_vs_ai.state_invariants import validate_state_invariants


ENTITY_DOMAIN_PLACEMENT_OPTION_SCHEMA_VERSION = (
    "minimal-entity-domain-placement-option-v0"
)
ENTITY_DOMAIN_PLACEMENT_OPTIONS_SCHEMA_VERSION = (
    "minimal-entity-domain-placement-options-v0"
)
ENTITY_DOMAIN_PLACEMENT_MODEL = "structural-entity-domain-placement-v0"
PLACEMENT_VALIDATION_SCOPE = "source_type_zone_and_target_occupancy_only_v0"
SUPPORTED_TARGET_POSITION_TYPES = ("horizon", "zenith")

RUNTIME_CARD_TYPE_FIELD = "card_type"
CARD_TYPE_LOOKUP_GROUP = "card_type"
ENTITY_CANONICAL_CARD_TYPE = "entity"

UNCHECKED_REQUIREMENTS = (
    "turn_and_priority",
    "phase_and_timing",
    "magnitude_threshold",
    "aura_payment",
    "card_text_position_restrictions",
    "continuous_effect_modifiers",
    "per_turn_play_limits",
    "ability_support",
    "entry_state",
    "summoning_sickness",
)

INELIGIBLE_SOURCE_REASONS = (
    "source_not_controlled_by_player",
    "source_not_in_player_hand",
    "source_zone_not_hand",
    "source_card_type_not_entity",
)

_REQUIRED_OPTION_FIELDS = (
    "schema_version",
    "contract_type",
    "option_id",
    "player_id",
    "source_card_instance_id",
    "source_zone",
    "target_player_id",
    "target_position_id",
    "target_current_index",
    "target_position_type",
    "target_row",
    "target_occupancy_state",
    "structurally_available",
    "unavailable_reason",
    "metadata",
)

_REQUIRED_OPTIONS_FIELDS = (
    "schema_version",
    "contract_type",
    "placement_model",
    "validation_scope",
    "match_id",
    "state_version",
    "player_id",
    "source_card_instance_id",
    "source_card",
    "source_card_type",
    "source_eligible",
    "reason",
    "target_player_id",
    "target_option_count",
    "structurally_available_count",
    "structurally_unavailable_count",
    "options",
    "unchecked_requirements",
    "metadata",
)

_REQUIRED_OPTION_METADATA = {
    "source": "python.engine.entity_domain_placement",
    "placement_model": ENTITY_DOMAIN_PLACEMENT_MODEL,
    "capacity_required": 1,
    "target_occupancy_checked": True,
    "full_play_legality": False,
}

_REQUIRED_OPTIONS_METADATA = {
    "source": "python.engine.entity_domain_placement",
    "full_play_legality": False,
    "state_mutation": False,
    "legal_action_integration": "not_implemented",
    "play_card_integration": "not_implemented",
    "entity_entry_state_model": "not_implemented",
    "card_text_restrictions_checked": False,
    "payment_checked": False,
    "timing_checked": False,
}

_FORBIDDEN_FULL_LEGALITY_FIELDS = {
    "payment_valid",
    "timing_valid",
    "action_request",
    "events",
    "state_after",
}

_SOURCE_LOCATION_INVARIANT_CODES = {
    "CARD_INSTANCE_ZONE_MISMATCH",
    "CARD_INSTANCE_ZONE_INDEX_MISMATCH",
    "CARD_INSTANCE_ORPHANED",
}


class EntityDomainPlacementError(ValueError):
    """Raised when a placement query cannot be projected safely."""

    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = deepcopy(list(errors or []))


def create_entity_domain_placement_option(
    player_id,
    source_card_instance_id,
    target_player_id,
    target_position_id,
    target_current_index,
    target_position_type,
    target_occupancy_state,
):
    """Create one detached structural placement option."""

    structurally_available = target_occupancy_state == "empty"
    unavailable_reason = None if structurally_available else "position_occupied"
    record = {
        "schema_version": ENTITY_DOMAIN_PLACEMENT_OPTION_SCHEMA_VERSION,
        "contract_type": "entity_domain_placement_option",
        "option_id": "place_%s_to_%s" % (source_card_instance_id, target_position_id),
        "player_id": player_id,
        "source_card_instance_id": source_card_instance_id,
        "source_zone": "hand",
        "target_player_id": target_player_id,
        "target_position_id": target_position_id,
        "target_current_index": target_current_index,
        "target_position_type": target_position_type,
        "target_row": target_position_type,
        "target_occupancy_state": target_occupancy_state,
        "structurally_available": structurally_available,
        "unavailable_reason": unavailable_reason,
        "metadata": deepcopy(_REQUIRED_OPTION_METADATA),
    }
    validation = validate_entity_domain_placement_option(record)
    if not validation["valid"]:
        raise EntityDomainPlacementError(
            "Cannot create invalid Entity Domain placement option.",
            validation["errors"],
        )
    return record


def list_structural_entity_domain_placement_options(
    state,
    runtime_package,
    player_id,
    card_instance_id,
):
    """Project structural own-Domain targets for one known card instance."""

    player = _get_player_or_raise(state, player_id)
    source_record = _get_card_instance_or_raise(state, card_instance_id)
    card_definition = _get_runtime_card_or_raise(runtime_package, source_record.get("card_id"))
    source_card_type = _resolve_canonical_card_type(runtime_package, card_definition)
    topology = _get_topology_or_raise(state, player_id)
    occupancy = _get_occupancy_or_raise(state, player_id)

    topology_validation = validate_player_domain_topology(topology)
    if not topology_validation.get("valid"):
        raise EntityDomainPlacementError(
            "Invalid Domain topology for player_id: %s" % player_id,
            topology_validation.get("errors", []),
        )
    occupancy_validation = validate_player_domain_occupancy(occupancy, topology)
    if not occupancy_validation.get("valid"):
        raise EntityDomainPlacementError(
            "Invalid Domain occupancy for player_id: %s" % player_id,
            occupancy_validation.get("errors", []),
        )

    reason = _source_ineligibility_reason(
        player,
        source_record,
        player_id,
        card_instance_id,
        source_card_type,
    )
    invariant_errors = validate_state_invariants(state, runtime_package)
    invariant_errors = _filter_source_location_invariants(
        invariant_errors,
        reason,
        card_instance_id,
    )
    if invariant_errors:
        raise EntityDomainPlacementError("Invalid MatchState for placement query.", invariant_errors)

    options = []
    if reason is None:
        options = _create_options_from_topology_and_occupancy(
            topology,
            occupancy,
            player_id,
            card_instance_id,
        )

    available_count = sum(
        1 for option in options if option.get("structurally_available") is True
    )
    record = {
        "schema_version": ENTITY_DOMAIN_PLACEMENT_OPTIONS_SCHEMA_VERSION,
        "contract_type": "entity_domain_placement_options",
        "placement_model": ENTITY_DOMAIN_PLACEMENT_MODEL,
        "validation_scope": PLACEMENT_VALIDATION_SCOPE,
        "match_id": getattr(state, "match_id", None),
        "state_version": getattr(state, "state_version", None),
        "player_id": player_id,
        "source_card_instance_id": card_instance_id,
        "source_card": card_instance_to_object_reference(source_record),
        "source_card_type": source_card_type,
        "source_eligible": reason is None,
        "reason": reason,
        "target_player_id": player_id,
        "target_option_count": len(options),
        "structurally_available_count": available_count,
        "structurally_unavailable_count": len(options) - available_count,
        "options": options,
        "unchecked_requirements": list(UNCHECKED_REQUIREMENTS),
        "metadata": deepcopy(_REQUIRED_OPTIONS_METADATA),
    }
    validation = validate_entity_domain_placement_options(record)
    if not validation["valid"]:
        raise EntityDomainPlacementError(
            "Generated Entity Domain placement options failed validation.",
            validation["errors"],
        )
    return record


def validate_entity_domain_placement_option(record):
    """Validate one option and return diagnostics instead of raising."""

    errors = []
    normalized = record if isinstance(record, dict) else {}
    if not isinstance(record, dict):
        errors.append(_error("OPTION_NOT_DICT", "placement option must be a dict."))

    _require_fields(normalized, _REQUIRED_OPTION_FIELDS, errors)
    if normalized.get("schema_version") != ENTITY_DOMAIN_PLACEMENT_OPTION_SCHEMA_VERSION:
        errors.append(
            _error(
                "FIELD_EMPTY",
                "schema_version must identify the structural placement option contract.",
                field="schema_version",
            )
        )
    if normalized.get("contract_type") != "entity_domain_placement_option":
        errors.append(
            _error(
                "CONTRACT_TYPE_INVALID",
                "contract_type must be entity_domain_placement_option.",
            )
        )
    for field_name in (
        "option_id",
        "player_id",
        "source_card_instance_id",
        "target_player_id",
        "target_position_id",
    ):
        if not _is_non_empty_string(normalized.get(field_name)):
            errors.append(_error("FIELD_EMPTY", "field must be non-empty.", field=field_name))

    if normalized.get("source_zone") != "hand":
        errors.append(_error("SOURCE_ZONE_INVALID", "source_zone must be hand."))
    if normalized.get("target_player_id") != normalized.get("player_id"):
        errors.append(
            _error("TARGET_PLAYER_MISMATCH", "target player must match source player.")
        )

    current_index = normalized.get("target_current_index")
    current_index_valid = _is_integer(current_index) and 1 <= current_index <= 6
    if not current_index_valid:
        errors.append(
            _error(
                "CURRENT_INDEX_INVALID",
                "target_current_index must be an integer from 1 through 6.",
            )
        )
    position_type = normalized.get("target_position_type")
    position_type_valid = position_type in SUPPORTED_TARGET_POSITION_TYPES
    if not position_type_valid:
        errors.append(
            _error(
                "TARGET_POSITION_TYPE_INVALID",
                "target_position_type must be horizon or zenith.",
            )
        )
    if position_type_valid and normalized.get("target_row") != position_type:
        errors.append(
            _error("TARGET_ROW_INVALID", "target_row must match target_position_type.")
        )

    player_id = normalized.get("player_id")
    if _is_non_empty_string(player_id) and current_index_valid and position_type_valid:
        expected_position_id = create_domain_position_id(
            player_id,
            current_index,
            position_type,
        )
        if normalized.get("target_position_id") != expected_position_id:
            errors.append(
                _error(
                    "TARGET_POSITION_ID_MISMATCH",
                    "target_position_id must be canonical.",
                    expected=expected_position_id,
                )
            )

    occupancy_state = normalized.get("target_occupancy_state")
    if occupancy_state not in ("empty", "occupied"):
        errors.append(
            _error(
                "TARGET_OCCUPANCY_STATE_INVALID",
                "target_occupancy_state must be empty or occupied.",
            )
        )
    structurally_available = normalized.get("structurally_available")
    if not isinstance(structurally_available, bool):
        errors.append(
            _error(
                "STRUCTURAL_AVAILABILITY_INVALID",
                "structurally_available must be a bool.",
            )
        )
    elif occupancy_state == "empty" and structurally_available is not True:
        errors.append(
            _error(
                "STRUCTURAL_AVAILABILITY_INVALID",
                "empty targets must be structurally available.",
            )
        )
    elif occupancy_state == "occupied" and structurally_available is not False:
        errors.append(
            _error(
                "STRUCTURAL_AVAILABILITY_INVALID",
                "occupied targets must be structurally unavailable.",
            )
        )

    expected_reason = "position_occupied" if occupancy_state == "occupied" else None
    if occupancy_state in ("empty", "occupied") and normalized.get("unavailable_reason") != expected_reason:
        errors.append(
            _error(
                "UNAVAILABLE_REASON_INVALID",
                "unavailable_reason must match target occupancy.",
                expected=expected_reason,
            )
        )

    source_id = normalized.get("source_card_instance_id")
    target_id = normalized.get("target_position_id")
    if _is_non_empty_string(source_id) and _is_non_empty_string(target_id):
        expected_option_id = "place_%s_to_%s" % (source_id, target_id)
        if normalized.get("option_id") != expected_option_id:
            errors.append(
                _error(
                    "OPTION_ID_MISMATCH",
                    "option_id must derive from source and target IDs.",
                    expected=expected_option_id,
                )
            )

    _validate_metadata(
        normalized.get("metadata"),
        _REQUIRED_OPTION_METADATA,
        errors,
    )
    return {"valid": len(errors) == 0, "errors": errors}


def validate_entity_domain_placement_options(record):
    """Validate the complete structural placement-options contract."""

    errors = []
    normalized = record if isinstance(record, dict) else {}
    if not isinstance(record, dict):
        errors.append(_error("OPTIONS_NOT_DICT", "placement options must be a dict."))

    _require_fields(normalized, _REQUIRED_OPTIONS_FIELDS, errors)
    if normalized.get("schema_version") != ENTITY_DOMAIN_PLACEMENT_OPTIONS_SCHEMA_VERSION:
        errors.append(
            _error(
                "FIELD_MISSING",
                "schema_version must identify the placement-options contract.",
                field="schema_version",
            )
        )
    if normalized.get("contract_type") != "entity_domain_placement_options":
        errors.append(
            _error(
                "CONTRACT_TYPE_INVALID",
                "contract_type must be entity_domain_placement_options.",
            )
        )
    if normalized.get("placement_model") != ENTITY_DOMAIN_PLACEMENT_MODEL:
        errors.append(_error("PLACEMENT_MODEL_INVALID", "placement_model is invalid."))
    if normalized.get("validation_scope") != PLACEMENT_VALIDATION_SCOPE:
        errors.append(_error("VALIDATION_SCOPE_INVALID", "validation_scope is invalid."))
    for field_name in (
        "match_id",
        "player_id",
        "source_card_instance_id",
        "source_card_type",
        "target_player_id",
    ):
        if not _is_non_empty_string(normalized.get(field_name)):
            errors.append(_error("FIELD_MISSING", "field must be non-empty.", field=field_name))

    state_version = normalized.get("state_version")
    if not _is_non_negative_integer(state_version):
        errors.append(
            _error("FIELD_MISSING", "state_version must be a non-negative integer.")
        )
    source_eligible = normalized.get("source_eligible")
    if not isinstance(source_eligible, bool):
        errors.append(
            _error("SOURCE_ELIGIBILITY_INVALID", "source_eligible must be a bool.")
        )
    reason = normalized.get("reason")
    if source_eligible is True and reason is not None:
        errors.append(_error("SOURCE_REASON_INVALID", "eligible source reason must be null."))
    elif source_eligible is False and reason not in INELIGIBLE_SOURCE_REASONS:
        errors.append(
            _error("SOURCE_REASON_INVALID", "ineligible source reason is invalid.")
        )
    if normalized.get("target_player_id") != normalized.get("player_id"):
        errors.append(
            _error("TARGET_PLAYER_MISMATCH", "target_player_id must match player_id.")
        )

    _validate_source_object_reference(normalized, errors)
    if source_eligible is True and normalized.get("source_card_type") != ENTITY_CANONICAL_CARD_TYPE:
        errors.append(
            _error(
                "SOURCE_CARD_TYPE_INVALID",
                "eligible source_card_type must be canonical entity.",
            )
        )

    options = normalized.get("options")
    if not isinstance(options, list):
        errors.append(_error("OPTIONS_INVALID", "options must be a list."))
        options = []

    counts = {}
    for field_name in (
        "target_option_count",
        "structurally_available_count",
        "structurally_unavailable_count",
    ):
        value = normalized.get(field_name)
        if not _is_non_negative_integer(value):
            errors.append(
                _error("COUNT_MISMATCH", "count must be a non-negative integer.", field=field_name)
            )
        counts[field_name] = value

    if _is_non_negative_integer(counts["target_option_count"]):
        if counts["target_option_count"] != len(options):
            errors.append(
                _error(
                    "TARGET_OPTION_COUNT_INVALID",
                    "target_option_count must match options length.",
                )
            )

    option_ids = []
    target_position_ids = []
    available_count = 0
    unavailable_count = 0
    top_player_id = normalized.get("player_id")
    top_source_id = normalized.get("source_card_instance_id")
    for option_index, option in enumerate(options):
        validation = validate_entity_domain_placement_option(option)
        if not validation["valid"]:
            errors.append(
                _error(
                    "OPTION_RECORD_INVALID",
                    "option failed its contract validation.",
                    option_index=option_index,
                    option_errors=validation["errors"],
                )
            )
        if not isinstance(option, dict):
            continue
        option_ids.append(option.get("option_id"))
        target_position_ids.append(option.get("target_position_id"))
        if option.get("player_id") != top_player_id:
            errors.append(
                _error("OPTION_RECORD_INVALID", "option player_id must match contract player_id.")
            )
        if option.get("target_player_id") != top_player_id:
            errors.append(
                _error("OPTION_RECORD_INVALID", "option target must be the query player's Domain.")
            )
        if option.get("source_card_instance_id") != top_source_id:
            errors.append(
                _error("OPTION_RECORD_INVALID", "option source must match contract source.")
            )
        if option.get("structurally_available") is True:
            available_count += 1
        elif option.get("structurally_available") is False:
            unavailable_count += 1

    duplicate_option_ids = _duplicates(option_ids)
    if duplicate_option_ids:
        errors.append(
            _error("OPTION_ID_DUPLICATE", "option IDs must be unique.", values=duplicate_option_ids)
        )
    duplicate_target_ids = _duplicates(target_position_ids)
    if duplicate_target_ids:
        errors.append(
            _error(
                "TARGET_POSITION_ID_DUPLICATE",
                "target position IDs must be unique.",
                values=duplicate_target_ids,
            )
        )

    if source_eligible is True:
        if len(options) != 12:
            errors.append(
                _error("TARGET_OPTION_COUNT_INVALID", "eligible source must have twelve options.")
            )
        expected_targets = _expected_target_position_ids(top_player_id)
        if set(target_position_ids) != expected_targets:
            errors.append(
                _error(
                    "TARGET_POSITION_SET_INVALID",
                    "eligible options must cover own horizon and zenith positions exactly.",
                )
            )
    elif source_eligible is False:
        if options:
            errors.append(_error("OPTIONS_INVALID", "ineligible source options must be empty."))
        if any(value != 0 for value in counts.values() if _is_non_negative_integer(value)):
            errors.append(_error("COUNT_MISMATCH", "ineligible source counts must be zero."))

    if (
        _is_non_negative_integer(counts["structurally_available_count"])
        and counts["structurally_available_count"] != available_count
    ):
        errors.append(_error("COUNT_MISMATCH", "available count does not match options."))
    if (
        _is_non_negative_integer(counts["structurally_unavailable_count"])
        and counts["structurally_unavailable_count"] != unavailable_count
    ):
        errors.append(_error("COUNT_MISMATCH", "unavailable count does not match options."))
    if source_eligible is True and available_count + unavailable_count != 12:
        errors.append(_error("COUNT_MISMATCH", "eligible option counts must total twelve."))

    unchecked = normalized.get("unchecked_requirements")
    if (
        not isinstance(unchecked, list)
        or any(not _is_non_empty_string(value) for value in unchecked)
        or len(unchecked) != len(set(unchecked))
        or not set(UNCHECKED_REQUIREMENTS).issubset(set(unchecked))
    ):
        errors.append(
            _error(
                "UNCHECKED_REQUIREMENTS_INVALID",
                "unchecked_requirements must include every deferred rule check.",
            )
        )

    _validate_metadata(
        normalized.get("metadata"),
        _REQUIRED_OPTIONS_METADATA,
        errors,
    )
    forbidden = _find_forbidden_full_legality_claims(normalized)
    if forbidden:
        errors.append(
            _error(
                "FULL_LEGALITY_CLAIM_INVALID",
                "structural options cannot claim full play legality.",
                fields=forbidden,
            )
        )
    return {"valid": len(errors) == 0, "errors": errors}


def _create_options_from_topology_and_occupancy(
    topology,
    occupancy,
    player_id,
    card_instance_id,
):
    positions = [
        position
        for position in topology.get("positions", [])
        if isinstance(position, dict)
        and position.get("player_id") == player_id
        and position.get("position_type") in SUPPORTED_TARGET_POSITION_TYPES
        and position.get("area") == "domain"
    ]
    type_order = {value: index for index, value in enumerate(SUPPORTED_TARGET_POSITION_TYPES)}
    positions.sort(
        key=lambda position: (
            position.get("current_index"),
            type_order[position.get("position_type")],
        )
    )
    options = []
    for position in positions:
        slot = get_domain_position_occupancy(occupancy, position["position_id"])
        options.append(
            create_entity_domain_placement_option(
                player_id=player_id,
                source_card_instance_id=card_instance_id,
                target_player_id=player_id,
                target_position_id=position["position_id"],
                target_current_index=position["current_index"],
                target_position_type=position["position_type"],
                target_occupancy_state=slot["occupancy_state"],
            )
        )
    return options


def _resolve_canonical_card_type(runtime_package, card_definition):
    if not isinstance(card_definition, dict):
        _raise_builder_error(
            "RUNTIME_CARD_DEFINITION_INVALID",
            "runtime card definition must be a dict.",
        )
    raw_card_type = card_definition.get(RUNTIME_CARD_TYPE_FIELD)
    if not _is_non_empty_string(raw_card_type):
        _raise_builder_error(
            "RUNTIME_CARD_TYPE_MISSING",
            "runtime card definition is missing card_type.",
        )
    lookups = getattr(runtime_package, "lookups", None)
    if not isinstance(lookups, list):
        _raise_builder_error(
            "RUNTIME_CARD_TYPE_LOOKUPS_INVALID",
            "runtime package lookups must be a list.",
        )
    canonical_values = {
        lookup.get("canonical_value")
        for lookup in lookups
        if isinstance(lookup, dict)
        and lookup.get("lookup_group") == CARD_TYPE_LOOKUP_GROUP
        and lookup.get("status") == "active"
        and lookup.get("value") == raw_card_type
        and _is_non_empty_string(lookup.get("canonical_value"))
    }
    if len(canonical_values) != 1:
        _raise_builder_error(
            "RUNTIME_CARD_TYPE_UNRESOLVED",
            "runtime card_type has no unambiguous active canonical mapping.",
            card_type=raw_card_type,
        )
    return next(iter(canonical_values))


def _source_ineligibility_reason(
    player,
    source_record,
    player_id,
    card_instance_id,
    source_card_type,
):
    if source_record.get("controller_player_id") != player_id:
        return "source_not_controlled_by_player"
    if source_record.get("zone") != "hand":
        return "source_zone_not_hand"
    if card_instance_id not in list(getattr(player, "hand_card_instance_ids", []) or []):
        return "source_not_in_player_hand"
    if source_card_type != ENTITY_CANONICAL_CARD_TYPE:
        return "source_card_type_not_entity"
    return None


def _filter_source_location_invariants(errors, reason, card_instance_id):
    """Keep explicit source location mismatch as ineligibility, not state failure."""

    if reason not in ("source_not_in_player_hand", "source_zone_not_hand"):
        return list(errors or [])
    return [
        error
        for error in list(errors or [])
        if not (
            isinstance(error, dict)
            and error.get("code") in _SOURCE_LOCATION_INVARIANT_CODES
            and error.get("card_instance_id") == card_instance_id
        )
    ]


def _get_player_or_raise(state, player_id):
    try:
        player = state.get_player(player_id)
    except Exception as exc:
        raise EntityDomainPlacementError(
            "Unknown player_id: %s" % player_id,
            [_error("PLAYER_UNKNOWN", "player_id does not exist.", player_id=player_id)],
        ) from exc
    return player


def _get_card_instance_or_raise(state, card_instance_id):
    try:
        source_record = state.get_card_instance(card_instance_id)
    except Exception as exc:
        raise EntityDomainPlacementError(
            "Unknown card_instance_id: %s" % card_instance_id,
            [
                _error(
                    "CARD_INSTANCE_UNKNOWN",
                    "card_instance_id does not exist.",
                    card_instance_id=card_instance_id,
                )
            ],
        ) from exc
    if not isinstance(source_record, dict):
        _raise_builder_error(
            "CARD_INSTANCE_INVALID",
            "source card instance must be a record dict.",
            card_instance_id=card_instance_id,
        )
    return source_record


def _get_runtime_card_or_raise(runtime_package, card_id):
    if not _is_non_empty_string(card_id):
        _raise_builder_error("CARD_ID_INVALID", "source card_id must be non-empty.")
    try:
        card_definition = runtime_package.get_card(card_id)
    except Exception as exc:
        raise EntityDomainPlacementError(
            "Missing runtime card definition: %s" % card_id,
            [
                _error(
                    "RUNTIME_CARD_DEFINITION_MISSING",
                    "source card_id does not exist in runtime package.",
                    card_id=card_id,
                )
            ],
        ) from exc
    return card_definition


def _get_topology_or_raise(state, player_id):
    try:
        return state.get_domain_topology(player_id)
    except Exception as exc:
        raise EntityDomainPlacementError(
            "Missing Domain topology for player_id: %s" % player_id,
            [_error("DOMAIN_TOPOLOGY_MISSING", "player topology is unavailable.")],
        ) from exc


def _get_occupancy_or_raise(state, player_id):
    try:
        return state.get_domain_occupancy(player_id)
    except Exception as exc:
        raise EntityDomainPlacementError(
            "Missing Domain occupancy for player_id: %s" % player_id,
            [_error("DOMAIN_OCCUPANCY_MISSING", "player occupancy is unavailable.")],
        ) from exc


def _validate_source_object_reference(record, errors):
    source_card = record.get("source_card")
    source_eligible = record.get("source_eligible")
    if source_card is None and source_eligible is not True:
        return
    if not isinstance(source_card, dict):
        errors.append(
            _error("SOURCE_OBJECT_REFERENCE_INVALID", "source_card must be an ObjectReference.")
        )
        return
    expected_source_id = record.get("source_card_instance_id")
    expected_values = {
        "contract_type": "object_reference",
        "object_type": "card_instance",
        "object_id": expected_source_id,
        "card_instance_id": expected_source_id,
    }
    if any(source_card.get(key) != value for key, value in expected_values.items()):
        errors.append(
            _error(
                "SOURCE_OBJECT_REFERENCE_INVALID",
                "source_card identity does not match the placement source.",
            )
        )
    if source_eligible is True:
        if source_card.get("zone") != "hand":
            errors.append(
                _error("SOURCE_OBJECT_REFERENCE_INVALID", "eligible source must reference hand zone.")
            )
        if source_card.get("controller_player_id") != record.get("player_id"):
            errors.append(
                _error(
                    "SOURCE_OBJECT_REFERENCE_INVALID",
                    "eligible source controller must match player_id.",
                )
            )


def _expected_target_position_ids(player_id):
    if not _is_non_empty_string(player_id):
        return set()
    return {
        create_domain_position_id(player_id, current_index, position_type)
        for current_index in range(1, 7)
        for position_type in SUPPORTED_TARGET_POSITION_TYPES
    }


def _validate_metadata(metadata, expected, errors):
    if not isinstance(metadata, dict):
        errors.append(_error("METADATA_INVALID", "metadata must be a dict."))
        return
    for field_name, expected_value in expected.items():
        if metadata.get(field_name) != expected_value:
            errors.append(
                _error(
                    "METADATA_INVALID",
                    "metadata value is invalid.",
                    field="metadata.%s" % field_name,
                    expected=expected_value,
                    actual=metadata.get(field_name),
                )
            )


def _find_forbidden_full_legality_claims(value, path="options"):
    matches = []
    if isinstance(value, dict):
        for key, nested in value.items():
            nested_path = "%s.%s" % (path, key)
            if key in _FORBIDDEN_FULL_LEGALITY_FIELDS:
                matches.append(nested_path)
            elif key in ("legal", "playable") and nested is True:
                matches.append(nested_path)
            matches.extend(_find_forbidden_full_legality_claims(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            matches.extend(
                _find_forbidden_full_legality_claims(nested, "%s[%s]" % (path, index))
            )
    return matches


def _require_fields(record, field_names, errors):
    for field_name in field_names:
        if field_name not in record:
            errors.append(_error("FIELD_MISSING", "required field is missing.", field=field_name))


def _duplicates(values):
    seen = set()
    duplicates = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates, key=lambda value: str(value))


def _is_non_empty_string(value):
    return isinstance(value, str) and value.strip() != ""


def _is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _is_non_negative_integer(value):
    return _is_integer(value) and value >= 0


def _raise_builder_error(code, message, **details):
    raise EntityDomainPlacementError(message, [_error(code, message, **details)])


def _error(code, message, **details):
    error = {"code": code, "message": message}
    error.update(details)
    return error


__all__ = [
    "ENTITY_DOMAIN_PLACEMENT_OPTION_SCHEMA_VERSION",
    "ENTITY_DOMAIN_PLACEMENT_OPTIONS_SCHEMA_VERSION",
    "ENTITY_DOMAIN_PLACEMENT_MODEL",
    "PLACEMENT_VALIDATION_SCOPE",
    "SUPPORTED_TARGET_POSITION_TYPES",
    "RUNTIME_CARD_TYPE_FIELD",
    "ENTITY_CANONICAL_CARD_TYPE",
    "UNCHECKED_REQUIREMENTS",
    "EntityDomainPlacementError",
    "create_entity_domain_placement_option",
    "list_structural_entity_domain_placement_options",
    "validate_entity_domain_placement_option",
    "validate_entity_domain_placement_options",
]
