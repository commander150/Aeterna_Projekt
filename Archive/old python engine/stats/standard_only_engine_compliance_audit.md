# Standard-only engine compliance audit

Only final canonical standard values appear as rows below. Aliases and legacy/internal names are intentionally excluded from the main audit and referenced through `canonical_alias_map.md`.

## Zona_Felismerve

| canonical value | support status | evidence in code | evidence in tests | current handling path | blockers / missing logic | recommended next step |
| --- | --- | --- | --- | --- | --- | --- |
| `aeternal` | `fully_supported` | `engine/game.py` | - | core board model | No major blocker. | Keep as reference standard value. |
| `blank` | `fully_supported` | `engine/game.py` | - | core board model | No major blocker. | Keep as reference standard value. |
| `deck` | `fully_supported` | `engine/game.py` | - | core board model | No major blocker. | Keep as reference standard value. |
| `dominium` | `fully_supported` | `engine/game.py` | - | core board model | No major blocker. | Keep as reference standard value. |
| `graveyard` | `fully_supported` | `engine/game.py` | - | core board model | No major blocker. | Keep as reference standard value. |
| `hand` | `fully_supported` | `engine/game.py` | - | core board model | No major blocker. | Keep as reference standard value. |
| `horizont` | `fully_supported` | `engine/game.py` | - | core board model | No major blocker. | Keep as reference standard value. |
| `lane` | `fully_supported` | `engine/game.py` | - | core board model | No major blocker. | Keep as reference standard value. |
| `seal_row` | `fully_supported` | `engine/game.py` | - | core board model | No major blocker. | Keep as reference standard value. |
| `source` | `fully_supported` | `engine/game.py` | - | core board model | No major blocker. | Keep as reference standard value. |
| `zenit` | `fully_supported` | `engine/game.py` | - | core board model | No major blocker. | Keep as reference standard value. |

## Kulcsszavak_Felismerve

| canonical value | support status | evidence in code | evidence in tests | current handling path | blockers / missing logic | recommended next step |
| --- | --- | --- | --- | --- | --- | --- |
| `aegis` | `fully_supported` | `engine/keyword_engine.py` | `tests/test_keywords.py` | keyword_engine | No major blocker. | Keep as reference keyword. |
| `bane` | `fully_supported` | `engine/keyword_engine.py` | - | keyword_engine | No major blocker. | Keep as reference keyword. |
| `blank` | `partially_supported` | `engine/keyword_engine.py` | - | keyword_engine | Keyword is recognized but not yet proven end-to-end everywhere. | Add targeted runtime proof where cards demand it. |
| `burst` | `partially_supported` | `cards/resolver.py`, `engine/effect_diagnostics_v2.py` | - | mixed runtime handler + diagnostics | Runtime exists, but not as a fully generic standard keyword path. | Continue moving burst semantics off text-only routing. |
| `celerity` | `fully_supported` | `engine/card.py`, `engine/keyword_engine.py` | - | card/unit initialization | No major blocker. | Keep as reference keyword. |
| `clarion` | `partially_supported` | `cards/resolver.py`, `cards/priority_handlers.py` | - | card-specific runtime handlers | Mostly card-local, not a single generic standard resolver. | Prefer shared Clarion routing when touching new cards. |
| `echo` | `partially_supported` | `engine/effects.py`, `cards/resolver.py` | - | death/runtime mix | Death-side semantics are still partly card-local. | Unify generic Echo bookkeeping later. |
| `ethereal` | `fully_supported` | `engine/keyword_engine.py` | `tests/test_keywords.py` | keyword_engine | No major blocker. | Keep as reference keyword. |
| `harmonize` | `fully_supported` | `engine/keyword_engine.py` | - | keyword_engine | No major blocker. | Keep as reference keyword. |
| `resonance` | `fully_supported` | `engine/keyword_engine.py` | - | keyword_engine | No major blocker. | Keep as reference keyword. |
| `sundering` | `fully_supported` | `engine/keyword_engine.py` | - | keyword_engine | No major blocker. | Keep as reference keyword. |
| `taunt` | `small_change_needed` | `engine/game.py`, `engine/keyword_engine.py` | - | targeting/combat | Forced-target routing is not fully driven from the standard keyword field. | Add an explicit targeting gate for taunt. |

## Trigger_Felismerve

