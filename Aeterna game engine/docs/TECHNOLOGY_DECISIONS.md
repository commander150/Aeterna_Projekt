# AETERNA Game Engine – Technology Decisions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív technológiai döntési dokumentum  
**Aktuális technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum az AETERNA Game Engine jelenleg elfogadott technológiai döntéseit, réteghatárait és még nyitott megvalósítási kérdéseit rögzíti.

Nem hivatalos játékszabály, nem részletes contract-specifikáció és nem checkpoint-napló.

Kapcsolódó elsődleges dokumentumok:

- `ARCHITECTURE.md`
- `CURRENT_CONTRACT_STATUS.md`
- `CURRENT_OPEN_QUESTIONS.md`
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `CONTRACT_SPECIFICATION.md`
- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

Eltérés esetén a hivatalos 1.4v szabályforrások, a v6.0 projektterv és a `CURRENT_ENGINE_CHECKPOINT.md` a frissebb státuszforrás.

---

## 1. A technológiai döntés jelenlegi állapota

A korábbi kérdés így szólt:

> Python, GDScript vagy hibrid modell legyen-e az AETERNA fő szabálymotorja?

A jelenlegi projektállapot alapján ez a fő döntés megszületett:

> **Az authoritative AETERNA rules engine jelenlegi és tervezett fő megvalósítási helye a Python engine.**

A Godot/GDScript jelenlegi szerepe:

- runtime package fogyasztás;
- registry- és adapterréteg;
- debug nézetek;
- játékos input;
- vizuális UI;
- animáció;
- későbbi lokális kliens;
- action requestek elküldése;
- player-visible válaszok megjelenítése.

A Godot nem külön authoritative szabálymotor.

A régi Python motor nem az új engine alapja, hanem:

- `OLD_ENGINE_REVIEW`;
- `OLD_ENGINE_REFERENCE`;
- külön döntéssel felhasználható algoritmus-, AI-, diagnostics- vagy balanszforrás.

---

## 2. Elfogadott magas szintű modell

A jelenlegi technológiai modell:

```text
Google Sheets / XLSX
        ↓
Python export, validáció és runtime package build
        ↓
runtime package
        ↓
Python authoritative rules engine
        ↓
player-visible snapshot / legal actions / action response / events
        ↓
Godot kliens, debug UI és későbbi játékos UI
```

A rétegek nem egyenrangú szabálymotorok.

### Python felelőssége

- statikus adatok betöltése és ellenőrzése;
- MatchState létrehozása;
- authoritative állapot tárolása;
- state invariantok;
- legal actionök számítása;
- action request validálása;
- state mutation;
- typed eventek;
- player-visible és debug projection;
- determinisztikus headless futtatás;
- AI-vs-AI és batch tesztelés;
- replay- és reprodukálhatósági alap;
- export-, diagnostics- és build tooling.

### Godot felelőssége

- runtime package betöltése;
- player-visible contractok fogyasztása;
- input és UI;
- animation és presentation;
- debug viewer;
- későbbi menük, deckbuilder, collection és játékosfelület;
- action request összeállítása a kapott legal action alapján;
- engine-válaszok megjelenítése.

### Runtime package felelőssége

- kártyadefiníciók;
- deckek;
- lookupok;
- alias- és normalizációs adatok;
- ability registry;
- engine-support és diagnostics adatok;
- statikus, programbiztos adatátadás.

A runtime package nem tartalmazza az authoritative meccsállapotot, és nem hajt végre szabályt.

---

## 3. Miért a Python rules engine lett az authoritative réteg?

A döntést nem önmagában a nyelv, hanem az elkészült bizonyítékok indokolják.

A Python engine jelenleg már működően bizonyítja:

- MatchState és PlayerState kezelést;
- card instance registryt;
- state version guardot;
- state invariantokat;
- legal action és action request alapot;
- draw és end-turn transitiont;
- typed eventeket;
- player-visible snapshotot;
- hidden-information elhatárolást;
- Domain topológiát és occupancyt;
- board projectiont;
- strukturális Entitás-placementet;
- activity state-et;
- izolált Wellspring resource contractot;
- determinisztikus AI trajectoryt;
- nagy számú automatizált unit és contract tesztet.

A Python technikai előnyei ebben a projektben:

- gyors, kis lépésekben tesztelhető fejlesztés;
- egyszerű headless futtatás;
- jól elkülöníthető tiszta contract- és state-logika;
- erős JSON/JSONL/XLSX feldolgozás;
- determinisztikus batch és AI-vs-AI tesztelés;
- egyszerű diagnostics és riportkészítés;
- a Godot UI-tól független szabálytesztelés.

A döntés azt jelenti, hogy a Python az authoritative szabálymotor. Nem jelenti azt, hogy minden termékfunkció Pythonban készül.

---

## 4. Godot/GDScript elfogadott szerepe

A Godot ág korábbi prototípusfeladata sikeres volt.

Bizonyított:

- runtime package loader;
- card/deck/lookup registry;
- sample snapshot betöltés;
- sample legal action betöltés;
- sample event log betöltés;
- snapshot viewer;
- legal action debug panel;
- event log debug view;
- unified debug dashboard;
- headless smoke futtatás;
- explicit logfájlos Windows/Godot futtatási minta.

Ez a réteg ezért nem eldobott prototípus.

A jelenlegi státusza:

- `ACTIVE_CONSUMER_LAYER`;
- `ACTIVE_DEBUG_LAYER`;
- `FUTURE_PLAYER_CLIENT`.

A Godotban nem készülhet párhuzamosan:

- saját legalitásszámítás;
- saját authoritative MatchState;
- külön card effect végrehajtás;
- Python engine-től eltérő phase vagy combat szabály;
- UI-node-okba rejtett rules logic.

A Godot kliens a szabálymotor által előállított contractokat fogyasztja.

---

## 5. A korábban vizsgált technológiai modellek státusza

### Modell A – Régi Python motor mint backend

**Státusz:** `not_selected_as_primary`

A régi motor nem válik automatikusan az új backenddé.

Használható:

- referencia;
- összevetés;
- AI-minta;
- diagnostics-minta;
- balanszriport-ötlet;
- célzott algoritmusforrás.

Bármilyen átvételhez külön audit és új teszt szükséges.

### Modell B – Új tiszta Python backend + Godot frontend

**Státusz:** `selected_current_architecture`

Ez a jelenlegi aktív modell.

A pontos Python–Godot runtime kapcsolat még külön implementációs döntés, de az authoritative felelősség már eldőlt.

### Modell C – Teljes GDScript rules engine

**Státusz:** `not_selected`

Nem építünk második authoritative szabálymotort GDScriptben.

Egyes tiszta kliensoldali előnézeti vagy megjelenítési helper készülhet, de nem hozhat szabályi döntést.

### Modell D – Python tesztmotor + külön GDScript játékengine

**Státusz:** `rejected_due_to_duplicate_rules_risk`

Két külön szabálymotor hosszú távon eltérést, duplikált karbantartást és bizonytalan referenciaeredményt okozna.

### Modell E – Python csak package builder, GDScript fő runtime

**Státusz:** `superseded_by_python_authoritative_engine`

A runtime package és Godot alapozás sikeres volt, de a szabálymotor fejlesztése időközben Pythonban érdemi, tesztelt állapotra jutott.

---

## 6. Python–Godot integráció

A felelősségi döntés megszületett, de a konkrét futási integráció még nyitott.

Lehetséges későbbi megoldások:

1. Python child process és stdin/stdout JSON protokoll.
2. Lokális socket vagy HTTP service.
3. Csomagolt Python runtime a Godot alkalmazás mellett.
4. Előre futtatott headless engine csak fejlesztői/tesztelői módban.
5. Későbbi natív bridge vagy más beágyazási megoldás.

