# AETERNA – kptmn/godot-card-game-framework4 ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-25
- **Státusz:** repository-forrásokra épülő első teljes elemzés
- **Fő elemzési fájl:** `learning/analyses/kptmn__godot-card-game-framework4.md`
- **Repository:** `kptmn/godot-card-game-framework4`
- **Stabil upstream URL:** `https://github.com/kptmn/godot-card-game-framework4`
- **Vizsgált branch:** `main`
- **Vizsgált commit:** `18c4bb376304ac57ceb1b76bff3046b226bc054f`
- **Vizsgált merge:** PR #2 – `Catching Up`
- **Projektfájl szerinti Godot-verzió:** 4.2
- **CI-konfiguráció szerinti Godot-verzió:** 4.2.1
- **Nyelv:** GDScript
- **Kódbázis eredete:** a `db0/godot-card-game-framework` 2.2-es rendszerének Godot 4-es konverziója
- **Licenc:** GNU AGPL v3
- **AETERNA összehasonlítási bázis:** az aktuális C# authoritative engine-, contract-, runtime-package- és Godot-bridge rendszer
- **Vizsgálati korlát:** helyi Godot 4.2.1 import, GUT-futtatás és export ebben a körben nem történt
- **CI-bizonyíték:** a vizsgált commitnál nem volt elérhető összesített státusz vagy kapcsolt workflow run
- **Elsődleges AETERNA-érték:** Godot 3 → 4 migrációs jegyzék, Card/Hand/Pile/Target presentation és portolási hibakockázatok
- **Elsődleges AETERNA-kockázat:** az eredeti scene-node-alapú rules authority teljes egészében megmaradt, miközben a port bizonyítottan még konverziós javításokat és nyitott FIXME/TODO pontokat tartalmaz

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Projekt neve | Godot Card Game Framework 4 |
| Repository | `kptmn/godot-card-game-framework4` |
| Default branch | `main` |
| Vizsgált commit | `18c4bb376304ac57ceb1b76bff3046b226bc054f` |
| Repository állapot | nyilvános, nem archivált |
| Projektfájl | Godot 4.2 |
| CI | Godot 4.2.1 GUT + HTML5 export |
| Nyelv | GDScript |
| Fő card node | `Card extends Area2D` |
| Központi autoload | `cfc` / `CFControl.gd` |
| Kártyaadatok | GDScript dictionaryk |
| Képességrendszer | dictionary-alapú ScriptingEngine |
| Tesztek | Godot Unit Test / GUT konverzió |
| Multiplayer | nem bizonyított |
| Licenc | AGPL-3.0 |
| AETERNA-prioritás | P0 – Godot 4 portolási és presentation referencia |
| Közvetlen integráció | elutasítandó |

# 2. Vezetői összefoglaló

A repository nem önállóan tervezett új Godot 4 kártyajáték-engine, hanem az elemzett
`db0/godot-card-game-framework` Godot 4.2-re portolt változata.

A port:

- átírja a Godot 3 szintaxist Godot 4-re;
- `Reference` helyett `RefCounted` típust használ;
- `export` helyett `@export` mezőket használ;
- `yield` helyett `await` szerkezeteket vezet be;
- `instance()` helyett `instantiate()` hívásokat használ;
- a régi Tween node-rendszert SceneTreeTween/WeakRef megoldásokkal próbálja kiváltani;
- frissíti a CI-t Godot 4.2.1-re;
- megőrzi az eredeti Card, CardContainer, Board, `cfc`, NMAP és ScriptingEngine
  architektúrát.

A port ezért nem oldja meg az eredeti framework AETERNA-szempontú fő problémáit:

```text
Card scene-node
├── presentation state
├── rules state
├── input
├── target
├── card data
├── effect dictionary
├── tokenek
├── attachment
└── ScriptingEngine indítás
```

Az AETERNA számára a repository legfontosabb tanulsága:

> egy erősen összefonódott Godot 3 framework Godot 4-re portolása sok technikai
> javítást igényel, de ettől a rules authority határa nem válik jobbá.

A projekt használható:

- Godot 4 portolási ellenőrzőlistához;
- tween- és signal-migráció megértéséhez;
- kártya-UI viselkedések katalogizálásához;
- import/parse/runtime smoke gate tervezéséhez;
- annak bizonyítására, hogy az AETERNA C# engine és Godot view szétválasztása helyes döntés.

