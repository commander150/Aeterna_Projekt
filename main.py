import os
import traceback
from simulation.config import SimulationConfig
from utils.logger import naplo
from simulation.runner import futtat_szimulaciot

PROGRAM_MAPPA = os.path.dirname(os.path.abspath(__file__))
XLSX_FAJL = os.path.join(PROGRAM_MAPPA, "cards.xlsx")


def random_szimulacio_config():
    return SimulationConfig()


def celzott_szimulacio_config():
    return SimulationConfig(
        games=5,
        random_seed=42,
        player1_realm="Solaris",
        player2_realm="Umbra",
        random_realm_fallback=True,
        scenario="celzott-alapteszt",
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
            FUTTATASI_MOD = "random"

            if FUTTATASI_MOD == "targeted":
                config = celzott_szimulacio_config()
            else:
                config = random_szimulacio_config()

            futtat_szimulaciot(XLSX_FAJL, config=config)

        print("\nKész!")

    except Exception as e:
        print("\n!!! HIBA TÖRTÉNT !!!")
        traceback.print_exc()

    input("\nNyomj Entert a kilépéshez...")
