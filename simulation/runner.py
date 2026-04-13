import random
import traceback
from engine.effect_diagnostics_v2 import install_effect_diagnostics
from engine.config import set_active_engine_config
from engine.logging_utils import log_block_reason, log_shared_path
from utils.logger import naplo
from stats.analyzer import stats
from data.loader import kartyak_betoltese_xlsx
from engine.game import AeternaSzimulacio
from simulation.config import SimulationConfig, normalize_realm_name
from simulation.deck_presets import resolve_deck_preset_cards


def _elerheto_birodalmak(kartyak):
    return sorted({
        k.birodalom for k in kartyak
        if k.birodalom and k.birodalom != "None"
    })


def _valassz_birodalmat(kivant, elerheto_birodalmak, random_fallback=True, tiltott=None):
    tiltott = set(tiltott or [])
    canonical_lookup = {str(b).lower(): b for b in elerheto_birodalmak}
    normalized_requested = normalize_realm_name(kivant)
    resolved_requested = canonical_lookup.get(str(normalized_requested).lower()) if normalized_requested else None

    if normalized_requested:
        if resolved_requested and resolved_requested not in tiltott:
            return resolved_requested
        if not random_fallback:
            available = ", ".join(elerheto_birodalmak)
            raise ValueError(
                f"Hiba: a kert birodalom nem elerheto: {kivant}. "
                f"Elerheto opciok: {available}"
            )

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
        f"p1_nev={p1.nev} | p1_birodalom={p1.birodalom} | p1_preset={getattr(p1, 'deck_preset_name', None) or 'none'} | p1_pecset={len(p1.pecsetek)} | p1_pakli={len(p1.pakli)} | p1_kez={len(p1.kez)} | p1_temeto={len(p1.temeto)} | p1_board={_count_board_entities(p1)}",
        f"p2_nev={p2.nev} | p2_birodalom={p2.birodalom} | p2_preset={getattr(p2, 'deck_preset_name', None) or 'none'} | p2_pecset={len(p2.pecsetek)} | p2_pakli={len(p2.pakli)} | p2_kez={len(p2.kez)} | p2_temeto={len(p2.temeto)} | p2_board={_count_board_entities(p2)}",
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
        "player1_deck_preset": config.player1_deck_preset,
        "player2_deck_preset": config.player2_deck_preset,
        "p1_wins": p1_wins,
        "p2_wins": p2_wins,
        "draws": draws,
        "total_turns": total_turns,
        "average_turns": (total_turns / games_played) if games_played else 0.0,
    }


def _empty_run_metrics():
    return {
        "spells_cast": 0,
        "summons": 0,
        "traps_played": 0,
        "traps_triggered": 0,
        "seal_breaks": 0,
        "source_placements": 0,
        "destroyed_units": 0,
    }


def _merge_card_counter(target, source):
    if not isinstance(source, dict):
        return
    for card_name, count in source.items():
        if not card_name:
            continue
        target[card_name] = int(target.get(card_name, 0)) + int(count or 0)


def _winner_player_name(nyertes):
    winner_name = getattr(nyertes, "nev", nyertes)
    if winner_name in {"Jatekos_1", "Jatekos_2"}:
        return winner_name
    return None


def _resolve_player_setup(config, player_key, available_realms, cards):
    preset_name = getattr(config, f"{player_key}_deck_preset", None)
    requested_realm = getattr(config, f"{player_key}_realm", None)

    if preset_name:
        preset = resolve_deck_preset_cards(preset_name, cards)
        preset_realm = normalize_realm_name(preset["realm"])
        if requested_realm and normalize_realm_name(requested_realm) != preset_realm:
            raise ValueError(
                f"Hiba: a megadott realm ({requested_realm}) nem egyezik a preset realmjevel "
                f"({preset_realm}) a(z) {preset_name} presetnel."
            )
        return {
            "realm": preset_realm,
            "deck": preset["cards"],
            "preset_name": preset["name"],
        }

    chosen_realm = _valassz_birodalmat(
        requested_realm,
        available_realms,
        random_fallback=config.random_realm_fallback,
    )
    return {
        "realm": chosen_realm,
        "deck": None,
        "preset_name": None,
    }

