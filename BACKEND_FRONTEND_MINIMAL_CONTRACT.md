# AETERNA - Backend Frontend Minimal Contract

Ez a dokumentum a jelenlegi, minimalis backend-feluletet rogzitI ugy, ahogy azt
egy kesobbi Godot vagy mas frontend fogyaszthatja.

Nem teljes API-terv, nem vegleges protocol, es nem gameplay-specifikacio.
A celja csak annyi, hogy a mar meglevo backend-vazhoz legyen egy rovid,
egyertelmu, frontend-oldalrol is hasznalhato szerzodes.

## 1. Rogzites celja

A jelenlegi minimalis backend-reteg arra valo, hogy:
- uj meccset inditson
- gepileg fogyaszthato allapotkepet adjon
- visszaadja a legegyszerubb legal actionoket
- validalja az egyszeru action requesteket
- nehany actiont tenylegesen vegre is hajtson
- rovid action-utani esemenyeket es per-match event logot adjon

Ez mar eleg egy kezdeti, egyszeru frontend-prototipushoz.

## 2. Jelenlegi publikus facade muveletek

### `create_match(config=None) -> match_id`
- uj meccset hoz letre
- `SimulationConfig`, `dict` vagy `None` bemenetet fogad
- a meccset facade-szintu registryben tarolja

### `get_snapshot(match_id) -> dict | None`
- visszaadja a teljes jelenlegi meccs-snapshotot
- ismeretlen match eseten `None`

### `get_match_result(match_id) -> dict | None`
- rovid meccsallapotot ad:
  - `finished`
  - `winner`
  - `victory_reason`
  - `turn`
  - `active_player`
  - `phase`

### `drop_match(match_id) -> bool`
- eltavolitja a meccset a registrybol
- siker eseten `True`
- ismeretlen match eseten `False`

### `list_matches() -> list[dict]`
- rovid registry-listat ad az aktiv meccsekrol
- elsosorban fejlesztoi / prototipus celra hasznos

### `get_legal_actions(match_id, player_id) -> list[dict] | None`
- visszaadja az adott jatekos pillanatnyi legal actionjeit
- ismeretlen match vagy player eseten `None`

### `validate_action(match_id, player_id, action_request) -> dict`
- nem hajt vegre semmit
- csak a request szerkezeti es legal-actions alapu ervenyesseget ellenorzi

### `apply_action(match_id, player_id, action_request) -> dict`
- a jelenleg tamogatott actionok kozul nehanyat tenylegesen vegrehajt
- a valaszban visszaad:
  - action eredmenyt
  - rovid event listat
  - friss snapshotot

### `get_event_log(match_id, since_index=None) -> dict`
- visszaadja a meccshez tartozo facade-szintu event puffert
- tud teljes logot vagy adott indextol uj esemenyeket adni

## 3. Jelenlegi tamogatott action tipusk

### Legal-action szinten
A legal-actions helper jelenleg ismeri:
- `end_turn`
- `play_entity`
- `play_trap`

### Tenyleges execution szinten
Az `apply_action(...)` jelenleg tenylegesen vegre tudja hajtani:
- `end_turn`
- `play_entity`
- `play_trap`

Szandekos korlatozas:
- nincs spell execution
- nincs targeting execution
- nincs combat action execution
- nincs teljes trap aktivalasi rendszer

## 4. Snapshot szerzodes roviden

A snapshot a `backend/snapshot.py` exportjaira epul.

Fo szintu mezok:
- `turn`
- `active_player`
- `phase`
- `match_finished`
- `winner`
- `victory_reason`
- `p1`
- `p2`
- `log_metrics`

### Fontos state-context
A backend most mar explicit modon rogzitI:
- ki az aktiv jatekos
- milyen fo fazisban van a meccs
- lezarult-e a meccs

### Player snapshot fo elemei
Jelenleg tipikusan:
- `name`
- `realm`
- `deck_size`
- `hand_size`
- `graveyard_size`
- `seal_count`
- `source_count`
- `overflow_defeat`
- `hand_cards`
- `source_cards`
- `horizont`
- `zenit`

