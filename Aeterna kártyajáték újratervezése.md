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

