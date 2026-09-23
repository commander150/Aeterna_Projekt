# AETERNA Game Engine – Checkpoint Index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.8
**Dátum:** 2026-09-05
**Státusz:** aktív checkpoint-index
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9`
**Production kódbázis:** `0862e1002dbef81ee203852714d377592272a0e9` – Combat + Pecsét C0–C6 close

Ez a dokumentum elválasztja az aktív technikai folytatási pontot, a történeti mérföldkőnaplót és a hosszú távú termékcélt.

---

## 1. Aktív technikai checkpoint

- `../../../project/status/checkpoints/ENGINE_CHECKPOINT.md` v2.0

Szerepe:

- elsődleges technikai folytatási pont;
- Python reference, sidecar, C# proof és production folytonosság;
- lezárt runtime-döntés;
- C.5A/C.5B státusz;
- korábbi production gameplay foundation slice;
- Explicit Phase Foundation v1;
- Reaction / Priority Foundation v1;
- Combat + Pecsét Foundation C0–C6;
- megőrzendő invariánsok;
- learning/synthesis/OQ dokumentációs handoff;
- VS1 / M6 technical handoff;
- következő biztonságos technikai lépés.

A korábbi checkpointelődök történeti állapotban maradnak; nem aktív authority-k.

## 2. Történeti checkpointnapló

- `CHECKPOINTS.md` v1.4

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
- korábbi production gameplay foundation / Explicit Phase Foundation;
- Reaction / Priority Foundation v1;
- Combat + Pecsét Foundation C0–C6;
- későbbi fő mérföldkövek.

Nem aktív tasklista.

## 3. Hosszú távú termékcél

- `../AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

Current termékút:

```text
VS1 / M6
→ szükséges köztes mérföldkövek
→ AETERNA 0.0.1
```

A 0.0.1 az első zárt, játszható product target, nem napi technikai checkpoint.

## 4. Checkpointkészítési szabály

Az aktív `../../../project/status/checkpoints/ENGINE_CHECKPOINT.md` frissítendő, amikor:

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

1. `../../../project/status/checkpoints/ENGINE_CHECKPOINT.md`;
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

- jelen `README.md` v1.8;
- `../../../project/status/checkpoints/ENGINE_CHECKPOINT.md` v2.0;
- `CHECKPOINTS.md` v1.4.

Szinkronizációs dokumentációs / production bázis:

`0862e1002dbef81ee203852714d377592272a0e9`

Lezárt current foundation:

- Explicit Phase Foundation v1;
- Reaction / Priority Foundation v1;
- Combat + Pecsét Foundation C0–C6;
- terminal victory core.

Current következő major goal:

`VS1 / M6 readiness`

A három checkpointfájl szerepe eltérő, ezért a mérföldkő részleges ismétlése nem fölösleges tartalmi duplikáció.
