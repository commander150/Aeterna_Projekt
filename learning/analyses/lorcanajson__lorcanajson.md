# AETERNA – LorcanaJSON/LorcanaJSON ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott ingestion / correction / verification / output-generation source audit
- **Javasolt repository-útvonal:** `learning/analyses/lorcanajson__lorcanajson.md`
- **Repository:** `LorcanaJSON/LorcanaJSON`
- **Vizsgált branch:** `main`
- **Vizsgált commit:** `4114161ad1048c4d281bf7f0b05e1760691588a6`
- **Fő technológia:** Python + OCR + JSON output generation
- **Licenc:** MIT a generátor repositoryra; a feldolgozott játékadat/asset provenance külön kérdés
- **Elsődleges AETERNA-érték:** external input ingestion, generated output schema version, human correction layer, partial rebuild guard, verification, localization cross-check, több derived output
- **Vizsgálati korlát:** teljes OCR pipeline, minden output schema és a publikált lorcanajson.org artifact nem került teljes mezőszintű auditba
- **Nem AETERNA-szabályforrás.**

---

# 1. Projekt szerepe

A repository nem a publikált adatfájlokat tárolja, hanem a **generálásukhoz szükséges kódot és correction/metadata inputokat**.

Pipeline:

```text
official app/API data
+ card images
+ external link/source data
+ OCR
+ parser
+ correction data
+ structured metadata
→ generated JSON outputs
→ verifier/manual review
```

Ez nagyon közel áll az AETERNA:

```text
human authoring source
→ normalize/validate
→ canonical derived data
→ runtime/public outputs
```

szemléletéhez.

---

# 2. Input nem automatikusan canonical truth

A verifier külön input override réteget tart, mert maga az official input is tartalmazhat hibát vagy olyan eltérést, amely false positive verificationt okoz.

## AETERNA tanulság

A source authority és az ingest adatfájl nem mindig ugyanaz.

A human/rules authority magasabb szintű lehet, mint egy külső vagy generált export.

Ez megerősíti az AETERNA authority sorrendjét.

---

# 3. Format version first-class

A generator:

```text
FORMAT_VERSION = 2.3.5
```

értéket ír metadata-ba.

Részleges rebuild esetén a korábbi `allCards.json` csak akkor használható újra, ha a korábbi `metadata.formatVersion` pontosan egyezik az aktuálissal.

Mismatch:

```text
full parse required
```

## Erős AETERNA-minta

Schema/format version change esetén ne silently reuse-old-data történjen.

```text
SchemaVersion mismatch
→ migration OR full rebuild OR reject
```

---

# 4. Incremental rebuild, de canonical validationdel

A generator képes csak megadott card ID-ket újraparsolni.

A nem érintett kártyák a korábbi outputból újrahasználhatók, ha:
- output létezik;
- format version kompatibilis.

A módosított kártyákhoz külön `parsedCards.json` készül manuális reviewhoz.

## AETERNA candidate

Nagy card database esetén:

```text
changed source rows
→ targeted canonical rebuild
→ changed-record review artifact
→ full publish validation
```

hatékony lehet.

De a publish gate végén mindig teljes cross-table consistency ellenőrzés szükséges.

---

# 5. Human correction layer

A generator kétféle korrekciós adatot használ:

```text
outputDataCorrections.json
outputDataCorrections_<language>.json
```

A global correction előbb, a language-specific utána kerül alkalmazásra.

A correction:
- regex replace;
- field add/remove;
- list entry add/remove;
- ability/effect reclassification;
- ordering/splitting/merge special case

jellegű lehet.

## AETERNA tanulság

A human exception ne legyen szétszórt Python `if cardId == ...` kódban, ha adatként kezelhető.

Candidate:

```text
CanonicalOverrideRegistry
- record_id
- field/path
- expected old value/pattern
- new value
- reason
- source/reference
- scope/version
```

Az expected-old guard különösen fontos, hogy stale override ne fusson csendben.

---

# 6. Verification külön pipeline

A `verify` action:
- input vs parsed output;
- text normalization;
- rules text;
- flavor text;
- subtype;
- identifier;
- numeric/basic fields;
- whitespace/symbol invariants;
- external link completeness;
- historical data completeness;
- nem angol output vs English structural consistency

ellenőrzéseket futtat.

## AETERNA tanulság

```text
generation
!=
verification
```

A canonical export tool ne önmagát igazolja kizárólag ugyanazzal a transformation logikával.

Külön invariant/audit pass magas értékű.

---

# 7. Manual verification explicit része a pipeline-nak

A README kimondja, hogy OCR miatt manuális review továbbra is szükséges.

Külön OutputFileViewer segíti:
- image;
- parsed text;
- structured output

összevetését.

## AETERNA megfelelő

A human-authored rules/card text és gépi normalized fields esetén:
- diff/review artifact;
- changed records report;
- publish approval

különösen nagy migrationnél hasznos.

---

# 8. Stable culture-invariant card ID

Inputból:

```text
culture_invariant_id
```

lesz a generated card `id`.

A nyelv az identityt nem változtatja meg.

## AETERNA tanulság

```text
CardDefinitionId
```

ne legyen language-dependent.

Localization ugyanahhoz az identityhoz csatlakozik.

---

# 9. Language-specific generation

Output folder:

```text
output/<language>/
```

Metadata tartalmaz:
- formatVersion;
- generatedOn;
- language.

Set név csak akkor kerül be, ha az adott language számára rendelkezésre áll.

A non-English verifier English outputhoz is hasonlít strukturális mezőket.

## AETERNA candidate

Localization consistency audit:
- ugyanazok a card IDs;
- rules-releváns structural fields azonosak;
- language csak permitted text/display fieldsre hat.

---

# 10. Generated output több consumer-célra

A generator nem csak egyetlen allCards outputot készít.

Támogat:
- metadata;
- allCards;
- partial parsedCards review;
- deck output;
- további specialized derived files.

## AETERNA tanulság

Egy canonical database-ből több derived consumer package készülhet:

```text
canonical data
├── engine package
├── Godot/public catalog
├── website/API export
├── localization bundle
└── balance/analytics dataset
```

Ezek nem válhatnak vissza authoring authorityvé.

---

# 11. OCR cache és build cache invalidation

A cache csak gyorsítás.

Ha OCR code változik, a README külön rebuild opciót ad.

## Általános tanulság

Derived cache identity függjön:
- source fingerprinttől;
- generator/tool versiontől;
- schema versiontől.

Stale cache ne legyen canonical input.

---

# 12. Amit érdemes átvenni elvi mintaként

1. generator repo vs generated public data különválasztás;
2. explicit format/schema version;
3. partial rebuild compatibility guard;
4. human correction registry;
5. correction expected-value guard;
6. generation utáni külön verifier;
7. manual changed-record review artifact;
8. culture-invariant ID;
9. language-specific output, shared structural identity;
10. multiple derived consumer outputs;
11. cache invalidation version/fingerprint alapján.

---

# 13. Amit nem kell átvenni

1. OCR mint AETERNA primary authoring pipeline;
2. Lorcana field schema;
3. Python-specific correction syntax;
4. English mint kötelező canonical language;
5. third-party API mint AETERNA rules authority.

---

# 14. Döntés

- **Pipeline architecture:** P0
- **Schema/versioning:** P0
- **Correction/override:** P0
- **Verification:** P0
- **Localization:** P0
- **Direct dependency:** nem szükséges
- **Clean-room architecture inspiráció:** igen.
