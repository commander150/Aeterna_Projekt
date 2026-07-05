"""Run a partial real-data smoke build from XLSX EXPORT_RUNTIME cards."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from importlib import util
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[2]


def _load_module(module_name, path):
    spec = util.spec_from_file_location(module_name, path)
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


XLSX_EXPORT = _load_module(
    "xlsx_export",
    ENGINE_PYTHON_DIR / "tools" / "xlsx_export" / "xlsx_export.py",
)
PACKAGE_BUILDER = _load_module(
    "build_sample_runtime_package",
    ENGINE_PYTHON_DIR / "tools" / "runtime_package" / "build_sample_runtime_package.py",
)
LOOKUPS_XLSX_READER = _load_module(
    "lookups_xlsx_reader",
    ENGINE_PYTHON_DIR / "tools" / "runtime_package" / "lookups_xlsx_reader.py",
)
LEGACY_ALIASES_READER = _load_module(
    "runtime_legacy_aliases_reader",
    ENGINE_PYTHON_DIR / "tools" / "runtime_package" / "runtime_legacy_aliases_reader.py",
)


def run_smoke(
    xlsx_path=None,
    source_dir=None,
    output_dir=None,
    keep_output=False,
    include_decklists=False,
    include_lookups_runtime=False,
    lookups_xlsx_path=None,
    apply_normalization_patches=True,
):
    """Export runtime cards from XLSX and build a partial runtime package smoke output."""
    xlsx_path = _resolve_xlsx_path(xlsx_path, source_dir)
    owns_output_dir = output_dir is None
    root_output_dir = Path(output_dir) if output_dir else Path(tempfile.mkdtemp(prefix="aeterna_real_runtime_smoke_"))
    export_dir = root_output_dir / "exports"
    package_dir = root_output_dir / "runtime_package"

    try:
        profile, sheet_name, export_runtime_path, output_format = XLSX_EXPORT.resolve_export_options(
            "runtime_cards",
            None,
            None,
            None,
            output_dir=export_dir,
        )
        export_count, export_warnings = XLSX_EXPORT.export_worksheet(
            xlsx_path,
            sheet_name,
            export_runtime_path,
            output_format,
            profile=profile,
        )
        warnings_path = XLSX_EXPORT.write_warnings(export_runtime_path, export_warnings)

        export_decklists_path = None
        decklist_export_count = 0
        decklist_export_warnings = []
        decklist_warnings_path = None
        if include_decklists:
            deck_profile, deck_sheet_name, export_decklists_path, deck_output_format = XLSX_EXPORT.resolve_export_options(
                "decklists",
                None,
                None,
                None,
                output_dir=export_dir,
            )
            decklist_export_count, decklist_export_warnings = XLSX_EXPORT.export_worksheet(
                xlsx_path,
                deck_sheet_name,
                export_decklists_path,
                deck_output_format,
                profile=deck_profile,
            )
            decklist_warnings_path = XLSX_EXPORT.write_warnings(export_decklists_path, decklist_export_warnings)

        export_lookups_path = None
        lookups_export_count = 0
        lookups_export_warnings = []
        lookups_warnings_path = None
        if include_lookups_runtime:
            export_lookups_path = export_dir / "LOOKUPS_RUNTIME.jsonl"
            if lookups_xlsx_path:
                lookups_xlsx_path = Path(lookups_xlsx_path)
                lookup_reader_result = LOOKUPS_XLSX_READER.load_runtime_lookups_from_xlsx(lookups_xlsx_path)
                lookups_export_count = _write_lookup_jsonl(export_lookups_path, lookup_reader_result["lookups"])
                lookups_export_warnings = lookup_reader_result["summary"].get("diagnostics", [])
            else:
                lookups_profile, lookups_sheet_name, export_lookups_path, lookups_output_format = XLSX_EXPORT.resolve_export_options(
                    "lookups_runtime",
                    None,
                    None,
                    None,
                    output_dir=export_dir,
                )
                lookups_export_count, lookups_export_warnings = XLSX_EXPORT.export_worksheet(
                    xlsx_path,
                    lookups_sheet_name,
                    export_lookups_path,
                    lookups_output_format,
                    profile=lookups_profile,
                )
                lookups_warnings_path = XLSX_EXPORT.write_warnings(export_lookups_path, lookups_export_warnings)

        normalization_aliases_payload = PACKAGE_BUILDER.build_normalization_aliases_payload([])
        normalization_aliases_source = None
        if lookups_xlsx_path:
            legacy_aliases_result = LEGACY_ALIASES_READER.load_runtime_legacy_aliases_from_xlsx(lookups_xlsx_path)
            normalization_aliases_payload = PACKAGE_BUILDER.build_normalization_aliases_payload(
                legacy_aliases_result["aliases"]
            )
            normalization_aliases_source = {
                "path": str(Path(lookups_xlsx_path)),
                "type": "lookups_xlsx_runtime_legacy_aliases",
                "sheet": "RUNTIME_LEGACY_ALIAS",
                "adapter": "runtime_legacy_aliases_reader.py",
                "summary": legacy_aliases_result["summary"],
            }

        build_result = PACKAGE_BUILDER.build_package(
            package_dir,
            export_runtime_cards_path=export_runtime_path,
            export_runtime_decks_path=export_decklists_path,
            export_runtime_lookups_path=export_lookups_path,
            normalization_aliases_payload=normalization_aliases_payload,
            normalization_aliases_source=normalization_aliases_source,
            apply_normalization_patches=apply_normalization_patches,
        )

        manifest_path = package_dir / "manifest.json"
        diagnostics_path = package_dir / "diagnostics.json"
        cards_path = package_dir / "cards.jsonl"
        diagnostics = _read_diagnostics(diagnostics_path)
        manifest = _read_json(manifest_path)
        normalization_audit_summary = build_result.get("normalization_audit_summary", {})
        normalization_preview_summary = build_result.get("normalization_preview_summary", {})
        normalization_patch_plan_summary = build_result.get("normalization_patch_plan_summary", {})
        normalization_apply_summary = build_result.get("normalization_apply_summary", {})
        ability_support_summary = build_result.get("ability_support_summary", {})
        summary = {
            "xlsx_path": str(xlsx_path),
            "lookups_xlsx_path": str(lookups_xlsx_path) if lookups_xlsx_path else "none",
            "export_runtime_jsonl": str(export_runtime_path),
            "export_runtime_jsonl_exists": export_runtime_path.exists(),
            "exported_card_rows": export_count,
            "export_warnings": len(export_warnings),
            "export_warnings_path": str(warnings_path) if warnings_path else "none",
            "decklist_export_jsonl": str(export_decklists_path) if export_decklists_path else "none",
            "decklist_export_jsonl_exists": export_decklists_path.exists() if export_decklists_path else False,
            "decklist_export_rows": decklist_export_count,
            "decklist_export_warnings": len(decklist_export_warnings),
            "decklist_export_warnings_path": str(decklist_warnings_path) if decklist_warnings_path else "none",
            "lookups_export_jsonl": str(export_lookups_path) if export_lookups_path else "none",
            "lookups_export_jsonl_exists": export_lookups_path.exists() if export_lookups_path else False,
            "lookups_export_rows": lookups_export_count,
            "lookups_export_warnings": len(lookups_export_warnings),
            "lookups_export_warnings_path": str(lookups_warnings_path) if lookups_warnings_path else "none",
            "normalization_aliases_source": _normalization_aliases_source(lookups_xlsx_path),
            "normalization_aliases_count": normalization_aliases_payload["summary"]["records_loaded"],
            "normalization_aliases_requires_audit_count": normalization_aliases_payload["summary"]["requires_audit"],
            "normalization_aliases_allowed_count": normalization_aliases_payload["summary"]["normalization_allowed"],
            "normalization_audit_matches": int(normalization_audit_summary.get("matches_total", 0)),
            "normalization_audit_requires_audit": int(normalization_audit_summary.get("requires_audit", 0)),
            "normalization_audit_allowed": int(normalization_audit_summary.get("normalization_allowed", 0)),
            "normalization_preview_items": int(normalization_preview_summary.get("preview_items", 0)),
            "normalization_preview_skipped_requires_audit": int(
                normalization_preview_summary.get("skipped_requires_audit", 0)
            ),
            "normalization_preview_applied": int(normalization_preview_summary.get("applied", 0)),
            "normalization_patch_plan_ready": int(normalization_patch_plan_summary.get("patches_ready", 0)),
            "normalization_patch_plan_blocked": int(
                normalization_patch_plan_summary.get("blocked_or_ambiguous", 0)
            ),
            "normalization_patch_plan_applied": int(normalization_patch_plan_summary.get("applied", 0)),
            "normalization_apply_enabled": bool(normalization_apply_summary.get("enabled", False)),
            "normalization_apply_applied": int(normalization_apply_summary.get("applied", 0)),
            "normalization_apply_skipped": int(normalization_apply_summary.get("skipped", 0)),
            "normalization_apply_conflicts": int(normalization_apply_summary.get("conflicts", 0)),
            "ability_support_warnings": int(ability_support_summary.get("warnings", 0)),
            "ability_support_audit_notes": int(ability_support_summary.get("audit_notes", 0)),
            "ability_support_declared_only": int(ability_support_summary.get("declared_only", 0)),
            "ability_support_unsupported": int(ability_support_summary.get("unsupported", 0)),
            "ability_support_partial": int(ability_support_summary.get("partial", 0)),
            "ability_support_fallback_required": int(ability_support_summary.get("fallback_required", 0)),
            "ability_support_not_checked": int(ability_support_summary.get("not_checked", 0)),
            "ability_support_manual_review_required": int(
                ability_support_summary.get("manual_review_required", 0)
            ),
            "ability_support_unknown_status": int(ability_support_summary.get("unknown_support_status", 0)),
            "runtime_package_output_dir": str(package_dir),
            "cards_jsonl_exists": cards_path.exists(),
            "cards_jsonl_rows": _count_jsonl_rows(cards_path),
            "manifest_exists": manifest_path.exists(),
            "diagnostics_exists": diagnostics_path.exists(),
            "validation_blocking": build_result["validation_summary"]["blocking"],
            "deck_reference_errors": _count_diagnostic_code(diagnostics, "DECK_CARD_NOT_FOUND"),
            "unknown_realm_errors": _count_diagnostic_code(diagnostics, "UNKNOWN_REALM"),
            "unknown_card_type_errors": _count_diagnostic_code(diagnostics, "UNKNOWN_CARD_TYPE"),
            "diagnostic_count": len(diagnostics),
            "manifest_source_count": len(manifest.get("source_files", [])) if manifest else 0,
            "package_status": "smoke_partial_real_data_build",
            "cards_source": "export-derived",
            "decks_source": "export-derived" if include_decklists else "sample fixture",
            "lookups_source": _lookups_source(include_lookups_runtime, lookups_xlsx_path),
            "fixture_components": _fixture_components(include_decklists, include_lookups_runtime),
            "output_kept": (not owns_output_dir) or keep_output,
        }
        return summary
    finally:
        if owns_output_dir and not keep_output:
            shutil.rmtree(root_output_dir, ignore_errors=True)


def print_summary(summary):
    print("AETERNA real EXPORT_RUNTIME package smoke")
    print(f"xlsx_path: {summary['xlsx_path']}")
    print(f"lookups_xlsx_path: {summary.get('lookups_xlsx_path', 'none')}")
    print(f"exported_card_rows: {summary['exported_card_rows']}")
    print(f"export_runtime_jsonl_exists: {str(summary['export_runtime_jsonl_exists']).lower()}")
    print(f"export_runtime_jsonl: {summary['export_runtime_jsonl']}")
    print(f"runtime_package_output_dir: {summary['runtime_package_output_dir']}")
    print(f"cards_jsonl_exists: {str(summary['cards_jsonl_exists']).lower()}")
    print(f"cards_jsonl_rows: {summary['cards_jsonl_rows']}")
    print(f"manifest_exists: {str(summary['manifest_exists']).lower()}")
    print(f"diagnostics_exists: {str(summary['diagnostics_exists']).lower()}")
    print(f"validation_blocking: {str(summary['validation_blocking']).lower()}")
    print(f"deck_reference_errors: {summary['deck_reference_errors']}")
    print(f"unknown_realm_errors: {summary['unknown_realm_errors']}")
    print(f"unknown_card_type_errors: {summary['unknown_card_type_errors']}")
    print(f"export_warnings: {summary['export_warnings']}")
    print(f"decklist_export_jsonl_exists: {str(summary['decklist_export_jsonl_exists']).lower()}")
    print(f"decklist_export_jsonl: {summary['decklist_export_jsonl']}")
    print(f"decklist_export_rows: {summary['decklist_export_rows']}")
    print(f"decklist_export_warnings: {summary['decklist_export_warnings']}")
    print(f"lookups_export_jsonl_exists: {str(summary['lookups_export_jsonl_exists']).lower()}")
    print(f"lookups_export_jsonl: {summary['lookups_export_jsonl']}")
    print(f"lookups_export_rows: {summary['lookups_export_rows']}")
    print(f"lookups_export_warnings: {summary['lookups_export_warnings']}")
    print(f"normalization_aliases_source: {summary['normalization_aliases_source']}")
    print(f"normalization_aliases_count: {summary['normalization_aliases_count']}")
    print(f"normalization_aliases_requires_audit_count: {summary['normalization_aliases_requires_audit_count']}")
    print(f"normalization_aliases_allowed_count: {summary['normalization_aliases_allowed_count']}")
    print(f"normalization_audit_matches: {summary['normalization_audit_matches']}")
    print(f"normalization_audit_requires_audit: {summary['normalization_audit_requires_audit']}")
    print(f"normalization_audit_allowed: {summary['normalization_audit_allowed']}")
    print(f"normalization_preview_items: {summary['normalization_preview_items']}")
    print(f"normalization_preview_skipped_requires_audit: {summary['normalization_preview_skipped_requires_audit']}")
    print(f"normalization_preview_applied: {summary['normalization_preview_applied']}")
    print(f"normalization_patch_plan_ready: {summary['normalization_patch_plan_ready']}")
    print(f"normalization_patch_plan_blocked: {summary['normalization_patch_plan_blocked']}")
    print(f"normalization_patch_plan_applied: {summary['normalization_patch_plan_applied']}")
    print(f"normalization_apply_enabled: {str(summary['normalization_apply_enabled']).lower()}")
    print(f"normalization_apply_applied: {summary['normalization_apply_applied']}")
    print(f"normalization_apply_skipped: {summary['normalization_apply_skipped']}")
    print(f"normalization_apply_conflicts: {summary['normalization_apply_conflicts']}")
    print(f"ability_support_warnings: {summary['ability_support_warnings']}")
    print(f"ability_support_audit_notes: {summary['ability_support_audit_notes']}")
    print(f"ability_support_declared_only: {summary['ability_support_declared_only']}")
    print(f"ability_support_unsupported: {summary['ability_support_unsupported']}")
    print(f"ability_support_partial: {summary['ability_support_partial']}")
    print(f"ability_support_fallback_required: {summary['ability_support_fallback_required']}")
    print(f"ability_support_not_checked: {summary['ability_support_not_checked']}")
    print(f"ability_support_manual_review_required: {summary['ability_support_manual_review_required']}")
    print(f"ability_support_unknown_status: {summary['ability_support_unknown_status']}")
    print(f"diagnostic_count: {summary['diagnostic_count']}")
    print("cards_source: export-derived")
    print(f"decks_source: {summary['decks_source']}")
    print(f"lookups_source: {summary['lookups_source']}")
    print(f"fixture_components: {', '.join(summary['fixture_components'])}")
    print("package_status: smoke / partial real-data build")
    print(f"output_kept: {str(summary['output_kept']).lower()}")


def _resolve_xlsx_path(xlsx_path, source_dir):
    if xlsx_path:
        path = Path(xlsx_path)
        return XLSX_EXPORT.validate_source_path(path, source_dir=Path(source_dir) if source_dir else None)

    if not source_dir:
        raise XLSX_EXPORT.ExportError("Adj meg --xlsx vagy --source-dir argumentumot.")

    files = XLSX_EXPORT.find_xlsx_files(Path(source_dir))
    if not files:
        raise XLSX_EXPORT.ExportError(f"Nincs .xlsx fajl ebben a mappaban: {source_dir}")
    if len(files) > 1:
        names = ", ".join(path.name for path in files)
        raise XLSX_EXPORT.ExportError(f"Tobb .xlsx fajl talalhato, adj meg --xlsx argumentumot: {names}")
    return files[0]


def _read_json(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_diagnostics(path):
    payload = _read_json(path)
    return payload.get("diagnostics", [])


def _count_jsonl_rows(path):
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _count_diagnostic_code(diagnostics, code):
    return sum(1 for diagnostic in diagnostics if diagnostic.get("code") == code)


def _fixture_components(include_decklists, include_lookups_runtime):
    components = ["aliases", "ability_registry"]
    if not include_lookups_runtime:
        components.insert(0, "lookups")
    if not include_decklists:
        components.insert(0, "decks")
    return components


def _lookups_source(include_lookups_runtime, lookups_xlsx_path):
    if not include_lookups_runtime:
        return "sample fixture"
    if lookups_xlsx_path:
        return "LOOKUPS.xlsx:RUNTIME_CORE+RUNTIME_ABILITY"
    return "embedded 5A. LOOKUPS_RUNTIME"


def _normalization_aliases_source(lookups_xlsx_path):
    if lookups_xlsx_path:
        return "LOOKUPS.xlsx:RUNTIME_LEGACY_ALIAS"
    return "none"


def _write_lookup_jsonl(path, lookups):
    path.parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8", newline="\n") as handle:
        rows_written = 0
        for lookup in lookups:
            for row in _lookup_to_export_rows(lookup):
                handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
                rows_written += 1
    return rows_written


def _lookup_to_export_rows(lookup):
    rows = [_lookup_to_export_row(lookup, lookup["value"])]
    label_hu = lookup.get("label_hu", "none")
    if label_hu not in ("none", lookup["value"]):
        rows.append(_lookup_to_export_row(lookup, label_hu))
    return rows


def _lookup_to_export_row(lookup, value):
    return {
        "Lookup_Group": lookup["lookup_group"],
        "Value": value,
        "Label_HU": lookup["label_hu"],
        "Status": lookup["status"],
        "Canonical_Value": lookup["canonical_value"],
        "Used_For": ";".join(lookup["used_for"]),
        "Sort_Order": lookup["sort_order"],
        "Source": lookup["source"],
        "Notes": lookup["notes"],
    }


def build_parser():
    parser = argparse.ArgumentParser(description="Smoke build a partial runtime package from XLSX EXPORT_RUNTIME cards.")
    parser.add_argument("--xlsx", type=Path, default=None, help="Source XLSX file.")
    parser.add_argument("--source-dir", type=Path, default=None, help="Directory used to find or validate the source XLSX.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Optional smoke output directory.")
    parser.add_argument("--keep-output", action="store_true", help="Keep temporary output when --output-dir is omitted.")
    parser.add_argument(
        "--include-decklists",
        action="store_true",
        help="Also export PRODUCT_DECKLISTS and use it for decks.jsonl.",
    )
    parser.add_argument(
        "--include-lookups-runtime",
        action="store_true",
        help="Also export runtime lookups and use them for lookups.json.",
    )
    parser.add_argument("--lookups-xlsx", type=Path, default=None, help="Canonical LOOKUPS.xlsx source file.")
    normalization_group = parser.add_mutually_exclusive_group()
    normalization_group.add_argument(
        "--apply-normalization-patches",
        dest="apply_normalization_patches",
        action="store_true",
        help="Apply ready normalization patch plan rows to generated candidate cards/decks. This is the default.",
    )
    normalization_group.add_argument(
        "--no-apply-normalization-patches",
        dest="apply_normalization_patches",
        action="store_false",
        help="Raw/debug mode: build the candidate without applying safe normalization patches.",
    )
    parser.set_defaults(apply_normalization_patches=True)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run_smoke(
            xlsx_path=args.xlsx,
            source_dir=args.source_dir,
            output_dir=args.output_dir,
            keep_output=args.keep_output,
            include_decklists=args.include_decklists,
            include_lookups_runtime=args.include_lookups_runtime,
            lookups_xlsx_path=args.lookups_xlsx,
            apply_normalization_patches=args.apply_normalization_patches,
        )
        print_summary(summary)
        return 0
    except (XLSX_EXPORT.ExportError, OSError, ValueError) as exc:
        print(f"Hiba: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
