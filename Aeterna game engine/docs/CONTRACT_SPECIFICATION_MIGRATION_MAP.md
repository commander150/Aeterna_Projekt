# AETERNA Game Engine – Contract Specification Migration Map

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-15  
**Státusz:** első contract-konszolidációs kör lezárva; történeti ellenőrzési és későbbi migration-reference  
**Technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum eredetileg a hosszú `CONTRACT_SPECIFICATION.md` és a működő Python engine eltéréseit térképezte fel.

Az első konszolidációs kör a `CONTRACT_SPECIFICATION.md` 1.1 verziójával lezárult. A korábbi részletes migration map és a régi contract-specifikáció a Git-történetben megmarad.

A jelen fájl feladata most:

- rögzíteni, mi került át az aktív specifikációba;
- megjelölni, mi maradt current státusz-, nyitott kérdés- vagy későbbi gameplay-téma;
- megakadályozni, hogy a régi sample mezőlisták újra aktív sémának tűnjenek;
- kijelölni, mikor szükséges újabb contract-migrációs kör.

Elsődleges aktív források:

1. működő kód és tesztek;
2. `CURRENT_CONTRACT_STATUS.md`;
3. `CURRENT_OPEN_QUESTIONS.md`;
4. `CONTRACT_SPECIFICATION.md`;
5. ez a migration reference;
6. történeti tervek és sample dokumentumok.

---

## 1. Első konszolidációs kör eredménye

### 1.1 Dokumentumstátusz és forráshierarchia

**Státusz:** `completed`

A contract-specifikáció most:

- explicit current státuszt tartalmaz;
- a működő kód és current dokumentumok elsőbbségét rögzíti;
- technológiafüggetlen;
- nem kezeli a Python–GDScript kettőst végleges architektúrának;
- a Python sidecar, C#, GDScript és más jelölteket ugyanazon contractjelentés alá rendeli.

### 1.2 Sample és aktív schema elhatárolása

**Státusz:** `completed`

A Godot sample snapshot, legal action és event fájlok:

- `debug_fixture` státuszt kaptak;
- parser-, loader- és UI-bizonyítékként megmaradnak;
- nem számítanak authoritative Python gameplay-sémának;
- nem törlendők automatikusan.

### 1.3 Aktív schema-index

**Státusz:** `completed`

Az aktív specifikáció külön indexeli:

- card instance v1;
- ObjectReference;
- ZoneMove;
- MatchState;
- Domain topology és occupancy;
- snapshot v2;
- public Domain board;
- minimal action request/response;
- typed engine eventek;
- AI episode v1;
- isolated placement és Wellspring contractok.

### 1.4 Card instance, activity és zónainvariáns

**Státusz:** `completed`

Beépült:

- owner/controller elhatárolás;
- zone/index és sequence;
- `active`, `exhausted`, illetve zónán kívüli `None` activity;
- listás zóna és registry konzisztencia;
- Domain occupancy cross-validation;
- activity nem azonos summoning sickness-szel.

### 1.5 Domain topology és projection

**Státusz:** `completed`

Beépült:

- játékosonként 6 Áramlat;
- horizon, zenith és statikus seal position;
- 12 foglalható slot;
- occupancy és registry kétirányú kapcsolat;
- public Domain board;
- structural placement és teljes play legality elhatárolása.

### 1.6 Snapshot és visibility

**Státusz:** `completed_first_pass`

Beépült:

- `engine-player-visible-snapshot-v2`;
- viewer-specifikus projection;
- saját kéz, ellenfél kéz, deck, discard és Domain visibility;
- fair AI ugyanazt a player-visible observationt használja;
- debug snapshot külön réteg;
- teljes MatchState és registry player-facing tiltása.

Későbbi migration:

- Wellspring summary;
- Pecsét állapot;
- pending decision;
- visible event window;
- spectator és replay projection.

### 1.7 Legal action, request és response

**Státusz:** `completed_first_pass`

Beépült:

- aktív minimal actionök: `draw_card`, `end_turn`;
- legal action engine-authority;
- minimal request;
- expected state version guard;
- rejected request mutationmentessége;
- current response szerepe;
- későbbi target-, choice-, payment- és reaction-payload elhatárolása.

Későbbi migration:

- Inflow action;
- `play_card`;
- payment;
- pending decision;
- combat és reaction.

### 1.8 Typed eventek

**Státusz:** `completed_first_pass`

Beépült:

- `minimal-engine-event-v0`;
- `zone_move`;
- `turn_transition`;
- generic `action_resolved` felváltása pontosabb typed eventtel;
- hidden-information-védett visible payload követelménye.

Későbbi migration:

- Inflow/Wellspring;
- activity change;
- payment;
- card played és entry;
- combat;
- Pecsét;
- victory;
- ability execution.

### 1.9 Wellspring és resource summary

**Státusz:** `completed_as_isolated_contract`

Beépült:

- `minimal-player-wellspring-state-v0`;
- `minimal-wellspring-resource-summary-v0`;
- `magnitude == wellspring_card_count`;
- `available_aura == active_source_count`;
- active + exhausted = total;
- integrált és isolated státusz elhatárolása.

