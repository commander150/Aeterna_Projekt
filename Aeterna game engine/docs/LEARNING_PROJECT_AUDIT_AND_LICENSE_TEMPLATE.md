# AETERNA Game Engine – Tanulóprogram-audit és licencleltár sablon

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív, Codex előtti audit- és licencleltár-sablon  
**Kapcsolódó prioritás:** runtime engine language decision gate / P1 tanulóprogram-audit

Ez a dokumentum a helyileg letöltött, de az AETERNA GitHub repositoryba licencbiztonsági okból fel nem töltött tanulóprogramok egységes vizsgálati sablonja.

A sablon célja:

- projektenként azonos kérdések megválaszolása;
- a technológiai és architekturális minták bizonyíték-alapú összehasonlítása;
- a licenc- és attributionkötelezettségek elkülönített nyilvántartása;
- a közvetlen kódmásolás és a clean-room architektúraminta szétválasztása;
- a Python, C#, GDScript, C++, Rust vagy más technológiák tényleges szerepének azonosítása;
- a portable Windows-futtatás szempontjából használható minták felismerése.

---

## 1. Kötelező auditmunkarend

Minden projekt vizsgálatánál:

1. először read-only leltár készüljön;
2. a vizsgált projektben ne történjen módosítás;
3. az AETERNA repositoryba ne kerüljön automatikusan külső kód, asset vagy dokumentum;
4. minden tényhez konkrét fájl-, dokumentáció-, commit-, tag- vagy release-bizonyíték tartozzon;
5. vélemény és bizonyított tény külön mezőben szerepeljen;
6. a kód licence és az assetek licence külön vizsgálandó;
7. licenc hiányában vagy bizonytalanság esetén a projektből semmi ne legyen átvéve;
8. architektúraminta clean-room módon újraalkotható lehet, de a konkrét implementáció nem másolható automatikusan;
9. minden közvetlen kódátvételhez külön emberi jóváhagyás kell;
10. az audit ne döntsön önállóan az AETERNA végleges runtime-járól.

---

## 2. Projekttörzsadatok

### Projektazonosító

- **Audit_ID:**
- **Projekt neve:**
- **Repository / hivatalos forrás:**
- **Helyi mappa neve:**
- **Helyi mappa abszolút vagy projektfüggetlen elérési helye:**
- **Audit dátuma:**
- **Auditáló eszköz / személy:**
- **Vizsgálat típusa:** `read_only`

### Vizsgált verzió

- **Commit SHA:**
- **Tag / release:**
- **Branch:**
- **Utolsó releváns commit dátuma:**
- **Projekt állapota:** `active` / `maintenance` / `experimental` / `archived` / `unknown`
- **Vizsgált Godot-verzió:**
- **Vizsgált Python-verzió:**
- **Vizsgált .NET-verzió:**
- **Egyéb fő verziók:**

### Forrásbizonyíték

- README:
- hivatalos dokumentáció:
- buildleírás:
- releaseoldal:
- licence fájl:
- függőségmanifest:
- CI-konfiguráció:
- példaprojekt vagy demo:

---

## 3. Licenc- és attributionleltár

### 3.1 Fő programkód

- **Licenc neve:**
- **SPDX-azonosító, ha van:**
- **LICENSE fájl helye:**
- **Copyright jogosult:**
- **Kereskedelmi használat engedélyezett:** `igen` / `nem` / `nem tisztázott`
- **Módosítás engedélyezett:**
- **Terjesztés engedélyezett:**
- **Forrásközlési kötelezettség:**
- **Attributionkötelezettség:**
- **Notice vagy licencszöveg megőrzendő:**
- **Copyleft vagy továbbfertőző kötelezettség:**
- **Szabadalmi záradék:**
- **Védjegy- vagy névhasználati korlát:**
- **Licenckockázat:** `low` / `medium` / `high` / `unknown`

### 3.2 Assetek és külön komponensek

Minden eltérő licencű komponens külön sor:

| Komponens / asset | Forrás | Licenc | Attribution | Terjeszthető | AETERNA-kockázat |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

Vizsgálandó például:

- grafika;
- hang és zene;
- font;
- modell;
- ikon;
- logó;
- demo asset;
- harmadik féltől származó plugin;
- beágyazott runtime;
- NuGet-, pip-, Cargo- vagy más package.

### 3.3 Függőségek

| Függőség | Verzió | Licenc | Runtime/build | Kötelező/opcionális | Terjesztési megjegyzés |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

### 3.4 Licencdöntés

- **Csak tanulmányozható:**
- **Clean-room minta használható:**
- **Közvetlen kódátvétel elvileg lehetséges:**
- **Közvetlen kódátvétel tiltott vagy kerülendő:**
- **Emberi/jogi ellenőrzés szükséges:**
- **AETERNA repositoryba jelenleg bemásolható:** `nem`, alapértelmezés szerint
- **Indoklás:**

