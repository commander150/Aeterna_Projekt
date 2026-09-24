---
artifact_id: AET-DOC-CARD-DATA-MODEL
kind: document
type: specification
version: "1.0"
lifecycle: active
integration: current
authority: technical-contract
generated: false
depends_on:
  - AET-DOC-DOCUMENT-GOVERNANCE
  - AET-DOC-PROJECT-PLAN
supersedes: []
---

# AETERNA kártyaadatmodell

## Dokumentumállapot

**Verzió:** 1.0

**Dátum:** 2026-09-24

**Státusz:** aktív current specifikáció

**Artifact ID:** `AET-DOC-CARD-DATA-MODEL`

## 1. Cél és hatókör

Ez a dokumentum az AETERNA kártya- és kapcsolódó technikai adatok current tulajdonlási, identitási és szerkezeti elveit rögzíti. Meghatározza:

- a canonical szerkesztési és technikai forrásokat;
- a workbookok és normalizált táblák felelősségi határát;
- a fő azonosítók szemantikáját;
- a schema-, value-, alias- és contract-authorityt;
- a legacy compatibility és migráció határát;
- az authoring source és a generált runtime representation kapcsolatát.

A dokumentum nem hivatalos játékszabályforrás, nem termékterv, és nem helyettesíti a workbookok végrehajtható schema- és validation-definícióit.

## 2. Canonical authority model

### 2.1 `CARDDATABASE.xlsx`

`CARDDATABASE.xlsx` a canonical human-editing source és a canonical card-data authority. A kártyaidentitás, lokalizáció, nyomtatás, játékmeneti deck, strukturált képesség és kártyakapcsolat current adatai itt élnek a workbook saját schema- és validation-contractja szerint.

Current fizikai path:

```text
Aeterna dokumentációk/CARDDATABASE.xlsx
```

A későbbi kontrollált célpath:

```text
data/canonical/CARDDATABASE.xlsx
```

A fizikai move külön implementációs hullám. Ez a dokumentum nem hajtja végre.

### 2.2 `REGISTRY.xlsx`

`REGISTRY.xlsx` a canonical technical schema-, value-, alias- és contract-authority. A kontrollált technikai szókészlet, normalizációs aliasok, validation rule-ok, source- és migration-identitások, contract schemák és ability template-ek végrehajtható definícióit tartalmazza.

Current fizikai path:

```text
Aeterna dokumentációk/REGISTRY.xlsx
```

A későbbi kontrollált célpath:

```text
data/canonical/REGISTRY.xlsx
```

### 2.3 Közös authority

A két workbook együtt adja a jövőbeli canonical runtime-forrást:

```text
CARDDATABASE + REGISTRY
-> canonical tooling
-> validált, determinisztikus runtime representation
```

Egyik workbook sem általános helyettesítője a másiknak. A CARDDATABASE üzleti és játéktartalmi rekordjai a REGISTRY technikai fogalmaira és contractjaira támaszkodhatnak; a REGISTRY nem válik kártyasor-authorityvé.

## 3. Végrehajtható contract és normatív magyarázat

Az executable data contract forrásai:

```text
CARDDATABASE/REGISTRY schema tables
+ validation definitions
+ export manifests
+ REGISTRY contract definitions
```

Ez a Markdown normatív magyarázó és governance specifikáció. Nem másolja kézzel a workbookok teljes oszlop- és validation-sémáját, mert az két párhuzamos contractot hozna létre.

Ha a dokumentum és az executable workbook contract eltér:

```text
BLOCKING GOVERNANCE DEFECT
```

Az eltérés feloldásáig nincs silent prose override és nincs silent workbook override. A változtatásnak meg kell neveznie az authorityt, a migrációt, a tesztet és a dokumentációs hatást.

## 4. Azonosító-szemantika

### 4.1 `Card_ID`

`Card_ID` a szabályi/logikai kártya stabil identitása. Nem nyomtatási azonosító, nem collector number, nem lokalizált név és nem fájlpozíció. A név, nyomtatás, art vagy termékkapcsolat változása önmagában nem hoz létre új `Card_ID`-t.

### 4.2 `Print_ID`

`Print_ID` egy konkrét kártyanyomtatás identitása. A `Card_ID`-ra hivatkozik, és a set, collector, rarity, treatment, art, language, státusz és reprint adatokkal együtt írja le a nyomtatást. Nem használható szabályi kártyaidentitásként.

### 4.3 `Set_ID` és `Collector_Number`

`Set_ID` a kiadási készlet stabil identitása. `Collector_Number` a nyomtatás készleten belüli gyűjtői azonosítója; önmagában nem globális kártyaazonosító. Az egyediség és kötelezőség pontos szabályát a canonical schema és validation rule határozza meg.

### 4.4 `Deck_ID`

