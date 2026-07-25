# AETERNA – rametta/Pali ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-25
- **Státusz:** repository-forrásokra épülő első teljes multiplayer- és authority-elemzés
- **Fő elemzési fájl:** `learning/analyses/rametta__pali.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Repository:** `rametta/Pali`
- **Stabil upstream URL:** `https://github.com/rametta/Pali`
- **Vizsgált branch:** `main`
- **Vizsgált commit:** `bcea2eb2b3c49c90a7d4616dd80e5f7570dbcd42`
- **Vizsgált commit dátuma:** 2024-04-27
- **Technológiai alap:** Godot 4.1 / GDScript / ENetMultiplayerPeer
- **Licenc:** Apache-2.0
- **Játékmód:** kétjátékos, dedikált szerveres, körökre osztott 3D kártyajáték
- **AETERNA összehasonlítási bázis:** az aktuális C# authoritative engine-, contract-, runtime-package-, hidden-information- és Godot-bridge rendszer
- **Összehasonlítási szabály:** kizárólag az AETERNA rendszeréhez mérve
- **Vizsgálati korlát:** helyi hárompéldányos hálózati futtatás, packet-manipulációs teszt, export és dinamikus exploit-reprodukció ebben a körben nem történt
- **Elsődleges AETERNA-érték:** valódi Godot dedikált szerver, ENet lifecycle, két kliens–egy szerver fejlesztői workflow és egyszerű server-side turn/score validation
- **Elsődleges AETERNA-kockázat:** a teljes scene tree minden peerben canonical state-ként létezik, a teljes paklisorrend és minden rejtett kártyaazonosító eljut a kliensekhez, az action RPC-k pedig nem validálják teljesen a tulajdonjogot és az állapotverziót

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Projekt neve | Pali |
| Repository | `rametta/Pali` |
| Default branch | `main` |
| Vizsgált commit | `bcea2eb2b3c49c90a7d4616dd80e5f7570dbcd42` |
| Repository állapot | nyilvános, nem archivált |
| Godot-verzió | 4.1 |
| Renderer | GL Compatibility |
| Nyelv | GDScript |
| Hálózati backend | Godot High-Level Multiplayer / ENet |
| Szervermodell | külön dedikált szerver export |
| Játékosszám | pontosan két peer |
| Szerverkapacitás | két kliens, utána új kapcsolat elutasítása |
| Canonical state | Godot scene tree és node propertyk |
| Kártyaadat | typed `CardResource` `.tres` fájlok |
| Kártyapéldány | `Area3D` Card node, definition ID-ből képzett node-név |
| Rejtett kéz | vizuálisan korlátozott, adatként nem rejtett |
| Turn validation | részleges, szerveroldali |
| Ownership validation | hiányos |
| State version | nincs |
| Request ID / idempotency | nincs |
| Snapshot / resync | nincs |
| Replay / event log | nincs |
| Teszt/CI bizonyíték | nem talált |
| Licenc | Apache-2.0 |
| AETERNA-prioritás | P0 – multiplayer authority és hidden-information ellenpélda |
| Közvetlen integráció | nem javasolt |

# 2. Vezetői összefoglaló

A Pali az eddig vizsgált Godot-projektek között fontos, mert nem csak UI-demó vagy
multiplayer ötlet, hanem ténylegesen tartalmaz:

- dedikált szerver exportot;
- ENet szerver- és klienslétrehozást;
- két klienses lobbyt;
- server-only branch-et;
- server-side turn validationt;
- server-side score calculationt;
- RPC-alapú akciótovábbítást;
- server-controlled deck randomizálást;
- kapcsolat- és disconnect-kezelést;
- három példányos helyi fejlesztői workflow-t.

Ez jó bizonyíték arra, hogy Godotból viszonylag kevés kóddal készíthető működő
dedikált szerveres kártyajáték-prototípus.

A projekt ugyanakkor **nem production authority referencia**, mert a hálózati modell:

```text
server scene tree
↕ RPC
client 1 teljes scene tree
client 2 teljes scene tree
```

A szerver és minden kliens ugyanazt a teljes Card/Deck/Hand objektumgráfot tartja.
A kliens a teljes megkevert paklisorrendet megkapja, majd lokálisan példányosítja és
kiosztja mindkét játékos kézlapjait. A rejtett információ ezért csak vizuális korlátozás.

A szerver action-validációja szándékában jó, de hiányos:

- ellenőrzi, hogy a küldő van-e soron;
- ellenőrzi, hogy a dropzone és a kártyanév létezik-e;
- bizonyos esetben ellenőrzi a kártya zónáját;
- nem ellenőrzi teljesen, hogy a kártya a küldő saját kezében van-e;
- a csereakcióban nem ellenőrzi a kártyák elvárt zónáit;
- nincs state version;
- nincs request ID;
- nincs idempotency;
- nincs legal-action ID;
- nincs szerveroldali targetcandidate-lista;
- több `any_peer` RPC külön akció nélkül is állapotot léptethet.

## 2.1 Rövid döntés

