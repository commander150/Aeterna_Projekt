# AETERNA – LEARNING FORRÁSEREDTET-AZONOSÍTÁSI BACKLOG

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.3
- **Dátum:** 2026-08-15
- **Státusz:** **CLOSED – repository identity backlog lezárva**
- **Kapcsolódó forráslista:** az aktuális verziózott „AETERNA – LEARNING FORRÁSPROJEKTEK NYILVÁNTARTÁSA” dokumentum
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Cél:** a korábbi bizonytalan helyi mappák repository-identitásának lezárása és a snapshot-revision probléma különválasztása

# 1. Mi zárult le?

A 0.2 verzióban szereplő 11 elsőbbségi repository-identification rekord
repository/projekt szintjén feloldhatóvá vált.

A lezárás alapja:

- végső read-only local source inventory;
- `SOURCE_URL.url`;
- README/package/project metadata;
- licenc és file-tree evidence;
- korábbi analysis dokumentumok;
- célzott kézi GitHub-visszaellenőrzés.

Repository-identitás szintjén:

```text
ACTIVE UNRESOLVED RECORDS = 0
```

# 2. Fontos módszertani korrekció

A 0.2 lezárási feltétele egyetlen problémába mosta össze:

1. **melyik projekt/repository ez?**
2. **pontosan melyik commitból készült a helyi ZIP/snapshot?**

A final local inventory kimutatta:

```text
58 current local source
0 .git repository
0 exact local revision
58 CURRENT_SNAPSHOT_BUT_REVISION_UNKNOWN
```

Ezért a 0.3 két külön állapotot használ.

## 2.1 Project provenance

A repository/projekt identity külön lezárható erős metadata-egyezéssel.

## 2.2 Local snapshot revision

Exact commit csak `.git`, archive metadata vagy más direkt revision-bizonyíték alapján
állítható.

Az exact revision hiánya **nem teszi automatikusan bizonytalanná a repository identityt**.

# 3. A 0.2 eredeti 11 rekord lezárása

