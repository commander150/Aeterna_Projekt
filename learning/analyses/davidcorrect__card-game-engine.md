# AETERNA – DavidCorrect/card-game-engine ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-24
- **Státusz:** README-, kiadás-, repository-metaadat- és architekturális első elemzés
- **Fő elemzési fájl:** `learning/analyses/davidcorrect__card-game-engine.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Repository:** `DavidCorrect/card-game-engine`
- **Stabil upstream URL:** `https://gitlab.com/DavidCorrect/card-game-engine`
- **Vizsgált branch:** `main`
- **Reprodukálhatósági pont:** a README utolsó ellenőrzött fájlcommitja `9a092bdf`
- **README-verzió:** v3.1 – 2026-05-17
- **Repository létrehozása:** 2025-02-18
- **AETERNA összehasonlítási bázis:** az aktuális C# authoritative engine-, runtime-package-, contract- és Godot-bridge rendszer
- **Összehasonlítási szabály:** kizárólag az AETERNA rendszeréhez mérve
- **Vizsgálati korlát:** a teljes GitLab-forrásfa ebben a környezetben nem volt közvetlenül beolvasható; a konkrét RPC-k, mutation pathok, scene-ek és függvények helyi source auditra várnak
- **Elsődleges AETERNA-érték:** Godot Control-alapú kártya- és zóna-UI, drag-and-drop, Stack/Exile megjelenítés, valamint hidden-hand multiplayer-prototípus
- **Elsődleges kockázat:** a README szerint a game state RPC-k közvetlenül a `game.gd` fájlban vannak, ezért a Godot kliens és a hálózati state authority valószínűleg nincs elválasztva

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Projekt neve | Card Game Engine |
| Szerző | David Wright / DavidCorrect / Flamennight |
| Repository | `DavidCorrect/card-game-engine` |
| Platform | GitLab |
| Default branch | `main` |
| Technológia | Godot / főként GDScript |
| UI-alap | Godot Control Nodes |
| Alapkártyák | standard 52 lapos francia kártyapakli |
| Zónák | Deck, Hand, Stack, Play, Discard, Exile |
| Kártyakijátszás | drag-and-drop a Play területre |
| Stack | Last In, First Out feloldás |
| Multiplayer | Godot High-Level Multiplayer API és RPC |
| Lobby | kétjátékos helyi hálózati prototípus |
| Rejtett információ | ellenfél kézlapjainak elrejtése szempontként megjelenik |
| Licenc | MIT |
| Külső demo | itch.io HTML5 tool/demo |
| Automatizált teszt/CI | a hozzáférhető anyagokból nem bizonyított |
| AETERNA-prioritás | P1 – Godot kliens, zóna-UI és multiplayer threat-model referencia |

# 2. Vezetői összefoglaló

A projekt célja nem egy általános, UI-tól független szabálymotor, hanem egy könnyen
módosítható Godot-kártyajáték-alap, amely:

- Control Node-okra épül;
- standard 52 lapos kártyapaklit példányosít;
- zónák között mozgat kártyákat;
- drag-and-drop interactiont ad;
- Stack és Exile zónát mutat be;
- lokális kétjátékos hálózati prototípust tartalmaz;
- az ellenfél kezét vizuálisan rejtett információként kezeli.

Az AETERNA számára a projekt **nem authoritative engine referencia**.

A használható szerep:

```text
AETERNA C# snapshot és event
→ Godot view model
→ Zone/CardView/Hand/Stack/Play megjelenítés
→ animáció és input
```

Nem használható szerep:

```text
Godot Card/Zone node
→ authoritative state
→ közvetlen RPC state mutation
```

Az AETERNA elfogadott iránya szerint:

- a C# engine az egyetlen szabályi authority;
- a Godot kliens csak requestet készít;
- a Godot snapshotot, legal actiont, response-t és eventet jelenít meg;
- az ellenfél rejtett kártyaazonosítója nem kerülhet a klienshez;
- a kliensoldali drag-and-drop nem bizonyít jogszerű kijátszást;
- minden multiplayer actiont az authoritative engine validál.

## 2.1 Rövid döntés

