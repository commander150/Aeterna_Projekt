# AETERNA 1.8v – javított exportok újraellenőrzése és LOOKUPS-fókuszú javaslat

## Feldolgozott javított exportok

- 1. VERZIÓ: 32 sor
- 10. IMPORT_ORIGINAL: 814 sor
- 11. SETS: 3 sor
- 12. PRODUCTS: 22 sor
- 13. CARD_PRINTINGS: 3 sor
- 14. GENERATION_PROFILES: 5 sor
- 15. PRODUCT_DECKLISTS: 754 sor
- 17. NAME_PROFILE: 814 sor
- 3. CARDS_MASTER: 814 sor
- 4. AUDIT_LOG: 185 sor
- 5. LOOKUPS: 29 sor
- 6. RARITY_CODES: 6 sor
- 8. EXPORT_NOTES: 1 sor
- 9. DECISION_LOG: 133 sor

## Rövid eredmény

- A korábbi AETHER Rarity U/UC hiba a javított exportban már nem látható.
- A fő CARDS_MASTER → LOOKUPS alapértékek közül a laptípus, birodalom, klán, faj, kaszt, audit státusz, rarity, treatment, art variant, print status és play legal status jelenleg lefedett.
- A LOOKUPS viszont továbbra sem tartalmaz külön structured mezőérték-listákat, miközben a 7. EXPORT_RUNTIME lesz a program tényleges kártyalistája. Ez a legfontosabb szerkezeti irány.

## Fő nyitott issue-k

### P1 – NAME_PROFILE: NAME_PROFILE mezők eltérnek a CARDS_MASTER-től

- Darab: 78
- Státusz: nyitott
- Javaslat: NAME_PROFILE mezőket frissíteni CARDS_MASTER alapján

- Minta: `AET-IGN-HAM-009 Faj: Ember vagy Ork->Ember; AET-IGN-HAM-010 Faj: Ember vagy Ork->Ember; AET-IGN-HAM-010 Kaszt: Orgyilkos / Harcos->Orgyilkos; AET-IGN-HAM-012 Kaszt: Harcos vagy Őrző->Őrző; AET-IGN-LAN-006 Kaszt: Alap->Kósza; AET-LUX-FHL-024 Kaszt: Alap->Őrző; AET-LUX-FHL-026 Kaszt: Alap->Harcos; AET-LUX-FHL-029 Kaszt: Alap->Őrző; AET-LUX-APJ-003 Kaszt: Alap->Kósza; AET-LUX-APJ-005 Kaszt: Alap->Őrző`



### P1 – PRODUCT_DECKLISTS: Nem 40 lapos paklik

- Darab: 3
- Státusz: nyitott
- Javaslat: Decklist darabszám javítása 40-re

- Minta: `DECK-AQU-STARTER-001=41; DECK-LUX-FHL-TEST-001=41; DECK-TER-DRU-TEST-001=41`



### P2 – PRODUCT_DECKLISTS: Kártya_Név nem egyezik a CARDS_MASTER névvel

- Darab: 24
- Státusz: nyitott
- Javaslat: Decklist névmezők szinkronizálása ID alapján

- Minta: `AET-UMB-ARS-009/DECK-UMB-ARS-TEST-001: Árnyközvetítő->Árnyék-közvetítő; AET-UMB-ARS-015/DECK-UMB-ARS-TEST-001: Noctis, az Árnyak Ura->Noctis az Árnyak Ura; AET-UMB-ARS-037/DECK-UMB-ARS-TEST-001: Árnylépés->Árnyék-Ugrás; AET-UMB-ARS-039/DECK-UMB-ARS-TEST-001: Alvilági Összeköttetések->Alvilági Kapcsolatok; AET-UMB-ARS-049/DECK-UMB-ARS-TEST-001: Váratlan Sarckivetés->Váratlan Adóellenőrzés; AET-UMB-LEA-005/DECK-UMB-LEA-TEST-001: Morvessa, a Lélekszívó Papnő->Lélekszívó Papnő; AET-UMB-LEA-006/DECK-UMB-LEA-TEST-001: Feltámadt Csontzúzó->Feltámadt Csonttörő; AET-UMB-LEA-015/DECK-UMB-LEA-TEST-001: Sírvermi Sírásó->Temetői Sírásó`



