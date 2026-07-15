# AETERNA Game Engine – Ability Module System

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív, technológiafüggetlen hosszú távú ability-architektúra; implementáció a runtime-nyelvi kapu és az alap gameplay-lánc után  
**Aktuális Python referencia:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum meghatározza, hogyan épüljön fel hosszú távon az AETERNA kártyaképesség-, effect- és ability-execution rendszere.

Nem:

- teljes rules engine specifikáció;
- végleges kártyaképesség-adatséma;
- runtime package specifikáció;
- kártyaaudit-dokumentum;
- a következő közvetlen programozási feladat;
- valamely runtime-nyelv előzetes kiválasztása.

A korábbi részletes tervezési változat a Git-történetben megmarad. Ez az aktív változat a jelenlegi engine-, runtime- és dokumentációs állapothoz igazított konszolidáció.

Kapcsolódó aktív dokumentumok:

- `CURRENT_OPEN_QUESTIONS.md`;
- `CURRENT_CONTRACT_STATUS.md`;
- `CURRENT_RUNTIME_PACKAGE_STATUS.md`;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`;
- `ARCHITECTURE.md`;
- `TECHNOLOGY_DECISIONS.md`;
- `CONTRACT_SPECIFICATION.md`;
- `RUNTIME_PACKAGE_SPECIFICATION.md`.

---

## 1. Jelenlegi tényleges állapot

A runtime package jelenleg:

- tartalmaz `ability_registry.json` fájlt;
- tartalmaz `engine_support.json` fájlt;
- betölt két deklarált ability modult;
- a modulokat `declared_only` állapotban kezeli;
- a kártyák engine-support státuszát `not_evaluated` értéken tartja;
- strukturált diagnostics-réteget biztosít;
- nem futtat kártyaképességeket.

Aktuális manifestállítás:

- `runtime_executes_abilities: false`.

Ezért jelenleg:

- nincs production ability executor;
- nincs általános trigger resolver;
- nincs target-, choice-, cost- vagy effect execution pipeline;
- nincs reaction, replacement vagy prevention runtime;
- a 814 runtime-kártya package-ben való jelenléte nem jelenti a képességeik engine-támogatását;
- a Godot ability registry loader nem rules engine.

A jelenlegi ability-réteg minősítése:

- adat- és loader-foundation: `working_foundation`;
- support-status modell: `foundation_only`;
- ability execution: `not_implemented`;
- teljes kártyafedettség: `not_evaluated`.

---

## 2. Prioritási hely

Az ability executor nem a következő gameplay-fejlesztés.

Kötelező előfeltételek:

1. runtime-nyelvi és integrációs döntési kapu lezárása;
2. Wellspring production integráció;
3. Beáramlás transition és resource summary;
4. Magnitúdó-preflight;
5. Aura-payment és activity mutation;
6. `play_card` action és atomikus transition;
7. legal action alap;
8. timing, phase és priority alap;
9. target- és choice-contract minimuma;
10. typed event és player-visible projection stabil alapja.

Csak ezek után indulhat az első valódi ability-executor MVP.

Ez a sorrend megakadályozza, hogy az ability rendszer:

- hiányzó alapmechanikákat saját lokális logikával pótoljon;
- párhuzamos payment-, targeting- vagy timing-rendszert hozzon létre;
- UI-node-okba rejtett szabálylogikát építsen;
- a végleges runtime-nyelvi döntés előtt nagy migrációs adósságot termeljen.

---

## 3. Alapelv

Az AETERNA kártyaképességeit hosszú távon nem kártyánként szétszórt, kézzel írt szabálykóddal kell futtatni.

Cél:

- minél több képesség structured adatokból;
- újrahasználható trigger-, condition-, cost-, target-, choice- és effect-modulokból;
- verziózott execution plan alapján;
- explicit engine-support státusszal;
- strukturált diagnostics-szal;
- typed eventekkel;
- determinisztikusan és tesztelhetően működjön.

Alapelv:

> **A nyomtatott kártyaszöveg emberi szabályszöveg. A structured ability és az ability registry programlogikai köztes réteg. Az authoritative végrehajtást kizárólag a rules engine végzi.**

---

## 4. Kötelező réteghatárok

### 4.1 Card definition

Statikus programadat:

- Card_ID;
- kártyatípus;
- Magnitúdó- és Aura-adatok;
- printed text;
- structured ability forrásmezők;
- keyword- és effectcímkék;
- source metadata.

Nem tartalmazhat mérkőzésállapotot.

### 4.2 Ability definition

Deklaratív, stabil ability-rekord:

- ability ID;
- source card ID;
- ability type;
- trigger;
- conditionök;
- costok;
- targetek;
- choice-ok;
- effectek;
- duration és limit;
- support status;
- schema és version metadata.

### 4.3 MatchState

Authoritative mérkőzésállapot:

- kártyapéldányok;
- zónák;
- controller és owner;
- activity state;
- sebzés és módosítók;
- pending decision;
- turn, phase és priority;
- event sequence;
- effect- és duration-state.

### 4.4 Execution plan

A validált ability konkrét végrehajtási terve.

Nem lehet:

- nyers kártyaszöveg újraértelmezése futás közben;
- UI által összeállított szabálylogika;
- rejtett, card-local kódelágazás dokumentált support státusz nélkül.

### 4.5 Execution result

Strukturált eredmény:

- accepted vagy rejected;
- state version before/after;
- applied costok;
- selected targetek és choice-ok;
- effect resultok;
- typed eventek;
- diagnostics;
- pending következő döntés;
- player-visible projekcióhoz szükséges változások.

---

## 5. Stabil azonosítók

Minden ability kapjon determinisztikus, stabil azonosítót.

Javasolt alap:

- `Card_ID + ability_index`;
- vagy `Card_ID + stabil structured ability group`.

Az ability ID:

- ne függjön a megjelenített magyar névtől;
- ne függjön szabad szöveges effectleírástól;
- ne változzon puszta szövegjavítás miatt, ha a programlogikai ability nem változott;
- legyen használható save-, replay-, diagnostics- és support-report hivatkozásként.

Külön azonosítandó:

- ability definition;
- runtime ability instance vagy pending resolution;
- source card instance;
- execution request;
- target és choice decision.

---

## 6. Ability fő szerkezete

Javasolt technológiafüggetlen fogalmi mezők:

- `ability_id`;
- `source_card_id`;
- `ability_type`;
- `timing`;
- `triggers`;
- `conditions`;
- `costs`;
- `targets`;
- `choices`;
- `effects`;
- `duration`;
- `limits`;
- `replacement`;
- `prevention`;
- `execution_mode`;
- `support_status`;
- `schema_version`;
- `diagnostics`;
- `metadata`.

Nem minden mező kötelező minden abilitynél.

A végleges JSON-schema csak a működő MVP és a valós kártyaaudit alapján zárható le.

---

## 7. Ability-típusok

Lehetséges fő kategóriák:

- keyword;
- static;
- triggered;
- activated;
- reaction;
- replacement;
- prevention;
- continuous;
- one-shot;
- passive.

Az ability type önmagában nem végrehajtási logika. Szerepe:

- support mérés;
- timing- és legal-action kapcsolás;
- event window kiválasztása;
- AI döntés-előkészítés;
- diagnostics és audit.

A keywordök lehetnek külön keyword registryben, de végrehajtásuk ugyanazon authoritative engine és event rendszer része marad.

---

## 8. Modulcsaládok

### 8.1 Trigger

Meghatározza, milyen authoritative event vagy phase-helyzet figyelhető.

Példakategóriák:

- kijátszás;
- Domíniumba vagy pozícióba belépés;
- támadás és harci esemény;
- sebzés, gyógyítás vagy megsemmisülés;
- Pecsét feltörése vagy visszaállítása;
- lap húzása, eldobása vagy zónamozgása;
- Aura fizetése;
- kör- és fáziskezdet/vég;
- reaction window.

A trigger canonical értékei csak a szabályforrás és LOOKUPS auditja után véglegesíthetők.

### 8.2 Condition

Meghatározza, hogy az ability alkalmazható-e.

A condition:

- nem mutál state-et;
- ugyanazon state-en determinisztikus;
- használható legal action és execution validációhoz;
- strukturált failure reasonnel tér vissza.

### 8.3 Cost

A cost nem effect.

A costot:

- az effect előtt validálni kell;
- atomikusan kell alkalmazni;
- rejection esetén nem maradhat részleges mutation;
- payment- és activity-contractokra kell építeni.

Példakategóriák:

- Aura fizetés;
- source Kimerítése;
- Entitás feláldozása;
- lap eldobása;
- zónamozgatási költség;
- alternatív vagy additional cost.

### 8.4 Target

A targetmodul:

- candidate listát generál;
- visibility- és controller-szabályt alkalmaz;
- legalitást validál;
- stabil target reference-t ad;
- nem enged frontend-találgatást.

Az Aeternal és Pecsét nem kezelhető általános HP-targetként.

### 8.5 Choice

A choice külön pending decision lehet.

Lehetséges formák:

- célpontválasztás;
- módválasztás;
- mennyiségválasztás;
- sorrendválasztás;
- payment source választás;
- replacement vagy prevention választás;
- optional trigger elfogadása vagy elutasítása.

### 8.6 Effect

Az effect végzi a validált state transitiont.

Elsőként csak már meglévő authoritative alapokra épülő effect választható.

Lehetséges későbbi modulok:

- lap húzása;
- zónamozgatás;
- Entitás sebzése vagy gyógyítása;
- activity state változtatása;
- keyword adása vagy eltávolítása;
- token létrehozása;
- stat módosítása;
- Pecsét feltörése vagy visszaállítása;
- prevention vagy replacement.

### 8.7 Duration és continuous state

Az ideiglenes vagy folyamatos hatásnak authoritative runtime state-re van szüksége.

Kötelező:

- source és effect ID;
- érintett objektumok;
- kezdő és lejárati feltétel;
- stacking és priority policy;
- eltávolítás és cleanup;
- save/replay serialization.

---

## 9. Execution pipeline

Hosszú távú fogalmi lánc:

1. runtime card definition betöltése;
2. ability definition feloldása;
3. trigger vagy action azonosítása;
4. timing és priority validáció;
5. condition preflight;
6. cost preflight;
7. target- és choice-candidate generálás;
8. szükséges player decisionök begyűjtése;
9. execution plan összeállítása;
10. teljes atomikus újravalidálás;
11. cost alkalmazása;
12. effectek determinisztikus végrehajtása;
13. state invariánsok ellenőrzése;
14. typed eventek létrehozása;
15. state version növelése;
16. legal action és player-visible snapshot újragenerálása;
17. diagnostics és trajectory rögzítése.

Rejection esetén:

- nincs részleges mutation;
- nincs gameplay event;
- strukturált reason és diagnostics készül;
- a request és input state nem módosul.

---

## 10. Legal action és pending decision

Az ability rendszer nem kerülheti meg a legal action modellt.

Legal actionként vagy pending decisionként jelenhet meg:

- activated ability;
- optional trigger;
- target selection;
- mode vagy amount választás;
- payment source választás;
- reaction pass;
- replacement vagy prevention döntés.

A frontend:

- csak a rules engine által generált opciókat jeleníti meg;
- action requestet küld;
- nem épít saját candidate listát;
- nem mutál state-et;
- nem dönti el, hogy egy ability legális-e.

---

## 11. Eventmodell

Az ability execution typed eventeket generál.

Példakategóriák:

- ability triggered;
- ability activation requested;
- target vagy choice selected;
- cost paid;
- ability resolved;
- ability rejected vagy cancelled;
- effect applied;
- effect prevented vagy replaced;
- damage, heal, zone move vagy activity change;
- token created;
- duration started vagy expired.

Kötelező elvek:

- az event nem maga az authoritative state;
- az event sorrend determinisztikus;
- minden event stabil sequence-et kap;
- player-facing és debug payload elválik;
- rejtett információ nem szivároghat;
- eventekből UI-animáció, replay és diagnostics készíthető.

---

## 12. Support státusz

Javasolt supportállapotok:

- `not_evaluated`;
- `declared_only`;
- `unsupported`;
- `partial`;
- `supported`;
- `fallback_required`;
- `blocked_invalid_data`;
- `blocked_missing_engine_feature`.

A support státusz:

- nem manuális marketingcímke;
- konkrét module-, schema- és testbizonyítékhoz kötött;
- kártyánként és abilitynként mérhető;
- build mode szerint blokkolhatja a decket vagy buildet.

Egy kártya csak akkor tekinthető teljesen támogatottnak, ha:

- minden aktív abilityje támogatott;
- a szükséges alapmechanikák működnek;
- nincs rejtett card-local fallback;
- contract-, unit- és scenario-tesztjei zöldek.

---

## 13. Fallback policy

A fallback átmeneti eszköz, nem hosszú távú alapműködés.

Fallback csak akkor használható, ha:

- külön ID-val és support státusszal látható;
- diagnostics és audit report jelzi;
- nem kerül UI-node-ba;
- ugyanazon authoritative engine API-t használja;
- van hozzá célzott teszt;
- migrációs feladat és owner tartozik hozzá.

Tilos:

- névtelen card-specific `if Card_ID == ...` elágazások szétszórása;
- frontendben végrehajtott szabályhatás;
- diagnostics nélküli partial support;
- release buildben ismeretlen vagy nem auditált fallback.

---

## 14. Runtime package és LOOKUPS

A runtime package szerepe:

- ability definition és registry szállítása;
- canonical értékek;
- schema- és version metadata;
- support státusz;
- diagnostics;
- static card reference.

A runtime package nem:

- MatchState;
- pending decision store;
- save game;
- authoritative execution log;
- rules engine.

A LOOKUPS feladata:

- controlled vocabulary;
- canonical Value;
- magyar Label;
- active/inactive státusz;
- legacy alias;
- workflow-only és runtime-supported elhatárolás;
- danger vagy audit-required jelzés.

A LOOKUPS és ability registry pontos határa külön későbbi data-contract audit.

---

## 15. Diagnostics

Minden parse-, validation- és execution-szakasz strukturált diagnostics eredményt adhat.

Példák:

- unknown trigger;
- unknown target;
- unsupported effect;
- missing parameter;
- ambiguous structured mapping;
- workflow-only érték runtime mezőben;
- card-local fallback required;
- partial support;
- invalid Aeternal/Pecsét target;
- unknown keyword;
- missing lookup;
- invalid duration;
- cyclic execution plan;
- hidden-information leak risk.

A diagnostics tartalmazzon:

- stabil code;
- severity;
- source card és ability ID;
- mező vagy module path;
- emberi magyarázat;
- blocking/non-blocking státusz;
- javasolt audit vagy implementációs lépés.

---

## 16. Build mode

Lehetséges buildmódok:

- sample;
- development;
- strict;
- audit;
- ai_test;
- balance_test;
- release_candidate.

Elvi policy:

- sample engedhet nem futtatott deklaratív elemeket;
- development warninggal továbbmehet;
- strict unknown vagy invalid modult blokkol;
- ai_test nem engedhet olyan aktív lapot, amely torzítja a szimulációt;
- release candidate nem engedhet `fallback_required`, `not_evaluated` vagy blocking diagnostics állapotú aktív kártyát.

A pontos blocking policy későbbi döntés.

---

## 17. Runtime-nyelvi semlegesség

Az ability data model és a contractok nem függhetnek attól, hogy a végleges executor:

- Python sidecarban;
- Godot .NET/C# rules libraryben;
- GDScriptben;
- vagy indokolt más runtime-ban működik.

A runtime-nyelvi döntési kapu előtt:

- nem készül teljes ability executor egyik jelöltben sem;
- nem készül két párhuzamos ability engine;
- a Python referencia ability modellje sem tekinthető automatikusan végleges termékkódnak;
- a C# vagy GDScript proof nem bővülhet kártyaképesség-rendszerré.

A runtime-döntés után is kötelező:

- közös vagy explicit mappelt ability schema;
- determinisztikus execution result;
- azonos hidden-information policy;
- összehasonlítható event és diagnostics;
- Python AI/batch tooling adapterének fenntartása.

---

## 18. Első ability-executor MVP

Az MVP csak a szükséges alapmechanikák elkészülte után indulhat.

Javasolt scope:

1. egyetlen kötelező, automatikus trigger vagy egyszerű activated ability;
2. egy condition nélküli és egy egyszerű conditionnel rendelkező példa;
3. legfeljebb egy target;
4. legfeljebb egy egyszerű cost;
5. egy vagy két már létező state transitionre épülő effect;
6. strukturált accepted és rejected result;
7. typed event;
8. player-visible snapshot ellenőrzés;
9. determinisztikus scenario;
10. Python reference és product runtime összevetése, ha eltérő nyelvűek.

Nem megfelelő első effect:

- teljes combatot igénylő képesség;
- reaction stack;
- replacement/prevention;
- komplex Sík continuous effect;
- több target és több choice;
- tokenek teljes ökoszisztémája;
- kártyaláncok vagy rekurzív abilityk.

Az első konkrét effectet a már elkészült engine-contractok és a kártyaadat-audit alapján kell kiválasztani, nem a jelen dokumentum előre rögzített példalistájából.

---

## 19. Kötelező szabályi korlátok

### 19.1 Aeternal

- nem HP-objektum;
- nem kaphat sebzést;
- nem gyógyítható;
- csak explicit, auditált szabályhatás célozhatja;
- nem használható általános `entity` targetként.

### 19.2 Pecsét

- nem HP-objektum;
- feltörés és visszaállítás külön állapot- és eventmodell;
- nem kezelhető általános damage/heal effecttel;
- Áramlat-kapcsolata canonical topologyból származik.

### 19.3 Token

- létrehozott runtime instance;
- Domínium elhagyásakor megszűnik;
- alapból Aktív, ha szabály vagy hatás másként nem rendelkezik;
- nem kerülhet tartósan deck-, hand- vagy discard-definitionként kezelésre.

### 19.4 Hidden information

- opponent hand és deck tartalma nem szivároghat;
- target candidate sem fedhet fel tiltott Card_ID-t;
- diagnostics player-facing formája külön redakciót igényel;
- AI ugyanazt az observation-policyt használja, mint a játékos.

---

## 20. Tesztelési követelmények

Minden támogatott modulhoz szükséges:

- unit test;
- invalid input test;
- no-mutation-on-rejection test;
- deterministic serialization test;
- hidden-information test;
- event ordering test;
- state invariant test;
- legal action vagy pending decision test;
- player-visible snapshot test;
- replay/trajectory-kompatibilis artifact, amikor a replay alap elkészül.

Komplexebb module-oknál:

- property test;
- differential test;
- fuzz vagy malformed payload test;
- hosszabb AI-vs-AI scenario;
- save/load round-trip.

---

## 21. Nyitott döntési kapuk

A részletes történeti kérdések központi regisztere továbbra is:

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`;
- current kivonat: `CURRENT_OPEN_QUESTIONS.md`.

