# Canonical Runtime Batch 4 Summary

## Implemented

- Shared canonical selector support added for `lane`, `own_source_card`, `enemy_source_card`, `own_graveyard`, and `enemy_hand_card` through the common `ActionLibrary.targets_for_key(...)` path.
- Shared source-collection targeting added for `osforras`, so canonical source-card targets now resolve to concrete cards without card-local lookup code.
- Canonical structured effect support added for `ability_lock` using a shared runtime flag (`abilities_locked_until_turn_end`) and canonical-first routing.
- Canonical structured effect support added for `position_lock` using the shared `position_lock_awakenings` state instead of card-local-only mutation.
- Canonical structured effect support added for `source_manipulation` as a shared “promote to source” path built on the existing source helper family.
- Shared helper cleanup improved the `return_to_deck` / `move_to_source` family so they can also operate on `own_graveyard`, `own_source_card`, `enemy_source_card`, and `enemy_hand_card` selections where applicable.
- Canonical trigger adapter support added for `on_destroy`.
- Canonical trigger adapter support added for `on_discard`.
- Canonical trigger adapter support added for `on_source_placement`.
- Canonical trigger adapter support added for `on_gain_keyword`.

## Partially Improved

- `lane` is now a reusable canonical selector, but it is still a lightweight lane-index carrier rather than a full lane object / DSL.
- `ability_lock` now has a shared runtime state, but broad enforcement across every card-specific activated-ability path is still intentionally deferred.
- `source_manipulation` now has a real shared path for moving cards into source, but it is not yet a full generalized source-zone transformation framework.
- Source-targeted deck manipulation is now cleaner, but it still relies on simple ownership resolution rather than a deeper visibility / control model.

## Deferred

- No deep hidden-information model was added for enemy hand inspection or face-down trap targeting.
- No generalized source-zone rules engine was introduced beyond the shared helper path.
- No broad activated-ability suppression framework was added across every legacy priority handler.
- No control-change / copy / replacement style engine work was added in this batch.

## Affected Canonical Values

### Targets

- `lane`
- `own_source_card`
- `enemy_source_card`
- `own_graveyard`
- `enemy_hand_card`

### Effect Tags

- `ability_lock`
- `position_lock`
- `source_manipulation`
- `return_to_hand`
- `return_to_deck`
- `move_to_source`

### Triggers

- `on_destroy`
- `on_discard`
- `on_source_placement`
- `on_gain_keyword`

## Affected Cards / Examples

- Silence / ability-denial style entity effects
- Position-lock / stone-lock style movement denial effects
- Graveyard-to-source and source-promotion style cards
- Enemy hand / source interaction cards that previously needed local lookup assumptions
- Universal discard-style effects such as `Univerzalis Csere`

## New Tests Added

- `test_collection_target_selectors_cover_batch_four_targets`
- `test_structured_ability_lock_uses_shared_helper`
- `test_structured_position_lock_uses_shared_helper`
- `test_structured_source_manipulation_uses_shared_helper`
- `test_destroy_unit_emits_on_destroy`
- `test_discard_from_hand_emits_on_discard`
- `test_move_target_to_source_emits_on_source_placement`
- `test_grant_keyword_emits_on_gain_keyword`

## Remaining Gaps

- `ability_lock` is now shared state, but not every legacy activated ability path checks it yet.
- `source_manipulation` still covers the cheap common path, not every possible source-to-source or source-reorder variant.
- `lane` remains intentionally minimal and does not yet model full lane-wide batch operations.
- Enemy hand and source targets are runtime-compatible selectors now, but they still avoid deep hidden-information semantics.
