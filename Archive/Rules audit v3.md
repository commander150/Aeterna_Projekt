# AETERNA – SZABÁLY AUDIT DOKUMENTUM (v3)

Ez a dokumentum az AETERNA jelenlegi, konszolidált szabályauditját tartalmazza.
Célja, hogy egyetlen, ellentmondásmentes alapdokumentumként szolgáljon a teljes szabálykönyv későbbi újraírásához.

A dokumentumban kizárólag a véglegesített vagy átmenetileg elfogadott szabályértelmezések szerepelnek.
A korábbi, felülírt verziók nem részei ennek az állapotnak.

---

## 1. TÁMADÁS, CÉLZÁS, ÁRAMLAT

### 1.1 A támadás alapelve

A támadás nem a támadó Entitás saját pozíciójából vagy saját Áramlatából következik, hanem célpontválasztással történik.
A támadó játékos egy támadó Entitást választ, majd egy érvényes célpontot jelöl ki.

A saját támadó Entitás helye ebből a szempontból irreleváns.
A támadás érvényességét nem az határozza meg, hogy a támadó melyik oszlopban áll, hanem az, hogy a kijelölt célpont a szabályok szerint támadható-e.

---

### 1.2 Az Áramlat szerepe

Az Áramlat a játéktér védelmi szerkezeti egysége.
Egy Áramlat három egymás mögötti részből áll:

1. Horizont
2. Zenit
3. Pecsét

Az Áramlat nem támadási kötöttséget jelent, hanem azt határozza meg, hogy egy adott pozíció mögött mi érhető el, és mi védett.

---

### 1.3 Támadható célpontok

A támadási célpontok érvényessége a következő szabályok szerint dől el:

* Ha az ellenfélnél van aktív Oltalommal rendelkező Entitás a Horizonton, akkor támadással kizárólag Oltalommal rendelkező célpont választható.
* Ha nincs ilyen Oltalommal rendelkező Entitás, akkor bármely kimerült Horizont-Entitás megtámadható.
* Ha egy adott pozícióban nincs Horizont-Entitás, akkor az ugyanott álló Zenit-Entitás támadható.
* Ha egy adott pozícióban sem Horizont-, sem Zenit-Entitás nincs, akkor az ott lévő Pecsét támadható.
* Ha a játékosnak már nincs egyetlen Pecsétje sem, az Aeternal támadhatóvá válik.

---

### 1.4 Horizont és Zenit sebezhetősége

A Horizonton lévő Entitások közül alapszabály szerint csak a kimerült Entitások támadhatók.

A Zenitben lévő Entitás akkor támadható fizikai támadással, ha az előtte lévő Horizont mező üres.
Ebben az esetben a Zenit-Entitás nem azért támadható, mert a támadás „átmegy” egy Áramlaton, hanem azért, mert az adott pozícióban nincs előtte védő Horizont-Entitás.

---

### 1.5 Aeternal támadhatósága

Az Aeternal kizárólag akkor válik támadhatóvá, ha a játékos összes Pecsétje eltűnt, vagyis 0 Pecsétje maradt.

Ebben az állapotban egy sikeres támadás az Aeternal ellen azonnali vereséget jelent.

---

## 2. SEBZÉS ÉS PECSÉT-FELTÖRÉS

### 2.1 A sebzés fogalma

A sebzés kizárólag HP-val rendelkező célpontot érhet.
Ennek megfelelően a sebzés alapértelmezett célpontja Entitás.

A sebzés az Entitás HP értékéből kerül levonásra.
Ha a HP 0-ra vagy az alá csökken, az Entitás megsemmisül és az Ürességbe kerül.

---

### 2.2 A Pecsét-feltörés fogalma

A Pecsét nem rendelkezik HP-val.
Ebből következően a Pecsét nem szenved sebzést.

A Pecsét eltávolítása egy külön játékművelet, amelyet Pecsét-feltörésnek nevezünk.

Pecsétet kizárólag az alábbi esetek törhetnek fel:

* blokkolatlan fizikai támadás,
* vagy olyan explicit kártyaszöveg, amely Pecsét-feltörést ír elő.

Direkt sebzés vagy általános „okozz X sebzést” típusú hatás nem alakítható át automatikusan Pecsét-feltöréssé.

---

### 2.3 Pecsét-feltörés támadásból

Ha egy fizikai támadás érvényesen eléri a Pecsétet, akkor pontosan 1 darab Pecsét törik fel.

