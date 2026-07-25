# AETERNA – Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-25
- **Státusz:** repository-forrásokra épülő első teljes eredet-, UI-, shader-, input-, animation-, card-model- és authority-elemzés
- **Fő elemzési fájl:** `learning/analyses/fulafu-ai__godot4-fake3d-card-game-ui-demo.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Repository:** `Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo`
- **Stabil upstream URL:** `https://github.com/Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo`
- **Vizsgált branch:** `main`
- **Vizsgált commit:** `14c07f3983b6c22d9d8747dc3cbb9e3a870c895f`
- **Vizsgált projektmappa:** `Demo 0.2`
- **Vizsgált commit/projekt dátuma:** 2026-01-24
- **Technológiai alap:** Godot 4.5 / GDScript / Forward Plus / CanvasItem shaderek
- **Repository licence:** GPL-3.0
- **Kártyagrafika licence:** Screaming Brain Studios – CC0 1.0 / Public Domain
- **Alap perspective shader jelölése:** MIT fejléc
- **Külső vizuális inspirációk:** Balatro-szerű interakció; Godot 2D perspective shader; külső oktatóvideók
- **AETERNA összehasonlítási bázis:** az aktuális C# authoritative engine-, runtime-package-, contract-, legal-action-, viewer-projection- és Godot-bridge rendszer
- **Összehasonlítási szabály:** kizárólag az AETERNA rendszeréhez mérve
- **Vizsgálati korlát:** helyi Godot 4.5 import, teljes futtatás, shaderprofiler, gesture-reprodukció, export és vizuális összehasonlítás ebben a körben nem történt
- **CI-bizonyíték:** a vizsgált commitnál nincs GitHub status check vagy kapcsolt workflow run
- **Elsődleges AETERNA-érték:** ál-3D CanvasItem-kártya, front/back shader, dinamikus árnyék, selection flash, íves kéz, többkártyás drag, dobozos kijelölés, tween- és state-machine alapú presentation
- **Elsődleges AETERNA-kockázat:** a Card/Deck modellek, a rules manager, a scene-node UI-state és az animációs folyamat kölcsönösen módosítják egymást; nincs engine-owned MatchState, stable instance ID, state version, action contract vagy replay

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Repository | `Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo` |
| Default branch | `main` |
| Vizsgált commit | `14c07f3983b6c22d9d8747dc3cbb9e3a870c895f` |
| Commitüzenet | Demo 0.2 kiadás |
| Repository állapot | nyilvános, nem archivált |
| GitHub-fork jelölés | nincs |
| Commitok száma a vizsgálatkor | 5 |
| Projektverziók | Demo 0.1, Demo 0.11, Demo 0.2 |
| Godot | 4.5 |
| Renderer | Forward Plus |
| Nyelv | GDScript |
| Fő kártyamodell | `Card extends Resource` |
| Kártyaspecializáció | `PokerCard` |
| Paklimodell | `Deck extends Resource` |
| Kártyanézet | `CardUI extends Control` |
| Kéz/zóna nézet | `CardTable`, `HandTable`, `CardPile` |
| UI-state-ek | Idle, Display, Dragging, Destroy, Following, Playing, NoInteract |
| Szabályréteg | `PokerRuleManager` + `PokerRule` + `DoudizhuPokerRule` |
| Támogatott szabály | Dou Dizhu / 斗地主 |
| Adatforrás | `.tres` dictionary; CSV/XLSX authoringsegédek |
| Kártyakészlet | 52-indexes standard francia csomag |
| Joker-szabály | a rules code 54 lapos/Joker fogalmat is vár |
| Input | egér, görgő, számbillentyűk, Space |
| Többkártyás drag | igen |
| Téglalapos kijelölés | igen |
| Pile animation | igen |
| Rules authority | Godot Resource + node state |
| Multiplayer | nem talált |
| Hidden-information projection | nem talált |
| Tesztek | dedikált automatizált tesztcsomag nem talált |
| CI | nem talált |
| Repository licence | GPL-3.0 |
| Assetlicenc | CC0 |
| AETERNA-prioritás | P1 – kiemelt Godot presentation referencia |
| Közvetlen dependency | elutasítandó |
| Clean-room vizuális inspiráció | ajánlott |

# 2. Vezetői összefoglaló

A projekt a címénél többet tartalmaz. Nem csupán shaderbemutató, hanem:

- Card és Deck Resource-modell;
- kártya–UI egy-egy kapcsolat;
- CardUI state machine;
- hover- és mouse-follow perspective;
- front/back lapforgatás;
- shaderes árnyék;
- selection flash;
- dissolve;
- íves kéz;
- többkártyás drag;
- görgős fókusz;
- dobozos kijelölés;
- draw/discard pile;
- Dou Dizhu kombinációfelismerés;
- Space alapú kijátszás.

A presentation minősége és ötletgazdagsága magasabb, mint az architekturális
elkülönítésé.

A tényleges működési lánc:

```text
Card Resource
↕ WeakRef
CardUI Control
↕ state machine
CardTable / CardPile Deck Resource
↕ global Event autoload
PokerRuleManager
↕
PokerHand.play()
↕
Card.play() + CardUI animation + késleltetett discard
```

Ez azt jelenti, hogy:

- a domainmodell ismeri a UI-ját;
- a UI módosítja a Deck modellt;
- a szabályeredmény presentation adatot tart;
- a kijátszás egyszerre szabályi és animációs metódus;
- a zónamozgás scene-state-ekből történik;
- a shuffle nem determinisztikus;
- a validáció nem authoritative action contract.

## 2.1 AETERNA-döntés

- **Fake-3D shaderelv:** magas érték
- **Front/back és árnyék shaderfelosztás:** magas érték
- **Selection flash:** magas érték
- **Íves kéz:** magas érték
- **Többkártyás drag:** magas érték
- **Kijelölési UX:** magas érték
- **Presentation state machine:** közepes-magas érték
- **Card/Deck Resource ötlet:** közepes érték
- **Rules manager mint authority:** alacsony érték
- **Zóna- és kijátszásmodell:** alacsony érték
- **Determinism/replay:** alacsony
- **Multiplayer/hidden information:** nem megvalósított
- **Közvetlen kódintegráció:** nem
- **Clean-room vizuális újraimplementáció:** igen

A legfontosabb tanulság:

> a látványos kártyainterakciók önálló Godot presentation-rétegként rendkívül
> értékesek, de soha nem határozhatják meg vagy módosíthatják közvetlenül az
> authoritative kártya-, zóna- vagy szabályállapotot.

