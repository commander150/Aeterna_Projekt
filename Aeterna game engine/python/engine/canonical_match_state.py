"""Language-independent canonical projection of the minimal MatchState.

The v1 top-level contract is a required-value object with these fields:
``schema_version``, ``contract_type``, ``match_id``, ``state_version``,
``turn_number``, ``phase``, ``active_player_id``, ``priority_player_id``,
``priority_model``, ``players``, ``card_instances``, ``domain_topologies``,
``domain_occupancies``, ``event_log``, and ``semantic_metadata``.

Every nested field is classified in ``FIELD_POLICIES`` as required with a
value, required but nullable, or optional and omitted. Lists with gameplay
meaning retain their authoritative order. Object-key ordering belongs to the
canonical JSON writer, not this projection.

Internal ``metadata`` dictionaries are never copied wholesale. Each contract
has an explicit semantic allowlist; known implementation details are omitted,
and every unknown key is rejected so contract growth cannot become silent.
"""

from __future__ import annotations

import math

try:
    from card_instance import validate_card_instance_record
    from domain_occupancy import validate_player_domain_occupancy
    from domain_position import validate_player_domain_topology
    from engine_event import validate_engine_event_envelope
    from turn_transition import validate_turn_transition_record
    from zone_move import validate_zone_move_record
except ModuleNotFoundError:
    from .card_instance import validate_card_instance_record
    from .domain_occupancy import validate_player_domain_occupancy
    from .domain_position import validate_player_domain_topology
    from .engine_event import validate_engine_event_envelope
    from .turn_transition import validate_turn_transition_record
    from .zone_move import validate_zone_move_record

try:
    from state_invariants import validate_state_invariants
except ModuleNotFoundError:
    from tools.ai_vs_ai.state_invariants import validate_state_invariants


CANONICAL_MATCH_STATE_SCHEMA_VERSION = "aeterna-canonical-match-state-v1"
CANONICAL_MATCH_STATE_CONTRACT_TYPE = "canonical_match_state"
MINIMAL_PRIORITY_MODEL = "minimal_priority_model_v1"


FIELD_POLICIES = {
    "canonical_match_state": {
        "required_value": (
            "schema_version",
            "contract_type",
            "match_id",
            "state_version",
            "turn_number",
            "phase",
            "active_player_id",
            "priority_player_id",
            "priority_model",
            "players",
            "card_instances",
            "domain_topologies",
            "domain_occupancies",
            "event_log",
            "semantic_metadata",
        ),
        "required_nullable": (),
        "optional_omitted": (),
    },
    "player": {
        "required_value": (
            "player_id",
            "deck_id",
            "deck_card_instance_ids",
            "hand_card_instance_ids",
            "discard_card_instance_ids",
        ),
        "required_nullable": (),
        "optional_omitted": (),
    },
    "card_instance": {
        "required_value": (
            "schema_version",
            "contract_type",
            "card_instance_id",
            "card_id",
            "owner_player_id",
            "zone",
            "visibility",
            "created_sequence",
            "zone_sequence",
            "semantic_metadata",
        ),
        "required_nullable": (
            "controller_player_id",
            "zone_index",
            "activity_state",
        ),
        "optional_omitted": (),
    },
    "domain_topology_entry": {
        "required_value": ("player_id", "topology"),
        "required_nullable": (),
        "optional_omitted": (),
    },
    "domain_topology": {
        "required_value": (
            "schema_version",
            "contract_type",
            "player_id",
            "current_count",
            "row_count",
            "rows",
            "currents",
            "positions",
            "semantic_metadata",
        ),
        "required_nullable": (),
        "optional_omitted": (),
    },
    "domain_current": {
        "required_value": (
            "current_id",
            "current_index",
            "horizon_position_id",
            "zenith_position_id",
            "seal_position_id",
            "semantic_metadata",
        ),
        "required_nullable": (),
        "optional_omitted": (),
    },
    "domain_position": {
        "required_value": (
            "schema_version",
            "contract_type",
            "position_id",
            "player_id",
            "area",
            "current_index",
            "position_type",
            "linked_current_id",
            "visibility",
            "semantic_metadata",
        ),
        "required_nullable": ("row",),
        "optional_omitted": (),
    },
    "domain_occupancy_entry": {
        "required_value": ("player_id", "occupancy"),
        "required_nullable": (),
        "optional_omitted": (),
    },
    "domain_occupancy": {
        "required_value": (
            "schema_version",
            "contract_type",
            "player_id",
            "topology_schema_version",
            "topology_model",
            "occupancy_model",
            "slot_count",
            "slots",
            "semantic_metadata",
        ),
        "required_nullable": (),
        "optional_omitted": (),
    },
    "domain_occupancy_slot": {
        "required_value": (
            "schema_version",
            "contract_type",
            "position_id",
            "player_id",
            "current_index",
            "position_type",
            "row",
            "occupancy_state",
            "visibility",
            "semantic_metadata",
        ),
        "required_nullable": (
            "occupant_object_type",
            "occupant_card_instance_id",
        ),
        "optional_omitted": (),
    },
    "engine_event": {
        "required_value": (
            "schema_version",
            "contract_type",
            "event_index",
            "event_sequence",
            "event_type",
            "turn_number",
            "state_version",
            "payload",
            "semantic_metadata",
        ),
        "required_nullable": ("player_id", "action_type"),
        "optional_omitted": (),
    },
    "zone_move_payload": {
        "required_value": (
            "schema_version",
            "contract_type",
            "event_type",
            "card_instance_id",
            "card_id",
            "owner_player_id",
            "from_zone",
            "to_zone",
            "source_action_id",
            "source_action_type",
            "state_version",
            "event_sequence",
            "visibility_before",
            "visibility_after",
            "semantic_metadata",
        ),
        "required_nullable": (
            "controller_player_id",
            "from_zone_index",
            "to_zone_index",
        ),
        "optional_omitted": (),
    },
    "turn_transition_payload": {
        "required_value": (
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
            "semantic_metadata",
        ),
        "required_nullable": (),
        "optional_omitted": (),
    },
}


