Rendben. Most akkor **nem v0.2-t készítek**, hanem összegyűjtöm a v0.1-ben és az utána felmerült kérdéseket, hogy utána egyben tudjuk őket végignézni.

Fontos pontosításként felveszem a válaszodat erre a kérdésre:

> A jelenlegi Python motort hosszú távú backendnek próbáljuk alkalmassá tenni, vagy csak működő referenciának tekintjük, amely mellett megtervezünk egy új, játékprogramhoz jobban illő architektúrát?

**Válaszod állapota:** nem előre eldöntött irány. Azt kell választani, amelyik vizsgálat alapján hatékonyabbnak bizonyul.

Ez a v0.2-ben így jelenhet majd meg:

> A Python motor sorsa nem ideológiai döntés. A jelenlegi motor lehet hosszú távú backend, átmeneti referencia, vagy részben újraírandó rendszer. A döntést hatékonysági, Godot-kompatibilitási, karbantarthatósági és új célarchitektúra-szempontú vizsgálat alapján kell meghozni.

## Összegyűjtött döntési kérdések

### 1. Fő cél és termékszemlélet

1. A projekt hivatalos elsődleges célja továbbra is a **fizikai TCG** legyen?
    
    >igen továbbra is ez a cél. viszont mivel nagyon idő és erőforrás igényes ezért koncentrálok most kissé jobban a programra.

2. A digitális programot hogyan kezeljük?

   * tesztprogramként,
   * játszható melléktermékként,
   * vagy hosszú távon önálló digitális játékprogramként is?

   >nos ezek összessége föként

3. A három digitális mód hivatalos célstruktúra legyen?

   * AI vs AI,
   * AI vs játékos,
   * játékos vs játékos.

   >igen jelenleg igy gondolom viszont az AI vs. AI inkább teszteszköz

4. A digitális gyűjtemény, valuta, booster opening, jutalomrendszer maradjon távoli jövőkép, vagy már most külön „későbbi digitális termékréteg” státuszt kapjon?

    >szerintem meg kell teremteni a lehetőségét hogy ne utúlag keljen mindent átalakitani miatta

5. A projekttervben rögzítsük-e külön, hogy a digitális program nem írhatja felül a fizikai kártyajáték szabályi és balanszlogikáját?

    >igen mindenképpen a tervezésnél nagyon fontos lesz hogy nem elsősorban a program ban lesz a játék ezért nem lehet olyan megoldáokat használni ami programban müködik jól

### 2. Az „újrakezdés” jelentése

6. Az újrakezdés alatt pontosan mit értünk?

   * teljes technikai újraírást,
   * célarchitektúra újragondolását,
   * fokozatos refaktort,
   * vagy ezek kombinációját?

   >a kombinációját mondanám de inkább szerintem az újrairás lenne a jobb. ami a legmegfelelőbb lesz a projektnek

7. A jelenlegi programot minek tekintsük?

   * hosszú távú backend-jelöltnek,
   * működő referenciának,
   * átmeneti tesztmotornak,
   * vagy olyan alapnak, amelyből csak részeket mentünk át?

    >jelenleg ez müködö referencia és átmeneti tesztmotor, szerintem viszont inkább alap legyen amiből részeket mentünk át amenyiben van haszna

8. Milyen szempontok alapján döntsük el, hogy megtartás, refaktor vagy újraírás a jobb?

   * Godot-kompatibilitás,
   * karbantarthatóság,
   * meglévő működés értéke,
   * kódkomplexitás,
   * adatexportok kezelése,
   * későbbi bővíthetőség,
   * Codex által kezelhetőség.

   >ez mind fontos szempontnak tünik nekem ezen még kell gondolkodni

### 3. Technológiai irány

9. A Python maradjon-e hosszú távú backendnek, ha alkalmasnak bizonyul?

    >ha alkalmasnak bizonyul akkor maradhat

10. Kell-e külön technikai vizsgálat arról, hogy Python backend + Godot frontend mennyire jó irány?

    >igen szerintem kell

