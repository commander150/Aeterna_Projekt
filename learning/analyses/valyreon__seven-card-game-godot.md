# AETERNA – VALYREON/SEVEN-CARD-GAME-GODOT ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-26
- **Státusz:** első teljes repository-, szabály-, hálózat-, authority-, hidden-information-, lifecycle-, licenc- és AETERNA-adaptációs audit
- **Fő elemzési fájl:** `learning/analyses/valyreon__seven-card-game-godot.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Repository:** `Valyreon/seven-card-game-godot`
- **Stabil upstream URL:** `https://github.com/Valyreon/seven-card-game-godot`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `d5dd92d8d31395e8c2ffa62630278a74aa81d9fd`
- **Vizsgált commit dátuma:** 2020-12-08
- **Projekt eredeti technológiai kora:** Godot 2.1.5
- **Hálózati alap:** `TCP_Server`, `StreamPeerTCP`, `PacketPeerStream`
- **Játék:** kétjátékos Sedmice / Seven
- **Külső szabályforrás:** `https://www.pagat.com/sedma/sedmice.html`
- **Repositorylicenc:** nem talált
- **Képi assetek eredete:** a szerző szerint már nem rekonstruálható pontosan
- **CI-bizonyíték:** nincs GitHub status check vagy kapcsolt workflow run
- **AETERNA összehasonlítási bázis:** C# authoritative engine, typed action contract, expected state version, atomic transition, viewer projection és Godot presentation boundary
- **Összehasonlítási szabály:** kizárólag az AETERNA rendszeréhez mérve
- **Vizsgálati korlát:** helyi Godot 2.1.5 futtatás, kétpéldányos hálózati reprodukció és exportteszt nem történt
- **Elsődleges AETERNA-érték:** kis, teljes host–client kártyajáték; szerveroldali teljes kézállapot és kliensoldali dummy opponent hand; eredmény szerveroldali számítása
- **Elsődleges AETERNA-kockázat:** implicit coroutine game state, nyers tömbprotokoll, részleges szervervalidáció, kliensoldali optimista mutation, scene-node authority, seed nélküli RNG, hiányzó licenc és asset-provenance
- **AETERNA-döntés:** közvetlen integráció nem; hidden-information projection és kis multiplayer flow clean-room tanulságként használható

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Repository | `Valyreon/seven-card-game-godot` |
| Default branch | `master` |
| Vizsgált commit | `d5dd92d8d31395e8c2ffa62630278a74aa81d9fd` |
| Commitüzenet | `added table with screenshots to readme` |
| Commitok száma a vizsgálatkor | 4 |
| Repository állapot | public, nem archivált |
| Godot | 2.1.5 |
| Újabb Godot-kompatibilitás | a README szerint Godot 3.0+-ban nem fut |
| Játékosok | 2 |
| Pakli | 32 lap |
| Rangok | A, 7, 8, 9, 10, J, Q, K |
| Színek | 4 francia szín |
| Szerver | a host játékpéldánya |
| Kliens | egy távoli játékos |
| Port | 3560/TCP |
| Üzenetformátum | pozicionális Godot Array / Variant |
| Szerveroldali teljes deck | igen |
| Szerveroldali mindkét kéz | igen |
| Kliens saját kézidentitás | igen |
| Kliens ellenfélkéz-identitás | nem; dummy count |
| Szerveroldali pontszám | igen |
| Stable card instance ID | nincs |
| Match/session ID | nincs |
| State version | nincs |
| Request ID | nincs |
| Replay/event log | nincs |
| Reconnect/resync | nincs |
| Automatizált teszt | nem talált |
| CI | nem talált |
| Repositorylicenc | nem talált |
| AETERNA-prioritás | P2 – kis multiplayer és hidden-hand tanulási referencia |

# 2. Vezetői összefoglaló

A projekt valóban teljes, játszható kis multiplayer kártyajátékot céloz:

```text
Host
├── teljes Deck
├── host valódi Hand
├── kliens valódi Hand
├── Pile
├── két Graveyard
├── szabály- és pontszámítás
└── TCP kapcsolat

Client
├── saját valódi Hand
├── ellenfél DummyOpponentHand
├── saját Pile projection
└── eredménykijelző
```

A legjobb tanulsága:

> a szerver tárolja az ellenfél valódi lapjait, miközben a kliens csak az ellenfél
> lapjainak darabszámát és a nyilvánossá vált kijátszásokat kapja meg.

