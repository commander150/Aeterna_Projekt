Rendben, a milestone commitot ellenőriztem. A remote `main` új HEAD-je:

`d7e7e90bd38c2d5a426c37e6feeef7251e952b25`
`docs: close Reaction Priority v1 milestone`

A scope tiszta: csak a tervezett Reaction-milestone dokumentáció került fel, a v6.7/v1.10 elődök változatlan rename-ként kerültek archívumba. A v6.8 már hivatalosan a **Combat + Pecsét Foundation** szakaszt jelöli következő feladatnak.

El is kezdtem a hivatalos 1.4.3v forrás célzott Combat/Pecsét auditját. Az első fontos eredmény: **sokkal kevesebb tényleges játékszabályi döntés hiányzik, mint elsőre gondolnánk.** A harc nagy része már meglehetősen pontosan le van írva.

### Ami már eldöntött, ezt nem kell újraterveznünk

A támadó alaphelyzetben csak a Betörés fázisban támadhat; Aktív, Horizonton lévő Entitás kell, amelyet nem érint idézési betegség vagy támadási tiltás, és van szabályos célpontja. A támadó **a támadás deklarálásakor Kimerül**.

A célpontválasztás is elég részletes:

* **Oltalom elsőbbséget élvez**, és globális: ha van legalább egy Aktív Oltalom-Entitás a védekező Horizontján, fizikai támadásnál ezek közül kell választani. 
* Oltalom nélkül egy Kimerült Horizont-Entitás támadható.
* Aktív Horizont-Entitás normálisan nem támadható, kivéve például az Oltalmat vagy explicit szabályt.
* Zenit-Entitás akkor válik elérhetővé, ha **a saját Áramlatának Horizont-mezője üres**.
* Jel nem test, ezért önmagában nem védi fizikailag az Áramlatot.
* Pecsét csak akkor érhető el, ha az adott Áramlatban már nincs Entitás, amely a védelmi réteget fenntartaná.
* Aeternal kizárólag akkor célozható, ha **egy darab fennálló Pecsét sincs**.

A blokkolás szintén explicit: a védekező játékos saját **Aktív Horizont-Entitást** választ, az Kimerül, és az eredeti célpont helyett a blokkoló válik a harci célponttá. Alapesetben legfeljebb egy blokkoló van. Blokkolás után a támadó és blokkoló egyszerre okoz egymásnak ATK-nak megfelelő harci sebzést.

A Pecsét is tiszta: nincs HP-ja, csak `standing/broken` jellegű állapota; normál sikeres blokkolatlan támadás pontosan **1 Pecsétet** tör, ATK-tól függetlenül. A feltört Pecsét felfedődik, majd Surge-ként a tulajdonos kezébe kerül.

Az Aeternalnak sincs HP-rendszere: 0 Pecsét mellett egy sikeres fizikai támadás az Aeternal ellen **azonnali vereség**. Ez már a Core győzelmi feltétele. A current OQ is megerősíti, hogy az Aeternal nem damage/heal target, a Pecsét pedig nem HP-modell.

### A Reaction-integráció is nagyrészt adott

A főforrás két külön Combat ReactionWindowt nevez meg:

```text
attack declaration
→ ReactionWindow
```

és

```text
block declaration
→ ReactionWindow
→ combat damage
```

A hivatalos szöveg külön mondja, hogy reakciós ablak nyílhat a támadás kijelölése után, de feloldás előtt, illetve a blokkolás kijelölése után, de harci sebzés előtt.

Ez erősen arra mutat, hogy a production combat-flow alapja ez legyen:

```text
1. attack declaration
   - attacker
   - target
   - attacker Exhaust

2. ATTACK REACTION WINDOW

3. block opportunity

4. ha block:
   blocker declaration
   blocker Exhaust

5. BLOCK REACTION WINDOW

6. final revalidation

7. combat resolution
   - entity combat damage
   - vagy Seal break
   - vagy Aeternal victory

8. következmények / triggerek

9. stable state
```

Ez nagyon jól ráépíthető a most elkészült Reaction v1-re.

---

## Viszont találtam néhány valódi döntési pontot

Ezeket kell most megbeszélnünk, nem az egész harcrendszert újratervezni.

### 1. Az eredeti célpont blokkolhatja-e saját maga a támadást?

Ez főleg az **Aktív Oltalom-Entitásnál** érdekes.

A szabály szerint:

* Aktív Oltalom lehet támadás célpontja;
* bármely saját Aktív Horizont-Entitás lehet blokkoló;
* a blokkoló lesz az új harci célpont.

De nincs kimondva, hogy az eredeti támadási célpont **saját magát kijelölheti-e blokkolónak**.

Ez fontos, mert ha igen:

```text
Oltalom Entitás célpont
→ ugyanaz az Entitás blokkol
→ Kimerül
→ attacker ↔ Oltalom Entitás simultaneous combat damage
```

Ha nem, akkor egy megtámadott Aktív Oltalom-Entitás önmagában nem üt vissza; csak másik Entitás foghatja fel helyette a támadást.

**Én engedném, hogy az eredeti célpont saját maga blokkoljon**, ha egyébként szabályos blokkoló. Ez intuitívabb fizikai harcot ad, és értelmesebbé teszi az Aktív Oltalmat.

De ezt explicit emberi döntéssé tenném.

---

### 2. Pontosan mikor jön a blokkolási döntés?

A forrás alapján én ezt tartom a legerősebb értelmezésnek:

```text
attack declaration
→ attack ReactionWindow teljes lezárása
→ attack még érvényes?
→ block decision
→ block ReactionWindow
→ damage
```

Nem pedig:

```text
attack declaration
→ azonnal block
→ csak utána reaction
```

Az első modell szerint ha az első ReactionWindow már megszünteti vagy invalidálja a támadást, fölösleges blokkolási döntést sem kérünk.

**Ezt javaslom current defaultnak.**

---

### 3. Pecsét-identitás: ki láthatja a fennálló Pecsét lapját?

Ez valóban nincs eldöntve.

A főforrás annyit mond, hogy a pakli felső 6 lapját **képpel lefelé, érintetlenül** kell Pecsétként lehelyezni. Nem mondja ki, hogy a tulajdonos később megnézheti-e őket. Az OQ ezért helyesen tartja nyitva az „exact owner/opponent Seal identity visibility” kérdést.

Én a legegyszerűbb és fizikailag legtermészetesebb current defaultot javaslom:

> **A fennálló Pecsét identitása mindkét játékos előtt rejtett. A tulajdonosa sem nézheti meg, amíg szabály vagy hatás ezt kifejezetten nem engedi.**

Feltöréskor:

* public reveal;
* ezután Surge → owner hand.

Ez digitálisan is nagyon tiszta.

---

### 4. Gondviselés bekerüljön-e már az első Pecsét implementationbe?

Ez érdekesebb.

A Surge Core szerint a feltört Pecsét mindig kézbe kerül. Ha a lap Magnitúdója magasabb a játékos aktuális Magnitúdójánál, **Gondviselésként opcionálisan azonnal az Ősforrásba tehető**. 

Ha ezt kihagyjuk az első Combat/Pecsét slice-ból, nagyon sok normál Pecsét-feltörésnél máris unsupported helyzetbe kerülhetünk.

Ezért én most:

**Gondviselést BEVONNÁM az első Combat/Pecsét foundationbe.**

Burstöt viszont még nem. A Burst már kézből azonnali Ige-kijátszást és speciális Reaction-source lifecycle-t igényel, amit a Reaction v1 szándékosan nem implementált teljesen.

Tehát:

```text
Seal break
→ reveal
→ Surge to hand
→ ha Gondviselés eligible:
      owner choice:
      keep in hand
      OR move immediately to Wellspring
→ stable
```

Burst:

```text
explicit controlled unsupported / later slice
```

---

### 5. Az első Combat slice mely kulcsszavakat támogassa?

Szerintem:

**Kell most:**

* Gyorsaság – attacker eligibility része;
* Oltalom – target selection alapvető része;
* Légies – attack és block legality alapvető módosítója.

**Mehet későbbre:**

* Hasítás – külön excess-damage/Seal-break pipeline;
* Kényszerítés – külön forced-action rendszer;
* Jel-specifikus attack nullification;
* Burst;
* generic prevention/replacement.

Ez elég erős first slice lenne ahhoz, hogy már valódi AETERNA-harcot tudjunk tesztelni, de nem próbálnánk egyszerre minden harci kulcsszót megvalósítani.

---

## Tehát jelenleg 5 kérdésből áll a valódi döntési kapu

Én ezekre most ezt a defaultot javaslom:

1. **A célpont önmagát blokkolhatja:** igen, ha egyébként szabályos blokkoló.
2. **Combat sorrend:** Attack Declaration → Reaction → Block Decision → Block Declaration → Reaction → Resolution.
3. **Fennálló Pecsét identity:** mindkét játékos előtt rejtett feltörésig.
4. **Gondviselés:** legyen része az első Pecsét foundationnek.
5. **First-slice keywords:** Gyorsaság + Oltalom + Légies igen; Hasítás/Kényszerítés/Burst/Jel később.

Ha ez az öt irány alapvetően megfelel, akkor ebből már össze tudom állítani a **Combat + Pecsét Foundation v1 contract első draftját**. Nem kell hozzá újabb nagy kutatási kör, és még nem kell Codex sem.


--hát elég problémás dolog merült fel 
igy szerintem kicsit megállunk amig tisztázunk mindent 
haladunk sorban és egyszerre csak egy dologgal foglalkozunk
1. Az eredeti célpont blokkolhatja-e saját maga a támadást?
szerintem itt sok olyan probléma merült fel ami korábban nem lett megfelelően végiggondolva
itt két külön játék mechanikája találkozott és nem lett megfelelően átvezetve
az Oltalom a Hearthstone Taunt mechanikájából származik amit nem tudok ezzel kapcsolatban hogy mi történik ha van 2 vagy több olyan lény a mezőn ami rendelkezik ezzel a képességgel
a blokkolás pedig a Vanguard Intercept mechanikájából jött 
ezeket kéne alaposabban megvizsgálni először hogy ott van e válasz a kérdésre
nem tudom pontosan mire gondoltál, amugy én magam nem teljesen értem a kérdést mert ha van Oltalommal rendelkező entitás akkor azt kell támadni szerintem azt nincs értelme blokkolni hiszen pont az a lényege hogy az kapja be a támadást
szerintem blokkolni csak akkor van értelme ha konkrétan megakarsz védeni egy entitást a támadástól 
de ezt pontositani fogjuk amint lesz elég információ--

Igen, itt tényleg **nem egy apró edge case-ről van szó**, hanem arról, hogy két külön játékból átvett védelmi mechanika összecsúszott. Most csak ezt az egy kérdéskört néztem meg, és nem akarok még AETERNA-szabályt választani.

A legfontosabb eredmény: **az előző „az eredeti célpont blokkolhatja-e saját magát?” kérdésem rosszul volt megfogalmazva.** A két inspirációs játék alapján maga a kérdés sem ugyanabban a formában létezik.

### Hearthstone – Taunt / az Oltalom eredete

A Hearthstone Taunt tisztán **támadás előtti célpontkorlátozás**. Ha az ellenfélnek legalább egy Taunt minionja van, normál közvetlen támadással csak Taunt miniont lehet választani. Ha **több Taunt minion van**, a támadó **szabadon választ közülük**. Nem kötelező támadni, de amíg Taunt van, más karaktert nem lehet támadni. ([Hearthstone Wiki][1])

Tehát például:

```text
védő:
A = Taunt
B = Taunt
C = normál minion
Hero

támadó választhat:
A vagy B

nem választhat:
C vagy Hero
```

Ez pontosan megfelel annak, amit te ösztönösen mondtál.

És érdekes módon a jelenlegi AETERNA-főforrás **már ugyanezt mondja** az Oltalomról: amíg van legalább egy Aktív, Oltalommal rendelkező Horizont-Entitás, a támadó csak Oltalommal rendelkező Entitást választhat. Vagyis több Oltalom esetén nincs „első” Oltalom: az Oltalommal rendelkezők alkotják a szabályos célpontkört.

Ez tehát szerintem nem problémás rész. Az Oltalom Hearthstone-eredete jól át lett vezetve.

### Vanguard – Intercept / a blokkolás eredete

Itt viszont jött a fontos meglepetés.

A Vanguard **Interceptje nem úgy működik, ahogy a jelenlegi AETERNA-blokkolás**.

A jelenlegi hivatalos Vanguard rules-oldal a Comprehensive Rules 4.59-et jelöli aktuálisnak. ([CF Vanguard][2]) A hivatalos comprehensive rules és guide-ok Intercept-leírása szerint egy front-row rear-guard Intercepttel az ellenfél Guard Stepjében átmehet a **Guardian Circle-re**, amikor **egy másik saját unitot támadnak**. Az Interceptelő unit maga nem lehet az, amelyiket támadják. ([CF Vanguard][3])

Ez nagyon lényeges:

> **Vanguardban a megtámadott unit nem interceptálhatja saját magát.**

Sőt, még fontosabb:

> **az interceptor nem válik az új támadási célponttá.**

Hanem Guardian lesz, és a saját **Shield** értékével növeli a megtámadott unit védelmét. A Vanguard guide szerint kézből is lehet Guardianöket kijátszani, és Intercepttel a front rowból is lehet Guardian Circle-re mozgatni unitokat. ([CF Vanguard][4])

Vagyis nagyjából:

```text
Attacker → B-t támadja

A rendelkezik Intercepttel

A → Guardian Circle
B továbbra is a megtámadott unit
A Shield értéke segít B-nek túlélni
```

Nem:

```text
Attacker → B

A blokkol

Attacker → mostantól A
Attacker és A egymást sebzi
```

Az utóbbi **a jelenlegi AETERNA modellje**, nem a Vanguard Intercept.

### És itt találtuk meg a valódi problémát

Az AETERNA jelenlegi hivatalos szabálya kifejezetten azt mondja, hogy az Oltalom és blokkolás két külön művelet, és ha Oltalom-Entitás a támadás célpontja, később attól még lehet blokkolni.

Más részek pedig már egészen konkrétan rögzítik:

> blokkoláskor a blokkoló Entitás válik az új harci célponttá, az eredeti célpont nem szenved sebzést, a blokkoló Kimerül, és a támadóval egyszerre sebzik egymást.

Tehát a jelenlegi AETERNA-ban ez történt:

```text
Hearthstone Taunt
        ↓
     Oltalom
        +
Vanguard Intercept
        ↓
   blokkolás
        ↓
DE közben az Intercept jelentése megváltozott:

Guardian / shield
→
target replacement + combat
```

Ezért tűnik most furcsának.

### A te felvetésed különösen fontos

Azt mondtad, hogy ha egy Oltalom-Entitást már célpontként kell megtámadni, akkor:

> „azt nincs értelme blokkolni, hiszen pont az a lényege, hogy az kapja be a támadást”

A két eredeti játékot megnézve ennek **nagyon erős logikája van**.

Hearthstone-ban a Taunt célja pontosan az, hogy:

```text
Engem támadj a mögöttem levő értékes dolgok helyett.
```

Vanguardban az Intercept célja ezzel szemben:

```text
Egy másik megtámadott unit védelmére beavatkozom.
```

Tehát az eredeti két funkció nagyon szépen elkülönül:

| Mechanika           | Mikor?                    | Mit csinál?                             |
| ------------------- | ------------------------- | --------------------------------------- |
| **Taunt / Oltalom** | támadás kijelölésekor     | magára kényszeríti a támadás célpontját |
| **Intercept**       | már kijelölt támadás után | egy **másik** megtámadott unitot véd    |

Ez alapján az a helyzet, hogy:

```text
Oltalom-Entitást megtámadnak
→ valaki más megvédi helyette
```

**egyik eredeti rendszerből sem következik természetesen.**

Lehet belőle jó AETERNA-mechanika, de akkor ez már egy saját hibrid szabály, amit tudatosan kell választanunk, nem pedig úgy kezelni, mint az inspirációk automatikus következményét.

### Van még egy komoly eltérés

A Vanguard Interceptnél az Interceptor **nem feltétlenül Aktív/Stand**. A comprehensive rules szerint még Rest állapotú unit is Interceptelhet, ha egyébként megfelel a feltételeknek. ([CF Vanguard][3])

Az AETERNA viszont jelenleg:

```text
csak Aktív Horizont-Entitás blokkolhat
→ blokkoláskor Kimerül
```

Ez megint nem Vanguard Intercept, hanem saját AETERNA-s megoldás.

Nem mondom, hogy rossz. Csak azt, hogy **sokkal nagyobb mértékben eltértünk az eredeti Intercepttől, mint eddig gondoltuk**.

### Amit ebből most biztosnak tekintek

Most még semmit nem változtatnék a szabályokon.

Viszont az első kérdést szerintem le kell cserélnünk. Nem az a fő kérdés, hogy:

> „Az eredeti célpont blokkolhatja-e saját magát?”

A Vanguard erre eleve azt mondaná: **nem**, mert az Intercept definíció szerint egy másik megtámadott unit védelmére szolgál. ([CF Vanguard][3])

A valódi AETERNA-designkérdés inkább ez:

> **Mit akarunk, hogy a blokkolás alapvetően jelentsen az AETERNÁ-ban?**

De ezt még **nem kell megválaszolnunk**. A következő körben szerintem csak a Vanguard Interceptet bontsuk tovább teljesen: mit nyer vele a megtámadott egység, mi történik az interceptorral a harc végén, lehet-e több interceptort használni ugyanarra a támadásra, hogyan viszonyul a kézből történő Guardhoz, és pontosan milyen taktikai szerepet tölt be.

Utána már sokkal tisztábban meg tudjuk mondani, hogy ebből **mit akartunk eredetileg átvenni az AETERNÁ-ba**, és mi az, ami később véletlenül került hozzá.

[1]: https://hearthstone.wiki.gg/wiki/Taunt-generating?utm_source=chatgpt.com "Taunt - New Hearthstone Wiki"
[2]: https://en.cf-vanguard.com/howto/?utm_source=chatgpt.com "Rules/Q&A ｜ Cardfight!! Vanguard Trading Card Game | Official Website"
[3]: https://en.cf-vanguard.com/wordpress/wp-content/uploads/Cardfight-Vanguard-Comprehensive-Rules-4.45.pdf?utm_source=chatgpt.com "Vanguard Comprehensive Rules"
[4]: https://en.cf-vanguard.com/howto/pdf/Starters_Guide.pdf?utm_source=chatgpt.com "Attack the opposing vanguard with your unit in the front row! **Attack!!**"


--rendben van 
már igy is sokkal tisztább hogy összefolglaltad de folytassuk az elemzést--

Igen. Most csak a **Vanguard Interceptet** bontottam tovább, és ebből már elég tisztán látszik, hogy pontosan milyen mechanikát vettünk alapul — és hol tért el tőle később az AETERNA.

A jelenlegi hivatalos Vanguard rules oldalon a Comprehensive Rules **4.59** a legfrissebb, 2026. augusztus 28-i verzió. ([CF Vanguard][1]) Az Intercept alapjelentése a current official guide és FAQ alapján továbbra is stabil.

### Mit csinál valójában az Intercept?

Az Intercept **nem célpontcsere**.

A sorrend lényegében:

```text
ellenfél támad egy saját unitot
→ a célpont már ki van jelölve
→ Guard Step
→ egy másik front-row rear-guard Interceptelhet
→ átkerül a Guardian Circle-re
→ a Shield értékével növeli az eredeti célpont védelmét
→ az eredeti célpont marad a megtámadott unit
```

A current First Guide ezt kifejezetten úgy írja le, hogy a Guardian Circle-re tett lapok Shield értéke hozzáadódik **a megtámadott unit Power értékéhez**. Intercept esetén a front-row rear-guard innen kerül Guardian Circle-re. ([CF Vanguard][2])

Ez az első nagy különbség az AETERNÁ-hoz képest.

Az Interceptor tehát nem azt mondja, hogy:

```text
"inkább engem üss"
```

hanem:

```text
"segítek neked kivédeni ezt a támadást"
```

---

### A megtámadott unit nem Interceptelhet

Ez egyértelmű official szabály.

A current guide konkrétan kimondja, hogy az Intercepttel rendelkező unit guardolhat úgy, hogy a front rowból Guardian Circle-re mozog, **de az a unit, amelyet éppen támadnak, nem Interceptelhet**. ([CF Vanguard][2])

Ez nem egy technikai kivétel, hanem a mechanika logikájából következik:

```text
attacked unit = akit védenek
interceptor = aki védi
```

A kettő két külön szerep.

Ezért az előző „blokkolhatja-e saját magát?” kérdés tényleg nem jó Vanguard-szemszögből.

---

### Az Interceptor akár Rest állapotban is lehet

Ez különösen érdekes az AETERNA szempontjából.

A Vanguard official FAQ szerint egy **Rest** unit is Interceptelhet. ([CF Vanguard][3])

Tehát az Intercept nem:

```text
Stand
→ Intercept
→ Rest
```

hanem az állapotától függetlenül használható, ha egyébként jogosult.

Ez azért fontos, mert a Vanguardban az Intercept valójában **nem egy újabb akció elköltése**. Inkább a lap pozícióját és saját testét áldozod fel védekezésre.

Ezzel szemben az AETERNA current blokkolás:

```text
Aktív Horizont-Entitás
→ blokkol
→ Kimerül
```

Ez teljesen más erőforrásmodell.

---

### Az Interceptor a harc végén elveszik

Az Intercept nem ingyenes védelem.

Miután a unit Guardian Circle-re ment, a harc végén a guardianok onnan eltávoznak. Az official FAQ külön megerősíti, hogy az Interceptelt unit a battle után retire-ol. ([CF Vanguard][3]) A comprehensive rules történetileg is ugyanazt a lifecycle-t mutatja: a battle végén a guardianok lekerülnek a Guardian Circle-ről. ([CF Vanguard][4])

Vagyis taktikai értelemben:

```text
van egy Entitásom a mezőn
→ feláldozom mint Interceptort
→ cserébe nagyobb eséllyel megmentem a fontosabb célpontot
```

Ez sokkal inkább **önfeláldozó testőr**, mint klasszikus blokkoló.

---

### Egynél több Interceptor is használható ugyanarra a támadásra

Ez is érdekes.

A current official Q&A szerint egy battle során akár **kettő vagy több lap is Interceptelhet egyszerre**. ([CF Vanguard][5])

És kombinálható:

* kézből kijátszott Guardianökkel;
* Interceptorokkal;
* más guard-mechanikákkal, a saját timingjuk szerint.

Az official FAQ már korábban is rögzítette, hogy Intercept mellett további Guardiant lehet kézből használni. ([CF Vanguard][3])

Tehát például:

```text
B-t támadják.

A interceptel: +5000 Shield
C interceptel: +10000 Shield
D kézből Guardian: +15000 Shield

B továbbra is a támadott unit.
Összesen +30000 defense.
```

Ez már messze van az AETERNA:

```text
egy blokkoló
→ új célpont
→ támadó és blokkoló sebzi egymást
```

modelljétől.

---

## Mire jó taktikailag az Intercept?

Szerintem ezt érdemes külön megérteni, mert valószínűleg **ez volt az a gondolat**, amit eredetileg át akartunk venni.

Az Interceptor lényegében átváltja:

```text
jövőbeli mezőérték
```

erőforrását

```text
azonnali védelemre
```

Például van két egységed:

```text
A = fontos támadó / kombóelem
B = kevésbé fontos Interceptor
```

Az ellenfél megtámadja A-t.

Ahelyett, hogy A-t elveszítenéd:

```text
B-t feláldozod Guardiannek
→ A defense nő
→ ha a támadás már nem ér elég Power-t, A megmarad
→ B viszont távozik
```

Tehát a döntés:

> „Melyik egységem értékesebb nekem hosszú távon?”

Ez nagyon jó taktikai mechanika.

---

# És most jön a legfontosabb AETERNA-kapcsolat

Ha egymás mellé tesszük a három modellt:

### Hearthstone Taunt / Oltalom

```text
támadás ELŐTT
→ korlátozza, kit választhatsz célpontnak
```

### Vanguard Intercept

```text
támadás UTÁN
→ nem módosítja a célpontot
→ másik unit erőforrását feláldozva segít megvédeni
```

### Jelenlegi AETERNA-blokkolás

```text
támadás UTÁN
→ lecseréli a célpontot
→ a blokkoló maga harcol a támadóval
```

Vagyis az AETERNA jelenlegi blokkolása **valójában egyik sem**.

Ez már egy harmadik mechanika.

És ezzel jutunk el ahhoz a problémához, amit te az Oltalomnál éreztél.

---

## Mi történik jelenleg Oltalom + AETERNA-blokkolás esetén?

Tegyük fel:

```text
A = Aktív Oltalom
B = normál Aktív Horizont-Entitás
C = fontos Kimerült Entitás
```

Az Oltalom miatt a támadó csak A-t támadhatja.

Ez eddig teljesen Taunt:

```text
Attacker
→ A
```

De ha utána B blokkolhatja ezt:

```text
Attacker
→ A

B blokkol

Attacker
→ B
```

akkor a harc ténylegesen **nem A-val történik**, hanem B-vel.

Vagyis az Oltalom mechanikai jelentése megváltozik:

```text
nem:
"nekem kell elviselnem a támadást"

hanem:
"engem kell elsőként célpontként kijelölni"
```

Ez egy sokkal gyengébb és más jelentés.

És még furcsább több Oltalomnál.

```text
A = Oltalom
B = Oltalom
C = normál Aktív Entitás
```

A támadó szabályosan A-t választja.

Utána C blokkol:

```text
final combat:
Attacker ↔ C
```

Tehát egy **nem Oltalommal rendelkező Entitás** lesz a tényleges harci célpont, annak ellenére, hogy az Oltalom szabály eredetileg kizárta őt a támadható célpontok közül.

Ez szerintem pontosan az a pont, ahol a két eredeti mechanika **összeütközik**.

---

# Vanguardban ez a konfliktus azért nem létezik

Mert ott az Intercept nem cseréli le a célpontot.

Ha képzeletben lenne egy Taunt-szerű Vanguard szabály:

```text
Attacker → Taunt A
```

és B Interceptelne:

```text
Attacker → továbbra is A
B csak védelmet ad A-nak
```

Tehát:

* Taunt megőrzi a funkcióját;
* Intercept is megőrzi a funkcióját;
* nincs mechanikai ellentmondás.

Ez nagyon fontos felismerés.

---

## Van még egy bizonyító edge case a Vanguardból

Az official FAQ-ban szerepel olyan támadás, amely egyszerre az egész front rowt támadja.

Ebben az esetben a front row egységei **nem tudnak Interceptelni**, mert mindegyikük maga is attacked unit. ([CF Vanguard][6])

Ez megint megmutatja, mennyire erősen különválasztja a rendszer:

```text
attacked unit
≠
interceptor
```

Az Intercept lényege ténylegesen a **másik unit védelme**.

---

# Amit ebből most még nem döntésként, hanem következtetésként levonhatunk

Szerintem most három dolgot már biztosan tudunk.

**1. Az Oltalom mechanikája önmagában koherens.**
A probléma nem ott kezdődik.

**2. Az AETERNA blokkolás jelenlegi változata nem valódi Vanguard Intercept.**
Inspirációja lehetett az, de mára teljesen más mechanikává vált.

**3. Az Oltalom és a jelenlegi célpontcserés blokkolás között valódi szemantikai konfliktus van.**

Nem feltétlenül jelenti azt, hogy valamelyiket el kell dobni.

De explicit dönteni kell majd arról, hogy:

```text
Oltalom csak target-declaration restriction?
```

vagy:

```text
Oltalom ténylegesen azt jelenti,
hogy ennek az Entitásnak kell viselnie a támadás következményét?
```

Ez két külön design.

### Amit a következő körben vizsgálnék

Még mindig **nem választanék megoldást**.

A következő egyetlen kérdés szerintem az legyen:

> **Milyen védelmi funkciót szeretnénk egyáltalán a blokkolástól az AETERNÁ-ban?**

Ehhez érdemes összehasonlítani három konkrét modellt:

* Vanguard-féle **Guardian/Intercept**;
* Magic-féle klasszikus **combat blocking**;
* a jelenlegi AETERNA **target replacement + simultaneous combat** modellje.

Nem azért, hogy valamelyiket egyszerűen lemásoljuk, hanem hogy pontosan lássuk, **melyik milyen taktikai döntést teremt**, és ebből melyik illik az AETERNA Horizont/Zenit/Oltalom rendszeréhez.

Szerintem innen érdemes folytatnunk, továbbra is csak ezen az egy kérdésen belül.

[1]: https://en.cf-vanguard.com/howto/?utm_source=chatgpt.com "Rules/Q&A ｜ Cardfight!! Vanguard Trading Card Game | Official Website"
[2]: https://en.cf-vanguard.com/wordpress/wp-content/uploads/vg_first_guide_v1.6.pdf?utm_source=chatgpt.com "4 Guard (Performed by your Opponent)"
[3]: https://en.cf-vanguard.com/howto/question/?id=basic&utm_source=chatgpt.com "Frequently Asked Questions ｜ ｜ Q&A ｜ Cardfight!! Vanguard Trading Card Game | Official Website"
[4]: https://en.cf-vanguard.com/wordpress/wp-content/uploads/Cardfight-Vanguard-Comprehensive-Rules-2.3.pdf?utm_source=chatgpt.com "7.5.1.2.4.1. Automatic abilities with the timing “when unit intercepts” become stand by when that unit is chosen to perform an intercept, but if that unit does not move to the guardian circle for any reason, the stand by state is cancelled."
[5]: https://en.cf-vanguard.com/cardlist/?cardno=DZ-BT03%2F043EN&utm_source=chatgpt.com "Protection: Twincast ｜ Card List ｜ Cardfight!! Vanguard Trading Card Game | Official Website"
[6]: https://en.cf-vanguard.com/howto/question/?id=rule&utm_source=chatgpt.com "Frequently Asked Questions ｜ ｜ Q&A ｜ Cardfight!! Vanguard Trading Card Game | Official Website"


--ezt nem tudom én sem hogy mi lenne a legjobb megoldás
még egy kitétel ami fontos lehet abban hogy megfelelően eszközöljük a változtatást
eddig nem vettük figyelembe a teljes játékmezőt mi van akkor ha a célpont egy olyan Entitás ami a Zenitben van? esetleg ha már a Pecsétet támadnák? szerintem akkor van igazán lehetősége a Blokkolásnak 
vizsgáljuk meg mindent amit mondtál hogy legyen pontosabb ősszehasonlítási alapunk 
ez nem végleges döntés de szerintem mehetünk kicsit a Vanguard-féle **Guardian/Intercept** irányába--

Igen, ezzel az új szemponttal szerintem sokkal jobban látszik, **miért éppen a Zenit és a Pecsét környékén lehet igazán értelme a blokkolásnak**. És az is látszik, hogy nem érdemes egyszerűen „Vanguard Interceptre cserélni” a jelenlegi szabályt: inkább annak funkcióját érdemes átvenni, miközben az AETERNA saját ATK/HP- és Áramlat-rendszerét megtartjuk.

Most még semmit nem tekintenék döntésnek.

## 1. Először a teljes AETERNA-játéktérből induljunk ki

A jelenlegi Core szerint a hat Áramlat mindegyike ilyen védelmi láncot alkot:

```text
Horizont
   ↓
Zenit
   ↓
Pecsét
```

A Zenit-Entitás akkor válik normál fizikai támadás célpontjává, ha a saját Áramlatának Horizont-mezője üres. Ha az Áramlatban már nincs olyan Entitás, amely a támadást felfogná vagy szabályos célpont lenne, a Pecsét válhat elérhetővé.

Ez nagyon fontos következménnyel jár:

**pont akkor, amikor egy Zenit-Entitást vagy Pecsétet már közvetlenül megtámadhatnak, az adott Áramlat Horizontja jellemzően üres.**

Vagyis ha azt mondanánk:

> „csak az ugyanabban az Áramlatban álló Horizont-Entitás blokkolhat”,

akkor a blokkolás **pont a Zenit és a Pecsét védelménél gyakorlatilag használhatatlanná válna**.

Ez szerintem már most kizár egy lehetséges modellt.

---

## 2. A jelenlegi AETERNA-blokkolás problémája nagyobb, mint az Oltalom

A jelenlegi szabály szerint egy saját Aktív Horizont-Entitás kijelölhető blokkolónak, Kimerül, majd **ő válik az új harci célponttá**, és a támadóval kölcsönösen sebzik egymást. Alapesetben egy blokkoló lehet. 

Ez önmagában működőképes.

A probléma akkor jelenik meg, amikor hozzáadjuk az Áramlatokat.

A Hasítás jelenlegi szabálya konkrétan azt mondja, hogy ha blokkolás történt, **a blokkoló Áramlata lesz az új harci kiindulópont**, nem az eredeti célpont Áramlata.

Ez például ilyen furcsa helyzethez vezethet:

```text
Támadás eredeti célja:
Áramlat 2 Pecsétje

Áramlat 5 egyik Horizont-Entitása blokkol

jelenlegi rendszer:
→ blokkoló lesz az új célpont
→ harc az Áramlat 5-ben
→ Hasítás is az Áramlat 5 irányában folytatódik
```

Tehát egy **2. Áramlat Pecsétje ellen indított támadásból végül az 5. Áramlat védelmi lánca válhat relevánssá**.

Ez már nem csak Oltalom-probléma. Ez a hat Áramlat pozíciós jelentését is összekeverheti.

És itt szerintem nagyon értékes volt a felvetésed a teljes játéktérről.

---

# 3. Vanguard Guardian / Intercept

A jelenlegi Vanguard hivatalos szabályoldalán a Comprehensive Rules 4.59 az aktuális szabályzat. ([en.cf-vanguard.com][1])

Az Intercept lényegi modellje:

```text
támadó
   ↓
eredeti megtámadott unit

másik front-row unit
   ↓ Intercept
Guardian Circle
   ↓
védelmet ad az EREDETI célpontnak
```

Az eredeti célpont **nem változik meg**.

Az official beginner guide kifejezetten leírja, hogy az Interceptelő front-row rear-guard a Guardian Circle-re kerül, Shield értékével növeli a megtámadott unit védelmét, és maga a megtámadott unit nem Interceptelhet. ([en.cf-vanguard.com][2])

Ráadásul több Interceptor is használható ugyanabban a harcban. ([en.cf-vanguard.com][3])

### Ami ebből nagyon jó AETERNÁ-hoz

A két szerep tisztán különválik:

```text
AttackTarget
≠
Guardian
```

Ez megoldja az előző problémánkat.

Ha a Zenitben levő Mágust támadják:

```text
eredeti célpont = Zenit Mágus
védő = másik Horizont-Entitás
```

a Mágus **végig az eredeti támadás célpontja marad**.

Ugyanez működhet Pecsét esetén:

```text
eredeti célpont = 4. Pecsét
védő = Horizont-Entitás
```

A Pecsét támadása továbbra is **a 4. Pecsét elleni támadás**, csak közben valaki megvédi.

Ez pozíciós szempontból nagyon tiszta.

### Ami viszont nem vihető át egy az egyben

Vanguardban a Guardian **Shieldet ad**.

AETERNA-ban nincs Shield statunk.

Nálunk:

```text
ATK
HP
sebzés
```

van.

A Pecsétnek pedig egyáltalán nincs HP-ja. A főforrás ezt explicit rögzíti. 

Tehát egy teljes Vanguard-klónhoz valami új védekezési számértéket kellene létrehozni.

Ezt én nem tartom vonzónak.

---

# 4. Magic-féle blokkolás

Itt jön egy érdekes felismerés.

A Magic mechanikailag sokkal közelebb áll ahhoz, **amit az AETERNÁ-nak valószínűleg szüksége van**, mint elsőre gondoltam.

Magicben a támadás célpontja lehet játékos, planeswalker vagy battle. Ettől függetlenül a védekező játékos Entitás-szerű permanenseket, creature-öket rendelhet blockernek az őket támadó creature-höz. ([Wizards Media][4])

Ha a támadó blokkolt:

```text
eredeti támadott objektum megmarad

DE

a támadó combat damage-e
→ blockerre megy

blocker damage-e
→ támadóra megy
```

A jelenlegi Comprehensive Rules ezt nagyon egyértelműen rögzíti: az unblocked attacker az eredeti támadott player/planeswalker/battle objektumnak okoz sebzést; a blocked attacker viszont a blokkoló creature-öknek. A combat damage egyszerre történik. ([Wizards Media][4])

Ez egy kulcsfontosságú köztes megoldás.

---

# 5. A három modell közvetlen összehasonlítása

|                                     | Vanguard               | Magic          | jelenlegi AETERNA                    |
| ----------------------------------- | ---------------------- | -------------- | ------------------------------------ |
| eredeti célpont megmarad?           | **igen**               | **igen**       | **nem**                              |
| másik egység közbelép?              | igen                   | igen           | igen                                 |
| védő harcol a támadóval?            | nem közvetlen ATK-harc | **igen**       | **igen**                             |
| védő védi a célpontot?              | Shielddel              | saját testével | célpontcserével                      |
| több védő?                          | igen                   | igen           | nem                                  |
| külön defense stat kell?            | igen                   | nem            | nem                                  |
| jól működik nem-Entitás célpontnál? | adaptálni kell         | **igen**       | működik, de targetcsere miatt furcsa |
| eredeti pozíció jelentése megmarad? | igen                   | **igen**       | problémás                            |

És ebből nekem egy elég érdekes irány kezd kirajzolódni.

Nem tiszta Vanguard.

Nem tiszta Magic.

Hanem:

> **Vanguard-féle Guardian/Intercept szerep + Magic-szerű fizikai harci feloldás.**

---

# 6. Mit jelentene ez AETERNÁ-ban?

Csak gondolatkísérletként:

```text
Támadó deklarálja:
Attacker A
→ eredeti célpont X
```

Az `X` **nem változhat meg pusztán azért, mert blokkolás történik**.

Utána:

```text
védő játékos kijelöl B Entitást védőnek
```

B Kimerül.

De nem lesz „az új támadási célpont”.

Ehelyett:

```text
OriginalAttackTarget = X
Guardian = B
```

Majd harcnál:

```text
A ↔ B
simultaneous combat damage
```

Ha B szabályosan megvédte X-et:

```text
X nem kapja meg
a normál támadás következményét
```

Ez olyan, mintha B **a támadás útjába állna**.

Ez mechanikailag sokkal közelebb áll az általad mondott intuícióhoz.

---

# 7. Horizont célpont

Itt valóban van némi átfedés az Oltalommal.

Például:

```text
H1 = értékes Kimerült Horizont Entitás
H2 = Aktív Horizont Entitás
```

Az ellenfél megtámadja H1-et.

H2 közbeléphetne:

```text
Attacker → eredetileg H1
H2 védi
Attacker ↔ H2
H1 túléli
```

Ennek van taktikai értelme.

Azt mondja:

> „inkább ezt az Entitásomat teszem kockára, hogy megmentsem a fontosabbat.”

Ez nagyon Vanguard-szerű döntés.

---

# 8. Oltalom célpont

Itt viszont továbbra is van egy külön problémánk.

```text
H1 = Oltalom
H2 = normál Entitás
```

Az Oltalom miatt a támadónak H1-et kell választania.

Ha utána H2 közbeléphet:

```text
Oltalom:
"engem kell megtámadnod"

de utána:
H2 viseli a harcot
```

Ez továbbra is furcsa.

Viszont ez most már egy **nagyon pontosan izolált kérdés**:

> egy Oltalommal rendelkező eredeti célpont védhető-e Guardian/Intercepttel?

Nem kell hozzá az egész blokkolásrendszert újragondolni.

Ezt később külön megoldhatjuk.

---

# 9. Zenit célpont — itt válik igazán értékessé

Pont ezt érezted meg.

Tegyük fel:

```text
Áramlat 3

Horizont: üres
Zenit: értékes Mágus
Pecsét: fennáll
```

Az ellenfél ezért már megtámadhatja a Zenit Mágust. 

De egy másik Áramlatban van egy Aktív Harcosod:

```text
Áramlat 1:
Horizont = Harcos
```

Egy Guardian-szerű rendszerben:

```text
Attacker → Zenit Mágus

Harcos közbelép

Attacker ↔ Harcos

Zenit Mágus megmenekül
```

Ez szerintem **nagyon értelmes taktikai funkció**.

A játékos választása:

> „Feláldozom / kockára teszem a frontvonal egyik testét azért, hogy megvédjem a hátsó sorban levő kulcsegységet.”

Ez sokkal természetesebb, mint az, hogy a Harcos egyszerűen **új támadási célponttá válik**, és ezzel még az Áramlat-identitás is áthelyeződik.

---

# 10. Pecsét — szerintem itt a legerősebb

Példa:

```text
Áramlat 4

Horizont: üres
Zenit: üres
Pecsét: fennáll
```

A Pecsét szabályosan támadható. Egy blokkolatlan sikeres támadás pontosan egy Pecsétet törne fel. 

Másik Áramlatban:

```text
Aktív Horizont-Entitás B
```

Ha B közbelép:

```text
OriginalTarget = Pecsét 4
Guardian = B

Attacker ↔ B
```

és ha a védelem sikeresen létrejött:

```text
Pecsét 4 nem törik fel
```

Ez szerintem nagyon erős **tematikai és taktikai** működés.

Azt mondja:

> „A védelmi vonalam ezen a ponton már áttört, de egy másik frontvonalbeli egységem még utolsó pillanatban közbeléphet a Pecsétért.”

Ez tényleg „Guard / Intercept”.

És közben az eredeti célpont:

```text
Pecsét 4
```

marad.

Nem változik át:

```text
Pecsét 4
→ Entitás az Áramlat 1-ben
```

---

# 11. Ez a Hasítást is sokkal tisztábbá teheti

Jelenleg a blokkoló Áramlata veszi át a Hasítás útját. 

Guardian-jellegű rendszerben viszont logikusabb lenne:

```text
OriginalTarget = Pecsét 4
Guardian = Entitás Áramlat 1

Attacker Hasításos
→ megsemmisíti Guardiant
→ marad excess damage
```

A Hasítás **nem az Áramlat 1 felé menne tovább**.

Hanem az eredeti támadás vonalán:

```text
→ Pecsét 4
```

vagyis:

```text
Original attack path
nem változik.
```

Ez lényegében a Magic `trample` logikájához hasonló, de az AETERNA saját Pecsét/Hasítás szabályával.

Szerintem ez sokkal könnyebben érthető.

---

# 12. Légies is szépen ráilleszthető

A jelenlegi szabály szerint Légies támadót csak Légies Entitás blokkolhat.

Ez változtatás nélkül átvihető:

```text
Légies Attacker
→ csak Légies Guardian/Interceptor állhat elé
```

Ha tehát egy Légies támadó Pecsétet támad:

```text
normál Horizont-Entitás:
nem tud közbelépni

Légies Horizont-Entitás:
közbeléphet
```

Ez még stratégiai értéket is ad a Légies védekezésnek.

---

# 13. A legnagyobb új kérdés: honnan lehessen közbelépni?

És szerintem **ez legyen a következő egyetlen kérdésünk**, mert a teljes rendszer ezen áll vagy bukik.

Négy alapmodell képzelhető el:

| modell                           | eredmény                                                          |
| -------------------------------- | ----------------------------------------------------------------- |
| csak azonos Áramlat              | Zenit/Pecsét ellen szinte használhatatlan                         |
| bármely Áramlat                  | erős taktikai szabadság, de gyengítheti az Áramlatok jelentőségét |
| szomszédos Áramlatok             | erős pozíciós rendszer, de összetettebb                           |
| csak külön erre jogosult Entitás | Vanguard-szerű Intercept képesség, de komoly card-design változás |

Az **azonos Áramlatot én az elemzés alapján már nem tartom jó iránynak**, mert strukturálisan pont akkor nincs ott Horizont-Entitás, amikor Zenitet vagy Pecsétet már támadni lehet.

A másik három viszont mind életképes.

---

## Ami most nekem a legerősebb munkahipotézis

Nem döntésként, csak további vizsgálati alapként:

```text
1. Az eredeti támadási célpont immutable marad.

2. Blokkolás helyett funkcionálisan Guardian / Intercept történik.

3. Egy jogosult Horizont-Entitás
   közbeléphet az eredeti célpont védelmére.

4. A közbelépő Kimerül.

5. A támadó és a közbelépő
   AETERNA-módra kölcsönösen harci sebzést okoz.

6. Az eredeti célpont nem kapja meg
   a normál támadás következményét.

7. Hasítás esetén az eredeti támadási útvonal marad authority,
   nem a közbelépő Entitás Áramlata.
```

Ez gyakorlatilag:

**Vanguard szerepkör + Magic blokkolási struktúra + AETERNA ATK/HP/Hasítás.**

És szerintem különösen a **Zenit és a Pecsét** miatt ez jelenleg sokkal ígéretesebbnek tűnik, mint a mostani target-replacement modell.

De még nem fagyasztanám le.

A következő körben szerintem kizárólag ezt az egy kérdést vizsgáljuk:

> **Mely Horizont-Entitások kaphassanak jogot arra, hogy egy másik célpont védelmére közbelépjenek: bármelyik, csak közeli Áramlatból, vagy csak külön Intercept/Guardian-jogosultsággal rendelkezők?**

Ez már közvetlenül meghatározza, hogy az AETERNA hat Áramlata megőrzi-e a stratégiai jelentőségét, vagy a teljes Horizont egy közös globális védővonallá válik.

[1]: https://en.cf-vanguard.com/howto/?utm_source=chatgpt.com "Rules/Q&A ｜ Cardfight!! Vanguard Trading Card Game | Official Website"
[2]: https://en.cf-vanguard.com/wordpress/wp-content/uploads/vg_first_guide_v1.6.pdf?utm_source=chatgpt.com "4 Guard (Performed by your Opponent)"
[3]: https://en.cf-vanguard.com/cardlist/?cardno=DZ-BT03%2F043EN&utm_source=chatgpt.com "Protection: Twincast ｜ Card List ｜ Cardfight!! Vanguard Trading Card Game | Official Website"
[4]: https://media.wizards.com/2026/downloads/MagicCompRules%2020260619.pdf?utm_source=chatgpt.com "Magic: The Gathering Comprehensive Rules"


