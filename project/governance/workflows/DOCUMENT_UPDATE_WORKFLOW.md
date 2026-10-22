---
artifact_id: AET-DOC-DOCUMENT-UPDATE-WORKFLOW
kind: document
type: workflow
version: "2.1"
lifecycle: active
integration: current
authority: operational-workflow
generated: false
depends_on:
  - AET-DOC-DOCUMENT-GOVERNANCE
  - AET-DOC-GITHUB-WORKFLOW
supersedes: []
---

# AETERNA governed dokumentumműveleti workflow

## 1. Cél, hatáskör és authority

Ez a dokumentum az AETERNA governed lokális dokumentumműveleteinek operatív
contractja. A workflow feladata, hogy a választott művelet explicit identitás-
és baseline contractja szerint ellenőrizze a kiinduló állapotot, egy előre
rögzített tervhez kösse a műveletet, tranzakciósan alkalmazza a jóváhagyott
jelöltet, majd ellenőrizhető review-bizonyítékot készítsen.

A dokumentum-governance határozza meg az artifact-identitás, authority,
lifecycle, Archive és megőrzés szabályait. A GitHub workflow határozza meg a
lokális eredmény review-, commit-, push- és remote handoffját. A jelen workflow
ezeket nem írja felül, hanem a jelen dokumentumban operation-scope szerint
rögzített governed dokumentumműveletek részletes helyi rendjét adja meg.

Az `integration: current` azt jelenti, hogy a workflow implementált és az aktív
operatív dokumentumfrissítési út része. A Markdown MVP implementációja a
`tools/aeterna_document_workflow` alatt létezik, és a kontrollált valódi
repository-acceptance teszten megfelelt. A jelen dokumentum marad az operatív
contract; az implementációs bizonyítékot a repository kódja, tesztjei,
review-evidence anyagai és Git-története adják.

## Capability-státusz

```text
UPDATE_CONTRACT_STATUS = CURRENT
UPDATE_IMPLEMENTATION_STATUS = IMPLEMENTED_AND_ACCEPTED
UPDATE_PLAN_SCHEMA = aeterna-document-update-plan/0.1
UPDATE_REVIEW_SCHEMA = aeterna-document-update-review/0.1

CREATE_CONTRACT_STATUS = CURRENT
CREATE_IMPLEMENTATION_STATUS = IMPLEMENTED_AND_ACCEPTED
CREATE_ACCEPTANCE_STATUS = FIRST_REAL_GOVERNED_CREATE_COMPLETE_AND_REMOTE_VERIFIED
CREATE_MANIFEST_SCHEMA = aeterna-document-create-manifest/0.1
CREATE_PLAN_SCHEMA = aeterna-document-create-plan/0.1
CREATE_REVIEW_SCHEMA = aeterna-document-create-review/0.1

DOCUMENT_MANAGER_CREATE_CANDIDATE_AND_PLAN = IMPLEMENTED
DOCUMENT_MANAGER_CREATE_APPLY = IMPLEMENTED_AND_REMOTE_VERIFIED
DOCUMENT_MANAGER_CREATE_APPLY_ACCEPTANCE = ISOLATED_TESTCLONE_GUI_PASS_USER_REPORTED
DOCUMENT_MANAGER_UPDATE_APPLY = IMPLEMENTED_AND_REMOTE_VERIFIED
DOCUMENT_MANAGER_GOVERNANCE_APPLY = IMPLEMENTED_AND_REMOTE_VERIFIED

UPDATE_0_1_BACKWARD_COMPATIBLE = YES
```

Az `integration: current` az implementált és elfogadott UPDATE és production
CREATE backend-műveletre vonatkozik. A PILOT-8E első valódi governed CREATE
acceptance-e remote verified. A Document Manager grafikus CREATE candidate-et,
read-only `plan-create` tervet és külön ember által jóváhagyott CREATE Apply-t
biztosít. Az izolált tesztclone-ban végzett grafikus CREATE Apply és production
review-ellenőrzés sikerét a felhasználó jelentette; ez külön bizonyíték a
PILOT-8E backend-acceptance-től, és nem hivatalos repositoryban végzett
grafikus CREATE Apply.

## Normatív operation-scope boundary

A 2–27. szakasz az elfogadott UPDATE 0.1 contractot tartja fenn és kizárólag az
UPDATE műveletet szabályozza. A 28–47. szakasz az additív CREATE 0.1 contractot
határozza meg.

Ha egy szabály nincs kifejezetten shared/common szabályként megjelölve:

- az existing artifact resolution, current path, baseline target SHA-256,
  UPDATE change class és `git-only`/`minor`/`major` version intent kizárólag az
  UPDATE művelet preconditionje;
- a declared new identity, declared target path, target absence, explicit
  initial version és baseline-plus-one overlay kizárólag a CREATE művelet
  preconditionje.

A CREATE nem örökli az UPDATE-only preconditionöket pusztán azért, mert az
UPDATE contract korábban szerepel ugyanebben a dokumentumban. Az UPDATE nem
örökli a CREATE-only preconditionöket. Ha a két operation contract közös safety
principle-t fejez ki, mindkét művelet a saját, explicit operation-specific
preconditionje szerint teljesíti azt. A szakaszok sorrendje önmagában nem hoz
létre implicit precedenciát.

