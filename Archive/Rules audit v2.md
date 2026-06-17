# AETERNA – RULES AUDIT v2 (KONSZOLIDÁLT VÁLTOZAT)

Ez a dokumentum a jelenlegi auditfolyamat eredményeinek tisztított, egységesített összefoglalása.
Csak a véglegesített szabályértelmezések és a még nyitott kérdések szerepelnek benne; minden korábbi, felülírt vagy ellentmondásos verzió eltávolításra került.

---

## 1. A harc alapelvei

A játék harci rendszere szigorúan különválasztja egymástól a **sebzés** és a **Pecsét-feltörés** fogalmát.
Ez a különválasztás a rendszer egyik alapköve, és minden kapcsolódó szabály ebből következik.

A sebzés kizárólag Entitásokat érinthet. A sebzés mértéke az Entitás HP értékéből kerül levonásra, és ha a HP nullára vagy az alá csökken, az Entitás megsemmisül és az Ürességbe kerül.

A Pecsétek ezzel szemben nem rendelkeznek HP-val, ezért nem képesek sebzést elszenvedni. A Pecsét eltávolítása egy különálló játékművelet, amelyet **Pecsét-feltörésnek** nevezünk.

Pecsét kizárólag az alábbi módokon törhető fel:

* blokkolatlan fizikai támadás eredményeként,
* vagy olyan kártyahatás által, amely explicit módon „Pecsét feltörését” írja elő.

Fontos megkötés, hogy a „direkt sebzés” típusú hatások (például „okozz X sebzést”) semmilyen körülmények között nem alakíthatók át automatikusan Pecsét-feltöréssé.

---

## 2. A támadás szerkezete és célzási rendszere

Egy támadás során a játékos először kiválaszt egy támadó Entitást a Horizonton, majd egy érvényes célpontot. Egy támadás mindig egyetlen célpontra irányul.

A célpont kiválasztása nem az Áramlat kiválasztásán alapul, hanem közvetlen célpontválasztással történik. A támadó Entitás saját pozíciója ebből a szempontból irreleváns.

A célpontválasztás során a következő szabályrendszer érvényesül:

Amennyiben az ellenfél oldalán van olyan Entitás a Horizonton, amely rendelkezik **Oltalom (Aegis)** képességgel, úgy kizárólag ez az Entitás választható célpontként.

Ha nincs Oltalommal rendelkező Entitás, akkor a játékos bármely kimerült (elfordított) Horizonton lévő Entitást megtámadhatja.

Ha egy adott pozícióban nincs Horizont Entitás, akkor a mögötte lévő Zenit Entitás támadhatóvá válik.

Amennyiben sem a Horizonton, sem a Zeniten nincs Entitás az adott pozícióban, a támadás a Pecsét ellen irányulhat.

Az Aeternal (a játékos) csak abban az esetben válik támadhatóvá, ha az adott játékosnak már egyetlen Pecsétje sem maradt. Ilyenkor egy sikeres támadás azonnali vereséget jelent.

---

## 3. Az Áramlat szerepe

A játéktér oszlopai Áramlatokból állnak, amelyek három egymás mögötti részből épülnek fel: Horizont, Zenit és Pecsét.

Az Áramlat azonban nem korlátozza a támadás irányát. A támadó játékos nem Áramlatot választ, hanem konkrét célpontot. Az Áramlat szerepe kizárólag a védelem és a sebezhetőség meghatározása.

Ennek megfelelően:

* a támadó Entitás pozíciója nem határozza meg, hogy mit támadhat,
* a védekezés szempontjából viszont az Áramlat határozza meg, hogy egy Zenit Entitás mikor válik támadhatóvá.

Egy Zenit Entitás alaphelyzetben csak akkor sebezhető fizikai támadással, ha az előtte lévő Horizont mező üres.

---

## 4. Túlcsorduló sebzés – Hasítás

A Hasítás (Sundering) képesség a klasszikus „piercing” mechanika átdolgozott változata.

Amennyiben egy Hasítás képességgel rendelkező Entitás támadása során a kiosztott sebzés meghaladja a célpont HP értékét, a fennmaradó sebzés továbbszáll.

A fennmaradó sebzés először ugyanazon Áramlat másik Entitását érinti, amennyiben ilyen létezik. Ha nincs további Entitás az adott Áramlatban, akkor a hatás legfeljebb egyetlen Pecsét feltörését eredményezheti.

