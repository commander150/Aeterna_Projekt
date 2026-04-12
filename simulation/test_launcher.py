from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Callable, Dict, Optional

from engine.config import DEFAULT_EXPANSION_FLAGS, DEFAULT_EXPANSION_MODULES
from engine.logging_utils import create_logger
from simulation.config import SimulationConfig
from simulation.runner import futtat_szimulaciot
from utils.logger import naplo


PROGRAM_MAPPA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_XLSX_PATH = os.path.join(PROGRAM_MAPPA, "cards.xlsx")
LAST_SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".last_test_launcher.json")


PROFILE_PRESETS: Dict[str, Dict] = {
    "smoke_random": {
        "label": "Smoke test (veletlen matchup)",
        "description": "Gyors altalanos AI-vs-AI smoke kor veletlen birodalmakkal.",
        "settings": {
            "games": 3,
            "random_seed": None,
            "player1_realm": None,
            "player2_realm": None,
            "random_realm_fallback": True,
        },
    },
    "seeded_matchup": {
        "label": "Seedelt matchup",
        "description": "Rogzitett seed + konkret matchup gyors ujrafuttatasra.",
        "settings": {
            "games": 3,
            "random_seed": 105,
            "player1_realm": "Ignis",
            "player2_realm": "Aqua",
            "random_realm_fallback": False,
        },
    },
    "repeated_matchup": {
        "label": "Tobbszor ismEtelt matchup",
        "description": "Ugyanaz a matchup tobb jatekkal, gyozelmi minta nezesere.",
        "settings": {
            "games": 10,
            "random_seed": 211,
            "player1_realm": "Ignis",
            "player2_realm": "Aqua",
            "random_realm_fallback": False,
        },
    },
    "realm_focus": {
        "label": "Egy birodalom fokusz",
        "description": "Az egyik oldal fix, a masik veletlen; dominancia es hibaerzekenyseg nezesere.",
        "settings": {
            "games": 8,
            "random_seed": 314,
            "player1_realm": "Ignis",
            "player2_realm": None,
            "random_realm_fallback": True,
        },
    },
    "long_seeded_run": {
        "label": "Hosszabb seedelt futas",
        "description": "Hosszabb tesztkor kifogyas, overflow es tempo mintak nezesere.",
        "settings": {
            "games": 15,
            "random_seed": 777,
            "player1_realm": "Ignis",
            "player2_realm": "Aqua",
            "random_realm_fallback": False,
        },
    },
}


def get_profile_presets() -> Dict[str, Dict]:
    return deepcopy(PROFILE_PRESETS)


def _normalize_realm(value):
    if value in (None, "", "random", "veletlen", "none"):
        return None
    return str(value)


def _normalize_optional_int(value):
    if value in (None, "", "random", "none"):
        return None
    return int(value)


def _normalize_positive_int(value, default):
    if value in (None, ""):
        return int(default)
    parsed = int(value)
    return parsed if parsed > 0 else int(default)


def load_last_settings(path: str = LAST_SETTINGS_PATH) -> Optional[Dict]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            return None
        return data
    except Exception:
        return None


def save_last_settings(settings: Dict, path: str = LAST_SETTINGS_PATH) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def build_config_from_profile(profile_name: str, overrides: Optional[Dict] = None) -> SimulationConfig:
    if profile_name not in PROFILE_PRESETS:
        raise ValueError(f"Ismeretlen tesztprofil: {profile_name}")

    settings = deepcopy(PROFILE_PRESETS[profile_name]["settings"])
    settings.update(dict(overrides or {}))

    games = _normalize_positive_int(settings.get("games"), PROFILE_PRESETS[profile_name]["settings"]["games"])
    random_seed = _normalize_optional_int(settings.get("random_seed"))
    player1_realm = _normalize_realm(settings.get("player1_realm"))
    player2_realm = _normalize_realm(settings.get("player2_realm"))
    random_realm_fallback = bool(settings.get("random_realm_fallback", True))

    return SimulationConfig(
        games=games,
        random_seed=random_seed,
        player1_realm=player1_realm,
        player2_realm=player2_realm,
        random_realm_fallback=random_realm_fallback,
        engine_run_mode="core_only",
        expansion_modules=dict(DEFAULT_EXPANSION_MODULES),
        expansion_flags=dict(DEFAULT_EXPANSION_FLAGS),
    )


def run_test_profile(
    profile_name: str,
    *,
    overrides: Optional[Dict] = None,
    xlsx_path: str = DEFAULT_XLSX_PATH,
    base_dir: str = PROGRAM_MAPPA,
) -> SimulationConfig:
    config = build_config_from_profile(profile_name, overrides=overrides)
    create_logger(config, base_dir=base_dir, logger=naplo)
    futtat_szimulaciot(xlsx_path, config=config)
    return config


def _prompt_value(prompt: str, current_value, input_func: Callable[[str], str]) -> str:
    current_text = "random" if current_value is None else str(current_value)
    return input_func(f"{prompt} [{current_text}]: ").strip()


def launch_interactive(
    *,
    xlsx_path: str = DEFAULT_XLSX_PATH,
    base_dir: str = PROGRAM_MAPPA,
    input_func: Callable[[str], str] = input,
    print_func: Callable[[str], None] = print,
    settings_path: str = LAST_SETTINGS_PATH,
):
    presets = get_profile_presets()
    last_settings = load_last_settings(settings_path)

    print_func("=== AETERNA TESZTLAUNCHER ===")
    print_func("Valassz tesztprofilt:")
    for index, (profile_name, profile) in enumerate(presets.items(), start=1):
        print_func(f"{index}. {profile['label']} - {profile['description']}")
    if last_settings:
        print_func("R. Utolso hasznalt beallitas ujrafuttatasa")
    print_func("Q. Kilepes")

    choice = input_func("Valasztas: ").strip().lower()
    if choice == "q":
        return None

    if choice == "r" and last_settings:
        config = build_config_from_profile(last_settings["profile_name"], overrides=last_settings.get("overrides"))
        create_logger(config, base_dir=base_dir, logger=naplo)
        futtat_szimulaciot(xlsx_path, config=config)
        return config

    profile_names = list(presets.keys())
    try:
        selected_index = int(choice) - 1
        profile_name = profile_names[selected_index]
    except Exception as exc:
        raise ValueError("Ervenytelen tesztprofil-valasztas.") from exc

    base_settings = deepcopy(presets[profile_name]["settings"])
    games_raw = _prompt_value("Futasok szama", base_settings.get("games"), input_func)
    seed_raw = _prompt_value("Seed", base_settings.get("random_seed"), input_func)
    p1_raw = _prompt_value("P1 birodalom", base_settings.get("player1_realm"), input_func)
    p2_raw = _prompt_value("P2 birodalom", base_settings.get("player2_realm"), input_func)

    overrides = {
        "games": games_raw or base_settings.get("games"),
        "random_seed": seed_raw if seed_raw != "" else base_settings.get("random_seed"),
        "player1_realm": p1_raw if p1_raw != "" else base_settings.get("player1_realm"),
        "player2_realm": p2_raw if p2_raw != "" else base_settings.get("player2_realm"),
        "random_realm_fallback": base_settings.get("random_realm_fallback", True),
    }

    save_last_settings({"profile_name": profile_name, "overrides": overrides}, settings_path)
    config = build_config_from_profile(profile_name, overrides=overrides)
    create_logger(config, base_dir=base_dir, logger=naplo)
    futtat_szimulaciot(xlsx_path, config=config)
    return config


if __name__ == "__main__":
    launch_interactive()
