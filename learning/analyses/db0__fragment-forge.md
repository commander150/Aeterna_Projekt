# AETERNA – db0/Fragment-Forge ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-25
- **Státusz:** repository-forrásokra épülő első teljes alkalmazás-, content-, deckbuilder-, effect- és authority-elemzés
- **Fő elemzési fájl:** `learning/analyses/db0__fragment-forge.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Repository:** `db0/Fragment-Forge`
- **Stabil upstream URL:** `https://github.com/db0/Fragment-Forge`
- **Vizsgált branch:** `main`
- **Vizsgált commit:** `759100774d46fb1a30fb08f2e42947e48af90c40`
- **Vizsgált commit dátuma:** 2021-07-19
- **README-verzió:** Fragment Forge v0.18
- **Szabálydokumentum-verzió:** Single-Player v0.10
- **Technológiai alap:** Godot 3.x / GDScript / config_version 4
- **Licenc:** AGPL-3.0 a kódra; assetek és shaderek egyedi licencekkel
- **Játékmód:** egyjátékos, három versenyfordulós kártyajáték
- **Tartalom:** README szerint 100 lapos core card base
- **AETERNA összehasonlítási bázis:** az aktuális C# authoritative engine-, runtime-package-, content-compiler-, deck-validációs-, contract- és Godot-bridge rendszer
- **Összehasonlítási szabály:** kizárólag az AETERNA rendszeréhez mérve
- **Vizsgálati korlát:** helyi Godot-import, GUT-futtatás, teljes játékthrough, deckfájl-tampering és export ebben a körben nem történt
- **CI-bizonyíték:** a vizsgált commitnál nincs GitHub status check vagy kapcsolt workflow run
- **Elsődleges AETERNA-érték:** valódi játékban alkalmazott dictionary effectrendszer, game-specific effectbővítés, 100 lapos contentstruktúra, persona/affinity/inspiration deckbuilder és szabálykikényszerítő UI
- **Elsődleges AETERNA-kockázat:** a canonical state Godot scene-node-okban és singletonokban él; a deck JSON nem verziózott és nem teljesen validált; több konkrét state-, index- és ability-consumption hiba található

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Projekt neve | Fragment Forge |
| Repository | `db0/Fragment-Forge` |
| Default branch | `main` |
| Vizsgált commit | `759100774d46fb1a30fb08f2e42947e48af90c40` |
| Repository állapot | nyilvános, nem archivált |
| Utolsó commit | PR #12 merge – minimum 30 lapos startgomb-ellenőrzés |
| Godot | 3.x, config_version 4 |
| Nyelv | GDScript |
| Core autoload | `cfc` / `CFControl.gd` |
| Játékspecifikus autoload | `ffc` / `FFControl.gd` |
| Rules state | Godot node-ok, singleton dictionaryk és scene child order |
| Content definition | nagy GDScript dictionary-készlet |
| Effect definition | kártyanévhez kötött dictionary task/filter DSL |
| Kártyaazonosítás | canonical card name |
| Runtime példány | Card scene-node referencia |
| Deckbuilder | lista/grid, filter, kategória, mennyiség, persona, affinity, inspiration |
| Deck persistence | lokális JSON-fájl |
| Deck schema/version | nincs |
| Játékszabály | külön Markdown + runtime GDScript |
| Tesztelés | GUT beépítve; kevés bizonyított projektspecifikus teszt |
| CI | nem talált |
| Multiplayer | roadmap, nincs megvalósítva |
| Telemetria | opcionálisnak szánt CGF-Stats kliens, deck- és kliensadatot küld |
| Licenc | AGPL-3.0; asset/shader licencek külön |
| AETERNA-prioritás | P0 – alkalmazott effect/content/deckbuilder tanulási forrás |
| Közvetlen integráció | elutasítandó |

# 2. Vezetői összefoglaló

A Fragment Forge azért fontos tanulási forrás, mert nem általános demó, hanem teljes,
játszható alkalmazás, amely egy kártyajáték-framework fogalmait tényleges tartalmi és
játékszabályi igényekre használja.

A repository megvalósít:

- külön core és játékspecifikus réteget;
- 100 lapos core kártyabázist;
- külön card definition és card script állományt;
- dictionary-alapú ability- és triggerleírást;
- game-specific effect taskot;
- game-specific triggerfiltereket;
- játékos-personákat saját scriptjeikkel;
- affinity/inspiration-alapú deckbuildinget;
- lista- és gridnézetű deckbuildert;
- lokális deckmentést és betöltést;
- háromfordulós egyjátékos szabályfolyamot;
- költségelőnézetet;
- effect-alapú cost modificationt;
- tutorialt;
- statisztikai beküldési klienst;
- shader-alapú kártyagrafikát.

A projekt azonban továbbra is egy Godot scene-tree rules engine:

```text
Card definition dictionary
        ↓
Card scene
        ↓
cfc / ffc singleton
        ↓
NMAP node registry
        ↓
ScriptingEngine
        ↓
közvetlen Card / Hand / Board / Counter / Competition mutation
```

AETERNA megfelelője:

```text
authoring source
→ content compiler
→ verziózott runtime package
→ typed CardDefinition / EffectInstruction
→ C# EngineSession
→ atomic MatchState transition
→ EngineEvent
→ viewer projection
→ Godot CardView / DeckBuilderView / animation
```

## 2.1 Rövid döntés

