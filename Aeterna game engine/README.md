# AETERNA Game Engine

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.4
**Dátum:** 2026-08-16
**Státusz:** aktív programegység-README
**Szinkronizációs repository-bázis:** `14e315d3f04f5baddb547dcb767c8b156b02551f`
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95`
**C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Az **AETERNA Game Engine** az AETERNA fizikai kártyajáték contract-first digitális programegysége.

## Projektstátusz

Elfogadott architektúra:

```text
Godot / GDScript = vizuális kliens
C# / .NET        = egyetlen production authoritative rules engine
Python           = adatpipeline, audit, fixture, reference/oracle, AI, batch és elemzőtooling
```

Proofok:

- Python–Godot sidecar: `COMPLETE_AND_FROZEN`;
- Godot .NET/C# RuntimeCandidate: `COMPLETE_AND_ACCEPTED`.

Production mérföldkövek:

- C.5A: `COMPLETE_AND_ACCEPTED`;
- C.5B: `COMPLETE_AND_ACCEPTED`;
- első production gameplay vertical slice: `COMPLETE_AND_ACCEPTED`;
- Explicit Phase Foundation v1: `COMPLETE_AND_ACCEPTED`.

Aktuális checkpoint: `docs/checkpoints/ENGINE_CHECKPOINT.md`

---

## 1. Bizonyított proof-folytonosság

### Python reference engine

Szerep:

- reference implementation;
- comparison oracle;
- AI/batch/tooling alap;
- production C# regressziós ellenőrzés.

Nem production authority.

### Python–Godot sidecar

Lezáró commit: `d1fb7aaa23d58f166a30f9e0241799f35f5ac14e`

Státusz: `COMPLETE_AND_FROZEN`

### C# RuntimeCandidate

Lezáró commit: `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Történeti canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

Státusz: `COMPLETE_AND_ACCEPTED`

Proofként megmarad.

---

## 2. Fő mappaszerkezet

### `python/`

- runtime package build/validáció;
- canonical workbook export;
- XLSX/JSON/JSONL tooling;
- audit;
- reference engine;
- fixture/scenario;
- AI-vs-AI és batch;
- diagnostics/regresszió.

### `C#/`

Proof:

- `Aeterna.RuntimeCandidate`;
- `Aeterna.RuntimeCandidate.Proof`.

Production:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- `Aeterna.Engine.sln`.

### `Godot/`

- loader/registry;
- debug;
- visual client;
- C# proof bridge;
- production C# bridge/smoke.

Nem rules authority.

### `docs/`

Aktív engine-dokumentáció és checkpointok.

---

## 3. Runtime package és adatút

Általános út:

```text
Szerkesztési források / XLSX
        ↓
Python export, normalizálás és validáció
        ↓
canonical/runtime package
        ↓
C# production loader + Godot consumption
```

Szabályforrás:

- alapjáték 1.4.3v;
- kiegészítő főforrás 1.4v.

Adatút:

- 1.9v kártyaadatbázis;
- LOOKUPS;
- `CARDDATABASE.xlsx`;
- `REGISTRY.xlsx`;
- canonical workbook exporter;
- runtime package.

---

## 4. Production C# authority

Publikus `EngineSession` API:

- `CreateMatch`;
- `GetPlayerSnapshot`;
- `ListLegalActions`;
- `SubmitAction`;
- `GetEvents(string viewerPlayerId, int afterSequence = 0)`;
- `GetMatchResult`.

Alapelvek:

- state mutation csak engine transitionnel;
- rejected action atomikus;
- stale request guard;
- player-facing/debug projection külön;
- viewer-safe hidden information;
- internal event store full-fidelity;
- Godot bridge rules logikát nem tartalmaz.

---

## 5. Production gameplay állapot

C.5B foundation:

`931bf5571d541c752aa421a9f0626768bd8ffbe7`

Azóta production C#-ban elkészült:

- Wellspring;
- Beáramlás;
- Magnitúdó/Aura preflight;
- activity state;
- Domain;
- `play_card`;
- zone transition / Void;
- canonical card/runtime binding;
- ability catalog/template compiler;
- condition/target/trigger/effect foundation;
- continuous effects;
- modifier/keyword/duration;
- damage/vitals/lethal;
- draw/reference runtime.

Explicit Phase Foundation:

`2608345b61526097fc0b118f05461f92cfed0a95`

Phase flow:

`awakening -> infusion -> manifestation -> incursion -> distribution`

Public progression: `advance_phase`

Lezáró acceptance:

- Debug `222/222 PASS`;
- Release `222/222 PASS`;
- determinism `100/100 PASS`;
- Godot build és pozitív/negatív smoke PASS.

---

## 6. Mi nincs még teljes productionben?

- Reaction / Priority;
- combat;
- teljes Pecsétmodell;
- Refresh Penalty;
- teljes ability coverage;
- victory/defeat;
- replay;
- production AI-vs-AI;
- final packaging/UI.

---

## 7. Következő technikai irány

**Reaction / Priority Foundation v1** – `NEXT – MINIMAL_CONTRACT_FINALIZATION`.

A rules/source audit, OQ v2.2 és clean-room research elkészült. Most a minimal ReactionWindow/ResolutionStack contract, `react`/`pass_priority`, RC1, RC2 + trigger checkpoint/FIFO, event/projection és unsupported paths következik.

Csak ezután C# implementáció. Combat külön későbbi slice.

---

## 8. Nem programozási munkasávok

- kártyaadat- és szabályaudit;
- LOOKUPS/ID-contract;
- kártyadizájn;
- célzott learning/clean-room elemzés.

---

## 9. Codex-használat

Codex csak szükséges technikai feladathoz:

- programozás;
- build/test/smoke;
- lokális worktree/fájl elemzés.

Projekttervezés, dokumentáció és rules/contract döntés nem alapértelmezett Codex-feladat.

---

## 10. Dokumentációs állapot

A nagy dokumentációs cleanup lezárult.

A `2608345b...` mérföldkőhöz tartozó célzott A+B active-document consistency pass is lezárult.

A 2026-08-15/16-i learning/synthesis/OQ és targeted governance recovery handoff commitolva. Current OQ: `50/17/7/0`. A következő szakmai fókusz a Reaction / Priority minimal v1 contract finalizálása.
