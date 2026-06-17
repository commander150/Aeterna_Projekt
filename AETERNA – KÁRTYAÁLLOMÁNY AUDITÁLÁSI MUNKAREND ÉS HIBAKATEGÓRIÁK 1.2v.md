# AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK

## VERZIÓ / DOKUMENTUMSTÁTUSZ

A jelen dokumentum az AETERNA kártyaállományának auditálási és újratervezési munkarendjét rögzíti.

A dokumentum nem hivatalos szabályforrás, nem alapjáték-főforrás, nem kiegészítő-főforrás, nem kártyatáblázat, és nem önálló kártyatervezési katalógus.

Feladata az, hogy meghatározza, milyen sorrendben, milyen szempontok szerint, milyen hibakategóriákkal és milyen státuszolási logikával kell vizsgálni a `cards.xlsx` kártyaállományt.

A dokumentum a következő aktív forrásokra és segéddokumentumokra támaszkodik:

- AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS
- AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS
- AETERNA – KÁRTYATERVEZÉSI KATALÓGUS ÉS HASZNÁLHATÓ ELEMEK
- AETERNA – ÖTLETLÁDA ÉS NYITOTT TERVEK
- Aeterna kártyatáblázat – oszlopszabvány
- cards.xlsx
- tesztprogram- és warning-triage dokumentumok

A jelen dokumentum nem ír felül semmilyen hivatalos főforrást. Ha az audit során a kártyaadat, a természetes kártyaszöveg, a structured mező vagy az engine-viselkedés eltér a hivatalos főforrásoktól, akkor a hivatalos főforrások az elsődlegesek.

---

## Verziótörténet

### 1.0v verzió

Módosítás típusa: dokumentum létrehozása / kártyaállomány-audit munkarend kialakítása

Érintett részek: teljes dokumentum

Státusz: aktív audit- és újratervezési munkadokumentum

Változás leírása:

A jelen verzióban létrejött az AETERNA kártyaállomány auditálási munkarendjének első hivatalos munkaváltozata.

A dokumentum célja, hogy a `cards.xlsx` javítása és az alapjátékos kártyák újratervezése előtt rögzítse:

- az audit sorrendjét;
- az auditált mezők körét;
- a hibakategóriákat;
- a kártyák státuszolásának módját;
- az azonnal javítható és későbbi döntést igénylő hibák elválasztását;
- a structured / canonical mezők ellenőrzési logikáját;
- a kiegészítői, archív vagy nem aktív elemek kezelését;
- a balanszgyanúk és engine-gyanúk jelölését;
- valamint az auditkör lezárásának feltételeit.

Verziózási megjegyzés:

Az egyes kártyák státuszának, hibáinak vagy javításainak rögzítése önmagában nem igényel új dokumentumverziót. Új verzió akkor szükséges, ha az audit módszertana, hibakategória-rendszere, munkasorrendje, státuszolási logikája vagy a használt forráshierarchia módosul.

---

### 1.1v verzió

Módosítás típusa: auditmódszertani pontosítás / structured-bővítési igények kezelése / hibakategória-kiegészítés

Érintett részek: 7. Hibakategóriák; 13. Structured / canonical mezők auditja; 17. Engine-gyanú jelölése; 21. Kimeneti formátum és munkanapló

Státusz: aktív audit- és újratervezési munkadokumentum, bővített structured-audit eljárással

Változás leírása:

A jelen verzió pontosítja, hogyan kell kezelni azokat az audit során előkerülő eseteket, amikor egy kártya természetes szövege szabályilag értelmezhető és megtartható, de a jelenlegi structured mezőkészlet nem tartalmaz elég pontos Trigger_Felismerve, Hatáscímkék vagy más szabványértéket a hatás leírására.

A VENTUS / Viharhozók audit során több olyan ismétlődő mechanikai helyzet jelent meg, amely a meglévő structured mezőkkel csak közelítően volt jelölhető. Ide tartozik különösen a támadás befejezésére reagáló hatás, a harcban ellenséges Entitás elpusztítására reagáló hatás, a Kimerülés eseményére reagáló hatás, az aktiválható saját képesség, a Visszaállítás megakadályozása, a triggerelt képesség duplikálása, az extra Betörés fázis és a Pecsét-feltörés megelőzése.

A jelen módosítás alapján az ilyen eseteket nem kell automatikusan kártyaszöveg-hibaként vagy képességmódosítási igényként kezelni. Ha a természetes kártyaszöveg működőképes, a lap koncepciója megtartható, és a probléma elsősorban a structured értékkészlet szűkösségéből ered, akkor a lapot structured-bővítési igénnyel kell jelölni.

A structured-bővítési igény munkaszintű jelölés, nem automatikus szabványfrissítés. Az új értékek csak akkor válnak végleges structured szabványértékké, ha a kártyatáblázat-oszlopszabványban és szükség esetén a táblázatos validációs listákban külön átvezetésre kerülnek.

Verziózási megjegyzés:

A jelen módosítás azért igényel új dokumentumverziót, mert nem egyetlen kártya javításáról van szó, hanem az audit módszertanának kiegészítéséről. A dokumentum innentől külön kezeli azt az esetet, amikor egy lap nem feltétlenül kártyaszöveg-hibás, hanem a jelenlegi structured mezőkészlet nem elég részletes a pontos gépi jelöléséhez.

### 1.2v verzió

Módosítás típusa: structured-bővítési eljárás pontosítása / VENTUS Égbolt Úrai auditból származó triggerérték átvezetési példája

Érintett részek: 7.12 Structured-bővítési igény; 13. Structured / canonical mezők auditja; 21. Kimeneti formátum és munkanapló

Státusz: aktív audit- és újratervezési munkadokumentum, pontosított structured-bővítési átvezetési eljárással

Változás leírása:

A VENTUS / Égbolt Úrai Klán auditja alapján pontosításra kerül a structured-bővítési igények kezelése abban az esetben, amikor egy korábban hiányzó structured érték az audit során először bővítési jelöltként jelenik meg, majd később a kártyatáblázat-oszlopszabványba is bekerül.

