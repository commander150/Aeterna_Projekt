# AETERNA – GitHub Munkarend és Commit Szabályok

Ez a dokumentum az AETERNA projekt GitHub-alapú munkarendjét rögzíti.

Célja:
- a változtatások követhetőségének javítása
- a különböző típusú munkák elkülönítése
- a commitok és branchek tudatosabb használata
- a projekt későbbi átláthatóságának és visszakövethetőségének biztosítása

Ez a dokumentum nem haladó Git kézikönyv.  
Elsődleges célja egy egyszerű, gyakorlatias rend kialakítása az AETERNA projekthez.

---

## 1. Alapelv

A GitHubot a projektben nem csak tárolásra, hanem követhető fejlesztési működésre kell használni.

A fő szabály:

**Egy változtatási egység = egy világos cél = egy jól azonosítható commit vagy commit-sorozat.**

A GitHub használatával azt akarjuk elérni, hogy később egyértelmű legyen:
- mi változott
- miért változott
- melyik módosítás mit javított
- melyik változtatás melyik problémához vagy célhoz kapcsolódott

---

## 2. Mit NE csináljunk

Az alábbiakat lehetőleg kerülni kell:

- ne keveredjen ugyanabba a commitba runtime-kód és dokumentációs nagyrendezés
- ne keveredjen ugyanabba a commitba cleanup és új mechanika
- ne keveredjen ugyanabba a commitba tesztbővítés és teljes report-rendezés
- ne legyenek „mindent egyszerre” commitok
- ne legyenek értelmezhetetlen commitüzenetek
- ne maradjanak félkész, véletlen vagy véletlenszerű állapotok dokumentálatlanul a fő ágon

---

## 3. Commit szabályok

### 3.1 Egy commit egy fő célt szolgáljon

Jó példák:
- egy konkrét logjavítás
- egy konkrét mechanikai fix
- egy konkrét dokumentációfrissítés
- egy konkrét cleanup lépés
- egy konkrét tesztbővítés

Rossz példa:
- runtime fix + README frissítés + report átrendezés + logfájl törlés egyetlen commitban

### 3.2 A commit legyen emberileg értelmezhető

A commitból később is látszódjon:
- mit javított
- mit rendezett
- melyik réteget érintette

### 3.3 Előbb kisebb, tiszta commit, mint nagy, kusza commit

Ha egy munka több részre bontható, inkább több kisebb commit legyen, mint egy nehezen átlátható nagy csomag.

---

## 4. Ajánlott commit-típusok

A projektben érdemes fejben legalább ezeket a kategóriákat használni:

### Runtime
A motor működését ténylegesen érintő változások.
Példák:
- effect fix
- targeting fix
- trigger adapter
- summary javítás
- canonical runtime batch

### Tests
Tesztfájlok, unittest bővítések, regressziós lefedések.

### Docs
Dokumentációs módosítások:
- README
- projektterv
- projekt-térkép
- architektúra-fájl

### Cleanup
Rendezés, átnevezés, szerkezeti tisztítás, de nem új funkció.

### Reports / Stats
Audit, summary, batch report, compliance anyagok rendezése vagy generálása.

### Tooling
Fejlesztői segédfájlok, script-ek, log- és workflow-segédeszközök.

---

## 5. Ajánlott commitüzenet-forma

A commitüzenet legyen rövid, de konkrét.

Ajánlott minta:

`<terület>: <mi változott>`

Példák:
- `runtime: fix seal break metrics in structured path`
- `logging: add block reason prefixes for spell target failures`
- `docs: add project guidance documents to readme`
- `cleanup: reorganize stats report categories`
- `tests: add coverage for trap consume summary`
- `project-map: document engine and cards folders`

Egyszerűbb rövid magyar változat is elfogadható, ha következetes:
- `runtime: pecsettöres számláló javítása`
- `docs: readme frissítése`
- `cleanup: stats mappa kategorizálása`

A fontos az egyértelműség.

---

## 6. Mikor kell külön branch

### Külön branch ajánlott, ha:
- a módosítás több fájlt érint
- a módosítás kockázatosabb
- cleanup és rendezés történik
- egy újabb nagyobb batch indul
- nem biztos, hogy elsőre jó lesz a megoldás
- több napon át tartó munka indul

### Nem feltétlen kell külön branch, ha:
- nagyon kicsi dokumentációs javításról van szó
- apró, gyors és egyértelmű fix történik
- biztosan nem keveredik mással