- **Dedikált szerver lifecycle referenciaként:** hasznos
- **Godot ENet prototípusként:** hasznos
- **Hárompéldányos fejlesztői workflowként:** hasznos
- **Authoritative server mintaként:** részlegesen hasznos, de súlyosan hiányos
- **Hidden-information mintaként:** negatív példa
- **RPC threat-model forrásként:** kiemelten hasznos
- **AETERNA rules engine alapként:** nem használható
- **Közvetlen kódbeemelés:** nem javasolt
- **Clean-room hálózati elvek:** igen
- **Legfontosabb tanulság:** a dedikált szerver önmagában nem jelent authoritative,
  információbiztos és reprodukálható játékmotort

# 3. Játékszabály és scope

A Pali egyszerű, 25 egyedi kártyából álló játék:

1. mindkét játékos öt lapot kap;
2. körönként egy kézlap kijátszható az asztalra, vagy egy asztali lap kézlappal cserélhető;
3. a kijátszás után a kéz új lapot húz;
4. a pakli elfogyásakor pontszámítás történik;
5. a pontot alapérték, kategória-, tag- és kapcsolati szinergia adja.

Ez a kis state space alkalmassá teszi a projektet authority- és RPC-audit tanulási
forrásnak.

Az AETERNA szabályrendszere ennél lényegesen nagyobb, ezért a Pali konkrét játéklogikája
nem átemelendő. A hálózati struktúra és a validációs hiányok a relevánsak.

# 4. Repository és technológiai állapot

## 4.1 Godot

A `project.godot` szerint:

```text
config/features=PackedStringArray("4.1", "GL Compatibility")
run/main_scene="res://Scenes/Manager/Manager.tscn"
Global autoload="res://Global.gd"
```

A projekt modern Godot 4 API-kat használ:

- `ENetMultiplayerPeer`;
- `@rpc`;
- `PackedByteArray`;
- `Node3D`, `Area3D`, `Camera3D`;
- SceneTreeTween;
- dedicated server feature.

## 4.2 Aktivitás

A vizsgált HEAD 2024-04-27-i, és főként:

- hozzájárulási útmutatót;
- lokális hárompéldányos futtatást;
- debug szervergomb láthatóságát

adta hozzá.

A projekt nem archivált, de a commitelőzmény alapján nem tekinthető gyorsan változó,
aktívan fejlesztett production frameworknek.

# 5. Dedikált szerver lifecycle

A `Manager.gd`:

1. létrehoz egy `ENetMultiplayerPeer` objektumot;
2. dedicated-server buildben automatikusan szervert indít;
3. kliensbuildben join/create gombokat köt;
4. `create_server(PORT, 2)` hívással pontosan két klienst fogad;
5. két peer kapcsolódásakor minden peerben létrehozza a World scene-t;
6. ezután új kapcsolatokat elutasít;
7. game over esetén bontja a peereket;
8. disconnect esetén felszabadítja a World scene-t és újra engedélyezi a csatlakozást.

## 5.1 Hasznos AETERNA-elv

Jól elkülöníthető transport lifecycle:

```text
server boot
→ peer join
→ player slot assignment
→ match creation
→ refuse extra peers
→ match end
→ disconnect
→ cleanup
→ new match availability
```

## 5.2 AETERNA szükséges továbbfejlesztés

A szervernek nem World scene-t kell authorityként létrehoznia, hanem:

```text
MatchHost
├── match_id
├── EngineSession
├── player/peer mapping
├── transport adapter
├── snapshot dispatcher
├── request deduplicator
├── reconnect state
└── match lifecycle
```

A Godot World scene csak kliensoldali projection legyen.

# 6. Peer identity és lobby

A kliens `send_display_name` RPC-vel küldi a nevet. A szerver a
`multiplayer.get_remote_sender_id()` alapján köti a nevet peer ID-hoz.

Pozitívum:

- nem bízik a kliens által küldött peer ID-ban;
- a sender ID-t a transportból olvassa;
- a peer–név mapet szerver állítja elő.

Hiányok:

- nincs name length limit;
- nincs normalizálás;
- nincs duplicate-name policy;
- nincs authentication;
- nincs session token;
- nincs reconnect identity;
- nincs persistent player ID;
- nincs match ID;
- a peer ID közvetlen player identityként működik.

Az AETERNA-ban:

```text
transport_peer_id
≠
player_id
≠
account_id
≠
match_slot
```

A négy fogalmat külön kell kezelni.

# 7. Match creation és player mapping

Két peer után a szerver:

```text
create_world.rpc(peers[0], peers[1])
```

hívással minden résztvevőn létrehozza ugyanazt a World scene-t. A local peer ID alapján
minden kliens meghatározza, hogy Player One, Player Two vagy Server szerepű.

Ez egyszerű és prototípushoz működőképes.

AETERNA-kockázatok:

- a `multiplayer.get_peers()` sorrendje határozza meg a játékosszámot és kezdőpozíciót;
- nincs explicit seat assignment event;
- nincs match creation response;
- nincs schema/version;
- nincs reconnecthez stabil slot mapping;
- nincs spectator role;
- nincs server-issued player credential;
- nincs match seed contract.

# 8. Canonical state: scene tree

A World authoritative és presentation state-et ugyanabban a node tree-ben tartja:

- deck;
- player 1 hand;
- player 2 hand;
- table cards;
- dropzones;
- selected kártyák;
- card zone property;
- turn;
- scores;
- intro és animation flags.

A kártyamozgás `remove_child` / `add_child` parentváltással történik.

A kártya zónája egy enum mező:

```text
DECK
TABLE
PLAYER_1_HAND
PLAYER_2_HAND
```

A state invariáns tehát több, külön módosítható forrásból áll:

```text
node parent
+ card.zone
+ node name
+ dropzone pickable flag
+ global selected names
```

Nincs központi invariant validator, amely bizonyítja, hogy ezek mindig egyeznek.

## 8.1 AETERNA követelmény

```text
MatchState
├── CardInstance registry
├── ZoneState
├── TurnState
├── SelectionState
├── PlayerState
└── state_version
```

A Godot scene tree ebből épül, nem fordítva.

# 9. Card definition és card instance

A `CardResource` typed Resource mezői:

- `id`;
- `title`;
- `color`;
- `texture`;
- `value`;
- `category`;
- `tags`;
- `relations`.

Ez hasznos statikus definition-minta.

A Deck 25 előre preloadolt resource-ot tart. A kártya node neve:

```text
card-<card_resource.id>
```

Mivel minden definitionből pontosan egy példány van, a definition ID egyben runtime
instance-azonosítóként is működik.

Ez AETERNA-ban nem elegendő, mert:

- ugyanabból a lapból több példány lehet;
- token vagy másolat keletkezhet;
- controller változhat;
- kártya visszatérhet vagy újrainicializálódhat;
- instance és definition életciklusa eltér.

Kötelező:

```text
card_id
card_instance_id
owner_player_id
controller_player_id
zone_id
zone_index
visibility
created_sequence
```

# 10. Deck randomizálás

A szerver:

```text
arr = range(25)
arr.shuffle()
PackedByteArray(arr)
start_cards_tween.rpc(packed)
```

módszerrel készít sorrendet.

Pozitívum:

- a sorrendet a szerver választja;
- minden peer ugyanazt a sorrendet kapja;
- a szerver is ugyanabból a sorrendből építi fel a state-et.

Hiányok:

- nincs explicit match seed;
- a seed nincs contractban;
- nincs RNG state;
- nincs random decision event;
- nincs shuffle audit;
- nincs replay;
- nincs state hash;
- a teljes deck order minden klienshez eljut.

AETERNA megfelelője:

```text
server EngineRandom(match_seed)
→ ShuffleDecision event / replay metadata
→ full order csak authoritative state-ben
→ kliensnek csak count és engedélyezett identity
```

# 11. Kritikus hidden-information szivárgás

A `start_cards_tween` RPC minden kliensnek elküldi a teljes 25 elemű megkevert
indexlistát.

Ezután minden kliens:

1. mind a 25 Card scene-t példányosítja;
2. mindegyikhez hozzárendeli a teljes `CardResource` objektumot;
3. `card-<definition id>` néven tárolja;
4. lokálisan kiosztja Player One és Player Two teljes kezét;
5. a deck teljes sorrendjét saját scene tree-ben tartja.

A kliensoldali `on_card_select` csak azt akadályozza meg, hogy a játékos normál UI-n
rákattintson az ellenfél kézlapjára.

Ez nem információvédelem.

Egy módosított kliens vagy debugger kiolvashatja:

- az ellenfél minden kézlapját;
- a pakli teljes hátralévő sorrendjét;
- a következő húzásokat;
- minden kártya pontértékét, kategóriáját, tagjeit és kapcsolatait.

## 11.1 AETERNA kötelező projection

```text
Server full state
├── Player 1 snapshot
│   ├── saját hand identity
│   ├── opponent hand count
│   └── deck count
└── Player 2 snapshot
    ├── saját hand identity
    ├── opponent hand count
    └── deck count
```

A rejtett kártyához legfeljebb opaque, nem korrelálható view token használható, ha az
animációhoz szükséges.

# 12. RPC inventory

| RPC | Mode | Cél | Audit |
|---|---|---|---|
| `sync_peer_name_map` | authority + call_local | névmap szinkron | elfogadható prototípus |
| `send_display_name` | any_peer | név küldése | sender ID jó; input policy hiányzik |
| `create_world` | authority + call_local | World scene létrehozás | teljes scene state replikáció |
| `update_player_turn` | authority + call_local | kör szinkron | state version/event hiányzik |
| `intro_done_server` | any_peer | intro ack | duplicate/sender-slot ellenőrzés hiányzik |
| `start_cards_tween_done_server` | any_peer | deal animation ack | duplicate/sender-slot ellenőrzés hiányzik |
| `card_played_server` | any_peer | kör váltása | kritikus: közvetlenül meghívható |
| `start_cards_tween` | authority + call_local | teljes deck order terjesztés | hidden-info leak |
| `play_card_client` | authority + call_local | scene mutation/animáció | rules commit és presentation összefonódik |
| `switch_card_client` | authority + call_local | scene mutation/animáció | rules commit és presentation összefonódik |
| `play_card_server` | any_peer | play request | részleges validáció |
| `switch_card_server` | any_peer | switch request | súlyosan hiányos validáció |
| `update_scores` | authority | pontszinkron | typed event/version hiányzik |
| `recalculate_scores_server` | any_peer | szerver score recalc | indokolatlanul klienshívható |
| `show_winner_dialog` | authority | winner UI | presentation RPC |