```text
UPDATE_ONLY_PRECONDITIONS_SCOPED = YES
CREATE_ONLY_PRECONDITIONS_SCOPED = YES
BASELINE_TARGET_SHA_REQUIRED_FOR_CREATE = NO
TARGET_ABSENCE_REQUIRED_FOR_UPDATE = NO
UPDATE_VERSION_INTENT_APPLIES_TO_CREATE_INITIAL_VERSION = NO
CREATE_INITIAL_VERSION_RULE_APPLIES_TO_UPDATE = NO
RESOLVE_EXISTING_ARTIFACT_REQUIRED_FOR_CREATE = NO
```

## 2. MVP-határ

Az első implementáció kizárólag:

```text
meglévő
+ ACTIVE scope-ban lévő
+ managed
+ Markdown
+ document artifact
+ ugyanazon stabil pathon végzett frissítés
```

Az MVP-n kívül marad:

- az UPDATE műveleten belüli új artifact létrehozása; a külön CREATE művelet a 28–47. szakasz szerint implementált és elfogadott;
- retirement vagy Archive-intake;
- move és rename;
- authority-váltás;
- batch editing;
- XLSX, DOCX, source bundle és package manifest szerkesztés;
- exact patch vagy unified diff bemenet;
- external-editor handoff a production UPDATE backend önálló műveleteként (a Document Manager VS Code candidate-szerkesztése külön GUI-réteg);
- Git staging, commit és push.

## 3. Fogalmak

**Native metadata:** az artifact saját YAML front mattere; a managed Markdown
identitásának és governance-mezőinek authorityje.

**Fresh scan:** a repository aktuális natív metadatájából közvetlenül végzett
teljes artifact-discovery és validáció.

**Candidate:** a felhasználó vagy segédeszköz által előkészített teljes,
ideiglenes Markdown-példány.

**Operation manifest:** strukturált JSON, amely a jelöltet az artifacthoz, a
baseline-hoz, a deklarált változási osztályhoz és a version intenthez köti.

**Plan:** determinisztikus, no-write eredmény, amely minden preconditiont,
tervezett byte-változást, impactot és elvárt changed pathot rögzít.

**Apply:** az egyetlen MVP-művelet, amely egy változatlan, materializált plan
alapján repository-tartalmat írhat.

**Overlay:** a teljes tervezett végállapot repositoryba írás előtti,
ideiglenes reprezentációja.

**Semantic identity:** a plan tartalma, amely az azonos inputból képzett két
terv összehasonlíthatóságát adja. Nem tartozik hozzá az instance timestamp vagy
egy véletlen operation ID.

## 4. Normatív műveleti modell

```text
RESOLVE
→ PLAN
→ APPLY
→ REVIEW
→ HUMAN GIT HANDOFF
```

Teljes folyamat:

```text
artifact_id
→ fresh native-metadata scan
→ pontosan egy current artifact feloldása
→ baseline és precondition validáció
→ immutable plan létrehozása
→ bounded candidate + manifest
→ candidate overlay validáció
→ explicit apply
→ tranzakciós írás
→ post-write validáció
→ review evidence
→ human/ChatGPT diff-review
→ emberi staging/commit/push döntés
```

Nincs közvetlen update parancs, amely megkerüli a materializált plant.

## 5. Artifact resolution

A resolver authorityje a natív metadatából végzett fresh repository scan.
Feloldáskor:

- ismeretlen artifact ID: `ERROR`;
- duplicate artifact ID: `BLOCKING`;
- bármely scan `ERROR` vagy `BLOCKING` diagnostic: `BLOCKING`;
- nem pontosan egy feloldott rekord: `BLOCKING`;
- repositoryn kívülre oldódó path: `BLOCKING`;
- Archive, Learning vagy generated path MVP-mutation céljaként: `BLOCKING`.

Az `artifacts_registry.json` összevethető, validálható és újragenerálható, de
nem lehet a feloldás egyetlen authorityje.

## 6. Plan- és apply-time preconditionök

A plan és az apply kötelezően ellenőrzi:

- az elvárt, canonical repository rootot;
- branchet és pontos `HEAD`-et;
- tiszta worktree-t;
- üres staginget;
- fresh artifact-resolutiont;
- az elvárt artifact ID-t és current pathot;
- a baseline fájl SHA-256 hashét;
- a metadata determinisztikus fingerprintjét;
- UTF-8 dekódolhatóságot;
- BOM-állapotot;
- newline-konvenciót;
- ACTIVE scope-ot és MVP artifacttípust.

Az apply minden mutation-releváns preconditiont közvetlenül az első írás előtt
újrafuttat. Bármely eltérés érvényteleníti a plant. Nincs fuzzy merge, automatikus
rebase vagy újabb emberi változást felülíró írás.

## 7. Candidate input contract

Az elfogadott MVP-input:

```text
strukturált JSON operation manifest
+
teljes ideiglenes candidate Markdown copy
```