---

## 7. Ajánlott branch-elnevezés

Az elnevezésből látszódjon, mi a cél.

Példák:
- `docs/project-map`
- `docs/readme-guidance`
- `cleanup/stats-structure`
- `runtime/canonical-batch-8`
- `runtime/trigger-fix`
- `logging/improvement-pass-3`
- `tests/trap-regression`
- `refactor/shared-actions-split`

---

## 8. Mit érdemes együtt commitolni

### Együtt mehet:
- egy runtime fix és a hozzá tartozó teszt
- egy dokumentációs változás és a kapcsolódó másik dokumentációs változás
- egy cleanup lépés és az azt leíró cleanup dokumentáció

### Ne menjen együtt:
- runtime javítás és nagy report-rendezés
- logikai fix és stats mappa nagytakarítás
- mechanikai batch és projektterv-frissítés, ha nem közvetlenül kapcsolódnak
- README szerkesztés és véletlen kódfixek

---

## 9. Projekt-specifikus munkarend

AETERNA esetében a munkák előtt mindig tisztázni kell, hogy a feladat melyik kategóriába tartozik:

- core runtime
- supporting runtime
- wrapper
- docs
- tests
- stats/report
- cleanup/refaktor

Ez azért fontos, mert a projekt jelenleg hibrid és többféle réteg él együtt:
- structured / canonical
- shared helper alapú
- card-local név-alapú
- report / audit / historical

Ha a kategória nincs tisztázva, könnyen összekeverednek a célok.

---

## 10. Javasolt minimál napi rutin

### Munka előtt
1. Nézd meg, mi a mostani konkrét cél.
2. Sorold be a munkát kategóriába.
3. Döntsd el, kell-e külön branch.

### Munka közben
1. Egy irányba haladj.
2. Ne keverj bele más típusú módosítást.
3. Ha új mellékszál jön elő, jegyezd fel külön, ne ugyanabban a commitban oldd meg.

### Munka végén
1. Nézd meg, pontosan mi változott.
2. Írj egyértelmű commitüzenetet.
3. Ha kell, frissítsd a megfelelő dokumentumot:
   - README
   - projekt-térkép
   - projektterv

---

## 11. Mikor kell dokumentációt is frissíteni

### README frissítendő, ha:
- új irányító dokumentum jön létre
- változik a projekt belépési logikája
- változik az alap munkaszabály

### Projekt-térkép frissítendő, ha:
- új fájl vagy mappa fontos szerepet kap
- egy fájl státusza változik
- kiderül, hogy valami aktív runtime / wrapper / report / archive kategóriába tartozik

### Projektterv frissítendő, ha:
- változik a fő prioritás
- új stratégiai cél jelenik meg
- változik a fejlesztési fókusz
- új hosszú távú architektúra-cél kerül be

---

## 12. Stats és report fájlok kezelése

Az AETERNA projektben különösen figyelni kell arra, hogy a `stats/` mappa ne keveredjen össze a tényleges runtime-kóddal.

Ezért:
- report-rendezés lehetőleg külön branch vagy külön commit legyen
- audit és compliance fájlok ne keveredjenek mechanikai fixekkel
- generált vagy történeti summaryk ne kerüljenek egy csomagba core runtime javításokkal

---

## 13. Mit nyerünk ezzel a renddel

Ha ezt a rendet követjük, akkor:
- könnyebb lesz visszakeresni a hibákat
- könnyebb lesz megérteni, mi történt a projektben
- könnyebb lesz a dokumentációt naprakészen tartani
- könnyebb lesz külső segítséget bevonni
- könnyebb lesz később Godot-integrációra készülni
- csökken annak az esélye, hogy a projekt újra átláthatatlanná válik

---

## 14. Gyakorlati minimumszabály

Ha semmi másra nincs idő, legalább ezeket mindig tartsuk be:

1. Egy commit egy fő célt szolgáljon.
2. A commitüzenetből látszódjon, mi változott.
3. Runtime, docs és stats/report ne keveredjen össze feleslegesen.
4. Nagyobb vagy kockázatosabb munkához használjunk külön branch-et.
5. Ha változik a projekt működési rendje, frissítsük a megfelelő dokumentumot is.

---

## 15. Verziózás

### v1
- elkészült az első egyszerű GitHub munkarend
- commit- és branch-használati alapelvek rögzítve
- a projekt sajátos hibrid működéséhez igazított szabályok bekerültek
