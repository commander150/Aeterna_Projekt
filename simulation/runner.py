import random
import traceback
from utils.logger import naplo
from stats.analyzer import stats
from data.loader import kartyak_betoltese_xlsx
from engine.game import AeternaSzimulacio

def futtat_szimulaciot(xlsx_utvonal, meccsek_szama=3):
    try:
        kartyak = kartyak_betoltese_xlsx(xlsx_utvonal)
        if not kartyak:
            return

        birodalmak = list(set(k.birodalom for k in kartyak if k.birodalom and k.birodalom != "None"))
        naplo.ir(f"Elérhető birodalmak: {', '.join(birodalmak)}")

        for i in range(meccsek_szama):
            b1 = random.choice(birodalmak)
            masik_birodalmak = [b for b in birodalmak if b != b1]
            b2 = random.choice(masik_birodalmak) if masik_birodalmak else b1

            naplo.ir(f"\n--- {i+1}. JÁTÉK INDUL: {b1} vs {b2} ---")
            jatek = AeternaSzimulacio(b1, b2, kartyak)
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