# AETERNA – Projekt Térkép és Fájlstátusz v1.5

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.5  
**Dátum:** 2026-07-21  
**Státusz:** aktív magas szintű projekt-, fájlstátusz- és cleanup-térkép  
**Felváltott dokumentum:** `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.4.md`  
**Aktuális repository HEAD:** `32a0cbea24c82dda440f1a053b454ef03949d8ae` – `docs update 2`  
**Aktuális C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Ez a dokumentum az AETERNA repository fő mappáit, aktív forrásait, technikai rétegeit, dokumentumstátuszait és a végső dokumentációs cleanup során végrehajtandó megtartási, áthelyezési vagy eltávolítási döntéseket rögzíti.

A v1.5 fő változásai:

- a lezárt runtime-nyelvi döntés átvezetése;
- a C# production authority rögzítése;
- a v1.4 hiányos tartalmának pótlása;
- a v1.3 hasznos mappatérképének megtartása, de az elavult Python-authority kijavítása;
- a projektterv v6.2 végleges helyének kijelölése;
- a `CURRENT_*` elődök törlési döntése;
- a három checkpointváltozat konszolidációja;
- a gyökérszintű elavult engine-összefoglalók eltávolításának kijelölése;
- a történeti, de nem duplikált dokumentumok elhatárolása;
- a végső hivatkozás- és commitellenőrzés sorrendje.

Ez nem teljes, minden generált fájlt felsoroló technikai inventár. A végső cleanup döntési térképe, amelyhez a tényleges `git status`, `git diff`, fájllista és hivatkozáskeresés társul.

---

## 1. Aktuális projektkép

A repository fő rendszerrétegei:

1. hivatalos szabályforrások;
2. kártyaadatbázis és LOOKUPS;
3. Python adatpipeline és runtime package tooling;
4. Python minimal rules-engine referencia;
5. Godot loader-, debug- és vizuális kliensréteg;
6. elfogadott C# in-process runtime proof;
7. tervezett production C# authoritative engine;
8. runtime comparison fixture és regressziós artifactok;
9. dokumentáció, audit és kártyatervezés;
10. régi motorok és archív anyagok;
11. generált review- és buildoutputok.

Elfogadott szerepfelosztás:

```text
Godot / GDScript = vizuális kliens
C# / .NET         = egyetlen production authoritative engine
Python            = external tooling, reference, AI és batch controller
```

A Python referencia továbbra is értékes, de nem production authority.

---

## 2. Forrás- és dokumentumelsőbbség

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
11. hosszú specificationök;
12. történeti, reference és archive anyagok.

A kód technikai tényt bizonyíthat, de hivatalos játékszabályt nem írhat felül.

---

## 3. Státuszszótár

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
| `GENERATED_OUTPUT` | Regenerálható, nem canonical output. |
| `TEST_FIXTURE` | Teszt- vagy debugfixture. |
| `HISTORICAL_REFERENCE` | Történeti dokumentum, aktív irányító szerep nélkül. |
| `SUPERSEDED_DELETE_AFTER_VERIFY` | Kijelölt utód után, hivatkozásellenőrzéssel eltávolítandó előd. |
| `REVIEW_BEFORE_ARCHIVE_OR_DELETE` | Nem nyilvánvaló duplikátum; tartalmi audit kell. |
| `OLD_ENGINE_REFERENCE` | Régi motoros referencia. |
| `ARCHIVE_REVIEW` | Archív vagy törlési döntés előtt vizsgálandó. |
| `PROTECTED_DO_NOT_MOVE` | Aktív hivatkozás vagy tooling miatt egyelőre nem mozgatható. |

---

## 4. Gyökérszint

### `README.md`

- státusz: `ACTIVE_PROJECT_GUIDANCE`;
- végleges szerep: rövid repository-belépési pont;
- frissítendő a C# authorityre, v6.2 projekttervre, v1.5 projekt-térképre és új engine-fájlnevekre;
- régi `python main.py` gyökérfuttatási út nem maradhat általános projektleírásként.

### Repository meta

- `.gitignore`;
- `.gitattributes`;
- `.editorconfig`.

Státusz:

- aktív repository meta;
- külön audit csak konkrét probléma esetén.

### Eltávolítandó gyökérszintű történeti engine-dokumentumok

#### `AETERNA game engine – aktuális állapotösszefoglaló.md`

