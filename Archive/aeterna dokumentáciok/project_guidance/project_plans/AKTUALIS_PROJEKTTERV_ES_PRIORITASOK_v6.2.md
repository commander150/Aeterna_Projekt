# AETERNA – Aktuális Projektterv és Prioritások

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 6.2  
**Dátum:** 2026-07-21  
**Státusz:** aktív projektirányító és prioritási dokumentum  
**Aktuális repository HEAD:** `32a0cbea24c82dda440f1a053b454ef03949d8ae` – `docs update 2`  
**Aktuális C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Ez a dokumentum az AETERNA projekt aktuális, élő munkatervét tartalmazza.

A 2026-07-20-i frissítés fő változásai:

> **A runtime-nyelvi döntési kapu lezárult. Az AETERNA tervezett authoritative játékmotorja C# lesz, a Godot/GDScript a vizuális és kliensréteg marad, a Python pedig külső adat-, audit-, teszt-, AI- és szimulációs eszközrétegként folytatódik.**

A Python-sidecar és a C# in-process proof egyaránt elkészült. A közös fixture kanonikus eredménye mindkét jelöltnél azonos volt:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

A C# proof ugyanazt az eredményt:

- közvetlenül a Godot-folyamatban;
- külön engine-processz nélkül;
- Python nélkül;
- TCP és IPC nélkül;
- watchdog és orphan-processz kezelés nélkül

állította elő.

A következő kódolási szakasz a production C# engine foundation, de a Codex használati keretének ideiglenes elfogyása miatt jelenleg szünetel. Addig a dokumentációs, audit- és tervezési feladatok folytatódnak.

---

## 1. Forrás- és dokumentumelsőbbség

A projekt döntéseinél az alábbi sorrendet kell követni.

1. **Hivatalos szabályforrások**
   - `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
   - `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`
2. **Hosszú távú termékcél**
   - `Aeterna game engine/docs/AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`
3. **Aktuális projektirány és prioritások**
   - jelen dokumentum
4. **Aktuális engine-checkpoint**
   - `Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`
5. **Runtime-nyelvi és architektúradöntés**
   - `Aeterna game engine/docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
   - `Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`
   - `Aeterna game engine/docs/ARCHITECTURE.md`
6. **Aktuális technikai státuszdokumentumok**
   - `DECISION_MAP.md`
   - `PROTOTYPE_STATUS.md`
   - `RUNTIME_PACKAGE_STATUS.md`
   - `CONTRACT_STATUS.md`
7. **Open Questions dokumentumpár**
   - `OPEN_QUESTIONS.md`
   - `OPEN_QUESTIONS_DECISIONS.md`
8. **Hosszú specifikációk és történeti referenciák**

Eltérés esetén a jelenlegi projektterv és az aktuális engine-checkpoint írja le a tényleges munkasorrendet, de egyik sem írhatja felül a hivatalos játékszabályokat.

---

## 2. Projektirány

Az AETERNA több elkülönített rétegből áll:

- fizikai TCG és hivatalos szabályrendszer;
- kártyaadatbázis és strukturált adatforrások;
- Python adatpipeline és runtime package tooling;
- működő Python minimal rules-engine referencia;
- Godot loader-, debug- és kliensalap;
- elfogadott Godot .NET/C# runtime proof;
- tervezett production C# authoritative engine;
- Python külső AI-, audit-, batch- és szimulációs tooling;
- dokumentációs, audit- és tervezési rendszer.

### 2.1 Végleges tervezett szerepfelosztás

#### Godot és GDScript

Feladata:

- megjelenítés;
- jelenetek;
- input;
- animációk;
- hangok;
- vizuális állapotfrissítés;
- menük és panelek;
- fejlesztői debugnézetek;
- a C# motor eredményeinek megjelenítése.

A GDScript nem lehet kanonikus játékszabályok gazdája.

#### C#

Feladata:

- authoritative MatchState;
- játékos- és kártyapéldány-állapot;
- szabályvalidáció;
- legális akciók;
- action request/response;
- state transitionök;
- eventek;
- snapshotok;
- hidden-information projection;
- determinisztikus működés;
- később teljes gameplay, harc, reakció és győzelmi feltételek.

