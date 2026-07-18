"""Runtime-neutral assembly and atomic writing of comparison artifacts."""

from __future__ import annotations

import json
import os
import re
import secrets
import shutil
from copy import deepcopy
from pathlib import Path

from .canonical_json import (
    CanonicalJsonError,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    sha256_bytes,
)


RUN_MANIFEST_SCHEMA_VERSION = "aeterna-runtime-comparison-run-manifest-v1"
RUN_MANIFEST_CONTRACT_TYPE = "runtime_comparison_run_manifest"
DIAGNOSTICS_SCHEMA_VERSION = "aeterna-runtime-comparison-diagnostics-v1"
CANONICAL_JSON_PROFILE = "aeterna-canonical-json-v1"
CANONICAL_JSONL_PROFILE = "aeterna-canonical-jsonl-v1"
COMPARISON_PROFILE = "minimal-draw-end-turn-canonical-v1"
ORACLE_ID = "python_reference"
ORACLE_VERSION = 1
FIXTURE_ID = "minimal_draw_end_turn_v1"

CANONICAL_ARTIFACT_PATHS = (
    "initial_state.json",
    "requests.jsonl",
    "responses.jsonl",
    "legal_actions.jsonl",
    "events.jsonl",
    "snapshot_player_1.json",
    "snapshot_player_2.json",
    "final_debug_state.json",
    "diagnostics.json",
)
REQUIRED_OUTPUT_PATHS = CANONICAL_ARTIFACT_PATHS + ("run_manifest.json",)
JSONL_ARTIFACT_PATHS = frozenset(
    {
        "requests.jsonl",
        "responses.jsonl",
        "legal_actions.jsonl",
        "events.jsonl",
    }
)

_REQUEST_FIELDS = frozenset(
    {
        "request_id",
        "match_id",
        "player_id",
        "action_id",
        "action_type",
        "expected_state_version",
        "payload",
    }
)
_RESPONSE_FIELDS = frozenset(
    {
        "request_id",
        "accepted",
        "reason",
        "state_version_before",
        "state_version_after",
        "events",
        "diagnostics",
    }
)
_EXPECTED_REQUEST_IDS = (
    "fixture_req_001_draw_player_1",
    "fixture_req_002_stale_end_turn_player_1",
    "fixture_req_003_end_turn_player_1",
    "fixture_req_004_draw_player_2",
)
_EXPECTED_STATE_VERSION_PATH = [0, 1, 1, 2, 3]
_EXPECTED_EVENT_SEQUENCES = [1, 2, 3]
_EXPECTED_EVENT_TYPES = ["zone_move", "turn_transition", "zone_move"]
_FORBIDDEN_ENVIRONMENT_KEYS = frozenset(
    {
        "created_at",
        "current_timestamp",
        "generated_at",
        "hostname",
        "pid",
        "process_id",
        "timestamp",
        "user",
        "username",
    }
)
_UUID_PATTERN = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-"
    r"[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
)
_MEMORY_ADDRESS_PATTERN = re.compile(r"\b0x[0-9a-fA-F]{6,}\b")
_BASE_KNOWN_DEVIATION = {
    "code": "ACTION_REQUEST_SCHEMA_VERSION_NOT_EMBEDDED",
    "blocking": False,
    "description": (
        "The current action request is identified by its fixed field contract; "
        "it does not yet embed schema_version."
    ),
}


class RuntimeComparisonArtifactBuildError(Exception):
    """Stable package assembly or atomic-output failure."""

    def __init__(self, code, message, details=None):
        self.code = str(code)
        self.message = str(message)
        self.details = deepcopy(details or {})
        try:
            canonical_json_bytes(self.to_dict())
        except CanonicalJsonError as exc:
            raise ValueError("Artifact builder error details must be canonical JSON-compatible.") from exc
        super().__init__("%s: %s" % (self.code, self.message))

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "details": deepcopy(self.details),
        }


def normalize_output_directory(output_directory):
    try:
        target = Path(output_directory).resolve()
    except (OSError, TypeError, ValueError) as exc:
        raise RuntimeComparisonArtifactBuildError(
            "artifact_contract_invalid",
            "Output directory is invalid.",
        ) from exc
    if not target.name or target == target.parent:
        raise RuntimeComparisonArtifactBuildError(
            "artifact_contract_invalid",
            "Output directory must name an explicit child directory.",
        )
    return target


def preflight_output_directory(output_directory, *, replace=False):
    target = normalize_output_directory(output_directory)
    if target.exists() and not replace:
        raise RuntimeComparisonArtifactBuildError(
            "output_exists",
            "Output directory already exists.",
            {"output_name": target.name},
        )
    if target.is_symlink():
        raise RuntimeComparisonArtifactBuildError(
            "target_replace_failed",
            "Output directory must not be a symbolic link.",
            {"output_name": target.name},
        )
    return target


