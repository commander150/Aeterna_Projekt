# AETERNA – DarkPro1337/Arcomage ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.2
- **Dátum:** 2026-07-24
- **Státusz:** előzetes, repository-forrásokra épülő elemzés
- **Fő elemzési fájl:** `learning/analyses/darkpro1337__arcomage.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Vizsgált branch:** `mono`
- **Vizsgált commit:** `d816ada56ecc775a6d794a285e71e7e55d4969b6`
- **Commit üzenete:** `chore: add UID files for Player and TableGameState scripts`
- **Vizsgálati korlát:** helyi build, Godot-import, hálózati futtatás és modteszt ebben a körben nem történt
- **Besorolás:** teljes Godot/C# kétjátékos kártyajáték adatvezérelt effect DSL-lel, ENet multiplayerrel és WASM modrendszerrel
- **Elsődleges AETERNA-érték:** adatvezérelt kártyadefiníciók, effect AST/parser, tartalomcsomagok és hálózati kliens–host minták
- **Fontos megjegyzés:** a repository aktív forrását mindig a `mono` default branch aktuális HEAD-je jelenti; az elemzés reprodukálhatóságát a fenti commit biztosítja

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Repository | `DarkPro1337/Arcomage` |
| Eredeti URL | https://github.com/DarkPro1337/Arcomage |
| Aktív/default branch | `mono` |
| Vizsgált commit | `d816ada56ecc775a6d794a285e71e7e55d4969b6` |
| Repository állapot | nyilvános, nem archivált |
| Motor | Godot 4.7 .NET |
| Target framework | .NET 10 |
| Nyelv | C# |
| Játékmód | kétjátékos; offline AI és ENet multiplayer |
| Kártyaadat | YAML |
| Effect-leírás | saját textuális DSL, Sprache parserrel |
| Modrendszer | `.arcpak`, PCK/YAML/CSV és WASM |
| Lokalizáció | CSV, több nyelv |
| Licenc | MIT |
| Automatizált tesztek | nem találtunk |
| CI | nem találtunk |
| AETERNA-prioritás | P0 – effect DSL és content pipeline; P1 – multiplayer/modrendszer |

# 2. Vezetői összefoglaló

Az Arcomage egy teljes, játszható fan-remake, amely a korábban vizsgált kisebb
frameworköknél jóval több production-közeli területet fed le:

- adatvezérelt kártyapaklik;
- kártyaköltségek, típusok, funkciók és action listák;
- feltételes effectek;
- matematikai és összehasonlító expressionök;
- aggregált cél- és állapotlekérdezések;
- offline AI;
- host–client ENet multiplayer;
- headless indítás;
- többnyelvű lokalizáció;
- csomagolt modok;
- WASM modulok;
- külső asset- és localization pipeline.

A projekt legerősebb AETERNA-tanulsága a kártyahatások adatból történő felépítése.

Példa a YAML-ból:

```yaml
actions:
  - if: self.Quarry < opponent.Quarry
    then:
      - self.Quarry.Gain(2)
    else:
      - self.Quarry.Gain(1)
