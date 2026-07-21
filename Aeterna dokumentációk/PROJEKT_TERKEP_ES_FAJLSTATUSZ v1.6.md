# AETERNA – Projekt Térkép és Fájlstátusz v1.6

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.6  
**Dátum:** 2026-07-21  
**Státusz:** commitra előkészített aktív utód és archiválási térkép  
**Felváltott dokumentum:** `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`  
**Aktuális repository HEAD:** `ccfd3dc05a0cf16409aeb27c91333fe41d9633cc` – `docs update 3`  
**Aktuális C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Ez a dokumentum az AETERNA repository fő rendszerrétegeit, aktív forrásait, dokumentumstátuszait, valamint az aktív helyről archívumba mozgatandó elődöket és generált batch-eket rögzíti.

A v1.6 fő változásai:

- a korábbi „törlés” megfogalmazás archiválási szabályra javítása;
- a `reference/` első tartalmi auditjának átvezetése;
- az `archive_review/` jelenlegi dokumentumainak pontos besorolása;
- a `generated_review/Új mappa` teljes generált batch-ének azonosítása;
- a négy 1.8v adataudit és LOOKUPS-terv aktív utódjának kijelölése;
- a régi Python-backend dokumentumok lezárt történeti státuszának rögzítése;
- a generált batch archiválási célútvonalának kijelölése;
- a végső dokumentációs ellenőrzés sorrendjének pontosítása.

Ez nem teljes, minden forráskódot és buildartifactot felsoroló technikai inventár. A dokumentációs, adatforrás- és archív réteg döntési térképe.

---

## 1. Alapvető archiválási szabály

Az aktív helyről kikerülő fájlok nem véglegesen törlendők.

Kötelező folyamat:

1. a fájl tartalmának és hivatkozásainak ellenőrzése;
2. aktív utód vagy beolvasztási cél kijelölése;
3. tartalomvesztés-ellenőrzés;
4. archiválási célútvonal kijelölése;
5. fájl mozgatása az `Archive/` megfelelő részébe;
6. aktív hivatkozások átvezetése;
7. Git diff és repository-keresés;
8. csak ezután tekinthető lezártnak az előd aktív szerepe.

A Git-történet további történeti biztonságot ad, de nem helyettesíti az explicit archívumot, ha a projekt külön archiválási példányt kíván megőrizni.

---

## 2. Aktuális projektkép

A repository fő rétegei:

1. hivatalos szabályforrások;
2. kártyaadatbázis és LOOKUPS;
3. Python adatpipeline és runtime package tooling;
4. Python minimal rules-engine referencia;
5. Godot loader-, debug- és vizuális kliensréteg;
6. elfogadott C# in-process runtime proof;
7. tervezett production C# authoritative engine;
8. runtime comparison fixture és regressziós artifactok;
9. dokumentáció, audit és kártyatervezés;
10. régi motorok és történeti archívum;
11. regenerálható review-, export- és buildoutputok.

Elfogadott szerepfelosztás:

- **Godot / GDScript:** vizuális kliens;
- **C# / .NET:** egyetlen production authoritative engine;
- **Python:** külső tooling, referencia, AI- és batch-controller.

A Python referencia továbbra is értékes, de nem production authority.

---

## 3. Forrás- és dokumentumelsőbbség

