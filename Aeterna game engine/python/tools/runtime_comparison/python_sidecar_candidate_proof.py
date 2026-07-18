"""End-to-end sidecar candidate export, validation, and oracle proof."""

from __future__ import annotations

import argparse
import sys
from copy import deepcopy

from tools.runtime_comparison.artifact_comparator import (
    ArtifactComparatorInputError,
    compare_runtime_comparison_artifacts,
)
from tools.runtime_comparison.artifact_validator import (
    ArtifactValidatorInputError,
    validate_runtime_comparison_artifacts,
)
from tools.runtime_comparison.canonical_json import canonical_json_bytes
from tools.runtime_comparison.python_sidecar_candidate_exporter import (
    PythonSidecarCandidateExportError,
    RUNTIME_CANDIDATE,
    export_python_sidecar_candidate_artifacts,
)
from tools.runtime_comparison.runtime_comparison_artifact_builder import (
    CANONICAL_ARTIFACT_PATHS,
    FIXTURE_ID,
)
from tools.runtime_comparison.sidecar_protocol import PROTOCOL_VERSION


PROOF_RESULT_SCHEMA_VERSION = "aeterna-python-sidecar-candidate-proof-result-v1"
PROOF_RESULT_CONTRACT_TYPE = "python_sidecar_candidate_artifact_proof_result"


class PythonSidecarCandidateProofError(Exception):
    def __init__(self, code, message, *, category="technical"):
        self.code = str(code)
        self.message = str(message)
        self.category = str(category)
        super().__init__("%s: %s" % (self.code, self.message))


def run_python_sidecar_candidate_artifact_proof(
    fixture_path,
    reference_directory,
    candidate_output_directory,
    *,
    replace=False,
):
    """Export one candidate, validate it, and compare it to the oracle."""

    export_result = export_python_sidecar_candidate_artifacts(
        fixture_path,
        candidate_output_directory,
        replace=replace,
    )
    try:
        validation = validate_runtime_comparison_artifacts(
            candidate_output_directory,
            expected_fixture_id=FIXTURE_ID,
        )
        comparison = compare_runtime_comparison_artifacts(
            reference_directory,
            candidate_output_directory,
            expected_fixture_id=FIXTURE_ID,
        )
    except (ArtifactValidatorInputError, ArtifactComparatorInputError) as exc:
        raise PythonSidecarCandidateProofError(
            getattr(exc, "code", "SIDECAR_CANDIDATE_PROOF_INPUT_INVALID"),
            "Candidate proof input could not be validated or compared.",
        ) from exc

    canonical_records = [
        item
        for item in comparison.get("artifact_comparisons", [])
        if item.get("path") in CANONICAL_ARTIFACT_PATHS
    ]
    equal_count = sum(
        item.get("status") == "equal"
        and item.get("semantic_equal") is True
        and item.get("byte_equal") is True
        for item in canonical_records
    )
    manifest_record = next(
        (
            item
            for item in comparison.get("artifact_comparisons", [])
            if item.get("path") == "run_manifest.json"
        ),
        {},
    )
    validation_summary = _validation_summary(validation)
    comparison_summary = {
        "comparable": comparison.get("comparable") is True,
        "semantic_match": comparison.get("semantic_match") is True,
        "canonical_match": comparison.get("canonical_match") is True,
        "match": comparison.get("match") is True,
        "manifest_status": manifest_record.get("status"),
        "allowed_difference_codes": sorted(
            {item.get("code", "") for item in comparison.get("allowed_differences", [])}
        ),
        "blocking_error_count": comparison.get("summary", {}).get("blocking_error_count", 0),
        "warning_count": comparison.get("summary", {}).get("warning_count", 0),
    }
    diagnostics = []
    if not validation_summary["valid"]:
        diagnostics.append(
            {
                "code": "SIDECAR_CANDIDATE_VALIDATION_FAILED",
                "blocking": True,
                "message": "Candidate package validation failed.",
            }
        )
    if not comparison_summary["comparable"]:
        diagnostics.append(
            {
                "code": "SIDECAR_CANDIDATE_NOT_COMPARABLE",
                "blocking": True,
                "message": "Candidate package is not compatible with the reference package.",
            }
        )
    elif not comparison_summary["match"]:
        diagnostics.append(
            {
                "code": "SIDECAR_CANDIDATE_COMPARISON_MISMATCH",
                "blocking": True,
                "message": "Candidate canonical gameplay artifacts do not match the oracle.",
            }
        )

    lifecycle = export_result.get("lifecycle", {})
    lifecycle_succeeded = bool(
        lifecycle.get("startup_succeeded")
        and lifecycle.get("health_succeeded")
        and lifecycle.get("fixture_succeeded")
        and lifecycle.get("shutdown_succeeded")
        and lifecycle.get("process_exit_code") == 0
        and lifecycle.get("process_stopped")
        and lifecycle.get("listener_closed")
        and lifecycle.get("stdout_clean")
        and lifecycle.get("stderr_clean")
        and lifecycle.get("separate_process")
        and not lifecycle.get("forced_termination_used")
    )
    success = bool(
        export_result.get("success")
        and lifecycle_succeeded
        and validation_summary["valid"]
        and comparison_summary["comparable"]
        and comparison_summary["semantic_match"]
        and comparison_summary["canonical_match"]
        and comparison_summary["match"]
        and len(canonical_records) == len(CANONICAL_ARTIFACT_PATHS)
        and equal_count == len(CANONICAL_ARTIFACT_PATHS)
        and not diagnostics
    )
    if success:
        outcome = "success"
    elif validation_summary["valid"] and comparison_summary["comparable"]:
        outcome = "comparison_mismatch"
    else:
        outcome = "compatibility_or_validation_failure"

    result = {
        "schema_version": PROOF_RESULT_SCHEMA_VERSION,
        "contract_type": PROOF_RESULT_CONTRACT_TYPE,
        "fixture_id": export_result["fixture_id"],
        "runtime_candidate": RUNTIME_CANDIDATE,
        "transport_protocol": PROTOCOL_VERSION,
        "export": {
            "success": export_result["success"],
            "manifest_sha256": export_result["manifest_sha256"],
            "canonical_artifacts": deepcopy(export_result["canonical_artifacts"]),
        },
        "lifecycle": deepcopy(export_result["lifecycle"]),
        "validation": validation_summary,
        "comparison": comparison_summary,
        "canonical_artifact_count": len(canonical_records),
        "equal_canonical_artifact_count": equal_count,
        "outcome": outcome,
        "success": success,
        "diagnostics": diagnostics,
    }
    canonical_json_bytes(result)
    return result


