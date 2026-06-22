# AETERNA - Godot Backend Facade Elokeszites

Ez a dokumentum a jelenlegi Python motor es egy kesobbi Godot frontend kozotti
minimalis backend-hatar elokesziteset rogziti.

Celja nem egy teljes API vagy frontend terv leirasa, hanem egy kis-kockazatu,
gyakorlati kovetkezo technikai irany kijelolese.

Kapcsolodo, aktualis allapotot rogzitO szerzodes:
- `BACKEND_FRONTEND_MINIMAL_CONTRACT.md`

## 1. Kiindulasi helyzet

A jelenlegi hivatalos futasi ut:

1. `main.py`
2. `simulation/config.py`
3. `engine/logging_utils.py`
4. `simulation/runner.py`
5. `data/loader.py`
6. `engine/game.py`

A jelenlegi motor erossege:
- van mukodo meccsfuttatasi mag
- van shared action/helper reteg (`engine/actions.py`)
- van trigger-dispatch reteg (`engine/triggers.py`)
- van card resolver / priority handler reteg

A jelenlegi motor fo hianya Godot-szempontbol:
- nincs kulon backend-facade reteg
- nincs konnyen exportalhato allapotkep
- nincs tiszta legal-actions szerzodes
- a jatekos-akcio boundary jelenleg foleg random AI-folyamatba van agyazva

## 2. Minimalis backend-interfesz muveletek

Egy kesobbi Godot kliens fele a minimalis kulso muveletek:

1. `create_match(...)`
   - uj jatek inditasa konfiguraciobol

2. `get_snapshot(match_id)`
   - a jelenlegi jatekallapot lekerese frontend-barat formaban

3. `get_legal_actions(match_id, player_id)`
   - a jatekos szamara most vegrehajthato akciok lekerese

4. `apply_action(match_id, player_id, action_request)`
   - egy jatekos-akcio vegrehajtasa

5. `run_ai_step(match_id, player_id=None)`
   - egy AI dontesi lepes vagy teljes aktiv fazis futtatasa

6. `get_event_log(match_id, since_seq=None)`
   - uj esemenyek, log-elemek vagy state-deltak lekerese

7. `get_match_result(match_id)`
   - meccsvegi allapot, gyoztes, gyozelmi ok, vegso metrikak

## 3. Jelenlegi modulkapcsolatok

### Mar most jol hasznalhato

- `simulation/config.py`
  - jo konfiguracios bemenet
  - alkalmas facade-szintu match letrehozasra

- `engine/game.py`
  - itt van a valodi meccsallapot es korfuttatas
  - `AeternaSzimulacio` jo kiindulasi belso match-objektum

- `engine/player.py`
  - a jatekos-zonak, kez, pakli, pecsetek, forrasok itt elnek

- `engine/actions.py`
  - a legtobb allapotmodosito muvelet mar shared helperen megy
  - ez jo alap kesobbi action execution reteghez

- `engine/triggers.py`
  - egyszeru, kozponti dispatch pont
  - jo alap kesobbi facade-esemeny tovabbitashoz

- `cards/resolver.py`
  - egysegesebb handler-feloldasi pont az on-play/trap/burst kategoriakra

### Reszben hasznalhato, de nem eleg tiszta meg

- `simulation/runner.py`
  - jo orchestration reteg AI-vs-AI futtatashoz
  - de Godot backendnek tul magas szintu es tul log-orientalt

- `engine/targeting.py`
  - van benne shared validation/allapot
  - de nem teljes, frontend-barat targeting szerzodes

- `cards/priority_handlers.py`
  - mukodo runtime
  - de erosen card-local es nev-alapu, ezert nem lehet facade API-kent kozvetlenul kitenni

## 4. Javasolt minimalis facade modul

Javasolt uj modul:

- `backend/facade.py`

Masodik, opcionális helper modul:

- `backend/snapshot.py`

### A facade publikus metodusai

