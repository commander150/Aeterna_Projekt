# AETERNA – Projekt Térkép és Fájlstátusz v1.3

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.3  
**Dátum:** 2026-07-15  
**Státusz:** aktív magas szintű projekt- és fájlstátusz-térkép  
**Felváltott dokumentum:** `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`

Ez a dokumentum az AETERNA repository jelenlegi fő mappáit, aktív forrásait, technikai rétegeit és fájlstátuszait rögzíti.

Nem teljes fájlonkénti inventár, nem törlési lista és nem refaktor-parancs.

Feladata:

- az aktív, generált, referencia-, review- és archív rétegek elhatárolása;
- a jelenlegi authoritative fejlesztési út megmutatása;
- a régi Python motor és az új rules engine szétválasztása;
- a dokumentációs és technikai elsőbbség rögzítése;
- későbbi részletes mappaauditok alapjának biztosítása.

---

## 1. Aktuális projektkép

A repository fő rendszerrétegei:

1. hivatalos szabályforrások;
2. kártyaadatbázis és LOOKUPS;
3. új Python rules engine;
4. runtime package és exportpipeline;
5. Godot fogyasztói és későbbi kliensréteg;
6. régi Python motor referenciaágként;
7. dokumentáció és audit;
8. archív és generált anyagok.

Az elsődleges programozási irány:

- `Aeterna game engine/python/` determinisztikus rules engine.

Az elsődleges projektterv:

- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`.

Az aktuális engine-checkpoint:

- `Aeterna game engine/docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`.

---

## 2. Státuszszótár

| Státusz | Jelentés |
|---|---|
| `ACTIVE_CANONICAL_RULE_SOURCE` | Elsődleges hivatalos szabályforrás. |
| `ACTIVE_EDITING_SOURCE` | Ember által aktívan szerkesztett adatforrás. |
| `ACTIVE_PROJECT_GUIDANCE` | Aktív projektirányító dokumentum. |
| `ACTIVE_ENGINE_SOURCE` | Aktív authoritative engine-kód. |
| `ACTIVE_TOOLING` | Aktív export-, build- vagy validációs eszköz. |
| `ACTIVE_TEST` | Aktív regressziós vagy smoke teszt. |
| `ACTIVE_CONSUMER` | Aktív fogyasztói, loader- vagy kliensréteg. |
| `GENERATED_OUTPUT` | Regenerálható kimenet, nem canonical szerkesztési forrás. |
| `TEST_FIXTURE` | Teszt- vagy debugfixture. |
| `SUPERSEDED_REFERENCE` | Újabb dokumentum által felváltott, megőrzött referencia. |
| `OLD_ENGINE_REVIEW` | Régi motorhoz tartozó, áttekintendő kód vagy dokumentum. |
| `OLD_ENGINE_REFERENCE` | Megőrzendő régi motoros háttérforrás. |
| `ARCHIVE_REVIEW` | Archívum- vagy törlési döntés előtt felülvizsgálandó. |
| `PROTECTED_DO_NOT_MOVE` | Hivatkozások miatt jelenleg nem mozgatható biztonságosan. |

---

## 3. Gyökérszint

### `README.md`

- státusz: `ACTIVE_PROJECT_GUIDANCE`
- szerep: repository-szintű rövid projektkép és belépési pont
- frissítve: 2026-07-15
- elsődleges hivatkozások: v6.0 projektterv, current engine checkpoint

### `.gitignore`, `.gitattributes`, `.editorconfig`

- státusz: aktív repository meta
- runtime szerep: közvetlenül nincs
- kezelési irány: maradjanak, külön repository-meta audit csak indokolt esetben

### Egyéb régi gyökérszintű fájlok

A v1.2 dokumentumban részletesen felsorolt régi DOCX-, XLSX-, log-, report- és motorfájlok közül több időközben áthelyezésre vagy archiválásra kerülhetett.

A v1.2 ezért történeti fájlszintű referencia marad, de nem tekinthető a jelenlegi könyvtárstruktúra teljes és pontos listájának.

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
- kezelés: védett, nem mozgatható vagy konvertálható külön döntés nélkül

#### `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

