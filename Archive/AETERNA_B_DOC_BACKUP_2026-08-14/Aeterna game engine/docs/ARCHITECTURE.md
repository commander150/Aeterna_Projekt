# AETERNA Game Engine – Architecture

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.3\
**Dátum:** 2026-07-22\
**Státusz:** aktív kanonikus rendszerarchitektúra  
**Aktuális repository-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`

Ez a dokumentum az AETERNA digitális rendszerének aktív architektúráját, réteghatárait és authority-szabályait rögzíti.

A korábbi nyitott runtime-alternatívák döntési kapuja lezárult.

Az elfogadott hosszú távú felosztás:

- **Godot/GDScript:** vizuális kliens- és megjelenítési réteg;
- **C#/.NET:** egyetlen kanonikus authoritative szabálymotor;
- **Python:** külső adat-, audit-, teszt-, AI-, batch- és elemzőeszközréteg.

Kapcsolódó aktív dokumentumok:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `TECHNOLOGY_DECISIONS.md`
- `DECISION_MAP.md`
- `PROTOTYPE_STATUS.md`
- `CONTRACT_STATUS.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `checkpoints/ENGINE_CHECKPOINT.md`
- `../../Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.4.md`

---

## 1. Stabil architektúra-alapelvek

A következő elvek kötelezőek:

- előbb contract, utána implementáció;
- egy adott meccsnek pontosan egy authoritative state-je lehet;
- a UI nem lehet szabályforrás;
- a frontend és az AI nem találgathat legalitást;
- state mutation csak validált engine transition útján történhet;
- a kliens action requestet küld;
- az engine action response-t, eventet és projectiont ad;
- player-visible és debug contract külön marad;
- rejtett információt projection véd;
- eventek determinisztikusak és auditálhatók;
- a runtime package statikus programadat, nem szabálymotor;
- a Python nem lehet a C# mellett második kanonikus rules engine;
- a Godot/GDScript nem módosíthat közvetlenül authoritative state-et.

---

## 2. Felső szintű rendszerkép

```text
Hivatalos szabályforrások
        ↓
Google Sheets / XLSX / LOOKUPS
        ↓
Python adatpipeline
        ↓
Validált runtime package
        ↓
C# authoritative engine
        ↓
Snapshotok / legal actionök / action response-ok / eventek
        ↓
Godot / GDScript vizuális kliens
```

Külső fejlesztői és elemző ág:

```text
Python audit / AI / batch / simulation tooling
        ↓
C# headless engine API
        ↓
Canonical eredmény / eventek / snapshotok
        ↓
Python statisztika / riport / balanszelemzés
```

A játékosnál futó normál Godot kliens nem igényel Python-processzt.

---

## 3. Hivatalos szabályréteg

Elsődleges szabályforrások:

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

A kód, structured mező, tanulóprojekt vagy régi Python-implementáció nem írhatja felül ezeket emberi döntés nélkül.

Implementációs prioritás:

1. hivatalos szabályforrás;
2. aktív contract vagy specifikáció;
3. elfogadott fixture;
4. Python referencia;
5. C# production implementáció.

A Python referencia nem automatikus szabályspecifikáció.

---

## 4. Szerkesztési adatforrás és runtime package

### 4.1 Szerkesztési forrás

- Google Sheets;
- abból letöltött XLSX munkaforrások;
- aktív kártyaadatbázis;
- `LOOKUPS.xlsx`;
- hivatalos főforrások.

### 4.2 Python adatpipeline

Feladata:

- XLSX beolvasás;
- export;
- canonical normalizálás;
- legacy alias audit;
- validáció;
- runtime package build;
- diagnostics és report;
- Godot consumption copy publikálása.

### 4.3 Runtime package

Statikus adatcontract:

- kártyák;
- deckek;
- lookupok;
- aliasok;
- ability registry;
- engine-support;
- diagnostics;
- build report.

A runtime package nem tartalmaz:

- futó MatchState-et;
- meccsspecifikus card instance-eket;
- aktív turn vagy phase állapotot;
- authoritative rules runtime-ot.

A C# engine runtime package-et fogyaszt, de nem olvas közvetlenül XLSX-et.

---

## 5. Godot és GDScript réteg

### 5.1 Feladatok

- jelenetek;
- inputkezelés;
- vizuális kártyák;
- animációk;
- hangok;
- menük;
- debugpanelek;
- snapshotok megjelenítése;
- legal actionök felkínálása;
- action requestek összeállítása;
- engine eventek vizuális feldolgozása.

### 5.2 Tiltott felelősségek

A GDScript nem:

- dönthet egy action szabályosságáról;
- vonhat le Aurát;
- mozgathat authoritative kártyapéldányt;
- válthat kört engine transition nélkül;
- oldhat fel kártyahatást;
- módosíthat state versiont;
- tárolhat külön kanonikus játékmenetet.

### 5.3 Godot–C# kapcsolat

A Godot a C# engine-t ugyanazon processzen belül hívja:

```text
GDScript / UI
    ↓
Godot C# bridge
    ↓
Aeterna.Engine
    ↓
Godot C# bridge
    ↓
JSON / Dictionary / signal alapú klienscontract
    ↓
GDScript / UI
```

Nem szükséges:

- TCP;
- HTTP;
- gRPC;
- külön rules engine-processz;
- watchdog;
- Python sidecar.

A bridge nem tartalmazhat játékszabályt.

---

## 6. C# authoritative engine

A C# engine az egyetlen kanonikus runtime.

### 6.1 Felelősségek

- MatchState;
- PlayerState;
- CardInstance;
- zónák;
- turn és phase;
- priority;
- legal action számítás;
- action request-validáció;
- költségek;
- targeting;
- transitionök;
- effect resolution;
- trigger és reaction;
- combat;
- typed eventek;
- player-visible snapshot;
- debug projection;
- replay-alap;
- determinisztikus random;
- győzelmi és vereségi feltételek.

Nem minden elem implementált jelenleg, de hosszú távon mind ide tartozik.

### 6.2 Authority-szabály

Az authoritative állapot kizárólag a C# belső `MatchState`.

State mutation kizárólag:

```text
SubmitAction(ActionRequest)
```

vagy azzal egyenértékű belső, validált engine transition kapun keresztül történhet.

Nem adható ki:

- módosítható MatchState;
- módosítható PlayerState;
- közvetlen zónalista-referencia;
- belső registry-referencia.

### 6.3 Aktív production projektek

```text
Aeterna game engine/
└── C#/
    ├── Aeterna.Engine.sln
    ├── Aeterna.Engine/
    ├── Aeterna.Engine.Headless/
    └── Aeterna.Engine.Tests/
```

#### Aeterna.Engine

Pure C# class library:

- Godot-hivatkozás nélkül;
- Python-hivatkozás nélkül;
- UI nélkül;
- TCP/HTTP/gRPC nélkül;
- operációsrendszer-processz kezelés nélkül.

Státusz: aktív `net8.0` production foundation. A C.5B-ben a MatchState/PlayerState minimum, typed contractok, `EngineSession`, runtime package minimum loader, draw, end-turn és stale rejection valósult meg.

#### Aeterna.Engine.Headless

Vékony futtató:

- fixture;
- scenario;
- AI/batch;
- CI;
- Python tooling kapcsolat.

Nem tartalmaz saját gameplay-szabályt.

Státusz: aktív, ugyanazt az `Aeterna.Engine` implementációt futtató headless host.

#### Aeterna.Engine.Tests

C# contract-, invariant-, transition-, determinism- és regressziós tesztek.

Státusz: aktív production tesztprojekt.

---

## 7. Python szerepe

### 7.1 Aktív feladatok

- adatfeldolgozás;
- XLSX/JSON/JSONL;
- audit;
- runtime package build;
- fixture-generálás;
- batchteszt;
- AI-vs-AI koordináció;
- balanszelemzés;
- statisztika;
- riport;
- regressziós összehasonlítás.

### 7.2 Python minimal engine referencia

A meglévő Python minimal engine:

- működő referencia;
- comparison oracle;
- differential testing alap;
- AI- és batchkutatási forrás;
- migrációs bizonyíték.

A saját futásaiban authoritative, de nem a végleges játék production authoritative runtime-ja.

Új production gameplay-szabályt nem szabad kizárólag Pythonban továbbfejleszteni.

### 7.3 Python–C# kommunikáció

Első tervezett forma:

```text
Python
  ↓ subprocess + JSON/JSONL
Aeterna.Engine.Headless
  ↓ canonical JSON/JSONL
Python
```

A Python:

- meccset vagy scenario-t kezdeményezhet;
- snapshotot kérhet;
- legal actionökből választhat;
- action requestet küldhet;
- eredményt elemezhet.

A Python nem:

- írhat közvetlenül C# MatchState-et;
- mozgathat kártyát a `SubmitAction` megkerülésével;
- számíthat külön authoritative legalitást;
- adhat át olyan állapotot, amelyet a C# validálás nélkül elfogad.

### 7.4 Későbbi service API

Localhost HTTP vagy gRPC csak teljesítménymérés alapján vizsgálható.

Nem alapértelmezett architektúra.

