# AETERNA – kártyaadatbázis audit munkafolyamat és adatkezelési rend

Verzió: 1.2  
Státusz: aktív munkarendi segéddokumentum  
Cél: rögzíteni az AETERNA kártyaadatbázis javításának, auditjának, névprofilozásának, tesztpakli-előkészítésének és verziózásának követhető, fájlalapú munkafolyamatát.

---

## 1. Miért kellett ezt a dokumentumot létrehozni?

Az AETERNA kártyaadatbázis nagy mennyiségű, több munkalapos, sok oszlopos táblázatos forrásból áll. A munka során egyszerre kell kezelni:

- a természetes kártyaszövegeket;
- a structured / canonical mezőket;
- a kártyák auditstátuszait;
- a döntéseket;
- a névprofilokat;
- a termék- és paklilistákat;
- a set-, print-, rarity- és exportadatokat;
- valamint a későbbi engine / runtime feldolgozás igényeit.

A korábbi munkafolyamatban problémát okozott, amikor túl hosszú, teljes kártyasorok kerültek egyetlen chatválaszba. Ez oszlopcsúszást, csonkolást vagy hiányos generálást okozhatott.

A javított munkafolyamat célja ezért nem az, hogy elhagyjuk a teljes soros javítást, hanem az, hogy szabályozottan használjuk.

A bevált módszer az IGNIS birodalom feldolgozása során alakult ki:

- Birodalmonként haladás;
- Klánonként haladás;
- 10 kártyás adagok;
- teljes `CARDS_MASTER` sorok esetén kétblokkos bontás;
- először az 1–22. oszlop;
- utána a 23–43. oszlop;
- klánvégi audit;
- problémás lapok külön kezelése;
- szükséges `AUDIT_LOG` és `DECISION_LOG` bejegyzések;
- névprofilozás;
- tesztpaklik;
- végül verziófrissítés.

Ez a dokumentum ezt a bevált folyamatot rögzíti.

---

## 2. Kapcsolódó fájlok és dokumentumok

### 2.1 Excel / Google Sheets munkafájl

Az Excel / Google Sheets marad a végső szerkesztési és nyilvántartási hely.

Ebben történik:

- a tényleges kártyasorok módosítása;
- a `CARDS_MASTER` frissítése;
- az `AUDIT_LOG` vezetése;
- a `DECISION_LOG` vezetése;
- a `NAME_PROFILE` kitöltése;
- a `PRODUCTS` és `PRODUCT_DECKLISTS` lapok kezelése;
- a `SETS`, `CARD_PRINTINGS`, `BOOSTER_POOLS` és generálási lapok karbantartása;
- a verzióbejegyzés rögzítése.

A jelenlegi munkafájl neve munkaszinten:

**AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.2v**

A fájl 17 munkalapot tartalmaz. Ezek részletes szerkezetét külön dokumentum rögzíti:

**AETERNA – Excel / Google Sheets munkafájl szerkezete és oszlopszabvány**

### 2.2 Szöveges munkakivonatok

A nagy Excel-fájl mellett hasznos lehet külön szöveges exportokat is használni.

Javasolt formátumok:

- `.md` a munkarendhez, dokumentációhoz és magyarázatokhoz;
- `.tsv` a táblázatos kártyaadatokhoz;
- `.jsonl` opcionális gépi ellenőrzéshez.

A TSV és JSONL exportok célja:

- könnyebb olvashatóság;
- pontos sorazonosítás;
- Birodalmonkénti és Klánonkénti szűrés;
- gyorsabb ellenőrzés;
- kevesebb Excel-olvasási hiba;
- kisebb chatválaszok;
- könnyebb diffelés és validálás.

Fontos: a szöveges export segédeszköz, nem váltja ki az aktív Excel / Google Sheets munkafájlt.

---

## 3. Fontos szerkezeti alapelv: 22 oszlop és 43 oszlop

### 3.1 Régi / egyszerűsített 22 oszlopos forma

