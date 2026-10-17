"""Command line interface for governed AETERNA document updates."""

from __future__ import annotations

import argparse
import json
import sys

from .impact import build_impact
from .model import WorkflowError
from .create_planner import build_create_plan
from .content import inspect_markdown
from .git_state import capture_git_state
from .planner import build_update_plan
from .resolver import record_payload, resolve_artifact
from .review import verify_review_file
from .transaction import apply_governance_gui_plan, apply_governance_plan, apply_plan
from tools.aeterna_artifacts.scanner import scan_repository
from tools.aeterna_artifacts.validation import CONTROLLED_VALUES


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

    baseline = commands.add_parser(
        "inspect-update-baseline",
        help="Inspect UPDATE baseline identity and metadata without writing.",
    )
    baseline.add_argument("artifact_id")
    baseline.add_argument("--repo", required=True)

    plan = commands.add_parser("plan-update", help="Build a deterministic no-write update plan.")
    plan.add_argument("--manifest", required=True)
    plan.add_argument("--repo", required=True)

    create = commands.add_parser("plan-create", help="Build a deterministic read-only CREATE plan.")
    create.add_argument("--manifest", required=True)
    create.add_argument("--repo", required=True)
    create.add_argument("--external-candidate-root")

    create_baseline = commands.add_parser("inspect-create-baseline", help="Read CREATE input options and current repository identity without writing.")
    create_baseline.add_argument("--repo", required=True)

    apply = commands.add_parser("apply", help="Apply one materialized governed plan transactionally.")
    apply.add_argument("plan")
    apply.add_argument("--repo", required=True)
    apply.add_argument("--review-dir", required=True)

    governance_apply = commands.add_parser(
        "apply-governance",
        help="Apply one high-risk UPDATE after an operation-bound interactive confirmation.",
    )
    governance_apply.add_argument("plan")
    governance_apply.add_argument("--repo", required=True)
    governance_apply.add_argument("--review-dir", required=True)

    gui_apply = commands.add_parser(
        "apply-governance-gui",
        help="Apply high-risk UPDATE with one process-local GUI challenge/response.",
    )
    gui_apply.add_argument("plan")
    gui_apply.add_argument("--repo", required=True)
    gui_apply.add_argument("--review-dir", required=True)

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
    if arguments.command == "inspect-update-baseline":
        resolved = resolve_artifact(arguments.repo, arguments.artifact_id)
        git = capture_git_state(resolved.root)
        snapshot = inspect_markdown(git.root / resolved.record.path)
        _print_json({
            "schema_version": "aeterna-document-update-baseline/0.1",
            "artifact_id": resolved.record.artifact_id,
            "path": resolved.record.path,
            "repository_root": str(git.root),
            "branch": git.branch,
            "head": git.head,
            "worktree_clean": not git.worktree_entries,
            "staging_empty": not git.staged_paths,
            "sha256": snapshot.sha256,
            "metadata_fingerprint": snapshot.metadata_fingerprint,
            "metadata": dict(snapshot.metadata.fields),
            "byte_convention": {
                "encoding": snapshot.encoding,
                "bom": snapshot.bom,
                "newline": snapshot.newline,
            },
        })
        return 0
    if arguments.command == "plan-update":
        _print_json(build_update_plan(arguments.repo, arguments.manifest))
        return 0
    if arguments.command == "plan-create":
        _print_json(build_create_plan(arguments.repo, arguments.manifest, arguments.external_candidate_root))
        return 0
    if arguments.command == "inspect-create-baseline":
        git = capture_git_state(arguments.repo)
        scan = scan_repository(git.root)
        _print_json({
            "schema_version": "aeterna-document-create-baseline/0.1",
            "repository_root": str(git.root),
            "branch": git.branch,
            "head": git.head,
            "worktree_clean": not git.worktree_entries,
            "staging_empty": not git.staged_paths,
            "diagnostics": [item.code for item in scan.diagnostics],
            "existing_artifact_ids": sorted(item.artifact_id for item in scan.artifacts),
            "controlled_values": {name: sorted(values) for name, values in CONTROLLED_VALUES.items()},
            "create_contract": {"kind": "document", "lifecycle": "active", "generated": False,
                                "integration": ["current", "pending_integration"]},
        })
        return 0
    if arguments.command == "apply":
        _print_json(apply_plan(arguments.plan, arguments.repo, arguments.review_dir))
        return 0
    if arguments.command == "apply-governance":
        _print_json(apply_governance_plan(arguments.plan, arguments.repo, arguments.review_dir))
        return 0
    if arguments.command == "apply-governance-gui":
        _print_json(apply_governance_gui_plan(arguments.plan, arguments.repo, arguments.review_dir))
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