Nem használható:

- authoritative rules engine-ként;
- C# engine helyett;
- közvetlen addonként;
- multiplayer authorityként;
- licenckockázat nélküli dependencyként;
- bizonyítottan stabil Godot 4 frameworkként.

# 3. Kapcsolat a db0 eredeti frameworkkel

## 3.1 Repository-szintű státusz

A `kptmn/godot-card-game-framework4` külön GitHub repository és külön commit-történet,
ezért külön forrásrekordként kezelendő.

## 3.2 Implementációs leszármazás

A source audit alapján azonban a tartalma a db0 framework közvetlen konverziója:

- a README változatlanul `Godot Card Game Framework 2.2` címet használ;
- a README badge-je az eredeti `db0/godot-card-game-framework` repositoryra mutat;
- a wiki- és közösségi linkek az eredeti projekthez tartoznak;
- a Card, CardContainer, Board, ScriptingEngine és CFControl szerkezete az eredeti
  frameworkből származik;
- a commitok jelentős része kifejezetten „3→4 fixes” és „conversion” jellegű;
- a legfrissebb vizsgált commit egy `conversion` branchből készült merge.

A nyilvántartási helyes kapcsolat:

```text
db0/godot-card-game-framework
├── eredeti Godot 3.4 / GDScript framework
├── linyangqi/godot-card-game-framework-gd4
│   └── külön Godot 4 portkísérlet
└── kptmn/godot-card-game-framework4
    └── külön repositoryban fenntartott Godot 4.2 konverzió
```

A rekordokat nem kell összevonni, de a kptmn projekt nem tekinthető független
architekturális találmánynak.

# 4. Dokumentációs állapot

## 4.1 README

A README:

- 2.2 verziót jelöl;
- az eredeti db0 projekt badge-jét használja;
- az eredeti framework feature-listáját ismétli;
- az eredeti wikihez és közösségi csatornákhoz irányít;
- AGPL-3.0 licencet jelez;
- nem ad külön Godot 4 portstátuszt;
- nem sorolja fel a konverzió ismert hibáit;
- nem közöl PASS tesztmátrixot;
- nem közöl támogatott Godot 4 minorverziókat.

Ezért a README funkciólistája az eredeti framework képességcéljait mutatja, nem pedig
önmagában a Godot 4 port működési bizonyítékát.

## 4.2 INSTALL

Az install guide továbbra is az eredeti beépítési modellt írja elő:

- `src` mappa bemásolása;
- `cfc` singleton;
- CardTemplate öröklése;
- `cfc.NMAP` használata;
- szoros scene-node struktúra;
- core scene-ek módosításának kerülése.

A dokumentum saját maga is jelzi, hogy a Card és Hand node-elrendezése szorosan
be van drótozva a kódba.

AETERNA számára ez további érv a clean-room, kompozícióalapú view-réteg mellett.

# 5. Godot 4 technológiai konverzió

## 5.1 Projektfájl

A `project.godot`:

```text
config_version=5
config/features=PackedStringArray("4.2")
```

A projekt neve:

```text
(new)Card Game Framework
```

A `cfc` autoload megmaradt.

A GUT plugin engedélyezett.

## 5.2 Fő konverziós minták

| Godot 3 minta | Godot 4 portminta |
|---|---|
| `Reference` | `RefCounted` |
| `export var` | `@export var` |
| `setget` | property getter/setter |
| `yield(signal)` | `await signal` |
| `instance()` | `instantiate()` |
| régi Tween node | `create_tween()` |
| közvetlen Tween referencia | több helyen `WeakRef` |
| `doubleclick` | `double_click` |
| `raise()` | `move_to_front()` |
| régi connect | Callable vagy direkt callable |
| OS idő | `Time.get_ticks_msec()` |

Ezek jó migrációs inventoryt adnak, de nem jelentenek automatikus működési paritást.

# 6. A port készültségének bizonyítékai

## 6.1 Pozitív bizonyítékok

- a projektfájl már Godot 4.2;
- a CI Godot 4.2.1-et céloz;
- a GUT teszteket Godot 4 szintaxisra módosították;
- a forrás nagy része parse-szinten konvertálva van;
- a legfrissebb merge jelentős Tween-, signal- és await-javításokat tartalmaz;
- a tesztfájlokban Godot 4-es `await` és SceneTreeTween-kezelés szerepel;
- a main workflow a teszt után exportlépést tartalmaz.