Az audit során több olyan Jel és reakciós hatás jelent meg, amely akkor indul, amikor az ellenfél Igéje vagy Rituáléja célpontként választ egy saját Entitást vagy saját Légies Entitást. Erre a korábbi structured triggerértékek csak pontatlanul voltak használhatók, ezért az alábbi új Trigger_Felismerve érték került bevezetésre a kártyatáblázat-oszlopszabványban:

`on_enemy_spell_or_ritual_target`

A jelen dokumentum frissítése nem új structured értéklistát hoz létre, és nem írja felül a kártyatáblázat-oszlopszabványt. Célja kizárólag annak rögzítése, hogy az ilyen eseteket auditmódszertani szinten hogyan kell kezelni:

* először structured-bővítési igényként kell jelölni, ha a természetes kártyaszöveg működőképes, de nincs elég pontos structured érték;
* a hiányzó értéket külön meg kell nevezni az auditbejegyzésben;
* ha az érték később bekerül a kártyatáblázat-oszlopszabványba, a hozzá tartozó kártyasorok structured mezői már nem közelítő értékkel, hanem az új szabványos értékkel javíthatók;
* a szabványfrissítés után az érintett lapoknál a structured-bővítési igény lezárható vagy átvezetettként jelölhető.

Példa a jelen frissítés alapján:

Hiányzó structured érték:
`on_enemy_spell_or_ritual_target`

Érintett mező:
`Trigger_Felismerve`

Eredeti probléma:
A kártya nem egyszerűen ellenséges Ige célzására vagy ellenséges Ige/Rituálé kijátszására reagál, hanem arra, amikor az ellenfél Igéje vagy Rituáléja célpontként választ egy saját lapot, saját Entitást vagy saját Légies Entitást.

Átvezetési státusz:
A hiányzó triggerérték a kártyatáblázat-oszlopszabvány frissítésével szabványosított értékké válik, ezért az érintett kártyák structured mezőiben használható.

Verziózási megjegyzés:

A jelen módosítás nem egyetlen kártya javítása, hanem az auditmódszertan structured-bővítési átvezetési lépésének pontosítása. Ezért a dokumentum verziója 1.2v-re frissíthető.

---

## Főindex

0. Dokumentumstátusz  
1. A dokumentum célja  
2. Forráshierarchia  
3. Az audit fő célja  
4. Az audit alapelvei  
5. Auditálási sorrend  
6. Vizsgált adatmezők  
7. Hibakategóriák  
8. Kártyastátuszok az audit során  
9. Azonnal javítható hibák  
10. Döntést igénylő hibák  
11. Ötletládába mentendő elemek  
12. Kiegészítőbe vagy későbbi kiadásba áthelyezendő elemek  
13. Structured / canonical mezők auditja  
14. Természetes kártyaszöveg auditja  
15. Szabályforrás-megfelelési audit  
16. Balanszgyanú jelölése  
17. Engine-gyanú jelölése  
18. Warning-triage kapcsolódás  
19. Auditkörök javasolt sorrendje  
20. Első auditkör javasolt kezdése  
21. Kimeneti formátum és munkanapló  
22. Audit lezárási feltételei  
23. Záró alapelv  

---

## 0. Dokumentumstátusz

A jelen dokumentum aktív audit- és újratervezési munkadokumentum.

Nem szabályforrás, hanem munkarendi segédlet.

A dokumentum feladata az, hogy a kártyaállomány vizsgálata során követhetővé tegye:

- mit kell ellenőrizni;
- milyen sorrendben kell haladni;
- mikor kell javítani;
- mikor kell csak jelölni;
- mikor kell döntést kérni;
- mikor kell Ötletládába menteni;
- mikor kell kiegészítői vagy booster packhoz kötött státuszt adni;
- és mikor kell engine- vagy tesztprogram-oldali problémát jelezni.

A dokumentum elsődlegesen a jelenlegi alapjátékos kártyaújratervezési munkát támogatja, de a módszertana később használható kiegészítői, booster packhoz kötött vagy reprint / új kiadási kártyák auditálásánál is.

---

## 1. A dokumentum célja

A dokumentum célja, hogy egységes auditálási módszert adjon a `cards.xlsx` kártyaállomány javításához és újratervezéséhez.

Az audit nem pusztán helyesírási vagy táblázatjavítási feladat.

A kártyák vizsgálatakor egyszerre kell ellenőrizni:

- a kártya alapadatait;
- a laptípust;
- a Birodalmat;
- a Klánt;
- a Fajt;
- a Kasztot;
- a Magnitúdó és Aura értéket;
- az ATK / HP arányt;
- a természetes kártyaszöveget;
- a structured / canonical mezőket;
- a kártya státuszát;
- a főforrásokkal való összhangot;
- a kiegészítői vagy archív elemek esetleges hibás használatát;
- a balanszgyanút;
- valamint az engine-kompatibilitást.

A dokumentum célja nem az, hogy minden kártyát azonnal véglegesen átírjon. A cél először az, hogy a teljes állomány auditálható, kategorizálható és biztonságosan javítható legyen.

---

## 2. Forráshierarchia

A kártyaállomány auditja során az alábbi forráshierarchiát kell követni:

1. AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS
2. AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS
3. AETERNA – KÁRTYATERVEZÉSI KATALÓGUS ÉS HASZNÁLHATÓ ELEMEK
4. Aeterna kártyatáblázat – oszlopszabvány
5. AETERNA – ÖTLETLÁDA ÉS NYITOTT TERVEK
6. cards.xlsx
7. engine / tesztprogram / warning-triage / runtime auditanyagok

Az alapjátékos kártyák elsődleges szabályi ellenőrzése az alapjáték-főforrás alapján történik.

A kiegészítői elemek ellenőrzése a kiegészítő-főforrás alapján történik.

A kártyatervezési katalógus a használható elemek, státuszok, tiltott / archív elemek, kulcsszavak, Birodalmak, Klánok, Fajok, Kasztok, Vérvonalak és ritkasági / kiadási elvek gyakorlati segédlete.