- **Godot UI-referenciaként:** igen
- **Drag-and-drop referenciaként:** igen
- **Zónanézet referenciaként:** igen
- **Stack presentation referenciaként:** igen, de nem AETERNA rules stackként
- **Hidden-hand UX referenciaként:** igen
- **Multiplayer authority referenciaként:** csak kockázati és prototípus-tanulságként
- **Rules-engine alapként:** nem
- **Közvetlen kódbeemelés:** csak külön source- és licencaudit után; saját implementáció ajánlott
- **Teljes mélyelemzés lezárva:** nem
- **Következő szükséges lépés:** helyi forráskód- és RPC-audit

# 3. Forrásbizonyosság

## 3.1 Megerősített a README-ből

- a projekt főként GDScriptet használ;
- a UI Control Node-okra épül;
- a `Card` statikus `create_card` konstruktort használ;
- a kártyák standard 52 lapos pakliból készülnek;
- a deck script az assetfájlnév alapján inicializál kártyát;
- létezik Deck, Hand, Stack, Play és Discard zóna;
- a v3.1 changelog szerint Exile zóna is bekerült;
- a zónák közös `Zone` alaposztályt használnak;
- a `CardView` szintén Zone-leszármazott;
- a kártyák drag-and-drop módon játszhatók ki;
- a Stack LIFO módon oldódik fel;
- a multiplayer Godot High-Level API és RPC;
- a hálózati inicializálás és lobby egy autoload `mp_network_handler.gd` feladata;
- a game state RPC-k közvetlenül a `game.gd` fájlban vannak;
- a szerző tudatosan nem használ MultiplayerSpawner és MultiplayerSynchronizer node-okat,
  mert a kéz rejtett információ;
- a v3.0 helyi hálózatot, lobbyt és ellenfélkurzor/kártyamozgás továbbítását adta;
- a szerző külön figyelmeztet, hogy a hálózati megoldás nem production-security proof;
- a licenc MIT.

## 3.2 Erős architekturális következtetés

A README alapján valószínű:

- a kártya vizuális node és a játékmeneti kártyaállapot szorosan összekapcsolódik;
- a zónák scene/node szintű objektumok;
- a multiplayer state-szinkron UI/game scene szinten történik;
- a host/client állapotgép nem külön pure rules library;
- a rejtett információt elsősorban scene- és replication-döntéssel védi;
- a projekt oktatási/prototípus célt szolgál.

Ezeket helyi source auditnak kell igazolnia.

## 3.3 Nem bizonyított

A hozzáférhető anyagokból nem állítható biztosan:

- melyik peer authoritative;
- minden action szerveroldalon újravalidált-e;
- van-e request ID;
- van-e state version;
- van-e stale-request guard;
- van-e reconnect vagy resync;
- van-e idempotency;
- van-e deterministic seed;
- van-e event log;
- van-e replay;
- az ellenfél kliens megkapja-e a rejtett kártyák identityjét;
- az RPC-k `any_peer`, `authority`, reliable vagy unreliable beállításai;
- milyen sender-validáció van;
- van-e anti-cheat;
- van-e automatikus teszt;
- van-e CI;
- milyen Godot-verzió a canonical target;
- mi a repository teljes aktuális HEAD SHA-ja.

# 4. Card-modell

A README szerint a `Card`:

- statikus `create_card` konstruktorral készül;
- standard 52 lapos pakli adataira van kialakítva;
- a deck scene script az asset fájlnevéből következtet a kártyára.

## 4.1 Használható AETERNA-tanulság

A vizuális kártyagyártásnál lehet központi factory:

```text
CardViewFactory
- card_instance_id
- public card reference
- owner/controller projection
- zone
- visibility
- localized definition
- art reference
- interaction state
```

A view factory egységesen készíthet:

- kézlapot;
- Domain-lapot;
- Wellspring-lapot;
- discard-listanézetet;
- animációs átmeneti nézetet.

## 4.2 Amit az AETERNA nem vehet át

Az AETERNA nem azonosíthat kártyát assetfájlnévből.

Kötelező:

```text
card_id
card_instance_id
owner_player_id
controller_player_id
zone
zone_index
visibility
activity_state
```