Ez az AETERNA viewer projection alapelvével összhangban áll.

A rendszer ugyanakkor nem production authoritative protokoll:

- az explicit phase/state helyett a futó `while`/`yield` kódpozíció jelenti az állapotot;
- a kliens nyers rank/suit üzenetet küld;
- nincs action request/response;
- nincs expected state version;
- a szerver nem ellenőrzi minden kliensparancs kontextusjogosultságát;
- a kliens szerverelfogadás előtt módosítja saját kéz- és pile-state-jét;
- a Deck, Hand, Pile és Card scene-node objektumok egyben rules state-ek;
- nincs reprodukálható RNG, replay vagy resync.

# 3. Repository és projektérettség

A repository rövid, négycommitos történetű, régi projekt feltöltése.

A legutóbbi commit csak README-screenshot táblát adott hozzá. A játék forrása a korábbi
első commitban már lényegében jelen volt.

A README kifejezetten rögzíti:

- Godot 2.1.5 szükséges;
- Godot 3.0 vagy újabb nem támogatott;
- internetes hostoláshoz a 3560-as port továbbítása szükséges;
- a képek pontos eredete már nem ismert.

Ez tanulási snapshotként értékes, production dependencyként nem.

# 4. Szabályforrás és implementált változat

A README a Pagat Sedmice szabályoldalára hivatkozik.

## 4.1 Forrásoldali alapok

A hivatkozott szabály szerint:

- 32 lapos francia pakli;
- A, K, Q, J, 10, 9, 8, 7;
- négy lapos kezdőkéz;
- bármely lap kijátszható;
- az eredeti vezető rangjával azonos lap vagy hetes veszi át a vezetést;
- az utolsó ilyen lap nyeri az ütést;
- ütés után a győztes húz először;
- az ászok és tízesek pontlapok;
- a horvát változatban nincs külön utolsóütés-pont, döntetlennél az utolsó ütés dönt.

## 4.2 Megvalósított deck

A Deck:

```text
[1, 7, 8, 9, 10, 11, 12, 13] × 4 suit
```

tehát pontosan 32 lapot hoz létre.

## 4.3 Kijátszási feltétel

A program:

- üres pile esetén bármely lapot enged;
- páratlan pile-méretnél bármely lapot enged;
- páros pile-méretnél csak az eredeti vezető rangját vagy egy hetest enged.

Ez a folytatott ütés alapját jól modellezi.

## 4.4 Dokumentált szabálytól eltérő folytatás

A hivatkozott szabály szerint, ha a vezető játékos a két lap után továbbra is nyer,
az ütés automatikusan véget ér.

A program ehelyett a vezetőnek választást ad:

```text
elviszi az ütést
vagy
azonos ranggal/hetes lappal tovább folytatja
```

Ez lehet helyi változat, de a repository nem dokumentálja külön.

## 4.5 Húzási sorrend eltérése

A szabály szerint az ütés győztese húz először.

A szerverkód minden újraosztási ágban:

```text
serverHand.add_to_hand(...)
clientHand.add_to_hand(...)
```

sorrendben húz.

Ez akkor hibás, amikor a kliens nyerte az ütést, mert a kliens helyett a szerver kapja
a következő decklapot.

A sorrend a kártyák rejtett identitását és a következő döntéseket is módosítja.

## 4.6 Pontozás

A Graveyard:

- ászért 1 pont;
- tízesért 1 pont;
- más lapért 0 pont

értéket ad.

Külön utolsóütés-pont nincs. Pontazonosságnál az `is_server_leading` alapján az utolsó
ütés győztese dönt.

Ez a horvát, 80 pontos változat egyszerűsített 0–8 skálájához áll legközelebb.

A program egyetlen leosztás után eredményt hirdet; nem valósít meg 120 pontos
többleosztásos mérkőzést.

# 5. Card modell

A Card egy `Area2D`, amely egyszerre:

- rank/suit adat;
- face-up állapot;
- texture resolver;
- inputobjektum;
- scene-node;
- signalsource.

## 5.1 Pozitívum

A 32 lapos deckben a rank+suit pár egyedi, így ezen szűk játéknál a szerver meg tudja
keresni a kliens által megnevezett lapot.

## 5.2 AETERNA-korlát

A rank+suit nem általános instance identity.

Az AETERNA minimum:

```text
card_definition_id
printing_id
card_instance_id
owner_player_id
controller_player_id
zone_id
zone_index
```