A régi `cards.xlsx`, a `10. IMPORT_ORIGINAL`, valamint jelenleg a `7. EXPORT_RUNTIME` lap a 22 oszlopos kártyaadat-formához kapcsolódik.

Ez a forma tartalmazza:

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

### 3.2 Jelenlegi 43 oszlopos CARDS_MASTER

A jelenlegi `3. CARDS_MASTER` már nem 22, hanem 43 oszlopos aktív kártyaadat-master.

Ezért teljes kártyasor javításakor nem szabad csak 22 oszloppal dolgozni, kivéve ha kifejezetten `EXPORT_RUNTIME` vagy 22 oszlopos kivonat készül.

A `CARDS_MASTER` teljes sorát két részben kell kezelni:

- első blokk: 1–22. oszlop;
- második blokk: 23–43. oszlop.

Ez a kétblokkos bontás megőrzi a strukturált adat teljességét, de csökkenti az oszlopcsúszás és csonkolás kockázatát.

---

## 4. Általános munkafolyamat

### 4.1 Előkészítés

Egy új munkafázis előtt ellenőrizni kell:

1. a legfrissebb Excel / Google Sheets fájl állapotát;
2. a munkalapok számát;
3. a releváns lapok oszlopait;
4. a vizsgált Birodalom sorait;
5. Klánonkénti bontást;
6. Típusonkénti bontást;
7. hiányzó vagy extra lapokat;
8. duplikált azonosítókat;
9. ismert döntésblokkoló pontokat.

### 4.2 Birodalomindítás

Egy új Birodalom indításakor először nem javítunk kártyát.

Először rögzítjük:

- hány lap van az adott Birodalomban;
- melyik két alapjátékos Klán szerepel;
- Klánonként hány lap van;
- Típusonként milyen eloszlás van;
- van-e többlet vagy hiány;
- melyik Klánnal kezdünk;
- van-e előzetes döntési pont;
- van-e olyan lap, amely valószínűleg nem CORE01-be való.

Példa aktuális AQUA állapot:

- `Mélység Őrzői`: 58 lap;
- `Áramlat-táncosok`: 60 lap;
- az Áramlat-táncosok +2 lapja CORE01-többletként / későbbi döntési pontként kezelendő;
- a +2 lap sorsa későbbi audit és döntés tárgya, valószínűleg CORE01-ből kikerül.

---

## 5. Klánfeldolgozás

### 5.1 Alapmódszer

Egy Klánt nem egyszerre dolgozunk fel.

A bevált módszer:

- 10 kártyás adagok;
- minden adag külön ellenőrzés;
- teljes soros javítás esetén két blokk:
  - 1–22. oszlop;
  - 23–43. oszlop;
- minden adag után rövid ellenőrző megjegyzés;
- vitás lapokat külön félretesszük a klánvégi vagy köztes auditkörre.

Ez a módszer működött az IGNIS birodalomnál, ezért ezt kell alapértelmezettnek tekinteni AQUA és a további Birodalmak esetében is.

### 5.2 Egy 10 lapos adag ellenőrzési szempontjai

Minden 10 lapos adagban ellenőrizni kell:

1. kártyanév;
2. laptípus;
3. Birodalom;
4. Klán;
5. Faj;
6. Kaszt;
7. Magnitúdó;
8. Aura;
9. ATK / HP;
10. természetes kártyaszöveg;
11. `Képesség_Canonical`;
12. `Zóna_Felismerve`;
13. `Kulcsszavak_Felismerve`;
14. `Trigger_Felismerve`;
15. `Célpont_Felismerve`;
16. `Hatáscímkék`;
17. `Időtartam_Felismerve`;
18. `Feltétel_Felismerve`;
19. `Gépi_Leírás`;
20. `Értelmezési_Státusz`;
21. `Engine_Megjegyzés`;
22. auditstátusz;
23. hibakategória;
24. javítási prioritás;
25. javítási megjegyzés;
26. balanszgyanú;
27. engine-gyanú;
28. forráshivatkozás;
29. döntést igényel-e;
30. Ötletláda-kapcsolat;
31. kiegészítői státusz;
32. szabályi és print azonosítók;
33. set- és collector adatok;
34. rarity / treatment / art variant;
35. print státusz;
36. version / reprint kapcsolat;
37. play legal státusz.