# 3. Eredet és provenance

## 3.1 Repository-eredet

A repository:

- önálló GitHub repository;
- nem GitHub-forkként jelölt;
- rövid, ötcommitos történetet tartalmaz;
- egymás után őrzi a Demo 0.1, 0.11 és 0.2 projektmappákat.

Nem bizonyítható, hogy minden technika teljesen eredeti. A szerző maga megjelöli a
vizuális előképeket és külső forrásokat.

## 3.2 Megjelölt inspirációk

A projektleírás szerint:

- Balatro-szerű ál-3D kártyamozgás;
- külső Godot perspective shader;
- oktatóvideók;
- Screaming Brain Studios kártyagrafikák.

Ez korrekt forrásjelölési irány, de AETERNA-integráció előtt komponensenként kell kezelni:

```text
repository kód
shadereredet
módosított shader
grafikai asset
tutorialból átvett elv
```

# 4. Licencrétegek

## 4.1 Repository-kód

A root licenc GPL-3.0.

Közvetlen forrásátvétel ezért az AETERNA jelenlegi licencelési és zárt production
irányához nem javasolt.

## 4.2 Kártyagrafika

A csomagolt Screaming Brain Studios assetek licence:

```text
CC0 1.0 / Public Domain
```

Ez önmagában kedvezőbb, de:

- csak a megjelölt assetkészletre vonatkozik;
- a pontos fájlinventárt továbbra is rögzíteni kell;
- a repository licence nem írja felül az asset külön licencét.

## 4.3 Fake-3D shader

A `fake3d.gdshader` és a shadow-változat fejlécében MIT szerepel.

A `fake3d_flash.gdshader` már módosított/bővített változat, de a fájl elején nem látható
ugyanaz a teljes attribution fejléc.

Ezért közvetlen shaderátvétel előtt:

- eredeti shader szerzőjét;
- eredeti MIT notice-t;
- módosítások szerzőségét;
- kombinált shader licencét

külön kell dokumentálni.

## 4.4 AETERNA-licencdöntés

- teljes repository import: **tiltandó**;
- GDScript másolás: **tiltandó**;
- scene másolás: **tiltandó**;
- módosított flash shader közvetlen másolása: **előzetes licenctisztázás nélkül nem**;
- CC0 kártyagrafika: külön assetinventárral lehetséges, de nem feltétlenül illeszkedik az AETERNA vizuális identitásához;
- matematikai/presentation elvek clean-room implementációja: **ajánlott**.

# 5. Godot-projektállapot

A `project.godot`:

```text
Godot 4.5
Forward Plus
config_version 5
```

Autoloadok:

```text
DataLab
Event
Shake
RuleManager
```

Globális csoportok:

```text
main
selectable
selected
dragger
hand
discard_pile
```

## 5.1 Pozitívum

- modern Godot 4.5;
- typed GDScript több helyen;
- Resource-alapú modell;
- CanvasItem shaderek;
- UID-alapú resourcekapcsolatok;
- resource-local shaderanyagok;
- state machine.

## 5.2 Portabilitási probléma

A projektfájl szerzői gépre mutató abszolút movie-writer útvonalat tartalmaz.

Ez:

- nem futtatási blocker;
- repository-higiéniai probléma;
- lokális felhasználói útvonalat publikál;
- CI és csapatmunka szempontjából kerülendő.

# 6. Card Resource

A `Card` külön Resource.

Tartalmaz:

- `id`;
- front texture;
- back texture;
- current Deck WeakRef;
- CardUI WeakRef;
- play signalokat;
- UI-létrehozó metódust.

## 6.1 Erős gondolat

A kártyaadat és a Control node fizikailag külön objektum.

Ez előrelépés a scene child ordert teljes rules state-ként használó demókhoz képest.

## 6.2 Határsértés

A Card:

- tárolja saját CardUI-ját;
- PackedScene alapján létrehozza a UI-t;
- UI-state-et állít;
- presentation textúrákat tart;
- gameplay signalokat bocsát ki.

Így egyszerre:

```text
runtime card instance
presentation definition
presentation factory
event source
```

## 6.3 AETERNA-felosztás

```text
C# CardDefinition
C# CardInstance
C# CardInstanceId
Godot CardViewModel
Godot CardView
Godot CardViewFactory
```

A CardInstance nem ismerheti a CardView-t.

# 7. Kártyaazonosítás

A `Card.id` string, de:

- módosítható;
- signalon keresztül frissíthető;
- nincs külön definition ID és instance ID;
- a 52 lapos csomag kártyafajtáját jelöli;
- nem garantálja két azonos nyomtatású kártyapéldány külön identitását.

AETERNA minimum:

```text
card_id
card_instance_id
printing_id
owner_player_id
controller_player_id
zone_id
zone_index
```

# 8. Deck Resource

A Deck:

- typed Card tömböt kezel;
- ObservableArrayre épül;
- reference alapján kiszűri az ismételt ugyanazon példányt;
- automatikusan eltávolítja a Cardot a korábbi Deckből;
- add/remove/insert/sort/shuffle műveletet ad;
- WeakReffel visszaírja a membershipet.

## 8.1 Erősségek

- modell nem scene childlista;
- explicit pakliobjektum;
- egy kártyapéldány egyszerre egy Deckben lehet;
- Deck-változási signal;
- rendezés és indexelés.

## 8.2 Kockázatok

- nincs stable Deck/Zone ID;
- nincs owner;
- nincs state version;
- nincs expected source;
- nincs atomic move;
- automatikus cross-deck eltávolítás rejtett side effect;
- az underlying Array kijut a getterből;
- shuffle seed nélküli;
- nincs event/replay;
- invalid index nullt ad diagnosztika nélkül;
- WeakRef membership könnyen stale lehet.

## 8.3 AETERNA-megfelelő

```text
ZoneState
- zone_id
- ordered card_instance_ids
- owner
- visibility policy
- capacity
- version
```

A kártyamozgatás egy EngineTransition része.

# 9. PokerCard

A PokerCard:

- 0–51 indexet használ;
- globális dictionaryből olvas;
- suit és rank alapján assetútvonalat képez;
- véletlenszerű card backet választ;
- id-t és texture-t állít.

## 9.1 Pozitívum

- táblázatvezérelt kártyaadat;
- kis, jól érthető lookup;
- külön specializált Card Resource.

## 9.2 Kockázatok

