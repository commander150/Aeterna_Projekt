# AETERNA Game Engine – Prototype Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.6
**Dátum:** 2026-09-05
**Státusz:** aktív prototípus- és technikai bizonyíték státusztérkép
**Előző aktív verzió:** 1.5 (Git history)
**Aktuális repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9` – `engine: add aeternal outcome and terminal match result`

Ez a dokumentum rögzíti:

- mely proofok készültek el;
- melyek váltak aktív rendszeralappá;
- melyek maradnak referencia/történeti proofok;
- milyen production rétegek készültek el;
- mi a következő implementáció előtti döntési kapu;
- mit nem szabad kész production rendszerként kezelni.

---

## 1. Státuszjelölések

| Státusz | Jelentés |
|---|---|
| `COMPLETE_AND_ACCEPTED` | A proof/mérföldkő célját teljesítette és elfogadott. |
| `COMPLETE_AND_FROZEN` | Működő proof, de production főágként nem fejlesztendő. |
| `PROMOTED_TO_ACTIVE_SYSTEM` | Aktív tooling/runtime/contract réteg lett. |
| `COMPLETED_FOUNDATION` | Az alapozási cél teljesült. |
| `REFERENCE_ORACLE` | Összehasonlítási/regressziós referencia. |
| `IMPLEMENTED_AND_ACTIVE` | Productionben létező, tovább bővíthető réteg. |
| `RULES_CONTRACT_PREP` | Következő feladat, de implementáció előtt rules/contract munka kell. |
| `VS1_READINESS_REQUIRED` | Következő product-facing kapu; előbb deck/mechanic readiness audit szükséges. |
| `RESEARCH_ONLY_DEFERRED` | Későbbi kutatási irány. |
| `HISTORICAL_REFERENCE` | Történeti bizonyíték. |
| `NOT_IMPLEMENTED` | Productionben még nincs megvalósítva. |

A korábbi `QUEUED_AFTER_C5B` jelölés a C.5B utáni gameplay-sor nagy részére már elavult.

---

## 2. Runtime package és adatpipeline

### Runtime package generator/publish
`PROMOTED_TO_ACTIVE_SYSTEM`

### Godot runtime loader
`PROMOTED_TO_ACTIVE_SYSTEM`

### Sample contract/debug nézetek
`COMPLETED_FOUNDATION`

### Canonical workbook/runtime binding
`IMPLEMENTED_AND_ACTIVE`

Tartalmaz:

- canonical workbook export;
- `CARDDATABASE.xlsx`;
- `REGISTRY.xlsx`;
- canonical package loader;
- runtime lookup/card binding.

---

## 3. Python minimal rules-engine referencia

`REFERENCE_ORACLE`

Megmarad:

- comparison fixture;
- expected-output forrás;
- AI/batch/regressziós oracle.

Nem production authority.

---

## 4. Python–Godot sidecar proof

`COMPLETE_AND_FROZEN`

Lezáró commit:
`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e`

---

## 5. C# RuntimeCandidate proof

`COMPLETE_AND_ACCEPTED`

Lezáró commit:
`8e5ee64e42e1657e10f3413444bb870524ee07f9`

Történeti canonical SHA:
`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

---

## 6. Runtime language decision gate

`COMPLETE_AND_ACCEPTED`

- Godot/GDScript = visual client;
- C#/.NET = production authority;
- Python = external tooling/reference.

Embedded Python:
`RESEARCH_ONLY_DEFERRED`

---

## 7. C.5A – Production architecture

`COMPLETE_AND_ACCEPTED`

---

## 8. C.5B – Production engine foundation

`COMPLETE_AND_ACCEPTED`

Lezáró commit:
`931bf5571d541c752aa421a9f0626768bd8ffbe7`

Történeti acceptance:

- Debug/Release `13/13`;
- canonical SHA;
- determinism `100/100`;
- Godot bridge smoke.

Az akkori hiánylista történeti; nem használható jelenlegi queue-ként.

---

## 9. Korábbi production gameplay foundation slice

- Wellspring: `IMPLEMENTED_AND_ACTIVE`
- player-visible Wellspring: `IMPLEMENTED_AND_ACTIVE`
- normal Infusion: `IMPLEMENTED_AND_ACTIVE`
- Magnitúdó-preflight: `IMPLEMENTED_AND_ACTIVE`
- Aura-payment preflight: `IMPLEMENTED_AND_ACTIVE`
- activity mutation: `IMPLEMENTED_AND_ACTIVE`
- Domain / placement: `IMPLEMENTED_AND_ACTIVE`
- `play_card`: `IMPLEMENTED_AND_ACTIVE`
- canonical zone transition / Void: `IMPLEMENTED_AND_ACTIVE`
- canonical card/runtime binding: `IMPLEMENTED_AND_ACTIVE`

---

## 10. Ability/effect runtime foundation

- ability catalog: `IMPLEMENTED_AND_ACTIVE`
- ability template compiler: `IMPLEMENTED_AND_ACTIVE`
- condition evaluator: `IMPLEMENTED_AND_ACTIVE`
- target filter/resolver: `IMPLEMENTED_AND_ACTIVE`
- trigger resolver foundation: `IMPLEMENTED_AND_ACTIVE`
- effect executor: `IMPLEMENTED_AND_ACTIVE`
- continuous effects: `IMPLEMENTED_AND_ACTIVE`
- modifier/keyword/duration: `IMPLEMENTED_AND_ACTIVE`
- damage/vitals/lethal: `IMPLEMENTED_AND_ACTIVE`
- draw/reference runtime: `IMPLEMENTED_AND_ACTIVE`

