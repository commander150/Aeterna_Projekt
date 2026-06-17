# Aeterna kártyatáblázat – oszlopszabvány

## VERZIÓ / DOKUMENTUMSTÁTUSZ

A jelen dokumentum az AETERNA kártyatáblázat 22 oszlopos structured / canonical mezőinek oszlopszabványa.

A dokumentum célja annak rögzítése, hogy a kártyaadatok egyszerűsített, runtime-előkészítő vagy import/export célú 22 oszlopos formájában milyen mezők szerepelnek, ezekbe milyen értékek kerülhetnek, és hogyan kell kezelni a természetes kártyaszöveg gépileg előkészített értelmezését.

A dokumentum nem önálló szabályforrás. A természetes kártyaszöveg, a főforrások és a kártyaadatbázis munkaforrás elsődleges szabályi vagy adatforrási szerepét nem írja felül. Feladata kizárólag a structured mezők kitöltési rendjének és engedélyezett értékeinek rögzítése.

## Verziótörténet

### 1.0v verzió

Módosítás típusa: oszlopszabvány létrehozása / 22 oszlopos structured mezők rögzítése

Érintett részek: teljes dokumentum

Státusz: aktív kártyatáblázat-oszlopszabvány

Változás leírása:

A dokumentum első munkaváltozatként rögzíti a 22 oszlopos kártyatáblázat szerkezetét, a structured mezők szerepét, a kötelező oszlopsorrendet, valamint az egyes structured mezők engedélyezett értékeit.

### 1.1v verzió

Módosítás típusa: structured értékkészlet bővítése / VENTUS audit alapján szükséges trigger- és hatáscímke-pontosítás

Érintett részek: 4. Trigger_Felismerve; 7. Hatáscímkék; gyakori hibák; structured-bővítési megjegyzések

Státusz: aktív kártyatáblázat-oszlopszabvány, bővített trigger- és hatáscímke-listával

Változás leírása:

A VENTUS / Viharhozók Klán auditja alapján több olyan visszatérő mechanikai helyzet jelent meg, amelyet a korábbi Trigger_Felismerve és Hatáscímkék lista csak közelítően tudott kezelni.

A jelen verzióban új engedélyezett triggerértékek és hatáscímkék kerülnek bevezetésre. Ezek célja nem új játékszabály létrehozása, hanem a már meglévő vagy audit során megtartott kártyaszövegek pontosabb structured leírása.

Új Trigger_Felismerve értékek:

on_attack_finished
on_combat_destroy_enemy
on_exhausted
activated_ability

Új Hatáscímkék értékek:

ready_prevention
trigger_duplicate
extra_breakthrough_phase
seal_break_prevention

Később mérlegelendő, de jelen verzióban még nem kötelező érték:

stat_gain_prevention

A változás célja, hogy a structured mezők ne kényszerítsék pontatlan közelítő értékekre az auditált lapokat, ha a természetes kártyaszöveg egyébként szabályilag működőképes.

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

### 1.2v verzió

Módosítás típusa: structured triggerérték bővítése / VENTUS Égbolt Úrai audit alapján szükséges célzás-trigger pontosítás

Érintett részek: 4. Trigger_Felismerve; gyakori hibák; 12. Újonnan beemelt szabványbővítések

Státusz: aktív kártyatáblázat-oszlopszabvány, bővített Ige/Rituálé-célzás triggerrel

Változás leírása:

A VENTUS / Égbolt Úrai Klán auditja alapján szükségessé vált egy új, pontosabb Trigger_Felismerve érték bevezetése.

Az audit során több olyan lap jelent meg, amely nem egyszerűen ellenséges Ige kijátszására vagy ellenséges Ige célzására reagál, hanem arra, amikor egy ellenséges Ige vagy Rituálé egy saját Entitást vagy saját Légies Entitást célba vesz.

A korábbi on_enemy_spell_target érték erre nem elég pontos, mert csak Ige-célzásra utal.

A korábbi on_enemy_spell_or_ritual_played érték sem megfelelő, mert az általános kijátszási eseményt jelöli, nem pedig azt, hogy az Ige vagy Rituálé konkrét célpontot választott.

Ezért a jelen verzióban új engedélyezett Trigger_Felismerve érték kerül bevezetésre:

on_enemy_spell_or_ritual_target

Ez az érték akkor használandó, ha a hatás akkor indul, amikor az ellenfél Igéje vagy Rituáléja célpontként választ egy saját lapot, saját Entitást, saját Légies Entitást vagy más, kártyaszövegben meghatározott saját célpontot.

