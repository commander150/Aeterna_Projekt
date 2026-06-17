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

## 2.7 Főforrás-alapú megfeleltetési cél

A projektben új fordulópont történt: elkészült a két hivatalos, aktív főforrás.

Aktuális elsődleges szabályi források:

AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx
AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx

Innentől minden szabályértelmezési, kártyatervezési, kártyaauditálási, engine-kompatibilitási és Codex-alapú kódellenőrzési feladatnál ezt a két dokumentumot kell mérvadó szabályi alapnak tekinteni.

Az alapjáték-főforrás kezeli:

a Core szabályrendszert;
az alapjáték megjelenéskori fogalmi rétegét;
az alapjátékos laptípusokat;
az alapjátékos kulcsszavakat és mechanikákat;
az alapjáték Birodalmait és Klánjait;
az alapjátékos Kaszt, Faj és Vérvonal azonosító-réteget;
valamint az alapjátékra vonatkozó audit-, megfigyelési és backlog-kezelési elveket.

A kiegészítő-főforrás kezeli:

az alapjáték után megjelenő kiegészítői tartalmakat;
Expansion-, pack- vagy formátumfüggő mechanikákat;
kiegészítő kulcsszavakat és kiváltságokat;
kiegészítő erőforrás- és fizetési mechanikákat;
a Pecsétprofil-rendszert;
a kiegészítő Birodalmakat;
az Avatár és Evolúció rendszert;
a Megbonthatatlan Szövetség mechanikai családját;
valamint a kiegészítő fogalomtárat és backlog-réteget.

A főforrás-alapú megfeleltetési cél most azt jelenti, hogy a következő munkafázisokban külön kell ellenőrizni:

a kártyák megfelelnek-e a két 1.4v főforrás szabályainak;
az adott kártya alapjátékos vagy kiegészítői státuszú-e;
a kártyák természetes szövege ugyanazt jelenti-e, mint a structured / canonical mezők;
a kártyák Birodalma, Klánja, Faja, Kasztja, Vérvonala és kulcsszavai szabályosan használhatók-e;
a Python engine tényleges viselkedése megfelel-e a főforrásokban rögzített szabályoknak;
a korábbi félreértések, régi szabályértelmezések vagy legacy kódrészletek nem maradtak-e aktívan a rendszerben;
az alapjátékos és kiegészítői mechanikai rétegek nem keverednek-e sem a kártyákban, sem a kódban.

Ez a cél nem új mechanikai front nyitását jelenti, hanem az elkészült két hivatalos főforrás és a meglévő kártyaadat-, structured-, engine- és tesztrendszer összehangolását.

---

# 3. Jelenlegi aktív fókusz

Elsődleges fókusz

A két 1.4v hivatalos főforrás alapján a kártyaállomány újratervezésének és javításának előkészítése.

Ennek közvetlen célja nem az, hogy azonnal tömegesen átírjuk az összes kártyát, hanem hogy előbb létrejöjjön a kártyatervezéshez szükséges két előkészítő munkadokumentum:

AETERNA – ÖTLETLÁDA ÉS NYITOTT TERVEK
AETERNA – KÁRTYATERVEZÉSI KATALÓGUS ÉS HASZNÁLHATÓ ELEMEK

Az Ötletláda feladata, hogy minden nem végleges, nem aktív, még kidolgozatlan vagy későbbre félretett terv, mechanikai gondolat, kártyaötlet, Birodalmi irány, Klánszinergia vagy szabályi lehetőség kontrollált helyre kerüljön.

A Kártyatervezési katalógus feladata, hogy pontosan felsorolja, mit lehet használni a kártyatervezés során:

laptípusokat;
Birodalmakat;
Klánokat;
Fajokat;
Kasztokat;
Vérvonalakat;
alapjátékos kulcsszavakat;
kiegészítői kulcsszavakat külön státusszal;
zónákat;
fizetési szabályokat;
Magnitúdó- és Aura-tervezési elveket;
kártyaszöveg-sablonokat;
structured mezőhasználati elveket;
valamint tiltott, archív vagy csak kiegészítőben használható elemeket.
Másodlagos fókusz

A jelenlegi cards.xlsx állapotának szabályforrás-alapú felmérése.

Ennek célja:

a jelenlegi kártyák státuszának meghatározása;
a megtartható, javítandó, újraírandó, kiegészítőbe áthelyezendő, archív vagy ötletládába mentendő kártyák elkülönítése;
a természetes kártyaszövegek és structured / canonical mezők összevetése;
a kártyaadat-hiba, szabályértelmezési hiba, engine-hiba és balanszgyanú elkülönítése.
Harmadlagos fókusz

A Python engine és a structured mezők későbbi megfelelési ellenőrzése a két 1.4v főforrás alapján.

Ez továbbra is fontos, de jelenleg nem előzi meg a kártyatervezési alapdokumentumok elkészítését. Előbb tudni kell, hogy milyen szabályos kártyatervezési készletből dolgozunk, és csak ezután érdemes teljes kártya- és engine-megfelelési auditot nyitni.

Negyedleges fókusz

A tesztprogram, backend/facade réteg, ember-vs-AI és későbbi Godot-kompatibilis irány fenntartása.

Ez az irány továbbra is érvényes, de jelenleg nem elsődleges. A projektterv alapján a motor fejlesztése továbbra sem nulláról újraépítésként, hanem feltérképezés, stabilizáció, cleanup, célzott refaktor és későbbi bővítés logikával halad tovább.

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
- nem kezdünk teljes engine-refaktorba a főforrás-alapú megfelelési audit előtt;
- nem javítunk tömegesen kártyákat előzetes szabályforrás szerinti hibakategorizálás nélkül;
- nem adunk Codexnek általános „nézd át a programot” típusú feladatot;
- nem használunk régi szabálydokumentumot vagy beszélgetési emléket döntési alapként, ha az eltér az 1.0v főforrástól;
- nem keverjük össze a kártyaadat-hibát, engine-hibát, dokumentációs hiányt és balanszproblémát.

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

## 5.9 Hivatalos főforrás elkészítése

Állapot: elkészült / aktív szabályi alap

Aktuális hivatalos főforrások:

AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx
AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx

Eredmény:

a korábbi egybeszerkesztett főforrás-modell helyett létrejött a két aktív főforrásos rendszer;
az alapjáték-főforrás kezeli a Core-t, az alapjátékos fogalmakat, alapjátékos kulcsszavakat, alapjátékos Birodalmakat, Klánokat, laptípusokat és alapjátékos mechanikai réteget;
a kiegészítő-főforrás kezeli az alapjáték után megjelenő Expansion-, packfüggő, formátumfüggő vagy külön aktiválható tartalmakat;
mindkét dokumentum 1.4v állapotban közös forrás-összehangoló auditon esett át;
a korábbi források ezután nem aktív szabályi referenciák, hanem archív / történeti háttéranyagok;
a további szabályi, kártyatervezési, kártyaauditálási és engine-kompatibilitási döntések elsődleges alapja ez a két 1.4v főforrás.

## 5.10 Kártyaállomány auditja az 1.0v főforrás alapján

Állapot: következő aktív munkafázis

Cél:

A kártyák javítása, újratervezése és új kártyák létrehozása előtt létre kell hozni azokat a segéddokumentumokat, amelyek megakadályozzák, hogy a kártyatervezés közben újra összekeveredjenek az alapjátékos, kiegészítői, archív és még nem végleges ötletek.

Kötelező előkészítő dokumentumok:

AETERNA – ÖTLETLÁDA ÉS NYITOTT TERVEK
AETERNA – KÁRTYATERVEZÉSI KATALÓGUS ÉS HASZNÁLHATÓ ELEMEK

Az Ötletláda célja:

nem végleges ötletek megőrzése;
későbbi mechanikai, kártya- vagy Birodalmi ötletek félretétele;
archív, vizsgálandó vagy még nem aktivált elemek kezelése;
a főforrások tisztaságának védelme;
annak megakadályozása, hogy egy ötlet idő előtt aktív szabályként vagy kártyatervezési engedélyként működjön.

A Kártyatervezési katalógus célja:

a kártyatervezéshez használható elemek pontos felsorolása;
a két 1.4v főforrásból származó használható Birodalmak, Klánok, Fajok, Kasztok, Vérvonalak, kulcsszavak és szabályi korlátok összegyűjtése;
a kiegészítői elemek státuszának elkülönítése;
a tiltott, archív vagy csak későbbi munkában használható elemek külön jelölése;
a cards.xlsx strukturált mezőinek későbbi javításához szükséges tervezési alap biztosítása.

