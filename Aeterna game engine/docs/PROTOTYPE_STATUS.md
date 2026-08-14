# AETERNA Game Engine – Prototype Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.5
**Dátum:** 2026-08-14
**Státusz:** aktív prototípus- és technikai bizonyíték státusztérkép
**Felváltott verzió:** `PROTOTYPE_STATUS.md` 1.4
**Aktuális repository-bázis:** `2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

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

## 9. C.5B utáni production gameplay vertical slice

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

## 12. Következő production réteg

### Reaction / Priority Foundation v1

`RULES_CONTRACT_PREP`

Még nem kész implementation task.

Előbb:

- official rules audit;
- OQ-frissítés;
- pending/reaction contract;
- pass;
- resolution ordering;
- exact public state/event boundary.

Combat nem része ennek az első slice-nak.

---

## 13. Még nem teljes production

- teljes Reaction/Priority runtime;
- combat;
- attack/block;
- Pecsétfeltörés;
- teljes Pecsét state/visibility;
- Refresh Penalty;
- prevention/replacement teljes runtime;
- teljes multi-trigger ordering;
- teljes ability coverage;
- victory/defeat;
- replay;
- production AI-vs-AI;
- final Windows packaging;
- full player UI.

---

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
- Első production gameplay vertical slice: elkészült.
- Ability/effect runtime foundation: aktív.
- Explicit Phase Foundation v1: `COMPLETE_AND_ACCEPTED`.
- Következő fókusz: Reaction / Priority rules/contract előkészítés.
- Combat: még nem következő implementation slice.
