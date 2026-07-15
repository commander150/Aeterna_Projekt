# AETERNA dokumentációk – mappaszintű rend

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Frissítve:** 2026-07-15  
**Státusz:** aktív dokumentációs mappaindex

Ez a mappa az AETERNA projekt fő dokumentációs és adatforrás-jellegű anyagait tartalmazza.

A főszint célja, hogy csak aktív vagy kiemelten fontos projektirányító források maradjanak itt. Régi auditok, felváltott tervek, generált exportok és háttéranyagok külön almappákba kerülnek vagy külön státuszt kapnak.

---

## 1. Főszinten maradhat

A fő `Aeterna dokumentációk/` szinten csak ezek a dokumentumtípusok maradjanak:

- hivatalos szabályforrások;
- aktív kártyaadatbázis- és LOOKUPS-munkaforrás;
- aktuális projektterv;
- aktuális projekt-térkép és fájlstátusz;
- aktív munkafolyamat- és adatkezelési szabványok;
- aktív Excel- és kártyatábla-szabványok;
- aktív kártyaauditálási munkarend.

---

## 2. Jelenlegi aktív és védett főszinti fájlok

### Hivatalos szabályforrások

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

### Aktív adatforrások

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`
- `LOOKUPS.xlsx`

### Aktív projektirányító dokumentumok

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.1.md`
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`

### Aktív munkaszabványok

- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`
- `kartya_tabla_szabvany v1.2.md`

---

## 3. Felváltott, de még főszinten található dokumentumok

### `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`

- státusz: `SUPERSEDED_REFERENCE`
- felváltotta: `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.1.md`
- a Python-engine fejlesztés korábbi prioritási sorrendjét őrzi;
- a Wellspringet még közvetlen következő programozási feladatként kezeli;
- az új runtime-nyelvi döntési kaput még nem tartalmazza.

### `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`

- státusz: `SUPERSEDED_REFERENCE`
- felváltotta előbb a v6.0, majd a v6.1;
- nem aktív projektirányító forrás.

### `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`

- státusz: `SUPERSEDED_REFERENCE`
- felváltotta: `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`
- értékes történeti és részletes régi motoros fájlfelmérés;
- nem tekintendő a jelenlegi repository teljes és pontos aktív térképének.

A felváltott dokumentumokat ez a frissítés nem törli és nem mozgatja.

Később külön dokumentációs rendezési commitban helyezhetők át `archive_review/` alá, minden hivatkozás ellenőrzése után.

---

## 4. Kapcsolódó aktív engine-dokumentumok

Az új rules engine technikai dokumentumai az `Aeterna game engine/docs/` alatt találhatók.

### Aktuális irány és döntési kapu

- `Aeterna game engine/docs/AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`
  - hosszú távú első játszható termékmérföldkő;
- `Aeterna game engine/docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
  - a következő elsődleges Codex-prioritás;
  - Python sidecar és Godot .NET/C# összehasonlító proof;
  - szükség esetén minimal GDScript proof;
- `Aeterna game engine/docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`
  - a működő Python engine referenciaállapota;
- `Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`
  - technológiai jelöltek és elfogadott réteghatárok;
- `Aeterna game engine/docs/DECISION_MAP.md`
  - rövid aktuális döntés- és prioritástérkép;
- `Aeterna game engine/docs/CURRENT_PROTOTYPE_STATUS.md`
  - proofok és prototípusok státusza;
- `Aeterna game engine/docs/CURRENT_CONTRACT_STATUS.md`
  - a ténylegesen implementált contractok státusza;
- `Aeterna game engine/docs/CURRENT_OPEN_QUESTIONS.md`
  - közeli döntési kapuk és blokkolók.

### Open Questions dokumentumpár

- `Aeterna game engine/docs/OPEN_QUESTIONS.md`
  - teljes történeti és hosszú távú kérdésregiszter;
- `Aeterna game engine/docs/OPEN_QUESTIONS_DECISIONS.md`
  - a kérdésekhez tartozó válasz- és döntési irányok.

A két fájl együtt olvasandó.

### Hosszú formájú háttér- és történeti dokumentumok

- `Aeterna game engine/docs/checkpoints/CHECKPOINTS.md`
- `Aeterna game engine/docs/CONTRACT_SPECIFICATION.md`
- `Aeterna game engine/docs/RUNTIME_PACKAGE_SPECIFICATION.md`
- `Aeterna game engine/docs/ABILITY_MODULE_SYSTEM.md`
- `Aeterna game engine/docs/PROTOTYPE_PLANS.md`

Dokumentumelsőbbség esetén:

1. hivatalos 1.4v főforrások;
2. v6.1 projektterv;
3. `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
4. `CURRENT_ENGINE_CHECKPOINT.md`;
5. `TECHNOLOGY_DECISIONS.md` és `DECISION_MAP.md`;
6. current status dokumentumok;
7. `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md` együtt;
8. hosszú formájú korábbi tervezési dokumentumok.

---

## 5. Almappák

### `reference/`

Nem aktív, de hasznos háttér- vagy referenciaanyagok:

- designjegyzetek;
- ötletládák;
- régi technikai referenciaanyagok;
- tesztelési workflow-dokumentumok;
- névprofil-sablonok;
- régi architektúra- vagy backend referenciaanyagok.

### `archive_review/`

Korábbi auditok, felváltott tervek, állapotjelentések és cleanup-nyomok.

Ezek nem törlendők automatikusan.

### `generated_review/`

Generált, exportált vagy gépi feldolgozásból származó review-anyagok.

Ezek nem canonical források.

### `active/`

Fenntartott mappa. A fő aktív forrásokat egyelőre nem mozgatjuk ide, mert több dokumentum és tooling útvonal alapján hivatkozik rájuk.

---

## 6. Munkaszabály

Új fájl elhelyezésekor:

1. el kell dönteni, hogy aktív forrás, referencia, auditnyom vagy generált output;
2. aktív főforrás csak indokolt esetben kerüljön főszintre;
3. átmeneti audit vagy report ne maradjon főszinten;
4. generált export ne maradjon főszinten;
5. felváltott projektirányító dokumentum kapjon explicit `SUPERSEDED_REFERENCE` státuszt;
6. törlés vagy mozgatás előtt legyen külön döntés és hivatkozásellenőrzés;
7. dokumentációs rendezés ne keveredjen runtime kódmódosítással;
8. teljes kérdésregisztert nem szabad rövidítéskor elveszíteni;
9. a napi aktív állapot külön current dokumentumban tartható;
10. tanulóprogramok vagy külső forráskódok ne kerüljenek automatikusan az AETERNA repositoryba;
11. kódátvétel előtt licenc- és attributionellenőrzés szükséges.

---

## 7. Jelenlegi státusz

A 2026-07-15-i dokumentációs frissítések eredménye:

- a v6.1 az aktív projektterv;
- a v6.0 és v5.1 felváltott referencia;
- a v1.3 az aktív projekt-térkép;
- a működő Python engine checkpointként megőrzött referencia;
- a következő Codex-prioritás a runtime-nyelvi comparison;
- a C#/.NET egyenrangú fő jelöltként bekerült;
- a Python sidecar továbbra is fő jelölt;
- GDScript csak szükség esetén kap szűk proofot;
- a Wellspring gameplay-feladat a döntési kapu után folytatandó;
- Codex nélkül dokumentációs, audit- és döntés-előkészítő munka folytatódik;
- a hivatalos főforrások és adatforrások változatlanul védettek;
- nem történt fájltörlés vagy fájlmozgatás.
