# AETERNA Game Engine – Dokumentációs index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.3  
**Dátum:** 2026-07-15  
**Státusz:** aktív engine-dokumentációs index

Ez a fájl az `Aeterna game engine/docs/` dokumentumainak szerepét, elsőbbségét és jelenlegi státuszát rögzíti.

Fontos pontosítás:

- a Python minimal engine a jelenlegi működő authoritative fejlesztési bázis;
- a Python backend + Godot frontend a legerősebb hosszú távú jelölt;
- a végleges runtime/backend és packaging architektúra még nyitott technológiai kapu;
- az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó;
- a tanulóprogram-audit és a Python–GDScript comparison nem obsolete.

---

## 1. Elsődleges aktuális dokumentumok

### Hosszú távú termékcél

- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

### Aktuális technikai folytatási pont

- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

### Aktuális architektúra

- `ARCHITECTURE.md`

Szerepe:

- jelenlegi működő Python-engine architektúra;
- stabil contract- és réteghatárok;
- nyitott végleges Python–Godot/GDScript architektúra.

### Aktuális technológiai döntések

- `TECHNOLOGY_DECISIONS.md`

Szerepe:

- jelenlegi munkamodell;
- technológiai jelöltek;
- tanulóprogram-audit;
- Python–GDScript comparison;
- bridge és packaging döntési kapuk.

### Aktuális rövid döntéstérkép

- `DECISION_MAP.md`

### Aktuális contract-státusz

- `CURRENT_CONTRACT_STATUS.md`

### Contract-specifikáció migrációs térkép

- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`

### Aktuális runtime package-státusz

- `CURRENT_RUNTIME_PACKAGE_STATUS.md`

### Aktuális prototípus-státusz

- `CURRENT_PROTOTYPE_STATUS.md`

### Aktuális közeli kérdések

- `CURRENT_OPEN_QUESTIONS.md`

Ez már tartalmazza:

- a tanulóprogram-forrásauditot;
- a Python–GDScript comparison scope kérdését;
- a Python–Godot integration prototype kaput;
- a Wellspring és Beáramlás közeli engine-kérdéseit.

---

## 2. Open Questions dokumentumpár

### `OPEN_QUESTIONS.md`

Státusz:

- `FULL_HISTORICAL_QUESTION_REGISTRY`

Szerepe:

- az eredeti OQ-azonosítók és kérdések megőrzése;
- minden régi és hosszú távú döntési kapu nyilvántartása.

### `OPEN_QUESTIONS_DECISIONS.md`

Státusz:

- `ANSWER_AND_DECISION_DIRECTION_REGISTRY`

Szerepe:

- az OQ-khoz adott részletes válaszok;
- részben megválaszolt kérdések;
- javasolt státuszfrissítések;
- célfájlok és átvezetési irányok.

Használati szabály:

- egyik dokumentum sem olvasandó a másik nélkül;
- az eredeti kérdés megmarad az `OPEN_QUESTIONS.md` fájlban;
- a részletes válasz a decisions fájlban található;
- a napi fejlesztési kivonat a `CURRENT_OPEN_QUESTIONS.md`.

Az architektúra-kérdések jelenlegi helyes státusza:

- részben megválaszolt;
- Python a jelenlegi munkabázis;
- a végleges technológiai modell további prototípust és összehasonlítást igényel.

---

## 3. Hosszú specifikációk és referencia-dokumentumok

### `CONTRACT_SPECIFICATION.md`

- `LONG_FORM_DESIGN_REFERENCE`
- aktuális státusz: `CURRENT_CONTRACT_STATUS.md`
- eltérések: `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`

### `RUNTIME_PACKAGE_SPECIFICATION.md`

- `LONG_FORM_DESIGN_AND_PIPELINE_REFERENCE`
- aktuális státusz: `CURRENT_RUNTIME_PACKAGE_STATUS.md`

### `PROTOTYPE_PLANS.md`

- `HISTORICAL_AND_FUTURE_PROTOTYPE_REFERENCE`
- aktuális státusz: `CURRENT_PROTOTYPE_STATUS.md`

A benne szereplő GDScript rules-service és comparison tervek nem tekintendők sem közvetlen aktív implementációnak, sem végleg obsolete iránynak. Pontos státuszuk a current prototype dokumentumban található.

### `ABILITY_MODULE_SYSTEM.md`

- `PLANNED_SYSTEM_REFERENCE`
- ability executor jelenleg nincs implementálva.

---

## 4. Checkpointok

- `checkpoints/README.md` – checkpoint-index és státusztérkép
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md` – aktuális Python engine folytatási pont
- `checkpoints/CHECKPOINTS.md` – történeti technikai napló

A checkpoint a jelenlegi engine-implementáció állapotát rögzíti, nem zárja le automatikusan a végleges product runtime-technológiát.

---

## 5. Dokumentumelsőbbség

Engine-fejlesztésnél:

1. hivatalos 1.4v szabályforrások;
2. v6.0 projektterv;
3. `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`;
4. `ARCHITECTURE.md`;
5. `TECHNOLOGY_DECISIONS.md`;
6. `DECISION_MAP.md`;
7. `CURRENT_CONTRACT_STATUS.md`;
8. `CURRENT_RUNTIME_PACKAGE_STATUS.md`;
9. `CURRENT_PROTOTYPE_STATUS.md`;
10. `CURRENT_OPEN_QUESTIONS.md`;
11. `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md` együtt;
12. hosszú specifikációk;
13. történeti checkpointok és régi dokumentumok.

A 0.0.1 célállapot a hosszú távú termékirányt adja, de nem helyettesíti az aktuális technikai checkpointot és nem dönti el önmagában a runtime-technológiát.

---

## 6. Következő dokumentációs feladatok

- az Open Questions és Decisions teljes OQ-azonosítós triázsa;
- tanulóprogram-forrásleltár;
- projektenkénti technológiai audit;
- Python–Godot/GDScript comparison scope;
- az `ABILITY_MODULE_SYSTEM.md` felülvizsgálata;
- a hosszú contract-specifikáció fokozatos konszolidációja;
- a történeti checkpointnapló formázási tisztítása.

Ezek közül a tanulóprogram-audit a végleges technológiai döntést blokkolja, de a Wellspring és más belső Python engine-alapok fejlesztését nem.
