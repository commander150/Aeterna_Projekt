import os
import traceback
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
    "jatekok_szama": 10,
    "random_seed": 123,
    "jatekos1_birodalom": None,
    "jatekos2_birodalom": None,
    "veletlen_birodalmak": False,
    "scenario_nev": None,
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
    )

if __name__ == "__main__":
    try:
        print("=== AETERNA SZIMULÁTOR INDUL ===")

        # ÚJ LOG fájl létrehozása
        naplo.uj_log_fajl(PROGRAM_MAPPA)

        print(f"Kártya fájl: {XLSX_FAJL}")

        if not os.path.exists(XLSX_FAJL):
            print("HIBA: cards.xlsx nem található!")
        else:
            config = _config_from_main_settings()
            print(f"Aktív konfiguráció: {config.describe()}")
            naplo.ir(f"Startup konfiguráció: {config.describe()}")
            futtat_szimulaciot(XLSX_FAJL, config=config)

        print("\nKész!")

    except Exception as e:
        print("\n!!! HIBA TÖRTÉNT !!!")
        traceback.print_exc()

    input("\nNyomj Entert a kilépéshez...")
