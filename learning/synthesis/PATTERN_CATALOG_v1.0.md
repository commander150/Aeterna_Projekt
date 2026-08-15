# AETERNA – CROSS-PROJECT PATTERN CATALOG

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Verzió:** 1.0
- **Dátum:** 2026-08-15
- **Státusz:** önálló, kumulatív pre-OQ pattern snapshot
- **Javasolt repository-útvonal:** `learning/synthesis/PATTERN_CATALOG_v1.0.md`
- **Kiinduló AETERNA repository HEAD:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Módszertan:** `CROSS_PROJECT_METHOD_v0.1`
- **Nem AETERNA-authority.**
- **A korábbi v0.2–v0.9 rolling katalógusok tartalma ebbe a dokumentumba összevonva.**

---

# 1. Státuszértelmezés

A `Synthesis / evidence` oszlop a learning bizonyíték állapotát írja le.
Az `AETERNA státusz` azt jelzi, hogy az adott minta a jelenlegi AETERNA-ban milyen helyzetben van.

A minták nem válnak AETERNA-szabállyá pusztán attól, hogy több projektben megjelennek.
A hivatalos rules authority és a külön emberi design decision elsőbbsége változatlan.

---

# 2. Authority / state patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-AUTH-001` | rules authority külön a presentation state-től | több független / REPEATED_PATTERN | VERIFIED |
| `P-AUTH-002` | dedicated server önmagában nem authority guarantee | több / REPEATED_PATTERN | CANDIDATE |
| `P-AUTH-003` | hidden information data projection | több / REPEATED_PATTERN | IMPLEMENTED/VERIFIED |
| `P-AUTH-004` | single validated mutation gate | több / REPEATED_PATTERN | VERIFIED |
| `P-AUTH-005` | explicit lifecycle state | több / REPEATED_PATTERN | VERIFIED |
| `P-AUTH-006` | pure domain library UI/headless/AI számára | több / REPEATED_PATTERN | IMPLEMENTED |

---

# 3. Reaction / trigger / resolution patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-RT-001` | Event creation külön trigger detectiontől | FORGE/MAGE/IGNIS / REPEATED_PATTERN | CANDIDATE |
| `P-RT-002` | Pending state explicit és resumable | MAGE/IGNIS/FORGE / REPEATED_PATTERN | CANDIDATE |
| `P-RT-003` | Simultaneous trigger batch külön resolution stacktől | FORGE/MAGE/IGNIS / REPEATED_PATTERN | BASE ORDERING RULES DECIDED; RUNTIME PARTIAL |
| `P-RT-004` | Priority owner authoritative state | MAGE/IGNIS/FORGE / REPEATED_PATTERN | FIELD EXISTS; REACTION USE CANDIDATE |
| `P-RT-005` | Reaction declaration külön resolutiontől | FORGE/IGNIS/CSBCGF / REPEATED_PATTERN | CANDIDATE |
| `P-RT-006` | LIFO explicit resolution | rules + learning / SUPPORTING | RULES DECIDED |
| `P-RT-007` | Resolution-time revalidation | FORGE/MAGE/IGNIS + negative evidence / REPEATED_PATTERN | RULES DECIDED |
| `P-RT-008` | Resolution entry causality/context | MAGE/IGNIS/FORGE / REPEATED_PATTERN | CANDIDATE |
| `P-RT-009` | Replacement/prevention külön interception layer | FORGE/MAGE / REPEATED_PATTERN | HIGH-CONFIDENCE ARCH CANDIDATE; RULES DEFERRED |
| `P-RT-010` | Continuous/static külön lifecycle | FORGE/MAGE/IGNIS / REPEATED_PATTERN | PRODUCTION FOUNDATION EXISTS |
| `P-RT-011` | Generic Pending List kerülendő | synthesis / PROPOSED | PROPOSED |
| `P-RT-012` | Engine advances until explicit input | IGNIS/FORGE/MAGE / REPEATED_PATTERN | CANDIDATE |

---

