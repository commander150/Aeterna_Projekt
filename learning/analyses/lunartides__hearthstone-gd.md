# AETERNA – LUNARTIDES/HEARTHSTONE.GD ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-26
- **Státusz:** első teljes repository-, card model-, module-, multiplayer-, anticheat-, hidden-information-, content-tooling-, UI-, determinism-, teszt- és licencaudit
- **Fő elemzési fájl:** `learning/analyses/lunartides__hearthstone-gd.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Repository:** `LunarTides/Hearthstone.gd`
- **Stabil upstream URL:** `https://github.com/LunarTides/Hearthstone.gd`
- **Vizsgált branch:** `main`
- **Vizsgált commit:** `df37022101aa84c467acceaf3b6914a699ab48c9`
- **Vizsgált commit dátuma:** 2024-04-24
- **Commitüzenet:** `Enforce consistent rng between clients`
- **Projektverzió:** `0.1.0`
- **Godot-verzió:** 4.2 / a történet szerint 4.2.2
- **Renderer:** Forward Plus
- **Nyelv:** GDScript
- **Hálózat:** ENet high-level multiplayer RPC
- **Licenc:** GPL-3.0
- **CI-bizonyíték:** nincs status check vagy kapcsolt workflow run
- **Szerzői minősítés:** nagyon korai, használatra nem kész
- **AETERNA összehasonlítási bázis:** C# authoritative engine, typed action request, stable instance ID, state version, atomic transition, viewer projection és Godot presentation boundary
- **Összehasonlítási szabály:** kizárólag az AETERNA aktuális rendszeréhez viszonyítva
- **Vizsgálati korlát:** helyi Godot futtatás, kétklienses hálózati teszt, export, profiler és adversarial packetteszt nem történt
- **Elsődleges AETERNA-érték:** moduláris feature/hook rendszer, szerveroldali anticheat rétegek, Godot editoros kártyaauthoring, 3D kártyapresentation és konfigurálható module registry
- **Elsődleges AETERNA-kockázat:** teljes állapot replikálása minden kliensre, opponent deck leak, scene-node rules authority, zone-index alapú identity, kliensenként futó effectlogika, animation/rules összefonódás és több konkrét kódhiba
- **AETERNA-döntés:** közvetlen integráció nem; modul- és authoringötletek clean-room referenciaként használhatók

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Repository | `LunarTides/Hearthstone.gd` |
| Default branch | `main` |
| Vizsgált commit | `df37022101aa84c467acceaf3b6914a699ab48c9` |
| Utolsó commit dátuma | 2024-04-24 |
| Repository | public, nem archivált |
| Godot | 4.2.2 |
| Project version | 0.1.0 |
| Main scene | `scenes/ui/main_menu.tscn` |
| Multiplayer | ENet + Godot RPC |
| Server port | 4545 |
| Max players | 2, más érték nem támogatott |
| Card model | `Area3D` scene-node |
| Blueprint model | `Node3D` scene + Card child |
| Player model | `Resource` Card-arrayekkel |
| Zone identity | location + index |
| Stable instance ID | nincs |
| State version | nincs |
| Request ID | nincs |
| Action log | packet history, de nem canonical replay |
| RNG | globális seed szinkronizálva |
| Deck shuffle | a vizsgált forrásban nem talált |
| Hidden projection | vizuális cover/hide; teljes deckcode minden kliensnek |
| Module system | autoload module registry + hook chain |
| Anticheat | packetenkénti core + module validation |
| Tests | nem talált |
| CI | nem talált |
| License | GPL-3.0 |
| AETERNA-prioritás | P1 – moduláris Godot prototípus és negatív authority-referencia |

# 2. Vezetői összefoglaló

A projekt ambiciózus Godot-rewrite a szerző korábbi `Hearthstone.js` rendszeréből.

A fő rétegek:

```text
Game singleton
├── Player Resource
├── Card Area3D
├── Blueprint Node3D
├── Packet dispatcher
├── Multiplayer service
├── Anticheat service
├── Deckcode service
├── Module registry
└── Godot scene/UI/presentation

Modules
├── Armor / Attack / Health
├── Type
│   ├── Hero
│   ├── Hero Power
│   ├── Minion
│   └── Spell
├── Keyword / Taunt
├── Location / Layout
│   ├── Hand
│   ├── Deck
│   ├── Board
│   ├── Graveyard
│   ├── Hero
│   └── Hero Power
└── Rarity
```

A rendszer több olyan elvet próbál megvalósítani, amely az AETERNA szempontjából
tanulságos:

- feature-modulok és függőségek;
- központi hooklista;
- packet type allowlist;
- packetenkénti szervervalidáció;
- module-level anticheat;
- ENet authority RPC;
- közös RNG-seed;
- kártyaszerkesztő és automatikus ID-javaslat;
- deckcode;
- presentation-layout külön module callbackekkel.

A legfontosabb ellenkövetkeztetés:

> A rendszer „azonos szimuláció minden peer-en” modellt használ, nem viewer-projected
> authoritative state-et. Emiatt a rejtett információk, a stabil identity és a
> determinisztikus transition contract nem felel meg az AETERNA követelményeinek.

# 3. Repositoryérettség

