---
artifact_id: AET-DOC-CARD-DATA-WORKFLOW
kind: document
type: workflow
version: "1.0"
lifecycle: active
integration: current
authority: operational-workflow
generated: false
depends_on:
  - AET-DOC-CARD-DATA-MODEL
  - AET-DOC-DOCUMENT-GOVERNANCE
supersedes: []
---

# AETERNA canonical kártyaadat-munkafolyamat

## Dokumentumállapot

**Verzió:** 1.0

**Dátum:** 2026-09-24

**Státusz:** aktív current workflow

**Artifact ID:** `AET-DOC-CARD-DATA-WORKFLOW`

## 1. Cél

Ez a dokumentum a canonical kártyaadat kontrollált operatív folyamatát szabályozza:

```text
edit
-> validate
-> review
-> decide
-> canonical build
-> parity/quality gate
-> publish
-> rollback/archive
```

A workflow célja, hogy minden változás egyértelmű authorityvel, kiszámítható ellenőrzéssel, reprodukálható outputtal és teljes megőrzési lánccal történjen.

## 2. Editing authority

### 2.1 Current canonical források

- `CARDDATABASE.xlsx`: canonical human-editing és card-data authority;
- `REGISTRY.xlsx`: canonical technical schema, value, alias és contract authority.

A workbookok current pathja az `Aeterna dokumentációk/` könyvtár. Későbbi `data/canonical/` move csak külön, reference rewrite-tal együtt végrehajtott hullámban történhet.

### 2.2 Frozen compatibility források

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `LOOKUPS.xlsx`;
- legacy `cards.xlsx` és származtatott exportok.

Ezek read-only migration/provenance vagy compatibility inputok. Nem fogadnak current szerkesztést, és nem írhatják felül automatikusan a canonical forrásokat.

## 3. Change-set mint munkegység

A current munkegység:

```text
controlled table / field / domain change-set
```

A legacy „10-card batch” használható emberi review-méretként, de nem normatív adatcontract. A teljes 22 vagy 43 oszlopos sor újragenerálása nem current alapmódszer. Csak az indokolt canonical rekordok és mezők változhatnak; kapcsolódó child-table rekordokat explicit módon kell kezelni.

Minden change-set tartalmazza:

1. cél és scope;
2. érintett artifact, workbook, tábla és rekord identity;
3. authority és dependency;
4. before/after evidence;
5. schema- és referenciális hatás;
6. semantic review igény;
7. teszt- és publish-hatás;
8. rollback és preservation alap.

## 4. Előkészítés és edit

Edit előtt kötelező:

- branch, HEAD és worktree baseline;
- forrásfájl SHA-256 vagy más stabil source identity;
- a megfelelő canonical owner kiválasztása;
- az executable schema és controlled value ellenőrzése;
- párhuzamos vagy historical authority kizárása;
- target és rollback meghatározása.

Az edit nem történhet generált exportban, runtime package-ben, frozen legacy workbookban vagy Archive-példányban.

## 5. Validation gate

### 5.1 Schema validation

Ellenőrizni kell a required mezőket, típust, null/TBD policyt, primary identityt, egyediséget, manifestet és aktív schema-verziót. A workbook schema és REGISTRY executable definíciói a végrehajtható contract.

### 5.2 Referential integrity

Minden külső kulcsnak és child-table kapcsolatnak feloldhatónak kell lennie. Kiemelt kapcsolatok:

- Card_ID → lokalizáció, printing, keyword, trait, ability és deck entry;
- ability → trigger, condition, target, cost, effect és parameter;
- effect/template/value → REGISTRY identity;
- Deck_ID → DECKS;
- Print_ID → Card_ID és Set_ID.

### 5.3 Controlled values és aliasok

Új canonical value csak a megfelelő REGISTRY owner és review alapján jöhet létre. Alias explicit targettal és normalizációs móddal kerülhet be. Legacy string előfordulása nem elegendő.

### 5.4 Semantic review

A strukturálisan valid adat lehet szemantikailag hibás. Human review kötelező többek között:

- kártyaszöveg és executable ability graph megfelelésénél;
- trigger/target/condition/effect jelentésénél;
- név, realm, clan, race/class vagy set kontextus változásánál;
- deck-purpose és product kapcsolatnál;
- legacy lookup/alias migrációnál.

### 5.5 Runtime representation és source identity

A canonical buildnek a deklarált source identitykből kell készülnie. Ellenőrizni kell a source hash-eket, tool identityt, determinisztikus outputot, manifestet, referenciákat és consumer contractot.

## 6. Review és döntés

A reviewer a change-set scope-ját, authorityjét, tartalmi helyességét, tesztevidenciáját, migrációs kockázatát és preservation tervét ellenőrzi. Az elfogadás nem következhet pusztán abból, hogy a workbook megnyitható vagy az export lefut.

A döntések négy állapota külön kezelendő:

- **active unresolved work item:** további munka vagy emberi döntés szükséges;
- **accepted durable decision:** current workflowban és jövőbeli változtatásnál irányadó;
- **historical audit evidence:** teljes eredetiben megőrzendő, de nem current utasítás;
- **migration provenance:** forrás–cél átvezetést és indoklást bizonyít.

Egy historical sor nem marad current teendőként csak azért, mert a legacy workbookban szerepel.

