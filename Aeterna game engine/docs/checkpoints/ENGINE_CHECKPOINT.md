# AETERNA Game Engine – Engine Checkpoint

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.3  
**Dátum:** 2026-07-21  
**Státusz:** aktív elsődleges technikai és dokumentációs folytatási checkpoint  
**Felváltott fájlok:** `CURRENT_ENGINE_CHECKPOINT.md`, `AETERNA_CURRENT_ENGINE_CHECKPOINT_v1.1_2026-07-20.md`  
**Aktuális repository HEAD:** `32a0cbea24c82dda440f1a053b454ef03949d8ae` – `docs update 2`  
**Aktuális C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Ez a dokumentum az AETERNA Game Engine biztonságos folytatási pontja.

Nem hivatalos játékszabály és nem teljes production engine-specifikáció.

---

## 1. Rövid állapot

A runtime-nyelvi döntési kapu lezárult.

Elfogadott architektúra:

```text
Godot/GDScript = vizuális kliens
C#/.NET         = egyetlen production authoritative rules engine
Python          = external tooling, reference, AI és batch controller
```

Proofok:

- Python–Godot sidecar: `COMPLETE_AND_FROZEN`;
- Godot .NET/C# in-process candidate: `COMPLETE_AND_ACCEPTED`.

Canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

A production C# engine még nem létezik.

---

## 2. Forráselsőbbség

1. hivatalos 1.4v szabályfőforrások;
2. elfogadott emberi döntések;
3. 0.0.1 termékcél;
4. aktuális projektterv v6.2;
5. projekt-térkép v1.5;
6. jelen checkpoint;
7. runtime-nyelvi döntési gate;
8. architecture és technology decisions;
9. aktuális státuszdokumentumok;
10. Open Questions kérdés–válasz pár;
11. specificationök;
12. Python reference és proofok;
13. történeti dokumentumok.

---

## 3. Python reference engine

Státusz:

`REFERENCE_IMPLEMENTATION / COMPARISON_ORACLE / EXTERNAL_TOOLING_BASE`

Bizonyított fő elemek:

- MatchState és PlayerState;
- state version guard;
- card instance registry;
- deck/hand/discard instance-zónák;
- draw és end-turn;
- typed zone/turn eventek;
- invariánsok;
- player-visible snapshot;
- hidden-information alap;
- Domain topology és occupancy;
- public board;
- structural Entity placement option;
- activity state;
- izolált Wellspring és resource summary;
- deterministic AI trajectory.

A Python nem production authority.

---

## 4. Python–Godot sidecar proof

Státusz:

`COMPLETE_AND_FROZEN`

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e`

Bizonyította:

- külön Python processz;
- localhost TCP;
- request/response;
- lifecycle és shutdown;
- parent watchdog;
- orphan elleni védelem;
- canonical fixture-egyezés.

Production főmotorként nem folytatandó.

---

## 5. C# in-process candidate proof

Státusz:

`COMPLETE_AND_ACCEPTED`

Proof-bázis:

`8e5ee64e42e1657e10f3413444bb870524ee07f9`

Bizonyította:

- pure C# runtime candidate;
- Godot .NET in-process bridge;
- Python, TCP és külön engine-processz nélküli futás;
- draw, stale reject és end-turn;
- legal action, snapshot és typed event;
- canonical JSON/SHA;
- 100-run determinisztika;
- mutation negative proof;
- Debug/Release;
- headless/visual PASS;
- nulla warning/error.

A candidate `ACCEPTED_PROOF`, nem nevezendő át közvetlenül production motorrá.

---

## 6. Production C# irány

Tervezett projektek:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`.

Publikus EngineSession-határ:

- `CreateMatch`;
- `GetPlayerSnapshot`;
- `ListLegalActions`;
- `SubmitAction`;
- `GetEvents`;
- `GetMatchResult`.

State mutation csak a C# authorityn keresztül történhet.

---

## 7. C.5A és C.5B

### C.5A – Production architecture

`COMPLETE_AND_ACCEPTED`

### C.5B – Production engine foundation

`READY_FOR_IMPLEMENTATION / PAUSED_CODEX_QUOTA`

Scope:

- pure C# engine;
- headless host;
- test project;
- typed core contractok;
- EngineSession;
- minimum runtime package loader;
- draw/end-turn/stale reject;
- canonical serializer és fixture adapter;
- Godot production bridge;
- candidate és GDScript regresszió.

Nem tartalmaz új gameplayt.

---

## 8. C.5B utáni gameplay-sorrend

1. Wellspring production state;
2. player-visible Wellspring;
3. `infusion` / Beáramlás;
4. Magnitúdó-preflight;
5. Aura-payment;
6. simple Entity `play_card`;
7. Domain placement;
8. phase/priority;
9. reaction;
10. combat;
11. ability execution;
12. victory/defeat.

