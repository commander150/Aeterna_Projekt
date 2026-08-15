# AETERNA – CROSS-PROJECT SYNTHESIS: MULTIPLAYER, SESSION AND RECONNECT

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első multiplayer/session/reconnect synthesis
- **Javasolt repository-útvonal:** `learning/synthesis/topics/multiplayer.md`
- **Nem AETERNA-authority.**

---

# 1. Fő evidence family

Új:
- Colyseus
- Nakama

Korábbi:
- boardgame.io
- Arcomage
- Pali
- Hearthstone.gd
- Seven Card Game

A korábbi Godot multiplayer auditok különösen jó negatív evidence-et adnak hidden-info, scene-tree authority és optimistic mutation hibákra.

---

# 2. P-NET-001 – Network host külön a rules engine-től

**Státusz:** `REPEATED_PATTERN`  
**AETERNA:** `HIGH_CONFIDENCE_CANDIDATE`

```text
Connections/Sessions
        ↓
Network MatchHost
        ↓
Aeterna.Engine EngineSession
        ↓
Viewer Projection
        ↓
Transport
```

A network library nem lesz új rules authority.

---

# 3. P-NET-002 – Identityt több rétegre kell bontani

Külön:
- account/user;
- auth session;
- network connection;
- match seat/player;
- reconnect credential;
- match ID.

AETERNA engine `PlayerId` a match seat/rules identity.

Nem automatikusan account ID.

---

# 4. P-NET-003 – Per-match serialized mutation queue

Nakama erős evidence.

A concurrent socket/input réteg:

```text
concurrent
→ per-match command queue
→ single authoritative mutation stream
```

A state-version/idempotency guard ettől még megmarad.

---

# 5. P-NET-004 – Join/reconnect külön lifecycle

Colyseus:
- seat reservation;
- auth;
- join;
- drop;
- reconnect grace/token;
- leave.

Nakama:
- join attempt;
- allow/reason;
- presence binding.

AETERNA candidate:

```text
MATCH_CREATED
SEAT_RESERVED
JOINED
CONNECTED
DISCONNECTED_GRACE
RECONNECTED
LEFT
FORFEITED/EXPIRED
```

Network presence state nem azonos gameplay turn state-tel.

---

# 6. P-NET-005 – Reconnect authoritative resync

Reconnect után ne a kliens local state-jére építsünk.

Javasolt:

```text
authenticate reconnect
→ recover same match seat
→ current viewer-safe full snapshot
→ state version
→ event continuation cursor
```

A kliens régi pending UI-ja eldobható és újraépíthető.

---

# 7. P-NET-006 – Projection az engine-ben, transport view másodlagos

Colyseus képes per-client state filteringre.

Boardgame.io képes playerView projectionre.

Pali/Hearthstone.gd megmutatja a visual-only hiding veszélyét.

AETERNA current engine már viewer-safe snapshot/event API-t ad.

## Döntési irány

Hidden policy **egyetlen authorityja az engine projection**.

Transport:
- csak azt küldi, amit kapott;
- opcionálisan technikai field filtering/compression.

---

# 8. P-NET-007 – Reliable gameplay command + request identity

Nakama reliable flaget és bounded input queue-t mutat.

AETERNA current ActionRequest már:
- `request_id`;
- `expected_state_version`.

Online layerben ehhez kell:
- server ack/reject;
- retry policy;
- idempotency cache;
- timeout.

Canonical gameplay requestet nem szabad silent dropolni.

---

# 9. P-NET-008 – Full snapshot + ordered continuation

boardgame.io:
- full sync;
- log;
- delta patch.

Colyseus:
- full state joinkor;
- patch thereafter.

AETERNA candidate:

```text
FullPlayerSnapshot
StateVersion N
LastEventSequence X
→ subsequent viewer events/patches X+1...
```

Reconnectnél ez egyszerű és robust.

---

# 10. P-NET-009 – Network event/state ordering explicit

Colyseus `afterNextPatch`.

AETERNA current events:
- sequence;
- state version.

Későbbi protocolnak garantálnia kell:
- mely state versionhöz tartozik event;
- event sequence gap detection;
- resync trigger.

---

# 11. P-NET-010 – Rate limit / backpressure külön a rules rejecttől

Transport abuse:
- message rate;
- payload size;
- queue saturation.

Rules reject:
- stale state;
- wrong actor;
- illegal action.

A kettő külön diagnostics.

---

# 12. Proposed online action envelope

A production `ActionRequest` belseje megmaradhat.

Network envelope candidate:

```text
ProtocolVersion
NetworkMatchId
SessionId / authenticated transport context
EngineActionRequest
ClientEventCursor?
```

A user/player identityt a server session bindingből kell ellenőrizni.

---

# 13. Reconnect credential

A reconnect token:
- secret;
- rotálható;
- rövid életű;
- nem rules identity.

Ne legyen:
- deck ID;
- player ID;
- account token újrahasználva.

---

# 14. Idempotency

Ha kliens timeout után ugyanazt a `request_id`-t újraküldi:

Server candidate:
- ha már processed → ugyanaz az outcome/ack visszaadható;
- ne hajtsa végre kétszer.

Ehhez bounded request-result cache per session/match kellhet.

A jelenlegi local EngineSession request-id semantics auditját külön kell majd ehhez hozzáilleszteni.

---

# 15. Disconnect gameplay policy – rules/product gate

Network layer csak észleli:

- disconnected;
- reconnect timeout.

A game policy külön döntés:

- pause?
- clock continues?
- auto-pass?
- forfeit after timeout?
- AI takeover?

Ezt nem networking framework alapján döntjük el.

---

# 16. Spectator

Későbbi külön projection role:

```text
PLAYER_A
PLAYER_B
SPECTATOR
ADMIN/DEBUG
```

Spectator hidden policy explicit.

V1 online playhoz spectator nem szükséges.

---

# 17. Persistence

Network match host crash recoveryhez később:

```text
Save/checkpoint
+ replay/event suffix
+ session/seat metadata
```

A save/replay blueprinthez kapcsolódik.

Első online slice lehet single-process no-crash-recovery, ha explicit non-goal.

---

# 18. Anti-patternök

| ID | Név |
|---|---|
| `A-NET-001` | network framework state = rules authority |
| `A-NET-002` | account ID = connection = engine player ID |
| `A-NET-003` | client payloadból elhitt player identity |
| `A-NET-004` | hidden projection csak transport/UI filterben |
| `A-NET-005` | concurrent socket handler közvetlen MatchState mutation |
| `A-NET-006` | canonical action silent drop |
| `A-NET-007` | reconnect új playerként |
| `A-NET-008` | reconnect client local state-be vetett bizalom |
| `A-NET-009` | request ID nélküli retry |
| `A-NET-010` | state/event sequence gap detection hiánya |
| `A-NET-011` | unreliable canonical gameplay transport |
| `A-NET-012` | disconnect policy transport layerbe hardcodeolva |

---

# 19. AETERNA multiplayer architecture candidate

```text
Transport Connections
        ↓
Authentication / Session Registry
        ↓
Match Seat Binding
        ↓
Per-Match Command Queue
        ↓
EngineSession
        ↓
PlayerSnapshot / Player Events
        ↓
Per-Session Transport
```

---

# 20. Verdict

A multiplayer/session/reconnect architecture fő iránya blueprintképes.

Nem szükséges most eldönteni, hogy Colyseus, Nakama vagy saját host lesz-e a konkrét backend.

Az architecture úgy tervezendő, hogy a transport/backend cserélhető legyen az EngineSession fölött.
