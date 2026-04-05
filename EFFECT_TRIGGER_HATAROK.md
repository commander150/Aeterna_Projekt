# Aeterna – Effect Trigger Határok

Ez a rövid dokumentum a trigger-belépési pontok és a diagnostics réteg közti
szolgáltatási határt rögzíti.

## Hivatalos Trigger Belépési Pontok

Az aktív runtime továbbra is ezeket hívja:

- `EffectEngine.trigger_on_play(...)`
- `EffectEngine.trigger_on_trap(...)`
- `EffectEngine.trigger_on_burst(...)`
- `EffectEngine.trigger_on_death(...)`

## Új Explicit Határ

Az `EffectEngine` most hivatalos adapter API-t biztosít:

- `install_trigger_adapter(trigger_name, handler)`
- `clear_trigger_adapter(trigger_name)`
- `get_trigger_adapter(trigger_name)`
- `has_trigger_adapter(trigger_name)`

Támogatott adapter-nevek a jelenlegi diagnostics bekötéshez:

- `on_play`
- `trap`
- `burst`
- `death`

## Mi Változott

Korábban az `engine.effect_diagnostics_v2` közvetlenül átírta az
`EffectEngine.trigger_*` metódusokat.

Most:

1. a runtime továbbra is az `EffectEngine.trigger_*` belépési pontokat hívja
2. ezek a metódusok először megnézik, van-e regisztrált adapter
3. ha van, az adapter fut le
4. ha nincs, a default effect-logika fut le

## Mi Nem Változott

- a trigger-metódusok publikus neve
- a runtime hívási út a `game.py` felől
- a diagnostics wrapper tartalmi viselkedése
- a structured -> custom -> fallback sorrend

## Mi Maradt Későbbre

- az `engine.effects.py` belső duplikált trigger-definícióinak tisztítása
- az adapterek esetleges egységes pipeline-objektumba emelése