# 4. Determinism / RNG patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-DET-001` | RNG continuation state first-class | REPEATED/SUPPORTING | CANDIDATE |
| `P-DET-002` | RNG state viewer-hidden | OBSERVED_STRONG | CANDIDATE |
| `P-DET-003` | random-dependent client prediction kerülendő | OBSERVED_STRONG | CANDIDATE |
| `P-DET-004` | random outcome historyban materializálható | OBSERVED_STRONG | CANDIDATE |
| `P-DET-005` | determinism contract versioned | SYNTHESIZED | PROPOSED |

---

# 5. Replay / save patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-REP-001` | current state külön transition historytól | REPEATED_PATTERN | CANDIDATE |
| `P-REP-002` | replay strict event sourcing nélkül | REPEATED_PATTERN | CANDIDATE |
| `P-REP-003` | replay initial context/fingerprint | SYNTHESIZED | PROPOSED |
| `P-REP-004` | normalized decision stream | SYNTHESIZED | PROPOSED |
| `P-REP-005` | canonical outcome/event verification layer | SYNTHESIZED | PROPOSED |
| `P-REP-006` | snapshot checkpoint + log hibrid | REPEATED_SUPPORT | CANDIDATE |
| `P-REP-007` | viewer-specific replay projection | REPEATED_SUPPORT | CANDIDATE |
| `P-REP-008` | save és replay külön contract | SYNTHESIZED | PROPOSED |

---

# 6. AI / simulation patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-AI-001` | egy rules engine, több consumer | REPEATED | ADOPTED |
| `P-AI-002` | observation külön authoritative state-től | REPEATED | CANDIDATE |
| `P-AI-003` | legal action first-class AI input | REPEATED | CURRENT FOUNDATION |
| `P-AI-004` | fair AI és trusted analyzer külön capability | REPEATED | CANDIDATE |
| `P-AI-005` | structured/combinatorial actions | REPEATED/SUPPORT | CANDIDATE |
| `P-AI-006` | advance until external decision | REPEATED | CANDIDATE |
| `P-AI-007` | clone/fork simulation state | REPEATED | CANDIDATE |
| `P-AI-008` | agent RNG külön match RNG-től | SYNTHESIZED | PROPOSED |
| `P-AI-009` | trajectory külön replaytől | REPEATED | CANDIDATE |
| `P-AI-010` | illegal action fallback tilos | NEGATIVE EVIDENCE | PROPOSED INVARIANT |

---

# 7. Multiplayer / session / reconnect patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-NET-001` | network host külön rules engine-től | REPEATED | CANDIDATE |
| `P-NET-002` | multi-layer identity | REPEATED | CANDIDATE |
| `P-NET-003` | per-match serialized mutation queue | STRONG | CANDIDATE |
| `P-NET-004` | join/reconnect külön lifecycle | REPEATED | CANDIDATE |
| `P-NET-005` | reconnect authoritative resync | REPEATED | CANDIDATE |
| `P-NET-006` | engine projection, transport secondary | SYNTHESIZED | PROPOSED |
| `P-NET-007` | reliable request + idempotency | SYNTHESIZED | PROPOSED |
| `P-NET-008` | full snapshot + ordered continuation | REPEATED | CANDIDATE |
| `P-NET-009` | explicit state/event network ordering | REPEATED | CANDIDATE |
| `P-NET-010` | transport backpressure külön rules rejecttől | REPEATED | CANDIDATE |

---

# 8. Actions / validation patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-ACT-001` | legal discovery külön executiontől | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-ACT-002` | state-bound engine-issued action identity | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-ACT-003` | layered validation | részletek a kapcsolódó topic synthesisben | IMPLEMENTED/GENERALIZE |
| `P-ACT-004` | complex plan-before-commit | részletek a kapcsolódó topic synthesisben | PARTIAL/STRONG |
| `P-ACT-005` | final revalidation | részletek a kapcsolódó topic synthesisben | REQUIRED |
| `P-ACT-006` | reject = unchanged state | részletek a kapcsolódó topic synthesisben | ADOPTED |
| `P-ACT-007` | deterministic legal action order | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-ACT-008` | pending decision owns action surface | részletek a kapcsolódó topic synthesisben | PARTIAL |
| `P-ACT-009` | external generic payload → internal typed plan | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-ACT-010` | request correlation != idempotency | részletek a kapcsolódó topic synthesisben | CURRENT FACT |
| `P-ACT-011` | public/internal diagnostic split | részletek a kapcsolódó topic synthesisben | FUTURE CANDIDATE |
| `P-ACT-012` | session binding validates player identity | részletek a kapcsolódó topic synthesisben | NETWORK CANDIDATE |

