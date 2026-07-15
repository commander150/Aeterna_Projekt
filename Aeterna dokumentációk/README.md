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

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`

### Aktív munkaszabványok

- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`
- `kartya_tabla_szabvany v1.2.md`

---

## 3. Felváltott, de még főszinten található dokumentumok

### `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`

- státusz: `SUPERSEDED_REFERENCE`
- felváltotta: `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`
- nem aktív projektirányító forrás

### `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`

- státusz: `SUPERSEDED_REFERENCE`
- felváltotta: `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`
- értékes történeti és részletes régi motoros fájlfelmérés
- nem tekintendő a jelenlegi repository teljes és pontos aktív térképének

A felváltott dokumentumokat ez a frissítés nem törli és nem mozgatja.

Később külön dokumentációs rendezési commitban helyezhetők át `archive_review/` alá, minden hivatkozás ellenőrzése után.

---

## 4. Kapcsolódó aktív engine-dokumentumok

Az új rules engine technikai dokumentumai az `Aeterna game engine/docs/` alatt találhatók.

### Aktuális irány és állapot

- `Aeterna game engine/docs/AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`
  - hosszú távú első játszható termékmérföldkő;
- `Aeterna game engine/docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`
  - aktuális rules-engine folytatási pont;
- `Aeterna game engine/docs/ARCHITECTURE.md`
  - aktív Python-authoritative célarchitektúra;
- `Aeterna game engine/docs/CURRENT_CONTRACT_STATUS.md`
  - a ténylegesen implementált contractok státusza;
- `Aeterna game engine/docs/CURRENT_OPEN_QUESTIONS.md`
  - közeli engine-döntési kapuk és blokkolók.

### Hosszú formájú háttér- és történeti dokumentumok

- `Aeterna game engine/docs/checkpoints/CHECKPOINTS.md`
  - korábbi időrendi technikai checkpointok;
- `Aeterna game engine/docs/CONTRACT_SPECIFICATION.md`
  - hosszú formájú contract-tervezési háttér;
- `Aeterna game engine/docs/OPEN_QUESTIONS.md`
  - teljes történeti és hosszú távú kérdésregiszter;
- `Aeterna game engine/docs/RUNTIME_PACKAGE_SPECIFICATION.md`
  - runtime package és adatpipeline;
- `Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`
  - technológiai döntési háttér;
- `Aeterna game engine/docs/ABILITY_MODULE_SYSTEM.md`
  - későbbi ability/effect engine terve.

Dokumentumelsőbbség esetén:

1. hivatalos 1.4v főforrások;
2. v6.0 projektterv;
3. `CURRENT_ENGINE_CHECKPOINT.md`;
4. `ARCHITECTURE.md` v2.0;
5. `CURRENT_CONTRACT_STATUS.md` és `CURRENT_OPEN_QUESTIONS.md`;
6. hosszú formájú korábbi tervezési dokumentumok.

---

## 5. Almappák

### `reference/`

Ide kerülnek azok az anyagok, amelyek nem aktív főforrások, de hosszabb távon hasznos háttér- vagy referenciaanyagok.

Példák:

- designjegyzetek;
- ötletládák;
- régi technikai referenciaanyagok;
- tesztelési workflow-dokumentumok;
- névprofil-sablonok;
- régi architektúra- vagy backend referenciaanyagok.

Ezeket nem kell törölni, de nem irányíthatják felül az aktív forrásokat.

### `archive_review/`

Ide kerülnek azok az anyagok, amelyek korábbi auditok, felváltott tervek, állapotjelentések vagy cleanup-nyomok.

Példák:

- régi projekttervek;
- régi projekt-térképek;
- régi auditjelentések;
- régi exportellenőrzések;
- átmeneti README- és guidance-fájlok;
- cleanup candidate listák;
- régi backend readiness auditok;
- korábbi LOOKUPS-bővítési tervek.

Ezek nem törlendők automatikusan. Később külön archívum- vagy törlési döntéssel rendezhetők.

### `generated_review/`

Ide kerülnek generált, exportált vagy gépi feldolgozásból származó review-anyagok.

Példák:

- TSV exportok;
- generált LOOKUPS-oszlopkimenetek;
- régi exportcsomagok;
- ideiglenes gépi outputok.

Ezek nem canonical források. Feladatuk az ellenőrzés, összevetés és későbbi audit.

### `active/`

Ez a mappa továbbra is fenntartott, de a fő aktív forrásokat egyelőre nem mozgatjuk ide.

Ennek oka:

- több dokumentum és tooling még név vagy útvonal alapján hivatkozik a főszinti fájlokra;
- a hivatalos szabályforrások és adatforrások mozgatása csak hivatkozásfrissítési tervvel történhet;
- a főszint jelenleg maga tölti be az aktív források szerepét.

---

## 6. Munkaszabály

Új fájl elhelyezésekor:

1. először el kell dönteni, hogy aktív forrás, referencia, auditnyom vagy generált output;
2. aktív főforrás csak indokolt esetben kerüljön főszintre;
3. átmeneti audit vagy report ne maradjon főszinten;
4. generált export ne maradjon főszinten;
5. felváltott projektirányító dokumentum kapjon explicit `SUPERSEDED_REFERENCE` státuszt;
6. törlés vagy mozgatás előtt mindig legyen külön döntés és hivatkozásellenőrzés;
7. dokumentációs rendezés ne keveredjen runtime kódmódosítással;
8. teljes kérdésregisztert nem szabad rövidítéskor elveszíteni;
9. a napi aktív állapot külön current dokumentumban tartható, a hosszú háttéranyag megőrzése mellett.

---

## 7. Jelenlegi státusz

Az `Aeterna dokumentációk/` első mappatisztítási köre lezárult.

A 2026-07-15-i dokumentációs frissítések eredménye:

- a v6.0 az aktív projektterv;
- a v1.3 az aktív projekt-térkép;
- a v5.1 és v1.2 felváltott referencia;
- az aktuális rules-engine checkpoint külön engine-dokumentumban rögzített;
- elkészült az aktív architecture v2.0;
- elkészült a current contract-státusz;
- elkészült a current döntési kapu-lista;
- a teljes régi contract- és kérdésanyag megmaradt;
- a hivatalos főforrások és adatforrások változatlanul védettek;
- nem történt fájltörlés vagy fájlmozgatás.