```

A parser ebből typed C# objektumokat készít:

```text
ConditionalAction
BinaryExpression
VariableExpression
MethodCallAction
```

Ez lényegében egy kis effect DSL és AST. Az AETERNA számára ez sokkal értékesebb,
mint a kártyánkénti C# osztályokat használó oktatási projektek.

A fő korlát:

> Az effect AST közvetlenül egy Godot `Control`-ból származó `Table` objektumot mutál,
> ezért az adatvezérelt réteg ellenére nincs Godot-független authoritative engine.

A CardControl egérkattintáskor közvetlenül végrehajtja a kártya actionjeit a globális
Table objektumon. A Table egyszerre:

- Godot UI;
- játékállapot;
- hálózati host/client kód;
- RNG;
- resource mutation;
- turn flow;
- kéz- és kártyanode-kezelés.

Az AETERNA számára ezért a DSL és content pipeline tanulmányozandó, de az execution
boundaryt teljesen újra kell tervezni.

# 3. Előzetes értékelés

| Szempont | Pontszám | Indok |
|---|:---:|---|
| Godot/C# technológiai illeszkedés | 5/5 | Godot 4.7 és .NET 10 |
| Adatvezérelt kártyarendszer | 5/5 | YAML + typed action AST |
| Effect DSL tanulási érték | 5/5 | parser, expressionök, feltételek, targetek |
| Content/mod pipeline | 5/5 | deck pack, tavern pack, CSV, PCK, WASM |
| Rules-engine elválasztás | 2/5 | gameplay és Godot Table összekötve |
| Multiplayer tanulási érték | 3/5 | ENet, lobby, headless; authority vegyes |
| Determinizmus | 1/5 | Randomize és nincs seed/replay contract |
| Hidden information | 2/5 | face-down UI van, viewer snapshot nincs |
| Tesztelhetőség | 1/5 | külön test projektet nem találtunk |
| Build reprodukálhatóság | 2/5 | build közben hálózatról CSV-t tölt |
| Lokalizáció | 4/5 | több CSV-alapú nyelv és modlokalizáció |
| Licencelési használhatóság | 4/5 | kód MIT; fan-remake asset/IP külön kezelendő |
| Összesített prioritás | **P0** | effect DSL és tartalomcsomag szempontjából kiemelt |

# 4. Repository- és projektstruktúra

A jelenlegi branch fő szerkezete:

```text
src/
├── Arcomage.csproj
├── project.godot
├── Decks/
│   └── MM8.yaml
├── Locales/
├── Scenes/
├── Scripts/
│   ├── Core/
│   │   ├── Global.cs
│   │   ├── Config.cs
│   │   └── ModApi.cs
│   ├── Data/
│   │   ├── Card.cs
│   │   ├── CardActions.cs
│   │   ├── CardActionParser.cs
│   │   ├── CardActionTypeConverter.cs
│   │   └── CardEnums.cs
│   ├── Gameplay/
│   │   ├── Table.cs
│   │   ├── TableGameState.cs
│   │   ├── Player.cs
│   │   └── CardControl.cs
│   ├── Managers/
│   │   ├── DeckManager.cs
│   │   ├── ModManager.cs
│   │   ├── TavernManager.cs
│   │   └── TranslationManager.cs
│   └── UI/
│       └── NetworkSetup.cs
└── ...
```

A solution nem választja külön a gameplay domain libraryt és a Godot klienst. Az összes
C# kód egyetlen `Godot.NET.Sdk` projektbe kerül.

# 5. Build és technológiai alap

Az `Arcomage.csproj`:

- `Godot.NET.Sdk/4.7.0`;
- `net10.0`;
- dynamic loading;
- unsafe blockok engedélyezése;
- Sprache 2.3.1;
- Wasmtime 22.0.0;
- YamlDotNet 16.2.1.

## 5.1 Nem hermetikus build

A build előtt két lokalizációs CSV-fájlt tölt le publikus Google Sheets URL-ről `curl`
segítségével.

Kockázatok:

- offline build hibája;
- külső tartalom időközbeni megváltozása;
- nincs checksum;
- nincs rögzített artifact version;
- a build eredménye ugyanazon commitnál is eltérhet;
- a `curl` rendelkezésre állása platformfüggő;
- külső szolgáltatás kiesése blokkolhatja a buildet.

AETERNA-ban a build csak repositoryban vagy rögzített artifactban tárolt, hash-ellenőrzött
inputot használjon.

## 5.2 README-verzióeltérés

A README Godot 4.7-et és .NET 10-et jelöl követelményként, de a futtatási lépés még egy
Godot 4.6.2 letöltési linkre mutat. A `.csproj` és a `project.godot` alapján a tényleges
cél Godot 4.7.

# 6. Kártyaadat-modell

A `Card` mezői:

- `Id`;
- `Name`;
- `Description`;
- `Type`;
- `Cost`;
- `Pic`;
- `Actions`;
- `Uses`;
- `Features`.

A `Deck`:

- név;
- leírás;
- kártyalista;
- runtime `IsEnabled` jelző.

## 6.1 Erősségek

- stabil string card ID;
- vizuális és szabályi mezők együtt elérhetők;
- action lista kompozíció;
- enumos card type és feature;
- egyszerű YAML authoring;
- több deck betölthető;
- modból is regisztrálható.

## 6.2 Hiányzó production contractok

A vizsgált loaderben nem találtunk:

- schema versiont;
- package ID-t;
- content hash-t;
- duplicate card ID ellenőrzést;
- ismeretlen mező policyt;
- külön definition és localized display data réteget;
- atomikus package activationt;
- dependency és compatibility contractot;
- stabil diagnosztikai kódokat;
- canonical exportot;
- master–runtime parity proofot.

A loader exception esetén logol és `null` értéket ad. Ez használható felhasználói modnál,
de canonical runtime package-nél túl gyenge.

# 7. Effect DSL és AST

## 7.1 Action típusok

A jelenlegi AST fő elemei:

```text
ActionBase
├── MethodCallAction
└── ConditionalAction

