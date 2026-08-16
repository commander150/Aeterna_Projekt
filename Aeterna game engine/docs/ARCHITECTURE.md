# AETERNA Game Engine – Architecture

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.5
**Dátum:** 2026-08-16
**Státusz:** aktív kanonikus rendszerarchitektúra
**Szinkronizációs repository-bázis:** `14e315d3f04f5baddb547dcb767c8b156b02551f`
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

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
- `../../Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.6.md`

---

### Blueprint- és evolving-design határ

A `docs/blueprints/` AETERNA architecture proposal/current-foundation expansion réteg. Learning/synthesis evidence-ből táplálkozhat, de önmagában nem rules authority.

Current canonical architecture explicit reviewed döntéssel később módosítható, ha playtest, Expansion, meta vagy bizonyított architecture probléma indokolja. A lezárt runtime-language gate ettől nem nyílik újra automatikusan.

Történeti változás: `EXTENDED / SCOPED / SUPERSEDED / REPLACED`.

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

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4.3v.docx`;
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`.

A kód, structured mező, learning projekt vagy régi Python-implementáció nem írhatja felül ezeket emberi döntés nélkül.

Szabályi/contract prioritás:

1. hivatalos szabályforrás;
2. elfogadott, verziózott emberi döntés;
3. aktív Open Questions decision log;
4. aktív contract/specification;
5. elfogadott fixture/reference;
6. production implementáció mint technikai bizonyíték.

A Python referencia nem automatikus szabályspecifikáció. A működő production kód technikai tényt bizonyíthat, de új játékszabályt nem.


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

Státusz: aktív `net8.0` production authoritative core. A C.5B történeti foundationben a MatchState/PlayerState minimum, typed contractok, `EngineSession`, runtime package minimum loader, draw, end-turn és stale rejection valósult meg. A `931bf... → 2608345b...` szakaszban ehhez production Wellspring/Infusion, payment preflight, Domain/`play_card`, canonical ability/effect foundation, damage/vitals, continuous/modifier/keyword/duration, draw/reference runtime és Explicit Phase Foundation társult.

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

A production C# modell aktív fő elemei:

### MatchState

- match ID;
- seed;
- state version;
- turn number;
- canonical phase;
- `StartingPlayerId`;
- active player;
- priority player;
- player state-ek;
- card instance registry;
- Domain;
- Wellspring;
- pending trigger/decision state;
- continuous effect state;
- modifier/keyword/duration state;
- event sequence és event log;
- match result.

### PlayerState

- player ID;
- deck ID;
- deck card instance ID-k;
- hand card instance ID-k;
- canonical Void card instance ID-k;
- Wellspring card instance ID-k;
- erőforrás-summary;
- turn-scoped usage state;
- player-specifikus runtime state.

A MatchState belső authoritative adat, normál kliensnek nem exportálható közvetlenül.

### 9.1 Canonical phase lifecycle

A phase az authoritative state része, nem dekoratív label.

Canonical sorrend:

`awakening -> infusion -> manifestation -> incursion -> distribution`

Elvek:

- public progression: `advance_phase`;
- Awakening entry automatikus ready/draw logikát futtat;
- a kezdő játékos első Awakeningje explicit 0-draw kivétel;
- Distribution explicit, megfigyelhető state;
- `incursion -> distribution` turn-end cleanup boundary;
- `distribution -> awakening` vált aktív játékost;
- legal action space phase-specifikus;
- automatic phase entry logic a C# core feladata.

A következő architecture expansion a Reaction/Priority pending state; combat külön későbbi layer.


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

Canonical/aktív zónák:

- deck;
- hand;
- wellspring;
- domain;
- void;
- szükség szerinti explicit resolution/intermediate zone.

A `discard` nem canonical C# zónanév: eldobás művelet/ok lehet, normál canonical célzónája a `void`, ha replacement szabály másként nem rendelkezik.

A Domain pozíció nem egyszerű listaindex, hanem topology és occupancy alapján kezelt authoritative state.


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
- canonical Void public;
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

## 17. Migrációs és production mérföldkő-sorrend

### C.5A

`COMPLETE_AND_ACCEPTED`

Rögzítette a production C# architecture tervet.

### C.5B

Lezáró commit:

`931bf5571d541c752aa421a9f0626768bd8ffbe7`

`COMPLETE_AND_ACCEPTED`

Történeti foundation:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- `EngineSession`;
- runtime package minimum loader;
- draw/end-turn proof;
- Godot production bridge;
- RuntimeCandidate/Python regresszió.

Történeti acceptance:

- Debug/Release `13/13`;
- canonical SHA-egyezés;
- `100/100` determinisztika;
- Godot pozitív/negatív smoke.

### C.5B utáni production gameplay vertical slice

`COMPLETE_AND_ACCEPTED`

Megvalósult:

- Wellspring;
- player-visible Wellspring;
- Beáramlás;
- Magnitúdó/Aura payment preflight;
- `play_card`;
- Domain placement;
- canonical ability/effect foundation;
- damage/vitals;
- continuous/modifier/keyword/duration;
- draw/reference runtime.

### Explicit Phase Foundation v1

Lezáró commit:

`2608345b61526097fc0b118f05461f92cfed0a95`

`COMPLETE_AND_ACCEPTED`

Canonical lifecycle:

`awakening -> infusion -> manifestation -> incursion -> distribution`

### Következő architecture expansion

1. Reaction / Priority minimal contract;
2. Reaction / Priority production foundation;
3. külön combat contract/foundation;
4. Pecsét/Refresh/victory rétegek a saját rules gate-jeik után;
5. replay/AI/UI/packaging későbbi mérföldkövek.

A korábbi Wellspring-first migrációs sor történeti, nem current roadmap.

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
- verzióblokk, dátum és státusz minden aktív dokumentumban;
- történeti fájlok elkülönítése;
- tartalomvesztés nélküli merge;
- nyitott kérdések és proof-folytonosság megőrzése.

Alapszabály:

- meglévő aktív dokumentumot frissítünk;
- új dokumentum csak önálló canonical szerep esetén készül;
- `CURRENT_*` előd nem aktív authority;
- párhuzamos aktív authority nem maradhat;
- törlés/archiválás csak ellenőrzött utóddal történhet;
- minden nagy mérföldkőnél célzott, nem tömeges consistency audit történhet.

A `2608345b...` mérföldkőhöz tartozó A+B consistency pass lezárult.

## 20. Rövid aktuális összefoglaló

- A hivatalos játékszabályok az elsődleges források.
- A Python adatpipeline, audittooling és reference/oracle megmarad.
- A Godot/GDScript a vizuális kliensréteg.
- A C#/.NET az egyetlen aktív authoritative production runtime.
- A Godot és a C# közvetlenül, ugyanazon processzen belül kommunikál.
- A Python a C# headless interfészt használhatja AI-, batch- és elemzési célra.
- A Python-sidecar proof lezárt és befagyasztott.
- A C# in-process proof lezárt és elfogadott.
- A C.5B production engine foundation lezárt.
- A post-C.5B gameplay/ability vertical slice lezárt.
- Az Explicit Phase Foundation v1 lezárt.
- A `2608345b...` dokumentációs consistency pass lezárt.
- A következő szakmai engine-fókusz Reaction / Priority rules és minimal contract.
- Combat külön későbbi architecture/rules slice.
