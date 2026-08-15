# AETERNA – heroiclabs/nakama ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott authoritative-match/runtime/presence/message source audit
- **Javasolt repository-útvonal:** `learning/analyses/heroiclabs__nakama.md`
- **Repository:** `heroiclabs/nakama`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `1cec7d4bba2dd2542cff59ebd97cef3a693098fe`
- **Commit dátuma:** 2026-08-05
- **Fő technológia:** Go server + runtime modules
- **Licenc:** Apache-2.0
- **Elsődleges AETERNA-érték:** authoritative match host, serialized match call queue, match/user/session/presence identity, join authorization, input queue, targeted reliable/unreliable broadcast
- **Vizsgálati korlát:** kliens SDK-k, cluster/storage/session reconnect teljes stack és runtime language-ek teljes auditja nem történt
- **Nem AETERNA-rules authority és nem backend-választási döntés.**

---

# 1. Vizsgálati cél

A cél annak feltárása volt, hogyan hosztol egy production game backend authoritative match runtime-ot:

- match identity;
- state ownership;
- serialized callback lifecycle;
- user/session/presence identity;
- join attempt;
- input message queue;
- tick;
- targeted broadcast;
- overload/failure;
- authoritative match discovery/state access.

---

# 2. Vizsgált source-ok

| Terület | Fájl |
|---|---|
| runtime match callbacks | `server/runtime_go_match_core.go` |
| serialized match host | `server/match_handler.go` |
| match registry / join / send | `server/match_registry.go` |

---

# 3. Explicit authoritative match

A match stream mode explicit:

```text
StreamModeMatchAuthoritative
```

A match registry API az authoritative flaget, tick rate-et, handler nevét és presence size-ot is publikálja.

## AETERNA tanulság

Az online hostnak világosan meg kell mondania:

- mely process/node birtokolja a match-et;
- mely EngineSession instance authoritative;
- mi a match ID.

Kliens oldali shadow state nem authority.

---

# 4. Match state lifecycle

`RuntimeGoMatchCore.MatchInit`:

```text
runtime.Match.MatchInit
→ state + tickRate + label
```

A state nem lehet nil.

A következő callbackek mind:

```text
old state
→ callback
→ new state
```

mintát követnek:

- MatchJoinAttempt;
- MatchJoin;
- MatchLeave;
- MatchLoop;
- MatchTerminate;
- MatchSignal.

## Tanulság

A network runtime lehet opaque host a domain engine körül.

AETERNA esetén a hosted state lehet:

```text
EngineSession / serialized MatchHostState reference
```

de a game semantics a C# engine-ben marad.

---

# 5. Serialized match call queue

A `MatchHandler` külön channelokat tart:

- call;
- join attempt;
- signal;
- input data;
- deferred output.

Egy goroutine serializáltan dolgozza fel a match callbackokat.

A tick is ugyanebbe a call queue-ba kerül.

## Erős tanulság

Network concurrency ne érje közvetlenül párhuzamosan a MatchState-et.

AETERNA online host candidate:

```text
concurrent sockets
→ per-match command queue
→ serial EngineSession mutation
```

Ez kiegészíti, nem helyettesíti a `expected_state_version` guardot.

---

# 6. Match identity

Authoritative match ID:

```text
UUID + node
```

A registry ellenőrzi, hogy a match az adott node-on él-e.

## AETERNA candidate

Online match identity külön a local in-memory ID-tól:

```text
NetworkMatchId
HostingNodeId
EngineMatchId
```

Kis rendszerben lehet 1:1, de a fogalmi határ hasznos.

---

# 7. User vs session vs presence

`MatchDataMessage` külön tart:

- UserID;
- SessionID;
- Username;
- Node;
- OpCode;
- Data;
- Reliable;
- ReceiveTime.

`MatchPresence` is user + session + node identitást hordoz.

## AETERNA tanulság

Nem szabad feltételezni:

```text
user == connection == player seat
```

Account, session, network presence és engine player binding külön.

---

# 8. Join attempt authoritative callback

A registry:

