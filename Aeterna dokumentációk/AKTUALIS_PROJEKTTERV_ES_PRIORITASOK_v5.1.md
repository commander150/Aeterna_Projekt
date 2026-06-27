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

## 1. A projekt jelenlegi iránya

Az AETERNA jelenlegi projektállapota hibrid.

A projektnek két, egymástól elválasztandó, de később összehangolható technikai rétege van:

1. a régi Python-alapú szimulációs motor;
2. az új `Aeterna game engine/` contract-first digitális programegység.

A régi Python motor továbbra is értékes referencia. Működő AI-vs-AI szimulációs alapot, kártya- és effectlogikai előzményeket, diagnosztikai tapasztalatokat, batch futtatási mintákat és balanszfigyelési ötleteket tartalmaz. Ezért nem törlendő és nem eldobandó.

A régi Python motor jelenlegi státusza:

* `OLD_ENGINE_REVIEW`
* `OLD_ENGINE_REFERENCE`

Ez azt jelenti, hogy a régi motorból később külön döntési körben kell eldönteni, mi:

* megtartandó referenciaként;
* migrálható az új contract-first pipeline-ba;
* archiválható;
* vagy kiváltható új megoldással.

Az új digitális fejlesztési irány az `Aeterna game engine/` mappában futó contract-first fejlesztés.

Ennek fő részei:

* `Aeterna game engine/python/` mint aktív Python tooling, exportvalidációs és runtime package build irány;
* `Aeterna game engine/Godot/` mint runtime package-et és sample contractokat fogyasztó Godot debug / prototípus ág;
* runtime package mint Python és Godot közötti programbiztos adatcontract;
* sample snapshot, legal action, event log és action request contractok;
* Godot debug nézetek, registry-k, loader és smoke testek;
* az XLSX exporter migrált új Python tooling helye.

A projekt továbbra sem nulláról újraépítendő rendszerként van kezelve.

A jelenlegi stratégia:

1. meglévő értékek feltérképezése;
2. régi és új technikai irány szétválasztása;
3. hivatalos szabályforrások, kártyaadat-források és runtime package adatút elkülönítése;
4. dokumentációs és mappaszintű döntések rögzítése;
5. célzott prototípusok és kis lépésű fejlesztések;
6. csak külön döntés után nagyobb refaktor vagy integráció.

Az új célok nem törlik a régi motor értékét, de módosítják a projekt aktuális technikai prioritását.

A további programfejlesztés elsődleges iránya nem a régi Python motor közvetlen bővítése, hanem az új contract-first adatpipeline és Godot-fogyasztói réteg fokozatos, ellenőrizhető fejlesztése.

### 1.1 Új contract-first Aeterna game engine irány

Az új AETERNA game engine célja, hogy a játék digitális feldolgozása ne közvetlenül szerkesztési forrásokból, régi XLSX-ből vagy kézzel értelmezett runtime logikából dolgozzon, hanem validált, programbiztos contract rétegen keresztül.

Az adatút hosszú távú célja:

1. Google Sheets / XLSX szerkesztési forrás;
2. Python exporter és validáció;
3. runtime package;
4. Godot loader és registry réteg;
5. sample contractok;
6. debug nézetek;
7. később interaktív játékréteg.

Fontos elvek:

* Godot nem XLSX-olvasó;
* Godot nem canonical adatforrás;
* Python végzi az exportálást, validálást, package-építést és későbbi adat-előkészítést;
* Godot a runtime package-et és contractokat fogyasztja;
* a runtime package legyen a programbiztos adatközvetítő réteg;
* a régi Python motor nem automatikusan törlendő, hanem review alatt álló referencia.

---

## 2. A projekt fő céljai

### 2.1 Rövid távú fő cél
A jelenlegi rendszer pontos feltérképezése és stabilizálása.

Ez azt jelenti:
- tudjuk, melyik fájl mi
- tudjuk, mi aktív runtime és mi nem
- tudjuk, melyik réteg tiszta és melyik refaktorra szorul
- a futó motor diagnosztikailag követhető legyen
- a tesztprogramból megbízható balanszfigyelő eszköz legyen

### 2.2 Középtávú fő cél
A jelenlegi structured szabvány és a működő motor jobb összekapcsolása.

Ez azt jelenti:
- a szabványos mezők valódi mechanikákat hajtsanak meg
- a még hiányzó vagy részleges mechanikák bekötése folytatódjon
- a card-local és shared/runtime rétegek viszonya tisztuljon
- a szabálymagyarázat és a tényleges engine-viselkedés közti eltérések láthatóvá váljanak

### 2.3 Kibővített középtávú cél

A középtávú cél már nem kizárólag a régi tesztmotorra épülő félvezérelt ember-vs-AI előkészítés.

