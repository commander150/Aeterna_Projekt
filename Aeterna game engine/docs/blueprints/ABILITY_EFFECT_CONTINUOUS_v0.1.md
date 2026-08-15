# AETERNA – ABILITY / EFFECT / CONTINUOUS SYSTEM BLUEPRINT

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** architecture blueprint / current foundation expansion plan
- **Javasolt repository-útvonal:** `Aeterna game engine/docs/blueprints/ABILITY_EFFECT_CONTINUOUS_v0.1.md`
- **Repository-bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Rules authority:** official AETERNA sources
- **Nem full card coverage spec.**

---

# 1. Fő döntés

A jelenlegi canonical ability architecture **megtartandó**.

Nem váltunk:
- per-card C# class only modellre;
- arbitrary scripting authorityra;
- natural language runtime parserre.

Hosszú távú forma:

```text
Canonical Ability Definition
        ↓
Trigger / Condition / Target / Cost / Effect / Duration graph
        ↓
Reusable typed runtime primitives
        ↓
Rare explicit exceptional module where necessary
        ↓
Authoritative transition + events + projection
```

---

# 2. Existing production building blocks

Már létezik:

```text
CanonicalAbilityCatalog
CanonicalAbilityTemplateCompiler
CanonicalEffectConditionEvaluator
CanonicalTargetFilterEvaluator
CanonicalTargetResolver
CanonicalTriggerResolver
CanonicalEffectExecutor
CanonicalContinuousEffects
CanonicalZoneTransition
CanonicalDamageResolver
CanonicalDrawResolver
CanonicalVitals
```

State:
- modifier instances;
- keyword grant instances;
- durations/creation metadata;
- pending trigger foundation.

Ezekre építünk.

---

# 3. Canonical ability graph – megtartandó

Fő node familyk:
- Ability;
- Trigger;
- Condition;
- Target;
- Effect;
- EffectParameter;
- Expression;
- Duration;
- Template + arguments/provenance.

Future additions csak akkor:
- official semantics indokolja;
- existing node nem írja le tisztán;
- schema/validation/test adható hozzá.

---

# 4. Implementation mode

Candidate hosszú távú módok:

```text
structured_graph
compiled_template
exception_module
unsupported
```

A jelenlegi adatschema meglévő `implementation_mode_id` semanticséhez igazítandó, nem feltétlen új enumként.

## `structured_graph`
Közvetlen canonical node graph.

## `compiled_template`
Authoring/template → load-time structured graph.

## `exception_module`
Ritka typed C# module, registryből explicit kötve.

## `unsupported`
Fail closed.

---

# 5. Module contract

Egy executable primitive/module akkor production-supported, ha:

```text
Stable Module/Action ID
Input Parameter Schema
Source Policy
Timing/Stage Policy
Condition Contract
Target/Choice Contract
Cost Contract if any
Transition/Result Contract
Event Contract
Projection Policy
Diagnostics
Determinism Proof
Positive/Negative Fixtures
```

Nem minden egyszerű effecthez kell külön public module object; ez semantic checklist.

---

# 6. Execution coordinator

Candidate logical flow:

```text
Ability Declaration/Trigger
→ Build Resolution Context
→ Precondition
→ Cost/Choice if required
→ Target resolution/selection
→ Reaction window where rules permit
→ Resolution revalidation
→ Effect graph execution
→ Atomic transition(s)
→ Committed events
→ Consequence/trigger discovery
→ Continuous state installation/expiry
→ stable closure
```

A Reaction coordinator és ability executor külön ownership, de együttműködik.

---

# 7. ResolutionContext – candidate

Current context már tart:
- ability;
- source card instance;
- controller;
- resolution ID;
- resolution event type;
- target overrides.

Future bővítés csak igény szerint:

```text
OriginatingEventId?
ReactionWindowId?
ParentResolutionEntryId?
TriggerContext?
ChoiceResults
PaymentPlan
```

Ne legyen teljes MatchState snapshot.

---

# 8. Effect primitive families

Current supported familyk például:
- zone move;
- draw;
- damage;
- apply modifier;
- grant keyword.

Future family csak official rules alapján.

Javasolt taxonomy:

```text
STATE_MUTATION
RESOURCE
ZONE
DAMAGE/HEAL if rules
MODIFIER
KEYWORD
TRIGGER/TIMING
CHOICE
META/CONTROL
```

Taxonomy audit/coverage cél; executiont továbbra is explicit action type/module végzi.

---

# 9. Effect graph

## Invariants

- node IDs stable;
- root/child reference valid;
- no cycle unless future explicit looping mechanic, ami jelenleg nem cél;
- sequence deterministic;
- branch semantics explicit;
- child ordering explicit;
- unknown node/action blocking.

## Future branching

Ha conditional branch bővül:
- explicit true/false child relation;
- no implicit exception-driven branch;
- branch condition side-effect-free.

---

# 10. Trigger integration

Trigger detection:
- committed eventből;
- canonical event mappinggel;
- source/context validationdel.

Future trigger batch:

```text
DiscoveredTrigger
→ eligibility
→ simultaneous batch/order
→ optional/mandatory decision
→ resolution entry
```

Ability executor nem maga dönt multi-trigger orderingről.

---

# 11. Reaction integration

Reaction-capable ability:
- timing metadata/policy;
- engine-generated reaction option;
- declaration → ResolutionStackEntry;
- executor csak resolutionkor fut.

Ne legyen:
```text
react request → immediate effect mutation
```

A Reaction blueprint marad authority a priority/pass/window lifecyclere.

---

# 12. Choice / target architecture

## Simple deterministic target
Current resolver.