Korlát: a teljes kártyaállomány teljes ability coverage-e nincs kész.

---

## 11. Explicit Phase Foundation v1

`COMPLETE_AND_ACCEPTED`

Lezáró commit:
`2608345b61526097fc0b118f05461f92cfed0a95`

Canonical fázisok:

- awakening;
- infusion;
- manifestation;
- incursion;
- distribution.

Megvalósult:

- `advance_phase`;
- explicit `StartingPlayerId`;
- first-turn Awakening draw exception;
- automatic ready/draw;
- Distribution cleanup;
- player switch;
- retired production `draw_card`/`end_turn`;
- viewer-safe ActionResponse;
- Godot production bridge migration.

Lezáró acceptance:

- Debug `222/222 PASS`;
- Release `222/222 PASS`;
- oracle/reference PASS;
- determinism `100/100 PASS`;
- Godot build/smoke PASS.

---

## 12. Reaction + Combat/Pecsét production foundation

### Reaction / Priority Foundation v1

`COMPLETE_AND_ACCEPTED`

Lezáró commit:

`f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`

Aktív productionben többek között:

- authoritative `ReactionWindow`;
- `react`;
- `pass_priority`;
- resolution stack;
- LIFO;
- RC1;
- RC2 queued-trigger checkpoint/FIFO;
- viewer-safe pending projection.

### Combat + Pecsét Foundation C0–C6

`COMPLETE_AND_ACCEPTED`

Lezáró commit:

`0862e1002dbef81ee203852714d377592272a0e9`

Aktív productionben többek között:

- canonical setup + Jóslat;
- hat stabil Pecsét-slot;
- viewer-safe Seal visibility;
- `attack` / AttackCommit;
- intervention / DefenseCommit;
- két Combat ReactionWindow;
- Entity Combat;
- SealBreak / reveal / Surge;
- Gondviselés;
- Aeternal terminal outcome;
- authoritative `MatchResult v2`.

Final acceptance:

- Debug/Release `301/301 PASS`;
- determinism/reference `100/100 PASS`;
- Python isolated `465/465 PASS` + 5 skip;
- exporter `23/23 PASS`;
- Godot positive/negative smoke PASS;
- unresolved P0/P1: `0/0`.

### Következő product-facing kapu

`VS1_READINESS_REQUIRED`

A következő lépés nem általános engine-bővítés, hanem a két canonical VS1 deck
card/mechanic readiness auditja:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

Csak a tényleges VS1 blocker válik kötelező következő implementation slice-szá.

## 13. Még nem teljes production / product layer

Továbbra sem teljes többek között:

- Refresh Penalty;
- generic prevention/replacement;
- compound non-reaction choice;
- special timing/activation-policy kivételek;
- teljes ability/content coverage;
- special Seal restore/ward-effect runtime;
- Hasítás runtime;
- full Burst/Jel runtime;
- replay runner;
- production AI-vs-AI orchestration;
- simple fair VS1 AI;
- minimal playable Godot UI;
- final Windows packaging;
- profile/save;
- tutorial;
- collection/economy;
- teljes player UI.

Ezek közül nem mind VS1-blocker.

VS1 előtt csak az a hiány kötelező, amely:

1. a két canonical VS1 deck tényleges szabályos lejátszásához kell; vagy
2. általános rules-correct / deterministic / viewer-safe invariáns.

## 14. Python–C# headless kapcsolat

Elfogadott irány:

- fixture;
- scenario;
- AI-vs-AI;
- batch;
- balanszelemzés;
- CI/regresszió.

HTTP/gRPC:
`RESEARCH_ONLY_DEFERRED`

---

## 15. Dokumentumkezelési hatás

Ez a fájl továbbra is az aktív `PROTOTYPE_STATUS.md`.

A `CURRENT_PROTOTYPE_STATUS.md` nem aktív authority.

A dokumentum célja státusztérkép, nem teljes roadmap vagy contract-specifikáció.

---

## 16. Rövid aktuális összefoglaló

- Runtime package/Godot alap: aktív.
- Python reference: `REFERENCE_ORACLE`.
- Python sidecar: `COMPLETE_AND_FROZEN`.
- C# RuntimeCandidate: `COMPLETE_AND_ACCEPTED`.
- Production authority: C#.
- C.5B: `COMPLETE_AND_ACCEPTED`.
- Korábbi production gameplay foundation slice: `COMPLETE_AND_ACCEPTED`.
- Ability/effect runtime foundation: aktív.
- Explicit Phase Foundation v1: `COMPLETE_AND_ACCEPTED`.
- Reaction / Priority Foundation v1: `COMPLETE_AND_ACCEPTED`.
- Combat + Pecsét Foundation C0–C6: `COMPLETE_AND_ACCEPTED`.
- Terminal victory core: `COMPLETE_AND_ACCEPTED`.
- Current repository/production base: `0862e1002dbef81ee203852714d377592272a0e9`.
- Current next gate: `VS1_READINESS_REQUIRED`.
- Következő major product-facing cél: VS1 / M6.
- 0.0.1: aktív hosszú távú product target.
