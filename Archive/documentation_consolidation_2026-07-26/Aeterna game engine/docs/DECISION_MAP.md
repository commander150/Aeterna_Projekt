# AETERNA Game Engine – Decision Map

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.5\
**Dátum:** 2026-07-22\
**Státusz:** aktív rövid döntési és iránytérkép  
**Aktuális repository-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`

Ez a dokumentum röviden rögzíti:

- mi biztosan eldöntött;
- mi a jelenlegi működő referencia;
- mi a kiválasztott production runtime;
- mi lezárt, mi függő és mi elhalasztott;
- milyen sorrendben halad a fejlesztés;
- mit nem szabad összekeverni;
- milyen dokumentációs rendrakás szükséges.

Kapcsolódó aktív dokumentumok:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `TECHNOLOGY_DECISIONS.md`
- `ARCHITECTURE.md`
- `PROTOTYPE_STATUS.md`
- `CONTRACT_STATUS.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `checkpoints/ENGINE_CHECKPOINT.md`
- `../../Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.4.md`

---

## 1. Biztos projektcél

Az AETERNA elsődlegesen fizikai TCG.

A digitális programegység célja:

- szabálymodellezés és tesztelés;
- programbiztos kártyaadat;
- determinisztikus meccsfuttatás;
- AI-vs-AI;
- későbbi ember–AI játék;
- Godot-alapú kliens;
- végül a 0.0.1 zárt tesztkiadás.

A digitális rendszer nem írhatja felül a hivatalos 1.4v szabályforrásokat emberi döntés nélkül.

### 1.1 Playtest és szabályfelülvizsgálat

Az AETERNA még nem kapott teljes, szabályhű valódi játéktesztet. Több jelenlegi szabály- és balanszdöntés ezért elméleti tervezésre, részleges tesztre vagy szimulációs várakozásra épül.

Projektirányítási szabály:

- az elfogadott döntés az aktuális rulesetben canonical;
- az engine, AI és tesztek ezt kötelesek követni;
- a „playtestre vár” megjelölés nem teszi a szabályt opcionálissá;
- szabályhű playtest alapján bármely szabály, számérték vagy identitás felülvizsgálható;
- playtesteredmény nem módosít automatikusan szabályt;
- változtatáshoz explicit emberi döntés, döntésnapló és verziózott forrásátvezetés kell;
- a korábbi szabály, a teszteredmény és a módosítás indoka visszakereshető marad;
- stabil engine-contract csak az új canonical döntés elfogadása után módosítható.

---

## 2. Végleges technológiai irány

### Godot/GDScript

**Szerep:** vizuális kliensréteg

Feladata:

- jelenetek;
- input;
- UI;
- animáció;
- hang;
- debugpanelek;
- snapshot- és eventmegjelenítés;
- action requestek előkészítése.

Nem lehet szabályforrás.

### C#/.NET

**Szerep:** egyetlen production authoritative rules runtime

Feladata:

- MatchState;
- PlayerState;
- CardInstance;
- legal action;
- action request-validáció;
- state transitionök;
- eventek;
- snapshotok;
- hidden-information projection;
- determinisztika;
- később teljes gameplay, reakció, harc és győzelmi feltételek.

### Python

**Szerep:** külső adat-, audit-, AI-, batch- és elemzőeszközréteg

Feladata:

- XLSX/JSON/JSONL;
- runtime package build;
- validáció;
- audit;
- fixture-generálás;
- AI-vs-AI koordináció;
- batchfuttatás;
- balanszelemzés;
- riport;
- regression oracle.

A Python nem maradhat a C# mellett második production authoritative engine.

---

## 3. Runtime-jelöltek lezárt státusza

### Python sidecar + Godot

