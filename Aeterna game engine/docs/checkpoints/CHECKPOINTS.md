# AETERNA Game Engine – Checkpoints

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.4
**Dátum:** 2026-09-05
**Státusz:** történeti technikai mérföldkőnapló
**Aktív folytatási checkpoint:** `../../../project/status/checkpoints/ENGINE_CHECKPOINT.md`

Ez a fájl az AETERNA Game Engine fő technikai mérföldköveinek időrendi összefoglalója.

Nem:

- aktív tasklista;
- architektúra-specifikáció;
- contract-status;
- Open Questions-regiszter.

Régi „következő lépés” nem írhatja felül az aktív `../../../project/status/checkpoints/ENGINE_CHECKPOINT.md` vagy projektterv állapotát.

---

## v0.1 – Python sample runtime package + Godot loader

Bizonyította:

- sample package generator;
- manifest/cards/decks/lookups/aliases/ability/support/diagnostics;
- Python unit test;
- Godot loader és registry;
- headless smoke.

---

## v0.2 – Sample contracts és debug views

Bizonyította:

- snapshot/legal action/event loader;
- debug nézetek;
- unified dashboard;
- card reference resolution.

Korlát: statikus fixture, nem authoritative state.

---

## v0.3 – XLSX exporter migration

Bizonyította az exporter Python tooling alá helyezését és az XLSX → JSONL utat.

---

## v0.4 – Runtime package publish pipeline

Bizonyította:

- valós card/deck/lookup build;
- blocking validation;
- Godot consumption copy;
- diagnostics/report.

---

## Python minimal engine szakasz

Meghatározó bázis:

`84a7e8f42d313ed58689bbb975c7d6c85ab6e87b` – `Add minimal Wellspring resource contracts`

Elkészült:

- state version;
- card instance;
- draw/end-turn reference flow;
- typed event;
- player snapshot;
- Domain;
- activity;
- Wellspring;
- deterministic AI trajectory.

Aktuális szerepe: reference/oracle.

---

## Runtime comparison fixture

Történeti canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

Bizonyította a determinisztikus közös comparison contractot.

---

## Python–Godot sidecar proof

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e`

Státusz:

`COMPLETE_AND_FROZEN`

Nem production főmotor.

---

## C# in-process runtime proof

Lezáró commit:

`8e5ee64e42e1657e10f3413444bb870524ee07f9`

Státusz:

`COMPLETE_AND_ACCEPTED`

Bizonyította a pure C# + Godot .NET in-process irányt, determinisztikát és regressziós proofot.

---

## Runtime-nyelvi döntés

Elfogadott:

- Godot/GDScript visual layer;
- C# authoritative production engine;
- Python external tooling/reference.

---

## C.5A – Production C# architecture

Státusz:

`COMPLETE_AND_ACCEPTED`

---

## C.5B – Production C# foundation

Státusz:

`COMPLETE_AND_ACCEPTED`

Lezáró commit:

`931bf5571d541c752aa421a9f0626768bd8ffbe7`

Történeti acceptance:

- Debug/Release `13/13`;
- canonical artifact `210730` byte;
- SHA-egyezés;
- determinism `100/100`;
- pozitív/negatív Godot bridge smoke.

---

## Korábbi production gameplay foundation slice

Szakasz:

`931bf5571d541c752aa421a9f0626768bd8ffbe7`
→
`2608345b61526097fc0b118f05461f92cfed0a95`

Összesen: `39 commit`

Megvalósult fő rétegek:

- alapjáték főforrás `1.4.3v`;
- canonical workbook, `CARDDATABASE.xlsx`, `REGISTRY.xlsx`;
- Wellspring;
- Beáramlás;
- Magnitúdó;
- Aura-payment;
- activity;
- Domain / `play_card`;
- zone transition / Void;
- canonical card/runtime binding;
- ability catalog/template compiler;
- condition / target / trigger / effect foundation;
- continuous effects;
- modifier/keyword/duration;
- damage/vitals/lethal;
- draw/reference runtime.

### Explicit Phase Foundation v1

Lezáró commit:

`2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