A középtávú cél most kettős:

1. az új contract-first technikai adatpipeline stabilizálása;
2. a későbbi emberi döntés / debug / interaktív működés előkészítése.

Ez nem teljes UI/UX projektet jelent.

Első célként olyan technikai alapréteget kell fenntartani és bővíteni, amelyben:

* a játékadatok validált runtime package formában érkeznek;
* a Godot oldal be tudja tölteni és ellenőrizni tudja a package-et;
* a sample contractok alapján megjeleníthető egy snapshot;
* listázhatók a legal action jellegű döntések;
* követhető az event log;
* az action request minta alapján később emberi döntés is visszaküldhető;
* a debug nézetek segítik a contractok ellenőrzését.

A félvezérelt ember-vs-AI irány továbbra is értékes hosszabb távú cél, de nem közvetlenül a régi Python CLI-ből kell továbbépíteni. Előbb a runtime package / contract / Godot fogyasztói útvonalat kell tisztán tartani.

### 2.4 Hosszú távú fő cél

A projektből hosszú távon használható, játszható AETERNA digitális eszköz legyen.

Célállapot:

1. hivatalos szabályforrások és kártyaadatbázis alapján validált adatpipeline;
2. Python oldali export, validáció, runtime package build és tesztelés;
3. Godot oldali runtime package loader, registry és debug nézet;
4. sample snapshot, legal action, event log és action request contractok;
5. félvezérelt ember-vs-AI technikai prototípus;
6. ember-vs-AI játszható rendszer;
7. később ember-vs-ember irány.

A régi AI-vs-AI Python szimulációs motor továbbra is hasznos referencia és későbbi összevetési alap, de már nem egyedüli fejlesztési tengely.

### 2.5 Architektúra-cél

Az architektúra-cél a frissített projektállapotban nem egyszerűen az, hogy a jelenlegi Python motor később Godot frontendhez kapcsolható backend legyen.

Az új cél egy contract-first, rétegezett technikai architektúra:

* Python oldalon adatfeldolgozás, XLSX export, validáció, runtime package build, tesztek és későbbi batch / AI jellegű feldolgozás;
* Godot oldalon runtime package fogyasztás, registry, debug nézetek, sample contractok és későbbi interaktív megjelenítés;
* a két oldal között JSON / JSONL alapú runtime package és contract réteg;
* a régi Python motor review alatt álló referencia, nem pedig automatikusan továbbfejlesztendő fő backend.

Ez azt jelenti:

* Godot nem találgat szabálylogikát nyers XLSX-ből;
* Python nem keveri össze a régi szimulációs motort az új package build pipeline-nal;
* a runtime package határa legyen világos;
* a sample contractok legyenek külön ellenőrizhetők;
* minden integráció kis, tesztelhető lépésben történjen;
* a régi Python motorból csak külön döntés alapján emelünk át logikát az új rendszerbe.

### 2.6 Szabályérthetőségi cél
A projektben külön céllá válik annak vizsgálata, hogy a játék szabályai mennyire jól magyarázhatók el a jelenlegi dokumentumok és a tényleges engine alapján.

Ez azt jelenti:
- legyen külön rules explainability audit
- legyen látható, ha az elképzelt szabály és a motor viselkedése eltér
- a szabálymagyarázat ne csak írott dokumentum, hanem validációs eszköz is legyen

### 2.7 Főforrás-alapú megfeleltetési cél

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

## 3. Jelenlegi aktív fókusz

A jelenlegi aktív fókusz négy egymástól elkülönített, de összefüggő munkasávra oszlik.

### 3.1 Dokumentációs és mappaszintű rendezés

Elsődleges közvetlen fókusz az aktív dokumentációs és mappaszintű állapot tisztázása.

Ennek oka, hogy az új contract-first `Aeterna game engine/` irány már működő technikai checkpointokat ért el, miközben több régi dokumentum még a Python szimulációs motor központú projektképet tartalmazza.

Közvetlen célok:

* az `Aeterna dokumentációk/` mappa dokumentumainak státuszolása;
* elavult, átvezetett, aktív és review státuszú dokumentumok elkülönítése;
* a régi Python motoros dokumentumok referencia státuszának rögzítése;
* az új contract-first engine dokumentáció és a régi projektirányító dokumentumok összehangolása;
* törlés vagy mozgatás nélküli archiválási előkészítés.

Ez a munkasáv nem törlési feladat.

### 3.2 Technikai adatpipeline és contract-first engine

A technikai adatpipeline első mappaszintű rendezési köre lezárult.

Elfogadott állapot:

* az új aktív XLSX exporter helye: `Aeterna game engine/python/tools/xlsx_export/`;
* az exporter unit és smoke tesztekkel ellenőrzött;
* a régi `XLSX export/` mappa státusza: `OBSOLETE_AFTER_MIGRATION_CANDIDATE`;
* a Python oldali `sample_runtime_package/` státusza: `GENERATED_TEST_FIXTURE`;
* a Godot oldali `sample_runtime_package/` státusza: `GODOT_CONSUMPTION_COPY`;
* a Godot oldali `sample_contracts/` státusza: `HAND_AUTHORED_TEST_FIXTURE`;
* Godot nem XLSX olvasó és nem canonical adatforrás;
* a régi Python engine maradványok státusza: `OLD_ENGINE_REVIEW`.

Következő technikai fejlesztés csak külön döntési kapu után induljon.

Javasolt későbbi fejlesztési irány:

* exporter output contract mapping terv;
* később runtime package builder integráció;
* később Godot consumption copy automatikus frissítése.

### 3.3 Kártyaadatbázis és főforrás-alapú audit

A két 1.4v hivatalos főforrás továbbra is az AETERNA jelenlegi aktív szabályi alapja.

Aktív főforrások:

* `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
* `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

A kártyaaudit és kártyatervezési előkészítés továbbra is fontos munkasáv.

Ennek célja:

* a kártyák státuszának meghatározása;
* az alapjátékos és kiegészítői kártyák elkülönítése;
* a természetes kártyaszövegek és structured / canonical mezők összevetése;
* a kártyaadat-hiba, szabályértelmezési hiba, engine-hiány és balanszgyanú elkülönítése;
* a Google Sheets / XLSX munkaforrás és a runtime exportfolyamat közötti kapcsolat tisztítása.

A kártyaaudit nem indulhat tömeges, előzetes hibakategorizálás nélküli javításként.

### 3.4 Régi Python motor review

A régi Python szimulációs motor nem elsődleges új fejlesztési cél, de továbbra is értékes referencia.

Megtartandó értékei:

* AI-vs-AI tesztmotor;
* balanszfigyelési tapasztalatok;
* structured és card-local runtime előzmények;
* effectlogikai megoldások;
* logolási és diagnosztikai megoldások;
* futtatható összevetési alap.

Jelenlegi státusza:

* `OLD_ENGINE_REVIEW`
* `OLD_ENGINE_REFERENCE`

A régi motoron nagyobb refaktor vagy új fejlesztés csak külön döntési kör után induljon.

---

## 4. Amit most NEM csinálunk

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

## 5. Jelenlegi munkablokkok

### 5.0 Contract-first engine és technikai adatpipeline

Állapot: aktív, első rendezési kör lezárva

Cél:

* az új `Aeterna game engine/` technikai adatút tisztán tartása;
* a Python tooling és Godot fogyasztói ág szerepének elkülönítése;
* az XLSX exporter migrált helyének rögzítése;
* a runtime package mint adatcontract fenntartása;
* a sample contractok és debug prototípusok továbbfejlesztésének előkészítése;
* a régi Python motor és az új engine összekeverésének megelőzése.

Jelenlegi ismert elemek:

* `Aeterna game engine/python/tools/xlsx_export/`
* `Aeterna game engine/python/sample_runtime_package/`
* `Aeterna game engine/Godot/sample_runtime_package/`
* `Aeterna game engine/Godot/sample_contracts/`
* Godot loader, registry és debug nézetek
* smoke tesztek
* contract consistency ellenőrzések

Jelenlegi döntés:

* az adatpipeline első mappaszintű rendezési köre lezárható;
* programfejlesztés folytatható, de csak külön döntési kapuval;
* közvetlen következő fejlesztési jelölt: exporter output contract mapping terv;
* runtime package builder integráció még nem indul automatikusan.

### 5.1 Projekt- és dokumentáció-feltérképezés

Állapot: folyamatban

Cél:

* a főmappák és fájlok feltárása;
* szerepek és státuszok rögzítése;
* a projekt-térkép dokumentum frissítése;
* az `Aeterna dokumentációk/` mappa aktív, elavult, átvezetett, duplikált és archiválási jelölt dokumentumainak elkülönítése.

Jelenlegi ismert fókuszterületek:

* `Aeterna dokumentációk/`
* `Aeterna game engine/`
* `XLSX export/`
* `Archive/`
* régi Python motor dokumentumai
* új contract-first engine dokumentumai

A projekt-feltérképezés nem törlési lista és nem refaktor-parancs.

### 5.2 Régi Python runtime stabilizáció

Állapot: review alatt, nem elsődleges új fejlesztési fókusz

Cél:

* a régi motor működő értékeinek megőrzése;
* a régi futási út dokumentálása;
* a structured és card-local runtime előzmények megértése;
* későbbi átmentési vagy archiválási döntések előkészítése.

Jelenlegi státusz:

* `OLD_ENGINE_REVIEW`
* `OLD_ENGINE_REFERENCE`

A régi Python motoron nem indul nagy refaktor, amíg nincs külön döntés arról, hogy mely részei maradnak referenciák, mely részei migrálhatók, és mely részei archiválhatók.

### 5.3 Balanszfigyelő tesztprogram

Állapot: értékes régi motoros referencia

Cél:

* a régi AI-vs-AI tesztprogram tapasztalatainak megőrzése;
* a balanszfigyelési, warning- és diagnostics-minták későbbi felhasználása;
* a régi batch és suspicious hint logika értékelése.

Ez a munkablokk jelenleg nem elsődleges új fejlesztési fókusz, de később fontos lehet, amikor a runtime package és contract-first rendszer már képes lesz stabilabb adatútból dolgozni.

### 5.4 Kártyaállomány auditja és újratervezése

Állapot: aktív munkasáv, főforrás-alapú

Cél:

* a kártyák megfeleltetése a két 1.4v hivatalos főforrásnak;
* az alapjátékos, kiegészítői, archív, ötletládába mentendő és újraírandó lapok elkülönítése;
* a természetes kártyaszövegek és structured mezők összevetése;
* a Google Sheets / XLSX munkaforrás és az exportált runtime adatok kapcsolatának tisztázása.

Ez a munkasáv nem azonos a régi Python motor fejlesztésével.

A kártyaaudit elsődleges adatforrása a kártyaadatbázis munkaforrás és a hivatalos főforrások, nem a régi motor viselkedése.

### 5.5 Szabálymagyarázhatósági audit
Állapot: új munkablokk

Cél:
- külön beszélgetés vagy munkafolyamat keretében a játék szabályainak elmagyarázása
- a dokumentumok és a motor alapján rekonstruált játékkép összevetése a tervezői szándékkal
- eltéréslista készítése

Ebből elvárt eredmények:
- könnyebben megérthető szabálymagyarázat
- rejtett szabályellentmondások azonosítása
- célzott szabálytisztázási backlog

### 5.6 Félvezérelt ember-vs-AI előkészítés
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

### 5.7 `stats/` mappa rendezése
Állapot: előkészítés alatt

Cél:
- az aktív statisztikai runtime elem elkülönítése
- a reportok, batch summaryk, compliance auditok és egyszeri script-ek szétválasztása
- későbbi cleanup és mappaszerkezeti rendezés előkészítése

### 5.8 Godot-integráció előkészítése
Állapot: jövőbeli architektúra-cél

Cél:
- a jelenlegi motor ne zárja ki a későbbi vizuális frontend bekötését
- a tiszta állapotkezelés és action-határok kialakítása
- későbbi backend–frontend interfész előkészítése

Megjegyzés:
Ez továbbra sem elsődleges aktív fejlesztési kör.
A jelenlegi ember-vs-AI irány első lépése nem Godot lesz, hanem kisebb technikai megoldás.

### 5.9 Hivatalos főforrás elkészítése

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

### 5.10 Kártyaállomány auditja az 1.0v főforrás alapján

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

### 5.11 Kártyaállomány újratervezése és auditja a két 1.4v főforrás alapján

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

### 5.12 Codex kódellenőrzés a két 1.4v főforrás alapján
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

## 6. Prioritási sorrend

A prioritási sorrend a frissített projektállapot alapján módosul.

A projekt jelenleg nem egyetlen Python szabálymotor stabilizációs feladatként kezelendő, hanem hibrid rendszerként:

* hivatalos szabályforrások;
* kártyaadatbázis és Google Sheets / XLSX munkaforrás;
* új contract-first `Aeterna game engine/`;
* régi Python szimulációs motor review státuszban;
* Godot runtime package fogyasztói prototípus;
* dokumentációs és mappaszintű rendezés.

### P1 – Dokumentációs és mappaszintű rendezés

Elsődleges prioritás:

* `Aeterna dokumentációk/` mappa rendezése;
* elavult, átvezetett, aktív és review státuszú dokumentumok jelölése;
* duplikált dokumentumszerepek tisztázása;
* projektirányító dokumentumok frissítése;
* régi Python motoros dokumentumok referencia státuszának rögzítése;
* új contract-first engine dokumentumokkal való összevetés.

Indok:

A további fejlesztés csak akkor marad követhető, ha a dokumentumok nem mondanak ellent egymásnak a projekt aktuális irányáról.

### P2 – Contract-first technikai adatpipeline fenntartása

Második prioritás:

* új Python tooling ág tisztán tartása;
* XLSX exporter migrált helyének fenntartása;
* runtime package adatcontract szerepének rögzítése;
* Godot fogyasztói ág szerepének fenntartása;
* sample runtime package és sample contract státuszok megtartása;
* smoke tesztek és contract consistency ellenőrzések megőrzése.