---

# 9. Events / projection patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-EVT-001` | internal vs viewer event | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-EVT-002` | ordered immutable history | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-EVT-003` | first-class causality metadata | részletek a kapcsolódó topic synthesisben | PARTIAL/CANDIDATE |
| `P-EVT-004` | pending timing context != committed event | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-EVT-005` | canonical history only after commit | részletek a kapcsolódó topic synthesisben | ADOPTED |
| `P-EVT-006` | trigger discovery from committed event | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-EVT-007` | audience != payload projection | részletek a kapcsolódó topic synthesisben | IMPLEMENTED CONCEPT / CANDIDATE GENERALIZATION |
| `P-EVT-008` | projection policy registry as scale refactor | részletek a kapcsolódó topic synthesisben | DEFERRED CANDIDATE |
| `P-EVT-009` | event-existence secrecy separate gate | részletek a kapcsolódó topic synthesisben | DEFERRED |
| `P-EVT-010` | technical vs gameplay event classification | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-EVT-011` | diagnostic != gameplay event | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-EVT-012` | response/event stream same projection policy | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-EVT-013` | projection deterministic/side-effect-free | részletek a kapcsolódó topic synthesisben | REQUIRED |
| `P-EVT-014` | snapshot/event visibility consistent | részletek a kapcsolódó topic synthesisben | REQUIRED |

---

# 10. Data / content patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-DATA-001` | human/canonical/runtime authority külön | részletek a kapcsolódó topic synthesisben | ADOPTED |
| `P-DATA-002` | definition külön implementationtől | részletek a kapcsolódó topic synthesisben | ADOPTED/PARTIAL |
| `P-DATA-003` | stable semantic IDs | részletek a kapcsolódó topic synthesisben | IMPLEMENTED FOUNDATION |
| `P-DATA-004` | schema/format version first-class | részletek a kapcsolódó topic synthesisben | IMPLEMENTED FOUNDATION |
| `P-DATA-005` | explicit package dependency | részletek a kapcsolódó topic synthesisben | IMPLEMENTED FOUNDATION |
| `P-DATA-006` | generation külön verificationtől | részletek a kapcsolódó topic synthesisben | ADOPTED |
| `P-DATA-007` | human override registry | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-DATA-008` | localization != definition identity | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-DATA-009` | format/legality külön domain | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-DATA-010` | installed/published/active lifecycle külön | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-DATA-011` | consumer outputs derived | részletek a kapcsolódó topic synthesisben | ADOPTED |
| `P-DATA-012` | delta/cache csak optimization | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-DATA-013` | engine capability != content coverage | részletek a kapcsolódó topic synthesisben | ADOPTED CONCEPT |
| `P-DATA-014` | blocking publish gate | részletek a kapcsolódó topic synthesisben | ADOPTED |
| `P-DATA-015` | asset provenance külön manifest | részletek a kapcsolódó topic synthesisben | CANDIDATE |

---

# 11. Ability / effect / continuous patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-ABIL-001` | ability graph külön card definitiontől | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-ABIL-002` | reusable primitive + composition | részletek a kapcsolódó topic synthesisben | IMPLEMENTED DIRECTION |
| `P-ABIL-003` | template compile, no runtime text interpretation | részletek a kapcsolódó topic synthesisben | IMPLEMENTED FOUNDATION |
| `P-ABIL-004` | explicit lifecycle stages | részletek a kapcsolódó topic synthesisben | CANDIDATE/FOUNDATION |
| `P-ABIL-005` | trigger discovery != execution | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-ABIL-006` | source/event resolution context | részletek a kapcsolódó topic synthesisben | PARTIAL/CANDIDATE |
| `P-ABIL-007` | unknown/unsupported fail closed | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-ABIL-008` | explicit deterministic effect order | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-ABIL-009` | side-effect-free bounded conditions | részletek a kapcsolódó topic synthesisben | CANDIDATE/FOUNDATION |
| `P-ABIL-010` | target resolver separate mutation | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-ABIL-011` | cost separate result | részletek a kapcsolódó topic synthesisben | FUTURE CANDIDATE |
| `P-ABIL-012` | continuous instance state first-class | részletek a kapcsolódó topic synthesisben | IMPLEMENTED V1 |
| `P-ABIL-013` | target zone-presence identity | részletek a kapcsolódó topic synthesisben | IMPLEMENTED |
| `P-ABIL-014` | duration policy first-class | részletek a kapcsolódó topic synthesisben | IMPLEMENTED V1 |
| `P-ABIL-015` | expiry is rules transition | részletek a kapcsolódó topic synthesisben | IMPLEMENTED V1 |
| `P-ABIL-016` | dependency/layering only from rules inventory | részletek a kapcsolódó topic synthesisben | PROPOSED |
| `P-ABIL-017` | replacement/prevention separate subsystem | részletek a kapcsolódó topic synthesisben | HIGH-CONFIDENCE CANDIDATE |
| `P-ABIL-018` | engine capability != content coverage | részletek a kapcsolódó topic synthesisben | ADOPTED CONCEPT |
| `P-ABIL-019` | explicit typed exceptional fallback | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-ABIL-020` | versioned content-facing module contract | részletek a kapcsolódó topic synthesisben | FUTURE CANDIDATE |