Az asset path csak presentation metadata.

A kártya rules identity nem függhet:

- fájlnévtől;
- sprite path-tól;
- scene node nevétől;
- lokalizált névtől;
- Control node példánytól.

# 5. Zónamodell

A README Deck, Hand, Stack, Play és Discard zónát sorol fel, a v3.1 pedig Exile zónát ad.

A Zone közös függvényeket ad, például:

- `recieve_cards()`;
- `clear_zone()`.

A CardView is Zone-leszármazott, és Deck/Discard tartalomnézetként használható.

## 5.1 Hasznos presentation-minta

A Godot oldalon indokolt lehet közös zóna-view interface:

```text
ZoneView
- ApplySnapshot(...)
- AddCardView(...)
- RemoveCardView(...)
- Reorder(...)
- Clear(...)
- SetHiddenCount(...)
- PlayTransition(...)
```

Speciális view-k:

- DeckView;
- HandView;
- DiscardView;
- DomainView;
- WellspringView;
- Stack/ResolutionView;
- CardBrowserView.

## 5.2 Fontos AETERNA-elhatárolás

A Godot Zone nem lehet authoritative zóna.

Az authoritative zóna:

- a C# MatchState része;
- card instance ID-kat tart;
- kétirányú registry-invariánst követ;
- transition csak engine-ben történik;
- zone sequence-et és eventet frissít;
- viewer-specifikusan projektálódik.

A Godot Zone csak a snapshot projekciója.

## 5.3 Stack és Exile

A projekt Stack zónája:

- a kijátszott kártyákat előbb fogadja;
- Resolve gombot mutat;
- LIFO sorrendben mozgatja őket Play zónába.

Ez hasznos UI-referencia egy feloldási sor megjelenítésére.

Nem következik belőle, hogy az AETERNA jelenlegi hivatalos szabályrendszerében általános
Stack vagy Exile zónát kell létrehozni.

AETERNA-ban:

- csak kanonikus szabályforrásból származó zóna létezhet;
- az effect/reaction resolution modell külön döntést igényel;
- egy vizuális pending-resolution lista nem automatikusan zóna;
- Exile csak külön főforrás- és contractdöntés után kerülhet be.

# 6. Drag-and-drop és input

A projekt kártyái a Play területre húzva játszhatók ki. A célterületet zöld particle effect jelzi.

## 6.1 Hasznos AETERNA-UX

```text
pointer down
→ drag visual
→ candidate target highlight
→ legal-action projection ellenőrzése
→ drop
→ ActionRequest készítése
→ pending UI
→ engine response
→ accepted animation vagy snap-back
```

A zöld particle effekt helyett vagy mellett az AETERNA használhat:

- legal target keretet;
- tiltott target jelzést;
- költség-előnézetet;
- pending selection állapotot;
- state-version frissítés utáni snap-backet;
- response-diagnostic tooltipet.

## 6.2 Kötelező authority-elv

A drag-and-drop csak felhasználói intent.

Nem hajthat végre közvetlenül:

- Hand → Domain mozgást;
- Aura-paymentet;
- Magnitúdó-ellenőrzést;
- target selection commitot;
- trigger/effect resolutiont;
- state version növelést.

A drop után `ActionRequest` készül, és a C# engine dönt.

# 7. CardView

A CardView Deck és Discard teljes képernyős tartalomnézetet ad.

## 7.1 Hasznos AETERNA-funkciók

- discard megtekintése;
- saját publikus zónák böngészése;
- pakli count;
- kereshető/filterezhető card browser;
- runtime debug view;
- hover/detail overlay;
- mobil és asztali layout.

## 7.2 Hidden-information szabály

A CardView csak viewer számára engedélyezett adatot kaphat.

Példák:

| Zóna | Saját nézet | Ellenfél nézet |
|---|---|---|
| Hand | identity és részlet | count / opaque |
| Deck | count, esetleges engedélyezett top info | count |
| Discard | publikus identity | publikus identity |
| Domain | publikus identity | publikus identity |
| Wellspring | szabály szerint projektált | szabály szerint projektált |

