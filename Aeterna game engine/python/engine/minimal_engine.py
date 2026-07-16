"""Minimal Python engine facade for the current contract-first smoke loop.

This module is not the full AETERNA rules engine. It gives the existing
runtime-package -> match-state -> legal-action -> action-request -> resolve
path a small official engine-facing boundary while the rules kernel is still
limited to the current end_turn smoke slice.
"""

from __future__ import annotations

import sys
from pathlib import Path


AI_VS_AI_DIR = Path(__file__).resolve().parents[1] / "tools" / "ai_vs_ai"
if str(AI_VS_AI_DIR) not in sys.path:
    sys.path.insert(0, str(AI_VS_AI_DIR))

from action_request import create_action_request, resolve_action_request, validate_action_request  # noqa: E402
from rules_kernel import create_initial_match_state, list_legal_actions  # noqa: E402
from state_invariants import validate_state_invariants  # noqa: E402

try:
    from player_visible_snapshot import create_player_visible_snapshot as _create_player_visible_snapshot
except ModuleNotFoundError:
    from .player_visible_snapshot import create_player_visible_snapshot as _create_player_visible_snapshot


def create_match(
    runtime_package,
    deck_id_a,
    deck_id_b,
    match_id="ENGINE-SMOKE-001",
    player_ids=("P1", "P2"),
    starting_hand_size=0,
):
    return create_initial_match_state(
        runtime_package,
        deck_id_a,
        deck_id_b,
        match_id=match_id,
        player_ids=player_ids,
        starting_hand_size=starting_hand_size,
    )


def get_legal_actions(state, player_id=None):
    return list_legal_actions(state, player_id)


def build_action_request(state, action, player_id=None, expected_state_version=None):
    return create_action_request(
        state.match_id,
        player_id or state.active_player_id,
        action,
        expected_state_version=expected_state_version,
    )


def validate_request(state, request, legal_actions):
    return validate_action_request(request, legal_actions, state)


def resolve_request(state, request, legal_actions):
    return resolve_action_request(state, request, legal_actions)


def validate_invariants(state, runtime_package=None):
    return validate_state_invariants(state, runtime_package)


def event_log(state):
    return list(state.event_log)


def can_player_draw(state, player_id):
    try:
        player = state.get_player(player_id)
    except Exception:
        return {
            "player_id": player_id,
            "can_draw": False,
            "reason": "player_unknown",
            "deck_count": 0,
            "hand_count": 0,
            "metadata": {
                "source": "python.engine.minimal_engine",
                "rules_scope": "minimal_end_turn_smoke",
                "card_instance_model": "minimal_registry_v0",
                "card_id_overlap_guard": False,
            },
        }

    deck_count = len(player.deck_card_instance_ids)
    hand_count = len(player.hand_card_instance_ids)
    reason = _draw_precondition_reason(player)
    return {
        "player_id": player_id,
        "can_draw": reason == "ok",
        "reason": reason,
        "deck_count": deck_count,
        "hand_count": hand_count,
        "metadata": {
            "source": "python.engine.minimal_engine",
            "rules_scope": "minimal_end_turn_smoke",
            "card_instance_model": "minimal_registry_v0",
            "card_id_overlap_guard": False,
        },
    }


def create_debug_snapshot(state, legal_actions=None, diagnostics=None):
    actions = list(legal_actions or [])
    invariant_errors = list(diagnostics or [])
    return {
        "schema_version": "engine-debug-snapshot-v0",
        "contract_type": "engine_debug_snapshot",
        "snapshot_type": "debug_snapshot",
        "visibility_mode": "debug",
        "match_id": state.match_id,
        "state_version": state.state_version,
        "turn": state.turn_number,
        "turn_number": state.turn_number,
        "phase": state.phase,
        "active_player_id": state.active_player_id,
        "priority_player_id": state.active_player_id,
        "players": [_player_debug_summary(player) for player in state.players],
        "legal_action_summary": _legal_action_summary(actions, state.state_version),
        "event_log_summary": _event_log_summary(state.event_log),
        "diagnostics_summary": {
            "invariant_errors": len(invariant_errors),
            "blocking_errors": len(invariant_errors),
            "warnings": 0,
            "hand_deck_invariants_ok": _hand_deck_invariants_ok(invariant_errors),
            "draw_preconditions_ok": _draw_preconditions_ok(state),
        },
        "card_instance_count": len(state.card_instances),
        "metadata": {
            "source": "python.engine.minimal_engine",
            "rules_scope": "minimal_end_turn_smoke",
            "runtime_decision": "reference_smoke_backend_candidate",
            "card_instance_model": "minimal_registry_v0",
            "card_id_overlap_guard": False,
        },
    }


def create_player_visible_snapshot(state, player_id, legal_actions=None, diagnostics=None):
    return _create_player_visible_snapshot(state, player_id, legal_actions, diagnostics)


def _player_debug_summary(player):
    return {
        "player_id": player.player_id,
        "deck_id": player.deck_id,
        "deck_count": len(player.deck_card_instance_ids),
        "hand_count": len(player.hand_card_instance_ids),
        "discard_count": len(player.discard_card_instance_ids),
        "zone_summary": _player_zone_summary(player),
    }


def _player_zone_summary(player):
    reason = _draw_precondition_reason(player)
    return {
        "deck_count": len(player.deck_card_instance_ids),
        "hand_count": len(player.hand_card_instance_ids),
        "discard_count": len(player.discard_card_instance_ids),
        "draw_precondition": {
            "can_draw": reason == "ok",
            "reason": reason,
        },
    }


def _legal_action_summary(legal_actions, state_version=None):
    return {
        "state_version": state_version,
        "action_count": len(legal_actions),
        "enabled_count": sum(1 for action in legal_actions if action.get("enabled") is True),
        "disabled_count": sum(1 for action in legal_actions if action.get("enabled") is not True),
        "action_types": sorted({str(action.get("action_type", "")) for action in legal_actions if action.get("action_type")}),
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


def _draw_preconditions_ok(state):
    return all(can_player_draw(state, player.player_id)["can_draw"] for player in state.players)


def _draw_precondition_reason(player):
    if not player.deck_card_instance_ids:
        return "deck_empty"
    return "ok"