# 13. `intro_done_server` és animation ACK sérülékenység

A szerver két tömböt tart:

```text
server_peers_intro_done
server_peers_start_cards_tween_done
```

Az `any_peer` RPC-k a sender ID-t egyszerűen hozzáfűzik.

Nincs:

- duplicate sender check;
- `id in expected_peers` check;
- phase check;
- one-time token;
- timeout;
- disconnect cleanup;
- request sequence.

Következményként egy peer elméletileg kétszer is elküldheti ugyanazt az ACK-t, és a tömb
mérete elérheti a kettőt a másik peer nélkül.

További probléma:

> a rules progression a kliens animációjának befejezési visszajelzésére vár.

Egy kliens:

- végtelenül késleltetheti a match startot;
- hamisan korán jelezhet kész állapotot;
- ismételt ACK-kal fázist léptethet.

## 13.1 AETERNA helyes modell

```text
server authoritative deal commit
→ state_version növelés
→ snapshot/event kiküldés
→ kliens animálhat
→ animációs ACK legfeljebb telemetry
```

A rules state nem vár kliens Tweenre.

# 14. `card_played_server` kritikus RPC

A metódus `any_peer`, és a szerveren csak ezt ellenőrzi:

```text
multiplayer.is_server()
```

Nem ellenőrzi:

- a sender játékosslotját;
- hogy volt-e elfogadott action;
- request ID-t;
- aktuális state versiont;
- phase-et;
- egyszeri használatot;
- correlation ID-t.

A metódus közvetlenül váltja a kör tulajdonosát.

Egy módosított kliens ezért elméletileg tetszőleges időben meghívhatja, és köröket
ugorhat vagy visszaválthat.

Ez különösen fontos AETERNA-tanulság:

> belső transition helper soha ne legyen player-callable RPC.

A kliens egyetlen publikus belépési pontja:

```text
SubmitAction(ActionRequest)
```

# 15. `play_card_server` validáció

Pozitív szerverellenőrzések:

- csak szerveren fut;
- sender ID-t transportból olvas;
- ellenőrzi az aktuális játékos körét;
- ellenőrzi a dropzone létezését;
- ellenőrzi a kártya létezését;
- tiltja a TABLE és DECK zónából történő playt.

Hiányok:

1. nem ellenőrzi, hogy Player One csak `PLAYER_1_HAND` kártyát játszhat;
2. nem ellenőrzi, hogy Player Two csak `PLAYER_2_HAND` kártyát játszhat;
3. nem ellenőrzi a kártya ownerét;
4. nincs külön controller;
5. nem ellenőrzi, hogy a dropzone szabad-e;
6. nem tart authoritative occupancy mapet;
7. nem ellenőrzi, hogy a card name az adott sender legal-action listájában szerepel-e;
8. nincs expected state version;
9. nincs request ID;
10. nincs duplicate suppression;
11. nincs schema validation;
12. rejection csak log, strukturált response nincs.

Mivel a kliens ismeri az ellenfél minden kártyájának nevét, egy módosított kliens
megpróbálhatja az ellenfél kezéből kijátszani a kártyát.

# 16. `switch_card_server` validáció

A csereakció még gyengébb.

A szerver ellenőrzi:

- a küldő van-e soron;
- a `table_card_name` létezik-e;
- a `hand_card_name` létezik-e.

Nem ellenőrzi:

- hogy a `table_card` ténylegesen TABLE zónában van-e;
- hogy a `hand_card` ténylegesen kézben van-e;
- hogy a kézlap a küldő saját kezében van-e;
- hogy a két név különböző-e;
- hogy a kártyák tulajdonosi viszonya megfelelő-e;
- hogy a jelenlegi state verzió megfelel-e;
- hogy az action legal action volt-e.

A `switch_card_client` a célslotot kizárólag az aktuális körből vezeti le, és közvetlenül
reparenteli a megadott node-okat. Hibás vagy rosszindulatú paraméterezés state
inkonzisztenciát okozhat.

# 17. Dropzone occupancy

A kliensoldali `play_card_client` ezt teszi:

```text
dz.input_ray_pickable = false
```

Ez UI-szinten megakadályozza az újabb normál kattintást.

A szerver requestvalidációja azonban nem ellenőrzi ezt a flaget, és nincs külön
authoritative `occupied_by_card_instance_id`.

Egy közvetlen RPC ugyanarra a dropzone-ra újra hivatkozhat.

AETERNA-ban:

```text
PositionState
- position_id
- occupant_instance_id?
- topology
- legal placement constraints
```

és az occupancy az engine invariant része.

# 18. Server-side score calculation

A szerver számolja a pontot a két hand node childjaiból.

Pozitívum:

- a kliens nem küld kész pontszámot;
- a server resource adatokból számol;
- a winner a szerver pontjai alapján készül.

Hiányok:

- a canonical hand maga scene childlista;
- nincs pure scoring function;
- nincs immutable input;
- nincs külön score breakdown;
- nincs deterministic result event;
- a `recalculate_scores_server` any peer által meghívható;
- nincs idempotent match-end guard;
- nincs state version.

A scoring logika pure C# függvényként jó AETERNA-minta lenne, de a node tree dependency
nem.

# 19. Action commit és presentation összefonódása

A szerver egy elfogadott request után:

```text
play_card_client.rpc(...)
```

vagy:

```text
switch_card_client.rpc(...)
```

hívást küld.

A `*_client` metódus:

- scene-node-okat reparentel;
- card.zone mezőt ír;
- globális selectiont töröl;
- hangot játszik;
- Tweent indít;
- hand layoutot frissít;
- a szerveren score-t számol;
- a szerveren turnt vált.

A rules commit tehát ugyanabban a metódusban él, mint az animáció.

AETERNA-ban szükséges:

```text
Engine transition commit
→ ActionResponse
→ EngineEvent
→ snapshot
→ Godot AnimationCoordinator
```

Ha az animáció megszakad vagy kihagyásra kerül, a canonical state akkor is már helyes.

# 20. Turn state és state version

A Pali egyetlen `synced_player_turn` mezőt használ.

Nincs:

- phase;
- priority;
- action sequence;
- expected state version;
- turn number;
- action budget;
- pending decision;
- transition ID;
- last accepted request;
- stale action rejection.

Versenyhelyzetben két gyors vagy ismételt request ugyanarra a kliensoldali állapotra
épülhet.

Az AETERNA `ActionRequest` legalább:

```text
schema_version
request_id
match_id
player_id
expected_state_version
action_id
payload
```

mezőket igényel.

# 21. Request és response contract hiánya

A kliens raw paramétereket küld:

```text
dropzone name
card node name
table card node name
hand card node name
```

A szerver logol és vagy visszatér, vagy broadcastolja a mutációt.

Nincs:

- typed request object;
- schema version;
- stable action ID;
- legal-action proof;
- structured rejection code;
- diagnostic details;
- accepted response;
- state version before/after;
- event list;
- retry semantics.

A node name nem megfelelő network object reference.

# 22. Disconnect és reconnect

A szerver disconnectkor:

- törli a nevet;
- új kapcsolatot enged;
- felszabadítja a teljes World scene-t.

Ez egyszerű cleanup, de nincs:

- reconnect grace period;
- player slot visszaállítás;
- snapshot resend;
- match resume;
- forfeit outcome;
- disconnect reason event;
- remaining player tájékoztatás;
- persisted match state.

Az AETERNA-ban külön döntés kell:

```text
disconnect
→ grace period vagy immediate forfeit
→ reconnect token
→ viewer snapshot resync
→ state version check
```

# 23. Transport és security

A projekt:

- ENet transportot használ;
- fix IP-címet és portot fordít a kliensbe;
- nem mutat authenticationt;
- nem mutat session tokent;
- nem mutat titkosítást;
- nem mutat rate limitet;
- nem mutat payload size limitet;
- nem mutat abuse logot;
- nem mutat protocol version negotiationt.

Prototípusnál ez elfogadható lehet, de production AETERNA esetén nem.

# 24. Dedicated server export

Az `export_presets.cfg` külön Linux/X11 dedicated server presetet tartalmaz:

```text
dedicated_server=true
```

Ez hasznos AETERNA deployment referencia:

- külön server artifact;
- külön client artifact;
- dedicated-server feature ágon automatikus boot;
- headless üzem.

AETERNA esetén a server artifact ideális esetben nem igényli a teljes 3D scene- és
assetkészletet a szabályok futtatásához.

A pure C# engine külön processben vagy minimális Godot hostban futhat.

# 25. Tesztelés és CI

A repositoryban az elérhető keresés alapján nem találtunk:

- GitHub Actions workflowt;
- GUT tesztet;
- headless multiplayer tesztet;
- RPC security tesztet;
- deterministic testet;
- hidden-information tesztet;
- reconnect tesztet.

A CONTRIBUTING három Godot-példány kézi futtatását írja elő:

1. egy szerver;
2. két kliens;
3. localhost cím;
4. join és match indítás.

Ez jó manual smoke, de nem automatizált proof.

## 25.1 AETERNA multiplayer tesztminimum

- server boot;
- két player join;
- harmadik peer reject;
- seat assignment;
- own-hand projection;
- opponent-hand redaction;
- legal play accepted;
- opponent card spoof rejected;
- wrong-turn rejected;
- duplicate request rejected/idempotent;
- stale request rejected;
- occupied position rejected;
- malformed ID rejected;
- direct internal RPC lehetetlen;
- disconnect;
- reconnect/resync;
- deterministic seed;
- replay parity;
- server/client state hash;
- match end egyszeri.

# 26. Licenc és assetek

A kód Apache-2.0 licencű, Jason Rametta 2023-as copyrighttal.

Ez lényegesen megengedőbb, mint az előző AGPL frameworkek.

A README ugyanakkor külső assetforrásokat is felsorol:

- Kay Lousberg 3D assetek;
- Noto Sans;
- freesound hangok;
- Layerrel generált képek.

