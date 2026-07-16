"""Minimal rules kernel for AI smoke work.

This is not the AETERNA rules engine. It only proves the first contract-first
loop: runtime package -> match state -> legal actions -> action resolve -> log.
"""

from __future__ import annotations

try:
    from match_state import MatchState, PlayerState
    from runtime_package_reader import RuntimePackageReadError
except ModuleNotFoundError:
    from .match_state import MatchState, PlayerState
    from .runtime_package_reader import RuntimePackageReadError

try:
    from card_instance import create_card_instance_id, create_card_instance_record
except ModuleNotFoundError:
    from engine.card_instance import create_card_instance_id, create_card_instance_record

try:
    from zone_move import create_zone_move_record, validate_zone_move_record, zone_move_to_event
except ModuleNotFoundError:
    from engine.zone_move import create_zone_move_record, validate_zone_move_record, zone_move_to_event

try:
    from turn_transition import (
        create_turn_transition_record,
        turn_transition_to_event,
        validate_turn_transition_record,
    )
except ModuleNotFoundError:
    from engine.turn_transition import (
        create_turn_transition_record,
        turn_transition_to_event,
        validate_turn_transition_record,
    )

try:
    from domain_position import create_player_domain_topology
except ModuleNotFoundError:
    from engine.domain_position import create_player_domain_topology

try:
    from domain_occupancy import create_empty_player_domain_occupancy
except ModuleNotFoundError:
    from engine.domain_occupancy import create_empty_player_domain_occupancy


class RulesKernelError(Exception):
    """Raised when the minimal rules kernel rejects an operation."""


DEFAULT_PLAYER_IDS = ("P1", "P2")


def create_initial_match_state(
    runtime_package,
    deck_id_a,
    deck_id_b,
    match_id="AI-SMOKE-001",
    player_ids=DEFAULT_PLAYER_IDS,
    starting_hand_size=0,
):
    player_ids = _validate_player_ids(player_ids)
    starting_hand_size = _validate_starting_hand_size(starting_hand_size)
    _ensure_valid_runtime_package_deck_refs(runtime_package)
    deck_a = _get_deck_or_raise(runtime_package, deck_id_a)
    deck_b = _get_deck_or_raise(runtime_package, deck_id_b)
    deck_card_ids_a = _expand_deck_entries(deck_a)
    deck_card_ids_b = _expand_deck_entries(deck_b)
    _validate_starting_hand_fits_deck(starting_hand_size, deck_id_a, deck_card_ids_a)
    _validate_starting_hand_fits_deck(starting_hand_size, deck_id_b, deck_card_ids_b)

    card_instances = {}
    players = [
        _create_player_state(
            player_ids[0],
            deck_id_a,
            deck_card_ids_a,
            card_instances,
            starting_hand_size,
        ),
        _create_player_state(
            player_ids[1],
            deck_id_b,
            deck_card_ids_b,
            card_instances,
            starting_hand_size,
        ),
    ]
    domain_topologies = {
        player.player_id: create_player_domain_topology(player.player_id) for player in players
    }
    domain_occupancies = {
        player.player_id: create_empty_player_domain_occupancy(
            domain_topologies[player.player_id]
        )
        for player in players
    }

    return MatchState(
        match_id=match_id,
        turn_number=1,
        active_player_id=player_ids[0],
        players=players,
        phase="main",
        card_instances=card_instances,
        domain_topologies=domain_topologies,
        domain_occupancies=domain_occupancies,
        event_log=[],
    )


def list_legal_actions(state, player_id=None):
    player_id = player_id or state.active_player_id
    enabled = player_id == state.active_player_id
    end_turn_action = {
        "action_id": "end_turn:%s:%s" % (state.turn_number, player_id),
        "action_type": "end_turn",
        "player_id": player_id,
        "enabled": enabled,
    }
    if not enabled:
        end_turn_action["reason"] = "not_active_player"

    draw_enabled = enabled and _can_player_draw(state, player_id)
    draw_action = {
        "action_id": "draw_card:%s:%s:%s" % (state.turn_number, state.state_version, player_id),
        "action_type": "draw_card",
        "player_id": player_id,
        "enabled": draw_enabled,
    }
    if not enabled:
        draw_action["reason"] = "not_active_player"
    elif not draw_enabled:
        player = state.get_player(player_id)
        draw_action["reason"] = "deck_empty" if not player.deck_card_instance_ids else "action_not_enabled"

    return [end_turn_action, draw_action]