### P2 – PRODUCTS: Teljes none sorok

- Darab: 5
- Státusz: nyitott
- Javaslat: Üres sorok törlése vagy exportból szűrése

- Minta: `[18, 19, 20, 21, 22]`



### P3 – PRODUCTS/DECKLISTS: Product_ID decklist nélkül

- Darab: 3
- Státusz: részben elfogadott
- Javaslat: Nem végleges productként jelölni vagy később decklistet készíteni

- Minta: `BP-CORE01; KLP-IGN-HAM01; KZK-CORE01`



### P2 – CARD_PRINTINGS: CARD_PRINTINGS eltér a CARDS_MASTER-től

- Darab: 2
- Státusz: döntési pont
- Javaslat: Ha CARD_PRINTINGS aktív, szinkronizálni; ha nem aktív, státuszát dokumentálni

- Minta: `AET-IGN-HAM-023 Play_Legal_Status: CORE01_needs_token_rules->CORE01_test_required; AET-IGN-HAM-031 Play_Legal_Status: CORE01_needs_token_rules->CORE01_test_required`



### P3 – VERZIÓ: Üres / none verziósorok

- Darab: 23
- Státusz: nyitott
- Javaslat: Exportból szűrés vagy munkalapról törlés

- Minta: `[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]`



### P1 – EXPORT_RUNTIME: 7. EXPORT_RUNTIME nincs feltöltve

- Darab: 1
- Státusz: nem ellenőrizhető
- Javaslat: A program végleges kártyalistájához külön export szükséges



### P1 – BOOSTER_POOLS: 16. BOOSTER_POOLS nincs feltöltve

- Darab: 1
- Státusz: nem ellenőrizhető
- Javaslat: AQUA +2 lap booster pool átvezetésének ellenőrzéséhez szükséges



### P1 – LOOKUPS: Hiányzó structured LOOKUPS oszlop: Zóna_Felismerve

- Darab: 13
- Státusz: nyitott
- Javaslat: LOOKUPS bővítése külön structured validációs oszloppal



### P1 – LOOKUPS: Hiányzó structured LOOKUPS oszlop: Kulcsszavak_Felismerve

- Darab: 12
- Státusz: nyitott
- Javaslat: LOOKUPS bővítése külön structured validációs oszloppal



### P1 – LOOKUPS: Hiányzó structured LOOKUPS oszlop: Trigger_Felismerve

- Darab: 108
- Státusz: nyitott
- Javaslat: LOOKUPS bővítése külön structured validációs oszloppal



### P1 – LOOKUPS: Hiányzó structured LOOKUPS oszlop: Célpont_Felismerve

- Darab: 83
- Státusz: nyitott
- Javaslat: LOOKUPS bővítése külön structured validációs oszloppal



### P1 – LOOKUPS: Hiányzó structured LOOKUPS oszlop: Hatáscímkék

- Darab: 114
- Státusz: nyitott
- Javaslat: LOOKUPS bővítése külön structured validációs oszloppal



### P1 – LOOKUPS: Hiányzó structured LOOKUPS oszlop: Időtartam_Felismerve

- Darab: 33
- Státusz: nyitott
- Javaslat: LOOKUPS bővítése külön structured validációs oszloppal



### P1 – LOOKUPS: Hiányzó structured LOOKUPS oszlop: Értelmezési_Státusz

- Darab: 24
- Státusz: nyitott
- Javaslat: LOOKUPS bővítése külön structured validációs oszloppal



## Javasolt új LOOKUPS-oszlopok a program/runtime irány miatt

### Zóna_Felismerve értékek (13 egyedi)

horizont (414), dominium (381), zenit (213), hand (128), deck (116), void (44), seal_row (43), graveyard (40), source (33), lane (14), aeternal (13), seal (10), both_sides (8)


### Kulcsszavak_Felismerve értékek (12 egyedi)

aegis (89), clarion (85), sundering (57), celerity (55), ethereal (47), resonance (45), burst (42), harmonize (32), echo (24), bane (16), taunt (2), aethereal (1)