Közvetlen assetátvételnél minden elem saját licencét külön ellenőrizni kell.

Az AETERNA számára továbbra is saját clean-room implementáció ajánlott, főleg mert az
architektúra nem illeszkedik a C# authority modellhez.

# 27. Erősségek az AETERNA szempontjából

1. Valódi Godot 4 dedikált szerver export.
2. ENet szerver- és klienslifecycle.
3. Kétjátékos peer limit.
4. Automatikus dedicated server boot.
5. Peer sender ID szerveroldali olvasása.
6. Server-side turn check.
7. Server-side score calculation.
8. Server-selected deck order.
9. Egy szerver + két kliens manual smoke workflow.
10. Connection/disconnection signalok kezelése.
11. Lobby és névszinkron.
12. Separate client/server exportgondolat.
13. Typed CardResource.
14. Egyszerűen auditálható kis szabálytér.
15. Apache-2.0 licenc.
16. Jó RPC threat-model tananyag.
17. Jó hidden-information ellenpélda.
18. Jó bizonyíték arra, hogy dedicated server nem egyenlő teljes authorityval.

# 28. Gyengeségek és kritikus kockázatok

1. Teljes deck order eljut minden klienshez.
2. Mindkét kéz teljes identityje eljut minden klienshez.
3. Hidden information csak UI-szinten rejtett.
4. Scene tree a canonical state.
5. Node parent és zone mező párhuzamos state.
6. Definition ID és instance ID összemosása.
7. Node name network reference.
8. `card_played_server` közvetlenül klienshívható.
9. Intro ACK duplicate check hiányzik.
10. Deal ACK duplicate check hiányzik.
11. Kliensanimáció ACK-tól függ a rules progression.
12. Play ownership validation hiányzik.
13. Switch zone validation hiányzik.
14. Switch ownership validation hiányzik.
15. Dropzone occupancy server validation hiányzik.
16. Nincs legal-action lista.
17. Nincs state version.
18. Nincs request ID.
19. Nincs idempotency.
20. Nincs structured response.
21. Nincs stable diagnostic.
22. Nincs snapshot/resync.
23. Nincs reconnect.
24. Nincs replay.
25. Nincs state hash.
26. Nincs explicit RNG seed contract.
27. Nincs protocol version.
28. Nincs authentication.
29. Nincs rate limit.
30. Nincs automated test/CI proof.
31. Rules commit és Tween egy metódusban.
32. Full 3D World scene a szerveren is létrejön.
33. Raw display name policy hiányzik.
34. Match ID és player ID elválasztás hiányzik.
35. A score recalc indokolatlanul `any_peer`.
36. Match-end idempotency nincs bizonyítva.

# 29. AETERNA számára átvehető elvek

## 29.1 Transport lifecycle

- dedicated server boot;
- peer join;
- seat assignment;
- capacity close;
- disconnect cleanup.

## 29.2 Sender identity

A transport sender ID-ját a szerver olvassa, nem a kliens küldi.

## 29.3 Server-side calculation

Pont, legalitás és győzelem mindig szerveren/engine-ben számítandó.

## 29.4 Külön server artifact

A fejlesztés és deployment külön kliens- és szerverbuildet használhat.

## 29.5 Hárompéldányos smoke

Automatizált vagy kézi:

```text
server
client A
client B
```

workflow kötelező.

## 29.6 RPC threat matrix

Minden player-callable endpointnál:

- caller;
- phase;
- ownership;
- expected version;
- object existence;
- legal action;
- duplicate;
- rate;
- visibility;
- result.

# 30. Amit nem szabad átvenni

1. A teljes deck order broadcastja.
2. Az ellenfél hand identity lokális tárolása.
3. UI tiltás mint security.
4. Scene tree mint MatchState.
5. Node name mint card reference.
6. `any_peer` belső transition helper.
7. Kliens Tween ACK mint rules gate.
8. Card parentváltás mint authoritative transaction.
9. Raw RPC-paraméterek contract nélkül.
10. Definition ID mint runtime instance ID.
11. Dropzone UI flag mint occupancy.
12. Turnváltás külön player-callable RPC-ben.
13. Fixed server IP production configként.
14. Authentication nélküli production szerver.
15. Testek nélküli multiplayer kiadás.

# 31. Javasolt AETERNA multiplayer architektúra

```text
Aeterna Dedicated Host
├── TransportServer
│   ├── peer connection
│   ├── authentication/session
│   ├── rate limiting
│   └── protocol version
├── MatchHostRegistry
│   └── MatchHost
│       ├── match_id
│       ├── peer → player mapping
│       ├── EngineSession
│       ├── RequestDeduplicator
│       ├── ReconnectManager
│       └── SnapshotDispatcher
└── Logging/Telemetry
        │
        ▼
ActionRequest
        │
        ▼
EngineSession.SubmitAction
        │
        ├── schema
        ├── match/player identity
        ├── expected state version
        ├── legal action ID
        ├── ownership
        ├── target
        ├── payment
        └── final revalidation
        │
        ▼
ActionResponse + EngineEvents
        │
        ▼
ProjectionService(viewer)
        │
        ├── own snapshot
        └── redacted opponent snapshot
        │
        ▼
Godot Client
├── local view state
├── animation
├── input
└── no hidden authoritative data
```

