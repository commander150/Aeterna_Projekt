# AETERNA Game Engine – Technology Decisions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív technológiai döntési és vizsgálati dokumentum  
**Aktuális technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum külön kezeli:

- a jelenleg bizonyított és használt fejlesztési modellt;
- a hosszú távú termékarchitektúra jelöltjét;
- a még vizsgálandó technológiai alternatívákat;
- a végleges döntéshez szükséges prototípusokat és auditokat.

Kapcsolódó elsődleges dokumentumok:

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

### 1.1 Biztos jelenlegi munkairány

A jelenleg aktívan fejlesztett és bizonyított szabálymotor:

> **az új Python minimal rules engine.**

Ez jelenleg ténylegesen biztosít:

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

A Python engine ezért a jelenlegi fejlesztési szakasz authoritative implementációs bázisa.

### 1.2 Ami még nem végleges döntés

A következő állítás jelenleg még nem bizonyított véglegesen:

> a kész AETERNA termékben minden authoritative rules runtime biztosan külön Python backendként fog futni a Godot kliens mellett.

A hosszú távú célállapot-jelölt továbbra is:

- Python rules/backend;
- Godot frontend/kliens.

Ez erős jelölt, mert a Python engine már működik és jól tesztelhető. A végleges termékarchitektúrához azonban még vizsgálni kell:

- a Godot és Python közötti tényleges futási kapcsolatot;
- a Python runtime csomagolását;
- Windows-indítást és process lifecycle-t;
- teljesítményt és hibakezelést;
- a tanulóprogramok releváns technológiai mintáit;
- azt, van-e olyan működő referencia, amely Godot klienssel Python engine-t használ;
- szükséges-e célzott Python–GDScript összehasonlító prototípus.

### 1.3 Fontos különbség

Nem azonos állítás:

- „jelenleg Pythonban fejlesztjük az authoritative engine-t”;
- „a végleges termékarchitektúra már visszavonhatatlanul eldőlt”.

Az első igaz és bizonyított.

A második még technológiai vizsgálati kapu.

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
- eventek determinisztikusak és auditálhatók.

Ezek az elvek Python backend, GDScript runtime vagy más hibrid megoldás esetén is megtartandók.

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
    player-visible snapshot / legal actions / responses / events
            ↓
    jelenlegi debug és későbbi Godot kliensintegráció

Ez a működő fejlesztési kép, nem feltétlenül a végleges process- és packaging-architektúra.

---

## 4. Python jelenlegi szerepe

### Bizonyított szerepek

- adatpipeline;
- XLSX és JSON/JSONL feldolgozás;
- runtime package build;
- validáció és diagnostics;
- authoritative minimal MatchState;
- transitionök és eventek;
- player-visible projection;
- headless futtatás;
- AI-vs-AI;
- scenario és batch alap;
- determinisztikus tesztelés.

### Miért folytatjuk most Pythonban?

- már jelentős működő engine-alap készült el;
- minden kis lépés automatikusan tesztelhető;
- a szabálylogika UI nélkül ellenőrizhető;
- a contractok később más kliensből is fogyaszthatók;
- a most elkészülő state- és szabálymodellek akkor is hasznosak, ha a végső futási integráció módosul.

A Python fejlesztés folytatása tehát nem előlegezi meg automatikusan a végleges packaging-döntést.

---

## 5. Godot/GDScript jelenlegi szerepe

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
- későbbi játékos UI;
- input és animáció;
- kliensoldali contract-fogyasztás.

Jelenlegi korlát:

- UI node-ba nem kerülhet rejtett szabálylogika;
- a Godot kliens nem találgathat legalitást;
- ugyanazon futási modellben nem tarthatunk fenn ellenőrizetlenül eltérő Python és GDScript szabályokat.

Ez nem jelenti azt, hogy a GDScript runtime-alkalmasság kérdése végleg lezárult. Azt jelenti, hogy jelenleg nem építünk párhuzamosan egy második teljes szabálymotort bizonyíték nélkül.

---

## 6. Vizsgált technológiai modellek aktuális státusza

### Modell A – Régi Python motor mint backend

**Státusz:** `reference_only_pending_audit`

- nem automatikus új backend;
- algoritmus-, AI-, diagnostics- és balanszforrás lehet;
- célzott audit és új teszt nélkül nem emelhető át.

### Modell B – Új Python backend + Godot frontend

**Státusz:** `leading_candidate_and_current_working_model`

- jelenleg ez a legerősebb jelölt;
- a Python engine működése bizonyított;
- a Godot frontend és loader alapja működik;
- a tényleges bridge, packaging és termékfuttatás még bizonyítandó.

### Modell C – Teljes GDScript rules runtime

**Státusz:** `open_but_not_active_implementation`

- nincs kiválasztva jelenlegi fejlesztési főágként;
- nincs véglegesen elutasítva;
- érdemi döntéshez tanulóprogram-audit és célzott prototípus kell;
- egy teljes második motor megépítése nem előfeltétele a vizsgálatnak.

### Modell D – Python tesztmotor + külön GDScript játékengine

**Státusz:** `high_duplicate_rules_risk_pending_comparison_evidence`

- magas a szabályeltérés és dupla karbantartás kockázata;
- emiatt nem aktív megvalósítási terv;
- csak erős technikai indok és összehasonlító bizonyíték esetén válhat reális iránnyá.

### Modell E – Python csak package builder, GDScript fő runtime

**Státusz:** `deferred_pending_learning_project_and_runtime_audit`

