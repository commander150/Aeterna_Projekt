"""Versioned canonical runtime materialization policy."""

from __future__ import annotations

from dataclasses import dataclass


MATERIALIZER_ID = "canonical-runtime-materializer"
MATERIALIZER_CONTRACT_VERSION = "1"
MATERIALIZATION_PROFILE_ID = "runtime-package-source-compatible-v1"
MATERIALIZATION_POLICY_ID = "canonical-runtime-materialization-policy-v1"
RUNTIME_ID_DOMAIN = "aeterna-runtime-package-v1"
RUNTIME_SCHEMA_VERSION = "sample-runtime-package-v1"
RUNTIME_PACKAGE_VERSION = "0.1.0-canonical-candidate"
RUNTIME_RULESET_VERSION = "canonical-candidate"

OUTPUT_FILES = (
    "manifest.json",
    "cards.jsonl",
    "decks.jsonl",
    "lookups.json",
    "aliases.json",
    "normalization_aliases.json",
    "ability_registry.json",
    "engine_support.json",
    "diagnostics.json",
    "build_report.md",
    "provenance.json",
)

IDENTITY_PAYLOAD_FILES = tuple(
    item for item in OUTPUT_FILES if item not in {"manifest.json", "provenance.json"}
)

FORBIDDEN_INPUT_NAMES = frozenset(
    {
        "AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx",
        "LOOKUPS.xlsx",
        "cards.xlsx",
        "PRODUCT_CATALOG.xlsx",
        "DATA_REVIEW_LEDGER.xlsx",
        "CARD_NAME_REVIEWS.xlsx",
        "EXPORT_RUNTIME.jsonl",
    }
)

FORBIDDEN_OUTPUT_FRAGMENTS = (
    "MUNKAFORRÁS",
    "LOOKUPS.xlsx",
    "cards.xlsx",
    "PRODUCT_CATALOG",
    "DATA_REVIEW_LEDGER",
    "CARD_NAME_REVIEWS",
    "EXPORT_RUNTIME.jsonl",
)


@dataclass(frozen=True)
class RuntimeMappingRule:
    group: str
    source_value: str
    runtime_value: str
    canonical_value: str
    canonical_alias_id: str
    mapping_kind: str
    used_by_vs1: bool


RUNTIME_MAPPING_RULES = (
    RuntimeMappingRule("realm", "AETHER", "aether", "aether", "alias_realm_aether_legacy_uppercase", "DIRECT_EQUIVALENT", False),
    RuntimeMappingRule("realm", "AQUA", "aqua", "aqua", "alias_realm_aqua_legacy_uppercase", "DIRECT_EQUIVALENT", True),
    RuntimeMappingRule("realm", "IGNIS", "ignis", "ignis", "alias_realm_ignis_legacy_uppercase", "DIRECT_EQUIVALENT", True),
    RuntimeMappingRule("realm", "LUX", "lux", "lux", "alias_realm_lux_legacy_uppercase", "DIRECT_EQUIVALENT", False),
    RuntimeMappingRule("realm", "TERRA", "terra", "terra", "alias_realm_terra_legacy_uppercase", "DIRECT_EQUIVALENT", False),
    RuntimeMappingRule("realm", "UMBRA", "umbra", "umbra", "alias_realm_umbra_legacy_uppercase", "DIRECT_EQUIVALENT", False),
    RuntimeMappingRule("realm", "VENTUS", "ventus", "ventus", "alias_realm_ventus_legacy_uppercase", "DIRECT_EQUIVALENT", False),
    RuntimeMappingRule("card_type", "Entitás", "entity", "entity", "alias_card_type_entitas_legacy", "DIRECT_EQUIVALENT", True),
    RuntimeMappingRule("card_type", "Ige", "incantation", "spell", "alias_card_type_ige_legacy", "DETERMINISTIC_TECHNICAL_ADAPTER", True),
    RuntimeMappingRule("card_type", "Jel", "sigil", "sign", "alias_card_type_jel_legacy", "DETERMINISTIC_TECHNICAL_ADAPTER", False),
    RuntimeMappingRule("card_type", "Rituálé", "ritual", "ritual", "alias_card_type_rituale_legacy", "DIRECT_EQUIVALENT", True),
    RuntimeMappingRule("card_type", "Sík", "plane", "plane", "alias_card_type_sik_legacy", "DIRECT_EQUIVALENT", False),
)

TOKEN_ADAPTER_ALLOWLIST = frozenset(
    {
        ("card_type", "spell", "incantation"),
        ("card_type", "sign", "sigil"),
    }
)
