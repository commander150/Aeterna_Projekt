import random
import traceback
from engine.effect_diagnostics_v2 import install_effect_diagnostics
from engine.config import set_active_engine_config
from engine.logging_utils import log_block_reason, log_shared_path
from utils.logger import naplo
from stats.analyzer import stats
from data.loader import kartyak_betoltese_xlsx
from engine.game import AeternaSzimulacio
from simulation.config import SimulationConfig


def _elerheto_birodalmak(kartyak):
    return sorted({
        k.birodalom for k in kartyak
        if k.birodalom and k.birodalom != "None"
    })


def _valassz_birodalmat(kivant, elerheto_birodalmak, random_fallback=True, tiltott=None):
    tiltott = set(tiltott or [])

    if kivant:
        if kivant in elerheto_birodalmak and kivant not in tiltott:
            return kivant
        if not random_fallback:
            raise ValueError(f"Hiba: a kert birodalom nem elerheto: {kivant}")

    jeloltek = [b for b in elerheto_birodalmak if b not in tiltott]
    if not jeloltek:
        raise ValueError("Hiba: nincs valaszthato birodalom a szimulaciohoz.")

    return random.choice(jeloltek)


def _resolve_config(config=None, meccsek_szama=3):
    if config is None:
        return SimulationConfig(games=meccsek_szama)
    if isinstance(config, SimulationConfig):
        return config
    if isinstance(config, dict):
        return SimulationConfig(**config)
    raise TypeError("A konfiguracio csak SimulationConfig, dict vagy None lehet.")

def _count_board_entities(player):
    total = 0
    for zone_name in ("horizont", "zenit"):
        zone = getattr(player, zone_name, [])
        for item in zone:
            if getattr(item, "lap", None) is not None:
                total += 1
    return total

def _match_victory_reason(jatek, nyertes):
    p1 = jatek.p1
    p2 = jatek.p2

    if nyertes is None:
        return "timeout_draw"

    if getattr(p1, "overflow_vereseg", False) or getattr(p2, "overflow_vereseg", False):
        return "overflow"

    if len(getattr(p1, "pecsetek", [])) == 0 or len(getattr(p2, "pecsetek", [])) == 0:
        return "seal_break_finish"

    return "unknown"


def _match_summary_lines(jatek, nyertes):
    p1 = jatek.p1
    p2 = jatek.p2
    victory_reason = _match_victory_reason(jatek, nyertes)
    metrics = getattr(jatek, "log_metrics", {}) or {}

    return [
        f"gyoztes={nyertes if nyertes else 'DONTETLEN'}",
        f"gyozelem_oka={victory_reason}",
        f"korok_szama={jatek.kor}",
        f"p1_nev={p1.nev} | p1_birodalom={p1.birodalom} | p1_pecset={len(p1.pecsetek)} | p1_pakli={len(p1.pakli)} | p1_kez={len(p1.kez)} | p1_temeto={len(p1.temeto)} | p1_board={_count_board_entities(p1)}",
        f"p2_nev={p2.nev} | p2_birodalom={p2.birodalom} | p2_pecset={len(p2.pecsetek)} | p2_pakli={len(p2.pakli)} | p2_kez={len(p2.kez)} | p2_temeto={len(p2.temeto)} | p2_board={_count_board_entities(p2)}",
        f"overflow_p1={getattr(p1, 'overflow_vereseg', False)} | overflow_p2={getattr(p2, 'overflow_vereseg', False)}",
        "metrics="
        + " | ".join(
            [
                f"spells_cast={metrics.get('spells_cast', 0)}",
                f"summons={metrics.get('summons', 0)}",
                f"traps_played={metrics.get('traps_played', 0)}",
                f"traps_triggered={metrics.get('traps_triggered', 0)}",
                f"seal_breaks={metrics.get('seal_breaks', 0)}",
                f"source_placements={metrics.get('source_placements', 0)}",
                f"destroyed_units={metrics.get('destroyed_units', 0)}",
            ]
        ),
    ]


def _capture_stats_snapshot():
    return {
        "jatekok_szama": stats.jatekok_szama,
        "p1_gyozelem": stats.p1_gyozelem,
        "p2_gyozelem": stats.p2_gyozelem,
        "dontetlen": stats.dontetlen,
        "osszes_kor": stats.osszes_kor,
    }


