# AETERNA – db0/godot-card-game-framework ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-25
- **Státusz:** repository-forrásokra épülő első teljes elemzés
- **Fő elemzési fájl:** `learning/analyses/db0__godot-card-game-framework.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Repository:** `db0/godot-card-game-framework`
- **Stabil upstream URL:** `https://github.com/db0/godot-card-game-framework`
- **Vizsgált branch:** `main`
- **Vizsgált commit:** `f3ca9afd9705ff895839253fad208360d2f45146`
- **Vizsgált commit dátuma:** 2025-05-20
- **Framework-verzió:** 2.2
- **Technológiai alap:** Godot 3.4.x / GDScript
- **Licenc:** GNU AGPL v3, Steamworks-kommunikációs addendummal
- **AETERNA összehasonlítási bázis:** az aktuális C# authoritative engine-, contract-, runtime-package- és Godot-bridge rendszer
- **Összehasonlítási szabály:** kizárólag az AETERNA rendszeréhez mérve
- **Vizsgálati korlát:** helyi Godot-import, GUT-futtatás, export és teljes dinamikus viselkedésvizsgálat ebben a körben nem történt
- **Elsődleges AETERNA-érték:** deklaratív kártyaképesség-leírás, költség-előellenőrzés, target/selection UX, valamint fejlett Godot-kártya- és zónapresentation
- **Elsődleges AETERNA-kockázat:** a rules execution közvetlenül Godot scene-node-okat és globális autoload állapotot módosít

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Projekt neve | Godot Card Game Framework |
| Repository | `db0/godot-card-game-framework` |
| Default branch | `main` |
| Vizsgált commit | `f3ca9afd9705ff895839253fad208360d2f45146` |
| Repository állapot | nyilvános, nem archivált |
| README-verzió | 2.2 |
| Motor | Godot 3.4.x |
| Nyelv | GDScript |
| Fő card node | `Card extends Area2D` |
| Központi autoload | `cfc` / `CFControl.gd` |
| Kártyaadatok | GDScript dictionaryk, készletfájlokra bontva |
| Képességleírás | dictionary-alapú task/trigger/filter rendszer |
| Tesztek | GUT unit és integration tesztek |
| CI | GitHub Actions, Godot 3.4.4 teszt és Godot 3.4 HTML5 export |
| Multiplayer | nem része a framework bizonyított magjának |
| Licenc | AGPL-3.0, külön Steamworks addendummal |
| AETERNA-prioritás | P0 – effect compiler és Godot presentation tanulási forrás |
| Közvetlen integráció | elutasítandó |

# 2. Vezetői összefoglaló

A framework két, AETERNA szempontjából eltérő értékű réteget tartalmaz.

## 2.1 Erős presentation-réteg

A projekt kész megoldásokat ad többek között:

- kéz- és paklielrendezésre;
- húzásra, mozgatásra és drag-and-dropra;
- célzónyílra;
- face-up/face-down állapotra;
- tokenekre és számlálókra;
- attachment-megjelenítésre;
- grid- és szabad board-elhelyezésre;
- kártyakönyvtárra;
- deck builderre;
- pile-tartalom megtekintésére;
- hover/focus nézetre;
- animációkra;
- skálázásra és ablakátméretezésre.

Ezekből az AETERNA Godot-kliens saját, C# snapshotokra és eventekre épülő view-réteget
alakíthat ki.

## 2.2 Erős, de rossz authority-határon futó képességrendszer

A ScriptingEngine összetett kártyaképességeket ír le dictionaryk segítségével:

- taskok;
- triggerfeltételek;
- targetek;
- boardseek és tutor;
- költségek;
- optional és multiple-choice ágak;
- selection;
- repeat;
- nested taskok;
- filterek;
- token- és tulajdonságmódosítások;
- kártyamozgatás;
- spawn;
- runtime intenzitásszámítás;
- korábbi eredmények továbbadása.

Ez fontos bizonyíték arra, hogy nagy képességtér kártyánkénti egyedi programosztályok
nélkül is leírható.

A megvalósítás azonban AETERNA production authorityként nem használható:

```text
dictionary task
→ ScriptingEngine
→ globális cfc/NMAP
→ Card és CardContainer scene-node
→ közvetlen node/state mutation
→ Godot signal
```

Az AETERNA helyes iránya:

```text
authoring adat
→ schema validation
→ typed AST / instruction
→ runtime package
→ EngineSession
→ teljes validáció és final revalidation
→ atomic MatchState transition
→ typed EngineEvent
→ viewer-specifikus projection
→ Godot animáció
```

## 2.3 Rövid döntés

- **Godot UI-referenciaként:** kiemelten hasznos
- **Effect DSL-referenciaként:** kiemelten hasznos
- **Költség-preflight gondolatként:** hasznos
- **Target/selection UX-ként:** hasznos
- **Production rules engine-ként:** nem használható
- **Authoritative multiplayer engine-ként:** nem használható
- **Közvetlen dependencyként:** elutasítandó
- **Közvetlen kódmásolás:** AGPL miatt és architekturális okból nem javasolt
- **Clean-room elvi újraimplementálás:** igen
- **AETERNA-következtetés:** a szemantikát kell megtartani, nem a Godot-node-alapú végrehajtást

# 3. Előzetes értékelés az AETERNA szempontjából