1. hivatalos 1.4v szabályfőforrások;
2. elfogadott, verziózott emberi döntések;
3. `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`;
4. `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`;
5. jelen projekt-térkép;
6. `ENGINE_CHECKPOINT.md`;
7. `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
8. `ARCHITECTURE.md` és `TECHNOLOGY_DECISIONS.md`;
9. aktuális technikai státuszdokumentumok;
10. Open Questions kérdés–válasz pár;
11. aktív adat- és auditstandardok;
12. hosszú specificationök;
13. reference, archive és generated anyagok.

A kód technikai tényt bizonyíthat, de hivatalos játékszabályt nem írhat felül.

---

## 4. Státuszszótár

| Státusz | Jelentés |
|---|---|
| `ACTIVE_CANONICAL_RULE_SOURCE` | Elsődleges hivatalos szabályforrás. |
| `ACTIVE_EDITING_SOURCE` | Ember által szerkesztett adatforrás. |
| `ACTIVE_PROJECT_GUIDANCE` | Aktív projektirányító dokumentum. |
| `ACTIVE_ENGINE_DOCUMENTATION` | Aktív engine-dokumentáció. |
| `ACTIVE_REFERENCE_ENGINE` | Működő, tesztelt referenciaengine. |
| `ACCEPTED_PROOF` | Elfogadott technológiai bizonyíték. |
| `FROZEN_PROOF` | Megőrzött, de production főágként nem folytatandó proof. |
| `ACTIVE_TOOLING` | Aktív build-, export-, audit- vagy AI-eszköz. |
| `ACTIVE_CONSUMER` | Aktív loader-, kliens- vagy UI-réteg. |
| `ACTIVE_TEST` | Aktív regressziós, unit vagy smoke teszt. |
| `ACTIVE_REFERENCE_DOCUMENT` | Hasznos, karbantartott, de nem canonical háttérdokumentum. |
| `GENERATED_OUTPUT` | Regenerálható, nem canonical output. |
| `TEST_FIXTURE` | Teszt- vagy debugfixture. |
| `HISTORICAL_REFERENCE` | Történeti dokumentum, aktív irányító szerep nélkül. |
| `ARCHIVE_AFTER_VERIFY` | Aktív utód vagy beolvasztás után archívumba mozgatandó előd. |
| `ARCHIVED_HISTORICAL_AUDIT` | Korábbi audit, amelyet újabb aktív audit váltott fel. |
| `OLD_ENGINE_REFERENCE` | Régi motorhoz tartozó történeti referencia. |
| `GENERATED_BATCH_ARCHIVE` | Egyben archiválandó régi generált exportbatch. |
| `REVIEW_BEFORE_ARCHIVE` | Tartalmi audit után archiválható vagy aktívvá minősíthető. |
| `PROTECTED_DO_NOT_MOVE` | Aktív hivatkozás vagy tooling miatt egyelőre nem mozgatható. |

A korábbi `SUPERSEDED_DELETE_AFTER_VERIFY` státusz helyett mindenhol az `ARCHIVE_AFTER_VERIFY` használandó.

---

## 5. Gyökérszint

### Aktív

- `README.md` – `ACTIVE_PROJECT_GUIDANCE`;
- `.gitignore`, `.gitattributes`, `.editorconfig` – aktív repository meta.

### Archivált vagy archiválandó történeti engine-dokumentumok

#### `AETERNA game engine – aktuális állapotösszefoglaló.md`

- státusz: `ARCHIVE_AFTER_VERIFY`;
- régi Python-first és nyitott runtime-döntési állapot;
- érvényes részei átkerültek az engine README-be, checkpointba és státuszdokumentumokba;
- archiválási cél: projektirányítási vagy old-engine dokumentumarchívum.

#### `AETERNA – tanulóprojektekből kinyert legfontosabb fejlesztési irányok.md`

- státusz: `ARCHIVE_AFTER_VERIFY`;
- hasznos elvei átkerültek az architektúrába, contractrendszerbe és audit-sablonba;
- archiválási cél: kutatási és döntés-előkészítési dokumentumarchívum.

---

## 6. `Aeterna dokumentációk/` főszint

### 6.1 Aktív, védett források

#### Hivatalos szabályforrások

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`;
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`.

Státusz: `ACTIVE_CANONICAL_RULE_SOURCE`.

#### Aktív adatforrások

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `LOOKUPS.xlsx`.

Státusz: `ACTIVE_EDITING_SOURCE`.

#### Aktív projektirányítás

- `README.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.6.md`.

#### Aktív standardok

- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`;
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`;
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`;
- `kartya_tabla_szabvany v1.2.md`.