def futtat_szimulaciot(xlsx_utvonal, meccsek_szama=3, config=None):
    try:
        install_effect_diagnostics()
        config = _resolve_config(config, meccsek_szama)
        before_stats = _capture_stats_snapshot()
        run_metrics = _empty_run_metrics()
        winner_played_cards = {}
        last_p1_setup = None
        last_p2_setup = None
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
            p1_setup = _resolve_player_setup(config, "player1", birodalmak, kartyak)

            p2_requested_realm = config.player2_realm
            p2_preset = config.player2_deck_preset
            if p2_preset:
                p2_setup = _resolve_player_setup(config, "player2", birodalmak, kartyak)
            else:
                b2 = _valassz_birodalmat(
                    p2_requested_realm,
                    birodalmak,
                    random_fallback=config.random_realm_fallback,
                    tiltott=[] if p2_requested_realm else [p1_setup["realm"]],
                )
                p2_setup = {
                    "realm": b2,
                    "deck": None,
                    "preset_name": None,
                }
            last_p1_setup = p1_setup
            last_p2_setup = p2_setup

            naplo.separator(f"{i+1}. JATEK INDUL")
            naplo.ir(f"--- {i+1}. JÁTÉK INDUL: {p1_setup['realm']} vs {p2_setup['realm']} ---")
            naplo.tech(
                "MATCH",
                f"index={i+1} | p1={p1_setup['realm']} | p2={p2_setup['realm']} | "
                f"p1_preset={p1_setup['preset_name'] or 'none'} | p2_preset={p2_setup['preset_name'] or 'none'} | "
                f"seed={config.random_seed} | scenario={config.scenario or 'none'}"
            )
            jatek = AeternaSzimulacio(
                p1_setup["realm"],
                p2_setup["realm"],
                kartyak,
                engine_config=engine_config,
                player1_deck=p1_setup["deck"],
                player2_deck=p2_setup["deck"],
                player1_preset_name=p1_setup["preset_name"],
                player2_preset_name=p2_setup["preset_name"],
            )
            jatek.log_metrics = {
                "spells_cast": 0,
                "summons": 0,
                "traps_played": 0,
                "traps_triggered": 0,
                "seal_breaks": 0,
                "source_placements": 0,
                "destroyed_units": 0,
                "played_cards": {},
                "played_cards_by_player": {},
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
            for metric_name in run_metrics:
                run_metrics[metric_name] += int(jatek.log_metrics.get(metric_name, 0))
            winning_player_name = _winner_player_name(nyertes)
            if winning_player_name:
                _merge_card_counter(
                    winner_played_cards,
                    (jatek.log_metrics.get("played_cards_by_player") or {}).get(winning_player_name, {}),
                )

        stats.osszesites_mentese()
        naplo.summary(
            "FUTAS VEGE",
            [
                f"jatekok_szama={config.games}",
                f"random_seed={config.random_seed}",
                f"run_mode={engine_config.run_mode}",
                f"player1_realm={(last_p1_setup or {}).get('realm', config.player1_realm or 'random')}",
                f"player2_realm={(last_p2_setup or {}).get('realm', config.player2_realm or 'random')}",
                f"player1_preset={config.player1_deck_preset or 'none'}",
                f"player2_preset={config.player2_deck_preset or 'none'}",
                f"scenario={config.scenario or 'none'}",
                f"osszes_kor={stats.osszes_kor}",
            ],
        )
        summary = _build_run_summary(config, before_stats, _capture_stats_snapshot())
        summary["metrics"] = dict(run_metrics)
        summary["winner_played_cards"] = dict(
            sorted(winner_played_cards.items(), key=lambda item: (-item[1], item[0]))
        )
        return summary

    except Exception as exc:
        naplo.ir("\n" + "!"*40)
        naplo.ir("PROGRAM LEÁLLT - KRITIKUS HIBA:")
        naplo.ir(f"Hiba oka: {exc}")
        traceback.print_exc()
        naplo.ir("!"*40)
        return None