- **Valódi effect-DSL alkalmazásként:** kiemelten hasznos
- **Content authoring mintaként:** magas tanulási érték
- **Game-specific DSL-bővítésként:** magas tanulási érték
- **Deckbuilder UX-ként:** magas tanulási érték
- **Deck-validációs authorityként:** elégtelen
- **Runtime package mintaként:** elégtelen
- **Authoritative rules engine-ként:** nem használható
- **Multiplayer mintaként:** nem használható
- **Közvetlen kódbeemelés:** AGPL és architekturális okból nem
- **Clean-room szemantikai újraimplementálás:** igen
- **Legfontosabb tanulság:** a content- és deckbuilder-fogalmak értékesek, de minden
  validációt, effectet és state-változást typed, engine-owned rétegbe kell áthelyezni

# 3. Repository-rétegek

A repository két világosan elkülöníthető kódréteget tartalmaz.

## 3.1 Általános core réteg

```text
src/core/
├── Card
├── CardContainer
├── Hand
├── Pile
├── Board
├── BoardPlacementGrid
├── DeckBuilder
├── ScriptingEngine
├── ScriptTask
├── ScriptProperties
├── AlterantEngine
├── GameStats
└── CFControl
```

## 3.2 Fragment Forge réteg

```text
src/fragment_forge/
├── Board.gd
├── Deck.gd
├── Hand.gd
├── Competition.gd
├── FFCardTemplate.gd
├── FFScriptingEngine.gd
├── FFControl.gd
├── SP.gd
├── Persona.gd
├── InGamePersona.gd
├── deckbuilder/
└── cards/sets/
```

Ez jó szerkezeti elv:

> a generikus primitivek és a játék-specifikus content/rules bővítések külön
> namespace-ben és fájlrendszeri rétegben éljenek.

AETERNA-ban azonban a core határ ne scene-öröklés, hanem assembly- és contract-határ
legyen.

# 4. Technológiai állapot

## 4.1 Godot

A projekt:

- config_version 4;
- `Reference`, `yield`, régi signal-connect és Tween API;
- `Area2D` Card;
- Control-alapú Board;
- globális script classlista;
- Godot 3-as autoloadminta.

Ez nem vihető át közvetlenül az AETERNA Godot 4/C# irányába.

## 4.2 Autoloadok

```text
cfc = core framework state/service locator
ffc = Fragment Forge current deck/persona/difficulty/stats
```

A `cfc` tárol:

- beállításokat;
- card definitionöket;
- card scripteket;
- NMAP node registryt;
- active dragot;
- RNG-t;
- scripting engine referenciát;
- alterant cache-t;
- temp property modifiereket.

Az `ffc` tárol:

- aktuális deck dictionaryt;
- aktuális persona Resource-ot;
- nehézséget;
- game statst;
- tutorial flaget.

Ez kényelmes prototípus-szerkezet, de az AETERNA-ban a match state és a felhasználói
beállítások nem lehetnek ugyanazon globális runtime-környezet részei.

# 5. Kártyaadatmodell

A core set egy nagy dictionary.

A mezők például:

```text
Type
Tags
Abilities
Time
Value
Kudos
skill_req
cred_req
motivation_req
_illustration
_affinity
_influence
_abilities_power
_max_allowed
```

## 5.1 Erősségek

- jól elkülönül a kijelzett és a metaadat;
- külön CardConfig sorolja a string, number és array mezőket;
- a `_` prefix metaadatot jelöl;
- a card type meghatározza a scene template-et;
- külön affinity és influence adat;
- cardonként quantity override;
- generated value sentinel;
- illusztráció-credit;
- kártyaszöveg és effect script külön.

## 5.2 AETERNA-hiányok

- nincs stabil `card_id`;
- a kártyanév a kulcs;
- a név egyben content lookup és asset lookup;
- nincs schema version;
- nincs package ID;
- nincs set ID/printing ID;
- nincs content hash;
- nincs duplicate-name hard failure;
- nincs unknown-field policy;
- nincs buildidős type validation;
- nincs lokalizációs kulcs;
- a rules és presentation meta egy dictionaryben él;
- a GEN sentinel implicit authoringkonvenció.

# 6. Definition és effect különválasztása

A projekt külön kezeli:

```text
SetDefinition_Core.gd
SetScripts_Core.gd
```

Ez kifejezetten jó elv.

A definition tartalmazza:

- nyomtatott tulajdonságokat;
- deckbuilding adatokat;
- presentation metadata egy részét.

A scripts fájl tartalmazza:

- manual effecteket;
- triggert;
- alterantot;
- targetet;
- filtert;
- costot;
- zónamozgást;
- counter- és tokenmódosítást;
- nested executiont;
- per-expressiont.

AETERNA-ban ennek typed megfelelője:

```text
CardDefinition
AbilityDefinition
TriggerDefinition
EffectInstruction[]
PresentationDefinition
LocalizedText
```

# 7. Content load és ütközési kockázat

A `CFControl` a setfájlokat könyvtárból gyűjti.

## 7.1 Definition merge

```text
combined_sets[card_name] = set_dict[card_name]
```

Azonos név esetén a későbbi definition csendben felülírhatja a korábbit.

## 7.2 Script lookup

A scriptbetöltő kártyánként végigmegy a scriptfájlokon, és az első nem üres találatnál
megáll.

Kockázatok:

- fájlrendszeri sorrendtől függő eredmény;
- duplicate script nincs diagnosztizálva;
- definition és script ütközési szabály eltér;
- nincs package dependency vagy priority;
- nincs compiler report;
- nincs source location.

Az AETERNA content compilernek minden duplicate és shadowing esetet explicit hibaként
vagy deklarált override-ként kell kezelnie.

# 8. Generated card value

A shaderlapok `Value` mezője lehet `GEN = -1`.

A runtime formula:

```text
Value = Time + 1 + skill_req * 2 - abilities_power
```

