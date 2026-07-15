# AETERNA Game Engine – Termékruntime- és telepítési követelmények

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
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

## 1. Elsődleges termékcél

Az AETERNA 0.0.1 elsődleges platformja:

- Windows asztali számítógép;
- első körben 64 bites rendszer;
- zárt, baráti és fejlesztői tesztelés;
- internetkapcsolat nélkül is használható játékmenet;
- egyszerű, játékokra jellemző indítás.

A játékos szempontjából az alkalmazás egyetlen termék legyen, függetlenül attól, hogy belül:

- egy folyamat;
- több folyamat;
- beágyazott runtime;
- natív könyvtár;
- vagy más technikai modell működik.

A belső architektúra nem terhelheti a játékost kézi fejlesztői beállításokkal.

---

## 2. Kötelező felhasználói futtatási élmény

### 2.1 Indítás

Kötelező cél:

- a program ikonról vagy egyértelmű fő executable-ből induljon;
- ne kelljen parancssort használni;
- ne kelljen BAT- vagy Python-scriptet kézzel futtatni;
- ne kelljen környezeti változót beállítani;
- ne kelljen portszámot vagy processzt kézzel kezelni;
- ne jelenjen meg szükségtelen konzolablak;
- az engine és a kliens indulása automatikusan, kontrolláltan történjen;
- indítási hiba esetén érthető hibaüzenet és diagnosztikai napló készüljön.

### 2.2 Leállítás

Kötelező cél:

- a program normál bezáráskor minden saját folyamatát leállítsa;
- ne maradjon háttérben elárvult engine-processz;
- mentés vagy logírás közben biztonságos lezárás történjen;
- kényszerített leállás után a következő indítás felismerhesse az előző rendellenes kilépést;
- a sérült vagy félbehagyott ideiglenes fájl ne tegye indíthatatlanná a programot.

### 2.3 Offline működés

A 0.0.1 alapjátékmenethez:

- ne legyen kötelező internetkapcsolat;
- ne legyen kötelező online fiók;
- ne legyen kötelező külső licenc- vagy hitelesítőszerver;
- a runtime package, mentések és szükséges programkomponensek helyben legyenek elérhetők.

Későbbi frissítés-, telemetria- vagy online rendszer külön döntési kapu.

---

## 3. Függőség- és telepítési szabály

### 3.1 Amit a játékosnak nem kellhet külön telepítenie

A célkiadás nem követelheti meg kézzel:

- a Python teljes rendszertelepítését;
- Python package-ek vagy `pip` használatát;
- a Godot Editort;
- a .NET SDK-t;
- Visual Studio vagy más fejlesztői környezet telepítését;
- Git, Node.js, Java vagy más fejlesztői toolchain használatát;
- projektfájlok vagy konfigurációk kézi szerkesztését;
- több külön indítóprogram megfelelő sorrendű kézi elindítását.

### 3.2 Elfogadható függőség

Elfogadható lehet:

- az alkalmazással együtt szállított runtime;
- az alkalmazás saját könyvtárában lévő interpreter vagy framework;
- egyetlen, széles körben használt rendszerkomponens vagy redistributable;
- olyan prerequisite, amelyet a telepítő automatikusan és egyértelműen kezel;
- operációs rendszer által biztosított alapkomponens.

Feltételek:

- a szükségessége dokumentált legyen;
- a telepítés ne igényeljen fejlesztői tudást;
- a licenc és terjeszthetőség ellenőrzött legyen;
- az eltávolítás és frissítés kezelhető legyen;
- a prerequisite hiánya esetén a program érthetően jelezzen.

### 3.3 Preferált terjesztési modellek

Elsőként vizsgálandó:

1. **portable vagy kibontott tesztmappa**;
2. **egyetlen Windows-telepítő**;
3. szükség esetén mindkettő.

A portable forma fejlesztői és zárt tesztelési célra előnyös lehet.

A telepítő a későbbi szélesebb tesztelésnél lehet elsődleges.

A 0.0.1 elfogadásához legalább az egyik modellnek stabilan működnie kell tiszta tesztkörnyezetben.

---

## 4. Stabilitási követelmények

### 4.1 Engine-stabilitás

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

### 4.2 Folyamat- és kapcsolatstabilitás

Ha több folyamat vagy bridge működik:

- legyen verziózott handshake;
- legyen timeout;
- legyen kontrollált shutdown;
- legyen megszakadt kapcsolat felismerése;
- legyen újraindítási vagy biztonságos kilépési stratégia;
- a kliens ne folytasson játékmenetet bizonytalan authoritative state mellett;
- stdout, stderr, protokoll és emberi log ne keveredjen ellenőrizetlenül.

### 4.3 Mentés és diagnosztika

Kötelező cél:

- a mentési forma verziózott legyen;
- mentés közben ne íródjon felül közvetlenül az egyetlen érvényes példány biztonsági stratégia nélkül;
- rendellenes leállás után legyen diagnosztikai nyom;
- a felhasználó által elküldhető hibacsomag ne tartalmazzon szükségtelen személyes adatot;
- a logok és mentések helye legyen meghatározott és dokumentált.

A teljes save/replay rendszer későbbi implementáció, de a runtime-döntés nem akadályozhatja annak biztonságos kialakítását.

---

## 5. Telepítési és csomagolási elfogadási próbák

Minden komoly runtime-jelölt ugyanazon környezetben vizsgálandó.

### 5.1 Tiszta Windows-környezet

Kötelező proof:

- tiszta vagy a projekttől független Windows tesztkörnyezet;
- nincs előre telepített fejlesztői Python;
- nincs Godot Editor;
- nincs .NET SDK;
- nincs projektforrás;
- csak a kiadási csomag és az explicit prerequisite áll rendelkezésre.