| Szempont | Pontszám | AETERNA-vonatkozás |
|---|:---:|---|
| Godot presentation | 5/5 | sok kész kártya-, kéz-, pile-, target- és board-minta |
| Deklaratív képességleírás | 5/5 | gazdag dictionary task/filter rendszer |
| Költség-preflight | 4/5 | valós dry-run, de nem tranzakció és nem engine authority |
| Selection/choice | 4/5 | target, popup, multiple choice és integer input |
| Trigger-rendszer | 3/5 | sok signal és filter, de nincs explicit determinisztikus ordering |
| Determinizmus | 3/5 | seedelt játék-RNG és teszt van, replay/event log nincs |
| Adatpipeline | 3/5 | definition/script setekre bontva, schema/version/ID gyenge |
| Tesztelés | 4/5 | széles GUT unit/integration készlet |
| CI | 4/5 | teszt és HTML5 export automatizált |
| Engine–UI elválasztás | 1/5 | Card node egyszerre view, state és rules actor |
| Authority | 1/5 | globális autoload és scene-tree mutation |
| Hidden information | 1/5 | face-down presentation van, viewer projection nincs |
| Multiplayer | 0/5 | nem bizonyított authoritative network modell |
| Modern Godot-illeszkedés | 1/5 | Godot 3.4/GDScript, AETERNA Godot 4/C# iránya eltér |
| Licenc-kompatibilitás | 1/5 | AGPL közvetlen integrációhoz problémás |
| Összesített prioritás | **P0** | effect- és presentation-tanulás; nem dependency |

# 4. Technológiai és repository-állapot

## 4.1 Aktuális upstream

A repository nem archivált, és a vizsgált `main` HEAD:

```text
f3ca9afd9705ff895839253fad208360d2f45146
```

A legutóbbi commit README-frissítés. A közeli korábbi commitok között szerepel
teljesítményjavítás, v2.2 kiadás és CI-fix is.

## 4.2 Godot-verzió

A CI:

- Godot 3.4.4 alatt futtatja a GUT teszteket;
- Godot 3.4 headless binárissal exportál HTML5 buildet.

A kód Godot 3 API-kat használ:

- `Reference`;
- `yield`;
- `GDScriptFunctionState`;
- külön Tween node;
- régi `export` és `setget` szintaxis;
- `config_version=4`.

AETERNA-ban ezért közvetlen script- vagy scene-átvétel nem célszerű. A mintákat Godot 4
és az AETERNA C# bridge szerkezetéhez kell újraimplementálni.

# 5. Fő projektstruktúra

A `project.godot` alapján a framework jelentős globális osztálykészletet tartalmaz:

```text
Card
CardContainer
Hand
Pile
Board
BoardPlacementGrid
BoardPlacementSlot
CardViewer
CardLibrary
DeckBuilder
TargetingArrow
Token
Counters
ScriptingEngine
ScriptTask
ScriptObject
ScriptProperties
AlterantEngine
CFControl
CFUtils
```

A fő autoload:

```text
cfc = res://src/core/CFControl.gd
```

A `cfc` egyszerre tárol:

- beállításokat;
- card definitionöket;
- card scriptdefiníciókat;
- node mapet;
- aktív dragállapotot;
- RNG-t és seedet;
- cache-eket;
- temporary modifiereket;
- scripting engine referenciát;
- signal propagatort.

Ez service locator és globális runtime state egyben.

Az AETERNA-ban a Godot autoload használható:

- UI-beállításokra;
- assetcache-re;
- bridge elérésére;
- scene-registryre;
- lokalizációra.

Nem lehet:

- authoritative MatchState;
- rules registry;
- zónaállapot;
- fizetési authority;
- trigger queue;
- RNG authority.

# 6. Card node: view, state és rules összefonódása

A framework `Card` osztálya `Area2D`, és egyetlen objektumban tartja:

- a vizuális finite state machine-t;
- a kártyatulajdonságokat;
- a képességdictionaryt;
- face-up/face-down állapotot;
- rotationt;
- attachmenteket;
- board placementet;
- targetelt és potenciális container állapotot;
- temp modifiereket;
- token view-t;
- highlightot;
- tweeneket;
- inputkezelést;
- scriptfuttatást;
- scene-hivatkozásokat.

## 6.1 Vizuális CardState

A CardState értékek például:

- `IN_HAND`;
- `FOCUSED_IN_HAND`;
- `DRAGGED`;
- `DROPPING_TO_BOARD`;
- `ON_PLAY_BOARD`;
- `IN_PILE`;
- `IN_POPUP`;
- `VIEWPORT_FOCUS`;
- `DECKBUILDER_GRID`.

Ezek presentation-állapotok. A framework azonban a `get_state_exec()` segítségével ezekből
következteti, hogy a képesség `hand`, `board` vagy `pile` ága fusson.

Ez AETERNA-ban nem elfogadható, mert a rules zone nem a vizuális FSM-ből származik.

Helyes AETERNA-minta:

```text
Engine CardInstance.zone
→ PlayerSnapshot projection
→ CardViewModel.zone
→ CardView presentation state
```

A view animation állapotából semmilyen rules state nem következhet vissza.

## 6.2 Kártyaazonosítás

A framework `canonical_name` mezőt tekinti a node authoritative nevének.

AETERNA számára ez nem elég:

- a név lokalizálható;
- több azonos kártyapéldány létezik;
- runtime módosított másolat létezhet;
- token vagy generált példány létezhet;
- ugyanaz a definition több ownernél szerepelhet.

Kötelező különválasztás:

```text
card_id              # statikus definition
card_instance_id     # meccsspecifikus példány
localized_name       # presentation
scene/view id         # csak kliens
```

# 7. Card definition és script definition

A framework a statikus adatot és a képességdictionaryt külön fájlokba tudja tenni.

## 7.1 Card definition példa

A készletdefiníció mezői:

- `Type`;
- `Tags`;
- `Requirements`;
- `Abilities`;
- `Cost`;
- `Power`;
- `_keywords`.

Ez hasznos elv, mert a megjelenési és alapstatisztikai adatok nem a Card osztályba vannak
hard-code-olva.

## 7.2 Script definition példa

Egy külön scriptfájl megadhat:

- manuális `hand` és `board` ágakat;
- signal triggert;
- targetet;
- `previous` subjectet;
- multiple-choice opciókat;
- integer inputot;
- deckből discardba mozgatást.

## 7.3 AETERNA számára átvehető elv

Az AETERNA munkaforrásból készülő runtime package-ben szintén külön kezelhető:

```text
CardDefinition
AbilityDefinition
EffectDefinition
LocalizedText
PresentationMetadata
```

## 7.4 AETERNA számára javítandó hiányok

A framework betöltése a card nevet dictionary kulcsként használja, és a setek összefűzésekor
ugyanaz a kulcs felülírhatja a korábbit.

AETERNA-nál szükséges:

- stabil `card_id`;
- stabil `ability_id`;
- package ID;
- schema version;
- content hash;
- duplicate ID hiba;
- unknown field policy;
- kötelező mezőellenőrzés;
- típusellenőrzés;
- support registry;
- stable diagnostic code;
- atomikus package load;
- localized név külön mezőben.

# 8. ScriptingEngine mint deklaratív képességrendszer

A ScriptingEngine taskonként konkrét műveleti primitiveket ad. Példák:

- rotate;
- flip;
- view;
- move card containerbe;
- move card boardra;
- token módosítás;
- counter módosítás;
- property módosítás;
- spawn;
- ask integer;
- nested task;
- más kártya scriptjének futtatása;
- selection;
- shuffle;
- wait/yield jellegű folyamatok.

A dictionaryk tulajdonképpen egy runtime effect DSL-t alkotnak.

## 8.1 Használható AETERNA-fogalom

```text
EffectInstruction
- opcode
- source
- subject selector
- amount/expression
- destination
- filters
- optionality
- selection contract
- tags
```

## 8.2 A jelenlegi megvalósítás problémája

A task neve stringként kerül meghívásra:

```text
call(script.script_name, script)
```

A subjectek raw Card/Node referenciák. A destination a globális `cfc.NMAP` dictionaryből
név alapján oldódik fel. A taskok közvetlenül:

- node-ot reparentelnek;
- Card property dictionaryt írnak;
- token node-ot módosítanak;
- Board countert írnak;
- scene-t példányosítanak;
- UI-dialogot nyitnak;
- yielddel animációra vagy játékosinputra várnak.

Ez nem typed, nem platformfüggetlen és nem authoritative engine.

# 9. AETERNA effect compiler javaslat

A framework szemantikájából az alábbi pipeline használható:

```text
AETERNA authoring source
        │
        ▼
Schema validator
        │
        ▼
Effect parser/compiler
        │
        ├── subject selector
        ├── predicate/filter
        ├── cost
        ├── choice/selection
        ├── arithmetic expression
        ├── operation
        └── trigger/reaction metadata
        │
        ▼
Typed immutable runtime instruction
        │
        ▼
Engine evaluator / resolution queue
        │
        ▼
Atomic MatchState transition + EngineEvent
```

A Godot kliens nem értelmezi a képességdictionaryt.

# 10. Subject- és targetrendszer

A framework több subjectforrást támogat:

- self;
- target;
- trigger;
- previous;
- boardseek;
- tutor;
- index;
- egyedi játék-specifikus lookup.

Továbbá:

- subject count;
- all;
- up to;
- selection;
- selection count/type;
- optional selection;
- exclude self;
- property/token/parent/class/group filter;
- sort;
- previous subject továbbadása.

## 10.1 Erős AETERNA-tanulság

A targetelés nem csak egy `target_card_id`, hanem külön szerződés:

```text
SelectionContract
- selection_id
- source_reference
- candidate type
- min_count
- max_count
- exact/up_to
- optional
- ordering
- visibility
- filter predicate
- continuation
```

## 10.2 Jelenlegi kockázat

A selection közvetlen Godot popup és target arrow. A subjectek scene-node referenciák.

AETERNA-ban:

- az engine számolja a candidate listát;
- stabil CardReference/ObjectReference kerül a contractba;
- a kliens csak megjeleníti;
- a selection request state versiont hordoz;
- a választás visszaérkezésekor az engine újravalidál;
- a candidate identity viewer-szinten redaktált.

# 11. Költség dry-run

A Card `execute_scripts()` először COST_CHECK futást végez. Ha minden költség fizethető,
akkor újra lefuttatja a tasklistát normál módban. Ha nem fizethető, ELSE ág futhat.

## 11.1 Pozitívum

A framework felismeri a fontos elvet:

> a költséget és a szükséges targetet a hatások előtt ellenőrizni kell.

A tesztek külön vizsgálják:

- rotation cost;
- flip cost;
- target cost;
- multiple cost;
- token cost;
- property cost;
- card move cost;
- board/grid move cost.

