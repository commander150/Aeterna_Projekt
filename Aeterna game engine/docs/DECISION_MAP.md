# AETERNA Game Engine – Decision Map

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.2  
**Dátum:** 2026-07-15  
**Státusz:** aktív rövid döntési és iránytérkép  
**Aktuális technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum röviden rögzíti:

- mi biztosan eldöntött;
- mi a jelenlegi működő referencia;
- mi a következő elsődleges Codex-prioritás;
- mi maradt nyitott technológiai kapu;
- milyen sorrendben halad a fejlesztés;
- mit nem szabad összekeverni.

Kapcsolódó dokumentumok:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `TECHNOLOGY_DECISIONS.md`
- `ARCHITECTURE.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `CURRENT_OPEN_QUESTIONS.md`
- `CURRENT_PROTOTYPE_STATUS.md`
- `CURRENT_CONTRACT_STATUS.md`
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

---

## 1. Biztos projektcél

Az AETERNA elsődlegesen fizikai TCG.

A digitális programegység célja:

- szabálymodellezés és tesztelés;
- programbiztos kártyaadat;
- determinisztikus meccsfuttatás;
- AI-vs-AI;
- későbbi ember–AI játék;
- Godot-alapú kliens;
- végül a 0.0.1 zárt tesztkiadás.

A digitális rendszer nem írhatja felül a hivatalos 1.4v szabályforrásokat emberi döntés nélkül.

---

## 2. Jelenlegi működő referencia

Biztos jelenlegi állítás:

> **Az aktívan fejlesztett és tesztelt authoritative referenciaimplementáció a Python minimal engine.**

Biztos Godot-szerep:

- runtime package loader;
- registry;
- debug nézetek;
- input és UI;
- animáció;
- későbbi kliens;
- contract-fogyasztás.

A Python engine jelenlegi működése bizonyított, ezért:

- megmarad;
- összehasonlítási orákulum;
- regressziós referencia;
- későbbi AI/batch alap;
- akkor sem elveszett munka, ha a termékruntime C# lesz.

Ez nem azonos a végleges termékarchitektúra eldöntésével.

---

## 3. Elsődleges következő Codex-prioritás

> **Runtime engine language and integration comparison.**

Kötelező fő jelöltek:

1. Python sidecar engine + Godot kliens;
2. Godot .NET/C# authoritative runtime.

Opcionális harmadik proof:

3. minimal GDScript transition, csak indokolt esetben.

Kiegészítő kutatási irány:

- embedded Python GDExtension/binding megoldások.

Részletes terv:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

A Codex-feladat sorrendje:

1. helyi tanulóprogramok read-only auditja;
2. licenc- és forrásleltár;
3. közös comparison scenario;
4. Python sidecar proof;
5. Godot .NET/C# proof;
6. contract-, teszt-, packaging- és karbantarthatósági összevetés;
7. szükség esetén GDScript proof;
8. A/B/C döntési jelentés;
9. emberi jóváhagyás.

---

## 4. Végleges technológiai döntés státusza

### Fő jelölt A – Python sidecar + Godot

**Státusz:** `leading_candidate_pending_proof`

Bizonyítandó:

- bridge;
- process lifecycle;
- Windows packaging;
- hibatűrés;
- latency;
- verzióegyeztetés;
- egyértelmű indítás és leállítás.

### Fő jelölt B – Godot .NET/C# runtime

**Státusz:** `leading_candidate_pending_proof`

Bizonyítandó:

- UI-tól elkülönített rules library;
- contracthűség;
- unit tesztelhetőség;
- Godot .NET integráció;
- Windows export;
- portolási és karbantartási költség;
- Python AI/batch réteggel való együttélés.

### Opcionális jelölt C – GDScript runtime

**Státusz:** `open_but_not_primary_proof`

- nincs véglegesen elutasítva;
- teljes második motor nem készül automatikusan;
- csak szűk proof, ha az audit indokolja.

### Embedded Python

**Státusz:** `research_only_deferred`

- több közösségi projekt létezik;
- több experimental vagy WIP;
- első 0.0.1 proofnak jelenleg magasabb kockázatú.

---

## 5. Stabil contract-first döntések

Elfogadott:

- előbb contract, utána implementáció;
- egy futásban egy authoritative state;
- frontend és AI nem találgat legalitást;
- kliens nem módosít MatchState-et;
- kliens action requestet küld;
- engine validál és transitiont hajt végre;
- player-visible és debug projection külön;
- hidden information védett;
- state mutation atomikus;
- rejected action nem mutál state-et;
- typed event és state version determinisztikus.

Ezek a végleges nyelvi/runtime döntéstől függetlenek.

---

## 6. Elkészült alapozási mérföldkövek

### Runtime package–Godot alap

**Állapot:** `completed_foundation`

Elkészült:

- Python runtime package build;
- XLSX exporter migráció;
- valós card/deck/lookup publish;
- Godot loader;
- registryk;
- sample contract loader;
- card reference resolver;
- consistency smoke;
- debug dashboard;
- Godot headless smoke.

### Python minimal rules engine

**Állapot:**

- `current_working_basis`;
- `reference_oracle`.

Elkészült:

- state version guard;
- card instance registry;
- draw és end-turn;
- typed eventek;
- player-visible snapshot;
- Domain topology és occupancy;
- board projection;
- structural Entity placement;
- activity state;
- izolált Wellspring resource contract;
- deterministic AI trajectory.

---

## 7. Gameplay-engine queue

A következő gameplay-lánc továbbra is érvényes, de a runtime-nyelvi döntési kapu mögé került:

1. Wellspring PlayerState- és MatchState-integráció.
2. Player-visible Wellspring summary.
3. Beáramlás precondition.
4. Beáramlás transition és typed event.
5. Magnitúdó-preflight.
6. Aura-source és payment contract.
7. Activity mutation transition.
8. Entitás kijátszási precondition.
9. `play_card` action.
10. Hand → Domain transition.
11. Entry-state.
12. Teljesebb phase és priority.

Státusz:

- `queued_after_language_gate`

A Wellspring feladat nem törlődött. A kiválasztott runtime-ágon folytatandó.

---

## 8. Codex nélküli aktív prioritás

1. `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` közös triázsa.
2. Tanulóprogram-forrás- és licencleltár előkészítése.
3. Runtime language comparison kritériumainak pontosítása.
4. `ABILITY_MODULE_SYSTEM.md` auditja.
5. Hosszú contract-specifikáció konszolidációja.
6. Hivatalos szabályforrásból megválaszolható kérdések ellenőrzése.
7. Dokumentációs státuszok karbantartása.

---

## 9. Tanulóprogram-audit döntési kapu

Vizsgálandó:

- mely tanulóprogramok forrása érhető el helyileg;
- vizsgált commit/tag/verzió;
- licenc és attribution;
- melyik használ Python engine-t;
- melyik használ C#/.NET runtime-ot;
- van-e Godot + Python működő minta;
- hol van az authoritative state;
- milyen bridge és packaging készül;
- melyik csak UI-minta;
- melyik minta alkalmazható clean-room módon AETERNA-ra.

A tanulóprogramok szándékosan nincsenek az AETERNA GitHub repositoryban.

---

## 10. Runtime package döntések

Lezárt:

- Godot nem olvas közvetlenül XLSX-et;
- Python végzi az exportot és validációt;
- runtime package statikus programadat;
- Godot `runtime_package/` consumption copy;
- publish előtt validation gate.

Nyitott:

- végleges package identity és schema;
- build/output könyvtár;
- release/version registry;
- TEMP staging kiváltása;
- publikus build integritásvédelem.

Ezek a runtime-nyelvi döntéstől részben függetlenek.

---

## 11. Mérföldkő-térkép

- M1 – minimal determinisztikus engine-alapok
- M2 – player view és board contract
- M3 – első gameplay actionök
- M4 – phase, priority és reakciók
- M5 – combat és győzelmi feltételek
- M6 – első játszható vertical slice
- M7 – teljes alapjátékos tesztprogram
- M8 – meta- és termékrendszerek
- M9 – 0.0.1 release candidate

Jelenlegi állapot:

- M1 jelentős alapja elkészült Pythonban;
- M2 első szakasza elkészült;
- M3 előtt runtime-nyelvi döntési kapu került be;
- a döntés után a választott runtime-ágon folytatódik a gameplay-engine.

---

## 12. Amit biztosan nem keverünk össze

- jelenlegi Python referencia ≠ végleges termékruntime;
- C# jelölt ≠ eldöntött C# migráció;
- Godot UI ≠ authoritative state;
- runtime package ≠ MatchState;
- sample contract ≠ production contract;
- structural placement ≠ teljes play legality;
- Magnitúdó ≠ elérhető Aura;
- activity state ≠ idézési betegség;
- tanulóprogram-minta ≠ automatikusan átvehető kód;
- comparison prototype ≠ két teljes engine kötelező felépítése;
- Python referencia fenntartása ≠ kötelező Python termékruntime.

---

## 13. Rövid jelenlegi döntés

- A Python minimal engine megmarad működő referenciaimplementációnak.
- A Godot kliens- és loaderalap megmarad.
- A következő Codex-prioritás a Python sidecar és a Godot .NET/C# összehasonlító proofja.
- GDScript csak szükség esetén kap szűk comparison scope-ot.
- A végleges runtime/backend döntés még nyitott.
- A jelentős gameplay-engine bővítés a döntési kapu után folytatódik.
- Codex nélkül dokumentációs, audit- és döntés-előkészítő munka folytatódik.