## 5.11 Kártyaállomány újratervezése és auditja a két 1.4v főforrás alapján

Állapot: előkészítés után induló nagy munkafázis

Cél:

A jelenlegi kártyaállomány szabályforrás-alapú felmérése, javítása, újratervezése és szükség esetén új kártyákkal való kiegészítése.

A munkafázis fő céljai:

a kártyák természetes szövegének ellenőrzése a két 1.4v főforrás alapján;
a structured / canonical mezők ellenőrzése;
a kártyák alapjátékos vagy kiegészítői státuszának tisztázása;
a Birodalom / Klán / Faj / Kaszt / Vérvonal használatának ellenőrzése;
az alapjátékos és kiegészítő kulcsszavak szétválasztása;
a kártyák szerepének meghatározása Birodalmonként és Klánonként;
a nem használható vagy rossz rétegbe került kártyák kiszűrése;
a kártyaadat-hiba, szabályértelmezési hiba, engine-hiba és balanszgyanú elkülönítése.

Első rendezési kategóriák:

megtartható;
kisebb javítással megtartható;
teljesen újraírandó;
kiegészítőbe áthelyezendő;
archív / nem aktív;
ötletládába mentendő;
törlendő vagy új koncepcióval helyettesítendő.

A tényleges kártyaújratervezés csak az Ötletláda és a Kártyatervezési katalógus elkészülte után induljon.

---

## 5.12 Codex kódellenőrzés a két 1.4v főforrás alapján
Állapot: párhuzamosan előkészíthető, de nem elsődleges

Cél:

a Python engine szabálymegfelelési ellenőrzése az alapjáték-főforrás és a kiegészítő-főforrás alapján;
annak vizsgálata, hogy a kód nem hordoz-e régi, félreértett vagy legacy szabálylogikát;
engine-oldali, card-local, structured és fallback eltérések elkülönítése;
a kódellenőrzési eredmények későbbi javítási backlogba rendezése.

Fontos korlát:

A Codex első körben ne végezzen nagy refaktort és ne javítson automatikusan mindent. Először diagnosztikai, megfelelési és hibakategorizálási audit készüljön.

A Codex-feladatok csak akkor legyenek kiadva, ha világos, hogy az adott probléma:

kártyaadatból;
structured mezőből;
engine-oldali működésből;
card-local handlerből;
vagy régi szabályértelmezésből ered.

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

## 9.6 Terminológiai és dokumentumszintű tisztázás – Booster pack, Expansion pack és kiegészítő mechanikai réteg

Az AETERNA projektben külön kell választani a termékszintű és a szabályréteg-szintű fogalmakat, mert ezek részben összefüggnek, de nem azonosak.

### Booster pack

A Booster pack az AETERNA TCG-ben is a szokásos TCG-értelemben vett kártyacsomagot jelenti: olyan csomagot, amely lapokat ad a játékhoz.

A Booster pack elsődleges szerepe:
- új lapok hozzáadása a játékhoz,
- meglévő Birodalmak és Klánok bővítése,
- új pakliépítési lehetőségek megnyitása.

A Booster pack tehát termékszintű fogalom, nem külön szabályréteg.

### Expansion pack / Kiegészítő csomag

Az Expansion pack, magyarul Kiegészítő csomag, az AETERNA-ban is alapvetően a más TCG-kben megszokott jelentéshez igazodik.

Az Expansion pack olyan bővítés, amely:
- új lapkészletet ad a játékhoz,
- új témákat, Klánokat, Birodalmi irányokat vagy mechanikákat vezethet be,
- kibővíti a játék lehetőségeit,
- és bizonyos esetekben hibajavító vagy korrekciós szerepet is betölthet a játék fejlődése során.

Az Expansion pack tehát elsősorban a játék bővítésének termékszintű és tartalmi egysége.

### A kiegészítő mechanikai réteg

A korábbi dokumentumokban részben „expansion-rétegként” kezelt fogalom valójában nem azonos az Expansion pack termékjelentésével.

Ezt a fogalmat a jövőben pontosabban kiegészítő mechanikai rétegnek vagy kiegészítő szabályrétegnek kell nevezni.

A kiegészítő mechanikai réteg:
- a Core fölé épül,
- külön kezelendő szabályi és mechanikai sáv,
- azt rögzíti, hogyan működnek a nem alapjátéki kivételek, új mechanikák és bővítő rendszerek,
- és nem azonos magával a termékként megjelenő Expansion packkel.