Nem indulhat automatikusan nagy integráció.

Következő technikai fejlesztési döntési kapu:

* exporter output contract mapping terv.

### P3 – Kártyaadatbázis és főforrás-alapú kártyaaudit

Harmadik prioritás:

* a két 1.4v hivatalos főforrás szerinti kártyaellenőrzés;
* a kártyaadatbázis munkaforrás és exportok szerepének tisztázása;
* structured / canonical mezők ellenőrzése;
* kártyaszöveg, adatmező, engine-hiány és balanszgyanú elkülönítése;
* kártyatervezési katalógus és auditmunkarend használata.

Ez a prioritás nem jelent tömeges, előzetes kategorizálás nélküli kártyaátírást.

### P4 – Régi Python motor review

Negyedik prioritás:

* régi Python motor értékeinek feltárása;
* régi futási út megtartása referenciaként;
* AI-vs-AI, balanszfigyelő és diagnostics megoldások értékelése;
* későbbi migrációs vagy archiválási döntések előkészítése.

A régi Python motor jelenleg nem elsődleges új fejlesztési alap, hanem `OLD_ENGINE_REVIEW` státuszú referencia.

### P5 – Későbbi interaktív / játszható prototípus irány

Ötödik prioritás:

* félvezérelt ember-vs-AI irány;
* ember-vs-AI játszható rendszer;
* későbbi ember-vs-ember irány;
* teljesebb Godot UI / UX;
* rules explanation és játékosbarát szabálymegjelenítés.

Ez csak akkor induljon, ha az adatcontract, package, loader, registry és alap debug útvonal már stabilabb.

---

## 7. Jelenlegi fő megállapítások

A feltérképezés és a futások eddigi állása alapján:

### 7.1 Nem minden réteg problémás
Rendezettebbnek tűnő rétegek:
- `data/`
- `simulation/`
- `utils/`
- a minimális `backend/` réteg alapjai

### 7.2 A vegyesebb, később refaktorálandó rétegek
- `engine/`
- `cards/`
- bizonyos structured effect útvonalak

### 7.3 A legerősebb cleanup-jelölt jelenleg
- `stats/`

### 7.4 A projekt jelenleg inkább hibrid, mint szétesett
Ez azt jelenti:
- van structured irány
- van shared helper irány
- van card-local név-alapú irány is
- van már backend/facade jellegű előkészítés is
- és ezek együtt élnek

Ez refaktorálási feladatot jelent, nem automatikusan teljes újrakezdést.

### 7.5 A tesztmotor már túl van a puszta prototípus állapoton
A jelenlegi állapot alapján a tesztmotor:
- már nem csak technikai próbafutás
- hanem ténylegesen használható hibakereső és balanszfigyelő alap

Ezért az ember-vs-AI irány előkészítése már nem idő előtti, ha kis lépésekben történik.

### 7.6 Az ember-vs-AI jelenleg még nem teljes feature-cél, hanem technikai előkészítési cél
Ez azt jelenti:
- a cél most még nem a teljes játékélmény
- hanem a döntési pontok formalizálása
- és a meglévő backend/action réteg tényleges használhatóságának növelése

---

## 8. GitHub használati alapelvek

A GitHubot a jövőben nem csak tárolásra, hanem követhető munkarendre is használni kell.

### 8.1 Alapelv
Egy commit egy jól körülírható célt szolgáljon.

Példák jó commit-típusokra:
- egy konkrét logjavítás
- egy konkrét mechanikai batch
- dokumentáció frissítés
- cleanup / rendezés
- tesztbővítés
- egy kis, izolált ember-vs-AI előkészítő lépés

### 8.2 Amit nem szabad keverni egy commitban
Lehetőleg ne keveredjen egyetlen commitba:
- runtime kódmódosítás
- dokumentációs rendezés
- reportfájl-rendezés
- nagytakarítás
- logfájlok vagy generált kimenetek
- félvezérelt CLI előkészítés és teljes mechanikai javítási batch

### 8.3 Commit üzenetek
A commit üzenetek legyenek rövidek, de egyértelműek.

Példák:
- `stabilize logging summaries`
- `add canonical trap consume metrics`
- `document engine and cards folders`
- `reorganize stats reports`
- `refactor shared source placement path`
- `add minimal human decision surface`

### 8.4 Branch használat
Ha fontosabb vagy kockázatosabb munkáról van szó, érdemes külön branch-et használni.

Példák:
- `docs/project-map`
- `cleanup/stats-structure`
- `runtime/canonical-batch-8`
- `logging/improvement-pass-2`
- `cli/human-loop-mvp`
- `rules/explainability-audit`