1. `-1` index 0-ra clampelődik, így hiányos inicializációból érvényesnek látszó lap lesz.
2. A rule code 54 lapos csomagot és Joker 14/15 értékeket vár, miközben a model 52 indexre clampel.
3. A card back minden update-nél újrarandomizálható.
4. Nincs seed/event.
5. A rules mező és assetútvonal közvetlenül összekapcsolódik.
6. Hiányzó dictionary key runtime hibát okozhat.
7. Nincs schema- vagy required-field validáció.

# 10. DataLab és CSV-import

A DataLab runtimeban `.tres` dictionaryt preloadol.

A helper:

- CSV-t dictionaryvé alakít;
- header suffix alapján int/float/bool konverziót végez;
- JSON-t ír és olvas.

## 10.1 Használható authoringelv

```text
column_name_to_int
column_name_to_float
column_name_to_bool
```

gyors prototípus-importnál praktikus.

## 10.2 Production-hiányok

- nincs schema version;
- nincs required column;
- nincs duplicate key error;
- invalid typed value stringként marad;
- nincs row/column diagnosztika;
- nincs enum validation;
- nincs range validation;
- nincs content hash;
- nincs compiler artifact;
- file open guard hiányos.

Az AETERNA Excel/CSV munkaforrásból csak content compiler állíthat elő runtime package-et.

# 11. CardUI scene

A CardUI scene külön rétegeket használ:

```text
CardTexture
CardBackTexture
Shadow
Dissolve material
StateMachine
Collision area
Selection/order labels
```

Minden fontos shaderanyag `resource_local_to_scene`, így a példányonként módosított
uniformok nem feltétlenül szivárognak át más lapokra.

Ez jó Godot-technikai döntés.

# 12. Fake-3D shader

Az alap shader:

- CanvasItem perspektívát szimulál;
- x/y rotation uniformokat használ;
- FOV-t állít;
- backface cullingot támogat;
- UV perspektívatranszformációt végez;
- green-screen színkivágást ad.

## 12.1 AETERNA-érték

- valódi 3D mesh nélkül térbeli lapérzet;
- Control-alapú UI-val kompatibilis;
- front/back TextureRect könnyen animálható;
- hoverkövetéshez alkalmas;
- olcsóbb authoring, mint teljes 3D scene.

## 12.2 Kockázat

- pixelméret-alapú vertexnövelés clippinget és layouttúlnyúlást okozhat;
- FOV szélsőértékeknél torzulás;
- p.z közeli értéknél UV-instabilitás;
- sok külön material és tween GPU/CPU költséget növel;
- green-screen kivágás kártyaképtől függ;
- mobil és Compatibility renderer nincs bizonyítva.

# 13. Front/back megoldás

A CardUI külön front és back TextureRectet tart.

A back y-rotációja 180 fokkal eltolt.

Ez jó minta:

```text
front shader rotation
back shader rotation - 180°
backface culling
```

Előnye:

- nincs textúracsere a flip közepén;
- folyamatos átfordulás;
- front/back külön anyagparaméter;
- face-down state könnyen animálható.

AETERNA-ban ez kizárólag a viewer projection láthatóságát jelenítheti meg.

# 14. Selection flash

A flash shader:

- ki- és bekapcsolható;
- színfiltert támogat;
- pure/rainbow/gradient módot ad;
- mask texture-t használ;
- szög-, intenzitás-, stripe- és sebességparamétert ad;
- a kártyaforgás és a TIME alapján mozgatja a fényt.

## 14.1 Használható

- kijelölt lap;
- célpont;
- rare/foil presentation;
- legal action highlight;
- preview focus;
- hover feedback.

## 14.2 AETERNA-korlát

A flash oka typed UI-state legyen:

```text
Selected
LegalTarget
Hovered
PendingAction
Triggered
RareTreatment
```

Ne egyetlen `use_flash` bool próbálja összevonni a jelentéseket.

# 15. Árnyék shader

A shadow shader:

- ugyanazt a perspective transzformációt követi;
- fekete vagy selected színt ad;
- alpha uniformot használ;
- külön x/y rotationt kap.

Ez vizuálisan egységesíti a lap és az árnyék alakját.

A CardUI ezen felül a pozíciót is a fényforrás és a kártyadőlés alapján frissíti.

## 15.1 Teljesítménykérdés

Minden CardUI physics frame-ben:

- fény/árnyék számítást;
- order label kezelést;
- több shaderuniform módosítást

végezhet.

AETERNA-ban:

- csak hovered/animated lap legyen dinamikus;
- settled lapoknál dirty update;
- shared global light;
- performance budget;
- reduced motion/low FX mód.

# 16. Dissolve

A dissolve shader:

- noise texture-t;
- thresholdot;
- burn bordert;
- burn colort használ.

A CardUI dissolve végén queue_free-t hajt végre.

Hasznos:

- lap eltűnés;
- token megsemmisülés;
- discard/exile vizuális effekt;
- transition feedback.

A vizuális destroy nem lehet az authoritative destroy művelet.

# 17. CardUI animációs API

A CardUI külön metódusokat ad:

- `to_rot`;
- `to_rot_z`;
- `to_scale`;
- `to_pos`;
- `to_dissolve`;
- `go_to_pile`;
- `go_to_play`.

A pozíciómódok között van:

- lineáris;
- elastic;
- spring;
- Bézier;
- szakaszos Bézier + elastic.

## 17.1 Erős elv

A presentation motion primitivek központi helyen vannak.

## 17.2 Kockázat

- minden tulajdonság külön Tween;
- interruptibility külön boolokkal;
- több helyen force-kill;
- nincs közös animation generation/token;
- nincs snapshot version;
- await után stale node/state lehet;
- animációs callback modellmódosítást is végezhet.

AETERNA-javaslat:

```text
AnimationCoordinator
- transition_id
- card_instance_id
- from_pose
- to_pose
- cancellation token
- state_version
- completion policy
```

# 18. Presentation state machine

State-ek:

```text
IDLE
DISPLAY
DRAGGING
DESTROY
FOLLOWING
PLAYING
NO_INTERACT
```

Ez jó állapotszótár a Godot presentationhöz.

## 18.1 Használható szétválasztás

- Idle: szabad lap;
- Following: kéz/zóna követése;
- Display: nagyított megtekintés;
- Dragging: egérrel mozgatás;
- Playing: kijátszási animáció;
- Destroy: eltűnés;
- NoInteract: inputtiltás.

## 18.2 State machine hibák

A generikus StateMachine:

- invalid targetet indexelhet ellenőrzés előtt;
- default targetként `previous_state.state` értéket használ, amely kezdetben null lehet;
- `state_trans_started` signalt még a stale-source ellenőrzés előtt kibocsát;
- lock után várakozó transition stale lehet;
- nincs transition generation;
- nincs cancel;
- nincs queue policy;
- paraméteres és nem paraméteres út duplikált.

