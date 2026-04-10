# Aeterna kártyatáblázat – oszlopszabvány

Ez a dokumentum rögzíti, hogy a kártyatáblázat következő oszlopaiba pontosan milyen típusú adat kerülhet, és milyen szabályok szerint kell kitölteni őket:

- Képesség_Canonical
- Zóna_Felismerve
- Kulcsszavak_Felismerve
- Trigger_Felismerve
- Célpont_Felismerve
- Hatáscímkék
- Időtartam_Felismerve
- Feltétel_Felismerve
- Gépi_Leírás
- Értelmezési_Státusz
- Engine_Megjegyzés

---

# 0. Táblaszerkezeti alapszabály

A kártyatáblázat **fixen 22 oszlopból áll**.

## A kötelező oszlopsorrend

1. `Kártya név`
2. `Típus`
3. `Birodalom`
4. `Klán`
5. `Faj`
6. `Kaszt`
7. `Magnitudó`
8. `Aura`
9. `ATK`
10. `HP`
11. `Képesség`
12. `Képesség_Canonical`
13. `Zóna_Felismerve`
14. `Kulcsszavak_Felismerve`
15. `Trigger_Felismerve`
16. `Célpont_Felismerve`
17. `Hatáscímkék`
18. `Időtartam_Felismerve`
19. `Feltétel_Felismerve`
20. `Gépi_Leírás`
21. `Értelmezési_Státusz`
22. `Engine_Megjegyzés`

## Kötelező szerkezeti szabályok

- minden sorban pontosan **22 mezőnek** kell lennie
- **nincs üres cella**
- ha egy mezőbe nem kerül tényleges érték, akkor kötelezően:
  - `blank`
  - vagy `none`
- **plusz üres mező nem lehet**
- különösen figyelni kell arra, hogy a `Kulcsszavak_Felismerve` után ne csússzon be még egy extra oszlop
- ha egy mezőnek nincs tartalma, attól még a sor többi oszlopa nem tolódhat el
- minden későbbi kitöltésnél az üresen hagyható helyek helyett is explicit kitöltést kell használni

### Javasolt használat
- `blank` = nincs adat / nem releváns mező
- `none` = nincs külön feltétel / nincs külön megjegyzés / nincs további részletezés

---

## 1. Képesség_Canonical

### Célja
Rövid, egységes, gépileg jól olvasható átírás a természetes nyelvű képességről.

### Tartalom
- rövid, szabályos leírás
- több részes hatás esetén pontosvesszővel tagolható
- lehetőleg egységes angolos mintában

### Példák
- `[HORIZONT] celerity`
- `[ZENIT] resonance 2`
- `[DOMINIUM] clarion: deal 1 damage to target enemy entity`
- `target allied entity gains ethereal until end of turn`
- `destroy one exhausted allied entity; draw 3 cards`

### Ne kerüljön bele
- fejlesztői komment
- bizonytalanság
- engine-megjegyzés
- hosszú magyarázat

---

## 2. Zóna_Felismerve

### Célja
Az a játéktéri zóna vagy zónák, amelyekhez a képesség közvetlenül kötődik.

### Engedélyezett értékek
- `horizont`
- `zenit`
- `dominium`
- `graveyard`
- `hand`
- `deck`
- `source`
- `seal_row`
- `aeternal`
- `blank`

### Több zóna esetén
Vesszővel elválasztva:
- `horizont, zenit`
- `dominium, graveyard`

### Ne kerüljön bele
- keyword
- trigger
- célpont
- hatás
- `burst`

---

## 3. Kulcsszavak_Felismerve

### Célja
Csak a valódi, szabályszintű kulcsszavak rögzítése.

### Engedélyezett értékek
- `aegis`
- `bane`
- `burst`
- `celerity`
- `clarion`
- `echo`
- `ethereal`
- `harmonize`
- `resonance`
- `sundering`
- `taunt`
- `blank`

### Ne kerüljön bele
- `damage`
- `draw`
- `redirect`
- `flow_related`
- `cost_mod`
- `continuous`
- `spell_immunity`
- `untargetable`
- `trap`

---

## 4. Trigger_Felismerve

### Célja
Az esemény, amely kiváltja a képességet.

