# AETERNA Game Engine – Contract Specification

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.0
**Dátum:** 2026-09-05
**Státusz:** aktív, technológiafüggetlen contract-specifikáció
**Aktuális megvalósítási státusz:** `CONTRACT_STATUS.md`
**Production authority:** C#/.NET
**Aktuális repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9` – `engine: add aeternal outcome and terminal match result`

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
- `../../project/status/checkpoints/ENGINE_CHECKPOINT.md`

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

Current productionben többek között:

- match ID;
- seed;
- state version;
- turn number;
- canonical phase;
- `StartingPlayerId`;
- active player;
- priority player;
- player state-ek;
- card instance registry;
- deck/hand/Void/Wellspring zónák;
- Domain topology/occupancy;
- turn-scoped usage state;
- continuous effect state;
- modifier/keyword/duration state;
- event sequence és log;
- `ReactionWindow`;
- `ResolutionStack`;
- `QueuedTriggerBatches`;
- `MatchSetupState`;
- `PendingCombatState`;
- `PendingSurgeWindowState`;
- `SealSlots`;
- terminal `MatchResult`.

Future/külön scope lehet:

- generic compound non-Reaction choice;
- generic prevention/replacement;
- további Expansion-specifikus pending state.

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

Minimum/current contract:

- schema version;
- snapshot ID;
- match ID;
- viewer ID;
- state version;
- turn/phase/priority summary;
- own allowed public/private data;
- opponent redacted data;
- Domain board;
- Wellspring summary;
- Seal slot summary;
- pending decision/reaction/combat/surge summary;
- enabled legal actions vagy reference;
- recent visible events vagy index;
- terminal match result.

### Visibility

- own hand: owner-visible;
- opponent hand: count/redacted;
- deck: count-only;
- Void: public, rules szerint;
- Domain: public, rules szerint;
- own Wellspring identity: owner-visible;
- opponent Wellspring identity: redacted;
- Wellspring count/activity: public;
- face-down Jel: viewer szerint szűrt;
- Seal slot identity/lane/status: public;
- standing Seal card identity: hidden mindkét player-facing viewer előtt, owner előtt is;
- Seal break reveal: public;
- Surge után hand identity: ismét viewer-private;
- Reveal history: public;
- debug: külön mód.

Player-facing output nem tartalmaz szükségtelen internal instance ID-t vagy debug payloadot.

A `discard` művelet-, költség-, ok- és eventjelentés; nem önálló canonical zóna.
Normál eldobáskor a tényleges célzóna `void`, de replacement szabály ettől eltérhet.

### Fair AI

Ugyanazt a viewer-safe snapshotot, engine-issued enabled legal action listát és visible eventet kapja,
mint az adott emberi játékos. Az AI nem implementálhat külön rules legality engine-t.

## 11. Pending decision és Reaction/Combat specializációk

A complex choice authoritative state.

Lehetséges window family-k többek között:

- main;
- reaction;
- targeting;
- choice;
- payment;
- combat;
- surge;
- system.

Általános pending minimum:

- has pending;
- window type;
- priority/current decision player;
- expected action family;
- can pass/decline, ha releváns;
- state version;
- allowed choices/action IDs;
- optional safe prompt key/params.

A frontend nem tárolhat egyedüli igaz pending állapotot.

### Reaction / Priority v1

Specializált contract:

`REACTION_PRIORITY_CONTRACT.md`

Current státusz:

`COMPLETE_AND_ACCEPTED`

Current production alap:

- `react`;
- `pass_priority`;
- engine-issued `reaction_option_id`;
- typed `response_policy_id`;
- MatchState-owned `ReactionWindow`;
- canonical `ResolutionStack`;
- viewer-safe pending projection;
- existing `expected_state_version` stale guard;
- RC1 single-responder closure;
- RC2 queued trigger + post-resolution checkpoint/FIFO;
- LIFO;
- final revalidation.

### Combat pending

Current `PendingCombatState` a committed attack/defense lifecycle authoritative state-je.

Minimum fogalmi elemek:

- attacker long-term object reference;
- original target;
- committed defender, ha van;
- declaration/commit state;
- reaction-window state;
- participant continuity identity;
- contact/outcome revalidation context.

Long-term object identity:

```text
GameObjectRef {
  ObjectId,
  ObjectKindId,
  IncarnationSequence
}
```

Leave/re-enter, row/lane move vagy új incarnation nem kapcsolódhat vissza automatikusan a régi participant reference-hez.

### Surge pending

Current `PendingSurgeWindowState` a Seal break utáni Surge opportunity authoritative state-je.

Exact public action:

`resolve_surge_opportunity`

Current v1 choices:

- `apply`;
- `decline`.

A surged card ekkor már a tulajdonos kezében van.

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

Aktív production event family többek között:

- phase/turn transition;
- zone move;
- card ready/activity;
- payment;
- card play;
- ability/effect resolution;
- Reaction/Priority;
- Combat declaration/commit/resolution;
- `combat_resolved`;
- `seal_break_intent`;
- `seal_broken`;
- `seal_revealed`;
- `seal_surged`;
- `aeternal_hit`;
- `match_ended`.

Future/külön scope:

- special Seal restore/ward effect eventek;
- generic prevention/replacement;
- unsupported Expansion/ability event family-k.

A pontos event-type lista és payload mindig az aktuális `CONTRACT_STATUS.md`
és production implementation szerint értelmezendő.

## 17. Aeternal és Pecsét contract

### Seal slot

Canonical minimum:

```text
SealSlot {
  SealSlotId,
  OwnerPlayerId,
  LaneIndex,
  Status standing|broken,
  CardInstanceId?
}
```

Current invariánsok:

- playerenként pontosan 6 stabil Seal slot;
- lane 1–6;
- slot identity/lane/status public;
- standing Seal card identity hidden mindkét player-facing viewer előtt, owner előtt is;
- Sealnek nincs HP;
- standing → broken transition break pipeline-on keresztül;
- breakkor public reveal;
- Surge után a lap owner handba kerül;
- hand identity ezután ismét owner-only;
- reveal event/history public marad.

Break pipeline:

```text
successful unprevented Seal hit
→ seal_break_intent
→ break commit
→ seal_broken
→ seal_revealed
→ Surge to owner hand
→ seal_surged
→ Surge opportunity, ha eligible
→ close
```

### Gondviselés / Surge opportunity v1

Ha a surged card Magnitude-ja nagyobb a current player Magnitude-jánál,
a tulajdonos dönthet:

- keep in hand; vagy
- face-down Wellspringbe helyezés.

Ez nem normál Beáramlás.

### Aeternal

- Aeternal = player;
- nincs HP;
- nem damage/heal target;
- csak 0 standing Seal mellett targetelhető;
- successful physical Aeternal hit immediate loss;
- zero-Seal feltétel outcome előtt újra validálandó;
- restored Seal megakadályozhatja a hit outcome-ot;
- Oltalom commit után nem retargetel/cancel;
- terminal `MatchResult` authoritative.

Current events:

- `aeternal_hit`;
- `combat_resolved`;
- `match_ended`.

Future/külön scope:

- special Seal restore/ward ability payload;
- generic prevention/replacement.

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

Az unresolved mandatory trigger továbbra is gate-eli a normál phase actionöket. A fenti Explicit Phase Foundation lezárásakor Combat, reaction/priority és Refresh Penalty még nem volt része ennek a foundationnek; a későbbi Reaction és Combat/Pecsét réteget a 24.3–24.4 fejezet rögzíti.

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

Ez a 24.2 fejezet a korábbi gameplay/ability foundation történeti scope-ját rögzíti. Nem jelent teljes kártyacoverage-et vagy teljes keyword supportot. A Reaction/Priority és Combat/Pecsét későbbi current contractját a 24.3–24.4 fejezet tartalmazza.

Történeti implementation-bázis:

`2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