A kártyatáblázat-oszlopszabvány határozza meg, hogyan kell kitölteni a structured / canonical mezőket.

Az Ötletláda nem ad aktív használati engedélyt, csak a még nem végleges ötletek megőrzésére és későbbi döntés-előkészítésére szolgál.

---

## 3. Az audit fő célja

Az audit fő célja annak eldöntése, hogy egy adott kártya:

- megtartható-e alapjátékos kártyaként;
- javítandó-e alapjátékos formában;
- teljes újraírást igényel-e;
- kiegészítőbe vagy későbbi booster packba helyezendő-e;
- Ötletládába mentendő-e;
- archív / nem aktív státuszú-e;
- vagy elvetendő-e.

Az audit másodlagos célja, hogy feltárja:

- a hibás adatmezőket;
- a Faj / Kaszt / Klán / Birodalom keveredéseket;
- a régi terminológiai maradványokat;
- a kiegészítői mechanikák hibás alapjátékos használatát;
- a structured mezők hibáit;
- az engine-szempontból bizonytalan hatásokat;
- a túl erős vagy túl gyenge kártyagyanúkat;
- és azokat a lapokat, amelyek külön tesztprogramos vizsgálatot igényelnek.

---

## 4. Az audit alapelvei

I. Egy kártyát nem szabad automatikusan törölni csak azért, mert hibás vagy régi szöveggel rendelkezik.

II. Először mindig a kártya státuszát kell meghatározni.

III. Az alapjátékos kártyát alapjátékos forrás alapján kell javítani.

IV. Kiegészítői mechanika nem maradhat alapjátékos kártyán külön döntés nélkül.

V. Archív vagy nem aktív elem nem használható aktív kártyatervezési alapként.

VI. Ha egy kártya koncepciója jó, de a jelenlegi szövege hibás, a lap újraírandó, nem automatikusan elvetendő.

VII. Ha egy kártya érdekes, de nem illeszkedik a jelenlegi munkafázisba, az Ötletládába menthető.

VIII. Ha egy kártya structured mezői hibásak, de a természetes szöveg érthető, structured javítás szükséges.

IX. Ha a természetes szöveg és a structured mezők eltérnek, a kártya értelmezési hibás.

X. Ha a kártya szabályilag helyesnek tűnik, de engine-szempontból bizonytalan, engine-gyanúval kell jelölni.

XI. Ha a kártya szabályilag és technikailag működhet, de gyanúsan erős vagy gyenge, balanszgyanúval kell jelölni.

XII. Az audit nem helyettesíti a későbbi tesztprogramos validációt.

---

## 5. Auditálási sorrend

Az auditot nem érdemes egyszerre az egész kártyaállományra rázúdítani.

Javasolt sorrend:

1. Táblaszerkezeti ellenőrzés
2. Alapadatok ellenőrzése
3. Laptípus ellenőrzése
4. Birodalom és Klán ellenőrzése
5. Faj és Kaszt ellenőrzése
6. Magnitúdó / Aura / ATK / HP elsődleges ellenőrzése
7. Kulcsszavak felismerése
8. Természetes kártyaszöveg ellenőrzése
9. Structured / canonical mezők ellenőrzése
10. Kártyastátusz meghatározása
11. Hibakategória hozzárendelése
12. Javítási javaslat vagy újraírási irány megadása
13. Balanszgyanú jelölése
14. Engine-gyanú jelölése
15. Tesztprogramos vizsgálati igény jelölése

Az első auditkör célja nem a végleges balansz, hanem a használhatósági és szabálymegfelelési állapot feltárása.

---

## 6. Vizsgált adatmezők

A kártyatáblázat auditja során a következő mezőket kell vizsgálni:

1. Kártya név
2. Típus
3. Birodalom
4. Klán
5. Faj
6. Kaszt
7. Magnitudó
8. Aura
9. ATK
10. HP
11. Képesség
12. Képesség_Canonical
13. Zóna_Felismerve
14. Kulcsszavak_Felismerve
15. Trigger_Felismerve
16. Célpont_Felismerve
17. Hatáscímkék
18. Időtartam_Felismerve
19. Feltétel_Felismerve
20. Gépi_Leírás
21. Értelmezési_Státusz
22. Engine_Megjegyzés

Az audit során minden sornál ellenőrizni kell, hogy a mezők nem tolódtak-e el, nincs-e üres cella, és a nem releváns mezők megfelelően `blank` vagy `none` értékkel szerepelnek-e.

---

## 7. Hibakategóriák

Az audit során az alábbi hibakategóriákat kell használni.

### 7.1 Táblaszerkezeti hiba

A sor nem felel meg a 22 oszlopos szabványnak.

Ide tartozik:

- hiányzó mező;
- extra mező;
- üres cella;
- oszlopeltolódás;
- rossz oszlopsorrend;
- `blank` / `none` hiánya.

Javasolt státusz:

**Szerkezeti javítás szükséges**

### 7.2 Alapadat-hiba

A kártya neve, típusa, Birodalma, Klánja, Faja, Kasztja vagy alapértéke hibás vagy nem szabványos.

Ide tartozik:

- nem hivatalos laptípus;
- hibás Birodalom;
- Klán és Birodalom keveredése;
- Faj és Kaszt keveredése;
- kivezetett Kaszt;
- archív Fajnév;
- hibás Magnitúdó;
- hibás Aura;
- nem-Entitáson szereplő ATK / HP;
- Entitáson hiányzó ATK / HP.

Javasolt státusz:

**Adatjavítás szükséges**

### 7.3 Laptípus-hiba

A kártya rossz laptípusba van sorolva, vagy régi / nem hivatalos laptípus-megnevezést használ.

Ide tartozik:

- Varázslat mint hivatalos típus;
- Csapda mint hivatalos típus;
- Field / Spell / Trap idegen rendszerből átvett típusnév;
- Sík, Jel, Ige és Rituálé összekeverése;
- Entitásként kezelt nem-Entitás;
- nem-Entitásként kezelt Entitás.

