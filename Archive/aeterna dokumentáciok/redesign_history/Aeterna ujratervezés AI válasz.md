Rendben, ez jó kiinduló újratervezési jegyzet. Látom az átfedéseket is: több pont már szerepelt a korábbi feladatlistákban, csak most magasabb szintű célként fogalmaztad meg.

Apró jelzés: a fájl címe most **„Aetherna kártyajáték újratervezése”**, miközben a projekt neve eddig **AETERNA / Aeterna** volt. Ezt később érdemes egységesíteni, de most nem fontos tartalmi akadály.

A jegyzeted fő állításai: az eddigi „teszteszközből később játék” irány helyett már eleve játékprogramként kell tervezni; három digitális módot látsz: AI vs AI, AI vs játékos, játékos vs játékos; közben a fizikai TCG marad az igazi fő prioritás; Godotot figyelembe kell venni; a Python akár maradhat, akár később cserélhető; a mappa/fájlszerkezetet felül kell vizsgálni; a `cards.xlsx` helyett exportált fájlokból kell dolgozni; a program törzsét jobban szét kell bontani; a LOOKUPS-exportot használható értéklistás alapra kell hozni. 

# Hogyan illeszkedik ez a mostani feladatlistához?

## Ami már részben vagy teljesen elindult

### 1. `cards.xlsx` lecserélése exportokra

Ez már jó úton van.

Jelenlegi állapot:

```text
EXPORT_RUNTIME.jsonl loader = kész
PRODUCT_DECKLISTS.jsonl loader = kész
régi XLSX fallback = megmaradt
Card_ID alapú kapcsolás = működik
deckek 40 lapos validációja = rendben
```

Tehát ez a pont **nem új feladat**, hanem a mostani irány megerősítése.

### 2. LOOKUPS értéklisták használata

Ez is elkezdődött.

Amit már megtettünk:

```text
structured mezők értéklistái részben kidolgozva
runtime warningok már vannak
unknown enum / legacy enum kategóriák látszanak
```

Ami még hátra van:

```text
LOOKUPS export programoldali használata
structured warningok triage-a
mely warning valódi hiba, melyik csak átmeneti legacy érték
adatstandardizálás
```

Ez lesz szerintem a következő nagyobb adatoldali szakasz.

### 3. Godot figyelembevétele

Ez nagyon fontos, de **nem azt jelenti, hogy most azonnal Godotba kell költöztetni mindent**.

Helyes sorrend:

```text
előbb stabil backend contract
utána snapshot / legal actions / apply_action / event log tisztítása
utána Godot adapter
utána vizuális kliens
```

Godot szempontból már most figyelni kell arra, hogy a backend ne legyen túl szorosan CLI-hez vagy Excelhez kötve.

---

# Új, összefésült nagy struktúra

Én most így bontanám a teljes projektet:

## A. Fizikai TCG / szabály- és kártyatervezés

Ez marad a legfőbb projektcél.

Ide tartozik:

```text
szabályforrások
kártyaadatbázis
Birodalmak / Klánok
kártyabalansz
paklik
ritkaság / print / booster logika
fizikai kiadhatóság
```

Ez nem rendelhető alá teljesen a programnak. A program ennek segédeszköze és digitális kiterjesztése.

## B. Digitális tesztprogram

Ez az AI vs AI rész.

Célja:

```text
kártyák tesztelése
paklik összevetése
warningok gyűjtése
balanszhibák felismerése
engine-problémák feltárása
```

Ez épül elsőként, mert ez segíti a fizikai TCG fejlesztését is.

## C. Játszható digitális játék

Ez az AI vs játékos és játékos vs játékos irány.

Ez már nem csak tesztprogram, hanem játéktermék.

Későbbi elemei:

```text
Godot kliens
kártyagyűjtemény
csomagnyitás
valuta / jutalom
pakliépítés
kártyavizuál rétegek
PvP
```

Ez fontos hosszú távon, de csak akkor stabil, ha az adat- és backendréteg tiszta.

---

# Függőségi sorrend, nem csak prioritás

## 0. szint — Projektcél újrarögzítése

Ez a mostani jegyzeted miatt szükséges.

Rögzíteni kell:

```text
A projekt elsődleges célja: fizikai TCG megalkotása.
A program célja: tesztelés + későbbi digitális játék.
Digitális módok:
1. AI vs AI
2. AI vs játékos
3. játékos vs játékos
```

Ez nem blokkolja a kódot, de blokkolja a hosszú távú rossz irányok elkerülését.

## 1. szint — Adatút stabilizálása

Ez már majdnem kész.

Kész:

```text
EXPORT_RUNTIME loader
PRODUCT_DECKLISTS loader
Card_ID használat
Generated_Print_ID
deck validáció
```

Következő ehhez kapcsolódó feladat:

```text
LOOKUPS / structured warning triage
```

Ez fontos, mert ha a structured mezők túl zajosak, akkor az engine és a tesztprogram később rengeteg hamis warningot fog adni.

## 2. szint — Programarchitektúra és mappaszerkezet felmérése

Ezt a jegyzeted külön kiemeli.

De itt óvatosnak kell lenni:

```text
ne töröljünk fájlokat azonnal
ne rendezzük át a teljes projektet vakon
előbb import/runtime audit kell
```

Helyes sorrend:

```text
1. jelenlegi mappaszerkezet feltérképezése
2. aktív / inaktív / bizonytalan fájlak jelölése
3. Archive-jelöltek listája
4. csak tesztek után áthelyezés vagy törlés
```

Ez középtávú feladat, nem a következő kódolási lépés.

## 3. szint — Backend contract stabilizálása

Ez a Godot és a játszható program előfeltétele.

Kulcselemek:

```text
create_match
get_snapshot
get_legal_actions
validate_action
apply_action
get_event_log
run_ai_step
```

Ezeknek úgy kell működniük, hogy később Godot is tudjon velük kommunikálni.

## 4. szint — AI vs AI tesztprogram

Ez legyen az első komoly programhasználati mód.

Függ tőle:

```text
EXPORT_RUNTIME
PRODUCT_DECKLISTS
backend actions
event log
tesztprofilok
deckek
```

Ez közvetlenül segíti a fizikai TCG balanszát is.

## 5. szint — AI vs játékos

Ez már fél-játék.

Előfeltétele:

```text
stabil legal action lista
snapshot emberi olvashatóság
apply_action megbízhatóság
alap spell/combat/trap működés
```

## 6. szint — Játékos vs játékos / Godot / gyűjtemény

Ez hosszú távú.

Függ tőle:

```text
backend contract
Godot adapter
kártyavizuál komponensek
Generated_Print_ID
collection / economy / pack opening rendszer
```

---

# Mit nem csinálnék most?

Nem kezdeném el azonnal:

```text
teljes program újraírását
Python lecserélését
teljes mappaszerkezet átrendezését
Godot implementációt
booster / valuta / csomagnyitás programozását
PvP rendszert
```

Ezek fontosak, de előbb az alap útvonalat kell stabilizálni.

# Következő konkrét javasolt lépés

A mostani állapot alapján én ezt tenném következőnek:

```text
LOOKUPS / structured enum warning triage
```

Indok:

```text
a loader már működik;
a decklist már működik;
minden deck 40 lapos;
a teljes EXPORT_RUNTIME még 519 warningot ad;
ezek közül el kell választani a valódi hibákat, a LOOKUPS-bővítési igényeket és az átmeneti legacy értékeket.
```

Ezután jöhet:

```text
programarchitektúra / mappaszerkezet felmérése
```

De nem törléssel, hanem státuszolással.

# Frissített sorrend röviden

```text
1. Projektcél újrarögzítése az új jegyzet alapján
2. LOOKUPS / structured warning triage
3. Programarchitektúra és mappaszerkezet audit
4. Backend contract ellenőrzés Godot-szemmel
5. AI vs AI tesztprogram stabilizálás
6. Spell / targeting / combat / trap mélyítés
7. AI vs játékos prototípus
8. Godot vizuális kliens előkészítés
9. Collection / pack opening / digitális gazdaság
10. PvP
```

A saját jegyzeted tehát nem írja felül az eddigi listát, hanem egy magasabb szintű célt ad fölé. Szerintem ez hasznos, mert így nem csak „tesztprogramot foltozunk”, hanem már most olyan irányba igazítjuk a programot, hogy később valódi játékprogram lehessen.
