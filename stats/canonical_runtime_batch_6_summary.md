# Canonical Runtime Batch 6 Summary

## Implemented
- Added a shared `place_card_in_source` helper in `engine/actions.py`, and routed the common source-placement paths through it.
- `move_target_to_source` and `grant_resource` now use the same canonical source helper instead of direct `osforras` writes.
- `Jatekos.osforras_bovites()` now uses the shared source path instead of hand-pop + direct source append.
- Seal-break source placement in both `engine/effects.py` and `engine/game.py` now goes through the shared canonical source helper.
- Horizont summon play in `engine/game.py` now uses `ActionLibrary.summon_card_to_horizont(...)` instead of a local summon branch.
- `handle_hamis_halal(...)` now uses the shared `return_target_to_hand(...)` path, so `untargetable` enforcement is no longer bypassed there.
- `_put_entity_on_top_of_deck(...)` now uses the shared `move_target_to_deck(...)` path, so deck-return enforcement is consistent there too.

## Partially Improved
- Source placement is more canonical-first on the common paths, but some card-local `osforras`-adjacent logic still exists outside the main helper family.
- Summon aftermath is cleaner for common Horizont play, but Zenit summon and some token/card-local aftermath branches are still mixed.
- Bounce / deck-return consistency improved on the patched local helpers, but not every legacy card-local branch was swept in this batch.

## Deferred
- No repository-wide cleanup of every direct zone write.
- No deep source-zone subsystem rewrite.
- No new hidden-information, control-change, copy, or replacement mechanics.
- No full normalization of every trap discard / consume path into a single shared helper family.

## Affected Canonical Values
- `move_to_source`
- `source_manipulation`
- `on_source_placement`
- `on_position_changed`
- `summon`
- `on_entity_enters_horizont`
- `return_to_hand`
- `return_to_deck`
- `untargetable`

## Affected Runtime Paths
- Shared source helper family
- Resource gain from deck to source
- Manual source expansion from hand
- Seal break to source placement
- Common Horizont summon play path
- Card-local return-to-hand prevention path (`Hamis Halal`)
- Card-local return-to-deck/top-deck path

## New Tests Added
- `tests.test_game_flow.TestGameFlow.test_kijatszas_fazis_horizont_summon_uses_shared_horizont_path`
- `tests.test_player_resource_payment.TestJatekosFizetes.test_osforras_bovites_uses_shared_source_dispatch`
- `tests.test_priority_handlers.TestPriorityHandlers.test_hamis_halal_uses_shared_return_to_hand_enforcement`
- `tests.test_priority_handlers.TestPriorityHandlers.test_put_entity_on_top_of_deck_uses_shared_deck_enforcement`

## Remaining Gaps
- Some older card-local movement and trap-consume branches still perform direct zone writes.
- A few source-adjacent flows still dispatch canonically but are not yet funneled through one single helper path.
- Zenit summon and some special aftermath flows are still only partially consolidated.