- státusz: `ACTIVE_CANONICAL_RULE_SOURCE`
- szerep: kiegészítői szabályi főforrás
- kezelés: védett

### 4.3 Kártyaadat- és lookupforrások

#### `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`

- státusz: `ACTIVE_EDITING_SOURCE`
- szerep: kártya- és decklista-munkaforrás helyi példánya
- canonical szerkesztési háttér: Google Sheets
- runtime közvetlen használat: kerülendő; export és runtime package közvetítsen

#### `LOOKUPS.xlsx`

- státusz: `ACTIVE_EDITING_SOURCE`
- szerep: runtime lookupok és legacy alias előkészítése
- aktív sheetek: többek között `RUNTIME_CORE`, `RUNTIME_ABILITY`
- `RUNTIME_LEGACY_ALIAS`: előkészített, még nem teljes runtime output

### 4.4 Projektirányító dokumentumok

#### `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`

- státusz: `ACTIVE_PROJECT_GUIDANCE`
- szerep: jelenlegi prioritások, M1–M9 roadmap és következő engine-lánc

#### `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`

- státusz: `SUPERSEDED_REFERENCE`
- felváltotta: v6.0
- később `archive_review/` alá mozgatható külön commitban

#### `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`

- státusz: `ACTIVE_PROJECT_GUIDANCE`
- szerep: jelen dokumentum

#### `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`

- státusz: `SUPERSEDED_REFERENCE`
- érték: részletesebb történeti fájlfelmérés, főleg a régi motor korszakáról

### 4.5 Aktív munkaszabványok

- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`
- `kartya_tabla_szabvany v1.2.md`

Státuszuk:

- aktív workflow- és adatszabvány;
- engine-kódot nem írnak felül;
- kártyaadat- és auditmunkánál kötelező referenciák.

### 4.6 Almappák

#### `reference/`

- státusz: referenciaanyagok
- nem aktív canonical forrás

#### `archive_review/`

- státusz: `ARCHIVE_REVIEW`
- régi tervek, auditok és cleanup-nyomok
- automatikusan nem törlendő

#### `generated_review/`

- státusz: `GENERATED_OUTPUT` / review
- generált exportok és összevetési anyagok

#### `active/`

- fenntartott mappa
- a fő aktív források jelenleg továbbra is főszinten maradnak a hivatkozások miatt

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
- frissítve: current Python rules engine állapotra

---

## 6. `Aeterna game engine/python/`

### 6.1 Fő státusz

- státusz: `ACTIVE_ENGINE_SOURCE` és `ACTIVE_TOOLING`
- elsődleges authoritative rules-engine hely
- emellett runtime package és XLSX tooling helye

### 6.2 `engine/`

- státusz: `ACTIVE_ENGINE_SOURCE`

Jelenlegi fő contract- és projection-modulok többek között:

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

Kezelési irány:

- kis, contract-first commitok;
- schema-migráció csak explicit feladatban;
- player-visible és internal state elválasztása.

### 6.3 `tools/ai_vs_ai/`

- státusz: `ACTIVE_ENGINE_SOURCE`

Szerepe:

- minimal MatchState és PlayerState;
- rules kernel;
- state invariánsok;
- action request és legal-action flow;
- deterministic bot policy;
- AI-vs-AI episode runner.

Nem azonos a régi Python szimulációs motorral.

### 6.4 `tools/engine/`

- státusz: `ACTIVE_TOOLING`
- szerep: minimal engine smoke és debug export

### 6.5 `tools/runtime_package/`

- státusz: `ACTIVE_TOOLING`
- szerep: package build, publish, lookup és alias reader, validáció

### 6.6 `tools/xlsx_export/`

- státusz: `ACTIVE_TOOLING`
- szerep: új helyre migrált XLSX exporter

### 6.7 `tests/`

- státusz: `ACTIVE_TEST`

A `84a7e8f4` bázisnál:

- 59 modul izoláltan zöld;
- 333 teszt zöld.

Ismert külön probléma:

- két sorrendfüggő XLSX mock-eltérés monolitikus discoveryben.

A tesztmappa későbbi szerkezeti rendezése csak read-only audit után induljon.

### 6.8 Runtime package fixture/output mappák

- Python fixture package: `TEST_FIXTURE` / `GENERATED_OUTPUT`
- nem canonical szerkesztési forrás
- kézi tartalmi szerkesztés kerülendő

### 6.9 Legacy `main.py` és régi motor-maradványok

- státusz: `OLD_ENGINE_REVIEW`
- történeti okból maradhatnak az új engine Python mappájában
- nem az új authoritative rules engine végleges entrypointjai
- később külön mappaaudit és elhatárolás szükséges

---

## 7. `Aeterna game engine/Godot/`

### 7.1 Fő státusz

- státusz: `ACTIVE_CONSUMER`
- nem authoritative szabálymotor

### 7.2 Jelenlegi szerep

- runtime package loader;
- registry-k;
- sample/debug contract loader;
- snapshot viewer;
- legal action debug panel;
- event log debug view;
- headless smoke tesztek;
- későbbi player UI alapja.

### 7.3 Runtime package copy

- státusz: `GODOT_CONSUMPTION_COPY`
- nem canonical szerkesztési forrás
- validált Python publish pipeline frissíti

### 7.4 Sample/debug contractok

- státusz: `TEST_FIXTURE`
- loader és UI tesztelésre szolgálnak
- nem azonosak automatikusan az új Python rules engine aktív contractjaival

---

## 8. `Aeterna game engine/docs/`

### 8.1 Aktív jelenlegi dokumentumok

#### `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