## 6.2 Negatív vagy hiányzó bizonyítékok

- a vizsgált commitnál nem volt elérhető combined status;
- nem volt kapcsolt workflow run;
- nincs rögzített PASS tesztösszegzés;
- egy korábbi commit üzenete szerint a legtöbb teszt már lefutott, de nem feltétlenül PASS;
- a ScriptingEngineben nyitott FIXME van a `previous_subjects` priming körül;
- a CardTemplate-ben TODO van a duplikált card front/back child index körül;
- a CardTemplate-ben FIXME jelzi, hogy egyes duplikált elemek `card_front` nélkül elakadhatnak;
- több Tween-megoldás WeakRef workaroundra épül;
- a dokumentáció nem közöl támogatottsági mátrixot;
- a külön `gut.yml` csak a `conversion` branch pushaira fut;
- az egyik CI action `@main` referenciát használ, nem rögzített commitot.

A forrás alapján a projekt státusza:

```text
Godot 4 portkísérlet / migrációs munkaváltozat
```

és nem:

```text
bizonyítottan stabil production framework
```

# 7. Card osztály Godot 4-ben

A Card továbbra is:

```gdscript
class_name Card
extends Area2D
```

A CardState továbbra is presentation-állapotokat és rules-helyzetet vegyít:

- kéz;
- fókusz;
- drag;
- board;
- pile;
- popup;
- preview;
- deckbuilder.

A port a szintaxist módosítja, de a felelősségeket nem választja szét.

## 7.1 Getter/setter workaroundok

A Card több privát mezőt vezet be a Godot 4 setterkorlátok megkerülésére:

- `_is_viewed`;
- `_card_rotation`;
- `_canonical_name`;
- `_card_size`;
- `_is_faceup`.

Ez önmagában legitim portolási megoldás lehet, de mutatja, hogy a régi API közvetlen
átírása sok kompatibilitási réteget igényel.

## 7.2 Input és rules összekapcsolása

A double click továbbra is közvetlenül meghívja az `execute_scripts()` metódust.

A drag továbbra is:

- globális `cfc.card_drag_ongoing` állapotot ír;
- scene-node targetet választ;
- közvetlen `move_to()` hívást indít;
- rules zónát a vizuális parentből és CardState-ből következtet.

Ez AETERNA-ban továbbra sem elfogadható authority-határ.

# 8. Tween-konverzió

A Godot 4 port egyik legnehezebb része a Tween-kezelés.

## 8.1 Megfigyelt megoldás

A Card:

- `WeakRef` objektumban tárolja a tweent;
- `create_tween()` hívással készít új tweent;
- szükség esetén `kill()` hívást használ;
- több helyen `await tween.finished` szerkezetet alkalmaz;
- stuck tween figyelést tart fenn.

## 8.2 Nyitott kockázatok

A forrásban:

- TODO jelzi a duplikált card front child index problémáját;
- FIXME jelzi, hogy a duplikátumok front/back referenciái hibásak lehetnek;
- több helyen eltérő módon ellenőrzik a Tween futását;
- a tesztek egy része közvetlen Tweenre, más része WeakRefre számít;
- a merge diffben több korábbi tween await ki lett kapcsolva vagy átírva.

AETERNA-tanulság:

```text
Engine transition completion
≠
Animation completion
```

A C# engine action nem várhat Godot Tweenre.

A Godot oldalon külön:

```text
AnimationCoordinator
- event queue
- tween ownership
- cancellation
- stale animation guard
- view disposal
- no rules mutation
```

szükséges.

# 9. ScriptingEngine Godot 4-ben

A ScriptingEngine:

```gdscript
class_name ScriptingEngine
extends RefCounted
```

Ez a `Reference → RefCounted` konverzió technikailag helyes irány.

Az architektúra azonban változatlan:

- task dictionary;
- string opcode;
- ScriptTask;
- raw Node/Card subject;
- globális `cfc.NMAP`;
- Card method mutation;
- temporary modifier;
- cost dry-run;
- UI selection;
- signal/await alapú folytatás.

## 9.1 Nyitott FIXME