--rendben van folyatassuk az elemzést
jelzem hogy jelenleg amig tervezünk nem számit de ha van végleges irány nem vesszük át a "Intercept/Guardian" nevek egyikét sem--

Igen, ezt külön rögzítem: az **„Intercept” és „Guardian” most csak összehasonlító munkakifejezések**. Ha az AETERNA-ban véglegesítünk egy hasonló funkciót, saját nevet kap.

Most kizárólag azt vizsgáltam tovább, hogy **mely Horizont-Entitások avatkozhassanak közbe egy másik célpont védelmében**.

### Először egy fontos AETERNA-tény

A jelenlegi főforrás szerint az Áramlat elsősorban **védelmi és célpontelérési szerkezet**, nem a támadó saját sávja. A támadó konkrét célpontot választ, nem „Áramlatot támad”. Ugyanakkor minden Horizont-Entitás passzívan **a saját Áramlatának** Zenitjét és Pecsétjét védi.  

A blokkolási jogosultságnál viszont a jelenlegi forrás csak azt mondja, hogy az Entitás legyen Aktív, Horizonton álljon, és más szabály ne tiltsa. Nem találtam benne olyan általános kikötést, hogy **azonos vagy szomszédos Áramlatban** kellene lennie. 

Vagyis a jelenlegi szabály ténylegesen közel áll ehhez:

```text
bármely saját Aktív Horizont-Entitás
→ közbeléphet
```

Ez fontos, mert ha változtatunk, akkor nem egy eddig definiálatlan részletet töltünk ki, hanem a meglévő globális blokkolást alakítjuk át.

## Mit csinálnak a mintául szolgáló rendszerek?

| Modell                        | Ki védekezhet?                                    | Pozíciós korlát                           | Külön képesség kell? |
| ----------------------------- | ------------------------------------------------- | ----------------------------------------- | -------------------- |
| **Magic**                     | gyakorlatilag bármely jogosult, untapped creature | nincs sáv-/távolságkorlát                 | nem                  |
| **Vanguard**                  | front row unit, amely rendelkezik Intercepttel    | front row, de nem azonos oszlophoz kötött | **igen**             |
| **Duel Masters**              | Blocker képességű creature                        | nincs sávgeometria                        | **igen**             |
| **jelenlegi AETERNA**         | bármely Aktív Horizont-Entitás                    | jelenleg nincs explicit Áramlat-korlát    | nem                  |
| **szomszédos AETERNA-modell** | jogosult Horizont-Entitás                         | saját/közeli Áramlat                      | nem feltétlenül      |

Magicben a védekező játékos bármely megfelelő untapped creature-jét rendelheti támadóhoz; a rendszer nem térbeli, ezért ez természetesen globális. ([MAGIC: THE GATHERING][1])

Vanguardban viszont már kettős szűrés van: a közbelépőnek **front rowban kell lennie és Intercepttel kell rendelkeznie**, de nem találtam azonos oszlopra vonatkozó feltételt. A current rules szerint egy vagy több megfelelő front-row Intercept unit választható, ha azok maguk nincsenek támadás alatt. ([en.cf-vanguard.com][2])

A Duel Masters még érdekesebb összehasonlítás: ott a „Blocker” kifejezetten támadási célpontot módosító képesség, és a megtámadott creature **nem használhatja saját magán** ezt a képességet. Tehát ez a rendszer „külön jogosultság + globális közbelépés” felé megy. ([デュエル・マスターズ][3])

### Mit jelentene a teljesen globális modell az AETERNÁ-ban?

Tegyük fel:

```text
Áramlat 1: Aktív Entitás A
Áramlat 2: Aktív Entitás B
Áramlat 3: üres Horizont → Zenit támadható
Áramlat 4: üres
Áramlat 5: Aktív Entitás C
Áramlat 6: üres Horizont → Pecsét támadható
```

Ha **bármely Aktív Horizont-Entitás** közbeléphet, akkor:

```text
Áramlat 6 Pecsétjét támadják
→ A, B vagy C megvédheti
```

Ez nagyon rugalmas és egyszerű.

De van egy komoly következménye: az Áramlat 6 frontvonalának áttörése **nem jelenti azt, hogy ténylegesen áttörtél a védelem azon részén**. Mert az Áramlat 1-ből egy Entitás rögtön átérhet oda.

A hat külön Áramlat ezért részben:

```text
6 külön védelmi oszlop
```

helyett

```text
1 közös hatmezős Horizont-védőpool
```

jellegűvé válik.

Ez szerintem az első komoly érv a jelenlegi globális blokkolás ellen.

## A teljesen azonos Áramlatos modell viszont szinte biztosan rossz

Ebben az esetben:

```text
Áramlat 3 Zenitje támadható
```

pont azért, mert:

```text
Áramlat 3 Horizontja üres
```

Tehát ugyanabban az Áramlatban **definíció szerint nincs Horizont-Entitás**, amely közbeléphetne.

Ugyanez a Pecsét esetén.

Ezért:

```text
csak azonos Áramlatból lehet védeni
```

a Zenit/Pecsét-védelem szempontjából önellentmondó lenne.

Ezt én az elemzésből gyakorlatilag ki is húznám a komoly jelöltek közül.

## A szomszédos Áramlat-modell

Ez már sokkal érdekesebb.

Például:

```text
          H1 H2 __ H4 H5 H6
Áramlat:  1  2  3  4  5  6
                ↑
           támadott Zenit
```

Ha a 3. Áramlat Zenitjét támadják, akkor például:

```text
Áramlat 2 Horizontja
és
Áramlat 4 Horizontja
```

avatkozhatna közbe.

Ez nagyon szépen megtartaná azt az érzést, hogy **a szomszédos frontszakaszok segíthetnek egymásnak**, de egy Entitás nem teleportál át az egész csatatéren.

És rögtön értelmet adna a pozíciómozgatásnak is. Az AETERNA már most is ismer szomszédos mezőre történő mozgást a tervezési rétegben, tehát a „szomszédság” nem teljesen idegen fogalom a rendszertől. 

Viszont ennek van egy problémája:

```text
1. Áramlat → csak 2. szomszéd
6. Áramlat → csak 5. szomszéd

3–4. Áramlat → két szomszéd
```

Tehát a középső Áramlatok **természetesen könnyebben védhetők**, mint a szélsők.

Ez lehet jó taktikai tulajdonság — de lehet nem kívánt board-geometry bias is.

És még egy következmény:

```text
ha a 3. Áramlat Pecsétjét támadják,
a 2. és 4. Áramlatban tartott Aktív Entitások
fenyegetésként számítanak
```

Tehát a játékos már az Entitások elhelyezésekor **védelmi hálót** épít.

Ez sokkal több értelmet adna a 6 oszlopnak, mint a globális modell.

## Külön jogosultsághoz kötött modell

A másik nagy irány az lenne, hogy nem minden Horizont-Entitás képes közbelépni.

Ez áll legközelebb a Vanguard és Duel Masters gondolkodásához. ([en.cf-vanguard.com][4])

Például:

```text
Harcos A → nem képes speciális közbelépésre
Lovag B → képes
Mágus C → nem képes
```

Ez viszont **nagyon nagy AETERNA-változás** lenne.

A jelenlegi főforrás általános Horizont-funkcióként kezeli a blokkolást, és a kártyatervezési katalógus is úgy beszél például Harcosokról és Lovagokról, hogy a védekezés/blokkolás általános harci rendszerre épül. A Lovag csak különösen védelmi karakterű.  

Ha csak külön jogosultságú lapok védhetnének:

```text
generic Core action
→
kártyaspecifikus képesség
```

változás történne.

Ez deckbuilding szempontból is erős lenne: egy pakli, amely nem húzza fel a megfelelő védő típusait, sokkal könnyebben elveszítené a Zenitet/Pecséteket.

Nem feltétlenül rossz — csak lényegesen nagyobb újratervezés.

## Van viszont egy negyedik, szerintem különösen érdekes hibrid

Ezt egyik vizsgált játék sem adja készen; ez már kifejezetten **AETERNA-specifikus** lenne.

Alapszabályként:

```text
bármely Aktív Horizont-Entitás
→ a szomszédos Áramlat védelmére közbeléphet
```

és bizonyos kártyák külön képességgel kiterjeszthetnék ezt:

```text
ez az Entitás távolabbi Áramlat védelmére is közbeléphet
```

vagy:

```text
bármely saját Áramlatot védhet
```

Így nem kellene az egész Core-védekezést külön kulcsszóhoz kötni, de a védelmi specialista Entitásoknak lenne **valódi extra szerepük**.

Ez például nagyon jól illene ahhoz, amit a kártyatervezési katalógus már most a Lovagról mond: „társak védelme”, „Pecsét vagy Áramlat védelme”, „védelmi formáció”. 

Nem azt jelenti, hogy ezt kell választanunk. Csak azt, hogy a meglévő AETERNA kártyaszerepekkel feltűnően jól összeilleszthető.

### Jelenlegi összehasonlításom

Ha most csak ezt az egy dimenziót nézem:

**Globális, minden Aktív Horizont-Entitás:** egyszerű és nagy játékosi szabadság, de szerintem túlságosan összemossa a hat Áramlatot.

**Csak speciális Entitás:** erős kártyaszerepek és Vanguard-szerűség, de túlságosan nagy Core-átalakítás lehet.

**Szomszédos Áramlat:** a legerősebb pozíciós játékot hozza, viszont kezelni kell a szélső/középső Áramlat különbségét.

**Szomszédos alap + külön kiterjesztett védelmi képességek:** jelenleg ezt tartom a legérdekesebb munkahipotézisnek, mert egyszerre őrizné meg a Core-védekezést és adna jelentést a Domínium geometriájának.

De ezt még **nem választanám ki**.

Mert van egy olyan kérdés, amely előbb eldöntheti, hogy ezek közül melyik működik egyáltalán:

> **Ugyanaz legyen-e a közbelépési szabály akkor, amikor Horizont-Entitást, Zenit-Entitást, Pecsétet vagy végül az Aeternalt támadják?**

Szerintem ez a következő vizsgálandó rész. Könnyen lehet ugyanis, hogy az optimális rendszer **nem egyetlen globális szabály**, hanem a védett rétegtől függően más: például Horizont-célpont védése szigorúbb, míg Pecsét védelmére szélesebb közbelépési lehetőség jár. Ez közvetlenül kapcsolódik ahhoz, amit korábban mondtál, hogy a blokkolás igazi értelme különösen a **Zenit és Pecsét** támadásakor látszik.

[1]: https://magic.wizards.com/en/news/feature/dynamics-turn-2006-11-04?utm_source=chatgpt.com "The Dynamics of a Turn | MAGIC: THE GATHERING"
[2]: https://en.cf-vanguard.com/howto/?utm_source=chatgpt.com "Rules/Q&A ｜ Cardfight!! Vanguard Trading Card Game | Official Website"
[3]: https://dm.takaratomy.co.jp/rule/rulechange/31636/?utm_source=chatgpt.com "攻撃先を変更する能力の処理に関する裁定変更のお知らせ | デュエル・マスターズ"
[4]: https://en.cf-vanguard.com/wordpress/wp-content/uploads/Cardfight-Vanguard-Comprehensive-Rules-4.45.pdf?utm_source=chatgpt.com "Vanguard Comprehensive Rules"


--rendben van 
folytassuk akkor az elemzést
nekem legjobb jelenleg a Szomszédos alap + külön kiterjesztett védelmi képességek verzió tetszik 
akár képesség akár kulcsszóval is megtudjuk oldani
ez még nem végleges irány de erős koncepciónak gondolom--

Igen, ezt most **erős koncepcióként**, de nem végleges döntésként kezelném:

> **Alapból a szomszédos Áramlat Horizont-Entitása avatkozhat közbe, bizonyos kártyák pedig képességgel vagy kulcsszóval kiterjeszthetik ezt a védelmi hatótávot.**

Az „Intercept/Guardian” továbbra is csak összehasonlító munkanyelv; végleges AETERNA-név majd később lesz.

A források alapján ez az irány ráadásul jól illeszkedik a játék már meglévő identitásához. A Core kifejezetten pozíciós, 6 Áramlatos védelmi rendszert akar, a Hasítás egy Áramlaton belüli áttörést jelent, a kártyatervezési katalógus pedig már most külön szerepet ad a Lovagoknak és Őrzőknek a társak, Pecsétek és Áramlatok védelmében.  

## Nézzük meg rétegenként

| Eredeti támadási célpont | Szomszédos alapvédelem mennyire természetes? | Fő probléma                             |
| ------------------------ | -------------------------------------------: | --------------------------------------- |
| Horizont-Entitás         |                               közepesen erős | Oltalommal összeakadhat                 |
| Zenit-Entitás            |                              **nagyon erős** | alig van szemantikai probléma           |
| Pecsét                   |                              **nagyon erős** | balansz / játék lassulása               |
| Aeternal                 |                                  bizonytalan | nincs saját Áramlata, endgame-et érinti |

### Horizont-Entitás

Egy normál, például Kimerült Horizont-Entitásnál ez jól érthető lenne:

```text
Áramlat 3: megtámadott Entitás
Áramlat 2 vagy 4: Aktív védő Entitás

→ valamelyik közbeléphet
```

Itt valódi taktikai döntés keletkezik: érdemes-e egy másik frontvonalbeli egységet kockára tenni azért, hogy megmentsünk egy fontos célpontot.

Ez Magic-szerű szempontból is természetes: ott a védekező creature nem az eredeti megtámadott objektum helyét veszi át, hanem az adott támadó útját állítja el. A rendszer ugyanígy működik akkor is, ha a támadás játékos, planeswalker vagy battle ellen irányul. ([MAGIC: THE GATHERING][1])

Az **Oltalom azonban külön eset** marad.

A saját forrásunk világosan rögzíti, hogy az Oltalom célpontválasztási kényszer, nem automatikus blokkolás és nem sebzéscsökkentés. 

Ezért két koherens értelmezés maradna:

```text
A)
Oltalom = csak azt szabja meg,
kit KELL megtámadni.
Utána az Oltalom-célpont is védhető.

B)
Oltalom = "én fogom fel ezt a támadást",
ezért a normál védelmi közbelépés
nem mentheti ki.
```

Jelenleg nekem a **B** tematikailag tisztábbnak tűnik, és közelebb áll ahhoz, amit te korábban mondtál. De ezt még nem venném döntésnek.

### Zenit-Entitás

Itt szerintem a legerősebb az egész új koncepció.

A Zenit normálisan csak akkor válik fizikai támadás számára elérhetővé, ha a saját Áramlatának Horizontja már üres. 

Tehát:

```text
Áramlat 3

Horizont: üres
Zenit: Mágus
```

A saját Áramlatából már **nincs aki megvédje**.

Viszont:

```text
Áramlat 2: Aktív Horizont Entitás
Áramlat 4: Aktív Horizont Entitás
```

logikusan beavatkozhat.

Ez ténylegesen azt modellezi, hogy a szomszédos frontszakaszok támogatják a meggyengült védelmi vonalat.

És ettől a hat Áramlat nem dekoráció lesz, hanem valódi **védelmi formáció**.

### Pecsét

Szerintem itt még erősebb a mechanika.

A Core szerint a normál Pecsét-feltöréshez sikeres, **blokkolatlan** fizikai támadás kell. 

Tehát már a jelenlegi szabály filozófiája is azt mondja:

```text
Pecsét támadható
≠
Pecsét automatikusan feltörik
```

Van még egy védekezési lehetőség.

Az új rendszerben:

```text
Áramlat 3 Pecsétjét támadják

Áramlat 2 vagy 4
Aktív Horizont-Entitása
közbeléphet
```

Ez szerintem nagyon jó.

A játékos áttörte a 3. Áramlat saját védelmét, de **a szomszédos front még képes reagálni**.

Ez több fontos stratégiai következményt ad:

* az egymás melletti frontok támogatják egymást;
* nem mindegy, melyik Áramlatot hagyod üresen;
* az ellenfél megpróbálhatja előbb Kimeríteni a szomszédos védőket;
* pozíciómozgató lapok sokkal érdekesebbé válnak;
* a védelmi specialisták valóban Pecsétvédő szerepet kaphatnak.

Ez nagyon jól illik a LUX / Lovag / Őrző már leírt identitásához.  

## Van itt egy különösen fontos Hasítás-kapcsolat

Ez szerintem megerősíti az új modellt.

A Hasítás hivatalosan **nem általános túlcsordulás**. Csak akkor visz tovább felesleges harci sebzést, ha a támadó ténylegesen rendelkezik Hasítással, és mindig egyetlen Áramlat szerkezeti láncát követi:

```text
Horizont
→ Zenit
→ Pecsét
```

Nem ugrik másik Áramlatba.

Ez azt sugallja, hogy a normál közbelépés esetén:

```text
nincs Hasítás
→ a védő megállítja a támadást
```

még akkor is, ha maga a védő elpusztul.

És csak:

```text
Hasítás
→ megfelelő feltételekkel
felesleges sebzés továbbhaladhat
```

Ez szerintem **nagyon tiszta rendszer** lenne.

Mert így nem kell külön általános „áttörés” szabályt létrehozni: már van erre saját kulcsszavunk.

## A Légies is természetesen beilleszthető

A jelenlegi főforrás egyértelmű: Légies támadót csak Légies Entitás blokkolhat. 

Tehát az új rendszerben egyszerűen:

```text
Légies támadó
→ csak Légies jogosult védő
avatkozhat közbe
```

A szomszédosság csak a **pozíciós jogosultság**, a Légies pedig továbbra is fizikai-interakciós jogosultság.

Ez kifejezetten jól rétegezhető szabály.

---

# Az Aeternal viszont tényleg külön probléma

Az Aeternal nem egy Áramlathoz tartozik.

A Core szerint akkor válik támadhatóvá, ha már nincs fennálló Pecsét, és vereség akkor következik be, ha az Aeternal elleni fizikai támadás **sikeresen feloldódik**. 

Tehát:

```text
6 Áramlat
↓
6 Pecsét
↓
Aeternal
```

de az Aeternal mögött már nincs:

```text
"3. Áramlat"
```

vagy:

```text
"szomszédos Áramlat"
```

fogalom.

Ezért a szomszédos alapszabály **nem alkalmazható rá természetesen**.

És itt három modell van:

| Aeternal-védelem                        | Következmény                                                       |
| --------------------------------------- | ------------------------------------------------------------------ |
| bármely Aktív Horizont-Entitás védheti  | a végjátékban a rendszer hirtelen globálissá válik                 |
| egyetlen Entitás sem védheti normálisan | 0 Pecsét után valódi „végső veszély” állapot                       |
| csak külön képességgel lehet védeni     | Core finisher megmarad, de védelmi specialisták kaphatnak kivételt |

Jelenleg a **harmadikat tartom a legérdekesebbnek** a te felvetéseddel együtt:

```text
normál szomszédos közbelépés:
Horizont / Zenit / Pecsét

Aeternal:
nem tartozik az alap hatótávba

DE

speciális védelmi képesség/kulcsszó:
engedheti az Aeternal védelmét
```

Ez nagyon jól megkülönböztetné az igazán különleges testőr/őrző lapokat.

És közben a 0 Pecsét továbbra is súlyos állapot maradna.

## Egy komoly geometriai problémánk még van

A lineáris 6 Áramlat miatt:

```text
1 – 2 – 3 – 4 – 5 – 6
```

a 3. és 4. Áramlatnak két szomszédja van.

Az 1.-nek és 6.-nak csak egy.

Tehát:

```text
középső Pecsétek:
akár 2 potenciális védő Áramlat

szélső Pecsétek:
csak 1
```

Ez **automatikus balanszkülönbséget** hoz létre.

Mivel a támadó szabadon választhat szabályos célpontot, könnyen kialakulhat:

> „mindig a szélső Áramlatot érdemes elsőként áttörni.”

Ez még nem biztos, hogy probléma — playtest nélkül nem tudjuk.

De fontos, mert ha a szomszédos modell lesz a végleges, **ezt kötelező lesz tesztelni**.

Én nem oldanám most mesterségesen körkörössé:

```text
6 ↔ 1
```

mert az fizikailag és intuitívan elég furcsa lenne a jelenlegi játéktéren.

---

## Jelenlegi munkahipotézis

Most nagyjából ezt látom legerősebbnek — továbbra sem döntésként:

```text
NORMAL DEFENSE RANGE

Horizont:
szomszédos Áramlat
[Oltalom külön tisztázandó]

Zenit:
szomszédos Áramlat

Pecsét:
szomszédos Áramlat

Aeternal:
nincs normál szomszédos védelem
```

és erre épülne:

```text
EXTENDED DEFENSE

képesség vagy kulcsszó például:
- távolabbi Áramlat védése
- bármely Áramlat védése
- Pecsét fokozott védése
- Aeternal védése
- speciális pozícióból történő közbelépés
```

Ez a rendszer szerintem **nagyon erős design space-t** nyitna anélkül, hogy minden Entitás globális védővé válna.

A Vanguardban az Intercept is külön jogosultsághoz kötött front-row védelmi eszköz, míg Magicben a blocking általánosabb és célponttípustól nagyrészt független. A mi jelenlegi irányunk a kettő között lenne, de kifejezetten az AETERNA Áramlat-geometriájára építve. ([CF Vanguard][2])

### A következő egyetlen kérdés

Szerintem most **nem az Aeternal vagy az Oltalom** következzen még.

Előbb ezt tisztázzuk:

> **Ha egy védő Entitás közbelép, majd a harcban megsemmisül, a támadás teljesen megálljon-e — és csak Hasítás esetén mehessen tovább az eredeti célpont felé?**

Ez alapvetően meghatározza, hogy az új mechanika ténylegesen mit jelent, és utána sokkal könnyebb lesz külön kezelni az Oltalmat, Pecsétet és Aeternalt.

[1]: https://magic.wizards.com/en/news/feature/march-of-the-machine-release-notes?utm_source=chatgpt.com "March of the Machine Release Notes"
[2]: https://en.cf-vanguard.com/wordpress/wp-content/uploads/Cardfight-Vanguard-Comprehensive-Rules170830.pdf?utm_source=chatgpt.com "ヴァンガード 総合ルール ver"


--az én értelmezésemben igen megáll
hiszen a támadó már támadott és támadás után kimerül ha nincs valami modosito képessége vagy speciális akadályozó képesség akkor marad az alap szabály egy entitás egyszer támadhat azután kimerül 
esetleg van valami amit rosszul értelmezek ?--

Igen, az alapértelmezésed **eredményében helyes**, csak egy fontos fogalmi pontosítás van.

A támadás azért **nem megy tovább automatikusan az eredeti célpontra**, mert a közbelépő védővel lezajlott harc ugyanannak az egy deklarált támadásnak a feloldása. Az, hogy a támadó Kimerült, egy külön következmény: ez azt akadályozza meg, hogy utána újabb normál támadást deklaráljon.

Tehát nem így érdemes elképzelni:

```text
védő meghal
→ támadó még Aktív lenne?
→ ha nem, akkor nem tud továbbmenni
```

hanem inkább:

```text
egy támadás deklarálva
→ közbelép egy védő
→ támadó ↔ védő harci sebzés
→ az adott támadás befejeződik
```

A támadó állapota ettől függetlenül:

```text
támadás deklarálása
→ támadó Kimerül
```

