from __future__ import annotations

from backend.legal_actions import get_legal_actions_for_player


SUPPORTED_ACTION_TYPES = {"end_turn", "play_entity", "play_trap"}
REQUIRED_FIELDS = {
    "end_turn": {"action_type", "player"},
    "play_entity": {"action_type", "player", "card_name", "zone", "lane"},
    "play_trap": {"action_type", "player", "card_name", "zone", "lane"},
}


def normalize_action_request(action_request):
    raw = action_request or {}
    normalized = {
        "action_type": raw.get("action_type"),
        "player": raw.get("player"),
        "card_name": raw.get("card_name"),
        "zone": raw.get("zone"),
        "lane": raw.get("lane"),
    }

    if normalized["action_type"] in {"end_turn"}:
        normalized["card_name"] = None
        normalized["zone"] = None
        normalized["lane"] = None

    if normalized["lane"] is not None:
        try:
            normalized["lane"] = int(normalized["lane"])
        except Exception:
            pass

    return normalized


def action_request_to_key(action_request):
    normalized = normalize_action_request(action_request)
    return (
        normalized.get("action_type"),
        normalized.get("player"),
        normalized.get("card_name"),
        normalized.get("zone"),
        normalized.get("lane"),
    )


def _missing_required_fields(normalized):
    action_type = normalized.get("action_type")
    required = REQUIRED_FIELDS.get(action_type, {"action_type", "player"})
    missing = []
    for field in required:
        value = normalized.get(field)
        if value is None or value == "":
            missing.append(field)
    return missing


def validate_action_request(game, player, action_request):
    normalized = normalize_action_request(action_request)
    action_type = normalized.get("action_type")

    if game is None or player is None:
        return {"valid": False, "reason": "missing_game_or_player", "normalized": normalized}

    if action_type not in SUPPORTED_ACTION_TYPES:
        return {"valid": False, "reason": "unsupported_action_type", "normalized": normalized}

    player_name = getattr(player, "nev", None)
    if normalized.get("player") != player_name:
        return {"valid": False, "reason": "player_mismatch", "normalized": normalized}

    missing_fields = _missing_required_fields(normalized)
    if missing_fields:
        return {
            "valid": False,
            "reason": f"missing_required_fields:{','.join(sorted(missing_fields))}",
            "normalized": normalized,
        }

    legal_actions = get_legal_actions_for_player(game, player)
    legal_keys = {action_request_to_key(item) for item in legal_actions}
    if action_request_to_key(normalized) not in legal_keys:
        return {"valid": False, "reason": "not_in_legal_actions", "normalized": normalized}

    return {"valid": True, "reason": None, "normalized": normalized}
