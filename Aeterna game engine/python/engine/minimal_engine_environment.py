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

try:
    from episode_trajectory import (
        create_episode_step_record,
        validate_episode_step_record,
        validate_episode_trajectory,
    )
except ModuleNotFoundError:
    from .episode_trajectory import (
        create_episode_step_record,
        validate_episode_step_record,
        validate_episode_trajectory,
    )


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
        player_snapshot = self.session.get_player_snapshot(player_id)
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
                "player_snapshot": player_snapshot,
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
            observation_before = self.get_observation(player_id)
            policy = agents.get(player_id) or DeterministicMinimalBotPolicy()
            action = policy.choose_action(observation_before)
            if action is None:
                stop_reason = "no_enabled_action"
                break

            request = self.session.build_action_request(action, player_id=player_id)
            response = self.step(request)
            observation_after = self.get_observation()
            step_record = create_episode_step_record(
                step_index=step_index,
                acting_player_id=player_id,
                observation_before=observation_before,
                selected_action=action,
                action_request=request,
                action_response=response,
                observation_after=observation_after,
            )
            step_validation = validate_episode_step_record(step_record)
            if not step_validation.get("valid"):
                codes = [error.get("code", "unknown") for error in step_validation.get("errors", [])]
                raise MinimalEngineEnvironmentError(
                    "Invalid canonical episode step %s: %s" % (step_index, ", ".join(codes))
                )
            trajectory.append(step_record)
            if response.get("accepted") is not True:
                stop_reason = response.get("reason") or "action_rejected"
                break
        else:
            stop_reason = "max_steps_reached"

        final_observation = self.get_observation()
        diagnostics = self.session.get_diagnostics()
        trajectory_validation = validate_episode_trajectory(trajectory)
        if not trajectory_validation.get("valid"):
            codes = [error.get("code", "unknown") for error in trajectory_validation.get("errors", [])]
            raise MinimalEngineEnvironmentError(
                "Invalid canonical episode trajectory: %s" % ", ".join(codes)
            )
        return deepcopy(
            {
                "schema_version": "minimal-ai-vs-ai-episode-v1",
                "contract_type": "minimal_ai_vs_ai_episode",
                "match_id": final_observation["match_id"],
                "max_steps": max_steps,
                "steps_run": len(trajectory),
                "stop_reason": stop_reason,
                "initial_observation": initial_observation,
                "final_observation": final_observation,
                "trajectory": trajectory,
                "trajectory_validation": trajectory_validation,
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
                    "trajectory_model": "full_transition_v0",
                    "replay_support": "not_implemented",
                    "replay_ready": False,
                },
            }
        )


class MinimalEngineEnvironmentError(Exception):
    """Raised when the minimal environment cannot run an episode."""