### Card ref fo elemei
- `name`
- `card_type`
- `realm`
- `clan`
- `magnitude`
- `aura_cost`
- tipusflag-ek:
  - `is_entity`
  - `is_trap`
  - `is_field`
  - `is_spell`

## 5. Action request szerzodes roviden

A minimalis request forma:

```python
{
    "action_type": ...,
    "player": ...,
    "card_name": ...,
    "zone": ...,
    "lane": ...,
}
```

### Jelenlegi tamogatott request-tipusok
- `end_turn`
- `play_entity`
- `play_trap`

### Mezoelvarasok
`end_turn`
- kotelezo:
  - `action_type`
  - `player`

`play_entity`
- kotelezo:
  - `action_type`
  - `player`
  - `card_name`
  - `zone`
  - `lane`

`play_trap`
- kotelezo:
  - `action_type`
  - `player`
  - `card_name`
  - `zone`
  - `lane`

### Validacios elv
A backend:
- normalizalja a requestet
- ellenorzi a kotelezo mezoket
- ellenorzi a player-egyezest
- ellenorzi, hogy a request benne van-e az aktualis legal action listaban

## 6. Action response szerzodes roviden

Az `apply_action(...)` kulso valaszforma:

```python
{
    "ok": bool,
    "reason": str | None,
    "action": dict | None,
    "result": dict | None,
    "events": list[dict],
    "snapshot": dict | None,
}
```

### `result` blokk jelenlegi formaja

```python
{
    "executed_action_type": str,
    "status": str,
    "card_name": str | None,
    "zone": str | None,
    "lane": int | None,
    "winner": str | None,
    "details": dict,
}
```

### Tipikus `reason` ertekek
- `unknown_match_id`
- `unknown_player_id`
- `unsupported_action_type`
- `player_mismatch`
- `missing_required_fields:...`
- `not_in_legal_actions`
- `action_type_not_executable_yet`

## 7. Event log mukodes roviden

A facade minden matchhez tart egy egyszeru event puffert.

### Alapelv
- az `apply_action(...)` valaszaban benne marad az adott action rovid `events` listaja
- ugyanezek az esemenyek bekerulnek a meccshez tartozo per-match event logba is

### `get_event_log(match_id, since_index=None)`
Visszateres:

```python
{
    "events": [...],
    "next_index": int,
    "reason": str | None,
}
```

### `since_index`
- ha nincs megadva, a teljes log jon vissza
- ha meg van adva, onnan jonnek az uj esemenyek

### `next_index`
- a frontend ezt el tudja menteni
- a kovetkezo pollnal `since_index`-kent vissza tudja adni

### Event objektum jelenlegi formaja

```python
{
    "type": str,
    "player": str | None,
    "card_name": str | None,
    "zone": str | None,
    "lane": int | None,
    "details": dict,
    "index": int,  # csak a per-match logban
}
```

Jelenlegi facade-szintu esemenytipusok:
- `action_executed`
- `turn_advanced`
- `entity_played`
- `trap_played`
- `board_changed`
- `winner_declared`

## 8. Jelenlegi korlatok

### Ami meg nincs
- spell execution
- targeting execution
- combat action execution
- teljes legal-actions paletta
- teljes event bus vagy replay rendszer
- delta-szamitott state export

### Ami most csak reszleges
- a `phase` csak fo fazisszintu jelzes
- a trap execution csak egyszeru lerakast fed le, nem aktivalasi rendszert
- az action result `details` blokk meg action-tipusonkent specializalodik

### Kovetkezo lehetseges iranyok
A legkezenfekvobb kovetkezo, meg mindig kis-kockazatu iranyok:
- uj action-tipus nagyon szuk execution-boundaryval
- action/result/events szerzodes tovabbi finomitasa
- kesobbi frontend polling mintahoz meg egy kis facade-dokumentacio
