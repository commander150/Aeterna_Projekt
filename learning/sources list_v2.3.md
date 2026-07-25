# AETERNA – LEARNING FORRÁSPROJEKTEK NYILVÁNTARTÁSA

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 2.3
- **Dátum:** 2026-07-25
- **Státusz:** kizárólag verziózott központi dokumentummodellel és tizennégy AETERNA-központú elemzéssel pontosított munkaváltozat
- **Szerep:** a `learning/sources/` alatt tárolt vagy korábban letöltött külső projektek eredet-nyilvántartása
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Kapcsolódó elemzések:** `learning/analyses/`
- **A lista nem minősül AETERNA-szabályforrásnak vagy engedélynek kód átvételére.**

## 1. A dokumentum célja

Ez a nyilvántartás azt rögzíti, hogy milyen külső programok és repositoryk kerültek
összegyűjtésre, melyik gyűjtési körben jelentek meg, és mennyire biztos az eredeti
forrásuk azonosítása.

A fájl elsődleges szerepei:

- a duplikált letöltések és ajánlások elkerülése;
- a helyi forrásmappa és az eredeti repository későbbi összerendelése;
- a projektenkénti elemzések kiinduló forrásának megőrzése;
- a bizonytalan vagy többértelmű eredetű mappák elkülönítése;
- a későbbi commit-, verzió- és licencellenőrzés előkészítése.

## 2. Összesítés

| Mutató | Érték |
|---|---:|
| Gyűjtési körök száma | 5 |
| Nyilvántartott projektek száma | 53 |
| Közvetlenül rögzített forrás-URL | 42 |
| Még megerősítendő vagy ismeretlen eredet | 11 |
| Elkészült első projektszintű elemzés | 14 |

## 3. Azonosítási állapotok

- **forrás rögzítve:** a jelenlegi listában konkrét URL szerepel; ez még nem bizonyítja,
  hogy a helyi mappa pontosan abból a repositoryból és abból a commitból származik;
- **azonosításra vár:** nincs közvetlenül rögzített URL, ezért helyi `.git/config`,
  README, archive-metaadat vagy letöltési előzmény szükséges;
- **katalógusjelölt:** korábbi kutatás alapján van valószínű repository, de azt nem szabad
  megerősített forrásként kezelni a helyi mappával való egyeztetés előtt.

## 3.1 Dokumentumhivatkozási szabály

Ez a forrásnyilvántartás csak verziózott fájlnéven létezik:

```text
sources list_vX.Y.md
```

- Nincs külön `sources list.md` vagy `sources list_REPLACEMENT*.md` aktív másolat.
- Frissítéskor új verzió készül, a korábbi elfogadott változat történeti snapshot.
- A kapcsolódó dokumentumokra nem konkrét fájlnévvel hivatkozunk.
- A katalógus hivatkozási formája: **az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum**.
- Az aktuális változat a `learning/` mappában található legmagasabb elfogadott verzió.

## 4. Forrásprojektek gyűjtési körönként

