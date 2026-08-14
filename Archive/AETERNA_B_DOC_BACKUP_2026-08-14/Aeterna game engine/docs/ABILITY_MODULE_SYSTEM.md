# AETERNA Game Engine – Ability Module System

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2  
**Dátum:** 2026-07-20  
**Státusz:** aktív, hosszú távú ability-architektúra; production implementáció a core gameplay-alapok után  
**Production authority:** C#/.NET  
**Adat- és buildréteg:** Python  
**Aktuális repository-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Ez a dokumentum az AETERNA kártyaképesség-, keyword-, trigger-, effect- és ability-execution rendszerének hosszú távú felépítését rögzíti.

Nem:

- teljes rules engine-specifikáció;
- végleges kártyaképesség-JSON schema;
- runtime package-specifikáció;
- kártyaaudit-napló;
- a következő közvetlen programozási feladat;
- működő ability executor leírása.

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

A runtime package jelenleg:

- tartalmaz `ability_registry.json` fájlt;
- tartalmaz `engine_support.json` fájlt;
- két deklarált ability modult kezel;
- a modulok státusza `declared_only`;
- a kártyák supportja `not_evaluated`;
- diagnostics- és loader-foundationt biztosít;
- nem futtat kártyaképességet.

Manifestállítás:

- `runtime_executes_abilities: false`.

Nincs még:

- production ability executor;
- trigger resolver;
- target/choice/cost/effect pipeline;
- reaction, prevention vagy replacement runtime;
- teljes keyword support;
- teljes kártyafedettség.

A package-ben szereplő 814 kártya nem jelent 814 engine-supported képességet.

---

## 2. Authority és réteghatár

### Python

Feladata:

- structured adatok feldolgozása;
- ability registry build;
- normalizálás;
- support-status számítás;
- diagnostics;
- execution plan generálás, ha később szükséges;
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

## 3. Kötelező előfeltételek

Az ability executor nem a következő gameplay-feladat.

Előbb szükséges:

1. C.5B production C# engine foundation;
2. Wellspring production state;
3. player-visible Wellspring;
4. `infusion` transition;
5. Magnitúdó-preflight;
6. Aura-payment;
7. activity mutation;
8. `play_card`;
9. Entity Domain-placement;
10. phase és priority minimum;
11. target és choice contract minimum;
12. stabil typed event és projection.

Csak ezután indulhat az első production ability vertical slice.

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

### Execution plan

Az ability modulok, paraméterek, sorrendek és kapcsolatok normalizált végrehajtási terve.

Korai MVP-ben nem kötelező minden kártyához.

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

Javasolt execution mode:

- `fully_modular`;
- `partially_modular`;
- `card_local_fallback`;
- `manual_only`;
- `unsupported`;
- `not_checked`.

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
- későbbi execution plan.

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

Elfogadott irány:

- reaction windowt a core engine kezeli;
- Burst és Jel ugyanazon keretrendszerben, eltérő subtype-pal kezelhető;
- prevention és replacement ugyanahhoz a timingrendszerhez kapcsolódik;
- nincs korai kötelező teljes stack/chain;
- az első modell pending reaction queue lehet.

Nyitott:

- több trigger sorrendjének játékosi választása;
- nested reaction;
- replacement prioritás;
- prevention és replacement lánc;
- optional trigger timeout/pass;
- részleges resolution.

---

## 14. Card-local fallback

A card-local fallback egyedi, kártyaspecifikus C# logika.

Státusza:

- átmeneti kivétel;
- nem hosszú távú alap;
- explicit diagnostics;
- support report;
- migrációs lista.

Release-ben nem futhat csendben.

Development/debug módban csak akkor engedhető, ha:

- külön jelölt;
- tesztelt;
- nem szivárogtat rejtett információt;
- nem torzít fair balance futást észrevétlenül.

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

## 18. Első production ability vertical slice

Csak core gameplay után.

Jó első module-jelöltek lehetnek:

- egyszerű kártyahúzás;
- Entitás sebzése;
- Entitás gyógyítása;
- egyszerű keyword adása kör végéig;
- egyszerű token létrehozás;
- ward restore vagy break prevention, ha a Pecsét-spec kész.

Kiválasztási feltétel:

- auditált kártya;
- egyértelmű szabály;
- kevés target;
- nincs reaction stack;
- nincs replacement;
- nincs összetett duration;
- teljes positive/negative fixture.

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

Közvetlenül nem ability executor következik.

Sorrend:

1. C.5B production engine foundation;
2. Wellspring;
3. infusion;
4. Magnitúdó;
5. payment;
6. play_card;
7. Entity placement;
8. phase/priority;
9. target/choice minimum;
10. első simple ability vertical slice.

A pontos nyitott kérdések:

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

Az implementációs állapot:

- `CONTRACT_STATUS.md`;
- `PROTOTYPE_STATUS.md`.
