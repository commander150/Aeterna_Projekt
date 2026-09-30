"""Headless AI smoke scenario runner.

The runner orchestrates existing contract-first AI smoke layers. It does not
define rules, generate actions, or implement card gameplay.
"""

from __future__ import annotations

try:
    from action_request import create_action_request, resolve_action_request
    from bot_policy import DeterministicBotPolicy, BotPolicyError
    from rules_kernel import create_initial_match_state, list_legal_actions
    from scenario_config import validate_scenario_config
    from state_invariants import StateInvariantError, assert_state_invariants, validate_state_invariants
except ModuleNotFoundError:
    from .action_request import create_action_request, resolve_action_request
    from .bot_policy import DeterministicBotPolicy, BotPolicyError
    from .rules_kernel import create_initial_match_state, list_legal_actions
    from .scenario_config import validate_scenario_config
    from .state_invariants import StateInvariantError, assert_state_invariants, validate_state_invariants


def run_scenario(config, runtime_package):
    config_errors = validate_scenario_config(config, runtime_package)
    if config_errors:
        return _failed_summary(
            config,
            result="invalid_config",
            invariant_errors=config_errors,
        )

    state = create_initial_match_state(
        runtime_package,
        config.deck_id_a,
        config.deck_id_b,
        match_id=config.match_id,
    )
    policy = DeterministicBotPolicy()
    rejected_actions = 0

    for _step_index in range(config.max_steps):
        try:
            assert_state_invariants(state, runtime_package)
        except StateInvariantError:
            return _summary(
                config,
                state,
                completed=False,
                steps_run=len(state.event_log),
                rejected_actions=rejected_actions,
                invariant_errors=validate_state_invariants(state, runtime_package),
                result="invariant_failed_before_step",
            )

        active_player_id = state.active_player_id
        legal_actions = list_legal_actions(state, active_player_id)
        try:
            chosen_action = policy.choose_action(legal_actions, active_player_id)
        except BotPolicyError:
            result = "no_enabled_action"
            if config.fail_on_no_enabled_action:
                result = "failed_no_enabled_action"
            return _summary(
                config,
                state,
                completed=False,
                steps_run=len(state.event_log),
                rejected_actions=rejected_actions,
                invariant_errors=[],
                result=result,
            )

        request = create_action_request(state.match_id, active_player_id, chosen_action)
        response = resolve_action_request(state, request, legal_actions)
        if not response.get("accepted"):
            rejected_actions += 1
            return _summary(
                config,
                state,
                completed=False,
                steps_run=len(state.event_log),
                rejected_actions=rejected_actions,
                invariant_errors=[],
                result=response.get("reason") or "action_rejected",
            )

        try:
            assert_state_invariants(state, runtime_package)
        except StateInvariantError:
            return _summary(
                config,
                state,
                completed=False,
                steps_run=len(state.event_log),
                rejected_actions=rejected_actions,
                invariant_errors=validate_state_invariants(state, runtime_package),
                result="invariant_failed_after_step",
            )

        if config.max_turns is not None and state.turn_number > config.max_turns:
            return _summary(
                config,
                state,
                completed=True,
                steps_run=len(state.event_log),
                rejected_actions=rejected_actions,
                invariant_errors=[],
                result="max_turns_reached",
            )

    return _summary(
        config,
        state,
        completed=True,
        steps_run=len(state.event_log),
        rejected_actions=rejected_actions,
        invariant_errors=[],
        result="completed",
    )


def _summary(config, state, *, completed, steps_run, rejected_actions, invariant_errors, result):
    return {
        "scenario_id": config.scenario_id,
        "match_id": config.match_id,
        "completed": completed,
        "steps_run": steps_run,
        "turn_number": state.turn_number,
        "event_count": len(state.event_log),
        "final_active_player_id": state.active_player_id,
        "rejected_actions": rejected_actions,
        "invariant_errors": list(invariant_errors or []),
        "result": result,
        "event_log": list(state.event_log),
    }


def _failed_summary(config, *, result, invariant_errors):
    return {
        "scenario_id": getattr(config, "scenario_id", None),
        "match_id": getattr(config, "match_id", None),
        "completed": False,
        "steps_run": 0,
        "turn_number": None,
        "event_count": 0,
        "final_active_player_id": None,
        "rejected_actions": 0,
        "invariant_errors": list(invariant_errors or []),
        "result": result,
        "event_log": [],
    }