Expression
├── NumberExpression
├── VariableExpression
├── AggregateExpression
└── BinaryExpression
```

A MethodCallAction tartalmazza:

- target;
- opcionális resource;
- effect method;
- expression argumentumok.

Támogatott effectek a vizsgált kódban:

- Gain;
- Lose;
- Set;
- Swap;
- Damage.

## 7.2 Targetek és aggregátumok

A rendszer kezel:

- Self;
- Opponent;
- All;
- AllExceptSelf;
- LowestWall;
- HighestWall;
- LowestTower;
- HighestTower;
- valamint több highest/lowest resource aggregátumot.

## 7.3 Expressionök

Támogatott műveletek:

- összeadás;
- kivonás;
- szorzás;
- osztás;
- egyenlőség és nem egyenlőség;
- kisebb/nagyobb;
- kisebb vagy egyenlő;
- nagyobb vagy egyenlő;
- zárójelek;
- target.resource változók;
- aggregált változók.

Ez már valódi, kis méretű, deklaratív effect nyelv.

## 7.4 Parser

A Sprache parser:

- typed enum tokenekre fordítja a szöveget;
- rekurzív expression parsert használ;
- parser failure eredményt készít ismeretlen target/resource/effect esetén;
- method call és conditional action AST-t állít elő.

## 7.5 Közvetlen AETERNA-tanulság

Az AETERNA effect pipeline-ja hasonlóan bontható:

```text
forrásadat
→ parser / compiler
→ validated typed AST
→ immutable runtime instruction
→ deterministic evaluator
→ state transition
→ typed engine events
```

Az Arcomage közvetlenül az első négy lépéshez ad jó inspirációt.

# 8. Effect execution

Az ActionBase ezt a szerződést használja:

```text
Execute(Table gameState)
```

A MethodCallAction:

1. lekéri az aktuális játékost;
2. feloldja a targetet;
3. kiértékeli az expressionöket;
4. közvetlenül meghívja a Table `Damage`, `GainValue` vagy `SetValue` metódusát.

## 8.1 Erősség

- a YAML-ból létrejövő AST valóban végrehajtható;
- az általános effectek nem kártyánkénti C# osztályok;
- a conditional és expression composable;
- új tartalom programkód nélkül készíthető.

## 8.2 Fő architekturális probléma

A runtime context egy Godot `Control`:

```text
Table : Control
```

A `TableGameState` partial osztály közvetlenül Godot `Mathf` függőséget is használ.
Ezért:

- az evaluator nem headless domain library;
- a Table egyszerre UI és state;
- a tesztelés Godot nélkül nehéz;
- az effect futása közvetlen mutable object mutation;
- nincs transition transaction;
- nincs event list;
- nincs rollback;
- nincs state version;
- nincs request ID;
- nincs viewer projection.

AETERNA-ban az AST evaluator kizárólag Godot-független `EngineState` és kontrollált
`TransitionContext` objektumot kaphat.

# 9. Kártyakijátszás és UI

A `CardControl`:

- kártyát ID, index vagy véletlen választás alapján tölt;
- vizuális adatot közvetlenül a DeckManagerből olvas;
- külön face-down állapotot kezel;
- hoverkor csak vizuálisan jelzi a `Usable` állapotot;
- bal kattintáskor végrehajtja az összes CardActiont a `Global.Table` objektumon;
- jobb kattintásos discard még TODO.

## 9.1 Kiemelt kockázat

A vizsgált `OnGuiInput` útvonal:

- nem ellenőrzi a `Usable` jelzőt;
- nem ellenőrzi közvetlenül a costot;
- nem küld authoritative requestet;
- nem vár host-visszaigazolásra;
- közvetlenül mutálja a Table állapotát.

Lehetséges, hogy a scene vagy más kód korábban tiltja az inputot, de a bemutatott
CardControl önmagában nem garantálja a szabályos kijátszást.

## 9.2 AETERNA-helyettesítés

```text
CardView click
→ PlayCardRequest(card_instance_id, state_version)
→ engine preflight
→ payment validation
→ target/selection validation
→ atomic transition
→ EngineResult
→ snapshot + events
→ UI animation
```

# 10. Table és game state

A Table több mint 500 soros Godot `Control`, amely kezeli:

- UI node-hivatkozásokat;
- player dictionaryt;
- turn playert;
- RNG-t;
- offline és multiplayer állapotot;
- initial hands;
- erőforrás-beáramlást;
- deck visibilityt;
- hálózati peer eventeket;
- kártyanode-ok létrehozását;
- game stat panelt;
- win/lose folyamatot.

A `TableGameState` partial rész:

- resource get/set/gain;
- target resolution;
- damage;
- wall és tower kezelés.

## 10.1 Pozitívum

A 2026-os refaktor külön `Player` és `TableGameState` fájlba emelt részeket, így a
repository láthatóan a modularitás irányába halad.

## 10.2 Korlát

A partial fájlok nem hoznak valódi assembly- vagy dependency-határt. A domain továbbra
is Godot Control és autoload környezetben marad.

# 11. Játékosállapot

A Player tartalmaz:

- stabil `long` ID;
- név;
- host/AI/ready státusz;
- play-again, discard és draw jelzők;
- tower/wall;
- három generátor;
- három erőforrás.

A kezdőértékeket globális Config singletonból olvassa property initializerben.

Kockázatok:

- a domain konstrukció rejtett globális konfigurációtól függ;
- nincs immutable setup input;
- nincs state version;
- publikus set propertyk miatt invariánsok könnyen megkerülhetők;
- network, lobby és gameplay mezők egy osztályban keverednek.

# 12. Determinizmus

Véletlen pontok:

- Table `_rng.Randomize()`;
- kezdő játékos;
- kezdő kéz;
- új kártyaválasztás;
- CardControl fallback-véletlen.

Nem találtunk:

- seed contractot;
- RNG state exportot;
- random-decision eventet;
- replayt;
- state hash-t;
- deterministic fixture-t.

Multiplayerben a host generálhatja a kezdő adatokat és RPC-vel terjeszti, ami jobb,
mint a független kliens RNG. Ugyanakkor a teljes authoritative transition és RNG
szerződés nem különül el egy engine sessionben.

# 13. Multiplayer

A NetworkSetup:

- ENet szervert és klienst hoz létre;
- fix 8070 portot használ;
- két játékosra korlátoz;
- lobbyt és ready státuszt kezel;
- hostot az 1-es peer ID alapján jelöli;
- headless kijelzőn automatikus csatlakozási útvonalat tartalmaz;
- RPC-kkel indítja a játékot és szinkronizál lobbyadatokat.

A Table:

- szerveroldalon kezeli a peer kapcsolatokat;
- szerver választ kezdőjátékost és kezeket;
- RPC-vel példányosít kezdő kezeket;
- face-down módot használ az ellenfél lapjaihoz.

## 13.1 Pozitívum

- van valódi hálózati példa;
- ENet;
- host/client elkülönítés;
- headless útvonal;
- kézvizualizáció;
- lobby és ready flow.

## 13.2 Kockázatok

- több RPC `AnyPeer`;
- nincs request DTO;
- nincs state version;
- nincs stale-request guard;
- nincs idempotency;
- nincs reconnect;
- nincs snapshot sync;
- nincs auditálható action log;
- nincs anti-cheat validációs réteg;
- nincs viewer-specifikus authoritative projection;
- a UI és game state ugyanabban a node-ban van;
- a kártya action execution útvonalának hálózati authorityja külön mélyauditra szorul.

# 14. Hidden information

A kliens face-down módot használ és a helyi játékosnak megfelelően fordítja a lapokat.
Ez jó presentation-elv.

Azonban:

- a kliens scene fában mindkét kéz kártya-ID-i jelen lehetnek;
- nincs külön redacted snapshot;
- nincs opaque hidden-card instance;
- nincs viewer-specifikus serialization;
- nincs server-only card definition/instance mapping.

Az AETERNA multiplayerben az ellenfél kezéről csak count és opaque projection juthat
a klienshez.

# 15. DeckManager és YAML betöltés

A DeckManager:

- `res://Decks/` könyvtárat olvas;
- YAML/YML fájlokat támogat;
- YamlDotNet deserializert használ;
- saját ActionTypeConvertert kapcsol be;
- file-ból és textből is tölt;
- deckeket enabled státusszal tárol;
- exception esetén logol és nullt ad.

