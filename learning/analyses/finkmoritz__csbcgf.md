# AETERNA – finkmoritz/csbcgf ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.2
- **Dátum:** 2026-07-24
- **Státusz:** előzetes, repository-forrásokra és az AETERNA aktív architektúrájára épülő elemzés
- **Fő elemzési fájl:** `learning/analyses/finkmoritz__csbcgf.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Vizsgált repository:** `finkmoritz/csbcgf`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `36c4c80ca22a105fef4024c4f15a525f3cdb7e2d`
- **Commit üzenete:** `Move IsCastable and IsSummonable methods to demo`
- **Vizsgált commit dátuma:** 2023-02-14
- **AETERNA összehasonlítási bázis:** `commander150/Aeterna_Projekt` – `main`, vizsgált HEAD: `309cb01bd3f0d0b9877923acc49d7be20fd476c3`
- **AETERNA production engine bázis:** a `5ee20cf199da53818e576726ed378be384d65df6` commitig elfogadott C# foundation
- **Vizsgálati korlát:** helyi build, NUnit-futtatás, serialization fuzz és teljes call graph ebben a körben nem történt
- **Besorolás:** általános C# battle-card-game framework action-, reaction-, component-, stat- és serialization-rendszerrel
- **Összehasonlítási szabály:** a projekt kizárólag az AETERNA aktuális engine-, contract-, runtime-package- és Godot-architektúrájához van mérve

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Repository | `finkmoritz/csbcgf` |
| Stabil upstream URL | https://github.com/finkmoritz/csbcgf |
| Default branch | `master` |
| Vizsgált commit | `36c4c80ca22a105fef4024c4f15a525f3cdb7e2d` |
| Repository állapot | nyilvános, nem archivált |
| Utolsó vizsgált commit dátuma | 2023-02-14 |
| Framework target | .NET 7 |
| Nyelv | C# |
| Fő dependency | Newtonsoft.Json 13.0.2 |
| Demo | Hearthstone-jellegű console/implementation projekt |
| Teszt | NUnit + coverlet |
| CI | GitHub Actions, push eseményre |
| Licenc | MIT |
| AETERNA-prioritás | P0 – action/reaction pipeline; P1 – component és serialization tanulságok |

A repository saját leírása szerint általános battle card game framework, amely központi
`Game` objektumot, event-driven game loopot, örökölhető action-, reaction-, card-,
component-, stat- és collection-osztályokat biztosít.

# 2. Vezetői összefoglaló

A CSBCGF legfontosabb AETERNA-releváns gondolata:

> A state mutation elvileg csak `IAction` objektumokon és a központi `Game.Execute`
> kapun keresztül történhet.

Ez közel áll az AETERNA kötelező elvéhez:

```text
ActionRequest
→ EngineSession.SubmitAction
→ teljes validáció
→ authoritative transition
→ ActionResponse + EngineEvent + projection
```

A CSBCGF ezen belül további hasznos mintákat ad:

- execution előtti `IsExecutable` ellenőrzés;
- actionök szekvenciális és „simultaneous” csoportosítása;
- before/after reactionök;
- eventnek nevezett marker actionök;
- dinamikusan hozzáadható card componentek;
- aggregált statértékek;
- targetful és targetless műveletek;
- teljes objektumgráf JSON-serialization;
- demo- és CI-teszt.

A legfontosabb eltérés az AETERNA-tól:

> A CSBCGF nem hoz létre valódi authority-határt.

Bár a dokumentáció szerint a mutation csak actionön keresztül történjen, a publikus API
továbbra is közvetlenül módosítható objektumokat ad ki:

- `Game.State` az aktuális state objektum;
- `IGameState` maga tartalmaz `AddPlayer` és `RemovePlayer` mutation metódusokat;
- `Player` publikus card collectionöket ad;
- `CardCollection.Add`, `Remove`, `Shuffle`, `Owner` és `MaxSize` közvetlenül elérhető;
- a statok publikus settere közvetlenül írható;
- a kártyák, reactionök és componentek közvetlen objektumreferenciák.

Ez ellentétes az AETERNA aktív contractjával, ahol:

- az `EngineSession` birtokolja a MatchState-et;
- a caller nem kap módosítható state-referenciát;
- minden mutation `SubmitAction` vagy kontrollált belső transition;
- snapshot, legal action és event új projection objektum;
- hidden state nem adható ki.

## Rövid döntés

- **Mélyelemzés folytatása:** igen, elsősorban action/reaction szemantika miatt
- **Közvetlen framework-dependencyként használható:** nem
- **Kód közvetlen beemelése:** nem javasolt
- **Architekturális inspiráció:** igen, szelektíven
- **Legértékesebb terület:** action queue, reaction phase és component-alapú módosítók
- **Legnagyobb kockázat:** a központi kapu megkerülhető és a reakció utáni végrehajtás nincs újravalidálva
- **AETERNA-ban alkalmazandó irány:** a jó szemantikai ötletek typed request/transition/event contractba fordítása

# 3. Előzetes értékelés az AETERNA szempontjából

| Szempont | Pontszám | AETERNA-viszony |
|---|:---:|---|
| Pure C# rules framework | 4/5 | Godot-független, de nem valódi class library boundary |
| Központi mutation-kapu | 3/5 | elvként erős, API-szinten megkerülhető |
| Action preflight | 3/5 | `IsExecutable` létezik, de reaction után nincs kötelező újraellenőrzés |
| Reaction-rendszer | 4/5 | before/after és dinamikus reactionök; ordering és recursion guard hiányzik |
| Simultaneous resolution | 3/5 | hasznos szemantikai irány, nem atomikus transition |
| Card component rendszer | 4/5 | dinamikus stats/reactions; instance/definition összemosás |
| Card instance modell | 1/5 | nincs stabil instance ID, zone registry vagy visibility |
| Contract/API érettség | 1/5 | nincs request/response, schema, state version vagy diagnostic |
| Event log/replay | 1/5 | event marker action van, de nincs sequence-elt tartós event log |
| Determinizmus | 1/5 | `new Random()`-alapú shuffle, seed contract nélkül |
| Hidden information | 0/5 | teljes state serializációját célozza |
| Serialization | 2/5 | object graph roundtrip működik, wire-contract és security boundary gyenge |
| Tesztelés | 3/5 | NUnit és CI van, de a vizsgált tesztkészlet szűk |
| Karbantartási aktivitás | 1/5 | utolsó commit 2023 |
| Licenc | 5/5 | MIT |
| Összesített AETERNA-prioritás | **P0/P1** | action/reaction P0; component/serialization P1 |

# 4. Projektstruktúra

A repository fő rétegei:

```text
csbcgf/
├── Program.cs
├── csbcgf.csproj
└── Library/
    ├── Action/
    ├── Card/
    ├── CardCollection/
    ├── Character/
    ├── Event/
    ├── Game/
    ├── Player/
    ├── Reaction/
    ├── Stat/
    └── Util/