11. Mikor tekinthető indokoltnak a nyelvváltás vagy újraírás?

    >ha bármit akadáyoz azok közül amit a 8. kérdésben felsoroltál

12. A Godot-kompatibilitást már most kötelező architektúra-szempontként kezeljük-e, még akkor is, ha Godot-fejlesztést nem kezdünk azonnal?

    >szerintem igen ha kell erről még folytatunk vizsgálatokat

13. Kell-e már most egy minimális backend-contract gondolkodás?

* game snapshot,
* legal actions,
* apply action,
* event log,
* validation result,
* AI step.

>szerintem kell 

### 4. Könyvtár- és fájlszerkezet

14. A mappaszerkezet átalakítása cleanup-feladat legyen, vagy új célarchitektúra-tervezési feladat?

    >szerintem mindkettő együtt

15. Előbb teljes fájlstátusz-audit kell, mielőtt bármit törlünk vagy Archive-ba teszünk?

    >mindenképpen

16. Milyen státuszkategóriákat használjunk?

* active runtime,
* supporting runtime,
* wrapper,
* docs,
* tests,
* reports,
* audit,
* legacy,
* archive candidate,
* inspect further.

    >ezt nem tudom pontosan megmondani. amire szükség lesz gondolom

17. A régi fájloknál a cél inkább törlés legyen, vagy biztonságos archiválás?

    >azokat kell archiválni amik fontosak voltak és nincsenek esetleg átvezetve egy másik fájlban 

18. Kell-e külön új, célarchitektúra-alapú mappaterv, amely nem feltétlenül követi a mostani Python-projekt szerkezetét?

    >szerintem szükséglehet rá

### 5. Exportalapú adatút

19. A `CARDS_MASTER` maradjon-e szerkesztési master?

    >egy .xlsx fájl amit szerkesztek annak egyik lapja ez. ebből készül az export. a kártyák elsődleges forrása volt ebből készült másolat az `EXPORT_RUNTIME` lapra.

20. Az `EXPORT_RUNTIME` legyen-e a program elsődleges runtime kártyaforrása?

    >egy .xlsx fájl amit szerkesztek annak egyik lapja ez. ebből készül az export. a kártyák program által használt forrása.

21. A `PRODUCT_DECKLISTS` export legyen-e a paklik elsődleges runtime forrása?

    >egy .xlsx fájl amit szerkesztek annak egyik lapja ez. ebből készül az export. igen ebbél vegye a program a paklikat.

22. A LOOKUPS / értéklisták is exportként kerüljenek-e a programba?

    >a LOOKUPS már külön dokumentumban van. annak a lapjait fogom exportáltatni a programmal.

23. Legyen-e különbség:

* szerkesztői export,
* validált runtime export,
* program által ténylegesen használt compiled export között?

    >szerkesztői export nincs jelenleg csak forrás fájl, de lehet hogy később kelleni fog egy szerkesztő program főleg ha esetleg zárt fájlokkal dolgozunk. szerintem talán ez lehet a külömbség pont hogy a program által használt végleges verzió a compiled export fájlok nem szerkeszthetőek viszont a runtime export még igen.

24. Ha kézzel módosítasz egy exportot, az hivatalos munkamód legyen, vagy csak ideiglenes tesztelési / javítási lehetőség?

    >magukat az exportokat jelenleg nem szerkesztem. ha modosítást végzek akkor az .xlsx fájlt modosítom és abból készitek új exportot

25. A programnak mit kell tennie, ha hibás exporttal találkozik?

* leáll errorral,
* warningot ad és továbbmegy,
* fallbacket használ,
* hibariportot készít.

    >nem tudom. a hibától függ szerintem. jelenleg amig fejlesztünk talán az a legjobb ha leáll és készit reportot hogy lássuk mi volt a hiba.

26. Kell-e külön exportvalidációs lépés a program futtatása előtt?

    >lehetséges hogy igen legalábbis a jelenlegi formájában. a végleges verzó müködésben lehet hogy kicsit eltér majd

### 6. LOOKUPS és értéklisták

