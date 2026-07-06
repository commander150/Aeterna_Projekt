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


def default_runtime_package_dir():
    return ENGINE_PYTHON_DIR.parent / "Godot" / "runtime_package"


def run_minimal_engine_smoke(runtime_package_dir=None, match_id="ENGINE-SMOKE-COMMAND-001"):
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

    result = {
        "match_id": state.match_id,
        "deck_id_a": deck_id_a,
        "deck_id_b": deck_id_b,
        "initial_snapshot": initial_snapshot,
        "post_snapshot": post_snapshot,
        "action_request": request,
        "request_valid": bool(validation.get("valid")),
        "action_response": response,
        "invariants_ok": not initial_invariants and not post_invariants,
        "diagnostics_count": len(initial_invariants) + len(post_invariants),
        "event_log": event_log(state),
    }
    return result


def format_report(result):
    initial = result["initial_snapshot"]
    post = result["post_snapshot"]
    response = result["action_response"]
    lines = [
        "MINIMAL ENGINE SMOKE REPORT",
        "match_id: %s" % result["match_id"],
        "deck_id_a: %s" % result["deck_id_a"],
        "deck_id_b: %s" % result["deck_id_b"],
        "initial_turn: %s" % initial["turn"],
        "initial_active_player_id: %s" % initial["active_player_id"],
        "initial_legal_action_count: %d" % int(initial["legal_action_summary"]["action_count"]),
        "initial_event_count: %d" % int(initial["event_log_summary"]["event_count"]),
        "request_valid: %s" % _format_bool(result["request_valid"]),
        "action_resolved: %s" % _format_bool(response.get("accepted")),
        "action_type: %s" % str((response.get("action") or {}).get("action_type", "")),
        "post_turn: %s" % post["turn"],
        "post_active_player_id: %s" % post["active_player_id"],
        "post_event_count: %d" % int(post["event_log_summary"]["event_count"]),
        "last_event_type: %s" % str(post["event_log_summary"].get("last_event_type")),
        "invariants_ok: %s" % _format_bool(result["invariants_ok"]),
        "diagnostics_count: %d" % int(result["diagnostics_count"]),
        "runtime_note: python engine facade is a reference smoke/backend candidate, not a final runtime decision",
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


def _format_bool(value):
    return "true" if value else "false"


if __name__ == "__main__":
    raise SystemExit(main())
