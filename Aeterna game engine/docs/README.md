# AETERNA Game Engine – Dokumentációs index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.5  
**Dátum:** 2026-07-15  
**Státusz:** aktív engine-dokumentációs index

Ez a fájl az `Aeterna game engine/docs/` dokumentumainak szerepét, elsőbbségét és jelenlegi státuszát rögzíti.

Fontos pontosítás:

- a Python minimal engine a jelenlegi működő authoritative referenciaimplementáció;
- a végleges termékruntime még nincs kiválasztva;
- a fő összehasonlítandó jelöltek a Python sidecar és a Godot .NET/C#;
- GDScript szükség esetén kap szűk proofot;
- embedded Python és más nyelvek kutatható, későbbi jelöltek;
- a nyelvváltás nem önálló cél;
- a végleges runtime-nak a termékruntime- és telepítési követelményeket kell teljesítenie;
- a következő Codex-prioritás a runtime-nyelvi és integrációs comparison;
- a jelentős gameplay-engine bővítés a döntési kapu után folytatódik;
- az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó.

---

## 1. Elsődleges aktuális dokumentumok

### Hosszú távú termékcél

- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

### Termékruntime- és telepítési követelmények

- `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`

Szerepe:

- meghatározza a játékosnak átadandó program futtatási élményét;
- rögzíti a megengedett és tiltott külső függőségeket;
- előírja a stabilitási, offline, lifecycle- és packaging próbákat;
- objektív mércét ad minden runtime- és nyelvi jelölt összehasonlításához;
- kimondja, hogy a Python csak akkor váltandó le, ha bizonyítottan akadályozza a termékkövetelmények teljesítését, vagy más modell lényegesen jobb összeredményt ad.

### Aktuális runtime-nyelvi döntési kapu

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

Szerepe:

- a következő Codex-prioritás részletes scope-ja;
- tanulóprogram-audit;
- Python sidecar proof;
- Godot .NET/C# proof;
- opcionális minimal GDScript proof;
- szükség esetén más runtime-jelöltek vizsgálata;
- comparison mátrix;
- elfogadási feltételek;
- döntés utáni migrációs irányok.

A döntési kapu a `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md` követelményei alapján értékelendő.

### Aktuális technikai referencia

- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

Szerepe:

- a működő Python minimal engine tényleges állapota;
- comparison reference és regression oracle;
- nem zárja le a végleges runtime-nyelvet.

### Aktuális architektúra

- `ARCHITECTURE.md`

### Aktuális technológiai döntések

- `TECHNOLOGY_DECISIONS.md`

Szerepe:

- jelenlegi Python referencia;
- Python sidecar és C# fő jelöltek;
- GDScript, C++, embedded Python és más jelöltek státusza;
- tanulóprogram-audit;
- bridge és packaging kapuk.

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

- a runtime language comparison elsődleges prioritását;
- a tanulóprogram-forrásauditot;
- a Python sidecar proofot;
- a Godot .NET/C# proofot;
- a Python–GDScript comparison lehetséges szűk scope-ját;
- a Wellspring és Beáramlás döntés utáni queue-ját.

A következő frissítésben a termékruntime- és telepítési nyitott kérdéseket is hozzá kell kapcsolni.

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

A runtime-technológiai kérdések jelenlegi helyes státusza:

- részben megválaszolt;
- Python a működő referencia;
- Python sidecar és C# a két első proof-jelölt;
- GDScript és más megoldás nincs végleg kizárva;
- a végleges technológiai modellnek teljesítenie kell a termékruntime- és telepítési követelményeket;
- a döntés proofot és emberi jóváhagyást igényel.

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

### `ABILITY_MODULE_SYSTEM.md`

- `PLANNED_SYSTEM_REFERENCE`
- ability executor jelenleg nincs implementálva;
- a következő Codex nélküli dokumentációs audit egyik későbbi célja.

---

## 4. Checkpointok

- `checkpoints/README.md` – checkpoint-index és státusztérkép
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md` – aktuális Python referencia folytatási pont
- `checkpoints/CHECKPOINTS.md` – történeti technikai napló

A checkpoint a jelenlegi engine-implementáció állapotát rögzíti, nem zárja le automatikusan a végleges product runtime-technológiát.

---

## 5. Dokumentumelsőbbség

Engine- és runtime-döntésnél:

1. hivatalos 1.4v szabályforrások;
2. v6.1 projektterv;
3. `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`;
4. `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
5. `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`;
6. `TECHNOLOGY_DECISIONS.md`;
7. `DECISION_MAP.md`;
8. `CURRENT_PROTOTYPE_STATUS.md`;
9. `CURRENT_CONTRACT_STATUS.md`;
10. `CURRENT_RUNTIME_PACKAGE_STATUS.md`;
11. `CURRENT_OPEN_QUESTIONS.md`;
12. `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md` együtt;
13. hosszú specifikációk;
14. történeti checkpointok és régi dokumentumok.

A 0.0.1 célállapot a hosszú távú termékirányt adja. A termékruntime- és telepítési követelményspecifikáció meghatározza az értékelési mércét. A nyelvi döntési kapu ennek alapján hasonlítja össze a jelölteket.

---

## 6. Következő dokumentációs feladatok fontossági sorrendben

1. A termékruntime- és telepítési követelmények nyitott kérdéseinek első triázsa.
2. Az `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` technológiai OQ-azonosítóinak közös frissítése.
3. Tanulóprogram-audit sablon és helyi leltárstruktúra.
4. Licenc- és attributionjegyzék előkészítése.
5. Nyelvfüggetlen comparison fixture és pontozási mátrix dokumentálása.
6. Az `ABILITY_MODULE_SYSTEM.md` felülvizsgálata.
7. A hosszú contract-specifikáció fokozatos konszolidációja.
8. A történeti checkpointnapló formázási tisztítása.

Ha közben a runtime-döntést vagy a 0.0.1 termékcélt közvetlenül veszélyeztető új kérdés merül fel, a sorrend megállítható és a fontosabb döntési kapu előre vehető.

A runtime-nyelvi proof a következő Codex-feladat. Addig a dokumentációs, kutatási, audit- és döntés-előkészítő munkasáv aktív.