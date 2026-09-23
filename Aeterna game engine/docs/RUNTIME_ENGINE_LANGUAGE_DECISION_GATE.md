# AETERNA Game Engine – Runtime Engine Language Decision Gate

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.4
**Dátum:** 2026-09-05
**Státusz:** lezárt technológiai döntési kapu és aktív döntési referencia  
**Döntés:** Godot/GDScript vizuális réteg + C# authoritative runtime + Python külső tooling  
**Aktuális repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9` – `engine: add aeternal outcome and terminal match result`

Ez a dokumentum az AETERNA hosszú távú authoritative rules runtime nyelvi és futási modelljének lezárt döntési kapuja.

A döntési kapu célja annak bizonyítása volt, hogy melyik runtime-modell ad:

- stabil működést;
- tiszta authoritative state-et;
- determinisztikus és jól tesztelhető szabálymotort;
- megbízható Godot-integrációt;
- kezelhető Windows-futtatási modellt;
- hosszú távon használható AI-, batch-, replay- és diagnostics-alapot.

A döntés nem a Python elvetése. A Python referenciaimplementációként és külső eszközrétegként megmarad.

Kapcsolódó aktív dokumentumok:

- `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `CONTRACT_STATUS.md`
- `TECHNOLOGY_DECISIONS.md`
- `ARCHITECTURE.md`
- `../../project/status/checkpoints/ENGINE_CHECKPOINT.md`
- `../../project/planning/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.9.md`

---

## 1. Végleges döntés

Az AETERNA tervezett runtime-architektúrája:

### Godot és GDScript

Feladata:

- megjelenítés;
- scene-ek;
- input;
- animációk;
- hangok;
- vizuális állapotfrissítés;
- menük és panelek;
- debugnézetek;
- a C# motor eredményeinek megjelenítése.

A GDScript nem lehet a kanonikus játékszabályok gazdája.

### C#

Feladata:

- egyetlen authoritative MatchState;
- legal action számítás;
- action request-validáció;
- state transitionök;
- eventek;
- snapshotok;
- hidden-information projection;
- determinisztikus működés;
- teljes authoritative gameplay, beleértve Reaction/Priority, Combat/Pecsét és győzelmi rendszert.

Új kanonikus játékszabály kizárólag a production C# engine-ben implementálható.

### Python

Feladata:

- adatpipeline;
- XLSX/JSON/JSONL feldolgozás;
- runtime package build és validáció;
- kártyaaudit;
- fixture- és tesztgenerálás;
- AI- és batchvezérlés;
- tömeges headless C# futások;
- balanszelemzés;
- riport és diagnosztika.

A Python nem maradhat a C# mellett külön fejlődő második kanonikus szabálymotorként.

---

## 2. A döntési kapu eredménye

### 2.1 Python–Godot sidecar jelölt

**Státusz:** `COMPLETE AND FROZEN`

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e` – `Fix Godot sidecar cancellation race warnings`

Bizonyított működés:

- külön Python engine-processz;
- localhost TCP;
- verziózott request/response;
- frame-olvasás és írás;
- timeout és cancellation;
- kontrollált shutdown;
- Emergency Shutdown;
- Godot F8 után parent watchdog;
- orphan-processz elleni védelem;
- normál PASS;
- manuális warning-, error- és crashmentes futás.

Előnyök:

- a meglévő Python engine közvetlenül használható;
- erős headless tesztelés;
- AI-, audit- és batch-tooling közvetlenül elérhető;
- processhatár egyértelmű authority-határt biztosít;
- Python referencia és termékruntime ugyanaz lehetne.

Bizonyított költségek:

- külön processz;
- TCP és framing;
- launcher;
- runtime config;
- handshake;
- shutdown-protokoll;
- cancellation-race kezelése;
- watchdog;
- orphan-audit;
- külön Python-környezet;
- összetettebb packaging és diagnosztika.

A jelölt működőképes, de production főmotorként nem folytatandó.

### 2.2 Godot .NET/C# in-process jelölt

**Státusz:** `COMPLETE AND ACCEPTED`

Lezáró commit:

`8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Környezet:

- Godot `4.7.1.stable.mono.official.a13da4feb`;
- .NET SDK `8.0.423`;
- `Microsoft.NETCore.App 8.0.29`;
- target framework `net8.0`.

Bizonyított működés:

- pure C# runtime candidate;
- közvetlen in-process Godot-hívás;
- külön engine-processz nélkül;
- Python-processz nélkül;
- TCP/listener nélkül;
- Debug és Release build;
- nulla C# warning/error;
- nulla Godot warning/error;
- candidate console proof;
- Godot headless proof;
- valódi renderelt visual proof;
- 100-run determinisztika;
- mutation negative proof;
- candidate és GDScript regressziók;
- manuális első és második PASS;
- F8 után szabályos Godot-ablakbezárás;
- crash nélkül.

Előnyök:

- nincs IPC;
- nincs külön engine lifecycle;
- nincs watchdog;
- nincs orphan engine-processz;
- a szabálymotor ugyanabban a processzben fut, mint a Godot;
- statikusan típusos;
- Godot nélküli pure C# tesztút megtartható;
- a meglévő GDScript-réteg mellette tovább működik.

Költségek és korlátok:

- Godot .NET Editor szükséges fejlesztéshez;
- kompatibilis .NET SDK szükséges;
- megjelenik egy második Godot-oldali nyelv;
- a Python referenciafunkciókat kontrolláltan át kell migrálni;
- a végleges Windows packaging még production engine-nel bizonyítandó.

---

## 3. Közös comparison fixture

Mindkét fő jelölt ugyanazt a `minimal_draw_end_turn_v1` fixture-t használta.

Kötelező lépések:

1. canonical initial state;
2. `draw_card` player 1;
3. stale `expected_state_version` request elutasítása state mutation nélkül;
4. `end_turn` player 1 → player 2;
5. `draw_card` player 2;
6. player-visible snapshot mindkét játékos számára;
7. typed event log;
8. legal action checkpointok;
9. canonical JSON;
10. determinisztikus ismétlés.

Közös helyes canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

A Python- és C#-jelölt ugyanazt a kanonikus eredményt állította elő.

A C# mutation proof:

- fixture seed `1 → 2`;
- eltérő SHA;
- elvárt `CANONICAL_SHA_MISMATCH`.

Ez bizonyította, hogy a C# nem előre eltárolt eredményt vagy SHA-t ad vissza.

---

## 4. Miért a C# lett az authoritative runtime?

A két jelölt szabályhelyességi és determinisztikai alapja egyaránt bizonyított.

A fő különbség a futási és karbantartási összetettségben jelent meg.

A C# ugyanazt a kanonikus eredményt:

- közvetlenül a Godot-folyamatban;
- külön processz nélkül;
- TCP nélkül;
- launcher nélkül;
- shutdown-protokoll nélkül;
- watchdog nélkül

állította elő.

A Python sidecar működőképes, de a C# egy teljes köztes futási infrastruktúrát tesz szükségtelenné.

A döntés ezért nem azon alapul, hogy a Python gyenge lenne szabálymotorhoz, hanem azon, hogy a C# az AETERNA Godot-termékruntime-jában egyszerűbb és természetesebb integrációt biztosít.

---

## 5. Elvetett vagy feltételes modellek

### 5.1 Python authoritative sidecar

Elvetve production főirányként.

Megmarad:

- referenciaimplementáció;
- regressziós orákulum;
- AI- és batch-alap;
- toolingforrás;
- migrációs összehasonlítás.

Nem készül hozzá jelenleg:

- production packaging;
- új TCP-protokoll;
- új launcherfunkció;
- további watchdogfejlesztés;
- új sidecar UI.

### 5.2 Tiszta GDScript rules runtime

Nem szükséges további proof.

A C# és Python proof elegendő döntési információt adott.

GDScriptben továbbra is maradhat:

- UI;
- scene-vezérlés;
- animáció;
- vizuális adapter;
- debugeszköz.

GDScriptben nem készülhet külön authoritative gameplay engine.

### 5.3 Beágyazott Python a C# vagy Godot runtime-ban

Jelenleg nem indokolt.

Kockázatok:

- CPython runtime és verziófüggőség;
- Python.NET vagy más bridge;
- GIL;
- típuskonverzió;
- packaging;
- közös processzben bekövetkező natív crash;
- három nyelv futásidejű szoros összekapcsolása.

Csak későbbi, jól elkülöníthető és nélkülözhetetlen Python-specifikus funkció esetén vizsgálható újra.

### 5.4 C# és Python között megosztott kanonikus szabálymotor

Elvetve.

Tilos olyan felosztás, amelyben:

- egyes játékszabályok C#-ban;
- más szabályok Pythonban;
- mindkettő authoritative módon

működnek.

Ez contracteltérést, determinisztikai kockázatot és nehéz hibakeresést okozna.

---

## 6. Python–C# kommunikációs irány

Az elsődleges külső tooling-határ már implementált alap:

```text
Python
  ↓ subprocess + JSON/JSONL / file / stdin
Aeterna.Engine.Headless
  ↓ canonical JSON/JSONL
Python
```

A Python:

- fixture-t vagy scenario-t adhat át;
- elindíthatja a C# headless hostot;
- eredményt gyűjthet;
- statisztikát készíthet;
- AI-akciót választhat a C# által kiadott viewer-safe snapshot és legal action lista alapján.

A C#:

- létrehozza és módosítja az authoritative meccsállapotot;
- validálja az action requestet;
- eventet és snapshotot készít;
- `MatchResult` állapotig vezeti a meccset;
- nem fogad el Pythonból közvetlen state mutationt.

Későbbi feltételes forma:

Localhost HTTP vagy gRPC csak akkor készülhet, ha mérések bizonyítják, hogy:

- a folyamatindítás jelentős teljesítményprobléma;
- hosszú életű C# service szükséges;
- nagy mennyiségű folyamatos Python–C# interakció történik.

Ez reserved extension point, nem current production requirement.

Nem használható:

- HTTP/TCP/gRPC a Godot és a C# production rules path között;
- Python a Godot frame-loop kötelező részeként;
- API, amely megkerüli a C# `SubmitAction`/engine transition authority-kapuját;
- Python által közvetlenül módosított C# `MatchState`;
- külön Python legality engine AI számára.

## 7. Production C# migrációs szabályok

A jelenlegi `Aeterna.RuntimeCandidate` státusza:

`ACCEPTED_PROOF`

Nem szabad:

- átnevezni production motorrá;
- közvetlenül korlátlanul továbbépíteni;
- törölni;
- átformázni tömegesen;
- fixture-specifikus logikát production contractként rögzíteni.

A production engine külön indul:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- Godot production bridge.

A migráció prioritási sorrendje:

1. hivatalos szabályforrás;
2. aktív contract/specifikáció;
3. elfogadott fixture;
4. Python referencia;
5. C# production implementáció.

A Python nem automatikus szabályspecifikáció.

Minden migrációs egységhez szükséges:

- pontos hivatalos viselkedés;
- typed contract;
- pozitív fixture;
- negatív fixture;
- determinisztikai teszt;
- Python–C# összevetés;
- hidden-information ellenőrzés;
- rejected action state-immutability;
- Godot regresszió.

---

## 8. Production technikai szakaszok

### C.5A – C# production engine architektúraterv

**Státusz:** `COMPLETE`

### C.5B – Production C# engine foundation

**Státusz:** `COMPLETE_AND_ACCEPTED`

**Lezáró commit:** `931bf5571d541c752aa421a9f0626768bd8ffbe7`

Történeti minimum scope:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- core contractok;
- `EngineSession`;
- minimum runtime package loader;
- draw/end-turn reprodukció;
- production fixture adapter;
- Godot production bridge;
- RuntimeCandidate regresszió.

A C.5B scope-határ történeti. Az azóta megvalósult production rétegek ugyanebben
a C# authoritative architektúrában épültek tovább.

### Korábbi production gameplay/ability foundation

**Státusz:** `COMPLETE_AND_ACCEPTED`

Többek között:

- Wellspring / Beáramlás;
- Magnitúdó/Aura preflight;
- Domain / `play_card`;
- canonical ability/effect foundation;
- damage/vitals;
- continuous/modifier/keyword/duration;
- draw/reference runtime.

### Explicit Phase Foundation v1

**Státusz:** `COMPLETE_AND_ACCEPTED`

Lezáró commit:

`2608345b61526097fc0b118f05461f92cfed0a95`

### Reaction / Priority Foundation v1

**Státusz:** `COMPLETE_AND_ACCEPTED`

Lezáró commit:

`f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`

### Combat + Pecsét Foundation C0–C6

**Státusz:** `COMPLETE_AND_ACCEPTED`

Current production base:

`0862e1002dbef81ee203852714d377592272a0e9`

Current foundation többek között:

- canonical setup/Jóslat;
- AttackCommit;
- intervention / DefenseCommit;
- Combat ReactionWindows;
- Entity Combat;
- Seal break/reveal/Surge;
- Gondviselés;
- Aeternal terminal outcome;
- authoritative `MatchResult`.

A nyelvi döntési gate szempontjából ez fontos follow-up evidence:
a kiválasztott C# same-process architecture a nagyobb gameplay foundationökön is működőképes maradt.

### Current next gate

`VS1_READINESS_REQUIRED`

Következő major product-facing cél:

`VS1 / M6 – első ténylegesen játszható vertical slice`

## 9. Még nyitott technikai bizonyítások

A runtime-nyelvi döntést nem blokkolják és nem nyitják újra automatikusan.

VS1 felé current nyitott:

- canonical VS1 deck/card/mechanic readiness audit;
- szükséges content/ability blocker lezárás;
- simple fair AI;
- match orchestration;
- minimal playable Godot UI;
- teljes human-vs-AI meccs;
- reproducible AI-vs-AI smoke.

0.0.1 / release felé később nyitott többek között:

- production Windows export;
- self-contained vagy egyszerű prerequisite packaging;
- tiszta tesztgépes indítás;
- hosszabb soak teszt;
- replay/bug-report/diagnostics product workflow;
- profile/save/tutorial/collection/economy;
- teljesítmény és memória mérése valósabb meccseken;
- final compatibility/release policy.

Már nem nyitott nyelvi-gate bizonyítás:

- production C# engine foundation;
- Godot production bridge foundation;
- Python headless C# tooling alap;
- Reaction/Priority;
- Combat/Pecsét;
- terminal Aeternal/MatchResult core.

A végleges nyelvi döntés csak új, erős és AETERNA-specifikus technikai bizonyíték alapján nyitható újra.
A jövőbeli feature-hiány önmagában nem ilyen bizonyíték.

## 10. Dokumentumkezelési szabály

A dokumentumszaporodás elkerülése érdekében:

- új alfeladathoz alapértelmezetten nem készül új dokumentum;
- új eredmény a természetes aktív fődokumentumba kerüljön;
- külön fájl csak önálló, tartós és más dokumentumba nem illeszthető canonical témának készülhet;
- a `../../project/status/checkpoints/ENGINE_CHECKPOINT.md` a fő technikai folytatási pont;
- azonos szerepű párhuzamos current dokumentum nem hozható létre;
- fájlnévben verziózott current dokumentum ugyanazon fájl rename-jével lép új verzióra;
- korábbi current verziót normál esetben a Git history őrzi;
- Archive csak valódi historical/deprecated/replaced szerepre szolgál;
- merge/migration során nyitott kérdés vagy döntés nem veszhet el;
- current dokumentációs sync targeted patch + diff/consistency review módszerrel történik.

Ez a nyelvi döntési gate aktív reference marad, de nem napi roadmap-dokumentum.

## 11. Rövid aktuális státusz

**Döntési kapu:** lezárva.
**Authoritative runtime:** C#/.NET.
**Vizuális kliens:** Godot/GDScript.
**Külső tooling, AI/batch koordináció és reference:** Python.
**Godot–C# production rules path:** same-process.
**Python sidecar proof:** `COMPLETE_AND_FROZEN`.
**C# in-process proof:** `COMPLETE_AND_ACCEPTED`.
**Közös történeti candidate canonical SHA:** `650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`.
**C.5B production foundation:** `COMPLETE_AND_ACCEPTED`.
**Explicit Phase Foundation v1:** `COMPLETE_AND_ACCEPTED`.
**Reaction / Priority Foundation v1:** `COMPLETE_AND_ACCEPTED`.
**Combat + Pecsét Foundation C0–C6:** `COMPLETE_AND_ACCEPTED`.
**Current production base:** `0862e1002dbef81ee203852714d377592272a0e9`.
**Current OQ:** `52 answered / 15 partly_answered / 7 deferred / 0 open`.
**Current next gate:** `VS1_READINESS_REQUIRED`.
**Következő major product-facing cél:** `VS1 / M6 – első ténylegesen játszható vertical slice`.
**Nyelvi döntés újranyitása:** `NOT_REQUIRED`.