A Godot kliens nem kap teljes MatchState-et, majd nem maga rejti el a tiltott mezőket.

# 8. Multiplayer szerkezet

A README szerint:

- Godot High-Level Multiplayer API;
- RPC-alapú state update;
- `mp_network_handler.gd` autoload;
- lobby és hálózati inicializáció;
- game state RPC-k közvetlenül `game.gd`-ben;
- kétjátékos local network;
- ellenfélkurzor és kártyamozgás továbbítása;
- Auto Launch gyors teszteléshez.

## 8.1 Hasznos AETERNA-tanulság

A hálózati és presentation események szétválaszthatók:

```text
authoritative gameplay
- action request
- action response
- snapshot
- engine event

ephemeral presence
- cursor position
- hover
- card drag preview
- emote
- connection quality
```

Az ellenfélkurzor vagy drag preview nem authoritative state.

## 8.2 AETERNA-kockázat

A README szerint a state RPC-k közvetlenül a `game.gd` fájlban vannak. Ez arra utalhat,
hogy a scene script:

- egyszerre presentation coordinator;
- network endpoint;
- state synchronizer;
- esetleg state mutator.

Az AETERNA-ban ez tiltott.

Javasolt határ:

```text
Godot Network/Transport Adapter
→ trusted host boundary
→ Aeterna.EngineSession
→ validated ActionRequest
→ ActionResponse
→ viewer-specific snapshot/events
→ Godot presentation
```

## 8.3 Az autoload szerepe

A `mp_network_handler.gd` autoload kezelheti:

- peer létrehozását;
- host/join;
- lobby;
- connection/disconnection;
- transport status;
- peer ID mapping.

Nem kezelheti szabályforrásként:

- legal actiont;
- zónamozgást;
- fizetést;
- target validációt;
- effectet;
- turn state-et;
- győzelmet.

# 9. MultiplayerSpawner és MultiplayerSynchronizer elhagyása

A szerző tudatosan kerülte ezeket a node-okat, mert a kéz rejtett információ.

## 9.1 Pozitívum

Ez helyesen felismeri, hogy:

- a teljes scene-tree automatikus replikációja információt szivárogtathat;
- nem minden kliens kaphat azonos kártyaadatot;
- a multiplayer kártyajáték viewer-specifikus state-et igényel.

## 9.2 AETERNA következtetés

A megoldás nem pusztán az automatikus synchronizer elhagyása.

Szükséges:

```text
authoritative full state
→ ProjectionService(viewer_player_id)
→ redacted snapshot
→ redacted events
→ client-specific transport payload
```

Az ellenfél kliensére eleve nem kerülhet:

- rejtett card ID;
- deck order;
- hidden hand card instance ID;
- nem publikus selection;
- titkos target;
- debug metadata.

# 10. Authority és biztonság

A szerző maga figyelmeztet, hogy nem hálózati vagy security szakértő, és külön óvatosságot kér release előtt.

Ez fontos és helyes projektstátusz-jelzés.

## 10.1 A helyi source audit kötelező kérdései

1. Ki a host/authority?
2. Mely RPC-k fogadnak `any_peer` hívást?
3. Ellenőrzik-e `multiplayer.get_remote_sender_id()` értékét?
4. A sender és a player mapping stabil-e?
5. A kliens adhat-e meg tetszőleges kártyát?
6. A kliens adhat-e meg tetszőleges forrás- és célzónát?
7. A host újravalidálja-e az actiont?
8. Van-e turn ownership check?
9. Van-e state version?
10. Van-e duplicate action védelem?
11. Van-e reconnect/resync?
12. Van-e snapshot?
13. Van-e full-state leak?
14. Megkapja-e az ellenfél a kézlap identityjét?
15. A drag preview és a committed card move külön RPC-e?
16. Reliable vagy unreliable csatornát használnak?
17. Mi történik peer disconnect alatt?
18. Mi történik host disconnectnél?
19. Van-e malformed payload kezelés?
20. Van-e rate limit?

## 10.2 AETERNA minimum multiplayer contract