### 5.3 Teljes soros javítás formája

Ha teljes `CARDS_MASTER` sort kell adni, akkor a válaszban két külön TSV blokk készüljön.

Első blokk:

- 1–22. oszlop;
- tartalmazza a kártya alapadatait és structured mezőit.

Második blokk:

- 23–43. oszlop;
- tartalmazza az audit-, javítási-, státusz-, azonosító-, kiadási- és play legal mezőket.

Egy blokkban legfeljebb 10 kártya szerepeljen.

### 5.4 Mikor kell teljes sor?

Teljes soros javítás indokolt, ha:

- sok mező változik;
- a kártya teljes structured része javul;
- a természetes kártyaszöveg és a canonical mezők is módosulnak;
- a státuszmezők is változnak;
- egy teljes 10 lapos blokkot egységesen kell átvezetni;
- importból vagy régi állapotból tiszta `CARDS_MASTER` sorokat kell létrehozni.

### 5.5 Mikor elég mezőszintű javítólista?

Mezőszintű javítólista elég, ha:

- csak egy-két mező változik;
- csak státuszjavítás történik;
- csak név vagy névjavaslat változik;
- csak Product_ID vagy decklist javítás történik;
- csak `AUDIT_LOG` vagy `DECISION_LOG` bejegyzés kell;
- egy korábbi hiba utólagos korrekciójáról van szó.

Példa mezőszintű javítólista formátum:

```tsv
Szabályi_Kártya_ID	Kártya név	Mező	Régi érték	Új érték	Indoklás
AET-AQU-MOR-004	Zafírszemű Dajka	Faj	Elemi Lény	Elementál	Az Elementál a hivatalos Faj-név.
```

---

## 6. Klánvégi audit

Minden Klán végén külön klánvégi auditot kell tartani.

Ellenőrizni kell:

- minden lap feldolgozásra került-e;
- nincs-e hiányzó vagy duplikált lap;
- minden lap kapott-e auditstátuszt;
- maradt-e `Döntést_Igényel = igen`;
- van-e javítatlan structured eltérés;
- a természetes szöveg és structured mezők összhangban vannak-e;
- a Faj / Kaszt mezők nem keverednek-e;
- nincs-e kiegészítői mechanika CORE01 lapon;
- a balanszgyanúk jelölve vannak-e;
- az engine-gyanúk jelölve vannak-e;
- vannak-e törlendő / kivételre jelölt lapok;
- szükséges-e Ötletláda-bejegyzés;
- szükséges-e `AUDIT_LOG` bejegyzés;
- szükséges-e `DECISION_LOG` bejegyzés.

A klánvégi audit után kell eldönteni, hogy a Klán munkaszinten lezárható-e.

---

## 7. Felmerült feladatok kezelése

A klánvégi audit vagy egy 10 lapos adag közben felmerülő problémás lapokat külön kell kezelni.

A munkafolyamat:

1. problémás lap vagy téma kiválasztása;
2. probléma pontos megfogalmazása;
3. több lehetséges megoldás kidolgozása, ha szükséges;
4. érvek és ellenérvek áttekintése;
5. a legjobb irány kiválasztása;
6. kártyaszöveg / structured / státusz javítása;
7. szükség esetén Ötletláda-bejegyzés;
8. szükség esetén `AUDIT_LOG` bejegyzés;
9. szükség esetén `DECISION_LOG` bejegyzés.

Fontos tervezési alapelv:

A CORE01 feltöltése és használhatóvá tétele prioritás. Ezért az elsődleges javaslat lehetőleg ne a lap kivétele vagy megszüntetése legyen, hanem a lap CORE01-kompatibilis átformálása. Lap kivétele, Ötletládába helyezése vagy későbbi boosterbe mozgatása akkor legyen elsődleges javaslat, ha a lap tisztán nem alakítható át, vagy túl sok alapjátékos problémát okozna.

---

## 8. AUDIT_LOG és DECISION_LOG

### 8.1 AUDIT_LOG

Ha egy javítás auditproblémához kapcsolódik, akkor a `4. AUDIT_LOG` lapra kell szöveget készíteni.

Az `AUDIT_LOG` célja:

- hibák rögzítése;
- structured eltérések követése;
- balanszgyanúk jelölése;
- engine-gyanúk jelölése;
- későbbi tesztfigyelési pontok megőrzése.

Nem minden `AUDIT_LOG` bejegyzés jelent döntést.

### 8.2 DECISION_LOG

Ha valódi döntés születik, akkor a `9. DECISION_LOG` lapra is kell bejegyzés.

Decision Logot igényel például:

- lap CORE01-ből kivéve;
- lap Ötletládába kerül;
- lap kiegészítői státuszt kap;
- mechanikai irány véglegesen kiválasztva;
- névirány vagy névátvezetési elv elfogadva;
- token-, Sík-, Jel- vagy Pecsétlogika elvi döntése;
- Product_ID vagy termékstruktúra elvi rendezése.

Nem minden auditprobléma döntés. Ha csak hibát rögzítünk, elég lehet az `AUDIT_LOG`.

---

## 9. Birodalomszintű lezárás

Ha mindkét Klán munkaszinten lezárult, akkor Birodalomszintű audit következik.

Ellenőrizni kell:

- mindkét Klán első javítóköre kész-e;
- mindkét Klán klánauditja kész-e;
- a Birodalom teljes lapmennyisége rendben van-e;
- maradt-e extra vagy kivételre váró lap;
- van-e duplikált `Szabályi_Kártya_ID`;
- van-e duplikált `Print_ID`;
- van-e duplikált `Collector_Number`;
- a Play Legal Status mezők egységesek-e;
- minden `CORE01_test_required` vagy `CORE01_needs_*` státusz indokolt-e;
- a Birodalom mechanikai identitása koherens-e;
- a két Klán együtt nem okoz-e túl erős vagy túl széttartó működést;
- kell-e további javító kör.

Egy Birodalom akkor zárható munkaszinten, ha:

1. mindkét Klán első javítóköre kész;
2. mindkét Klán klánauditja kész;
3. birodalomszintű eltérések rendezve vagy jelölve vannak;
4. szükséges `AUDIT_LOG` és `DECISION_LOG` bejegyzések elkészültek;
5. nincs ismert blokkoló hiba.

Fontos pontosítás:

A Birodalomszintű lezárás nem azonos a teljes játék végső balansz- és identitáslezárásával.

A Birodalom végén tartott záróellenőrzés célja:

- az adott Birodalom két Klánjának helyi koherencia-ellenőrzése;
- a nyitott státuszok rendezése;
- a technikai, structured és auditmezők tisztítása;
- a nyilvánvaló loopok, lockok, túl stabil engine-ek és ellenjáték nélküli helyzetek jelölése vagy javítása;
- annak ellenőrzése, hogy az adott Birodalom munkaszinten továbbvihető-e.

A Birodalom végén nem kell teljes identitásmegőrző újrabalanszolást tartani.  
Az identitásmegőrző, teljes játékra kiterjedő balansz-visszaellenőrzés csak akkor következik, amikor minden Birodalom első audit-/javítókörén végigértünk.

---

## 10. Névprofil / névaudit

A Birodalom kártyaállományának első javítóköre után jön a névprofilozás.

A névprofilozás menete:

1. Entitás lapok Klánonként;
2. nem-Entitás lapok Klánonként;
3. ID-alapú feldolgozás;
4. névszint meghatározása;
5. világbeli szerep meghatározása;
6. mechanikai szerep meghatározása;
7. képességből következő névirány;
8. egyedi jegy;
9. névforma;
10. névstátusz;
11. javasolt új név;
12. megjegyzés.