A forrás kifejezetten jelzi:

- `prev_subjects` néha nincs hozzárendelve;
- a script priming nem mindig történik megfelelően;
- a script nem feltétlenül válik valid állapotúvá.

Ez a `previous` subject lánc, többfázisú költség és target-alapú effectek szempontjából
kritikus terület.

## 9.2 Dinamikus call és await

A port továbbra is:

```text
call(script.script_name, script)
```

mintát használ.

Az eredményt ezután `await` feldolgozásnak adja át.

Mivel a taskfüggvények egy része azonnali integer returnt, más része aszinkron folyamatot
adhat, ezt helyi Godot 4 futtatással külön bizonyítani kell.

A source önmagában nem igazolja minden task szinkron/aszinkron paritását.

## 9.3 AETERNA-következtetés

A port nem alkalmas annak bizonyítására, hogy a dictionary ScriptingEngine biztonságosan
átvehető Godot 4-ben.

A használható tanulság továbbra is csak a szemantikai modell:

- task;
- selector;
- filter;
- cost;
- choice;
- selection;
- stored result;
- nested effect.

A végrehajtás AETERNA typed C# instruction legyen.

# 10. Cost dry-run

A Card továbbra is:

1. triggerfiltert értékel;
2. állapot alapján `hand`/`board`/`pile` scriptágat választ;
3. opcionális popupot nyit;
4. multiple-choice popupot nyit;
5. COST_CHECK futást indít;
6. siker esetén normál futást indít;
7. sikertelenség esetén ELSE ágat indíthat.

A Godot 4 port ezt `await` szerkezetekkel aktualizálta, de nem vezette be:

- immutable preflight snapshotot;
- state versiont;
- resolution plant;
- final revalidationt;
- atomic commitot;
- rollbackot;
- typed EngineEventet.

Az eredeti framework kritikája ezért teljes egészében érvényes marad.

# 11. CFControl és globális authority

A `cfc` autoload továbbra is tárol:

- card definitionöket;
- card scripteket;
- NMAP-et;
- dragállapotot;
- RNG-t;
- alterant cache-t;
- temporary modifiereket;
- scripting engine referenciát;
- utility példányt;
- tesztállapotot;
- beállításokat.

A Godot 4 port csak API-szinten módosította ezt.

## 11.1 Thread-kezelés

A source threadet indít a scriptbetöltéshez, majd közvetlenül `wait_to_finish()` hívást végez.

Ez a konverzió jelen formájában elveszítheti az eredeti háttérbetöltés előnyét, és
külön teljesítményvizsgálatot igényel.

## 11.2 Definition merge

A card definitionök továbbra is névkulcs alapján kerülnek közös dictionarybe:

```text
combined_sets[card_name] = set_def.CARDS[card_name]
```

Duplicate ID diagnosztika nincs.

AETERNA runtime package-ben továbbra is stabil ID és duplicate-failure szükséges.

# 12. CI és tesztelés

## 12.1 Main workflow

A main push workflow:

- `actions/checkout@v4`;
- külső `db0/godot-tester` repository checkout;
- Godot 4.2.1 GUT;
- `max-fails: 0`;
- HTML5 export;
- itch.io upload.

## 12.2 Külön gut workflow

A külön `gut.yml`:

- csak `conversion` branch pushra fut;
- `ceceppa/godot-gut-ci@main` actiont használ;
- Godot 4.2-t céloz.

## 12.3 Bizonyítási hiány

A workflow-fájl létezése nem azonos a PASS bizonyítékkal.

A vizsgált commitnál:

- combined status nem volt;
- PR workflow run nem volt elérhető;
- teszteredmény artifact nem volt ellenőrizhető.

A projektet ezért nem lehet PASS-ként minősíteni.

## 12.4 AETERNA CI-tanulság

Szükséges gate-ek:

```text
dotnet build
→ C# engine tests
→ content compiler tests
→ Godot 4 import/parse
→ GUT/GdUnit view tests
→ bridge smoke
→ export
→ artifact launch smoke
```

Minden actiont commit SHA-ra kell pinelni vagy ellenőrzött verzióhoz kötni.

# 13. Tesztállomány

A costtesztek Godot 4-re portolt formában továbbra is vizsgálják:

- self rotation cost;
- target cost;
- multiple cost;
- flip cost;
- token cost;
- property cost.

