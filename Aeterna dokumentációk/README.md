# AETERNA dokumentációk – mappaszintű index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.3
**Dátum:** 2026-08-16
**Státusz:** aktív dokumentációs mappaindex
**Felváltott dokumentum:** `README.md` 2.2
**Szinkronizációs repository-bázis:** `14e315d3f04f5baddb547dcb767c8b156b02551f`
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95`
**Kapcsolódó fájlstátusz-térkép:** `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.9.md`

Ez a mappa az AETERNA projekt hivatalos szabály-, adat-, projektirányítási és munkafolyamat-dokumentumainak elsődleges helye.

A főszinten csak aktív, védett vagy közvetlenül a jelenlegi munkafolyamatot irányító dokumentum maradhat. Felváltott vagy történeti tartalom nem maradhat párhuzamos aktív igazságforrásként.

---

## 1. Főszinten megtartandó aktív fájlok

### 1.1 Hivatalos szabályforrások

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4.3v.docx`;
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`.

Státusz: `ACTIVE_CANONICAL_RULE_SOURCE`

Védett dokumentumok; tartalmi módosítás csak külön emberi döntéssel.

### 1.2 Aktív adatforrások

Szerkesztési/munkaforrás:

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `LOOKUPS.xlsx`.

Programfogyasztási/canonical adatút részei:

- `CARDDATABASE.xlsx`;
- `REGISTRY.xlsx`;
- canonical workbook export;
- runtime package.

A program validált runtime/canonical adatot fogyaszt; a programkimenet nem válik automatikusan szerkesztési authorityvé.

### 1.3 Aktív projektirányító dokumentumok

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.6.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.9.md`;
- jelen `README.md`;
- `../Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`.

### 1.4 Aktív munkaszabványok

- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`;
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`;
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`;
- `kartya_tabla_szabvany v1.2.md`.

Ezek munkaszabványok, nem hivatalos játékszabályforrások.

### 1.5 Aktuális adataudit

- `AETERNA – KÁRTYAADATBÁZIS AKTUÁLIS ADATAUDIT 1.0.md`.

Státusz: `ACTIVE_DATA_AUDIT`

---

## 2. Archiválási alapelv

Egy fájl csak akkor kerülhet ki az aktív helyéről, ha:

1. tartalmát átvizsgáltuk;
2. kijelöltük az aktív utódot vagy beolvasztási célt;
3. ellenőriztük, hogy fontos nyitott kérdés, döntés vagy történeti adat nem vész el;
4. kijelöltük az archív célútvonalat;
5. átvezettük az aktív hivatkozásokat;
6. ellenőriztük a Git diffet és a régi fájlnévre mutató hivatkozásokat.

Az archív példány nem aktív authority.

---

## 3. Projektterv- és projekt-térkép verziók

Aktív:

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.6.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.9.md`.

A felváltott verziók az archív projekt-guidance rétegbe kerülnek.

---

## 4. `reference/`

A `reference/` mappa nem canonical, de hasznos karbantartható háttér- és munkaforrásokat tartalmazhat.

Fontos reference fájlok többek között:

- `AETERNA – KÁRTYATERVEZÉSI KATALÓGUS ÉS HASZNÁLHATÓ ELEMEK 1.1v.md`;
- `AETERNA – ÖTLETLÁDA ÉS NYITOTT TERVEK 1.1v.md`;
- `Általános névprofil-sablon.md`;
- `GITHUB_MUNKAREND_ES_COMMIT_SZABALYOK.md`;
- `TESZTPROGRAM_WORKFLOW_ES_TESZTPROFILOK.md`;
- `ujratervezés/Master Duel  Hearthstone tanulságok v0.1.md`.

Reference dokumentum nem írhat felül hivatalos főforrást és nem válik automatikusan elfogadott döntéssé.

Régi Python motor-, backend-, effect-, trigger- és redesign-anyagok történeti/archív státuszban maradnak.

---

## 5. Korábbi review- és generated réteg

A korábbi `archive_review/` és `generated_review/` auditja és rendezése elkészült.