A támadó Entitás ATK értéke nem növeli a feltört Pecsétek számát.
Egy normál fizikai támadás alapértelmezésben legfeljebb 1 darab Pecsétet törhet fel.

---

### 2.4 Többes Pecsét-feltörés

Több Pecsét feltörése csak akkor lehetséges, ha azt egy képesség vagy kártyaszöveg kifejezetten előírja.

Ez nem azonos a sebzés fogalmával, és nem következik az ATK értékből önmagában.

---

## 3. HARCI FELDOLGOZÁS, BLOKK, PUSZTULÁS

### 3.1 A támadás deklarálása

Egy támadás menete a következő alaplépésekből áll:

1. támadó Entitás kijelölése,
2. célpont kijelölése,
3. támadás deklarálása.

A támadás után a támadó Entitás kimerül.

---

### 3.2 Reakciós ablak támadásra

A támadás deklarálása után reakciós ablak nyílik.
Ebben az ablakban az olyan reakciók és Jelek használhatók, amelyek triggerfeltétele teljesült.

---

### 3.3 Blokkolás

A védekező játékos egy aktív, Horizonton lévő Entitással blokkolhat.

Blokkolás esetén:

* a blokkoló Entitás válik a támadás új célpontjává,
* az eredeti célpont nem szenved sebzést,
* a blokkoló Entitás kimerül.

Egy támadás ellen pontosan egy blokkoló használható.
Zenit-Entitás nem blokkolhat.
Kimerült Entitás nem blokkolhat.

A blokk teljes célpontcsere, nem sebzésmegosztás.

---

### 3.4 Harci sebzés

Ha a célpont Entitás, a támadó Entitás a saját ATK értékének megfelelő sebzést okoz neki.

Ha a támadást blokkolták, a támadó és a blokkoló egymásnak okoz harci sebzést.
A harci sebzés ilyen esetben egyszerre történik.

---

### 3.5 Megsemmisülés és túlélés

Az Entitás megsemmisül, ha aktuális HP értéke 0-ra vagy az alá csökken.

A megsemmisült Entitás a Domíniumból az Ürességbe kerül.

Ha egy Entitás túléli a harcot vagy egyéb sebzést, a rajta lévő sérülés megmarad az Eloszlás fázisig.
Az Eloszlás fázisban a túlélő Entitásokról lekerül a sebzés, és visszaállnak teljes HP-ra.

---

## 4. HASÍTÁS (SUNDERING)

### 4.1 Alapelv

A Hasítás a túlcsorduló harci sebzéshez kapcsolódó képesség.

Ha egy Hasítás képességgel rendelkező Entitás több harci sebzést okoz, mint amennyi a célpont HP-ja, a fennmaradó sebzés továbbvihető.

---

### 4.2 A továbbvitt sebzés iránya

A fennmaradó sebzés először egy másik érvényes Entitásra kerülhet át ugyanabban a feloldási láncban.
Ha ilyen nincs, akkor a támadás 1 darab Pecsét feltörését okozza.

A Hasítás nem teszi a Pecsétet sebződő célponttá.
A Pecsét ebben az esetben sem sebzést kap, hanem külön következményként törik fel.

---

## 5. IDÉZÉSI BETEGSÉG ÉS TÁMADÁSI JOGOSULTSÁG

### 5.1 Idézési betegség

Az újonnan kijátszott Horizont-Entitás aktív állapotban érkezik meg, de ugyanabban a körben nem indíthat támadást.

Ez nem azonos a kimerültséggel.
Az idézési betegség támadási tiltás, nem fizikai állapot.

Az így kijátszott Entitás ugyanabban a körben még blokkolhat, ha egyébként szabályosan képes erre.

---

### 5.2 Gyorsaság (Celerity)

A Gyorsaság képességgel rendelkező Entitás figyelmen kívül hagyja az idézési betegséget, és a kijátszása körében is támadhat.

---

### 5.3 Első körös támadási tiltás

A kezdő játékos a játék első saját körében nem indíthat támadást.

Ez globális szabály, és nem az Entitások egyedi állapotából következik.

---

## 6. ERŐFORRÁSRENDSZER

### 6.1 Ősforrás

Az Ősforrás a játék központi erőforrászónája.
A játékos a Beáramlás fázisban pontosan 1 lapot helyezhet ide a kezéből, képpel lefelé.

Az Ősforrás lapjai nem normál játéktéri lapként működnek, hanem erőforrásként.

---

### 6.2 Magnitúdó

