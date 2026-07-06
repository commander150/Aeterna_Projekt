"""Command entrypoint for the minimal Python engine smoke loop."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[2]
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
for module_dir in (ENGINE_DIR, AI_VS_AI_DIR):
    if str(module_dir) not in sys.path:
        sys.path.insert(0, str(module_dir))

from minimal_engine import (  # noqa: E402
    build_action_request,
    create_debug_snapshot,
    create_match,
    event_log,
    get_legal_actions,
    resolve_request,
    validate_invariants,
    validate_request,
)
from runtime_package_reader import load_runtime_package  # noqa: E402


RUNTIME_DECISION_NOTE = "Python engine facade is a reference smoke/backend candidate, not a final runtime decision."


def default_runtime_package_dir():
    return ENGINE_PYTHON_DIR.parent / "Godot" / "runtime_package"


def run_minimal_engine_smoke(runtime_package_dir=None, match_id="ENGINE-SMOKE-COMMAND-001"):
    return build_minimal_engine_smoke_report(runtime_package_dir, match_id=match_id)


def build_minimal_engine_smoke_report(runtime_package_dir=None, match_id="ENGINE-SMOKE-COMMAND-001"):
    package_dir = Path(runtime_package_dir) if runtime_package_dir is not None else default_runtime_package_dir()
    runtime_package = load_runtime_package(package_dir)
    deck_id_a, deck_id_b = _pick_two_decks(runtime_package)
    state = create_match(runtime_package, deck_id_a, deck_id_b, match_id=match_id)
    initial_invariants = validate_invariants(state, runtime_package)
    initial_legal_actions = get_legal_actions(state)
    initial_snapshot = create_debug_snapshot(state, initial_legal_actions, initial_invariants)

    request = build_action_request(state, initial_legal_actions[0])
    validation = validate_request(state, request, initial_legal_actions)
    response = resolve_request(state, request, initial_legal_actions)

    post_invariants = validate_invariants(state, runtime_package)
    post_legal_actions = get_legal_actions(state)
    post_snapshot = create_debug_snapshot(state, post_legal_actions, post_invariants)

    return {
        "schema_version": "minimal-engine-smoke-report-v0",
        "report_type": "minimal_engine_smoke",
        "runtime_decision_note": RUNTIME_DECISION_NOTE,
        "match": {
            "match_id": state.match_id,
            "initial_turn": initial_snapshot["turn"],
            "initial_active_player_id": initial_snapshot["active_player_id"],
            "post_turn": post_snapshot["turn"],
            "post_active_player_id": post_snapshot["active_player_id"],
        },
        "decks": {
            "deck_id_a": deck_id_a,
            "deck_id_b": deck_id_b,
        },
        "initial_snapshot_summary": _snapshot_summary(initial_snapshot),
        "post_action_snapshot_summary": _snapshot_summary(post_snapshot),
        "action_request": request,
        "action_response": {
            "request_valid": bool(validation.get("valid")),
            "accepted": bool(response.get("accepted")),
            "reason": response.get("reason"),
            "event_count": int(response.get("event_count", 0)),
            "action_type": str((response.get("action") or {}).get("action_type", "")),
        },
        "events": {
            "event_log": event_log(state),
            "initial_event_count": int(initial_snapshot["event_log_summary"]["event_count"]),
            "post_event_count": int(post_snapshot["event_log_summary"]["event_count"]),
            "last_event_type": post_snapshot["event_log_summary"].get("last_event_type"),
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
        "metadata": {
            "source": "tools.engine.run_minimal_engine_smoke",
            "runtime_package_dir": str(package_dir),
            "rules_scope": "minimal_end_turn_smoke",
        },
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
    lines = [
        "MINIMAL ENGINE SMOKE REPORT",
        "match_id: %s" % match["match_id"],
        "deck_id_a: %s" % decks["deck_id_a"],
        "deck_id_b: %s" % decks["deck_id_b"],
        "initial_turn: %s" % match["initial_turn"],
        "initial_active_player_id: %s" % match["initial_active_player_id"],
        "initial_legal_action_count: %d" % int(initial["legal_action_summary"]["action_count"]),
        "initial_event_count: %d" % int(events["initial_event_count"]),
        "request_valid: %s" % _format_bool(response["request_valid"]),
        "action_resolved: %s" % _format_bool(response["accepted"]),
        "action_type: %s" % response["action_type"],
        "post_turn: %s" % match["post_turn"],
        "post_active_player_id: %s" % match["post_active_player_id"],
        "post_event_count: %d" % int(events["post_event_count"]),
        "last_event_type: %s" % str(events["last_event_type"]),
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
    return parser


def _pick_two_decks(runtime_package):
    preferred = ["DECK-IGN-HAM-TEST-001", "DECK-IGN-LAN-TEST-001"]
    available = sorted(runtime_package.decks_by_id)
    selected = [deck_id for deck_id in preferred if deck_id in runtime_package.decks_by_id]
    if len(selected) >= 2:
        return selected[0], selected[1]
    for deck_id in available:
        if deck_id not in selected:
            selected.append(deck_id)
        if len(selected) == 2:
            return selected[0], selected[1]
    raise RuntimeError("The runtime package must contain at least two decks for minimal engine smoke.")


def _snapshot_summary(snapshot):
    return {
        "snapshot_type": snapshot["snapshot_type"],
        "visibility_mode": snapshot["visibility_mode"],
        "match_id": snapshot["match_id"],
        "turn": snapshot["turn"],
        "phase": snapshot["phase"],
        "active_player_id": snapshot["active_player_id"],
        "priority_player_id": snapshot["priority_player_id"],
        "player_count": len(snapshot["players"]),
        "legal_action_summary": dict(snapshot["legal_action_summary"]),
        "event_log_summary": dict(snapshot["event_log_summary"]),
        "diagnostics_summary": dict(snapshot["diagnostics_summary"]),
    }


def _format_bool(value):
    return "true" if value else "false"


if __name__ == "__main__":
    raise SystemExit(main())
