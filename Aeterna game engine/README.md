# AETERNA Game Engine

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.1  
**Dátum:** 2026-07-21  
**Státusz:** aktív programegység-README  
**Aktuális repository HEAD:** `32a0cbea24c82dda440f1a053b454ef03949d8ae` – `docs update 2`  
**Aktuális C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Az **AETERNA Game Engine** az AETERNA fizikai kártyajáték contract-first digitális programegysége.

## Projektstátusz

A runtime-nyelvi döntési kapu lezárult.

Elfogadott hosszú távú architektúra:

```text
Godot / GDScript
    = vizuális kliens, scene, input, UI, animáció és debug

C# / .NET
    = egyetlen production authoritative rules engine

Python
    = adatpipeline, audit, fixture, AI, batch, simulation és elemzőtooling
```

Bizonyított runtime-jelöltek:

- Python–Godot sidecar: `COMPLETE_AND_FROZEN`;
- Godot .NET/C# in-process candidate: `COMPLETE_AND_ACCEPTED`.

A production C# engine még nem létezik.

Következő kódolási szakasz:

- **C.5B – Production C# Engine Foundation**
- státusz: `READY_FOR_IMPLEMENTATION`;
- ideiglenesen: `PAUSED_CODEX_QUOTA`.

Aktuális checkpoint:

- `docs/checkpoints/ENGINE_CHECKPOINT.md`

Dokumentációs index:

- `docs/README.md`

Projekt- és cleanup-térkép:

- `../Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`

---

## 1. Bizonyított technikai bázis

### Python reference engine

A Python minimal engine bizonyítottan tartalmaz:

- MatchState és PlayerState;
- state version guard;
- action request/response alap;
- legal action alap;
- card instance registry;
- deck, hand és discard instance-zónák;
- draw és end-turn transition;
- typed `zone_move` és `turn_transition` event;
- state invariánsok;
- player-visible snapshot v2;
- hidden-information projection;
- Domain topology és occupancy;
- public Domain board;
- structural Entity placement option;
- Aktív/Kimerült card instance state;
- izolált Wellspring state és resource summary;
- determinisztikus AI episode trajectory.

Aktuális szerepe:

- referenciaimplementáció;
- comparison oracle;
- AI/batch/tooling alap;
- production C# migráció ellenőrző forrása.

Nem a végleges production authority.

### Python–Godot sidecar proof

Bizonyított:

- localhost TCP;
- request/response;
- handshake;
- controlled és emergency shutdown;
- F8 parent watchdog;
- orphan-processz elleni védelem;
- canonical fixture-egyezés.

Lezáró commit:

- `d1fb7aaa23d58f166a30f9e0241799f35f5ac14e`

A proof megmarad, de production főmotorként nem folytatandó.

### C# in-process runtime proof

Bizonyított:

- pure C# runtime candidate;
- Godot 4.7.1 .NET;
- .NET 8;
- közvetlen processzen belüli hívás;
- nincs Python;
- nincs TCP;
- nincs külön engine-processz;
- draw, end-turn és stale rejection;
- legal action, snapshot és typed event;
- canonical JSON/SHA;
- 100-run determinisztika;
- mutation negative proof;
- Debug/Release build;
- headless és visual PASS;
- nulla warning/error.

Közös canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

Lezáró commit:

- `8e5ee64e42e1657e10f3413444bb870524ee07f9`

A `Aeterna.RuntimeCandidate` proofként megmarad; nem nevezendő át közvetlenül production motorrá.

---

## 2. Fő mappaszerkezet

### `python/`

Aktív szerepek:

- runtime package build és validáció;
- XLSX/JSON/JSONL tooling;
- kártya- és LOOKUPS-audit;
- Python minimal reference engine;
- fixture- és scenario-generálás;
- AI-vs-AI és batch koordináció;
- diagnostics, statisztika és riport;
- differential testing.

Új production gameplay-szabály nem készülhet kizárólag Pythonban.

### `C#/`

Jelenlegi proofprojektek:

- `Aeterna.RuntimeCandidate`;
- `Aeterna.RuntimeCandidate.Proof`.

Tervezett production projektek:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`.

### `Godot/`

Aktív és bizonyított szerepek:

- runtime package loader és registry;
- snapshot/legal action/event debug nézetek;
- unified dashboard;
- headless smoke;
- Godot .NET/C# bridge proof;
- későbbi player UI és visual client.

Korlátok:

- nem lehet szabályforrás;
- nem módosíthat authoritative state-et közvetlenül;
- nem olvas közvetlenül XLSX-et;
- a production bridge nem tartalmazhat rules logicot.

### `docs/`

Kanonikus navigáció:

- `README.md`;
- `checkpoints/ENGINE_CHECKPOINT.md`;
- `ARCHITECTURE.md`;
- `TECHNOLOGY_DECISIONS.md`;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `DECISION_MAP.md`;
- `PROTOTYPE_STATUS.md`;
- `RUNTIME_PACKAGE_STATUS.md`;
- `CONTRACT_STATUS.md`;
- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

---

## 3. Runtime package és adatút

Bizonyított út:

```text
Google Sheets / XLSX
        ↓
Python export, normalizálás és validáció
        ↓
runtime package candidate
        ↓
blocking publish validation
        ↓
Godot/runtime_package consumption copy
        ↓
