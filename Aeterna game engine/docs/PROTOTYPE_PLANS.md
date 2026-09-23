# AETERNA Game Engine – Prototype Plans

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.3
**Dátum:** 2026-09-06
**Státusz:** történeti prototípusterv és proof-folytonossági referencia  
**Aktuális státuszfájl:** `PROTOTYPE_STATUS.md`  
**Aktuális checkpoint:** `../../project/status/checkpoints/ENGINE_CHECKPOINT.md`
**Aktuális repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9`

Ez a dokumentum a korábbi prototípuslépések célját és egymásra épülését őrzi.

Nem:

- aktuális tasklista;
- aktív prioritási dokumentum;
- production engine-specifikáció;
- Codex-prompt;
- következő programozási feladat.

Az aktuális feladatokat a `../../project/status/checkpoints/ENGINE_CHECKPOINT.md`, az `../../project/planning/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.9.md` és a `PROTOTYPE_STATUS.md` tartalmazza.

Current next gate: `VS1_READINESS_REQUIRED`.

A jelen fájlban szereplő korábbi gameplay slice nem azonos a current `VS1 / M6 – első ténylegesen játszható vertical slice` mérföldkővel.

---

## 1. Prototípus-alapelv

Egy prototípus:

- egy pontos kérdést bizonyít;
- kicsi és visszafordítható;
- nem kever több nagy döntést;
- teszttel vagy smoke-kal rendelkezik;
- nem írja felül a hivatalos szabályt;
- nem válik automatikusan production rendszerré;
- csak emberi döntés után léptethető elő.

---

## 2. Elkészült proof-lánc

### P0.1 – Python sample runtime package

Bizonyította:

- többfájlos package generálását;
- manifest/cards/decks/lookups/ability/support/diagnostics outputot;
- Python unit tesztelhetőséget.

### P0.2 – Godot package loader

Bizonyította:

- package betöltést;
- registryket;
- headless smoke-ot;
- Godot consumption pathot.

### P0.3 – Sample contract és debug view

Bizonyította:

- snapshot/legal action/event parser;
- debug megjelenítés;
- card reference resolution;
- unified dashboard.

### P0.4 – XLSX exporter és publish pipeline

Bizonyította:

- valós XLSX exportot;
- source splitet;
- candidate buildet;
- blocking validation gate-et;
- Godot consumption copy frissítést.

### P1 – Python minimal reference engine

Bizonyította:

- MatchState;
- card instance;
- draw/end-turn;
- state version;
- typed event;
- player snapshot;
- Domain;
- Wellspring isolated contract;
- deterministic AI trajectory.

### P2 – Python–Godot sidecar

Státusz:

- `COMPLETE_AND_FROZEN`.

Bizonyította:

- process/TCP kapcsolat;
- lifecycle;
- shutdown;
- watchdog;
- canonical comparison.

### P3 – Godot .NET/C# in-process candidate

Státusz:

- `COMPLETE_AND_ACCEPTED`.

Bizonyította:

- pure C# runtime;
- Godot in-process bridge;
- Python/TCP/külön engine-processz nélküli működés;
- canonical SHA;
- determinisztika;
- headless és visual PASS.

---

## 3. Lezárt döntési kapu

A runtime comparison eredménye:

- C#/.NET = production authority;
- Godot/GDScript = visual client;
- Python = external tooling/reference.

A korábbi alternatív prooftervek nem aktívak:

- további GDScript authority proof;
- production Python sidecar;
- embedded Python;
- új TCP lifecycle proof.

Csak új, erős technikai bizonyíték nyithatja újra a döntést.

---

## 4. Production prototípus és történeti foundation-slice sorrend

### C.5A

Production C# architecture plan.

Státusz:

- `COMPLETE_AND_ACCEPTED`.

### C.5B

Production C# engine foundation.

Státusz:

- `COMPLETE_AND_ACCEPTED`;
- lezáró commit: `931bf5571d541c752aa421a9f0626768bd8ffbe7`.

### Korábbi production gameplay foundation slice

C.5B után a korai production gameplay foundation történeti migrációs sorrendje:

1. Wellspring production state;
2. player-visible Wellspring;
3. Beáramlás;
4. Magnitúdó;
5. Aura-payment;
6. simple Entity `play_card`;
7. Domain placement;
8. event, snapshot és Godot interaction.

---

## 5. Prototípus elfogadási sablon

Minden új proofhoz:

- cél;
- nem cél;
- forrás;
- fixture;
- success criteria;
- negative test;
- determinism;
- hidden-information;
- build;
- unit/integration/smoke;
- Godot visual vagy headless szükség szerint;
- diagnostics;
- cleanup;
- commit scope;
- emberi PASS.

A proofból production csak külön döntéssel és production project-határral lesz.

---

## 6. Megőrzési szabály

Megőrzendő:

- fixture;
- expected artifact;
- proof log;
- candidate projekt, ha regressziós értéke van;
- commit SHA;
- acceptance result;
- ismert korlát.

Nem szükséges minden proofhoz külön új dokumentum.

A `PROTOTYPE_STATUS.md` a jelenlegi állapot, ez a fájl történeti folytonossági referencia.

A korábbi részletes prototípustervek a Git-történetben megmaradnak.