## 8.1 Használható elv

- authoringsegéd;
- balanszheurisztika;
- automatikus alapérték;
- deckbuilder-previewben is használható.

## 8.2 AETERNA-javaslat

A formula buildidőben fusson:

```text
source field + formula version
→ compiler-generated explicit value
→ audit report
→ runtime package
```

A runtime ne módosítsa csendben a nyomtatott CardDefinitiont.

# 9. CardConfig

A CardConfig rögzíti:

- három card type-ot;
- négy affinityt;
- megjelenített mezőket;
- scene propertyt;
- 0-nál rejtett mezőket;
- aktív tageket;
- tagmagyarázatokat.

Ez jó példa egy központi content-presentation policyra.

AETERNA-ban külön legyen:

```text
RulesSchema
PresentationSchema
DeckbuildingSchema
LocalizationSchema
```

Egyetlen CardConfig ne legyen egyszerre rules-, UI- és deckbuilder-authority.

# 10. Dictionary effectrendszer

A SetScripts_Core nagy, kártyanév szerint indexelt dictionaryt ad vissza.

Támogatott minták:

- manual hand/board effect;
- install trigger;
- competition end;
- token trigger;
- counter trigger;
- alterant;
- cost task;
- move to container;
- deckből húzás;
- target;
- boardseek;
- property filter;
- tagfilter;
- current place;
- first played;
- previous result;
- stored integer;
- nested script;
- execute another object's script;
- optional/multiple-choice flow.

Ez a repository legerősebb AETERNA-tanulsága:

> összetett kártyakészlet leírható kompozíciós effect primitivekkel, kártyánkénti
> egyedi osztályok tömege nélkül.

# 11. Game-specific DSL-bővítés

A Fragment Forge két fontos bővítési pontot használ.

## 11.1 Saját effect task

A `FragmentForgeScriptingEngine` új `mod_competition` taskot ad.

Ez képes:

- place kiválasztására;
- direkt vagy stored integer módosításra;
- per-expressionre;
- inversionre;
- alterantokra;
- set-to módra;
- cost dry-runra;
- stored result képzésére.

## 11.2 Saját filterek

Az `SP` kibővíti a triggerfiltert:

- aktuális helyezés;
- nem aktuális helyezés;
- első lap;
- első laptípus;
- prismatic egyediség.

Ez jó extension-point szemlélet.

## 11.3 AETERNA megfelelője

```text
EffectOpcodeRegistry
PredicateOpcodeRegistry
CompilerPlugin
RuntimeSupportRegistry
```

A bővítés typed és versioned legyen, ne string method-dispatch és globális singleton lookup.

# 12. Effect authority problémája

A taskok közvetlenül:

- Card node-ot mozgatnak;
- Board countert írnak;
- Competition node-ot módosítanak;
- tokeneket írnak;
- globális NMAP node-okat használnak;
- UI-targetelésre várnak;
- Tweenre vagy signalra yieldelnek.

A subjectek gyakran Card vagy más Godot node referenciák.

AETERNA-ban:

```text
EffectInstruction
→ immutable input snapshot
→ ResolutionPlan
→ final revalidation
→ atomic MatchState commit
```

A Godot node csak az eredményt rendereli.

# 13. Cost dry-run

A Card és Persona effectek COST_CHECK futást végeznek, majd siker esetén normál futást.

## 13.1 Pozitívum

A projekt felismeri, hogy:

- több költséget együtt kell előellenőrizni;
- targetválasztás is lehet preflight része;
- sikertelen költség esetén effect nem futhat;
- ELSE ág létezhet.

## 13.2 Hiány

- ugyanazt a scene state-et olvassa;
- temp modifiereket kezel;
- nincs immutable state snapshot;
- nincs state version;
- nincs explicit resolution plan;
- nincs rollback;
- nincs commit boundary;
- a dry-run és execution között változhat a state;
- nested task részmutationt okozhat.

# 14. Persona mint leader/commander fogalom

A Persona tartalmaz:

- nevet;
- affinityt;
- inspirationt;
- képességszöveget;
- artot;
- effect dictionaryt;
- usage frequencyt.

Lehetséges frequencyk:

- always;
- once per competition;
- once per game.

Ez hasznos AETERNA-tanulság vezér-, avatár- vagy leaderjellegű objektumhoz.

## 14.1 Konkrét ability-consumption hiba

Az InGamePersona a gombot letiltja **a COST_CHECK előtt**, ha a frequency nem `always`.

Ha:

- a cost dry-run sikertelen;
- a targetelés nem fejeződik be;
- a cost nem fizethető;

a persona a kód alapján továbbra is letiltva maradhat.

Ez azt jelenti, hogy a használat sikertelen activationre is elfogyhat.

AETERNA-ban:

```text
usage counter
→ csak accepted, committed action után növekszik
```

# 15. Persona állapot mint UI-state

A persona használhatósága egy Button `disabled` állapotából következik.

Ez egyszerre:

- presentation;
- input policy;
- rules usage state;
- alterant availability.

AETERNA-ban külön:

```text
PersonaState
- uses_remaining
- reset_scope
- exhausted
- active modifiers
```

és ebből képzett UI disabled state szükséges.

# 16. Deckbuilder – generikus képességek

A core deckbuilder támogat:

- available card listát;
- gridnézetet;
- listanézetet;
- card previewt;
- card category csoportosítást;
- mennyiségi vezérlést;
- global max quantityt;
- cardonkénti max quantityt;
- minimum és maximum deckméretet;
- textfiltert;
- property filtergombokat;
- random decknevet;
- JSON save/loadot;
- delete/resetet;
- deck summaryt.

