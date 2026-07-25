# AETERNA – insideout-andrew/deckbuilder-framework ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-25
- **Státusz:** repository-forrásokra épülő első teljes Godot deck/presentation- és interaction-elemzés
- **Fő elemzési fájl:** `learning/analyses/insideout-andrew__deckbuilder-framework.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Repository:** `insideout-andrew/deckbuilder-framework`
- **Stabil upstream URL:** `https://github.com/insideout-andrew/deckbuilder-framework`
- **Vizsgált branch:** `main`
- **Vizsgált commit:** `41199fc02c3c9abaae1505737bd9c9080254fe15`
- **Vizsgált commit dátuma:** 2024-12-16
- **Plugin-manifest szerinti verzió:** 1.0.0
- **Technológiai alap:** Godot 4.3 / GDScript / Control-alapú addon
- **Licenc:** MIT
- **AETERNA összehasonlítási bázis:** az aktuális C# authoritative engine-, runtime-package-, contract-, content-compiler- és Godot-bridge rendszer
- **Összehasonlítási szabály:** kizárólag az AETERNA rendszeréhez mérve
- **Vizsgálati korlát:** helyi Godot 4.3 import, plugin-engedélyezés, futtatás, profiler-, export- és gesture-reprodukció ebben a körben nem történt
- **Elsődleges AETERNA-érték:** CardData–Card–Deck komponensfelosztás, deckszintű inputsignalok, kártyareparent animáció, kézlegyező, drag/swap és custom Deck-specializáció
- **Elsődleges AETERNA-kockázat:** a Godot scene tree és child order alkotja a deck/pile state-et; shuffle, move és példajátékszabályok közvetlenül node-okat módosítanak, stabil instance ID, state version, tranzakció és hidden-information projection nélkül

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Projekt neve | Deckbuilder Framework |
| Repository | `insideout-andrew/deckbuilder-framework` |
| Default branch | `main` |
| Vizsgált commit | `41199fc02c3c9abaae1505737bd9c9080254fe15` |
| Repository állapot | nyilvános, nem archivált |
| Godot-verzió | 4.3 |
| Renderer | GL Compatibility |
| Nyelv | GDScript |
| Addonmappa | `addons/deckbuilder-framework` |
| Fő adatobjektum | `CardData extends Resource` |
| Fő kártyanézet | `Card extends Control` |
| Fő deck/pile komponens | `Deck extends Control` |
| Beépített mintakártya | `PlayingCard` / `PlayingCardData` |
| Példák | simple, fancy, solitaire |
| Kártya-identitás | Godot Card node referencia és child index |
| Deck-sorrend | scene child order |
| Top card | utolsó child |
| Shuffle | childlista `shuffle()` + reparent |
| Drag | Deck-be centralizált egérinput |
| Reorder | vízszintes prev/next pozíció alapján child order csere |
| Rules specializáció | Deck öröklés és jelenetscriptek |
| Deck editor/collection manager | nem található |
| Deck legality/persistence | nem található |
| Tesztek | nem talált |
| CI-státusz | a vizsgált commitnál nincs status check vagy workflow run |
| Licenc | MIT |
| AETERNA-prioritás | P1 – Godot deck/pile presentation és interaction referencia |
| Közvetlen integráció | nem javasolt; clean-room komponenselvek ajánlottak |

# 2. Vezetői összefoglaló

A projekt neve könnyen félreérthető. A forrás alapján nem kész constructed-deck editor,
kollekciókezelő vagy paklilegalitási rendszer, hanem egy általános Godot kártya- és
deck/pile interaction framework.

A mag:

```text
CardData Resource
    ↓ card_scene
Card Control
    ↓ child node
Deck Control
```

A `Deck`:

- kártyákat példányosít CardData alapján;
- childként tartja őket;
- child orderből határozza meg a sorrendet és a top cardot;
- egyik Deckből a másikba reparenteli őket;
- kéz- és stack-layoutot számol;
- drag policyt kezel;
- deckszintű inputsignalokat ad;
- shuffle-t hajt végre;
- opcionálisan drag közben átrendezi a child ordert.

A szabályok nem a framework formalizált szerződésében vannak. A példák külön
jelenetscriptekben:

- húznak;
- kézlimitet ellenőriznek;
- discardra mozgatnak;
- visszakevernek;
- pasziánsz legalitást számolnak;
- győzelmet ellenőriznek.

## 2.1 Fő AETERNA-döntés

- **CardData/Card/Deck komponensötlet:** hasznos
- **Deckszintű inputrouter:** hasznos
- **Kéz- és stack-layout:** hasznos
- **Reparent utáni animációs folytonosság:** hasznos
- **Custom drag policy:** hasznos
- **Deck editor vagy collection manager mintaként:** nem alkalmas
- **Paklilegalitási rendszerként:** nem alkalmas
- **Authoritative deck/pile state-ként:** nem alkalmas
- **Multiplayer vagy hidden-information state-ként:** nem alkalmas
- **Közvetlen addonként:** nem javasolt
- **Clean-room Godot presentation-implementációhoz:** ajánlott

