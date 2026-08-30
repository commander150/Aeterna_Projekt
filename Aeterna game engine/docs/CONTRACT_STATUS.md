# AETERNA Game Engine – Contract Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.5
**Dátum:** 2026-08-30
**Státusz:** aktív megvalósítási contract-státusz
**Felváltott fájl:** `CURRENT_CONTRACT_STATUS.md`
**Aktuális repository-bázis:** `f4e035bb1b8a1b94840a180df7f9c24aa3cf302c` – `engine: implement Reaction Priority v1 foundation`

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
- a C.5B történeti minimuma nem tartalmazta a Wellspring, Beáramlás, payment, `play_card` vagy ability execution réteget; a `931bf... → 2608345b...` production szakaszban ezek közül több már megvalósult. Reaction / Priority Foundation v1 productionben implementált és elfogadott; Combat továbbra sincs productionben.

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

### 2.3 Reaction / Priority v1 production status

Production commit:

`f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`

Megvalósult többek között:

- `react` / `pass_priority`;
- authoritative `ReactionWindow`;
- canonical resolution stack;
- LIFO resolution;
- RC1;
- RC2 queued-trigger checkpoint/FIFO;
- shared `resolution` zone played Ige/egyszeri Rituálé lifecycle-hoz;
- viewer-safe reaction projection;
- full-closure transactional preflight.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION / COMPLETE_AND_ACCEPTED`

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

- deck, hand, void → `None`;
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

Történeti referenciahasználat:

- draw: deck → hand.

Production C# használat többek között:

- draw: deck → hand;
- normál Beáramlás: hand → Wellspring;
- `play_card`: hand → Domain;
- canonical Void-tranzíciók;
- ability/effect runtime által végrehajtott támogatott canonical zónamozgások.

A ZoneMove/typed `zone_move` jelentés a production transitionök közös alapja. Ez nem jelenti azt, hogy minden jövőbeli zónamozgás vagy replacement szabály már támogatott.

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
- void: `ACTIVE_REFERENCE_RUNTIME`;
- Wellspring: referenciaoldalon megvalósított resource/zónaalap.

Production C#:

- deck;
- hand;
- void;
- Wellspring;
- Domainhoz kapcsolódó authoritative board/occupancy állapot;
- zónánként és activity szerint konzisztens card-instance registry.

A teljes jövőbeli zónakészlet és minden resolution/intermediate zone ettől még nincs lezárva.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`


---

## 4. Domain contractok

### 4.1 Domain position

Schema/reference:

- `minimal-domain-position-v0`

Python referencia:

- `ACTIVE_REFERENCE_RUNTIME`

Támogatott történeti pozíciótípusok:

- horizon;
- zenith;
- seal.

Production C#:

- typed Domain position/topology foundation aktív;
- Domain placement a canonical `play_card` flow része;
- a Pecsét pozíció nem hagyományos HP-objektum és nem tekintendő normál card-occupancy slotnak.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 4.2 Player Domain topology

Schema/reference:

- `minimal-player-domain-topology-v0`

Python referencia:

- `ACTIVE_REFERENCE_RUNTIME`

A Domain stabil topology/position reference elve productionben is megmarad.

**Production státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

A teljes combat- és Pecsét-state semantics külön későbbi rules/contract réteg.

### 4.3 Domain occupancy

Schema/reference:

- `minimal-domain-position-occupancy-v0`;
- `minimal-player-domain-occupancy-v0`.

Python referencia:

- `ACTIVE_REFERENCE_RUNTIME`

Production C#:

- Domain occupancy/placement authoritative state-ben aktív;
- az occupant card instance a registryvel konzisztens;
- `play_card` validálja a támogatott placementet;
- viewer-safe Domain board projection aktív foundation.

**Production státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

A combat, attack/block és teljes Pecsétmodell nem következik automatikusan ebből.


---

## 5. Snapshot és projection contractok

### 5.1 Player-visible snapshot v4

Schema:

- `engine-player-visible-snapshot-v4`

Python státusz:

- `ACTIVE_REFERENCE_PROJECTION`

Visibility-policy:

- saját kéz: owner-visible;
- ellenfél kéz: redacted, count-only;
- deck: count-only;
- Void: public;
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

Schema/reference:

- `minimal-player-visible-domain-board-v0`

Python státusz:

- `ACTIVE_REFERENCE_PROJECTION`

Production C#:

- a Domain board viewer-safe player snapshot/projection részeként production foundation;
- nem teljes MatchState dump;
- az occupancy és card reference a public visibility szabály szerint jelenik meg.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 5.3 Debug snapshot

Schema:

- `aeterna-debug-match-snapshot-v4`

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

### 6.1 Production legal action space

A production C# engine authoritative phase state machine-je:

`awakening -> infusion -> manifestation -> incursion -> distribution`

Canonical public progression action:

- `advance_phase`.

Aktuális minimum fázismátrix:

- Awakening: `advance_phase`;
- Infusion: `normal_inflow`, `advance_phase`;
- Manifestation: `play_card`, `advance_phase`;
- Incursion: `advance_phase`;
- Distribution: `advance_phase`.

A normál production public action space-ben nincs:

- `draw_card`;
- `end_turn`.

A historical runtime-comparison adapter a régi draw/end-turn proofot izoláltan megtarthatja.

Direct hand-crafted production requesttel:

- `draw_card`;
- `end_turn`;
- rossz fázisú `normal_inflow`

stabilan elutasított és nem mutál authoritative state-et vagy event historyt.

A pending-trigger gate továbbra is authoritative.

A public `ActionResponse.Events` viewerje a requestet beküldő `player_id`; player switch nem cserélheti át a viewer identitását. Az internal event store full-fidelity.

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

Aktív `LegalAction` minimum:

- `action_id`;
- `action_type`;
- `player_id`;
- `enabled`;
- `order_rank`;
- `disabled_reason`;
- `payload` vagy `payload_schema`.

### 6.2 Structural Entity Domain placement options

A történeti structural placement reference a production Domain/`play_card` flow előkészítő proofja volt.

Production C#-ban a támogatott placement:

- authoritative state alapján számított;
- phase- és source-validált;
- Domain occupancy invariánssal ellenőrzött;
- player-facing legal action/play request része.

Nem jelenti a combat vagy minden card-type placement szabály teljes támogatását.

**Production státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

### 6.3 `play_card`

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

Production minimum:

- Manifestation phase legality;
- hand source;
- canonical card/runtime binding;
- Magnitúdó-preflight;
- Aura-payment preflight;
- támogatott source selection;
- Domain placement;
- atomikus state mutation;
- typed eventek;
- canonical ability/effect hook;
- rejection esetén változatlan state/event history.

Továbbra sem jelenti:

- teljes kártyaállomány teljes ability coverage-ét;
- Reaction/Priority implementációt;
- combatot;
- minden alternate/temporary payment mechanikát.


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

### 8.4 Production event lifecycle és további typed eventek

Aktív production foundation:

- `phase_transition`;
- `turn_transition`;
- `card_readied`;
- canonical `zone_move`;
- támogatott activity/payment transitionök structured eventjei;
- támogatott card-play és canonical ability/effect resolution eventcsalád.

Az explicit phase foundation eventjei viewer-safe public projectionön keresztül érhetők el; az internal event store full-fidelity marad.

További későbbi event-réteg:

- Reaction/Priority;
- combat attack/block/combat-damage;
- Pecsét-feltörés és restore;
- victory/defeat;
- további még nem támogatott ability/replacement események.

**Aktív alap státusza:** `ACTIVE_PRODUCTION_FOUNDATION`
**További eventcsaládok:** `PLANNED_GAMEPLAY`

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

**Státusz:** `ACTIVE_PRODUCTION_FOUNDATION`

Megvalósult:

- PlayerState-integráció;
- initial üres Wellspring;
- listás zónatagság;
- card-instance registry invariáns;
- Wellspring resource summary;
- player-visible/viewer-safe projection;
- normál `normal_inflow`;
- once-per-turn usage guard;
- face-down + active entry;
- Magnitúdó/Aura preflight kapcsolódás;
- `active -> exhausted` payment mutation foundation;
- Awakening ready kapcsolódás.

Nem tekintendő teljes supportnak többek között:

- temporary Aura;
- Rezonancia teljes production mechanikája;
- Aura-égés;
- Magnitúdó-override;
- alternate cost/replacement.


---

## 12. Runtime comparison fixture contractok

A `minimal_draw_end_turn_v2` fixture bizonyítja:

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

`97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`

A fixture:

- Python reference oracle;
- sidecar comparison;
- C# candidate proof;
- később production C# regresszió.

**Státusz:** `REFERENCE_ONLY`

A fixture-specifikus request ID-k és lépéssor nem kerülhet az általános production EngineSession contractba.

A `minimal_draw_end_turn_v1` és a hozzá tartozó `650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d` hash történeti bizonyítékként változatlanul megmarad. A v2 a `discard` technikai zóna canonical `void` zónára migrálása miatt új contract-fixture.

---

## 13. Superseded és debug contractok

### 13.1 Player-visible snapshot v1

- schema: `engine-player-visible-snapshot-v1`;
- státusz: `SUPERSEDED`;
- felváltotta: v2, v3, majd v4.

### 13.1.1 Player-visible snapshot v2

- schema: `engine-player-visible-snapshot-v2`;
- státusz: `SUPERSEDED`;
- felváltotta: v3, majd v4.

### 13.1.2 Canonical match state v1 és debug snapshot v1

- schema: `aeterna-canonical-match-state-v1`, `aeterna-debug-match-snapshot-v1`;
- státusz: `SUPERSEDED`;
- felváltotta: v2, majd v3 és v4.

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

### C.5B – implementált történeti foundation

Lezáró commit:

`931bf5571d541c752aa421a9f0626768bd8ffbe7`

A C.5B bizonyította többek között:

1. runtime package minimum loader;
2. `CreateMatchRequest`;
3. authoritative MatchState minimum;
4. player snapshot;
5. legal action;
6. action request/response;
7. draw;
8. stale rejection;
9. viewer-safe event projection;
10. Godot production bridge.

Ez történeti scope-határ, nem a jelenlegi production maximum.

### C.5B utáni production gameplay/ability foundation

A `931bf... -> 2608345b...` szakaszban aktív production foundation lett többek között:

1. Wellspring state és projection;
2. normal Infusion;
3. Magnitúdó-preflight;
4. Aura-payment preflight;
5. activity mutation;
6. Domain/placement;
7. `play_card`;
8. canonical zone/Void transition;
9. canonical card/runtime binding;
10. ability catalog/template compiler;
11. condition/target/trigger/effect execution foundation;
12. continuous effects;
13. modifier/keyword/duration;
14. damage/vitals/lethal lifecycle;
15. draw/reference runtime;
16. explicit phase lifecycle.

### Explicit Phase Foundation v1

Lezáró commit:

`2608345b61526097fc0b118f05461f92cfed0a95`

Státusz:

`COMPLETE_AND_ACCEPTED`

### Következő contract-kapu

`Reaction / Priority Foundation v1`

Előbb rules/OQ/contract audit szükséges. Combat külön későbbi slice.


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
**Python aktív player projection:** snapshot és public Domain board reference
**Python aktív action/event:** történeti reference draw/end-turn és zone/turn eventek
**C# candidate proof:** draw, stale rejection, end-turn, snapshot, event és legal action
**Production C# contractok:** C.5B foundation + post-C.5B gameplay/ability + Explicit Phase Foundation aktív
**Aktív production gameplay foundation:** Wellspring, normal Infusion, payment preflight, Domain, `play_card`, canonical ability/effect runtime foundation
**Nem teljes production:** Reaction/Priority, combat, teljes Pecsétmodell, Refresh Penalty, teljes ability coverage, victory/defeat
