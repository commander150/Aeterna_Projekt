# AETERNA Game Engine – Ability Module System

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.4
**Dátum:** 2026-08-16
**Státusz:** aktív, hosszú távú ability-architektúra és a meglévő production ability/effect foundation továbbfejlesztési kerete
**Production authority:** C#/.NET
**Adat- és buildréteg:** Python
**Szinkronizációs repository-bázis:** `743c00d85ddc60bbbc70715fefab8ffc9dacbdae`
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95`

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
- `runtime_executes_abilities: false` értéket deklarál.

Ez a package support/coverage metadata állapota.

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
- draw/reference integration.

Ez nem teljes kártyafedettség.

### 1.3 Ami továbbra sincs teljesen kész

- teljes card ability coverage;
- teljes keyword coverage;
- Reaction/Priority runtime;
- prevention/replacement;
- speciális timing/trigger activation policy és batch-order kivételek;
- minden komplex target/choice forma;
- package support matrix teljes migrációja.

A package-ben szereplő teljes kártyaszám nem jelent ugyanennyi engine-supported képességet.


---

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
- explicit phase foundation;
- target resolver foundation;
- typed event és projection;
- canonical card/ability runtime binding.

### Következő nagy ability-bővítés előtt szükséges

- Reaction/Priority minimum contract;
- pending reaction/choice state;
- az adott bővítési slice által ténylegesen igényelt prevention/replacement contract;
- speciális timing/activation/batch-order policy, ha konkrét content igényli;
- package support/coverage matrix migráció;
- első hivatalosan támogatott effect/keyword készletek explicit coverage-listája.

Az ability runtime továbbfejlesztése csak ezek közül a ténylegesen szükséges dependency-k lezárása után terjeszthető ki.


---

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

A hivatalos 1.4.3v alapján már rögzített reaction-alapok:

- a reaction windowt az authoritative core engine nyitja és zárja;
- ha mindkét játékos reagálhat, először az eseményt nem kezdeményező játékos kap lehetőséget;
- a játékos passzolhat;
- két egymást követő passz lezárja az ablakot;
- reakciók egymásra épülhetnek;
- feloldás visszafelé történik;
- feloldáskor a releváns target/feltételek újraellenőrizendők;
- lezárt eseményre nincs visszamenőleges reakció.

Ability-modul szerepe:

- trigger/reaction jogosultság és payload deklarálása;
- a core timing state-et nem helyettesíti;
- a modul nem tarthat saját párhuzamos priority/stack authorityt.

Current official/current-default elhatárolás:

- simultaneous trigger ordering általános alapja official;
- mandatory/optional trigger semantics official;
- ordinary trigger RC2 current defaultja queued trigger + post-resolution checkpoint;
- same-timing batch az official simultaneous ordering szerint rendeződik.

Továbbra is részleges/nyitott technikai kapu:

- prevention/replacement exact contract;
- nested pending decision/reaction;
- komplex multi-part resolution, retarget és replacement/prevention részletei;
- exact public reaction-state/event projection;
- combat-specifikus reaction pontok production integrációja;
- jövőbeli special timing/strict-event policy.

Az első Reaction/Priority foundation nem keverendő össze a combat implementációval.


---

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

Az első production ability/effect vertical slice már megvalósult foundation szinten.

Aktív production komponensek többek között:

- ability catalog;
- template compiler;
- condition evaluation;
- target filter/resolver;
- trigger resolver foundation;
- effect executor;
- continuous effects;
- modifier/keyword/duration;
- damage/vitals/lethal;
- draw/reference integration.

Következő coverage-bővítésnél jó jelöltek továbbra is lehetnek:

- egyszerű kártyahúzás;
- Entitás sebzése;
- Entitás gyógyítása;
- egyszerű keyword adása meghatározott durationnel;
- támogatott token/collection/zone effect;
- ward effect csak a Pecsét-spec után.

Kiválasztási feltétel:

- auditált kártya;
- egyértelmű canonical szabály;
- ismert target/condition;
- támogatott timing;
- nincs tisztázatlan reaction/replacement;
- positive/negative fixture;
- deterministic invariant teszt.

A következő általános ability-bővítés jelenleg a Reaction/Priority contracttól függ, nem a már elkészült Wellspring/`play_card` alaptól.


---

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

## 20. Nem cél az első MVP-ben

- minden kártya teljes futtatása;
- minden keyword;
- teljes trigger stack;
- minden prevention/replacement;
- teljes Sík continuous-effect rendszer;
- teljes combat ability-rendszer;
- automatikus természetesnyelv-értelmezés;
- csendes fallback;
- teljes tanuló AI;
- teljes balanszaudit.

---

## 21. Következő lépések

A production ability/effect foundation már létezik; nem kell újra végigjárni a C.5B → Wellspring → Infusion → `play_card` történeti sort.

Következő dependency-sorrend:

1. Reaction / Priority hivatalos rules audit;
2. minimal pending/reaction contract;
3. prevention/replacement és multi-trigger fennmaradó kapuk pontosítása;
4. Reaction/Priority production foundation;
5. ezután célzott ability coverage-bővítés;
6. package support/coverage matrix fokozatos migrációja.

Combat-specifikus ability support csak a külön combat foundation után bővíthető.

A pontos nyitott kérdések:

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

Az implementációs állapot:

- `CONTRACT_STATUS.md`;
- `PROTOTYPE_STATUS.md`.