### Trigger_Felismerve értékek (108 egyedi)

static (193), on_summon (94), on_attack_declared (62), on_play (37), on_death (27), instant (25), on_combat_damage_dealt (15), on_seal_break (14), on_turn_end (13), on_enemy_spell_or_ritual_played (12), on_enemy_summon (11), on_combat_damage_taken (10), on_move_zenit_to_horizont (10), on_stat_gain (10), on_this_moves_from_dominium_to_void (8), on_bounce (8), on_block_survived (7), on_ready_from_exhausted (7), on_position_swap (6), activated_ability (6), on_enemy_extra_draw (5), on_enemy_spell_target (5), reaction (5), on_enter_void_from_dominium (4), on_combat_destroy (4), on_attack_hits (4), on_combat_damage (4), on_own_jel_activated (4), on_damage_survived (3), on_own_ige_or_ritual_play (3)


### Célpont_Felismerve értékek (83 egyedi)

self (271), enemy_entity (124), own_entity (112), own_horizont_entity (53), own_entities (49), enemy_horizont_entity (44), own_horizont_entities (29), enemy_zenit_entity (22), enemy_horizont_entities (21), own_deck (21), opponent (20), enemy_entities (16), other_own_entity (15), own_zenit_entity (12), own_aeternal (11), own_hand (10), own_seal (10), enemy_hand (9), own_graveyard_entity (9), attacking_enemy_entity (8), enemy_seal (8), own_zenit_entities (6), enemy_spell_or_ritual (6), own_void_entity (5), enemy_aeternal (4), enemy_zenit_entities (3), lane (3), enemy_spell (3), own_source_card (3), own_jel (3)


### Hatáscímkék értékek (114 egyedi)

atk_mod (113), damage (109), draw (105), hp_mod (75), exhaust (61), grant_keyword (59), return_to_hand (54), resource_gain (38), keyword (31), sacrifice (28), cost_mod (28), damage_prevention (28), heal (28), move_zenit (28), attack_restrict (26), destroy (24), move_horizont (24), untargetable (20), discard (19), attack_nullify (19), ability_lock (18), ready (17), graveyard_recursion (15), tutor (14), reveal (13), block_restrict (11), stat_protection (10), counterspell (10), reveal_information (10), summon_token (9)


### Időtartam_Felismerve értékek (33 egyedi)

instant (375), until_turn_end (169), static_while_on_board (160), while_active (40), during_combat (27), until_match_end (17), next_own_awakening (8), until_next_enemy_turn (7), permanent (7), permanent_until_match_end (6), static_while_plane_active (6), until_next_own_turn_end (5), until_next_controller_awakening (5), replacement (4), until_next_controller_turn_end (3), until_next_controller_breach_phase (2), delayed_next_own_awakening (2), next_own_turn (2), until_combat_end (2), delayed_until_distribution (1), after_combat (1), once_per_own_manifestation_phase (1), static_while_active (1), while_in_zenit (1), until_next_controller_awakening_if_target_was_exhausted (1), until_next_own_awakening (1), each_turn (1), delayed_until_turn_end (1), once_per_own_turn (1), once_per_turn (1)


### Értelmezési_Státusz értékek (24 egyedi)

osszetett_egyedi (324), elso_koros_gepi_ertelmezes (105), szövegjavított (59), tiszta (42), passziv_vagy_egyszeru (42), osszetett_egyedi_review_required (32), osszetett_egyedi_tesztelendő (32), szövegjavított_tesztelendő (29), folyamatos_sik_hatas (28), javított_tesztelendő (28), javított_review_required (25), újraszövegezett (21), javított_egyedi (10), Kaszt javítva (9), Jel-formátum javítva (7), átalakított_tesztelendő (5), folyamatos_sik_hatas_tesztelendő (5), folyamatos_sik_hatas_review_required (3), token szabály átvezetve (2), átalakított_egyedi (2), megtartható_tesztelendő (1), átalakított_review_required (1), szövegjavított_review_required (1), passziv_vagy_egyszeru_review_required (1)

