# AETERNA Game Engine – Technology Decisions

Ez a dokumentum az AETERNA Game Engine technológiai döntési terét rögzíti.

Nem végleges technológiai ítélet.

Nem implementációs terv.

Nem contract-specifikáció.

Nem checkpoint-napló.

Feladata, hogy tisztázza:

* milyen szerepet kaphat Python;
* milyen szerepet kaphat Godot/GDScript;
* miért nem egyszerű „Python vagy GDScript” kérdésről van szó;
* milyen hibrid modellek lehetségesek;
* mi számít már bizonyítottnak;
* milyen döntési kapuk vannak még nyitva;
* milyen prototípusokra van szükség a végleges döntések előtt.

Kapcsolódó fő dokumentumok:

* `DECISION_MAP.md`
* `ARCHITECTURE.md`
* `CHECKPOINTS.md`
* `OPEN_QUESTIONS.md`
* `CONTRACT_SPECIFICATION.md`
* `RUNTIME_PACKAGE_SPECIFICATION.md`
* `PROTOTYPE_PLANS.md`

---

## 1. Alapállítás

Az AETERNA Game Engine technológiai kérdése nem az, hogy:

**Python vagy GDScript?**

A helyesebb kérdés:

**Melyik réteg melyik technológiában működik a legbiztonságosabban, legátláthatóbban és leghatékonyabban?**

A jelenlegi projektállapot alapján a legbiztonságosabb irány:

**contract-first architektúra + runtime package mint közös határ + rétegenkénti technológiai döntés**

Ez a megközelítés akkor is hasznos marad, ha később:

* Python marad a fő backend;
* GDScript/Godot veszi át a fő runtime szerepet;
* hibrid modell alakul ki;
* Python főként adatpipeline és tesztmotor lesz;
* Godot főként kliens és debug UI lesz.

---

## 2. Jelenlegi bizonyított technikai állapot

A checkpointok alapján jelenleg bizonyított:

* Python képes kontrollált sample runtime package-et generálni.
* Python oldali unit test működik.
* A sample runtime package többfájlos szerkezete működik.
* Godot képes a runtime package betöltésére.
* Godot képes registry-kbe rendezni a betöltött adatokat.
* Godot képes sample snapshot, legal actions és event log contractok betöltésére.
* Godot képes Snapshot viewer debug nézetet futtatni.
* Godot képes Legal action debug panelt futtatni.
* Godot képes Event log debug view-t futtatni.
* A kapcsolódó headless smoke testek működnek.
* A runtime package loader és sample contracts réteg együtt tud létezni.

Ez még nem bizonyítja:

* a teljes szabálymotor működését Pythonban;
* a teljes szabálymotor működését GDScriptben;
* legal actionök szabályból történő kiszámítását;
* action request feldolgozását;
* action-végrehajtást;
* kártyaképességek futtatását;
* AI döntéshozatalt;
* AI-vs-AI batch tesztet az új engine-ben;
* végleges játék UI-t;
* PvP működést.

---

## 3. Python lehetséges szerepei

Python erős jelölt az alábbi rétegekben:

* adatfeldolgozás;
* XLSX / JSONL / package build;
* exportvalidáció;
* LOOKUPS ellenőrzés;
* legacy alias normalizálás;
* diagnostics report generálás;
* runtime package összeállítás;
* engine support report;
* AI-vs-AI batch tesztelés;
* statisztika és balanszriport;
* régi motor referenciaelemzése;
* összehasonlító tesztek.

Python előnyei:

* gyors fejlesztés;
* erős adatfeldolgozási ökoszisztéma;
* könnyű JSON/JSONL/XLSX kezelés;
* jó automatizált teszteléshez;
* jó batch futtatáshoz;
* jó riportkészítéshez;
* jól használható AI-vs-AI szimulációkra;
* meglévő projektelőzmény kapcsolódik hozzá.

Python kockázatai:

* nem természetes Godot runtime környezet;
* Godot klienshez külön integrációs réteg kellene;
* végleges játékterjesztésnél bonyolíthatja a csomagolást;
* a régi Python motor architektúrája nem biztos, hogy hosszú távon tiszta alap;
* könnyen megmaradhat túl sok régi, card-local vagy wrapper jellegű megoldás;
* ha Python backend + Godot frontend modell lesz, később kommunikációs / szinkronizációs kérdések jelennek meg.

---

## 4. Godot / GDScript lehetséges szerepei

Godot/GDScript erős jelölt az alábbi rétegekben:

* vizuális játékfelület;
* debug UI;
* Snapshot viewer;
* Legal action debug panel;
* Event log debug view;
* játékos input kezelése;
* animáció;
* lokális játékélmény;
* későbbi player-vs-AI mód;
* későbbi player-vs-player kliens;
* esetleges saját GDScript runtime.

Godot/GDScript előnyei:

* természetes játékmotoros környezet;
* UI, input, scene, node és animációs rendszer adott;
* a felhasználó főleg Godot felületről szeretné használni;
* a már elkészült loader és debug nézetek működnek;
* a headless smoke testek explicit logfájllal működnek;
* a runtime package fogyasztása már bizonyított mintaszinten.

Godot/GDScript kockázatai:

* nem biztos, hogy kényelmes nagy, komplex szabálymotorhoz;
* GDScript adatfeldolgozásban gyengébb, mint Python;
* batch AI-vs-AI tesztelésben valószínűleg kevésbé kényelmes;
* óvni kell attól, hogy a UI node-okba rejtett szabálylogika kerüljön;
* GDScriptben a típuskezelésre és type inference hibákra figyelni kell;
* hosszú távú rules service réteg alkalmasságát még bizonyítani kell.

---

## 5. Miért nem döntünk még véglegesen?

Nem döntünk még véglegesen a fő runtime technológiáról, mert jelenleg csak az adatbetöltési, contract-betöltési és debug nézeti rétegek bizonyítottak.

Még nem bizonyított:

* GDScript teljes szabálymotor-alkalmassága;
* Python új tiszta backendként való hosszú távú fenntarthatósága;
* régi Python motor átalakíthatósága;
* hibrid rendszer fenntartható működése;
* Python ↔ GDScript azonos szabályeredmény biztosítása;
* AI-vs-AI tesztek helye;
* action execution és ability execution technológiai költsége.

Ezért a jelenlegi döntési állapot:

**nyitott, de irányított technológiai döntési tér**

---

## 6. Vizsgált technológiai modellek

### Modell A – Régi Python motor mint hosszú távú backend

Leírás:

A meglévő Python motor továbbfejlesztése, refaktorálása és backendként való megtartása.

Előnyök:

* már van működő előzmény;
* lehetnek átmenthető szabálylogikai részek;
* AI-vs-AI és batch tesztelés Pythonban természetesebb;
* adatfeldolgozás és riportkészítés erős.

Kockázatok:

* régi architektúra visszahúzhatja az új rendszert;
* card-local vagy wrapper jellegű megoldások újra beépülhetnek;
* Godot integráció bonyolultabb lehet;
* végleges digitális kliensnél Python függőség maradhat.

Jelenlegi státusz:

**nem kizárt, de nem preferált automatikus folytatás**

Döntési feltétel:

Csak akkor maradhat hosszú távú backend, ha külön audit igazolja, hogy tisztítható, contract-first módon leválasztható és fenntartható.

---

### Modell B – Új tiszta Python backend + Godot frontend

Leírás:

Új, tisztább Python rules backend készül, Godot pedig frontendként / kliensként fogyasztja a contractokat.

Előnyök:

* Python erős marad adat- és AI-oldalon;
* tisztább lehet, mint a régi motor refaktorálása;
* contract-first backend építhető;
* AI-vs-AI és balanszteszt Pythonban egyszerűbb lehet.

