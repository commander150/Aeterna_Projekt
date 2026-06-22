# AETERNA – Excel / Google Sheets munkafájl szerkezete és oszlopszabvány

Verzió: 1.2
Státusz: munkarendi segéddokumentum
Cél: rögzíteni, hogy az AETERNA kártyaadatbázisban melyik munkalap mire való, milyen oszlopai vannak, milyen szerepet tölt be a munkafolyamatban, és hogyan kell vele dolgozni.

## Verziótörténet

### 1.2v verzió

Módosítás típusa: munkafájl-validációs rend pontosítása / LOOKUPS structured értékkészlet frissítési megjegyzés / VENTUS Égbolt Úrai audit alapján új triggerérték átvezetése

Érintett részek: 5. LOOKUPS; 9.13 Structured értékkészlet és LOOKUPS frissítése; VERZIÓ-lap bejegyzési irányelve

Státusz: aktív munkarendi segéddokumentum, pontosított LOOKUPS-frissítési iránnyal

Változás leírása:

A VENTUS / Égbolt Úrai Klán auditja alapján pontosításra kerül a munkafájl structured értékkészletének és LOOKUPS / validációs listáinak frissítési rendje.

A kártyatáblázat-oszlopszabvány frissítése alapján új Trigger_Felismerve érték került bevezetésre:

`on_enemy_spell_or_ritual_target`

Ez az érték akkor használható, ha a hatás akkor indul, amikor az ellenfél Igéje vagy Rituáléja célpontként választ egy saját lapot, saját Entitást, saját Légies Entitást vagy más, kártyaszövegben meghatározott saját célpontot.

A jelen dokumentum frissítése nem új szabályt és nem új kártyahatást hoz létre. Célja annak rögzítése, hogy ha a kártyatáblázat-oszlopszabvány új structured értéket vezet be, akkor a munkafájlban használt LOOKUPS / validációs értékkészletet is ellenőrizni és szükség esetén frissíteni kell.

A jelen frissítés alapján a LOOKUPS lapon, ha a Trigger_Felismerve értékek külön validációs listában szerepelnek, fel kell venni az alábbi új értéket:

`on_enemy_spell_or_ritual_target`

A CARDS_MASTER oszlopszerkezete nem módosul. A változás kizárólag a meglévő Trigger_Felismerve mező engedélyezett / validált értékkészletét érinti.

Engine / runtime megjegyzés:

Az új triggerérték későbbi engine-oldali feldolgozást igényelhet, mert nem általános Ige/Rituálé-kijátszási eseményt, hanem célpontválasztási eseményt jelöl. Ezért az érintett lapoknál az Engine_Gyanú vagy Engine_Megjegyzés mezőben szükség esetén jelezhető, hogy a trigger runtime-támogatása későbbi ellenőrzést igényel.


## 1. A dokumentum célja

A jelen dokumentum az AETERNA kártyaadatbázis Excel / Google Sheets munkafájljának szerkezetét és használati rendjét rögzíti.

A cél az, hogy a további kártyaaudit, kártyaújratervezés, névprofilozás, termék-előkészítés, exportálás és engine-kompatibilitási munka során mindig egyértelmű legyen:

melyik munkalap mire való;
melyik lap aktív kártyaadat-forrás;
melyik lap audit-, döntési-, import-, export-, termék- vagy segédadat szerepű;
milyen oszlopokat tartalmaznak az egyes lapok;
mely mezők azonosítók;
mely mezők kézzel szerkeszthetők;
mely mezők kapcsolódnak más munkalapokhoz;
milyen formátumban kell kitölteni őket;
és milyen munkaszabályok szerint kell a fájlt módosítani.

Ez a dokumentum nem szabályforrás, nem kártyatervezési katalógus és nem játékmechanikai döntési dokumentum. A feladata kizárólag a táblázatos munkafájl szerkezetének és használatának tisztázása.

## 2. Két külön szintet kell megkülönböztetni

### 2.1 Régi / egyszerűsített cards.xlsx szint

A korábbi vagy egyszerűsített cards.xlsx kártyaadat-forrás Birodalmonként külön munkalapokat használhatott.

Például:

IGNIS
AQUA
TERRA
LUX
UMBRA
VENTUS
AETHER

Ezek a Birodalom-lapok a régi / alap 22 oszlopos kártyatáblázat-szabványt követték.

Ez a 22 oszlopos szerkezet továbbra is fontos lehet:

importált régi kártyaadatok értelmezéséhez;
runtime / engine exportokhoz;
egyszerűsített szöveges TSV-khez;
Birodalmonkénti kivonatokhoz;
korábbi cards.xlsx állományok visszaolvasásához;
illetve olyan esetekben, ahol csak a kártya alapadataira és structured mezőire van szükség.

### 2.2 Jelenlegi kártyaadatbázis munkaforrás

A jelenlegi AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.2v már nem egyszerű Birodalom-lapos cards.xlsx.

Ez egy több munkalapból álló, kibővített kártyaadatbázis-munkaforrás.

A fájl egyszerre szolgál:

aktív kártyaadatbázisként;
kártyaauditálási munkafájlként;
structured mező javítási felületként;
döntésnaplóként;
auditnaplóként;
importált eredeti adatok tárolóhelyeként;
set-, product-, printing- és booster-előkészítő táblázatként;
termékpakli- és tesztpakli-listák tárolójaként;
későbbi runtime / engine exportok előkészítő forrásaként;
névprofilozási és névaudit munkafelületként.

Ezért a jelenlegi munkafájlt nem szabad a régi 22 oszlopos cards.xlsx struktúrával azonosítani.

## 3. A munkafájl jelenlegi lapjai

Az AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.2v jelenleg 17 munkalapot tartalmaz:

1. VERZIÓ
2. README
3. CARDS_MASTER
4. AUDIT_LOG
5. LOOKUPS
6. RARITY_CODES
7. EXPORT_RUNTIME
8. EXPORT_NOTES
9. DECISION_LOG
10. IMPORT_ORIGINAL
11. SETS
12. PRODUCTS
13. CARD_PRINTINGS
14. GENERATION_PROFILES
15. PRODUCT_DECKLISTS
16. BOOSTER_POOLS
17. NAME_PROFILE

A további dokumentációban minden munkalapot külön kell ismertetni:

cél;
oszlopok;
azonosítómezők;
kapcsolódó lapok;
kézzel szerkeszthető mezők;
automatikus / export / audit szerepű mezők;
kitöltési szabályok;
tipikus hibák;
és munkafolyamatbeli szerep.

## 4. Fontos szerkezeti pontosítás: 22 oszlopos szabvány és 43 oszlopos CARDS_MASTER

A régi / alap cards.xlsx struktúra, illetve bizonyos runtime- vagy exportcélú formátumok 22 oszlopos kártyaadat-szabványt használnak.

A jelenlegi munkafájlban azonban a 3. CARDS_MASTER lap már nem 22 oszlopos, hanem egy kibővített, 43 oszlopos aktív kártyaadat-master.

Ezért a további munkában külön kell kezelni:

a 22 oszlopos alap / import / runtime / export jellegű kártyaadat-struktúrát;
és a 43 oszlopos 3. CARDS_MASTER aktív munkalapot.

A 3. CARDS_MASTER lapot nem szabad a 22 oszlopos szabvány alapján csonkítani, újragenerálni vagy rövidebb struktúrára visszavágni.

## 5. A 22 oszlopos kártyaadat-szabvány

