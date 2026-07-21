# AETERNA – Aktuális Projektterv és Prioritások

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 6.3  
**Dátum:** 2026-07-21  
**Státusz:** commitra előkészített aktív projektirányító és prioritási dokumentum  
**Felváltott dokumentum:** `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`  
**Aktuális repository HEAD:** `ccfd3dc05a0cf16409aeb27c91333fe41d9633cc` – `docs update 3`  
**Aktuális C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Ez a dokumentum az AETERNA projekt aktuális, élő munkatervét tartalmazza.

A 2026-07-21-i 6.3-as frissítés fő változásai:

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

A következő kódolási szakasz továbbra is a production C# engine foundation, de a Codex használati keretének ideiglenes elfogyása miatt jelenleg szünetel. A dokumentációs cleanup közben jelentősen előrehaladt: az engine-dokumentáció első konszolidációja, az Open Questions beolvasztása, a `reference/`, `archive_review/` és `generated_review/` első tartalmi auditja, valamint az 1.9v kártyaadatbázis aktuális adataudit-utódja elkészült. A következő közvetlen cél a helyi utódfájlok repositoryba illesztésének előkészítése, az archiválási mozgatások végrehajtása és a teljes végső visszaellenőrzés.

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
   - `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.6.md`
   - `Aeterna dokumentációk/README.md` 2.1
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
8. **Aktuális adat- és auditforrások**
   - `AETERNA – KÁRTYAADATBÁZIS AKTUÁLIS ADATAUDIT 1.0.md` – a commit után aktív
   - aktív kártyaadat- és lookupstandardok
9. **Hosszú specifikációk és történeti referenciák**

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

### P1 – Dokumentációs utódcsomag véglegesítése

A következő commitra előkészítendő aktív utódok:

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.3.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.6.md`;
- `Aeterna dokumentációk/README.md` 2.1;
- `AETERNA – KÁRTYAADATBÁZIS AKTUÁLIS ADATAUDIT 1.0.md`;
- `reference/AETERNA – ÖTLETLÁDA ÉS NYITOTT TERVEK 1.1v.md`;
- `reference/Általános névprofil-sablon.md`;
- az engine-dokumentáció korábban elkészített replacement fájljai.

Kötelező:

- minden célútvonal ellenőrzése;
- verzió-, dátum- és státuszblokk;
- felváltott előd megnevezése;
- belső hivatkozások frissítése;
- azonos témájú második aktív utód kizárása.

### P2 – Archiválási mozgatások

Az aktív helyről kikerülő elődök nem véglegesen törlendők, hanem tartalmi ellenőrzés után az `Archive/` megfelelő csoportjába kerülnek.

Fő archiválási csoportok:

1. `Archive/project_guidance/`
   - v5.1, v6.0, v6.1 és v6.2 projekttervek;
   - v1.2–v1.5 projekt-térképek;
   - 2026-07-03-i cleanup-checkpoint.

2. `Archive/engine_docs_superseded/`
   - `CURRENT_*` státuszdokumentumok;
   - régi és dátumozott checkpointelődök;
   - teljesült object identity / zone move terv.

3. `Archive/design_ideas/`
   - a beolvasztott `Ötlet - Aeterna 4 .md`.

4. `Archive/old_python_engine_docs/`
   - régi runtime/effect/trigger reference fájlok;
   - régi backend/facade és project-guidance dokumentumok;
   - újratervezési történeti anyagok.

5. `Archive/card_database_audits_1.8v/`
   - három 1.8v adataudit;
   - régi LOOKUPS-bővítési terv.

6. `Archive/generated_exports/cards_xlsx_text_export_2026-05-25/`
   - a teljes `generated_review/Új mappa/` exportbatch.

Minden mozgatás előtt és után repository-keresés szükséges a régi fájlnévre.

### P3 – Dokumentációs végső visszaellenőrzés

A teljes rendezés csak külön visszaellenőrzési kör után zárható le.

Ellenőrizendő:

- teljes repository-fájllista;
- aktív és archív útvonalak;
- hiányzó vagy duplikált célfájlok;
- azonos tartalmú duplikátumok;
- régi fájlnevekre mutató hivatkozások;
- `CURRENT_*`, `Új mappa`, `OLD_`, `final`, `copy`, `másolat` előfordulások;
- minden aktív Markdown verziója, dátuma és státusza;
- Open Questions azonosítók;
- projektterv, projekt-térkép, README-k és checkpoint összhangja;
- archív dokumentum nem jelenik-e meg aktív authorityként;
- generált output nem szerepel-e canonical forrásként;
- `git status --short`;
- `git diff --check`;
- stage- és commit-scope;
- commit utáni ismételt repository-keresés.

### P4 – Külön `LOOKUPS.xlsx` teljes audit

A kártyaadatbázis aktuális adatauditja elkészült, de a külön canonical lookupforrás teljes táblázatszintű összevetése még nyitott.

Vizsgálandó:

- laplista és schema;
- `Value`, `Canonical_Value`, `Label_HU`;
- active, inactive, legacy és workflow státusz;
- duplikáció;
- aliasok;
- delimiter-policy;
- trigger-, target-, effect-, duration- és status-coverage;
- a munkaforrás 5A–5D lapjaihoz képesti eltérés;
- a runtime package builder által ténylegesen fogyasztott forrás.

### P5 – Aktív adat- és auditstandardok frissítése

A következő dokumentumok tartalmi összevetése szükséges az 1.9v munkaforrással és a külön LOOKUPS-rendszerrel:

- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`;
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`;
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`;
- `kartya_tabla_szabvany v1.2.md`.