A legfontosabb tanulság:

> a Deck komponens jól centralizálhatja a kártyanézetek layoutját és inputját, de a
> deck tartalma, sorrendje, shuffle-je, húzása és zónamozgása kizárólag az AETERNA C#
> engine authoritative állapotából származhat.

# 3. Scope-pontosítás: mi ez és mi nem?

## 3.1 Amit ténylegesen megvalósít

- kártya-adatból scene példányosítás;
- kártyanézet frissítés;
- deck/pile vizuális sorrend;
- egyik deckből másikba mozgatás;
- top card;
- shuffle;
- drag policy;
- hover/click/drop signalok;
- centered hand;
- exact stack;
- Curve-alapú kézforgatás;
- kártyák drag közbeni átrendezése;
- standard francia kártyacsomag;
- egyszerű és látványos példa;
- pasziánszpélda.

## 3.2 Amit nem találtunk

- deck list dokumentum;
- paklinév és metadata;
- kártyamennyiség-szabály;
- minimum/maximum pakliméret;
- Birodalom/klán/kaszt vagy más szabályi szűrő;
- sideboard;
- format;
- ban/restriction lista;
- collection ownership;
- craft/collection count;
- keresés és filter;
- deck import/export;
- mentés/betöltés;
- deck hash;
- runtime package validation;
- stable card ID;
- stable card instance ID;
- multiplayer projection;
- szerver-authority;
- replay;
- undo/redo;
- teszt- vagy CI-réteg.

A projektet ezért az AETERNA-ban nem „deckbuilder rendszer”, hanem:

```text
Godot deck/pile presentation + interaction framework
```

kategóriában érdemes kezelni.

# 4. Technológiai és repository-állapot

## 4.1 Godot

A `project.godot`:

```text
config/features=PackedStringArray("4.3", "GL Compatibility")
run/main_scene="res://example.tscn"
window/stretch/mode="canvas_items"
```

A cél tehát Godot 4.3 és Control-alapú 2D UI.

## 4.2 Commitállapot

A vizsgált HEAD:

```text
41199fc02c3c9abaae1505737bd9c9080254fe15
```

A legutóbbi commit csak README-szövegjavítás. Az előző nagyobb commit:

- a Card inputját Deckbe mozgatta;
- click timer alapú kattintásdetektálást adott;
- dokumentálta a késleltetett mouse-exit quirköt.

## 4.3 CI

A vizsgált commitnál:

- nincs combined status;
- nincs kapcsolt workflow run;
- repositorykereséssel nem találtunk automatikus tesztet.

Ezért működési PASS státusz nem állítható.

# 5. Addon- és pluginmanifest

A repository `addons/deckbuilder-framework` mappát ad, és `plugin.cfg` fájlt tartalmaz.

A manifest:

```text
name="Deckbuilder Framework"
version="1.0.0"
script="deck.gd"
```

A `deck.gd` azonban:

```gdscript
class_name Deck extends Control
```

nem `EditorPlugin`.

Ez forrásszintű konfigurációs ellentmondás. A README telepítése csak az addonmappa
bemásolását írja elő, pluginengedélyezést nem.

A helyes minősítés:

- a `class_name` scriptek bemásolt addonként használhatók;
- a manifestből nem bizonyított, hogy Godot editorpluginként engedélyezhető;
- helyi import- és enable/disable smoke szükséges.

AETERNA saját Godot csomagjánál:

- vagy valódi `EditorPlugin` regisztrál custom type-okat;
- vagy pluginmanifest nélkül, normál class_name scriptek kerülnek a projektbe;
- a kettőt nem szabad összekeverni.

# 6. CardData

A `CardData` minimális:

```gdscript
class_name CardData extends Resource
@export var card_scene : PackedScene
```

## 6.1 Pozitívum

- statikus Resource külön a Card node-tól;
- definition választja ki a presentation scene-t;
- örökléssel bővíthető;
- `.tres` authoring jól illeszkedik a Godot editorhoz.

## 6.2 Kockázatok

- nincs stabil `card_id`;
- nincs schema version;
- nincs required-field validation;
- nincs duplicate ID;
- nincs content hash;
- nincs asset preflight;
- a CardData közvetlen PackedScene-t tart;
- arbitrary scene példányosítható;
- nincs bizonyítva, hogy a scene valóban `Card`;
- rules és presentation mezők könnyen egy Resource-ba keveredhetnek.

## 6.3 AETERNA-felosztás

```text
C# CardDefinition
- card_id
- rules data
- ability references
- content version

Godot CardPresentationDefinition
- art
- frame
- icon
- theme
- card_view_scene_id

CardViewModel
- card_instance_id
- viewer-visible values
- zone
- interaction flags
```

A runtime package compilernek buildidőben kell ellenőriznie a presentation scene ID-ket.

