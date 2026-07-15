# AETERNA Game Engine – Current Contract Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív megvalósítási contract-státusz  
**Technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum azt rögzíti, hogy a hosszú formájú contract-tervekből mi létezik ténylegesen a jelenlegi Python engine-ben.

Nem helyettesíti a `CONTRACT_SPECIFICATION.md` teljes tervezési anyagát. A hosszú dokumentum megőrzi a későbbi modelleket és kérdéseket; ez a fájl az aktív implementáció rövid, authoritative státuszlistája.

---

## 1. Státuszjelölések

| Státusz | Jelentés |
|---|---|
| `active_runtime` | Production minimal engine használja. |
| `active_projection` | Player-facing vagy debug projekcióban használatos. |
| `active_isolated` | Megvalósított és tesztelt helper, de még nincs MatchState/runtime integráció. |
| `foundation_only` | Alapcontract létezik, teljes gameplay-integráció még nincs. |
| `planned` | Dokumentált, de még nincs aktív implementáció. |
| `superseded` | Korábbi minta vagy séma, aktív runtime már nem használja. |
| `debug_fixture` | Kézzel írt vagy generált teszt/debug adat, nem authoritative gameplay-contract. |

---

## 2. Aktív belső state contractok

### 2.1 Card instance record

- schema: `minimal-card-instance-record-v1`
- státusz: `active_runtime`
- fő szerep: meccsbeli kártyapéldány authoritative rekordja

Fő mezők:

- `card_instance_id`
- `card_id`
- `owner_player_id`
- `controller_player_id`
- `zone`
- `zone_index`
- `visibility`
- `created_sequence`
- `zone_sequence`
- `activity_state`
- `metadata`

Támogatott activity értékek:

- `None`
- `active`
- `exhausted`

Jelenlegi zone/activity szabály:

- deck, hand, discard → `None`
- domain, wellspring → `active` vagy `exhausted`

A Wellspring-zone record támogatott, de a Wellspring még nincs production PlayerState-be kötve.

### 2.2 ObjectReference

- schema: `minimal-object-reference-v0`
- státusz: `active_projection`
- fő szerep: card instance rövid, biztonságos hivatkozása contractokban

Nem teljes card instance dump.

Jelenleg nem tartalmaz activity state-et.

### 2.3 ZoneMove

- schema: minimal ZoneMove contract
- státusz: `active_runtime`
- fő szerep: zónamozgás strukturált leírása

Aktív production használat:

- draw: deck → hand

Még nincs aktív használat:

- hand → Wellspring;
- hand → Domain;
- Domain → discard;
- más komplex zónamozgások.

### 2.4 MatchState

- státusz: `active_runtime`
- authoritative belső meccsállapot

Jelenlegi fő rétegek:

- player state-ek;
- card instance registry;
- state version;
- turn/priority alap;
- event log;
- Domain topológiák;
- Domain occupancy state-ek.

A MatchState nem player-facing contract.

### 2.5 PlayerState zónalisták

- deck: `active_runtime`
- hand: `active_runtime`
- discard: `active_runtime`
- Wellspring: `planned_next`

A Wellspring isolated state contractja létezik, de a PlayerState-mező még nincs bevezetve.

---

## 3. Domain contractok

### 3.1 Domain position

- schema: `minimal-domain-position-v0`
- státusz: `active_runtime`

Támogatott pozíciótípusok:

- horizon;
- zenith;
- seal.

### 3.2 Player Domain topology

- schema: `minimal-player-domain-topology-v0`
- státusz: `active_runtime`

Játékosonként:

- 6 current;
- 6 horizon;
- 6 zenith;
- 6 seal position;
- 18 stabil position reference.

### 3.3 Domain position occupancy

- schema: `minimal-domain-position-occupancy-v0`
- státusz: `active_runtime`

### 3.4 Player Domain occupancy

- schema: `minimal-player-domain-occupancy-v0`
- státusz: `active_runtime`

Játékosonként:

- 12 occupancy slot;
- 6 horizon;
- 6 zenith;
- seal nem occupancy slot.

Canonical kapcsolat:

- occupancy `position_id`;
- `occupant_card_instance_id`;
- card instance registry.

A kapcsolatot kétirányú state-invariáns védi.

---

## 4. Snapshot és projection contractok

### 4.1 Player-visible snapshot

- schema: `engine-player-visible-snapshot-v2`
- státusz: `active_projection`

Jelenlegi visibility-policy:

- saját kéz: owner-visible;
- ellenfél kéz: redacted, count-only;
- deck: count-only;
- discard: public;
- Domain board: public.

Nem tartalmaz:

- teljes MatchState-et;
- teljes registryt;
- teljes topology vagy occupancy contractot;
- ellenfél rejtett kézadatait;
- deck instance ID-kat.

Wellspring projection még nincs.

### 4.2 Player-visible Domain board

- schema: `minimal-player-visible-domain-board-v0`
- model: `minimal-public-domain-board-v0`
- státusz: `active_projection`

Tartalmaz:

- két player boardját;
- current 1–6;
- horizon és zenith slotot;
- empty/occupied állapotot;
- occupied slotban ObjectReference-et;
- statikus seal position reference-et.

Seal state még `not_implemented`.

### 4.3 Debug snapshot

- státusz: `active_projection`
- schema és részletes tartalom változatlan a player-visible board bevezetése során

Nem tekintendő player-facing nézetnek.

### 4.4 Spectator, replay és külön AI snapshot

- státusz: `planned`

A fair AI jelenleg a canonical player-visible observationt használja.

---

## 5. Legal action és placement contractok

### 5.1 Minimal legal action space

- státusz: `foundation_only`

Jelenlegi aktív actionök:

- `draw_card`
- `end_turn`

A legal action rendszer még nem modellezi a teljes AETERNA döntési teret.

### 5.2 Structural Entity Domain placement option

- schema: `minimal-entity-domain-placement-option-v0`
- státusz: `active_isolated`

### 5.3 Structural Entity Domain placement options

- schema: `minimal-entity-domain-placement-options-v0`
- model: `structural-entity-domain-placement-v0`
- státusz: `active_isolated`

Eligible source feltételei:

- instance létezik;
- source a query player kezében van;
- controller egyezik;
- runtime card type canonical értéke `entity`.

Output:

- pontosan 12 saját horizon/zenith option;
- occupied target is megmarad;
- occupied target structurally unavailable.

Explicit nem ellenőrzi:

- timingot;
- priorityt;
- phase-t;
- Magnitúdót;
- Aura-paymentet;
- card-text restrictiont;
- entry state-et.

Ez nem teljes legal play result és nincs bekötve `play_card` actionként.

### 5.4 `play_card`

- státusz: `planned`

Előfeltételek:

- Wellspring runtime integráció;
- Beáramlás;
- Magnitúdó-preflight;
- payment;
- timing és priority;
- placement;
- entry-state;
- atomikus transition és event.

---

## 6. Action request és response

### 6.1 Minimal action request

- státusz: `active_runtime`

Támogatja többek között:

- match identity;
- player identity;
- expected state version;
- action type;
- request létrehozását és validálását.

### 6.2 Expected state version guard

- státusz: `active_runtime`

Stale vagy hibás state version esetén reject, state mutation nélkül.

### 6.3 Rejected action response

- státusz: `active_runtime`

A rejected request:

- nem mutál state-et;
- strukturált reason/diagnostics eredményt ad;
- trajectory stepként is megőrizhető.

### 6.4 Teljes `play_card` request/response

- státusz: `planned`

Payment-, target-, choice- és reaction-rétegek még nem aktívak.

---

## 7. Event contractok

### 7.1 Generic engine event envelope

- schema: `minimal-engine-event-v0`
- státusz: `active_runtime`

### 7.2 Zone move event

- event type: `zone_move`
- státusz: `active_runtime`
- aktív használat: draw