#### Beillesztésre előkészített aktuális adataudit

- `AETERNA – KÁRTYAADATBÁZIS AKTUÁLIS ADATAUDIT 1.0.md`.

Jelenlegi állapot:

- helyi utódfájl;
- a végső ellenőrzés után kerül a repositoryba;
- addig nem repository-authority.

Tervezett szerepe:

- az 1.9v munkaforrás aktuális adatintegritási auditja;
- a három 1.8v audit és a régi LOOKUPS-bővítési terv aktív utódja;
- a külön `LOOKUPS.xlsx` teljes auditja még nyitott kapu.

### 6.2 Felváltott projekttervek és projekt-térképek

Az aktív helyről archívumba mozgatandók:

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.1.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.4.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`;
- `DOCUMENTATION_CLEANUP_CHECKPOINT_2026-07-03.md`.

Javasolt archív csoport:

- `Archive/project_guidance/`.

A v1.6 megőrzi a szükséges fájlstátusz- és cleanup-információt.

---

## 7. `reference/` audit

A `reference/` nem canonical, de hasznos munkaforrások és történeti háttéranyagok helye.

### 7.1 Megtartandó és frissítendő aktív reference dokumentumok

#### `AETERNA – KÁRTYATERVEZÉSI KATALÓGUS ÉS HASZNÁLHATÓ ELEMEK 1.1v.md`

- státusz: `ACTIVE_REFERENCE_DOCUMENT`;
- jóváhagyott tervezési elemek és használható minták;
- nem egyesítendő az Ötletládával.

#### `AETERNA – ÖTLETLÁDA ÉS NYITOTT TERVEK 1.1v.md`

- státusz: `ACTIVE_REFERENCE_DOCUMENT`;
- nem végleges ötletek és parkoltatott alternatívák;
- beolvasztja az `Ötlet - Aeterna 4 .md` érvényes tartalmát `ÖT-0001` azonosítóval.

#### `Általános névprofil-sablon.md`

- státusz: `ACTIVE_REFERENCE_DOCUMENT`;
- javított 1.0-s utód szükséges;
- használja a `Szabályi_Kártya_ID` elsődleges azonosítót;
- nem helyettesíti a `NAME_PROFILE` munkalapot.

#### `GITHUB_MUNKAREND_ES_COMMIT_SZABALYOK.md`

- státusz: `ACTIVE_REFERENCE_DOCUMENT`;
- projektfüggetlen commit-, branch- és scope-szabály;
- metaadat- és terminológiafrissítés szükséges.

#### `TESZTPROGRAM_WORKFLOW_ES_TESZTPROFILOK.md`

- státusz: `ACTIVE_REFERENCE_DOCUMENT`, frissítendő;
- a tesztprofilok értékesek;
- a régi Python launcher/facade útvonalakat C# authority + Python headless tooling modellre kell átírni.

#### `Master Duel  Hearthstone tanulságok v0.1.md`

- státusz: `ACTIVE_REFERENCE_DOCUMENT`, nem canonical;
- külső design- és UI-tanulságok;
- később rövidítendő és szabványos metaadatblokkot kap.

### 7.2 Beolvasztott, majd archiválandó reference előd

#### `Ötlet - Aeterna 4 .md`

- státusz: `ARCHIVE_AFTER_VERIFY`;
- tartalma az Ötletláda 1.1v `ÖT-0001` bejegyzésébe került;
- archiválási cél: `Archive/design_ideas/`.

### 7.3 Régi Python motorhoz tartozó technikai reference csoport

- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`;
- `EFFECT_RETEG_AKTIV_UTVONAL.md`;
- `EFFECT_TRIGGER_HATAROK.md`.

Státusz:

- `OLD_ENGINE_REFERENCE`;
- ugyanazon archivált Python motor runtime-, effect- és triggerláncát írják le;
- aktív architektúraként nem használhatók;
- együtt archiválandók az old-engine dokumentációs rétegben.

