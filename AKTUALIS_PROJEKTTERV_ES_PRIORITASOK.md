# AETERNA – Aktuális Projektterv és Prioritások

Ez a dokumentum az AETERNA projekt aktuális, élő munkatervét tartalmazza.

Célja:
- a projekt fő irányainak rögzítése
- az aktuális fókuszok kijelölése
- a rövid, közép- és hosszú távú célok elkülönítése
- a feladatok priorizálása
- a GitHub-alapú munkarend egyszerűsítése
- egy olyan központi referencia fenntartása, amelyet könnyű bővíteni, módosítani vagy egyszerűsíteni

Ez a dokumentum **nem technikai specifikáció**, és **nem részletes fejlesztői log**.  
Elsődleges célja az, hogy a projektgazda számára átlátható és követhető legyen, hogy:
- mi a projekt valódi célja
- min dolgozunk most
- mi a következő logikus lépés
- és mit kell kerülni

---

# 1. A projekt jelenlegi iránya

Az AETERNA jelenleg egy Python-alapú, szabálymotor-központú kártyajáték-projekt.

A jelenlegi motor fő feladata:
- a kártyák és mechanikák szabályhű kezelése
- AI-vs-AI tesztmeccsek futtatása
- a structured kártyaadatok felhasználása
- a mechanikák fokozatos engine-integrációja

A projekt **nem nulláról újraépítendő rendszerként** van kezelve.  
A jelenlegi stratégia:

1. feltérképezés
2. stabilizáció
3. cleanup / rendezés
4. célzott refaktor
5. csak ezután részleges újraírás, ha tényleg szükséges

---

# 2. A projekt fő céljai

## 2.1 Rövid távú fő cél
A jelenlegi rendszer pontos feltérképezése és stabilizálása.

Ez azt jelenti:
- tudjuk, melyik fájl mi
- tudjuk, mi aktív runtime és mi nem
- tudjuk, melyik réteg tiszta és melyik refaktorra szorul
- a futó motor diagnosztikailag követhető legyen

## 2.2 Középtávú fő cél
A jelenlegi structured szabvány és a működő motor jobb összekapcsolása.

Ez azt jelenti:
- a szabványos mezők valódi mechanikákat hajtsanak meg
- a még hiányzó vagy részleges mechanikák bekötése folytatódjon
- a card-local és shared/runtime rétegek viszonya tisztuljon

## 2.3 Hosszú távú fő cél
A projektből használható, játszható játékeszköz legyen.

Célállapot:
1. AI-vs-AI tesztmotor
2. ember-vs-AI játszható rendszer
3. később ember-vs-ember irány

## 2.4 Architektúra-cél
A jelenlegi Python motor készüljön fel arra, hogy később Godot frontendhez kapcsolható backendként működjön.

Ez azt jelenti:
- a mostani munkáknál figyelni kell a tiszta határokra
- a motor ne ragadjon bele a jelenlegi konzolos/logalapú működésbe
- később lehessen rá vizuális réteget kötni anélkül, hogy a teljes motort újra kellene írni

---

# 3. Jelenlegi aktív fókusz

## Elsődleges fókusz
A projekt szerkezetének és fájlrendszerének feltérképezése.

Ennek célja:
- világossá tenni, mi micsoda
- elkülöníteni az aktív runtime-ot a report / audit / történeti rétegektől
- előkészíteni a későbbi cleanupot és refaktort

## Másodlagos fókusz
A logikus, követhető projektműködés kialakítása.

Ennek része:
- könnyen kezelhető célrendszer
- GitHub követhetőbb használata
- dokumentáció és projektterv összerendezése

## Harmadlagos fókusz
A meglévő motor mechanikai és architektúra-szintű stabilizációja.

---

# 4. Amit most NEM csinálunk

A jelenlegi fázisban kerülendő:

- teljes újrakezdés 0-ról
- új nagy mechanikai család nyitása csak azért, hogy több funkció legyen
- új frontend építése a backend tisztázása előtt
- több irány egyszerre történő erőltetése
- jelentős fájltörlések pontos feltérképezés nélkül
- runtime, audit és dokumentációs változtatások összekeverése egyetlen nagy lépésben

---

# 5. Jelenlegi munkablokkok

## 5.1 Projekt-feltérképezés
Állapot: folyamatban

Cél:
- a főmappák és fájlok feltárása
- szerepek és státuszok rögzítése
- a `PROJEKT_TERKEP_ES_FAJLSTATUSZ_v1.md` dokumentum bővítése

Jelenlegi ismert fókuszterületek:
- `engine/`
- `cards/`
- `data/`
- `simulation/`
- `utils/`
- `stats/`

## 5.2 Runtime stabilizáció
Állapot: részben folyamatban

Cél:
- a jelenlegi motor stabil működésének fenntartása
- a canonical/shared runtime fejlesztések követhetővé tétele
- a fő hibák és hiányok célzott kezelése

## 5.3 Logikai és diagnosztikai átláthatóság
Állapot: részben javítva

Cél:
- a logokból könnyebben látszódjon, mi történt
- shared pathok és blokk-okok követhetők legyenek
- meccssummaryk használhatóak legyenek

Megjegyzés:
ez a kör jelentősen javult, jelenleg nem ez az első számú fókusz.

## 5.4 `stats/` mappa rendezése
Állapot: előkészítés alatt

Cél:
- az aktív statisztikai runtime elem elkülönítése
- a reportok, batch summaryk, compliance auditok és egyszeri script-ek szétválasztása
- későbbi cleanup és mappaszerkezeti rendezés előkészítése

