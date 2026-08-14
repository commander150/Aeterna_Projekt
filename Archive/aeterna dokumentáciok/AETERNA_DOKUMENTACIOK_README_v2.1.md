# AETERNA dokumentációk – mappaszintű index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.1  
**Dátum:** 2026-07-21  
**Státusz:** commitra előkészített aktív dokumentációs mappaindex  
**Felváltott dokumentum:** `README.md` 2.0  
**Aktuális repository HEAD:** `ccfd3dc05a0cf16409aeb27c91333fe41d9633cc` – `docs update 3`  
**Kapcsolódó fájlstátusz-térkép:** `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.6.md`

Ez a mappa az AETERNA projekt hivatalos szabály-, adat-, projektirányítási és munkafolyamat-dokumentumainak elsődleges helye.

A főszinten csak:

- aktív;
- védett;
- vagy közvetlenül a jelenlegi munkafolyamatot irányító

dokumentum maradhat.

Felváltott terv, régi projekt-térkép, generált export, korábbi audit vagy történeti háttéranyag nem maradhat párhuzamos aktív igazságforrásként.

Az aktív helyről kikerülő fájlok nem véglegesen törlendők. Ellenőrzés után az `Archive/` megfelelő területére kerülnek.

---

## 1. Főszinten megtartandó aktív fájlok

### 1.1 Hivatalos szabályforrások

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`;
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`.

Státusz:

- `ACTIVE_CANONICAL_RULE_SOURCE`;
- védett;
- formátumváltás vagy tartalmi módosítás csak külön emberi döntéssel történhet.

### 1.2 Aktív adatforrások

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `LOOKUPS.xlsx`.

Státusz:

- `ACTIVE_EDITING_SOURCE`;
- a fő szerkesztési háttér Google Sheets;
- a helyi XLSX-fájlok szerkesztési vagy exportbemeneti példányok;
- a program validált runtime package-et fogyaszt, nem közvetlenül a munkafüzetet.

### 1.3 Aktív projektirányító dokumentumok

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.6.md`;
- jelen `README.md`.

A v1.6 projekt-térkép és a jelen 2.1-es index a következő dokumentációs commitra előkészített utódok. A repositoryba kerülésükig a jelenlegi GitHub-fájlok maradnak a tényleges repository-állapot dokumentumai.

### 1.4 Aktív munkaszabványok

- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`;
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`;
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`;
- `kartya_tabla_szabvany v1.2.md`.

Ezek:

- kártyaadat- és auditmunkánál kötelező referenciák;
- nem hivatalos játékszabályforrások;
- nem írhatják felül az engine-contractokat vagy a hivatalos főforrásokat;
- külön későbbi verzió- és tartalmi auditot igényelnek.

### 1.5 Előkészített aktuális adataudit

- `AETERNA – KÁRTYAADATBÁZIS AKTUÁLIS ADATAUDIT 1.0.md`.

Tervezett szerepe:

- az 1.9v kártyaadatbázis aktuális adatintegritási auditja;
- a három korábbi 1.8v audit és a régi LOOKUPS-bővítési terv aktív utódja;
- a külön `LOOKUPS.xlsx` teljes auditjáig nyitott lookup-ellenőrzési kaput tart fenn.

A fájl a végső ellenőrzés és commit után válik repository-szintű aktív auditdokumentummá.

---

## 2. Archiválási alapelv

Egy fájl csak akkor kerülhet ki az aktív helyéről, ha:

1. tartalmát átvizsgáltuk;
2. kijelöltük az aktív utódot vagy beolvasztási célt;
3. ellenőriztük, hogy nyitott kérdés, döntés vagy fontos történeti adat nem vész el;
4. kijelöltük az archív célútvonalat;
5. átvezettük az aktív hivatkozásokat;
6. ellenőriztük a Git diffet és a régi fájlnévre mutató hivatkozásokat.

A fájl mozgatása után:

- nem maradhat aktív elsődleges hivatkozás az archív példányra;
- az archív példány nem írhatja felül az újabb aktív dokumentumot;
- a dokumentum státuszának egyértelműen történetinek kell lennie.

---

## 3. Főszintről archiválandó felváltott verziók

### 3.1 Projekttervek