Új Core-döntésként bekerült:

- a normál Beáramlással bekerülő lap Aktív;
- ugyanabban a körben Aura fizetésére használható;
- fizetéskor Kimerül.

A transition implementation továbbra is későbbi feladat.

### 1.10 AI és trajectory

**Státusz:** `completed_first_pass`

Beépült:

- `minimal-ai-vs-ai-episode-v1`;
- accepted/rejected step;
- player-visible observation;
- determinisztikus JSON;
- AI nem mutálhat state-et;
- `replay_ready: false` elhatárolás.

### 1.11 Diagnostics és validáció

**Státusz:** `completed_first_pass`

Beépült:

- strukturált validator result;
- builder/validator elhatárolás;
- deep-copy és inputváltozatlanság;
- determinisztikus sorrend;
- hidden-information audit;
- severity és blocking elvi szétválasztása;
- player-facing és developer diagnostics elhatárolása.

Egyetlen globális diagnostics schema továbbra sem kötelező, amíg a külön contractok következetes strukturált hibát adnak.

### 1.12 Ability registry és support

**Státusz:** `completed_as_foundation`

Beépült:

- ability registry nem executor;
- 2 modul `declared_only`;
- kártyák supportja `not_evaluated`;
- `runtime_executes_abilities: false`;
- card-local fallback átmeneti és diagnosztizált lehet csak;
- ability executor az alap gameplay-contractok után következhet.

---

## 2. Felváltott vagy történeti elemek

### 2.1 Snapshot v1

- `engine-player-visible-snapshot-v1`;
- `superseded`;
- felváltotta a v2 public Domain boarddal.

### 2.2 Card instance v0

- `minimal-card-instance-record-v0`;
- `superseded`;
- felváltotta a v1 activity state-tel.

### 2.3 Régi sample mezőlisták

- nem canonical field listák;
- nem minden mező közös vagy kötelező;
- csak történeti tervezési jelöltek és debug fixture-ek.

### 2.4 Python–GDScript kettős engine-feltételezés

- felváltotta a runtime-nyelvi döntési kapu;
- kötelező fő proof: Python sidecar és Godot .NET/C#;
- GDScript vagy más nyelv csak indokolt további proof;
- két teljes authoritative motor tartós párhuzamos fenntartása kerülendő.

---

## 3. Továbbra is nyitott vagy későbbi contract-kapuk

### 3.1 Runtime-nyelvi kapu

- `fourth turn` audit;
- comparison fixture;
- Python sidecar proof;
- C# proof;
- packaging és stabilitás;
- emberi döntés.

### 3.2 Wellspring és Beáramlás

- PlayerState/MatchState integráció;
- player-visible summary;
- Inflow precondition;
- transition és event;
- per-turn usage;
- visibility policy.

### 3.3 Magnitúdó, Aura és payment

- canonical Aura LOOKUPS mapping;
- preflight result;
- source selection;
- atomic payment;
- activity event;
- temporary Aura és kivételek.

### 3.4 `play_card`

- timing és priority;
- Magnitúdó és payment;
- placement/target/choice;
- atomic transition;
- card played és entry event;
- structured rejection.

### 3.5 Reaction, combat és ability

- pending decision;
- queue/stack/chain;
- Burst és Jel reaction;
- attack/block/damage;
- Pecsét és victory;
- trigger/condition/cost/target/choice/effect.

### 3.6 Replay és spectator

- action history;
- snapshot checkpoint;
- deterministic reconstruction;
- event visibility;
- spectator policy.

Ezek részletes döntéseinek aktív helye a `CURRENT_OPEN_QUESTIONS.md`.

---

## 4. Mikor kell új migration-kör?

Új contract-specifikációs migration szükséges, ha:

- a runtime-nyelvi kapu lezárul és új product runtime kerül kiválasztásra;
- Wellspring és Beáramlás production integráció elkészül;
- a snapshot új főverziót kap;
- `play_card`, payment vagy pending decision aktívvá válik;
- combat vagy reaction layer elkészül;
- ability executor MVP elkészül;
- replay/spectator contract aktívvá válik;
- current kód és specifikáció között jelentős eltérés keletkezik.

A migration során továbbra is tilos:

- dokumentációból runtime-sémát megváltoztatni;
- javasolt mezőt implementáció nélkül kötelezővé tenni;
- sample fixture-t production contractnak nevezni;
- teljes MatchState-et player snapshotként kezelni;
- isolated helpert integrált gameplayként leírni;
- nyitott kérdést elveszíteni.

---

## 5. Rövid lezárás

**Első konszolidáció:** lezárva.  
**Aktív főspecifikáció:** `CONTRACT_SPECIFICATION.md` 1.1.  
**Aktuális implementációs státusz:** `CURRENT_CONTRACT_STATUS.md`.  
**Nyitott döntések:** `CURRENT_OPEN_QUESTIONS.md`.  
**Történeti részletes eltéréstérkép:** Git-történetben megőrizve.  
**Következő migration:** csak új működő contract-réteg vagy lezárt runtime-döntés után.