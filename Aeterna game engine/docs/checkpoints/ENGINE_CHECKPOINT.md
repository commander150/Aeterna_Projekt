# AETERNA Game Engine – Engine Checkpoint

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2  
**Dátum:** 2026-07-20  
**Státusz:** aktív elsődleges technikai folytatási checkpoint  
**Felváltott fájl:** `CURRENT_ENGINE_CHECKPOINT.md`  
**Célútvonal:** `Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`  
**Aktuális bizonyított repository-commit:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`  
**Commitüzenet:** `Add minimal C# runtime candidate proof`

A repository dokumentumai a jelen dokumentációs munkaszakasz alatt nem módosultak. Ez a fájl helyi utódfájl, amelyet a többi ellenőrzött dokumentummal együtt, a végső átadási audit után kell a repositoryba beilleszteni és commitolni.

A korábbi checkpoint bázisa:

- `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`
- `Add minimal Wellspring resource contracts`

Ez a dokumentum felváltja a 2026-07-15-i, elsősorban a Python minimal engine állapotára épülő technikai checkpointot.

Feladata:

- biztonságos folytatási pont biztosítása új beszélgetés vagy hosszabb munkaszünet után;
- a Python- és C# runtime-jelöltek bizonyított állapotának rögzítése;
- a lezárt runtime-nyelvi és architektúradöntés megőrzése;
- az elkészült, előkészített, szünetelő és halasztott feladatok elhatárolása;
- a dokumentációs átnevezési és konszolidációs munka állapotának rögzítése;
- a végső repository-beillesztés előtti ellenőrzési követelmények megőrzése.

Ez nem hivatalos játékszabály és nem teljes production engine-specifikáció.

---

## 1. Rövid állapot

A runtime-nyelvi döntési kapu lezárult.

Két, azonos összehasonlító fixture-t feldolgozó technikai jelölt készült el:

1. Python sidecar + Godot integráció;
2. Godot .NET/C# közvetlen, processzen belüli runtime-jelölt.

Mindkét jelölt ugyanazt a kanonikus eredményt állította elő:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

Elfogadott hosszú távú technikai irány:

- **Godot és GDScript:** vizuális réteg, jelenetek, input, animációk és UI;
- **C#:** az egyetlen kanonikus production játékmotor és szabályi authority;
- **Python:** külső adatfeldolgozó, auditáló, tesztelő, elemző, AI- és szimulációs eszközréteg.

A Python nem része a játékosnál futó kötelező runtime-láncnak.

A játékszabályokat nem szabad C# és Python között két kanonikus félmotorra osztani.

---

## 2. Aktuális dokumentum- és forráselsőbbség

A technikai folytatásnál az alábbi sorrend érvényes:

1. hivatalos játékszabályforrások;
2. hosszú távú AETERNA 0.0.1 termékcél;
3. lezárt runtime-nyelvi és architektúradöntés;
4. jelen `ENGINE_CHECKPOINT.md`;
5. `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`;
6. `ARCHITECTURE.md`;
7. `TECHNOLOGY_DECISIONS.md`;
8. `DECISION_MAP.md`;
9. `CONTRACT_STATUS.md`;
10. `RUNTIME_PACKAGE_STATUS.md`;
11. elfogadott comparison fixture és canonical eredmény;
12. Python referenciaimplementáció;
13. történeti és legacy dokumentumok.

A GitHubon jelenleg még a régi fájlnevek és tartalmak találhatók. A fenti utódfájlok csak a végső audit és kézi repository-beillesztés után válnak tényleges repository-forrássá.

---

## 3. Python minimal engine referencia

A Python minimal engine továbbra is értékes és megtartandó.

Bizonyított vagy korábban elkészült fő elemei:

- authoritative MatchState;
- card instance registry;
- draw és end-turn transition;
- typed eventek;
- expected state version guard;
- state invariánsok;
- player-visible snapshot;
- Domain topológia és occupancy;
- public board projection;
- strukturális Entitás-placement option;
- Aktív/Kimerült card-instance állapot;
- izolált Wellspring és resource summary contract;
- determinisztikus AI-vs-AI trajectory;
- headless és batch tesztelési tapasztalat.

Státusz:

`REFERENCE_IMPLEMENTATION / COMPARISON_ORACLE / EXTERNAL_TOOLING_BASE`

A Python nem automatikus hivatalos szabályforrás.

Migrációs sorrend:

```text
hivatalos szabályforrás
→ aktív contract és fixture
→ Python referencia
→ production C# implementáció
```

---

## 4. Python–Godot sidecar jelölt