# 19. Model mutation presentation state-ből

A legsúlyosabb határsértés:

- Following state Deckbe szúr;
- Idle state follow_target nullázásával Deckből eltávolíthat;
- Destroy state Deckből töröl;
- Playing state késleltetés után discard pile-ba küld;
- Dragging state célterület alapján közvetlenül mozgat;
- CardUI setter Decket módosít.

A presentation-state tehát rules state-et ír.

AETERNA-ban:

```text
UI state
→ ActionIntent
→ C# engine validation
→ MatchState commit
→ EngineEvent
→ UI state transition
```

# 20. Íves CardTable

A CardTable:

- Curve alapján y-pozíciót számol;
- Curve alapján z-rotációt számol;
- vizuális placeholder Controlokat használ;
- kapacitást kezel;
- shrink/expand módot ad;
- sortingot támogat;
- order labelt mutathat.

## 20.1 Magas érték

Ez közvetlenül használható HandFanLayout tervezési referenciaként.

## 20.2 Kockázat

- a model Deck sorrendje UI global X pozícióból rendezhető;
- CardUI meglétét feltételezi;
- frame-enként labelt frissít;
- timeres 16,67 ms késleltetéssel stabilizál layoutot;
- card removal közben ugyanazt az arrayt iterálhatja;
- UI ordering rules orderinggé válhat.

# 21. Téglalapos kijelölés

A CardSelector:

- bal egérrel selection boxot húz;
- Ctrl mellett toggle-alapú kijelölést ad;
- selected_before_select snapshotot tart;
- scene groupból keresi a selectable lapokat;
- global Event állapot szerint tiltja magát.

Hasznos desktop UX.

Hiány:

- pointer capture;
- viewport/window elhagyás cancel;
- touch;
- gamepad;
- keyboard-only accessibility;
- semantic selection model;
- engine legal-selectability;
- maximum target count.

# 22. Többkártyás drag

A DraggingCards:

- global CardUI listát mozgat;
- kiterített és összecsukott mód;
- görgővel fókuszált lap;
- íves csoportlayout;
- multiple drop table/pile/destroy célra;
- capacity feedback;
- shake feedback;
- order insertion.

Ez a projekt egyik legerősebb UX-rétege.

## 22.1 AETERNA-átvételi elv

```text
MultiCardDragView
- selected instance IDs
- primary instance ID
- expanded/collapsed
- focus index
- preview poses
- legal target visuals
```

## 22.2 Kockázatok

- global mutable CardUI lista;
- első CardUI alapján keresi a célt;
- target validity scene overlap;
- részleges await közbeni stateváltozás;
- model order pozícióból;
- több lapot egyenként mozgat, nem egy actionként;
- részleges siker lehetséges;
- nincs rollback;
- nincs grouped engine request.

# 23. Drag buffer és gesture

A Dragging state 0,2 másodperces buffer után engedi el a dropot.

Ez csökkentheti a click/drag kétértelműséget, de:

- gyors press-release esetén release figyelmen kívül maradhat;
- a lap dragging állapotban ragadhat;
- timer nincs cancellation tokenhez kötve;
- exit után is lefuthat;
- nincs pixel-distance threshold;
- nincs explicit pointer capture.

A helyes AETERNA gesture:

```text
Pressed
→ ClickCandidate
→ movement threshold
→ Dragging
→ Released / Cancelled
```

Idő- és távolságküszöb együtt.

# 24. Global Event autoload

Az Event tárol:

- dragging CardUI-kat;
- displaying CardUI-kat;
- hand table node-ot;
- selection signalokat;
- mouse signalokat;
- combo signalokat.

Ez kényelmes UI event bus.

Kockázat:

- globális mutable state;
- scene-váltás után stale node;
- first-node group lookup;
- hidden lifecycle;
- nincs scoped match/view;
- párhuzamos boardok nem támogatottak;
- tesztizoláció nehéz.

AETERNA Godot-rétegben match-scoped coordinator szükséges.

# 25. HandTable

A HandTable:

- draw és discard pile-t ismer;
- CardPlayHandlert tart;
- számbillentyűvel választ;
- Space-szel játszik;
- draw/discard lock számlálókat használ;
- max hand capacityig húz;
- discardból draw pile-ba „shuffle”-öl;
- selected lapokból PokerHandet képez.

## 25.1 Jó UX

- gyors billentyűvezérlés;
- selected fallback az első lapra;
- draw/discard state feedback;
- automatikus hand fill;
- látványos átvezetés.

## 25.2 Authority-probléma

- közvetlenül poppol Deck Resource-ból;
- CardUI state-tel szúr a kéz Deckjébe;
- discard UI-művelet;
- „shuffle” valójában sorrendben mozgatja át a discard lapjait;
- a tényleges random shuffle hívás ki van kommentelve;
- nincs action request;
- nincs state version;
- nincs atomic transition;
- nincs replay.

# 26. Kozmetikai shuffle

A CardPile saját `shuffle()` metódusa `unfinished` megjegyzést tartalmaz.

A látható kód:

- animálja a lapokat;
- pile shuffle finished signalt küld;
- nem látható benne `deck.shuffle()` hívás.

A HandTable reshuffle útjában a `discard_pile.shuffle()` hívás ki van kommentelve.

Ezért a „shuffle” forrásszinten inkább:

```text
pile transfer animation
```

mint bizonyított random sorrendváltozás.

AETERNA-ban a shuffle kizárólag engine RNG döntésből származhat.

# 27. CardPile lockrendszer

A CardPile count-alapú lockokat használ:

- UI-change-by-deck counter;
- cannot-change-deck counter;
- signal, amikor újra engedélyezett.

Ez jó kísérlet az animáció és modellváltozás összehangolására.

## 27.1 Konkrét lock leak

A `drag_a_card()`:

1. növeli a change lock countert;
2. ellenőrzi, hogy a lap megtalálható-e;
3. sikertelen lookupnál returnöl;
4. nem csökkenti vissza a countert.

Ez permanent `can_change_deck = false` állapotot okozhat.

Production rendszerben RAII/finally jellegű lock token szükséges.

# 28. Array mutation iteráció közben

Több helyen:

```text
for card in deck.cards
→ deck.remove_card(card)
```

vagy UI state-en keresztüli removal történik.

Ez:

- elemek kihagyását;
- sorrendfüggő hibát;
- deck_changed reentrancyt;
- részleges törlést