---

## 4. Technológiai leltár

### 4.1 Nyelvek

| Nyelv | Szerep | Kódarány vagy jelentőség | Runtime/build | Megjegyzés |
|---|---|---|---|---|
| Python |  |  |  |  |
| C# |  |  |  |  |
| GDScript |  |  |  |  |
| C/C++ |  |  |  |  |
| Rust |  |  |  |  |
| Más |  |  |  |  |

### 4.2 Engine és framework

- **Godot használata:**
- **Godot-verzió:**
- **Godot standard vagy .NET kiadás:**
- **GDExtension:**
- **Más game engine:**
- **Web/framework/service komponens:**
- **Headless futtatás:**
- **Editorfüggés:**

### 4.3 Runtime-modell

Jelöld a tényleges modellt:

- [ ] egyetlen Godot-folyamat;
- [ ] Godot + Python sidecar;
- [ ] Godot .NET + C#;
- [ ] Godot + GDExtension;
- [ ] külön kliens és service;
- [ ] embedded Python;
- [ ] csak Python headless engine;
- [ ] más modell.

Részletezés:

- ki indít kit;
- mi indul először;
- hogyan történik a handshake;
- hogyan történik a leállítás;
- hogyan kezelik a crash-t;
- maradhat-e orphan process;
- hol található az authoritative state;
- van-e több párhuzamos state;
- van-e explicit state version;
- van-e action request/response határ.

---

## 5. Rules engine és authority

### 5.1 Authoritative state

- **Authoritative MatchState helye:**
- **State tulajdonos process vagy modul:**
- **A frontend közvetlenül módosít state-et:**
- **Legal actiont ki számít:**
- **Actiont ki validál:**
- **Transitiont ki hajt végre:**
- **Rejected action mutálhat state-et:**
- **Van atomikus mutation:**
- **Van state-version guard:**
- **Van replay vagy event sourcing:**

### 5.2 Szabálylogika elhelyezése

- rules kernel;
- UI script;
- scene node;
- service;
- library;
- plugin;
- adatvezérelt ability rendszer;
- hardcoded card logic;
- scriptelt effectmodul;
- más.

### 5.3 Hidden information

- saját kéz és ellenfélkéz szétválasztása;
- player-visible snapshot;
- debug snapshot;
- fair AI nézet;
- spectator/replay nézet;
- eventek visibility-szűrése;
- rejtett objektumok azonosítóinak védelme.

### 5.4 AETERNA-illeszkedés

Értékelendő:

- contract-first modellhez illeszthető;
- UI-tól függetlenül tesztelhető;
- determinisztikus;
- AI-vs-AI kompatibilis;
- több száz kártyaképességhez skálázható;
- Domain/Wellspring/phase/priority modellhez alakítható;
- két authoritative motor fenntartását igényelné-e.

---

## 6. Frontend–engine kommunikáció

### Kommunikációs mód

- [ ] közvetlen függvényhívás;
- [ ] signal/event;
- [ ] stdin/stdout;
- [ ] JSONL;
- [ ] TCP;
- [ ] WebSocket;
- [ ] HTTP;
- [ ] native binding;
- [ ] shared library;
- [ ] fájlalapú kommunikáció;
- [ ] más.

### Protokoll

- üzenetkeretezés;
- schema verzió;
- handshake;
- request ID;
- state version;
- timeout;
- retry;
- shutdown;
- hibaválasz;
- logcsatorna;
- binary vagy JSON;
- platformfüggés.

### Megbízhatóság

- kapcsolatvesztés kezelése;
- duplikált request;
- stale action;
- részleges üzenet;
- hibás JSON;
- engine-crash;
- kliens-crash;
- újraindítás;
- state-helyreállítás.

---

## 7. Build, csomagolás és felhasználói futtatás

### 7.1 Fejlesztői build

- szükséges toolchain;
- szükséges SDK-k;
- buildparancs;
- build reprodukálhatósága;
- platformfüggő lépések;
- CI jelenléte;
- cache vagy generált kód;
- buildidő.

### 7.2 Kiadási csomag

- portable mappa készíthető;
- egyértelmű fő executable;
- szükséges külön runtime;
- runtime együtt szállítható;
- adminjog kell;
- konzolablak jelenik meg;
- külön processzek száma;
- csomag mérete;
- első indítás ideje;
- offline működés;
- antivírus false positive tapasztalat;
- Windows 10+ 64-bit működés;
- Linux-port lehetősége.

### 7.3 Külső telepítések

- külön Python kell;
- .NET runtime kell;
- .NET SDK kell;
- VC++ redistributable kell;
- más prerequisite kell;
- telepítések száma;
- automatikusan kezelhető;
- self-contained kiadás lehetséges.

### 7.4 AETERNA termékkövetelmény megfelelés