## 11.2 Miért nem elég AETERNA production transitionnek?

A dry-run:

- nem immutable snapshoton fut;
- temp modifiereket ír globális és Card objektumokra;
- target popupot nyithat;
- ugyanazt a scene-node rendszert olvassa;
- a normal run később újra végrehajtja a taskokat;
- nincs state version;
- nincs transaction delta;
- nincs rollback;
- nincs final revalidation közvetlen commit előtt;
- a dry-run és normal run között más trigger/state változhat.

A nested task dokumentációja külön jelzi, hogy costként is módosíthat boardot, mielőtt a
teljes külső költséglánc eredménye ismert lenne.

## 11.3 AETERNA megfelelője

```text
Preflight
→ minden költség és selection candidate ellenőrzése
→ ResolutionPlan felépítése
→ minden replacement/reaction feldolgozása
→ final validation
→ egyetlen atomic commit
→ state version növelés
→ eventek
```

# 12. Trigger- és signalrendszer

A Card signalokat küld például:

- rotate;
- flip;
- view;
- board/pile/hand move;
- token change;
- attachment;
- property change;
- target.

A `SignalPropagator` összegyűjti ezeket, majd a scene tree összes `cards` és `scriptables`
csoporttagját végigjárja, és meghívja az `execute_scripts()` metódust.

## 12.1 Hasznos elv

- központi trigger discovery;
- trigger payload;
- trigger filterek;
- cardon kívüli scriptable objektumok;
- tag alapú szűrés;
- source/another/self különbség.

## 12.2 AETERNA-kockázat

A sorrend scene-tree sorrendből ered. Nem látható explicit:

- trigger ID;
- source sequence;
- priority;
- layer;
- mandatory/optional státusz;
- active-player ordering;
- timestamp;
- parent/correlation;
- maximum depth;
- loop detection;
- deterministic tie-break;
- event sequence.

A `execute_scripts` task maga is további kártyák scriptjeit indíthatja, és a kód figyelmeztet
az infinite loop lehetőségére.

## 12.3 AETERNA reaction queue

```text
Committed transition
→ trigger facts
→ eligible reaction candidates
→ deterministic ordering
→ mandatory resolution
→ optional player decision
→ internal instruction queue
→ loop/depth/step budget
→ final event correlation
```

A trigger signal nem azonos a player-facing EngineEventtel.

# 13. Filterrendszer

A ScriptProperties összetett filtereket támogat:

- property;
- token;
- parent/container;
- source/destination;
- face-up;
- rotation;
- counter;
- card count;
- group;
- class;
- modified property old/new value;
- tag;
- task name;
- comparison operators.

A filterlisták OR-logikát, az egyes dictionaryk mezői AND-logikát adhatnak.

## 13.1 AETERNA-tanulság

Az AETERNA effect compilerének szüksége lehet általános predicate AST-re:

```text
Predicate
├── And
├── Or
├── Not
├── Compare
├── HasKeyword
├── HasClass
├── IsInZone
├── IsControlledBy
├── HasActivity
├── HasModifier
└── CountMatches
```

## 13.2 Jelenlegi kockázat

- string kulcsok;
- futásidejű alapértékek;
- typo gyakran csak runtime alatt látható;
- raw node/class/group szűrés;
- globális counter lookup;
- nincs schema error location;
- nincs normalizált AST;
- nincs support registry;
- nincs package compilation failure.

AETERNA-ban hibás filter nem kerülhet be runtime package-be.

# 14. Previous subjects és stored result

A framework taskok között átadhat:

- previous subject listát;
- stored integer értéket;
- repeat eredményt;
- selected inputot;
- spawnolt kártyákat.

Ez fontos kompozíciós minta.

AETERNA megfelelője lehet:

```text
ResolutionLocal
- selected_objects
- previous_result
- integer_slots
- created_instance_ids
- calculated_amounts
```

Ez kizárólag egy engine-owned resolution scope-ban élhet, nem globális singletonban vagy
Godot node propertyben.

# 15. Nested script és recursive execution

A framework támogat nested tasklistát és más objektum scriptjének meghívását.

## 15.1 Előny

Összetett effectek új primitive írása nélkül kombinálhatók.

## 15.2 Kockázat

- rekurzív végrehajtás;
- infinite loop;
- nested költség részmutation;
- implicit parent-child kapcsolat;
- nincs explicit queue;
- nincs maximum step;
- nincs rollback;
- UI yieldekkel összekötött rules-flow.

AETERNA-ban a nested effectet a compiler inline-olhatja vagy kontrollált child resolution
plan lehet, explicit budgettel és correlation ID-val.

# 16. CardContainer és zónák

A CardContainer `Area2D`, amely Card child node-okat tart.

A kártyasorrend:

- scene child order;
- a „top” kártya a child lista vége;
- a „bottom” kártya az eleje;
- shuffle a child node-okat rendezi újra.

## 16.1 Hasznos Godot-view minta

- HandView;
- PileView;
- responsive anchor;
- pile count;
- hover/manipulation button;
- stack reorganization;
- viewport-resize kezelés.

## 16.2 AETERNA rules-zóna eltérés

Az AETERNA zóna:

- `CardInstanceId` listát tart;
- központi instance registryvel egyezik;
- owner/controller/visibility külön mező;
- zone sequence van;
- transition eventet ad;
- nem függ scene child ordertől;
- nem hagyja ki a dragged CardView-t a rules listából.

A CardContainer view kizárólag snapshotot renderelhet.