## 5.3 Busy-loop hiba

A `Card.apply()` több helyen:

```gdscript
while has_node("CardSprite") == false:
    pass
```

üres várakozó ciklust használ.

Ha a scene hibás vagy a child nem létezik:

- a főszál 100%-os CPU-val beragad;
- nincs timeout;
- nincs error;
- nincs recovery.

Production kódban node dependency `_ready()`-ben vagy explicit invariant checkkel
kezelendő.

## 5.4 Assetútvonal

A texture index:

```text
suit * 13 + rank
```

A kód közvetlen fájlútvonalat képez és runtimeban `load()`-ol.

AETERNA-ban asset ID → manifest → előellenőrzött resource út szükséges.

# 6. Deck modell

A Deck scene-node listában tárol Card node-okat.

## 6.1 Erősség

- explicit 32 lapos konstrukció;
- `draw()`;
- `cards_remaining()`;
- ürességkezelés.

## 6.2 RNG

A shuffle:

```gdscript
randomize()
randi() % cards_in_deck.size()
```

alapú.

Hiányzik:

- rögzített seed;
- RNG stream;
- döntésnapló;
- unbiased shuffle bizonyíték;
- replay;
- reprodukálható teszt.

A moduloalapú választás elméleti bias-t is hordozhat a generátor tartományától függően.

AETERNA:

```text
EngineRandom.Shuffle(zone_id, seed, decision_index)
```

és typed shuffle event.

# 7. Hand modell

A Hand:

- Card node-okat tárol arrayben;
- childként birtokolja őket;
- clickből `card_played` signalt emittál;
- eltávolítja és lecsatolja a lapot;
- rank/suit szerint keres.

A kéz sorrendje és pozíciója ugyanabban az objektumban rules/presentation state.

AETERNA-ban:

```text
C# HandZoneState
Godot HandView
```

külön szükséges.

# 8. Pile modell

A Pile:

- Card node-okat tárol;
- az első lap rankját `leading_card` mezőben őrzi;
- a pile paritásából következtet a döntési pontra;
- vizuális eltolást is végez.

Pozitív:

- az eredeti lead rank stabilan megmarad;
- a lapok száma alapján egyszerűen felismeri a pár végpontot.

Korlát:

- nincs trick ID;
- nincs play index;
- nincs actor;
- nincs authoritative transition history;
- a paritás helyettesíti az explicit phase state-et;
- a rules és a vizuális stack ugyanaz az array.

# 9. Graveyard és pontszámítás

A Graveyard `get_points()`:

- végigiterál a kártyákon;
- számolja az ászokat és tízeseket;
- `queue_free()`-t hív minden Cardra.

Ez azt jelenti, hogy a pontszámítás:

- nem pure;
- megsemmisíti a presentation node-okat;
- második futásnál stale referenciákat hagyhat;
- nincs külön captured-card domain state.

AETERNA-ban a pontozás pure query legyen a MatchState-en.

# 10. Host-authority modell

A host process:

- hozza létre a decket;
- kever;
- oszt;
- tárolja mindkét valós kezet;
- kezeli a pile-t;
- számolja mindkét graveyardot;
- elküldi az eredményt.

Ez valódi részleges authority.

A legjobb tanulság:

> a távoli kliens nem tárolhatja az ellenfél rejtett lapjainak identitását.

Korlát:

- a host maga is játékos;
- a host process memóriájában a kliens teljes keze látható;
- nincs dedicated server;
- a host technikailag csalhat.

Az AETERNA-nak explicit trust model vagy dedicated authoritative host szükséges.

# 11. Kliensoldali hidden-information projection

A kliens:

- a saját lapjainak rank/suit adatait megkapja;
- az ellenfél kezét `DummyOpponentHand` darabszámként tartja;
- az ellenfél kijátszott lapját csak kijátszáskor kapja meg;
- húzásnál csak a saját új lapjait kapja;
- az ellenfél dummy countja nő.

Ez a repository legerősebb AETERNA-tanulsága.

Javasolt AETERNA-contract:

```text
OpponentHandProjection
- card_count
- public_modifiers
- revealed_instance_ids
```

Ne legyen benne rejtett CardDefinition vagy printing információ.

# 12. DummyOpponentHand

A DummyOpponentHand:

- `number_of_cards` számlálót tart;
- előre létrehozott hátlap Sprite-okat mutat/elrejt;
- nem tárol valódi ellenféllap-identitást.