# 32. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | Player-specific snapshot projection | Engine | P0 |
| 2 | Hidden hand identity ne kerüljön opponent klienshez | Security | P0 |
| 3 | Dedicated MatchHost + EngineSession | Server | P0 |
| 4 | Egyetlen player-callable `SubmitAction` endpoint | Contract | P0 |
| 5 | Belső transition helper ne legyen RPC | Security | P0 |
| 6 | `request_id` és deduplicator | Server/Contract | P0 |
| 7 | `expected_state_version` | Engine/Contract | P0 |
| 8 | Stable `card_instance_id` | Engine | P0 |
| 9 | Ownership/controller validáció | Engine | P0 |
| 10 | Position occupancy invariant | Engine | P0 |
| 11 | Structured rejection code | Contract | P0 |
| 12 | Server-issued match/player mapping | Server | P0 |
| 13 | Animation ne blokkolja rules state-et | Godot/Bridge | P0 |
| 14 | Explicit match seed és RNG event | Engine | P0 |
| 15 | Reconnect/resync contract | Multiplayer | P1 |
| 16 | Three-process automated smoke | Tests | P0 |
| 17 | Malicious RPC integration tests | Tests/Security | P0 |
| 18 | Wrong-owner card spoof test | Tests | P0 |
| 19 | Duplicate ACK/request test | Tests | P0 |
| 20 | Occupied target test | Tests | P0 |
| 21 | Hidden-state memory/payload audit | Security | P0 |
| 22 | Server artifact minimális assetfüggése | Build | P1 |
| 23 | Protocol version negotiation | Server | P1 |
| 24 | Authentication/session token | Server | P1 |
| 25 | Rate and payload limits | Security | P1 |
| 26 | Apache notice és assetlicenc audit | License | P1 |

# 33. Bizonyítékjegyzék

| ID | Állítás | Forrás |
|---|---|---|
| E-001 | Pali 3D multiplayer TCG | `README.md` |
| E-002 | dedicated server és client export | `README.md` |
| E-003 | két klienses server | `README.md` |
| E-004 | Godot 4.1 | `project.godot` |
| E-005 | Global autoload | `project.godot` |
| E-006 | ENetMultiplayerPeer | `Manager.gd` |
| E-007 | dedicated_server feature auto boot | `Manager.gd` |
| E-008 | `create_server(PORT, 2)` | `Manager.gd` |
| E-009 | két peer után World create + refuse connections | `Manager.gd` |
| E-010 | sender ID alapján display name | `Manager.gd` |
| E-011 | World server/player role | `Manager.gd` / `World.gd` |
| E-012 | intro ACK any_peer | `World.gd` |
| E-013 | teljes 25 elemű deck order RPC | `World.gd` |
| E-014 | mindkét hand lokális deal | `World.gd` |
| E-015 | opponent selection csak UI-ban tiltott | `World.gd` |
| E-016 | `card_played_server` any_peer | `World.gd` |
| E-017 | play card server turn validation | `World.gd` |
| E-018 | play ownership check hiánya | `World.gd` |
| E-019 | switch server csak existence/turn check | `World.gd` |
| E-020 | scene-node reparent mutation | `World.gd` |
| E-021 | server-side score calculation | `World.gd` |
| E-022 | score recalc any_peer | `World.gd` |
| E-023 | CardResource typed definition | `Cards/CardResource.gd` |
| E-024 | minden card resource preload | `Scenes/World/Deck.gd` |
| E-025 | card name definition ID-ből | `Scenes/World/Deck.gd` |
| E-026 | teljes card resource minden kliensben | `Deck.gd` + `World.gd` |
| E-027 | fixed IP/port | `Global.gd` |
| E-028 | global selected card names | `Global.gd` |
| E-029 | dedicated Linux export preset | `export_presets.cfg` |
| E-030 | hárompéldányos manual workflow | `CONTRIBUTING.md` |
| E-031 | Apache-2.0 | `LICENSE` |
| E-032 | harmadik fél assetek | `README.md` |
| E-033 | vizsgált commit dátuma és tartalma | GitHub commit metadata |
| E-034 | repository nem archivált | GitHub repository metadata |

# 34. Prioritásos exploit-scenariók helyi auditja

## P0-1 – Ellenfél kézlapjának kijátszása

1. kliens kiolvassa az opponent hand card node nevét;
2. saját köre alatt `play_card_server` hívás;
3. server turn check PASS;
4. card zone nem TABLE/DECK, ezért PASS;
5. owner-hand check nincs;
6. server broadcastolja a move-ot.

## P0-2 – Tetszőleges csere

1. kliens kiválaszt két létező card node nevet;
2. `switch_card_server` hívás;
3. server turn check PASS;
4. existence check PASS;
5. zone/ownership check nincs;
6. scene tree hibásan reparentelhető.

## P0-3 – Kör önkényes váltása

1. kliens közvetlenül meghívja `card_played_server` RPC-t;
2. server guard PASS;
3. sender/action correlation nincs;
4. turn megváltozik.

## P0-4 – Korai match start

