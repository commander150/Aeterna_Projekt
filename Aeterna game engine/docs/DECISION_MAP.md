# AETERNA Game Engine – Decision Map

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.3  
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

### 1.1 Playtest és szabályfelülvizsgálat

Az AETERNA még nem kapott teljes, szabályhű valódi játéktesztet. Több jelenlegi szabály- és balanszdöntés ezért elméleti tervezésre, részleges tesztre vagy szimulációs várakozásra épül.

Projektirányítási szabály:

- az elfogadott döntés az aktuális rulesetben canonical;
- az engine, AI és tesztek ezt kötelesek követni;
- a „playtestre vár” megjelölés nem teszi a szabályt opcionálissá;
- szabályhű playtest alapján bármely szabály, számérték vagy identitás felülvizsgálható;
- playtesteredmény nem módosít automatikusan szabályt;
- változtatáshoz explicit emberi döntés, döntésnapló és verziózott forrásátvezetés kell;
- a korábbi szabály, a teszteredmény és a módosítás indoka visszakereshető marad;
- a stabil engine-contractot csak az új canonical döntés elfogadása után szabad módosítani.

Ez az elv minden jelenlegi és későbbi gameplay-, balansz-, Birodalom-, Klán- és kártyadöntésre érvényes.

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

1. Elfogadott gameplay-döntések current dokumentumokba vezetése.
2. Beáramlás timing/priority/event kérdéseinek előkészítése.
3. Payment source selection döntési lehetőségeinek előkészítése.
4. LOOKUPS Birodalom-, Aura-költség- és explicit kivételértékek célzott ellenőrzése.
5. Dokumentációs státuszok karbantartása új párhuzamos fájlok nélkül.

---

## 9. Rövid irányelv

> **A current canonical szabályt implementáljuk és teszteljük. A szabályhű playtest eredménye alapján később explicit, verziózott döntéssel módosíthatjuk.**