Megvalósult:

- `awakening`;
- `infusion`;
- `manifestation`;
- `incursion`;
- `distribution`;
- `advance_phase`;
- `StartingPlayerId`;
- Awakening draw exception és auto ready/draw;
- Distribution cleanup és player switch;
- viewer-safe ActionResponse;
- Godot bridge migráció.

Lezáró acceptance:

- Debug `222/222 PASS`;
- Release `222/222 PASS`;
- oracle/reference PASS;
- canonical byte count `210676`;
- canonical SHA `97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`;
- determinism `100/100 PASS`;
- Godot build/smoke PASS.

Státusz:

`COMPLETE_AND_ACCEPTED`

---

## Reaction / Priority Foundation v1

Lezáró production commit:

`f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`

Megvalósult fő rétegek:

- authoritative `ReactionWindow`;
- `react`;
- `pass_priority`;
- canonical resolution stack;
- LIFO;
- RC1;
- RC2 queued-trigger checkpoint/FIFO;
- viewer-safe pending projection.

Lezáró acceptance:

- Debug/Release `246/246 PASS`;
- determinism `100/100 PASS`;
- oracle/reference PASS;
- Python isolated `465/465 PASS` + 5 skip;
- Godot C# build + pozitív/negatív smoke PASS;
- unresolved P0/P1: `0/0`.

Státusz:

`COMPLETE_AND_ACCEPTED`

---

## Combat + Pecsét Foundation C0–C6

Rules migration:

`61ad2605dd1aa3d7ea95444f0bb66cebf819014e`

Production slice-ok:

- `ca55bc3714de2692753fccc18a8f11d9dac1beea` – C0 setup + Seal foundation;
- `558d4453a1604c0ebe76065df08a207192c21c8b` – C1+C2 attack + első Combat ReactionWindow;
- `d236f0e3c36994f65e7d00d25972660baac2a842` – C3 intervention + DefenseCommit;
- `68b07dd6906fc8c37245325a855322d48f5f2635` – C4 Entity Combat;
- `d30f8a4c42383a0200e416acb7148facc3bbbc11` – C5 SealBreak + Surge + Gondviselés;
- `0862e1002dbef81ee203852714d377592272a0e9` – C6 Aeternal + terminal MatchResult.

Megvalósult fő rétegek:

- canonical setup + Jóslat;
- hat stabil Pecsét-slot és viewer-safe visibility;
- `attack` / AttackCommit;
- intervention / DefenseCommit;
- két Combat ReactionWindow;
- Entity Combat simultaneous damage;
- SealBreak / public reveal / Surge;
- Gondviselés Surge opportunity;
- Aeternal outcome;
- authoritative terminal `MatchResult v2`.

Lezáró acceptance:

- Debug/Release C#: `301/301 PASS`;
- targeted C6: `8/8 PASS`;
- determinism/reference: `100/100 PASS`;
- canonical byte count: `210676`;
- canonical SHA:
  `97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`;
- Python isolated regression: `465/465 PASS`, `5 skip`;
- exporter: `23/23 PASS`;
- Godot C# consumer + pozitív/negatív smoke: PASS;
- `git diff --check`: PASS;
- unresolved P0/P1: `0/0`.

Státusz:

`COMBAT_AND_SEAL_FOUNDATION_C0_C6 = COMPLETE_AND_ACCEPTED`

---

## Következő mérföldkőnapló-bejegyzés

Új történeti bejegyzés csak új nagy, lezárt production/product mérföldkőnél készül.

Current következő nagy cél:

`VS1 / M6 – első ténylegesen játszható vertical slice`

A VS1 még nincs lezárva, ezért még nem kap történeti acceptance-bejegyzést.

Későbbi példák:

- VS1;
- production AI/replay/packaging proof;
- 0.0.1 fő mérföldkő.

Kisebb dokumentum- vagy egyedi commit nem igényel külön történeti checkpointbejegyzést.