A tesztekben azonban vegyes Tween-kezelés látható:

- `_flip_tween`;
- `_tween.get_ref()`;
- `is_running()` és `is_running`;
- feltételes await.

Ez további jel arra, hogy a port célja jelenleg a régi tesztkorpusznak a Godot 4
runtimehoz igazítása, nem egy új engine contract kialakítása.

# 14. Determinizmus

A `cfc.game_rng` és seedmodell megmaradt.

Ez pozitív, mert:

- a rules random külön kezelhető;
- azonos seed reprodukálható;
- a Godot globális RNG-től részben elválasztható.

A port nem ad új bizonyítékot:

- replayre;
- state hashre;
- event logra;
- RNG decision eventre;
- multiplayer parityre.

A ScriptingEngine snapshot ID továbbra sem az AETERNA-féle determinisztikus event identity.

# 15. Hidden information és multiplayer

A projekt továbbra is presentation-szinten kezel face-down kártyákat.

Nem látható:

- viewer-specific projection;
- owner/opponent snapshot;
- opaque hidden reference;
- authority server;
- ActionRequest version;
- reject-no-mutation;
- network event stream;
- hidden deck order protection.

A Godot 4 port ebből a szempontból nem hoz előrelépést az eredeti frameworkhez képest.

# 16. Licenc

A repository GNU AGPL v3 licencet tartalmaz.

Ez az eredeti frameworkkel azonos közvetlen felhasználási kockázatot jelent.

AETERNA-döntés:

- közvetlen dependency: nem;
- addonként beemelés: nem;
- scene vagy script másolása: nem;
- fork használata production kliensben: nem;
- clean-room UX és migrációs elv: igen;
- feature inventory felhasználása: igen;
- saját Godot 4/C# view implementáció: igen.

# 17. Összehasonlítás az eredeti db0 frameworkkel

| Terület | db0 Godot 3 | kptmn Godot 4 port | AETERNA értékelés |
|---|---|---|---|
| Godot verzió | 3.4.x | 4.2 / 4.2.1 | technikailag frissebb |
| Nyelv | GDScript | GDScript | C# authorityhoz nem közelít |
| Card architecture | scene + rules + input | változatlan | továbbra is elutasítandó |
| `cfc` singleton | igen | igen | továbbra is authority-kockázat |
| NMAP | igen | igen | továbbra is scene-node registry |
| ScriptingEngine | dictionary | dictionary | typed AST továbbra is hiányzik |
| cost dry-run | igen | igen | továbbra sem tranzakció |
| target/selection | Godot UI | Godot 4 UI | csak presentation minta |
| Tween | régi Tween node | SceneTreeTween/WeakRef | értékes migrációs tanulság |
| async | yield | await | portolási minta, parity nem bizonyított |
| tesztek | GUT | GUT 4 port | PASS nem bizonyított |
| CI | Godot 3.4 | Godot 4.2.1 | frissebb, de futásbizonyíték hiányzik |
| licenc | AGPL | AGPL | változatlan kockázat |
| új engine insight | magas az első auditnál | alacsony | fő érték a portkockázat |

# 18. Erősségek az AETERNA szempontjából

1. Valós, nagy Godot 3 → 4 portpélda.
2. Átfogó Card/Hand/Pile/Board UI-rendszer.
3. Godot 4 `@export` migráció.
4. Godot 4 property getter/setter migráció.
5. `Reference → RefCounted` migráció.
6. `yield → await` migráció.
7. `instance → instantiate` migráció.
8. Tween API változásainak valós problémái.
9. Signal connect migráció.
10. Godot 4.2.1 CI-konfiguráció.
11. Régi GUT tesztkorpusz portja.
12. Az eredeti effect DSL szemantikája megmaradt.
13. Közvetlen összehasonlítási alap a db0 audithoz.
14. Jó ellenpélda a scene/rules coupling portköltségére.
15. Hasznos import-, parse-, runtime- és export-gate tervezéshez.

# 19. Gyengeségek és kockázatok