A 22 oszlopos szerkezet a régi / egyszerűsített cards.xlsx, a Birodalmonkénti exportok és bizonyos runtime-előkészítő fájlok alapformátuma lehet.

### 5.1 Kötelező oszlopsorrend

Kártya név
Típus
Birodalom
Klán
Faj
Kaszt
Magnitudó
Aura
ATK
HP
Képesség
Képesség_Canonical
Zóna_Felismerve
Kulcsszavak_Felismerve
Trigger_Felismerve
Célpont_Felismerve
Hatáscímkék
Időtartam_Felismerve
Feltétel_Felismerve
Gépi_Leírás
Értelmezési_Státusz
Engine_Megjegyzés

### 5.2 Kötelező kitöltési szabály

A 22 oszlopos formátumban:

minden sorban pontosan 22 mező legyen;
üres cella ne maradjon;
ha nincs releváns adat: blank vagy none;
extra üres oszlop nem lehet;
hosszú szöveg miatt sem tolódhat el a sor;
structured mezőkben csak szabványosított értékek szerepeljenek;
a Kulcsszavak_Felismerve után különösen figyelni kell, hogy ne csússzon be extra oszlop;
minden exportált sor visszaellenőrizendő oszlopszám alapján.

Numerikus mezők formátuma:

A numerikus mezőkben, ha az érték egész szám, sima egész számként kell szerepelnie.

Helyes:

1
2
3
4
5

Helytelen:

1.0
2.0
3.0
4.0
5.0

Ez különösen érinti az alábbi mezőket:

Magnitudó
Aura
ATK
HP
Darabszám
Release_Order
Collector_Number, ha a munkafájl adott formátuma egyszerű sorszámként kezeli

Nem-Entitás lapoknál az ATK és HP mezőben továbbra is a munkafájlban használt standard üresérték szerepeljen, jellemzően none.

A cél az, hogy a CARDS_MASTER, az importált TSV-k, az exportok és a kézzel beillesztett blokkok ne keverjék az egész számokat tizedes formátumú értékekkel.

### 5.3 Fontos mezőértelmezések

Képesség
Természetes, magyar kártyaszöveg. Ez az emberi játékosnak szóló kártyaleírás.

Képesség_Canonical
Rövid, egységes, gépileg olvasható képesség-átírás.

Zóna_Felismerve
Az a zóna vagy zónák, amelyekhez a képesség közvetlenül kötődik.

Kulcsszavak_Felismerve
Csak valódi szabályszintű kulcsszavak. Ide nem kerülhet általános hatáscímke, például damage, draw vagy redirect.

Trigger_Felismerve
Az esemény, amely kiváltja a képességet.

Célpont_Felismerve
A végső hatás célpontja, nem feltétlenül a trigger kiváltó alanya.

Hatáscímkék
A tényleges mechanikai hatások rövid címkéi.

Időtartam_Felismerve
A hatás időtartama.

Feltétel_Felismerve
Extra feltétel vagy szűrés, amely nem trigger és nem célpont.

Gépi_Leírás
Rövid, embernek is olvasható, de gépileg követhető összefoglaló.

Értelmezési_Státusz
A structured értelmezés állapota.

Engine_Megjegyzés
Technikai / engine-szempontú megjegyzés.

## 6. A 3. CARDS_MASTER lap

### 6.1 A lap szerepe

A 3. CARDS_MASTER lap az aktív kártyaadatbázis fő munkalapja.

Ez tartalmazza a kártyák:

jelenlegi munkaszintű nevét;
típusát;
Birodalmát;
Klánját;
Faját;
Kasztját;
Magnitúdó- és Aura-adatait;
ATK / HP értékeit;
természetes kártyaszövegét;
structured / canonical mezőit;
auditstátuszait;
hibakategóriáit;
javítási megjegyzéseit;
balansz- és engine-gyanúit;
forráshivatkozásait;
döntési jelöléseit;
Ötletláda- és kiegészítői kapcsolatait;
szabályi és print azonosítóit;
set- és collector adatait;
ritkasági és treatment adatait;
art-variánsát;
print státuszát;
verzióját;
reprint kapcsolatát;
és játszhatósági státuszát.

A 3. CARDS_MASTER lapot kell elsődleges forrásként használni, amikor egy kártyát ténylegesen javítunk, státuszolunk, auditálunk vagy későbbi exporthoz előkészítünk.

### 6.2 Teljes oszlopsorrend

A 3. CARDS_MASTER lap jelenlegi oszlopszáma: 43 oszlop.

A teljes oszlopsorrend:

Kártya név
Típus
Birodalom
Klán
Faj
Kaszt
Magnitudó
Aura
ATK
HP
Képesség
Képesség_Canonical
Zóna_Felismerve
Kulcsszavak_Felismerve
Trigger_Felismerve
Célpont_Felismerve
Hatáscímkék
Időtartam_Felismerve
Feltétel_Felismerve
Gépi_Leírás
Értelmezési_Státusz
Engine_Megjegyzés
Audit_Státusz
Hibakategória
Javítási_Prioritás
Javítási_Megjegyzés
Balanszgyanú
Engine_Gyanú
Forrás_Hivatkozás
Döntést_Igényel
Ötletláda_Kapcsolat
Kiegészítői_Státusz
Szabályi_Kártya_ID
Print_ID
Set_ID
Collector_Number
Rarity
Treatment
Art_Variant
Print_Status
Version
Reprint_Of
Play_Legal_Status

### 6.3 Oszlopcsoportok

A 3. CARDS_MASTER oszlopai négy nagy csoportra bonthatók.

#### A) Alap kártyaadatok

Ide tartoznak az 1–11. oszlopok:

Kártya név
Típus
Birodalom
Klán
Faj
Kaszt
Magnitudó
Aura
ATK
HP
Képesség

Ezek adják a kártya természetes, ember által olvasható alapadatait.

#### B) Structured / canonical / engine-előkészítő mezők

Ide tartoznak a 12–22. oszlopok:

Képesség_Canonical
Zóna_Felismerve
Kulcsszavak_Felismerve
Trigger_Felismerve
Célpont_Felismerve
Hatáscímkék
Időtartam_Felismerve
Feltétel_Felismerve
Gépi_Leírás
Értelmezési_Státusz
Engine_Megjegyzés

Ezek a mezők a természetes kártyaszöveg gépileg értelmezhető, structured / runtime-előkészítő rétegét adják.

#### C) Audit- és javítási mezők

Ide tartoznak a 23–32. oszlopok:

Audit_Státusz
Hibakategória
Javítási_Prioritás
Javítási_Megjegyzés
Balanszgyanú
Engine_Gyanú
Forrás_Hivatkozás
Döntést_Igényel
Ötletláda_Kapcsolat
Kiegészítői_Státusz

Ezek a mezők mutatják, hogy a kártya milyen auditállapotban van, milyen hibája van, kell-e döntés, van-e balansz- vagy engine-gyanú, illetve kapcsolódik-e Ötletláda- vagy kiegészítői státuszhoz.

#### D) Azonosító-, kiadási és play legality mezők

Ide tartoznak a 33–43. oszlopok:

Szabályi_Kártya_ID
Print_ID
Set_ID
Collector_Number
Rarity
Treatment
Art_Variant
Print_Status
Version
Reprint_Of
Play_Legal_Status

Ezek a mezők biztosítják a kártya stabil szabályi azonosítását, nyomtatási / kiadási kezelését, ritkasági és variánskezelését, valamint azt, hogy az adott kártya milyen játékkörnyezetben használható.

