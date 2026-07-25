# AETERNA – insideout-andrew/simple-card-pile-ui ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-25
- **Státusz:** repository-forrásokra épülő első teljes Godot UI- és presentation-elemzés
- **Fő elemzési fájl:** `learning/analyses/insideout-andrew__simple-card-pile-ui.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Repository:** `insideout-andrew/simple-card-pile-ui`
- **Stabil upstream URL:** `https://github.com/insideout-andrew/simple-card-pile-ui`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `e9f52b0b3485fb83dd8072fe8098e820d5b90236`
- **Vizsgált commit dátuma:** 2024-02-02
- **README szerinti kiadás:** 1.1.0
- **Plugin-konfiguráció szerinti verzió:** 1.0.0
- **Technológiai alap:** Godot 4.2 / GDScript / EditorPlugin
- **Licenc:** a repository gyökerében nem található ellenőrizhető LICENSE fájl; közvetlen átvétel nem engedélyezhető licenctisztázás nélkül
- **AETERNA összehasonlítási bázis:** az aktuális C# authoritative engine-, runtime-package-, contract- és Godot-bridge rendszer
- **Összehasonlítási szabály:** kizárólag az AETERNA rendszeréhez mérve
- **Vizsgálati korlát:** helyi Godot 4.2 import, futtatás, profiler- és exportvizsgálat ebben a körben nem történt
- **Elsődleges AETERNA-érték:** kézlegyező, húzó- és dobóhalom, kártyahover, drag/drop, dropzone, editor custom type és signal-alapú presentation API
- **Elsődleges AETERNA-kockázat:** a presentation manager draw-, discard-, shuffle-, hand-limit-, remove-from-game- és dropzone-döntéseket is végrehajt, ezért UI és szabályi state összekeveredik

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Projekt neve | Simple CardPileUI |
| Repository | `insideout-andrew/simple-card-pile-ui` |
| Default branch | `master` |
| Vizsgált commit | `e9f52b0b3485fb83dd8072fe8098e820d5b90236` |
| Repository állapot | nyilvános, nem archivált |
| Utolsó vizsgált commit | `Fixes script bug` |
| Godot-verzió | 4.2 |
| Renderer | Mobile |
| Nyelv | GDScript |
| Csomagolás | Godot EditorPlugin / `addons/simple_card_pile_ui` |
| Fő manager | `CardPileUI extends Control` |
| Kártyanézet | `CardUI extends Control` |
| Kártyaadat | `CardUIData extends Resource` |
| Célterület | `CardDropzone extends Control` |
| Debugnézet | `CardPileUIDebugger extends RichTextLabel` |
| Adatbetöltés | JSON card database + JSON collection |
| Beépített pile-ok | draw, hand, discard |
| Egyedi pile | CardDropzone |
| Interakció | click, hover, drag/drop |
| Layout | stack irányok + görbe alapú kézlegyező |
| Tesztek | nem talált |
| CI | nem talált |
| Explicit licenc | nem talált |
| AETERNA-prioritás | P0 – tisztán presentation- és Godot bridge-tanulási forrás |
| Közvetlen integráció | nem javasolt |

# 2. Vezetői összefoglaló

A projekt egy kisméretű Godot 4 addon, amely egy kártyakollekció vizuális kezeléséhez
biztosít:

- húzóhalmot;
- kézhalmot;
- dobóhalmot;
- egyedi dropzone-okat;
- kártyalétrehozást JSON-adatból;
- kártya-elő- és hátlapot;
- kézlegyezőt;
- pile-irányokat;
- hoverkiemelést;
- z-index kezelést;
- kattintást;
- drag-and-dropot;
- pile- és kártyasignalokat;
- editor custom type-okat;
- egyszerű signal debuggert.

Az addon legjobb része az, hogy viszonylag kis felületen jól demonstrálja a
presentation-komponensek együttműködését:

```text
CardUIData
→ CardUI
→ CardPileUI
→ CardDropzone
→ signalok
→ célpozíciók és animált visszatérés
```

Az AETERNA számára ezt nem kész rules-rétegként, hanem **UI viselkedéskatalógusként**
érdemes használni.

A fő elhatárolás:

```text
Külső addon:
CardPileUI.draw()
→ saját tömbök módosítása
→ CardUI átmozgatása
→ presentation és game state együtt

AETERNA:
Player input
→ ActionRequest
→ C# EngineSession
→ validált MatchState transition
→ snapshot / EngineEvent
→ Godot CardView és ZoneView animáció
```

