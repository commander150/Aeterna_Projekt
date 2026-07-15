# AETERNA Game Engine – Dokumentációs index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.6  
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
- az első termékkövetelmény-csomag lezárta a Windows 10+ 64-bit, portable-first, adminjog nélküli és kevés prerequisite irányt;
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
- előírja a stabilitási, offline, lifecycle- és portable packaging próbákat;
- objektív mércét ad minden runtime- és nyelvi jelölt összehasonlításához;
- kimondja, hogy a Python csak akkor váltandó le, ha bizonyítottan akadályozza a termékkövetelmények teljesítését, vagy más modell lényegesen jobb összeredményt ad;
- v1.1-ben lezárta az első közvetlen proof-feltételeket.

Lezárt első döntések:

- 64 bites Windows 10 és újabb;
- Linux későbbi, nem prioritásos lehetőség;
- jelenleg portable csomag, telepítő nélkül;
- normál futás adminjog nélkül;
- felhasználói írható mentés-, beállítás- és loghely;
- kevés közismert prerequisite elfogadható;
- fejlesztői környezet kézi telepítése nem fogadható el.

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

### Tanulóprogram-audit és licencleltár

- `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`

Szerepe:

- egységes read-only auditstruktúra a helyileg tárolt külső projektekhez;
- projekt-, verzió-, licenc-, dependency- és attributionleltár;
- nyelv-, runtime-, authority-, bridge-, packaging- és stabilitási vizsgálat;
- Windows 10+ 64-bit portable megfelelés;
- clean-room architektúraminta és közvetlen kódátvétel elkülönítése;
- projektenkénti AETERNA-pontozás és bizonyítékjegyzék.

A külső tanulóprogramok nem kerülnek automatikusan az AETERNA repositoryba. A sablon az audit eredményének szerkezetét adja, nem engedélyezi a kódmásolást.

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

Ez tartalmazza:

- a runtime language comparison elsődleges prioritását;
- a tanulóprogram-forrásauditot;
- a Python sidecar proofot;
- a Godot .NET/C# proofot;
- a Python–GDScript comparison lehetséges szűk scope-ját;
- a Wellspring és Beáramlás döntés utáni queue-ját.

Következő frissítése:

- az első termékruntime- és telepítési döntések átvezetése;
- a proofot blokkoló és nem blokkoló kérdések elválasztása.

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
5. `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md` az audit módszertanához;
6. `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`;
7. `TECHNOLOGY_DECISIONS.md`;
8. `DECISION_MAP.md`;
9. `CURRENT_PROTOTYPE_STATUS.md`;
10. `CURRENT_CONTRACT_STATUS.md`;
11. `CURRENT_RUNTIME_PACKAGE_STATUS.md`;
12. `CURRENT_OPEN_QUESTIONS.md`;
13. `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md` együtt;
14. hosszú specifikációk;
15. történeti checkpointok és régi dokumentumok.

A 0.0.1 célállapot a hosszú távú termékirányt adja. A termékruntime- és telepítési követelményspecifikáció meghatározza az értékelési mércét. A nyelvi döntési kapu ennek alapján hasonlítja össze a jelölteket. Az audit-sablon a külső bizonyítékgyűjtés egységes módszerét adja.

---

## 6. Következő dokumentációs feladatok fontossági sorrendben

Elkészült:

1. termékruntime- és telepítési követelményspecifikáció;
2. első közvetlen proof-feltételek emberi lezárása;
3. tanulóprogram-audit és licencleltár-sablon.

Következik:

1. a `CURRENT_OPEN_QUESTIONS.md` frissítése a lezárt termékdöntésekkel;
2. az `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` technológiai OQ-azonosítóinak közös frissítése;
3. a helyi tanulóprogram-leltár konkrét kitöltési sorrendjének előkészítése;
4. nyelvfüggetlen comparison fixture és pontozási mátrix dokumentálása;
5. az `ABILITY_MODULE_SYSTEM.md` felülvizsgálata;
6. a hosszú contract-specifikáció fokozatos konszolidációja;
7. a történeti checkpointnapló formázási tisztítása.

Ha közben a runtime-döntést vagy a 0.0.1 termékcélt közvetlenül veszélyeztető új kérdés merül fel, a sorrend megállítható és a fontosabb döntési kapu előre vehető.

A runtime-nyelvi proof a következő Codex-feladat. Addig a dokumentációs, kutatási, audit- és döntés-előkészítő munkasáv aktív.