---

# 12. Release / diagnostics / compatibility patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-REL-001` | acceptance proof != CI | részletek a kapcsolódó topic synthesisben | CURRENT FACT / CANDIDATE |
| `P-REL-002` | one canonical acceptance recipe | részletek a kapcsolódó topic synthesisben | PROPOSED |
| `P-REL-003` | machine-readable proof artifact | részletek a kapcsolódó topic synthesisben | PROPOSED |
| `P-REL-004` | multi-component release identity | részletek a kapcsolódó topic synthesisben | PROPOSED |
| `P-REL-005` | engine/data/rules versions separate | részletek a kapcsolódó topic synthesisben | ADOPTED CONCEPT |
| `P-REL-006` | explicit compatibility gate | részletek a kapcsolódó topic synthesisben | PARTIAL/PROPOSED |
| `P-REL-007` | diagnostics/log/metric/trace/proof separate | részletek a kapcsolódó topic synthesisben | PROPOSED |
| `P-REL-008` | public/internal diagnostic projection | részletek a kapcsolódó topic synthesisben | FUTURE CANDIDATE |
| `P-REL-009` | causal correlation IDs | részletek a kapcsolódó topic synthesisben | PARTIAL/CANDIDATE |
| `P-REL-010` | structured operational logging | részletek a kapcsolódó topic synthesisben | FUTURE CANDIDATE |
| `P-REL-011` | metrics side-effect-free | részletek a kapcsolódó topic synthesisben | REQUIRED |
| `P-REL-012` | relative performance baseline | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-REL-013` | staged CI gates | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-REL-014` | immutable release input/artifact | részletek a kapcsolódó topic synthesisben | PROPOSED |
| `P-REL-015` | semantic versions only external contracts | részletek a kapcsolódó topic synthesisben | PROPOSED |
| `P-REL-016` | explicit backward compatibility policy | részletek a kapcsolódó topic synthesisben | PROPOSED |
| `P-REL-017` | reproducible bug report bundle | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-REL-018` | crash != rules reject | részletek a kapcsolódó topic synthesisben | REQUIRED |
| `P-REL-019` | human release notes != machine manifest | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-REL-020` | historical manual proof remains valid evidence | részletek a kapcsolódó topic synthesisben | ADOPTED |

---

# 13. Godot client / UI patternök