- státusz: aktív hosszú távú termékcél

#### `ARCHITECTURE.md`

- státusz: aktív célarchitektúra v2.0

#### `CURRENT_CONTRACT_STATUS.md`

- státusz: aktív implementációs contract-státusz

#### `CURRENT_OPEN_QUESTIONS.md`

- státusz: aktív közeli döntési kapu

#### `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

- státusz: aktív gördülő technikai folytatási pont

### 8.2 Hosszú formájú háttér- és tervezési dokumentumok

#### `CONTRACT_SPECIFICATION.md`

- státusz: aktív hosszú formájú tervezési referencia
- megjegyzés: több tervezett és részben elavult szakaszt tartalmaz; az aktuális megvalósítást a `CURRENT_CONTRACT_STATUS.md` mutatja

#### `OPEN_QUESTIONS.md`

- státusz: aktív teljes kérdésregiszter
- napi prioritási használat: `CURRENT_OPEN_QUESTIONS.md`

#### `CHECKPOINTS.md`

- státusz: történeti checkpointnapló
- aktuális állapot: `CURRENT_ENGINE_CHECKPOINT.md`

#### `RUNTIME_PACKAGE_SPECIFICATION.md`

- státusz: aktív adatpipeline-specifikáció

#### `TECHNOLOGY_DECISIONS.md`

- státusz: frissítendő hosszú formájú technológiai háttér
- jelenlegi döntés: Python authoritative engine, Godot kliensréteg

#### `ABILITY_MODULE_SYSTEM.md`

- státusz: tervezett későbbi engine-réteg

#### `PROTOTYPE_PLANS.md`

- státusz: részben történeti, frissítendő

---

## 9. Régi Python motor

### 9.1 Státusz

- `OLD_ENGINE_REVIEW`
- `OLD_ENGINE_REFERENCE`

### 9.2 Megőrzendő érték

- AI-vs-AI tapasztalat;
- balanszfigyelés;
- diagnostics és logging;
- effectlogikai előzmény;
- összevetési és migrációs forrás.

### 9.3 Kezelési szabály

