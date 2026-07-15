# AETERNA Game Engine – Termékruntime- és telepítési követelmények

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív termékkövetelmény és runtime-döntési mérce  
**Kapcsolódó mérföldkő:** AETERNA 0.0.1 zárt tesztkiadás

Ez a dokumentum nem választ ki programnyelvet vagy engine-runtime modellt.

Feladata annak rögzítése, hogy:

- milyen programot kell végül a játékos és a tesztelő kezébe adni;
- milyen telepítési és futtatási élmény kötelező;
- milyen külső függőségek elfogadhatók;
- milyen stabilitási és csomagolási bizonyíték szükséges;
- milyen mérce alapján hasonlítható össze a Python sidecar, a Godot .NET/C#, a GDScript vagy más jelölt;
- mikor tekinthető egy runtime-megoldás az AETERNA számára alkalmasnak.

A nyelvváltás nem önálló cél.

> **A jelenlegi Python engine csak akkor váltandó le vagy portolandó, ha a bizonyított termékkövetelmények teljesítését akadályozza, vagy egy másik megoldás összességében lényegesen biztonságosabb és fenntarthatóbb.**

---

## 1. Lezárt első termékdöntések

### 1.1 Elsődleges platform

**Döntés:**

- elsődleges platform: 64 bites Windows 10 és minden ennél újabb támogatott Windows asztali rendszer;
- a 32 bites Windows nem cél;
- Linux-támogatás később vizsgálható;
- Linux jelenleg nem prioritás és nem blokkolja a 0.0.1 Windows-kiadást.

### 1.2 Jelenlegi kiadási forma

**Döntés:**

- a technológiai proofokhoz és a jelenlegi zárt tesztverziókhoz portable, kibontott mappa elegendő;
- jelenleg nem készül telepítő;
- a portable csomag egyértelmű fő executable-ből induljon;
- a véglegesebb vagy szélesebb kiadásnál később külön telepítő készülhet;
- a telepítő kérdése nem blokkolja a mostani runtime-összehasonlítást.

### 1.3 Jogosultság és felhasználói fájlok

**Döntés:**

- a program normál futtatásához ne kelljen adminisztrátori jogosultság;
- a portable program saját mappájából induljon;
- a mentések, beállítások, logok és hibacsomagok felhasználói írható mappába kerüljenek;
- a program ne írjon futás közben védett rendszerkönyvtárba;
- egy későbbi telepítő lehetőleg felhasználónként, adminjog nélkül is telepíthető legyen.

### 1.4 Külső függőségek

**Döntés:**

- a játékosnak ne kelljen külön Pythont, Godot Editort, .NET SDK-t, Visual Studiót vagy más fejlesztői környezetet telepítenie;
- ne kelljen csomagokat, modulokat, környezeti változókat vagy több külön indítóprogramot kezelnie;
- egy kevés számú, közismert és egyszerű prerequisite elfogadható;
- például egy .NET runtime vagy hasonló széles körben használt rendszerkomponens nem kizáró ok;
- az alkalmazással együtt szállított self-contained runtime továbbra is előny;
- minden szükséges külső komponens legyen dokumentált, jogszerűen terjeszthető és egyszerűen kezelhető.

---

## 2. Elsődleges termékcél

Az AETERNA 0.0.1 célja:

- zárt, baráti és fejlesztői tesztelés;
- internetkapcsolat nélkül is használható játékmenet;
- egyszerű, játékokra jellemző indítás;
- stabil és reprodukálható futás;
- a játékos számára egyetlen termékként viselkedő program.

A játékos szempontjából az alkalmazás egyetlen termék legyen, függetlenül attól, hogy belül:

- egy folyamat;
- több folyamat;
- beágyazott runtime;
- natív könyvtár;
- vagy más technikai modell működik.

A belső architektúra nem terhelheti a játékost kézi fejlesztői beállításokkal.

---

## 3. Kötelező felhasználói futtatási élmény

### 3.1 Indítás

Kötelező cél:

- a portable csomag kibontás után indítható legyen;
- a program ikonról vagy egyértelmű fő executable-ből induljon;
- ne kelljen parancssort használni;
- ne kelljen BAT- vagy Python-scriptet kézzel futtatni;
- ne kelljen környezeti változót beállítani;
- ne kelljen portszámot vagy processzt kézzel kezelni;
- ne jelenjen meg szükségtelen konzolablak;
- az engine és a kliens indulása automatikusan, kontrolláltan történjen;
- indítási hiba esetén érthető hibaüzenet és diagnosztikai napló készüljön.

### 3.2 Leállítás

Kötelező cél:

- a program normál bezáráskor minden saját folyamatát leállítsa;
- ne maradjon háttérben elárvult engine-processz;
- mentés vagy logírás közben biztonságos lezárás történjen;
- kényszerített leállás után a következő indítás felismerhesse az előző rendellenes kilépést;
- a sérült vagy félbehagyott ideiglenes fájl ne tegye indíthatatlanná a programot.

### 3.3 Offline működés

A 0.0.1 alapjátékmenethez:

- ne legyen kötelező internetkapcsolat;
- ne legyen kötelező online fiók;
- ne legyen kötelező külső licenc- vagy hitelesítőszerver;
- a runtime package, mentések és szükséges programkomponensek helyben legyenek elérhetők.

Későbbi frissítés-, telemetria- vagy online rendszer külön döntési kapu.

---

## 4. Függőség- és terjesztési szabály

### 4.1 Amit a játékosnak nem kellhet külön telepítenie vagy kezelnie

A célkiadás nem követelheti meg kézzel:

- a Python teljes rendszertelepítését;
- Python package-ek vagy `pip` használatát;
- a Godot Editort;
- a .NET SDK-t;
- Visual Studio vagy más fejlesztői környezet telepítését;
- Git, Node.js, Java vagy más fejlesztői toolchain használatát;
- projektfájlok vagy konfigurációk kézi szerkesztését;
- több külön indítóprogram megfelelő sorrendű kézi elindítását.

### 4.2 Elfogadható függőség

Elfogadható lehet:

- az alkalmazással együtt szállított runtime;
- az alkalmazás saját könyvtárában lévő interpreter vagy framework;
- kevés számú, széles körben használt rendszerkomponens vagy redistributable;
- például megfelelő .NET runtime, ha a választott megoldás ezt ténylegesen igényli;
- olyan prerequisite, amelynek telepítése egyszerű és egyértelmű;
- operációs rendszer által biztosított alapkomponens.

Feltételek:

- a szükségessége dokumentált legyen;
- ne igényeljen fejlesztői tudást;
- a licenc és terjeszthetőség ellenőrzött legyen;
- a prerequisite hiánya esetén a program érthetően jelezzen;
- a külső függőségek száma maradjon a lehető legkisebb;
- a runtime-jelölt összehasonlításában külön mérjük a kézi telepítések számát és bonyolultságát.

### 4.3 Terjesztési modellek időbeli sorrendje

**Jelenlegi proof- és tesztfázis:**

1. portable, kibontott Windows-mappa;
2. egyértelmű fő executable;
3. külön telepítő nélkül.

**Későbbi véglegesebb kiadás:**

- Windows-telepítő;
- Start menü és parancsikon;
- eltávolítás és frissítés;
- szükség esetén prerequisite-kezelés.

A proofok jelenleg kizárólag a portable modellt kötelesek bizonyítani.

---

## 5. Stabilitási követelmények

### 5.1 Engine-stabilitás

A kiválasztott runtime-nak támogatnia kell:

- determinisztikus MatchState-kezelést;
- expected state version ellenőrzést;
- atomikus state transitiont;
- rejected action esetén változatlan state-et;
- typed eventeket;
- player-visible és debug projekció szétválasztását;
- rejtett információ védelmét;
- reprodukálható scenario-futtatást;
- strukturált diagnostics kimenetet.

### 5.2 Folyamat- és kapcsolatstabilitás

Ha több folyamat vagy bridge működik:

- legyen verziózott handshake;
- legyen timeout;
- legyen kontrollált shutdown;
- legyen megszakadt kapcsolat felismerése;
- legyen újraindítási vagy biztonságos kilépési stratégia;
- a kliens ne folytasson játékmenetet bizonytalan authoritative state mellett;
- stdout, stderr, protokoll és emberi log ne keveredjen ellenőrizetlenül.

### 5.3 Mentés és diagnosztika

Kötelező cél:

- a mentési forma verziózott legyen;
- mentés közben ne íródjon felül közvetlenül az egyetlen érvényes példány biztonsági stratégia nélkül;
- rendellenes leállás után legyen diagnosztikai nyom;
- a felhasználó által elküldhető hibacsomag ne tartalmazzon szükségtelen személyes adatot;
- a logok és mentések helye legyen meghatározott és dokumentált;
- a portable program mappája ne legyen az egyetlen kötelező írható adattárolási hely.

A teljes save/replay rendszer későbbi implementáció, de a runtime-döntés nem akadályozhatja annak biztonságos kialakítását.

---

## 6. Telepítési és csomagolási elfogadási próbák

Minden komoly runtime-jelölt ugyanazon környezetben vizsgálandó.

### 6.1 Tiszta Windows-környezet