| ID | Pattern | Synthesis / evidence | AETERNA státusz |
|---|---|---|---|
| `P-UI-001` | presentation state külön rules state-től | részletek a kapcsolódó topic synthesisben | ADOPTED |
| `P-UI-002` | CardView stable engine identityhoz kötve | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-003` | child order layout, nem rules order | részletek a kapcsolódó topic synthesisben | PROPOSED INVARIANT |
| `P-UI-004` | drag/drop = intent | részletek a kapcsolódó topic synthesisben | PROPOSED |
| `P-UI-005` | legal actions hajtják affordance-et | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-006` | pending decision explicit UI mode | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-007` | reaction/priority UI engine-driven | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-008` | target selection engine optionból | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-009` | animation state/event következmény | részletek a kapcsolódó topic synthesisben | PROPOSED INVARIANT |
| `P-UI-010` | visual event queue külön engine event store-tól | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-011` | full snapshot reconciliation | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-012` | hidden info only projectionből | részletek a kapcsolódó topic synthesisben | REQUIRED |
| `P-UI-013` | hand/pile layout pure presentation | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-014` | visual state machine presentation-only | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-015` | visual/foil profile separate | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-016` | performance tier gameplay-neutral | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-017` | accessibility presentation policy | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-018` | input device adapter külön action intenttől | részletek a kapcsolódó topic synthesisben | CANDIDATE |
| `P-UI-019` | reject → reconcile, no guessing | részletek a kapcsolódó topic synthesisben | REQUIRED |
| `P-UI-020` | centralized viewer ViewModel/StateStore | részletek a kapcsolódó topic synthesisben | CANDIDATE |

---

# 14. Official rules companion facts – Reaction / Timing

- `R-RT-001`: non-initiator first if both may react;
- `R-RT-002`: pass;
- `R-RT-003`: two consecutive passes close window;
- `R-RT-004`: reaction can stack on reaction;
- `R-RT-005`: further response opportunity only where rule/card text permits;
- `R-RT-006`: LIFO resolution;
- `R-RT-007`: resolution-time revalidation;
- `R-RT-008`: no retroactive reaction to closed event by default;
- `R-RT-009`: mandatory/optional comes from rules/card text;
- `R-RT-010`: optional effect use chosen by eligible player in the reaction window;
- `R-RT-011`: simultaneous effects identified before ordering;
- `R-RT-012`: default simultaneous ordering = active player effects, then opponent;
- `R-RT-013`: one player orders own simultaneous effects unless overridden;
- `R-RT-014`: event closure requires all mandatory effects, windows, pending effects and zone endpoints resolved to stable state.

---

# 15. Anti-pattern registry


## Authority / state

| ID | Anti-pattern |
|---|---|
| `A-AUTH-001` | scene tree mint canonical rules state |
| `A-AUTH-002` | hidden data minden kliensen, csak visual hiding |
| `A-AUTH-003` | több peer rules mutation |
| `A-AUTH-004` | direct RPC mutation |
| `A-AUTH-005` | state-version guard hiánya |
| `A-AUTH-006` | request identity/idempotency hiánya |
| `A-AUTH-007` | optimistic client rules mutation |
| `A-AUTH-008` | implicit coroutine/call-stack game state |
| `A-AUTH-009` | projection helyett visual hiding |
| `A-AUTH-010` | domain orchestration UI-ba szivárog |

## Reaction / trigger / resolution

| ID | Anti-pattern |
|---|---|
| `A-RT-001` | event = azonnali effect execution |
| `A-RT-002` | trigger registry = pending trigger batch |
| `A-RT-003` | simultaneous trigger incidental list-order |
| `A-RT-004` | priority implicit call-order |
| `A-RT-005` | reaction közvetlen recursive mutation |
| `A-RT-006` | final revalidation hiánya |
| `A-RT-007` | replacement reactionként modellezve |
| `A-RT-008` | continuous effect reaction stacken |
| `A-RT-009` | generic pending lista minden semanticsra |
| `A-RT-010` | resolution context current source state-ből rekonstruálva |
| `A-RT-011` | implicit callback pending state |
| `A-RT-012` | closed event causality nélkül újranyílik |
| `A-RT-013` | minden reaction automatikusan új response roundot nyit rules-policy nélkül |

## Determinism / RNG

| ID | Anti-pattern |
|---|---|
| `A-DET-001` | process-global RNG; |
| `A-DET-002` | seed nincs perzisztálva; |
| `A-DET-003` | RNG continuation elveszik; |
| `A-DET-004` | future-predictive RNG state kliensnek; |
| `A-DET-005` | random outcome event correlation nélkül; |
| `A-DET-006` | replay engine/data version nélkül; |
| `A-DET-007` | implicit iteration order határozza meg RNG callordert. |

