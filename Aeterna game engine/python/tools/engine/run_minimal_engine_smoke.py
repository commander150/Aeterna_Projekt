"""Command entrypoint for the minimal Python engine smoke loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[2]
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
for module_dir in (ENGINE_DIR, AI_VS_AI_DIR):
    if str(module_dir) not in sys.path:
        sys.path.insert(0, str(module_dir))

from minimal_engine_session import MinimalEngineSession  # noqa: E402
from runtime_package_reader import load_runtime_package  # noqa: E402


RUNTIME_DECISION_NOTE = "Python engine facade is a reference smoke/backend candidate, not a final runtime decision."


def default_runtime_package_dir():
    return ENGINE_PYTHON_DIR.parent / "Godot" / "runtime_package"


def run_minimal_engine_smoke(runtime_package_dir=None, match_id="ENGINE-SMOKE-COMMAND-001"):
    return build_minimal_engine_smoke_report(runtime_package_dir, match_id=match_id)


def build_minimal_engine_debug_export(runtime_package_dir=None, match_id="ENGINE-SMOKE-COMMAND-001"):
    context = _run_smoke_session(runtime_package_dir, match_id)
    session = context["session"]
    return session.export_debug_session_state()


def build_minimal_engine_smoke_report(runtime_package_dir=None, match_id="ENGINE-SMOKE-COMMAND-001"):
    context = _run_smoke_session(runtime_package_dir, match_id)
    session = context["session"]
    package_dir = Path(runtime_package_dir) if runtime_package_dir is not None else default_runtime_package_dir()
    state = session.state
    deck_id_a = session.deck_id_a
    deck_id_b = session.deck_id_b
    initial_snapshot = context["initial_snapshot"]
    post_snapshot = session.get_debug_snapshot()
    initial_invariants = context["initial_invariants"]
    post_invariants = session.get_diagnostics()
    action_response = dict(session.get_last_action_response())
    action_response["request_valid"] = bool(context["validation"].get("valid"))
    transition_summary = session.get_transition_summary()
    debug_session_state = session.export_debug_session_state()

    return {
        "schema_version": "minimal-engine-smoke-report-v0",
        "report_type": "minimal_engine_smoke",
        "runtime_decision_note": RUNTIME_DECISION_NOTE,
        "match": {
            "match_id": state.match_id,
            "initial_state_version": initial_snapshot["state_version"],
            "initial_turn": initial_snapshot["turn"],
            "initial_active_player_id": initial_snapshot["active_player_id"],
            "post_state_version": post_snapshot["state_version"],
            "post_turn": post_snapshot["turn"],
            "post_active_player_id": post_snapshot["active_player_id"],
        },
        "decks": {
            "deck_id_a": deck_id_a,
            "deck_id_b": deck_id_b,
        },
        "initial_snapshot_summary": _snapshot_summary(initial_snapshot),
        "post_action_snapshot_summary": _snapshot_summary(post_snapshot),
        "initial_action_space": context["initial_action_space"],
        "action_request": context["request"],
        "action_response": action_response,
        "events": {
            "event_log": session.get_event_log(),
            "initial_event_count": int(initial_snapshot["event_log_summary"]["event_count"]),
            "post_event_count": int(post_snapshot["event_log_summary"]["event_count"]),
            "last_event_type": post_snapshot["event_log_summary"].get("last_event_type"),
            "last_event_sequence": post_snapshot["event_log_summary"].get("last_event_sequence"),
        },
        "invariants": {
            "ok": not initial_invariants and not post_invariants,
            "initial_errors": list(initial_invariants),
            "post_action_errors": list(post_invariants),
        },
        "diagnostics": {
            "count": len(initial_invariants) + len(post_invariants),
            "blocking_errors": len(initial_invariants) + len(post_invariants),
            "warnings": 0,
        },
        "response_history_count": len(session.get_action_response_history()),
        "transition_summary": transition_summary,
        "debug_session_state_summary": _debug_session_state_summary(debug_session_state),
        "metadata": {
            "source": "tools.engine.run_minimal_engine_smoke",
            "runtime_package_dir": str(package_dir),
            "rules_scope": "minimal_end_turn_smoke",
        },
    }


def _run_smoke_session(runtime_package_dir=None, match_id="ENGINE-SMOKE-COMMAND-001"):
    package_dir = Path(runtime_package_dir) if runtime_package_dir is not None else default_runtime_package_dir()
    runtime_package = load_runtime_package(package_dir)
    session = MinimalEngineSession(runtime_package)
    session.create_match(match_id=match_id)
    initial_invariants = session.get_diagnostics()
    initial_action_space = session.get_action_space()
    initial_legal_actions = list(initial_action_space["actions"])
    initial_snapshot = session.get_debug_snapshot()

    request = session.build_action_request(initial_legal_actions[0])
    validation = session.validate_action_request(request)
    session.submit_action_request(request)
    return {
        "session": session,
        "initial_invariants": initial_invariants,
        "initial_action_space": initial_action_space,
        "initial_snapshot": initial_snapshot,
        "request": request,
        "validation": validation,
    }


def format_report(report):
    match = report["match"]
    decks = report["decks"]
    initial = report["initial_snapshot_summary"]
    post = report["post_action_snapshot_summary"]
    response = report["action_response"]
    events = report["events"]
    invariants = report["invariants"]
    diagnostics = report["diagnostics"]
    transition_summary = report["transition_summary"]
    lines = [
        "MINIMAL ENGINE SMOKE REPORT",
        "match_id: %s" % match["match_id"],
        "deck_id_a: %s" % decks["deck_id_a"],
        "deck_id_b: %s" % decks["deck_id_b"],
        "initial_state_version: %s" % match["initial_state_version"],
        "initial_turn: %s" % match["initial_turn"],
        "initial_active_player_id: %s" % match["initial_active_player_id"],
        "initial_legal_action_count: %d" % int(initial["legal_action_summary"]["action_count"]),
        "initial_event_count: %d" % int(events["initial_event_count"]),
        "request_valid: %s" % _format_bool(response["request_valid"]),
        "action_resolved: %s" % _format_bool(response["accepted"]),
        "action_type: %s" % response["action_type"],
        "post_state_version: %s" % match["post_state_version"],
        "post_turn: %s" % match["post_turn"],
        "post_active_player_id: %s" % match["post_active_player_id"],
        "post_event_count: %d" % int(events["post_event_count"]),
        "last_event_sequence: %s" % str(events["last_event_sequence"]),
        "last_event_type: %s" % str(events["last_event_type"]),
        "response_history_count: %d" % int(transition_summary["response_count"]),
        "accepted_response_count: %d" % int(transition_summary["accepted_response_count"]),
        "rejected_response_count: %d" % int(transition_summary["rejected_response_count"]),
        "invariants_ok: %s" % _format_bool(invariants["ok"]),
        "diagnostics_count: %d" % int(diagnostics["count"]),
        "runtime_note: %s" % report["runtime_decision_note"],
    ]
    return "\n".join(lines)


def main(argv=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.json_debug_export:
            result = build_minimal_engine_debug_export(args.runtime_package_dir, match_id=args.match_id)
            stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            result = run_minimal_engine_smoke(args.runtime_package_dir, match_id=args.match_id)
            stdout.write(format_report(result))
        stdout.write("\n")
        return 0
    except Exception as exc:
        stderr.write("Minimal engine smoke failed: %s\n" % exc)
        return 1


def _build_parser():
    parser = argparse.ArgumentParser(description="Run the minimal AETERNA Python engine smoke loop.")
    parser.add_argument(
        "--runtime-package-dir",
        default=None,
        help="Runtime package directory. Defaults to ../Godot/runtime_package relative to python/.",
    )
    parser.add_argument("--match-id", default="ENGINE-SMOKE-COMMAND-001")
    parser.add_argument(
        "--json-debug-export",
        action="store_true",
        help="Print only the JSON debug session state export to stdout.",
    )
    return parser


def _snapshot_summary(snapshot):
    return {
        "snapshot_type": snapshot["snapshot_type"],
        "visibility_mode": snapshot["visibility_mode"],
        "match_id": snapshot["match_id"],
        "turn": snapshot["turn"],
        "phase": snapshot["phase"],
        "active_player_id": snapshot["active_player_id"],
        "state_version": snapshot["state_version"],
        "priority_player_id": snapshot["priority_player_id"],
        "player_count": len(snapshot["players"]),
        "legal_action_summary": dict(snapshot["legal_action_summary"]),
        "event_log_summary": dict(snapshot["event_log_summary"]),
        "diagnostics_summary": dict(snapshot["diagnostics_summary"]),
    }


def _debug_session_state_summary(debug_session_state):
    transition_summary = debug_session_state["transition_summary"]
    return {
        "contract_type": debug_session_state["contract_type"],
        "state_version": transition_summary["state_version"],
        "response_count": transition_summary["response_count"],
        "event_count": transition_summary["event_count"],
        "replay_support": debug_session_state["metadata"]["replay_support"],
    }


def _format_bool(value):
    return "true" if value else "false"


if __name__ == "__main__":
    raise SystemExit(main())