### 6.4 A CARDS_MASTER oszlopainak rövid funkcióleírása

Kártya név
A kártya jelenlegi munkaszintű neve. Névprofilozás után csak külön döntéssel módosítandó.

Típus
A kártya laptípusa: Entitás, Ige, Rituálé, Jel vagy Sík.

Birodalom
A kártya Birodalma, például IGNIS, AQUA, TERRA.

Klán
A kártya Birodalmon belüli Klánja.

Faj
Entitásoknál a lény Faja. Nem-Entitásoknál általában none.

Kaszt
Entitásoknál a szerep / foglalkozás / mechanikai kaszt. Nem-Entitásoknál általában none.

Magnitudó
A lap kijátszási küszöbe.

Aura
A lap kijátszásához szükséges Aura-költség.

ATK
Entitás támadóértéke. Nem-Entitásoknál none vagy a munkafájlban használt standard érték.

HP
Entitás életereje. Nem-Entitásoknál none vagy a munkafájlban használt standard érték.

Képesség
A kártya természetes, játékosnak szóló kártyaszövege.

Képesség_Canonical
Rövid, gépileg olvasható canonical képességleírás.

Zóna_Felismerve
A képességhez közvetlenül kapcsolódó zóna vagy zónák.

Kulcsszavak_Felismerve
Csak a valódi szabályi kulcsszavak listája.

Trigger_Felismerve
A képességet kiváltó esemény, ha van.

Célpont_Felismerve
A hatás végső célpontja.

Hatáscímkék
A lap mechanikai hatásainak rövid címkéi.

Időtartam_Felismerve
A hatás időtartama.

Feltétel_Felismerve
Extra feltétel vagy szűrés, amely nem trigger és nem célpont.

Gépi_Leírás
Rövid, embernek is olvasható, de szabályos gépi összefoglaló.

Értelmezési_Státusz
Jelzi, hogy a structured értelmezés mennyire tiszta vagy bizonytalan.

Engine_Megjegyzés
Engine / runtime feldolgozáshoz kapcsolódó megjegyzés.

Audit_Státusz
A kártya aktuális auditállapota.

Hibakategória
A kártyán azonosított fő hibatípus.

Javítási_Prioritás
A javítás sürgőssége vagy fontossága.

Javítási_Megjegyzés
Rövid magyarázat arról, mit kell javítani vagy miért.

Balanszgyanú
Jelzi, hogy a lap erőszintje tesztfigyelést igényel-e.

Engine_Gyanú
Jelzi, hogy a lap engine / runtime szempontból bizonytalan-e.

Forrás_Hivatkozás
A vonatkozó forrásdokumentumra vagy szabályhelyre mutató hivatkozás.

Döntést_Igényel
Jelzi, hogy a lap vagy mező külön emberi döntést igényel-e.

Ötletláda_Kapcsolat
Kapcsolódó Ötletláda-bejegyzés, ha van.

Kiegészítői_Státusz
Jelzi, hogy a lap vagy mechanika alapjátékos, kiegészítői, boosterhez kötött, archív stb. státuszú-e.

Szabályi_Kártya_ID
Stabil, szabályi azonosító. Ezt kell elsődleges azonosítóként használni auditnál és paklilistáknál.

Print_ID
Konkrét nyomtatási / kiadási változat azonosítója.

Set_ID
A készlet / kiadás azonosítója.

Collector_Number
Gyűjtői sorszám az adott készleten belül.

Rarity
Ritkasági kategória.

Treatment
Kivitelezési / foil / treatment réteg.

Art_Variant
Képváltozat vagy art-variáns jelölése.

Print_Status
A print státusza: aktív, teszt, promo, archív stb.

Version
A kártyasor / print / munkaváltozat verziója.

Reprint_Of
Ha reprint, az eredeti kártya vagy print azonosítója.

Play_Legal_Status
Játszhatósági státusz, például CORE01_candidate vagy CORE01_test_required.

### 6.5 Munkaszabály a CARDS_MASTER szerkesztéséhez

A 3. CARDS_MASTER lap szerkesztésénél a következő szabályokat kell követni:

A Szabályi_Kártya_ID az elsődleges stabil azonosító. A kártyanév változhat, az ID nem.
A Kártya név mezőt csak külön névdöntés után szabad átvezetni.
A természetes Képesség és a structured mezők jelentése nem térhet el egymástól.
Ha a természetes szöveg jó, de a structured mezők rosszak, structured javítás szükséges.
Ha a structured mezők jók, de a természetes szöveg rossz vagy félrevezető, kártyaszöveg-javítás szükséges.
Ha a lap balansz szempontból gyanús, a Balanszgyanú mezőben kell jelölni, nem automatikusan törölni.
Ha a lap engine szempontból bizonytalan, az Engine_Gyanú és Engine_Megjegyzés mezőkben kell jelölni.
Kiegészítői vagy archív elem nem maradhat alapjátékos kártyán külön döntés nélkül.
Ha egy lap CORE01-ből valószínűleg kikerül, azt először státuszolni kell, nem azonnal törölni.
Teljes sor újragenerálása helyett lehetőség szerint mezőszintű javítólistát kell használni.
Structured értékek és CARDS_MASTER:

A Trigger_Felismerve, Hatáscímkék, Értelmezési_Státusz, Hibakategória, Audit_Státusz, Play_Legal_Status és hasonló kontrollált mezők értékeinek összhangban kell lenniük a kapcsolódó szabvány- és segédlistákkal.

Ha egy kártya természetes szövege olyan triggert vagy hatást tartalmaz, amely a jelenlegi listákkal csak közelítően írható le, akkor nem szabad automatikusan kártyaszöveget módosítani.

Ilyenkor először meg kell vizsgálni, hogy:

a kártyaszöveg szabályilag működőképes-e;
a structured mezők javíthatók-e meglévő értékekkel;
szükséges-e új structured érték;
az új értéket fel kell-e venni a kártyatáblázat-szabványba;
és szerepelnie kell-e a LOOKUPS validációs listában.

Ha új structured érték kerül bevezetésre, akkor a CARDS_MASTER érintett mezőiben csak azután érdemes egységesen használni, hogy a kapcsolódó dokumentum és a LOOKUPS / validációs lista is frissült.

Ideiglenes vagy közelítő érték használata esetén az Engine_Megjegyzés, Javítási_Megjegyzés, Hibakategória, Audit_Státusz vagy Döntést_Igényel mezőben jelölni kell, hogy az érték structured-bővítési igényhez kapcsolódik.

## 7. Munkaforrás-lapok részletesen

### 7.1 1. VERZIÓ

Cél: a fájl verziótörténetének követése.

Oszlopok:

Verzió
Dátum
Módosítás típusa
Érintett munkalapok
Státusz
Változás leírása
Megjegyzés

Használat:

csak táblázat-kompatibilis, egy soros bejegyzés kerüljön ide;
hosszú dokumentumos verzióleírást nem ide kell teljes terjedelemben beilleszteni;
a Változás leírása és Megjegyzés lehet hosszabb, de maradjon egy cellában;
a verzióbejegyzés nem szabályszöveg;
a verzióbejegyzés célja kizárólag a fájl módosításainak követése.

### 7.2 2. README

Cél: a munkafájl rövid használati ismertetője.

Jelenlegi szerkezet:

a lapnak jelenleg nincs többoszlopos táblázatszerkezete;
gyakorlatilag egyetlen szöveges információs felületként működik;
a fájl célját, státuszát, használati rendjét és alapvető eligazító információit tartalmazza.

