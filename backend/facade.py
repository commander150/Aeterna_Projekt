from __future__ import annotations

import os
import random
import uuid

from data.loader import kartyak_betoltese_xlsx
from engine.config import set_active_engine_config
from engine.effect_diagnostics_v2 import install_effect_diagnostics
from engine.game import AeternaSzimulacio
from simulation.config import SimulationConfig

from backend.action_request import validate_action_request
from backend.legal_actions import get_legal_actions_for_player
from backend.snapshot import export_match_snapshot


_MATCH_REGISTRY: dict[str, dict] = {}


def _resolve_config(config=None):
    if config is None:
        return SimulationConfig()
    if isinstance(config, SimulationConfig):
        return config
    if isinstance(config, dict):
        simulation_fields = {
            "games",
            "random_seed",
            "player1_realm",
            "player2_realm",
            "random_realm_fallback",
            "player1_deck",
            "player2_deck",
            "scenario",
            "scripted_opening_hands",
            "scripted_board_state",
            "engine_run_mode",
            "expansion_modules",
            "expansion_flags",
            "log_base_dir",
        }
        return SimulationConfig(**{key: value for key, value in config.items() if key in simulation_fields})
    raise TypeError("A facade konfiguracio csak SimulationConfig, dict vagy None lehet.")


def _resolve_cards(config=None):
    if isinstance(config, dict) and config.get("cards") is not None:
        return list(config["cards"])

    xlsx_path = None
    if isinstance(config, dict):
        xlsx_path = config.get("xlsx_path")

    if not xlsx_path:
        xlsx_path = os.path.join(os.getcwd(), "cards.xlsx")

    cards = kartyak_betoltese_xlsx(xlsx_path)
    if not cards:
        raise ValueError(f"Nem sikerult kartyakat betolteni innen: {xlsx_path}")
    return cards


def _available_realms(cards):
    return sorted(
        {
            getattr(card, "birodalom", None)
            for card in cards
            if getattr(card, "birodalom", None) and getattr(card, "birodalom", None) != "None"
        }
    )


def _pick_realm(preferred, available, random_fallback=True, forbidden=None):
    forbidden = set(forbidden or [])
    if preferred:
        if preferred in available and preferred not in forbidden:
            return preferred
        if not random_fallback:
            raise ValueError(f"Nem elerheto birodalom a facade create_match hivasban: {preferred}")

    choices = [realm for realm in available if realm not in forbidden]
    if not choices:
        raise ValueError("Nincs valaszthato birodalom a facade create_match hivasban.")
    return random.choice(choices)


def create_match(config=None):
    install_effect_diagnostics()
    resolved_config = _resolve_config(config)
    if resolved_config.random_seed is not None:
        random.seed(resolved_config.random_seed)

    engine_config = set_active_engine_config(resolved_config.to_engine_config())
    cards = _resolve_cards(config)
    available_realms = _available_realms(cards)

    player1_realm = _pick_realm(
        resolved_config.player1_realm,
        available_realms,
        random_fallback=resolved_config.random_realm_fallback,
    )
    player2_realm = _pick_realm(
        resolved_config.player2_realm,
        available_realms,
        random_fallback=resolved_config.random_realm_fallback,
        forbidden=[] if resolved_config.player2_realm else [player1_realm],
    )

    game = AeternaSzimulacio(player1_realm, player2_realm, cards, engine_config=engine_config)
    match_id = uuid.uuid4().hex
    _MATCH_REGISTRY[match_id] = {
        "game": game,
        "config": resolved_config,
        "engine_config": engine_config,
        "player1_realm": player1_realm,
        "player2_realm": player2_realm,
    }
    return match_id


def get_snapshot(match_id):
    entry = _MATCH_REGISTRY.get(match_id)
    if entry is None:
        return None
    return export_match_snapshot(entry["game"])


def get_match_result(match_id):
    snapshot = get_snapshot(match_id)
    if snapshot is None:
        return None
    return {
        "match_id": match_id,
        "finished": bool(snapshot.get("match_finished")),
        "winner": snapshot.get("winner"),
        "victory_reason": snapshot.get("victory_reason"),
        "turn": snapshot.get("turn"),
        "active_player": snapshot.get("active_player"),
        "phase": snapshot.get("phase"),
    }


def drop_match(match_id):
    return _MATCH_REGISTRY.pop(match_id, None) is not None


def list_matches():
    return [
        {
            "match_id": match_id,
            "player1_realm": entry.get("player1_realm"),
            "player2_realm": entry.get("player2_realm"),
            "turn": getattr(entry.get("game"), "kor", None),
        }
        for match_id, entry in _MATCH_REGISTRY.items()
    ]


def get_legal_actions(match_id, player_id):
    entry = _MATCH_REGISTRY.get(match_id)
    if entry is None:
        return None

    game = entry["game"]
    player = None
    if player_id in {"p1", getattr(getattr(game, "p1", None), "nev", None)}:
        player = getattr(game, "p1", None)
    elif player_id in {"p2", getattr(getattr(game, "p2", None), "nev", None)}:
        player = getattr(game, "p2", None)

    if player is None:
        return None

    return get_legal_actions_for_player(game, player)


def validate_action(match_id, player_id, action_request):
    entry = _MATCH_REGISTRY.get(match_id)
    if entry is None:
        return {"valid": False, "reason": "unknown_match_id", "normalized": None}

    game = entry["game"]
    player = None
    if player_id in {"p1", getattr(getattr(game, "p1", None), "nev", None)}:
        player = getattr(game, "p1", None)
    elif player_id in {"p2", getattr(getattr(game, "p2", None), "nev", None)}:
        player = getattr(game, "p2", None)

    if player is None:
        return {"valid": False, "reason": "unknown_player_id", "normalized": None}

    return validate_action_request(game, player, action_request)