def apply_action(state, action):
    action_type = action.get("action_type")
    if action_type not in {"end_turn", "draw_card"}:
        raise RulesKernelError("Unsupported action_type: %s" % action_type)
    if not action.get("enabled", False):
        raise RulesKernelError("Action is not enabled: %s" % action.get("action_id"))

    player_id = action.get("player_id")
    if player_id != state.active_player_id:
        raise RulesKernelError("Action player is not active: %s" % player_id)

    if action_type == "draw_card":
        return _apply_draw_card(state, action)
    return _apply_end_turn(state, action)


def _apply_end_turn(state, action):
    previous_player_id = state.active_player_id
    previous_priority_player_id = state.active_player_id
    turn_number_before = state.turn_number
    phase_before = state.phase
    next_player_id = state.get_inactive_player_id()
    state.active_player_id = next_player_id
    ordered_player_ids = [player.player_id for player in state.players]
    if ordered_player_ids.index(previous_player_id) == len(ordered_player_ids) - 1:
        state.turn_number += 1
    state.state_version += 1

    event_index = len(state.event_log)
    event_sequence = event_index + 1
    turn_transition = create_turn_transition_record(
        previous_active_player_id=previous_player_id,
        next_active_player_id=state.active_player_id,
        previous_priority_player_id=previous_priority_player_id,
        next_priority_player_id=state.active_player_id,
        turn_number_before=turn_number_before,
        turn_number_after=state.turn_number,
        phase_before=phase_before,
        phase_after=state.phase,
        source_action_id=action.get("action_id"),
        source_action_type="end_turn",
        state_version=state.state_version,
        event_sequence=event_sequence,
        metadata={
            "semantic_event_type": "end_turn_resolved",
            "authority": "rules_kernel",
            "turn_model": "minimal_alternating_players",
            "applied": True,
        },
    )
    validation = validate_turn_transition_record(turn_transition)
    if not validation.get("valid"):
        first_error = (validation.get("errors") or [{}])[0]
        raise RulesKernelError(
            "Invalid end_turn TurnTransition record: %s" % first_error.get("code", "unknown")
        )

    event = turn_transition_to_event(
        turn_transition,
        event_index=event_index,
        turn_number=state.turn_number,
        player_id=previous_player_id,
        action_type="end_turn",
    )
    state.event_log.append(event)
    return {
        "ok": True,
        "action": dict(action),
        "event": event,
        "state": state,
    }


def _apply_draw_card(state, action):
    player_id = action.get("player_id")
    player = state.get_player(player_id)
    if not player.deck_card_instance_ids:
        raise RulesKernelError("Cannot draw from empty deck: %s" % player_id)

    from_zone_index = 0
    to_zone_index = len(player.hand_card_instance_ids)
    event_index = len(state.event_log)
    event_sequence = event_index + 1
    card_instance_id = player.deck_card_instance_ids.pop(from_zone_index)
    player.hand_card_instance_ids.append(card_instance_id)
    card_instance = state.get_card_instance(card_instance_id)
    card_id = card_instance.get("card_id")
    visibility_before = card_instance.get("visibility")
    card_instance["zone"] = "hand"
    card_instance["zone_index"] = to_zone_index
    card_instance["visibility"] = "owner_only"
    card_instance["zone_sequence"] = int(card_instance.get("zone_sequence") or 0) + 1
    _reindex_zone(state, player.deck_card_instance_ids, "deck")
    state.state_version += 1

    zone_move = create_zone_move_record(
        card_instance_id=card_instance_id,
        card_id=card_id,
        owner_player_id=card_instance.get("owner_player_id"),
        controller_player_id=card_instance.get("controller_player_id"),
        from_zone="deck",
        from_zone_index=from_zone_index,
        to_zone="hand",
        to_zone_index=to_zone_index,
        source_action_id=action.get("action_id"),
        source_action_type="draw_card",
        state_version=state.state_version,
        event_sequence=event_sequence,
        visibility_before=visibility_before,
        visibility_after=card_instance.get("visibility"),
        metadata={
            "zone_operation": "draw_card",
            "semantic_event_type": "card_drawn",
            "authority": "rules_kernel",
            "applied": True,
        },
    )
    validation = validate_zone_move_record(zone_move)
    if not validation.get("valid"):
        first_error = (validation.get("errors") or [{}])[0]
        raise RulesKernelError("Invalid draw ZoneMove record: %s" % first_error.get("code", "unknown"))

    event = zone_move_to_event(
        zone_move,
        event_index=event_index,
        turn_number=state.turn_number,
        player_id=player_id,
        action_type="draw_card",
    )
    state.event_log.append(event)
    return {
        "ok": True,
        "action": dict(action),
        "event": event,
        "state": state,
    }