A jelenlegi Core-ban az attacker Exhaust valóban már a támadás deklarálásának része, tehát a védő későbbi megsemmisülése nem „adja vissza” a támadást.

Ez azért fontos, mert különben egy nagyon furcsa szabály keletkezne. Például:

```text
Attacker ATK 10
Guardian HP 1

Guardian közbelép
→ meghal
→ marad 9 "fel nem használt" ATK
```

Normál esetben ez a 9 **nem jelent semmit**. Az ATK nem egy olyan erőforrás, amelyből levonogatjuk az útba kerülő egységeket.

A támadó megtámadta a közbelépő védőt az adott combat resolution során, az attack pedig ezzel teljesült.

És pontosan itt kap értelmet a **Hasítás**.

Normál támadó:

```text
Attacker 10 ATK
→ Defender 1 HP

Defender megsemmisül
→ támadás vége
→ eredeti célpont sértetlen
```

Hasításos támadó esetén viszont külön szabály mondhatja:

```text
Attacker 10 ATK
→ Defender 1 HP
→ 1 szükséges a Defender legyőzéséhez
→ fennmaradó 9 továbbhaladhat
   az eredeti támadási útvonalon
```

Ez nem azért történik, mert a támadó „még támadhat”, hanem mert a **Hasítás módosítja ugyanannak az egy támadásnak a feloldását**.

Ez szerintem nagyon fontos különbség.

### Egy támadás ≠ egy sebzéscsomag, amely addig megy, amíg van ATK

Hanem:

> **egy támadás egy deklarált harci eseménysor.**

A normál közbelépés lezárja azt.

A Hasítás pedig explicit kivétel:

> **a támadás bizonyos fennmaradó következménye továbbhaladhat.**

Ez ráadásul nagyon szépen illeszkedik az AETERNA már meglévő Hasítás-koncepciójához, amely eleve az Áramlat védelmi rétegein történő áttörésről szól, nem arról, hogy a támadó újabb támadást kap.

Egyetlen további dolgot kell majd később pontosan definiálnunk: **mi történik akkor, ha a közbelépő még a harci sebzés előtt eltűnik vagy illegálissá válik egy reakció következtében**.

Például:

```text
Attack → Pecsét
→ Defender közbelép
→ Reaction
→ Defender visszakerül kézbe
→ ?
```

Ott már nem arról beszélünk, hogy a Defender meghalt a harcban, hanem arról, hogy **a combat resolution pillanatában nincs ott**. Ilyenkor külön kell majd eldöntenünk, hogy az eredeti támadás szabaddá válik-e, meghiúsul-e, vagy újraértékeljük-e.

De ez egy következő edge case.

Arra a mostani kérdésre, hogy:

> „Ha a közbelépő harcban megsemmisül, továbbmegy-e normálisan a támadás?”

szerintem a tiszta válasz:

**Nem. A normál támadás ott véget ér. Továbbhaladás csak explicit módosítóval, elsősorban Hasítással történhet.**

És az indok nem elsősorban a Kimerülés, hanem az, hogy **az egyetlen deklarált támadás már feloldódott**.


--ebben az esetben akkor a korábbi kérdést megválaszoltnak tekinthetjük?
a következö kérdésed viszont nagyon érdekes dolgokat vet fel: **mi történik akkor, ha a közbelépő még a harci sebzés előtt eltűnik vagy illegálissá válik egy reakció következtében**.  
korábban pont hasonló helyzetet vizsgáltunk a Rituálé/Ige lapokkal 
ugynézki mégis csak kell egy komolyabb Timeing rendszer valami hasonló mint a yugiohban a Chain vagy spell speed mechanikák
kelleni fog igy egy saját rendszer amibe beköthetünk ilyen dolgokat mint ami a kérdésedben is szerepel mert igy már nem csak a Rituálé/Ige lapokkal lesz gond hanem másokkal is--

Igen. A korábbi kérdést szerintem **megválaszoltnak tekinthetjük munkadöntésként**:

> **Ha a közbelépő védő a normál harci sebzés során megsemmisül, az eredeti támadás nem halad tovább. Az adott támadás ezzel feloldódott. Továbbhaladás csak explicit szabály vagy módosító — elsősorban Hasítás — miatt történhet.**

Ezt még nem nevezném örökre végleges szabálynak, de jelenleg nincs rajta olyan ellentmondás, ami miatt tovább kellene bontanunk.

A második felismerésed viszont nagyon fontos: **igen, most már látszik, hogy az AETERNÁ-nak általános timing-rendszer kell.** Nem csak az Ige/Rituálé miatt.

A jó hír az, hogy ezt nem nulláról kell felépítenünk. A Reaction / Priority v1, amit most fejeztünk be, tulajdonképpen már ennek a váza: van `ReactionWindow`, priority, LIFO stack, passzolás, revalidáció, invalidált feloldás és trigger-checkpoint.

Ami most kiderült, az az, hogy ezt **nem szabad kizárólag „spell reaction systemként” kezelni**. Általános játékmotor-timing rendszerként kell továbbfejleszteni.

Például a mostani harci eset:

```text
Attack declaration
→ attacker Kimerül
→ target rögzítve
→ ReactionWindow

window lezár
→ attack revalidation

→ block opportunity

Defender közbelép
→ defender Kimerül
→ ReactionWindow

reakció:
Defender visszakerül kézbe

window lezár
→ block/combat state revalidation

→ mi történjen?
```

És ugyanez a szerkezeti probléma már előjött az Igénél:

```text
Ige kijátszva
→ resolution state
→ ReactionWindow
→ reakciók
→ eredeti Ige revalidálása
→ resolve vagy invalidated/fizzle
```

Vagyis valójában ugyanarról a motorproblémáról beszélünk.

## Yu-Gi-Oh jó inspiráció, de nem másolnám le

A Chain nagyon hasznos modell arra, hogy:

```text
Action / effect
→ válasz
→ válasz a válaszra
→ ...
→ fordított sorrendű feloldás
```

A Spell Speed pedig arra válaszol, hogy:

> **mi mire válaszolhat?**

Ez az AETERNÁ-ban is szükséges lesz valamilyen formában.

De én nem hoznék be automatikusan egy ilyen rendszert:

```text
Spell Speed 1
Spell Speed 2
Spell Speed 3
```

mert nálunk nemcsak varázslatok vannak, hanem:

* támadás deklarálása;
* közbelépő védelem;
* Pecsétfeltörés;
* aktivált képesség;
* triggered képesség;
* Ige;
* Rituálé;
* Jel;
* esetleges Burst;
* állapotváltozás;
* kényszerített akció;

és ezekre ugyanannak a timing frameworknek kell működnie.

Inkább saját kategóriáink lehetnek majd.

Például — **csak szemléltetésként, még nem javasolt végleges séma**:

```text
DECLARATION
    attack
    defense
    activated ability
    card play

RESPONSE WINDOW
    normál reakciók
    speciális reakciók

RESOLUTION

REVALIDATION

POST-RESOLUTION
    triggers
    state-based consequences
```

És külön lehet response-class:

```text
cannot_respond
normal_response
immediate_response
special_response
```

Ez ugyanazt a problémát oldaná meg, mint a Spell Speed, de AETERNA-nyelven.

## A legfontosabb elv szerintem már most kirajzolódik

**Nem minden eseményre kell ReactionWindow.**

Ez kulcsfontosságú.

Ha minden apróság:

```text
sebzés
Kimerülés
lapmozgás
Pecsét reveal
HP változás
trigger létrejötte
```

új ablakot nyitna, a játék rettenetesen szétesne.

Inkább explicit **timing pointok** kellenek.

Például harcnál:

```text
Attack declared
↓
TIMING POINT A
ReactionWindow

↓
revalidation

Block/defense declared
↓
TIMING POINT B
ReactionWindow

↓
revalidation

Combat resolves
↓
no normal interruption during atomic combat resolution

↓
POST-RESOLUTION checkpoint
triggers / consequences
```

Ez nagyon hasonló gondolkodás ahhoz, amit a Yu-Gi-Oh Chain és más TCG-k használnak, csak nálunk jobban ráilleszthető a fizikai harcra.

## És ez megoldhatja a „védő eltűnik” problémát is

Ha a közbelépő eltűnik **a védelmi ReactionWindow alatt**, akkor nem kell rögtön minden lehetséges eredményt külön szabályként beleégetni.

A rendszer:

```text
ReactionWindow lezár
→ revalidate combat state
```

és akkor megvizsgáljuk:

```text
attacker még szabályos?
original target még szabályos?
declared defender még szabályos?
```

Innen jön a subject-specifikus következmény.

Például később dönthetünk úgy, hogy:

```text
defender invalid
→ defense declaration invalidated
→ original attack continues toward original target
```

vagy:

```text
defender invalid
→ entire combat attempt fizzles
```

vagy valamilyen harmadik szabály.

**De a timing engine-nek nem kell kitalálnia ezt.**

A timing engine csak ezt garantálja:

> „Most van az a pont, ahol kötelező újraellenőrizni az állapotot.”

Ez nagyon fontos architekturális szétválasztás.

---

Szerintem tehát két külön rétegünk lesz:

```text
TIMING FRAMEWORK
- mikor nyílik ablak
- ki kap priorityt
- mi válaszolhat mire
- milyen sorrendben oldódik fel
- mikor történik revalidation
```

és:

```text
SUBJECT-SPECIFIC RULES
- ha Ige source eltűnik → mi legyen?
- ha attack target eltűnik → mi legyen?
- ha defender eltűnik → mi legyen?
- ha Pecsét már nem standing → mi legyen?
```

Ez szerintem **sokkal stabilabb**, mint minden egyes mechanikához külön reakciós szabályt fabrikálni.

És emiatt most nem mennék tovább a „védő eltűnt, tehát pontosan mi történjen?” kérdéssel.

Előbb egyetlen alapvető dolgot tisztáznék:

> **Mely játékműveletek legyenek az AETERNA hivatalos response/timing pointjai, amelyek után ReactionWindow nyílhat?**

Mert ha ezt jól rakjuk össze, az Ige/Rituálé, Combat, Pecsét és később a többi mechanika ugyanarra a közös rendszerre tud majd ráülni.


--"Mert ha ezt jól rakjuk össze, az Ige/Rituálé, Combat, Pecsét és később a többi mechanika ugyanarra a közös rendszerre tud majd ráülni. "
igen pontosan ezt szeretném igazad van nem konkrétan a yugioh modelt kell beleültetni az Aeternába hanem mintaként kell használni és a segitségével kifejleszteni egy saját megoldást
szerintem kicsit sok rétűbb a helyzet mint a hogy te látod itt megint csak vissza utalok a yugiohra de igazából akár az Aeternán bellül is mondhatom mert itt is vannak képességek, "varászlatok" és "csapdák" is 
szerintem pontosabb a: mi történik akkor ha egy lánc közbenső elemével valami történik? eltünik vagy megváltozik a célpont például mert lehet hogy az Entitás nem tünik el de a képesség ami célozta egy speciális feltételt figyel például az ATK értékét ha azt egy másik képesség megváltoztatta akkor már nem érvényes rá a feltétel
kicsit konkrétabb példa: az aktivált hatás hogy az ellenfél legalacsonyabb ATK értékü Entitása megsemmisül-- válaszlépés hatás ami az ATK értéket nőveli -- már nem az a legalacsonyabb ATK értékü Entitás -- folytatás 
ebben az esetben egyértelmü hogy mi történik mert van másik Entitás akkor a hatás átvált rá de nem biztos hogy minden hatás folytatható igy--

Igen, pontosan. Most már látszik, hogy **nem elég egy egyszerű „ReactionWindow + LIFO” rendszer**. Két külön, de összekapcsolt dolgot kell megterveznünk:

1. **mikor és milyen sorrendben lehet válaszolni**;
2. **mi történik az egyes közbenső elemekkel feloldáskor, ha közben megváltozott a játékállapot**.

A Yu-Gi-Oh ebből a szempontból nagyon jó minta, mert hivatalosan is külön kezeli az aktiválási feltételeket, a célzást és a feloldáskori feltételeket. A Chain visszafelé oldódik fel, és a card text külön jelzi, hogy valamely feltétel csak aktiváláskor számít-e, vagy feloldáskor is újra ellenőrizni kell. ([yugioh-card.com][1])

A példád tökéletesen megmutatja, miért kell ennél pontosabb modell.

Tegyük fel:

```text
E1 ATK = 1000
E2 ATK = 1500
```

Aktiválódik:

> „Semmisítsd meg az ellenfél legalacsonyabb ATK értékű Entitását.”

Erre válasz:

> „E1 kap +1000 ATK-t.”

A válasz oldódik fel először:

```text
E1 = 2000
E2 = 1500
```

Most jön az eredeti hatás.

És itt **nem egyetlen automatikusan helyes válasz létezik**. Attól függ, hogyan definiáltuk magát a hatást.

### A) Dinamikus kiválasztás

Ha a hatás jelentése:

> „Feloldáskor keresd meg az ellenfél jelenlegi legalacsonyabb ATK-jú Entitását, és semmisítsd meg.”

akkor:

```text
aktiváláskor nincs véglegesen rögzített target

resolution:
→ újra kiszámítjuk a legalacsonyabb ATK-t
→ E2
→ E2 megsemmisül
```

Ebben az esetben valóban **„átvált”** E2-re.

De valójában nem retarget történt. A hatás **csak most választotta ki a végrehajtási objektumot**.

Ez fontos fogalmi különbség.

---

### B) Rögzített célpont + feloldáskori újraellenőrzés

Másképp is írhatjuk:

> „Válaszd ki az ellenfél legalacsonyabb ATK-jú Entitását; semmisítsd meg azt a célpontot.”

Aktiváláskor:

```text
target = E1
```

A válasz után:

```text
E1 már nem a legalacsonyabb ATK
```

Ha a szabály szerint a `lowest ATK` feltételnek **feloldáskor is igaznak kell lennie**, akkor:

```text
target E1 invalid
→ effect nem tud rá végrehajtódni
```

És nagyon fontos:

**nem vált át automatikusan E2-re.**

A Yu-Gi-Oh PSCT pont ilyen megkülönböztetéseket használ: bizonyos targeting követelményeket feloldáskor is újra kell ellenőrizni, más feltételek viszont csak aktiváláskor számítanak. ([yugioh-card.com][2])

---

### C) Rögzített célpont, de a feltétel csak aktiváláskor számít

Megint más szabály:

```text
activation:
E1 legal target volt
→ target = E1
```

E1 később kap +1000 ATK-t.

De ha a „legalacsonyabb ATK” csak **target-selection condition**, és nem resolution condition, akkor:

```text
E1 továbbra is a rögzített target
→ effect megsemmisíti E1-et
```

Ez is teljesen koherens.

A Yu-Gi-Oh hivatalos PSCT rendszere még ezt a különbséget is képes kifejezni: van, amikor a target eredeti jogosultsága elegendő, és van, amikor a feloldáskor újra teljesítenie kell a feltételeket. ([yugioh-card.com][2])

---

És szerintem **itt van az AETERNA saját rendszerének egyik kulcsa**.

Nem elég azt tárolni, hogy:

```text
target = card_123
```

A hatásnak azt is tudnia kell, hogy **milyen kapcsolatban van ezzel a targettel**.

Én jelenleg legalább négy külön fogalmat látok.

| Típus                   | Mit jelent?                                                             |
| ----------------------- | ----------------------------------------------------------------------- |
| **Locked Target**       | aktiváláskor kiválasztjuk és rögzítjük                                  |
| **Dynamic Selector**    | csak feloldáskor számítjuk ki                                           |
| **Locked + Revalidate** | rögzítjük, de resolutionkor újra legalitást vizsgálunk                  |
| **Explicit Reselect**   | ha az eredeti target invalid, a hatás kifejezetten új célpontot választ |

Az utolsó szerintem különösen fontos:

> **A retarget soha ne történjen automatikusan csak azért, mert az eredeti célpont illegálissá vált.**

Ha egy effect új célt kereshet, azt **explicit képességtulajdonságnak** tekinteném.

Ez megakadályozna rengeteg későbbi félreértést.

---

## A „közbenső láncelem eltűnik” kérdése még ennél is szélesebb

Vegyünk három láncelemet:

```text
L1: semmisítsd meg E1-et
L2: E1 ATK +1000
L3: küldd E1-et a Voidba
```

LIFO:

```text
L3
→ L2
→ L1
```

L3 feloldódik:

```text
E1 elhagyja a Domaint
```

Most L2 következik.

A kérdés:

> eltűnik-e L2 a stackből?

Én azt gondolom, hogy **nem**.

Ez nagyon fontos alapelv lehetne:

> **Ha egy resolution entry egyszer szabályosan létrejött, a későbbi state-változás önmagában nem törli ki a stackből.**

Hanem amikor sorra kerül:

```text
L2 revalidation
→ nincs megfelelő subject/target
→ invalidated / no applicable effect
→ resolution attempt lezárul
```

Majd:

```text
L1 revalidation
→ ugyanez
```

Ez sokkal determinisztikusabb.

A Yu-Gi-Oh Chain is ilyen alapelvre épít: a Chain Linkek felkerülnek a láncra, majd visszafelé próbálnak feloldódni; az, hogy közben megváltozott az állapot, nem jelenti automatikusan azt, hogy a Chain Link egyszerűen eltűnik. ([Yu-Gi-Oh! Kártyák][3])

Az effect persze lehet olyan, amelynek a forrásának továbbra is jelen kell lennie. A Yu-Gi-Oh is külön jelzi az ilyen eseteket; például vannak effectek, amelyek csak akkor oldódnak fel, ha a source továbbra is megfelelő helyen/állapotban van. ([yugioh-card.com][2])

---

## Vagyis legalább három dolgot külön kell vizsgálnunk minden resolution entrynél

Nem csak targetet.

### 1. Source

Például:

```text
Entitás aktivált képessége
→ Entitást közben megsemmisítik
```

Kérdés:

```text
a képesség önállóan tovább él?
```

vagy:

```text
source jelenléte szükséges resolutionkor?
```

Mindkettőre lesznek képességek.

---

### 2. Target / Subject

```text
target eltűnt
target zónát váltott
controller megváltozott
ATK megváltozott
activity megváltozott
keywordet kapott/vesztett
```

Melyik változás invalidálja?

Ez effect-specifikus.

---

### 3. A hatás végrehajthatósága

Például:

```text
"Semmisíts meg egy Entitást,
majd húzz 2 lapot."
```

Ha az Entitást már nem lehet megsemmisíteni:

```text
húzol azért 2-t?
```

Ez megint nem timing kérdés önmagában.

Ez **effect dependency** kérdés.

A Yu-Gi-Oh erre is külön szövegi logikát használ: például az „and”, „then”, „and if you do”, „also” eltérően hat arra, hogy az egyik művelet sikertelensége leállítja-e a másikat. ([yugioh-card.com][4])

És szerintem az AETERNÁ-nak is szüksége lesz ugyanerre az elvre, még ha nem is ugyanezekkel a szavakkal.

---

# Ez alapján pontosítanám a rendszert

A korábbi felosztásom túl egyszerű volt.

Nem csak:

```text
TIMING SYSTEM
+
SUBJECT-SPECIFIC RULES
```

hanem inkább:

```text
1. RESPONSE / PRIORITY SYSTEM
   mikor lehet reagálni?
   mi válaszolhat mire?
   milyen sorrendben oldódik?

2. RESOLUTION ENTRY MODEL
   mi került a stackre?
   mi a source?
   mi van előre rögzítve?

3. BINDING / SELECTION MODEL
   locked target?
   dynamic selector?
   reselect?
   több target?

4. REVALIDATION MODEL
   mit ellenőrzünk újra resolutionkor?

5. INVALIDATION POLICY
   ha valami már nem érvényes:
   - teljes fizzle?
   - csak azt a részt hagyjuk ki?
   - más target?
   - current eligible object keresése?

6. EFFECT DEPENDENCY MODEL
   A után B
   A és B
   A sikeres → B
   A-tól függetlenül B

7. POST-RESOLUTION / TRIGGER CHECKPOINT
```

Ez már tényleg egy **általános AETERNA timing/resolution framework** lehetne.

És nem csak Igére.

Ugyanezt használhatná:

```text
Rituálé
Entitás aktivált képessége
triggerelt képesség
Jel
támadás
védelmi közbelépés
Pecsét interaction
Burst
kényszerített action
későbbi Expansion mechanikák
```

---

## A te példádat ezért én három külön AETERNA-kártyává tudnám alakítani

Ez jól szemlélteti, mekkora design-teret kapunk.

**1. Dinamikus**

> „Semmisítsd meg az ellenfeled legalacsonyabb ATK-jú Entitását.”

A rendszer ezt úgy értheti:

```text
selector = lowest_ATK
selection_time = resolution
```

Az ATK-buff után az új legalacsonyabb pusztul.

---

**2. Célzó**

> „Válaszd ki az ellenfeled legalacsonyabb ATK-jú Entitását. Semmisítsd meg azt.”

```text
selection_time = activation
binding = locked
revalidation = lowest_ATK_required
```

Ha közben már nem legalacsonyabb:

```text
effect invalidated
```

---

**3. Megjelölt áldozat**

> „Válaszd ki az ellenfeled legalacsonyabb ATK-jú Entitását. Semmisítsd meg a kiválasztott Entitást.”

Ebben az értelmezésben:

```text
lowest_ATK
csak selection requirement

utána identity locked
```

Ha később nő az ATK:

```text
attól még megsemmisül
```

Három nagyon hasonló effekt-szöveg, de teljesen eltérő taktikai viselkedés.

Ezért szerintem a későbbi kártyaszöveg-szabványunknak is ezt **egyértelműen kifejezhetővé kell tennie**.

---

És szerintem most találtunk egy fontosabb tervezési szintet, mint a konkrét Combat edge case.

A következő kérdést ezért még nem úgy tenném fel, hogy:

> „Mi történjen, ha a védő eltűnik?”

Hanem:

> **Milyen általános „binding + revalidation + invalidation” kategóriákat engedjen az AETERNA?**

Ha ezt jól definiáljuk, akkor a védő eltűnése, az ATK megváltozása, az Ige targetjének eltűnése és egy Entitás aktivált képességének source-vesztése **mind ugyanannak az általános rendszernek külön esete lesz**.

Ez szerintem sokkal közelebb visz ahhoz az egységes timing engine-hez, amit most keresünk.

[1]: https://www.yugioh-card.com/eu/wp-content/uploads/2022/07/Rulebook_v9_en.pdf?utm_source=chatgpt.com "OFFICIAL RULEBOOK"
[2]: https://www.yugioh-card.com/en/play/psct/psct-4/?utm_source=chatgpt.com "Problem-Solving Card Text, Part 4: The Clues on Your Cards – Yu-Gi-Oh! TRADING CARD GAME"
[3]: https://img.yugioh-card.com/ygo_cms/ygo/all/uploads/Rulebook_v9_en.pdf?utm_source=chatgpt.com "OFFICIAL RULEBOOK"
[4]: https://www.yugioh-card.com/en/play/psct/psct-7/?utm_source=chatgpt.com "Problem-Solving Card Text, Part 7: 2012 Update – Conjunction Functions – Yu-Gi-Oh! TRADING CARD GAME"