---

## 9. Dokumentációs állapot

A repositoryban a 2026-07-20-i docs commitok már megtalálhatók.

Elkészült:

- architektúra és technológiai döntések frissítése;
- runtime decision gate lezárása;
- prototype/runtime package/contract status utódok;
- Open Questions 2.0 kérdés–válasz konszolidáció;
- specificationök és README-k első frissítési köre;
- történeti checkpoint rövidítése;
- projektterv v6.2 első változata.

A docs commitok azonban több régi elődöt nem töröltek, és egy projektterv rossz mappába került.

---

## 10. Azonosított duplikációk

Kijelölt utód után törlendő:

- `CURRENT_PROTOTYPE_STATUS.md` → `PROTOTYPE_STATUS.md`;
- `CURRENT_RUNTIME_PACKAGE_STATUS.md` → `RUNTIME_PACKAGE_STATUS.md`;
- `CURRENT_CONTRACT_STATUS.md` → `CONTRACT_STATUS.md`;
- `CURRENT_OPEN_QUESTIONS.md` → `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md`;
- `CURRENT_ENGINE_CHECKPOINT.md` → `ENGINE_CHECKPOINT.md`;
- `AETERNA_CURRENT_ENGINE_CHECKPOINT_v1.1_2026-07-20.md` → `ENGINE_CHECKPOINT.md`.

További cleanup:

- engine docs alá került v6.2 projektterv eltávolítása;
- v5.1/v6.0/v6.1 tervek eltávolítása a v6.2 után;
- v1.2/v1.3/v1.4 projekt-térképek eltávolítása a v1.5 után;
- `DOCUMENTATION_CLEANUP_CHECKPOINT_2026-07-03.md` eltávolítása;
- két elavult gyökérszintű engine-összefoglaló eltávolítása;
- teljesült object identity/zone move terv eltávolítása.

Pontos lista:

- `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`.

---

## 11. Whitespace-only kódeltérés

Commit:

`243620df0ad393f782b292ed73f306e8ae4ceea5`

Érintett fájl:

- `Godot/scripts/debug/CsharpMinimalRuntimeProof.cs`.

A változás kizárólag négy szóköz → tab behúzás; logikai eltérés nincs.

Státusz:

`NON_BLOCKING_WHITESPACE_ONLY`

A végső cleanupnál:

- visszaállítandó, vagy
- külön formázási commitként kezelendő.

---

## 12. Aktuális nem programozási munkasáv

1. root README és mappaindexek frissítése;
2. projekt-térkép v1.5 beillesztése;
3. projektterv v6.2 végleges helyre tétele;
4. régi elődök eltávolítása;
5. belső hivatkozásaudit;
6. verzió/dátum/státusz audit;
7. Git diff és commit-scope ellenőrzés;
8. `Aeterna dokumentációk/reference`, `archive_review` és `generated_review` mély auditja;
9. keresztmappa-ellenőrzés.

---

## 13. Törlés előtti kapu

Minden törlés előtt:

- az utód létezik;
- az utód tartalma teljes;
- nincs aktív hivatkozás az elődre;
- az Open Questions tartalma nem veszett el;
- Git diff ellenőrzött;
- a törlés nem keveredik runtime kódmódosítással;
- a felhasználó hagyja jóvá a stage-scope-ot.

A Git-történet megőrzi az eltávolított elődöket.

---

## 14. Biztonságos újrakezdési utasítás

Új beszélgetés vagy hosszabb megszakítás után:

1. olvasd el ezt az `ENGINE_CHECKPOINT.md` fájlt;
2. ellenőrizd az aktuális repository HEAD-et;
3. ne nyisd újra a lezárt runtime-nyelvi döntést;
4. dokumentációs munka esetén a projekt-térkép v1.5 cleanup-listáját kövesd;
5. kódolásnál C.5B a következő feladat;
6. production C# engine-t ne tekints késznek;
7. a RuntimeCandidate és sidecar proofot regressziós bizonyítékként őrizd meg;
8. régi fájlt csak utód- és hivatkozásellenőrzés után törölj.

---

## 15. Rövid folytatási összefoglaló

- Repository HEAD: `32a0cbea24c82dda440f1a053b454ef03949d8ae`.
- C# proof-bázis: `8e5ee64e42e1657e10f3413444bb870524ee07f9`.
- Python sidecar: kész és befagyasztva.
- C# candidate: kész és elfogadva.
- Production C# engine: még nem létezik.
- C.5A: kész.
- C.5B: előkészítve, Codex-korlát miatt szünetel.
- Engine docs aktív rétegének auditja: lényegében kész.
- Duplikációs térkép: kész.
- Régi fájlok tényleges eltávolítása: a következő repository cleanup commit feladata.
- Utána: `Aeterna dokumentációk/` mély almappaaudit és végső keresztellenőrzés.