## 15.1 Erősség

- egyszerű authoring;
- modból is újrahasználható;
- action DSL integrált;
- több deck kezelhető;
- a tartalom és a C# kód elválik.

## 15.2 Kockázat

- nincs schema validation;
- nincs duplicate ID check;
- nincs package-level atomicity;
- egy hibás deck csak null lesz;
- nincs stabil diagnostic code;
- a loader Godot FileAccesshez kötött;
- minden deck automatikusan enabled;
- deck enable/disable UI TODO.

# 16. Modrendszer

A ModManager:

- rekurzívan keres `.arcpak` fájlokat;
- ZIP-ként nyitja őket;
- `metadata.yaml` fájlt vár;
- PCK resource packot tölthet;
- YAML deck vagy tavern packot regisztrál;
- CSV lokalizációt adhat hozzá;
- WASM entry pointot futtathat Wasmtime-tal;
- `init`, `process`, `exit` funkciókat kezel;
- host callbacket ad logoláshoz.

## 16.1 Tanulási érték

Ez az egyik legösszetettebb vizsgált content-extension rendszer:

```text
.arcpak
├── metadata.yaml
├── deck/tavern YAML
├── localization CSV
├── Godot PCK
└── WASM module
```

## 16.2 Biztonsági és lifecycle kockázatok