1. `create_match(config: dict | SimulationConfig) -> str`
2. `get_snapshot(match_id: str) -> dict`
3. `get_legal_actions(match_id: str, player_id: str) -> list[dict]`
4. `apply_action(match_id: str, player_id: str, action: dict) -> dict`
5. `run_ai_step(match_id: str, player_id: str | None = None) -> dict`
6. `get_event_log(match_id: str, since_seq: int | None = None) -> list[dict]`
7. `get_match_result(match_id: str) -> dict | None`
8. `drop_match(match_id: str) -> bool`

### Mi menne bele

- match-peldanyok regisztralasa
- `SimulationConfig` es `AeternaSzimulacio` osszekotese
- stabil kulso muveleti felulet
- snapshot-export hivasok
- legal-action helper hivasok
- event/log buffer kiadasa

### Mi nem menne bele

- card effect implementacio
- trigger-rendszer nagy ujratervezese
- teljes frontend-protokoll
- HTTP vagy socket szerver
- Godot-specifikus UI logika

## 5. Legnagyobb akadalyozo tenyezok

1. Nincs tiszta snapshot reteg
   - a meccsallapot ma a `AeternaSzimulacio` + `Jatekos` + board objectekben el
   - nincs egyetlen stabil exportfuggveny

2. Nincs kulon legal-actions reteg
   - a legfontosabb akciodonto logika ma a random play/combat folyamokba van agyazva
   - kulso kliensnek nem adhato vissza konnyen

3. Az action boundary nem eleg tiszta
   - a `kor_futtatasa()` teljes aktiv turn loopot visz
   - frontend szempontbol kisebb, explicit lepesek kellenek

4. A card-local reteg eros
   - `cards/priority_handlers.py` sok valos viselkedest hordoz
   - ez jo runtime-nak, de nem jo kulso API-hatarnak

5. A logger jelenleg inkabb emberi olvasasra optimalizalt
   - hasznos diagnosztikai reteg
   - de egy frontendnek jobb lenne egy kulon, gepileg fogyaszthato event buffer

## 6. Legjobb kovetkezo technikai lepes

Legnagyobb hasznu, meg mindig kis-kozepes kockazatu kovetkezo lepes:

- `backend/snapshot.py` letrehozasa

Minimum tartalom:
- `export_card_ref(card) -> dict`
- `export_unit_state(unit) -> dict`
- `export_player_state(player) -> dict`
- `export_match_snapshot(game) -> dict`

Miért ez a legjobb elso lepes:
- nem nyit uj mechanikai frontot
- nem kell hozza a teljes action-rendszert ujratervezni
- azonnal segiti a Godot-backend gondolkodast
- tesztelheto es izolalhato
- kesobb erre epulhet a facade, a legal-actions helper es az event/delta reteg

## 7. Facade utani ajanlott sorrend

1. snapshot export helper
2. minimalis facade modul match-regiszterrel
3. legal actions helper a leggyakoribb play/summon/trap aktivalasi esetekre
4. action request schema
5. kulon gepi event buffer a logger melle

## 8. Döntesi elv

A kovetkezo korben sem teljes API-t erdemes epiteni, hanem:

- eloszor stabil snapshot
- utana vekony facade
- csak ezutan legal actions es action execution boundary

Ez illeszkedik a projekt jelenlegi strategiajahoz:

- felterkepezes
- stabilizacio
- cleanup
- celzott refaktor

## 9. Elso kodkor eredmenye

Az elso tenyleges backend-elokeszito kodkorben letrejott a minimalis snapshot-export reteg:

- `backend/snapshot.py`
- `backend/__init__.py`

Az elso exportfuggvenyek:

- `export_card_ref(card)`
- `export_unit_state(unit)`
- `export_player_state(player)`
- `export_match_snapshot(game)`

Ez meg nem facade, nem legal-actions reteg es nem action API, de mar ad egy stabil,
geppel fogyaszthato allapotkepet, amire a kovetkezo korben lehet facade-ot vagy state export
helper-bovitest epiteni.

## 10. Masodik kodkor eredmenye