A Magnitúdó az Ősforrásban lévő lapok száma.
Ez határozza meg, hogy a játékos milyen szintű lapokat játszhat ki.

A Magnitúdó nem fizetőeszköz, hanem kijátszási küszöb.

---

### 6.3 Aura

Az Aura a ténylegesen elkölthető erőforrás.

Az Ősforrás minden aktív lapja 1 Aurát biztosít.
A költségek kifizetése a megfelelő számú Aura-forrás kimerítésével történik.

---

### 6.4 Kimerítés és visszaállítás

A Kimerítés a lap 90 fokos elfordítása.
Ez jelzi, hogy a lapot a körben már felhasználták.

Az Ébredés fázisban minden kimerült lap visszaáll aktív állapotba.

---

### 6.5 Képességből eredő visszaállítás

A képességből fakadó Visszaállítás nem lehet általános, szabadon választott művelet.

Ha egy kártya vagy képesség visszaállít valamit, annak egyértelműen meg kell határoznia, hogy:

* Entitást,
* vagy Ősforrásban lévő lapot
  érint.

A játékos nem döntheti el szabadon, hogy a két kategória közül melyikre alkalmazza.

---

### 6.6 Entitások fizetése

Az Entitások kijátszási költsége fizethető:

* saját Birodalmi Aurából,
* Aether (Semleges) Aurából,
* vagy ezek kombinációjából.

Entitások esetén nincs Soft Penalty.

---

### 6.7 Varázslatok fizetése és Soft Penalty

A Varázslatok alapértelmezésben saját Birodalmi Aurával fizethetők ki a legkedvezőbben.
Aether Aura is bevonható a fizetésbe, de ekkor Soft Penalty lép életbe.

A Soft Penalty szabály szerint, ha egy Varázslat kifizetéséhez Aether Aurát is használsz, a Varázslat teljes költsége +1 Aurával megnő.

---

### 6.8 Birodalmi színek

A Birodalmakhoz társított színek kizárólag vizuális megkülönböztetést szolgálnak.
Mechanikailag a Birodalomhoz tartozás számít, nem a szín mint külön játékelem.

---

## 7. BURST, SURGE, GONDVISELÉS, JEL

### 7.1 Pecsét-feltörés utáni alapfolyamat

Ha egy Pecsét feltörik, a hozzá tartozó lap a játékos kezébe kerül.
Ez a Pecsét-feltörés alapkövetkezménye.

A Surge gyűjtőfogalomként a Pecsét-feltörés utáni következményrendszert jelenti.
Ide tartozik:

* a lap kézbe kerülése,
* a Burst lehetősége,
* és a Gondviselés lehetősége.

---

### 7.2 Burst – végleges változat

Ha a feltört Pecsét lapja Burst képességgel rendelkezik, a lap kézbe kerülése után a játékos eldöntheti, hogy azonnal Burstként használja-e.

Ha használja, a Burst ekkor és csak ekkor, azonnal és költség nélkül oldódik fel.

Ha nem használja, a Burst-ablak lezárul, a lap a kézben marad, és később már csak a normál használati feltételek szerint játszható ki.

A Burst tehát nem kötelező, de a Pecsét-feltörés pillanatához kötött, egyszeri azonnali lehetőség.

---

### 7.3 Több Burst egyszerre

Ha több Pecsét törik fel ugyanabban az eseményláncban, minden Pecsét külön Surge-folyamatot indít.

A Bursttel rendelkező lapok külön kerülnek feldolgozásra, és a játékos határozza meg a feloldás sorrendjét.

---

### 7.4 Gondviselés

Ha a feltört Pecsét lapjának Magnitúdója magasabb, mint a játékos jelenlegi Magnitúdója, a játékos dönthet úgy, hogy a lapot azonnal az Ősforrásába helyezi.

A Gondviselés opcionális hatás.
A lap először kézbe kerül, és csak ezután kerülhet át az Ősforrásba.

A Gondviselésből az Ősforrásba kerülő lap nem számít bele a kör normál Beáramlás fázisának 1 lapos korlátjába.

---

### 7.5 Jel (Trap)

A Jel előre lerakott, rejtett reakciólap, amely a Zenitbe kerül.

A Jel nem automatikusan aktiválódik.
A játékos dönt róla, hogy a triggerfeltétel teljesülésekor használja-e.

Ha a feltétel teljesült, de a játékos nem aktiválja abban az eseményablakban, akkor a Jel megmarad, de csak egy újabb, ismét teljesülő trigger esetén dönthet újra róla.