`Deck_ID` egy deck-definíció identitása. A canonical gameplay deckek és tagságuk a CARDDATABASE `DECKS` és `DECK_ENTRIES` tábláiban élnek. Legacy starter-, test- vagy playtest-deck nem válik automatikusan canonical gameplay deckké.

### 4.5 `Product_ID`

`Product_ID` kereskedelmi vagy disztribúciós termék identitása. Nem azonos a `Deck_ID`-val. Egy termék több decket is tartalmazhat, egy deck pedig külön döntés alapján kapcsolódhat termékhez. A jövőbeli product/distribution owner a `PRODUCT_CATALOG.xlsx`; ez még nem létezik, létrehozása W3B.2/W3B.3 feladat.

### 4.6 Ability- és effect-azonosítók

Az `ability_id`, template-, node-, trigger-, condition-, target-, cost-, effect-, parameter-, duration-, usage-limit-, choice- és expression-azonosítók a normalizált ability graph rekordjait kötik össze. Jelentésüket a CARDDATABASE táblák, a REGISTRY template/contract definíciók és a validation rule-ok együtt adják.

Legacy természetes szöveg vagy delimiterrel tagolt hint nem hozhat automatikusan canonical ability/effect azonosítót.

### 4.7 Canonical value és alias identity

A canonical technikai érték a REGISTRY value group és value identity szabályai szerint létezik. Az alias külön identitású bemeneti vagy migrációs leképezés, amely explicit canonical registry value-ra mutat. Alias nem válik canonical értékké pusztán előfordulás vagy gyakoriság alapján.

## 5. Normalizált canonical workbook model

### 5.1 Kártya és lokalizáció

- `CARDS`: logikai kártyaidentitás, típus, realm, osztályozás, alapértékek, lifecycle és provenance;
- `CARD_LOCALIZATION`: nyelvhez kötött név és lokalizált kártyaszöveg;
- `CARD_PRINTINGS`: nyomtatási identitás és kiadási tulajdonságok;
- `SETS` és `SET_LOCALIZATION`: készletidentitás és lokalizáció.

### 5.2 Deckek

- `DECKS`: canonical gameplay deck definíció;
- `DECK_ENTRIES`: rendezett, mennyiséggel ellátott kártyatagság.

Commercial product, starter, test és playtest deck külön domain-besorolást igényel. Csak jóváhagyott canonical gameplay deck kerül ezekbe a táblákba.

### 5.3 Képességek és hatások

A normalizált ability réteg többek között az alábbi táblacsaládot használja:

- `ABILITIES` és `ABILITY_TEMPLATE_ARGUMENTS`;
- `ABILITY_TRIGGERS`, `ABILITY_CONDITIONS`, `ABILITY_TARGETS`;
- `ABILITY_COSTS`, `ABILITY_EFFECTS`, `ABILITY_EFFECT_PARAMETERS`;
- `ABILITY_DURATIONS`, `ABILITY_USAGE_LIMITS`;
- `ABILITY_CHOICES`, `ABILITY_CHOICE_OPTIONS`, `ABILITY_EXPRESSIONS`;
- `EFFECT_TAGS` és `CARD_RELATIONS`.

A táblák tényleges mezőit, required/null szabályait és referenciáit az executable schema határozza meg.

### 5.4 Kulcsszavak és trait-ek

`CARD_KEYWORDS` és `CARD_TRAITS` normalizált many-to-many kapcsolatot képviselnek. A canonical érték identity a REGISTRYből származik; delimiterrel összefűzött legacy cella csak migrációs input.

### 5.5 Registry és contract réteg

A REGISTRY fő felelősségi csoportjai:

- `VALUE_GROUPS`, `VALUE_REGISTRY`, `VALUE_RELATIONS`, `ALIASES`, `LOCALIZATION`;
- rules-, event-, reference-, operator-, target-, cost-, effect-, modifier-, restriction-, duration-, timing- és usage-policy registryk;
- `SOURCE_REGISTRY` és `MIGRATION_MAP`;
- `VALIDATION_RULES`;
- `CONTRACT_SCHEMAS` és `CONTRACT_FIELDS`;
- ability template-ek, node-ok és bindingok.

## 6. Érték-, null- és delimiter-szabály

A canonical export contract a workbook metadata és schema alapján kezeli a `#NULL` és `#TBD` sentinel értékeket. Production exportban a schema által tiltott vagy unresolved `#TBD` blocking hiba. Az üres cella, a `blank`, a `none`, a `#NULL` és a domainbeli „nincs” jelentés nem cserélhető fel automatikusan.

Normalizált child-table kapcsolatnál külön rekordok az authorityk. Ha egy canonical mező kifejezetten többértékű szöveges reprezentációt enged, a deklarált delimiter-policyt kell követni; legacy vessző, pontosvessző vagy szabad szöveg nem írhatja felül a schema szabályát.

