# AETERNA Game Engine – Runtime Engine Language Decision Gate

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív, elsődleges következő Codex-prioritás és technológiai döntési kapu  
**Aktuális Python technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum az AETERNA végleges vagy hosszú távon fenntartható authoritative rules runtime nyelvi és futási modelljének döntési kapuja.

A döntés célja nem a Python leváltása. A cél annak bizonyítása, hogy melyik runtime-modell ad:

- stabil működést;
- egyszerű Windows 10+ 64 bites portable futtatást;
- kevés külső függőséget;
- jól tesztelhető és karbantartható szabálymotort;
- megbízható Godot-integrációt;
- hosszú távon használható AI-, batch-, replay- és diagnostics-alapot.

A működő Python engine referenciaimplementáció és összehasonlítási orákulum marad akkor is, ha később más nyelv lesz a termékruntime.

Kapcsolódó aktív dokumentumok:

- `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`
- `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`
- `LEARNING_PROJECT_AUDIT_QUEUE.md`
- `CURRENT_OPEN_QUESTIONS.md`
- `CURRENT_CONTRACT_STATUS.md`
- `TECHNOLOGY_DECISIONS.md`
- `ARCHITECTURE.md`
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

---

## 1. Prioritási döntés

A következő Codex-hozzáférés elsődleges feladata:

> **a Python sidecar + Godot és a Godot .NET/C# authoritative runtime bizonyíték-alapú összehasonlítása, szükség esetén szűk GDScript vagy más célzott prooffal.**

A Wellspring production integráció:

- továbbra is kész, jól definiált engine-feladat;
- nincs törölve;
- a runtime-nyelvi döntési kapu mögött várakozik;
- a kiválasztott runtime-ág első jelentős gameplay-feladata lesz.

A döntési kapuig:

- jelentős új gameplay-réteg ne épüljön kizárólag Pythonban;
- a Python engine hibajavítása, tesztfenntartása és auditja megengedett;
- dokumentáció, szabályforrás-ellenőrzés, contract-tervezés és tanulóprogram-audit folytatható;
- teljes C#- vagy GDScript-engine nem készülhet a comparison előtt;
- a meglévő Python engine nem archiválandó és nem tekintendő eldobható prototípusnak.

---

## 2. Miért most kell dönteni?

A Python minimal engine már elegendően fejlett valós összehasonlítási alapnak:

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

Még nem készült el:

- Beáramlás;
- Aura-payment;
- `play_card`;
- teljes phase és priority rendszer;
- combat;
- ability executor;
- több száz kártyaképesség.

Ezért a comparison és egy esetleges kontrollált migráció költsége még kezelhető. A döntés teljes engine után történő elhalasztása indokolatlanul drága lenne.

---

## 3. Termékkövetelmények, amelyeket minden jelöltnek teljesítenie kell

Lezárt első követelmények:

- elsődleges cél: Windows 10 és újabb, 64 bit;
- jelenlegi proof- és zárt tesztforma: portable, kibontott mappa;
- egyértelmű fő executable;
- normál futáshoz nem kellhet adminjog;
- nem kellhet külön Python, Godot Editor, .NET SDK vagy fejlesztői toolchain;
- kevés számú, közismert prerequisite elfogadható;
- offline játékmenet szükséges;
- a játékos szempontjából az alkalmazás egyetlen termékként viselkedjen;
- minden saját folyamat kontrolláltan induljon és álljon le;
- mentések, beállítások és logok felhasználói írható mappába kerüljenek.

A részletes mérce a `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md` fájlban található.

---

## 4. Vizsgálandó runtime-modellek

### 4.1 Modell A – Python sidecar engine + Godot kliens

Lehetséges formák:

- child process + stdin/stdout JSONL;
- localhost TCP + JSON;
- csomagolt Python executable vagy one-folder runtime;
- a játékos számára egy fő Godot-indító, amely automatikusan kezeli a sidecart.

Erősségek:

- a jelenlegi Python engine közvetlenül újrahasználható;
- headless és AI-vs-AI tesztelés megmarad;
- a rules engine teljesen UI-független;
- a processhatár egyértelmű authority-határt ad;
- a Python tooling és a termékruntime ugyanazt a szabályimplementációt használhatja.

Kockázatok:

- process lifecycle és elárvult folyamat;
- bridge-protokoll és verzióegyeztetés;
- kapcsolatvesztés és timeout;
- Windows-csomagolás;
- két executable belső kezelése;
- antivírus vagy SmartScreen false positive;
- stdout, stderr, protokoll és emberi log elhatárolása.

### 4.2 Modell B – Godot .NET + C# authoritative rules runtime

Lehetséges forma:

- tiszta C# rules library;
- külön Godot .NET wrapper vagy kliensassembly;
- a rules library ne függjön Godot Node- vagy UI-típusoktól;
- Python továbbra is adatpipeline-, audit-, AI- és batch-tooling.

Erősségek:

- hivatalosan támogatott Godot-nyelv és buildút;
- nincs külön Python-processz és bridge a termékfutásban;
- erős statikus típusosság;
- kiforrott unit test és serialization eszközök;
- egyszerűbb lehet az egységes portable Windows-csomag;
- a Godot kliens és a runtime közös processzben futhat.

Kockázatok:

- a meglévő Python engine kontrollált portolási költsége;
- Python AI/batch és C# runtime contracteltérésének veszélye;
- Godot .NET build-, export- és runtime-függőségek;
- az engine és UI helytelen összekeverése;
- self-contained és framework-dependent csomagolás gyakorlati bizonyítása;
- Codex és emberi karbantartás C#-minőségének vizsgálata.

### 4.3 Modell C – GDScript rules runtime

Csak szűk proofként vizsgálandó első körben:

- egyetlen minimal transition;
- contract parsing és serialization;
- azonos snapshot/event output;
- headless tesztelhetőség;
- nem teljes második engine.

Erősségek:

- közvetlen Godot-integráció;
- egyszerű Godot export;
- nincs külső runtime.

Kockázatok:

- nagy szabálymotor hosszú távú karbantarthatósága;
- Python-logika duplikációja;
- AI/batch tooling és termékruntime eltérése;
- két authoritative implementáció veszélye;
- UI-node-okba szivárgó szabálylogika.

Csak akkor kapjon nagyobb scope-ot, ha az audit vagy az első két proof valódi indokot ad.

### 4.4 Modell D – Embedded Python vagy más GDExtension-nyelv

Példák:

- py4godot;
- godot-python-extension;
- GodoPy;
- régi godot-python;
- szükség esetén C++ vagy Rust GDExtension.

Jelenlegi minősítés:

- kutatási és tanulási irány;
- több megoldás experimental vagy WIP;
- Windows packaging, ABI, Godot-verzió és natív crash-kockázat külön bizonyítandó;
- nem elsődleges proof-jelölt;
- csak production-közeli bizonyíték esetén emelhető előre.

---

## 5. Kötelező tanulóprogram-audit

A helyileg letöltött tanulóprogramok a `fourth turn` nevű mappában vannak. Ez a mappa nem része automatikusan az AETERNA GitHub repositorynak.

A Codex első lépése read-only leltár:

- projekt neve és hivatalos forrása;
- helyi mappa neve;
- commit, tag vagy release-verzió;
- kód-, asset- és dependencylicenc;
- programnyelvek és fő runtime;
- Godot-, Python- és .NET-verzió;
- rules runtime és authoritative state helye;
- frontend–engine kommunikáció;
- processindítás és lifecycle;
- packaging és Windows támogatás;
- unit, integration és headless tesztek;
- clean-room módon használható architektúraminta;
- közvetlenül át nem vehető vagy kockázatos rész;
- attributionkötelezettség.

Az audit sorrendje és batchszabályai a `LEARNING_PROJECT_AUDIT_QUEUE.md` fájlban találhatók.

Másolt kód alapértelmezetten nem kerülhet az AETERNA repositoryba. Minden közvetlen átvétel külön emberi döntést igényel.

---

## 6. Közös comparison fixture

Minden proof ugyanazt a `RUNTIME_COMPARISON_FIXTURE_SPEC.md` szerinti scenario-t használja.

Kötelező jelentés:

1. canonical initial state;
2. `draw_card` player 1;
3. stale `expected_state_version` request elutasítása mutation nélkül;
4. `end_turn` player 1 → player 2;
5. `draw_card` player 2;
6. player-visible snapshot mindkét játékosnak;
7. typed event log;
8. legal action ellenőrzés;
9. canonical JSON artifactok;
10. ugyanazon futás ismétlése determinisztikai összevetéssel.

A proof nem igényli a Wellspring, Beáramlás, payment, `play_card`, combat vagy ability executor portolását.