Ez jelentős AETERNA UX-referencia.

# 17. Fragment Forge deckbuilder-bővítés

A játékspecifikus deckbuilder hozzáad:

- persona választást;
- affinity ikont;
- inspiration maximumot;
- shader skill alapú inspiration költséget;
- off-affinity influence költséget;
- persona-specifikus kedvezményt;
- affinity filtergombot;
- shader value generálást;
- animált preview/grid beállítást;
- persona mentést a deck JSON-ba.

Ez már valódi domain-deckbuilder.

# 18. Deck-validációs modell

A deckbuilder UI pirossal jelzi:

- minimum/maximum card count problémát;
- inspiration túllépést.

A quantity objektumok korlátozhatják a kártyamennyiséget.

A NewGame azonban csak ezt ellenőrzi:

```text
deck.total >= 30
```

A start gate nem bizonyítottan ellenőrzi újra:

- maximum méretet;
- persona jelenlétét;
- inspirationt;
- off-affinity influence-t;
- cardonkénti mennyiséget;
- Restricted taget;
- ismeretlen kártyát;
- negatív quantityt;
- package/set kompatibilitást.

AETERNA-ban egyetlen pure `DeckValidator` szolgálja:

- deckbuilder UI-t;
- mentést;
- importot;
- match startot;
- szervert;
- migrationt.

# 19. Módosítható deck JSON

A mentett formátum:

```json
{
  "persona": "...",
  "name": "...",
  "cards": {
    "Card Name": 3
  },
  "total": 30
}
```

## 19.1 Hiányzó mezők

- schema version;
- game/content version;
- format ID;
- package hash;
- stable card ID;
- deck ID;
- checksum/signature;
- created/modified timestamp;
- validation result;
- migration version.

## 19.2 Trust-probléma

A JSON kézzel módosítható.

A loader csak azt ellenőrzi, hogy a root dictionary.

A NewGame a `total` mező alapján engedélyezi a startot.

Egy módosított deck például:

```json
{
  "total": 30,
  "cards": {}
}
```

értékkel átjuthat a startgomb ellenőrzésén, miközben a tényleges deck üres.

A Board később közvetlenül példányosítja a `cards` dictionary tartalmát.

# 20. Deckfájl-hibakategóriák

A source alapján külön tesztelendő:

1. hiányzó `name`;
2. hiányzó `total`;
3. hiányzó `cards`;
4. hiányzó `persona`;
5. ismeretlen persona;
6. ismeretlen card name;
7. negatív quantity;
8. nem egész quantity;
9. rendkívül nagy quantity;
10. duplicate JSON key;
11. `total` és tényleges összeg eltérése;
12. malformed JSON;
13. nem dictionary root;
14. régi schema;
15. tiltott vagy deaktivált kiegészítőlap;
16. hibás filename.

# 21. Decknév és fájlútvonal

A save és delete közvetlenül ezt használja:

```text
DECKS_PATH + deck_name + ".json"
```

Nem látható:

- filename sanitization;
- path separator tiltás;
- reserved filename policy;
- üres név tiltás;
- collision policy;
- atomic write;
- backup;
- write-then-rename.

AETERNA-ban:

```text
deck_id → belső filename
display_name → külön metadata
```

szükséges.

# 22. Hiányzó persona edge case

A deckmentés persona nélkül is létrehozhat `persona: null` értéket.

A NewGame ilyenkor `current_persona = null` állapotot állít, de a startot a total alapján
engedélyezheti.

A Board később valid decknél hivatkozik:

```text
ffc.current_persona.persona_name
```

Ez null persona esetén runtime hibát okozhat.

A match start előtt teljes DeckDefinition + PersonaDefinition validáció kötelező.

# 23. Game start és deckauthority

A Board:

1. a current deck dictionaryből Card scene-eket példányosít;
2. a node-okat a Deck alá teszi;
3. child ordert shuffle-öl;
4. starting handet húz;
5. persona game_start scriptet futtat.

Nincs:

- immutable deck snapshot;
- stable card instance ID;
- match ID;
- state version;
- load diagnostic;
- card count hard failure;
- package compatibility check;
- deck hash.

# 24. Hand és húzás

A Hand:

- 10-es hand size-t állít;
- a top Card node-ot olvassa;
- motivation és hand count alapján 1 vagy 2 time költséget számol;
- közvetlenül countert csökkent;
- game statst ír;
- Card node-ot mozgat.

## 24.1 Race/atomicity hiány

A folyamat:

```text
read top
→ calculate cost
→ read counter
→ modify counter
→ move Card
```

nem egy atomic engine transition.

AETERNA-ban:

```text
DrawCardAction
→ final validation
→ counter delta + zone move egy commitban
```

# 25. Starting hand hibaeset

A `fill_starting_hand()` addig fut, amíg a kézben nincs öt lap.

Nem ellenőrzi, hogy a deck kiürült-e.

Üres vagy négy lapnál kisebb módosított deck esetén:

```text
get_top_card() → null
null.move_to(...)
```

runtime hiba lehet.

Ez összekapcsolódik a `total` mezőben megbízó NewGame validációval.

# 26. Card play-cost rendszer

Az FFCard több rétegben ellenőriz:

- Time;
- Kudos;
- skill;
- cred;
- motivation;
- Unique;
- Reputation;
- unplayable flag;
- egyes speciális lapok.

A költségelőnézet színnel jelzi:

- normál;
- csökkentett;
- növelt;
- lehetetlen.

Továbbá részletes modifier breakdown készül.

Ez jó AETERNA UX-minta:

```text
ActionCostPreview
- base
- final
- source modifiers
- requirement violations
- stable diagnostics
```

