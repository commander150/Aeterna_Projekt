# AETERNA Game Engine – Checkpoint Index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-20  
**Státusz:** aktív checkpoint-index és státusztérkép  
**Aktuális repository-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Ez a dokumentum elválasztja:

- az aktív elsődleges technikai folytatási checkpointot;
- a történeti runtime package-, exporter-, Godot- és engine-mérföldköveket;
- a hosszú távú termékmérföldkövet;
- a részletes történeti checkpointnaplót.

Nem helyettesíti a részletes checkpointokat.

---

## 1. Melyik checkpoint mire való?

### 1.1 Aktív technikai folytatási pont

- `ENGINE_CHECKPOINT.md`

Ez az elsődleges dokumentum, ha az AETERNA Game Engine jelenlegi technikai állapotát vagy munkáját kell folytatni.

Tartalmazza:

- a Python referenciaengine állapotát;
- a befagyasztott Python–Godot sidecar proofot;
- az elfogadott C# in-process proofot;
- a lezárt runtime-nyelvi döntést;
- a C# production engine tervezett architektúráját;
- a C.5B szünetelő implementációs feladatot;
- a contract- és runtime package állapotot;
- a dokumentációs átnevezési és auditfeladatokat;
- a biztonságos következő lépést.

A fájl a korábbi `CURRENT_ENGINE_CHECKPOINT.md` utódja.

### 1.2 Történeti technikai checkpointnapló

- `CHECKPOINTS.md`

Ez a fájl megőrzi a korábbi:

- runtime package;
- exporter;
- Godot loader;
- sample contract;
- Python engine;
- proof és technikai mérföldkövek

történeti állapotát.

Nem az aktuális technikai folytatási pont.

### 1.3 Hosszú távú termékmérföldkő

- `../AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

Ez nem technikai checkpoint, hanem az első zárt, játszható tesztkiadás célállapota.

---

## 2. Történeti checkpointok

### v0.1 – Python sample runtime package + Godot loader

**Státusz:** `COMPLETED_FOUNDATION`

Bizonyította:

- Python sample runtime package generálását;
- többfájlos package-et;
- Godot loader működését;
- registrybetöltést;
- headless package smoke tesztet.

Nem bizonyította:

- szabálymotort;
- action-végrehajtást;
- AI-t;
- játszható UI-t.

### v0.2 – Sample contracts + debug views

**Státusz:** `COMPLETED_FOUNDATION`

Bizonyította:

- statikus sample snapshot betöltését;
- statikus sample legal action betöltését;
- statikus sample event log betöltését;
- snapshot viewer működését;
- legal action debug panel működését;
- event log debug view működését.

Nem bizonyította:

- valós MatchState generálását;
- szabályból számított legal actiont;
- valódi action request/response végrehajtást.

### v0.3 – XLSX exporter migration smoke

**Státusz:** `COMPLETED_FOUNDATION`

Bizonyította:

- az exporter Python tooling alá migrálását;
- explicit source és output útvonalat;
- valódi XLSX → JSONL smoke futtatást;
- az exporter unit tesztelhetőségét.

### v0.4 – Runtime package publish pipeline és LOOKUPS source split

**Státusz:** `COMPLETED_FOUNDATION_ACTIVE_PIPELINE`

Bizonyította:

- candidate build és validation gate használatát;
- Godot runtime package publish útvonalat;
- 1.9v kártyaadatbázis és LOOKUPS source splitet;
- runtime lookup reader működését;
- normalization alias és audit report package outputot;
- Godot consumption copy frissítését.

A runtime package–Godot alapozás elkészült és aktív architektúrarész maradt.

---

## 3. Python rules-engine referenciaszakasz

### Bázis

Meghatározó Python commit:

- `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`
- `Add minimal Wellspring resource contracts`

Elkészült többek között:

- expected state version guard;
- card instance registry;
- deck/hand/discard authoritative zónák;
- draw transition;
- ZoneMove event;
- end-turn transition;
- generic event envelope;
- player-visible snapshot v2;
- canonical AI trajectory;
- Domain position contract;
- Domain topology MatchState-integráció;
- Domain occupancy;
- player-visible Domain board;
- structural Entity placement option;
- card instance activity state;
- isolated Wellspring state és resource summary.

Aktuális szerepe:

- referenciaimplementáció;
- comparison oracle;
- AI- és batchtooling-alap;
- production C# migráció ellenőrző forrása.

Nem a végleges production authoritative runtime.

---

## 4. Python–Godot sidecar proof

**Státusz:** `COMPLETE_AND_FROZEN`

Lezáró commit:

- `d1fb7aaa23d58f166a30f9e0241799f35f5ac14e`
- `Fix Godot sidecar cancellation race warnings`

Bizonyította:

- külön Python engine-processz;
- localhost TCP;
- request/response framing;
- normál és emergency shutdown;
- parent watchdog;
- F8 utáni orphan-processz elleni védelem;
- canonical fixture-egyezés;
- warning-, error- és crashmentes elfogadott futás.

Production főmotorként nem folytatandó.

---

## 5. C# in-process runtime proof

**Státusz:** `COMPLETE_AND_ACCEPTED`

Lezáró commit:

- `8e5ee64e42e1657e10f3413444bb870524ee07f9`
- `Add minimal C# runtime candidate proof`

Bizonyította:

- pure C# runtime candidate;
- Godot .NET in-process futás;
- külön engine-processz nélkül;
- Python nélkül;
- TCP nélkül;
- draw és end-turn;
- stale rejection;
- player snapshot;
- legal action;
- typed eventek;
- canonical JSON és SHA;
- 100-run determinisztika;
- mutation negative proof;
- Debug és Release build;
- headless és visual proof;
- manuális kétfutásos PASS;
- nulla warning/error.