- nincs aláírás;
- nincs package hash;
- nincs trust policy;
- nincs dependency graph;
- nincs API/version compatibility;
- PCK betöltés módosíthatja a resource namespace-t;
- WASM modul minden frame-ben `process` hívást kaphat;
- nincs látható instruction/fuel limit;
- nincs memória- vagy időkvóta;
- nincs canonical mod manifest validation;
- nincs unload/rollback teljes lifecycle;
- az `IsEnabled` mező és a tényleges disable működés külön vizsgálandó.

Az AETERNA-ban modding csak a production engine és runtime package stabilizálása után
jöhet szóba.

# 17. Lokalizáció

A projekt több nyelvet támogat. A localization:

- beépített CSV-k;
- build közben letöltött CSV-k;
- modból betöltött CSV;
- Godot TranslationServer.

Hasznos elv:

- card ID és display text különválhat;
- mod saját lokalizációt adhat;
- több nyelv egy adatpipeline-ból kezelhető.

Kockázat:

- a build inputja külső és változó;
- nincs localization schema/version;
- nincs hiányzó kulcs audit;
- nincs canonical runtime package-be zárt lokalizációs proof.

# 18. Tesztek és CI

A repository kódkeresésében nem találtunk:

- xUnit/NUnit/MSTest test projektet;
- Godot unit-test frameworköt;
- `.github/workflows` build/test workflowt;
- deterministic scenario fixture-t;
- multiplayer integration testet;
- parser regression testet;
- mod security testet.

Ez negatív távoli keresési eredmény; helyi teljes repository-audit szükséges.

A parser, evaluator, network és modrendszer összetettsége miatt az automatizált tesztek
hiánya jelentős kockázat.

# 19. Licenc és jogi megjegyzés

A repository kódja MIT licencű:

```text
Copyright (c) 2020–2026 Artem Chernykh
```

A kód használható és módosítható a licencfeltételek betartásával.

Külön kezelendő:

- a Might and Magic / Arcomage fan-remake státusz;
- eredeti játékhoz kapcsolódó nevek;
- grafikai és hangassetek;
- külső fontok;
- modokban lévő assetek;
- itch.io/GameJolt disztribúció tartalma.

A repository MIT kódlicence nem bizonyítja automatikusan minden asset és szellemi
tulajdon átvételi jogát.

# 20. Erősségek

