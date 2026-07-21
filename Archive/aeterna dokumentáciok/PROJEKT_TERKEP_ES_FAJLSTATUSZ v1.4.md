# AETERNA – Projekt Térkép és Fájlstátusz v1.4

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.4  
**Dátum:** 2026-07-15  
**Státusz:** aktív magas szintű projekt- és fájlstátusz-térkép  
**Felváltott dokumentum:** `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`

Ez a dokumentum az AETERNA repository jelenlegi fő mappáit, aktív forrásait, technikai rétegeit, döntési kapuit és fájlstátuszait rögzíti.

Nem teljes fájlonkénti inventár, nem törlési lista és nem refaktor-parancs.

A v1.4 fő változása:

- a Python engine működő referenciaimplementációként szerepel;
- a végleges termékruntime még nyitott;
- a Python sidecar és a Godot .NET/C# a két fő comparison-jelölt;
- a következő Codex-prioritás a runtime-nyelvi proof;
- a Wellspring gameplay-feladat a döntési kapu után folytatandó.

---

## 1. Aktuális projektkép

A repository fő rendszerrétegei:

1. hivatalos szabályforrások;
2. kártyaadatbázis és LOOKUPS;
3. Python adatpipeline és runtime package tooling;
4. működő Python minimal rules-engine referencia;
5. Godot loader-, debug- és kliensalap;
6. Godot .NET/C# runtime proof-jelölt;
7. Python sidecar runtime proof-jelölt;
8. régi Python motor referenciaágként;
9. dokumentáció és audit;
10. archív és generált anyagok.

Aktuális projektterv:

- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.1.md`

Aktuális elsődleges technológiai kapu:

- `Aeterna game engine/docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

Aktuális működő engine-reference:

- `Aeterna game engine/docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

---

## 2. Státuszszótár

| Státusz | Jelentés |
|---|---|
| `ACTIVE_CANONICAL_RULE_SOURCE` | Elsődleges hivatalos szabályforrás. |
| `ACTIVE_EDITING_SOURCE` | Ember által aktívan szerkesztett adatforrás. |
| `ACTIVE_PROJECT_GUIDANCE` | Aktív projektirányító dokumentum. |
| `CURRENT_REFERENCE_ENGINE` | Működő és tesztelt referenciaimplementáció. |
| `RUNTIME_CANDIDATE` | Végleges termékruntime-jelölt, proof szükséges. |
| `ACTIVE_TOOLING` | Aktív export-, build- vagy validációs eszköz. |
| `ACTIVE_TEST` | Aktív regressziós vagy smoke teszt. |
| `ACTIVE_CONSUMER` | Aktív fogyasztói, loader- vagy kliensréteg. |
| `GENERATED_OUTPUT` | Regenerálható kimenet, nem canonical szerkesztési forrás. |
| `TEST_FIXTURE` | Teszt- vagy debugfixture. |
| `QUEUED_AFTER_LANGUAGE_GATE` | A runtime-nyelvi döntés után folytatandó feladat vagy réteg. |
| `SUPERSEDED_REFERENCE` | Újabb dokumentum által felváltott, megőrzött referencia. |
| `OLD_ENGINE_REVIEW` | Régi motorhoz tartozó, áttekintendő kód vagy dokumentum. |
| `OLD_ENGINE_REFERENCE` | Megőrzendő régi motoros háttérforrás. |
| `EXTERNAL_RESEARCH_SOURCE` | Helyileg vagy külső forrásból vizsgált, nem repository-canonical projekt. |
| `ARCHIVE_REVIEW` | Archívum- vagy törlési döntés előtt felülvizsgálandó. |
| `PROTECTED_DO_NOT_MOVE` | Hivatkozások miatt jelenleg nem mozgatható biztonságosan. |

---

## 3. Gyökérszint

### `README.md`

- státusz: `ACTIVE_PROJECT_GUIDANCE`
- szerep: repository-szintű projektkép és belépési pont
- elsődleges hivatkozások:
  - v6.1 projektterv;
  - runtime language decision gate;
  - current engine checkpoint.

### Repository meta

- `.gitignore`
- `.gitattributes`
- `.editorconfig`

Státusz:

- aktív repository meta;
- külön audit csak indokolt esetben.

### Külső tanulóprogramok

- státusz: `EXTERNAL_RESEARCH_SOURCE`
- nem részei az AETERNA GitHub repositorynak;
- helyi Codex-audit tárgyai;
- licenc-, verzió- és attributionellenőrzés szükséges;
- alapértelmezetten clean-room architektúraminta használható.

---

## 4. `Aeterna dokumentációk/`

### 4.1 Mappa szerepe

- hivatalos szabályforrások;
- aktív kártyaadatbázis;
- lookupforrás;
- projektirányító dokumentumok;
- munkafolyamat- és audit-szabványok;
- referencia- és review-anyagok.

### 4.2 Hivatalos szabályforrások

#### `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`

- státusz: `ACTIVE_CANONICAL_RULE_SOURCE`
- szerep: Core és alapjáték szabályi főforrás
- kezelés: védett

#### `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