A Jel nem használható visszamenőleg egy már elmúlt triggerre.

---

## 8. OLTALOM, LÉGIES, MÉTELY, HARMONIZÁLÁS, REZONANCIA, VISSZHANG

### 8.1 Oltalom (Aegis)

Amíg az ellenfélnél van aktív Oltalommal rendelkező Entitás a Horizonton, addig támadással kizárólag Oltalommal rendelkező célpont választható.

Ez felülírja az általános célpontválasztási szabályokat.

Ha több Oltalommal rendelkező aktív Entitás van, a támadó ezek közül választhat.

---

### 8.2 Légies

A Légies képesség a fizikai interakciókat korlátozza.

A Légies Entitást fizikai támadással csak másik Légies Entitás támadhatja szabályosan, és fizikai blokkolásban is csak másik Légies Entitás vehet részt vele szemben.

A képesség nem vonatkozik varázslatokra, lapképességekre vagy egyéb nem fizikai hatásokra.

---

### 8.3 Métely

A Métely képességgel megsebzett Entitás, ha túléli a sebzést, nem azonnal pusztul el, hanem a következő kör elején semmisül meg.

A „következő kör” itt a következő globális kört jelenti, nem a tulajdonos következő saját körét.

---

### 8.4 Harmonizálás

A Harmonizálás a Zenitből az előtte, vele azonos pozícióban álló Horizont-Entitásnak nyújt támogatást.

Az alap Harmonizálás Magnitúdó-alapú ATK-bónuszt ad:

* Mag 1–4 esetén +2 ATK,
* Mag 5–8 esetén +1 ATK,
* Mag 9+ esetén a lap nem rendelkezhet Harmonizálás kulcsszóval.

Egy célponton egyszerre csak 1 Harmonizálás hatás lehet aktív.

Bizonyos lapok a Harmonizálás alap hatását további, a kártyaszövegben meghatározott támogatási effekttel bővíthetik.

Ha a Zenitben lévő Harmonizáló Entitás előtt nincs Horizont-Entitás, a Harmonizálás nem fejt ki hatást.

---

### 8.5 Rezonancia

A Rezonancia X azt jelenti, hogy az Entitás, amíg a Zenitben van, minden saját Ébredés fázisban X mennyiségű extra Aurát biztosít.

Skálázás:

* Mag 1–4 → Rezonancia 2
* Mag 5–8 → Rezonancia 1

---

### 8.6 Visszhang

A Visszhang akkor aktiválódik, amikor a lap az Ürességbe kerül.

Ha egy hatás megakadályozza, hogy a lap az Ürességbe kerüljön, vagy más zónába helyezi át, a Visszhang nem aktiválódik.

---

## 9. REFRESH PENALTY

### 9.1 Paklikifogyás

Ha a játékosnak húznia kellene, de a paklija üres, nem veszít azonnal.

Ehelyett az Ürességben lévő lapjait új húzópaklivá keveri.

---

### 9.2 A Refresh Penalty költsége

Az újrakeverés ára, hogy a játékosnak azonnal meg kell semmisítenie 1 saját, még ép Pecsétjét.

Ez nem normál Pecsét-feltörés:

* nem számít támadásnak,
* nem indít Surge-folyamatot,
* nem aktivál Burstöt,
* a lap közvetlenül az Ürességbe kerül.

---

### 9.3 Vereség deck-out miatt

Ha a játékosnak húznia kellene, a paklija üres, és nincs saját ép Pecsétje, amelyet a Refresh Penalty költségeként feláldozhatna, azonnal elveszíti a játékot.

Ez külön vereségi feltétel, nem azonos az Aeternal megtámadásából eredő vereséggel.

---

### 9.4 Jövőbeli megfigyelési pont

A jelenlegi szabályrendszerben nyitott kockázat, hogy Pecsét-visszaállító hatásokkal és Refresh Penalty ismétlődéssel túl hosszú vagy végtelen közeli játékhurkok alakulhatnak ki.

Ez jelenleg nem kap külön hard limit szabályt.
Csak akkor kerül külön szabályozásra, ha a tesztfutások ténylegesen indokolják.

---

## 10. JELENLEGI ÁLLAPOT

A jelenlegi audit alapján a rendszer fő szabálymagja már összerakható egy új szabálykönyv alapjává.

A következő fázis logikusan már nem újabb szétszórt auditjegyzetek gyártása, hanem ennek a konszolidált anyagnak a felhasználása egy tiszta, újraszerkesztett szabálykönyv elkészítéséhez.

---
