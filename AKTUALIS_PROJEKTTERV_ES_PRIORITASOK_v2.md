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
- a balansz- és hibafelismerés támogatása futás közbeni diagnosztikával

A projekt **nem nulláról újraépítendő rendszerként** van kezelve.
A jelenlegi stratégia:

1. feltérképezés
2. stabilizáció
3. cleanup / rendezés
4. célzott refaktor
5. csak ezután részleges újraírás, ha tényleg szükséges

Ez továbbra is érvényes.
Az új célok **nem lecserélik**, hanem **kibővítik** ezt az irányt.

---

# 2. A projekt fő céljai

## 2.1 Rövid távú fő cél
A jelenlegi rendszer pontos feltérképezése és stabilizálása.

Ez azt jelenti:
- tudjuk, melyik fájl mi
- tudjuk, mi aktív runtime és mi nem
- tudjuk, melyik réteg tiszta és melyik refaktorra szorul
- a futó motor diagnosztikailag követhető legyen
- a tesztprogramból megbízható balanszfigyelő eszköz legyen

## 2.2 Középtávú fő cél
A jelenlegi structured szabvány és a működő motor jobb összekapcsolása.

Ez azt jelenti:
- a szabványos mezők valódi mechanikákat hajtsanak meg
- a még hiányzó vagy részleges mechanikák bekötése folytatódjon
- a card-local és shared/runtime rétegek viszonya tisztuljon
- a szabálymagyarázat és a tényleges engine-viselkedés közti eltérések láthatóvá váljanak

## 2.3 Kibővített középtávú cél
A jelenlegi tesztmotorra építve induljon el egy **kis kockázatú ember-vs-AI előkészítési ág**.

Ez nem teljes UI/UX projektet jelent.
Első célként egy olyan minimális, félvezérelt rendszer előkészítése szükséges, ahol:
- a játékállapot olvasható módon megjeleníthető
- a rendszer ki tudja listázni az érvényes döntéseket
- az ember bizonyos döntéseket kiválaszthat
- a többi lépést továbbra is a motor vagy AI viheti

Ennek első reális formája:
- CLI-alapú vagy félig vezérelt emberi döntési mód
- nem teljes játékfelület
- nem Godot-első megközelítés

## 2.4 Hosszú távú fő cél
A projektből használható, játszható játékeszköz legyen.

Célállapot:
1. AI-vs-AI tesztmotor
2. félvezérelt ember-vs-AI technikai MVP
3. ember-vs-AI játszható rendszer
4. később ember-vs-ember irány

## 2.5 Architektúra-cél
A jelenlegi Python motor készüljön fel arra, hogy később Godot frontendhez kapcsolható backendként működjön.

Ez azt jelenti:
- a mostani munkáknál figyelni kell a tiszta határokra
- a motor ne ragadjon bele a jelenlegi konzolos/logalapú működésbe
- később lehessen rá vizuális réteget kötni anélkül, hogy a teljes motort újra kellene írni

## 2.6 Szabályérthetőségi cél
A projektben külön céllá válik annak vizsgálata, hogy a játék szabályai mennyire jól magyarázhatók el a jelenlegi dokumentumok és a tényleges engine alapján.

Ez azt jelenti:
- legyen külön rules explainability audit
- legyen látható, ha az elképzelt szabály és a motor viselkedése eltér
- a szabálymagyarázat ne csak írott dokumentum, hanem validációs eszköz is legyen

---

# 3. Jelenlegi aktív fókusz

## Elsődleges fókusz
A tesztprogram és a szabálymotor stabilizálása, különösen balanszfigyelő irányban.

Ennek célja:
- világossá tenni, mi micsoda
- elkülöníteni az aktív runtime-ot a report / audit / történeti rétegektől
- a futásból gyorsan látszódjanak a gyanús lapok, mechanikák és szabályütközések
- előkészíteni a későbbi cleanupot és refaktort

## Másodlagos fókusz
A logikus, követhető projektműködés kialakítása.

Ennek része:
- könnyen kezelhető célrendszer
- GitHub követhetőbb használata
- dokumentáció és projektterv összerendezése
- a futás közbeni diagnosztika és summaryk használhatóbbá tétele

