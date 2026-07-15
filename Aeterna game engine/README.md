# AETERNA Game Engine

## Projektstátusz

Az **AETERNA Game Engine** az AETERNA kártyajáték új, contract-first digitális programegysége.

A jelenlegi elsődleges technikai cél:

> **egy determinisztikus, headless, tesztelhető és fokozatosan szabályhűvé bővíthető Python rules engine létrehozása.**

A Godot ág aktív, de jelenleg elsősorban:

- runtime package fogyasztó;
- registry- és debugréteg;
- későbbi player UI és kliens alapja.

Az authoritative szabálylogika jelenlegi helye a Python engine.

---

## Aktuális technikai bázis

**Báziscommit:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`  
**Commitüzenet:** `Add minimal Wellspring resource contracts`  
**Aktuális checkpoint:** `docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

A jelenlegi engine már tartalmaz:

- minimal MatchState-et és PlayerState-et;
- state version guardot;
- action request és response alapot;
- legal action alapot;
- card instance registryt;
- deck, hand és discard instance-listákat;
- draw és end-turn transitiont;
- generic event envelope-ot;
- typed ZoneMove és TurnTransition eventet;
- state invariant rendszert;
- canonical AI episode trajectoryt;
- player-visible snapshot v2-t;
- hidden-information projekciót;
- Domain topológiát és occupancyt;
- public board projectiont;
- structural Entity placement option contractot;
- card instance Aktív/Kimerült állapotot;
- izolált Wellspring state és resource summary contractot.

Aktív minimal actionök:

- `draw_card`
- `end_turn`

---

## Mit nem bizonyít még a jelenlegi engine?

Még nincs runtime gameplayként:

- Wellspring PlayerState- és MatchState-integráció;
- Beáramlás;
- Magnitúdó-precondition;
- Aura-payment;
- typed Aura;
- `play_card`;
- Entitás actionön keresztüli Domainba helyezése;
- teljes phase és priority rendszer;
- reakciós ablakok;
- Burst-rendszer;
- activity mutation action;
- idézési betegség;
- támadás és blokkolás;
- sebzés és HP;
- Pecsét- és Aeternal-state;
- ability executor;
- teljes target legality;
- győzelmi és vereségi feltételek;
- replay-végrehajtás;
- emberi játékmenet;
- végleges UI.

---

## Fő mappaszerkezet

### `python/`

Az aktív Python oldal fő feladatai:

- authoritative rules engine;
- state és transition logika;
- contract helperek;
- invariánsok;
- player-visible és debug projection;
- AI-vs-AI headless tesztelés;
- runtime package tooling;
- XLSX export és validáció;
- unit, integration és smoke tesztek.

Fontosabb területek:

- `python/engine/`
- `python/tools/ai_vs_ai/`
- `python/tools/engine/`
- `python/tools/runtime_package/`
- `python/tools/xlsx_export/`
- `python/tests/`

### `Godot/`

A Godot ág feladata:

- runtime package betöltés;
- registry-k;
- sample és debug contractok fogyasztása;
- snapshot, legal action és event log debug nézetek;
- headless Godot smoke tesztek;
- későbbi játékos UI.

A Godot nem olvas közvetlenül XLSX-et és nem canonical szabályforrás.

### `docs/`

A dokumentációs ág feladata:

- architektúra;
- aktuális contract-státusz;
- runtime package;
- technológiai döntések;
- nyitott kérdések;
- mérföldkövek;
- checkpointok;
- folytatási pontok.

---

## Authoritative állapotmodell

### MatchState

A MatchState jelenleg kezeli többek között:

- match ID;
- state version;
- aktív játékos;
- priority player;
- minimal phase;
- event log;
- player state-ek;
- card instance registry;
- Domain topológiák;
- Domain occupancy state-ek.

A Wellspring még nem production MatchState-réteg.

### PlayerState

Jelenlegi instance-listás zónák:

- `deck_card_instance_ids`
- `hand_card_instance_ids`
- `discard_card_instance_ids`

