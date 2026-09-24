---
artifact_id: AET-DOC-DOCUMENT-GOVERNANCE
kind: document
type: governance
version: "0.1"
lifecycle: active
integration: current
authority: document-governance
generated: false
depends_on: []
supersedes: []
---

# AETERNA dokumentum- és artifact-governance

## 1. Cél és hatáskör

Ez a dokumentum az AETERNA dokumentum- és artifact-életciklus governance authorityje. A logikai artifactok identitását, metadata-kezelését, tulajdonlását, életciklusát, migrációját és ellenőrzését szabályozza.

Saját hatáskörén kívül nem írja felül:

- a hivatalos játékszabályokat;
- a technical architecture vagy technical contract authorityt;
- a canonical adat authorityt;
- a roadmap- és product-prioritásokat.

## 2. Canonical owner

Egy információegységnek egy canonical gazdája legyen. Ugyanazt a current tartalmat történeti okból nem tartjuk fenn párhuzamos példányokban. A dokumentum történetét, korábbi állapotait és változásait a Git history őrzi.

## 3. Artifact identity

Az artifact ID stabil logikai identitás:

```text
AET-{KIND}-{STABLE-NAME}
```

Elfogadott prefixek:

```text
AET-DOC-
AET-DATA-
AET-SOURCE-
AET-GEN-
AET-PKG-
AET-BP-
```

Az artifact ID:

- nem path;
- nem fájlnév;
- nem kiterjesztés;
- nem lifecycle;
- nem dokumentumverzió.

Az identity túléli a fájl átnevezését és mozgatását.

## 4. Native metadata és generált nézetek

Az artifact saját, natív metadata-rétege az authority:

- Markdown esetén YAML front matter;
- XLSX esetén saját META vagy manifest réteg;
- package esetén manifest.

A későbbi központi artifact registry és index ezekből generálódik. Ugyanazt a metadata-információt nem tartjuk fenn kézzel két helyen.

A jövőbeli `artifacts_registry.json` és `DOCUMENT_INDEX.md` generált nézet, nem önálló authority a forrásai fölött.

## 5. Lifecycle, integration és authority

A `lifecycle`, az `integration` és az `authority` külön dimenziók.

A `lifecycle` értékei:

```text
draft
active
deprecated
historical
```

Az `integration` értékei:

```text
current
pending_integration
recovery_candidate
```

A lifecycle az artifact életciklusát, az integration a repositoryba és a canonical rendszerbe való beillesztettségét jelzi. Az authority ettől a két fogalomtól különállóan adja meg, hogy az artifact milyen kérdésben irányadó.

## 6. Stable filename policy

Az új és current governance irány:

```text
stabil current fájlnév
+ belső dokumentumverzió
+ Git history
```

Példák:

```text
PROJECT_PLAN.md
DEVELOPMENT_ROADMAP.md
DOCUMENT_GOVERNANCE.md
```

A korábbi verziózott fájlnevek nem voltak hibás döntések. A régebbi ChatGPT- és file-workflow mellett nehéz volt megkülönböztetni a stale és current példányokat, a fájlnévben látható verzió pedig egyértelmű azonosítást adott. A korábbi munkafolyamat ezt igényelte.

A stable-filename policy későbbi governance döntésként csak a fájlnév-kezelést váltja fel; a korábbi döntés indoklása megmarad.

### 6.1 Grandfathered transition

A még nem migrált, verziózott current fájlok nem automatikus hibák. Az átmenet:

```text
legacy versioned filename
→ explicit migration target
→ audited rename
→ stable filename enforcement
```

A checker v0.x nem tekintheti minden legacy verziózott fájl létezését automatikusan `ERROR` állapotnak.

### 6.2 Legacy status block transition

Az új YAML metadata és a régi `VERZIÓ / DOKUMENTUMSTÁTUSZ` blokk átmenetileg együtt élhet. A migráció első fázisának célja a metadata hozzáadása és a két réteg konzisztenciájának ellenőrzése, nem a legacy header azonnali eltávolítása.

## 7. Version policy

A dokumentum semantic version kezelése:

- typo-, link- vagy style-jellegű változás lehet Git-only;
- minor verziót indokolhat jelentős tartalmi vagy operatív bővítés;
- major verziót indokol az authority, contract vagy alapértelmezés lényegi változása.

Normál dokumentumfrissítés nem használ `supersedes` kapcsolatot: ugyanaz az artifact ID marad. A `supersedes` más logikai artifact leváltására szolgál.

Nem kényszerítünk egyetlen univerzális `version` mezőt minden artifacttípusra. Külön dimenzió lehet:

- document version;
- schema version;
- data version;
- package version;
- ruleset version;
- generator vagy contract version.

Generated dokumentum nem talál ki független semantic content versiont.

## 8. Generated artifactok

A generated artifact:

- nem kézzel szerkesztendő;
- forrása visszakövethető;
- determinisztikusan újragenerálható;
- saját forrásai fölött nem authority.

## 9. Dependencies

A `depends_on` csak erős semantic dependencyt jelöl. Nem minden hivatkozás vagy link dependency.

Ha egy source megváltozik:

- generated dependent esetén az eredmény `STALE`;
- human-maintained dependent esetén az eredmény `REVIEW_RECOMMENDED`.

Human-maintained tartalom automatikus átírása nem történik.

## 10. Recovery és migration

A recovery artifact nem válik automatikusan current authorityvé. A recovery alapelve:

```text
old current
+ recovery candidate
+ newer actual source truth
+ accepted decisions
→ new current canonical artifact
```

Ez nem vak verzióemelés.

`REBUILD`, `SPLIT`, `MERGE` vagy `HISTORICAL` művelethez content disposition szükséges. Minden érdemi régi tartalom:

- új ownerhez kerül;
- generated ownerhez kerül;
- vagy explicit obsolete/historical döntést kap.

### 10.1 Logical cutover before physical movement

A tömeges move vagy rename előtt logikailag rögzíteni kell:

- az artifact ID-t;
- az ownert;
- az authorityt;
- a lifecycle-t;
- a metadatát;
- a dependencyket.

### 10.2 File-level preservation

Tracked vagy más durable project artifact teljes fájlként nem semmisíthető meg pusztán azért, mert current szerepe megszűnik. A retirement kötelező útja:

```text
active owner
→ historical disposition
→ Archive vagy más durable preservation owner
```

Superseded, obsolete, historical vagy current használatból kivont fájlt teljes eredeti példányként meg kell őrizni. Ha nincs más durable célhelye, append-only intake-ként az Archive-ba kerül. A Git history önmagában nem archive és nem megfelelő file-preservation mechanism.

Az Archive meglévő tartalma immutable; új történeti artifact hozzáadható, de meglévő archív fájl nem szerkeszthető, mozgatható, nevezhető át, törölhető vagy írható felül. A szabály a file-level megőrzésre vonatkozik: current fájlon belül sor, fejezet vagy mező szerkeszthető vagy eltávolítható a rendes authority és review szerint.

Durable fájl végleges, preservation nélküli törlése csak az adott fájlra vonatkozó explicit emberi kivétellel engedélyezett.

## 11. Scope profiles

### 11.1 ACTIVE

Az ACTIVE scope-ban teljes governance és validation érvényes.

### 11.2 LEARNING

A LEARNING scope állapota `DEFERRED_REVIEW_REQUIRED`. A Learning nem maradhat korlátlan ideig audit nélkül; külön, későbbi teljes Learning Documentation Audit szükséges. A pilot alatt nem kényszerítünk rá új metadata-contractot.

### 11.3 ARCHIVE

Az ARCHIVE preservation layer. Meglévő archived fájl:

- nem szerkeszthető;
- nem formázható át;
- nem nevezhető át;
- nem mozgatható;
- nem javítható automatikus link-rewrite-tal.

Új artifact később explicit archive operationnel kerülhet ide. Miután Archive-ba került, immutable.

## 12. AI- és Codex-szerkesztés

AI vagy Codex:

- explicit, bounded munkacsomagban dolgozik;
- authority source-t nem ír át automatikusan;
- az elfogadott munkafolyamatban nem commitol és nem pushol automatikusan;
- local diff, teszt és human/ChatGPT review után adható át;
- source rewrite vagy fix műveletet csak külön engedéllyel végez.

## 13. Git szerepe

A Git biztosítja a historyt, diffet, provenance-t, rollbacket és audit evidence-et. Nem szükséges manual version-history szöveget minden dokumentumban megismételni, ha a történetet a Git már megőrzi.

## 14. Artifact és fizikai fájl

Egy logikai artifact vagy source nem feltétlenül egyetlen fizikai fájl. Különösen az adatforrások állhatnak később source bundle-ből. A részletes Source Bundle Contract külön, későbbi specifikáció.

## 15. Enforcement principle

A governance checker kezdetben fokozatos enforcementet használ. Nem idézhet elő repository-wide false-positive vihart csak azért, mert a régi repository még nem migrált teljesen. A migráció explicit batch-ekben történik.