okozhat.

Biztonságos minta:

```text
for card in deck.cards.duplicate()
```

de AETERNA-ban a teljes transition egyszeri MatchState commit legyen.

# 29. DrawnCards demókód

A `draw_cards()`:

- CardUI-t példányosít;
- új PokerCard modellt hoz létre;
- random 0–51 lapot választ;
- random backet választ;
- animálja.

Ez tiszta látványdemóhoz működik.

Production authorityként elfogadhatatlan:

- UI hozza létre a kártyát;
- duplikált standard lapok létrejöhetnek;
- nincs deck source;
- nincs RNG seed/event;
- nincs owner/zone;
- nincs instance ID.

## 29.1 Konkrét edge case

A képletek `num - 1` osztót használnak.

`num = 1` esetén divide-by-zero lehetséges.

## 29.2 Callback-paramétersorrend kockázata

A Tween finished callback binding sorrendje és a callback paramétersorrendje eltérőnek
látszik:

```text
bind(tween).bind(instance)
vs.
_on_card_drawn(card_UI, drawn_tween)
```

Helyi futtatással reprodukálandó.

# 30. CardPlayHandler

A handler:

- Card Resource kulcsú selected dictionaryt tart;
- UI selection signalra figyel;
- selected PokerCard tömböt képez.

A `play_a_card()` és `play_card_combo()` metódusok lényegében üresek.

A tényleges kijátszás a HandTable → RuleManager → PokerHand.play útvonalon történik.

Ez kettős/félbehagyott application-réteget jelez.

# 31. Signal type mismatch kockázat

A CardUI signal deklarációjában az első paraméter CardUI-ként szerepel, de a setter a
hozzárendelt Card Resource-ot emittálja.

A receiver Card paramétert vár.

Ez valószínű typed signal mismatch, amelyet helyi Godot-futtatással ellenőrizni kell.

AETERNA-ban a signal payload:

```text
card_instance_id
selected
source_view_id
```

legyen.

# 32. PokerRuleManager

A RuleManager:

- szabályregistryt tart;
- rule switcht támogat;
- Dou Dizhu implementációt regisztrál;
- hand checket ad;
- card/hand compare API-t ad;
- rule propertyket ad UI-nak;
- card-list validationt próbál adni.

## 32.1 Pozitívum

- rule implementation külön osztály;
- rule manager interface;
- typed PokerHand;
- több rule később hozzáadható;
- hand classification külön a UI-tól indul.

## 32.2 Határsértés

- RuleManager CardUI PackedScene-t preloadol;
- autoload ready során tesztet futtat és printel;
- global singleton;
- nincs match instance;
- nincs pure state input;
- Card Resource referenciákkal dolgozik;
- nem validál owner/zone/turn/action contextet.

# 33. Hibás validate_cards

A `validate_cards()` a PokerCardon:

```text
card.suit
card.num
```

mezőket használ.

A PokerCard ténylegesen:

```text
index
info_dict
```

adatot tart.

Ez invalid property runtime hibát okozhat.

További probléma:

- a check_hand nem hívja a validate_cards-ot;
- a validation max 54 lapot enged;
- a Card model csak 52 indexet hoz létre.

# 34. PokerRule base

A PokerRule:

- rule name;
- suit rank;
- number rank;
- hand type dictionary;
- compare;
- rank count;
- hand creation.

## 34.1 Statikus rule_name

A `rule_name` static, miközben a child `_init()` módosítja.

Több rule instance esetén megosztott állapot okozhat szabálynév-szivárgást.

## 34.2 Type filtering hiba

A `_create_hand()` létrehoz egy typed `pokers` tömböt, de az eredeti `cards` tömböt adja
a PokerHand konstruktorának.

A type filtering eredménye így nincs felhasználva.

# 35. Dou Dizhu szabály

A DoudizhuPokerRule felismer:

- single;
- pair;
- trio with single;
- trio with pair;
- straight;
- pair straight;
- airplane;
- airplane with singles/pairs;
- bomb;
- rocket.

A visible enum tartalmaz `BOMB_WITH_TWO` típust is, de külön ilyen ellenőrző függvényt
repositorykeresés nem talált.

Ez content/rules completeness kérdés.

# 36. Hand-összehasonlítási probléma

A RuleManager különböző hand type esetén egyszerűen a type enum numerikus értékét
hasonlítja.

Dou Dizhu esetén ez nem elegendő:

- a legtöbb különböző normál kombináció nem hasonlítható egymással;
- bomb és rocket külön szabály;
- azonos szerkezet/hossz is számít;
- aktuális asztali handet is figyelembe kell venni.

A projekt jelenlegi fő flowja csak azt vizsgálja, hogy a selected lapok alkotnak-e
valamilyen handet; nem bizonyított, hogy egy korábbi kijátszást legálisan felülmúlnak.

# 37. 52/54 lapos inkonzisztencia

A Doudizhu rule:

- small joker = 14;
- big joker = 15;
- rocketet vár;
- max 54 lapot említ.

A PokerCard indexe 0–51.

Ez azt jelenti, hogy a rule egy része a standard 52 lapos runtime modellel nem érhető el.

# 38. CardCombo félbehagyott absztrakció

A CardCombo konstruktor:

- deduplikál;
- validációt futtat;
- de nem állítja be a `cards` mezőt;
- a base validáció mindig true.

A tényleges rendszer PokerHandet használ.

A CardCombo ezért:

- félbehagyott;
- dead code;
- félrevezető contract.

Production repositoryban törlendő vagy befejezendő.

# 39. PokerHand

A PokerHand egyszerre tartalmaz:

- rules resultot;
- Card Resource referenciákat;
- visual widthöt;
- layout Curve-öket;
- `play()` commandot.

Ez legalább négy külön felelősség.

A helyes AETERNA-felosztás:

```text
HandEvaluation
PlayCardsAction
PlayCardsResult
CardPlayAnimationPlan
```

# 40. PokerHand.play határsértése

A `play()`:

1. invalid esetén UI/globális signalt emittál;
2. Card.play-t hív;
3. UI-t hoz létre;
4. presentation pozíciót számol;
5. CardUI PLAYING state-et indít;
6. global played signalt emittál.

Nincs:

- zone validation;
- player ownership;
- turn;
- expected state version;
- atomic removal;
- discard destination validation;
- partial failure guard;
- rollback.

# 41. Playing state

A Playing state:

- reparenteli a lapot DrawnCards containerbe;
- egy másodpercig animál;
- utána discard pile-ba mozgatja.

