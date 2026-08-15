# AETERNA – CROSS-PROJECT SYNTHESIS: DATA AND CONTENT PIPELINE

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első data/content/runtime-package synthesis
- **Javasolt repository-útvonal:** `learning/synthesis/topics/data_and_content_pipeline.md`
- **Nem AETERNA-authority.**

---

# 1. Evidence

Új targeted audit:
- BabelCDB;
- Distribution;
- LorcanaJSON.

Korábbi audit:
- ProjectIgnis/CardScripts;
- Fragment Forge;
- Arcomage;
- Forge;
- MAGE.

AETERNA current:
- human XLSX + LOOKUPS;
- Python normalize/validate;
- `CARDDATABASE.xlsx`;
- `REGISTRY.xlsx`;
- canonical loader;
- runtime package specification;
- Godot sample runtime package / support metadata.

---

# 2. P-DATA-001 – Human authoring, canonical data és runtime package külön authority

**Státusz:** `REPEATED_PATTERN`  
**AETERNA:** `ALREADY_ADOPTED`

```text
human/rules authority
→ editable source
→ normalize/validate
→ canonical derived data
→ runtime/distribution artifact
```

Visszafelé nincs authority promotion.

Runtime package kézi javítása nem írhatja felül az authoring/canonical source-t.

---

# 3. P-DATA-002 – Definition és implementation külön

BabelCDB vs CardScripts nagyon tiszta példát ad.

AETERNA:

```text
CardDefinition
Ability/Effect Module
```

külön identity és lifecycle.

Card definition hivatkozhat implementation/module ID-ra.

Publish gate ellenőrzi a referenciát.

---

# 4. P-DATA-003 – Stable semantic IDs

Közös minta:
- BabelCDB passcode primary key;
- Lorcana culture-invariant ID;
- AETERNA canonical primary key.

Candidate invariant:

> semantic identity ne függjön row ordertől, language-től vagy runtime object instance-től.

Külön identity domain lehet:
- card definition;
- ability module;
- effect module;
- format;
- expansion;
- localization key;
- printing/art variant.

---

# 5. P-DATA-004 – Schema/format version first-class

LorcanaJSON explicit formatVersion.

AETERNA canonical loader már explicit SchemaVersion/DataVersion és dependency minimumokat ellenőriz.

## Candidate

Minden derived package:

```text
PackageFormatVersion
SchemaVersion
DataVersion
GeneratorVersion
SourceFingerprint
DependencyFingerprints
```

nem feltétlen mind külön mező, de a semantics legyen meg.

---

# 6. P-DATA-005 – Package dependency explicit

AETERNA loader már:
- card database → registry dependency;
- minimum schema/data version;
- registry manifest/meta reference

ellenőrzést végez.

Distribution submodule/repository composition ezt külső evidence-ként is támogatja.

## Következtetés

Package dependency ne implicit folder presence legyen.

---

# 7. P-DATA-006 – Generation és verification külön

LorcanaJSON erős evidence.

AETERNA current Python validation + loader validation már részben ezt teszi.

Candidate publish pipeline:

```text
normalize
→ generate
→ schema validate
→ cross-table validate
→ semantic/rules validate
→ support coverage validate
→ review diagnostics
→ publish
```

---

# 8. P-DATA-007 – Human override/correction registry

LorcanaJSON data-driven correction layer.

AETERNA-ban különösen hasznos lehet migration/import esetén.

Candidate:

```text
OverrideEntry
- target_id
- field/path
- expected_old_value
- replacement
- reason
- authority/source
- scope/version
```

A correction nem új gameplay rule.

---

# 9. P-DATA-008 – Localization nem definition identity

AETERNA candidate:

```text
CardDefinitionId
→ LocalizedText[language]
```

Rules-releváns strukturált fields language-invariant.

Localization package külön release cadence-et is kaphat később.

---

# 10. P-DATA-009 – Format/legality külön domain

Distribution forbidden/limited list, Lorcana allowed-format handling és TCG content projectek közös tanulsága:

```text
Card exists
!=
Card legal in current format
```

AETERNA:
- base/expansion availability;
- booster activation;
- future format legality

külön policy/data domain legyen.

---

# 11. P-DATA-010 – Installed/published/active külön lifecycle

Candidate:

```text
AUTHORED
VALIDATED
PUBLISHED
INSTALLED
ENABLED_FOR_FORMAT
LOADED_FOR_MATCH
```

Nem minden projekthez kell mind a hat state; a fogalmi különválasztás fontos.

---

# 12. P-DATA-011 – Consumer output derived

Egy canonical sourceból több artifact:

```text
engine package
Godot catalog
website export
AI/balance dataset
localization bundle
release delta
```

Mindegyik derived.

---

# 13. P-DATA-012 – Delta/cache csak optimization

Babel delta repo és Lorcana OCR/incremental cache:

```text
source of truth
→ full rebuild possible
```

Delta/cache törölhető és újragenerálható.

Ne legyen olyan adat, amely csak delta chainben létezik.

---

# 14. P-DATA-013 – Ability support metadata külön engine capabilitytől

A current AETERNA sample `engine_support.json` egy package-support snapshot.

A production C# ability/effect foundation ettől független.

Candidate később két külön report:

```text
EngineCapabilityManifest
ContentCoverageReport
```

Példa:
- engine supports effect type X;
- package cards közül 812/814 migrált X-compatible schema-ra.

A kettő nem ugyanaz.

---

# 15. P-DATA-014 – Publish gate blocking

Runtime package csak akkor frissíthet production consumption copyt, ha:
- schema;
- dependency;
- referential integrity;
- sentinel;
- support policy;
- diagnostics

PASS.

A jelenlegi AETERNA spec ezt már helyesen irányozza elő.

---

# 16. P-DATA-015 – Asset/provenance külön manifest

Data/schema validation nem bizonyítja:
- asset license;
- attribution;
- redistribution rights.

Release előtt asset provenance matrix külön gate.

---

# 17. Anti-patternök

| ID | Név |
|---|---|
| `A-DATA-001` | runtime package kézi authority edit |
| `A-DATA-002` | row index mint semantic ID |
| `A-DATA-003` | language-dependent card identity |
| `A-DATA-004` | card definition = ability implementation |
| `A-DATA-005` | installed package = mechanic active |
| `A-DATA-006` | schema mismatch silent reuse |
| `A-DATA-007` | correction special case szétszórva generator code-ban |
| `A-DATA-008` | generator saját magát egyetlen validatorral igazolja |
| `A-DATA-009` | package dependency implicit pathból |
| `A-DATA-010` | cache/delta canonical source lesz |
| `A-DATA-011` | support metadata = production engine capability |
| `A-DATA-012` | format legality card definitionbe égetve |
| `A-DATA-013` | asset license nincs release provenanceben |
| `A-DATA-014` | consumer output visszaír authoring source-ba |

---

# 18. Verdict

A D1 data/content architecture fő iránya **már nagyrészt jól létezik AETERNA-ban**.

A blueprint feladata nem új data stack kitalálása, hanem:
- identity/lifecycle formalizálás;
- localization/format domain szétválasztás;
- override/migration policy;
- engine capability vs content coverage különválasztás;
- release fingerprint/provenance;
- derived consumer output szabály.