CARD_INSTANCE_SEMANTIC_METADATA = frozenset({"creation_reason", "initial_zone"})
DOMAIN_TOPOLOGY_SEMANTIC_METADATA = frozenset(
    {
        "topology_model",
        "static_topology",
        "domain_scope",
        "full_play_area_model",
        "occupancy_model",
        "four_current_variant_active",
    }
)
DOMAIN_CURRENT_SEMANTIC_METADATA = frozenset({"positionally_linked_seal", "ordered"})
DOMAIN_POSITION_SEMANTIC_METADATA = frozenset(
    {"topology_model", "current_count", "static_topology", "occupancy_model"}
)
DOMAIN_OCCUPANCY_SEMANTIC_METADATA = frozenset(
    {
        "static_topology_reference",
        "slot_capacity",
        "seal_state_model",
        "mutation_api",
        "play_card_integration",
        "match_state_integration",
        "four_current_variant_active",
    }
)
DOMAIN_OCCUPANCY_SLOT_SEMANTIC_METADATA = frozenset(
    {
        "occupancy_model",
        "capacity",
        "topology_model",
        "mutation_api",
        "gameplay_integration",
        "seal_position_supported",
    }
)
ZONE_MOVE_SEMANTIC_METADATA = frozenset(
    {"semantic_event_type", "zone_operation", "applied"}
)
TURN_TRANSITION_SEMANTIC_METADATA = frozenset(
    {"semantic_event_type", "turn_model", "applied"}
)
ENGINE_EVENT_SEMANTIC_METADATA = frozenset()

IMPLEMENTATION_SPECIFIC_METADATA = frozenset(
    {
        "source",
        "source_module",
        "authority",
        "runtime_decision",
        "module",
        "component",
        "class",
        "class_name",
        "function",
        "function_name",
        "build",
        "build_id",
        "build_path",
        "path",
    }
)