Erősség:

- jó minimális projection boundary.

Kockázat:

- nincs negatívérték-guard;
- nincs maximum;
- csak négy Sprite készül;
- duplikált/stale packet count driftet okozhat;
- nincs server snapshot alapján történő korrekció.

AETERNA-ban minden action response után authoritative viewer snapshot korrigálja a countot.

# 13. Hálózati protokoll

A protokoll pozicionális Array üzeneteket használ.

Példák:

```text
["start", rank, suit, ...]
["throw", rank, suit]
["server", "throw", rank, suit]
["carry_pressed"]
["take_pressed"]
["confirm", draw_count, rank, suit, ...]
["result", server_points, client_points]
["yes"]
["no"]
```

## 13.1 Hiányzó mezők

- protocol version;
- match ID;
- session ID;
- player ID;
- request ID;
- correlation ID;
- expected state version;
- action type enum;
- payload schema;
- response status;
- rejection reason;
- server state version;
- checksum;
- maximum collection length.

## 13.2 Pozicionális törékenység

A kód közvetlenül olvassa:

```text
packet[0]
packet[1]
packet[2]
...
```

Nincs length/type validation.

Egy üres, rövid vagy rossz típusú packet:

- indexhibát;
- hibás loop countot;
- invalid Card konstrukciót;
- protokoll-deszinkront

okozhat.

# 14. Illegális klienslap átugorhatja az akciót

A szerver kliensüzenetnél:

1. megkeresi a rank/suit lapot;
2. meghívja a `client_play_card(card)` metódust;
3. a game loop ezután továbblép.

A `client_play_card()` csak akkor módosít state-et, ha a lap legális.

Ha a kliens:

- illegális lapot küld;
- nem létező rank/suit párt küld;

akkor nincs mutation, de:

- nincs reject;
- nincs újrakérés;
- nincs accepted flag;
- a szerver fázisa továbbléphet.

Ez akció- vagy turn-skip hibát okozhat.

AETERNA-ban:

```text
ActionRejected
- request_id
- state_version
- reason_code
- authoritative_snapshot_delta
```

szükséges, és rejection után nem léphet fázist a rules engine.

# 15. Jogosulatlan take/carry parancs

A szerver kliensfázisban bármelyik alábbi packetet elfogadja:

```text
throw
carry_pressed
take_pressed
```

A `carry_pressed` és `take_pressed` ágak nem validálják újra:

- pile nem üres;
- pile páros;
- ki vezet;
- melyik action legális;
- a küldő jogosult-e;
- ugyanabban a state versionben vagyunk-e.

A kliens UI gombtiltása nem biztonsági határ.

Egy módosított kliens jogosulatlanul:

- odaadhatja az ütést;
- elviheti az ütést;
- húzást indíthat;
- pile-t törölhet.

# 16. Optimista kliensoldali mutation

A kliens `play_card()`:

1. elküldi a `throw` packetet;
2. eltávolítja a lapot a saját Handből;
3. hozzáadja a saját Pile-jához;
4. acceptednek tekinti az akciót.

Nincs szerver ACK.

Ha a szerver:

- elutasítaná;
- nem találja a lapot;
- más state-ben van;
- megszakad a kapcsolat;

a kliens már eltérő state-ben marad.

AETERNA-ban a kliens csak intentet küldhet; presentation state az authoritative response/event után módosul.

# 17. Duplicate és race kockázat

A Hand minden clicket azonnal emittál.

A várakozó loop csak boolean flaget figyel:

```text
cardPlayed
takePressed
carryPressed
```

Nincs input generation vagy action lock.

Lehetséges:

- gyors dupla kattintás;
- lap és gomb azonos frame-ben;
- több `throw` packet;
- maradék flag a következő várakozási ponton;
- stale packet a következő fázisban.

A helyes modell:

```text
current_action_window_id
single accepted request
server state version
idempotency key
```

# 18. Implicit game state coroutine-pozícióból

A teljes szabályfolyam hosszú:

```gdscript
while true:
    ...
    yield(timer, "timeout")
```

blokkokból áll.

Nincs explicit:

```text
phase
turn owner
action window
trick state
awaited request type
```

A program állapota abból következik, hogy éppen melyik soron vár a coroutine.

Következmény:

- nehéz menteni;
- nehéz visszaállítani;
- reconnect szinte lehetetlen;
- stale packet nehezen szűrhető;
- tesztelhetőség gyenge;
- több action race-et okozhat.

