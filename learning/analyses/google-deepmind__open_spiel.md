# AETERNA – google-deepmind/open_spiel ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott game-state / AI / observation / chance / serialization source audit
- **Javasolt repository-útvonal:** `learning/analyses/google-deepmind__open_spiel.md`
- **Repository:** `google-deepmind/open_spiel`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `d7c4fc2dac825cb34b50131042a151b43c12edc5`
- **Vizsgált verzió:** OpenSpiel 2.0.2
- **Fő technológia:** C++ core + Python bindings/environment
- **Licenc:** Apache-2.0
- **Elsődleges AETERNA-érték:** általános Game/State API, legal actions, player-specific observation/information state, chance model, clone/child, serialization, RL environment és bot interface
- **Vizsgálati korlát:** nem történt lokális build/test; a több száz konkrét game implementation és összes algorithm nem került auditálásra
- **Nem AETERNA-szabályforrás és nem production dependency-javaslat.**

---

# 1. Vizsgálati cél

A cél annak feltárása volt, hogy egy általános játék- és AI-framework hogyan választja szét:

- canonical game state;
- current actor;
- legal action space;
- imperfect-information player view;
- perfect-recall information state;
- chance/random node;
- state cloning/search branch;
- history/serialization;
- RL environment;
- bot/agent interface.

---

# 2. Vizsgált fő source-ok

| Terület | Fájl |
|---|---|
| Game/State API | `open_spiel/spiel.h` |
| state transition + serialization | `open_spiel/spiel.cc` |
| RL environment | `open_spiel/python/rl_environment.py` |
| bot interface | `open_spiel/spiel_bots.h` |

---

# 3. Game és State különválasztása

A `Game` statikus/konfigurációs tulajdonságokat képvisel:

- game type;
- dynamics;
- chance mode;
- information type;
- player count;
- action-space tulajdonság;
- utility/reward model;
- observation/info-state support.

A `State` egy konkrét futó game-state.

Ez jó alapminta:

```text
GameDefinition / RulesEnvironment
        ↓
State instance
        ↓
legal actions / observation / transition
```

AETERNA megfelelő:

```text
canonical package + engine rules
        ↓
MatchState
```

Nem szükséges egyetlen „AI game objectbe” másolni a rules logikát.

---

# 4. Current actor és node type explicit

`State::CurrentPlayer()` explicit.

A state type megkülönböztet:

- decision;
- chance;
- terminal;
- mean-field.

Simultaneous dynamics külön modell.

## AETERNA tanulság

A headless interface ne csak azt kérdezze:

```text
whose turn?
```

hanem az authoritative pending state alapján azt:

```text
milyen decision boundary van most?
ki jogosult dönteni?
milyen action family legal?
```

Reaction/Priority esetén ez különösen fontos.

---

# 5. Legal actions first-class API

`LegalActions(player)` minden state-re definiált interface.

Nem-acting playernél üres lista.

OpenSpiel külön `LegalActionsMask` API-t is ad.

Structured action esetén:

- `ValidateActionStruct` nem mutál;
- `ApplyActionStruct` előbb validál;
- invalid esetben a state változatlan.

## AETERNA-következtetés

A meglévő:

```text
ListLegalActions
→ SubmitAction
```

minta közvetlenül alkalmas AI-ra.

AI nem kap külön rules-validator implementationt.

---

# 6. Observation és information state külön fogalom

OpenSpiel külön kezeli:

## Observation

Az adott pillanat player-viewja.

A teljes observation+own-action history elegendő lehet az information state rekonstruálásához.

## Information state

Perfect-recall reprezentáció az adott játékos szemszögéből.

Nem azonos a teljes authoritative state-tel.

Mindkettő lehet:

- string;
- tensor;
- újabban structured representation.

## AETERNA tanulság

Három réteg legyen külön:

```text
Authoritative MatchState        # engine-only
Player Observation              # current visible state
Player Information State        # optional AI/history feature
```

Az első AETERNA AI v1-hez valószínűleg elegendő a player observation + legal actions.

Perfect-recall information state később építhető observation/action historyból vagy külön encoderrel.

---

# 7. Full state csak trusted/debug capability

Az OpenSpiel RL environment `include_full_state` opcióval képes teljes serialized state-et is az observationbe tenni.

Ez explicit opcionális debug/analysis feature.

## AETERNA-következtetés

AI módok:

```text
FAIR_PLAYER
TRUSTED_ANALYZER
DEBUG_FULL_STATE
```

A normál ellenfél-AI kizárólag `FAIR_PLAYER`.

Full MatchState ne kerüljön véletlenül player agenthez.

---

# 8. Chance model explicit

GameType chance mode:

- deterministic;
- explicit stochastic;
- sampled stochastic.

## Explicit stochastic

Az összes chance outcome + probability lekérdezhető.

Az outcome explicit actionként kerül a state-re; maga az ApplyAction determinisztikus.

## Sampled stochastic

A game saját RNG-t tart, az ApplyAction belül mintáz.