### 4.1 Státusz

`COMPLETE_AND_FROZEN`

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e` – `Fix Godot sidecar cancellation race warnings`

### 4.2 Bizonyított képességek

- Godotból indított külön Python sidecar;
- localhost TCP;
- framing és request/response contract;
- ugyanazon comparison fixture feldolgozása;
- canonical SHA-egyezés;
- normál shutdown;
- Emergency Shutdown;
- F8 és parent-process megszűnés kezelése;
- parent watchdog;
- cancellation socket-race javítása;
- warning-, error- és orphanmentes elfogadott futások.

### 4.3 Következmény

A sidecar-jelölt technikailag működik, de production runtime-ként nem folytatandó.

Nem készül hozzá jelenleg:

- Python packaging;
- új TCP-protokoll;
- új watchdog;
- production launcher;
- Python.NET beágyazás;
- új sidecar UI.

A proof történeti és regressziós bizonyítékként megmarad.

---

## 5. C# in-process runtime-jelölt

### 5.1 Környezet

Elfogadott fejlesztői környezet:

- Godot .NET: `4.7.1.stable.mono.official.a13da4feb`;
- target framework: `net8.0`;
- .NET SDK: `8.0.423`;
- Microsoft.NETCore.App: `8.0.29`;
- MSBuild: `17.11.48.46605`.

C# buildhez és C# scene futtatásához a .NET-enabled Godot szükséges.

### 5.2 Státusz

`COMPLETE_AND_ACCEPTED`

Lezáró commit:

`8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

### 5.3 Létrejött fő elemek

- `Aeterna.RuntimeCandidate` pure C# library;
- `Aeterna.RuntimeCandidate.Proof` console proof;
- Godot C# bridge;
- Godot C# headless proof;
- Godot C# visual proof;
- Godot `.csproj` és `.sln` integráció;
- `.NET 8` környezetbeállítás.

A proof szerepe:

`ACCEPTED_PROOF`

Nem nevezendő át közvetlenül production motorrá. A production `Aeterna.Engine` külön projektként indul, a candidate pedig regressziós referenciaként megmarad.

### 5.4 Automatikus bizonyítékok

- ugyanaz a `minimal_draw_end_turn_v1` fixture;
- P1 draw;
- stale P1 end-turn rejection;
- valid P1 end-turn;
- P2 draw;
- önálló C# state-, request-, response-, event- és snapshot-számítás;
- canonical SHA-egyezés;
- console proof PASS;
- 100-run determinism PASS;
- Godot C# headless proof PASS;
- Godot visual proof PASS;
- Debug build PASS;
- Release/ExportRelease build PASS;
- C# warning/error: 0/0;
- Godot warning/error: 0/0;
- crash vagy modal dialog: nem volt;
- final orphan audit PASS;
- Python process delta: 0;
- TCP listener delta: 0.

Kanonikus eredmény:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

Canonical result méret:

`210730` byte

Mutation proof:

- seed `1 → 2`;
- eltérő SHA;
- elvárt `CANONICAL_SHA_MISMATCH`.

### 5.5 Manuális elfogadás

A felhasználó a Godot .NET Editorban elvégezte a vizuális tesztet.

Eredmény:

- jelenet megnyílt;
- UI olvasható;
- első futás PASS;
- második futás PASS;
- a két SHA azonos;
- actual SHA helyes;
- direct in-process: YES;
- separate engine process: NO;
- Python: NOT USED;
- TCP: NOT USED;
- Run gomb újra használható;
- F8 után a játékablak bezárult;
- Godot warning: nem;
- Godot error: nem;
- crash: nem.

---

## 6. Elfogadott runtime- és nyelvi architektúra

### 6.1 Godot és GDScript

Feladata:

- scene-ek;
- UI;
- input;
- kártyák vizuális mozgatása;
- animációk;
- hangok;
- képernyőállapotok;
- vizuális debug;
- C# engine eredményeinek megjelenítése.

Nem lehet a kanonikus játékszabályok gazdája.

### 6.2 C#

Feladata:

- egyetlen kanonikus MatchState;
- legal actionök;
- action request-validáció;
- state transitionök;
- játékszabályok;
- költségek és erőforrások;
- targeting;
- effectek és triggerek;
- eventek;
- snapshotok;
- determinisztikus random;
- replay-alapok;
- AI-k által használt ugyanazon action API.

A C# az egyetlen production kanonikus szabálymotor.

### 6.3 Python

Feladata:

- XLSX, JSON és JSONL feldolgozás;
- runtime package build és validáció;
- kártyaaudit;
- exportálás;
- batch tesztvezérlés;
- balanszelemzés;
- statisztika és riport;
- AI-kutatás;
- scenario- és fixture-generálás;
- C# headless futások koordinálása és elemzése.

A Python nem módosíthat kanonikus állapotot a C# authority-kapujának megkerülésével.

---

## 7. Python–C# kommunikációs irány

Elfogadott fokozatos irány:

1. Godot → C#: közvetlen, ugyanazon processen belüli API;
2. Python → C#: kezdetben headless parancssori JSON/JSONL interfész;
3. csak mérési szükség esetén: hosszú életű localhost HTTP vagy gRPC szolgáltatás.

Első tervezett forma:

```text
Python scenario vagy fixture
        ↓
Aeterna.Engine.Headless
        ↓
production C# engine
        ↓
canonical JSON/JSONL eredmény
        ↓
Python elemzés, AI vagy statisztika
```

Most nem készül:

- ASP.NET server;
- gRPC infrastruktúra;
- hosszú életű C# daemon;
- Python production kliens;
- új sidecar-lifecycle rendszer.

---

## 8. Runtime language decision gate

**Státusz:** `COMPLETE_AND_ACCEPTED`

Döntés:

- Python főmotor + Godot sidecar: működőképes, de production runtime-ként túl összetett;
- C# főmotor + Godot: elfogadott production irány;
- Python külső toolingként: megtartandó és stratégiailag fontos;
- GDScript authoritative proof: már nem szükséges.

A döntési kapu csak új, erős, AETERNA-specifikus technikai bizonyíték alapján nyitható újra.

---

## 9. C.5A production C# architektúraterv

**Státusz:** `COMPLETE_AND_ACCEPTED`

Elfogadott production projektirány:

- `Aeterna.Engine` – pure C# authoritative engine library;
- `Aeterna.Engine.Headless` – vékony parancssori host;
- `Aeterna.Engine.Tests` – közös C# tesztprojekt;
- Godotban külön vékony production C# bridge.

Javasolt fő engine-modulok egy assemblyn belül:

- Contracts;
- Model;
- Runtime;
- Rules;
- RuntimePackage;
- Serialization;
- Diagnostics.

Tervezett publikus API:

- `CreateMatch`;
- `GetPlayerSnapshot`;
- `ListLegalActions`;
- `SubmitAction`;
- `GetEvents`;
- `GetMatchResult`.

Authority szabály:

- kizárólag a C# engine módosíthatja a kanonikus állapotot;
- a GDScript és a Python csak action requesten keresztül kérhet műveletet;
- a belső MatchState nem adható ki módosítható objektumként.

---

## 10. C.5B production engine foundation

**Státusz:** `READY_FOR_IMPLEMENTATION`

**Ideiglenes állapot:** `PAUSED_CODEX_QUOTA`

A végrehajtási specifikáció elkészült.

Tervezett scope:

- új `Aeterna.Engine`;
- új `Aeterna.Engine.Headless`;
- új `Aeterna.Engine.Tests`;
- typed production contractok;
- production `EngineSession`;
- runtime package minimum loader;
- draw és end-turn actionök;
- fixture adapter;
- ugyanazon canonical SHA reprodukálása;
- production Godot bridge;
- candidate- és GDScript-regressziók.

Nem része:

- új kártyakijátszás;
- Aura és Magnitúdó;
- Beáramlás;
- effect engine;
- trigger;
- harc;
- AI;
- HTTP/gRPC;
- teljes Python-port;
- packaging;
- végleges UI.

A szünet oka nem architekturális vagy technikai blocker, hanem a Codex használati keretének elfogyása.

Build és regressziós teszt nélkül production engine-kód nem commitolható.

---

## 11. Contract- és package-státusz

### 11.1 Python referencia

Aktív vagy bizonyított:

- card instance record v1;
- MatchState;
- PlayerState deck/hand/discard;
- Domain topology;
- Domain occupancy;
- snapshot v2;
- public Domain board;
- draw;
- end-turn;
- typed zone move és turn transition;
- stale state rejection;
- AI episode v1;
- isolated Wellspring és resource summary.

### 11.2 C# candidate

Bizonyított:

- minimal match state;
- draw;
- stale rejection;
- end-turn;
- legal action;
- player snapshot;
- typed event;
- canonical serializer és SHA;
- deterministic fixture execution.

### 11.3 Production C#

Még nem implementált.

C.5B-ben tervezett:

- `CreateMatchRequest`;
- `CreateMatchResponse`;
- `ActionRequest`;
- `ActionResponse`;
- `LegalAction`;
- `PlayerSnapshot`;
- `EngineEvent`;
- `EngineDiagnostic`;
- `MatchResult`;
- `EngineSession`;
- minimum runtime package loader.

### 11.4 Runtime package

Működik:

- Python build és validáció;
- Godot consumption copy;
- loader és registry;
- cards/decks/lookups/aliases/diagnostics;
- legutóbbi rögzített állapot: 814 kártya és 28 deck.

Nem végleges:

- production package identity;
- schema/ruleset version policy;
- source fingerprint;
- package hash;
- production C# loader;
- ability execution.

---

## 12. C# formázási megfigyelés

A `CsharpMinimalRuntimeProof.cs` összehasonlított változatai logikailag azonosak voltak.

Eltérés:

- 4 szóközös behúzás;
- tabulátoros behúzás.

Státusz:

`OBSERVE_ONLY / NON_BLOCKING`

Addig:

- nincs külön commit;
- nincs `.editorconfig` módosítás;
- nincs tömeges C# formázás;
- nincs kritikus hibaminősítés.

Ismétlődés esetén egységes C# formázási szabály szükséges.

A tényleges working tree állapotot a következő kódolási munka előtt újra ellenőrizni kell.

---

## 13. Dokumentációs munkaszakasz

A repository dokumentumai közvetlenül nem módosultak. Helyi utódfájlok készülnek, amelyeket a felhasználó a végső ellenőrzés után fog bemásolni és commitolni.

### 13.1 Elkészült vagy előkészített utódfájlok

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `ARCHITECTURE.md`;
- `TECHNOLOGY_DECISIONS.md`;
- `DECISION_MAP.md`;
- `PROTOTYPE_STATUS.md`;
- `RUNTIME_PACKAGE_STATUS.md`;
- `CONTRACT_STATUS.md`;
- `ENGINE_CHECKPOINT.md`.

### 13.2 Tervezett névváltások

