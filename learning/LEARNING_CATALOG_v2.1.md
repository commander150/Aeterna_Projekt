# AETERNA – LEARNING PROJECT CATALOG

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 2.1
- **Dátum:** 2026-08-15
- **Státusz:** a 58 current local source, 30 projektszintű analysis és a cross-project synthesis/blueprint program alapján újraszinkronizált központi katalógus
- **Szerep:** külső learning projektek, analysis coverage, synthesis-szerep és jövőbeli vizsgálati prioritások központi nyilvántartása
- **Forráslista:** az aktuális verziózott „AETERNA – LEARNING FORRÁSPROJEKTEK NYILVÁNTARTÁSA” dokumentum
- **Projektenkénti elemzések:** `learning/analyses/<owner>__<repository>.md`
- **Cross-project synthesis:** `learning/synthesis/`
- **Nem AETERNA-szabályforrás és nem engine-specifikáció.**

## 1. Dokumentummodell

A `learning/` központi dokumentumai továbbra is verziózott fájlnevet használnak:

```text
LEARNING_CATALOG_vX.Y.md
sources list_vX.Y.md
ANALYSIS_TEMPLATE_vX.Y.md
ORIGIN_IDENTIFICATION_BACKLOG_vX.Y.md
```

A projektenkénti analysis állandó fájlnevet használ:

```text
learning/analyses/<owner>__<repository>.md
```

A cross-project synthesis külön réteg:

```text
learning/synthesis/
```

A 2.1-es katalógus szerkezeti frissítés; a 2.0 változat történeti snapshotként megmarad.

## 2. Aktuális összesítés

| Mutató | Érték |
|---|---:|
| Aktív registry project record | 59 |
| Current local source | 58 |
| Current local source nélkül, de analysis-szel megőrzött project | 1 |
| Projektszintű analysis dokumentum | 30 |
| Current local source analysis nélkül | 29 |
| Analysis current local source nélkül | 1 |
| Cross-project synthesis témadokumentum | 12 |
| Általános architecture capability gap, amely új source letöltését kötelezővé teszi | 0 |

## 3. Audit és synthesis összehasonlítási határa

### 3.1 Projektenkénti audit – izolált

A `learning/analyses/` alatt minden projektet továbbra is kizárólag az AETERNA
aktuális rendszeréhez viszonyítunk.

Az egyedi analysisban tilos:

- külső learning projekteket egymással rangsorolni;
- egyik projekt hiányosságát egy másik projekt megoldásával „kijavítani”;
- másik learning projektre támaszkodó vegyes auditot készíteni;
- AETERNA szabályt vagy döntést külső projekttel felülírni.

Ez a tiszta auditmódszer változatlan.

### 3.2 Cross-project synthesis – külön engedélyezett réteg

A fenti tiltás **nem** jelenti azt, hogy a teljes learning programban tilos a projektek
közös mintáinak összevetése.

A cross-project összevetés kizárólag:

```text
learning/synthesis/
```

alatt történhet, külön synthesis módszertannal.

A synthesis:

1. csak már elkészült izolált auditokra támaszkodik;
2. megőrzi az evidence lineage-ot;
3. külön kezeli az azonos source-familybe tartozó forkokat;
4. nem projekt-rangsort készít;
5. közös patterneket, anti-patterneket, trade-offokat és capability gapeket keres;
6. minden következtetést visszafordít AETERNA-specifikus kérdéssé;
7. önmagában nem válik AETERNA-authorityvé.

A folyamat:

```text
isolated source audit
→ cross-project synthesis
→ pattern catalog
→ AETERNA blueprint proposal
→ human decision
→ adopted contract
→ implementation
```

## 4. Elemzési állapotok

- **regisztrálva:** repository record létezik;
- **provenance ellenőrizve:** project identity használható;
- **source feltérképezve:** struktúra és fő komponensek ellenőrizve;
- **analysis kész:** projektszintű analysis dokumentum létezik;
- **synthesisben felhasználva:** legalább egy cross-project synthesis evidence-e;
- **AETERNA-döntéshez felhasználva:** külön emberi döntés explicit hivatkozik a tanulságra.

Az `analysis kész` nem jelenti automatikusan azt, hogy minden subsystem teljesen auditált.