A README saját szavai szerint:

- a projekt nagyon korai;
- egyáltalán nem használatra kész;
- a kívánt Hearthstone.js feature parity messze van;
- a featurelista félkész;
- „minden más” hiányzik.

A repository technikailag fejlettebb, mint a README alapján várható, de a source sok
`TODO`, `HACK`, `CRITICAL`, experimental jelölést és ismert regressziót tartalmaz.

A commit historyben külön commitok vannak például:

- Godot 4.2.2 upgrade;
- module split;
- module performance bug;
- module regression;
- card summon;
- internal wiki;
- RNG synchronization.

Ez aktív prototípusfejlődést mutatott 2024-ben, nem production kész állapotot.

# 4. Project autoload-architektúra

A `project.godot` központi autoloadjai:

```text
Game
Multiplayer
Deckcode
UPnP
Packet
Anticheat
Settings
Modules
```

és további featuremodulok:

```text
Armor
Attack
Health
Keyword
Taunt
Location
Layout
Hand/Deck/Board/Graveyard/Hero/HeroPower layouts
Rarity
Type
Hero/HeroPower/Minion/Spell
Tribe
SpellSchool
```

Pozitív:

- a featurefelelősségek nevekkel elkülönülnek;
- module dependency deklarálható;
- module kikapcsolható;
- feature mesh és packet regisztrálható;
- card type, keyword, rarity és layout bővíthető.

Kockázat:

- sok autoload globális mutable state;
- initialization order kritikus;
- module set kliensenként eltérhet;
- nincs server-authoritative module manifest;
- nincs module schema/version/hash handshake;
- a module kikapcsolása rules contractot módosíthat.

AETERNA-ban a rules module set a C# engine build/runtime package allowlist része, nem
kliensoldali config.

# 5. Card–Blueprint modell

## 5.1 Blueprint

A Blueprint egy `Node3D`, amely:

- exportált kártyaadatokat tárol;
- Card childot tart;
- kártyascriptet futtat;
- scene-ként authorolható;
- setupkor a scene tree root alá kerül;
- module hookokat kérhet.

Fő mezők:

```text
card_name
text
cost
texture
classes
tags
modules
collectible
id
attack
health
armor
hero_power_id
durability
cooldown
```

## 5.2 Card

A Card egy `Area3D`, amely egyszerre:

- rules instance;
- zoneelem;
- 3D mesh;
- inputtarget;
- drag/hover controller;
- hidden-info presentation;
- ability registry;
- packetcímzési objektum;
- animation host;
- death lifecycle.

Ez az AETERNA számára túl sok felelősség egy osztályban.

## 5.3 Blueprint lookup

`Blueprint.create_from_id()`:

1. rekurzívan bejárja a teljes `cards/` mappát;
2. minden `.tscn` scene-t sorban példányosít;
3. ID-egyezésnél a blueprintet a scene tree-be teszi;
4. Card node-ot hoz létre;
5. module hookokat futtat.

Kockázatok:

- O(n) filesystem scan minden lookupnál;
- scene-instantiation csak ID-kereséshez;
- side effectes lookup;
- performance és lifecycle overhead;
- nincs előfordított, verziózott immutable catalog;
- nincs content hash;
- duplicate ID csak editor warning.

AETERNA megfelelője:

```text
RuntimeCardDefinitionCatalog
- immutable
- package-versioned
- validated
- stable string ID
- O(1) lookup
```

# 6. Card ID és instance identity

A Blueprint numeric `id` definícióazonosító.

Az editor `BlueprintManager`:

- minden blueprintet betölt;
- ID szerint rendez;
- duplicate ID-t jelez;
- hiányzó ID-t automatikusan kioszt;
- scene-t ment.

Ez jó authoring-segédötlet.

Korlát:

- az automatikus sorfolytonos numeric ID fájlmozgatás/branch merge esetén konfliktusos;
- nincs központi registry transaction;
- nincs stable CardInstanceId;
- a packetek Cardot location+index párral címeznek;
- indexváltozás után stale packet más lapot célozhat.

AETERNA:

```text
card_definition_id = stabil tartalmi ID
card_instance_id = mérkőzésen belüli egyedi ID
state_version = request előfeltétel
```

# 7. Player és zónák

A Player `Resource` a következő Card-arrayeket tartja:

```text
hand
deck
board
graveyard
```

A Card `location_array` getter a location stringből választja ki az arrayt.

A Card `index` mindig:

```text
location_array.find(self)
```

Ez egyszerű, de:

- a Card node maga a domainobjektum;
- zone identity az array-sorrendtől függ;
- párhuzamos packeteknél index drift;
- hidden zone is teljes Card-node array;
- nincs zone version;
- nincs stable order key.

A `Player.hero` getter globálisan keres és `[0]` indexel, tehát hiányzó hero esetén
hibára futhat.

A `Player.get_from_id()` minden nem nulla ID-t player2-ként kezel, nincs explicit
érvénytelen-ID rejection.

# 8. Hidden information

## 8.1 Vizuális hidden modell

A Card `is_hidden` getter:

- board/hero/hero power esetén public;
- local player Hand esetén látható;
- opponent ownership esetén kliensen hidden;
- deck/graveyard esetén általában hidden;
- mesh/text/labels és cover visibilityt állít.

