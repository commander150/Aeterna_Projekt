# AETERNA Game Engine – Contract Specification

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.9
**Dátum:** 2026-08-14
**Státusz:** aktív, technológiafüggetlen contract-specifikáció
**Aktuális megvalósítási státusz:** `CONTRACT_STATUS.md`
**Production authority:** C#/.NET
**Aktuális repository-bázis:** `7af5bf7fec7b762ec41d1368b072ff6a3d818f5e` – `docs: update project guidance after OQ and learning sync`

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
- `REACTION_PRIORITY_CONTRACT.md`
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

Az aktuális státuszokat a `CONTRACT_STATUS.md` tartalmazza. A `planned_c5b` és más korábbi planning jelölések történeti tervezési státuszok; nem írhatják felül a későbbi production implementációt.

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

Tartalmazhat/production foundationben már tartalmaz többek között:

- match ID;
- seed;
- state version;
- turn number;
- canonical phase;
- `starting_player_id`;
- active player;
- priority player;
- player state-ek;
- card instance registry;
- deck/hand/Void/Wellspring zónák;
- Domain topology/occupancy;
- turn-scoped usage state;
- pending trigger/decision state;
- continuous effect state;
- modifier/keyword/duration state;
- event sequence és log;
- match result.

Későbbi bővítés:

- teljes Reaction/Priority state;
- teljes combat state;
- további pending choice/replacement state.

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
- viewer-safe events;
- diagnostics;
- opcionális transition summary;
- opcionális pending decision.

Visibility invariáns:

- a public `ActionResponse.Events` viewerje a requestet beküldő játékos;
- a transition közbeni `ActivePlayerId`-váltás nem változtathatja át a response viewerjét;
- a public response viewer-specifikusan projektált;
- az internal authoritative event store full-fidelity marad;
- az ugyanazon viewerre kért későbbi event projection szemantikailag konzisztens a direct response-zal.

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

Aktív production API:

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
- Void instance ID-k;
- Wellspring instance ID-k;
- resource summary;
- player-scoped usage state.

Aktív vagy tervezett zónák:

- `deck`;
- `hand`;
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

- deck/hand/void: nincs active/exhausted gameplay activity;
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
- Void: public, szabály szerint;
- Domain: public;
- saját Wellspring identity: owner-visible;
- ellenfél Wellspring identity: redacted;
- Wellspring count/activity: public;
- face-down Jel: viewer szerint szűrt;
- debug: külön mód.

Player-facing output nem tartalmaz szükségtelen internal instance ID-t vagy debug payloadot.

A `discard` művelet-, költség-, ok- és eventjelentés; nem önálló canonical zóna. Normál eldobáskor a tényleges célzóna `void`, de replacement szabály ettől eltérő célzónát is meghatározhat.

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

### Reaction / Priority v1 accepted specialization

Az első production Reaction slice külön aktív contractja:

`REACTION_PRIORITY_CONTRACT.md` v1.0 – `ACCEPTED_FOR_IMPLEMENTATION`.

Megőrzi a jelen top-level public contractot, és erre specializál:

- `react`;
- `pass_priority`;
- engine-issued `reaction_option_id`;
- typed `response_policy_id`;
- MatchState-owned `ReactionWindow`;
- canonical ability resolution stack;
- viewer-safe `pending_decision_summary`;
- existing `expected_state_version` stale guard;
- RC1 single-responder closure;
- RC2 queued trigger + post-resolution checkpoint.

A részletes first-slice non-goal és acceptance szabályokat a specializált contract tartalmazza.

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
- azonnal növeli a Magnitúdót és az elérhető Aurát;
- nem nyit automatikusan reaction windowt.

Production usage state:

- az engine turn-scoped/turn-number alapú guarddal tartja nyilván, hogy a normál Beáramlás megtörtént-e;
- külön `skipped` gameplay-state nem szükséges;
- a Beáramlás kihagyása a canonical phase progression része.

Legal action:

- `normal_inflow`, ha az adott körben még legális;
- `advance_phase` az opcionális Beáramlás kihagyására vagy a fázisból továbblépésre.

Accepted `normal_inflow` transition:

- atomikus;
- hand → Wellspring;
- face-down + active;
- usage guard frissül;
- resource summary frissül;
- egyszeri state-version növelés;
- viewer-safe typed eventek;
- a phase `infusion` marad mindaddig, amíg külön `advance_phase` nem történik.