Közös canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

A proof nem nevezendő át közvetlenül production motorrá.

---

## 6. Lezárt runtime-nyelvi döntés

Elfogadott architektúra:

```text
Godot/GDScript
    = vizuális kliensréteg

C#/.NET
    = egyetlen production authoritative engine

Python
    = külső adat-, audit-, teszt-, AI-, batch- és elemzőeszköz
```

A Python-sidecar és a C# proof összehasonlítása után további GDScript authoritative proof nem szükséges.

---

## 7. Production C# szakasz

### C.5A – Production architecture

**Státusz:** `COMPLETE_AND_ACCEPTED`

Rögzítve:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- typed contractok;
- EngineSession;
- Godot production bridge;
- Python headless interfész;
- fixture-alapú migráció.

### C.5B – Production engine foundation

**Státusz:** `READY_FOR_IMPLEMENTATION`

**Ideiglenesen:** `PAUSED_CODEX_QUOTA`

Tervezett:

- production pure C# engine;
- headless host;
- test runner;
- minimum runtime package loader;
- draw/end-turn reprodukció;
- canonical comparison;
- Godot production bridge;
- candidate regresszió.

Nem tartalmaz új gameplayt.

---

## 8. Mérföldkő-folytonosság

```text
v0.1 runtime package loader alap
        ↓
v0.2 sample contract és debug UI alap
        ↓
v0.3 exporter migration
        ↓
v0.4 publish pipeline és LOOKUPS source split
        ↓
Python minimal authoritative referenciaengine
        ↓
Python–Godot sidecar proof
        ↓
C# in-process runtime proof
        ↓
runtime-nyelvi döntés
        ↓
C.5A production architecture
        ↓
C.5B production C# foundation
        ↓
első production gameplay vertical slice
        ↓
AETERNA 0.0.1
```

A korábbi munkarétegek nem vesztek el, hanem új szerepet kaptak:

- runtime package: aktív statikus adatcontract;
- Python engine: referencia és tooling;
- sidecar: befagyasztott proof;
- C# candidate: elfogadott regressziós proof;
- production C#: következő authoritative runtime.

---

## 9. Aktuális mérföldkő-rétegek

### M1 – Minimal determinisztikus engine-alapok

**Állapot:** Python referenciában elkészült, C# productionben migrálandó.

### M2 – Player view és board contract

**Állapot:** Python referenciában első jelentős szakasz elkészült.

### TG1 – Runtime language decision gate

**Állapot:** `COMPLETE_AND_ACCEPTED`

### C.5A – Production architecture

**Állapot:** `COMPLETE_AND_ACCEPTED`

### C.5B – Production engine foundation

**Állapot:** `READY_FOR_IMPLEMENTATION / PAUSED_CODEX_QUOTA`

### M3 – Első production gameplay actionök

**Állapot:** `QUEUED_AFTER_C5B`

Tervezett lánc:

1. Wellspring MatchState-integráció;
2. player-visible Wellspring;
3. Beáramlás;
4. Magnitúdó;
5. Aura-payment;
6. Entity play precondition;
7. `play_card`;
8. Domain-placement.

### M4–M9

**Állapot:** későbbi roadmap.

---

## 10. Checkpointkészítési szabály

Az `ENGINE_CHECKPOINT.md` frissítendő, amikor:

- érdemi technikai szakasz lezárult;
- architecture vagy authority döntés változott;
- új production mérföldkő készült el;
- hosszabb beszélgetés vagy munkaszakasz lezárul;
- új beszélgetés előtt biztonságos folytatási pont szükséges;
- a dokumentációs átadás vagy commit jelentősen módosítja a projektállapotot.

Nem kell külön új checkpointfájl minden apró commit vagy dokumentumfrissítés után.

Minden checkpoint tartalmazza:

- báziscommit;
- architecture és authority;
- elkészült funkciók;
- contract- és schemaállapot;
- teszteredmények;
- ismert korlátok;
- nem implementált rendszerek;
- következő biztonságos lépés;
- dokumentációs állapot;
- worktree vagy repository állapot.

---

## 11. Dokumentumelsőbbség

Aktuális technikai folytatásnál:

1. `ENGINE_CHECKPOINT.md`;
2. `../CONTRACT_STATUS.md`;
3. `../OPEN_QUESTIONS.md` és `../OPEN_QUESTIONS_DECISIONS.md`;
4. `../ARCHITECTURE.md`;
5. `../TECHNOLOGY_DECISIONS.md`;
6. `CHECKPOINTS.md`.

A `CHECKPOINTS.md` régi „következő lépés” megjegyzései történeti állapotot rögzítenek, és nem írják felül az aktív checkpointot.

---

## 12. Dokumentumkezelési hatás

Repository alkalmazásakor:

1. `ENGINE_CHECKPOINT.md` bekerül a `docs/checkpoints/` mappába;
2. `CURRENT_ENGINE_CHECKPOINT.md` eltávolítandó;
3. a jelen `README.md` lecseréli a régi checkpoint-indexet;
4. minden `CURRENT_ENGINE_CHECKPOINT.md` hivatkozást át kell vezetni;
5. az eltávolítás csak a hivatkozások ellenőrzése után történhet;
6. a végső audit során a `CHECKPOINTS.md` történeti tartalma is ellenőrizendő, de nem keverendő automatikusan az aktív checkpointba.
