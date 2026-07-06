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
