# AETERNA Game Engine – Checkpoint Index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2  
**Dátum:** 2026-07-21  
**Státusz:** aktív checkpoint-index  
**Aktuális repository HEAD:** `32a0cbea24c82dda440f1a053b454ef03949d8ae` – `docs update 2`

Ez a dokumentum elválasztja az aktív technikai folytatási pontot, a történeti mérföldkőnaplót és a hosszú távú termékcélt.

---

## 1. Aktív technikai checkpoint

- `ENGINE_CHECKPOINT.md`

Szerepe:

- elsődleges folytatási pont;
- Python reference, sidecar és C# proof állapot;
- lezárt runtime-döntés;
- C.5A/C.5B státusz;
- dokumentációs cleanup és következő biztonságos lépés.

Felváltja:

- `CURRENT_ENGINE_CHECKPOINT.md`;
- `AETERNA_CURRENT_ENGINE_CHECKPOINT_v1.1_2026-07-20.md`.

A két előd a hivatkozásellenőrzés után eltávolítandó.

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
- C.5A és későbbi mérföldkövek

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

## 6. Aktuális cleanup

Megtartandó:

- `README.md`;
- `ENGINE_CHECKPOINT.md`;
- `CHECKPOINTS.md`.

Eltávolítandó:

- `CURRENT_ENGINE_CHECKPOINT.md`;
- `AETERNA_CURRENT_ENGINE_CHECKPOINT_v1.1_2026-07-20.md`.

A három megtartott fájl szerepe különböző, ezért nem tartalmi duplikáció.