Új kanonikus játékszabályt kizárólag a C# production engine-ben szabad implementálni.

#### Python

Feladata:

- XLSX/JSON/JSONL adatfeldolgozás;
- runtime package előállítás és validáció;
- kártyaaudit;
- teszt- és fixture-generálás;
- tömeges C# headless futások vezérlése;
- balanszstatisztika;
- AI-kutatás és AI-vs-AI koordináció;
- riportok és diagnosztikai elemzés.

A Python nem maradhat a C# mellett külön fejlődő második kanonikus szabálymotorként.

### 2.2 Python–C# kapcsolat

Elsőként egyszerű headless kapcsolat tervezett:

Python → C# headless process → JSON/JSONL eredmény → Python elemzés

A játék Godot–C# kapcsolata továbbra is közvetlen, in-process hívás.

Későbbi localhost HTTP vagy gRPC API csak akkor indokolt, ha a tömeges szimulációk mérései szerint a processzindítás valódi teljesítményproblémát okoz.

Nem tervezett:

- HTTP a Godot és a C# között;
- Python beágyazása a játék kötelező runtime-jába;
- C# és Python között megosztott kanonikus szabálymotor.

---

## 3. Bizonyított implementációs bázis

### 3.1 Python minimal rules-engine referencia

A Python engine bizonyítottan tartalmaz:

- authoritative MatchState-et;
- card instance registryt;
- state invariantokat;
- action request/response alapot;
- draw és end-turn transitiont;
- typed eventeket;
- player-visible snapshotot;
- Domain topológiát és occupancyt;
- structural Entity placementet;
- activity state-et;
- izolált Wellspring resource contractot;
- determinisztikus AI trajectoryt.

Ez a bázis:

- nem törlendő;
- nem automatikusan archiválandó;
- comparison reference és expected-output orákulum;
- AI-, batch- és differential testing alap;
- production C# migráció során referenciaként használható.

### 3.2 Python–Godot sidecar proof

**Státusz:** `COMPLETE AND FROZEN`

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e` – `Fix Godot sidecar cancellation race warnings`

Bizonyított:

- külön Python sidecar;
- localhost TCP;
- request/response framing;
- kontrollált shutdown;
- emergency shutdown;
- Godot F8 utáni parent watchdog;
- orphan-processz elleni védelem;
- manuális és automatizált warning/error nélküli futás.

A proof működőképes, de production főmotorként nem folytatandó.

Nem készül hozzá jelenleg:

- production packaging;
- további TCP-protokoll;
- új watchdog-funkció;
- új Python-sidecar UI.

### 3.3 C# minimal in-process runtime proof

**Státusz:** `COMPLETE AND ACCEPTED`

Lezáró commit:

`8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Bizonyított:

- Godot 4.7.1 .NET;
- .NET 8;
- pure C# runtime candidate;
- közvetlen in-process Godot-hívás;
- külön engine-processz nélkül;
- Python nélkül;
- TCP/listener nélkül;
- Debug és Release build;
- zero warning/error;
- két manuális visual PASS;
- 100-run determinisztika;
- mutation negative proof;
- GDScript regressziók;
- helyes canonical SHA.

Manuális teszt:

- UI megnyílt és olvasható volt;
- első és második futás PASS;
- SHA-k azonosak;
- Run gomb újra használható;
- F8-ra a játékablak bezárult;
- warning, error és crash nem jelent meg.

### 3.4 Runtime package és Godot kliensalap

Elkészült:

- Python package build;
- validáció;
- valós card/deck/lookup adat;
- Godot loader és registry;
- sample snapshot/legal action/event fixture;
- debug nézetek;
- smoke tesztek;
- C# .NET project integration.

Ez a réteg megtartandó.

---

## 4. Hosszú távú cél: AETERNA 0.0.1

A 0.0.1 az első zárt, használható, könnyen elindítható digitális tesztkiadás célverziója.

