"""Read-only CLI inspector for normalization audit/preview reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[2]
ENGINE_DIR = ENGINE_PYTHON_DIR.parent
DEFAULT_PACKAGE_DIR = ENGINE_DIR / "Godot" / "runtime_package"


class InspectError(Exception):
    """Raised when normalization reports cannot be inspected."""


def inspect_package(package_dir=DEFAULT_PACKAGE_DIR, limit=20):
    package_dir = Path(package_dir)
    audit_report = _read_report(package_dir / "normalization_audit_report.json", "normalization_audit", "summary")
    preview_report = _read_report(
        package_dir / "normalization_preview_report.json",
        "normalization_preview",
        "summary",
        optional_list_key="skipped",
    )
    return build_inspection_summary(audit_report, preview_report, limit=limit)


def build_inspection_summary(audit_report, preview_report, limit=20):
    audit_summary = audit_report["summary"]
    preview_summary = preview_report["summary"]
    limit = max(0, int(limit))
    return {
        "summary": {
            "audit_matches_total": int(audit_summary.get("matches_total", 0)),
            "preview_items": int(preview_summary.get("preview_items", 0)),
            "skipped_requires_audit": int(preview_summary.get("skipped_requires_audit", 0)),
            "applied": int(preview_summary.get("applied", 0)),
        },
        "top_field_matches": _top_counts(audit_summary.get("field_matches", {}), limit),
        "top_lookup_group_matches": _top_counts(audit_summary.get("lookup_group_matches", {}), limit),
        "safe_preview_examples": list(preview_report.get("normalization_preview", []))[:limit],
        "manual_audit_examples": list(preview_report.get("skipped", []))[:limit],
    }


def format_inspection(summary):
    lines = [
        "AETERNA normalization preview inspector",
        "audit_matches_total: %d" % summary["summary"]["audit_matches_total"],
        "preview_items: %d" % summary["summary"]["preview_items"],
        "skipped_requires_audit: %d" % summary["summary"]["skipped_requires_audit"],
        "applied: %d" % summary["summary"]["applied"],
        "",
        "TOP FIELD MATCHES",
    ]
    lines.extend(_format_count_rows(summary["top_field_matches"]))
    lines.append("")
    lines.append("TOP LOOKUP GROUP MATCHES")
    lines.extend(_format_count_rows(summary["top_lookup_group_matches"]))
    lines.append("")
    lines.append("SAFE PREVIEW EXAMPLES")
    lines.extend(_format_preview_rows(summary["safe_preview_examples"]))
    lines.append("")
    lines.append("MANUAL AUDIT EXAMPLES")
    lines.extend(_format_manual_audit_rows(summary["manual_audit_examples"]))
    return "\n".join(lines)


def build_parser():
    parser = argparse.ArgumentParser(description="Inspect AETERNA normalization preview reports.")
    parser.add_argument("--package-dir", type=Path, default=DEFAULT_PACKAGE_DIR, help="Runtime package directory.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum rows per example/count section.")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = inspect_package(args.package_dir, args.limit)
        print(format_inspection(summary))
        return 0
    except (InspectError, OSError, json.JSONDecodeError, ValueError) as exc:
        print("Normalization preview inspect failed: %s" % exc, file=sys.stderr)
        return 1


def _read_report(path, list_key, summary_key, optional_list_key=None):
    path = Path(path)
    if not path.is_file():
        raise InspectError("missing report file: %s" % path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise InspectError("report root must be an object: %s" % path)
    if list_key not in payload or not isinstance(payload[list_key], list):
        raise InspectError("report missing list field '%s': %s" % (list_key, path))
    if summary_key not in payload or not isinstance(payload[summary_key], dict):
        raise InspectError("report missing summary object: %s" % path)
    if optional_list_key and optional_list_key in payload and not isinstance(payload[optional_list_key], list):
        raise InspectError("report field '%s' must be a list: %s" % (optional_list_key, path))
    return payload


def _top_counts(counts, limit):
    if not isinstance(counts, dict):
        return []
    rows = [{"name": str(name), "count": int(count)} for name, count in counts.items()]
    return sorted(rows, key=lambda row: (-row["count"], row["name"]))[:limit]


def _format_count_rows(rows):
    if not rows:
        return ["(none)"]
    return ["- %s: %d" % (row["name"], row["count"]) for row in rows]


def _format_preview_rows(rows):
    if not rows:
        return ["(none)"]
    return [
        "- {object_type} {object_id} {field}: {original_value} | {matched_value} -> {canonical_value} | preview: {preview_value}".format(
            object_type=row.get("object_type", ""),
            object_id=row.get("object_id", ""),
            field=row.get("field", ""),
            original_value=_compact(row.get("original_value")),
            matched_value=row.get("matched_value", ""),
            canonical_value=row.get("canonical_value", ""),
            preview_value=_compact(row.get("preview_value")),
        )
        for row in rows
    ]


def _format_manual_audit_rows(rows):
    if not rows:
        return ["(none)"]
    return [
        "- {object_type} {object_id} {field}: {matched_value} -> {canonical_value} [{preview_status}]".format(
            object_type=row.get("object_type", ""),
            object_id=row.get("object_id", ""),
            field=row.get("field", ""),
            matched_value=row.get("matched_value", ""),
            canonical_value=row.get("canonical_value", ""),
            preview_status=row.get("preview_status", ""),
        )
        for row in rows
    ]


def _compact(value):
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