# 17. Board és grid

A Board `Control`, amely Card child node-okat és placement gridet kezel.

A framework támogat:

- szabad placementet;
- konkrét gridet;
- automatikus slotválasztást;
- több gridet;
- runtime grid spawnolást;
- attachmenteket.

## 17.1 AETERNA-tanulság

A Domain topológia megjelenítésére használható:

```text
DomainTopology projection
→ BoardGridView
→ PositionView
→ OccupancyView
```

## 17.2 Tiltott irány

A `BoardPlacementSlot.occupying_card` nem lehet authoritative occupancy.

Az AETERNA C# engine-ben:

- position ID;
- occupant card instance ID;
- topology invariant;
- placement validation;
- atomic move;
- event.

Godotban csak a vizuális megfelelőjük létezik.

# 18. Tokenek, counterek és temporary modifierek

A framework:

- Card tokeneket;
- Board countereket;
- temporary property modifier dictionaryket;
- alterant engine-t;
- runtime property aggregationt kezel.

## 18.1 Használható elv

- forrásazonosítható modifier;
- ideiglenes számítás;
- current/preview érték;
- effect-intenzitás board state alapján;
- token/counter filter.

## 18.2 AETERNA szükséges typed modell

```text
ModifierInstance
- modifier_instance_id
- source_reference
- target_reference
- layer
- operation
- value/expression
- duration
- created_sequence
- visibility
```

A payment preview vagy target preview temporary értéke nem írhat bele a canonical state-be.

# 19. Determinizmus

A framework egyik erős részlete a saját játék-RNG:

- string seed;
- `RandomNumberGenerator`;
- saját shuffle helper;
- RNG state visszaállítás;
- külön lehetőség vizuális, nem reprodukálandó random használatára;
- teszt bizonyítja, hogy azonos game seed azonos shufflet ad akkor is, ha Godot globális
  RNG-je közben változik.

## 19.1 AETERNA számára átvehető elv

A rules RNG és a visual RNG külön legyen.

```text
EngineRandom
- match seed
- deterministic state
- decision sequence
- recorded result

VisualRandom
- particle
- cosmetic animation
- nem befolyásolja a MatchState-et
```

## 19.2 Hiányok

A frameworkből nem bizonyított:

- random decision EngineEvent;
- event log;
- replay input;
- state hash;
- cross-runtime parity;
- RNG call ordering contract.

A ScriptingEngine `snapshot_id` például globális `rand_range` használatával készül, nem
a game RNG-ből. Ez nem rules random, de mutatja, hogy a randomforrások teljes elhatárolása
nem mindenhol szigorú.

# 20. Hidden information

A framework tud face-down kártyát és annak megtekintését kezelni.

Ez presentation-funkció, nem viewer-specific authority.

Nem látható:

- külön owner snapshot;
- opponent redaction;
- opaque hidden card reference;
- deck order elrejtés;
- event visibility;
- network payload projection.

AETERNA Godot-kliens nem kaphatja meg az ellenfél rejtett identityjét, majd nem pusztán
lefordítva jeleníti meg.

# 21. Card Library és Deck Builder

A framework kész Card Library és Deck Builder UI-t tartalmaz:

- list/grid mód;
- filter;
- preview;
- deck summary;
- quantity;
- deck load;
- card definition pool.

## 21.1 AETERNA számára használható

- gyűjteményböngésző;
- pakliépítő UI;
- filterchips;
- keyword/class/realm filter;
- deck validation result;
- kártyaelőnézet;
- mennyiségi vezérlők;
- import/export felület.

## 21.2 Engine-határ

A deck builder az AETERNA runtime package card definitionjeit és külön deck-validation
service eredményét használja.

A Godot UI nem döntheti el egyedül:

- minimum/maximum pakliméret;
- másolatszám;
- Birodalom/klán kompatibilitás;
- tiltott lap;
- formátum;
- kiegészítő aktiváltság;
- runtime package version.

# 22. Tesztek

A repository sok GUT tesztet tartalmaz:

- Card;
- CardContainer;
- anchor és scaling;
- mouse pointer;
- targeting;
- placement grid;
- RNG seed;
- scripting engine costs;
- subjects;
- filters;
- repeat;
- nested/execute scripts;
- alterants;
- shuffle;
- spawn;
- selection/popups;
- signal tags.

## 22.1 Erősség

A komplex interaction és effect DSL ténylegesen tesztelt.

## 22.2 AETERNA-korlát

A tesztek Godot scene-környezetben futnak. Nem bizonyítanak:

- pure C# authorityt;
- player-facing contractot;
- stale requestet;
- reject-no-mutationt;
- viewer redactiont;
- engine replayt;
- runtime package compiler parityt;
- Godot nélküli rules executiont.

Az AETERNA-nak továbbra is a C# headless tests az elsődleges proof.

# 23. CI és export

A GitHub Actions:

1. checkout;
2. külső `db0/godot-tester` action checkout;
3. GUT tesztek Godot 3.4.4 alatt;
4. Godot 3.4 HTML5 export;
5. itch.io publikálás.

## 23.1 Hasznos AETERNA-minta

Külön gate-ek:

```text
C# engine build/test
→ Godot import/parse
→ bridge smoke
→ export
→ artifact smoke
```

## 23.2 Kockázat

A CI külső repositoryból checkoutolt actionre és régi action-verziókra épül. Az AETERNA
saját CI-jében:

- commit-pinnelt action;
- kontrollált Godot-verzió;
- dependency hash;
- artifact audit;
- export smoke;
- release és debug elkülönítés

szükséges.

# 24. Licenc

A repository teljes LICENSE fájlja GNU AGPL v3.

Az addendum kimondja, hogy a Steamworks SDK kommunikációja nem aktiválja önmagában a
copyleft követelményt, de a Steamen terjesztett framework-alapú program többi részére
továbbra is AGPL-forrásközlési követelmény vonatkozik.

## 24.1 AETERNA döntés

- közvetlen framework-beemelés: nem;
- addonként bekötés: nem;
- source másolás: nem;
- scene/script másolás: nem;
- konkrét algoritmus átvétele: külön jogi döntés nélkül nem;
- általános architekturális és UX-elv tanulmányozása: igen;
- saját clean-room implementáció: igen.

# 25. Erősségek az AETERNA szempontjából

1. Nagyon széles kártya-presentation funkciókészlet.
2. Hand és pile layout.
3. Drag-and-drop.
4. Targeting arrow.
5. Attachment UX.
6. Face-down megjelenítés.
7. Token/counter UI.
8. Grid és free placement.
9. Card Library.
10. Deck Builder.
11. Dictionary-alapú card definition.
12. Készletfájlokra bontás.
13. Dictionary-alapú effect taskok.
14. Trigger/filter rendszer.
15. Optional és multiple-choice.
16. Selection és integer input.
17. Cost dry-run.
18. Previous subject és stored result.
19. Nested task.
20. Seedelt játék-RNG.
21. Visual RNG elkülönítésének gondolata.
22. Széles GUT tesztkészlet.
23. Automatikus CI és export.
24. Dokumentált upgrade és customization pontok.

# 26. Gyengeségek és kockázatok az AETERNA szempontjából

1. Godot 3 legacy technológia.
2. GDScript production rules authority.
3. Card node egyszerre view, state és rules actor.
4. Vizuális CardState alapján választ rules scriptágat.
5. `canonical_name` definition- és identity-szerepe.
6. Nincs stabil card instance ID.
7. Nincs owner/controller/visibility typed contract.
8. Scene child order a zónasorrend.
9. Globális `cfc` singleton.
10. Globális node map név alapú lookupkal.
11. Dictionary/string alapú opcode.
12. Raw node reference subjectként.
13. Runtime typo és schema hiba.
14. Nincs compiled typed AST.
15. Közvetlen scene-node mutation.
16. UI-dialog a rules evaluatorban.
17. Animációs yield a rules-flowban.
18. Cost dry-run nem tranzakció.
19. Nested cost részmutation lehetősége.
20. Nincs final revalidation.
21. Nincs state version.
22. Nincs ActionRequest/Response.
23. Nincs stable diagnostic.
24. Signal propagation scene-tree sorrendben.
25. Nincs reaction priority/order contract.
26. Nincs loop/depth budget.
27. Nincs typed event log.
28. Nincs viewer projection.
29. Nincs multiplayer authority.
30. Duplicate card name felülírásának veszélye.
31. Nincs package schema/version/hash.
32. AGPL licenc.
33. Közvetlen Godot 4 kompatibilitás nincs.
34. Runtime és presentation cache/állapot összefonódik.

# 27. AETERNA számára átvehető elvek

## 27.1 Effect primitive katalógus

A taskkészletből AETERNA-specifikus typed primitivek tervezhetők.

## 27.2 Cost preflight

A hatás előtt minden költség, target és selection ellenőrzendő.

## 27.3 Subject selector

Self, target, previous, tutor, boardseek jellegű fogalmak typed selectorokká alakíthatók.

## 27.4 Filter AST

Tulajdonság-, token-, zóna-, source- és triggerfilterek typed predicate-rendszerben.

## 27.5 Optional/multiple choice

Külön PendingDecision/SelectionContract.

## 27.6 Resolution-local adatok

Previous subject, stored integer és created instance ID kontrollált lokális scope-ban.

## 27.7 Rules és visual random különválasztása

Seedelt engine RNG, külön cosmetic RNG.

## 27.8 Godot view-komponensek

CardView, HandView, PileView, TargetingArrow, GridView, CardLibrary, DeckBuilder.

# 28. Amit nem szabad átvenni

1. `cfc` mint rules authority.
2. `NMAP` mint zónaregistry.
3. Card node mint runtime card instance.
4. canonical name mint card ID.
5. visual state mint rules zone.
6. scene child order mint deck/hand order.
7. dictionary task közvetlen runtime végrehajtása.
8. string method dispatch production engine-ben.
9. raw Node target.
10. UI yield az engine transitionben.
11. direct `move_to` mint rules zone move.
12. Card signal mint player-facing engine event.
13. scene-tree reaction ordering.
14. nested recursive script loop guard nélkül.
15. AGPL script vagy scene közvetlen másolása.
16. Godot 3 kód portolása az authority-rétegbe.

# 29. Javasolt AETERNA effect- és Godot-architektúra