## 2.1 Rövid döntés

- **Kéz-UI referenciaként:** kiemelten hasznos
- **Pile-layout referenciaként:** hasznos
- **Hover/drag UX-ként:** hasznos
- **EditorPlugin mintaként:** hasznos
- **Signal API mintaként:** hasznos
- **JSON authoring mintaként:** korlátozottan hasznos
- **Authoritative zóna- vagy játékmotorként:** nem használható
- **Közvetlen addonként:** nem javasolt
- **Közvetlen kódmásolás:** explicit licenc hiányában nem
- **Clean-room újraimplementálás:** igen
- **Legfontosabb AETERNA-tanulság:** a vizuális pile manager kizárólag projectiont és
  animációt kezeljen; draw, discard, shuffle és legal drop az engine feladata

# 3. Forrásbizonyosság

## 3.1 Megerősített

A repository és a forrás alapján megerősített:

- default branch: `master`;
- vizsgált HEAD: `e9f52b0b3485fb83dd8072fe8098e820d5b90236`;
- Godot 4.2 projekt;
- EditorPluginként telepíthető;
- négy custom type-ot regisztrál;
- JSON card database és collection használható;
- külön CardUIData és CardUI fogalom létezik;
- draw/hand/discard pile-t tart;
- CardDropzone egyedi pile-ként működik;
- hand rotation és vertical Curve használható;
- hover és drag/drop interakció van;
- a manager signalokat ad a pile- és cardeseményekhez;
- README 1.1.0 changelogot tartalmaz;
- plugin.cfg 1.0.0 verziót tartalmaz;
- nem található root LICENSE;
- nem található bizonyított automatizált test- vagy CI-réteg.

## 3.2 Erős következtetések

A source alapján:

- a CardPileUI nem csak view, hanem lokális játékmeneti state manager;
- a CardUI node referenciák alkotják a pile-state-et;
- a dropzone-legalitás csak drag során automatikus;
- a programozott set_card_dropzone megkerüli a can_drop_card ellenőrzést;
- a teljes scene-tree dropzone-scan nagyobb jelenetben drága lehet;
- az állandó `_process` layoutfrissítés felesleges munkát végezhet;
- a JSON pipeline schema és diagnosztika nélkül alkalmatlan AETERNA runtime authorityhoz.

# 4. Repository- és kiadási állapot

## 4.1 Aktivitás

A repository commitjai 2024. január 31. és február 2. közötti rövid fejlesztési időszakot
mutatnak. Az utolsó commit két example_2 hibát javított:

- a scriptet a megfelelő custom CardUI scriptre állította;
- a label- és texture-node útvonalakat a `Frontface` alá helyezte.

Ez kisméretű, korai addonra utal.

## 4.2 Verzióeltérés

A README changelog:

```text
1.1.0 – 2024-02-02
```

A plugin.cfg:

```text
version="1.0.0"
```

A két verzió nincs szinkronban.

AETERNA saját addon- vagy package-kiadásánál ugyanaz a verzió jelenjen meg:

- package manifestben;
- runtime contractban;
- dokumentációban;
- build artifactban;
- changelogban.

# 5. Godot EditorPlugin

A plugin az editorban custom type-ként regisztrálja:

```text
CardPileUI
CardUI
CardDropzone
CardPileUIDebugger
```

## 5.1 Használható AETERNA-minta

Az AETERNA Godot-rétege hasonló szerkesztői komponenseket adhat:

```text
AeternaCardView
AeternaZoneView
AeternaHandView
AeternaDropTargetView
AeternaProjectionDebugger
```

A custom type-ok előnye:

- könnyen példányosíthatók a Godot editorból;
- exported propertykkel konfigurálhatók;
- scene-ben vizuálisan szerkeszthetők;
- csökkentik az egyedi boilerplate-et.

## 5.2 AETERNA-határ

Az editor custom type nem lehet szabályi authority.

Az AETERNA plugin csak ezt állíthatja:

- layout;
- art;
- animáció;
- input;
- event-to-animation mapping;
- debug projection.

Nem állíthatja:

- legal action;
- zónamozgás;
- draw;
- shuffle;
- payment;
- effect;
- state version;
- győzelem.

# 6. CardUIData és CardUI szétválasztása

A projekt külön kezeli:

```text
CardUIData extends Resource
CardUI extends Control
```

A `CardUIData` alaposztály minimális:

```text
nice_name
card_data_updated signal
```

A felhasználó örökléssel adhat további mezőket.