Használat:

belépési / tájékozódási lap;
nem részletes szabályforrás;
nem auditnapló;
nem döntésnapló;
nem kártyaadat-forrás;
módosítása akkor indokolt, ha a fájl általános használati rendje vagy státusza változik.

### 7.3 3. CARDS_MASTER

Cél: a tényleges aktív kártyaadatbázis fő munkalapja.

A 3. CARDS_MASTER lap a jelenlegi munkafájl aktív kártyaadat-master lapja. Ez már nem a régi 22 oszlopos cards.xlsx formátumot használja önmagában, hanem 43 oszlopos kibővített szerkezetet.

Elsődleges azonosító:

Szabályi_Kártya_ID

Teljes oszlopsorrend:

Kártya név
Típus
Birodalom
Klán
Faj
Kaszt
Magnitudó
Aura
ATK
HP
Képesség
Képesség_Canonical
Zóna_Felismerve
Kulcsszavak_Felismerve
Trigger_Felismerve
Célpont_Felismerve
Hatáscímkék
Időtartam_Felismerve
Feltétel_Felismerve
Gépi_Leírás
Értelmezési_Státusz
Engine_Megjegyzés
Audit_Státusz
Hibakategória
Javítási_Prioritás
Javítási_Megjegyzés
Balanszgyanú
Engine_Gyanú
Forrás_Hivatkozás
Döntést_Igényel
Ötletláda_Kapcsolat
Kiegészítői_Státusz
Szabályi_Kártya_ID
Print_ID
Set_ID
Collector_Number
Rarity
Treatment
Art_Variant
Print_Status
Version
Reprint_Of
Play_Legal_Status

Használat:

a kártyák tényleges neve, szövege, structured mezői, auditstátuszai és kiadási adatai itt változnak;
a NAME_PROFILE nem írja át automatikusan ezt a lapot;
a Szabályi_Kártya_ID az elsődleges stabil azonosító;
a kártyanév változhat, de az ID nem;
a természetes Képesség és a structured mezők jelentése nem térhet el egymástól;
a 43 oszlopos sort nem szabad 22 oszlopos exportformára visszavágni;
kártyajavításkor továbbra is működhet a 22+21 mezős bontás: először az első 22 oszlop, utána a 23–43. oszlopok.

Fontos munkaszabály:

A teljes CARDS_MASTER sor újragenerálása csak akkor biztonságos, ha egyszerre legfeljebb 10 kártyával dolgozunk, és a sort két részben kezeljük:

első blokk: 1–22. oszlop;
második blokk: 23–43. oszlop.

Ez az IGNIS-munka során bevált, ezért a további Birodalmaknál is ez marad az alapmódszer.

### 7.4 4. AUDIT_LOG

Cél: konkrét auditproblémák és javítások naplózása.

Oszlopok:

Audit_ID
Dátum
Kártya név
Birodalom
Klán
Típus
Auditkör
Jelenlegi státusz
Hibakategória
Probléma
Javasolt javítás
Structured javítás szükséges
Balanszgyanú
Engine-gyanú
Döntést igényel
Megjegyzés

Használat:

ide kerül minden konkrét hibajelentés;
kártyaszintű problémák, structured eltérések, balanszgyanúk és engine-gyanúk itt legyenek követhetők;
egy kártyához több auditbejegyzés is készülhet, ha több külön probléma van;
az AUDIT_LOG nem döntésnapló;
ha egy auditprobléma döntéssé válik, azt külön a 9. DECISION_LOG lapon is rögzíteni kell;
klánvégi audit után ide kell felvenni azokat a problémákat, amelyek dokumentált javítást, követést vagy későbbi tesztfigyelést igényelnek.

### 7.5 5. LOOKUPS

Cél: egységes listák, validációs értékek, státuszok és kódok tárolása.

A lap jelenlegi oszlopai:

Laptípusok
Birodalmak
Alapjátékos Klánok
Fajok
Kasztok
Kártyatervezési státuszok
Audit státuszok
Hibakategóriák
Rarity kódok
Treatment kódok
Art Variant kódok
Print Status kódok
Play Legal Status értékek

Tartalmi szerep:

A LOOKUPS lap nem aktív kártyaadat-forrás, hanem validációs és segédlista-lap. Olyan értékeket tartalmaz, amelyeket más munkalapokon következetesen kell használni.

Például:

laptípusok: Entitás, Ige, Rituálé, Jel, Sík;
Birodalmak: IGNIS, AQUA, TERRA, LUX, UMBRA, VENTUS, AETHER;
alapjátékos Klánok: Hamvaskezű, Lángidéző, Mélység Őrzői, Áramlat-táncosok, Ős-druidák, Vadon Vadászai, Fényhozó Lovagrend, Aeterna Papjai, Árnyékszindikátus, Lélekaratók, Viharhozók, Égbolt Urai, Fogaskerék Szövetség, Kóborlók;
Fajok: például Ember, Bestia, Gólem, Elementál, Sárkány, Szellem, Szárnyas Bestia, Sellő, Növény, Hüllő, Rovar, Angyal, Démon, Élőholt, Vámpír, Kiborg, Gépezet, Tünde, Törp, Goblin, Ork, Dinoszaurusz, Gomba, Asztrális, Kiméra, Óriás, Pszichikus, Mélységi, Parazita;
Kasztok: például Harcos, Lovag, Orgyilkos, Nindzsa, Kósza, Vadász, Szamuráj, Zsoldos, Kalóz, Mágus, Pap, Nekromanta, Boszorkánymester, Sámán, Druida, Nemes, Parancsnok, Tolvaj, Hős, Őrző;
kártyatervezési státuszok: alapjátékos, kiegészítői, feltételesen_használható, vizsgálandó, archív_nem_aktív, elvetett, kiadásfüggő_booster_packhoz_kötött, alapjátékos_tokenfüggő, alapjátékos_jelölt;
audit státuszok: például megtartható, megtartható_tesztelendő, javítandó_megtartható, újraszövegezett, szövegjavított, döntést_igényel, token_szabályra_vár, CORE01_needs_rework, kiegészítőbe_áthelyezendő, ötletláda_jelölt, elvetendő, megoldva_tesztelendő;
Play Legal Status értékek: CORE01_candidate, CORE01_test_required, CORE01_needs_decision, CORE01_needs_token_rules, CORE01_needs_rework, not_core01_legal_candidate, expansion_candidate, idea_box, archived, banned_not_legal.

Használat:

a többi munkalap legördülő listái vagy ellenőrzött értékei innen táplálkozhatnak;
ha új hivatalos kategória kerül be, azt itt is fel kell venni;
a LOOKUPS értékei segítenek megelőzni az elgépelést, státuszkeveredést és terminológiai szétesést;
nem kártyaadat-forrás;
nem auditnapló;
nem döntésnapló.
Structured értékek frissítése a LOOKUPS lapon:

Ha a kártyatáblázat-oszlopszabvány új Trigger_Felismerve, Hatáscímkék, Értelmezési_Státusz, Hibakategória, Audit_Státusz, Play_Legal_Status vagy más kontrollált értéket vezet be, akkor ellenőrizni kell, hogy az adott értéknek szerepelnie kell-e a LOOKUPS lapon is.

A LOOKUPS lap nem hoz létre új szabályt, és nem írja felül a kártyatáblázat-szabványt. A szerepe az, hogy a munkafájlban használt értékek következetesek, validálhatók és elgépeléstől védettek legyenek.