# 7. Card

A `Card`:

- `Control`;
- CardData referenciát tart;
- target_position és target_rotation felé interpolál;
- saját dragállapotot tart;
- auto-position kikapcsolható;
- `update_display()` virtuális hookként üres;
- az összes child mouse filterét PASS értékre állítja;
- drag kezdetén Deck signalját emittáltatja.

## 7.1 Használható AETERNA-minta

- CardView alaposztály;
- külön viewmodel-betöltés;
- célpose felé animáció;
- auto-layout ideiglenes kikapcsolása;
- root input továbbítása;
- subclass presentation.

## 7.2 Gesture-probléma

A drag küszöbe:

```text
mouse_down_point != current mouse position
```

Nincs pixel- vagy időalapú minimális elmozdulás.

A Deck clicklogikája releasekor `click_timer < 0.3` alapján kattintást emittál, majd
ugyanazon release eseményben dropot is emittálhat, ha a kártya held állapotú.

Egy gyors drag ezért elméletileg egyszerre válhat:

- `card_clicked`;
- `card_dropped`

intentre.

AETERNA-ban külön `PointerGestureState` szükséges:

```text
Pressed
→ movement threshold előtt ClickCandidate
→ threshold után Dragging
→ release: pontosan Click vagy Drop
```

## 7.3 Teljesítmény

Minden Card minden frame-ben:

- `lerp_angle`;
- `lerp`;
- global position write

műveletet végez, amíg auto_position engedélyezett.

AETERNA-ban Tween vagy dirty pose update célszerű, továbbá:

- settled state felismerés;
- animation cancellation;
- reduced-motion mód;
- view disposal guard.

# 8. PlayingCard

A PlayingCard:

- Cardból öröklődik;
- front- és backface TextureRectet használ;
- AnimationPlayert tart;
- flipped bool alapján vált oldalt;
- `update_display()` során minden alkalommal textúrát állít.

Ez használható CardView subclass minta.

A `Deck._update_display()` azonban layoutváltáskor is meghívja a Card
`update_display()` metódusát. A PlayingCard emiatt pose-frissítéskor újra beállíthatja:

- a front texture-t;
- a back texture-t;
- a visible állapotot.

AETERNA-ban szét kell választani:

```text
ApplyViewModel()
ApplyPose()
PlayAnimation()
```

A layout nem indokolja a teljes card content újrarenderelését.

# 9. Deck mint presentation manager

A `Deck` erőssége, hogy a Card inputját és a deckspecifikus interakciókat egy helyre
centralizálja.

Signaljai:

- mouse entered/exited;
- top card clicked;
- card clicked;
- card picked up;
- start card drag;
- card dropped;
- cards updated.

## 9.1 Használható elv

A Godot scene nem minden CardView-ra külön kapcsolódik, hanem a ZoneView/DeckView
aggregálja az intenteket.

AETERNA-javaslat:

```text
ZoneView
├── CardView children
├── layout
├── input aggregation
└── ViewIntent signal
```

A signal payload Card node helyett stabil instance ID legyen.

# 10. Scene child order mint state

A Deck nem a deklarált:

```gdscript
var cards : Array[Card]
```

tömböt használja, hanem a scene childokat.

A sorrend:

```text
get_children()
child index
get_top_card() = get_child(-1)
```

A shuffle is a childokat rendezi át.

## 10.1 Előny

- egyszerű;
- z-index és order együtt kezelhető;
- Godot scene-ben jól látható;
- prototípushoz gyors.

## 10.2 AETERNA-kockázat

A scene child order:

- presentation detail;
- nem stabil serialization contract;
- nem viewer-independent;
- nem alkalmas replayre;
- nem alkalmas authoritative multiplayerre;
- drag közben ideiglenesen módosulhat;
- node törlés/reparent megváltoztatja;
- nincs state version.

Az AETERNA-ban:

```text
ZoneState.OrderedCardInstanceIds
```

az authority, a Godot child order csak ennek projectionje.

# 11. Kártyalétrehozás

A `create_from_card_data()`:

1. `card_data.card_scene.instantiate()`;
2. `set_card_data`;
3. add child;
4. layout update;
5. `cards_updated`.

Hiányzik:

- null guard;
- scene type check;
- duplicate instance guard;
- stable instance ID;
- creation reason;
- source snapshot;
- structured error.

AETERNA CardViewFactory:

```text
CreateOrUpdateView(CardViewModel)
- instance_id
- presentation_scene_id
- visibility
- content hash
```

Nem hoz létre authoritative CardInstance-et.

# 12. Deckek közötti mozgatás

A `move_card_to_deck()`:

1. bontja a source Deck signalbekötéseit;
2. elmenti a global positiont;
3. eltávolítja a source childjai közül;
4. source layout + signal;
5. hozzáadja a cél Deckhez;
6. target layout + signal;
7. visszaállítja a korábbi global positiont.

## 12.1 Erős presentation-minta