demos/hearthstone/
├── implementation/
└── test/

.github/workflows/test.yml
```

## 4.1 Fontos technikai megjegyzés

A `csbcgf.csproj`:

- szabványos `Microsoft.NET.Sdk`;
- `net7.0`;
- nullable bekapcsolva;
- Newtonsoft.Json;
- ugyanakkor `OutputType` értéke `Exe`.

Az AETERNA production engine ezzel szemben tiszta `net8.0` class library, külön
Headless és Tests projekttel. Az AETERNA szempontjából a CSBCGF kódja csak akkor lenne
megfelelő szerkezeti jelölt, ha:

- class library lenne;
- nem tartalmazna demo/Program belépési pontot;
- külön contracts/runtime/tests réteg lenne;
- a publikus state mutation API-k zártak lennének.

# 5. Központi Game és state

## 5.1 `Game<T>`

A `Game<T>` tárolja:

- a teljes `state` objektumot;
- a game-over jelzőt;
- az `executeReactions` flaget.

Publikus műveletei:

- `Execute`;
- `ExecuteSimultaneously`;
- `ExecuteSequentially`.

A `State` property közvetlenül visszaadja a belső state objektumot.

## 5.2 `IGameState`

A README szerint az `IGameState` a játék olyan nézete, amely nem módosítható. A tényleges
interface azonban tartalmazza:

```text
AddPlayer(IPlayer)
RemovePlayer(IPlayer)
```

Ez dokumentáció–implementáció eltérés.

Az AETERNA-ban a hasonló player-facing vagy bridge-facing contract nem tartalmazhat
mutation metódust. A belső MatchState sem adható ki publikus callernek.

## 5.3 Közvetlen state-mutation megkerülési utak

A keretrendszer szándéka ellenére a következő utak közvetlenül elérhetők:

```text
game.State.AddPlayer(...)
game.State.RemovePlayer(...)
player.AddCardCollection(...)
player.GetCardCollection(...).Add(...)
player.GetCardCollection(...).Remove(...)
cardCollection.Shuffle()
cardCollection.MaxSize = ...
stat.Value = ...
card.AddComponent(...)
card.AddReaction(...)
```

A CSBCGF ezért inkább konvencióval védett mutable object graph, nem authority boundary.

Az AETERNA aktív EngineSession ezzel szemben:

- belső nullable `_state` mezőben birtokolja a MatchState-et;
- `GetPlayerSnapshot` új projectiont épít;
- `ListLegalActions` typed lehetőségeket ad;
- `SubmitAction` requestet validál;
- state versiont ellenőriz;
- structured rejectiont ad;
- mutation után invariantet validál.

# 6. Action-rendszer

## 6.1 `IAction`

Az action contract:

```text
IsAborted
IsExecutable(IGameState)
Execute(IGame)
```

A generikus változat typed game state-et és typed game-et használ.

Ez az AETERNA szempontjából hasznos szétválasztás:

- az action rendelkezik preconditionnel;
- az action mutationt hajt végre;
- az action önálló típusként serializálható.

## 6.2 AETERNA-megfeleltetés

A CSBCGF action nem azonos az AETERNA `ActionRequest` contracttal.

Helyes megfeleltetés:

```text
CSBCGF IAction
    ≈ belső AETERNA TransitionCommand / EngineInstruction

AETERNA ActionRequest
    = külső, nem megbízható player/UI/AI intent

AETERNA LegalAction
    = engine által előre számított lehetőség

AETERNA ActionResponse
    = accepted/rejected transitioneredmény