Ellenőrzendő:

- telepítés vagy kibontás;
- első indítás;
- meccs-scenario futtatása;
- mentés vagy tesztállapot írása;
- bezárás;
- újraindítás;
- eltávolítás vagy mappatörlés;
- visszamaradt processzek és fájlok.

### 5.2 Ismételt indítás és leállítás

Első minimum proof:

- legalább 20 egymást követő indítás és szabályos leállítás;
- nincs elárvult processz;
- nincs portütközés;
- nincs átmeneti fájl miatti indulási hiba;
- a logok kezelhető méretűek maradnak.

### 5.3 Hosszabb futás

Első minimum soak proof:

- legalább 2 órás headless vagy gyorsított AI-vs-AI futás;
- memóriahasználat megfigyelése;
- processz- és handle-szivárgás ellenőrzése;
- determinisztikus scenario-k kontrollmintája;
- crash vagy kapcsolatvesztés esetén használható diagnostics.

A végleges kiadás előtt ennél hosszabb tesztek szükségesek lehetnek.

### 5.4 Offline próba

- hálózat nélkül elindul;
- a helyi játékmenet működik;
- hiányzó hálózat nem okoz hosszú, megmagyarázatlan várakozást;
- opcionális online funkció hiánya érthetően kezelhető.

---

## 6. Runtime-jelöltek összehasonlítási szempontjai

A jelöltek nem pusztán programnyelvként, hanem teljes termékruntime-modellként hasonlítandók össze.

Fő jelöltek:

- Python sidecar + Godot kliens;
- Godot .NET/C# authoritative runtime;
- GDScript authoritative runtime vagy szűk rules proof;
- szükség esetén C++ GDExtension vagy más technológia;
- embedded Python csak akkor, ha az érettség és packaging bizonyítható.

### 6.1 Elsődleges súlyozás

| Terület | Javasolt súly |
|---|---:|
| Stabilitás és hibakezelés | 25% |
| Telepítés és felhasználói egyszerűség | 25% |
| Karbantarthatóság és tesztelhetőség | 20% |
| Godot-integráció | 15% |
| AI, batch és fejlesztői tooling | 10% |
| Nyers teljesítmény | 5% |

A súlyozás emberi döntéssel módosítható, de a stabilitás és a telepítési egyszerűség nem kerülhet másodlagos helyre pusztán a fejlesztési kényelem miatt.

### 6.2 Kötelezően mérendő adatok

- kiadási csomag mérete;
- első indítás ideje;
- ismételt indítás megbízhatósága;
- memóriahasználat;
- engine-válaszidő;
- build reprodukálhatósága;
- szükséges külső telepítések száma;
- platform- és runtime-verziófüggés;
- crash és kapcsolatvesztés kezelése;
- unit és integration tesztelhetőség;
- Codex által készített kis módosítások ellenőrizhetősége;
- szabálymotor és UI fizikai elválaszthatósága;
- Python AI/batch toolinggal való együttműködés;
- licenc- és attributionkötelezettség;
- antivírus vagy aláíratlan executable okozta tesztproblémák.

---

## 7. Kötelező architekturális elvek minden jelöltnél

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

## 8. Döntési kapu és prioritási sorrend

### P0 – Termékkövetelmények

Jelen dokumentum létrehozása és emberi felülvizsgálata.

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

### P4 – Telepítési és stabilitási proof

- tiszta Windows-környezet;
- portable vagy installer;
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

## 9. Jelenleg nyitott termékkérdések

A következő kérdések még nem lezártak:

- Windows 10, Windows 11 vagy mindkettő legyen-e az első hivatalos minimum;
- portable mappa, telepítő vagy mindkettő legyen-e a 0.0.1 kiadási forma;
- elfogadható-e egy automatikusan telepített redistributable;
- milyen maximális csomagméret fogadható el;
- kell-e digitális kódaláírás a zárt 0.0.1 teszthez;
- hová kerüljenek a mentések, logok és hibacsomagok;
- milyen frissítési modell szükséges a 0.0.1 után;
- kell-e külön headless engine executable a tesztelői csomagban;
- szükséges-e több operációs rendszer támogatása a 0.0.1 előtt;
- milyen minimális hardverkövetelmény legyen;
- milyen adatokat tartalmazhat a hibajelentési csomag;
- hogyan kezeljük a runtime- és package-verzió inkompatibilitását.

Ezeket nem kell egyszerre lezárni. A proofok megkezdéséhez először csak azok a kérdések döntendők el, amelyek közvetlenül befolyásolják az összehasonlíthatóságot.

---

## 10. Rövid elfogadási összefoglaló

Egy runtime-jelölt csak akkor ajánlható az AETERNA 0.0.1 authoritative termékruntime-jának, ha bizonyítottan:

- a játékos számára egyszerűen indítható;
- nem igényel több fejlesztői környezet kézi telepítését;
- stabilan leáll és nem hagy elárvult folyamatot;
- offline is működik;
- tiszta Windows-környezetben reprodukálhatóan telepíthető vagy futtatható;
- megtartja a contract-first és hidden-information elveket;
- UI nélkül is tesztelhető;
- támogatja a determinisztikus és hosszabb AI-vs-AI tesztelést;
- megfelelő diagnosticsot ad;
- licencelése és terjesztése kezelhető;
- karbantartási költsége arányos a projekt méretével;
- nem kényszeríti a projektet két tartósan eltérő authoritative rules engine fenntartására.

A végleges döntés a technikai proofok, a tanulóprogram-audit, a telepítési tesztek és az emberi mérlegelés együttes eredménye lesz.