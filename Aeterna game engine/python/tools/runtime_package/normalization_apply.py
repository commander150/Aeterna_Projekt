"""Apply safe normalization patch plans to generated runtime records.

This module only works on already generated candidate package data. It never
touches XLSX sources and never publishes to Godot by itself.
"""

from __future__ import annotations

from copy import deepcopy


def build_disabled_apply_report(patch_plan=None):
    patches = _extract_ready_patches(patch_plan)
    blocked = _extract_blocked_patches(patch_plan)
    return {
        "enabled": False,
        "applied_patches": [],
        "skipped_patches": [],
        "summary": {
            "enabled": False,
            "patches_input": len(patches) + len(blocked),
            "applied": 0,
            "skipped": 0,
            "conflicts": 0,
        },
    }


def apply_normalization_patch_plan(cards, decks, patch_plan, enabled=False):
    """Apply ready patch plan rows to cards/decks when explicitly enabled.

    The function mutates the provided ``cards`` and ``decks`` lists only when
    ``enabled`` is true and all ready patches pass validation.
    """
    if not enabled:
        return build_disabled_apply_report(patch_plan)

    patches = _extract_ready_patches(patch_plan)
    blocked = _extract_blocked_patches(patch_plan)
    cards_by_id = _index_by_id(cards, "card_id")
    decks_by_id = _index_by_id(decks, "deck_id")

    skipped = []
    for blocked_patch in blocked:
        skipped.append(_skipped_from_patch(blocked_patch, "blocked_or_ambiguous_patch"))

    for patch in patches:
        skipped.extend(_validate_patch(patch, cards_by_id, decks_by_id))

    if skipped:
        return {
            "enabled": True,
            "applied_patches": [],
            "skipped_patches": skipped,
            "summary": {
                "enabled": True,
                "patches_input": len(patches) + len(blocked),
                "applied": 0,
                "skipped": len(skipped),
                "conflicts": len(skipped),
            },
        }

    applied = []
    for patch in patches:
        target = _target_record(patch, cards_by_id, decks_by_id)
        field = patch["field"]
        old_value = deepcopy(target[field])
        new_value = deepcopy(patch["planned_value"])
        target[field] = new_value
        applied.append(
            {
                "object_type": patch.get("object_type"),
                "object_id": patch.get("object_id"),
                "field": field,
                "old_value": old_value,
                "new_value": new_value,
                "applied": True,
                "changes": deepcopy(patch.get("changes", [])),
            }
        )

    return {
        "enabled": True,
        "applied_patches": applied,
        "skipped_patches": [],
        "summary": {
            "enabled": True,
            "patches_input": len(patches) + len(blocked),
            "applied": len(applied),
            "skipped": 0,
            "conflicts": 0,
        },
    }


def _extract_ready_patches(patch_plan):
    if not isinstance(patch_plan, dict):
        return []
    patches = patch_plan.get("patch_plan", [])
    return patches if isinstance(patches, list) else []


def _extract_blocked_patches(patch_plan):
    if not isinstance(patch_plan, dict):
        return []
    blocked = patch_plan.get("blocked_or_ambiguous", [])
    return blocked if isinstance(blocked, list) else []


def _index_by_id(records, id_field):
    result = {}
    for record in records or []:
        if isinstance(record, dict) and record.get(id_field):
            result[str(record[id_field])] = record
    return result


def _validate_patch(patch, cards_by_id, decks_by_id):
    if not isinstance(patch, dict):
        return [_skipped_from_patch({}, "invalid_patch")]
    if patch.get("status") != "ready":
        return [_skipped_from_patch(patch, "patch_not_ready")]
    if patch.get("applied") is not False:
        return [_skipped_from_patch(patch, "patch_already_applied_or_unknown")]
    if patch.get("planned_value") is None:
        return [_skipped_from_patch(patch, "missing_planned_value")]

    target = _target_record(patch, cards_by_id, decks_by_id)
    if target is None:
        return [_skipped_from_patch(patch, "missing_object")]

    field = patch.get("field")
    if not field or field not in target:
        return [_skipped_from_patch(patch, "missing_field")]
    if target[field] != patch.get("original_value"):
        return [_skipped_from_patch(patch, "original_value_mismatch")]
    return []


def _target_record(patch, cards_by_id, decks_by_id):
    object_type = patch.get("object_type")
    object_id = str(patch.get("object_id", ""))
    if object_type == "card":
        return cards_by_id.get(object_id)
    if object_type == "deck":
        return decks_by_id.get(object_id)
    return None


def _skipped_from_patch(patch, reason):
    return {
        "object_type": patch.get("object_type"),
        "object_id": patch.get("object_id"),
        "field": patch.get("field"),
        "reason": reason,
        "applied": False,
    }