## 6.1 Pozitívum

Ez fontos AETERNA-elv:

- statikus/viewadat külön a node-tól;
- egy view több külön adatstruktúrával használható;
- a custom card scene szabadon kiegészíthető;
- az editor validálhatja a szükséges node-struktúrát.

## 6.2 Korlát

A CardUIData itt nem csak presentation metadata. A JSON-ból tetszőleges mezők és
`resource_script_path` alapján futásidejű Resource osztály épülhet.

AETERNA-ban külön kell választani:

```text
Engine CardDefinition
├── card_id
├── rules fields
└── ability references

Godot CardPresentationDefinition
├── localized name
├── art reference
├── frame/theme
├── icon references
└── animation hints

CardViewModel
├── card_instance_id
├── viewer-visible fields
├── zone
├── interaction state
└── presentation definition
```

# 7. CardUI szerkezet

A CardUI:

- `Control`;
- Frontface és Backface TextureRectet vár;
- editor warninggal jelzi a hibás root child-struktúrát;
- hover-, click- és drop-signalokat ad;
- target_position felé lerpel;
- kattintáskor közvetlenül az egérhez ugrik;
- face-up/face-down állapotot a két TextureRect láthatóságával kezeli;
- z-indexet a parent CardPileUI segítségével rendezi.

## 7.1 Használható UX-részletek

- click alatt közvetlen pointerkövetés;
- release után sima visszatérés;
- hover emelés;
- egyidejű drag kizárása;
- csak top dropzone-card interaktív;
- elő- és hátlap külön node;
- editor configuration warning.

## 7.2 AETERNA-javaslat

```text
CardView
├── ViewModel
├── FrontRenderer
├── BackRenderer
├── HoverState
├── DragState
├── SelectionState
├── LegalTargetState
└── AnimationHandle
```

A CardView ne tároljon:

- owner rules state-et;
- authoritative zone-t;
- ability scriptet;
- payment state-et;
- engine mutation metódust.

# 8. Kézlegyező

A CardPileUI a kéz targetpozícióit:

- a kártya indexéből;
- hand ratio értékből;
- max hand spreadből;
- vertical Curve-ből;
- rotation Curve-ből

számolja.

Ez közvetlenül hasznos AETERNA presentation-minta.

## 8.1 Javasolt AETERNA HandLayout

```text
HandLayoutInput
- viewport width
- card count
- card size
- selected index
- hovered index
- max spread
- rotation curve
- vertical curve
- accessibility scale
```

Kimenet:

```text
CardLayoutPose
- position
- rotation
- z order
- scale
```

## 8.2 Javítások AETERNA-ban

- reszponzív viewport;
- több felbontás;
- UI scale;
- mobil touch;
- balkezes mód;
- nagy kéz összehúzása;
- selected/hovered card offset;
- animation duration;
- reduced motion;
- stable instance ID ordering;
- snapshot által meghatározott zone sequence.

# 9. Draw- és discard-pile presentation

A manager a draw és discard pile-t négy irányban tudja stackelni:

- up;
- down;
- left;
- right.

A stack display gap és max stack display korlátozza a vizuális kiterjedést.

Ez jó általános ZoneStackLayout minta.

## 9.1 Konkrét forráshiba

A discard-pile down ágában a source ezt ellenőrzi:

```text
draw_pile_layout == down
```

a helyes:

```text
discard_pile_layout == down
```

Ezért a discard downward layout működése a draw pile layoutjától függhet.

A hiba jó AETERNA-tanulság:

- layoutkomponens legyen külön, újrahasznosított függvény;
- ne legyen négy ág többször bemásolva;
- legyen parameterized layout test.

# 10. CardDropzone

A CardDropzone:

- saját `_held_cards` tömböt tart;
- top cardot ad;
- stackel;
- irányt és gapet konfigurál;
- face-up/face-down megjelenítést állít;
- drag során `can_drop_card()` ellenőrzést ad;
- alapértelmezésben minden látható dropzone elfogadja a lapot.

## 10.1 Pozitívum

A dropzone jó presentation-komponens lehet:

```text
DropTargetView
- target ID
- bounds
- highlight
- stack layout
- candidate state
- accepted/rejected preview
```

## 10.2 Kritikus authority-határ

A README is jelzi, hogy a `can_drop_card()` automatikusan csak drag/drop esetén fut,
programozott mozgatásnál nem.

A `CardPileUI.set_card_dropzone()` közvetlenül:

1. eltávolítja a kártyát más pile-okból;
2. eltávolítja más dropzone-okból;
3. hozzáadja az új dropzone-hoz.

Nem hívja a `can_drop_card()` metódust.

Az AETERNA-ban a Godot DropTargetView csak a C# engine által adott legal target listát
jelenítheti meg. A valódi commitot az EngineSession végzi.

## 10.3 Nem érvényesített exportok

A CardDropzone alaposztályban:

- `can_drag_top_card`;
- `held_card_direction`

exportált mezők vannak, de a vizsgált alaposztály működése nem használja őket.

Ez API-érettségi és dokumentációs kockázat.

# 11. Pile state és központi mozgatás

A `set_card_pile()` kommentje szerint ez az egyetlen kívánt út a pile-ok közötti
mozgatásra.

Ez jó szándék:

- előbb eltávolítás más helyről;
- majd hozzáadás egy új helyre;
- signalok;
- layout reset.

## 11.1 AETERNA-tanulság

Minden zónamozgásnak legyen egyetlen szabályi kapuja.

## 11.2 Miért nem megfelelő itt authorityként?

- CardUI node referencia a state;
- nincs card instance ID;
- nincs source zone paraméter;
- nincs expected state version;
- nincs ownership;
- nincs controller;
- nincs invariant validator;
- nincs atomic transition;
- több signal köztes állapotban lefuthat;
- nincs structured failure;
- nincs event sequence;
- nincs rollback.

A megfelelő AETERNA transition:

```text
MoveCardInstruction
- card_instance_id
- expected source zone
- destination zone
- destination index/position
- actor
- reason
- visibility
```

# 12. JSON card database és collection

A plugin két JSON-t használ:

1. card database;
2. collection, amely nice_name-ek listája.

A card database minimális mezői:

- `nice_name`;
- `texture_path`;
- `backface_texture_path`;
- `resource_script_path`.

A custom mezők a Resource script alapján kerülnek a CardUIData objektumba.

## 12.1 Használható AETERNA-elv

- külön definíciólista;
- külön példányszám/collection lista;
- custom presentation data;
- assetreferenciák adatból;
- viewscene konfigurálható.

## 12.2 Hiányok

- nincs schema version;
- nincs package ID;
- nincs content hash;
- nincs stabil card ID;
- a nice_name az egyedi kulcs;
- nincs duplicate nice_name diagnosztika;
- nincs explicit required field validation;
- nincs típushiba-diagnosztika;
- nincs JSON parse error location;
- a hibás parse egyszerűen üres listát adhat;
- nincs unknown field policy;
- nincs asset existence preflight;
- runtime script path tölthető adatból;
- nincs trust policy.

Az AETERNA munkaforrásból előállított runtime package compilernek ezeket buildidőben
kell elutasítania.

# 13. Kártyapéldány-identitás

A collection ugyanazt a nice_name-et többször tartalmazhatja, így több CardUI készülhet
ugyanabból a definitionből.

A példányok identitása azonban csak:

- a CardUI node referenciája;
- a tömbbeli pozíciója;
- az aktuális scene-életciklusa.

Nincs stabil `card_instance_id`.

Az AETERNA-ban minden CardView kulcsa az engine által kiadott instance ID.

```text
Dictionary<CardInstanceId, CardView>
```

A view újrapéldányosítható, de az identity megmarad.

# 14. Shuffle és determinizmus

A reset során a plugin a draw pile tömbön közvetlen:

```text
shuffle()
```

hívást végez.

Nem látható:

- seed;
- RNG state;
- shuffle event;
- replay;
- deterministic test.

Presentation addonként ez elfogadható lehet.

AETERNA-ban a shuffle kizárólag C# engine rules random:

```text
MatchSeed
→ EngineRandom
→ authoritative order
→ viewer-redacted snapshot
```

A Godot view nem keverhet authoritative paklit.

# 15. Draw, hand limit és discard

A CardPileUI beépítetten kezeli:

- draw;
- max hand limit;
- hand-limit feletti discardot;
- empty draw pile esetén discard reshuffle-t;
- discard-at műveletet.

Ezek nem pusztán UI-funkciók, hanem játékszabályok.

Az AETERNA-ban:

- a húzás mennyisége;
- a húzás engedélyezettsége;
- a pakli kifogyása;
- a kézlimit;
- a kézlimit következménye;
- a discard reshuffle;
- a dobás célpontja

mind az engine és a hivatalos szabályforrás része.

A Godot ZoneView csak az engine eredményét animálja.

# 16. Remove from game