## 7. Product/data boundary

```text
CARDDATABASE
= gameplay és card identity

REGISTRY
= technical vocabulary, schema és contract

future PRODUCT_CATALOG
= product és distribution planning
```

A jövőbeli `PRODUCT_CATALOG.xlsx` tervezett felelőssége a product identity, product–deck kapcsolat, generation profile, printing–product kapcsolat, set release policy és esetleges booster pool. Nem része a canonical runtime-authority párnak, és nem jön létre W3B.1-ben.

## 8. Naming boundary

A legacy `NAME_PROFILE` 814 soros design-review dataset. A benne szereplő javaslat:

```text
not canonical card name
```

Tervezett owner:

```text
design/naming/reviews/CARD_NAME_REVIEWS.xlsx
```

Ez a dataset W3B.2/W3B.3 scope. Canonical névváltoztatás csak explicit accept/reject döntés, friss kontextusellenőrzés és külön CARDDATABASE módosítás után történhet.

## 9. Legacy compatibility és migrációs modell

Az alábbi rétegek nem current authoring authorityk:

- `cards.xlsx`: hét realm-lapos legacy kártyasnapshot és compatibility/import evidence;
- legacy 22-column structure: egyszerűsített import/runtime-előkészítő forma;
- `CARDS_MASTER` 43-column structure: korábbi szerkesztési, audit- és migrációs munkalap;
- MUNKAFORRÁS 21 sheetje: frozen migration/provenance és átmeneti compatibility input;
- `LOOKUPS.xlsx` runtime-, alias-, workflow-, product- és design-rétegei: frozen legacy-pipeline input;
- a MUNKAFORRÁS embedded lookup lapjai: migrációs és összehasonlítási evidence.

Ezekből adat csak explicit disposition, target owner, semantic review és reconciliation evidence alapján emelhető át. A teljes MUNKAFORRÁS és LOOKUPS a consumer cutover után historical Archive artifact lesz.

## 10. Structured ability migration

```text
legacy structured hints != canonical executable ability graph
```

A legacy `Képesség_Canonical`, zone, keyword, trigger, target, effect-tag, duration, condition, machine-description és engine-note mezők leíró vagy compatibility információt hordozhatnak. Nem bizonyítják automatikusan a canonical ability node-ok, paraméterek, referenciák és runtime semantics ekvivalenciáját.

A migráció `LOSS_RISK`. Kötelező:

1. per-card mapping;
2. semantic human review;
3. REGISTRY value/template resolution;
4. referential validation;
5. runtime-required behavior tests;
6. explicit retirement acceptance.

## 11. Lookup migration caveat

A `LOOKUPS.xlsx`, a MUNKAFORRÁS embedded lookup rétege és a REGISTRY közötti semantic reconciliation nincs lezárva.

```text
P04 / HD-07 lookup semantic reconciliation = OPEN
```

A W3B.0 `Lookup_Group + Value` evidence view 187 közös kulcsnál azonos canonical value-t talált. Ez egy részleges összehasonlítási nézet. Nem bizonyít teljes mapping parityt, nem oldja fel a korábbi alias- és domain-szemantikai eltéréseket, és nem jogosít automatikus migrációra.

## 12. Runtime authority boundary

Az authoring source nem runtime package. A target adatút:

```text
CARDDATABASE + REGISTRY
-> tools/data
-> TEMP validated candidate
-> generated runtime package
```

A runtime package determinisztikus, validált, source hash-ekkel és tool identityvel rendelkező representation. Nem szerkesztési authority és nem ír vissza a canonical workbookokba.

A current runtime pipeline átmenetileg még MUNKAFORRÁS/LOOKUPS inputot is használ. Ennek eltávolítása későbbi producer/consumer cutover. A target állapotban nincs legacy canonical fallback.

## 13. Változtatási és review-követelmény

Canonical adatváltozásnak azonosítható change-setben kell történnie. A change-set megnevezi:

- az érintett authorityt és táblákat;
- az identitás- és lifecycle-hatást;
- a schema/registry függőséget;
- a migrációs és compatibility hatást;
- a validációt és semantic review-t;
- a runtime representation tesztjét;
- a provenance-t és rollback alapot.

Az operatív folyamat authorityje az `AET-DOC-CARD-DATA-WORKFLOW`.

## 14. Current migrációs kapuk

W3B.1 nem migrál workbook-adatot. Nyitott marad:

- P01 structured ability/hint mapping;
- P02/P03 audit- és decision-owner kialakítása;
- P04/HD-07 lookup semantic reconciliation;
- product, deck, generation-profile és naming promotion;
- canonical runtime materializer és consumer cutover;
- canonical workbookok fizikai path-move-ja.

Ezek nyitottsága nem változtatja meg a jelen dokumentumban rögzített canonical authorityt.
