# AETERNA – SZABÁLY AUDIT DOKUMENTUM (v1)

---

## TÁMADÁS ÉS CÉLZÁS

### 1. Eredeti szabály

A támadás áramlaton keresztül történik, és a támadás iránya számít.

### 2. Tényleges működés

A játékos kiválaszt egy célpontot a Horizonton, függetlenül attól, melyik áramlatból támad.

### 3. Probléma

Az áramlat-alapú támadási logika félrevezető, és nem tükrözi a tényleges működést.

### 4. Javított szabály

A támadó játékos szabadon választ célpontot az ellenfél Horizontján.
Az áramlat kiválasztása nem befolyásolja a támadás érvényességét.

### 5. Megjegyzés

Az áramlat csak a Zenit védettsége miatt releváns.

---

## TÁMADHATÓ CÉLPONTOK

### 1. Eredeti szabály

Az entitások általánosan támadhatók.

### 2. Tényleges működés

Csak kimerült (Kimerített) entitások támadhatók.

### 3. Probléma

Ez alapvető szabály, de nincs elég hangsúlyosan és egyértelműen definiálva.

### 4. Javított szabály

Csak kimerült entitás választható támadás célpontjaként a Horizonton.

### 5. Megjegyzés

Ez az egyik legfontosabb core szabály → kiemelten kell kezelni a végleges dokumentumban.

---

## ZENIT SEBEZHETŐSÉG

### 1. Eredeti szabály

A Zenit védett zóna.

### 2. Tényleges működés

A Zenit entitás mindig sebezhető, HA nincs előtte Horizonton entitás.

### 3. Probléma

A szabály gyakran fordítva van értelmezve (mintha alapból védett lenne).

### 4. Javított szabály

A Zenit entitás sebezhető, ha az előtte lévő Horizont pozíció üres.
Ha van előtte entitás, akkor az védi.

### 5. Megjegyzés

Ez egy strukturális szabály, nem kivétel.

---

## AETERNAL TÁMADHATÓSÁG

### 1. Eredeti szabály

Az Aeternal támadható bizonyos helyzetekben.

### 2. Tényleges működés

Az Aeternal CSAK akkor támadható, ha a játékosnak 0 darab Pecsétje van.

### 3. Probléma

Korábban nem volt egyértelműen lezárva.

### 4. Javított szabály

Az Aeternal kizárólag akkor válik támadhatóvá, ha a játékos összes Pecsétje megsemmisült.

### 5. Megjegyzés

Ez a győzelmi feltétel kulcseleme.

---

## HASÍTÁS (SUNDERING) – ÚJRADEFINIÁLÁS

### 1. Eredeti szabály

Több Pecsét törése vagy speciális támadási hatás.

### 2. Tényleges működés

Nem konzisztens, hibás implementáció és szabályleírás.

### 3. Probléma

Az eredeti definíció nem működőképes és félreérthető.

### 4. Javított szabály

Ha egy Hasítás képességgel rendelkező entitás támadásakor az okozott sebzés meghaladja a célpont HP értékét:

* a fennmaradó sebzés egy másik entitásra kerül át
* ha nincs másik entitás az adott oldalon:
  → a támadás 1 darab Pecséttörést okoz

### 5. Megjegyzés

Ez a Piercing mechanika átdolgozott verziója.

---

## SEBZÉS ÉS TÚLCSORDULÁS

### 1. Eredeti szabály

A sebzés célponton belül marad.

### 2. Tényleges működés

Normál esetben a sebzés nem terjed tovább.

### 3. Probléma

Nincs egyértelműen elválasztva a Hasítás viselkedésétől.

### 4. Javított szabály

Sebzés nem vihető át másik célpontra, kivéve ha a támadó rendelkezik Hasítás képességgel.

### 5. Megjegyzés

Ez külön szabály, nem a Hasítás része.

---

## ÁRAMLAT SZEREPE

### 1. Eredeti szabály

Az áramlat meghatározza a támadás irányát.

### 2. Tényleges működés

Az áramlat csak a Zenit védelmi kapcsolat miatt releváns.

### 3. Probléma

Túl van értelmezve támadási szempontból.

### 4. Javított szabály

Az áramlat kizárólag a Horizont–Zenit kapcsolatot határozza meg.
A támadás célpontválasztása nem kötött áramlathoz.

### 5. Megjegyzés

Ez leegyszerűsíti a rendszert jelentősen.

---

## NYITOTT / MÉG NEM AUDITÁLT TERÜLETEK

* blokk mechanika (védekezés pontos menete)
* több támadó / több védekező interakciók
* idézési betegség (summoning sickness pontos működése)
* képességek időzítése (reakciók, burst, jelek)
* pecséttörés pontos lépései (támadás vs effekt)
* aura és magnitúdó finom részletek
* körfázisok precíz definíciója

---

## ÁLLAPOT

Ez a dokumentum az audit első stabil blokkját tartalmazza.
A további mechanikák ugyanebben a formátumban kerülnek feldolgozásra.

---

## BLOKK (VÉDEKEZÉS) MECHANIKA

### 1. Eredeti szabály

A védekező játékos blokkolhat támadásokat a Horizonton lévő entitásokkal.

### 2. Tényleges működés

A védekező játékos egy aktív (nem kimerült) Horizonton lévő entitást használhat blokkolásra.
A blokkoló entitás a blokk során kimerül.

### 3. Probléma

* Nincs egyértelműen definiálva:

  * mikor történik a blokk (időzítés)
  * hány blokkoló lehet
  * hogyan történik a célpontváltás
* Nem tiszta, hogy a blokk helyettesíti-e a célpontot vagy csak közbeavatkozik.

### 4. Javított szabály

Blokkolás menete:

1. A támadó kijelöli a célpontot.

2. A védekező játékos dönthet úgy, hogy blokkol.

3. Blokkolni csak:

   * aktív (nem kimerült)
   * Horizonton lévő
     entitással lehet.

4. Blokkolás esetén:

   * a blokkoló entitás válik a támadás új célpontjává
   * az eredeti célpont nem szenved sebzést

5. A blokkoló entitás:

   * kimerül a blokk során

6. Egy támadás ellen:

   * pontosan egy blokkoló használható

### 5. Megjegyzés

A blokk teljes célpontcsere, nem sebzésmegosztás.

---

## BLOKK ÉS CÉLZÁS VISZONYA

### 1. Eredeti szabály

A blokk védekezési opció.

### 2. Tényleges működés

A blokk felülírja a támadás eredeti célpontját.

### 3. Probléma

Nem volt kimondva, hogy ez teljes átirányítás.

### 4. Javított szabály

Blokkolás esetén a támadás célpontja teljes egészében a blokkoló entitás lesz.

### 5. Megjegyzés

Ez fontos a Hasítás és egyéb effekt interakciók miatt.

---

## BLOKK ÉS KIMERÜLTSÉG

### 1. Eredeti szabály

Nem volt egyértelműen definiálva.

### 2. Tényleges működés

A blokkolás kimeríti az entitást.

### 3. Probléma

Ha nincs kimondva, visszaéléshez vezet (többszöri blokk).

### 4. Javított szabály

A blokkoló entitás a blokk után azonnal kimerül.

### 5. Megjegyzés

Ez korlátozza a védekezési láncokat.

---

## BLOKK KORLÁTAI

### 1. Eredeti szabály

Nem részletezett.

### 2. Tényleges működés

Implicit korlátok vannak, de nincsenek formalizálva.

### 3. Probléma

Nem tiszta:

* több blokk lehetséges-e
* Zenitből lehet-e blokkolni

### 4. Javított szabály

* Egy támadás ellen csak egy blokkoló használható
* Csak Horizonton lévő entitás blokkolhat
* Zenit entitás nem blokkolhat
* Kimerült entitás nem blokkolhat

### 5. Megjegyzés

Ez stabil és egyszerű rendszert ad.

---

## BLOKK ÉS SPECIÁLIS ESETEK (ELŐKÉSZÍTÉS)

### 1. Eredeti szabály

Nincs.

### 2. Tényleges működés

Későbbi képességek módosíthatják.

### 3. Probléma

Nincs elkülönítve az alap és a kivétel.

### 4. Javított szabály

Az alap blokk szabályokat képességek felülírhatják.

### 5. Megjegyzés

Ez lesz az alap minden későbbi kulcsszóhoz.

---

## IDÉZÉSI BETEGSÉG (SUMMONING SICKNESS)

### 1. Eredeti szabály

Az újonnan kijátszott entitások nem támadhatnak azonnal.

### 2. Tényleges működés

A Horizonton megjelenő entitások aktív állapotban érkeznek, de nem indíthatnak támadást ugyanabban a körben.

### 3. Probléma

Nem egyértelmű:

* hogy blokkolhatnak-e
* hogy a kimerültség hogyan kapcsolódik hozzá
* hogy ez állapot vagy csak tiltás

### 4. Javított szabály

Az újonnan kijátszott entitás:

* aktív állapotban érkezik a Horizonton
* blokkolhat ugyanabban a körben
* nem indíthat támadást ugyanabban a körben

Ez egy ideiglenes állapot, amely a kör végéig tart.

### 5. Megjegyzés

Ez nem kimerültség, hanem támadási tiltás.

---

## IDÉZÉSI BETEGSÉG ÉS KIMERÜLTSÉG VISZONYA

### 1. Eredeti szabály

Nem tisztázott.

### 2. Tényleges működés

Két külön mechanika, de gyakran összekeverhető.

### 3. Probléma

Ha nincs szétválasztva, logikai hibákhoz vezet.

### 4. Javított szabály

* Az idézési betegség:
  → csak a támadás indítását tiltja

* A kimerültség:
  → fizikai állapot (nem támadhat, nem blokkolhat)

A kettő egymástól független.

### 5. Megjegyzés

Ez fontos minden további interakcióhoz.

---

## GYORSASÁG (CELERITY) – KIVÉTEL

### 1. Eredeti szabály

A Gyorsaság lehetővé teszi az azonnali támadást.

### 2. Tényleges működés

Felülírja az idézési betegséget.

### 3. Probléma

Nem volt egyértelműen elkülönítve kivételként.

### 4. Javított szabály

