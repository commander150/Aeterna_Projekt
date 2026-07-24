# AETERNA – LEARNING PROJECT ANALYSIS TEMPLATE

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Sablonverzió:** 0.4
- **Dátum:** 2026-07-24
- **Státusz:** első használható munkasablon
- **Szerep:** egy külső referencia-projekt reprodukálható, bizonyítékokra épülő mélyelemzése
- **Kapcsolódó katalógus:** `learning/LEARNING_CATALOG.md`
- **Célútvonal:** `learning/analyses/<owner>__<repository>.md`
- **Megőrzési elv:** a fő `.md` elemzés későbbi részanyagok létrejötte után is megmarad

> A dokumentum nem marketing-összefoglaló. Minden fontos állításhoz repository-fájl,
> commit, dokumentáció vagy reprodukálható futtatási eredmény tartozzon. A README állítása
> önmagában nem bizonyítja, hogy a kód valóban megvalósítja az adott funkciót.

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Projekt neve | |
| Repository | |
| Eredeti URL | |
| Helyi forrásmappa | |
| Vizsgált branch/tag | |
| Vizsgált commit SHA | |
| Elemzés dátuma | |
| Elemző | |
| Azonosítás bizonyossága | megerősített / valószínű / bizonytalan |
| Projekt állapota | aktív / karbantartott / archivált / elhagyott / ismeretlen |
| Licenc | |
| Fő nyelv(ek) | |
| Motor/framework | |
| Célplatform | |

# 2. Vezetői összefoglaló

## 2.1 Mi ez a projekt?

Rövid, tényszerű leírás.

## 2.2 Miért érdekes az AETERNA számára?

Legfeljebb 5–8 konkrét pont.

## 2.3 Előzetes minősítés

| Szempont | Érték |
|---|---|
| Közvetlen technológiai illeszkedés | 0–5 |
| Rules-engine tanulási érték | 0–5 |
| Godot-kliens tanulási érték | 0–5 |
| Multiplayer tanulási érték | 0–5 |
| AI/szimuláció tanulási érték | 0–5 |
| Adatpipeline tanulási érték | 0–5 |
| Kódminőség | 0–5 |
| Dokumentáltság | 0–5 |
| Tesztelhetőség | 0–5 |
| Licencelési felhasználhatóság | 0–5 |
| Összesített prioritás | P0 / P1 / P2 / P3 |

## 2.4 Rövid döntés

- **Mélyelemzés folytatása:** igen / nem / feltételes
- **Kódátvétel vizsgálható:** igen / nem / csak elvi minta
- **Elsődleges tanulási terület:** 
- **Legfontosabb kockázat:** 

# 3. Vizsgálati alap és reprodukálhatóság

## 3.1 Felhasznált források

| Forrás | Útvonal/URL | Commit/verzió | Szerep |
|---|---|---|---|
| README | | | |
| Fő solution/project | | | |
| Rules/domain réteg | | | |
| Tests | | | |
| Dokumentáció | | | |
| Release/changelog | | | |

## 3.2 Build- és futtatási környezet

- Operációs rendszer:
- SDK/runtime:
- Godot/Unity/egyéb motor verzió:
- Külső függőségek:
- Build parancs:
- Tesztparancs:
- Indítási parancs:
- Szükséges adat- vagy szerverkomponens:

## 3.3 Reprodukálási eredmény

| Ellenőrzés | Eredmény | Bizonyíték |
|---|---|---|
| Repository letölthető | | |
| Build sikeres | | |
| Tesztek futnak | | |
| Demó/játék elindul | | |
| Példajáték végigjátszható | | |
| Determinisztikus futás vizsgálható | | |

# 4. Repository- és modulstruktúra

## 4.1 Fő mappák

```text
<ide kerül a releváns, rövidített repository-fa>
```

## 4.2 Modulok és felelősségek

| Modul | Felelősség | Függőségek | AETERNA-megfelelő |
|---|---|---|---|
| | | | |

## 4.3 Függőségi irányok

- Domain → UI:
- UI → Domain:
- Network → Rules:
- Data → Runtime:
- Tesztek → Production:
- Tiltott vagy problémás körkörös függőségek:

# 5. Architektúra

## 5.1 Authoritative state

- Hol él az egyetlen igaz játékállapot?
- Van-e külön state és projection?
- Módosíthatja-e a UI közvetlenül?
- Hogyan kezelik a rejtett információt?
- Mi a szerver és kliens felelőssége?

## 5.2 Fő adatáramlás

```text
input/request
    ↓
validation
    ↓
legal action / rule evaluation
    ↓
state transition
    ↓
event
    ↓
viewer-specific projection
    ↓
UI / AI / network
```

