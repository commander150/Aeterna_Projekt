# Canonical Runtime Batch 1 Summary

## Implemented

- Canonical shared target selector path added in `engine/actions.py` for:
  - `enemy_horizont_entity`
  - `own_horizont_entity`
  - `enemy_zenit_entity`
  - `other_own_entity`
  - `opposing_entity`
- Structured effect resolution now reuses canonical selectors in `engine/structured_effects.py` for:
  - `damage`
  - `destroy`
  - `exhaust`
  - `ready`
  - `grant_keyword`
  - `return_to_hand`
  - `move_horizont`
  - `move_zenit`
- Shared effect primitives strengthened in `engine/actions.py`:
  - `grant_keyword`
  - `ready_unit`
  - `move_target_to_horizont`
  - existing `return_target_to_hand` and `move_target_to_zenit` now participate in canonical paths
- Canonical runtime trigger adapters added in `engine/game.py`:
  - `on_combat_damage_taken`
  - `on_start_of_turn`
  - `on_next_own_awakening`
  - `on_seal_break`
- Canonical move trigger emitted from shared movement helper:
  - `on_move_zenit_to_horizont`
- `taunt` keyword added to keyword registry and given real combat meaning in `engine/keyword_engine.py`:
  - taunt blockers are mandatory before normal blockers
  - `aegis` priority still applies inside the taunt-restricted blocker set

## Partially Improved

- Structured effect canonicalization still tolerates legacy internal aliases such as `reactivate`, `move_to_horizon`, `move_to_zenit` while allowing canonical tags to run through the same shared paths.
- `return_to_hand` shared structured routing now correctly handles both own and enemy selected units, but broader generic owner inference is still intentionally lightweight.
- Canonical trigger names now appear in runtime dispatch, but many older card-local handlers still listen to legacy event shapes in parallel.

## Deferred

- No new global targeting engine or declarative selector DSL was introduced.
- No deep replacement/control/copy mechanics were added.
- No broad event-bus redesign was attempted; canonical triggers are thin adapters over existing runtime flow.
- No full metadata-driven combat routing rewrite was attempted.

## Affected Canonical Values

### Targets

- `enemy_horizont_entity`
- `own_horizont_entity`
- `enemy_zenit_entity`
- `other_own_entity`
- `opposing_entity`

### Effect tags

- `grant_keyword`
- `ready`
- `return_to_hand`
- `move_horizont`
- `move_zenit`

### Triggers

- `on_combat_damage_taken`
- `on_start_of_turn`
- `on_next_own_awakening`
- `on_move_zenit_to_horizont`
- `on_seal_break`

### Keywords

- `taunt`

## Affected Cards / Examples

- `Provokalo Kialtas` style cards using `grant_keyword` + `other_own_entity`
- `Ujra Ebredes` style cards using canonical `ready`
- `Mentolanc` style cards using canonical `return_to_hand` on own units
- `Lehivas` style cards using canonical `move_horizont` from enemy Zenit
- `Soron Tulel` style cards using `opposing_entity`
- Existing combat traps and retaliation flows now also emit `on_combat_damage_taken`
- Seal-break based cards now receive canonical `on_seal_break`
- Turn-based delayed effects can hook onto `on_start_of_turn` and `on_next_own_awakening`
- `taunt`-bearing defenders now influence real blocker selection

## New Tests Added

- `tests/test_structured_effects.py`
  - canonical `grant_keyword`
  - canonical `ready`
  - own-target `return_to_hand`
  - `enemy_zenit_entity` -> `move_horizont`
  - `opposing_entity` damage targeting
- `tests/test_keywords.py`
  - mandatory taunt blocking
  - exhausted taunt no longer forcing a block
- `tests/test_game_flow.py`
  - `on_combat_damage_taken` dispatch
  - `on_seal_break` dispatch
  - `on_move_zenit_to_horizont` dispatch
  - `on_start_of_turn` and `on_next_own_awakening` dispatch

## Remaining Known Gaps

- Several canonical targets and effect tags still rely on card-local fallbacks outside this batch.
- Some legacy internal names still exist internally even where canonical runtime support now exists.
- `taunt` currently has combat-blocking meaning only; it does not yet rewrite broader attack-targeting preferences outside blocker resolution.
- Canonical trigger support is still adapter-based rather than fully canonical end-to-end in every handler.
