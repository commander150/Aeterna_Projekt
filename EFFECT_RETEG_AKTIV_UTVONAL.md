# Aeterna – Effect Réteg Aktív Útvonal

Ez a dokumentum a jelenlegi, ténylegesen futó effect-kezelési útvonalat rögzíti.
Nem refaktor-terv, hanem a mostani hivatalos runtime út rövid leírása.

## Hivatalos Runtime Belépés

Az effect-kezelés aktív runtime belépési pontja:

- `engine/game.py`

A meccs közben innen indulnak az effect-hívások:

- `EffectEngine.trigger_on_play(...)`
- `EffectEngine.trigger_on_trap(...)`
- `EffectEngine.trigger_on_burst(...)`
- `EffectEngine.trigger_on_death(...)`
- `resolve_card_handler(...)`
- `resolve_spell_cast_trap(...)`
- `resolve_lethal_trap(...)`

## Aktív Effect Lánc

### 1. Kijátszás / trigger-indítás

`engine/game.py`

- kijátszáskor meghívja a `trigger_engine.dispatch("on_play", ...)` eseményt
- majd meghívja az `EffectEngine.trigger_on_play(...)` útvonalat

### 2. Diagnostics wrapper bekötés

`simulation/runner.py` explicit módon meghívja:

- `engine.effect_diagnostics_v2.install_effect_diagnostics()`

Ez a belépési pont futáskor beregisztrálja a diagnostics réteget az
`EffectEngine` hivatalos trigger-adapter pontjaira:

- `on_play`
- `trap`
- `burst`
- `death`

Így a hivatalos runtime effect-hívás ténylegesen:

`game.py -> EffectEngine.trigger_* -> EffectEngine trigger adapter -> effect_diagnostics_v2 ->`

1. structured próbálkozás (`engine.structured_effects`)
2. név-alapú custom handler (`cards.resolver` -> `cards.priority_handlers`)
3. text fallback / common resolver (`engine.effects`)

## Rétegek Szerepe

### `engine/effects.py`

- hivatalos effect core
- tartalmazza a közös effect helper logikát
- tartalmazza a text fallback / common resolver viselkedést
- tartalmazza a sebzés, pusztítás, zónakezelés több központi helperét

### `engine/structured_effects.py`

- structured metadata alapú effect próbálkozás
- a diagnostics wrapper innen próbál először feloldani
- részben az `EffectEngine` helperjeire támaszkodik

### `cards/resolver.py`

- név-alapú dispatch réteg
- kategóriánként választ handlert (`on_play`, `trap`, `summon_trap`, `burst`)
- trigger-regisztrációkat is tartalmaz

### `cards/priority_handlers.py`

- konkrét, lapnévhez kötött egyedi handlerek
- részben közvetlenül használja az `EffectEngine` helperjeit

### `engine/effect_diagnostics_v2.py`

- aktív runtime hook/adapterszolgáltató
- nem csak riportol, hanem ténylegesen ő vezeti a structured -> custom -> fallback
  feloldási sorrendet
- explicit install-hívással aktiválódik, és az `EffectEngine` adapter API-ját
  használja, ezért a függés most már látható és követhető

## Mi Számít Hivatalosnak Most

- effect core: `engine.effects.EffectEngine`
- structured réteg: `engine.structured_effects`
- custom dispatch: `cards.resolver`
- custom handlerek: `cards.priority_handlers`
- aktív runtime wrapper: `engine.effect_diagnostics_v2`

## Mi Nem Hivatalos Külön Effect Út

- `engine/effects_core.py` már nincs használatban, kivezetett wrapper volt

## Fő Kockázatok

- `engine.effect_diagnostics_v2.py` továbbra is trigger-wrapper réteg, de már
  nem metódusfelülírással, hanem az `EffectEngine` explicit adapter API-ján át
  kapcsolódik
- `engine.structured_effects.py` és `cards/resolver.py` egymás mellett élő
  feloldási réteg, ezért későbbi refaktornál könnyű párhuzamos logikát bent
  hagyni
- `engine.effects.py` továbbra is nagy, és egyszerre core helper + fallback
  effektmotor