A global position megőrzése miatt a Card az új parentbe kerülés után az előző vizuális
helyről animálhat az új célpose felé.

Ez jó AETERNA AnimationCoordinator minta.

## 12.2 Authority-hiány

A metódus nem ellenőrzi:

- hogy a source valóban tartalmazza-e a kártyát;
- ownership;
- legal source zone;
- legal destination;
- expected state version;
- position occupancy;
- visibility;
- effect reason;
- duplicate request;
- atomic transition.

Köztes állapotban source és target `cards_updated` signalok is lefutnak.

Az AETERNA-ban a move már commitált EngineEventből következzen:

```text
CardMoved
- card_instance_id
- from_zone
- to_zone
- from_index
- to_index
- state_version
```

# 13. Shuffle

A Deck:

```text
children = get_children()
children.shuffle()
remove all
add in shuffled order
```

megoldást használ.

Ez view- vagy offline prototípushoz működőképes.

AETERNA-ban nem fogadható el authoritative shuffle-ként, mert nincs:

- explicit seed;
- RNG stream;
- decision event;
- replay;
- state hash;
- server authority;
- hidden projection.

A Godot DeckView csak egy már meghatározott authoritative sorrend változását animálhatja.

# 14. Drag policy

A Deck támogatja:

```text
NONE
ALL
TOP
CUSTOM
```

policyt.

A `CUSTOM` örökléssel felülírható.

Ez jó UI-rugalmasság.

AETERNA-ban azonban a drag engedélyezése két rétegből áll:

```text
Engine legal action
AND
local UI accessibility/input policy
```

A `custom_can_card_be_dragged()` nem lehet rules authority. A C# engine által kiadott
legal action vagy interaction capability alapján kell működnie.

# 15. Drag alatti kártyasorrend-csere

A `SWAP_POSITIONS` mód:

- a held card aktuális indexét olvassa;
- az előző és következő kártya global X pozícióját hasonlítja;
- child ordert cserél;
- layoutot újraszámolja.

## 15.1 Használható

- kéz kézi átrendezése;
- vizuális insert-sort érzés;
- folyamatos drag feedback.

## 15.2 Korlátok

- csak X tengelyt vizsgál;
- függ a CardView aktuális animált global positionjétől;
- a child order már drag közben módosul;
- nincs cancelkor eredeti sorrend-visszaállítás;
- nincs stabil reorder intent;
- nincs engine-confirmáció;
- vertikális vagy íves kéznél pontatlan lehet.

AETERNA:

```text
local preview order
→ ReorderHandIntent
→ ha szabályilag releváns, engine validation
→ snapshot order
```

Ha a kézsorrend nem szabályi, maradhat kliensoldali presentation preference, de nem
változtathat replay-releváns állapotot.

# 16. Drop target felismerés

A Deck a teljes scene tree-t rekurzívan bejárja, és azt a Deck node-ot adja vissza,
amelynek global rectje tartalmazza a kurzort.

Kockázatok:

- minden dropnál teljes tree scan;
- több átfedő Deck közül child-traversal sorrend dönt;
- z-order nincs figyelembe véve;
- source Deck is találat lehet;
- disabled/hidden/blocked state nincs formalizálva;
- target csak node referencia.

AETERNA-ban:

```text
DropTargetRegistry
LegalTargetId set
hit test by UI layer/z-order
→ ActionRequest target ID
```

# 17. Click- és hover-quirk

A README dokumentálja, hogy a `mouse_exited_card` nem feltétlenül közvetlenül drop után
fut; új egérmozdulat szükséges.

A commitelőzményben több javítás próbálta kezelni:

- kézi mouse-exit;
- második exit kihagyása;
- később inputlogika Deckbe helyezése.

A vizsgált forrás továbbra is quirköt dokumentál.

AETERNA-tanulság:

- pointer capture;
- explicit gesture FSM;
- drag endkor saját hover recompute;
- ne Godot mouse-enter/exit sorrendből vezessünk szabályi intentet.

# 18. Simple példa

A simple példa:

- 52 CardData Resource-t preloadol;
- létrehozza a Draw Deckben;
- face-downra állítja;
- randomize + shuffle;
- hét lapot húz;
- draw pile clickre húz;
- kézlimit 16;
- discard dropra mozgat;
- discard clickre visszakever.

Ez jól demonstrálja a framework használatát.

A szabályok azonban a scene scriptben vannak, és közvetlenül:

- child countot;
- Card node-ot;
- Deck move-ot;
- shuffle-t

használnak.

Az AETERNA-ban ugyanez csak engine actionként létezhet.

# 19. Fancy példa

A fancy példa hozzáad:

- hover animációt;
- drag start resetet;
- pile count labelt;
- időzített kezdőkéz-animációt;
- drop feedbacket.

Hasznos presentation-minták:

- signal → AnimationPlayer;
- deck count display;
- async dealing animation;
- input és animation elkülönítése a Card subclassban.