Aktív utód:

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`.

Archiválandó elődök:

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.1.md`.

### 3.2 Projekt-térképek

Aktív utód:

- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.6.md`.

Archiválandó elődök:

- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.4.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`.

A v1.4 különösen nem maradhat aktív, mert:

- nyitottként kezeli a már lezárt runtime-döntést;
- v6.1-re és `CURRENT_*` fájlokra hivatkozik;
- a tartalma a Python engine-rész közepén megszakad.

### 3.3 Korábbi cleanup-checkpoint

Archiválandó:

- `DOCUMENTATION_CLEANUP_CHECKPOINT_2026-07-03.md`.

Az érvényes tartalma átkerült:

- a projekt-térképbe;
- a jelen mappaindexbe;
- az aktív engine-checkpointba.

### 3.4 Javasolt közös archív cél

- `Archive/project_guidance/`.

A pontos mozgatás a végső hivatkozás- és fájllista-ellenőrzés után történjen.

---

## 4. `reference/`

A `reference/` mappa nem canonical, de hasznos, karbantartható háttér- és munkaforrásokat tartalmazhat.

A reference dokumentum:

- nem írhat felül hivatalos főforrást;
- nem válhat automatikusan elfogadott döntéssé;
- státusza és szerepe legyen egyértelmű;
- aktív reference esetén kapjon verziót, dátumot és státuszt.

### 4.1 Megtartandó és frissítendő reference fájlok

- `AETERNA – KÁRTYATERVEZÉSI KATALÓGUS ÉS HASZNÁLHATÓ ELEMEK 1.1v.md`;
- `AETERNA – ÖTLETLÁDA ÉS NYITOTT TERVEK 1.1v.md`;
- `Általános névprofil-sablon.md`;
- `GITHUB_MUNKAREND_ES_COMMIT_SZABALYOK.md`;
- `TESZTPROGRAM_WORKFLOW_ES_TESZTPROFILOK.md`;
- `ujratervezés/Master Duel  Hearthstone tanulságok v0.1.md`.

### 4.2 Beolvasztott ötletelőd

- `Ötlet - Aeterna 4 .md`.

Tartalma az Ötletláda 1.1v `ÖT-0001` bejegyzésébe került.

Archiválási cél:

- `Archive/design_ideas/`.

### 4.3 Régi Python motor technikai reference fájljai

- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`;
- `EFFECT_RETEG_AKTIV_UTVONAL.md`;
- `EFFECT_TRIGGER_HATAROK.md`.

Ezek ugyanannak az archivált Python motornak a runtime-, effect- és triggerláncát írják le.

Státuszuk:

- `OLD_ENGINE_REFERENCE`;
- aktív architektúraként nem használhatók;
- az old-engine dokumentációval együtt archiválandók.

### 4.4 `ujratervezés/` történeti dokumentumai

A korábbi:

- céljegyzetek;
- AI-válaszok;
- kérdés–válasz dokumentumok;
- Python-hatékonysági vizsgálatok;
- korai digitális checkpointok

történeti döntés-előkészítési források.

A fő döntések már átkerültek:

- az aktuális projekttervbe;
- a technológiai döntésekbe;
- az Open Questions-rendszerbe;
- az engine-checkpointba.

Ezek csoportosan archiválhatók a döntéstörténet megőrzésére.

---

## 5. `archive_review/`

A mappa auditja elkészült.

### 5.1 Archivált kártyaadat- és LOOKUPS-auditok

Az alábbi négy fájl történeti auditként megmarad:

- `aeterna_1_8v_teljes_jsonl_audit_jelentes.md`;
- `aeterna_1_8v_ujraellenorzes_reszleges_audit.md`;
- `aeterna_1_8v_javitott_export_lookup_audit.md`;
- `aeterna_LOOKUPS_bovitesi_terv.md`.

Aktív utódjuk:

- `AETERNA – KÁRTYAADATBÁZIS AKTUÁLIS ADATAUDIT 1.0.md`.

Javasolt archív cél:

- `Archive/card_database_audits_1.8v/`.

### 5.2 Régi Python-backend és projekt-guidance dokumentumok

- `BACKEND_READINESS_AUDIT.md`;
- `GODOT_BACKEND_FACADE_ELOKESZITES.md`;
- `KOVETKEZO_LEPES_ES_FOLYTATASI_PONT.md`;
- `README_AETERNA_project_guidance.md`;
- `README_UPDATED_WITH_GITHUB_GUIDANCE.md`.

Ezek:

- a régi Python backend/facade rendszert írják le;
- nem aktív C# production dokumentumok;
- általánosan érvényes elveik már bekerültek az aktív architektúra-, contract- és checkpointdokumentumokba;
- nem igényelnek új összevont aktív backend-dokumentumot.

Javasolt archív cél:

- `Archive/old_python_engine_docs/backend_and_guidance/`.

### 5.3 Mappa további kezelése

A két dokumentumcsoport archiválása után az `archive_review/` kiürülhet.

Új fájl csak átmeneti review-státusszal kerülhet ide. Minden ilyen fájlnak rendelkeznie kell:

- kijelölt vizsgálati céllal;
- felelősségi vagy döntési ponttal;
- következő lépéssel;
- aktív utóddal vagy várható archív céllal.

---

## 6. `generated_review/`

A mappa auditja elkészült.

### 6.1 Azonosított generált batch

A teljes:

- `generated_review/Új mappa/`

egy 2026. május 25-én a régi `cards.xlsx` fájlból létrehozott szöveges exportbatch.

Fő tartalma:

- `00_README.md`;
- `all_cards.json`;
- `all_cards.tsv`;
- `cards_export_summary.json`;
- hét Birodalom szerinti TSV a `cards_by_realm/` mappában;
- két `OLD_*.md` dokumentum.

### 6.2 Státusz

- `GENERATED_BATCH_ARCHIVE`;
- nem canonical;
- nem aktív szerkesztési forrás;
- nem aktív runtime input;
- kézzel nem szerkesztendő;
- történeti exportpillanatként egyben archiválandó.

### 6.3 Ismert batchhibák

- a forrás a régi `cards.xlsx`, nem az 1.9v munkaforrás;
- az `all_cards.json` tartalma valójában JSONL-jellegű;
- a belső README `all_cards.jsonl` fájlnevet használ;
- a belső README `AQUA_working_export.tsv` fájlt említ, amely nem található;
- az `Új mappa` név nem elfogadható végleges útvonal;
- a két `OLD_*.md` dokumentumot aktív 1.2-es standardok váltották fel.

### 6.4 Javasolt archív cél

- `Archive/generated_exports/cards_xlsx_text_export_2026-05-25/`.

A teljes batch egy egységként archiválandó. Nem szükséges fájlonként külön aktív vagy archív dokumentumszerepet létrehozni.

### 6.5 Jövőbeli generált batch szabálya

Minden új generált mappához kötelező:

- egyértelmű batchnév;
- forrásfájl vagy forrás-fingerprint;
- generálás dátuma;
- generátor és futtatási parancs;
- schema- vagy formátumverzió;
- rekordszám;
- canonical vagy nem canonical státusz;
- regenerálási leírás;
- retention- és cleanup-policy.

`Új mappa`, `copy`, `final`, `new` vagy hasonló ideiglenes név nem maradhat végleges repository-útvonalban.

---

## 7. `active/`

Fenntartott mappa.

A fő aktív források jelenleg a dokumentációs főszinten maradnak, amíg:

- a hivatkozások;
- az export- és buildtooling;
- az archiválási mozgatások;
- és a végső mappastruktúra

ellenőrzése be nem fejeződik.

Az `active/` mappába nem kell automatikusan áthelyezni minden aktív dokumentumot.

---

## 8. Kapcsolódó engine-dokumentáció

### 8.1 Aktív engine-index

- `../Aeterna game engine/README.md`;
- `../Aeterna game engine/docs/README.md`.

### 8.2 Aktív technikai folytatási pont

- `../Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`.

### 8.3 Aktív architektúra és döntések

- `../Aeterna game engine/docs/ARCHITECTURE.md`;
- `../Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`;
- `../Aeterna game engine/docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `../Aeterna game engine/docs/DECISION_MAP.md`.

### 8.4 Aktív státuszdokumentumok

