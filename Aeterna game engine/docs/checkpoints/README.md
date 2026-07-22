# AETERNA Game Engine – Checkpoint Index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.3\
**Dátum:** 2026-07-22\
**Státusz:** aktív checkpoint-index  
**Ellenőrzött C.5B kódbázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`

Ez a dokumentum elválasztja az aktív technikai folytatási pontot, a történeti mérföldkőnaplót és a hosszú távú termékcélt.

---

## 1. Aktív technikai checkpoint

- `ENGINE_CHECKPOINT.md`

Szerepe:

- elsődleges folytatási pont;
- Python reference, sidecar, C# proof és production foundation állapot;
- lezárt runtime-döntés;
- C.5A/C.5B státusz;
- következő biztonságos gameplay-migrációs lépés.

A korábbi checkpointelődök archív/történeti állapotban maradnak; nem aktív authority-k.

---

## 2. Történeti checkpointnapló

- `CHECKPOINTS.md`

Szerepe:

- runtime package;
- exporter;
- Godot loader;
- sample contract;
- Python reference engine;
- sidecar proof;
- C# proof;
- runtime-döntés;
- C.5A, C.5B és későbbi mérföldkövek

időrendi rövid megőrzése.

Nem aktív tasklista és nem írhatja felül az `ENGINE_CHECKPOINT.md` fájlt.

---

## 3. Hosszú távú termékcél

- `../AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

Ez a későbbi első zárt, játszható tesztkiadás célállapota, nem technikai checkpoint.

---

## 4. Checkpointkészítési szabály

Az aktív `ENGINE_CHECKPOINT.md` frissítendő, amikor:

- érdemi technikai szakasz lezárult;
- authority vagy architecture döntés változott;
- fontos dokumentációs cleanup vagy átadás történt;
- új beszélgetés előtt biztonságos folytatási pont szükséges;
- production mérföldkő teljesült.

Nem készül új dátumozott checkpoint minden kisebb feladathoz.

A `CHECKPOINTS.md` csak nagy, lezárt mérföldkő után kap új történeti bejegyzést.

---

## 5. Dokumentumelsőbbség

1. `ENGINE_CHECKPOINT.md`;
2. aktuális projektterv és projekt-térkép;
3. `ARCHITECTURE.md` és `TECHNOLOGY_DECISIONS.md`;
4. aktuális státuszdokumentumok;
5. `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md`;
6. `CHECKPOINTS.md` történeti napló.

A hivatalos játékszabályforrás mindegyik fölött áll szabályi kérdésben.

---

## 6. Aktuális checkpointállapot

Aktív:

- `README.md`;
- `ENGINE_CHECKPOINT.md`;
- `CHECKPOINTS.md`.

A három fájl szerepe különböző, ezért nem tartalmi duplikáció. A C.5B production foundation mérföldkő a naplóban és az aktív checkpointban is rögzített.