def validate_fixture_result(result):
    """Validate the fixed fixture result without importing an engine runner."""

    def require(condition, message, check):
        if not condition:
            raise RuntimeComparisonArtifactBuildError(
                "artifact_contract_invalid",
                message,
                {"check": check},
            )

    require(isinstance(result, dict), "Fixture result must be an object.", "result_shape")
    identity = result.get("fixture_identity") or {}
    requests = result.get("requests") or []
    responses = result.get("responses") or []
    checkpoints = result.get("legal_action_checkpoints") or []
    events = result.get("events") or []
    summary = result.get("run_summary") or {}
    final_state = result.get("final_canonical_state") or {}

    require(identity.get("fixture_id") == FIXTURE_ID, "Fixture ID is invalid.", "fixture_id")
    require(len(requests) == 4, "Fixture must contain exactly four requests.", "request_count")
    require(len(responses) == 4, "Fixture must contain exactly four responses.", "response_count")
    require(
        all(isinstance(item, dict) and set(item) == _REQUEST_FIELDS for item in requests),
        "Canonical request fields are invalid.",
        "request_fields",
    )
    require(
        [item.get("request_id") for item in requests] == list(_EXPECTED_REQUEST_IDS),
        "Canonical request IDs are invalid.",
        "request_ids",
    )
    require(
        len(set(item.get("request_id") for item in requests)) == 4,
        "Canonical request IDs must be unique.",
        "request_id_uniqueness",
    )
    require(
        all(item.get("payload") == {} for item in requests),
        "Fixture request payloads must be empty objects.",
        "request_payloads",
    )
    require(
        all(isinstance(item, dict) and _RESPONSE_FIELDS.issubset(item) for item in responses),
        "Canonical response fields are invalid.",
        "response_fields",
    )
    require(
        [item.get("request_id") for item in responses] == list(_EXPECTED_REQUEST_IDS),
        "Response request IDs do not match request order.",
        "response_request_ids",
    )
    require(
        [item.get("accepted") is True for item in responses] == [True, False, True, True],
        "Response acceptance path is invalid.",
        "responses",
    )
    accepted_responses = (responses[0], responses[2], responses[3])
    require(
        all(item.get("reason") is None and item.get("diagnostics") == [] for item in accepted_responses),
        "Accepted response reason or diagnostics are invalid.",
        "accepted_responses",
    )
    require(
        responses[1].get("reason") == "stale_state_version"
        and responses[1].get("events") == []
        and len(responses[1].get("diagnostics") or []) == 1,
        "Stale response contract is invalid.",
        "stale_response",
    )
    require(
        summary.get("state_version_path") == _EXPECTED_STATE_VERSION_PATH,
        "State-version path is invalid.",
        "state_version_path",
    )
    require(len(checkpoints) == 4, "Fixture must contain four legal-action checkpoints.", "checkpoint_count")
    require(
        [event.get("event_sequence") for event in events] == _EXPECTED_EVENT_SEQUENCES,
        "Event sequence is invalid.",
        "event_sequences",
    )
    require(
        [event.get("event_type") for event in events] == _EXPECTED_EVENT_TYPES,
        "Event type path is invalid.",
        "event_types",
    )
    require(
        (result.get("snapshot_player_1") or {}).get("player_id") == "player_1"
        and (result.get("snapshot_player_2") or {}).get("player_id") == "player_2",
        "Player snapshot identities are invalid.",
        "snapshot_player_ids",
    )
    require(
        final_state.get("active_player_id") == "player_2"
        and final_state.get("priority_player_id") == "player_2",
        "Final active or priority player is invalid.",
        "final_players",
    )
    require(
        (result.get("visibility_checks") or {}).get("all_passed") is True,
        "Hidden-information validation failed.",
        "hidden_information",
    )
    stale = result.get("stale_immutability") or {}
    require(
        stale.get("canonical_state_unchanged") is True
        and stale.get("input_request_unchanged") is True
        and all((stale.get("components") or {}).values()),
        "Stale request immutability validation failed.",
        "stale_immutability",
    )
    require(
        summary.get("completed") is True and summary.get("invariant_error_count") == 0,
        "Fixture completion or invariant validation failed.",
        "fixture_validation",
    )
    require(
        result.get("diagnostics") == responses[1].get("diagnostics"),
        "Runner diagnostics contain an unexpected blocking entry.",
        "runner_diagnostics",
    )