--rendben van
akkor probáljuk meg ezt felépiteni most
viszont ne felejtsük el hogy merre felé kellene tartani az irányt--

Igen. És közben **nem térünk le a Combat + Pecsét irányról**. Ezt az általános rendszert azért építjük meg most, mert kiderült, hogy nélküle a Combatnál ugyanazokat a problémákat egyenként újra meg újra megoldanánk.

A jelenlegi irányt így tartom fejben:

* Reaction / Priority v1 marad az alap; **nem dobjuk ki, hanem általánosítjuk**.
* A következő nagy gameplay cél továbbra is **Combat + Pecsét**.
* A védekezés erős munkakoncepciója: **szomszédos Áramlatból történő alap-védelem + képességgel/kulcsszóval kiterjeszthető hatótáv**.
* „Intercept” és „Guardian” csak elemzési munkaszavak, **nem AETERNA-nevek**.
* normál közbelépésnél a támadás ott ér véget; **Hasítás lehet explicit továbbhaladási kivétel**.
* ezek még playtest előtt álló munkairányok, nem végleges szabályok.

## AETERNA Timing & Resolution Framework – első munkavázlat

Szerintem a korábbi gondolkodásunkat egy fontos módon kell továbbfejleszteni. Nem külön „targeting-típusokat” kell mereven létrehoznunk, hanem **egymástól független tulajdonságokat**.

Egy resolution entry nagyjából így nézne ki:

```text
Resolution Entry
│
├─ Source
├─ Subject / Target / Selection
├─ Binding
├─ Revalidation requirements
├─ Effect dependency
├─ Failure / fallback policy
└─ Resolution outcome
```

Ez azért jobb, mert ugyanaz az alapmodell használható Igére, Rituáléra, Entitás-képességre, támadásra és később Pecsét-interakcióra is.

---

# 1. Egy szabályosan létrejött entry ne „tűnjön el”

Ezt első foundation-elvnek javaslom.

Ha valami szabályosan bekerült a feloldási sorba:

```text
E1
→ E2 válasz
→ E3 válasz
```

akkor LIFO:

```text
E3
E2
E1
```

Ha E3 miatt E2 már nem végrehajtható, **E2 nem törlődik visszamenőleg**.

Hanem:

```text
E2 sorra kerül
→ revalidation
→ invalidated / no effect / partial / stb.
→ lifecycle lezárul
```

Ez replay, determinisztika és UI szempontból is sokkal jobb.

Később lehet explicit olyan hatásunk, hogy „semmisíts meg / érvényteleníts egy függő hatást”, de az is inkább:

```text
entry.status = cancelled
```

legyen, ne történeti eltüntetés.

---

# 2. Selection Time – mikor dől el, mire hat?

Ez az egyik legfontosabb tengely.

### `selection_at_declaration`

A célpont már az aktiválás/deklarálás során rögzül.

```text
Válassz egy Entitást.
→ target = E1
→ ReactionWindow
→ ...
→ E1 marad a kötött objektum
```

### `selection_at_resolution`

Nem választunk konkrét objektumot előre.

```text
"Az ellenfeled legalacsonyabb ATK-jú Entitása..."
```

Resolutionkor:

```text
current state
→ calculate eligible set
→ find lowest ATK
→ apply
```

Ebben a modellben a példádban az effekt **nem célt vált**.

Nem volt még végleges célpontja.

---

# 3. Binding – mi rögzül?

Ez külön kérdés a selection time-tól.

### `identity_locked`

Konkrét objektumhoz kötődik:

```text
card_instance_123
```

Nem:

```text
"valamilyen megfelelő Entitás"
```

Ha az objektum később alkalmatlanná válik, nem ugrunk automatikusan másikra.

### `dynamic_query`

Nem konkrét identity, hanem egy lekérdezés kötődik az entryhez:

```text
opponent
AND entity
AND domain
ORDER BY atk ascending
TAKE 1
```

Resolutionkor az **aktuális állapoton** fut.

Ez adja a példád dinamikus változatát.

---

# 4. Revalidation – mit kell újra ellenőrizni?

Ez szerintem különösen fontos, mert nem minden aktiválási feltételnek kell resolutionkor is igaznak maradnia.

Vegyük:

> „Válaszd ki az ellenfél legalacsonyabb ATK-jú Entitását.”

Aktiváláskor E1 = 1000 ATK.

Közben E1 → 2000 ATK, E2 = 1500.

Három külön effect létezhet.

### A. A „legalacsonyabb” csak kiválasztási feltétel

```text
activation:
E1 legal
→ identity_locked = E1

resolution:
E1 még létezik?
E1 még ellenfél Entitása?
igen

→ E1 megsemmisül
```

Nem érdekel, hogy már nem ő a legalacsonyabb.

### B. A „legalacsonyabb” folyamatos resolution-feltétel

```text
activation:
E1 legal
→ target = E1

reaction:
E1 → 2000 ATK

resolution:
E1 még legalacsonyabb?
nem

→ target invalid
```

De:

**nem ugrik E2-re automatikusan.**

### C. Dinamikus selection

```text
nincs locked target

resolution:
ki MOST a legalacsonyabb?

→ E2
→ E2 megsemmisül
```

Ez három teljesen külön mechanika.

---

# 5. Nincs implicit retarget

Ezt elég erős foundation-szabálynak érzem:

> **Egy locked target érvénytelenné válása önmagában soha nem jogosítja fel az effectet arra, hogy másik targetet válasszon.**

Tehát:

```text
E1 target invalid
```

nem jelentheti automatikusan:

```text
akkor keressünk E2-t
```

Retarget/reselect csak akkor legyen, ha maga a képesség kifejezetten rendelkezik erről:

```text
fallback = explicit_reselection
```

Ez rengeteg későbbi bizonytalanságot megszüntetne.

---

# 6. A Source-ot ugyanilyen módon kell kezelni

Nem csak a target változhat.

Példa:

```text
Entitás E1:
"Kimerítés: okozz 3 sebzést."
```

Aktiválja.

Erre válaszként E1 megsemmisül.

Két lehetséges képességtípusunk lehet.

### Önállósult képesség

```text
activation legal
→ ability entry létrejött
→ source később eltűnhet
→ ability továbbra is feloldódik
```

Ez a klasszikus „a kilőtt nyílvessző attól még repül” modell.

### Source-dependent képesség

Például:

> „Amíg ez az Entitás a Horizonton van, ...”

vagy:

> „Ennek az Entitásnak az aktuális ATK-jával egyenlő sebzés...”

Itt szükség lehet:

```text
source_presence_required
```

vagy:

```text
source_current_value_required
```

Tehát a source-nak is lesz **revalidation policyje**.

---

# 7. Az értékeknél is kell snapshot vs current

Ez egy később nagyon fontos rész lesz.

Példa:

> „Okozz ennek az Entitásnak az ATK-jával egyenlő sebzést.”

E1 aktiváláskor:

```text
ATK = 4
```

válasz után:

```text
ATK = 7
```

Mit használunk?

Két külön képesség lehetséges.

### Snapshot value

```text
activation:
captured_atk = 4

resolution:
damage = 4
```

### Current value

```text
resolution:
read source.current_atk

damage = 7
```

Tehát nemcsak identityt, hanem **értéket is lehet bindingolni**.

Ezért az általános fogalom szerintem nem pusztán targeting, hanem:

> **Binding**

---

# 8. Effect dependency – mi függ mitől?

Ez a másik hatalmas terület.

Példa:

> „Semmisíts meg egy Entitást, majd húzz két lapot.”

Ha az Entitás már nem semmisíthető meg, mi lesz a húzással?

Nem akarom a Yu-Gi-Oh PSCT-t lemásolni, de ugyanazt a problémát nekünk is ki kell tudnunk fejezni.

Szerintem legalább ilyen kapcsolatok kellenek.

### Független

```text
A
AND
B
```

Ha A nem hajtható végre, B még igen.

### Függő

```text
A
IF SUCCESS → B
```

A sikertelen → B sem történik.

### Szekvenciális, de nem sikerfüggő

```text
A
THEN
B
```

A-t megkíséreljük, majd B-t is.

### Atomic package

```text
A + B
```

csak akkor hajtható végre, ha az egész csomag legális.

Ez különösen payment/cost esetén lesz fontos.

---

# 9. Resolution outcome

Egy entry feloldásának ne csak `success/fail` állapota legyen.

Első körben szerintem ezek kellenek:

```text
resolved
resolved_partial
resolved_no_effect
invalidated
cancelled
```

Például:

### `resolved`

Minden elvárt rész megtörtént.

### `resolved_partial`

Több független effectből csak némelyik volt végrehajtható.

### `resolved_no_effect`

Az entry szabályosan megpróbált feloldódni, de már nem tudott érdemi változást okozni.

### `invalidated`

Valamilyen kötelező resolution-feltétel megszűnt.

### `cancelled`

Egy másik explicit szabály/képesség mondta:

```text
"ez a függő hatás ne oldódjon fel"
```

Ezeket később finomíthatjuk.

---

# 10. Resolution algoritmus

Most már összeáll egy általános folyamat:

```text
ENTRY SORRA KERÜL
        ↓
1. cancelled/replaced?
        ↓
2. source revalidation
        ↓
3. locked object revalidation
        ↓
4. dynamic selector evaluation
        ↓
5. cardinality / legality
        ↓
6. effect dependency evaluation
        ↓
7. complete execution plan
        ↓
8. atomic preflight
        ↓
9. authoritative commit
        ↓
10. resolution outcome
        ↓
11. post-resolution trigger checkpoint
```

És itt különösen jó, hogy a Reaction v1-ben már létrehoztuk a **szimulált, evolving state-en történő előzetes tervezést**.

Tehát nem dobjuk ki az eddigi munkát.

Éppen ellenkezőleg:

```text
Reaction v1 transactional closure
        ↓
általános Resolution Framework
```

irányba bővíthetjük.

---

# 11. És most kössük vissza a Combatra

Vegyük a problémás példánkat.

```text
Attacker A
→ Pecsét 3

szomszédos Horizontból
Defender B közbelép
```

A combat pending objektum tárolhatná például:

```text
original_target = Seal_3
attacker = A
defender = B
```

Mindegyik **locked identity**.

Utána ReactionWindow.

Egy reakció:

```text
B → Hand
```

Resolution előtt:

```text
REVALIDATE

A még támadásra releváns?
Seal_3 még fennáll?
B még jogosult defender?
```

B:

```text
nem
```

Innen **nem a timing framework találja ki**, hogy mi történjen.

A Combat szabály adja meg az invalidation policyt.

Például majd dönthetünk:

```text
defender invalid
→ defense invalidated
→ original attack resumes
```

vagy valami más.

De a motor ugyanazt az infrastruktúrát használja, mint az előbbi ATK-példa.

Ez volt a cél.

---

# 12. Pecsét esetén ugyanez

Tegyük fel:

```text
Attack → Seal_3
```

és Reaction során valami más effekt már feltöri Seal_3-at.

Feloldáskor:

```text
original_target = Seal_3
revalidation:
standing == false
```

Combat szabály:

```text
target invalid
→ attack resolution policy
```

Ugyanaz a rendszer.

---

# 13. Ige esetén ugyanez

```text
Ige → Entity E1
```

Reaction során:

```text
E1 elhagyja a Domaint
```

Resolution:

```text
locked target revalidation
→ invalid
→ effect policy
```

Megint ugyanaz.

---

## Szerintem tehát már van egy használható első foundationünk

Munkanéven:

### **AETERNA Timing & Resolution Framework v0.1**

Nem canonical contract még.

A legfontosabb elvei:

```text
1. Legálisan létrejött resolution entry megmarad és resolution attemptet kap.

2. Selection time külön tulajdonság.

3. Identity binding és dynamic query külön fogalom.

4. Activation legality és resolution legality külön fogalom.

5. Source és target is kaphat revalidation policyt.

6. Érték lehet snapshot vagy current-state olvasás.

7. Nincs implicit retarget.

8. Explicit reselection megengedhető.

9. Effect-részek közti dependency explicit.

10. Invalid/partial/no-effect/cancelled outcome külön kezelhető.

11. Resolution előtt teljes preflight.

12. Commit után trigger checkpoint.

13. Ugyanez a framework szolgálja az Igét, Rituálét,
    abilityt, Combatot és Pecsétet.
```

### És az irányt sem veszítettük el

Ezt én most nem engedném újabb többhetes általános rendszertervezéssé válni.

A cél:

```text
Timing/Resolution minimum
        ↓
Combat + Pecsét használja
        ↓
szomszédos védelmi mechanika
        ↓
combat ReactionWindowok
        ↓
játszható Combat foundation
```

Tehát **csak annyi általános timing-rendszert építünk most meg koncepcionálisan, amennyi ahhoz kell, hogy ne kelljen a következő tíz mechanikánál újra feltalálni ugyanezt.**

A következő egyetlen kérdés szerintem most az legyen, hogy **hogyan értelmezze alapértelmezésben az AETERNA kártyaszöveg a célkiválasztást**: mi legyen a különbség a „válassz/célozz meg egy…” és az olyan megfogalmazás között, mint „az ellenfél legalacsonyabb ATK-jú Entitása…”. Ez dönti el a `locked target` és `dynamic selector` természetes nyelvi határát, és utána a többi revalidation-szabályt már erre tudjuk felépíteni.


--rendben van
elfogadom amit irtál egy dologgal kiegésziteném a ReactionTimingWindow kimaradt szerintem a tervezésből de lehet tévedek
bizonyos helyzetekben fontos hogy a játékos döntsön például hogy aktiválja a képességet vagy sem
folytathatjuk a munkát tovább--

Igazad van: a **ReactionTimingWindowot túlzottan belesűrítettem a „Response / Priority System” fogalmába**, pedig külön, elsőrendű elemként kell szerepelnie. Különösen azért, mert nemcsak azt kell eldönteni, hogy *mi reagálhat mire*, hanem azt is, hogy **a játékos kap-e egyáltalán döntési lehetőséget egy adott pillanatban, és ha igen, mit tehet vagy mit utasíthat vissza**.

A már elkészült Reaction/Priority v1-et ez nem érvényteleníti. Inkább most kezdjük pontosabban megfogalmazni azt az általános rendszert, aminek a ReactionWindow az egyik végrehajtási eleme.

## Timing & Resolution Framework v0.2

Én most így választanám szét a fogalmakat:

```text
GAME EVENT / DECLARATION
        ↓
TIMING POINT
        ↓
kell-e interaktív döntés?
        ↓ igen
REACTION TIMING WINDOW
        ↓
PRIORITY
        ↓
legal options:
- képesség aktiválása
- reakció kijátszása
- speciális akció
- pass
        ↓
WINDOW CLOSE
        ↓
STACK / RESOLUTION
        ↓
REVALIDATION
        ↓
RESOLUTION
        ↓
POST-RESOLUTION TIMING POINT
```

Tehát három külön fogalom van.

### 1. Timing Point

Ez egyszerűen egy olyan meghatározott játékszabályi pillanat, amelyhez valamilyen reakció vagy döntés kapcsolódhat.

Például:

```text
attack_declared
block_declared
card_played
ability_activated
entity_destroyed
seal_broken
card_entered_void
combat_resolved
```

**Nem minden game event automatikusan Timing Point.**

Ez fontos, mert különben minden apró state-változás megszakítaná a játékot.

---

### 2. Reaction Timing Window

A Timing Point után akkor nyílik, ha a szabály szerint valakinek lehetősége van dönteni.

Itt jelenik meg pontosan az, amit mondtál:

> „aktiválom a képességet vagy nem?”

Például egy Entitás:

> „Amikor az ellenfeled támadást deklarál, megteheted, hogy Kimeríted ezt az Entitást: a támadó -2 ATK-t kap a harc végéig.”

Attack declaration:

```text
Attack declared
        ↓
Timing Point: after_attack_declaration
        ↓
Reaction Timing Window
        ↓
játékosnak megjelenik:

[A képesség aktiválása]
[Pass]
```

Ha aktiválja:

```text
ability → resolution stack
```

Ha nem:

```text
pass
```

és az adott lehetőség később **lejárhat**.

Ez utóbbi nagyon fontos.

Nem mondhatja három eseménnyel később:

> „Ja, az attack declarationre reagáló képességemet mégis használom.”

A window lezárásával elveszett az adott alkalom.

---

## 3. Priority

A ReactionTimingWindow és a Priority sem ugyanaz.

A window azt mondja:

> **„Most lehet reagálni.”**

A priority pedig:

> **„Most ki dönthet?”**

Például:

```text
ReactionTimingWindow nyitva

P1 priority
→ react vagy pass

P2 priority
→ react vagy pass

ha reakció történt:
→ priority szabály szerint folytatódik

ha szükséges pass-feltétel teljesül:
→ window close
```

Ez lényegében már benne van a Reaction v1-ben; most csak magasabb szintű timing-rendszerbe helyezzük.

---

# Nagyon fontos: nem minden „képesség aktiválása” ugyanaz

Szerintem itt kell most egy nagyon fontos különbséget bevezetnünk.

Legalább három eset létezik.

### A. Szabadon aktiválható képesség

Például:

> „Kimerítés: húzz 1 lapot.”

Ennek lehetnek activation timing szabályai:

```text
saját Manifesztáció
+ megfelelő state
+ nincs tiltás
```

Nem azért jelenik meg, mert történt egy trigger event.

A játékos maga indítja.

---

### B. Opcionális triggered képesség

Például:

> „Amikor egy saját Entitás megsemmisül, megteheted, hogy húzol 1 lapot.”

Itt:

```text
Entity destroyed
↓
matching trigger detected
↓
Reaction/Trigger Timing Window
↓
[Activate]
[Decline]
```

A játékos **dönt**.

Ez pontosan az a rész, amit jogosan hiányoltál.

---

### C. Kötelező triggered képesség

Például:

> „Amikor ez az Entitás megsemmisül, okozz 2 sebzést...”

Ha nincs benne opcionális elem:

```text
trigger condition true
↓
trigger automatikusan létrejön / queued
```

Nem kérdezzük:

```text
"Aktiválod?"
```

mert nem opcionális.

De később lehet szükség további döntésre:

```text
"válassz célpontot"
```

Ez **nem activation decision**, hanem egy külön choice/pending decision.

Ez a különbség fontos lesz a UI-nak és az engine-nek is.

---

# Ezért az optionalitást sem raknám a kártyaszöveg-kezelés perifériájára

Az ability runtime-nak tudnia kellene legalább:

```text
activation_mode:
    manual
    optional_trigger
    mandatory_trigger
```

és külön:

```text
timing_condition
```

Például:

```text
activation_mode = optional_trigger
timing_condition = after_attack_declared
```

vagy:

```text
activation_mode = manual
timing_condition = manifestation_priority
```

Ez sokkal tisztább, mint mindenre egyszerűen azt mondani:

```text
reaction ability
```

---

# És itt jutunk el a saját „Spell Speed”-szerű rendszerünkhöz

Szerintem még **nem kell sebességi szinteket számoznunk**.

Előbb azt kell megmondanunk, hogy egy adott ReactionTimingWindow **milyen reakcióosztályokat fogad el**.

Például egy későbbi adatmodellben:

```text
TimingWindow:
    anchor = attack_declared
    allowed_response_classes:
        - normal_reaction
        - combat_reaction
```

Egy képességnél pedig:

```text
response_class = combat_reaction
```

Így az engine egyszerűen kiszámolja:

```text
window.allowed_classes
∩
player.available_abilities
=
legal reaction options
```

Ez funkcionálisan ugyanazt a problémát kezeli, mint a Yu-Gi-Oh Spell Speed, de nem kell a Yu-Gi-Oh háromfokozatú rendszerét lemásolnunk.

Később, ha valóban szükségünk lesz rá, lehet például:

```text
normal
fast
exclusive
```

vagy teljesen más AETERNA-specifikus osztályozás.

De ezt **nem dönteném el addig, amíg nincs rá konkrét szabályigény**.

---

# Van még egy fontos rész: Decline ≠ Pass

Elsőre ugyanannak tűnnek, pedig szerintem nem azok.

Vegyük ezt:

> „Amikor egy saját Entitás megsemmisül, megteheted, hogy húzol 1 lapot.”

A játékos kap egy opcionális triggert.

Ha azt mondja:

```text
Decline
```

akkor az adott triggerlehetőségről mondott le.

De ettől ugyanabban a ReactionTimingWindowban **még lehet más reakciója**.

Például:

```text
Optional ability A → decline

de

Ige B → activate
```

Ezzel szemben:

```text
Pass Priority
```

jelentése:

> „Ebben a priority opportunityben jelenleg semmilyen elérhető actiont nem teszek.”

Ezért én belsőleg külön kezelném:

```text
decline_option(option_id)
```

és

```text
pass_priority
```

A játékos UI-ban ettől még lehet egyszerű.

---

# És egy opcionális trigger csak egyszer ajánlható fel

Ez is fontos.

```text
Entity destroyed
→ optional trigger T created
```

Ha a játékos:

```text
decline T
```

akkor T:

```text
expired
```

Ne történhessen:

```text
pass
→ opponent reacts
→ priority visszajön
→ "akkor mégis aktiválom T-t"
```

**ha az adott képesség szabálya szerint az egyszeri trigger decision már lezárult.**

Viszont ez még külön designkérdés: bizonyos rendszerek megengedik, hogy a teljes timing window alatt bármikor aktiváld a rendelkezésre álló triggered optiont, amíg nem zárul az ablak.

Tehát itt két lehetséges modellünk lesz később:

```text
A) one-shot offer
trigger megjelenik
→ most döntesz
→ activate/decline
```

vagy:

```text
B) window-lived option
trigger megjelenik
→ addig marad legal option,
  amíg a window le nem zárul
```

**Ezt még nem dönteném el.**

Nagyon hasonló kérdés ahhoz, hogy a Yu-Gi-Oh trigger/fast-effect időzítése hogyan kezeli az aktiválási lehetőségeket, ezért ezt majd érdemes külön összehasonlítanunk.

---

## A teljes v0.2 modell így néz ki

```text
┌─────────────────────────────┐
│ EVENT / ACTION DECLARATION  │
└──────────────┬──────────────┘
               ↓
        TIMING POINT
               ↓
     trigger collection
               ↓
┌─────────────────────────────┐
│ REACTION TIMING WINDOW      │
│                             │
│ - mandatory triggers        │
│ - optional trigger options  │
│ - manual legal responses    │
│ - special legal responses   │
│ - priority                  │
│ - pass / decline            │
└──────────────┬──────────────┘
               ↓
         WINDOW CLOSE
               ↓
┌─────────────────────────────┐
│ RESOLUTION STACK            │
└──────────────┬──────────────┘
               ↓
       ENTRY REVALIDATION
               ↓
          RESOLUTION
               ↓
           OUTCOME
               ↓
      POST-RESOLUTION
        TIMING POINT
```

Ez már szerintem valóban olyan alap, amelyre rá tudjuk kötni:

```text
Ige
Rituálé
Entitás-képesség
Jel
támadás
védelmi közbelépés
Pecsét
Burst
triggerelt képességek
```

anélkül, hogy minden mechanikához külön timing-rendszert írnánk.

## Innen folytatnám az előző kérdésünket

Most, hogy a ReactionTimingWindow a helyére került, visszatérhetünk a **binding / target selection** részhez.