def _ensure_valid_runtime_package_deck_refs(runtime_package):
    errors = runtime_package.validate_deck_card_refs()
    if errors:
        first = errors[0]
        raise RulesKernelError(
            "Runtime package has invalid deck card references; first error: deck_id=%s card_id=%s"
            % (first.get("deck_id"), first.get("card_id"))
        )


def _get_deck_or_raise(runtime_package, deck_id):
    try:
        return runtime_package.get_deck(deck_id)
    except RuntimePackageReadError as exc:
        raise RulesKernelError("Unknown deck_id: %s" % deck_id) from exc


def _expand_deck_entries(deck):
    card_ids = []
    for entry in deck.get("card_entries", []) or []:
        count = int(entry.get("count") or 0)
        card_ids.extend([entry.get("card_id")] * count)
    return card_ids


def _validate_player_ids(player_ids):
    if player_ids is None or isinstance(player_ids, (str, bytes)):
        raise RulesKernelError("player_ids must contain exactly two player IDs.")
    try:
        normalized = tuple(player_ids)
    except TypeError as exc:
        raise RulesKernelError("player_ids must contain exactly two player IDs.") from exc
    if len(normalized) != 2:
        raise RulesKernelError("player_ids must contain exactly two player IDs.")
    for index, player_id in enumerate(normalized):
        if not isinstance(player_id, str) or not player_id.strip():
            raise RulesKernelError("player_ids[%s] must be a non-empty string." % index)
    if normalized[0] == normalized[1]:
        raise RulesKernelError("player_ids must contain two distinct values.")
    return normalized


def _validate_starting_hand_size(starting_hand_size):
    if (
        not isinstance(starting_hand_size, int)
        or isinstance(starting_hand_size, bool)
        or starting_hand_size < 0
    ):
        raise RulesKernelError("starting_hand_size must be a non-negative integer.")
    return starting_hand_size


def _validate_starting_hand_fits_deck(starting_hand_size, deck_id, card_ids):
    if starting_hand_size > len(card_ids):
        raise RulesKernelError(
            "starting_hand_size %s exceeds deck size %s for deck_id: %s"
            % (starting_hand_size, len(card_ids), deck_id)
        )


def _can_player_draw(state, player_id):
    try:
        return bool(state.get_player(player_id).deck_card_instance_ids)
    except Exception:
        return False


def _create_player_state(
    player_id,
    deck_id,
    ordered_card_ids,
    card_instances,
    starting_hand_size,
):
    deck_card_instance_ids = []
    hand_card_instance_ids = []
    for original_deck_index, card_id in enumerate(ordered_card_ids):
        sequence = original_deck_index + 1
        initial_zone = "hand" if original_deck_index < starting_hand_size else "deck"
        target_zone = hand_card_instance_ids if initial_zone == "hand" else deck_card_instance_ids
        zone_index = len(target_zone)
        card_instance_id = create_card_instance_id(player_id, sequence)
        card_instances[card_instance_id] = create_card_instance_record(
            card_instance_id=card_instance_id,
            card_id=card_id,
            owner_player_id=player_id,
            controller_player_id=player_id,
            zone=initial_zone,
            zone_index=zone_index,
            visibility="owner_only",
            created_sequence=sequence,
            zone_sequence=1,
            metadata={
                "creation_reason": "initial_match_setup",
                "initial_zone": initial_zone,
            },
            activity_state=None,
        )
        target_zone.append(card_instance_id)
    return PlayerState(
        player_id=player_id,
        deck_id=deck_id,
        deck_card_instance_ids=deck_card_instance_ids,
        hand_card_instance_ids=hand_card_instance_ids,
    )


def _reindex_zone(state, card_instance_ids, zone):
    for zone_index, card_instance_id in enumerate(card_instance_ids):
        card_instance = state.get_card_instance(card_instance_id)
        card_instance["zone"] = zone
        card_instance["zone_index"] = zone_index
