# AETERNA Game Engine – Architecture

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív célarchitektúra és jelenlegi réteghatár-dokumentum  
**Aktuális technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum az AETERNA Game Engine jelenlegi célarchitektúráját és a már működő technikai rétegeket rögzíti.

Nem helyettesíti:

- a hivatalos játékszabályokat;
- a runtime package részletes specifikációját;
- a contractok mezőszintű specifikációját;
- az ability module rendszer tervét;
- az aktuális technikai checkpointot.

Kapcsolódó elsődleges dokumentumok:

- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`
- `CURRENT_CONTRACT_STATUS.md`
- `CURRENT_OPEN_QUESTIONS.md`
- `CONTRACT_SPECIFICATION.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `TECHNOLOGY_DECISIONS.md`
- `ABILITY_MODULE_SYSTEM.md`

Eltérés esetén a hivatalos 1.4v főforrások, a v6.0 projektterv és a `CURRENT_ENGINE_CHECKPOINT.md` a frissebb státuszforrás.

---

## 1. Architektúra-alapelv

Az AETERNA digitális rendszerének alapelve:

> **Előbb contract, utána implementáció; a szabálymotor az authoritative állapot egyetlen végrehajtási helye.**

Ennek következményei:

- a kliens nem módosítja közvetlenül a MatchState-et;
- a frontend és az AI nem találgat legalitást;
- a Godot nem tartalmazhat rejtett, párhuzamos szabálylogikát;
- a state mutation csak validált action request vagy belső engine transition útján történhet;
- a player-visible és debug nézet külön contract;
- a rejtett információt a projection-réteg védi;
- az események determinisztikus és auditálható történeti réteget alkotnak;
- a runtime package programbiztos adatforrás, nem szabálymotor.

---

## 2. Magas szintű rendszerkép

A jelenlegi célarchitektúra:

    Hivatalos szabályforrások
            ↓
    Google Sheets / XLSX kártyaadat- és LOOKUPS-forrás
            ↓
    Python export, normalizálás és validáció
            ↓
    Validált runtime package
            ↓
    Python authoritative rules engine
            ↓
    MatchState + invariánsok
            ↓
    Legal actions / action request / transition
            ↓
    Typed events + új state version
            ↓
    Player-visible / debug / AI projection
            ↓
    Godot kliens, debug UI, AI és tesztrendszer

A lánc nem jelenti azt, hogy minden futtatásnál újra kell építeni a runtime package-et. A package a kártya- és lookup-adatot szolgáltatja, a meccs authoritative állapotát a rules engine kezeli.

---

## 3. Rétegek és felelősségek

### 3.1 Hivatalos szabályréteg

Elsődleges források:

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

Felelőssége:

- a Core szabályok meghatározása;
- az alapjáték és kiegészítő réteg elhatárolása;
- terminológia és mechanikai jelentés;
- engine-megfelelés végső szabályi alapja.

A kód, a structured mező és a régi dokumentáció nem írhatja felül ezt a réteget.

### 3.2 Szerkesztési adatforrásréteg

Elsődleges emberi szerkesztési forma:

- Google Sheets;
- abból letöltött aktív XLSX munkaforrások.

Fő helyi források:

- kártyák és decklisták: `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- runtime lookupok: `LOOKUPS.xlsx`.

Ez a réteg emberi szerkesztésre szolgál, nem közvetlen meccsfuttatásra.

### 3.3 Python adatpipeline

Felelőssége:

- XLSX beolvasás;
- exportprofilok;
- normalizálás;
- canonical értékek ellenőrzése;
- legacy alias és auditjelzések;
- runtime package build;
- diagnostics és build report;
- Godot consumption copy publikálása.

Fontos határ:

- az adatpipeline nem authoritative meccsállapot;
- a builder nem hajt végre játékszabályt;
- a runtime package generált programadat, nem szerkesztési forrás.

### 3.4 Runtime package

A runtime package a program által fogyasztható validált adatcsomag.

Jelenlegi fő fájlcsoport:

- `manifest.json`
- `cards.jsonl`
- `decks.jsonl`
- `lookups.json`
- `aliases.json`
- `ability_registry.json`
- `engine_support.json`
- `diagnostics.json`
- `build_report.md`

Felelőssége:

- kártyadefiníciók és paklik átadása;
- lookupok és támogatási információk átadása;
- Python és Godot közös programadat-határa.

Nem tartalmazza a futó meccs authoritative MatchState-jét.

### 3.5 Authoritative Python rules engine

Jelenlegi elsődleges szabálymotor:

- `Aeterna game engine/python/`

Felelőssége:

- meccsállapot létrehozása és védelme;
- state version kezelés;
- legal actionök előállítása;
- action request validálása;
- atomikus transitionök;
- typed eventek;
- state-invariánsok;
- player-visible és debug projection;
- determinisztikus AI-vs-AI futás.

A Python jelenlegi szerepe ezért már nem pusztán tooling vagy hipotetikus tesztréteg. Az új minimal rules engine ténylegesen működik, bár még nem teljes AETERNA motor.

### 3.6 MatchState és PlayerState

A MatchState a játék belső igaz állapota.

Jelenleg többek között kezeli:

- match identity;
- state version;
- aktív és priority player;
- minimal phase;
- event log;
- player state-ek;
- card instance registry;
- Domain topológiák;
- Domain occupancy state-ek.

A PlayerState jelenlegi instance-listás zónái:

- deck;
- hand;
- discard.

A következő bővítés:

- Wellspring instance-lista.

A MatchState soha nem exportálható közvetlenül normál játékosnak vagy UI-nak.

### 3.7 Card instance és object identity

A kártyadefiníció és a meccsbeli kártyapéldány külön objektum.

A card instance registry authoritative az alábbi adatokhoz:

- instance identity;
- Card_ID;
- owner;
- controller;
- zone;
- zone index;
- visibility;
- activity state;
- sequence adatok.

A konkrét Domain-pozíció nem a registry rekordban, hanem a Domain occupancy slotban található.

### 3.8 Zónák

Jelenlegi ismert zónák:

- deck;
- hand;
- discard;
- domain;
- wellspring.

A Wellspring jelenleg izolált contractként készült el; a production PlayerState-integráció a következő engine-lépés.

A zónatagság authoritative containere:

- listás zónáknál a PlayerState megfelelő ID-listája;
- Domainnál az occupancy slot;
- minden registry instance pontosan egy authoritative helyen szerepelhet.

### 3.9 Domain és board

A canonical alapjátékos topológia játékosonként:

- 6 Áramlat;
- Áramlatonként Horizont és Zenit;
- 6 kapcsolt Pecsét-pozíció.

A card occupancy:

- 12 slot játékosonként;
- Horizont és Zenit;
- egy slot legfeljebb egy card instance-et tartalmaz;
- a Pecsét nem card occupancy slot.

A player-visible board public projection.

### 3.10 Activity state

Canonical értékek:

- `active`
- `exhausted`
- `None`, ha az activity állapot az adott zónában nem alkalmazható.

A zone/activity kapcsolatot a card-instance validator és a state-invariáns védi.

Az activity state nem azonos:

- idézési betegséggel;
- támadási jogosultsággal;
- face-down állapottal;
- legal-action státusszal.

### 3.11 Resource réteg

A jelenlegi izolált Wellspring resource model:

- Magnitúdó = Ősforrás-lapok száma;
- elérhető Aura = Aktív Ősforrás-lapok száma;
- Kimerült forrás továbbra is növeli a Magnitúdót;
- typed Aura és payment még nincs implementálva.

A resource summary származtatott contract, nem külön authoritative számláló.

### 3.12 Legal action és structural option

A legal action réteg mondja meg, milyen döntést küldhet a játékos vagy AI.

Jelenleg működik a minimal legal-action alap és a külön structural Entity placement option contract.

A structural placement:

- nem teljes kijátszási legalitás;
- nem ellenőrzi a timingot, Magnitúdót, paymentet és entry state-et;
- nincs bekötve `play_card` actionként.

### 3.13 Action request és transition

A kliens vagy AI action requestet küld.

A rules engine:

1. ellenőrzi a match és state versiont;
2. ellenőrzi a játékost és actiont;
3. reject esetén nem mutál state-et;
4. siker esetén atomikus transitiont hajt végre;
5. növeli a state versiont;
6. typed eventet készít;
7. új projectiont adhat vissza.

Jelenlegi aktív actionök:

- `draw_card`
- `end_turn`

### 3.14 Eventrendszer

A snapshot az állapot, az event a történet.

Jelenlegi generic envelope:

- `minimal-engine-event-v0`

Aktív typed eventek:

- `zone_move`
- `turn_transition`

Az eventek szerepe:

- auditálhatóság;
- UI animáció;
- log és magyarázat;
- determinisztikus AI epizód;
- későbbi replay.

### 3.15 Projection és visibility

A projection-réteg a MatchState-ből nézőpontfüggő contractot készít.

Jelenlegi player snapshot:

- `engine-player-visible-snapshot-v2`

Jelenlegi szabályok:

- saját kéz látható;
- ellenfél kéz redacted és count-only;
- deck count-only;
- discard public;
- Domain board public;
- nincs teljes registry vagy MatchState export.

A Wellspring player-visible projection még nincs implementálva.

### 3.16 AI, trajectory és replay-alap

A minimal AI-vs-AI környezet ugyanazt az authoritative engine-utakat használja.

Aktív episode contract:

- `minimal-ai-vs-ai-episode-v1`

Fő elvek:

- determinisztikus actionválasztás;
- accepted és rejected step;
- player-visible observation;
- typed eventek;
- deep-copyzott trajectory;
- byte-szinten ismételhető JSON;
- replay-előkészítés, de még nem replay-végrehajtás.

### 3.17 Godot kliens- és debugréteg

A Godot jelenlegi bizonyított szerepe:

- runtime package loader;
- registry-k;
- sample és debug contractok;
- snapshot viewer;
- legal action debug panel;
- event log debug view;
- headless smoke testek.

Hosszú távú szerepe:

- játékos UI;
- tester/debug mód;
- action request beküldése;
- player-visible state és események megjelenítése.

A Godot nem authoritative szabálymotor és nem módosíthatja közvetlenül a MatchState-et.

### 3.18 Ability és effect engine

Az ability/effect engine még tervezett réteg.

Felelőssége később:

- trigger;
- condition;
- target selector;
- cost;
- effect;
- duration és limit;
- replacement és prevention;
- keyword support;
- kontrollált card-local fallback.

A természetes kártyaszöveg nem közvetlen runtime parser-forrás.

---

## 4. Authoritative adat- és vezérlési határok

### 4.1 Canonical szerkesztési adat

- Google Sheets / aktív XLSX.

### 4.2 Canonical programadat

- validált runtime package.

### 4.3 Canonical meccsállapot

- Python MatchState.

### 4.4 Canonical kártyapéldány

- card instance registry record és authoritative zónacontainer.

### 4.5 Canonical döntési felület

- engine által készített legal action vagy explicit precondition contract.

### 4.6 Canonical állapotváltozás

- rules engine transition.

### 4.7 Canonical történet

- typed event sequence.

### 4.8 Canonical játékosnézet

- player-visible snapshot és kapcsolódó public event projection.

---

## 5. Jelenlegi bizonyított állapot

A `84a7e8f4` bázisnál bizonyított:

- card instance-alapú MatchState;
- deck → hand draw transition;
- end-turn transition;
- typed event envelope;
- state version guard;
- Domain topológia és occupancy;
- public player-visible board;
- hidden-information snapshot;
- structural Entity placement options;
- activity state;
- izolált Wellspring resource contract;
- determinisztikus AI-vs-AI trajectory;
- 59 izolált Python tesztmodul és 333 zöld teszt.

Nem bizonyított még:

- Wellspring production integráció;
- Beáramlás;
- full timing és priority;
- Magnitúdó-preflight;
- Aura-payment;
- `play_card`;
- combat;
- ability execution;
- Pecsét és Aeternal teljes runtime modell;
- győzelmi feltétel;
- teljes emberi játékmenet.

---

## 6. Következő architekturális függőségi lánc

    Wellspring PlayerState-integráció
            ↓
    Player-visible Wellspring summary
            ↓
    Beáramlás precondition
            ↓
    Beáramlás transition + typed event
            ↓
    Magnitúdó-preflight
            ↓
    Aura-source selection + payment
            ↓
    Entity play precondition
            ↓
    play_card transition
            ↓
    Entity entry state
            ↓
    phase / priority / reaction rendszer
            ↓
    combat és győzelmi feltételek

A lánc későbbi eleme nem implementálható a korábbi authoritative réteg megkerülésével.

---

## 7. Technológiai döntés

A jelenlegi elfogadott irány:

- Python az authoritative rules engine és adatpipeline elsődleges nyelve;
- Godot/GDScript a kliens-, loader-, registry- és debugréteg;
- a két réteg explicit JSON/JSONL és action/snapshot/event contractokon keresztül kapcsolódik;
- nem tartunk fenn két külön authoritative szabálymotort.

A régi Python motor továbbra is reference/review forrás, nem a jelen engine automatikus backendje.

---

## 8. Nem cél a jelenlegi szakaszban

- teljes Godot-first rules runtime;
- két párhuzamos engine viselkedésének fenntartása;
- közvetlen UI state mutation;
- teljes `play_card` minden előfeltétel nélkül;
- minden kártyaképesség egyszerre;
- online PvP és szerverarchitektúra;
- collection, booster és gazdaság a stabil match engine előtt;
- nagy általános refaktor;
- régi engine automatikus migrációja.

---

## 9. Dokumentációs szerepek

- `CURRENT_ENGINE_CHECKPOINT.md`: mi működik most;
- `CURRENT_CONTRACT_STATUS.md`: mely contractok ténylegesen aktívak;
- `CURRENT_OPEN_QUESTIONS.md`: mely közeli döntési kapuk blokkolják a következő feladatokat;
- `CONTRACT_SPECIFICATION.md`: hosszú formájú contract-tervezési és háttérspecifikáció;
- `OPEN_QUESTIONS.md`: teljes történeti és hosszú távú kérdésregiszter;
- `RUNTIME_PACKAGE_SPECIFICATION.md`: package-adatmodell;
- `ABILITY_MODULE_SYSTEM.md`: későbbi effect engine;
- `checkpoints/CHECKPOINTS.md`: korábbi időrendi checkpointnapló.

---

## 10. Rövid architektúra-összefoglaló

**Authoritative rules engine:** Python  
**Authoritative match state:** MatchState  
**Programadat-forrás:** validált runtime package  
**Frontend:** Godot, később player UI  
**Döntési út:** legal action → action request → engine transition  
**Történeti út:** typed event sequence  
**Player output:** player-visible projection  
**AI output:** ugyanazon fair projection és legal action út  
**Következő architekturális feladat:** Wellspring production state-integráció