---

## 7. Első Codex-feladat szakaszai

### Szakasz 0 – Read-only audit

- AETERNA Python engine és Godot projekt áttekintése;
- `fourth turn` helyi leltára;
- licencek és verziók ellenőrzése;
- semmilyen kódmódosítás;
- comparison-terv és pontos fájlscope.

### Szakasz 1 – Canonical comparison fixture

- a Python reference engine canonical builderéből;
- verziózott input és expected output;
- canonical JSON rendezés;
- strukturált eltérésjelentés.

### Szakasz 2 – Python sidecar proof

- minimal launcher és handshake;
- action request/response;
- snapshot és event export;
- timeout, kapcsolatvesztés és kontrollált shutdown;
- portable Windows 10+ futás;
- külön Python-telepítés nélkül.

### Szakasz 3 – Godot .NET/C# proof

- ugyanazon scenario C# rules libraryben;
- Godot UI-tól fizikailag elkülönített state és transition;
- unit tesztek;
- kompatibilis JSON-contract;
- Godot .NET wrapper;
- portable Windows 10+ export;
- self-contained vagy egyszerű prerequisite-modell.

### Szakasz 4 – Feltételes harmadik proof

GDScript, embedded Python vagy más nyelv csak akkor, ha:

- az audit konkrét előnyt vagy kockázatot jelez;
- a Python és C# proof nem ad elég döntési információt;
- a scope kicsi és összehasonlítható marad.

### Szakasz 5 – Packaging és stabilitási proof

- tiszta Windows 10+ 64-bit környezet;
- 20 egymást követő indítás és szabályos leállítás;
- nincs elárvult processz;
- offline futás;
- legalább 2 órás soak vagy gyorsított AI-vs-AI teszt;
- memória-, processz- és handle-megfigyelés;
- reprodukálható build;
- diagnosztikai logok.

### Szakasz 6 – Döntési jelentés

A jelentés tartalmazza:

- kizáró feltételek eredményét;
- súlyozott pontozást;
- bizonyítékszintet;
- mérési adatokat;
- migrációs költséget;
- ismert kockázatokat;
- A/B/C/D ajánlást;
- emberi döntési pontot.

---

## 8. Kizáró feltételek

Egy jelölt nem választható termékruntime-nak, ha az alábbiak bármelyike tartósan fennáll és a proof során nem javítható.

### GATE-01 – Portable indítás

- Nem indítható tiszta Windows 10+ 64-bit környezetben kibontott portable csomagból.
- A játékosnak fejlesztői környezetet, package managert vagy több programot kézzel kell kezelnie.

### GATE-02 – Authoritative state és UI-elhatárolás

- Nem biztosítható pontosan egy authoritative MatchState.
- A UI közvetlenül módosítja a state-et vagy rejtett szabálylogikát tartalmaz.

### GATE-03 – Contracthelyesség

- Nem teljesíti a közös fixture action-, response-, event-, snapshot- és version-contractját.
- Rejected action részleges state mutationt okoz.

### GATE-04 – Determinisztika és rejtett információ

- Azonos inputból nem állítható elő reprodukálható output.
- Player-facing output rejtett card ID-t, instance ID-t vagy debug-state-et szivárogtat.

### GATE-05 – Tesztelhetőség

- A szabálymotor Godot UI nélkül nem tesztelhető.
- Nincs használható unit vagy headless tesztút.

### GATE-06 – Lifecycle és stabilitás

- Normál bezárás után elárvult saját processz marad.
- A bridge vagy runtime hibája bizonytalan authoritative state mellett folytathatja a játékot.
- Nincs kontrollált crash-, timeout- vagy kapcsolatvesztés-kezelés.

### GATE-07 – Terjeszthetőség és licenc

- A szükséges runtime vagy dependency nem terjeszthető jogszerűen.
- A licenc- vagy attributionkötelezettség nem tisztázható.

A `not_tested` állapot nem automatikus bukás, de döntés sem hozható addig, amíg minden kizáró kapu `pass` vagy külön emberileg elfogadott `conditional_pass` eredményt nem kap.

---

## 9. Súlyozott összehasonlítási mátrix

A kizáró kapuk teljesítése után minden jelöltet 0–5 skálán kell pontozni.

