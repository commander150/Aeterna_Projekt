# AETERNA Game Engine – Dokumentációs index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.7  
**Dátum:** 2026-07-15  
**Státusz:** aktív engine-dokumentációs index

Ez a fájl az `Aeterna game engine/docs/` dokumentumainak szerepét, elsőbbségét és jelenlegi státuszát rögzíti.

Fontos aktuális állítások:

- a Python minimal engine a működő authoritative referenciaimplementáció;
- a végleges termékruntime még nincs kiválasztva;
- a nyelvváltás nem önálló cél;
- a fő első proof-jelöltek a Python sidecar és a Godot .NET/C#;
- GDScript és más nyelv csak indokolt, szűk proofot kap;
- a runtime-jelöltnek teljesítenie kell a portable Windows-termékkövetelményeket;
- a jelentős gameplay-engine bővítés a runtime-nyelvi döntési kapu után folytatódik;
- az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` történeti dokumentumpár;
- a technológiai OQ-k aktuális státuszát a `CURRENT_OPEN_QUESTIONS.md` tartalmazza.

---

## 1. Elsődleges aktuális dokumentumok

### 1.1 Hosszú távú termékcél

- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

Szerepe:

- az első zárt, használható és játszható tesztkiadás célállapota;
- nem választ önmagában runtime-nyelvet.

### 1.2 Termékruntime- és telepítési követelmények

- `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`

Szerepe:

- a játékosnak átadandó program futtatási élménye;
- megengedett és tiltott külső függőségek;
- stabilitási, offline, lifecycle- és portable packaging próbák;
- objektív runtime-értékelési mérce.

Lezárt első döntések:

- 64 bites Windows 10 és újabb;
- Linux későbbi, nem prioritásos lehetőség;
- jelenleg portable csomag, telepítő nélkül;
- normál futás adminjog nélkül;
- felhasználói írható mentés-, beállítás- és loghely;
- kevés közismert prerequisite elfogadható;
- fejlesztői környezet kézi telepítése nem fogadható el.

### 1.3 Runtime engine language decision gate

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

Szerepe:

- a következő Codex-prioritás fő scope-ja;
- tanulóprogram-audit;
- Python sidecar proof;
- Godot .NET/C# proof;
- feltételes GDScript vagy más proof;
- comparison és packaging elfogadási feltételek;
- döntés utáni migrációs irányok.

### 1.4 Tanulóprogram-audit módszertan

- `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`

Szerepe:

- egységes read-only auditlap;
- projekt-, verzió-, licenc-, dependency- és attributionleltár;
- runtime-, authority-, bridge-, packaging- és stabilitási vizsgálat;
- clean-room architektúraminta és közvetlen kódátvétel elkülönítése.

### 1.5 Tanulóprogram-audit prioritási sor

- `LEARNING_PROJECT_AUDIT_QUEUE.md`

Szerepe:

- Batch 0 helyi leltár;
- közvetlen Python–Godot és C# runtime-bizonyítékok előresorolása;
- C#, GDScript, embedded Python, AI/rules és packaging projektek auditbatchjei;
- batchenkénti stop/continue/defer/expand döntési pontok.

Első mély auditjelöltek:

1. Godot RL Agents és plugin;
2. hivatalos Godot C# / Mono minták;
3. `ch200c/Durak.Godot` külön gameplay library és tesztstruktúra.

### 1.6 Nyelvfüggetlen runtime comparison fixture

- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`

Szerepe:

- közös minimal initial state;
- azonos action request sequence;
- accepted és stale-version rejected action;
- state version és typed event ellenőrzés;
- player_1/player_2 snapshot és hidden-information negatív teszt;
- canonical JSON és semantic comparison;
- Python direct, Python sidecar/Godot, C# direct és Godot .NET wrapper összevetése;
- későbbi GDScript vagy más proof közös mércéje.

### 1.7 Aktuális technikai referencia

- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

Szerepe:

- a működő Python minimal engine tényleges állapota;
- comparison reference és regression oracle;
- nem zárja le a végleges runtime-nyelvet.

### 1.8 Aktuális közeli kérdések és OQ-triázs

- `CURRENT_OPEN_QUESTIONS.md`

Szerepe:

- termékruntime-kérdések;
- eredeti OQ-azonosítók aktuális technológiai státusza;
- Python sidecar, C# és feltételes más proofok;
- runtime package és AI döntési összefüggések;
- Wellspring/Beáramlás döntés utáni gameplay queue;
- Codex és Codex nélküli prioritási sorrend.

