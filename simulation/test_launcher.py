from __future__ import annotations

import argparse
import json
import os
from copy import deepcopy
from typing import Callable, Dict, List, Optional, Sequence

from data.loader import kartyak_betoltese_xlsx
from engine.config import DEFAULT_EXPANSION_FLAGS, DEFAULT_EXPANSION_MODULES
from engine.logging_utils import create_logger
from simulation.config import SimulationConfig, normalize_realm_name
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
    return normalize_realm_name(value)


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


def parse_seed_batch_args(seed_list=None, seed_start=None, seed_count=None) -> List[int]:
    if seed_list not in (None, ""):
        parsed = []
        for raw_part in str(seed_list).split(","):
            part = raw_part.strip()
            if not part:
                continue
            parsed.append(int(part))
        if not parsed:
            raise ValueError("A seed-list nem lehet ures.")
        return parsed

    if seed_start is None and seed_count is None:
        return []

    if seed_start is None or seed_count is None:
        raise ValueError("A seed-start es seed-count csak egyutt hasznalhato.")

    parsed_start = int(seed_start)
    parsed_count = int(seed_count)
    if parsed_count <= 0:
        raise ValueError("A seed-count ertekenek pozitivnak kell lennie.")

    return [parsed_start + offset for offset in range(parsed_count)]


def _summary_value(summary, key, default=0):
    if not isinstance(summary, dict):
        return default
    return summary.get(key, default)


def _collect_batch_metrics(run_summaries: Sequence[Dict]) -> Dict[str, int]:
    totals = {
        "spells_cast": 0,
        "summons": 0,
        "traps_played": 0,
        "traps_triggered": 0,
        "seal_breaks": 0,
    }
    for summary in run_summaries:
        metrics = summary.get("metrics", {}) if isinstance(summary, dict) else {}
        for key in totals:
            totals[key] += int(metrics.get(key, 0))
    return totals


def detect_batch_alerts(run_summaries: Sequence[Dict]) -> List[str]:
    if not run_summaries:
        return []

    total_runs = sum(int(_summary_value(summary, "games", 0)) for summary in run_summaries)
    p1_wins = sum(int(_summary_value(summary, "p1_wins", 0)) for summary in run_summaries)
    p2_wins = sum(int(_summary_value(summary, "p2_wins", 0)) for summary in run_summaries)
    draws = sum(int(_summary_value(summary, "draws", 0)) for summary in run_summaries)
    total_turns = sum(int(_summary_value(summary, "total_turns", 0)) for summary in run_summaries)
    average_turns = (total_turns / total_runs) if total_runs else 0.0
    metrics = _collect_batch_metrics(run_summaries)

    alerts: List[str] = []
    if total_runs and (p1_wins == total_runs or p2_wins == total_runs):
        dominant_side = "P1" if p1_wins == total_runs else "P2"
        alerts.append(f"Egyoldalu matchup-gyanu: {dominant_side} nyerte az osszes futast.")
    if total_runs >= 3 and average_turns <= 6:
        alerts.append(f"Nagyon gyors meccsek: atlagos korszam csak {average_turns:.2f}.")
    if total_runs >= 3 and average_turns >= 16:
        alerts.append(f"Nagyon hosszu meccsek: atlagos korszam {average_turns:.2f}.")
    if metrics["traps_played"] == 0 and metrics["traps_triggered"] == 0:
        alerts.append("Nem latszik trap aktivitas a batchben.")
    if metrics["spells_cast"] == 0:
        alerts.append("Nem latszik spell/rituale aktivitas a batchben.")
    if metrics["seal_breaks"] == 0 and draws == total_runs:
        alerts.append("Nem tortent pecsettores, a batch teljesen dontetlen maradt.")
    return alerts


def format_batch_summary(run_summaries: Sequence[Dict]) -> List[str]:
    if not run_summaries:
        return [
            "Futasok szama: 0",
            "Seedek: -",
            "Gyozelmek: P1=0 | P2=0 | Dontetlen=0",
            "Atlagos korszam: -",
        ]

    seeds = [str(summary.get("random_seed", "random")) for summary in run_summaries]
    total_runs = sum(int(_summary_value(summary, "games", 0)) for summary in run_summaries)
    p1_wins = sum(int(_summary_value(summary, "p1_wins", 0)) for summary in run_summaries)
    p2_wins = sum(int(_summary_value(summary, "p2_wins", 0)) for summary in run_summaries)
    draws = sum(int(_summary_value(summary, "draws", 0)) for summary in run_summaries)
    total_turns = sum(int(_summary_value(summary, "total_turns", 0)) for summary in run_summaries)
    average_turns = (total_turns / total_runs) if total_runs else 0.0
    metrics = _collect_batch_metrics(run_summaries)
    alerts = detect_batch_alerts(run_summaries)

    lines = [
        f"Futasok szama: {total_runs}",
        f"Seedek: {', '.join(seeds)}",
        f"Gyozelmek: P1={p1_wins} | P2={p2_wins} | Dontetlen={draws}",
        f"Atlagos korszam: {average_turns:.2f}" if total_runs else "Atlagos korszam: -",
        "Aktivitas: "
        + " | ".join(
            [
                f"summons={metrics['summons']}",
                f"spells={metrics['spells_cast']}",
                f"traps_played={metrics['traps_played']}",
                f"traps_triggered={metrics['traps_triggered']}",
                f"seal_breaks={metrics['seal_breaks']}",
            ]
        ),
    ]
    if alerts:
        lines.append("Gyanus jelek:")
        lines.extend([f"- {alert}" for alert in alerts])
    else:
        lines.append("Gyanus jelek: nincs kiemelt launcher-szintu figyelmeztetes.")
    return lines