```

Az AETERNA-nak nem szabad a kliens által létrehozott polymorphic action objektumot
közvetlenül végrehajtania.

## 6.3 Preflight

A `Game` az actiont `IsExecutable(State)` segítségével ellenőrzi. Ez jó alapelv.

Az AETERNA már ennél szigorúbb:

- schema version;
- request ID;
- match ID;
- player ID;
- expected state version;
- action ID;
- action type;
- payload;
- enabled legal action;
- payment és target contract;
- structured diagnostic.

A CSBCGF preflight önmagában nem azonosít:

- ki kérte az actiont;
- melyik matchhez tartozik;
- milyen state versionből indult;
- milyen legal action alapján készült;
- ismételt vagy stale request-e;
- milyen viewer jogosultsággal rendelkezik.

# 7. Kritikus validációs probléma

A `Game.Execute(List<IAction>)` sorrendje:

1. `IsExecutable` ellenőrzés és GameOver marker feldolgozás;
2. újabb `IsExecutable` ellenőrzés;
3. minden reaction `ReactBefore` hívása;
4. action `Execute`;
5. minden reaction `ReactAfter` hívása.

Az action tényleges `Execute` lépése előtt már nincs újabb `IsExecutable` ellenőrzés.

Ez azért kockázatos, mert a `ReactBefore`:

- módosíthatja az állapotot;
- más actiont futtathat;
- módosíthatja magát az actiont;
- beállíthatja az `IsAborted` értéket.

Az `IsAborted` ellenőrzése megmarad, de ha a reaction állapotot változtat és nem abortálja
az actiont, a korábban valid action időközben illegálissá válhat.

Az AETERNA kötelező mintája:

```text
request validation
→ reaction/replacement előkészítés
→ execution-time final validation
→ atomic mutation
→ event commit
→ state version increment
```

Ha a reaction megváltoztatja a releváns preconditiont, az actiont újra kell validálni.

# 8. `withReactions=false` forrásszintű probléma

Az `ExecuteSimultaneously` beállítja:

```text
executeReactions = withReactions
```

A belső `Execute(List<IAction>)` viszont ezt teszi:

```text
if (!executeReactions)
    return new List<IAction>();
```

Ez azt jelenti, hogy `withReactions=false` esetén nemcsak a reactionök maradnak el,
hanem maga az actionlista sem hajtódik végre.

Ez a publikus paraméter neve és dokumentált jelentése alapján forrásszintű viselkedési
hiba vagy legalábbis súlyos szerződés-eltérés.

Helyi teszttel külön reprodukálandó.

Az AETERNA-ban a reaction policy nem lehet olyan globális mutable flag, amely a teljes
transition végrehajtását véletlenül letilthatja.

# 9. Sequential és simultaneous semantics

## 9.1 Sequential

Az `ExecuteSequentially` actionönként teljes `Execute` ciklust futtat. Ha egy action nem
hajtódik végre, a sorozat megáll.

Pozitívum:

- explicit sorrend;
- egy lépés sikertelensége blokkolhatja a következőket.

Korlát:

- a korábbi actionök mutationje már megtörtént;
- nincs rollback;
- nincs egyetlen transaction result;
- nincs state version a részlépésekhez;
- minden action külön reaction-láncot nyit.

## 9.2 Simultaneous

A „simultaneous” actionök:

- együtt kerülnek validációra;
- before reactionök lefutnak;
- utána sorban végrehajtódnak;
- csak ezután jönnek az after reactionök.

Ez hasznos szemantikai modell például kölcsönös sebzéshez.

Azonban nem valódi atomikus szimultaneitás:

- a mutationök egymás után történnek;
- egy action exceptionje után korábbi mutation megmaradhat;
- nincs intermediate state izoláció;
- nincs transition builder;
- nincs rollback;
- action ordering továbbra is list order;
- event sequence nincs explicit.

Az AETERNA számára a hasznos tanulság nem a kód, hanem a fogalom:

```text
resolution batch
→ minden effect preflightja
→ közös state-delta felépítése
→ invariant check
→ egyetlen commit
→ ordered typed events
```

# 10. Reaction-rendszer

## 10.1 Reaction contract

A reaction két fázist kap:

- `ReactBefore`;
- `ReactAfter`.

A generikus reaction:

- state típust;
- game típust;
- action típust paraméterez.

A reaction a teljes game és action objektumot megkapja.

## 10.2 Reaction discovery

A GameState `AllReactions` sorrendje:

1. game-state reactionök;
2. playerenként player reactionök;
3. player card collectionjeiben lévő kártyák;
4. kártya reactionök;
5. card component reactionök.

Ez implicit ordering, amely a listák és dictionaryk aktuális iterációs sorrendjétől függ.

Nincs:

- reaction ID;
- priority;
- timestamp;
- source sequence;
- layer;
- mandatory/optional státusz;
- owner/controller tie-break;
- active-player/non-active-player order;
- stable ordering contract;
- loop/depth limit.

Az AETERNA reaction rendszerének ezeket explicit contractként kell meghatároznia.

## 10.3 Rekurzív execution

Egy reaction közvetlenül meghívhatja:

```text
game.Execute(new Action(...))
```

Például életpont-módosítás után a death reaction `DieAction` végrehajtását indítja.

Ez egyszerű, de kockázatos:

- mély rekurzió;
- végtelen reaction loop;
- nem látható parent/correlation;
- nincs depth budget;
- nincs action stack projection;
- nincs pending decision;
- nincs explicit priority window.

Az AETERNA-ban a reactionből származó action ne közvetlen rekurzív publikus call legyen,
hanem engine-owned resolution queue:

```text
trigger detected
→ candidate reactions
→ deterministic ordering
→ mandatory resolution / pending player choice
→ queued internal instruction
→ parent/correlation event
```

# 11. Event-rendszer

A CSBCGF-ben az `Event` egy olyan `IAction`, amely nem módosít state-et, hanem marker és
reaction trigger.

Példák:

- start/end turn;
- start/end draw;
- start/end attack;
- start/end card play;
- game over.

Ez jó fogalom a folyamat határainak jelölésére.

Az AETERNA-ban azonban az event más contract:

- a transition strukturált történeti eredménye;
- event ID;
- sequence;
- match ID;
- state version;
- actor/cause;
- payload;
- visibility;
- correlation/parent;
- viewer-specifikus projection.

A CSBCGF event actiontípus és az AETERNA EngineEvent ezért nem azonos.

Javasolt AETERNA-megfeleltetés:

```text
CSBCGF marker Event
    → belső TriggerSignal vagy ResolutionMarker