## Erős AETERNA-tanulság

AI/simulation szempontból az explicit chance node nagyon erős minta:

```text
chance decision
→ legal outcomes + probabilities
→ selected canonical outcome
→ deterministic state transition
```

Ez könnyebb:
- search;
- replay;
- verification;
- scenario testing.

AETERNA-ban nem szükséges minden random mechanicot player-facing actionná tenni, de internal chance event/transition explicit lehet.

---

# 9. Clone és Child

A State kötelező `Clone()` API-t ad.

`Child(action)`:

```text
clone
→ apply action
→ child state
```

Ez search/planning algoritmusokhoz kiváló.

## AETERNA candidate

Későbbi planning AI számára szükséges lehet:

```text
SimulationState Clone/Fork
ApplyCandidate
Evaluate
```

De ezt nem a public multiplayer `EngineSession` contractba kell feltétlen kitenni.

Lehet trusted headless/simulation API.

---

# 10. History és serialization

A State:

- `history_`;
- `move_number_`;
- optional starting-state string

adatokat tart.

Default state serialization action historyból rekonstruál.

A source külön figyelmeztet:

> sampled stochastic state esetén puszta history nem elég általánosan.

A `Game::Serialize()` sampled stochastic game esetén külön RNG state-et tárol.

`SerializeGameAndState` meta/game/state szakaszokat használ és verziószámot rögzít.

## AETERNA-következtetés

Ez megerősíti a korábbi replay synthesis eredményt:

```text
game/rules/data identity
+ initial state
+ decision history
+ RNG state/outcomes
```

együtt szükséges robust reprodukcióhoz.

---

# 11. RL TimeStep contract

A Python RL wrapper minden reset/step után `TimeStep`-et ad:

- observations;
- rewards;
- discounts;
- step type FIRST/MID/LAST.

Observation:

- playerenként info/observation tensor;
- playerenként legal actions;
- current player;
- optional serialized full state debughoz.

A step:

- turn-based vagy simultaneous action listát fogad;
- opcionális legalitásellenőrzés;
- state transition után automatikusan feldolgozza external chance eventeket;
- a következő decision/terminal boundarynél áll meg.

## AETERNA candidate

A headless AI adapter ne engine-eventenként kényszerítse az agentet dönteni.

Az agent-facing step:

```text
decision → engine advances internal mandatory work → next external decision
```

formát követheti.

---

# 12. Bot interface

A `Bot`:

- `Step(State)` → action;
- opcionális policy distribution;
- `InformAction`;
- `Restart`;
- `RestartAt`;
- `Clone`.

A bot nem authority.

A game State marad rules source.

## AETERNA-következtetés

AI agent interface legyen:

```text
observation + legal actions
→ choice
```

Nem:

```text
AI mutálja MatchState-et
```

Stateful agent fenntarthat saját memóriát, de ez nem canonical rules state.

---

# 13. Structured actions és large action spaces

OpenSpiel 2.0 külön támogat structured actiont olyan játékokra, ahol lapos integer action-space nem skálázódik.

## AETERNA tanulság

A kártyajáték action space természetesen kombinatorikus lehet:

- reaction;
- source;
- target;
- payment;
- order;
- choices.

Ezért AETERNA-nál jobb:

```text
engine-issued legal action option
+ typed payload/selection schema
```

mint egy globális fix numeric action ID minden lehetséges kombinációra.

Ez közvetlenül támogatja a `reaction_option_id` blueprintet.

---

# 14. Amit érdemes átvenni elvi mintaként

1. Game/State szétválasztás;
2. explicit current decision actor;
3. first-class legal action API;
4. no-mutation validation;
5. player-specific observation;
6. observation vs information-state elválasztás;
7. full-state debug külön capability;
8. explicit chance model;
9. clone/child search interface;
10. state/history/RNG serialization;
11. RL TimeStep;
12. agent nem authority;
13. structured action support;
14. step until next external decision.

---

# 15. Amit nem kell közvetlenül átvenni

1. C++ API;
2. flat integer action space;
3. OpenSpiel reward/discount semantics mint AETERNA game rule;
4. mean-field model;
5. teljes algorithm framework;
6. full state serializer formátum;
7. direct dependency.

---

# 16. AETERNA AI/headless candidate

```text
AeternaSimulationEnvironment
- Reset/CreateMatch
- Observe(playerId, mode)
- ListLegalActions(playerId)
- Step(actionRequest)
- IsTerminal
- GetOutcome
```

Fair observation:
- viewer-safe snapshot;
- current pending summary;
- legal actions;
- optional derived feature vector.

Trusted simulation:
- internal clone/fork;
- controlled perfect-information access.

---

# 17. Döntés

- **AI/headless architecture:** P0
- **imperfect information:** P0
- **legal action interface:** P0
- **chance/determinism:** P0
- **search/cloning:** P0
- **serialization:** P0
- **direct dependency:** nem szükséges
- **clean-room architecture inspiráció:** igen.
