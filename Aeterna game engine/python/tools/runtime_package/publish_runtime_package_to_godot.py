"""Validate and publish a real-data runtime package candidate to Godot."""

from __future__ import annotations

import argparse
import shutil
import sys
import uuid
from importlib import util
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[2]
ENGINE_DIR = ENGINE_PYTHON_DIR.parent
PROJECT_ROOT = ENGINE_DIR.parent
PROJECT_TEMP_DIR = PROJECT_ROOT / "TEMP"
DEFAULT_XLSX_PATH = (
    PROJECT_ROOT
    / "Aeterna dokumentációk"
    / "AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx"
)
DEFAULT_TEMP_OUTPUT_DIR = PROJECT_TEMP_DIR / "publish_runtime_package_candidate"
DEFAULT_GODOT_PACKAGE_DIR = ENGINE_DIR / "Godot" / "runtime_package"

PACKAGE_FILES = [
    "manifest.json",
    "cards.jsonl",
    "decks.jsonl",
    "lookups.json",
    "diagnostics.json",
    "engine_support.json",
    "aliases.json",
    "ability_registry.json",
    "build_report.md",
]


class PublishError(Exception):
    """Raised when the candidate package must not be published."""


def _load_module(module_name, path):
    spec = util.spec_from_file_location(module_name, path)
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


SMOKE_RUNNER = _load_module(
    "smoke_real_export_runtime_package",
    ENGINE_PYTHON_DIR / "tools" / "runtime_package" / "smoke_real_export_runtime_package.py",
)


def publish_runtime_package(
    xlsx_path=DEFAULT_XLSX_PATH,
    temp_output_dir=DEFAULT_TEMP_OUTPUT_DIR,
    godot_package_dir=DEFAULT_GODOT_PACKAGE_DIR,
    dry_run=False,
):
    temp_output_dir = Path(temp_output_dir)
    godot_package_dir = Path(godot_package_dir)

    temp_output_dir = _create_candidate_output_dir(temp_output_dir)

    summary = SMOKE_RUNNER.run_smoke(
        xlsx_path=Path(xlsx_path),
        output_dir=temp_output_dir,
        include_decklists=True,
        include_lookups_runtime=True,
    )
    candidate_package_dir = temp_output_dir / "runtime_package"
    validation_errors = validate_candidate(summary, candidate_package_dir)
    publish_summary = dict(summary)
    publish_summary["candidate_package_dir"] = str(candidate_package_dir)
    publish_summary["godot_package_dir"] = str(godot_package_dir)
    publish_summary["dry_run"] = bool(dry_run)
    publish_summary["validation_errors"] = validation_errors
    publish_summary["copied_files"] = []
    publish_summary["would_copy_files"] = list(PACKAGE_FILES)
    publish_summary["published"] = False

    if validation_errors:
        raise PublishError(_format_validation_errors(validation_errors, publish_summary))

    if dry_run:
        return publish_summary

    godot_package_dir.mkdir(parents=True, exist_ok=True)
    copied_files = []
    for filename in PACKAGE_FILES:
        source = candidate_package_dir / filename
        target = godot_package_dir / filename
        shutil.copy2(source, target)
        copied_files.append(filename)

    publish_summary["copied_files"] = copied_files
    publish_summary["published"] = True
    return publish_summary


def validate_candidate(summary, candidate_package_dir):
    errors = []
    candidate_package_dir = Path(candidate_package_dir)

    if bool(summary.get("validation_blocking", True)):
        errors.append("validation_blocking must be false")
    if int(summary.get("diagnostic_count", -1)) != 0:
        errors.append("diagnostic_count must be 0")
    if int(summary.get("deck_reference_errors", -1)) != 0:
        errors.append("deck_reference_errors must be 0")
    if int(summary.get("unknown_realm_errors", -1)) != 0:
        errors.append("unknown_realm_errors must be 0")
    if int(summary.get("unknown_card_type_errors", -1)) != 0:
        errors.append("unknown_card_type_errors must be 0")

    for filename in PACKAGE_FILES:
        if not (candidate_package_dir / filename).is_file():
            errors.append("missing package file: %s" % filename)

    return errors