| Korábbi helyi név | Lezárt repository | Project confidence | Fő bizonyíték |
|---|---|---|---|
| `CardGameEngine-main` | [`CyrSol/CardGameEngine`](https://github.com/CyrSol/CardGameEngine) | STRONG | local `cgePy`/`ui4cgePy` metadata + SOURCE_URL + kézi GitHub-egyezés |
| `card-game-engine-master` | [`karthikpanicker/card-game-engine`](https://github.com/karthikpanicker/card-game-engine) | STRONG | exact `setup.py` repository/author metadata + SOURCE_URL |
| `mighty-engine-main` | [`dj-shin/mighty-engine`](https://github.com/dj-shin/mighty-engine) | STRONG | exact `pyproject.toml` homepage/repository + package identity |
| `mage-master` | [`magefree/mage`](https://github.com/magefree/mage) | STRONG | Maven `org.mage:mage-root` identity + SOURCE_URL + analysis |
| `Godot4-Fake3D-Card-Game-UI-Demo-main` | [`Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo`](https://github.com/Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo) | STRONG | Godot project/tree + LICENSE + SOURCE_URL + analysis |
| `HearthClone-master` | [`Fiskell/HearthClone`](https://github.com/Fiskell/HearthClone) | STRONG | Laravel structure + exact README badge/repository paths + SOURCE_URL |
| `nakama-master` | [`heroiclabs/nakama`](https://github.com/heroiclabs/nakama) | STRONG | Go/server metadata + README clone identity + SOURCE_URL + analysis |
| `PTCG-Bench-main` | [`zjunet/PTCG-Bench`](https://github.com/zjunet/PTCG-Bench) | STRONG | current GitHub canonical repo is zjunet; gemelom is contributor; stale README clone path remains |
| `rtcg-master` | [`frissyn/rtcg`](https://github.com/frissyn/rtcg) | STRONG | README/LICENSE self-link + SOURCE_URL; `hiasmstudio/RTCG` is a different Runtime Code Generator project |
| `yugioh-duel-simulator-main` | [`Nivaldo-Nilngn/yugioh-duel-simulator`](https://github.com/Nivaldo-Nilngn/yugioh-duel-simulator) | STRONG | exact GitHub Pages/project identity + SOURCE_URL |
| `Yu-Gi-Oh-Master-Duel-Draw-Simulator-main` | [`struja125/Yu-Gi-Oh-Master-Duel-Draw-Simulator`](https://github.com/struja125/Yu-Gi-Oh-Master-Duel-Draw-Simulator) | STRONG | unique author/project/license/files + SOURCE_URL |

# 4. PTCG-Bench speciális lezárás

A local-only inventory helyesen jelezte a következő konfliktust:

```text
folder + SOURCE_URL:
zjunet/PTCG-Bench

README clone command:
gemelom/PTCG-Bench
```

Kézi GitHub-visszaellenőrzéssel:

- a current repository: `zjunet/PTCG-Bench`;
- a current GitHub repository nem fork;
- `gemelom` contributor;
- a current README-ben a régi `gemelom/PTCG-Bench` clone parancs még szerepel;
- `gemelom/ptcg-engine` külön működő dependency/source;
- a `gemelom/PTCG-Bench` current endpoint nem a canonical current repository.

Döntés:

```text
CURRENT CANONICAL PROJECT IDENTITY = zjunet/PTCG-Bench
LOCAL SNAPSHOT EXACT REVISION = UNKNOWN
```

Ez repository-identitás szinten lezárja a backlogot anélkül, hogy hamis local commitot állítanánk.

# 5. További provenance-tisztázások a 0.2 backlogon kívül

## 5.1 `arthastheking113/yugioh-simulator`

A final local inventory még PROBABLE státuszt adott.

Kézi GitHub-visszaellenőrzéssel az upstream README ugyanazokat az egyedi:

- YGOVietnam;
- MetaDuelist;
- simulator/module

azonosítókat tartalmazza, mint a helyi source.

Döntés:

```text
Project provenance = STRONG
Local snapshot exact revision = UNKNOWN
```

## 5.2 Godot fork-family

```text
db0/godot-card-game-framework
├── linyangqi/godot-card-game-framework-gd4
└── menaechmi/godot-card-game-framework4
    └── kptmn/godot-card-game-framework4
```

A `linyangqi` és `kptmn` source nem ugyanaz a project record.

## 5.3 `rtcg`

Current local source:

`frissyn/rtcg`

A korábbi `hiasmstudio/RTCG` jelölt más projekt.

## 5.4 `edo9300/ygopro-core`

A final local inventory explicit metadata-ellentmondást talált a local folder/URL és
a snapshot tartalma között.

A hibát a riport után helyileg javították.

Current registry identity:

`edo9300/ygopro-core`

Upstream family:

`Fluorohydride/ygopro-core`

# 6. Névütközési csoport lezárása

A következő rekordok külön projektek:

```text
CyrSol/CardGameEngine
karthikpanicker/card-game-engine
jcbcn/card-game-engine
DavidCorrect/card-game-engine
```

A névegyezés nem jelent repository- vagy codebase-egyezést.

# 7. Global snapshot-revision limitation

Ez a dokumentum **nem** állítja, hogy a 58 current local snapshot pontos commitja ismert.

Current state:

| Mutató | Érték |
|---|---:|
| Current local source | 58 |
| `.git` metadata | 0 |
| Exact revision | 0 |
| Archive revision metadata | 0 |
| Revision unknown | 58 |

Ha később a helyi ZIP-ek pontos revisionjének reprodukálása szükséges, külön
`LOCAL_SNAPSHOT_REVISION` vagy reprodukálhatósági backlog nyitható.

Ez nem automatikusan repository-origin probléma.

# 8. Lezárási állapot

## Repository identity backlog

**CLOSED**

Feltételek:

- project identity rögzített;
- stable current repository URL rögzített;
- fork/upstream/replacement viszony, ahol releváns, dokumentált;
- licenc státusz legalább repository-szinten rögzített;
- source list és catalog frissíthető egységes identityval.

## Snapshot revision

**KNOWN GLOBAL LIMITATION**

Nem lezárási blocker a repository identity backlog számára.

# 9. Változásnapló

## 0.3 – 2026-08-15

- a final 58-source local inventory beemelve;
- project provenance és local snapshot revision különválasztva;
- az eredeti 11 backlog rekord repository identityja lezárva;
- `CardGameEngine-main` → `CyrSol/CardGameEngine`;
- `card-game-engine-master` → `karthikpanicker/card-game-engine`;
- `mighty-engine-main` → `dj-shin/mighty-engine`;
- `mage-master` → `magefree/mage`;
- `HearthClone-master` → `Fiskell/HearthClone`;
- `nakama-master` → `heroiclabs/nakama`;
- `PTCG-Bench-main` current canonical identity → `zjunet/PTCG-Bench`;
- `rtcg-master` → `frissyn/rtcg`;
- `yugioh-duel-simulator-main` → `Nivaldo-Nilngn/yugioh-duel-simulator`;
- `Yu-Gi-Oh-Master-Duel-Draw-Simulator-main` → `struja125/Yu-Gi-Oh-Master-Duel-Draw-Simulator`;
- `arthastheking113/yugioh-simulator` STRONG-ra emelve kézi upstream-egyezéssel;
- Godot fork-family pontosítva;
- `edo9300/ygopro-core` current identity és upstream family különválasztva;
- repository identity backlog státusza CLOSED;
- exact local snapshot revision hiánya külön globális korlátként megőrizve.

A 0.2 és 0.1 verzió történeti snapshotként változatlanul megmarad.
