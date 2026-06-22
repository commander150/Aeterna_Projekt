# Aeterna kártyajáték újratervezése

mivel a projekt hatalmasra nőtt már nem tudjuk kezelni az eddigi megközelittéssel. Ezért szerintem eljött az ideje egy nagyobb reworknek. Nem szeretnék mindent kidobni de jelenleg ugy akarok hozzá álni hogy szinte tiszta lappal kezdjük el.

## 0. lépés Célok újrameghatározása

az eddigi megközelittés már nem fog müködni. a korábbi cél az volt hogy készitsünk egy teszteszközt amit később átalakitunk játékra alkalmassá. 
ezzel szemben jelenleg már rögtön ugy tervezzük meg az egészet hogy ez egy játék program lesz.
ugyanugy szeretném tesztelésre is használni de a jelenlegi forma inkább 3 főbb része lesz: az AI vs. AI ez lesz ami teszt eszközként fog funkcionálni, az AI vs. Játékos ez is szolgálhat tesztelési célokat de ez inkább már a játszható játék felé mozdul, és az utolsó a Játékos vs. Játékos ez téynleg csak játék célőkra lesz főleg de mellete lehet gyüjteni log adatokat ebből is.
arra gondolok hogy hasonlo lehetne maga a játék mint a Hearthstone vagy a Yugioh Master Duel itt gondolok arra hogy lehet gyüjteni a kártyákat a gyözelmekért kapsz valutát amivel lehet venni csomagokat amiből lehet szerezni új kártyákat.
fontos feltétel még hogy az alapvető cél maga a játék létrehozása ezen bellül lesz a program de az igazi prioritás a TCG tehát a valódi fizikai kártyjáték megalkotása.
A program és a kód tervezésekor figyelembe kell venni hogy a Godot engine szeretnénk használni a vizuális megjelenitésre ezt az ujratervezésnél mindenképpen fiygelembe kell venni.
Jelenleg Python programnyelvet használunk de ha szükséges átválthatunk egy másikra a jobb kompatibilitás miatt.
szükséges fellülvizsgálni a jelenlegi mappa és fájl szerkezetet is.
mindenképpen kell egy jobb felosztás és és mappaszerkezet hogy követhetőbb legyen.
a szükségtelen fájlokat vagy töröni vagy áthelyezni Archive mappába.

## 1. Megoldandó feladatok

a programnak tudnia kell az exportált fájlokból dolgoznia a card.xlsx lecseréljük.
szerintem amugy is átkell alakitani a program törzsét több felé kell bontani a könnyebb kezelhetőség miatt és hogy ne terhelőjön túl a komplex fájlok miatt a kód.
arra is szükség lesz hogy értéklistával dolgozzunk hogy minél kevesebb hiba legyen a LOOKUPS exportot megfelelő formába kell hozni hozzá 


IDEIGLENESEN VÉGE

fontos még hogy szerkeszthető/javitható legyen tehát ha átirom az exportot akkor már abból dolgozzon a program ha pedig esetlegesen emiatt hiba alakul ki azt mindenképpen jelezze
kelleni fog nem csak egy Log rész hanem egy Error rész is amiben lehet ezeket is követni esetleg egy Warn résszel is ez lehet az Error logban
szeretném ha minden értékhez lenne majd egy program kód. ez most ebben a formában hülyén hangzik de megprobálom kifejteni tehát ha a program azt látja hogy "Keyword	bane" akkor már vban hozzá egy kod ami megmondja hogy mit kell csinálnia de szertném ha nem csak a Kulcsszavaknak lenne hanem a Triggerekhez és akár a képességekhez is lenne pontosabban a meglévő rendszerekkel olyan formára kell leforditani a képeségeket hogy ne kitalálnia keljen a programnak hanem meglenne az értelmezése és abból tudná hogy mit kell végre hajtania. ennek nagyon fontos része lenne az is hogy ez moduláris legyen tehát hogy nem minden kártyához kelljen kell irni egy programkodot hanem a megfelelő darabokból kirakra hogy mit kell tennie
át kell majd alakitani a szabályfőforássokat is mert hiába minden igy is maradtak benne hibák amiket majd közben akarok javitani. az átalakitás oylan formában kell hogy történjen hogy egy program is tudja értelmezni a leirt szabályokat tehát egy AI vagy a codex könnyen értse mit várunk el tőle. ezenkivül kell egy olyan forma ami egy játékos vagyis egy ember számára is könnyen érthető, itt fontos azis hogy olyan legyen hogy az is megértse aki semmit nem tud a játékról.
szükség lesz majd egy ujabb kártya auditra is hogy megnézzük nem lettek e tulgyengitve a kártyák fontos hogy megőrizzék az egyediségüket nagyon kényes helyzet lesz ezt beállitani hogy ne legyenek teljesen kiegyesúlyozottzak de ne is legyenek teljesen unbalancedek
felmerült ismét az egyensúly problémája ezeért megprobálom kifejezni mire gondolok. szerintem ha minden tökéletes egyensólyban van az nem jó mert akkor minden egyformának ha hiába vannak egyedi mechanikáik ha nem érvényesülnek igazán. ha ezt egy képzeletbeli szám skálára helyezem 1-10ig akkore azt mondanám hogy az 1 amikor szinte egyáltalán nincs identitás a 10 pedig a maximális identitás érvényesülése. ebben az esetben középpen tehát 5 nél van az egyensúly viszont szerintem az nem jó inkább tolnám elaz érvényesülést 6 vagy 7 maxiumum 7 irányába mert akkor látszik hogy minden klán más. nem szeretném azt sem hogy kő-papir-ollo játékká alakuljon hogy A üti a B mert jó lenne ha mindennek lenne esélye minden ellen maximum kevesebb vagy nehezebb nyerni de szerintem ez adja az élményt.
