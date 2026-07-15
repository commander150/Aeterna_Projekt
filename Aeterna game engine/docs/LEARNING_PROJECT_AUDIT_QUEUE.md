# AETERNA Game Engine – Tanulóprogram-audit prioritási sor

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív auditqueue és Codex előtti vizsgálati sorrend  
**Helyi auditgyökér:** `fourth turn`  
**Kapcsolódó döntési kapu:** `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

Ez a dokumentum nem választ runtime-nyelvet és nem minősít előre győztes technológiát.

Feladata:

- meghatározni a helyileg letöltött és az online referencia-projektek vizsgálati sorrendjét;
- előre venni a portable Windows-runtime döntést közvetlenül befolyásoló mintákat;
- elkerülni a túl sok projekt egyidejű, felületes feldolgozását;
- elkülöníteni a runtime-, engine-, UI-, AI-, packaging- és licencszempontokat;
- minden batch után lehetővé tenni a prioritás újraértékelését.

Kapcsolódó aktív fájlok:

- audit-sablon: `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`;
- termékkövetelmény: `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`;
- döntési és pontozási szabály: `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- közös scenario: `RUNTIME_COMPARISON_FIXTURE_SPEC.md`.

---

## 1. Helyi auditgyökér állapota

A felhasználó a korábban említett tanulóprogramokat a `fourth turn` nevű helyi mappába töltötte le.

Jelenlegi státusz:

- a mappa nem része automatikusan az AETERNA GitHub repositorynak;
- a mappanév ismert, a pontos abszolút elérési út még helyileg azonosítandó;
- a mappa tartalma még nem tekinthető leltározottnak vagy licencellenőrzöttnek;
- nem feltételezhető, hogy minden alkönyvtár teljes repository vagy azonos verziójú forrás;
- ZIP, kibontott repository, build-output, dokumentációmásolat és saját jegyzet külön kategória;
- Codex először kizárólag read-only Batch 0 leltárt készít.

A helyi mappa GitHubba másolása nem szükséges és licencbiztonsági okból alapértelmezetten tilos.

---

## 2. Általános auditelvek

1. Minden audit read-only leltárral kezdődjön.
2. A külső projektek ne kerüljenek automatikusan az AETERNA repositoryba.
3. A kód, asset, dokumentáció és dependency licence külön ellenőrzendő.
4. A konkrét implementáció és a clean-room módon újraalkotható architektúraminta külön kategória.
5. Egy batch egyszerre kevés, közvetlenül összehasonlítható projektet tartalmazzon.
6. Alacsonyabb prioritású batch nem indul automatikusan, ha a magasabb prioritású már elegendő bizonyítékot adott.
7. Minden batch végén `continue`, `defer`, `stop` vagy `expand` döntés készüljön.
8. Az audit nem írhatja át automatikusan az AETERNA engine-kódját.
9. Közvetlen kódátvételhez külön emberi jóváhagyás kell.
10. A végleges runtime-döntés emberi jóváhagyást igényel.
11. Bizonyított tény, következtetés és javaslat külön mezőben szerepeljen.
12. Bizonytalan vagy hiányzó licenc esetén semmilyen kód vagy asset nem vehető át.

---

## 3. Batch 0 – `fourth turn` helyi programleltár

**Prioritás:** kötelező első Codex-lépés  
**Mód:** read-only fájl- és projektazonosítás

### 3.1 Cél

- a `fourth turn` pontos helyi elérési útjának azonosítása;
- minden közvetlen alkönyvtár és önálló projekt felismerése;
- teljes repository, ZIP-kibontás, build-output, dokumentációmásolat és jegyzet elkülönítése;
- repository URL, commit, tag vagy release-verzió azonosítása;
- fő technológia és várható auditbatch megjelölése;
- minden projekthez ideiglenes `Audit_ID` rendelése.

### 3.2 Kötelező kimenet

| Audit_ID | Projekt | Helyi mappa | Forrás | Verzió | Fő technológia | Licenc elérhető | Következő batch |
|---|---|---|---|---|---|---|---|
| `LP-...` |  |  |  |  |  |  |  |

### 3.3 Ebben a batchben tilos

- mély architektúra- vagy kódelemzés;
- build vagy futtatás;
- dependencytelepítés;
- fájlmódosítás;
- kódmásolás;
- projekt GitHubba helyezése;
- licencfeltételezés pusztán repositorynév alapján.

### 3.4 Stop feltétel

Nem indulhat mély audit, amíg legalább a vizsgálandó projekt neve, forrása, verziója és licence nincs azonosítva vagy `unknown` státusszal explicit rögzítve.