AETERNA-ban minden rules state explicit C# adat.

# 19. Polling és Timer-yield

A szerver és kliens rendszeresen:

- ellenőrzi a packet countot;
- elindít egy Timert;
- yieldel;
- újra ellenőrzi.

Ez esemény helyett polling.

Tanulság:

- a network receive event csak typed commandot tegyen queue-ba;
- az engine tick/action dispatcher kezelje;
- a rules engine ne UI Timertől függjön;
- timeout legyen explicit policy, ne végtelen várakozás.

# 20. Kapcsolatkezelés

## 20.1 Pozitívum

- localhost tesztelés támogatott;
- host és connect menü;
- connect timeout-szerű 20 × 0,25 s próbálkozás;
- kapcsolatvesztéskor visszatérés a menübe.

## 20.2 Hiányok

- nincs auth;
- nincs encryption;
- nincs handshake/version negotiation;
- nincs heartbeat;
- nincs reconnect;
- nincs state resync;
- nincs lobby/session;
- nincs disconnect reason contract;
- nincs NAT traversal;
- nincs server discovery;
- nincs rate limit.

## 20.3 Connection check lifecycle

A `connection_check()` `queue_free()`-t hív, de a hívó coroutine nem kap explicit stop
eredményt.

A deferred free előtt a loop tovább futhat.

Javasolt:

```text
if !connection_check():
    return
```

és egyetlen lifecycle coordinator.

# 21. Rematch protokoll

A Result scene:

- `yes` / `no` packetet küld;
- mindkét fél döntésére vár;
- ugyanazon TCP kapcsolatból új Server/Client scene-t indít.

Ez jó minimális rematch-handshake ötlet.

Kockázatok:

- nincs connection check a Result várakozásaiban;
- nincs timeout;
- nincs match ID;
- nincs new-match ACK;
- nincs reset snapshot;
- mindkét fél korlátlan ideig várhat;
- stale `yes/no` packet új játékba csúszhat.

# 22. Eredményszámítás

A szerver:

- mindkét graveyard pontját kiszámítja;
- elküldi a result packetet;
- a kliens nem számít authoritative eredményt.

Ez helyes authority-irány.

Korlát:

- a score query megsemmisíti Card node-okat;
- nincs typed result contract;
- nincs match summary;
- nincs integrity proof;
- nincs last-trick explicit field;
- nincs event log.

# 23. Húzási és pile-transfer flow

A pile lapjait a szerver graveyard arraybe teszi, majd eltávolítja a Pile scene-ből.

Ez egyszerűen működhet, de:

- nincs atomic transition;
- nincs captured-card order;
- nincs typed `TrickCaptured` event;
- a draw és capture külön UI-mutationek sorozata;
- részleges hiba köztes state-et hagyhat.

AETERNA-ban egy accepted action eredménye egyetlen atomic state transition.

# 24. Kliens és szerver kódduplikáció

A rules-flow nagy része két külön fájlban megismétlődik:

- server local player branch;
- client local player branch;
- take/carry logic;
- pile update;
- draw;
- lead state.

Következmény:

- eltérő bugok;
- eltérő szabályváltozat;
- drift;
- dupla tesztteher.

AETERNA-ban egyetlen C# rules implementation van; Godot csak projection.

# 25. Export- és platformállapot

A project:

- 512×600 fix ablak;
- nem resizable;
- fixed physics 10;
- shadows disabled.

Az export config régi platformlistát tartalmaz.

Fontos eltérés:

- Android `permissions/internet=false`;
- Windows Universal internet capability is false.

Így a hálózati játék ezekben az exportokban várhatóan nem működik konfigurációmódosítás nélkül.

A projekt valódi célplatformja valószínűleg desktop Godot 2.1.5.

# 26. IP-validáció

A connect menü IPv4 regexet használ, de csak azt ellenőrzi, hogy találat van-e a
string elején.

Nem bizonyított a teljes string egyezése.

Például suffixszel rendelkező input átmehet az első ellenőrzésen, majd a TCP connect
meghiúsul.

AETERNA-ban endpoint parsing platform/library API-val történjen.

# 27. Hidden information értékelés

## 27.1 Jó

- a kliens nem kapja meg a host kézidentitását;
- csak card countot lát;
- kijátszott lap nyilvánossá válik;
- új húzásnál csak saját új lapokat kap;
- szerver tárolja mindkét valódi kezet.