Javasolt státusz:

**Laptípus javítandó**

### 7.4 Faj / Kaszt / Vérvonal hiba

A kártya Faj, Kaszt vagy Vérvonal rétege hibásan van kezelve.

Ide tartozik:

- Faj és Kaszt perjeles keverése egy mezőben;
- Élőholt Kasztként;
- Alap Kaszt használata;
- Elemi Lény az Elementál helyett;
- Fénylény aktív Fajként;
- Kozmikus aktív Fajként külön döntés nélkül;
- Vérvonal Fajként kezelése;
- Kasztból automatikus mechanikai jogosultság levezetése.

Javasolt státusz:

**Azonosító-réteg javítandó**

### 7.5 Szabályszöveg-hiba

A természetes kártyaszöveg pontatlan, régi terminológiát használ, kétértelmű, vagy ellentmond a főforrásnak.

Ide tartozik:

- „lény” Entitás helyett;
- „varázslat” hivatalos kategóriaként;
- „csapda” Jel helyett;
- „pusztuláskor” Visszhang helyett, ha valójában Ürességbe kerülésről van szó;
- „sebzés a Pecsétnek” Pecsét-feltörés helyett;
- „ugyanott lévő Zenit-Entitás” pontatlan megfogalmazás;
- trigger, célpont, hatás vagy időtartam hiánya;
- túl hangulati, nem szabályi szöveg.

Javasolt státusz:

**Szabályszöveg javítandó**

### 7.6 Structured mezőhiba

A kártya természetes szövege és structured / canonical mezői nem fedik egymást, vagy valamelyik structured mező rossz kategóriát tartalmaz.

Ide tartozik:

- trigger és hatás keverése;
- célpont és zóna keverése;
- kulcsszó és hatáscímke keverése;
- `trap` rossz mezőben;
- `burst` rossz zónaként;
- időtartam hatáscímke nélkül;
- canonical szöveg túl általános;
- Gépi_Leírás és Engine_Megjegyzés keveredése;
- Értelmezési_Státusz hiánya bizonytalan lapnál.

Javasolt státusz:

**Structured mező javítandó**

### 7.7 Státuszhiba

A kártya olyan elemet használ, amely nem illik a kártya jelenlegi státuszához.

Ide tartozik:

- alapjátékos kártyán kiegészítői kulcsszó;
- alapjátékos kártyán kiegészítő Birodalom;
- alapjátékos kártyán Avatár / Evolúció / Extra Pakli;
- archív mechanika aktívként kezelése;
- Ötletládás elem aktív kártyán;
- booster packhoz kötött elem alapjátékos készletben jelölés nélkül.

Javasolt státusz:

**Státusz tisztázandó**

### 7.8 Kiegészítői / archív mechanika hibás használata

A kártya olyan régi vagy kiegészítői mechanikát használ, amely nem lehet aktív alapjátékos elem.

Ide tartozik:

- Túlterhelés;
- Lopakodás;
- Menedék;
- Lélekőrző;
- Kiképzés;
- Túltöltés;
- Jövőbelátás X;
- Csapásmérő Osztag;
- Álhír;
- Gyökérzet;
- Orgyilkosság;
- Tiszta Hangolás;
- Pecsétprofil-rendszer;
- Avatár;
- Evolúció;
- Extra Pakli;
- Aura-égés;
- Megbonthatatlan Szövetség;
- Soft Penalty;
- kombinált Birodalmi fizetés külön döntés nélkül.

Javasolt státusz:

**Kiegészítőbe / Ötletládába / újraírásra jelölendő**

### 7.9 Balanszgyanú

A kártya szabályilag lehetséges, de értékei, hatása vagy kombinációi alapján túl erősnek, túl gyengének vagy torzítónak tűnik.

Ide tartozik:

- túl olcsó nagy test;
- túl olcsó lapelőny;
- túl erős Riadó;
- túl könnyen ismételhető Visszhang;
- túl korai Pecsétfenyegetés;
- túl erős Oltalom + gyógyítás;
- Gyorsaság + Hasítás magas ATK mellett;
- Rezonancia + lapelőny;
- Légies + magas ATK;
- Métely + tömeges sebzés;
- Kényszerítés + támadásbüntetés.

Javasolt státusz:

**Balanszteszt szükséges**

### 7.10 Engine-gyanú

A kártya szabályilag értelmezhető, de nem biztos, hogy a jelenlegi engine helyesen tudja kezelni.

Ide tartozik:

- összetett célpontválasztás;
- többzónás hatás;
- késleltetett trigger;
- állapotjelölő;
- Pecsétre ható speciális szabály;
- Domíniumon belüli mozgatás;
- visszajátszás / ismétlés;
- replacement-szerű hatás;
- reakciós ablakban működő összetett Ige vagy Jel;
- card-local handler igénye;
- structured mezőkből nem modellezhető hatás.

Javasolt státusz:

**Engine-audit szükséges**

### 7.11 Tesztprogramos gyanú

A kártya viselkedését tényleges futásokkal kell ellenőrizni.

Ide tartozik:

- túl gyors győzelmi minta;
- egyoldalú matchup;
- túl gyakori Pecsét-feltörés;
- trap / Jel réteg nem aktiválódik;
- kulcsszó nem látszik működni;
- túl sok warning kapcsolódik hozzá;
- a logban rendszeresen blokkolt vagy review-needed állapotba kerül;
- ugyanaz a kártya több seedben is torz eredményt okoz.

Javasolt státusz:

**Tesztprofilban vizsgálandó**

### 7.12 Structured-bővítési igény

A structured-bővítési igény olyan auditpont, amikor a kártya természetes szövege szabályilag értelmezhető, de a jelenlegi structured mezőkészlet nem tartalmaz elég pontos értéket a hatás gépi jelölésére.

Ide tartozik különösen:

hiányzó Trigger_Felismerve érték;
hiányzó Hatáscímkék érték;
olyan hatás, amely csak közelítő structured értékkel írható le;
olyan trigger, amely nem azonos pontosan egyik meglévő triggerrel sem;
olyan mechanikai minta, amely több kártyán is előfordulhat;
olyan engine-előkészítő jelölés, amely később oszlopszabvány- vagy validációs lista bővítését igényelheti.

Javasolt jelölések:

structured_trigger_hiány
structured_hatáscímke_hiány
structured_bővítési_jelölt
approx_trigger
approx_effect_tag

Javasolt státusz:

Structured-bővítési jelölt

Fontos:

A structured-bővítési igény önmagában nem jelenti azt, hogy a kártya képessége hibás. Ha a természetes kártyaszöveg egyértelmű, a célpont, időtartam, trigger és hatás szabályilag értelmezhető, akkor először a structured mezőkészlet bővítését vagy pontosítását kell mérlegelni.

Kártyaszöveget csak akkor kell módosítani, ha a probléma nem oldható meg pontosabb structured jelöléssel, vagy ha a természetes szöveg is túl tág, hiányos, ellentmondásos vagy főforrással ütköző.

Példák structured-bővítési igényre:

a hatás akkor indul, amikor egy Entitás befejezi a támadását, de nincs pontos támadásbefejezési trigger;
a hatás akkor indul, amikor egy Entitás harcban elpusztít egy ellenséges Entitást, de a meglévő trigger csak sebzésokozást jelöl;
a lap akkor reagál, amikor Kimerült állapotba kerül, de nincs külön Kimerülés-trigger;
a lap aktiválható saját képességet tartalmaz, de a jelenlegi triggerlista csak automatikus eseménytriggereket kezel;
egy hatás megakadályozza a Visszaállítást, de nincs külön erre szolgáló hatáscímke;
egy hatás megakadályozza a Pecsét-feltörést, de nem magát a támadást érvényteleníti.
a lap akkor reagál, amikor az ellenfél Igéje vagy Rituáléja célpontként választ egy saját Entitást, saját Légies Entitást vagy más, kártyaszövegben meghatározott saját célpontot, de a meglévő triggerlista csak külön ellenséges Ige-célzást vagy általános Ige/Rituálé-kijátszást tud jelölni.

---

## 8. Kártyastátuszok az audit során

Az audit során minden kártya kapjon munkastátuszt.

Javasolt státuszok:

### 8.1 Rendben / megtartható

A kártya alapadatai, szövege és structured mezői elfogadhatóak.

### 8.2 Kisebb adatjavítás szükséges

A kártya koncepciója jó, de kisebb mezőhibák javítandók.

### 8.3 Szövegjavítás szükséges

A természetes kártyaszöveg pontatlan vagy nem szabványos.

### 8.4 Structured javítás szükséges

A természetes szöveg érthető, de a structured / canonical mezők hibásak.

### 8.5 Teljes újraírás szükséges

A kártya megtartható alapötlettel rendelkezik, de a jelenlegi szöveg vagy működés nem használható.

### 8.6 Státusz tisztázandó

Nem világos, hogy a kártya alapjátékos, kiegészítői, booster packhoz kötött, archív vagy Ötletládás.

### 8.7 Kiegészítőbe áthelyezendő

A kártya kiegészítői mechanikára épül, ezért nem maradhat alapjátékos kártyaként.

### 8.8 Ötletládába mentendő

A kártya érdekes, de jelenleg nincs használható aktív státusza.

### 8.9 Archív / nem aktív

A kártya megőrizhető történeti vagy referencia céllal, de nem kerül aktív használatba.

### 8.10 Elvetendő

A kártya koncepciója nem illeszkedik a jelenlegi rendszerbe, és nem érdemes újrahasznosítani.

---

## 9. Azonnal javítható hibák

Azonnal javítható hibának számít, ha a probléma nem igényel szabályi vagy koncepcionális döntést.

Ide tartozik:

- elgépelés;
- rossz kis- vagy nagybetű;
- hivatalos névváltozat javítása;
- Elemi Lény → Elementál;
- Varázslat típus → Ige vagy Rituálé, ha a szöveg egyértelmű;
- Csapda → Jel, ha a szöveg egyértelmű;
- Faj / Kaszt mező szétválasztása, ha egyértelmű;
- `blank` / `none` pótlása;
- structured mező eltolódás javítása;
- egyértelmű triggermező javítása;
- egyértelmű célpontmező javítása;
- egyértelmű hatáscímke javítása.

Az azonnali javításokat is dokumentálni kell, de nem szükséges minden esetben külön döntési kör.

---

## 10. Döntést igénylő hibák

Döntést igényel minden olyan hiba, ahol a javítás nem egyértelmű.

Ide tartozik:

- nem világos laptípus;
- nem világos Birodalom;
- nem világos Klán;
- Faj vagy Kaszt státusza bizonytalan;
- Pszichikus, Dinoszaurusz, Gomba vagy hasonló vizsgálandó azonosító;
- Vérvonal használata;
- Hős Kaszt és egyedi státusz kapcsolata;
- alapjátékos vagy kiegészítői státusz kérdése;
- régi mechanika újraírása;
- kiegészítői kulcsszó alapjátékos megfelelőjének keresése;
- erősen balanszérzékeny értékek módosítása;
- engine-szempontból új logikát igénylő hatás.

A döntést igénylő hibákat nem szabad automatikusan javítani.

Ezeket külön auditmegjegyzéssel kell jelölni.

---

## 11. Ötletládába mentendő elemek

Ötletládába kell menteni azt az elemet, amely:

- érdekes, de nem illeszkedik az alapjáték jelenlegi újratervezésébe;
- nem rendelkezik végleges szabályi státusszal;
- későbbi booster packban vagy kiegészítőben hasznos lehet;
- új Klán, Faj, Kaszt, Vérvonal vagy mechanika ötletét hordozza;
- túl nagy rendszermódosítást igényelne most;
- archív forrásból származik, de nem akarjuk elveszíteni;
- kártyakoncepcióként jó, de jelenleg nincs megfelelő szabályi helye.

Az Ötletládába mentés nem aktív használati engedély.

