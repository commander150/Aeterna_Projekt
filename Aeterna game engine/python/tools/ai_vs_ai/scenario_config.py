"""Scenario configuration model for AI smoke tests.

This module only describes and validates future headless AI smoke scenarios.
It does not create match state, list legal actions, choose bot actions, resolve
requests, or write event logs.
"""

from __future__ import annotations

from dataclasses import dataclass, field


DEFAULT_DECK_ID_A = "DECK-IGN-HAM-TEST-001"
DEFAULT_DECK_ID_B = "DECK-IGN-LAN-TEST-001"


@dataclass(frozen=True)
class ScenarioConfig:
    scenario_id: str
    match_id: str
    deck_id_a: str
    deck_id_b: str
    max_steps: int = 6
    max_turns: int | None = 5
    seed: int | None = 1
    expected_event_types: tuple = field(default_factory=tuple)
    fail_on_no_enabled_action: bool = True


class ScenarioConfigError(Exception):
    """Raised when a scenario config is invalid."""


def default_end_turn_smoke_config():
    return ScenarioConfig(
        scenario_id="end_turn_smoke",
        match_id="AI-SCENARIO-END-TURN-001",
        deck_id_a=DEFAULT_DECK_ID_A,
        deck_id_b=DEFAULT_DECK_ID_B,
        max_steps=6,
        max_turns=5,
        seed=1,
        expected_event_types=(),
        fail_on_no_enabled_action=True,
    )


def validate_scenario_config(config, runtime_package=None):
    errors = []

    if not getattr(config, "scenario_id", None):
        errors.append(_error("SCENARIO_ID_MISSING", "scenario_id must not be empty."))
    if not getattr(config, "match_id", None):
        errors.append(_error("MATCH_ID_MISSING", "match_id must not be empty."))
    if not getattr(config, "deck_id_a", None):
        errors.append(_error("DECK_ID_A_MISSING", "deck_id_a must not be empty."))
    if not getattr(config, "deck_id_b", None):
        errors.append(_error("DECK_ID_B_MISSING", "deck_id_b must not be empty."))

    max_steps = getattr(config, "max_steps", None)
    if not isinstance(max_steps, int) or max_steps <= 0:
        errors.append(_error("MAX_STEPS_INVALID", "max_steps must be a positive integer."))

    max_turns = getattr(config, "max_turns", None)
    if max_turns is not None and (not isinstance(max_turns, int) or max_turns <= 0):
        errors.append(_error("MAX_TURNS_INVALID", "max_turns must be None or a positive integer."))

    seed = getattr(config, "seed", None)
    if seed is not None and not isinstance(seed, int):
        errors.append(_error("SEED_INVALID", "seed must be an integer or None."))

    expected_event_types = getattr(config, "expected_event_types", None)
    if not isinstance(expected_event_types, (list, tuple)):
        errors.append(_error("EXPECTED_EVENT_TYPES_INVALID", "expected_event_types must be a list or tuple."))
    else:
        for index, event_type in enumerate(expected_event_types):
            if not isinstance(event_type, str) or not event_type:
                errors.append(
                    _error(
                        "EXPECTED_EVENT_TYPE_INVALID",
                        "expected_event_types must only contain non-empty strings.",
                        event_index=index,
                    )
                )

    if not isinstance(getattr(config, "fail_on_no_enabled_action", None), bool):
        errors.append(
            _error("FAIL_ON_NO_ENABLED_ACTION_INVALID", "fail_on_no_enabled_action must be a boolean.")
        )

    if runtime_package is not None:
        errors.extend(_validate_decks_exist(config, runtime_package))

    return errors


def assert_scenario_config(config, runtime_package=None):
    errors = validate_scenario_config(config, runtime_package)
    if errors:
        codes = ", ".join(error["code"] for error in errors)
        raise ScenarioConfigError("Scenario config validation failed: %s" % codes)
    return True


def _validate_decks_exist(config, runtime_package):
    errors = []
    decks_by_id = getattr(runtime_package, "decks_by_id", {}) or {}
    for field_name in ("deck_id_a", "deck_id_b"):
        deck_id = getattr(config, field_name, None)
        if deck_id and deck_id not in decks_by_id:
            errors.append(
                _error(
                    "DECK_ID_UNKNOWN",
                    "scenario deck_id must exist in runtime package.",
                    field_name=field_name,
                    deck_id=deck_id,
                )
            )
    return errors


def _error(code, message, **details):
    error = {"code": code, "message": message}
    error.update(details)
    return error
