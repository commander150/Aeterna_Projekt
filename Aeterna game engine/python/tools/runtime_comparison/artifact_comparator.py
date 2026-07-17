"""Read-only comparison of validated runtime-comparison artifact packages."""

from __future__ import annotations

import argparse
import json
import ntpath
import sys
from collections import Counter
from pathlib import Path

from tools.runtime_comparison.artifact_validator import (
    ArtifactValidatorInputError,
    CANONICAL_ARTIFACT_PATHS,
    JSONL_ARTIFACT_PATHS,
    REQUIRED_ARTIFACT_PATHS,
    validate_runtime_comparison_artifacts,
)
from tools.runtime_comparison.canonical_json import (
    canonical_json_bytes,
    sha256_bytes,
)


COMPARISON_RESULT_SCHEMA_VERSION = "aeterna-runtime-comparison-result-v1"
COMPARISON_RESULT_CONTRACT_TYPE = "runtime_comparison_result"
SUPPORTED_COMPARISON_LEVELS = (
    "canonical_bytes",
    "semantic",
    "informational",
)
MAX_MISMATCHES_PER_ARTIFACT = 100
MAX_MISMATCHES_TOTAL = 500

_ALLOWED_MANIFEST_FIELDS = (
    ("runtime_candidate", "RUNTIME_CANDIDATE_DIFFERENCE"),
    ("implementation_language", "IMPLEMENTATION_LANGUAGE_DIFFERENCE"),
    ("runtime_version", "RUNTIME_VERSION_DIFFERENCE"),
    ("operating_system", "OPERATING_SYSTEM_DIFFERENCE"),
    ("architecture", "ARCHITECTURE_DIFFERENCE"),
    ("build_identifier", "BUILD_IDENTIFIER_DIFFERENCE"),
    ("implementation_specific", "IMPLEMENTATION_SPECIFIC_DIFFERENCE"),
    ("known_deviations", "DECLARED_KNOWN_DEVIATION_DIFFERENCE"),
)
_COMPATIBILITY_FIELDS = (
    ("fixture_id", "FIXTURE_ID_MISMATCH"),
    ("fixture_schema_version", "FIXTURE_SCHEMA_MISMATCH"),
    ("oracle_id", "ORACLE_ID_MISMATCH"),
    ("oracle_version", "ORACLE_VERSION_MISMATCH"),
    ("canonicalization_profile", "CANONICALIZATION_PROFILE_MISMATCH"),
    ("comparison_profile", "COMPARISON_PROFILE_MISMATCH"),
)
_PHASE_RANKS = {
    "validation": 10,
    "compatibility": 20,
    "comparison": 30,
}