## Replay / save

| ID | Anti-pattern |
|---|---|
| `A-REP-001` | UI gesture replay input; |
| `A-REP-002` | initial fingerprint nélküli replay; |
| `A-REP-003` | authoritative hidden replay publikus; |
| `A-REP-004` | save pending state nélkül; |
| `A-REP-005` | debug log = replay log összemosás; |
| `A-REP-006` | silent reinterpretation engine upgrade után; |
| `A-REP-007` | random nincs replay contractban; |
| `A-REP-008` | szükségtelen strict event-sourcing migration. |

## AI / simulation

| ID | Anti-pattern |
|---|---|
| `A-AI-001` | külön AI rules implementation |
| `A-AI-002` | full state fair agentnek |
| `A-AI-003` | AI saját legal validator |
| `A-AI-004` | UI gesture agent actionként |
| `A-AI-005` | illegal action fallback |
| `A-AI-006` | agent/match RNG összekeverve |
| `A-AI-007` | trajectory és replay összemosva |
| `A-AI-008` | feature tensor rules authority |
| `A-AI-009` | reward shaping production rulesban |
| `A-AI-010` | shared mutable state search clone-nál |

## Multiplayer / session / reconnect

| ID | Anti-pattern |
|---|---|
| `A-NET-001` | network state = rules authority |
| `A-NET-002` | account/session/connection/player összemosva |
| `A-NET-003` | payload player identity elhitt |
| `A-NET-004` | hidden policy csak transportban |
| `A-NET-005` | concurrent direct MatchState mutation |
| `A-NET-006` | canonical action silent drop |
| `A-NET-007` | reconnect új playerként |
| `A-NET-008` | reconnect local state-be vetett bizalom |
| `A-NET-009` | request ID nélküli retry |
| `A-NET-010` | event gap detection hiánya |
| `A-NET-011` | unreliable canonical action |
| `A-NET-012` | disconnect gameplay policy transportban |

## Actions / validation

| ID | Anti-pattern |
|---|---|
| `A-ACT-001` | UI derives rules legality |
| `A-ACT-002` | list index stable action identity |
| `A-ACT-003` | no final revalidation |
| `A-ACT-004` | normal reject during partial commit |
| `A-ACT-005` | silent fallback |
| `A-ACT-006` | raw JSON deep mutation logic |
| `A-ACT-007` | nondeterministic action order |
| `A-ACT-008` | multiple blocking pending authorities |
| `A-ACT-009` | request ID claimed idempotent without ledger |
| `A-ACT-010` | developer diagnostics public |
| `A-ACT-011` | client player ID trusted by network |
| `A-ACT-012` | enumeration/execution rules drift |

## Events / projection

| ID | Anti-pattern |
|---|---|
| `A-EVT-001` | UI redaction authority |
| `A-EVT-002` | internal event broadcast directly |
| `A-EVT-003` | pending intent as committed event |
| `A-EVT-004` | reject leaves event |
| `A-EVT-005` | ad-hoc trigger scan |
| `A-EVT-006` | audience/payload visibility conflated |
| `A-EVT-007` | projection differs by API path |
| `A-EVT-008` | snapshot hidden but event leaks identity |
| `A-EVT-009` | diagnostic as gameplay event |
| `A-EVT-010` | nondeterministic projection |
| `A-EVT-011` | implicit causality from event type string |
| `A-EVT-012` | secret event existence leaked by sequence |

## Data / content

| ID | Anti-pattern |
|---|---|
| `A-DATA-001` | runtime package kézi authority edit |
| `A-DATA-002` | row index semantic ID |
| `A-DATA-003` | language-dependent card identity |
| `A-DATA-004` | definition és executable implementation összemosva |
| `A-DATA-005` | installed = active |
| `A-DATA-006` | schema mismatch silent reuse |
| `A-DATA-007` | correction ad-hoc hardcode minden rekordra |
| `A-DATA-008` | generator saját maga egyetlen validatorral |
| `A-DATA-009` | implicit package dependency |
| `A-DATA-010` | cache/delta canonical source |
| `A-DATA-011` | support metadata production capabilityként |
| `A-DATA-012` | format legality definitionbe égetve |
| `A-DATA-013` | asset provenance hiánya |
| `A-DATA-014` | derived consumer visszaír source-ba |

