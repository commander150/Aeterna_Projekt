# AETERNA Game Engine – Contract Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2\
**Dátum:** 2026-07-22\
**Státusz:** aktív megvalósítási contract-státusz  
**Felváltott fájl:** `CURRENT_CONTRACT_STATUS.md`  
**Aktuális repository-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`

Ez a dokumentum röviden rögzíti:

- mely contractok léteznek ténylegesen a Python referenciaengine-ben;
- mely contractokat bizonyított a C# minimal runtime candidate;
- mely contractok aktívak a production C# foundationben;
- mi aktív, izolált, tervezett, felváltott vagy csak debug-fixture;
- hol van eltérés a hosszú contract-specifikáció és a tényleges implementáció között.

Ez a dokumentum nem helyettesíti:

- `CONTRACT_SPECIFICATION.md` – technológiafüggetlen szerkezeti specifikáció;
- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md` – történeti konszolidációs és migrációs referencia;
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md` – a runtime-jelöltek közös comparison fixture-je;
- `RUNTIME_PACKAGE_SPECIFICATION.md` – statikus package-contract.

Kapcsolódó aktív dokumentumok:

- `CONTRACT_SPECIFICATION.md`
- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`
- `RUNTIME_PACKAGE_STATUS.md`
- `PROTOTYPE_STATUS.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `ARCHITECTURE.md`
- `checkpoints/ENGINE_CHECKPOINT.md`

---

## 1. Státuszjelölések

| Státusz | Jelentés |
|---|---|
| `ACTIVE_REFERENCE_RUNTIME` | A Python referenciaengine ténylegesen használja. |
| `ACTIVE_REFERENCE_PROJECTION` | A Python referencia player-facing vagy debug projekciója használja. |
| `PROVEN_CSHARP_CANDIDATE` | A minimal C# candidate proofban ténylegesen működik és tesztelt. |
| `ACTIVE_ISOLATED` | Megvalósított és tesztelt helper vagy contract, de nincs teljes runtime-integrációban. |
| `FOUNDATION_ONLY` | Alapcontract létezik, a teljes gameplay-lánc még hiányzik. |
| `ACTIVE_PRODUCTION_FOUNDATION` | A production C# foundationben implementált és tesztelt. |
| `PLANNED_GAMEPLAY` | Későbbi production gameplay-szakasz része. |
| `SUPERSEDED` | Korábbi séma vagy modell, amelyet újabb aktív változat felváltott. |
| `DEBUG_FIXTURE` | Parser-, loader-, UI- vagy comparison-tesztadat; nem production gameplay-contract. |
| `REFERENCE_ONLY` | Összehasonlítási vagy történeti contract, production authority nélkül. |

Fontos elhatárolás:

- a Python contract aktív lehet a referenciaengine-ben anélkül, hogy production C# contract lenne;
- a C# candidate proofban használt fixture-specifikus contract nem válik automatikusan production API-vá;
- a C.5B contractok a `931bf5571d541c752aa421a9f0626768bd8ffbe7` commit és tesztlánca alapján aktív production foundation státuszt kaptak;
- ez nem jelenti a Wellspring, Beáramlás, payment, `play_card`, combat vagy ability contractok elkészültét.

---

## 2. Authority és runtime-határ

### 2.1 Elfogadott production authority

A production authoritative runtime:

- C#/.NET.

A Godot/GDScript:

- vizuális kliens;
- action requestet készít;
- snapshotot, legal actiont, response-t és eventet jelenít meg.

A Python:

- referencia;
- fixture- és tesztforrás;
- AI-, batch- és audittooling;
- nem második production authority.

### 2.2 Production contract authority-kapu

Production state mutation csak validált C# engine transitionön keresztül történhet.

Aktív publikus belépési pontok:

- `CreateMatch`;
- `GetPlayerSnapshot`;
- `ListLegalActions`;
- `SubmitAction`;
- `GetEvents(string viewerPlayerId, int afterSequence = 0)`;
- `GetMatchResult`.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

A publikus eventfelület viewer-specifikus és redaktált. A teljes event- és debugállapot internal, kizárólag a Headless/Tests friend assemblyk számára érhető el; a Godot production bridge ezt nem exportálja.

Draw eventnél a tulajdonos nézete megkaphatja a `card_instance_id` és `card_id` értéket; az ellenfél projekciója csak a megengedett zóna- és számlálóváltozást tartalmazza, rejtett kártyaazonosító nélkül.

Null, hiányos vagy malformed create/action JSON stabil, strukturált rejectiont vagy diagnosticot ad. Nyers JSON-, null-reference- vagy argument-null kivétel nem hagyhatja el a production JSON-határt.

---

## 3. Card instance és belső state contractok

### 3.1 Card instance record v1

Schema:

- `minimal-card-instance-record-v1`

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

Fő mezők:

- `card_instance_id`;
- `card_id`;
- `owner_player_id`;
- `controller_player_id`;
- `zone`;
- `zone_index`;
- `visibility`;
- `created_sequence`;
- `zone_sequence`;
- `activity_state`;
- `metadata`.

Támogatott activity értékek:

- `None`;
- `active`;
- `exhausted`.

Jelenlegi Python zone/activity szabály:

- deck, hand, discard → `None`;
- domain, wellspring → `active` vagy `exhausted`.

Production C# státusz:

- a C.5B minimum modell és jelentése aktív;
- a Python dict-schema nem kötelező C# belső objektumforma;
- typed immutable vagy kontrollált mutable C# belső modell szükséges.

**Státusz:** `FOUNDATION_ONLY`

### 3.2 ObjectReference

Schema:

- `minimal-object-reference-v0`

Python státusz:

- `ACTIVE_REFERENCE_PROJECTION`

Szerep:

- rövid, biztonságos card instance hivatkozás;
- nem teljes card instance dump;
- hidden-information-védett contract.

Production C# státusz:

- typed `CardReference` projection contractként aktív a player snapshotban.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 3.3 ZoneMove

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

Aktív referenciahasználat:

- draw: deck → hand.

Későbbi használat:

- hand → Wellspring;
- hand → Domain;
- Domain → discard;
- más zónamozgások.

C# candidate:

- a comparison fixture draw-láncában bizonyított.

**Státusz:** `PROVEN_CSHARP_CANDIDATE`

Production C#:

- draw transition és typed `zone_move` event alapként aktív.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 3.4 MatchState

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

Jelenlegi fő rétegek:

- player state-ek;
- card instance registry;
- state version;
- aktív és priority player;
- minimal phase;
- event log;
- Domain topológiák;
- Domain occupancy state-ek.

C# candidate:

- fixture-specifikus minimal state és projection bizonyított.

Production C#:

- aktív egyetlen authoritative MatchState;
- publikus hívó számára nem adható ki módosítható referenciaként.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 3.5 PlayerState zónalisták

Python referencia:

- deck: `ACTIVE_REFERENCE_RUNTIME`;
- hand: `ACTIVE_REFERENCE_RUNTIME`;
- discard: `ACTIVE_REFERENCE_RUNTIME`;
- Wellspring: `ACTIVE_ISOLATED`.

Production C# C.5B:

- deck;
- hand;
- discard.

Későbbi gameplay:

- Wellspring;
- Domain occupancy kapcsolatok;
- további zónák.

---

## 4. Domain contractok

### 4.1 Domain position

Schema:

- `minimal-domain-position-v0`

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

Támogatott pozíciótípusok:

- horizon;
- zenith;
- seal.

Production C# státusz:

- nem része a minimal draw/end-turn C.5B bizonyítás kötelező működési scope-jának;
- később typed production modellként migrálandó.

**Státusz:** `PLANNED_GAMEPLAY`

### 4.2 Player Domain topology

Schema:

- `minimal-player-domain-topology-v0`

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

Játékosonként:

- 6 current;
- 6 horizon;
- 6 zenith;
- 6 seal position;
- 18 stabil position reference.

**Production státusz:** `PLANNED_GAMEPLAY`

### 4.3 Domain occupancy

Schema:

- `minimal-domain-position-occupancy-v0`;
- `minimal-player-domain-occupancy-v0`.

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

Játékosonként:

- 12 occupancy slot;
- 6 horizon;
- 6 zenith;
- seal nem card occupancy slot.

Canonical kapcsolat:

- occupancy `position_id`;
- `occupant_card_instance_id`;
- card instance registry.

**Production státusz:** `PLANNED_GAMEPLAY`

---

## 5. Snapshot és projection contractok

### 5.1 Player-visible snapshot v2

Schema:

- `engine-player-visible-snapshot-v2`

Python státusz:

- `ACTIVE_REFERENCE_PROJECTION`

Visibility-policy:

- saját kéz: owner-visible;
- ellenfél kéz: redacted, count-only;
- deck: count-only;
- discard: public;
- Domain board: public.

Nem tartalmazhat:

- teljes MatchState-et;
- teljes registryt;
- ellenfél rejtett kézadatait;
- deck instance ID-kat;
- nem engedélyezett diagnosticsot.

C# candidate:

- mindkét játékos snapshotja a comparison fixture részeként bizonyított.

**Státusz:** `PROVEN_CSHARP_CANDIDATE`

Production C#:

- aktív viewer-specifikus typed `PlayerSnapshot`;
- saját kéz látható;
- ellenfél rejtett adatai csak számlálóként;
- stabil state version és legal action kapcsolat.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 5.2 Player-visible Domain board

Schema:

- `minimal-player-visible-domain-board-v0`

Python státusz:

- `ACTIVE_REFERENCE_PROJECTION`

Production C#:

- nem szükséges a C.5B draw/end-turn minimumhoz;
- az első valódi card-play vertical slice előtt migrálandó.

**Státusz:** `PLANNED_GAMEPLAY`

### 5.3 Debug snapshot

Python státusz:

- `ACTIVE_REFERENCE_PROJECTION`

Production C#:

- külön internal debug/diagnostics contract aktív;
- nem keverhető a player-facing snapshottal.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 5.4 Spectator, replay és külön AI snapshot

**Státusz:** `PLANNED_GAMEPLAY`

A fair AI továbbra is ugyanazt a player-visible observationt használja, mint az emberi játékos.

---

## 6. Legal action contractok

### 6.1 Minimal legal action space

Python státusz:

- `FOUNDATION_ONLY`

Aktív referenciaactionök:

- `draw_card`;
- `end_turn`.

C# candidate:

- draw és end-turn legal actionök bizonyítottak;
- stale action rejection bizonyított.

**Státusz:** `PROVEN_CSHARP_CANDIDATE`

Aktív production C# `LegalAction` minimum:

- `action_id`;
- `action_type`;
- `player_id`;
- `enabled`;
- `order_rank`;
- `disabled_reason`;
- `payload` vagy `payload_schema`.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 6.2 Structural Entity Domain placement options

Sémák:

- `minimal-entity-domain-placement-option-v0`;
- `minimal-entity-domain-placement-options-v0`.

Python státusz:

- `ACTIVE_ISOLATED`

Nem teljes legal play result.

Nem ellenőrzi:

- timing;
- priority;
- phase;
- Magnitúdó;
- Aura-payment;
- card-text restriction;
- entry state.

**Production státusz:** `PLANNED_GAMEPLAY`

### 6.3 `play_card`

**Státusz:** `PLANNED_GAMEPLAY`

Előfeltételek:

- production Wellspring;
- Beáramlás;
- Magnitúdó;
- Aura-payment;
- timing és priority;
- placement;
- entry-state;
- atomikus transition és event.

---

## 7. Action request és response

### 7.1 Minimal action request

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

Támogatja:

- match identity;
- player identity;
- expected state version;
- action type;
- request validáció.

C# candidate:

- request ID;
- match;
- player;
- expected state version;
- draw és end-turn request;
- stale request rejection.

**Státusz:** `PROVEN_CSHARP_CANDIDATE`

Aktív production C# minimum:

- `schema_version`;
- `request_id`;
- `match_id`;
- `player_id`;
- `expected_state_version`;
- `action_id`;
- `action_type`;
- `payload`.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 7.2 Expected state version guard

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

C# candidate:

- stale state rejection;
- state mutation nélkül;
- determinisztikus reason.

**Státusz:** `PROVEN_CSHARP_CANDIDATE`

Production C#:

- aktív stabil diagnostic code;
- state version nem változik;
- event sequence nem változik;
- request nem módosul.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 7.3 ActionResponse

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

Aktív production C# minimum:

- `schema_version`;
- `request_id`;
- `match_id`;
- `accepted`;
- `reason`;
- `state_version_before`;
- `state_version_after`;
- `events`;
- `diagnostics`.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

---

## 8. Event contractok

### 8.1 Generic event envelope

Schema:

- `minimal-engine-event-v0`

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

Aktív production C# minimum:

- event ID;
- event sequence;
- event type;
- match ID;
- state version;
- public payload;
- szükség esetén viewer-specifikus projection.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 8.2 Zone move event

Event type:

- `zone_move`

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

C# candidate:

- draw eseményként bizonyított.

**Státusz:** `PROVEN_CSHARP_CANDIDATE`

### 8.3 Turn transition event

Event type:

- `turn_transition`

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

C# candidate:

- end-turn eseményként bizonyított.

**Státusz:** `PROVEN_CSHARP_CANDIDATE`

### 8.4 Későbbi typed eventek

**Státusz:** `PLANNED_GAMEPLAY`

- Wellspring/infusion transition;
- activity state change;
- payment;
- card played;
- Entity entered Domain;
- attack/block/damage;
- seal break/restore;
- victory/defeat;
- ability resolution.

---

## 9. Diagnostics contract

### 9.1 Python referenciaelv

- non-throwing validator normál hibás inputra;
- strukturált `{valid, errors}`;
- deep-copy és inputváltozatlanság;
- determinisztikus sorrend;
- hidden-information audit;
- player-facing és developer diagnostics elhatárolása.

### 9.2 Aktív production C# minimum

`EngineDiagnostic` mezők:

- `code`;
- `severity`;
- `category`;
- `message`;
- `retry_policy`;
- strukturált `details`.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

Player-facing diagnostics nem szivárogtathat hidden informationt.

---

## 10. AI és trajectory contractok

### 10.1 Minimal AI-vs-AI episode

Schema:

- `minimal-ai-vs-ai-episode-v1`

Python státusz:

- `ACTIVE_REFERENCE_RUNTIME`

Támogatja:

- deterministic bot policy;
- accepted és rejected steps;
- player-visible observation;
- action request/response;
- eventek;
- trajectory validation;
- deterministic JSON output.

Production irány:

- a Python bot a C# headless engine legal action listájából választ;
- a C# marad authority;
- a Python nem implementál külön legalitást.

**Státusz:** `PLANNED_GAMEPLAY`

### 10.2 Replay readiness

Jelenlegi érték:

- `replay_ready: false`

**Státusz:** `FOUNDATION_ONLY`

---

## 11. Wellspring és resource contractok

### 11.1 Player Wellspring state

Schema:

- `minimal-player-wellspring-state-v0`

Python státusz:

- `ACTIVE_ISOLATED`

Fő mezők:

- player ID;
- zone `wellspring`;
- visibility `owner_only`;
- instance ID-lista;
- card count;
- metadata.

### 11.2 Wellspring resource summary

Schema:

- `minimal-wellspring-resource-summary-v0`

Python státusz:

- `ACTIVE_ISOLATED`

Canonical számítás:

- `magnitude == wellspring_card_count`;
- `available_aura == active_source_count`;
- active + exhausted = total count.

Nem implementált:

- typed Aura;
- payment;
- Rezonancia;
- temporary Aura;
- Aura-égés;
- Magnitúdó-override.

### 11.3 Production C# Wellspring

Nem része a C.5B scope-jának.

Első gameplay-migrációs feladat a C.5B után:

- PlayerState-integráció;
- initial üres Wellspring;
- listás zónatagság;
- registry-invariáns;
- resource summary;
- player-visible projection.

**Státusz:** `PLANNED_GAMEPLAY`

---

## 12. Runtime comparison fixture contractok

A `minimal_draw_end_turn_v1` fixture bizonyítja:

1. initial state;
2. P1 draw;
3. stale request rejection;
4. P1 end turn;
5. P2 draw;
6. player-visible snapshotok;
7. typed eventek;
8. legal action checkpointok;
9. canonical JSON;
10. determinisztikus ismétlés.

Helyes canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

A fixture:

- Python reference oracle;
- sidecar comparison;
- C# candidate proof;
- később production C# regresszió.

**Státusz:** `REFERENCE_ONLY`

A fixture-specifikus request ID-k és lépéssor nem kerülhet az általános production EngineSession contractba.

---

## 13. Superseded és debug contractok

### 13.1 Player-visible snapshot v1

- schema: `engine-player-visible-snapshot-v1`;
- státusz: `SUPERSEDED`;
- felváltotta: v2.

### 13.2 Card instance record v0

- schema: `minimal-card-instance-record-v0`;
- státusz: `SUPERSEDED`;
- felváltotta: v1.

### 13.3 Godot sample snapshot/legal actions/events

- státusz: `DEBUG_FIXTURE`.

Fontos loader- és UI-tesztek, de nem production gameplay-contractok.

### 13.4 RuntimeCandidate belső proof contractok

- státusz: `REFERENCE_ONLY`.

A production C# API tervezésénél felhasználhatók bizonyítékként, de nem emelendők át automatikusan változatlan publikus contractként.

---

## 14. Production C# contract-lánc

### C.5B – implementált foundation

1. runtime package descriptor vagy source;
2. `CreateMatchRequest`;
3. `CreateMatchResponse`;
4. `ActionRequest`;
5. `ActionResponse`;
6. `LegalAction`;
7. `PlayerSnapshot`;
8. `EngineEvent`;
9. `EngineDiagnostic`;
10. `MatchResult`;
11. EngineSession API;
12. draw;
13. end-turn;
14. stale rejection;
15. canonical serializer;
16. fixture adapter;
17. Godot production bridge.

Lezáró commit:

`931bf5571d541c752aa421a9f0626768bd8ffbe7`

Ellenőrzött bizonyíték:

- production tesztek Debug és Release: `13/13`;
- canonical expected és actual SHA: `650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`;
- canonical méret: `210730` byte;
- determinisztika: `100/100`;
- a canonical snapshot és eventösszegzés a production player projectionből és viewer-safe event API-ból származik;
- Godot pozitív és negatív production bridge smoke: PASS.

### C.5B után

1. Wellspring state;
2. Wellspring projection;
3. infusion precondition;
4. infusion transition;
5. Magnitúdó-preflight;
6. Aura-source selection;
7. payment;
8. activity mutation;
9. Entity play precondition;
10. `play_card`;
11. Entity entry;
12. phase/priority/reaction;
13. combat;
14. ability execution.

---

## 15. Contract-validációs elvek

Minden production contractnál kötelező:

- explicit schema version;
- typed C# belső vagy publikus modell;
- stabil mezőjelentés;
- inputváltozatlanság;
- deterministic ordering;
- rejected action state-immutability;
- hidden-information-védelem;
- player-facing és debug payload elhatárolása;
- stabil diagnostic code;
- canonical serialization;
- fixture- és regressziós teszt;
- Godot adapterben nincs rules logic;
- Python kliens nem kerülheti meg a C# authority-kaput.

---

## 16. Dokumentumkapcsolatok és összevonási döntés

A contract-dokumentumok külön szerepe indokolt:

### `CONTRACT_SPECIFICATION.md`

- technológiafüggetlen cél- és szerkezeti specifikáció;
- hosszú távú contractjelentések;
- nem kizárólag implementációs státusz.

### `CONTRACT_STATUS.md`

- aktuális megvalósítási státusz;
- Python reference, C# candidate és production terv elkülönítése;
- rövid, operatív folytatási referencia.

### `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`

- történeti konszolidációs referencia;
- jelzi, mi került át az aktív specifikációba;
- későbbi migrációs kör indítási feltétele.

Döntés:

- a három fájl jelenleg nem egyesítendő;
- mindhárom verziózandó és státuszolandó;
- a migration map később történeti dokumentummá minősíthető;
- a végső dokumentumauditban újra ellenőrizendő, hogy maradt-e érdemi aktív szerepe.

---

## 17. Dokumentumkezelési hatás

Ez a fájl a `CURRENT_CONTRACT_STATUS.md` utódja.

A repository aktuális állapota:

1. az aktív név `CONTRACT_STATUS.md`;
2. a régi `CURRENT_CONTRACT_STATUS.md` nem aktív authority;
3. az aktív hivatkozások az utódfájlra mutatnak.

---

## 18. Rövid státuszösszegzés

**Python aktív referencia state:** card instance v1, MatchState, Domain topology és occupancy  
**Python aktív player projection:** snapshot v2 és public Domain board  
**Python aktív action:** draw, end turn  
**Python aktív event:** zone move, turn transition  
**Python aktív AI contract:** episode v1  
**C# candidate proof:** draw, stale rejection, end-turn, snapshot, event és legal action  
**Production C# contractok:** C.5B foundationben aktívak\
**Izolált következő gameplay-alap:** Wellspring state és resource summary  
**Nem aktív production gameplay:** infusion, payment, play_card, combat, ability execution