A Gyorsaság (Celerity) képességgel rendelkező entitás:

* figyelmen kívül hagyja az idézési betegséget
* azonnal támadhat abban a körben, amelyben kijátszották

### 5. Megjegyzés

Ez az első explicit kivétel az alap támadási szabály alól.

---

## ELSŐ KÖR KORLÁTOZÁS

### 1. Eredeti szabály

Az első játékos nem támadhat az első körben.

### 2. Tényleges működés

Ez egy globális szabály, független az entitások állapotától.

### 3. Probléma

Összekeverhető az idézési betegséggel.

### 4. Javított szabály

A kezdő játékos az első körében nem indíthat támadást.

### 5. Megjegyzés

Ez nem az entitásokra, hanem a játékosra vonatkozó szabály.

---

## TÁMADÁS ENGEDÉLYEZÉS FELTÉTELEI (ÖSSZESÍTÉS)

### 1. Eredeti szabály

Szétszórtan definiált feltételek.

### 2. Tényleges működés

Több külön szabály kombinációja.

### 3. Probléma

Nincs egy helyen összefoglalva.

### 4. Javított szabály

Egy entitás akkor támadhat, ha:

* a Horizonton van
* aktív (nem kimerült)
* nincs idézési betegsége
  VAGY rendelkezik Gyorsasággal
* a játékos nincs első körös támadási tiltás alatt

### 5. Megjegyzés

Ez egy kulcs összefoglaló blokk a végleges szabálykönyvhöz.

---

## PECSÉT (WARD) – ALAP DEFINÍCIÓ

### 1. Eredeti szabály

A játékos 5 Pecséttel rendelkezik, amelyeket az ellenfélnek le kell rombolnia.

### 2. Tényleges működés

A Pecsétek különálló objektumok, amelyek nem rendelkeznek HP-val.

### 3. Probléma

Nem volt elég egyértelmű:

* hogy nem sebződnek fokozatosan
* hogy minden támadás pontosan mit csinál velük

### 4. Javított szabály

A Pecsét:

* nem rendelkezik HP-val
* nem sebződik részlegesen
* egy sikeres támadás mindig pontosan 1 Pecséttörést okoz

### 5. Megjegyzés

Ez diszkrét rendszer, nem sebzés alapú.

---

## PECSÉTTÖRÉS – TÁMADÁSBÓL

### 1. Eredeti szabály

A támadás Pecséteket törhet.

### 2. Tényleges működés

Ha egy támadás nem kerül blokkolásra és a célpont Pecsét, akkor az eltörik.

### 3. Probléma

Nem volt egyértelmű:

* hogy az ATK számít-e
* hogy több törhető-e egyszerre

### 4. Javított szabály

Ha egy támadás sikeresen eléri a Pecséteket:

* pontosan 1 darab Pecsét törik
* az ATK érték nem befolyásolja a törés mértékét

### 5. Megjegyzés

Ez alapértelmezett viselkedés, kivételek külön szabályokkal.

---

## PECSÉTTÖRÉS – EFFEKTBŐL

### 1. Eredeti szabály

Egyes képességek közvetlenül Pecséteket törnek.

### 2. Tényleges működés

Sebzésként megfogalmazott effektek Pecséttörést okoznak.

### 3. Probléma

Nem volt tisztázva a sebzés → pecséttörés konverzió.

### 4. Javított szabály

Ha egy effekt azt mondja, hogy:

„X sebzést okoz közvetlenül az ellenfélnek vagy Pecséteinek”,

akkor:

* 1 sebzés = 1 darab Pecsét törése

### 5. Megjegyzés

Ez eltér a harci sebzéstől.

---

## PECSÉTEK ÉS AETERNAL VISZONYA

### 1. Eredeti szabály

A Pecsétek védik az Aeternalt.

### 2. Tényleges működés

Amíg van legalább 1 Pecsét, az Aeternal nem támadható.

### 3. Probléma

Nem volt teljesen lezárva.

### 4. Javított szabály

Amíg a játékos rendelkezik legalább 1 Pecséttel:

* az Aeternal nem választható célpontként

### 5. Megjegyzés

Ez összhangban van a korábban auditált szabállyal.

---

## 0 PECSÉT ÁLLAPOT

### 1. Eredeti szabály

A játék végéhez kapcsolódik.

### 2. Tényleges működés

A játékos védtelenné válik.

### 3. Probléma

Nem volt formalizálva állapotként.

### 4. Javított szabály

Ha egy játékosnak 0 Pecséte van:

* az Aeternal támadhatóvá válik
* bármilyen sikeres támadás az Aeternal ellen a játék azonnali elvesztését jelenti

### 5. Megjegyzés

Ez egy állapotváltás, nem csak következmény.

---

## PECSÉTTÖRÉS SORRENDJE (FONTOS)

### 1. Eredeti szabály

Nem részletezett.

### 2. Tényleges működés

Törés után további események történnek.

### 3. Probléma

Hiányzik a pontos lépéssor.

### 4. Javított szabály

Pecséttörés esemény sorrendje:

1. Pecsét megsemmisül
2. A játékos kézbe veszi a Pecséttel reprezentált lapot
3. Aktiválódnak az azonnali hatások (pl. Reakció / Burst)
4. Ellenőrzés: maradt-e még Pecsét

### 5. Megjegyzés

Ez kritikus a későbbi mechanikákhoz.

---

## TÖBBES PECSÉTTÖRÉS – KIVÉTEL

### 1. Eredeti szabály

Bizonyos képességek több Pecséttörést okozhatnak.

### 2. Tényleges működés

Nem egységesen definiált.

### 3. Probléma

Keveredik a Hasítással és effekt sebzéssel.

### 4. Javított szabály

Alap esetben:

* egy támadás = 1 Pecsét törése

Eltérés csak akkor történik, ha:

* egy képesség kifejezetten több Pecséttörést ír le

### 5. Megjegyzés

A Hasítás NEM többes Pecséttörés, csak speciális túlcsordulás.

---

## DECK-OUT ÉS PECSÉT

### 1. Eredeti szabály

Pakli elfogyása büntetéssel jár.

### 2. Tényleges működés

A játékos Pecséteket veszít.

### 3. Probléma

Nem volt összekötve a Pecséttörés rendszerrel.

### 4. Javított szabály

Ha a játékos húzna, de nincs lapja:

* újrakeveri a temetőt paklivá
* el kell pusztítania 1 darab ép Pecsétet

Ez:

* nem számít támadásnak
* nem aktivál Burst/reakció hatásokat

### 5. Megjegyzés

Ez külön mechanika, nem normál Pecséttörés.

---

## NYITOTT / MÉG NEM AUDITÁLT PECSÉT KAPCSOLATOK

* Burst / Reakció pontos működése
* Pecsétből kézbe vétel finom szabályai
* Pecsét manipuláció (visszaállítás, mozgatás)
* több effekt egyidejű Pecséttörése

---

## ÁLLAPOT

A Pecsétek mechanikája alap szinten stabilizálva.
A Burst és reakció rendszer még auditálásra vár.

---

## PECSÉT (WARD) – JAVÍTOTT DEFINÍCIÓ

### 1. Eredeti szabály

A Pecsét törhető és sebzésként értelmezhető.

### 2. Tényleges működés

A Pecsét nem sebződik, hanem egy külön művelettel törik.

### 3. Probléma

Korábban hibásan lett kezelve:

* sebzésként
* effekt konverzióval (X sebzés → X Pecséttörés)

### 4. Javított szabály

A Pecsét:

* nem rendelkezik HP-val
* nem szenved sebzést
* a Pecsét-feltörés egy különálló játékművelet

Pecsétet kizárólag:

* blokkolatlan fizikai támadás
  VAGY
* explicit „Törj fel X Pecsétet” szöveg

törhet fel.

### 5. Megjegyzés

A sebzés és a Pecséttörés teljesen külön rendszer.

---

## PECSÉTTÖRÉS – EFFEKTEK JAVÍTÁSA

### 1. Eredeti szabály

Sebzés alapú effektek Pecséteket törhetnek.

### 2. Tényleges működés

Ez nem megengedett.

### 3. Probléma

Hibás konverzió:
„X sebzés” → „X Pecséttörés”

### 4. Javított szabály

Tilos a direkt sebzést Pecsétekre alkalmazni.

* „okozz X sebzést” típusú effekt
  → nem tör Pecséteket

Pecséttörés csak explicit utasítással történhet.

### 5. Megjegyzés

Ez erősen szétválasztja a spell és combat rendszert.

---

## PECSÉTTÖRÉS – TÁMADÁSBÓL (JAVÍTOTT)

### 1. Eredeti szabály

A támadás Pecséteket törhet.

### 2. Tényleges működés

Csak blokkolatlan fizikai támadás tör Pecsétet.

### 3. Probléma

Nem volt elég szigorúan definiálva.

### 4. Javított szabály

Ha egy fizikai támadás:

* nincs blokkolva
  ÉS
* a célpont Áramlat végéig jut

akkor:

→ 1 darab Pecsét feltörik

### 5. Megjegyzés

Ez az alap Pecséttörési mód.

---

## ÁRAMLAT (STREAM) – STRUKTÚRA JAVÍTÁSA

### 1. Eredeti szabály

Az Áramlat két részből áll (Horizont + Zenit).

### 2. Tényleges működés

Az Áramlat három egymás mögötti elemből áll.

### 3. Probléma

A Pecsét nem volt integrálva az Áramlat definícióba.

### 4. Javított szabály

Egy Áramlat három részből áll:

1. Horizont (frontvonal)
2. Zenit (hátvéd)
3. Pecsét (hátsó réteg)

### 5. Megjegyzés

Ez a harci logika alapja.

---

## TÁMADÁS IRÁNYA – ÁRAMLAT ALAPÚ MODELL

### 1. Eredeti szabály

A célpont kiválasztása szabad a Horizonton.

### 2. Tényleges működés

A támadás mindig egy konkrét Áramlatra irányul.

### 3. Probléma

Korábban hibásan lett egyszerűsítve (szabad targetelés).

### 4. Javított szabály

A támadó játékos:

* egy ellenséges Áramlatot választ célpontként

A támadás:

* ezen az Áramlaton halad végig

Fontos:

