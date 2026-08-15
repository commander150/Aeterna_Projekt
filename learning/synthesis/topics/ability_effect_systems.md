# AETERNA – CROSS-PROJECT SYNTHESIS: ABILITY / EFFECT / CONTINUOUS SYSTEMS

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első ability/effect/continuous dependency synthesis
- **Javasolt repository-útvonal:** `learning/synthesis/topics/ability_effect_systems.md`
- **AETERNA production összevetési bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Nem AETERNA-szabályforrás.**

---

# 1. Evidence

Fő learning evidence:

- ProjectIgnis/CardScripts;
- Card-Forge/forge;
- magefree/mage;
- edo9300/ygopro-core;
- DarkPro1337/Arcomage;
- db0/godot-card-game-framework;
- db0/Fragment-Forge;
- finkmoritz/csbcgf.

AETERNA current production:

- `CanonicalAbilityCatalog`;
- `CanonicalAbilityTemplateCompiler`;
- condition evaluator;
- target filter/resolver;
- trigger resolver;
- effect executor;
- zone transition/damage/draw primitives;
- modifier/keyword/duration state;
- continuous expiry plan;
- canonical event/projection;
- current package/registry binding.

---

# 2. P-ABIL-001 – Ability graph külön a card definitiontől

**Státusz:** `REPEATED_PATTERN`  
**AETERNA:** `IMPLEMENTED_FOUNDATION`

A card definition az ability identityra hivatkozik.

Az ability külön node-kban/rekordokban reprezentálhat:
- trigger;
- condition;
- target;
- cost;
- effect;
- expression;
- duration;
- template argument.

Ez skálázhatóbb, mint egyetlen monolit `CardEffectScript` blob.

---

# 3. P-ABIL-002 – Shared primitives + card-local composition

CardScripts több ezer card scriptet közös:
- utility;
- cost;
- summon/procedure;
- chain helper

rétegre épít.

Forge/MAGE nagy shared effect/ability class hierarchiát használ.

AETERNA current:
- shared typed effect action types;
- reusable target/condition primitives;
- template compiler.

## Következtetés

```text
small reusable primitives
+ data-driven composition/templates
+ rare explicit exceptional implementation
```

jobb hosszú távú stratégia, mint:
- minden card egyedi C# class;
- vagy minden card egyetlen túl általános scripting language.

---

# 4. P-ABIL-003 – Template/macro compile, nem runtime text interpretation

A current `CanonicalAbilityTemplateCompiler`:
- versioned template;
- parameter schema;
- node/binding model;
- typed arguments;
- generated stable node IDs;
- provenance;
- load-time compilation

réteget használ.

Ez erős AETERNA saját minta.

A template:
- authoring convenience;
- canonical graph expansion.

Runtime executor már a compiled structured graphot fogyasztja.

## Invariant

Template semantics változása:
- version bump;
- rebuild;
- provenance trace.

Ne változzon egy meglévő card ability csendben egy template implementation update miatt.

---

# 5. P-ABIL-004 – Ability lifecycle explicit stage-ek

Közös evidence:

```text
trigger/timing
→ condition
→ cost
→ target/choice
→ response/reaction boundary
→ resolution
→ state mutation
→ events
→ duration/continuous aftermath
```

Nem minden ability használ minden stage-et.

A stage-ek szemantikai különválasztása fontosabb, mint az osztályhierarchia.

---

# 6. P-ABIL-005 – Trigger discovery nem ability execution

Forge/MAGE/ocgcore és current AETERNA is ezt mutatja.

A current `CanonicalTriggerResolver`:
- csak committed authoritative EngineEventet fogad;
- eventet visszaellenőriz state/event store ellen;
- candidate discoveryt ad;
- még nem maga az effect mutation.

Ez megtartandó.

---

# 7. P-ABIL-006 – Source/event context snapshot

CardScripts chain-local data, MAGE triggering event és ocgcore chain context ugyanazt a problémát jelzi:

> resolutionkor a source current state-je már nem feltétlen ugyanaz, mint declaration/trigger pillanatban.

AETERNA candidate context mezők csak rules igény szerint:
- source presence/zone sequence;
- originating event ID;
- selected targets;
- controller;
- resolved parameters;
- trigger-time relevant snapshot.