Ez vizuálisan jó staged transition.

Rules szempontból:

- a lap átmenetileg nincs stabil authoritative zónában;
- minden kijátszott lap automatikusan discardba kerül;
- animation timing határozza meg a zónamozgást;
- scene path hardcoded;
- scene változás/queue_free közben await hibás lehet.

# 42. Hidden information

A Card Resource:

- front texture-t;
- back texture-t;
- teljes info dictionaryt;
- ID-t

tart, és CardUI-ból elérhető.

Multiplayerben a face-down csak vizuális.

AETERNA-ban az ellenfél rejtett lapja nem kaphat teljes CardViewModelt.

# 43. Determinizmus és replay

Nem találtunk:

- match seed contractot;
- engine RNG streamet;
- random decision eventet;
- state versiont;
- action logot;
- replayt;
- state hash-t.

Random használat:

- Card back;
- DrawnCards random lap;
- dissolve noise;
- shuffle.

Ezek közül csak a kozmetikai random maradhat kliensoldali.

# 44. Multiplayer

Nem találtunk:

- network API-t;
- RPC-t;
- authoritative servert;
- viewer projectiont;
- reconnectet;
- state syncet;
- server-side validationt.

A jelenlegi architektúra single-client presentation és lokális Resource-state.

# 45. Tesztelés és CI

A repositorykeresés nem talált dedikált automatizált tesztcsomagot.

A RuleManager `_ready()` metódusában található egy hardcoded test resource és print, de
ez nem regressziós tesztkeret.

A vizsgált commitnál:

- nincs GitHub combined status;
- nincs kapcsolt workflow run.

A rules és gesture rendszerhez ez különösen kockázatos.

# 46. Szükséges tesztmátrix

## 46.1 Shader

- front 0/90/180 fok;
- backface;
- FOV 1/60/90/179;
- texture edge;
- transparency;
- green-screen tolerance;
- low-end GPU;
- Compatibility renderer;
- mobile;
- 10/50/100 CardUI.

## 46.2 Gesture

- quick click;
- quick release buffer előtt;
- drag cancel;
- window focus loss;
- overlapping targets;
- full target;
- locked pile;
- multi-drag partial failure;
- wheel focus;
- selector + drag konfliktus;
- Ctrl selection;
- touch/gamepad.

## 46.3 State machine

- invalid target;
- missing previous state;
- stale transition;
- two transitions same frame;
- lock release;
- node freed while awaiting;
- scene change;
- reparent during tween.

## 46.4 Model

- Card one-deck invariant;
- move transaction;
- duplicate instance;
- invalid index;
- 52/54 deck;
- Joker;
- deterministic shuffle;
- array mutation;
- lock leak.

## 46.5 Rules

- every Dou Dizhu hand;
- BOMB_WITH_TWO;
- invalid duplicates;
- Joker rocket;
- compare same type;
- compare different normal types;
- bomb over normal;
- rocket over bomb;
- previous hand legality.

# 47. Konkrét reprodukálandó hibák

## P0-1 – CardPile lock leak

1. `drag_a_card()` olyan Carddal, amely nincs a Deckben;
2. count nő;
3. early return;
4. ellenőrizni, hogy `can_change_deck` örökre false marad-e.

## P0-2 – validate_cards invalid property

1. bármely PokerCard tömb;
2. RuleManager.validate_cards;
3. `card.suit` / `card.num` access.

## P0-3 – 52/54 Joker eltérés

1. rocket kombináció létrehozása;
2. PokerCard index API-val;
3. ellenőrizni, hogy elérhetetlen-e.

## P0-4 – Single-card draw divide by zero

1. DrawnCards.draw_cards(..., 1);
2. `float(num - 1)` denominator;
3. animációs értékek vizsgálata.

## P0-5 – Draw callback paramétersorrend

1. DrawnCards draw;
2. tween finished;
3. callback argument type error ellenőrzése.

## P0-6 – Selection signal type

1. CardUI selected toggle;
2. typed signal emission;
3. Card vs CardUI paraméterhiba ellenőrzése.

## P0-7 – Cosmetic shuffle

1. ismert Deck sorrend;
2. CardPile.shuffle;
3. sorrend előtte/utána;
4. ellenőrizni, változik-e.

## P0-8 – Hand comparison

1. két külön normál Dou Dizhu hand type;
2. compare_hands;
3. ellenőrizni, hogy hibásan numerikus enum szerint rangsorol-e.

## P1-1 – Array mutation

1. több lap delete/discard;
2. iteration közbeni removal;
3. kihagyott lapok ellenőrzése.

## P1-2 – Locked pile drop

1. dragging;
2. cél pile locked;
3. release;
4. stuck dragging állapot ellenőrzése.

# 48. Erősségek az AETERNA szempontjából

1. Godot 4.5.
2. Modern CanvasItem shader.
3. Front/back külön TextureRect.
4. Shaderes perspective.
5. Dinamikus árnyék.
6. Selection flash.
7. Gradient/rainbow treatment.
8. Dissolve/burn edge.
9. Resource-local materials.
10. Íves kéz.
11. Curve-alapú rotation.
12. Többkártyás drag.
13. Kiterített/összecsukott drag group.
14. Görgős lapfókusz.
15. Selection rectangle.
16. Ctrl toggle selection.
17. Hover zoom.
18. Display state.
19. Reparent animation.
20. Több tween motion profile.
21. Bézier movement.
22. Capacity feedback.
23. Shake feedback.
24. Card és CardUI külön objektum.
25. Deck Resource a scene child order helyett.
26. Rule registry.
27. Typed PokerHand.
28. Game-specific rule subclass.
29. CC0 grafikai assetek.
30. Jól látható 0.1 → 0.11 → 0.2 fejlődési minta.

# 49. Gyengeségek és kockázatok