A manifest legalább rögzíti:

- artifact ID;
- expected HEAD;
- expected current path;
- baseline file SHA-256;
- metadata fingerprint;
- deklarált change class;
- explicit version intent;
- candidate path és SHA-256.

A candidate nem authority a manifest vagy a repository-governance fölött. A
candidate-ben megjelenő, nem deklarált metadata-eltérés blokkoló hiba.

## 8. Változási osztályok

### 8.1 `body-only`

Csak a front matter lezárása utáni törzs változhat. Minden metadata-mező és a
path változatlan.

### 8.2 `metadata-only`

Csak explicit old→new metadata-delta változhat. A dokumentumtörzs bytejai
változatlanok.

### 8.3 `metadata+body`

Az explicit metadata-delta és a törzs is változhat. Mindkét változás külön
review-részben jelenik meg.

### 8.4 `reference-only`

Csak deklarált hivatkozási sorok változhatnak; a plan felsorolja a régi és új
referenciákat. Nem jogosít repository-wide automatikus átírásra.

### 8.5 `semantic-governance-change`

Felismert magas kockázatú osztály authority-, contract- vagy alapértelmezésbeli
jelentés változására. Az MVP ezt nem hagyhatja jóvá hallgatólagosan.
A `semantic-governance-change` besorolást az UPDATE manifest explicit módon
deklarálja. A production terv ezt rögzíti, és a javasolt verziószándékot
a deklarált osztály alapján számítja. A normál `apply` blokkolja a magas
kockázatú governance UPDATE végrehajtását. A külön `apply-governance` vagy
`apply-governance-gui` belépési pont az immutable tervhez kötött, interaktív,
egyszer használható jóváhagyás és a production ellenőrzések után alkalmazhatja
a változtatást; a review és a rollback védelme megmarad.

## 9. Védett metadata és explicit delták

Normál MVP-update során változatlan:

```text
artifact_id
path
authority
kind
type
generated
supersedes
```

Bármely eltérés `BLOCKING / REJECT`.

A `depends_on` kizárólag explicit old→new delta és teljes graph-validáció
mellett változhat. A `version`, `lifecycle` és `integration` csak explicit
old→new deklarációval módosulhat. A full candidate copy egyetlen mezőt sem
változtathat incidentálisan.

Authority-váltás az MVP-ben tiltott. Egy későbbi, külön operation class csak
explicit régi és új értékkel, indoklással, pontos HEAD/hash preconditionnel,
explicit acknowledgementtel és emberi review-val tervezhető.

## 10. Version intent

Kötelező intentértékek:

```text
git-only
minor
major
```

A tool ajánlást adhat, a felhasználó intentje azonban explicit, és a tool nem
emelhet automatikusan semantic document versiont. Irányadó ajánlás:

- typo, link, style vagy reference-only változás: gyakran `git-only`;
- jelentős operatív vagy tartalmi bővítés: gyakran `minor`;
- authority, contract vagy alapértelmezés lényegi változása: gyakran `major`.

Az ajánlás és az intent eltérését a plan és a review kötelezően jelzi; az
eltérés nem oldható fel rejtett automatikus döntéssel.

## 11. Dependency graph és impact

A candidate overlay teljes artifact-gráfján ellenőrizendő:

- duplicate artifact ID;
- hiányzó dependency-target;
- self dependency;
- dependency cycle;
- case- vagy path-collision.

A workflow kiszámítja a forward dependencyket, reverse dependencyket és a
transitive dependent halmazt. Impact-label:

```text
generated dependent → STALE
human-maintained dependent → REVIEW_RECOMMENDED
```

Human-maintained dependent automatikusan nem írható át. Szöveges hivatkozás
önmagában nem válik `depends_on` kapcsolattá.

## 12. Generated view-k

Derived outputok:

```text
project/generated/artifacts_registry.json
project/generated/DOCUMENT_INDEX.md
```

Ezek nem elsődleges edit inputok és nem tarthatók karban manuálisan. A workflow
a fresh candidate artifact-state-ből memóriában rendereli őket, byte-szinten
összeveti a jelenlegi fájlokkal, és csak eltérés esetén írja őket ugyanabban a
tranzakcióban. Body-only update változatlan title, metadata és path mellett nem
írhatja újra őket szükségtelenül.

## 13. Byte-, encoding- és newline-contract

A baseline-fájl byte-konvenciója megőrzendő. Kötelező:

- strict UTF-8;
- BOM jelenlétének rögzítése;
- newline-stílus rögzítése;
- mixed newline input elutasítása;
- lone CR elutasítása;
- candidate newline-drift elutasítása;
- platform-default newline-konverzió kerülése;
- repository-wide normalizálás tiltása normál update részeként.

A PILOT-7A baseline-audit során vizsgált managed Markdown dokumentumok
UTF-8, BOM nélküli és LF-only formátumúak voltak; a `.gitattributes`
`text=auto`, a Markdown EOL nincs külön rögzítve, az `.editorconfig`
nem ad szabályt.

## 14. Archive safety

Normál update blokkolja:

- Archive alatti source-ot vagy targetet;
- meglévő Archive-fájl szerkesztését vagy felülírását;
- Archive-fájl rename-jét, move-ját vagy törlését;
- Archive-on belüli automatikus reference-fixet.

A path-guard canonical, case-insensitive, traversal-, symlink- és reparse-escape
ellenőrzést használ. Retirement nem MVP. Később kizárólag append-only,
nem ütköző Archive-intake engedhető byte-preservation evidence mellett.

## 15. Dry-run és plan

Minden `plan-*` viselkedés `NO-WRITE`; nincs `--dry-run=false` mód. A plan
legalább tartalmazza:

- schema version és operation type;
- artifact ID, branch, HEAD és resolved path;
- baseline hash, metadata fingerprint és byte convention;
- candidate hash;
- change class és version intent;
- metadata delta és body diff summary;
- dependency és generated-output impact;
- validation gate-ek és scope violationök;
- expected changed paths.

Azonos inputból azonos semantic plan keletkezik.

## 16. Apply

Repositoryt kizárólag a production Apply belépési pontok mutálhatnak:
normál UPDATE és CREATE esetén `apply PLAN.json`, magas kockázatú
`semantic-governance-change` UPDATE esetén külön interaktív
`apply-governance PLAN.json` vagy `apply-governance-gui PLAN.json`.
A normál `apply` governance-változásra továbbra is blokkol.

Az UPDATE Apply:

1. betölti és validálja az immutable plant;
2. újra feloldja az artifactot;
3. újrafuttatja a preconditionöket;
4. újrahasheli a baseline-t és a candidate-et;
5. teljes overlayben validálja a candidate-et és a gráfot;
6. memóriában rendereli a generated view-ket;
7. előkészíti a teljes tranzakciót;
8. csak minden pre-write gate PASS után ír;
9. post-write scant, validációt és scope-checket futtat;
10. review evidence-et készít.

## 17. Tranzakció és rollback

Normatív MVP:

```text
same-volume, repositoryhoz kötött tartós `.git` tranzakciós terület
→ minden intended byte előállítása
→ teljes overlay validáció
→ transaction journal
→ touched existing fájlok byte-backupja
→ atomic replacement
→ post-write validáció
```

A production review-evidence jelenleg a repository Git-ignored `TEMP/`
könyvtárába kerül; ez a GITHUB_WORKFLOW 2.0 dokumentált átmeneti technikai
kivétele, nem a tranzakciós/recovery-adatok tárolója.

Bármely írás utáni hiba esetén a workflow:

- visszaállít minden érintett eredeti fájlt;
- csak a tranzakció által létrehozott pathokat távolítja el;
- ellenőrzi az eredeti baseline hasheket;
- megőrzi a failed transaction evidence-et.

A Git rollback önmagában nem elég, és a workflow nem használhat resetet,
restore-t, stash-t vagy cleant.

## 18. Review evidence

Sikeres vagy sikertelen apply géppel olvasható JSON-t és olvasható szöveges
bundle-t készít. Kötelező tartalom:

- schema és operation identity;
- baseline branch, HEAD és status;
- artifact ID és régi/új path;
- régi/új metadata és fingerprint;
- change class és diff summary;
- régi/új hash és byte convention;
- dependency impact;
- generated outputok és hashek;
- validációk, tesztek, parancsok és exit code-ok;
- transaction és rollback eredmény;
- scope, `git diff --check`, final worktree és staging;
- eltérések és final status.

## 19. Git responsibility boundary

A workflow nem hajthatja végre:

```text
git add
git commit
git push
git reset
git restore
git stash
git clean
```

Read-only Git-parancs használható branch, HEAD, status, diff, `diff --check` és
tracked-file evidence céljára. Staging, commit és push emberi döntés marad a
GitHub workflow szerint.

## 20. AI és Codex határa

AI vagy Codex azonosíthat célartifactot, előkészíthet candidate-et és manifestet,
meghívhat resolve/plan/apply műveletet, és elemezheti az evidence-et. Nem authority
source, implicit approval layer, automatikus version authority, authority-change
mechanism vagy commit layer. A workflow AI nélkül is teljesen használható.

## 21. Plan JSON contract

Schema version:

```text
aeterna-document-update-plan/0.1
```

Kötelező conceptual mezők:

| Mező | Típus | Tartalom |
|---|---|---|
| `schema_version` | string | pontos schema identity |
| `operation` | string | MVP-ben `update` |
| `artifact_id` | string | stabil célidentitás |
| `repository` | object | canonical root és repository fingerprint |
| `baseline` | object | branch, HEAD, status, staging |
| `resolved_artifact` | object | path, metadata, scope, title |
| `candidate` | object | path, SHA-256, byte convention |
| `change` | object | class, body diff summary, protected-field result |
| `metadata_delta` | array | explicit field/old/new elemek |
| `version` | object | current, recommendation, intent, proposed value, mismatch |
| `impact` | object | graph diagnostics és dependentek |
| `generated` | object | expected derived output byte-változások |
| `preconditions` | array | név, expected, observed, result |
| `expected_changes` | array | repository-relative path és operation |