Fő elemei:

- egyszerű Windows-indítás;
- játékos- és tesztelői mód;
- teljes ember–AI mérkőzés;
- több AI-nehézség;
- kezdőpaklik és tutorialok;
- pakliszerkesztő és gyűjtemény;
- helyi tesztgazdaság és booster rendszer;
- profil és mentés;
- részletes logok;
- replay- és reprodukálhatósági alap;
- hibajelentési csomag;
- használható Godot UI.

A végleges tervezett runtime-felosztás:

Godot/GDScript visual client + C# authoritative engine + Python external tooling.

---

## 5. Roadmap

### M1 – Minimal determinisztikus engine-alapok

**Állapot:** Python referenciaalap elkészült.

### M2 – Player view és board contract

**Állapot:** első jelentős Python referenciaszakasz elkészült.

### TG1 – Runtime engine language decision gate

**Állapot:** `COMPLETE AND ACCEPTED`

Elkészült:

- közös comparison fixture;
- Python reference output;
- Python–Godot sidecar proof;
- C# Godot in-process proof;
- canonical differential comparison;
- automatizált és manuális tesztek;
- emberi döntés.

Döntés:

- C# authoritative runtime;
- Godot/GDScript visual layer;
- Python external tooling.

Nyitva maradó, de nem blokkoló kérdés:

- production Windows packaging csak a production C# engine későbbi szakaszában bizonyítható teljesen.

### C.5A – C# production engine architektúraterv

**Állapot:** `COMPLETE`

Rögzítve:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- typed public contractok;
- EngineSession;
- Godot production bridge;
- Python headless tooling kapcsolat;
- fixture-alapú migráció;
- egyetlen C# authoritative state.

### C.5B – Production C# engine foundation

**Állapot:** `READY_FOR_IMPLEMENTATION`

**Ideiglenes állapot:** `PAUSED – CODEX QUOTA`

Tervezett első scope:

- production pure C# engine projekt;
- production headless host;
- zero-dependency test runner;
- stabil core contractok;
- EngineSession;
- runtime package minimum loader;
- draw/end-turn production reprodukció;
- Godot production bridge;
- candidate regresszió megtartása.

Nem része:

- új gameplay;
- Wellspring integráció;
- play_card;
- harc;
- effect engine;
- HTTP vagy gRPC API.

### M3 – Első tényleges gameplay actionök

**Állapot:** C.5B után folytatandó.

Első gameplay-lánc tervezett sorrendje:

1. Wellspring production integráció;
2. player-visible Wellspring summary;
3. Beáramlás precondition;
4. Beáramlás transition és event;
5. Magnitúdó-preflight;
6. Aura-payment;
7. Entitás kijátszási precondition;
8. `play_card`;
9. Entitás Domainba helyezése;
10. entry-state és eventek.

További roadmap:

- M4 – fázisok, prioritás és reakciók;
- M5 – harc és győzelmi feltételek;
- M6 – első játszható vertical slice;
- M7 – teljes alapjátékos tesztprogram;
- M8 – meta- és termékrendszerek;
- M9 – 0.0.1 release candidate.

---

## 6. Aktuális prioritási sorrend

### P1 – Meglévő aktív dokumentumok frissítése és végső cleanup

Az aktív engine-dokumentumok első frissítési köre elkészült. A végső cleanupban az alábbi fájlokat kell összehangolni:

- `ENGINE_CHECKPOINT.md`;
- jelen projektterv;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `TECHNOLOGY_DECISIONS.md`;
- `ARCHITECTURE.md`;
- `DECISION_MAP.md`;
- `PROTOTYPE_STATUS.md`;
- `RUNTIME_PACKAGE_STATUS.md`;
- `CONTRACT_STATUS.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`;
- kapcsolódó README-k.

Új párhuzamos dokumentum csak akkor készülhet, ha nincs megfelelő meglévő célfájl.

### P2 – Dokumentációs audit és konszolidáció

A munkaszakasz aktív. A fő engine-dokumentumok auditja, az Open Questions konszolidációja és a duplikációs térkép elkészült.

