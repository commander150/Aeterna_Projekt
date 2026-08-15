# AETERNA – CROSS-PROJECT SYNTHESIS: EVENTS AND PROJECTION

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első generalized event/projection synthesis
- **Javasolt repository-útvonal:** `learning/synthesis/topics/events_and_projection.md`
- **AETERNA production összevetési bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Nem AETERNA-szabályforrás.**

---

# 1. Evidence

Learning:

- boardgame.io – state/log különválasztás, playerView, redacted log, filtered-state delta;
- PokerKit – typed operation history;
- Forge/MAGE/ocgcore – trigger/event/resolution context és causality;
- OpenSpiel – history/serialization/player observation;
- Colyseus – per-client view + state patch ordering;
- Nakama – targeted reliable broadcast.

AETERNA current:

- ordered internal `EngineEvent` store;
- event ID + sequence + state version + turn + actor + cause action type;
- typed payload records;
- `GetEvents(viewer, afterSequence)`;
- `ProjectEventForViewer`;
- debug full event stream;
- ActionResponse event projection;
- trigger discovery from committed events.

---

# 2. P-EVT-001 – Internal event és viewer event külön contract

**Státusz:** `REPEATED_PATTERN`  
**AETERNA:** `IMPLEMENTED_FOUNDATION`

Current:

```text
state.Events          # internal full fidelity
GetEvents(viewer)     # projection
ActionResponse        # projected events
GetDebugEvents        # internal clone
```

Ez megtartandó.

---

# 3. P-EVT-002 – Ordered immutable history

Current internal invariant:

- event sequences contiguous;
- event IDs sequence-alapúak;
- state version rögzített.

Ez értékes:
- trigger correlation;
- replay;
- network cursor;
- diagnostics;
- deterministic proof.

Később event store implementation változhat, de ordered sequence invariant maradjon.

---

# 4. P-EVT-003 – Causality legyen elsőrendű

A current top-level event metadata tart:

- cause action type.

Sok canonical payload külön tart:
- source action ID;
- resolution ID;
- pending trigger ID;
- trigger ID;
- cause event ID egyes payloadokban.

Ez már jó irány, de heterogén.

Reaction/replay/network előtt candidate:

```text
EventCausality
- cause_action_id?
- cause_action_type?
- parent_event_id?
- originating_event_id?
- resolution_id?
- pending_window_id?
```

Nem kell minden mező minden eventre.

## Migration elv

Ne másoljuk duplán minden payloadba, ha generic metadata elég.

De ne törjük visszamenőleg a működő payloadokat csak esztétikai refactorért.

---

# 5. P-EVT-004 – Pending timing context nem ugyanaz mint committed event

Reaction esetén fontos három fogalom:

```text
Action/Intent
Pending Resolution/Timing Context
Committed EngineEvent
```

Egy jövőbeli effect még nem „megtörtént event” pusztán azért, mert reaction window nyílt fölötte.

A rules által külön eseménynek minősülő declaration viszont saját committed event lehet.

## Következtetés

Reaction stack entry / timing context ne legyen hamis `EngineEvent`.

EngineEvent tényt/historyt jelent.

---

# 6. P-EVT-005 – Commit után kerülhet canonical historyba

Normal transition:

```text
validate / plan
→ commit authoritative state
→ materialize/append committed events
```

Current `play_card` event-descriptorokat előre tud tervezni, de az event store-ba csak a commit környezetében kerülnek.

Normál reject nem hagy eventet.

Ez megtartandó.

---

# 7. P-EVT-006 – Consequence/trigger discovery committed eventből

Current:

```text
action events committed/materialized
→ DiscoverCanonicalTriggers
→ consequence events / pending trigger state
```

Ez erős event-driven primitive.

Később reaction/trigger coordinator ezt kiterjesztheti, de ne legyen minden effect handler saját ad-hoc trigger scan.

---

# 8. P-EVT-007 – Audience és payload projection két külön kérdés

A current projection jó példája:

- `zone_move` esemény maga public;
- opponent számára a hidden card identity redaktált;
- `card_readied` / `aura_source_exhausted` payload identity szintén viewer-függő.

Tehát:

```text
event existence visibility
≠
payload field visibility
```

Future candidate metadata:

```text
AudiencePolicyId
PayloadProjectionPolicyId
```

Példák:

- event public + identity redacted;
- owner-only event;
- public event fully visible;
- debug-only internal event.

---

# 9. P-EVT-008 – Hardcoded event-type projection később registry/policy felé nőhet

Current `ProjectEventForViewer` konkrét event type branch-eket tart.

A jelenlegi scopeban működőképes.

Ahogy bekerül:
- Reaction;
- hidden Jel;
- optional private choice;
- spectator;
- network replay

érdemes projection registry/policyt használni.

Candidate:

```text
IEventProjectionPolicy
Project(internalEvent, viewerContext)
```

