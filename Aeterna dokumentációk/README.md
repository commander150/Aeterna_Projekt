# AETERNA dokumentációk – mappaszintű index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.0  
**Dátum:** 2026-07-21  
**Státusz:** aktív dokumentációs mappaindex  
**Aktuális repository HEAD:** `32a0cbea24c82dda440f1a053b454ef03949d8ae` – `docs update 2`

Ez a mappa az AETERNA projekt hivatalos szabály-, adat-, projektirányítási és munkafolyamat-dokumentumainak elsődleges helye.

A főszinten csak aktív vagy védett dokumentum maradhat. Felváltott terv, régi projekt-térkép, generált export, átmeneti audit és történeti háttéranyag nem maradhat tartós párhuzamos aktív forrásként.

---

## 1. Főszinten megtartandó aktív fájlok

### Hivatalos szabályforrások

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`;
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`.

Státusz:

- `ACTIVE_CANONICAL_RULE_SOURCE`;
- védett;
- formátumváltás vagy tartalmi módosítás csak külön döntéssel.

### Aktív adatforrások

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `LOOKUPS.xlsx`.

Státusz:

- `ACTIVE_EDITING_SOURCE`;
- a fő szerkesztési háttér Google Sheets;
- a program közvetlenül ne az XLSX-et fogyassza, hanem validált runtime package-et.

### Aktív projektirányító dokumentumok

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`;
- jelen `README.md`.

### Aktív munkaszabványok

- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`;
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`;
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`;
- `kartya_tabla_szabvany v1.2.md`.

Ezek kártyaadat- és auditmunkánál kötelező referenciák, de nem írják felül az engine- vagy szabályforrást.

---

## 2. Főszintről eltávolítandó felváltott verziók

A v6.2 és v1.5 sikeres beillesztése, valamint a hivatkozások ellenőrzése után eltávolítandó:

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.1.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.4.md`;
- `DOCUMENTATION_CLEANUP_CHECKPOINT_2026-07-03.md`.

A Git-történet ezeket megőrzi. Külön archívmásolat csak akkor indokolt, ha a repositorytörténettől független offline archívum készül.

A dátumozott cleanup checkpoint külön aktív fájlként szintén nem marad szükséges: az érvényes tartalma a v1.5 projekt-térképbe, a jelen mappaindexbe és az engine-checkpointba került.

A v1.4 különösen nem maradhat aktív, mert:

- nyitottként kezeli a már lezárt runtime-döntést;
- v6.1-re és `CURRENT_*` fájlokra hivatkozik;
- a fájl tartalma a Python engine-rész közepén megszakad.

---

## 3. Almappák

### `reference/`

Nem canonical, de hasznos háttéranyag:

- kártyatervezési katalógus;
- ötletláda;
- névprofil-sablon;
- régi architektúra- és workflow-referenciák;
- tanulságok és kutatási anyagok.

A reference fájl nem írhat felül aktív főforrást.

### `archive_review/`

Felváltott auditok, régi tervek és cleanup-nyomok.

Kezelés:

- automatikusan nem törlendő;
- tartalmi audit után összevonható vagy eltávolítható;
- aktív hivatkozás nem mutathat ide elsődleges forrásként.

### `generated_review/`

Regenerálható review- és exportanyag.

Kezelés:

- nem canonical;
- kézzel nem szerkesztendő;
- generált mappanevek, például `Új mappa`, későbbi külön cleanupot igényelnek;
- csak szükséges fixture vagy ellenőrzési output maradjon verziókezelésben.

### `active/`

Fenntartott mappa. A fő aktív források jelenleg főszinten maradnak, amíg a hivatkozások és tooling útvonalak rendezése be nem fejeződik.

---

## 4. Kapcsolódó engine-dokumentáció

Aktív engine-index:

- `../Aeterna game engine/README.md`;
- `../Aeterna game engine/docs/README.md`.

Aktív technikai folytatási pont:

- `../Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`.

Aktív architektúra és döntések:

- `../Aeterna game engine/docs/ARCHITECTURE.md`;
- `../Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`;
- `../Aeterna game engine/docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `../Aeterna game engine/docs/DECISION_MAP.md`.

Aktív státuszok:

- `../Aeterna game engine/docs/PROTOTYPE_STATUS.md`;
- `../Aeterna game engine/docs/RUNTIME_PACKAGE_STATUS.md`;
- `../Aeterna game engine/docs/CONTRACT_STATUS.md`.

Open Questions:

- `../Aeterna game engine/docs/OPEN_QUESTIONS.md`;
- `../Aeterna game engine/docs/OPEN_QUESTIONS_DECISIONS.md`.

A korábbi `CURRENT_*` fájlok a kijelölt utódok ellenőrzése után eltávolítandók.

---

## 5. Dokumentumnév- és verziószabály

- Aktív, stabil szerepű engine-dokumentum lehet verziószám nélküli fájlnévvel, de a dokumentum belsejében kötelező a verzió.
- Projektterv és projekt-térkép verziója a fájlnévben is szerepelhet, mert egymást követő projektirányítási kiadásokat jelöl.
- `CURRENT_` előtag nem használható, ha nincs külön, indokolt párfájl.
- A `frissitett`, `new`, `final`, `copy`, `másolat` vagy hasonló állapotjelző nem lehet tartós fájlnév része.
- Az újabb verzió kijelöli a felváltott elődöt.
- Felváltott verzió nem marad aktív főszinten csak azért, mert történeti értéke van; erre a Git-történet vagy az `archive_review/` szolgál.
- Minden aktív Markdown-dokumentumban legyen verzió, dátum és státusz.

---

## 6. Aktuális cleanup-szakasz

Elkészült:

- engine-dokumentáció első konszolidációja;
- `CURRENT_OPEN_QUESTIONS.md` beolvasztása;
- C# runtime-döntés átvezetése;
- új státuszdokumentumok;
- aktív checkpoint-utód;
- project-map v1.5 cleanup-terv.

Következik:

1. a projekt-térkép v1.5 és a jelen README beillesztése;
2. régi projekttervek és projekt-térképek eltávolítása;
3. engine `CURRENT_*` elődök eltávolítása;
4. checkpointduplikációk megszüntetése;
5. gyökérszintű elavult engine-összefoglalók eltávolítása;
6. teljes hivatkozás- és verzióaudit;
7. `reference/`, `archive_review/` és `generated_review/` külön tartalmi auditja;
8. végső keresztmappa-ellenőrzés.

A teljes fájlstátusz- és törlési térkép:

- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`.
