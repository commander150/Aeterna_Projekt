"""Single-use local confirmation for high-risk governance UPDATEs.

This is an interactive local approval, not authentication of a person's identity.
No approval file, command-line flag, or reusable bearer token is accepted.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys

from .model import fail


APPROVAL_SCHEMA = "aeterna-local-governance-approval/0.1"


def approval_binding(
    plan: dict[str, object], repository_root: Path, operation_id: str,
) -> dict[str, object]:
    """Bind the local decision to one operation and the complete planned scope."""
    return {
        "schema_version": APPROVAL_SCHEMA,
        "operation_id": operation_id,
        "repository_root": str(repository_root.resolve()),
        "artifact_id": plan["artifact_id"],
        "baseline_branch": plan["baseline"]["branch"],
        "baseline_head": plan["baseline"]["head"],
        "plan_semantic_sha256": plan["plan_semantic_sha256"],
        "expected_changed_paths": [item["path"] for item in plan["expected_changes"]],
        "change_class": plan["change"]["class"],
        "version_intent": plan["version"]["declared_intent"],
    }


def approval_review(
    binding: dict[str, object], *, decision: str = "NOT_CONFIRMED",
    consumed: bool = False,
) -> dict[str, object]:
    return {
        "method": "interactive-console",
        "identity_assurance": "local-interaction-only",
        "decision": decision,
        "consumed": consumed,
        "binding": dict(binding),
    }


@dataclass
class GovernanceApproval:
    """A confirmation exists only in this Apply invocation and can be consumed once."""

    binding: dict[str, object]
    consumed: bool = False

    def consume(
        self, plan: dict[str, object], repository_root: Path, operation_id: str,
    ) -> None:
        if self.consumed or self.binding != approval_binding(plan, repository_root, operation_id):
            fail("SEMANTIC_GOVERNANCE_APPROVAL_INVALID", "Governance approval is stale or already used.")
        self.consumed = True

    def review(self) -> dict[str, object]:
        return approval_review(self.binding, decision="CONFIRMED", consumed=self.consumed)


def confirm_governance_apply(
    plan: dict[str, object], repository_root: Path, operation_id: str,
) -> GovernanceApproval:
    """Show the complete scope and require an exact, operation-specific response."""
    if not sys.stdin.isatty() or not sys.stderr.isatty():
        fail(
            "SEMANTIC_GOVERNANCE_APPLY_BLOCKED",
            "Governance Apply requires a local interactive terminal and separate confirmation.",
        )
    binding = approval_binding(plan, repository_root, operation_id)
    scope = {
        "approval_binding": binding,
        "candidate_sha256": plan["candidate"]["sha256"],
        "metadata_delta": plan["metadata_delta"],
        "body_diff": plan["change"]["body_diff"],
        "dependency_impact": plan["impact"],
        "generated_outputs": plan["generated"],
    }
    challenge = f"APPLY {operation_id} {plan['plan_semantic_sha256']}"
    print("HIGH-RISK GOVERNANCE APPLY — review the exact scope:", file=sys.stderr)
    print(json.dumps(scope, ensure_ascii=False, indent=2), file=sys.stderr)
    print(f"To approve this one Apply, type exactly:\n{challenge}", file=sys.stderr, flush=True)
    try:
        response = sys.stdin.readline()
    except (KeyboardInterrupt, EOFError, OSError):
        fail("SEMANTIC_GOVERNANCE_APPROVAL_INTERRUPTED", "Interactive governance approval was interrupted.")
    if not response:
        fail("SEMANTIC_GOVERNANCE_APPROVAL_INTERRUPTED", "Interactive governance approval ended without a response.")
    if response.rstrip("\r\n") != challenge:
        fail("SEMANTIC_GOVERNANCE_APPROVAL_REJECTED", "Governance Apply was not explicitly confirmed.")
    return GovernanceApproval(binding)