Írd le, hogy a projekt ténylegesen mennyire követi ezt vagy más modellt.

## 5.3 Állapotgép és lifecycle

- meccslétrehozás;
- játékosok;
- kör/fázis/priority;
- pending decision;
- reaction/stack/chain;
- game over;
- reset/replay/save-load.

# 6. Akció- és szabályvégrehajtás

## 6.1 Legal action modell

- Ki számítja?
- Strukturált vagy UI-ból következtetett?
- Van enabled/disabled reason?
- Tartalmaz state-version guardot?
- Újraellenőrzik execution előtt?

## 6.2 Request validation

| Ellenőrzés | Megoldás | Fájl/szimbólum |
|---|---|---|
| játékos | | |
| turn/phase | | |
| ownership/control | | |
| zone | | |
| resource/cost | | |
| target/selection | | |
| stale request | | |
| duplicate/replay request | | |

## 6.3 State transition

- Atomikus?
- Van részleges mutation kockázat?
- Exception esetén rollback történik?
- State version mikor nő?
- Eventek mikor jönnek létre?
- Determinisztikus a sorrend?

## 6.4 Eventmodell

- event type-ok;
- sequence;
- payload;
- belső és player-facing event különválasztása;
- hidden-info redaction;
- replay és audit célú használat.

# 7. Kártyamodell

## 7.1 Definition és instance

| Tulajdonság | Definition | Instance | Megjegyzés |
|---|:---:|:---:|---|
| card ID | | | |
| owner | | | |
| controller | | | |
| zone | | | |
| activity/tapped state | | | |
| cost | | | |
| stats | | | |
| ability | | | |
| visibility | | | |

## 7.2 Zónák

| Zóna | Rendezett? | Rejtett? | Tulajdonos | Fő transitionök |
|---|:---:|:---:|---|---|
| deck | | | | |
| hand | | | | |
| discard | | | | |
| play/domain | | | | |
| stack | | | | |
| exile | | | | |
| egyéb | | | | |

## 7.3 Költség- és erőforrásrendszer

- printed/base cost;
- current/normalized cost;
- fizetési forrás;
- forrásválasztás;
- exact payment/túlfizetés;
- refund/rollback;
- temporary resource;
- cost modifier;
- erőforrás-identitás/szín/birodalom.

# 8. Ability- és effect-rendszer

## 8.1 Reprezentáció

- kódolt osztály;
- script;
- adatvezérelt payload;
- natural language;
- expression/DSL;
- kombinált modell.

## 8.2 Ability lifecycle

```text
declaration
→ validation
→ trigger/hook
→ target/selection
→ resolution
→ mutation/event
→ cleanup/expiration
```

## 8.3 Vizsgálandó részletek

- trigger;
- condition;
- target;
- cost;
- effect;
- duration;
- modifier;
- prevention/replacement;
- continuous effect;
- stack/chain;
- dependency/order;
- unsupported ability handling.

## 8.4 Kiterjeszthetőség

- Új kártya mennyi kódot igényel?
- Új effect type mennyi kódot igényel?
- Kártyaadat és rules code mennyire válik szét?
- Van registry/factory/reflection?
- Van schema- és verziókezelés?

# 9. Godot/UI réteg

## 9.1 Scene- és node-szerkezet

- fő scene-ek;
- autoloadok;
- card view;
- card pile/hand;
- drag-and-drop;
- input;
- animáció;
- tooltip;
- viewer-specific projection.

## 9.2 C# és Godot határa

- Godot Node-okban van-e rules-logika?
- Pure C# domainréteg létezik-e?
- Signal/event adapter hogyan működik?
- Mennyire tesztelhető headless módon?
- Milyen függőségek kötik a domaint a Godot API-hoz?

## 9.3 AETERNA szempontú értékelés

- Közvetlenül használható UI-minta:
- Csak inspiráció:
- Kerülendő csatolás:
- Szükséges adapterhatár:

# 10. Multiplayer és hálózat

- peer-to-peer vagy authoritative server;
- lobby/matchmaking;
- session és reconnect;
- state sync;
- delta/event sync;
- hidden information;
- anti-cheat;
- stale/duplicate request;
- determinisztika;
- server tick/turn authority;
- persistence.

| Kockázat | Jelenlegi megoldás | AETERNA-következtetés |
|---|---|---|
| kliensoldali csalás | | |
| rejtett kéz szivárgása | | |
| desync | | |
| reconnect | | |
| request replay | | |

# 11. AI, szimuláció és benchmark

- agent API;
- observation;
- action space;
- legal-action mask;
- reward;
- hidden information;
- seed/determinism;
- batch/headless futtatás;
- self-play;
- replay dataset;
- benchmark.