Ne snapshotoljunk teljes MatchState-et minden abilityhez.

---

# 8. P-ABIL-007 – Effect executor csak supportált graphot hajtson végre

Current AETERNA erős safety minta:
- unknown action type → controlled `CANONICAL_EFFECT_UNSUPPORTED`;
- unsupported parameter shape → reject;
- unsupported source selector → reject;
- graph validation előbb;
- duplicate/missing node reference blocking.

## Invariant

```text
unknown/partial structured data
!=
best-effort gameplay
```

Unsupported content fail closed.

---

# 9. P-ABIL-008 – Effect order explicit

Current effects explicit `Sequence` alapján rendeződnek.

A current executor child/root graphot validál és deterministic sequence ordert használ.

Külső nagy engine-ek is explicit resolution ordert tartanak.

## AETERNA

- effect tag sorrendje nem execution order;
- collection iteration nem execution order;
- source row order csak akkor semantic, ha explicit schema contracttá tettük.

---

# 10. P-ABIL-009 – Conditions declarative, de bounded

Current condition evaluator külön runtime component.

Expressions/conditions canonical recordként léteznek.

## Candidate

Condition language legyen:
- typed;
- bounded;
- deterministic;
- side-effect-free;
- auditable.

Condition evaluation nem mutálhat MatchState-et.

Ne legyen arbitrary user code conditionként production package-ből.

---

# 11. P-ABIL-010 – Target resolver külön a effect mutatortól

Current `CanonicalTargetResolver` / target-filter evaluator külön layer.

Ez támogatja:
- legal action generation;
- preflight;
- UI highlight;
- resolution revalidation.

## Invariant

A target query:
- side-effect-free;
- deterministic;
- viewer-safe option projection.

Execution nem maga keresi random módon a targetet, ha a card rules választást kér.

---

# 12. P-ABIL-011 – Cost külön a effect resulttól

CardScripts és több engine explicit cost stage-et használ.

A current AETERNA első ability/effect slice nem teljes generic cost system.

Később:

```text
CanPayCost
→ reserve/plan
→ pay atomically
→ only then resolve declaration
```

Cost failure nem partial effect.

---

# 13. P-ABIL-012 – Continuous effect instance state first-class

Current AETERNA már tárol:
- modifier instance;
- keyword grant instance;
- source ability/effect/resolution;
- target card + zone sequence;
- duration ID/policy;
- created state version/sequence.

Ez jó primitive.

## Fontos scope

Current support szándékosan szűk:
- additive positive Attack/MaxHP;
- Ward/Cleave keyword grant;
- until end of current turn.

Nem állítjuk, hogy full continuous engine kész.

---

# 14. P-ABIL-013 – Continuous target presence identity

Current modifier/grant targethoz:
- CardInstanceId;
- TargetZoneSequence

kapcsolódik.

Ha a card elhagyja a zónát és új presence-ként visszatér, a régi continuous instance nem automatikusan ugyanazt az object presence-t érinti.

Ez erős object-lifecycle safety minta.

---

# 15. P-ABIL-014 – Duration külön policy

Current duration:
- külön canonical definition;
- külön runtime instance metadata;
- explicit policy ID.

V1 csak:
`duration_until_end_of_current_turn`.

Későbbi candidate policyk csak official rules alapján:
- until phase boundary;
- while source remains;
- until condition;
- fixed applications;
- permanent/until removed.

Ne legyen minden effect handler saját timeout/cleanup logikája.

---

# 16. P-ABIL-015 – Expiry maga is rules transition

Current `BuildEndTurnPlan`:
- deterministic expiry order;
- effective value before/after;
- keyword before/after;
- lethal consequence planning.

Ez fontos:

> duration expiry nem egyszerű dictionary delete.

Expiry új rules consequence-et hozhat létre.

Később event/trigger discoveryt is indíthat official rules szerint.

---

# 17. P-ABIL-016 – Continuous dependency/layering a következő valódi gap

Jelenleg additive stat + union keyword modell egyszerű.

Komplex későbbi esetek:
- set value;
- multiply;
- copy;
- suppression;
- source-dependent value;
- type/keyword dependency;
- replacement;
- prevention;
- continuous ability enabling/disabling another effect.