Ability-specifikus nyitott témák:

### Adatmodell

- structured ability részletessége;
- ability ID végleges képzése;
- LOOKUPS és registry határa;
- execution plan tárolási helye;
- schema migration és backward compatibility.

### Trigger és timing

- kötelező és opcionális triggerek;
- több azonos trigger sorrendje;
- ki választ trigger-sorrendet;
- trigger priority és reaction window;
- eventből származó triggerlánc és ciklusvédelem.

### Cost és payment

- automatikus vagy kézi Aura-forrásválasztás;
- alternatív és additional cost;
- cost visszaellenőrzése resolution előtt;
- rollback és atomikus végrehajtás.

### Target és choice

- target candidate contract;
- több target/effect mapping;
- target order;
- invalid target resolution policy;
- hidden-information és owner/controller kezelés;
- pending decision serialization.

### Effect és duration

- effect ordering;
- partial resolution engedhetősége;
- continuous modifier layering;
- stacking;
- end-of-turn és más expiry;
- source eltűnésének hatása;
- replacement és prevention sorrend.

### Keyword és token

- keyword registry vagy ability module;
- parametrizált keywordök;
- ideiglenes keyword forrása és lejárata;
- token definition és runtime instance határa;
- token másolás és transform későbbi modellje.

### Support és fallback