### A kettő viszonya

Az Expansion pack és a kiegészítő mechanikai réteg nem ugyanaz, de szorosan összefügghetnek.

A helyes viszony:
- az Expansion pack a játékot bővítő tartalmi / termékszintű egység,
- a kiegészítő mechanikai réteg pedig az a szabályi háttér, amelynek alapján az ilyen bővítések új mechanikái értelmezhetők és beilleszthetők.

Vagyis egy Expansion pack tartalmazhat olyan lapokat és újításokat, amelyek működéséhez kiegészítő mechanikai réteg szükséges, de a két fogalom akkor is külön marad.

### Követendő terminológiai elv

A projekt további szakaszában az alábbi terminológiai rendet kell követni:

- Booster pack = lapokat adó kártyacsomag
- Expansion pack / Kiegészítő csomag = a játékot bővítő új lapkészlet vagy bővítés
- Kiegészítő mechanikai réteg / kiegészítő szabályréteg = a Core fölé épülő külön szabályi-mechanikai sáv

Ennek célja, hogy a terméklogika, a tartalmi bővítés és a belső szabályréteg többé ne keveredjen össze a projekt dokumentumaiban.

---

# 10. Következő konkrét lépések

## Rövid távon

1. Az AKTUALIS_PROJEKTTERV_ES_PRIORITASOK frissítése v5-re a két 1.4v főforrás alapján.
2. Az AETERNA – ÖTLETLÁDA ÉS NYITOTT TERVEK dokumentum létrehozása.
3. Az AETERNA – KÁRTYATERVEZÉSI KATALÓGUS ÉS HASZNÁLHATÓ ELEMEK dokumentum létrehozása.
4. A jelenlegi cards.xlsx állapotának előzetes felmérése.
5. A kártyaállomány első státuszkategorizálása: megtartható, javítandó, újraírandó, kiegészítőbe áthelyezendő, archív, ötletládába mentendő.

## Párhuzamosan

1. A structured / canonical mezők szabványának összevetése a két 1.4v főforrással.
2. A runtime warningok újraértékelése a két főforrás alapján.
3. A Python engine megfelelési auditjának előkészítése, de még nem tömeges javítása.
4. A kártyaadat-hiba, engine-hiba, szabályértelmezési eltérés és balanszgyanú elkülönítési rendszerének fenntartása.

## Ezután

1. Birodalmonként és Klánonként elindítható a kártyák tényleges újratervezése.
2. Minden kártyánál ellenőrizni kell:
 - laptípus;
 - Birodalom;
 - Klán;
 - Faj;
 - Kaszt;
 - Vérvonal;
 - Magnitúdó;
 - Aura;
 - kulcsszavak;
 - zónák;
 - célpontválasztás;
 - trigger;
 - hatás;
 - időtartam;
 - structured / canonical mezők.
3. A biztos kártyaadat-hibák javítási listába kerülnek.
4. A nem végleges ötletek az Ötletládába kerülnek.
5. A kiegészítői státuszú elemek a kiegészítő-főforrás logikája szerint kezelendők.
6. A bizonytalan esetek megfigyelési pontként vagy backlog-elemként maradnak.

## Később

1. Codex-alapú engine-megfelelési audit.
2. AI/kódbarát szabályspecifikáció előkészítése.
3. Szabálymagyarázhatósági audit folytatása.
4. Ember-vs-AI minimális technikai irány újranyitása.
5. Godot-kompatibilis backend-határok pontosítása.

---

# 11. Egyszerű státuszblokk

## Kész / előrehaladott

- elkészült a két hivatalos aktív főforrás:
   - AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx;
   - AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx;
- a régi egybeszerkesztett főforrásmodell aktív használata megszűnt;
- a régi források archív / történeti háttérként kezelendők;
- a főforrások közös auditja megtörtént;
- a Core / alapjáték / kiegészítő elhatárolás rögzítve van;
- az alapjátékos kulcsszavak és Birodalom- / Klánprofilok kidolgozása megtörtént;
- a kiegészítői kulcsszavak, Birodalmak, Pecsétprofil-rendszer, Avatár / Evolúció és Megbonthatatlan Szövetség külön főforrásban szerepelnek;
- a minimális backend/facade + snapshot + legal-actions + apply_action lánc használható alapként megvan;
- a projektirányító dokumentumok alapja rendelkezésre áll.