## 26.1 Hardcoded card special case

A `Matrix` nevű lap külön `match canonical_name` ágban szerepel.

Ez azt jelzi, hogy a deklaratív DSL nem fedett le minden effektet.

AETERNA-ban a compiler support report jelezze:

- deklaratívan támogatott;
- typed custom opcode szükséges;
- implementálatlan.

A card name alapú runtime branch kerülendő.

# 27. Rules és presentation összefonódása

Az FFCard `_process`:

- shader time/frame adatot frissít;
- animation policyt kezel;
- modified propertyt számol;
- kártyalabelt ír;
- modifier színezést végez;
- debug költséget számol.

A Competition `_process`:

- minden frame-ben végigolvassa a board cardjait;
- demo value-t számol;
- alterantot kér;
- placement UI-t fest;
- current place-et módosít.

Ez sok rules-lekérdezést köt a render frame-hez.

AETERNA-ban:

```text
state commit
→ derived state recomputation
→ event/snapshot
→ UI update
```

szükséges.

# 28. Konkrét stale-placement hiba

A Competition `_process` csak akkor állítja `current_place` értékét, ha az adott
küszöb teljesül.

Ha a játékos korábban elért egy helyezést, majd a demo value csökken:

- a label pirosra válhat;
- `current_place` azonban nem kerül vissza `-1` vagy alacsonyabb értékre.

Így a forduló végén korábbi, már nem teljesített helyezés maradhat érvényben.

A derived state-et minden számításnál teljesen újra kell képezni.

# 29. Konkrét place-index hiba

A Place enum:

```text
THIRD = 0
SECOND = 1
FIRST = 2
```

A `mod_place_requirements()` validációja:

```text
if place > 3 or place < 1
```

Következmény:

- a THIRD = 0 hibásként elutasításra kerül;
- a 3-as index átjuthat, majd array access hibát okozhat.

Helyes tartomány:

```text
0 <= place < placement_requirements.size()
```

# 30. Competition random és replay

A Board minden nem-teszt játékhoz random seedet generál.

A Competition ebből választ versenyt.

Pozitívum:

- központi game RNG létezik.

Hiány:

- a seed nincs match artifactban;
- nincs event log;
- nincs random decision event;
- nincs replay input;
- nincs state hash;
- nincs cross-runtime proof.

# 31. Persona és card triggerordering

A framework signal propagator minden `cards` és `scriptables` csoporttagot végigjár.

A Fragment Forge további triggert ad:

- competition_ended;
- placement_modified;
- persona scripts.

Nem látható explicit:

- deterministic priority;
- timestamp;
- source sequence;
- mandatory/optional layer;
- active player order;
- loop/depth limit;
- correlation ID.

A scene-tree iteration sorrend rules orderingként működhet.

# 32. Tutorial

A tutorial közvetlen node referenciákat kap:

- start button;
- counters;
- competition;
- game goal;
- persona;
- deck;
- hand;
- discard;
- board zones.

Ez hatékony egy szorosan kötött tutorialhoz.

AETERNA-ban jobb:

```text
TutorialStep
- semantic anchor ID
- required state predicate
- allowed actions
- highlight target
- completion event
```

Így a tutorial nem függ konkrét scene pathoktól.

# 33. GameStats és telemetria

A GameStats képes külső szolgáltatásnak elküldeni:

- decket;
- persona adatot a deck részeként;
- kliens operációs rendszert;
- végső state-et;
- részleteket.

A HTTP-kezelés több helyen `assert()` hívást használ.

AETERNA-követelmények:

- explicit opt-in;
- adatminimalizálás;
- privacy notice;
- timeout;
- retry/backoff;
- offline-safe működés;
- a telemetria hibája ne állítsa le a játékot;
- deck tartalma csak indokolt és anonimizált formában menjen;
- külön telemetry DTO és schema version.

# 34. Multiplayer-státusz

A README a multiplayer szabályokat roadmapként jelöli.

A source auditban nem találtunk:

- authoritative server;
- RPC contract;
- player projection;
- hidden information protection;
- reconnect;
- state sync;
- server-side deck validation.

A jelenlegi architecture single-player scene authority.

# 35. Hidden information

Egyjátékos módban a hidden-information biztonság nem elsődleges.

Ha ugyanez a model multiplayerre kerülne:

- minden Card node teljes definitiont tart;
- deck order scene child orderben van;
- face-down csak presentation;
- cfc globálisan minden node-ot elér.

AETERNA-ban a viewer projection már az engine contract része kell legyen.

# 36. Tesztelési állapot

A repository:

- tartalmaz GUT addont;
- tartalmaz UTcommon helper scene-eket;
- tartalmaz legalább egy `test_scripting_engine_per.gd` integration fájlt.

A megtalált integration fájl csak setupot tartalmazott, assertion/test metódust nem.

A vizsgált commitnál:

- nincs status check;
- nincs workflow run;
- nincs bizonyított automatizált teljes tesztfuttatás.

A README „full rules enforcement” állítása ezért nem egyenlő teljes regressziós proof-fal.

# 37. Szükséges AETERNA-tesztkategóriák

- content compiler schema;
- duplicate card ID;
- definition/script parity;
- every ability supported;
- deck JSON tampering;
- missing persona;
- unknown card;
- total mismatch;
- negative/huge quantity;
- inspiration overflow;
- restricted quantity;
- starting hand short deck;
- failed persona action does not consume use;
- third-place modification;
- invalid place index;
- placement downgrade;
- trigger ordering;
- loop limit;
- deterministic seed;
- replay parity;
- reject-no-mutation;
- hidden projection;
- telemetry offline failure.

# 38. Licenc