- `CURRENT_PROTOTYPE_STATUS.md` → `PROTOTYPE_STATUS.md`;
- `CURRENT_RUNTIME_PACKAGE_STATUS.md` → `RUNTIME_PACKAGE_STATUS.md`;
- `CURRENT_CONTRACT_STATUS.md` → `CONTRACT_STATUS.md`;
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md` → `checkpoints/ENGINE_CHECKPOINT.md`.

### 13.3 Open Questions szabály

Az alábbi két fájl szándékos kérdés–válasz dokumentumpár:

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

Ezek nem egyesítendők automatikusan.

A `CURRENT_OPEN_QUESTIONS.md` tartalmát külön kell auditálni:

- kérdés kerüljön az `OPEN_QUESTIONS.md` fájlba;
- elfogadott válasz vagy döntés kerüljön az `OPEN_QUESTIONS_DECISIONS.md` fájlba;
- sem kérdés, sem döntés nem veszhet el;
- OQ-azonosítók és keresztreferenciák szükségesek;
- a `CURRENT_OPEN_QUESTIONS.md` csak a sikeres tartalmi átvezetés után távolítható el.

### 13.4 Két dokumentummappa

Első audit:

- `Aeterna game engine/docs/`

Második audit:

- `Aeterna dokumentációk/`

A két audit után közös keresztmappa-ellenőrzés szükséges.

Minden aktív dokumentumnak legyen:

- verzió;
- dátum;
- státusz;
- egyértelmű szerep;
- érvényes belső hivatkozás.

---

## 14. Végső átadás előtti ellenőrzés

Mielőtt a felhasználó bemásolja és commitolja a fájlokat, külön teljes audit szükséges.

Ellenőrizendő:

1. minden elkészült helyi fájl létezik;
2. minden célútvonal egyértelmű;
3. régi → új fájlnév térkép teljes;
4. minden aktív dokumentumnak van verziója;
5. minden aktív dokumentumnak van dátuma;
6. minden aktív dokumentumnak van státusza;
7. nem maradt indokolatlan `CURRENT_` előtag;
8. nincs két azonos szerepű aktív dokumentum;
9. szándékos kérdés–válasz dokumentumpárok nem sérültek;
10. minden belső Markdown-hivatkozás az új nevekre mutat;
11. nincs hivatkozás eltávolítandó fájlra;
12. nincs tartalomvesztés;
13. nincs runtime- vagy architektúra-ellentmondás;
14. nincs elavult nyitott nyelvi döntési kapu;
15. nincs téves állítás arról, hogy a production C# engine már létezik;
16. a Python reference és a C# production szerepe elkülönül;
17. a runtime package nem keveredik MatchState-tel;
18. a két dokumentummappa keresztellenőrzése megtörtént;
19. elkészült a törlendő vagy archiválandó régi fájlok listája;
20. elkészült a javasolt commit-scope és commitüzenet;
21. Git diff ellenőrzés történik a commit előtt;
22. sem generált TEMP-, log- vagy fölösleges fájl nem kerül stage-be.

GitHubon vagy a repositoryban történő törlés csak a felhasználó jóváhagyásával és a helyi új fájlok sikeres beillesztése után történhet.

---

## 15. Nem programozási aktív fókusz

A Codex-korlát idején:

1. engine-dokumentumok átnevezése, aktualizálása és verziózása;
2. Open Questions kérdés–válasz rendszer auditja;
3. checkpoint-index és README-k frissítése;
4. dokumentumhivatkozások átvezetése;
5. engine-dokumentációs teljes audit;
6. `Aeterna dokumentációk/` teljes audit;
7. keresztmappa-konszolidáció;
8. kártyaadat- és szabályaudit;
9. kártyadizájn- és vizuális workflow tervezése.

Nem készül ellenőrizetlen production C# kód.

---

## 16. Halasztott technikai feladatok

Nem blokkoló backlog:

- Godot window/content stretch és maximized-window policy;
- egységes runtime diagnosztikai log;
- C# visual proof külön manuális logfájlja;
- Python unittest global discovery module-name collision;
- Python-sidecar proof archiválási stratégia;
- meglévő GDScript-fájlok kategorizálása;
- C# headless publikus interfész véglegesítése;
- Windows packaging a production engine stabilizálása után;
- hosszú életű Python–C# API csak teljesítménymérés alapján;
- replay;
- production AI-vs-AI;
- hosszú soak tesztek.

---

## 17. Következő programozási lépés

Amikor ismét elérhető a szükséges programozási eszköz:

**C.5B – Production C# Engine Foundation**

Indulási feltételek:

- branch, HEAD és working tree ellenőrzése;
- dokumentációs commit már lezárva vagy elkülönítve;
- whitespace-only eltérés kezelése;
- .NET 8 és Godot .NET ellenőrzése;
- nincs futó AETERNA processz;
- teljes C.5B specifikáció használata;
- build, teszt és regresszió nélkül nincs commit.

A C.5B után következő első valódi production gameplay-szelet:

- Wellspring integráció;
- Beáramlás;
- Magnitúdó-preflight;
- Aura-payment;
- egy egyszerű auditált Entitás kijátszása;
- Domain-placement;
- typed eventek;
- player snapshot.

---

## 18. Biztonságos újrakezdési utasítás

Új beszélgetés vagy hosszabb megszakítás után:

1. ezt az `ENGINE_CHECKPOINT.md` fájlt kell elsőként elolvasni;
2. ellenőrizni kell, hogy a helyi dokumentumcsomag már bekerült-e a repositoryba;
3. ha még nem került be, a dokumentációs audit és végső ellenőrzés folytatandó;
4. nem szabad visszatérni a nyitott runtime-nyelvi döntési kapuhoz;
5. a C# kanonikus motor + Godot visual layer + Python external tooling döntést elfogadottnak kell tekinteni;
6. programozási eszköz nélkül a dokumentációs és auditfeladatokat kell folytatni;
7. programozási eszköz elérhetőségekor a C.5B a következő kódolási feladat;
8. a RuntimeCandidate proofot és a Python sidecar proofot regressziós bizonyítékként meg kell őrizni;
9. régi fájl nem törölhető az utódfájl és a hivatkozások ellenőrzése előtt.

---

## 19. Rövid folytatási összefoglaló

- Aktuális bizonyított repository-commit: `8e5ee64e42e1657e10f3413444bb870524ee07f9`.
- Python sidecar: elkészült és befagyasztva.
- C# in-process candidate: elkészült és elfogadva.
- Runtime language gate: lezárva.
- Végleges irány: Godot/GDScript visual layer + C# authoritative engine + Python external tooling.
- C.5A architektúraterv: elkészült.
- C.5B implementáció: előkészítve, Codex-korlát miatt szünetel.
- Production C# engine: még nem létezik.
- Jelenlegi munka: dokumentumok átnevezése, verziózása, frissítése és konszolidációja.
- GitHub repository: ebben a dokumentációs szakaszban nem módosult.
- Commit: a felhasználó a végső audit után végzi el.
- Következő dokumentációs feladat: checkpoint-index és kapcsolódó hivatkozások frissítése, majd az Open Questions audit.
