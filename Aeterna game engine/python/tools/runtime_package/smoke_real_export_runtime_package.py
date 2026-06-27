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


def run_smoke(xlsx_path=None, source_dir=None, output_dir=None, keep_output=False, include_decklists=False):
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

        build_result = PACKAGE_BUILDER.build_package(
            package_dir,
            export_runtime_cards_path=export_runtime_path,
            export_runtime_decks_path=export_decklists_path,
        )

        manifest_path = package_dir / "manifest.json"
        diagnostics_path = package_dir / "diagnostics.json"
        cards_path = package_dir / "cards.jsonl"
        diagnostics = _read_diagnostics(diagnostics_path)
        manifest = _read_json(manifest_path)
        summary = {
            "xlsx_path": str(xlsx_path),
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
            "runtime_package_output_dir": str(package_dir),
            "cards_jsonl_exists": cards_path.exists(),
            "cards_jsonl_rows": _count_jsonl_rows(cards_path),
            "manifest_exists": manifest_path.exists(),
            "diagnostics_exists": diagnostics_path.exists(),
            "validation_blocking": build_result["validation_summary"]["blocking"],
            "deck_reference_errors": _count_diagnostic_code(diagnostics, "DECK_CARD_NOT_FOUND"),
            "diagnostic_count": len(diagnostics),
            "manifest_source_count": len(manifest.get("source_files", [])) if manifest else 0,
            "package_status": "smoke_partial_real_data_build",
            "cards_source": "export-derived",
            "decks_source": "export-derived" if include_decklists else "sample fixture",
            "fixture_components": ["lookups", "aliases", "ability_registry"]
            if include_decklists
            else ["decks", "lookups", "aliases", "ability_registry"],
            "output_kept": (not owns_output_dir) or keep_output,
        }
        return summary
    finally:
        if owns_output_dir and not keep_output:
            shutil.rmtree(root_output_dir, ignore_errors=True)


def print_summary(summary):
    print("AETERNA real EXPORT_RUNTIME package smoke")
    print(f"xlsx_path: {summary['xlsx_path']}")
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
    print(f"export_warnings: {summary['export_warnings']}")
    print(f"decklist_export_jsonl_exists: {str(summary['decklist_export_jsonl_exists']).lower()}")
    print(f"decklist_export_jsonl: {summary['decklist_export_jsonl']}")
    print(f"decklist_export_rows: {summary['decklist_export_rows']}")
    print(f"decklist_export_warnings: {summary['decklist_export_warnings']}")
    print(f"diagnostic_count: {summary['diagnostic_count']}")
    print("cards_source: export-derived")
    print(f"decks_source: {summary['decks_source']}")
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
        )
        print_summary(summary)
        return 0
    except (XLSX_EXPORT.ExportError, OSError, ValueError) as exc:
        print(f"Hiba: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