* a támadó entitás saját Áramlata irreleváns

### 5. Megjegyzés

Ez visszaállítja a pozíciós harcot.

---

## ÁRAMLATON BELÜLI TÁMADÁSI PRIORITÁS

### 1. Eredeti szabály

Nem volt pontosan definiálva.

### 2. Tényleges működés

A támadás rétegenként halad.

### 3. Probléma

Hiányzott a teljes logikai lánc.

### 4. Javított szabály

Egy támadás az adott Áramlatban:

1. Horizont
2. ha nincs → Zenit
3. ha nincs → Pecsét

sorrendben halad.

### 5. Megjegyzés

Ez egységesíti a teljes támadási rendszert.

---

## KORREKCIÓ – KORÁBBI HIBA

### Érintett szabály

Szabad célpontválasztás a Horizonton

### Helyes állapot

A támadás Áramlat alapú, nem globális célzás.

---

## ÁLLAPOT

A harci rendszer egyik alaprétege újradefiniálva:

* Pecséttörés külön mechanika
* Direkt sebzés leválasztva
* Áramlat struktúra pontosítva
* Támadás iránya formalizálva

---

## TÁMADÁS ÉS ÁRAMLAT – HELYES MODELL

### 1. Alapelv

A támadás **nem az Áramlatból indul**, hanem **célpontválasztással működik**.

A támadó játékos:

* nem Áramlatot választ
* hanem konkrét célpontot választ az ellenfél Domíniumán

---

## 2. HORIZONT CÉLPONTOK

### Szabály

Ha az ellenfél Horizontján van legalább 1 Entitás:

* a támadó játékos **bármelyik Horizonton lévő Entitást megtámadhatja**

### Fontos

* teljesen független attól, hogy a támadó Entitás melyik mezőn áll
* nincs „szemben állás” vagy kötött oszlop

---

## 3. ZENIT CÉLPONTOK

### Szabály

Zeniten lévő Entitás akkor támadható, ha:

* az adott pozícióban **nincs előtte Horizonton Entitás**

### Következmény

* a Zenit **pozícióhoz kötötten válik sebezhetővé**
* de a támadó továbbra is **szabadon választhat célpontot**

---

## 4. PECSÉT TÁMADÁSA

### Szabály

Pecsét akkor támadható, ha az adott pozícióban:

* nincs Entitás a Horizonton
  ÉS
* nincs Entitás a Zeniten

### Következmény

* a Pecsét **csak teljesen üres „oszlop” mögött érhető el**

---

## 5. AZ ÁRAMLAT SZEREPE (PONTOSÍTVA)

Az Áramlat:

* nem korlátozza, hogy honnan támadhatsz
* hanem azt határozza meg, hogy **egy adott pozíció mögött mi érhető el**

Egy Áramlat három része:

1. Horizont
2. Zenit
3. Pecsét

Ez egy **védelmi réteg**, nem támadási kötöttség.

---

## 6. SPECIÁLIS KIVÉTEL – OLTALOM (AEGIS)

### Szabály

Ha az ellenfél rendelkezik legalább egy Oltalom (Aegis) kulcsszavú Entitással a Horizonton:

* **csak az Oltalommal rendelkező Entitás támadható**

### Következmény

* minden más célpont **érvénytelen**, amíg ez a feltétel fennáll

---

## 7. TÁMADÁSI PRIORITÁS – HELYES SORREND

A célpontválasztás szabálya:

1. Ha van Horizont Entitás → bármelyik választható
2. Ha egy adott pozícióban nincs Horizont → Zenit támadható
3. Ha ott sincs → Pecsét támadható

Ez **nem globális sorrend**, hanem **pozíciónként értelmezett elérhetőség**.

---

## 8. FONTOS KORREKCIÓ

Hibás volt:

* „A támadás egy kiválasztott Áramlaton halad végig”

Helyes:

* a játékos célpontot választ
* az Áramlat csak azt határozza meg, hogy mi védett

---

## ÁLLAPOT

A támadási rendszer helyesen:

* nincs kötve támadó pozícióhoz
* globális célpontválasztást használ
* az Áramlat csak védelmi struktúra
* kivételek (pl. Aegis) felülírhatják a célpontválasztást

---

## BURST / REAKCIÓ – ALAP MECHANIKA

### 1. Alapelv

A Burst (Reakció) egy **azonnali, megszakítás nélküli aktiválás**, amely:

* nem kerül kézbe normál módon
* nem kerül kijátszásra
* nem igényel Aura fizetést

---

## 2. MIKOR AKTIVÁLÓDIK

Burst kizárólag akkor aktiválódhat, amikor:

* egy Pecsét feltörik

A folyamat:

1. Pecsét feltörik
2. A Pecsét mögötti lap kézbe kerül
3. Ha a lap rendelkezik Burst / Reakció képességgel → azonnal aktiválódik

---

## 3. AUTOMATIKUS AKTIVÁLÁS

A Burst:

* nem opcionális (alap esetben)
* automatikusan lefut
* nem lehet „későbbre tartogatni”

---

## 4. ERŐFORRÁS SZABÁLY

Burst aktiválás:

* nem kerül Aura-ba
* nem számít kijátszásnak
* nem fogyaszt akciót

---

## 5. IDŐZÍTÉS (KRITIKUS)

A Burst:

* **a Pecséttörés után azonnal történik**
* még azelőtt, hogy a játék továbbhaladna

Ez azt jelenti:

* megszakítja az aktuális folyamatot
* azonnal resolve-ol

---

## 6. TÖBB BURST ESETÉN

Ha több Burst aktiválódik egyszerre:

* sorrendjük meghatározása szükséges

(→ ez még nincs formalizálva, audit szükséges)

---

## 7. JEL (TRAP) – ALAP MECHANIKA

### 1. Alapelv

A Jel egy előre lerakott, rejtett hatás.

* Zenitbe kerül
* képpel lefelé

---

## 8. AKTIVÁLÁS

A Jel aktiválódhat:

* egy esemény hatására
* egy trigger feltétel teljesülésekor

---

## 9. IDŐZÍTÉS

A Jel:

* reakcióként működik
* az eseményre válaszul aktiválódik

---

## 10. PROBLÉMA

Jelenleg nem tisztázott:

* mikor előzi meg a Burst a Jelt
* mikor aktiválódhat Jel Pecséttörés közben
* lehet-e több Jel láncolva

---

## 11. NYITOTT KÉRDÉSEK

* Burst vs Jel prioritás
* több trigger egyidejű kezelése
* opcionális vs kötelező reakciók
* reakciók megszakíthatják-e egymást

---

## ÁLLAPOT

A Burst alap mechanika stabil:

* Pecséthez kötött
* automatikus
* azonnali

A Jel és reakciós rendszer még **nincs teljesen formalizálva**.

---

## BURST (REAKCIÓ) – VÉGLEGESÍTETT MODELL

### 1. Alapelv

A Burst egy **kötelező, azonnali aktiválás**, amely kizárólag Pecséttöréshez kötött.

* nem opcionális
* nem kerül kijátszásra
* nem igényel Aura-t

---

## 2. AKTIVÁLÁSI FOLYAMAT

Pecséttöréskor:

1. Pecsét feltörik
2. A lap kézbe kerül
3. Ha van Burst → **azonnal aktiválódik**

---

## 3. FONTOS ELV

A Burst:

* nem „választható reakció”
* hanem **kötelező triggerelt esemény**

---

## 4. TÖBB BURST EGYIDEJŰ ESETÉN

(Duel Masters logika alapján rendezve)

Ha több Pecsét törik egyszerre ÉS több Burst aktiválódik:

👉 a Burst effektek **nem egyszerre futnak le**, hanem sorban

### Szabály:

* az aktiváló játékos (akié a Pecsét tört) határozza meg a sorrendet
* a Burst effektek **egyesével resolve-olnak**

### Következmény:

* nincs „stack” jellegű bonyolult lánc
* egyszerű, soros feldolgozás

---

## 5. IDŐZÍTÉS (KRITIKUS)

A Burst:

* közvetlenül a Pecséttörés után aktiválódik
* még a játék továbblépése előtt
* megszakítja az aktuális folyamatot

---

## 6. FONTOS KORLÁTOZÁS

Burst:

* nem halasztható
* nem tagadható meg
* nem aktiválható később

---

## 7. JEL (TRAP) – VÉGLEGESÍTETT MODELL

### 1. Alapelv

A Jel egy:

* előre lerakott
* feltételhez kötött
* opcionális reakció

---

## 8. AKTIVÁLÁS

A Jel:

* **nem automatikus**
* a játékos dönt róla

DE csak akkor, ha:

* a trigger feltétel teljesül

---

## 9. TRIGGER LOGIKA

Példa:

„Amikor egy ellenséges Entitás támad”

### Működés:

* minden egyes támadás egy külön trigger esemény
* minden eseménynél újra dönthetsz

---

## 10. KRITIKUS SZABÁLY

Ha a feltétel már nem teljesül:

* a Jel **nem aktiválható**

Példa:

* ellenfél támad → aktiválhatod
* ellenfél nem támad többet → **elveszett az aktiválási lehetőség**

---

## 11. TÖBB JEL ESETÉN

(egyszerűsített, konzisztens modell)

* minden Jel külön döntés
* nincs automatikus láncolás
* a játékos választ, hogy melyiket aktiválja

---

## 12. BURST VS JEL – PRIORITÁS

### Szabály:

1. Pecsét feltörik
2. Burst (ha van) → kötelezően lefut
3. utána jöhetnek egyéb reakciók (pl. Jel)

### Következmény:

* Burst mindig megelőzi a Jel-eket
* Jel nem tud „megelőzni” egy Burstöt

---

## 13. KORREKCIÓ – FONTOS ELV

Hibás lenne:

* Burst és Jel azonos szinten kezelése

Helyes:

* Burst = kötelező rendszer esemény
* Jel = opcionális játékos reakció

---

## 14. MODELL ÖSSZEFOGLALÓ

Burst:

* kötelező
* azonnali
* Pecséthez kötött
* sorrendben resolve

Jel:

* opcionális
* feltételhez kötött
* eseményenként dönthető
* elveszik, ha trigger elmúlik

---