def build_canonical_artifact_bytes(result):
    diagnostics = _build_diagnostics(result)
    values = {
        "initial_state.json": result["initial_canonical_state"],
        "requests.jsonl": result["requests"],
        "responses.jsonl": result["responses"],
        "legal_actions.jsonl": result["legal_action_checkpoints"],
        "events.jsonl": result["events"],
        "snapshot_player_1.json": result["snapshot_player_1"],
        "snapshot_player_2.json": result["snapshot_player_2"],
        "final_debug_state.json": result["final_canonical_state"],
        "diagnostics.json": diagnostics,
    }
    validate_canonical_hygiene(values)
    artifacts = {}
    try:
        for path in CANONICAL_ARTIFACT_PATHS:
            value = deepcopy(values[path])
            artifacts[path] = (
                canonical_jsonl_bytes(value)
                if path in JSONL_ARTIFACT_PATHS
                else canonical_json_bytes(value)
            )
    except (CanonicalJsonError, TypeError) as exc:
        raise RuntimeComparisonArtifactBuildError(
            "artifact_contract_invalid",
            "Canonical artifact serialization failed.",
        ) from exc
    return artifacts


def build_run_manifest(
    result,
    artifacts,
    *,
    runtime_candidate,
    implementation_language,
    runtime_version,
    operating_system,
    architecture,
    build_identifier,
    known_deviations=(),
    implementation_specific=None,
):
    initial = result["initial_canonical_state"]
    final = result["final_canonical_state"]
    deviations = [deepcopy(_BASE_KNOWN_DEVIATION)]
    deviations.extend(deepcopy(list(known_deviations)))
    canonical_artifacts = []
    for path in CANONICAL_ARTIFACT_PATHS:
        data = artifacts[path]
        is_jsonl = path in JSONL_ARTIFACT_PATHS
        canonical_artifacts.append(
            {
                "path": path,
                "media_type": "application/x-ndjson" if is_jsonl else "application/json",
                "canonicalization": CANONICAL_JSONL_PROFILE if is_jsonl else CANONICAL_JSON_PROFILE,
                "byte_size": len(data),
                "sha256": sha256_bytes(data),
                "comparison_level": "canonical_bytes",
            }
        )
    manifest = {
        "schema_version": RUN_MANIFEST_SCHEMA_VERSION,
        "contract_type": RUN_MANIFEST_CONTRACT_TYPE,
        "fixture_id": result["fixture_identity"]["fixture_id"],
        "fixture_schema_version": result["fixture_identity"]["schema_version"],
        "oracle_id": ORACLE_ID,
        "oracle_version": ORACLE_VERSION,
        "runtime_candidate": runtime_candidate,
        "implementation_language": implementation_language,
        "runtime_version": runtime_version,
        "operating_system": operating_system,
        "architecture": architecture,
        "canonicalization_profile": CANONICAL_JSON_PROFILE,
        "comparison_profile": COMPARISON_PROFILE,
        "contract_schema_mapping": build_contract_schema_mapping(result),
        "build_identifier": build_identifier,
        "start_result": {
            "state_version": initial["state_version"],
            "active_player_id": initial["active_player_id"],
            "priority_player_id": initial["priority_player_id"],
            "event_count": len(initial["event_log"]),
            "validation": "passed",
        },
        "end_result": {
            "state_version": final["state_version"],
            "active_player_id": final["active_player_id"],
            "priority_player_id": final["priority_player_id"],
            "event_count": len(final["event_log"]),
            "validation": "passed",
        },
        "canonical_artifacts": canonical_artifacts,
        "known_deviations": deviations,
        "implementation_specific": deepcopy(implementation_specific or {}),
    }
    validate_canonical_hygiene(manifest)
    return manifest


def build_artifact_package(result, **manifest_arguments):
    """Build all package bytes in memory from an existing fixture result."""

    validate_fixture_result(result)
    artifacts = build_canonical_artifact_bytes(result)
    manifest = build_run_manifest(result, artifacts, **manifest_arguments)
    try:
        manifest_bytes = canonical_json_bytes(manifest)
    except CanonicalJsonError as exc:
        raise RuntimeComparisonArtifactBuildError(
            "artifact_contract_invalid",
            "Run manifest is not canonical JSON-compatible.",
        ) from exc
    planned_files = dict(artifacts)
    planned_files["run_manifest.json"] = manifest_bytes
    return planned_files, manifest