## Player-selected target
Engine legal option list → ActionRequest/choice → final revalidation.

## Nested choice
Future typed:
```text
PendingChoiceState
```

Choice state:
- owner/player;
- option IDs;
- min/max count;
- order significance;
- cancel policy;
- originating resolution;
- state version.

Ne legyen ability-specific UI callback authority.

---

# 13. Cost architecture

Későbbi generic cost külön stage:

```text
CostDefinition
→ CanPay
→ CostOption/PaymentPlan
→ Commit Cost
→ Ability Declaration succeeds
```

Cost és effect payment különválasztható az official rules alapján.

A card-play Aura payment foundation reusable primitive lehet, de ability-cost semantics nem automatikusan ugyanaz.

---

# 14. Continuous effect v1 current contract

Current proof:
- additive Attack;
- additive MaxHP;
- Ward grant;
- Cleave grant;
- end-of-current-turn expiry;
- deterministic ordering;
- zone-presence identity;
- lethal consequence after MaxHP expiry.

Ezt `CONTINUOUS_V1` capabilityként dokumentálhatjuk.

Nem full generic continuous support.

---

# 15. Continuous v2 – csak rules inventory után

Előbb listázandó official szükség:
- set stat;
- cap/floor;
- multiply;
- copy;
- conditional continuous;
- source-dependent;
- suppression;
- multiple duration boundaries;
- continuous keyword removal;
- dependency chains.

Ezután döntjük el, kell-e:
- operation precedence;
- explicit layers;
- dependency graph;
- fixed-point recomputation.

**Nem importáljuk Magic layer rendszerét szükséglet nélkül.**

---

# 16. Replacement / prevention blueprint boundary

Külön future component:

```text
ReplacementPreventionEvaluator
```

Input:
- proposed canonical transition/event;
- current authoritative state;
- applicable replacement definitions.

Output candidate:
```text
unchanged
replaced(modified proposal)
prevented
choice required
```

Exact ordering/choice/layer rules később official decision.

Nem része Reaction v1 first slice-nak.

---

# 17. Duration engine vNext

Current duration object jó primitive.

Future duration policy registry candidate:

```text
DurationPolicy
- policy_id
- install context
- expiration predicate/boundary
- dependency/source relation
- max applications
```

Expiration evaluation:
- deterministic;
- state/event boundaryn;
- consequence plan before mutation;
- expiry events where useful.

---

# 18. Continuous dependency safety

Minden persistent instance tároljon elegendő identityt:
- source card presence/instance where needed;
- source ability/effect;
- target presence;
- created sequence/state version;
- duration identity.

Ha source relevance rules szerint megszűnik:
- explicit expiration/removal reason.

---

# 19. Coverage model

## Engine capability
Milyen primitive/module supported?

## Content coverage
Mely ability/effect rekordok executable?

## Card coverage
Egy card minden mandatory abilityje supported?

Javasolt hierarchy:

```text
EffectCoverage
→ AbilityCoverage
→ CardCoverage
→ Deck/FormatCoverage
```

Egy deck csak akkor `FULLY_EXECUTABLE`, ha minden required content supported.

---

# 20. Unsupported policy

Development:
- diagnostics;
- controlled fixture skip where explicitly allowed.

Production playable match:
- mandatory unsupported effect/ability → blocking.

Ne legyen silent no-op, kivéve ha official rule szerint effect érvénytelenné vált resolutionkor.

`unsupported implementation` és `rules-invalidated resolution` két külön állapot.

---

# 21. Versioning

Template már versioned provenance-t használ.

Később module contract változásnál:
- module/semantic version;
- parameter schema version;
- package compatibility;
- migration diagnostics.

Nem kell minden belső helperre public semver.

Csak persisted/content-facing contractokra.

---

# 22. Exceptional module

Ha egy card nem éri meg generikussá tenni:

```text
exception_module_id
→ typed C# handler
```

Kötelező:
- explicit registration;
- source/card/ability scope;
- same atomicity/event/projection rules;
- positive/negative fixture;
- coverage report.

Nem férhet hozzá tetszőleges global mutable API-n keresztül kontroll nélkül.

---

# 23. Test strategy

## Primitive fixtures
Effect action type szint.

## Ability fixtures
Canonical graph + expected transitions.

## Interaction fixtures
- Reaction;
- trigger ordering;
- continuous expiry;
- source leaves zone;
- simultaneous effects;
- replacement later.

## Golden content fixtures
Néhány representative real card per supported module family.

## Coverage gate
Unsupported mandatory content blocker.

---

# 24. Implementation roadmap

Nem kell most mindet leprogramozni.

### A6.1 – Reaction integration
A már tervezett Reaction v1.

### A6.2 – Optional/choice foundation
Csak amikor card coverage igényli.

### A6.3 – Trigger batch ordering
Official base rule implementálása.

### A6.4 – Coverage matrix migration
Package/content report.

### A6.5 – Replacement/prevention
Rules gate után.

### A6.6 – Continuous v2
Csak official mechanic inventory után.

---

# 25. Non-goal

- Lua scripting runtime;
- user code mods;
- arbitrary WASM;
- full Magic rules clone;
- every future mechanic előre implementálása;
- runtime natural-language interpretation;
- ability system rewrite.

---

# 26. Változásnapló

## 0.1 – 2026-08-15
- current production ability/effect foundation formalizálva;
- graph/template/module boundaries rögzítve;
- current continuous v1 scope pontosítva;
- replacement/prevention külön future subsystem;
- choice/cost/duration/coverage roadmap létrejött;
- exceptional typed module escape hatch rögzítve.
