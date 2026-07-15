# AETERNA Game Engine – Runtime Engine Language Decision Gate

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív, elsődleges következő Codex-prioritás és technológiai döntési kapu  
**Aktuális Python technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum az AETERNA végleges vagy hosszú távon fenntartható authoritative rules runtime nyelvi és futási modelljének döntési kapuját rögzíti.

A döntés súlya miatt:

- nem választunk ki előre győztes nyelvet;
- nem írjuk át az egész engine-t bizonyíték nélkül;
- nem várunk a teljes játékmotor elkészültéig;
- ugyanazt a kis, már működő contract- és transitionkészletet hasonlítjuk össze;
- a működő Python engine megmarad referenciaimplementációnak és összehasonlítási orákulumnak.

Kapcsolódó dokumentumok:

- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `CURRENT_OPEN_QUESTIONS.md`
- `TECHNOLOGY_DECISIONS.md`
- `DECISION_MAP.md`
- `CURRENT_PROTOTYPE_STATUS.md`
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

---

## 1. Prioritási döntés

A következő Codex-hozzáférés elsődleges feladata:

> **a Python sidecar + Godot, a Godot .NET/C# authoritative runtime és szükség esetén egy szűk GDScript proof összehasonlító vizsgálata és prototípusa.**

A korábban következőnek tervezett Wellspring production integráció:

- továbbra is kész, jól definiált engine-feladat;
- nincs törölve;
- a runtime-nyelvi döntési kapu mögé kerül;
- csak akkor indul újra elsődleges programozási feladatként, amikor a comparison eredménye alapján eldőlt, mely runtime-ágon érdemes folytatni.

A döntési kapuig:

- jelentős új gameplay-réteg ne épüljön kizárólag Pythonban;
- a Python engine hibajavítása, tesztfenntartása és auditja megengedett;
- dokumentáció, szabályforrás-ellenőrzés, contract-tervezés, adat- és tanulóprogram-audit folytatható;
- a meglévő Python engine nem archiválandó és nem tekintendő eldobható prototípusnak.

---

## 2. Miért most kell dönteni?

A jelenlegi Python minimal engine már elegendően fejlett ahhoz, hogy valós összehasonlítási alap legyen:

- MatchState és PlayerState;
- card instance registry;
- expected state version guard;
- invariánsok;
- `draw_card` és `end_turn`;
- typed `zone_move` és `turn_transition` eventek;
- player-visible snapshot v2;
- Domain topológia és occupancy;
- public board projection;
- activity state;
- izolált Wellspring contract;
- determinisztikus AI trajectory;
- 333 zöld izolált teszt a jelenlegi checkpointnál.

Ugyanakkor még nem készült el:

- Beáramlás;
- Aura-payment;
- `play_card`;
- teljes phase és priority rendszer;
- combat;
- ability executor;
- több száz kártyaképesség.

Ezért a migrációs és összehasonlítási költség még kontrollálható. A döntés túl késői elhalasztása jelentősen növelné az esetleges C#- vagy más runtime-váltás költségét.

---

## 3. Vizsgálandó fő modellek

### 3.1 Modell A – Python sidecar engine + Godot kliens

Lehetséges futási formák:

- stdin/stdout JSONL;
- localhost TCP + JSON;
- lokális service;
- csomagolt Python executable vagy one-folder runtime.

Erősségek:

- a jelenlegi Python engine közvetlenül újrahasználható;
- headless és AI-vs-AI tesztelés megmarad;
- a rules engine teljesen UI-független;
- processhatár jól elkülöníti az authorityt;
- a Godot csak contract-fogyasztó.

Kockázatok:

- process lifecycle;
- bridge-protokoll;
- Windows-csomagolás;
- külön runtime verzióegyeztetés;
- hibás vagy megszakadt kapcsolat kezelése;
- két executable indítása és leállítása;
- deployment méret és antivírus false positive kockázat.

Kutatási bizonyíték:

- a Godot RL Agents működő Python–Godot külön processz és localhost TCP/JSON mintát használ;
- ez nem AETERNA rules engine, de bizonyítja a technikai kommunikációs modellt.

### 3.2 Modell B – Godot .NET + C# authoritative rules runtime

Lehetséges forma:

- a rules engine tiszta C# library vagy Godot .NET projektben elkülönített C# assembly;
- a Godot UI közvetlenül C# contractokon keresztül hívja;
- a szabálymotor továbbra sem kerülhet UI node-okba.

Erősségek:

- hivatalosan támogatott Godot nyelv és .NET buildút;
- nincs külön Python process és bridge;
- erős statikus típusosság;
- kiforrott unit test és serialization eszközök;
- egyszerűbb lehet az egyetlen Windows-alkalmazásként való csomagolás;
- a Godot kliens és engine közös runtime-ban futhat.

Kockázatok:

- a meglévő Python engine portolási költsége;
- Python AI/batch és C# runtime közötti esetleges contracteltérés;
- Godot .NET build- és exportfüggőségek;
- az engine és UI helytelen összekeverésének veszélye;
- a Codex és a projekt jelenlegi C#-ismeretének gyakorlati bizonyítása szükséges.

### 3.3 Modell C – Embedded Python Godot GDExtensionnel

Példák:

- py4godot;
- godot-python-extension;
- GodoPy;
- régi godot-python.

Jelenlegi minősítés:

- kutatandó és tanulási szempontból értékes;
- több projekt aktív vagy WIP;
- több projekt saját dokumentációja szerint experimental vagy nem production ready;
- elsődleges 0.0.1 termékalapnak jelenleg magasabb kockázatú.

Nem zárható ki végleg, de nem ez legyen az első AETERNA proof.

### 3.4 Modell D – GDScript rules runtime

Lehetséges vizsgálat:

- egyetlen minimal transition;
- contract parser;
- azonos snapshot/event output;
- nem teljes második engine.

Erősségek:

- közvetlen Godot-integráció;
- egyszerű Godot export;
- nincs külső runtime.

Kockázatok:

- gyengébb statikus típusosság és nagy szabálymotor karbantarthatósága;
- Python engine-logika duplikációja;
- AI/batch tooling és játék-runtime eltérése;
- két authoritative implementáció veszélye.

Csak akkor kapjon nagyobb scope-ot, ha a tanulóprogram-audit vagy a Python/C# proof ezt indokolja.

---

## 4. Kötelező tanulóprogram-audit

A felhasználó által letöltött tanulóprogramok nincsenek az AETERNA GitHub repositoryban licencbiztonsági okból.

A Codex-audit előtt külön helyi leltár kell.

Projektenként rögzítendő:

- projekt neve és forrása;
- vizsgált commit/tag/verzió;
- licenc;
- programnyelvek;
- Godot-verzió;
- rules runtime helye;
- authoritative state helye;
- Python használat módja;
- C# használat módja;
- GDScript szerepe;
- frontend–engine kommunikáció;
- processindítás és lifecycle;
- packaging;
- Windows támogatás;
- tesztek;
- használható architektúraminta;
- AETERNA-kockázat;
- szükséges attribution;
- clean-room módon reprodukálható ötlet.

Kiemelt online referenciák:

- `edbeeching/godot_rl_agents`
- `edbeeching/godot_rl_agents_plugin`
- `niklas2902/py4godot`
- `niklas2902/py4godot-examples`
- `maiself/godot-python-extension`
- `godopy/godopy`
- `touilleMan/godot-python`

Másolt kód alapértelmezés szerint ne kerüljön az AETERNA repositoryba. A vizsgálat elsődlegesen architektúra- és működésminta-audit.

---

## 5. Közös összehasonlítási scenario

A három fő proof ugyanazt a kis scenario-contractot használja.

### Kötelező alapállapot

- két játékos;
- néhány determinisztikus card instance;
- deck és hand;
- state version;
- event sequence;
- minimal Domain topológia;
- player-visible snapshot.

### Kötelező lépések

1. initial state létrehozása;
2. `draw_card` P1;
3. `end_turn` P1 → P2;
4. `draw_card` P2;
5. player-visible snapshot P1 számára;
6. player-visible snapshot P2 számára;
7. event log export;
8. ugyanazon input második futtatása;
9. determinisztikus JSON összevetés;
10. stale `expected_state_version` rejection.

### Kötelező contractok

- action request;
- action response;
- typed event envelope;
- player-visible snapshot;
- state version;
- diagnostics vagy kontrollált rejection;
- JSON-kompatibilis serialization.

A proof nem igényli a teljes Domain-, Wellspring- vagy gameplay-rendszer portolását, ha a fenti scenario ezek nélkül is összevethető.

---

## 6. Első Codex-feladat szakaszai

### Szakasz 0 – Read-only audit

- vizsgálja meg az AETERNA jelenlegi Python engine contractjait;
- vizsgálja meg a Godot projekt és a runtime package jelenlegi állapotát;
- leltározza a helyi tanulóprogramokat;
- ellenőrizze a licenceket;
- ne módosítson kódot;
- készítsen összehasonlító tervet és fájlscope-ot.

### Szakasz 1 – Közös comparison fixture

- egy nyelvfüggetlen, verziózott scenario/input fixture;
- expected output és összehasonlítási szabályok;
- canonical JSON rendezés;
- eltérések strukturált jelentése.

### Szakasz 2 – Python sidecar proof

- minimális engine launcher;
- handshake;
- action request/response;
- snapshot/event export;
- kontrollált shutdown;
- stdout csak protokoll vagy külön csatorna;
- log stderr-re vagy fájlba;
- Windows futtatási proof.

### Szakasz 3 – Godot .NET/C# proof

- ugyanazon scenario C# implementációja;
- tiszta rules library/UI-elhatárolás;
- azonos vagy explicit kompatibilis JSON-contract;
- unit tesztek;
- Godot .NET indítás;
- Windows export vagy legalább reprodukálható export proof.