| Terület | Súly | Fő kérdés |
|---|---:|---|
| Stabilitás és lifecycle | 25% | Megbízhatóan indul, fut, hibázik és áll le? |
| Portable futás és függőségek | 20% | Egyszerűen átadható-e Windows 10+ 64-bit csomagként? |
| Szabályhelyesség, determinisztika és visibility | 20% | Hűen és biztonságosan teljesíti-e a contractokat? |
| Karbantarthatóság és tesztelhetőség | 15% | Biztonságosan bővíthető, reviewzható és tesztelhető-e? |
| Godot-integráció | 10% | Tiszta és stabil-e a kliens–engine határ? |
| AI, batch, replay és tooling | 5% | Megtartható-e a hosszú távú tesztelési és elemzési képesség? |
| Teljesítmény és csomagméret | 5% | Elfogadható-e a latency, memória, buildméret és indítási idő? |
| **Összesen** | **100%** |  |

### 9.1 Pontskála

| Pont | Jelentés |
|---:|---|
| 0 | Nem működik vagy a követelmény lényegét megsérti. |
| 1 | Súlyos hiányosság; csak elméleti vagy törékeny megoldás. |
| 2 | Részben működik, de jelentős kockázat vagy kézi beavatkozás marad. |
| 3 | Elfogadható proofszint, ismert és kezelhető korlátokkal. |
| 4 | Erős, ismételten bizonyított megoldás, kisebb adóssággal. |
| 5 | Kiemelkedő, stabil, reprodukálható és termékesíthető eredmény. |

Súlyozott pontszám:

`kategóriapont / 5 × kategóriasúly`

### 9.2 Bizonyítékszint

A pontszám mellett külön bizonyítékszint szükséges.

| Szint | Jelentés |
|---|---|
| E0 | Feltételezés vagy vélemény. |
| E1 | Dokumentáció vagy külső példa. |
| E2 | Helyi forrásaudit vagy reprodukált külső demo. |
| E3 | AETERNA minimal proof sikeresen fut. |
| E4 | Tiszta Windows portable, ismételt indítás és integration teszt sikeres. |
| E5 | Soak, hibainjektálás, reprodukálható build és teljes mérési csomag sikeres. |

Szabályok:

- E0–E1 bizonyítékkal egy kategória legfeljebb 2 pontot kaphat.
- E2 bizonyítékkal legfeljebb 3 pont adható.
- 4–5 pont csak AETERNA-specifikus E3–E5 proof alapján adható.
- A jelölt teljes pontszáma mellett fel kell tüntetni a legalacsonyabb kritikus bizonyítékszintet is.

---

## 10. Döntési szabályok

A mátrix döntést támogat, de nem helyettesíti az emberi mérlegelést.

### 10.1 Python megtartása

A Python sidecar marad az elsődleges ajánlás, ha:

- minden kizáró kaput teljesít;
- stabil portable csomag készíthető külön Python-telepítés nélkül;
- lifecycle- és bridge-kockázata kezelhető;
- súlyozott eredménye legfeljebb 5 ponttal marad el a legjobb jelölttől;
- más megoldás nem szüntet meg kritikus, Pythonban nem javítható kockázatot.

Ez a szabály védi a projektet a csekély előnyért fizetett nagy migrációs költségtől.

### 10.2 C#-váltás indoka

A C# authoritative runtime akkor ajánlható, ha:

- minden kizáró kaput teljesít;
- legalább E4 portable és integration bizonyítéka van;
- a Python sidecarhoz képest legalább 10 súlyozott pont előnyt ér el; **vagy**
- olyan kritikus stabilitási, packaging- vagy lifecycle-kockázatot szüntet meg, amely Python sidecarral nem kezelhető elfogadhatóan;
- a contractonkénti migráció költsége és terve elfogadható;
- a Python AI-, batch- és adattoolinggal való kapcsolat fenntartható.

### 10.3 Szoros eredmény

Ha a különbség 6–9 pont:

- újabb célzott proof szükséges a különbséget okozó kategóriákban;
- nem indul automatikus migráció;
- a döntésben külön súlyt kap a migrációs költség és a hosszú távú rules-engine karbantarthatósága.

Ha a különbség 0–5 pont:

- alapértelmezésben a működő Python referencia marad;
- kivétel csak kritikus minőségi vagy termékkockázat esetén lehetséges.

### 10.4 GDScript vagy más jelölt elővétele

Harmadik runtime-proof akkor indokolt, ha:

- sem Python, sem C# nem teljesíti valamelyik kizáró kaput;
- a két fő jelölt eredménye nem ad döntést;
- a tanulóprogram-audit konkrét, erős és reprodukálható alternatívát talál;
- a proof scope kicsi marad.

### 10.5 Nincs megfelelő győztes

Ha egyik jelölt sem teljesíti a kapukat:

- a Python referenciaengine megmarad;
- jelentős gameplay-bővítés továbbra sem indul;
- csak a bukott kapukra célzott új proof készül;
- nem választunk runtime-ot pusztán azért, hogy a döntési kaput formálisan lezárjuk.

### 10.6 Holtverseny

Holtversenynél előnyben részesítendő:

1. kevesebb runtime- és processzfüggőség;
2. kisebb migrációs kockázat;
3. erősebb automatizált tesztelés;
4. tisztább UI–engine elhatárolás;
5. egyszerűbb portable build;
6. jobb hosszú távú emberi és Codex-karbantarthatóság.

---

## 11. A döntés lehetséges eredményei

### Eredmény A – Python sidecar marad authoritative runtime

- Python engine-fejlesztés folytatása;
- Godot bridge és packaging termékesítése;
- a játékos továbbra is egyetlen fő indítót használ;
- C# csak kliens- vagy adapteroldali szerepben jelenhet meg, ha szükséges.

### Eredmény B – C# lesz az authoritative termékruntime

- Python referenciaimplementáció és tesztorákulum marad;
- kontrollált, contractonkénti C# migráció;
- Python továbbra is adatpipeline, AI/batch, audit és balansztooling;
- nem készül egyetlen nagy, ellenőrizhetetlen automatikus port.

### Eredmény C – Tiszta, indokolt hibrid modell

Csak akkor fogadható el, ha:

- egyértelmű az authoritative state;
- nincs duplikált legalitásszámítás;
- a réteghatár verziózott contracttal védett;
- a tesztelés bizonyítja az egyezést;
- a portable packaging kezelhető.

### Eredmény D – GDScript vagy más runtime bizonyul a legjobbnak

Csak célzott, azonos fixture-ön futó és termékkövetelményeket teljesítő bizonyíték után fogadható el. A Python tooling- és referencia-réteg ekkor is megmaradhat.

---

## 12. Dokumentációs munkarend a döntési kapu alatt

A dokumentumszaporodás elkerülése érdekében:

- új alfeladathoz alapértelmezetten nem készül új dokumentum;
- új eredmény a természetes aktív fődokumentumba kerüljön;
- külön fájl csak önálló, tartós és más dokumentumba nem illeszthető canonical témának készülhet;
- átmeneti terv vagy eredmény lehet szakasz, táblázat vagy checkpoint-bejegyzés;
- történeti dokumentum nem törlendő audit nélkül;
- azonos szerepű párhuzamos current dokumentum nem hozható létre.

A jelenlegi döntési mátrix ezért ebbe a fájlba került, nem külön dokumentumba.

---

## 13. Átmeneti munkarend Codex nélkül

Folytatható:

- dokumentációs konszolidáció meglévő főfájlokban;
- `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` triázsa;
- ability rendszer dokumentációs auditja;
- contract-specifikáció konszolidációja;
- `fourth turn` auditjának előkészítése;
- licenc- és forrásjegyzék;
- szabályforrásból megválaszolható engine-kérdések ellenőrzése.

Nem indul:

- teljes C# engine-port;
- teljes GDScript engine;
- új nagy Python gameplay-réteg;
- végleges bridge-implementáció;
- nyelvi döntés pusztán vélemény alapján.

---

## 14. Jelenlegi rövid státusz

**Jelenlegi működő referencia:** Python minimal rules engine.  
**Helyi tanulóprogram-mappa:** `fourth turn`.  
**Következő Codex-prioritás:** read-only audit, canonical fixture, Python sidecar proof és Godot .NET/C# proof.  
**Kötelező fő jelöltek:** Python sidecar és Godot .NET/C#.  
**Feltételes proof:** GDScript, embedded Python vagy más célzott runtime.  
**Döntési mérce:** kizáró kapuk + 100 pontos súlyozás + bizonyítékszintek.  
**Wellspring integration:** kész következő gameplay-feladat, de a nyelvi döntési kapu mögé sorolva.  
**Dokumentációs szabály:** meglévő fődokumentum frissítése az alapértelmezés; új fájl csak indokolt canonical témához.