A VENTUS / Viharhozók audit alapján a következő új Trigger_Felismerve értékek kerültek structured-bővítési körbe:

on_attack_finished
on_combat_destroy_enemy
on_exhausted
activated_ability

A VENTUS / Viharhozók audit alapján a következő új Hatáscímkék értékek kerültek structured-bővítési körbe:

ready_prevention
trigger_duplicate
extra_breakthrough_phase
seal_break_prevention

A VENTUS / Égbolt Úrai audit alapján a következő új Trigger_Felismerve érték került structured-bővítési körbe, majd a kártyatáblázat-oszlopszabvány frissítése alapján szabványosított értékké vált:

on_enemy_spell_or_ritual_target

Később mérlegelendő, de jelenleg nem kötelezően felvett hatáscímke-jelölt:

stat_gain_prevention

A stat_gain_prevention csak akkor kerüljön be tényleges LOOKUPS / validációs értékként, ha több lapnál is rendszeresen előfordul olyan hatás, amely megakadályozza, hogy egy lap vagy lapcsoport ATK-, HP- vagy más statbónuszt kapjon.

LOOKUPS-frissítéskor ellenőrizni kell:

az új érték pontosan egyezik-e a kártyatáblázat-szabványban szereplő alakkal;
nincs-e elgépelés vagy más írásmód;
nem duplikál-e már meglévő értéket;
nem jelent-e mást, mint egy korábbi címke;
kell-e hozzá audit- vagy decision log bejegyzés;
kell-e engine / runtime oldali későbbi támogatás.
Ha egy új structured érték a kártyatáblázat-oszlopszabványban már elfogadott értékként szerepel, de a LOOKUPS lapon külön validációs lista is tartozik az adott mezőhöz, akkor a LOOKUPS listát is frissíteni kell.

A LOOKUPS frissítésnél pontosan ugyanazt az írásmódot kell használni, mint a kártyatáblázat-oszlopszabványban. Például:

on_enemy_spell_or_ritual_target

Nem használható helyette eltérő alak, rövidítés vagy kevert forma, például:

on_enemy_spell_ritual_target
on_spell_or_ritual_target
on_enemy_spell_or_ritual_played

### 7.6 6. RARITY_CODES

Cél: ritkasági kódok és rarity kategóriák nyilvántartása.

Oszlopok:

Kód
Név
Réteg
Leírás
Használati megjegyzés

Jelenlegi ritkasági kódok:

C – Common
UC – Uncommon
R – Rare
SR – Super Rare
UR – Ultra Rare
LEG – Legendary / Egyedi

Használat:

a CARDS_MASTER Rarity mezőjének ellenőrzéséhez használható;
a CARD_PRINTINGS és BOOSTER_POOLS lapokkal is kapcsolatban állhat;
a Rarity jelenleg gyakorisági réteg, nem azonos a foil / treatment réteggel;
nem kártyaszöveg-forrás;
nem szabálymechanikai lap;
a ritkasági kódok később bővíthetők, ha a rarity / foil / treatment rendszer részletesebbé válik.

### 7.7 7. EXPORT_RUNTIME

Cél: runtime / engine exporthoz előkészített kártyaadatok tárolása.

Jelenlegi szerkezet:

jelenleg a 22 oszlopos kártyaadat-formát használja;
ide kerülhetnek a véglegesített vagy exportálásra előkészített lapok;
a terv szerint ez lenne az a lap, ahonnan később a tényleges runtime / engine export készülhet.

Használat:

nem aktív kártyaszerkesztési főlap;
nem auditnapló;
a CARDS_MASTER alapján frissítendő;
csak olyan lapok kerüljenek ide, amelyek exportálásra alkalmas státuszban vannak;
export előtt ellenőrizni kell a 22 oszlopos oszlopszámot, a structured mezőket és az értelmezési státuszt;
később módosulhat, ha az engine-nek több vagy más adatmezőre lesz szüksége.

Megjegyzés:

Lehetséges, hogy a EXPORT_RUNTIME lap később nem marad pontosan 22 oszlopos, ha az engine-oldali feldolgozás több adatot igényel. Jelenlegi állapotban azonban a 22 oszlopos forma az alap.

### 7.8 8. EXPORT_NOTES

Cél: exporttal, runtime feldolgozással, engine-kompatibilitással vagy generálási problémákkal kapcsolatos megjegyzések tárolása.

Oszlopok:

Dátum
Export verzió
Forrás munkalap
Célfájl
Tartalom
Megjegyzés

Jelenlegi példaállapot:

2026.05.20.
nincs export
CARDS_MASTER
cards.xlsx
Kapcsolódó munkalapok előkészítése
Ez a módosítás még nem runtime-export. A cards.xlsx nem módosul automatikusan.

Használat:

exportműveletek dokumentálása;
exporthibák, figyelmeztetések, ismert korlátozások rögzítése;
annak jelzése, hogy egy módosítás tényleges export volt-e vagy csak előkészítés;
nem kártyaadat-master;
nem döntésnapló;
nem auditlog, de auditproblémára vagy exportproblémára hivatkozhat.

### 7.9 9. DECISION_LOG

Cél: döntések naplózása.

Oszlopok:

Döntés_ID
Dátum
Téma
Döntés
Indoklás
Érintett kártyák / mezők
Forrásdokumentum
Státusz
Megjegyzés

Használat:

ide csak valódi döntések kerüljenek;
például: lap CORE01-ből kivéve, lap Ötletládába kerül, névirány elfogadva, mechanikai irány véglegesítve;
nem minden auditprobléma decision log;
egy döntés több kártyát vagy több mezőt is érinthet;
a döntésnek később visszakereshetőnek kell lennie;
ha egy auditprobléma végleges irányt kap, akkor az auditbejegyzés mellett decision log is készülhet.

### 7.10 10. IMPORT_ORIGINAL

Cél: eredeti vagy importált kártyaadatok megőrzése.

Jelenlegi szerkezet:

az eredeti forrásból származó másolat;
jelenleg a 22 oszlopos formát használja.

Használat:

történeti / összehasonlító forrás;
nem aktív munkaforrás;
nem innen kell közvetlenül javítani a kártyákat;
ha eltérés van az IMPORT_ORIGINAL és a CARDS_MASTER között, akkor a CARDS_MASTER az aktív munkaforrás;
az IMPORT_ORIGINAL hasznos arra, hogy visszanézhető legyen, honnan indult egy kártya a javítás előtt;
nem szabad automatikusan felülírni.

### 7.11 11. SETS

Cél: kiadások, setek és kártyakészletek nyilvántartása.

Oszlopok:

Set_ID
Set_Name_HU
Set_Name_EN
Set_Type
Release_Order
Release_Status
Rules_Layer
Allowed_Realms
Introduced_Realms
Introduced_Clans
Introduced_Mechanics
Notes

Jelenlegi fő sorok:

CORE01 – Alapkészlet / Base Set;
EXP01_TBD – Első kiegészítő – később döntendő / First Expansion – TBD.

Használat:

a CARDS_MASTER Set_ID mezője ehhez kapcsolódik;
minden aktív Set_ID szerepeljen ezen a lapon;
a CORE01 az első nagy kártyakészlet / megjelenéskori lapkészlet munkakódja;
az EXP01_TBD későbbi kiegészítői placeholder, nem automatikus új Birodalom-bevezetés;
nem paklilista;
nem booster pool;
nem kártyaszöveg-forrás.

### 7.12 12. PRODUCTS