def _build_run_summary(config, before_stats, after_stats):
    games_played = after_stats["jatekok_szama"] - before_stats["jatekok_szama"]
    p1_wins = after_stats["p1_gyozelem"] - before_stats["p1_gyozelem"]
    p2_wins = after_stats["p2_gyozelem"] - before_stats["p2_gyozelem"]
    draws = after_stats["dontetlen"] - before_stats["dontetlen"]
    total_turns = after_stats["osszes_kor"] - before_stats["osszes_kor"]

    return {
        "games": games_played,
        "random_seed": config.random_seed,
        "player1_realm": config.player1_realm,
        "player2_realm": config.player2_realm,
        "p1_wins": p1_wins,
        "p2_wins": p2_wins,
        "draws": draws,
        "total_turns": total_turns,
        "average_turns": (total_turns / games_played) if games_played else 0.0,
    }

def futtat_szimulaciot(xlsx_utvonal, meccsek_szama=3, config=None):
    try:
        install_effect_diagnostics()
        config = _resolve_config(config, meccsek_szama)
        before_stats = _capture_stats_snapshot()
        engine_config = set_active_engine_config(config.to_engine_config())

        if config.random_seed is not None:
            random.seed(config.random_seed)
            naplo.tech("SEED", f"random_seed={config.random_seed}")
        else:
            naplo.tech("SEED", "random_seed=None")

        kartyak = kartyak_betoltese_xlsx(xlsx_utvonal)
        if not kartyak:
            return None

        birodalmak = _elerheto_birodalmak(kartyak)
        naplo.ir(f"Elérhető birodalmak: {', '.join(birodalmak)}")

        naplo.ir(f"Aktiv szimulacios konfiguracio: {config.describe()}")
        naplo.ir(f"Aktiv engine konfiguracio: {engine_config.describe()}")

        for i in range(config.games):
            b1 = _valassz_birodalmat(
                config.player1_realm,
                birodalmak,
                random_fallback=config.random_realm_fallback,
            )
            b2 = _valassz_birodalmat(
                config.player2_realm,
                birodalmak,
                random_fallback=config.random_realm_fallback,
                tiltott=[] if config.player2_realm else [b1],
            )

            naplo.separator(f"{i+1}. JATEK INDUL")
            naplo.ir(f"--- {i+1}. JÁTÉK INDUL: {b1} vs {b2} ---")
            naplo.tech(
                "MATCH",
                f"index={i+1} | p1={b1} | p2={b2} | seed={config.random_seed} | scenario={config.scenario or 'none'}"
            )
            jatek = AeternaSzimulacio(b1, b2, kartyak, engine_config=engine_config)
            jatek.log_metrics = {
                "spells_cast": 0,
                "summons": 0,
                "traps_played": 0,
                "traps_triggered": 0,
                "seal_breaks": 0,
                "source_placements": 0,
                "destroyed_units": 0,
            }
            stats.jatekok_szama += 1

            nyertes = None
            while not nyertes and jatek.kor < 100:
                nyertes = jatek.kor_futtatasa()

            stats.rogzit_meccs_eredmenyt(nyertes)

            stats.osszes_kor += jatek.kor
            naplo.ir(f"Játék vége! Győztes: {nyertes if nyertes else 'Döntetlen (Időtúllépés)'}")
            naplo.summary(
                f"MECCS {i+1} VEGE",
                _match_summary_lines(jatek, nyertes),
            )

        stats.osszesites_mentese()
        naplo.summary(
            "FUTAS VEGE",
            [
                f"jatekok_szama={config.games}",
                f"random_seed={config.random_seed}",
                f"run_mode={engine_config.run_mode}",
                f"player1_realm={config.player1_realm or 'random'}",
                f"player2_realm={config.player2_realm or 'random'}",
                f"scenario={config.scenario or 'none'}",
                f"osszes_kor={stats.osszes_kor}",
            ],
        )
        return _build_run_summary(config, before_stats, _capture_stats_snapshot())

    except Exception:
        naplo.ir("\n" + "!"*40)
        naplo.ir("PROGRAM LEÁLLT - KRITIKUS HIBA:")
        traceback.print_exc()
        naplo.ir("!"*40)
        return None

