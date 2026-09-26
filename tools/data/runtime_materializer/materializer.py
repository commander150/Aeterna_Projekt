"""Build a deterministic RuntimePackageSource-compatible package from a verified candidate."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from tools.data.canonical_producer import verify_candidate

from .policy import (
    FORBIDDEN_INPUT_NAMES,
    FORBIDDEN_OUTPUT_FRAGMENTS,
    IDENTITY_PAYLOAD_FILES,
    MATERIALIZATION_POLICY_ID,
    MATERIALIZATION_PROFILE_ID,
    MATERIALIZER_CONTRACT_VERSION,
    MATERIALIZER_ID,
    OUTPUT_FILES,
    RUNTIME_ID_DOMAIN,
    RUNTIME_MAPPING_RULES,
    RUNTIME_PACKAGE_VERSION,
    RUNTIME_RULESET_VERSION,
    RUNTIME_SCHEMA_VERSION,
    TOKEN_ADAPTER_ALLOWLIST,
    RuntimeMappingRule,
)


class MaterializationError(RuntimeError):
    """A controlled materializer rejection with a stable diagnostic code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class BuildResult:
    candidate_id: str
    package_set_id: str
    runtime_package_id: str
    output_directory: Path
    file_count: int
    card_count: int
    deck_count: int
    lookup_mapping_count: int
    token_adapter_count: int
    materialization_valid: bool
    production_ready: bool
    publish_allowed: bool
    idempotent: bool

    def as_dict(self, repository_root: Path | None = None) -> dict[str, Any]:
        output = self.output_directory
        if repository_root is not None:
            try:
                output = output.relative_to(repository_root)
            except ValueError:
                pass
        return {
            "candidate_id": self.candidate_id,
            "package_set_id": self.package_set_id,
            "runtime_package_id": self.runtime_package_id,
            "output_directory": output.as_posix(),
            "file_count": self.file_count,
            "card_count": self.card_count,
            "deck_count": self.deck_count,
            "lookup_mapping_count": self.lookup_mapping_count,
            "token_adapter_count": self.token_adapter_count,
            "materialization_valid": self.materialization_valid,
            "production_ready": self.production_ready,
            "publish_allowed": self.publish_allowed,
            "idempotent": self.idempotent,
            "materializer_id": MATERIALIZER_ID,
            "materializer_contract_version": MATERIALIZER_CONTRACT_VERSION,
            "materialization_profile_id": MATERIALIZATION_PROFILE_ID,
            "materialization_policy_id": MATERIALIZATION_POLICY_ID,
        }


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MaterializationError("CANONICAL_INPUT_INVALID", f"Cannot read canonical JSON: {path.name}") from exc
    if not isinstance(value, dict):
        raise MaterializationError("CANONICAL_INPUT_INVALID", f"Canonical JSON root is not an object: {path.name}")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(_canonical_json_bytes(value))


def _write_jsonl(path: Path, values: Iterable[dict[str, Any]]) -> None:
    with path.open("wb") as handle:
        for value in values:
            handle.write(_canonical_json_bytes(value))


