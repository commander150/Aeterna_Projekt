# AETERNA – CROSS-PROJECT SYNTHESIS: ACTIONS AND VALIDATION

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első generalized action/validation synthesis
- **Javasolt repository-útvonal:** `learning/synthesis/topics/actions_and_validation.md`
- **AETERNA production összevetési bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Nem AETERNA-szabályforrás.**
- **Nem implementation spec.**

---

# 1. Evidence

Fő learning evidence:

- OpenSpiel – `LegalActions`, structured action validation, no-mutation validation;
- PokerKit – `can_*` + domain operation pattern;
- boardgame.io – state ID, reducer, `INVALID_MOVE`;
- Forge / MAGE / ocgcore – resolution-time revalidation és pending/timing lifecycle;
- RLCard – legal action input, valamint illegal-action fallback negatív példa;
- Nakama / Colyseus – transport/schema/auth/queue boundary.

AETERNA current production evidence:

- `LegalActionSpace`;
- state-bound action IDs;
- `ActionRequest`;
- `expected_state_version`;
- `SubmitAction`;
- payload validation;
- detailed transition validation;
- immutable `PlayCardPlan`;
- post-transition invariant validation;
- trigger discovery;
- viewer projection.

---

# 2. P-ACT-001 – Legal action discovery és execution külön lifecycle

**Státusz:** `REPEATED_PATTERN`  
**AETERNA:** `IMPLEMENTED_FOUNDATION`

```text
current authoritative state
→ enumerate legal actions/options
→ external decision
→ submit selected action
→ revalidate
→ execute
```

A legal action lista nem garantálhatja, hogy egy később beküldött request még mindig legal.

Ezért executionkor final revalidation kötelező.

---

# 3. P-ACT-002 – State-bound engine-issued action identity

**Státusz:** `REPEATED/SYNTHESIZED`  
**AETERNA:** `IMPLEMENTED_FOUNDATION`

A jelenlegi production action ID-k több esetben tartalmazzák a state versiont, phase/turn/player contextet.

A pending-trigger optionok engine-issued stable ID-t használnak.

Candidate általános szabály:

> a kliens/AI ne találja ki a rules object/action identityt; az engine adja ki az aktuális state-hez tartozó optiont.

Reactionnél ezt folytatja a tervezett `reaction_option_id`.

---

# 4. P-ACT-003 – Layered validation

**Státusz:** `REPEATED_PATTERN`  
**AETERNA:** `IMPLEMENTED_FOUNDATION + GENERALIZE`

Javasolt általános rétegek:

```text
L0 envelope/schema parse
L1 match / actor identity
L2 expected state version
L3 action ID lookup
L4 action type + payload shape
L5 action availability / timing / pending authority
L6 domain preflight
L7 target/payment/selection revalidation
L8 immutable execution plan
L9 atomic commit
L10 post-state invariant validation
L11 consequence/trigger discovery
L12 internal event materialization
L13 viewer projection
```

Nem minden egyszerű action igényel külön objektumot minden réteghez, de a szemantikai határ maradjon.

---

# 5. P-ACT-004 – Complex action plan-before-commit

**Státusz:** `REPEATED/SUPPORTING`  
**AETERNA:** `ALREADY_USED_FOR_PLAY_CARD`

A current `play_card`:

```text
BuildPlayCardPlan
→ events/transition plan
→ commit
```

modellt használ.

Ez különösen fontos:

- payment;
- multiple targets;
- reaction;
- combat;
- replacement;
- multi-step effect

esetén.

Candidate:

```text
ActionExecutionPlan
```

nem feltétlen közös base class; a fontos invariant:

> normál rules reject ne maradjon a commit közepére.

---

# 6. P-ACT-005 – Final revalidation

**Státusz:** `REPEATED_PATTERN`  
**AETERNA:** `RULES/PRODUCTION REQUIREMENT`

A legal action enumeration és submit között állapotváltozás történhet.

State-version guard sok stale requestet megfog, de resolution/timing közben további state változás is lehet.

Ezért:

- target;
- source;
- cost/payment;
- timing;
- pending ownership

a szükséges boundaryn újraellenőrzendő.

Reaction resolution különösen ezt igényli.

---

# 7. P-ACT-006 – Reject = unchanged state

**Státusz:** `REPEATED_PATTERN`  
**AETERNA:** `ADOPTED`

Illegális vagy stale request:

```text
Accepted = false
StateVersionBefore == StateVersionAfter
Events = empty
```

és semmilyen rules state nem változik.

RLCard silent check/fold fallbackje erős ellenpélda.

---

# 8. P-ACT-007 – Deterministic legal-action ordering

**AETERNA current foundation**

A current production:

```text
OrderRank
→ ActionType
→ ActionId
```

sorrendet használ.

Ezt meg kell tartani:

- UI stabilitás;
- AI reproducibility;
- golden fixture;
- network diff;
- deterministic hashing

miatt.

---

# 9. P-ACT-008 – Pending decision birtokolja az action surface-t

**Státusz:** `REPEATED/SYNTHESIZED`  
**AETERNA:** `PARTIALLY_IMPLEMENTED`

Current:

- `PendingTriggerWindow` blokkolja a phase actionöket;
- a controller egyetlen trigger-resolution action familyt kap.

Reaction blueprint:

- ReactionWindow alatt csak `react` / `pass_priority`.

Később ugyanez:

- PendingTargetChoice;
- PendingPaymentChoice;
- PendingOrderChoice;
- CombatDecision.

Candidate invariant:

> egy externally blocking pending decision family határozza meg az enabled legal-action surface-t.

V1-ben ne legyen két egymástól független blocking decision egyszerre.

---

# 10. P-ACT-009 – External generic payload, internal typed state

A public contract JSON payloadot használ.

Ez jó boundary:
- Godot;
- AI;
- network;
- scripting/tooling

számára.

Rules codeban viszont a payloadot typed internal rekordokra/planre kell materializálni.

Ne fusson mély rules logic közvetlen tetszőleges `JsonElement` property-kre támaszkodva.

---

# 11. P-ACT-010 – `request_id` correlation és idempotency külön fogalom

## Jelenlegi production

`request_id`:
- kötelező;
- visszatér az ActionResponse-ban.

A current EngineSessionben nincs általános duplicate-request ledger/cache.

Tehát:

```text
request_id = correlation identity
```

de jelenleg nem bizonyított:

```text
request_id = exactly-once execution guarantee
```

## Online később

Network host:
- duplicate request detection;
- cached prior outcome;
- conflicting reuse reject.

Crash recoveryhez később persistált request ledger is szükséges lehet.

---

# 12. P-ACT-011 – Diagnostic trust boundary

A current `EngineDiagnostic` tart:

- code;
- severity;
- category;
- blocking;
- safe message;
- developer message;
- retry policy;
- details.

Local development/Godot bridge számára ez hasznos.

Future untrusted network clientnél a `DeveloperMessage` és `Details` nem küldhető automatikusan változatlanul.

Candidate:

```text
InternalDiagnostic
→ ProjectDiagnosticForViewer
→ PublicDiagnostic
```

Player/public:
- code;
- safe message;
- retry policy;
- safe details.

Server/debug:
- developer message;
- internal context;
- stack/trace.

Ez **future hardening**, nem jelenlegi bizonyított leak.

---

# 13. P-ACT-012 – Auth/session identity nem request payload authority

Online:
- transport session köti a connectiont MatchSeat/EnginePlayer ID-hoz;
- request `player_id` csak akkor fogadható el, ha egyezik a bound identityval.

A local EngineSession továbbra is player ID-t validál.

Network host nem bízhat a kliens által szabadon választott `player_id`-ban.

---

# 14. Public action model – hosszú távú candidate

```text
LegalAction
- action_id
- action_type
- actor_player_id
- enabled
- order_rank
- disabled_reason
- payload_schema / options

ActionRequest
- request_id
- match_id
- player_id
- expected_state_version
- action_id
- action_type
- payload
```

A jelenlegi contract ezt már lényegében tartalmazza.

Nincs szükség új public action modellre.

---

# 15. Internal action-rule registry – csak későbbi refactor candidate

A jelenlegi `switch` és payload validator kis action-számnál elfogadható.

Ahogy nő:

- reaction;
- optional trigger;
- ordering;
- target choice;
- combat;
- Pecsét;
- special actions

esetén a central switch/payload validator túl nagy lehet.

Későbbi candidate:

```text
IActionRule / ActionRuleDescriptor
- ActionType
- EnumerateLegalActions
- ValidatePayload
- BuildPlan
- Commit
```

De:

**Reaction v1 miatt önmagában nem kötelező előre megcsinálni ezt a refactort.**

A refactor akkor induljon, amikor a duplication/maintenance risk ténylegesen megjelenik.

---

# 16. Preflight és legal action drift

Kockázat:

```text
ListLegalActions logic
≠
SubmitAction detailed validation
```

Ha ugyanazt a rules conditiont két helyen külön implementáljuk, drift keletkezhet.

Current `play_card` sok shared preflightot már újrahasznál.

Candidate:

- legal option builder és final plan builder ugyanazokat a typed rules primitive-eket használja;
- UI schema csak a preflight eredmény projectionje;
- execution final revalidation ugyanazt a primitive-et hívja.

---

# 17. Anti-patternök

| ID | Név |
|---|---|
| `A-ACT-001` | UI saját legal-action derivation |
| `A-ACT-002` | action listből választott index mint stable identity |
| `A-ACT-003` | stale state-ben enumerált action final revalidation nélkül |
| `A-ACT-004` | commit közbeni normál rules reject |
| `A-ACT-005` | illegal action silent fallback |
| `A-ACT-006` | payload JSON közvetlenül mély mutation logicban |
| `A-ACT-007` | nondeterministic legal action ordering |
| `A-ACT-008` | több egymástól független blocking pending authority |
| `A-ACT-009` | request ID-t idempotencynek állítjuk cache nélkül |
| `A-ACT-010` | developer diagnostic automatikusan public |
| `A-ACT-011` | network payload player ID authorityként |
| `A-ACT-012` | legal-action és execution validation külön rules implementation |

---

# 18. Verdict

Az AETERNA jelenlegi action contract **nem cserélendő le**.

A fő feladat:

- a meglévő mintát generalized invariantként rögzíteni;
- Reaction/Priorityt erre ráépíteni;
- diagnostics/network idempotency/projection boundaryt később hardeningolni;
- action registry refactort csak tényleges növekedési nyomásnál bevezetni.