Ez presentation szinten használható.

## 8.2 Teljes deck leak

A szerver:

```text
Multiplayer.start_game.rpc(deckcode1, deckcode2)
```

hívással mindkét teljes deckcode-ot elküldi minden kliensnek.

A kliens ezután:

- beállítja mindkét Player deckcode-ját;
- mindkét teljes paklit importálja;
- minden Card Blueprintjét létrehozza.

Következmény:

- az ellenfél teljes decklistája kliensmemóriában van;
- a hidden Card csak vizuálisan fedett;
- card name, cost, type, class, ability script és texture elérhető;
- módosított kliens egyszerűen kiolvashatja.

## 8.3 Deck order

A vizsgált source-ban nem találtunk deck shuffle hívást.

Az import a deckcode sorrendjében hozza létre a lapokat, a draw pedig a deck array végéről
vesz le.

A legutóbbi commit ugyan egységes globális RNG-seedet állít minden kliensen, de:

- nem találtunk hozzá deck shuffle-t;
- a seed minden kliens számára ismert;
- nincs privát szerver RNG;
- nincs viewer-safe draw projection.

Ha később shuffle kerülne a kliensekre, a közös seed miatt az ellenfél sorrendje akkor is
rekonstruálható lenne.

AETERNA-ban a deck order kizárólag szerveroldali hidden state.

# 9. Multiplayer lifecycle

A Multiplayer service:

- ENet servert vagy clientet hoz létre;
- server configot tölt;
- module configot tölt;
- UPnP-t próbál;
- deckcode-ot fogad;
- player ID-t oszt;
- configot RPC-zik;
- scene-t vált;
- game setupot RPC-zik.

Pozitív:

- authority RPC annotációk;
- deckcode szervervalidáció;
- ban list;
- configurable anticheat;
- disconnect kezelés;
- localhost debug multi-instance workflow.

Kockázatok:

- module config nem server-enforced;
- content version nincs egyeztetve;
- deckcode response az egyetlen dokumentált request/response;
- peer disconnect bármelyik játékosnál teljes quit;
- `quit()` ismert klienscrash kommentet tartalmaz;
- nincs reconnect;
- nincs full state resync;
- nincs match ID;
- nincs protocol version;
- nincs package hash;
- deckcode-wait polling loopnak nincs timeout.

# 10. Packet rendszer

## 10.1 Packet type allowlist

Core packetek:

```text
Attack
Create Card
Draw Cards
End Turn
Play
Reveal
Set Drag To Play Target
Summon
Trigger Ability
```

Module új packetet regisztrálhat.

## 10.2 Packet schema

A packet logikai mezői:

```text
packet_type: StringName
player_id: int
info: Array
```

A packet history:

```text
[sender_peer_id, packet_type, player_id, info]
```

Pozitív:

- packet type allowlist;
- readable logging;
- reliable RPC;
- szervervalidáció broadcast előtt;
- module anticheat;
- info type/length check.

Korlát:

- `info` továbbra is pozicionális Array;
- nincs schema version;
- nincs request ID;
- nincs expected state version;
- nincs result state version;
- nincs correlation;
- nincs atomic action response;
- packet history nem canonical event log.

## 10.3 Actor resolution hiba

A szerver a packet type és info teljes validálása előtt:

```text
actor_player = players.values().filter(...)[0]
```

alapú lookupot végez a kliens által megadott `player_id` értékkel.

Érvénytelen ID vagy hiányos players state esetén:

- üres filter `[0]`;
- runtime hiba;
- packet validation előtti crash.

Az actor identityt a sender peerből kell származtatni, nem kliensmezőből.

## 10.4 Server packet bypass

A szerver által küldött packetek bypassolják az anticheatet.

A code maga warningot ír:

```text
server packets bypass anticheat
```

Authority oldalon ez részben természetes, de az AETERNA-ban ugyanaz a precondition
pipeline kezelje a server/system actionöket is, külön privilege-jelöléssel.

# 11. Anticheat

## 11.1 Erősségek

A core anticheat ellenőrzi többek között:

- packet info shape/type;
- attacker/target létezés;
- turn ownership;
- actor authorization;
- mana;
- Hand location;
- board capacity;
- exhaustion;
- attack count;
- type-specific constraints;
- module-specific szabályokat, például Taunt.

Anticheat consequence:

```text
DROP_PACKET
KICK
BAN
```

A default level `-1`, azaz maximális.

## 11.2 Korlát

Az anticheat:

- nem state transition engine, hanem packet filter;
- ugyanazokat a rules preconditionöket részben kliens és szerver is duplikálja;
- player state scene-node-okból áll;
- indexalapú target driftet nem old meg;
- nincs expected state version;
- nincs idempotency;
- nincs final revalidation közvetlenül commit előtt;
- nincs request-specific rejection response.

A server csak warningot/logot kap; nincs strukturált `ActionRejected`.

# 12. Replikált simulation vs authority

A szerver a validált packetet:

```text
_accept.rpc(...)
```

hívással minden kliensen és saját magán lefuttatja.

Minden peer:

- Cardot keres;
- manát módosít;
- zónát módosít;
- abilityt futtat;
- sebzést számít;
- animationt vár;
- eventet emittál.

