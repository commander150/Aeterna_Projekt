---
artifact_id: AET-DOC-CARD-DATA-WORKFLOW
kind: document
type: workflow
version: "1.1"
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

**Verzió:** 1.1

**Dátum:** 2026-09-25

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

## 7. Current review ledger schema-owner

A current owner:

```text
data/workflows/DATA_REVIEW_LEDGER.xlsx
```

Feladata az aktív audit itemek, durable döntések és controlled workflow statusok kezelése. A workbook W3B.2-ben üres business táblákkal és aktív schema-governance réteggel létrejött. Dataset identityje `AET-DATA-REVIEW-LEDGER`.

Nem kártyaadat-authority, nem rules authority, nem Archive-helyettesítő, és nem veszi át automatikusan a teljes legacy audit historyt. A teljes eredeti `AUDIT_LOG` és `DECISION_LOG` a MUNKAFORRÁS historical példányában marad meg. A 205 audit- és 151 decision-sor tartalmi triage-ja és promotionje továbbra is nyitott; W3B.2-ben business row nem került a ledgerbe.

## 8. Naming review

A `NAME_PROFILE` vagy a current schema-owner `design/naming/reviews/CARD_NAME_REVIEWS.xlsx` névjavaslatai design-review inputok. A workbook dataset identityje `AET-DATA-CARD-NAME-REVIEWS`, és W3B.2 után továbbra is 0 business sort tartalmaz. Canonical névváltoztatás előtt kötelező:

1. a Card_ID és aktuális kontextus friss ellenőrzése;
2. explicit accept/reject döntés;
3. lokalizációs és hivatkozási hatásvizsgálat;
4. külön CARDDATABASE change-set;
5. audit/provenance bejegyzés.

Javasolt név nem írható automatikusan a canonical lokalizációba. A schema létrejötte nem dönt a 391 eltérő proposalról, és nem javítja a 78 stale context cellát.

```text
proposal != canonical name
review acceptance != automatic CARDDATABASE write
```

## 9. Deck- és product-review

```text
Product_ID != Deck_ID
```

A reviewer külön osztályozza a commercial/distributable productot, starter decket, test decket, playtest decket és canonical gameplay decket. Legacy deck nem válik canonical gameplay deckké automatikusan. Canonical `DECKS`/`DECK_ENTRIES` promotion előtt gameplay-eligibility, kártyareferencia, mennyiség, sorrend és lifecycle review szükséges.

A product/distribution schema current ownere a `data/canonical/PRODUCT_CATALOG.xlsx`, dataset identityje `AET-DATA-PRODUCT-CATALOG`. A business táblák W3B.2-ben üresek. A 28 legacy deck konkrét osztályozása, a 17 productrekord és az 5 generation profile promotionje későbbi content-review.

A HD-03 szerkezeti döntés szerint a product identity, deck identity, product–deck relation és deck composition külön fogalom. A product-domain `DECKS` nem azonos a CARDDATABASE canonical gameplay `DECKS` táblájával; gameplay promotion csak külön elfogadás és CARDDATABASE change-set után történhet.

A `BOOSTER_POOLS` schema létezik, de `SCHEMA_ONLY / INACTIVE`, business row countja 0. Ez nem runtime authority, nem aktív booster feature és nem VS1-követelmény.

## 10. Ability- és lookup-migráció

Legacy structured hint és canonical executable ability graph között nincs automatikus ekvivalencia. A változtatás per-card mappinget, human semantic review-t, registry/template feloldást és runtime behavior tesztet igényel.

A LOOKUPS, embedded lookup és REGISTRY reconciliation állapota:

```text
P04 / HD-07 lookup semantic reconciliation = OPEN
```

A W3B.0 187 azonos `Lookup_Group + Value` mappingje részleges evidence view, nem teljes parity bizonyíték. W3B.2 nem migrál lookupot és nem oldja fel HD-07-et.

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

## 15. W3B.2 current határ

W3B.2 létrehozta a három governed, self-describing target schema-ownert, de legacy business/content sort nem promótált.

```text
PROMOTED_LEGACY_BUSINESS_ROWS = 0
P01–P10 = OPEN
```

Továbbra is nyitott emberi vagy content-döntés:

- HD-01 runtime mismatch truth;
- a 28 legacy deck lifecycle/classification és canonical gameplay-acceptance besorolása;
- a 17 legacy productrekord és 5 generation profile konkrét promotionje;
- a 391 eltérő névjavaslat, valamint a stale context rendezése;
- audit- és decision-sorok tartalmi triage-ja;
- P04 / HD-07 lookup semantic reconciliation;
- structured ability mapping, amely továbbra is `LOSS_RISK`;
- rarity design rationale targetja és konkrét content promotionje.

A schema-lét nem kényszerít VS1 content-döntést. A frozen source workbookok, runtime producer/consumer, canonical gameplay deckek és Archive tartalma W3B.2-ben nem változnak.