Következő bővítés:

- `wellspring_card_instance_ids`

### Card instance record

Aktív schema:

- `minimal-card-instance-record-v1`

Támogatott activity értékek:

- `None`
- `active`
- `exhausted`

Canonical activity kapcsolat:

- deck → `None`
- hand → `None`
- discard → `None`
- domain → `active` vagy `exhausted`
- wellspring → `active` vagy `exhausted`

Canonical visibility:

- Wellspring → `owner_only`
- Domain → `public`

---

## Eventrendszer

Generic event schema:

- `minimal-engine-event-v0`

Aktív typed eventek:

- `zone_move`
- `turn_transition`

A jelenlegi eventrendszer determinisztikus sequence-et használ.

Player-facing projection nem kap teljes debug payloadot.

---

## Domain board

Játékosonként:

- 6 Áramlat;
- 6 Horizont-pozíció;
- 6 Zenit-pozíció;
- 6 Pecsét-pozíció;
- 12 card occupancy slot.

Az occupancy és a card instance registry kapcsolata kétirányú invariánssal védett.

A player-visible board:

- mindkét játékos Domainját public adatként mutatja;
- üres és foglalt slotot jelenít meg;
- occupied slotban canonical ObjectReference-et használ;
- nem exportál teljes topológiát, occupancyt vagy registryt.

---

## Player-visible snapshot

Aktív schema:

- `engine-player-visible-snapshot-v2`

Jelenlegi visibility-policy:

- saját kéz owner-visible;
- ellenfél kéz count-only és redacted;
- deck count-only;
- discard public;
- Domain board public.

A Wellspring még nincs a snapshotba integrálva.

---

## Structural Entity placement

Aktív model:

- `structural-entity-domain-placement-v0`

Eligible Entitás instance esetén:

- saját kéz szükséges;
- controller-egyezés szükséges;
- canonical runtime card type `entity`;
- 12 saját Horizont/Zenit target option készül;
- foglalt target megmarad, de strukturálisan unavailable.

A helper nem ellenőrzi:

- timingot;
- priorityt;
- Magnitúdót;
- Aura-paymentet;
- card-text restrictiont;
- entry state-et.

Ez nem teljes play legality és nincs bekötve a legal action listába.

---

## Wellspring resource contract

Aktív state schema:

- `minimal-player-wellspring-state-v0`

Aktív summary schema:

- `minimal-wellspring-resource-summary-v0`

Resource model:

- `base-wellspring-count-and-activity-v0`

Canonical összefüggések:

- `magnitude == wellspring_card_count`
- `available_aura == active_source_count`
- `active_source_count + exhausted_source_count == wellspring_card_count`

A Kimerült Ősforrás-lap:

- beleszámít a Magnitúdóba;
- nem biztosít elérhető Aurát.

Még nincs:

- typed Aura;
- payment;
- Rezonancia;
- temporary Aura;
- Aura-égés;
- MatchState-integráció;
- Beáramlás.

---

## AI-vs-AI és trajectory

Aktív episode contract:

- `minimal-ai-vs-ai-episode-v1`

A trajectory:

- accepted és rejected stepeket kezel;
- canonical player-visible observationre épül;
- deep-copy biztonságos;
- determinisztikus JSON-t ad;
- replay-alapot készít elő;
- jelenleg `replay_ready: false`.

A jelenlegi bot még nem teljes AETERNA-játékos AI.

---

## Tesztelés

A `84a7e8f4` bázisnál:

- 59 Python tesztmodul izolált futása zöld;
- 333 izolált teszt zöld;
- minimal engine JSON smoke zöld;
- AI-vs-AI text és JSON smoke zöld;
- két azonos AI JSON-futás byte-szinten azonos.

Ismert monolitikus discovery-problémák:

- `test_finds_xlsx_files_only_in_source_directory`
- `test_lists_sheets_in_read_only_data_only_mode`

Ezek sorrendfüggő XLSX mock-problémák, külön tesztinfrastruktúra-feladatként kezelendők.