## 5. Current project catalog

A `Prioritás` oszlop csak a **még nem analizált** projektek következő vizsgálati
sorrendjére vonatkozik. Elkészült analysis esetén `—`.

| # | Current local folder | Repository | Fő kategória | Analysis státusz | Prioritás | Elsődleges további tanulási terület |
|---:|---|---|---|---|:---:|---|
| 1 | `boardgameio__boardgame.io` | [`boardgameio/boardgame.io`](https://github.com/boardgameio/boardgame.io) | rules engine / card-game architecture | analysis kész | — | legal actions, timing, ability/effect, state transition, testing |
| 2 | `datamllab__rlcard` | [`datamllab/rlcard`](https://github.com/datamllab/rlcard) | AI / headless / benchmark | analysis kész | — | observation, legal action, imperfect information, simulation, evaluation |
| 3 | `magefree__mage` | [`magefree/mage`](https://github.com/magefree/mage) | rules engine / card-game architecture | analysis kész | — | legal actions, timing, ability/effect, state transition, testing |
| 4 | `open-duelyst__duelyst` | [`open-duelyst/duelyst`](https://github.com/open-duelyst/duelyst) | rules engine / card-game architecture | analysis nincs | P2 | legal actions, timing, ability/effect, state transition, testing |
| 5 | `db0__Fragment-Forge` | [`db0/Fragment-Forge`](https://github.com/db0/Fragment-Forge) | Godot card-game architecture | analysis kész | — | Godot client architecture, state/UI boundary, multiplayer/card flow |
| 6 | `db0__godot-card-game-framework` | [`db0/godot-card-game-framework`](https://github.com/db0/godot-card-game-framework) | Godot card-game architecture | analysis kész | — | Godot client architecture, state/UI boundary, multiplayer/card flow |
| 7 | `Fulafu-ai__Godot4-Fake3D-Card-Game-UI-Demo` | [`Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo`](https://github.com/Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo) | client / UI / presentation | analysis kész | — | card presentation, hand/pile layout, interaction, visual effects |
| 8 | `hackclub__hackstone` | [`hackclub/hackstone`](https://github.com/hackclub/hackstone) | Godot card-game architecture | analysis nincs | P2 | Godot client architecture, state/UI boundary, multiplayer/card flow |
| 9 | `insideout-andrew__deckbuilder-framework` | [`insideout-andrew/deckbuilder-framework`](https://github.com/insideout-andrew/deckbuilder-framework) | client / UI / presentation | analysis kész | — | card presentation, hand/pile layout, interaction, visual effects |
| 10 | `insideout-andrew__simple-card-pile-ui` | [`insideout-andrew/simple-card-pile-ui`](https://github.com/insideout-andrew/simple-card-pile-ui) | client / UI / presentation | analysis kész | — | card presentation, hand/pile layout, interaction, visual effects |
| 11 | `linyangqi__godot-card-game-framework-gd4` | [`linyangqi/godot-card-game-framework-gd4`](https://github.com/linyangqi/godot-card-game-framework-gd4) | Godot card-game architecture | analysis nincs | P2 | Godot client architecture, state/UI boundary, multiplayer/card flow |
| 12 | `rametta__Pali` | [`rametta/Pali`](https://github.com/rametta/Pali) | Godot card-game architecture | analysis kész | — | Godot client architecture, state/UI boundary, multiplayer/card flow |
| 13 | `Valyreon__seven-card-game-godot` | [`Valyreon/seven-card-game-godot`](https://github.com/Valyreon/seven-card-game-godot) | Godot card-game architecture | analysis kész | — | Godot client architecture, state/UI boundary, multiplayer/card flow |
| 14 | — | [`kptmn/godot-card-game-framework4`](https://github.com/kptmn/godot-card-game-framework4) | Godot card-game architecture | analysis kész; current local source nincs | — | Godot client architecture, state/UI boundary, multiplayer/card flow |
| 15 | `arthastheking113__yugioh-simulator` | [`arthastheking113/yugioh-simulator`](https://github.com/arthastheking113/yugioh-simulator) | Yu-Gi-Oh runtime / tooling / simulator | analysis nincs | P2 | rules/runtime integration, engine wrappers, scenario/simulator patterns |
| 16 | `Buttys__YGOCore` | [`Buttys/YGOCore`](https://github.com/Buttys/YGOCore) | Yu-Gi-Oh runtime / tooling / simulator | analysis nincs | P2 | rules/runtime integration, engine wrappers, scenario/simulator patterns |
| 17 | `colyseus__colyseus` | [`colyseus/colyseus`](https://github.com/colyseus/colyseus) | multiplayer backend | analysis kész | — | authoritative hosting, session, reconnect, sync, transport |
| 18 | `CyrSol__CardGameEngine` | [`CyrSol/CardGameEngine`](https://github.com/CyrSol/CardGameEngine) | rules engine / card-game architecture | analysis nincs | P1 | legal actions, timing, ability/effect, state transition, testing |
| 19 | `dj-shin__mighty-engine` | [`dj-shin/mighty-engine`](https://github.com/dj-shin/mighty-engine) | rules engine / card-game architecture | analysis nincs | P1 | legal actions, timing, ability/effect, state transition, testing |
| 20 | `EnginKARATAS__hearthstone-web-version` | [`EnginKARATAS/hearthstone-web-version`](https://github.com/EnginKARATAS/hearthstone-web-version) | rules engine / card-game architecture | analysis nincs | P1 | legal actions, timing, ability/effect, state transition, testing |
| 21 | `Farama-Foundation__PettingZoo` | [`Farama-Foundation/PettingZoo`](https://github.com/Farama-Foundation/PettingZoo) | AI / headless / benchmark | analysis nincs | P1 | observation, legal action, imperfect information, simulation, evaluation |
| 22 | `Fiskell__HearthClone` | [`Fiskell/HearthClone`](https://github.com/Fiskell/HearthClone) | rules engine / card-game architecture | analysis nincs | P1 | legal actions, timing, ability/effect, state transition, testing |
| 23 | `Fluorohydride__ygopro` | [`Fluorohydride/ygopro`](https://github.com/Fluorohydride/ygopro) | Yu-Gi-Oh runtime / tooling / simulator | analysis nincs | P2 | rules/runtime integration, engine wrappers, scenario/simulator patterns |
| 24 | `frissyn__rtcg` | [`frissyn/rtcg`](https://github.com/frissyn/rtcg) | rules engine / card-game architecture | analysis nincs | P2 | legal actions, timing, ability/effect, state transition, testing |
| 25 | `ghlin__node-ygocore` | [`ghlin/node-ygocore`](https://github.com/ghlin/node-ygocore) | Yu-Gi-Oh runtime / tooling / simulator | analysis nincs | P2 | rules/runtime integration, engine wrappers, scenario/simulator patterns |
| 26 | `ghlin__node-ygocore-interface` | [`ghlin/node-ygocore-interface`](https://github.com/ghlin/node-ygocore-interface) | Yu-Gi-Oh runtime / tooling / simulator | analysis nincs | P2 | rules/runtime integration, engine wrappers, scenario/simulator patterns |
| 27 | `google-deepmind__open_spiel` | [`google-deepmind/open_spiel`](https://github.com/google-deepmind/open_spiel) | AI / headless / benchmark | analysis kész | — | observation, legal action, imperfect information, simulation, evaluation |
| 28 | `heroiclabs__nakama` | [`heroiclabs/nakama`](https://github.com/heroiclabs/nakama) | multiplayer backend | analysis kész | — | authoritative hosting, session, reconnect, sync, transport |
| 29 | `karthikpanicker__card-game-engine` | [`karthikpanicker/card-game-engine`](https://github.com/karthikpanicker/card-game-engine) | rules engine / card-game architecture | analysis nincs | P1 | legal actions, timing, ability/effect, state transition, testing |
| 30 | `LorcanaJSON__LorcanaJSON` | [`LorcanaJSON/LorcanaJSON`](https://github.com/LorcanaJSON/LorcanaJSON) | data / content / Yu-Gi-Oh ecosystem | analysis kész | — | content identity, schema, package, scripts, localization, fixture/data workflow |
| 31 | `LunarTides__Hearthstone.gd` | [`LunarTides/Hearthstone.gd`](https://github.com/LunarTides/Hearthstone.gd) | Godot card-game architecture | analysis kész | — | Godot client architecture, state/UI boundary, multiplayer/card flow |
| 32 | `Mari6814__mdgachasim` | [`Mari6814/mdgachasim`](https://github.com/Mari6814/mdgachasim) | Yu-Gi-Oh runtime / tooling / simulator | analysis nincs | P3 | rules/runtime integration, engine wrappers, scenario/simulator patterns |
| 33 | `Nivaldo-Nilngn__yugioh-duel-simulator` | [`Nivaldo-Nilngn/yugioh-duel-simulator`](https://github.com/Nivaldo-Nilngn/yugioh-duel-simulator) | Yu-Gi-Oh runtime / tooling / simulator | analysis nincs | P2 | rules/runtime integration, engine wrappers, scenario/simulator patterns |
| 34 | `ProjectIgnis__BabelCDB` | [`ProjectIgnis/BabelCDB`](https://github.com/ProjectIgnis/BabelCDB) | data / content / Yu-Gi-Oh ecosystem | analysis kész | — | content identity, schema, package, scripts, localization, fixture/data workflow |
| 35 | `ProjectIgnis__CardScripts` | [`ProjectIgnis/CardScripts`](https://github.com/ProjectIgnis/CardScripts) | data / content / Yu-Gi-Oh ecosystem | analysis kész | — | content identity, schema, package, scripts, localization, fixture/data workflow |
| 36 | `ProjectIgnis__Distribution` | [`ProjectIgnis/Distribution`](https://github.com/ProjectIgnis/Distribution) | data / content / Yu-Gi-Oh ecosystem | analysis kész | — | content identity, schema, package, scripts, localization, fixture/data workflow |
| 37 | `ProjectIgnis__Puzzles` | [`ProjectIgnis/Puzzles`](https://github.com/ProjectIgnis/Puzzles) | data / content / Yu-Gi-Oh ecosystem | analysis nincs | P1 | content identity, schema, package, scripts, localization, fixture/data workflow |
| 38 | `ronaldosvieira__gym-locm` | [`ronaldosvieira/gym-locm`](https://github.com/ronaldosvieira/gym-locm) | AI / headless / benchmark | analysis nincs | P1 | observation, legal action, imperfect information, simulation, evaluation |
| 39 | `stevoduhhero__YGOSiM-archive` | [`stevoduhhero/YGOSiM-archive`](https://github.com/stevoduhhero/YGOSiM-archive) | Yu-Gi-Oh runtime / tooling / simulator | analysis nincs | P3 | rules/runtime integration, engine wrappers, scenario/simulator patterns |
| 40 | `struja125__Yu-Gi-Oh-Master-Duel-Draw-Simulator` | [`struja125/Yu-Gi-Oh-Master-Duel-Draw-Simulator`](https://github.com/struja125/Yu-Gi-Oh-Master-Duel-Draw-Simulator) | Yu-Gi-Oh runtime / tooling / simulator | analysis nincs | P3 | rules/runtime integration, engine wrappers, scenario/simulator patterns |
| 41 | `uoftcprg__pokerkit` | [`uoftcprg/pokerkit`](https://github.com/uoftcprg/pokerkit) | rules engine / card-game architecture | analysis kész | — | legal actions, timing, ability/effect, state transition, testing |
| 42 | `zjunet__PTCG-Bench` | [`zjunet/PTCG-Bench`](https://github.com/zjunet/PTCG-Bench) | AI / headless / benchmark | analysis nincs | P3 | observation, legal action, imperfect information, simulation, evaluation |
| 43 | `ch200c__Durak.Godot` | [`ch200c/Durak.Godot`](https://github.com/ch200c/Durak.Godot) | Godot card-game architecture | analysis kész | — | Godot client architecture, state/UI boundary, multiplayer/card flow |
| 44 | `edbeeching__godot_rl_agents` | [`edbeeching/godot_rl_agents`](https://github.com/edbeeching/godot_rl_agents) | AI / headless / benchmark | analysis nincs | P2 | observation, legal action, imperfect information, simulation, evaluation |
| 45 | `godopy__godopy` | [`godopy/godopy`](https://github.com/godopy/godopy) | Godot language/binding tooling | analysis nincs | P3 | Godot integration, language bridge, tooling boundary |
| 46 | `maiself__godot-python-extension` | [`maiself/godot-python-extension`](https://github.com/maiself/godot-python-extension) | Godot language/binding tooling | analysis nincs | P3 | Godot integration, language bridge, tooling boundary |
| 47 | `niklas2902__py4godot` | [`niklas2902/py4godot`](https://github.com/niklas2902/py4godot) | Godot language/binding tooling | analysis nincs | P3 | Godot integration, language bridge, tooling boundary |
| 48 | `touilleMan__godot-python` | [`touilleMan/godot-python`](https://github.com/touilleMan/godot-python) | Godot language/binding tooling | analysis nincs | P3 | Godot integration, language bridge, tooling boundary |
| 49 | `DarkPro1337__Arcomage` | [`DarkPro1337/Arcomage`](https://github.com/DarkPro1337/Arcomage) | Godot card-game architecture | analysis kész | — | Godot client architecture, state/UI boundary, multiplayer/card flow |
| 50 | `DavidCorrect__card-game-engine` | [`DavidCorrect/card-game-engine`](https://gitlab.com/DavidCorrect/card-game-engine) | Godot card-game architecture | analysis kész | — | Godot client architecture, state/UI boundary, multiplayer/card flow |
| 51 | `finkmoritz__csbcgf` | [`finkmoritz/csbcgf`](https://github.com/finkmoritz/csbcgf) | rules engine / card-game architecture | analysis kész | — | legal actions, timing, ability/effect, state transition, testing |
| 52 | `Ggross98__Godot-CardPileFramework` | [`Ggross98/Godot-CardPileFramework`](https://github.com/Ggross98/Godot-CardPileFramework) | client / UI / presentation | analysis kész | — | card presentation, hand/pile layout, interaction, visual effects |
| 53 | `jcbcn__card-game-engine` | [`jcbcn/card-game-engine`](https://gitlab.com/jcbcn/card-game-engine) | rules engine / card-game architecture | analysis kész | — | legal actions, timing, ability/effect, state transition, testing |
| 54 | `TheSchlote__Godot-4-Card-Game-CSharp` | [`TheSchlote/Godot-4-Card-Game-CSharp`](https://github.com/TheSchlote/Godot-4-Card-Game-CSharp) | client / UI / presentation | analysis kész | — | card presentation, hand/pile layout, interaction, visual effects |
| 55 | `Card-Forge__forge` | [`Card-Forge/forge`](https://github.com/Card-Forge/forge) | rules engine / card-game architecture | analysis kész | — | legal actions, timing, ability/effect, state transition, testing |
| 56 | `edo9300__edopro` | [``edo9300/edopro` / Project Ignis EDOPro`](https://github.com/`edo9300/edopro` / Project Ignis EDOPro) | rules engine / card-game architecture | analysis nincs | P3 | legal actions, timing, ability/effect, state transition, testing |
| 57 | `edo9300__ygopro-core` | [`edo9300/ygopro-core`](https://github.com/edo9300/ygopro-core) | Yu-Gi-Oh runtime / tooling / simulator | analysis kész | — | rules/runtime integration, engine wrappers, scenario/simulator patterns |
| 58 | `gemelom__ptcg-engine` | [`gemelom/ptcg-engine`](https://github.com/gemelom/ptcg-engine) | rules engine / card-game architecture | analysis nincs | P0 | legal actions, timing, ability/effect, state transition, testing |
| 59 | `simeydotme__pokemon-cards-css` | [`simeydotme/pokemon-cards-css`](https://github.com/simeydotme/pokemon-cards-css) | client / UI / presentation | analysis kész | — | card presentation, hand/pile layout, interaction, visual effects |

## 6. Analysis coverage

### 6.1 Elkészült projektszintű analysis

Összesen: **30**.

Ebből:

- 29 current local source-hoz tartozik;
- 1 (`kptmn/godot-card-game-framework4`) current local source nélkül megőrzött analysis.

### 6.2 Current local source analysis nélkül

Összesen: **29**.

A következő új analysis prioritás:

1. **P0:** `gemelom/ptcg-engine`
2. **P1:** `ProjectIgnis/Puzzles`
3. **P1:** `EnginKARATAS/hearthstone-web-version`
4. **P1:** `edo9300/edopro`
5. **P1:** `Farama-Foundation/PettingZoo`
6. **P1:** `ronaldosvieira/gym-locm`
7. **P1:** `dj-shin/mighty-engine`
8. **P1:** `CyrSol/CardGameEngine`
9. **P1:** `karthikpanicker/card-game-engine`
10. **P1:** `Fiskell/HearthClone`

Ez rugalmas lista. Konkrét OPEN_QUESTION vagy implementation gap felülírhatja.

## 7. Cross-project synthesis coverage

Az első nagy blueprint-programban elkészült synthesis témák:

1. authority and state;
2. reactions / triggers / resolution;
3. determinism and random;
4. serialization / save / replay;
5. actions and validation;
6. events and projection;
7. ability / effect / continuous systems;
8. AI and simulation;
9. multiplayer / session / reconnect;
10. data and content pipeline;
11. release / diagnostics / observability;
12. Godot client and UI.

Ezek mellett külön:

- project capability matrix;
- pattern catalog;
- AETERNA-specifikus blueprint dokumentumok

készültek.

A synthesis dokumentumok **nem szabályforrások**.

## 8. Új source letöltési kapu

A jelenlegi coverage mellett új learning source csak akkor indokolt, ha:

1. konkrét capability gap marad;
2. egy OPEN_QUESTION több architecture-alternatíva között nyitott;
3. combat/replacement vagy más új subsystem speciális bizonyítékot igényel;
4. technology selectionhez friss összehasonlítás kell;
5. a jelenlegi source-family nem ad független evidence-et.

Általános „gyűjtsünk még több card engine-t” feladat jelenleg nincs.

## 9. Korábbi, még nem local candidate projektek

A 2.0 verzióból megőrzött jelöltek:

| Repository | Eredeti tanulási irány | Jelenlegi státusz |
|---|---|---|
| `StefanoFiumara/harry-potter-tcg` | Unity/C# TCG rules, AI, deck editor | csak konkrét gap esetén újraellenőrizendő |
| `sominator/colyseus-2d-multiplayer-card-game-templates` | Colyseus multiplayer template | B1 coverage miatt jelenleg nem prioritás |
| `JenardKin/triple-triad-godot` | kisebb Godot+C# card placement | E1 coverage miatt jelenleg nem prioritás |
| `DapperDino/CCG-Single-Player-Learning` | oktatási CCG minta | P2/P3 referencia |
| `kai63001/wildcard-game` | Godot+Nakama flow | B1 coverage miatt jelenleg nem prioritás |

Nem töröljük őket, de letöltés előtt aktuális repository/licenc/érték ellenőrzés szükséges.

## 10. Licenc- és provenance-elv

- Nyilvános repository nem jelent automatikus kódátvételi engedélyt.
- Az egyedi analysis rögzíti a vizsgált revision licencét.
- Current local snapshot licencadata eltérhet egy korábban analizált revisiontől.
- Példa: `insideout-andrew/simple-card-pile-ui` current local snapshotban MIT licenc található,
  miközben egy régebbi analysis revisionban más licencállapot volt rögzítve.
- `jcbcn/card-game-engine` root licenc és package/NuGet licencmetadata külön egyeztetendő.
- Fork family licencet minden konkrét repository/revision szintjén ellenőrizni kell.

## 11. Következő fő munkakör

A pre-OQ architecture coverage elkészült.

Következő sorrend:

1. source registry / catalog / provenance dokumentumok szinkronizálása;
2. teljes blueprint consistency audit lezárása;
3. teljes OPEN_QUESTIONS feldolgozás;
4. Reaction/Priority decision closure;
5. Reaction/Priority implementation;
6. később combat és további rules-driven blueprint-ek.

## 12. Változásnapló

### 2.1 – 2026-08-15

- registry count 59, current local source 58;
- analysis count 30;
- final local inventory és kézi provenance-vizsgálat beemelve;
- az egyedi audit és a külön cross-project synthesis szabálya pontosítva;
- 12 synthesis tématerület rögzítve;
- új source letöltési kapu bevezetve;
- future analysis prioritás frissítve;
- historical candidate list megőrizve;
- current local/source replacement és fork-family állapothoz igazítva.

A korábbi változástörténet a 2.0 és régebbi verziókban megmarad.