Kockázatok:

* Godot és Python közötti runtime kapcsolatot meg kell oldani;
* deployment / csomagolás bonyolultabb lehet;
* két technológiai stack fenntartása szükséges;
* interaktív UI és backend szinkron kérdései megjelennek.

Jelenlegi státusz:

**lehetséges hosszú távú irány, de prototípus és integrációs vizsgálat kell**

---

### Modell C – Teljes GDScript rules engine

Leírás:

A fő rules engine Godot/GDScriptben készül, Python főként adatpipeline és package builder marad.

Előnyök:

* a digitális játék teljes runtime-ja Godotban maradhat;
* nincs külön Python backend dependency játék közben;
* UI és engine egy környezetben működik;
* lokális játékprogramként egyszerűbb lehet terjeszteni.

Kockázatok:

* GDScript komplex szabálymotorra való alkalmassága még nem bizonyított;
* batch AI-vs-AI tesztelés kevésbé kényelmes lehet;
* adatvalidáció és riportok Pythonban valószínűleg jobbak;
* nagy veszély, hogy a UI és rules logic összefolyik, ha nincs tiszta service-réteg.

Jelenlegi státusz:

**erős vizsgálandó jelölt, de rules service prototípus kell**

---

### Modell D – Python test motor + GDScript játékengine hibrid

Leírás:

Python megmarad package buildernek, validátornak, AI-vs-AI / teszt motornak, Godot/GDScript pedig a játszható kliens és esetleg saját runtime irány.

Előnyök:

* mindkét technológia erősségeit használja;
* Python marad adat- és tesztoldalon;
* Godot marad kliens- és UI-oldalon;
* contract-first határ védőréteg lehet;
* összehasonlító tesztekkel ellenőrizhető az eltérés.

Kockázatok:

* két rendszer közötti szabályeltérés veszélye;
* duplikált szabálylogika alakulhat ki;
* reference engine kérdését tisztázni kell;
* comparison test nélkül hosszú távon veszélyes.

Jelenlegi státusz:

**jelenleg az egyik legerősebb átmeneti munkahipotézis**

---

### Modell E – Python package builder + GDScript main runtime

Leírás:

Python csak a package builder, validáció, diagnostics és riport oldalon marad. A fő játék runtime Godot/GDScriptben készül.

Előnyök:

* tiszta elválasztás;
* runtime package a közös határ;
* Godot a teljes játék futási környezete;
* Python nem szükséges játék közben;
* adatpipeline és játékprogram rétege szétválik.

Kockázatok:

* GDScript rules runtime alkalmasságát bizonyítani kell;
* AI-vs-AI batch tesztelés helye kérdéses;
* Python oldali referencia nélkül nehezebb lehet balansztesztelni;
* ability execution komplexitás GDScriptben még nyitott.

Jelenlegi státusz:

**erős hosszú távú jelölt, ha a GDScript rules prototípus sikeres**

---

## 7. Jelenlegi munkahipotézis

A jelenlegi legbiztonságosabb munkahipotézis:

**Python marad adatpipeline, validáció, runtime package build, diagnostics, riport és AI-vs-AI / batch tesztelési jelölt oldalon.**

**Godot/GDScript marad debug UI, játékos UI, kliens és későbbi runtime jelölt oldalon.**

**A runtime package és a contract-réteg a közös határ.**

**A végleges rules runtime döntés csak további prototípus után születhet meg.**

Ez a munkahipotézis nem végleges döntés.

---

## 8. Biztos döntések

A következő technológiai döntések jelenleg biztonságosnak tekinthetők:

* A rendszer contract-first irányban fejlődjön.
* A runtime package legyen központi adatátadási forma.
* A Python/Godot határ ne belső objektumokra, hanem fájlokra és contractokra épüljön.
* A Godot UI ne találgasson szabályokat.
* Az AI ne találgasson szabályokat.
* A legal action listát később rules engine adja.
* A snapshot player-visible módban ne szivárogtasson rejtett információt.
* A diagnostics strukturált legyen.
* A checkpointok smoke test eredményekre épüljenek.
* A régi Python motort ne emeljük át automatikusan.
* Codex rövid, célzott technikai feladatokat kapjon.

---

## 9. Nyitott döntések

Nyitott technológiai döntések:

* Python marad-e hosszú távú backend?
* GDScript alkalmas-e teljes rules runtime-nak?
* Hibrid modell marad-e hosszú távon?
* Melyik rendszer legyen referencia, ha Python és GDScript eltér?
* Kell-e Python ↔ GDScript comparison test?
* AI-vs-AI Pythonban, GDScriptben vagy mindkettőben fusson?
* A runtime package mikortól legyen kötelező input?
* Action execution melyik rétegben készüljön először?
* Ability execution melyik technológiában legyen prototipizálva?
* Milyen mélységig kell Godot headless teszteket írni?

A részletes kérdéslista helye:

`OPEN_QUESTIONS.md`

---

## 10. Godot headless tesztelési döntések

Jelenlegi tanulság:

Windows / Godot 4.7 környezetben a headless smoke test stabilabb explicit logfájllal.

Javasolt irány:

* minden headless smoke testhez legyen kényelmi `.bat` futtató;
* a futtató lépjen be a Godot projektmappába;
* a `--path "."` használható, ha a BAT a Godot mappából fut;
* legyen explicit `--log-file`;
* a smoke log fájlok ne kerüljenek verziókezelésbe;
* a root certificate store warning nem blokkoló, ha az OK output után jelenik meg.

Nem eldöntött:

* később kell-e CI-ben futtatni a Godot headless teszteket;
* milyen Godot warning számít AETERNA hibának;
* milyen Godot warning számít környezeti, nem blokkoló warningnak.

---

## 11. Codex technológiai szerepe

Codex technológiai feladatokra használható, de csak célzottan.

Codexnek adható:

* loader javítás;
* smoke test készítés;
* registry bővítés;
* package builder módosítás;
* konkrét GDScript debug panel;
* konkrét Python validátor;
* konkrét exportáló-funkció;
* fájllista alapján végzett mechanikus módosítás.

Codexnek nem adható önállóan:

* teljes projektirányítás;
* szabályi döntés;
* balanszdöntés;
* nagy homályos refaktor;
* automatikus törlés;
* mappák tömeges mozgatása pontos lista nélkül;
* végleges dokumentációs szerkezet meghatározása;
* hivatalos szabályforrás átírása emberi döntés nélkül.

Codex promptok formátuma:

* legyen rövid;
* legyen konkrét;
* legyen ellenőrizhető;
* tartalmazzon bemenetet;
* tartalmazzon elvárt outputot;
* tartalmazzon tiltásokat;
* tartalmazzon tesztelési elvárást.

---

## 12. Következő technológiai bizonyítási lépések

A következő biztonságos technológiai bizonyítási irányok:

### 12.1 Runtime package + sample contracts integráció

Cél:

* `card_id` alapján kártyanév feloldása;
* kártyatípus feloldása;
* Birodalom / Klán megjelenítése;
* legal action source és target olvashatóbbá tétele;
* missing card reference diagnostics.

Ez nem szabálymotor.

### 12.2 Unified debug dashboard

Cél:

* snapshot összefoglaló;
* legal action lista;
* event log lista;
* diagnostics összefoglaló;
* card reference resolution egy nézetben.

Ez nem interaktív játék UI.

### 12.3 Action request smoke test

Cél:

* statikus legal action alapján action request minta;
* validation stub;
* action response minta;
* diagnostics;
* snapshot_ref ellenőrzés.

Ez még nem teljes action-végrehajtás.

### 12.4 GDScript rules service minimál prototípus