_PLAYER_FIELDS = frozenset(
    {
        "player_id",
        "deck_id",
        "deck_card_instance_ids",
        "hand_card_instance_ids",
        "discard_card_instance_ids",
    }
)
_CARD_INSTANCE_FIELDS = frozenset(
    {
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
        "activity_state",
        "metadata",
    }
)
_DOMAIN_TOPOLOGY_FIELDS = frozenset(
    {
        "schema_version",
        "contract_type",
        "player_id",
        "current_count",
        "row_count",
        "rows",
        "currents",
        "positions",
        "metadata",
    }
)
_DOMAIN_CURRENT_FIELDS = frozenset(
    {
        "current_id",
        "current_index",
        "horizon_position_id",
        "zenith_position_id",
        "seal_position_id",
        "metadata",
    }
)
_DOMAIN_POSITION_FIELDS = frozenset(
    {
        "schema_version",
        "contract_type",
        "position_id",
        "player_id",
        "area",
        "current_index",
        "position_type",
        "row",
        "linked_current_id",
        "visibility",
        "metadata",
    }
)
_DOMAIN_OCCUPANCY_FIELDS = frozenset(
    {
        "schema_version",
        "contract_type",
        "player_id",
        "topology_schema_version",
        "topology_model",
        "occupancy_model",
        "slot_count",
        "slots",
        "metadata",
    }
)
_DOMAIN_OCCUPANCY_SLOT_FIELDS = frozenset(
    {
        "schema_version",
        "contract_type",
        "position_id",
        "player_id",
        "current_index",
        "position_type",
        "row",
        "occupancy_state",
        "occupant_object_type",
        "occupant_card_instance_id",
        "visibility",
        "metadata",
    }
)
_ENGINE_EVENT_FIELDS = frozenset(
    {
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
    }
)
_ZONE_MOVE_FIELDS = frozenset(
    {
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
    }
)
_TURN_TRANSITION_FIELDS = frozenset(
    {
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
    }
)


class CanonicalMatchStateSerializationError(ValueError):
    """Raised when MatchState cannot be projected without semantic loss."""


def serialize_match_state(state, runtime_package=None):
    """Return a detached canonical DTO for one valid minimal MatchState."""

    _validate_match_state_shape(state)
    invariant_errors = validate_state_invariants(state, runtime_package)
    if invariant_errors:
        first = invariant_errors[0]
        raise CanonicalMatchStateSerializationError(
            "MatchState invariant validation failed: %s: %s"
            % (first.get("code", "unknown"), first.get("message", "invalid state"))
        )

    players = list(state.players)
    player_ids = [player.player_id for player in players]
    card_instances = [
        _serialize_card_instance(record, card_instance_id)
        for card_instance_id, record in sorted(
            state.card_instances.items(),
            key=lambda item: (item[1].get("created_sequence"), item[0]),
        )
    ]
    domain_topologies = [
        {
            "player_id": player_id,
            "topology": _serialize_domain_topology(
                state.domain_topologies[player_id], player_id
            ),
        }
        for player_id in player_ids
    ]
    domain_occupancies = [
        {
            "player_id": player_id,
            "occupancy": _serialize_domain_occupancy(
                state.domain_occupancies[player_id],
                state.domain_topologies[player_id],
                player_id,
            ),
        }
        for player_id in player_ids
    ]

    return {
        "schema_version": CANONICAL_MATCH_STATE_SCHEMA_VERSION,
        "contract_type": CANONICAL_MATCH_STATE_CONTRACT_TYPE,
        "match_id": state.match_id,
        "state_version": state.state_version,
        "turn_number": state.turn_number,
        "phase": state.phase,
        "active_player_id": state.active_player_id,
        "priority_player_id": state.active_player_id,
        "priority_model": MINIMAL_PRIORITY_MODEL,
        "players": [_serialize_player(player, index) for index, player in enumerate(players)],
        "card_instances": card_instances,
        "domain_topologies": domain_topologies,
        "domain_occupancies": domain_occupancies,
        "event_log": [_serialize_event(event, index) for index, event in enumerate(state.event_log)],
        "semantic_metadata": {},
    }