- a Python rules engine előrehaladása miatt jelenleg nem elsődleges;
- mégsem tekintendő bizonyítás nélkül végleg obsolete-nek;
- a tanulóprogramok és Godot runtime-minták auditja után újraértékelhető.

---

## 7. Tanulóprogram-audit

### 7.1 Miért szükséges?

A tanulóprogramok vizsgálatából kiderülhet:

- használ-e valamelyik Godot kliens Python engine-t;
- milyen bridge- vagy process-modellt alkalmaz;
- hogyan kezeli a state-et és a kliensprojekciót;
- hogyan csomagolja a Python runtime-ot;
- milyen teljesítmény- vagy platformkorlátok jelentkeznek;
- mennyi szabálylogika marad a Godotban;
- a minták közül mi fordítható AETERNA-saját clean-room megoldásra.

### 7.2 Jelenlegi forráshelyzet

A repositoryban jelenleg elérhető:

- `AETERNA – tanulóprojektekből kinyert legfontosabb fejlesztési irányok.md`

A dokumentum több külső referenciát összefoglal, de a jelenlegi GitHub-keresésben a tanulóprogramok teljes forrásfái nem azonosíthatók egyértelműen.

Ezért a teljes technológiai audit előtt ellenőrizni kell:

- mely forrásprojektek vannak ténylegesen a repositoryban;
- melyek külső referenciák;
- melyek töltendők fel vagy linkelendők később;
- melyik használ Python engine-t Godottal;
- melyik releváns csak UI-mintaként.

### 7.3 Auditkimenet

A későbbi audit készítsen projektenkénti táblát legalább ezekkel:

- projekt neve;
- nyelv és engine;
- Godot-verzió;
- rules runtime helye;
- Python használat módja;
- frontend–engine kommunikáció;
- packaging;
- state authority;
- hidden information kezelése;
- használható minta;
- AETERNA-kockázat;
- ajánlott további prototípus.

---

## 8. Python–GDScript összehasonlító vizsgálat

A Python–GDScript comparison kérdés **nem obsolete**.

Jelenlegi státusza:

- `deferred_pending_learning_project_audit`;
- `blocked_by_comparison_scope_design`;
- `not_active_parallel_engine_build`.

A vizsgálat célja nem feltétlenül két teljes engine megépítése.

Lehetséges szűk bizonyítások:

1. azonos action request és response round-trip;
2. azonos player-visible snapshot Godot-oldali parserrel;
3. minimal state transition GDScript proof-of-concept;
4. Python child process vagy service bridge;
5. latency és hibakezelés;
6. deterministic JSON összevetés;
7. Windows packaging és indítás;
8. egy tanulóprogram működő Python–Godot mintájának reprodukálása.

Csak a tanulóprogram-audit után kell eldönteni, melyik összehasonlítás ad valódi információt.

---

## 9. Python–Godot integrációs alternatívák

Továbbra is nyitott:

1. Python child process + stdin/stdout JSON;
2. lokális socket vagy HTTP service;
3. csomagolt Python sidecar;
4. fejlesztői headless engine és külön kliens;
5. natív vagy más beágyazási bridge;
6. GDScript runtime bizonyos vagy teljes szabályrétegre, ha a későbbi audit ezt indokolja.

Kötelező elvek bármelyik megoldásnál:

- explicit action request;
- state/version guard;
- atomikus state mutation;
- player-visible response;
- debug adat csak debug módban;
- determinisztikus naplózhatóság;
- kontrollált kapcsolat- és processhiba;
- egyértelmű authoritative state.

---

## 10. Adatpipeline és runtime package

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

---

## 11. Tesztelési döntések

Elfogadott:

- minden új engine-contract kapjon célzott tesztet;
- state mutation success és rejection tesztet kapjon;
- rejected action ne mutáljon state-et;
- minden Python tesztmodul izoláltan is fusson;
- minimal engine smoke kötelező;
- AI-vs-AI determinisztikus JSON ellenőrzés kötelező;
- hidden-information tesztek kötelezők;
- deep-copy és inputváltozatlanság ellenőrzendő;
- Godot loader és contract smoke tesztek megőrzendők;
- későbbi bridge-prototípushoz kétoldali contract compatibility teszt kell.

---

## 12. Következő technológiai bizonyítási sorrend

A belső rules-engine fejlesztés folytatható a jelenlegi Python bázison:

1. Wellspring production integráció;
2. player-visible Wellspring summary;
3. Beáramlás;
4. Magnitúdó és payment;
5. első `play_card`;
6. első szabálymotoros vertical slice.

Ezzel párhuzamos vagy közbeiktatott dokumentációs/technológiai munkasáv:

1. `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` közös triázsa;
2. tanulóprogram-források leltára;
3. Python–Godot minták auditja;
4. comparison-prototípus scope;
5. minimal bridge-prototípus;
6. Windows packaging proof;
7. végleges runtime-technológiai döntési kapu.

---

## 13. Jelenleg biztosan kijelenthető

- A Python minimal rules engine működik és továbbfejleszthető.
- A Godot runtime package-, registry- és debugalap működik.
- A contract-first határ mindkét irányban szükséges.
- A UI nem lehet szabályforrás.
- A jelenlegi engine-fejlesztést nem kell megállítani a végleges bridge-döntésig.
- Nem célszerű most két teljes szabálymotort párhuzamosan felépíteni.
- A Python backend + Godot frontend a legerősebb jelenlegi jelölt.
- A végleges termékarchitektúra még technológiai bizonyítást igényel.
- A Python–GDScript összehasonlítás és a tanulóprogram-audit továbbra is nyitott feladat.
