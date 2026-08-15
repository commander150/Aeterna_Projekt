# AETERNA – colyseus/colyseus ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott room/session/reconnect/projection source audit
- **Javasolt repository-útvonal:** `learning/analyses/colyseus__colyseus.md`
- **Repository:** `colyseus/colyseus`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `1dcf9e5b3dce8485e4a1a809dd98af9b328da149`
- **Commit dátuma:** 2026-08-10
- **Fő technológia:** TypeScript / Node.js
- **Licenc:** MIT
- **Elsődleges AETERNA-érték:** Room/session lifecycle, seat reservation, authentication, reconnection token, per-client state view, patch sync, message validation/rate limiting
- **Vizsgálati korlát:** a külön `@colyseus/schema` repository teljes belső auditja, matchmaking driver és kliens SDK-k teljes auditja nem történt
- **Nem AETERNA-rules authority és nem közvetlen backend-választási döntés.**

---

# 1. Vizsgálati cél

A cél annak feltárása volt, hogyan kezeli egy production multiplayer framework:

- room/match identity;
- session identity;
- seat reservation;
- authentication;
- join/reconnect/leave;
- per-client state projection;
- full state + patch sync;
- message validation;
- message rate limiting;
- lifecycle/disposal.

---

# 2. Vizsgált fő source-ok

| Terület | Fájl |
|---|---|
| Room lifecycle | `packages/core/src/Room.ts` |
| state serializer | `packages/core/src/serializer/SchemaSerializer.ts` |
| matchmaking/lifecycle kapcsolódás | `packages/core/src/MatchMaker.ts` részleges |

---

# 3. Room mint session host

A `Room`:

- egy konkrét multiplayer session/communication channel;
- saját `roomId`;
- connected client list;
- state;
- metadata;
- lifecycle hookok;
- patch rate;
- optional simulation interval;
- reserved seats;
- reconnect state.

## AETERNA tanulság

Későbbi online rétegben külön:

```text
NetworkMatchHost
- MatchId
- Seats
- Sessions
- Connections
- EngineSession
```

A network host ne maga legyen a rules engine.

---

# 4. Identity rétegek

Colyseus explicit különválaszt:

- room ID;
- session ID;
- authentication data/user identity;
- private reconnection token;
- client connection object.

Reconnectionkor az új connection:

- visszakapja a korábbi auth/userData/view state-et;
- a régi client reference átvezethető az új transport refre;
- új private reconnection token keletkezik.

## AETERNA candidate

Külön identityk:

```text
PlayerAccountId      # hosszú életű user/account
MatchPlayerId        # engine player ID / seat
NetworkSessionId     # adott bejelentkezési/network session
ConnectionId         # transport connection
ReconnectCredential  # rövid életű secret
```

Ezeket nem szabad egyetlen `player_id` mezőbe összemosni.

---

# 5. Seat reservation

A framework room join előtt seat reservationt használ:

- session ID;
- join options;
- auth data;
- consumed flag;
- reconnect flag;
- timeout.

A max player countnál a reserved seat is számít.

## AETERNA tanulság

Matchmaking seat és engine player slot külön lifecycle.

```text
match found
→ seat reserved
→ auth/join
→ engine seat binding
```

Disconnectkor a seat ideiglenesen fenntartható reconnecthez.

---

# 6. Authentication boundary

`onAuth` a `onJoin` előtt fut.

A client auth data külön tárolódik.

Async auth alatt disconnectet is kezel.

## AETERNA candidate

Online command actor identityt nem client payloadból kell elhinni.

Transport/auth layer:

```text
connection/session
→ authenticated account
→ bound match seat
→ engine PlayerId
```

A client requestből érkező `player_id` csak a bound identityval egyezve fogadható el.

---

# 7. Reconnection lifecycle

A `allowReconnection`:

- csak valóban joined clientre;
- timeoutos vagy manual;
- duplicate reconnect request ellen véd;
- private reconnection token;
- seat reservation;
- reconnect attempt handling network switch/stale old connection esetén;
- cleanup timeout/resolve/reject után.