## ÁLLAPOT

A reakciórendszer most már stabil:

* Burst = determinisztikus
* Jel = játékos döntés
* időzítés tiszta
* nincs rejtett konverzió

---

## KÖRSTRUKTÚRA – ALAP

Egy játékos köre fix fázisokból áll:

1. Ébredés
2. Beáramlás
3. Manifesztáció
4. Betörés
5. Eloszlás

---

## BETÖRÉS FÁZIS – ALAPELV

A Betörés fázis a harc fázisa.

Ebben a fázisban:

* a játékos támadásokat indíthat
* minden támadás külön esemény

---

## 1. TÁMADÁS INDÍTÁSA

Egy támadás lépései:

1. támadó Entitás kiválasztása
2. célpont kiválasztása
3. támadás deklarálása

Fontos:

* csak aktív (nem kimerült) Entitás támadhat
* a támadás után az Entitás kimerül (90° elfordítás)

---

## 2. REAKCIÓS ABLAK – TÁMADÁSRA

Miután a támadás deklarálva lett:

→ reakciós ablak nyílik

Itt aktiválható:

* Jel (ha feltétel teljesül)

Fontos:

* ez az egyetlen pont, ahol „támadásra reagáló” Jel működik

---

## 3. BLOKKOLÁS

A védekező játékos:

* választhat egy aktív Entitást a Horizonton
* és blokkolhatja a támadást

Ha blokk történik:

* a célpont megváltozik a blokkolóra

---

## 4. SEBZÉS FELDOLGOZÁSA

Ha a célpont Entitás:

* a támadó ATK-ja sebzést okoz
* ha a sebzés ≥ HP → az Entitás megsemmisül

Fontos:

* sebzés csak Entitást érhet
* nincs sebzés → Pecsét konverzió

---

## 5. SPECIÁLIS ESET – HASÍTÁS

Ha van Hasítás:

* a túlcsorduló sebzés továbbmegy

Prioritás:

1. másik Entitás az adott pozícióban
2. ha nincs → 1 Pecsét törik

---

## 6. HA NINCS ÉRVÉNYES ENTITÁS CÉLPONT

Ha a támadás olyan pozíciót ér:

* ahol nincs Entitás a Horizonton
  ÉS
* nincs Entitás a Zeniten

→ a támadás a Pecséthez jut

---

## 7. PECSÉTTÖRÉS

Ha a támadás eléri a Pecséteket:

* pontosan 1 Pecsét törik

Ez nem sebzés.

---

## 8. BURST ABLAK

Pecséttörés után AZONNAL:

1. lap kézbe kerül
2. Burst aktiválódik (ha van)

Ha több Burst:

* sorrendben, a tulajdonos döntése szerint

---

## 9. REAKCIÓK PECSÉTTÖRÉS UTÁN

Burst után:

→ új reakciós ablak nyílhat

(pl. Jel, ha van releváns trigger)

---

## 10. TÁMADÁS LEZÁRÁSA

A támadás véget ér:

* minden hatás lefutott
* minden reakció lezárult

---

## 11. KÖVETKEZŐ TÁMADÁS

A játékos:

* indíthat új támadást
  VAGY
* kilép a Betörés fázisból

---

## 12. FONTOS ELVEK

* minden támadás teljesen külön esemény
* nincs globális „combat stack”
* reakciók mindig lokális ablakokban történnek

---

## 13. KORREKCIÓK

Hibás volt:

* sebzés → Pecsét
* Áramlat-alapú támadás
* Burst késleltetése

Helyes:

* célpont alapú támadás
* Burst azonnali
* Jel esemény-alapú

---

## ÁLLAPOT

A combat flow most:

* lineáris
* implementálható
* konzisztens a korábbi javításokkal

---

## KÖRSTRUKTÚRA – ALAP

Egy játékos köre fix fázisokból áll:

1. Ébredés
2. Beáramlás
3. Manifesztáció
4. Betörés
5. Eloszlás

---

## BETÖRÉS FÁZIS – ALAPELV

A Betörés fázis a harc fázisa.

Ebben a fázisban:

* a játékos támadásokat indíthat
* minden támadás külön esemény

---

## 1. TÁMADÁS INDÍTÁSA

Egy támadás lépései:

1. támadó Entitás kiválasztása
2. célpont kiválasztása
3. támadás deklarálása

Fontos:

* csak aktív (nem kimerült) Entitás támadhat
* a támadás után az Entitás kimerül (90° elfordítás)

---

## 2. REAKCIÓS ABLAK – TÁMADÁSRA

Miután a támadás deklarálva lett:

→ reakciós ablak nyílik

Itt aktiválható:

* Jel (ha feltétel teljesül)

Fontos:

* ez az egyetlen pont, ahol „támadásra reagáló” Jel működik

---

## 3. BLOKKOLÁS

A védekező játékos:

* választhat egy aktív Entitást a Horizonton
* és blokkolhatja a támadást

Ha blokk történik:

* a célpont megváltozik a blokkolóra

---

## 4. SEBZÉS FELDOLGOZÁSA

Ha a célpont Entitás:

* a támadó ATK-ja sebzést okoz
* ha a sebzés ≥ HP → az Entitás megsemmisül

Fontos:

* sebzés csak Entitást érhet
* nincs sebzés → Pecsét konverzió

---

## 5. SPECIÁLIS ESET – HASÍTÁS

Ha van Hasítás:

* a túlcsorduló sebzés továbbmegy

Prioritás:

1. másik Entitás az adott pozícióban
2. ha nincs → 1 Pecsét törik

---

## 6. HA NINCS ÉRVÉNYES ENTITÁS CÉLPONT

Ha a támadás olyan pozíciót ér:

* ahol nincs Entitás a Horizonton
  ÉS
* nincs Entitás a Zeniten

→ a támadás a Pecséthez jut

---

## 7. PECSÉTTÖRÉS

Ha a támadás eléri a Pecséteket:

* pontosan 1 Pecsét törik

Ez nem sebzés.

---

## 8. BURST ABLAK

Pecséttörés után AZONNAL:

1. lap kézbe kerül
2. Burst aktiválódik (ha van)

Ha több Burst:

* sorrendben, a tulajdonos döntése szerint

---

## 9. REAKCIÓK PECSÉTTÖRÉS UTÁN

Burst után:

→ új reakciós ablak nyílhat

(pl. Jel, ha van releváns trigger)

---

## 10. TÁMADÁS LEZÁRÁSA

A támadás véget ér:

* minden hatás lefutott
* minden reakció lezárult

---

## 11. KÖVETKEZŐ TÁMADÁS

A játékos:

* indíthat új támadást
  VAGY
* kilép a Betörés fázisból

---

## 12. FONTOS ELVEK

* minden támadás teljesen külön esemény
* nincs globális „combat stack”
* reakciók mindig lokális ablakokban történnek

---

## 13. KORREKCIÓK

Hibás volt:

* sebzés → Pecsét
* Áramlat-alapú támadás
* Burst késleltetése

Helyes:

* célpont alapú támadás
* Burst azonnali
* Jel esemény-alapú

---

## ÁLLAPOT

A combat flow most:

* lineáris
* implementálható
* konzisztens a korábbi javításokkal

---

## BURST / REAKCIÓ – ALAP DEFINÍCIÓ

### 1. Eredeti szabály

A Burst a Pecsét feltörésekor aktiválódó különleges hatás.

### 2. Tényleges működés

A Burst a feltört Pecsét lapjához kötött, és a Pecsét feltörése után azonnal létrejön.

### 3. Probléma

Nem volt teljesen formalizálva:

* kötelező vagy opcionális-e
* mikor pontosan aktiválódik
* hogyan kezelendő több Burst egyszerre

### 4. Javított szabály

A Burst egy **kötelező**, Pecsét-feltöréshez kötött azonnali hatás.

Ha egy feltört Pecsét lapja Burst / Reakció képességgel rendelkezik, akkor:

* a lap kézbe kerül
* a Burst hatás azonnal aktiválódik

### 5. Megjegyzés

A Burst nem normál kijátszás, és nem választható későbbi időpontra.

---

## BURST AKTIVÁLÁS SORRENDJE

### 1. Eredeti szabály

A Pecsét feltörése után a lap kézbe kerül, majd aktiválódhat.

### 2. Tényleges működés

A Burst a Pecsét feltörés közvetlen következménye.

### 3. Probléma

Nem volt elég világosan elválasztva a törés, a kézbe vétel és az effekt aktiválása.

### 4. Javított szabály

A Burst aktiválás sorrendje:

1. Pecsét feltörik
2. A Pecsét lapja kézbe kerül
3. Ha a lapon Burst van, a Burst azonnal aktiválódik
4. A Burst teljes egészében lefut
5. Csak ezután haladhat tovább a játékfolyamat

### 5. Megjegyzés

A Burst a Pecsét-feltörés lezárásának része.

---

## BURST KÖLTSÉGE ÉS STÁTUSZA

### 1. Eredeti szabály

A Burst különleges, azonnali hatás.

### 2. Tényleges működés

A Burst nem a normál kijátszási szabályok szerint működik.

### 3. Probléma

Nem volt külön kimondva, hogy Aura, kijátszás és akciószámítás szempontjából minek számít.

### 4. Javított szabály

A Burst:

* nem igényel Aura-fizetést
* nem számít normál kijátszásnak
* nem fogyaszt külön akciót
* nem halasztható el

### 5. Megjegyzés

A Burst kötelező triggerelt esemény.

---

## TÖBB BURST EGYIDEJŰ ESETÉN

### 1. Eredeti szabály

Nem részletezett.

### 2. Tényleges működés

Előfordulhat, hogy több Pecsét törik fel egyidejűleg vagy ugyanazon esemény részeként.

### 3. Probléma

Nem volt meghatározva, hogyan kell több Burstöt kezelni.

### 4. Javított szabály

Ha több Burst aktiválódik ugyanabban a feloldási ablakban, akkor:

* ezek nem egyszerre futnak le
* egymás után, sorban oldódnak fel
* a sorrendet a Burstöt birtokló játékos határozza meg

### 5. Megjegyzés

Ez egyszerű, soros feloldást ad.

---

## JEL (TRAP) – ALAP DEFINÍCIÓ

