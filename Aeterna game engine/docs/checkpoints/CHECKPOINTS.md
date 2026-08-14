# AETERNA Game Engine – Checkpoints

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.3
**Dátum:** 2026-08-14
**Státusz:** történeti technikai mérföldkőnapló
**Aktív folytatási checkpoint:** `ENGINE_CHECKPOINT.md`

Ez a fájl az AETERNA Game Engine fő technikai mérföldköveinek időrendi összefoglalója.

Nem:

- aktív tasklista;
- architektúra-specifikáció;
- contract-status;
- Open Questions-regiszter.

Régi „következő lépés” nem írhatja felül az aktív `ENGINE_CHECKPOINT.md` vagy projektterv állapotát.

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

## Első production gameplay vertical slice

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

## Következő mérföldkőnapló-bejegyzés

Új történeti bejegyzés csak következő nagy, lezárt production mérföldkőnél készül, például:

- Reaction / Priority foundation;
- jelentős combat foundation;
- production AI/replay/packaging proof;
- 0.0.1 fő mérföldkő.

Kisebb dokumentum- vagy egyedi commit nem igényel külön történeti checkpointbejegyzést.
