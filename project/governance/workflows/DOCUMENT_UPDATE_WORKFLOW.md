---
artifact_id: AET-DOC-DOCUMENT-UPDATE-WORKFLOW
kind: document
type: workflow
version: "0.2"
lifecycle: active
integration: current
authority: operational-workflow
generated: false
depends_on:
  - AET-DOC-DOCUMENT-GOVERNANCE
  - AET-DOC-GITHUB-WORKFLOW
supersedes: []
---

# AETERNA dokumentumfrissítési workflow

## 1. Cél, hatáskör és authority

Ez a dokumentum az AETERNA lokális dokumentumszerkesztő és -frissítő
workflow-jának operatív contractja. A workflow feladata, hogy stabil artifact ID
alapján feloldja a célartifactot, ellenőrizze a kiinduló állapotot, egy előre
rögzített tervhez kösse a módosítást, tranzakciósan alkalmazza a jóváhagyott
jelöltet, majd ellenőrizhető review-bizonyítékot készítsen.

A dokumentum-governance határozza meg az artifact-identitás, authority,
lifecycle, Archive és megőrzés szabályait. A GitHub workflow határozza meg a
lokális eredmény review-, commit-, push- és remote handoffját. A jelen workflow
ezeket nem írja felül, hanem a dokumentumfrissítés részletes helyi műveleti
rendjét adja meg.

Az `integration: current` azt jelenti, hogy a workflow implementált és az aktív
operatív dokumentumfrissítési út része. A Markdown MVP implementációja a
`tools/aeterna_document_workflow` alatt létezik, és a kontrollált valódi
repository-acceptance teszten megfelelt. A jelen dokumentum marad az operatív
contract; az implementációs bizonyítékot a repository kódja, tesztjei,
review-evidence anyagai és Git-története adják.

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

- új artifact létrehozása;
- retirement vagy Archive-intake;
- move és rename;
- authority-váltás;
- batch editing;
- XLSX, DOCX, source bundle és package manifest szerkesztés;
- exact patch vagy unified diff bemenet;
- external-editor handoff;
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
jelentés változására. Az MVP ezt nem hagyhatja jóvá hallgatólagosan. Ha egy
candidate tartalma ilyen változásra utal, a plan ezt jelzi, és a szokásos update
apply blokkol, amíg külön, explicit governance scope és review nincs.

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

Csak az alábbi forma mutálhat repository-t:

```text
apply PLAN.json
```

Az apply:

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
same-volume ignored operation directory
→ minden intended byte előállítása
→ teljes overlay validáció
→ transaction journal
→ touched existing fájlok byte-backupja
→ atomic replacement
→ post-write validáció
```

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

MVP surface:

```text
resolve
impact
plan-update
apply
verify-review
```

Read-only: `resolve`, `impact`, `plan-update`, `verify-review`.

Mutating: kizárólag `apply`.

Későbbi, nem aktív parancsjelöltek: `plan-create`, `plan-retire`, `plan-move`,
`authority-change`.

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

A current MVP-n kívül marad: `create`; retirement vagy Archive-intake;
move/rename; authority change; batch editing; XLSX; DOCX; source bundle; package
manifest.
