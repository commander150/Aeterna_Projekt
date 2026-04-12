# Canonical Runtime Batch 7 Summary

## Implemented
- Added shared trap cleanup helpers in `engine/actions.py` for Zenit trap consume and trap restore.
- Added a shared `retreat_horizont_to_zenit(...)` movement helper that keeps `position_lock` enforcement and `on_position_changed` dispatch together.
- Added a shared `summon_card_to_zenit(...)` helper so the common Zenit entity play path no longer uses a bespoke local summon branch.
- Consolidated the main trap-consume paths in `engine/game.py` through `_consume_trap(...)`, covering summon-trap, spell-trap, combat-trap, and direct-attack-trap cleanup.
- Consolidated `_consume_named_trap(...)` / `_restore_consumed_trap(...)` in `cards/priority_handlers.py` onto the shared trap helper family.
- Moved `Fa-oleles` and `Eletmento Burok` retreat logic onto the shared Zenit retreat helper.

## Partially Improved
- Common trap consume/cleanup is now much more centralized, but some card-local trap destruction paths still intentionally bypass consume semantics because they are destruction, not activation.
- Shared movement coverage improved for self-retreat-to-Zenit paths, but lane-swap and sideways movement special cases still have local implementations.
- Zenit summon is cleaner on the common play path, but not every nonstandard Zenit placement route is funneled through the new helper yet.

## Deferred
- No full trap framework rewrite.
- No full movement/lane abstraction rewrite.
- No repository-wide sweep of all direct `set_zone_slot(...)` usages.
- No deep hidden-information or replacement/control mechanics.

## Affected Canonical Values
- `on_trap_triggered`
- `on_position_changed`
- `on_source_placement`
- `on_entity_enters_horizont`
- `on_move_zenit_to_horizont`
- `position_lock`
- `untargetable`

## Affected Runtime Paths
- Summon trap consume path
- Spell trap consume path
- Combat trap consume path
- Direct seal-attack trap consume path
- Named trap consume / restore helper path
- Self retreat from Horizont to Zenit
- Common Zenit summon play path

## New Tests Added
- `tests.test_game_flow.TestGameFlow.test_summon_card_to_zenit_uses_shared_dispatch_path`
- `tests.test_game_flow.TestGameFlow.test_resolve_summon_traps_emits_on_trap_triggered_and_consumes_trap`
- `tests.test_priority_handlers.TestPriorityHandlers.test_fa_oleles_respects_shared_position_lock_on_retreat`
- `tests.test_priority_handlers.TestPriorityHandlers.test_eletmento_burok_uses_shared_retreat_to_zenit_path`

## Remaining Gaps
- A few trap-related destroy/limit-discard paths still use local cleanup because they are not plain consume flows.
- Sideways slide / full swap / lane-rearrangement effects still have card-local movement logic.
- Some special summon aftermath branches still dispatch locally instead of through one shared post-summon helper family.