1. Aktív, modern Godot 4.7/.NET 10 projekt.
2. Teljes játék, nem csak tutorial.
3. Stabil card ID.
4. YAML content authoring.
5. Typed action AST.
6. Saját effect DSL.
7. Feltételes és matematikai expressionök.
8. Aggregált state queryk.
9. Nem szükséges kártyánkénti C# osztály.
10. Több deck.
11. Offline és online mód.
12. ENet lobby és headless útvonal.
13. Többnyelvű lokalizáció.
14. Modcsomagok.
15. WASM extension.
16. MIT licenc.
17. Látható folyamatos refaktor és fejlesztés.

# 21. Gyengeségek és kockázatok

1. Egyetlen Godot assembly.
2. Nincs pure C# authoritative engine.
3. Table egyszerre UI, state, network és RNG.
4. Global singletonok.
5. CardControl közvetlen action execution.
6. A bemutatott click útvonal nem ellenőrzi a `Usable` értéket.
7. Cost validation nem látható a click execution előtt.
8. Nincs request/response contract.
9. Nincs state version.
10. Nincs event log vagy replay.
11. Nincs deterministic RNG.
12. Nincs viewer projection.
13. Keveredő lobby és gameplay Player state.
14. Publikus mutable propertyk.
15. YAML schema és package version hiánya.
16. Duplicate ID validation hiánya.
17. Stable diagnostic code hiánya.
18. Loader hiba esetén null.
19. Nem hermetikus localization build.
20. Tesztek hiánya.
21. CI hiánya.
22. AnyPeer RPC-k külön auditot igényelnek.
23. Reconnect és resync hiánya.
24. Modcsomag aláírás és trust policy hiánya.
25. WASM kvóta/fuel policy nem látható.
26. PCK resource namespace kockázat.
27. Fan-remake asset/IP kockázat.

# 22. AETERNA számára közvetlenül átvehető elvek

## 22.1 Typed effect AST

Az effectek legyenek adatvezéreltek és typed runtime modellre fordítva.

## 22.2 Parser és compiler elkülönítése

```text
source syntax
→ parse result
→ validation
→ normalized AST
→ compiled runtime instruction
```

A parser soha ne legyen egyben runtime executor.

## 22.3 Általános effect primitives

- Gain;
- Lose;
- Set;
- Swap;
- Damage;
- Conditional;
- Arithmetic expression;
- State query.

Az AETERNA saját fogalmaihoz igazítva ez jó instruction-készlet-alap.

## 22.4 Stabil ID és lokalizáció

A card ID legyen független a lokalizált névtől és leírástól.

## 22.5 Content pack és extension határ

A deck/tavern/mod pack modell inspiráció, de AETERNA-ban:

- schema version;
- package ID;
- checksum;
- dependency;
- signature/trust;
- atomic activation;
- stable diagnostics

kötelező.

# 23. Amit nem szabad átvenni

1. `Execute(Table)` effect contract.
2. Godot Control mint authoritative state.
3. Global.Table.
4. UI-clickből közvetlen state mutation.
5. Randomize seed nélkül.
6. Kliens scene-ben tárolt hidden hand identity.
7. AnyPeer RPC authority validáció nélkül.
8. Build közbeni változó internetes input.
9. Null-visszatérés canonical package hiba esetén.
10. Mod PCK/WASM trust policy nélkül.
11. Egyetlen nagy Table node mint engine session.
12. Publikus set propertyk kontrollált transition helyett.

# 24. Javasolt AETERNA effect-architektúra

```text
Aeterna.Content.Source
    XLSX / JSON / authoring format
          │
          ▼
Aeterna.Content.Compiler
    schema validation
    ID validation
    effect parser
    normalized typed AST
    stable diagnostics
          │
          ▼
Aeterna.RuntimePackage
    immutable definitions
    compiled instructions
    content hash
          │
          ▼
Aeterna.Engine
    EngineSession
    MatchState
    RequestValidator
    CostPayment
    SelectionContract
    EffectEvaluator
    TransitionBuilder
    EngineEvent
    ProjectionService
          │
          ▼
Godot Bridge
    request DTO
    snapshot
    event animation
```