- nem törlendő automatikusan;
- nem bővítendő elsődleges engine-ként;
- logika csak célzott audit és új contractba illesztés után emelhető át;
- régi szabályértelmezés nem tekinthető canonicalnak.

---

## 10. `Archive/`

- státusz: archív és történeti réteg
- nem aktív canonical forrás
- tartalom csak külön áttekintés után törölhető
- régi engine-checkpointok, mappaképek és másolatok megőrzési helye lehet

---

## 11. Generált és ideiglenes outputok

Általános státusz:

- `GENERATED_OUTPUT`

Ide tartozhat:

- exportált JSON/JSONL/TSV;
- runtime package candidate;
- build report;
- diagnostics output;
- smoke temp;
- logok;
- debug exportok.

Kezelési elv:

- ne váljanak canonical szerkesztési forrássá;
- pipeline-ból reprodukálhatók legyenek;
- Gitben csak indokolt fixture vagy release-reference maradjon;
- temp és cache tartalom lehetőleg ignorált legyen.

---

## 12. Jelenlegi aktív futási utak

### 12.1 Rules engine smoke

    cd "Aeterna game engine/python"
    python tools/engine/run_minimal_engine_smoke.py --json-debug-export

### 12.2 AI-vs-AI minimal episode

    python tools/ai_vs_ai/run_minimal_ai_vs_ai_episode.py --max-steps 8
    python tools/ai_vs_ai/run_minimal_ai_vs_ai_episode.py --max-steps 8 --json

### 12.3 Runtime package publish

- `Aeterna game engine/python/publish_runtime_package_to_godot.bat`

### 12.4 XLSX raw/debug export

- `Aeterna game engine/python/run_xlsx_export.bat`

A rules engine smoke és a runtime package publish külön technikai út; egyik sem helyettesíti a másikat.

---

## 13. Következő mappaszintű auditok

Javasolt sorrend:

1. `Aeterna game engine/docs/` hosszú dokumentumainak státusza;
2. `Aeterna game engine/python/` legacy és új engine kódjának fizikai elhatárolása;
3. `tests/` read-only szerkezeti audit;
4. generált package és debug fixture mappák;
5. régi `XLSX export/` aktív státuszának végleges lezárása;
6. root és `Archive/` régi motoros anyagai.

Egy audit ne járjon automatikus törléssel vagy tömeges mozgatással.

---

## 14. Jelenlegi védett elemek

Külön döntés nélkül ne törlendő vagy mozgatható:

- két 1.4v hivatalos főforrás;
- 1.9v kártyaadatbázis;
- `LOOKUPS.xlsx`;
- v6.0 projektterv;
- current engine checkpoint;
- aktív Python engine-kód;
- runtime package tooling;
- aktív tesztek;
- Godot loader és smoke réteg;
- archív régi engine-anyagok a felülvizsgálatuk előtt.

---

## 15. Felváltott dokumentumok kezelése

Jelenlegi felváltott dokumentumok:

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`

Státuszuk:

- `SUPERSEDED_REFERENCE`

Később egy külön dokumentációs rendezési commitban:

- hivatkozásellenőrzés;
- `archive_review/` alá mozgatás;
- README-k és linkek frissítése.

A jelen v1.3 létrehozása nem törli és nem mozgatja őket.

---

## 16. Rövid projekt-térkép

**Szabályforrás:** két 1.4v DOCX  
**Kártyaadat:** Google Sheets / 1.9v XLSX  
**Lookup:** `LOOKUPS.xlsx`  
**Authoritative engine:** `Aeterna game engine/python/`  
**Runtime programadat:** validált runtime package  
**Kliens/debug:** `Aeterna game engine/Godot/`  
**Aktuális projektterv:** v6.0  
**Aktuális engine-checkpoint:** `CURRENT_ENGINE_CHECKPOINT.md`  
**Régi engine:** review/reference  
**Archív:** `Archive/` és `archive_review/`  
**Következő technikai feladat:** Wellspring runtime integráció
