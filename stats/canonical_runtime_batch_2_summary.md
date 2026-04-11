# Canonical Runtime Batch 2 Summary

## Implemented

- Shared canonical selector coverage strengthened for:
  - `own_entities`
  - `enemy_entities`
  - `own_horizont_entities`
  - `enemy_horizont_entities`
  - `own_zenit_entity`
  - `own_zenit_entities`
- Structured runtime now uses canonical multi-target selectors in shared paths for:
  - `heal`
  - `attack_restrict`
  - `block_restrict`
- Shared effect primitives added or strengthened:
  - `counterspell`
  - `attack_restrict`
  - `block_restrict`
  - `graveyard_recursion`
  - `summon`
  - `summon_token`
- Shared summon helpers added in `engine/actions.py`:
  - `summon_card_to_horizont`
  - `summon_token_to_horizont`
- Existing token creation in `cards/priority_handlers.py` now reuses the shared token helper instead of card-local summon construction.
- Canonical trigger adapters added in runtime:
  - `on_attack_hits`
  - `on_enemy_spell_or_ritual_played`
  - `on_enemy_zenit_summon`
  - `on_trap_triggered`

## Partially Improved

- `counterspell` is now a real shared structured primitive, but broader trap/spell cancellation still mixes canonical runtime with existing card-local trap handlers.
- `graveyard_recursion` is shared for simple entity return flows, but does not yet model broader graveyard replacement, timing, or ownership edge cases.
- `summon` is now shared for context-driven simple entity placement, but not yet a full generic summon/search/ownership framework.
- `on_attack_hits` is emitted for successful combat connections, but still rides on the existing combat loop instead of a fully separate canonical combat event layer.

## Deferred

- No hidden-information target family was added.
- No source-card / source-zone special target DSL was introduced.
- No deep summon/control/copy/replacement engine was added.
- No full generalized graveyard semantics or resurrection timing model was introduced.
- No large trap framework rewrite was attempted; canonical trap trigger reporting is layered onto the existing runtime.

## Affected Canonical Values

### Targets

- `own_entities`
- `enemy_entities`
- `own_horizont_entities`
- `enemy_horizont_entities`
- `own_zenit_entity`
- `own_zenit_entities`

### Effect tags

- `counterspell`
- `attack_restrict`
- `block_restrict`
- `graveyard_recursion`
- `summon`
- `summon_token`

### Triggers

- `on_attack_hits`
- `on_enemy_spell_or_ritual_played`
- `on_enemy_zenit_summon`
- `on_trap_triggered`

## Affected Cards / Examples

- `Tamadastilto Hullam` style cards using `enemy_entities` + `attack_restrict`
- `Hatso Zar` style cards using `own_zenit_entity` + `block_restrict`
- simple resurrection cards such as `Siri Visszahivas` style effects
- simple summon cards using shared `summon`
- token-producing cards now sharing the common token summon path
- enemy spell reaction cards now visible through `on_enemy_spell_or_ritual_played`
- enemy Zenit summon reaction cards now visible through `on_enemy_zenit_summon`
- trap activations now also emit `on_trap_triggered`
- successful combat hits now expose `on_attack_hits`

## New Tests Added

- `tests/test_structured_effects.py`
  - canonical plural selector coverage
  - `attack_restrict`
  - `block_restrict`
  - `graveyard_recursion`
  - `summon`
  - `summon_token`
  - `counterspell`
- `tests/test_game_flow.py`
  - `on_enemy_spell_or_ritual_played`
  - `on_enemy_zenit_summon`
  - `on_trap_triggered`
  - `on_attack_hits`

## Remaining Gaps

- Some canonical multi-target paths still rely on fallback local iteration outside the shared selector route.
- Canonical summon support is intentionally simple and does not yet cover advanced lane choice, opponent-side summons, or control-changing summons.
- Trap runtime remains a mixed model: canonical trigger reporting is now present, but many concrete effects are still card-local.
- Canonical effect support still coexists with legacy internal alias names in parts of the structured runtime.