## 7. Jövőbeli review ledger

A tervezett current owner:

```text
data/workflows/DATA_REVIEW_LEDGER.xlsx
```

Feladata az aktív audit itemek, durable döntések és controlled workflow statusok kezelése. Nem kártyaadat-authority, és nem veszi át a teljes legacy audit historyt. A teljes eredeti `AUDIT_LOG` és `DECISION_LOG` a MUNKAFORRÁS historical példányában marad meg.

A ledger W3B.2/W3B.3 scope; W3B.1 nem hozza létre.

## 8. Naming review

A `NAME_PROFILE` vagy jövőbeli `CARD_NAME_REVIEWS.xlsx` névjavaslatai design-review inputok. Canonical névváltoztatás előtt kötelező:

1. a Card_ID és aktuális kontextus friss ellenőrzése;
2. explicit accept/reject döntés;
3. lokalizációs és hivatkozási hatásvizsgálat;
4. külön CARDDATABASE change-set;
5. audit/provenance bejegyzés.

Javasolt név nem írható automatikusan a canonical lokalizációba.

## 9. Deck- és product-review

```text
Product_ID != Deck_ID
```

A reviewer külön osztályozza a commercial/distributable productot, starter decket, test decket, playtest decket és canonical gameplay decket. Legacy deck nem válik canonical gameplay deckké automatikusan. Canonical `DECKS`/`DECK_ENTRIES` promotion előtt gameplay-eligibility, kártyareferencia, mennyiség, sorrend és lifecycle review szükséges.

A product/distribution adatok jövőbeli ownere a `PRODUCT_CATALOG.xlsx`; létrehozása nem W3B.1 feladat.

## 10. Ability- és lookup-migráció

Legacy structured hint és canonical executable ability graph között nincs automatikus ekvivalencia. A változtatás per-card mappinget, human semantic review-t, registry/template feloldást és runtime behavior tesztet igényel.

A LOOKUPS, embedded lookup és REGISTRY reconciliation állapota:

```text
P04 / HD-07 lookup semantic reconciliation = OPEN
```

A W3B.0 187 azonos `Lookup_Group + Value` mappingje részleges evidence view, nem teljes parity bizonyíték. W3B.1 nem migrál lookupot és nem oldja fel HD-07-et.

## 11. Canonical build és quality gate

A target buildút:

```text
CARDDATABASE + REGISTRY
-> tools/data
-> TEMP validated candidate
-> generated runtime package
```

A quality gate legalább:

- production canonical validation;
- referential és controlled-value ellenőrzés;
- determinisztikus ismételt build;
- manifest- és file-hash ellenőrzés;
- card/deck/lookup/ability coverage;
- consumer contract tests;
- legacy parity csak evidence-ként, silent fallback nélkül;
- unresolved eltérések explicit döntési kapuja.

## 12. Publish

Csak teljesen validált TEMP candidate publikálható. A publish atomikus vagy biztonságosan visszagörgethető legyen, és rögzítse:

- canonical source identityket;
- exporter/materializer identityt;
- package identityt és verziót;
- tartalmi hash-eket;
- validation eredményt;
- publish célpathot.

A runtime package generált representation. Nem szerkeszthető authorityként és nem ír vissza a workbookokba.

A current pipeline legacy inputja átmeneti. A producer/consumer cutover után legacy fallback tilos. Ennek implementációja későbbi W3B hullám.

## 13. Rollback és preservation

Kötelező policy:

```text
NO FILE-LEVEL LOSS
```

Jelentése:

- teljes durable fájl nem veszhet el;
- Git history önmagában nem preservation owner;
- current szerepből kivont fájl dispositiont és durable targetet kap;
- ha nincs más current/historical owner, Archive-ba kerül;
- existing Archive content immutable;
- új historical intake append-only;
- permanent whole-file deletion csak explicit emberi kivétellel lehetséges.

Rollbacknál a canonical source, a generált package és a consumer config konzisztens verziójára kell visszaállni. Egy későbbi változás nem használhatja a frozen legacy source-t rejtett fallbackként.

## 14. Archive handoff

Retired durable source csak akkor hagyhatja el current pathját, ha:

1. target szerepe és replacementje rögzített;
2. minden szükséges current tartalom promóciója vagy historical dispositionje lezárt;
3. active consumer/reference nincs;
4. exact source hash ismert;
5. collision-ellenőrzött Archive target létezik;
6. source és Archive hash azonos;
7. intake manifest rögzíti a provenance-t;
8. a current build és consumer teszt az old path nélkül is PASS.

Elvárt verdict:

```text
verified exact Archive owner
```

Archive-példány nem current authority és nem módosítható.

## 15. W3B.1 current határ

W3B.1 kizárólag a current adatmodell- és workflow-dokumentációt, a négy recovery input exact archiválását, a közvetlen current reference-eket és artifact-governance nézeteket változtatja.

Nem része:

- canonical workbook rekord- vagy path-módosítás;
- PRODUCT_CATALOG, DATA_REVIEW_LEDGER vagy CARD_NAME_REVIEWS létrehozása;
- lookup/ability/product/deck/naming promotion;
- runtime producer vagy consumer módosítás;
- HD-01–HD-08 feloldása;
- MUNKAFORRÁS, LOOKUPS vagy cards.xlsx retirementje.