### 7.4 Újratervezési történeti csoport

Az `ujratervezés/` alatti, korábbi céljegyzetek, AI-válaszok, kérdés–válasz anyagok, Python-hatékonysági vizsgálatok és korai checkpointok:

- státusz: `HISTORICAL_REFERENCE`;
- a fő döntések átkerültek a projekttervbe, technológiai döntésekbe, Open Questions-rendszerbe és checkpointba;
- a Python-versus-újraírás kérdés lezárult;
- csoportosan archiválhatók a döntés-előkészítési történet megőrzésére.

---

## 8. `archive_review/` lezárt audit

A jelenlegi mappa két jól elkülöníthető történeti csoportot tartalmaz.

### 8.1 Kártyaadat- és LOOKUPS-audit elődök

1. `aeterna_1_8v_teljes_jsonl_audit_jelentes.md`;
2. `aeterna_1_8v_ujraellenorzes_reszleges_audit.md`;
3. `aeterna_1_8v_javitott_export_lookup_audit.md`;
4. `aeterna_LOOKUPS_bovitesi_terv.md`.

Közös státusz:

- `ARCHIVED_HISTORICAL_AUDIT`;
- az 1.8v állapotot, javítási menetet és LOOKUPS-tervet őrzik;
- beillesztésre előkészített aktív utód:
  `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS AKTUÁLIS ADATAUDIT 1.0.md`;
- nem törlendők;
- nem maradhatnak aktív hibajegyzékként;
- az archívumban egy közös `card_database_audits_1.8v/` csoportba rendezhetők.

### 8.2 Régi Python-backend és projekt-guidance dokumentumok

1. `BACKEND_READINESS_AUDIT.md`;
2. `GODOT_BACKEND_FACADE_ELOKESZITES.md`;
3. `KOVETKEZO_LEPES_ES_FOLYTATASI_PONT.md`;
4. `README_AETERNA_project_guidance.md`;
5. `README_UPDATED_WITH_GITHUB_GUIDANCE.md`.

Közös státusz:

- `OLD_ENGINE_REFERENCE`;
- a régi Python `backend/`, facade, snapshot, legal action, `play_entity`, `play_trap` és `AeternaSzimulacio` útvonalat írják le;
- az általános elvek átkerültek az aktív:
  - root és engine README-be;
  - `ARCHITECTURE.md` fájlba;
  - `CONTRACT_SPECIFICATION.md` és `CONTRACT_STATUS.md` fájlokba;
  - `ENGINE_CHECKPOINT.md` fájlba;
  - GitHub-munkarendbe;
- nem szükséges új összevont aktív backend-dokumentum;
- együtt archiválhatók az old-engine dokumentáció alatt.

Javasolt cél:

- `Archive/old_python_engine_docs/backend_and_guidance/`.

### 8.3 `archive_review/` végleges szerepe

A fenti csoportok archiválása után az `archive_review/` mappa kiürülhet.

Üres mappát a Git nem követ, ezért külön megtartása nem szükséges.

Új fájl csak átmeneti auditállapotban kerülhet ide, és minden ilyen fájlnak kijelölt felülvizsgálati vagy archiválási következő lépéssel kell rendelkeznie.

---

## 9. `generated_review/` lezárt audit

### 9.1 Azonosított batch

A `generated_review/Új mappa/` egyetlen, régi szöveges kártyaexport-batch.

Forrás:

- `cards.xlsx`.

Exportdátum:

- `2026-05-25T09:48:49`.

Formátum:

- `AETERNA_text_export_1.0`.

A batch fő tartalma:

- `00_README.md`;
- `all_cards.json`;
- `all_cards.tsv`;
- `cards_export_summary.json`;
- `cards_by_realm/AETHER.tsv`;
- `cards_by_realm/AQUA.tsv`;
- `cards_by_realm/IGNIS.tsv`;
- `cards_by_realm/LUX.tsv`;
- `cards_by_realm/TERRA.tsv`;
- `cards_by_realm/UMBRA.tsv`;
- `cards_by_realm/VENTUS.tsv`;
- `OLD_AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.0.md`;
- `OLD_AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.0.md`.

