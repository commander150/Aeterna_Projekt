# Szabvány ↔ engine megfelelőségi audit

Forrás: `cards.xlsx` és a jelenlegi élő kód.

## Döntési kategóriák

- `teljesen támogatott`
- `részben támogatott`
- `beköthető kis módosítással`
- `új engine-logikát igényel`

## Zóna_Felismerve

| Elem | Besorolás | Bizonyíték | Megjegyzés |
| --- | --- | --- | --- |
| `horizont` | teljesen támogatott | `engine/game.py`, `engine/actions.py`, `engine/structured_effects.py` | A core harc- és zónalogika explicit Horizont-támogatással fut. |
| `dominium` | részben támogatott | `engine/game.py`, `cards/priority_handlers.py` | A Domínium több helyen összefoglaló fogalomként szerepel, de nem minden effect-route használ explicit dominium-szűrést. |
| `zenit` | teljesen támogatott | `engine/game.py`, `engine/actions.py`, `engine/structured_effects.py` | A Zenit zóna külön sorlogikával és mozgással támogatott. |
| `deck` | teljesen támogatott | `engine/player.py`, `engine/structured_effects.py` | Pakli tetejére helyezés és húzás támogatott. |
| `seal_row` | teljesen támogatott | `engine/game.py`, `engine/effects.py` | Pecsét-sor és direkt Pecsét-sebzés támogatott. |
| `graveyard` | teljesen támogatott | `engine/actions.py`, `cards/priority_handlers.py` | Temető/Üresség alapú mozgatások és recursion már léteznek. |
| `aeternal` | részben támogatott | `engine/game.py`, `engine/effects.py` | A játékos/Aeternal közvetlen sebzése megvan, de nem minden célzás routolt explicit `aeternal` tokenre. |
| `hand` | teljesen támogatott | `engine/actions.py`, `engine/player.py` | Kézbe visszavétel és húzás támogatott. |
| `source` | teljesen támogatott | `engine/player.py`, `cards/priority_handlers.py` | Ősforrás/Aura kezelés külön runtime-logikával él. |
| `burst` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `lane` | beköthető kis módosítással | `engine/game.py`, `engine/actions.py` | Az áramlat/lane index a motorban implicit jelen van, de kevés helyen strukturált mezőből vezetett. |
| `from hand` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |

## Kulcsszavak_Felismerve

| Elem | Besorolás | Bizonyíték | Megjegyzés |
| --- | --- | --- | --- |
| `celerity` | teljesen támogatott | `engine/keyword_engine.py`, `engine/card.py` | Gyorsaság belépéskor azonnal feloldja a kimerülést. |
| `sundering` | teljesen támogatott | `engine/keyword_engine.py`, `engine/game.py` | Hasítás extra pecséttörés útvonallal támogatott. |
| `clarion` | részben támogatott | `engine/effect_diagnostics_v2.py`, `cards/resolver.py` | Több Clarion lap explicit kezelt, de nem minden Clarion generic keywordként oldódik fel. |
| `aegis` | teljesen támogatott | `engine/keyword_engine.py`, `engine/targeting.py`, `engine/game.py` | Blokkolási és célzási következményekkel együtt kezelt keyword. |
| `bane` | teljesen támogatott | `engine/keyword_engine.py` | Sebzés utáni megjelölés és megsemmisítés támogatott. |
| `echo` | részben támogatott | `engine/keyword_engine.py`, `cards/resolver.py` | Van death-route és több explicit handler, de nem minden Echo teljesen generikus. |
| `ethereal` | teljesen támogatott | `engine/keyword_engine.py`, `engine/targeting.py` | Légi/ethereal blokkolási és célzási korlátok támogatottak. |
| `taunt` | beköthető kis módosítással | `engine/keyword_engine.py`, `engine/game.py` | A kötelező célzás logikája még nincs explicit keywordként végigvezetve. |
| `burst` | részben támogatott | `engine/effect_diagnostics_v2.py`, `cards/resolver.py` | Burst runtime-ban kezelt, de szabálykönyvileg Surge-kapcsolt és nem mindenhol teljesen generic. |
| `harmonize` | teljesen támogatott | `engine/keyword_engine.py`, `engine/game.py` | Harmonize bonusz explicit runtime függvénnyel kezelt. |
| `resonance` | teljesen támogatott | `engine/keyword_engine.py`, `engine/player.py` | Rezonancia támadásmódosítóként támogatott. |
| `trap` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |

## Trigger_Felismerve