Fontos korlát, hogy ezen mechanika révén egyszerre legfeljebb egy Pecsét törhető fel.

---

## 5. Erőforrás és kimerítés

Az Aura a játék alapvető erőforrása, amelyet a játékosok kártyák kijátszására használnak. Az Aura felhasználása a kimerítés mechanikáján keresztül történik, amelyet a lap 90 fokos elfordítása jelez.

A visszaállítás során a lap visszaforgatásra kerül alaphelyzetbe.

A Birodalmak színei kizárólag vizuális megkülönböztetésre szolgálnak, és nem jelentenek mechanikai kötöttséget a fizetés szempontjából.

A varázslatok esetében azonban érvényes a Soft Penalty szabály: ha egy varázslat kifizetéséhez Aether (Semleges) Aurát is felhasznál a játékos, a varázslat teljes költsége 1 Aurával megnő.

---

## 6. Kulcsképességek

Az **Oltalom (Aegis)** biztosítja, hogy amíg ilyen képességgel rendelkező Entitás van a Horizonton, addig kizárólag az választható célpontként.

A **Légies (Aerial)** képesség kizárólag a fizikai harcot korlátozza: az ilyen Entitásokat csak más Légies Entitások támadhatják vagy blokkolhatják. Ez a korlátozás nem vonatkozik varázslatokra vagy egyéb hatásokra.

A **Métely (Blight)** olyan állapot, amely az Entitás késleltetett megsemmisülését okozza. A pontos időzítése még nem véglegesített: vagy az adott kör végén, vagy a következő kör elején történik megsemmisülés.

A **Harmonizálás (Harmonize)** a Zenitből biztosít támogatást az előtte lévő Horizont Entitásnak. Az alapváltozatban ez Magnitúdó-alapú ATK bónuszt jelent, és egy célponton egyszerre csak egy ilyen hatás lehet aktív. A mechanika később speciális képességekkel bővíthető.

A **Rezonancia (Resonance X)** a Zenitben aktív, és minden saját Ébredés fázisban extra Aurát biztosít.

A **Visszhang (Echo)** akkor aktiválódik, amikor a kártya az Ürességbe kerül, lehetővé téve, hogy erre az eseményre további hatások épüljenek.

A **Visszaállítás** képességből fakadó formája nem lehet szabadon választható: a kártyának egyértelműen meg kell határoznia, hogy Entitást vagy az Ősforrás egy lapját érinti.

---

## 7. Burst és reakciók

Amikor egy Pecsét feltörik, a kártya a játékos kezébe kerül. Ha a kártya rendelkezik Burst képességgel, a játékos dönthet úgy, hogy azonnal, költség nélkül aktiválja azt.

Ez a lehetőség kizárólag a Pecsét feltörésének pillanatában áll fenn. Ha a játékos nem él vele, a kártya a továbbiakban normál módon használható.

Ha több Pecsét törik fel egyszerre, azok hatásai külön kerülnek feldolgozásra, és a játékos dönt a feldolgozás sorrendjéről.

A **Jelek (Trap)** aktiválása feltételhez kötött. A játékos minden egyes feltétel teljesülésekor dönthet az aktiválásról, de ha a feltétel nem következik be újra, a hatás később már nem használható fel.

---

## 8. Refresh Penalty

Amennyiben egy játékosnak húznia kellene, de a paklija elfogyott, az Üresség tartalma újrakeverésre kerül. Ezt követően a játékos egy Pecsétet elveszít.

A rendszer jelenlegi formájában lehetőséget adhat végtelen ciklusokra bizonyos kombinációk esetén. Ennek kezelése egyelőre nem része a szabályrendszernek, és csak tesztelési tapasztalatok alapján kerül majd bevezetésre.

---

## 9. Nyitott kérdések

Az audit jelenlegi állapotában néhány mechanika még véglegesítésre vár.

A Métely pontos időzítése még nem eldöntött (kör vége vagy következő kör eleje).

Az Oltalom hatóköre jelenleg globális értelmezést kapott, de szükség esetén szűkíthető Áramlat-alapú működésre.

A Harmonizálás mechanika bővíthetőségének mélysége (pusztán statikus bónusz vagy komplexebb hatásrendszer) szintén további tervezési döntést igényel.

---

Ez a dokumentum a jelenlegi legstabilabb, ellentmondásmentes állapotot rögzíti, és közvetlenül alkalmas a teljes szabálykönyv újraírásának alapjául.
