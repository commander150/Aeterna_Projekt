# AETERNA Game Engine – Dokumentációs index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív engine-dokumentációs index

Ez a fájl az `Aeterna game engine/docs/` dokumentumainak szerepét, elsőbbségét és jelenlegi státuszát rögzíti.

---

## 1. Elsődleges aktuális dokumentumok

### Hosszú távú termékcél

- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

Szerepe:

- az első zárt, játszható tesztkiadás célállapota;
- termékmérföldkő;
- nem aktuális technikai schema-verzió.

### Aktuális technikai folytatási pont

- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

Szerepe:

- a jelenlegi Python rules engine tényleges állapota;
- biztonságos programozási folytatási pont;
- tesztállapot és következő feladat.

### Aktuális architektúra

- `ARCHITECTURE.md`

Szerepe:

- Python authoritative rules engine;
- Godot kliens- és UI-réteg;
- runtime package és adatút;
- réteghatárok.

### Aktuális technológiai döntések

- `TECHNOLOGY_DECISIONS.md`

Szerepe:

- Python/Godot felelősségek;
- elfogadott technológiai modell;
- nyitott integrációs és packaging kérdések.

### Aktuális rövid döntéstérkép

- `DECISION_MAP.md`

Szerepe:

- elfogadott irányok;
- közeli fejlesztési sorrend;
- fő nyitott kapuk;
- párhuzamos munkasávok.

### Aktuális contract-státusz

- `CURRENT_CONTRACT_STATUS.md`

Szerepe:

- mi aktív runtime contract;
- mi player-facing projection;
- mi izolált helper;
- mi csak tervezett;
- mely régi sample contract felváltott.

### Aktuális közeli kérdések

- `CURRENT_OPEN_QUESTIONS.md`

Szerepe:

- a következő engine-lépéseket blokkoló döntések;
- rövid napi fejlesztési kérdéslista.

---

## 2. Hosszú specifikációk és referencia-dokumentumok

### `CONTRACT_SPECIFICATION.md`

Státusz:

- `LONG_FORM_DESIGN_REFERENCE`

Szerepe:

- snapshot, legal action, action request/response, event és diagnostics hosszú tervezési anyaga;
- későbbi modellek és mezőjelöltek megőrzése.

Fontos:

- nem minden benne szereplő mező vagy schema aktív runtime contract;
- az aktuális implementációs státusz elsődleges forrása a `CURRENT_CONTRACT_STATUS.md`.

### `RUNTIME_PACKAGE_SPECIFICATION.md`

Státusz:

- `ACTIVE_LONG_FORM_SPECIFICATION`

Szerepe:

- runtime package adatút;
- manifest és package-fájlok;
- source split;
- validation és publish pipeline.

### `ABILITY_MODULE_SYSTEM.md`

Státusz:

- `PLANNED_SYSTEM_REFERENCE`

Szerepe:

- későbbi structured ability és effect engine tervezési anyaga.

Az ability executor jelenleg nincs implementálva.

### `OPEN_QUESTIONS.md`

Státusz:

- `FULL_HISTORICAL_QUESTION_REGISTRY`

Szerepe:

- minden korábbi és hosszú távú kérdés megőrzése;
- dokumentummigráció során elveszni nem hagyott döntési kapuk.

A közeli feladatokhoz a `CURRENT_OPEN_QUESTIONS.md` használatos.

### `PROTOTYPE_PLANS.md`

Státusz:

- `HISTORICAL_AND_FUTURE_PROTOTYPE_REFERENCE`

Szerepe:

- régi és lehetséges technikai prototípusok;
- nem az aktuális szűk engine-task queue.

---

## 3. Checkpointok

### Checkpoint-index

- `checkpoints/README.md`

Szerepe:

- történeti és aktuális checkpointok elhatárolása;
- runtime package–Godot alap és rules-engine szakasz összekapcsolása.

### Aktuális checkpoint

- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

### Történeti checkpointnapló

- `checkpoints/CHECKPOINTS.md`

Státusz:

- `HISTORICAL_TECHNICAL_LOG`

A régi checkpointok saját „következő lépés” szakaszai történeti állapotot rögzítenek, és nem írják felül az aktuális checkpointot.

---

## 4. Dokumentumelsőbbség

Engine-fejlesztésnél:

1. hivatalos 1.4v szabályforrások;
2. v6.0 projektterv;
3. `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`;
4. `ARCHITECTURE.md`;
5. `TECHNOLOGY_DECISIONS.md`;
6. `DECISION_MAP.md`;
7. `CURRENT_CONTRACT_STATUS.md`;
8. `CURRENT_OPEN_QUESTIONS.md`;
9. hosszú specifikációk;
10. történeti checkpointok és régi dokumentumok.

A 0.0.1 célállapot a hosszú távú termékirányt adja, de nem helyettesíti az aktuális technikai checkpointot.

---

## 5. Jelenlegi dokumentációs állapot

2026-07-15-én frissítve:

- projektterv v6.0;
- projekt-térkép v1.3;
- current engine checkpoint;
- architecture v2.0;
- technology decisions v2.0;
- decision map v2.0;
- current contract status;
- current open questions;
- checkpoint index;
- root és engine README.

Továbbra is későbbi feladat:

- a hosszú `CONTRACT_SPECIFICATION.md` tartalmi konszolidációja;
- a `RUNTIME_PACKAGE_SPECIFICATION.md` aktuális source/output státuszának ellenőrzése;
- az `ABILITY_MODULE_SYSTEM.md` felülvizsgálata az első valódi ability implementation előtt;
- a teljes `OPEN_QUESTIONS.md` státuszainak fokozatos átvezetése;
- a történeti checkpointnapló formázási tisztítása.

Ezek nem blokkolják a következő engine-programozási lépést.