| canonical value | support status | evidence in code | evidence in tests | current handling path | blockers / missing logic | recommended next step |
| --- | --- | --- | --- | --- | --- | --- |
| `blank` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_attack_declared` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_attack_hits` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_block_survived` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_bounce` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_combat_damage_dealt` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_combat_damage_taken` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_damage_survived` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_death` | `fully_supported` | `engine/triggers.py`, `cards/resolver.py` | - | death trigger dispatch | No major blocker. | Keep as reference trigger. |
| `on_destroy` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_discard` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_enemy_ability_activated` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_enemy_card_played` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_enemy_extra_draw` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_enemy_horizont_threshold` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_enemy_multiple_draws` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_enemy_second_summon_in_turn` | `new_engine_logic_needed` | `engine/game.py` | - | none | Needs turn-scoped summon counters. | Add generic per-turn summon counters first. |
| `on_enemy_spell_or_ritual_played` | `small_change_needed` | `engine/game.py`, `cards/priority_handlers.py` | - | event routing | Spell vs ritual event unification is still uneven. | Add a shared enemy spell-or-ritual event payload. |
| `on_enemy_spell_target` | `fully_supported` | `engine/game.py`, `cards/priority_handlers.py` | - | spell-target reaction path | No major blocker. | Keep as reference trigger. |
| `on_enemy_summon` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_enemy_third_draw_in_turn` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_enemy_zenit_summon` | `small_change_needed` | `engine/game.py` | - | summon event with zone context | Zone-filtered summon subscribers are still sparse. | Route zenit summon subscribers from the existing summon payload. |
| `on_entity_enters_horizont` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_gain_keyword` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_heal` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_influx_phase` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_leave_board` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_move_zenit_to_horizont` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_next_own_awakening` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_position_swap` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_ready_from_exhausted` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_seal_break` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_source_placement` | `not_observed_in_current_cards` | - | - | - | Not observed in the current cards.xlsx. | Keep documented; no runtime action needed yet. |
| `on_spell_cast_by_owner` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_start_of_turn` | `fully_supported` | `engine/game.py` | - | turn phase dispatch | No major blocker. | Keep as reference trigger. |
| `on_stat_gain` | `new_engine_logic_needed` | `engine/triggers.py` | - | none | No generic stat-gain dispatch exists. | Add a generic stat-change event if the cards justify it. |
| `on_summon` | `fully_supported` | `engine/game.py`, `cards/priority_handlers.py` | - | runtime trigger dispatch | No major blocker. | Keep as reference trigger. |
| `on_trap_triggered` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `on_turn_end` | `small_change_needed` | `engine/game.py`, `engine/triggers.py` | - | event dispatch | Trigger exists conceptually, but standard routing is not fully unified yet. | Add a thin adapter before deeper engine work. |
| `static` | `partially_supported` | `engine/structured_effects.py`, `engine/effect_diagnostics_v2.py` | - | passive/static classification | Many static cards are recognized but not all are explicitly simulated. | Prefer passive/runtime_supported bookkeeping over missing_implementation. |

## Celpont_Felismerve