| Elem | Besorolás | Bizonyíték | Megjegyzés |
| --- | --- | --- | --- |
| `static` | teljesen támogatott | `engine/structured_effects.py`, `engine/effect_diagnostics_v2.py` | Passzív/statikus lapok elkülönítése megvan. |
| `on_combat_damage_dealt` | teljesen támogatott | `engine/keyword_engine.py`, `engine/triggers.py` | Külön trigger dispatch létezik. |
| `on_attack_declared` | teljesen támogatott | `engine/game.py`, `cards/priority_handlers.py` | Támadásdeklarációs csapdák és reakciók működnek. |
| `on_summon` | teljesen támogatott | `engine/triggers.py`, `engine/game.py`, `cards/priority_handlers.py` | Summon dispatch és runtime routing támogatott. |
| `on_block_survived` | részben támogatott | `engine/keyword_engine.py` | Első túlélés/combat survived részben támogatott, de nem teljes generic blokktúlélési trigger. |
| `on_destroyed` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_damage_survived` | részben támogatott | `engine/effects.py`, `cards/priority_handlers.py` | Damage-survive jellegű állapot levezethető, de nincs egységes generic routing. |
| `on_enemy_summon` | teljesen támogatott | `engine/game.py`, `cards/priority_handlers.py` | Ellenséges idézésre reagáló dispatch létezik. |
| `on_enemy_spell_target` | teljesen támogatott | `engine/game.py`, `cards/priority_handlers.py` | Spell-target reakciók explicit útvonallal támogatottak. |
| `on_combat_damage_taken` | beköthető kis módosítással | `engine/triggers.py`, `engine/effects.py` | Sebzés payload rendelkezésre áll, de kevés explicit consumer használja. |
| `on_spell_cast_by_owner` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_turn_end` | teljesen támogatott | `engine/game.py` | Kör végi cleanup és időzített buffok támogatottak. |
| `on_seal_break` | részben támogatott | `engine/game.py` | Surge/Burst alaphelyzet megvan, de nem minden seal-break trigger generic. |
| `on_enemy_extra_draw` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_enemy_spell_or_ritual_played` | beköthető kis módosítással | `engine/effect_diagnostics_v2.py`, `cards/resolver.py` | Spell/ritual kategória részben routolható, de nincs mindenhol egységes esemény. |
| `on_enemy_third_draw_in_turn` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_enemy_zenit_summon` | beköthető kis módosítással | `engine/game.py` | A summon payloadban zóna adott, de kevés explicit trap/handler használja generikusan. |
| `on_influx_phase` | beköthető kis módosítással | `engine/game.py` | Beáramlás fázis létezik, de kevés strukturált effect route használja. |
| `on_bounce` | beköthető kis módosítással | `engine/actions.py`, `cards/priority_handlers.py` | Kézbe visszavétel van, bounce event kevésbé egységes. |
| `on_heal` | beköthető kis módosítással | `engine/structured_effects.py` | Gyógyítás támogatott, de heal-trigger routing nem teljes. |
| `on_attack_hits` | részben támogatott | `engine/game.py` | Betörés és találat útvonal megvan, de nincs teljes generic trigger routing. |
| `on_next_own_awakening` | beköthető kis módosítással | `engine/game.py` | Körfázisok adottak, de következő saját ébredésre célzott markerkezelés még nem egységes. |
| `on_position_swap` | beköthető kis módosítással | `engine/actions.py`, `engine/triggers.py` | Pozícióváltás trigger dispatch létezik, de kevés explicit subscriberrel. |
| `on_move_zenit_to_horizont` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_entity_enters_horizont` | beköthető kis módosítással | `engine/actions.py`, `engine/game.py` | Zónamozgásból levezethető. |
| `on_enemy_ability_activated` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_enemy_multiple_draws` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_enemy_horizont_threshold` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_leave_board` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_destroy` | teljesen támogatott | `engine/effects.py`, `engine/triggers.py`, `cards/priority_handlers.py` | Megsemmisítés és halál trigger útvonal támogatott. |
| `on_play` | teljesen támogatott | `cards/resolver.py`, `engine/effect_diagnostics_v2.py` | On-play handler routing stabil. |
| `on_burst` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_stat_gain` | új engine-logikát igényel | `engine/triggers.py` | Stat gain routing nincs explicit globális triggerként felépítve. |
| `on_lane_filled` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_trap_triggered` | beköthető kis módosítással | `engine/game.py`, `cards/priority_handlers.py` | Trap fogyasztási pontok adottak, de külön meta-trigger nincs végigkötve. |
| `on_enemy_card_played` | beköthető kis módosítással | `engine/game.py` | Kijátszási pontok felismerhetők, de nincs teljesen közös esemény minden laptípusra. |
| `on_start_of_turn` | teljesen támogatott | `engine/game.py` | Turn start/awakening fázis explicit. |
| `on_discard` | beköthető kis módosítással | `engine/player.py`, `cards/priority_handlers.py` | Dobatás részben van, discard-trigger routing nem egységes. |
| `on_graveyard_recursion` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_infusion_phase` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_ready_from_exhausted` | beköthető kis módosítással | `engine/game.py`, `engine/player.py` | Újraaktiválási limit és állapot van, de nincs külön generic esemény. |
| `on_ready` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_enemy_manifestation_start` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `on_gain_keyword` | beköthető kis módosítással | `cards/priority_handlers.py` | Ideiglenes keyword-adás támogatott, de esemény-dispatch nem egységes. |
| `on_enemy_second_summon_in_turn` | új engine-logikát igényel | `engine/game.py` | Turn-scoped summon számláló nincs általánosan modellezve. |

