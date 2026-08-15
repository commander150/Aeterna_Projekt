# AETERNA – CROSS-PROJECT SYNTHESIS: AI AND SIMULATION

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első AI/headless synthesis
- **Javasolt repository-útvonal:** `learning/synthesis/topics/ai_and_simulation.md`
- **Nem AETERNA-authority.**

---

# 1. Fő evidence

Elsődleges:
- OpenSpiel
- RLCard

Támogató:
- PokerKit
- MAGE
- Durak.Godot
- AETERNA current headless/EngineSession architecture

---

# 2. P-AI-001 – Egy rules engine, több consumer

**Státusz:** `REPEATED_PATTERN`  
**AETERNA státusz:** `ALREADY_ADOPTED`

```text
Authoritative Engine
├── Human UI adapter
├── AI adapter
├── Headless batch host
└── Debug/analyzer adapter
```

Ne legyen AI-specifikus rules engine.

---

# 3. P-AI-002 – Observation külön az authoritative state-től

**OpenSpiel:** observation/info-state külön State API.  
**RLCard:** player state külön perfect-information API.

AETERNA:

```text
MatchState              # private engine
PlayerSnapshot          # viewer-safe raw observation
AIObservation           # derived/versioned encoding
```

---

# 4. P-AI-003 – Legal action space first-class input

OpenSpiel:
- LegalActions;
- legal-action mask;
- validation.

RLCard:
- legal_actions state-ben;
- agent ebből választ.

AETERNA current:
- `ListLegalActions`.

## Következtetés

Az AI-nak soha nem kell saját rules-validatort implementálnia.

---

# 5. P-AI-004 – Fair AI és trusted analyzer külön capability

Normál AI:
- csak player-visible observation;
- own legal actions.

Trusted analyzer:
- explicit capabilityval full state;
- offline balance/debug use.

Nem szabad egyetlen API flag defaultjával véletlenül full state-et adni fair AI-nak.

---

# 6. P-AI-005 – Structured/combinatorial actions

OpenSpiel új structured-action API-ja erős minta.

AETERNA reaction/target/payment/action space kombinatorikus.

Candidate:

```text
LegalActionOption
- option/action ID
- action family
- typed selection schema
- enabled/disabled reason
```

AI ugyanazt fogyasztja, mint UI.

---

# 7. P-AI-006 – Environment step until next external decision

OpenSpiel RL env chance nodeokat automatikusan feldolgoz a következő decision boundaryig.

PokerKit automation ugyanezt a mintát támogatja.

AETERNA candidate:

```text
SubmitAction
→ deterministic mandatory engine work
→ stop when external player/agent decision needed
```

Reaction/trigger/choice coordinatorral később ez különösen értékes.

---

# 8. P-AI-007 – Clone/Fork simulation state

OpenSpiel `Clone` + `Child(action)`.

RLCard step-back.

MAGE copy/restore.

## AETERNA candidate

Planning/search AI számára később:

```text
SimulationSession Fork()
ApplyLegalAction()
Evaluate()
```

Ez trusted internal/headless API.

Nem public network authority.

---

# 9. P-AI-008 – Agent RNG külön a match RNG-től

RLCard game local RNG és agent global RNG különbsége rámutat a seed domain problémára.

AETERNA explicit:

```text
MatchRandomState
AgentRandomState
TrainingSamplerRandomState
```

A match replayt az agent RNG nem befolyásolja közvetlenül; csak a kiválasztott accepted action.

---

# 10. P-AI-009 – Trajectory külön a canonical replaytől

Training trajectory:

- observation;
- action;
- reward/outcome.

Canonical replay:

- accepted commands;
- canonical events;
- RNG outcomes/state;
- version/fingerprints.

Külön cél, külön contract.

---

# 11. P-AI-010 – Illegal action fallback tilos

RLCard Leduc `_decode_action` negatív példa:

illegal encoded action → check/fold.

AETERNA:

```text
illegal choice
→ reject
→ unchanged state
```

AI error/metric marad látható.

---

# 12. Observation versioning

AI model stabil feature schema-t igényel.

Javasolt:

```text
ObservationSchemaId
ObservationSchemaVersion
Rules/DataFingerprint
```

A PlayerSnapshot JSON önmagában nem feltétlen ideális neural input.

Legyen külön derived encoder.

---

# 13. AI observation rétegek – PROPOSED

## Raw fair observation

A jelenlegi viewer-safe PlayerSnapshot.

## Structured agent observation

Versioned DTO:

```text
AIObservation
- schema_version
- state_version
- actor/player
- phase
- priority/pending type
- visible zones/cards
- resources/vitals
- legal_action_ids
```

## Encoded tensor

Külön adapter:

```text
AIObservation
→ FeatureEncoder
→ tensor/vector
```

A tensor schema ne legyen rules authority.

---

# 14. Reward/outcome

AETERNA játékban a reward nem game rule.

Minimum:

```text
terminal outcome
win/loss/draw
```

Training reward shaping külön agent/training layer.

Ne kerüljön production rules engine-be.

---

# 15. Headless batch architecture – candidate

```text
Aeterna.Engine
        ↓
Headless MatchHost
        ↓
AIEnvironmentAdapter
        ↓
Agent A / Agent B
        ↓
Trajectory / Metrics
```

Batch runner:
- N matches;
- deterministic seeds;
- deck configs;
- result aggregation;
- replay artifact optional.

---

# 16. Search/planning architecture – later

```text
trusted canonical/simulation state
→ fork
→ legal actions
→ child state
→ evaluate
```

Hidden-information fair searchnél:
- csak player information/observation;
- belief/resampling külön algorithm layer.

Ne használjon opponent hidden state-et normál fair policy.

---

# 17. Anti-patternök

| ID | Név |
|---|---|
| `A-AI-001` | külön AI rules implementation |
| `A-AI-002` | full MatchState normál fair agentnek |
| `A-AI-003` | AI saját legal-action validátor |
| `A-AI-004` | UI gesture mint agent action |
| `A-AI-005` | illegal action automatikus fallback |
| `A-AI-006` | agent RNG és match RNG összekeverve |
| `A-AI-007` | training trajectory = canonical replay |
| `A-AI-008` | neural tensor schema rules authorityként |
| `A-AI-009` | reward shaping production game rulesban |
| `A-AI-010` | search clone shared mutable MatchState-tel |

---

# 18. AETERNA current fit

Már meglévő jó alap:
- pure C# engine;
- headless project;
- viewer-safe snapshot;
- legal actions;
- version-guarded submit;
- deterministic proof;
- hidden projection.

Hiányzó későbbi réteg:
- explicit AIObservation DTO;
- feature encoder;
- batch match runner;
- trajectory format;
- clone/fork simulation API;
- AI metrics/evaluation harness.

---

# 19. Következő forrás szükségessége

OpenSpiel + RLCard után általános AI env architectureből már jó coverage van.

PettingZoo csak akkor P0, ha:
- standardized multi-agent sequencing;
- AEC API;
- simultaneous/turn handoff

külön értéket ad.

PTCG-Bench később P1 lehet:
- LLM agent evaluation;
- scenario benchmark;
- card-game-specific evaluation.

gym-locm:
- csak akkor, ha observation/action encodingból új card-game-specific tanulságot ad.

---

# 20. Verdict

Az AI/headless architecture fő iránya már blueprintképes.

Nem szükséges újabb általános RL frameworköt letölteni a következő AETERNA-design döntéshez.
