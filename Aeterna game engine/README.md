# AETERNA Game Engine

## Projektstátusz

Az **AETERNA Game Engine** az AETERNA kártyajáték új, contract-first digitális programegysége.

A jelenlegi elsődleges technikai cél:

> **egy determinisztikus, headless, tesztelhető és fokozatosan szabályhűvé bővíthető Python minimal rules engine fejlesztése.**

Fontos elhatárolás:

- a Python engine a jelenlegi működő és tesztelt authoritative fejlesztési bázis;
- a Godot ág működő loader-, registry-, debug- és későbbi UI-alap;
- a Python backend + Godot frontend a legerősebb hosszú távú jelölt;
- a végleges runtime/backend, bridge és packaging architektúra még nyitott technológiai kapu;
- a tanulóprogram-audit és a Python–GDScript comparison továbbra is szükséges vizsgálat.

A jelenlegi munkairány tehát nem azonos a végleges termékarchitektúra visszavonhatatlan lezárásával.

---

## Aktuális technikai bázis

**Báziscommit:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`  
**Commitüzenet:** `Add minimal Wellspring resource contracts`  
**Aktuális checkpoint:** `docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

A jelenlegi Python engine tartalmaz:

- MatchState-et és PlayerState-et;
- state version guardot;
- action request és response alapot;
- legal action alapot;
- card instance registryt;
- deck, hand és discard instance-listákat;
- draw és end-turn transitiont;
- generic event envelope-ot;
- typed `zone_move` és `turn_transition` eventet;
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
- harc;
- ability executor;
- Pecsét- és Aeternal-state;
- győzelmi és vereségi feltételek;
- replay-végrehajtás;
- emberi játékmenet;
- végleges UI.

A jelenlegi rendszer továbbá még nem bizonyítja:

- a Python engine és Godot kliens végleges összekapcsolását;
- a Python runtime Windows-csomagolását;
- a process lifecycle és crash recovery működését;
- azt, hogy a végleges runtime biztosan kizárólag külön Python backend lesz;
- a GDScript runtime-alkalmasság végleges elutasítását.

---

## Fő mappaszerkezet

### `python/`

Jelenlegi aktív szerepei:

- minimal rules engine;
- state és transition logika;
- contract helperek;
- invariánsok;
- player-visible és debug projection;
- AI-vs-AI headless tesztelés;
- runtime package tooling;
- XLSX export és validáció;
- unit, integration és smoke tesztek.

### `Godot/`

Bizonyított szerepei:

- runtime package betöltés;
- registryk;
- sample és debug contractok fogyasztása;
- snapshot, legal action és event log debug nézetek;
- unified dashboard;
- headless Godot smoke tesztek;
- későbbi játékos UI alapja.

Biztos korlát:

- a Godot UI nem lehet rejtett szabályforrás;
- a kliens nem módosíthat authoritative state-et;
- Godot nem olvas közvetlenül XLSX-et.

Nyitott technológiai kérdés:

- a végleges rules runtime Pythonban, GDScriptben vagy pontosan meghatározott hibrid modellben működik-e.

### `docs/`

Fő aktuális dokumentumok:

- `docs/ARCHITECTURE.md`
- `docs/TECHNOLOGY_DECISIONS.md`
- `docs/DECISION_MAP.md`
- `docs/CURRENT_CONTRACT_STATUS.md`
- `docs/CURRENT_RUNTIME_PACKAGE_STATUS.md`
- `docs/CURRENT_PROTOTYPE_STATUS.md`
- `docs/CURRENT_OPEN_QUESTIONS.md`
- `docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

Az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó.

---

## Authoritative állapotmodell

A jelenlegi Python futásban a MatchState az authoritative belső állapot.

Jelenleg kezeli többek között:

- match ID;
- state version;
- aktív és priority player;
- minimal phase;
- event log;
- player state-ek;
- card instance registry;
- Domain topológiák;
- Domain occupancy state-ek.

PlayerState listás zónák:

- `deck_card_instance_ids`
- `hand_card_instance_ids`
- `discard_card_instance_ids`

Következő bővítés:

- `wellspring_card_instance_ids`

Ez az authority a jelenlegi Python engine-futásra vonatkozó tényleges állapotmodell. A végleges termékprocessz helye és bridge-e még nyitott.

---

## Card instance és activity state

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

A rendszer determinisztikus sequence-et használ, és a player-facing projection nem kap teljes debug payloadot.

---

## Domain board és snapshot

Játékosonként:

- 6 Áramlat;
- 6 Horizont;
- 6 Zenit;
- 6 Pecsét-pozíció;
- 12 card occupancy slot.

Aktív player snapshot:

- `engine-player-visible-snapshot-v2`

Visibility-policy:

- saját kéz owner-visible;
- ellenfél kéz redacted és count-only;
- deck count-only;
- discard public;
- Domain board public;
- Wellspring még nincs projektálva.

---

## Wellspring resource contract

Aktív izolált sémák:

- `minimal-player-wellspring-state-v0`
- `minimal-wellspring-resource-summary-v0`

Canonical összefüggések:

- `magnitude == wellspring_card_count`
- `available_aura == active_source_count`
- active + exhausted = total count

Még nincs:

- MatchState-integráció;
- typed Aura;
- payment;
- Rezonancia;
- Beáramlás.

---

## AI-vs-AI és tesztelés

Aktív episode contract:

- `minimal-ai-vs-ai-episode-v1`

A `84a7e8f4` bázisnál:

- 59 Python tesztmodul izolált futása zöld;
- 333 izolált teszt zöld;
- minimal engine JSON smoke zöld;
- AI-vs-AI text és JSON smoke zöld;
- két azonos AI JSON-futás byte-szinten azonos.

Ismert monolitikus discovery-problémák:

- `test_finds_xlsx_files_only_in_source_directory`
- `test_lists_sheets_in_read_only_data_only_mode`

---

## Következő programozási lánc

1. Wellspring MatchState-integráció.
2. Player-visible Wellspring summary.
3. Beáramlás precondition.
4. Beáramlás transition és typed event.
5. Magnitúdó-preflight.
6. Aura-source és payment contract.
7. Activity mutation.
8. Entity play precondition.
9. `play_card`.
10. Hand → Domain transition.
11. Entry-state.
12. Teljesebb phase és priority.

Ez a belső engine-lánc a végleges bridge-döntés előtt is biztonságosan folytatható.

---

## Párhuzamos technológiai vizsgálat

1. `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` közös triázsa.
2. Tanulóprogram-forrásleltár.
3. Python-engine/Godot minták auditja.
4. Python–GDScript comparison scope.
5. Minimal Python–Godot bridge prototype.
6. Szükség esetén minimal GDScript rules proof.
7. Windows packaging prototype.
8. Végleges product runtime-döntés.

---

## Rövid összefoglaló

**Jelenlegi működő engine:** Python minimal rules engine  
**Godot:** loader-, registry-, debug- és későbbi kliensréteg  
**Legerősebb hosszú távú jelölt:** Python backend + Godot frontend  
**Végleges runtime-technológia:** még nyitott  
**Tanulóprogram-audit:** szükséges  
**Python–GDScript comparison:** nyitott technológiai kapu  
**Báziscommit:** `84a7e8f4`  
**Következő engine-feladat:** Wellspring runtime integráció