A rules state azonban itt is node-alapú.

# 20. Solitaire példa

A pasziánszpélda bizonyítja, hogy a generic Deckből összetettebb játék építhető.

Megvalósít:

- draw/discard;
- hét tableau;
- négy build deck;
- többkártyás tableau-drag;
- face-down/face-up;
- legal move;
- win check.

## 20.1 Hasznos tanulság

A generic viewkomponens specializálható:

```text
TableauDeck
BuildDeck
```

## 20.2 AETERNA számára kerülendő

A rules state Deck subclassban van:

- `suit`;
- `required_value`;
- child count;
- top Card CardData;
- face state.

A `BuildDeck.play_card()` önmagában nem hívja a `can_hold_card()` ellenőrzést; a helyes
caller sorrendre támaszkodik.

A `TableauDeck.can_hold_card()` node tree-ből számol legalitást.

Ez AETERNA-ban nem elég biztonságos. A legalitás pure C# engine function legyen, és a
commit végén újra validáljon.

# 21. Többkártyás drag

A pasziánsz a frameworken kívül, külön `held_card_pile` tömbben kezeli a több kártya
együttes mozgatását.

Drag alatt:

- kikapcsolja az auto-positiont;
- külön z-indexet ad;
- frame-enként kézzel pozicionál;
- dropkor egyenként reparenteli;
- visszakapcsolja az auto-positiont.

Ez jó bizonyíték arra, hogy:

- a single-card Card/Deck primitive kiterjeszthető;
- csoportos view animation külön koordinátort igényel.

AETERNA-ban:

```text
CardViewGroupDrag
- selected instance IDs
- preview poses
- one ActionRequest
- accepted/rejected group animation
```

# 22. Definition és instance identitás

A CardData Resource a definition.

A Card node a runtime példány.

Ez fogalmilag jó kezdet, de nincs stabil azonosító egyik rétegen sem.

A CardInstance identitása:

- node reference;
- parent;
- child index.

AETERNA minimum:

```text
card_id
card_instance_id
owner_player_id
controller_player_id
zone_id
zone_index
created_sequence
visibility
```

A Godot CardView a `card_instance_id` projectionje.

# 23. Hidden information

A PlayingCard `flipped` boolal váltja a front/back láthatóságot, de a CardData továbbra is
a node-ban van.

Multiplayer vagy ellenfélkéz esetén a face-down presentation nem adatbiztonság.

AETERNA:

- saját kéz CardViewModelje kaphat teljes visible adatot;
- ellenfél rejtett kártyája nem kaphat card ID-t, artot vagy rules adatot;
- opaque view token és card back elegendő.

# 24. Determinizmus és replay

Nem található:

- match seed;
- state version;
- engine RNG;
- random decision event;
- replay log;
- serialization;
- state hash;
- undo/redo.

A `randomize()` használata a példákban lokális és nem reprodukálható match contract.

A frameworket ezért kizárólag presentation layerként szabad használni az AETERNA
determinisztikus engine-je felett.

# 25. Deckbuilding és content tooling hiánya

A projekt nem oldja meg az AETERNA pakliépítési problémáit:

- Birodalom- és klánazonosság;
- pakliméret;
- kártyalimit;
- tiltott kombinációk;
- format/set legality;
- collection ownership;
- deck code;
- import/export;
- migráció;
- runtime package compatibility;
- localized card search;
- card variant/printing;
- checksum.

A megfelelő AETERNA-réteg:

```text
DeckDefinition
DeckValidator
DeckImportExport
CollectionProjection
ContentCatalog
DeckBuilderView
```

A vizsgált `Deck` legfeljebb a DeckBuilderView egy vizuális zóna- és kártyamozgató
komponenséhez ad ötleteket.

# 26. Tesztelés

A repositoryban nem találtunk automatizált tesztet.

A vizsgált commitnál nincs:

- status check;
- workflow run;
- import log;
- export proof.

AETERNA Godot tesztminimum:

- CardData → CardView creation;
- wrong scene type rejection;
- empty deck;
- top card;
- move between zones;
- parentváltás utáni pose;
- 0/1/20/100 card layout;
- centered hand curve;
- click vs drag disambiguation;
- fast drag ne emittáljon clicket;
- drop null target;
- overlapping targets;
- drag cancel;
- reorder cancel/commit;
- hidden CardViewModel redaction;
- mobile/touch;
- resize;
- import/export smoke.

# 27. Licenc

A repository MIT licencű.

Ez lehetővé teszi a használatot és módosítást a copyright- és engedélyszöveg
megőrzésével.

Az AETERNA számára ennek ellenére clean-room újraimplementáció ajánlott, mert:

- a jelenlegi C# engine/bridge architektúrához kis, célzott komponensek szükségesek;
- a scene-tree authority nem vihető át;
- a gesture és drop target modellek áttervezendők;
- a runtime content contract eltér.