A plugin külön `remove_card_from_game()` műveletet ad, amely eltávolítja a kártyát minden
pile-ból és dropzone-ból, signal után pedig `queue_free()` hívást végez.

Ez egy UI-életciklus művelet.

AETERNA-ban a szabályi fogalom nem azonos a node törlésével:

```text
rules state:
CardInstance zone/activity/lifecycle state

view state:
CardView létrehozás, eltávolítás vagy poolba visszaadás
```

A view eltűnése nem törölheti önmagában a CardInstance-et.

# 17. Signal API

A manager signalokat ad:

- pile updated;
- dropzone add/remove;
- card hovered/unhovered;
- card clicked/dropped;
- card removed from game.

Ez jó decoupling-minta a UI-n belül.

## 17.1 AETERNA-ban külön signalrétegek

```text
EngineEvent
- authoritative committed fact

Bridge signal
- snapshot/event érkezett

View signal
- hover/click/drag/animation
```

A CardUI `card_dropped` signalja intent, nem committed rules event.

# 18. CardPileUIDebugger

A debugger egy RichTextLabel, amely a CardPileUI signalokra csatlakozik és szöveges
naplót épít.

Hasznos AETERNA-minta:

```text
ProjectionDebugger
- state version
- snapshot viewer
- legal action count
- event sequence
- card instance
- zone transition
- rejected UI intent
- animation lifecycle
```

A production debugpanel:

- debug buildben jelenjen meg;
- ne tartalmazzon ellenfél rejtett adatot;
- ne módosítson state-et;
- ne legyen szabályforrás.

# 19. Teljesítmény- és skálázási kockázatok

## 19.1 Scene-tree scan

A CardPileUI a dropzone-ok kereséséhez rekurzívan végigjárja a teljes scene tree-t:

- get_card_dropzone;
- remove from dropzone;
- interaction check.

Nagy scene-ben ez drága lehet.

AETERNA-ban:

```text
DropTargetRegistry
Dictionary<DropTargetId, DropTargetView>
Dictionary<CardInstanceId, CardView>
```

## 19.2 Folyamatos `_process`

- minden CardUI frame-enként lerpel;
- minden CardDropzone frame-enként újraszámolja minden held card targetpozícióját.

Eventvezérelt dirty-layout célszerűbb:

```text
zone changed
viewport resized
hover changed
selection changed
→ recalculate layout
```

## 19.3 Tömbös lookup

Több művelet lineáris keresést és filtert használ. Kis kéznél ez rendben van, nagy
kártyaszámnál registry és indexelt állapot jobb.

# 20. Source-szintű további kockázatok

1. `is_card_ui_in_hand()` integer countot ad vissza bool helyett.
2. `_reset_card_collection()` minden közvetlen childot kártyaként próbál eltávolítani;
   custom nem-CardUI child esetén type guard szükséges.
3. JSON parsehiba stabil diagnosztika nélkül üres eredménybe fordulhat.
4. hiányzó nice_name esetén nincs strukturált hiba.
5. hiányzó texture/resource script runtime hibát okozhat.
6. a dropzone default legalitása csak `visible`.
7. programozott drop megkerüli a can_drop_cardot.
8. a discard-down branch rossz layoutváltozót ellenőriz.
9. README és pluginverzió eltér.
10. nincs test/CI proof.
11. nincs explicit licenc.

# 21. Hidden information

A plugin önmagában nem multiplayer engine. Ha azonban ugyanazt a CardPileUI-t ellenfél
kezének renderelésére használják, fontos:

- a `hand_face_up=false` csak vizuális rejtés;
- a CardUI továbbra is hordozhatja a teljes CardUIData-t;
- a texture path és nice_name lokálisan elérhető lehet.

AETERNA opponent hand view-ja ne kapjon teljes card definitiont.

Használjon:

```text
HiddenCardViewModel
- opaque view id
- card back presentation
- zone index, ha látható
- animation correlation
```

# 22. Tesztelés és CI

A repositoryban nem találtunk bizonyított:

- unit tesztet;
- integration tesztet;
- Godot import CI-t;
- plugin install tesztet;
- export tesztet;
- layout snapshot tesztet;
- drag/drop tesztet;
- malformed JSON tesztet.

## 22.1 AETERNA presentation tesztek

