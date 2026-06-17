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
python xlsx_export.py "source\forrás.xlsx" --sheet Adatok --format tsv --output "saját_kimenet.tsv"
```