### 1. Eredeti szabály

A Jel egy előre lerakott, rejtett reakciólap.

### 2. Tényleges működés

A Jel a Zenitbe kerül lefordítva, és csak akkor használható, ha a saját feltétele teljesül.

### 3. Probléma

Nem volt teljesen világos, hogy automatikus vagy döntéshez kötött-e.

### 4. Javított szabály

A Jel egy:

* előre lerakott
* feltételhez kötött
* opcionális reakció

A Jel csak akkor aktiválható, ha a megadott triggerfeltétel teljesül.

### 5. Megjegyzés

A Jel nem kötelező, a használatáról a játékos dönt.

---

## JEL AKTIVÁLÁSA – JÁTÉKOSI DÖNTÉS

### 1. Eredeti szabály

A Jel reagál eseményekre.

### 2. Tényleges működés

A játékos dönt róla, hogy a teljesült triggerre reagál-e.

### 3. Probléma

Nem volt elválasztva a Burst kötelező jellegétől.

### 4. Javított szabály

Ha egy Jel feltétele teljesül, a játékos dönthet úgy, hogy aktiválja.

Ha nem aktiválja abban az eseményablakban, akkor:

* a Jel megmarad
* de csak egy újabb, ismét teljesülő triggernél dönthet róla újra

### 5. Megjegyzés

A Jel nem használható utólag egy már elmúlt triggerre.

---

## JEL TRIGGERPÉLDA – TÁMADÁS

### 1. Eredeti szabály

„Amikor egy ellenséges Entitás támad” típusú trigger.

### 2. Tényleges működés

Minden egyes támadás külön triggeresemény.

### 3. Probléma

Fontos tisztázni, hogy egy több támadásos körben mikor lehet aktiválni.

### 4. Javított szabály

Ha a Jel feltétele például:

* „amikor egy ellenséges Entitás támad”

akkor:

* minden egyes támadás külön triggeralkalom
* a játékos minden ilyen alkalomnál külön dönthet az aktiválásról

Ha az ellenfél nem támad többet, akkor:

* a korábban el nem használt Jel arra az elmúlt eseményre már nem aktiválható

### 5. Megjegyzés

A triggerablak eseményhez kötött, nem tart nyitva korlátlan ideig.

---

## BURST ÉS JEL PRIORITÁSA

### 1. Eredeti szabály

Mindkettő reakciószerű hatás.

### 2. Tényleges működés

Eltérő természetűek:

* Burst: kötelező rendszeresemény
* Jel: opcionális játékosi reakció

### 3. Probléma

Nem volt formalizálva a kettő közötti prioritás.

### 4. Javított szabály

Ha egy Pecsét feltörése Burstöt hoz létre, akkor:

1. a Pecsét-feltörés lezajlik
2. a Burst azonnal és kötelezően feloldódik
3. csak ezután jöhetnek egyéb reakciók vagy további döntési ablakok

### 5. Megjegyzés

A Burst elsőbbséget élvez a normál opcionális reakciókkal szemben.

---

## TÖBB JEL EGYIDEJŰ LEHETŐSÉGE

### 1. Eredeti szabály

Nem részletezett.

### 2. Tényleges működés

Lehetséges, hogy több Jel feltétele is teljesül ugyanarra az eseményre.

### 3. Probléma

Nincs formalizálva a választás és a sorrend.

### 4. Javított szabály

Ha ugyanarra az eseményre több saját Jel is aktiválható lenne, akkor:

* a játékos dönt, hogy melyiket aktiválja
* minden Jel külön döntési lehetőség
* a sorrendet az aktiváló játékos határozza meg

### 5. Megjegyzés

Ez még később finomítható, de alapnak stabil.

---

## BURST ÉS JEL KÖZÖS ELVE

### 1. Eredeti szabály

Mindkettő reakciós mechanika.

### 2. Tényleges működés

Két eltérő szabálycsalád.

### 3. Probléma

Könnyen összemoshatóak.

### 4. Javított szabály

A Burst és a Jel külön kategória:

* Burst:

  * kötelező
  * Pecsét-feltöréshez kötött
  * azonnali
  * költségmentes

* Jel:

  * opcionális
  * triggerfeltételhez kötött
  * játékosi döntéshez kapcsolt
  * csak a triggerablakban használható

### 5. Megjegyzés

A két mechanikát a végleges szabályszövegben is külön kell kezelni.

---

## ÁLLAPOT

A Burst / Reakció / Jel rendszer jelenlegi alapja tisztázva:

* Burst = kötelező, azonnali, Pecsét-feltöréshez kötött
* Jel = opcionális, triggerfüggő, eseményablakhoz kötött
* Burst elsőbbséget élvez a normál reakciókkal szemben
* az el nem használt Jel nem aktiválható visszamenőleg

---

## ERŐFORRÁSRENDSZER – ALAP STRUKTÚRA

### 1. Eredeti szabály

A játék erőforrásait az Ősforrás biztosítja, amely Magnitúdót és Aurát ad.

### 2. Tényleges működés

Az Ősforrás a játék központi erőforrászónája, és minden erőforrás-szabály innen indul ki.

### 3. Probléma

A Magnitúdó, Aura, Kimerítés és fizetési szabályok több helyen külön szerepelnek, ezért könnyen szétcsúsznak.

### 4. Javított szabály

Az Ősforrás a játékos képpel lefelé lerakott lapjaiból álló erőforrászóna.
Ez határozza meg:

* a Magnitúdót
* az elérhető Aurát
* a kártyák kijátszhatóságának alapfeltételeit

### 5. Megjegyzés

Ez a rendszer alapja, ezért a végleges szabálykönyvben külön, tiszta fejezetet kell kapnia.

---

## ŐSFORRÁS

### 1. Eredeti szabály

A játékos minden körben lapot helyezhet az Ősforrásba.

### 2. Tényleges működés

A Beáramlás fázisban a játékos pontosan 1 lapot helyezhet ide képpel lefelé.

### 3. Probléma

Fontos elkülöníteni a kézben lévő, a Domíniumon lévő és az Ősforrásban lévő lapok funkcióját.

### 4. Javított szabály

Az Ősforrásba a játékos a Beáramlás fázisban pontosan 1 lapot helyezhet le a kezéből, képpel lefelé.

### 5. Megjegyzés

Az Ősforrásba tett lapok erőforrásként működnek, nem normál játéktéri lapként.

---

## MAGNITÚDÓ

### 1. Eredeti szabály

A Magnitúdó a szintkövetelmény.

### 2. Tényleges működés

A Magnitúdó az Ősforrásban lévő lapok száma.

### 3. Probléma

Néha költségként, néha szintként van kezelve.

### 4. Javított szabály

A Magnitúdó az Ősforrásban lévő lapok száma.
Ez határozza meg, hogy a játékos milyen szintű lapokat játszhat ki.

### 5. Megjegyzés

A Magnitúdó nem fizetőeszköz, hanem kijátszási küszöb.

---

## AURA

### 1. Eredeti szabály

Az Aura a ténylegesen elhasználható energia.

### 2. Tényleges működés

Az Ősforrás minden aktív lapja 1 Aurát biztosít.

### 3. Probléma

A Magnitúdóval könnyen összekeverhető.

### 4. Javított szabály

Az Aura a ténylegesen elkölthető erőforrás.
Az Ősforrás minden aktív lapja 1 Aurát biztosít.

### 5. Megjegyzés

Az Aura a költségek kifizetésére szolgál, a Magnitúdó csak korlátoz.

---

## KIMERÍTÉS

### 1. Eredeti szabály

A fizetéshez és bizonyos akciókhoz a lapokat el kell fordítani.

### 2. Tényleges működés

A Kimerítés 90 fokos elfordítással történik.

### 3. Probléma

A Kimerítés erőforrásfizetésnél, támadásnál és blokkolásnál is megjelenik, ezért egységes definíció kell.

### 4. Javított szabály

A Kimerítés egy kártya 90 fokos elfordítása.
Ez jelzi, hogy a lapot ebben a körben már használták.

### 5. Megjegyzés

A Kimerítés általános állapot, amely több szabályterületen is használatos.

---

## VISSZAÁLLÍTÁS

### 1. Eredeti szabály

A kör elején a kimerült lapok visszafordulnak.

### 2. Tényleges működés

Az Ébredés fázisban minden kimerült lap normál állásba kerül vissza.

### 3. Probléma

El kell különíteni a természetes kör eleji visszaállítást a képességekből eredő újraaktiválástól.

### 4. Javított szabály

Az Ébredés fázisban minden kimerült lap visszaáll aktív állapotba, vagyis normál állásba visszafordul.

### 5. Megjegyzés

Ez az alap visszaállítási folyamat, nem azonos a külön effektekből származó újraaktiválással.

---

## MAGNITÚDÓ ÉS AURA VISZONYA

### 1. Eredeti szabály

Mindkettő az Ősforráshoz kapcsolódik.

### 2. Tényleges működés

A Magnitúdó és az Aura ugyanabból a zónából származik, de eltérő szerepet tölt be.

### 3. Probléma

Ha nincs külön kimondva, könnyen egyetlen erőforrásnak tűnnek.

### 4. Javított szabály

A Magnitúdó és az Aura két külön funkció:

* Magnitúdó = kijátszási küszöb
* Aura = elkölthető fizetőerő

### 5. Megjegyzés

Ezt a különbséget a végleges szabálykönyvben hangsúlyosan kell kezelni.

---

## ENTITÁSOK FIZETÉSE

### 1. Eredeti szabály

Entitások saját Birodalmi és Aether Aurából is fizethetők.

### 2. Tényleges működés

A rendszer engedi a vegyes fizetést Entitásoknál.

### 3. Probléma

Fontos elkülöníteni a Varázslatok szabályától.

### 4. Javított szabály

Az Entitások kijátszási költsége fizethető:

* saját Birodalmi Aurából
* Aether (Semleges) Aurából
* vagy ezek kombinációjából

### 5. Megjegyzés

Entitásoknál nincs Soft Penalty.

---

## VARÁZSLATOK FIZETÉSE

### 1. Eredeti szabály

A Varázslatok saját Birodalmi Aurát igényelnek.

### 2. Tényleges működés

