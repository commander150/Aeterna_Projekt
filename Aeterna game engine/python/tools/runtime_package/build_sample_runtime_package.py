"""Build a small AETERNA sample runtime package.

This script intentionally uses controlled in-code fixture data. It proves the
runtime package shape without reading production exports or running card logic.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from importlib import util
from pathlib import Path


try:
    from runtime_cards_builder_adapter import load_builder_cards_from_export_runtime_jsonl
except ModuleNotFoundError:
    adapter_path = Path(__file__).resolve().with_name("runtime_cards_builder_adapter.py")
    spec = util.spec_from_file_location("runtime_cards_builder_adapter", adapter_path)
    runtime_cards_builder_adapter = util.module_from_spec(spec)
    spec.loader.exec_module(runtime_cards_builder_adapter)
    load_builder_cards_from_export_runtime_jsonl = (
        runtime_cards_builder_adapter.load_builder_cards_from_export_runtime_jsonl
    )

try:
    from runtime_decks_builder_adapter import load_builder_decks_from_product_decklists_jsonl
except ModuleNotFoundError:
    adapter_path = Path(__file__).resolve().with_name("runtime_decks_builder_adapter.py")
    spec = util.spec_from_file_location("runtime_decks_builder_adapter", adapter_path)
    runtime_decks_builder_adapter = util.module_from_spec(spec)
    spec.loader.exec_module(runtime_decks_builder_adapter)
    load_builder_decks_from_product_decklists_jsonl = (
        runtime_decks_builder_adapter.load_builder_decks_from_product_decklists_jsonl
    )

try:
    from runtime_lookups_builder_adapter import load_builder_lookups_from_runtime_lookups_jsonl
except ModuleNotFoundError:
    adapter_path = Path(__file__).resolve().with_name("runtime_lookups_builder_adapter.py")
    spec = util.spec_from_file_location("runtime_lookups_builder_adapter", adapter_path)
    runtime_lookups_builder_adapter = util.module_from_spec(spec)
    spec.loader.exec_module(runtime_lookups_builder_adapter)
    load_builder_lookups_from_runtime_lookups_jsonl = (
        runtime_lookups_builder_adapter.load_builder_lookups_from_runtime_lookups_jsonl
    )

try:
    from normalization_audit_report import build_normalization_audit_report
except ModuleNotFoundError:
    adapter_path = Path(__file__).resolve().with_name("normalization_audit_report.py")
    spec = util.spec_from_file_location("normalization_audit_report", adapter_path)
    normalization_audit_report = util.module_from_spec(spec)
    spec.loader.exec_module(normalization_audit_report)
    build_normalization_audit_report = normalization_audit_report.build_normalization_audit_report

try:
    from normalization_preview_report import build_normalization_preview_report
except ModuleNotFoundError:
    adapter_path = Path(__file__).resolve().with_name("normalization_preview_report.py")
    spec = util.spec_from_file_location("normalization_preview_report", adapter_path)
    normalization_preview_report = util.module_from_spec(spec)
    spec.loader.exec_module(normalization_preview_report)
    build_normalization_preview_report = normalization_preview_report.build_normalization_preview_report


PACKAGE_ID = "aeterna.sample_runtime_package"
PACKAGE_VERSION = "0.1.0"
SCHEMA_VERSION = "sample-runtime-package-v1"
RULESET_VERSION = "sample-ruleset-v0"

OUTPUT_FILES = [
    "manifest.json",
    "cards.jsonl",
    "decks.jsonl",
    "lookups.json",
    "aliases.json",
    "normalization_aliases.json",
    "normalization_audit_report.json",
    "normalization_preview_report.json",
    "ability_registry.json",
    "engine_support.json",
    "diagnostics.json",
    "build_report.md",
]


def _fixture_lookups():
    return [
        {
            "lookup_group": "card_type",
            "value": "Entitas",
            "label_hu": "Entitas",
            "status": "active",
            "canonical_value": "Entitas",
            "used_for": ["cards.card_type"],
        },
        {
            "lookup_group": "card_type",
            "value": "Ige",
            "label_hu": "Ige",
            "status": "active",
            "canonical_value": "Ige",
            "used_for": ["cards.card_type"],
        },
        {
            "lookup_group": "card_type",
            "value": "Rituale",
            "label_hu": "Rituale",
            "status": "active",
            "canonical_value": "Rituale",
            "used_for": ["cards.card_type"],
        },
        {
            "lookup_group": "card_type",
            "value": "Jel",
            "label_hu": "Jel",
            "status": "active",
            "canonical_value": "Jel",
            "used_for": ["cards.card_type"],
        },
        {
            "lookup_group": "card_type",
            "value": "Sik",
            "label_hu": "Sik",
            "status": "active",
            "canonical_value": "Sik",
            "used_for": ["cards.card_type"],
        },
        {
            "lookup_group": "realm",
            "value": "Ignis",
            "label_hu": "Ignis",
            "status": "active",
            "canonical_value": "Ignis",
            "used_for": ["cards.realm", "decks.realm"],
        },
        {
            "lookup_group": "realm",
            "value": "Aqua",
            "label_hu": "Aqua",
            "status": "active",
            "canonical_value": "Aqua",
            "used_for": ["cards.realm", "decks.realm"],
        },
    ]


def _fixture_aliases():
    return [
        {
            "lookup_group": "card_type",
            "alias_value": "Rituálé",
            "canonical_value": "Rituale",
            "status": "active",
            "danger_level": "low",
            "notes": "Human-facing accented form mapped to runtime-safe sample value.",
        },
        {
            "lookup_group": "realm",
            "alias_value": "Tűz",
            "canonical_value": "Ignis",
            "status": "active",
            "danger_level": "low",
            "notes": "Hungarian thematic alias for sample fixtures.",
        },
    ]


def _fixture_cards():
    return [
        {
            "card_id": "SMP-IGN-001",
            "name_hu": "Parazsorzo Entitas",
            "card_type": "Entitas",
            "realm": "Ignis",
            "clan": "Hamvaskez",
            "magnitude": 1,
            "aura_cost": 1,
            "atk": 2,
            "hp": 3,
            "keywords": ["orzo"],
            "runtime_status": "sample_ready",
            "interpretation_status": "structured_sample",
            "structured_ability": {"module_id": "sample_damage_1", "parameters": {"amount": 1}},
            "engine_support_status": "declared_only",
            "diagnostics": [],
        },
        {
            "card_id": "SMP-IGN-002",
            "name_hu": "Szikra Ige",
            "card_type": "Ige",
            "realm": "Ignis",
            "clan": "Hamvaskez",
            "magnitude": 1,
            "aura_cost": 1,
            "atk": 0,
            "hp": 0,
            "keywords": ["azonnali"],
            "runtime_status": "sample_ready",
            "interpretation_status": "structured_sample",
            "structured_ability": {"module_id": "sample_damage_1", "parameters": {"amount": 1}},
            "engine_support_status": "declared_only",
            "diagnostics": [],
        },
        {
            "card_id": "SMP-IGN-003",
            "name_hu": "Hamuesku Rituale",
            "card_type": "Rituale",
            "realm": "Ignis",
            "clan": "Hamvaskez",
            "magnitude": 2,
            "aura_cost": 2,
            "atk": 0,
            "hp": 0,
            "keywords": ["tartos"],
            "runtime_status": "sample_ready",
            "interpretation_status": "manual_review",
            "structured_ability": {"module_id": "sample_aura_gain", "parameters": {"amount": 1}},
            "engine_support_status": "not_executed",
            "diagnostics": ["diag_sample_manual_review"],
        },
        {
            "card_id": "SMP-IGN-004",
            "name_hu": "Voros Jel",
            "card_type": "Jel",
            "realm": "Ignis",
            "clan": "Hamvaskez",
            "magnitude": 1,
            "aura_cost": 0,
            "atk": 0,
            "hp": 0,
            "keywords": ["reakcio"],
            "runtime_status": "sample_ready",
            "interpretation_status": "structured_sample",
            "structured_ability": {"module_id": "sample_damage_1", "parameters": {"amount": 1}},
            "engine_support_status": "declared_only",
            "diagnostics": [],
        },
        {
            "card_id": "SMP-IGN-005",
            "name_hu": "Kohos Sik",
            "card_type": "Sik",
            "realm": "Ignis",
            "clan": "Hamvaskez",
            "magnitude": 3,
            "aura_cost": 2,
            "atk": 0,
            "hp": 0,
            "keywords": ["helyszin"],
            "runtime_status": "sample_ready",
            "interpretation_status": "structured_sample",
            "structured_ability": {"module_id": "sample_aura_gain", "parameters": {"amount": 1}},
            "engine_support_status": "declared_only",
            "diagnostics": [],
        },
    ]


def _fixture_decks():
    return [
        {
            "deck_id": "SMP-DECK-IGNIS-001",
            "product_id": "SMP-PRODUCT-001",
            "name_hu": "Ignis sample pakli",
            "realm": "Ignis",
            "deck_type": "sample_constructed",
            "card_entries": [
                {"card_id": "SMP-IGN-001", "count": 2},
                {"card_id": "SMP-IGN-002", "count": 2},
                {"card_id": "SMP-IGN-003", "count": 1},
                {"card_id": "SMP-IGN-004", "count": 1},
                {"card_id": "SMP-IGN-005", "count": 1},
            ],
            "card_count": 7,
            "valid": True,
            "diagnostics": [],
        }
    ]


def _fixture_ability_registry():
    return [
        {
            "module_id": "sample_damage_1",
            "module_type": "effect",
            "label_hu": "Sebzes minta modul",
            "support_status": "declared_only",
            "input_parameters": [{"name": "amount", "type": "int", "required": True}],
            "output_events": ["damage_declared"],
            "diagnostics": [],
        },
        {
            "module_id": "sample_aura_gain",
            "module_type": "effect",
            "label_hu": "Aura nyeres minta modul",
            "support_status": "declared_only",
            "input_parameters": [{"name": "amount", "type": "int", "required": True}],
            "output_events": ["resource_gain_declared"],
            "diagnostics": [],
        },
    ]


def _fixture_base_diagnostics():
    return [
        {
            "diagnostic_id": "diag_sample_manual_review",
            "severity": "warning",
            "category": "sample_data",
            "code": "MANUAL_REVIEW_PLACEHOLDER",
            "message_hu": "A Rituale kartya kepessege csak strukturalt minta, nem futtathato szabaly.",
            "blocking": False,
            "object_ref": {"type": "card", "id": "SMP-IGN-003"},
            "suggested_action": "Eles adatfeldolgozas elott add meg a vegleges ertelmezest.",
        }
    ]


def _uses_export_inputs(export_runtime_cards_path, export_runtime_decks_path, export_runtime_lookups_path):
    return any((export_runtime_cards_path, export_runtime_decks_path, export_runtime_lookups_path))


def build_normalization_aliases_payload(aliases):
    aliases = list(aliases or [])
    return {
        "normalization_aliases": aliases,
        "summary": {
            "records_loaded": len(aliases),
            "normalization_allowed": sum(1 for alias in aliases if alias.get("normalization_allowed")),
            "requires_audit": sum(1 for alias in aliases if alias.get("requires_audit")),
        },
    }


def _empty_normalization_aliases_payload():
    return build_normalization_aliases_payload([])


def _lookup_values(lookups, group):
    return {item["value"] for item in lookups if item["lookup_group"] == group and item["status"] == "active"}


def _error(diagnostic_id, code, message_hu, object_ref):
    return {
        "diagnostic_id": diagnostic_id,
        "severity": "error",
        "category": "validation",
        "code": code,
        "message_hu": message_hu,
        "blocking": True,
        "object_ref": object_ref,
        "suggested_action": "Javitsd a sample fixture adatot, majd epitsd ujra a csomagot.",
    }


def validate_package(cards, decks, lookups, diagnostics):
    known_card_types = _lookup_values(lookups, "card_type")
    known_realms = _lookup_values(lookups, "realm")
    card_ids = [card.get("card_id") for card in cards if card.get("card_id")]
    card_id_counts = Counter(card_ids)
    known_card_ids = set(card_ids)

    for index, card in enumerate(cards):
        card_ref = {"type": "card", "id": card.get("card_id"), "index": index}
        if not card.get("card_id"):
            diagnostics.append(
                _error(
                    f"diag_missing_card_id_{index}",
                    "MISSING_CARD_ID",
                    "A kartyanak nincs card_id erteke.",
                    card_ref,
                )
            )
        if card.get("card_type") not in known_card_types:
            diagnostics.append(
                _error(
                    f"diag_unknown_card_type_{index}",
                    "UNKNOWN_CARD_TYPE",
                    f"Ismeretlen card_type lookup ertek: {card.get('card_type')}",
                    card_ref,
                )
            )
        if card.get("realm") not in known_realms:
            diagnostics.append(
                _error(
                    f"diag_unknown_card_realm_{index}",
                    "UNKNOWN_REALM",
                    f"Ismeretlen realm lookup ertek: {card.get('realm')}",
                    card_ref,
                )
            )

    for card_id, count in card_id_counts.items():
        if count > 1:
            diagnostics.append(
                _error(
                    f"diag_duplicate_card_id_{card_id}",
                    "DUPLICATE_CARD_ID",
                    f"Duplikalt card_id: {card_id}",
                    {"type": "card", "id": card_id},
                )
            )

    for deck in decks:
        deck_ref = {"type": "deck", "id": deck.get("deck_id")}
        if deck.get("realm") not in known_realms:
            diagnostics.append(
                _error(
                    f"diag_unknown_deck_realm_{deck.get('deck_id')}",
                    "UNKNOWN_REALM",
                    f"Ismeretlen deck realm lookup ertek: {deck.get('realm')}",
                    deck_ref,
                )
            )
        for entry in deck.get("card_entries", []):
            if entry.get("card_id") not in known_card_ids:
                diagnostics.append(
                    _error(
                        f"diag_missing_deck_card_{deck.get('deck_id')}_{entry.get('card_id')}",
                        "DECK_CARD_NOT_FOUND",
                        f"A deck nem letezo card_id-ra hivatkozik: {entry.get('card_id')}",
                        {"type": "deck_card_entry", "deck_id": deck.get("deck_id"), "card_id": entry.get("card_id")},
                    )
                )

    blocking = any(item.get("blocking") for item in diagnostics)
    warnings = sum(1 for item in diagnostics if item.get("severity") == "warning")
    errors = sum(1 for item in diagnostics if item.get("severity") == "error")
    return {
        "blocking": blocking,
        "card_count": len(cards),
        "deck_count": len(decks),
        "diagnostic_count": len(diagnostics),
        "warning_count": warnings,
        "error_count": errors,
    }


def _engine_support_summary(cards, ability_registry):
    statuses = Counter(card["engine_support_status"] for card in cards)
    module_statuses = Counter(module["support_status"] for module in ability_registry)
    return {
        "card_statuses": dict(sorted(statuses.items())),
        "ability_module_statuses": dict(sorted(module_statuses.items())),
        "runtime_executes_abilities": False,
        "notes_hu": "A sample package csak deklaralja a kepesseg modulokat, nem futtatja oket.",
    }


def _write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path, rows):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def _build_report(cards, decks, diagnostics, validation_summary, normalization_audit_report, normalization_preview_report):
    warnings = validation_summary["warning_count"]
    blocking_errors = sum(1 for item in diagnostics if item.get("blocking"))
    audit_summary = normalization_audit_report.get("summary", {})
    preview_summary = normalization_preview_report.get("summary", {})
    return "\n".join(
        [
            "# AETERNA sample runtime package build report",
            "",
            f"- Kartyak szama: {len(cards)}",
            f"- Paklik szama: {len(decks)}",
            f"- Warningok szama: {warnings}",
            f"- Blocking hibak szama: {blocking_errors}",
            f"- Validation blocking: {str(validation_summary['blocking']).lower()}",
            f"- Normalization audit matches: {int(audit_summary.get('matches_total', 0))}",
            f"- Normalization audit requires audit: {int(audit_summary.get('requires_audit', 0))}",
            f"- Normalization audit allowed preview: {int(audit_summary.get('normalization_allowed', 0))}",
            f"- Normalization preview items: {int(preview_summary.get('preview_items', 0))}",
            f"- Normalization preview skipped audit-required: {int(preview_summary.get('skipped_requires_audit', 0))}",
            f"- Normalization preview applied: {int(preview_summary.get('applied', 0))}",
            "",
            "Ez a csomag kontrollalt fixture adatbol epult. Nem olvas XLSX-et, nem futtat kepessegeket, es nem teljes export rendszer.",
            "",
        ]
    )


def build_package(
    output_dir=None,
    export_runtime_cards_path=None,
    export_runtime_decks_path=None,
    export_runtime_lookups_path=None,
    normalization_aliases_payload=None,
    normalization_aliases_source=None,
):
    repo_root = Path(__file__).resolve().parents[2]
    target_dir = Path(output_dir) if output_dir else repo_root / "fixture_runtime_package"
    target_dir.mkdir(parents=True, exist_ok=True)

    aliases = _fixture_aliases()
    source_files = [{"path": "tools/runtime_package/build_sample_runtime_package.py", "type": "in_code_fixture"}]
    if export_runtime_lookups_path:
        lookup_adapter_result = load_builder_lookups_from_runtime_lookups_jsonl(export_runtime_lookups_path)
        lookups = lookup_adapter_result["lookups"]
        source_files.append(
            {
                "path": str(Path(export_runtime_lookups_path)),
                "type": "lookups_runtime_jsonl",
                "adapter": "runtime_lookups_builder_adapter.py",
                "summary": lookup_adapter_result["summary"],
            }
        )
    else:
        lookups = _fixture_lookups()
    if export_runtime_cards_path:
        adapter_result = load_builder_cards_from_export_runtime_jsonl(export_runtime_cards_path)
        cards = adapter_result["cards"]
        source_files.append(
            {
                "path": str(Path(export_runtime_cards_path)),
                "type": "export_runtime_cards_jsonl",
                "adapter": "runtime_cards_builder_adapter.py",
                "summary": adapter_result["summary"],
            }
        )
    else:
        cards = _fixture_cards()
    if export_runtime_decks_path:
        deck_adapter_result = load_builder_decks_from_product_decklists_jsonl(export_runtime_decks_path)
        decks = deck_adapter_result["decks"]
        source_files.append(
            {
                "path": str(Path(export_runtime_decks_path)),
                "type": "product_decklists_jsonl",
                "adapter": "runtime_decks_builder_adapter.py",
                "summary": deck_adapter_result["summary"],
            }
        )
    else:
        decks = _fixture_decks()
    if normalization_aliases_payload is None:
        normalization_aliases_payload = _empty_normalization_aliases_payload()
    elif normalization_aliases_source:
        source_files.append(normalization_aliases_source)
    ability_registry = _fixture_ability_registry()
    diagnostics = [] if _uses_export_inputs(export_runtime_cards_path, export_runtime_decks_path, export_runtime_lookups_path) else _fixture_base_diagnostics()

    validation_summary = validate_package(cards, decks, lookups, diagnostics)
    normalization_audit_report = build_normalization_audit_report(cards, decks, normalization_aliases_payload)
    normalization_preview_report = build_normalization_preview_report(normalization_audit_report)
    engine_support = {
        "schema_version": SCHEMA_VERSION,
        "summary": _engine_support_summary(cards, ability_registry),
        "supported_card_types": sorted(_lookup_values(lookups, "card_type")),
        "supported_realms": sorted(_lookup_values(lookups, "realm")),
        "ability_execution": "not_implemented",
    }
    manifest = {
        "package_id": PACKAGE_ID,
        "package_version": PACKAGE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ruleset_version": RULESET_VERSION,
        "source_files": source_files,
        "files": [{"path": filename, "format": filename.rsplit(".", 1)[-1]} for filename in OUTPUT_FILES],
        "validation_summary": validation_summary,
        "engine_support_summary": engine_support["summary"],
        "metadata": {
            "generator": "build_sample_runtime_package.py",
            "purpose_hu": "Minimalis sample runtime package szerkezet bizonyitasa.",
            "production_export": False,
        },
    }

    _write_json(target_dir / "manifest.json", manifest)
    _write_jsonl(target_dir / "cards.jsonl", cards)
    _write_jsonl(target_dir / "decks.jsonl", decks)
    _write_json(target_dir / "lookups.json", {"lookups": lookups})
    _write_json(target_dir / "aliases.json", {"aliases": aliases})
    _write_json(target_dir / "normalization_aliases.json", normalization_aliases_payload)
    _write_json(target_dir / "normalization_audit_report.json", normalization_audit_report)
    _write_json(target_dir / "normalization_preview_report.json", normalization_preview_report)
    _write_json(target_dir / "ability_registry.json", {"ability_registry": ability_registry})
    _write_json(target_dir / "engine_support.json", engine_support)
    _write_json(target_dir / "diagnostics.json", {"diagnostics": diagnostics})
    (target_dir / "build_report.md").write_text(
        _build_report(
            cards,
            decks,
            diagnostics,
            validation_summary,
            normalization_audit_report,
            normalization_preview_report,
        ),
        encoding="utf-8",
        newline="\n",
    )
    return {
        "output_dir": target_dir,
        "files": OUTPUT_FILES,
        "validation_summary": validation_summary,
        "normalization_audit_summary": normalization_audit_report["summary"],
        "normalization_preview_summary": normalization_preview_report["summary"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build the AETERNA sample runtime package.")
    parser.add_argument(
        "--output-dir",
        "--output",
        default=None,
        help="Optional output directory. Defaults to ./fixture_runtime_package from the repository root.",
    )
    parser.add_argument(
        "--export-runtime-cards",
        default=None,
        help="Optional EXPORT_RUNTIME.jsonl-style card input. Defaults to the in-code sample card fixture.",
    )
    parser.add_argument(
        "--export-runtime-decks",
        default=None,
        help="Optional PRODUCT_DECKLISTS.jsonl-style deck input. Defaults to the in-code sample deck fixture.",
    )
    parser.add_argument(
        "--export-runtime-lookups",
        default=None,
        help="Optional LOOKUPS_RUNTIME.jsonl-style lookup input. Defaults to the in-code sample lookup fixture.",
    )
    args = parser.parse_args(argv)

    result = build_package(
        args.output_dir,
        export_runtime_cards_path=args.export_runtime_cards,
        export_runtime_decks_path=args.export_runtime_decks,
        export_runtime_lookups_path=args.export_runtime_lookups,
    )
    print(f"Sample runtime package written to: {result['output_dir']}")
    print(f"Validation blocking: {str(result['validation_summary']['blocking']).lower()}")
    print(f"Files: {', '.join(result['files'])}")
    return 0 if not result["validation_summary"]["blocking"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
