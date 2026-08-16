# AETERNA – Projekt Térkép és Fájlstátusz v1.9

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.9
**Dátum:** 2026-08-16
**Státusz:** aktív magas szintű projekt- és fájlszerep-térkép
**Felváltott dokumentum:** `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.9.md`
**Szinkronizációs repository-bázis:** `14e315d3f04f5baddb547dcb767c8b156b02551f`
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`
**C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Ez a dokumentum a jelenlegi fő projekt-rétegeket, aktív forrásokat, fontos fájlszerepeket és történeti elhatárolásokat rögzíti. Nem teljes repository-inventár és nem részletes cleanup-napló.

---

## 1. Projekt fő rétegei

1. hivatalos szabályforrások;
2. kártyaadatbázis, REGISTRY és LOOKUPS;
3. Python adat-, export-, audit-, AI-, batch- és reference tooling;
4. Python reference engine;
5. Godot vizuális kliens és debugréteg;
6. történeti C# runtime proof;
7. production C# authoritative engine;
8. aktív projekt- és engine-dokumentáció;
9. Open Questions döntési réteg;
10. learning / clean-room source és izolált project analyses;
11. cross-project synthesis;
12. AETERNA architecture blueprints;
13. történeti archívum;
14. regenerálható outputok és test fixture-ök.

Elfogadott authority:

- Godot/GDScript = vizuális kliens;
- C#/.NET = egyetlen production rules authority;
- Python = external tooling és reference/oracle.

---

## 2. Aktív hivatalos és szerkesztési források

### 2.1 Hivatalos szabályforrások

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4.3v.docx`;
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`.

Státusz: `ACTIVE_CANONICAL_RULE_SOURCE`

A kód, runtime package, learning projekt vagy technikai dokumentum nem írhatja felül őket.

### 2.2 Aktív szerkesztési adatforrások

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `LOOKUPS.xlsx`.

Státusz: `ACTIVE_EDITING_SOURCE`

### 2.3 Canonical runtime-adatforrások / programfogyasztási réteg

- `CARDDATABASE.xlsx`;
- `REGISTRY.xlsx`;
- canonical workbook export;
- validált runtime package.

Ezek programfogyasztási/canonical adatút részei; nem helyettesítik automatikusan a szerkesztési munkaforrást vagy a hivatalos szabályforrást.

### 2.4 Aktuális adataudit

- `AETERNA – KÁRTYAADATBÁZIS AKTUÁLIS ADATAUDIT 1.0.md`.

Státusz: `ACTIVE_DATA_AUDIT`

---

## 3. Aktív projektirányítás

- root `README.md`;
- `Aeterna dokumentációk/README.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.6.md`;
- jelen `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.9.md`;
- `Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`.

A korábbi projekttervek és projekt-térképek történeti/archív elődök.

---

## 4. Aktív engine-réteg

### 4.1 C# proofréteg

Történeti proofprojektek:

- `Aeterna.RuntimeCandidate`;
- `Aeterna.RuntimeCandidate.Proof`.

Státusz:

- proof: `COMPLETE_AND_ACCEPTED`;
- nem production motor;
- regressziós bizonyítékként megmarad.

### 4.2 Production C# projektek

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- `Aeterna.Engine.sln`.

C.5B foundation commit:

`931bf5571d541c752aa421a9f0626768bd8ffbe7`

Aktuális production mérföldkő:

`2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

Jelenlegi bizonyított production scope többek között:

- runtime package betöltés;
- match bootstrap;
- state version / stale rejection;
- player-visible snapshot;
- viewer-safe event projection;
- Wellspring;
- normál Beáramlás;
- Magnitúdó- és Aura-preflight;
- activity mutation;
- Domain és `play_card`;
- canonical zone transition;
- Void;
- canonical card/runtime binding;
- canonical ability/effect execution foundation;
- target/trigger/effect runtime;
- damage/vitals;
- continuous effects;
- modifier/keyword/duration;
- draw/reference runtime;
- explicit öt-fázisú turn lifecycle;
- Godot production bridge.

Nincs még teljes production:

- Reaction / Priority runtime;
- combat;
- Pecsét teljes state/visibility;
- Refresh Penalty;
- teljes ability coverage;
- victory/defeat;
- replay;
- production AI-vs-AI;
- teljes player UI.

### 4.3 Python

Aktív szerepek:

- runtime package build;
- XLSX/JSON/JSONL tooling;
- canonical export;
- audit és diagnostics;
- reference engine;
- fixture és scenario;
- AI-vs-AI és batch;
- differential testing.

Nem production authority.

### 4.4 Godot

Aktív szerepek:

- runtime package loader;
- registryk;
- snapshot/legal action/event debug;
- visual client foundation;
- C# bridge proof;
- production C# engine bridge;
- pozitív/negatív smoke.

Nem szabályforrás és nem módosíthat authoritative state-et közvetlenül.

---