### 9.2 Megállapított problémák

- a forrás a régi `cards.xlsx`, nem a jelenlegi 1.9v munkaforrás;
- az export nem tartalmazza a jelenlegi teljes adat- és azonosítócontractot;
- a belső README `all_cards.jsonl` fájlt említ, miközben a tényleges fájl `all_cards.json`;
- a belső README `AQUA_working_export.tsv` fájlt is említ, amely a repository-inventárban és keresésben nem található;
- az `Új mappa` név nem elfogadható végleges projektstruktúra;
- a két `OLD_*.md` dokumentumot az aktív 1.2-es standardok felváltották;
- a batch kézi szerkesztésre nem alkalmas;
- a jelenlegi runtime package és XLSX-export tooling mellett nem aktív programinput.

### 9.3 Döntés

A teljes `generated_review/Új mappa/` egyetlen egységként:

- státusz: `GENERATED_BATCH_ARCHIVE`;
- nem canonical;
- nem aktív szerkesztési forrás;
- nem aktív runtime input;
- történeti exportpillanatként archiválható;
- tartalmát nem kell külön fájlonként aktívvá minősíteni.

Javasolt archív célútvonal:

- `Archive/generated_exports/cards_xlsx_text_export_2026-05-25/`.

Az archiválás után:

- a `generated_review/Új mappa/` útvonal megszűnik;
- a `generated_review/` mappa kiürülhet;
- új generált review csak egyértelmű batchnévvel, forrásazonosítóval, dátummal és regenerálási paranccsal készülhet.

### 9.4 Jövőbeli generált output-szabály

Minden új batchhez szükséges:

- egyértelmű mappanév;
- source file vagy source fingerprint;
- build/export dátum;
- generátor és parancs;
- schema vagy format version;
- record count;
- canonical/nem canonical státusz;
- regenerálhatósági leírás;
- cleanup/retention policy.

`Új mappa`, `copy`, `final`, `new` vagy hasonló ideiglenes név nem maradhat végleges útvonalban.

---

## 10. `Aeterna game engine/` aktív rétegei

### `C#/`

- `Aeterna.RuntimeCandidate` – `ACCEPTED_PROOF`;
- `Aeterna.RuntimeCandidate.Proof` – `ACCEPTED_PROOF`;
- tervezett production projektek:
  `Aeterna.Engine`, `Aeterna.Engine.Headless`, `Aeterna.Engine.Tests`.

### `python/`

- `ACTIVE_REFERENCE_ENGINE`;
- `ACTIVE_TOOLING`;
- runtime package;
- XLSX/JSON/JSONL;
- audit és diagnostics;
- fixture, scenario, AI és batch;
- nem production authority.

### `Godot/`

- `ACTIVE_CONSUMER`;
- visual client foundation;
- C# bridge proof;
- nem authoritative szabálymotor.

### `runtime_comparison/`

- aktív regressziós referencia;
- expected és candidate artifactok;
- megtartási szabályát a reprodukálhatóság határozza meg.

---

## 11. Engine-dokumentációs réteg

### Aktív index és irány

- `README.md`;
- `ARCHITECTURE.md`;
- `TECHNOLOGY_DECISIONS.md`;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `DECISION_MAP.md`.

### Aktuális státusz

- `PROTOTYPE_STATUS.md`;
- `RUNTIME_PACKAGE_STATUS.md`;
- `CONTRACT_STATUS.md`.

### Open Questions

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

### Aktív specificationök

- `CONTRACT_SPECIFICATION.md`;
- `RUNTIME_PACKAGE_SPECIFICATION.md`;
- `ABILITY_MODULE_SYSTEM.md`;
- `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`;
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`.

### Történeti/reference szerep

- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`;
- `PROTOTYPE_PLANS.md`;
- `LEARNING_PROJECT_AUDIT_QUEUE.md`;
- `checkpoints/CHECKPOINTS.md`.