def _print_batch_summary(
    run_summaries: Sequence[Dict],
    print_func: Callable[[str], None] = print,
):
    print_func("=== AETERNA BATCH OSSZESITO ===")
    for line in format_batch_summary(run_summaries):
        print_func(line)


def run_seed_batch(
    profile_name: str,
    *,
    seed_values: Sequence[int],
    overrides: Optional[Dict] = None,
    xlsx_path: str = DEFAULT_XLSX_PATH,
    base_dir: str = PROGRAM_MAPPA,
    print_func: Callable[[str], None] = print,
) -> List[Dict]:
    summaries: List[Dict] = []
    for seed in seed_values:
        seed_overrides = dict(overrides or {})
        seed_overrides["random_seed"] = seed
        config = build_config_from_profile(profile_name, overrides=seed_overrides)
        create_logger(config, base_dir=base_dir, logger=naplo)
        summary = futtat_szimulaciot(xlsx_path, config=config)
        summaries.append(summary or {
            "games": config.games,
            "random_seed": config.random_seed,
            "player1_realm": config.player1_realm,
            "player2_realm": config.player2_realm,
            "p1_wins": 0,
            "p2_wins": 0,
            "draws": 0,
            "total_turns": 0,
            "average_turns": 0.0,
        })

    _print_batch_summary(summaries, print_func=print_func)
    return summaries


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AETERNA konnyu tesztlauncher a dokumentalt tesztprofilokhoz."
    )
    parser.add_argument("--profile", choices=sorted(PROFILE_PRESETS.keys()), help="Elore definialt tesztprofil neve.")
    parser.add_argument("--seed", help="Seed felulirasa.")
    parser.add_argument("--runs", type=int, help="Futasok szamanak felulirasa.")
    parser.add_argument("--p1", dest="player1_realm", help="P1 birodalom felulirasa.")
    parser.add_argument("--p2", dest="player2_realm", help="P2 birodalom felulirasa.")
    parser.add_argument("--seed-list", help="Tobb seed vesszovel elvalasztva, pl. 101,102,103.")
    parser.add_argument("--seed-start", type=int, help="Batch seed kezdoertek.")
    parser.add_argument("--seed-count", type=int, help="Batch seed darabszam.")
    parser.add_argument("--last-run", action="store_true", help="Az utolso launcher-beallitas ujrafuttatasa.")
    parser.add_argument("--list-profiles", action="store_true", help="Az elerheto profilok kilistazasa.")
    parser.add_argument("--xlsx-path", default=DEFAULT_XLSX_PATH, help="A cards.xlsx eleresi utja.")
    parser.add_argument("--base-dir", default=PROGRAM_MAPPA, help="A logok alapkonyvtara.")
    return parser


def _cli_overrides_from_args(args) -> Dict:
    overrides = {}
    if args.runs is not None:
        overrides["games"] = args.runs
    if args.seed is not None:
        overrides["random_seed"] = args.seed
    if args.player1_realm is not None:
        overrides["player1_realm"] = args.player1_realm
    if args.player2_realm is not None:
        overrides["player2_realm"] = args.player2_realm
    return overrides


def _print_profiles(print_func: Callable[[str], None] = print):
    print_func("Elerheto tesztprofilok:")
    for profile_name, profile in PROFILE_PRESETS.items():
        print_func(f"- {profile_name}: {profile['label']} | {profile['description']}")


def _available_realms_hint(xlsx_path: str) -> str:
    try:
        cards = kartyak_betoltese_xlsx(xlsx_path)
        realms = sorted(
            {
                getattr(card, "birodalom", None)
                for card in cards
                if getattr(card, "birodalom", None) not in (None, "", "None", "-")
            }
        )
        if realms:
            return ", ".join(realms)
    except Exception:
        pass
    return "random vagy konkret birodalomnev a cards.xlsx alapjan"