Fontos:

- a `17. NAME_PROFILE` nem automatikus átnevezési lap;
- a `Javasolt új név` döntés-előkészítő;
- a `CARDS_MASTER` `Kártya név` mezője csak külön döntés után módosul;
- a névprofilozás során a `Kártya` / `Szabályi_Kártya_ID` az elsődleges, nem a név;
- a kártya képessége, világbeli szerepe, Faja, Kasztja, Klánja és mechanikai szerepe mind befolyásolhatja a névprofilt.

---

## 11. Tesztpaklik és kezdőpaklik

A Birodalom névprofil első köre után jöhetnek a tesztpaklik.

Javasolt paklitípusok Birodalmonként:

1. első Klán tiszta tesztpaklija;
2. második Klán tiszta tesztpaklija;
3. vegyes Birodalmi tesztpakli;
4. Birodalmi kezdőpakli-jelölt.

A paklikat a `15. PRODUCT_DECKLISTS` lapon kell vezetni.

A decklisták oszlopai:

- `Product_ID`
- `Deck_ID`
- `Szabályi_Kártya_ID`
- `Kártya_Név`
- `Darabszám`
- `Szerep_A_Pakliban`
- `Megjegyzés`

Fontos:

- a decklistákat mindig ID-alapon kell vezetni;
- a `Szabályi_Kártya_ID` az elsődleges azonosító;
- a `Kártya_Név` csak segédmező;
- a pakliméretet darabszám alapján ellenőrizni kell;
- minden használt `Product_ID` szerepeljen a `12. PRODUCTS` lapon;
- a kezdőpakli-jelölt nem feltétlenül legerősebb pakli, hanem tanító jellegű pakli.

---

## 12. Verziófrissítés

A Birodalom teljes munkaszintű lezárása után lehet verziófrissítést írni.

A verziófrissítésbe csak akkor kerüljön be a Birodalom lezárása, ha:

- mindkét Klán első javítóköre kész;
- klánvégi auditok készültek;
- a felmerült problémák rendezve vagy jelölve vannak;
- szükséges `AUDIT_LOG` és `DECISION_LOG` bejegyzések elkészültek;
- névprofil első köre kész;
- tesztpaklik / kezdőpakli-jelölt elkészültek, ha az adott munkafázis része volt;
- a fájl főbb kapcsolatai ellenőrizve lettek.

A verzióbejegyzés a `1. VERZIÓ` lap 7 oszlopos formátumához igazodjon:

- `Verzió`
- `Dátum`
- `Módosítás típusa`
- `Érintett munkalapok`
- `Státusz`
- `Változás leírása`
- `Megjegyzés`

A verzióbejegyzés ne hosszú dokumentumos verziófejezet legyen, hanem táblázat-kompatibilis sor.

Fontos:

A Birodalomhoz kapcsolódó verziófrissítés munkaszintű lezárást jelent, nem végleges globális balanszlezárást.

A teljes első audit-/javítókör végén külön identitásmegőrző balansz-visszaellenőrzés következik. Ez később újabb verzióbejegyzést igényelhet, ha a visszaellenőrzés alapján lapok részben visszaerősödnek, alternatív féket kapnak, vagy Birodalom-identitási javítás történik.

---

## 13. Teljes első kör utáni identitásmegőrző balansz-visszaellenőrzés

Amikor a teljes kártyaállomány első audit-/javítókörén végigértünk, külön globális visszaellenőrzést kell tartani.

Ez a visszaellenőrzés nem Birodalmonként, nem Klánonként és nem minden részlezárás után történik, hanem csak a teljes első kör befejezése után.

### 13.1 A visszaellenőrzés célja

A cél annak ellenőrzése, hogy az audit- és javítási folyamat során a játék nem lett-e túlzottan legyengítve, túl steril vagy túl egyformára húzva.

