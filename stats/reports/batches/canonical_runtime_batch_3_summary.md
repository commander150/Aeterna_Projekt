# Canonical Runtime Batch 3 Summary

## Implemented

- Shared canonical selector support added for `enemy_spell`, `enemy_spell_or_ritual`, `own_deck`, `own_graveyard_entity`, `own_hand`, and `enemy_hand` through the common `ActionLibrary.targets_for_key(...)` path.
- Canonical structured effect support added for `return_to_deck` and `deck_bottom` using shared deck movement helpers instead of card-local deck manipulation.
- Canonical structured effect support added for `move_to_source` using a shared source-movement helper.
- Canonical structured effect support added for `resource_gain` using a shared resource helper that promotes cards from deck into `osforras`.
- Canonical structured effect support added for `cost_mod` using shared next-card discount buckets with canonical-first routing.
- Canonical structured effect support strengthened for `untargetable` through a shared targeting-state helper instead of local flag mutation.
- Canonical trigger adapter support added for `on_heal`.
- Canonical trigger adapter support added for `on_bounce`.
- Canonical trigger adapter support added for `on_position_swap`.
- Canonical trigger adapter support added for `on_entity_enters_horizont`.

## Partially Improved

- `enemy_spell` and `enemy_spell_or_ritual` now have shared selector/runtime support, but they still rely on current spell context rather than a full generic stack model.
- `move_to_source` now works for common graveyard/hand/board paths, but it is not yet a full generalized source-zone routing system.
- `cost_mod` is now canonical-first, but it still maps onto the existing next-entity / next-trap / next-machine discount buckets rather than a deeper universal cost layer.
- `untargetable` now has a shared helper path, but it still depends on the current targeting-state model rather than a broader layered replacement system.

## Deferred

- No hidden-information targeting for face-down enemy hand or face-down trap special cases.
- No full spell stack / spell object targeting framework beyond the current spell context.
- No deep source manipulation semantics beyond the common shared helper path implemented here.
- No generalized replacement/control/copy engine work in this batch.

## Affected Canonical Values

### Targets

- `enemy_spell`
- `enemy_spell_or_ritual`
- `own_deck`
- `own_graveyard_entity`
- `own_hand`
- `enemy_hand`

### Effect Tags

- `return_to_deck`
- `deck_bottom`
- `move_to_source`
- `resource_gain`
- `cost_mod`
- `untargetable`

### Triggers

- `on_heal`
- `on_bounce`
- `on_position_swap`
- `on_entity_enters_horizont`

## Affected Cards / Examples

- Counterspell-style reactions using `enemy_spell` / `enemy_spell_or_ritual`
- Hand and deck manipulation effects that return cards to deck top or deck bottom
- Graveyard-to-source style effects
- Simple resource acceleration effects
- Simple cost reduction effects
- Untargetable buff effects
- Bounce / heal / movement-triggered cards that depend on canonical trigger names

## New Tests Added

- `test_collection_target_selectors_cover_batch_three_targets`
- `test_structured_return_to_deck_moves_own_hand_card_to_top`
- `test_structured_deck_bottom_moves_enemy_hand_card_to_bottom`
- `test_structured_move_to_source_uses_own_graveyard_entity`
- `test_structured_resource_gain_uses_shared_helper`
- `test_structured_cost_mod_uses_shared_helper`
- `test_structured_untargetable_uses_shared_helper`
- `test_heal_unit_emits_on_heal`
- `test_return_target_to_hand_emits_on_bounce`
- `test_move_target_to_zenit_swap_emits_on_position_swap`
- `test_summon_card_to_horizont_emits_on_entity_enters_horizont`

## Remaining Gaps

- Enemy spell targeting still does not model a full independent spell stack.
- Source movement is still shared-helper based, not a complete standardized source-zone subsystem.
- Cost modification is still bucket-based and not yet a generalized effect-lifetime-aware cost framework.
- No deep hidden-information targeting semantics were added for hand-based enemy selection.
