# AETERNA – LEARNING FORRÁSPROJEKTEK NYILVÁNTARTÁSA

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 2.7
- **Dátum:** 2026-08-15
- **Státusz:** a végső helyi source-inventoryval, kézi provenance-visszaellenőrzéssel és a blueprint-program új elemzéseivel szinkronizált munkaváltozat
- **Szerep:** a `learning/sources/` alatt jelenleg tárolt, illetve már analizált külső learning projektek eredet- és jelenlét-nyilvántartása
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Kapcsolódó elemzések:** `learning/analyses/`
- **Kapcsolódó synthesis réteg:** `learning/synthesis/`
- **A lista nem AETERNA-szabályforrás és nem engedély kód vagy asset átvételére.**

## 1. A dokumentum célja

A nyilvántartás külön kezeli:

1. a külső projekt/repository **azonosságát**;
2. a **jelenlegi helyi source snapshot** meglétét;
3. a helyi snapshot **pontos revisionjének bizonyíthatóságát**;
4. az elkészült projektszintű elemzés státuszát;
5. a fork/upstream/replacement kapcsolatokat.

A 2.7-es verzió tudatos szerkezeti frissítés. A korábbi 2.6 változat történeti
snapshotként megmarad; az abban szereplő részletes korábbi auditmegjegyzéseket nem
töröljük, a jelenlegi részletes következtetések elsődleges helye a projektenkénti
`learning/analyses/` dokumentum.

## 2. Aktuális összesítés

| Mutató | Érték |
|---|---:|
| Gyűjtési körök száma | 6 |
| Aktív nyilvántartott projekt-rekord | 59 |
| Jelenleg helyben tárolt source projekt | 58 |
| Current local source nélkül, de külön analysis-szel megőrzött projekt | 1 |
| Helyi Git repository | 0 |
| Helyi archive/current snapshot | 58 |
| Projektazonosság szintjén lezáratlan rekord | 0 |
| Pontos local snapshot revision bizonyítható | 0 |
| Pontos local snapshot revision nem bizonyítható | 58 |
| Elkészült projektszintű analysis dokumentum | 30 |
| Jelenlegi local source analysis nélkül | 29 |
| Analysis current local source nélkül | 1 |

### 2.1 Fontos számlálási különbség

A **59 nyilvántartott projekt** és az **58 jelenlegi local source** nem hiba.

A különbség:

- `kptmn/godot-card-game-framework4` továbbra is önálló, már analizált registry-rekord;
- current local source mappája jelenleg nincs;
- a `linyangqi/godot-card-game-framework-gd4` nem helyettesíti a kptmn analysis targetet.

A korábbi `EnginKARATAS/fable5-hearthstone-clone-game-demo` nem külön aktív rekord:
tudatos **SOURCE REPLACEMENT** történt a frissebb
`EnginKARATAS/hearthstone-web-version` projektre.

## 3. Azonosítási modell

### 3.1 Project provenance confidence

- **CONFIRMED:** `.git` origin, bizonyított commit/archive metadata vagy ezzel egyenértékű közvetlen bizonyíték;
- **STRONG:** több egymást erősítő lokális metadata/README/project evidence és stabil repository-hivatkozás;
- **PROBABLE:** jó jelölt, de még nem elég többforrású bizonyíték;
- **AMBIGUOUS:** több repository reálisan lehetséges;
- **UNKNOWN:** nincs megbízható azonosítás.

A jelenlegi 58 local snapshot mind projektazonosság szintjén **STRONG**.

### 3.2 Local snapshot revision status

- **EXACT:** helyi commit SHA bizonyítható;
- **ARCHIVE_METADATA:** archive metadata konkrét revisiont rögzít;
- **CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN:** a projekt ismert, de a letöltött ZIP/snapshot pontos commitja nem;
- **N/A:** current local source nincs.

A jelenlegi 58 local source mind
`CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN`.

Ez nem projektazonosítási hiba, hanem reprodukálhatósági korlát.

## 4. Aktív projekt-registry