**Státusz:** `COMPLETE_AND_FROZEN`

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e` – `Fix Godot sidecar cancellation race warnings`

Bizonyított:

- localhost TCP;
- request/response;
- handshake;
- kontrollált shutdown;
- Emergency Shutdown;
- F8 parent watchdog;
- orphan cleanup;
- helyes canonical output;
- warning-, error- és crashmentes manuális futás.

Döntés:

- proofként és történeti referenciaként megmarad;
- production főmotorként nem folytatandó;
- új sidecar, TCP, watchdog vagy packaging fejlesztés most nem készül.

### Godot .NET/C# in-process runtime

**Státusz:** `COMPLETE_AND_ACCEPTED`

Lezáró commit:

`8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Bizonyított:

- pure C# runtime;
- Godot 4.7.1 .NET;
- .NET 8;
- közvetlen in-process futás;
- nincs külön engine-processz;
- nincs Python;
- nincs TCP;
- Debug és Release build;
- headless és visual proof;
- két manuális PASS;
- 100-run determinisztika;
- mutation negative proof;
- GDScript regressziók;
- nulla warning/error.

Közös canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

Döntés:

- a production authoritative runtime C#;
- a candidate proof megmarad regressziós bizonyítékként;
- nem nevezendő át közvetlenül production motorrá.

### GDScript authoritative runtime

**Státusz:** `REJECTED_AS_PRODUCTION_AUTHORITY`

A GDScript marad vizuális és adapterréteg.

Nem készül külön GDScript rules engine proof vagy teljes motor.

### Embedded Python

**Státusz:** `RESEARCH_ONLY_DEFERRED`

Csak későbbi, nélkülözhetetlen és nem authoritative Python-funkció esetén vizsgálható újra.

---

## 4. Stabil contract-first döntések

Elfogadott:

- előbb contract, utána implementáció;
- egy futásban egy authoritative state;
- frontend és AI nem találgat legalitást;
- kliens nem módosít MatchState-et;
- kliens action requestet küld;
- engine validál és transitiont hajt végre;
- player-visible és debug projection külön;
- hidden information védett;
- state mutation atomikus;
- rejected action nem mutál state-et;
- rejected request nem módosulhat;
- typed event és state version determinisztikus;
- canonical JSON explicit sorrendű;
- a runtime package statikus programadat.

---

## 5. Jelenlegi működő referencia

A Python minimal engine továbbra is:

- működő referencia;
- comparison oracle;
- regressziós alap;
- AI/batch kutatási forrás;
- production C# migráció ellenőrző alapja.

Bizonyított Python referenciafunkciók:

- state version guard;
- card instance registry;
- draw és end-turn;
- typed eventek;
- player-visible snapshot;
- Domain topology és occupancy;
- board projection;
- structural Entity placement;
- activity state;
- izolált Wellspring resource contract;
- deterministic AI trajectory.

Fontos elhatárolás:

A Python saját futásaiban authoritative, de nem a végleges production runtime.

---

## 6. Elkészült alapozási mérföldkövek

### Runtime package–Godot alap

**Státusz:** `COMPLETED_FOUNDATION`

Elkészült:

- Python runtime package build;
- XLSX exporter migráció;
- valós card/deck/lookup publish;
- Godot loader;
- registryk;
- sample contract loader;
- card reference resolver;
- consistency smoke;
- debug dashboard;
- Godot headless smoke.

### Runtime language decision gate

**Státusz:** `COMPLETE_AND_ACCEPTED`

Elkészült:

- közös fixture;
- Python reference output;
- Python sidecar proof;
- C# in-process proof;
- canonical differential comparison;
- automatizált és manuális tesztek;
- emberi döntés.

### C.5A – Production C# architecture plan

**Státusz:** `COMPLETE`

Rögzítve:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- typed public contractok;
- EngineSession;
- Godot production bridge;
- Python headless tooling kapcsolat;
- fixture-alapú migráció.

---

## 7. Production fejlesztési prioritás

### C.5B – Production C# engine foundation

**Státusz:** `COMPLETE_AND_ACCEPTED`

**Lezáró commit:** `931bf5571d541c752aa421a9f0626768bd8ffbe7`

Első scope:

- pure C# production engine;
- headless host;
- test runner;
- core contractok;
- EngineSession;
- minimum runtime package loader;
- draw/end-turn production reprodukció;
- Godot production bridge;
- candidate regresszió.

Bizonyított:

- production Debug/Release build és `13/13` teszt;
- viewer-safe event projection;
- strukturált JSON boundary rejection;
- canonical SHA-egyezés és `100/100` determinisztika;
- Godot pozitív és negatív production bridge smoke.

A C.5B-nek nem része:

- új gameplay;
- Wellspring;
- Beáramlás;
- Aura;
- Magnitúdó;
- `play_card`;
- harc;
- effect engine;
- HTTP;
- gRPC;
- production packaging.

### Következő: P3 első production gameplay-migráció

**Státusz:** `NEXT`

Első scope:

1. Wellspring production state;
2. player-visible Wellspring.

Beáramlás, Magnitúdó, Aura-payment és `play_card` csak a Wellspring-szakasz külön elfogadása után következik.

---

## 8. Gameplay-engine queue

A production C# alap után:

1. Wellspring PlayerState- és MatchState-integráció.
2. Player-visible Wellspring summary.
3. Beáramlás precondition.
4. Beáramlás transition és typed event.
5. Magnitúdó-preflight.
6. Aura-source és payment contract.
7. Activity mutation transition.
8. Entitás kijátszási precondition.
9. `play_card` action.
10. Hand → Domain transition.
11. Entry-state.
12. Teljesebb phase és priority.
13. Reaction.
14. Combat.
15. Ability execution.
16. Win/loss.

**Státusz:** `QUEUED_AFTER_C5B`

---

## 9. Python–C# kommunikáció

Első tervezett forma:

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

A Python csak a C# által kiadott legal actionökből választhat.

Localhost HTTP vagy gRPC:

**Státusz:** `DEFERRED_UNTIL_MEASURED_NEED`

Nem készül addig, amíg teljesítménymérés nem igazolja.

---

## 10. Nem programozási aktív prioritás

1. Kártyaadat- és szabályaudit.
2. LOOKUPS- és ID-contract munka.
3. Kártyadizájn-workflow tervezése.

Nem készül új párhuzamos dokumentum, ha a tartalom meglévő aktív fájlba illeszthető.

---

## 11. Dokumentációs állapot

A nagy dokumentációs és archiválási rendezés lezárult. A további dokumentáció nem önálló projektprioritás.

Frissítés csak technikai mérföldkő, contract- vagy authority-változás, fontos döntés vagy biztonságos checkpoint esetén szükséges.

Tilos:

- új párhuzamos authority-dokumentum indokolatlan létrehozása;
- tartalomvesztés;
- nyitott kérdés elvesztése;
- aktív és történeti forrás összekeverése.

---

## 12. Nyitott, de nem blokkoló tételek

- production C# Windows packaging;
- self-contained vagy prerequisite modell;
- runtime diagnostic log;
- hosszabb soak teszt;
- Python headless controller;
- production AI-vs-AI;
- replay;
- Godot stretch és maximized-window policy;
- Python unittest monolitikus discovery adósság;
- GDScript-fájlok szerepkategorizálása;
- sidecar proof archiválási stratégia;
- C# whitespace-megfigyelés.

---

## 13. C# whitespace-megfigyelés

**Státusz:** `OBSERVE_ONLY_NON_BLOCKING`

A `CsharpMinimalRuntimeProof.cs` két vizsgált változata logikailag azonos volt.

Eltérés:

- 4 szóközös behúzás;
- tabulátoros behúzás.

Döntés:

- nincs azonnali javítás;
- nincs whitespace-only commit;
- ismétlődés esetén `.editorconfig` vagy egységes formázási szabály készül.

---

## 14. Rövid irányelv

> **A current canonical szabályt a C# production engine-ben implementáljuk és teszteljük. A Godot/GDScript megjeleníti, a Python pedig külső eszközként teszteli, elemzi és AI-val vezérli. A szabályhű playtest eredménye alapján később explicit, verziózott döntéssel módosíthatjuk.**