1. megtalálja a match-et;
2. ellenőrzi, hogy a session már presence-e;
3. join attemptot queue-z;
4. MatchJoinAttempt megkapja:
   - user ID;
   - session ID;
   - username;
   - session expiry;
   - vars;
   - client IP/port;
   - node;
   - metadata;
5. runtime state + allow/reason tér vissza;
6. csak allow után jön presence/join.

## AETERNA candidate

```text
network authenticated identity
→ match seat eligibility
→ Engine/player binding
→ join
```

A join attempt maga is authoritative state transition lehet, ha reconnect/seat state-et módosít.

---

# 9. Match input queue

Incoming match data:

```text
QueueData
→ bounded inputCh
→ MatchLoop drains current queue
→ runtime receives []MatchData
```

Ha input queue full, a message dropolható warninggal.

## AETERNA fontos korrekció

Kártyajáték action requestet **nem szabad csendben eldobni** mint semleges UDP inputot.

AETERNA reliable gameplay commandhoz:

- request ID;
- ack/reject;
- state version;
- timeout/retry/idempotency

szükséges.

Nakama queue pattern jó concurrency isolation, de a drop policy nem jó canonical TCG actionre.

---

# 10. Tick és turn-based engine

Nakama fixed tick rate 1–60 Hz.

MatchLoop tickenként fut, input batchtel.

## AETERNA döntés

Az AETERNA rules engine nem igényel frame/tick simulation authorityt.

Network host azonban használhat:
- timers;
- disconnect grace;
- heartbeat;
- timeout.

Gameplay transition továbbra is action/event driven.

---

# 11. Targeted broadcast

Runtime broadcast:

- optional recipient presence list;
- validates session IDs;
- filters target presences against actual match membership;
- sender identity validálható;
- reliable flag támogatott.

## AETERNA tanulság

Viewer-specific projection után a transport:

```text
player-specific payload
→ exact bound session/presence recipients
```

A broadcast API önmagában nem hidden-info safe.

A payload/projection policy marad engine/app responsibility.

---

# 12. Reliable vs unreliable

Match data `Reliable` flaget hordoz.

## AETERNA candidate

Canonical gameplay:
- action request;
- state snapshot;
- authoritative event

megbízható deliveryt igényel.

Unreliable csak:
- cosmetic telemetry;
- cursor/presence;
- nem-authoritative UX signal

jellegű jövőbeli adatra.

---

# 13. Overload és failure

Bounded:
- call queue;
- join queue;
- input queue;
- deferred broadcast queue.

Súlyos call processing overloadnál a match leállhat és klienseket bont.

Input overflow esetén data message drop lehet.

## AETERNA candidate

Online host:
- bounded queue;
- metrics;
- backpressure;
- controlled disconnect/error.

De canonical requestet ne silently dropoljon.

---

# 14. GetState és admin/debug

Registry képes authoritative match state stringet és presence listát lekérni queue-n keresztül.

Ez admin/debug concern.

## AETERNA tanulság

Full authoritative state diagnostic API ne legyen player-facing.

---

# 15. Amit érdemes átvenni elvi mintaként

1. explicit authoritative match host;
2. per-match serialized mutation queue;
3. match/user/session/presence identity;
4. authoritative join attempt;
5. bounded queues/backpressure;
6. state-in/state-out callback model;
7. targeted recipient validation;
8. reliable/unreliable transport distinction;
9. hosting node/match registry boundary;
10. debug state külön player protocoltól.

---

# 16. Amit nem kell átvenni

1. fixed tick rules engine;
2. Go runtime;
3. opaque opcode payload mint AETERNA public action contract;
4. input overflow silent drop canonical gameplayhez;
5. full Nakama backend;
6. arbitrary runtime match state mint rules authority.

---

# 17. Döntés

- **authoritative host érték:** P0
- **concurrency/queue érték:** P0
- **identity érték:** P0
- **join/presence érték:** P0
- **transport érték:** P1
- **direct dependency:** nincs döntés
- **clean-room architecture inspiráció:** igen.
