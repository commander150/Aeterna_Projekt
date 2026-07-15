# AETERNA Game Engine

## Projektstátusz

Az **AETERNA Game Engine** az AETERNA kártyajáték contract-first digitális programegysége.

A jelenlegi működő authoritative referenciaimplementáció:

> **a determinisztikus, headless és tesztelhető Python minimal rules engine.**

A végleges termékruntime nyelve és futási modellje még nincs kiválasztva.

A következő elsődleges Codex-prioritás:

> **Python sidecar + Godot és Godot .NET/C# authoritative runtime összehasonlító proof.**

Szükség esetén egy szűk GDScript transition proof is készülhet. Embedded Python jelenleg kutatási, későbbi irány.

A jelentős gameplay-engine bővítés a runtime-nyelvi döntési kapu után folytatódik.

---

## Aktuális technikai bázis

**Báziscommit:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`  
**Commitüzenet:** `Add minimal Wellspring resource contracts`  
**Aktuális checkpoint:** `docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`  
**Runtime-nyelvi döntési kapu:** `docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

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
- a Godot .NET/C# rules runtime karbantarthatóságát;
- a C# portolási költséget;
- azt, hogy a végleges runtime biztosan Python, C# vagy GDScript lesz.

---

## Fő mappaszerkezet

### `python/`

Jelenlegi aktív szerepei:

- minimal rules-engine referencia;
- state és transition logika;
- contract helperek;
- invariánsok;
- player-visible és debug projection;
- AI-vs-AI headless tesztelés;
- runtime package tooling;
- XLSX export és validáció;
- unit, integration és smoke tesztek.

A Python réteg a végleges termékruntime döntéstől függetlenül megtarthatja:

- adatpipeline;
- AI/batch;
- differential testing;
- diagnostics;
- balansz- és kutatási tooling szerepét.

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
- Godot nem olvas közvetlenül XLSX-et;
- C# runtime esetén is elkülönített rules library szükséges.

### `docs/`

Fő aktuális dokumentumok:

- `docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `docs/TECHNOLOGY_DECISIONS.md`
- `docs/DECISION_MAP.md`
- `docs/CURRENT_PROTOTYPE_STATUS.md`
- `docs/CURRENT_CONTRACT_STATUS.md`
- `docs/CURRENT_RUNTIME_PACKAGE_STATUS.md`
- `docs/CURRENT_OPEN_QUESTIONS.md`
- `docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`
- `docs/ARCHITECTURE.md`

Az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó.

---

## Runtime engine language decision gate

### Python sidecar + Godot

Vizsgálandó:

- stdin/stdout JSONL;
- localhost TCP + JSON;
- handshake;
- action request/response;
- state/version guard;
- process lifecycle;
- kontrollált shutdown;
- crash és version mismatch;
- Windows packaging.

### Godot .NET/C# authoritative runtime

Vizsgálandó:

- UI-tól független C# rules library;
- ugyanazon comparison scenario;
- kompatibilis JSON-contract;
- unit tesztek;
- Godot .NET integráció;
- Windows export;
- Python reference outputtal való differential comparison;
- emberi karbantarthatóság és portolási költség.

### Minimal GDScript proof

Csak akkor készül, ha:

- a tanulóprogram-audit indokolja;
- az első két proof nem ad elég döntési információt;
- egyetlen transitionre korlátozható.

### Embedded Python

Közösségi GDExtension/binding irányok léteznek, de jelenleg nem ez az első AETERNA proof.

Részletes scope:

- `docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

---

## Tanulóprogramok

A felhasználó által letöltött külső tanulóprogramok szándékosan nincsenek az AETERNA GitHub repositoryban licencbiztonsági okból.

A következő Codex-audit helyileg vizsgálja:

- forrást és verziót;
- licencet;
- Python/C#/GDScript szerepet;
- Godot-verziót;
- state authorityt;
- bridge-et;
- process lifecycle-t;
- packaginget;
- Windows támogatást;
- teszteket;
- clean-room módon használható mintákat;
- attributionkövetelményt.

---

## Authoritative állapotmodell

A jelenlegi Python reference futásban a MatchState az authoritative belső állapot.

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

Döntés utáni első bővítés:

- `wellspring_card_instance_ids`

A contract jelentése a későbbi C# vagy más runtime-ban is megőrzendő.

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

Ezek a comparison scenario kötelező elemei.

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

A Wellspring production integráció a runtime-nyelvi döntési kapu utáni első gameplay-feladat.

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

A comparison proof követelményei:

- közös scenario;
- canonical JSON;
- stale state rejection;
- Python reference output;
- C# unit tesztek;
- bridge lifecycle tesztek;
- structured differential report;
- Windows launch proof.

---

## Gameplay-engine queue a döntés után

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

---

## Codex nélküli aktív munkasáv

1. `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` közös triázsa.
2. Tanulóprogram-forrás- és licencleltár előkészítése.
3. Comparison kritériumok pontosítása.
4. `ABILITY_MODULE_SYSTEM.md` auditja.
5. Contract-specifikáció konszolidációja.
6. Hivatalos szabályforrásból megválaszolható kérdések ellenőrzése.

---

## Rövid összefoglaló

**Működő referencia:** Python minimal rules engine  
**Következő Codex-prioritás:** Python sidecar vs Godot .NET/C# comparison  
**Godot:** loader-, registry-, debug- és későbbi kliensréteg  
**Opcionális proof:** minimal GDScript transition  
**Embedded Python:** kutatási, későbbi irány  
**Végleges runtime-technológia:** még nyitott  
**Báziscommit:** `84a7e8f4`  
**Gameplay queue első eleme a döntés után:** Wellspring runtime integráció  
**Codex nélküli aktív sáv:** dokumentáció, audit és döntés-előkészítés
