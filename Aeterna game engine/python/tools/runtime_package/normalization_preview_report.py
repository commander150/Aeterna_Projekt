"""Safe-normalization preview report built from normalization audit rows.

The preview report is diagnostics-only: it never mutates runtime cards/decks and
never applies normalization.
"""

from __future__ import annotations


def build_normalization_preview_report(normalization_audit_report):
    audit_rows = _extract_audit_rows(normalization_audit_report)
    preview_rows = []
    skipped_rows = []

    for row in audit_rows:
        if bool(row.get("normalization_allowed", False)):
            preview_rows.append(_build_preview_row(row))
        elif bool(row.get("requires_audit", False)):
            skipped_rows.append(_build_skipped_row(row))

    return {
        "normalization_preview": preview_rows,
        "skipped": skipped_rows,
        "summary": {
            "audit_matches_total": len(audit_rows),
            "preview_items": len(preview_rows),
            "skipped_requires_audit": len(skipped_rows),
            "applied": 0,
            "field_preview_counts": _count_by_key(preview_rows, "field"),
            "lookup_group_preview_counts": _count_by_key(preview_rows, "lookup_group"),
        },
    }


def _extract_audit_rows(normalization_audit_report):
    if isinstance(normalization_audit_report, dict):
        rows = normalization_audit_report.get("normalization_audit", [])
        if isinstance(rows, list):
            return rows
    return []


def _build_preview_row(row):
    original_value = row.get("original_value", row.get("value"))
    matched_value = str(row.get("value", ""))
    canonical_value = str(row.get("canonical_value", ""))
    preview_value = _preview_value(original_value, matched_value, canonical_value)
    preview_status = "safe_preview" if preview_value is not None else "safe_preview_unresolved_shape"
    return {
        "object_type": str(row.get("object_type", "")),
        "object_id": str(row.get("object_id", "")),
        "field": str(row.get("field", "")),
        "lookup_group": str(row.get("lookup_group", "")),
        "original_value": original_value,
        "matched_value": matched_value,
        "canonical_value": canonical_value,
        "preview_value": preview_value,
        "normalization_allowed": True,
        "requires_audit": False,
        "applied": False,
        "preview_status": preview_status,
        "notes": str(row.get("notes", "")),
    }


def _build_skipped_row(row):
    return {
        "object_type": str(row.get("object_type", "")),
        "object_id": str(row.get("object_id", "")),
        "field": str(row.get("field", "")),
        "matched_value": str(row.get("value", "")),
        "canonical_value": str(row.get("canonical_value", "")),
        "normalization_allowed": False,
        "requires_audit": True,
        "preview_status": "manual_audit_required",
        "applied": False,
    }


def _preview_value(original_value, matched_value, canonical_value):
    if isinstance(original_value, list):
        replaced = False
        preview_items = []
        for item in original_value:
            preview_item = _preview_text(str(item), matched_value, canonical_value)
            if preview_item is None:
                preview_items.append(item)
            else:
                preview_items.append(preview_item)
                replaced = True
        return preview_items if replaced else None

    if original_value is None:
        return None
    return _preview_text(str(original_value), matched_value, canonical_value)


def _preview_text(text, matched_value, canonical_value):
    if text.strip() == matched_value:
        return _replace_whole_trimmed_text(text, canonical_value)

    separators = _split_with_separators(text)
    replaced = False
    for index, part in enumerate(separators):
        if part in (",", ";"):
            continue
        if part.strip() == matched_value:
            separators[index] = _replace_whole_trimmed_text(part, canonical_value)
            replaced = True
    if replaced:
        return "".join(separators)
    return None


def _replace_whole_trimmed_text(text, replacement):
    leading = text[: len(text) - len(text.lstrip())]
    trailing = text[len(text.rstrip()) :]
    return "%s%s%s" % (leading, replacement, trailing)


def _split_with_separators(text):
    parts = []
    current = []
    for char in text:
        if char in (",", ";"):
            parts.append("".join(current))
            parts.append(char)
            current = []
        else:
            current.append(char)
    parts.append("".join(current))
    return parts


def _count_by_key(rows, key):
    counts = {}
    for row in rows:
        value = row.get(key, "")
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))