def _validate_match_state_shape(state):
    if state is None:
        raise CanonicalMatchStateSerializationError("MatchState is required.")
    for field_name in (
        "match_id",
        "state_version",
        "turn_number",
        "phase",
        "active_player_id",
        "players",
        "card_instances",
        "domain_topologies",
        "domain_occupancies",
        "event_log",
    ):
        if not hasattr(state, field_name):
            raise CanonicalMatchStateSerializationError(
                "MatchState is missing required field: %s" % field_name
            )
    for field_name in ("match_id", "phase", "active_player_id"):
        _require_non_empty_string(getattr(state, field_name), "MatchState.%s" % field_name)
    _require_integer(state.state_version, "MatchState.state_version", minimum=0)
    _require_integer(state.turn_number, "MatchState.turn_number", minimum=1)
    if not isinstance(state.players, list):
        raise CanonicalMatchStateSerializationError("MatchState.players must be a list.")
    if len(state.players) != 2:
        raise CanonicalMatchStateSerializationError("MatchState.players must contain exactly two players.")
    player_ids = []
    for index, player in enumerate(state.players):
        _validate_player_shape(player, index)
        player_ids.append(player.player_id)
    if len(set(player_ids)) != len(player_ids):
        raise CanonicalMatchStateSerializationError("MatchState player IDs must be distinct.")
    if state.active_player_id not in player_ids:
        raise CanonicalMatchStateSerializationError(
            "MatchState.active_player_id must identify a player."
        )
    for field_name in ("card_instances", "domain_topologies", "domain_occupancies"):
        if not isinstance(getattr(state, field_name), dict):
            raise CanonicalMatchStateSerializationError("MatchState.%s must be a dict." % field_name)
    if not isinstance(state.event_log, list):
        raise CanonicalMatchStateSerializationError("MatchState.event_log must be a list.")


def _validate_player_shape(player, index):
    if player is None:
        raise CanonicalMatchStateSerializationError("players[%s] is required." % index)
    actual_fields = set(vars(player)) if hasattr(player, "__dict__") else set()
    if actual_fields and actual_fields != _PLAYER_FIELDS:
        _raise_field_set_error("players[%s]" % index, actual_fields, _PLAYER_FIELDS)
    _require_non_empty_string(getattr(player, "player_id", None), "players[%s].player_id" % index)
    _require_non_empty_string(getattr(player, "deck_id", None), "players[%s].deck_id" % index)
    for field_name in (
        "deck_card_instance_ids",
        "hand_card_instance_ids",
        "discard_card_instance_ids",
    ):
        values = getattr(player, field_name, None)
        if not isinstance(values, list):
            raise CanonicalMatchStateSerializationError(
                "players[%s].%s must be a list." % (index, field_name)
            )
        for value_index, value in enumerate(values):
            _require_non_empty_string(
                value,
                "players[%s].%s[%s]" % (index, field_name, value_index),
            )


def _serialize_player(player, index):
    _validate_player_shape(player, index)
    return {
        "player_id": player.player_id,
        "deck_id": player.deck_id,
        "deck_card_instance_ids": list(player.deck_card_instance_ids),
        "hand_card_instance_ids": list(player.hand_card_instance_ids),
        "discard_card_instance_ids": list(player.discard_card_instance_ids),
    }


def _serialize_card_instance(record, registry_key):
    context = "card_instances[%s]" % registry_key
    _require_exact_dict(record, _CARD_INSTANCE_FIELDS, context)
    validation = validate_card_instance_record(record)
    _raise_contract_validation(context, validation)
    if record.get("card_instance_id") != registry_key:
        raise CanonicalMatchStateSerializationError(
            "%s card_instance_id does not match its registry key." % context
        )
    return {
        "schema_version": record["schema_version"],
        "contract_type": record["contract_type"],
        "card_instance_id": record["card_instance_id"],
        "card_id": record["card_id"],
        "owner_player_id": record["owner_player_id"],
        "controller_player_id": record["controller_player_id"],
        "zone": record["zone"],
        "zone_index": record["zone_index"],
        "visibility": record["visibility"],
        "created_sequence": record["created_sequence"],
        "zone_sequence": record["zone_sequence"],
        "activity_state": record["activity_state"],
        "semantic_metadata": _extract_semantic_metadata(
            record["metadata"], CARD_INSTANCE_SEMANTIC_METADATA, "%s.metadata" % context
        ),
    }