Ez lockstep-szerű replicated simulation.

Kockázat:

- kliens content/module/config eltérés;
- eltérő animation setting;
- eltérő frame timing;
- plugin/module hook order;
- floating point és scene timing;
- hiányzó packet vagy későbbi packet;
- local mutation;
- nincs state hash és reconciliation.

AETERNA architektúra:

```text
Godot ActionIntent
→ C# engine validation
→ atomic MatchState commit
→ viewer-projected snapshot/event
→ Godot animation
```

# 13. RNG és determinisztika

A legutóbbi commit:

1. a szerveren választ 32 bites seedet;
2. authority RPC-vel minden peeren `seed()`-et hív;
3. utána player ID-t is ugyanebből a globális RNG-ből választ.

Ez javítja az azonos RNG-sorozat esélyét.

Nem elég:

- globális RNG-t UI/effect kód is fogyaszthat;
- nincs külön rules RNG stream;
- nincs decision index;
- nincs RNG event;
- nincs state hash;
- nincs replay;
- nincs cross-peer audit;
- module/content eltérés más random call-számot okozhat;
- a seed kliens számára ismert, tehát hidden random nem védett.

AETERNA:

```text
RulesRng
CosmeticRng
AiRng
```

külön stream, szerveroldali döntésnaplóval.

# 14. Module registry

A Module base támogat:

- name;
- dependency;
- load/unload;
- hook handler;
- card mesh;
- packet registration.

Ez a projekt egyik legerősebb clean-room tanulsága.

AETERNA megfelelő:

```text
EffectModuleDescriptor
- module_id
- schema_version
- dependencies
- supported_hooks
- deterministic
- server_only
- presentation_only
```

Kötelező különválasztás:

- rules module;
- validation module;
- presentation module;
- tooling module.

# 15. Module request queue hiba

A `Modules.request()` meghívja a `wait_in_queue()` függvényt.

A queue implementation:

- `_processing` false indul;
- ha `_queue` üres, visszatér;
- nem állítja `_processing = true` értékre;
- első kérésnél nem tesz elemet a queue-ba;
- a vizsgált fájlban nincs más `_processing` assignment;
- `stopped_processing` emit sem látható.

Ez alapján a dokumentált request serialization ténylegesen nem működik.

Párhuzamos hook requestek:

- összefuthatnak;
- signal-alapú waitet összekeverhetnek;
- ability order driftet okozhatnak;
- deadlock/rossz response párosítást okozhatnak.

# 16. Hook order és effect resolution

A `Modules.request()`:

```text
for module in enabled_modules.values()
    for hook_handler
        result = result and await handler(...)
```

Következmények:

- order Dictionary iteration/load ordertől függ;
- explicit priority nincs;
- dependency nem jelent hook execution ordert;
- egy false után a short-circuit miatt későbbi handler nem fut;
- nincs immutable preflight/commit/post-event szakasz;
- handler közvetlen state-et módosíthat;
- await és animation beépülhet a rules resolutionbe.

AETERNA javaslat:

```text
PRE_VALIDATE
VALIDATE
PRE_COMMIT
COMMIT
POST_COMMIT
PRESENTATION
```

explicit sorrenddel.

# 17. Type module konkrét hibák

A `types` tömb Dictionary rekordokat tárol:

```text
{"name": type, "summonable": bool}
```

Az `is_summonable()` viszont:

```text
card.modules.types in types.filter(...)
```

kifejezéssel egy type Arrayt hasonlít Dictionary-listához.

Ez várhatóan mindig false.

Az `unregister_type(type)`:

```text
types.erase(type)
```

hívást használ, miközben a tömb Dictionaryket tartalmaz, tehát a type nem kerül ki.

Lehetséges következmény:

- summonable board-space anticheat nem aktiválódik;
- summon packetet helytelenül tilt/engedi;
- module unload nem tisztítja a registryt.

# 18. Play transaction és refund

A core `_accept_play_packet()`:

1. Card lookup;
2. pre-event;
3. visibility reveal;
4. `CARD_PLAY_BEFORE`;
5. mana levonás;
6. armor hozzáadás;
7. animation tween;
8. `CARD_PLAY`;
9. szükség esetén `_refund()`;
10. post-event.

A `_refund()` csak:

```text
player.mana += cost
```

műveletet végez.

Nem rollbackeli:

- armor hozzáadást;
- target state-et;
- ability side effectet;
- module signal subscriptiont;
- létrehozott Cardot;
- RNG fogyasztást;
- animation/lifecycle állapotot.

Ez nem atomic transaction.

# 19. Minion play order

A Minion module:

1. Battlecryt triggerel;
2. megvárja;
3. refund esetén megszakít;
4. csak utána summonolja a Cardot.

A source maga „gross” megoldásként dokumentálja.

Kockázat:

- a battlecry a boardon kívül fut;
- board-presence alapú effekt más eredményt ad;
- passzívok és replacement effectek sorrendje eltérhet;
- battlecry irreverzibilis side effectet végezhet refund előtt;
- általános transaction nincs.

# 20. Spell resolution

A Spell module:

1. Cast trigger;
2. wait;
3. refund check;
4. `card.location = None`.

