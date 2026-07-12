"""Run a minimal AI-vs-AI episode over the Python MinimalEngineEnvironment."""

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

from minimal_engine_environment import MinimalEngineEnvironment  # noqa: E402
from runtime_package_reader import load_runtime_package  # noqa: E402


def default_runtime_package_dir():
    return ENGINE_PYTHON_DIR.parent / "Godot" / "runtime_package"


def run_episode(runtime_package_dir=None, max_steps=8, match_id="AI-VS-AI-EPISODE-001"):
    package_dir = Path(runtime_package_dir) if runtime_package_dir is not None else default_runtime_package_dir()
    runtime_package = load_runtime_package(package_dir)
    environment = MinimalEngineEnvironment(runtime_package)
    return environment.run_episode(max_steps=max_steps, match_id=match_id)


def format_episode_summary(episode):
    action_counts = {}
    for step in episode["trajectory"]:
        action_type = step["selected_action_type"]
        action_counts[action_type] = action_counts.get(action_type, 0) + 1
    action_counts_text = ", ".join("%s=%s" % (key, action_counts[key]) for key in sorted(action_counts))
    if not action_counts_text:
        action_counts_text = "none"
    return "\n".join(
        [
            "MINIMAL AI VS AI EPISODE",
            "match_id: %s" % episode["match_id"],
            "steps_run: %s" % episode["steps_run"],
            "max_steps: %s" % episode["max_steps"],
            "stop_reason: %s" % episode["stop_reason"],
            "final_state_version: %s" % episode["final_observation"]["state_version"],
            "final_active_player_id: %s" % episode["final_observation"]["active_player_id"],
            "event_count: %s" % episode["transition_summary"]["event_count"],
            "action_counts: %s" % action_counts_text,
            "diagnostics_count: %s" % episode["diagnostics_summary"]["count"],
            "runtime_note: MinimalEngineEnvironment is a reference smoke/backend candidate, not a final runtime decision.",
        ]
    )


def main(argv=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        episode = run_episode(args.runtime_package_dir, max_steps=args.max_steps, match_id=args.match_id)
        if args.json:
            stdout.write(json.dumps(episode, ensure_ascii=False, indent=2))
        else:
            stdout.write(format_episode_summary(episode))
        stdout.write("\n")
        return 0
    except Exception as exc:
        stderr.write("Minimal AI-vs-AI episode failed: %s\n" % exc)
        return 1


def _build_parser():
    parser = argparse.ArgumentParser(description="Run the minimal AETERNA AI-vs-AI episode stub.")
    parser.add_argument("--runtime-package-dir", default=None)
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--match-id", default="AI-VS-AI-EPISODE-001")
    parser.add_argument("--json", action="store_true")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
