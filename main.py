import os
import traceback
from engine.config import DEFAULT_EXPANSION_FLAGS, DEFAULT_EXPANSION_MODULES
from engine.logging_utils import create_logger
from simulation.config import SimulationConfig
from utils.logger import naplo
from simulation.runner import futtat_szimulaciot

PROGRAM_MAPPA = os.path.dirname(os.path.abspath(__file__))
XLSX_FAJL = os.path.join(PROGRAM_MAPPA, "cards.xlsx")

# =========================
# SZIMULACIOS BEALLITASOK
# Ures ertek vagy None -> alapertelmezett, veletlen viselkedes.
# =========================
SZIMULACIOS_BEALLITASOK = {
    "jatekok_szama": 5,
    "random_seed": 101,
    "jatekos1_birodalom": "Aqua",
    "jatekos2_birodalom": "Aether",
    "veletlen_birodalmak": False,
    "scenario_nev": None,
    "engine_futasi_mod": "core_only",
    "expansion_modulok": dict(DEFAULT_EXPANSION_MODULES),
    "expansion_flagek": dict(DEFAULT_EXPANSION_FLAGS),
    "log_mappa": None,
}


def _config_from_main_settings():
    beallitas = SZIMULACIOS_BEALLITASOK
    return SimulationConfig(
        games=beallitas.get("jatekok_szama") or 3,
        random_seed=beallitas.get("random_seed"),
        player1_realm=beallitas.get("jatekos1_birodalom") or None,
        player2_realm=beallitas.get("jatekos2_birodalom") or None,
        random_realm_fallback=beallitas.get("veletlen_birodalmak", True),
        scenario=beallitas.get("scenario_nev") or None,
        engine_run_mode=beallitas.get("engine_futasi_mod") or "core_only",
        expansion_modules=dict(beallitas.get("expansion_modulok") or {}),
        expansion_flags=dict(beallitas.get("expansion_flagek") or {}),
        log_base_dir=beallitas.get("log_mappa") or None,
    )

if __name__ == "__main__":
    try:
        print("=== AETERNA SZIMULÁTOR INDUL ===")

        config = _config_from_main_settings()
        create_logger(config, base_dir=PROGRAM_MAPPA, logger=naplo)

        print(f"Kártya fájl: {XLSX_FAJL}")

        if not os.path.exists(XLSX_FAJL):
            print("HIBA: cards.xlsx nem található!")
        else:
            print(f"Aktív konfiguráció: {config.describe()}")
            futtat_szimulaciot(XLSX_FAJL, config=config)

        print("\nKész!")

    except Exception as e:
        print("\n!!! HIBA TÖRTÉNT !!!")
        traceback.print_exc()

    input("\nNyomj Entert a kilépéshez...")
