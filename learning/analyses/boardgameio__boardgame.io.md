# AETERNA – boardgameio/boardgame.io ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott authoritative-state / determinism / log / projection source audit
- **Javasolt repository-útvonal:** `learning/analyses/boardgameio__boardgame.io.md`
- **Repository:** `boardgameio/boardgame.io`
- **Vizsgált branch:** `main`
- **Vizsgált commit:** `5e9a2c94bde803fae8b081958c406c4d0a7be8ae`
- **Fő technológia:** TypeScript / JavaScript / Redux-szerű state reducer
- **Licenc:** MIT
- **Elsődleges AETERNA-érték:** authoritative server state, stale-state guard, deterministic PRNG state, delta log, player-specific state/log projection, reconnect/sync
- **Vizsgálati korlát:** build/test lokális futtatás nem történt; a teljes framework API, lobby és minden storage backend nem került mély auditba
- **Nem AETERNA-szabályforrás és nem közvetlen dependency-javaslat.**

---

# 1. Vizsgálati cél

A cél annak feltárása volt, hogy egy általános turn-based game framework hogyan kezeli:

- authoritative state-et;
- state transitiont;
- stale client actiont;
- random állapot determinisztikus folytatását;
- log/deltalog réteget;
- undo/redo state snapshotokat;
- player-specific projectiont;
- hidden log-redactiont;
- reconnect/sync állapotot;
- teljes state vs delta patch transportot.

---

# 2. Vizsgált fő source-ok

| Terület | Fájl |
|---|---|
| state reducer / transition | `src/core/reducer.ts` |
| authoritative server | `src/master/master.ts` |
| player projection | `src/master/filter-player-view.ts` |
| projection tests | `src/master/filter-player-view.test.ts` |
| random plugin | `src/plugins/plugin-random.ts` |
| PRNG state | `src/plugins/random/random.ts` |
| random tests | `src/plugins/random/random.test.ts` |

---

# 3. Authoritative server boundary

A `Master` dokumentáltan:

> runs the game and maintains the authoritative state.

A kliens actiont küld a szervernek.

Az `onUpdate`:

1. ellenőrzi az action shape-et;
2. csak public client action típust enged;
3. autentikálhat;
4. ellenőrzi az engedélyezett game eventet;
5. betölti az authoritative state-et;
6. ellenőrzi game-over státuszt;
7. ellenőrzi active player jogosultságot;
8. ellenőrzi a move elérhetőségét;
9. összeveti a kliens `stateID`-ját az authoritative `_stateID`-val;
10. reduceren futtatja az actiont;
11. broadcastolja a state-et vagy patch-et;
12. perzisztálja az új state-et és deltalogot.

## AETERNA-következtetés

Ez közvetlenül megerősíti a már alkalmazott:

```text
request
+ expected state version
→ authoritative validation
→ transition
→ state version increment
→ event/projection
```

mintát.

Az AETERNA `expected_state_version` jelenlegi iránya megtartandó.

---

# 4. Reducer mint transition boundary

A `CreateGameReducer` külön kezeli:

- GAME_EVENT;
- MAKE_MOVE;
- PLAYER_LEAVE;
- RESET/UPDATE/SYNC;
- UNDO/REDO;
- plugin action;
- patch.

MOVE esetén a flow előbb ellenőrzi, hogy a move az adott state-ben elérhető-e.

A move `INVALID_MOVE` eredménnyel atomikusan elutasítható.

Plugin flush/validation hiba esetén a reducer a korábbi state-re épített error state-et adja vissza.

Sikeres move/event után `_stateID` nő.

## Tanulság

A transition boundary:

- validálható;
- state-versioned;
- logolható;
- plugin validation után commitolható.

Ez jó architecture-minta, még ha AETERNA konkrét typed C# contractja más is.

---

# 5. Deltalog

Minden releváns actionhöz log entry készülhet:

```text
action
_stateID
turn
phase
metadata?
redact?
```

A log nem azonos a teljes state-tel.

A reducer actiononként `deltalog`-ot épít, a `Master` pedig:

- state nélkül külön is perzisztálja;
- client update mellé továbbíthatja;
- reconnect/sync során a teljes logot visszaadhatja.

## AETERNA-következtetés

Hasznos rétegkülönbség:

```text
authoritative state
≠
transition/event history
≠
viewer-specific history
```

A jelenlegi AETERNA belső event store már jó alap erre.

A későbbi replay rétegnek nem szükséges a teljes MatchState-et minden transitionnél másolnia, ha a determinisztikus újrajátszás feltételei teljesülnek.

---

# 6. State ID és stale request

A szerver explicit összeveti:

```text
client stateID
vs
authoritative state._stateID
```

Mismatch esetén action reject, kivéve explicit `ignoreStaleStateID` move policyt.

## Pozitív tanulság

A stale guard elsőrendű protocol concern.

## AETERNA-korrekció

AETERNA-nál a state-version bypass alapértelmezett gameplay actionre nem javasolt.

Ha valaha kell stale-toleráns command, külön, szűk semantics és proof szükséges.

---

# 7. Undo / redo snapshot history

A reducer state részeként `_undo` / `_redo` listát tart.

Egy undo entry:

- G;
- ctx;
- plugin state;
- player ID;
- move type

adatokat őriz.

Az undo/redo teljes state-szeletet állít vissza, nem esemény-visszafordítást számol.

## AETERNA-következtetés

Ez jó bizonyíték arra, hogy:

- snapshot history egyszerű és robusztus lehet;
- event replay és user-visible undo két külön feature;
- production TCG-ben az undo nem feltétlen gameplay feature.

