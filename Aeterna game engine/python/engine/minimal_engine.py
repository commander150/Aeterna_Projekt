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


def create_match(runtime_package, deck_id_a, deck_id_b, match_id="ENGINE-SMOKE-001"):
    return create_initial_match_state(runtime_package, deck_id_a, deck_id_b, match_id=match_id)


def get_legal_actions(state, player_id=None):
    return list_legal_actions(state, player_id)


def build_action_request(state, action, player_id=None):
    return create_action_request(state.match_id, player_id or state.active_player_id, action)


def validate_request(state, request, legal_actions):
    return validate_action_request(request, legal_actions, state)


def resolve_request(state, request, legal_actions):
    return resolve_action_request(state, request, legal_actions)


def validate_invariants(state, runtime_package=None):
    return validate_state_invariants(state, runtime_package)


def event_log(state):
    return list(state.event_log)


def create_debug_snapshot(state, legal_actions=None, diagnostics=None):
    actions = list(legal_actions or [])
    invariant_errors = list(diagnostics or [])
    return {
        "schema_version": "engine-debug-snapshot-v0",
        "contract_type": "engine_debug_snapshot",
        "snapshot_type": "debug_snapshot",
        "visibility_mode": "debug",
        "match_id": state.match_id,
        "turn": state.turn_number,
        "turn_number": state.turn_number,
        "phase": state.phase,
        "active_player_id": state.active_player_id,
        "priority_player_id": state.active_player_id,
        "players": [_player_debug_summary(player) for player in state.players],
        "legal_action_summary": _legal_action_summary(actions),
        "event_log_summary": _event_log_summary(state.event_log),
        "diagnostics_summary": {
            "invariant_errors": len(invariant_errors),
            "blocking_errors": len(invariant_errors),
            "warnings": 0,
        },
        "metadata": {
            "source": "python.engine.minimal_engine",
            "rules_scope": "minimal_end_turn_smoke",
            "runtime_decision": "reference_smoke_backend_candidate",
        },
    }


def _player_debug_summary(player):
    return {
        "player_id": player.player_id,
        "deck_id": player.deck_id,
        "deck_count": len(player.deck_card_ids),
        "hand_count": len(player.hand),
        "discard_count": len(player.discard),
    }


def _legal_action_summary(legal_actions):
    return {
        "action_count": len(legal_actions),
        "enabled_count": sum(1 for action in legal_actions if action.get("enabled") is True),
        "disabled_count": sum(1 for action in legal_actions if action.get("enabled") is not True),
        "action_types": sorted({str(action.get("action_type", "")) for action in legal_actions if action.get("action_type")}),
    }


def _event_log_summary(events):
    return {
        "event_count": len(events),
        "last_event_type": str(events[-1].get("event_type", "")) if events else None,
    }
