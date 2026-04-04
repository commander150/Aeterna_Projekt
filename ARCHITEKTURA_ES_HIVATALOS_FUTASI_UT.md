# Aeterna – Architektúra és Hivatalos Futási Út

Ez a dokumentum a jelenlegi, ténylegesen használt futási útvonalat rögzíti.
A célja nem az ideális jövőbeli szerkezet leírása, hanem a mostani hivatalos
motorút egyértelmű kijelölése.

## Entrypoint

- `main.py`

## Aktív Futási Lánc

1. `main.py`
2. `simulation/config.py`
3. `engine/logging_utils.py`
4. `simulation/runner.py`
5. `engine/effect_diagnostics_v2.py`
6. `data/loader.py`
7. `engine/game.py`

Innen a meccsfuttatás közben jellemzően ezek a core modulok kapcsolódnak be:

- `engine/player.py`
- `engine/card.py`
- `engine/actions.py`
- `engine/board_utils.py`
- `engine/triggers.py`
- `engine/keyword_engine.py`
- `engine/effects.py`
- `engine/structured_effects.py`
- `engine/targeting.py`
- `cards/resolver.py`
- `cards/priority_handlers.py`
- `stats/analyzer.py`
- `utils/logger.py`
- `utils/text.py`

## Core Modulok

Az alábbi modulok jelenleg a hivatalos, aktív motor részei:

- `main.py`
- `simulation/runner.py`
- `simulation/config.py`
- `data/loader.py`
- `engine/game.py`
- `engine/player.py`
- `engine/card.py`
- `engine/actions.py`
- `engine/board_utils.py`
- `engine/effects.py`
- `engine/structured_effects.py`
- `engine/effect_diagnostics_v2.py`
- `engine/triggers.py`
- `engine/targeting.py`
- `engine/keyword_engine.py`
- `engine/keyword_registry.py`
- `engine/config.py`
- `cards/resolver.py`
- `cards/priority_handlers.py`
- `stats/analyzer.py`
- `utils/logger.py`
- `utils/text.py`

## Wrapper / Átmeneti Modulok

Ezek a fájlok jelenleg inkább adapterek, re-exportok vagy előkészített
modulhelyek, nem a fő viselkedés elsődleges hordozói:

- `engine/game_state.py`
- `engine/phases.py`
- `engine/combat.py`
- `engine/effects_core.py`
- `engine/keywords_core.py`
- `engine/effects_expansions.py`
- `expansions/` alatti placeholder modulok

## Wrapper Státuszdöntések

Az alábbi státuszok a jelenlegi, működő architektúrához igazodnak.

- `engine/effects_core.py`
  - státusz: wrapper marad átmenetileg
  - indok: tiszta re-export az `engine.effects` fölött, nem zavarja a runtime-ot,
    de önálló viselkedése nincs

- `engine/keywords_core.py`
  - státusz: wrapper marad átmenetileg
  - indok: tiszta re-export az `engine.keyword_engine` fölött, biztonságos, de
    később kivezethető

- `engine/game_state.py`
  - státusz: wrapper marad átmenetileg
  - indok: nagyon vékony állapot-adapter, jelenleg nem zavarja a futási utat,
    de nem tekinthető teljes moduláris szeletnek

- `engine/phases.py`
  - státusz: wrapper kivezethető később
  - indok: jelenleg egyetlen delegáló metódust tartalmaz a `game.py` felé

- `engine/combat.py`
  - státusz: wrapper kivezethető később
  - indok: jelenleg egyetlen delegáló metódust tartalmaz a `game.py` felé

- `engine/keywords.py`
  - státusz: wrapper marad átmenetileg
  - indok: tiszta kompatibilitási re-export a hivatalos
    `engine.keyword_engine.KeywordEngine` fölött, benne maradt legacy logika
    nélkül

- `engine/keyword_engine.py`
  - státusz: core és marad
  - indok: ez a hivatalos, közvetlen runtime keyword-útvonal

- `tests/test_keywords.py`
  - státusz: tesztoldali igazítást igényelt
  - indok: megszűnt `engine.keyword_rules` importot használt, ezért a tesztet a
    tényleges aktív `engine.keyword_engine` útvonalhoz kellett igazítani

## Jelenlegi Fő Kockázatok

- `engine/effects.py` még mindig nagy és több korszak logikáját hordozza.
- `engine/effect_diagnostics_v2.py` side-effect importtal aktiválódik a
  runnerből, ami rejtett függést jelent.
- A hivatalos keyword-útvonal most: `engine.keyword_engine.KeywordEngine`.
  Az `engine.keywords` csak kompatibilitási wrapper.
- A `game_state/phases/combat` szétválasztás jelenleg még vékony wrapper-szintű,
  nem teljes moduláris szeletelés.
- A `cards/resolver.py` + `cards/priority_handlers.py` útvonal működőképes, de
  erősen név-alapú, ezért későbbi tisztításnál figyelni kell a párhuzamos
  effect-megoldásokra.

## Cleanup Megjegyzés

Ebben a cleanup körben csak a biztosan generált vagy már hiányzó legacy elemek
lettek kezelve. A core motor viselkedését ez a dokumentáció nem változtatja meg.
