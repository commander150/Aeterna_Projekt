# AETERNA Game Engine – Tanulóprogram-audit prioritási sor

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív auditqueue és Codex előtti vizsgálati sorrend  
**Kapcsolódó döntési kapu:** `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

Ez a dokumentum nem választ runtime-nyelvet és nem minősít előre győztes technológiát.

Feladata:

- meghatározni, milyen sorrendben vizsgáljuk a helyileg letöltött és az online referencia-projekteket;
- előre venni azokat a mintákat, amelyek közvetlenül befolyásolják az AETERNA portable Windows-runtime döntését;
- elkerülni, hogy a Codex véletlenszerű vagy túl nagy projektmennyiséget próbáljon egyszerre feldolgozni;
- elkülöníteni a futási, engine-, UI-, AI- és licencszempontból eltérő tanulóanyagokat;
- minden batch után lehetővé tenni a prioritás újraértékelését.

Aktív audit-sablon:

- `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`

Termékkövetelmény-mérce:

- `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`

---

## 1. Alapelvek

1. Minden audit read-only leltárral kezdődjön.
2. A helyi tanulóprogramok ne kerüljenek automatikusan az AETERNA GitHub repositoryba.
3. A kód, asset, dokumentáció és dependency licence külön ellenőrzendő.
4. A konkrét implementáció és a clean-room módon újraalkotható architektúraminta külön kategória.
5. Egy batch egyszerre kevés, közvetlenül összehasonlítható projektet tartalmazzon.
6. Alacsonyabb prioritású batch nem kezdődhet el automatikusan, ha a magasabb prioritású batch már elegendő döntési bizonyítékot adott.
7. Minden batch végén külön `continue`, `defer`, `stop` vagy `expand` döntés készüljön.
8. Az audit nem írhatja át automatikusan az AETERNA engine-kódját.
9. A végleges runtime-döntés emberi jóváhagyást igényel.

---

## 2. Batch 0 – Helyi programleltár

**Prioritás:** kötelező első lépés  
**Mód:** csak read-only fájl- és projektazonosítás

Cél:

- megállapítani, pontosan mely tanulóprogramok vannak helyileg letöltve;
- elkülöníteni a teljes repositorykat, ZIP-kibontásokat, build-outputokat, dokumentációmásolatokat és saját jegyzeteket;
- rögzíteni a helyi mappanevet anélkül, hogy a fájlok az AETERNA repositoryba kerülnének;
- azonosítani a repository URL-t, commitot, taget vagy release-verziót;
- minden projekthez ideiglenes `Audit_ID` rendelése.

Kötelező kimenet:

| Audit_ID | Projekt | Helyi mappa | Forrás | Verzió | Fő technológia | Licenc elérhető | Következő batch |
|---|---|---|---|---|---|---|---|
| `LP-...` |  |  |  |  |  |  |  |

Ebben a batchben még nem történik mély architektúra- vagy kódelemzés.

### Batch 0 stop feltétel

Nem indulhat mély audit, amíg legalább a vizsgálandó projekt neve, forrása, verziója és licence nincs azonosítva.

---

## 3. Batch 1 – Közvetlen runtime- és integrációs bizonyítékok

**Prioritás:** legmagasabb mély auditprioritás

Ez a batch közvetlenül azt vizsgálja, hogy a Python sidecar vagy a Godot .NET/C# modell képes-e teljesíteni az AETERNA portable Windows-követelményeit.

### 3.1 Godot RL Agents

Jelöltek:

- `edbeeching/godot_rl_agents`
- `edbeeching/godot_rl_agents_plugin`

Fő vizsgálati ok:

- Godot és Python külön folyamatban működik;
- Python indít vagy vezérel exportált Godot-programot;
- localhost TCP és strukturált JSON-kommunikáció;
- handshake, action, observation, reset és shutdown minta;
- process lifecycle és hibaágak;
- exportált programmal működő tanulási környezet.

AETERNA-kérdés:

> Mely részek alkalmazhatók tiszta, saját Python sidecar + Godot action request/response bridge-ként?

### 3.2 Hivatalos Godot C# / Mono minták

Elsődleges forrás:

- `godotengine/godot-demo-projects` `mono/` példái;
- hivatalos Godot .NET dokumentáció és exportút.

Fő vizsgálati ok:

- hivatalosan támogatott Godot C# buildmodell;
- project/solution szerkezet;
- C# script és Godot scene kapcsolat;
- Windows export alapja;
- szükséges .NET- és Godot-verziók;
- portable futás és prerequisite-ek.

AETERNA-kérdés:

> Mi a legkisebb hivatalosan támogatott Godot .NET build, amely tiszta Windows 10+ környezetben portable módon elindítható?

### 3.3 `ch200c/Durak.Godot`

Fő vizsgálati ok:

- Godot .NET projekt;
- külön `Durak.Gameplay` C# library;
- a Godot főprojekt project reference-szel fogyasztja a gameplay libraryt;
- külön unit és functional test projektek;
- card game domain;
- UI és gameplay fizikai elválasztásának közvetlen példája.

Kiemelt auditpontok:

- a gameplay library Godot nélkül tesztelhető-e;
- mennyi Godot-típus szivárog a rules librarybe;
- state és action modell;
- serialization;
- unit/functional testek felépítése;
- export- és dependencykezelés;
- licenc- és assetkülönbségek.

Megjegyzés:

- a repository fő licence MIT-szöveg, de a copyright-helyőrző kitöltetlennek tűnik;
- az assetekhez külön licencek is tartozhatnak;
- emiatt közvetlen kódátvétel helyett elsődlegesen architektúramintaként vizsgálandó.

### Batch 1 elfogadási kimenet

Minden projekthez:

- authority diagram;
- process diagram;
- build és runtime dependency lista;
- portable Windows-relevancia;
- tesztelhetőségi értékelés;
- licenc- és attributionjegyzet;
- AETERNA számára clean-room módon használható minta;
- ismert kockázatok;
- javaslat a Python sidecar és C# proof scope-jára.

### Batch 1 döntési pont

A Batch 1 után felül kell vizsgálni:

- szükséges-e további C# kártyajáték-projekt;
- a Python sidecar proof első transportja JSONL pipe vagy TCP legyen-e;
- a Godot .NET proofhoz elég-e tiszta library + minimal Godot wrapper;
- indokolt-e már ekkor minimal GDScript proof.

---

## 4. Batch 2 – További Godot .NET/C# kártya- és frameworkminták

**Prioritás:** magas, de csak Batch 1 után

Lehetséges jelöltek:

- `Ggross98/Godot-CardPileFramework`;
- `TheSchlote/Godot-4-Card-Game-CSharp`;
- a helyi tanulóprogramok között talált további Godot 4 + C# kártyajátékok;
- olyan projektek, amelyek külön rules/gameplay assemblyt, unit tesztet vagy adatvezérelt kártyamodellt használnak.

Megjegyzés:

- az archivált repository önmagában nem kizáró ok tanulási célra;
- aktív termékalapnak azonban az archiváltság és elavult Godot-verzió jelentős kockázat;
- a batch célja nem a projekt átvétele, hanem a szerkezeti minták összevetése.

Kiemelt kérdések:

- Godot node-független rules layer;
- dependency injection vagy service boundary;
- command/action modell;
- save/serialization;
- headless tesztelés;
- card definition és card instance szétválasztása;
- package/export tapasztalat.

---

## 5. Batch 3 – GDScript rules- és kártyajáték-minták

**Prioritás:** feltételes

Csak akkor kapjon mély scope-ot, ha:

- a helyi tanulóprogramok között erős, jól tesztelt GDScript rules engine található;
- a Python sidecar és C# proof valamely fontos követelményben gyengén teljesít;
- vagy egy minimal GDScript proof valódi döntési információt ad.

Előnyben részesítendő projekt:

- Godot 4;
- szabálylogika fizikailag elkülönül a scene/UI rétegtől;
- headless vagy unit tesztelhető;
- adatvezérelt kártyamodell;
- legal action / command / event szerkezet;
- exportált Windows-build bizonyíték;
- aktív vagy karbantartott repository.

Nem elegendő önmagában:

- látványos kártyahúzás vagy drag-and-drop UI;
- szabálylogika közvetlenül Control/Node callbackekben;
- csak tutorialszintű demo;
- teszt és licenc nélküli repository.

---

## 6. Batch 4 – Embedded Python és community bindingok

**Prioritás:** kutatási, nem első termékproof

Jelöltek:

- `niklas2902/py4godot`;
- `niklas2902/py4godot-examples`;
- `maiself/godot-python-extension`;
- `godopy/godopy`;
- `touilleMan/godot-python`.

Vizsgálandó:

- aktív fejlesztési állapot;
- támogatott Godot-verzió;
- támogatott Python-verzió;
- Windows build;
- embedded vagy rendszer-Python;
- export és dependencycsomagolás;
- editor-integráció;
- natív crash- és ABI-kockázat;
- community karbantartási kockázat;
- saját README szerinti experimental/production státusz.

A batch csak akkor emelhet embedded Python modellt elsődleges proof-jelöltté, ha production-közeli Windows packaging és stabilitás bizonyítható.

---

## 7. Batch 5 – Nem Godot-specifikus rules engine és AI minták

**Prioritás:** runtime-döntéshez közvetett, engine-tervezéshez hosszú távon fontos

Lehetséges jelöltek:

- RLCard;
- boardgame.io;
- XMage;
- Duelyst és kapcsolódó nyílt forrású maradványok;
- más deterministic card/board game engine-ek.

Elsődleges vizsgálati témák:

- authoritative state;
- legal action generation;
- command/action resolver;
- event sourcing vagy replay;
- hidden information;
- deterministic simulation;
- AI environment adapter;
- batch futtatás;
- differential és property testing;
- kártyaképesség-modulok.

Ez a batch nem dönt közvetlenül Godot–Python–C# kérdésben, de a végleges engine-contractokat javíthatja.

---

## 8. Batch 6 – Packaging, kiadási és stabilitási minták

**Prioritás:** a minimal runtime proofok elkészülte után

Cél:

- Windows 10+ 64-bit portable csomag;
- fő executable;
- adminjog nélküli futás;
- szükséges prerequisite-ek felismerése;
- self-contained .NET és csomagolt Python összevetése;
- elárvult processz ellenőrzése;
- log- és mentési könyvtár;
- SmartScreen/antivírus tapasztalat;
- 20 indítás/leállítás;
- legalább 2 órás soak futás;
- offline próba;
- reprodukálható build.

Ez a batch már nem pusztán forráskód-audit, hanem az AETERNA saját proofcsomagjainak mérési szakasza.

---

## 9. Auditbatch-kimenetek egységes formája

Minden lezárt batch adjon:

1. projektenként kitöltött auditlapot;
2. összesített comparison táblát;
3. licenc- és attributionlistát;
4. bizonyított tények és következtetések különválasztását;
5. AETERNA számára használható clean-room mintákat;
6. tiltott vagy kockázatos közvetlen átvételeket;
7. következő batch-ajánlást;
8. `continue`, `defer`, `stop` vagy `expand` döntést.

---

## 10. Jelenlegi ajánlott végrehajtási sorrend

1. Batch 0 – helyi leltár.
2. Batch 1.1 – Godot RL Agents és plugin.
3. Batch 1.2 – hivatalos Godot C# / Mono build- és exportminta.
4. Batch 1.3 – Durak.Godot rules-library és tesztelési szerkezet.
5. Köztes döntési pont.
6. Batch 2 – további C# kártyajáték/framework csak szükség szerint.
7. Batch 3 – GDScript proof csak szükség szerint.
8. Batch 4 – embedded Python kutatás, ha indokolt.
9. Batch 5 – rules engine és AI minták.
10. Batch 6 – AETERNA saját packaging és stabilitási proofjai.

A sorrend nem merev. Ha egy magasabb prioritású batch során súlyos licenc-, stabilitási vagy csomagolási kockázat merül fel, a következő feladatot ennek megfelelően előre kell venni.