---

## 2. Aktuális technikai státuszdokumentumok

### Architektúra

- `ARCHITECTURE.md`

### Technológiai döntések

- `TECHNOLOGY_DECISIONS.md`

### Rövid döntéstérkép

- `DECISION_MAP.md`

### Contract-státusz

- `CURRENT_CONTRACT_STATUS.md`

### Contract migrációs térkép

- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`

### Runtime package-státusz

- `CURRENT_RUNTIME_PACKAGE_STATUS.md`

### Prototípus-státusz

- `CURRENT_PROTOTYPE_STATUS.md`

Ezek a dokumentumok a jelenlegi működő rendszert és a nyitott runtime-döntési kaput együtt értelmezik.

---

## 3. Open Questions dokumentumpár

### `OPEN_QUESTIONS.md`

Státusz:

- `FULL_HISTORICAL_QUESTION_REGISTRY`

Szerepe:

- az eredeti OQ-azonosítók és kérdésmegfogalmazások megőrzése;
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

- egyik történeti dokumentum sem olvasandó a másik nélkül;
- az eredeti kérdés megmarad az `OPEN_QUESTIONS.md` fájlban;
- a részletes történeti válasz a decisions fájlban található;
- a napi és aktuális technológiai státusz a `CURRENT_OPEN_QUESTIONS.md` fájlban található;
- eltérés esetén a current dokumentum az aktuális prioritás és státusz forrása.

---

## 4. Hosszú specifikációk és referencia-dokumentumok

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
- későbbi Codex nélküli dokumentációs audit célja.

---

## 5. Checkpointok

- `checkpoints/README.md` – checkpoint-index és státusztérkép;
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md` – működő Python referencia folytatási pont;
- `checkpoints/CHECKPOINTS.md` – történeti technikai napló.

A checkpoint nem zárja le automatikusan a végleges product runtime-technológiát.

---

## 6. Dokumentumelsőbbség

Engine- és runtime-döntésnél:

1. hivatalos 1.4v szabályforrások;
2. v6.1 projektterv;
3. `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`;
4. `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
5. `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`;
6. `LEARNING_PROJECT_AUDIT_QUEUE.md`;
7. `RUNTIME_COMPARISON_FIXTURE_SPEC.md`;
8. `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`;
9. `CURRENT_OPEN_QUESTIONS.md`;
10. `TECHNOLOGY_DECISIONS.md`;
11. `DECISION_MAP.md`;
12. `CURRENT_PROTOTYPE_STATUS.md`;
13. `CURRENT_CONTRACT_STATUS.md`;
14. `CURRENT_RUNTIME_PACKAGE_STATUS.md`;
15. `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md` együtt;
16. hosszú specifikációk;
17. történeti checkpointok és régi dokumentumok.

A termékruntime-követelményspecifikáció adja az értékelési mércét. A runtime-nyelvi kapu adja a döntési folyamatot. Az auditqueue és a fixture-spec adja a végrehajtási sorrendet és a közös technikai bizonyítékot.

---

## 7. Dokumentációs feladatok fontossági sorrendben

### Elkészült

1. termékruntime- és telepítési követelményspecifikáció;
2. Windows 10+ 64-bit, portable-first, adminjog nélküli és kevés prerequisite döntés;
3. tanulóprogram-audit és licencleltár-sablon;
4. Open Questions és Decisions technológiai OQ-inak current triázsa;
5. tanulóprogram-auditbatch és prioritási sor;
6. nyelvfüggetlen runtime comparison fixture specifikáció.

### Következik

1. comparison pontozási és döntési mátrix;
2. licenc- és attributionjegyzék összesítő formája;
3. Codex read-only Batch 0 és Batch 1 prompt előkészítése;
4. `ABILITY_MODULE_SYSTEM.md` felülvizsgálata;
5. hosszú contract-specifikáció fokozatos konszolidációja;
6. hivatalos szabályforrásból megválaszolható gameplay-kérdések ellenőrzése;
7. történeti checkpointnapló formázási tisztítása.

Ha közben a runtime-döntést vagy a 0.0.1 termékcélt közvetlenül veszélyeztető új kérdés merül fel, a sorrend megállítható és a fontosabb döntési kapu előre vehető.

A runtime-nyelvi proof a következő Codex-feladat. Addig a dokumentációs, kutatási, audit- és döntés-előkészítő munkasáv aktív.