A semantic identity minden fenti normatív mezőt tartalmaz a candidate tartalmi
hashével együtt. `operation_id`, létrehozási timestamp és display-only elapsed
time instance metadata, ezért determinisztikussági összevetéskor kizárandó. A
PILOT-7B nem hoz létre külön JSON Schema fájlt.

## 22. Review JSON contract

Schema version:

```text
aeterna-document-update-review/0.1
```

Kötelező szekciók:

| Szekció | Kötelező tartalom |
|---|---|
| `schema_version` | pontos schema identity |
| `operation_id` | instance azonosító |
| `operation` | típus, plan semantic hash |
| `baseline` | root, branch, HEAD, initial Git state |
| `artifact` | ID, old/new path és metadata |
| `change` | class, version intent, diff summary |
| `hashes` | baseline, candidate, final és generated SHA-256 |
| `byte_conventions` | encoding, BOM, newline old/new |
| `dependency_impact` | diagnostics és impact labels |
| `generated_outputs` | render/write/unchanged eredmény |
| `validation` | gate-ek, diagnostics és exit code-ok |
| `tests` | parancsok és teljes eredményreferenciák |
| `transaction` | journal, writes és atomic replace eredmény |
| `rollback` | required/performed/verified és hashek |
| `scope` | expected/actual pathok és violationök |
| `git` | diff, diff-check, staging és final status |
| `deviations` | ismert eltérések vagy üres lista |
| `final_status` | PASS/FAIL/BLOCKED |

Timestamp lehet instance metadata, de semantic determinism összevetést nem
ronthat el.

## 23. Exit code-ok

```text
0 = success
1 = validation vagy policy rejection
2 = technical execution error
3 = stale plan vagy precondition mismatch
4 = transaction failure, verified rollbackkal
5 = rollback verification failure
```

Az `0/1/2` jelentése kompatibilis a jelenlegi artifact-tooling konvenciójával.
A speciális workflow-hibák külön `3–5` kategóriát kapnak; nagyobb mátrixot az
MVP nem vezet be.

## 24. MVP CLI-felület

Current production CLI surface:

```text
resolve
impact
inspect-update-baseline
plan-update
inspect-create-baseline
plan-create
apply
apply-governance
apply-governance-gui
verify-review
```

Read-only: `resolve`, `impact`, `inspect-update-baseline`,
`plan-update`, `inspect-create-baseline`, `plan-create`, `verify-review`.
Mutating: `apply`, `apply-governance`, `apply-governance-gui` csak a saját
operation- és jóváhagyási contractjuk szerint. Nincs `resolve-create` vagy
`impact-create`. A `plan-retire`, `plan-move` és `authority-change` továbbra
sem jóváhagyott művelet.

## 25. Adapter boundary

A formatadapter conceptual interface-e:

```text
inspect
fingerprint
validate_candidate
render_change
impact_hooks
```

Az első adapter Markdown. Később külön XLSX-, source-bundle-, package-manifest-
és DOCX migration/preservation adapter készülhet. Az XLSX művelet bináris-safe,
META/manifest-aware és multi-sheet integrityt őrző kell legyen; nem text patch.
A Markdown MVP nem tehet olyan one-file vagy text-only feltételezést a közös
orchestration rétegbe, amely ezeket ellehetetleníti.

## 26. Elfogadott tervezési döntések

A contract tartósan rögzíti a tervezési audit négy elfogadott döntését:

- **D01:** structured JSON manifest + teljes ideiglenes candidate Markdown copy;
- **D02:** tool-ajánlás + explicit felhasználói `git-only/minor/major` intent;
- **D03:** MVP-ben tiszta worktree és üres staging kötelező;
- **D04:** authority-váltás MVP-ben elutasítandó.

E döntésekhez nem szükséges TEMP-evidence mint authority; a jelen normatív
szöveg az operatív forrás.

## 27. Implementációs fázishatár

A PILOT-7B contract, a PILOT-7C read-only foundation, a PILOT-7D safe
Markdown update MVP, a PILOT-7D.1 transaction hardening és a PILOT-7E
controlled real repository acceptance `COMPLETE_AND_REMOTE_VERIFIED`.

A `tools/aeterna_document_workflow` implementált és elfogadott a current,
existing-managed-Markdown update MVP számára; az `integration` értéke `current`.

A külön CREATE backend implementációja és első valódi governed CREATE
acceptance-e remote verified; contractját az alábbi additív fejezetek rögzítik.
A Document Manager CREATE candidate, read-only plan és explicit grafikus
CREATE Apply felülete implementált. Az izolált testclone grafikus acceptance
sikerét a felhasználó jelentette. Továbbra is kívül
marad: retirement vagy Archive-intake; move/rename; authority change; batch
editing; XLSX; DOCX; source bundle; package manifest.

## 28. CREATE MVP normatív scope

Egy CREATE művelet pontosan egy:

```text
új
+ active
+ managed
+ Markdown
+ document artifact
+ ACTIVE repository layer
```