- `../Aeterna game engine/docs/PROTOTYPE_STATUS.md`;
- `../Aeterna game engine/docs/RUNTIME_PACKAGE_STATUS.md`;
- `../Aeterna game engine/docs/CONTRACT_STATUS.md`.

### 8.5 Open Questions

- `../Aeterna game engine/docs/OPEN_QUESTIONS.md`;
- `../Aeterna game engine/docs/OPEN_QUESTIONS_DECISIONS.md`.

A korábbi `CURRENT_*` fájlok az aktív utódok és hivatkozások ellenőrzése után archívumba kerülnek.

---

## 9. Dokumentumnév- és verziószabály

- Aktív, stabil szerepű engine-dokumentum lehet verziószám nélküli fájlnévvel, de a dokumentum belsejében kötelező a verzió.
- Projektterv és projekt-térkép verziója a fájlnévben is szerepelhet.
- `CURRENT_` előtag csak valódi, indokolt párfájl esetén használható.
- `frissitett`, `new`, `final`, `copy`, `másolat` vagy hasonló állapotjelző nem lehet tartós fájlnév része.
- Az újabb verzió nevezze meg a felváltott elődöt.
- Felváltott verzió ne maradjon aktív főszinten történeti okból; erre az `Archive/` szolgál.
- Minden aktív Markdown-dokumentumban legyen verzió, dátum és státusz.
- Történeti archív dokumentum eredeti fájlneve megőrizhető, ha a mappakörnyezet és státusz egyértelmű.
- Generált batch mappaneve tartalmazza a forrást vagy funkciót és a létrehozás dátumát.

---

## 10. Aktuális cleanup-szakasz

### Elkészült

- engine-dokumentáció első konszolidációja;
- `CURRENT_OPEN_QUESTIONS.md` tartalmi beolvasztása;
- C# runtime-döntés átvezetése;
- új státuszdokumentumok;
- aktív checkpoint-utód;
- projekt-térkép v1.6 előkészítése;
- `reference/` első tartalmi auditja;
- `archive_review/` teljes első auditja;
- `generated_review/` teljes első auditja;
- 1.9v kártyaadatbázis aktuális audit-utódjának előkészítése.

### Még hátralévő dokumentációs feladatok

1. jelen README 2.1 és a projekt-térkép v1.6 beillesztése;
2. reference replacement fájlok beillesztése;
3. a kártyaadat-audit repositoryba helyezése;
4. régi projekttervek és projekt-térképek archiválása;
5. engine `CURRENT_*` és checkpointelődök archiválása;
6. `reference/` történeti csoportjainak archiválása;
7. `archive_review/` két csoportjának végleges archiválása;
8. `generated_review/Új mappa/` exportbatchének archiválása;
9. külön `LOOKUPS.xlsx` teljes tartalmi auditja;
10. aktív standardok tartalmi és verzióauditja;
11. végső keresztmappa-, hivatkozás-, verzió- és duplikációellenőrzés.

A teljes fájlstátusz- és archiválási térkép:

- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.6.md`.

---

## 11. Végső visszaellenőrzés

A teljes dokumentációs rendezés végén külön végső ellenőrzési kör szükséges.

Kötelező ellenőrzések:

1. teljes repository-fájllista;
2. aktív és archív fájlok útvonalának ellenőrzése;
3. hiányzó célfájlok;
4. azonos vagy közel azonos fájlnevek;
5. azonos tartalmú duplikátumok;
6. régi verziókra és fájlnevekre mutató hivatkozások;
7. `CURRENT_*`, `Új mappa`, `OLD_`, `final`, `copy`, `másolat` előfordulások;
8. minden aktív Markdown verzió-, dátum- és státuszblokkja;
9. Open Questions kérdés–válasz azonosítók;
10. hivatalos szabályforrásokra mutató hivatkozások;
11. aktív projektterv, projekt-térkép és checkpoint összhangja;
12. archív fájlok nem jelennek-e meg aktív authorityként;
13. generált outputok nem kerülnek-e canonical forrásként hivatkozásra;
14. `git status --short`;
15. `git diff --check`;
16. stage-scope ellenőrzése;
17. commit utáni ismételt repository-keresés.

A cleanup csak e visszaellenőrzés után tekinthető teljesen lezártnak.
