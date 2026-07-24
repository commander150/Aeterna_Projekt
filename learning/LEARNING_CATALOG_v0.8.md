# AETERNA – LEARNING PROJECT CATALOG

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.8
- **Dátum:** 2026-07-24
- **Státusz:** egységes, kizárólag verziózott központi dokumentummodellel pontosított munkaváltozat
- **Szerep:** külső referencia-projektek központi nyilvántartása
- **Forráslista:** az aktuális verziózott „AETERNA – LEARNING FORRÁSPROJEKTEK NYILVÁNTARTÁSA” dokumentum
- **Tervezett egyedi elemzések:** `learning/analyses/<projekt-azonosító>.md`

Ez a dokumentum nem AETERNA-szabályforrás és nem engine-specifikáció. A célja annak
követhető rögzítése, hogy mely külső projekteket gyűjtöttük össze, melyeket azonosítottunk
biztosan, milyen területen lehetnek tanulságosak, és milyen mélységű vizsgálat vár még rájuk.

A `learning/sources/` mappa helyi, letöltött forráskódokat tartalmazhat, de Git által
figyelmen kívül hagyott referenciaanyag. A repositoryba elsősorban a katalógus, az elemzések,
az idézett fájlútvonalak, a commit-azonosítók és a levont következtetések kerüljenek.

## Központi dokumentumok verzió- és hivatkozási szabálya

A `learning/` központi nyilvántartási dokumentumai **csak verziózott fájlnéven**
léteznek és frissülnek:

```text
LEARNING_CATALOG_vX.Y.md
sources list_vX.Y.md
ANALYSIS_TEMPLATE_vX.Y.md
ORIGIN_IDENTIFICATION_BACKLOG_vX.Y.md
```

Kötelező működési elvek:

1. Nincs külön verziótlan, `CURRENT` vagy `REPLACEMENT` központi másolat.
2. Módosításkor új verziózott fájl készül; a korábbi verzió történeti snapshot marad.
3. A korábbi verziózott fájlt elfogadás után nem írjuk felül.
4. Egy másik dokumentum nem konkrét fájlnévre vagy verziószámra hivatkozik, hanem a
   dokumentum szerepére, például: **az aktuális verziózott „AETERNA – LEARNING FORRÁSPROJEKTEK NYILVÁNTARTÁSA” dokumentum**.
5. Az aktuális változat az adott dokumentumtípus legmagasabb, elfogadott verziója a
   `learning/` mappában.
6. A projektenkénti fő elemzések ettől eltérően állandó fájlnevet használnak:
   `learning/analyses/<owner>__<repository>.md`. Ezek belső dokumentumverziója frissül.
7. A hivatkozás ezért új katalógus- vagy forráslistaverzió esetén nem igényli a
   projektenkénti elemzések módosítását.

A következő fájlnevek nem részei az aktív modellnek:

```text
LEARNING_CATALOG.md
sources list.md
LEARNING_CATALOG_CURRENT*.md
sources list_REPLACEMENT*.md
```

## 1. Státusz- és prioritásjelölések

### Azonosítási bizonyosság

- **megerősített:** a mappanév és az eredeti repository megbízhatóan összerendelhető;
- **valószínű:** erős egyezés van, de a helyi `.git/config`, README vagy letöltési előzmény még szükséges;
- **bizonytalan:** több azonos nevű projekt létezik, ezért nem szabad találomra repositoryt hozzárendelni.

### Vizsgálati prioritás

- **P0:** közvetlenül hasznos az AETERNA engine, Godot/C# kliens vagy kártyarendszer számára;
- **P1:** fontos architekturális, AI-, adat- vagy multiplayer-tanulságot adhat;
- **P2:** részterülethez, UI-hoz vagy összehasonlításhoz hasznos;
- **P3:** történeti vagy periférikus referencia, csak célzott kérdés esetén vizsgálandó.

### Elemzési állapot

1. `regisztrálva`;
2. `metaadat ellenőrizve`;
3. `forrásstruktúra feltérképezve`;
4. `mélyelemzés folyamatban`;
5. `mélyelemzés lezárva`;
6. `AETERNA-következtetések elfogadva`.


## Külső projektek összehasonlítási szabálya

Minden learning projektet kizárólag az AETERNA aktuális, kanonikus állapotához kell
viszonyítani:

- hivatalos AETERNA szabályforrások;
- aktív AETERNA engine-architektúra;
- aktív contract-specifikáció;
- production C# engine;
- runtime package;
- Godot bridge és klienshatár;
- AETERNA teszt-, determinism- és projection-követelmények.

Külső learning projekteket egymással nem szabad rangsorolni vagy architekturálisan
összehasonlítani. A katalógus prioritása kizárólag azt jelzi, hogy az adott projekt
mennyire hasznos az AETERNA következő feladataihoz.