A Card update később queue_free-zza.

Korlát:

- graveyard helyett None/destroy;
- effect és zone transition nem atomic;
- local scene update timerre támaszkodik;
- refund csak mana;
- ability callback közvetlen state mutationt végez.

# 21. Példakártyák

## 21.1 The Coin

- közvetlenül `player.mana += 1`;
- minden peeren fut;
- effect animationt vár;
- nincs külön typed ManaGained event.

A rules outcome az animation setting és await timing környezetében fut.

## 21.2 Fireblast

- targetet Card/Player objectként tárol;
- Card targetnél közvetlen `health -= 1`;
- Player targetnél `damage(1)`;
- a két targettípus eltérő hook/damage pipeline-t használ;
- null/invalid target esetén csendben success.

## 21.3 Brann

A Brann példakártya:

- global `Game.card_played` signalra csatlakozik;
- minden kijátszott Cardon `Cast` abilityt próbál triggerelni;
- nem Battlecryt;
- nem ellenőrzi a játékost;
- nem ellenőrzi, hogy Brann Boardon van-e a trigger idején;
- a callback lifecycle csak death signalra támaszkodik.

Ez jó példa arra, hogy a signal-hook rugalmasság rules pontatlansághoz vezethet.

# 22. Hidden target és Drag To Play

A Card a targetet object referenciaként tárolja:

```text
drag_to_play_target
```

A kliens előbb külön `Set Drag To Play Target` packetet küld, utána Play packetet.

Kockázat:

- két külön network action;
- nincs transaction/correlation ID;
- közben state/index változhat;
- stale target;
- másik Play request felhasználhatja a targetet;
- target object minden peeren külön scene-node.

AETERNA-ban a target ugyanazon `PlayCardRequest` payload része.

# 23. Card update loop

Minden Card saját 0,1 másodperces update Timert használ.

Minden tick:

- blueprint mezőket ellenőriz;
- hidden visibilityt újraszámol;
- texturát és labelt ír;
- `CARD_UPDATE` module requestet indít;
- layoutot indít;
- death checket futtat.

Sok Card esetén:

- sok Timer;
- sok hook;
- sok layout;
- sok material update;
- scene-tree overhead;
- async request race.

A rules state nem függhet periodikus presentation pollingtól.

# 24. Rarity module

Erősség:

- rarity registry;
- rarity → color;
- külön mesh;
- moduleként kikapcsolható.

Korlát:

- minden Cardnak kötelező `rarities` module field;
- hiánynál assert;
- minden Card update új `StandardMaterial3D` példányt készít;
- 0,1 s update mellett material churn;
- rarity csak szín és mesh;
- nincs printing/provenance/foil kapcsolat.

A fóliakutatáshoz képest ez csak egyszerű rarity marker, nem végleges AETERNA-minta.

# 25. Layout system

A layoutokat location szerint callbackek regisztrálják.

A Hand layout:

- íves pozíció;
- indexalapú forgatás;
- ellenfél kéz 180°;
- player/opponent súly;
- animation vagy instant fallback.

Ez hasznos presentationötlet.

Kockázatok:

- Card rules indexből számol layoutot;
- dictionaryk RID szerint Card node-ot követnek;
- hover esetén `_layout_tweens[rid].kill()` úgy is futhat, hogy nincs ilyen tween;
- layout hookok async rules hookrendszerben futnak;
- `stabilize_layout_while()` rules effectet és presentation freeze-t összeköt;
- layout module nélkül gameplay kód is `LayoutModule`-ra támaszkodik.

AETERNA-ban:

```text
CardViewModel.zone_index
→ HandLayoutView
```

presentation-only.

# 26. Death lifecycle

A Card update loop észleli `health <= 0` állapotot.

A death flow:

- pre-signal;
- scale animation;
- Graveyard location;
- collision disable;
- hidden update;
- post-signal;
- module hook.

Kockázat:

- periodic polling indítja;
- animation előtt/után rules state eltér;
- `should_die` presentation flag rules gate;
- death prevention signal callbackból state mutation;
- nincs state-based action fixpoint;
- több egyszerre haló Card order frame- és hookfüggő.

AETERNA-ban a C# engine state-based action queue rendezi a halálokat, animation csak eventet követ.

# 27. Deckcode

Erősség:

- kompakt deckcode;
- hex card ID;
- copy run-length szerű definíció;
- hero ID;
- collectible és deck size validation;
- server deckcode fogadás.

Kockázatok:

- split size nincs ellenőrizve indexelés előtt;
- invalid hex ID null blueprintet okozhat;
- null dereference a Card accessnél;
- validáció scene-eket és Card node-okat hoz létre;
- validation side effectes és drága;
- default `4/1:30/1` explicit bypass;
- class legality nincs;
- copy limit nincs;
- rarity/legendary limit nincs;
- content version nincs;
- deckcode minden kliensnek elküldve.

# 28. Card creator és BlueprintManager

## Használható tanulság

- editor script generál card foldert, scriptet és scene-t;
- script template;
- filesystem rescan;
- BlueprintManager ID-diagnosztika;
- duplicate/missing ID warning.

AETERNA-ban ennek megfelelő tool lehet:

```text
CardDefinitionCreator
CardSchemaValidator
StableIdRegistry
PreviewGenerator
```

De az output nem közvetlen scene-authority, hanem validált runtime package rekord.

# 29. Content/module version mismatch

A rendszer nem egyeztet:

- repository version;
- content hash;
- card catalog hash;
- enabled module list;
- module version;
- server config schema;
- packet schema.

Két kliens eltérő builddel:

- más ability scriptet futtathat;
- más module hook ordert kaphat;
- más Card ID-t oldhat fel;
- más RNG-hívást végezhet;
- más board state-re juthat.

A server nem küld authoritative snapshotot, így nincs reconciliation.

# 30. Biztonság

Pozitív:

- sender peer lookup;
- ban/kick;
- server-only config;
- packet allowlist;
- info type validation;
- turn/owner/mana checks;
- module anticheat;
- UPnP fallback.

Kockázat:

- opponent deck teljes leak;
- actor Player kliens player_id mezőből is befolyásolt;
- invalid actor lookup packet validation előtt;
- stable instance ID hiánya;
- state version hiánya;
- replay protection hiánya;
- duplicate/idempotency hiánya;
- local module config;
- local content scripts;
- server packets teljes bypass;
- assert network input kezelésben;
- ENet encryption/auth bizonyíték nem talált.

# 31. Tesztelés és CI

Nem találtunk:

- GUT/GdUnit suite-ot;
- unit test mappát;
- integration network testet;
- hidden information testet;
- deterministic replay testet;
- GitHub Actions workflow run;
- combined status checket.

A source-ban számos TODO és ismert bugkomment van, de automated regression proof nincs.

# 32. Licenc és IP

## 32.1 Kód

Root licenc:

```text
GPL-3.0
```

Közvetlen kódintegráció az AETERNA-ba nem ajánlott.

## 32.2 Hearthstone név és tartalom

A projekt Hearthstone rewrite:

- Hearthstone classnevek;
- kártyanevek;
- hero/hero power;
- rules terminológia;
- kártyaadat és artwork.

Ezek AETERNA assetként vagy tartalomként nem használhatók.

Átvehető csak az általános architekturális elv clean-room módon.

# 33. Konkrét hibajegyzék

## P0 – authority és hidden information

1. mindkét teljes deckcode broadcast minden kliensnek;
2. mindkét teljes deck Blueprint létrejön minden kliensen;
3. hidden flag csak vizuális;
4. stable CardInstanceId nincs;
5. packet location+index alapján címez;
6. expected state version nincs;
7. request/correlation ID nincs;
8. client/server replicated simulation, nem viewer projection;
9. local module set eltérhet;
10. content hash handshake nincs.

## P0 – konkrét implementáció

11. Module request queue nem állít `_processing` értéket és nem serializál;
12. TypeModule `is_summonable()` hibás összehasonlítást használ;
13. TypeModule `unregister_type()` Dictionary-arrayből StringName-et töröl;
14. actor lookup packet validálás előtt `[0]` indexel;
15. deckcode parser structural check nélkül indexel;
16. unknown card ID null dereference;
17. refund csak manát állít vissza;
18. Minion battlecry summon előtt irreverzibilis side effectet futtathat;
19. Drag target és Play két külön packet;
20. deck shuffle hívás nem talált.

## P1 – lifecycle és presentation

21. Card 0,1 s polling update;
22. Rarity minden updatekor új material;
23. layout hover ág missing tweenre `kill()`-t hívhat;
24. Card `_exit_tree()` parentet queue_free-zza;
25. Player hero getter `[0]` crash;
26. Player ID lookup minden nem nullát player2-re képez;
27. death animation rules transition előtt fut;
28. animation settings resolution timingot módosíthat;
29. Brann sample hibás `Cast` trigger;
30. Fireblast Card damage bypassolja a közös damage pipeline-t;
31. Multiplayer quit ismert crash komment;
32. module dependency unload rekurzió circularity guard nélkül.

# 34. AETERNA számára használható minták

1. moduldescriptor és dependency deklaráció;
2. explicit Hook enum;
3. packet type allowlist;
4. core + module validation réteg;
5. server-configurable validation consequence;
6. editoros CardDefinition generátor;
7. duplicate/missing stable ID validator ötlete;
8. deckcode parser/validator mint külön toolingréteg;
9. Card layout location callbackekkel;
10. presentation moduleként Attack/Health/Rarity mesh;
11. keyword module például Taunt;
12. debug többpéldányos localhost indítás;
13. server-selected RNG seed fogalma;
14. module/config dokumentáció;
15. client animation fallback.

# 35. Amit nem szabad átvenni

1. Card Area3D mint authoritative state;
2. Blueprint Node3D mint runtime definition catalog;
3. location+index packet identity;
4. teljes deckcode minden viewernek;
5. vizuális hide mint security boundary;
6. replicated effect execution minden peeren;
7. global RNG;
8. animation-await rules pipeline;
9. hook Dictionary order;
10. side-effectes validation;
11. partial refund;
12. local module config mint rules contract;
13. network input assert;
14. packet history mint replay;
15. GPL kód közvetlen másolása;
16. Hearthstone content vagy asset.

# 36. Javasolt AETERNA clean-room modulrendszer