A javítások során jogosan vissza kell fogni:

- a végtelen vagy túl könnyen ismételhető loopokat;
- a lockokat;
- a túl stabil engine-eket;
- a túl olcsó vagy túl kevés árral működő erős hatásokat;
- az ellenjáték nélküli helyzeteket;
- a túl könnyen halmozódó erőforrás-, húzás-, visszahozás- vagy védelmi csomagokat.

Ugyanakkor nem cél minden erős hatás automatikus gyengítése.

Az AETERNA-nak meg kell őriznie:

- az erős Birodalom-identitásokat;
- az emlékezetes, látványos lapokat;
- a Birodalmak közötti karakteres különbségeket;
- a nagy fordító- vagy csúcspontokat;
- azokat az erős hatásokat, amelyeknek megfelelő ára, feltétele, időzítése vagy ellenjátéka van.

### 13.2 A vizsgálat alapelve

A visszaellenőrzés során nem az a kérdés, hogy egy lap vagy Birodalom erős-e.

A helyes kérdések:

1. Az erős hatás illik-e az adott Birodalom identitásába?
2. Van-e ára, feltétele vagy kockázata?
3. Van-e rá ellenjáték?
4. Túl könnyen ismételhető-e?
5. Halmozódik-e túl sok más engine-darabbal?
6. Okoz-e loopot vagy lockot?
7. Kizárja-e az ellenfelet a játékból?
8. Túl stabilizálja-e a játékállást?
9. Elvesz-e valamit a Birodalom karakteréből a korábbi gyengítés?
10. Érdemes-e nyers gyengítés helyett inkább árat, feltételt, időzítést vagy korlátot használni?

### 13.3 Kategóriák a visszaellenőrzéshez

A teljes első kör után a korábban gyengített vagy problémásnak jelölt lapokat három kategóriába kell sorolni.

#### A) Maradjon gyengítve

Ide tartoznak azok a lapok vagy hatások, amelyek:

- loopot okozhatnak;
- lockot hozhatnak létre;
- túl olcsón adnak túl nagy előnyt;
- túl könnyen ismételhetők;
- ellenjáték nélküli helyzetet teremtenek;
- túl stabil engine-t építenek.

Ezeknél a korábbi gyengítés vagy korlátozás megtartható.

#### B) Részben visszaerősíthető

Ide tartoznak azok a lapok, amelyek:

- erős, de identitáserősítő hatást képviselnek;
- emlékezetes Birodalom-pillanatot adnak;
- magas költségűek vagy ritka feltételhez kötöttek;
- nem okoznak loopot vagy lockot;
- erősek ugyan, de tesztelhető keretek között maradnak.

Ezeknél meg kell vizsgálni, hogy a korábbi javítás túl óvatos volt-e.

#### C) Nyers gyengítés helyett más fék kell

Ide tartoznak azok a lapok, ahol az eredeti hatás karakteres volt, de túl könnyen használható vagy túl olcsó volt.

Ilyenkor nem feltétlenül a hatás erejét kell csökkenteni, hanem más féket kell beépíteni, például:

- magasabb Aura-költség;
- szigorúbb feltétel;
- körönként egyszeri korlát;
- Magnitúdókorlát;
- Kimerült állapot;
- képességaktiválási tiltás;
- késleltetett hatás;
- ellenfélnek adott ellenjáték;
- Pecsét-, lap-, mező- vagy tempóár;
- nem halmozódó működés.

### 13.4 Dokumentálás

A teljes első kör utáni identitásmegőrző balansz-visszaellenőrzésről külön auditblokkot kell készíteni.

Ennek tartalmaznia kell:

- mely Birodalmaknál merült fel túlgyengítés gyanúja;
- mely lapok maradnak gyengítve;
- mely lapok részben visszaerősíthetők;
- mely lapoknál kell más típusú fék;
- mely Birodalom-identitások erősítendők vissza;
- mely engine-ek maradnak korlátozva;
- milyen döntések kerültek a `DECISION_LOG` lapra;
- milyen további playtest / tesztprogramos megfigyelés szükséges.