# 12. Adatpipeline és tooling

- szerkesztési forrás;
- export;
- normalizáció;
- validáció;
- runtime package;
- schema;
- lookup;
- diagnostics;
- versioning;
- publish;
- migration.

# 13. Tesztelés és minőségbiztosítás

| Teszttípus | Van? | Lefedett terület | Hiány |
|---|:---:|---|---|
| unit | | | |
| integration | | | |
| rules scenario | | | |
| fixture/golden | | | |
| determinism | | | |
| replay | | | |
| network | | | |
| UI/smoke | | | |
| performance | | | |

## 13.1 CI és release

- CI provider:
- build matrix:
- formatter/linter:
- package/release:
- semantic version:
- changelog:
- artifact retention:

# 14. Kódminőség és karbantarthatóság

## 14.1 Erősségek

- 

## 14.2 Gyengeségek

- 

## 14.3 Technikai adósság

- 

## 14.4 Biztonsági megfigyelések

- input validation;
- file/network trust boundary;
- serialization;
- secrets;
- dependency risk;
- server authority.

# 15. Licenc és felhasználhatóság

- Licenc neve:
- Kódrészletek átvétele megengedett:
- Attribution szükséges:
- Copyleft hatás:
- Assetek külön licence:
- Dokumentáció licence:
- AETERNA számára biztonságos használat:
  - [ ] elvi minta;
  - [ ] architekturális inspiráció;
  - [ ] kódrészlet átvétele;
  - [ ] közvetlen függőség;
  - [ ] nem használható.

> Licencbizonytalanság esetén kódot nem veszünk át.

# 16. AETERNA-összevetés

| Terület | Külső projekt | AETERNA jelenlegi állapot | Tanulság |
|---|---|---|---|
| authoritative state | | | |
| legal actions | | | |
| state version | | | |
| events | | | |
| hidden info | | | |
| card data | | | |
| abilities | | | |
| resources | | | |
| Godot adapter | | | |
| tests | | | |
| multiplayer | | | |
| AI | | | |

# 17. Átvehető elvek

Minden tétel legyen konkrét, bizonyítékkal alátámasztott és AETERNA-feladatra fordított.

1. 
2. 
3. 

# 18. Amit nem szabad átvenni

1. 
2. 
3. 

# 19. Konkrét AETERNA-javaslatok

| # | Javaslat | Indok | Érintett AETERNA-réteg | Prioritás | Döntési státusz |
|---:|---|---|---|:---:|---|
| 1 | | | | | |

# 20. Bizonyítékjegyzék

| ID | Állítás | Repository-fájl/szimbólum | Sor/commit | Ellenőrzés módja |
|---|---|---|---|---|
| E-001 | | | | |

# 21. Nyitott kérdések

1. 
2. 
3. 

# 22. Végső minősítés

- **Projekt tanulási értéke:** alacsony / közepes / magas / kiemelkedő
- **AETERNA-illeszkedés:** alacsony / közepes / magas / közvetlen
- **Ajánlott következő lépés:** 
- **Újravizsgálat szükséges:** igen / nem
- **Újravizsgálat feltétele:** 

# 23. Változásnapló

## 0.4 – 2026-07-24

- a katalógushivatkozás stabil `learning/LEARNING_CATALOG.md` útvonalra állt;
- a repository URL mindig az aktuális upstream default ágára mutat;
- a reprodukálhatóságot az elemzésben kötelezően rögzített branch/tag és commit SHA biztosítja;
- upstream változás miatt a korábbi elemzési dokumentumot nem kell automatikusan átírni;
- újravizsgálatkor külön dátum, commit és változásnapló-bejegyzés szükséges.

## 0.3 – 2026-07-24

- a katalógushivatkozás az aktív verziózott `LEARNING_CATALOG_v0.5.md` fájlra frissült;
- az üres, verziótlan `LEARNING_CATALOG.md` fájl nem szükséges;
- a projektenkénti fő elemzés továbbra is állandó, verziótlan fájlnéven marad.

## 0.2 – 2026-07-23

- a célmappa neve `analyses/` lett;
- bekerült az állandó fő elemzési dokumentum megőrzési elve;
- a későbbi részanyagok projektspecifikus almappába helyezhetők.

## 0.1 – 2026-07-23

- első egységes projektszintű mélyelemzési sablon;
- bekerült az authoritative state, legal action, event, hidden information és determinisztika vizsgálata;
- külön fejezetet kapott a Godot/C# határ, multiplayer, AI, adatpipeline, tesztelés és licenc;
- az AETERNA-következtetések bizonyítékjegyzékhez kötöttek.