### 8.5 Mit nyerünk ezzel
- visszakövethető lesz, mi változott
- könnyebb lesz hibát visszakeresni
- könnyebb lesz dokumentálni a haladást
- könnyebb lesz külső segítséget bevonni
- könnyebb lesz később frontend-integrációra készülni
- kisebb lesz a kockázata annak, hogy az ember-vs-AI irány szétfolyjon

---

## 9. Jelenlegi dokumentumrendszer

A projektben jelenleg külön szerepet töltenek be ezek a dokumentumok:

### 9.1 Projekt-térkép
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ_v1.md`
- cél: mi micsoda, mi mire való, milyen státuszú

### 9.2 Hivatalos futási út
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`
- cél: a jelenlegi hivatalos runtime és core/wrapper elhatárolás rögzítése

### 9.3 Aktuális munkairány
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK.md`
- cél: a projekt működési és prioritási irányainak követése

### 9.4 Tesztprogram workflow
- `TESZTPROGRAM_WORKFLOW_ES_TESZTPROFILOK.md`
- cél: a tesztprogram használati módjai, profiljai, futtatási logikája

### 9.5 Egyéb technikai háttérdokumentumok
- szabvány
- effect-határok
- seed-konvenció
- cleanup-jelöltek
- fejlesztési terv
- külön audit- és reportfájlok
- backend/facade előkészítő dokumentumok

### 9.6 Terminológiai és dokumentumszintű tisztázás – Booster pack, Expansion pack és kiegészítő mechanikai réteg

Az AETERNA projektben külön kell választani a termékszintű és a szabályréteg-szintű fogalmakat, mert ezek részben összefüggnek, de nem azonosak.

#### Booster pack

A Booster pack az AETERNA TCG-ben is a szokásos TCG-értelemben vett kártyacsomagot jelenti: olyan csomagot, amely lapokat ad a játékhoz.

A Booster pack elsődleges szerepe:
- új lapok hozzáadása a játékhoz,
- meglévő Birodalmak és Klánok bővítése,
- új pakliépítési lehetőségek megnyitása.

A Booster pack tehát termékszintű fogalom, nem külön szabályréteg.

#### Expansion pack / Kiegészítő csomag

Az Expansion pack, magyarul Kiegészítő csomag, az AETERNA-ban is alapvetően a más TCG-kben megszokott jelentéshez igazodik.

Az Expansion pack olyan bővítés, amely:
- új lapkészletet ad a játékhoz,
- új témákat, Klánokat, Birodalmi irányokat vagy mechanikákat vezethet be,
- kibővíti a játék lehetőségeit,
- és bizonyos esetekben hibajavító vagy korrekciós szerepet is betölthet a játék fejlődése során.

Az Expansion pack tehát elsősorban a játék bővítésének termékszintű és tartalmi egysége.

#### A kiegészítő mechanikai réteg

A korábbi dokumentumokban részben „expansion-rétegként” kezelt fogalom valójában nem azonos az Expansion pack termékjelentésével.

Ezt a fogalmat a jövőben pontosabban kiegészítő mechanikai rétegnek vagy kiegészítő szabályrétegnek kell nevezni.

A kiegészítő mechanikai réteg:
- a Core fölé épül,
- külön kezelendő szabályi és mechanikai sáv,
- azt rögzíti, hogyan működnek a nem alapjátéki kivételek, új mechanikák és bővítő rendszerek,
- és nem azonos magával a termékként megjelenő Expansion packkel.

#### A kettő viszonya

Az Expansion pack és a kiegészítő mechanikai réteg nem ugyanaz, de szorosan összefügghetnek.

A helyes viszony:
- az Expansion pack a játékot bővítő tartalmi / termékszintű egység,
- a kiegészítő mechanikai réteg pedig az a szabályi háttér, amelynek alapján az ilyen bővítések új mechanikái értelmezhetők és beilleszthetők.

Vagyis egy Expansion pack tartalmazhat olyan lapokat és újításokat, amelyek működéséhez kiegészítő mechanikai réteg szükséges, de a két fogalom akkor is külön marad.

#### Követendő terminológiai elv

A projekt további szakaszában az alábbi terminológiai rendet kell követni:

- Booster pack = lapokat adó kártyacsomag
- Expansion pack / Kiegészítő csomag = a játékot bővítő új lapkészlet vagy bővítés
- Kiegészítő mechanikai réteg / kiegészítő szabályréteg = a Core fölé épülő külön szabályi-mechanikai sáv

Ennek célja, hogy a terméklogika, a tartalmi bővítés és a belső szabályréteg többé ne keveredjen össze a projekt dokumentumaiban.

---

## 10. Következő konkrét lépések

### Rövid távon

1. Az `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.md` frissítése a hibrid projektállapotra.
2. Az `Aeterna dokumentációk/` mappa további dokumentumauditja.
3. Az elavult, átvezetett, duplikált és aktív dokumentumok jelölése törlés vagy mozgatás nélkül.
4. A friss `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md` és az aktuális projektterv összehangolása.
5. A technikai adatpipeline lezárt első körének rögzítése a projekttervben.
6. A következő programfejlesztési döntési kapu kijelölése.

### Párhuzamosan

1. A két 1.4v hivatalos főforrás aktív szabályi státuszának fenntartása.
2. A kártyaadatbázis munkaforrás és exportfolyamat szerepeinek tisztítása.
3. A régi `cards.xlsx` és az újabb kártyaadatbázis munkaforrás viszonyának későbbi tisztázása.
4. A régi Python motor review státuszának fenntartása.
5. A régi `XLSX export/` mappa `OBSOLETE_AFTER_MIGRATION_CANDIDATE` státuszának megtartása.
6. Az új `Aeterna game engine/python/tools/xlsx_export/` aktív exporter státuszának megtartása.

### Ezután

A következő programfejlesztési lépés külön döntéssel induljon.

Javasolt első fejlesztési döntési kapu:

* exporter output contract mapping terv.

Ez még ne legyen runtime package builder integráció.

A mapping terv célja csak annak meghatározása legyen, hogy az exporter outputjai milyen inputként szolgálhatnak később a runtime package builder számára.

### Nem most

Most nem cél:

* teljes runtime package builder integráció;
* Godot automatikus package-frissítés;
* régi Python motor nagy refaktora;
* régi `XLSX export/` törlése vagy mozgatása;
* `Aeterna dokumentációk/` mappa tömeges átrendezése;
* tömeges kártyaátírás;
* teljes ember-vs-AI vagy UI-fejlesztés.

## 11. Egyszerű státuszblokk

### Aktuális projektállapot

Státusz: hibrid, rendezés alatt álló AETERNA projekt.

Fő technikai irány:

* új contract-first `Aeterna game engine/`;
* Python tooling + runtime package build irány;
* Godot runtime package és sample contract fogyasztói ág;
* régi Python motor review státuszban.

### Aktív hivatalos szabályforrások

* `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
* `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

### Aktív kártyaadat-munkaforrás

* `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`

Megjegyzés:

A Google Sheets / XLSX szerkesztési forrás és a helyi pipeline input copyk szerepét külön kell kezelni.

### Aktív technikai adatpipeline döntések

* `Aeterna game engine/python/tools/xlsx_export/`: `KEEP_ACTIVE_SOURCE`
* `Aeterna game engine/python/tests/test_xlsx_export.py`: `KEEP_ACTIVE_TEST`
* `Aeterna game engine/python/tests/test_xlsx_export_smoke.py`: `KEEP_ACTIVE_SMOKE_TEST`
* `Aeterna game engine/python/run_xlsx_export.bat`: `KEEP_ACTIVE_RUNNER_MANUAL`
* `Aeterna game engine/python/run_xlsx_export_smoke.bat`: `KEEP_ACTIVE_RUNNER_NONINTERACTIVE`
* `Aeterna game engine/python/sample_runtime_package/`: `GENERATED_TEST_FIXTURE`
* `Aeterna game engine/Godot/sample_runtime_package/`: `GODOT_CONSUMPTION_COPY`
* `Aeterna game engine/Godot/sample_contracts/`: `HAND_AUTHORED_TEST_FIXTURE`
* `XLSX export/`: `OBSOLETE_AFTER_MIGRATION_CANDIDATE`
* régi Python motor maradványok: `OLD_ENGINE_REVIEW`

### Jelenlegi elsődleges munka

* dokumentációs és mappaszintű rendezés;
* projektirányító dokumentumok frissítése;
* technikai adatpipeline döntések rögzítése;
* következő programfejlesztési döntési kapu előkészítése.

### Következő fejlesztési jelölt

* exporter output contract mapping terv

Ez még nem runtime package builder integráció.

### Fő tiltások / óvatossági pontok

* nem törlünk vagy mozgatunk régi mappákat külön jóváhagyás nélkül;
* nem keverjük össze a régi Python motort az új contract-first engine-nel;
* Godot nem XLSX olvasó és nem canonical adatforrás;
* nem kezdünk nagy refaktorba dokumentációs és státuszdöntés nélkül;
* nem adunk Codexnek általános, túl nagy „nézd át a projektet” típusú feladatot;
* minden technikai fejlesztés kis, ellenőrizhető lépésben induljon.

---

## 12. Verziózás

### v1
- elkészült az első központi projektterv
- a fő célok és prioritások rögzítve
- a GitHub használati alapelvek bekerültek
- a projekt jelenlegi fázisa és fókusza tisztázva

### v2
- a tesztprogram balanszfigyelő szerepe erősebben bekerült a fő fókuszok közé
- az ember-vs-AI irány nem lecserélésként, hanem bővítésként került be
- rögzítve lett a félvezérelt CLI / human-in-the-loop megközelítés mint legbiztosabb köztes út
- külön munkablokként bekerült a szabálymagyarázhatósági audit
- a prioritások frissítve lettek a jelenlegi projektállapothoz igazítva

### v3
- terminológiai tisztázásra került a Booster pack fogalma mint a játékhoz lapokat adó kártyacsomag
- rögzítve lett, hogy az Expansion pack / Kiegészítő csomag az AETERNA-ban is elsősorban a más TCG-kben megszokott jelentéshez igazodik, vagyis a játékot bővítő új lapkészletet vagy bővítést jelenti
- pontosítva lett, hogy az Expansion pack és a Core fölé épülő új mechanikák részben összefügghetnek, de nem azonosak
- külön elválasztásra került a termékszintű bővítés és a belső szabályi-mechanikai réteg fogalma
- rögzítve lett, hogy a korábban expansion-rétegként kezelt fogalmat a jövőben pontosabban kiegészítő mechanikai rétegként vagy kiegészítő szabályrétegként érdemes kezelni
- ezzel a projekt terminológiája tisztább lett a terméklogika, a tartalmi bővítés és a dokumentumszintű szabályréteg szétválasztása szempontjából

### v4
- elkészült és elsődleges szabályi forrássá vált az **AETERNA – HIVATALOS AUDITÁLT FŐFORRÁS DOKUMENTUM 1.0v.docx**;
- a projektállapot frissült a főforrás-alapú megfeleltetési fázisra;
- rögzítésre került, hogy a következő nagy munkafázis a kártyaállomány auditja az 1.0v főforrás alapján;
- rögzítésre került, hogy a Codex párhuzamosan programkód-auditot végezhet ugyanebből a főforrásból kiindulva;
- pontosításra került, hogy a kártyaaudit és a kódellenőrzés két párhuzamos, de később összevezetendő munkaszál;
- a következő konkrét lépések és az egyszerű státuszblokk frissültek.

### v5
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

### v5.1

Módosítás típusa: projektirány-frissítés / contract-first engine irány beemelése / régi Python motor státuszpontosítása / technikai adatpipeline első rendezési körének rögzítése

Érintett részek:

* `1. A projekt jelenlegi iránya`
* `2.3 Kibővített középtávú cél`
* `2.4 Hosszú távú fő cél`
* `2.5 Architektúra-cél`
* `3. Jelenlegi aktív fókusz`
* `5. Jelenlegi munkablokkok`
* `6. Prioritási sorrend`
* `10. Következő konkrét lépések`
* `11. Egyszerű státuszblokk`

Státusz: frissített projektirányító munkaváltozat

Változás leírása:

A dokumentum frissítésre kerül az AETERNA projekt új hibrid állapotának megfelelően.

A korábbi Python szabálymotor-központú projektkép pontosításra kerül. A régi Python szimulációs motor továbbra is megőrzendő és értékes referencia, de jelenlegi státusza `OLD_ENGINE_REVIEW` / `OLD_ENGINE_REFERENCE`.

A dokumentumba bekerül az új `Aeterna game engine/` contract-first digitális irány, amelyben:

* a Python ág aktív tooling, exportvalidációs és runtime package build irány;
* a Godot ág runtime package-et és sample contractokat fogyasztó debug / prototípus réteg;
* a runtime package a Python és Godot közötti programbiztos adatcontract;
* Godot nem XLSX olvasó és nem canonical adatforrás;
* az új XLSX exporter aktív helye az `Aeterna game engine/python/tools/xlsx_export/`.

Rögzítésre kerül a technikai adatpipeline hárommappás rendezésének első lezárása, beleértve:

* az új Python exporter státuszát;
* a régi `XLSX export/` mappa átmeneti migrációs jelölt státuszát;
* a Python és Godot oldali `sample_runtime_package` eltérő szerepét;
* a `Godot/sample_contracts` kézzel írt tesztfixture szerepét;
* a régi Python engine maradványok review státuszát.

A dokumentum prioritási sorrendje frissül. Elsődleges rövid távú fókusz a dokumentációs és mappaszintű rendezés, valamint a következő programfejlesztési döntési kapu előkészítése.

A következő fejlesztési jelölt az exporter output contract mapping terv, de ez még nem runtime package builder integráció.

Verziózási megjegyzés:

A jelen frissítés nem új szabályforrást hoz létre, és nem módosítja a két hivatalos 1.4v főforrás státuszát. Célja az aktuális projektirány, prioritási sorrend és technikai adatpipeline státusz pontosítása.