def print_publish_summary(summary):
    print("AETERNA runtime package publish")
    print("candidate_package_dir: %s" % summary.get("candidate_package_dir", ""))
    print("godot_package_dir: %s" % summary.get("godot_package_dir", ""))
    print("cards_count: %s" % summary.get("cards_jsonl_rows", ""))
    print("decks_source: %s" % summary.get("decks_source", ""))
    print("lookups_source: %s" % summary.get("lookups_source", ""))
    print("validation_blocking: %s" % str(summary.get("validation_blocking", "")).lower())
    print("diagnostic_count: %s" % summary.get("diagnostic_count", ""))
    print("deck_reference_errors: %s" % summary.get("deck_reference_errors", ""))
    print("unknown_realm_errors: %s" % summary.get("unknown_realm_errors", ""))
    print("unknown_card_type_errors: %s" % summary.get("unknown_card_type_errors", ""))
    print("dry_run: %s" % str(summary.get("dry_run", False)).lower())
    if summary.get("dry_run"):
        print("would_copy_files: %s" % ", ".join(summary.get("would_copy_files", [])))
    else:
        print("copied_files: %s" % ", ".join(summary.get("copied_files", [])))
    print("published: %s" % str(summary.get("published", False)).lower())


def build_parser():
    parser = argparse.ArgumentParser(description="Validate and publish a runtime package candidate to Godot.")
    parser.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX_PATH, help="Source XLSX file.")
    parser.add_argument(
        "--temp-output-dir",
        type=Path,
        default=DEFAULT_TEMP_OUTPUT_DIR,
        help="TEMP candidate output directory.",
    )
    parser.add_argument(
        "--godot-package-dir",
        type=Path,
        default=DEFAULT_GODOT_PACKAGE_DIR,
        help="Godot runtime package target directory.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate candidate but do not copy to Godot.")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = publish_runtime_package(
            xlsx_path=args.xlsx,
            temp_output_dir=args.temp_output_dir,
            godot_package_dir=args.godot_package_dir,
            dry_run=args.dry_run,
        )
        print_publish_summary(summary)
        return 0
    except PublishError as exc:
        print("Publish blocked:", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print("Hiba: %s" % exc, file=sys.stderr)
        return 1


def _ensure_temp_output_dir(path):
    resolved = Path(path).resolve()
    temp_root = PROJECT_TEMP_DIR.resolve()
    if resolved != temp_root and temp_root not in resolved.parents:
        raise PublishError("temp-output-dir must be under project TEMP: %s" % temp_root)


def _create_candidate_output_dir(path):
    path = Path(path)
    _ensure_temp_output_dir(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=False)
        return path

    parent = path.parent
    for _attempt in range(100):
        candidate = parent / ("%s_%s" % (path.name, uuid.uuid4().hex[:8]))
        _ensure_temp_output_dir(candidate)
        if not candidate.exists():
            candidate.mkdir(parents=True, exist_ok=False)
            return candidate
    raise PublishError("could not allocate unique temp output dir under project TEMP")



def _format_validation_errors(errors, summary):
    lines = [
        "candidate_package_dir: %s" % summary.get("candidate_package_dir", ""),
        "godot_package_dir: %s" % summary.get("godot_package_dir", ""),
        "validation_blocking: %s" % str(summary.get("validation_blocking", "")).lower(),
        "diagnostic_count: %s" % summary.get("diagnostic_count", ""),
        "deck_reference_errors: %s" % summary.get("deck_reference_errors", ""),
        "unknown_realm_errors: %s" % summary.get("unknown_realm_errors", ""),
        "unknown_card_type_errors: %s" % summary.get("unknown_card_type_errors", ""),
        "errors:",
    ]
    lines.extend("- %s" % error for error in errors)
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
