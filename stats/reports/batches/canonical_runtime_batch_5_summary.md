# Canonical Runtime Batch 5 Summary

## Implemented

- Shared enforcement strengthened for `ability_lock` on important priority-trigger paths:
  - locked sources now skip the common `on_summon_priority` path
  - locked destroyed sources now skip the common `on_destroyed` priority path through payload-based enforcement
  - locked reactive targets now skip the common `on_spell_targeted_priority` path
- Shared enforcement strengthened for `position_lock` on the common movement paths:
  - `move_entity_between_zones(...)` now blocks repositioning locked entities
  - `move_target_to_zenit(...)` now blocks both a locked front entity and locked swap target
  - `move_target_to_horizont(...)` inherits the same lock enforcement through the shared movement helper
- Shared enforcement strengthened for `untargetable` on common targeting/movement helpers:
  - `return_target_to_hand(...)` now validates the shared targeting state
  - `move_target_to_deck(...)` now respects target validation for board entities
  - `move_target_to_source(...)` now respects target validation for board entities
  - `move_target_to_zenit(...)` now also respects target validation before targeted repositioning
- `taunt` remained the blocker-level meaning, but its stability is now explicitly regression-covered alongside `ethereal` filtering and existing blocker-priority logic.
- Trigger consistency improved for `on_seal_break` by emitting the canonical event from the direct seal-damage effect path, not only the main combat seal-break path.
- Trigger consistency improved for `on_source_placement` by emitting the canonical event from:
  - seal-to-source guardianship placement in the main combat seal-break path
  - seal-to-source placement in direct effect-driven seal damage
  - fallback resource gain in `engine/effects.py` through the shared source helper
- Existing `on_destroy`, `on_discard`, `on_gain_keyword`, `on_attack_hits`, and `on_seal_break` paths are now regression-covered more explicitly in common runtime scenarios.

## Partially Improved

- `ability_lock` now blocks key shared priority paths, but it still does not suppress every legacy card-local activated ability branch in the codebase.
- `untargetable` is more consistent on shared movement/return/source helpers, but not every bespoke card-local redirect or manipulation path has been consolidated yet.
- `on_source_placement` is now emitted in more shared places, but some legacy direct source writes may still exist outside the helper family.

## Deferred

- No full global “silence framework” was added for every handler and trigger family.
- No deep source-zone rules engine or source-specific visibility/control system was added.
- No broad hidden-information or replacement-style mechanics were introduced.
- No full sweep was made across every card-local movement/manipulation special case.

## Affected Canonical Values

### Runtime States / Keywords

- `ability_lock`
- `position_lock`
- `untargetable`
- `taunt`

### Triggers

- `on_destroy`
- `on_discard`
- `on_source_placement`
- `on_gain_keyword`
- `on_attack_hits`
- `on_seal_break`

## Affected Cards / Examples

- `Lopakodo Felcser-Dron` style summon-triggered unit abilities
- `Kod-Alak` style spell-targeted reactive abilities
- `Kove Valas` / movement-lock style position denial
- `Univerzalis Csere` discard path
- direct seal-damage effects such as structured seal-damage and `Utolso Szikra`-type seal hits
- source placement from deck, graveyard, and seal-row guardianship paths

## New Tests Added

- `test_harc_fazis_emits_on_attack_hits_for_blocker_hit`
- `test_return_to_hand_respects_untargetable_enforcement`
- `test_position_lock_blocks_move_to_horizont`
- `test_locked_summon_ability_does_not_apply_priority_effect`
- `test_feltor_pecset_emits_on_source_placement_when_guardianship_moves_to_source`
- `test_direct_seal_damage_emits_on_seal_break`
- `test_taunt_remains_primary_under_ethereal_block_filtering`

## Remaining Gaps

- `ability_lock` still needs incremental rollout to more card-local handlers if we want near-total silence enforcement.
- `untargetable` still has legacy bypass risk in bespoke card-local targeting code that does not yet use shared helpers.
- `on_source_placement` is much cleaner now, but a full source write inventory would still be needed for total canonical consistency.
- `taunt` remains intentionally scoped to blocker choice, not a broader attack redirection system.
