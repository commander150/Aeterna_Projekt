"""Minimal AI-vs-AI environment wrapper over MinimalEngineSession.

This is a small smoke/balance-runner boundary, not the full AETERNA AI and not
the final runtime decision. It does not define rules; it only drives the
existing MinimalEngineSession API with deterministic test policies.
"""

from __future__ import annotations

from copy import deepcopy

try:
    from minimal_engine_session import MinimalEngineSession
except ModuleNotFoundError:
    from .minimal_engine_session import MinimalEngineSession


class DeterministicMinimalBotPolicy:
    """Choose from the legal action-space contract without mutating state."""

    ACTION_PRIORITY = ("draw_card", "end_turn")

    def choose_action(self, observation):
        action_space = observation.get("action_space") or {}
        actions = list(action_space.get("actions") or [])
        for action_type in self.ACTION_PRIORITY:
            candidates = [
                action
                for action in actions
                if action.get("enabled") is True and action.get("action_type") == action_type
            ]
            if candidates:
                return dict(sorted(candidates, key=lambda action: str(action.get("action_id") or ""))[0])
        return None


class MinimalEngineEnvironment:
    """Tiny environment facade for the current draw_card/end_turn smoke slice."""

    def __init__(self, runtime_package):
        self.runtime_package = runtime_package
        self.session = MinimalEngineSession(runtime_package)

    def reset(self, match_id=None, deck_id_a=None, deck_id_b=None):
        self.session = MinimalEngineSession(self.runtime_package)
        self.session.create_match(deck_id_a=deck_id_a, deck_id_b=deck_id_b, match_id=match_id)
        return self.get_observation()

    def get_observation(self, player_id=None):
        state = self.session._require_state()
        player_id = player_id or state.active_player_id
        diagnostics = self.session.get_diagnostics()
        return deepcopy(
            {
                "schema_version": "minimal-engine-observation-v0",
                "contract_type": "minimal_engine_observation",
                "match_id": state.match_id,
                "player_id": player_id,
                "state_version": state.state_version,
                "turn": state.turn_number,
                "phase": state.phase,
                "active_player_id": state.active_player_id,
                "priority_player_id": state.active_player_id,
                "action_space": self.get_action_space(player_id),
                "transition_summary": self.session.get_transition_summary(),
                "engine_context_summary": self.session.get_engine_context_summary(player_id),
                "last_action_response": self.session.get_last_action_response(),
                "diagnostics_summary": {
                    "count": len(diagnostics),
                    "blocking_errors": len(diagnostics),
                    "warnings": 0,
                },
                "metadata": {
                    "source": "python.engine.minimal_engine_environment",
                    "rules_scope": "minimal_draw_end_turn_smoke",
                    "runtime_decision": "reference_smoke_backend_candidate",
                },
            }
        )

    def get_action_space(self, player_id=None):
        return self.session.get_action_space(player_id)

    def step(self, action_request):
        return self.session.step(action_request)

    def run_episode(self, agents=None, max_steps=10, match_id=None):
        if max_steps <= 0:
            raise MinimalEngineEnvironmentError("max_steps must be greater than 0.")
        agents = agents or {}
        initial_observation = self.reset(match_id=match_id)
        trajectory = []
        stop_reason = "max_steps_reached"

        for step_index in range(max_steps):
            state = self.session._require_state()
            player_id = state.active_player_id
            observation = self.get_observation(player_id)
            policy = agents.get(player_id) or DeterministicMinimalBotPolicy()
            action = policy.choose_action(observation)
            if action is None:
                stop_reason = "no_enabled_action"
                break

            request = self.session.build_action_request(action, player_id=player_id)
            response = self.step(request)
            trajectory.append(_trajectory_entry(step_index, player_id, action, response))
            if response.get("accepted") is not True:
                stop_reason = response.get("reason") or "action_rejected"
                break
        else:
            stop_reason = "max_steps_reached"

        final_observation = self.get_observation()
        diagnostics = self.session.get_diagnostics()
        return deepcopy(
            {
                "schema_version": "minimal-ai-vs-ai-episode-v0",
                "contract_type": "minimal_ai_vs_ai_episode",
                "match_id": final_observation["match_id"],
                "max_steps": max_steps,
                "steps_run": len(trajectory),
                "stop_reason": stop_reason,
                "initial_observation": initial_observation,
                "final_observation": final_observation,
                "trajectory": trajectory,
                "transition_summary": self.session.get_transition_summary(),
                "diagnostics_summary": {
                    "count": len(diagnostics),
                    "blocking_errors": len(diagnostics),
                    "warnings": 0,
                },
                "metadata": {
                    "source": "python.engine.minimal_engine_environment",
                    "rules_scope": "minimal_draw_end_turn_smoke",
                    "runtime_decision": "not_final",
                    "replay_support": "not_implemented",
                },
            }
        )


class MinimalEngineEnvironmentError(Exception):
    """Raised when the minimal environment cannot run an episode."""


def _trajectory_entry(step_index, player_id, action, response):
    return {
        "step_index": step_index,
        "player_id": player_id,
        "selected_action_type": action.get("action_type"),
        "selected_action_id": action.get("action_id"),
        "response_accepted": response.get("accepted"),
        "response_success": response.get("success"),
        "response_reason": response.get("reason"),
        "state_version_before": response.get("state_version_before"),
        "state_version_after": response.get("state_version_after"),
        "new_event_sequences": list(response.get("new_event_sequences") or []),
    }