## Folyamatban

- az aktuális projektterv frissítése a két 1.4v főforrás alapján;
- az Ötletláda előkészítése;
- a Kártyatervezési katalógus előkészítése;
- a kártyaállomány újratervezési és auditfolyamatának előkészítése;
- a jelenlegi cards.xlsx későbbi szabályforrás-alapú felmérésének előkészítése.

## Párhuzamosan indítható

- cards.xlsx structured mezőinek célzott ellenőrzése;
- runtime warningok újraértékelése a két főforrás alapján;
- Codex programkód-audit előkészítése a két 1.4v főforrás alapján;
- szabályeltérések engine-szintű kategorizálása;
- kártyatervezési sablonok és státuszkategóriák kidolgozása.

## Még előttünk áll

- Ötletláda dokumentum létrehozása;
- Kártyatervezési katalógus létrehozása;
- első teljes kártyaállomány-felmérés;
- kártyák státuszkategorizálása;
- Birodalmonkénti és Klánonkénti újratervezés;
- biztos kártyajavítások és biztos engine-javítások elkülönítése;
- célzott javítási backlog készítése;
- javítások utáni regressziós tesztelés;
- AI/kódbarát specifikáció előkészítése;
- későbbi ember-vs-AI és Godot-kompatibilis irány folytatása.

---

12. Verziózás
# 
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

## v3
- terminológiai tisztázásra került a Booster pack fogalma mint a játékhoz lapokat adó kártyacsomag
- rögzítve lett, hogy az Expansion pack / Kiegészítő csomag az AETERNA-ban is elsősorban a más TCG-kben megszokott jelentéshez igazodik, vagyis a játékot bővítő új lapkészletet vagy bővítést jelenti
- pontosítva lett, hogy az Expansion pack és a Core fölé épülő új mechanikák részben összefügghetnek, de nem azonosak
- külön elválasztásra került a termékszintű bővítés és a belső szabályi-mechanikai réteg fogalma
- rögzítve lett, hogy a korábban expansion-rétegként kezelt fogalmat a jövőben pontosabban kiegészítő mechanikai rétegként vagy kiegészítő szabályrétegként érdemes kezelni
- ezzel a projekt terminológiája tisztább lett a terméklogika, a tartalmi bővítés és a dokumentumszintű szabályréteg szétválasztása szempontjából

## v4
- elkészült és elsődleges szabályi forrássá vált az **AETERNA – HIVATALOS AUDITÁLT FŐFORRÁS DOKUMENTUM 1.0v.docx**;
- a projektállapot frissült a főforrás-alapú megfeleltetési fázisra;
- rögzítésre került, hogy a következő nagy munkafázis a kártyaállomány auditja az 1.0v főforrás alapján;
- rögzítésre került, hogy a Codex párhuzamosan programkód-auditot végezhet ugyanebből a főforrásból kiindulva;
- pontosításra került, hogy a kártyaaudit és a kódellenőrzés két párhuzamos, de később összevezetendő munkaszál;
- a következő konkrét lépések és az egyszerű státuszblokk frissültek.

## v5
- frissítésre került a projektterv a két hivatalos aktív főforrás alapján;
- az eddigi egy főforrásos 1.0v hivatkozás helyét átvette a két 1.4v főforrás:
   - AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx;
   - AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx;
- rögzítésre került, hogy a következő nagy szakasz a kártyák javításának, újratervezésének és új kártyák létrehozásának előkészítése;
- bekerült az Ötletláda mint külön előkészítő munkadokumentum;
- bekerült a Kártyatervezési katalógus mint a kártyatervezéshez használható elemeket felsoroló referencia;
- a kártyaállomány auditja át lett fogalmazva szélesebb kártyarendezési és újratervezési munkafázissá;
- rögzítésre került, hogy a kártyák tényleges újratervezése csak az Ötletláda és a Kártyatervezési katalógus elkészülte után induljon;
- a Codex / engine-megfelelési audit megmaradt fontos párhuzamos iránynak, de nem előzi meg a kártyatervezési alapdokumentumok elkészítését;
- a projekt végső célja továbbra is egy szabályhű, auditálható, engine-kompatibilis, tesztelhető és balanszolható AETERNA kártyaállomány létrehozása.