De ezt sem kell előre refactorolni Reaction v1 első napján, ha a supported eventek kicsik és tiszták.

---

# 10. P-EVT-009 – Event existence secrecy külön kapu

A current `GetEvents` minden internal eventet végigprojektál; a sequence így minden viewernek ugyanaz a globális timeline.

Ez kiváló, ha az event **létezése public**, és csak payloadja rejtett.

Ha később olyan official mechanic jelenik meg, ahol már az event létezése is titkos:

- globális sequence gap placeholder leak lehet;
- vagy viewer event cursor szükséges.

## V0.1 döntés

Ne tervezzünk még külön viewer sequence-et szükség nélkül.

Legyen explicit future gate:

`EVENT_EXISTENCE_CONFIDENTIALITY_REQUIRED`

csak akkor, ha official rule ténylegesen megköveteli.

---

# 11. P-EVT-010 – Technical vs canonical gameplay event

Current event streamben együtt él:

- zone move;
- phase transition;
- canonical ability resolved;
- modifier/keyword lifecycle;
- trigger technical events.

Reaction blueprint új technical eventeket is javasol.

Hosszú távú candidate classification:

```text
gameplay
timing
system/lifecycle
audit/debug
```

Ez:
- replay export;
- UI filtering;
- diagnostics;
- spectator

szempontból hasznos.

Nem kell új event store.

---

# 12. P-EVT-011 – Diagnostic nem gameplay event

Reject:
- ActionResponse diagnostic;
- nincs EngineEvent.

Ez helyes.

Operational/server error:
- logging/metrics;
- nem rules event.

Replay:
- accepted gameplay decisions/events;
- nem minden developer diagnostic.

---

# 13. P-EVT-012 – ActionResponse és GetEvents ugyanazt a projection policyt használja

Current `ProjectActionResponseForViewer` ugyanazt a `ProjectEventForViewer` függvényt alkalmazza, mint `GetEvents`.

Ez kiváló invariant:

> ugyanaz az internal event ugyanannak a viewernek minden API-n ugyanazt a projected payloadot adja.

Megőrzendő.

---

# 14. P-EVT-013 – Projection determinisztikus és side-effect-free

Viewer projection:

- nem mutál state-et;
- nem random;
- csak viewer identity + event + authority policy alapján számol.

Ez szükséges:
- replay;
- network retry;
- snapshot hash;
- AI.

---

# 15. P-EVT-014 – Player snapshot és event projection ugyanazt a visibility modelt használja

Current:
- hand owner-visible/count-only;
- Wellspring owner-visible/summary-only;
- Domain public;
- event payloadok ugyanezekhez igazodnak.

Future rule:

> egy object identity ne legyen rejtett snapshotban, majd ugyanabban a rules state-ben véletlenül kiszivárogtatva event payloadban.

Projection policy közös visibility primitive-ekre épüljön.

---

# 16. Diagnostic projection – future network hardening

Current ActionResponse projection csak az eventeket projektálja.

Future remote client előtt:

```text
ActionResponse
├── projected events
└── projected public diagnostics
```

Developer messages:
- server log;
- debug UI;
- trusted analyzer.

Ez nem szükséges a local current bridge átírásához, de multiplayer milestone előtt kapu.

---

# 17. Network/replay cursor

Current:
```text
GetEvents(viewer, afterSequence)
```

Jól működik, amíg global event existence public.

Future network resync:
- state version;
- last internal/public event cursor;
- viewer projection.

Ha hidden event existence valaha szükséges:
- opaque viewer cursor vagy separate projected sequence.

Ne vezessük be előre.

---

# 18. Anti-patternök

| ID | Név |
|---|---|
| `A-EVT-001` | UI maga redaktál authoritative eventet |
| `A-EVT-002` | internal event közvetlenül minden viewernek |
| `A-EVT-003` | pending intent committed eventként |
| `A-EVT-004` | reject után event marad |
| `A-EVT-005` | trigger scan ad-hoc minden handlerben |
| `A-EVT-006` | event audience és payload visibility összemosva |
| `A-EVT-007` | projection pathonként eltérő |
| `A-EVT-008` | hidden snapshot, de event identity leak |
| `A-EVT-009` | developer diagnostic player eventként |
| `A-EVT-010` | nondeterministic projection |
| `A-EVT-011` | event type stringből implicit causality |
| `A-EVT-012` | private event existence global sequenceből kiszivárog, ha rules szerint titkos |

---

# 19. Verdict

A current AETERNA event architecture erős alap.

A következő fejlesztési irány nem event-sourcing rewrite, hanem:

1. reaction causality/context;
2. projection policy fokozatos általánosítása;
3. public diagnostic hardening online előtt;
4. replay/network cursor és versioning később;
5. event-existence confidentiality csak valós rules igénynél.