def _safe_relative(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise MaterializationError("CANONICAL_PATH_UNSAFE", f"Unsafe canonical relative path: {value}")
    return path


def _validate_candidate_input(candidate_root: Path, repository_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if candidate_root.name in FORBIDDEN_INPUT_NAMES or candidate_root.suffix.lower() == ".xlsx" or candidate_root.is_file():
        raise MaterializationError("CANDIDATE_DIRECTORY_REQUIRED", "Materializer input must be a verified candidate directory, not a source/export file.")
    if not candidate_root.is_dir():
        raise MaterializationError("CANDIDATE_NOT_FOUND", "Canonical candidate directory was not found.")
    try:
        errors = verify_candidate(candidate_root, repository_root)
    except Exception as exc:
        raise MaterializationError("CANDIDATE_VERIFICATION_FAILED", "Canonical candidate verification could not complete.") from exc
    if errors:
        raise MaterializationError("CANDIDATE_VERIFICATION_FAILED", "; ".join(errors))
    package_set = _read_json(candidate_root / "package_set.json")
    provenance = _read_json(candidate_root / "provenance.json")
    readiness = _read_json(candidate_root / "readiness.json")
    if provenance.get("candidate_id") is None or package_set.get("package_set_id") is None:
        raise MaterializationError("CANDIDATE_IDENTITY_MISSING", "Verified candidate identity is incomplete.")
    if provenance.get("package_set_id") != package_set.get("package_set_id"):
        raise MaterializationError("CANDIDATE_IDENTITY_MISMATCH", "Candidate and package-set identities disagree.")
    return package_set, provenance, readiness


def _component_root(candidate_root: Path, package_set: dict[str, Any], kind: str) -> tuple[Path, dict[str, Any]]:
    matches = [item for item in package_set.get("components", []) if item.get("component_kind") == kind]
    if len(matches) != 1:
        raise MaterializationError("CANONICAL_COMPONENT_MISSING", f"Expected exactly one {kind} component.")
    descriptor = matches[0]
    manifest_path = candidate_root / _safe_relative(str(descriptor.get("manifest_file", "")))
    return manifest_path.parent, descriptor


def _load_tables(component_root: Path, manifest_name: str) -> dict[str, list[dict[str, Any]]]:
    manifest = _read_json(component_root / manifest_name)
    tables: dict[str, list[dict[str, Any]]] = {}
    for item in manifest.get("records", []):
        if not isinstance(item, dict) or item.get("export_enabled") is not True:
            continue
        table_id = item.get("table_id")
        export_file = item.get("export_file")
        if not isinstance(table_id, str) or not isinstance(export_file, str):
            raise MaterializationError("CANONICAL_MANIFEST_INVALID", "Enabled canonical table has no file binding.")
        payload = _read_json(component_root / _safe_relative(export_file))
        if payload.get("table_id") != table_id or not isinstance(payload.get("records"), list):
            raise MaterializationError("CANONICAL_TABLE_INVALID", f"Canonical table binding is invalid: {table_id}")
        records = payload["records"]
        if not all(isinstance(record, dict) for record in records):
            raise MaterializationError("CANONICAL_TABLE_INVALID", f"Canonical table contains a non-object: {table_id}")
        tables[table_id] = records
    return tables


def _require_table(tables: dict[str, list[dict[str, Any]]], table_id: str) -> list[dict[str, Any]]:
    if table_id not in tables:
        raise MaterializationError("CANONICAL_TABLE_MISSING", f"Required canonical table is missing: {table_id}")
    return tables[table_id]


def _runtime_value_for(group: str, canonical_value: str, requested_runtime_value: str | None = None) -> str:
    if requested_runtime_value is None or requested_runtime_value == canonical_value:
        return canonical_value
    if (group, canonical_value, requested_runtime_value) not in TOKEN_ADAPTER_ALLOWLIST:
        raise MaterializationError(
            "RUNTIME_MAPPING_DECISION_REQUIRED",
            f"Unsupported semantic mapping is not allowlisted: {group}:{canonical_value}->{requested_runtime_value}",
        )
    return requested_runtime_value


def _verify_mapping_policy(registry_tables: dict[str, list[dict[str, Any]]]) -> tuple[RuntimeMappingRule, ...]:
    if len(RUNTIME_MAPPING_RULES) != 12:
        raise MaterializationError("RUNTIME_MAPPING_SUBSET_INVALID", "Runtime-required mapping subset must contain exactly 12 rows.")
    adapters = [rule for rule in RUNTIME_MAPPING_RULES if rule.mapping_kind == "DETERMINISTIC_TECHNICAL_ADAPTER"]
    if len(adapters) != 2:
        raise MaterializationError("RUNTIME_MAPPING_SUBSET_INVALID", "Runtime-required mapping subset must contain exactly two token adapters.")
    values = {item.get("registry_value_id"): item for item in _require_table(registry_tables, "value_registry")}
    aliases = {item.get("alias_id"): item for item in _require_table(registry_tables, "aliases")}
    seen: set[tuple[str, str]] = set()
    for rule in RUNTIME_MAPPING_RULES:
        if (rule.group, rule.source_value) in seen:
            raise MaterializationError("RUNTIME_MAPPING_SUBSET_INVALID", "Runtime mapping subset contains a duplicate source mapping.")
        seen.add((rule.group, rule.source_value))
        alias = aliases.get(rule.canonical_alias_id)
        if not alias or alias.get("status") != "active" or alias.get("group_id") != rule.group or alias.get("alias_value") != rule.source_value:
            raise MaterializationError("RUNTIME_MAPPING_CANONICAL_MISMATCH", f"Canonical alias does not prove mapping: {rule.canonical_alias_id}")
        value = values.get(alias.get("canonical_registry_value_id"))
        if not value or value.get("group_id") != rule.group or value.get("value_id") != rule.canonical_value:
            raise MaterializationError("RUNTIME_MAPPING_CANONICAL_MISMATCH", f"Canonical value does not prove mapping: {rule.canonical_alias_id}")
        if value.get("runtime_enabled") is not True or value.get("lifecycle_status") != "active":
            raise MaterializationError("RUNTIME_MAPPING_CANONICAL_MISMATCH", f"Canonical runtime value is not active: {rule.canonical_alias_id}")
        actual = _runtime_value_for(rule.group, rule.canonical_value, rule.runtime_value)
        if actual != rule.runtime_value:
            raise MaterializationError("RUNTIME_MAPPING_SUBSET_INVALID", "Runtime mapping adapter result is inconsistent.")
        if rule.mapping_kind == "DETERMINISTIC_TECHNICAL_ADAPTER" and (rule.group, rule.canonical_value, rule.runtime_value) not in TOKEN_ADAPTER_ALLOWLIST:
            raise MaterializationError("RUNTIME_MAPPING_DECISION_REQUIRED", "Token adapter is not explicitly allowlisted.")
        if rule.mapping_kind != "DETERMINISTIC_TECHNICAL_ADAPTER" and rule.runtime_value != rule.canonical_value:
            raise MaterializationError("RUNTIME_MAPPING_DECISION_REQUIRED", "Non-adapter mapping changes canonical semantics.")
    return RUNTIME_MAPPING_RULES


def _mapping_index(rules: Iterable[RuntimeMappingRule]) -> dict[tuple[str, str], str]:
    return {(rule.group, rule.canonical_value): rule.runtime_value for rule in rules}


def _materialize_cards(
    card_tables: dict[str, list[dict[str, Any]]],
    mappings: dict[tuple[str, str], str],
) -> list[dict[str, Any]]:
    localizations: dict[str, dict[str, Any]] = {}
    for item in _require_table(card_tables, "card_localization"):
        if item.get("language") == "hu" and item.get("status") == "active":
            card_id = item.get("card_id")
            if not isinstance(card_id, str) or card_id in localizations:
                raise MaterializationError("CARD_LOCALIZATION_INVALID", "Hungarian card localization is missing or duplicate.")
            localizations[card_id] = item
    abilities_by_card: dict[str, list[str]] = defaultdict(list)
    for ability in _require_table(card_tables, "abilities"):
        if ability.get("status") == "active":
            abilities_by_card[str(ability.get("card_id"))].append(str(ability.get("ability_id")))
    cards: list[dict[str, Any]] = []
    for source in _require_table(card_tables, "cards"):
        if source.get("status") != "active":
            continue
        card_id = source.get("card_id")
        card_type = source.get("card_type_id")
        realm = source.get("realm_id")
        if not isinstance(card_id, str) or not isinstance(card_type, str) or not isinstance(realm, str):
            raise MaterializationError("CARD_FIELD_INVALID", "Canonical card identity/type/realm is invalid.")
        try:
            runtime_card_type = mappings[("card_type", card_type)]
            runtime_realm = mappings[("realm", realm)]
        except KeyError as exc:
            raise MaterializationError("RUNTIME_MAPPING_DECISION_REQUIRED", f"No audited runtime mapping exists for card {card_id}.") from exc
        magnitude = source.get("magnitude")
        aura_cost = source.get("aura_cost")
        if not isinstance(magnitude, int) or magnitude < 0 or not isinstance(aura_cost, int) or aura_cost < 0:
            raise MaterializationError("CARD_FIELD_INVALID", f"Card has invalid magnitude/aura cost: {card_id}")
        localization = localizations.get(card_id)
        if localization is None:
            raise MaterializationError("CARD_LOCALIZATION_MISSING", f"Active Hungarian localization is missing: {card_id}")
        cards.append(
            {
                "ability_ids": sorted(abilities_by_card.get(card_id, [])),
                "atk": source.get("atk"),
                "aura_cost": aura_cost,
                "canonical_card_type": card_type,
                "card_id": card_id,
                "card_type": runtime_card_type,
                "class_id": source.get("class_id"),
                "clan_id": source.get("clan_id"),
                "diagnostics": [],
                "engine_support_status": source.get("engine_support_status"),
                "hp": source.get("hp"),
                "magnitude": magnitude,
                "name_hu": localization.get("card_name"),
                "race_id": source.get("race_id"),
                "realm": runtime_realm,
                "rules_text_hu": localization.get("rules_text"),
                "runtime_status": "canonical_materialized",
                "status": "active",
            }
        )
    cards.sort(key=lambda item: item["card_id"])
    return cards


def _materialize_decks(
    card_tables: dict[str, list[dict[str, Any]]],
    card_ids: set[str],
    mappings: dict[tuple[str, str], str],
) -> list[dict[str, Any]]:
    entries: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in _require_table(card_tables, "deck_entries"):
        if item.get("status") == "active":
            entries[str(item.get("deck_id"))].append(item)
    decks: list[dict[str, Any]] = []
    for source in _require_table(card_tables, "decks"):
        if source.get("status") != "active":
            continue
        deck_id = source.get("deck_id")
        realm = source.get("realm_id")
        if not isinstance(deck_id, str) or not isinstance(realm, str) or ("realm", realm) not in mappings:
            raise MaterializationError("DECK_FIELD_INVALID", "Canonical deck identity or realm is invalid.")
        ordered = sorted(entries.get(deck_id, []), key=lambda item: item.get("entry_index", 0))
        card_entries: list[dict[str, Any]] = []
        for item in ordered:
            card_id = item.get("card_id")
            quantity = item.get("quantity")
            if card_id not in card_ids or not isinstance(quantity, int) or quantity <= 0:
                raise MaterializationError("DECK_CARD_REFERENCE_INVALID", f"Canonical deck contains an invalid card reference: {deck_id}")
            card_entries.append({"card_id": card_id, "count": quantity})
        card_count = sum(item["count"] for item in card_entries)
        if card_count != source.get("required_card_count"):
            raise MaterializationError("DECK_CARD_COUNT_INVALID", f"Canonical deck count is invalid: {deck_id}")
        decks.append(
            {
                "card_count": card_count,
                "card_entries": card_entries,
                "deck_id": deck_id,
                "deck_type": "canonical_vs1",
                "diagnostics": [],
                "name_hu": source.get("internal_name"),
                "primary_clan_id": source.get("primary_clan_id"),
                "profile_id": "vs1",
                "realm": mappings[("realm", realm)],
                "secondary_clan_id": source.get("secondary_clan_id"),
                "status": "active",
                "valid": True,
            }
        )
    decks.sort(key=lambda item: item["deck_id"])
    return decks


def _materialize_lookups(rules: Iterable[RuntimeMappingRule]) -> list[dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for rule in rules:
        for value in (rule.runtime_value, rule.canonical_value, rule.source_value):
            key = (rule.group, value)
            row = {
                "canonical_value": rule.runtime_value,
                "label_hu": rule.source_value,
                "lookup_group": rule.group,
                "status": "active",
                "used_for": ["runtime_validation"],
                "value": value,
            }
            existing = rows.get(key)
            if existing is not None and existing["canonical_value"] != rule.runtime_value:
                raise MaterializationError("RUNTIME_LOOKUP_CONFLICT", f"Runtime lookup alias conflict: {rule.group}:{value}")
            rows[key] = row
    return [rows[key] for key in sorted(rows)]


def _materialize_aliases(
    registry_tables: dict[str, list[dict[str, Any]]],
    mappings: dict[tuple[str, str], str],
) -> list[dict[str, Any]]:
    values = {item.get("registry_value_id"): item for item in _require_table(registry_tables, "value_registry")}
    result: list[dict[str, Any]] = []
    for source in _require_table(registry_tables, "aliases"):
        if source.get("status") != "active":
            continue
        target = values.get(source.get("canonical_registry_value_id"))
        if target is None:
            raise MaterializationError("ALIAS_TARGET_MISSING", f"Canonical alias target is missing: {source.get('alias_id')}")
        group = target.get("group_id")
        canonical_value = target.get("value_id")
        if not isinstance(group, str) or not isinstance(canonical_value, str):
            raise MaterializationError("ALIAS_TARGET_INVALID", f"Canonical alias target is invalid: {source.get('alias_id')}")
        runtime_value = mappings.get((group, canonical_value), canonical_value)
        result.append(
            {
                "alias_id": source.get("alias_id"),
                "alias_type": source.get("alias_type"),
                "alias_value": source.get("alias_value"),
                "canonical_registry_value_id": source.get("canonical_registry_value_id"),
                "canonical_value": runtime_value,
                "case_sensitive": bool(source.get("case_sensitive", False)),
                "group_id": group,
                "normalization_mode": source.get("normalization_mode"),
                "requires_audit": bool(source.get("requires_audit", False)),
                "status": "active",
            }
        )
    result.sort(key=lambda item: item["alias_id"])
    return result


def _runtime_graph_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.items()
        if key not in {"source_id", "source_ref", "notes"}
    }


def _materialize_abilities(
    card_tables: dict[str, list[dict[str, Any]]],
    registry_tables: dict[str, list[dict[str, Any]]],
    card_ids: set[str],
) -> dict[str, Any]:
    templates = {item.get("ability_template_id") for item in _require_table(registry_tables, "ability_templates")}
    modules: list[dict[str, Any]] = []
    for source in _require_table(card_tables, "abilities"):
        if source.get("status") != "active":
            continue
        ability_id = source.get("ability_id")
        card_id = source.get("card_id")
        template_id = source.get("ability_template_id")
        if not isinstance(ability_id, str) or card_id not in card_ids:
            raise MaterializationError("ABILITY_REFERENCE_INVALID", f"Canonical ability has an invalid card reference: {ability_id}")
        if template_id is not None and template_id not in templates:
            raise MaterializationError("ABILITY_TEMPLATE_MISSING", f"Canonical ability template is missing: {template_id}")
        modules.append(
            {
                "ability_id": ability_id,
                "ability_index": source.get("ability_index"),
                "ability_template_id": template_id,
                "canonical_engine_support_status": source.get("engine_support_status"),
                "card_id": card_id,
                "diagnostics": [],
                "execution_mode": "canonical_runtime_binding_required",
                "implementation_mode_id": source.get("implementation_mode_id"),
                "manual_review_required": True,
                "module_id": ability_id,
                "module_type": "canonical_ability",
                "support_status": "not_checked",
            }
        )
    modules.sort(key=lambda item: item["module_id"])
    graph_table_ids = sorted(
        table_id
        for table_id in card_tables
        if table_id == "abilities" or table_id.startswith("ability_") or table_id == "effect_tags"
    )
    graph = {
        table_id: [_runtime_graph_record(record) for record in card_tables[table_id]]
        for table_id in graph_table_ids
    }
    return {
        "ability_registry": modules,
        "canonical_graph": graph,
        "execution_authority": "CanonicalRuntimeSource",
        "schema_version": RUNTIME_SCHEMA_VERSION,
    }


def _validate_unique_and_refs(cards: list[dict[str, Any]], decks: list[dict[str, Any]], abilities: list[dict[str, Any]]) -> None:
    card_ids = [item.get("card_id") for item in cards]
    if any(not isinstance(item, str) or not item for item in card_ids) or len(card_ids) != len(set(card_ids)):
        raise MaterializationError("DUPLICATE_CARD_ID", "Runtime cards contain missing or duplicate card IDs.")
    deck_ids = [item.get("deck_id") for item in decks]
    if any(not isinstance(item, str) or not item for item in deck_ids) or len(deck_ids) != len(set(deck_ids)):
        raise MaterializationError("DUPLICATE_DECK_ID", "Runtime decks contain missing or duplicate deck IDs.")
    known_cards = set(card_ids)
    for deck in decks:
        for entry in deck.get("card_entries", []):
            if entry.get("card_id") not in known_cards or not isinstance(entry.get("count"), int) or entry["count"] <= 0:
                raise MaterializationError("BROKEN_DECK_CARD_FK", f"Runtime deck has an invalid card reference: {deck.get('deck_id')}")
    ability_ids = [item.get("module_id") for item in abilities]
    if len(ability_ids) != len(set(ability_ids)):
        raise MaterializationError("DUPLICATE_ABILITY_ID", "Runtime ability registry contains duplicate module IDs.")
    for ability in abilities:
        if ability.get("card_id") not in known_cards:
            raise MaterializationError("BROKEN_ABILITY_CARD_FK", f"Runtime ability has an invalid card reference: {ability.get('module_id')}")


def _normalize_blockers(blockers: Any, source: str) -> list[dict[str, Any]]:
    if not isinstance(blockers, list) or any(not isinstance(item, Mapping) for item in blockers):
        raise MaterializationError("READINESS_BLOCKERS_INVALID", f"{source} blockers must be a list of objects.")
    normalized: list[dict[str, Any]] = []
    for item in blockers:
        if not all(isinstance(item.get(field), str) and item.get(field) for field in ("id", "status", "summary")):
            raise MaterializationError(
                "READINESS_BLOCKERS_INVALID",
                f"{source} blocker identity, status, or summary is invalid.",
            )
        normalized.append(dict(item))
    return sorted(normalized, key=lambda item: str(item["id"]))


def _derive_readiness(
    candidate_readiness: Mapping[str, Any],
    *,
    materialization_valid: bool,
    materializer_blockers: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    candidate_production_ready = candidate_readiness.get("production_ready")
    candidate_publish_allowed = candidate_readiness.get("publish_allowed")
    if not isinstance(candidate_production_ready, bool) or not isinstance(candidate_publish_allowed, bool):
        raise MaterializationError("CANDIDATE_READINESS_INVALID", "Candidate readiness flags must be booleans.")
    candidate_blockers = _normalize_blockers(candidate_readiness.get("blockers"), "Candidate readiness")
    local_blockers = _normalize_blockers(materializer_blockers or [], "Materializer")
    production_blocked = any(bool(item.get("blocks_production", True)) for item in local_blockers)
    publish_blocked = any(bool(item.get("blocks_publish", True)) for item in local_blockers)
    return {
        "authority": "canonical_candidate_readiness",
        "blockers": candidate_blockers + local_blockers,
        "candidate_production_ready": candidate_production_ready,
        "candidate_publish_allowed": candidate_publish_allowed,
        "materialization_valid": materialization_valid,
        "production_ready": candidate_production_ready and materialization_valid and not production_blocked,
        "publish_allowed": candidate_publish_allowed and materialization_valid and not publish_blocked,
    }


def _candidate_blocker_diagnostics(blockers: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    for blocker in blockers:
        blocker_id = str(blocker["id"])
        code_id = "_".join(part for part in re.split(r"[^A-Za-z0-9]+", blocker_id.upper()) if part)
        diagnostics.append(
            {
                "blocking": False,
                "category": "candidate_readiness",
                "code": f"CANDIDATE_{code_id}_BLOCKER",
                "human_review_required": True,
                "message_hu": str(blocker["summary"]),
                "production_blocking": blocker.get("impact") == "BLOCKING_FOR_PRODUCTION_PARITY",
                "severity": "warning",
                "source": "canonical_candidate_readiness",
                "source_blocker": dict(blocker),
            }
        )
    return diagnostics


def compute_runtime_package_id(
    candidate_id: str,
    package_set_id: str,
    payload_file_hashes: dict[str, str],
) -> str:
    preimage = {
        "candidate_id": candidate_id,
        "domain": RUNTIME_ID_DOMAIN,
        "materialization_policy_id": MATERIALIZATION_POLICY_ID,
        "materialization_profile_id": MATERIALIZATION_PROFILE_ID,
        "materializer_contract_version": MATERIALIZER_CONTRACT_VERSION,
        "materializer_id": MATERIALIZER_ID,
        "package_set_id": package_set_id,
        "payload_file_hashes": dict(sorted(payload_file_hashes.items())),
    }
    return _sha256_bytes(_canonical_json_bytes(preimage))


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _validate_output_location(output_root: Path, repository_root: Path) -> Path:
    resolved = output_root.resolve()
    temp_root = (repository_root / "TEMP").resolve()
    try:
        resolved.relative_to(temp_root)
    except ValueError as exc:
        raise MaterializationError("OUTPUT_PATH_FORBIDDEN", "Runtime materialization output must remain under repository TEMP/.") from exc
    forbidden = [
        (repository_root / "Aeterna game engine" / "Godot" / "runtime_package").resolve(),
        (repository_root / "game" / "data").resolve(),
    ]
    if any(resolved == item or item in resolved.parents for item in forbidden):
        raise MaterializationError(
            "OUTPUT_PATH_FORBIDDEN",
            "Runtime materializer output must not target consumer publish paths.",
        )
    return resolved


def _assert_no_forbidden_output(root: Path) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if any(fragment.casefold() in text.casefold() for fragment in FORBIDDEN_OUTPUT_FRAGMENTS):
            raise MaterializationError("LEGACY_SOURCE_REFERENCE_FORBIDDEN", f"Legacy source reference leaked into runtime output: {path.name}")
        if re_contains_absolute_path(text):
            raise MaterializationError("ABSOLUTE_PATH_FORBIDDEN", f"Absolute path leaked into runtime output: {path.name}")


def re_contains_absolute_path(text: str) -> bool:
    normalized = text.replace("\\\\", "\\")
    if any(f"{letter}:\\" in normalized for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"):
        return True
    return '"/' in text and any(marker in text for marker in ('"/home/', '"/Users/', '"/tmp/', '"/var/'))


def validate_runtime_package(package_root: Path | str) -> tuple[str, ...]:
    root = Path(package_root)
    errors: list[str] = []
    if not root.is_dir():
        return ("runtime package directory is missing",)
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    if actual_files != set(OUTPUT_FILES):
        errors.append(f"runtime file set mismatch: {sorted(actual_files ^ set(OUTPUT_FILES))}")
        return tuple(errors)
    try:
        manifest = _read_json(root / "manifest.json")
        provenance = _read_json(root / "provenance.json")
        cards = [json.loads(line) for line in (root / "cards.jsonl").read_text(encoding="utf-8").splitlines() if line]
        decks = [json.loads(line) for line in (root / "decks.jsonl").read_text(encoding="utf-8").splitlines() if line]
        lookups = _read_json(root / "lookups.json").get("lookups", [])
        ability_payload = _read_json(root / "ability_registry.json")
        aliases = _read_json(root / "aliases.json").get("aliases", [])
        diagnostics = _read_json(root / "diagnostics.json").get("diagnostics", [])
    except (MaterializationError, OSError, json.JSONDecodeError) as exc:
        return (f"runtime package parse failed: {exc}",)
    if manifest.get("package_id") != manifest.get("runtime_package_id"):
        errors.append("manifest package_id/runtime_package_id mismatch")
    if provenance.get("runtime_package_id") != manifest.get("runtime_package_id"):
        errors.append("manifest/provenance runtime_package_id mismatch")
    file_hashes = provenance.get("file_hashes", {})
    for relative, expected in file_hashes.items():
        path = root / _safe_relative(relative)
        if not path.is_file() or _sha256_file(path) != expected:
            errors.append(f"file hash mismatch: {relative}")
    payload_hashes = provenance.get("identity_payload_file_hashes", {})
    if set(payload_hashes) != set(IDENTITY_PAYLOAD_FILES):
        errors.append("identity payload file set mismatch")
    else:
        expected_id = compute_runtime_package_id(
            str(provenance.get("candidate_id")),
            str(provenance.get("package_set_id")),
            payload_hashes,
        )
        if expected_id != provenance.get("runtime_package_id"):
            errors.append("runtime_package_id verification failed")
    try:
        _validate_unique_and_refs(cards, decks, ability_payload.get("ability_registry", []))
    except MaterializationError as exc:
        errors.append(f"{exc.code}: {exc}")
    lookup_aliases = {
        (item.get("lookup_group"), item.get("value")): item.get("canonical_value")
        for item in lookups
        if isinstance(item, dict) and item.get("status") == "active"
    }
    for card in cards:
        for group, field in (("realm", "realm"), ("card_type", "card_type")):
            if (group, card.get(field)) not in lookup_aliases:
                errors.append(f"card lookup does not resolve: {card.get('card_id')}:{field}")
    if len({(item.get("lookup_group"), item.get("value")) for item in lookups}) != len(lookups):
        errors.append("duplicate lookup alias")
    if any(not isinstance(item, dict) or not item.get("alias_id") or not item.get("canonical_value") for item in aliases):
        errors.append("alias record does not resolve")
    if not isinstance(diagnostics, list) or any(
        not isinstance(item, dict)
        or not isinstance(item.get("code"), str)
        or item.get("severity") not in {"warning", "error", "audit_note"}
        or not isinstance(item.get("blocking"), bool)
        for item in diagnostics
    ):
        errors.append("diagnostics format is invalid")
    try:
        _assert_no_forbidden_output(root)
    except MaterializationError as exc:
        errors.append(f"{exc.code}: {exc}")
    return tuple(sorted(set(errors)))


def materialize(
    candidate_root: Path | str,
    output_root: Path | str = "TEMP/runtime_materialization",
    repository_root: Path | str | None = None,
) -> BuildResult:
    root = Path(repository_root).resolve() if repository_root is not None else _repository_root().resolve()
    candidate = Path(candidate_root)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    destination_root = Path(output_root)
    if not destination_root.is_absolute():
        destination_root = root / destination_root
    destination_root = _validate_output_location(destination_root, root)
    package_set, candidate_provenance, candidate_readiness = _validate_candidate_input(candidate, root)
    card_root, card_descriptor = _component_root(candidate, package_set, "CARDDATABASE")
    registry_root, registry_descriptor = _component_root(candidate, package_set, "REGISTRY")
    card_tables = _load_tables(card_root, Path(str(card_descriptor["manifest_file"])).name)
    registry_tables = _load_tables(registry_root, Path(str(registry_descriptor["manifest_file"])).name)
    rules = _verify_mapping_policy(registry_tables)
    mappings = _mapping_index(rules)
    cards = _materialize_cards(card_tables, mappings)
    card_ids = {item["card_id"] for item in cards}
    decks = _materialize_decks(card_tables, card_ids, mappings)
    lookups = _materialize_lookups(rules)
    aliases = _materialize_aliases(registry_tables, mappings)
    ability_payload = _materialize_abilities(card_tables, registry_tables, card_ids)
    _validate_unique_and_refs(cards, decks, ability_payload["ability_registry"])

    readiness = _derive_readiness(candidate_readiness, materialization_valid=True)
    diagnostics = _candidate_blocker_diagnostics(readiness["blockers"])
    card_statuses = dict(sorted(Counter(str(item.get("engine_support_status")) for item in cards).items()))
    ability_statuses = dict(sorted(Counter(str(item.get("canonical_engine_support_status")) for item in ability_payload["ability_registry"]).items()))
    engine_support = {
        "ability_execution": "canonical_runtime_binding_required",
        "ability_support_summary": {
            "canonical_statuses": ability_statuses,
            "not_checked": len(ability_payload["ability_registry"]),
        },
        "schema_version": RUNTIME_SCHEMA_VERSION,
        "summary": {
            "ability_module_statuses": {"not_checked": len(ability_payload["ability_registry"])},
            "card_statuses": card_statuses,
            "runtime_executes_abilities": False,
            "canonical_runtime_binding_required": True,
        },
        "supported_card_types": [],
        "supported_realms": [],
    }
    engine_support["supported_card_types"] = sorted({rule.runtime_value for rule in rules if rule.group == "card_type"})
    engine_support["supported_realms"] = sorted({rule.runtime_value for rule in rules if rule.group == "realm"})
    normalization_aliases = {
        "normalization_aliases": [
            {
                **item,
                "normalization_allowed": not item["requires_audit"],
            }
            for item in aliases
        ],
        "schema_version": RUNTIME_SCHEMA_VERSION,
    }
    build_report = "\n".join(
        [
            "# AETERNA canonical runtime materialization report",
            "",
            f"- cards: {len(cards)}",
            f"- decks: {len(decks)}",
            f"- lookup mappings: {len(rules)}",
            f"- explicit token adapters: {len(TOKEN_ADAPTER_ALLOWLIST)}",
            f"- canonical abilities: {len(ability_payload['ability_registry'])}",
            "- materialization_valid: true",
            f"- production_ready: {str(readiness['production_ready']).lower()}",
            f"- publish_allowed: {str(readiness['publish_allowed']).lower()}",
            "- consumer cutover: not performed",
            "",
            "The package was derived only from a verified canonical candidate.",
            "Candidate readiness blockers are propagated to diagnostics and provenance.",
            "",
        ]
    )

    destination_root.mkdir(parents=True, exist_ok=True)
    staging = destination_root / f".runtime-materialization-{uuid.uuid4().hex}"
    staging.mkdir()
    try:
        _write_jsonl(staging / "cards.jsonl", cards)
        _write_jsonl(staging / "decks.jsonl", decks)
        _write_json(staging / "lookups.json", {"lookups": lookups, "schema_version": RUNTIME_SCHEMA_VERSION})
        _write_json(staging / "aliases.json", {"aliases": aliases, "schema_version": RUNTIME_SCHEMA_VERSION})
        _write_json(staging / "normalization_aliases.json", normalization_aliases)
        _write_json(staging / "ability_registry.json", ability_payload)
        _write_json(staging / "engine_support.json", engine_support)
        _write_json(staging / "diagnostics.json", {"diagnostics": diagnostics, "schema_version": RUNTIME_SCHEMA_VERSION})
        (staging / "build_report.md").write_text(build_report, encoding="utf-8", newline="\n")
        payload_hashes = {name: _sha256_file(staging / name) for name in IDENTITY_PAYLOAD_FILES}
        candidate_id = str(candidate_provenance["candidate_id"])
        package_set_id = str(package_set["package_set_id"])
        runtime_package_id = compute_runtime_package_id(candidate_id, package_set_id, payload_hashes)
        manifest = {
            "build_profile": MATERIALIZATION_PROFILE_ID,
            "compatibility": {
                "canonical_binding_required_for_structured_abilities": True,
                "consumer_contract": "RuntimePackageSource",
                "runtime_lookup_mapping_count": len(rules),
                "token_adapter_count": len(TOKEN_ADAPTER_ALLOWLIST),
            },
            "engine_support_summary": engine_support["summary"],
            "files": [
                {"format": name.rsplit(".", 1)[-1], "path": name}
                for name in OUTPUT_FILES
            ],
            "identity_payload_file_hashes": payload_hashes,
            "metadata": {
                "generator": MATERIALIZER_ID,
                "materialization_policy_id": MATERIALIZATION_POLICY_ID,
                "production_export": False,
            },
            "package_id": runtime_package_id,
            "package_version": RUNTIME_PACKAGE_VERSION,
            "readiness": readiness,
            "ruleset_version": RUNTIME_RULESET_VERSION,
            "runtime_package_id": runtime_package_id,
            "schema_version": RUNTIME_SCHEMA_VERSION,
            "source_components": [
                {"component_identity": card_descriptor["component_identity"], "component_kind": "CARDDATABASE"},
                {"component_identity": registry_descriptor["component_identity"], "component_kind": "REGISTRY"},
            ],
            "source_identity": {"candidate_id": candidate_id, "package_set_id": package_set_id},
            "validation_summary": {
                "blocking": False,
                "card_count": len(cards),
                "deck_count": len(decks),
                "diagnostic_count": len(diagnostics),
                "error_count": 0,
                "materialization_valid": True,
                "warning_count": len(diagnostics),
            },
        }
        _write_json(staging / "manifest.json", manifest)
        all_hashes = dict(payload_hashes)
        all_hashes["manifest.json"] = _sha256_file(staging / "manifest.json")
        provenance = {
            "candidate_id": candidate_id,
            "candidate_verifier": {"errors": [], "result": "PASS"},
            "file_hash_scope": "all package files except self-referential provenance.json",
            "file_hashes": dict(sorted(all_hashes.items())),
            "identity_payload_file_hashes": dict(sorted(payload_hashes.items())),
            "materialization_policy_id": MATERIALIZATION_POLICY_ID,
            "materialization_profile_id": MATERIALIZATION_PROFILE_ID,
            "materializer": {"contract_version": MATERIALIZER_CONTRACT_VERSION, "id": MATERIALIZER_ID},
            "package_set_id": package_set_id,
            "read_audit": {
                "candidate_only": True,
                "external_source_file_read_count": 0,
                "legacy_source_read_count": 0,
            },
            "readiness": readiness,
            "runtime_identity_domain": RUNTIME_ID_DOMAIN,
            "runtime_package_id": runtime_package_id,
            "source_components": {
                "CARDDATABASE": {
                    "component_identity": card_descriptor["component_identity"],
                    "content_hash": card_descriptor["content_hash"],
                },
                "REGISTRY": {
                    "component_identity": registry_descriptor["component_identity"],
                    "content_hash": registry_descriptor["content_hash"],
                },
            },
        }
        _write_json(staging / "provenance.json", provenance)
        _assert_no_forbidden_output(staging)
        errors = validate_runtime_package(staging)
        if errors:
            raise MaterializationError("RUNTIME_PACKAGE_VALIDATION_FAILED", "; ".join(errors))
        target = destination_root / runtime_package_id.removeprefix("sha256:")
        idempotent = target.exists()
        if idempotent:
            if _tree_hashes(staging) != _tree_hashes(target):
                raise MaterializationError("RUNTIME_PACKAGE_ID_COLLISION", "Existing runtime package bytes do not match deterministic output.")
            shutil.rmtree(staging)
        else:
            staging.replace(target)
        return BuildResult(
            candidate_id=candidate_id,
            package_set_id=package_set_id,
            runtime_package_id=runtime_package_id,
            output_directory=target,
            file_count=len(OUTPUT_FILES),
            card_count=len(cards),
            deck_count=len(decks),
            lookup_mapping_count=len(rules),
            token_adapter_count=len(TOKEN_ADAPTER_ALLOWLIST),
            materialization_valid=True,
            production_ready=readiness["production_ready"],
            publish_allowed=readiness["publish_allowed"],
            idempotent=idempotent,
        )
    except Exception:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise
