# AETERNA Game Engine – Runtime Engine Language Decision Gate

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2  
**Dátum:** 2026-07-20  
**Státusz:** lezárt technológiai döntési kapu és aktív döntési referencia  
**Döntés:** Godot/GDScript vizuális réteg + C# authoritative runtime + Python külső tooling  
**Aktuális repository-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

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
- `CURRENT_OPEN_QUESTIONS.md`
- `CURRENT_CONTRACT_STATUS.md`
- `TECHNOLOGY_DECISIONS.md`
- `ARCHITECTURE.md`
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`

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
- később a teljes gameplay, reakció-, harc- és győzelmi rendszer.

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

A Python és a C# később API-szerű felületen kommunikálhat.

### Első tervezett forma

`Python → Aeterna.Engine.Headless → JSON/JSONL → Python`

A Python:

- fixture-t vagy scenario-t ad át;
- elindítja a C# headless hostot;
- eredményt gyűjt;
- statisztikát készít;
- AI-akciót választhat a C# legal action listájából.

A C#:

- létrehozza és módosítja a meccsállapotot;
- validálja az action requestet;
- eventet és snapshotot készít;
- győzelmet vagy vereséget állapít meg.

### Későbbi feltételes forma

Localhost HTTP vagy gRPC csak akkor készülhet, ha mérések bizonyítják, hogy:

- a folyamatindítás jelentős teljesítményprobléma;
- hosszú életű C# service szükséges;
- nagy mennyiségű folyamatos Python–C# interakció történik.

### Nem használható

- HTTP a Godot és a C# között;
- Python a Godot frame-loop kötelező részeként;
- API, amely megkerüli a C# `SubmitAction` authority-kapuját;
- Python által közvetlenül módosított C# MatchState.

---

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

## 8. Következő technikai szakasz

### C.5A – C# production engine architektúraterv

**Státusz:** `COMPLETE`

Rögzítve:

- production project-határok;
- pure C# engine;
- headless host;
- tesztprojekt;
- typed contractok;
- EngineSession;
- Godot production bridge;
- Python headless tooling kapcsolat;
- kontrollált fixture-alapú migráció.

### C.5B – Production C# engine foundation

**Státusz:** `READY_FOR_IMPLEMENTATION`

**Ideiglenes állapot:** `PAUSED – CODEX QUOTA`

Első scope:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- core contractok;
- EngineSession;
- minimum runtime package loader;
- draw/end-turn reprodukció;
- production fixture adapter;
- Godot production bridge;
- RuntimeCandidate regresszió.

Nem része:

- Wellspring gameplay integráció;
- Beáramlás;
- Aura-payment;
- Magnitúdó;
- `play_card`;
- harc;
- effect engine;
- trigger;
- HTTP;
- gRPC;
- production packaging.

---

## 9. Még nyitott technikai bizonyítások

A runtime-nyelvi döntést nem blokkolják, de a későbbi release-ek előtt szükségesek:

- production C# Windows export;
- self-contained vagy egyszerű prerequisite packaging;
- tiszta tesztgépes indítás;
- hosszabb soak teszt;
- teljes gameplay-migráció;
- production runtime diagnosztikai log;
- Python headless controller;
- AI-vs-AI production C# futás;
- replay és reprodukálhatóság;
- teljesítmény és memória mérése valósabb meccseken.

A végleges nyelvi döntés csak új, erős és AETERNA-specifikus technikai bizonyíték alapján nyitható újra.

---

## 10. Dokumentumkezelési szabály

A dokumentumszaporodás elkerülése érdekében:

- új alfeladathoz alapértelmezetten nem készül új dokumentum;
- új eredmény a természetes aktív fődokumentumba kerüljön;
- külön fájl csak önálló, tartós és más dokumentumba nem illeszthető canonical témának készülhet;
- a `CURRENT_ENGINE_CHECKPOINT.md` a fő technikai folytatási pont;
- történeti dokumentum nem törlendő audit nélkül;
- azonos szerepű párhuzamos current dokumentum nem hozható létre;
- később dokumentumaudit és tartalomvesztés nélküli összevonás szükséges;
- nyitott kérdés vagy korábbi döntés nem veszhet el merge során.

---

## 11. Rövid aktuális státusz

**Döntési kapu:** lezárva.  
**Authoritative runtime:** C#/.NET.  
**Vizuális kliens:** Godot/GDScript.  
**Külső tooling, AI és batch:** Python.  
**Python sidecar proof:** `COMPLETE AND FROZEN`.  
**C# in-process proof:** `COMPLETE AND ACCEPTED`.  
**Közös canonical SHA:** `650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`.  
**Következő kódolási szakasz:** C.5B production C# engine foundation.  
**Kódolási állapot:** ideiglenesen szünetel a Codex használati kerete miatt.  
**Codex nélküli aktív sáv:** meglévő dokumentumok aktualizálása, dokumentumaudit előkészítése, projekt-térkép, open questions és kártyaaudit.