```text
AETERNA authoring
├── card data
├── ability data
├── localized text
└── presentation metadata
        │
        ▼
Content Compiler
├── schema validation
├── duplicate ID check
├── selector compiler
├── predicate compiler
├── effect instruction compiler
├── diagnostic report
└── runtime package hash
        │
        ▼
Aeterna.Engine
├── EngineSession
├── LegalActionService
├── CostPreflight
├── SelectionService
├── ResolutionQueue
├── EffectEvaluator
├── ReactionResolver
├── TransitionBuilder
├── InvariantValidator
├── EngineEvent
└── ProjectionService
        │
        ▼
Aeterna.Godot
├── CardViewFactory
├── HandView
├── PileView
├── DomainGridView
├── WellspringView
├── TargetingArrow
├── SelectionWindow
├── CardLibrary
├── DeckBuilder
└── AnimationCoordinator
```

# 30. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | Typed effect instruction alapkészlet | Engine/Runtime | P0 |
| 2 | Selector és predicate AST | Runtime/Engine | P0 |
| 3 | Cost preflight + final revalidation | Engine | P0 |
| 4 | Pending selection contract | Contracts | P0 |
| 5 | Resolution-local result store | Engine | P1 |
| 6 | Determinisztikus reaction queue | Engine | P0 |
| 7 | Reaction depth/step budget | Engine | P0 |
| 8 | Trigger marker és EngineEvent különválasztása | Engine | P0 |
| 9 | Package schema/version/hash | Runtime | P0 |
| 10 | Duplicate card/ability ID diagnosztika | Tooling | P0 |
| 11 | CardView és CardInstance teljes elválasztása | Godot/Engine | P0 |
| 12 | ZoneView snapshot-alapon | Godot | P0 |
| 13 | TargetingArrow candidate listből | Godot/Bridge | P1 |
| 14 | SelectionWindow engine contractból | Godot/Bridge | P1 |
| 15 | Deck Builder külön validation service-szel | Tooling/Godot | P1 |
| 16 | Card Library runtime package-ből | Godot | P1 |
| 17 | Engine RNG és cosmetic RNG külön | Engine/Godot | P0 |
| 18 | Seed/replay/state-hash teszt | Tests | P0 |
| 19 | Effect compiler corpus teszt | Tests | P0 |
| 20 | AGPL közvetlen dependency tiltás | License | P0 |
| 21 | Godot 4 clean-room UI proof | Godot | P1 |
| 22 | Kódmásolás helyett funkciólista-alapú újraimplementálás | Projekt | P0 |

# 31. Bizonyítékjegyzék

| ID | Állítás | Forrásfájl | Forráspont |
|---|---|---|---|
| E-001 | Framework 2.2 és feature-lista | `README.md` | Provided features |
| E-002 | Dictionary Scripting Engine képességek | `README.md` | Scripting Engine Features |
| E-003 | Godot 3.4.4 GUT CI | `.github/workflows/main.yml` | test job |
| E-004 | Godot 3.4 HTML5 export | `.github/workflows/main.yml` | export job |
| E-005 | `cfc` autoload | `project.godot` | autoload |
| E-006 | Globális classok és GUT plugin | `project.godot` | script classes/editor plugins |
| E-007 | Card Area2D és visual FSM | `CardTemplate.gd` | fájl eleje |
| E-008 | Card signalok | `CardTemplate.gd` | signal blokk |
| E-009 | Card properties/scripts dictionary | `CardTemplate.gd` | exported vars |
| E-010 | Double click → execute scripts | `CardTemplate.gd` | input handler |
| E-011 | Drag drop → move_to | `CardTemplate.gd` | input handler |
| E-012 | Definitionből property mutation | `CardTemplate.gd` | setup/modify_property |
| E-013 | Visual state → hand/board/pile scriptág | `CardTemplate.gd` | get_state_exec |
| E-014 | Cost dry-run és actual execution | `CardTemplate.gd` | execute_scripts |
| E-015 | CardContainer scene-child kártyalista | `CardContainer.gd` | get_all_cards |
| E-016 | Scene-child order shuffle | `CardContainer.gd` | shuffle_cards |
| E-017 | Board mint Control node | `BoardTemplate.gd` | class definition |
| E-018 | `cfc` globális state és RNG | `CFControl.gd` | vars |
| E-019 | Node map | `CFControl.gd` | map_node |
| E-020 | Definition és script set load | `CFControl.gd` | load functions |
| E-021 | Seedelt RNG | `CFControl.gd` | set_seed |
| E-022 | Fisher–Yates-szerű shuffle | `CFUtils.gd` | shuffle_array |
| E-023 | RNG determinism teszt | `test_rng_seed.gd` | teljes fájl |
| E-024 | ScriptingEngine task API | `ScriptingEngine.gd` | fájl eleje |
| E-025 | String method dispatch és direct mutation | `ScriptingEngine.gd` | execute |
| E-026 | Container move globális NMAP-pal | `ScriptingEngine.gd` | move_card_to_container |
| E-027 | Spawn scene-node-ként | `ScriptingEngine.gd` | spawn_card |
| E-028 | Recursive execute_scripts warning | `ScriptingEngine.gd` | execute_scripts task |
| E-029 | Nested cost részmutation figyelmeztetés | `ScriptingEngine.gd` | nested_script |
| E-030 | Subject selectorok | `ScriptObject.gd` | _find_subjects |
| E-031 | Optional/selection | `ScriptTask.gd` | prime/check_confirm |
| E-032 | Task- és filterkulcsok | `ScriptProperties.gd` | teljes fájl |
| E-033 | Card definition dictionary | `SetDefinition_Demo2.gd` | CARDS |
| E-034 | Script definition dictionary | `SetScripts_Demo2.gd` | scripts |
| E-035 | SignalPropagator scene-tree scan | `CFControl.gd` | SignalPropagator |
| E-036 | GUT cost tesztkészlet | `test_scripting_engine_costs.gd` | teljes fájl |
| E-037 | CardContainer unit teszt | `test_cardcontainer_class.gd` | teljes fájl |
| E-038 | AGPL v3 | `LICENSE` | teljes licenc |
| E-039 | Steamworks addendum, AGPL megmarad | `ADDENDUM1` | teljes fájl |
| E-040 | Vizsgált commit | GitHub commit | `f3ca9afd...` |