A visszaellenőrzés eredménye nem írja felül automatikusan az első auditkör javításait.  
Minden visszaerősítés vagy alternatív fék külön döntést igényel, és `AUDIT_LOG` / `DECISION_LOG` bejegyzéssel követendő.

---

## 14. Jelenlegi projektállapot

### 14.1 IGNIS

Munkaszinten lezárva.

Elkészült:

- Hamvaskezű klán első javítóköre;
- Lángidéző klán első javítóköre;
- klánszintű auditok;
- felmerült problémás lapok javítása;
- `AUDIT_LOG` és `DECISION_LOG` bejegyzések;
- névprofil első köre;
- első IGNIS tesztpaklik;
- Product_ID rendezés;
- 1.2v táblázatos verzióbejegyzés.

Későbbi visszatérő feladatok:

- IGNIS tesztpaklik playtest / engine vizsgálata;
- `CORE01_test_required` lapok eredményeinek kiértékelése;
- névjavaslatok tényleges átvezetése, ha döntés születik róla.

### 14.2 AQUA

Munkafázis: előkészítés / újraindítás javított munkafolyamattal.

Ismert állapot:

- `Mélység Őrzői`: 58 lap;
- `Áramlat-táncosok`: 60 lap;
- az Áramlat-táncosok +2 lapja valószínűleg nem marad CORE01-ben;
- a Mélység Őrzői első 10 lapjának korábbi chatgenerálása nem tekinthető végleges javítóblokknak, mert nem a most rögzített, kétblokkos 43 oszlopos workflow szerint készült.

Következő munkalépés:

1. AQUA előzetes állapot végleges rögzítése;
2. Mélység Őrzői klán feldolgozása 10 lapos adagokban;
3. minden adaghoz 1–22. oszlopos blokk;
4. minden adaghoz 23–43. oszlopos blokk;
5. klánvégi audit;
6. problémás lapok rendezése;
7. `AUDIT_LOG` / `DECISION_LOG`, ha kell;
8. Áramlat-táncosok feldolgozása;
9. +2 lap döntési kezelése;
10. AQUA birodalomszintű lezárás;
11. AQUA névprofil;
12. AQUA tesztpaklik.

---

## 15. Záró alapelv

A további munka alapelve:

Nem az egész fájlt próbáljuk egyszerre javítani.

Birodalmonként, Klánonként és 10 lapos adagokban haladunk.

A `CARDS_MASTER` teljes 43 oszlopos szerkezetét tiszteletben tartjuk.

Ha teljes sort adunk, két részben adjuk:

1. 1–22. oszlop;
2. 23–43. oszlop.

A klán végén mindig auditálunk.

A Birodalom végén mindig helyi birodalmi záróellenőrzést tartunk.

Ez a záróellenőrzés az adott Birodalom technikai, structured, státusz- és klánkoherencia-vizsgálata.  
Nem azonos a teljes játékra vonatkozó identitásmegőrző balansz-visszaellenőrzéssel.

A teljes játékra kiterjedő identitásmegőrző balansz-visszaellenőrzést csak akkor tartjuk meg, amikor minden Birodalom első audit-/javítókörén végigértünk.

A balanszmunka alapelve:

Nem az erős Birodalom-identitásokat kell megszüntetni, hanem a visszaélhető, ismételhető, ellenjáték nélküli vagy túl stabil engine-helyzeteket kell kontrollálni.

Az AETERNA akkor működik jól, ha minden Birodalomnak vannak erős, emlékezetes és karakteres pillanatai, de ezek ára, feltétele, korlátja vagy ellenjátéka világosan követhető.

A névprofil és a tesztpaklik csak az első javító- és auditkör után következnek.

A fájlban csak olyan módosítás kerülhet végleges munkaszintű állapotba, amely követhető, auditálható és szükség esetén visszakereshető.
