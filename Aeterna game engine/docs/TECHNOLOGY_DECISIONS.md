# AETERNA Game Engine – Technology Decisions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.2  
**Dátum:** 2026-07-15  
**Státusz:** aktív technológiai döntési és vizsgálati dokumentum  
**Aktuális technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum külön kezeli:

- a jelenleg bizonyított és használt fejlesztési modellt;
- a működő Python referenciaimplementációt;
- a hosszú távú authoritative termékruntime jelöltjeit;
- a végleges döntéshez szükséges prototípusokat és auditokat;
- a Codex következő elsődleges feladatát.

Kapcsolódó elsődleges dokumentumok:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `CURRENT_OPEN_QUESTIONS.md`
- `ARCHITECTURE.md`
- `DECISION_MAP.md`
- `CURRENT_PROTOTYPE_STATUS.md`
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

Az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó. Az előbbi a kérdésindex, az utóbbi a részleges válaszok és döntési irányok nyilvántartása.

---

## 1. A technológiai döntés jelenlegi állapota

### 1.1 Biztos jelenlegi munkabázis

A jelenleg működő, tesztelt és authoritative referenciaimplementáció:

> **az új Python minimal rules engine.**

Ez ténylegesen biztosít:

- MatchState-et és PlayerState-et;
- card instance registryt;
- state invariantokat;
- action request/response alapot;
- draw és end-turn transitiont;
- typed eventeket;
- player-visible snapshotot;
- Domain topológiát és occupancyt;
- AI-vs-AI trajectoryt;
- nagy számú automatizált tesztet.

A Python engine ezért:

- megőrzendő;
- regression/reference oracle;
- comparison fixture alap;
- későbbi AI/batch és fejlesztői tooling alapja;
- akkor sem elveszett munka, ha a végső termékruntime C# lesz.

### 1.2 Ami még nem végleges döntés

Nincs még véglegesen eldöntve, hogy a kész AETERNA termék authoritative rules runtime-ja:

- külön Python sidecar lesz;
- Godot .NET/C# lesz;
- részleges vagy teljes GDScript runtime lesz;
- más, contract-first hibrid modell lesz.

Embedded Python binding/GDExtension megoldás szintén létezik mint kutatási irány, de jelenleg nem elsődleges proof.

### 1.3 Új prioritási döntés

A következő Codex-hozzáférés elsődleges feladata:

> **Python sidecar + Godot és Godot .NET/C# authoritative runtime összehasonlító proof.**

A jelentős új gameplay-engine bővítés a döntési kapuig szünetel.

A Wellspring production integráció:

- továbbra is kész következő gameplay-feladat;
- nincs törölve;
- a kiválasztott runtime-ágon folytatandó.

---

## 2. Contract-first közös alap

A végleges technológiai modelltől függetlenül elfogadott:

- előbb contract, utána implementáció;
- a UI nem lehet szabályforrás;
- a kliens nem módosíthatja közvetlenül a MatchState-et;
- a legalitást authoritative engine számítja;
- a kliens action requestet küld;
- az engine action response-t, eventeket és projectiont ad;
- player-visible és debug nézet külön marad;
- rejtett információ nem szivároghat;
- state mutation atomikus;
- rejected action nem mutál state-et;
- eventek determinisztikusak és auditálhatók;
- ugyanazon comparison scenariónak nyelvtől függetlenül azonos jelentésű outputot kell adnia.

Ezek Python, C#, GDScript vagy más hibrid megoldás esetén is megtartandók.

---

## 3. Jelenlegi működő rendszerkép

A jelenlegi fejlesztési és tesztelési út:

    Google Sheets / XLSX
            ↓
    Python export, validáció és runtime package build
            ↓
    runtime package
            ↓
    Python minimal rules engine
            ↓
    snapshot / legal actions / responses / events
            ↓
    Godot loader és debug kliensalap

Ez a jelenlegi működő fejlesztési kép, nem feltétlenül a végleges process- és packaging-architektúra.

---

## 4. Python tartósan biztos szerepei

A végleges runtime-nyelvtől függetlenül a Python erős és valószínűleg tartós szerepei:

- adatpipeline;
- XLSX és JSON/JSONL feldolgozás;
- runtime package build;
- validáció és diagnostics;
- AI-vs-AI és batch futtatás;
- balansz- és statisztikai tooling;
- szabályregressziós referencia;
- scenario runner;
- replay és reprodukálhatósági ellenőrzés;
- tanuló AI és kutatási workflow.