Közvetlen átvétel esetén külön assetlicenc-audit is szükséges a csomagolt
kártyaképekre.

# 28. Erősségek az AETERNA szempontjából

1. Kicsi, áttekinthető Godot 4.3 kódbázis.
2. CardData és Card node különválasztása.
3. Card subclass presentation hook.
4. Deckszintű inputcentralizálás.
5. Deckszintű signal API.
6. Top-card fogalom.
7. CardData-alapú view factory.
8. Deckek közötti reparent.
9. Global position megőrzése parentváltáskor.
10. Exact és centered layout.
11. Curve-alapú kézlegyező.
12. Auto-position kikapcsolás.
13. Drag policy enum.
14. Custom drag predicate.
15. Drag közbeni kézsorrend-preview.
16. Standard kártyacsomag demonstráció.
17. Egyszerű és animált példák.
18. Pasziánsz specializáció.
19. Többkártyás drag demonstráció.
20. MIT licenc.

# 29. Gyengeségek és kockázatok

1. A név deckbuildert ígér, de nincs deck editor.
2. Nincs paklilegalitás.
3. Nincs collection management.
4. Scene child order a deck state.
5. Card node referencia az instance identity.
6. Nincs stable card ID.
7. Nincs stable instance ID.
8. Shuffle Godot childlistán.
9. Nincs seed/replay.
10. Reparent közvetlen state mutation.
11. Nincs state version.
12. Nincs atomic transition.
13. Nincs structured failure.
14. Nincs ownership/controller.
15. Nincs hidden projection.
16. Drop target full scene-tree scan.
17. Átfedő targetek sorrendje nem explicit.
18. Drag reorder csak X tengely.
19. Gyors drag clicket és dropot is emittálhat.
20. Nincs drag threshold.
21. Mouse-exit quirk dokumentált.
22. Layout update content update-et is hív.
23. Card minden frame-ben interpolál.
24. `cards` tömb deklarált, de nem authority.
25. `parent_deck` lokális változó nem használt.
26. CardData arbitrary scene-t példányosít.
27. Base Card `update_display()` üres runtime hook.
28. BuildDeck commit caller-fegyelemre támaszkodik.
29. Rules node subclassokban és scene scriptben.
30. Pluginmanifest scriptje nem EditorPlugin.
31. Nincs test.
32. Nincs CI.
33. Nincs bizonyított export.
34. Assetlicencek külön ellenőrzendők.

# 30. AETERNA számára átvehető elvek

## 30.1 CardViewFactory

Presentation scene létrehozása engine-projection alapján.

## 30.2 ZoneView input aggregation

A zónakomponens signalja instance ID-t és local intentet ad.

## 30.3 HandFanLayout

Curve-alapú centered kéz.

## 30.4 Parent-change animation continuity

A kártyanézet előző global pose-ból animál az új ZoneView targetpose felé.

## 30.5 InteractionPolicy

Drag NONE/ALL/TOP/CUSTOM presentation capabilityként.

## 30.6 CardViewGroupDrag

Több nézet együtt mozgatása, egyetlen action intettel.

## 30.7 AnimationPlayer hook

Card-specifikus hover/selection animation.

# 31. Amit nem szabad átvenni

1. Deck scene node mint authoritative zóna.
2. Child order mint rules order.
3. Node reference mint network/state identity.
4. Godot-oldali shuffle.
5. Godot-oldali draw/discard rules.
6. UI-oldali legal move.
7. Callerre bízott can-hold → play-card sorrend.
8. Face-down mint hidden security.
9. Full scene-tree drop lookup.
10. Quick click/drag kétértelműség.
11. Direct reparent engine commit nélkül.
12. Pluginmanifestben Control script.
13. Test nélküli production használat.

# 32. Javasolt AETERNA presentation-architektúra

```text
Aeterna.Engine
├── MatchState
├── DeckState / ZoneState
├── DeckValidator
├── LegalActionService
├── EngineRandom
├── EngineEvent
└── ProjectionService
        │
        ▼
Aeterna.GodotBridge
├── CardViewModelAdapter
├── ZoneViewModelAdapter
├── LegalInteractionAdapter
├── VisibilityGuard
└── StateVersionGuard
        │
        ▼
Aeterna.Godot
├── CardViewFactory
├── CardViewRegistry
├── CardView
├── ZoneView
├── HandFanLayout
├── StackLayout
├── PointerGestureController
├── DropTargetRegistry
├── CardViewGroupDrag
├── AnimationCoordinator
└── ProjectionDebugger
```

# 33. Javasolt deckbuilder-architektúra

```text
Aeterna.ContentCatalog
        │
        ▼
DeckBuilderApplication
├── DeckDraft
├── Add/RemoveCard command
├── DeckValidator
├── violation list
├── format/set filters
├── copy count
├── import/export
└── save/load
        │
        ▼
DeckBuilderView
├── search/filter
├── collection grid
├── deck list
├── counts
├── validation panel
└── CardView/ZoneView presentation
```