A régi kártyaadat/LOOKUPS auditok, Python-backend dokumentumok és generált `cards.xlsx` exportbatch történeti archív rétegben maradnak.

Generált output:

- nem canonical;
- nem kézzel szerkesztendő;
- csak azonosítható forrással és reprodukálható generálási leírással tartható meg.

---

## 6. `active/`

Fenntartott mappa.

Nem kell automatikusan minden aktív dokumentumot ide mozgatni. A fő aktív dokumentumok addig maradhatnak a dokumentációs főszinten, amíg a hivatkozások és tooling ezt indokolják.

---

## 7. Kapcsolódó engine-dokumentáció

Engine-index:

- `../Aeterna game engine/README.md`;
- `../Aeterna game engine/docs/README.md`.

Technikai folytatás:

- `../Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`.

Architektúra és döntések:

- `../Aeterna game engine/docs/ARCHITECTURE.md`;
- `../Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`;
- `../Aeterna game engine/docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `../Aeterna game engine/docs/DECISION_MAP.md`.

Aktív státusz:

- `../Aeterna game engine/docs/PROTOTYPE_STATUS.md`;
- `../Aeterna game engine/docs/RUNTIME_PACKAGE_STATUS.md`;
- `../Aeterna game engine/docs/CONTRACT_STATUS.md`.

Open Questions:

- `../Aeterna game engine/docs/OPEN_QUESTIONS.md`;
- `../Aeterna game engine/docs/OPEN_QUESTIONS_DECISIONS.md`.

A `CURRENT_*` elődök nem aktív authority-k.

---

## 8. Aktuális engine- és projektállapot

Ellenőrzött production mérföldkő:

`2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

Az előző C.5B foundation óta elkészült többek között:

- Wellspring;
- Beáramlás;
- Magnitúdó/Aura preflight;
- Domain és `play_card`;
- canonical ability/effect runtime foundation;
- damage/vitals;
- modifier/keyword/duration;
- draw/reference runtime;
- explicit öt-fázisú authoritative turn lifecycle.

A régi Wellspring-first fejlesztési sor már történeti.

Learning/OQ current: `59/58/30`; synthesis/blueprint committed; OQ `50/17/7/0`.

Következő engine-fókusz:

`Reaction / Priority Foundation v1` minimal contract finalizálása. A source/OQ/research előkészítés kész.

---

## 9. Dokumentumnév- és verziószabály

- Stabil szerepű engine-dokumentum fájlneve lehet verziószám nélküli, de belső verzióblokk kötelező.
- Projektterv és projekt-térkép verziója a fájlnévben is szerepel.
- `CURRENT_`, `new`, `final`, `copy`, `másolat` nem maradhat indokolatlan tartós aktív név.
- Az újabb verzió nevezze meg a felváltott elődöt.
- Felváltott verzió ne maradjon párhuzamos aktív authority.
- Minden aktív Markdown-dokumentumban legyen verzió, dátum és státusz.

---

## 10. Dokumentációs állapot

A nagy archiválási és cleanup-szakasz: `COMPLETE`.

A `2608345b...` production mérföldkőhöz tartozó célzott aktív A+B dokumentációs consistency pass tartalmilag lezárult.

A továbbiakban nem indul új tömeges cleanup.

Frissítendő csak az, ami:

- későbbi technikai mérföldkő miatt ténylegesen elavul;
- rossz aktuális állapotot közöl;
- authority- vagy contractváltozást követ;
- közvetlenül érintett státusz- vagy irányító dokumentum.

## 11. Visszaellenőrzési minimum

Dokumentációs frissítés lezárása előtt ellenőrizni kell:

1. projektterv/projekt-térkép/checkpoint összhang;
2. hivatalos 1.4.3v hivatkozások;
3. elavult v6.5/v1.8 vagy régebbi „aktuális” hivatkozások;
4. Wellspring-first stale roadmapok;
5. `CURRENT_*` authority-hivatkozások;
6. archív fájl aktívként hivatkozása;
7. generált output canonicalként hivatkozása;
8. Git diff és stage-scope;
9. TEMP/build/cache kizárása.