### 1. gyűjtési kör
| # | Rögzített név / helyi mappanév | Forrás | Állapot | Megjegyzés |
|---:|---|---|---|---|
| 1 | `RLCard: A Toolkit for Reinforcement Learning in Card Games` | [aktuális upstream](https://github.com/datamllab/rlcard) | forrás rögzítve | A helyi letöltés erre az upstream repositoryra cserélendő. A hivatkozás mindig a default `master` ág aktuális állapotára mutat; minden elemzés külön rögzíti a ténylegesen vizsgált commitot. A korábbi `mjiang9/_rlcard` csak történeti snapshotként marad megjegyzésben. |
| 2 | `boardgame.io` | [forrás](https://github.com/boardgameio/boardgame.io) | forrás rögzítve | — |
| 3 | `duelyst` | [forrás](https://github.com/open-duelyst/duelyst) | forrás rögzítve | — |
| 4 | `mage-master` | — | azonosításra vár | Katalógusjelölt: https://github.com/magefree/mage — a helyi mappával még egyeztetendő. |

### 2. gyűjtési kör
| # | Rögzített név / helyi mappanév | Forrás | Állapot | Megjegyzés |
|---:|---|---|---|---|
| 5 | `deckbuilder-framework` | [forrás](https://github.com/insideout-andrew/deckbuilder-framework) | forrás rögzítve | Első teljes source audit elkészült. Vizsgált commit: `41199fc02c3c9abaae1505737bd9c9080254fe15`; Godot 4.3 / GDScript / MIT. A projekt CardData–Card–Deck presentation és interaction framework, nem kész deck editor. Hasznos deckszintű signal, kézlegyező, reparent animáció és drag/reorder referencia; scene child order authority, stable ID, state version, hidden projection, determinism és CI/test proof hiányzik. |
| 6 | `Fragment-Forge` | [forrás](https://github.com/db0/Fragment-Forge) | forrás rögzítve | Első teljes application/content/deckbuilder source audit elkészült. Vizsgált commit: `759100774d46fb1a30fb08f2e42947e48af90c40`; Godot 3.x / GDScript / AGPL-3.0. 100 lapos content, dictionary effectrendszer, custom opcode/predicate, Persona és affinity/inspiration deckbuilder. Scene-node authority, nem verziózott JSON deck, hiányos startvalidáció, persona-use és placement/index hibák; közvetlen integráció elutasítva. |
| 7 | `Godot4-Fake3D-Card-Game-UI-Demo-main` | [forrás](https://github.com/Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo) | forrás rögzítve | Első teljes provenance/presentation/shader source audit elkészült. Vizsgált commit: `14c07f3983b6c22d9d8747dc3cbb9e3a870c895f`; Godot 4.5 / GDScript / GPL-3.0. Kiemelt fake-3D, front/back, shadow, flash, dissolve, íves kéz, box select és multi-card drag referencia. UI/model/rules összefonódás, kozmetikai shuffle, lock/state/rule hibák, stable ID/version/replay/multiplayer hiány. Assetek CC0; alap perspective shader MIT fejlécű; közvetlen repository-integráció elutasítva. |
| 8 | `godot-card-game-framework4` | [forrás](https://github.com/kptmn/godot-card-game-framework4) | forrás rögzítve | Első teljes source audit elkészült. Vizsgált commit: `18c4bb376304ac57ceb1b76bff3046b226bc054f`; Godot 4.2, CI Godot 4.2.1. Külön repository, de implementációsan a `db0/godot-card-game-framework` 2.2-es rendszerének Godot 4 konverziója. Nyitott ScriptingEngine/Card portkockázatok és nem bizonyított PASS workflow-státusz. Licenc: AGPL-3.0; közvetlen integráció elutasítva. |
| 9 | `godot-card-game-framework` | [aktuális upstream](https://github.com/db0/godot-card-game-framework) | forrás rögzítve | Első teljes source audit elkészült. Vizsgált commit: `f3ca9afd9705ff895839253fad208360d2f45146`; framework 2.2; Godot 3.4.x/GDScript; dictionary ScriptingEngine, Card/Hand/Pile/DeckBuilder presentation, GUT CI és seedelt RNG. Licenc: AGPL-3.0 Steamworks addendummal; közvetlen AETERNA-integráció elutasítva. |
| 10 | `hackstone` | [forrás](https://github.com/hackclub/hackstone) | forrás rögzítve | — |
| 11 | `Pali – 3D Multiplayer Godot Card Game` | [forrás](https://github.com/rametta/Pali) | forrás rögzítve | Első teljes multiplayer/source audit elkészült. Vizsgált commit: `bcea2eb2b3c49c90a7d4616dd80e5f7570dbcd42`; Godot 4.1, GDScript, ENet, kétpeer-es dedicated server. Hasznos lifecycle és server-side score referencia, de teljes deck/hand identity leak, scene-tree authority, player-callable turnváltó RPC és hiányos ownership/zónavalidáció található. Licenc: Apache-2.0; assetek külön auditálandók. |
| 12 | `Seven Card Game` | [forrás](https://github.com/Valyreon/seven-card-game-godot) | forrás rögzítve | — |
| 13 | `Simple CardPileUI` | [forrás](https://github.com/insideout-andrew/simple-card-pile-ui) | forrás rögzítve | Első teljes presentation/source audit elkészült. Vizsgált commit: `e9f52b0b3485fb83dd8072fe8098e820d5b90236`; Godot 4.2 / GDScript / EditorPlugin. Hasznos HandFan, pile-layout, CardUI/CardUIData, dropzone és signal referencia. A draw/discard/shuffle/hand-limit UI-oldali, a programozott drop nem validál automatikusan; stable ID, schema, determinism, test/CI és explicit licenc nem talált. |

### 3. gyűjtési kör
| # | Rögzített név / helyi mappanév | Forrás | Állapot | Megjegyzés |
|---:|---|---|---|---|
| 14 | `Project Ignis card databases for EDOPro [BabelCDB]` | [forrás](https://github.com/ProjectIgnis/BabelCDB/tree/master) | forrás rögzítve | — |
| 15 | `CardGameEngine-main` | — | azonosításra vár | Nincs elég adat megbízható repository-hozzárendeléshez. |
| 16 | `card-game-engine-master` | — | azonosításra vár | Több azonos nevű projekt létezik; helyi README vagy .git/config szükséges. |
| 17 | `Project Ignis card scripts for EDOPro [CardScripts]` | [forrás](https://github.com/ProjectIgnis/CardScripts) | forrás rögzítve | — |
| 18 | `colyseus` | [forrás](https://github.com/colyseus/colyseus) | forrás rögzítve | — |
| 19 | `Project Ignis: EDOPro [Distribution]` | [forrás](https://github.com/ProjectIgnis/Distribution) | forrás rögzítve | — |
| 20 | `Hearthstone Clone App` | [forrás](https://github.com/EnginKARATAS/fable5-hearthstone-clone-game-demo) | forrás rögzítve | — |
| 21 | `gym-locm` | [forrás](https://github.com/ronaldosvieira/gym-locm) | forrás rögzítve | — |
| 22 | `HearthClone-master` | — | azonosításra vár | Katalógusjelölt: https://github.com/Fiskell/HearthClone — több azonos nevű projekt miatt ellenőrzendő. |
| 23 | `Hearthstone.gd` | [forrás](https://github.com/LunarTides/Hearthstone.gd) | forrás rögzítve | — |
| 24 | `LorcanaJSON` | [forrás](https://github.com/LorcanaJSON/LorcanaJSON) | forrás rögzítve | — |
| 25 | `mdgachasim` | [forrás](https://github.com/Mari6814/mdgachasim) | forrás rögzítve | — |
| 26 | `mighty-engine-main` | — | azonosításra vár | A mappanév önmagában nem azonosít egyértelmű repositoryt. |
| 27 | `nakama-master` | — | azonosításra vár | Katalógusjelölt: https://github.com/heroiclabs/nakama — a helyi forrással még egyeztetendő. |
| 28 | `node-ygocore-interface` | [forrás](https://github.com/ghlin/node-ygocore-interface) | forrás rögzítve | — |
| 29 | `node-ygocore` | [forrás](https://github.com/ghlin/node-ygocore) | forrás rögzítve | — |
| 30 | `OpenSpiel: A Framework for Reinforcement Learning in Games` | [forrás](https://github.com/google-deepmind/open_spiel) | forrás rögzítve | — |
| 31 | `PettingZoo` | [forrás](https://github.com/Farama-Foundation/PettingZoo) | forrás rögzítve | — |
| 32 | `PokerKit` | [forrás](https://github.com/uoftcprg/pokerkit) | forrás rögzítve | — |
| 33 | `PTCG-Bench-main` | — | azonosításra vár | Katalógusjelölt: https://github.com/zjunet/PTCG-Bench — a helyi forrással még egyeztetendő. |
| 34 | `Project Ignis canonical puzzle collection for EDOPro [Puzzles]` | [forrás](https://github.com/ProjectIgnis/Puzzles) | forrás rögzítve | — |
| 35 | `rtcg-master` | — | azonosításra vár | Katalógusjelölt: https://github.com/hiasmstudio/RTCG — a helyi forrással még egyeztetendő. |
| 36 | `YGOCore` | [forrás](https://github.com/Buttys/YGOCore) | forrás rögzítve | — |
| 37 | `ygopro` | [forrás](https://github.com/Fluorohydride/ygopro) | forrás rögzítve | — |
| 38 | `YGOSiM` | [forrás](https://github.com/stevoduhhero/YGOSiM-archive) | forrás rögzítve | — |
| 39 | `yugioh-duel-simulator-main` | — | azonosításra vár | Katalógusjelölt: https://github.com/Nivaldo-Nilngn/yugioh-duel-simulator — a helyi forrással még egyeztetendő. |
| 40 | `Yu-Gi-Oh-Master-Duel-Draw-Simulator-main` | — | azonosításra vár | Katalógusjelölt: https://github.com/struja125/Yu-Gi-Oh-Master-Duel-Draw-Simulator — a helyi forrással még egyeztetendő. |
| 41 | `yugioh-simulator` | [forrás](https://github.com/arthastheking113/yugioh-simulator) | forrás rögzítve | A név gyakori; a rögzített URL és a helyi origin később összevetendő. |

### 4. gyűjtési kör
| # | Rögzített név / helyi mappanév | Forrás | Állapot | Megjegyzés |
|---:|---|---|---|---|
| 42 | `Durak.Godot` | [forrás](https://github.com/ch200c/Durak.Godot) | forrás rögzítve | Első repository-forráskód-audit elkészült; külön Godot, pure C# gameplay, unit- és functional-test projektek. |
| 43 | `GodoPy` | [forrás](https://github.com/godopy/godopy) | forrás rögzítve | — |
| 44 | `Godot RL Agents` | [forrás](https://github.com/edbeeching/godot_rl_agents) | forrás rögzítve | — |
| 45 | `godot-python-extension` | [forrás](https://github.com/maiself/godot-python-extension) | forrás rögzítve | — |
| 46 | `Godot Python` | [forrás](https://github.com/touilleMan/godot-python) | forrás rögzítve | — |
| 47 | `py4godot` | [forrás](https://github.com/niklas2902/py4godot) | forrás rögzítve | — |

### 5. gyűjtési kör
| # | Rögzített név / helyi mappanév | Forrás | Állapot | Megjegyzés |
|---:|---|---|---|---|
| 48 | `Godot-CardPileFramework` | [forrás](https://github.com/Ggross98/Godot-CardPileFramework) | forrás rögzítve | Első repository-forráskód-audit elkészült. |
| 49 | `Arcomage` | [aktuális upstream](https://github.com/DarkPro1337/Arcomage) | forrás rögzítve | Első repository-forráskód-audit elkészült; aktív default branch: `mono`; Godot 4.7/.NET 10, YAML effect DSL, ENet és WASM modrendszer. |
| 50 | `C# Battle Card Game Framework (CSBCGF)` | [aktuális upstream](https://github.com/finkmoritz/csbcgf) | forrás rögzítve | Első AETERNA-központú repository-audit elkészült; vizsgált commit: `36c4c80ca22a105fef4024c4f15a525f3cdb7e2d`; action/reaction és component framework; utolsó vizsgált commit 2023-02-14. |
| 51 | `Godot-4-Card-Game-CSharp` | [forrás](https://github.com/TheSchlote/Godot-4-Card-Game-CSharp) | forrás rögzítve | Első repository-forráskód-audit elkészült; a repository archivált. |
| 52 | `card-game-engine` | [aktuális upstream](https://gitlab.com/jcbcn/card-game-engine) | forrás rögzítve | Első strukturális és package-audit elkészült. Vizsgált branch: `main`; rövid HEAD: `e5c9e468`; kiadás: Engine/Abstractions 2.6.3; .NET 10; NuGet licencmező: `GPL-3.0-only`. A helyi mappa originje, teljes SHA-ja és belső rules-flow auditja még nyitott. |
| 53 | `Card Game Engine` | [aktuális upstream](https://gitlab.com/DavidCorrect/card-game-engine) | forrás rögzítve | Első README/architecture audit elkészült. Godot/GDScript; Control Node UI; Deck, Hand, Stack, Play, Discard és Exile; drag-and-drop; Godot High-Level API és RPC; README snapshot: `9a092bdf`, v3.1. A helyi source-, RPC-, authority- és hidden-information audit még nyitott. |

## 5. Kiemelt konzisztencia-eltérések

### 5.1 RLCard

A projekt kanonikus és folyamatosan használt hivatkozása:

- `https://github.com/datamllab/rlcard`

A korábbi letöltött `mjiang9/_rlcard` repository ugyanennek a projektnek egy régebbi,
nem hivatalos GitHub-forkként jelölt snapshotja volt. A helyi forrás erre az aktuális
upstreamre cserélendő.

A nyilvántartási szabály:

- a forráslista mindig a repository default ágára mutató stabil URL-t tartja;
- az elemzés mindig rögzíti a vizsgált branch/tag és commit SHA értékét;
- új upstream commit miatt a régi elemzési fájlt nem kell automatikusan átírni;
- új vizsgálatkor az elemzés státusza és a vizsgált commit frissül;
- az upstream legutóbbi ellenőrzött HEAD-je 2024-06-26-án
  `d7d0a957baf4cc7225a50522adb0164bf130a9d0` volt, de letöltéskor mindig a tényleges
  default-branch HEAD-et kell használni.

### 5.2 Godot 4 card game frameworkek

Az aktuális source audit alapján a kapcsolat:

```text
db0/godot-card-game-framework
├── eredeti Godot 3.4 / GDScript framework
├── linyangqi/godot-card-game-framework-gd4
│   └── külön Godot 4 port/fork
└── kptmn/godot-card-game-framework4
    └── külön repositoryban fenntartott Godot 4.2 konverzió
```

A `kptmn` repository tehát külön forrásrekord marad, de nem önálló, a db0 rendszertől
független architektúra. A README, a classok, a dictionary ScriptingEngine és a commitok
alapján a db0 2.2 framework konverziója.

A három projektet külön repositoryként és külön commit-alapon kell kezelni, de az
implementációs leszármazást minden későbbi elemzésben rögzíteni kell.

### 5.3 Az ötödik gyűjtési kör státusza

Az ötödik kör hat projektje már letöltött forrásként szerepel ebben a listában.
A LEARNING_CATALOG v0.3 még „újonnan talált, nem letöltött jelöltként” kezelte őket.
A v0.4 katalógusban ezek átkerülnek a letöltött projektek közé.

### 5.4 Lehetséges, de nem bizonyított névütközések

A következő korábbi helyi mappák és az ötödik kör GitLab-projektjei között névegyezés
van, de a kapcsolat nem bizonyított:

- `CardGameEngine-main`;
- `card-game-engine-master`;
- `jcbcn/card-game-engine`;
- `DavidCorrect/card-game-engine`.

Ezeket a helyi `.git/config` vagy README ellenőrzéséig külön rekordként kell kezelni.

## 6. Karbantartási szabályok

1. Új projekt felvételekor a rögzített helyi mappanevet változtatás nélkül meg kell őrizni.
2. Az eredeti repository URL-t csak ellenőrzött információ alapján szabad hozzáadni.
3. A `main`, `master` vagy archive-utótag nem bizonyítja a repository eredetét.
4. A projekt első elemzésekor rögzíteni kell a vizsgált branch/tag és commit SHA értékét.
5. A licencet projektenként külön kell ellenőrizni; a nyilvános repository nem jelent
   automatikus átvételi engedélyt.
6. Az elemzési dokumentum útvonala:
   `learning/analyses/<owner>__<repository>.md`.
7. A forrásmappák nem kerülnek Gitbe; a reprodukálhatóságot URL, commit SHA és
   bizonyítékjegyzék biztosítja.
8. Ha egy helyi mappa eredete nem igazolható, a státusza maradjon `azonosításra vár`.
9. Két hasonló nevű repositoryt nem szabad egyetlen rekordba összevonni pusztán névegyezés alapján.
10. A lista és a központi katalógus projekt- és státuszszámait minden módosítás után
    össze kell vetni.

## 7. Következő ellenőrzési feladatok

### Elsőbbségi eredetazonosítás

1. `CardGameEngine-main`
2. `card-game-engine-master`
3. `mighty-engine-main`
4. `mage-master`
5. `Godot4-Fake3D-Card-Game-UI-Demo-main`

### Katalógusjelölt és helyi mappa összevetése

1. `HearthClone-master`
2. `nakama-master`
3. `PTCG-Bench-main`
4. `rtcg-master`
5. `yugioh-duel-simulator-main`
6. `Yu-Gi-Oh-Master-Duel-Draw-Simulator-main`

### Külön konfliktusvizsgálat

1. Godot 4 framework: `kptmn/godot-card-game-framework4` vagy
   `linyangqi/godot-card-game-framework-gd4`

## 8. Változásnapló

### 2.3 – 2026-07-25

- elkészült a `Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo` első teljes provenance/presentation/shader source auditja;
- az elkészült projektszintű elemzések száma tizennégyre frissült;
- bekerült a vizsgált commit, a Godot 4.5 és a GPL-3.0 licenc;
- rögzítésre került az önálló repository és a külső shader/tutorial/asset provenance;
- rögzítésre került a fake-3D, shadow, flash, dissolve, hand layout és multi-drag tanulási érték;
- rögzítésre került az UI/model/rules összefonódás, a kozmetikai shuffle és több konkrét forráshiba;
- rögzítésre került az MIT shader- és CC0 assetlicencréteg;
- rögzítésre került a hiányzó status check, workflow run és automatizált teszt;
- a következő kijelölt forrás a `Valyreon/seven-card-game-godot`.

### 2.2 – 2026-07-25

- elkészült a `db0/Fragment-Forge` első teljes application/content/deckbuilder source auditja;
- az elkészült projektszintű elemzések száma tizenháromra frissült;
- bekerült a vizsgált commit, a Godot 3.x és az AGPL-3.0 licenc;
- rögzítésre került a 100 lapos content, a dictionary effectrendszer és a custom DSL-bővítés;
- rögzítésre került a Persona és affinity/inspiration deckbuilder;
- rögzítésre került a deck JSON trust boundary és a konkrét persona/placement/index hibák;
- rögzítésre került a hiányzó CI/workflow proof;
- a következő kijelölt forrás a `Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo`, eredetellenőrzéssel kezdve.

### 2.1 – 2026-07-25

- elkészült az `insideout-andrew/deckbuilder-framework` első teljes source auditja;
- az elkészült projektszintű elemzések száma tizenkettőre frissült;
- bekerült a vizsgált commit, a Godot 4.3 és az MIT licenc;
- pontosításra került a CardData–Card–Deck presentation/interaction scope;
- rögzítésre került, hogy a projekt nem kész constructed-deck editor vagy paklilegalitási rendszer;
- rögzítésre került a child-order authority, stable ID/state version, hidden projection és determinism hiánya;
- rögzítésre került a hiányzó status check, workflow run és automatizált teszt;
- a következő kijelölt forrás a `db0/Fragment-Forge`.

### 2.0 – 2026-07-25

- elkészült az `insideout-andrew/simple-card-pile-ui` első teljes presentation/source auditja;
- az elkészült projektszintű elemzések száma tizenegyre frissült;
- bekerült a vizsgált commit és a Godot 4.2 / EditorPlugin technológiai állapot;
- rögzítésre került a HandFan-, pile-layout-, CardUI/CardUIData-, dropzone- és signal-scope;
- rögzítésre került a UI-oldali draw/discard/shuffle és a programozott drop validációhiánya;
- rögzítésre került a stable ID, schema, determinism, test/CI és explicit licenc hiánya;
- a következő kijelölt forrás az `insideout-andrew/deckbuilder-framework`.

### 1.9 – 2026-07-25

- elkészült a `rametta/Pali` első teljes multiplayer- és authority-source auditja;
- az elkészült projektszintű elemzések száma tízre frissült;
- bekerült a vizsgált commit, a Godot 4.1, az ENet és a dedicated server scope;
- rögzítésre került a teljes deck/hand identity kliensoldali szivárgása;
- rögzítésre került a scene-tree authority és a hiányos RPC/ownership validation;
- rögzítésre került az Apache-2.0 licenc és a külön assetaudit;
- a következő kijelölt forrás az `insideout-andrew/simple-card-pile-ui`.

### 1.8 – 2026-07-25

- elkészült a `kptmn/godot-card-game-framework4` első teljes source auditja;
- az elkészült projektszintű elemzések száma kilencre frissült;
- pontosításra került, hogy külön repository, de a db0 framework Godot 4.2-es konverziója;
- bekerült a vizsgált commit és a Godot 4.2/4.2.1 állapot;
- rögzítésre került a nyitott ScriptingEngine/Card portkockázat;
- rögzítésre került a nem bizonyított PASS workflow-státusz;
- rögzítésre került az AGPL közvetlen integráció elutasítása;
- a következő kijelölt forrás a `rametta/Pali`.

### 1.7 – 2026-07-25

- elkészült a `db0/godot-card-game-framework` első teljes source auditra épülő elemzése;
- az elkészült projektszintű elemzések száma nyolcra frissült;
- bekerült a vizsgált commit, a 2.2 framework-verzió és a Godot 3.4.x technológia;
- rögzítésre került a dictionary ScriptingEngine, a GUT teszt/CI és a seedelt RNG;
- rögzítésre került az AGPL-3.0 licenc és a közvetlen integráció elutasítása;
- a következő kijelölt forrás a `kptmn/godot-card-game-framework4`.

### 1.6 – 2026-07-24

- elkészült a `DavidCorrect/card-game-engine` első README- és architekturális elemzése;
- az elkészült projektszintű elemzések száma hétre frissült;
- bekerült a README snapshot, v3.1 státusz és a Godot/GDScript technológia;
- rögzítésre került a zóna-, Stack/Exile-, drag-and-drop és multiplayer scope;
- a helyi source-, RPC-, authority- és hidden-information audit nyitott maradt.

### 1.5 – 2026-07-24

- elkészült a `jcbcn/card-game-engine` első strukturális és package-szintű elemzése;
- az elkészült projektszintű elemzések száma hatra frissült;
- a rekordhoz bekerült a `main` branch, az `e5c9e468` rövid HEAD és a 2.6.3 kiadás;
- rögzítésre került a `.NET 10` target;
- rögzítésre került a NuGet `GPL-3.0-only` licencmező;
- a helyi origin, teljes SHA és rules-engine source audit továbbra is nyitott.

### 1.4 – 2026-07-24

- megszűnt a verziózott és verziótlan forráslisták párhuzamos kezelése;
- a forráslista kizárólag `sources list_vX.Y.md` formában marad;
- a `sources list.md` és `sources list_REPLACEMENT*.md` nem része az aktív modellnek;
- a katalógusra való hivatkozás logikai dokumentumszerepre váltott;
- az aktuális forráslista a legmagasabb elfogadott verzió;
- az RLCard eredetkonfliktusa lezárult: a kanonikus forrás `datamllab/rlcard`.

### 1.3 – 2026-07-24

- elkészült a `finkmoritz/csbcgf` első részletes elemzése;
- az elkészült elemzések száma ötre frissült;
- rögzítésre került, hogy minden külső projektet kizárólag az AETERNA-val hasonlítunk össze;
- a CSBCGF rekordhoz bekerült a vizsgált commit és a 2023-as aktivitási státusz.

### 1.2 – 2026-07-24

- az RLCard kanonikus forrása `datamllab/rlcard` lett;
- a `mjiang9/_rlcard` csak történeti snapshotként marad megjegyzésben;
- bevezetésre került a stabil upstream URL + elemzésenként rögzített commit elv;
- a kapcsolódó katalógus stabil útvonala az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum lett;
- elkészült a `DarkPro1337/Arcomage` első részletes elemzése;
- az elkészült elemzések száma négyre frissült;
- a problémás eredetű projektek külön backlog dokumentumba kerültek.

### 1.1 – 2026-07-24

- megerősítésre került, hogy a letöltött RLCard-forrás a `mjiang9/_rlcard`;
- a `datamllab/rlcard` aktuális upstream- és összehasonlítási alapként került rögzítésre;
- a két RLCard repositoryt snapshot/upstream kapcsolatként kezeljük, nem azonos aktív forrásként;
- rögzítésre került, hogy a `linyangqi/godot-card-game-framework-gd4` a
  `db0/godot-card-game-framework` forkja és Godot 4 portkísérlete;
- a `kptmn/godot-card-game-framework4` külön repositoryként marad nyilvántartva;
- elkészült a `ch200c/Durak.Godot` első projektszintű elemzése;
- az elkészült elemzések száma háromra frissült;
- a kapcsolódó katalógus akkor használt konkrét verzióhivatkozása frissült.

### 1.0 – 2026-07-23

- a nyers, behúzásokkal tagolt lista strukturált Markdown-dokumentummá alakult;
- az öt gyűjtési kör és mind az 53 projekt megmaradt;
- különválasztásra került a rögzített forrás, a katalógusjelölt és az azonosítatlan eredet;
- bekerült a 42 rögzített URL és a 11 még megerősítendő tétel összesítése;
- dokumentálásra került az RLCard és a Godot 4 framework katalóguseltérése;
- dokumentálásra kerültek a lehetséges `card-game-engine` névütközések;
- bekerültek az egységes karbantartási és későbbi eredetellenőrzési szabályok.