Aether Aura is használható, de Soft Penalty mellett.

### 3. Probléma

Korábbi verziókban teljes tiltásként szerepelt.

### 4. Javított szabály

A Varázslatok (Igék, Rituálék, Jelek) alapértelmezetten saját Birodalmi Aurával fizethetők ki a legkedvezőbben, de Aether Aura is bevonható a fizetésbe a Soft Penalty szabály szerint.

### 5. Megjegyzés

Ez nem tiltás, hanem büntetéssel engedett keverés.

---

## SOFT PENALTY

### 1. Eredeti szabály

A rendszer jutalmazza a tiszta fizetést, de nem tiltja a kevertet.

### 2. Tényleges működés

Ha Varázslat fizetésébe Aether Aura is bekerül, a teljes költség nő.

### 3. Probléma

Több helyen ellentmondásosan volt leírva.

### 4. Javított szabály

Ha egy Varázslat kifizetéséhez Aether (Semleges) Aurát is használsz, akkor a Varázslat teljes költsége +1 Aurával megnő.

### 5. Megjegyzés

Ez a kevert fizetés enyhe büntetése.

---

## BIRODALMI SZÍNEK

### 1. Eredeti szabály

A színek a Birodalmakhoz kapcsolódnak.

### 2. Tényleges működés

A színek csak vizuális megkülönböztetést szolgálnak.

### 3. Probléma

A „szín” mechanikai fogalomként félreérthető.

### 4. Javított szabály

A Birodalmak vizuális színe csak megkülönböztetésre szolgál.
Mechanikailag a Birodalomhoz tartozás számít, nem a szín mint játékelem.

### 5. Megjegyzés

Ezt érdemes a szabálykönyvben egyetlen helyen rögzíteni.

---

## ERŐFORRÁSFOLYAMAT – RÖVID ÖSSZEFOGLALÓ

### 1. Eredeti szabály

Szétszórtan szerepelt.

### 2. Tényleges működés

A játékos lapot tesz az Ősforrásba, ebből lesz Magnitúdó és Aura.

### 3. Probléma

Nincs egy helyen áttekinthetően összefoglalva.

### 4. Javított szabály

Az erőforrásrendszer folyamata:

1. lap kerül az Ősforrásba
2. nő a Magnitúdó
3. az aktív Ősforrás-lapok Aurát adnak
4. a költségek fizetése Kimerítéssel történik
5. az Ébredés fázisban a lapok visszaállnak

### 5. Megjegyzés

Ez a blokk jó lesz a végleges szabálykönyv rövid összefoglalójához is.

---

## ÁLLAPOT

Az erőforrásrendszer jelenlegi alapja tisztázva:

* Ősforrás = központi erőforrászóna
* Magnitúdó = kijátszási küszöb
* Aura = elkölthető erőforrás
* Kimerítés = 90 fokos elfordítás
* Entitások és Varázslatok fizetési szabálya különválasztva
* Soft Penalty formalizálva

---

A Visszaállítás képességből nem lehet általános, szabadon választott művelet.
A képességnek mindig meg kell határoznia, hogy pontosan mire vonatkozik:

Entitásra
vagy Ősforrásban lévő lapra

Tehát a javított elv:

a játékos nem döntheti el szabadon, hogy milyen típusú lapot állít vissza
a kártyaszöveg vagy képesség típusa meghatározza a célpontkört
a természetes, kör eleji Visszaállítás ettől külön szabály

---

## SURGE / PECSÉT-FELTÖRÉS UTÁNI LAPKEZELÉS

### 1. Eredeti szabály

A feltört Pecsét lapja kézbe kerül, és külön hatások aktiválódhatnak.

### 2. Tényleges működés

A Pecsét feltörése nemcsak védelmi veszteség, hanem lapnyerés is.

### 3. Probléma

A Pecsét-feltörés, a kézbe vétel, a Burst és a Gondviselés sorrendje könnyen összecsúszik.

### 4. Javított szabály

Ha egy Pecsét feltörik:

1. a Pecsét megszűnik védelemként
2. a hozzá tartozó lap a játékos kezébe kerül
3. ha a lapon Burst / Reakció van, az azonnal aktiválódik
4. ha a lapon Gondviselés feltétel teljesül, az a saját szabálya szerint feloldódik

### 5. Megjegyzés

A Pecsét-feltörés nem csak veszteség, hanem erőforrás- és reakcióforrás is.

---

## SURGE – ALAP DEFINÍCIÓ

### 1. Eredeti szabály

A Surge a Pecsét feltöréséhez kapcsolódó következményrendszer.

### 2. Tényleges működés

A feltört Pecsét lapja kézbe kerül, és további hatásokat nyithat meg.

### 3. Probléma

A Surge gyakran összeolvad a Bursttel, pedig nem ugyanaz.

### 4. Javított szabály

A Surge a Pecsét feltörése utáni általános következményrendszer gyűjtőneve.
Ide tartozik:

* a lap kézbe kerülése
* a Burst / Reakció esetleges aktiválódása
* a Gondviselés esetleges aktiválódása

### 5. Megjegyzés

A Burst a Surge egyik lehetséges része, nem maga a Surge teljes egésze.

---

## GONDVISELÉS – ALAP DEFINÍCIÓ

### 1. Eredeti szabály

Ha a feltört Pecsét lapja túl magas Magnitúdójú, az Ősforrásba kerülhet.

### 2. Tényleges működés

A játékos gyorsított erőforrásfejlődést kap bizonyos feltétellel.

### 3. Probléma

El kell különíteni a normál kézbe vételtől és a Bursttől.

### 4. Javított szabály

Ha a feltört Pecsét lapjának Magnitúdója magasabb, mint a játékos jelenlegi Magnitúdója, akkor a játékos azt azonnal és ingyen lehelyezheti az Ősforrásába.

### 5. Megjegyzés

Ez nem normál Beáramlás, hanem külön Pecsét-feltörési következmény.

---

## GONDVISELÉS – Opcionális vagy kötelező

### 1. Eredeti szabály

A játékos „lehelyezheti”.

### 2. Tényleges működés

Ez választási lehetőségként van megfogalmazva.

### 3. Probléma

Nem volt külön kiemelve, hogy ez eltér a Burst kötelező jellegétől.

### 4. Javított szabály

A Gondviselés opcionális hatás.
Ha a feltétel teljesül, a játékos dönthet úgy, hogy a lapot azonnal az Ősforrásába helyezi.

### 5. Megjegyzés

Ez fontos különbség a Bursthöz képest.

---

## GONDVISELÉS ÉS KÉZBE VÉTEL VISZONYA

### 1. Eredeti szabály

A Pecsét lapja kézbe kerül.

### 2. Tényleges működés

A lap előbb kézbe kerül, majd onnan kerülhet az Ősforrásba.

### 3. Probléma

Nem volt egyértelmű, hogy a Gondviselés megkerüli-e a kézbe vételt.

### 4. Javított szabály

A feltört Pecsét lapja először kézbe kerül.
A Gondviselés ezután ad lehetőséget arra, hogy a játékos azt azonnal az Ősforrásába helyezze.

### 5. Megjegyzés

Ez megőrzi az egységes Pecsét-feltörési sorrendet.

---

## GONDVISELÉS ÉS ŐSFORRÁS LIMIT

### 1. Eredeti szabály

Nem részletezett.

### 2. Tényleges működés

A Gondviselés extra Ősforrás-lapot hozhat létre a kör normál Beáramlásán felül.

### 3. Probléma

El kell különíteni a normál körönkénti 1 lapos Ősforrás-bővítéstől.

### 4. Javított szabály

A Gondviselésből az Ősforrásba kerülő lap nem számít bele a kör normál Beáramlás fázisában lehelyezhető 1 lapos korlátba.

### 5. Megjegyzés

Ez külön, triggerelt erőforrásnövekedés.

---

## SURGE – KÖTELEZŐ ÉS OPCIONÁLIS ELEMEK SZÉTVÁLASZTÁSA

### 1. Eredeti szabály

A Pecsét-feltörés többféle utóhatást hozhat.

### 2. Tényleges működés

Ezek egy része kötelező, más része opcionális.

### 3. Probléma

A rendszer könnyen összekeverhető.

### 4. Javított szabály

Pecsét-feltörés után:

* kötelező:

  * a lap kézbe kerülése
  * Burst aktiválása, ha van

* opcionális:

  * Gondviselés alkalmazása, ha a feltétel teljesül

### 5. Megjegyzés

Ez tiszta döntési szerkezetet ad.

---

## SURGE – TÖBB PECSÉT ESETÉN

### 1. Eredeti szabály

Nem részletezett.

### 2. Tényleges működés

Ha több Pecsét törik, több Surge-folyamat is létrejöhet.

### 3. Probléma

Nem volt egyértelmű a sorrend.

### 4. Javított szabály

Ha több Pecsét törik fel ugyanabban az eseményláncban, minden Pecsét külön Surge-folyamatot indít.
Ezeket sorban kell feldolgozni.

### 5. Megjegyzés

Ez összhangban van a több Burst egymás utáni feloldásával.

---

## ÁLLAPOT

A Pecsét-feltörés utáni lapkezelés jelenlegi alapja tisztázva:

* a lap mindig kézbe kerül
* a Burst kötelezően, azonnal aktiválódik
* a Gondviselés opcionális
* a Gondviselés az Ősforrásba helyezés külön útja
* a Surge gyűjtőfogalom, nem azonos a Bursttel

---

Burst – javított definíció

A Burst egy Pecsét-feltöréshez kötött, azonnali opcionális aktiválási lehetőség.

Ha a feltört Pecsét lapja Burst képességgel rendelkezik:

a lap kézbe kerül
a játékos dönthet úgy, hogy azonnal aktiválja Burstként

Ha nem aktiválja ekkor:

a Burst-ablak lezárul
a lap a kézben marad
később csak normál módon használható

---

## PAKLI KIFOGYÁSA – ALAPHELYZET

### 1. Eredeti szabály

A játékos nem veszít azonnal, ha elfogy a paklija.

### 2. Tényleges működés

Paklikifogyáskor újrakeverés történik, de ez büntetéssel jár.

### 3. Probléma