## Candidate architecture

Ne implementáljunk rögtön Magic-szerű layer systemet.

Előbb official AETERNA rulesból inventory:
- milyen modifier operationök vannak;
- milyen dependency ciklusok lehetségesek;
- milyen ordering szükséges.

Csak utána minimal layer/dependency model.

---

# 18. P-ABIL-017 – Replacement/prevention külön subsystem

Forge/MAGE erős evidence.

Current AETERNA ability doc pipeline már helyet tart neki, de runtime nincs.

Architecture:

```text
ProposedTransition/Event
→ Replacement/Prevention Evaluation
→ ResultingTransition/Event
→ Commit
```

Nem:
- normal effect child;
- reaction stack post-hoc correction;
- continuous stat modifier.

Exact rules separate gate.

---

# 19. P-ABIL-018 – Module support vs content coverage külön

D1 synthesishez kapcsolódik.

```text
Effect primitive implemented
!=
all cards using that concept migrated/tested
```

Coverage card/ability/effect szinten mérhető.

---

# 20. P-ABIL-019 – Exceptional card-local fallback csak explicit

Nagy TCG-k mutatják, hogy teljesen generikus schema valószínűleg nem fed le mindent gazdaságosan.

Candidate:
- reusable modules first;
- rare typed C# exceptional handler possible;
- explicit registry identity;
- same validation/event/projection contract;
- fixture mandatory;
- no hidden arbitrary reflection/script execution.

Fallback ne legyen `eval(card text)`.

---

# 21. P-ABIL-020 – Versioned executable module contract

Hosszú távon module identity mellé:
- module semantic version / contract version;
- parameter schema version;
- supported package schema;
- deterministic migration policy

kellhet.

Nem szükséges minden jelenlegi primitive-hez azonnal új version field, de template provenance már mutatja a mintát.

---

# 22. Ability execution error policy

Unsupported:
- controlled diagnostic;
- no partial mutation;
- test/content coverage FAIL ahol mandatory.

Invalid source/target:
- declarationkor reject;
- resolutionkor official revalidation semantics.

Internal invariant violation:
- `EngineStateException` / blocking developer error.

Ne mossuk össze a három kategóriát.

---

# 23. Test matrix per primitive/module

Minimum:
1. positive simple;
2. boundary values;
3. invalid source;
4. invalid target;
5. stale target/presence;
6. multiple targets/order;
7. hidden info projection;
8. deterministic event order;
9. duration/expiry;
10. source leaves zone;
11. interaction with trigger/reaction where relevant;
12. unsupported schema reject;
13. package fixture coverage.

---

# 24. Anti-patternök

| ID | Név |
|---|---|
| `A-ABIL-001` | every card one-off engine class |
| `A-ABIL-002` | arbitrary natural-language runtime execution |
| `A-ABIL-003` | generic script API mutates global MatchState directly |
| `A-ABIL-004` | trigger detection = immediate mutation |
| `A-ABIL-005` | effect order implicit collection order |
| `A-ABIL-006` | condition has side effects |
| `A-ABIL-007` | targeting inside mutation without preflight |
| `A-ABIL-008` | unknown structured effect best-effort executes |
| `A-ABIL-009` | duration cleanup ad-hoc per handler |
| `A-ABIL-010` | modifier tied only to card instance, ignores zone presence |
| `A-ABIL-011` | replacement as normal reaction/effect |
| `A-ABIL-012` | support primitive = full card coverage |
| `A-ABIL-013` | template update silently changes historical semantics |
| `A-ABIL-014` | exceptional fallback bypasses event/projection/validation |

---

# 25. Verdict

AETERNA ability/effect foundation **architecture-szinten erős és bővíthető**.

Nem indokolt új ability scripting framework keresése.

A következő valódi capability gapek:
1. Reaction/Priority;
2. optional/nested choice;
3. generic cost choice;
4. replacement/prevention;
5. simultaneous trigger batch;
6. richer duration;
7. continuous dependency/layering;
8. coverage migration.

A6 blueprintnek ezeket kell sorrendbe tenni, nem új alapmotort létrehozni.
