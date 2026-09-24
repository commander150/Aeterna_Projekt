# AETERNA Game Engine

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.5
**Dátum:** 2026-09-05
**Státusz:** aktív programegység-README
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9` – Combat + Pecsét Foundation C0–C6
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
- korábbi production gameplay foundation slice: `COMPLETE_AND_ACCEPTED`;
- Explicit Phase Foundation v1: `COMPLETE_AND_ACCEPTED`;
- Reaction / Priority Foundation v1: `COMPLETE_AND_ACCEPTED`;
- Combat + Pecsét Foundation C0–C6: `COMPLETE_AND_ACCEPTED`.

Aktuális checkpoint: `../project/status/checkpoints/ENGINE_CHECKPOINT.md`

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

Current szabályforrás:

- `rules/sources/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.5v.docx`;
- `rules/sources/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4.1v.docx`.

Adatút:

- 1.9v kártyaadatbázis;
- LOOKUPS;
- `CARDDATABASE.xlsx`;
- `REGISTRY.xlsx`;
- canonical workbook exporter;
- runtime package.

A rules authority és a runtime package külön réteg.

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

Korábbi production gameplay/ability foundationként elkészült többek között:

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

Public progression:

`advance_phase`

Explicit Phase történeti lezáró acceptance:

- Debug `222/222 PASS`;
- Release `222/222 PASS`;
- determinism `100/100 PASS`;
- Godot build és pozitív/negatív smoke PASS.

Reaction / Priority Foundation v1:

`f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`

`COMPLETE_AND_ACCEPTED`

Combat + Pecsét Foundation C0–C6:

- C0 `ca55bc3714de2692753fccc18a8f11d9dac1beea`;
- C1+C2 `558d4453a1604c0ebe76065df08a207192c21c8b`;
- C3 `d236f0e3c36994f65e7d00d25972660baac2a842`;
- C4 `68b07dd6906fc8c37245325a855322d48f5f2635`;
- C5 `d30f8a4c42383a0200e416acb7148facc3bbbc11`;
- C6 `0862e1002dbef81ee203852714d377592272a0e9`.

Current state:

`COMBAT_AND_SEAL_FOUNDATION_C0_C6 = COMPLETE_AND_ACCEPTED`

Current core többek között:

- canonical setup + Jóslat;
- six-Seal model és hidden-info projection;
- `attack` / AttackCommit;
- intervention / DefenseCommit;
- Combat ReactionWindows;
- participant continuity/contact revalidation;
- Entity Combat;
- SealBreak/reveal/Surge;
- Gondviselés;
- Aeternal terminal outcome;
- authoritative `MatchResult`.

Final C0–C6 acceptance:

- Debug/Release C#: `301/301 PASS`;
- targeted C6: `8/8 PASS`;
- determinism/reference: `100/100 PASS`;
- canonical bytes: `210676`;
- canonical SHA:
  `97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`;
- Python isolated: `465/465 PASS` + 5 skip;
- exporter: `23/23 PASS`;
- Godot C# positive/negative smoke: PASS;
- unresolved P0/P1: `0/0`.

## 6. Mi nincs még teljes productionben?

Továbbra sem teljes többek között:

- Refresh Penalty;
- generic prevention/replacement;
- teljes compound non-Reaction choice;
- Hasítás runtime;
- full Burst/Jel runtime;
- teljes ability/content coverage;
- special Seal restore/ward effect runtime;
- replay runner;
- production AI-vs-AI orchestration;
- simple fair VS1 AI;
- minimal playable Godot UI;
- final Windows packaging;
- profile/save/tutorial/collection/economy.

Ezek közül nem mind VS1-blocker.

## 7. Következő technikai irány

Következő major product-facing cél:

`VS1 / M6 – első ténylegesen játszható vertical slice`

Canonical VS1 deckek:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

Technikai sequence:

```text
VS1 card/mechanic readiness audit
→ unsupported blocker azonosítás
→ csak blockerre finite contract + C# implementation
→ simple fair AI + match orchestration
→ minimal playable Godot
→ human-vs-AI full match
→ reproducible AI-vs-AI smoke
→ VS1 acceptance
```

VS1 előtt csak az a hiány kötelező, amely:

1. a két canonical VS1 deck szabályos lejátszásához kell; vagy
2. általános rules-correct / deterministic / viewer-safe invariáns.

Reaction / Priority v1 és Combat + Pecsét C0–C6 már nem következő implementation slice:
mindkettő `COMPLETE_AND_ACCEPTED`.

## 8. Nem programozási munkasávok

- kártyaadat- és szabályaudit;
- LOOKUPS/ID-contract;
- kártyadizájn;
- célzott learning/clean-room elemzés.

---

## 9. Codex-használat

### Hordozható Godot smoke-konfiguráció

A Godot smoke BAT futtatók az alábbi sorrendben oldják fel a futtatható állományt:

1. `AETERNA_GODOT_EXE`, ha egy létező fájlra mutat;
2. `godot4` a `PATH` környezeti változóban;
3. `godot` a `PATH` környezeti változóban.

Az `AETERNA_GODOT_EXE` értékét külső idézőjelek nélkül add meg. A szóközt tartalmazó elérési utak támogatottak. Ha a futtatható állomány nem oldható fel, a futtató egyértelmű hibával leáll; sikeres feloldás esetén változatlanul továbbadja a Godot folyamat kilépési kódját.

Codex szerepe:

- programozás;
- build/test/smoke;
- szükséges célzott lokális technikai vizsgálat.

Current programming workflow:

```text
Codex local edit + validation
→ NO COMMIT / NO PUSH
→ ChatGPT + human report/diff/test audit
→ human approval
→ user commit/push
→ remote verification
```

Codex nem hoz önálló rules-, project-priority- vagy dokumentációs authority-döntést.

Projekttervezés, dokumentáció, rules/OQ/contract scope és acceptance:
ChatGPT + ember.

## 10. Dokumentációs állapot

A nagy dokumentációs cleanup lezárult.

A current célzott sync a Combat + Pecsét C0–C6 lezárása utáni current-truth frissítés.

Current production base:

`0862e1002dbef81ee203852714d377592272a0e9`

Current OQ:

`52 answered / 15 partly_answered / 7 deferred / 0 open`.

Current next technical/product gate:

`VS1_READINESS_REQUIRED`

A dokumentációs frissítés history-aware targeted patch + diff/consistency review módszerrel történik;
nem hoz létre párhuzamos active dokumentumokat ugyanarra a szerepre.