A repository kódja AGPL-3.0.

A README szerint:

- a kód AGPL3;
- assetek és shaderek saját licenceket jelölnek.

AETERNA-döntés:

- közvetlen source-beemelés: nem;
- core framework beágyazása: nem;
- scriptmásolás: nem;
- deckbuilder scene másolása: nem;
- shader/asset átvétel: külön licenc nélkül nem;
- általános content/effect/deckbuilder elvek tanulmányozása: igen;
- clean-room typed implementáció: igen.

# 39. Erősségek az AETERNA szempontjából

1. Valódi, játszható kártyajáték.
2. 100 lapos core content.
3. Definition és script különválasztás.
4. Dictionary effect DSL nagy contenten.
5. Game-specific opcode.
6. Game-specific predicate.
7. Persona/leader rendszer.
8. Usage frequency fogalom.
9. Affinity deckbuilding.
10. Inspiration budget.
11. Influence költség.
12. Cardonkénti quantity override.
13. Lista- és grid deckbuilder.
14. Filter és preview.
15. JSON save/load.
16. Generated card value.
17. Cost preview és modifier breakdown.
18. Difficulty modifierréteg.
19. Tutorial.
20. Game stats adapter.
21. Seedelt RNG-alap.
22. Core és alkalmazási réteg elkülönítése.
23. AGPL forrásból auditálható teljes implementáció.

# 40. Gyengeségek és kockázatok

1. Godot 3 legacy technológia.
2. Scene tree canonical state.
3. Globális `cfc` és `ffc`.
4. NMAP node service locator.
5. Card name mint ID.
6. Card node mint runtime instance.
7. Nincs state version.
8. Nincs atomic transition.
9. Nincs typed request/response.
10. Nincs replay.
11. Nincs state hash.
12. Nincs multiplayer.
13. Nincs hidden projection.
14. String opcode és raw node subject.
15. UI yield a rules flowban.
16. Silent duplicate definition overwrite.
17. First-found script shadowing.
18. Nincs content schema/package/hash.
19. Runtime generated printed value.
20. Hardcoded card-name special case.
21. Persona use sikertelen activationnél elfogyhat.
22. Deck JSON módosítható.
23. `total` mezőben megbízik.
24. Hiányzó persona crash-kockázat.
25. Starting hand short-deck null-kockázat.
26. Ismeretlen card name nincs preflightolva.
27. Negatív/óriási quantity nincs validálva.
28. Deck filename nincs sanitizálva.
29. Save nem atomikus.
30. Placement stale-state hiba.
31. Place index off-by-one hiba.
32. Frame-enkénti rules recomputation.
33. Scene-tree triggerordering.
34. Nincs loop/depth budget.
35. Telemetria assertokra támaszkodik.
36. Kevés bizonyított projektspecifikus teszt.
37. Nincs CI proof.
38. AGPL közvetlen integrációs kockázat.
39. Asset/shader licencek külön kezelendők.

# 41. AETERNA számára átvehető elvek

## 41.1 Content layering

Definition, effect, presentation és balance metadata külön rétegben.

## 41.2 Typed effect extension

Game-specific opcode és predicate registry.

## 41.3 Deckbuilder domain

Persona/leader, affinity, influence és budget-alapú validation.

## 41.4 Generated balance metadata

Buildidős formula és audit report.

## 41.5 Cost explanation

Base cost, modifierforrások és diagnosztika.

## 41.6 Difficulty ruleset

Typed scenario modifier package.

## 41.7 Tutorial semantic contract

State predicate és action-based completion.

## 41.8 Telemetry adapter

Match enginetől leválasztott, hibabiztos opt-in szolgáltatás.

# 42. Amit nem szabad átvenni

1. Godot node mint MatchState.
2. Singleton dictionary mint match authority.
3. NMAP mint rules object registry.
4. Card name mint stabil ID.
5. JSON `total` mint validációs bizonyíték.
6. UI szín mint deckvaliditás.
7. Scene button disabled mint ability usage state.
8. Runtime definition mutation.
9. Silent content override.
10. Raw filename a deck display name-ből.
11. Frame-loop rules derivation.
12. Card-name hardcode.
13. Telemetry assert mint error policy.
14. AGPL kódmásolás.

# 43. Javasolt AETERNA content-architektúra

```text
Authoring sources
├── CardSource
├── AbilitySource
├── PersonaSource
├── DeckRuleSource
├── DifficultySource
├── PresentationSource
└── LocalizationSource
        │
        ▼
Content Compiler
├── schema validation
├── stable ID assignment
├── duplicate detection
├── generated value calculation
├── effect AST compilation
├── support registry check
├── asset preflight
├── localization check
├── diagnostic report
└── package hash/version
        │
        ▼
Runtime Package
├── CardDefinition
├── AbilityDefinition
├── PersonaDefinition
├── DeckFormatDefinition
├── DifficultyDefinition
└── PresentationDefinition
```

# 44. Javasolt AETERNA deckbuilder-architektúra

```text
ContentCatalog
        │
        ▼
DeckDraft
├── deck_id
├── display_name
├── format_id
├── persona_id
├── card quantities
└── source package hash
        │
        ▼
DeckValidator
├── minimum/maximum size
├── quantity
├── realm/clan/persona
├── budget/influence
├── set activation
├── bans/restrictions
└── diagnostics
        │
        ▼
ValidatedDeckArtifact
├── schema_version
├── content_version
├── normalized entries
├── validation hash
└── migration metadata
```

# 45. Javasolt AETERNA effect-architektúra