## 2. Központi nyilvántartási mezők

Minden projekt rekordja legalább a következőket tartalmazza:

- helyi mappanév;
- gyűjtési kör;
- eredeti repository és URL;
- azonosítási bizonyosság;
- projekt típusa;
- fő technológia;
- AETERNA számára várható tanulási terület;
- prioritás;
- elemzési állapot;
- külön elemzési dokumentum útvonala;
- licenc és felhasználási kockázat;
- utolsó ellenőrzés dátuma.

## 3. Már letöltött projektek

> A táblázat elsődleges célja a duplikált ajánlások elkerülése. A „tanulási érték”
> még nem mélyelemzési következtetés, hanem a további vizsgálat iránya.
| # | Helyi mappa | Kör | Repository | Bizonyosság | Típus | Technológia | Várható tanulási érték | Prioritás | Állapot |
|---:|---|:---:|---|---|---|---|---|:---:|---|
| 1 | `rlcard-master` | 1 | [datamllab/rlcard](https://github.com/datamllab/rlcard) | kanonikus aktuális upstream; a helyi forrás cserélendő erre | RL-kártyajáték-környezet | Python | Állapottér, legal action, imperfect information és agent API; minden audit rögzített commiton történjen | **P1** | upstream kijelölve; mélyelemzésre vár |
| 2 | `boardgame.io-main` | 1 | [boardgameio/boardgame.io](https://github.com/boardgameio/boardgame.io) | megerősített | Körökre osztott játékmotor | TypeScript / JavaScript | Authoritative state, turn flow, multiplayer, replay-szerű naplózás | **P1** | metaadat ellenőrizve |
| 3 | `duelyst-main` | 1 | [open-duelyst/duelyst](https://github.com/open-duelyst/duelyst) | megerősített | Teljes online taktikai kártyajáték | JavaScript / CoffeeScript / szerverkomponensek | Nagy projektstruktúra, kliens–szerver felosztás, tartalomkezelés | **P2** | metaadat ellenőrizve |
| 4 | `mage-master` | 1 | [magefree/mage](https://github.com/magefree/mage) | megerősített | Komplex TCG-szabálymotor és kliens | Java | Nagy szabálykészlet, ability- és eseménykezelés, szerveres játék | **P0** | metaadat ellenőrizve |
| 5 | `deckbuilder-framework-main` | 2 | [insideout-andrew/deckbuilder-framework](https://github.com/insideout-andrew/deckbuilder-framework) | valószínű | Godot deckbuilder keretrendszer | Godot / GDScript | Kártyapaklik, húzó- és dobóhalom, deckbuilder-játékmenet | **P1** | eredeti repository megerősítésre vár |
| 6 | `Fragment-Forge-main` | 2 | [db0/Fragment-Forge](https://github.com/db0/Fragment-Forge) | megerősített | Godot kártyajáték | Godot / GDScript | A db0 card framework valós alkalmazása, kártyaszkriptek és UI | **P1** | metaadat ellenőrizve |
| 7 | `Godot4-Fake3D-Card-Game-UI-Demo-main` | 2 | [Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo](https://github.com/Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo) | valószínű | Godot kártya-UI demó | Godot | Ál-3D kéz, kártyamozgatás, vizuális bemutatás | **P1** | több tükör/fork miatt eredet ellenőrzendő |
| 8 | `godot-card-game-framework4` | 2 | [kptmn/godot-card-game-framework4](https://github.com/kptmn/godot-card-game-framework4) | megerősített | külön Godot 4 kártyajáték-framework | Godot / GDScript | Godot 4 rule scripting és scene-ek; külön kezelendő a [linyangqi fork-porttól](https://github.com/linyangqi/godot-card-game-framework-gd4), amely a db0 upstream forkja | **P0** | forráskapcsolatok ellenőrizve |
| 9 | `godot-card-game-framework-main` | 2 | [db0/godot-card-game-framework](https://github.com/db0/godot-card-game-framework) | megerősített | Godot kártyajáték-keretrendszer | Godot / GDScript | Kártyaobjektumok, scriptelhető szabályok, jelenetek és UI | **P0** | metaadat ellenőrizve |
| 10 | `hackstone-main` | 2 | [hackclub/hackstone](https://github.com/hackclub/hackstone) | megerősített | Hearthstone-jellegű kártyajáték | webes technológiák | Egyszerű digitális CCG-folyamat és oktatási megközelítés | **P2** | metaadat ellenőrizve |
| 11 | `Pali-main` | 2 | [rametta/Pali](https://github.com/rametta/Pali) | megerősített | 3D többjátékos Godot TCG | Godot / GDScript | Dedikált szerver, rejtett kéz, 3D asztal és multiplayer kliens | **P0** | README ellenőrizve |
| 12 | `seven-card-game-godot-master` | 2 | [Valyreon/seven-card-game-godot](https://github.com/Valyreon/seven-card-game-godot) | megerősített | Godot kártyajáték | Godot / GDScript | Kis, áttekinthető Godot-kártyajáték felépítése | **P2** | metaadat ellenőrizve |
| 13 | `simple-card-pile-ui-master` | 2 | [insideout-andrew/simple-card-pile-ui](https://github.com/insideout-andrew/simple-card-pile-ui) | megerősített | Kártyahalom- és kéz-UI | Godot / GDScript | Kártyakéz, halmok, animációk; közvetlen vizuális referencia | **P0** | metaadat ellenőrizve |
| 14 | `BabelCDB-master` | 3 | [ProjectIgnis/BabelCDB](https://github.com/ProjectIgnis/BabelCDB) | megerősített | Kártyaadatbázis és lokalizáció | adatfájlok / tooling | Nagy kártyaadatbázis, többnyelvű tartalom, ID-kezelés | **P1** | metaadat ellenőrizve |
| 15 | `CardGameEngine-main` | 3 | azonosításra vár | bizonytalan | Ismeretlen kártyajáték-motor | helyi forrás ellenőrzendő | A pontos repository nélkül nem értékelhető megbízhatóan | **P0** | helyi .git/config vagy README szükséges |
| 16 | `card-game-engine-master` | 3 | azonosításra vár | bizonytalan | Ismeretlen kártyajáték-motor | helyi forrás ellenőrzendő | Több azonos nevű repository létezik | **P0** | helyi .git/config vagy README szükséges |
| 17 | `CardScripts-master` | 3 | [ProjectIgnis/CardScripts](https://github.com/ProjectIgnis/CardScripts) | megerősített | Yu-Gi-Oh kártyaszkript-állomány | Lua | Nagy mennyiségű adatvezérelt kártyaképesség és scriptkonvenció | **P0** | metaadat ellenőrizve |
| 18 | `colyseus-master` | 3 | [colyseus/colyseus](https://github.com/colyseus/colyseus) | megerősített | Authoritative multiplayer framework | TypeScript / Node.js | Szerverállapot, szobák, szinkronizáció és klienskapcsolat | **P1** | metaadat ellenőrizve |
| 19 | `Distribution-master` | 3 | [ProjectIgnis/Distribution](https://github.com/ProjectIgnis/Distribution) | megerősített | Yu-Gi-Oh kliens-adatcsomag | adat- és tartalomcsomag | Adatcsomag-szerkezet, release- és tartalomelosztás | **P2** | repository ellenőrizve |
| 20 | `fable5-hearthstone-clone-game-demo-main` | 3 | [EnginKARATAS/fable5-hearthstone-clone-game-demo](https://github.com/EnginKARATAS/fable5-hearthstone-clone-game-demo) | megerősített | Hearthstone-klón demó | Unity / C# (ellenőrzendő mélység) | Kártyajáték UI, körfolyamat és klienslogika | **P1** | metaadat ellenőrizve |
| 21 | `gym-locm-master` | 3 | [ronaldosvieira/gym-locm](https://github.com/ronaldosvieira/gym-locm) | megerősített | AI/RL kártyajáték-környezet | Python | Legal action, állapotkódolás, agent training és benchmark | **P1** | metaadat ellenőrizve |
| 22 | `HearthClone-master` | 3 | [valószínűleg Fiskell/HearthClone](https://github.com/Fiskell/HearthClone) | bizonytalan | Hearthstone-klón | helyi forrás ellenőrzendő | Több azonos nevű repository miatt az eredet nem biztos | **P1** | helyi .git/config vagy README szükséges |
| 23 | `Hearthstone.gd-main` | 3 | [LunarTides/Hearthstone.gd](https://github.com/LunarTides/Hearthstone.gd) | megerősített | Godot Hearthstone-projekt | Godot / GDScript | Godot-kártyajáték felépítés és Hearthstone-jellegű UI | **P1** | metaadat ellenőrizve |
| 24 | `LorcanaJSON-main` | 3 | [LorcanaJSON/LorcanaJSON](https://github.com/LorcanaJSON/LorcanaJSON) | megerősített | TCG-adatprojekt | JSON / tooling | Kártyaadat-séma, készletek, nyomtatások és publikált adat | **P1** | metaadat ellenőrizve |
| 25 | `mdgachasim-master` | 3 | [Mari6814/mdgachasim](https://github.com/Mari6814/mdgachasim) | megerősített | Kártyahúzás/gacha szimulátor | ellenőrzendő | Valószínűségi húzás és szimuláció; korlátozott engine-relevancia | **P3** | metaadat ellenőrizve |
| 26 | `mighty-engine-main` | 3 | azonosításra vár | bizonytalan | Ismeretlen engine | helyi forrás ellenőrzendő | A mappanév nem azonosít egyértelmű repositoryt | **P2** | helyi .git/config vagy README szükséges |
| 27 | `nakama-master` | 3 | [heroiclabs/nakama](https://github.com/heroiclabs/nakama) | megerősített | Online játékbackend | Go / több kliens-SDK | Authoritative multiplayer, session, matchmaking és storage | **P1** | metaadat ellenőrizve |
| 28 | `node-ygocore-interface-master` | 3 | [ghlin/node-ygocore-interface](https://github.com/ghlin/node-ygocore-interface) | megerősített | YGOCore Node interfész | Node.js / native bridge | Rules engine köré épített nyelvi adapter és folyamatkapcsolat | **P1** | metaadat ellenőrizve |
| 29 | `node-ygocore-master` | 3 | [ghlin/node-ygocore](https://github.com/ghlin/node-ygocore) | megerősített | YGOCore Node wrapper | Node.js / native bridge | Natív szabálymotor integráció, wrapper-határok | **P1** | metaadat ellenőrizve |
| 30 | `open_spiel-master` | 3 | [google-deepmind/open_spiel](https://github.com/google-deepmind/open_spiel) | megerősített | Általános játékelméleti és RL keretrendszer | C++ / Python | Játékmodell, perfect/imperfect information, agentek, benchmarkok | **P0** | metaadat ellenőrizve |
| 31 | `PettingZoo-main` | 3 | [Farama-Foundation/PettingZoo](https://github.com/Farama-Foundation/PettingZoo) | megerősített | Többágenses RL API | Python | Multi-agent környezet-API, turn-based agent interfész | **P1** | metaadat ellenőrizve |
| 32 | `pokerkit-main` | 3 | [uoftcprg/pokerkit](https://github.com/uoftcprg/pokerkit) | megerősített | Kártyajáték-szabálymotor | Python | Állapotgép, akcióvalidáció és determinisztikus kártyajáték-logika | **P1** | metaadat ellenőrizve |
| 33 | `PTCG-Bench-main` | 3 | [zjunet/PTCG-Bench](https://github.com/zjunet/PTCG-Bench) | megerősített | Pokémon TCG AI-benchmark | AI/benchmark tooling | LLM-agentek, tesztesetek és kártyajáték-értékelés | **P1** | metaadat ellenőrizve |
| 34 | `Puzzles-master` | 3 | [ProjectIgnis/Puzzles](https://github.com/ProjectIgnis/Puzzles) | megerősített | Yu-Gi-Oh puzzle-állomány | Lua / adat | Reprodukálható szabályhelyzetek és célzott tesztszcenáriók | **P1** | metaadat ellenőrizve |
| 35 | `rtcg-master` | 3 | [hiasmstudio/RTCG](https://github.com/hiasmstudio/RTCG) | valószínű | Kártyajáték-projekt | ellenőrzendő | A pontos tanulási érték mélyellenőrzésre vár | **P3** | eredeti repository megerősítésre vár |
| 36 | `YGOCore-master` | 3 | [Buttys/YGOCore](https://github.com/Buttys/YGOCore) | valószínű | Yu-Gi-Oh szabálymotor | C/C++ | Komplex szabálymotor, események, script interfész | **P0** | eredeti repository megerősítésre vár |
| 37 | `ygopro-master` | 3 | [Fluorohydride/ygopro](https://github.com/Fluorohydride/ygopro) | valószínű | Yu-Gi-Oh kliens és engine-integráció | C++ / Lua | Rules core, kliens, replay és kártyaszkriptek integrációja | **P0** | eredeti repository megerősítésre vár |
| 38 | `YGOSiM-archive-master` | 3 | [stevoduhhero/YGOSiM-archive](https://github.com/stevoduhhero/YGOSiM-archive) | megerősített | Archivált Yu-Gi-Oh szimulátor | webes technológiák | Történeti online-szimulátor felépítés | **P3** | metaadat ellenőrizve |
| 39 | `yugioh-duel-simulator-main` | 3 | [Nivaldo-Nilngn/yugioh-duel-simulator](https://github.com/Nivaldo-Nilngn/yugioh-duel-simulator) | megerősített | Yu-Gi-Oh szimulátor | ellenőrzendő | Kisebb szimulátorprojekt; megvalósítási minták | **P2** | metaadat ellenőrizve |
| 40 | `Yu-Gi-Oh-Master-Duel-Draw-Simulator-main` | 3 | [struja125/Yu-Gi-Oh-Master-Duel-Draw-Simulator](https://github.com/struja125/Yu-Gi-Oh-Master-Duel-Draw-Simulator) | megerősített | Kezdőkéz/húzás szimulátor | ellenőrzendő | Pakli-valószínűség és húzásszimuláció | **P3** | metaadat ellenőrizve |
| 41 | `yugioh-simulator-main` | 3 | [valószínűleg arthastheking113/yugioh-simulator](https://github.com/arthastheking113/yugioh-simulator) | bizonytalan | Yu-Gi-Oh szimulátor | helyi forrás ellenőrzendő | Több azonos nevű repository létezik | **P2** | helyi .git/config vagy README szükséges |
| 42 | `Durak.Godot-master` | 4 | [ch200c/Durak.Godot](https://github.com/ch200c/Durak.Godot) | megerősített | 3D Godot kártyajáték külön gameplay libraryvel | Godot 4.3 / C# / .NET 8 | Pure C# domain, preflight validáció, unit/functional tesztek, 3D presentation és engine–Godot határ | **P0** | első forráskód-audit elkészült |
| 43 | `godopy-main` | 4 | [godopy/godopy](https://github.com/godopy/godopy) | megerősített | Godot–Python integráció | Python / Godot | Nyelvi bridge és külső Python-integráció; jelenlegi C# irány miatt háttéranyag | **P3** | metaadat ellenőrizve |
| 44 | `godot_rl_agents-main` | 4 | [edbeeching/godot_rl_agents](https://github.com/edbeeching/godot_rl_agents) | megerősített | Godot RL-integráció | Godot / Python | Godot-szimuláció és AI-agent kommunikáció | **P1** | metaadat ellenőrizve |
| 45 | `godot-python-extension-master` | 4 | [maiself/godot-python-extension](https://github.com/maiself/godot-python-extension) | valószínű | Godot Python GDExtension | Python / C++ / Godot | Nyelvi integrációs referencia; production irányhoz nem elsődleges | **P3** | eredeti repository megerősítésre vár |
| 46 | `godot-python-master` | 4 | [touilleMan/godot-python](https://github.com/touilleMan/godot-python) | megerősített | Godot Python nyelvi kötés | Python / C++ / Godot | Történeti Godot nyelvi bridge; háttéranyag | **P3** | metaadat ellenőrizve |
| 47 | `py4godot-master` | 4 | [niklas2902/py4godot](https://github.com/niklas2902/py4godot) | megerősített | Godot Python GDExtension | Python / C++ / Godot | Python-integráció, extension boundary és build pipeline | **P3** | metaadat ellenőrizve |
| 48 | `Godot-CardPileFramework` | 5 | [Ggross98/Godot-CardPileFramework](https://github.com/Ggross98/Godot-CardPileFramework) | megerősített | Godot/C# kártya-UI framework | Godot 4.6.2 / C# / .NET 8 | Kéz-, halom-, drag-and-drop és presentation minták | **P0** | első forráskód-audit elkészült |
| 49 | `Arcomage` | 5 | [DarkPro1337/Arcomage](https://github.com/DarkPro1337/Arcomage) | megerősített, aktív upstream (`mono`) | teljes kétjátékos kártyajáték | Godot 4.7 / C# / .NET 10 | YAML effect DSL, typed AST, ENet multiplayer, lokalizáció és WASM modrendszer | **P0** | első forráskód-audit elkészült |
| 50 | `C# Battle Card Game Framework (CSBCGF)` | 5 | [finkmoritz/csbcgf](https://github.com/finkmoritz/csbcgf) | megerősített upstream; vizsgált HEAD 2023-02-14 | általános C# battle card framework | C# / .NET 7 | action queue, reaction phase, card componentek, statok, serialization és NUnit CI; kizárólag AETERNA authority/contract rendszerhez mérve | **P0** | első forráskód-audit elkészült |
| 51 | `Godot-4-Card-Game-CSharp` | 5 | [TheSchlote/Godot-4-Card-Game-CSharp](https://github.com/TheSchlote/Godot-4-Card-Game-CSharp) | megerősített | Godot/C# oktatási card battle | Godot 4.2.1 / C# | Card UI state machine, targeting és enemy intent | **P0** | első forráskód-audit elkészült; archivált |
| 52 | `card-game-engine` | 5 | [jcbcn/card-game-engine](https://gitlab.com/jcbcn/card-game-engine) | megerősített URL; helyi mappanév ellenőrzendő | .NET kártya- és társasjáték-motor | .NET / C# | Solution, tesztek, benchmarkok, publikus API és CI | **P0** | letöltve; mélyelemzésre vár |
| 53 | `Card Game Engine` | 5 | [DavidCorrect/card-game-engine](https://gitlab.com/DavidCorrect/card-game-engine) | megerősített URL; helyi mappanév ellenőrzendő | Godot-kártyamotor | Godot / GDScript | Zónák, Stack/Exile, rejtett kéz és multiplayer | **P1** | letöltve; mélyelemzésre vár |

### 3.1 Forráslista-egyeztetés

A a forrásnyilvántartás 1.0 változata öt gyűjtési körben **53 projektet** tart nyilván.
Ebből **42 rekordhoz közvetlen URL** szerepel, **11 rekord eredete még megerősítésre vár**.

Kiemelt eltérések:

- az RLCard helyi forrásához a forráslista `mjiang9/_rlcard`, a korábbi katalógus
  `datamllab/rlcard` repositoryt rendelt;
- a Godot 4 framework rekordhoz a forráslista `kptmn/godot-card-game-framework4`,
  a korábbi katalógus `linyangqi/godot-card-game-framework-gd4` repositoryt rendelt;
- mindkét esetben a helyi `.git/config`, README vagy commitazonosító alapján kell dönteni;
- az ötödik gyűjtési kör hat projektje átkerült a letöltött projektek közé;
- a hasonló nevű `CardGameEngine-main`, `card-game-engine-master` és a két új GitLab
  projekt külön rekord marad, amíg az eredetkapcsolat nem bizonyított.

## 4. Újonnan talált, még nem letöltött jelöltek

Ezek a projektek továbbra sem részei a jelenlegi, öt körből álló letöltött listának. Letöltés vagy mélyelemzés előtt
ellenőrizni kell a repository aktuális állapotát, licencét, buildelhetőségét, kódtisztaságát,
valamint azt, hogy a tényleges implementáció megfelel-e a README állításainak.

| Repository | Illeszkedés | Fő tanulási terület | Prioritás | Előzetes állapot | Licenc |
|---|---|---|:---:|---|---|
| [StefanoFiumara/harry-potter-tcg](https://github.com/StefanoFiumara/harry-potter-tcg) | Unity/C# teljes TCG; nem Godot, de szabálymotor-szempontból erős | Automatikus szabálykikényszerítés, AI, deck editor, kártyatípusok, replay/multiplayer terv | **P1** | előzetesen ellenőrizve | ellenőrzendő |
| [sominator/colyseus-2d-multiplayer-card-game-templates](https://github.com/sominator/colyseus-2d-multiplayer-card-game-templates) | Többmotoros kártyajáték-multiplayer sablon | Authoritative Colyseus backend és kliens–szerver szinkronizáció | **P1** | repositorystruktúra mélyellenőrzésre vár | ellenőrzendő |
| [JenardKin/triple-triad-godot](https://github.com/JenardKin/triple-triad-godot) | Godot + C# kártyajáték-jelölt | Kisebb, áttekinthető projekt; grid-alapú kártyaelhelyezés | **P2** | mélyellenőrzésre vár | ellenőrzendő |
| [DapperDino/CCG-Single-Player-Learning](https://github.com/DapperDino/CCG-Single-Player-Learning) | Unity/C# oktatási CCG-projekt | Lépésenkénti oktatási minta; a theliquidfire CCG-sorozat követése | **P2** | előzetesen ellenőrizve | ellenőrzendő |
| [kai63001/wildcard-game](https://github.com/kai63001/wildcard-game) | Godot 3.4 + Nakama multiplayer; nem klasszikus TCG-motor | Godot–Nakama hálózat, szerverindítás és multiplayer flow | **P2** | előzetesen ellenőrizve | ellenőrzendő |
## 5. Különösen fontos első elemzési sorrend

### 5.1 Közvetlen Godot + C# referenciák

1. `Ggross98/Godot-CardPileFramework` – első audit elkészült
2. `TheSchlote/Godot-4-Card-Game-CSharp` – első audit elkészült
3. `ch200c/Durak.Godot` – első audit elkészült
4. `DarkPro1337/Arcomage` – első audit elkészült
5. `finkmoritz/csbcgf` – első audit elkészült
6. `jcbcn/card-game-engine` – következő engine-központú elemzési jelölt

Ezek közül az első kettő elsősorban keretrendszer- és oktatási referencia, az Arcomage pedig
egy teljes, működő alkalmazás. Együtt jól elkülöníthető belőlük:

- a Godot-scene és C#-domain réteg határa;
- a kártya- és halomobjektumok reprezentációja;
- a UI-jelek és rules-logika kapcsolata;
- a mentés/betöltés és adatvezérelt kártyadefiníció;
- a build- és exportstruktúra.

### 5.2 C# szabálymotor és teljes TCG referenciák

1. `jcbcn/card-game-engine`
2. `finkmoritz/csbcgf`
3. `StefanoFiumara/harry-potter-tcg`
4. az egyelőre azonosítatlan helyi `CardGameEngine-main`
5. az egyelőre azonosítatlan helyi `card-game-engine-master`

Ezekből elsősorban a következőket kell vizsgálni:

- authoritative game state;
- legal action és request validation;
- eseményvezérelt szabálymotor;
- ability- és effect-dispatch;
- determinisztika és replay;
- tesztelési stratégia;
- szerializáció és verziózható contractok;
- UI-tól független domainmodell.

### 5.3 Godot/GDScript projektek, amelyek C# mellett is tanulságosak

- `db0/godot-card-game-framework`;
- `linyangqi/godot-card-game-framework-gd4`;
- `db0/Fragment-Forge`;
- `rametta/Pali`;
- `DavidCorrect/card-game-engine`;
- `LunarTides/Hearthstone.gd`.

Ezeket nem kódmásolási, hanem architekturális és UX-referenciaként kell kezelni.

## 6. Minden egyedi mélyelemzés kötelező szempontjai

Minden projekt külön dokumentuma térjen ki legalább az alábbiakra:

1. **Forrás és reprodukálhatóság**
   - repository, branch/tag/commit;
   - elemzés dátuma;
   - buildelhetőség és szükséges környezet;
   - licenc.

2. **Architektúra**
   - domain/rules/UI/network rétegek;
   - authoritative state tulajdonosa;
   - adatáramlás;
   - modulhatárok és függőségi irányok.

3. **Játékszabály-végrehajtás**
   - fázisok és körök;
   - legal action;
   - request validation;
   - state transition;
   - eventek;
   - hidden information;
   - hibakezelés és atomikusság.

4. **Kártya- és ability-rendszer**
   - kártyadefiníció és instance;
   - zónák;
   - költségek és erőforrások;
   - target és selection;
   - trigger, effect, modifier és duration;
   - adatvezérelt vagy kódolt képességek.

5. **Minőségbiztosítás**
   - unit/integration/smoke tesztek;
   - determinisztika;
   - fixture és replay;
   - benchmark;
   - CI és release-folyamat.

6. **AETERNA számára levonható következtetések**
   - közvetlenül átvehető elv;
   - csak inspirációként használható minta;
   - kerülendő megoldás;
   - licenc- vagy biztonsági korlát;
   - konkrét következő feladat.

## 7. Bizonytalan azonosítások feloldása

A következő helyi mappákhoz elsődlegesen a helyi forrásból kell kinyerni az eredeti URL-t:

- `CardGameEngine-main`;
- `card-game-engine-master`;
- `HearthClone-master`;
- `mighty-engine-main`;
- `yugioh-simulator-main`;
- `deckbuilder-framework-main`;
- `Godot4-Fake3D-Card-Game-UI-Demo-main`;
- `godot-python-extension-master`.

Ellenőrzési sorrend:

1. `.git/config` → `remote "origin"` URL;
2. `.git/FETCH_HEAD`;
3. README repository-linkje;
4. package/solution/project metadata;
5. ZIP letöltési előzmény vagy böngésző letöltési lista;
6. csak ezek hiányában név-, fájlstruktúra- és commit-egyezés.

## 8. Tervezett fájlszerkezet

```text
learning/
├── LEARNING_CATALOG_vX.Y.md
├── sources list_vX.Y.md
├── ANALYSIS_TEMPLATE_vX.Y.md
├── ORIGIN_IDENTIFICATION_BACKLOG_vX.Y.md
├── analyses/
│   ├── <owner>__<repository>.md     # állandó fő elemzés, belső verzióval
│   ├── <owner>__<repository>/       # későbbi opcionális részanyagok
│   │   ├── architecture.md
│   │   ├── rules-engine.md
│   │   ├── godot-ui.md
│   │   ├── multiplayer.md
│   │   └── evidence/
│   └── ...
└── sources/                          # helyi, Git által ignorált forráskód
```

Javasolt állandó fő elemzési fájlnév:

```text
learning/analyses/<owner>__<repository>.md
```

Példák:

```text
learning/analyses/ggross98__godot-cardpileframework.md
learning/analyses/darkpro1337__arcomage.md
learning/analyses/magefree__mage.md
```

## 9. Következő dokumentációs lépések

1. A bizonytalan repositoryk helyi azonosítása.
2. A katalógus URL-, licenc- és technológia-auditja.
3. Az első négy Godot/C# projekt gyors szerkezeti előszűrése.
4. A két legerősebb projekt mélyelemzése külön dokumentumban.
5. Az AETERNA számára alkalmazható elvek külön döntési listába gyűjtése.
6. Csak elfogadott következtetés kerüljön át engine- vagy projektdokumentációba.

## 10. Változásnapló

### 0.8 – 2026-07-24

- megszűnt a verziózott és verziótlan központi fájlok párhuzamos kezelése;
- a katalógus, a forráslista, az elemzési sablon és az eredetazonosítási backlog
  kizárólag verziózott fájlnéven marad;
- a `CURRENT` és `REPLACEMENT` másolatok kikerültek az aktív fájlstruktúrából;
- a dokumentumok közötti hivatkozás mostantól logikai dokumentumszerepre mutat,
  nem konkrét fájlnévre vagy verziószámra;
- rögzítésre került, hogy az aktuális változat a legmagasabb elfogadott verzió;
- a projektenkénti elemzések állandó fájlneve és belső verziózása változatlan marad;
- a 0.6–0.7 változatban kipróbált stabil, verziótlan központi fájlmodell felváltásra került.

### 0.7 – 2026-07-24

- elkészült a `finkmoritz/csbcgf` első részletes elemzése;
- az elkészült első elemzések száma ötre frissült;
- rögzítésre került a kötelező összehasonlítási szabály: minden külső projektet
  kizárólag az AETERNA-val hasonlítunk össze;
- a CSBCGF fő tanulási területe action/reaction resolution és component model;
- a következő engine-központú jelölt a `jcbcn/card-game-engine`;
- a forráslista-hivatkozás 1.3 verzióra frissült.

### 0.6 – 2026-07-24

- az RLCard rekord kanonikus forrása `datamllab/rlcard` lett;
- a katalógus minden repositoryhoz stabil upstream URL-t használ;
- a reprodukálhatóságot nem a URL verziózása, hanem az elemzésben rögzített commit SHA biztosítja;
- az aktív katalógus stabil fájlneve a verziózott learning katalógus;
- a verziózott `LEARNING_CATALOG_v0.6.md` változat snapshotként megmarad;
- elkészült a `DarkPro1337/Arcomage` első részletes elemzése;
- az elkészült első elemzések száma négyre frissült;
- a következő teljes elemzési cél a `finkmoritz/csbcgf`;
- létrejött az eredetazonosítási backlog.

### 0.5 – 2026-07-24

- megerősítésre került a helyi `mjiang9/_rlcard` forrás;
- a `datamllab/rlcard` aktuális upstream- és összehasonlítási alapként került rögzítésre;
- a Godot 4 framework rekord `kptmn/godot-card-game-framework4` forrásra pontosult;
- a `linyangqi/godot-card-game-framework-gd4` külön, db0-upstreamből származó forkként került rögzítésre;
- elkészült a `ch200c/Durak.Godot` első részletes elemzése;
- az elkészült első elemzések száma háromra frissült;
- a következő teljes elemzési cél a `DarkPro1337/Arcomage`;
- a forráslista-hivatkozás 1.1 verzióra frissült.

### 0.4 – 2026-07-23

- a katalógus összehangolásra került a a verziózott forráslista 1.0 változatával;
- az ötödik gyűjtési kör hat projektje bekerült a letöltött projektek közé;
- a projektösszesítés 53 letöltött rekordra frissült;
- a már letöltött hat projekt kikerült a „nem letöltött jelöltek” táblából;
- bekerültek az RLCard és Godot 4 framework forráshozzárendelési eltérései;
- rögzítésre került a `card-game-engine` névütközések külön kezelésének elve.


### 0.3 – 2026-07-23

- elkészült a `TheSchlote/Godot-4-Card-Game-CSharp` első projektszintű elemzése;
- a projekt státusza archiváltra frissült;
- rögzítésre került az egyértelmű repository-licenc hiánya;
- az elemzés kiemelte a Card UI state machine, targeting és enemy intent tanulságait;
- bekerültek a signal payload szerződés-eltérések és a saját újraimplementálási elv.

### 0.2 – 2026-07-23

- a félreérthető `projects/` elnevezést `analyses/` váltotta fel;
- minden projekthez megmarad az állandó fő `.md` elemzés;
- a későbbi projektspecifikus almappák csak kiegészítő részanyagokat tartalmaznak;
- az első projektszintű elemzés célfájlja `learning/analyses/ggross98__godot-cardpileframework.md`.

### 0.1 – 2026-07-23

- a 47 helyi projektmappa strukturált nyilvántartásba került;
- bekerült az azonosítási bizonyosság és a prioritási rendszer;
- elkülönült a már letöltött állomány és az új jelöltlista;
- létrejött az egyedi projektdokumentumok tervezett rendszere;
- rögzítésre kerültek a bizonytalan azonosítások;
- bekerült az első C#/Godot és C# szabálymotor kutatási shortlist.