---

## 8. Bizonyított runtime-jelöltek

### 8.1 Python–Godot sidecar

**Státusz:** `COMPLETE AND FROZEN`

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e`

Bizonyított:

- localhost TCP;
- handshake;
- request/response;
- shutdown;
- emergency shutdown;
- parent watchdog;
- orphan cleanup;
- Godot integráció;
- helyes canonical output.

Megmarad proofként, de nem production főirány.

### 8.2 C# in-process candidate

**Státusz:** `COMPLETE AND ACCEPTED`

Lezáró commit:

`8e5ee64e42e1657e10f3413444bb870524ee07f9`

Bizonyított:

- pure C#;
- Godot .NET in-process;
- nincs Python;
- nincs TCP;
- nincs külön engine-processz;
- Debug/Release build;
- headless és visual proof;
- 100-run determinisztika;
- mutation proof;
- helyes canonical SHA.

Közös comparison SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

A candidate projekt proofként megőrzendő, nem közvetlenül átnevezendő production motorrá.

---

## 9. MatchState és PlayerState

A production C# modell tervezett fő elemei:

### MatchState

- match ID;
- seed;
- state version;
- turn number;
- phase;
- active player;
- priority player;
- player state-ek;
- card instance registry;
- Domain;
- Wellspring;
- event sequence;
- event log;
- match result.

### PlayerState

- player ID;
- deck ID;
- deck card instance ID-k;
- hand card instance ID-k;
- discard card instance ID-k;
- Wellspring card instance ID-k;
- erőforrás-summary;
- player-specifikus state.

A MatchState belső authoritative adat, normál kliensnek nem exportálható közvetlenül.

---

## 10. Card instance és zónák

A card definition és a meccsbeli card instance külön objektum.

Card instance fő adatai:

- instance ID;
- Card_ID;
- owner;
- controller;
- zone;
- zone index vagy board position;
- visibility;
- activity state;
- created sequence;
- zone sequence;
- runtime metadata.

Tervezett aktív zónák:

- deck;
- hand;
- discard;
- wellspring;
- domain;
- void;
- szükség szerinti átmeneti resolution zóna.

A Domain pozíció nem egyszerű listaindexként kezelendő, hanem topology és occupancy alapján.

---

## 11. Domain és board

Játékosonként:

- 6 Áramlat;
- 6 Horizont;
- 6 Zenit;
- 6 Pecsét-pozícióreferencia;
- 12 card occupancy slot.

A topology, occupancy és card instance registry kölcsönösen validált.

A player-visible board public projection, nem teljes MatchState-dump.

A Pecsét állapota külön authoritative modell, nem hagyományos card occupancy slot.

---

## 12. Player-visible és debug projection

### Player-visible snapshot

- saját kéz látható;
- ellenfél kéz redacted;
- deck count-only;
- discard public;
- Domain board public;
- Wellspring owner-specifikusan rejtett;
- legal action lista;
- public turn/phase/resource összefoglaló;
- csak a néző számára engedélyezett információ.

### Debug projection

Külön contracton adhat:

- teljes registry;
- topology;
- occupancy;
- invariantdiagnosztika;
- belső event payload;
- state hash;
- reprodukciós adatok.

A fair AI ugyanazt a player-visible observationt használja, mint az emberi játékos.

---

## 13. Action- és event-architektúra

### Publikus engine API

Aktív minimum:

```text
CreateMatch
GetPlayerSnapshot
ListLegalActions
SubmitAction
GetEvents(viewerPlayerId, afterSequence)
GetMatchResult
```

### ActionRequest

Minimum:

- schema version;
- request ID;
- match ID;
- player ID;
- expected state version;
- action ID;
- action type;
- payload.

### ActionResponse

Minimum:

- accepted;
- reason;
- state version before;
- state version after;
- events;
- diagnostics.

### EngineEvent

Minimum:

- event ID;
- sequence;
- event type;
- match ID;
- state version;
- public payload;
- szükség esetén projection-specific payload.

A publikus event API viewer-azonosított és redaktált. A teljes event payload csak internal headless/teszt debughatáron érhető el; a Godot production bridge ezt nem exportálja.

Rejected action esetén:

- állapot nem változhat;
- event sequence nem változhat;
- request nem módosulhat;
- stabil reason és diagnostic code szükséges.

---

## 14. Determinizmus és canonical serialization

Kötelező:

- explicit sorrendezés;
- `StringComparer.Ordinal`;
- stabil array-sorrend;
- UTF-8;
- BOM nélkül;
- LF;
- object keyek ordinal sorrendben;
- egész számok egész formában;
- SHA-256 lowercase hex;
- seedelt random;
- reprodukálható event sequence;
- byte-szintű összevethető fixture-eredmény.

A dictionary természetes enumerációs sorrendje nem használható canonical output alapjaként.

---

## 15. Tesztelési architektúra

Minden production C# migrációhoz szükséges:

- hivatalos szabályforrás-ellenőrzés;
- typed contract;
- pozitív fixture;
- negatív fixture;
- state invariant;
- action immutability;
- stale-state immutability;
- hidden-information;
- determinisztika;
- canonical SHA;
- Python reference comparison;
- candidate regression;
- Godot in-process proof;
- GDScript regresszió;
- Debug és Release build;
- warning/error audit;
- process- és listener-audit.

A teszteknek Godot nélkül is futtatható pure C# útvonalat kell biztosítaniuk.

---

## 16. Packaging és futtatás

### Normál játék

```text
Godot .NET application
    └── C# authoritative engine