27. A LOOKUPS egyetlen nagy fájl legyen, vagy több tematikus fájl?

    >én több fájlra gondoltam de jelezted hogy az hibákhoz vezethet. talán at a legjobb ha készít egy nagy fájlt belőle

28. Szerkesztéshez külön fájlok legyenek, programnak pedig összefűzött validált export?

    >én jelenleg az .xlsx fájlt szerkesztem. a programnak valoszinüleg az ősszefüzött validált export lesz a legjobb

29. A Google Sheets / Excel maradjon-e a fő szerkesztési felület?

    >jelenleg igen. amint problémás lesz vagy lesz/szükséges jobb megoldás lecserélem

30. A LOOKUPS-ban minden `Value` kódbarát, angol vagy ASCII `snake_case` legyen?

    >szerintem igen

31. A magyar megjelenítési név külön `Label_HU` mezőben legyen?

    >szerintem igen

32. A legacy / archív értékek maradjanak-e elkülönített alias rétegben?

    >szerintem igen

33. Mikor tekintjük lezártnak a `RUNTIME_LEGACY_ALIAS` munkát?

    >egy ellenőrzés még mindenképpen kell. utánna valoszinüleg lezárhatjuk.

34. Kell-e még külön `audit_required` / veszélylista a kétes structured értékekhez?

    >szerintem igen

### 7. Structured → programlogika

35. Először csak lookup-validáció legyen, vagy már most tervezzük meg a structured → végrehajtási mappinget?

    >szerintem már tervezhetjük

36. A programnak minden kulcsszóhoz legyen konkrét futtatható logikája?

    >szerintem igen

37. A triggerekhez is legyen konkrét programoldali jelentés?

    >szerintem igen

38. A célpontértékekhez is legyen programoldali érvényesség-ellenőrzés?

    >szerintem igen

39. A hatáscímkék csak diagnosztikai címkék legyenek, vagy később végrehajtási modulokat is indítsanak?

    >ezt most nem tudom. ha szükséges lesz akkor igen

40. A képességek hosszú távon modulokból épüljenek fel, ne kártyánként külön kódból?

    >szerintem igen. esetleg kiegészíttő kód ha szükségessé válik. mivel rengeteg kártya lesz mindnek külön megirne hatalmas munka lenne

41. Hogyan kezeljük azokat a kártyákat, amelyek jelenleg card-local, név-alapú handlerrel működnek?

    >át kell vezetni az új rendszerbe 

42. Kell-e átmeneti vegyes rendszer:

* structured-alapú,
* shared handler,
* card-local fallback?

    >szerintem csak akkor ha nem lehet megoldani másképpen

### 8. Log / Warn / Error / Audit rendszer

43. Egy közös diagnosztikai rendszer legyen, vagy több külön réteg?

    >amelyik megfelelőbb mert mind a kettőnek van előnye és hátránya is

44. Kell-e külön:

* export validation log,
* runtime error log,
* engine warning log,
* audit warning log,
* balance/test report?

    >szerinetm mind kell

45. Mi számít errornak?

    >error szerintem az ami blokkolja a müködést

46. Mi számít warningnak?

    >warning szerintem figyelmeztetés nem akadályozza a müködés de mindenképpen megoldandó

47. Mi számít audit note-nak?

    > olyan megjegyzés amit kikell vizsgálni

48. Mi számít balance suspicionnek?

    >ezt még át kell beszélnünk

49. Ha egy kártya szabályosan fut, de structured mezője pontatlan, az warning vagy audit issue legyen?

    >valoszinüleg mindkettő

50. Ha egy kártya structured mezője jó, de engine nem támogatja, az engine warning vagy error?

    >valószinüleg mindkettő de föleg error

51. A warningok blokkolják-e a futtatást, vagy csak riportba kerülnek?

    >szerintem elég ha riportba kerülnek

### 9. Szabályforrások új formái

52. Maradjon-e a két 1.4v főforrás a hivatalos szabályi alap?

    >igen de kell majd még modositás

53. Készüljön-e később külön játékosbarát szabálykönyv?

    >igen de csak ha javitva lett a főforrás