def _serialize_domain_topology(topology, player_id):
    context = "domain_topologies[%s]" % player_id
    _require_exact_dict(topology, _DOMAIN_TOPOLOGY_FIELDS, context)
    validation = validate_player_domain_topology(topology)
    _raise_contract_validation(context, validation)
    if topology.get("player_id") != player_id:
        raise CanonicalMatchStateSerializationError("%s player_id mismatch." % context)
    rows = _copy_string_list(topology["rows"], "%s.rows" % context)
    currents = [
        _serialize_domain_current(current, "%s.currents[%s]" % (context, index))
        for index, current in enumerate(topology["currents"])
    ]
    positions = [
        _serialize_domain_position(position, "%s.positions[%s]" % (context, index))
        for index, position in enumerate(topology["positions"])
    ]
    return {
        "schema_version": topology["schema_version"],
        "contract_type": topology["contract_type"],
        "player_id": topology["player_id"],
        "current_count": topology["current_count"],
        "row_count": topology["row_count"],
        "rows": rows,
        "currents": currents,
        "positions": positions,
        "semantic_metadata": _extract_semantic_metadata(
            topology["metadata"], DOMAIN_TOPOLOGY_SEMANTIC_METADATA, "%s.metadata" % context
        ),
    }


def _serialize_domain_current(current, context):
    _require_exact_dict(current, _DOMAIN_CURRENT_FIELDS, context)
    return {
        "current_id": _copy_scalar(current["current_id"], "%s.current_id" % context),
        "current_index": _copy_scalar(current["current_index"], "%s.current_index" % context),
        "horizon_position_id": _copy_scalar(
            current["horizon_position_id"], "%s.horizon_position_id" % context
        ),
        "zenith_position_id": _copy_scalar(
            current["zenith_position_id"], "%s.zenith_position_id" % context
        ),
        "seal_position_id": _copy_scalar(
            current["seal_position_id"], "%s.seal_position_id" % context
        ),
        "semantic_metadata": _extract_semantic_metadata(
            current["metadata"], DOMAIN_CURRENT_SEMANTIC_METADATA, "%s.metadata" % context
        ),
    }


def _serialize_domain_position(position, context):
    _require_exact_dict(position, _DOMAIN_POSITION_FIELDS, context)
    return {
        "schema_version": position["schema_version"],
        "contract_type": position["contract_type"],
        "position_id": position["position_id"],
        "player_id": position["player_id"],
        "area": position["area"],
        "current_index": position["current_index"],
        "position_type": position["position_type"],
        "row": position["row"],
        "linked_current_id": position["linked_current_id"],
        "visibility": position["visibility"],
        "semantic_metadata": _extract_semantic_metadata(
            position["metadata"], DOMAIN_POSITION_SEMANTIC_METADATA, "%s.metadata" % context
        ),
    }


def _serialize_domain_occupancy(occupancy, topology, player_id):
    context = "domain_occupancies[%s]" % player_id
    _require_exact_dict(occupancy, _DOMAIN_OCCUPANCY_FIELDS, context)
    validation = validate_player_domain_occupancy(occupancy, topology)
    _raise_contract_validation(context, validation)
    if occupancy.get("player_id") != player_id:
        raise CanonicalMatchStateSerializationError("%s player_id mismatch." % context)
    slots = [
        _serialize_domain_occupancy_slot(slot, "%s.slots[%s]" % (context, index))
        for index, slot in enumerate(occupancy["slots"])
    ]
    return {
        "schema_version": occupancy["schema_version"],
        "contract_type": occupancy["contract_type"],
        "player_id": occupancy["player_id"],
        "topology_schema_version": occupancy["topology_schema_version"],
        "topology_model": occupancy["topology_model"],
        "occupancy_model": occupancy["occupancy_model"],
        "slot_count": occupancy["slot_count"],
        "slots": slots,
        "semantic_metadata": _extract_semantic_metadata(
            occupancy["metadata"], DOMAIN_OCCUPANCY_SEMANTIC_METADATA, "%s.metadata" % context
        ),
    }