artifactot hozhat létre. A CREATE nem általános filesystem-create, nem batch
művelet, nem hoz létre directory tree-t, és nem választ automatikusan alternatív
fájlnevet.

```text
CREATE_TARGET_SCOPE = ONE_NEW_ACTIVE_MANAGED_MARKDOWN_DOCUMENT
CREATE_PARENT_DIRECTORY_POLICY = MUST_ALREADY_EXIST
CREATE_TARGET_ABSENCE_POLICY = MUST_BE_ABSENT_EXACT_CASE_UNICODE_AND_FILESYSTEM
```

CREATE v0.1-ben a `lifecycle` kizárólag `active`, az `integration` pedig
`current` vagy `pending_integration` lehet. A választott érték minden esetben
explicit candidate metadata; a tool nem állít be defaultot.

## 29. CREATE target path contract

A target path normalizált, repository-relative POSIX path, `.md` kiterjesztéssel.
Az abszolút path, drive-qualified path, backslash, üres, `.` vagy `..` komponens,
ADS-kettőspont, NUL, Windows reserved basename és záró pont vagy szóköz tiltott.

Engedélyezett dokumentációs gyökerek:

```text
project/**
data/**
design/**
src/engine/docs/**
```

Kifejezetten tiltott target scope többek között:

```text
.git/**
.venv/**
TEMP/**
Archive/**
learning/**
project/generated/**
tools/**
egyéb source/tool gyökerek
```

A target parent directorynek a plan és az apply preflight idején már létező,
valós directorynak kell lennie. A parent és minden létező path-komponens a
canonical repositoryn belül marad, és nem lehet symlink, junction vagy reparse
point.

A target leaf `lstat`/`lexists` szemantikával teljesen hiányzik. Sem fájl,
directory, symlink, junction, broken link, tracked, untracked vagy ignored entry
nem írható felül. A teljes filesystem inventory exact, NFC-normalizált,
casefoldolt és NFC+casefoldolt összevetést végez. Bármely exact, case-insensitive,
Unicode-normalization vagy file/directory collision blokkoló. Collision esetén
nincs automatikus rename vagy alternatív fájlnév.

## 30. CREATE artifact ID contract

Az artifact ID független a fizikai pathtól. A manifest és a candidate
`artifact_id` értéke byte-pontosan egyezik, megfelel a current artifact ID
lexikai szabálynak, és a baseline-plus-one overlayben egyedi.

Blokkoló:

- invalid vagy hiányzó artifact ID;
- exact duplicate ID;
- case-equivalent ID collision, ahol alkalmazható;
- hiányos native metadata;
- `generated: true` human candidate;
- nem támogatott artifact kind vagy type;
- target/path collision.

## 31. CREATE candidate és metadata contract

A candidate teljes Markdown fájl. A Document Manager a repository
szülőkönyvtárából levezetett `AETERNA_LOCAL/document_editor/create` gyökér alatt
tárolja a CREATE candidate-et és a hozzá tartozó sessionadatokat. A production
`plan-create` ezt kizárólag explicit `--external-candidate-root` megadásával,
az engedélyezett gyökér pontos egyezése és a path/symlink/reparse ellenőrzések
mellett fogadja el. A manifesthez viszonyított candidate path nem léphet ki
az engedélyezett tárolási gyökérből.

A backend explicit külső gyökér nélkül továbbra is elfogad repositorybeli,
Git-ignored és untracked `TEMP/` alatti CREATE candidate-et a meglévő
útvonalvédelmekkel. Ez kompatibilitási út, nem a Document Manager elsődleges
tárolása, és nem enged tetszőleges külső könyvtárat. A candidate tárolási pathja
input/evidence; soha nem válik canonical artifact pathtá.

A plan külön rögzíti:

```text
candidate bytes
+ candidate storage path
+ declared repository target path
```

Az overlay artifact rekordja a candidate metadata és H1 tartalmából, valamint a
manifestben deklarált target pathból épül fel.

```text
CREATE_METADATA_POLICY = EXPLICIT_COMPLETE_CANDIDATE_METADATA_NO_DEFAULTS
```

A candidate front matter pontos, teljes kulcskészlete:

```text
artifact_id
kind
type
version
lifecycle
integration
authority
generated
depends_on
supersedes
```

CREATE v0.1 további szabályai:

- `kind: document`;
- `generated: false`;
- `lifecycle: active`;
- `integration: current` vagy `pending_integration`;
- explicit `depends_on` lista, akár üresen, duplikáció nélkül;
- `supersedes: []`;
- pontosan egy nem üres H1;
- nincs ismeretlen metadata-kulcs.

A tool nem talál ki, nem defaultol és nem normalizál governance metadatát.

## 32. CREATE kezdeti version contract

CREATE esetén nincs korábbi semantic document version.

```text
CREATE_INITIAL_VERSION_POLICY = EXPLICIT_CANDIDATE_VERSION_NO_INITIAL_INTENT_NO_DEFAULT
CREATE_INITIAL_VERSION_DEFAULT = NONE
```