| Követelmény | Megfelel | Részben | Nem | Bizonyíték |
|---|---:|---:|---:|---|
| Windows 10+ 64-bit |  |  |  |  |
| Portable csomag |  |  |  |  |
| Adminjog nélküli futás |  |  |  |  |
| Nincs fejlesztői környezet a játékosnál |  |  |  |  |
| Kevés prerequisite |  |  |  |  |
| Egyértelmű fő indító |  |  |  |  |
| Offline játékmenet |  |  |  |  |
| Kontrollált leállítás |  |  |  |  |
| Nincs orphan process |  |  |  |  |
| Felhasználói írható mentés/log |  |  |  |  |
| UI nélküli engine-teszt |  |  |  |  |
| Determinisztikus futás |  |  |  |  |

---

## 8. Tesztelés és stabilitás

### Automatizált tesztek

- unit tesztek;
- integration tesztek;
- end-to-end tesztek;
- headless smoke;
- deterministic comparison;
- serialization round-trip;
- hidden-information teszt;
- packaging smoke;
- CI-platformok.

### Stabilitási bizonyíték

- ismételt indítás/leállítás;
- hosszabb futás;
- memória- vagy handle-szivárgás;
- crashlog;
- hibás input;
- kapcsolatvesztés;
- orphan process;
- mentési sérülés;
- offline működés.

### Mért vagy dokumentált eredmény

- tesztszám;
- sikeres platformok;
- ismert hibák;
- nyitott issue-k;
- release-stabilitás;
- benchmark, ha van;
- bizonyíték forrása.

---

## 9. Használható tanulságok

### Közvetlenül alkalmazható architektúraminta

- minta neve;
- probléma, amit megold;
- hogyan működik;
- miért releváns az AETERNA számára;
- milyen AETERNA-contracttal kapcsolható össze;
- clean-room újraalkotás javasolt formája.

### Feltételesen használható minta

- szükséges előfeltétel;
- platformkockázat;
- licenckockázat;
- karbantartási kockázat;
- szükséges proof.

### Nem javasolt minta

- ok;
- elavult technológia;
- magas duplikáció;
- hidden-information veszély;
- túl sok dependency;
- nem reprodukálható build;
- licencprobléma;
- UI-ba kevert szabálylogika.

---

## 10. AETERNA-értékelés

### Pontozás

| Terület | Súly | Pont 0–5 | Súlyozott eredmény | Indoklás |
|---|---:|---:|---:|---|
| Stabilitás és hibakezelés | 25% |  |  |  |
| Telepítés és felhasználói egyszerűség | 25% |  |  |  |
| Karbantarthatóság és tesztelhetőség | 20% |  |  |  |
| Godot-integráció | 15% |  |  |  |
| AI, batch és tooling | 10% |  |  |  |
| Nyers teljesítmény | 5% |  |  |  |

### Összesített státusz

- [ ] `high_priority_reference`
- [ ] `useful_pattern_reference`
- [ ] `comparison_candidate`
- [ ] `packaging_reference`
- [ ] `ai_reference`
- [ ] `ui_reference`
- [ ] `historical_reference`
- [ ] `not_recommended`
- [ ] `blocked_by_license`
- [ ] `insufficient_evidence`

### Ajánlás

- AETERNA runtime-jelöltként vizsgálandó:
- csak részrendszer mintájaként használható:
- clean-room proof javasolt:
- további forrás szükséges:
- Codex következő feladata:
- emberi döntési kapu:

---

## 11. Bizonyítékjegyzék

Minden lényeges megállapítás külön sorban:

| Állítás | Bizonyítékfájl / URL | Sor / szakasz | Commit / verzió | Bizonyosság |
|---|---|---|---|---|
|  |  |  |  |  |

Bizonyossági értékek:

- `confirmed_by_code`
- `confirmed_by_official_docs`
- `confirmed_by_build`
- `confirmed_by_runtime_test`
- `maintainer_claim_only`
- `inferred`
- `unknown`

---

## 12. Audit lezárási feltételek

Egy projekt auditja akkor tekinthető lezártnak, ha:

- a vizsgált verzió pontosan azonosított;
- a fő és eltérő licencek rögzítve vannak;
- a nyelvek és runtime-modell azonosított;
- az authoritative state helye tisztázott;
- a frontend–engine kommunikáció dokumentált;
- a build- és packagingút ismert vagy hiánya rögzített;
- a Windows 10+ 64-bit portable megfelelés értékelve;
- az adminjog és prerequisite-igény rögzített;
- a teszt- és stabilitási bizonyítékok felmérve;
- a használható minták és tiltott átvételek elkülönítve;
- minden fontos állításhoz bizonyíték tartozik;
- az AETERNA-szempontú ajánlás és bizonytalanságok rögzítve vannak.

Az audit eredménye nem automatikus technológiai döntés. A több projektből származó bizonyítékokat és az AETERNA saját proofjait közös döntési jelentésben kell összevetni.