A vizsgált framework ötletei csak a legalsó view-rétegben használhatók.

# 34. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | CardViewRegistry `card_instance_id` alapján | Godot | P0 |
| 2 | ZoneView input aggregator | Godot | P0 |
| 3 | HandFanLayout külön pure komponens | Godot | P0 |
| 4 | StackLayout külön pure komponens | Godot | P0 |
| 5 | Parent-change animation coordinator | Godot | P0 |
| 6 | PointerGestureController threshold/FSM | Godot | P0 |
| 7 | Click és drag kölcsönös kizárása | Tests/Godot | P0 |
| 8 | DropTargetRegistry explicit z-orderrel | Godot | P0 |
| 9 | Legal target lista engine-ből | Bridge | P0 |
| 10 | CardData és rules definition szétválasztása | Runtime/Godot | P0 |
| 11 | Presentation scene ID compiler-preflight | Tooling | P0 |
| 12 | Shuffle kizárólag EngineRandommal | Engine | P0 |
| 13 | HiddenCardViewModel redaction | Security | P0 |
| 14 | `CardMoved` eventből view transition | Bridge | P0 |
| 15 | Group drag egyetlen ActionRequesttel | Godot/Contract | P1 |
| 16 | DeckDraft + DeckValidator | Application | P0 |
| 17 | Deck import/export contract | Application | P1 |
| 18 | ContentCatalog search/filter | Application | P1 |
| 19 | Godot import/export CI | CI | P0 |
| 20 | Layout és gesture automated tests | Tests | P0 |
| 21 | MIT notice/asset audit, ha bármi átkerül | License | P1 |
| 22 | Következőként valós framework-alkalmazás auditja | Learning | P1 |

# 35. Bizonyítékjegyzék

| ID | Állítás | Forrás |
|---|---|---|
| E-001 | repository default branch main | GitHub repository metadata |
| E-002 | vizsgált HEAD és dátum | GitHub commit metadata |
| E-003 | Godot 4.3 / GL Compatibility | `project.godot` |
| E-004 | MIT licenc | `LICENSE` |
| E-005 | CardData Resource + card_scene | `card_data.gd` |
| E-006 | Card Control és targetpose | `card.gd` |
| E-007 | Card frame-enként interpolál | `card.gd` |
| E-008 | Deck inputsignalok | `deck.gd` |
| E-009 | CardData-alapú instantiate | `deck.gd` |
| E-010 | Deckek közti reparent | `deck.gd` |
| E-011 | shuffle child orderrel | `deck.gd` |
| E-012 | top card utolsó child | `deck.gd` |
| E-013 | drag policy | `deck.gd` |
| E-014 | X-alapú swap positions | `deck.gd` |
| E-015 | full scene-tree drop target lookup | `deck.gd` |
| E-016 | click timer input | `deck.gd` |
| E-017 | mouse-exit quirk | `README.md`, commit history |
| E-018 | centered hand Curve | `deck.gd`, README |
| E-019 | PlayingCard front/back és AnimationPlayer | `playing_card.gd` |
| E-020 | PlayingCardData suit/value/images | `playing_card_data.gd` |
| E-021 | simple draw/discard/reshuffle | `simple/simple.gd` |
| E-022 | fancy animation és labels | `fancy/fancy.gd` |
| E-023 | solitaire node-alapú rules | `solitaire/solitaire.gd` |
| E-024 | BuildDeck suit/required value | `solitaire/build_deck.gd` |
| E-025 | TableauDeck legalitás node state-ből | `solitaire/tableau_deck.gd` |
| E-026 | multi-card drag külön viewlistával | `solitaire/solitaire.gd` |
| E-027 | pluginmanifest Deck Control scriptre mutat | `plugin.cfg`, `deck.gd` |
| E-028 | nincs commit status check | GitHub combined status |
| E-029 | nincs kapcsolt workflow run | GitHub workflow query |
| E-030 | repository search nem talált automatizált testet | GitHub code search |

# 36. Prioritásos helyi reprodukciók

## P0-1 – Gyors drag kettős intent

1. mouse press;
2. kis elmozdulás, drag elindul;
3. 0,3 másodpercen belüli release;
4. ellenőrizni, hogy `card_clicked` és `card_dropped` egyszerre fut-e.

## P0-2 – Átfedő Deck target

1. két Deck rect átfed;
2. drag release az átfedésben;
3. ellenőrizni, melyik Deck tér vissza;
4. scene child order és z-order összevetése.

## P0-3 – Plugin enable

1. addon bemásolása;
2. pluginengedélyezés;
3. ellenőrizni, elfogadja-e a Godot a Control-alapú manifest scriptet.

## P1-1 – Vertikális kéz reorder

1. y_spread domináns;
2. SWAP_POSITIONS;
3. drag vertikális irányban;
4. ellenőrizni, hogy az X-only logika hibás-e.

## P1-2 – Hibás CardData scene