A cél:

- aktív, történeti és elavult dokumentumok elkülönítése;
- azonos témájú párhuzamos fájlok felismerése;
- checkpointok összevonása;
- README-k és indexek egységesítése;
- felesleges verziómásolatok archiválása;
- stabil, lehetőleg verziószám nélküli aktív fájlnevek kialakítása;
- nyitott kérdések megőrzése;
- tartalomvesztés nélküli merge.

A kijelölt elődök csak az utódfájl, a belső hivatkozások és a Git diff ellenőrzése után törölhetők. A pontos lista a `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md` fájlban található.

### P3 – Open Questions közös triázs

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

A korábbi `CURRENT_OPEN_QUESTIONS.md` tartalma a két kanonikus 2.0-s fájlba beolvadt és már a repositoryban van; a régi fájl a végső hivatkozás-ellenőrzés után eltávolítandó.

Cél:

- OQ-azonosítók;
- megválaszolt kérdések lezárása;
- hivatalos főforrásból megválaszolható kérdések ellenőrzése;
- technikai, szabályi, design- és későbbi kérdések szétválasztása.

### P3.1 – Végső dokumentációs cleanup

A projekt-térkép v1.5 alapján eltávolítandó:

- a `CURRENT_*` státusz- és checkpointelődök;
- a dátumozott átmeneti checkpoint;
- az engine docs alá tévesen került v6.2 projektterv;
- a v5.1/v6.0/v6.1 projekttervek;
- a v1.2/v1.3/v1.4 projekt-térképek;
- a 2026-07-03-i külön dokumentációs cleanup-checkpoint;
- a két elavult gyökérszintű engine-összefoglaló;
- a teljesült object identity/zone move terv.

A törlés után kötelező:

- Markdown-hivatkozáskeresés;
- verzió/dátum/státusz audit;
- `git diff --check`;
- C# whitespace-only diff elkülönítése;
- commit-scope ellenőrzése.

### P4 – C.5B production C# foundation

A Codex használati keretének helyreállása után.

A korábban elkészített C.5B specifikáció alapján egyetlen célzott implementációs futás következik.

### P5 – Első gameplay production migráció

Csak a C.5B teljes tesztje és elfogadása után.

Első cél: Wellspring production integráció.

---

## 7. Párhuzamos, Codex nélküli munkasávok

### 7.1 Dokumentáció és projektirány

Aktív:

- meglévő dokumentumok frissítése;
- dokumentumlista és státusztérkép;
- konszolidációs terv;
- döntések és checkpointok megőrzése;
- architektúra és prioritások összehangolása.

### 7.2 Kártyaadatbázis és audit

Továbbra is külön munkasáv:

- főforrás-alapú kártyaaudit;
- structured és természetes szöveg összevetése;
- adat-, engine-, szabályértelmezési és balanszhiba elkülönítése;
- runtime package és lookupok fenntartása.

### 7.3 Kártyadizájn és vizuális workflow

Külön tervezési sáv:

- Photoshop-szintű ingyenes vagy kedvező árú eszköz;
- AI-segített képszerkesztés;
- kártyakeret és elemek réteges kezelése;
- generált elemek következetes újrafelhasználása;
- exportálási szabvány.

### 7.4 Runtime package és Godot

Fenntartandó:

- exporter és publish pipeline;
- package validáció;
- loader és registry;
- debug nézetek;
- smoke tesztek.

Nagy player UI-fejlesztés csak stabilabb production C# player-facing contractok után induljon.

### 7.5 Régi engine review

Csak külön döntéssel emelhető át:

- algoritmus;
- AI-minta;
- diagnostics;
- balanszmetrika;
- effectlogika.

---

## 8. Dokumentumkezelési szabály

A projektben túl sok részben átfedő dokumentum keletkezett.

Új szabály:

1. Elsődlegesen meglévő aktív dokumentumot kell frissíteni.
2. Új dokumentum csak akkor készülhet, ha:
   - nincs megfelelő meglévő célfájl;
   - külön contract vagy specifikáció valóban indokolt;
   - az információ nem illeszthető biztonságosan a meglévő struktúrába.
