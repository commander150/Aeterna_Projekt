# AETERNA – ProjectIgnis/BabelCDB ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott card-data / identity / delta-distribution source audit
- **Javasolt repository-útvonal:** `learning/analyses/projectignis__babelcdb.md`
- **Repository:** `ProjectIgnis/BabelCDB`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `4034a8fd4de97bd776d05be7e5df01d97f1fa864`
- **Fő technológia:** SQLite CDB + Python/Shell/SQL tooling
- **Licenc:** a vizsgált repository gyökerében nem találtunk külön LICENSE fájlt; kód/adat közvetlen átvétele ezért külön jogi/provenance ellenőrzés nélkül nem javasolt
- **Elsődleges AETERNA-érték:** stabil card ID/passcode policy, data/text table szétválasztás, pre-release/official lifecycle, delta adatfrissítés, content repository és script repository összekötése
- **Vizsgálati korlát:** a teljes CDB tartalom, minden workflow és a DeltaBagooska fogyasztói oldal nem került mély auditba
- **Nem AETERNA-szabályforrás.**

---

# 1. Projekt szerepe

A BabelCDB nem rules engine és nem kártyaszkript-gyűjtemény.

A Project Ignis ökoszisztémában a kártya-adatbázis réteg:

```text
CardScripts
    ability/rules script

BabelCDB
    card metadata + localized text / CDB

Distribution / update repository
    client delivery
```

A repository README-je külön összeköti az új adatbázis-bejegyzést a kapcsolódó CardScripts contribution folyamattal.

## AETERNA tanulság

```text
Card Definition Data
!=
Ability Implementation
!=
Distribution Package
```

A három réteg kapcsolódik, de nem ugyanaz az authority vagy artifact.

---

# 2. Stabil identity és lifecycle

A CDB schema `datas.id` és `texts.id` primary keyt használ.

A README külön passcode policyt rögzít:

- prerelease ID tartományok;
- official releasekor official passcode-ra váltás;
- unofficial tartományok;
- alternate artwork alias policy.

## Erős tanulság

Az ID nem egyszerű sorindex.

Az identity policynek dokumentáltnak kell lennie:

```text
stable content identity
edition/printing identity
pre-release identity
alias/reprint relationship
```

AETERNA-ban a canonical card definition ID és a fizikai printing/art variant identity később külön kezelhető, ha tényleges igény lesz.

---

# 3. Data és text külön táblák

A canonical CDB minimum schema két fő table:

```text
datas
- id
- ot
- alias
- setcode
- type
- atk/def/level/race/attribute/category

texts
- id
- name
- desc
- str1..str16
```

Mindkettő `id` primary keykel.

## AETERNA tanulság

A rules-releváns strukturált adat és a megjelenítési/lokalizált text különválasztása hosszú távon értékes.

AETERNA-ban:

```text
CanonicalCardDefinition
LocalizedCardText
```

fogalmilag külön réteg lehet, még ha a human XLSX-ben szerkesztési okból egy helyen is szerepelnek.

---

# 4. Pre-release és official content lifecycle

A README külön adatállapotot kezel:

- pre-release database;
- release database;
- official database;
- region-limited release;
- unofficial additions.

## AETERNA candidate

Expansion/content lifecycle később ne boolean `active` legyen csak.

Lehetséges state:

```text
DRAFT
PREVIEW
VALIDATED
PUBLISHED
ACTIVE_IN_FORMAT
RETIRED
```

A konkrét AETERNA státuszok külön design decision.

---

# 5. Delta distribution

A GitHub Action:

1. figyeli a master pushokat;
2. új CDB-ket teljesen másol;
3. megváltozott CDB-kből SQLite delta adatbázist generál;
4. törölt fájlokat a destination repositoryból is eltávolít;
5. a source commit SHA-t `VERSION` fájlba írja;
6. az eredeti commit author/message metadata jelentős részét átviszi;
7. külön update repositoryba pushol.

## AETERNA tanulság

```text
canonical source snapshot
→ derived distribution delta
```

A delta nem új authority.

A release package-ben hasznos lehet:

```text
BasePackageFingerprint
TargetPackageFingerprint
DeltaPackage
```

De a teljes package bármikor újraépíthető kell legyen canonical forrásból.

---

# 6. Content–script consistency

Az új unofficial database contribution a README szerint a CardScripts contributionhöz kötött.

Ez az ökoszisztéma szinten azt próbálja elkerülni, hogy:

- adat van script nélkül;
- script van megfelelő adat nélkül.

## AETERNA candidate

Publish gate:

```text
card definition
+ referenced ability/module IDs
+ registry definitions
+ localization requirements
+ format activation
→ consistency validation
```

Egy missing ability implementation ne csak runtimeban derüljön ki.

---

# 7. Amit érdemes átvenni elvi mintaként

1. stabil documented content ID policy;
2. structured data és text separation;
3. pre-release/published lifecycle;
4. content data és ability code külön repository/artifact szerep;
5. cross-layer consistency gate;
6. derived delta distribution;
7. source commit/fingerprint megőrzése distributionben.

---

# 8. Amit nem szabad közvetlenül átvenni

1. Yu-Gi-Oh passcode scheme;
2. fixed `str1..str16` text schema;
3. SQLite CDB mint kötelező AETERNA runtime format;
4. region/OT bit semantics;
5. repo-adat licenc/provenance tisztázás nélkül;
6. delta repository mint canonical source.

---

# 9. AETERNA-következtetés

A current AETERNA:

```text
human work source
→ canonical CARDDATABASE / REGISTRY
→ runtime package
```

irány jó.

A BabelCDB legfontosabb plusz tanulsága:

- content identity lifecycle;
- script/data consistency;
- derived delta release;
- published update provenance.

---

# 10. Döntés

- **Data identity érték:** P0
- **Distribution delta érték:** P1
- **Localization/data separation:** P1
- **Ability/data consistency:** P0
- **Közvetlen átvétel:** nem
- **Clean-room architecture inspiráció:** igen.