1. GPL-3.0 repository.
2. Nincs teljes README.
3. Rövid commit history.
4. Nincs CI.
5. Nincs automatizált teszt.
6. Card model ismeri és létrehozza UI-ját.
7. UI módosítja a Deck modellt.
8. UI state rules state-et ír.
9. PokerHand rules és presentation egyszerre.
10. Scene group service locator.
11. Global Event mutable state.
12. Nincs stable instance ID.
13. Nincs state version.
14. Nincs action contract.
15. Nincs atomic transition.
16. Nincs replay.
17. Nincs deterministic shuffle.
18. Hidden info nincs védve.
19. Shuffle félkész/kozmetikai.
20. CardPile lock leak.
21. Array mutation iteration közben.
22. 52/54 deck inkonzisztencia.
23. validate_cards hibás mezőket olvas.
24. CardCombo félkész.
25. RuleManager autoload ready tesztet futtat.
26. Hand compare túl egyszerű.
27. BOMB_WITH_TWO completeness kérdés.
28. State machine invalid-index/null default kockázat.
29. Stale transition.
30. Buffer előtti release elveszhet.
31. Node path hardcode.
32. Await utáni lifecycle kockázat.
33. UI random Cardot hoz létre.
34. Random back nem determinisztikus.
35. DrawnCards divide-by-zero.
36. Callback paramétersorrend kockázat.
37. Typed selection signal mismatch kockázat.
38. Per-card physics shaderfrissítés.
39. Abszolút editor movie path.
40. Modified shader attribution további auditot igényel.

# 50. AETERNA számára átvehető elvek

## 50.1 CardTiltView

Mouse position → x/y tilt → front/back/shadow shaderuniform.

## 50.2 SelectionTreatment

Typed selection/target/pending highlight shader.

## 50.3 HandFanLayout

Curve-alapú pose számítás pure komponensben.

## 50.4 MultiCardDragView

Selected ID-k csoportos vizuális mozgatása.

## 50.5 PresentationStateMachine

Csak presentation state, engine mutation nélkül.

## 50.6 AnimationCoordinator

Tween profile, cancellation és transition ID.

## 50.7 PileVisual

Darabszám, vastagság, top-card projection és animation.

## 50.8 ReducedFXPolicy

Shader, shadow, TIME flash és dissolve skálázása gép/setting szerint.

# 51. Amit nem szabad átvenni

1. Card → CardUI WeakRef.
2. Card által létrehozott UI.
3. CardUI setterből Deck mutation.
4. UI state-ből zone mutation.
5. Scene overlap mint legal target.
6. Global Event mint match state.
7. Resource Deck mint authoritative multiplayer state.
8. UI oldali random kártyalétrehozás.
9. UI időzítés mint discard commit.
10. Seed nélküli shuffle.
11. Rule managerben CardUI preload.
12. Rules resultban visual Curve.
13. Különböző hand type numerikus összehasonlítása.
14. GPL kód közvetlen másolása.

# 52. Javasolt AETERNA Godot-architektúra

```text
Aeterna.Engine
├── MatchState
├── LegalActionService
├── ZoneTransitionService
├── EngineRandom
├── RuleResolution
└── ViewerProjection
        │
        ▼
Aeterna.GodotBridge
├── ProjectionAdapter
├── CardViewModelAdapter
├── LegalInteractionAdapter
├── AnimationEventAdapter
└── StateVersionGuard
        │
        ▼
Aeterna.Godot
├── CardView
│   ├── FrontLayer
│   ├── BackLayer
│   ├── ShadowLayer
│   ├── SelectionTreatment
│   └── TiltController
├── HandFanLayout
├── PileView
├── MultiCardDragView
├── SelectionBox
├── PointerGestureController
├── DropTargetRegistry
├── PresentationStateMachine
├── AnimationCoordinator
└── ReducedFXPolicy
```

# 53. Javasolt presentation contract

```text
CardViewModel
- card_instance_id
- visible_card_id?
- front_asset_id?
- card_back_id
- zone_id
- zone_index
- selected
- selectable
- legal_target
- face
- presentation_tags
- state_version
```

```text
CardAnimationEvent
- transition_id
- card_instance_id
- kind
- from_zone
- to_zone
- from_index
- to_index
- duration_hint
- state_version
```

# 54. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | Clean-room CardTiltView proof | Godot | P0 |
| 2 | Front/back/shadow shader prototype | Godot | P0 |
| 3 | Resource-local material smoke | Tests | P0 |
| 4 | SelectionTreatment state enum | Godot | P0 |
| 5 | HandFanLayout pure pose API | Godot | P0 |
| 6 | MultiCardDragView ID-listával | Godot | P1 |
| 7 | SelectionBox accessibilityvel | Godot | P1 |
| 8 | Pointer gesture FSM | Godot | P0 |
| 9 | DropTargetRegistry legal target ID-kkel | Bridge/Godot | P0 |
| 10 | PresentationStateMachine engine mutation nélkül | Godot | P0 |
| 11 | Animation transition ID/cancellation | Godot | P0 |
| 12 | ReducedFXPolicy | Godot | P1 |
| 13 | Shader performance benchmark | Tests | P0 |
| 14 | Compatibility/mobile shader test | Tests | P1 |
| 15 | Hidden-card projection test | Security | P0 |
| 16 | CardView nem ismerhet MatchState mutationt | Architecture | P0 |
| 17 | Shuffle csak EngineRandomból | Engine | P0 |
| 18 | GPL direct-code guard | License | P0 |
| 19 | MIT shader attribution inventory | License | P1 |
| 20 | CC0 asset inventory | License | P1 |
| 21 | Következő Godot kisjáték auditja | Learning | P1 |

# 55. Bizonyítékjegyzék

| ID | Állítás | Forrás |
|---|---|---|
| E-001 | önálló public repository, öt commit | GitHub metadata/history |
| E-002 | Demo 0.2 commit | GitHub commit metadata |
| E-003 | Godot 4.5 / Forward Plus | `Demo 0.2/project.godot` |
| E-004 | DataLab/Event/Shake/RuleManager autoload | `project.godot` |
| E-005 | hardcoded movie path | `project.godot` |
| E-006 | Card Resource és UI WeakRef | `card.gd` |
| E-007 | Deck Resource és one-deck membership | `deck.gd` |
| E-008 | seed nélküli Deck.shuffle | `deck.gd` |
| E-009 | 0–51 PokerCard index | `poker_card.gd` |
| E-010 | runtime table/asset lookup | `poker_card.gd` |
| E-011 | CSV suffix type conversion | `csv2dict.gd` |
| E-012 | global UI Event bus | `card_event.gd` |
| E-013 | CardUI fake3D/tween/state API | `card_UI.gd` |
| E-014 | resource-local shaderanyagok | `card_UI.tscn` |
| E-015 | CardTable curve layout | `card_table.gd` |
| E-016 | rectangular selection | `card_selector.gd` |
| E-017 | multi-card dragging | `dragging_cards.gd` |
| E-018 | presentation states | `card_state.gd` |
| E-019 | state machine lock/transition | `state_machine.gd` |
| E-020 | direct Deck mutation from Following | `card_state.gd` |
| E-021 | Playing delayed discard | `playing.gd` |
| E-022 | destroy removes from Deck | `destroy.gd` |
| E-023 | CardPile model+visual lock | `card_pile.gd` |
| E-024 | unfinished pile shuffle | `card_pile.gd` |
| E-025 | HandTable draw/discard/play | `hand_table.gd` |
| E-026 | reshuffle randomization commented out | `hand_table.gd` |
| E-027 | UI creates random PokerCard | `drawn_cards.gd` |
| E-028 | CardPlayHandler incomplete play methods | `card_play_handler.gd` |
| E-029 | PokerRuleManager registry | `poker_rule_manager.gd` |
| E-030 | invalid validate field access | `poker_rule_manager.gd`, `poker_card.gd` |
| E-031 | PokerRule base | `poker_rule.gd` |
| E-032 | Dou Dizhu classification | `doudizhu_poker_rule.gd` |
| E-033 | PokerHand rules+visual+command | `poker_hand.gd` |
| E-034 | base fake3D shader MIT header | `fake3d.gdshader` |
| E-035 | selection flash shader | `fake3d_flash.gdshader` |
| E-036 | fake3D shadow | `fake3d_shadow.gdshader` |
| E-037 | dissolve shader | `dissolve2d.gdshader` |
| E-038 | GPL-3.0 root license | `LICENSE` |
| E-039 | Screaming Brain assets CC0 | `game/art/License.txt` |
| E-040 | nincs commit status | GitHub combined status |
| E-041 | nincs workflow run | GitHub workflow query |
| E-042 | nincs dedikált test találat | GitHub repository search |

