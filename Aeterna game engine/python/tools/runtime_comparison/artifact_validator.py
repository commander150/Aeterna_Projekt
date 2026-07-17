"""Independent, read-only validation for runtime-comparison artifact sets.

The validator consumes already exported files.  It deliberately does not import
or execute the fixture runner, engine session, or reference exporter.
"""

from __future__ import annotations

import argparse
import copy
import json
import ntpath
import re
import sys
from pathlib import Path

from tools.runtime_comparison.canonical_json import (
    CanonicalJsonError,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    sha256_bytes,
)


VALIDATION_RESULT_SCHEMA_VERSION = (
    "aeterna-runtime-comparison-validation-result-v1"
)
VALIDATION_RESULT_CONTRACT_TYPE = "runtime_comparison_validation_result"

REQUIRED_ARTIFACT_PATHS = (
    "initial_state.json",
    "requests.jsonl",
    "responses.jsonl",
    "legal_actions.jsonl",
    "events.jsonl",
    "snapshot_player_1.json",
    "snapshot_player_2.json",
    "final_debug_state.json",
    "diagnostics.json",
    "run_manifest.json",
)
CANONICAL_ARTIFACT_PATHS = REQUIRED_ARTIFACT_PATHS[:-1]
JSONL_ARTIFACT_PATHS = {
    "requests.jsonl",
    "responses.jsonl",
    "legal_actions.jsonl",
    "events.jsonl",
}

EXPECTED_REQUEST_IDS = (
    "fixture_req_001_draw_player_1",
    "fixture_req_002_stale_end_turn_player_1",
    "fixture_req_003_end_turn_player_1",
    "fixture_req_004_draw_player_2",
)
EXPECTED_CHECKPOINT_IDS = (
    "initial_v0",
    "after_player_1_draw_v1",
    "after_player_1_end_turn_v2",
    "after_player_2_draw_v3",
)
EXPECTED_SCHEMA_MAPPING = {
    "action_request": "minimal-action-request-unversioned",
    "action_response": "minimal-action-response-v0",
    "action_space": "minimal-legal-action-space-v0",
    "canonical_match_state": "aeterna-canonical-match-state-v1",
    "card_instance": "minimal-card-instance-record-v1",
    "engine_event": "minimal-engine-event-v0",
    "fixture": "aeterna-runtime-comparison-fixture-v1",
    "player_visible_snapshot": "engine-player-visible-snapshot-v2",
    "run_manifest": "aeterna-runtime-comparison-run-manifest-v1",
}

