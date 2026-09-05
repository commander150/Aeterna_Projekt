# AETERNA Game Engine – Ability Module System

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.5
**Dátum:** 2026-09-05
**Státusz:** aktív, hosszú távú ability-architektúra és a meglévő production ability/effect foundation továbbfejlesztési kerete
**Production authority:** C#/.NET
**Adat- és buildréteg:** Python
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9` – Combat + Pecsét Foundation C0–C6

Ez a dokumentum az AETERNA kártyaképesség-, keyword-, trigger-, effect- és ability-execution rendszerének hosszú távú felépítését rögzíti.

Nem:

- teljes rules engine-specifikáció;
- végleges kártyaképesség-JSON schema;
- runtime package-specifikáció;
- kártyaaudit-napló;
- a következő közvetlen programozási feladat;
- a teljes production ability coverage vagy minden kártyaképesség végleges executor-specifikációja.

Kapcsolódó aktív dokumentumok:

- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `CONTRACT_STATUS.md`
- `RUNTIME_PACKAGE_STATUS.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `ARCHITECTURE.md`
- `TECHNOLOGY_DECISIONS.md`
- `checkpoints/ENGINE_CHECKPOINT.md`

---

## 1. Jelenlegi tényleges állapot

Két külön réteget kell megkülönböztetni.

### 1.1 Runtime package support metadata

A statikus runtime package jelenleg:

- tartalmaz `ability_registry.json` fájlt;
- tartalmaz `engine_support.json` fájlt;
- deklarált ability modulokat kezel;
- metadata-szinten `declared_only` / `not_evaluated` állapotot hordozhat;
- korábbi sample/metadata rétegben `runtime_executes_abilities: false` érték szerepelhet.

Ez package support/coverage metadata, nem production engine capability statement.

### 1.2 Production C# ability/effect runtime foundation

A production C# engine-ben már megvalósult foundation többek között:

- `CanonicalAbilityCatalog`;
- `CanonicalAbilityTemplateCompiler`;
- effect condition evaluator;
- target filter evaluator;
- `CanonicalTargetResolver`;
- `CanonicalTriggerResolver`;
- `CanonicalEffectExecutor`;
- template/collection/zone effect runtime;
- continuous effect state;
- modifier/keyword/duration runtime;
- damage/vitals/lethal integration;
- draw/reference integration;
- Reaction / Priority Foundation v1;
- Combat + Pecsét Foundation C0–C6;
- terminal Aeternal / `MatchResult` outcome integration.

Current production base:

`0862e1002dbef81ee203852714d377592272a0e9`

Ez továbbra sem teljes kártyafedettség.

### 1.3 Ami továbbra sincs teljesen kész

- teljes card ability coverage;
- teljes keyword coverage;
- generic prevention/replacement;
- speciális future timing/trigger activation policy és batch-order kivételek;
- minden komplex compound target/payment/choice forma;
- special Seal restore/ward ability payload;
- teljes Expansion-specifikus ability coverage;
- package support matrix teljes migrációja.

A package-ben szereplő teljes kártyaszám nem jelent ugyanennyi engine-supported képességet.

Current elv:

`EngineCapability != ContentCoverage`

## 2. Authority és réteghatár

### Python

Feladata:

- structured adatok feldolgozása;
- ability registry build;
- normalizálás;
- support-status számítás;
- diagnostics;
- CanonicalAbilityGraph/registry build és validáció;
- ephemeral execution/transition plan tooling támogatása csak ott, ahol erre ténylegesen szükség van;
- coverage és audit report.

Nem futtat production gameplayt.

### C#

Feladata:

- ability precondition;
- cost;
- targeting;
- choice;
- effect resolution;
- trigger és reaction hook;
- state mutation;
- typed event;
- diagnostics;
- player-visible projection.

A production ability executor kizárólag C#-ban lehet authoritative.

### Godot/GDScript

Feladata:

- registry és support megjelenítése;
- target/choice/payment UI;
- event animáció;
- debug viewer;
- action request összeállítása.

Nem értelmezhet önállóan kártyaszöveget és nem futtathat párhuzamos ability-logikát.

---

## 3. Előfeltételek és jelenlegi dependency-k

Az első production ability/effect foundation már nem jövőbeli feladat.

### Teljesült dependency-k

- C.5B production C# engine foundation;
- Wellspring production state;
- player-visible Wellspring;
- canonical `infusion`;
- Magnitúdó-preflight;
- Aura-payment preflight;
- activity mutation;
- `play_card`;
- Domain placement;
- Explicit Phase Foundation v1;
- target resolver foundation;
- typed event és projection;
- canonical card/ability runtime binding;
- Reaction / Priority Foundation v1;
- `ReactionWindow` / `ResolutionStack` / queued-trigger foundation;
- Combat + Pecsét Foundation C0–C6;
- Combat ReactionWindow integration;
- SealBreak / Surge / Aeternal terminal integration.

