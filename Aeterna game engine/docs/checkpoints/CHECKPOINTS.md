# AETERNA Game Engine – Checkpoints

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2\
**Dátum:** 2026-07-22\
**Státusz:** történeti technikai mérföldkőnapló  
**Aktív folytatási checkpoint:** `ENGINE_CHECKPOINT.md`

Ez a fájl az AETERNA Game Engine fő technikai mérföldköveinek időrendi összefoglalója.

Nem:

- aktív tasklista;
- architektúra-specifikáció;
- contract-status;
- Open Questions-regiszter.

Régi „következő lépés” megjegyzés nem írhatja felül az aktív `ENGINE_CHECKPOINT.md` vagy projektterv állapotát.

---

## v0.1 – Python sample runtime package + Godot loader

Bizonyította:

- sample package generator;
- manifest/cards/decks/lookups/aliases/ability/support/diagnostics;
- Python unit test;
- Godot loader és registry;
- headless smoke;
- explicit Godot logfájl.

Korlát:

- nem rules engine;
- nem action runtime;
- nem player UI.

---

## v0.2 – Sample contracts és debug views

Bizonyította:

- snapshot loader;
- legal action loader;
- event loader;
- snapshot viewer;
- legal action panel;
- event log view;
- unified debug dashboard;
- card reference resolution.

Korlát:

- statikus fixture;
- nem authoritative state.

---

## v0.3 – XLSX exporter migration

Bizonyította:

- exporter Python tooling alá helyezését;
- explicit source/output;
- XLSX → JSONL;
- unit/smoke futást.

---

## v0.4 – Runtime package publish pipeline

Bizonyította:

- valós kártya/deck/lookup build;
- külön LOOKUPS-forrás;
- candidate build;
- blocking validation;
- Godot consumption copy;
- diagnostics és report.

A runtime package–Godot alap aktív rendszer lett.

---

## Python minimal engine szakasz

Meghatározó bázis:

- `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`
- `Add minimal Wellspring resource contracts`

Elkészült:

- expected state version;
- card instance registry;
- draw;
- end turn;
- typed event;
- player snapshot;
- Domain topology/occupancy;
- Entity placement option;
- activity state;
- isolated Wellspring;
- deterministic AI trajectory.

Aktuális szerepe:

- reference implementation;
- comparison oracle;
- AI/batch tooling base.

---

## Runtime comparison fixture

Fixture:

- `minimal_draw_end_turn_v1`.

Canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

Bizonyította:

- draw;
- stale reject;
- end turn;
- second draw;
- snapshot;
- legal actions;
- typed events;
- deterministic canonical output.

---

## Python–Godot sidecar proof

Lezáró commit:

- `d1fb7aaa23d58f166a30f9e0241799f35f5ac14e`.

Státusz:

- `COMPLETE_AND_FROZEN`.

Bizonyította:

- localhost TCP;
- request/response;
- shutdown;
- emergency shutdown;
- parent watchdog;
- orphan cleanup;
- canonical comparison.

Nem production főmotor.

---

## C# in-process runtime proof

Lezáró commit:

- `8e5ee64e42e1657e10f3413444bb870524ee07f9`.

Státusz:

- `COMPLETE_AND_ACCEPTED`.

Bizonyította:

- pure C# candidate;
- Godot .NET bridge;
- nincs Python/TCP/külön engine-processz;
- Debug/Release;
- headless/visual;
- 100-run determinism;
- mutation negative proof;
- canonical SHA.

---

## Runtime-nyelvi döntés

Elfogadott:

- Godot/GDScript visual layer;
- C# authoritative production engine;
- Python external tooling/reference.

A nyelvi döntési kapu lezárult.

---

## C.5A – Production C# architecture

Státusz:

- `COMPLETE_AND_ACCEPTED`.

Rögzítve:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- EngineSession;
- typed contracts;
- Godot bridge;
- Python headless kapcsolat.

---

## C.5B – Production C# foundation

Státusz:

- `COMPLETE_AND_ACCEPTED`.

Lezáró commit:

- `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`.

Scope:

- pure C# engine;
- headless host;
- tests;
- package loader;
- draw/end-turn;
- stale reject;
- canonical fixture;
- Godot production bridge.

Bizonyította:

- pure `net8.0` production core;
- ugyanazt az `EngineSession` implementációt használó headless és Godot út;
- viewer-safe snapshot- és eventprojekció;
- strukturált JSON boundary rejection;
- Debug/Release `13/13` production teszt;
- expected és actual canonical SHA-egyezés;
- `210730` byte canonical artifact;
- `100/100` determinisztika;
- pozitív és negatív Godot production bridge smoke.

---

## Következő mérföldkőnapló-bejegyzés

Új történeti bejegyzés akkor készül, amikor:

- első production gameplay vertical slice;
- jelentős packaging proof;
- 0.0.1 fő mérföldkő.

Kisebb dokumentum- vagy egyedi commit nem igényel külön történeti checkpointbejegyzést.

A részletes régi checkpointszövegek a Git-történetben megmaradnak.
