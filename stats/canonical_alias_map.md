# Canonical vs alias map

The final audit should only present canonical standard values. Non-standard values stay here as alias, legacy, or invalid observations.

## Zona_Felismerve

| field_name | observed_value | value_type | canonical_value | source_of_mapping | used_in_loader | used_in_runtime | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Zona_Felismerve` | `aeternal` | `standard` | `aeternal` | `standard_doc` | `yes` | `no` | - |
| `Zona_Felismerve` | `blank` | `standard` | `blank` | `standard_doc` | `yes` | `no` | - |
| `Zona_Felismerve` | `burst` | `invalid` | `-` | `none` | `yes` | `no` | No safe canonical mapping from the current standard. Burst is a keyword, not a zone. |
| `Zona_Felismerve` | `deck` | `standard` | `deck` | `standard_doc` | `yes` | `no` | - |
| `Zona_Felismerve` | `dominium` | `standard` | `dominium` | `standard_doc` | `yes` | `no` | - |
| `Zona_Felismerve` | `eternal` | `alias` | `aeternal` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Zona_Felismerve` | `forras` | `alias` | `source` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Zona_Felismerve` | `from hand` | `invalid` | `-` | `none` | `yes` | `no` | No safe canonical mapping from the current standard. |
| `Zona_Felismerve` | `graveyard` | `standard` | `graveyard` | `standard_doc` | `yes` | `no` | - |
| `Zona_Felismerve` | `hand` | `standard` | `hand` | `standard_doc` | `yes` | `no` | - |
| `Zona_Felismerve` | `horizont` | `standard` | `horizont` | `standard_doc` | `yes` | `no` | - |
| `Zona_Felismerve` | `kez` | `alias` | `hand` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Zona_Felismerve` | `lane` | `standard` | `lane` | `standard_doc` | `yes` | `no` | - |
| `Zona_Felismerve` | `pakli` | `alias` | `deck` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Zona_Felismerve` | `pecset` | `alias` | `seal_row` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Zona_Felismerve` | `pecsetek` | `alias` | `seal_row` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Zona_Felismerve` | `player` | `alias` | `aeternal` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Zona_Felismerve` | `seal` | `alias` | `seal_row` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Zona_Felismerve` | `seal_row` | `standard` | `seal_row` | `standard_doc` | `yes` | `no` | - |
| `Zona_Felismerve` | `sealrow` | `alias` | `seal_row` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Zona_Felismerve` | `source` | `standard` | `source` | `standard_doc` | `yes` | `no` | - |
| `Zona_Felismerve` | `temeto` | `alias` | `graveyard` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Zona_Felismerve` | `wards` | `alias` | `seal_row` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Zona_Felismerve` | `zenit` | `standard` | `zenit` | `standard_doc` | `yes` | `no` | - |

## Kulcsszavak_Felismerve

