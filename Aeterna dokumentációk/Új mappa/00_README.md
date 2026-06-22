# AETERNA cards.xlsx szöveges munkakivonat

Forrás: `cards.xlsx`

Export típusa: TSV + JSONL

Cél:
- a kártyaadatok könnyebben olvasható és ellenőrizhető formába hozása;
- az Excelből származó oszlopcsúszások és részleges chat-generálások kockázatának csökkentése;
- későbbi auditoknál stabil forrás használata az Excel közvetlen olvasása helyett.

## Fájlok

- `all_cards.tsv` – minden kártya egyetlen TSV-ben, `Forrás_lap` és `Forrás_sor` oszloppal kiegészítve.
- `all_cards.jsonl` – minden kártya külön JSON objektumként, gépi feldolgozásra.
- `AQUA_working_export.tsv` – csak az AQUA lapok, a következő munkafázishoz.
- `cards_by_realm/*.tsv` – Birodalmonként külön TSV.
- `cards_export_summary.json` – sor-, oszlop-, típus- és klánszintű összesítés.

## Használati szabály

A jövőben a chatben nem kell 10 vagy több teljes 22 oszlopos sort egyszerre generálni. 
A munkamenetben először mindig erre a kivonatra hivatkozunk, és csak a konkrét módosítandó mezőket / auditbejegyzéseket adjuk meg.

## Fontos

Ez az export nem helyettesíti az Excel-munkafájlt. 
Ez egy olvasási és auditálási segédfájl, amelyből biztonságosabban lehet dolgozni.