A reconnect:
- ugyanazon session/seat continuityt célozza;
- új connectiont köt a logikai clienthez;
- auth/userData/view átvihető.

## AETERNA tanulság

Reconnect nem „új player join”.

Külön:

```text
disconnect
→ grace state
→ authenticated reconnect
→ seat continuity
→ resync authoritative current viewer state
```

---

# 8. Per-client StateView

`SchemaSerializer` támogat:

- shared encoded state;
- per-client `StateView`;
- per-client full state;
- per-client patch;
- view-specific cache.

A reconnectelt client `view` state-je is átvihető.

## Erős tanulság

Transport technikailag képes eltérő kliensnézeteket küldeni.

## AETERNA architecture döntés

**A hidden-information authority ne kerüljön át a network serializerbe.**

A C# engine már viewer-safe projectiont ad.

Javasolt:

```text
Engine GetPlayerSnapshot(player)
→ network DTO
→ transport serialization
```

Colyseus-jellegű view layer legfeljebb transport-optimalizáció, nem rules policy.

---

# 9. Full state + incremental patch

Új JOIN_ROOM ack után a server teljes current state-et küldhet.

Futás közben serializer patch-eket küld.

Per-client filterrel a patch is viewer-specific.

## AETERNA candidate

Reconnect/resync:

1. full viewer snapshot;
2. state version;
3. ezután ordered delta/event continuation.

Nem szükséges a kliens korábbi state-jében megbízni.

---

# 10. Message validation

A Room `onMessage`:

- typed message handler;
- optional standard schema validation;
- invalid payloadnál disconnect;
- unknown handler productionban kapcsolat lezárható.

Külön byte-message API is validálható.

## AETERNA tanulság

Network payload validation két réteg:

### Transport/schema
- decode;
- type;
- size;
- envelope.

### Engine/rules
- request ID;
- state version;
- player/priority;
- action ID;
- target/cost legality.

A transport validation nem helyettesíti az EngineSession validationt.

---

# 11. Rate limiting / overload

A client max messages/sec limitet kaphat.

A room:
- patch interval;
- simulation interval;
- auto dispose;
- join timeout.

## AETERNA candidate

Online layerben szükséges:
- per-session rate limit;
- payload size cap;
- request queue cap;
- controlled overload diagnostics.

Turn-based card game miatt agresszív throughput nem kell, de abuse protection igen.

---

# 12. Message vs state-patch ordering

A Room támogat:

```text
broadcast(..., afterNextPatch)
```

tehát egy message explicit a következő state patch után küldhető.

## AETERNA tanulság

State/event ordering a networken is contract.

Később:

```text
stateVersion N snapshot/patch
→ events through sequence X
```

korrelálható legyen.

A client ne dolgozzon fel olyan eventet, amelyhez szükséges state még nincs alkalmazva.

---

# 13. Amit érdemes átvenni elvi mintaként

1. room/session host külön rules engine-től;
2. room ID vs session ID vs reconnect secret;
3. seat reservation;
4. auth-before-join;
5. reconnect grace;
6. reconnect token rotation;
7. full resync + patch continuation;
8. per-view transport capability;
9. payload schema validation;
10. message rate limiting;
11. explicit state/message ordering.

---

# 14. Amit nem kell átvenni

1. Room state mint AETERNA rules authority;
2. Node.js/TypeScript backend;
3. 20Hz/60Hz simulation loop turn-based ruleshoz;
4. serializer filter mint hidden-info authority;
5. generic mutable message handler mint engine action API;
6. framework autoDispose semantics közvetlenül.

---

# 15. Döntés

- **session/reconnect érték:** P0
- **projection transport érték:** P0
- **message validation érték:** P1
- **state sync érték:** P0
- **direct dependency:** nincs döntés, nem szükséges a blueprinthez
- **clean-room architecture inspiráció:** igen.