### Current next gate

`VS1_READINESS_REQUIRED`

A következő ability/content munka nem általános, előre kijelölt ability-expansion.

Előbb a két canonical VS1 deck tényleges requirementjeit kell auditálni:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

Csak az a dependency kötelező VS1 előtt, amely:

1. valamelyik canonical VS1 deck tényleges card/mechanic működéséhez kell; vagy
2. általános rules-correct / deterministic / viewer-safe invariáns.

Generic prevention/replacement, complex nested choice, future special timing vagy package support-matrix
csak akkor válik VS1 blockeré, ha a readiness audit konkrétan igényli.

## 4. Alapfogalmak

### Ability

Egy kártyához tartozó szabályi egység.

Tartalmazhat:

- triggert;
- timingot;
- feltételt;
- költséget;
- célpontot;
- választást;
- effectet;
- durationt;
- optional/mandatory jelleget;
- event- és diagnostics-következményt.

### Module

Újrahasználható, explicit schema és viselkedés alapján futó végrehajtási egység.

### Effect tag

Audit-, keresési és coverage-címke.

Az effect tag önmagában nem executable module.

### CanonicalAbilityGraph, ResolutionContext és execution plan

A persisted canonical ability-definíció alapja a `CanonicalAbilityGraph`.

Futás közben az ability/effect végrehajtás contextje a `ResolutionContext`
és az authoritative MatchState.

Nem kötelező univerzális, persisted `AbilityExecutionPlan` minden abilityhez.

Egyszerű effect közvetlen typed executionnel futhat.
Komplex effectnél az engine készíthet immutable, ephemeral typed execution/transition plant,
ha az atomic preflight vagy a determinisztikus feloldás ezt igényli.

Az ephemeral plan runtime részlet, nem új rules authority.

---

## 5. Ability registry

A `ability_registry.json` a runtime package része vagy közvetlenül hozzá tartozó fájl.

Minimum rekord:

- `ability_id`;
- `source_card_id`;
- `ability_index`;
- `module_id` vagy structured reference;
- `support_status`;
- `execution_mode`;
- `trigger_summary`;
- `target_summary`;
- `diagnostics_refs`;
- `fallback_required`;
- `manual_review_required`;
- schema version.

Az `ability_id` determinisztikus.

Nem függhet:

- véletlentől;
- buildidőtől;
- instabil szövegtől;
- meccsspecifikus instance ID-től.

---

## 6. Support status és execution mode

Javasolt support státuszok:

- `supported`;
- `partial`;
- `unsupported`;
- `not_checked`;
- `fallback_required`;
- `manual_review_required`.

Current execution-architecture kategóriák:

- `canonical_graph`;
- `compiled_template`;
- `exception_module`;
- `unsupported`;
- `not_evaluated`.

A konkrét registry enumok később schema-verzióval változhatnak,
de productionben silent/implicit fallback nem megengedett.

A `fallback_required` külön migration/coverage diagnostic lehet;
nem production execution mode.

Elvek:

- unsupported modul szerepelhet registryben;
- unsupported nem futhat csendben;
- aktív tesztdeckben unsupported/not-checked tartalom blocking lehet;
- partial eredmény külön diagnosticsot és coverage-jelölést kap;
- support státusz nem azonos a kártya balanszával.

---

## 7. Structured adatok szerepe

A kártyaszöveg emberi szabályszöveg.

A structured adat programlogikai köztes réteg.

A structured mezők rövid távú szerepe:

- audit;
- keresés;
- support becslés;
- diagnostics;
- registry build;
- module-jelölt képzés;
- CanonicalAbilityGraph-, template- vagy module-jelölt képzés.

A structured mező nem válik automatikusan executable logikává.

Új mező csak akkor készül, ha:

- ismétlődő;
- konkrét;
- végrehajtáshoz szükséges;
- meglévő mezővel nem írható le biztonságosan;
- schema és validáció rendelhető hozzá.

Példák későbbi kapcsolómezőkre:

- `ability_group`;
- `effect_order`;
- `target_ref`;
- `condition_ref`;
- `choice_ref`;
- `duration_ref`.

---

## 8. Module-szerződés

Egy production module csak akkor nevezhető támogatottnak, ha van:

- stabil `module_id`;
- input parameter schema;
- precondition;
- valid target/choice szabály;
- authoritative transition;
- output/result contract;
- typed event;
- diagnostics code;
- hidden-information policy;
- positive fixture;
- negative fixture;
- deterministic test;
- state-invariant teszt;
- C# implementation.

A module nem olvashat és nem értelmezhet futás közben szabad természetes nyelvű kártyaszöveget.

---

## 9. Trigger és timing

A trigger nem önálló UI-funkció.

