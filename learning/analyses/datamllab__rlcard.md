# AETERNA – datamllab/rlcard ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott card-game AI environment source audit
- **Javasolt repository-útvonal:** `learning/analyses/datamllab__rlcard.md`
- **Repository:** `datamllab/rlcard`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `d7d0a957baf4cc7225a50522adb0164bf130a9d0`
- **Commit dátuma:** 2024-06-26
- **Fő technológia:** Python / NumPy
- **Licenc:** MIT
- **Elsődleges AETERNA-érték:** card-game-specific env/agent boundary, player observation, legal action mapping, trajectories, seed, step-back
- **Vizsgálati korlát:** nem történt lokális futtatás; csak base Env + Leduc environment/game + random agent került célzott source-auditba
- **Nem AETERNA-szabályforrás.**

---

# 1. Vizsgálati cél

A cél annak feltárása volt, hogyan fordít le egy card-game engine state-et AI/RL számára:

- player observation;
- legal actions;
- action encoding;
- agent API;
- trajectory;
- random seed;
- step-back;
- perfect information debug.

---

# 2. Vizsgált fő source-ok

| Terület | Fájl |
|---|---|
| base environment | `rlcard/envs/env.py` |
| Leduc environment | `rlcard/envs/leducholdem.py` |
| Leduc game | `rlcard/games/leducholdem/game.py` |
| random agent | `rlcard/agents/random_agent.py` |

---

# 3. Env és Game különválasztás

A base `Env`:

- a konkrét `game`-et wrapeli;
- actiont dekódol;
- state-et AI reprezentációvá alakít;
- agenteket futtat;
- trajectoryt gyűjt.

A rules a Game-ben maradnak.

## AETERNA tanulság

AI adapter:

```text
production engine
→ observation/action adapter
→ agent
```

Ne:

```text
production engine
+
külön AI rules implementation
```

---

# 4. Player-specific state

`Env.get_state(player_id)`:

```text
game.get_state(player_id)
→ _extract_state
```

Leduc `_extract_state` tart:

- legal actions;
- encoded observation;
- raw player-view observation;
- raw legal actions;
- action recorder.

Az encoded state:

- saját hand;
- public card;
- own chips;
- opponent aggregate chips

alapján készül.

## AETERNA következtetés

Agent observation:

- viewer-safe stateből származzon;
- lehet belőle derived tensor/vector;
- raw viewer snapshot debugging/training célra külön elérhető lehet.

---

# 5. Perfect information külön API

Leduc külön:

```text
get_perfect_information()
```

amely minden játékos hand identityját is visszaadja.

Ez nem a normál player state API része.

## AETERNA candidate

Külön AI capability:

- `FAIR_PLAYER`
- `TRUSTED_ANALYZER`

A normál ellenfél-AI soha ne kapjon perfect info-t.

---

# 6. Legal action encoding

A raw game action stringek:

```text
call
raise
fold
check
```

integer action space-re mapelődnek.

A state `legal_actions` OrderedDictként adja az aktuális legális ID-ket.

A random agent kizárólag ebből választ.

## Pozitív tanulság

Az agent kapjon explicit legal-action mask/listát.

## AETERNA korrekció

AETERNA action space összetettebb.

Globális fix integer action space helyett engine-issued option/action ID + payload schema jobb.

---

# 7. Erős negatív minta – illegal action fallback

Leduc `_decode_action`:

ha az action ID által jelölt raw action nem legal:

- ha `check` legal → `check`;
- különben → `fold`.

Ez csendes action-korrekció.

## AETERNA anti-pattern

```text
illegal AI choice
→ "closest valid" action
```

tiltandó.

A helyes modell:

```text
illegal/stale action
→ controlled reject
→ state unchanged
```

Ez különösen fontos trainingnél is, mert különben az agent hibás policyje láthatatlanná válik.

---

# 8. Seed és game randomness

Base Env:

```text
seeding.np_random(seed)
→ self.game.np_random
```

A game objectek ezt a local RNG-t használják.

Leduc:

- dealer;
- player;
- judger;
- round

ugyanazt az RNG referenciát kapja.

## Pozitív tanulság

Environment-local random stream, nem globális game RNG.

## Korlát

A random agent maga:

```text
np.random.choice(...)
```

globális NumPy randomot használ.

Tehát az env seed nem feltétlen kontrollálja az agent stochasticityt.

## AETERNA tanulság

Külön seed domain:

```text
Match RNG
Agent RNG
Training sampler RNG
```

Ne osszuk össze őket.

---

# 9. Step-back

A base Env opcionális `step_back()` API-t ad.

Leduc Game minden step előtt snapshotolja:

- round;
- raise state;
- current player;
- round counter;
- deck;
- public card;
- players;
- hands.

Step-back visszaállítja ezeket.

## Tanulság

Search/training szempontból hasznos branch/undo capability.

## Korlát

Ez game-specifikus manual snapshot.

Nem általános serialization contract.

AETERNA számára inkább:

```text
Clone/Fork simulation state
```

vagy canonical save/checkpoint jobb hosszú távú megoldás.

---

# 10. Trajectory

`Env.run()` playerenként trajectory listát épít:

```text
state
action
state
action
...
final state
```

és payoffot ad.

Ez egyszerű, de hasznos training interface.

## AETERNA candidate

Egy evaluation/training trajectory:

```text
Observation
LegalActionSummary
SelectedAction
Reward/Outcome
StateVersion
```

A canonical replay viszont külön maradjon.

Training trajectory != authoritative replay.

---

# 11. Agent interface

Agent:

```text
step(state) -> action
eval_step(state) -> action + diagnostics/policy info
```

RandomAgent explicit legal action state-ből választ.

## AETERNA tanulság

Agent legyen pure decision provider.

Nem kell:
- EngineSession reference;
- MatchState mutation;
- Godot node;
- database write authority.

---

# 12. Amit érdemes átvenni elvi mintaként

1. game vs env adapter;
2. player-specific observation;
3. legal action list/mask;
4. perfect information külön API;
5. trajectory collection;
6. environment-local RNG;
7. separate agent API;
8. optional step-back/search support.

---

# 13. Amit kifejezetten nem szabad átvenni

1. illegal action → check/fold fallback;
2. flat integer action space mint kötelező forma;
3. raw perfect info normál agentnek;
4. global agent RNG;
5. manual game-specific snapshot mint általános save contract;
6. training trajectory = replay összemosás.

---

# 14. AETERNA AI/headless candidate

```text
Observation
- state_version
- viewer/player_id
- phase/pending/priority
- public/own visible state
- legal action options

AgentDecision
- selected action_id / option
- optional target/choice payload

Environment
- Reset
- Observe
- Step
- IsTerminal
- Outcome
```

A production engine marad authority.

---

# 15. Döntés

- **card-game AI env érték:** P0
- **observation/legal-action érték:** P0
- **trajectory érték:** P1
- **seed/step-back érték:** P1
- **illegal fallback:** erős anti-pattern
- **direct dependency:** nem szükséges
- **clean-room architecture inspiráció:** igen.