A következő elvek kötelezők:

- az integrációs transport nem válhat szabályforrássá;
- minden kérés explicit action request;
- stale state/version ellenőrzés megmarad;
- a válasz player-visible contract;
- debug adat csak explicit debug módban érhető el;
- a kommunikáció determinisztikusan naplózható;
- hibás vagy megszakadt kapcsolat nem hozhat részleges state mutationt.

A konkrét transport döntése nem szükséges a minimal rules engine következő belső feladataihoz.

---

## 7. Adatpipeline és runtime package

Elfogadott döntések:

- a fő szerkesztés Google Sheetsben történik;
- a lokális XLSX forrásmásolat;
- a Godot nem olvas közvetlenül XLSX-et;
- a Python végzi az exportot, validációt és runtime package buildet;
- a kártyák és decklisták az aktív 1.9v kártyaadatbázisból jönnek;
- a runtime lookupok a `LOOKUPS.xlsx` fájlból jönnek;
- a Godot `runtime_package/` consumption copy;
- a generált runtime package nem canonical szerkesztési forrás;
- a publish előtt validáció szükséges.

Elsődleges publish runner:

- `python/publish_runtime_package_to_godot.bat`

A TEMP candidate staging:

- jelenleg elfogadott átmeneti megoldás;
- nem végleges release-architektúra;
- később külön build/output struktúrával váltható ki.

---

## 8. Jelenlegi futási és fejlesztési modell

### Headless fejlesztés

A rules engine elsődleges fejlesztési módja:

- Python unit és contract tesztek;
- isolated test module futtatás;
- minimal engine smoke;
- AI-vs-AI text smoke;
- AI-vs-AI JSON smoke;
- determinisztikus ismétlés.

### Godot fejlesztés

A Godot fejlesztés elsődleges módja:

- loader smoke;
- debug scene;
- headless Godot teszt;
- explicit `--log-file` Windows/Godot 4.7 alatt;
- player-facing contractok megjelenítésének fokozatos bekötése.

### Adatpipeline-fejlesztés

- explicit source/output útvonalak;
- candidate build;
- validation gate;
- dry-run;
- Godot consumption copy csak sikeres build után.

---

## 9. Tesztelési technológiai döntések

Elfogadott:

- minden új engine-contract kapjon célzott tesztet;
- minden state mutation kapjon success és rejection tesztet;
- rejected action ne mutáljon state-et;
- a teljes Python tesztkészlet izolált modulonként is fusson;
- minimal engine smoke kötelező;
- AI-vs-AI determinisztikus JSON ellenőrzés kötelező;
- player-visible hidden-information tesztek kötelezők;
- deep-copy és inputváltozatlanság ellenőrzendő;
- Git státusz minden technikai checkpointnál ellenőrzendő.

Ismert tesztinfrastruktúra-adósság:

- két sorrendfüggő XLSX mock-probléma a monolitikus discoveryben.

Ezek külön izolációs feladatban javítandók, nem szabad véletlenül engine-refaktorral összekeverni.

---

## 10. Csomagolás és terjesztés

A 0.0.1 egyik célja az egyszerű Windows-indítás.

A Python-authoritative modell miatt később külön bizonyítani kell:

- hogyan kerül a Python runtime a tesztbuildbe;
- hogyan indul a Godot kliens és Python engine együtt;
- hogyan találják meg a runtime package-et;
- hogyan készül a mentés és log;
- hogyan készül reprodukálható hibajelentési csomag;
- hogyan kezelhető az engine process összeomlása;
- hogyan történik a verzióegyeztetés.

Ez fontos termékesítési kapu, de nem blokkolja a jelenlegi M1–M3 szabálymotor-fejlesztést.

Javasolt későbbi bizonyítás:

- minimális Windows package prototype;
- Godot launcher;
- Python engine child process;
- egy action request/response kör;
- tiszta leállítás;
- hibás engine-verzió kontrollált jelzése.

---

## 11. AI és szimuláció technológiai helye

Az AI-vs-AI elsődleges futási helye Python.

Rövid távon:

- deterministic bot policy;
- smoke és scenario runner;
- trajectory;
- invariánsellenőrzés.

Hosszú távon:

- valódi játékosszerű AI;
- több nehézség;
- batch matchup tesztek;
- balance report;
- replay és reprodukálhatóság;
- AI-vs-player.

A fair AI ugyanazt a player-visible információt használja, mint az emberi játékos.

Debug AI külön, explicit módban kaphat több információt.

---

## 12. Codex és közvetlen GitHub-munka szerepe

Codex vagy más kódoló agent használható:

- szűk engine-contract feladatra;
- célzott validátorra;
- konkrét transitionre;
- tesztkészítésre;
- loader- vagy registry-javításra;
- exportpipeline-részfeladatra.

Nem delegálható önállóan:

- hivatalos szabályi döntés;
- teljes projektirányítás;
- nagy, homályos refaktor;
- automatikus törlés vagy tömeges mozgatás;
- kétértelmű gameplay feltételezés;
- végleges dokumentációs elsőbbség meghatározása.

Programozási prompt követelményei:

- szűk cél;
- előzetes vizsgálat;
- explicit scope;
- explicit nem-célok;
- schema- és invariáns-elvárások;
- célzott és regressziós tesztek;
- smoke futtatások;
- commitfeltételek;
- részletes végső jelentés.

A GitHub a repository elsődleges átadási és együttműködési felülete.

---

## 13. Nyitott technológiai döntések

A fő rules-engine technológia már nem nyitott.

Még nyitott:

- Python–Godot transport;
- Windows packaging;
- Python runtime beágyazás vagy sidecar;
- engine process lifecycle;
- save/load tárolási forma;
- replay végrehajtási forma;
- CI-ben futó Python és Godot tesztek köre;
- performance profiling küszöbök;
- nagy AI batch futások infrastruktúrája;
- runtime package release/version registry;
- TEMP candidate staging későbbi kiváltása;
- publikus build integritásvédelme.

A közeli döntések részletes helye:

- `CURRENT_OPEN_QUESTIONS.md`

A teljes történeti kérdésregiszter:

- `OPEN_QUESTIONS.md`

---

## 14. Következő technológiai bizonyítási lépések

A jelenlegi sorrend:

1. Wellspring production MatchState-integráció.
2. Player-visible Wellspring summary.
3. Beáramlás precondition és transition.
4. Magnitúdó- és Aura-payment réteg.
5. Első `play_card` action.
6. Phase és priority rendszer bővítése.
7. Első tényleges játszható Python vertical slice.
8. Python–Godot action request/response integrációs prototípus.
9. Godot player UI vertical slice.
10. Windows packaging prototype.

A Godot-integrációt nem kell a rules engine minden lépésével párhuzamosan fejleszteni, de az első stabil játszható vertical slice előtt újra aktív prioritássá válik.

---

## 15. Biztos döntések összefoglalója

- A Python engine authoritative szabálymotor.
- A Godot kliens-, loader-, registry-, debug- és UI-réteg.
- Nem készül két külön authoritative rules engine.
- A frontend és az AI nem találgat legalitást.
- A kliens action requestet küld.
- A state mutation a Python engine-ben történik.
- A player-visible és debug projection külön marad.
- A runtime package statikus adatcontract.
- Godot nem olvas közvetlenül XLSX-et.
- A Python végzi az exportot, validációt és runtime package buildet.
- Az AI-vs-AI elsődleges futási helye Python.
- A régi Python motor review és referencia.
- A Windows packaging későbbi külön technológiai kapu.
- A jelenlegi közvetlen cél a stabil rules engine, nem a végleges kliens.