- státusz: `ACTIVE_CANONICAL_RULE_SOURCE`
- szerep: kiegészítői szabályi főforrás
- kezelés: védett

### 4.3 Kártyaadat- és lookupforrások

#### `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`

- státusz: `ACTIVE_EDITING_SOURCE`
- canonical szerkesztési háttér: Google Sheets
- runtime közvetlen használat: kerülendő

#### `LOOKUPS.xlsx`

- státusz: `ACTIVE_EDITING_SOURCE`
- szerep: runtime lookupok és legacy alias előkészítése

### 4.4 Projektirányító dokumentumok

#### `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.1.md`

- státusz: `ACTIVE_PROJECT_GUIDANCE`
- szerep:
  - runtime-nyelvi döntési kapu prioritása;
  - Codex nélküli munkasáv;
  - döntés utáni gameplay queue;
  - M1–M9 roadmap.

#### `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`

- státusz: `SUPERSEDED_REFERENCE`
- felváltotta: v6.1

#### `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`

- státusz: `SUPERSEDED_REFERENCE`

#### `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.4.md`

- státusz: `ACTIVE_PROJECT_GUIDANCE`
- szerep: jelen dokumentum

#### `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`

- státusz: `SUPERSEDED_REFERENCE`
- felváltotta: v1.4

#### `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`

- státusz: `SUPERSEDED_REFERENCE`
- érték: részletesebb történeti fájlfelmérés

### 4.5 Aktív munkaszabványok

- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`
- `kartya_tabla_szabvany v1.2.md`

Státuszuk:

- aktív workflow- és adatszabvány;
- kártyaadat- és auditmunkánál kötelező referencia;
- engine-kódot nem írnak felül.

---

## 5. `Aeterna game engine/`

### 5.1 Mappa szerepe

Az új digitális programegység aktív helye.

Fő részei:

- `python/`
- `Godot/`
- `docs/`
- `README.md`

### 5.2 `Aeterna game engine/README.md`

- státusz: `ACTIVE_PROJECT_GUIDANCE`
- szerep: engine-szintű belépési dokumentum
- aktuális prioritás: runtime language comparison

---

## 6. `Aeterna game engine/python/`

### 6.1 Fő státusz

- `CURRENT_REFERENCE_ENGINE`
- `ACTIVE_TOOLING`

A Python ág jelenleg:

- működő rules-engine referencia;
- expected output és differential testing alap;
- AI/batch futtatási alap;
- runtime package és XLSX tooling helye;
- Python sidecar termékruntime-jelölt.

Nem jelenti automatikusan, hogy a végleges product runtime biztosan Python lesz.

### 6.2 `engine/`

- státusz: `CURRENT_REFERENCE_ENGINE`

Fő contract- és projection-modulok:

- card instance;
- zone move;
- event envelope;
- player-visible snapshot;
- Domain position;
- Domain occupancy;
- Domain board projection;
- Entity structural placement;
- episode trajectory;
- Wellspring state és resource summary.

### 6.3 `tools/ai_vs_ai/`

- státusz: `CURRENT_REFERENCE_ENGINE` / `ACTIVE_TOOLING`
- szerep:
  - state és invariánsok;
  - action flow;
  - deterministic bot policy;
  - AI-vs-AI episode runner;
  - későbbi comparison és batch alap.

### 6.4 `tools/engine/`

- státusz: `ACTIVE_TOOLING`
- szerep: minimal engine smoke és debug export

### 6.5 `tools/runtime_package/`

- státusz: `ACTIVE_TOOLING`
- szerep: package build, publish, lookup/alias reader, validáció

### 6.6 `tools/xlsx_export/`

- státusz: `ACTIVE_TOOLING`
- szerep: XLSX exporter

### 6.7 `tests/`

- státusz: `ACTIVE_TEST`

A `84a7e8f4` bázisnál:

- 59 modul izoláltan zöld;
- 333 teszt zöld.

Ismert külön probléma:

- két sorrendfüggő XLSX mock-eltérés monolitikus discoveryben.

A tesztek:

- megmaradnak;
- comparison expected output alapok;
- C# proof esetén differential reference szerepet kapnak.

### 6.8 Gameplay queue

- státusz: `QUEUED_AFTER_LANGUAGE_GATE`

Első elem:

- Wellspring production integráció.

---

## 7. `Aeterna game engine/Godot/`

### 7.1 Fő státusz

- `ACTIVE_CONSUMER`
- lehetséges C#/.NET `RUNTIME_CANDIDATE`

### 7.2 Bizonyított szerep

- runtime package loader;
- registryk;
- sample/debug contract loader;
- snapshot viewer;
- legal action debug panel;
- event log debug view;
- headless smoke tesztek;
- későbbi player UI alapja.

### 7.3 C#/.NET proof-jelölt

Vizsgálandó:

- Godot .NET projekt;
- UI-tól független C# rules library;
- ugyanazon comparison scenario;
- unit tesztek;
- JSON-contract;
- Windows export.

A C# proof még nincs implementálva.

### 7.4 Runtime package copy

- státusz: `GODOT_CONSUMPTION_COPY`
- nem canonical szerkesztési forrás
- validált Python publish pipeline frissíti

### 7.5 Sample/debug contractok

- státusz: `TEST_FIXTURE`
- loader és UI tesztelésre szolgálnak
- nem azonosak automatikusan az aktuális production engine contractokkal

---

## 8. `Aeterna game engine/docs/`

### 8.1 Elsődleges aktuális dokumentumok

#### `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