### 7.3 Turn transition event

- event type: `turn_transition`
- státusz: `active_runtime`
- aktív használat: end turn

### 7.4 Még tervezett typed eventek

- Wellspring/Inflow transition;
- activity state change;
- payment;
- card played;
- Entity entered Domain;
- attack/block/damage;
- seal break/restore;
- victory/defeat.

---

## 8. AI és trajectory contractok

### 8.1 Minimal AI-vs-AI episode

- schema: `minimal-ai-vs-ai-episode-v1`
- státusz: `active_runtime`

Támogatja:

- deterministic bot policy;
- accepted és rejected steps;
- player-visible observation;
- action request/response;
- eventek;
- trajectory validation;
- deterministic JSON output.

### 8.2 Replay readiness

- jelenlegi érték: `replay_ready: false`
- státusz: `foundation_only`

A trajectory replay-alapot ad, de nincs teljes replay runner.

---

## 9. Wellspring és resource contractok

### 9.1 Player Wellspring state

- schema: `minimal-player-wellspring-state-v0`
- státusz: `active_isolated`

Fő mezők:

- player ID;
- zone `wellspring`;
- visibility mode `owner_only`;
- instance ID-lista;
- card count;
- metadata.

### 9.2 Wellspring resource summary

- schema: `minimal-wellspring-resource-summary-v0`
- model: `base-wellspring-count-and-activity-v0`
- státusz: `active_isolated`

Canonical számítás:

- `magnitude == wellspring_card_count`
- `available_aura == active_source_count`
- active + exhausted = total count

Nem implementált:

- typed Aura;
- payment;
- Rezonancia;
- temporary Aura;
- Aura-égés;
- Magnitúdó-override.

### 9.3 Wellspring MatchState-integráció

- státusz: `planned_next`

Következő feladat:

- PlayerState-lista;
- initial üres Wellspring;
- registry és listás zónatagsági invariáns;
- resource summary canonical elérése.

---

## 10. Contract-validációs elvek

A jelenlegi contract helperek általános elvei:

- JSON-kompatibilis dict/list output;
- schema version;
- contract type;
- non-throwing validator normál hibás inputra;
- strukturált `{valid, errors}` eredmény;
- kontrollált builder exception invalid state/query esetén;
- deep-copy és inputváltozatlanság;
- determinisztikus sorrend és azonosítók;
- runtime state leak és tiltott mezők ellenőrzése;
- canonical builder/validator újrahasználata.

---

## 11. Superseded és fixture contractok

### 11.1 Player-visible snapshot v1

- schema: `engine-player-visible-snapshot-v1`
- státusz: `superseded`
- felváltotta: v2 public Domain boarddal

### 11.2 Card instance record v0

- schema: `minimal-card-instance-record-v0`
- státusz: `superseded`
- felváltotta: v1 `activity_state` mezővel

### 11.3 Godot sample snapshot/legal actions/events

- státusz: `debug_fixture`

Ezek fontos loader- és UI-tesztek, de nem azonosak a jelen Python rules engine aktív contractjaival.

---

## 12. Következő contract-lánc

1. Wellspring MatchState-integráció;
2. player-visible Wellspring summary;
3. Inflow precondition contract;
4. Inflow transition és typed event;
5. Magnitúdó-preflight;
6. Aura-source selection;
7. payment contract;
8. activity mutation;
9. Entity play precondition;
10. `play_card` action és response;
11. Entity entry event;
12. phase/priority/reaction contractok.

---

## 13. Rövid státuszösszegzés

**Aktív belső state:** card instance v1, MatchState, Domain topology és occupancy  
**Aktív player projection:** snapshot v2 és public Domain board  
**Aktív runtime action:** draw, end turn  
**Aktív event:** zone move, turn transition  
**Aktív AI contract:** episode v1  
**Izolált következő alap:** Wellspring state és resource summary  
**Következő contract-integráció:** Wellspring production state  
**Nem aktív még:** Inflow, payment, play_card, combat, ability execution