Kötelező proof:

- 64 bites Windows 10 vagy újabb, a projekttől független tesztkörnyezet;
- nincs előre telepített fejlesztői Python;
- nincs Godot Editor;
- nincs .NET SDK;
- nincs projektforrás;
- csak a portable kiadási csomag és az explicit prerequisite áll rendelkezésre;
- normál futtatás adminisztrátori jogosultság nélkül.

Ellenőrzendő:

- ZIP vagy más csomag kibontása;
- első indítás;
- meccs-scenario futtatása;
- mentés vagy tesztállapot írása felhasználói mappába;
- bezárás;
- újraindítás;
- portable mappa törölhetősége;
- visszamaradt processzek és fájlok;
- hiányzó prerequisite érthető kezelése.

### 6.2 Ismételt indítás és leállítás

Első minimum proof:

- legalább 20 egymást követő indítás és szabályos leállítás;
- nincs elárvult processz;
- nincs portütközés;
- nincs átmeneti fájl miatti indulási hiba;
- a logok kezelhető méretűek maradnak.

### 6.3 Hosszabb futás

Első minimum soak proof:

- legalább 2 órás headless vagy gyorsított AI-vs-AI futás;
- memóriahasználat megfigyelése;
- processz- és handle-szivárgás ellenőrzése;
- determinisztikus scenario-k kontrollmintája;
- crash vagy kapcsolatvesztés esetén használható diagnostics.

A végleges kiadás előtt ennél hosszabb tesztek szükségesek lehetnek.

### 6.4 Offline próba

- hálózat nélkül elindul;
- a helyi játékmenet működik;
- hiányzó hálózat nem okoz hosszú, megmagyarázatlan várakozást;
- opcionális online funkció hiánya érthetően kezelhető.

### 6.5 Későbbi Linux-vizsgálat

- a Windows-runtime döntésnél előny, ha a választott technológia később Linuxra is átvihető;
- a Linux-proof jelenleg nem kötelező;
- a Linux-támogatás hiánya önmagában nem zár ki runtime-jelöltet a 0.0.1-ből;
- a platformfüggő döntéseket úgy dokumentáljuk, hogy egy későbbi Linux-port költsége becsülhető legyen.

---

## 7. Runtime-jelöltek összehasonlítási szempontjai

A jelöltek nem pusztán programnyelvként, hanem teljes termékruntime-modellként hasonlítandók össze.

Fő jelöltek:

- Python sidecar + Godot kliens;
- Godot .NET/C# authoritative runtime;
- GDScript authoritative runtime vagy szűk rules proof;
- szükség esetén C++ GDExtension vagy más technológia;
- embedded Python csak akkor, ha az érettség és packaging bizonyítható.

### 7.1 Elsődleges súlyozás

| Terület | Javasolt súly |
|---|---:|
| Stabilitás és hibakezelés | 25% |
| Telepítés és felhasználói egyszerűség | 25% |
| Karbantarthatóság és tesztelhetőség | 20% |
| Godot-integráció | 15% |
| AI, batch és fejlesztői tooling | 10% |
| Nyers teljesítmény | 5% |

A súlyozás emberi döntéssel módosítható, de a stabilitás és a telepítési egyszerűség nem kerülhet másodlagos helyre pusztán a fejlesztési kényelem miatt.

### 7.2 Kötelezően mérendő adatok

- kiadási csomag mérete;
- első indítás ideje;
- ismételt indítás megbízhatósága;
- memóriahasználat;
- engine-válaszidő;
- build reprodukálhatósága;
- szükséges külső telepítések száma és bonyolultsága;
- adminjog szükségessége;
- platform- és runtime-verziófüggés;
- crash és kapcsolatvesztés kezelése;
- unit és integration tesztelhetőség;
- Codex által készített kis módosítások ellenőrizhetősége;
- szabálymotor és UI fizikai elválaszthatósága;
- Python AI/batch toolinggal való együttműködés;
- későbbi Linux-port várható költsége;
- licenc- és attributionkötelezettség;
- antivírus vagy aláíratlan executable okozta tesztproblémák.

---

## 8. Kötelező architekturális elvek minden jelöltnél

A kiválasztott nyelvtől függetlenül:

- egy futásban pontosan egy authoritative MatchState legyen;
- a UI ne legyen szabályforrás;
- a kliens ne módosítsa közvetlenül az authoritative state-et;
- action request, validation, transition és response különüljön el;
- a rules engine UI nélkül is tesztelhető legyen;
- a player-visible és debug output külön maradjon;
- a runtime package ne legyen azonos a MatchState-tel;
- a kártyaadat és lookupforrás továbbra is az export- és validációs pipeline-on keresztül érkezzen;
- a Python AI-, audit- és batch tooling megtartandó akkor is, ha a termékruntime más nyelvű lesz;
- két teljes authoritative szabálymotor tartós párhuzamos fenntartása csak rendkívül erős indokkal fogadható el.