Ha a termékruntime C# lesz, a Python engine:

- referenciaimplementáció maradhat;
- expected outputot adhat;
- differential testing alap lehet;
- nem kell automatikusan minden termékkódot duplikálnia.

---

## 5. Godot tartósan biztos szerepei

Bizonyított:

- runtime package loader;
- card/deck/lookup registry;
- sample snapshot, legal action és event betöltés;
- snapshot viewer;
- legal action debug panel;
- event log debug view;
- unified debug dashboard;
- headless smoke futtatás;
- Windows/Godot futtatási minta.

Jelenlegi biztos szerepek:

- runtime package fogyasztó;
- debug- és visualization-réteg;
- játékos UI;
- input és animáció;
- kliensoldali contract-fogyasztás.

Kötelező határ:

- UI node-ba nem kerülhet rejtett szabálylogika;
- a Godot kliens nem találgathat legalitást;
- C# runtime esetén is külön rules library/réteg kell;
- GDScript proof esetén sem keverhető a rules state a megjelenítési node-okkal.

---

## 6. Technológiai modellek aktuális státusza

### Modell A – Régi Python motor mint backend

**Státusz:** `reference_only_pending_audit`

- nem automatikus új backend;
- algoritmus-, AI-, diagnostics- és balanszforrás lehet;
- célzott audit és új teszt nélkül nem emelhető át.

### Modell B – Új Python sidecar backend + Godot frontend

**Státusz:** `leading_candidate_pending_proof`

Bizonyított:

- a Python engine belső működése;
- a Godot kliens- és loaderalap;
- külön folyamatú Godot–Python kommunikációra létező működő külső minta.

Még bizonyítandó:

- AETERNA handshake és protocol;
- stdin/stdout vagy TCP választás;
- process lifecycle;
- Windows packaging;
- version mismatch;
- crash és restart;
- deployment méret és egyszerű indítás.

### Modell C – Godot .NET/C# authoritative runtime

**Státusz:** `leading_candidate_pending_proof`

Előnyjelölt:

- hivatalos Godot/.NET út;
- közvetlen Godot-integráció;
- nincs külön Python process;
- erős statikus típusosság;
- kiforrott unit test és serialization ökoszisztéma;
- egyszerűbb egyetlen Windows-alkalmazásként való csomagolás lehetősége.

Még bizonyítandó:

- tiszta rules library/UI-elhatárolás;
- ugyanazon Python reference scenarióval való contractegyezés;
- Godot .NET build és export;
- portolási költség;
- karbantarthatóság;
- Codex által készített C# kód minősége;
- Python AI/batch toolinggal való együttélés.

### Modell D – Teljes vagy részleges GDScript rules runtime

**Státusz:** `open_but_not_primary_proof`

- nincs kiválasztva főágként;
- nincs véglegesen elutasítva;
- tanulóprogram-audit vagy első két proof után kaphat szűk vizsgálati scope-ot;
- teljes második motor nem előfeltétel.

### Modell E – Embedded Python Godotban

**Státusz:** `research_only_deferred`

Vizsgált közösségi irányok:

- py4godot;
- godot-python-extension;
- GodoPy;
- régi godot-python.

Jelenlegi megállapítás:

- technikailag érdekes;
- több projekt aktív vagy fejlődő;
- több projekt experimental/WIP;
- Godot- és Python-verzió kompatibilitás, natív build és packaging kockázatosabb;
- nem az első AETERNA comparison proof.

### Modell F – Python reference + C# product runtime

**Státusz:** `possible_hybrid_outcome`

Lehetséges végállapot:

- Python: adatpipeline, AI/batch, differential test és referencia;
- C#: authoritative játék-runtime;
- Godot .NET: kliens és termékfuttatás;
- közös contractok és fixture-ek.

Csak akkor fogadható el, ha a differential testing és a contractkezelés nem hoz létre kezelhetetlen kettős szabálykarbantartást.

---

## 7. Tanulóprogram-audit

A felhasználó által letöltött tanulóprogramok szándékosan nincsenek az AETERNA GitHub repositoryban licencbiztonsági okból.

A következő Codex-audit helyileg vizsgálja őket.

Kötelező auditmezők:

- projekt és forrás;
- vizsgált commit/tag/verzió;
- licenc;
- nyelvek;
- Godot-verzió;
- rules runtime helye;
- authoritative state;
- Python használat;
- C# használat;
- GDScript szerep;
- kommunikáció és bridge;
- packaging;
- Windows támogatás;
- automatikus tesztek;
- clean-room módon használható minta;
- attributionkövetelmény;
- AETERNA-kockázat.

Kiemelt online referenciák:

- Godot RL Agents;
- py4godot;
- godot-python-extension;
- GodoPy;
- régi godot-python.

Másolt kód alapértelmezés szerint ne kerüljön az AETERNA repositoryba.

---

## 8. Közös comparison scenario

A Python sidecar és C# proof ugyanazt a minimal scenariót használja:

1. initial state;
2. `draw_card` P1;
3. `end_turn`;
4. `draw_card` P2;
5. player-visible snapshot P1;
6. player-visible snapshot P2;
7. typed event log;
8. stale expected state version rejection;
9. determinisztikus második futás;
10. canonical JSON összevetés.

Kötelezően összevetendő:

- contracthűség;
- determinisztika;
- hidden-information;
- unit tesztelhetőség;
- headless futás;
- AI/batch alkalmasság;
- Godot-integráció;
- Windows packaging;
- process- és crash-kezelés;
- teljesítmény;
- build reprodukálhatóság;
- emberi karbantarthatóság;
- Codex kódminőség;
- portolási költség;
- licenc.

Részletes terv:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

---

## 9. Runtime package és adatpipeline

Ezek a döntések lezártnak tekinthetők:

- a fő szerkesztés Google Sheetsben történik;
- a lokális XLSX forrásmásolat;
- Godot nem olvas közvetlenül XLSX-et;
- Python végzi az exportot, validációt és package buildet;
- a runtime package statikus programadat;
- publish előtt validation gate kell;
- a Godot `runtime_package/` consumption copy;
- a generált output nem canonical szerkesztési forrás.

A package identity, release-versioning, final build/output struktúra és integritásvédelem még nyitott.

Ezek akkor is érvényesek maradhatnak, ha a rules runtime C# lesz.

---

## 10. Tesztelési döntések

Elfogadott:

- minden új engine-contract kapjon célzott tesztet;
- state mutation success és rejection tesztet kapjon;
- rejected action ne mutáljon state-et;
- a Python referencia teljes izolált tesztkészlete megmarad;
- minimal engine smoke megmarad;
- AI-vs-AI determinisztikus JSON ellenőrzés megmarad;
- hidden-information tesztek kötelezők;
- deep-copy és inputváltozatlanság ellenőrzendő;
- Godot loader és contract smoke tesztek megőrzendők;
- comparison proofhoz közös fixture és expected output kell;
- C# proof kapjon saját unit teszteket;
- bridge-prototípus kapjon kétoldali compatibility és lifecycle tesztet;
- a két runtime outputeltérését strukturált differential report jelezze.

---

## 11. Prioritási sorrend

### Következő Codex-prioritás

1. helyi tanulóprogram-audit;
2. licenc- és forrásleltár;
3. közös scenario/fixture;
4. Python sidecar proof;
5. Godot .NET/C# proof;
6. összehasonlító tesztek és Windows packaging;
7. szükség esetén minimal GDScript proof;
8. döntési jelentés;
9. emberi választás.

### Gameplay-engine queue a döntés után

1. Wellspring production integráció;
2. player-visible Wellspring summary;
3. Beáramlás;
4. Magnitúdó és payment;
5. első `play_card`;
6. első szabálymotoros vertical slice.

### Codex nélküli munkasáv

- Open Questions + Decisions közös triázsa;
- dokumentációs konszolidáció;
- auditmezők és comparison kritériumok kidolgozása;
- ability module audit;
- contract-specifikáció konszolidációja;
- hivatalos szabályforrás-ellenőrzés.

---

## 12. Jelenleg biztosan kijelenthető

- A Python minimal engine működik és értékes referencia.
- A Godot runtime package-, registry- és debugalap működik.
- A C#/.NET komolyan vizsgálandó, hivatalos Godot-runtime jelölt.
- A Python sidecar technikailag reális jelölt.
- A contract-first határ minden modellnél szükséges.
- A UI nem lehet szabályforrás.
- Nem célszerű két teljes szabálymotort előre felépíteni.
- A jelentős gameplay-fejlesztést a nyelvi/runtime döntési kapu után kell folytatni.
- A végleges termékarchitektúra még technológiai bizonyítást igényel.
- A végleges döntés emberi jóváhagyással történik.