## 5.5 Godot-integráció előkészítése
Állapot: jövőbeli architektúra-cél

Cél:
- a jelenlegi motor ne zárja ki a későbbi vizuális frontend bekötését
- a tiszta állapotkezelés és action-határok kialakítása
- későbbi backend–frontend interfész előkészítése

---

# 6. Prioritási sorrend

## P1 – Azonnali prioritás
1. projekt-feltérképezés befejezése
2. a projekt-térkép dokumentum bővítése
3. a fő rétegek elkülönítése:
   - core runtime
   - supporting runtime
   - wrapper
   - tests
   - docs
   - reports / audits
   - archive / cleanup candidates

## P2 – Következő prioritás
1. `stats/` mappa rendezési terve
2. GitHub munkarend egyszerűsítése
3. a fő refaktor-célpontok kijelölése

## P3 – Középtávú prioritás
1. mechanikai hiányok célzott folytatása
2. structured ↔ card-local ↔ shared runtime viszony tisztítása
3. engine-határok jobb elkülönítése

## P4 – Hosszú távú prioritás
1. backend API-szerű gondolkodás előkészítése
2. Godot-kötés előfeltételeinek kidolgozása
3. későbbi játszható frontend

---

# 7. Jelenlegi fő megállapítások

A feltérképezés eddigi állása alapján:

## 7.1 Nem minden réteg problémás
Rendezettebbnek tűnő rétegek:
- `data/`
- `simulation/`
- `utils/`

## 7.2 A vegyesebb, később refaktorálandó rétegek
- `engine/`
- `cards/`

## 7.3 A legerősebb cleanup-jelölt jelenleg
- `stats/`

## 7.4 A projekt jelenleg inkább hibrid, mint szétesett
Ez azt jelenti:
- van structured irány
- van shared helper irány
- van card-local név-alapú irány is
- és ezek együtt élnek

Ez refaktorálási feladatot jelent, nem automatikusan teljes újrakezdést.

---

# 8. GitHub használati alapelvek

A GitHubot a jövőben nem csak tárolásra, hanem követhető munkarendre is használni kell.

## 8.1 Alapelv
Egy commit egy jól körülírható célt szolgáljon.

Példák jó commit-típusokra:
- egy konkrét logjavítás
- egy konkrét mechanikai batch
- dokumentáció frissítés
- cleanup / rendezés
- tesztbővítés

## 8.2 Amit nem szabad keverni egy commitban
Lehetőleg ne keveredjen egyetlen commitba:
- runtime kódmódosítás
- dokumentációs rendezés
- reportfájl-rendezés
- nagytakarítás
- logfájlok vagy generált kimenetek

## 8.3 Commit üzenetek
A commit üzenetek legyenek rövidek, de egyértelműek.

Példák:
- `stabilize logging summaries`
- `add canonical trap consume metrics`
- `document engine and cards folders`
- `reorganize stats reports`
- `refactor shared source placement path`

## 8.4 Branch használat
Ha fontosabb vagy kockázatosabb munkáról van szó, érdemes külön branch-et használni.

Példák:
- `docs/project-map`
- `cleanup/stats-structure`
- `runtime/canonical-batch-8`
- `logging/improvement-pass-2`

## 8.5 Mit nyerünk ezzel
- visszakövethető lesz, mi változott
- könnyebb lesz hibát visszakeresni
- könnyebb lesz dokumentálni a haladást
- könnyebb lesz külső segítséget bevonni
- könnyebb lesz később frontend-integrációra készülni

---

# 9. Jelenlegi dokumentumrendszer

A projektben jelenleg külön szerepet töltenek be ezek a dokumentumok:

## 9.1 Projekt-térkép
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ_v1.md`
- cél: mi micsoda, mi mire való, milyen státuszú

## 9.2 Hivatalos futási út
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`
- cél: a jelenlegi hivatalos runtime és core/wrapper elhatárolás rögzítése

## 9.3 Aktuális munkairány
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK.md`
- cél: a projekt működési és prioritási irányainak követése

## 9.4 Egyéb technikai háttérdokumentumok
- szabvány
- effect-határok
- seed-konvenció
- cleanup-jelöltek
- fejlesztési terv
- külön audit- és reportfájlok

---

# 10. Következő konkrét lépések

## Rövid távon
1. a projekt-térkép dokumentum további bővítése
2. a maradék fontos mappák feltárása
3. a `stats/` mappa későbbi rendezési tervének előkészítése

## Ezután
1. a fő refaktor-célpontok kijelölése
2. GitHub használati rend tényleges alkalmazása
3. a jövőbeli backend-határok tudatosítása

## Később
1. Godot-integrációs előfeltételek összegyűjtése
2. backend API-szerű gondolkodás kialakítása
3. vizuális frontend irányába nyitás

---

# 11. Egyszerű státuszblokk

## Kész / előrehaladott
- structured adatoldal működik
- a fő futási út dokumentálva van
- a logolás használhatóbb lett
- a projekt-térkép építése megkezdődött
- több főmappa szerepe tisztábban látszik

## Folyamatban
- részletes fájl- és mappafeltérképezés
- célok és prioritások rendezése
- cleanupra alkalmas területek azonosítása

## Még előttünk áll
- `stats/` tényleges rendezése
- fő refaktorirányok kijelölése
- backend–frontend előkészítés
- későbbi Godot-kompatibilis architektúra-határok pontosítása

---

# 12. Verziózás

## v1
- elkészült az első központi projektterv
- a fő célok és prioritások rögzítve
- a GitHub használati alapelvek bekerültek
- a projekt jelenlegi fázisa és fókusza tisztázva