A kovetkezo kis-kockazatu backend-elokeszito lepesben letrejott egy minimalis facade reteg:

- `backend/facade.py`

A jelenlegi publikus muveletei:

- `create_match(config)`
- `get_snapshot(match_id)`
- `get_match_result(match_id)`
- `drop_match(match_id)`
- `list_matches()`

Ez a facade meg nem legal-actions rendszer es nem action API, de mar ad egy stabil,
egyszeru backend-belepesi pontot a jelenlegi motor fole, a snapshot reteg ujrafelhasznalasaval.

## 11. Harmadik kodkor eredmenye

Az elso, szuk legal-actions helper is letrejott:

- `backend/legal_actions.py`

Az elso verzio szandekosan csak a legegyszerubb akciokat fedi le:

- `end_turn`
- egyszeru kezbol kijatszhato entitas-lerakasi lehetosegek
- egyszeru trap / jel lerakasi lehetosegek

Kimondottan nem resze meg:

- spell legal-actions
- teljes targeting rendszer
- action execution boundary
- request schema

Ha a facade-bol kerjuk, az uj belepesi pont:

- `get_legal_actions(match_id, player_id)`

## 13. Felvezerelt CLI es minimalis AI-step allapot

A kulon, facade-alapu CLI prototipus mar letrejott:

- `simulation/interactive_match_cli.py`
- kulon inditoval: `run_interactive_match_cli.py`

Ehhez a facade most mar ad egy szuk, technikai `run_ai_step(match_id, player_id=None)` muveletet is.

Ez jelenleg nem teljes AI-API es nem teljes korfuttato frontend-hatar, hanem:
- egy egyszeru automatikus lepes az aktualis aktiv jatekosnak
- a mar tamogatott actionokbol valaszt:
  - `play_entity`
  - `play_trap`
  - `end_turn`

Ez eleg arra, hogy a kulon interactive CLI mod egy fokkal kozelebb keruljon a tenyleges
ember-vs-AI technikai mintahoz, mikozben a regi tesztlauncher tovabbra is kulon marad.

## 12. Negyedik kodkor eredmenye

Az elso explicit backend-kompatibilis state-context is bekerult:

- aktiv jatekos
- fo fazis
- meccs lezart allapota

Ez most nem teljes phase-engine, hanem minimalis, stabil state-jelzes a jatekobjektumon:

- `state.active_player`
- `state.phase`
- `state.match_finished`
- `state.winner`
- `state.victory_reason`

Ennek hatasara a snapshot, a facade eredmeny-lekerdezese es a legal-actions helper
mar kevesebbet kovetkeztet implicit allapotbol, es tisztabb backend-hatart ad a
kovetkezo action-boundary korhoz.

## 13. Otodik kodkor eredmenye

Az elso minimalis action request / validation reteg is letrejott:

- `backend/action_request.py`

Az elso tamogatott action tipusk:

- `end_turn`
- `play_entity`
- `play_trap`

Az uj alapmuveletek:

- `normalize_action_request(action_request)`
- `validate_action_request(game, player, action_request)`
- `action_request_to_key(action_request)`

Ha a facade-bol kerjuk, az uj belepesi pont:

- `validate_action(match_id, player_id, action_request)`

Ez meg nem action execution, csak stabil request-forma es legal-actions alapu validacio.

## 14. Hatodik kodkor eredmenye

Az elso minimalis `apply_action` boundary is bekerult a facade-be:

- `apply_action(match_id, player_id, action_request)`

Az elso tenylegesen vegrehajthato action tipus:

- `end_turn`

Jelenlegi szandekos korlatozas:

- `play_entity` meg validalhato, de ebben a korben meg nem vegrehajthato
- `play_trap` nincs bekotve vegrehajtasra

Az `end_turn` jelenlegi mukodese:

- a valid request utan a meglEvo `kor_futtatasa()` utvonalra tamaszkodik
- vagyis a jelenlegi motorban a kovetkezo stabil backend-dontesi pontig lepteti a meccset

Ez meg nem teljes action pipeline, de mar az elso valodi backend-vegrehajtasi kapu.