Cél: termékek, tesztpakli-csoportok, kezdőpaklik és egyéb kiadási egységek nyilvántartása.

Oszlopok:

Product_ID
Product_Name_HU
Product_Type
Related_Set_ID
Distribution_Type
Fixed_Or_Random
Target_Audience
Contains_Cards_From
Excluded_Cards_From
Notes

Jelenlegi termék- és product-típusok példái:

kezdőkészlet;
Birodalmi kezdőpaklik;
booster pack;
klánpakli;
belső tesztpakli-csoport.

Jelenlegi Product_ID példák:

KZK-CORE01
BKP-IGN01
BKP-AQU01
BKP-TER01
BKP-LUX01
BKP-UMB01
BKP-VEN01
BKP-AET01
BP-CORE01
KLP-IGN-HAM01
TEST-CORE01-IGNIS

Használat:

minden Product_ID, amely a PRODUCT_DECKLISTS vagy BOOSTER_POOLS lapon szerepel, legyen itt felvéve;
belső tesztpakli is kaphat Product_ID-t;
nem kereskedelmi termékeket is lehet jelölni internal_test státusszal;
kezdőpaklik, booster packok, belső tesztpakli-csoportok és egyéb termékstruktúrák itt kezelhetők;
a Product_ID nem azonos a Deck_ID mezővel;
egy Product_ID alatt több deck vagy több pool is előfordulhat, ha a termékstruktúra ezt indokolja.

### 7.13 13. CARD_PRINTINGS

Cél: konkrét kártyanyomtatások, printváltozatok és reprint kapcsolatok kezelése.

Oszlopok:

Szabályi_Kártya_ID
Print_ID
Card_Name
Set_ID
Product_ID
First_Print
Reprint
Rarity
Treatment
Art_Variant
Collector_Number
Version
Play_Legal_Status
Generation_Legal
Notes

Használat:

a Print_ID mezőhöz kapcsolódik;
egy szabályi kártyának több printje is lehet;
a Szabályi_Kártya_ID a szabályi kártyát azonosítja;
a Print_ID a konkrét nyomtatási / kiadási változatot azonosítja;
a Generation_Legal jelzi, hogy az adott print generálható-e normál módon;
tokenre váró, test_required vagy nem végleges lapok esetében a generálhatóság korlátozható;
nem természetes kártyaszöveg-főforrás, ha a CARDS_MASTER az aktív főlap.

### 7.14 14. GENERATION_PROFILES

Cél: generálási, exportálási vagy kártyakészítési profilok kezelése.

Oszlopok:

Profile_ID
Profile_Name
Allowed_Set_IDs
Allowed_Product_Types
Allowed_Rules_Layers
Allowed_Realms
Allowed_Clans
Allowed_Mechanics
Excluded_Statuses
Include_Reprints
Include_Promos
Include_Alt_Arts
Include_Collector_Treatments
Notes

Jelenlegi profilok példái:

GEN_CORE01_ALL
GEN_CORE01_IGNIS
GEN_CORE01_HAMVASKEZU
GEN_CORE01_NO_EXPANSION
GEN_BP_CORE01

Használat:

meghatározza, milyen lapok kerülhetnek adott generálási / exportálási folyamatba;
alkalmas teljes CORE01 generálásra, Birodalom-fókuszú generálásra, Klán-fókuszú generálásra vagy booster-generálásra;
az Excluded_Statuses mező különösen fontos, mert kizárhatja a nem legal, kiegészítői, ötletláda, archív vagy újradolgozást igénylő lapokat;
nem kártyaadat-master;
nem auditnapló;
exportfolyamatoknál hivatkozási alap lehet.

### 7.15 15. PRODUCT_DECKLISTS

Cél: paklik és termékpaklik konkrét kártyalistája.

Oszlopok:

Product_ID
Deck_ID
Szabályi_Kártya_ID
Kártya_Név
Darabszám
Szerep_A_Pakliban
Megjegyzés

Használat:

decklistát mindig ID-alapon kell vezetni;
a Szabályi_Kártya_ID az elsődleges kártyaazonosító;
a Kártya_Név segédmező, nem elsődleges azonosító;
a pakliméret darabszám alapján ellenőrizendő;
ha egy Product_ID nincs a 12. PRODUCTS lapon, javítani kell;
a tesztpaklik és kezdőpakli-jelöltek is itt kezelhetők;
a Darabszám mezők összege adja a pakliméretet;
ha egy kártyanév később változik, a decklistát ID alapján lehet biztonságosan frissíteni.

### 7.16 16. BOOSTER_POOLS

Cél: booster packokhoz, random termékekhez vagy rarity alapú bontási struktúrákhoz kapcsolódó kártyapoolok kezelése.

Oszlopok:

Booster_ID
Set_ID
Szabályi_Kártya_ID
Kártya_Név
Rarity
Booster_Eligible
Variant_Eligible
Megjegyzés

Jelenlegi állapot:

a lap jelenleg üres;
a szerkezet elő van készítve a későbbi booster pool kezeléshez.

Használat:

booster poolok, rarity poolok, sethez vagy producthoz kötött randomizált kártyakészletek előkészítésére használható;
kapcsolódhat a 12. PRODUCTS, 11. SETS, 6. RARITY_CODES és 13. CARD_PRINTINGS lapokhoz;
nem fix decklista;
nem kártyaszöveg-master;
csak olyan lap kerüljön ide, amely booster szempontból engedélyezett;
a Booster_Eligible és Variant_Eligible mezők később fontosak lesznek a booster generálásnál.

### 7.17 17. NAME_PROFILE

Cél: névprofilozás és névjavaslatok kezelése.

Oszlopok:

Kártya
Jelenlegi név
Birodalom
Klán
Faj
Kaszt
Képesség rövid szerepe
Névszint
Világbeli szerep
Mechanikai szerep
Képességből következő névirány
Egyedi jegy
Névforma
Névstátusz
Javasolt új név
Megjegyzés

Használat:

ez nem automatikus átnevezési lap;
a Javasolt új név csak döntés-előkészítő mező;
a tényleges kártyanév csak külön döntés után kerül át a CARDS_MASTER lapra;
névprofilozásnál figyelni kell a Fajra, Kasztra, Klánra, képességre, világbeli szerepre és mechanikai szerepre;
a névprofilozásnál a Kártya azonosító fontosabb, mint a kártyanév, mert a név később változhat;
a NAME_PROFILE elsődleges célja, hogy a kártyanév ne pusztán ritkaság vagy mechanikai funkció alapján készüljön, hanem az adott lap tényleges szerepéből, képességéből és világban betöltött helyéből induljon ki.

## 8. Javasolt szöveges exportok

### 8.1 Birodalmonkénti TSV

Minden Birodalom külön TSV fájlban exportálható.

Javasolt forma:

cards_by_realm/IGNIS.tsv
cards_by_realm/AQUA.tsv
cards_by_realm/TERRA.tsv
cards_by_realm/LUX.tsv
cards_by_realm/UMBRA.tsv
cards_by_realm/VENTUS.tsv
cards_by_realm/AETHER.tsv

Előny:

kisebb fájlok;
könnyebb olvasni;
nem kell egész Excel-munkafájlt feldolgozni;
Klánonként is könnyebben szűrhető;
auditnál kisebb a csonkulás és félreolvasás kockázata.

### 8.2 Egyesített TSV

Javasolt forma:

all_cards.tsv

Kiegészített oszlopokkal:

Forrás_lap
Forrás_sor

Ezek segítenek visszatalálni az Excel-helyre.

