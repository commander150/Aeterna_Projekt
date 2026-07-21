# AETERNA Game Engine – Aktuális Engine Checkpoint

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-20  
**Státusz:** friss technikai folytatási checkpoint, repository-beillesztésre előkészítve  
**Javasolt célfájl:** `Aeterna game engine/docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`  
**Jelen dokumentum még nincs automatikusan commitolva a repositoryba.**

**Aktuális bizonyított repository-commit:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`  
**Commitüzenet:** `Add minimal C# runtime candidate proof`

**Korábbi checkpoint bázisa:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b` – `Add minimal Wellspring resource contracts`

Ez a dokumentum felváltja a 2026-07-15-i, kizárólag a Python minimal engine állapotára épülő technikai checkpoint tartalmát.

Feladata:

- biztonságos folytatási pont biztosítása új beszélgetés vagy hosszabb munkaszünet után;
- a Python- és C# runtime-jelöltek bizonyított állapotának rögzítése;
- a 2026-07-20-i runtime-nyelvi és architektúradöntés megőrzése;
- az elkészült, előkészített és halasztott feladatok világos elhatárolása;
- a Codex használati keretének ideiglenes hiánya melletti munkasorrend rögzítése.

Ez nem hivatalos játékszabály és nem teljes production engine-specifikáció.

---

## 1. Rövid állapot

A runtime-nyelvi döntési kapu lezárult.

Két, azonos összehasonlító fixture-t feldolgozó technikai jelölt készült el:

1. Python sidecar + Godot integráció;
2. Godot .NET/C# közvetlen, processzen belüli runtime-jelölt.

Mindkét jelölt ugyanazt a kanonikus eredményt állította elő:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

A bizonyítékok alapján az AETERNA elfogadott hosszú távú technikai iránya:

- Godot és GDScript: vizuális réteg, jelenetek, input, animációk és UI;
- C#: az egyetlen kanonikus játékmotor és szabályi authority;
- Python: külső adatfeldolgozó, auditáló, tesztelő, elemző, AI- és szimulációs eszközréteg.

A Python nem része a játékosnál futó kötelező runtime-láncnak.

A játékszabályokat nem szabad C# és Python között két kanonikus félmotorra osztani.

---

## 2. Aktuális dokumentum- és forráselsőbbség

A technikai folytatásnál az alábbi sorrend érvényes:

1. hivatalos játékszabályforrások;
2. hosszú távú AETERNA 0.0.1 termékcél;
3. a 2026-07-20-i runtime-nyelvi és architektúradöntés;
4. jelen checkpoint;
5. az aktuális projektterv és technológiai döntési dokumentumok;
6. elfogadott comparison fixture és canonical eredmény;
7. Python referenciaimplementáció;
8. történeti és legacy dokumentumok.

A repositoryban jelenleg lévő `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.1.md` még nyitott runtime-nyelvi kaput ír le. A kapu azóta lezárult, ezért a dokumentum runtime-döntési és prioritási részei frissítendők egy új verzióban.

A repositoryban jelenleg lévő `CURRENT_ENGINE_CHECKPOINT.md` 1.0 verziója a Python Wellspring előtti állapotot rögzíti. Technikai folytatáshoz ezt az 1.1 checkpointot kell alapul venni.

---

## 3. Python minimal engine referencia

A korábbi Python minimal engine továbbra is értékes és megtartandó.

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

A Python referencia státusza:

**REFERENCE IMPLEMENTATION / COMPARISON ORACLE / EXTERNAL TOOLING BASE**

A Python nem automatikus hivatalos szabályforrás. Portoláskor a sorrend:

hivatalos szabályforrás → elfogadott contract és fixture → Python referencia → C# implementáció.

---

## 4. Python–Godot sidecar jelölt

### 4.1 Státusz

**Python–Godot integration candidate: COMPLETE AND FROZEN**

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e` – `Fix Godot sidecar cancellation race warnings`

### 4.2 Bizonyított képességek