A változás célja nem új játékszabály létrehozása, hanem a már meglévő kártyaszövegek pontosabb structured jelölése.

Új Trigger_Felismerve érték:

on_enemy_spell_or_ritual_target

Új Hatáscímkék érték nem kerül bevezetésre ebben a verzióban, mert a VENTUS / Égbolt Úrai audit során szükséges resource_drain érték már szerepel az aktív hatáscímke-listában.

---

## 0. Táblaszerkezeti alapszabály

A kártyatáblázat **fixen 22 oszlopból áll**.

### A kötelező oszlopsorrend

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

### Kötelező szerkezeti szabályok

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
- `lane`
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
- `on_gain_keyword`
- `on_destroy`
- `on_discard`
- `on_enemy_card_played`
- `on_enemy_second_summon_in_turn`
- `on_start_of_turn`
- `on_attack_finished`
- `on_combat_destroy_enemy`
- `on_exhausted`
- `activated_ability`
- `on_enemy_spell_or_ritual_target`
- `blank`

### Ne kerüljön bele

- célpont
- hatás
- keyword
- időtartam

### Megjegyzés

A `Sík` lapoknál a `Trigger_Felismerve` mező csak akkor legyen kitöltve, ha ténylegesen konkrét eseményhez kötött a hatás. A pusztán folyamatos síkhatásoknál `blank` maradjon.

#### Új triggerértékek pontosítása

`on_attack_finished`

Akkor használandó, ha a hatás akkor indul, amikor egy Entitás befejezi a támadását.

Nem azonos az `on_attack_declared` triggerrel, mert nem a támadás kijelölésére reagál.

Nem azonos az `on_attack_hits` triggerrel sem, mert a támadás befejezése nem feltétlenül jelent sikeres találatot, sebzést vagy Pecsét-feltörést.

Példa:

támadás befejezése után Visszaállítás;
támadás befejezése után ön-visszavétel;
támadás befejezése után extra támadási lehetőség.

`on_combat_destroy_enemy`

Akkor használandó, ha a hatás akkor indul, amikor egy Entitás harc során elpusztít egy ellenséges Entitást.

Nem azonos az `on_combat_damage_dealt` triggerrel, mert itt nem pusztán sebzés okozása a feltétel, hanem az, hogy az ellenséges Entitás ténylegesen elpusztuljon a harc során.

Példa:

harci pusztítás után Visszaállítás;
harci pusztítás után visszaküldés;
harci pusztítás után további jutalomhatás.

`on_exhausted`

Akkor használandó, ha a hatás akkor indul, amikor egy lap Kimerült állapotba kerül.

Nem azonos az `on_attack_declared` triggerrel, mert egy lap nem csak támadás miatt merülhet ki. Kimerülhet költség, képesség, kártyahatás, blokkolás vagy más szabályi ok miatt is.

Példa:

amikor ez az Entitás Kimerül;
amikor egy saját Entitás Kimerül;
amikor egy lap kártyahatás miatt Kimerült állapotba kerül.

`activated_ability`

Akkor használandó, ha a kártya saját, játékos által aktiválható képességgel rendelkezik.

Az `activated_ability` nem önmagában határozza meg az aktiválás időpontját. A pontos időpontot, költséget vagy feltételt a Feltétel_Felismerve mezőben kell rögzíteni.

Példa:

`activated_only_during_own_manifestation_phase`
`exhaust_this_as_activation_cost`
`usable_once_per_turn`

`on_enemy_spell_or_ritual_target`

Akkor használandó, ha a hatás akkor indul, amikor az ellenfél Igéje vagy Rituáléja célpontként választ egy saját lapot, saját Entitást, saját Légies Entitást vagy más, a kártyaszövegben pontosan meghatározott saját célpontot.

Nem azonos az `on_enemy_spell_target` triggerrel, mert az csak ellenséges Ige célzására utal.

Nem azonos az `on_enemy_spell_or_ritual_played` triggerrel sem, mert az általános kijátszási eseményt jelöli, nem a célpontválasztást.

Példa:

amikor az ellenfél Igéje vagy Rituáléja célba venne egy saját Légies Entitást;
amikor egy ellenséges Ige vagy Rituálé saját Entitást céloz;
amikor egy Jel az ellenséges Ige/Rituálé célzására reagál, majd a célpontot kézbe menti vagy a hatást érvényteleníti.

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
- `enemy_hand_card`
- `enemy_face_down_trap`
- `own_face_down_trap`
- `own_graveyard`
- `opponent`
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
- `heal`
- `reveal`
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
- `resource_drain`
- `resource_acceleration`
- `resource_spend`
- `move_horizont`
- `move_zenit`
- `graveyard_recursion`
- `graveyard_replacement`
- `grant_keyword`
- `type_change`
- `stat_reset`
- `trap_immunity`
- `damage_immunity`
- `damage_bonus`
- `damage_prevention`
- `overflow_damage`
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
- `deck_bottom`
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
- `ready_prevention`
- `trigger_duplicate`
- `extra_breakthrough_phase`
- `seal_break_prevention`
- `blank`