Kiemelt döntési kapuk:

- `Card_ID` vagy `Szabályi_Kártya_ID`;
- `AET-` prefix;
- structured többértékű delimiter;
- `blank` és `none`;
- canonical `wellspring`, `infusion`, `void`, `sigil`;
- embedded lookup-lapok és külön `LOOKUPS.xlsx` viszonya.

### P6 – C.5B production C# foundation

A Codex használati keretének helyreállása után.

A korábban elkészített C.5B specifikáció alapján egyetlen célzott implementációs futás következik.

### P7 – Első gameplay production migráció

Csak a C.5B teljes tesztje és elfogadása után.

Első cél:

- Wellspring production integráció.

## 7. Párhuzamos, Codex nélküli munkasávok

### 7.1 Dokumentáció és projektirány

Aktív:

- helyi replacement csomag rendezése a pontos repository-útvonalakra;
- archiválási mozgatások előkészítése;
- README-k, projektterv, projekt-térkép és checkpoint összehangolása;
- `reference/`, `archive_review/` és `generated_review/` auditdöntéseinek átvezetése;
- végső keresztmappa-, hivatkozás-, verzió- és duplikációellenőrzés;
- commit előtti és commit utáni kontroll.

### 7.2 Kártyaadatbázis és audit

Továbbra is külön munkasáv:

- az 1.9v aktuális adataudit nyitott tételeinek rendezése;
- külön `LOOKUPS.xlsx` teljes auditja;
- `NAME_PROFILE`, decklistanév és master–export eltérések rendezése;
- ID-, delimiter- és canonical terminológiadöntések;
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

## 8. Dokumentumkezelési és archiválási szabály

A projektben túl sok részben átfedő dokumentum keletkezett.

Kötelező szabály:

1. Elsődlegesen meglévő aktív dokumentumot kell frissíteni.
2. Új dokumentum csak akkor készülhet, ha:
   - nincs megfelelő meglévő célfájl;
   - külön contract, audit vagy specifikáció valóban indokolt;
   - az információ nem illeszthető biztonságosan a meglévő struktúrába.
3. Új napi vagy feladatspecifikus checkpoint helyett az `ENGINE_CHECKPOINT.md` frissítendő.
4. Az aktív fájloknak verziót, dátumot és státuszt kell tartalmazniuk.
5. `CURRENT_`, `new`, `final`, `copy`, `másolat` és `Új mappa` nem maradhat indokolatlan aktív fájlnévben vagy útvonalban.
6. Azonos témájú fájloknál tartalmi összevetés és egyetlen aktív utód kijelölése szükséges.
7. Nyitott kérdés, döntés vagy fontos történeti adat nem veszhet el.
8. Aktív helyről kikerülő előd csak:
   - tartalmi audit;
   - aktív utód vagy beolvasztási cél;
   - hivatkozásfrissítés;
   - és kijelölt archív célútvonal
   után mozgatható.
9. Az elődök az `Archive/` megfelelő csoportjába kerülnek; nem véglegesen törlendők.
10. Az archív fájl nem jelenhet meg aktív authorityként.
11. Generált output nem canonical szerkesztési forrás.
12. Dokumentációs cleanup és runtime kód nem keverhető ugyanabba a commitba.
13. A teljes munkaszakasz végén külön visszaellenőrzés kötelező.

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
- dokumentum végleges törlése audit és archív cél nélkül;
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
**Aktuális repository HEAD:** `ccfd3dc05a0cf16409aeb27c91333fe41d9633cc`.  
**Aktuális C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`.  
**Dokumentációs állapot:** az engine docs első konszolidációja és a három mély almappa első auditja elkészült.  
**Commitra előkészített fő utódok:** projektterv v6.3, projekt-térkép v1.6, dokumentációs README 2.1 és kártyaadat-audit 1.0.  
**Archiválási irány:** az elődök tartalmi ellenőrzés után az `Archive/` kijelölt csoportjaiba kerülnek.  
**Következő dokumentációs lépés:** replacement csomag összehangolása, archiválási mozgatások és teljes végső visszaellenőrzés.  
**Következő adatfeladat:** a külön `LOOKUPS.xlsx` teljes auditja.  
**Következő kódolási feladat:** C.5B production C# engine foundation.  
**Kódolási állapot:** Codex-keret miatt ideiglenesen szünetel.