def _serialize_domain_occupancy_slot(slot, context):
    _require_exact_dict(slot, _DOMAIN_OCCUPANCY_SLOT_FIELDS, context)
    return {
        "schema_version": slot["schema_version"],
        "contract_type": slot["contract_type"],
        "position_id": slot["position_id"],
        "player_id": slot["player_id"],
        "current_index": slot["current_index"],
        "position_type": slot["position_type"],
        "row": slot["row"],
        "occupancy_state": slot["occupancy_state"],
        "occupant_object_type": slot["occupant_object_type"],
        "occupant_card_instance_id": slot["occupant_card_instance_id"],
        "visibility": slot["visibility"],
        "semantic_metadata": _extract_semantic_metadata(
            slot["metadata"],
            DOMAIN_OCCUPANCY_SLOT_SEMANTIC_METADATA,
            "%s.metadata" % context,
        ),
    }


def _serialize_event(event, index):
    context = "event_log[%s]" % index
    _require_exact_dict(event, _ENGINE_EVENT_FIELDS, context)
    validation = validate_engine_event_envelope(event)
    _raise_contract_validation(context, validation)
    if event.get("event_index") != index or event.get("event_sequence") != index + 1:
        raise CanonicalMatchStateSerializationError(
            "%s must retain zero-based index and one-based sequence ordering." % context
        )
    event_type = event["event_type"]
    payload = event["payload"]
    if event_type == "zone_move":
        canonical_payload = _serialize_zone_move_payload(payload, "%s.payload" % context)
    elif event_type == "turn_transition":
        canonical_payload = _serialize_turn_transition_payload(payload, "%s.payload" % context)
    else:
        raise CanonicalMatchStateSerializationError(
            "%s has unsupported typed event_type: %s" % (context, event_type)
        )
    return {
        "schema_version": event["schema_version"],
        "contract_type": event["contract_type"],
        "event_index": event["event_index"],
        "event_sequence": event["event_sequence"],
        "event_type": event_type,
        "player_id": event["player_id"],
        "action_type": event["action_type"],
        "turn_number": event["turn_number"],
        "state_version": event["state_version"],
        "payload": canonical_payload,
        "semantic_metadata": _extract_semantic_metadata(
            {}, ENGINE_EVENT_SEMANTIC_METADATA, "%s.metadata" % context
        ),
    }


def _serialize_zone_move_payload(payload, context):
    _require_exact_dict(payload, _ZONE_MOVE_FIELDS, context)
    _raise_contract_validation(context, validate_zone_move_record(payload))
    return {
        "schema_version": payload["schema_version"],
        "contract_type": payload["contract_type"],
        "event_type": payload["event_type"],
        "card_instance_id": payload["card_instance_id"],
        "card_id": payload["card_id"],
        "owner_player_id": payload["owner_player_id"],
        "controller_player_id": payload["controller_player_id"],
        "from_zone": payload["from_zone"],
        "from_zone_index": payload["from_zone_index"],
        "to_zone": payload["to_zone"],
        "to_zone_index": payload["to_zone_index"],
        "source_action_id": payload["source_action_id"],
        "source_action_type": payload["source_action_type"],
        "state_version": payload["state_version"],
        "event_sequence": payload["event_sequence"],
        "visibility_before": payload["visibility_before"],
        "visibility_after": payload["visibility_after"],
        "semantic_metadata": _extract_semantic_metadata(
            payload["metadata"], ZONE_MOVE_SEMANTIC_METADATA, "%s.metadata" % context
        ),
    }


def _serialize_turn_transition_payload(payload, context):
    _require_exact_dict(payload, _TURN_TRANSITION_FIELDS, context)
    _raise_contract_validation(context, validate_turn_transition_record(payload))
    return {
        "schema_version": payload["schema_version"],
        "contract_type": payload["contract_type"],
        "event_type": payload["event_type"],
        "previous_active_player_id": payload["previous_active_player_id"],
        "next_active_player_id": payload["next_active_player_id"],
        "previous_priority_player_id": payload["previous_priority_player_id"],
        "next_priority_player_id": payload["next_priority_player_id"],
        "turn_number_before": payload["turn_number_before"],
        "turn_number_after": payload["turn_number_after"],
        "phase_before": payload["phase_before"],
        "phase_after": payload["phase_after"],
        "source_action_id": payload["source_action_id"],
        "source_action_type": payload["source_action_type"],
        "state_version": payload["state_version"],
        "event_sequence": payload["event_sequence"],
        "semantic_metadata": _extract_semantic_metadata(
            payload["metadata"], TURN_TRANSITION_SEMANTIC_METADATA, "%s.metadata" % context
        ),
    }