Az első igazán fontos szabály szerintem az legyen:

> **Az AETERNA-ban mi különböztesse meg természetes kártyaszövegben a deklaráláskor rögzített célpontot a feloldáskor dinamikusan meghatározott érintett objektumtól?**

Mert például ez:

> „Válassz egy ellenfél által irányított Entitást…”

nagyon természetesen `identity_locked`.

Míg:

> „Az ellenfeled legalacsonyabb ATK-jú Entitása…”

nagyon természetesen lehet `dynamic_selector`.

Ha ezt a nyelvi és mechanikai határt jól rakjuk le, utána már pontosan meg tudjuk oldani azt a példát is, amivel az egész kérdés előjött: **mi történjen, ha a lánc közben megváltoztatja az ATK-sorrendet.**


--a példám nem volt a legjobb és ezért mondok inkább egy másikat 
amugy szerintem a yugioh rendszert elemezzük mégjobban mert szinte minden kérdésünkre lehet ott válasz föleg ha találunk az interneten konkért Duelek szöveges replayeit mert ott láthatjuk mi történt
a példa ami talán kicsit jobb maradunk yugiohban
ha nekem van egy csapda lapom ami aktiválási feltétele hogy "amikor az ellenfél leidéz egy szörnyet..." akkor minden alkalommal feldobja a rendszer hogy akarom e aktiválni a kártyát 
ez nagyon idegesitö szokottt lenni DE SZÜKSÉGES ez egy fontos elem mert a játékos dönti el mikor van a legmegfelelőbb pillanat az aktiválásra

tehát ha kell még keresek példákat de szerintem most az lenne a legjobb ha mégjobban kielemeznénk a ezeket a rendszereket a yugiohban
mivel más játékokat nem ismerek ennyire mélyrehatóan ezért lehet hogy vannak jó megoldások a többiben is igy majd ott is kell vizsgálodni--

Igen, ez a példa jobb, mert rámutat egy hibára a korábbi modellünkben: **összemostam az opcionális triggerelt képességet az olyan reakcióval, amelynek egy esemény csak az aktiválási időablakát nyitja meg.** A Yu-Gi-Oh! ezt a kettőt külön kezeli, és szerintem ezt nekünk is érdemes lesz különválasztani.

Most mélyebben átnéztem a hivatalos Yu-Gi-Oh! timing-, Chain-, Spell Speed- és PSCT-rendszert. Találtam konkrét hivatalos láncpéldákat is, valamint nyilvános Master Duel duel logokat/replayeket; utóbbiakat inkább gyakorlati ellenőrzésre érdemes használni, a rules authority továbbra is a Konami szabályanyag legyen.

## A csapdalapos példád pontosan hogyan működik?

Vegyük a hivatalos **Torrential Tribute** szövegét:

> `When a monster(s) is Summoned: Destroy all monsters on the field.`

Ez Normal Trap. ([db.yugioh-card.com][1])

A fontos rész az, hogy egy normál idézés **maga nem indít Chaint**. A Fast Effect Timing szabály szerint a Normal Summon, a Chain nélkül történő Special Summon, sőt a támadás deklarálása is olyan akció, amely után a játék „open” állapota megszűnik, és meg kell vizsgálni az arra reagáló effekteket. ([Yu-Gi-Oh! Kártyák][2])

Ezért a folyamat leegyszerűsítve:

```text
OPEN GAME STATE

ellenfél:
Normal Summon

↓
a Summon sikeresen megtörtént
↓
SUMMON TIMING POINT

↓
van-e erre trigger?
↓
trigger effektek összegyűjtése

↓
FAST-EFFECT RESPONSE OPPORTUNITY

Torrential Tribute legal?
igen

↓
játékos dönt:
ACTIVATE
vagy
nem aktiválja

↓
ha aktiválja:
Chain épül
```

Pontosan ezért érzed szükségesnek a Master Duel idegesítő kérdezgetését.

**A digitális kliensnek nem szabad kitalálnia helyetted, hogy „ezt biztos nem akarod most használni”.**

A játékos stratégiai döntése lehet például:

```text
első Summon
→ nem használom

második Summon
→ nem használom

ellenfél kirakja a kulcsfontosságú harmadik Entitást
→ MOST használom
```

Ha a program nem kínálná fel a lehetőséget a megfelelő időpontban, akkor gyakorlatilag **játékosi döntést venne el**.

Ez az AETERNA szempontjából nagyon fontos.

---

# És most jött az első lényeges korrekció a saját modellünkhöz

Korábban ezt írtuk:

```text
optional_trigger
mandatory_trigger
manual
```

Ez **nem elég**.

A Yu-Gi-Oh alapján legalább két egészen különböző opcionális mechanika létezik.

### Opcionális Trigger

Például:

```text
"When this card is Summoned:
You can..."
```

Az esemény maga **létrehozza a trigger lehetőségét**.

A rendszer nagyjából:

```text
EVENT
↓
trigger condition matched
↓
Trigger Candidate
↓
Activate?
```

Ha elmulasztod a megfelelő trigger-aktiválási lehetőséget, azt a konkrét triggert később már nem használod fel tetszőlegesen.

### Feltételes reakció

A Torrential Tribute más jellegű.

A Trap egy **Spell Speed 2 fast effect**, amelynek az aktiválásához most teljesült a feltétel:

```text
When a monster is Summoned
```

Nem ugyanúgy „automatikusan létrejövő trigger object”.

Hanem:

```text
Summon happened
↓
jelenlegi Timing Window megfelel a Trap feltételének

Torrential Tribute
= legal response option
```

A hivatalos Fast Effect Timing külön kezeli a Trigger Effecteket és az utánuk használható fast effecteket. ([Yu-Gi-Oh! Kártyák][2])

**Ez óriási különbség az AETERNA számára.**

---

# A Yu-Gi-Oh valójában több rétegből építi fel a timingot

Az eddig vizsgált szabályokat szétszedve ezt látom:

| Réteg                | Yu-Gi-Oh feladata                    | AETERNA szempontjából             |
| -------------------- | ------------------------------------ | --------------------------------- |
| Game state           | open / nem open                      | mikor lehet normál akciót kezdeni |
| Timing event         | summon, attack declaration stb.      | mire reagálhat valami             |
| Trigger collection   | esemény által kiváltott effektek     | Riadó/Visszhang/stb.              |
| Activation condition | most használható-e a lap/ability     | opcionális reakció                |
| Priority             | ki dönthet következőnek              | már van Reaction v1-ben           |
| Spell Speed          | mi mire válaszolhat                  | saját response-class kellhet      |
| Chain construction   | válaszok összegyűjtése               | Reaction stack                    |
| Chain resolution     | LIFO                                 | már megvan                        |
| Resolution semantics | target/source/feltétel újraértékelés | most tervezzük                    |
| Aftermath            | új trigger események                 | checkpoint                        |

És ezek **nem ugyanazok a fogalmak**.

---

# 1. Az „open game state” szerintem különösen értékes ötlet

A Yu-Gi-Oh hivatalos timing-chart szerint vannak pillanatok, amikor a játékállapot „open”.

Ilyenkor az aktuális játékos szabadon végezhet megfelelő normál akciókat: summon, attack declaration, Ignition Effect stb. Amint bárki csinál valamit, a state már nem open. Csak akkor válik újra openné, ha a szükséges reakciós lehetőségek lezajlottak és mindkét játékos továbbengedte a játékot. ([Yu-Gi-Oh! Kártyák][2])

Ez az AETERNA-ban valahogy így nézhetne ki:

```text
OPEN STATE
↓
aktív játékos:
attack / play card / ability / advance stb.

↓
ACTION / DECLARATION

↓
TIMING PROCESSING

↓
REACTION WINDOW

↓
RESOLUTION

↓
AFTERMATH

↓
ha nincs további kötelező/pending folyamat

OPEN STATE
```

Ez valójában nagyon szépen ráilleszthető a már elkészült fázis- és legal-action rendszerünkre.

---

# 2. Egy esemény után előbb a triggereket kell összeszedni

Ez fontos Yu-Gi-Oh szabály.

Ha egy Chain nélküli akció történik, például egy Normal Summon vagy attack declaration, a rendszer először megvizsgálja, keletkeztek-e Trigger Effectek. Csak utána lép tovább a gyors válaszok felé. ([Yu-Gi-Oh! Kártyák][2])

Ráadásul több egyszerre kiváltott trigger esetén külön Chain-építési szabály létezik. A hivatalos rulebook korábbi részletes változata ezt így rendezi:

```text
turn player mandatory
↓
opponent mandatory
↓
turn player optional
↓
opponent optional
```

azonos kategórián belül pedig a játékos határozhatja meg saját effektjei sorrendjét. ([Yu-Gi-Oh! Kártyák][3])

Nem mondom, hogy ezt másoljuk.

De az alapelv nagyon értékes:

> **Trigger collection nem ugyanaz, mint a szabad Reaction Priority.**

AETERNA-ban is lehet majd:

```text
EVENT
↓
collect triggered obligations/options
↓
rendezzük őket
↓
ezután engedjük a szabad reakciókat
```

---

# 3. Utána jönnek a gyors válaszok

A Yu-Gi-Oh Spell Speed rendszere ezt korlátozza.

Hivatalosan:

```text
Spell Speed 1
→ normál esetben nem válaszolhat más effectre

Spell Speed 2
→ válaszolhat Speed 1-re és 2-re

Spell Speed 3
→ bármire válaszolhat
→ rá csak Speed 3 válaszolhat
```



Ez érdekes számunkra, de továbbra sem gondolom, hogy:

```text
AETERNA Speed 1
AETERNA Speed 2
AETERNA Speed 3
```

rendszert kellene csinálnunk.

A tanulság inkább:

> **A timing eligibility és a response compatibility két külön tulajdonság.**

Egy képesség lehet például:

```text
timing:
    after_entity_manifested

response_class:
    normal
```

egy másik:

```text
timing:
    when_effect_activated

response_class:
    counter
```

és majd később eldöntjük, milyen osztályokra van ténylegesen szükség.

---

# 4. Chain építés és Chain feloldás két teljesen külön fázis

Ez talán az egyik legfontosabb Yu-Gi-Oh tulajdonság.

Először:

```text
Chain Link 1
↓
válasz
Chain Link 2
↓
válasz
Chain Link 3
↓
...
↓
mindketten kész
```

**Csak ezután kezdődik a feloldás.**

És:

```text
CL3 resolve
↓
CL2 resolve
↓
CL1 resolve
```



Még fontosabb: Konami egy hivatalos Exosister szabályanyagban egészen explicit kimondja, hogy **Chain feloldása közben semmilyen új lap vagy effect nem aktiválható**. ([Yu-Gi-Oh! Kártyák][4])

Ez nagyon érdekes, mert a Reaction v1-gyel mi is lényegében ebbe az irányba mentünk:

```text
reakciók összegyűjtése
↓
window close
↓
LIFO unwind

és nincs közben új külső ReactionWindow
```

Ez tehát valószínűleg **jó alapelv**.

---

# 5. A közbenső Chain Link megváltoztatja az állapotot

És erre találtam egy tökéletes **hivatalos Konami-példát**.

A PSCT oktatóanyagban:

```text
CL1:
Trident Warrior effect

CL2:
Raigeki Break
→ target egy monster

CL3:
Gemini Spark
→ ugyanazt a monstert Tribute costként feláldozza
```

Feloldás:

```text
CL3 Gemini Spark
→ monster eltűnik

CL2 Raigeki Break
→ a target már nincs a fielden
→ semmi nem történik

CL1 Trident Warrior
→ ettől függetlenül feloldódik
```

Ez **pontosan ugyanaz a problémakategória**, amit mi most az AETERNÁ-nál felfedeztünk. ([Yu-Gi-Oh! Kártyák][5])

És nagyon fontos:

**Raigeki Break nem tűnik ki a Chainből.**

Megkapja a saját resolution attemptjét, csak már nem tudja végrehajtani a célzott műveletét.

Ez erősen támogatja a korábban megfogalmazott AETERNA-elvünket:

```text
legálisan létrejött ResolutionEntry
→ nem tűnik el
→ sorra kerül
→ revalidation
→ outcome
```

---

# 6. Az aktiválási feltétel nem feltétlenül resolution-feltétel

Ez pedig közvetlenül érinti a korábbi ATK-példádat.

Konami hivatalos PSCT-szabálya:

> az aktiválási feltételeknek alapértelmezésben az **aktiválás pillanatában** kell teljesülniük; ha resolutionkor is teljesülniük kell, azt külön jelzi a kártyaszöveg. ([Yu-Gi-Oh! Kártyák][6])

Tehát Yu-Gi-Oh-ban ténylegesen megvan az a különbség, amit mi kerestünk:

```text
ACTIVATION LEGALITY
≠
RESOLUTION LEGALITY
```

Ez szerintem szinte biztosan kell az AETERNÁ-ba is.

---

# 7. A source jelenléte sem automatikus követelmény

A legtöbb aktivált effect önállóan létezhet a Chainben.

De a kártyaszöveg előírhatja:

> ennek a lapnak továbbra is face-up állapotban kell lennie resolutionkor.

A hivatalos PSCT egyik példája a Zombie Master: a lap explicit szövege miatt source-presence szükséges; ha eltűnik, az effect nem oldódik fel megfelelően. ([Yu-Gi-Oh! Kártyák][7])

Ez nagyon pontosan megfelel annak, amit már felvázoltunk:

```text
source_policy:
    independent_after_activation
```

vagy:

```text
source_policy:
    presence_required_at_resolution
```

Ez tehát nem elméleti igényünk: egy évtizedek óta működő TCG ugyanezt a problémát explicit kezeli.

---

# 8. A költség külön lifecycle

A Yu-Gi-Oh-ban costot **aktiváláskor** kell kifizetni.

És ha később az aktiválást vagy effectet megállítják:

```text
cost
NEM jár vissza
```

A hivatalos rulebook ezt külön rögzíti. ([Yu-Gi-Oh! Kártyák][8])

Ez is nagyon fontos AETERNA-szempontból:

```text
activation cost
≠
resolution effect
```

Például:

```text
Kimerítsd ezt az Entitást:
okozz 3 sebzést
```

ha a képességet később megállítják:

```text
Kimerítés megtörtént
→ nincs refund
```

ha ezt a szabályt választjuk.

---

# 9. A target revalidation sem egyetlen globális szabály

A PSCT még finomabb.

Konami különbséget tesz például aközött, hogy resolutionkor a szöveg továbbra is:

```text
"that target"
```

módon hivatkozik az objektumra, vagy más módon. Az első esetben bizonyos targeting-követelményeket újra ellenőrizni kell; több targetnél pedig a szöveg azt is meghatározhatja, hogy egyetlen elveszett target az egész effectet érvényteleníti-e. ([Yu-Gi-Oh! Kártyák][7])

Ez pontosan azt mutatja, hogy a mi:

```text
Binding
+
Revalidation Policy
```

felosztásunk jó irány.

---

# 10. Még az egy effecten belüli műveletek függőségét is szabványosították

A Yu-Gi-Oh PSCT négy kötőszóval mondja meg, hogy két effect-rész hogyan függ egymástól:

```text
then
also
and if you do
and
```

Ezek egyszerre határozzák meg:

* az időbeli kapcsolatot;
* hogy A sikere szükséges-e B-hez;
* mit hajtunk végre, ha az egyik rész már nem lehetséges.

Például az `also` elve: amennyit lehet, hajts végre; az `and if you do` esetében A sikerétől függ B. ([Yu-Gi-Oh! Kártyák][9])

Tehát az általunk felvetett:

```text
independent
dependent_on_success
sequential
atomic
```

effect-dependency rendszernek **nagyon erős valós precedense van**.

---

# 11. Van viszont Yu-Gi-Oh-szabály, amit én egyelőre NEM másolnék

Ez az úgynevezett szigorú `When` timing / „miss the timing”.

Yu-Gi-Oh-ban bizonyos:

```text
When X happens: You can...
```

effektek csak akkor aktiválhatók, ha X volt a releváns utolsó esemény. Az effect-szövegek `then` vs. simultán kötése ezt is befolyásolhatja. ([Yu-Gi-Oh! Kártyák][10])

Ez például ilyen furcsaságokat okozhat:

```text
Summon történt
↓
de ugyanazon effectben utána még valami más történt
↓
"when Summoned" opportunity elveszett
```

A Torrential Tribute régi és jelenlegi rulingsainak jelentős része pont erről szól.

**Ezt nagyon alaposan megvizsgálnám, de nem venném át automatikusan.**

Ez a Yu-Gi-Oh egyik leghírhedtebb komplexitási pontja.

Az AETERNA valószínűleg tud ennél tisztább modellt alkotni, például explicit:

```text
trigger_scope = immediate_after
```

vagy:

```text
trigger_scope = next_checkpoint
```

anélkül, hogy természetes nyelvi `when/if` különbségből kellene rulingsot megfejteni.

---

# És vissza a te csapdalapos példádhoz: találtunk még egy fontos dolgot

Korábban felvetettem:

> ha egyszer megkérdezi a rendszer, és nemet mondasz, az option rögtön járjon-e le?

Most már azt mondom: **ez túl egyszerű modell lenne.**

Egy Yu-Gi-Oh-szerű rendszerben különbség van például:

```text
OPTIONAL TRIGGER
```

és:

```text
CONDITIONAL FAST RESPONSE
```

között.

Egy Torrential Tribute-szerű Trap a megfelelő response Chain építése közben akár későbbi Chain Linkként is bekerülhet; nem feltétlenül neki kell Chain Link 1-nek lennie. Egy közösségi ruling-példában például egy Summonra létrejövő Trigger Effect CL1, Torrential Tribute pedig CL2 lehet — ez összhangban áll a hivatalos timing-charttal. ([Reddit][11])

Ez azt jelenti, hogy az AETERNA-ban valószínűleg szükség lesz:

```text
OpportunityLifetime
```

fogalomra is.

Például:

```text
single_trigger_offer
```

vs.

```text
while_timing_window_open
```

Ez egy **új, valóban hasznos elem**, ami eddig hiányzott a tervezetünkből.

---

## A Master Duel „idegesítő popupja” pedig külön UI-tanulság

Az official rules nem a Master Duel UI-t definiálja, ezért ezt különválasztom.

A közösségi dokumentáció alapján Master Duelben az `ON` confirmation gyakorlatilag minden lehetséges gyors aktiválási alkalomnál kérdez, míg az `AUTO` sok ilyen promptot elnyom, ezért kényelmesebb, de bizonyos speciális időzítési lehetőségekről le lehet maradni. Ezt a játékosok rendszeresen pont azért kapcsolgatják, mert a teljes szabályosság és a prompt-fáradtság között kompromisszum van. ([Reddit][12])

Ez az AETERNA számára szerintem nagyon jó termékdesign-tanulság:

> **az authoritative engine mindig tudja és kínálja fel a valódi legal optiont; az UI kényelmi rendszere ettől külön réteg.**

Tehát később akár lehet:

```text
Always ask
Smart prompts
Auto-pass configured situations
```

de ez **nem változtathatja meg a játékszabályt**.

---

## Jelenleg így módosítanám a Timing Framework munkamodellünket

```text
OPEN GAME STATE
        ↓
ACTION / DECLARATION
        ↓
TIMING ANCHOR
        ↓
TRIGGER COLLECTION
        │
        ├─ mandatory triggers
        └─ optional trigger opportunities
        ↓
REACTION TIMING WINDOW
        │
        ├─ conditional responses
        ├─ general legal responses
        ├─ special/counter responses
        └─ priority / pass
        ↓
CHAIN / STACK COMPLETE
        ↓
LOCK NORMAL RESPONSE INPUT
        ↓
LIFO RESOLUTION
        │
        ├─ source revalidation
        ├─ target/binding revalidation
        ├─ current-state queries
        ├─ effect dependency
        └─ outcome
        ↓
AFTERMATH / TRIGGER COLLECTION
        ↓
ha kell:
NEW TIMING WINDOW
        ↓
egyébként:
OPEN GAME STATE
```

Ez **lényegesen pontosabb** annál, ahonnan tegnap elindultunk.

És ami különösen jó: a Reaction v1-et nem kell szétverni hozzá. A már meglévő LIFO/priority/window rendszerünk ennek a középső része; köré kell pontosabb timing-, trigger-, binding- és resolution-szemantikát építeni.

### Merre mennék innen

Még **nem térnék vissza a Combat konkrét edge case-éhez**. Egy kicsit tovább kell bontanunk a Yu-Gi-Oh rendszert, mert most látszik, hogy tényleg rengeteg választ ad.

A következő kutatási körben együtt vizsgálnám a Yu-Gi-Oh négy legnehezebb timing-esetét: **simultaneous triggers / SEGOC, „When” vs „If” és missing timing, activation negation vs effect negation, valamint target/source eltűnése vagy állapotváltozása Chain közben**. Ezekhez konkrét rulings- és duel-log példákat is keresek. Utána már lesz egy elég komplett Yu-Gi-Oh „boncolásunk”, amit össze tudunk vetni Magic/Vanguard és esetleg más TCG-k megoldásaival, majd vissza tudjuk fordítani AETERNA-specifikus szabályokká.

A cél közben változatlan: **ezzel az általános timing foundationnel visszamegyünk a Combat + Pecsét rendszerhez, és azon keresztül készítjük el az első valóban játszható harci foundationt.**

[1]: https://www.db.yugioh-card.com/yugiohdb/card_search.action?cid=5114&ope=2&request_locale=en&utm_source=chatgpt.com "Torrential Tribute | Card Details | Yu-Gi-Oh! Neuron(TRADING CARD GAME CARD DATABASE)"
[2]: https://www.yugioh-card.com/en/play/fast-effect-timing/ "Fast Effect Timing – Yu-Gi-Oh! TRADING CARD GAME"
[3]: https://img.yugioh-card.com/en/downloads/rulebook/SD_RuleBook_EN_10.pdf?utm_source=chatgpt.com "SD_RuleBook_EN_V10.indd"
[4]: https://www.yugioh-card.com/en/downloads/rivalry_of_warlords/Exosister-Manual.pdf?utm_source=chatgpt.com "EXOSISTER 
1\. A Light in the Darkness! 
2\. Pair Up"
[5]: https://www.yugioh-card.com/eu/play/understanding-card-text/part-3-conditions-activations-and-effects/ "Part 3: Conditions, Activations, and Effects – Yu-Gi-Oh!"
[6]: https://www.yugioh-card.com/eu/play/understanding-card-text/part-4-the-clues-on-your-cards/?utm_source=chatgpt.com "Part 4: The Clues on Your Cards – Yu-Gi-Oh!"
[7]: https://www.yugioh-card.com/en/play/psct/psct-4/?utm_source=chatgpt.com "Problem-Solving Card Text, Part 4: The Clues on Your Cards – Yu-Gi-Oh! TRADING CARD GAME"
[8]: https://www.yugioh-card.com/eu/wp-content/uploads/2022/07/Rulebook_v9_en.pdf?utm_source=chatgpt.com "OFFICIAL RULEBOOK"
[9]: https://www.yugioh-card.com/en/play/psct/psct-7/?utm_source=chatgpt.com "Problem-Solving Card Text, Part 7: 2012 Update – Conjunction Functions – Yu-Gi-Oh! TRADING CARD GAME"
[10]: https://www.yugioh-card.com/eu/play/understanding-card-text/part-7-conjunction-functions/?utm_source=chatgpt.com "Part 7: Conjunction Functions – Yu-Gi-Oh!"
[11]: https://www.reddit.com/r/Yugioh101/comments/f73w8g?utm_source=chatgpt.com "Yosenju Kama 1 Ruling?"
[12]: https://www.reddit.com/r/Yugioh101/comments/s8ywmp?utm_source=chatgpt.com "Master Duel chaining"