A candidate `version` kötelező és explicit; a create manifest `initial_version`
értéke pontosan megegyezik vele. Nincs automatikus `0.1`, nincs
`version_intent = initial`, és a CREATE nem használja az UPDATE
`git-only/minor/major` intent szemantikáját a kezdeti version kiválasztására.

## 33. CREATE authority contract

A candidate `authority` kötelező és explicit. A create manifest/plan
`declared_authority` értéke pontosan megegyezik vele. Az authority nem
inferálható és nem normalizálható.

```text
CREATE_AUTHORITY_POLICY = EXPLICIT_DECLARED_AUTHORITY_EXACT_MATCH_HIGH_RISK_LABEL
```

A `canonical-rules`, `project-direction`, `document-governance` és
`technical-contract` authority új artifacton HIGH review-risk jelölést kap. Ez
nem authority-change művelet és nem enged authority-váltást meglévő artifacton.

## 34. CREATE dependency és overlay modell

A plan-create overlaye:

```text
baseline managed artifact set
+ egy candidate artifact a declared target pathon
```

Generic count contract:

```text
EXPECTED_ARTIFACT_COUNT_AFTER = BASELINE_ARTIFACT_COUNT + 1
```

A teljes overlayt írás előtt validálni kell duplicate ID, missing dependency,
self dependency, dependency cycle, path collision és scope violation ellen. A
plan-create ugyanabban az outputban közli a candidate forward dependencyit,
direct reverse dependencyit és transitive impactját. Nincs külön
`impact-create` parancs.

## 35. Generated view contract

Derived outputok:

```text
project/generated/artifacts_registry.json
project/generated/DOCUMENT_INDEX.md
```

A plan-create a baseline-plus-one overlayből determinisztikusan, memóriában
rendereli őket. Kézi szerkesztésük tiltott. A normal first CREATE rendszerint a
new documentet és a két byte-ban változó generated view-t írja, de a contract a
determinált tényleges byte-eltérést rögzíti, és nem hardcode-olja a három írást.

```text
GENERATED_VIEW_STRATEGY = DETERMINISTIC_IN_MEMORY_BASELINE_PLUS_ONE_OVERLAY
```

## 36. CREATE manifest contract

Schema:

```text
aeterna-document-create-manifest/0.1
```

Kötelező deklarált mezők:

- `schema_version`;
- `artifact_id`;
- `target_path`;
- `candidate_path`;
- `expected_branch`;
- `expected_head`;
- `candidate_sha256`;
- `candidate_metadata_fingerprint`;
- complete `candidate_metadata`;
- `candidate_byte_convention` = UTF-8, BOM false, LF;
- `declared_authority`;
- `initial_version`.

Derived, nem felhasználó által felülírható invariáns:

```text
target_must_be_absent = true
parent_directory_must_already_exist = true
expected_artifact_count_after = baseline_artifact_count + 1
```

CREATE esetén nincs baseline target SHA vagy baseline target metadata
fingerprint; ezek helyett exact target absence, exact branch/HEAD, clean Git
baseline, baseline artifact-set identity és immutable candidate identity a
precondition.

## 37. CREATE plan contract

Normatív schema:

```text
aeterna-document-create-plan/0.1
```

A determinisztikus plan legalább bizonyítja:

- `operation = create`;
- canonical repository identity;
- expected branch és HEAD;
- clean baseline worktree és empty staging;
- baseline artifact scan identity/count;
- artifact ID;
- declared target path és target absence;
- candidate path, SHA-256, teljes metadata és fingerprint;
- candidate byte convention;
- declared authority és explicit initial version;
- dependency/impact eredmény;
- generated in-memory preview és hashek;
- expected changed pathok;
- semantic plan identity.

Random operation ID és timestamp nem része a semantic plan identitynek.

## 38. CREATE review contract

Normatív schema:

```text
aeterna-document-create-review/0.1
```

A review CREATE-specifikusan rögzíti:

- baseline branch, HEAD, worktree és staging;
- target absence a write előtt;
- artifact identity és target path;
- candidate és final SHA-256;
- teljes metadata, initial version és declared authority;
- dependency graph és impact;
- generated output hashek;
- transaction writes;
- rollback state;
- post-create artifact count;
- expected új untracked target;
- generated tracked módosítások;
- scope validation, tests és `git diff --check`;
- final `PASS`, `FAIL` vagy `BLOCKED` státusz.

A review schema nem helyettesíti és nem módosítja az UPDATE review 0.1 sémát.

## 39. Apply architektúra és dispatch

A normál production `apply PLAN.json` a materializált plan schema alapján
dispatch-el:

```text
aeterna-document-update-plan/0.1 -> UPDATE behavior
aeterna-document-create-plan/0.1 -> CREATE behavior
```

Ismeretlen schema vagy operation blokkoló. A `semantic-governance-change`
UPDATE a normál `apply` belépési ponton blokkol; csak a külön interaktív
`apply-governance` vagy `apply-governance-gui` út alkalmazhatja. A CREATE és
UPDATE ugyanazt a repositoryszintű Apply-zárat és tartós recovery-védelmet
használja.

## 40. CREATE immediate pre-write recomputation