```text
RulesModuleDescriptor
- module_id
- schema_version
- dependencies
- hooks
- execution_priority
- deterministic
- authority_scope
- content_hash
```

Hook pipeline:

```text
collect intents
→ pure validation
→ final validation
→ atomic commit
→ typed events
→ viewer projection
→ presentation hooks
```

Module handler nem kaphat Godot Node referenciát.

# 37. Javasolt kártyatartalom-rendszer

```text
CardDefinition
- stable_definition_id
- schema_version
- name_key
- type_ids
- keyword_ids
- cost
- stats
- ability_module_ids
- art_asset_id
```

```text
CardInstanceState
- instance_id
- definition_id
- owner
- controller
- zone
- zone_order
- mutable_stats
- flags
```

```text
CardViewModel
- visible_definition?
- card_back_profile
- public_stats
- selection_state
- presentation_profile
```

# 38. Javasolt multiplayer contract

```text
ActionRequest
- protocol_version
- match_id
- request_id
- actor_player_id
- expected_state_version
- action_type
- payload
```

```text
ActionResponse
- request_id
- accepted
- reason_code
- resulting_state_version
- viewer_snapshot_delta
- public_events
```

A Card target `instance_id`, nem zone index.

# 39. Javasolt hidden deck contract

Opponent viewer:

```text
OpponentDeckProjection
- card_count
- public_reveals
- public_modifiers
```

Nem tartalmazhat:

- deckcode;
- definition IDs;
- order;
- hidden card blueprint;
- private RNG seed.

# 40. Javasolt authoring pipeline

```text
Godot/editor vagy külön tool
→ source card definition
→ schema validation
→ stable ID validation
→ module dependency validation
→ package compile
→ immutable runtime catalog
→ C# engine load
→ Godot view assets
```

A BlueprintManager ötlete megtartható, a runtime scene-scan nem.

# 41. Javasolt tesztmátrix

## 41.1 Authority

- client cannot act for opponent;
- invalid player ID;
- stale state version;
- duplicate request;
- zone index change;
- illegal target;
- partial transition rollback;
- module mismatch rejection.

## 41.2 Hidden information

- opponent deckcode unavailable;
- opponent order unavailable;
- own hand visible;
- opponent hand count only;
- revealed Card public;
- RNG seed not sufficient to infer hidden order.

## 41.3 Modules

- dependency topological order;
- cycle rejection;
- deterministic priority;
- disabled module manifest;
- version/hash mismatch;
- parallel hook request serialization;
- false handler policy.

## 41.4 Content

- duplicate definition ID;
- unknown ID;
- malformed deckcode;
- class legality;
- copy limit;
- collectible flag;
- package hash;
- migration/version.

## 41.5 Determinism

- server-only rules RNG;
- action log replay;
- identical state hash;
- animations on/off same state;
- different FPS same state;
- headless vs Godot bridge same state.

# 42. AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | Stable CardInstanceId minden actionben | Engine/Contract | P0 |
| 2 | Opponent deck projection only count/public data | Projection | P0 |
| 3 | Full deckcode broadcast tiltása | Security | P0 |
| 4 | Server-only hidden deck order | Engine | P0 |
| 5 | Request ID + state version | Contract | P0 |
| 6 | Atomic action transaction | Engine | P0 |
| 7 | Pure validation és final recheck | Engine | P0 |
| 8 | Rules/presentation module szétválasztás | Architecture | P0 |
| 9 | Module manifest/version/hash | Package | P0 |
| 10 | Explicit hook priority | Engine | P0 |
| 11 | Rules RNG külön stream | Engine | P0 |
| 12 | Immutable card catalog | Runtime package | P0 |
| 13 | CardDefinition editor generator | Tooling | P1 |
| 14 | Stable ID validator | Tooling | P0 |
| 15 | Deckcode structural validator | Tooling | P1 |
| 16 | Location-based HandLayoutView | Godot | P1 |
| 17 | Attack/Health/Rarity presentation modules | Godot | P1 |
| 18 | Anticheat adversarial suite | Tests | P0 |
| 19 | Hidden-info memory inspection test | Tests | P0 |
| 20 | Következő audit: `ProjectIgnis/CardScripts` | Learning | P1 |

# 43. Bizonyítékjegyzék