### Engedélyezett értékek
- `static`
- `on_summon`
- `on_death`
- `on_attack_declared`
- `on_attack_hits`
- `on_combat_damage_dealt`
- `on_combat_damage_taken`
- `on_block_survived`
- `on_damage_survived`
- `on_enemy_spell_target`
- `on_enemy_spell_or_ritual_played`
- `on_enemy_summon`
- `on_enemy_zenit_summon`
- `on_enemy_extra_draw`
- `on_enemy_third_draw_in_turn`
- `on_turn_end`
- `on_next_own_awakening`
- `on_influx_phase`
- `on_heal`
- `on_enemy_ability_activated`
- `on_enemy_multiple_draws`
- `on_enemy_horizont_threshold`
- `on_move_zenit_to_horizont`
- `on_leave_board`
- `on_spell_cast_by_owner`
- `on_position_swap`
- `on_entity_enters_horizont`
- `on_source_placement`
- `on_seal_break`
- `on_bounce`
- `on_trap_triggered`
- `on_ready_from_exhausted`
- `on_stat_gain`
- `blank`

### Ne kerüljön bele
- célpont
- hatás
- keyword
- időtartam

### Megjegyzés
A `Sík` lapoknál a `Trigger_Felismerve` mező csak akkor legyen kitöltve, ha ténylegesen konkrét eseményhez kötött a hatás. A pusztán folyamatos síkhatásoknál `blank` maradjon.

---

## 5. Célpont_Felismerve

### Célja
A célpont típusa, amire a lap hat.

### Engedélyezett értékek
- `self`
- `own_entity`
- `other_own_entity`
- `enemy_entity`
- `own_horizont_entity`
- `enemy_horizont_entity`
- `own_zenit_entity`
- `enemy_zenit_entity`
- `own_entities`
- `enemy_entities`
- `own_horizont_entities`
- `enemy_horizont_entities`
- `own_zenit_entities`
- `enemy_zenit_entities`
- `own_seal`
- `enemy_seal`
- `own_seals`
- `enemy_seals`
- `own_aeternal`
- `enemy_aeternal`
- `own_hand`
- `enemy_hand`
- `own_deck`
- `own_graveyard_entity`
- `enemy_spell`
- `enemy_spell_or_ritual`
- `lane`
- `source_card`
- `own_source_card`
- `enemy_source_card`
- `opposing_entity`
- `blank`

### Ne kerüljön bele
- zóna mint általános leírás
- trigger
- hatáscímke
- `lane_entities`

### Külön szabály
A `Célpont_Felismerve` mezőbe **a végső hatás célpontja** kerüljön, ne a trigger kiváltó alanya.

---

## 6. Hatáscímkék

### Célja
A lap tényleges mechanikai hatásainak listázása.

### Engedélyezett értékek
- `damage`
- `seal_damage`
- `draw`
- `atk_mod`
- `hp_mod`
- `exhaust`
- `summon`
- `destroy`
- `discard`
- `counterspell`
- `redirect`
- `cost_mod`
- `resource_gain`
- `move_horizont`
- `move_zenit`
- `graveyard_recursion`
- `grant_keyword`
- `damage_immunity`
- `damage_bonus`
- `damage_prevention`
- `stat_protection`
- `sacrifice`
- `free_cast`
- `tutor`
- `untargetable`
- `return_to_hand`
- `summon_token`
- `attack_restrict`
- `summon_restrict`
- `block_restrict`
- `control_change`
- `ready`
- `return_to_deck`
- `move_to_source`
- `source_manipulation`
- `cleanse`
- `copy_stats`
- `copy_keywords`
- `position_lock`
- `attack_nullify`
- `ability_lock`
- `random_discard`
- `choice`
- `blank`

### Ne kerüljön bele
- trigger
- célpont
- időtartam
- túl speciális egyszer használatos címkék, ha nem szükségesek

---

## 7. Időtartam_Felismerve

### Célja
A hatás meddig tart.

### Engedélyezett értékek
- `instant`
- `during_combat`
- `until_turn_end`
- `until_next_own_turn_end`
- `until_next_enemy_turn`
- `until_match_end`
- `static_while_on_board`
- `while_active`
- `next_own_awakening`
- `blank`

### Ne kerüljön bele
- komment
- trigger
- célpont
- fejlesztői megjegyzés

---

## 8. Feltétel_Felismerve

### Célja
Minden extra feltétel vagy szűrés, ami nem trigger, nem célpont és nem hatás.

### Példák
- `must_be_on_horizont`
- `target_enemy_is_exhausted`
- `another_allied_goblin_on_dominium`
- `target_must_be_allied_entity_in_zenit`
- `target_must_be_entity_in_own_graveyard_with_magnitude_lte_3`
- `enemy_spell_or_ritual_must_target_own_entity`
- `count_allied_elemental_entities_max_3`
- `trigger_on_third_card_draw_in_same_turn`
- `random_target_selection`
- `usable_once_per_turn`
- `trigger_only_if_effect_is_from_spell`
- `trigger_only_if_stat_gain_is_from_effect`
- `chosen_mode_1_or_2`