def _validation_summary(validation):
    artifact_results = validation.get("artifact_results") or []
    summary = validation.get("summary") or {}
    return {
        "valid": validation.get("valid") is True,
        "error_count": summary.get("error_count", 0),
        "warning_count": summary.get("warning_count", 0),
        "artifact_count_present": summary.get("artifact_count_present", 0),
        "canonical_integrity_valid_count": sum(
            item.get("path") in CANONICAL_ARTIFACT_PATHS and item.get("integrity_valid") is True
            for item in artifact_results
        ),
        "semantic_check_count": summary.get("semantic_check_count", 0),
        "semantic_check_failed_count": summary.get("semantic_check_failed_count", 0),
        "warning_codes": sorted({item.get("code", "") for item in validation.get("warnings", [])}),
    }


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise PythonSidecarCandidateProofError(
            "SIDECAR_CANDIDATE_PROOF_CLI_INVALID",
            "Python sidecar candidate proof CLI arguments are invalid.",
        )


def _build_parser():
    parser = _ArgumentParser(description="Export and compare a Python sidecar candidate package.")
    parser.add_argument("--fixture", required=True, help="Fixture-root-relative fixture.json path.")
    parser.add_argument("--reference", required=True, help="Reference artifact directory.")
    parser.add_argument("--candidate-output", required=True, help="Candidate output directory.")
    parser.add_argument("--replace", action="store_true", help="Replace only the explicit candidate output.")
    return parser


def main(argv=None):
    try:
        arguments = _build_parser().parse_args(argv)
        result = run_python_sidecar_candidate_artifact_proof(
            arguments.fixture,
            arguments.reference,
            arguments.candidate_output,
            replace=arguments.replace,
        )
    except PythonSidecarCandidateProofError as exc:
        print("%s: %s" % (exc.code, exc.message), file=sys.stderr)
        return 3 if exc.category == "technical" else 2
    except PythonSidecarCandidateExportError as exc:
        print("%s: %s" % (exc.code, exc.message), file=sys.stderr)
        return 3 if exc.category == "technical" else 2
    except (OSError, ValueError):
        print(
            "SIDECAR_CANDIDATE_PROOF_TECHNICAL_ERROR: Candidate proof could not run.",
            file=sys.stderr,
        )
        return 3
    sys.stdout.write(canonical_json_bytes(result).decode("utf-8"))
    if result["success"]:
        return 0
    if result["outcome"] == "comparison_mismatch":
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROOF_RESULT_CONTRACT_TYPE",
    "PROOF_RESULT_SCHEMA_VERSION",
    "PythonSidecarCandidateProofError",
    "main",
    "run_python_sidecar_candidate_artifact_proof",
]