```text
EffectSource
→ typed EffectInstruction
→ Selector AST
→ Predicate AST
→ CostPreflight
→ PendingSelection
→ ResolutionQueue
→ final revalidation
→ atomic commit
→ EngineEvent
```

A persona és difficulty is ugyanebben a typed runtime modellben működhet, külön source
és usage-state contracttal.

# 46. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | Stable card/ability/persona ID | Content | P0 |
| 2 | Content schema/version/hash | Compiler | P0 |
| 3 | Definition/script duplicate hard failure | Compiler | P0 |
| 4 | Buildidős generated value | Compiler | P1 |
| 5 | Effect opcode support registry | Runtime | P0 |
| 6 | Typed game-specific opcode extension | Engine | P0 |
| 7 | Typed predicate extension | Engine | P0 |
| 8 | DeckValidator egyetlen authorityként | Application | P0 |
| 9 | ValidatedDeckArtifact | Contract | P0 |
| 10 | Deck JSON migration/version | Tooling | P0 |
| 11 | Deck filename `deck_id` alapján | Tooling | P0 |
| 12 | Atomic deck save | Tooling | P1 |
| 13 | Persona usage state engine-ben | Engine | P0 |
| 14 | Usage csak committed success után fogyjon | Engine | P0 |
| 15 | Derived placement teljes újraszámítása | Engine | P0 |
| 16 | Enum/index bound tests | Tests | P0 |
| 17 | Starting-hand short deck guard | Engine | P0 |
| 18 | ActionCostPreview contract | Contract/Godot | P1 |
| 19 | DifficultyDefinition package | Runtime | P1 |
| 20 | Tutorial semantic step contract | Godot/Application | P1 |
| 21 | Telemetry opt-in és failure isolation | Services | P1 |
| 22 | Trigger priority/depth budget | Engine | P0 |
| 23 | Deterministic seed/event/replay | Engine | P0 |
| 24 | AGPL direct dependency tiltás | License | P0 |
| 25 | Asset/shader licence inventory | License | P1 |

# 47. Bizonyítékjegyzék

| ID | Állítás | Forrás |
|---|---|---|
| E-001 | Fragment Forge v0.18 | `README.md` |
| E-002 | early release, full rules enforcement claim | `README.md` |
| E-003 | 100-card core és deckbuilder | `README.md` |
| E-004 | multiplayer csak roadmap | `README.md` |
| E-005 | AGPL code, külön asset/shader licencek | `README.md`, `LICENSE` |
| E-006 | Godot config_version 4 | `project.godot` |
| E-007 | cfc és ffc autoload | `project.godot` |
| E-008 | core és game-specific classréteg | `project.godot` |
| E-009 | cfc definitions/scripts/NMAP/RNG/cache | `CFControl.gd` |
| E-010 | silent definition merge | `CFControl.gd` |
| E-011 | first-found script lookup | `CFControl.gd` |
| E-012 | card fields és affinity | `CardConfig.gd` |
| E-013 | 100-card dictionary | `SetDefinition_Core.gd` |
| E-014 | dictionary effectkészlet | `SetScripts_Core.gd` |
| E-015 | custom `mod_competition` opcode | `FFScriptingEngine.gd` |
| E-016 | custom trigger predicates | `SP.gd` |
| E-017 | persona definition és effectek | `Personas.gd` |
| E-018 | persona cost dry-run | `InGamePersona.gd` |
| E-019 | persona disable COST_CHECK előtt | `InGamePersona.gd` |
| E-020 | core deckbuilder min/max/filter/save/load | core `DeckBuilder.gd` |
| E-021 | persona/affinity/inspiration deckbuilder | custom `deckbuilder/DeckBuilder.gd` |
| E-022 | deck JSON loader csak dictionary rootot ellenőriz | `DeckLoader.gd` |
| E-023 | startgomb csak `deck.total >= 30` | `NewGame.gd` |
| E-024 | current deck és persona globális state | `FFControl.gd`, `NewGame.gd` |
| E-025 | deck scene-node példányosítás és shuffle | `Board.gd` |
| E-026 | starting hand loop deck-empty guard nélkül | `Hand.gd` |
| E-027 | manual draw direct counter + card move | `Hand.gd` |
| E-028 | deck clickből draw signal | `Deck.gd` |
| E-029 | card cost és hardcoded Matrix | `FFCardTemplate.gd` |
| E-030 | competition frame-based derived state | `Competition.gd` |
| E-031 | stale `current_place` lehetősége | `Competition.gd` |
| E-032 | place enum 0–2, validator 1–3 | `Competition.gd` |
| E-033 | random competition | `Competition.gd`, `Board.gd` |
| E-034 | GameStats deck/client payload | `GameStats.gd` |
| E-035 | GUT jelen van | `project.godot`, `addons/gut/` |
| E-036 | egy megtalált integration fixture assertion nélkül | `tests/integration/test_scripting_engine_per.gd` |
| E-037 | nincs commit status | GitHub combined status |
| E-038 | nincs kapcsolt workflow run | GitHub workflow query |
| E-039 | vizsgált HEAD és dátum | GitHub commit metadata |

# 48. Prioritásos helyi reprodukciók

## P0-1 – Hamis deck total

1. kézzel létrehozott JSON `total: 30`;
2. `cards: {}`;
3. betöltés;
4. startgomb aktív;
5. starting hand null-card hiba ellenőrzése.

## P0-2 – Persona nélküli deck

1. 30 valós kártya;
2. `persona: null`;
3. game start;
4. `current_persona.persona_name` hiba ellenőrzése.

## P0-3 – Sikertelen persona activation

1. costtal vagy targettel rendelkező once-per-game persona;
2. cost/target failure;
3. ellenőrizni, disabled marad-e.