| canonical value | support status | evidence in code | evidence in tests | current handling path | blockers / missing logic | recommended next step |
| --- | --- | --- | --- | --- | --- | --- |
| `blank` | `not_observed_in_current_cards` | - | - | - | Not observed in the current cards.xlsx. | Keep documented; no runtime action needed yet. |
| `enemy_aeternal` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_entities` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_entity` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_face_down_trap` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_hand` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_hand_card` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_horizont_entities` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_horizont_entity` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_seal` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_seals` | `not_observed_in_current_cards` | - | - | - | Not observed in the current cards.xlsx. | Keep documented; no runtime action needed yet. |
| `enemy_source_card` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_spell` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_spell_or_ritual` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_zenit_entities` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `enemy_zenit_entity` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `lane` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `opponent` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `opposing_entity` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `other_own_entity` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_aeternal` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_deck` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_entities` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_entity` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_face_down_trap` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_graveyard` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_graveyard_entity` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_hand` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_horizont_entities` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_horizont_entity` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_seal` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_seals` | `not_observed_in_current_cards` | - | - | - | Not observed in the current cards.xlsx. | Keep documented; no runtime action needed yet. |
| `own_source_card` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_zenit_entities` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `own_zenit_entity` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `self` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |
| `source_card` | `partially_supported` | `engine/structured_effects.py`, `engine/game.py` | - | target routing | Target family exists, but not every standard target has a direct shared validator path. | Tighten target validation incrementally. |

## Hatascimkek

| canonical value | support status | evidence in code | evidence in tests | current handling path | blockers / missing logic | recommended next step |
| --- | --- | --- | --- | --- | --- | --- |
| `ability_lock` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `atk_mod` | `fully_supported` | `cards/priority_handlers.py`, `engine/structured_effects.py` | `tests/test_priority_handlers.py` | buff helper + structured routing | No major blocker. | Keep as reference primitive. |
| `attack_nullify` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `attack_restrict` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `blank` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `block_restrict` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `choice` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `cleanse` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `control_change` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `copy_keywords` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `copy_stats` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `cost_mod` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `counterspell` | `small_change_needed` | `cards/priority_handlers.py` | - | card-local spell cancel | Existing spell-target reactions do not yet expose a generic counterspell primitive. | Lift the shared cancel branch into a reusable helper. |
| `damage` | `fully_supported` | `engine/effects.py`, `engine/structured_effects.py` | `tests/test_structured_effects.py` | central damage pipeline | No major blocker. | Keep as reference primitive. |
| `damage_bonus` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `damage_immunity` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `damage_prevention` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `deck_bottom` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `destroy` | `fully_supported` | `engine/effects.py`, `engine/structured_effects.py` | - | destroy pipeline | No major blocker. | Keep as reference primitive. |
| `discard` | `partially_supported` | `cards/priority_handlers.py` | - | card-local runtime | Discard exists, but not as one uniform primitive. | Add a shared discard helper when the next batch needs it. |
| `draw` | `fully_supported` | `engine/player.py`, `engine/structured_effects.py` | - | draw pipeline | No major blocker. | Keep as reference primitive. |
| `exhaust` | `fully_supported` | `engine/structured_effects.py` | - | structured + runtime | No major blocker. | Keep as reference primitive. |
| `free_cast` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `grant_keyword` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `graveyard_recursion` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `graveyard_replacement` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `heal` | `fully_supported` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | heal pipeline | No major blocker. | Keep as reference primitive. |
| `hp_mod` | `partially_supported` | `cards/priority_handlers.py`, `engine/structured_effects.py` | - | buff helper | HP lifecycle and cleanup are less uniform than ATK buffs. | Keep canonical `hp_mod`, continue consolidating cleanup. |
| `move_horizont` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `move_to_source` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `move_zenit` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `overflow_damage` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `position_lock` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `random_discard` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `ready` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `redirect` | `small_change_needed` | `cards/priority_handlers.py` | - | card-local redirect | Redirect exists locally, not as a generic primitive. | Keep it local unless more redirect cards arrive. |
| `resource_acceleration` | `small_change_needed` | `engine/player.py` | - | source acceleration helpers | Close to source manipulation, but not yet tagged explicitly. | Alias into source acceleration helper if semantics match. |
| `resource_drain` | `new_engine_logic_needed` | `engine/player.py` | - | none | No clean generic enemy resource drain primitive is exposed. | Design a shared resource-drain contract first. |
| `resource_gain` | `small_change_needed` | `engine/player.py` | - | resource/source manipulation | Resource gain exists around source handling, but not under a standard effect-tag path. | Add a small effect-tag adapter to source gain. |
| `resource_spend` | `small_change_needed` | `engine/player.py` | - | source spend flow | Spend is implicit in costs, not explicit as an effect primitive. | Add a thin explicit resource spend helper. |
| `return_to_deck` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `return_to_hand` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `reveal` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `sacrifice` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `seal_damage` | `fully_supported` | `engine/effects.py`, `engine/structured_effects.py` | - | seal damage pipeline | No major blocker. | Keep as reference primitive. |
| `source_manipulation` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `stat_protection` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `stat_reset` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `summon` | `small_change_needed` | `cards/priority_handlers.py`, `engine/game.py` | - | card-local summon logic | No shared metadata-driven summon primitive exists yet. | Introduce a small shared summon helper before broad rollout. |
| `summon_restrict` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `summon_token` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `trap_immunity` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `tutor` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `type_change` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |
| `untargetable` | `small_change_needed` | `engine/structured_effects.py`, `cards/priority_handlers.py` | - | structured + local runtime mix | Canonical tag is present in data, but not yet a first-class runtime primitive. | Prefer small tag adapters over new frameworks. |

## Idotartam_Felismerve

| canonical value | support status | evidence in code | evidence in tests | current handling path | blockers / missing logic | recommended next step |
| --- | --- | --- | --- | --- | --- | --- |
| `blank` | `not_observed_in_current_cards` | - | - | - | Not observed in the current cards.xlsx. | Keep documented; no runtime action needed yet. |
| `during_combat` | `small_change_needed` | `engine/game.py` | - | expiry bookkeeping | Timing buckets exist, but many standard durations are not yet explicit. | Add one expiry bucket at a time. |
| `instant` | `small_change_needed` | `engine/game.py` | - | expiry bookkeeping | Timing buckets exist, but many standard durations are not yet explicit. | Add one expiry bucket at a time. |
| `next_own_awakening` | `small_change_needed` | `engine/game.py` | - | expiry bookkeeping | Timing buckets exist, but many standard durations are not yet explicit. | Add one expiry bucket at a time. |
| `next_own_turn_start` | `small_change_needed` | `engine/game.py` | - | expiry bookkeeping | Timing buckets exist, but many standard durations are not yet explicit. | Add one expiry bucket at a time. |
| `static_while_on_board` | `small_change_needed` | `engine/game.py` | - | expiry bookkeeping | Timing buckets exist, but many standard durations are not yet explicit. | Add one expiry bucket at a time. |
| `until_match_end` | `small_change_needed` | `engine/game.py` | - | expiry bookkeeping | Timing buckets exist, but many standard durations are not yet explicit. | Add one expiry bucket at a time. |
| `until_next_enemy_turn` | `small_change_needed` | `engine/game.py` | - | expiry bookkeeping | Timing buckets exist, but many standard durations are not yet explicit. | Add one expiry bucket at a time. |
| `until_next_own_turn_end` | `small_change_needed` | `engine/game.py` | - | expiry bookkeeping | Timing buckets exist, but many standard durations are not yet explicit. | Add one expiry bucket at a time. |
| `until_turn_end` | `small_change_needed` | `engine/game.py` | - | expiry bookkeeping | Timing buckets exist, but many standard durations are not yet explicit. | Add one expiry bucket at a time. |
| `while_active` | `small_change_needed` | `engine/game.py` | - | expiry bookkeeping | Timing buckets exist, but many standard durations are not yet explicit. | Add one expiry bucket at a time. |