Cél:

* UI-tól elkülönített rules service réteg;
* egyetlen nagyon egyszerű action ellenőrzése;
* legal action → action request → response kör;
* event log stub;
* diagnostics stub.

Ez lehet az első valódi technológiai próba arra, hogy GDScript alkalmas-e szabályrétegre.

### 12.5 Python ↔ GDScript comparison scenario

Cél:

* ugyanazon sample scenario lefuttatása Python és GDScript oldalon;
* event log összevetése;
* determinisztikus mezők ellenőrzése;
* eltérések diagnostics reportja.

Ez csak akkor aktuális, ha már mindkét oldalon van legalább minimális action execution.

---

## 13. Döntési kapuk

### Gate 1 – Godot contract fogyasztás

Státusz: részben teljesült.

Bizonyított:

* runtime package betöltés;
* sample contract betöltés;
* debug nézetek;
* smoke testek.

Következő erősítés:

* card reference resolution;
* unified dashboard;
* action request smoke.

---

### Gate 2 – GDScript rules service alkalmasság

Státusz: nyitott.

Szükséges bizonyítás:

* UI-tól elkülönített rules service;
* legal action számítás minimális mintán;
* action request / response;
* event log és diagnostics;
* headless smoke test.

---

### Gate 3 – Python hosszú távú backend alkalmasság

Státusz: nyitott.

Szükséges bizonyítás:

* régi motor audit;
* új tiszta Python backend lehetőségének vizsgálata;
* contract-first adapter;
* runtime package input;
* event log output;
* legal action output;
* AI-vs-AI futási képesség.

---

### Gate 4 – Hibrid modell fenntarthatósága

Státusz: nyitott.

Szükséges bizonyítás:

* közös runtime package;
* közös contractok;
* comparison scenario;
* eltérésdiagnosztika;
* duplikált szabálylogika kontrollja.

---

### Gate 5 – AI-vs-AI és balanszteszt technológiai helye

Státusz: későbbi.

Szükséges előfeltételek:

* stabil legal action;
* action execution;
* event log;
* ability support;
* fair snapshot;
* diagnostics;
* decklist támogatás;
* batch futtatás.

---

## 14. Jelenlegi ajánlott technológiai sorrend

A jelenlegi ajánlott sorrend:

1. Runtime package + sample contracts kapcsolat erősítése.
2. Unified debug dashboard vagy action request smoke test.
3. Contract-specifikáció szigorítása.
4. Runtime package specification szigorítása.
5. Ability module system váz stabilizálása.
6. Minimális GDScript rules service prototípus.
7. Csak ezután döntés a GDScript runtime alkalmasságáról.
8. Később Python ↔ GDScript comparison test.
9. Még később AI-vs-AI és balanszteszt.

---

## 15. Mit nem dönt el ez a dokumentum?

Ez a dokumentum nem dönti el véglegesen, hogy:

* Python lesz-e a végleges backend;
* GDScript lesz-e a végleges rules runtime;
* teljes hibrid modell marad-e;
* Python motorból mit kell átmenteni;
* AI-vs-AI hol fusson véglegesen;
* ability execution melyik nyelven készüljön véglegesen.

Ezekhez további prototípusok, auditok és emberi döntések kellenek.

---

## 16. Záró döntési állapot

A jelenlegi technológiai döntési állapot:

**A contract-first + runtime package alap biztonságos és megtartandó.**

**Python jelenleg erős adatpipeline, validációs, package build, diagnostics, riport és AI-vs-AI jelölt réteg.**

**Godot/GDScript jelenleg bizonyított package/contract fogyasztó, debug UI és későbbi játék/kliens/rules runtime jelölt.**

**A végleges rules runtime technológia nyitott döntési kapu.**

**A következő helyes technológiai lépés nem a teljes engine megírása, hanem a meglévő Godot/Python contract-first prototípus fokozatos erősítése.**