AETERNA EngineEvent
    → mutation után commitált, typed, sequence-elt történeti output
```

# 12. Card-, component- és modifier-rendszer

## 12.1 Card

A `Card`:

- `ReactiveCompound`;
- `IStatContainer`;
- `IReactive`;
- `ICompound`;
- `IOwnable`.

Tart:

- owner object referenciát;
- statokat;
- reactionöket;
- componenteket.

Nincs:

- card definition ID;
- card instance ID;
- controller;
- zone;
- visibility;
- creation sequence;
- zone sequence;
- activity state;
- runtime metadata;
- immutable printed values.

## 12.2 Component

A card component dinamikusan hozzáadható és eltávolítható. A komponensek:

- statértéket adhatnak;
- reactiont adhatnak;
- targetful/targetless actionöket adhatnak;
- ParentCard referenciát kapnak.

Ez jó minta az AETERNA későbbi:

- modifier;
- granted ability;
- equipment/enchantment;
- temporary effect;
- aura-derived stat;
- trigger registration

rendszeréhez.

## 12.3 AETERNA-korlát

Az AETERNA nem tárolhat minden runtime módosítást közvetlenül mutable component objectként.

Szükséges:

```text
ModifierInstance
- modifier_id
- source_instance_id
- target_reference
- layer
- timestamp/sequence
- duration
- parameters
- visibility
```

A card definition, card instance, modifier és ability source külön maradjon.

## 12.4 Stat-aggregáció

A `ReactiveCompound.GetValue`:

```text
base stat value
+ minden component azonos kulcsú értéke
```

Ez egyszerű és jól érthető additive modifier minta.

Az AETERNA számára azonban szükséges lehet:

- set/base layer;
- additive layer;
- multiplicative layer;
- min/max clamp;
- replacement;
- conditional modifier;
- source ordering;
- printed vs current value;
- viewer-safe projection.

A CSBCGF stat-aggregáció jó minimális proof, de nem elég teljes szabályrétegnek.

# 13. Stat-rendszer

A `Stat` tart:

- current value;
- base value;
- min;
- max.

A settere clampeli az értéket.

Pozitívum:

- központi min/max;
- base/current elválasztás;
- serializálható állapot;
- componentből aggregálható.

AETERNA-megfontolások:

- Magnitude és Aura nem általános kulcs-string statként kezelendő automatikusan;
- printed és runtime értékek contractja explicit;
- resource payment és stat mutation külön transition;
- statváltozás typed eventet ad;
- a publikus caller nem kaphat settert;
- overflow policy explicit legyen.

# 14. Player és zónák

A Player card collection dictionaryt tart, amelyet string kulcsok azonosítanak.

A demo tipikus collectionjei:

- deck;
- hand;
- board;
- graveyard.

Ez a zónák általánosíthatóságát mutatja.

AETERNA-eltérések:

- AETERNA zónalistái instance ID-kat tartanak;
- központi card instance registry van;
- registry és zóna kétirányú invariáns;
- Domain topology és occupancy külön contract;
- Wellspring nem egyszerű board collection;
- visibility viewer szerint változik;
- ellenfél kéz identityje nem adható ki;
- zone move typed eventet és zone sequence-et frissít.

A CSBCGF `CardCollection` közvetlenül kártyaobjektumokat tart, ezért:

- nincs stabil external reference;
- serialization object graphra támaszkodik;
- ugyanaz a card object több listában elvileg megjelenhet;
- nincs központi registry invariáns;
- a `Remove` akkor is nullázza az Owner-t, ha a listában nem volt benne a kártya;
- a `MaxSize` futás közben szabadon módosítható.

# 15. Shuffle és determinizmus

A `CardCollection.Shuffle`:

```text
cardsCopy.OrderBy(x => new Random().Next())
```

Minden kulcsválasztásnál új `Random` példány jöhet létre.

Kockázatok:

- nincs seed;
- nincs engine-owned RNG;
- nincs random decision event;
- nincs reprodukálható shuffle;
- időalapú seed-korreláció;
- az `OrderBy(random key)` nem Fisher–Yates;
- nincs replay;
- nincs state hash.

Az AETERNA-ban:

```text
IRandomSource
→ match seed
→ deterministic draw/shuffle
→ random event metadata
→ replay-verifikáció
```

kötelező.

# 16. Serialization

## 16.1 Cél

A README szerint a teljes game state serializálható, hogy szerver és kliens között
küldhető legyen.

A JsonSerializer beállításai:

- `TypeNameHandling.Auto`;
- non-public default constructor;
- object reference preservation;
- automatic object creation.

Ez lehetővé teszi:

- polymorphic interface objektumok;
- reaction/action concrete type-ok;
- cyclic/shared object reference-ek;
- teljes game roundtrip.

## 16.2 Teszt

A demo teszt:

1. JSON-ná alakítja a game objektumot;
2. visszatölti;
3. újraserializálja;
4. byte-szintű stringegyezést vár;
5. player- és card countot ellenőriz.

Ez jó regressziós minimum az object graph megőrzésére.

## 16.3 AETERNA szempontjából miért nem megfelelő wire-contract?

Az AETERNA nem küldhet teljes MatchState object graphot kliensnek.

Hiányzik:

- schema version;
- contract DTO;
- viewer filtering;
- hidden-information redaction;
- state version;
- stable field naming policy;
- migration;
- unknown-field policy;
- diagnostic contract;
- content hash;
- card instance reference contract;
- security/trust boundary;
- server-authoritative request model.

A CLR type-neveket használó polymorphic JSON erősen összeköti a mentést vagy hálózati
adatot a konkrét C# osztályhierarchiával.

AETERNA helyes iránya:

```text
internal MatchState
≠ serialized player snapshot
≠ action request
≠ action response
≠ event
≠ debug snapshot
≠ save/replay format
```

# 17. Hidden information és multiplayer

A CSBCGF célja szerint a teljes state szerver és kliens között küldhető.

Ez az AETERNA számára nem elfogadható, mert a MatchState tartalmazhat:

- mindkét kéz kártyáit;
- deck sorrendet;
- hidden Wellspring identityt;
- face-down objektumokat;
- debug metadata-t;
- belső reaction és component állapotot.

Az AETERNA aktív contractja viewer-specifikus projectiont követel:

- saját kéz identity;
- ellenfél kéz csak count/redacted;
- deck count-only;
- Domain public;
- Wellspring identity viewer szerint;
- event visibility;
- debug külön internal contract.

# 18. Legal action és targetelés

A CSBCGF kártyák és demo-osztályok saját metódusokkal számítják:

- `IsCastable`;
- `IsSummonable`;
- `GetPotentialTargets`.

Ez jó domain helper minta.

Az AETERNA-ban azonban a legalitás nem maradhat szétszórt card subclass metódusokban.

Szükséges:

```text
EngineSession.ListLegalActions(viewer/player)
→ stabil action ID
→ action type
→ source
→ target/choice/payment context
→ payload schema
→ enabled/disabled
→ disabled reason debug módban
```

A targetek nem raw object referenciák, hanem stabil object/card/position reference-ek.

# 19. Demo-kártyák és öröklés

A demo sok konkrét kártyát C# subclassként valósít meg.

Előny:

- C# type safety;
- összetett egyedi viselkedés;
- közvetlen tesztelhetőség;
- reaction/action kompozíció.

AETERNA-korlát:

- az AETERNA több száz vagy több ezer kártyájához nem kívánatos kártyánkénti subclass;
- a hivatalos adatbázis és runtime package a statikus content source;
- ability registry és support státusz szükséges;
- a rules text nem szabad C# subclassba rejtve maradjon;
- custom engine code csak auditált, ritka ability module lehet.

# 20. Tesztek és CI

## 20.1 Tesztprojekt

A demo tesztprojekt:

- .NET 7;
- NUnit;
- NUnit adapter;
- analyzers;
- coverlet;
- hivatkozik a frameworkre és a Hearthstone implementációra.

## 20.2 Vizsgált tesztek

A `Test.cs` három fő területet ellenőriz:

- initial conditions;
- többlépéses game flow;
- serialization roundtrip.

A game flow lefedi:

- turnváltás;
- mananövekedés;
- draw;
- summon;
- attack;
- simultaneous death;
- graveyard;
- spell damage.

## 20.3 CI

A GitHub Actions workflow:

- minden pushra fut;
- Ubuntu latest;
- .NET 7 setup;
- restore;
- build;
- test.

## 20.4 AETERNA-eltérés

Az AETERNA production engine-hez szükséges tesztterületek:

- contract schema;
- malformed input;
- stale state version;
- legal action;
- reject-no-mutation;
- invariant;
- event sequence;
- viewer redaction;
- deterministic seed;
- replay;
- runtime package validation;
- payment;
- target selection;
- reaction ordering;
- recursion/loop budget;
- serialization migration.

A CSBCGF tesztje hasznos scenario-minta, de nem elég authority- és contract-proof.

# 21. CI- és karbantartási státusz

A repository technikailag nem archivált, de a vizsgált HEAD 2023-02-14-i.

Következmények:

- .NET 7-et használ;
- dependencyk régiek lehetnek;
- a CI actionök v3-asak;
- aktuális runtime compatibility helyi builddel ellenőrzendő;
- production dependencyként nem célszerű építeni rá;
- tanulási forrásként továbbra is értékes.

A commit status API a vizsgált HEAD-hez nem adott vissza státuszokat, ezért a workflow
tényleges utolsó eredménye külön GitHub Actions audittal ellenőrzendő.

# 22. Licenc

A repository MIT licencű:

```text
Copyright (c) 2020 Moritz Fink
```

Lehetséges:

- használat;
- módosítás;
- terjesztés;
- sublicencelés;
- értékesítés;

a copyright- és engedélyszöveg megtartásával.

AETERNA-javaslat:

- közvetlen dependency ne legyen;
- kis algoritmusrész átvétele csak attributionnel;
- általános action/reaction ötletek saját implementációban;
- Hearthstone demo content és márkanevek nem AETERNA-tartalom.

# 23. Erősségek az AETERNA szempontjából

1. Godot-független C# rules framework.
2. Központi action execution elv.
3. `IsExecutable` preflight.
4. Before/after reaction fázisok.
5. Simultaneous resolution fogalma.
6. Start/end marker eventek.
7. Generikus typed action és reaction contract.
8. Dinamikus card componentek.
9. Stat-aggregáció.
10. Targetful/targetless elkülönítés.
11. Több zóna általános collectionként.
12. Serialization roundtrip.
13. NUnit scenario teszt.
14. GitHub Actions CI.
15. MIT licenc.

# 24. Gyengeségek és technikai kockázatok az AETERNA szempontjából

1. A Game.State közvetlen mutable state.
2. Az IGameState mutation metódusokat tartalmaz.
3. Közvetlen card collection mutation megkerüli a Game.Execute kaput.
4. Közvetlen stat setter megkerüli a Game.Execute kaput.
5. Nincs ActionRequest contract.
6. Nincs ActionResponse contract.
7. Nincs state version.
8. Nincs request ID vagy idempotency.
9. Nincs legal action projection.
10. Nincs structured diagnostic.
11. Nincs stable card instance ID.
12. Nincs definition/instance elválasztás.
13. Owner és controller nincs külön.
14. Nincs zone registry invariáns.
15. Nincs visibility model.
16. Nincs viewer projection.
17. Nincs typed, sequence-elt event log.
18. Event és action fogalma összemosódik.
19. Reaction ordering implicit.
20. Nincs reaction depth/loop guard.
21. Reaction után nincs kötelező újravalidálás.
22. `withReactions=false` nem hajt végre actiont.
23. Simultaneous action nem atomikus.
24. Sequential actionnél nincs rollback.
25. `executeReactions` mutable és serializált engine flag.
26. Shuffle nem seedelt és gyenge algoritmus.
27. Teljes object graph serialization.
28. CLR-type-alapú polymorphic JSON.
29. Hidden information védelem hiánya.
30. Nincs runtime package/content contract.
31. Kártyánkénti subclass skálázási kockázat.
32. Framework projekt `Exe`, nem class library.
33. .NET 7 és 2023-as utolsó commit.
34. Szűk tesztkészlet.
35. Nincs contract/replay/determinism teszt.

# 25. AETERNA számára átvehető elvek

## 25.1 Minden mutation belső transition instruction legyen

A CSBCGF `IAction` gondolata használható, de csak belső engine objektumként.

```text
External ActionRequest
→ RequestValidator
→ Internal TransitionInstruction
→ TransitionBuilder
→ Commit
```

## 25.2 Final revalidation

Minden replacement/reaction/selection után, közvetlenül commit előtt újra kell ellenőrizni
a transition preconditionjeit.

## 25.3 Reaction phase-ek

Használható fogalmak:

- before/replacement;
- after/trigger;
- mandatory;
- optional;
- player-choice;
- simultaneous batch.

De explicit ordering és queue contract kell.

## 25.4 Component-alapú granted behavior

A component ötlet megfeleltethető:

- granted ability;
- temporary modifier;
- static modifier;
- reaction source;
- card-linked effect state.

Ezek stabil instance ID-s typed state-ek legyenek.

## 25.5 Simultaneous batch

Az AETERNA combat és többcélú effectek számára hasznos:

- precompute;
- közös delta;
- invariant validation;
- atomic commit;
- event ordering.

## 25.6 Scenario és serialization teszt

A teljes game flow tesztmintája követhető, de AETERNA-specifikus contract assertionökkel.

# 26. Amit nem szabad átvenni

1. Publikus mutable MatchState.
2. `IGameState` mutation metódusokkal.
3. Kliens által küldhető polymorphic IAction objektum.
4. Raw object reference targetként.
5. Card object zónaazonosítóként.
6. Event mint no-op action player-facing esemény helyett.
7. Globálisan bejárható reactionlista explicit ordering nélkül.
8. Rekurzív `game.Execute` loop guard nélkül.
9. `new Random()` shuffle.
10. Teljes object graph kliensnek.
11. `TypeNameHandling.Auto` alapú hálózati/save contract.
12. Reaction után újravalidálás nélküli végrehajtás.
13. Nem atomikus simultaneous mutation.
14. Közvetlen CardCollection.Add/Remove authoritative API-ként.
15. Kártyánkénti kötelező subclass.

# 27. Javasolt AETERNA action/reaction modell

```text
Player/UI/AI
    │
    ▼