### Szakasz 4 – Opcionális minimal GDScript proof

Csak akkor készüljön, ha:

- az audit konkrét előnyt jelez;
- a C# és Python eredmény nem ad elég döntési információt;
- a scope egyetlen transitionre és contract round-tripre korlátozható.

### Szakasz 5 – Döntési jelentés

A jelentés ne csak működés/nem működés eredményt adjon, hanem mérhető összevetést.

---

## 7. Összehasonlítási mátrix

Minden jelöltet azonos skálán kell értékelni.

### Kötelező szempontok

- contracthűség;
- determinisztikus output;
- hidden-information biztonság;
- unit tesztelhetőség;
- headless futtathatóság;
- AI-vs-AI és batch alkalmasság;
- Godot-integráció egyszerűsége;
- Windows-csomagolás;
- egykattintásos vagy egyszerű indítás;
- process- és crash-kezelés;
- performance és latency;
- debugolhatóság;
- logolás;
- dependencyk;
- build reprodukálhatóság;
- repository és projektméret;
- Codex által előállított kód minősége;
- emberi karbantarthatóság;
- portolási költség;
- hosszú távú kártyaképesség-rendszer alkalmassága;
- replay és save/load alkalmasság;
- licenc- és attributionkövetelmények.

### Különösen fontos döntési súlyok

Magas súly:

- szabályhelyesség;
- tesztelhetőség;
- determinisztika;
- karbantarthatóság;
- Windows-terjeszthetőség;
- Godot klienssel való stabil együttműködés.

Közepes súly:

- buildméret;
- indítási idő;
- latency;
- fejlesztői kényelem.

Alacsonyabb súly az első döntésnél:

- mobil és web export;
- végleges grafikai teljesítmény;
- online multiplayer.

---

## 8. Elfogadási feltételek

A nyelvi/runtime döntési kapu csak akkor zárható le, ha:

- a tanulóprogram-audit elkészült;
- a közös scenario rögzített;
- a Python referenciafutás reprodukálható;
- legalább a Python sidecar és a C# proof elkészült;
- ugyanazon contractok vagy explicit mapping alapján összevethetők;
- Windows-indítás és packaging legalább prototípusszinten bizonyított;
- az eltérések és korlátok dokumentáltak;
- a licenckövetelmények ellenőrzöttek;
- a felhasználó megkapja az A/B/C döntési javaslatot;
- a végleges választás emberi jóváhagyással történik.

---

## 9. A döntés lehetséges eredményei

### Eredmény A – Python sidecar marad authoritative runtime

Következmény:

- Python engine-fejlesztés folytatása;
- Godot bridge és packaging termékesítése;
- C# csak kliens- vagy adapteroldali szerepben, ha egyáltalán szükséges.

### Eredmény B – C# lesz az authoritative termékruntime

Következmény:

- a Python engine referenciaimplementáció és tesztorákulum marad;
- kontrollált, contractonkénti C# migráció;
- Python továbbra is adatpipeline, AI/batch, audit és balansztooling;
- nem egyetlen nagy automatikus port.

### Eredmény C – Hibrid vagy részleges megosztás

Csak akkor fogadható el, ha:

- egyértelmű az authoritative state;
- nincs duplikált legalitásszámítás;
- a réteghatár contracttal védett;
- a tesztelés bizonyítja az egyezést;
- a packaging kezelhető.

### Eredmény D – GDScript runtime bizonyul a legjobb megoldásnak

Csak célzott bizonyíték után fogadható el. Ekkor a Python továbbra is tooling-, AI-, batch- és referencia-réteg maradhat.

---

## 10. Átmeneti munkarend Codex nélkül

Amíg a Codex nem használható:

- folytatódik a dokumentációs konszolidáció;
- az `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` közös triázsa;
- ability rendszer dokumentációs auditja;
- contract-specifikáció konszolidációja;
- tanulóprogramok külső és helyi leltárának előkészítése;
- licenc- és forrásjegyzék;
- összehasonlítási kritériumok pontosítása;
- szabályforrásból megválaszolható engine-kérdések ellenőrzése.

Nem indul:

- teljes C# engine-port;
- teljes GDScript engine;
- új nagy Python gameplay-réteg;
- végleges bridge-implementáció;
- nyelvi döntés pusztán vélemény alapján.

---

## 11. Jelenlegi rövid státusz

**Jelenlegi működő referencia:** Python minimal rules engine.  
**Következő Codex-prioritás:** runtime-nyelvi és integrációs comparison.  
**Kötelező fő jelöltek:** Python sidecar és Godot .NET/C#.  
**Opcionális harmadik proof:** szűk GDScript transition.  
**Embedded Python:** kutatandó, jelenleg magasabb kockázatú.  
**Wellspring integration:** kész következő gameplay-feladat, de a nyelvi döntési kapu mögé sorolva.  
**Codex nélküli aktív munkasáv:** dokumentáció, audit, contract- és döntés-előkészítés.