### Ne kerüljön bele
- trigger
- célpont
- időtartam
- túl speciális egyszer használatos címkék, ha nem szükségesek

### Megjegyzés

#### Új hatáscímkék pontosítása

`ready_prevention`

Akkor használandó, ha egy lap vagy lapcsoport nem állhat vissza Aktív állapotba egy meghatározott időpontban vagy időtartamban.

Nem azonos a `position_lock` címkével.
A `position_lock` pozíciómozgást vagy helyzeti korlátozást jelöl.
A `ready_prevention` kifejezetten a Kimerült állapotból Aktív állapotba való Visszaállítást akadályozza.

Példa:

az ellenfél következő Ébredés fázisában nem áll vissza Aktív állapotba;
a célpont a következő körben nem állhat vissza;
egy lap meghatározott időtartamig Kimerült marad.

`trigger_duplicate`

Akkor használandó, ha egy triggerelt képesség vagy triggerelt esemény kétszer aktiválódik, kétszer kerül feldolgozásra, vagy egy kártyahatás megduplázza egy triggerelt képesség működését.

Példa:

a következő Riadó képesség kétszer aktiválódik;
egy belépési trigger kétszer jön létre;
egy meghatározott triggerelt hatás megduplázódik.

`extra_breakthrough_phase`

Akkor használandó, ha a lap további Betörés fázist vagy Betörés fázisszerű extra támadási ablakot engedélyez.

Nem azonos a `ready` hatással.
A `ready` egy lap Aktív állapotba állítását jelöli.
Az `extra_breakthrough_phase` a körszerkezeten belül ad új támadási lehetőséget.

Példa:

a normál Betörés fázis után második Betörés fázis következhet;
csak meghatározott saját Entitások támadhatnak az extra Betörés fázisban;
extra harci ablak jön létre szűrt támadási jogosultsággal.

`seal_break_prevention`

Akkor használandó, ha egy hatás megakadályozza, érvényteleníti vagy megelőzi egy Pecsét feltörését.

Nem azonos az `attack_nullify` hatással.
Az `attack_nullify` magát a támadást vagy annak harci eredményét érvényteleníti.
A `seal_break_prevention` kifejezetten a Pecsét-feltörés eredményét akadályozza meg.

Példa:

amikor az ellenfél feltörné az utolsó fennálló Pecsétedet, akadályozd meg a feltörést;
a támadás létrejön, de a Pecsét nem törik fel;
egy konkrét Pecsét-feltörési esemény meghiúsul.

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
- `next_own_turn_start`
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

## Kiemelt megjegyzések

### Jel lapokra külön szabály
A `Jel` lapok két részből állnak:
- Aktiválás
- Hatás

Ezért ezeknél különösen fontos:

- `Trigger_Felismerve` = csak az aktiválási esemény
- `Célpont_Felismerve` = a hatás végső célpontja
- `Feltétel_Felismerve` = minden triggerhez tartozó extra szűrés
- `Hatáscímkék` = a végrehajtott mechanikai hatás