1. Nem önálló új architektúra.
2. README nem portspecifikus.
3. README badge az eredeti repositoryt mutatja.
4. Nincs támogatottsági mátrix.
5. Nincs PASS tesztösszegzés.
6. Nincs elérhető combined status a vizsgált commitnál.
7. Nincs elérhető workflow run a vizsgált merge-nél.
8. Korábbi commit szerint a tesztek nem feltétlenül passzoltak.
9. Nyitott ScriptingEngine FIXME.
10. Nyitott Card duplicate TODO.
11. Nyitott `card_front` FIXME.
12. WeakRef Tween workaroundok.
13. Vegyes Tween-kezelés a tesztekben.
14. Dinamikus string task dispatch.
15. Raw Node/Card subjectek.
16. Globális `cfc`.
17. Globális NMAP.
18. Card node authority.
19. Visual CardState → rules scriptág.
20. UI await a rules flowban.
21. Közvetlen scene-node mutation.
22. Nincs atomic transition.
23. Nincs state version.
24. Nincs viewer projection.
25. Nincs authoritative multiplayer.
26. Nincs replay/event log proof.
27. Duplicate card name felülírás.
28. Thread indítás után azonnali wait.
29. Külön workflow csak conversion branchre.
30. Unpinned `@main` action.
31. AGPL.
32. GDScript authority nem illeszkedik az AETERNA C# irányához.

# 20. AETERNA számára átvehető elvek

## 20.1 Godot 4 migrációs checklist

- scene import;
- node type changes;
- signal API;
- Tween lifecycle;
- coroutine/await parity;
- property setter semantics;
- duplicate/clone behavior;
- SubViewport behavior;
- input event field changes;
- test await behavior;
- CI Godot minorversion pin.

## 20.2 Presentation komponensek funkciólistája

- CardView;
- HandView;
- PileView;
- TargetingArrow;
- AttachmentView;
- CardPreview;
- CardLibrary;
- DeckBuilder;
- GridView;
- TokenDrawer.

## 20.3 Portbizonyítás

Minden Godot-verzióváltásnál külön kell bizonyítani:

```text
parse
→ scene instantiate
→ signal wiring
→ input
→ tween
→ cancellation
→ duplicate
→ viewport
→ export
```

## 20.4 Rules–animation szétválasztás

A port legnagyobb negatív tanulsága:

```text
await animation
```

nem lehet az authoritative transition része.

# 21. Amit nem szabad átvenni

1. A teljes framework forkként.
2. A CardTemplate rules actor szerepe.
3. A `cfc` rules authority szerepe.
4. Az NMAP zónaregiszter.
5. A visual state alapú rules dispatch.
6. A dictionary opcode közvetlen Godot futtatása.
7. A raw Card/Node target.
8. Az UI popup a rules evaluatorban.
9. A Tween completion mint engine continuation.
10. A scene child order mint authoritative sorrend.
11. A canonical name mint definition ID.
12. A duplicate dictionary merge diagnosztika nélkül.
13. A thread + azonnali wait minta.
14. Az unpinned CI action.
15. A README-állítás működési bizonyítékként.
16. Az AGPL kódmásolás.

# 22. Javasolt AETERNA Godot 4 szerkezet

```text
Aeterna.Engine
├── MatchState
├── EngineSession
├── CostPreflight
├── ResolutionQueue
├── SelectionContract
├── EngineEvent
└── ProjectionService
        │
        ▼
Aeterna.GodotBridge
├── ActionRequest adapter
├── snapshot adapter
├── event adapter
├── stale-view guard
└── visibility-safe DTO
        │
        ▼
Aeterna.Godot
├── CardView
├── HandView
├── PileView
├── DomainGridView
├── TargetingArrow
├── SelectionWindow
├── CardLibrary
├── DeckBuilder
└── AnimationCoordinator
```

A view:

- nem tárol rules state-et;
- nem futtat ability dictionaryt;
- nem mozgat authoritative kártyát;
- nem választ legal targetet;
- nem számol költséget;
- nem blokkolja az engine-t Tweenre várva.