ActionRequest
    schema_version
    request_id
    match_id
    player_id
    expected_state_version
    action_id
    action_type
    payload
    │
    ▼
RequestValidator
    identity
    stale guard
    legal action match
    payload
    payment
    target
    │
    ▼
ResolutionPlan
    primary instruction
    replacements
    mandatory triggers
    optional trigger windows
    simultaneous groups
    parent/correlation
    │
    ▼
Final Validation
    │
    ▼
Atomic Transition Commit
    state version increment
    invariant check
    │
    ├── EngineEvents
    ├── ActionResponse
    └── viewer-specific snapshots
```

# 28. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | Belső `TransitionInstruction` interface kialakítása | Engine | P1 |
| 2 | Külső ActionRequest és belső instruction szigorú elkülönítése | Contracts/Engine | P0 |
| 3 | Final revalidation minden reaction/replacement után | Engine | P0 |
| 4 | Typed resolution queue | Engine | P0 |
| 5 | Reaction source ID és priority/order contract | Engine | P0 |
| 6 | Reaction depth, step és loop budget | Engine | P0 |
| 7 | Parent/correlation ID minden kiváltott instructionhöz | Events | P1 |
| 8 | Simultaneous transition builder | Engine | P1 |
| 9 | Atomic delta commit és rollback-free preflight | Engine | P0 |
| 10 | ModifierInstance typed model componentek helyett | State | P1 |
| 11 | Printed/base/current stat layer explicit contract | State | P1 |
| 12 | CardInstanceId minden zóna- és targethivatkozásban | State/Contracts | P0 |
| 13 | Player-facing event és internal trigger marker különválasztása | Events | P0 |
| 14 | Viewer projection minden hidden state-hez | Projection | P0 |
| 15 | Seedelt Fisher–Yates vagy engine RNG service | Engine | P0 |
| 16 | Reaction-order determinism teszt | Tests | P0 |
| 17 | Infinite reaction loop teszt | Tests | P0 |
| 18 | Simultaneous death/combat fixture | Tests | P1 |
| 19 | Reject-no-mutation fixture | Tests | P0 |
| 20 | Serialization csak explicit DTO-kkal | Contracts | P0 |
| 21 | Stable schema és migration policy | Contracts | P1 |
| 22 | CSBCGF közvetlen dependency elutasítása | Projekt | P0 |

# 29. Bizonyítékjegyzék

## 29.1 CSBCGF-források

| ID | Állítás | Forrásfájl | Sorok |
|---|---|---|---|
| C-001 | Framework célja és event-driven loop | `readme.md` | 3–11 |
| C-002 | Game tartja a teljes match state-et | `readme.md` | 32–41 |
| C-003 | Action-only mutation elv | `readme.md` | 117–129 |
| C-004 | Marker eventek | `readme.md` | 131–147 |
| C-005 | Reaction before/after modell | `readme.md` | 149–156 |
| C-006 | Sequential/simultaneous különbség | `readme.md` | 237–256 |
| C-007 | Teljes game state serialization cél | `readme.md` | 160–223 |
| C-008 | .NET 7 és Newtonsoft.Json | `csbcgf.csproj` | 3–14 |
| C-009 | Game belső state és flag | `Game.cs` | 7–27 |
| C-010 | State közvetlen kiadása | `Game.cs` | 29–39 |
| C-011 | Execute entry pointok | `Game.cs` | 42–71 |
| C-012 | withReactions=false korai return | `Game.cs` | 73–78 |
| C-013 | Reaction és action sorrend | `Game.cs` | 80–116 |
| C-014 | Execute előtti check hiánya a harmadik fázisban | `Game.cs` | 102–104, 119–133 |
| C-015 | IGame mutation-kapu dokumentációja | `IGame.cs` | 5–37 |
| C-016 | IAction IsExecutable/Execute | `IAction.cs` | 5–30 |
| C-017 | Action abort és generikus adapter | `Action.cs` | 7–60 |
| C-018 | IGameState mutation metódusokat tartalmaz | `IGameState.cs` | 5–25 |
| C-019 | GameState mutable player/reaction lista | `GameState.cs` | 8–28, 56–83 |
| C-020 | Reaction discovery | `GameState.cs` | 56–64 |
| C-021 | Player collection és reaction aggregation | `Player.cs` | 27–85 |
| C-022 | CardCollection public mutation | `CardCollection.cs` | 83–102 |
| C-023 | Nem seedelt OrderBy/new Random shuffle | `CardCollection.cs` | 104–112 |
| C-024 | Card owner és component | `Card.cs` | 7–35 |
| C-025 | Component/reaction aggregation | `ReactiveCompound.cs` | 20–69 |
| C-026 | Stat clamp | `Stat.cs` | 30–63 |
| C-027 | Polymorphic object graph serializer | `JsonSerializer.cs` | 7–25 |
| C-028 | Draw két collection actionből | `DrawCardAction.cs` | 36–48 |
| C-029 | Death reaction rekurzív game.Execute | `DieOnModifyLifeStatActionReaction.cs` | 7–19 |
| C-030 | Demo NUnit project | `test.csproj` | 3–25 |
| C-031 | Scenario és serialization teszt | `Test.cs` | 50–182 |
| C-032 | Push CI restore/build/test | `.github/workflows/test.yml` | 3–27 |
| C-033 | MIT licenc | `LICENSE` | 3–22 |
| C-034 | Vizsgált HEAD 2023-02-14 | commit `36c4c80...` | commit metadata |

## 29.2 AETERNA összehasonlítási források

| ID | Állítás | Forrásfájl | Sorok |
|---|---|---|---|
| A-001 | Egy authoritative state, UI nem szabályforrás | `ARCHITECTURE.md` | 36–52 |
| A-002 | Runtime package → C# engine → Godot | `ARCHITECTURE.md` | 56–72 |
| A-003 | Godot tiltott mutationök | `ARCHITECTURE.md` | 158–184 |
| A-004 | C# engine felelősségek | `ARCHITECTURE.md` | 217–244 |
| A-005 | SubmitAction authority-kapu | `ARCHITECTURE.md` | 246–263 |
| A-006 | Pure C# production projekt | `ARCHITECTURE.md` | 265–306 |
| A-007 | Contract-first és reject-no-mutation | `CONTRACT_SPECIFICATION.md` | 40–57 |
| A-008 | MatchState fő mezők | `CONTRACT_SPECIFICATION.md` | 121–144 |
| A-009 | LegalAction contract | `CONTRACT_SPECIFICATION.md` | 158–179 |
| A-010 | ActionRequest contract | `CONTRACT_SPECIFICATION.md` | 181–196 |
| A-011 | ActionResponse contract | `CONTRACT_SPECIFICATION.md` | 198–213 |
| A-012 | EngineEvent contract | `CONTRACT_SPECIFICATION.md` | 215–231 |
| A-013 | EngineSession határ | `CONTRACT_SPECIFICATION.md` | 251–270 |
| A-014 | Definition/instance elválasztás | `CONTRACT_SPECIFICATION.md` | 274–306 |
| A-015 | Zónák és registry invariáns | `CONTRACT_SPECIFICATION.md` | 310–334 |
| A-016 | Viewer-specific hidden projection | `CONTRACT_SPECIFICATION.md` | 387–425 |
| A-017 | Production C# publikus entry pointok | `CONTRACT_STATUS.md` | 67–107 |
| A-018 | Active authoritative MatchState | `CONTRACT_STATUS.md` | 207–233 |
| A-019 | EngineSession actual stale guard és legal action | `EngineSession.cs` | 136–199, 201–356 |
| A-020 | EngineSession viewer snapshot és debug separation | `EngineSession.cs` | 94–134, 359–422 |

# 30. Nyitott kérdések

1. Buildelhető-e a vizsgált commit aktuális SDK-val?
2. Az NUnit tesztek jelenleg PASS állapotúak-e?
3. A `withReactions=false` hibát teszt fedi-e?
4. ReactBefore state mutation után végrehajtható-e illegálissá vált action?
5. Van-e reaction loopot megakadályozó rejtett mechanizmus?
6. Milyen pontos orderinggel járja be a dictionary card collectionöket?
7. Serialization után az ordering és object identity stabil marad-e?
8. Deserializált reactionök ParentCard és owner referenciái mindig helyreállnak-e?
9. Ugyanaz a card object több collectionbe bekerülhet-e?
10. Remove nem létező card esetén miért nullázza az Ownert?
11. `new Random()` shuffle eredménye mennyire torz vagy ismétlődő?
12. Exception közben részleges simultaneous mutation marad-e?
13. GameOverEvent egy batch többi actionjét hogyan blokkolja?
14. Az `executeReactions` nested Execute hívásoknál milyen szemantikát eredményez?
15. A teljes object graph JSON fogad-e nem megbízható hálózati inputot?
16. Van-e schema migration vagy backward compatibility?
17. A framework és demo ténylegesen külön assembly boundaryként működik-e?
18. Mely action/reaction minták felelnek meg az AETERNA hivatalos trigger/reaction szabályainak?
19. Mely component minták fordíthatók AETERNA ModifierInstance contracttá?
20. Érdemes-e külön action/reaction fogalomtérképet készíteni az AETERNA későbbi gameplay phase előtt?

# 31. Következő vizsgálati lépések

## Codex nélkül elvégezhető

1. Helyi origin és commit rögzítése.
2. `dotnet restore`.
3. `dotnet build`.
4. `dotnet test`.
5. `withReactions=false` reprodukció.
6. ReactBefore invalidation teszt.
7. Infinite reaction loop teszt.
8. Simultaneous exception/partial-mutation teszt.
9. Shuffle determinism és distribution smoke.
10. Serialization roundtrip több reaction/component kombinációval.
11. Hidden-information leakage mintasnapshot.
12. Public mutation bypass lista véglegesítése.
13. Action/reaction ordering trace.
14. AETERNA reaction contract fogalmi javaslat külön dokumentumban.

## Később Codexszel gyorsítható

1. teljes call graph;
2. minden publikus mutation surface listázása;
3. action/reaction recursion graph;
4. serialization type map;
5. ordering és determinism audit;
6. automatikus NUnit boundary test generation;
7. AETERNA internal TransitionInstruction proof-of-concept;
8. CSBCGF actionök gépi megfeleltetése AETERNA contractfogalmakhoz.

# 32. Végső előzetes minősítés

- **Tanulási érték:** magas
- **Elsődleges AETERNA-tanulság:** action/reaction resolution szemantika
- **Központi authority-kapu érettsége:** közepes elv, gyenge kikényszerítés
- **Card instance és hidden-information érték:** alacsony
- **Serialization tanulság:** hasznos object-graph proof, nem használható AETERNA wire-contractként
- **Determinizmus:** nem megfelelő
- **Tesztelési alap:** létezik, bővítendő
- **Production dependencyként:** nem ajánlott
- **Saját AETERNA-implementációhoz inspirációként:** igen
- **Közvetlenül átvehető kód:** csak külön licenc- és minőségi audit után, jelenleg nem javasolt
- **Mélyelemzés folytatása:** igen, action/reaction tesztcsomaggal
- **Következő learning projekt:** a katalógus prioritása szerint a `jcbcn/card-game-engine` vagy más, közvetlenül AETERNA engine-határhoz releváns projekt

# 33. Változásnapló

## 0.1 – 2026-07-24

- elkészült a CSBCGF első repository-forrásokra épülő elemzése;
- az összehasonlítás kizárólag az AETERNA aktív architektúrájával történt;
- vizsgálat készült a Game, IAction, reaction, event, component, stat és collection rétegről;
- azonosításra került a publikus mutation-kapu megkerülhetősége;
- azonosításra került a reaction utáni final revalidation hiánya;
- azonosításra került a `withReactions=false` forrásszintű szerződés-eltérése;
- vizsgálat készült a simultaneous és sequential szemantikáról;
- feldolgozásra került a teljes object graph serialization és hidden-information kockázata;
- elkészült az AETERNA action/reaction contractjavaslat;
- létrejött a helyi build- és célzott tesztlista.

## Hivatkozási modell javítása – 2026-07-24

- a kapcsolódó katalógus hivatkozása mostantól: az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum;
- az elemzés nem tartalmaz konkrét katalógusfájlnevet vagy katalógusverziót;
- új központi katalógusverzió miatt ezt a projektdokumentumot nem kell módosítani;
- a projekt vizsgált állapotának reprodukálhatóságát továbbra is a saját branch/tag,
  commit SHA és vizsgálati dátum biztosítja;
- a korábbi verziótlan központi fájlmodell felváltásra került.