### Gyakori hibák
- `continuous` helyett inkább `static`
- `lane` mostantól érvényes zónaérték is lehet, ha maga az Áramlat a hatás elsődleges hivatkozási egysége
- `lane_entities` helyett `lane`
- `burst` csak akkor kerülhet a `Kulcsszavak_Felismerve` mezőbe, ha a lap tényleg rendelkezik Bursttel
- a `Kulcsszavak_Felismerve` után nem csúszhat be még egy plusz mező
- a `Feltétel_Felismerve` mezőbe nem kerülhet a `Gépi_Leírás`
- a `Gépi_Leírás` mezőbe nem kerülhet az `Értelmezési_Státusz`
- az `Értelmezési_Státusz` mezőbe nem kerülhet az `Engine_Megjegyzés`
- `on_attack_declared` nem használható automatikusan minden támadáshoz kapcsolódó hatásra. Ha a hatás a támadás befejezésekor indul, `on_attack_finished` használandó.
- `on_combat_damage_dealt` nem helyettesíti a harci pusztítást. Ha a feltétel az, hogy egy ellenséges Entitás harcban elpusztuljon, `on_combat_destroy_enemy` használandó.
- `on_attack_declared` nem megfelelő, ha a lap bármilyen Kimerülésre reagál. Ilyenkor `on_exhausted` használandó.
- Aktiválható saját képességnél nem `static` használandó, hanem `activated_ability`; a pontos időpont, költség vagy feltétel a `Feltétel_Felismerve` mezőbe kerüljön.
- Visszaállítás megakadályozására nem `position_lock`, hanem `ready_prevention` használandó.
- Triggerelt képesség megduplázására nem `ability_lock`, hanem `trigger_duplicate` használandó.
- Extra Betörés fázis vagy extra harci ablak esetén nem elég a `ready` vagy `attack_restrict`; szükség esetén `extra_breakthrough_phase` is használandó.
- Pecsét-feltörés megelőzésére nem mindig `attack_nullify` használandó. Ha maga a Pecsét-feltörés hiúsul meg, `seal_break_prevention` a pontos címke.
- Ha egy lap nem pusztán ellenséges Ige kijátszására, hanem ellenséges Ige vagy Rituálé célzására reagál, akkor nem `on_enemy_spell_target` és nem `on_enemy_spell_or_ritual_played` használandó, hanem `on_enemy_spell_or_ritual_target`.

### Alapszabály
Ha egy információ:
- **mi váltja ki** → `Trigger_Felismerve`
- **mire hat** → `Célpont_Felismerve`
- **mit csinál** → `Hatáscímkék`
- **meddig tart** → `Időtartam_Felismerve`
- **milyen extra szűrés kell** → `Feltétel_Felismerve`

### Kitöltési alapszabály
Ha egy mezőbe nincs valódi tartalom:
- használj `blank` vagy `none` értéket
- **ne hagyj üres cellát**

---

## 12. Újonnan beemelt szabványbővítések

A friss teljes táblázatellenőrzés alapján az alábbi bővítések ténylegesen szükségesek, ezért a dokumentum most már hivatalosan tartalmazza őket.

### Új zónaérték
- `lane`

### Új triggerértékek
- `on_gain_keyword`
- `on_destroy`
- `on_discard`
- `on_enemy_card_played`
- `on_enemy_second_summon_in_turn`
- `on_start_of_turn`
- `on_attack_finished`
- `on_combat_destroy_enemy`
- `on_exhausted`
- `activated_ability`
- `on_enemy_spell_or_ritual_target`

### Új célpontértékek
- `opponent`
- `enemy_hand_card`
- `enemy_face_down_trap`
- `own_face_down_trap`
- `own_graveyard`

### Új hatáscímkék
- `heal`
- `reveal`
- `resource_drain`
- `deck_bottom`
- `graveyard_replacement`
- `type_change`
- `stat_reset`
- `trap_immunity`
- `resource_acceleration`
- `resource_spend`
- `overflow_damage`
- `ready_prevention`
- `trigger_duplicate`
- `extra_breakthrough_phase`
- `seal_break_prevention`

### Új időtartamérték
- `next_own_turn_start`

### Megjegyzés

Az alábbi jelöltek egyelőre továbbra sem kötelező alapszabvány-bővítések, mert többnyire kezelhetők meglévő címkékkel és pontos `Feltétel_Felismerve` + `Engine_Megjegyzés` kombinációval:
- `effect_reduction`
- `delayed_revival`
- `reflect_damage`
- `retaliation_damage`
- `return_to_deck_bottom`

A VENTUS / Viharhozók audit alapján beemelt új trigger- és hatáscímke-értékek célja nem új játékszabály létrehozása, hanem a már meglévő kártyaszövegek pontosabb structured jelölése.

A következő érték egyelőre továbbra sem kötelező szabványbővítés, csak későbbi mérlegelési jelölt:

`stat_gain_prevention`

Indok:

A statbónusz megszerzésének tiltása jelenleg ritkább hatás. Amíg csak kevés lapnál fordul elő, kezelhető `stat_protection` vagy más közelítő címkével, pontos `Feltétel_Felismerve` és `Engine_Megjegyzés` mellett. Ha több hasonló lap jelenik meg, külön hatáscímkeként beemelhető.


A on_enemy_spell_or_ritual_target érték a VENTUS / Égbolt Úrai audit alapján kerül be a szabványba. Célja, hogy a saját Entitást vagy saját Légies Entitást célzó ellenséges Ige/Rituálé reakciók ne pontatlanul on_enemy_spell_target vagy on_enemy_spell_or_ritual_played értékkel legyenek jelölve.