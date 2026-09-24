# AETERNA Game Engine – Architecture

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.7
**Dátum:** 2026-09-05
**Státusz:** aktív kanonikus rendszerarchitektúra
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9` – `engine: add aeternal outcome and terminal match result`

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
- `../../project/status/checkpoints/ENGINE_CHECKPOINT.md`
- `../../project/planning/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.9.md`

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

- `rules/sources/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.5v.docx`;
- `rules/sources/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4.1v.docx`.

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

Státusz: aktív `net8.0` production authoritative core. A C.5B történeti foundationben a MatchState/PlayerState minimum, typed contractok, `EngineSession`, runtime package minimum loader, draw, end-turn és stale rejection valósult meg. A korábbi gameplay/ability foundation és Explicit Phase után ugyanebben a core-ban zárult le a Reaction / Priority Foundation v1, majd a Combat + Pecsét Foundation C0–C6 és a terminal Aeternal / `MatchResult` outcome.

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
- `ReactionWindow`;
- `ResolutionStack`;
- `QueuedTriggerBatches`;
- `MatchSetupState`;
- `PendingCombatState`;
- `PendingSurgeWindowState`;
- `SealSlots`;
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

A Reaction/Priority pending state és Combat/Pecsét current production layer már aktív. A következő architecture gate nem generic engine-layer, hanem `VS1_READINESS_REQUIRED`.


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

### C.5B

`COMPLETE_AND_ACCEPTED`

### Korábbi production gameplay/ability foundation slice

`COMPLETE_AND_ACCEPTED`

Ez a Wellspring / Infusion / Domain / `play_card` / ability-effect / damage-vitals /
continuous-modifier-keyword-duration és kapcsolódó foundation réteg.

### Explicit Phase Foundation v1

Lezáró commit:

`2608345b61526097fc0b118f05461f92cfed0a95`

`COMPLETE_AND_ACCEPTED`

### Reaction / Priority Foundation v1

Lezáró commit:

`f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`

`COMPLETE_AND_ACCEPTED`

### Combat + Pecsét Foundation C0–C6

Rules migration:

`61ad2605dd1aa3d7ea95444f0bb66cebf819014e`

Production commitlánc:

- C0 `ca55bc3714de2692753fccc18a8f11d9dac1beea`;
- C1+C2 `558d4453a1604c0ebe76065df08a207192c21c8b`;
- C3 `d236f0e3c36994f65e7d00d25972660baac2a842`;
- C4 `68b07dd6906fc8c37245325a855322d48f5f2635`;
- C5 `d30f8a4c42383a0200e416acb7148facc3bbbc11`;
- C6 `0862e1002dbef81ee203852714d377592272a0e9`.

Current state:

`COMBAT_AND_SEAL_FOUNDATION_C0_C6 = COMPLETE_AND_ACCEPTED`

A C0–C6 nem külön engine vagy külön authority-réteg:
a meglévő `Aeterna.Engine` authoritative MatchState/action/event/projection architektúrát bővíti.

### Current next gate

`VS1_READINESS_REQUIRED`

Következő major product-facing cél:

`VS1 / M6 – első ténylegesen játszható vertical slice`

Canonical VS1 deckek:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

A következő architecture/implementation munka nem előre kijelölt generic engine-feature.
Előbb a két VS1 deck tényleges card/mechanic readiness auditja azonosít blockert.

VS1 előtt kötelező csak:

1. a két canonical deck szabályos futásához szükséges capability; vagy
2. általános rules-correct / deterministic / viewer-safe invariáns.

Ezután:

```text
simple fair AI + match orchestration
→ minimal playable Godot
→ human-vs-AI full match
→ reproducible AI-vs-AI smoke
→ VS1 acceptance
→ szükséges köztes mérföldkövek
→ AETERNA 0.0.1
```

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

A current dokumentációs sync a `0862e100...` Combat + Pecsét C0–C6 lezárás utáni current-truth állapotot követi. A korábbi consistency passok történeti evidence-ként megmaradnak.

## 20. Rövid aktuális összefoglaló

- A hivatalos játékszabályok az elsődleges rules authority-k:
  Core `1.5v`, Expansion `1.4.1v`.
- A Python adatpipeline, audittooling és reference/oracle megmarad.
- A Godot/GDScript a vizuális kliens- és presentation réteg.
- A C#/.NET az egyetlen authoritative production rules runtime.
- Godot ↔ C# production kapcsolat same-process; nincs production sidecar/TCP/HTTP/gRPC rules path.
- Python ↔ engine tooling kapcsolat headless JSON/JSONL/subprocess alapon használható.
- `MatchState` current productionben ReactionWindow, ResolutionStack, queued trigger,
  pending Combat/Surge, Seal slot és terminal MatchResult state-et is tartalmaz.
- Reaction / Priority Foundation v1 `COMPLETE_AND_ACCEPTED`.
- Combat + Pecsét Foundation C0–C6 `COMPLETE_AND_ACCEPTED`.
- Current production base:
  `0862e1002dbef81ee203852714d377592272a0e9`.
- Current OQ:
  `52 answered / 15 partly_answered / 7 deferred / 0 open`.
- Következő gate:
  `VS1_READINESS_REQUIRED`.
- Következő major product-facing cél:
  `VS1 / M6 – első ténylegesen játszható vertical slice`.
- A későbbi generic prevention/replacement, compound choice, Refresh Penalty,
  Hasítás, full Burst/Jel, replay, AI orchestration, UI és packaging nem mind automatikus VS1-blocker.
