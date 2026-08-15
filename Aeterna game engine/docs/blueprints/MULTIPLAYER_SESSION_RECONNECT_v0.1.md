# AETERNA – MULTIPLAYER / SESSION / RECONNECT BLUEPRINT

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** architecture blueprint / backend-semleges
- **Javasolt repository-útvonal:** `Aeterna game engine/docs/blueprints/MULTIPLAYER_SESSION_RECONNECT_v0.1.md`
- **Production rules authority:** Aeterna.Engine
- **Nem választ konkrét backend technológiát.**

---

# 1. Cél

Előre rögzíteni az online multiplayer réteghatárokat úgy, hogy később:

- saját .NET host;
- Nakama;
- Colyseus;
- más backend

is illeszthető legyen.

---

# 2. Kötelező authority

```text
Aeterna.Engine MatchState
```

marad az egyetlen gameplay authority.

Network:
- transport;
- auth;
- session;
- matchmaking;
- reconnect;
- delivery.

Nem implementálja újra a rules-t.

---

# 3. Identity model – candidate

```text
AccountId
AuthSessionId
ConnectionId
NetworkMatchId
MatchSeatId
EnginePlayerId
ReconnectToken
```

Mapping:
```text
authenticated session
→ match seat
→ engine player
```

A mapping server-side.

---

# 4. MatchHost

Candidate:

```text
NetworkMatchHost
- NetworkMatchId
- EngineSession
- SeatBindings
- SessionBindings
- ReconnectReservations
- CommandQueue
- EventCursors
```

Per-match single mutation queue.

---

# 5. Command flow

```text
network message
→ envelope/schema validation
→ authenticated session lookup
→ match/seat binding
→ enqueue
→ deserialize Engine ActionRequest
→ enforce bound PlayerId
→ EngineSession.SubmitAction
→ store idempotency outcome
→ project response/events
→ send
```

---

# 6. Idempotency

`request_id` authoritative request identity.

Network host:
- bounded recent request-result cache;
- duplicate same request → same ack/result;
- conflicting reuse → reject diagnostic.

Exact cache lifetime később.

---

# 7. State/version flow

Every authoritative response includes enough to correlate:
- state version;
- event sequence cursor.

Client stores:
```text
last_state_version
last_event_sequence
```

Gap:
→ resync request.

---

# 8. Initial join

```text
authenticate
→ matchmaking/seat reservation
→ join authorization
→ bind session to seat/player
→ full viewer snapshot
→ current event cursor
→ client READY
```

---

# 9. Disconnect/reconnect

Disconnect:
```text
connection lost
→ seat enters RECONNECT_GRACE
→ engine player identity preserved
```

Reconnect:
```text
new connection
+ valid reconnect credential
+ authenticated account/session
→ rebind same seat
→ rotate reconnect token
→ full authoritative player snapshot
→ new event cursor baseline
```

Old local client state not trusted.

---

# 10. Hidden information

All gameplay payloads derive from:
- `GetPlayerSnapshot`
- `GetEvents(viewerPlayerId, afterSequence)`

or equivalent future engine projection API.

Transport serializer must not receive full MatchState for client delivery.

---

# 11. Event delivery

V1 candidate:
- reliable ordered transport;
- player-specific events;
- event sequence gap detection.

State snapshot may be sent:
- initial join;
- reconnect;
- explicit resync;
- periodic checkpoint optionally.

Normal flow can be event + targeted snapshot/delta later.

---

# 12. Disconnect policy – intentionally open

Not network architecture decision:

- pause;
- grace duration;
- auto-pass;
- timer;
- forfeit;
- AI substitute.

Later game/product rules decision.

---

# 13. Backpressure

Server:
- bounded per-match command queue;
- per-session rate limit;
- max payload;
- timeout.

Canonical action:
- never silently dropped after accepted transport receipt;
- explicit BUSY/RETRY/REJECT response.

---

# 14. Backend adapter boundary

Concept:

```text
IMultiplayerTransport
ISessionAuthenticator
IMatchDirectory
```

A concrete backend adapter translates to `NetworkMatchHost`.

Do not leak backend-specific Room/Presence objects into `Aeterna.Engine`.

---

# 15. V1 non-goal

- spectator;
- tournament service;
- cross-node migration;
- crash recovery;
- distributed simulation;
- voice/chat;
- friends/social;
- ranking;
- persistent matchmaking rating;
- live patch migration.

---

# 16. Later crash recovery

Uses save/replay blueprint:

```text
latest match checkpoint
+ canonical event/decision suffix
+ seat/session metadata
→ restore
```

Separate milestone.

---

# 17. Acceptance candidate

1. same engine behavior local vs network host;
2. wrong bound PlayerId rejected;
3. stale action rejected;
4. duplicate request not executed twice;
5. hidden info absent;
6. disconnect does not create new engine player;
7. reconnect gets current authoritative state;
8. event gap triggers resync;
9. concurrent client messages serialize per match;
10. network loss cannot partially mutate MatchState.

---

# 18. Technology decision gate later

Only after contract/requirements stable compare:
- own ASP.NET/.NET host;
- Nakama adapter;
- Colyseus adapter;
- others if capability gap.

Criteria:
- C# integration;
- operational complexity;
- persistence;
- scale;
- reconnect;
- auth;
- licensing;
- hosting cost;
- debugging;
- deterministic engine isolation.

No backend selection now.