A paklikifogyás, az újrakeverés és a Pecsét-vesztés kapcsolatát egy helyen, tisztán kell rögzíteni.

### 4. Javított szabály

Ha a játékosnak húznia kellene, de a paklija üres, akkor nem veszít azonnal.
Ehelyett külön paklikifogyási eljárás indul el.

### 5. Megjegyzés

Ez a mechanika eltér a sok kártyajátékban szokásos azonnali vereségtől.

---

## ÚJRAKEVERÉS (REFRESH)

### 1. Eredeti szabály

Az Üresség új paklivá keverhető.

### 2. Tényleges működés

A játékos az Ürességben lévő lapjait új húzópaklivá alakítja.

### 3. Probléma

El kell különíteni a normál húzástól és a büntetéstől.

### 4. Javított szabály

Ha a játékos húzna, de a paklija üres, akkor az Ürességben lévő összes lapját megkeveri, és azok új húzópakliként szolgálnak.

### 5. Megjegyzés

Az újrakeverés a paklikifogyási eljárás része, nem különálló opcionális művelet.

---

## REFRESH PENALTY – ALAP DEFINÍCIÓ

### 1. Eredeti szabály

Az újrakeverésért a játékos Pecsétet veszít.

### 2. Tényleges működés

Az új pakli létrejön, de a játékosnak azonnal fel kell áldoznia egy ép Pecsétet.

### 3. Probléma

A Pecsét-vesztést el kell különíteni a normál Pecsét-feltöréstől.

### 4. Javított szabály

Az újrakeverés ára, hogy a játékosnak azonnal meg kell semmisítenie 1 saját, még ép Pecsétjét.

### 5. Megjegyzés

Ez büntetés, nem támadásból vagy effektből származó normál Pecsét-feltörés.

---

## A BÜNTETÉSBŐL ELVESZTETT PECSÉT STÁTUSZA

### 1. Eredeti szabály

A Pecsét elpusztul, de nem aktivál normál hatásokat.

### 2. Tényleges működés

A büntetésből elvesztett Pecsét nem ad kézbe lapot és nem aktivál Burstöt.

### 3. Probléma

Ha ez nincs kimondva, könnyen összekeverhető a normál Surge-folyamattal.

### 4. Javított szabály

A Refresh Penalty miatt elpusztított Pecsét:

* nem kerül kézbe
* nem indít Surge-folyamatot
* nem aktivál Burst / Reakció hatást

A lap közvetlenül az Ürességbe kerül.

### 5. Megjegyzés

Ez a legfontosabb különbség a normál Pecsét-feltöréshez képest.

---

## MIKOR KÖVETKEZIK BE A VERESÉG

### 1. Eredeti szabály

Ha nincs Pecsét, amit fel lehetne áldozni, a játékos veszít.

### 2. Tényleges működés

A paklikifogyás csak addig kezelhető, amíg van saját Pecsét a büntetés kifizetésére.

### 3. Probléma

Ezt el kell különíteni attól az állapottól, amikor a játékosnak 0 Pecsétje van, de a paklija még nem ürült ki.

### 4. Javított szabály

Ha a játékosnak húznia kellene, a paklija üres, és nincs saját ép Pecsétje, amelyet a Refresh Penalty költségeként feláldozhatna, akkor azonnal elveszíti a játékot.

### 5. Megjegyzés

Ez külön vereségi feltétel, nem azonos az Aeternal megtámadásával.

---

## REFRESH PENALTY ÉS 0 PECSÉT ÁLLAPOT VISZONYA

### 1. Eredeti szabály

A 0 Pecsét másik veszélyállapotot is jelent.

### 2. Tényleges működés

A 0 Pecsét önmagában még nem deck-out vereség, csak támadási szempontból teszi védtelenné a játékost.

### 3. Probléma

Külön kell választani a kétféle veszteségi útvonalat.

### 4. Javított szabály

A 0 Pecsét állapot önmagában azt jelenti, hogy az Aeternal támadhatóvá válik.
A deck-out miatti vereség csak akkor következik be, ha a játékosnak húznia kellene üres pakliból, és már nincs Pecsétje a Refresh Penalty megfizetésére.

### 5. Megjegyzés

Ez két külön vereségi mechanika.

---

## TÖBBSZÖRI ÚJRAKEVERÉS

### 1. Eredeti szabály

Nem kizárt, hogy a játékos többször is újrakeverje a pakliját.

### 2. Tényleges működés

Minden újabb paklikifogyás újabb Refresh Penaltyt vált ki.

### 3. Probléma

Ezt egyértelművé kell tenni, hogy ne egyszeri szabályként legyen értelmezve.

### 4. Javított szabály

Valahányszor a játékosnak húznia kellene üres pakliból, minden alkalommal új Refresh Penalty eljárás indul.

### 5. Megjegyzés

Ez fokozatosan közelebb viszi a játékost a vereséghez.

---

## PAKLI KIFOGYÁSA – RÖVID FOLYAMAT

### 1. Eredeti szabály

Szétszórtan szerepelt.

### 2. Tényleges működés

A paklikifogyás több egymást követő lépésből áll.

### 3. Probléma

Nincs egy helyen röviden összefoglalva.

### 4. Javított szabály

Ha a játékos húzna, de a paklija üres:

1. az Ürességét új paklivá keveri
2. feláldoz 1 saját ép Pecsétet
3. a feláldozott Pecsét lapja az Ürességbe kerül
4. nem aktiválódik Burst / Surge
5. ha nincs feláldozható Pecsét, a játékos veszít

### 5. Megjegyzés

Ez jó lesz a végleges szabálykönyv rövid, technikai definíciójához.

---

## ÁLLAPOT

A paklikifogyás és Refresh Penalty rendszere jelenlegi alapszinten tisztázva:

* a paklikifogyás nem azonnali vereség
* újrakeverés történik
* ezért 1 saját Pecsétet kell feláldozni
* ez nem normál Pecsét-feltörés
* nem jár Bursttel vagy Surge-dzsel
* ha nincs feláldozható Pecsét, a játékos veszít

---

## KULCSSZAVAK – ÁLTALÁNOS ELV

### 1. Eredeti szabály

A kulcsszavak különleges képességeket adnak az Entitásoknak vagy más lapoknak.

### 2. Tényleges működés

A kulcsszavak az alap szabályok alóli kivételeket, módosításokat vagy kiegészítő viselkedéseket adják.

### 3. Probléma

A kulcsszavak több helyen eltérő részletességgel vannak leírva, és néhány régi definíció ellentmond az új szabályalapnak.

### 4. Javított szabály

A kulcsszavak rövid, szabványosított mechanikai definíciók.
Mindig az alapszabályhoz képest kell őket értelmezni.

### 5. Megjegyzés

A kulcsszavakat külön fogalmi rétegként kell kezelni, nem szabad őket szétszórtan, eltérő verziókban bent hagyni.

---

## GYORSASÁG (CELERITY)

### 1. Eredeti szabály

A frissen kijátszott Entitás azonnal támadhat.

### 2. Tényleges működés

Felülírja az idézési betegséget.

### 3. Probléma

Nincs, ez már tiszta.

### 4. Javított szabály

A Gyorsaság (Celerity) kulcsszóval rendelkező Entitás a kijátszása körében is indíthat támadást.

### 5. Megjegyzés

Csak az idézési betegség alól ad kivételt, más támadási feltételeket nem ír felül.

---

## OLTALOM (AEGIS)

### 1. Eredeti szabály

Az Oltalommal rendelkező Entitás kötelező célpont.

### 2. Tényleges működés

Aktív Horizont-entitásként célpontkényszert hoz létre.

### 3. Probléma

Régi szövegekben nem mindig volt tiszta, hogy globális vagy lokális hatás.

### 4. Javított szabály

Amíg egy Oltalommal (Aegis) rendelkező Entitás aktív állapotban van a Horizonton, az ellenfél támadással csak Oltalommal rendelkező célpontot választhat.

### 5. Megjegyzés

Ez felülírja az általános célpontválasztási szabályt.

---

## HASÍTÁS (SUNDERING)

### 1. Eredeti szabály

Többféle, egymásnak is ellentmondó változatban szerepelt.

### 2. Tényleges működés

A túlcsorduló harci sebzéshez kötött.

### 3. Probléma

Régi verziók extra Pecsét-törésként vagy közvetlen Pecsét-sebzésként kezelték.

### 4. Javított szabály

Ha egy Hasítás (Sundering) kulcsszóval rendelkező Entitás több harci sebzést okoz, mint amennyi a célpont Entitás HP-ja, a fennmaradó sebzés továbbvihető ugyanabban a feloldási láncban egy másik érvényes Entitásra. Ha ilyen nincs, akkor pontosan 1 Pecsét törik fel.

### 5. Megjegyzés

A Hasítás nem teszi a Pecsétet sebződő célponttá. A Pecsét itt sem sebzést kap, hanem külön következményként törik fel.

---

## HARMONIZÁLÁS (HARMONIZE)

### 1. Eredeti szabály

A Zenitben lévő Entitás támadóerőt ad az előtte álló Entitásnak.

### 2. Tényleges működés

A Zenit és a Horizont azonos pozíciója közötti támogatási kapcsolatot modellezi.

### 3. Probléma

Két eltérő változat is megjelent:

* fix ATK bónusz
* ATK felének átadása

### 4. Javított szabály

A Harmonizálás (Harmonize) egy Zenitből adott támogatási képesség, amely az előtte, vele azonos pozícióban álló Horizont-Entitásra hat.

### 5. Megjegyzés

A pontos mechanikai változatot még külön véglegesíteni kell, mert jelenleg több eltérő definíció is létezik a dokumentumokban.

---

## MÉTELY (BANE)

### 1. Eredeti szabály

A megsebzett célpont később elpusztul.

### 2. Tényleges működés

Ha a célpont túléli a harci sebzést, késleltetett pusztulás következik be.

### 3. Probléma

Pontosan meg kell mondani, hogy mikor ellenőrződik és mikor pusztul el a célpont.

### 4. Javított szabály

A Métely (Bane) kulcsszóval rendelkező Entitás által megsebzett célpont, ha túléli a harci sebzést, a meghatározott késleltetett időpontban elpusztul.