### Aktív sablon és termékcél

- `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`;
- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`.

---

## 12. `CURRENT_*` és checkpoint-elődök

Az alábbi elődök az aktív utód ellenőrzése után archívumba kerülnek:

| Archiválandó előd | Aktív utód |
|---|---|
| `docs/CURRENT_PROTOTYPE_STATUS.md` | `docs/PROTOTYPE_STATUS.md` |
| `docs/CURRENT_RUNTIME_PACKAGE_STATUS.md` | `docs/RUNTIME_PACKAGE_STATUS.md` |
| `docs/CURRENT_CONTRACT_STATUS.md` | `docs/CONTRACT_STATUS.md` |
| `docs/CURRENT_OPEN_QUESTIONS.md` | `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md` |
| `docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md` | `docs/checkpoints/ENGINE_CHECKPOINT.md` |
| `docs/checkpoints/AETERNA_CURRENT_ENGINE_CHECKPOINT_v1.1_2026-07-20.md` | `docs/checkpoints/ENGINE_CHECKPOINT.md` |
| `docs/ENGINE_OBJECT_IDENTITY_AND_ZONE_MOVE_PLAN_v0.1.md` | contract specification, status és checkpoint |

Javasolt archív csoport:

- `Archive/engine_docs_superseded/`.

A megtartandó aktív checkpoint-rendszer:

- `ENGINE_CHECKPOINT.md`;
- `CHECKPOINTS.md`;
- `README.md`.

---

## 13. Kötelező végső ellenőrzési sorrend

1. jelen projekt-térkép v1.6 beillesztése;
2. `AETERNA dokumentációk/README.md` archiválási szóhasználatának frissítése;
3. az aktuális adatauditban a négy leváltott archív előd pontos felsorolása;
4. a reference replacement fájlok beillesztése;
5. `archive_review/` két csoportjának archiválása;
6. `generated_review/Új mappa/` teljes batchének archiválása;
7. minden régi és új útvonal keresése;
8. minden `CURRENT_*` hivatkozás ellenőrzése;
9. verzió-, dátum- és státuszaudit;
10. Open Questions azonosítók ellenőrzése;
11. Markdown-hivatkozások célfájljainak létezésellenőrzése;
12. `git status --short`;
13. `git diff --check`;
14. whitespace-only C# diff külön kezelése;
15. generált TEMP/log/output kizárása a stage-ből;
16. archiválási és aktív fájlmódosítások scope-jának ellenőrzése;
17. commit;
18. commit utáni repository-keresés a régi fájlnevekre és `Új mappa` útvonalra.

---

## 14. Aktuális státusz

- engine-dokumentáció első konszolidációja: `SUBSTANTIALLY_COMPLETE`;
- aktív engine-fájlok auditja: `COMPLETE`;
- `CURRENT_*` és checkpointduplikációk besorolása: `COMPLETE`;
- `reference/` első tartalmi auditja: `COMPLETE`;
- `archive_review/` auditja: `COMPLETE`;
- `generated_review/` auditja: `COMPLETE`;
- kártyaadatbázis 1.9v első aktuális adataudit-utódja: `PREPARED_WITH_OPEN_LOOKUPS_GATE`;
- külön `LOOKUPS.xlsx` teljes auditja: `PENDING`;
- jelen projekt-térkép és az adataudit repository-beillesztése: `PENDING_USER_COMMIT`;
- reference utódfájlok beillesztése: `PENDING_USER_COMMIT`;
- archív mozgatások: `PENDING_USER_COMMIT`;
- dokumentációs README és projektterv végső frissítése: `PENDING`;
- teljes keresztmappa- és hivatkozásellenőrzés: `NEXT`;
- C.5B production engine: `READY_FOR_IMPLEMENTATION / PAUSED_CODEX_QUOTA`.