## 5. Aktív engine-dokumentáció

Elsődleges technikai folytatás:

- `ARCHITECTURE.md`;
- `TECHNOLOGY_DECISIONS.md`;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `DECISION_MAP.md`;
- `checkpoints/ENGINE_CHECKPOINT.md`.

Aktuális státusz:

- `PROTOTYPE_STATUS.md`;
- `RUNTIME_PACKAGE_STATUS.md`;
- `CONTRACT_STATUS.md`.

Contract/specification:

- `CONTRACT_SPECIFICATION.md`;
- `RUNTIME_PACKAGE_SPECIFICATION.md`;
- `ABILITY_MODULE_SYSTEM.md`.

Kérdés–válasz rendszer:

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

A `CURRENT_*` elődök nem aktív authority-k.

---

## 6. Reference-, learning-, synthesis- és blueprint-réteg

A `reference/` nem canonical háttér- és munkaforrás.

### 6.1 Learning registry és analyses

Aktív registry: `sources list_v2.7.md`, `LEARNING_CATALOG_v2.1.md`, `ORIGIN_IDENTIFICATION_BACKLOG_v0.3.md`, valamint `learning/analyses/`.

Current: `59 registry / 58 local / 30 analyses`.

### 6.2 Cross-project synthesis

`learning/synthesis/` – 152 unique pattern ID, 140 unique anti-pattern ID, 30-analysis capability matrix.

### 6.3 AETERNA blueprints

`Aeterna game engine/docs/blueprints/` – AETERNA proposal/current-foundation expansion layer; nem official rules source és nem automatikus ADOPTED döntés.

```text
isolated analysis → synthesis → blueprint → human decision → contract → implementation
```

### 6.4 Open Questions

OQ v2.2 current: `50 answered / 17 partly_answered / 7 deferred / 0 open`.

Reference, learning, synthesis vagy blueprint nem írhatja felül az AETERNA szabályt vagy contractot.

---

## 7. Archívum

Fő történeti útvonalak:

- `Archive/aeterna dokumentáciok/`;
- `Archive/aeterna gaming engine/`.

Az archív fájl:

- nem aktív authority;
- nem szerkesztendő canonical forrásként;
- történeti és auditcélra megőrzendő.

---

## 8. Generált és ideiglenes outputok

Generált output nem válhat canonical szerkesztési forrássá.

`TEMP/`, build output, cache vagy lokális tooling nem commitolandó pusztán azért, mert egy audit használta.

---

## 9. Fontos aktív munkasávok

### Production gameplay foundation

Státusz: `COMPLETE_AND_ACCEPTED`

A Wellspring → Beáramlás → payment → `play_card` → ability/effect foundation → explicit phase szakasz elkészült production C#-ban.

### Következő engine-fókusz

`Reaction / Priority Foundation v1`

Státusz: `NEXT – MINIMAL_CONTRACT_FINALIZATION`.

A source/OQ/research előkészítés kész. Current következő lépés: ReactionWindow/ResolutionStack minimum contract, `react`/`pass_priority`, RC1, RC2 + trigger checkpoint/FIFO, event/projection és unsupported paths.

Csak ezután production C# implementáció.

### Combat

Nem a következő közvetlen implementation slice.

### Adat- és LOOKUPS-audit

Továbbra is nyitott:

- LOOKUPS-audit;
- ID-contract;
- delimiter;
- aliasok;
- master–export parity;
- névprofil és decklista-segédnevek.

---

## 10. Dokumentációs minimum

Aktív projektfolytatásnál kritikus:

1. aktuális projektterv;
2. aktuális projekt-térkép;
3. `ENGINE_CHECKPOINT.md`;
4. root `README.md`;
5. közvetlenül érintett státusz/contract dokumentum.

Nem kell minden kisebb commit után teljes dokumentációs tömegfrissítés.

---

## 11. Aktuális státusz

- dokumentációs archív rendezés: `COMPLETE`;
- C.5A: `COMPLETE_AND_ACCEPTED`;
- C.5B: `COMPLETE_AND_ACCEPTED`;
- első production gameplay vertical slice: `COMPLETE_AND_ACCEPTED`;
- canonical ability/effect runtime foundation: `IMPLEMENTED_AND_ACTIVE`;
- Explicit Phase Foundation v1: `COMPLETE_AND_ACCEPTED`;
- aktív dokumentációs consistency pass: `COMPLETE`;
- learning registry: `59 registry / 58 local`;
- project analyses: `30`;
- synthesis/blueprint program: `COMMITTED`;
- OQ: `50 answered / 17 partly_answered / 7 deferred / 0 open`;
- governance/ability/checkpoint recovery: `COMMITTED` (`14e315d...`);
- Reaction preparation: `COMPLETE_FOR_V1_CONTRACT_DRAFTING`;
- Reaction implementation: `NOT_STARTED`;
- következő engine rules/contract munka: Reaction / Priority minimal v1 contract.