- státusz: aktív elsődleges technológiai és Codex-prioritás

#### `TECHNOLOGY_DECISIONS.md`

- státusz: aktív technológiai döntési dokumentum

#### `DECISION_MAP.md`

- státusz: aktív rövid prioritás- és döntéstérkép

#### `CURRENT_PROTOTYPE_STATUS.md`

- státusz: aktív proof- és prototípus-státusz

#### `CURRENT_OPEN_QUESTIONS.md`

- státusz: aktív közeli döntési kapu

#### `CURRENT_CONTRACT_STATUS.md`

- státusz: aktív implementációs contract-státusz

#### `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

- státusz: aktív Python reference checkpoint

#### `ARCHITECTURE.md`

- státusz: aktív contract-first réteghatár-dokumentum

### 8.2 Open Questions dokumentumpár

#### `OPEN_QUESTIONS.md`

- státusz: teljes kérdésregiszter

#### `OPEN_QUESTIONS_DECISIONS.md`

- státusz: válasz- és döntési irányok regisztere

Együtt olvasandók.

### 8.3 Hosszú formájú háttér- és tervezési dokumentumok

- `CONTRACT_SPECIFICATION.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `ABILITY_MODULE_SYSTEM.md`
- `PROTOTYPE_PLANS.md`
- `checkpoints/CHECKPOINTS.md`

Aktuális megvalósítási státuszt nem szabad kizárólag ezekből megállapítani.

---

## 9. Régi Python motor

### Státusz

- `OLD_ENGINE_REVIEW`
- `OLD_ENGINE_REFERENCE`

### Megőrzendő érték

- AI-vs-AI tapasztalat;
- balanszfigyelés;
- diagnostics és logging;
- effectlogikai előzmény;
- összevetési és migrációs forrás.

### Kezelési szabály

- nem törlendő automatikusan;
- nem bővítendő elsődleges engine-ként;
- logika csak célzott audit és új teszt után emelhető át;
- régi szabályértelmezés nem canonical.

---

## 10. Külső tanulóprogramok

### Státusz

- `EXTERNAL_RESEARCH_SOURCE`

### Kezelési szabály

- nem kerülnek automatikusan az AETERNA repositoryba;
- Codex helyileg auditálja őket;
- licenc és attribution ellenőrzendő;
- vizsgált commit/tag/verzió rögzítendő;
- alapértelmezetten clean-room architektúraminta használható;
- assetlicenc külön ellenőrizendő.

### Kiemelt kutatási irányok

- Godot RL Agents;
- Python sidecar/bridge minták;
- Godot .NET/C# rules library minták;
- py4godot;
- godot-python-extension;
- GodoPy;
- régi godot-python.

---

## 11. `Archive/`

- státusz: archív és történeti réteg
- nem aktív canonical forrás
- tartalom csak külön áttekintés után törölhető

---

## 12. Generált és ideiglenes outputok

Általános státusz:

- `GENERATED_OUTPUT`

Ide tartozhat:

- exportált JSON/JSONL/TSV;
- runtime package candidate;
- build report;
- diagnostics output;
- smoke temp;
- logok;
- debug exportok;
- későbbi comparison reportok.

Kezelési elv:

- ne váljanak canonical szerkesztési forrássá;
- pipeline-ból reprodukálhatók legyenek;
- Gitben csak indokolt fixture vagy release-reference maradjon;
- temp és cache tartalom lehetőleg ignorált legyen.

---

## 13. Jelenlegi aktív futási utak

### Python rules-engine smoke

    cd "Aeterna game engine/python"
    python tools/engine/run_minimal_engine_smoke.py --json-debug-export

### AI-vs-AI minimal episode

    python tools/ai_vs_ai/run_minimal_ai_vs_ai_episode.py --max-steps 8
    python tools/ai_vs_ai/run_minimal_ai_vs_ai_episode.py --max-steps 8 --json

### Runtime package publish

- `Aeterna game engine/python/publish_runtime_package_to_godot.bat`

### XLSX raw/debug export

- `Aeterna game engine/python/run_xlsx_export.bat`

A későbbi comparison proof új futási utakat ad:

- Python sidecar + Godot;
- Godot .NET/C# proof;
- optional GDScript proof.

---

## 14. Következő auditok és feladatok

### Codex következő prioritás

1. tanulóprogram-audit;
2. comparison fixture;
3. Python sidecar proof;
4. Godot .NET/C# proof;
5. Windows packaging;
6. döntési jelentés.

### Codex nélküli dokumentációs sáv

1. Open Questions + Decisions közös triázs;
2. tanulóprogram- és licencleltár előkészítés;
3. Ability Module System audit;
4. contract-specifikáció konszolidáció;
5. történeti checkpointok rendezése;
6. repository hivatkozások és státuszok karbantartása.

### Gameplay queue a döntés után

1. Wellspring runtime integráció;
2. player-visible Wellspring summary;
3. Beáramlás;
4. Magnitúdó és payment;
5. `play_card`.

---

## 15. Jelenlegi védett elemek

Külön döntés nélkül ne törlendő vagy mozgatható:

- két 1.4v hivatalos főforrás;
- 1.9v kártyaadatbázis;
- `LOOKUPS.xlsx`;
- v6.1 projektterv;
- v1.4 projekt-térkép;
- runtime language decision gate;
- current engine checkpoint;
- Python reference engine-kód;
- runtime package tooling;
- aktív tesztek;
- Godot loader és smoke réteg;
- archív régi engine-anyagok a felülvizsgálatuk előtt.

---

## 16. Felváltott dokumentumok kezelése

Jelenlegi felváltott dokumentumok:

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`