--rendben van akkor folytassuk--

Igen. Akkor tartjuk a korábbi elvet: **egyszerre egy problémát bontunk ki**, és nem ugrunk még vissza a Combat implementációjára.

Most az első Yu-Gi-Oh-részt néztem végig mélyebben: **az egyszerre kiváltott hatások / SEGOC logikát**. Ez különösen fontos az AETERNÁ-nak, mert itt találkozik a Trigger-rendszer a ReactionTimingWindowval.

### 1. A Yu-Gi-Oh fontos alapelve: „egyszerre kivált” nem azt jelenti, hogy egyszerre oldódik fel

Ha egy esemény miatt több Trigger Effect válik aktiválhatóvá, a Yu-Gi-Oh nem próbálja őket párhuzamosan végrehajtani. **Egy speciálisan felépített Chainbe rendezi őket**, majd a Chain normál módon, visszafelé oldódik fel. A hivatalos rulebook kifejezetten ezt írja az egyszerre aktiválódó Spell Speed 1, például Trigger Effectekről. ([Yu-Gi-Oh! Kártyák][1])

Ez nagyon erős minta nekünk:

```text
EVENT
↓
több trigger egyszerre jogosulttá válik

NEM:
trigger A és B "egyszerre történik"

HANEM:
trigger candidate collection
↓
deterministic ordering
↓
stack / chain
↓
LIFO resolution
```

Vagyis máris szét kell választanunk:

**trigger bekövetkezése → trigger aktiválása → trigger feloldása.**

Ez három külön pillanat.

---

## 2. A Trigger nem szakíthat félbe egy éppen feloldódó effektet

Ez szerintem az egyik legértékesebb Yu-Gi-Oh-szabály az AETERNA számára.

Ha egy Chain Link feloldása közben történik valami, ami új képességet triggerel:

```text
CL2 resolving
    ↓
Entitás megsemmisül
    ↓
egy képesség erre triggerel
```

akkor az új trigger **nem állítja meg CL2-t**, és nem nyit ott helyben új Chaint.

Előbb az egész jelenlegi Chain lefut.

Utána jön a következő trigger-feldolgozási pont. A hivatalos Fast Effect Timing diagram ugyanezt a struktúrát használja: Chain-resolution után ellenőrzi a rendszer, hogy létrejött-e aktiválható Trigger Effect, és csak ezután tér tovább a fast-effect lehetőségekhez. ([Yu-Gi-Oh! Kártyák][2])

Ez gyakorlatilag:

```text
STACK UNWIND
=========================

CL3 resolve
    trigger történt → FELJEGYEZZÜK

CL2 resolve
    trigger történt → FELJEGYEZZÜK

CL1 resolve
    trigger történt → FELJEGYEZZÜK

=========================
STACK COMPLETE

↓
TRIGGER CHECKPOINT
↓
új trigger chain/window
```

Ez nagyon közel van ahhoz, amerre a Reaction v1-et már elkezdtük építeni.

És szerintem **ezt érdemes megtartanunk**: normál resolution közben ne nyissunk új külső ReactionTimingWindowt.

---

# 3. A Yu-Gi-Oh előbb összegyűjti a Triggeröket, és csak UTÁNA engedi a szabad reakciókat

Ez kapcsolódik közvetlenül a korábbi csapdalapos példádhoz.

Tegyük fel:

```text
Monster Summoned
```

Ez maga nem Chain Link. A hivatalos timing-chart szerint Normal Summon, Chain nélkül történő Special Summon, attack declaration stb. után először meg kell vizsgálni, hogy van-e Trigger Effect. ([Yu-Gi-Oh! Kártyák][2])

Tehát:

```text
SUMMON
↓
TRIGGER COLLECTION
↓
trigger effectek bekerülnek a Chainbe
↓
ezután
FAST RESPONSE OPPORTUNITY
↓
Trap / Quick Effect / stb.
```

Ez nagyon fontos.

A Torrential Tribute-szerű csapda tehát nem ugyanaz, mint egy:

> „Ha ezt az Entitást megidézik, megteheted…”

Trigger Effect.

Mindkettő ugyanarra az eseményre reagálhat, de **más rétegen keresztül kerül be a rendszerbe**.

AETERNA nyelven valami ilyesmi kezd kirajzolódni:

```text
TIMING ANCHOR
      ↓
TRIGGER COLLECTION
      ↓
trigger entries rendezése
      ↓
REACTION TIMING WINDOW
      ↓
conditional/manual response options
      ↓
priority
```

Ez jobb annál, mintha mindent egyszerűen „reakciónak” neveznénk.

---

# 4. Ha több Trigger egyszerre történik, sorrendet kell adni nekik

A részletesebb hivatalos Yu-Gi-Oh rulebook ennek külön ordering-rendszert ad. A sorrend lényege:

```text
1. turn player mandatory
2. opponent mandatory
3. turn player optional
4. opponent optional
```

Az azonos csoporton belüli saját effectek sorrendjét a játékos állíthatja össze. ([Yu-Gi-Oh! Kártyák][3])

Vegyünk egy elméleti példát:

```text
P1 mandatory trigger: A
P1 mandatory trigger: B

P2 mandatory trigger: C

P1 optional trigger: D

P2 optional trigger: E
P2 optional trigger: F
```

A Chain például:

```text
CL1 A
CL2 B
CL3 C
CL4 D
CL5 E
CL6 F
```

P1 saját A/B sorrendjéről dönthet, P2 saját E/F sorrendjéről dönthet.

Majd:

```text
resolve F
resolve E
resolve D
resolve C
resolve B
resolve A
```

Ez elsőre furcsának tűnik, de két nagyon fontos problémát megold.

**Nincs valódi simultaneity ambiguity**, mert mindig kialakul egy pontos sorrend.

És **a játékosi döntést sem veszi el**, amikor több saját triggerének sorrendje stratégiailag számít.

AETERNA szempontjából ez rendkívül fontos, mert később simán lehet:

```text
egy Entitás megsemmisül

→ Visszhang A
→ másik Entitás ability B
→ Rituálé trigger C
→ valamilyen Pecsét/Domain trigger D
```

Nem mondhatjuk egyszerűen azt, hogy „mind megtörténik”.

Pontosan rendezni kell őket.

---

# 5. Ez viszont nem azt jelenti, hogy a Yu-Gi-Oh sorrendjét kell lemásolnunk

Szerintem ez az a pont, ahol tanulnunk kell tőlük, de nem automatikusan másolni.

A fontos felismerés:

> **Az egyszerre kiváltott trigger-eknek kell egy explicit ordering policy.**

Hogy az AETERNA ordering policy végül:

```text
active player mandatory
opponent mandatory
active player optional
opponent optional
```

legyen-e, még egyáltalán nincs eldöntve.

Akár lehet egyszerűbb is.

Például:

```text
mandatory triggers
↓
controller-ordering
↓
optional trigger decisions
↓
normal reactions
```

vagy valami más.

De **az ordering policy létezése már strukturális követelménynek látszik**.

---

# 6. Van egy még érdekesebb állapot: a Trigger már megtörtént, de még nem aktiválható

A Yu-Gi-Oh 2021-es hivatalos szabályfrissítése nagyon konkrét esetet kezel.

Ha egy monster Trigger Effect aktiválási feltétele már teljesült, de még nincs lehetősége aktiválódni — például mert még egy Chain közepén vagyunk —, akkor úgymond várnia kell.

Viszont ha közben a kártya **helye megváltozik**, mielőtt elérkezik az aktiválási lehetőség, az effect már nem aktiválódik. ([Yu-Gi-Oh! Kártyák][4])

Ez például:

```text
Chain resolving

↓
E1 a fieldről Graveyardba kerül

→ E1 GY trigger condition teljesül
→ de most még NEM lehet aktiválni

↓
ugyanazon Chain következő része:
E1 Graveyard → banished

↓
Chain vége
↓
Trigger checkpoint

E1 már nincs azon a locationön,
ahol a triggerét aktiválhatná

→ trigger nem aktiválódik
```

Ez egy teljesen új fogalmi réteget mutat:

```text
TRIGGER CONDITION MET
≠
TRIGGER ACTIVATED
```

A kettő között létezhet egy **pending trigger opportunity**.

És ez tökéletesen kapcsolódik ahhoz, amit korábban a ReactionTimingWindowról mondtál.

---

# 7. Ez AETERNÁ-ban valószínűleg külön objektumot igényel

Nem konkrét contractot írok még, csak a koncepciót.

Eddig valahogy így gondolkodtunk:

```text
Event
→ Trigger
→ StackEntry
```

Most már látszik, hogy ez túl egyszerű.

Inkább:

```text
EVENT
↓
TRIGGER CONDITION MATCH

↓
TriggerCandidate / TriggerOpportunity

↓
megfelelő Timing Checkpoint

↓
activation legality check

↓
mandatory:
activate automatically

vagy

optional:
player decision

↓
StackEntry
```

Tehát a `TriggerCandidate` **még nem StackEntry**.

Ez nagyon fontos.

---

# 8. És itt jön vissza a játékosi döntés

Tegyük fel, hogy egyszerre két opcionális saját képességed triggerelt:

```text
A:
"amikor egy saját Entitás megsemmisül,
meg­teheted, hogy húzol 1 lapot"

B:
"amikor egy saját Entitás megsemmisül,
meg­teheted, hogy kapsz 1 Aurát"
```

Nem elég ezt mondani:

```text
A triggerelt
B triggerelt

→ automatikusan stack
```

Hanem:

```text
TriggerCandidate A
TriggerCandidate B

↓
játékos dönt:
A használom?
B használom?

↓
ha mindkettő igen:
milyen sorrendben?
```

Ez **nem ugyanaz**, mint a normál Reaction Priority.

Előbb trigger-decision történik.

Utána lehet:

```text
ReactionTimingWindow
```

ahol akár az ellenfél is reagálhat az így felépített stackre.

Ez már sokkal tisztább.

---

# 9. Konkrét Yu-Gi-Oh Chain-példa: nagyon hasonló ahhoz, amire nekünk szükségünk van

A Konami hivatalos PSCT-oktatóanyaga egy teljes, konkrét láncot mutat:

```text
CL1 Trident Warrior
CL2 Raigeki Break
CL3 Gemini Spark
```

A Gemini Spark aktiválási költségeként feláldozzák azt a monstert, amelyet Raigeki Break korábban célba vett.

Feloldás:

```text
CL3 Gemini Spark
→ feloldódik

CL2 Raigeki Break
→ az eredeti target már nincs ott
→ nem tudja megsemmisíteni
→ ettől még CL2 megkapta a resolution attemptjét

CL1 Trident Warrior
→ normálisan tovább oldódik
```

([Yu-Gi-Oh! Kártyák][5])

Ez igazolja azt a korábbi AETERNA-elvünket:

> **egy szabályosan létrejött stack entry nem tűnik el csak azért, mert később értelmetlenné válik.**

És nagyon fontos:

```text
CL2 failure
```

nem teszi ezt:

```text
CL1 is cancelled
```

A külön Chain Linkek saját resolution lifecycle-lal rendelkeznek.

---

# 10. Az effect belső lépései viszont lehetnek függők

Ez megint egy másik probléma.

A Yu-Gi-Oh PSCT `then`, `also`, `and if you do`, `and` kötőszavai egyszerre határozzák meg:

* az események időbeli kapcsolatát;
* és azt, hogy az egyik rész sikertelensége leállítja-e a másikat. ([Yu-Gi-Oh! Kártyák][6])

Például:

```text
DO A, THEN B
```

A szükséges B-hez.

Ha A nem sikerül:

```text
B sem történik
```

De:

```text
DO A, ALSO B
```

esetén:

```text
A nem sikerül
→ B attól még megpróbálható
```

Tehát megint:

```text
CHAIN LINK dependency
```

és

```text
EFFECT-INTERNAL dependency
```

két teljesen külön dolog.

Ez nagyon fontos lesz az AETERNA ability compiler szempontjából.

---

# 11. Mit tanulnék ebből jelenleg az AETERNÁ-nak?

Még **nem döntésként**, hanem erős rendszertervezési tanulságként ezt látom:

| Fogalom                    | Jelentés                                        |
| -------------------------- | ----------------------------------------------- |
| `TimingAnchor`             | olyan esemény/pont, amely triggerelhet valamit  |
| `TriggerCandidate`         | feltétel teljesült, de még nem aktivált ability |
| `TriggerCheckpoint`        | amikor a várakozó triggerek feldolgozhatók      |
| `ActivationDecision`       | opcionális trigger esetén játékosi igen/nem     |
| `TriggerOrdering`          | egyszerre aktiválódó entryk sorrendje           |
| `ReactionTimingWindow`     | a rendezett trigger-entrykre további válaszok   |
| `StackEntry`               | már aktivált, feloldásra váró egység            |
| `ResolutionAttempt`        | minden létrejött entry kapja                    |
| `PostResolutionCheckpoint` | új triggerek feldolgozásának következő helye    |

És így már a teljes folyamat:

```text
ATOMIC ACTION / RESOLUTION
        ↓
events keletkeznek
        ↓
trigger candidates feljegyzése
        ↓
nem szakítjuk félbe az aktuális resolutiont
        ↓
TRIGGER CHECKPOINT
        ↓
eligibility revalidation
        ↓
mandatory + optional trigger decisions
        ↓
TRIGGER ORDERING
        ↓
initial stack segment
        ↓
REACTION TIMING WINDOW
        ↓
priority / additional responses
        ↓
window close
        ↓
LIFO RESOLUTION
        ↓
következő checkpoint
```

Ez szerintem már **lényegesen közelebb van egy komoly AETERNA timing rendszerhez**.

### És van egy nagyon fontos jó hír

Ez pontosan annak az általánosításnak tűnik, amire szükségünk van, miközben nem dobjuk ki a Reaction v1-et.

A Reaction v1 már kezeli a:

```text
ReactionWindow
priority
pass
stack
LIFO
revalidation
checkpoint
```

részeket.

Ami most hiányzó rétegként kezd körvonalazódni:

```text
TimingAnchor
TriggerCandidate
TriggerCheckpoint
simultaneous trigger ordering
optional activation decision
```

Ez pedig éppen az a terület, amelyet a Reaction v1 első körében tudatosan nem vittünk végig teljesen.

A következő egyetlen Yu-Gi-Oh témának szerintem most a **„When” vs. „If” / miss the timing** rendszert vegyük. Ez mutatja meg, hogy egy `TriggerCandidate` **meddig őrzi meg az aktiválási jogát**, és mikor mondja a játék azt, hogy az alkalom már elmúlt. Ott fogjuk látni, hogy a Yu-Gi-Oh egyik legkomplexebb — és szerintem részben kerülendő — timing-megoldását hogyan tudnánk AETERNA számára tisztábban újragondolni.

[1]: https://www.yugioh-card.com/eu/wp-content/uploads/2022/07/Rulebook_v9_en.pdf "https://www.yugioh-card.com/eu/wp-content/uploads/2022/07/Rulebook_v9_en.pdf"
[2]: https://www.yugioh-card.com/en/play/fast-effect-timing/ "https://www.yugioh-card.com/en/play/fast-effect-timing/"
[3]: https://img.yugioh-card.com/en/downloads/rulebook/SD_RuleBook_EN_10.pdf "https://img.yugioh-card.com/en/downloads/rulebook/SD_RuleBook_EN_10.pdf"
[4]: https://www.yugioh-card.com/en/play/2021_rules_update/ "https://www.yugioh-card.com/en/play/2021_rules_update/"
[5]: https://www.yugioh-card.com/eu/play/understanding-card-text/part-3-conditions-activations-and-effects/ "https://www.yugioh-card.com/eu/play/understanding-card-text/part-3-conditions-activations-and-effects/"
[6]: https://www.yugioh-card.com/eu/play/understanding-card-text/part-7-conjunction-functions/ "https://www.yugioh-card.com/eu/play/understanding-card-text/part-7-conjunction-functions/"


--rendben van 
folytassuk akkor tovább--

Rendben. Most kizárólag a **Yu-Gi-Oh „When / If / miss the timing”** réteget bontottam tovább. Ez azért különösen hasznos, mert pontosan arra válaszol, hogy:

> egy esemény bekövetkezett, egy képesség reagálhatna rá — **meddig él ez az aktiválási lehetőség?**

És itt már látok olyat is, amit érdemes átvennünk, illetve olyat is, amit szerintem az AETERNÁ-ban tudatosan **jobban kell megoldanunk**, mint a Yu-Gi-Oh.

## 1. A Yu-Gi-Oh-ban nem minden „amikor X történik” egyforma

A legfontosabb különbség az opcionális trigger két klasszikus formája között van.

Nagyon leegyszerűsítve:

```text
WHEN X happens: You can...
```

és

```text
IF X happens: You can...
```

nem feltétlenül ugyanúgy viselkedik.

A Konami saját PSCT-anyaga explicit rámutat, hogy bizonyos, **„CAN” + „WHEN”** típusú effektek csak akkor használhatók, ha a kiváltó esemény volt a releváns **„last thing that happened”**. ([Yu-Gi-Oh! Kártyák][1])

Az `IF ... You can` típusú opcionális trigger ezzel szemben alapvetően nem ugyanilyen szigorú „azonnal az utolsó eseménynek kell lennie” logikát követ.

Ezért létezik a közismert **miss the timing** jelenség.

---

# 2. Mit jelent valójában a „last thing that happened”?

Vegyünk egy effectet:

```text
Do A, THEN do B.
```

A Konami PSCT szerint:

```text
A
↓
B
```

nem egyidejű.

B történik utoljára. ([Yu-Gi-Oh! Kártyák][1])

Például a hivatalos Heraldry Change-példa:

```text
Special Summon egy monstert,
THEN
end the Battle Phase
```

A feloldás után az utolsó esemény:

```text
Battle Phase ended
```

és **nem**:

```text
Monster was Summoned
```

Ezért egy olyan effekt, amely csak akkor aktiválható, **amikor egy monster Summoned**, és szigorú „WHEN” timingot használ, már nem feltétlenül aktiválható. A Konami konkrétan a Torrential Tribute-ot hozza fel példának. ([Yu-Gi-Oh! Kártyák][1])

Ez elsőre nagyon furcsa:

```text
monster TÉNYLEG meg lett idézve
```

de a rendszer azt mondja:

```text
igen, de nem ez volt a feloldás utolsó releváns eseménye
```

Ez a „miss the timing”.

---

# 3. Ugyanezért számítanak a kötőszavak

A PSCT nem pusztán szép nyelvtan.

A Konami négy fontos kapcsolatot különböztet meg:

```text
then
also
and if you do
and
```

És ezek közül a timing szempontjából lényeges:

### `A, then B`

Szekvenciális.

```text
A megtörténik
↓
B megtörténik

utolsó esemény = B
```

### `A, also B`

Időzítésileg egyidejű.

```text
A + B
ugyanazon időpont része
```

### `A, and if you do, B`

Szintén egyidejűnek tekintett az aktiválási timing szempontjából, csak B végrehajtása A sikerétől függ.

### `A and B`

Szintén egyidejű, ráadásul erősen összekötött végrehajtás.

Ezt a Konami kifejezetten azért használja, hogy meg lehessen mondani, **mi számít az utolsó megtörtént eseménynek**, és ezáltal milyen új Trigger Effect nyílhat meg. ([Yu-Gi-Oh! Kártyák][1])

Ez nagyon érdekes az AETERNA számára, mert itt találkozik:

```text
effect dependency
```

és

```text
timing
```

— de **nem ugyanaz a kettő**.

---

# 4. Konkrét „miss the timing” példa

Van hivatalos Konami ruling például a régi **Core Blaster** esetére.

A lapnak olyan opcionális `When ... you can` jellegű effektje volt, amely akkor működhetett volna, amikor a hozzá tartozó felszerelt monster eltűnik, és a lap a Graveyardba kerül.

A hivatalos ruling szerint, ha ez **egy éppen feloldódó Chain közepén** történik, a játékos elveszítheti az aktiválási timingot. ([Yu-Gi-Oh! Kártyák][2])

A szerkezet:

```text
Chain még oldódik

CL2 részeként:
Core Blaster triggerfeltétele megtörténik

↓
DE nem aktiválhatunk új Chain Linket
a jelenlegi Chain resolution közben

↓
CL2 / CL1 folytatódik

↓
amikor végre aktiválni lehetne:
már nem az a releváns "when" pillanat

→ opportunity lost
```

Ez nagyon fontos, mert itt nem arról van szó, hogy:

```text
trigger condition nem történt meg
```

Hanem:

```text
megtörtént,
de nem volt olyan jogi időpont,
amikor az optional WHEN effect aktiválható lett volna.
```

---

# 5. Az `IF` megközelítés pont ezt kerüli meg

A mai Yu-Gi-Oh kártyák között rengeteg ilyen szöveget látunk:

> `If this card is ... : You can ...`

Például a hivatalos kártyaadatbázisban a **Hallo, the Spirit of Tricks**:

```text
If this card is Normal or Special Summoned:
You can activate this effect...
```

és:

```text
If this card is destroyed by battle or card effect:
You can...
```

formát használ. ([Yu-Gi-Oh! Kártyák][3])

Ez lényegében kevésbé törékeny trigger-szemantika.

A játék megjegyezheti:

```text
az aktiválási feltétel teljesült
```

és a következő szabályos trigger-feldolgozási ponton foglalkozhat vele.

---

# 6. De van egy nagyon fontos korlát még az `IF`-szerű triggerekre is

Itt jön a **2021 Rules Update**, amit szerintem nekünk különösen érdemes tanulmányozni.

Konami explicit szabálya:

ha egy monster Trigger Effect feltétele teljesül, de még nem aktiválható, mert például Chain resolution közepén vagyunk, akkor az effect „vár”.

Viszont ha **a kártya locationje megváltozik**, mielőtt eljutnánk az aktiválási lehetőséghez, a trigger már nem aktiválódik. ([Yu-Gi-Oh! Kártyák][4])

Például:

```text
CL2 resolving

E1:
Field → Graveyard

→ GY trigger condition met

de még nincs trigger checkpoint
```

Majd ugyanazon Chainben:

```text
E1:
Graveyard → Banished
```

Chain vége.

Amikor végre feldolgoznánk:

```text
E1 már nem a Graveyardban van
```

→ a Trigger Effect **nem aktiválódik**. ([Yu-Gi-Oh! Kártyák][4])

Ez nagyon fontos különbséget mutat:

```text
TRIGGER CONDITION MET
```

még mindig nem jelenti azt, hogy:

```text
ACTIVATION GUARANTEED
```

---

# 7. Ez valójában három életciklus-állapotot jelent

Szerintem ezt az AETERNA számára érdemes kiemelni.

Nem:

```text
triggered
→ stack
```

hanem:

```text
1. CONDITION MATCHED
        ↓
2. PENDING OPPORTUNITY
        ↓
3. ACTIVATED ENTRY
```

A második állapot alatt még történhet olyan változás, amely miatt:

```text
pending opportunity
→ expires / invalidates
```

Ez szerintem nagyon jó koncepció.

---

# 8. De a Yu-Gi-Oh „miss the timing” mechanikáját nem venném át egy az egyben

Itt szerintem tényleg tudunk jobbat csinálni.

Yu-Gi-Oh-ban egy részét a timingnak olyan természetes nyelvi részletek határozzák meg, mint:

```text
WHEN
vs
IF
```

és:

```text
THEN
vs
AND IF YOU DO
```

Ez nagyon precíz rendszer lett az évek alatt, de a játékos számára elég nehezen intuitív.

Például:

```text
A történt
majd B történt
```

és egy játékos teljesen jogosan mondhatná:

> „De hát A megtörtént, miért nem használhatom az A-ra reagáló kártyámat?”

A válasz:

> „Mert nem A volt az utolsó dolog, ami történt.”

Ez szabálytechnikailag koherens, de elég nagy tudásküszöböt teremt.

---

# 9. AETERNA-ban ezt szerintem explicit adatszemantikával kellene kezelni

Nem a magyar:

```text
amikor
```

vagy:

```text
ha
```

szó alapján kellene a rules engine-nek kitalálnia.

Hanem egy ability adatmodell mondja meg.

Például:

```text
trigger_event = entity_destroyed
```

és külön:

```text
opportunity_policy =
    immediate_only
```

vagy:

```text
opportunity_policy =
    next_trigger_checkpoint
```

Ez ugyanazt a képességet sokkal egyértelműbben írja le.

---

# 10. `immediate_only`

Ez lenne a Yu-Gi-Oh strict `When ... can` funkcionális megfelelője.

```text
trigger event = X

X bekövetkezik
↓
csak a közvetlen következő
megengedett timing pointon használható
```

Ha közben más olyan esemény kerül a timing authority elé, amely ezt megszakítja:

```text
opportunity expires
```

De ezt csak olyan kártyáknál használnánk, ahol **tényleges designértéke van**.

Nem a természetes nyelv véletlen mellékhatásaként.

---

# 11. `next_checkpoint`

Ez szerintem jobb általános default lehet.

```text
X bekövetkezik
↓
TriggerCandidate létrejön
↓
current atomic resolution befejeződik
↓
TriggerCheckpoint
↓
ha továbbra is eligible:
opportunity offered
```

Vagyis:

```text
nem kell X-nek a "last thing that happened"-nek lennie
```

Ez közelebb állna a modern, játékosbarát trigger-rendszerhez.

---

# 12. És lehet `window_bound` is

Ez inkább a korábbi csapdalapos példádhoz kapcsolódik.

Például egy AETERNA „csapda”-jellegű képesség:

> „Amikor az ellenfél Entitást manifesztál…”

Nem feltétlenül TriggerCandidate.

Lehet:

```text
activation_condition = entity_manifested
opportunity_policy = while_associated_window_open
```

Tehát:

```text
Entity manifested
↓
ReactionTimingWindow opens

ability legal option marad
amíg ez a konkrét window él
```

Ha passzolod az első priorityt, majd az ellenfél csinál valamit, és később priorityt kapsz vissza **ugyanabban a windowban**, a képesség még lehet legális.

A window lezárása után:

```text
expired
```

Ez közelebb áll a Torrential Tribute-szerű conditional response-höz.

---

# 13. Ez alapján három külön OpportunityLifetime már nagyon indokoltnak látszik

Munkaszinten:

| Policy            | Mit jelent?                                                  | Yu-Gi-Oh-szerű példa         |
| ----------------- | ------------------------------------------------------------ | ---------------------------- |
| `immediate_only`  | csak közvetlen timing-alkalom                                | strict optional `When`       |
| `next_checkpoint` | megjegyezzük, következő trigger checkpointon dolgozzuk fel   | `If`-szerű trigger           |
| `window_bound`    | az adott ReactionTimingWindow teljes ideje alatt használható | Trap / Quick response jelleg |

Ez szerintem sokkal pontosabb, mint az előző egyszerű:

```text
optional_trigger
```

címke.

---

# 14. De kell még egy negyedik dimenzió: source requirement

A 2021-es Yu-Gi-Oh szabályból látszik, hogy nemcsak az idő számít.

A TriggerCandidate létrejöhet:

```text
source = Graveyard
```

de mire sorra kerül:

```text
source = Banished
```

és ezért már nem aktiválható. ([Yu-Gi-Oh! Kártyák][4])

AETERNA-ban külön kellene lennie például:

```text
activation_source_requirement =
    same_zone
```

vagy:

```text
activation_source_requirement =
    identity_only
```

vagy:

```text
activation_source_requirement =
    none_after_trigger
```

Ez megint külön réteg az opportunity lifetime-tól.

---

# 15. Példa AETERNÁ-val

Tegyük fel egy jövőbeli Entitás:

> „Amikor ez az Entitás a Voidba kerül, megteheted, hogy húzol 1 lapot.”

Kétféleképpen lehetne definiálni.

### Változat A – source-nak ott kell lennie

```text
trigger_event = entered_void

opportunity_policy = next_checkpoint

activation_source_requirement =
    still_in_void
```

Folyamat:

```text
E1 → Void
↓
candidate created

current resolution folytatódik

másik effect:
E1 → Hand

↓
TriggerCheckpoint

E1 nincs Voidban
→ candidate expires
```

Ez szinte pontosan a Yu-Gi-Oh 2021-es modellje.

---

### Változat B – az esemény önmagában elegendő

```text
trigger_event = entered_void

opportunity_policy = next_checkpoint

activation_source_requirement =
    event_was_valid
```

Ugyanez:

```text
E1 → Void
↓
trigger fact recorded

E1 → Hand

↓
checkpoint

→ ability továbbra is aktiválható
```

Mindkettő értelmes lehet.

A lényeg: **a kártya/ability contract mondja meg**, nem implicit engine-találgatás.

---

# 16. Ez különösen fontos lesz a Visszhang miatt

Itt visszakapcsolódunk egy már ismert AETERNA-területhez.

A Visszhang alapvetően Void-entry eseményekkel kapcsolódik össze.

Ha majd teljesen implementáljuk, pontosan meg kell mondanunk:

```text
Voidba lépés
→ trigger fact?
```

és azt is:

```text
a lapnak még Voidban kell lennie,
amikor a Visszhang aktiválódik?
```

vagy elég:

```text
hitelesen belépett a Voidba
```

Ez ugyanaz a kérdés, amit most a Yu-Gi-Oh 2021-es trigger-location szabályában látunk.

Tehát ez az elemzés tényleg nem elméleti kitérő: később közvetlenül kelleni fog az AETERNA kulcsszavaihoz is.

---

# 17. És a Combatnál is ugyanaz jön vissza

Például:

```text
Attack declared
```

egy ability:

> „Amikor az ellenfeled támadást deklarál, megteheted…”

Lehet:

```text
window_bound
```

és a konkrét:

```text
after_attack_declaration
ReactionTimingWindow
```

lezárásáig él.

Másik ability:

> „Ha ebben a körben megtámadták egyik Pecsétedet…”

lehet:

```text
event remembered
→ next_checkpoint vagy későbbi explicit timing
```

Tehát nem kell mindent ugyanabba az „amikor történt” dobozba raknunk.

---

## Jelenlegi következtetésem

A Yu-Gi-Oh egyik legjobb ötlete:

> **az aktiválási alkalomnak önálló timing-identitása van.**

Az egyik legrosszabb öröksége viszont szerintem az, hogy ennek jelentős részét történelmileg:

```text
WHEN / IF
+
last thing that happened
+
szövegi conjunction
```

kombinációjából kell kikövetkeztetni.

Az AETERNÁ-ban szerintem jobb lenne:

```text
TriggerCondition
+
OpportunityLifetime
+
ActivationSourceRequirement
+
TimingWindow
```

explicit rendszer.

A kártyaszöveg ebből legyen **ember számára olvasható megjelenítés**, ne maga a rules-engine parserének egyetlen authorityja.

Ez ráadásul illik ahhoz az architektúránkhoz is, ahol a canonical ability-adat és a production runtime binding már külön réteg.

### Ezzel a „miss the timing” témát szerintem elég jól feltártuk

A tanulságot megtartanám, de a Yu-Gi-Oh komplikált `When/If` szabályát **nem venném át defaultként**.

A következő Yu-Gi-Oh-réteg, amit most érdemes ugyanezzel a mélységgel kibontani, az **activation negation vs effect negation**.

Ez azért különösen fontos, mert elsőre mindkettő úgy hangzik, hogy:

> „megállítottam a másik képességét”,

de Yu-Gi-Oh-ban teljesen eltérő következménye lehet annak, hogy:

```text
maga az activation vált érvénytelenné
```

vagy csak:

```text
az entry feloldódik,
de az effectje negated
```

És ebből közvetlen választ kaphatunk arra, hogy az AETERNA timing rendszerben mit jelentsen majd a **`cancelled`**, **`invalidated`** és **`resolved_no_effect`** közötti különbség.

[1]: https://www.yugioh-card.com/eu/play/understanding-card-text/part-7-conjunction-functions/?utm_source=chatgpt.com "Part 7: Conjunction Functions – Yu-Gi-Oh!"
[2]: https://img.yugioh-card.com/ygo_cms/ygo/all/uploads/ANPR_rules.pdf?utm_source=chatgpt.com "ANPR rules for sneak peek v1bx"
[3]: https://www.db.yugioh-card.com/yugiohdb/card_search.action?cid=20723&ope=2&request_locale=ae&utm_source=chatgpt.com "Hallo, the Spirit of Tricks | Card Details | Yu-Gi-Oh! Neuron(OFFICIAL CARD GAME CARD DATABASE)"
[4]: https://www.yugioh-card.com/en/play/2021_rules_update/?utm_source=chatgpt.com "2021 Rules Update – Yu-Gi-Oh! TRADING CARD GAME"


--rendben van
én sem szeretném hogy a nyelvtani külömbségek megakasszák a folyamatokat 
megneheztitené a forditást, az értelmezést és szerintem mindent 
amit irtál az szerintem nagyrészt jó mindenképpen kell még finomitani rajta de szerintem olyan megoldás kell mint a Kulcsszavaknál tehát ha van egy paraméter az fix és nem a játékosnak vagy a programnak kell eldönteni hogy azt ő hogyan értelmezi
még nem tudom ezt hogy lehetne jól megoldani és az is lehet hogy hülye ötlet ezért csak megjegyezzük hogy van és nem kezdőnk mindent ehhez igazitani
ha ugy gondolod hogy eléggé kielemeztük a yugioht akkor nézzük meg hogy ezen tudással találunk e még releváns információkat a többi forrásjátékban 
ha megvagyunk akkor folytathatjuk a munkát a rendszer kialakitásához--

Igen, szerintem a Yu-Gi-Oh-t a mostani rendszertervezési célhoz már elég mélyen szétszedtük. Nem mondom, hogy minden rulingját ismerjük; például a negation különbségeihez később még vissza kell térnünk, amikor az AETERNÁ-ban ténylegesen megjelenik „hatás megállítása / aktiválás megakadályozása”. De a timing-framework felépítéséhez már megvannak a fontos szerkezeti tanulságok.

És a paraméteres elképzelésed egyáltalán nem rossz. Sőt, a többi játék vizsgálata után még erősebb iránynak látszik: a játékos által olvasott szöveg és az engine által használt pontos szemantika legyen két külön réteg. Vagyis a magyar, angol vagy bármely más fordítás mondhatja természetesen, hogy „amikor”, „ha”, „válassz”, de mögötte legyen például fix selection_timing, revalidation_policy, opportunity_lifetime stb. Az engine ne nyelvtant értelmezzen.

Mit ad hozzá a Magic?

A Magicből meglepően sok olyan dolgot találtam, amely közvetlenül megerősíti az eddigi gondolkodásunkat. A Wizards jelenleg is külön Comprehensive Rules dokumentumot tart fenn a corner case-ek számára.

A legfontosabb talán a célpontok kezelése. Magicben a célpontokat általában a spell/ability stackre helyezésekor választják. Resolutionkor újra ellenőrzik őket. Ha több target van és csak egy része vált illegálissá, a legálisakra továbbra is végrehajtódik a hatás; ha viszont minden target illegális, az egész spell/ability nem resolve-ol. A már kiosztott sebzés vagy effect nem osztódik át automatikusan egy másik célpontra.

Ez szinte pontosan támogatja a mi elvünket:

locked target invalid
≠
automatic retarget

Retarget Magicben is csak akkor történik, ha egy külön effect kifejezetten megengedi vagy előírja az új target kiválasztását. Erre jó hivatalos példa a Return the Favor.

Ezért az AETERNA számára a:

target_failure_policy

paraméter nagyon indokoltnak tűnik.

Például:

all_targets_required
partial_targets_allowed
explicit_reselection

Nem a szövegből találgatnánk.

Magic még a te ATK-példádra is ad egy nagyon jó analógiát

A Magicben létezik az úgynevezett intervening if feltétel.

Az ilyen trigger kétszer ellenőrzi a feltételt:

trigger pillanatában
ÉS
resolutionkor

Ha első alkalommal nem igaz, nem triggerel. Ha triggerelt, de resolutionkor már nem igaz, nem történik meg a hatás.

Viszont egy normál aktivált képességnél az aktiválási feltételt nem feltétlenül ellenőrzi újra resolutionkor. A Wizards konkrétan össze is hasonlítja ezt a két modellt.

Ez nagyon erős bizonyíték arra, hogy nálunk is külön paraméter kell:

condition_check =
    activation_only

vagy:

condition_check =
    activation_and_resolution

Nem pedig általános szabály, hogy „mindent újraellenőrzünk”.

A source eltűnése

Magicben egy már stackre került trigger gyakran független a forrásától. A Saga chapter ability például tovább él a stacken akkor is, ha maga a Saga eltűnik vagy megváltozik.

Viszont létezhet olyan effect, amely resolutionkor aktuális vagy last-known informationt használ. Erre is vannak explicit rulings.

Ez megint azt erősíti, hogy ne legyen egyetlen univerzális:

source must still exist

szabály.

Hanem:

source_requirement =
    independent_after_activation
    current_source_required
    same_zone_required
    last_known_information_allowed

jellegű szemantika kellhet.

Magicből viszont van valami, amit valószínűleg NEM akarunk átvenni

Ez nagy különbség a Yu-Gi-Oh-hoz képest.

Magicben amikor a stack teteje resolve-ol, utána újra priority következik, mielőtt a következő stackelem resolve-olna. Vagyis két stackelem feloldása közé új spell/ability kerülhet.

Például:

Stack:
A
B
C

C resolve

→ priority újra
→ D még bekerülhet

D resolve
→ priority
→ B...

Yu-Gi-Oh-ban ezzel szemben:

Chain complete
→ C
→ B
→ A

és Chain resolution közben nincs normál új aktiválás.

Az AETERNA Reaction v1 jelenleg inkább a második modell felé épült.

Én ezt most nem nyitnám újra. A zárt LIFO unwind egyszerűbb, determinisztikusabb, és már megépítettük hozzá a foundationt. De ezt most már tudatos designválasztásként látjuk, nem véletlen implementációként.

Vanguard: itt találtam talán a legértékesebb új ötletet

A current Vanguard rules oldalon jelenleg a Comprehensive Rules 4.59, 2026. augusztus 28-i verzió szerepel.

A Vanguardnak van egy nagyon tiszta fogalma:

check timing

Az automatic ability triggerfeltétele megtörténik:

event
↓
ability becomes "standing by"

Nem feltétlenül oldódik fel azonnal.

A következő megfelelő check timing feldolgozza a várakozó automatic abilityket. A rendszer közben rule actionöket is kezel, majd egyesével resolve-olja a várakozó képességeket.

Ez nagyon közel áll ahhoz, amit mi:

TriggerCandidate
↓
TriggerCheckpoint

néven kezdtünk kialakítani.

Tehát nem csak a Yu-Gi-Oh támasztja alá ezt a modellt.

És Vanguardból kaptunk egy nagyon konkrét Combat-választ is

A Vanguard combat szabály kifejezetten ellenőrzi a damage step során, hogy a támadó és a megtámadott unit továbbra is megfelelő helyen és megfelelő controllerrel van-e.

Ha valamelyik:

elhagyta a fieldet
vagy
controllert váltott
vagy
másik circle-re mozgott

akkor a power comparison nem történik meg és a támadás nem talál.

Ez nagyon érdekes a korábbi AETERNA-kérdésünkre:

Attack → target
→ Reaction
→ target eltűnik / elmozdul / megváltozik
→ ?

Vanguard nem keres automatikusan új targetet.

Hanem:

combat revalidation
→ feltétel már nem teljesül
→ attack doesn't hit

Nem azt mondom, hogy az AETERNA-ban pontosan ezt kell választanunk. De most már van kipróbált precedensünk arra, hogy a Combat saját explicit revalidation policyt kapjon.

Ez megint tökéletesen illik a paraméteres elképzelésünkhöz.

Duel Masters: váratlanul hasznos kontrollforrás

A jelenlegi japán Comprehensive Rules 1.51, 2026. július 23-i.

Itt két nagyon releváns dolgot találtam.

Ha több „when attacking” jellegű képesség egyszerre triggerel, a hivatalos ruling szerint egy időben triggerelnek, de egyenként oldódnak fel.

Megint:

simultaneous trigger facts
≠
simultaneous resolution

Ez most már Yu-Gi-Oh + Magic + Vanguard + Duel Masters oldalról is ugyanabba az irányba mutat.

A másik még érdekesebb: Duel Masters 2022-ben megváltoztatta a szabályát, hogy bizonyos több opciós képességeknél mikor kell választani. Korábban trigger/cast időben kellett kiválasztani az opciót; az új szabály szerint a választás resolutionkor történik.

Ez elképesztően jól illeszkedik a mi:

selection_timing =
    activation
    resolution

paraméterünkhöz.

Tehát még egy létező TCG is arra jutott, hogy a választás időpontja önálló szabályparaméterként fontos, olyannyira, hogy később át kellett alakítaniuk a rendszerüket.

Hearthstone ebből a szempontból inkább figyelmeztetés

A Hearthstone nagyon jó inspiráció volt például a Taunt/Oltalom számára, de timing-framework mintának sokkal gyengébb.

Nem találtam a Blizzardtól a Magic vagy Vanguard Comprehensive Rules-ához hasonló jelenlegi nyilvános, formális timing-specifikációt. A közösség által használt „Advanced Rulebook” megfigyelésekből és tesztekből épült; még a Blizzard fórumán is külön megjegyzik, hogy nem hivatalos Blizzard rules document.

Ez pontosan azt a problémát mutatja, amit mi kerülni szeretnénk:

"így szokott működni a kliens"

ne legyen ugyanaz, mint:

"ez a szabály"

Hearthstone-nál a digitális engine elrejtheti a részletek jelentős részét. Az AETERNA viszont fizikai játék is, ezért nekünk leírható, reprodukálható timing semantics kell.

A négy rendszerből most már nagyon erős közös minták rajzolódnak ki
Kérdés	Yu-Gi-Oh	Magic	Vanguard	Duel Masters	AETERNA felé mutató irány
trigger ≠ resolution	igen	igen	igen	igen	igen
pending trigger állapot	igen	igen, stackre vár	standing by	várakozó effect	igen
explicit checkpoint	timing flow	priority/SBA	check timing	timing processing	igen
LIFO válaszrendszer	igen	igen	nem ilyen	nem ilyen	Reaction v1 miatt igen
resolution közben új válasz	nem	stackelemek között igen	saját modell	saját modell	jelenleg nem
activation vs resolution condition	igen	explicit különbség	feltételes	igen	külön paraméter
target invalid → automatikus retarget	nem	nem	nem	nem általános	nem
selection timing	többféle	többféle	effectfüggő	explicit módosították	paraméter
source eltűnés kezelése	effectfüggő	effectfüggő	effectfüggő	effectfüggő	paraméter

És szerintem itt ér össze az ötleted a kutatással.

A „kulcsszóhoz hasonló fix paraméter” irány nagyon életképes

Még nem fagyasztanám le az exact mezőneveket, de koncepcionálisan egy canonical ability nem pusztán ezt mondaná:

"amikor egy Entitás megsemmisül..."

hanem a rules data valami ehhez hasonló, fix enumokból álló szemantikát hordozna:

timing_anchor
trigger_mode
opportunity_lifetime
selection_timing
binding_policy
activation_condition_policy
resolution_condition_policy
source_requirement
target_failure_policy
effect_dependency
resolution_outcome_policy

Például a természetes szöveg lehet több nyelven:

HU:
"Amikor az ellenfeled Entitást manifesztál..."

EN:
"When your opponent manifests an Entity..."

De egyik nyelv sem mondja meg a motornak, hogy pontosan hogyan működik.

Az authority valami ilyesmi lenne:

timing_anchor = opponent_entity_manifested
opportunity_lifetime = associated_reaction_window
activation_mode = optional_response

Így magyarul akár másképp is lehet majd jól megfogalmazni, mint angolul.

A fordítás nem tudja megváltoztatni a szabályt.

Ez szerintem pontosan az a tulajdonság, amit a Kulcsszavaknál is szeretnénk:

a név/szöveg megjelenítés; a mögötte lévő canonical jelentés rögzített.

Viszont egyetértek veled abban is, hogy most még ne igazítsunk hozzá mindent. Először meg kell találnunk a minimális paraméterkészletet. Ha túl korán húsz enumot hozunk létre, könnyen egy túltervezett rendszert kapunk.

A legnagyobb tanulság a cross-TCG auditból

Most már elég biztosan látom, hogy nem egy másik játék teljes timing rendszerét kell kiválasztanunk.

A jó AETERNA-rendszer valószínűleg több helyről veszi át a jó ötleteket:

Yu-Gi-Oh
→ zárt response-chain + explicit aktiválási alkalmak

Magic
→ precíz binding/target/revalidation szemantika

Vanguard
→ trigger standby + check timing
→ nagyon tiszta combat revalidation

Duel Masters
→ explicit one-by-one trigger processing
→ resolution-time choice precedens

és mindezt a már elkészült AETERNA Reaction/Priority foundation köré építjük.

Azt hiszem, ezen a ponton már nem további forrásjátékokat kell gyűjtenünk. A fő strukturális megoldások ismétlődni kezdtek, ami jó jel: elértük azt a pontot, ahol már többet nyerünk a saját rendszerünk felépítésével, mint újabb TCG-k boncolásával.

A következő lépésben ezért már elkezdeném szisztematikusan felépíteni az AETERNA saját Timing & Resolution Frameworkjét, de még mindig csak koncepcionális szabályként, nem contractként és nem kódként. Elsőként a teljes lifecycle-t raknám le az EVENT → TimingAnchor → TriggerCandidate → ReactionTimingWindow → Stack → Resolution → Checkpoint tengelyen, és utána egyenként illesztenénk bele a fix szemantikai paramétereket. Így nem veszítjük szem elől a célt sem: amint ez a minimum stabil, visszakötjük a Combat + Pecsét rendszerhez és a szomszédos védelmi koncepcióhoz.