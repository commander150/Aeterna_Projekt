import os
import traceback
from utils.logger import naplo
from simulation.runner import futtat_szimulaciot

PROGRAM_MAPPA = os.path.dirname(os.path.abspath(__file__))
XLSX_FAJL = os.path.join(PROGRAM_MAPPA, "cards.xlsx")

if __name__ == "__main__":
    try:
        print("=== AETERNA SZIMULÁTOR INDUL ===")

        # ÚJ LOG fájl létrehozása
        naplo.uj_log_fajl(PROGRAM_MAPPA)

        print(f"Kártya fájl: {XLSX_FAJL}")

        if not os.path.exists(XLSX_FAJL):
            print("HIBA: cards.xlsx nem található!")
        else:
            futtat_szimulaciot(XLSX_FAJL, meccsek_szama=3)

        print("\nKész!")

    except Exception as e:
        print("\n!!! HIBA TÖRTÉNT !!!")
        traceback.print_exc()

    input("\nNyomj Entert a kilépéshez...")