# 32. Nyitott kérdések

1. A vizsgált commit importálható-e hibamentesen Godot 3.4.4 alatt?
2. Minden GUT teszt jelenleg PASS?
3. Milyen ismert flaky tesztek vannak?
4. Hány unit és integration teszt fut?
5. A duplicate card name felülírás tesztelt-e?
6. Van-e card definition schema validation?
7. A dictionary typo milyen diagnosztikát ad?
8. A cost dry-run és normal run között megváltozhat-e a state?
9. Nested cost milyen részmutationt hagyhat?
10. Van-e valódi transaction vagy rollback bármely tasknál?
11. Mi a signal/reaction pontos orderingje?
12. Lehetséges-e végtelen trigger loop?
13. Van-e runtime loop/depth limit?
14. Milyen stabil ordering van több azonos triggerű kártyánál?
15. A game RNG minden rules randomot lefed-e?
16. A `snapshot_id` nem-game-RNG használata okoz-e releváns eltérést?
17. Van-e tényleges replay serializer?
18. Hogyan tárolódik a deck?
19. Van-e save/load teljes match state-re?
20. Mennyire vihető át a UI Godot 4-re?
21. Mely CardView/DeckBuilder részek választhatók le rules kódról?
22. A Card state gép mely részei tisztán presentation állapotok?
23. Hogyan kezelné a framework a két azonos nevű, eltérő runtime példányt?
24. Hogyan kezelne viewer-specifikus hidden state-et?
25. Milyen asset licencek vannak a frameworkben?
26. Az AGPL addendum pontosan mely komponensekre vonatkozik?
27. A release export tartalmaz-e minden forrásközlési notice-t?
28. Mely primitivek fedik az AETERNA jelenlegi ability-support registryjét?
29. Mely AETERNA effectek igényelnek új typed instructiont?
30. Érdemes-e külön AETERNA effect-DSL fogalomtérképet készíteni?

# 33. Következő vizsgálati lépések

## 33.1 Codex nélkül

1. Helyi origin és HEAD ellenőrzése.
2. Godot 3.4.4 import.
3. GUT teljes tesztfuttatás.
4. Tesztlista és flaky státusz.
5. Card definition duplicate audit.
6. Script dictionary schema audit.
7. Cost dry-run parity scenario.
8. Nested partial-mutation scenario.
9. Trigger ordering trace.
10. Infinite loop scenario.
11. RNG call inventory.
12. Replay/save keresés.
13. Card Library és Deck Builder UI smoke.
14. Godot 4 portolhatósági jegyzék.
15. Asset- és licencinventár.
16. AETERNA effect primitive mapping külön dokumentumban.

## 33.2 Később Codexszel gyorsítható

1. teljes scene–script gráf;
2. dictionary kulcs- és opcode-inventory;
3. minden task → mutation path;
4. trigger call graph;
5. loop és recursion audit;
6. card definition/schema extractor;
7. AETERNA typed instruction mapping;
8. Godot 4 CardView/ZoneView clean-room proof;
9. effect compiler tesztgenerálás;
10. runtime support coverage report.

# 34. Végső minősítés

- **Godot presentation tanulási érték:** nagyon magas
- **Effect DSL tanulási érték:** nagyon magas
- **Költség-preflight tanulási érték:** magas
- **Selection/target UX:** magas
- **Authoritative engine érték:** alacsony
- **Contract és viewer projection érték:** alacsony
- **Determinism érték:** közepes; jó seedalap, hiányzó replay/event proof
- **Tesztelési érték:** magas Godot framework szinten
- **Modern technológiai illeszkedés:** alacsony
- **Licenc-kompatibilitás közvetlen használathoz:** alacsony
- **Közvetlen dependency:** elutasítandó
- **Clean-room inspiráció:** kiemelten ajánlott
- **Elemzés státusza:** első teljes source audit elkészült
- **Következő learning cél:** `kptmn/godot-card-game-framework4`

# 35. Változásnapló

## 0.1 – 2026-07-25

- elkészült a `db0/godot-card-game-framework` első teljes repository-forráskód-elemzése;
- rögzítésre került a Godot 3.4/GDScript technológiai állapot;
- feldolgozásra került a Card, CardContainer, Board és globális `cfc` szerkezet;
- feldolgozásra került a dictionary-alapú card és script definition;
- vizsgálat készült a ScriptingEngine task-, subject-, filter-, cost- és selection-rendszeréről;
- elhatárolásra került a cost dry-run és az AETERNA atomic transition;
- feldolgozásra került a trigger SignalPropagator és a determinisztikus ordering hiánya;
- rögzítésre került a seedelt RNG és a determinism teszt;
- vizsgálat készült a Card Library, Deck Builder, target, attachment és zónapresentation értékéről;
- rögzítésre került az AGPL licenckorlát;
- elkészült az AETERNA typed effect compiler és Godot view újraimplementálási javaslat;
- a következő elemzési cél `kptmn/godot-card-game-framework4`.