# 23. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | Godot 4 import/parse CI gate | CI | P0 |
| 2 | Godot minorverzió pin | CI | P0 |
| 3 | Action commit SHA pin | CI | P0 |
| 4 | CardView clean-room implementáció | Godot | P0 |
| 5 | HandView/PileView snapshotból | Godot | P0 |
| 6 | Tween ownership és cancellation service | Godot | P0 |
| 7 | Engine transitiontől független animáció | Bridge/Godot | P0 |
| 8 | View duplicate smoke test | Tests | P1 |
| 9 | SubViewport card preview smoke test | Tests | P1 |
| 10 | TargetingArrow candidate contractból | Bridge/Godot | P1 |
| 11 | SelectionWindow engine contractból | Bridge/Godot | P1 |
| 12 | Godot view state ne vezéreljen rules dispatchot | Architecture | P0 |
| 13 | Typed effect compiler maradjon C# oldalon | Engine/Runtime | P0 |
| 14 | Runtime package stable ID | Runtime | P0 |
| 15 | Duplicate card ID hard failure | Tooling | P0 |
| 16 | Engine RNG és visual RNG külön | Engine/Godot | P0 |
| 17 | Godot export launch smoke | CI | P0 |
| 18 | AGPL direct dependency tiltás | License | P0 |
| 19 | Portmigrációs checklist dokumentálása | Docs | P1 |
| 20 | db0 és kptmn elemzések közös effect primitive mappingje | Learning | P1 |

# 24. Bizonyítékjegyzék

| ID | Állítás | Forrás |
|---|---|---|
| E-001 | default branch `main`, repository nem archivált | GitHub repository metadata |
| E-002 | vizsgált HEAD `18c4bb...` | GitHub commit search |
| E-003 | legfrissebb merge `conversion` branchből | PR #2 / merge commit |
| E-004 | README továbbra is 2.2 | `README.md` |
| E-005 | README badge az eredeti db0 repositoryra mutat | `README.md` |
| E-006 | eredeti feature-lista megmaradt | `README.md` |
| E-007 | Godot 4.2 projekt | `project.godot` |
| E-008 | `cfc` autoload megmaradt | `project.godot` |
| E-009 | GUT plugin engedélyezett | `project.godot` |
| E-010 | CI Godot 4.2.1 | `.github/workflows/main.yml` |
| E-011 | HTML5 export Godot 4.2.1 | `.github/workflows/main.yml` |
| E-012 | külön gut workflow conversion branchre | `.github/workflows/gut.yml` |
| E-013 | Card továbbra is Area2D | `CardTemplate.gd` |
| E-014 | CardState struktúra megmaradt | `CardTemplate.gd` |
| E-015 | `@export` és Godot 4 property conversion | `CardTemplate.gd` |
| E-016 | WeakRef Tween | `CardTemplate.gd` |
| E-017 | duplicate child index TODO | `CardTemplate.gd` |
| E-018 | card_front duplicate FIXME | merge diff / `CardTemplate.gd` |
| E-019 | input közvetlen execute_scripts | `CardTemplate.gd` |
| E-020 | Card state alapján hand/board/pile dispatch | `CardTemplate.gd` |
| E-021 | ScriptingEngine RefCounted | `ScriptingEngine.gd` |
| E-022 | cost dry-run megmaradt | `ScriptingEngine.gd` / `CardTemplate.gd` |
| E-023 | previous subject priming FIXME | `ScriptingEngine.gd` |
| E-024 | string method dispatch | `ScriptingEngine.gd` |
| E-025 | globális NMAP/temp modifier | `ScriptingEngine.gd` |
| E-026 | `cfc` globális állapot | `CFControl.gd` |
| E-027 | thread után wait_to_finish | `CFControl.gd` |
| E-028 | card name dictionary merge | `CFControl.gd` |
| E-029 | Godot 4-re portolt cost tesztek | `test_scripting_engine_costs.gd` |
| E-030 | workflow run hiány a vizsgált commitnál | GitHub workflow query |
| E-031 | combined status hiány | GitHub status query |
| E-032 | korábbi commit: tesztek lefutnak, de nem feltétlen passzolnak | commit `a525aaa...` |
| E-033 | AGPL-3.0 | `LICENSE` |
| E-034 | szoros scene layout dokumentált | `INSTALL.md` |
| E-035 | NMAP installmodell dokumentált | `INSTALL.md` |

# 25. Nyitott kérdések

