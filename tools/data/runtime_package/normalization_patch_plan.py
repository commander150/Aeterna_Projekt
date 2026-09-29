"""Build a field-level patch plan from safe normalization preview items.

The patch plan is read-only planning data. It never mutates runtime package
records and never applies normalization.
"""

from __future__ import annotations


def build_normalization_patch_plan(normalization_preview_report):
    preview_items = _extract_preview_items(normalization_preview_report)
    grouped = {}
    for item in preview_items:
        key = (
            str(item.get("object_type", "")),
            str(item.get("object_id", "")),
            str(item.get("field", "")),
        )
        grouped.setdefault(key, []).append(item)

    patch_rows = []
    blocked_rows = []
    for (object_type, object_id, field), items in sorted(grouped.items()):
        patch_or_blocked = _build_group_patch(object_type, object_id, field, items)
        if patch_or_blocked["status"] == "ready":
            patch_rows.append(patch_or_blocked)
        else:
            blocked_rows.append(patch_or_blocked)

    return {
        "patch_plan": patch_rows,
        "blocked_or_ambiguous": blocked_rows,
        "summary": {
            "preview_items_input": len(preview_items),
            "patches_ready": len(patch_rows),
            "blocked_or_ambiguous": len(blocked_rows),
            "applied": 0,
            "field_patch_counts": _count_by_key(patch_rows, "field"),
            "object_type_patch_counts": _count_by_key(patch_rows, "object_type"),
        },
    }


def _extract_preview_items(normalization_preview_report):
    if not isinstance(normalization_preview_report, dict):
        return []
    rows = normalization_preview_report.get("normalization_preview", [])
    if not isinstance(rows, list):
        return []
    return rows


def _build_group_patch(object_type, object_id, field, items):
    safe_items = [item for item in items if _is_safe_preview_item(item)]
    if len(safe_items) != len(items):
        return _blocked(object_type, object_id, field, "unsupported_preview_status", items)
    if any(item.get("preview_value") is None for item in safe_items):
        return _blocked(object_type, object_id, field, "unresolved_preview_value", items)

    originals = {_stable_value_key(item.get("original_value")) for item in safe_items}
    if len(originals) != 1:
        return _blocked(object_type, object_id, field, "conflicting_original_values", items)

    changes = _dedupe_changes(safe_items)
    if _has_conflicting_canonical(changes):
        return _blocked(object_type, object_id, field, "conflicting_preview_values", items)

    original_value = safe_items[0].get("original_value")
    planned_value = _apply_changes(original_value, changes)
    if planned_value is None:
        return _blocked(object_type, object_id, field, "could_not_merge_preview_values", items)

    return {
        "object_type": object_type,
        "object_id": object_id,
        "field": field,
        "original_value": original_value,
        "planned_value": planned_value,
        "status": "ready",
        "applied": False,
        "changes": changes,
        "notes": [],
    }


def _is_safe_preview_item(item):
    return (
        bool(item.get("normalization_allowed", False))
        and not bool(item.get("requires_audit", False))
        and str(item.get("preview_status", "")) == "safe_preview"
    )


def _dedupe_changes(items):
    seen = set()
    changes = []
    for item in items:
        change = {
            "matched_value": str(item.get("matched_value", "")),
            "canonical_value": str(item.get("canonical_value", "")),
            "lookup_group": str(item.get("lookup_group", "")),
        }
        key = (change["matched_value"], change["canonical_value"], change["lookup_group"])
        if key in seen:
            continue
        seen.add(key)
        changes.append(change)
    return changes


def _has_conflicting_canonical(changes):
    canonical_by_match = {}
    for change in changes:
        matched_value = change["matched_value"]
        canonical_value = change["canonical_value"]
        existing = canonical_by_match.setdefault(matched_value, canonical_value)
        if existing != canonical_value:
            return True
    return False


def _apply_changes(original_value, changes):
    if isinstance(original_value, list):
        planned_items = list(original_value)
        replaced_any = False
        for change in changes:
            planned_items, replaced = _replace_in_list(
                planned_items,
                change["matched_value"],
                change["canonical_value"],
            )
            replaced_any = replaced_any or replaced
        return planned_items if replaced_any else None

    if original_value is None:
        return None

    planned_text = str(original_value)
    replaced_any = False
    for change in changes:
        planned_text, replaced = _replace_in_text(
            planned_text,
            change["matched_value"],
            change["canonical_value"],
        )
        replaced_any = replaced_any or replaced
    return planned_text if replaced_any else None


def _replace_in_list(values, matched_value, canonical_value):
    replaced_any = False
    result = []
    for value in values:
        replaced_text, replaced = _replace_in_text(str(value), matched_value, canonical_value)
        result.append(replaced_text if replaced else value)
        replaced_any = replaced_any or replaced
    return result, replaced_any


def _replace_in_text(text, matched_value, canonical_value):
    if text.strip() == matched_value:
        return _replace_whole_trimmed_text(text, canonical_value), True

    parts = _split_with_separators(text)
    replaced = False
    for index, part in enumerate(parts):
        if part in (",", ";"):
            continue
        if part.strip() == matched_value:
            parts[index] = _replace_whole_trimmed_text(part, canonical_value)
            replaced = True
    if replaced:
        return "".join(parts), True
    return text, False


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


def _blocked(object_type, object_id, field, reason, items):
    return {
        "object_type": object_type,
        "object_id": object_id,
        "field": field,
        "status": "ambiguous",
        "reason": reason,
        "applied": False,
        "preview_items": items,
    }


def _stable_value_key(value):
    if isinstance(value, list):
        return ("list", tuple(_stable_value_key(item) for item in value))
    if isinstance(value, dict):
        return ("dict", tuple(sorted((key, _stable_value_key(item)) for key, item in value.items())))
    return ("scalar", str(value))


def _count_by_key(rows, key):
    counts = {}
    for row in rows:
        value = row.get(key, "")
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))
