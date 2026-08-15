# AETERNA – uoftcprg/pokerkit ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott state-machine / operation-history / replay source audit
- **Javasolt repository-útvonal:** `learning/analyses/uoftcprg__pokerkit.md`
- **Repository:** `uoftcprg/pokerkit`
- **Vizsgált branch:** `main`
- **Vizsgált commit:** `5841c0afe4d6eb71ae5db0f8a6a376ee3e329afb`
- **Fő technológia:** Python
- **Licenc:** MIT
- **Elsődleges AETERNA-érték:** explicit domain state, can/perform operation pattern, append-only typed operation history, action-notation replay, automation boundary, scenario/unit tests
- **Vizsgálati korlát:** teljes poker rules audit, teljes parser/protocol audit és lokális tesztfuttatás nem történt
- **Nem AETERNA-szabályforrás.**

---

# 1. Vizsgálati cél

A cél annak feltárása volt, hogyan működik egy tisztán domain-központú kártyajáték-szimulációs library:

- explicit State modellel;
- validált operationökkel;
- automationnel;
- operation historyval;
- hand-history exporttal;
- historyból újraépített state-sorozattal;
- tesztelt rules state transitionökkel.

---

# 2. Vizsgált fő source-ok

| Terület | Fájl |
|---|---|
| domain state | `pokerkit/state.py` |
| operation model | `pokerkit/state.py` |
| history / replay notation | `pokerkit/notation.py` |
| state tests | `pokerkit/tests/test_state.py` |
| notation tests | `pokerkit/tests/test_notation.py` |
| simulation docs | `docs/simulation.rst` |

---

# 3. Explicit domain State

A `State` nem UI objektum.

Explicit mezőkben tartja többek között:

- deck;
- board;
- muck/burn/discard;
- player status;
- bets/stacks/payoffs;
- hole cards és visibility statusok;
- current street;
- runout state;
- all-in/folded/game status;
- operation history.

A lifecycle és a rules data tehát explicit domain state.

## AETERNA-következtetés

Erős clean-domain referencia.

A Godot-tól független `Aeterna.Engine` irányát támogatja.

---

# 4. Typed immutable Operation modell

Az abstract `Operation` frozen dataclass.

Minden konkrét state update saját type:

- AntePosting;
- BetCollection;
- HoleDealing;
- BoardDealing;
- Folding;
- CheckingOrCalling;
- CompletionBettingOrRaisingTo;
- ChipsPushing;
- stb.

Az operation:

> egyetlen poker state update/change leírása.

A State:

```text
operations: list[Operation]
```

append-only listát tart.

Az `_update(operation)` minden végrehajtott operationt hozzáadhat ehhez.

## AETERNA tanulság

Nagyon erős minta:

```text
state transition
→ typed immutable operation/event record
```

A jelenlegi AETERNA typed canonical/internal event iránya ezzel kompatibilis.

---

# 5. Legal action / can-perform minta

A State sok művelethez külön:

```text
can_...
perform...
```

szerkezetet használ.

A `HandHistory.state_actions` is ezeken keresztül dönti el, mely automatikus operation hajtható végre.

A unit tesztek illegális állapotban `ValueError` rejectet várnak több operationnél.

## AETERNA-következtetés

A `ListLegalActions` + `SubmitAction` szétválasztás jó irány.

Különösen fontos:

- availability/preflight;
- execution előtt rules validation;
- kontrollált reject.

---

# 6. Automation boundary

Az `Automation` enum megmondja, mely engine-lépéseket nem akarja a caller manuálisan kezelni.

Példák:

- ante posting;
- bet collection;
- dealing;
- showdown-related steps;
- chips pushing/pulling.

A HandHistory replay loop:

1. megpróbálja a következő explicit actiont;
2. ha az még nem hajtható végre, automatikus rules operationöket hajt végre;
3. minden transition után state-et yieldel;
4. addig folytatja, amíg a state/action sor konzisztensen feldolgozható.

## Erős AETERNA-minta

```text
engine advances deterministic internal work
→ stops at external decision
→ consumes decision
→ advances again
```

Ez közvetlenül támogatja a blueprint-program `advance-until-input` patternjét.

---

# 7. Operation history → portable HandHistory

`HandHistory.from_game_state(...)` a `state.operations` listát végigjárja és text action historyt állít elő.

A dealing operationöket szükség esetén tömöríti.

A history tartalmazhat:

- variant;
- setup;
- starting stacks;
- player actions;
- explicit dealt cards;
- metadata.

A `dumps()` text reprezentációt készít.

## AETERNA-következtetés

A replay/export formátum nem kell, hogy belső object serialization legyen.

