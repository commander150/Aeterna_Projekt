# AETERNA – Excel / Google Sheets munkafájl szerkezete és oszlopszabvány

Verzió: 1.0  
Státusz: munkarendi segéddokumentum  
Cél: rögzíteni, hogy az AETERNA kártyaadatbázisban melyik lap mire való, milyen oszlopai vannak, és hogyan kell dolgozni vele.

## 1. Két külön szintet kell megkülönböztetni

### 1.1 Kártyaadat-forrás / cards.xlsx

A `cards.xlsx` a kártyák tényleges kártyaadat-forrása.

A jelenlegi egyszerűsített `cards.xlsx` szerkezetében Birodalmonként külön munkalapok vannak:

- IGNIS
- AQUA
- TERRA
- LUX
- UMBRA
- VENTUS
- AETHER

Minden ilyen Birodalom-lap ugyanazt a 22 oszlopos kártyatáblázat-szabványt követi.

### 1.2 Kártyaadatbázis munkaforrás

A nagyobb Google Sheets / Excel munkaforrás ennél több munkalapot tartalmazhat.

Ebben szerepelhet például:

- `1. VERZIÓ`
- `3. CARDS_MASTER`
- `4. AUDIT_LOG`
- `9. DECISION_LOG`
- `12. PRODUCTS`
- `15. PRODUCT_DECKLISTS`
- `17. NAME_PROFILE`

Ez a dokumentum mindkét szintet rögzíti, mert a munkában mindkettőre szükség lehet.

---

# 2. cards.xlsx / kártyalapok 22 oszlopos szabványa

A Birodalom-lapok és a `CARDS_MASTER` jellegű kártyatáblák alapja a fix 22 oszlopos szabvány.

## 2.1 Kötelező oszlopsorrend

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

## 2.2 Kötelező kitöltési szabály

- minden sorban pontosan 22 mező legyen;
- üres cella ne maradjon;
- ha nincs releváns adat: `blank` vagy `none`;
- extra üres oszlop nem lehet;
- hosszú szöveg miatt sem tolódhat el a sor;
- structured mezőkben csak szabványosított értékek szerepeljenek.

## 2.3 Fontos mezőértelmezések

### Képesség

Természetes, magyar kártyaszöveg.

### Képesség_Canonical

Rövid, egységes, gépileg olvasható képesség-átírás.

### Zóna_Felismerve

Az a zóna vagy zónák, amelyekhez a képesség közvetlenül kötődik.

### Kulcsszavak_Felismerve

Csak valódi szabályszintű kulcsszavak.

### Trigger_Felismerve

Az esemény, amely kiváltja a képességet.

### Célpont_Felismerve

A végső hatás célpontja, nem feltétlenül a trigger kiváltó alanya.

### Hatáscímkék

A tényleges mechanikai hatások.

### Időtartam_Felismerve

A hatás időtartama.

### Feltétel_Felismerve

Extra feltétel vagy szűrés.

### Gépi_Leírás

Rövid, embernek is olvasható, gépileg követhető összefoglaló.

### Értelmezési_Státusz

A strukturált értelmezés állapota.

### Engine_Megjegyzés

Technikai / engine-szempontú megjegyzés.

---

# 3. Munkaforrás-lapok

## 3.1 `1. VERZIÓ`

Cél: a fájl verziótörténetének követése.

Oszlopok:

```tsv
Verzió	Dátum	Módosítás típusa	Érintett munkalapok	Státusz	Változás leírása	Megjegyzés
```

Használat:

- csak táblázat-kompatibilis, egy soros bejegyzés kerüljön ide;
- hosszú dokumentumos verzióleírást nem ide kell teljes terjedelemben beilleszteni;
- a `Változás leírása` és `Megjegyzés` lehet hosszabb, de maradjon egy cellában.

## 3.2 `3. CARDS_MASTER`

Cél: a tényleges aktív kártyaadatbázis fő munkalapja.

Alapja a 22 oszlopos kártyaszabvány, de a nagyobb munkaforrás tartalmazhat további azonosító-, státusz- vagy termékmezőket is.

Használat:

- a kártyák tényleges neve és szövege itt változik;
- a NAME_PROFILE nem írja át automatikusan ezt a lapot;
- minden módosítás előtt tudni kell, hogy teljes sorcsere vagy mezőszintű javítás történik.

## 3.3 `4. AUDIT_LOG`

Cél: konkrét auditproblémák és javítások naplózása.

Oszlopok:

```tsv
Audit_ID	Dátum	Kártya név	Birodalom	Klán	Típus	Auditkör	Jelenlegi státusz	Hibakategória	Probléma	Javasolt javítás	Structured javítás szükséges	Balanszgyanú	Engine-gyanú	Döntést igényel	Megjegyzés
```

Használat:

- ide kerül minden konkrét hibajelentés;
- kártyaszintű problémák, structured eltérések, balanszgyanúk és engine-gyanúk itt legyenek követhetők;
- egy kártyához több auditbejegyzés is készülhet, ha több külön probléma van.

## 3.4 `9. DECISION_LOG`

Cél: döntések naplózása.

Oszlopok:

```tsv
Döntés_ID	Dátum	Téma	Döntés	Indoklás	Érintett kártyák / mezők	Forrásdokumentum	Státusz	Megjegyzés
```

Használat:

- ide csak valódi döntések kerüljenek;
- például: lap CORE01-ből kivéve, lap ötletládába kerül, névirány elfogadva, mechanikai irány véglegesítve;
- nem minden auditprobléma decision log.

## 3.5 `12. PRODUCTS`

Cél: termékek, tesztpakli-csoportok, kezdőpaklik és egyéb kiadási egységek nyilvántartása.

Javasolt / használt oszlopok:

```tsv
Product_ID	Product_Name_HU	Product_Type	Related_Set_ID	Distribution_Type	Fixed_Or_Random	Target_Audience	Contains_Cards_From	Excluded_Cards_From	Notes
```

Használat:

- minden `Product_ID`, amely a decklistben szerepel, legyen itt felvéve;
- belső tesztpakli is kaphat Product_ID-t;
- nem kereskedelmi termékeket is lehet jelölni internal_test státusszal.

## 3.6 `15. PRODUCT_DECKLISTS`

Cél: paklik és termékpaklik konkrét kártyalistája.

Oszlopok:

```tsv
Product_ID	Deck_ID	Szabályi_Kártya_ID	Kártya_Név	Darabszám	Szerep_A_Pakliban	Megjegyzés
```

Használat:

- decklistát mindig ID-alapon kell vezetni;
- a kártyanév segédmező, nem elsődleges azonosító;
- a pakliméret darabszám alapján ellenőrizendő;
- ha egy Product_ID nincs a PRODUCTS lapon, javítani kell.

## 3.7 `17. NAME_PROFILE`

Cél: névprofilozás és névjavaslatok kezelése.

Oszlopok:

```tsv
Kártya	Jelenlegi név	Birodalom	Klán	Faj	Kaszt	Képesség rövid szerepe	Névszint	Világbeli szerep	Mechanikai szerep	Képességből következő névirány	Egyedi jegy	Névforma	Névstátusz	Javasolt új név	Megjegyzés
```

Használat:

- ez nem automatikus átnevezési lap;
- a `Javasolt új név` csak döntés-előkészítő mező;
- a tényleges kártyanév csak külön döntés után kerül át a CARDS_MASTER lapra;
- névprofilozásnál figyelni kell a Fajra, Kasztra, Klánra, képességre, világbeli szerepre és mechanikai szerepre.

---

# 4. Javasolt új szöveges exportok

## 4.1 Birodalmonkénti TSV

Minden Birodalom külön TSV fájlban:

```text
cards_by_realm/IGNIS.tsv
cards_by_realm/AQUA.tsv
...
```

Előny:

- kisebb fájlok;
- könnyebb olvasni;
- nem kell egész Excel-munkafájlt feldolgozni;
- Klánonként is könnyebben szűrhető.

## 4.2 Egyesített TSV

```text
all_cards.tsv
```

Kiegészített oszlopokkal:

- `Forrás_lap`
- `Forrás_sor`

Ezek segítenek visszatalálni az Excel-helyre.

## 4.3 JSONL

```text
all_cards.jsonl
```

Egy sor = egy kártya.

Előny:

- gépileg könnyen olvasható;
- egy kártya teljes adata egy objektumban van;
- később validálásra, diffelésre és scriptelésre is jó.

---

# 5. Új munkaszabály

A továbbiakban kártyasor-javításkor a preferált kimenet:

1. auditösszefoglaló;
2. mezőszintű javítólista;
3. auditlog / decisionlog szöveg;
4. csak indokolt esetben teljes 22 oszlopos sor.

A teljes 22 oszlopos sor chatben túl kockázatos, ezért nem alapértelmezett munkamódszer.
