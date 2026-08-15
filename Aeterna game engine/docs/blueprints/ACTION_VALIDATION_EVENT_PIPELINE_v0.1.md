# AETERNA – ACTION / VALIDATION / EVENT PIPELINE BLUEPRINT

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** architecture blueprint / production-foundation generalization
- **Javasolt repository-útvonal:** `Aeterna game engine/docs/blueprints/ACTION_VALIDATION_EVENT_PIPELINE_v0.1.md`
- **Repository-bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Nem engine rewrite terv.**
- **Cél:** a már működő production contractot hosszú távú invariánsokká emelni.

---

# 1. Fő döntés

A jelenlegi public API család megtartandó:

```text
CreateMatch
GetPlayerSnapshot
ListLegalActions
SubmitAction
GetEvents
GetMatchResult
```

Nincs szükség új command busra vagy külön AI/network action API-ra.

Minden consumer:
- Godot;
- headless;
- AI;
- későbbi network

ugyanerre a semanticsra épül.

---

# 2. Canonical pipeline

```text
[External decision]
        ↓
0. Request envelope / schema
        ↓
1. Match + actor identity
        ↓
2. State-version guard
        ↓
3. Engine-issued ActionId lookup
        ↓
4. ActionType + payload-shape validation
        ↓
5. Current availability / pending-decision authority
        ↓
6. Domain preflight
        ↓
7. Final selection/target/payment/timing validation
        ↓
8. Immutable transition/effect plan
        ↓
9. Atomic commit
        ↓
10. State invariant validation
        ↓
11. Committed EngineEvent materialization
        ↓
12. Trigger/consequence discovery
        ↓
13. Additional committed events/pending state
        ↓
14. Viewer projection
        ↓
15. ActionResponse + event stream
```

Egyszerű actionnél 6–8 összevonható.

Az invariáns fontosabb, mint a class count.

---

# 3. Három külön object semantics

## ActionRequest
A player/agent döntési intentje.

## Pending Resolution / Timing Context
Olyan szabályállapot, amely még nincs végleg feloldva:
- reaction entry;
- pending trigger;
- target/choice;
- payment selection.

## EngineEvent
Megtörtént, committed history fact.

E hármat nem szabad összemosni.

---

# 4. LegalAction mint capability token

A LegalAction:

- current state-bound;
- actor-bound;
- engine-issued;
- ordered;
- payload contractot ad;
- enabled/disabled reasont adhat.

Nem:
- state mutation;
- event;
- permanent command definition.

---

# 5. Action ID és option ID

## Action ID
A current action family instance.

Tartalmazhat state/turn/phase/player contextet.

## Option ID
Egy action payloadon belüli engine-issued választás.

Példa:
- pending trigger ID;
- reaction option ID;
- future ordering choice ID.

## Szabály

List index nem stable identity.

---

# 6. Validation ownership

Közös typed rule primitive-et használjon:

```text
LegalAction enumeration
Final request validation
Resolution revalidation
```

Ne legyen három eltérő rules implementation.

A legal action az előzetes nézet.

A final validation mindig authoritative.

---

# 7. Complex plan-before-commit

Kötelező candidate olyan actionre, ahol több state elem változik:

- card + payment;
- targets;
- reaction stack;
- combat;
- replacement;
- multi-zone effect.

Plan legyen:
- immutable vagy commit alatt nem változó;
- teljesen validált;
- deterministic order;
- minden szükséges source/target identityval.

---

# 8. Atomic reject

Minden normál request rejection:

```text
StateVersionBefore == StateVersionAfter
no committed EngineEvent
no partial zone/payment/activity mutation
```

A diagnostic önmagában nem state event.

---

# 9. Request ID

## Current
Correlation ID.

## Online future
Idempotency key candidate.

A semantic változást dokumentálni kell; nem állítjuk, hogy current EngineSession exactly-once.

---

# 10. Diagnostic model

## Local/current
A jelenlegi rich `EngineDiagnostic` megmarad.

## Online boundary előtt
Public projection:

```text
PublicDiagnostic
- code
- category
- safe_message
- retry_policy
- safe_details
```

Developer details server/debug oldalon.

---

# 11. Event architecture

Internal event:

```text
EventId
EventSequence
EventType
MatchId
StateVersion
TurnNumber
ActorPlayerId
CauseActionType
Visibility/Projection metadata
Payload
```

Current foundation megtartandó.

---

# 12. Event causality vNext – candidate