### 5. Megjegyzés

A pontos timingot még külön rögzíteni kell, de az alapelv az, hogy nem azonnali plusz sebzésről, hanem késleltetett megsemmisülésről van szó.

---

## LÉGIES (ETHEREAL)

### 1. Eredeti szabály

Különleges blokkolási vagy támadási kivételt hoz létre.

### 2. Tényleges működés

A fizikai interakciót korlátozza.

### 3. Probléma

A dokumentumokban a blokkolási korlátozás már szerepel, de pontosan el kell választani a fizikai támadást és a varázslati célzást.

### 4. Javított szabály

A Légies (Ethereal) kulcsszóval rendelkező Entitást fizikai támadással csak másik Légies Entitás képes szabályosan blokkolni vagy feltartóztatni, a varázslati és egyéb nem fizikai célzásra vonatkozó szabályok ettől külön értelmezendők.

### 5. Megjegyzés

A végleges megfogalmazásnál pontosan el kell dönteni, hogy a Légies a támadási, blokkolási vagy mindkét fizikai interakciót korlátozza-e.

---

## REZONANCIA (RESONANCE X)

### 1. Eredeti szabály

A Zenitben lévő Entitás extra Aurát termel.

### 2. Tényleges működés

Kiegészítő erőforrás-termelő kulcsszó.

### 3. Probléma

A skálázás és a pontos időzítés külön tisztázást igényelhet.

### 4. Javított szabály

A Rezonancia X (Resonance X) kulcsszóval rendelkező Entitás, miközben a meghatározott zónában van, a saját Ébredés fázisban X mennyiségű extra Aurát biztosít.

### 5. Megjegyzés

A végleges szabályszövegben a zóna- és időzítési feltételt pontosan hozzá kell kötni a kulcsszóhoz.

---

## KÉNYSZERÍTÉS (TAUNT)

### 1. Eredeti szabály

Az ellenfélnek legalább egy támadást kell indítania.

### 2. Tényleges működés

A passzív, teljes támadásmegtagadást korlátozó mechanika.

### 3. Probléma

Pontosan meg kell mondani, milyen feltétellel érvényesül: csak akkor, ha az ellenfél ténylegesen képes támadni.

### 4. Javított szabály

A Kényszerítés (Taunt) kulcsszóval létrehozott hatás arra kötelezi az ellenfelet, hogy a következő saját Betörés fázisában legalább 1 szabályosan támadásra képes Entitásával támadást indítson, amennyiben erre ténylegesen van érvényes lehetősége.

### 5. Megjegyzés

Ez nem írhatja felül a támadás szabályos feltételeit.

---

## RIADÓ (CLARION)

### 1. Eredeti szabály

Megjelenéskor aktiválódó hatás.

### 2. Tényleges működés

Belépési trigger.

### 3. Probléma

Nincs, de jó külön rögzíteni.

### 4. Javított szabály

A Riadó (Clarion) kulcsszó a lap Domíniumra kerülésekor azonnal létrejövő megjelenési hatást jelöl.

### 5. Megjegyzés

Ez triggermechanika, nem állandó passzív képesség.

---

## VISSZHANG (ECHO)

### 1. Eredeti szabály

Pusztuláskor aktiválódó hatás.

### 2. Tényleges működés

Haláltrigger.

### 3. Probléma

Pontosan el kell különíteni a normál pusztulástól és az Ürességbe kerüléstől.

### 4. Javított szabály

A Visszhang (Echo) kulcsszó azt jelzi, hogy a lap elpusztulásakor, illetve az Ürességbe kerüléséhez kapcsolódóan külön utóhatás aktiválódik.

### 5. Megjegyzés

A végleges szövegben meg kell mondani, hogy elpusztuláskor vagy Ürességbe kerüléskor számít-e a trigger.

---

## KULCSSZAVAK – NYITOTT PONTOK

Az alábbi kulcsszavak alapja ismert, de még nem teljesen végleges:

* Harmonizálás
* Métely
* Légies
* Rezonancia
* Visszhang pontos triggerfeltétele

---

## KULCSSZAVAK – STÁTUSZ

Jelenleg stabilnak tekinthető:

* Gyorsaság
* Oltalom
* Hasítás
* Kényszerítés
* Riadó

Részben tisztázott, további finomítást igényel:

* Harmonizálás
* Métely
* Légies
* Rezonancia
* Visszhang

---

## HARMONIZÁLÁS (HARMONIZE) – JAVASOLT VÉGLEGES MODELL

### 1. Kiinduló helyzet

A Harmonizálás jelenleg úgy szerepel, hogy a Zenitben meditáló Entitás ATK bónuszt ad a kizárólag előtte álló Entitásnak, és egy célponton egyszerre csak 1 Harmonizálás hatás lehet aktív.

Skálázás:

* Mag 1–4 → +2 ATK
* Mag 5–8 → +1 ATK
* Mag 9+ → nem rendelkezhet vele

Ez az alap jó, mert:

* illeszkedik a Zenit támogató szerepéhez
* egyszerűen érthető
* könnyen balanszolható

### 2. Probléma

Felmerült egy jobb, rugalmasabb irány is: a Harmonizálás ne csak nyers ATK bónuszt jelentsen, hanem később egyes lapokon speciális támogatást is adhasson.

A cél ezért nem az, hogy a jelenlegi rendszert lecseréljük, hanem hogy úgy bővítsük, hogy:

* a meglévő, egyszerű verzió megmaradjon
* később speciális lapokon egyedi támogatási hatások is megjelenhessenek
* a kulcsszó továbbra is konzisztens maradjon

### 3. Javasolt végleges irány

A Harmonizálás két rétegű rendszerként kerüljön rögzítésre.

#### 3.1 Alap Harmonizálás

A Zenitben lévő Harmonizáló Entitás ATK bónuszt ad a közvetlenül előtte, vele azonos pozícióban álló Horizont Entitásnak.

Skálázás:

* Mag 1–4 → +2 ATK
* Mag 5–8 → +1 ATK
* Mag 9+ → nem rendelkezhet vele

Korlát:

* egy célponton egyszerre csak 1 Harmonizálás hatás lehet aktív

#### 3.2 Kiterjesztett Harmonizálás

Egyes lapoknál a Harmonizálás az alap ATK bónuszon felül vagy helyett külön, a kártyaszövegben megadott támogatási hatást is adhat.

Példák lehetséges irányokra:

* az előtte álló Entitás Hasítás kulcsszót kap
* az előtte álló Entitás támadásakor további hatás aktiválódik
* az előtte álló Entitás blokkolási vagy célzási kivételt kap

Ebben a modellben:

* a kulcsszó alapjelentése továbbra is a Zenit → előtte álló Horizont támogatás
* az egyedi lapok ezt bővíthetik speciális hatással

### 4. Javasolt szabályszöveg

A Harmonizálás (Harmonize) olyan támogatási képesség, amely a Zenitben lévő Entitás és a közvetlenül előtte, vele azonos pozícióban álló Horizont Entitás között jön létre.

Alap esetben a Harmonizálás ATK bónuszt ad:

* Mag 1–4 esetén +2 ATK
* Mag 5–8 esetén +1 ATK
* Mag 9+ esetén a kártya nem rendelkezhet Harmonizálás kulcsszóval

Egy célponton egyszerre csak 1 Harmonizálás hatás lehet aktív.

Bizonyos kártyák a Harmonizálás alap hatását további, a kártyaszövegben meghatározott támogatási effekttel bővíthetik.

### 5. Kiegészítő pontosítások

* Ha nincs a Zenitben lévő Harmonizáló Entitás előtt Horizont Entitás, a Harmonizálás nem fejt ki hatást.
* A Harmonizálás csak addig aktív, amíg a Zenitbeli Entitás és az előtte álló Horizont Entitás pozíciós kapcsolata fennáll.
* Ha a célpont elpusztul, elmozdul vagy a kapcsolat megszűnik, a Harmonizálás hatása azonnal megszűnik.
* Az egyszerre csak 1 aktív Harmonizálás szabályt a végleges szabálykönyvben külön, egyértelműen rögzíteni kell.

---

## REZONANCIA (RESONANCE X) – RÖGZÍTETT VÁLTOZAT

### 1. Kiinduló helyzet

A Rezonancia X jelenleg úgy szerepel, hogy amíg az Entitás a Zenitben tartózkodik, minden saját Ébredés fázisban X mennyiségű extra Aurát ad.

Skálázás:

* Mag 1–4 → Rezonancia 2
* Mag 5–8 → Rezonancia 1

### 2. Értelmezés

Ez a mechanika már elég tiszta. Az X egy fix érték, amelyet a kártya tervezésekor kap meg a lap. A Magnitúdó szerinti skálázás meghatározza, hogy milyen erősségű Rezonancia kerülhet az adott lapra.

### 3. Javasolt végleges szabály

A Rezonancia X (Resonance X) azt jelenti, hogy az Entitás, amíg a Zenitben van, a saját Ébredés fázisban X mennyiségű extra Aurát biztosít.

Skálázás:

* Mag 1–4 → Rezonancia 2
* Mag 5–8 → Rezonancia 1
* Mag 9+ → nem rendelkezhet vele, ha ez a tervezési szabály így kerül véglegesítésre

### 4. Megjegyzés

A Rezonancia és a Harmonizálás jól elkülöníthető:

* Harmonizálás = közvetlen pozíciós támogatás a Horizontnak
* Rezonancia = erőforrás-termelés az Ébredés fázisban

---

## JELENLEGI ÁLLAPOT – RÖVID ÖSSZEFOGLALÓ

A kulcsszavak közül jelenleg stabilnak tekinthető vagy közel végleges:

* Gyorsaság
* Oltalom
* Hasítás
* Kényszerítés
* Riadó
* Rezonancia
* Visszhang
* Légies
* Métely

A Harmonizálás esetében most már van egy jól használható, véglegesíthető irány:

* marad az eredeti ATK-bónusz alap
* de megnyílik a lehetőség a kártyaszövegben meghatározott speciális támogatási hatásokra is

Ez a megoldás:

* illeszkedik az eddigi szabályokhoz
* nem dobja ki a korábbi rendszert
* és bővíthető marad a későbbi laptervezéshez

---
