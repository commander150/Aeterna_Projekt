# AETERNA game engine – aktuális állapotösszefoglaló

Dátum: 2026-07-12
Fókusz: AETERNA digitális engine / AI-vs-AI tesztelő / későbbi Godot debug UI

## 1. Rövid, érthető állapotkép

A program jelenleg még nem teljes AETERNA digitális játék, és még nem teljes AI-vs-AI tesztelő. Viszont elkészült egy stabil, contract-first engine alap, amelyre már rá lehet építeni az AI-vs-AI tesztelő első valódi változatát.

A legfontosabb változás: a motor már nemcsak állapotot tud létrehozni és körpasszolást kezelni, hanem van egy minimális, működő `draw_card` akció is.

Ez azt jelenti, hogy a program jelenleg már képes erre:

* létrehoz egy minimális meccsállapotot;
* meg tudja mondani, milyen akciók érhetők el;
* az aktív játékos tud `draw_card` akciót végrehajtani;
* a húzás ténylegesen mozgat 1 lapot a pakliból a kézbe;
* a `deck_count` csökken;
* a `hand_count` nő;
* a `state_version` nő;
* event keletkezik;
* a változás JSON debug exportban látható;
* hibás akciók esetén stabil rejected response jön vissza, nem omlik össze a session.

Egyszerűen: már nem csak láthatatlan alapozás van, hanem az első kicsi játékszerű művelet is működik.

## 2. A jelenlegi fejlesztési irány

A jelenlegi engine továbbra is Pythonban készül, de ez nem végleges technológiai döntés.

A projekt hivatalos álláspontja:

* a mostani Python engine egy contract-first referencia / smoke / backend-jelölt réteg;
* a végleges runtime később lehet Python, GDScript vagy hibrid modell;
* Godot továbbra is a vizuális felület / kliens / debug UI fő jelöltje;
* a szabálylogika ne szóródjon szét Godot node-okba;
* Godot és AI a stabil engine contractokon keresztül kommunikáljon.

## 3. Mi készült el a legutóbbi engine-szakaszban?

### 3.1. MinimalEngineSession boundary

Létrejött a `MinimalEngineSession`, ami a központi engine API szerepét tölti be.

Fontosabb metódusok:

* `create_match()`
* `get_debug_snapshot()`
* `get_player_snapshot(player_id)`
* `list_legal_actions()`
* `get_action_space(player_id=None)`
* `submit_action_request(request)`
* `step(request)`
* `get_event_log()`
* `get_diagnostics()`
* `get_last_action_response()`
* `get_action_response_history()`
* `get_transition_summary()`
* `export_debug_session_state()`
* `export_smoke_report()`
* `get_draw_precondition(player_id)`

Ez azért fontos, mert a későbbi AI, Godot debug panel, fake UI és smoke runner ugyanazon a session boundaryn keresztül tud dolgozni.

## 4. Snapshotok és nézetek

### 4.1. Debug snapshot

A debug snapshot a fejlesztői / tesztelői nézet. Ebben lehet több információ, mint amit egy valódi játékos láthatna.

### 4.2. Player-visible snapshot stub

Készült külön `player_visible_snapshot` is.

Fontos: ez még nem valódi hidden information modell, csak API-szintű elkülönítés.

A metadata jelenleg jelzi:

* `hidden_information_model: "not_implemented"`

Ez jó, mert később nem kell utólag szétválasztani a debug és player nézeteket.

## 5. State version és event sequence

Bevezetésre került:

* `state_version`
* `event_sequence`

Jelenlegi működés:

* kezdeti állapot: `state_version = 0`
* sikeres akció után: `state_version` nő
* eventek kapnak `event_sequence` mezőt
* az első event sequence jelenleg `1`

Ez később fontos lesz:

* debug UI szinkronhoz;
* AI futtatásokhoz;
* regressziós tesztekhez;
* replay funkcióhoz, ha később bekerül;
* események sorrendjének bizonyításához.

## 6. Action space contract

A régi `list_legal_actions()` kompatibilis maradt, mellette létrejött a stabil külső wrapper:

* `get_action_space(player_id=None)`

Ez adja vissza, hogy a játékos milyen akciókat hajthat végre.

A legal action space fő mezői:

* `schema_version`
* `contract_type: "legal_action_space"`
* `match_id`
* `player_id`
* `state_version`
* `turn`
* `phase`
* `active_player_id`
* `priority_player_id`
* `actions`
* `enabled_action_count`
* `disabled_action_count`
* `metadata`

Az action mezők:

* `action_id`
* `action_type`
* `player_id`
* `enabled`
* `disabled_reason`
* `request_template`
* `metadata`

Jelenlegi akciók:

* `end_turn`
* `draw_card`

## 7. Action response contract

A `submit_action_request()` és a `step()` stabil JSON-kompatibilis action response contractot ad vissza.

Fő mezők:

* `schema_version`
* `contract_type: "action_response"`
* `response_type: "minimal_action_response"`
* `match_id`
* `request_id`
* `player_id`
* `action_id`
* `action_type`
* `accepted`
* `success`
* `reason`
* `state_version_before`
* `state_version_after`
* `new_event_count`
* `new_event_sequences`
* `events`
* `diagnostics_summary`
* `invariants_ok`
* `metadata`

Ez sikeres és rejected action esetén is működik.

## 8. Rejected action response

Hibás akció esetén nem exception vagy széteső állapot történik, hanem stabil rejected response.

Tesztelt rejected esetek:

* ismeretlen action id: `unknown_action_id`
* rossz játékos: `player_not_active`
* üres deck draw esetén: `deck_empty`

Rejected response esetén:

* `accepted: false`
* `success: false`
* `state_version_before == state_version_after`
* `new_event_count == 0`
* `new_event_sequences == []`
* `events == []`
* event log nem nő
* a session utána tovább használható

Ez nagyon fontos későbbi Godot UI és AI runner miatt.

## 9. Response history és transition summary

A session eltárolja az action response-okat.

Metódusok:

* `get_last_action_response()`
* `get_action_response_history()`

Ez csak response contractokat tárol, nem teljes state historyt.

Készült transition summary is:

* `get_transition_summary()`

Ez gépileg olvasható rövid összesítő:

* event count
* last event sequence
* response count
* accepted response count
* rejected response count
* last response állapota
* aktuális state version

Ez nem replay rendszer, csak debug/API összesítő.

## 10. Debug session export

Készült egy egyesített debug export:

* `export_debug_session_state()`

Fő mezők:

* `schema_version`
* `contract_type: "debug_session_state"`
* `match_id`
* `debug_snapshot`
* `action_space`
* `transition_summary`
* `last_action_response`
* `diagnostics_summary`
* `metadata`

Ez később alkalmas lehet:

* Godot debug panelhez;
* fake UI-hoz;
* AI runnerhez;
* smoke runnerhez;
* fejlesztői ellenőrzésekhez.

Replay státusz:

* `replay_support: "not_implemented"`
* `replay_future_candidate: true`

Fontos döntés: a végleges AETERNA-ban lehet később replay funkció, de most nem prioritás. A jelenlegi rendszer nem replay engine.

## 11. JSON debug CLI export

A smoke runner kapott JSON módot:

* `python tools/engine/run_minimal_engine_smoke.py --json-debug-export`

Ez:

* csak valid JSON-t ír stdout-ra;
* nem ír fájlt;
* nem készít tracked outputot;
* gépileg olvasható debug state-et ad.

A normál BAT továbbra is emberileg olvasható:

* `run_minimal_engine_smoke.bat`

## 12. Hand/deck/discard zóna-invariantok

A program jelenleg meglévő mezőkre épít:

* `PlayerState.deck_card_ids`
* `PlayerState.hand`
* `PlayerState.discard`

Készült minimális zóna-invariant réteg:

* player zónák nem lehetnek `None`;
* deck / hand / discard listák;
* ugyanaz a `card_id` nem lehet egyszerre ugyanannál a játékosnál deckben és handben;
* runtime package mellett deck card reference validáció továbbra is fut.

Snapshotokban megjelent:

* `zone_summary.deck_count`
* `zone_summary.hand_count`
* `zone_summary.discard_count`

Diagnosticsban megjelent:

* `hand_deck_invariants_ok`

## 13. Draw precondition

Készült read-only helper:

* `can_player_draw(state, player_id)`
* `MinimalEngineSession.get_draw_precondition(player_id)`

Ez megmondja:

* tud-e a játékos húzni;
* miért nem;
* mennyi lap van a deckben;
* mennyi lap van kézben.

Lehetséges reason értékek:

* `ok`
* `deck_empty`
* `player_unknown`

Ez még nem mozgatott lapot, csak előkészítette a draw actiont.

## 14. Minimal draw action vertical slice

Utolsó commit:

* `fe75471 Add minimal draw action vertical slice`

Új action:

* `draw_card`

Működés:

* az aktív játékos húzhat;
* ha van lap a deckben, `draw_card.enabled == true`;
* ha üres a deck, `draw_card.enabled == false`, illetve rejected response reason: `deck_empty`;
* sikeres draw esetén 1 lap mozog a deckből a handbe;
* `deck_count` csökken;
* `hand_count` nő;
* `state_version` nő;
* `card_drawn` event keletkezik;
* event kap `event_sequence` mezőt;
* `last_action_response.action_type == "draw_card"`;
* `end_turn` draw után is működik.

Nem készült:

* automatikus draw phase;
* Refresh Penalty;
* play_card;
* attack;
* payment;
* targeting;
* ability executor;
* teljes rules engine;
* replay rendszer.

Ez az első valódi játékszerű engine művelet.

## 15. Fontos technikai adósság: Card_ID vs card instance

A mostani modellben a `deck_card_ids` és `hand` még `card_id` szinten dolgozik.

Ez később problémás, mert egy TCG-ben ugyanabból a lapból több példány is lehet a pakliban.

Hosszabb távon kell majd különbséget tenni:

* `Card_ID`: a kártyatípus, például egy konkrét lap szabályi azonosítója;
* `Card_Instance_ID`: egy konkrét példány a meccsen belül.

Jelenlegi workaround:

* a minimal draw determinisztikusan olyan deckbeli `card_id`-t húz, amelyből nincs másik példány a deckben, hogy a mostani invariant zöld maradjon.

Ez prototípushoz elfogadható, de később szükséges lesz card instance / zone instance modell.

Ez fontosabb technikai adósság, amit nem szabad elfelejteni.

## 16. AI-vs-AI állapot

Jelenleg még nincs teljes AI-vs-AI játéktesztelő, de már elég sok alap elkészült hozzá.

Már megvan:

* session létrehozás;
* legal action space;
* `draw_card`;
* `end_turn`;
* action request;
* action response;
* accepted/rejected handling;
* event log;
* state version;
* debug JSON export;
* response history;
* transition summary.

Ez már elég ahhoz, hogy a következő nagyobb lépés egy nagyon egyszerű AI-vs-AI loop legyen:

* P1 lekéri az action space-t;
* bot választ `draw_card` vagy `end_turn` között;
* engine végrehajtja;
* P2 lekéri az action space-t;
* bot választ;
* engine végrehajtja;
* ez ismétlődik max lépésszámig.

Ez még nem teljes AETERNA játék, de már látható AI-vs-AI technikai teszt lehet.

## 17. Godot állapot

Godot még nincs rákötve erre az új engine session / debug JSON export rendszerre.

Viszont már van mit megjeleníteni:

* aktív játékos;
* P1 deck_count / hand_count;
* P2 deck_count / hand_count;
* elérhető actionök;
* utolsó action response;
* event count;
* state_version;
* diagnostics summary;
* draw precondition;
* draw után változó deck/hand számok.

Ez alapján később egy első Godot debug UI meg tudná jeleníteni például:

* P1 húzott egy lapot;
* P1 deck: 4;
* P1 hand: 1;
* last event: `card_drawn`;
* state_version: 1.

Első Godot cél ne teljes játék UI legyen, hanem debug panel / tesztpanel.

## 18. Régi AETERNA tesztprogram hasznosítása

A korábbi AETERNA tesztprogram nem fő iránynak javasolt, de hasznos referencia lehet.

Lehetséges hasznos részek:

* AI-vs-AI loop gondolata;
* bot ciklus;
* match loop;
* korábbi tesztlogika;
* korábbi hibák tanulságai;
* esetleges egyszerű húzás / körkezelés / lapkijátszás ötletek.

Nem javasolt:

* a régi programot fő alapként foltozni;
* régi szabálymodellt változtatás nélkül átvenni;
* régi HP / Pecsét / zóna / erőforrás modellt visszahozni;
* contract-first alapot feladni.

Javasolt hozzáállás:

* régi program = referencia / bányászati forrás;
* új engine = fő irány.

## 19. Letöltött külső kártyás/Godot projektek hasznosítása

A külső projektek tanulási forrásként hasznosak, de nem javasolt őket közvetlenül AETERNA-motorrá alakítani.

Hasznosítható belőlük:

* Godot kártya node ötletek;
* kéz megjelenítés;
* deck / discard zone UI;
* drag & drop;
* hover / zoom;
* debug panel;
* deck builder ötletek;
* UI szervezési minták.

Nem javasolt:

* külső szabálymotor közvetlen átvétele;
* külső projekt átalakítása AETERNA szabálymotorra;
* licencelt kód másolása;
* AGPL/GPL jellegű kód beépítése;
* AETERNA egyedi szabályait idegen engine-re erőltetni.