- Godotból indított külön Python sidecar;
- localhost TCP kommunikáció;
- framing és request/response contract;
- ugyanazon comparison fixture feldolgozása;
- canonical SHA-egyezés;
- normál shutdown;
- Emergency Shutdown;
- F8 és parent-process megszűnés kezelése;
- parent watchdog;
- cancellation socket-race javítása;
- warning-, error- és orphanmentes elfogadott futások.

### 4.3 Manuális elfogadás

A felhasználó megerősítette:

- nem állított le manuálisan Python-folyamatot;
- az F8 után a korábbi sidecar már nem volt látható;
- nem jelent meg Godot warning vagy error;
- a normál PASS, F8 CANCELLED és Emergency Shutdown viselkedés megfelelő volt.

### 4.4 Következmény

A Python sidecar bizonyította, hogy a Python főmotor technikailag összekapcsolható a Godottal, de a működéshez szükséges volt:

- külön processz;
- TCP;
- saját protokoll;
- timeout és cancellation;
- shutdown-kezelés;
- parent watchdog;
- orphan-processz elleni védelem;
- külön futtatókörnyezet és későbbi csomagolás.

Ezért a sidecar-jelöltet nem fejlesztjük tovább production runtime irányba.

Nem következik:

- Python packaging;
- új Python–Godot TCP-funkció;
- Python.NET beágyazás;
- production sidecar továbbépítése.

---

## 5. C# in-process runtime-jelölt

### 5.1 Környezet

Elfogadott fejlesztői környezet:

- Godot .NET: `4.7.1.stable.mono.official.a13da4feb`;
- Godot .NET executable: `G:\Godot\Godot_v4.7.1-stable_mono_win64\Godot_v4.7.1-stable_mono_win64.exe`;
- target framework: `net8.0`;
- .NET SDK: `8.0.423`;
- Microsoft.NETCore.App: `8.0.29`;
- MSBuild: `17.11.48.46605`.

A standard Godot továbbra is létezhet, de C# buildhez és C# scene futtatásához a .NET-enabled Godot szükséges.

### 5.2 Státusz

**C# minimal runtime candidate: COMPLETE AND ACCEPTED**

Lezáró commit:

`8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

### 5.3 Létrejött fő elemek

- `Aeterna.RuntimeCandidate` pure C# library;
- `Aeterna.RuntimeCandidate.Proof` console proof;
- Godot C# bridge;
- Godot C# headless proof;
- Godot C# visual proof scene;
- Godot `.csproj` és `.sln` integráció;
- `global.json` .NET 8 környezethez.

A proof jelenlegi szerepe:

**ACCEPTED_PROOF**

Nem szabad automatikusan átnevezni vagy közvetlenül production motorrá bővíteni. A későbbi production `Aeterna.Engine` külön projektként induljon, miközben a proof regressziós referenciaként megmarad.

### 5.4 Automatikus bizonyítékok

- ugyanaz a `minimal_draw_end_turn_v1` fixture;
- P1 draw;
- stale P1 end-turn rejection;
- valid P1 end-turn;
- P2 draw;
- önálló C# state-, request-, response-, event- és snapshot-számítás;
- canonical SHA-egyezés;
- két külön console proof PASS;
- 100-run determinism PASS;
- Godot C# headless proof PASS;
- két Godot visual proof PASS;
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
- eltérő SHA keletkezett;
- várt hiba: `CANONICAL_SHA_MISMATCH`;
- ez bizonyítja, hogy a C# jelölt nem előre eltárolt eredményt ad vissza.

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

A felhasználó jelezte, hogy a Codex automatikus tesztje közben rövid időre felbukkant a Godot game ablak. Ez nem hiba, hanem kiegészítő bizonyíték arra, hogy valódi renderelt Godot session futott. Nem helyettesíti a manuális tesztet, amely később szintén sikeresen megtörtént.

### 5.6 Visual proof log

A C# visual proof jelenleg nem készít külön manuális logfájlt.

Státusz:

**NON_BLOCKING / LATER GENERAL RUNTIME DIAGNOSTICS**

Nem kell csak emiatt továbbfejleszteni a proofot.

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

Új kanonikus játékszabályt nem szabad GDScriptben implementálni.

### 6.2 C#

Feladata:

- egyetlen kanonikus MatchState;
- legal actionök;
- action request validáció;
- state transitionök;
- játékszabályok;
- költségek és erőforrások;
- targeting;
- effectek és triggerek;
- eventek;
- snapshotok;
- determinisztikus random;
- replay-alapok;
- későbbi hálózati authority;
- AI-k által használt ugyanazon action API.

A C# az egyetlen kanonikus szabálymotor.

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

A Python nem módosíthat kanonikus állapotot a C# `SubmitAction` jellegű kapujának megkerülésével.

---

## 7. Python–C# kommunikációs irány

Elfogadott fokozatos irány:

1. Godot → C#: közvetlen, ugyanazon processen belüli API;
2. Python → C#: kezdetben headless parancssori JSON API;
3. csak mérési szükség esetén: hosszú életű localhost HTTP vagy gRPC szolgáltatás.

Első tervezett Python–C# forma:

- Python scenario vagy fixture JSON-t készít;
- elindítja az `Aeterna.Engine.Headless` hostot;
- C# futtatja a kanonikus szabálymotort;
- JSON/JSONL eredményt ad vissza;
- Python elemzi az eredményt.

Most nem készítünk:

- ASP.NET szervert;
- gRPC infrastruktúrát;
- hosszú életű C# daemont;
- Python-klienst;
- új sidecar-lifecycle rendszert.

---

## 8. C.4B runtime language decision gate

**Státusz: COMPLETE AND ACCEPTED**

Döntés:

- Python főmotor + Godot sidecar: működőképes, de production runtime-ként túl összetett;
- C# főmotor + Godot: elfogadott production irány;
- Python külső toolingként: megtartandó és stratégiailag fontos;
- opcionális GDScript rules proof: már nem szükséges a döntéshez.

A döntési kapu csak új, erős technikai bizonyíték alapján nyitható újra.

---

## 9. C.5A production C# architektúraterv

**Státusz: COMPLETE / ACCEPTED PLAN**

Elfogadott production projektirány:

- `Aeterna.Engine` – pure C# kanonikus engine library;
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
- a belső `MatchState` nem adható ki módosítható objektumként.

---

## 10. C.5B production engine foundation

**Státusz: READY_FOR_IMPLEMENTATION / TEMPORARILY PAUSED**

A teljes végrehajtási specifikáció elkészült.

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

A C.5B implementációja azért szünetel, mert a Codex használati keret elfogyott.

Ez nem architekturális vagy technikai blocker.

Nem szabad ellenőrizetlenül, build- és regressziós tesztek nélkül commitolni a production engine alapját.

---

## 11. C# formázási megfigyelés

A manuális Godot-futtatás után a Git/GitHub Desktop módosultként jelezte:

`CsharpMinimalRuntimeProof.cs`

Az OLD és NEW fájl összehasonlítása szerint:

- programkód: azonos;
- sorok száma: azonos;
- logikai eltérés: nincs;
- sorvég: LF mindkettőben;
- BOM: egyikben sincs;
- eltérés: 4 szóközös behúzás → tabulátor;
- a NEW fájl 209 tabulátort tartalmazott;
- a normalizált tartalom 100%-ban azonos.

Státusz:

**OBSERVE_ONLY / NON_BLOCKING**

A felhasználó teszteli, hogy egyszeri vagy ismétlődő jelenség.

Addig:

- nem készítünk külön commitot;
- nem módosítunk `.editorconfig` fájlt;
- nem végzünk tömeges C# formázást;
- nem tekintjük kritikus hibának.

Amennyiben ismétlődik, egységes C# formázási szabályt kell rögzíteni.

A jelenlegi pontos working tree státuszt új munka előtt ismét ellenőrizni kell, mert a Codex commit után clean állapotot jelentett, de a későbbi manuális futás whitespace-only helyi eltérést okozhatott.

---

## 12. Aktuális nem programozási fókusz

A Codex-korlát idején csak olyan feladatok folytatandók, amelyek nem igényelnek production kód implementációt.

Prioritási sorrend:

1. jelen checkpoint véglegesítése és későbbi repository-beillesztése;
2. `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK` frissítése új verzióra;
3. `PROJEKT_TERKEP_ES_FAJLSTATUSZ` frissítése;
4. `ARCHITECTURE.md` és `TECHNOLOGY_DECISIONS.md` runtime-döntésének aktualizálása;
5. nyitott kérdések és halasztott technikai adósságok rendezése;
6. dokumentációs migráció és összevonás;
7. kártyaadat- és szabályaudit;
8. kártyadizájn- és vizuális workflow tervezése.

Egyszerre csak egy dokumentumot kell aktualizálni, a célfájl szerkezetéhez igazodva.

---

## 13. Halasztott technikai feladatok

Nem blokkoló backlog:

- Godot window/content stretch és maximized-window policy;
- egységes runtime diagnosztikai log;
- C# visual proof külön manuális logfájlja;
- Python unittest global discovery module-name collision;
- Python-sidecar proof archiválási stratégia;
- meglévő GDScript-fájlok kategorizálása;
- C# headless publikus interfész véglegesítése;
- Windows packaging csak a production engine stabilizálása után;
- hosszú életű Python–C# API csak teljesítménymérés alapján.

---

## 14. Következő programozási lépés, amikor ismét elérhető a szükséges eszköz

**C.5B – Production C# Engine Foundation**

Indulási feltételek:

- branch és HEAD ellenőrzése;
- working tree tisztázása;
- whitespace-only eltérés kezelése vagy visszaállítása;
- .NET 8 és Godot .NET környezet ellenőrzése;
- nincs futó AETERNA processz;
- teljes C.5B specifikáció használata;
- build, teszt és regresszió nélkül nincs commit.

A C.5B után következő gameplay-szelet csak sikeres foundation után indulhat.

Tervezett első valódi production gameplay-szelet:

- Wellspring integráció;
- Beáramlás;
- Magnitúdó-preflight;
- Aura-payment;
- egy egyszerű auditált Entitás kijátszása;
- Domain-placement;
- typed eventek és player snapshot.

---

## 15. Biztonságos újrakezdési utasítás

Új beszélgetés vagy hosszabb megszakítás után:

1. ezt a checkpointot kell elsőként elolvasni;
2. ellenőrizni kell a Git branch, HEAD és working tree állapotát;
3. nem szabad visszatérni a nyitott runtime-nyelvi döntési kapuhoz;
4. a C# kanonikus motor + Godot visual layer + Python external tooling döntést elfogadottnak kell tekinteni;
5. programozási eszköz nélkül a dokumentációs és auditfeladatokat kell folytatni;
6. programozási eszköz elérhetőségekor a C.5B foundation a következő kódolási feladat;
7. a RuntimeCandidate proofot és a Python sidecar proofot regressziós bizonyítékként meg kell őrizni.

---

## 16. Rövid folytatási összefoglaló

- Aktuális bizonyított commit: `8e5ee64e42e1657e10f3413444bb870524ee07f9`.
- Python sidecar: elkészült és befagyasztva.
- C# in-process candidate: elkészült és elfogadva.
- Runtime language gate: lezárva.
- Végleges irány: Godot/GDScript visual layer + C# canonical engine + Python external tooling.
- C.5A architektúraterv: elkészült.
- C.5B implementáció: előkészítve, Codex-korlát miatt szünetel.
- Jelenlegi munka: dokumentáció és projektirányítás frissítése.
- Következő dokumentum: az aktuális projektterv új verziója.