```text
ActionRequest
- schema_version
- request_id
- match_id
- player_id
- expected_state_version
- action_id
- action_type
- payload

ActionResponse
- accepted
- rejection code
- state_version_before
- state_version_after
- diagnostics

PlayerSnapshot
- viewer_player_id
- state_version
- redacted players
- redacted zones
- legal actions

EngineEvent
- sequence
- state version
- type
- payload
- visibility
```

# 11. Determinizmus és replay

A hozzáférhető projektleírás nem igazol:

- match seedet;
- deterministic deck shufflet;
- random event metadata-t;
- input logot;
- replayt;
- state hash-t;
- reconnect replayt.

Az AETERNA-ban a multiplayer és AI-vs-AI miatt ezek nem opcionálisak hosszú távon.

A visual drag, cursor és tween nem része a rules replaynek.

# 12. Tesztelés

A README Auto Launch módot javasol kétjátékos multiplayer gyors teszteléshez.

Ez hasznos manual smoke:

```text
app instance A
app instance B
→ lobby
→ initial state
→ drag preview
→ card move
→ stack resolve
→ discard/exile debug
```

Nem helyettesíti:

- headless engine tesztet;
- RPC authority testet;
- hidden-information testet;
- disconnect/reconnect tesztet;
- deterministic testet;
- malformed request tesztet;
- stale-state tesztet;
- reject-no-mutation tesztet.

# 13. Debug gombok

A projekt debug gombokat ad:

- kártyahúzás;
- kiválasztott kártya discard;
- Exile mozgatás;
- más zónaműveletek.

A v3.1 changelog szerint ezek multiplayerben is működnek.

## 13.1 AETERNA-javaslat

A production kliens debug actionje:

- külön debug buildhez kötött;
- nem exportálható release-be;
- ugyanazon EngineSession validációt használja;
- explicit debug authorityt igényel;
- audit eventet ad;
- nem közvetlenül mozgat node-ot/state-et.

# 14. Presentation és engine határ

## 14.1 A projektből újraimplementálható Godot-réteg

```text
CardView
ZoneView
HandLayout
DeckCounter
DiscardBrowser
PendingStackView
DropTargetHighlight
DragCoordinator
AnimationCoordinator
OpponentCursor
LobbyView
NetworkStatusView
```

## 14.2 A C# engine-ben maradó AETERNA-réteg

```text
MatchState
PlayerState
CardInstance registry
Zone invariants
Legal actions
Payments
Selections
Turn/phase/priority
Effects/reactions
Combat
Win/loss
RNG
Event log
Viewer projection
Diagnostics
```

# 15. Stack fogalmi figyelmeztetés

A projekt Stackje vizuálisan és működésében LIFO kártyahalom.

Az AETERNA későbbi reaction/effect modelljénél külön kell dönteni:

- van-e valódi rules stack;
- van-e pending resolution queue;
- milyen player priority van;
- milyen response window van;
- milyen mandatory/optional trigger van;
- hogyan történik a selection;
- mi a cancel/replacement szemantika.

A Godot StackView ezek megjelenítésére alkalmas lehet, de nem definiálhatja a szabályt.

# 16. Exile fogalmi figyelmeztetés

Az Exile a külső projekt saját zónája.

Az AETERNA jelenlegi production contractjában csak a kanonikus szabályforrások által
engedélyezett zónák és állapotok használhatók.

Exile beemelése külön igényelné:

- főforrás-döntést;
- zónadefiníciót;
- visibilityt;
- visszatérési szabályt;
- kártyaszöveg-konvenciót;
- structured mezőt;
- runtime package változást;
- engine transitiont;
- eventet;
- UI-t;
- auditot.

Ezért jelenleg csak presentation-ötlet, nem AETERNA-javaslat.

# 17. Licenc

A repository MIT licencet jelez, és a README szerint a szerző készítette a kódot és asseteket.

Közvetlen átvételnél:

- a LICENSE teljes szövegét meg kell őrizni;
- a szerzői jogi notice-t meg kell tartani;
- assetenként ellenőrizni kell, valóban a repository MIT hatálya alá tartozik-e;
- az itch.io build és repository assetkészlete közötti eltérést ellenőrizni kell;
- saját AETERNA-specifikus UI újraimplementálása továbbra is tisztább.

