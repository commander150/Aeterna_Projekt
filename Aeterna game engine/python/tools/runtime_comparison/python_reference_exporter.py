"""Versioned canonical artifact exporter for the Python comparison oracle."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import secrets
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

from .canonical_json import (
    CanonicalJsonError,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    sha256_bytes,
)
from .python_reference_fixture import (
    FIXTURE_ID,
    REQUEST_IDS,
    RuntimeComparisonFixtureError,
    run_python_reference_fixture,
)


RUN_MANIFEST_SCHEMA_VERSION = "aeterna-runtime-comparison-run-manifest-v1"
RUN_MANIFEST_CONTRACT_TYPE = "runtime_comparison_run_manifest"
DIAGNOSTICS_SCHEMA_VERSION = "aeterna-runtime-comparison-diagnostics-v1"
CANONICAL_JSON_PROFILE = "aeterna-canonical-json-v1"
CANONICAL_JSONL_PROFILE = "aeterna-canonical-jsonl-v1"
COMPARISON_PROFILE = "minimal-draw-end-turn-canonical-v1"
ORACLE_ID = "python_reference"
ORACLE_VERSION = 1

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

_JSONL_PATHS = frozenset(
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
    REQUEST_IDS["draw_player_1"],
    REQUEST_IDS["stale_end_turn_player_1"],
    REQUEST_IDS["end_turn_player_1"],
    REQUEST_IDS["draw_player_2"],
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


class PythonReferenceExportError(Exception):
    """Stable exporter failure with JSON-compatible, path-safe details."""

    def __init__(self, code, message, details=None):
        self.code = str(code)
        self.message = str(message)
        self.details = deepcopy(details or {})
        try:
            canonical_json_bytes(self.to_dict())
        except CanonicalJsonError as exc:
            raise ValueError("Exporter error details must be canonical JSON-compatible.") from exc
        super().__init__("%s: %s" % (self.code, self.message))

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "details": deepcopy(self.details),
        }


def export_python_reference_artifacts(fixture_path, output_directory, *, replace=False):
    """Run the fixed fixture and atomically export its versioned artifacts."""

    target = _normalize_output_directory(output_directory)
    if target.exists() and not replace:
        raise PythonReferenceExportError(
            "output_exists",
            "Output directory already exists.",
            {"output_name": target.name},
        )
    if target.is_symlink():
        raise PythonReferenceExportError(
            "target_replace_failed",
            "Output directory must not be a symbolic link.",
            {"output_name": target.name},
        )

    first_result = _run_fixture(fixture_path)
    second_result = _run_fixture(fixture_path)
    try:
        deterministic = canonical_json_bytes(first_result) == canonical_json_bytes(second_result)
    except CanonicalJsonError as exc:
        raise PythonReferenceExportError(
            "artifact_contract_invalid",
            "Fixture result is not canonical JSON-compatible.",
        ) from exc
    if not deterministic:
        raise PythonReferenceExportError(
            "artifact_contract_invalid",
            "Two clean fixture runs produced different canonical results.",
            {"check": "runner_determinism"},
        )

    _validate_fixture_result(first_result)
    artifacts = _build_canonical_artifact_bytes(first_result)
    manifest = _build_run_manifest(first_result, artifacts)
    _validate_canonical_hygiene(manifest)
    try:
        manifest_bytes = canonical_json_bytes(manifest)
    except CanonicalJsonError as exc:
        raise PythonReferenceExportError(
            "artifact_contract_invalid",
            "Run manifest is not canonical JSON-compatible.",
        ) from exc
    planned_files = dict(artifacts)
    planned_files["run_manifest.json"] = manifest_bytes

    _write_atomic_output(target, planned_files, manifest, replace=replace)
    return deepcopy(manifest)


def _normalize_output_directory(output_directory):
    try:
        target = Path(output_directory).resolve()
    except (OSError, TypeError, ValueError) as exc:
        raise PythonReferenceExportError(
            "artifact_contract_invalid",
            "Output directory is invalid.",
        ) from exc
    if not target.name or target == target.parent:
        raise PythonReferenceExportError(
            "artifact_contract_invalid",
            "Output directory must name an explicit child directory.",
        )
    return target


def _run_fixture(fixture_path):
    try:
        return run_python_reference_fixture(fixture_path)
    except RuntimeComparisonFixtureError as exc:
        raise PythonReferenceExportError(
            "fixture_run_failed",
            "Python reference fixture execution failed.",
            {"fixture_error": exc.to_dict()},
        ) from None
    except Exception:
        raise PythonReferenceExportError(
            "fixture_run_failed",
            "Python reference fixture execution failed.",
        ) from None


def _validate_fixture_result(result):
    def require(condition, message, check):
        if not condition:
            raise PythonReferenceExportError(
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
    accepted = [item.get("accepted") is True for item in responses]
    require(accepted == [True, False, True, True], "Response acceptance path is invalid.", "responses")
    require(
        all(item.get("reason") is None and item.get("diagnostics") == [] for item in (responses[0], responses[2], responses[3])),
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


def _build_canonical_artifact_bytes(result):
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
    _validate_canonical_hygiene(values)
    artifacts = {}
    try:
        for path in CANONICAL_ARTIFACT_PATHS:
            value = deepcopy(values[path])
            artifacts[path] = (
                canonical_jsonl_bytes(value) if path in _JSONL_PATHS else canonical_json_bytes(value)
            )
    except (CanonicalJsonError, TypeError) as exc:
        raise PythonReferenceExportError(
            "artifact_contract_invalid",
            "Canonical artifact serialization failed.",
        ) from exc
    return artifacts


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


def _build_run_manifest(result, artifacts):
    initial = result["initial_canonical_state"]
    final = result["final_canonical_state"]
    build_identifier, build_deviation = _resolve_build_identifier()
    deviations = [
        {
            "code": "ACTION_REQUEST_SCHEMA_VERSION_NOT_EMBEDDED",
            "blocking": False,
            "description": (
                "The current action request is identified by its fixed field contract; "
                "it does not yet embed schema_version."
            ),
        }
    ]
    if build_deviation is not None:
        deviations.append(build_deviation)
    canonical_artifacts = []
    for path in CANONICAL_ARTIFACT_PATHS:
        data = artifacts[path]
        is_jsonl = path in _JSONL_PATHS
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
    return {
        "schema_version": RUN_MANIFEST_SCHEMA_VERSION,
        "contract_type": RUN_MANIFEST_CONTRACT_TYPE,
        "fixture_id": result["fixture_identity"]["fixture_id"],
        "fixture_schema_version": result["fixture_identity"]["schema_version"],
        "oracle_id": ORACLE_ID,
        "oracle_version": ORACLE_VERSION,
        "runtime_candidate": "python_reference",
        "implementation_language": "python",
        "runtime_version": platform.python_version(),
        "operating_system": platform.system().lower() or "unknown",
        "architecture": platform.machine().lower() or "unknown",
        "canonicalization_profile": CANONICAL_JSON_PROFILE,
        "comparison_profile": COMPARISON_PROFILE,
        "contract_schema_mapping": _build_contract_schema_mapping(result),
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
        "implementation_specific": {
            "exporter_id": "python_reference_exporter_v1",
            "fixture_result_schema_version": result["schema_version"],
        },
    }


def _build_contract_schema_mapping(result):
    initial = result["initial_canonical_state"]
    first_card = initial["card_instances"][0]
    first_action_space = result["legal_action_checkpoints"][0]["action_space"]
    first_response = result["responses"][0]
    first_event = result["events"][0]
    first_snapshot = result["snapshot_player_1"]
    return {
        "fixture": result["fixture_identity"]["schema_version"],
        "canonical_match_state": initial["schema_version"],
        "card_instance": first_card["schema_version"],
        "action_space": first_action_space["schema_version"],
        "action_request": "minimal-action-request-unversioned",
        "action_response": first_response["schema_version"],
        "engine_event": first_event["schema_version"],
        "player_visible_snapshot": first_snapshot["schema_version"],
        "run_manifest": RUN_MANIFEST_SCHEMA_VERSION,
    }


def _resolve_build_identifier():
    repository_root = Path(__file__).resolve().parents[4]
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        value = completed.stdout.strip().lower()
        if completed.returncode == 0 and len(value) == 40 and all(char in "0123456789abcdef" for char in value):
            return value, None
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown", {
        "code": "BUILD_IDENTIFIER_UNAVAILABLE",
        "blocking": False,
        "description": "The source Git commit could not be resolved during export.",
    }


def _validate_canonical_hygiene(value):
    def visit(current):
        if isinstance(current, dict):
            for key, nested in current.items():
                if key.lower() in _FORBIDDEN_ENVIRONMENT_KEYS:
                    raise PythonReferenceExportError(
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
                raise PythonReferenceExportError(
                    "artifact_contract_invalid",
                    "Canonical artifact contains an absolute path.",
                    {"check": "absolute_path"},
                )
            if _UUID_PATTERN.search(current):
                raise PythonReferenceExportError(
                    "artifact_contract_invalid",
                    "Canonical artifact contains a random-UUID-shaped value.",
                    {"check": "random_uuid"},
                )
            if _MEMORY_ADDRESS_PATTERN.search(current):
                raise PythonReferenceExportError(
                    "artifact_contract_invalid",
                    "Canonical artifact contains a memory-address-shaped value.",
                    {"check": "memory_address"},
                )

    visit(value)


def _write_atomic_output(target, planned_files, manifest, *, replace):
    parent = target.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
        staging = _create_sibling_directory(parent, ".%s.staging-" % target.name)
    except OSError as exc:
        raise PythonReferenceExportError(
            "staging_write_failed",
            "Could not create the staging directory.",
            {"output_name": target.name},
        ) from exc

    try:
        try:
            for relative_path in REQUIRED_OUTPUT_PATHS:
                (staging / relative_path).write_bytes(planned_files[relative_path])
        except OSError as exc:
            raise PythonReferenceExportError(
                "staging_write_failed",
                "Could not write all staged artifacts.",
            ) from exc
        _validate_staging_directory(staging, planned_files, manifest)
        _promote_staging_directory(staging, target, replace=replace)
    finally:
        if staging.exists() or staging.is_symlink():
            _remove_explicit_sibling(staging, parent)


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
            if relative_path in _JSONL_PATHS:
                lines = text.splitlines()
                if not lines:
                    raise ValueError("JSONL artifact is empty for %s" % relative_path)
                for line in lines:
                    parsed = json.loads(line)
                    if not isinstance(parsed, dict):
                        raise ValueError("JSONL record is not an object for %s" % relative_path)
            else:
                parsed = json.loads(text)
                if not isinstance(parsed, dict):
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
        raise PythonReferenceExportError(
            "staging_validation_failed",
            "Staged artifact validation failed.",
        ) from exc


def _promote_staging_directory(staging, target, *, replace):
    if target.exists() and not replace:
        raise PythonReferenceExportError("output_exists", "Output directory already exists.")
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
        raise PythonReferenceExportError(
            "target_replace_failed",
            "Could not promote the validated staging directory.",
            {"output_name": target.name},
        ) from exc
    finally:
        if promoted and backup is not None and (backup.exists() or backup.is_symlink()):
            _remove_explicit_sibling(backup, target.parent)


def _remove_explicit_sibling(path, expected_parent):
    resolved_parent = path.parent.resolve()
    if resolved_parent != expected_parent.resolve():
        raise PythonReferenceExportError(
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


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export canonical Python runtime comparison artifacts.")
    parser.add_argument("--fixture", required=True, help="Path to the comparison fixture.json file.")
    parser.add_argument("--output", required=True, help="Output directory to create.")
    parser.add_argument("--replace", action="store_true", help="Replace only the explicit output directory.")
    args = parser.parse_args(argv)
    try:
        manifest = export_python_reference_artifacts(
            args.fixture,
            args.output,
            replace=args.replace,
        )
    except PythonReferenceExportError as exc:
        print("%s: %s" % (exc.code, exc.message), file=sys.stderr)
        return 1
    print("Python reference artifacts exported.")
    print("fixture_id: %s" % manifest["fixture_id"])
    print("oracle_version: %s" % manifest["oracle_version"])
    print("canonical_artifact_count: %s" % len(manifest["canonical_artifacts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CANONICAL_ARTIFACT_PATHS",
    "DIAGNOSTICS_SCHEMA_VERSION",
    "PythonReferenceExportError",
    "REQUIRED_OUTPUT_PATHS",
    "RUN_MANIFEST_SCHEMA_VERSION",
    "export_python_reference_artifacts",
    "main",
]