# 25. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | Typed effect AST fenntartása/bővítése | Content/Engine | P0 |
| 2 | Parser és evaluator külön assemblyben | Engine | P0 |
| 3 | Godot-független EvaluationContext | Engine | P0 |
| 4 | Immutable compiled instructionök | Runtime | P0 |
| 5 | Schema és package version | Runtime | P0 |
| 6 | Duplicate ID és unknown-token diagnosztika | Tooling | P0 |
| 7 | Stable diagnostic code minden parse/validation hibához | Tooling | P0 |
| 8 | Atomic package load/activate | Runtime | P0 |
| 9 | Parser unit-test corpus | Tests | P0 |
| 10 | Effect scenario fixture | Tests | P0 |
| 11 | Seedelt RNG és random decision event | Engine | P0 |
| 12 | EngineSession request boundary | Engine | P0 |
| 13 | Viewer-specific hidden projection | Engine | P0 |
| 14 | Multiplayer state version és stale guard | Network | P0 |
| 15 | YAML-szerű authoring csak fordítási forrásként | Tooling | P1 |
| 16 | Lokalizáció külön package-rétegben | Runtime | P1 |
| 17 | Modding elhalasztása a stabil engine utánra | Projekt | P1 |
| 18 | Későbbi mod trust/signature policy | Runtime | P2 |
| 19 | Build inputok repositoryban vagy hash-elt artifactban | Build | P0 |
| 20 | Fan-remake assetek helyett saját AETERNA assetek | Projekt | P0 |

# 26. Bizonyítékjegyzék

| ID | Állítás | Forrásfájl | Sorok |
|---|---|---|---|
| E-001 | Godot 4.7 és .NET 10 | `README.md` | 5–7, 66–75 |
| E-002 | Két játékos, resource/generator modell | `README.md` | 20–44 |
| E-003 | Godot SDK, NuGet dependencyk | `src/Arcomage.csproj` | 5–20 |
| E-004 | Build közbeni CSV-letöltés | `src/Arcomage.csproj` | 11–24 |
| E-005 | Godot 4.7 és autoloadok | `src/project.godot` | 19–38 |
| E-006 | Card és Deck adatmodell | `Card.cs` | 13–31 |
| E-007 | ActionBase és MethodCallAction | `CardActions.cs` | 11–75 |
| E-008 | ConditionalAction | `CardActions.cs` | 101–116 |
| E-009 | Expression hierarchy | `CardActions.cs` | 119–186 |
| E-010 | Aggregate state queryk | `CardActions.cs` | 189–224+ |
| E-011 | Sprache parser és expression grammar | `CardActionParser.cs` | 11–124 |
| E-012 | Method call és conditional parsing | `CardActionParser.cs` | 131–234 |
| E-013 | YAML deck és action syntax | `MM8.yaml` | fájl eleje és teljes kártyakészlet |
| E-014 | DeckManager YAML betöltés | `DeckManager.cs` | 21–105 |
| E-015 | YAML text loader | `DeckManager.cs` | 108–138 |
| E-016 | Player mutable state | `Player.cs` | 9–31 |
| E-017 | Table resource mutation | `TableGameState.cs` | 14–102 |
| E-018 | Target resolution és damage | `TableGameState.cs` | 104–131 |
| E-019 | Table UI/state/network/RNG összefonódás | `Table.cs` | teljes fájl |
| E-020 | Kezdő kéz host RNG és RPC | `Table.cs` | fájl első fele |
| E-021 | CardControl kártyaadat betöltés | `CardControl.cs` | 48–110 |
| E-022 | Face-down presentation | `CardControl.cs` | 113–124 |
| E-023 | Közvetlen click action execution | `CardControl.cs` | 152–170 |
| E-024 | ENet lobby és headless útvonal | `NetworkSetup.cs` | 14–75, 121–150 |
| E-025 | AnyPeer RPC-k | `NetworkSetup.cs` | fájl második fele |
| E-026 | Mod API deck/tavern regisztráció | `ModApi.cs` | 10–28 |
| E-027 | Arcpak és metadata | `ModManager.cs` | 22–100 |
| E-028 | PCK/YAML/CSV mod resource | `ModManager.cs` | 102–179 |
| E-029 | WASM modulbetöltés | `ModManager.cs` | fájl második fele |
| E-030 | MIT licenc | `LICENSE` | 5–24 |

# 27. Nyitott kérdések