## Harmadlagos fókusz
Az ember-vs-AI irány előkészítése kis, kontrollált lépésekben.

Ennek jelenlegi értelme:
- nem teljes játék készítése
- nem új frontend építése
- hanem annak meghatározása, mi kell egy minimális, félig vezérelt emberi döntési módhoz

## Negyedleges fókusz
A szabálymagyarázhatóság ellenőrzése.

Ennek célja:
- mérni, mennyire érthető a játék külső magyarázat alapján
- megtalálni az eltéréseket a dokumentumok, a te elképzelésed és a runtime között

---

# 4. Amit most NEM csinálunk

A jelenlegi fázisban kerülendő:

- teljes újrakezdés 0-ról
- új nagy mechanikai család nyitása csak azért, hogy több funkció legyen
- teljes UI/UX építése a backend és action-réteg tisztázása előtt
- azonnali Godot-first fejlesztés
- több nagy irány egyszerre történő erőltetése
- jelentős fájltörlések pontos feltérképezés nélkül
- runtime, audit és dokumentációs változtatások összekeverése egyetlen nagy lépésben
- teljes, egyszerre történő ember-vs-AI megvalósítás
- az összes kártya tömeges előzetes újraauditja, ha azt a runtime-log természetes módon később is ki tudja jelölni

---

# 5. Jelenlegi munkablokkok

## 5.1 Projekt-feltérképezés
Állapot: folyamatban

Cél:
- a főmappák és fájlok feltárása
- szerepek és státuszok rögzítése
- a projekt-térkép dokumentum bővítése

Jelenlegi ismert fókuszterületek:
- `engine/`
- `cards/`
- `data/`
- `simulation/`
- `utils/`
- `stats/`
- `backend/`

## 5.2 Runtime stabilizáció
Állapot: folyamatban

Cél:
- a jelenlegi motor stabil működésének fenntartása
- a canonical/shared runtime fejlesztések követhetővé tétele
- a fő hibák és hiányok célzott kezelése
- a structured és non-structured execution pathok közti eltérések felszínre hozása

## 5.3 Balanszfigyelő tesztprogram
Állapot: aktív fő fókusz

Cél:
- a tesztprogramból valódi balanszfigyelő eszköz legyen
- batch futások végén gyorsabban látszódjon, mely lapok és események gyanúsak
- kevesebb kézi logbányászat kelljen
- a matchupok ismételhetően futtathatók és összevethetők legyenek

Jelenlegi ismert elemek:
- launcher
- seed batch
- suspicious hint-ek
- winner-side összesítések
- fixed deck preset támogatás
- szabályütközési diagnosztika a logban

## 5.4 Logikai és diagnosztikai átláthatóság
Állapot: javuló, de még aktív

Cél:
- a logokból könnyebben látszódjon, mi történt
- shared pathok, blokk-okok és szabályütközések követhetők legyenek
- meccssummaryk és batch summaryk megbízhatóak legyenek
- a runtime futás közben jelölje a később review-t igénylő lapokat

## 5.5 Szabálymagyarázhatósági audit
Állapot: új munkablokk

Cél:
- külön beszélgetés vagy munkafolyamat keretében a játék szabályainak elmagyarázása
- a dokumentumok és a motor alapján rekonstruált játékkép összevetése a tervezői szándékkal
- eltéréslista készítése

Ebből elvárt eredmények:
- könnyebben megérthető szabálymagyarázat
- rejtett szabályellentmondások azonosítása
- célzott szabálytisztázási backlog

## 5.6 Félvezérelt ember-vs-AI előkészítés
Állapot: jövőközeli, de még nem elsődleges

Cél:
- meghatározni a minimális technikai utat az emberi döntési pontok bevonásához
- a meglévő backend/facade és snapshot alapra építkezni
- CLI vagy félig vezérelt megoldásban gondolkodni

Első reális lépések:
- snapshot megjelenítés használható formában
- legal action lista emberi olvashatósága
- kiválasztott akciók kézi beadása
- a többi lépés maradhat AI-vezérelt vagy automatikus