---

## 4. Batch 1 – Közvetlen runtime- és integrációs bizonyítékok

**Prioritás:** legmagasabb mély auditprioritás

Ez a batch közvetlenül azt vizsgálja, hogy a Python sidecar vagy a Godot .NET/C# modell képes-e teljesíteni az AETERNA portable Windows-követelményeit.

### 4.1 Godot RL Agents és plugin

Jelöltek:

- `edbeeching/godot_rl_agents`;
- `edbeeching/godot_rl_agents_plugin`.

Fő vizsgálati ok:

- Godot és Python külön folyamatban működik;
- exportált Godot-program és Python közötti kommunikáció;
- localhost TCP és strukturált JSON;
- handshake, action, observation, reset és shutdown;
- process lifecycle és hibaágak;
- csomagolt vagy exportált futás.

AETERNA-kérdés:

> Mely részek alkalmazhatók saját Python sidecar + Godot action request/response bridge-ként anélkül, hogy külső kódot másolnánk?

### 4.2 Hivatalos Godot C# / Mono minták

Elsődleges forrás:

- `godotengine/godot-demo-projects` `mono/` példái;
- hivatalos Godot .NET dokumentáció és exportút.

Fő vizsgálati ok:

- hivatalosan támogatott Godot C# buildmodell;
- project/solution szerkezet;
- C# script és scene kapcsolata;
- Windows export;
- szükséges .NET- és Godot-verziók;
- portable futás, self-contained vagy prerequisite-modell.

AETERNA-kérdés:

> Mi a legkisebb hivatalosan támogatott Godot .NET build, amely tiszta Windows 10+ 64-bit környezetben portable módon elindítható?

### 4.3 `ch200c/Durak.Godot`

Fő vizsgálati ok:

- Godot .NET projekt;
- külön `Durak.Gameplay` C# library;
- a Godot főprojekt project reference-szel fogyasztja a gameplay libraryt;
- külön unit és functional test projektek;
- kártyajáték-domain;
- UI és gameplay fizikai elválasztásának példája.

Kiemelt auditpontok:

- a gameplay library Godot nélkül tesztelhető-e;
- mennyi Godot-típus szivárog a rules librarybe;
- state, command/action és event modell;
- serialization;
- unit és functional testek;
- export és dependencykezelés;
- kód- és assetlicencek különbsége.

Licencmegjegyzés:

- a repository MIT-szöveget tartalmaz, de a copyright-helyőrző kitöltetlennek tűnik;
- az assetekhez külön licencek tartozhatnak;
- ezért elsődlegesen clean-room architektúramintaként vizsgálandó.

### 4.4 Batch 1 kötelező kimenet

Minden projekthez:

- authority diagram;
- process diagram;
- build- és runtime dependencylista;
- portable Windows-relevancia;
- tesztelhetőségi értékelés;
- licenc- és attributionjegyzet;
- clean-room módon használható minta;
- ismert kockázatok;
- javaslat a Python sidecar és C# proof scope-jára;
- kapcsolódó kizáró kapuk és bizonyítékszintek.

### 4.5 Batch 1 döntési pont

Felülvizsgálandó:

- szükséges-e további C# kártyajáték-projekt;
- a Python sidecar első transportja JSONL pipe vagy TCP legyen-e;
- a Godot .NET proofhoz elég-e tiszta library + minimal Godot wrapper;
- indokolt-e minimal GDScript proof;
- van-e a `fourth turn` mappában előre sorolandó másik projekt.

---

## 5. Batch 2 – További Godot .NET/C# kártya- és frameworkminták

**Prioritás:** magas, de csak Batch 1 után

Lehetséges jelöltek:

- `Ggross98/Godot-CardPileFramework`;
- `TheSchlote/Godot-4-Card-Game-CSharp`;
- a `fourth turn` között talált további Godot 4 + C# kártyajátékok;
- külön rules/gameplay assemblyt, unit tesztet vagy adatvezérelt modellt használó projektek.

Az archivált repository tanulási célra használható, de termékalapként az elavult Godot-verzió és karbantartási állapot jelentős kockázat.

Kiemelt kérdések:

- Godot node-független rules layer;
- dependency injection vagy service boundary;
- command/action modell;
- save és serialization;
- headless tesztelés;
- card definition és card instance szétválasztása;
- export és packaging.

---

## 6. Batch 3 – GDScript rules- és kártyajáték-minták

**Prioritás:** feltételes

Mély scope csak akkor indokolt, ha:

- a `fourth turn` mappában erős, jól tesztelt GDScript rules engine található;
- a Python sidecar vagy C# proof fontos követelményben gyengén teljesít;
- minimal GDScript proof valódi döntési információt ad.

Előnyben részesítendő:

- Godot 4;
- UI-tól fizikailag elkülönített rules layer;
- headless vagy unit teszt;
- adatvezérelt kártyamodell;
- legal action, command és event szerkezet;
- exportált Windows-build bizonyíték;
- aktív vagy karbantartott repository.

Nem elegendő önmagában:

- drag-and-drop vagy látványos kártya-UI;
- szabálylogika közvetlenül Control/Node callbackekben;
- tutorialszintű demo;
- teszt és licenc nélküli repository.

---

## 7. Batch 4 – Embedded Python és community bindingok

**Prioritás:** kutatási, nem első termékproof

Jelöltek:

- `niklas2902/py4godot`;
- `niklas2902/py4godot-examples`;
- `maiself/godot-python-extension`;
- `godopy/godopy`;
- `touilleMan/godot-python`.

Vizsgálandó:

- aktív fejlesztési állapot;
- támogatott Godot- és Python-verzió;
- Windows build;
- embedded vagy rendszer-Python;
- export és dependencycsomagolás;
- editor-integráció;
- natív crash-, ABI- és community-karbantartási kockázat;
- saját dokumentáció szerinti experimental vagy production státusz.

Csak production-közeli Windows packaging és stabilitási bizonyíték emelheti elsődleges jelöltté.

---

## 8. Batch 5 – Nem Godot-specifikus rules engine és AI minták

**Prioritás:** runtime-döntéshez közvetett, engine-tervezéshez hosszú távon fontos

Lehetséges jelöltek:

- RLCard;
- boardgame.io;
- XMage;
- Duelyst és kapcsolódó nyílt forrású maradványok;
- más deterministic card/board game engine-ek.

Vizsgálandó:

- authoritative state;
- legal action generation;
- command/action resolver;
- event sourcing és replay;
- hidden information;
- deterministic simulation;
- AI environment adapter;
- batch futtatás;
- differential és property testing;
- kártyaképesség-modulok.

Ez a batch nem dönt közvetlenül a Python–C#–GDScript kérdésben.

---

## 9. Batch 6 – AETERNA packaging és stabilitási proof

**Prioritás:** a minimal runtime proofok után

Kötelező mérés:

- Windows 10+ 64-bit portable csomag;
- egyértelmű fő executable;
- adminjog nélküli futás;
- szükséges prerequisite-ek száma;
- self-contained .NET és csomagolt Python összevetése;
- elárvult processzek;
- log- és mentési könyvtár;
- SmartScreen- és antivírus-tapasztalat;
- 20 indítás és szabályos leállítás;
- legalább 2 órás soak vagy gyorsított AI-vs-AI futás;
- offline próba;
- reprodukálható build.

Ez már az AETERNA saját proofcsomagjainak mérési szakasza.

---

## 10. Auditbatch-kimenetek egységes formája

Minden lezárt batch adjon:

1. projektenként kitöltött auditlapot;
2. összesített comparison táblát;
3. licenc- és attributionlistát;
4. bizonyított tények és következtetések különválasztását;
5. használható clean-room mintákat;
6. tiltott vagy kockázatos közvetlen átvételeket;
7. kapcsolódó runtime-kapuk és bizonyítékszintek eredményét;
8. következő batch-ajánlást;
9. `continue`, `defer`, `stop` vagy `expand` döntést.

Az audit eredménye alapértelmezetten meglévő aktív dokumentumba, táblázatba vagy checkpointba kerüljön. Új dokumentum csak önálló, tartós canonical téma esetén készülhet.

---

## 11. Jelenlegi végrehajtási sorrend

1. Batch 0 – `fourth turn` helyi leltár.
2. Batch 1.1 – Godot RL Agents és plugin.
3. Batch 1.2 – hivatalos Godot C# / Mono build- és exportminta.
4. Batch 1.3 – Durak.Godot rules-library és tesztelési szerkezet.
5. Köztes döntési pont.
6. Batch 2 – további C# kártyajáték/framework csak szükség szerint.
7. Batch 3 – GDScript proof csak szükség szerint.
8. Batch 4 – embedded Python kutatás, ha indokolt.
9. Batch 5 – rules engine és AI minták.
10. Batch 6 – AETERNA saját packaging és stabilitási proofjai.

A sorrend nem merev. Súlyos licenc-, stabilitási vagy csomagolási kockázat esetén a fontosabb döntési pont előre vehető.