- plugin import;
- CardView creation;
- missing Frontface/Backface warning;
- hand 0/1/2/10/20 card layout;
- viewport resize;
- hover z-index;
- drag cancel;
- drop candidate highlight;
- accepted drop;
- rejected drop snap-back;
- hidden card data absence;
- event-order animation;
- view disposal;
- duplicate instance ID guard;
- reduced-motion mode;
- mobile pointer/touch;
- export smoke.

# 23. Licenc

A repository gyökerében nem található ellenőrizhető LICENSE fájl.

A GitHubon nyilvánosan olvasható kód nem jelenti automatikusan azt, hogy szabadon
másolható, módosítható vagy terjeszthető.

AETERNA-döntés:

- közvetlen addonbeemelés: nem;
- scriptmásolás: nem;
- scene- vagy assetmásolás: nem;
- fork használata: nem, amíg nincs licenctisztázás;
- általános UI-funkciók clean-room újraimplementálása: igen;
- saját HandLayout/ZoneView/CardView kód: igen.

# 24. Erősségek az AETERNA szempontjából

1. Kicsi és könnyen áttekinthető Godot 4 addon.
2. EditorPlugin custom type-ok.
3. CardUIData és CardUI fogalmi szétválasztás.
4. Frontface/Backface struktúra.
5. Editor configuration warning.
6. Draw/hand/discard pile presentation.
7. Négyirányú stack layout.
8. Görbe alapú kézlegyező.
9. Hoverkiemelés.
10. Drag/drop.
11. Dropzone stack.
12. Top-card interaction.
13. Signal-alapú UI API.
14. JSON database és collection elkülönítés.
15. Custom CardUI scene.
16. Debug signal viewer.
17. Központi mozgatási szándék.
18. Array duplicate visszaadása a belső lista védelmére.
19. Jó clean-room presentation funkciólista.

# 25. Gyengeségek és kockázatok

1. UI manager játékszabályokat hajt végre.
2. CardUI node a pile state alapja.
3. Nincs stabil card instance ID.
4. nice_name a definition kulcs.
5. Nincs schema/version/hash.
6. Nincs duplicate ID diagnosztika.
7. Nincs structured JSON error.
8. Runtime resource script path.
9. Unseeded authoritative shuffle.
10. Draw/discard/hand limit UI-ban.
11. Dropzone programozott mozgatásnál nem validál.
12. Default drop legality csak visibility.
13. Scene-tree scan.
14. Frame-enkénti dropzone layout.
15. Frame-enkénti CardUI lerp.
16. Köztes signalok atomic transition nélkül.
17. Nincs ownership/controller/visibility.
18. Nincs state version.
19. Nincs replay.
20. Hidden data csak face-downnal nem védhető.
21. Discard-down layout bug.
22. Két nem érvényesített dropzone export.
23. README/plugin verzióeltérés.
24. Nincs test/CI.
25. Nincs explicit licenc.

# 26. AETERNA számára átvehető elvek

## 26.1 HandFanLayout

Curve-alapú pozíció és rotáció.

## 26.2 ZoneStackLayout

Négyirányú stack és maximális vizuális offset.

## 26.3 CardInteractionController

Hover, click, drag, drop és snap-back.

## 26.4 Editor custom type

Könnyen konfigurálható Godot komponensek.

## 26.5 Presentation data/view szétválasztás

CardPresentationDefinition és CardView külön.

## 26.6 Signal debugger

Projection és animation események látható naplója.

## 26.7 Central view registry

CardInstanceId → CardView és DropTargetId → DropTargetView.

# 27. Amit nem szabad átvenni

1. CardPileUI mint game state.
2. Godot node referencia mint card identity.
3. nice_name mint stabil card ID.
4. UI-oldali shuffle.
5. UI-oldali draw.
6. UI-oldali hand limit.
7. UI-oldali discard.
8. UI-oldali remove-from-game rules döntés.
9. CardDropzone mint legal action authority.
10. `visible` mint drop legalitás.
11. programozott drop validáció nélkül.
12. teljes JSON runtime schema nélkül.
13. resource script path trusted contentként.
14. face-down mint hidden-information security.
15. explicit licenc nélküli kódmásolás.

# 28. Javasolt AETERNA Godot presentation-architektúra

```text
Aeterna.Engine
├── MatchState
├── EngineSession
├── LegalActionService
├── EngineEvent
└── ProjectionService
        │
        ▼
Aeterna.GodotBridge
├── PlayerSnapshotAdapter
├── LegalActionAdapter
├── EngineEventAdapter
├── VisibilityGuard
└── StateVersionGuard
        │
        ▼
Aeterna.Godot
├── CardViewRegistry
├── CardViewFactory
├── HandView
│   └── HandFanLayout
├── ZoneView
│   └── ZoneStackLayout
├── DropTargetView
├── CardInteractionController
├── AnimationCoordinator
├── CardDetailPanel
└── ProjectionDebugger
```