Az Infusion → Manifestation váltás kizárólag canonical phase transitionnel történik.


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

Aktív production event foundation többek között:

- phase és turn transition;
- zone move;
- card ready/activity state;
- támogatott payment transition;
- támogatott card-play transition;
- canonical ability/effect resolution.

Későbbi contract-bővítés:

- Reaction/Priority;
- combat;
- Pecsét-feltörés/restore;
- victory/defeat;
- további replacement/prevention és nem támogatott ability-resolution esetek.

A pontos event-type lista és payload mindig az aktuális `CONTRACT_STATUS.md` és production contract szerint értelmezendő.

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

**Megvalósítási státusz:** `COMPLETE_AND_ACCEPTED`
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

A fenti lista a C.5B lezáráskori történeti scope-határt rögzíti. Nem a jelenlegi production állapotot írja le; a későbbi foundationt a 24.2 fejezet rögzíti.

### 24.1 Explicit phase foundation v1

Az aktív production C# turn-flow authoritative fázisállapota:

- `awakening`;
- `infusion`;
- `manifestation`;
- `incursion`;
- `distribution`.

A normál sorrend kötött, és kizárólag célfázis nélküli `advance_phase` actionnel halad. A
normál public action space nem hirdet `draw_card` vagy `end_turn` actiont. A Beáramlásban
`normal_inflow`, a Manifesztációban az egyébként jogszerű `play_card` érhető el; a többi
foundation fázisban a jelenlegi normál action az `advance_phase`.

Az Ébredés entry egyszeri authoritative transition: az aktív játékos Domínium- és
Ősforrás-lapjainak Visszaállítása után a meglévő canonical draw transitionnel két lapot
húz. A `starting_player_id` explicit match-state authority; a kezdő játékos legelső
Ébredése nulla húzásos kivétel. A Refresh Penalty hiányában a nem teljesíthető kötelező
húzás `CANONICAL_DRAW_REFRESH_PENALTY_UNSUPPORTED` hibával, teljesen atomikusan áll meg.

Az `incursion -> distribution` boundary végzi az end-of-turn modifier/keyword expiry és
a túlélő Entitások sebzésének eltávolítását. A játékosváltás és az új Ébredés automatikus
entry-je csak a `distribution -> awakening` transitionben történik.

Az unresolved mandatory trigger továbbra is gate-eli a normál phase actionöket. Combat,
reaction/priority és Refresh Penalty végrehajtás nem része ennek a foundationnek.

A public `ActionResponse.Events` viewerje a requestet beküldő játékos akkor is, ha a
transition közben az aktív játékos megváltozik. A response ugyanazt a viewer-specifikus
eventprojekciót használja, mint a `GetEvents(viewer)`, miközben az internal authoritative
event store teljes identitású eseményei változatlanul megmaradnak.

Post-audit bizonyítás: a Godot 4.7.1 .NET pozitív production bridge headless smoke canonical
`advance_phase` flow-val, öt state transitionnel és hét sorrendhelyes eventtel PASS; a
negatív smoke két kontrollált create- és négy kontrollált action-rejectionnel PASS.

---

### 24.2 C.5B utáni production gameplay és ability contract foundation

A C.5B történeti minimum után a production C# contract-réteg kibővült.

Aktív foundation többek között:

- Wellspring state és viewer-safe projection;
- `normal_inflow`;
- Magnitúdó-preflight;
- Aura-payment preflight;
- activity mutation;
- Domain topology/occupancy és placement;
- `play_card`;
- canonical zone transition és Void;
- canonical package/card/runtime binding;
- canonical ability catalog;
- ability-template compiler;
- effect condition evaluator;
- target filter és target resolver;
- trigger resolver foundation;
- effect executor;
- template/collection/zone effect runtime;
- continuous effects;
- modifier/keyword/duration state;
- damage/vitals/lethal lifecycle;
- canonical draw/reference runtime;
- Explicit Phase Foundation v1.

Ez `foundation` státusz:

- nem jelent teljes kártyacoverage-et;
- nem jelent teljes keyword supportot;
- nem jelent Reaction/Priority implementációt;
- nem jelent combat implementációt;
- nem jelenti a Refresh Penalty vagy teljes victory/defeat lifecycle elkészültét.

Aktuális implementation-bázis:

`2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

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