# 56. Nyitott kérdések

1. Importálható-e warning/error nélkül Godot 4.5-ben?
2. Működik-e Godot 4.6-ban?
3. Működik-e Compatibility rendererrel?
4. Mekkora 50–100 CardUI GPU/CPU költsége?
5. Reprodukálható-e a CardPile lock leak?
6. Reprodukálható-e a signal type mismatch?
7. Reprodukálható-e a DrawnCards callbackhiba?
8. Reprodukálható-e a num=1 divide-by-zero?
9. Valóban változatlan marad-e a Deck CardPile.shuffle után?
10. A discard→draw út sorrendje randomizálódik-e bárhol?
11. A CardUI materialok minden példánynál izoláltak-e?
12. Van-e shared noise/gradient bottleneck?
13. Működik-e touch inputtal?
14. Mi történik ablakfókusz-vesztésnél drag közben?
15. Működik-e gamepaddal?
16. Minden Dou Dizhu kombináció helyes-e?
17. BOMB_WITH_TWO implementálva van-e más néven?
18. Hogyan hasonlítja a rendszer a previous handet?
19. Létrehozható-e Joker PokerCard?
20. A modified flash shader attributionja teljes-e?
21. A Demo 0.2 pontos futási licencértelmezése mi?
22. Mely vizuális primitiveket érdemes elsőként AETERNA proofba emelni?

# 57. Következő vizsgálati lépések

## 57.1 Codex nélkül

1. repository snapshot;
2. Godot 4.5 import;
3. main scene smoke;
4. shader screenshot baseline;
5. 10/50/100 card profiler;
6. Compatibility test;
7. drag/cancel/focus loss;
8. multi-drag;
9. lock leak;
10. selection signal;
11. DrawnCards callback;
12. single-card draw;
13. shuffle order;
14. Dou Dizhu rule corpus;
15. asset/shader notice inventory;
16. export smoke.

## 57.2 Később Codexszel gyorsítható

1. CardUI call graph;
2. model-mutation inventory;
3. state transition graph;
4. shader parameter inventory;
5. performance harness;
6. rule property tests;
7. clean-room CardTiltView;
8. clean-room HandFanLayout;
9. clean-room MultiCardDragView;
10. bridge-driven animation proof.

# 58. Végső minősítés

- **Vizuális presentation érték:** nagyon magas
- **Fake-3D shader érték:** magas
- **Selection/hover feedback:** magas
- **Íves kéz és multi-drag:** nagyon magas
- **Godot state-machine tanulási érték:** közepes
- **Card/Deck modellérték:** közepes
- **Rules-engine érték:** alacsony
- **Authoritative state érték:** nagyon alacsony
- **Determinism/replay:** alacsony
- **Multiplayer/hidden information:** nem megvalósított
- **Teszt/CI érettség:** alacsony
- **Licenc közvetlen használathoz:** GPL miatt kedvezőtlen
- **Közvetlen dependency:** elutasítandó
- **Clean-room vizuális inspiráció:** kiemelten ajánlott
- **Legfontosabb AETERNA-tanulság:** a shaderes ál-3D, árnyék, flash, kézlayout és
  többkártyás drag erős Godot client primitive lehet, de minden zóna-, szabály-,
  kijátszás- és random döntésnek a C# engine-ből kell érkeznie
- **Elemzés státusza:** első teljes source audit elkészült
- **Következő learning cél:** `Valyreon/seven-card-game-godot`

# 59. Változásnapló

## 0.1 – 2026-07-25

- elkészült a `Fulafu-ai/Godot4-Fake3D-Card-Game-UI-Demo` első teljes source auditja;
- ellenőrzésre került az önálló repository- és verziótörténet;
- rögzítésre került a vizuális provenance;
- rögzítésre került a Godot 4.5 / Forward Plus állapot;
- feldolgozásra került a Card–Deck Resource-modell;
- feldolgozásra került a CardUI és resource-local shaderanyagok;
- feldolgozásra került az ál-3D, front/back, shadow, flash és dissolve rendszer;
- feldolgozásra került az íves CardTable és HandTable;
- feldolgozásra került a téglalapos kijelölés;
- feldolgozásra került a többkártyás drag;
- feldolgozásra került a presentation state machine;
- feldolgozásra került a PokerRuleManager és a Dou Dizhu szabály;
- azonosításra került a UI/model/rules réteghatár sérülése;
- azonosításra került a CardPile lock leak;
- azonosításra került a kozmetikai shuffle;
- azonosításra került a 52/54 lapos inkonzisztencia;
- azonosításra került a validate_cards mezőhibája;
- azonosításra került a CardCombo félkész állapota;
- rögzítésre kerültek a DrawnCards és selection signal reprodukálandó hibái;
- rögzítésre került a GPL-3.0, MIT és CC0 licencréteg;
- rögzítésre került a hiányzó CI és automatizált teszt;
- elkészült az AETERNA CardTiltView, HandFanLayout, MultiCardDragView és AnimationCoordinator javaslat;
- a következő kijelölt projekt `Valyreon/seven-card-game-godot`.