# 29. Példa AETERNA-flow

```text
Player megfog egy CardView-t
→ CardInteractionController megkeresi a legal action candidate-eket
→ DropTargetView-k highlightot kapnak
→ player elengedi a lapot
→ Godot ActionRequest intentet készít
→ EngineSession validál
→ accepted:
     snapshot/event érkezik
     CardViewRegistry frissül
     AnimationCoordinator animál
→ rejected:
     stabil diagnostic
     snap-back
```

A Godot view sem accepted, sem rejected esetben nem ír közvetlen MatchState-et.

# 30. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | `HandFanLayout` önálló komponens | Godot | P0 |
| 2 | `ZoneStackLayout` önálló komponens | Godot | P0 |
| 3 | `CardViewRegistry` instance ID alapján | Godot | P0 |
| 4 | `CardPresentationDefinition` külön rules definitiontől | Runtime/Godot | P0 |
| 5 | `CardInteractionController` | Godot | P0 |
| 6 | Legal-action alapú DropTargetView | Bridge/Godot | P0 |
| 7 | Accepted/rejected snap-back flow | Godot | P0 |
| 8 | HiddenCardViewModel teljes identity nélkül | Security/Godot | P0 |
| 9 | Dirty/event-driven layout | Godot | P1 |
| 10 | Viewport és accessibility scale | Godot | P1 |
| 11 | Reduced-motion támogatás | Godot | P2 |
| 12 | Touch input proof | Godot | P1 |
| 13 | ProjectionDebugger | Debug | P1 |
| 14 | Godot import/export CI | CI | P0 |
| 15 | Layout unit/snapshot tesztek | Tests | P1 |
| 16 | Malformed presentation data teszt | Tests | P1 |
| 17 | UI managerből draw/discard/shuffle kizárása | Architecture | P0 |
| 18 | Explicit addonlicenc minden saját kiadásnál | License | P0 |
| 19 | Clean-room implementáció | Projekt | P0 |
| 20 | Következőként deckbuilder UI source audit | Learning | P1 |

# 31. Bizonyítékjegyzék

| ID | Állítás | Forrás |
|---|---|---|
| E-001 | plugin card pile UI-t céloz | `README.md` |
| E-002 | JSON database és collection | `README.md`, `card_pile_ui.gd` |
| E-003 | draw/hand/discard fogalmak | `README.md`, `card_pile_ui.gd` |
| E-004 | CardUIData külön Resource | `card_ui_data.gd` |
| E-005 | CardUI külön Control | `card_ui.gd` |
| E-006 | Frontface/Backface követelmény | `card_ui.gd`, README |
| E-007 | editor warning | `card_ui.gd` |
| E-008 | hover/click/drag/drop | `card_ui.gd` |
| E-009 | dropzone scan | `card_ui.gd`, `card_pile_ui.gd` |
| E-010 | központi `set_card_pile` | `card_pile_ui.gd` |
| E-011 | CardDropzone saját held-card lista | `card_dropzone.gd` |
| E-012 | can_drop_card alapból visible | `card_dropzone.gd` |
| E-013 | CardDropzone frame-enként layoutol | `card_dropzone.gd` |
| E-014 | hand rotation/vertical Curve | `card_pile_ui.gd` |
| E-015 | négyirányú pile layout | `card_pile_ui.gd`, `card_dropzone.gd` |
| E-016 | discard down branch rossz változója | `card_pile_ui.gd` |
| E-017 | draw/discard/shuffle/hand limit | `card_pile_ui.gd`, README |
| E-018 | CardUI node-ref pile state | `card_pile_ui.gd` |
| E-019 | unseeded Array.shuffle | `card_pile_ui.gd` |
| E-020 | EditorPlugin custom type-ok | `simple_card_pile_ui.gd` |
| E-021 | signal debugger | `card_pile_ui_debugger.gd` |
| E-022 | Godot 4.2 | `project.godot` |
| E-023 | README 1.1.0 | `README.md` |
| E-024 | plugin.cfg 1.0.0 | `plugin.cfg` |
| E-025 | vizsgált commit | GitHub commit metadata |
| E-026 | root LICENSE nem található | repository contents ellenőrzése |
| E-027 | automatizált test/CI nem talált | repository search |