Javasolt hozzáállás:

* külső projektek = tanulási és UI inspiráció;
* szabálymotor = saját AETERNA contract-first engine.

## 20. Jelenleg mi működik?

A program jelenleg működőképesen tudja:

* minimal match state létrehozása;
* state invariant ellenőrzés;
* hand/deck/discard invariant ellenőrzés;
* debug snapshot;
* player-visible snapshot stub;
* action space export;
* `end_turn` action;
* `draw_card` action;
* valid action response;
* rejected action response;
* state_version követés;
* event_sequence követés;
* card_drawn event;
* response history;
* transition summary;
* debug session export;
* JSON debug CLI export;
* draw precondition;
* empty deck draw reject;
* smoke BAT futás;
* JSON export stdout-ra.

## 21. Mi nincs még kész?

Még nincs:

* teljes AI-vs-AI tesztelő;
* `MinimalEngineEnvironment` / `AeternaEnv`;
* bot policy valódi döntésekkel;
* automatikus turn loop;
* kezdőkéz / setup draw;
* play_card action;
* Aura / Magnitúdó fizetés;
* célzás;
* támadás;
* Entitás boardra rakása;
* Horizont / Zenit / Áramlat működő boardmodell;
* Pecsét / vereségmodell runtime működésben;
* Refresh Penalty;
* ability executor;
* kulcsszóhatások;
* teljes phase rendszer;
* valódi hidden information modell;
* card instance modell;
* Godot debug UI rákötés;
* replay rendszer.

## 22. Javasolt következő fejlesztési sorrend

A következő sorrendet javasolt tartani, hogy ne ugorjunk túl nagyot.

### 1. Minimal AI-vs-AI runner / environment stub

Cél:

* `reset()`
* `get_action_space()`
* `step()`
* egyszerű bot választás
* max lépésszám
* trajectory summary

A bot kezdetben lehet nagyon egyszerű:

* ha lehet húzni, húz;
* különben end_turn;
* vagy determinisztikus sorrend szerint választ.

Ez már látványosabb futás lenne, de még nem teljes játék.

### 2. Card instance technikai terv

Mielőtt sok zónamozgatás készül, rögzíteni kell:

* hogyan különül el `Card_ID` és `Card_Instance_ID`;
* mikor kap példányazonosítót egy lap;
* hogyan mozog instance deck / hand / discard / board között.

Nem biztos, hogy ezt azonnal implementálni kell, de a terv kelleni fog.

### 3. Minimal setup / starting hand

Később:

* kezdődeck;
* kezdőkéz;
* setup draw;
* determinisztikus tesztállapot.

### 4. Minimal play_card előkészítés

Előbb csak precondition:

* van-e a lap kézben;
* aktív játékosé-e;
* milyen típusú a lap;
* most még fizetés nélkül vagy nagyon minimális fizetéssel.

### 5. Minimal Godot debug panel

Első Godot cél ne teljes játék UI legyen.

Első debug panel mutassa:

* P1/P2 deck_count;
* P1/P2 hand_count;
* aktív játékos;
* action space;
* last action response;
* event count;
* state_version;
* draw gomb / end_turn gomb később.

## 23. Következő Codex-feladat javaslat

A legjobb következő Codex-feladat valószínűleg:

* `MinimalEngineEnvironment` / `AeternaEnv` stub létrehozása;
* csak `draw_card` és `end_turn` használatával;
* nincs új gameplay szabály;
* nincs Godot;
* nincs play_card;
* nincs attack;
* nincs payment;
* nincs ability.

Ez adná az első valóban látható AI-vs-AI futtató keretet.

A feladat célja ne teljes AI legyen, csak:

* két egyszerű bot;
* determinisztikus döntés;
* max lépésszám;
* trajectory / episode summary;
* JSON-kompatibilis eredmény;
* meglévő session contractok használata.

## 24. Összegzés

A program jelenleg stabil contract-first engine prototípus, amely már tartalmazza az első minimális gameplay-szerű akciót: `draw_card`.

Még nem teljes játék, de már jó alap az első AI-vs-AI tesztelőhöz.

A legfontosabb elért állapot:

* van engine session;
* van action discovery;
* van action execution;
* van draw;
* van end_turn;
* van accepted/rejected response;
* van event/state követés;
* van debug JSON export;
* van zóna-invariant;
* van előkészített út az AI-vs-AI runnerhez és később Godot debug UI-hoz.

A fejlesztés jó irányban halad, de továbbra is kis, kontrollált lépésekben érdemes menni.