- státusz: `SUPERSEDED_DELETE_AFTER_VERIFY`;
- ok: 2026-07-12-i Python-first állapot, nyitott runtime-döntés és régi Card_ID-modell;
- tartalma beolvadt: engine README, checkpoint, contract status, prototype status;
- utód: nincs egyetlen közvetlen fájl, mert a tartalom szerep szerint szétvált;
- kezelés: eltávolítható a working tree-ből; Git-történet megőrzi.

#### `AETERNA – tanulóprojektekből kinyert legfontosabb fejlesztési irányok.md`

- státusz: `SUPERSEDED_DELETE_AFTER_VERIFY`;
- ok: a fontos elvek és feladatok már átvezetésre vagy implementálásra kerültek;
- tartalma beolvadt: architecture, contract specification, technology decisions, audit template;
- kezelés: eltávolítható a working tree-ből.

---

## 5. `Aeterna dokumentációk/`

### 5.1 Aktív és védett főszinti fájlok

#### Hivatalos szabályforrások

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx` – `ACTIVE_CANONICAL_RULE_SOURCE`;
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx` – `ACTIVE_CANONICAL_RULE_SOURCE`.

#### Adatforrások

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx` – `ACTIVE_EDITING_SOURCE`;
- `LOOKUPS.xlsx` – `ACTIVE_EDITING_SOURCE`.

#### Projektirányítás

- `README.md` – `ACTIVE_PROJECT_GUIDANCE`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md` – `ACTIVE_PROJECT_GUIDANCE`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md` – `ACTIVE_PROJECT_GUIDANCE`.

#### Munkaszabványok

- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`;
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`;
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`;
- `kartya_tabla_szabvany v1.2.md`.

Státusz: aktív standardok, későbbi külön tartalmi és verzióaudit szükséges.

### 5.2 Felváltott projekttervek

Eltávolítandó a v6.2 sikeres elhelyezése után:

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.1.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`.

A v6.2 végleges helye:

- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`.

A tévesen engine docs alá került v6.2 példány eltávolítandó:

- `Aeterna game engine/docs/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`.

### 5.3 Felváltott dokumentációs cleanup-checkpoint

#### `DOCUMENTATION_CLEANUP_CHECKPOINT_2026-07-03.md`

- státusz: `SUPERSEDED_DELETE_AFTER_VERIFY`;
- az első cleanup-kör történeti állapotát rögzíti;
- nincs teljes dokumentumverzió-blokkja;
- több már elavult Python-first és mappastátusz-állítást tartalmaz;
- érvényes tartalma beolvadt a v1.5 projekt-térképbe, a mappaindexbe és az aktív engine-checkpointba;
- working tree-ből eltávolítható, a Git-történet megőrzi.

### 5.4 Felváltott projekt-térképek

A v1.5 beillesztése után eltávolítandó:

- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.4.md`;
- `DOCUMENTATION_CLEANUP_CHECKPOINT_2026-07-03.md`.

A v1.5:

- megőrzi a v1.3 hasznos mappaszerepeit;
- kijavítja a v1.3 Python-authority állítását;
- pótolja a v1.4 megszakadt tartalmát;
- hozzáadja a cleanup-térképet.

### 5.5 Almappák

#### `reference/`

- státusz: háttér- és designreferencia;
- nem canonical;
- külön tartalmi audit később.

#### `archive_review/`

- státusz: `ARCHIVE_REVIEW`;
- automatikusan nem törlendő;
- régi auditok és tervek összevonása szükséges lehet.

#### `generated_review/`

- státusz: `GENERATED_OUTPUT` / review;
- generált fájlok és ideiglenes mappák külön cleanupot igényelnek;
- `Új mappa` jellegű mappanév nem maradhat végleges struktúrában.

---

## 6. `Aeterna game engine/`

### 6.1 Fő részek

- `C#/`;
- `python/`;
- `Godot/`;
- `docs/`;
- `runtime_comparison/`;
- `README.md`.

### 6.2 `C#/`

Jelenleg:

- `Aeterna.RuntimeCandidate` – `ACCEPTED_PROOF`;
- `Aeterna.RuntimeCandidate.Proof` – `ACCEPTED_PROOF`.

