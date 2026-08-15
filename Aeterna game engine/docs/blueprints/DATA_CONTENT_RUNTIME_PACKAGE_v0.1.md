# AETERNA – DATA / CONTENT / RUNTIME PACKAGE BLUEPRINT

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** architecture blueprint / current data architecture formalization
- **Javasolt repository-útvonal:** `Aeterna game engine/docs/blueprints/DATA_CONTENT_RUNTIME_PACKAGE_v0.1.md`
- **Repository-bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Rules authority:** official AETERNA sources
- **Nem új data-authority dokumentum.**

---

# 1. Cél

Előre rögzíteni a teljes content lifecycle-t:

```text
human authority
→ authoring data
→ normalized/canonical data
→ verified runtime package
→ consumer projections/exports
→ release/update
```

úgy, hogy később expansion, localization, AI, web/API és online release is ugyanarra az identity/versioning alapra épüljön.

---

# 2. Authority hierarchy – megtartandó

```text
Official Rules Sources
        ↓
Accepted Human Decisions
        ↓
Human Editing Source (XLSX + LOOKUPS)
        ↓
Normalization / Validation
        ↓
Canonical Derived Data
    CARDDATABASE.xlsx
    REGISTRY.xlsx
        ↓
Runtime Package / Consumer Exports
```

**Derived adat nem emelkedik vissza human/rules authorityvé.**

---

# 3. Data domainok

## 3.1 CardDefinition

Rules-releváns és card identity adat.

Nem runtime card instance.

## 3.2 Ability/Effect Module Registry

Executable capability identity és parameter schema.

## 3.3 Localization

Language-specific display/card text.

## 3.4 Format/Activation Policy

Mely content:
- base;
- expansion;
- booster;
- future format

számára aktív/legal.

## 3.5 Deck/Product Definitions

Starter deck / predefined list / product composition.

## 3.6 Asset Metadata

Art, icon, audio, visual resource reference + provenance.

E domainok fizikailag lehetnek részben közös workbookban, de semantics szinten különüljenek el.

---

# 4. Identity namespaces – candidate

```text
card:<stable-card-id>
ability:<module-id>
effect:<effect-id>
keyword:<keyword-id>
format:<format-id>
expansion:<expansion-id>
product:<product-id>
localization:<key>
asset:<asset-id>
```

A konkrét string prefix nem kötelező.

Alapelv:
- stable;
- language-independent;
- order-independent;
- unique within namespace;
- deprecated ID nem reuse-olható más semantic objectre.

---

# 5. Package identity/versioning

A current canonical loader már jó alap.

Minimum semantics:

```text
PackageId
PackageFormatVersion
SchemaVersion
DataVersion
GeneratedAt
GeneratorVersion
SourceFingerprint
DependencyFingerprints
```

A jelenlegi manifest struktúrába csak azt emeljük be, ami ténylegesen szükséges; nem kell mezőszaporítás önmagáért.

---

# 6. Dependency model

Példa:

```text
CardDatabasePackage
requires
RegistryPackage >= required schema/data version
```

Később:

```text
LocalizationPackage
requires CardDefinition IDs

FormatPackage
requires Card/Expansion IDs
```

Dependency explicit manifestben/metadata-ban.

---

# 7. Human override registry – migration/tooling candidate

Nem minden manuális javításnak kell special Python branch.

Candidate:

```text
OverrideEntry
- OverrideId
- TargetDomain
- TargetId
- FieldPath
- ExpectedValue/Fingerprint
- Replacement
- Reason
- AuthorityReference
- AppliesFromVersion
- ExpiresAtVersion?
```

Use case:
- import normalization exception;
- known source typo;
- migration correction.

Nem use case:
- új gameplay rule megírása.

---

# 8. Build pipeline

```text
1. load human source
2. structural validation
3. normalize aliases/sentinels/enums
4. resolve IDs/references
5. generate canonical tables
6. schema validation
7. cross-table referential validation
8. ability/effect registry compatibility validation
9. localization consistency validation
10. format/activation validation
11. diagnostics/build report
12. changed-record review artifact
13. publish gate
14. runtime package/export
15. fingerprints
```

Development mód lazíthat bizonyos sentinel szabályokon.

Production publish gate nem.

---

# 9. Partial rebuild

Későbbi performance optimization.

Csak akkor:
- generator/schema compatible;
- dependency fingerprints kompatibilisek;
- végén full semantic validation fut.

Mismatch:
```text
full rebuild required
```

---

# 10. Localization

Canonical identity language-independent.

Candidate:

```text
LocalizedCardText
- CardDefinitionId
- Language
- Name
- RulesTextDisplay
- FlavorText
- UI labels
```

Fontos:
- executable rules nem natural-language localizationből értelmeződnek;
- structured ability/effect data marad canonical.

## Consistency audit

Nyelvek között:
- ugyanaz card ID set;
- structural fields invariant;
- text-only differences permitted.

---

