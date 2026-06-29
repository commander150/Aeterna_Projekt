"""Command entrypoint for the headless AI smoke scenario."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from event_log_summary import format_scenario_summary
    from runtime_package_reader import load_runtime_package
    from scenario_config import default_end_turn_smoke_config
    from scenario_runner import run_scenario
except ModuleNotFoundError:
    from .event_log_summary import format_scenario_summary
    from .runtime_package_reader import load_runtime_package
    from .scenario_config import default_end_turn_smoke_config
    from .scenario_runner import run_scenario


def default_runtime_package_dir():
    python_dir = Path(__file__).resolve().parents[2]
    return python_dir.parent / "Godot" / "runtime_package"


def run_default_smoke(runtime_package_dir=None):
    package_dir = Path(runtime_package_dir) if runtime_package_dir is not None else default_runtime_package_dir()
    runtime_package = load_runtime_package(package_dir)
    config = default_end_turn_smoke_config()
    result = run_scenario(config, runtime_package)
    return format_scenario_summary(result)


def main(argv=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        text = run_default_smoke(args.runtime_package_dir)
    except Exception as exc:
        stderr.write("AI smoke scenario failed: %s\n" % exc)
        return 1
    stdout.write(text)
    stdout.write("\n")
    return 0


def _build_parser():
    parser = argparse.ArgumentParser(description="Run the default AETERNA headless AI smoke scenario.")
    parser.add_argument(
        "--runtime-package-dir",
        default=None,
        help="Runtime package directory. Defaults to ../Godot/runtime_package relative to python/.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
