# XLSX export

Ez egy különálló Python parancssoros program, amely egy `.xlsx` fájl kiválasztott
munkalapját JSONL vagy TSV formátumba exportálja.

## Indítás fájlból

Másold az exportálandó `.xlsx` fájlokat a program `source` mappájába, majd kattints
duplán az `XLSX export indítása.bat` fájlra. A megjelenő választómenüben:

1. válaszd ki az XLSX fájlt;
2. válaszd ki a munkalapot;
3. válaszd ki a JSONL vagy TSV formátumot.

A program kizárólag a saját `source` mappájában keresi és fogadja el az XLSX fájlokat.
A kimenet az `exports` mappába kerül.

## Követelmény

```powershell
python -m pip install openpyxl
```

## Használat

Az interaktív választómenü parancssorból is elindítható:

```powershell
python xlsx_export.py
```

## Profilalapú export

A profilok AETERNA-specifikus lapot, kimeneti fájlnevet, kötelező mezőket és
számmező-normalizálást használnak. Az üres cellák, illetve a `none` értékű
helykitöltők kimaradnak a rekordokból.

```powershell
python xlsx_export.py "source\AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx" --profile runtime_cards
python xlsx_export.py "source\AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx" --profile decklists
python xlsx_export.py "source\AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx" --profile lookups_runtime
```

Elérhető profilok:

- `runtime_cards` → `7. EXPORT_RUNTIME` → `exports/EXPORT_RUNTIME.jsonl`
- `decklists` → `15. PRODUCT_DECKLISTS` → `exports/PRODUCT_DECKLISTS.jsonl`
- `lookups_runtime` → `5A. LOOKUPS_RUNTIME` → `exports/LOOKUPS_RUNTIME.jsonl`
- `lookups_print_product` → `5B. LOOKUPS_PRINT_PRODUCT` → `exports/LOOKUPS_PRINT_PRODUCT.jsonl`
- `lookups_workflow_audit` → `5C. LOOKUPS_WORKFLOW_AUDIT` → `exports/LOOKUPS_WORKFLOW_AUDIT.jsonl`
- `lookups_design_catalog` → `5D. LOOKUPS_DESIGN_CATALOG` → `exports/LOOKUPS_DESIGN_CATALOG.jsonl`
- `generic_sheet` → kézzel megadott lapnév, formátum és kimenet

Ha a profil warningot talál, az export nem áll le. A warningok megjelennek a
konzolban, és külön `.warnings.txt` fájlba is mentődnek a kimenet mellé.

Munkalapok listázása:

```powershell
python xlsx_export.py "source\AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.7v.xlsx" --list-sheets
```

Export automatikus fájlnévvel az `exports` mappába:

```powershell
python xlsx_export.py "source\AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.7v.xlsx" --sheet "3. CARDS_MASTER" --format jsonl
```

Az automatikus fájlnév formája:

```text
<forrásfájl neve>__<munkalap neve>.<formátum>
```

Egyedi kimeneti útvonal is megadható:

```powershell
python xlsx_export.py "source\forrás.xlsx" --profile generic_sheet --sheet Adatok --format tsv --output "saját_kimenet.tsv"
```