AETERNA számára inkább debug/replay checkpointként lehet értékes.

---

# 8. Determinisztikus PRNG state

A random subsystem külön `RandomState`-et tárol:

```text
seed
prngstate
```

Minden random hívás:

1. az előző PRNG state-ből indul;
2. előállítja a következő értéket;
3. visszaírja az új PRNG state-et.

A plugin `flush` az új RNG state-et perzisztálja.

A random plugin player viewja az RNG state-et nem küldi ki a kliensnek.

A tesztek fix seed esetén konkrét értékeket assertálnak, és azt is ellenőrzik, hogy a PRNG state nem kerül player viewba.

## AETERNA számára erős candidate

```text
MatchRandomState
- Seed
- GeneratorState / Counter
```

A random output ne globális RNG mellékhatás legyen.

A seed önmagában nem mindig elég; a continuation state is first-class.

---

# 9. Client optimism és random

Ha move random API-t használ, a plugin `NoClient` megakadályozza, hogy a kliens optimistán materializálja a random eredményt.

A teszt explicit ellenőrzi:

- server reducerben a random move eredményt ad;
- client reducerben ugyanaz a random move nem materializálja a titkos/random state-et.

## AETERNA tanulság

Ha később online kliensprediction lenne:

- random/hidden-dependent transition ne fusson authoritative-ként kliensen;
- a viewer ne kapja meg a PRNG belső state-et.

---

# 10. Player-specific state projection

`applyPlayerView`:

- a game state `G` részét `game.playerView` segítségével szűri;
- plugin state-eket player view alapján szűri;
- deltalogot eltávolítja;
- undo/redo historyt eltávolítja.

Update és patch előtt a transport playerenként alkalmazza ezt.

Delta patch esetén:

```text
authoritative previous state
→ playerView(previous)

authoritative next state
→ playerView(next)

→ patch(filteredPrevious, filteredNext)
```

## Erős AETERNA-minta

Viewer delta mindig viewer-safe state-ek között képződjön.

Ne:

```text
authoritative delta
→ utólag próbáljuk redaktálni
```

Ez különösen fontos hidden hand / Jel / secret choice esetén.

---

# 11. Viewer-specific log redaction

A log action argumentumai move-onként redaktálhatók.

A move-ot végrehajtó player megtarthatja a saját argumentumot, míg más player és spectator `args: null` nézetet kaphat.

## AETERNA-következtetés

A replay/event log sem automatikusan public.

Külön:

```text
InternalEvent
PlayerEventProjection
SpectatorEventProjection
DebugEventProjection
```

policy indokolt lehet.

---

# 12. Reconnect / sync

`onSync` betölti:

- current state;
- metadata;
- full log;
- initial state.

A transport sync objektumot küld.

Ez jó példa arra, hogy reconnecthez nem feltétlen kell a kliens előző helyi állapotában megbízni.

## AETERNA-candidate

Későbbi online mód:

```text
authoritative current snapshot
+ state version
+ viewer-safe event/log continuation
```

legyen a resync alapja.

---

# 13. Fontos projection-kockázat / mélyaudit-jelölt

A vizsgált `filter-player-view.ts` `sync` ágban:

- `syncInfo.state` playerViewt kap;
- `syncInfo.log` redaktálódik;
- a `syncInfo.initialState` mező változatlanul marad a spreadelt objektumban.

A `Master.onSync` az authoritative `initialState`-et is betölti és a syncInfo részeként adja tovább.

## Státusz

`POTENTIAL_HIDDEN_INFO_BOUNDARY_RISK`

Nem állítható általánosan, hogy ez tényleges adatleak minden boardgame.io játékban, mert az `initialState` tartalma game-specifikus.

De ha setup titkos kezdeti adatot tartalmaz, a kódútvonal külön security review-t igényel.

## AETERNA tanulság

**Minden** snapshot/history/baseline elem viewer projectiont igényel, nem csak a current state.

---

# 14. Amit érdemes átvenni elvi mintaként

1. authoritative Master + reducer boundary;
2. stale state ID reject;
3. state transition után monotonic version;
4. action-deltalog külön a state-től;
5. seed + PRNG continuation state;
6. RNG state hidden projection;
7. player-specific state projection;
8. player-specific event/log redaction;
9. viewer-safe statesből képzett delta patch;
10. full resync current state + log;
11. snapshot history és event log külön fogalom.

---

# 15. Amit nem kell átvenni

1. Redux API;
2. JavaScript mutable/loosely typed game payload;
3. generic plugin architecture teljes formája;
4. client-side optimistic move processing;
5. gameplay undo/redo mint kötelező feature;
6. `ignoreStaleStateID` általános kivétel;
7. teljes boardgame.io network stack.

---

# 16. AETERNA blueprint candidate-ek

## Random

```text
DeterministicRandomState
- Seed
- GeneratorState / DrawCounter
```

## Replay

```text
ReplayHeader
- engine/rules/data version
- initial canonical state fingerprint
- random state/seed
- player/deck/setup fingerprints

ReplayEntry[]
- sequence
- accepted request/command identity
- resulting canonical event correlation
- post-state hash optional
```

Ez még synthesis candidate, nem elfogadott spec.

## Projection

Replay/log projection külön policyként kezelendő.

---

# 17. Döntés

- **Authoritative state érték:** P0
- **State-version érték:** P0
- **Determinism/RNG érték:** P0
- **Replay/log érték:** P0
- **Projection érték:** P0
- **Reconnect érték:** P1
- **Közvetlen dependency:** nem szükséges
- **Clean-room architecture inspiráció:** igen
- **Teljes későbbi audit:** különösen multiplayer/reconnect/storage területen indokolt.