# 18. Erősségek az AETERNA szempontjából

1. Modern, aktív Godot-kártyajáték-prototípus.
2. Control Node-alapú UI.
3. Közös Zone view szemlélet.
4. Deck/Hand/Play/Discard megjelenítés.
5. Stack LIFO presentation.
6. Exile presentation.
7. CardView teljes képernyős tartalomnézet.
8. Drag-and-drop kijátszás.
9. Drop target vizuális jelzés.
10. Dinamikus deck/card példányosítás.
11. Hidden-hand probléma felismerése.
12. MultiplayerSpawner/Synchronizer információszivárgási kockázat felismerése.
13. Lobby és local network prototípus.
14. Opponent cursor/card motion UX.
15. Auto Launch multiplayer smoke.
16. MIT licenc.
17. A szerző őszinte security-státuszjelzése.

# 19. Gyengeségek és nyitott kockázatok az AETERNA szempontjából

1. GDScript/scene valószínűleg state authorityt is tart.
2. A game state RPC-k a `game.gd` fájlban vannak.
3. Nincs bizonyított pure C# rules boundary.
4. Nincs bizonyított request contract.
5. Nincs bizonyított state version.
6. Nincs bizonyított legal action.
7. Nincs bizonyított host-side revalidation.
8. Nincs bizonyított viewer projection service.
9. Nincs bizonyított event visibility.
10. Nincs bizonyított reconnect/resync.
11. Nincs bizonyított replay.
12. Nincs bizonyított deterministic RNG.
13. A Card standard 52 lapos és assetfilename-alapú.
14. Nincs bizonyított card definition/instance elválasztás.
15. Nincs bizonyított stabil card instance ID.
16. A Zone scene-modell könnyen összekeverhető authoritative zónával.
17. A Stack nem bizonyít reaction/priority rendszert.
18. Exile nem AETERNA-canonical zóna.
19. Debug gombok multiplayer authorityját auditálni kell.
20. Automatizált teszt/CI nem bizonyított.
21. A teljes aktuális commit SHA nem került rögzítésre.
22. A Godot targetverzió nem bizonyított.
23. A szerző külön jelzi a hálózati security korlátot.

# 20. AETERNA számára közvetlenül használható elvek

1. Godot ZoneView absztrakció.
2. CardView factory stabil card instance ID alapján.
3. Drag-and-drop mint intent.
4. Drop target highlight legal-action alapján.
5. Accepted/rejected animáció különválasztása.
6. Stack/ResolutionView csak presentationként.
7. Discard/CardBrowser teljes képernyős nézet.
8. Opponent cursor ephemeral presence channel.
9. Lobby autoload külön transport adapterként.
10. Hidden handhez viewer-specifikus payload.
11. Multiplayer Auto Launch smoke workflow.
12. Debug controls kizárólag debug buildben.
13. Scene/node soha ne legyen rules identity.
14. Asset path soha ne legyen card identity.
15. A Godot kliens csak projectiont tartson.

# 21. Amit nem szabad átvenni

1. Assetfájlnév mint card ID.
2. Godot node mint card instance authority.
3. Godot Zone mint authoritative zone.
4. Közvetlen game.gd state RPC mint production contract.
5. Kliensoldali drag-drop mint committed mutation.
6. Rejtett információ pusztán sprite elfordítással.
7. Teljes state minden kliensre küldése.
8. Debug zone move production multiplayerben.
9. Stack zóna automatikus AETERNA-beemelése.
10. Exile zóna automatikus AETERNA-beemelése.
11. Peer által megadott forrás- és célzóna validáció nélkül.
12. Godot autoload mint rules authority.

# 22. Javasolt AETERNA Godot-struktúra

