# AETERNA – AI / HEADLESS ENVIRONMENT BLUEPRINT

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** architecture blueprint / nem implementation spec
- **Javasolt repository-útvonal:** `Aeterna game engine/docs/blueprints/AI_HEADLESS_ENVIRONMENT_v0.1.md`
- **Rules authority:** AETERNA official sources
- **Production authority:** current C# EngineSession / MatchState
- **Learning input:** AI/simulation synthesis
- **Nem nyit új runtime engine-t.**

---

# 1. Cél

Olyan headless/AI boundary tervezése, amely:

- ugyanazt a production engine-t használja;
- fair AI-nak nem szivárogtat hidden info-t;
- ugyanazt a legal-action contractot használja, mint UI;
- determinisztikus batch futtatásra alkalmas;
- később search/planning és training környezetet támogat;
- nem teszi az AI-t rules authorityvé.

---

# 2. Authority

```text
Aeterna.Engine
        ↑
single authority
        ↓
EngineSession / trusted simulation facade
```

AI csak dönt.

AI nem:
- mutál MatchState-et;
- hajt végre zone move-ot;
- számol saját legal actiont;
- alkalmaz saját rules exceptiont.

---

# 3. Agent mode

## FAIR_PLAYER

Input:
- viewer-safe observation;
- own enabled legal actions.

Nem kap:
- opponent hidden hand;
- hidden Jel identity;
- internal trigger data;
- private RNG state.

## TRUSTED_ANALYZER

Offline/debug/balance.

Kaphat:
- full state;
- all-player projection;
- internal diagnostics.

Explicit capability required.

## DEBUG_FULL_STATE

Fejlesztői reprodukció, nem gameplay AI.

---

# 4. Environment API – concept

```text
Reset(matchConfig, seed) -> Observation
Observe(playerId) -> Observation
ListLegalActions(playerId) -> LegalActionSpace
Step(actionRequest) -> StepResult
IsTerminal -> bool
GetOutcome -> MatchOutcome
```

Nem feltétlen új public production API.

Lehet adapter a meglévő EngineSession fölött.

---

# 5. Observation

## Raw

Current `PlayerSnapshot`.

## AIObservation DTO

Később versioned:

```text
SchemaVersion
StateVersion
ViewerPlayerId
ActivePlayerId
PriorityPlayerId
Phase
PendingDecisionSummary
VisiblePlayerState
VisibleCards/Zones
Vitals/Resources
LegalActionRefs
```

## Feature tensor

Külön encoder:

```text
AIObservation -> tensor
```

Nem része engine rules contractnak.

---

# 6. Action

Az AI ugyanazt az engine-issued action ID-t / option ID-t választja.

```text
legal actions
→ selected action
→ ActionRequest
→ SubmitAction
```

No fallback.

Reject:
- training metric;
- test failure;
- state unchanged.

---

# 7. StepResult

Candidate:

```text
Observation next
Events viewer-safe
Terminal bool
Outcome optional
StateVersion
```

Training-specific reward ne legyen production game contract.

Reward adapter külön számítható outcome/event alapján.

---

# 8. Advance-until-decision

A későbbi coordinator a mandatory internal worket automatikusan futtatja.

AI csak authoritative external decision boundaryn kap `Step`.

Decision type lehet:
- normal action;
- reaction;
- trigger choice;
- target choice;
- combat choice;
- later special decision.

---

# 9. Batch runner

Későbbi tool:

```text
BatchConfig
- match count
- deck A/B
- seed sequence
- agent A/B
- rules/data fingerprint
- replay policy
```

Output:
- wins/losses/draws;
- turns;
- duration;
- invalid action count;
- rule diagnostics;
- optional replay IDs.

---

# 10. Simulation fork – later

Search AI számára:

```text
ForkSimulationState()
ListLegalActions()
ApplySimulationAction()
Evaluate()
```

A fork:
- isolated;
- deterministic;
- hidden-info policy-aware.

Nem oszthat mutable state-et az authoritative live match-csel.

---

# 11. Versioning

AI model artifacthez rögzítendő:

- ObservationSchemaVersion;
- ActionContractVersion;
- RulesSourceVersion;
- CanonicalDataFingerprint;
- EngineVersion.

Így model incompatibility explicit.

---

# 12. Replay relation

Training trajectory:
- model input/output.

Replay:
- authoritative decision/outcome history.

Külön fájl/contract.

Batch runner opcionálisan canonical replayt kérhet az engine-től.

---

# 13. V1 non-goal

- neural model architecture;
- konkrét RL algorithm;
- MCTS implementation;
- distributed trainer;
- GPU pipeline;
- matchmaking;
- online inference service;
- reward shaping rules;
- opponent modeling.

---

# 14. Acceptance candidate – későbbi implementation

1. AI uses same EngineSession semantics;
2. fair mode snapshot equals player visibility policy;
3. hidden opponent data absent;
4. legal action set equals engine legal actions;
5. invalid AI action rejected, no fallback;
6. deterministic same-seed batch reproducible;
7. state version carried through;
8. terminal outcome stable;
9. existing human/Godot behavior unchanged;
10. agent replacement requires no engine rules changes.

---

# 15. Következő döntés

A blueprint jelenleg nem igényel implementationt.

Előbb:
- Reaction/Priority contract;
- event/pending model;
- RNG policy

stabilizálása hasznos.

Utána az első headless AI adapter nagyon kis slice lehet.