Az Ötletládából bármely elem csak külön döntés, audit, státuszváltás és megfelelő dokumentumba történő átvezetés után válhat aktív kártyatervezési elemmé.

---

## 12. Kiegészítőbe vagy későbbi kiadásba áthelyezendő elemek

Kiegészítőbe vagy későbbi kiadásba kell áthelyezni azt a kártyát vagy kártyaelemet, amely:

- kiegészítői kulcsszót használ;
- kiegészítő Birodalomhoz tartozik;
- Avatár / Evolúció / Extra Pakli rendszerre épül;
- Pecsétprofil-rendszert használ;
- Megbonthatatlan Szövetség vagy Csapásmérő Osztag jellegű kapcsolt mechanikát használ;
- későbbi booster packhoz illő új Klánt vagy altémát vezetne be;
- alapjátékos Birodalmat bővít, de nem az első alapjátékos kártyakészlet részeként;
- promóciós, collector, reprint vagy alternatív art státuszt igényel.

Az áthelyezés nem jelenti a kártya elvetését.

Azt jelenti, hogy nem a jelenlegi alapjátékos kártyaújratervezési körben kell véglegesíteni.

---

## 13. Structured / canonical mezők auditja

A structured / canonical mezők auditjánál a kártyatáblázat-oszlopszabvány az elsődleges technikai referencia.

A vizsgálat fő kérdései:

1. A sor pontosan 22 mezőből áll?
2. Nincs üres cella?
3. A nem releváns mezők `blank` vagy `none` értékkel szerepelnek?
4. A Képesség_Canonical ugyanazt jelenti, mint a természetes Képesség mező?
5. A Zóna_Felismerve valóban zónát jelöl?
6. A Kulcsszavak_Felismerve csak valódi kulcsszót tartalmaz?
7. A Trigger_Felismerve tényleges triggerpontot jelöl?
8. A Célpont_Felismerve tényleges célpontot jelöl?
9. A Hatáscímkék tényleges hatást jelölnek?
10. Az Időtartam_Felismerve nem marad hatás nélkül?
11. A Feltétel_Felismerve ellenőrizhető feltételt tartalmaz?
12. A Gépi_Leírás rövid és értelmezhető?
13. Az Értelmezési_Státusz jelzi a bizonytalanságokat?
14. Az Engine_Megjegyzés nem keveredik a szabályszöveggel?
15. A structured mezők nem tartalmaznak hangulati vagy fejlesztői kommentet?

Ha a structured mezők nem fedik a természetes szöveget, a kártya structured javítást igényel.

Ha a természetes szöveg sem egyértelmű, először a kártyaszöveget kell javítani.

Ha a structured mezők nem fedik a természetes szöveget, először meg kell határozni, hogy a probléma a kártyaszövegben vagy a structured értékkészletben van-e.

Ha a természetes kártyaszöveg is pontatlan, túl tág, hiányos vagy ellentmondásos, akkor kártyaszöveg-javítás szükséges.

Ha azonban a természetes kártyaszöveg szabályilag értelmezhető, és a probléma abból ered, hogy a jelenlegi Trigger_Felismerve, Hatáscímkék vagy más structured mező nem tartalmaz elég pontos értéket, akkor a lapot structured-bővítési igénnyel kell jelölni.

Ilyenkor a közelítő structured érték ideiglenesen használható, de az Engine_Megjegyzés, Javítási_Megjegyzés, Hibakategória vagy auditnapló mezőben jelezni kell, hogy az érték csak közelítő.

A structured-bővítési igényt külön kell naplózni, ha:

az adott hiány több lapon is előfordul;
a hatás engine-oldali feldolgozása külön logikát igényelhet;
a jelenlegi mezőkészlet rendszeresen pontatlan structured leírást eredményezne;
vagy az új érték később oszlopszabványba emelhető.

A structured-bővítési igény nem írja felül a kártyatáblázat-oszlopszabványt. Csak azt jelzi, hogy a szabvány későbbi bővítése indokolt lehet.

Ha egy korábban structured-bővítési igényként jelölt érték időközben bekerült a kártyatáblázat-oszlopszabványba, akkor az érintett kártyák structured mezőit már az új szabványos értékkel kell javítani. Ilyenkor nem kell tovább közelítő trigger- vagy hatáscímke-értéket használni.

Példa:

Ha egy lap az ellenfél Igéje vagy Rituáléja által végzett célpontválasztásra reagál, és az új `on_enemy_spell_or_ritual_target` érték már szerepel a kártyatáblázat-oszlopszabványban, akkor a `Trigger_Felismerve` mezőben ezt az értéket kell használni, nem pedig a pontatlanabb `on_enemy_spell_target` vagy `on_enemy_spell_or_ritual_played` értéket.

---

## 14. Természetes kártyaszöveg auditja

A természetes kártyaszöveg auditjánál ellenőrizni kell, hogy a szöveg:

- hivatalos terminológiát használ-e;
- megmondja-e a triggerpontot;
- megmondja-e a célpontot;
- megmondja-e a hatást;
- megmondja-e az időtartamot;
- tartalmazza-e a feltételt, ha van;
- nem keveri-e össze a Core, alapjátékos és kiegészítői elemeket;
- nem használ-e archív terminológiát;
- nem tartalmaz-e idegen TCG-ből átvett, nem AETERNA-s kategóriát;
- átvezethető-e structured mezőkbe.

A jó kártyaszöveg nem hosszú, hanem pontos.

A szöveg akkor megfelelő, ha egy játékos, egy szabályaudit és az engine ugyanazt a működést tudja belőle kiolvasni.

---

## 15. Szabályforrás-megfelelési audit

A szabályforrás-megfelelési audit célja annak ellenőrzése, hogy a kártya összhangban van-e a hivatalos főforrásokkal.

Alapjátékos kártyánál ellenőrizni kell:

- alapjátékos Birodalmat használ-e;
- alapjátékos Klánt használ-e;
- alapjátékos vagy engedélyezett Fajt / Kasztot használ-e;
- alapjátékos kulcsszót használ-e;
- nem használ-e kiegészítői rendszert;
- fizetési szabálya megfelel-e az Entitás / nem-Entitás elhatárolásnak;
- nem kezeli-e a Pecsétet HP-s célpontként;
- nem keveri-e a Surge, Gondviselés, Burst, Visszhang vagy Refresh Penalty logikáját;
- nem hoz-e létre rejtett Core-szabály kivételt.

Kiegészítői kártyánál ellenőrizni kell:

- melyik kiegészítőhöz vagy későbbi kiadáshoz tartozik;
- rendelkezik-e megfelelő kiegészítői szabályi háttérrel;
- nem írja-e felül hallgatólagosan az alapjáték-főforrást;
- aktiválási feltétele egyértelmű-e;
- megfelelően jelölt-e a kártyatáblában.

---

## 16. Balanszgyanú jelölése

A balanszgyanú nem végleges ítélet.

A balanszgyanú azt jelenti, hogy a kártyát később külön tesztelni kell.

Balanszgyanús lehet egy lap, ha:

- túl gyorsan nyer;
- túl sok értéket ad alacsony költségen;
- túl nehezen eltávolítható;
- túl nagy lapelőnyt ad;
- túl erős Pecsétfenyegetést jelent;
- túl stabil védekező zárat hoz létre;
- több veszélyes kulcsszót kombinál;
- túl könnyen ismételhető;
- túl sok pakliba automatikusan bekerülne;
- vagy megszünteti a saját Birodalma természetes gyengeségét.

A balanszgyanús kártyát nem kell azonnal gyengíteni.

Először jelölni kell, majd tesztprogrammal és matchup-alapú vizsgálattal ellenőrizni.

---

## 17. Engine-gyanú jelölése

Engine-gyanú akkor merül fel, ha a kártya szabályilag értelmezhető, de a jelenlegi motor működése alapján nem biztos, hogy helyesen kezelhető.

Engine-gyanús lehet egy lap, ha:

- új triggerpontot igényel;
- több célpontot kezel;
- zónaváltási kivételt használ;
- késleltetett állapotot hoz létre;
- Pecsétet vagy Aeternalt érint speciális módon;
- Domíniumon belüli pozícióváltást kezel;
- reakciós ablakot igényel;
- Jelként vagy Burstként összetettebb időzítést használ;
- card-local handlerre szorul;
- structured mezőkből nem oldható fel;
- vagy a jelenlegi warning-triage szerint magas kockázatú mezőkombinációt tartalmaz.

Engine-gyanúval kell jelölni azt az esetet is, amikor a kártya hatása olyan új vagy hiányzó structured triggerre, hatáscímkére vagy feldolgozási mintára épül, amelyet a jelenlegi structured mezőkészlet csak közelítően tud leírni.

Ide tartozhat különösen:

támadás befejezésekor történő hatás;
harcban ellenséges Entitás elpusztítására reagáló hatás;
Kimerülés eseményére reagáló hatás;
aktiválható saját képesség;
Visszaállítás megakadályozása;
triggerelt képesség duplikálása;
extra Betörés fázis;
Pecsét-feltörés megelőzése;
vagy más olyan hatás, amely új engine-oldali eseménykezelést igényelhet.

Az ilyen lap nem feltétlenül hibás. Az engine-gyanú azt jelenti, hogy a lap működését nem szabad automatikusan engine-kompatibilisnek tekinteni addig, amíg a szükséges structured és runtime kezelés nincs külön ellenőrizve.

Az engine-gyanú nem jelenti azt, hogy a kártya rossz.

Azt jelenti, hogy a kártyát nem szabad engine-kompatibilisnek tekinteni külön ellenőrzés nélkül.

---

## 18. Warning-triage kapcsolódás

A kártyaállomány auditjánál figyelembe kell venni a warning-triage szempontokat.

Nem minden warning azonos súlyú.

### 18.1 Alacsony prioritású warning

Olyan figyelmeztetés, amely inkább zaj vagy standardizációs adósság.

Példák:

- régi triggernév, ha a runtime adaptereli;
- ritka, futásban alig érintett enum-eltérés;
- dokumentációs jellegű inkonzisztencia.

### 18.2 Közepes prioritású warning

Olyan figyelmeztetés, amely rontja a tesztelés értelmezhetőségét.

Példák:

- időtartam hatáscímke nélkül;
- gyanús target-típus kombináció;
- kézben lévő lapra mutató, de nem tiszta hatás;
- structured mezőből nem egyértelmű kártyaműködés.

### 18.3 Magas prioritású warning

Olyan figyelmeztetés, amely ténylegesen félrevezető gameplay-képet adhat.

Példák:

- `trap` rossz structured mezőben;
- `burst` zónaként;
- kulcsszó helyett hatáscímke;
- hatáscímke helyett laptípus;
- olyan enum-érték, amely miatt a runtime fallbackre vagy hibás értelmezésre kényszerül.

A magas prioritású warninggal érintett kártyákat az auditban külön kell jelölni.

---

## 19. Auditkörök javasolt sorrendje

A teljes kártyaállomány auditja több körben történjen.

### 19.1 Nulladik kör – táblaszerkezeti ellenőrzés

Cél:

- 22 oszlop megléte;
- üres cellák kiszűrése;
- oszlopeltolódás keresése;
- `blank` / `none` használat egységesítése.

### 19.2 Első kör – alapadat-audit

Cél:

- Típus;
- Birodalom;
- Klán;
- Faj;
- Kaszt;
- Magnitudó;
- Aura;
- ATK;
- HP ellenőrzése.

### 19.3 Második kör – szabályszöveg-audit

Cél:

- természetes Képesség mező ellenőrzése;
- régi terminológia kiszűrése;
- kiegészítői / archív mechanikák kiszűrése;
- kártyaszöveg-sablonokhoz igazítás.

### 19.4 Harmadik kör – structured mező audit

Cél:

- canonical mező;
- zóna;
- kulcsszó;
- trigger;
- célpont;
- hatáscímke;
- időtartam;
- feltétel;
- gépi leírás;
- értelmezési státusz;
- engine megjegyzés ellenőrzése.