| field_name | observed_value | value_type | canonical_value | source_of_mapping | used_in_loader | used_in_runtime | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Kulcsszavak_Felismerve` | `aegis` | `standard` | `aegis` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `bane` | `standard` | `bane` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `blank` | `standard` | `blank` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `burst` | `standard` | `burst` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `celerity` | `standard` | `celerity` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `clarion` | `standard` | `clarion` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `echo` | `standard` | `echo` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `ethereal` | `standard` | `ethereal` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `harmonize` | `standard` | `harmonize` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `resonance` | `standard` | `resonance` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `sundering` | `standard` | `sundering` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `taunt` | `standard` | `taunt` | `standard_doc` | `yes` | `no` | - |
| `Kulcsszavak_Felismerve` | `trap` | `invalid` | `-` | `none` | `yes` | `yes` | No safe canonical mapping from the current standard. Trap/Jel is card-type semantics, not a standard keyword. |

## Trigger_Felismerve

| field_name | observed_value | value_type | canonical_value | source_of_mapping | used_in_loader | used_in_runtime | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Trigger_Felismerve` | `blank` | `standard` | `blank` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `death` | `alias` | `on_death` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Trigger_Felismerve` | `on_attack_declared` | `standard` | `on_attack_declared` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_attack_hits` | `standard` | `on_attack_hits` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_block_survived` | `standard` | `on_block_survived` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_bounce` | `standard` | `on_bounce` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_burst` | `legacy_internal` | `-` | `runtime_alias` | `yes` | `yes` | Runtime/internal naming; keep out of final canonical reports. |
| `Trigger_Felismerve` | `on_combat_damage_dealt` | `standard` | `on_combat_damage_dealt` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_combat_damage_taken` | `standard` | `on_combat_damage_taken` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_damage_survived` | `standard` | `on_damage_survived` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_death` | `standard` | `on_death` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_destroy` | `standard` | `on_destroy` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_destroyed` | `alias` | `on_death` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Trigger_Felismerve` | `on_discard` | `standard` | `on_discard` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_enemy_ability_activated` | `standard` | `on_enemy_ability_activated` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_enemy_card_played` | `standard` | `on_enemy_card_played` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_enemy_extra_draw` | `standard` | `on_enemy_extra_draw` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_enemy_horizont_threshold` | `standard` | `on_enemy_horizont_threshold` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_enemy_manifestation_start` | `legacy_internal` | `-` | `runtime_alias` | `yes` | `yes` | Runtime/internal naming; keep out of final canonical reports. |
| `Trigger_Felismerve` | `on_enemy_multiple_draws` | `standard` | `on_enemy_multiple_draws` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_enemy_second_summon_in_turn` | `standard` | `on_enemy_second_summon_in_turn` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_enemy_spell_or_ritual_played` | `standard` | `on_enemy_spell_or_ritual_played` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_enemy_spell_target` | `standard` | `on_enemy_spell_target` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_enemy_summon` | `standard` | `on_enemy_summon` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_enemy_third_draw_in_turn` | `standard` | `on_enemy_third_draw_in_turn` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_enemy_zenit_summon` | `standard` | `on_enemy_zenit_summon` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_entity_enters_horizont` | `standard` | `on_entity_enters_horizont` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_gain_keyword` | `standard` | `on_gain_keyword` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_graveyard_recursion` | `legacy_internal` | `-` | `runtime_alias` | `yes` | `yes` | Runtime/internal naming; keep out of final canonical reports. |
| `Trigger_Felismerve` | `on_heal` | `standard` | `on_heal` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_influx_phase` | `standard` | `on_influx_phase` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_infusion_phase` | `legacy_internal` | `-` | `runtime_alias` | `yes` | `yes` | Runtime/internal naming; keep out of final canonical reports. |
| `Trigger_Felismerve` | `on_lane_filled` | `legacy_internal` | `-` | `runtime_alias` | `yes` | `yes` | Runtime/internal naming; keep out of final canonical reports. |
| `Trigger_Felismerve` | `on_leave_board` | `standard` | `on_leave_board` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_move_zenit_to_horizont` | `standard` | `on_move_zenit_to_horizont` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_next_own_awakening` | `standard` | `on_next_own_awakening` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_play` | `legacy_internal` | `-` | `runtime_alias` | `yes` | `yes` | Runtime/internal naming; keep out of final canonical reports. Not listed in the final trigger standard; keep as legacy/runtime-only until data is cleaned. |
| `Trigger_Felismerve` | `on_position_swap` | `standard` | `on_position_swap` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_ready` | `alias` | `on_ready_from_exhausted` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Trigger_Felismerve` | `on_ready_from_exhausted` | `standard` | `on_ready_from_exhausted` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_seal_break` | `standard` | `on_seal_break` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_spell_cast_by_owner` | `standard` | `on_spell_cast_by_owner` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_spell_targeted` | `alias` | `on_enemy_spell_target` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Trigger_Felismerve` | `on_start_of_turn` | `standard` | `on_start_of_turn` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_stat_gain` | `standard` | `on_stat_gain` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_summon` | `standard` | `on_summon` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_trap_triggered` | `standard` | `on_trap_triggered` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `on_turn_end` | `standard` | `on_turn_end` | `standard_doc` | `yes` | `no` | - |
| `Trigger_Felismerve` | `static` | `standard` | `static` | `standard_doc` | `yes` | `no` | - |

## Celpont_Felismerve

| field_name | observed_value | value_type | canonical_value | source_of_mapping | used_in_loader | used_in_runtime | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Celpont_Felismerve` | `ellenseges_entitas` | `alias` | `enemy_entity` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Celpont_Felismerve` | `ellenseges_pecset` | `alias` | `enemy_seal` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Celpont_Felismerve` | `enemy_aeternal` | `standard` | `enemy_aeternal` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_entities` | `standard` | `enemy_entities` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_entity` | `standard` | `enemy_entity` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_face_down_trap` | `standard` | `enemy_face_down_trap` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_hand` | `standard` | `enemy_hand` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_hand_card` | `standard` | `enemy_hand_card` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_horizont_entities` | `standard` | `enemy_horizont_entities` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_horizont_entity` | `standard` | `enemy_horizont_entity` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_seal` | `standard` | `enemy_seal` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_source_card` | `standard` | `enemy_source_card` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_spell` | `standard` | `enemy_spell` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_spell_or_ritual` | `standard` | `enemy_spell_or_ritual` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_zenit_entities` | `standard` | `enemy_zenit_entities` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `enemy_zenit_entity` | `standard` | `enemy_zenit_entity` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `jatekos` | `alias` | `opponent` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Celpont_Felismerve` | `lane` | `standard` | `lane` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `masik_sajat_entitas` | `alias` | `other_own_entity` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Celpont_Felismerve` | `opponent` | `standard` | `opponent` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `opponent_player` | `alias` | `opponent` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Celpont_Felismerve` | `opposing_entity` | `standard` | `opposing_entity` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `other_own_entity` | `standard` | `other_own_entity` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_aeternal` | `standard` | `own_aeternal` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_deck` | `standard` | `own_deck` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_entities` | `standard` | `own_entities` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_entity` | `standard` | `own_entity` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_face_down_trap` | `standard` | `own_face_down_trap` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_graveyard` | `standard` | `own_graveyard` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_graveyard_entity` | `standard` | `own_graveyard_entity` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_hand` | `standard` | `own_hand` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_horizont_entities` | `standard` | `own_horizont_entities` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_horizont_entity` | `standard` | `own_horizont_entity` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_seal` | `standard` | `own_seal` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_source_card` | `standard` | `own_source_card` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_zenit_entities` | `standard` | `own_zenit_entities` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `own_zenit_entity` | `standard` | `own_zenit_entity` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `pecset` | `alias` | `enemy_seal` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Celpont_Felismerve` | `pecsetek` | `alias` | `enemy_seals` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Celpont_Felismerve` | `sajat_entitas` | `alias` | `own_entity` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Celpont_Felismerve` | `sajat_pecset` | `alias` | `own_seal` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Celpont_Felismerve` | `self` | `standard` | `self` | `standard_doc` | `yes` | `no` | - |
| `Celpont_Felismerve` | `self unit` | `alias` | `self` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Celpont_Felismerve` | `self_entity` | `alias` | `self` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Celpont_Felismerve` | `source_card` | `standard` | `source_card` | `standard_doc` | `yes` | `no` | - |

