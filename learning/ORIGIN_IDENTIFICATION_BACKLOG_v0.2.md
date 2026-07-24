# AETERNA – LEARNING FORRÁSEREDTET-AZONOSÍTÁSI BACKLOG

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.2
- **Dátum:** 2026-07-24
- **Státusz:** aktív ellenőrzési backlog
- **Kapcsolódó forráslista:** az aktuális verziózott „AETERNA – LEARNING FORRÁSPROJEKTEK NYILVÁNTARTÁSA” dokumentum
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Cél:** a bizonytalan helyi mappák eredeti repositoryjának bizonyítható azonosítása

# 1. Alapelv

Egy helyi mappa eredete csak akkor tekinthető megerősítettnek, ha legalább egy erős
bizonyíték rendelkezésre áll:

1. `.git/config` origin URL;
2. `.git/refs` vagy rögzített commit SHA, amely megtalálható az upstreamben;
3. archive metadata vagy letöltési URL;
4. README-ben egyértelmű repository-link és egyedi tartalmi egyezés;
5. package/solution metadata és teljes fájlszerkezeti egyezés.

Pusztán a mappanév, a `main/master` utótag vagy egy hasonló README nem elegendő.

# 2. Elsőbbségi azonosítatlan projektek

| Prioritás | Helyi mappanév | Jelenlegi állapot | Következő bizonyíték |
|:---:|---|---|---|
| P0 | `CardGameEngine-main` | nincs megbízható hozzárendelés | `.git/config`, README, solution/project metadata |
| P0 | `card-game-engine-master` | több azonos nevű repository lehetséges | origin, package metadata, file tree |
| P0 | `mighty-engine-main` | nem azonosított | README, package/solution név, egyedi namespace |
| P1 | `mage-master` | katalógusjelölt: `magefree/mage` | origin vagy commit-egyezés |
| P1 | `Godot4-Fake3D-Card-Game-UI-Demo-main` | több fork/tükör | README author, commit és project.godot |
| P1 | `HearthClone-master` | katalógusjelölt: `Fiskell/HearthClone` | origin és README |
| P1 | `nakama-master` | katalógusjelölt: `heroiclabs/nakama` | origin/commit |
| P1 | `PTCG-Bench-main` | katalógusjelölt: `zjunet/PTCG-Bench` | origin/README |
| P1 | `rtcg-master` | katalógusjelölt: `hiasmstudio/RTCG` | origin/namespace |
| P1 | `yugioh-duel-simulator-main` | katalógusjelölt ismert | origin/commit |
| P1 | `Yu-Gi-Oh-Master-Duel-Draw-Simulator-main` | katalógusjelölt ismert | origin/README |

# 3. Külön névütközési csoport

A következő rekordokat nem szabad összevonni bizonyíték nélkül:

```text
CardGameEngine-main
card-game-engine-master
jcbcn/card-game-engine
DavidCorrect/card-game-engine
```

Ellenőrizendő:

- nyelv és framework;
- solution/project nevek;
- namespace-ek;
- test- és docs-mappák;
- GitLab/GitHub linkek;
- commit history.

# 4. Fork- és upstream-kapcsolatok

Már tisztázott:

## RLCard

```text
datamllab/rlcard
    = kanonikus aktuális upstream

mjiang9/_rlcard
    = korábbi történeti snapshot; helyi forrásból eltávolítandó
```

## Godot card game framework

```text
db0/godot-card-game-framework
    └── linyangqi/godot-card-game-framework-gd4
        fork / Godot 4 portkísérlet

kptmn/godot-card-game-framework4
    külön repository
```

# 5. Ellenőrzési eredmény sablon

```text
Helyi mappa:
Megerősített repository:
Repository státusz:
Upstream/fork kapcsolat:
Default branch:
Helyi vagy vizsgált commit:
Bizonyíték:
Licenc:
Katalógusmódosítás:
Forráslista-módosítás:
```

# 6. Lezárási feltétel

Egy rekord akkor zárható le, ha:

- repository egyértelmű;
- upstream/fork viszony rögzített;
- stabil URL szerepel a forráslistában;
- legalább egy commit vagy archive eredet igazolt;
- licenc státusza rögzített;
- a katalógus és a forráslista egyezik.

# 7. Változásnapló

## 0.2 – 2026-07-24

- a katalógus- és forráslistahivatkozások logikai dokumentumszerepre váltottak;
- a backlog továbbra is kizárólag verziózott központi dokumentum;
- konkrét központi fájlnév vagy verziószám nem került a hivatkozásokba.

## 0.1 – 2026-07-24

- létrejött a külön eredetazonosítási backlog;
- bekerült a 11 jelenleg bizonytalan vagy megerősítendő rekord;
- rögzítésre került a `card-game-engine` névütközési csoport;
- bekerült az RLCard és a Godot-framework tisztázott upstream/fork kapcsolata;
- létrejött az egységes bizonyíték- és lezárási sablon.
