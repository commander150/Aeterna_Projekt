# Aeterna Projekt

Az **AETERNA** saját fejlesztésű fizikai és digitális gyűjtögetős kártyajáték-projekt.

## Elsődleges belépési pontok

- **Aktuális projektállapot és következő lépés:**  
  `Aeterna dokumentációk/AETERNA_AKTUALIS_PROJEKTALLAPOT.md`
- **Projekt- és fájltérkép:**  
  `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ.md`
- **Technikai mérföldkőnapló:**  
  `Aeterna game engine/docs/checkpoints/CHECKPOINTS.md`
- **Game Engine dokumentációs index:**  
  `Aeterna game engine/docs/README.md`
- **Külső learning projektek:**  
  `learning/`

## Hivatalos szabály- és adatforrások

1. `Aeterna dokumentációk/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
2. `Aeterna dokumentációk/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`
3. `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`
4. `Aeterna dokumentációk/LOOKUPS.xlsx`

A két hivatalos főforrás az elsődleges játékszabályforrás. A kód, a runtime package,
a learning anyagok és a régi dokumentumok nem írhatják felül őket.

## Elfogadott digitális architektúra

- **Godot / GDScript:** vizuális kliens, UI, input, animáció és debug.
- **C# / .NET:** az egyetlen production authoritative rules engine.
- **Python:** adat-, audit-, fixture-, AI-, batch- és elemzőtooling, valamint reference engine.

## Repository fő területei

- `Aeterna dokumentációk/` – szabály- és adatforrások, aktuális projektállapot.
- `Aeterna game engine/` – C# engine, Python tooling/reference, Godot kliens és technikai dokumentáció.
- `learning/` – külső projektek AETERNA-központú elemzései.
- `Archive/` – történeti anyagok; nem aktív authority.

## Dokumentációs működés

A gyorsan változó aktuális állapot csak az
`AETERNA_AKTUALIS_PROJEKTALLAPOT.md` fájlban szerepelhet.

Egy elfogadott mérföldkő normál esetben csak két operatív dokumentumot érint:

1. az aktuális projektállapot frissítése;
2. egy új, append-only bejegyzés a `CHECKPOINTS.md` végén.

A README-k nem tartalmaznak commitfüggő roadmapet vagy részletes státuszlistát.
