# AETERNA – LEARNING FORRÁSPROJEKTEK NYILVÁNTARTÁSA

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 1.0
- **Dátum:** 2026-07-23
- **Státusz:** strukturált, ellenőrzési megjegyzésekkel kiegészített munkaváltozat
- **Szerep:** a `learning/sources/` alatt tárolt vagy korábban letöltött külső projektek eredet-nyilvántartása
- **Kapcsolódó katalógus:** `learning/LEARNING_CATALOG_v0.4.md`
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
| Elkészült első projektszintű elemzés | 2 |

## 3. Azonosítási állapotok

- **forrás rögzítve:** a jelenlegi listában konkrét URL szerepel; ez még nem bizonyítja,
  hogy a helyi mappa pontosan abból a repositoryból és abból a commitból származik;
- **azonosításra vár:** nincs közvetlenül rögzített URL, ezért helyi `.git/config`,
  README, archive-metaadat vagy letöltési előzmény szükséges;
- **katalógusjelölt:** korábbi kutatás alapján van valószínű repository, de azt nem szabad
  megerősített forrásként kezelni a helyi mappával való egyeztetés előtt.

## 4. Forrásprojektek gyűjtési körönként

### 1. gyűjtési kör
| # | Rögzített név / helyi mappanév | Forrás | Állapot | Megjegyzés |
|---:|---|---|---|---|
| 1 | `RLCard: A Toolkit for Reinforcement Learning in Card Games` | [forrás](https://github.com/mjiang9/_rlcard) | forrás rögzítve | Eltérés: a LEARNING_CATALOG v0.3 a datamllab/rlcard projektet rendeli hozzá. A helyi origin alapján kell dönteni. |
| 2 | `boardgame.io` | [forrás](https://github.com/boardgameio/boardgame.io) | forrás rögzítve | — |
| 3 | `duelyst` | [forrás](https://github.com/open-duelyst/duelyst) | forrás rögzítve | — |
| 4 | `mage-master` | — | azonosításra vár | Katalógusjelölt: https://github.com/magefree/mage — a helyi mappával még egyeztetendő. |

### 2. gyűjtési kör
| # | Rögzített név / helyi mappanév | Forrás | Állapot | Megjegyzés |
|---:|---|---|---|---|
| 5 | `deckbuilder-framework` | [forrás](https://github.com/insideout-andrew/deckbuilder-framework) | forrás rögzítve | — |
| 6 | `Fragment-Forge` | [forrás](https://github.com/db0/Fragment-Forge) | forrás rögzítve | — |
| 7 | `Godot4-Fake3D-Card-Game-UI-Demo-main` | — | azonosításra vár | Katalógusjelölt: https://github.com/Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo — fork/tükör miatt ellenőrzendő. |
| 8 | `godot-card-game-framework4` | [forrás](https://github.com/kptmn/godot-card-game-framework4) | forrás rögzítve | Eltérés: a LEARNING_CATALOG v0.3 a linyangqi/godot-card-game-framework-gd4 projektet rendeli hozzá. A két repository külön létezik. |
| 9 | `godot-card-game-framework` | [forrás](https://github.com/db0/godot-card-game-framework) | forrás rögzítve | — |
| 10 | `hackstone` | [forrás](https://github.com/hackclub/hackstone) | forrás rögzítve | — |
| 11 | `Pali – 3D Multiplayer Godot Card Game` | [forrás](https://github.com/rametta/Pali) | forrás rögzítve | — |
| 12 | `Seven Card Game` | [forrás](https://github.com/Valyreon/seven-card-game-godot) | forrás rögzítve | — |
| 13 | `Simple CardPileUI` | [forrás](https://github.com/insideout-andrew/simple-card-pile-ui) | forrás rögzítve | — |

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
| 42 | `Durak.Godot` | [forrás](https://github.com/ch200c/Durak.Godot) | forrás rögzítve | — |
| 43 | `GodoPy` | [forrás](https://github.com/godopy/godopy) | forrás rögzítve | — |
| 44 | `Godot RL Agents` | [forrás](https://github.com/edbeeching/godot_rl_agents) | forrás rögzítve | — |
| 45 | `godot-python-extension` | [forrás](https://github.com/maiself/godot-python-extension) | forrás rögzítve | — |
| 46 | `Godot Python` | [forrás](https://github.com/touilleMan/godot-python) | forrás rögzítve | — |
| 47 | `py4godot` | [forrás](https://github.com/niklas2902/py4godot) | forrás rögzítve | — |

### 5. gyűjtési kör
| # | Rögzített név / helyi mappanév | Forrás | Állapot | Megjegyzés |
|---:|---|---|---|---|
| 48 | `Godot-CardPileFramework` | [forrás](https://github.com/Ggross98/Godot-CardPileFramework) | forrás rögzítve | Első repository-forráskód-audit elkészült. |
| 49 | `Arcomage` | [forrás](https://github.com/DarkPro1337/Arcomage) | forrás rögzítve | — |
| 50 | `C# Battle Card Game Framework (CSBCGF)` | [forrás](https://github.com/finkmoritz/csbcgf) | forrás rögzítve | — |
| 51 | `Godot-4-Card-Game-CSharp` | [forrás](https://github.com/TheSchlote/Godot-4-Card-Game-CSharp) | forrás rögzítve | Első repository-forráskód-audit elkészült; a repository archivált. |
| 52 | `card-game-engine` | [forrás](https://gitlab.com/jcbcn/card-game-engine/-/tree/main) | forrás rögzítve | — |
| 53 | `Card Game Engine` | [forrás](https://gitlab.com/DavidCorrect/card-game-engine) | forrás rögzítve | — |

## 5. Kiemelt konzisztencia-eltérések

### 5.1 RLCard

A jelenlegi forráslistában a következő repository szerepel:

- `mjiang9/_rlcard`

A LEARNING_CATALOG v0.3 ugyanakkor ezt rendelte a helyi projekthez:

- `datamllab/rlcard`

Mindkét repository létezik. A helyes hozzárendelést a helyi `origin` URL, a README,
a commit SHA vagy az archive letöltési adatai alapján kell eldönteni. Addig egyik
hozzárendelés sem írhatja felül automatikusan a másikat.

### 5.2 Godot 4 card game framework

A jelenlegi forráslistában ez szerepel:

- `kptmn/godot-card-game-framework4`

A LEARNING_CATALOG v0.3 ezt rendelte hozzá:

- `linyangqi/godot-card-game-framework-gd4`

A két repository külön projektként létezik. A helyi mappa eredetét ellenőrizni kell,
és szükség esetén mindkettőt külön rekordként kell nyilvántartani.

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

1. RLCard: `mjiang9/_rlcard` vagy `datamllab/rlcard`
2. Godot 4 framework: `kptmn/godot-card-game-framework4` vagy
   `linyangqi/godot-card-game-framework-gd4`

## 8. Változásnapló

### 1.0 – 2026-07-23

- a nyers, behúzásokkal tagolt lista strukturált Markdown-dokumentummá alakult;
- az öt gyűjtési kör és mind az 53 projekt megmaradt;
- különválasztásra került a rögzített forrás, a katalógusjelölt és az azonosítatlan eredet;
- bekerült a 42 rögzített URL és a 11 még megerősítendő tétel összesítése;
- dokumentálásra került az RLCard és a Godot 4 framework katalóguseltérése;
- dokumentálásra kerültek a lehetséges `card-game-engine` névütközések;
- bekerültek az egységes karbantartási és későbbi eredetellenőrzési szabályok.