A core C# timing/priority rendszer feladata:

- eventfigyelés;
- trigger-jelöltek összegyűjtése;
- kötelező/opcionális megkülönböztetés;
- reaction window nyitása;
- sorrend;
- pass;
- resolution;
- lezárás.

Az ability module:

- triggerfeltételt deklarál;
- reaction/prevention/replacement lehetőséget ad;
- payloadot szolgáltat.

A core engine marad az authority.

---

## 10. Targeting és choice

Egyszerű target:

- a legal action vagy play request payload része lehet.

Komplex target:

- külön authoritative pending decision;
- több lépcső;
- sorrend;
- cancel/return policy;
- state-version guard;
- player-safe object reference.

A frontend:

- kiemelheti az engine által megadott targeteket;
- nem dönthet végleges legalitásról.

Invalid target esetén a production C# engine rejectel vagy explicit szabály alapján részlegesen old fel.

---

## 11. Cost és payment

Az ability cost különül el a normál card-play Aura-költségtől.

Későbbi cost típusok lehetnek:

- Aura;
- source exhaustion;
- sacrifice;
- discard;
- life/ward jellegű, csak ha szabály szerint értelmes;
- counter removal;
- once-per-turn usage;
- choice;
- alternate cost.

A cost:

- preflight része;
- atomikus transitionnel kerül kifizetésre;
- hiba esetén nem okozhat részleges mutationt.

Aeternal HP-költség nem használható, mert az Aeternal nem HP-objektum.

---

## 12. Effect pipeline

Egy effect feldolgozása:

1. module és schema validáció;
2. source és controller;
3. timing;
4. condition;
5. target/choice;
6. cost;
7. replacement/prevention;
8. transition;
9. event;
10. projection;
11. diagnostics;
12. invariant check.

Az effectek sorrendje explicit.

Az effect tag sorrendje nem execution order.

---

## 13. Reaction, prevention és replacement

### Current Reaction/Priority authority

Reaction / Priority Foundation v1:

`COMPLETE_AND_ACCEPTED`

Lezáró commit:

`f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`

Current core többek között:

- authoritative `ReactionWindow`;
- engine-issued `react` / `pass_priority`;
- non-initiator-first policy, ha mindkét player eligible;
- single-responder closure;
- két-player window két egymást követő passzal zár;
- nested reaction;
- canonical `ResolutionStack`;
- LIFO;
- final revalidation;
- queued trigger + post-resolution checkpoint/FIFO;
- viewer-safe pending projection.

### Combat-integráció

Combat + Pecsét C0–C6:

`COMPLETE_AND_ACCEPTED`

A combat-specifikus ReactionWindow pontok productionben aktívak.

Ability-modul szerepe:

- trigger/reaction jogosultság és payload deklarálása;
- a core timing state-et nem helyettesíti;
- a modul nem tarthat saját párhuzamos priority/stack authorityt.

### Ami továbbra is részleges

- generic prevention/replacement exact contract;
- complex nested non-Reaction decision;
- összetett retarget/replacement/prevention részletek;
- future explicit special timing / strict-event policy;
- konkrét content által igényelt további trigger-ordering kivételek.

A Reaction/Priority és Combat current core lezárása nem jelenti automatikusan
minden prevention/replacement vagy special timing ability támogatását.

## 14. Exception module és migration fallback

Silent vagy implicit runtime fallback tilos.

A `fallback_required` jelölés használható migration/coverage diagnosticsként,
amikor egy kártya még nem írható le a production structured execution modellel.
Ez önmagában nem jogosít futás közbeni ad hoc fallbackra.

Ritka, tartós kivételként explicit typed C# `exception_module` megengedhető,
ha mind teljesül:

- stabil registry/module ID;
- explicit scope;
- deterministic behavior;
- ugyanaz a validation/atomicity/event/projection contract, mint más production executionnél;
- positive és negative fixture;
- látható coverage/support státusz;
- nincs arbitrary reflection/eval/script;
- nincs rejtett global mutable API.

Ha egy exception pattern ismétlődik,
shared primitive/template/graph irányba kell migrálni.

A historical `card_local_fallback` fogalom ezért nem current production execution mode.

---

## 15. Keyword registry

A keyword registry minimuma:

- canonical keyword ID;
- Label_HU;
- rules reference;
- category;
- support status;
- required timing/event window;
- module vagy core rule kapcsolat;
- diagnostics;
- version.

Alap keywordök:

- Gyorsaság;
- Oltalom;
- Hasítás;
- Légies;
- Métely;
- Harmonizálás;
- Rezonancia;
- Visszhang;
- Riadó;
- Kényszerítés.

Nem kell mindet egyszerre támogatni.

Combatfüggő keyword combat után, reactionfüggő keyword reaction engine után kerülhet production supportba.

---

## 16. Aeternal és Pecsét