## Célpont_Felismerve

| Elem | Besorolás | Bizonyíték | Megjegyzés |
| --- | --- | --- | --- |
| `self` | teljesen támogatott | `cards/priority_handlers.py` | Önmagára ható route több helyen explicit. |
| `enemy_horizont_entity` | teljesen támogatott | `engine/structured_effects.py`, `engine/effects.py` | Ellenséges Horizont célzás támogatott. |
| `enemy_entity` | teljesen támogatott | `engine/effects.py`, `engine/structured_effects.py` | Általános ellenséges entitás célzás támogatott. |
| `other_own_entity` | teljesen támogatott | `cards/priority_handlers.py` | Másik saját entitás választása explicit mintákkal megoldott. |
| `own_horizont_entities` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `enemy_zenit_entity` | részben támogatott | `engine/structured_effects.py`, `engine/game.py` | Zenit-célzás részben támogatott. |
| `own_entities` | teljesen támogatott | `cards/priority_handlers.py`, `engine/actions.py` | Tömeges saját entitás iteráció adott. |
| `enemy_entities` | teljesen támogatott | `engine/structured_effects.py`, `engine/actions.py` | Tömeges ellenséges entitás iteráció adott. |
| `enemy_horizont_entities` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `own_horizont_entity` | teljesen támogatott | `engine/structured_effects.py`, `cards/priority_handlers.py` | Saját Horizont célzás támogatott. |
| `enemy_seal` | teljesen támogatott | `engine/effects.py`, `engine/game.py` | Direkt Pecsét-sebzés és betörés támogatott. |
| `own_entity` | teljesen támogatott | `engine/structured_effects.py`, `cards/priority_handlers.py` | Saját entitás célzás széles körben támogatott. |
| `enemy_aeternal` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `own_hand` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `own_graveyard_entity` | részben támogatott | `cards/priority_handlers.py`, `engine/actions.py` | Temetőből visszahozás és válogatás részben támogatott. |
| `enemy_zenit_entities` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `own_seal` | részben támogatott | `engine/game.py` | Saját Pecsét sor elérhető, de kevés explicit saját-pecsét célzó route van. |
| `lane` | beköthető kis módosítással | `engine/game.py`, `engine/actions.py` | Lane index a motorban él, de célpont-szinten nem egységesen modellezett. |
| `own_zenit_entity` | részben támogatott | `cards/priority_handlers.py`, `engine/actions.py` | Zenit-entitások kezelhetők, de nem minden generic célzás fedett. |
| `enemy_spell_or_ritual` | beköthető kis módosítással | `engine/game.py`, `cards/priority_handlers.py` | Kategória részben elérhető, egységesítés kell. |
| `own_zenit_entities` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `enemy_hand` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `enemy_spell` | teljesen támogatott | `engine/game.py`, `cards/priority_handlers.py` | Spell-target reakciók explicit úton működnek. |
| `own_aeternal` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `own_deck` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `own_source_card` | részben támogatott | `engine/player.py` | Ősforrás lapok kezelése megvan, de célzásuk nem teljesen általános. |
| `opposing_entity` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `opponent` | teljesen támogatott | `engine/effects.py`, `engine/game.py` | Ellenfél/Aeternal közvetlen célpont támogatott. |
| `own_graveyard` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `source_card` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `enemy_hand_card` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `own_face_down_trap` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `enemy_face_down_trap` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `enemy_source_card` | beköthető kis módosítással | `engine/player.py`, `cards/priority_handlers.py` | Forrás-zóna hozzáférhető, de kevés explicit target route van. |

## Hatáscímkék

