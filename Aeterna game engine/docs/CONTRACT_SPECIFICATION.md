# AETERNA Game Engine – Contract Specification

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.6\
**Dátum:** 2026-07-22\
**Státusz:** aktív, technológiafüggetlen contract-specifikáció  
**Aktuális megvalósítási státusz:** `CONTRACT_STATUS.md`  
**Production authority:** C#/.NET  
**Aktuális repository-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7`

Ez a dokumentum az AETERNA Game Engine contract-first rétegének aktív szerkezeti specifikációja.

Nem:

- teljes rules engine-specifikáció;
- runtime package mezőszintű schema;
- ability executor;
- kártyaadatbázis;
- valamely nyelv belső osztálydokumentációja;
- minden jövőbeli mező kötelezővé nyilvánítása.

Kapcsolódó dokumentumok:

- `CONTRACT_STATUS.md`
- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `ARCHITECTURE.md`
- `TECHNOLOGY_DECISIONS.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `ABILITY_MODULE_SYSTEM.md`
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`
- `checkpoints/ENGINE_CHECKPOINT.md`

---

## 1. Contract-first alapelv

> Előbb explicit contract, utána implementáció.

Kötelező következmények:

- pontosan egy authoritative MatchState;
- state mutation csak az authoritative engine-ben;
- frontend és AI nem találgat legalitást;
- kliens action requestet küld;
- engine validál és transitiont hajt végre;
- rejected request nem okozhat részleges mutationt;
- player-facing output nem teljes MatchState dump;
- hidden information nem szivároghat;
- debug és player-visible contract külön;
- azonos state és input determinisztikus outputot ad;
- contractjelentés Python-, C#- és Godot-adapter között megőrzendő;
- a production authority C#, a Python referencia és tooling.

---

## 2. Forráselsőbbség

Contracteltérésnél:

1. hivatalos játékszabályforrás;
2. elfogadott, verziózott emberi döntés;
3. aktív Open Questions döntésnapló;
4. jelen contract-specifikáció;
5. elfogadott fixture;
6. Python reference implementation;
7. C# implementation;
8. történeti sample és migration dokumentum.

A működő kód technikai tényt bizonyíthat, de nem írhatja felül a hivatalos szabályt.

---

## 3. Contract-státuszok

| Státusz | Jelentés |
|---|---|
| `active_reference_runtime` | A Python referenciaengine használja. |
| `active_reference_projection` | A Python player/debug projection használja. |
| `proven_csharp_candidate` | A C# candidate proofban működött. |
| `active_production_foundation` | A production C# foundationben implementált és tesztelt. |
| `active_isolated` | Megvalósított és tesztelt, de nincs teljes runtime-integrációban. |
| `foundation_only` | Alapcontract létezik, teljes gameplay még nincs. |
| `planned_c5b` | A production C# foundation része. |
| `planned_gameplay` | Későbbi production gameplay-réteg. |
| `superseded` | Újabb contract felváltotta. |
| `debug_fixture` | Loader/UI/comparison tesztadat. |
| `reference_only` | Történeti vagy összehasonlító referencia. |

Az aktuális státuszokat a `CONTRACT_STATUS.md` tartalmazza.

---

## 4. Contract-rétegek

### 4.1 Runtime package

Statikus programadat:

- card definition;
- deck definition;
- lookup;
- alias;
- ability registry;
- support státusz;
- build diagnostics.

Nem:

- MatchState;
- save;
- snapshot;
- legal action;
- action request;
- event log.

### 4.2 Authoritative MatchState

A belső igaz állapot.

Tartalmazhat:

- match ID;
- seed;
- state version;
- turn és phase;
- active player;
- priority player;
- player state-ek;
- card instance registry;
- zónák;
- Domain topology és occupancy;
- Wellspring;
- turn-scoped decision state;
- pending decision;
- event sequence és log;
- match result;
- később effect, duration és reaction state.

Nem adható ki módosítható player-facing objektumként.

### 4.3 Projection

Viewer-specifikus, MatchState-ből származtatott output:

- player-visible snapshot;
- public board;
- Wellspring summary;
- legal action projection;
- visible event window;
- debug snapshot;
- később spectator és replay projection.

### 4.4 Legal action

Az engine által számított döntési lehetőség.

Nem:

- frontend-találgatás;
- state mutation;
- kártyaszöveg szabad értelmezése.

Tartalmazhat:

- action ID;
- action type/family;
- player;
- source;
- target/choice/payment context;
- enabled;
- disabled reason debug módban;
- order rank;
- payload schema;
- UI-hint, amely nem szabályforrás.

### 4.5 Action request

A játékos, UI vagy AI szándéka.

Nem bizonyít legalitást.

Minimum:

- schema version;
- request ID;
- match ID;
- player ID;
- expected state version;
- action ID;
- action type;
- payload.

### 4.6 Action response

A validálás és transition eredménye.

Minimum:

- schema version;
- request ID;
- match ID;
- accepted;
- reason;
- state version before/after;
- events;
- diagnostics;
- opcionális transition summary;
- opcionális pending decision.

### 4.7 Event

A transition strukturált történeti leírása.

Nem authoritative state.

Minimum:

- event ID;
- sequence;
- type;
- match ID;
- state version;
- actor/cause;
- structured payload;
- visibility;
- opcionális correlation/parent.

### 4.8 Diagnostics

Strukturált probléma-, warning-, audit- és supportadat.

Minimum:

- code;
- category;
- severity;
- blocking;
- safe message;
- developer message;
- source/object/action/event reference;
- structured details;
- retry vagy suggested fix.

---

## 5. EngineSession publikus határ

Tervezett production API:

- `CreateMatch`;
- `GetPlayerSnapshot`;
- `ListLegalActions`;
- `SubmitAction`;
- `GetEvents`;
- `GetMatchResult`.

Elvek:

- az EngineSession birtokolja a belső MatchState-et;
- a caller nem kap módosítható state-referenciát;
- minden mutation `SubmitAction` vagy egyenértékű validált belső transition;
- snapshot és event projection új objektum;
- request input nem módosul;
- exception helyett normál hibás inputra strukturált reject/diagnostic;
- programmer error és corrupt internal state külön exception lehet.

---

## 6. Card definition és card instance

### Card definition

Statikus package-adat:

- card ID;
- név;
- card type;
- realm;
- printed Magnitude;
- printed Aura;
- rules text;
- set/printing;
- ability/support reference.

### Card instance

Meccsspecifikus authoritative objektum:

- instance ID;
- card ID;
- owner;
- controller;
- zone;
- zone index vagy board reference;
- visibility;
- created sequence;
- zone sequence;
- activity state;
- runtime metadata.

A definition és instance nem keverhető.

---

## 7. PlayerState és zónák

PlayerState tartalmazhat:

- player ID;
- deck ID;
- deck instance ID-k;
- hand instance ID-k;
- discard instance ID-k;
- Wellspring instance ID-k;
- resource summary;
- player-scoped usage state.

Aktív vagy tervezett zónák:

- `deck`;
- `hand`;
- `discard`;
- `wellspring`;
- `domain`;
- `void`;
- szükség szerinti resolution zóna.

Listás zóna és registry kölcsönösen konzisztens.

---

## 8. Domain

Játékosonként:

- 6 Áramlat;
- 6 Horizont;
- 6 Zenit;
- 6 Pecsét-pozíció;
- 12 foglalható card slot.

A topology és occupancy külön contract.

A Pecsét nem hagyományos card occupancy slot és nem HP-objektum.

A position reference stabil.

Occupancy:

- legfeljebb egy occupant;
- occupant instance létezik;
- zone `domain`;
- controller és position kapcsolata érvényes;
- registry és occupancy kétirányú invariáns.

---

## 9. Activity state

Alapértékek:

- `active`;
- `exhausted`;
- zónán kívüli vagy nem releváns esetben null/none.

Canonical elv:

- deck/hand/discard: nincs active/exhausted gameplay activity;
- Domain/Wellspring: active vagy exhausted.

Nem azonos:

- face-up/face-down;
- revealed/hidden;
- summoning sickness;
- attack eligibility;
- ownership;
- control.

---

## 10. Snapshot és visibility

### Player-visible snapshot

Minimum:

- schema version;
- snapshot ID;
- match ID;
- viewer ID;
- state version;
- turn/phase/priority summary;
- own public/private allowed data;
- opponent redacted data;
- board;
- resource summary;
- pending decision summary;
- enabled legal actions vagy reference;
- recent visible events vagy index;
- match result.

### Visibility

- saját kéz: owner-visible;
- ellenfél kéz: count/redacted;
- deck: count-only;
- discard: public, szabály szerint;
- Domain: public;
- saját Wellspring identity: owner-visible;
- ellenfél Wellspring identity: redacted;
- Wellspring count/activity: public;
- face-down Jel: viewer szerint szűrt;
- debug: külön mód.

Player-facing output nem tartalmaz szükségtelen internal instance ID-t vagy debug payloadot.

### Fair AI

Ugyanazt az observationt, enabled legal action listát és visible eventet kapja, mint az adott emberi játékos.

---

## 11. Pending decision

A complex choice authoritative state.

Lehetséges window family-k:

- main;
- reaction;
- targeting;
- choice;
- payment;
- combat;
- system.

Minimum:

- has pending;
- window type;
- priority player;
- expected action family;
- can pass;
- state version;
- allowed choices/action IDs;
- optional safe prompt key/params.

A frontend nem tárolhat egyedüli igaz pending állapotot.

---

## 12. Legal action szabályok

Player-facing:

- csak enabled actionök.

Debug:

- enabled és disabled;
- structured disabled reason.

Action ID:

- az adott state version/legal action listához kötött;
- state változáskor érvénytelen;
- determinisztikus a jelenlegi state-ben.

A legal action lehet:

- automatic;
- forced;
- choice.

Az AI és UI csak listából választhat, de az engine requestkor újra validál.

---

## 13. Request-validáció

Mutation előtt:

1. schema;
2. request ID;
3. match;
4. player;
5. expected state version;
6. action ID/type;
7. active/priority permission;
8. source;
9. target/choice/payment;
10. current legality;
11. atomic transition plan.

Reject esetén:

- state változatlan;
- event sequence változatlan;
- request változatlan;
- nincs részleges cost;
- stabil code és reason;
- hidden information nem szivárog.

---

## 14. Payment contract

Az első card-play payment:

- printed Aura cost;
- Realm-alapú source identity;
- AETHER Core policy;
- source selection mode:
  `none | forced | choice`;
- exact payment;
- source active;
- unique source;
- owner/controller ellenőrzés;
- atomikus active → exhausted.

A payment a `play_card` transition része, nem külön előzetes mutation.

Később:

- modifier;
- temporary Aura;
- alternate cost;
- wildcard;
- replacement;
- ability cost.

---

## 15. Infusion / Beáramlás contract

Canonical technical phase:

- `infusion`.

Normál Beáramlás:

- körönként legfeljebb egy;
- opcionális;
- kéz → Wellspring;
- face-down;
- active;
- azonnal növeli Magnitúdót és elérhető Aurát;
- nem nyit automatikusan reaction windowt;
- turn-scoped status:
  `pending | performed | skipped`.

Legal action:

- perform;
- skip.

Accepted transition:

- atomikus;
- egyszeri state-version növelés;
- zone move;
- phase transition;
- visibility-safe snapshot/event.

---

## 16. Event architecture

A snapshot az állapot, az event a történet.

Rétegek:

- gameplay;
- debug;
- system;
- később explanation/audit/balance.

Viewer projection:

- egy belső ordered történetből;
- hidden-information szűréssel;
- fair AI = player view;
- debug külön.

Aktív reference eventek:

- `zone_move`;
- `turn_transition`.

Későbbi:

- activity state changed;
- payment;
- card played;
- Entity entered Domain;
- reaction;
- combat;
- ward break/restore;
- victory/defeat;
- ability resolution.

---

## 17. Aeternal és Pecsét contract

Rögzített:

- Aeternal = játékos;
- nincs HP;
- nem damage/heal target;
- Pecsét nincs HP;
- ward break/restore esemény;
- védelem nélküli sikeres direkt támadás vereség.

Preferált eventek:

- `ward_broken`;
- `ward_restored`;
- `ward_break_prevented`;
- `aeternal_unprotected`;
- `direct_attack_victory`;
- `player_defeated`.

Nyitott:

- Pecsét létrehozása;
- visibility;
- linked current;
- restore action/effect;
- combat payload;
- snapshot state.

---

## 18. AI contract

AI input:

- player-visible snapshot;
- enabled legal actions;
- visible event window;
- policy/config;
- seed.

AI output:

- választott action ID;
- payload/choice;
- decision log.

Az engine validál.

AI-hiba:

- rossz, de szabályos döntés.

Engine-hiba:

- szabálytalan request elfogadása vagy rossz transition.

Fair és debug AI elkülönül.

---

## 19. Determinizmus

Kötelező:

- seedelt random;
- stabil instance/action/event ID;
- ordinal ordering;
- explicit array-sorrend;
- canonical JSON;
- UTF-8, BOM nélkül;
- LF;
- egész számok;
- azonos input → azonos output;
- reprodukálható fixture.

---

## 20. Validáció és invariánsok

Minimum invariánsok:

- unique IDs;
- listás zóna és registry egyezik;
- egy instance egy authoritative zónában;
- owner/controller valid;
- Domain occupancy cross-reference valid;
- state version monoton;
- event sequence monoton;
- active/priority valid;
- hidden info nem szivárog;
- pending decision konzisztens;
- rejected action no mutation.

Invalid internal state blocking developer error.

---

## 21. Replay-előkészítés

Teljes replay nem korai követelmény.

Előkészítő contractok:

- action history;
- event sequence;
- state version;
- seed;
- package/ruleset/engine version;
- snapshot checkpoint lehetősége;
- correlation ID.

Replay-ready csak külön runner és determinisztikus visszaépítés után.

---

## 22. Diagnostics és player-safe hiba

Player-facing:

- rövid;
- lokalizálható;
- safe;
- nem árul el rejtett okot.

Developer:

- code;
- category;
- state/request/event reference;
- details;
- stack/exception, ha releváns.

A diagnostics nem gameplay event, de hivatkozhat rá.

---

## 23. Canonical serialization

Külön réteg:

- nem a domain modell véletlen JSON dumpja;
- stabil key ordering;
- stabil enum- és null-policy;
- explicit schema version;
- canonicalization profile;
- SHA-256.

A comparison fixture canonical SHA csak explicit contractváltozás után módosítható.

---

## 24. Production C# C.5B minimum

**Megvalósítási státusz:** `COMPLETE_AND_ACCEPTED`\
**Lezáró commit:** `931bf5571d541c752aa421a9f0626768bd8ffbe7`

Contractok:

- runtime package source/descriptor;
- `CreateMatchRequest`;
- `CreateMatchResponse`;
- `ActionRequest`;
- `ActionResponse`;
- `LegalAction`;
- `PlayerSnapshot`;
- `EngineEvent`;
- `EngineDiagnostic`;
- `MatchResult`.

Működés:

- draw;
- end turn;
- stale reject;
- events;
- snapshots;
- legal actions;
- canonical serializer;
- fixture adapter;
- Godot bridge;
- headless JSON/JSONL host.

Aktív publikus `EngineSession`-határ:

- `CreateMatch`;
- `GetPlayerSnapshot`;
- `ListLegalActions`;
- `SubmitAction`;
- `GetEvents(string viewerPlayerId, int afterSequence = 0)`;
- `GetMatchResult`.

Boundary- és visibility-követelmények:

- a publikus eventprojekció viewer-specifikus és rejtett kártyaazonosságot redaktál;
- teljes event- és debugállapot csak internal headless/teszt felületen érhető el;
- a Godot production bridge nem exportál unsafe debughozzáférést;
- null, hiányos vagy malformed create/action JSON strukturált rejectiont vagy diagnosticot ad;
- rejected input nem mutálhat state-et, state versiont vagy event sequence-et.

Bizonyítás:

- production tesztek Debug és Release: `13/13`;
- canonical expected és actual SHA: `650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`;
- canonical méret: `210730` byte;
- determinisztika: `100/100`;
- Godot pozitív és negatív production bridge smoke: PASS.

Nem része:

- Wellspring gameplay;
- infusion;
- payment;
- play_card;
- combat;
- ability execution.

---

## 25. Contractverziózás

Egy contract verziót kell emelni, ha:

- mező jelentése változik;
- kötelező mező kerül be;
- enum jelentése változik;
- visibility változik;
- canonical ordering változik;
- rejection semantics változik.

Kompatibilis bővítés lehet minor változás.

Breaking változás explicit migrationt és fixture-frissítést igényel.

---

## 26. Dokumentumkapcsolat

Aktuális implementációs állapot:

- `CONTRACT_STATUS.md`.

Történeti migráció:

- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`.

Nyitott döntések:

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

A korábbi 1.4-es, Python-reference-központú specifikáció a Git-történetben megmarad. Az 1.5-ös változat a lezárt C# authority mellett technológiafüggetlen contractjelentést tart fenn.
