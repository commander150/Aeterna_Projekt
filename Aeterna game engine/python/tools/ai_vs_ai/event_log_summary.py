"""Text summary helpers for AI smoke scenario results.

The formatter is intentionally in-memory only. It prepares deterministic output
for later CLI, UI, or log-file layers without writing files itself.
"""

from __future__ import annotations


REQUIRED_RESULT_FIELDS = (
    "scenario_id",
    "match_id",
    "completed",
    "result",
    "steps_run",
    "turn_number",
    "event_count",
    "final_active_player_id",
    "rejected_actions",
    "invariant_errors",
    "event_log",
)


class EventLogSummaryError(Exception):
    """Raised when a scenario result cannot be summarized."""


def summarize_scenario_result(result):
    return build_scenario_summary(result)


def build_scenario_summary(result):
    _validate_result(result)
    event_log = list(result.get("event_log") or [])
    invariant_errors = list(result.get("invariant_errors") or [])
    return {
        "scenario_id": result["scenario_id"],
        "match_id": result["match_id"],
        "completed": result["completed"],
        "result": result["result"],
        "steps_run": result["steps_run"],
        "turn_number": result["turn_number"],
        "event_count": result["event_count"],
        "final_active_player_id": result["final_active_player_id"],
        "rejected_actions": result["rejected_actions"],
        "invariant_error_count": len(invariant_errors),
        "event_type_counts": _count_event_types(event_log),
        "player_action_counts": _count_player_actions(event_log),
    }


def format_scenario_summary(result):
    summary = build_scenario_summary(result)
    event_log = list(result.get("event_log") or [])
    lines = [
        "AI SMOKE SUMMARY",
        "scenario_id: %s" % summary["scenario_id"],
        "match_id: %s" % summary["match_id"],
        "completed: %s" % _format_bool(summary["completed"]),
        "result: %s" % summary["result"],
        "steps_run: %s" % summary["steps_run"],
        "event_count: %s" % summary["event_count"],
        "turn_number: %s" % summary["turn_number"],
        "final_active_player_id: %s" % summary["final_active_player_id"],
        "rejected_actions: %s" % summary["rejected_actions"],
        "invariant_errors: %s" % summary["invariant_error_count"],
        "",
        "COUNTS",
        "event_type_counts: %s" % _format_counts(summary["event_type_counts"]),
        "player_action_counts: %s" % _format_counts(summary["player_action_counts"]),
        "",
        "EVENTS",
    ]
    for index, event in enumerate(event_log, start=1):
        lines.append(
            "%s. turn=%s player=%s action=%s"
            % (
                index,
                event.get("turn_number"),
                event.get("player_id"),
                _event_type_key(event),
            )
        )
    return "\n".join(lines)


def _validate_result(result):
    if not isinstance(result, dict):
        raise EventLogSummaryError("Scenario result must be a dict.")
    missing = [field for field in REQUIRED_RESULT_FIELDS if field not in result]
    if missing:
        raise EventLogSummaryError("Missing scenario result fields: %s" % ", ".join(missing))
    if not isinstance(result.get("event_log"), list):
        raise EventLogSummaryError("Scenario result event_log must be a list.")
    if not isinstance(result.get("invariant_errors"), list):
        raise EventLogSummaryError("Scenario result invariant_errors must be a list.")


def _count_event_types(event_log):
    counts = {}
    for event in event_log:
        key = _event_type_key(event)
        counts[key] = counts.get(key, 0) + 1
    return _sorted_counts(counts)


def _count_player_actions(event_log):
    counts = {}
    for event in event_log:
        player_id = event.get("player_id") or "unknown"
        counts[player_id] = counts.get(player_id, 0) + 1
    return _sorted_counts(counts)


def _event_type_key(event):
    return str(event.get("action_type") or event.get("event_type") or "unknown")


def _sorted_counts(counts):
    return {key: counts[key] for key in sorted(counts)}


def _format_counts(counts):
    if not counts:
        return "-"
    return ", ".join("%s=%s" % (key, counts[key]) for key in sorted(counts))


def _format_bool(value):
    return "true" if bool(value) else "false"