Kötelező alap:

- Aeternal nem HP-objektum;
- nem damage target;
- nem heal target;
- Pecsét nem HP-objektum;
- Pecsét feltörés/visszaállítás esemény;
- explicit ward effectek szükségesek.

Tiltott vagy kerülendő:

- `player_damage`;
- `aeternal_damage`;
- `heal_aeternal`;
- `seal_damage`;
- `ward_damage`;
- `ward_hp_change`.

Preferált:

- `ward_break`;
- `ward_restore`;
- `ward_break_prevent`;
- `aeternal_unprotected`;
- `direct_attack_victory`;
- `player_defeated`.

A részletes target és payload a rules audit után készül.

---

## 17. Execution plan

Három szint:

1. nincs plan – csak audit/support;
2. simple plan – kevés egyszerű ability;
3. generated plan – stabil modulrendszer után.

Javasolt plan mezők:

- schema version;
- ability ID;
- ordered steps;
- module ID;
- parameters;
- source/target/choice refs;
- condition;
- optional flag;
- duration;
- failure policy;
- event hints;
- diagnostics refs.

A Python builder generálhat plan-t.

A C# executor validálja és futtatja.

A Godot megjeleníti, de nem authoritative executor.

---

## 18. Production ability foundation és következő coverage-szakasz

Az első production ability/effect vertical slice foundation szinten megvalósult,
és azóta ugyanebbe az authoritative C# rendszerbe integrálódott a Reaction/Priority
és a Combat/Pecsét C0–C6 layer is.

Current production foundation többek között:

- canonical ability catalog;
- compiled template path;
- effect condition/target resolution;
- effect executor;
- continuous effect state;
- modifier/keyword/duration;
- damage/vitals/lethal;
- draw/reference;
- Reaction/Priority;
- Combat/Pecsét event és timing integration;
- Seal/Aeternal outcome hooks.

Current production base:

`0862e1002dbef81ee203852714d377592272a0e9`

### Coverage-elv

A következő általános ability-bővítés nem automatikus roadmap-lépés.

Current sorrend:

```text
canonical VS1 deckek
→ card/mechanic requirement inventory
→ existing capability mapping
→ unsupported blocker azonosítás
→ csak blockerre finite contract/module/executor work
→ targeted regression
```

A teljes 814-card vagy teljes repository-content coverage nem VS1 előfeltétel.

Package support metadata és engine capability továbbra is külön réteg;
a support matrix csak explicit coverage audit alapján frissíthető.

## 19. Tesztelés

Minden module esetén:

- schema validation;
- unsupported case;
- valid source;
- invalid source;
- valid target;
- invalid target;
- cost success/fail;
- atomicity;
- determinism;
- hidden-information;
- event payload;
- diagnostics;
- C# unit/integration;
- Godot bridge regression;
- Python reference összevetés, ha van.

A teljes kártyafedettséget coverage report méri.

---

## 20. Nem automatikus VS1-követelmény

VS1 előtt nem szükséges automatikusan:

- minden kártya teljes futtatása;
- minden keyword;
- teljes generic prevention/replacement framework;
- minden compound target/payment/choice schema;
- minden special timing policy;
- teljes Expansion ability coverage;
- teljes package support-matrix migráció;
- teljes replay-rendszer;
- teljes tanuló AI;
- teljes balanszaudit.

Ezek közül bármelyik kötelezővé válhat,
ha a két canonical VS1 deck ténylegesen használja,
vagy ha általános rules-correct / deterministic / viewer-safe invariáns.

A VS1 readiness scope nem csökkenti a hosszú távú ability-architektúra érvényességét.

## 21. Következő lépések

A production ability/effect, Reaction/Priority és Combat/Pecsét foundation már létezik;
nem kell újra végigjárni a történeti dependency-sort.

Current next gate:

`VS1_READINESS_REQUIRED`

Következő dependency-sorrend:

1. `DECK-IGN-HAM-VS1-001` és `DECK-AQU-MOR-VS1-001` card/mechanic inventory;
2. minden szükséges ability/mechanic mapping a current C# capabilityhez;
3. unsupported vagy partial blocker lista;
4. csak blockerre finite contract/module/executor bővítés;
5. targeted C# + reference/determinism/Godot regression;
6. package support/coverage metadata csak a ténylegesen auditált scope-ban;
7. simple fair AI + match orchestration;
8. minimal playable Godot és VS1 acceptance.

Nem current blocker önmagában:

- generic prevention/replacement;
- future special timing;
- full content coverage;
- teljes package support matrix.

Combat-specifikus ability support már nem vár külön combat foundationre:
a Combat + Pecsét Foundation C0–C6 `COMPLETE_AND_ACCEPTED`.

Current OQ aggregate:

`52 answered / 15 partly_answered / 7 deferred / 0 open`.
