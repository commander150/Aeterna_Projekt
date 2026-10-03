"""Command line interface for governed AETERNA document updates."""

from __future__ import annotations

import argparse
import json
import sys

from .impact import build_impact
from .model import WorkflowError
from .planner import build_update_plan
from .resolver import record_payload, resolve_artifact
from .review import verify_review_file
from .transaction import apply_plan


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Governed AETERNA document workflow.")
    commands = parser.add_subparsers(dest="command", required=True)

    resolve = commands.add_parser("resolve", help="Resolve an artifact from a fresh scan.")
    resolve.add_argument("artifact_id")
    resolve.add_argument("--repo", required=True)
    resolve.add_argument("--json", action="store_true")

    impact = commands.add_parser("impact", help="Inspect dependency impact.")
    impact.add_argument("artifact_id")
    impact.add_argument("--repo", required=True)
    impact.add_argument("--transitive", action="store_true")
    impact.add_argument("--json", action="store_true")

    plan = commands.add_parser("plan-update", help="Build a deterministic no-write update plan.")
    plan.add_argument("--manifest", required=True)
    plan.add_argument("--repo", required=True)

    apply = commands.add_parser("apply", help="Apply one materialized update plan transactionally.")
    apply.add_argument("plan")
    apply.add_argument("--repo", required=True)
    apply.add_argument("--review-dir", required=True)

    verify = commands.add_parser("verify-review", help="Verify historical review evidence.")
    verify.add_argument("review")
    return parser


def _print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _run(arguments: argparse.Namespace) -> int:
    if arguments.command == "resolve":
        resolved = resolve_artifact(arguments.repo, arguments.artifact_id)
        payload = record_payload(resolved.record)
        if arguments.json:
            _print_json(payload)
        else:
            print(f"{payload['artifact_id']}\t{payload['path']}")
        return 0
    if arguments.command == "impact":
        resolved = resolve_artifact(arguments.repo, arguments.artifact_id)
        payload = build_impact(
            resolved.scan.artifacts,
            arguments.artifact_id,
            include_transitive=arguments.transitive,
        )
        if arguments.json:
            _print_json(payload)
        else:
            print(f"TARGET\t{payload['artifact_id']}")
            for item in payload["direct_reverse_dependencies"]:
                print(f"DEPENDENT\t{item['artifact_id']}\t{item['impact']}")
        return 0
    if arguments.command == "plan-update":
        _print_json(build_update_plan(arguments.repo, arguments.manifest))
        return 0
    if arguments.command == "apply":
        _print_json(apply_plan(arguments.plan, arguments.repo, arguments.review_dir))
        return 0
    if arguments.command == "verify-review":
        review = verify_review_file(arguments.review)
        _print_json({
            "status": "PASS",
            "schema_version": review["schema_version"],
            "review_semantic_sha256": review["review_semantic_sha256"],
        })
        return 0
    return 2


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    arguments = _parser().parse_args(argv)
    try:
        return _run(arguments)
    except WorkflowError as exc:
        _print = {
            "status": "ERROR",
            "exit_code": exc.exit_code,
            "diagnostics": [
                {
                    "code": item.code,
                    "severity": item.severity.value,
                    "message": item.message,
                    "field": item.field,
                }
                for item in exc.diagnostics
            ],
        }
        print(json.dumps(_print, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
