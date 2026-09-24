# AETERNA dokumentációk – mappaszintű index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.6
**Dátum:** 2026-09-05
**Státusz:** aktív dokumentációs mappaindex
**Előző aktív verzió:** 2.5 (Git history)
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9` – Combat + Pecsét Foundation C0–C6
**Kapcsolódó fájlstátusz-térkép:** `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.12.md`

Ez a mappa az AETERNA projekt adat-, projektirányítási és munkafolyamat-dokumentumainak elsődleges helye. A hivatalos szabályforrások current helye a repository `rules/sources/` területe.

A főszinten csak aktív, védett vagy közvetlenül a jelenlegi munkafolyamatot irányító dokumentum maradhat. Felváltott vagy történeti tartalom nem maradhat párhuzamos aktív igazságforrásként.

---

## 1. Aktív fájlok

### 1.1 Hivatalos szabályforrások

- `../rules/sources/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.5v.docx`;
- `../rules/sources/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4.1v.docx`.

Státusz: `ACTIVE_CANONICAL_RULE_SOURCE`

Védett dokumentumok; tartalmi módosítás csak külön emberi döntéssel.

A főforrások jelenlegi current authority szerepe ettől függetlenül megmarad.
A későbbi szerkezeti újratervezés külön dokumentációs/design feladat, nem része ennek a szinkronkörnek.

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

- `../project/planning/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.9.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.12.md`;
- jelen `README.md`;
- `../project/status/checkpoints/ENGINE_CHECKPOINT.md` v2.0.

Current fő roadmap:

`M5 / Combat + Victory Core → VS1 / M6 → szükséges köztes mérföldkövek → AETERNA 0.0.1`

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

- `../project/planning/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.9.md`;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.12.md`.

A fájlnévben verziózott current dokumentum új verzióra lépésekor ugyanaz a dokumentum
frissül és rename-elődik. A régi active copy nem marad párhuzamosan.

A Git history őrzi a korábbi current verziót; külön Archive-példány csak valódi történeti/archív
szerep esetén indokolt.

## 4. Ownership szerint rendezett governance és testing dokumentumok

Az operatív governance és testing dokumentumok current helye:

- `../project/governance/workflows/GITHUB_WORKFLOW.md`;
- `../project/requirements/testing/TEST_STRATEGY_AND_PROFILES.md`;
- `../project/requirements/testing/SEED_AND_REPRODUCIBILITY_CONVENTION.md`.

Az ownership szerint rendezett design dokumentumok current helye:

- `../design/card_design/AETERNA – KÁRTYATERVEZÉSI KATALÓGUS ÉS HASZNÁLHATÓ ELEMEK 1.1v.md`;
- `../design/concepts/AETERNA – ÖTLETLÁDA ÉS NYITOTT TERVEK 1.1v.md`;
- `../design/naming/Általános névprofil-sablon.md`;
- `../design/research/Master Duel  Hearthstone tanulságok v0.1.md`.

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

- `../project/status/checkpoints/ENGINE_CHECKPOINT.md`.

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

`0862e1002dbef81ee203852714d377592272a0e9` – `engine: add aeternal outcome and terminal match result`

Current lezárt foundation többek között:

- runtime package/publish;
- Wellspring / Beáramlás;
- Magnitúdó/Aura preflight;
- Domain és `play_card`;
- canonical ability/effect runtime foundation;
- damage/vitals;
- modifier/keyword/duration;
- draw/reference runtime;
- Explicit Phase Foundation v1;
- Reaction / Priority Foundation v1;
- Combat + Pecsét Foundation C0–C6;
- terminal Aeternal / `MatchResult` victory core.

Combat + Pecsét C0–C6:

`COMPLETE_AND_ACCEPTED`

Final acceptance:

- Debug/Release C#: `301/301 PASS`;
- targeted C6: `8/8 PASS`;
- determinism/reference: `100/100 PASS`;
- canonical SHA:
  `97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`;
- Python isolated: `465/465 PASS` + 5 skip;
- exporter: `23/23 PASS`;
- Godot C# positive/negative smoke: PASS;
- unresolved P0/P1: `0/0`.

Learning/OQ current:

- registry/project records: `59`;
- current local source: `58`;
- project analyses: `30`;
- OQ: `52 answered / 15 partly_answered / 7 deferred / 0 open`.

Következő major product-facing cél:

`VS1 / M6 – első ténylegesen játszható vertical slice`

Canonical VS1 deckek:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

VS1 előtt nem válik automatikusan minden future engine-hiány kötelezővé.
Csak tényleges deck/mechanic blocker vagy általános rules-correct / deterministic / viewer-safe invariáns kötelező.

## 9. Dokumentumnév- és verziószabály

- Stabil szerepű engine-dokumentum fájlneve lehet verziószám nélküli, de belső verzióblokk kötelező.
- Projektterv és projekt-térkép verziója a fájlnévben is szerepel.
- Fájlnévben verziózott current dokumentum ugyanazon fájl frissítésével + rename-jével lép új verzióra.
- Régi és új verzió nem maradhat párhuzamos active authority-ként.
- Git history a normál current verziótörténet.
- Archive csak valódi történeti/deprecated/replaced szerephez kell; verzióemelés önmagában nem archiválási ok.
- `CURRENT_`, `new`, `final`, `copy`, `másolat` nem maradhat indokolatlan tartós aktív név.
- Minden aktív Markdown-dokumentumban legyen verzió, dátum és státusz.

## 10. Dokumentációs állapot

A nagy archiválási és cleanup-szakasz: `COMPLETE`.

A jelenlegi célzott szinkron a Combat + Pecsét C0–C6 lezárás utáni current-truth
dokumentációs frissítés.

Current szerkesztési elv:

```text
committed current file
→ Git/Archive history comparison
→ targeted patch
→ diff/consistency review
→ human commit/push
```

Nem indul új tömeges cleanup.

Frissítendő csak az, ami:

- későbbi technikai mérföldkő miatt ténylegesen elavul;
- rossz aktuális állapotot közöl;
- authority- vagy contractváltozást követ;
- közvetlenül érintett státusz- vagy irányító dokumentum.

A hivatalos főforrások későbbi szerkezeti újratervezése külön tervezett munka,
de nem változtatja meg a jelen dokumentációs szinkron sorrendjét.

## 11. Visszaellenőrzési minimum

Dokumentációs frissítés lezárása előtt ellenőrizni kell:

1. projektterv/projekt-térkép/checkpoint összhang;
2. current rules authority: Core `1.5v`, Expansion `1.4.1v`;
3. elavult `v6.8 / v1.11` vagy régebbi aktuális hivatkozások;
4. Reaction-only vagy Combat-még-nincs stale roadmapok;
5. `CURRENT_*` authority-hivatkozások;
6. archív fájl aktívként hivatkozása;
7. generált output canonicalként hivatkozása;
8. OQ aggregate `52 / 15 / 7 / 0`;
9. Git diff és stage-scope;
10. TEMP/build/cache kizárása.