def _extract_semantic_metadata(metadata, semantic_fields, context):
    if not isinstance(metadata, dict):
        raise CanonicalMatchStateSerializationError("%s must be a dict." % context)
    unknown = [
        key
        for key in metadata
        if key not in semantic_fields and key not in IMPLEMENTATION_SPECIFIC_METADATA
    ]
    if unknown:
        raise CanonicalMatchStateSerializationError(
            "%s contains unknown metadata fields: %s"
            % (context, ", ".join(sorted(str(key) for key in unknown)))
        )
    return {
        key: _copy_json_value(metadata[key], "%s.%s" % (context, key))
        for key in sorted(semantic_fields)
        if key in metadata
    }


def _require_exact_dict(value, expected_fields, context):
    if not isinstance(value, dict):
        raise CanonicalMatchStateSerializationError("%s must be a dict." % context)
    _raise_field_set_error(context, set(value), expected_fields)


def _raise_field_set_error(context, actual_fields, expected_fields):
    missing = sorted(expected_fields - actual_fields)
    unexpected = sorted(actual_fields - expected_fields)
    if missing or unexpected:
        raise CanonicalMatchStateSerializationError(
            "%s field set mismatch; missing=%s unexpected=%s"
            % (context, missing, unexpected)
        )


def _raise_contract_validation(context, validation):
    if validation.get("valid") is True:
        return
    first = (validation.get("errors") or [{}])[0]
    raise CanonicalMatchStateSerializationError(
        "%s contract validation failed: %s: %s"
        % (context, first.get("code", "unknown"), first.get("message", "invalid record"))
    )


def _copy_string_list(values, context):
    if not isinstance(values, list):
        raise CanonicalMatchStateSerializationError("%s must be a list." % context)
    result = []
    for index, value in enumerate(values):
        _require_non_empty_string(value, "%s[%s]" % (context, index))
        result.append(value)
    return result


def _copy_scalar(value, context):
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise CanonicalMatchStateSerializationError(
        "%s must be a JSON scalar, got %s." % (context, type(value).__name__)
    )


def _copy_json_value(value, context):
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CanonicalMatchStateSerializationError("%s must be finite." % context)
        return value
    if isinstance(value, list):
        return [_copy_json_value(item, "%s[%s]" % (context, index)) for index, item in enumerate(value)]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalMatchStateSerializationError(
                    "%s object keys must be strings." % context
                )
            result[key] = _copy_json_value(item, "%s.%s" % (context, key))
        return result
    raise CanonicalMatchStateSerializationError(
        "%s is not JSON-compatible: %s." % (context, type(value).__name__)
    )


def _require_non_empty_string(value, context):
    if not isinstance(value, str) or not value.strip():
        raise CanonicalMatchStateSerializationError("%s must be a non-empty string." % context)


def _require_integer(value, context, minimum=None):
    if not isinstance(value, int) or isinstance(value, bool):
        raise CanonicalMatchStateSerializationError("%s must be an integer." % context)
    if minimum is not None and value < minimum:
        raise CanonicalMatchStateSerializationError(
            "%s must be >= %s." % (context, minimum)
        )


__all__ = [
    "CANONICAL_MATCH_STATE_SCHEMA_VERSION",
    "CANONICAL_MATCH_STATE_CONTRACT_TYPE",
    "MINIMAL_PRIORITY_MODEL",
    "FIELD_POLICIES",
    "CARD_INSTANCE_SEMANTIC_METADATA",
    "DOMAIN_TOPOLOGY_SEMANTIC_METADATA",
    "DOMAIN_CURRENT_SEMANTIC_METADATA",
    "DOMAIN_POSITION_SEMANTIC_METADATA",
    "DOMAIN_OCCUPANCY_SEMANTIC_METADATA",
    "DOMAIN_OCCUPANCY_SLOT_SEMANTIC_METADATA",
    "ZONE_MOVE_SEMANTIC_METADATA",
    "TURN_TRANSITION_SEMANTIC_METADATA",
    "IMPLEMENTATION_SPECIFIC_METADATA",
    "CanonicalMatchStateSerializationError",
    "serialize_match_state",
]
