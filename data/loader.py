import os
from openpyxl import load_workbook
from utils.text import normalize_lookup_text
from utils.logger import naplo
from engine.card import Kartya


HEADER_ALIASES = {
    "kartya_nev": "kartya_nev",
    "tipus": "kartyatipus",
    "kartyatipus": "kartyatipus",
    "birodalom": "birodalom",
    "klan": "klan",
    "faj": "faj",
    "kaszt": "kaszt",
    "magnitudo": "magnitudo",
    "aura": "aura_koltseg",
    "aura_koltseg": "aura_koltseg",
    "atk": "tamadas",
    "tamadas": "tamadas",
    "hp": "eletero",
    "eletero": "eletero",
    "kepesseg": "kepesseg",
    "kepesseg_canonical": "kepesseg_canonical",
    "kulcsszavak_felismerve": "kulcsszavak_felismerve",
    "trigger_felismerve": "trigger_felismerve",
    "celpont_felismerve": "celpont_felismerve",
    "hatascimkek": "hatascimkek",
    "ertelmezesi_statusz": "ertelmezesi_statusz",
    "engine_megjegyzes": "engine_megjegyzes",
}


def _normalize_header_name(header):
    normalized = normalize_lookup_text(header)
    normalized = normalized.replace(" ", "_")
    return HEADER_ALIASES.get(normalized, normalized)


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

            first_cell = normalize_lookup_text(str(sor[0]).strip()) if sor[0] is not None else ""
            third_cell = normalize_lookup_text(str(sor[2]).strip()) if len(sor) > 2 and sor[2] is not None else ""
            if first_cell in {"kartya_nev", "kartya nev"} or third_cell == "birodalom":
                continue

            sor_mapping = _row_to_mapping(headers, sor)
            osszes_kartya.append(Kartya(sor_mapping or sor))

    naplo.ir(f"Sikeresen betoltve {len(osszes_kartya)} kartya.")
    return osszes_kartya