Közvetlenül az első írás előtt újra bizonyítandó:

- branch és HEAD változatlan;
- staging üres;
- baseline worktree továbbra is elfogadható;
- candidate bytes, SHA és metadata változatlan;
- baseline artifact set változatlan;
- target továbbra is teljesen hiányzik;
- nincs új exact, case, Unicode vagy filesystem collision;
- parent továbbra is létező real directory;
- nincs traversal, symlink vagy reparse escape;
- teljes overlay és dependency graph valid;
- generated preview byte-pontosan egyezik az immutable plannel.

Nincs fuzzy recovery, automatikus rebase, alternate filename vagy újabb emberi
változást felülíró írás.

## 41. CREATE post-write és Git semantics

Plan és apply előtt minden non-ignored untracked fájl blokkoló; a stagingnek
üresnek kell lennie. Ez a baseline guard változatlanul szigorú.

Sikeres CREATE után kizárólag a declared target lehet expected untracked fájl.
A byte-ban változó generated view-k tracked unstaged módosítások. Bármely más
tracked vagy untracked eltérés blokkoló.

```text
POST_CREATE_UNTRACKED_HANDLING = EXACT_DECLARED_TARGET_ALLOWLIST
```

Az allowlist kizárólag post-create ellenőrzésre szolgál, és nem lazíthatja a
plan/apply előtti clean-worktree követelményt. Mivel a `git diff --check` nem
látja az untracked targetet, annak encoding, newline, tartalom- és trailing-
whitespace ellenőrzése közvetlenül is kötelező.

## 42. CREATE transaction és rollback

A CREATE a közös repositoryszintű Apply-zárat és a tartós `.git`
tranzakciós/recovery-területet használja. Az új target nem rendelkezik original
backuppal. Minden már létező generated/touched fájl byte-backupot kap.

Write utáni hiba esetén:

- kizárólag a tranzakció által létrehozott target távolítható el;
- minden pre-existing touched fájl original bytejai visszaállítandók;
- original hashek ellenőrizendők;
- a targetnek ismét hiányoznia kell;
- a failed transaction evidence megőrzendő.

Soha nem törölhető olyan path, amely a tranzakció előtt létezett. A new-path
rollback tesztek és az első valódi CREATE acceptance teljesültek; ezek a
garanciák a production CREATE működés részei.

## 43. Kötelező failure injection acceptance

A PILOT-8D regressziós tesztjei az alábbi hibapontokat fedik le:

- failure after new document write;
- failure after registry write;
- failure after index write;
- post-validation failure;
- rollback verification failure.

Minden teszt bizonyítja a target újbóli hiányát, az eredeti generated byteokat,
az üres staginget és a baseline Git-állapot helyreállítását.

## 44. CLI contract

Current accepted production surface:

```text
resolve
impact
inspect-update-baseline
plan-update
inspect-create-baseline
plan-create
apply
apply-governance
apply-governance-gui
verify-review
```

A `plan-create` tartalmazza a CREATE identity, validation és impact outputot.
Nincs `resolve-create` és nincs `impact-create`. A read-only parancsok nem
mutálnak; az `apply` a normál UPDATE/CREATE tervet, a két governance Apply
belépési pont csak külön interaktív jóváhagyással a magas kockázatú UPDATE-et
alkalmazhatja.

## 45. Első valós CREATE acceptance

Az elfogadott első valós target az AETERNA Document Editor v0.1 specification.

A dokumentum PILOT-8E alatt, emberileg áttekintett candidate-ből, production
governed CREATE Apply útján létrejött a
`project/requirements/DOCUMENT_EDITOR_SPECIFICATION.md` útvonalon. Az első
valódi CREATE acceptance remote verified; commit:
`4647d263e2ae23019723e8db8a0cebd92a065457`.

## 46. Implementációs fázisok

```text
PILOT-8A = CREATE design audit / COMPLETE
PILOT-8B = CREATE governance contract / COMPLETE_AND_REMOTE_VERIFIED
PILOT-8C = read-only plan-create implementation + tests / COMPLETE_AND_REMOTE_VERIFIED
PILOT-8D = transactional CREATE apply + rollback/review + tests / COMPLETE_AND_REMOTE_VERIFIED
PILOT-8E = first real governed CREATE acceptance / COMPLETE_AND_REMOTE_VERIFIED
```

A Document Manager CREATE candidate, read-only plan és külön jóváhagyáshoz
kötött grafikus CREATE Apply felülete implementált. Az izolált tesztclone
grafikus acceptance-e felhasználói beszámoló alapján PASS; a production
backend review és verify-review ettől külön bizonyíték. Az eredeti
repositoryban végzett grafikus CREATE Apply-t ez nem állítja.

## 47. Továbbra is out of scope

Nem támogatott:

- retirement és Archive intake;
- move és rename;
- authority change meglévő artifacton;
- batch create és batch update;
- XLSX vagy DOCX edit/create;
- source bundle mutation;
- package manifest mutation;
- directory migration.

```text
GENERIC_MOVE_SUPPORT = NO
GENERIC_RETIRE_SUPPORT = NO
```