def build_contract_schema_mapping(result):
    initial = result["initial_canonical_state"]
    return {
        "fixture": result["fixture_identity"]["schema_version"],
        "canonical_match_state": initial["schema_version"],
        "card_instance": initial["card_instances"][0]["schema_version"],
        "action_space": result["legal_action_checkpoints"][0]["action_space"]["schema_version"],
        "action_request": "minimal-action-request-unversioned",
        "action_response": result["responses"][0]["schema_version"],
        "engine_event": result["events"][0]["schema_version"],
        "player_visible_snapshot": result["snapshot_player_1"]["schema_version"],
        "run_manifest": RUN_MANIFEST_SCHEMA_VERSION,
    }


def write_atomic_artifact_package(
    output_directory,
    planned_files,
    manifest,
    *,
    replace=False,
    package_validator=None,
):
    """Write, reread, optionally validate, and atomically promote one package."""

    target = preflight_output_directory(output_directory, replace=replace)
    if set(planned_files) != set(REQUIRED_OUTPUT_PATHS):
        raise RuntimeComparisonArtifactBuildError(
            "artifact_contract_invalid",
            "Planned artifact inventory is incomplete or unexpected.",
        )
    parent = target.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
        staging = _create_sibling_directory(parent, ".%s.staging-" % target.name)
    except OSError as exc:
        raise RuntimeComparisonArtifactBuildError(
            "staging_write_failed",
            "Could not create the staging directory.",
            {"output_name": target.name},
        ) from exc

    validation_result = None
    try:
        try:
            for relative_path in REQUIRED_OUTPUT_PATHS:
                (staging / relative_path).write_bytes(planned_files[relative_path])
        except OSError as exc:
            raise RuntimeComparisonArtifactBuildError(
                "staging_write_failed",
                "Could not write all staged artifacts.",
            ) from exc
        _validate_staging_directory(staging, planned_files, manifest)
        if package_validator is not None:
            validation_result = package_validator(staging)
        _promote_staging_directory(staging, target, replace=replace)
    finally:
        if staging.exists() or staging.is_symlink():
            _remove_explicit_sibling(staging, parent)
    return validation_result


def validate_canonical_hygiene(value):
    def visit(current):
        if isinstance(current, dict):
            for key, nested in current.items():
                if key.lower() in _FORBIDDEN_ENVIRONMENT_KEYS:
                    raise RuntimeComparisonArtifactBuildError(
                        "artifact_contract_invalid",
                        "Canonical artifact contains environment-specific metadata.",
                        {"check": "forbidden_environment_key"},
                    )
                visit(nested)
        elif isinstance(current, list):
            for nested in current:
                visit(nested)
        elif isinstance(current, str):
            is_windows_absolute = (
                len(current) >= 3
                and current[0].isalpha()
                and current[1] == ":"
                and current[2] in {"/", "\\"}
            )
            if Path(current).is_absolute() or is_windows_absolute:
                raise RuntimeComparisonArtifactBuildError(
                    "artifact_contract_invalid",
                    "Canonical artifact contains an absolute path.",
                    {"check": "absolute_path"},
                )
            if _UUID_PATTERN.search(current):
                raise RuntimeComparisonArtifactBuildError(
                    "artifact_contract_invalid",
                    "Canonical artifact contains a random-UUID-shaped value.",
                    {"check": "random_uuid"},
                )
            if _MEMORY_ADDRESS_PATTERN.search(current):
                raise RuntimeComparisonArtifactBuildError(
                    "artifact_contract_invalid",
                    "Canonical artifact contains a memory-address-shaped value.",
                    {"check": "memory_address"},
                )

    visit(value)


def _build_diagnostics(result):
    stale = deepcopy(result["stale_immutability"])
    visibility = deepcopy(result["visibility_checks"])
    runner_items = deepcopy(result["diagnostics"])
    return {
        "schema_version": DIAGNOSTICS_SCHEMA_VERSION,
        "contract_type": "runtime_comparison_diagnostics",
        "result": "passed",
        "fixture_validation": {
            "passed": True,
            "fixture_id": result["fixture_identity"]["fixture_id"],
        },
        "invariant_validation": {
            "passed": result["run_summary"]["invariant_error_count"] == 0,
            "error_count": result["run_summary"]["invariant_error_count"],
        },
        "hidden_information_validation": {
            "passed": visibility["all_passed"],
            "players": {
                "player_1": visibility["player_1"],
                "player_2": visibility["player_2"],
            },
        },
        "determinism_validation": {
            "passed": True,
            "comparison": "two_clean_in_memory_canonical_results",
        },
        "stale_immutability_validation": {
            "passed": stale["canonical_state_unchanged"] and stale["input_request_unchanged"],
            "canonical_state_sha256_before": stale["canonical_state_sha256_before"],
            "canonical_state_sha256_after": stale["canonical_state_sha256_after"],
            "components": stale["components"],
        },
        "runner_diagnostics": {
            "blocking_error_count": 0,
            "expected_rejection_diagnostic_count": len(runner_items),
            "items": runner_items,
        },
    }


