# AETERNA – PROJECT CAPABILITY MATRIX

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első inventory-alapú synthesis mátrix
- **Szerep:** a már elkészült projektszintű learning elemzések képesség- és bizonyítéklefedettségének feltérképezése
- **Javasolt repository-útvonal:** `learning/synthesis/PROJECT_CAPABILITY_MATRIX_v0.1.md`
- **Kiinduló repository HEAD:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Vizsgált elemzési fájlok száma:** 18
- **Nem projekt-rangsor.**
- **Nem AETERNA-authority.**

## 1. Jelölések

| Jel | Jelentés |
|---|---|
| `P` | Primary – központi, auditált tanulási/bizonyítási terület |
| `S` | Secondary – releváns és dokumentált másodlagos terület |
| `O` | Observed – megfigyelt, de célzott synthesis szükséges |
| `—` | nincs jelenleg használható bizonyíték |

## 2. Evidence family

| Rövidítés | Family |
|---|---|
| `IGNIS` | ProjectIgnis / ocgcore kapcsolódó ökoszisztéma |
| `DB0` | db0 card framework / kapcsolódó implementációs család |
| `INSIDEOUT` | insideout-andrew presentation család |
| `IND` | jelen mátrixban önálló/független projektként kezelt |

## 3. Core / Runtime capability matrix

- **AUTH** – authoritative state / domain boundary
- **ACT** – action, legal action, validation, preflight
- **TIME** – turn/phase/pending/reaction/chain
- **ABIL** – ability/effect/modifier architecture
- **ZONE** – object identity / zone lifecycle
- **DET** – determinism / RNG / replay
- **TEST** – unit/scenario/CI/proof
- **DATA** – content/data/schema/tooling

| Projekt | Family | AUTH | ACT | TIME | ABIL | ZONE | DET | TEST | DATA |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| ProjectIgnis/CardScripts | IGNIS | O | S | P | P | S | O | S | P |
| ch200c/Durak.Godot | IND | P | P | S | S | S | O | P | O |
| DarkPro1337/Arcomage | IND | S | S | S | P | S | O | S | P |
| DavidCorrect/card-game-engine | IND | O | O | O | O | S | — | — | O |
| db0/Fragment-Forge | DB0 | O | S | O | P | S | — | O | P |
| db0/godot-card-game-framework | DB0 | O | P | S | P | S | S | S | S |
| finkmoritz/csbcgf | IND | S | P | P | P | S | O | P | S |
| Fulafu-ai/Fake3D Card UI Demo | IND | O | O | — | O | S | — | — | S |
| Ggross98/Godot-CardPileFramework | IND | O | O | — | — | S | — | O | S |
| insideout-andrew/deckbuilder-framework | INSIDEOUT | O | O | — | — | S | — | — | S |
| insideout-andrew/simple-card-pile-ui | INSIDEOUT | O | O | — | — | S | O | — | S |
| jcbcn/card-game-engine | IND | O | O | O | O | O | O | P | S |
| kptmn/godot-card-game-framework4 | DB0 | O | S | O | S | S | O | S | S |
| LunarTides/Hearthstone.gd | IND | S | S | S | P | S | O | — | P |
| rametta/Pali | IND | P | S | S | O | S | — | — | O |
| simeydotme/pokemon-cards-css | IND | — | — | — | — | — | O | O | S |
| TheSchlote/Godot-4-Card-Game-CSharp | IND | O | S | S | S | S | — | O | S |
| Valyreon/seven-card-game-godot | IND | S | S | S | — | S | — | — | O |

## 4. Client / Network / AI capability matrix

- **HID** – hidden information / viewer projection
- **NET** – multiplayer / authority / protocol
- **UI** – Godot/card presentation/input/layout
- **AI** – agent/headless/simulation
- **REL** – packaging/build/release/compatibility
- **EXT** – extensibility/modding/content-scale