Státuszuk:

- `SUPERSEDED_REFERENCE`

Később külön dokumentációs rendezési commitban:

- hivatkozásellenőrzés;
- `archive_review/` alá mozgatás;
- README-k és linkek frissítése.

A jelen v1.4 létrehozása nem törli és nem mozgatja őket.

---

## 17. Rövid projekt-térkép

**Szabályforrás:** két 1.4v DOCX  
**Kártyaadat:** Google Sheets / 1.9v XLSX  
**Lookup:** `LOOKUPS.xlsx`  
**Működő engine-reference:** `Aeterna game engine/python/`  
**Fő runtime-jelölt A:** Python sidecar + Godot  
**Fő runtime-jelölt B:** Godot .NET/C#  
**Opcionális proof:** minimal GDScript  
**Runtime programadat:** validált runtime package  
**Kliens/debug:** `Aeterna game engine/Godot/`  
**Aktuális projektterv:** v6.1  
**Aktuális projekt-térkép:** v1.4  
**Aktuális engine-checkpoint:** `CURRENT_ENGINE_CHECKPOINT.md`  
**Következő Codex-feladat:** runtime language comparison  
**Gameplay queue első eleme a döntés után:** Wellspring runtime integráció  
**Régi engine:** review/reference  
**Külső tanulóprogramok:** local research sources  
**Archív:** `Archive/` és `archive_review/`