### 19.5 Negyedik kör – kártyastátuszolás

Cél:

- megtartható;
- javítandó;
- újraírandó;
- kiegészítőbe áthelyezendő;
- Ötletládába mentendő;
- archív;
- elvetendő státuszok kiosztása.

### 19.6 Ötödik kör – balansz- és engine-gyanúk jelölése

Cél:

- veszélyes kombinációk jelölése;
- engine-bizonytalanság jelölése;
- tesztprogramos vizsgálati igény megadása.

---

## 20. Első auditkör javasolt kezdése

Az első konkrét auditkört érdemes szűk, kezelhető egységgel kezdeni.

Javasolt kezdés:

**IGNIS alapjátékos kártyák**

Indok:

- az IGNIS erősen tempó- és sebzésalapú Birodalom;
- jól láthatók rajta a Pecsétfenyegetés, Gyorsaság, Hasítás, Riadó és sebzésalapú hatások;
- gyorsan kiderülhet, ha a kártyák túl agresszívek;
- jó első minta a structured mezők és a természetes kártyaszöveg összehangolására;
- korábban is felmerült, hogy az alapjátékos kártyák vizsgálatánál különösen fontos a kiegészítői mechanikák kizárása.

Az első auditkörben nem kell azonnal az összes IGNIS lapot véglegesen átírni.

Első cél:

- hibák kigyűjtése;
- státuszok kiosztása;
- tipikus problémák azonosítása;
- javítási minta kialakítása.

---

## 21. Kimeneti formátum és munkanapló

Minden auditált kártyáról legalább az alábbi adatokat érdemes rögzíteni:

- kártyanév;
- Birodalom;
- Klán;
- laptípus;
- jelenlegi státusz;
- hibakategória;
- rövid hibaösszefoglaló;
- javasolt javítás;
- structured mező javítás szükséges-e;
- balanszgyanú van-e;
- engine-gyanú van-e;
- Ötletládába / kiegészítőbe / archívba kerül-e;
- döntést igényel-e.

Javasolt auditbejegyzés-forma:

Kártya:
Birodalom:
Klán:
Típus:
Jelenlegi státusz:
Hibakategória:
Probléma:
Javasolt javítás:
Structured javítás:
Balanszgyanú:
Engine-gyanú:
Döntést igényel:
Megjegyzés:

Structured-bővítési igény esetén az auditbejegyzésben lehetőség szerint külön szerepeljen:

Structured-bővítési igény:
Hiányzó structured érték:
Ideiglenesen használt közelítő érték:
Javasolt új structured érték:
Érintett mező:
Érintett lapok / lapcsoport:
Engine-gyanú:
Szabványfrissítés szükséges:
Megjegyzés:

Ha a structured-bővítési igény több lapot érint, akkor nem szükséges minden egyes laphoz külön hosszú magyarázatot írni. Ilyenkor elegendő lehet egy közös auditbejegyzés, amely felsorolja az érintett lapokat és a javasolt új structured értékeket.

A döntési naplóban rögzíteni kell, hogy a probléma:

kártyaszöveg-javítást igényelt-e;
structured mezőjavítással megoldható-e;
vagy későbbi oszlopszabvány-bővítési jelöltként marad-e nyilván.

Ha az audit később táblázatba kerül, ezek a mezők külön oszlopként is használhatók.

Ha a javasolt új structured érték később bekerül a kártyatáblázat-oszlopszabványba, akkor az auditbejegyzésben vagy a kapcsolódó döntési naplóban jelezhető, hogy a structured-bővítési igény átvezetve / lezárva státuszt kapott.

Ilyenkor érdemes rögzíteni:

Átvezetett structured érték:
Szabványfrissítés verziója:
Érintett kártyák:
Átvezetés státusza:
Megjegyzés:

Példa:

Átvezetett structured érték: `on_enemy_spell_or_ritual_target`
Szabványfrissítés verziója: `kartya_tabla_szabvany 1.2v`
Érintett kártyák: VENTUS / Égbolt Úrai célzásra reagáló Jel és reakciós lapok
Átvezetés státusza: átvezetve
Megjegyzés: A korábbi közelítő triggerértékek helyett a pontosított triggerérték használható.

---

## 22. Audit lezárási feltételei

Egy auditkör akkor tekinthető lezártnak, ha:

minden érintett kártya kapott auditstátuszt;
minden ismert hiba kategorizálva van;
a döntést igénylő lapok külön listában szerepelnek;
az azonnal javítható hibák javítási javaslatot kaptak;
az Ötletládába mentendő elemek külön jelölve vannak;
a kiegészítőbe áthelyezendő elemek külön jelölve vannak;
a balanszgyanús lapok tesztelési jelölést kaptak;
az engine-gyanús lapok technikai megjegyzést kaptak;
és elkészült az auditkör rövid összefoglalója.

Az auditkör lezárása nem jelenti azt, hogy minden kártya végleg kész.

A lezárás azt jelenti, hogy a vizsgált kártyacsomag állapota ismert, rendezett, és biztonságosan javítható.

## 23. Záró alapelv

A kártyaállomány auditja nem egyszerű javítási lista, hanem a szabályforrás, a kártyatervezési katalógus, a structured mezők, a tesztprogram és az engine közötti megfeleltetési munka.

Egy kártya akkor tekinthető egészségesnek, ha:

illeszkedik a megfelelő főforráshoz;
helyes státuszban van;
a természetes szövege érthető;
a structured mezői ugyanazt jelentik;
az engine számára értelmezhető;
nem használ hibás régi vagy kiegészítői elemet;
és balanszszempontból legalább előzetesen indokolható.

Az audit célja nem az, hogy minden régi kártyát azonnal megmentsen vagy elvessen.

A cél az, hogy minden kártyáról világosan látszódjon:

mi akar lenni, milyen szabályi réteghez tartozik, mi hibás benne, hogyan javítható, és milyen további döntés vagy teszt szükséges hozzá.