| Projekt | HID | NET | UI | AI | REL | EXT |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| ProjectIgnis/CardScripts | O | — | — | — | S | P |
| ch200c/Durak.Godot | O | O | S | O | S | S |
| DarkPro1337/Arcomage | O | P | S | — | S | P |
| DavidCorrect/card-game-engine | S | S | P | — | O | O |
| db0/Fragment-Forge | — | — | S | — | O | P |
| db0/godot-card-game-framework | — | — | P | — | S | P |
| finkmoritz/csbcgf | O | O | O | — | S | P |
| Fulafu-ai/Fake3D Card UI Demo | — | — | P | — | O | S |
| Ggross98/Godot-CardPileFramework | — | — | P | — | O | S |
| insideout-andrew/deckbuilder-framework | — | — | P | — | — | S |
| insideout-andrew/simple-card-pile-ui | — | — | P | — | — | S |
| jcbcn/card-game-engine | — | — | — | — | P | P |
| kptmn/godot-card-game-framework4 | — | — | P | — | S | P |
| LunarTides/Hearthstone.gd | P | P | P | — | O | P |
| rametta/Pali | P | P | S | — | O | O |
| simeydotme/pokemon-cards-css | — | — | P | — | O | P |
| TheSchlote/Godot-4-Card-Game-CSharp | — | — | P | — | O | S |
| Valyreon/seven-card-game-godot | P | P | S | — | — | O |

## 5. Első coverage-értékelés

### Erős / túlreprezentált
**Godot/UI/presentation.** Új általános card-UI projekt letöltése jelenleg alacsony prioritás.

### Erős, de vegyes
**Multiplayer + hidden information.** Több jó és rossz authority/projection példa van, de production-grade reconnect/session/versioned protocol kevés.

### Közepes
**Ability/effect architecture.** Erős források: CardScripts, db0 framework, Fragment Forge, CSBCGF, Arcomage, Hearthstone.gd.

### Közepes
**Reaction/pending/resolution.** Fő bizonyíték: CSBCGF, CardScripts, db0 effect/task, Arcomage.

### Gyenge
**Determinism/replay/reproducible simulation.** Kevés teljes event-log/replay/golden proof.

### Nagyon gyenge
**AI/headless agent interface.** A 18 kész audit között nincs elsődleges AI/RL projekt.

### Gyenge-közepes
**CI/release/package/backward compatibility.** Kiemelt jcbcn és részleges workflow-források, de save migration/compatibility/diagnostics hiányos.

## 6. Lineage-korrekció

A nyers projektszám nem bizonyítékszám.

```text
db0/godot-card-game-framework
├── kptmn/godot-card-game-framework4
└── db0/Fragment-Forge
```

Ezek synthesis során nem három teljesen független architecture-szavazatként kezelendők.

Az insideout-andrew két UI-projektje és a ProjectIgnis/ocgcore ökoszisztéma szintén family-korrekciót igényel.

## 7. Következő elemzési prioritás – már nyilvántartott források

### P0-A Rules engine scale
1. `Card-Forge/forge`
2. `magefree/mage`
3. `edo9300/ygopro-core` / aktuális ocgcore

### P0-B Deterministic game model
4. `uoftcprg/pokerkit`
5. `boardgameio/boardgame.io`

### P0-C AI/headless
6. `google-deepmind/open_spiel`
7. `datamllab/rlcard`

Ezek után dönthető el, hogy PettingZoo/gym-locm/PTCG-Bench ad-e külön architecture-értéket.

## 8. Új projekt letöltési kapu

Új projektet főként ezekre a hiányokra érdemes keresni:
1. deterministic replay/event sourcing;
2. save/load + schema migration;
3. production-grade reconnect/session protocol;
4. large rules-engine replacement/prevention/continuous dependency;
5. simulation/headless API;
6. property/scenario-based rules testing;
7. diagnostics/tracing/profiling;
8. desktop packaging/version compatibility.

## 9. Első synthesis témasorrend

1. `authority_and_state`
2. `actions_and_validation`
3. `turn_phase_timing`
4. `reactions_triggers_resolution`
5. `ability_effect_systems`
6. `events_and_projection`
7. `hidden_information`
8. `determinism_and_random`
9. `testing_and_scenarios`
10. `repository_and_module_structure`

A Reaction/Priority Foundation miatt a 3–4. témát előre lehet venni.

## 10. Nyilvántartási eltérés

A jelenlegi learning nyilvántartásban inventory-adósság látható:
- a source registry már tartalmaz `#55 Card-Forge/forge` rekordot;
- egyes összesítők még 54 projektet írnak;
- az `learning/analyses/` aktuális fájlkészlete 18 elemzést tartalmaz;
- a Learning Catalog / Source Registry több helyen még 17 elkészült elemzést jelez.

Ezt a következő learning-registry verziófrissítésben kell rendezni.

## 11. Változásnapló

### 0.1 – 2026-08-15
- elkészült az első 18-auditos capability inventory;
- bevezetésre került az evidence-family korrekció;
- azonosításra került az UI túlreprezentáltság;
- azonosításra került az AI/headless és determinism/replay hiány;
- kijelölésre került a következő meglévő P0 forráscsoport.
