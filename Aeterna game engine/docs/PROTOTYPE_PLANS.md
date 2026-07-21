# AETERNA Game Engine – Prototype Plans

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-20  
**Státusz:** történeti prototípusterv és proof-folytonossági referencia  
**Aktuális státuszfájl:** `PROTOTYPE_STATUS.md`  
**Aktuális checkpoint:** `checkpoints/ENGINE_CHECKPOINT.md`  
**Aktuális repository-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Ez a dokumentum a korábbi prototípuslépések célját és egymásra épülését őrzi.

Nem:

- aktuális tasklista;
- aktív prioritási dokumentum;
- production engine-specifikáció;
- Codex-prompt;
- következő programozási feladat.

Az aktuális feladatokat az `ENGINE_CHECKPOINT.md`, az `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md` és a `PROTOTYPE_STATUS.md` tartalmazza.

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

## 4. Production prototípus és vertical slice sorrend

### C.5A

Production C# architecture plan.

Státusz:

- `COMPLETE_AND_ACCEPTED`.

### C.5B

Production C# engine foundation.

Státusz:

- `READY_FOR_IMPLEMENTATION`;
- `PAUSED_CODEX_QUOTA`.

### Első gameplay vertical slice

C.5B után:

1. Wellspring;
2. infusion;
3. Magnitúdó;
4. Aura-payment;
5. simple Entity `play_card`;
6. Domain placement;
7. event és snapshot;
8. Godot interaction.

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