### 8.3 JSONL

Javasolt forma:

all_cards.jsonl

Egy sor = egy kártya.

Előny:

gépileg könnyen olvasható;
egy kártya teljes adata egy objektumban van;
később validálásra, diffelésre és scriptelésre is jó;
kisebb az esélye annak, hogy egy hosszú kártyaszöveg oszlopcsúszást okoz.

## 9. Munkafolyamat kártyaállomány javításakor

A további kártyaállomány-munka során az IGNIS alatt bevált munkarendet kell követni. A cél nem az, hogy a teljes fájlt egyszerre újrageneráljuk, hanem az, hogy Birodalmonként, Klánonként és kisebb kártyablokkonként haladjunk.

### 9.1 Birodalom előzetes átnézése

Minden új Birodalom előtt először rövid előzetes audit szükséges.

Ellenőrizni kell:

hány lap tartozik a Birodalomhoz;
melyik két alapjátékos Klán szerepel;
a Klánok lapmennyisége egyezik-e az elvárt szerkezettel;
vannak-e extra, hiányzó vagy duplikált lapok;
vannak-e nyilvánvaló hibás mezők;
vannak-e döntésblokkoló lapok;
vannak-e olyan lapok, amelyek valószínűleg nem CORE01-be valók.

Példa az AQUA esetében:

Mélység Őrzői: 58 lap;
Áramlat-táncosok: 60 lap;
az Áramlat-táncosok +2 lapja külön auditpont, és valószínűleg CORE01-ből kivételre vagy későbbi státuszba kerül.

Az ilyen problémát először jelölni kell, nem azonnal törölni.

### 9.2 Első Klán feldolgozása 10 lapos adagokban

A Klán kártyáit 10 lapos adagokban kell feldolgozni.

Egy adagban legfeljebb 10 kártya szerepeljen.

Minden 10 lapos adagban ellenőrizni kell:

szabályi megfelelés;
kártyaszöveg;
structured / canonical mezők;
kulcsszavak;
célpontok;
trigger;
időtartam;
feltételek;
Faj / Kaszt / Klán helyessége;
státuszok;
balanszgyanú;
engine-gyanú;
Play Legal Status;
esetleges döntést igénylő pontok.

### 9.3 43 oszlopos sorok kezelése két blokkban

Ha teljes CARDS_MASTER sorokat kell adni, akkor a 43 oszlopot két részben kell kezelni.

Első blokk:

1–22. oszlop;
ez lényegében a régi 22 oszlopos kártyaadat / structured rész;
tartalmazza a kártya természetes adatait, képességét és engine-előkészítő structured mezőit.

Második blokk:

23–43. oszlop;
ez tartalmazza az audit-, javítási-, státusz-, azonosító-, kiadási- és play legal mezőket.

Ez a kétlépcsős módszer az IGNIS alatt működött, ezért továbbra is ezt kell alapértelmezettnek tekinteni, ha teljes soros javítás készül.

Kézzel beilleszthető CARDS_MASTER blokkoknál az egész számokat tizedes nélkül kell megadni.

Példa helyes CARDS_MASTER értékekre:

4
5
6

Nem használandó forma:

4.0
5.0
6.0

Ez azért fontos, mert a kézzel beillesztett blokkok, a TSV-exportok és az Excel / Google Sheets automatikus értelmezése eltérően kezelheti a tizedes formájú számokat. A munkafájlban az egységes megjelenés és könnyebb ellenőrizhetőség miatt az egész számokat egész számként kell vezetni.

### 9.4 Nem minden esetben kell teljes sort újragenerálni

A teljes soros javítás hasznos, ha:

sok mező változik;
a structured rész teljesen hibás;
a lap újraszövegezésre kerül;
a státuszok is változnak;
az adott 10 lapos blokkot egységesen kell átvezetni.

Nem szükséges teljes sort újragenerálni, ha:

csak egy-két mező változik;
csak státuszjavítás történik;
csak AUDIT_LOG vagy DECISION_LOG bejegyzés kell;
csak névjavaslat készül;
csak Product_ID vagy decklist javítás történik.

Ilyenkor mezőszintű javítólista is elég.

### 9.5 Klánvégi audit

Minden Klán végén külön klánvégi audit szükséges.

A klánvégi audit célja:

ellenőrizni, hogy minden lap feldolgozásra került-e;
van-e hiányzó vagy duplikált lap;
minden lap státusza megfelelő-e;
maradt-e Döntést_Igényel = igen;
maradt-e javítatlan structured eltérés;
vannak-e balansz- vagy engine-gyanús lapok;
vannak-e olyan lapok, amelyek nem CORE01-be valók;
szükséges-e Ötletláda, kiegészítői vagy booster pack státusz;
szükséges-e AUDIT_LOG vagy DECISION_LOG bejegyzés.

A klánvégi audit után kell eldönteni, hogy a Klán munkaszinten lezárható-e.

### 9.6 Felmerült feladatok megoldása

A klánvégi audit után a problémás lapokat külön kell kezelni.

A munkafolyamat:

problémás lap vagy téma kiválasztása;
több lehetséges megoldás kidolgozása, ha szükséges;
a legjobb irány kiválasztása;
kártyaszöveg / structured / státusz javítása;
szükség esetén Ötletláda-bejegyzés;
szükség esetén AUDIT_LOG bejegyzés;
szükség esetén DECISION_LOG bejegyzés.

Fontos:

A CORE01 feltöltése és használhatóvá tétele prioritás. Ezért a javaslatok elsődlegesen arra irányuljanak, hogyan lehet egy lapot CORE01-kompatibilisen megtartani. Lap kivétele, Ötletládába helyezése vagy későbbi boosterbe mozgatása csak akkor legyen elsődleges javaslat, ha a lap tisztán nem alakítható át vagy túl sok alapjátékos problémát okozna.

### 9.7 AUDIT_LOG és DECISION_LOG frissítése

Ha egy javítás auditproblémához kapcsolódik, akkor a 4. AUDIT_LOG lapra kell szöveget készíteni.

Ha valódi döntés születik, akkor a 9. DECISION_LOG lapra is kell bejegyzés.

Nem minden auditprobléma döntés.

Példák Decision Logot igénylő esetekre:

lap CORE01-ből kivéve;
lap Ötletládába kerül;
lap kiegészítői státuszt kap;
mechanikai irány véglegesen kiválasztva;
névirány vagy névátvezetési elv elfogadva;
token-, Sík-, Jel- vagy Pecsétlogika elvi döntése.

### 9.8 Második Klán feldolgozása

Az első Klán lezárása után ugyanígy kell feldolgozni a második Klánt:

10 lapos adagok;
22 oszlopos első blokk;
23–43 oszlopos második blokk;
problémás lapok külön kezelése;
klánvégi audit;
AUDIT_LOG / DECISION_LOG frissítés, ha kell.

### 9.9 Birodalomszintű lezárás

Ha mindkét Klán munkaszinten lezárult, akkor Birodalomszintű audit következik.

Ellenőrizni kell:

mindkét Klán feldolgozása kész-e;
a Birodalom teljes lapmennyisége rendben van-e;
maradt-e extra vagy kivételre váró lap;
van-e duplikált ID, név, Print_ID vagy Collector_Number;
a Play Legal Status mezők egységesek-e;
minden CORE01_test_required vagy CORE01_needs_* státusz indokolt-e;
a Birodalom mechanikai identitása koherens-e;
a két Klán együtt nem okoz-e túl erős vagy túl széttartó működést;
kell-e további javító kör.

