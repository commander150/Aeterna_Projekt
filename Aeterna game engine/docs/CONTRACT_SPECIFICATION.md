# AETERNA Game Engine – Contract Specification

Ez a dokumentum az AETERNA Game Engine contract-first rétegének fő specifikációs váza.

Nem teljes rules engine specifikáció.

Nem runtime package schema.

Nem ability module rendszerleírás.

Nem checkpoint-napló.

Feladata, hogy egységes dokumentumba rendezze azokat a fő adatcontractokat, amelyek később összekötik a runtime package-et, a rules engine-t, a Godot/GDScript debug és UI réteget, az AI-t, a diagnostics rendszert és a későbbi simulation/balance futtatásokat.

Kapcsolódó fő dokumentumok:

- `DECISION_MAP.md`
- `ARCHITECTURE.md`
- `TECHNOLOGY_DECISIONS.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `ABILITY_MODULE_SYSTEM.md`
- `OPEN_QUESTIONS.md`
- `CHECKPOINTS.md`
- `PROTOTYPE_PLANS.md`

---

## Általános contract alapok

### 1. Contract-first alapelv

Az AETERNA Game Engine egyik központi alapelve:

**előbb contract, utána implementáció**

Ez azt jelenti, hogy a fő rendszerrészek nem egymás belső objektumaira, hanem explicit adatcontractokra épülnek.

A contractok célja:

- a frontend ne találgasson szabályokat;
- az AI ne találgasson szabályokat;
- a Godot UI ne tartalmazzon rejtett rules logicot;
- a rules engine világos formában adja vissza az állapotot, a lehetséges döntéseket, a végrehajtás eredményét és a diagnosztikát;
- a rejtett információ ne szivárogjon ki player-visible nézetben;
- ugyanaz az adatút használható legyen Python, Godot/GDScript, AI és tesztrétegek között;
- később összehasonlítható legyen Python és GDScript viselkedése.

---

### 2. Fő contractok

A contract-specifikáció jelenlegi fő rétegei:

- Runtime package
- Snapshot
- Legal actions
- Action request
- Action response
- Event log
- Diagnostics
- Ability registry
- Engine support report
- Sample contracts
- Contract consistency checks

A runtime package részletes leírása külön dokumentumba tartozik:

- `RUNTIME_PACKAGE_SPECIFICATION.md`

Az ability/effect module részletes leírása külön dokumentumba tartozik:

- `ABILITY_MODULE_SYSTEM.md`

Ez a dokumentum elsősorban az engine és frontend / AI / debug rétegek közötti contractokra fókuszál.

---

### 3. Contractok közötti alapkapcsolat

A fő működési lánc:

1. A runtime package betöltődik.
2. A match state vagy sample state létrejön.
3. A rendszer snapshotot ad egy adott nézőpontnak.
4. A rendszer legal action listát ad az adott döntési helyzethez.
5. A frontend vagy AI action requestet küld.
6. A rules engine validál.
7. A rules engine action response-t ad.
8. A response eventeket és diagnostics bejegyzéseket tartalmazhat.
9. A rendszer új snapshotot adhat vissza.
10. Az event logból követhető, mi történt.

Fontos elhatárolás:

- A snapshot az állapot nézőpontfüggő kivetítése.
- A legal action lista a szabályos döntések listája.
- Az action request a játékos vagy AI kérése.
- Az action response a validálás és végrehajtás eredménye.
- Az event log a történeti réteg.
- A diagnostics a problémák strukturált rétege.

---

### 4. Közös contract mezők

A legtöbb contractban érdemes közös azonosítókat használni.

Ajánlott közös mezők:

- `schema_version`
- `contract_type`
- `runtime_package_id`
- `runtime_package_version`
- `ruleset_version`
- `match_id`
- `snapshot_id`
- `turn`
- `phase`
- `step`
- `active_player_id`
- `priority_player_id`
- `viewer_id`
- `visibility_mode`
- `diagnostics`
- `metadata`

Ezek nem minden contractban kötelezőek, de a fő contractok között következetes névhasználat szükséges.

---

### 5. Schema version szabály

Minden önálló contractnak rendelkeznie kell schema verzióval.

Példák:

- `sample-snapshot-v1`
- `sample-legal-actions-v1`
- `sample-events-v1`
- `runtime-package-v1`
- `diagnostics-v1`

A schema verzió célja:

- kompatibilitás ellenőrzése;
- loader oldali validáció;
- régi sample fájlok felismerése;
- Godot és Python közötti adatváltozások kontrollja;
- későbbi migration támogatása.

Nyitott kérdés:

- Mikortól legyen a schema verziózás szigorúan blokkoló?

---

### 6. Visibility alapelv

A contract-rendszer egyik legfontosabb biztonsági elve:

**player-visible contract nem szivárogtathat rejtett információt**

Ez érinti:

- snapshotot;
- legal action listát;
- event logot;
- diagnostics üzeneteket;
- AI nézőpontokat;
- debug nézeteket;
- replayt.

A debug nézet tartalmazhat többletinformációt, de ezt egyértelműen el kell választani a player-visible nézettől.

Lehetséges visibility értékek:

- `debug`
- `player_visible`
- `opponent_visible`
- `spectator`
- `ai_fair`
- `ai_debug`

---

## Snapshot contract

### 7. Snapshot célja

A snapshot a match state nézőpontfüggő kivetítése.

Nem azonos a teljes belső match state-tel.

A snapshot célja:

- Godot UI megjelenítés;
- debug viewer;
- AI döntés-előkészítés;
- tesztelés;
- későbbi replay támogatás;
- state consistency ellenőrzés;
- legal action context megadása.

A snapshot ne legyen a szabálymotor belső állapotának közvetlen dumpja.

---

### 8. Snapshot típusok

Lehetséges snapshot típusok:

- `debug_snapshot`
- `player_visible_snapshot`
- `opponent_visible_snapshot`
- `spectator_snapshot`
- `ai_fair_snapshot`
- `ai_debug_snapshot`
- `replay_snapshot`

MVP-ben valószínűleg elég:

- `debug_snapshot`
- `player_visible_snapshot`

Később szükség lehet külön AI és replay snapshotokra.

---

### 9. Snapshot ajánlott fő mezői

Ajánlott snapshot mezők:

- `schema_version`
- `snapshot_id`
- `snapshot_type`
- `runtime_package_id`
- `ruleset_version`
- `match_id`
- `turn`
- `phase`
- `step`
- `active_player_id`
- `priority_player_id`
- `viewer_id`
- `visibility_mode`
- `match_finished`
- `winner_player_id`
- `victory_reason`
- `players`
- `board`
- `zones`
- `pending`
- `legal_action_summary`
- `recent_events`
- `visible_event_log`
- `diagnostics_summary`
- `scenario_context`
- `metadata`

Ezek közül MVP-ben nem mind kötelező.

---

### 10. Snapshot és match state elválasztása

A match state belső igaz állapot.

A snapshot abból származtatott, nézőpontfüggő állapotkép.

A match state tartalmazhat:

- teljes paklisorrendet;
- rejtett kézlapokat;
- face-down Jelek pontos adatait;
- debug információkat;
- belső engine állapotot;
- pending action részleteket;
- nem player-visible okokat.

A player-visible snapshot csak azt tartalmazhatja, amit az adott játékos szabályosan láthat.

---

### 11. Snapshot és rejtett információ

A snapshot visibility modelljének kezelnie kell:

- saját kézlapok láthatóságát;
- ellenfél kézlapjainak rejtését;
- saját face-down Jelek ismertségét;
- ellenfél face-down Jeleinek rejtését;
- deck sorrend rejtését;
- Ősforrás láthatóságát;
- AI fair és AI debug eltérését;
- spectator nézőpontot.

Nyitott kérdések:

- kell-e külön `known_to` mező;
- kell-e külön `face_down` mező;
- kell-e külön `revealed` mező;
- a fair AI pontosan ugyanazt lássa-e, mint a játékos.

---

### 12. Pending decision snapshotban

A snapshot tartalmazhat `pending` mezőt.

A `pending` célja:

- jelezni, hogy van-e folyamatban lévő döntés;
- megadni a döntési ablak típusát;
- megadni a priority player értékét;
- jelezni, hogy lehet-e passzolni;
- jelezni, milyen actionökre vár a rendszer.

Lehetséges `pending` mezők:

- `has_pending_decision`
- `window_type`
- `priority_player_id`
- `prompt_hu`
- `can_pass`
- `source_event_id`
- `source_action_id`
- `expected_action_family`

Nyitott kérdés:

- a `pending` mező minden snapshotban kötelező legyen-e.

---

### 13. Pecsétmodell snapshotban

Rögzített szabályi irány:

- A Pecsét nem HP-alapú objektum.
- A Pecsét nem rendelkezik `ward_hp` vagy `seal_hp` mezővel.
- A Pecsét feltörési / visszaállítási állapotként kezelendő.

Tiltott vagy kerülendő mezők:

- `ward_hp`
- `seal_hp`
- `seal_damage`
- `ward_damage`

Lehetséges Pecsét állapotok:

- `standing`
- `broken`
- `restored`
- `removed`

Nyitott kérdések:

- a Pecsét lapként, védelmi objektumként vagy mindkettőként jelenjen meg;
- a feltört Pecsét hová kerül;
- kell-e `linked_current`;
- látható-e a Pecsétlap neve;
- a Pecsét állapota a boardhoz vagy a player objektumhoz tartozzon.

---

### 14. Aeternal snapshotban

Rögzített szabályi irány:

- Az Aeternal maga a játékos.
- Az Aeternal nem HP objektum.
- Az Aeternal nem kaphat sebzést.
- Az Aeternal nem gyógyítható.

Tiltott vagy kerülendő mezők:

- `aeternal_hp`
- `player_hp`
- `aeternal_damage`
- `heal_aeternal`
- `heal_player`

Lehetséges engine szintű állapot:

- `aeternal_unprotected`
- `direct_attack_victory_available`
- `defeat_if_attack_connects`

Nyitott kérdés:

- hogyan jelenjen meg snapshotban, hogy egy játékos Aeternálja védtelen.

---

## Legal actions contract

### 15. Legal actions célja

A legal actions contract megadja, hogy egy adott játékos vagy AI milyen szabályos döntéseket hozhat az adott snapshot / match state pillanatban.

Alapelv:

**A frontend és az AI nem számolja ki önállóan a szabályos lépéseket.**

A legal action listát a rules engine vagy egy későbbi rules service adja vissza.

---

### 16. Legal action ajánlott fő mezői

Ajánlott mezők:

- `action_id`
- `action_type`
- `action_family`
- `player_id`
- `priority_player_id`
- `phase`
- `step`
- `window_type`
- `decision_context`
- `source`
- `targets`
- `choices`
- `payment`
- `requirements`
- `availability`
- `ui`
- `ai`
- `diagnostics`
- `metadata`

MVP-ben nem mindegyik kötelező.

---

### 17. Legal action családok

Lehetséges action family értékek:

- `turn_flow`
- `play_card`
- `combat`
- `reaction`
- `targeting`
- `choice`
- `payment`
- `ability`
- `system`
- `debug`

MVP-ben valószínűleg elég:

- `turn_flow`
- `play_card`
- `targeting`
- `reaction`
- `debug`

---

### 18. MVP action type jelöltek

Lehetséges MVP action type-ok:

- `end_turn`
- `pass_priority`
- `play_entity`
- `play_sigil`
- `play_incantation_simple`
- `play_ritual_simple`
- `choose_target_simple`
- `choose_option_simple`
- `debug_select_snapshot`
- `debug_refresh_contracts`

Későbbi action type-ok:

- `declare_attack`
- `choose_attack_target`
- `choose_blocker`
- `activate_sigil`
- `trigger_reaction`
- `pay_cost_manual`
- `choose_replacement`
- `choose_prevention`
- `concede`

---

### 19. Enabled és disabled actionök

A legal action lista tartalmazhat enabled és disabled actionöket.

Lehetséges modellek:

1. Normál játékban csak enabled actionök látszanak.
2. Debug módban disabled actionök is látszanak.
3. Tutorial módban disabled reason is látszhat.
4. AI csak enabled actionöket kap.
5. Debug AI kaphat disabled actionöket is elemzéshez.

Ajánlott irány:

- player-visible normál UI: enabled actionök;
- debug UI: enabled és disabled actionök;
- tutorial később: disabled reason játékosbarát szöveggel.

Nyitott kérdés:

- disabled actionök ugyanabban a listában legyenek-e, vagy külön debug listában.

---

### 20. Legal action és UI mezők

A legal action tartalmazhat UI-segédmezőket, de ezek nem válhatnak szabályforrássá.

Lehetséges UI mezők:

- `label_hu`
- `prompt_hu`
- `short_hint_hu`
- `disabled_reason_hu`
- `highlight_sources`
- `highlight_targets`
- `priority`
- `group`
- `display_order`

Nyitott kérdés:

- a magyar promptokat backend generálja-e, vagy frontend lokalizációs lookup.

---

### 21. Legal action és AI mezők

A legal action később tartalmazhat AI-segédadatokat.

Lehetséges AI mezők:

- `ai_tags`
- `risk_level`
- `requires_hidden_info`
- `estimated_value`
- `debug_score_hint`

Fontos korlátozás:

**Fair AI nem kaphat olyan információt, amit a játékos sem látna.**

Nyitott kérdés:

- legyen-e AI heuristic mező, vagy az AI teljesen külön értékeljen.

---

### 22. Legal action és targeting

A targeting lehet:

- a play action része;
- külön `choose_target` action;
- többlépcsős pending döntés;
- preview mező a legal actionben.

Lehetséges target mezők:

- `target_type`
- `target_scope`
- `valid_targets`
- `min_targets`
- `max_targets`
- `target_order_matters`
- `allow_empty_target`
- `invalid_target_policy`

Nyitott kérdések:

- több célpontnál hogyan kezeljük a sorrendet;
- invalid target esetén teljes vagy részleges feloldás legyen;
- a frontend highlight teljesen legal action adatokból épüljön-e.

---

### 23. Legal action és fizetés

A legal action tartalmazhat cost és payment információt.

Lehetséges mezők:

- `cost_summary`
- `requires_manual_payment`
- `available_payment_sources`
- `auto_payment_possible`
- `temporary_aura_usage`
- `payment_window_required`

Nyitott kérdések:

- meddig legyen automatikus Aura-fizetés;
- mikor kell kézi forrásválasztás;
- ideiglenes Aura elsőként vagy utolsóként költődjön;
- a fizetés külön legal action legyen-e.

---

### 24. Legal action és reakcióablak

A reakcióablak kapcsolódhat:

- Burst Igékhez;
- Jelekhez;
- prevention hatásokhoz;
- replacement hatásokhoz;
- opcionális triggerekkel kapcsolatos döntésekhez.

Nyitott kérdések:

- elég-e reaction queue;
- kell-e stack vagy chain;
- Burst és Jel ugyanabban a reaction rendszerben legyen-e;
- pass reaction külön legal action legyen-e;
- automatikusan átugorható-e a reakcióablak, ha nincs valódi döntés.

---

## Action request contract

### 25. Action request célja

Az action request a frontend vagy AI által küldött döntési kérés.

Alapelv:

**A kliens nem módosítja közvetlenül a játékállapotot.**

A kliens action requestet küld, a rules engine pedig validálja és végrehajtja vagy elutasítja.

---

### 26. Action request ajánlott fő mezői

Ajánlott mezők:

- `request_id`
- `client_request_id`
- `match_id`
- `snapshot_id`
- `state_version`
- `action_id`
- `player_id`
- `action_type`
- `source`
- `targets`
- `choices`
- `payment`
- `metadata`
- `debug`

MVP-ben nem biztos, hogy minden kötelező.

---

### 27. Request azonosítás

Nyitott kérdések:

- kötelező legyen-e `client_request_id`;
- backend vagy frontend generálja a request ID-t;
- kell-e idempotencia;
- hogyan kezeljük a duplicate requestet;
- PvP előtt mennyire legyen szigorú;
- lokális debug módban elég-e egyszerűbb request.

---

### 28. Snapshot frissesség

Az action request tartalmazhat `snapshot_id` és később `state_version` mezőt.

Cél:

- stale snapshot felismerése;
- régi legal action listából származó action elutasítása;
- interaktív UI szinkron tartása;
- későbbi PvP biztonság.

Nyitott kérdések:

- stale snapshot mindig reject legyen-e;
- a backend próbálja-e újravalidálni az actiont;
- PvP és local debug másként kezelje-e.

---

### 29. Action ID élettartama

Az `action_id` valószínűleg snapshoton belül stabil.

Nyitott kérdések:

- kell-e hosszabb életű action token;
- kell-e opaque vagy signed action token később;
- legal action lista frissülésekor mikor érvénytelenedik az action ID;
- AI-vs-AI tesztben szükséges-e stabil action ID.

---

## Action response contract

### 30. Action response célja

Az action response a rules engine válasza az action requestre.

Tartalmazhat:

- validációs eredményt;
- elutasítás okát;
- normalizált actiont;
- végrehajtási eredményt;
- eventeket;
- új snapshotot;
- diagnostics bejegyzéseket;
- pending decision jelzést.

---

### 31. Action response ajánlott fő mezői

Ajánlott mezők:

- `schema_version`
- `response_id`
- `request_id`
- `match_id`
- `snapshot_id`
- `ok`
- `reason`
- `validation`
- `normalized_action`
- `result`
- `events`
- `snapshot`
- `diagnostics`
- `metadata`

---

### 32. Validation reason jelöltek

Lehetséges validation reason értékek:

- `ok`
- `stale_snapshot`
- `unknown_action_id`
- `not_priority_player`
- `wrong_phase`
- `wrong_step`
- `invalid_action_type`
- `invalid_source`
- `invalid_target`
- `invalid_choice`
- `invalid_payment`
- `hidden_information_violation`
- `engine_not_supported`
- `card_not_playable`
- `insufficient_aura`
- `requirement_not_met`
- `action_expired`

---

### 33. Result status jelöltek

Lehetséges result status értékek:

- `executed`
- `rejected`
- `cancelled`
- `prevented`
- `replaced`
- `failed`
- `partially_resolved`
- `pending_choice`
- `pending_target`
- `pending_payment`
- `pending_reaction`
- `not_executable`

Fontos:

**A részleges feloldás nem automatikusan hiba.**

Lehet normál szabályeredmény, ha a hatás egy része szabályosan végrehajtható, más része pedig nem.

---

### 34. Action response és reakcióablak

Nyitott modellek:

1. Az action response `pending_reaction` státuszt ad.
2. Az action rögzül, majd külön reaction window event nyílik.
3. Az action response tartalmazza a következő legal action lista hivatkozását.
4. A reakcióablak külön snapshotot generál.

Nyitott kérdés:

- Burst és Jel válasz ugyanabba az action response / reaction rendszerbe tartozzon-e.

---

## Event log contract

### 35. Event log célja

Az event log a játék történeti rétege.

Alapelv:

**A snapshot az állapot. Az event log a történet.**

Az event log célja:

- UI animáció;
- játékosbarát magyarázat;
- debug;
- AI elemzés;
- replay előkészítés;
- audit;
- balanszvizsgálat;
- diagnostics kapcsolat.

---

### 36. Event log ajánlott fő mezői

Ajánlott mezők:

- `schema_version`
- `match_id`
- `events`
- `first_event_index`
- `last_event_index`
- `visibility_mode`
- `viewer_id`
- `diagnostics`
- `metadata`

Egy event ajánlott mezői:

- `event_id`
- `event_index`
- `event_type`
- `event_family`
- `event_layer`
- `match_id`
- `turn`
- `phase`
- `step`
- `actor_player_id`
- `controller_id`
- `owner_id`
- `source`
- `targets`
- `affected_objects`
- `payload`
- `visibility`
- `message_hu`
- `message_dev`
- `diagnostics`
- `caused_by`
- `parent_event_id`
- `correlation_id`
- `metadata`

MVP-ben nem mind kötelező.

---

### 37. Event layer értékek

Lehetséges event layer értékek:

- `gameplay`
- `frontend`
- `explanation`
- `debug`
- `audit`
- `balance`
- `system`

MVP-ben valószínűleg elég:

- `gameplay`
- `debug`
- `system`

Később bővíthető:

- `explanation`
- `audit`
- `balance`
- `frontend`

---

### 38. Event family jelöltek

Lehetséges event family értékek:

- `turn_flow`
- `card_movement`
- `card_played`
- `combat`
- `damage`
- `healing`
- `ward`
- `aura`
- `draw`
- `discard`
- `reaction`
- `ability`
- `token`
- `victory`
- `diagnostics`
- `system`

A `damage` family csak Entitás-sebzésre vagy szabályosan értelmezett sebzési eseményekre használható.

Nem használható Aeternal HP-sebzésre.

---

### 39. Aeternal / Pecsét események

Támogatandó event type jelöltek:

- `ward_broken`
- `ward_restored`
- `ward_break_prevented`
- `aeternal_unprotected`
- `direct_attack_victory`
- `player_defeated`

Kerülendő vagy tiltott event type jelöltek:

- `player_damage`
- `aeternal_damage`
- `heal_player`
- `heal_aeternal`
- `ward_damage`
- `seal_damage`

---

### 40. Event log és rejtett információ

Az event log visibility modellje kritikus.

Lehetséges megoldások:

1. Egy teljes belső event log, amelyből viewer szerint szűrt log készül.
2. Több külön event log nézőpontonként.
3. Debug log és player-visible log szétválasztása.

Ajánlott irány:

- belső teljes event log engedélyezett;
- player-visible event log szűrt;
- debug event log külön megjeleníthető;
- PvP előtt szigorú visibility audit kell.

---

### 41. Explanation log

Az explanation log célja játékosbarát magyarázat.

Lehetséges mezők:

- `message_hu`
- `message_dev`
- `explanation_key`
- `explanation_params`

Nyitott kérdések:

- backend generálja-e a magyar magyarázatot;
- frontend lookup generálja-e;
- minden eventhez kell-e magyarázat;
- csak komplex eventekhez kell-e.

---

### 42. Replay-kompatibilitás

A replay későbbi fázis.

Az event log szerkezeténél figyelembe kell venni, hogy később replayre alkalmas legyen.

Nyitott kérdések:

- MVP-ben kell-e teljes replay-kompatibilitás;
- kell-e action history;
- kell-e snapshot checkpoint;
- replayhez teljes vagy player-visible log kell.

---

## Diagnostics contract

### 43. Diagnostics célja

A diagnostics strukturált problémanyilvántartás.

Nem egyszerű hibalista.

Feladata:

- export hibák jelzése;
- lookup hibák jelzése;
- legacy aliasok jelzése;
- structured mező problémák jelzése;
- engine support problémák jelzése;
- hidden information problémák jelzése;
- action validation problémák jelzése;
- runtime warningok jelzése;
- audit note-ok kezelése;
- balance suspicion jelzése;
- smoke test és checkpoint problémák jelzése.

---

### 44. Diagnostics ajánlott fő mezői

Ajánlott diagnostics report mezők:

- `schema_version`
- `report_id`
- `report_type`
- `runtime_package_id`
- `match_id`
- `source_file`
- `generated_at`
- `summary`
- `entries`
- `blocking_errors`
- `warnings`
- `audit_notes`
- `metadata`

Egy diagnostics entry ajánlott mezői:

- `diagnostic_id`
- `category`
- `severity`
- `blocking`
- `code`
- `message_hu`
- `message_dev`
- `source_ref`
- `object_ref`
- `field`
- `value`
- `expected`
- `suggested_fix`
- `related_event_id`
- `related_action_id`
- `metadata`

---

### 45. Diagnostics category értékek

Lehetséges category értékek:

- `export_validation`
- `lookup`
- `legacy_alias`
- `structured`
- `engine`
- `rules`
- `card_data`
- `decklist`
- `runtime`
- `frontend_contract`
- `ai`
- `event_log`
- `snapshot`
- `action_validation`
- `action_execution`
- `hidden_information`
- `audit`
- `balance`
- `test`
- `system`

---

### 46. Diagnostics severity értékek

Lehetséges severity értékek:

- `critical`
- `error`
- `warning`
- `audit_note`
- `balance_suspicion`
- `info`
- `debug`

Fontos alapelv:

**A severity és a blocking külön mező legyen.**

Példa értelmezés:

- `warning` általában nem blokkoló;
- `error` lehet blokkoló vagy nem blokkoló;
- `critical` valószínűleg mindig blokkoló;
- `audit_note` emberi ellenőrzést jelez;
- `balance_suspicion` nem runtime hiba.

---

### 47. Blocking alapelv

A `blocking` mező külön jelzi, hogy a probléma megakadályozza-e a buildet, betöltést, actiont vagy runtime futást.

Példák blocking problémákra:

- érvénytelen schema;
- hiányzó kötelező mező;
- hidden information violation;
- aktív deckben unsupported kritikus effect;
- invalid action request;
- rossz match_id contractok között;
- snapshot_ref eltérés;
- olyan régi Aeternal/Pecsét HP-modell, amely runtime logikába kerülne.

Példák nem blokkoló problémákra:

- ismert Godot környezeti warning;
- nem használt kártyán unsupported feature;
- audit note;
- balance suspicion;
- nem kritikus legacy alias warning.

---

### 48. Diagnostics és visibility

Diagnostics üzenet nem szivárogtathat rejtett információt.

Ez különösen fontos:

- action rejected esetén;
- face-down Jel esetén;
- ellenfél kézlapjai esetén;
- fair AI snapshotnál;
- player-visible event lognál.

Lehetséges diagnostics visibility értékek:

- `debug_only`
- `developer_only`
- `player_visible`
- `ai_fair`
- `system_only`

---

### 49. LOOKUPS diagnostics

LOOKUPS és structured audit során különösen figyelni kell:

- unknown enum value;
- inactive value aktív kártyán;
- workflow-only value runtime mezőben;
- Label_HU és Value keveredése;
- legacy alias;
- dangerous alias;
- audit_required érték;
- canonical mismatch;
- semicolon delimiter problémák;
- többértékű mezők sorrendi kapcsolata.

Nyitott kérdések:

- mikor warning;
- mikor error;
- mikor blocking;
- mikor kell automatikus canonical normalizálás;
- mikor kell emberi kártyaaudit.

---

### 50. Engine support diagnostics

Engine support diagnostics jelzi, hogy az adott kártya vagy ability mennyire futtatható.

Lehetséges support status értékek:

- `supported`
- `partial`
- `unsupported`
- `not_checked`
- `fallback_required`
- `manual_review_required`

Nyitott kérdések:

- unsupported kártya blokkolja-e a package buildet;
- csak deckben szereplő unsupported kártya blokkoljon-e;
- card-local fallback warning vagy blocking legyen-e;
- AI-vs-AI tesztben kihagyható-e unsupported lap.

---

## Ability registry kapcsolódás

### 51. Ability registry szerepe

Az ability registry a runtime package és az ability module rendszer közötti contract jellegű réteg.

Célja:

- az ability module-ok azonosítása;
- support státusz jelzése;
- effect module-ok felsorolása;
- trigger / condition / target / cost / effect kapcsolódás előkészítése;
- engine support report támogatása;
- Godot loader és Python builder közös adatforrása.

Részletes ability module logika:

- `ABILITY_MODULE_SYSTEM.md`

---

### 52. Ability registry ajánlott mezői

Lehetséges mezők:

- `ability_id`
- `source_card_id`
- `module_id`
- `ability_type`
- `trigger`
- `conditions`
- `targets`
- `cost`
- `effects`
- `duration`
- `limits`
- `replacement`
- `prevention`
- `execution_mode`
- `support_status`
- `diagnostics`

MVP-ben valószínűleg egyszerűbb registry is elég.

---

### 53. Card-local fallback

Card-local fallback átmeneti lehetőség, nem hosszú távú alapműködés.

Alapelv:

- minden fallback legyen látható diagnostics-ban;
- minden fallback legyen migrációs jelölt;
- normál játékban fallback engedélyezése külön döntés;
- AI-vs-AI tesztben fallback engedélyezése külön döntés;
- Godot runtime-ban fallback engedélyezése külön döntés.

Nyitott kérdés:

- fallback mikor válik blocking problémává.

---

## Sample contracts

### 54. Sample contracts célja

A sample contractok nem végleges játékcontractok.

Céljuk:

- minimális tesztadat biztosítása;
- Godot loader próbája;
- debug nézetek próbája;
- contract consistency smoke testek;
- card reference resolution tesztelése;
- későbbi action request smoke teszt előkészítése.

Jelenlegi sample contract fájlok:

- `sample_snapshot.json`
- `sample_legal_actions.json`
- `sample_events.json`

---

### 55. Jelenlegi bizonyított sample contract réteg

A checkpointok alapján jelenleg működik:

- sample contracts loader;
- sample contracts smoke test;
- Snapshot viewer;
- Legal action debug panel;
- Event log debug view.

A sample contractok jelenleg statikusak.

Nem bizonyítják:

- valódi match state generálást;
- legal action számítást;
- action request feldolgozást;
- action-végrehajtást;
- event log valódi játékmenetből történő előállítását;
- ability executiont.

---

### 56. Contract consistency checks

A contractok között ellenőrizni kell:

- azonos `match_id`;
- legal actions `generated_for_snapshot_id` mezője a snapshotra mutat;
- events ugyanarra a match_id-re vonatkoznak;
- card reference-ek léteznek a runtime package card registryben;
- hiányzó card reference diagnostics entryt generál;
- schema verziók ismertek;
- blocking_errors száma helyes;
- warnings száma helyes;
- snapshot / legal action / event log egymással összhangban van.

---

### 57. Card reference resolution

A contractokban szereplő card reference-eket fel kell tudni oldani a runtime package card registryből.

Cél:

- `card_id` alapján kártyanév megjelenítése;
- kártyatípus megjelenítése;
- Birodalom megjelenítése;
- Klán megjelenítése;
- missing reference diagnostics;
- debug UI olvashatóság javítása.

Ez a következő prototípuslépések egyik fontos célja.

---

## MVP contract scope

### 58. MVP contract scope

Az első valóban használható contract MVP tartalmazza:

- runtime package load;
- debug snapshot;
- player-visible snapshot kezdemény;
- legal action lista statikus vagy minimálisan számolt formában;
- action request minta;
- action response minta;
- event log minta;
- diagnostics minta;
- card reference resolution;
- smoke testek.

Nem tartalmazza még:

- teljes szabálymotor;
- teljes ability execution;
- AI;
- PvP;
- replay;
- teljes digitális UI;
- teljes AETERNA kártyaadatbázis futtatása.

---

### 59. Tiltott vagy kerülendő régi modellek

A contractokban kerülni kell a régi, hibás vagy félrevezető Aeternal/Pecsét HP-modellt.

Kerülendő fogalmak:

- `player_damage`
- `aeternal_damage`
- `heal_player`
- `heal_aeternal`
- `ward_hp`
- `seal_hp`
- `seal_damage`
- `ward_damage`

Támogatandó modern fogalmak:

- `ward_break`
- `ward_restore`
- `ward_break_prevent`
- `aeternal_unprotected`
- `direct_attack_victory`
- `player_defeated`

---

### 60. Nyitott kérdések

A contract-réteg részletes nyitott kérdései a központi kérdéslistában szerepelnek:

- `OPEN_QUESTIONS.md`

Kiemelt témák:

- snapshot típusok;
- visibility modell;
- Pecsét snapshotmodell;
- Ősforrás láthatóság;
- reaction window;
- legal action disabled reason;
- action request stale snapshot;
- partial resolution;
- event log részletesség;
- diagnostics blocking szabályok;
- engine support státusz;
- ability registry és fallback;
- AI fair/debug contractok.

---

### 61. Következő kapcsolódó dokumentumok

A contract-specifikáció után részletesítendő fő dokumentumok:

- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `ABILITY_MODULE_SYSTEM.md`
- `PROTOTYPE_PLANS.md`
- később `README.md`

A contract-specifikációt később frissíteni kell, ha:

- elkészül az action request smoke test;
- elkészül a card reference resolution;
- elkészül a unified dashboard;
- elkészül az első rules service prototípus;
- pontosabbá válik a runtime package schema;
- pontosabbá válik az ability module rendszer.