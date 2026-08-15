# AETERNA – PROJECT CAPABILITY MATRIX

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Verzió:** 1.0
- **Dátum:** 2026-08-15
- **Státusz:** önálló, kumulatív pre-OQ capability inventory
- **Javasolt repository-útvonal:** `learning/synthesis/PROJECT_CAPABILITY_MATRIX_v1.0.md`
- **Kiinduló AETERNA HEAD:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Projektszintű analysis dokumentumok száma a teljes workpackage beemelése után:** **30**
- **Nem projekt-rangsor.**
- **Nem AETERNA-authority.**

---

# 1. Jelölések

| Jel | Jelentés |
|---|---|
| `P` | Primary – központi, auditált tanulási/bizonyítási terület |
| `S` | Secondary – releváns és dokumentált másodlagos terület |
| `O` | Observed – megfigyelt, de nem elsődleges auditfókusz |
| `—` | nincs jelenleg használható bizonyíték az adott analysis alapján |

A jel **nem minőségi pontszám**. Negatív példa is lehet `P`.

---

# 2. Evidence family

| Family | Megjegyzés |
|---|---|
| `FORGE` | Card-Forge/forge |
| `MAGE` | magefree/mage |
| `IGNIS_CORE` | edo9300/ygopro-core + ProjectIgnis/CardScripts kapcsolódó ökoszisztéma |
| `CSBCGF` | finkmoritz/csbcgf |
| `DB0` | db0 framework/kapcsolódó család |
| `INSIDEOUT` | insideout-andrew presentation család |
| `IND` | önálló evidence family ebben a mátrixban |

Forkok/portok ugyanazon családon belül nem számítanak automatikusan független bizonyítéknak.

---

# 3. Core / runtime matrix – az első 21 audit

- `AUTH` authority/domain
- `ACT` action/validation
- `TIME` timing/pending/reaction
- `ABIL` ability/effect
- `ZONE` object/zone lifecycle
- `DET` determinism/replay
- `TEST` tests/proof
- `DATA` content/schema/tooling

| Projekt | Family | AUTH | ACT | TIME | ABIL | ZONE | DET | TEST | DATA |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Card-Forge/forge | FORGE | P | P | P | P | P | O | S | P |
| magefree/mage | MAGE | P | P | P | P | P | S | P | P |
| edo9300/ygopro-core | IGNIS_CORE | P | P | P | P | P | S | S | S |
| ProjectIgnis/CardScripts | IGNIS_CORE | O | S | P | P | S | O | S | P |
| finkmoritz/csbcgf | CSBCGF | S | P | P | P | S | O | P | S |
| ch200c/Durak.Godot | IND | P | P | S | S | S | O | P | O |
| DarkPro1337/Arcomage | IND | S | S | S | P | S | O | S | P |
| jcbcn/card-game-engine | IND | O | O | O | O | O | O | P | S |
| db0/godot-card-game-framework | DB0 | O | P | S | P | S | S | S | S |
| kptmn/godot-card-game-framework4 | DB0 | O | S | O | S | S | O | S | S |
| db0/Fragment-Forge | DB0 | O | S | O | P | S | — | O | P |
| LunarTides/Hearthstone.gd | IND | S | S | S | P | S | O | — | P |
| rametta/Pali | IND | P | S | S | O | S | — | — | O |
| Valyreon/seven-card-game-godot | IND | S | S | S | — | S | — | — | O |
| TheSchlote/Godot-4-Card-Game-CSharp | IND | O | S | S | S | S | — | O | S |
| DavidCorrect/card-game-engine | IND | O | O | O | O | S | — | — | O |
| Fulafu-ai/Fake3D Card UI Demo | IND | O | O | — | O | S | — | — | S |
| Ggross98/Godot-CardPileFramework | IND | O | O | — | — | S | — | O | S |
| insideout-andrew/deckbuilder-framework | INSIDEOUT | O | O | — | — | S | — | — | S |
| insideout-andrew/simple-card-pile-ui | INSIDEOUT | O | O | — | — | S | O | — | S |
| simeydotme/pokemon-cards-css | IND | — | — | — | — | — | O | O | S |

---

# 4. Client / network / AI matrix – az első 21 audit

| Projekt | HID | NET | UI | AI | REL | EXT |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Card-Forge/forge | S | S | O | P | S | P |
| magefree/mage | S | P | S | P | S | P |
| edo9300/ygopro-core | S | O | — | O | S | P |
| ProjectIgnis/CardScripts | O | — | — | — | S | P |
| finkmoritz/csbcgf | O | O | O | — | S | P |
| ch200c/Durak.Godot | O | O | S | O | S | S |
| DarkPro1337/Arcomage | O | P | S | — | S | P |
| LunarTides/Hearthstone.gd | P | P | P | — | O | P |
| rametta/Pali | P | P | S | — | O | O |
| Valyreon/seven-card-game-godot | P | P | S | — | — | O |
| DavidCorrect/card-game-engine | S | S | P | — | O | O |
| db0/godot-card-game-framework | — | — | P | — | S | P |
| kptmn/godot-card-game-framework4 | — | — | P | — | S | P |
| db0/Fragment-Forge | — | — | S | — | O | P |
| Ggross98/Godot-CardPileFramework | — | — | P | — | O | S |
| insideout-andrew/deckbuilder-framework | — | — | P | — | — | S |
| insideout-andrew/simple-card-pile-ui | — | — | P | — | — | S |
| Fulafu-ai/Fake3D Card UI Demo | — | — | P | — | O | S |
| TheSchlote/Godot-4-Card-Game-CSharp | — | — | P | — | O | S |
| simeydotme/pokemon-cards-css | — | — | P | — | O | P |
| jcbcn/card-game-engine | — | — | — | — | P | P |