## 15. Readiness audit - rovid dontesi kovetkeztetes

A jelenlegi backend-vaz mar eleg eros ahhoz, hogy ne ujabb altalanos backend-reteget epitsunk eloszor, hanem a legnagyobb frontend-hasznot ado kovetkezo vegrehajtasi lepest valasszuk ki.

A rovid readiness audit kovetkeztetese:

- a snapshot, facade, legal-actions, state-context es action-request reteg mar hasznalhato alapot ad
- a fo hiany mar nem ujabb allapot-lekerdezes, hanem az elso valodi board-akcio vegrehajtasa
- emiatt a kovetkezo egyetlen legjobb technikai lepes a `play_entity` execution-boundary bekotese

Ez illeszkedik a jelenlegi strategiahoz:
- nincs nagy refaktor
- nincs uj mechanikai front
- a mar meglevo backend-lanc kapja meg a legnagyobb hasznu kovetkezo elemet

## 16. Hetedik kodkor eredmenye

Az elso valodi board-action execution boundary is bekerult:

- `play_entity` az `apply_action(...)` alatt

Jelenlegi szandekos korlatozas:

- csak egyszeru kezbol kijatszhato entitas
- csak egyertelmu `card_name` + `zone` + `lane`
- csak a meglevo shared summon helper utakon
- nincs trap execution
- nincs spell execution
- nincs targeting front

Ez azt jelenti, hogy a backend mar nem csak allapotot ad es `end_turn`-t hajt vegre,
hanem az elso valodi, nem-trivialis jatekos-akciot is vegre tudja hajtani.

## 17. Nyolcadik kodkor eredmenye

Az `apply_action(...)` valaszszerzodese tisztabb es egysegesebb lett.

A stabil kulso valaszforma:

- `ok`
- `reason`
- `action`
- `result`
- `snapshot`

Az egysegesebb `result` blokk most ezekre epul:

- `executed_action_type`
- `status`
- `card_name`
- `zone`
- `lane`
- `winner`
- `details`

Ez nem uj action tipus, hanem a mar meglevo backend-vegrehajtasi kapu frontend-baratabb
stabilizalasa a kesobbi Godot-koteshez.

## 18. Kilencedik kodkor eredmenye

Az `apply_action(...)` most mar egy rovid, gepileg fogyaszthato `events` listat is ad.

Ez a reteg szandekosan nagyon szuk:

- nem belso trigger-export
- nem teljes event bus
- nem replay rendszer

Jelenlegi celja csak annyi, hogy a frontendnek ne mindig a teljes snapshotbol kelljen
kovetkeztetnie arra, mi tortent kozvetlenul az akcio utan.

Az elso tamogatott esemenytipusok:

- `action_executed`
- `turn_advanced`
- `entity_played`
- `board_changed`
- `winner_declared`

## 19. Tizedik kodkor eredmenye

Az action-valasz `events` listaja most mar per-match pufferbe is bekerul a facade retegen belul.

Uj, nagyon szuk lekerdezesi felulet:

- `get_event_log(match_id, since_index=None)`

Ez jelenleg:
- nem teljes event bus
- nem replay rendszer
- nem logger-integracio

Csak arra jo, hogy a frontend a mar vegrehajtott actionok rovid backend-esemenyeit
kulon is le tudja kerni, ne csak az adott action-valaszbol.

## 20. Tizenegyedik kodkor eredmenye

A minimalis `play_trap` execution-boundary is bekerult:

- `apply_action(...)` most mar a legegyszerubb `play_trap` actiont is vegre tudja hajtani

Szandekosan szuk korlatokkal:
- csak kezben levo `Jel` lap
- csak egyertelmu `zone="zenit"` + `lane`
- csak a jelenlegi egyszeru trap-limit modell szerint
- nincs uj trap-framework
- nincs targeting vagy spell front

A backend valasz szerzodese es az `events` lista ehhez is konzisztensen bovult:
- `action_executed`
- `trap_played`
- `board_changed`