```text
Aeterna.Godot
├── Bridge/
│   ├── EngineBridge.cs
│   ├── ActionRequestFactory.cs
│   ├── SnapshotProjector.cs
│   └── EventAnimationRouter.cs
├── Views/
│   ├── CardView
│   ├── HandView
│   ├── DomainView
│   ├── WellspringView
│   ├── DeckView
│   ├── DiscardView
│   ├── ResolutionView
│   └── CardBrowserView
├── Input/
│   ├── DragCoordinator
│   ├── DropTargetResolver
│   └── SelectionCoordinator
├── Multiplayer/
│   ├── TransportAdapter
│   ├── LobbyCoordinator
│   ├── PresenceChannel
│   └── ReconnectCoordinator
└── Debug/
    ├── DebugPanel
    └── ProjectionInspector
```

# 23. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | Közös `ZoneView` Godot interface | Godot | P1 |
| 2 | `CardViewFactory` card instance ID alapján | Godot | P0 |
| 3 | Drag-and-drop → ActionRequest minta | Bridge | P0 |
| 4 | Accepted/rejected animation flow | Godot | P1 |
| 5 | Legal-action alapú drop highlight | Godot/Bridge | P1 |
| 6 | Viewer-specifikus hidden-hand projection | Engine | P0 |
| 7 | Presence channel leválasztása gameplay RPC-ről | Multiplayer | P1 |
| 8 | Lobby/transport autoload rules authority nélkül | Multiplayer | P1 |
| 9 | ResolutionView külön rules stack nélkül | Godot | P2 |
| 10 | Full-screen Discard/CardBrowser | Godot | P2 |
| 11 | Multiplayer two-instance auto-launch smoke | Tests | P1 |
| 12 | Hidden information integration test | Tests | P0 |
| 13 | RPC sender/authority audit | Security | P0 |
| 14 | Reconnect/resync contract | Multiplayer | P1 |
| 15 | Debug control release-strip gate | Build | P1 |
| 16 | Assetpath–card ID elválasztás | Runtime/Godot | P0 |
| 17 | Stack és Exile ne kerüljön szabályba forrásdöntés nélkül | Rules | P0 |
| 18 | Helyi source audit a letöltött projekten | Learning | P0 |

# 24. Bizonyítékjegyzék

| ID | Állítás | Forrás | Bizonyosság |
|---|---|---|---|
| E-001 | A projekt nyílt Godot-kártyajáték-alap | GitLab README | megerősített |
| E-002 | Főként GDScript és Control Nodes | GitLab README | megerősített |
| E-003 | `Card.create_card` és 52 lapos pakli | GitLab README | megerősített |
| E-004 | Assetfájlnév-alapú card inicializáció | GitLab README | megerősített |
| E-005 | Deck/Hand/Stack/Play/Discard zónák | GitLab README | megerősített |
| E-006 | Közös Zone és CardView | GitLab README | megerősített |
| E-007 | Drag-and-drop és green particle target | GitLab README | megerősített |
| E-008 | Stack LIFO resolve | GitLab README changelog v2.0 | megerősített |
| E-009 | Local network, lobby, opponent moves | GitLab README changelog v3.0 | megerősített |
| E-010 | Exile zóna | GitLab README changelog v3.1 | megerősített |
| E-011 | Godot High-Level API és RPC | GitLab README | megerősített |
| E-012 | MultiplayerSpawner/Synchronizer elhagyása hidden hand miatt | GitLab README | megerősített |
| E-013 | `mp_network_handler.gd` autoload | GitLab README | megerősített |
| E-014 | Game state RPC közvetlenül `game.gd`-ben | GitLab README | megerősített |
| E-015 | Auto Launch kétjátékos teszt | GitLab README | megerősített |
| E-016 | Szerző security-figyelmeztetése | GitLab README | megerősített |
| E-017 | MIT licenc | GitLab LICENSE és README | megerősített |
| E-018 | Projekt létrehozása 2025-02-18 | GitLab project metadata | megerősített |
| E-019 | README v3.1 commit `9a092bdf` | GitLab README metadata | megerősített |
| E-020 | HTML5 itch.io demo/tool | itch.io projektoldal | megerősített |

# 25. Nyitott kérdések