| Elem | Besorolás | Bizonyíték | Megjegyzés |
| --- | --- | --- | --- |
| `heal` | teljesen támogatott | `engine/structured_effects.py`, `cards/priority_handlers.py` | Gyógyítás támogatott. |
| `grant_attack` | teljesen támogatott | `cards/priority_handlers.py`, `engine/structured_effects.py` | ATK-bónusz támogatott. |
| `exhaust` | teljesen támogatott | `engine/structured_effects.py`, `engine/game.py` | Kimerítés támogatott. |
| `damage` | teljesen támogatott | `engine/effects.py`, `engine/structured_effects.py`, `cards/priority_handlers.py` | Célzott sebzés központi pipeline-on megy. |
| `grant_hp` | részben támogatott | `cards/priority_handlers.py`, `engine/structured_effects.py` | HP-bónusz támogatott, de életciklus és cleanup nem mindenhol egységes. |
| `attack_restrict` | részben támogatott | `engine/game.py`, `cards/priority_handlers.py` | Támadástiltás van, de nem minden mintára egységes. |
| `summon` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `damage_prevention` | részben támogatott | `engine/effects.py`, `cards/priority_handlers.py` | Sebzésmegelőzés több lokális mintával működik. |
| `grant_keyword` | részben támogatott | `cards/priority_handlers.py`, `engine/keyword_engine.py` | Ideiglenes kulcsszóadás több helyen van, de nem teljesen generikus. |
| `block_restrict` | beköthető kis módosítással | `engine/keyword_engine.py`, `engine/game.py` | Blokkolási tiltás részben levezethető, de külön generic pipeline gyenge. |
| `sacrifice` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `draw` | teljesen támogatott | `engine/player.py`, `engine/structured_effects.py` | Húzás és extra húzás támogatott. |
| `seal_damage` | teljesen támogatott | `engine/effects.py`, `engine/game.py` | Direkt Pecsét-sebzés támogatott. |
| `destroy` | teljesen támogatott | `engine/effects.py`, `engine/structured_effects.py` | Megsemmisítés támogatott. |
| `redirect` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `counterspell` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `summon_restrict` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `cost_mod` | részben támogatott | `engine/player.py`, `cards/priority_handlers.py` | Költségmódosítás részben támogatott, de nem teljesen általános. |
| `resource_gain` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `move_zenit` | teljesen támogatott | `engine/actions.py`, `engine/structured_effects.py` | Zenitbe mozgatás támogatott. |
| `untargetable` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `free_cast` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `discard` | részben támogatott | `cards/priority_handlers.py` | Dobatás több lokális handlerben megvan, de nincs teljesen generikus pipeline. |
| `damage_bonus` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `graveyard_recursion` | részben támogatott | `engine/actions.py`, `cards/priority_handlers.py` | Visszahozás és temető-interakció több helyen működik. |
| `source_manipulation` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `move_horizont` | teljesen támogatott | `engine/actions.py`, `engine/structured_effects.py` | Horizontra mozgatás támogatott. |
| `random_discard` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `move_to_source` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `ability_lock` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `return_to_hand` | teljesen támogatott | `engine/actions.py`, `engine/structured_effects.py` | Kézbe visszavétel támogatott. |
| `deck_bottom` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `attack_nullify` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `copy_stats` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `copy_keywords` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `control_change` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `cleanse` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `tutor` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `return_to_deck` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `position_lock` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `reveal` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `once_per_turn` | új engine-logikát igényel | `engine/game.py` | Általános turn-scoped once-per-turn state nincs egységesen modellálva. |
| `trap` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `reactivate` | teljesen támogatott | `engine/player.py`, `engine/structured_effects.py` | Újraaktiválás támogatott. |
| `effect_reduction` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `reflect_damage` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `retaliation_damage` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `choice` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `end_turn` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `delayed_revival` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `return_to_deck_bottom` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `overflow_damage` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `type_change` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `stat_reset` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `resource_spend` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `resource_acceleration` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `graveyard_replacement` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `trap_immunity` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `resource_drain` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |

## Időtartam_Felismerve