# 11. Human card text vs executable semantics

A printed/display rules text:
- human source;
- játékos számára authority text lehet a design dokumentum szerint;

de runtime execution:
- typed ability/effect/module data.

A kettő között coverage/consistency audit kell.

Ne legyen runtime natural-language parser a production authority alapja.

---

# 12. Engine capability vs content coverage

## EngineCapabilityManifest

Mit tud a C# runtime általánosan?

Például:
- damage;
- draw;
- move;
- modifier;
- keyword grant;
- reaction later.

## ContentCoverageReport

A current contentből mennyi:
- structured;
- executable;
- partially supported;
- unsupported;
- manual exception.

Ez külön report.

A régi `engine_support.json` jellegű sample metadata ne írja felül a production engine capabilityt.

---

# 13. Package support státuszok – candidate

```text
NOT_EVALUATED
DECLARED_ONLY
STRUCTURED
EXECUTABLE
PARTIAL
UNSUPPORTED
BLOCKED_BY_RULES
```

A pontos enum későbbi decision.

Egy card több abilityje külön coverage-et is kaphat.

---

# 14. Format/expansion activation

Külön policy:

```text
ContentDefinition exists
→ Package installed
→ Format permits
→ MatchConfig enables
```

A base-game audit nem aktiválhat expansion-only mechanicot pusztán azért, mert az adat ott van.

Ez különösen fontos az AETERNA jelenlegi base/expansion authority-szabályához.

---

# 15. Consumer exports

Canonicalból generálható:

```text
Engine Runtime Package
Godot Catalog
Website/API Export
AI/Balance Dataset
Localization Bundle
Print/Design Export
Release Delta
```

Mind derived.

Consumer nem ír vissza canonical source-ba.

---

# 16. Runtime package candidate layout

A jelenlegi package spec jó kiinduló pont:

```text
manifest.json
cards.jsonl
decks.jsonl
lookups/
aliases/
ability_registry.json
engine_support.json
build_report.json
diagnostics.jsonl
```

Hosszú távon felmerülhet:

```text
localization/
formats/
assets_manifest.json
coverage_report.json
```

De csak tényleges use case-nél.

---

# 17. Publish gate

Production publish FAIL, ha például:
- duplicate semantic ID;
- missing required table;
- invalid dependency version;
- dangling card/ability/effect reference;
- forbidden sentinel;
- unsupported mandatory mechanic policy;
- missing required localization policy szerint;
- format references nonexistent content;
- package fingerprint inconsistent.

Warnings külön kategória.

---

# 18. Release provenance

Release manifest később tartalmazhat:
- source commit/fingerprint;
- generator version;
- canonical package hashes;
- engine build version;
- rules source version;
- third-party asset/license manifest.

Ez megkönnyíti:
- bug reproduction;
- replay compatibility;
- support.

---

# 19. Delta/update

V1 nem szükséges.

Később:

```text
BasePackageHash
TargetPackageHash
ChangedArtifacts
DeletedArtifacts
```

Delta csak transport optimization.

Full target package mindig reprodukálható.

---

# 20. Security/trust boundary

Runtime ne töltsön arbitrary executable package codeot csak azért, mert package-ben van.

Executable ability/module code:
- compiled engine;
- allowlisted/versioned module system;
- később sandbox/mod policy külön blueprint.

External/user package:
- data capability;
- schema validation;
- explicit trust policy.

---

# 21. Current migration priorities

Nem kell azonnal újraformázni a teljes adatstack-et.

Rövid táv:
1. tartsuk meg CARDDATABASE/REGISTRY canonical role-t;
2. tartsuk meg CanonicalPackageLoader gate-et;
3. Reaction/ability fejlesztés közben registry IDs maradjanak stabilak;
4. static sample runtime package support metadata ne legyen production capability authority;
5. következő valódi package migrationkor coverage report és fingerprint model pontosítható.

---

# 22. Non-goal

- database technology újraválasztása;
- XLSX megszüntetése;
- web CMS építése;
- full mod marketplace;
- asset CDN;
- localization platform;
- delta updater implementation;
- OCR pipeline.

---

# 23. Acceptance invariants későbbi package fejlesztéshez

1. same source → deterministic canonical output;
2. stable IDs;
3. schema version enforced;
4. dependency version enforced;
5. dangling references blocked;
6. production sentinel blocked;
7. support coverage not confused with engine capability;
8. localization cannot change rules structure;
9. format cannot create nonexistent content;
10. consumer package fully derived/rebuildable;
11. current package fingerprint recorded;
12. no manual runtime-only authority edits.

---

# 24. Változásnapló

## 0.1 – 2026-08-15
- current AETERNA data stack formalizálva;
- identity/domain/version/dependency rétegek rögzítve;
- correction/override registry candidate hozzáadva;
- localization/format/coverage különválasztva;
- consumer export és release provenance irány rögzítve;
- sample support metadata és production engine capability határa megerősítve.