## 27.2 Hiány

- nincs viewer projection schema;
- nincs state version;
- nincs server snapshot;
- count drift nem javítható;
- host mint játékos hozzáfér az ellenfél teljes kezéhez;
- nincs spectator/observer projection;
- nincs rejoin projection.

# 28. Determinizmus és replay

Nem találtunk:

- match seedet;
- RNG decision logot;
- action logot;
- state hash-t;
- snapshot serializationt;
- replayt;
- canonical fixture-t.

A teljes meccs csak a két live scene-fában létezik.

# 29. Tesztelés és CI

Nem találtunk:

- unit testet;
- integration testet;
- network protocol testet;
- rule testet;
- headless testet;
- GitHub workflow-t;
- commit status checket.

A négycommitos repositoryban nincs regressziós bizonyíték.

# 30. Licenc és asset-provenance

## 30.1 Kódlicenc

Root `LICENSE`, COPYING vagy licencdeklaráció nem található.

Következmény:

- közvetlen kódmásolás nem engedélyezhető;
- a nyilvános repository önmagában nem jelent újrafelhasználási jogot;
- csak clean-room tanulság használható.

## 30.2 Képek

A szerző kijelenti, hogy:

- nem ő készítette a képeket;
- „open-source sites” helyekről töltötte le;
- a pontos forrásokra nem emlékszik;
- később megpróbálja megkeresni őket.

Ez nem auditálható licence evidence.

Az AETERNA nem használhatja ezeket az asseteket.

# 31. Használható AETERNA-tanulságok

1. A szerver tartsa mindkét játékos valódi állapotát.
2. A kliens ellenfélkéz-projekciója lehet puszta darabszám.
3. Saját kézidentitást csak a tulajdonos viewer kapjon.
4. Kijátszáskor váljon nyilvánossá a lap.
5. A szerver számolja a pontszámot és eredményt.
6. Rematch külön handshake legyen.
7. Egy kis játék teljes flow-ja explicit state machine-né alakítható.
8. Rank/suit jellegű public card data csak reveal után kerülhet a másik klienshez.
9. A dummy hand jó presentationkomponens, ha authoritative snapshot hajtja.
10. A szabályi trick state legyen külön a PileView-tól.

# 32. Amit nem szabad átvenni

1. Scene-node mint authoritative card instance.
2. Rank+suit mint általános instance ID.
3. Nyers Array network message.
4. Kliensoldali optimista Hand/Pile mutation.
5. UI button disable mint security.
6. Implicit phase a coroutine aktuális sorából.
7. Boolean event flags.
8. Polling/yield rules loop.
9. Seed nélküli shuffle.
10. Kliensparancs kontextusvalidáció nélkül.
11. Szerver ACK nélküli action.
12. Host-first draw minden ütésnél.
13. Pontszámítás közbeni node-destroy.
14. Direct TCP internet production protocol.
15. Busy-loop nodevárakozás.
16. Ismeretlen licencű kód és asset.

# 33. Javasolt AETERNA multiplayer action contract

```text
PlayCardRequest
- request_id
- match_id
- actor_player_id
- expected_state_version
- card_instance_id
- action_window_id
```

```text
PlayCardResponse
- request_id
- accepted
- reason_code?
- resulting_state_version
- viewer_snapshot_delta
- public_events
```

A szerver final validation:

```text
actor is active
request window matches
card belongs to actor
card is in expected zone
card is legal in current trick
state version matches
```

# 34. Javasolt trick state

```text
TrickState
- trick_id
- lead_rank
- leader_player_id
- current_winner_player_id
- next_actor_player_id
- round_index
- played_card_instance_ids
- continuation_allowed
- legal_actions
```

A pile paritása lehet származtatott adat, nem phase authority.

# 35. Javasolt hidden-hand projection

```text
PlayerPrivateProjection
- own_hand: visible cards
- opponent_hand_count
- public_pile
- own_captured_summary
- opponent_captured_summary
- legal_actions
- state_version
```

A CardView csak ebből épülhet.

# 36. Konkrét reprodukálandó hibák

## P0-1 – illegális throw skip

1. kliensfázis;
2. páros pile;
3. nem lead rank és nem hetes lap packet;
4. szerver `client_play_card()` nem módosít;
5. ellenőrizni, hogy a flow továbblép-e újrakérés nélkül.

## P0-2 – nem létező lap skip

