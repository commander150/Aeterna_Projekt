import random
import traceback
import engine.effect_diagnostics_v2
from engine.config import set_active_engine_config
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

def futtat_szimulaciot(xlsx_utvonal, meccsek_szama=3, config=None):
    try:
        config = _resolve_config(config, meccsek_szama)
        engine_config = set_active_engine_config(config.to_engine_config())

        if config.random_seed is not None:
            random.seed(config.random_seed)

        kartyak = kartyak_betoltese_xlsx(xlsx_utvonal)
        if not kartyak:
            return

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

            naplo.ir(f"\n--- {i+1}. JÁTÉK INDUL: {b1} vs {b2} ---")
            jatek = AeternaSzimulacio(b1, b2, kartyak, engine_config=engine_config)
            stats.jatekok_szama += 1

            nyertes = None
            while not nyertes and jatek.kor < 100:
                nyertes = jatek.kor_futtatasa()

            if nyertes == "Játékos_1": stats.p1_gyozelem += 1
            elif nyertes == "Játékos_2": stats.p2_gyozelem += 1
            
            stats.osszes_kor += jatek.kor
            naplo.ir(f"Játék vége! Győztes: {nyertes if nyertes else 'Döntetlen (Időtúllépés)'}")

        stats.osszesites_mentese()

    except Exception:
        naplo.ir("\n" + "!"*40)
        naplo.ir("PROGRAM LEÁLLT - KRITIKUS HIBA:")
        traceback.print_exc()
        naplo.ir("!"*40)