def launch_non_interactive(
    *,
    profile_name: Optional[str] = None,
    overrides: Optional[Dict] = None,
    use_last_run: bool = False,
    seed_values: Optional[Sequence[int]] = None,
    xlsx_path: str = DEFAULT_XLSX_PATH,
    base_dir: str = PROGRAM_MAPPA,
    settings_path: str = LAST_SETTINGS_PATH,
    print_func: Callable[[str], None] = print,
) -> SimulationConfig:
    if use_last_run:
        last_settings = load_last_settings(settings_path)
        if not last_settings:
            raise ValueError("Nincs elerheto utolso launcher-beallitas.")
        profile_name = last_settings["profile_name"]
        merged_overrides = dict(last_settings.get("overrides") or {})
        merged_overrides.update(dict(overrides or {}))
        if seed_values:
            run_seed_batch(
                profile_name,
                seed_values=seed_values,
                overrides=merged_overrides,
                xlsx_path=xlsx_path,
                base_dir=base_dir,
                print_func=print_func,
            )
            return build_config_from_profile(profile_name, overrides={**merged_overrides, "random_seed": seed_values[-1]})
        config = build_config_from_profile(profile_name, overrides=merged_overrides)
        create_logger(config, base_dir=base_dir, logger=naplo)
        futtat_szimulaciot(xlsx_path, config=config)
        return config

    if not profile_name:
        raise ValueError("Non-interactive inditashoz profile nev szukseges.")

    save_last_settings({"profile_name": profile_name, "overrides": dict(overrides or {})}, settings_path)
    if seed_values:
        run_seed_batch(
            profile_name,
            seed_values=seed_values,
            overrides=overrides,
            xlsx_path=xlsx_path,
            base_dir=base_dir,
            print_func=print_func,
        )
        return build_config_from_profile(profile_name, overrides={**dict(overrides or {}), "random_seed": seed_values[-1]})
    return run_test_profile(profile_name, overrides=overrides, xlsx_path=xlsx_path, base_dir=base_dir)


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
    last_result = None
    profile_names = list(presets.keys())
    realm_hint = _available_realms_hint(xlsx_path)

    while True:
        last_settings = load_last_settings(settings_path)

        print_func("=== AETERNA TESZTLAUNCHER ===")
        print_func("Valassz tesztprofilt, vagy futtasd ujra az utolso sikeres launcher-beallitast.")
        for index, (profile_name, profile) in enumerate(presets.items(), start=1):
            print_func(f"{index}. {profile['label']} - {profile['description']}")
        if last_settings:
            print_func("R. Utolso hasznalt beallitas ujrafuttatasa (ugyanazzal a profillal es override-okkal)")
        print_func("Q. Kilepes")

        choice = input_func("Valasztas (1-5, R, Q): ").strip().lower()
        if choice == "q":
            return last_result

        if choice == "r" and last_settings:
            config = build_config_from_profile(last_settings["profile_name"], overrides=last_settings.get("overrides"))
            create_logger(config, base_dir=base_dir, logger=naplo)
            futtat_szimulaciot(xlsx_path, config=config)
            last_result = config
            print_func("Futas kesz. Visszateres a fomenube...")
            continue

        try:
            selected_index = int(choice) - 1
            profile_name = profile_names[selected_index]
        except Exception:
            print_func("Ervenytelen valasztas. Valassz profilt szammal, vagy hasznald az R / Q opciot.")
            continue

        base_settings = deepcopy(presets[profile_name]["settings"])
        print_func(f"Kivalasztott profil: {presets[profile_name]['label']}")
        print_func(f"Rovid leiras: {presets[profile_name]['description']}")
        print_func("A futasszam pozitiv egesz szam. Uresen hagyva a profil alapertelmezese marad.")
        print_func("A seed uresen hagyhato. Uresen a profil seedje marad, vagy random lesz, ha a profil is ugy adja.")
        print_func(f"Birodalom opciok: {realm_hint}. Ures vagy 'random' eseten veletlen valasztas marad.")

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
        last_result = config
        print_func("Futas kesz. Visszateres a fomenube...")


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    input_func: Callable[[str], str] = input,
    print_func: Callable[[str], None] = print,
    settings_path: str = LAST_SETTINGS_PATH,
):
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    seed_values = parse_seed_batch_args(args.seed_list, args.seed_start, args.seed_count)

    if args.list_profiles:
        _print_profiles(print_func=print_func)
        return None

    overrides = _cli_overrides_from_args(args)

    if args.last_run:
        return launch_non_interactive(
            use_last_run=True,
            overrides=overrides,
            seed_values=seed_values,
            xlsx_path=args.xlsx_path,
            base_dir=args.base_dir,
            settings_path=settings_path,
            print_func=print_func,
        )

    if args.profile:
        return launch_non_interactive(
            profile_name=args.profile,
            overrides=overrides,
            seed_values=seed_values,
            xlsx_path=args.xlsx_path,
            base_dir=args.base_dir,
            settings_path=settings_path,
            print_func=print_func,
        )

    return launch_interactive(
        xlsx_path=args.xlsx_path,
        base_dir=args.base_dir,
        input_func=input_func,
        print_func=print_func,
        settings_path=settings_path,
    )


if __name__ == "__main__":
    main()