1. kliens `throw` ismeretlen rank/suit;
2. `is_in_hand()` null;
3. ellenőrizni, hogy a fázis mégis lezárul-e.

## P0-3 – jogosulatlan take/carry

1. pile üres vagy páratlan;
2. kliens kézzel küld `take_pressed` / `carry_pressed`;
3. ellenőrizni, hogy a szerver végrehajtja-e.

## P0-4 – kliens nyerte, szerver húz először

1. kliens nyeri az ütést;
2. ismert deck top order;
3. capture;
4. ellenőrizni, hogy a szerver kapja-e az első lapot.

## P0-5 – optimistic divergence

1. kliens kijátszik;
2. hálózat megszakad az üzenet után;
3. kliens már eltávolította lapját;
4. nincs authoritative rollback.

## P1-1 – dupla kattintás

1. két gyors card click ugyanabban az action windowban;
2. több packet/pile mutation vizsgálata.

## P1-2 – lap és gomb azonos frame

1. Take és Card click;
2. flag/state drift vizsgálata.

## P1-3 – malformed packet

1. `[]`, `["throw"]`, rossz típus;
2. index/type failure vizsgálata.

## P1-4 – result disconnect hang

1. Result scene;
2. peer disconnect;
3. végtelen wait vizsgálata.

## P1-5 – CardSprite hiány

1. Card scene child nélkül;
2. `apply()`;
3. main-thread freeze.

## P1-6 – Android export

1. Android build;
2. network connect;
3. INTERNET permission hiányának ellenőrzése.

# 37. Szükséges AETERNA-tesztmátrix

## 37.1 Rules

- first lead;
- equal rank;
- seven;
- irrelevant response;
- continuation;
- surrender/capture;
- last trick;
- scoring tie;
- deck exhaustion;
- exact draw order.

## 37.2 Network

- valid action;
- invalid action;
- stale version;
- duplicate request;
- out-of-order packet;
- reconnect;
- server timeout;
- client timeout;
- malformed payload;
- oversized payload.

## 37.3 Projection

- own hand visible;
- opponent hand hidden;
- played card reveal;
- draw count update;
- no card identity leak;
- reconnect snapshot;
- spectator view.

## 37.4 Determinism

- fixed seed;
- identical action log;
- identical final state hash;
- replay;
- cross-host equality.

# 38. AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | Typed `PlayCardRequest/Response` | Contract | P0 |
| 2 | Explicit trick/action-window state | Engine | P0 |
| 3 | Final server validation | Engine | P0 |
| 4 | Rejection no phase advance | Engine | P0 |
| 5 | Viewer-safe opponent hand count | Projection | P0 |
| 6 | Authoritative draw order | Engine | P0 |
| 7 | Request ID és state version | Contract | P0 |
| 8 | Duplicate/idempotency védelem | Engine | P0 |
| 9 | Atomic capture+draw transition | Engine | P0 |
| 10 | Engine RNG és shuffle event | Engine | P0 |
| 11 | Network schema/length validation | Boundary | P0 |
| 12 | Reconnect full snapshot | Network | P1 |
| 13 | Rematch new match ID | Network | P1 |
| 14 | DummyHandView snapshotból | Godot | P1 |
| 15 | Multiplayer adversarial tests | Tests | P0 |
| 16 | Asset provenance inventory | Legal | P0 |
| 17 | Következő audit: `LunarTides/Hearthstone.gd` | Learning | P1 |

# 39. Bizonyítékjegyzék

| ID | Állítás | Forrás |
|---|---|---|
| E-001 | Godot 2.1.5 és port 3560 | `README.md` |
| E-002 | 32 lapos deck és shuffle | `Scripts/Deck.gd` |
| E-003 | Card rank/suit és busy loop | `Scripts/Card.gd` |
| E-004 | Hand node/array state | `Scripts/Hand.gd` |
| E-005 | pile paritás és lead rank | `Scripts/Pile.gd` |
| E-006 | dummy opponent count | `Scripts/DummyOpponentHand.gd` |
| E-007 | score és node destroy | `Scripts/Graveyard.gd` |
| E-008 | host/connect flow | `Scene.gd` |
| E-009 | server teljes state és deal | `Server.gd` |
| E-010 | client optimistic mutation | `Client.gd` |
| E-011 | raw Array protocol | `Server.gd`, `Client.gd`, `Result.gd` |
| E-012 | illegális throw nincs újrakérve | `Server.gd` |
| E-013 | take/carry nincs context validation | `Server.gd` |
| E-014 | server-first draw | `Server.gd` |
| E-015 | rematch yes/no | `Result.gd` |
| E-016 | fixed physics 10 | `engine.cfg` |
| E-017 | Android/UWP internet disabled | `export.cfg` |
| E-018 | asset source ismeretlen | `README.md` |
| E-019 | licencfájl nem talált | repository search |
| E-020 | nincs test találat | repository search |
| E-021 | nincs commit status | GitHub combined status |
| E-022 | nincs workflow run | GitHub workflow query |
| E-023 | külső Sedmice szabály | Pagat Sedmice rules |