- mikor `partial`, `unsupported` vagy `fallback_required`;
- release blocking policy;
- card-local fallback maximális scope-ja;
- support coverage számítása;
- meglévő 814 kártya auditbatch-sorrendje.

### Runtime és AI

- product runtime adaptere a Python batch toolinghoz;
- ability executor differential comparison;
- fair AI legal action és observation;
- gyorsított batch és balance telemetry;
- replay és save/load contract.

Ezeket nem kell egyszerre lezárni. Minden döntés a legkisebb következő implementálható vertical slice előtt válik kötelezővé.

---

## 22. Következő feladatok sorrendje

### Most

1. runtime-nyelvi audit és proof;
2. Wellspring, Beáramlás, Magnitúdó/Aura és `play_card` alapok;
3. timing, phase, priority és legal action minimum;
4. current contractok és visibility-policy stabilizálása.

### Ezután

5. ability definition minimális schema;
6. support-status és diagnostics policy;
7. első execution plan;
8. egy szűk ability-executor MVP;
9. product runtime és Python reference comparison;
10. fokozatos kártyafedettségi audit.

### Nem indul még

- teljes ability library;
- teljes reaction stack;
- replacement/prevention rendszer;
- minden keyword;
- minden kártya automatikus futtatása;
- card-local fallback tömeges létrehozása;
- teljes Sík continuous engine;
- ability execution UI-node-okban.

---

## 23. Záró állapot

- Az ability module rendszer szükséges hosszú távú engine-réteg.
- A jelenlegi registry és support report csak deklaratív foundation.
- Nincs működő ability executor.
- A data modelnek és contractoknak runtime-nyelvtől függetlennek kell maradniuk.
- A végleges executor nyelvét a runtime-nyelvi döntési kapu választja ki.
- Az ability implementáció csak az alap gameplay- és decision-contractok után indulhat.
- A fallback átmeneti, látható és tesztelt megoldás lehet, de nem válhat fő architektúrává.
- Minden ability végrehajtás authoritative state transition, typed event, diagnostics és player-visible projection része.
- Új párhuzamos ability-dokumentum nem készül; a current tervet ebben a fájlban kell karbantartani.