1. Mi a repository aktuális teljes HEAD SHA-ja?
2. Mi a project.godot által jelölt Godot-verzió?
3. Mi a teljes root file tree?
4. Hol található a `card.gd`?
5. Milyen mezőket tart a Card?
6. Van-e stabil runtime card ID?
7. A card object és a CardView külön objektum-e?
8. Mi a Zone pontos API-ja?
9. Milyen zóna-invariánsok vannak?
10. Hogyan működik a Stack resolve?
11. A Play és Stack kártyasorrendje deterministic-e?
12. Az Exile visszahozható-e?
13. Melyik peer authority?
14. Milyen RPC annotációk vannak?
15. Van-e sender ID validation?
16. A kliens beküldhet tetszőleges card objectet vagy indexet?
17. A host újravalidálja a zónamozgást?
18. Az ellenfél kliens megkapja-e a hand card identityt?
19. A deck sorrend eljut-e minden klienshez?
20. Reliable vagy unreliable az opponent drag?
21. Reliable vagy unreliable a committed move?
22. Van-e state snapshot?
23. Van-e reconnect?
24. Van-e disconnect recovery?
25. Van-e malformed packet kezelés?
26. Van-e test vagy CI?
27. Van-e RNG seed?
28. Van-e replay?
29. A debug gombok milyen RPC-t hívnak?
30. A release build tartalmazza-e a debug mutationöket?

# 26. Következő helyi vizsgálati lépések

## 26.1 Codex nélkül

1. `.git/config` és origin ellenőrzése.
2. `git rev-parse HEAD`.
3. root file tree export.
4. project.godot ellenőrzése.
5. Card és CardView audit.
6. Zone és minden subclass audit.
7. game.gd mutation surface.
8. mp_network_handler.gd audit.
9. teljes `@rpc` lista.
10. RPC mode és transfer mode lista.
11. remote sender validation.
12. hidden-card payload audit.
13. deck-order leak audit.
14. two-instance local smoke.
15. unauthorized move teszt.
16. wrong-turn teszt.
17. wrong-zone teszt.
18. duplicate move teszt.
19. disconnect/reconnect teszt.
20. debug controls export audit.
21. LICENSE teljes ellenőrzése.
22. Godot headless parse/import smoke.

## 26.2 Később Codexszel gyorsítható

1. scene–script gráf;
2. RPC call graph;
3. mutation path audit;
4. hidden-information taint analysis;
5. zóna-invariáns audit;
6. authority bypass tesztgenerálás;
7. AETERNA ZoneView adapter proof;
8. drag-to-ActionRequest Godot proof;
9. multiplayer threat-model dokumentum;
10. deterministic visual replay proof.

# 27. Végső előzetes minősítés

- **Godot UI tanulási érték:** magas
- **Zónanézet tanulási érték:** magas
- **Drag-and-drop tanulási érték:** magas
- **Hidden-hand szemlélet:** hasznos
- **Multiplayer prototípus érték:** közepes
- **Multiplayer production authority érték:** nem bizonyított
- **Rules-engine érték:** alacsony
- **AETERNA C# engine kompatibilitás:** csak adapter/presentation szinten
- **Licenc:** MIT
- **Közvetlen dependency:** nem releváns
- **Közvetlen kódátvétel:** helyi audit után is inkább szelektív
- **Saját AETERNA újraimplementálás:** ajánlott
- **Elemzés státusza:** első README/architecture audit lezárva; source/RPC audit nyitott
- **Következő learning cél:** egy kanonikus, letöltött P0 projekt vagy az eredetazonosítási backlog célzott lezárása

# 28. Változásnapló

## 0.1 – 2026-07-24

- elkészült a DavidCorrect/card-game-engine első elemzése;
- rögzítésre került a Godot Control-, Card-, Zone- és CardView-szemlélet;
- feldolgozásra került a Stack, Exile és drag-and-drop presentation;
- feldolgozásra került a High-Level Multiplayer API és RPC felépítés;
- rögzítésre került a hidden-hand probléma felismerése;
- elhatárolásra került a Godot ZoneView és az AETERNA authoritative zóna;
- elhatárolásra került a visual Stack és a későbbi AETERNA resolution modell;
- elkészült az AETERNA multiplayer authority és hidden-information auditlista;
- elkészült a ZoneView/CardView/drag bridge javaslat;
- a teljes source audit nyitott státuszban maradt.