class ArtifactComparatorInputError(ValueError):
    """Technical input error that prevents a comparison result."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class _ComparisonContext:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.allowed_differences = []

    def error(self, phase, artifact, code, message, **details):
        self.errors.append(_issue(phase, artifact, code, message, details, True))

    def warning(self, phase, artifact, code, message, **details):
        self.warnings.append(_issue(phase, artifact, code, message, details, False))

    def allowed(self, artifact, code, message, **details):
        self.allowed_differences.append(
            _issue("compatibility", artifact, code, message, details, False)
        )


class _DiffBudget:
    def __init__(self, per_artifact, total):
        self.per_artifact_limit = per_artifact
        self.total_limit = total
        self.stored_total = 0


def _issue(phase, artifact, code, message, details, blocking):
    return {
        "artifact": artifact,
        "blocking": blocking,
        "code": code,
        "details": {
            key: _sanitize_result_value(details[key]) for key in sorted(details)
        },
        "message": message,
        "phase": phase,
    }


def _sanitize_result_value(value):
    if isinstance(value, dict):
        return {
            str(key): _sanitize_result_value(value[key])
            for key in sorted(value, key=str)
        }
    if isinstance(value, (list, tuple)):
        return [_sanitize_result_value(item) for item in value]
    if isinstance(value, str) and (ntpath.isabs(value) or value.startswith("/")):
        return "<absolute-path-redacted>"
    return value


def _issue_sort_key(issue):
    return (
        _PHASE_RANKS[issue["phase"]],
        issue["artifact"],
        issue["code"],
        json.dumps(
            issue["details"],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
    )


def _json_type(value):
    if value is None:
        return "null"
    if type(value) is bool:
        return "boolean"
    if type(value) is int:
        return "integer"
    if type(value) is float:
        return "number"
    if type(value) is str:
        return "string"
    if type(value) is list:
        return "array"
    if type(value) is dict:
        return "object"
    return "invalid"


def _json_pointer_child(pointer, token):
    escaped = str(token).replace("~", "~0").replace("/", "~1")
    return "%s/%s" % (pointer, escaped)


def _value_summary(value, missing=False):
    if missing:
        return {"type": "missing"}
    value_type = _json_type(value)
    if value_type in {"null", "boolean", "integer", "number"}:
        return value
    if value_type == "string":
        if len(value) <= 160:
            return value
        return {
            "length": len(value),
            "prefix": value[:120],
            "truncated": True,
            "type": "string",
        }
    if value_type == "array":
        return {"length": len(value), "type": "array"}
    if value_type == "object":
        keys = sorted(value)
        return {
            "key_count": len(keys),
            "keys": keys[:12],
            "truncated": len(keys) > 12,
            "type": "object",
        }
    return {"type": "invalid"}


def _typed_fingerprint(value):
    value_type = _json_type(value)
    if value_type == "object":
        return (
            value_type,
            tuple((key, _typed_fingerprint(value[key])) for key in sorted(value)),
        )
    if value_type == "array":
        return (value_type, tuple(_typed_fingerprint(item) for item in value))
    return (value_type, value)


def _mismatch_record(
    artifact_path,
    pointer,
    mismatch_type,
    reference,
    candidate,
    blocking,
    message,
    *,
    reference_missing=False,
    candidate_missing=False,
):
    return {
        "artifact_path": artifact_path,
        "blocking": blocking,
        "candidate_summary": _value_summary(candidate, candidate_missing),
        "candidate_type": "missing" if candidate_missing else _json_type(candidate),
        "json_pointer": pointer,
        "message": message,
        "mismatch_type": mismatch_type,
        "reference_summary": _value_summary(reference, reference_missing),
        "reference_type": "missing" if reference_missing else _json_type(reference),
    }


def _semantic_diff(
    reference,
    candidate,
    artifact_path,
    *,
    blocking=True,
    budget=None,
):
    """Return deterministic, explicitly JSON-type-sensitive mismatch details."""

    if budget is None:
        budget = _DiffBudget(MAX_MISMATCHES_PER_ARTIFACT, MAX_MISMATCHES_TOTAL)
    details = []
    mismatch_count = 0
    truncated = False

    def add(record):
        nonlocal mismatch_count, truncated
        mismatch_count += 1
        if (
            len(details) < budget.per_artifact_limit
            and budget.stored_total < budget.total_limit
        ):
            details.append(record)
            budget.stored_total += 1
        else:
            truncated = True

    def visit(reference_value, candidate_value, pointer):
        reference_type = _json_type(reference_value)
        candidate_type = _json_type(candidate_value)
        if reference_type != candidate_type:
            add(
                _mismatch_record(
                    artifact_path,
                    pointer,
                    "type_mismatch",
                    reference_value,
                    candidate_value,
                    blocking,
                    "JSON value types differ.",
                )
            )
            return
        if reference_type == "object":
            reference_keys = set(reference_value)
            candidate_keys = set(candidate_value)
            for key in sorted(reference_keys | candidate_keys):
                child_pointer = _json_pointer_child(pointer, key)
                if key not in candidate_value:
                    add(
                        _mismatch_record(
                            artifact_path,
                            child_pointer,
                            "field_missing",
                            reference_value[key],
                            None,
                            blocking,
                            "Candidate object is missing a reference field.",
                            candidate_missing=True,
                        )
                    )
                elif key not in reference_value:
                    add(
                        _mismatch_record(
                            artifact_path,
                            child_pointer,
                            "unexpected_field",
                            None,
                            candidate_value[key],
                            blocking,
                            "Candidate object contains an unexpected field.",
                            reference_missing=True,
                        )
                    )
                else:
                    visit(reference_value[key], candidate_value[key], child_pointer)
            return
        if reference_type == "array":
            if len(reference_value) != len(candidate_value):
                add(
                    _mismatch_record(
                        artifact_path,
                        pointer,
                        "list_length_mismatch",
                        reference_value,
                        candidate_value,
                        blocking,
                        "Array lengths differ.",
                    )
                )
            elif reference_value != candidate_value:
                reference_fingerprints = [
                    _typed_fingerprint(item) for item in reference_value
                ]
                candidate_fingerprints = [
                    _typed_fingerprint(item) for item in candidate_value
                ]
                if (
                    reference_fingerprints != candidate_fingerprints
                    and Counter(reference_fingerprints) == Counter(candidate_fingerprints)
                ):
                    add(
                        _mismatch_record(
                            artifact_path,
                            pointer,
                            "ordering_mismatch",
                            reference_value,
                            candidate_value,
                            blocking,
                            "Array items are equal as a multiset but ordered differently.",
                        )
                    )
            for index in range(min(len(reference_value), len(candidate_value))):
                visit(
                    reference_value[index],
                    candidate_value[index],
                    _json_pointer_child(pointer, index),
                )
            return
        if reference_value != candidate_value:
            add(
                _mismatch_record(
                    artifact_path,
                    pointer,
                    "value_mismatch",
                    reference_value,
                    candidate_value,
                    blocking,
                    "JSON values differ.",
                )
            )

    visit(reference, candidate, "")
    return {
        "details": details,
        "details_truncated": truncated,
        "mismatch_count": mismatch_count,
    }


def _validation_artifact_map(validation):
    return {
        item["path"]: item
        for item in validation.get("artifact_results", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }


def _validate_input(directory, side, expected_fixture_id):
    try:
        return validate_runtime_comparison_artifacts(
            directory,
            expected_fixture_id=expected_fixture_id,
        )
    except ArtifactValidatorInputError as exc:
        raise ArtifactComparatorInputError(
            "%s_INPUT_%s" % (side.upper(), exc.code),
            "%s artifact input cannot be validated." % side.capitalize(),
        ) from exc


def _read_manifest_if_safe(directory, validation):
    artifact = _validation_artifact_map(validation).get("run_manifest.json", {})
    if not artifact.get("parsed") or not artifact.get("canonical_bytes_valid"):
        return None
    try:
        return json.loads((directory / "run_manifest.json").read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ArtifactComparatorInputError(
            "MANIFEST_READ_FAILED",
            "Validated run manifest could not be read.",
        ) from exc


def _read_valid_package(directory):
    package = {}
    try:
        for path in REQUIRED_ARTIFACT_PATHS:
            data = (directory / path).read_bytes()
            package[path] = {
                "bytes": data,
                "parsed": (
                    [json.loads(line) for line in data.decode("utf-8").splitlines()]
                    if path in JSONL_ARTIFACT_PATHS
                    else json.loads(data.decode("utf-8"))
                ),
            }
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ArtifactComparatorInputError(
            "VALIDATED_PACKAGE_READ_FAILED",
            "Validated artifact package could not be read consistently.",
        ) from exc
    return package


def _manifest_artifact_records(manifest):
    records = manifest.get("canonical_artifacts") if isinstance(manifest, dict) else None
    if not isinstance(records, list):
        return [], {}
    paths = []
    by_path = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            continue
        path = record["path"]
        paths.append(path)
        by_path.setdefault(path, []).append(record)
    return paths, by_path


def _compatibility_check(field, code, reference, candidate, context, checks):
    reference_value = reference.get(field)
    candidate_value = candidate.get(field)
    passed = _typed_fingerprint(reference_value) == _typed_fingerprint(candidate_value)
    checks.append({"code": code, "field": field, "passed": passed})
    if not passed:
        context.error(
            "compatibility",
            "run_manifest.json",
            code,
            "Reference and candidate manifest compatibility fields differ.",
            candidate=_value_summary(candidate_value),
            field=field,
            reference=_value_summary(reference_value),
        )


def _compare_manifest_compatibility(reference, candidate, context):
    checks = []
    if not isinstance(reference, dict) or not isinstance(candidate, dict):
        return {
            "checks": checks,
            "passed": False,
            "supported_comparison_levels": list(SUPPORTED_COMPARISON_LEVELS),
        }

    for field, code in _COMPATIBILITY_FIELDS:
        _compatibility_check(field, code, reference, candidate, context, checks)

    reference_paths, reference_records = _manifest_artifact_records(reference)
    candidate_paths, candidate_records = _manifest_artifact_records(candidate)
    artifact_profile_passed = reference_paths == candidate_paths
    if artifact_profile_passed:
        for path in reference_paths:
            reference_entries = reference_records.get(path, [])
            candidate_entries = candidate_records.get(path, [])
            if len(reference_entries) != 1 or len(candidate_entries) != 1:
                artifact_profile_passed = False
                break
            reference_entry = reference_entries[0]
            candidate_entry = candidate_entries[0]
            for field in ("comparison_level", "canonicalization", "media_type"):
                if reference_entry.get(field) != candidate_entry.get(field):
                    artifact_profile_passed = False
                    break
            if not artifact_profile_passed:
                break
    checks.append(
        {
            "code": "ARTIFACT_PROFILE_MISMATCH",
            "field": "canonical_artifacts",
            "passed": artifact_profile_passed,
        }
    )
    if not artifact_profile_passed:
        context.error(
            "compatibility",
            "run_manifest.json",
            "ARTIFACT_PROFILE_MISMATCH",
            "Canonical artifact path order or comparison profile differs.",
        )

    mapping_passed = _typed_fingerprint(reference.get("contract_schema_mapping")) == (
        _typed_fingerprint(candidate.get("contract_schema_mapping"))
    )
    checks.append(
        {
            "code": "CONTRACT_SCHEMA_MAPPING_MISMATCH",
            "field": "contract_schema_mapping",
            "passed": mapping_passed,
        }
    )
    if not mapping_passed:
        context.error(
            "compatibility",
            "run_manifest.json",
            "CONTRACT_SCHEMA_MAPPING_MISMATCH",
            "Reference and candidate contract schema mappings differ.",
        )

    levels = []
    for path, records in (("reference", reference_records), ("candidate", candidate_records)):
        for artifact_path in CANONICAL_ARTIFACT_PATHS:
            entries = records.get(artifact_path, [])
            if len(entries) == 1:
                level = entries[0].get("comparison_level")
                levels.append((path, artifact_path, level))
                if level not in SUPPORTED_COMPARISON_LEVELS:
                    context.error(
                        "compatibility",
                        artifact_path,
                        "COMPARISON_LEVEL_UNSUPPORTED",
                        "Artifact declares an unsupported comparison level.",
                        package=path,
                        comparison_level=level,
                    )
    levels_passed = all(level in SUPPORTED_COMPARISON_LEVELS for _, _, level in levels)
    checks.append(
        {
            "code": "COMPARISON_LEVEL_UNSUPPORTED",
            "field": "comparison_level",
            "passed": levels_passed,
        }
    )

    for field, code in _ALLOWED_MANIFEST_FIELDS:
        reference_value = reference.get(field)
        candidate_value = candidate.get(field)
        if _typed_fingerprint(reference_value) != _typed_fingerprint(candidate_value):
            context.allowed(
                "run_manifest.json",
                code,
                "Manifest implementation identity differs as permitted.",
                candidate=_value_summary(candidate_value),
                field=field,
                reference=_value_summary(reference_value),
            )

    mapping = reference.get("contract_schema_mapping")
    if isinstance(mapping, dict) and mapping.get("action_request") == (
        "minimal-action-request-unversioned"
    ):
        context.warning(
            "compatibility",
            "requests.jsonl",
            "REQUEST_CONTRACT_UNVERSIONED",
            "Both packages use the declared unversioned request contract.",
        )

    passed = not any(
        error["phase"] == "compatibility" and error["blocking"]
        for error in context.errors
    )
    return {
        "checks": checks,
        "passed": passed,
        "supported_comparison_levels": list(SUPPORTED_COMPARISON_LEVELS),
    }


def _package_identity(directory, manifest, validation):
    identity = {
        "artifact_directory_name": directory.name,
        "fixture_id": validation.get("fixture_id"),
        "oracle_id": validation.get("oracle_id"),
        "oracle_version": validation.get("oracle_version"),
    }
    if isinstance(manifest, dict):
        for field in (
            "canonicalization_profile",
            "comparison_profile",
            "fixture_schema_version",
            "implementation_language",
            "runtime_candidate",
        ):
            identity[field] = manifest.get(field)
    return identity


def _invalid_artifact_comparisons(reference_validation, candidate_validation):
    reference = _validation_artifact_map(reference_validation)
    candidate = _validation_artifact_map(candidate_validation)
    records = []
    for path in REQUIRED_ARTIFACT_PATHS:
        reference_item = reference.get(path, {})
        candidate_item = candidate.get(path, {})
        records.append(
            {
                "byte_equal": None,
                "candidate_byte_size": candidate_item.get("byte_size"),
                "candidate_sha256": candidate_item.get("sha256"),
                "candidate_valid": bool(
                    candidate_item.get("canonical_bytes_valid")
                    and candidate_item.get("integrity_valid")
                ),
                "comparison_level": (
                    "compatibility" if path == "run_manifest.json" else None
                ),
                "details_truncated": False,
                "mismatch_count": 0,
                "path": path,
                "reference_byte_size": reference_item.get("byte_size"),
                "reference_sha256": reference_item.get("sha256"),
                "reference_valid": bool(
                    reference_item.get("canonical_bytes_valid")
                    and reference_item.get("integrity_valid")
                ),
                "semantic_equal": None,
                "status": "invalid",
            }
        )
    return records


def _incompatible_artifact_comparisons(reference_validation, candidate_validation):
    records = _invalid_artifact_comparisons(reference_validation, candidate_validation)
    for record in records:
        record["status"] = "incompatible"
    return records


def _artifact_manifest_map(manifest):
    _, records = _manifest_artifact_records(manifest)
    return {
        path: entries[0]
        for path, entries in records.items()
        if len(entries) == 1
    }


def _canonical_mismatch(path, reference_data, candidate_data):
    return {
        "artifact_path": path,
        "blocking": True,
        "candidate_byte_size": len(candidate_data),
        "candidate_sha256": sha256_bytes(candidate_data),
        "code": "CANONICAL_BYTES_MISMATCH",
        "message": "Canonical artifact bytes differ.",
        "reference_byte_size": len(reference_data),
        "reference_sha256": sha256_bytes(reference_data),
    }


def _compare_valid_packages(
    reference_package,
    candidate_package,
    reference_manifest,
    candidate_manifest,
    reference_validation,
    candidate_validation,
    compatibility,
    context,
):
    reference_validation_map = _validation_artifact_map(reference_validation)
    candidate_validation_map = _validation_artifact_map(candidate_validation)
    reference_profiles = _artifact_manifest_map(reference_manifest)
    candidate_profiles = _artifact_manifest_map(candidate_manifest)
    budget = _DiffBudget(MAX_MISMATCHES_PER_ARTIFACT, MAX_MISMATCHES_TOTAL)
    artifact_comparisons = []
    semantic_mismatches = []
    canonical_mismatches = []
    truncated_artifacts = []

    for path in CANONICAL_ARTIFACT_PATHS:
        reference_entry = reference_profiles[path]
        candidate_entry = candidate_profiles[path]
        level = reference_entry["comparison_level"]
        reference_payload = reference_package[path]
        candidate_payload = candidate_package[path]
        blocking_semantics = level != "informational"
        diff = _semantic_diff(
            reference_payload["parsed"],
            candidate_payload["parsed"],
            path,
            blocking=blocking_semantics,
            budget=budget,
        )
        semantic_mismatches.extend(diff["details"])
        if diff["details_truncated"]:
            truncated_artifacts.append(path)
        byte_equal = reference_payload["bytes"] == candidate_payload["bytes"]
        semantic_equal = diff["mismatch_count"] == 0

        if level == "canonical_bytes" and not byte_equal:
            canonical_mismatches.append(
                _canonical_mismatch(
                    path,
                    reference_payload["bytes"],
                    candidate_payload["bytes"],
                )
            )
        elif level == "semantic" and not byte_equal and semantic_equal:
            context.allowed(
                path,
                "SEMANTIC_LEVEL_BYTE_DIFFERENCE",
                "Semantic-level artifact bytes differ while parsed meaning is equal.",
                candidate_sha256=sha256_bytes(candidate_payload["bytes"]),
                reference_sha256=sha256_bytes(reference_payload["bytes"]),
            )
        elif level == "informational" and (
            not byte_equal or not semantic_equal
        ):
            context.allowed(
                path,
                "INFORMATIONAL_ARTIFACT_DIFFERENCE",
                "Informational artifact content differs without blocking gameplay semantics.",
            )

        if not semantic_equal and blocking_semantics:
            status = "semantic_mismatch"
        elif level == "canonical_bytes" and not byte_equal:
            status = "canonical_mismatch"
        elif level == "semantic" and not byte_equal:
            status = "allowed_difference"
        elif level == "informational" and (not semantic_equal or not byte_equal):
            status = "informational_difference"
        else:
            status = "equal"
        artifact_comparisons.append(
            {
                "byte_equal": byte_equal,
                "candidate_byte_size": len(candidate_payload["bytes"]),
                "candidate_sha256": sha256_bytes(candidate_payload["bytes"]),
                "candidate_valid": bool(
                    candidate_validation_map[path]["canonical_bytes_valid"]
                    and candidate_validation_map[path]["integrity_valid"]
                ),
                "comparison_level": level,
                "details_truncated": diff["details_truncated"],
                "mismatch_count": diff["mismatch_count"],
                "path": path,
                "reference_byte_size": len(reference_payload["bytes"]),
                "reference_sha256": sha256_bytes(reference_payload["bytes"]),
                "reference_valid": bool(
                    reference_validation_map[path]["canonical_bytes_valid"]
                    and reference_validation_map[path]["integrity_valid"]
                ),
                "semantic_equal": semantic_equal,
                "status": status,
            }
        )

    reference_manifest_payload = reference_package["run_manifest.json"]
    candidate_manifest_payload = candidate_package["run_manifest.json"]
    manifest_bytes_equal = (
        reference_manifest_payload["bytes"] == candidate_manifest_payload["bytes"]
    )
    manifest_allowed = any(
        item["artifact"] == "run_manifest.json" for item in context.allowed_differences
    )
    manifest_status = (
        "equal"
        if manifest_bytes_equal
        else "allowed_difference"
        if compatibility["passed"]
        else "incompatible"
    )
    artifact_comparisons.append(
        {
            "byte_equal": manifest_bytes_equal,
            "candidate_byte_size": len(candidate_manifest_payload["bytes"]),
            "candidate_sha256": sha256_bytes(candidate_manifest_payload["bytes"]),
            "candidate_valid": True,
            "comparison_level": "compatibility",
            "details_truncated": False,
            "mismatch_count": 0,
            "path": "run_manifest.json",
            "reference_byte_size": len(reference_manifest_payload["bytes"]),
            "reference_sha256": sha256_bytes(reference_manifest_payload["bytes"]),
            "reference_valid": True,
            "semantic_equal": compatibility["passed"],
            "status": manifest_status,
        }
    )
    if not manifest_bytes_equal and not manifest_allowed:
        context.allowed(
            "run_manifest.json",
            "MANIFEST_DERIVED_CONTENT_DIFFERENCE",
            "Compatible run manifests differ in derived artifact or run data.",
        )

    if truncated_artifacts:
        context.warning(
            "comparison",
            truncated_artifacts[0],
            "COMPARISON_DETAILS_TRUNCATED",
            "Detailed semantic mismatch output reached its configured limit.",
            artifact_paths=truncated_artifacts,
            max_per_artifact=MAX_MISMATCHES_PER_ARTIFACT,
            max_total=MAX_MISMATCHES_TOTAL,
        )
    return artifact_comparisons, semantic_mismatches, canonical_mismatches


def _build_result(
    reference_directory,
    candidate_directory,
    reference_manifest,
    candidate_manifest,
    reference_validation,
    candidate_validation,
    compatibility,
    artifact_comparisons,
    semantic_mismatches,
    canonical_mismatches,
    context,
):
    context.errors.sort(key=_issue_sort_key)
    context.warnings.sort(key=_issue_sort_key)
    context.allowed_differences.sort(key=_issue_sort_key)
    reference_valid = bool(reference_validation.get("valid"))
    candidate_valid = bool(candidate_validation.get("valid"))
    compatibility_passed = bool(
        reference_valid and candidate_valid and compatibility.get("passed")
    )
    comparable = compatibility_passed
    blocking_semantic_mismatches = [
        mismatch for mismatch in semantic_mismatches if mismatch["blocking"]
    ]
    semantic_match = comparable and not blocking_semantic_mismatches
    canonical_paths = {
        record["path"]
        for record in artifact_comparisons
        if record["comparison_level"] == "canonical_bytes"
    }
    canonical_mismatch_paths = {
        mismatch["artifact_path"] for mismatch in canonical_mismatches
    }
    canonical_match = comparable and not (canonical_paths & canonical_mismatch_paths)
    match = bool(
        comparable
        and semantic_match
        and canonical_match
        and not any(error["blocking"] for error in context.errors)
    )
    summary = {
        "allowed_difference_count": len(context.allowed_differences),
        "artifact_count": len(artifact_comparisons),
        "blocking_error_count": sum(error["blocking"] for error in context.errors),
        "candidate_valid": candidate_valid,
        "canonical_match": canonical_match,
        "canonical_mismatch_artifact_count": len(canonical_mismatch_paths),
        "comparable": comparable,
        "compatibility_passed": compatibility_passed,
        "equal_artifact_count": sum(
            record["status"] == "equal" for record in artifact_comparisons
        ),
        "match": match,
        "reference_valid": reference_valid,
        "semantic_match": semantic_match,
        "semantic_mismatch_artifact_count": len(
            {mismatch["artifact_path"] for mismatch in blocking_semantic_mismatches}
        ),
        "total_semantic_mismatch_count": sum(
            record["mismatch_count"] for record in artifact_comparisons
        ),
        "warning_count": len(context.warnings),
    }
    return {
        "allowed_differences": context.allowed_differences,
        "artifact_comparisons": artifact_comparisons,
        "candidate": _package_identity(
            candidate_directory, candidate_manifest, candidate_validation
        ),
        "canonical_match": canonical_match,
        "canonical_mismatches": canonical_mismatches,
        "comparable": comparable,
        "compatibility": compatibility,
        "contract_type": COMPARISON_RESULT_CONTRACT_TYPE,
        "errors": context.errors,
        "match": match,
        "reference": _package_identity(
            reference_directory, reference_manifest, reference_validation
        ),
        "schema_version": COMPARISON_RESULT_SCHEMA_VERSION,
        "semantic_match": semantic_match,
        "semantic_mismatches": semantic_mismatches,
        "summary": summary,
        "validation": {
            "candidate": candidate_validation,
            "reference": reference_validation,
        },
        "warnings": context.warnings,
    }


def compare_runtime_comparison_artifacts(
    reference_directory,
    candidate_directory,
    *,
    expected_fixture_id=None,
):
    """Compare two existing artifact packages after independent validation."""

    reference_path = Path(reference_directory)
    candidate_path = Path(candidate_directory)
    context = _ComparisonContext()

    reference_validation = _validate_input(
        reference_path, "reference", expected_fixture_id
    )
    candidate_validation = _validate_input(
        candidate_path, "candidate", expected_fixture_id
    )
    try:
        same_directory = reference_path.resolve(strict=True) == candidate_path.resolve(
            strict=True
        )
    except OSError as exc:
        raise ArtifactComparatorInputError(
            "INPUT_IDENTITY_CHECK_FAILED",
            "Artifact directory identity could not be determined.",
        ) from exc
    if same_directory:
        context.warning(
            "validation",
            "run_manifest.json",
            "SELF_COMPARISON",
            "Reference and candidate resolve to the same artifact directory.",
        )

    if not reference_validation.get("valid"):
        context.error(
            "validation",
            "reference",
            "REFERENCE_PACKAGE_INVALID",
            "Reference package failed independent artifact validation.",
            validator_error_count=reference_validation.get("summary", {}).get(
                "error_count", 0
            ),
        )
    if not candidate_validation.get("valid"):
        context.error(
            "validation",
            "candidate",
            "CANDIDATE_PACKAGE_INVALID",
            "Candidate package failed independent artifact validation.",
            validator_error_count=candidate_validation.get("summary", {}).get(
                "error_count", 0
            ),
        )

    reference_manifest = _read_manifest_if_safe(
        reference_path, reference_validation
    )
    candidate_manifest = _read_manifest_if_safe(
        candidate_path, candidate_validation
    )
    compatibility = _compare_manifest_compatibility(
        reference_manifest, candidate_manifest, context
    )

    both_valid = bool(
        reference_validation.get("valid") and candidate_validation.get("valid")
    )
    if not both_valid:
        artifact_comparisons = _invalid_artifact_comparisons(
            reference_validation, candidate_validation
        )
        semantic_mismatches = []
        canonical_mismatches = []
    elif not compatibility["passed"]:
        artifact_comparisons = _incompatible_artifact_comparisons(
            reference_validation, candidate_validation
        )
        semantic_mismatches = []
        canonical_mismatches = []
    else:
        reference_package = _read_valid_package(reference_path)
        candidate_package = _read_valid_package(candidate_path)
        (
            artifact_comparisons,
            semantic_mismatches,
            canonical_mismatches,
        ) = _compare_valid_packages(
            reference_package,
            candidate_package,
            reference_manifest,
            candidate_manifest,
            reference_validation,
            candidate_validation,
            compatibility,
            context,
        )

    return _build_result(
        reference_path,
        candidate_path,
        reference_manifest,
        candidate_manifest,
        reference_validation,
        candidate_validation,
        compatibility,
        artifact_comparisons,
        semantic_mismatches,
        canonical_mismatches,
        context,
    )


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArtifactComparatorInputError(
            "CLI_USAGE_ERROR",
            "Comparator CLI arguments are invalid.",
        )


def _build_argument_parser():
    parser = _ArgumentParser(
        description="Compare two validated runtime-comparison artifact directories."
    )
    parser.add_argument("--reference", required=True, help="Reference artifact directory.")
    parser.add_argument("--candidate", required=True, help="Candidate artifact directory.")
    parser.add_argument(
        "--expected-fixture-id",
        help="Optional fixture ID that both packages must declare.",
    )
    return parser


def main(argv=None):
    """Run the read-only comparator CLI and return its process exit code."""

    parser = _build_argument_parser()
    try:
        arguments = parser.parse_args(argv)
        result = compare_runtime_comparison_artifacts(
            arguments.reference,
            arguments.candidate,
            expected_fixture_id=arguments.expected_fixture_id,
        )
    except ArtifactComparatorInputError as exc:
        print("%s: %s" % (exc.code, exc.message), file=sys.stderr)
        return 3
    except (OSError, ValueError):
        print(
            "ARTIFACT_COMPARATOR_TECHNICAL_ERROR: Comparison could not be completed.",
            file=sys.stderr,
        )
        return 3
    sys.stdout.write(canonical_json_bytes(result).decode("utf-8"))
    if result["match"]:
        return 0
    if result["comparable"]:
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ArtifactComparatorInputError",
    "COMPARISON_RESULT_CONTRACT_TYPE",
    "COMPARISON_RESULT_SCHEMA_VERSION",
    "MAX_MISMATCHES_PER_ARTIFACT",
    "MAX_MISMATCHES_TOTAL",
    "SUPPORTED_COMPARISON_LEVELS",
    "compare_runtime_comparison_artifacts",
    "main",
]
