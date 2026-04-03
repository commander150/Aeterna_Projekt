import os
from openpyxl import load_workbook
from utils.logger import naplo
from engine.card import Kartya

def kartyak_betoltese_xlsx(fajl_utvonal):
    if not os.path.exists(fajl_utvonal):
        naplo.ir(f"HIBA: Nem található a kártyafájl itt: {fajl_utvonal}")
        return []

    naplo.ir(f"Excel betöltése: {fajl_utvonal}")
    wb = load_workbook(fajl_utvonal, data_only=True)
    osszes_kartya = []

    for lap_nev in wb.sheetnames:
        sheet = wb[lap_nev]
        for sor in sheet.iter_rows(min_row=2, values_only=True):
            if sor and sor[0]: # Ha a sornak van első cellája
                
                # BIZTONSÁGI SZŰRÉS: Ha ez egy fejléc sor, ugorjuk át!
                if str(sor[0]).strip() == "Kártya név" or str(sor[2]).strip() == "Birodalom":
                    continue
                    
                osszes_kartya.append(Kartya(sor))

    naplo.ir(f"Sikeresen betöltve {len(osszes_kartya)} kártya.")
    return osszes_kartya