### 9.10 Névprofil / névaudit

A Birodalom kártyaállományának első javítóköre után jön a névprofilozás.

A névprofilozás menete:

Entitás lapok Klánonként;
nem-Entitás lapok Klánonként;
ID-alapú feldolgozás;
névszint meghatározása;
világbeli szerep;
mechanikai szerep;
képességből következő névirány;
egyedi jegy;
névforma;
névstátusz;
javasolt új név;
megjegyzés.

Fontos:

a NAME_PROFILE nem automatikus átnevezési lap;
a Javasolt új név döntés-előkészítő;
a CARDS_MASTER Kártya név mezője csak külön döntés után módosul;
a névprofilozás során a Kártya / Szabályi_Kártya_ID az elsődleges, nem a név.

### 9.11 Tesztpaklik és kezdőpaklik

A Birodalom névprofil első köre után jöhetnek a tesztpaklik.

Javasolt paklitípusok Birodalmonként:

első Klán tiszta tesztpaklija;
második Klán tiszta tesztpaklija;
vegyes Birodalmi tesztpakli;
Birodalmi kezdőpakli-jelölt.

A paklikat a 15. PRODUCT_DECKLISTS lapon kell vezetni.

A decklisták oszlopai:

Product_ID
Deck_ID
Szabályi_Kártya_ID
Kártya_Név
Darabszám
Szerep_A_Pakliban
Megjegyzés

Fontos:

a decklistákat mindig ID-alapon kell vezetni;
a Kártya_Név csak segédmező;
a pakliméretet darabszám alapján ellenőrizni kell;
minden használt Product_ID szerepeljen a 12. PRODUCTS lapon;
a kezdőpakli-jelölt nem feltétlenül legerősebb pakli, hanem tanító jellegű pakli.

### 9.12 Verziófrissítés

A Birodalom teljes munkaszintű lezárása után lehet verziófrissítést írni.

A verziófrissítésbe csak akkor kerüljön be a Birodalom lezárása, ha:

mindkét Klán első javítóköre kész;
klánvégi auditok készültek;
a felmerült problémák rendezve vagy jelölve vannak;
szükséges AUDIT_LOG és DECISION_LOG bejegyzések elkészültek;
névprofil első köre kész;
tesztpaklik / kezdőpakli-jelölt elkészültek, ha az adott munkafázis része volt;
a fájl főbb kapcsolatai ellenőrizve lettek.

A verzióbejegyzés a 1. VERZIÓ lap 7 oszlopos formátumához igazodjon, ne hosszú dokumentumos verziófejezet legyen.

Structured értékkészlet vagy LOOKUPS frissítése esetén a VERZIÓ lapon külön jelezni kell, hogy nem kártyaszöveg-tömegjavítás, hanem munkafájl-szerkezeti / validációs / structured értékkészlet-frissítés történt.

A verzióbejegyzésben szerepeljen:

melyik structured mezők érintettek;
melyik LOOKUPS lista vagy validációs érték frissült;
melyik auditkör indokolta a módosítást;
módosult-e a CARDS_MASTER oszlopszerkezete;
és szükséges-e későbbi engine / runtime ellenőrzés.

Példa rövid VERZIÓ-lap bejegyzésre:

1.7v 2026-06-13 structured értékkészlet / LOOKUPS frissítés LOOKUPS; CARDS_MASTER; AUDIT_LOG; DECISION_LOG munkaszintű frissítés VENTUS / Viharhozók audit alapján új Trigger_Felismerve és Hatáscímkék értékek kerültek bevezetésre; a CARDS_MASTER oszlopszerkezete nem változott. Új értékek: on_attack_finished, on_combat_destroy_enemy, on_exhausted, activated_ability, ready_prevention, trigger_duplicate, extra_breakthrough_phase, seal_break_prevention.

### 9.13 Structured értékkészlet és LOOKUPS frissítése

Ha egy Birodalom vagy Klán auditja során új structured trigger, hatáscímke vagy más kontrollált érték válik szükségessé, akkor azt nem elég csak a CARDS_MASTER egyes soraiban használni.

A munkafolyamat sorrendje:

Az érintett lapokon jelölni kell a structured hiányt vagy közelítő értéket.
Meg kell vizsgálni, hogy a probléma kártyaszöveg-hiba vagy structured értékkészlet-hiány.
Ha a kártyaszöveg működőképes, az új érték structured-bővítési jelöltként kezelhető.
A döntést szükség esetén AUDIT_LOG és DECISION_LOG bejegyzésben kell rögzíteni.
A kártyatáblázat-oszlopszabványban át kell vezetni az új értéket, ha elfogadott structured érték lesz.
A LOOKUPS lapon is frissíteni kell a kapcsolódó validációs listát, ha az adott mező ott szerepel.
A CARDS_MASTER érintett sorai ezután használhatják egységesen az új értéket.
Ha az új érték engine-oldali feldolgozást igényel, az Engine_Gyanú és Engine_Megjegyzés mezőkben is jelölni kell.

Ez a folyamat különösen fontos a következő mezőknél:

Trigger_Felismerve
Hatáscímkék
Értelmezési_Státusz
Hibakategória
Audit_Státusz
Play_Legal_Status

A structured értékkészlet bővítése nem módosítja a 43 oszlopos CARDS_MASTER szerkezetét. Csak a meglévő structured mezők engedélyezett vagy ajánlott értékeit pontosítja.

Aktuális példa VENTUS / Égbolt Úrai audit alapján:

Új structured érték:
on_enemy_spell_or_ritual_target

Érintett mező:
Trigger_Felismerve

Átvezetési helyek:
- kártyatáblázat-oszlopszabvány Trigger_Felismerve listája;
- LOOKUPS Trigger_Felismerve validációs listája, ha a munkafájl külön validációs listát használ;
- CARDS_MASTER érintett VENTUS / Égbolt Úrai sorai;
- AUDIT_LOG / DECISION_LOG, ha a structured-bővítéshez külön naplóbejegyzés tartozik;
- VERZIÓ lap, mint structured értékkészlet / LOOKUPS frissítés.

Megjegyzés:

A CARDS_MASTER oszlopszerkezete nem változik. A frissítés csak a meglévő Trigger_Felismerve mező engedélyezett és következetesen használt értékkészletét pontosítja.

## 10. Példa: AQUA munkarend

Az AQUA Birodalomnál a következő munkarend alkalmazandó:

AQUA kártyaállomány első átnézése:
hány lap van;
melyik két Klán;
vannak-e hiányzó / hibás mezők;
van-e döntésblokkoló lap;
van-e extra lap.
Első AQUA Klán feldolgozása:
10-es adagokban;
szabályi megfelelés;
kártyaszöveg;
státuszok;
structured mezők;
1–22. oszlopos blokk;
23–43. oszlopos blokk;
auditlog / decisionlog, ahol kell.
Klánvégi audit:
ugyanúgy, ahogy az IGNIS-nél kialakult.
Második AQUA Klán feldolgozása:
ugyanabban a 10 lapos, kétblokkos módszerben.
AQUA birodalomszintű lezárás.
AQUA névprofil első köre.
AQUA tesztpaklik.

Jelenlegi AQUA előzetes megfigyelés:

Mélység Őrzői: 58 lap;
Áramlat-táncosok: 60 lap;
az Áramlat-táncosok +2 lapja auditpont;
a +2 lap valószínűleg törlendő vagy kivételre kerül a CORE01-ből, de ezt csak audit és döntés után szabad átvezetni.