# 40. Nyitott kérdések

1. Godot 2.1.5-ben reprodukálható-e a teljes kétpéldányos játék?
2. Mekkora a Timer wait time a Server/Client scene-ben?
3. Dupla clickkel kijátszható-e két lap?
4. Illegális packet valóban átugorja-e a kliens akcióját?
5. Jogosulatlan take/carry végrehajtható-e?
6. A draw order eltérés tudatos helyi szabály vagy bug?
7. A vezető folytatási joga tudatos házi szabály vagy eltérés?
8. PacketPeerStream mennyire korlátozza az objektumdeszerializációt Godot 2.1.5-ben?
9. Mi történik félbeszakadt `get_var()` vagy malformed Variant esetén?
10. Result scene disconnectnél végtelenül vár-e?
11. Android export ténylegesen hálózatképtelen-e INTERNET permission nélkül?
12. A képi assetekhez visszakereshető-e bármilyen licence evidence?
13. A repository szerzője ad-e később explicit kódlicencet?
14. A rematch teljesen reseteli-e minden flaget és packet queue-t?
15. A pile utolsó vezetője minden tie case-ben helyesen marad-e meg?

# 41. Végső minősítés

- **Kis teljes játékfolyam tanulási értéke:** magas
- **Hidden-hand projection értéke:** magas
- **Host-side scoring értéke:** közepes-magas
- **Rules implementáció:** közepes, több változat-/sorrendeltéréssel
- **Server authority:** részleges
- **Client trust biztonság:** alacsony
- **Network contract:** nagyon alacsony
- **Determinism/replay:** nincs
- **Reconnect/resync:** nincs
- **Godot modern használhatóság:** nagyon alacsony
- **Teszt/CI érettség:** nincs bizonyítva
- **Kódlicenc:** hiányzik
- **Assetlicenc:** nem auditálható
- **Közvetlen dependency:** elutasítandó
- **Clean-room multiplayer tanulság:** ajánlott
- **Legfontosabb AETERNA-tanulság:** az ellenfél valódi kézállapotát a szerver
  tarthatja, a kliens pedig csak darabszám-projekciót kaphat; minden actiont typed,
  verziózott és final-revalidated C# contracton kell elfogadni
- **Elemzés státusza:** első teljes source audit elkészült
- **Következő learning cél:** `LunarTides/Hearthstone.gd`

# 42. Változásnapló

## 0.1 – 2026-07-26

- elkészült a `Valyreon/seven-card-game-godot` első teljes AETERNA-központú auditja;
- ellenőrzésre került a repository, branch, commit és Godot-verzió;
- feldolgozásra került a Sedmice külső szabályforrás;
- feldolgozásra került a Card, Deck, Hand, Pile, Graveyard és DummyOpponentHand;
- feldolgozásra került a host–client TCP és PacketPeerStream flow;
- rögzítésre került a szerveroldali mindkét kéz és a kliensoldali dummy projection;
- azonosításra került az illegális/nem létező throw akcióátugrás;
- azonosításra került a context validation nélküli take/carry;
- azonosításra került a server-first draw sorrendhiba;
- azonosításra került az optimista kliensoldali Hand/Pile mutation;
- azonosításra került a nyers pozicionális packet schema;
- azonosításra kerültek a duplicate/race kockázatok;
- azonosításra került a coroutine-pozícióból származó implicit game state;
- azonosításra került a seed/replay/state-version hiánya;
- azonosításra került a CardSprite busy loop;
- azonosításra került az Android/UWP hálózati exportbeállítás hiánya;
- rögzítésre került a hiányzó kódlicenc és a nem auditálható asset-provenance;
- elkészült az AETERNA typed multiplayer contract-, trick-state- és projection-javaslata;
- a következő kijelölt learning projekt `LunarTides/Hearthstone.gd`.