| Elem | Besorolás | Bizonyíték | Megjegyzés |
| --- | --- | --- | --- |
| `static` | részben támogatott | `engine/structured_effects.py`, `engine/effect_diagnostics_v2.py` | Passzív/statikus lapok felismerése megvan, de nem mind explicit szimulált. |
| `instant` | teljesen támogatott | `engine/effect_diagnostics_v2.py`, `cards/resolver.py` | Azonnali kijátszású hatások támogatottak. |
| `until_end_of_combat` | teljesen támogatott | `engine/game.py`, `engine/structured_effects.py` | Harc végi buff-cleanup támogatott. |
| `permanent` | részben támogatott | `cards/priority_handlers.py`, `engine/card.py` | Állandó buffok és max HP növelések több helyen megvannak, de nincs egységes permanens effect réteg. |
| `until_end_of_turn` | teljesen támogatott | `engine/game.py`, `cards/priority_handlers.py` | Kör végi cleanup széles körben támogatott. |
| `until_next_enemy_turn` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `until_end_of_next_own_turn` | részben támogatott | `cards/priority_handlers.py` | Van rá lokális minta, de még nincs teljesen általános időzítés-réteg. |
| `next_own_awakening` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `next_own_turn_start` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |
| `trap` | beköthető kis módosítással | `cards/resolver.py` | Nincs külön explicit besorolás, de a jelenlegi rendszerhez adapterezhetőnek tűnik. |

## Feltétel_Felismerve minták

| Minta | Darab | Besorolás | Megjegyzés |
| --- | --- | --- | --- |
| `simple_other` | `483` | beköthető kis módosítással | Egyszerű feltételadapterrel levezethető. |
| `lane_dependent` | `17` | beköthető kis módosítással | Lane index rendelkezésre áll, explicit routing kell. |
| `aura_state_dependent` | `23` | részben támogatott | Aura/rezonancia feltételek részben kezeltek. |
| `seal_state` | `41` | részben támogatott | Pecsétállapot kezelhető, de nem minden csomópont routolt. |
| `graveyard_state` | `41` | részben támogatott | Temető állapot elérhető, de nem minden feltétel generikus. |
| `next_turn_effect` | `13` | részben támogatott | Vannak next-turn flag-ek, de nincs teljes általános scheduler. |
| `nth_time_in_turn` | `15` | új engine-logikát igényel | Általános turn-scoped eseményszámláló kell hozzá. |

## Külön nehéz mechanikák

| Mechanika | Besorolás | Megjegyzés |
| --- | --- | --- |
| `delayed revival` | részben támogatott | Van temetőből visszahozás, de késleltetett időzítés nem teljesen generikus. |
| `next-turn effects` | részben támogatott | Vannak lokális next-turn flag-ek, de nincs teljes általános scheduler. |
| `multi-phase / second combat phase logic` | új engine-logikát igényel | A körfázisok egyszeriek, második harcfázis nincs modellálva. |
| `attack nullification` | részben támogatott | Trap és combat flag-ekkel több helyen működik, de nem teljesen általános. |
| `redirect` | részben támogatott | Van több lokális redirect trap, de nincs teljes generic átirányítási rendszer. |
| `bounce with compensation` | beköthető kis módosítással | Bounce és plusz húzás/sebzés már meglévő primitívekkel összerakható. |
| `cost tax` | beköthető kis módosítással | Cost mod útvonal adott, csak ellenfél-adó jellegű routing kell. |
| `aura-state dependent conditions` | részben támogatott | Rezonancia és aura-limit jelen van, de nem minden feltétel generic. |
| `full lane swap logic` | új engine-logikát igényel | Komplex teljes pályasorrend-csere nincs egységesen kezelve. |
| `enemy forced movement` | részben támogatott | Mozgatás van, de összetettebb ellenfél-kényszerített átrendezés már nehezebb. |
| `board-wide rearrangement` | új engine-logikát igényel | Teljes táblarendezés nincs meg. |
| `first time this turn / second summon this turn / third draw this turn` | új engine-logikát igényel | Néhány limit van, de általános számláló-réteg nincs. |
| `spell metadata driven effects` | beköthető kis módosítással | A strukturált mezők már elérhetők, további routing kell. |
| `source manipulation` | részben támogatott | Ősforrás hozzáférés van, de komplex source-manipulation még nem teljes. |
| `seal restoration` | beköthető kis módosítással | Pecsétsor modell adott, visszaállítás csak részben explicit. |
| `temporary control change` | új engine-logikát igényel | Tulajdonos/kontroll váltás nincs egységesen modellálva. |
| `top/bottom deck placement` | részben támogatott | Pakli teteje adott, alja nincs teljesen általános útvonalon. |
| `out-of-combat mutual damage` | beköthető kis módosítással | Sebzéspipeline adott, csak új routing kell. |
| `conditional replacement effects` | új engine-logikát igényel | Would/Instead replacement réteg nincs. |
| `"would die instead..." prevention/replacement` | új engine-logikát igényel | Halál-helyettesítő effekt-réteg nincs egységesen jelen. |
