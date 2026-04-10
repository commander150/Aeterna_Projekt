# Trigger Compliance Audit

Scope: `Trigger_Felismerve`

Method:
- Canonical trigger list comes from [kartya_tabla_szabvany_frissett.md](/e:/Letöltések/Aeterna/Aeterna_Projekt/kartya_tabla_szabvany_frissett.md).
- Loader/validator acceptance is checked against [data/loader.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/data/loader.py) and [engine/card_metadata.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/engine/card_metadata.py).
- Runtime support is judged conservatively from actual dispatch/registration paths in [engine/game.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/engine/game.py), [engine/triggers.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/engine/triggers.py), [engine/keyword_engine.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/engine/keyword_engine.py), [cards/resolver.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/cards/resolver.py), [cards/priority_handlers.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/cards/priority_handlers.py), and related tests.
- Fresh runtime logs were also checked as secondary evidence. The latest sampled log family from April 10, 2026 still shows many trigger-heavy cards as `structured_deferred`, which supports conservative `partial` or `recognized_only` statuses for long-tail triggers.

Note: the standard document also allows `blank` as an explicit placeholder, but this audit only covers the actual canonical triggers themselves.

| trigger | in_standard_doc | accepted_by_loader | accepted_by_validator | aliases | runtime_supported | implementation_location | test_coverage | cards_using_it | current_status | exact_runtime_meaning | missing_parts | recommended_next_step |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `static` | yes | yes | yes | `none` | partial | `engine/card_metadata.py`, `engine/structured_effects.py`, `engine/keyword_engine.py`, `engine/game.py` | partial | `150 cards; examples: Hamvaskezű Újonc, Lángsörényű Oroszlán, Hamvaskezű Seregvezér, Vulkáni Gólem` | `partially_implemented` | The engine can store static metadata, apply some passive keyword states, and many simple static cards already work through combat or targeting code. | There is still no single generic static-effect executor that uniformly handles all non-keyword passive cards from structured metadata. | Keep using local handlers for proven passive patterns, then add a thin shared static pass for the simplest ATK/HP/zone-scoped effects. |
| `on_summon` | yes | yes | yes | `none` | yes | `engine/game.py`, `engine/triggers.py`, `cards/resolver.py`, `cards/priority_handlers.py`, `engine/keyword_engine.py` | good | `93 cards; examples: Parázsfarkas, Ignis Csonttörő, Tűzvihar Bajnoka, Élő Meteor` | `fully_working` | Summon flow dispatches `on_summon`, resolver and keyword handlers subscribe to it, and many Clarion/on-summon cards already resolve at runtime. | No major trigger-level gap found. Remaining gaps are card-effect-specific, not trigger-dispatch-specific. | Keep as the main reference trigger for event-driven entity abilities. |
| `on_death` | yes | yes | yes | `death`, `on_destroyed` | yes | `engine/card_metadata.py`, `engine/effects.py`, `engine/effect_diagnostics_v2.py`, `cards/resolver.py`, `cards/priority_handlers.py` | good | `53 cards; examples: Lángköpő Gyík, Tüzes Megtorlás, Füstbeburkolt Illúzió, Hamufőnix` | `fully_working` | Canonical `on_death` is normalized, then runtime death handling runs through the existing `on_destroyed` dispatch/adapter path and many concrete death cards are exercised by tests. | Canonical naming is still bridged through a legacy runtime event name, but the trigger is operational. | Keep as a reference for alias-normalized trigger support. |
| `on_attack_declared` | yes | yes | yes | `none` | yes | `engine/game.py`, `engine/triggers.py`, `cards/priority_handlers.py` | partial | `64 cards; examples: Lángoló Pörölyös, Vakmerő Hamuszóró, Hamvaskezű Kivégző, Parázs-Ork Martalóc` | `fully_working` | Combat flow dispatches `on_attack_declared` before combat resolution, and this already powers many trap and combat-reactive cards. | Test coverage is solid enough for combat traps, but not every attack-declared card family is covered generically. | Keep as a reference trigger; extend card coverage rather than changing the trigger model. |
| `on_attack_hits` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `19 cards; examples: Hullám-Parancsnok, Cunami Visszacsapás, Áramlat-táncos Pengemester, Zátony-Vívó` | `missing_implementation` | The spreadsheet and model can store the trigger, but no direct canonical `on_attack_hits` dispatch path was found in the runtime. | Missing post-hit event emission and missing shared payload for attacker, defender, and direct-hit outcome. | Add a thin post-hit combat dispatch after successful attack resolution. |
| `on_combat_damage_dealt` | yes | yes | yes | `none` | yes | `engine/keyword_engine.py`, `engine/triggers.py`, `engine/game.py`, `tests/test_keywords.py` | good | `13 cards; examples: Lángoló Öklű Bajnok, Vakmerő Hamuszóró, A Végtelen Harc Mezeje, Tengeri Baziliszkusz` | `fully_working` | `KeywordEngine.on_damage_dealt` emits `on_combat_damage_dealt`, and combat-result keywords already depend on this path. | No major trigger-level gap found. | Keep as a reference for combat-result triggers. |
| `on_combat_damage_taken` | yes | yes | yes | `legacy runtime: on_damage_taken` | partial | `engine/game.py`, `engine/effects.py`, `cards/resolver.py`, `cards/priority_handlers.py` | partial | `15 cards; examples: A Hamvaskezűek Arénája, Víz-Elementál Góliát, Életmentő Burok, Hullámtáncos Leviatán` | `partially_implemented` | Runtime damage paths emit the legacy `on_damage_taken` event, and some damage-reactive cards already use that route. | Canonical `on_combat_damage_taken` is not yet dispatched under its own name, and the current runtime path mixes combat and non-combat damage semantics. | Add a canonical adapter that emits `on_combat_damage_taken` only for combat-origin damage. |
| `on_block_survived` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `8 cards; examples: Vörösréz Pajzsos, Gyöngyvigyázó Papnő, Zátony-felderítő, Páncélos Vadkan` | `recognized_only` | The trigger is accepted structurally, but no dedicated survived-block dispatch was found. | Missing explicit block-survival event detection and missing standard payload for blocker/attacker/lane. | Add a small combat hook after block resolution for surviving blockers. |
| `on_damage_survived` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `2 cards; examples: Törp Lávakovács, Dühöngő Rozsomák` | `recognized_only` | The trigger is stored in metadata only. | Missing generic lethal-check outcome hook for "survived damage" semantics. | Delay until after `on_combat_damage_taken` and `on_block_survived` are canonicalized. |
| `on_enemy_spell_target` | yes | yes | yes | `on_spell_targeted` | yes | `engine/card_metadata.py`, `engine/effects.py`, `engine/game.py`, `cards/resolver.py`, `cards/priority_handlers.py`, `tests/test_structured_effects.py` | good | `13 cards; examples: Izzó Aura, Obszidián Gólem, Láng-Pajzs, Lángoló Tükör` | `fully_working` | Enemy spell targeting is normalized to the canonical trigger and routed through the existing spell-target reaction path; several trap/reaction cards already use it. | Canonical name still bridges to a legacy runtime label internally, but behavior is proven. | Keep as the reference trigger for spell-target reactions. |
| `on_enemy_spell_or_ritual_played` | yes | yes | yes | `legacy runtime: on_enemy_spell_played` | partial | `engine/game.py`, `engine/triggers.py`, `engine/structured_effects.py` | none | `15 cards; examples: Kirobbanó Rúna, Megtört Áramlat, Fagyos Tükröződés, Ragyogó Csapda` | `partially_implemented` | The engine has an enemy spell-play event family, so the runtime concept exists. | Canonical spell-or-ritual unification is not complete, and the current event naming does not cleanly cover both spell and ritual cards under one standard trigger. | Add a canonical adapter that emits one shared enemy-cast event for both spells and rituals. |
| `on_enemy_summon` | yes | yes | yes | `none` | yes | `engine/game.py`, `engine/triggers.py`, `cards/priority_handlers.py` | partial | `13 cards; examples: Csapda a Füstben, Csapda a Hamuban, Kagylócsapda, A Mélység Szeme` | `fully_working` | Summon flow dispatches `on_enemy_summon` with zone and summoner payload, and enemy-summon traps already consume that event. | No major trigger-level gap found. | Keep as the reference trigger for summon-reactive traps. |
| `on_enemy_zenit_summon` | yes | yes | yes | `none` | partial | `engine/game.py` | none | `1 card; example: Hamis Menedék` | `partially_implemented` | Enemy summon dispatch already includes `zone` in payload, so the raw information needed for a Zenit-only reaction exists. | There is no dedicated canonical `on_enemy_zenit_summon` emission or shared subscriber layer yet. | Route a filtered secondary dispatch from the existing summon payload when `zone == zenit`. |
| `on_enemy_extra_draw` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `5 cards; examples: Túlterhelt Elme, Kínok Hálója, Szélörvény, Informátor` | `recognized_only` | The trigger is present in structured data, but no dedicated extra-draw event dispatch was found. | Missing draw instrumentation that distinguishes normal awakening draw from extra draw. | Add a generic draw event payload with `is_extra_draw` metadata. |
| `on_enemy_third_draw_in_turn` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `1 card; example: Túlhevült Mana` | `recognized_only` | The trigger is only recognized by the loader and validator. | Missing per-turn enemy draw counters and missing threshold event dispatch. | Implement only after a generic draw-event layer exists. |
| `on_turn_end` | yes | yes | yes | `none` | yes | `engine/game.py`, `engine/triggers.py`, `cards/resolver.py`, `cards/priority_handlers.py`, `tests/test_priority_handlers.py`, `tests/test_game_flow.py` | good | `12 cards; examples: Lángoló Elme, Yggdrasil Sarja, Földsárkány Fióka, Szent Druida-Liget` | `fully_working` | Turn flow dispatches `on_turn_end`, and multiple temporary buffs/cleanup effects already rely on it. | No major trigger-level gap found. | Keep as a reference for timed cleanup and delayed-until-end-of-turn behavior. |
| `on_next_own_awakening` | yes | yes | yes | `legacy runtime: on_awakening_phase` | partial | `engine/game.py`, `engine/triggers.py`, `cards/resolver.py`, `cards/priority_handlers.py` | partial | `8 cards; examples: Atlantisz Utolsó Királya, A Változó Sziget, Napfény-Gyűjtő, Lovagrendi Gyógyító` | `partially_implemented` | Own awakening phase already exists at runtime and is dispatched through a legacy event name. | Canonical delayed scheduling for "next own awakening" is not unified; current support is card-specific or phase-based. | Add a canonical delayed-effect scheduler keyed to the next awakening phase. |
| `on_influx_phase` | yes | yes | yes | `legacy runtime: on_manifestation_phase`, `legacy internal: on_infusion_phase` | partial | `engine/game.py`, `engine/triggers.py`, `engine/structured_effects.py` | none | `19 cards; examples: Az Örök Tűz Szentélye, Óceáni Sámán, Illúzió-Szirén, Mélységi Szirén` | `partially_implemented` | The phase exists in runtime under the legacy manifestation-phase naming. | Canonical naming is not yet aligned, and there is no broad standard trigger routing under `on_influx_phase`. | Add a canonical phase alias/adapter first; then revisit card coverage. |
| `on_heal` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `3 cards; examples: Az Őstenger Akarata, A Korallzátony Szíve, Természet-Alakító` | `recognized_only` | The trigger is accepted structurally only. | Missing heal event emission from generic healing logic. | Add a generic heal hook with healed amount and source. |
| `on_enemy_ability_activated` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `4 cards; examples: Korall-csapda, Méregtövis, A Hallgatás Ára, Kettős Ügynök` | `recognized_only` | The trigger is stored, but no generic enemy ability-activation bus was found. | Missing unified "ability activation" definition, dispatch timing, and payload. | Delay until spell/trap/activated-ability routing is standardized. |
| `on_enemy_multiple_draws` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `2 cards; examples: Árapály-visszacsapás, Alvilági Csempész` | `recognized_only` | Metadata recognizes the trigger, but runtime does not yet track grouped enemy draw activity as a shared event. | Missing draw counters and multi-draw aggregation logic. | Add after basic draw event infrastructure exists. |
| `on_enemy_horizont_threshold` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `1 card; example: Átkozott Örvény` | `recognized_only` | The trigger is currently only a structured-data token. | Missing threshold watcher for enemy Horizont occupancy or similar board-count thresholds. | Add only when there are enough cards to justify a shared watcher. |
| `on_move_zenit_to_horizont` | yes | yes | yes | `partial legacy evidence: on_position_changed` | partial | `engine/actions.py`, `cards/priority_handlers.py`, `engine/structured_effects.py`, `engine/triggers.py` | none | `12 cards; examples: Örvény-Vadász, Hullámtörő Admirális, A Szüntelen Áramlások Folyója, Tengeri Szélcsatorna` | `partially_implemented` | Runtime already emits `on_position_changed` with `from` and `to` zone data, including Zenit/Horizont movement. | Canonical movement-specific dispatch is not emitted directly, so cards still need local filtering or custom handling. | Add a thin canonical movement adapter based on the existing position-change payload. |
| `on_leave_board` | yes | yes | yes | `partial legacy evidence: on_destroyed`, `on_position_changed` | partial | `engine/effects.py`, `engine/actions.py`, `cards/priority_handlers.py` | none | `4 cards; examples: Az Elveszett Áramlatok Csatornája, Hitbuzgó Zarándok, A Szent Sírbolt, Éjfattyú` | `partially_implemented` | Pieces of leave-board semantics already exist through death and movement paths. | There is no single canonical leave-board dispatch that covers destroy, bounce, return, and relocation consistently. | Add one shared leave-board event after movement and death adapters are stabilized. |
| `on_spell_cast_by_owner` | yes | yes | yes | `partial legacy evidence: on_play` | partial | `engine/game.py`, `engine/effect_diagnostics_v2.py`, `engine/structured_effects.py` | none | `9 cards; examples: Parázsló Tanítvány, Parázstáncos Nővér, Vulkáni Orákulum, A Katlan Őrzője` | `partially_implemented` | Spell play exists at runtime, and diagnostics already classify on-play spell resolution. | Owner-scoped canonical trigger dispatch is not unified and currently leans on older on-play terminology. | Add a canonical owner-cast adapter on top of spell play resolution. |
| `on_position_swap` | yes | yes | yes | `legacy runtime: on_position_changed` | partial | `engine/actions.py`, `cards/priority_handlers.py`, `engine/structured_effects.py`, `engine/triggers.py` | none | `6 cards; examples: Mélységi Áramlás-formáló, Zátony-Lopakodó, Mélytengeri Karmester, Hablovas Hírnök` | `partially_implemented` | Position changes are emitted with before/after zone data, and swap-like actions already exist. | Canonical swap-specific dispatch and payload are missing; current behavior is inferred from generic position changes. | Add a swap-specific adapter on top of `on_position_changed`. |
| `on_entity_enters_horizont` | yes | yes | yes | `partial legacy evidence: on_position_changed` | partial | `engine/actions.py`, `cards/priority_handlers.py`, `engine/structured_effects.py` | none | `1 card; example: Medúza-Idomár` | `partially_implemented` | The movement layer already knows when something moves into Horizont. | No canonical direct dispatch exists yet, so card support would still require local filtering. | Add as part of the same movement-adapter pass as `on_move_zenit_to_horizont`. |
| `on_source_placement` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `0 cards` | `recognized_only` | The trigger is allowed by the standard and accepted by the data layer. | No observed cards currently use it, and no runtime dispatch was found. | Leave as recognized-only until cards actually require it. |
| `on_seal_break` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py`, `engine/game.py` | none | `14 cards; examples: Füst-Tolvaj, Visszacsapó Hullám, Tengeri Áldozat, Földrengés-Orrszarvú` | `recognized_only` | Seal breaking clearly exists as gameplay, but no dedicated canonical `on_seal_break` event dispatch was found. | Missing event emission when a seal is actually broken and missing standard payload for breaker/source/owner. | Add a post-seal-break dispatch where seal damage is resolved. |
| `on_bounce` | yes | yes | yes | `partial legacy evidence: on_position_changed` | partial | `engine/actions.py`, `cards/priority_handlers.py`, `engine/structured_effects.py` | none | `9 cards; examples: Tengeri Császár, Viharhozó Dobos, A Végtelen Viharok Fennsíkja, Felhőtáncos Szirén` | `partially_implemented` | Return-to-hand movement exists and the generic position-change path can already observe it. | There is no canonical bounce event emitted directly, so bounce-reactive cards still need extra local logic. | Emit a canonical `on_bounce` adapter whenever board-to-hand movement succeeds. |
| `on_trap_triggered` | yes | yes | yes | `none` | partial | `engine/game.py`, `engine/effects.py`, `cards/priority_handlers.py` | none | `6 cards; examples: Árnyba Burkolt Kém, Alvilági Pénzmosó, Suttogó Démon, Éjszakai Besúgó` | `partially_implemented` | Trap runtime definitely exists and traps resolve in logs and tests. | The missing piece is a dedicated trigger event for "a trap has just triggered"; current code resolves traps but does not expose that as a clean canonical subscriber event. | Add a post-trap-resolution dispatch without changing trap framework behavior. |
| `on_ready_from_exhausted` | yes | yes | yes | `on_ready` | no | `engine/card_metadata.py`, `data/loader.py` | none | `8 cards; examples: Ciklonlovas Cserkész, Villámlépésű Kardforgató, Villámvágta Huszár, Szelek Suttogója` | `recognized_only` | The canonical trigger is normalized and stored, but no proven runtime dispatch for this exact event was found. | Missing ready-event emission that distinguishes ordinary readying from readying specifically from exhausted state. | Add a targeted dispatch inside the existing ready/reactivate helpers. |
| `on_stat_gain` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `10 cards; examples: Fényhozó Apród, Hajnalpír Papnő, Naphívó Zászlós, Pajzshordozó Templomos` | `recognized_only` | The trigger is recognized by the data layer only. | Missing shared stat-modification event emission for ATK/HP gain. | Add a generic stat-change hook only after buff/debuff application is more centralized. |
| `on_gain_keyword` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `1 card; example: Talizmán-Árus` | `recognized_only` | The trigger exists in metadata only. | Missing keyword-grant event emission for temporary and permanent keyword gains. | Add later together with a shared grant/remove-keyword helper. |
| `on_destroy` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `7 cards; examples: Törzsi Fővadász, Apex Tyrannus, Felbőszített Anyaállat, Véráztatta Vadászterület` | `recognized_only` | The runtime has death handling, but no distinct canonical destroy-event bus separate from death. | Missing separation between "was destroyed" and broader "died/left board" semantics. | Decide first whether `on_destroy` should be a canonical subset of death, then emit it from destroy-only paths. |
| `on_discard` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `1 card; example: Az Elfeledett Katakombák` | `recognized_only` | The trigger is accepted by the structured pipeline only. | Missing discard event dispatch and discard-origin payload. | Add only after hand/discard mechanics are instrumented more consistently. |
| `on_enemy_card_played` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `1 card; example: Váratlan Adóellenőrzés` | `recognized_only` | The standard trigger exists, but no unified enemy-card-played event was found. | Missing aggregation over enemy spell, ritual, summon, trap, and field plays into one canonical event. | Add only if multiple cards need the broad event rather than narrower existing ones. |
| `on_enemy_second_summon_in_turn` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `1 card; example: Kereskedelmi Embargó` | `recognized_only` | The trigger is structurally valid, but the runtime currently has no enemy summon-count threshold event. | Missing per-turn enemy summon counters and threshold dispatch. | Add after generic summon counters are exposed. |
| `on_start_of_turn` | yes | yes | yes | `legacy runtime: on_turn_start` | partial | `engine/game.py`, `engine/triggers.py` | none | `1 card; example: Éjszakai Piac` | `partially_implemented` | Turn start already exists in runtime under the legacy `on_turn_start` name. | Canonical trigger naming is not yet aligned and subscriber coverage is sparse. | Add a canonical start-of-turn adapter before implementing more cards on top of it. |

## Summary

### Actually working

- `on_summon`
- `on_death`
- `on_attack_declared`
- `on_combat_damage_dealt`
- `on_enemy_spell_target`
- `on_enemy_summon`
- `on_turn_end`

### Recognized only

- `on_block_survived`
- `on_damage_survived`
- `on_enemy_extra_draw`
- `on_enemy_third_draw_in_turn`
- `on_heal`
- `on_enemy_ability_activated`
- `on_enemy_multiple_draws`
- `on_enemy_horizont_threshold`
- `on_source_placement`
- `on_seal_break`
- `on_ready_from_exhausted`
- `on_stat_gain`
- `on_gain_keyword`
- `on_destroy`
- `on_discard`
- `on_enemy_card_played`
- `on_enemy_second_summon_in_turn`

### Partial

- `static`
- `on_combat_damage_taken`
- `on_enemy_spell_or_ritual_played`
- `on_enemy_zenit_summon`
- `on_next_own_awakening`
- `on_influx_phase`
- `on_move_zenit_to_horizont`
- `on_leave_board`
- `on_spell_cast_by_owner`
- `on_position_swap`
- `on_entity_enters_horizont`
- `on_bounce`
- `on_trap_triggered`
- `on_start_of_turn`

### Missing

- `on_attack_hits`

## Best implementation order

1. `on_combat_damage_taken`
   Reason: runtime already has `on_damage_taken`; a canonical adapter would unlock several cards with low risk.
2. `on_start_of_turn`
   Reason: the phase already exists as `on_turn_start`; this is mostly naming and routing cleanup.
3. `on_next_own_awakening`
   Reason: awakening phase already exists; delayed scheduling is the main missing piece.
4. `on_move_zenit_to_horizont`
   Reason: movement payload already exists through `on_position_changed`; a thin adapter is plausible.
5. `on_seal_break`
   Reason: seal breaking already happens in gameplay, but the event itself is not exposed canonically.
6. `on_attack_hits`
   Reason: this is the clearest truly missing combat trigger and needs one explicit post-hit dispatch point.