54. Készüljön-e külön AI / Codex / engine-barát szabályspecifikáció?

    >igen de csak ha javitva lett a főforrás

55. A főforrások hibáit mikor és hogyan javítsuk?

* azonnal,
* külön auditkörben,
* csak ha konkrét kártya/engine munka közben előkerülnek?

    >kell egy külön audit kör, de mindenképpen mielőtt elkészitjük a külön verziókat

56. A szabályforrások gépbarát átalakítása legyen-e külön projektfázis?

    >szerintem igen

### 10. Kártyaaudit és balansz

57. Mikor induljon új kártyaaudit?

    >ha tudunk teszteket folytatni

58. Előbb az adatút, LOOKUPS és validáció stabilizálódjon, és csak utána kezdődjön a balansz-audit?

    >igen

59. A korábbi javítások után külön ellenőrizzük-e, hogy a lapok nem lettek-e túlgyengítve?

    >igen

60. Rögzítsük-e hivatalos balanszfilozófiaként, hogy nem a steril 5/10 egyensúly a cél?

    >igen

61. Elfogadjuk-e a 6–7/10 identitásérvényesülési célt?

    >igen

62. Hogyan akadályozzuk meg, hogy a játék kő-papír-olló jellegű legyen?

    >figyelni kell az egyensúlyt és a tervezést ugy kell folytatni hogy ne legyen egyik a másik ellen fejlesztve

63. Hogyan különítsük el:

* balanszhibát,
* engine-hibát,
* kártyaadat-hibát,
* structured-hibát,
* szabályforrás-hibát?

    >hát nem tudom talán a logokban legyen jelezve

64. A klánidentitás megőrzése erősebb prioritás legyen-e, mint a teljesen egyenletes winrate?

    >igen. figyelni kell a winrate azért ne essen le 40-60 alá

### 11. Codex / ChatGPT / emberi döntés

65. Mi maradjon emberi döntés?

    >a döntések fussanak keresztül rajtam

66. Mit kezeljen ChatGPT?

* döntési térképek,
* projektirány,
* auditlogika,
* szabályértelmezés,
* Codex-promptok.

    >ezt mindet 

67. Mit kapjon Codex?

* célzott kódellenőrzés,
* tesztek,
* loader validáció,
* export validáció,
* kisebb refaktorok.

    >ezt mindet

68. Milyen feladatot ne adjunk Codexnek?

* teljes projektirányítás,
* nagy automatikus refaktor,
* szabályi döntés,
* kártyabalansz véglegesítés.

    >ezeket ne kapja a codex

69. Kell-e minden Codex-feladat előtt rövid, konkrét prompt és elvárt kimenet?

    >igen

### 12. Következő munkasorrend

70. Először a döntési térképet véglegesítsük v0.2-vé?

    >igen

71. Utána készüljön egy hatékonysági vizsgálati terv a Python motor / új architektúra kérdésre?

    >igen

72. Utána készüljön exportalapú adatút-terv?

    >igen

73. Utána LOOKUPS / structured / validation terv?

    >igen

74. Utána Log / Warn / Error rendszerterv?

    >igen

75. Csak ezek után kezdjünk új kártyaauditot?

    >igen

## Külön feljegyzett válaszod

A Python motor sorsa:

**Nem előre eldöntött.**
Azt kell választani, amelyik a leghatékonyabbnak bizonyul.

Ez azt jelenti, hogy a v0.2-ben nem azt írjuk, hogy „Python marad”, és nem is azt, hogy „újraírjuk”. Hanem azt:

> Döntési kapu szükséges: meg kell vizsgálni, hogy a jelenlegi Python motor hatékonyabban alakítható-e hosszú távú backenddé, vagy jobb egy új, játékprogramhoz és Godot-kompatibilis működéshez igazított architektúrát tervezni, amelyhez a jelenlegi motor referencia- és átmeneti tesztalapként szolgál.

Szerintem ezek azok a kérdések, amelyeket egyben érdemes majd megvizsgálni. Utána a válaszaidból már sokkal pontosabb v0.2 döntési térkép készíthető.