| ID | Állítás | Forrás |
|---|---|---|
| E-001 | nagyon korai, nem használatra kész | `README.md` |
| E-002 | Godot 4.2, version 0.1.0, autoloadok | `project.godot` |
| E-003 | GPL-3.0 | `LICENSE` |
| E-004 | Card Area3D és hidden logic | `scenes/card.gd` |
| E-005 | Player Card-arrayek | `scripts/player.gd` |
| E-006 | Blueprint scene és filesystem lookup | `scripts/blueprint.gd` |
| E-007 | editor ID manager | `scripts/blueprint_manager.gd` |
| E-008 | card creator | `scripts/card_creator.gd` |
| E-009 | both deckcodes broadcast | `scripts/game.gd`, `scripts/multiplayer/multiplayer.gd` |
| E-010 | shared RNG seed | latest commit, multiplayer RPC |
| E-011 | packet allowlist/history/broadcast | `scripts/multiplayer/packet.gd` |
| E-012 | core/module anticheat | `scripts/multiplayer/anticheat.gd` |
| E-013 | max anticheat default | `scripts/settings.gd` |
| E-014 | module registry és hooks | `scripts/modules.gd`, `modules/module.gd` |
| E-015 | request queue bug | `scripts/modules.gd` |
| E-016 | Type summonable/unregister bug | `modules/type/type.gd` |
| E-017 | Minion pre-summon battlecry | `modules/type/minion/minion.gd` |
| E-018 | Spell resolution | `modules/type/spell/spell.gd` |
| E-019 | Taunt module | `modules/keyword/taunt/taunt.gd` |
| E-020 | rarity material update | `modules/rarity/rarity.gd` |
| E-021 | hand layout | `modules/location/layout/hand/hand.gd` |
| E-022 | layout lifecycle | `modules/location/layout/layout.gd` |
| E-023 | deckcode parser | `scripts/functions/deckcode.gd` |
| E-024 | The Coin | `cards/the_coin/the_coin.gd` |
| E-025 | Fireblast | `cards/jaina_proudmoore/hero_power/fireblast.gd` |
| E-026 | Brann | `cards/brann_bronzebeard/brann_bronzebeard.gd` |
| E-027 | nincs testtalálat | repository code search |
| E-028 | nincs status check | GitHub combined status |
| E-029 | nincs workflow run | GitHub workflow query |

# 44. Nyitott kérdések

1. A decket ténylegesen sehol nem keveri a current source?
2. Két kliens eltérő module configgal meddig marad szinkronban?
3. Animation on/off esetén eltér-e packet/effect order?
4. A module queue bug reprodukálható párhuzamos abilitykkel?
5. Type `is_summonable` valóban mindig false?
6. Invalid player ID packet crash-t okoz-e az actor lookupnál?
7. Duplicate packet két alkalommal végrehajtódik-e?
8. Zone index drift rossz Cardot céloz-e?
9. Deckcode malformed input milyen kivételt dob?
10. Unknown Blueprint ID mennyi leaked scene-node-ot hagy?
11. Rarity update material memóriaszivárgást okoz-e?
12. Hidden Card adatai mennyire könnyen olvashatók modded kliensből?
13. Shared seedből teljes hidden order reprodukálható-e?
14. Brann effect szándékosan Castot ismétel?
15. Fireblast Card damage bypass szándékos?
16. Module unload dependency iránya helyes-e?
17. Circular dependency stack overflowt okoz-e?
18. Result state headless modeban animation nélkül azonos-e?
19. UPnP és ENet security productionre alkalmas-e?
20. Internal wiki és source között van-e drift?

# 45. Végső minősítés

- **Godot architecture tanulási érték:** magas
- **Modulrendszer-ötlet:** magas
- **Editor/authoring érték:** magas
- **3D presentation érték:** közepes-magas
- **Anticheat gondolkodás:** közepes-magas
- **Server authority:** részleges
- **Hidden-information biztonság:** nagyon alacsony
- **Stable identity:** nincs
- **Atomic transition:** nincs
- **Determinism:** részleges seed-szinkron, replay nélkül
- **Content package érettség:** alacsony
- **Teszt/CI:** nincs bizonyítva
- **Kódlicenc:** GPL-3.0
- **Közvetlen dependency:** elutasítandó
- **Clean-room tanulság:** ajánlott
- **Legfontosabb AETERNA-eredmény:** a feature-modulok, editor authoring és server validation
  ötletei használhatók, de csak úgy, ha a rules state teljesen C#-ban marad, a module
  contract verziózott és determinisztikus, a kliens pedig kizárólag viewer projectiont kap
- **Elemzés státusza:** első teljes source audit elkészült
- **Következő learning cél:** `ProjectIgnis/CardScripts`

# 46. Változásnapló

## 0.1 – 2026-07-26

- elkészült a `LunarTides/Hearthstone.gd` első teljes AETERNA-központú auditja;
- ellenőrzésre került a repository, branch, HEAD commit, Godot-verzió és GPL-3.0 licenc;
- feldolgozásra került a Card, Blueprint, Player és zone modell;
- feldolgozásra került a module registry, dependency és hookrendszer;
- feldolgozásra került a Packet, Multiplayer és Anticheat réteg;
- feldolgozásra került a deckcode és editor card creator/ID manager;
- feldolgozásra került a Type, Minion, Spell, Taunt, Rarity és Layout modul;
- azonosításra került a teljes opponent deckcode és Blueprint leak;
- azonosításra került a stable instance ID/state version/request ID hiánya;
- azonosításra került a module request queue hibája;
- azonosításra került a Type summonable és unregister hiba;
- azonosításra került a non-atomic refund és Minion battlecry order;
- azonosításra került a kétpacket drag target transaction;
- azonosításra került a deck shuffle hívás hiánya;
- azonosításra került a global RNG és content/module mismatch kockázat;
- azonosításra került a periodic Card update és rarity material churn;
- rögzítésre került a hiányzó automated test és CI proof;
- elkészült az AETERNA clean-room module-, content-, packet- és projection-javaslata;
- a következő kijelölt learning projekt `ProjectIgnis/CardScripts`.