Reaction/replay miatt általánosítható:

```text
CauseActionId?
ParentEventId?
OriginatingEventId?
ResolutionId?
PendingWindowId?
```

Ne legyen kötelező mind.

Migration:
- meglévő payload correlation maradhat;
- új top-level metadata csak akkor kerüljön be, amikor legalább két subsystem ténylegesen használja.

---

# 13. Projection policy vNext – candidate

Fogalmilag külön:

```text
AudiencePolicy
PayloadProjectionPolicy
```

Példa:

```text
zone_move
Audience = public
Payload = owner/full, opponent/redacted
```

A current hardcoded projection működik.

Registry/policy refactor csak a Reaction/Jel/spectator scope növekedésekor.

---

# 14. Event existence confidentiality gate

Default candidate:
- event existence public, payload redacted.

Ha official rules később azt igényli, hogy már az event létezése is titkos:
- új viewer cursor/projection sequence design kell.

Addig nincs szükség rá.

---

# 15. Event classes – későbbi metadata

Candidate:

```text
gameplay
timing
lifecycle
system
```

Debug diagnostic továbbra sem gameplay event.

Ez replay/UI filteringre hasznos, de nem azonnali refactor.

---

# 16. Trigger/consequence boundary

Committed event lehet trigger source.

```text
committed event
→ canonical trigger discovery
→ pending trigger / consequence event
```

Reaction esetén:
- declaration lehet saját event, ha rules fact;
- unresolved effect entry nem committed effect event.

Replacement:
- proposed transitiont interceptálja;
- nem utólag javít committed eventet.

---

# 17. Pending-decision exclusivity

V1:

```text
at most one externally blocking decision authority
```

Lehetséges typed state:
- PendingTriggerWindow;
- ReactionWindow;
- later PendingChoice.

Nested systems coordinatorral jöhetnek később.

---

# 18. Consumer matrix

| Consumer | Snapshot | Legal actions | Submit | Events | Full state |
|---|---:|---:|---:|---:|---:|
| Godot player UI | viewer | yes | yes | viewer | no |
| Fair AI | viewer/AI encoding | yes | yes | optional viewer | no |
| Network player | viewer | yes | yes | viewer | no |
| Replay verifier | canonical/trusted | replay commands | internal | canonical | controlled |
| Debug analyzer | debug | optional | controlled | debug | yes |

---

# 19. Future internal refactor gate

Később indokolt lehet action handler registry, ha:

- action switch túl nagy;
- payload validator túl nagy;
- legal/enforcement drift jelentkezik;
- plugin/module action family kell.

Lehetséges interface:

```text
ActionRule
- Enumerate
- ValidatePayload
- BuildPlan
- Commit
```

**Nem prerequisite a Reaction v1-hez.**

---

# 20. Acceptance invariants minden új action familyre

1. deterministic legal action ordering;
2. state-bound identity;
3. wrong actor disabled/rejected;
4. stale state rejected;
5. malformed payload rejected;
6. final rules preflight;
7. no partial mutation on reject;
8. committed state validates;
9. events contiguous/deterministic;
10. player projection safe;
11. debug projection full;
12. same consumer semantics UI/AI/network.

---

# 21. Reaction kapcsolat

A Reaction blueprint D1–D5 döntései e pipeline-ba illeszkednek:

```text
react/pass_priority
→ legal action
→ ActionRequest
→ final window/priority validation
→ ReactionStack plan
→ commit entry/pass transition
→ timing events
→ projection
```

Resolution külön internal transition/pending lifecycle lehet.

---

# 22. Multiplayer kapcsolat

Network host:
- envelope/auth/idempotency;
- majd ugyanaz az Engine `ActionRequest`.

Ne legyen network-only rules validation.

---

# 23. AI kapcsolat

AI:
- same legal action IDs;
- same SubmitAction;
- no fallback.

Feature encoder nem változtat action semanticsot.

---

# 24. Replay kapcsolat

Replay:
- normalized accepted ActionRequest/decision identity;
- canonical event/outcome stream;
- state/RNG fingerprints.

UI input nem replay command.

---

# 25. Változásnapló

## 0.1 – 2026-08-15

- current production action/event model generalized;
- layered validation pipeline rögzítve;
- ActionRequest / PendingResolution / EngineEvent különválasztva;
- diagnostic/idempotency future boundary rögzítve;
- event projection és causality bővítési kapu rögzítve;
- unnecessary immediate refactor elutasítva.