```

Nem kötelező runtime-komponens:

- Python;
- külön engine executable;
- TCP-listener;
- localhost service;
- watchdog.

### Fejlesztői és batch futás

```text
Aeterna.Engine.Headless
```

Használhatja:

- Python;
- CI;
- audittooling;
- AI-vs-AI runner;
- fixtureteszt;
- balanszelemzés.

A végleges Windows packaging production engine mellett még külön bizonyítandó.

---

## 17. Migrációs sorrend

### C.5A

**Státusz:** `COMPLETE`

Production architecture és project-határok rögzítve.

### C.5B

**Státusz:** `COMPLETE_AND_ACCEPTED`

Lezáró commit:

`931bf5571d541c752aa421a9f0626768bd8ffbe7`

Feladata:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- `Aeterna.Engine.sln`;
- core contractok;
- EngineSession;
- runtime package minimum loader;
- draw/end-turn production reprodukció;
- Godot production bridge;
- candidate regresszió.

Ellenőrzött minimum:

- Debug/Release production build és `13/13` teszt;
- canonical SHA-egyezés és `100/100` determinisztika;
- viewer-safe event projection;
- strukturált JSON boundary rejection;
- Godot pozitív és negatív production bridge smoke.

### Következő gameplay-sorrend

1. Wellspring production integráció;
2. player-visible Wellspring;
3. Beáramlás;
4. Magnitúdó;
5. Aura-payment;
6. `play_card`;
7. Entity Domain placement;
8. phase és priority;
9. reaction;
10. combat;
11. ability execution;
12. win/loss.

---

## 18. Elvetett architektúrák

### Python sidecar production főmotor

Működőképes, de nem választott production irány.

### Tiszta GDScript authoritative engine

Nem épül.

### C# és Python között megosztott authoritative gameplay

Tiltott.

### Embedded Python a normál játék runtime-jában

Jelenleg nem indokolt.

### Godot–C# HTTP/TCP kapcsolat

Felesleges, mert közvetlen in-process hívás rendelkezésre áll.

---

## 19. Dokumentációs architektúra

A projekt dokumentumkezelésének célja:

- kevés aktív fődokumentum;
- egyértelmű dokumentumszerepek;
- verzióblokk minden aktív dokumentumban;
- státusz és dátum minden aktív dokumentumban;
- történeti fájlok elkülönítése;
- tartalomvesztés nélküli merge;
- nyitott kérdések megőrzése.

Alapszabály:

- meglévő aktív dokumentum frissítendő;
- új dokumentum csak önálló canonical szerep esetén készülhet;
- verzió nélküli aktív dokumentumokat a későbbi teljes auditban verzióval kell ellátni;
- párhuzamos current dokumentumok később összevonandók;
- törlés vagy archiválás csak teljes audit és jóváhagyás után történhet.

---

## 20. Rövid aktuális összefoglaló

- A hivatalos játékszabályok az elsődleges források.
- A Python adatpipeline és audittooling megmarad.
- A Python minimal engine referencia és comparison oracle.
- A Godot/GDScript a vizuális kliensréteg.
- A C#/.NET az egyetlen tervezett authoritative runtime.
- A Godot és a C# közvetlenül, ugyanazon processzen belül kommunikál.
- A Python a C# headless interfészt használhatja AI-, batch- és elemzési célra.
- A Python-sidecar proof lezárt és befagyasztott.
- A C# in-process proof lezárt és elfogadott.
- A C.5B production engine foundation elkészült és elfogadott.
- A következő kódolási szakasz a Wellspring production state és player-visible Wellspring.
- A nem programozási aktív sáv dokumentáció, audit, projektirány, LOOKUPS- és kártyaadatmunka.
