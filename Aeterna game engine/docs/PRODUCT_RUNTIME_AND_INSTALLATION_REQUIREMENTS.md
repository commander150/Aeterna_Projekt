# AETERNA Game Engine – Termékruntime- és telepítési követelmények

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2  
**Dátum:** 2026-07-20  
**Státusz:** aktív termékkövetelmény és release-elfogadási mérce  
**Kapcsolódó mérföldkő:** AETERNA 0.0.1 zárt tesztkiadás  
**Kiválasztott architektúra:** Godot/GDScript visual client + C# authoritative engine + Python external tooling

Ez a dokumentum azt rögzíti, milyen programot kell a játékos és a tesztelő kezébe adni.

Nem:

- rules engine-specifikáció;
- napi fejlesztési terv;
- csomagolóscript;
- annak bizonyítéka, hogy a production build már elkészült.

A runtime-nyelvi döntés lezárult, de a production C# packaging még külön bizonyítandó.

---

## 1. Elsődleges platform

Döntés:

- 64 bites Windows 10 és újabb támogatott Windows asztali rendszer;
- 32 bites Windows nem cél;
- Linux később vizsgálható;
- Linux nem blokkolja a 0.0.1 Windows-kiadást.

A pontos minimális OS-build és hardverigény valós production build mérése után rögzíthető.

---

## 2. Kiadási forma

A proofokhoz és zárt tesztverzióhoz:

- portable, kibontott mappa;
- egyértelmű fő executable;
- telepítő nélkül;
- internetkapcsolat nélkül is használható;
- egyszerű törlés és frissítés.

Később:

- külön installer;
- digitális aláírás;
- automatikus frissítés;
- platform-specifikus csomagolás.

Ezek nem korai C.5B-követelmények.

---

## 3. Jogosultság és felhasználói fájlok

A normál futtatás:

- ne igényeljen adminisztrátori jogosultságot;
- ne írjon védett rendszerkönyvtárba;
- ne igényeljen fejlesztői parancssort.

A következő adatok felhasználói írható helyre kerüljenek:

- mentések;
- beállítások;
- profil;
- logok;
- crash/bug report csomag;
- replay vagy diagnosztikai export, ha van.

A pontos Windows-könyvtár külön implementation decision.

---

## 4. Külső függőségek

A játékosnak nem kellhet:

- Python;
- Godot Editor;
- .NET SDK;
- Visual Studio;
- csomagkezelő;
- környezeti változó;
- több kézi processzindítás;
- külön adatbuilder.

Elfogadható:

- az alkalmazással szállított self-contained .NET runtime;
- vagy kevés, közismert, egyszerű prerequisite, dokumentált telepítéssel.

Előnyben részesített:

- egyetlen Godot .NET alkalmazáscsomag;
- szükséges C# runtime-komponensek együtt szállítva;
- Python nélküli játékosoldali futás.

---

## 5. Processztopológia

Tervezett normál játék:

```text
Godot .NET application
    └── C# authoritative engine in-process
```

Nem szükséges:

- Python sidecar;
- TCP-listener;
- külön engine executable;
- watchdog;
- orphan-processz kezelés;
- localhost service.

Fejlesztői/batch környezetben külön használható:

- `Aeterna.Engine.Headless`;
- Python controller;
- CI;
- AI-vs-AI és fixture runner.

---

## 6. Indítás és leállítás

Kötelező cél:

- kibontás után egyértelműen indítható;
- egy fő executable;
- normál ablakbezárás;
- F8 vagy fejlesztői stop esetén tiszta leállás;
- nincs elárvult AETERNA processz;
- nincs nyitva maradó TCP-listener;
- nincs kézi cleanup;
- újraindítás tiszta állapotból.

A bizonyított C# candidate proof megfelelt a processzen belüli működés alapjainak, de a production engine és export külön tesztelendő.

---

## 7. Offline működés

A 0.0.1 alapjátéka:

- internet nélkül induljon;
- internet nélkül játsszon;
- internet nélkül töltsön be runtime package-et;
- ne igényeljen online fiókot;
- ne igényeljen felhőszolgáltatást.

Opcionális későbbi online szolgáltatás nem ronthatja az offline alapműködést.

---

## 8. Stabilitás

Minimum release-elfogadás:

- normál indítás;
- ismételt indítás;
- több egymás utáni mérkőzés;
- normál kilépés;
- fejlesztői stop;
- hosszabb soak futás;
- hibás package kezelése;
- hiányzó vagy inkompatibilis package kezelése;
- mentés- és logírási hiba kezelése;
- crash esetén diagnosztikai nyom.

Nem elfogadható:

- csendes állapotromlás;
- félbehagyott state mutation;
- rejtett információ szivárgása;
- elárvult processz;
- fejlesztői környezet hiánya miatt használhatatlan player build.

---

## 9. Determinizmus és reprodukálhatóság

Fejlesztői és teszt buildben legyen rögzíthető:

- engine version;
- ruleset version;
- runtime package ID/version/hash;
- seed;
- deck ID-k;
- match ID;
- AI policy/version;
- action history;
- event sequence;
- state version;
- diagnostics summary.

Azonos inputból az engine determinisztikus contractok esetén azonos eredményt adjon.

---

## 10. Log és hibacsomag

Fejlesztői vagy tesztmódban legyen elérhető:

- alkalmazásverzió;
- OS és runtime információ;
- runtime package identity;
- engine diagnostics;
- Godot log;
- C# exception/stack trace;
- match vagy scenario reference;
- seed;
- releváns snapshot/event/action adatok;
- rejtett információt nem szivárogtató felhasználói csomag.

Player-facing hibaüzenet rövid és biztonságos.

A részletes developer diagnostics elkülönül.

---

## 11. Runtime package elhelyezése

A player build tartalmazza vagy biztonságosan eléri a validált runtime package-et.

Kötelező:

- verzió- és compatibility-ellenőrzés;
- hiányzó package esetén kontrollált hiba;
- sérült package esetén kontrollált hiba;
- development és release package elkülönítése;
- szerkesztési XLSX nem szükséges a player buildhez.

---

## 12. Mentés és profil

A 0.0.1 célállapotban tervezett:

- helyi profil;
- beállítások;
- paklik;
- gyűjtemény;
- tesztgazdaság;
- mérkőzésállapot vagy folytatás, ha a gameplay design igényli.

A save schema:

- verziózott;
- visszafelé kompatibilitási vagy migrációs policyvel;
- hibás mentésnél kontrollált;
- külön a runtime package-től.

A pontos mentési contract későbbi szakasz.

---

## 13. Biztonság és adatvédelem

A zárt tesztverzió:

- ne gyűjtsön szükségtelen személyes adatot;
- ne küldjön automatikusan logot internetre;
- hibacsomag megosztása felhasználói művelet legyen;
- logban ne legyen szükségtelen elérési út vagy érzékeny adat;
- rejtett játékinformáció player-facing csomagban ne szivárogjon.

Nyilvánosabb kiadásnál később:

- package integritás;
- code signing;
- tamper detection;
- privacy notice;
- crash reporting consent.

---

## 14. Teljesítmény

A pontos célértékek valós vertical slice után mérendők.

Elvárt:

- UI nem fagy meg normál action alatt;
- legal action és snapshot elfogadható időn belül készül;
- egy meccs memóriája kontrollált;
- batch futás külön headless útvonalon skálázható;
- a Python tooling nem kerül a Godot frame loopba;
- service API csak mért szükség esetén készül.

---

## 15. Windows packaging proof

A production C# engine után kötelező bizonyítás:

1. Godot .NET export;
2. tiszta tesztgépes indítás;
3. szükséges .NET runtime modell;
4. portable mappa;
5. offline futás;
6. normál kilépés;
7. több egymás utáni indítás;
8. runtime package betöltés;
9. log és user data helye;
10. nincs Python prerequisite;
11. nincs SDK vagy Editor prerequisite;
12. nincs orphan process vagy listener;
13. legalább rövid soak teszt;
14. verzió- és hibajelzés.

Ez a proof még nincs kész.

---

## 16. Release profilok

Javasolt fokozatok:

### Developer

- részletes log;
- debug snapshot;
- developer diagnostics;
- fixture és smoke eszközök.

### Closed test

- player-facing alkalmazás;
- kontrollált bug report;
- debug funkciók korlátozva;
- validált runtime package;
- egyszerű portable terjesztés.

### Public release

- stabil packaging;
- integritásvédelem;
- code signing lehetőség;
- release notes;
- kompatibilitási és frissítési policy.

---

## 17. Elfogadási kapu 0.0.1 előtt

A program akkor tekinthető átadható zárt tesztbuildnek, ha:

- egyszerűen indul;
- offline működik;
- nem igényel fejlesztői eszközt;
- teljes meccs lejátszható;
- szabálymotor determinisztikus és tesztelt;
- hidden information védett;
- mentés és beállítások kontrolláltak;
- log és bug report használható;
- nincs ismert blocking crash;
- nincs orphan process;
- runtime package kompatibilis;
- verziók visszakereshetők;
- a fő gameplay vertical slice-ok zöldek.

---

## 18. Aktuális állapot

Lezárt:

- Python-sidecar proof;
- C# in-process candidate proof;
- runtime-nyelvi döntés;
- Godot + C# + Python szerepfelosztás.

Még nyitott:

- production C# engine;
- production Godot bridge;
- Windows export;
- self-contained/prerequisite döntés;
- save/log végleges helye;
- soak és tiszta gépes teszt;
- release package identity;
- 0.0.1 teljes gameplay.

A termékruntime-követelmények továbbra is kötelező elfogadási mércék. A kiválasztott C# architektúra csak akkor tekinthető release-késznek, ha ezeket production builddel bizonyítja.
