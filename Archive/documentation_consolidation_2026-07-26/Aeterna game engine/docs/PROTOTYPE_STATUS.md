# AETERNA Game Engine – Prototype Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.4\
**Dátum:** 2026-07-22\
**Státusz:** aktív prototípus- és technikai bizonyíték státusztérkép  
**Felváltott fájl:** `CURRENT_PROTOTYPE_STATUS.md`  
**Aktuális repository-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`

Ez a dokumentum azt rögzíti, hogy:

- mely prototípusok készültek el;
- melyek váltak aktív rendszeralappá;
- melyek maradnak referencia- vagy történeti proofok;
- mely technológiai döntések zárultak le;
- mi a következő implementációs lépés;
- mit nem szabad kész production rendszerként kezelni.

Kapcsolódó aktív dokumentumok:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `ARCHITECTURE.md`
- `TECHNOLOGY_DECISIONS.md`
- `DECISION_MAP.md`
- `CONTRACT_STATUS.md`
- `OPEN_QUESTIONS.md`
- `checkpoints/ENGINE_CHECKPOINT.md`
- `../../Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.4.md`

---

## 1. Státuszjelölések

| Státusz | Jelentés |
|---|---|
| `COMPLETE_AND_ACCEPTED` | A proof célját teljesítette, a döntés elfogadott. |
| `COMPLETE_AND_FROZEN` | A proof működőképes, de nem fejlesztendő tovább production főágként. |
| `PROMOTED_TO_ACTIVE_SYSTEM` | A prototípusból aktív tooling-, runtime- vagy contract-réteg lett. |
| `COMPLETED_FOUNDATION` | Az alapozási cél teljesült, a réteg megtartandó. |
| `REFERENCE_ORACLE` | Összehasonlítási és regressziós referencia. |
| `READY_FOR_IMPLEMENTATION` | A feladat specifikált és implementálható. |
| `PAUSED_CODEX_QUOTA` | A feladat nem technikai okból, hanem Codex-keret miatt szünetel. |
| `QUEUED_AFTER_C5B` | A production C# foundation után következik. |
| `RESEARCH_ONLY_DEFERRED` | Későbbi kutatási irány, nem aktív production feladat. |
| `HISTORICAL_REFERENCE` | Történeti bizonyíték, nem aktív task queue. |
| `NOT_STARTED` | Még nincs implementálva. |

---

## 2. Runtime package és adatpipeline

### 2.1 Runtime package generator és publish pipeline

**Státusz:** `PROMOTED_TO_ACTIVE_SYSTEM`

Bizonyított:

- package build;
- manifest és többfájlos package;
- cards/decks/lookups/aliases/diagnostics;
- candidate validation;
- Godot consumption copy;
- valós adatméret;
- determinisztikus és auditálható export.

A Python adatpipeline aktív és megtartandó.

### 2.2 Godot runtime package loader

**Státusz:** `PROMOTED_TO_ACTIVE_SYSTEM`

Bizonyított:

- package betöltés;
- card/deck/lookup registry;
- ability és diagnostics adat;
- headless smoke;
- consumption path: `res://runtime_package`.

### 2.3 Sample contract loader és debug nézetek

**Státusz:** `COMPLETED_FOUNDATION`

Ide tartozik:

- sample snapshot;
- sample legal action;
- sample event log;
- snapshot viewer;
- legal action debug panel;
- event log debug view;
- unified dashboard;
- card reference resolver;
- consistency smoke.

Ezek debug- és kliensintegrációs alapok.

---

## 3. Python minimal rules-engine referencia

**Státusz:** `REFERENCE_ORACLE`

A Python engine bizonyítottan tartalmaz:

- MatchState és PlayerState;
- session és environment;
- expected state version guard;
- card instance registry;
- draw transition;
- end-turn transition;
- generic typed event envelope;
- `zone_move` és `turn_transition` event;
- player-visible snapshot;
- hidden-information redakció;
- AI episode trajectory;
- Domain topology;
- Domain occupancy;
- public board projection;
- structural Entity placement options;
- card instance activity state;
- izolált Wellspring state és resource summary.

Döntés:

- nem törlendő;
- nem automatikusan archiválandó;
- comparison fixture és expected-output forrás;
- AI-, batch- és regressziós orákulum;
- production C# migráció ellenőrző alap.

Nem tekintendő a végleges production authoritative runtime-nak.

---

## 4. Python–Godot sidecar proof

**Státusz:** `COMPLETE_AND_FROZEN`

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e` – `Fix Godot sidecar cancellation race warnings`

Bizonyított:

- külön Python engine-processz;
- localhost TCP;
- handshake;
- request/response framing;
- timeout és cancellation;
- kontrollált shutdown;
- Emergency Shutdown;
- F8 parent watchdog;
- orphan-processz elleni védelem;
- helyes canonical output;
- warning-, error- és crashmentes manuális futás.

Döntés:

- proofként megmarad;
- production főmotorként nem folytatandó;
- nem készül hozzá új TCP-, watchdog-, launcher- vagy packaging-fejlesztés.

---

## 5. C# minimal in-process runtime proof

**Státusz:** `COMPLETE_AND_ACCEPTED`

Lezáró commit:

`8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Környezet:

- Godot `4.7.1.stable.mono.official.a13da4feb`;
- .NET SDK `8.0.423`;
- `Microsoft.NETCore.App 8.0.29`;
- target framework `net8.0`.

Bizonyított:

- pure C# runtime candidate;
- Godot .NET in-process futás;
- nincs külön engine-processz;
- nincs Python-processz;
- nincs TCP/listener;
- Debug és Release build;
- headless proof;
- visual proof;
- két manuális PASS;
- újrafuttatható Run gomb;
- 100-run determinisztika;
- mutation negative proof;
- GDScript regressziók;
- nulla warning/error;
- F8 után szabályos bezárás;
- nincs crash.

Közös canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

Döntés:

- C# lesz a production authoritative runtime;
- a candidate proof regressziós bizonyítékként megmarad;
- nem nevezendő át közvetlenül production motorrá.

---

## 6. Runtime engine language decision gate

**Státusz:** `COMPLETE_AND_ACCEPTED`

Lezárt döntés:

- Godot/GDScript: vizuális kliensréteg;
- C#/.NET: egyetlen authoritative production runtime;
- Python: külső adat-, audit-, AI-, batch- és elemzőeszközréteg.

Nem készül további GDScript authoritative proof.

Embedded Python:

`RESEARCH_ONLY_DEFERRED`

---

## 7. C.5A – Production C# architecture plan

**Státusz:** `COMPLETE_AND_ACCEPTED`

Rögzítve:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- typed public contractok;
- EngineSession;
- Godot production bridge;
- Python headless tooling kapcsolat;
- fixture-alapú migráció;
- egyetlen C# authoritative MatchState.

---

## 8. C.5B – Production C# engine foundation

**Státusz:** `COMPLETE_AND_ACCEPTED`

**Lezáró commit:** `931bf5571d541c752aa421a9f0626768bd8ffbe7`

Megvalósult scope:

- pure C# production engine;
- headless host;
- test runner;
- core contractok;
- EngineSession;
- minimum runtime package loader;
- draw/end-turn production reprodukció;
- production fixture adapter;
- Godot production bridge;
- RuntimeCandidate regresszió.

Bizonyíték:

- production tesztek Debug és Release: `13/13`;
- canonical SHA-egyezés és `100/100` determinisztika;
- viewer-safe snapshot és event projection;
- strukturált negatív JSON-boundary viselkedés;
- Godot pozitív és negatív production bridge smoke.

Nem része:

- Wellspring gameplay;
- Beáramlás;
- Aura;
- Magnitúdó;
- `play_card`;
- harc;
- effect engine;
- trigger;
- HTTP;
- gRPC;
- végleges Windows packaging.

---

## 9. Gameplay-engine queue

**Státusz:** `QUEUED_AFTER_C5B`

Sorrend:

1. Wellspring PlayerState- és MatchState-integráció.
2. Player-visible Wellspring summary.
3. Beáramlás precondition.
4. Beáramlás transition és typed event.
5. Magnitúdó-preflight.
6. Aura-source és payment contract.
7. Activity mutation transition.
8. Entitás kijátszási precondition.
9. `play_card`.
10. Hand → Domain transition.
11. Entry-state.
12. Teljesebb phase és priority.
13. Reaction.
14. Combat.
15. Ability execution.
16. Win/loss.

---

## 10. Python–C# headless kapcsolat

**Státusz:** elfogadott irány, még nem production implementáció

Első forma:

```text
Python
  ↓ subprocess + JSON/JSONL
Aeterna.Engine.Headless
  ↓ canonical JSON/JSONL
Python
```

Használat:

- fixture;
- scenario;
- AI-vs-AI;
- batch;
- balanszelemzés;
- CI;
- regresszió.

Localhost HTTP vagy gRPC:

`RESEARCH_ONLY_DEFERRED`

Csak mérési szükség esetén vizsgálható.

---

## 11. Elhalasztott vagy nem blokkoló tételek

- production C# Windows packaging;
- self-contained vagy prerequisite modell;
- runtime diagnostic log;
- hosszú soak teszt;
- production AI-vs-AI;
- replay;
- Godot stretch és maximized-window policy;
- Python unittest monolitikus discovery adósság;
- GDScript-fájlok szerepkategorizálása;
- sidecar proof archiválási stratégia;
- C# whitespace-megfigyelés.

---

## 12. C# whitespace-megfigyelés

**Státusz:** `OBSERVE_ONLY_NON_BLOCKING`

A `CsharpMinimalRuntimeProof.cs` összehasonlított változatai logikailag azonosak voltak.

Eltérés:

- 4 szóközös behúzás;
- tabulátoros behúzás.

Nincs azonnali javítás vagy whitespace-only commit.

---

## 13. Dokumentumkezelési hatás

Ez a fájl a `CURRENT_PROTOTYPE_STATUS.md` utódja.

A repository aktuális állapota:

1. az aktív név `PROTOTYPE_STATUS.md`;
2. a régi `CURRENT_PROTOTYPE_STATUS.md` nem aktív authority;
3. az aktív hivatkozások az utódfájlra mutatnak.

Általános szabály:

- `CURRENT_*` csak akkor maradhat ideiglenesen, amíg az összevonási vagy átnevezési audit tart;
- ahol nincs párfájl, a `CURRENT_` előtag nem használható aktív fájlnévként;
- ahol van párfájl, tartalmi összevetés és lehetőség szerint merge szükséges;
- minden aktív utódfájlnak verzióblokkot, dátumot és státuszt kell kapnia.

---

## 14. Rövid aktuális összefoglaló

- Runtime package és Godot kliensalap működik.
- A Python minimal engine referencia és comparison oracle.
- A Python sidecar proof lezárt és befagyasztott.
- A C# in-process proof lezárt és elfogadott.
- A production authoritative runtime C#.
- A production C# engine foundation elkészült, de a teljes gameplay-engine még nem.
- A C.5B kész és elfogadott.
- A következő kódolási munka a Wellspring production state és player-visible Wellspring.