1. card_scene nem Card;
2. `create_from_card_data`;
3. strukturált hiba helyett runtime exception ellenőrzése.

## P1-3 – Rejected drop

1. drag olyan Deckre, amely szabályilag nem fogadhatja;
2. scene controller nem mozgatja;
3. Card visszaanimálása és gesture state tisztítása.

# 37. Nyitott kérdések

1. Engedélyezhető-e a plugin.cfg Godot 4.3 alatt?
2. Importálható-e warning/error nélkül?
3. Működik-e Godot 4.4–4.5 alatt?
4. Reprodukálható-e a quick drag double intent?
5. Reprodukálható-e a dokumentált delayed mouse exit?
6. Hogyan választ targetet átfedő Deckeknél?
7. Hogyan viselkedik vertikális reorder?
8. Hogyan viselkedik íves és forgatott kéznél a reorder?
9. Mi történik null CardData esetén?
10. Mi történik null card_scene esetén?
11. Mi történik nem-Card scene esetén?
12. Biztonságos-e a bound Callable disconnect minden Godot 4.3 buildben?
13. Mi történik, ha move source nem a kártya parentje?
14. Mi történik 200–500 CardView esetén?
15. Mekkora a frame-költség a settled Card `_process` miatt?
16. Az assetek pontos licence megfelel-e a MIT kódlicenc mellett?
17. Van-e külön GitHub release?
18. Van-e aktív branch tesztekkel?
19. A framework ténylegesen használható-e plugin enable nélkül?
20. Melyik AETERNA CardView primitive-et érdemes elsőként proofként megvalósítani?

# 38. Következő vizsgálati lépések

## 38.1 Codex nélkül

1. helyi origin és HEAD ellenőrzés;
2. Godot 4.3 import;
3. plugin enable/disable;
4. simple smoke;
5. fancy smoke;
6. solitaire smoke;
7. quick click/drag teszt;
8. átfedő target teszt;
9. vertical reorder;
10. CardData type error;
11. 0/1/20/100/500 card profiler;
12. hidden CardData memory inspection;
13. resize/touch/gamepad;
14. export smoke;
15. assetlicenc-inventory.

## 38.2 Később Codexszel gyorsítható

1. Deck/Card call graph;
2. gesture-state audit;
3. scene mutation inventory;
4. layout benchmark harness;
5. CardViewRegistry proof;
6. HandFanLayout proof;
7. DropTargetRegistry proof;
8. snapshot-to-DeckView adapter;
9. DeckDraft/DeckValidator application skeleton;
10. Godot presentation test suite.

# 39. Végső minősítés

- **Card/Deck komponensérték:** magas
- **Godot presentation érték:** magas
- **Deckszintű inputrouter érték:** magas
- **Kézlayout érték:** magas
- **Kártyaanimáció érték:** közepes-magas
- **Constructed deckbuilder érték:** alacsony
- **Paklilegalitási érték:** nagyon alacsony
- **Authoritative engine érték:** nagyon alacsony
- **Hidden-information érték:** alacsony
- **Determinism/replay érték:** alacsony
- **Teszt/CI érettség:** alacsony
- **Licenc:** MIT, assetenként külön ellenőrzés szükséges
- **Közvetlen dependency:** nem javasolt
- **Clean-room presentation inspiráció:** ajánlott
- **Legfontosabb AETERNA-tanulság:** a Deck kiváló lehet ZoneView és inputaggregátor,
  de a tartalma és sorrendje kizárólag a C# MatchState projectionje lehet
- **Elemzés státusza:** első teljes source audit elkészült
- **Következő learning cél:** `db0/Fragment-Forge`

# 40. Változásnapló

## 0.1 – 2026-07-25

- elkészült az `insideout-andrew/deckbuilder-framework` első teljes source auditja;
- rögzítésre került a `main` branch, a vizsgált HEAD és a Godot 4.3 állapot;
- pontosításra került, hogy a projekt nem kész deck editor, hanem Card/Deck interaction framework;
- feldolgozásra került a CardData–Card–Deck komponensmodell;
- feldolgozásra került a deckszintű input- és signalrendszer;
- feldolgozásra került a kézlegyező, stack, drag policy és child-order reorder;
- feldolgozásra került a reparent utáni animációs folytonosság;
- feldolgozásra kerültek a simple, fancy és solitaire példák;
- azonosításra került a scene child order authority-kockázata;
- azonosításra került a quick drag click/drop kétértelműsége;
- azonosításra került a full scene-tree drop target keresés;
- rögzítésre került a stable ID, state version, hidden projection és determinism hiánya;
- rögzítésre került a pluginmanifest Control-script ellentmondása;
- rögzítésre került a hiányzó teszt/CI proof;
- rögzítésre került az MIT licenc;
- elkészült az AETERNA ZoneView, CardViewRegistry, gesture és DeckBuilderApplication javaslat;
- a következő kijelölt projekt `db0/Fragment-Forge`.
