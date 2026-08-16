# AETERNA Game Engine – Checkpoint Index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.6
**Dátum:** 2026-08-16
**Státusz:** aktív checkpoint-index
**Szinkronizációs repository-bázis:** `7af5bf7fec7b762ec41d1368b072ff6a3d818f5e`
**Production kódbázis:** `2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

Ez a dokumentum elválasztja az aktív technikai folytatási pontot, a történeti mérföldkőnaplót és a hosszú távú termékcélt.

---

## 1. Aktív technikai checkpoint

- `ENGINE_CHECKPOINT.md`

Szerepe:

- elsődleges technikai folytatási pont;
- Python reference, sidecar, C# proof és production folytonosság;
- lezárt runtime-döntés;
- C.5A/C.5B státusz;
- production gameplay vertical slice;
- Explicit Phase Foundation;
- megőrzendő invariánsok;
- learning/synthesis/OQ dokumentációs handoff;
- current Reaction/Priority contract state;
- következő biztonságos technikai lépés.

A korábbi checkpointelődök történeti állapotban maradnak; nem aktív authority-k.

---

## 2. Történeti checkpointnapló

- `CHECKPOINTS.md`

Szerepe a fő technikai mérföldkövek időrendi rövid megőrzése:

- runtime package;
- exporter;
- Godot loader;
- Python reference;
- sidecar proof;
- C# proof;
- runtime-döntés;
- C.5A;
- C.5B;
- első production gameplay vertical slice / Explicit Phase Foundation;
- későbbi fő mérföldkövek.

Nem aktív tasklista.

---

## 3. Hosszú távú termékcél

- `../AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

Ez a későbbi első zárt, játszható tesztkiadás célállapota, nem technikai checkpoint.

---

## 4. Checkpointkészítési szabály

Az aktív `ENGINE_CHECKPOINT.md` frissítendő, amikor:

- érdemi technikai szakasz lezárult;
- authority vagy architecture döntés változott;
- fontos dokumentációs átadás történt;
- új beszélgetés előtt biztonságos folytatási pont kell;
- production mérföldkő teljesült.

Nem készül új dátumozott checkpoint minden kisebb feladathoz.

A `CHECKPOINTS.md` csak nagy, lezárt mérföldkő után kap új történeti bejegyzést.

---

## 5. Dokumentumelsőbbség

Technikai folytatás:

1. `ENGINE_CHECKPOINT.md`;
2. aktuális projektterv;
3. aktuális projekt-térkép;
4. `ARCHITECTURE.md` és `TECHNOLOGY_DECISIONS.md`;
5. aktuális status/contract dokumentumok;
6. Open Questions;
7. `CHECKPOINTS.md`.

Szabályi kérdésben a hivatalos játékszabályforrás mindegyik fölött áll.

---

## 6. Aktuális checkpointállapot

Aktív:

- jelen `README.md`;
- `ENGINE_CHECKPOINT.md` v1.8;
- `CHECKPOINTS.md` v1.3.

Szinkronizációs dokumentációs bázis:

`743c00d85ddc60bbbc70715fefab8ffc9dacbdae`

Aktuális production implementation-bázis:

`2608345b61526097fc0b118f05461f92cfed0a95`

A három fájl szerepe eltérő, ezért a mérföldkő részleges ismétlése nem fölösleges tartalmi duplikáció.