| # | Kör | Jelenlegi helyi mappa | Repository | Project provenance | Local revision | Analysis | Licenc | Megjegyzés |
|---:|:---:|---|---|---|---|---|---|---|
| 1 | 1 | `boardgameio__boardgame.io` | [`boardgameio/boardgame.io`](https://github.com/boardgameio/boardgame.io) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT |  |
| 2 | 1 | `datamllab__rlcard` | [`datamllab/rlcard`](https://github.com/datamllab/rlcard) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT | Canonical upstream; historic `mjiang9/_rlcard` is not locally present. |
| 3 | 1 | `magefree__mage` | [`magefree/mage`](https://github.com/magefree/mage) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT | Earlier backlog provenance is now locally resolvable. |
| 4 | 1 | `open-duelyst__duelyst` | [`open-duelyst/duelyst`](https://github.com/open-duelyst/duelyst) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | CC0-1.0 |  |
| 5 | 2 | `db0__Fragment-Forge` | [`db0/Fragment-Forge`](https://github.com/db0/Fragment-Forge) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | AGPL-3.0 | Separate project from db0 card-game framework. |
| 6 | 2 | `db0__godot-card-game-framework` | [`db0/godot-card-game-framework`](https://github.com/db0/godot-card-game-framework) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | AGPL-3.0 plus Steamworks addendum | Upstream of the local linyangqi port. |
| 7 | 2 | `Fulafu-ai__Godot4-Fake3D-Card-Game-UI-Demo` | [`Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo`](https://github.com/Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | GPL-3.0; bundled asset/shader notices differ |  |
| 8 | 2 | `hackclub__hackstone` | [`hackclub/hackstone`](https://github.com/hackclub/hackstone) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | No explicit license found |  |
| 9 | 2 | `insideout-andrew__deckbuilder-framework` | [`insideout-andrew/deckbuilder-framework`](https://github.com/insideout-andrew/deckbuilder-framework) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT |  |
| 10 | 2 | `insideout-andrew__simple-card-pile-ui` | [`insideout-andrew/simple-card-pile-ui`](https://github.com/insideout-andrew/simple-card-pile-ui) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT in current `LICENSE.md` | Current snapshot license differs from older analysis state; old analysis commit is not current local HEAD proof. |
| 11 | 2 | `linyangqi__godot-card-game-framework-gd4` | [`linyangqi/godot-card-game-framework-gd4`](https://github.com/linyangqi/godot-card-game-framework-gd4) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | AGPL-3.0 plus Steamworks addendum | Not `kptmn/godot-card-game-framework4`; kptmn source is absent. |
| 12 | 2 | `rametta__Pali` | [`rametta/Pali`](https://github.com/rametta/Pali) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | Apache-2.0 | Asset provenance separate. |
| 13 | 2 | `Valyreon__seven-card-game-godot` | [`Valyreon/seven-card-game-godot`](https://github.com/Valyreon/seven-card-game-godot) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | No repository license found |  |
| 14 | 2 | — (current local source nincs) | [`kptmn/godot-card-game-framework4`](https://github.com/kptmn/godot-card-game-framework4) | megerősített upstream | `N/A – current local source missing` | kész | AGPL-3.0 | Külön analizált Godot 4 fork/konverzió. Current local source nincs. Fork family: `db0/godot-card-game-framework` → `menaechmi/godot-card-game-framework4` → `kptmn/godot-card-game-framework4`. |
| 15 | 3 | `arthastheking113__yugioh-simulator` | [`arthastheking113/yugioh-simulator`](https://github.com/arthastheking113/yugioh-simulator) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | No project-level explicit license found | Kézi GitHub-visszaellenőrzés: az upstream README ugyanazokat az egyedi YGOVietnam/MetaDuelist azonosítókat tartalmazza, mint a helyi snapshot. |
| 16 | 3 | `Buttys__YGOCore` | [`Buttys/YGOCore`](https://github.com/Buttys/YGOCore) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | No explicit license found | Distinct from C++ `ygopro-core`. |
| 17 | 3 | `colyseus__colyseus` | [`colyseus/colyseus`](https://github.com/colyseus/colyseus) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT |  |
| 18 | 3 | `CyrSol__CardGameEngine` | [`CyrSol/CardGameEngine`](https://github.com/CyrSol/CardGameEngine) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT; root/cgePy templates partly unfilled, ui4cgePy copyright CyrSol | Previous UNKNOWN provenance now resolved to STRONG. |
| 19 | 3 | `dj-shin__mighty-engine` | [`dj-shin/mighty-engine`](https://github.com/dj-shin/mighty-engine) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT | Previous UNKNOWN provenance now resolved. |
| 20 | 3 | `EnginKARATAS__hearthstone-web-version` | [`EnginKARATAS/hearthstone-web-version`](https://github.com/EnginKARATAS/hearthstone-web-version) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT stated in README; no separate root LICENSE | SOURCE REPLACEMENT for the removed fable5 snapshot. |
| 21 | 3 | `Farama-Foundation__PettingZoo` | [`Farama-Foundation/PettingZoo`](https://github.com/Farama-Foundation/PettingZoo) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT |  |
| 22 | 3 | `Fiskell__HearthClone` | [`Fiskell/HearthClone`](https://github.com/Fiskell/HearthClone) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT in `composer.json`; no root LICENSE | Earlier backlog provenance resolved. |
| 23 | 3 | `Fluorohydride__ygopro` | [`Fluorohydride/ygopro`](https://github.com/Fluorohydride/ygopro) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | GPL-3.0 | Upstream client family for EDOPro. |
| 24 | 3 | `frissyn__rtcg` | [`frissyn/rtcg`](https://github.com/frissyn/rtcg) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT | Registry `hiasmstudio/RTCG` candidate is stale/wrong. |
| 25 | 3 | `ghlin__node-ygocore` | [`ghlin/node-ygocore`](https://github.com/ghlin/node-ygocore) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT (`package.json`) | Submodule depends on `moecube/ygopro-core`. |
| 26 | 3 | `ghlin__node-ygocore-interface` | [`ghlin/node-ygocore-interface`](https://github.com/ghlin/node-ygocore-interface) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT (`package.json`) |  |
| 27 | 3 | `google-deepmind__open_spiel` | [`google-deepmind/open_spiel`](https://github.com/google-deepmind/open_spiel) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | Apache-2.0 | Owner rename/history explains metadata variants. |
| 28 | 3 | `heroiclabs__nakama` | [`heroiclabs/nakama`](https://github.com/heroiclabs/nakama) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | Apache-2.0 | Earlier backlog provenance resolved. |
| 29 | 3 | `karthikpanicker__card-game-engine` | [`karthikpanicker/card-game-engine`](https://github.com/karthikpanicker/card-game-engine) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT | Separate 28/56 game engine. |
| 30 | 3 | `LorcanaJSON__LorcanaJSON` | [`LorcanaJSON/LorcanaJSON`](https://github.com/LorcanaJSON/LorcanaJSON) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT for generator; data/assets separate |  |
| 31 | 3 | `LunarTides__Hearthstone.gd` | [`LunarTides/Hearthstone.gd`](https://github.com/LunarTides/Hearthstone.gd) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | GPL-3.0 |  |
| 32 | 3 | `Mari6814__mdgachasim` | [`Mari6814/mdgachasim`](https://github.com/Mari6814/mdgachasim) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT |  |
| 33 | 3 | `Nivaldo-Nilngn__yugioh-duel-simulator` | [`Nivaldo-Nilngn/yugioh-duel-simulator`](https://github.com/Nivaldo-Nilngn/yugioh-duel-simulator) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | No explicit license found | Earlier backlog provenance resolved. |
| 34 | 3 | `ProjectIgnis__BabelCDB` | [`ProjectIgnis/BabelCDB`](https://github.com/ProjectIgnis/BabelCDB) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | No root license found | `/tree/master` URL is branch-specific, not local branch proof. |
| 35 | 3 | `ProjectIgnis__CardScripts` | [`ProjectIgnis/CardScripts`](https://github.com/ProjectIgnis/CardScripts) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | AGPL-3.0-or-later |  |
| 36 | 3 | `ProjectIgnis__Distribution` | [`ProjectIgnis/Distribution`](https://github.com/ProjectIgnis/Distribution) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | AGPL-3.0; per-folder assets may vary | Composes CardScripts, BabelCDB and Puzzles. |
| 37 | 3 | `ProjectIgnis__Puzzles` | [`ProjectIgnis/Puzzles`](https://github.com/ProjectIgnis/Puzzles) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | AGPL-3.0-or-later |  |
| 38 | 3 | `ronaldosvieira__gym-locm` | [`ronaldosvieira/gym-locm`](https://github.com/ronaldosvieira/gym-locm) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT |  |
| 39 | 3 | `stevoduhhero__YGOSiM-archive` | [`stevoduhhero/YGOSiM-archive`](https://github.com/stevoduhhero/YGOSiM-archive) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT | Historic/archive project. |
| 40 | 3 | `struja125__Yu-Gi-Oh-Master-Duel-Draw-Simulator` | [`struja125/Yu-Gi-Oh-Master-Duel-Draw-Simulator`](https://github.com/struja125/Yu-Gi-Oh-Master-Duel-Draw-Simulator) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT; copyright Strahinja Miljković | Previous PROBABLE provenance upgraded to STRONG. |
| 41 | 3 | `uoftcprg__pokerkit` | [`uoftcprg/pokerkit`](https://github.com/uoftcprg/pokerkit) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT |  |
| 42 | 3 | `zjunet__PTCG-Bench` | [`zjunet/PTCG-Bench`](https://github.com/zjunet/PTCG-Bench) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT; copyright Dongdong Hua | Jelenlegi canonical GitHub repository: `zjunet/PTCG-Bench`. A README-ben történeti/stale `gemelom/PTCG-Bench` clone parancs maradt; a helyi snapshot pontos archive revisionje továbbra sem bizonyítható. |
| 43 | 4 | `ch200c__Durak.Godot` | [`ch200c/Durak.Godot`](https://github.com/ch200c/Durak.Godot) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT text with unfilled copyright placeholder | License template copyright is incomplete. |
| 44 | 4 | `edbeeching__godot_rl_agents` | [`edbeeching/godot_rl_agents`](https://github.com/edbeeching/godot_rl_agents) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT | `pyproject.toml` project URLs incorrectly use `pypa/godot_rl_agents`; other evidence supports edbeeching. |
| 45 | 4 | `godopy__godopy` | [`godopy/godopy`](https://github.com/godopy/godopy) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT |  |
| 46 | 4 | `maiself__godot-python-extension` | [`maiself/godot-python-extension`](https://github.com/maiself/godot-python-extension) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT |  |
| 47 | 4 | `niklas2902__py4godot` | [`niklas2902/py4godot`](https://github.com/niklas2902/py4godot) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT |  |
| 48 | 4 | `touilleMan__godot-python` | [`touilleMan/godot-python`](https://github.com/touilleMan/godot-python) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT | Historic binding project. |
| 49 | 5 | `DarkPro1337__Arcomage` | [`DarkPro1337/Arcomage`](https://github.com/DarkPro1337/Arcomage) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT | Fork/branch metadata known upstream, local revision unknown. |
| 50 | 5 | `DavidCorrect__card-game-engine` | [`DavidCorrect/card-game-engine`](https://gitlab.com/DavidCorrect/card-game-engine) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT | Separate from the other three `card-game-engine` projects. |
| 51 | 5 | `finkmoritz__csbcgf` | [`finkmoritz/csbcgf`](https://github.com/finkmoritz/csbcgf) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT |  |
| 52 | 5 | `Ggross98__Godot-CardPileFramework` | [`Ggross98/Godot-CardPileFramework`](https://github.com/Ggross98/Godot-CardPileFramework) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | MIT |  |
| 53 | 5 | `jcbcn__card-game-engine` | [`jcbcn/card-game-engine`](https://gitlab.com/jcbcn/card-game-engine) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | Root GPL-3.0; NuGet metadata previously documented as GPL-3.0-only | Full local SHA unavailable; license fields should be reconciled in registry. |
| 54 | 5 | `TheSchlote__Godot-4-Card-Game-CSharp` | [`TheSchlote/Godot-4-Card-Game-CSharp`](https://github.com/TheSchlote/Godot-4-Card-Game-CSharp) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | No explicit repository license found | Repository documented as archived. |
| 55 | 6 | `Card-Forge__forge` | [`Card-Forge/forge`](https://github.com/Card-Forge/forge) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | GPL-3.0; some headers “or later” |  |
| 56 | 6 | `edo9300__edopro` | [``edo9300/edopro` / Project Ignis EDOPro`](https://github.com/`edo9300/edopro` / Project Ignis EDOPro) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | AGPL-3.0-or-later overall; module/resource licenses vary | Fork of Fluorohydride client; depends on `edo9300/ygopro-core`. |
| 57 | 6 | `edo9300__ygopro-core` | [`edo9300/ygopro-core`](https://github.com/edo9300/ygopro-core) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | AGPL-3.0-or-later; inherited components include MIT | A final inventory után a helyi provenance metadata javítva; upstream/fork family: `Fluorohydride/ygopro-core` → `edo9300/ygopro-core`. |
| 58 | 6 | `gemelom__ptcg-engine` | [`gemelom/ptcg-engine`](https://github.com/gemelom/ptcg-engine) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | nincs | MIT | New independent source; dependency of PTCG-Bench. |
| 59 | 6 | `simeydotme__pokemon-cards-css` | [`simeydotme/pokemon-cards-css`](https://github.com/simeydotme/pokemon-cards-css) | STRONG | `CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN` | kész | GPL-3.0; assets separate | Related `pokemon-cards-151` is not a separate source folder. |

## 5. Kiemelt provenance- és kapcsolatdöntések

### 5.1 PTCG-Bench

Aktuális canonical repository:

`zjunet/PTCG-Bench`

A current upstream repository 2026-08-15-i kézi ellenőrzéssel létezik és nem fork.
A current README-ben történeti/stale `gemelom/PTCG-Bench` clone parancs maradt, miközben
`gemelom` contributor, és a külön `gemelom/ptcg-engine` projekt dependencyként szerepel.

Nyilvántartási döntés:

```text
zjunet/PTCG-Bench
    current canonical repository

gemelom/ptcg-engine
    külön kapcsolódó engine/dependency
```

A local PTCG-Bench ZIP pontos archive revisionje továbbra sem bizonyítható.

### 5.2 Godot card-game framework fork-family

```text
db0/godot-card-game-framework
├── linyangqi/godot-card-game-framework-gd4
│   └── külön local Godot 4 fork/port
└── menaechmi/godot-card-game-framework4
    └── kptmn/godot-card-game-framework4
        └── külön analizált fork; current local source nincs
```

A rekordok nem vonhatók össze, de közös fork-familyként kezelendők.

### 5.3 Project Ignis / ygopro family

```text
Fluorohydride/ygopro
    upstream client family

Fluorohydride/ygopro-core
    upstream core family
        └── edo9300/ygopro-core
            └── current local analyzed core snapshot identity

edo9300/edopro
    EDOPro client
        └── dependency: edo9300/ygopro-core
```

A final local inventoryben jelzett `Fluorohydride__ygopro-core` provenance metadata-hiba
a riport után helyileg javításra került; a current registry ezért
`edo9300/ygopro-core` identityt használ.

### 5.4 Hearthstone source replacement

```text
HISTORICAL:
EnginKARATAS/fable5-hearthstone-clone-game-demo

REPLACED_BY:
EnginKARATAS/hearthstone-web-version
```

A régi demo snapshot nem aktív source rekord.

### 5.5 `rtcg`

A current local source:

`frissyn/rtcg`

A korábbi `hiasmstudio/RTCG` jelölt más projekt, Run Time Code Generator; nem kapcsolódik
a helyi card-game source-hoz.

### 5.6 Azonos nevű card-game-engine projektek

Külön projektek, nem összevonandók:

```text
CyrSol/CardGameEngine
karthikpanicker/card-game-engine
jcbcn/card-game-engine
DavidCorrect/card-game-engine
```

## 6. Mappanév-szabvány

A current local source mappák normalizált formája:

```text
<owner>__<repository>
```

A gyűjtési kör továbbra is a parent mappa:

```text
first turn/
second turn/
...
sixth turn/
```

Minden current local source-ban `SOURCE_URL.url` található.

### 6.1 Rename policy

A korábbi 2.6 szabályt pontosítjuk.

A helyi mappanév **kontrolláltan módosítható**, ha:

1. a módosítás provenance-tisztázást vagy egységes naminget szolgál;
2. a repository identity nem változik;
3. a változás a következő registry-verzióban dokumentált;
4. source replacement esetén a régi és új project identity külön meg van nevezve.

A mappaátnevezés nem hoz létre automatikusan új projekt-rekordot.

## 7. Analysis és local source viszonya

- 30 projektszintű analysis dokumentum létezik;
- ebből 29-hez current local source is van;
- `kptmn/godot-card-game-framework4` analysis current local source nélkül marad;
- 29 current local source még nem kapott projektszintű analysis dokumentumot.

A korábban vizsgált upstream commit SHA **nem tekintendő automatikusan a jelenlegi local ZIP HEAD-jének**.

Az analysis dokumentumban külön kell kezelni:

```text
previously inspected upstream revision
current local snapshot revision
```

ha a kettő nem bizonyíthatóan azonos.

## 8. Karbantartási szabályok

1. Új local source lehetőleg `<owner>__<repository>` néven kerüljön be.
2. Minden local source tartalmazzon `SOURCE_URL.url` provenance segédmetaadatot.
3. A `.url` önmagában nem commit-bizonyíték.
4. Projektazonosság és local snapshot revision külön mező.
5. Forkokat külön project recordként kezelünk, family kapcsolattal.
6. Replacement nem számít két current projektnek.
7. A projektenkénti analysis útvonala:
   `learning/analyses/<owner>__<repository>.md`.
8. Az egyedi analysis mindig rögzítse a ténylegesen vizsgált upstream commitot.
9. Analysis commitot nem állítunk be local HEAD-nek bizonyíték nélkül.
10. Licencet és asset provenance-t projektenként külön kell kezelni.
11. A source list és a Learning Catalog darabszámait minden verzióváltáskor össze kell vetni.
12. A cross-project synthesis külön `learning/synthesis/` réteg; nem része a source provenance bizonyításának.

## 9. Nyitott technikai korlátok

Repository-identitás szintjén nincs aktív provenance backlog.

Globális korlát:

- 58/58 current local source ZIP/snapshot;
- 0/58 `.git`;
- 0/58 bizonyítható exact revision.

Ha később exact local revision szükséges, külön
**snapshot-revision/reproducibility** feladat nyitható. Ez nem nyitja újra automatikusan
a repository-identitási backlogot.

## 10. Változásnapló

### 2.7 – 2026-08-15

- teljes read-only local inventory alapján 58 current source rögzítve;
- aktív registry-rekordok száma 59-re pontosítva a current local source nélküli kptmn analysis-record miatt;
- analysis dokumentumok száma 30-ra frissítve;
- bevezetve a project provenance és local snapshot revision külön kezelése;
- a korábbi 11 provenance-backlog rekord repository-identitása lezárva;
- PTCG-Bench current canonical repository `zjunet/PTCG-Bench`;
- `gemelom/ptcg-engine` külön új source;
- fable5 demo → `hearthstone-web-version` source replacement;
- `frissyn/rtcg` provenance javítva;
- linyangqi és kptmn Godot forkok külön rekordként kezelve;
- `edo9300/edopro` és `edo9300/ygopro-core` önálló current source record;
- helyi mappák `<owner>__<repository>` szabványra rendezve;
- controlled rename policy bevezetve;
- a régi 2.6 változat történeti snapshotként változatlanul megmarad.

A korábbi változástörténet a 2.6 és annál régebbi verziókban marad meg.