# 32. Nyitott kérdések

1. Importálható-e a HEAD hiba nélkül Godot 4.2 alatt?
2. Működik-e Godot 4.3–4.5 alatt?
3. Reprodukálható-e a discard-down layout bug?
4. Milyen viselkedést okoz hibás JSON?
5. Mi történik duplicate nice_name esetén?
6. Mi történik hiányzó resource_script_path esetén?
7. Mi történik hiányzó texture_path esetén?
8. Mi történik nem-CardUI childdal resetkor?
9. Mekkora kártyaszámnál válik drágává a scene-tree scan?
10. Mekkora kártyaszámnál válik drágává az állandó dropzone layout?
11. Működik-e touch inputtal?
12. Működik-e gamepaddel?
13. Működik-e ablakátméretezésnél?
14. Hogyan viselkedik több CardPileUI egy scene-ben?
15. Hogyan viselkedik több kézzel?
16. A todo szerinti multiple-hand támogatás elkészült-e más branchben?
17. Van-e GitHub release és külön licencadat?
18. A screenshot assetek licence tisztázott-e?
19. A Kenney assetek pontos licence megőrzött-e?
20. A deckbuilder-framework ugyanennek a CardUI/pile modellnek továbbfejlesztése-e?

# 33. Következő helyi vizsgálati lépések

## 33.1 Codex nélkül

1. helyi origin és HEAD ellenőrzés;
2. Godot 4.2 import;
3. example 1 smoke;
4. example 2 smoke;
5. plugin enable/disable;
6. malformed JSON;
7. duplicate nice_name;
8. missing asset;
9. 0/1/10/50/200 card layout;
10. discard-down bug;
11. multiple dropzone;
12. programozott invalid drop;
13. viewport resize;
14. touch input;
15. profiler capture;
16. export smoke;
17. licenc- és assetinventár.

## 33.2 Később Codexszel gyorsítható

1. CardPileUI API inventory;
2. pile/dropzone invariant audit;
3. performance benchmark scene;
4. HandFanLayout clean-room C# vagy GDScript proof;
5. ZoneStackLayout proof;
6. CardViewRegistry proof;
7. AETERNA snapshot adapter;
8. drag-to-ActionRequest proof;
9. Godot view test suite;
10. deckbuilder-framework kapcsolatvizsgálat.

# 34. Végső minősítés

- **Kéz-UI tanulási érték:** nagyon magas
- **Pile-layout érték:** magas
- **Drag/drop érték:** magas
- **EditorPlugin érték:** magas
- **Signal API érték:** közepes-magas
- **Adatpipeline érték:** alacsony-közepes
- **Authoritative engine érték:** nagyon alacsony
- **Hidden-information érték:** alacsony
- **Determinism érték:** alacsony
- **Teszt/CI érettség:** alacsony
- **Licencbiztonság:** közvetlen használathoz elégtelen
- **Közvetlen dependency:** nem javasolt
- **Clean-room presentation inspiráció:** kiemelten ajánlott
- **Legfontosabb AETERNA-tanulság:** a kéz-, pile- és drag-rendszert érdemes
  újraimplementálni, de a Godot UI-ból minden szabályi draw/discard/shuffle/drop döntést
  el kell távolítani
- **Elemzés státusza:** első teljes source audit elkészült
- **Következő learning cél:** `insideout-andrew/deckbuilder-framework`

# 35. Változásnapló

## 0.1 – 2026-07-25

- elkészült az `insideout-andrew/simple-card-pile-ui` első teljes source auditja;
- rögzítésre került a Godot 4.2 / EditorPlugin állapot;
- feldolgozásra került a CardPileUI, CardUI, CardUIData és CardDropzone szerkezet;
- feldolgozásra került a görbe alapú kézlegyező;
- feldolgozásra kerültek a négyirányú pile- és dropzone-layoutok;
- feldolgozásra került a hover, click, drag/drop és z-index UX;
- rögzítésre került a UI manager szabályi draw/discard/shuffle felelőssége;
- rögzítésre került a programozott drop validációmegkerülése;
- azonosításra került a discard-down layout változóhibája;
- rögzítésre került a JSON schema, stable ID és determinism hiánya;
- rögzítésre került a README/plugin verzióeltérés;
- rögzítésre került a teszt/CI és explicit licenc hiánya;
- elkészült az AETERNA HandFanLayout, ZoneStackLayout és CardViewRegistry javaslat;
- a következő kijelölt projekt `insideout-andrew/deckbuilder-framework`.