---

## Futtatási példák

A parancsokat az `Aeterna game engine/python/` mappából kell futtatni.

Minimal engine smoke:

    python tools/engine/run_minimal_engine_smoke.py --json-debug-export

AI-vs-AI text smoke:

    python tools/ai_vs_ai/run_minimal_ai_vs_ai_episode.py --max-steps 8

AI-vs-AI JSON smoke:

    python tools/ai_vs_ai/run_minimal_ai_vs_ai_episode.py --max-steps 8 --json

Teljes unittest discovery:

    python -m unittest discover

Az összes tesztmodul külön folyamatban történő futtatása is kötelező, mert a monolitikus discoveryben jelenleg két ismert mock-sorrendhiba van.

---

## Runtime package és publish pipeline

Elsődleges publish runner:

- `python/publish_runtime_package_to_godot.bat`

Fontos elvek:

- Godot nem olvas közvetlenül XLSX-et;
- Godot csak validált runtime package-et fogyaszt;
- kártyák és decklisták az aktív 1.9v kártyaadatbázisból jönnek;
- runtime lookupok a `LOOKUPS.xlsx` fájlból jönnek;
- generált package nem canonical szerkesztési forrás.

---

## Következő programozási lépés

Következő biztonságos feladat:

> **az izolált Wellspring contract integrálása a PlayerState és MatchState production állapotába.**

Várt bővítés:

- `wellspring_card_instance_ids`;
- üres initial Wellspring;
- authoritative zónatagság;
- registry cross-validation;
- zone index;
- `owner_only` visibility;
- active/exhausted activity;
- resource summary elérés.

Ebben a következő lépésben még ne készüljön:

- Beáramlás action;
- hand → Wellspring transition;
- Aura-payment;
- player-visible Wellspring projection;
- új event;
- `play_card`.

---

## Következő függőségi lánc

1. Wellspring MatchState-integráció;
2. player-visible Wellspring summary;
3. Beáramlás precondition;
4. Beáramlás transition és typed event;
5. Magnitúdó-preflight;
6. Aura-source és payment contract;
7. activity mutation;
8. Entity play precondition;
9. `play_card`;
10. hand → Domain transition;
11. entry-state;
12. teljesebb phase és priority.

---

## Fő dokumentumok

### Aktuális állapot és irány

- `../Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`
- `../Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`
- `docs/AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`
- `docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`
- `docs/ARCHITECTURE.md`
- `docs/CURRENT_CONTRACT_STATUS.md`
- `docs/CURRENT_OPEN_QUESTIONS.md`

### Hosszú formájú háttérdokumentumok

- `docs/checkpoints/CHECKPOINTS.md`
- `docs/OPEN_QUESTIONS.md`
- `docs/DECISION_MAP.md`
- `docs/TECHNOLOGY_DECISIONS.md`
- `docs/CONTRACT_SPECIFICATION.md`
- `docs/RUNTIME_PACKAGE_SPECIFICATION.md`
- `docs/ABILITY_MODULE_SYSTEM.md`
- `docs/PROTOTYPE_PLANS.md`

A hosszú formájú dokumentumok egy része történeti vagy tervezett elemeket is tartalmaz. Az aktuális megvalósításnál a current dokumentumok az elsődleges státuszforrások.

---

## Rövid összefoglaló

**Elsődleges engine:** Python rules engine  
**Godot:** fogyasztói és későbbi kliensréteg  
**Báziscommit:** `84a7e8f4`  
**Aktív actionök:** `draw_card`, `end_turn`  
**Aktív eventek:** `zone_move`, `turn_transition`  
**Player snapshot:** v2, public Domain boarddal  
**Card instance schema:** v1, activity state-tel  
**Wellspring:** izolált state és summary kész  
**Következő feladat:** Wellspring runtime integráció  
**Tesztállapot:** 59 modul, 333 izolált zöld teszt  
**Ismert tesztprobléma:** két sorrendfüggő XLSX mock-eltérés