---

# 5. A későbbi 9 targeted audit capability profilja

| Projekt | AUTH/STATE | ACT/TIME | DATA | DET/REPLAY | AI | NET | UI | REL/TOOLING | Elsődleges synthesis-szerep |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| boardgameio/boardgame.io | P | P | S | P | O | P | O | P | authoritative sync, PRNG, log/projection |
| uoftcprg/pokerkit | P | P | S | P | S | O | — | S | operation history, replay, state machine |
| google-deepmind/open_spiel | P | P | S | P | P | O | — | P | legal actions, observation/info-state, chance, clone |
| datamllab/rlcard | S | P | O | S | P | — | — | S | card-game AI env, observation, trajectories |
| colyseus/colyseus | S | S | O | S | — | P | O | P | room/session/reconnect, per-client view |
| heroiclabs/nakama | P | S | O | O | — | P | — | P | authoritative host, queues, identity/presence |
| ProjectIgnis/BabelCDB | — | — | P | S | — | — | — | P | stable content identity, CDB, delta distribution |
| ProjectIgnis/Distribution | — | — | P | O | — | — | — | P | package composition, localization, activation/update |
| LorcanaJSON/LorcanaJSON | — | — | P | S | — | — | — | P | ingestion, corrections, schema version, verification |

Ezzel a mátrixban szereplő auditált projektek száma összesen **30**.

---

# 6. Architecture coverage snapshot

| Terület | Coverage | Aktuális AETERNA-következtetés |
|---|---|---|
| authoritative state | erős | production foundation verified |
| action/validation | erős | production foundation; generalized blueprint készült |
| phase/timing/reaction | erős | rules alap ismert; Reaction blueprint RC1/RC2 gap |
| trigger/resolution | erős | production foundation + synthesis |
| ability/effect | erős | production foundation + A6 blueprint |
| continuous | közepes-erős | narrow production v1; richer rules inventory később |
| determinism/RNG | erős architecture | implementation policy később |
| replay/save | erős architecture | implementation deferred |
| AI/headless | erős | blueprint készült |
| multiplayer/reconnect | erős | backend-semleges blueprint készült |
| data/content/package | erős | current AETERNA architecture jó, blueprint formalizálta |
| release/diagnostics | erős architecture | automation/observability implementation később |
| Godot/client/UI | erős | client blueprint készült |
| combat | tudatosan későbbi rules slice | nem teljes blueprint |
| replacement/prevention | architecture boundary ismert | exact AETERNA rules külön gate |

---

# 7. Local source inventory kapcsolata

A 2026-08-15-i végső read-only helyi inventory és a kézi provenance-visszaellenőrzés után az aktuális állapot:

```text
registry project records = 59
current local source folders = 58
analysis documents = 30
```

Ez nem ellentmondás.

A különbség oka:

- nem minden current local source-hoz készült még projektszintű analysis;
- egy már analizált project (`kptmn/godot-card-game-framework4`) current local source nélkül is külön registry-rekord marad;
- project provenance és local snapshot exact revision külön fogalom.

A learning registry maintenance helyileg elkészült:

- `learning/sources list_v2.7.md`;
- `learning/LEARNING_CATALOG_v2.1.md`;
- `learning/ORIGIN_IDENTIFICATION_BACKLOG_v0.3.md`.

Repository-identitás szintjén az origin backlog lezárható; a 58 local snapshot pontos commit/revisionje továbbra is külön ismert reprodukálhatósági korlát.

---

# 8. Új source szükségesség

Jelenleg nincs általános architecture capability gap, ami önmagában újabb nagy source-gyűjtést indokolna.

Új source akkor indokolt, ha konkrét kérdés marad például:
- Combat;
- replacement/prevention;
- konkrét backend technology decision;
- speciális UI capability;
- OPEN_QUESTION, amelyhez a jelenlegi evidence nem elég.

---

# 9. Aktuális továbblépés a pre-OQ program után

A korábbi pre-OQ munkakörök 2026-08-15-re teljesültek:

- local provenance manuális visszaellenőrzés;
- Learning Catalog / Source Registry maintenance;
- blueprint consistency audit;
- full `OPEN_QUESTIONS` A0–A4 review;
- Reaction/Priority current-default döntési kör, beleértve RC1-et és a formálható RC2 irányt.

A jelenlegi következő lépések:

1. pre-commit worktree blocker-javítás és read-only újraellenőrzés;
2. learning registry + analysis commit-scope;
3. synthesis + blueprint commit-scope;
4. `OPEN_QUESTIONS.md` / `OPEN_QUESTIONS_DECISIONS.md` v2.2 páros admin commit-scope;
5. projektterv/checkpoint rövid szinkron a tényleges commitolt állapot alapján;
6. Reaction/Priority contract/spec formalizálás a current-default döntésekből;
7. csak ezután Reaction implementation és teljes teszt/audit;
8. később Combat blueprint/implementation;
9. prevention/replacement és más future timing extensionök saját rules/contract kapun keresztül.

---

# 10. Változásnapló

## 1.0 – 2026-08-15

- a v0.2 alap 21-projektes mátrixa ténylegesen megőrizve;
- boardgame.io/PokerKit/OpenSpiel/RLCard/Colyseus/Nakama/BabelCDB/Distribution/LorcanaJSON hozzáadva;
- 30 analysis dokumentum önállóan értelmezhető inventoryvá összevonva;
- 59 registry record / 58 current local source / 30 analysis végső állapothoz szinkronizálva;
- korábbi rolling verziókra való rejtett tartalmi függés megszüntetve;
- pre-commit admin sync: provenance/registry és full OQ review már completed state-ként rögzítve.