### 24.3 Reaction / Priority Foundation v1

Lezáró commit:

`f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`

Státusz:

`COMPLETE_AND_ACCEPTED`

Current contract:

- authoritative `ReactionWindow`;
- `ResolutionStack`;
- `QueuedTriggerBatches`;
- `react`;
- `pass_priority`;
- engine-issued reaction option;
- typed response policy;
- RC1;
- RC2;
- LIFO;
- viewer-safe pending projection;
- final revalidation.

### 24.4 Combat + Pecsét Foundation C0–C6

Rules migration:

`61ad2605dd1aa3d7ea95444f0bb66cebf819014e`

Production commits:

- C0 `ca55bc3714de2692753fccc18a8f11d9dac1beea`;
- C1+C2 `558d4453a1604c0ebe76065df08a207192c21c8b`;
- C3 `d236f0e3c36994f65e7d00d25972660baac2a842`;
- C4 `68b07dd6906fc8c37245325a855322d48f5f2635`;
- C5 `d30f8a4c42383a0200e416acb7148facc3bbbc11`;
- C6 `0862e1002dbef81ee203852714d377592272a0e9`.

Státusz:

`COMBAT_AND_SEAL_FOUNDATION_C0_C6 = COMPLETE_AND_ACCEPTED`

Current contract core:

- canonical setup + Jóslat;
- `MatchSetupState`;
- six-Seal model/privacy;
- `attack` / AttackCommit;
- intervention / DefenseCommit;
- two Combat ReactionWindows;
- `PendingCombatState`;
- participant continuity;
- contact revalidation;
- Entity Combat simultaneous damage;
- SealBreak/reveal/Surge;
- `PendingSurgeWindowState`;
- Gondviselés;
- Aeternal terminal outcome;
- terminal `MatchResult`.

Combat lifecycle:

```text
DECLARATION
→ DECLARATION LEGALITY
→ COMMIT
→ TIMING ANCHOR
→ TRIGGERS/REACTIONS
→ PARTICIPANT CONTINUITY
→ COMBAT CONTACT LEGALITY
→ RESOLUTION CONDITIONS
→ COMBAT OUTCOME
→ AFTERMATH
```

Current implementation-bázis:

`0862e1002dbef81ee203852714d377592272a0e9`

Final acceptance:

- Debug/Release C#: `301/301 PASS`;
- targeted C6: `8/8 PASS`;
- determinism/reference: `100/100 PASS`;
- canonical byte count: `210676`;
- canonical SHA:
  `97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`;
- Python isolated `465/465 PASS` + 5 skip;
- exporter `23/23 PASS`;
- Godot positive/negative smoke PASS;
- unresolved P0/P1 `0/0`.

### 24.5 Current next contract gate

Nincs előre kijelölt általános future engine-feature contract.

Current gate:

`VS1_READINESS_REQUIRED`

A két canonical VS1 deck card/mechanic auditja dönti el, mely hiányból lesz következő finite contract:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

Generic prevention/replacement, Refresh Penalty, Hasítás, full Burst/Jel vagy más future mechanika
csak akkor kötelező VS1 előtt, ha a readiness audit tényleges blockerként azonosítja.

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

A migration map current konszolidációs triggerfeltételei a Reaction és Combat/Pecsét foundation
lezárásával teljesültek. Ezért a map `ARCHIVE_CANDIDATE_AFTER_MIGRATION_CLOSE`, de csak
cross-reference audit után mozgatható Archive-ba.

Nyitott/részleges döntések:

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

Current OQ aggregate:

`52 answered / 15 partly_answered / 7 deferred / 0 open`.

A korábbi 1.4-es, Python-reference-központú specifikáció a Git-történetben megmarad.
A v2.0 a lezárt C# authority mellett a Reaction + Combat/Pecsét C0–C6 current contract meaninget is rögzíti.