3. Új napi vagy feladatspecifikus checkpoint helyett az `ENGINE_CHECKPOINT.md` frissítendő.
4. Történeti állapot csak szükség esetén kerüljön archív checkpointba.
5. Azonos témájú fájlok később összevonandók.
6. Nyitott kérdés vagy döntés nem veszhet el összevonáskor.
7. Törlés vagy archiválás előtt teljes tartalmi audit szükséges.
8. A későbbi cél stabil, verziószám nélküli aktív dokumentumnevek használata, történeti verziókkal külön archívumban.

---

## 9. Amit most nem csinálunk

- ellenőrizetlen C# production implementáció;
- teljes Python → C# port egy lépésben;
- teljes GDScript engine;
- két kanonikus rules engine párhuzamos fejlesztése;
- új Python-sidecar production funkció;
- Python beágyazása a játék kötelező runtime-jába;
- HTTP vagy gRPC API mérési indok nélkül;
- teljes UI/UX;
- online mód;
- felhőmentés;
- minden kártyaképesség implementálása;
- nagy általános kódrefaktor;
- automatikus dokumentumtörlés;
- új dokumentum létrehozása meglévő megfelelő célfájl mellett;
- dokumentációs cleanup és runtime kód keverése egy commitban.

---

## 10. Tesztelési alapelvek

Minden C# production migráció során:

- hivatalos szabályforrás;
- közös fixture;
- Python reference output;
- C# production output;
- deterministic JSON;
- canonical SHA;
- hidden-information teszt;
- stale state rejection;
- request immutability;
- state invariant;
- Godot in-process proof;
- headless proof;
- Debug és Release build;
- warning/error audit;
- GDScript regresszió;
- Git státusz és scope ellenőrzés.

A Python referencia tesztkészlete megmarad.

A C# candidate proof regresszióként megmarad addig, amíg a production engine át nem veszi teljesen a bizonyított viselkedést.

---

## 11. Ismert, nem blokkoló technikai adósságok

- Python unittest monolitikus discovery modulnévütközés;
- Godot window/content stretch és maximized-window policy;
- egységes production runtime diagnostic log;
- Python-sidecar proof későbbi archiválási stratégia;
- GDScript-fájlok szerepkategorizálása;
- production C# Windows packaging;
- C# fájlformázás megfigyelése.

### C# whitespace-megfigyelés

A `CsharpMinimalRuntimeProof.cs` két vizsgált változata logikailag azonos volt.

Eltérés:

- 4 szóközös behúzás;
- tabulátoros behúzás.

Státusz:

`OBSERVE_ONLY – NON_BLOCKING`

Csak ismétlődés esetén kell `.editorconfig` vagy formázási szabály.

---

## 12. Rövid aktuális összefoglaló

**Hosszú távú cél:** AETERNA 0.0.1 zárt tesztkiadás.  
**Authoritative runtime döntés:** C#/.NET.  
**Vizuális és kliensréteg:** Godot/GDScript.  
**Külső tooling és AI/batch réteg:** Python.  
**Python-sidecar proof:** lezárt és befagyasztott.  
**C# in-process proof:** lezárt és elfogadott.  
**Aktuális repository HEAD:** `32a0cbea24c82dda440f1a053b454ef03949d8ae`.  
**Aktuális C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`.  
**Következő kódolási feladat:** C.5B production C# engine foundation.  
**Kódolási állapot:** Codex-keret miatt ideiglenesen szünetel.  
**Codex nélküli aktív sáv:** dokumentációs cleanup végrehajtása, projekt-térkép v1.5, régi elődök eltávolítása, hivatkozás- és verzióaudit, majd az `Aeterna dokumentációk/` mély almappaauditja.  
**Dokumentumkezelési irány:** egyetlen aktív utód témánként; a felváltott elődök a végső ellenőrzés után kikerülnek a working tree-ből, miközben a Git-történet megőrzi őket.