## Hatascimkek

| field_name | observed_value | value_type | canonical_value | source_of_mapping | used_in_loader | used_in_runtime | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Hatascimkek` | `ability_lock` | `standard` | `ability_lock` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `atk_buff` | `alias` | `atk_mod` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `atk_mod` | `standard` | `atk_mod` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `attack_nullify` | `standard` | `attack_nullify` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `attack_restrict` | `standard` | `attack_restrict` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `aura_modositas` | `alias` | `cost_mod` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `blank` | `standard` | `blank` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `block_restrict` | `standard` | `block_restrict` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `blokktiltas` | `alias` | `block_restrict` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `choice` | `standard` | `choice` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `cleanse` | `standard` | `cleanse` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `control_change` | `standard` | `control_change` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `copy_keywords` | `standard` | `copy_keywords` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `copy_stats` | `standard` | `copy_stats` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `cost_mod` | `standard` | `cost_mod` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `counterspell` | `standard` | `counterspell` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `damage` | `standard` | `damage` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `damage_bonus` | `standard` | `damage_bonus` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `damage_immunity` | `standard` | `damage_immunity` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `damage_prevention` | `standard` | `damage_prevention` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `deal_damage` | `alias` | `damage` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `deck_bottom` | `standard` | `deck_bottom` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `delayed_revival` | `invalid` | `-` | `none` | `yes` | `no` | No safe canonical mapping from the current standard. |
| `Hatascimkek` | `destroy` | `standard` | `destroy` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `discard` | `standard` | `discard` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `draw` | `standard` | `draw` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `effect_reduction` | `invalid` | `-` | `none` | `yes` | `no` | No safe canonical mapping from the current standard. |
| `Hatascimkek` | `end_turn` | `invalid` | `-` | `none` | `yes` | `no` | No safe canonical mapping from the current standard. |
| `Hatascimkek` | `exhaust` | `standard` | `exhaust` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `free_cast` | `standard` | `free_cast` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `grant_attack` | `alias` | `atk_mod` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `grant_hp` | `alias` | `hp_mod` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `grant_keyword` | `standard` | `grant_keyword` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `grant_max_hp` | `alias` | `hp_mod` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `grant_temp_attack` | `alias` | `atk_mod` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `graveyard_recursion` | `standard` | `graveyard_recursion` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `graveyard_replacement` | `standard` | `graveyard_replacement` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `gyogyitas` | `alias` | `heal` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `heal` | `standard` | `heal` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `hp_buff` | `alias` | `hp_mod` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `hp_mod` | `standard` | `hp_mod` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `huzas` | `alias` | `draw` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `keyword_adas` | `alias` | `grant_keyword` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `kezbe_vetel` | `alias` | `return_to_hand` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `kimerites` | `alias` | `exhaust` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `kulcsszoadas` | `alias` | `grant_keyword` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `laphuzas` | `alias` | `draw` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `megsemmisites` | `alias` | `destroy` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `move_horizont` | `standard` | `move_horizont` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `move_to_horizon` | `alias` | `move_horizont` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `move_to_horizont` | `alias` | `move_horizont` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `move_to_source` | `standard` | `move_to_source` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `move_to_zenit` | `alias` | `move_zenit` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `move_zenit` | `standard` | `move_zenit` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `mozgatas_horizontra` | `alias` | `move_horizont` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `mozgatas_zenitbe` | `alias` | `move_zenit` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `once_per_turn` | `invalid` | `-` | `none` | `yes` | `no` | No safe canonical mapping from the current standard. |
| `Hatascimkek` | `overflow_damage` | `standard` | `overflow_damage` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `pecsetsebzes` | `alias` | `seal_damage` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `position_lock` | `standard` | `position_lock` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `poziciocsere` | `alias` | `choice` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `pusztitas` | `alias` | `destroy` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `random_discard` | `standard` | `random_discard` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `reactivate` | `alias` | `ready` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `ready` | `standard` | `ready` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `redirect` | `standard` | `redirect` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `reflect_damage` | `alias` | `damage_bonus` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `resource_acceleration` | `standard` | `resource_acceleration` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `resource_drain` | `standard` | `resource_drain` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `resource_gain` | `standard` | `resource_gain` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `resource_spend` | `standard` | `resource_spend` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `retaliation_damage` | `alias` | `damage_bonus` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `return_to_deck` | `standard` | `return_to_deck` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `return_to_deck_bottom` | `alias` | `deck_bottom` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `return_to_hand` | `standard` | `return_to_hand` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `reveal` | `standard` | `reveal` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `sacrifice` | `standard` | `sacrifice` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `seal_damage` | `standard` | `seal_damage` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `sebzes` | `alias` | `damage` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `sebzessemlegesites` | `alias` | `damage_prevention` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `source_manipulation` | `standard` | `source_manipulation` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `stat_protection` | `standard` | `stat_protection` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `stat_reset` | `standard` | `stat_reset` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `summon` | `standard` | `summon` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `summon_restrict` | `standard` | `summon_restrict` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `summon_token` | `standard` | `summon_token` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `tamadastiltas` | `alias` | `attack_restrict` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Hatascimkek` | `trap` | `invalid` | `-` | `none` | `yes` | `no` | No safe canonical mapping from the current standard. |
| `Hatascimkek` | `trap_immunity` | `standard` | `trap_immunity` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `tutor` | `standard` | `tutor` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `type_change` | `standard` | `type_change` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `untargetable` | `standard` | `untargetable` | `standard_doc` | `yes` | `no` | - |
| `Hatascimkek` | `visszavetelkezbe` | `alias` | `return_to_hand` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |

## Idotartam_Felismerve

| field_name | observed_value | value_type | canonical_value | source_of_mapping | used_in_loader | used_in_runtime | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Idotartam_Felismerve` | `a_kor_vegeig` | `alias` | `until_turn_end` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `allando` | `alias` | `until_match_end` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `azonnali` | `alias` | `instant` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `during_combat` | `standard` | `during_combat` | `standard_doc` | `yes` | `no` | - |
| `Idotartam_Felismerve` | `harc_idejere` | `alias` | `during_combat` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `harc_vegeig` | `alias` | `during_combat` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `instant` | `standard` | `instant` | `standard_doc` | `yes` | `no` | - |
| `Idotartam_Felismerve` | `kor_vegeig` | `alias` | `until_turn_end` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `kovetkezo_kor_vegeig` | `alias` | `until_next_own_turn_end` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `next_own_awakening` | `standard` | `next_own_awakening` | `standard_doc` | `yes` | `no` | - |
| `Idotartam_Felismerve` | `next_own_turn_start` | `standard` | `next_own_turn_start` | `standard_doc` | `yes` | `no` | - |
| `Idotartam_Felismerve` | `permanent` | `alias` | `until_match_end` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `static` | `alias` | `static_while_on_board` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `static_while_on_board` | `standard` | `static_while_on_board` | `standard_doc` | `yes` | `no` | - |
| `Idotartam_Felismerve` | `statikus` | `alias` | `static_while_on_board` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `trap` | `invalid` | `-` | `none` | `yes` | `no` | No safe canonical mapping from the current standard. Trap is not a duration. |
| `Idotartam_Felismerve` | `until_end_of_combat` | `alias` | `during_combat` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `until_end_of_next_own_turn` | `alias` | `until_next_own_turn_end` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `until_end_of_next_turn` | `alias` | `until_next_own_turn_end` | `loader_alias` | `yes` | `no` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `until_end_of_turn` | `alias` | `until_turn_end` | `loader_alias` | `yes` | `yes` | Can be normalized to the canonical standard value. |
| `Idotartam_Felismerve` | `until_match_end` | `standard` | `until_match_end` | `standard_doc` | `yes` | `no` | - |
| `Idotartam_Felismerve` | `until_next_enemy_turn` | `standard` | `until_next_enemy_turn` | `standard_doc` | `yes` | `no` | - |
| `Idotartam_Felismerve` | `until_next_own_turn_end` | `standard` | `until_next_own_turn_end` | `standard_doc` | `yes` | `no` | - |
| `Idotartam_Felismerve` | `until_turn_end` | `standard` | `until_turn_end` | `standard_doc` | `yes` | `no` | - |
| `Idotartam_Felismerve` | `while_active` | `standard` | `while_active` | `standard_doc` | `yes` | `no` | - |