## P0-4 – Placement downgrade

1. küszöb elérése;
2. demo value csökkentése;
3. round end;
4. korábbi helyezés megmaradásának ellenőrzése.

## P0-5 – Third-place modification

1. `mod_competition` THIRD = 0 targettel;
2. ellenőrizni az elutasítást.

## P0-6 – Invalid place 3

1. place = 3;
2. ellenőrizni array out-of-range útvonalat.

## P1-1 – Ismeretlen card name

1. JSON deck ismeretlen kulccsal;
2. betöltés;
3. `instance_card` failure.

## P1-2 – Negatív és extrém quantity

1. quantity = -1;
2. quantity = 1 000 000;
3. validáció, memória és start viselkedés.

## P1-3 – Decknév útvonal

1. path separatort tartalmazó display name;
2. save/delete;
3. tényleges fájlútvonal vizsgálata.

# 49. Nyitott kérdések

1. Importálható-e a HEAD a korabeli cél-Godot verzióval?
2. Pontosan mely Godot 3 minorverzió szükséges?
3. Hány GUT teszt gyűlik össze ténylegesen?
4. Mely tesztek PASS/FAIL?
5. A SetDefinition_Core ténylegesen pontosan 100 card entryt tartalmaz-e?
6. Minden abilityszöveghez tartozik-e script vagy rule primitive?
7. Van-e definition script nélkül?
8. Van-e script definition nélkül?
9. Mely cardok hardcodedak a typed DSL-en kívül?
10. Reprodukálható-e a persona-consumption hiba?
11. Reprodukálható-e a placement stale-state hiba?
12. Reprodukálható-e a place index hiba?
13. Deckbuilderben blokkolható-e a save invalid decknél?
14. NewGame miért csak minimumot ellenőriz?
15. A Restricted quantity minden load útvonalon érvényesül-e?
16. Ismeretlen card name milyen konkrét hibát ad?
17. A deckfilename path traversal ténylegesen lehetséges-e Godot File API-val?
18. A GameStats alapból aktív-e?
19. Van-e telemetry notice?
20. Milyen asset/shader licencek találhatók?
21. A webes build még működik-e?
22. A public online példány elérhető-e?
23. A framework és app code pontos verziókapcsolata mi?
24. Mely AETERNA effect primitivekhez ad új mintát ez a content?
25. Érdemes-e külön effect-corpus mapping dokumentumot készíteni?

# 50. Következő vizsgálati lépések

## 50.1 Codex nélkül

1. helyi origin és HEAD ellenőrzés;
2. cél-Godot verzió meghatározás;
3. import;
4. GUT collection és teljes futás;
5. 100-card entry count;
6. definition/script parity report;
7. unsupported abilityszöveg audit;
8. deck JSON tampering;
9. persona failure;
10. placement downgrade;
11. place index;
12. deterministic seed trace;
13. trigger ordering trace;
14. telemetry offline test;
15. web/desktop export;
16. asset/shader licencinventár.

## 50.2 Később Codexszel gyorsítható

1. content extractor;
2. ability text ↔ script mapping;
3. opcode/filter inventory;
4. duplicate/shadowing report;
5. AETERNA typed instruction mapping;
6. deck validator property tests;
7. malicious deck corpus;
8. trigger call graph;
9. scene mutation inventory;
10. clean-room content compiler prototype.

# 51. Végső minősítés

- **Alkalmazott effect-DSL érték:** nagyon magas
- **Content authoring érték:** magas
- **Game-specific extension érték:** magas
- **Deckbuilder UX érték:** magas
- **Deck validation authority:** alacsony
- **Rules-engine authority:** nagyon alacsony
- **Determinism/replay:** alacsony
- **Multiplayer/hidden information:** nem megvalósított
- **Teszt/CI érettség:** alacsony
- **Licenc-kompatibilitás közvetlen használathoz:** alacsony
- **Közvetlen dependency:** elutasítandó
- **Clean-room content/effect/deckbuilder inspiráció:** kiemelten ajánlott
- **Legfontosabb AETERNA-tanulság:** a nagy contentkészlet és domain-deckbuilder jól
  építhető deklaratív modellekre, de a runtime authorityt, deckvalidációt és persistence
  trust boundaryt teljesen külön typed C# rétegbe kell helyezni
- **Elemzés státusza:** első teljes source audit elkészült
- **Következő learning cél:** `Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo`

# 52. Változásnapló

## 0.1 – 2026-07-25

- elkészült a `db0/Fragment-Forge` első teljes alkalmazás- és source auditja;
- rögzítésre került a vizsgált commit, a Godot 3.x állapot és az AGPL licenc;
- feldolgozásra került a core és game-specific kódréteg;
- feldolgozásra került a 100 lapos content definition és script szerkezet;
- feldolgozásra került a custom effect opcode és triggerpredicate bővítés;
- feldolgozásra került a Persona rendszer;
- feldolgozásra került az affinity/inspiration/influence deckbuilder;
- feldolgozásra került a JSON deck persistence és trust boundary;
- azonosításra került a hamis `total` és short-deck start kockázat;
- azonosításra került a hiányzó persona runtime kockázata;
- azonosításra került a persona-use sikertelen activation utáni fogyása;
- azonosításra került a stale placement state;
- azonosításra került a place-index off-by-one hiba;
- feldolgozásra került a frame-based rules recomputation;
- feldolgozásra került a GameStats telemetria;
- rögzítésre került a korlátozott teszt- és hiányzó CI-bizonyíték;
- elkészült az AETERNA content compiler, typed effect, DeckValidator és ValidatedDeckArtifact javaslat;
- a következő kijelölt projekt `Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo`.