## 5.7 `stats/` mappa rendezése
Állapot: előkészítés alatt

Cél:
- az aktív statisztikai runtime elem elkülönítése
- a reportok, batch summaryk, compliance auditok és egyszeri script-ek szétválasztása
- későbbi cleanup és mappaszerkezeti rendezés előkészítése

## 5.8 Godot-integráció előkészítése
Állapot: jövőbeli architektúra-cél

Cél:
- a jelenlegi motor ne zárja ki a későbbi vizuális frontend bekötését
- a tiszta állapotkezelés és action-határok kialakítása
- későbbi backend–frontend interfész előkészítése

Megjegyzés:
Ez továbbra sem elsődleges aktív fejlesztési kör.
A jelenlegi ember-vs-AI irány első lépése nem Godot lesz, hanem kisebb technikai megoldás.

---

# 6. Prioritási sorrend

## P1 – Azonnali prioritás
1. a tesztprogram és a runtime jelenlegi stabilizációs hibáinak lezárása
2. a szabálymotor és structured execution pathok következetességének javítása
3. a batch summaryk és diagnosztikai logok megbízhatóvá tétele
4. a projekt-feltérképezés befejezése a kritikus rétegekben

## P2 – Következő prioritás
1. a balanszfigyelő tesztprogram célzott bővítése
2. a `stats/` mappa rendezési terve
3. a fő refaktor-célpontok kijelölése
4. szabálymagyarázhatósági audit külön munkablokként

## P3 – Középtávú prioritás
1. mechanikai hiányok célzott folytatása
2. structured ↔ card-local ↔ shared runtime viszony tisztítása
3. backend-határok jobb elkülönítése
4. félvezérelt ember-vs-AI CLI MVP előfeltételeinek kidolgozása

## P4 – Közép-hosszú távú prioritás
1. minimális emberi döntési réteg prototípusa
2. legal action felület emberi használatra
3. snapshot + action alapú félvezérelt tesztjáték

## P5 – Hosszú távú prioritás
1. backend API-szerű gondolkodás további tisztítása
2. Godot-kötés előfeltételeinek kidolgozása
3. későbbi játszható frontend

---

# 7. Jelenlegi fő megállapítások

A feltérképezés és a futások eddigi állása alapján:

## 7.1 Nem minden réteg problémás
Rendezettebbnek tűnő rétegek:
- `data/`
- `simulation/`
- `utils/`
- a minimális `backend/` réteg alapjai

## 7.2 A vegyesebb, később refaktorálandó rétegek
- `engine/`
- `cards/`
- bizonyos structured effect útvonalak

## 7.3 A legerősebb cleanup-jelölt jelenleg
- `stats/`

## 7.4 A projekt jelenleg inkább hibrid, mint szétesett
Ez azt jelenti:
- van structured irány
- van shared helper irány
- van card-local név-alapú irány is
- van már backend/facade jellegű előkészítés is
- és ezek együtt élnek

Ez refaktorálási feladatot jelent, nem automatikusan teljes újrakezdést.

## 7.5 A tesztmotor már túl van a puszta prototípus állapoton
A jelenlegi állapot alapján a tesztmotor:
- már nem csak technikai próbafutás
- hanem ténylegesen használható hibakereső és balanszfigyelő alap

Ezért az ember-vs-AI irány előkészítése már nem idő előtti, ha kis lépésekben történik.

## 7.6 Az ember-vs-AI jelenleg még nem teljes feature-cél, hanem technikai előkészítési cél
Ez azt jelenti:
- a cél most még nem a teljes játékélmény
- hanem a döntési pontok formalizálása
- és a meglévő backend/action réteg tényleges használhatóságának növelése

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
- egy kis, izolált ember-vs-AI előkészítő lépés

## 8.2 Amit nem szabad keverni egy commitban
Lehetőleg ne keveredjen egyetlen commitba:
- runtime kódmódosítás
- dokumentációs rendezés
- reportfájl-rendezés
- nagytakarítás
- logfájlok vagy generált kimenetek
- félvezérelt CLI előkészítés és teljes mechanikai javítási batch

