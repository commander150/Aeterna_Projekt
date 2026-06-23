# AETERNA sample contracts contract-spec v0.1

Ez a dokumentum a jelenlegi statikus Godot sample contract réteg belső fejlesztői specifikációja.
A leírás debug/sample szintű, később szigorítandó.

## 1. Áttekintés

A `Godot/sample_contracts/` mappa három kézzel olvasható, determinisztikus contract fájlt tartalmaz:

- `sample_snapshot.json`
- `sample_legal_actions.json`
- `sample_events.json`

A cél a Godot oldali contract-first adatbetöltés, alapvalidálás és debug megjelenítés bizonyítása.
A sample contract réteg a `Godot/sample_runtime_package/` runtime package kártyaadatára hivatkozhat `card_id` értékekkel.

Ez a réteg nem szabálymotor, nem action execution rendszer, és nem event playback motor. A fájlok statikus minták: nem számított, nem visszajátszott és nem végrehajtott állapotot írnak le.

## 2. Közös contract szabályok

Minden sample contract fájlban kötelező:

- `schema_version`: a fájl contract verziója.
- `match_id`: azonos sample mérkőzésre mutató azonosító.
- `diagnostics`: diagnosztikai blokk.
- `diagnostics.warnings`: lista nem blokkoló figyelmeztetésekhez.
- `diagnostics.blocking_errors`: lista blokkoló hibákhoz.

Az ismeretlen mezők jelenleg toleráltak debug célból. Ez debug/sample szintű, később szigorítandó.

Blocking error jelentése: a contract elfogadása nem biztonságos, a debug loader vagy dashboard `ok` értéke nem lehet `true`.

## 3. `sample_snapshot.json` spec

Kötelező top-level mezők:

- `schema_version`
- `snapshot_id`
- `match_id`
- `active_player_id`
- `turn_number`
- `phase`
- `players`
- `board`
- `diagnostics`

Opcionális top-level mezők:

- `selected_card_id`

`snapshot_id` a konkrét statikus állapot azonosítója. Erre hivatkozhat például a legal actions contract `generated_for_snapshot_id` mezője.

`active_player_id` az aktuális aktív játékos azonosítója. Ez nem jelent szabályszámítást, csak a sample állapot metaadata.

`turn_number` a sample állapot körszáma. Debug/sample szintű, később szigorítandó.

`phase` a sample állapot fázisneve. Nem hajt végre fázislogikát.

### `players`

A `players` lista elemei:

- `player_id`
- `display_name`
- `realm`
- `seals_remaining`
- `deck_count`
- `hand_count`
- `wellspring_count`
- `void_count`

Ezek számláló és megjelenítési adatok, nem futtatnak játékszabályt.

### `board`

A `board` jelenlegi szerkezete:

- `lanes`: lista lane objektumokkal.
- `currents`: lista kártyareferenciákkal.

Lane mezők:

- `lane_id`
- `controller_player_id`
- `card_refs`

Card ref mezők:

- `card_id`
- `instance_id`
- `zone`
- opcionálisan `owner_player_id`
- opcionálisan `position`

A `card_id` a runtime package `cards.jsonl` egyik létező kártyájára mutasson.

### `diagnostics`

A snapshot diagnostics blokk csak az adott sample állapot strukturális vagy adatminőségi megjegyzéseit írja le. Nem játékszabályi döntés.

## 4. `sample_legal_actions.json` spec

Kötelező top-level mezők:

- `schema_version`
- `match_id`
- `generated_for_snapshot_id`
- `actions`
- `diagnostics`

Jelenleg használt top-level mező:

- `active_player_id`

`generated_for_snapshot_id` annak a snapshotnak az azonosítója, amelyhez a statikus action lista tartozik. Ennek létező `snapshot_id` értékre kell mutatnia.

`active_player_id` a sample action lista aktív játékosát jelöli, ha szerepel. Nem számít legal actiont.

### `actions`

Az `actions` lista elemei:

- `action_id`: egyedi action azonosító a sample fájlon belül.
- `action_type`: debug célú típusnév, például `play_card` vagy `attack`.
- `label_hu`: emberi olvasásra szánt magyar címke.
- `source_card_id`: opcionális kártyahivatkozás runtime package kártyára.
- `target_refs`: opcionális célhivatkozás lista.
- `cost_summary`: opcionális, emberi olvasásra szánt költségösszefoglaló.
- `enabled`: logikai érték, a statikus minta szerint engedélyezett-e.
- `disabled_reason`: opcionális magyarázat, ha `enabled` értéke `false`.

