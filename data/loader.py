import os
from openpyxl import load_workbook
from utils.text import normalize_lookup_text
from utils.logger import naplo
from engine.card import Kartya


def _normalize_header_name(header):
    normalized = normalize_lookup_text(header)
    return normalized.replace(" ", "_")


def _row_to_mapping(headers, row):
    mapping = {}
    for index, header in enumerate(headers):
        if not header:
            continue
        mapping[header] = row[index] if index < len(row) else None
    return mapping


def kartyak_betoltese_xlsx(fajl_utvonal):
    if not os.path.exists(fajl_utvonal):
        naplo.ir(f"HIBA: Nem talalhato a kartyafajl itt: {fajl_utvonal}")
        return []

    naplo.ir(f"Excel betoltese: {fajl_utvonal}")
    wb = load_workbook(fajl_utvonal, data_only=True)
    osszes_kartya = []

    for lap_nev in wb.sheetnames:
        sheet = wb[lap_nev]
        raw_headers = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
        headers = [_normalize_header_name(value) for value in raw_headers]

        for sor in sheet.iter_rows(min_row=2, values_only=True):
            if not sor or not sor[0]:
                continue

            if str(sor[0]).strip() == "Kartya nev" or (len(sor) > 2 and str(sor[2]).strip() == "Birodalom"):
                continue

            sor_mapping = _row_to_mapping(headers, sor)
            osszes_kartya.append(Kartya(sor_mapping or sor))

    naplo.ir(f"Sikeresen betoltve {len(osszes_kartya)} kartya.")
    return osszes_kartya