1. egy peer kétszer küld `intro_done_server` ACK-t;
2. ugyanaz a sender kétszer kerül a tömbbe;
3. size == 2;
4. deck deal elindul a másik peer tényleges ACK-ja nélkül.

## P0-5 – Hidden deck olvasás

1. kliens megkapja a teljes random indexlistát;
2. lokálisan felépíti a teljes decket;
3. resource és card ID alapján kiolvassa minden jövőbeli húzást.

## P1-1 – Foglalt dropzone újrahasználata

1. kliens közvetlen RPC-vel ugyanazt a `dz_name` értéket küldi;
2. server csak existence checket végez;
3. occupancy nincs validálva;
4. több kártya ugyanarra a pozícióra kerülhet.

# 35. Nyitott kérdések

1. A fenti P0 scenariók futásban reprodukálhatók-e?
2. Az `@rpc` default transfer mode reliable-e minden actionnél?
3. Milyen maximális packet- és stringméretet enged a projekt?
4. A card name globálisan mindig egyedi-e?
5. A dedicated server scene tree teljesen betöltődik-e headless módban?
6. A Tweenek headless szerveren azonos időzítéssel futnak-e?
7. Klienslag mennyire befolyásolja az intro/deal ACK-t?
8. Disconnect után a megmaradt kliens milyen UI-állapotban marad?
9. Lehetséges-e duplicate game-over?
10. Lehetséges-e ugyanazt a requestet gyorsan többször elküldeni?
11. Van-e ENet channel separation?
12. Van-e packet throttling?
13. A display name okozhat-e UI/layout problémát?
14. Az exportált kliensből egyszerűen módosítható-e a Global server address?
15. A third-party assetek milyen licencfeltételekkel használhatók?
16. Van-e dokumentálatlan test branch?
17. Van-e release artifact?
18. A server executable milyen erőforrásokat csomagol?
19. A teljes deck identity mennyire könnyen olvasható remote debugger nélkül?
20. Érdemes-e a Pali ellen konkrét AETERNA multiplayer threat-model tesztcsomagot készíteni?

# 36. Következő vizsgálati lépések

## 36.1 Codex nélkül

1. helyi origin és HEAD ellenőrzése;
2. Godot 4.1 import;
3. dedicated server export;
4. hárompéldányos localhost smoke;
5. normal match trace;
6. RPC lista és mode export;
7. opponent-hand memory inspection;
8. full deck order inspection;
9. duplicate intro ACK;
10. duplicate deal ACK;
11. direct `card_played_server`;
12. opponent-card play spoof;
13. arbitrary switch spoof;
14. occupied dropzone spoof;
15. duplicate request flood;
16. disconnect scenario;
17. assetlicenc-inventory;
18. server package-content audit.

## 36.2 Később Codexszel gyorsítható

1. RPC call graph;
2. trust-boundary inventory;
3. mutation path inventory;
4. automated malicious client harness;
5. server/client state-diff logger;
6. hidden-information taint analysis;
7. AETERNA ActionRequest adapter proof;
8. MatchHost/EngineSession server skeleton;
9. three-process integration harness;
10. protocol threat-model dokumentum.

# 37. Végső minősítés

- **Dedikált szerver tanulási érték:** magas
- **ENet lifecycle érték:** magas
- **Authoritative rules érték:** közepes-alacsony
- **Server-side validation érték:** részleges
- **Hidden-information biztonság:** elégtelen
- **RPC security:** elégtelen
- **Determinism/replay:** elégtelen
- **Godot 3D presentation:** magas
- **Teszt/CI érettség:** alacsony
- **Licenc:** kedvező Apache-2.0, assetenként külön audit szükséges
- **Közvetlen dependency:** nem javasolt
- **Clean-room multiplayer tanulási forrás:** kiemelten ajánlott
- **Legfontosabb AETERNA-tanulság:** a dedicated server mellett is kötelező a teljes
  engine-owned state, a player-specific projection és az egyetlen validált action gate
- **Elemzés státusza:** első teljes source audit elkészült
- **Következő learning cél:** `insideout-andrew/simple-card-pile-ui`

# 38. Változásnapló

## 0.1 – 2026-07-25

- elkészült a `rametta/Pali` első teljes multiplayer- és authority-source auditja;
- rögzítésre került a Godot 4.1, ENet és dedicated server szerkezet;
- feldolgozásra került a kétpeer-es lobby és match lifecycle;
- elkészült a teljes RPC inventory;
- azonosításra került a teljes deck order és hidden-hand identity szivárgása;
- azonosításra került a `card_played_server` közvetlen RPC-kockázata;
- azonosításra került a play ownership validation hiánya;
- azonosításra került a switch zone/ownership validation hiánya;
- azonosításra került az intro/deal ACK duplicate és animation-gate probléma;
- feldolgozásra került a server-side score calculation;
- elkészült az AETERNA MatchHost, ActionRequest és player projection javaslat;
- elkészült a prioritásos exploit-scenariók listája;
- rögzítésre került az Apache-2.0 licenc és a külön assetaudit szükségessége;
- a következő kijelölt projekt `insideout-andrew/simple-card-pile-ui`.