_PHASE_RANKS = {
    "inventory": 10,
    "canonical_bytes": 20,
    "manifest": 30,
    "integrity": 40,
    "state": 50,
    "requests": 60,
    "responses": 70,
    "events": 80,
    "legal_actions": 90,
    "snapshots": 100,
    "diagnostics": 110,
    "cross_artifact": 120,
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_PROHIBITED_TECHNICAL_KEYS = {
    "absolute_path",
    "cwd",
    "hostname",
    "host_name",
    "pid",
    "process_id",
    "source_module",
    "stack",
    "stack_trace",
    "traceback",
    "user",
    "username",
}


class ArtifactValidatorInputError(ValueError):
    """Technical input error that prevents a validation result."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class _ValidationContext:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.semantic_checks = []

    def error(self, phase, artifact, code, message, **details):
        self.errors.append(
            _issue(phase, artifact, code, message, details)
        )

    def warning(self, phase, artifact, code, message, **details):
        self.warnings.append(
            _issue(phase, artifact, code, message, details)
        )

    def check(self, name, phase, artifacts, start_error_count):
        self.semantic_checks.append(
            {
                "artifacts": list(artifacts),
                "check": name,
                "passed": len(self.errors) == start_error_count,
                "phase": phase,
            }
        )


def _issue(phase, artifact, code, message, details):
    return {
        "artifact": artifact,
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
            key: _sanitize_result_value(value[key])
            for key in sorted(value)
        }
    if isinstance(value, (list, tuple)):
        return [_sanitize_result_value(item) for item in value]
    if isinstance(value, str) and (ntpath.isabs(value) or value.startswith("/")):
        return "<absolute-path-redacted>"
    return value


def _issue_sort_key(issue):
    details = json.dumps(
        issue["details"],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (
        _PHASE_RANKS[issue["phase"]],
        issue["artifact"],
        issue["code"],
        details,
    )


def _artifact_result(path):
    return {
        "byte_size": None,
        "canonical_bytes_valid": False,
        "hash_matches_manifest": None,
        "integrity_valid": False,
        "manifest_byte_size": None,
        "manifest_listed": False,
        "manifest_sha256": None,
        "parsed": False,
        "path": path,
        "present": False,
        "regular_file": False,
        "sha256": None,
        "size_matches_manifest": None,
    }


def _read_inventory(directory, context, artifact_results):
    try:
        entries = list(directory.iterdir())
    except OSError as exc:
        raise ArtifactValidatorInputError(
            "ARTIFACT_DIRECTORY_UNREADABLE",
            "Artifact directory cannot be read.",
        ) from exc

    by_name = {entry.name: entry for entry in entries}
    case_groups = {}
    for entry in entries:
        case_groups.setdefault(entry.name.casefold(), []).append(entry.name)

    expected_case = {name.casefold(): name for name in REQUIRED_ARTIFACT_PATHS}
    for folded_name, names in sorted(case_groups.items()):
        canonical_name = expected_case.get(folded_name)
        if len(names) > 1 or (canonical_name and names != [canonical_name]):
            context.error(
                "inventory",
                sorted(names)[0],
                "ARTIFACT_NAME_COLLISION",
                "Artifact names collide under case-insensitive comparison.",
                names=sorted(names),
            )

    for name in REQUIRED_ARTIFACT_PATHS:
        result = artifact_results[name]
        entry = by_name.get(name)
        if entry is None:
            context.error(
                "inventory",
                name,
                "ARTIFACT_MISSING",
                "Required artifact is missing.",
                path=name,
            )
            continue
        result["present"] = True
        if entry.is_symlink() or not entry.is_file():
            context.error(
                "inventory",
                name,
                "ARTIFACT_NOT_REGULAR_FILE",
                "Artifact must be a regular file and not a symlink.",
                path=name,
            )
            continue
        result["regular_file"] = True

    expected = set(REQUIRED_ARTIFACT_PATHS)
    for entry in sorted(entries, key=lambda item: item.name):
        if entry.name not in expected:
            context.error(
                "inventory",
                entry.name,
                "ARTIFACT_UNEXPECTED",
                "Artifact directory contains an unexpected entry.",
                path=entry.name,
            )
        if entry.name not in expected and (entry.is_symlink() or not entry.is_file()):
            context.error(
                "inventory",
                entry.name,
                "ARTIFACT_NOT_REGULAR_FILE",
                "Artifact directory entry is not a regular file.",
                path=entry.name,
            )

    data = {}
    for name in REQUIRED_ARTIFACT_PATHS:
        result = artifact_results[name]
        if not result["regular_file"]:
            continue
        try:
            payload = by_name[name].read_bytes()
        except OSError as exc:
            raise ArtifactValidatorInputError(
                "ARTIFACT_FILE_UNREADABLE",
                "Artifact file cannot be read: %s." % name,
            ) from exc
        data[name] = payload
        result["byte_size"] = len(payload)
        result["sha256"] = sha256_bytes(payload)
    return data


def _reject_json_constant(value):
    raise ValueError("Non-finite JSON number is not allowed: %s." % value)


def _decode_utf8(data, context, artifact):
    source = data
    if source.startswith(b"\xef\xbb\xbf"):
        context.error(
            "canonical_bytes",
            artifact,
            "ARTIFACT_BOM_PRESENT",
            "UTF-8 BOM is not allowed.",
        )
        source = source[3:]
    if b"\r" in source:
        context.error(
            "canonical_bytes",
            artifact,
            "ARTIFACT_LINE_ENDING_INVALID",
            "Only LF line endings are allowed.",
        )
    try:
        return source.decode("utf-8")
    except UnicodeDecodeError:
        context.error(
            "canonical_bytes",
            artifact,
            "ARTIFACT_ENCODING_INVALID",
            "Artifact is not valid UTF-8.",
        )
        return None


def _validate_final_lf(data, context, artifact):
    without_bom = data[3:] if data.startswith(b"\xef\xbb\xbf") else data
    if not without_bom.endswith(b"\n") or without_bom.endswith(b"\n\n"):
        context.error(
            "canonical_bytes",
            artifact,
            "ARTIFACT_LINE_ENDING_INVALID",
            "Artifact must end with exactly one LF.",
        )


def _parse_canonical_json(data, context, artifact, result):
    start = len(context.errors)
    _validate_final_lf(data, context, artifact)
    text = _decode_utf8(data, context, artifact)
    if text is None:
        return None
    try:
        value = json.loads(text, parse_constant=_reject_json_constant)
    except (json.JSONDecodeError, ValueError):
        context.error(
            "canonical_bytes",
            artifact,
            "ARTIFACT_JSON_PARSE_FAILED",
            "Artifact is not valid strict JSON.",
        )
        return None
    if not isinstance(value, dict):
        context.error(
            "canonical_bytes",
            artifact,
            "ARTIFACT_JSON_ROOT_INVALID",
            "JSON artifact root must be an object.",
        )
        return None
    result["parsed"] = True
    try:
        regenerated = canonical_json_bytes(value)
    except CanonicalJsonError:
        regenerated = None
    if regenerated != data:
        context.error(
            "canonical_bytes",
            artifact,
            "ARTIFACT_CANONICAL_BYTES_MISMATCH",
            "JSON bytes do not match the canonical serialization.",
        )
    result["canonical_bytes_valid"] = len(context.errors) == start
    return value


def _parse_canonical_jsonl(data, context, artifact, result):
    start = len(context.errors)
    _validate_final_lf(data, context, artifact)
    text = _decode_utf8(data, context, artifact)
    if text is None:
        return None
    lines = text[:-1].split("\n") if text.endswith("\n") else text.split("\n")
    records = []
    valid_records = True
    for index, line in enumerate(lines, start=1):
        if not line:
            context.error(
                "canonical_bytes",
                artifact,
                "ARTIFACT_JSONL_RECORD_INVALID",
                "JSONL contains an empty record line.",
                line=index,
            )
            valid_records = False
            continue
        try:
            record = json.loads(line, parse_constant=_reject_json_constant)
        except (json.JSONDecodeError, ValueError):
            context.error(
                "canonical_bytes",
                artifact,
                "ARTIFACT_JSON_PARSE_FAILED",
                "JSONL record is not valid strict JSON.",
                line=index,
            )
            valid_records = False
            continue
        if not isinstance(record, dict):
            context.error(
                "canonical_bytes",
                artifact,
                "ARTIFACT_JSONL_RECORD_INVALID",
                "Every JSONL record must be an object.",
                line=index,
            )
            valid_records = False
            continue
        records.append(record)
    if not valid_records:
        return None
    result["parsed"] = True
    try:
        regenerated = canonical_jsonl_bytes(records)
    except CanonicalJsonError:
        regenerated = None
    if regenerated != data:
        context.error(
            "canonical_bytes",
            artifact,
            "ARTIFACT_CANONICAL_BYTES_MISMATCH",
            "JSONL bytes do not match the canonical serialization.",
        )
    result["canonical_bytes_valid"] = len(context.errors) == start
    return records


def _parse_artifacts(data, context, artifact_results):
    parsed = {}
    for name in REQUIRED_ARTIFACT_PATHS:
        payload = data.get(name)
        if payload is None:
            continue
        if name in JSONL_ARTIFACT_PATHS:
            value = _parse_canonical_jsonl(
                payload, context, name, artifact_results[name]
            )
        else:
            value = _parse_canonical_json(
                payload, context, name, artifact_results[name]
            )
        if value is not None:
            parsed[name] = value
    return parsed


def _manifest_path_is_safe(path):
    if not isinstance(path, str) or not path:
        return False
    if ntpath.isabs(path) or path in {".", ".."}:
        return False
    if "/" in path or "\\" in path or ".." in path:
        return False
    return Path(path).name == path


def _validate_manifest(manifest, context):
    if not isinstance(manifest, dict):
        return {}
    start = len(context.errors)
    artifact = "run_manifest.json"
    if manifest.get("schema_version") != EXPECTED_SCHEMA_MAPPING["run_manifest"]:
        context.error(
            "manifest",
            artifact,
            "MANIFEST_CONTRACT_INVALID",
            "Run manifest schema_version is invalid.",
            field="schema_version",
        )
    if manifest.get("contract_type") != "runtime_comparison_run_manifest":
        context.error(
            "manifest",
            artifact,
            "MANIFEST_CONTRACT_INVALID",
            "Run manifest contract_type is invalid.",
            field="contract_type",
        )
    for field in (
        "fixture_id",
        "oracle_id",
        "oracle_version",
        "runtime_candidate",
        "implementation_language",
    ):
        value = manifest.get(field)
        if value is None or value == "":
            context.error(
                "manifest",
                artifact,
                "MANIFEST_CONTRACT_INVALID",
                "Run manifest required identity field is missing.",
                field=field,
            )

    mapping = manifest.get("contract_schema_mapping")
    if not isinstance(mapping, dict):
        context.error(
            "manifest",
            artifact,
            "MANIFEST_SCHEMA_MAPPING_INVALID",
            "contract_schema_mapping must be an object.",
        )
    if not isinstance(manifest.get("known_deviations"), list):
        context.error(
            "manifest",
            artifact,
            "MANIFEST_CONTRACT_INVALID",
            "known_deviations must be a list.",
            field="known_deviations",
        )
    if not isinstance(manifest.get("implementation_specific"), dict):
        context.error(
            "manifest",
            artifact,
            "MANIFEST_CONTRACT_INVALID",
            "implementation_specific must be an object.",
            field="implementation_specific",
        )

    entries = manifest.get("canonical_artifacts")
    if not isinstance(entries, list):
        context.error(
            "manifest",
            artifact,
            "MANIFEST_CONTRACT_INVALID",
            "canonical_artifacts must be a list.",
            field="canonical_artifacts",
        )
        entries = []
    if len(entries) != len(CANONICAL_ARTIFACT_PATHS):
        context.error(
            "manifest",
            artifact,
            "MANIFEST_ARTIFACT_SEQUENCE_INVALID",
            "Run manifest must list exactly nine canonical artifacts.",
            actual_count=len(entries),
            expected_count=len(CANONICAL_ARTIFACT_PATHS),
        )

    paths = []
    entry_map = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            context.error(
                "manifest",
                artifact,
                "MANIFEST_CONTRACT_INVALID",
                "Canonical artifact entry must be an object.",
                index=index,
            )
            continue
        path = entry.get("path")
        if not _manifest_path_is_safe(path):
            context.error(
                "manifest",
                artifact,
                "MANIFEST_ARTIFACT_PATH_INVALID",
                "Canonical artifact path must be one safe relative filename.",
                index=index,
                path=path if isinstance(path, str) else "",
            )
            continue
        if path == "run_manifest.json":
            context.error(
                "manifest",
                artifact,
                "MANIFEST_ARTIFACT_PATH_INVALID",
                "Run manifest must not list itself as a canonical artifact.",
                index=index,
                path=path,
            )
        paths.append(path)
        entry_map.setdefault(path, []).append(entry)
        expected_media = (
            "application/x-ndjson" if path in JSONL_ARTIFACT_PATHS else "application/json"
        )
        expected_canonicalization = (
            "aeterna-canonical-jsonl-v1"
            if path in JSONL_ARTIFACT_PATHS
            else "aeterna-canonical-json-v1"
        )
        fields_valid = (
            entry.get("media_type") == expected_media
            and entry.get("canonicalization") == expected_canonicalization
            and isinstance(entry.get("byte_size"), int)
            and entry.get("byte_size", -1) >= 0
            and isinstance(entry.get("sha256"), str)
            and bool(_SHA256_RE.fullmatch(entry.get("sha256", "")))
            and entry.get("comparison_level") == "canonical_bytes"
        )
        if not fields_valid:
            context.error(
                "manifest",
                artifact,
                "MANIFEST_CONTRACT_INVALID",
                "Canonical artifact manifest entry has invalid fields.",
                index=index,
                path=path,
            )

    for path, duplicates in sorted(entry_map.items()):
        if len(duplicates) > 1:
            context.error(
                "manifest",
                path,
                "ARTIFACT_MANIFEST_ENTRY_DUPLICATED",
                "Canonical artifact has duplicate manifest entries.",
                count=len(duplicates),
                path=path,
            )
    if paths != list(CANONICAL_ARTIFACT_PATHS):
        context.error(
            "manifest",
            artifact,
            "MANIFEST_ARTIFACT_SEQUENCE_INVALID",
            "Canonical artifact paths are missing, unexpected, or out of order.",
            actual_paths=paths,
            expected_paths=list(CANONICAL_ARTIFACT_PATHS),
        )

    context.warning(
        "manifest",
        artifact,
        "BUILD_IDENTIFIER_NOT_EXTERNALLY_VERIFIED",
        "build_identifier is recorded but cannot be verified from artifacts alone.",
    )
    deviations = manifest.get("known_deviations")
    if isinstance(deviations, list):
        for deviation in deviations:
            code = deviation.get("code") if isinstance(deviation, dict) else ""
            context.warning(
                "manifest",
                artifact,
                "KNOWN_DEVIATION_DECLARED",
                "Run manifest declares a known deviation.",
                deviation_code=code if isinstance(code, str) else "",
            )
    if isinstance(mapping, dict) and mapping.get("action_request") == (
        "minimal-action-request-unversioned"
    ):
        context.warning(
            "manifest",
            "requests.jsonl",
            "REQUEST_CONTRACT_UNVERSIONED",
            "Action requests use the declared unversioned minimal contract.",
        )
    context.check(
        "run_manifest_contract",
        "manifest",
        (artifact,),
        start,
    )
    return entry_map


def _validate_integrity(data, entry_map, context, artifact_results):
    start = len(context.errors)
    for path in CANONICAL_ARTIFACT_PATHS:
        result = artifact_results[path]
        entries = entry_map.get(path, [])
        if not entries:
            context.error(
                "integrity",
                path,
                "ARTIFACT_MANIFEST_ENTRY_MISSING",
                "Canonical artifact is not listed once in the run manifest.",
                path=path,
            )
            continue
        if len(entries) != 1:
            continue
        entry = entries[0]
        result["manifest_listed"] = True
        result["manifest_byte_size"] = entry.get("byte_size")
        result["manifest_sha256"] = entry.get("sha256")
        payload = data.get(path)
        if payload is None:
            continue
        size_matches = entry.get("byte_size") == len(payload)
        hash_matches = entry.get("sha256") == sha256_bytes(payload)
        result["size_matches_manifest"] = size_matches
        result["hash_matches_manifest"] = hash_matches
        result["integrity_valid"] = size_matches and hash_matches
        if not size_matches:
            context.error(
                "integrity",
                path,
                "ARTIFACT_SIZE_MISMATCH",
                "Actual artifact byte size differs from the run manifest.",
                actual_byte_size=len(payload),
                manifest_byte_size=entry.get("byte_size"),
            )
        if not hash_matches:
            context.error(
                "integrity",
                path,
                "ARTIFACT_HASH_MISMATCH",
                "Actual artifact SHA-256 differs from the run manifest.",
                actual_sha256=sha256_bytes(payload),
                manifest_sha256=entry.get("sha256"),
            )
    manifest_result = artifact_results["run_manifest.json"]
    if manifest_result["regular_file"]:
        manifest_result["size_matches_manifest"] = True
        manifest_result["hash_matches_manifest"] = True
        manifest_result["integrity_valid"] = True
    context.check(
        "independent_size_and_sha256",
        "integrity",
        CANONICAL_ARTIFACT_PATHS,
        start,
    )


def _record_state_error(context, artifact, code, message, check, **details):
    details["check"] = check
    context.error("state", artifact, code, message, **details)


def _validate_state(state, artifact, context, expected_kind):
    start = len(context.errors)
    if not isinstance(state, dict):
        return
    if (
        state.get("schema_version") != EXPECTED_SCHEMA_MAPPING["canonical_match_state"]
        or state.get("contract_type") != "canonical_match_state"
    ):
        _record_state_error(
            context,
            artifact,
            "STATE_SCHEMA_INVALID",
            "State schema or contract type is invalid.",
            "root_contract",
        )

    list_fields = (
        "players",
        "card_instances",
        "domain_topologies",
        "domain_occupancies",
        "event_log",
    )
    for field in list_fields:
        if not isinstance(state.get(field), list):
            _record_state_error(
                context,
                artifact,
                "STATE_SCHEMA_INVALID",
                "Canonical state collection must be a list.",
                "collection_type",
                field=field,
            )

    players = state.get("players") if isinstance(state.get("players"), list) else []
    player_ids = [
        player.get("player_id") if isinstance(player, dict) else None
        for player in players
    ]
    if player_ids != ["player_1", "player_2"] or len(set(player_ids)) != len(player_ids):
        _record_state_error(
            context,
            artifact,
            "STATE_PLAYER_ORDER_INVALID",
            "Players must be unique and ordered player_1, player_2.",
            "player_order",
            actual_player_ids=player_ids,
        )
    for field in ("active_player_id", "priority_player_id"):
        if state.get(field) not in player_ids:
            _record_state_error(
                context,
                artifact,
                "STATE_PLAYER_ORDER_INVALID",
                "Active and priority players must reference a state player.",
                "active_priority_reference",
                field=field,
                value=state.get(field),
            )
    if state.get("priority_model") != "minimal_priority_model_v1":
        _record_state_error(
            context,
            artifact,
            "STATE_SCHEMA_INVALID",
            "State priority model is invalid.",
            "priority_model",
            value=state.get("priority_model"),
        )

    cards = (
        state.get("card_instances")
        if isinstance(state.get("card_instances"), list)
        else []
    )
    registry = {}
    card_ids = []
    created_sequences = []
    for index, card in enumerate(cards):
        if not isinstance(card, dict):
            _record_state_error(
                context,
                artifact,
                "STATE_SCHEMA_INVALID",
                "Card instance record must be an object.",
                "card_record_type",
                index=index,
            )
            continue
        card_instance_id = card.get("card_instance_id")
        card_ids.append(card_instance_id)
        if isinstance(card_instance_id, str):
            registry.setdefault(card_instance_id, []).append(card)
        created_sequences.append(card.get("created_sequence"))
        if (
            card.get("schema_version") != EXPECTED_SCHEMA_MAPPING["card_instance"]
            or card.get("contract_type") != "card_instance_record"
        ):
            _record_state_error(
                context,
                artifact,
                "STATE_SCHEMA_INVALID",
                "Card instance schema or contract type is invalid.",
                "card_contract",
                index=index,
            )
    duplicates = sorted(
        key for key, records in registry.items() if len(records) > 1
    )
    if duplicates or any(not isinstance(value, str) for value in card_ids):
        _record_state_error(
            context,
            artifact,
            "STATE_ZONE_REFERENCE_INVALID",
            "Card instance IDs must be non-empty and unique.",
            "card_instance_identity",
            duplicate_ids=duplicates,
        )
    if (
        any(not isinstance(value, int) for value in created_sequences)
        or created_sequences != sorted(created_sequences)
    ):
        _record_state_error(
            context,
            artifact,
            "STATE_CARD_INSTANCE_ORDER_INVALID",
            "Card instances must be ordered by non-decreasing created_sequence.",
            "created_sequence_order",
            actual_sequences=created_sequences,
        )

    memberships = {}
    zone_field_map = {
        "hand": "hand_card_instance_ids",
        "deck": "deck_card_instance_ids",
        "discard": "discard_card_instance_ids",
    }
    for player in players:
        if not isinstance(player, dict):
            continue
        player_id = player.get("player_id")
        for zone, field in zone_field_map.items():
            references = player.get(field)
            if not isinstance(references, list):
                _record_state_error(
                    context,
                    artifact,
                    "STATE_SCHEMA_INVALID",
                    "Player zone references must be lists.",
                    "zone_list_type",
                    field=field,
                    player_id=player_id,
                )
                continue
            for zone_index, card_instance_id in enumerate(references):
                memberships.setdefault(card_instance_id, []).append(
                    (player_id, zone, zone_index)
                )
                if card_instance_id not in registry:
                    _record_state_error(
                        context,
                        artifact,
                        "STATE_ZONE_REFERENCE_INVALID",
                        "Player zone references an unknown card instance.",
                        "unknown_zone_reference",
                        card_instance_id=card_instance_id,
                        player_id=player_id,
                        zone=zone,
                    )

    for card_instance_id, records in sorted(registry.items()):
        positions = memberships.get(card_instance_id, [])
        if len(positions) != 1:
            _record_state_error(
                context,
                artifact,
                "STATE_ZONE_MEMBERSHIP_INVALID",
                "Every card instance must appear in exactly one player zone.",
                "zone_membership_count",
                card_instance_id=card_instance_id,
                membership_count=len(positions),
            )
            continue
        player_id, zone, zone_index = positions[0]
        card = records[0]
        if (
            card.get("owner_player_id") != player_id
            or card.get("zone") != zone
            or card.get("zone_index") != zone_index
        ):
            _record_state_error(
                context,
                artifact,
                "STATE_ZONE_MEMBERSHIP_INVALID",
                "Card registry location does not match the player zone list.",
                "registry_zone_match",
                card_instance_id=card_instance_id,
            )

    for field, nested_field, expected_schema in (
        ("domain_topologies", "topology", "minimal-player-domain-topology-v0"),
        ("domain_occupancies", "occupancy", "minimal-player-domain-occupancy-v0"),
    ):
        wrappers = state.get(field) if isinstance(state.get(field), list) else []
        wrapper_ids = [
            item.get("player_id") if isinstance(item, dict) else None
            for item in wrappers
        ]
        valid = wrapper_ids == ["player_1", "player_2"]
        for wrapper in wrappers:
            nested = wrapper.get(nested_field) if isinstance(wrapper, dict) else None
            valid = valid and isinstance(nested, dict)
            if isinstance(nested, dict):
                valid = valid and nested.get("player_id") == wrapper.get("player_id")
                valid = valid and nested.get("schema_version") == expected_schema
                if nested_field == "topology":
                    valid = valid and nested.get("current_count") == 6
                    valid = valid and len(nested.get("positions", [])) == 18
                else:
                    valid = valid and nested.get("slot_count") == 12
                    valid = valid and len(nested.get("slots", [])) == 12
        if not valid:
            _record_state_error(
                context,
                artifact,
                "STATE_DOMAIN_MAPPING_INVALID",
                "Domain topology or occupancy mapping is invalid.",
                field,
                player_ids=wrapper_ids,
            )

    event_log = state.get("event_log") if isinstance(state.get("event_log"), list) else []
    sequences = [
        event.get("event_sequence") if isinstance(event, dict) else None
        for event in event_log
    ]
    indexes = [
        event.get("event_index") if isinstance(event, dict) else None
        for event in event_log
    ]
    if sequences != list(range(1, len(event_log) + 1)) or indexes != list(
        range(len(event_log))
    ):
        _record_state_error(
            context,
            artifact,
            "STATE_EVENT_SEQUENCE_INVALID",
            "State event log sequence or index is not continuous.",
            "event_sequence",
            event_indexes=indexes,
            event_sequences=sequences,
        )

    expected = {
        "initial": {
            "active_player_id": "player_1",
            "event_count": 0,
            "priority_player_id": "player_1",
            "state_version": 0,
            "turn_number": 1,
            "zone_counts": (1, 2, 0),
        },
        "final": {
            "active_player_id": "player_2",
            "event_count": 3,
            "priority_player_id": "player_2",
            "state_version": 3,
            "turn_number": 1,
            "zone_counts": (2, 1, 0),
        },
    }[expected_kind]
    semantic_failures = []
    for field in (
        "active_player_id",
        "priority_player_id",
        "state_version",
        "turn_number",
    ):
        if state.get(field) != expected[field]:
            semantic_failures.append(field)
    if len(event_log) != expected["event_count"]:
        semantic_failures.append("event_count")
    if state.get("phase") != "main":
        semantic_failures.append("phase")
    hand_count, deck_count, discard_count = expected["zone_counts"]
    for player in players:
        if not isinstance(player, dict):
            continue
        actual_counts = (
            len(player.get("hand_card_instance_ids", [])),
            len(player.get("deck_card_instance_ids", [])),
            len(player.get("discard_card_instance_ids", [])),
        )
        if actual_counts != (hand_count, deck_count, discard_count):
            semantic_failures.append("zones:%s" % player.get("player_id"))
    if semantic_failures:
        code = (
            "INITIAL_STATE_SEMANTICS_INVALID"
            if expected_kind == "initial"
            else "FINAL_STATE_SEMANTICS_INVALID"
        )
        _record_state_error(
            context,
            artifact,
            code,
            "State does not match the fixed comparison fixture semantics.",
            "%s_semantics" % expected_kind,
            failed_fields=sorted(set(semantic_failures)),
        )
    context.check(
        "%s_state_semantics" % expected_kind,
        "state",
        (artifact,),
        start,
    )


def _validate_requests(requests, match_id, context):
    artifact = "requests.jsonl"
    start = len(context.errors)
    if not isinstance(requests, list):
        return
    if len(requests) != 4:
        context.error(
            "requests",
            artifact,
            "REQUEST_COUNT_INVALID",
            "Request artifact must contain exactly four records.",
            actual_count=len(requests),
            expected_count=4,
        )
    ids = [record.get("request_id") for record in requests]
    if ids != list(EXPECTED_REQUEST_IDS):
        context.error(
            "requests",
            artifact,
            "REQUEST_ID_SEQUENCE_INVALID",
            "Request IDs are missing, unexpected, or out of order.",
            actual_ids=ids,
            expected_ids=list(EXPECTED_REQUEST_IDS),
        )
    duplicate_ids = sorted(
        {value for value in ids if ids.count(value) > 1 and isinstance(value, str)}
    )
    if duplicate_ids:
        context.error(
            "requests",
            artifact,
            "REQUEST_ID_DUPLICATED",
            "Request IDs must be unique.",
            duplicate_ids=duplicate_ids,
        )
    if [record.get("match_id") for record in requests] != [match_id] * len(requests):
        context.error(
            "requests",
            artifact,
            "REQUEST_MATCH_ID_MISMATCH",
            "Every request must reference the canonical match ID.",
        )
    expected_players = ["player_1", "player_1", "player_1", "player_2"]
    if [record.get("player_id") for record in requests] != expected_players:
        context.error(
            "requests",
            artifact,
            "REQUEST_PLAYER_SEQUENCE_INVALID",
            "Request player sequence is invalid.",
            expected_players=expected_players,
        )
    expected_actions = ["draw_card", "end_turn", "end_turn", "draw_card"]
    if [record.get("action_type") for record in requests] != expected_actions:
        context.error(
            "requests",
            artifact,
            "REQUEST_ACTION_SEQUENCE_INVALID",
            "Request action sequence is invalid.",
            expected_actions=expected_actions,
        )
    expected_versions = [0, 0, 1, 2]
    if [record.get("expected_state_version") for record in requests] != expected_versions:
        context.error(
            "requests",
            artifact,
            "REQUEST_EXPECTED_VERSION_INVALID",
            "Request expected_state_version sequence is invalid.",
            expected_versions=expected_versions,
        )
    expected_fields = {
        "action_id",
        "action_type",
        "expected_state_version",
        "match_id",
        "payload",
        "player_id",
        "request_id",
    }
    for index, record in enumerate(requests):
        if record.get("payload") != {}:
            context.error(
                "requests",
                artifact,
                "REQUEST_PAYLOAD_INVALID",
                "Request payload must be exactly an empty object.",
                index=index,
            )
        if set(record) != expected_fields or not isinstance(record.get("action_id"), str):
            context.error(
                "requests",
                artifact,
                "REQUEST_CONTRACT_INVALID",
                "Request fields do not match the fixed minimal request contract.",
                index=index,
            )
    context.check("request_sequence", "requests", (artifact,), start)


def _validate_responses(responses, requests, match_id, context):
    artifact = "responses.jsonl"
    start = len(context.errors)
    if not isinstance(responses, list):
        return
    if len(responses) != 4:
        context.error(
            "responses",
            artifact,
            "RESPONSE_COUNT_INVALID",
            "Response artifact must contain exactly four records.",
            actual_count=len(responses),
            expected_count=4,
        )
    request_ids = [request.get("request_id") for request in requests]
    if [response.get("request_id") for response in responses] != request_ids:
        context.error(
            "responses",
            artifact,
            "RESPONSE_REQUEST_ID_MISMATCH",
            "Response request IDs must match requests in order.",
        )
    expected_accepted = [True, False, True, True]
    if [response.get("accepted") for response in responses] != expected_accepted:
        context.error(
            "responses",
            artifact,
            "RESPONSE_ACCEPTANCE_SEQUENCE_INVALID",
            "Response accepted sequence is invalid.",
            expected_accepted=expected_accepted,
        )
    expected_reasons = [None, "stale_state_version", None, None]
    if [response.get("reason") for response in responses] != expected_reasons:
        context.error(
            "responses",
            artifact,
            "RESPONSE_REASON_INVALID",
            "Response reason sequence is invalid.",
            expected_reasons=expected_reasons,
        )
    expected_version_path = [(0, 1), (1, 1), (1, 2), (2, 3)]
    actual_version_path = [
        (response.get("state_version_before"), response.get("state_version_after"))
        for response in responses
    ]
    if actual_version_path != expected_version_path:
        context.error(
            "responses",
            artifact,
            "RESPONSE_STATE_VERSION_PATH_INVALID",
            "Response state-version path is invalid.",
            actual_path=[list(item) for item in actual_version_path],
            expected_path=[list(item) for item in expected_version_path],
        )
    stale_diagnostic = {
        "category": "request_validation",
        "code": "STALE_STATE_VERSION",
        "current_state_version": 1,
        "expected_state_version": 0,
        "retry_policy": "refresh_projection",
        "severity": "error",
    }
    for index, response in enumerate(responses):
        events = response.get("events")
        diagnostics = response.get("diagnostics")
        if not isinstance(events, list):
            context.error(
                "responses",
                artifact,
                "RESPONSE_EVENTS_INVALID",
                "Response events must be a list.",
                index=index,
            )
            events = []
        if not isinstance(diagnostics, list):
            context.error(
                "responses",
                artifact,
                "RESPONSE_DIAGNOSTICS_INVALID",
                "Response diagnostics must be a list.",
                index=index,
            )
            diagnostics = []
        if (
            response.get("schema_version") != EXPECTED_SCHEMA_MAPPING["action_response"]
            or response.get("contract_type") != "action_response"
            or response.get("response_type") != "minimal_action_response"
            or response.get("match_id") != match_id
            or response.get("success") != response.get("accepted")
        ):
            context.error(
                "responses",
                artifact,
                "RESPONSE_DIAGNOSTICS_INVALID",
                "Response contract identity or success state is invalid.",
                index=index,
            )
        if index == 1:
            if events != []:
                context.error(
                    "responses",
                    artifact,
                    "RESPONSE_EVENTS_INVALID",
                    "Stale response must not contain gameplay events.",
                    index=index,
                )
            if diagnostics != [stale_diagnostic]:
                context.error(
                    "responses",
                    artifact,
                    "STALE_DIAGNOSTIC_INVALID",
                    "Stale response diagnostic is not canonical.",
                    index=index,
                )
        elif response.get("accepted") is True:
            blocking = [
                item
                for item in diagnostics
                if isinstance(item, dict) and item.get("severity") == "error"
            ]
            if blocking:
                context.error(
                    "responses",
                    artifact,
                    "RESPONSE_DIAGNOSTICS_INVALID",
                    "Accepted response contains a blocking diagnostic.",
                    index=index,
                )
    context.check("response_sequence", "responses", (artifact,), start)


def _canonicalize_response_event(event):
    normalized = copy.deepcopy(event)
    if not isinstance(normalized, dict):
        return normalized
    normalized.setdefault("semantic_metadata", {})
    payload = normalized.get("payload")
    if isinstance(payload, dict) and "metadata" in payload:
        payload["semantic_metadata"] = payload.pop("metadata")
    return normalized


def _validate_events(events, final_state, responses, context):
    artifact = "events.jsonl"
    start = len(context.errors)
    if not isinstance(events, list):
        return
    if len(events) != 3:
        context.error(
            "events",
            artifact,
            "EVENT_COUNT_INVALID",
            "Event artifact must contain exactly three records.",
            actual_count=len(events),
            expected_count=3,
        )
    sequences = [event.get("event_sequence") for event in events]
    if sequences != [1, 2, 3]:
        context.error(
            "events",
            artifact,
            "EVENT_SEQUENCE_INVALID",
            "Event sequence must be exactly 1, 2, 3.",
            actual_sequences=sequences,
        )
    expected_types = ["zone_move", "turn_transition", "zone_move"]
    if [event.get("event_type") for event in events] != expected_types:
        context.error(
            "events",
            artifact,
            "EVENT_TYPE_SEQUENCE_INVALID",
            "Event type sequence is invalid.",
            expected_types=expected_types,
        )
    if [event.get("state_version") for event in events] != [1, 2, 3]:
        context.error(
            "events",
            artifact,
            "EVENT_STATE_VERSION_INVALID",
            "Event state-version sequence is invalid.",
        )
    expected_players = ["player_1", "player_1", "player_2"]
    expected_actions = ["draw_card", "end_turn", "draw_card"]
    for index, event in enumerate(events):
        payload = event.get("payload")
        event_type = event.get("event_type")
        expected_payload_contract = (
            "zone_move" if event_type == "zone_move" else "turn_transition"
        )
        expected_payload_schema = (
            "minimal-zone-move-record-v0"
            if event_type == "zone_move"
            else "minimal-turn-transition-record-v0"
        )
        valid = (
            event.get("schema_version") == EXPECTED_SCHEMA_MAPPING["engine_event"]
            and event.get("contract_type") == "engine_event"
            and event.get("event_index") == index
            and event.get("player_id") == expected_players[index]
            and event.get("action_type") == expected_actions[index]
            and event.get("turn_number") == 1
            and isinstance(payload, dict)
            and payload.get("contract_type") == expected_payload_contract
            and payload.get("schema_version") == expected_payload_schema
            and payload.get("event_sequence") == index + 1
            and payload.get("state_version") == index + 1
        )
        if not valid:
            context.error(
                "events",
                artifact,
                "EVENT_CONTRACT_INVALID",
                "Engine event or typed payload contract is invalid.",
                index=index,
            )
        prohibited = _find_prohibited_keys(event)
        if prohibited:
            context.error(
                "events",
                artifact,
                "EVENT_CONTRACT_INVALID",
                "Engine event contains implementation-specific metadata.",
                index=index,
                prohibited_keys=prohibited,
            )

    final_events = (
        final_state.get("event_log") if isinstance(final_state, dict) else None
    )
    if final_events != events:
        context.error(
            "events",
            artifact,
            "EVENT_FINAL_STATE_MISMATCH",
            "events.jsonl does not equal the final canonical event log.",
        )
    response_events = []
    for response in responses:
        if isinstance(response, dict) and response.get("accepted") is True:
            response_events.extend(response.get("events", []))
        elif isinstance(response, dict) and response.get("events"):
            context.error(
                "events",
                artifact,
                "EVENT_RESPONSE_MISMATCH",
                "Rejected response references a gameplay event.",
                request_id=response.get("request_id"),
            )
    normalized_response_events = [
        _canonicalize_response_event(event) for event in response_events
    ]
    if normalized_response_events != events:
        context.error(
            "events",
            artifact,
            "EVENT_RESPONSE_MISMATCH",
            "Accepted response events do not equal the canonical event stream.",
        )
    context.check(
        "event_trajectory",
        "events",
        (artifact, "responses.jsonl", "final_debug_state.json"),
        start,
    )


def _validate_legal_actions(checkpoints, match_id, context):
    artifact = "legal_actions.jsonl"
    start = len(context.errors)
    if not isinstance(checkpoints, list):
        return
    if len(checkpoints) != 4:
        context.error(
            "legal_actions",
            artifact,
            "LEGAL_ACTION_CHECKPOINT_COUNT_INVALID",
            "Legal-action artifact must contain exactly four checkpoints.",
            actual_count=len(checkpoints),
            expected_count=4,
        )
    checkpoint_ids = [item.get("checkpoint_id") for item in checkpoints]
    expected_versions = [0, 1, 2, 3]
    expected_players = ["player_1", "player_1", "player_2", "player_2"]
    if (
        checkpoint_ids != list(EXPECTED_CHECKPOINT_IDS)
        or len(set(checkpoint_ids)) != len(checkpoint_ids)
    ):
        context.error(
            "legal_actions",
            artifact,
            "LEGAL_ACTION_CHECKPOINT_SEQUENCE_INVALID",
            "Checkpoint IDs are missing, duplicated, or out of order.",
            actual_ids=checkpoint_ids,
            expected_ids=list(EXPECTED_CHECKPOINT_IDS),
        )
    if [item.get("state_version") for item in checkpoints] != expected_versions:
        context.error(
            "legal_actions",
            artifact,
            "LEGAL_ACTION_STATE_VERSION_INVALID",
            "Checkpoint state-version sequence is invalid.",
            expected_versions=expected_versions,
        )
    for index, checkpoint in enumerate(checkpoints):
        action_space = checkpoint.get("action_space")
        if not isinstance(action_space, dict):
            context.error(
                "legal_actions",
                artifact,
                "LEGAL_ACTION_CONTRACT_INVALID",
                "Checkpoint action_space must be an object.",
                index=index,
            )
            continue
        actions = action_space.get("actions")
        valid_contract = (
            action_space.get("schema_version") == EXPECTED_SCHEMA_MAPPING["action_space"]
            and action_space.get("contract_type") == "legal_action_space"
            and action_space.get("match_id") == match_id
            and action_space.get("state_version") == checkpoint.get("state_version")
            and action_space.get("player_id") == expected_players[index]
            and checkpoint.get("player_id") == expected_players[index]
            and checkpoint.get("state_unchanged") is True
            and isinstance(actions, list)
        )
        if not valid_contract:
            context.error(
                "legal_actions",
                artifact,
                "LEGAL_ACTION_CONTRACT_INVALID",
                "Legal-action checkpoint contract is invalid.",
                index=index,
            )
        if not isinstance(actions, list):
            continue
        expected_sorted = sorted(
            actions,
            key=lambda action: (
                (
                    action.get("order_rank")
                    if isinstance(action.get("order_rank"), int)
                    else 2**31
                ),
                (
                    action.get("action_type")
                    if isinstance(action.get("action_type"), str)
                    else ""
                ),
                (
                    action.get("action_id")
                    if isinstance(action.get("action_id"), str)
                    else ""
                ),
            ),
        )
        if actions != expected_sorted:
            context.error(
                "legal_actions",
                artifact,
                "LEGAL_ACTION_ORDER_INVALID",
                "Legal actions are not in canonical rank/type/ID order.",
                index=index,
            )
        expected_ranks = {"end_turn": 100, "draw_card": 200}
        for action_index, action in enumerate(actions):
            action_type = action.get("action_type")
            request_template = action.get("request_template")
            valid_rank = action.get("order_rank") == expected_ranks.get(action_type)
            if not valid_rank:
                context.error(
                    "legal_actions",
                    artifact,
                    "LEGAL_ACTION_RANK_INVALID",
                    "Legal action rank is invalid.",
                    action_index=action_index,
                    checkpoint_index=index,
                )
            valid_action = (
                isinstance(action.get("action_id"), str)
                and action_type in expected_ranks
                and isinstance(action.get("enabled"), bool)
                and (
                    (action.get("enabled") and action.get("disabled_reason") is None)
                    or (
                        not action.get("enabled")
                        and isinstance(action.get("disabled_reason"), str)
                    )
                )
                and action.get("player_id") == expected_players[index]
                and isinstance(request_template, dict)
                and request_template.get("expected_state_version") == expected_versions[index]
            )
            if not valid_action:
                context.error(
                    "legal_actions",
                    artifact,
                    "LEGAL_ACTION_CONTRACT_INVALID",
                    "Legal action record is invalid.",
                    action_index=action_index,
                    checkpoint_index=index,
                )
    context.check("legal_action_checkpoints", "legal_actions", (artifact,), start)


def _find_keys(value, key_names, path="$"):
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = "%s.%s" % (path, key)
            if key in key_names:
                found.append(child_path)
            found.extend(_find_keys(child, key_names, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_find_keys(child, key_names, "%s[%s]" % (path, index)))
    return found


def _find_prohibited_keys(value):
    return sorted(_find_keys(value, _PROHIBITED_TECHNICAL_KEYS))


def _player_state(final_state, player_id):
    for player in final_state.get("players", []):
        if player.get("player_id") == player_id:
            return player
    return None


def _card_registry(final_state):
    return {
        card.get("card_instance_id"): card
        for card in final_state.get("card_instances", [])
        if isinstance(card, dict) and isinstance(card.get("card_instance_id"), str)
    }


def _validate_snapshot(snapshot, viewer_id, final_state, context):
    artifact = "snapshot_%s.json" % viewer_id
    start = len(context.errors)
    if not isinstance(snapshot, dict) or not isinstance(final_state, dict):
        return
    if (
        snapshot.get("schema_version")
        != EXPECTED_SCHEMA_MAPPING["player_visible_snapshot"]
        or snapshot.get("contract_type") != "engine_player_visible_snapshot"
        or snapshot.get("snapshot_type") != "player_visible_snapshot"
        or snapshot.get("visibility_mode") != "player"
    ):
        context.error(
            "snapshots",
            artifact,
            "SNAPSHOT_SCHEMA_INVALID",
            "Player-visible snapshot contract is invalid.",
        )
    if snapshot.get("player_id") != viewer_id:
        context.error(
            "snapshots",
            artifact,
            "SNAPSHOT_VIEWER_INVALID",
            "Snapshot viewer identity is invalid.",
            expected_viewer=viewer_id,
        )
    if snapshot.get("state_version") != 3:
        context.error(
            "snapshots",
            artifact,
            "SNAPSHOT_STATE_VERSION_INVALID",
            "Snapshot must project final state version 3.",
        )

    registry = _card_registry(final_state)
    viewer_state = _player_state(final_state, viewer_id) or {}
    opponent_id = "player_2" if viewer_id == "player_1" else "player_1"
    opponent_state = _player_state(final_state, opponent_id) or {}
    projected_players = snapshot.get("players")
    projected_by_id = {
        item.get("player_id"): item
        for item in projected_players
        if isinstance(item, dict)
    } if isinstance(projected_players, list) else {}
    viewer_projection = projected_by_id.get(viewer_id, {})
    opponent_projection = projected_by_id.get(opponent_id, {})

    own_hand_ids = viewer_state.get("hand_card_instance_ids", [])
    own_hand_cards = [registry.get(card_id, {}).get("card_id") for card_id in own_hand_ids]
    own_hand_zone = viewer_projection.get("zones", {}).get("hand", {})
    own_objects = own_hand_zone.get("objects")
    actual_own_ids = [
        item.get("card_instance_id") for item in own_objects
    ] if isinstance(own_objects, list) else []
    actual_own_cards = [
        item.get("card_id") for item in own_objects
    ] if isinstance(own_objects, list) else []
    if (
        actual_own_ids != own_hand_ids
        or actual_own_cards != own_hand_cards
        or own_hand_zone.get("redacted") is not False
        or own_hand_zone.get("visibility_mode") != "owner_visible"
    ):
        context.error(
            "snapshots",
            artifact,
            "SNAPSHOT_OWN_HAND_INVALID",
            "Viewer hand projection does not identify exactly the viewer's cards.",
        )

    opponent_hand_ids = opponent_state.get("hand_card_instance_ids", [])
    opponent_hand_cards = [
        registry.get(card_id, {}).get("card_id") for card_id in opponent_hand_ids
    ]
    opponent_hand_zone = opponent_projection.get("zones", {}).get("hand", {})
    if (
        opponent_hand_zone.get("count") != len(opponent_hand_ids)
        or opponent_hand_zone.get("objects") != []
        or opponent_hand_zone.get("redacted") is not True
        or opponent_hand_zone.get("visibility_mode") != "count_only"
        or _structured_value_present(opponent_projection, opponent_hand_ids)
        or _structured_value_present(opponent_projection, opponent_hand_cards)
    ):
        context.error(
            "snapshots",
            artifact,
            "SNAPSHOT_OPPONENT_HAND_LEAK",
            "Opponent hand must expose count only and no card identity.",
        )

    all_deck_ids = []
    all_deck_cards = []
    for player_id in ("player_1", "player_2"):
        player_state = _player_state(final_state, player_id) or {}
        ids = player_state.get("deck_card_instance_ids", [])
        all_deck_ids.extend(ids)
        all_deck_cards.extend(registry.get(card_id, {}).get("card_id") for card_id in ids)
        zone = projected_by_id.get(player_id, {}).get("zones", {}).get("deck", {})
        if (
            zone.get("count") != len(ids)
            or zone.get("objects") != []
            or zone.get("redacted") is not True
            or zone.get("visibility_mode") != "count_only"
        ):
            context.error(
                "snapshots",
                artifact,
                "SNAPSHOT_DECK_INFORMATION_LEAK",
                "Deck projection must expose count only.",
                player_id=player_id,
            )
    if _structured_value_present(snapshot, all_deck_ids) or _structured_value_present(
        snapshot, all_deck_cards
    ):
        context.error(
            "snapshots",
            artifact,
            "SNAPSHOT_DECK_INFORMATION_LEAK",
            "Snapshot exposes a deck card or instance identity.",
        )

    forbidden_paths = _find_keys(
        snapshot,
        {
            "card_instances",
            "debug_state",
            "domain_occupancies",
            "domain_topologies",
            "event_log",
            "registry",
        },
    )
    if forbidden_paths:
        context.error(
            "snapshots",
            artifact,
            "SNAPSHOT_INTERNAL_STATE_LEAK",
            "Snapshot contains internal or debug-only state.",
            paths=forbidden_paths,
        )
    prohibited = _find_prohibited_keys(snapshot)
    if prohibited:
        context.error(
            "snapshots",
            artifact,
            "SNAPSHOT_IMPLEMENTATION_METADATA_LEAK",
            "Snapshot contains implementation-specific metadata.",
            paths=prohibited,
        )

    board = snapshot.get("board")
    public_valid = (
        snapshot.get("match_id") == final_state.get("match_id")
        and snapshot.get("active_player_id") == "player_2"
        and snapshot.get("priority_player_id") == "player_2"
        and isinstance(board, dict)
        and board.get("visibility_mode") == "public"
        and board.get("schema_version") == "minimal-player-visible-domain-board-v0"
        and [item.get("player_id") for item in board.get("players", [])]
        == ["player_1", "player_2"]
    )
    for player_id in ("player_1", "player_2"):
        state_player = _player_state(final_state, player_id) or {}
        discard = projected_by_id.get(player_id, {}).get("zones", {}).get("discard", {})
        public_valid = public_valid and (
            discard.get("count") == len(state_player.get("discard_card_instance_ids", []))
            and discard.get("redacted") is False
            and discard.get("visibility_mode") == "public"
        )
    if not public_valid:
        context.error(
            "snapshots",
            artifact,
            "SNAPSHOT_PUBLIC_STATE_INVALID",
            "Snapshot public board or discard projection is invalid.",
        )
    context.check(
        "hidden_information_%s" % viewer_id,
        "snapshots",
        (artifact, "final_debug_state.json"),
        start,
    )


def _structured_value_present(value, forbidden_values):
    forbidden = {item for item in forbidden_values if isinstance(item, str)}
    if not forbidden:
        return False
    if isinstance(value, dict):
        return any(
            (isinstance(key, str) and key in forbidden)
            or _structured_value_present(child, forbidden)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_structured_value_present(child, forbidden) for child in value)
    return isinstance(value, str) and value in forbidden


def _contains_absolute_path(value):
    if isinstance(value, dict):
        return any(
            _contains_absolute_path(key) or _contains_absolute_path(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_absolute_path(child) for child in value)
    if not isinstance(value, str):
        return False
    return ntpath.isabs(value) or value.startswith("/")


def _validate_diagnostics(diagnostics, context):
    artifact = "diagnostics.json"
    start = len(context.errors)
    if not isinstance(diagnostics, dict):
        return
    contract_valid = (
        diagnostics.get("schema_version")
        == "aeterna-runtime-comparison-diagnostics-v1"
        and diagnostics.get("contract_type") == "runtime_comparison_diagnostics"
        and diagnostics.get("result") == "passed"
    )
    if not contract_valid:
        context.error(
            "diagnostics",
            artifact,
            "DIAGNOSTICS_CONTRACT_INVALID",
            "Diagnostics root contract is invalid.",
        )
    expected_passed_paths = (
        ("fixture_validation", "passed"),
        ("invariant_validation", "passed"),
        ("hidden_information_validation", "passed"),
        ("determinism_validation", "passed"),
        ("stale_immutability_validation", "passed"),
    )
    failures = []
    for section, field in expected_passed_paths:
        value = diagnostics.get(section)
        if not isinstance(value, dict) or value.get(field) is not True:
            failures.append(section)
    runner = diagnostics.get("runner_diagnostics")
    if not isinstance(runner, dict) or runner.get("blocking_error_count") != 0:
        failures.append("runner_diagnostics")
    if failures:
        context.error(
            "diagnostics",
            artifact,
            "DIAGNOSTICS_BLOCKING_FAILURE",
            "Diagnostics report contains a blocking or failed validation.",
            failed_sections=sorted(set(failures)),
        )
    prohibited = _find_prohibited_keys(diagnostics)
    if prohibited or _contains_absolute_path(diagnostics):
        context.error(
            "diagnostics",
            artifact,
            "DIAGNOSTICS_PROHIBITED_DATA",
            "Diagnostics contains prohibited technical or environment data.",
            prohibited_keys=prohibited,
        )
    context.check("diagnostics_contract", "diagnostics", (artifact,), start)


def _cross_error(context, check, message, artifacts):
    context.error(
        "cross_artifact",
        artifacts[0] if artifacts else "",
        "CROSS_ARTIFACT_CONSISTENCY_FAILED",
        message,
        check=check,
        artifacts=list(artifacts),
    )


def _validate_cross_artifact(
    parsed,
    manifest,
    entry_map,
    expected_fixture_id,
    context,
):
    start = len(context.errors)
    initial = parsed.get("initial_state.json")
    final = parsed.get("final_debug_state.json")
    requests = parsed.get("requests.jsonl")
    responses = parsed.get("responses.jsonl")
    events = parsed.get("events.jsonl")
    checkpoints = parsed.get("legal_actions.jsonl")
    snapshots = [
        parsed.get("snapshot_player_1.json"),
        parsed.get("snapshot_player_2.json"),
    ]
    diagnostics = parsed.get("diagnostics.json")

    fixture_id = manifest.get("fixture_id") if isinstance(manifest, dict) else None
    if expected_fixture_id is not None and fixture_id != expected_fixture_id:
        _cross_error(
            context,
            "expected_fixture_id",
            "Manifest fixture ID does not match the caller expectation.",
            ("run_manifest.json",),
        )
    if isinstance(diagnostics, dict):
        diagnostics_fixture = diagnostics.get("fixture_validation", {}).get("fixture_id")
        if diagnostics_fixture != fixture_id:
            _cross_error(
                context,
                "fixture_id_consistency",
                "Diagnostics and manifest fixture IDs differ.",
                ("diagnostics.json", "run_manifest.json"),
            )

    match_id = initial.get("match_id") if isinstance(initial, dict) else None
    match_values = []
    if isinstance(final, dict):
        match_values.append(("final_debug_state.json", final.get("match_id")))
    for artifact, records in (
        ("requests.jsonl", requests),
        ("responses.jsonl", responses),
    ):
        if isinstance(records, list):
            match_values.extend((artifact, record.get("match_id")) for record in records)
    if isinstance(checkpoints, list):
        for checkpoint in checkpoints:
            action_space = checkpoint.get("action_space", {})
            match_values.append(("legal_actions.jsonl", action_space.get("match_id")))
    for artifact, snapshot in zip(
        ("snapshot_player_1.json", "snapshot_player_2.json"), snapshots
    ):
        if isinstance(snapshot, dict):
            match_values.append((artifact, snapshot.get("match_id")))
    mismatched_match_artifacts = sorted(
        {artifact for artifact, value in match_values if value != match_id}
    )
    if match_id is None or mismatched_match_artifacts:
        _cross_error(
            context,
            "match_id_consistency",
            "Relevant artifacts do not share one canonical match ID.",
            tuple(["initial_state.json"] + mismatched_match_artifacts),
        )

    if isinstance(initial, dict) and isinstance(final, dict):
        if initial.get("match_id") != final.get("match_id"):
            context.error(
                "state",
                "final_debug_state.json",
                "STATE_MATCH_ID_MISMATCH",
                "Initial and final state match IDs differ.",
                initial_match_id=initial.get("match_id"),
                final_match_id=final.get("match_id"),
            )
        if initial.get("state_version") != 0 or final.get("state_version") != 3:
            _cross_error(
                context,
                "state_version_endpoints",
                "Initial and final state versions do not define the expected trajectory.",
                ("initial_state.json", "final_debug_state.json"),
            )
    if isinstance(requests, list) and isinstance(responses, list):
        request_ids = [record.get("request_id") for record in requests]
        response_ids = [record.get("request_id") for record in responses]
        if request_ids != response_ids:
            _cross_error(
                context,
                "request_response_pairing",
                "Request and response IDs do not pair in order.",
                ("requests.jsonl", "responses.jsonl"),
            )
    if isinstance(checkpoints, list):
        versions = [record.get("state_version") for record in checkpoints]
        if versions != [0, 1, 2, 3]:
            _cross_error(
                context,
                "legal_action_trajectory",
                "Legal-action checkpoint versions do not match the state trajectory.",
                ("legal_actions.jsonl",),
            )
    if isinstance(final, dict):
        for artifact, snapshot in zip(
            ("snapshot_player_1.json", "snapshot_player_2.json"), snapshots
        ):
            if isinstance(snapshot, dict) and snapshot.get("state_version") != final.get(
                "state_version"
            ):
                _cross_error(
                    context,
                    "snapshot_final_state_version",
                    "Player snapshot does not project the final state version.",
                    (artifact, "final_debug_state.json"),
                )

    mapping = manifest.get("contract_schema_mapping") if isinstance(manifest, dict) else None
    actual_mapping = {}
    if isinstance(manifest, dict):
        actual_mapping["run_manifest"] = manifest.get("schema_version")
    if isinstance(initial, dict):
        actual_mapping["canonical_match_state"] = initial.get("schema_version")
        cards = initial.get("card_instances", [])
        if cards:
            actual_mapping["card_instance"] = cards[0].get("schema_version")
    if isinstance(responses, list) and responses:
        actual_mapping["action_response"] = responses[0].get("schema_version")
    if isinstance(events, list) and events:
        actual_mapping["engine_event"] = events[0].get("schema_version")
    if isinstance(checkpoints, list) and checkpoints:
        actual_mapping["action_space"] = checkpoints[0].get("action_space", {}).get(
            "schema_version"
        )
    if isinstance(snapshots[0], dict):
        actual_mapping["player_visible_snapshot"] = snapshots[0].get("schema_version")
    if isinstance(mapping, dict):
        actual_mapping["action_request"] = "minimal-action-request-unversioned"
        actual_mapping["fixture"] = manifest.get("fixture_schema_version")
        mapping_failures = sorted(
            key for key, value in actual_mapping.items() if mapping.get(key) != value
        )
    else:
        mapping_failures = sorted(actual_mapping)
    if mapping_failures:
        _cross_error(
            context,
            "manifest_schema_mapping",
            "Manifest schema mapping does not match parsed artifact contracts.",
            ("run_manifest.json",),
        )

    if any(len(entry_map.get(path, [])) != 1 for path in CANONICAL_ARTIFACT_PATHS):
        _cross_error(
            context,
            "manifest_artifact_coverage",
            "Manifest hash list does not cover every canonical artifact exactly once.",
            ("run_manifest.json",),
        )

    if isinstance(diagnostics, dict):
        stale = diagnostics.get("stale_immutability_validation", {})
        if (
            stale.get("canonical_state_sha256_before")
            != stale.get("canonical_state_sha256_after")
            or stale.get("passed") is not True
        ):
            _cross_error(
                context,
                "stale_state_hash_consistency",
                "Stale-request canonical state hashes are inconsistent.",
                ("diagnostics.json",),
            )
        determinism = diagnostics.get("determinism_validation", {})
        if determinism.get("passed") is not True:
            _cross_error(
                context,
                "determinism_declaration",
                "Diagnostics does not confirm deterministic canonical results.",
                ("diagnostics.json",),
            )
    context.check(
        "cross_artifact_consistency",
        "cross_artifact",
        REQUIRED_ARTIFACT_PATHS,
        start,
    )


def validate_runtime_comparison_artifacts(
    artifact_directory,
    *,
    expected_fixture_id=None,
):
    """Validate an existing artifact directory without modifying or regenerating it."""

    directory = Path(artifact_directory)
    if not directory.exists():
        raise ArtifactValidatorInputError(
            "ARTIFACT_DIRECTORY_MISSING",
            "Artifact directory does not exist.",
        )
    if not directory.is_dir():
        raise ArtifactValidatorInputError(
            "ARTIFACT_DIRECTORY_NOT_DIRECTORY",
            "Artifact input is not a directory.",
        )
    if expected_fixture_id is not None and (
        not isinstance(expected_fixture_id, str) or not expected_fixture_id
    ):
        raise ArtifactValidatorInputError(
            "EXPECTED_FIXTURE_ID_INVALID",
            "expected_fixture_id must be a non-empty string when provided.",
        )

    context = _ValidationContext()
    artifact_result_map = {
        path: _artifact_result(path) for path in REQUIRED_ARTIFACT_PATHS
    }
    data = _read_inventory(directory, context, artifact_result_map)
    parsed = _parse_artifacts(data, context, artifact_result_map)
    manifest = parsed.get("run_manifest.json")
    entry_map = _validate_manifest(manifest, context) if manifest else {}
    _validate_integrity(data, entry_map, context, artifact_result_map)

    initial = parsed.get("initial_state.json")
    final = parsed.get("final_debug_state.json")
    if initial is not None:
        _validate_state(initial, "initial_state.json", context, "initial")
    if final is not None:
        _validate_state(final, "final_debug_state.json", context, "final")
    match_id = initial.get("match_id") if isinstance(initial, dict) else None
    requests = parsed.get("requests.jsonl")
    responses = parsed.get("responses.jsonl")
    events = parsed.get("events.jsonl")
    checkpoints = parsed.get("legal_actions.jsonl")
    if requests is not None:
        _validate_requests(requests, match_id, context)
    if responses is not None:
        _validate_responses(responses, requests or [], match_id, context)
    if events is not None:
        _validate_events(events, final or {}, responses or [], context)
    if checkpoints is not None:
        _validate_legal_actions(checkpoints, match_id, context)
    if final is not None:
        for player_id in ("player_1", "player_2"):
            snapshot = parsed.get("snapshot_%s.json" % player_id)
            if snapshot is not None:
                _validate_snapshot(snapshot, player_id, final, context)
    diagnostics = parsed.get("diagnostics.json")
    if diagnostics is not None:
        _validate_diagnostics(diagnostics, context)
    _validate_cross_artifact(
        parsed,
        manifest or {},
        entry_map,
        expected_fixture_id,
        context,
    )

    context.errors.sort(key=_issue_sort_key)
    context.warnings.sort(key=_issue_sort_key)
    context.semantic_checks.sort(
        key=lambda item: (
            _PHASE_RANKS[item["phase"]],
            item["check"],
            item["artifacts"],
        )
    )
    artifact_results = [
        artifact_result_map[path] for path in REQUIRED_ARTIFACT_PATHS
    ]
    summary = {
        "artifact_count_expected": len(REQUIRED_ARTIFACT_PATHS),
        "artifact_count_present": sum(item["present"] for item in artifact_results),
        "canonical_bytes_valid_count": sum(
            item["canonical_bytes_valid"] for item in artifact_results
        ),
        "error_count": len(context.errors),
        "integrity_valid_count": sum(item["integrity_valid"] for item in artifact_results),
        "semantic_check_count": len(context.semantic_checks),
        "semantic_check_failed_count": sum(
            not item["passed"] for item in context.semantic_checks
        ),
        "warning_count": len(context.warnings),
    }
    return {
        "artifact_directory_name": directory.name,
        "artifact_results": artifact_results,
        "contract_type": VALIDATION_RESULT_CONTRACT_TYPE,
        "errors": context.errors,
        "fixture_id": manifest.get("fixture_id") if isinstance(manifest, dict) else None,
        "oracle_id": manifest.get("oracle_id") if isinstance(manifest, dict) else None,
        "oracle_version": (
            manifest.get("oracle_version") if isinstance(manifest, dict) else None
        ),
        "schema_version": VALIDATION_RESULT_SCHEMA_VERSION,
        "semantic_checks": context.semantic_checks,
        "summary": summary,
        "valid": not context.errors,
        "warnings": context.warnings,
    }


def _build_argument_parser():
    parser = argparse.ArgumentParser(
        description="Validate an existing runtime-comparison artifact directory read-only."
    )
    parser.add_argument("--input", required=True, help="Artifact directory to validate.")
    parser.add_argument(
        "--expected-fixture-id",
        help="Optional fixture ID that the run manifest must declare.",
    )
    return parser


def main(argv=None):
    """Run the read-only validator CLI and return its process exit code."""

    parser = _build_argument_parser()
    try:
        arguments = parser.parse_args(argv)
        result = validate_runtime_comparison_artifacts(
            arguments.input,
            expected_fixture_id=arguments.expected_fixture_id,
        )
    except ArtifactValidatorInputError as exc:
        print("%s: %s" % (exc.code, exc.message), file=sys.stderr)
        return 2
    except (OSError, ValueError):
        print(
            "ARTIFACT_VALIDATOR_TECHNICAL_ERROR: Validation could not be completed.",
            file=sys.stderr,
        )
        return 2
    sys.stdout.write(canonical_json_bytes(result).decode("utf-8"))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ArtifactValidatorInputError",
    "CANONICAL_ARTIFACT_PATHS",
    "REQUIRED_ARTIFACT_PATHS",
    "VALIDATION_RESULT_CONTRACT_TYPE",
    "VALIDATION_RESULT_SCHEMA_VERSION",
    "main",
    "validate_runtime_comparison_artifacts",
]