## Ability / effect / continuous

| ID | Anti-pattern |
|---|---|
| `A-ABIL-001` | every card one-off class |
| `A-ABIL-002` | natural-language runtime execution |
| `A-ABIL-003` | global script mutation API |
| `A-ABIL-004` | trigger = immediate mutation |
| `A-ABIL-005` | implicit effect order |
| `A-ABIL-006` | condition side effects |
| `A-ABIL-007` | targeting during mutation without preflight |
| `A-ABIL-008` | unsupported best-effort execution |
| `A-ABIL-009` | ad-hoc duration cleanup |
| `A-ABIL-010` | zone presence ignored |
| `A-ABIL-011` | replacement modeled as normal effect/reaction |
| `A-ABIL-012` | primitive support claimed as full card coverage |
| `A-ABIL-013` | template semantic drift without version |
| `A-ABIL-014` | exceptional fallback bypasses standard contract |

## Release / diagnostics / compatibility

| ID | Anti-pattern |
|---|---|
| `A-REL-001` | CI result rules authorityként |
| `A-REL-002` | release dirty worktreeből |
| `A-REL-003` | engine/data/rules versions összemosva |
| `A-REL-004` | silent compatibility best-effort |
| `A-REL-005` | raw developer diagnostics clientnek |
| `A-REL-006` | hidden data default logban |
| `A-REL-007` | metrics mutál rules state-et |
| `A-REL-008` | dev-machine benchmark SLA |
| `A-REL-009` | local/CI eltérő acceptance recipe |
| `A-REL-010` | internal exception normál rejectként |
| `A-REL-011` | release notes exact manifestként |
| `A-REL-012` | persisted contract version nélkül |
| `A-REL-013` | bug report state/fingerprint nélkül |
| `A-REL-014` | observability mint gameplay event |

## Godot client / UI

| ID | Anti-pattern |
|---|---|
| `A-UI-001` | scene tree rules authority |
| `A-UI-002` | card node identity rules identity |
| `A-UI-003` | child order canonical order |
| `A-UI-004` | drop mutates before engine accept |
| `A-UI-005` | UI recomputes legality |
| `A-UI-006` | targetability raycast-only |
| `A-UI-007` | animation callback completes rules |
| `A-UI-008` | hidden identity client receives then visually hides |
| `A-UI-009` | UI pending state drifts |
| `A-UI-010` | raw DTO parsing scattered scenes |
| `A-UI-011` | visual effect rules data |
| `A-UI-012` | drag-only action modality |
| `A-UI-013` | silent correction after reject |
| `A-UI-014` | visual cue mutates engine |
---

# 16. Promotion gate

`AETERNA_CANDIDATE → PROPOSED → ADOPTED` promotionhoz legalább:

1. official rules compatibility;
2. production architecture összevetés;
3. trade-off és alternatívák;
4. evidence lineage;
5. failure mode;
6. explicit emberi design decision

szükséges.

A már productionban létező, auditált invariáns `IMPLEMENTED/VERIFIED` státusza nem új blueprint-proposal elfogadását jelenti, hanem a meglévő rendszer állapotát dokumentálja.

---

# 17. Kapcsolódó synthesis dokumentumok

- `topics/authority_and_state.md`
- `topics/reactions_triggers_resolution.md`
- `topics/determinism_and_random.md`
- `topics/serialization_save_replay.md`
- `topics/ai_and_simulation.md`
- `topics/multiplayer.md`
- `topics/actions_and_validation.md`
- `topics/events_and_projection.md`
- `topics/data_and_content_pipeline.md`
- `topics/ability_effect_systems.md`
- `topics/diagnostics_and_observability.md`
- `topics/godot_client_and_ui.md`

---

# 18. Változásnapló

## 1.0 – 2026-08-15

- a v0.2–v0.9 rolling pattern családok ténylegesen beemelve;
- a v1.0 többé nem függ egy hiányzó aktív v0.9 katalógustól;
- UI/client pattern család hozzáadva;
- anti-pattern registry kumulatívvá téve;
- promotion gate és official rules companion facts megőrizve.