def _validate_staging_directory(staging, planned_files, manifest):
    try:
        actual_paths = sorted(path.name for path in staging.iterdir())
        if actual_paths != sorted(REQUIRED_OUTPUT_PATHS):
            raise ValueError("staged file inventory differs")
        for relative_path in REQUIRED_OUTPUT_PATHS:
            data = (staging / relative_path).read_bytes()
            if data != planned_files[relative_path]:
                raise ValueError("staged bytes differ for %s" % relative_path)
            if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
                raise ValueError("encoding or line ending differs for %s" % relative_path)
            if not data.endswith(b"\n") or data.endswith(b"\n\n"):
                raise ValueError("final newline differs for %s" % relative_path)
            text = data.decode("utf-8")
            if relative_path in JSONL_ARTIFACT_PATHS:
                lines = text.splitlines()
                if not lines:
                    raise ValueError("JSONL artifact is empty for %s" % relative_path)
                for line in lines:
                    if not isinstance(json.loads(line), dict):
                        raise ValueError("JSONL record is not an object for %s" % relative_path)
            elif not isinstance(json.loads(text), dict):
                raise ValueError("JSON artifact is not an object for %s" % relative_path)

        staged_manifest = json.loads((staging / "run_manifest.json").read_text(encoding="utf-8"))
        if staged_manifest != manifest:
            raise ValueError("run manifest content differs")
        records = staged_manifest.get("canonical_artifacts") or []
        if [record.get("path") for record in records] != list(CANONICAL_ARTIFACT_PATHS):
            raise ValueError("canonical artifact order differs")
        if any(record.get("path") == "run_manifest.json" for record in records):
            raise ValueError("run manifest hashes itself")
        for record in records:
            data = (staging / record["path"]).read_bytes()
            if record.get("byte_size") != len(data) or record.get("sha256") != sha256_bytes(data):
                raise ValueError("manifest hash or size differs for %s" % record["path"])
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise RuntimeComparisonArtifactBuildError(
            "staging_validation_failed",
            "Staged artifact validation failed.",
        ) from exc


def _promote_staging_directory(staging, target, *, replace):
    if target.exists() and not replace:
        raise RuntimeComparisonArtifactBuildError("output_exists", "Output directory already exists.")
    backup = None
    promoted = False
    try:
        if target.exists():
            backup = _create_sibling_directory(target.parent, ".%s.backup-" % target.name)
            backup.rmdir()
            os.replace(target, backup)
        os.replace(staging, target)
        promoted = True
    except OSError as exc:
        if backup is not None and backup.exists() and not target.exists():
            try:
                os.replace(backup, target)
            except OSError:
                pass
        raise RuntimeComparisonArtifactBuildError(
            "target_replace_failed",
            "Could not promote the validated staging directory.",
            {"output_name": target.name},
        ) from exc
    finally:
        if promoted and backup is not None and (backup.exists() or backup.is_symlink()):
            _remove_explicit_sibling(backup, target.parent)


def _remove_explicit_sibling(path, expected_parent):
    if path.parent.resolve() != expected_parent.resolve():
        raise RuntimeComparisonArtifactBuildError(
            "target_replace_failed",
            "Refused to remove a path outside the explicit output parent.",
        )
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _create_sibling_directory(parent, prefix):
    for _attempt in range(100):
        candidate = parent / (prefix + secrets.token_hex(8))
        try:
            candidate.mkdir()
        except FileExistsError:
            continue
        return candidate
    raise OSError("Could not allocate a unique sibling directory.")


__all__ = [
    "CANONICAL_ARTIFACT_PATHS",
    "CANONICAL_JSON_PROFILE",
    "COMPARISON_PROFILE",
    "DIAGNOSTICS_SCHEMA_VERSION",
    "FIXTURE_ID",
    "JSONL_ARTIFACT_PATHS",
    "ORACLE_ID",
    "ORACLE_VERSION",
    "REQUIRED_OUTPUT_PATHS",
    "RUN_MANIFEST_CONTRACT_TYPE",
    "RUN_MANIFEST_SCHEMA_VERSION",
    "RuntimeComparisonArtifactBuildError",
    "build_artifact_package",
    "build_canonical_artifact_bytes",
    "build_contract_schema_mapping",
    "build_run_manifest",
    "normalize_output_directory",
    "preflight_output_directory",
    "validate_canonical_hygiene",
    "validate_fixture_result",
    "write_atomic_artifact_package",
]