Tervezett:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`.

A candidate nem nevezendő át közvetlenül production motorrá.

### 6.3 `python/`

Státusz:

- `ACTIVE_REFERENCE_ENGINE`;
- `ACTIVE_TOOLING`.

Szerepe:

- runtime package build;
- XLSX/JSON/JSONL tooling;
- audit és diagnostics;
- Python minimal reference engine;
- fixture és scenario;
- AI/batch controller;
- comparison oracle.

Nem production authority.

### 6.4 `Godot/`

Státusz:

- `ACTIVE_CONSUMER`;
- visual client foundation;
- C# bridge proof.

Nem lehet authoritative szabálymotor.

### 6.5 `runtime_comparison/`

- canonical fixture;
- expected Python output;
- sidecar candidate output;
- C# candidate output;
- validators és logs.

Státusz:

- aktív regressziós referencia;
- generált artifactok megtartása csak a comparison reproducibility szerint.

---

## 7. `Aeterna game engine/docs/` aktív dokumentumkészlete

### 7.1 Aktív index és irány

- `README.md`;
- `ARCHITECTURE.md`;
- `TECHNOLOGY_DECISIONS.md`;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `DECISION_MAP.md`.

### 7.2 Aktuális státusz

- `PROTOTYPE_STATUS.md`;
- `RUNTIME_PACKAGE_STATUS.md`;
- `CONTRACT_STATUS.md`.

### 7.3 Kérdés–válasz pár

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

### 7.4 Aktív specificationök

- `CONTRACT_SPECIFICATION.md`;
- `RUNTIME_PACKAGE_SPECIFICATION.md`;
- `ABILITY_MODULE_SYSTEM.md`;
- `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`;
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`.

### 7.5 Történeti vagy referenciaszerepű, de nem közvetlen duplikátum

- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md` – történeti migration-reference;
- `PROTOTYPE_PLANS.md` – proof-folytonosság;
- `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md` – aktív általános sablon;
- `LEARNING_PROJECT_AUDIT_QUEUE.md` – lezárt döntési queue, történeti referencia;
- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md` – aktív termékcél.

Ezeket nem szabad a név alapján automatikusan törölni. A végső tartalmi auditban külön vizsgálandó, hogy a rövidített történeti fájlok Git-történetbe visszavonhatók-e.

### 7.6 Befejezett tervként eltávolítandó

#### `ENGINE_OBJECT_IDENTITY_AND_ZONE_MOVE_PLAN_v0.1.md`

- státusz: `SUPERSEDED_DELETE_AFTER_VERIFY`;
- a tervezett card instance, zone move, stale guard, ObjectReference, Domain position és visibility alap jelentős része elkészült;
- a megmaradó elvek szerepelnek a contract specificationben, contract statusban és checkpointokban;
- régi következő Codex-feladatokat tartalmaz;
- working tree-ből eltávolítható, Git-történet megőrzi.

---

## 8. `CURRENT_*` duplikációk

| Eltávolítandó előd | Megtartandó utód | Döntés |
|---|---|---|
| `docs/CURRENT_PROTOTYPE_STATUS.md` | `docs/PROTOTYPE_STATUS.md` | törlendő |
| `docs/CURRENT_RUNTIME_PACKAGE_STATUS.md` | `docs/RUNTIME_PACKAGE_STATUS.md` | törlendő |
| `docs/CURRENT_CONTRACT_STATUS.md` | `docs/CONTRACT_STATUS.md` | törlendő |
| `docs/CURRENT_OPEN_QUESTIONS.md` | `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md` | beolvasztva, törlendő |
| `docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md` | `docs/checkpoints/ENGINE_CHECKPOINT.md` | törlendő |
| `docs/checkpoints/AETERNA_CURRENT_ENGINE_CHECKPOINT_v1.1_2026-07-20.md` | `docs/checkpoints/ENGINE_CHECKPOINT.md` | átmeneti előd, törlendő |

Az új fájlok magasabb verziójúak, explicit módon megnevezik a felváltott elődöt és tartalmazzák a lezárt C# döntést.

---

## 9. Checkpoint-rendszer

Megtartandó:

- `docs/checkpoints/ENGINE_CHECKPOINT.md` – aktív elsődleges folytatási pont;
- `docs/checkpoints/CHECKPOINTS.md` – történeti mérföldkőnapló;
- `docs/checkpoints/README.md` – checkpoint-index.

Eltávolítandó:

- `CURRENT_ENGINE_CHECKPOINT.md`;
- `AETERNA_CURRENT_ENGINE_CHECKPOINT_v1.1_2026-07-20.md`.

A három megtartott fájl szerepe különbözik, ezért nem duplikáció.

---

## 10. Dokumentációs commitok utáni eltérés

A proof commit után három commit került a repositoryba:

- `243620df0ad393f782b292ed73f306e8ae4ceea5` – `update CsharpMinimalRuntimeProof.cs`;
- `a0cf7a40f349f150d6520f5907cbc1088f1309d1` – `docs update`;
- `32a0cbea24c82dda440f1a053b454ef03949d8ae` – `docs update 2`.

A C# fájl változása csak behúzáscsere:

- négy szóköz → tabulátor;
- logikai és szemantikai tartalom változatlan.

Kezelési javaslat:

- vagy visszaállítani az elfogadott proof commit formázására;
- vagy külön formázási commitként megtartani;
- a dokumentációs cleanup commit ne rejtsen nem dokumentációs diffet.

Státusz:

`NON_BLOCKING_WHITESPACE_ONLY`.

---

## 11. Pontos eltávolítási lista

A következő fájlok a megfelelő utódok és hivatkozások ellenőrzése után eltávolíthatók:

### Gyökér

- `AETERNA game engine – aktuális állapotösszefoglaló.md`;
- `AETERNA – tanulóprojektekből kinyert legfontosabb fejlesztési irányok.md`.

### `Aeterna dokumentációk/`

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.1.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.4.md`;
- `DOCUMENTATION_CLEANUP_CHECKPOINT_2026-07-03.md`.

### `Aeterna game engine/docs/`

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`;
- `CURRENT_PROTOTYPE_STATUS.md`;
- `CURRENT_RUNTIME_PACKAGE_STATUS.md`;
- `CURRENT_CONTRACT_STATUS.md`;
- `CURRENT_OPEN_QUESTIONS.md`;
- `ENGINE_OBJECT_IDENTITY_AND_ZONE_MOVE_PLAN_v0.1.md`.

### `Aeterna game engine/docs/checkpoints/`

- `CURRENT_ENGINE_CHECKPOINT.md`;
- `AETERNA_CURRENT_ENGINE_CHECKPOINT_v1.1_2026-07-20.md`.

A törlés nem jelenti a történet elvesztését: a Git-történet megőrzi a korábbi tartalmat.

---

## 12. Még külön auditálandó, nem automatikus törlés

- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`;
- `PROTOTYPE_PLANS.md`;
- `LEARNING_PROJECT_AUDIT_QUEUE.md`;
- `docs/checkpoints/README.md`;
- `docs/checkpoints/CHECKPOINTS.md`;
- `archive_review/` teljes tartalma;
- `reference/` technikai és újratervezési anyagai;
- `generated_review/` regenerálható fájljai;
- régi Python motor dokumentációi és outputjai;
- runtime comparison megtartandó és regenerálható artifactjai.

Ezek között lehet későbbi összevonási vagy archiválási jelölt, de jelenleg nincs elég bizonyíték az automatikus törléshez.

---

## 13. Végső ellenőrzési sorrend

1. új root README, dokumentációs README, projektterv v6.2 és projekt-térkép v1.5 beillesztése;
2. engine README, docs README, checkpoint és checkpoint-index frissítése;
3. minden `CURRENT_*` hivatkozás keresése;
4. minden v6.0/v6.1/v1.2/v1.3/v1.4 hivatkozás keresése;
5. Open Questions 74 azonosítójának és döntéspárjának ellenőrzése;
6. aktív dokumentumok verzió-, dátum- és státuszauditja;
7. hivatkozások célfájljainak létezésellenőrzése;
8. törlendő elődök eltávolítása;
9. `git status --short`;
10. `git diff --check`;
11. whitespace-only C# diff külön kezelése;
12. generált TEMP/log/output kizárása;
13. stage-scope ellenőrzése;
14. dokumentációs commit;
15. commit utáni repository-keresés a régi fájlnevekre;
16. ezután az `Aeterna dokumentációk/reference`, `archive_review` és `generated_review` mély auditja.

---

## 14. Aktuális státusz

- engine-dokumentáció első konszolidációja: `SUBSTANTIALLY_COMPLETE`;
- kimaradt engine-fájlok auditja: `COMPLETE_FOR_ACTIVE_LAYER`;
- duplikációs térkép: `COMPLETE`;
- régi fájlok tényleges törlése: `PENDING_USER_COMMIT`;
- root és mappaindexek frissítése: `PREPARED`;
- `Aeterna dokumentációk/` mély almappaauditja: `NEXT_MAJOR_DOCUMENTATION_TASK`;
- C.5B production engine: `READY_FOR_IMPLEMENTATION / PAUSED_CODEX_QUOTA`.