### Használat
- ha nincs külön feltétel: `none`

### Ne kerüljön bele
- maga a hatás
- célpontlista
- időtartam
- keyword
- a Gépi_Leírás szövege

---

## 9. Gépi_Leírás

### Célja
Rövid, ember számára is könnyen olvasható, de gépileg szabályos összefoglaló.

### Példák
- `Egy kimerült ellenséges entitás 4 sebzést szenved el.`
- `A saját Zenit-entitások a kör végéig immunisak az ellenséges kártyasebzésre.`
- `Megidézéskor egy másik saját entitás +1 ATK-ot és +1 max HP-t kap.`

### Használat
- ez mindig természetes nyelvű rövid összefoglaló
- nem lehet benne státuszérték
- nem lehet benne engine-megjegyzés

### Ne kerüljön bele
- hosszú kommentár
- bizonytalanság
- fejlesztői magyarázat
- `elso_koros_gepi_ertelmezes`
- `osszetett_egyedi`

---

## 10. Értelmezési_Státusz

### Célja
Azt mutatja, mennyire könnyen fordítható le gépi primitívekre.

### Engedélyezett értékek
- `passziv_vagy_egyszeru`
- `elso_koros_gepi_ertelmezes`
- `osszetett_egyedi`
- `folyamatos_sik_hatas`

### Jelentés
- `passziv_vagy_egyszeru`: egyszerű keyword vagy könnyen olvasható statikus szabály
- `elso_koros_gepi_ertelmezes`: jól bontható, de már 1-2 konkrét trigger/feltétel kell
- `osszetett_egyedi`: több részből álló vagy speciális kezelésű képesség
- `folyamatos_sik_hatas`: aktív Sík által fenntartott folyamatos, globális vagy mezőszintű hatás

### Külön szabály
Ez a mező **csak státuszértéket** tartalmazhat.  
Nem kerülhet bele:
- Gépi_Leírás
- Engine_Megjegyzés
- képességmagyarázat

---

## 11. Engine_Megjegyzés

### Célja
Fejlesztői megjegyzés arról, hogy milyen engine-primitívekre bontható, vagy mi a nehéz része.

### Jó példák
- `Egyszerű célzott sebzés-primitívre bontható.`
- `Lane-specifikus célzás kell hozzá.`
- `Spell-target reakciós infrastruktúrát igényel.`
- `Folyamatos globális költségmódosító.`
- `Halál utáni trigger külön state-trackinget kér.`

### Használat
- ha nincs külön megjegyzés: `none`

### Ne kerüljön bele
- maga a képességszöveg
- oszlopismétlés
- túl általános vagy üres komment
- Értelmezési_Státusz érték

---

# Kiemelt megjegyzések

## Jel lapokra külön szabály
A `Jel` lapok két részből állnak:
- Aktiválás
- Hatás

Ezért ezeknél különösen fontos:

- `Trigger_Felismerve` = csak az aktiválási esemény
- `Célpont_Felismerve` = a hatás végső célpontja
- `Feltétel_Felismerve` = minden triggerhez tartozó extra szűrés
- `Hatáscímkék` = a végrehajtott mechanikai hatás

## Gyakori hibák
- `continuous` helyett inkább `static`
- `lane_entities` helyett `lane`
- `burst` csak akkor kerülhet a `Kulcsszavak_Felismerve` mezőbe, ha a lap tényleg rendelkezik Bursttel
- a `Kulcsszavak_Felismerve` után nem csúszhat be még egy plusz mező
- a `Feltétel_Felismerve` mezőbe nem kerülhet a `Gépi_Leírás`
- a `Gépi_Leírás` mezőbe nem kerülhet az `Értelmezési_Státusz`
- az `Értelmezési_Státusz` mezőbe nem kerülhet az `Engine_Megjegyzés`

## Alapszabály
Ha egy információ:
- **mi váltja ki** → `Trigger_Felismerve`
- **mire hat** → `Célpont_Felismerve`
- **mit csinál** → `Hatáscímkék`
- **meddig tart** → `Időtartam_Felismerve`
- **milyen extra szűrés kell** → `Feltétel_Felismerve`

## Kitöltési alapszabály
Ha egy mezőbe nincs valódi tartalom:
- használj `blank` vagy `none` értéket
- **ne hagyj üres cellát**