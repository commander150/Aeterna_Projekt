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
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`

### Aktív munkaszabványok

- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`
- `kartya_tabla_szabvany v1.2.md`

---

## 3. Felváltott, de még főszinten található dokumentum

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`
  - státusz: `SUPERSEDED_REFERENCE`
  - felváltotta: `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`
  - nem aktív projektirányító forrás;
  - később külön dokumentációs rendezési commitban helyezhető át `archive_review/` alá;
  - addig sem szabad a v6.0 helyett döntési alapként használni.

A felváltott dokumentumot ez a frissítés nem törli és nem mozgatja.

---

## 4. Kapcsolódó aktív engine-dokumentumok

Az új rules engine technikai dokumentumai nem ebben a mappában, hanem az `Aeterna game engine/docs/` alatt találhatók.

Kiemelten fontos:

- `Aeterna game engine/docs/AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`
  - hosszú távú első játszható termékmérföldkő;
- `Aeterna game engine/docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`
  - aktuális rules-engine folytatási pont;
- `Aeterna game engine/docs/checkpoints/CHECKPOINTS.md`
  - korábbi időrendi technikai checkpointok;
- `Aeterna game engine/docs/ARCHITECTURE.md`
  - célarchitektúra;
- `Aeterna game engine/docs/CONTRACT_SPECIFICATION.md`
  - contract-specifikáció;
- `Aeterna game engine/docs/OPEN_QUESTIONS.md`
  - nyitott kérdések és döntési kapuk.

Dokumentumelsőbbség esetén az aktív v6.0 projektterv és a `CURRENT_ENGINE_CHECKPOINT.md` a korábbi engine-terveknél frissebb státuszforrás.

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
7. dokumentációs rendezés ne keveredjen runtime kódmódosítással.

---

## 7. Jelenlegi státusz

Az `Aeterna dokumentációk/` első mappatisztítási köre lezárult.

A 2026-07-15-i frissítés eredménye:

- a v6.0 az aktív projektterv;
- a v5.1 felváltott referencia;
- az aktuális rules-engine checkpoint külön engine-dokumentumban rögzített;
- a hivatalos főforrások és adatforrások változatlanul védettek;
- nem történt fájltörlés vagy fájlmozgatás.