1. Importálható-e a HEAD hiba nélkül Godot 4.2.1 alatt?
2. Hány parser warning és error van?
3. Lefut-e a demo MainMenu?
4. Minden Card scene példányosítható?
5. Működik-e a SubViewport preview?
6. Reprodukálható-e a duplicate card front TODO?
7. Reprodukálható-e a `card_front` nélküli elakadás?
8. Mely Tween utak ragadnak be?
9. Működik-e minden `await retcode` tasktípusnál?
10. Mely ScriptingEngine tesztek PASS?
11. Mely tesztek FAIL?
12. Mely tesztek timeoutolnak?
13. A `previous_subject` FIXME mely scenariókat töri?
14. A multiple-cost targetek működnek-e?
15. A nested taskok működnek-e?
16. A Card Library betöltődik-e?
17. A Deck Builder használható-e?
18. A HTML5 export elkészül-e?
19. Az export elindul-e böngészőben?
20. A thread + wait blokkolja-e az indulást?
21. A game RNG tesztek PASS?
22. A scene signalok mind megfelelően kapcsolódnak-e?
23. A port mely Godot 4 minorverziókon működik?
24. Godot 4.3/4.4/4.5 alatt milyen regressziók vannak?
25. A README miért nem portspecifikus?
26. A CI jelenleg ténylegesen aktív-e?
27. Mely actionök pinelhetők stabil SHA-ra?
28. Van-e aktív karbantartási terv?
29. A port mely részei tekinthetők befejezettnek?
30. A Pali multiplayer projekt milyen további Godot authority-mintát ad?

# 26. Következő vizsgálati lépések

## 26.1 Codex nélkül

1. helyi origin és HEAD ellenőrzés;
2. Godot 4.2.1 import;
3. parser error/warning export;
4. GUT teljes futtatás;
5. PASS/FAIL/timeout lista;
6. demo smoke;
7. Card drag/focus smoke;
8. target arrow smoke;
9. cost script smoke;
10. previous subject scenario;
11. duplicate/SubViewport scenario;
12. Card Library smoke;
13. Deck Builder smoke;
14. HTML5 export;
15. export launch smoke;
16. licenc- és assetinventár.

## 26.2 Később Codexszel gyorsítható

1. TODO/FIXME inventory;
2. Godot 3 és Godot 4 source-diff osztályonként;
3. GUT failure triage;
4. coroutine/await audit;
5. Tween ownership audit;
6. signal connect audit;
7. CardView clean-room proof;
8. AETERNA Godot import smoke suite;
9. effect primitive mapping;
10. migration checklist automatizálás.

# 27. Végső minősítés

- **Godot 4 portolási tanulási érték:** magas
- **Godot presentation érték:** magas, de stabilitása nem bizonyított
- **Effect DSL új tanulási érték:** alacsony; nagyrészt az eredeti db0 audit ismétlése
- **Authoritative engine érték:** nagyon alacsony
- **C# engine-illeszkedés:** nagyon alacsony
- **Tesztbizonyíték:** hiányos
- **CI-konfiguráció:** létezik, de PASS nem bizonyított
- **Modern Godot API:** részlegesen alkalmazott
- **Portkészültség:** munkaváltozat
- **Licenc-kompatibilitás:** közvetlen használathoz alacsony
- **Közvetlen dependency:** elutasítandó
- **Clean-room UI/migrációs inspiráció:** ajánlott
- **Legfontosabb AETERNA-tanulság:** a Godot 4-re portolás nem javítja automatikusan az
  authority-határt; a C# engine és Godot view szétválasztása továbbra is kötelező
- **Következő learning cél:** `rametta/Pali`

# 28. Változásnapló

## 0.1 – 2026-07-25

- elkészült a `kptmn/godot-card-game-framework4` első teljes source auditja;
- rögzítésre került a vizsgált commit és a PR #2 merge;
- pontosításra került, hogy a repository külön rekord, de implementációsan a db0
  framework Godot 4 konverziója;
- feldolgozásra került a Godot 4.2 projektállapot;
- feldolgozásra került a Godot 4.2.1 CI;
- összevetés készült az eredeti db0 frameworkkel;
- feldolgozásra kerültek a `Reference → RefCounted`, `yield → await`,
  `instance → instantiate`, Tween és property migrációs minták;
- rögzítésre kerültek a nyitott ScriptingEngine és Card duplicate hibakockázatok;
- rögzítésre került a hiányzó PASS workflow-bizonyíték;
- elutasításra került a közvetlen AETERNA-integráció;
- elkészült a Godot 4 clean-room presentation és CI-gate javaslat;
- a következő kijelölt projekt `rametta/Pali`.
