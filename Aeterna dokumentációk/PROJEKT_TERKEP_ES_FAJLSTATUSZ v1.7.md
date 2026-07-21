# AETERNA – Projekt Térkép és Fájlstátusz v1.7

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.7  
**Dátum:** 2026-07-22  
**Státusz:** aktív magas szintű projekt- és fájlszerep-térkép  
**Felváltott dokumentum:** `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.6.md`  
**Ellenőrzött repository-bázis:** `66a206c6e3bf9155fb9f71a354236fb5b6ab3b90` – `docs update 2026.07.22`  
**C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Ez a dokumentum csak a jelenlegi fő rétegeket, aktív forrásokat és fontos fájlszerepeket rögzíti. Nem teljes repository-inventár és nem részletes cleanup-napló.

---

## 1. Projekt fő rétegei

1. hivatalos szabályforrások;
2. kártyaadatbázis és LOOKUPS;
3. Python adat-, audit-, AI- és batch-tooling;
4. Python reference engine;
5. Godot vizuális kliens és debugréteg;
6. C# runtime proof;
7. tervezett production C# authoritative engine;
8. aktív projekt- és engine-dokumentáció;
9. történeti archívum;
10. regenerálható outputok és test fixture-ök.

Elfogadott authority:

- Godot/GDScript = vizuális kliens;
- C#/.NET = production rules authority;
- Python = external tooling és reference.

---

## 2. Aktív hivatalos és szerkesztési források

### Szabályforrások

- `Aeterna dokumentációk/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`;
- `Aeterna dokumentációk/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`.

Státusz: `ACTIVE_CANONICAL_RULE_SOURCE`

### Adatforrások

- `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `Aeterna dokumentációk/LOOKUPS.xlsx`.

Státusz: `ACTIVE_EDITING_SOURCE`

### Aktuális adataudit

- `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS AKTUÁLIS ADATAUDIT 1.0.md`.

Státusz: `ACTIVE_DATA_AUDIT`

A `reference/` alatti véletlen másolata már kikerült.

---

## 3. Aktív projektirányítás

- `README.md`;
- `Aeterna dokumentációk/README.md`;
- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.4.md`;
- jelen `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.7.md`;
- `Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`.

A korábbi projekttervek és projekt-térképek archívumba kerültek.

---

## 4. Aktív engine-réteg

### C#

Jelenlegi proofprojektek:

- `Aeterna.RuntimeCandidate`;
- `Aeterna.RuntimeCandidate.Proof`.

Következő production projektek:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`.

A production engine még nem létezik.

### Python

Aktív szerepek:

- runtime package build;
- XLSX/JSON/JSONL tooling;
- audit és diagnostics;
- reference engine;
- fixture és scenario;
- AI-vs-AI és batch;
- differential testing.

Nem production authority.

### Godot

Aktív szerepek:

- runtime package loader;
- registryk;
- snapshot/legal action/event debug;
- visual client foundation;
- C# bridge proof.

Nem szabályforrás.

### Runtime comparison

A comparison fixture és artifactok regressziós referenciaként megmaradnak.

---

## 5. Aktív engine-dokumentáció

Elsődleges technikai irány:

- `ARCHITECTURE.md`;
- `TECHNOLOGY_DECISIONS.md`;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `DECISION_MAP.md`.

Aktuális státusz:

- `PROTOTYPE_STATUS.md`;
- `RUNTIME_PACKAGE_STATUS.md`;
- `CONTRACT_STATUS.md`.

Kérdés–válasz rendszer:

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

Folytatási pont:

- `checkpoints/ENGINE_CHECKPOINT.md`.

A további tömeges dokumentációs aktualizálás nem aktív projektprioritás.

---

## 6. Reference-réteg

Megtartandó aktív reference dokumentumok:

- kártyatervezési katalógus;
- Ötletláda 1.1v;
- Általános névprofil-sablon;
- GitHub munkarend;
- tesztprogram-workflow;
- Master Duel / Hearthstone tanulságok.

A reference dokumentum nem canonical szabály- vagy runtime-forrás.

A régi Python-architektúra-, backend-, effect-, trigger- és újratervezési anyagok archívumba kerültek.

---

## 7. Archívum

A dokumentációs rendezés során az elődök és történeti fájlok archívumba kerültek.

Tényleges fő útvonalak:

- `Archive/aeterna dokumentáciok/`;
- `Archive/aeterna gaming engine/`.

A dokumentációs archívumban tematikus csoportok találhatók, többek között:

- `project_guidance/`;
- `card_database_audits_1.8v/`;
- `design_ideas/`;
- `generated_exports/`;
- `old_python_engine_docs/`;
- `redesign_history/`;
- `superseded_active_docs/`.

Az archív fájl:

- nem aktív authority;
- nem szerkesztendő canonical forrásként;
- történeti és auditcélra megőrzendő.

Az archív mappanevek további esztétikai rendezése jelenleg nem prioritás.

---

## 8. Generált és ideiglenes outputok

A régi `cards.xlsx` szöveges exportbatch archiválva lett:

`Archive/aeterna dokumentáciok/generated_exports/cards_xlsx_text_export_2026-05-25/`

Új generált batch csak egyértelmű:

- forrásazonosítóval;
- dátummal;
- formátumverzióval;
- rekordszámmal;
- regenerálási leírással

maradhat meg.

Generált output nem válhat canonical szerkesztési forrássá.

---

## 9. Fontos nyitott munkasávok

### C.5B production engine

Státusz: `READY_FOR_IMPLEMENTATION`

Ez a következő fő fejlesztési feladat.

### Adat- és LOOKUPS-audit

Nyitva:

- külön LOOKUPS-audit;
- ID-contract;
- delimiter;
- aliasok;
- master–export parity;
- névprofil és decklista-segédnevek.

Nem blokkolja a C.5B alapozást.

### Gameplay-migráció

C.5B után:

- Wellspring;
- Beáramlás;
- Magnitúdó;
- Aura;
- `play_card`;
- Domain;
- phase/priority;
- reaction;
- combat;
- ability;
- win/loss.

---

## 10. Dokumentációs minimum

A dokumentációs szakasz lezárásához csak négy fájl kritikus:

1. projektterv v6.4;
2. jelen projekt-térkép v1.7;
3. engine-checkpoint v1.4;
4. root README v2.1.

Minden más aktív dokumentumot csak valódi technikai vagy szabályi változáskor kell frissíteni.

---

## 11. Aktuális státusz

- archív rendezés: `COMPLETE`;
- adataudit-duplikáció megszüntetése: `COMPLETE`;
- régi projektverziók archiválása: `COMPLETE`;
- régi engine-terv és gyökér-összefoglalók archiválása: `COMPLETE`;
- kritikus dokumentumok frissítése: `IN_PROGRESS`;
- végső gyors dokumentációs ellenőrzés: `NEXT`;
- C.5B production foundation: `READY_FOR_IMPLEMENTATION`;
- Codex: `AVAILABLE`.