---

## 9. Döntési kapu és prioritási sorrend

### P0 – Termékkövetelmények

**Állapot:** első döntési csomag lezárva.

Lezárt:

- 64 bites Windows 10 és újabb;
- Linux későbbi, nem prioritásos lehetőség;
- portable csomag a jelenlegi proof- és tesztfázisban;
- telepítő csak későbbi véglegesebb kiadáshoz;
- adminjog nélküli normál futás;
- felhasználói írható mentés-, beállítás- és loghely;
- kevés számú közismert prerequisite elfogadható;
- fejlesztői környezet kézi telepítése nem fogadható el.

### P1 – Tanulóprogram-audit

- helyi programleltár;
- licenc;
- runtime és nyelvek;
- Godot-integráció;
- csomagolás;
- stabilitási minták;
- tiszta szobásan használható architektúraötletek.

### P2 – Közös comparison fixture

- azonos initial state;
- azonos action requestek;
- azonos expected output;
- determinisztikus JSON;
- azonos rejection-scenario;
- nyelvfüggetlen kiértékelés.

### P3 – Runtime proofok

- Python sidecar;
- C#/.NET;
- szükség esetén GDScript;
- csak indokolt esetben más technológia.

### P4 – Portable és stabilitási proof

- tiszta Windows 10+ 64-bit környezet;
- portable mappa;
- adminjog nélküli futás;
- explicit prerequisite;
- ismételt indítás;
- hosszabb futás;
- offline próba;
- diagnosztika.

### P5 – Döntési jelentés

- pontozás;
- mérési eredmények;
- ismert kockázatok;
- migrációs költség;
- ajánlás;
- emberi jóváhagyás.

### P6 – Gameplay-fejlesztés folytatása

A kiválasztott runtime-ágon:

1. Wellspring runtime integráció;
2. player-visible Wellspring summary;
3. Beáramlás;
4. Magnitúdó és Aura-payment;
5. első `play_card`;
6. további gameplay-engine lánc.

Ha a munka közben ennél súlyosabb blokkoló vagy termékkockázat merül fel, a prioritási sorrend megállítható és külön döntési kapu nyitható.

---

## 10. Nyitott, de a proof kezdetét nem blokkoló termékkérdések

A következők később döntendők el:

- milyen maximális csomagméret fogadható el;
- kell-e digitális kódaláírás a zárt 0.0.1 teszthez;
- a Windows felhasználói mappán belül pontosan hová kerüljenek a mentések, logok és hibacsomagok;
- milyen frissítési modell szükséges a 0.0.1 után;
- kell-e külön headless engine executable a tesztelői csomagban;
- mikor induljon a Linux-proof;
- milyen minimális hardverkövetelmény legyen;
- milyen adatokat tartalmazhat a hibajelentési csomag;
- hogyan kezeljük a runtime- és package-verzió inkompatibilitását;
- egy külső prerequisite-et a portable csomag mellé adjunk, automatikusan ellenőrizzünk vagy későbbi telepítő kezeljen.

Ezeket nem kell egyszerre lezárni. Mindig csak az a kérdés kerül előre, amely a következő auditot vagy proofot ténylegesen blokkolja.

---

## 11. Rövid elfogadási összefoglaló

Egy runtime-jelölt csak akkor ajánlható az AETERNA 0.0.1 authoritative termékruntime-jának, ha bizonyítottan:

- 64 bites Windows 10 vagy újabb rendszeren fut;
- portable csomagból, egyértelműen indítható;
- normál használatnál nem igényel adminjogot;
- nem igényel több fejlesztői környezet kézi telepítését;
- legfeljebb kevés, közismert és egyszerű prerequisite-et igényel;
- stabilan leáll és nem hagy elárvult folyamatot;
- offline is működik;
- tiszta Windows-környezetben reprodukálhatóan futtatható;
- megtartja a contract-first és hidden-information elveket;
- UI nélkül is tesztelhető;
- támogatja a determinisztikus és hosszabb AI-vs-AI tesztelést;
- megfelelő diagnosticsot ad;
- licencelése és terjesztése kezelhető;
- karbantartási költsége arányos a projekt méretével;
- nem kényszeríti a projektet két tartósan eltérő authoritative rules engine fenntartására.

A végleges döntés a technikai proofok, a tanulóprogram-audit, a portable futtatási tesztek és az emberi mérlegelés együttes eredménye lesz.