`enabled` nem szabálymotor eredménye ebben a rétegben, hanem statikus contract adat.

### `target_refs`

`target_refs` elemei jelenleg debug/sample szintű objektumok:

- `type`
- `id`

Ha a target kártyára mutat, a `type` értéke legyen `card` vagy `card_id`, az `id` pedig létező runtime package `card_id`.

### `diagnostics`

A legal actions diagnostics blokk strukturális vagy adatminőségi jelzésre szolgál. Nem action végrehajtási eredmény.

## 5. `sample_events.json` spec

Kötelező top-level mezők:

- `schema_version`
- `match_id`
- `events`
- `diagnostics`

### `events`

Az `events` lista elemei:

- `event_id`: egyedi event azonosító a sample fájlon belül.
- `sequence`: növekvő sorrendi szám.
- `event_type`: debug célú eseménytípus.
- `actor_player_id`: opcionális játékoshivatkozás.
- `card_id`: opcionális kártyahivatkozás runtime package kártyára.
- `message_hu`: emberi olvasásra szánt magyar üzenet.
- `refs`: opcionális objektum további hivatkozásokhoz.

Az event lista sorrendje `sequence` alapján értelmezhető. Ez nem playback sorrend és nem állapot-visszajátszás.

### `refs`

A `refs` objektum jelenleg debug/sample szintű, később szigorítandó.
Ha egy kulcs neve `card_id` vagy `_card_id` végű, a debug nézet kártyahivatkozásként próbálhatja feloldani.

### `diagnostics`

Az events diagnostics blokk strukturális vagy adatminőségi jelzésre szolgál. Nem event playback eredmény.

## 6. Hivatkozási szabályok

- A `match_id` mindhárom fájlban egyezzen.
- A `generated_for_snapshot_id` létező `snapshot_id` értékre mutasson.
- A `card_id`, `card_ref.card_id` és `source_card_id` létező runtime package kártyára mutasson.
- Ha egy card ref nem oldható fel, a debug nézetben `UNKNOWN CARD: <card_id>` jelenhet meg.
- Hiányzó card ref jelenleg nem feltétlen production fatal, de smoke testben trackingelendő `missing_card_refs` értékkel.

Ez a hivatkozáskezelés debug/sample szintű, később szigorítandó.

## 7. Diagnostics szabályok

`warnings` használható nem blokkoló adatminőségi vagy interpretációs megjegyzésekre.

`blocking_errors` használható olyan contract hibára, amely mellett a minta elfogadása nem biztonságos.

A debug nézetek `ok` értéke akkor lehet `true`, ha az adott réteg alapbetöltése sikeres és nincs blokkoló hiba.

Unified dashboard összesítési elv:

- `ok` csak akkor `true`, ha a snapshot, legal actions és event log alrétegek `ok` értéke is `true`.
- `blocking_errors` nem rejthető el; az összesítés legalább a blokkoló alréteg értékét meg kell őrizze.

## 8. Verziózás

Jelenlegi `schema_version` értékek:

- `sample-snapshot-v1`
- `sample-legal-actions-v1`
- `sample-events-v1`

Későbbi v2 változásnál új schema version értéket kell bevezetni, és a loader/debug nézeteknek explicit módon kell kezelniük az új verziót.

Visszafelé kompatibilitás jelenleg nincs garantálva, mert ez sample/debug réteg.

## 9. Nem célok

Ez a spec nem írja le:

- teljes játékszabályt;
- action számítást;
- action végrehajtást;
- event playbacket;
- snapshot visszajátszást eventekből;
- AI döntéshozatalt;
- production online protokollt.

## 10. Javasolt következő fejlesztési lépés

Biztonságos következő lépés lehet egy `contract consistency smoke test v0.1`, amely külön ellenőrzi:

- `match_id` egyezést;
- `generated_for_snapshot_id` hivatkozást;
- runtime package kártyahivatkozásokat;
- diagnostics blokkok alakját;
- `missing_card_refs` számlálást.

Alternatív következő lépés lehet egy `action_request sample contract v0.1`, amely továbbra sem hajt végre actiont, csak egy kért action statikus contract alakját rögzíti.