Lehet stabil, verziózott command/event notation.

---

# 8. HandHistory → state stream

`HandHistory` iterable `State` objektumokra.

A `state_actions`:

- új initial state-et hoz létre;
- explicit actionokat parse-ol;
- automatikus operationökkel kitölti a rules-driven lépéseket;
- minden lépés után state-et yieldel;
- ha a history nem reprodukálható/repairable, hibával lezár.

Ez valódi replay-szerű state reconstruction.

## AETERNA candidate

Replay verification:

```text
replay header/setup
+ accepted player decisions
+ deterministic internal engine
→ reconstructed state/event sequence
```

---

# 9. Fontos determinism-korlát

A PokerKit `State._setup()` a Python globális:

```python
shuffle(self.deck_cards)
```

függvényt használja.

A State-ben nem látható explicit seed/PRNG continuation state.

## Következmény

A puszta:

```text
initial rules configuration
+ player action list
```

nem bizonyítottan elég ugyanazon hidden deck order újrateremtéséhez.

## Mi teszi mégis replay-képessé a HandHistoryt?

A history explicit dealing actionokat is tartalmazhat konkrét card identityval.

Ez a random outcome-ot az operation/history szinten materializálja.

## AETERNA-következtetés

Két érvényes replay-stratégia létezik:

### A – deterministic RNG state replay
- seed + PRNG state;
- player commands;
- engine újraszámolja random outputot.

### B – outcome-materialized replay
- a canonical history tárolja a random eredményt is.

AETERNA számára a legerősebb modell várhatóan:

```text
seed/PRNG state
+ accepted commands
+ canonical random outcome events
```

így auditálható és reprodukálható is.

---

# 10. Operation mint audit log vs event sourcing

A PokerKit operation listája erős audit trail.

De a jelen targeted audit alapján nem kell azt állítani, hogy a teljes State kizárólag operation replayből származik futás közben.

A State közvetlenül mutálódik, majd Operation record keletkezik.

## AETERNA tanulság

Fontos különbség:

```text
event-recorded state machine
≠
strict event-sourced aggregate
```

AETERNA-nak nem kell event-sourcing architektúrát bevezetnie csak azért, hogy jó replaye legyen.

---

# 11. Scenario és real-hand tesztelés

A repository nagy `test_state.py` állománnyal rendelkezik.

A tesztek:

- invalid state constructiont;
- illegal operationöket;
- konkrét all-in/side-pot flowkat;
- sok rules edge case-et

vizsgálnak.

Külön WSOP valós hand scenario testek is vannak.

## AETERNA-következtetés

A célzott rules scenario fixture továbbra is magas értékű:

```text
setup
→ exact action sequence
→ intermediate asserts
→ terminal asserts
```

Különösen Reaction/Combat/Replacement esetén.

---

# 12. Amit érdemes átvenni elvi mintaként

1. pure domain State;
2. typed immutable operation record;
3. append-only operation history;
4. can/preflight + operation;
5. rules automation külön controllable policy;
6. action history export;
7. historyból state-stream reconstruction;
8. scenario/real-case tests;
9. portable notation és metadata;
10. event-recorded, de nem feltétlen strict event-sourced modell.

---

# 13. Amit nem szabad közvetlenül átvenni

1. poker-specifikus state modell;
2. player-index identity;
3. Python exception API mint public contract;
4. global RNG;
5. text parser mint authoritative online request protocol;
6. automatikus history repair AETERNA authoritative replayben.

AETERNA replayben invalid history inkább explicit verification failure legyen.

---

# 14. AETERNA replay candidate

## Header

```text
ReplayFormatVersion
EngineVersion
RulesSourceVersion
CanonicalDataFingerprint
MatchSeed
InitialSetupFingerprint
StartingPlayerId
Player/deck fingerprints
```

## Command/decision stream

```text
sequence
request/action type
actor
state version before
public payload / canonical normalized decision
```

## Canonical outcomes

```text
event sequence
random outcomes
zone moves
resolution correlation
post-transition state hash optional
```

## Verification

Replay során:

```text
initial state
→ command
→ engine transition
→ compare expected event/state hash
→ next
```

Mismatch:
`REPLAY_DIVERGENCE`

---

# 15. Döntés

- **Pure state-machine érték:** P0
- **Operation history érték:** P0
- **Replay/notation érték:** P0
- **Scenario testing érték:** P0
- **Deterministic RNG érték:** negatív/hiányos evidence
- **Közvetlen dependency:** nem szükséges
- **Clean-room elvi használat:** igen
- **Teljes későbbi audit:** AI/protocol/simulation területen opcionális.