1. A vizsgált commit buildelhető-e Godot 4.7/.NET 10 környezetben?
2. A README 4.6.2 futtatási linkje okoz-e felhasználói hibát?
3. A build működik-e internet és curl nélkül?
4. Van-e duplicate card ID a teljes deckkészletben?
5. Minden YAML action parse-olható-e?
6. A parser precedence minden kombinációnál helyes-e?
7. A conditional YAML converter hogyan ad stabil hibapozíciót?
8. A CardControl `Usable=false` mellett valóban végrehajtja-e az actiont?
9. Hol történik a cost levonás és végső legal-play ellenőrzés?
10. Multiplayerben melyik peer hajtja végre az effectet?
11. A kliensek állapota hogyan kerül teljesen szinkronba?
12. Lehetséges-e nem-host klienssel tiltott RPC vagy action?
13. Milyen reconnect/resync viselkedés van?
14. A hidden kéz kártya-ID-je eljut-e az ellenfél kliensére?
15. Van-e mod API compatibility version?
16. A Wasmtime store használ fuel vagy epoch interruption limitet?
17. A PCK mod felülírhat-e canonical resource-t?
18. A modok digitális aláírás nélkül hogyan megbízhatók?
19. Az assetek licence külön igazolható-e?
20. Milyen parser/evaluator teszteket lehet gyorsan kinyerni?

# 28. Következő vizsgálati lépések

## Codex nélkül elvégezhető

1. Helyi origin és `mono` HEAD rögzítése.
2. Godot 4.7/.NET 10 build.
3. Offline buildpróba a localization target miatt.
4. Teljes YAML parse audit.
5. Duplicate ID audit.
6. Effect syntax corpus export.
7. Cost és `Usable` útvonal kézi ellenőrzése.
8. Offline game smoke.
9. Host/client kétpéldányos smoke.
10. Hidden-information hálózati vizsgálat.
11. AnyPeer RPC lista.
12. Mod manifest és archive audit.
13. WASM limit és host API audit.
14. Asset- és licencinventár.

## Később Codexszel gyorsítható

1. teljes call graph;
2. Table felelősségi bontás;
3. RPC authority és sender-validation audit;
4. effect parser test generation;
5. összes YAML action AST export;
6. mutation path és state-diff audit;
7. deterministic evaluator proof;
8. mod security static audit;
9. AETERNA effect modellel gépi összevetés;
10. typed compiler proof-of-concept.

# 29. Végső előzetes minősítés

- **Tanulási érték:** nagyon magas
- **Legértékesebb terület:** effect DSL, typed AST, YAML content és modcsomagok
- **Godot/C# illeszkedés:** közvetlen
- **Rules-engine elválasztás:** gyenge
- **Multiplayer érték:** közepes, külön authority audit szükséges
- **Determinizmus:** gyenge
- **Tesztelési érettség:** alacsony
- **Licenc:** MIT kód; asset/IP külön kezelendő
- **Production engine-alapként:** nem alkalmas
- **AETERNA-adatpipeline inspirációként:** kiemelten alkalmas
- **Mélyelemzés folytatása:** igen
- **Elsődleges következő cél:** effect DSL corpus, parser-validáció és multiplayer authority audit

# 30. Változásnapló

## 0.1 – 2026-07-24

- elkészült az első repository-forrásokra épülő Arcomage-elemzés;
- vizsgálat készült a YAML card/deck modellről;
- feldolgozásra került az effect AST és Sprache parser;
- elkülönítésre kerültek az adatvezérelt rendszer erősségei és a Godot-bound execution hibái;
- vizsgálat készült az ENet multiplayer alapról;
- feldolgozásra került az arcpak/PCK/YAML/CSV/WASM modrendszer;
- rögzítésre kerültek a determinisztikai, hidden-information és authority kockázatok;
- elkészült az AETERNA effect compiler és runtime package javaslatlistája.

## Hivatkozási modell javítása – 2026-07-24

- a kapcsolódó katalógus hivatkozása mostantól: az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum;
- az elemzés nem tartalmaz konkrét katalógusfájlnevet vagy katalógusverziót;
- új központi katalógusverzió miatt ezt a projektdokumentumot nem kell módosítani;
- a projekt vizsgált állapotának reprodukálhatóságát továbbra is a saját branch/tag,
  commit SHA és vizsgálati dátum biztosítja;
- a korábbi verziótlan központi fájlmodell felváltásra került.