## 8.3 Commit üzenetek
A commit üzenetek legyenek rövidek, de egyértelműek.

Példák:
- `stabilize logging summaries`
- `add canonical trap consume metrics`
- `document engine and cards folders`
- `reorganize stats reports`
- `refactor shared source placement path`
- `add minimal human decision surface`

## 8.4 Branch használat
Ha fontosabb vagy kockázatosabb munkáról van szó, érdemes külön branch-et használni.

Példák:
- `docs/project-map`
- `cleanup/stats-structure`
- `runtime/canonical-batch-8`
- `logging/improvement-pass-2`
- `cli/human-loop-mvp`
- `rules/explainability-audit`

## 8.5 Mit nyerünk ezzel
- visszakövethető lesz, mi változott
- könnyebb lesz hibát visszakeresni
- könnyebb lesz dokumentálni a haladást
- könnyebb lesz külső segítséget bevonni
- könnyebb lesz később frontend-integrációra készülni
- kisebb lesz a kockázata annak, hogy az ember-vs-AI irány szétfolyjon

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

## 9.4 Tesztprogram workflow
- `TESZTPROGRAM_WORKFLOW_ES_TESZTPROFILOK.md`
- cél: a tesztprogram használati módjai, profiljai, futtatási logikája

## 9.5 Egyéb technikai háttérdokumentumok
- szabvány
- effect-határok
- seed-konvenció
- cleanup-jelöltek
- fejlesztési terv
- külön audit- és reportfájlok
- backend/facade előkészítő dokumentumok

---

# 10. Következő konkrét lépések

## Rövid távon
1. a jelenlegi runtime és diagnosztikai hibák lezárása
2. a tesztprogramból kijövő szabályütközések és gyanús lapok célzott kezelése
3. a projekt-térkép és a munkaterv naprakészen tartása
4. külön szabálymagyarázó audit kör elindítása

## Ezután
1. a félvezérelt ember-vs-AI technikai minimumának definiálása
2. a meglévő backend/facade és snapshot réteg felhasználási pontjainak kijelölése
3. legal action és state megjelenítés emberi olvashatóságának javítása

## Később
1. minimális CLI-alapú emberi döntési prototípus
2. backend API-szerű gondolkodás további tisztítása
3. Godot-integrációs előfeltételek összegyűjtése
4. vizuális frontend irányába nyitás

---

# 11. Egyszerű státuszblokk

## Kész / előrehaladott
- structured adatoldal működik
- a fő futási út dokumentálva van
- a logolás használhatóbb lett
- a projekt-térkép építése megkezdődött
- több főmappa szerepe tisztábban látszik
- minimális backend/facade alap létrejött
- snapshot és legal action alapok megjelentek

## Folyamatban
- részletes fájl- és mappafeltérképezés
- célok és prioritások rendezése
- cleanupra alkalmas területek azonosítása
- balanszfigyelő tesztprogram finomítása
- szabálymotor és structured útvonalak stabilizációja

## Újonnan megnyitott, de még nem elsődleges
- szabálymagyarázhatósági audit
- félvezérelt ember-vs-AI előkészítés

## Még előttünk áll
- `stats/` tényleges rendezése
- fő refaktorirányok kijelölése
- teljesebb action-surface emberi játékhoz
- backend–frontend előkészítés mélyítése
- későbbi Godot-kompatibilis architektúra-határok pontosítása

---

# 12. Verziózás

## v1
- elkészült az első központi projektterv
- a fő célok és prioritások rögzítve
- a GitHub használati alapelvek bekerültek
- a projekt jelenlegi fázisa és fókusza tisztázva

## v2
- a tesztprogram balanszfigyelő szerepe erősebben bekerült a fő fókuszok közé
- az ember-vs-AI irány nem lecserélésként, hanem bővítésként került be
- rögzítve lett a félvezérelt CLI / human-in-the-loop megközelítés mint legbiztosabb köztes út
- külön munkablokként bekerült a szabálymagyarázhatósági audit
- a prioritások frissítve lettek a jelenlegi projektállapothoz igazítva