Godot loader és később C# engine loader
```

Aktív szerkesztési források:

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `LOOKUPS.xlsx`;
- hivatalos 1.4v szabályfőforrások.

Legutóbbi rögzített package-állapot:

- 814 kártya;
- 28 deck;
- blocking diagnostics: 0;
- warning: 0;
- error: 0.

A package identity és production schema még nem végleges.

---

## 4. Authority- és contractmodell

A production C# engine lesz az egyetlen authoritative state-gazda.

Tervezett publikus API:

- `CreateMatch`;
- `GetPlayerSnapshot`;
- `ListLegalActions`;
- `SubmitAction`;
- `GetEvents`;
- `GetMatchResult`.

State mutation csak validált engine transitionön keresztül történhet.

A GDScript és a Python:

- snapshotot fogyaszt;
- legal actionből választ;
- action requestet küld;
- nem módosít MatchState-et közvetlenül.

Player-facing és debug projection külön marad.

Rejected action:

- nem mutál state-et;
- nem növeli state versiont;
- nem növeli event sequence-et;
- nem módosítja a requestet;
- stabil diagnostics reasonnel tér vissza.

---

## 5. Production C# roadmap

### C.5A – Production architecture

**Státusz:** `COMPLETE_AND_ACCEPTED`

Rögzítve:

- project-határok;
- EngineSession;
- typed contractok;
- Godot production bridge;
- Python headless kapcsolat;
- fixture-alapú migráció;
- egyetlen C# authority.

### C.5B – Production engine foundation

**Státusz:** `READY_FOR_IMPLEMENTATION / PAUSED_CODEX_QUOTA`

Scope:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- core typed contractok;
- EngineSession;
- minimum runtime package loader;
- draw/end-turn;
- stale rejection;
- canonical serializer;
- comparison fixture adapter;
- Godot production bridge;
- candidate és GDScript regresszió.

Nem része:

- Wellspring gameplay;
- Beáramlás;
- Magnitúdó;
- Aura-payment;
- `play_card`;
- combat;
- ability executor;
- HTTP/gRPC;
- végleges packaging.

### C.5B utáni gameplay-sorrend

1. Wellspring production state;
2. player-visible Wellspring;
3. `infusion`/Beáramlás;
4. Magnitúdó-preflight;
5. Aura-payment;
6. simple Entity play;
7. Domain placement;
8. phase/priority;
9. reaction;
10. combat;
11. ability execution;
12. win/loss.

---

## 6. Open Questions és dokumentáció

Aktív kérdés–válasz pár:

- `docs/OPEN_QUESTIONS.md`;
- `docs/OPEN_QUESTIONS_DECISIONS.md`.

A korábbi `CURRENT_OPEN_QUESTIONS.md` tartalma beolvadt a kanonikus kérdés–válasz párba; a régi fájl a végső hivatkozás-ellenőrzés után eltávolítandó.

Aktív átnevezések:

- `CURRENT_PROTOTYPE_STATUS.md` → `PROTOTYPE_STATUS.md`;
- `CURRENT_RUNTIME_PACKAGE_STATUS.md` → `RUNTIME_PACKAGE_STATUS.md`;
- `CURRENT_CONTRACT_STATUS.md` → `CONTRACT_STATUS.md`;
- `CURRENT_ENGINE_CHECKPOINT.md` → `ENGINE_CHECKPOINT.md`.

Minden aktív dokumentumnak verzió, dátum és státusz szükséges.

---

## 7. Mit nem bizonyít még a rendszer?

- production C# engine;
- production C# runtime package loader;
- teljes player-facing bridge;
- Wellspring és payment gameplay;
- `play_card`;
- teljes phase/priority;
- reaction;
- combat;
- ability execution;
- Pecsét teljes state- és visibility-modell;
- victory/defeat;
- replay runner;
- production AI-vs-AI;
- Windows production packaging;
- végleges UI.

---

## 8. Codex nélküli aktív munkasáv

1. engine-dokumentumok verziózása és konszolidációja;
2. belső hivatkozások átvezetése;
3. engine docs teljes inventory;
4. specificationök és történeti fájlok státusza;
5. `Aeterna dokumentációk/` külön auditja;
6. keresztmappa-ellenőrzés;
7. kártyaadat- és szabályaudit;
8. kártyadizájn- és vizuális workflow.

Ellenőrizetlen production C# kód nem commitolható.

---

## 9. Commit előtti követelmény

A jelen dokumentációs munkaszakasz helyi utódfájlokat készít. GitHubon nem történt módosítás.

A felhasználói commit előtt szükséges:

- minden célútvonal ellenőrzése;
- régi → új fájlnévtérkép;
- verzió/dátum/státusz audit;
- Markdown-hivatkozás-ellenőrzés;
- tartalomvesztés- és ellentmondásellenőrzés;
- törlendő/archiválandó fájlok listája;
- Git diff;
- tiszta stage-scope;
- TEMP/log/generated fájlok kizárása.

---

## 10. Dokumentációs cleanup állapota – 2026-07-21

Az aktív engine-dokumentáció frissítése elkészült, de a repositoryban több felváltott előd még megtalálható.

Eltávolítandó:

- `docs/CURRENT_PROTOTYPE_STATUS.md`;
- `docs/CURRENT_RUNTIME_PACKAGE_STATUS.md`;
- `docs/CURRENT_CONTRACT_STATUS.md`;
- `docs/CURRENT_OPEN_QUESTIONS.md`;
- `docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`;
- `docs/checkpoints/AETERNA_CURRENT_ENGINE_CHECKPOINT_v1.1_2026-07-20.md`;
- `docs/ENGINE_OBJECT_IDENTITY_AND_ZONE_MOVE_PLAN_v0.1.md`;
- `docs/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md` a projektterv végleges dokumentációs mappába helyezése után.

Pontos teljes lista:

- `../Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`.
