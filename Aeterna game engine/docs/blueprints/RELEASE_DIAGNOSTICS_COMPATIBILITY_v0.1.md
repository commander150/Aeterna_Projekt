# AETERNA – RELEASE / DIAGNOSTICS / COMPATIBILITY BLUEPRINT

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** architecture blueprint / release-maturity plan
- **Javasolt repository-útvonal:** `Aeterna game engine/docs/blueprints/RELEASE_DIAGNOSTICS_COMPATIBILITY_v0.1.md`
- **Repository-bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Nem release automation implementation spec.**

---

# 1. Cél

A jelenlegi manuálisan reprodukálható production proofot olyan rendszerbe emelni, amely:

- local és CI környezetben ugyanazt futtatja;
- pontos release identityt rögzít;
- compatibility mismatchet korán blokkol;
- strukturált diagnostics/log/metric/trace adatot ad;
- bugokat reprodukálható bundle-lé alakít;
- nem szivárogtat hidden/developer adatot.

---

# 2. Existing proof – preserved

Current accepted foundation:
- C# Debug/Release;
- 222/222 tests;
- canonical comparison fixture;
- canonical bytes/hash;
- 100/100 determinism;
- Godot C# Debug;
- positive smoke;
- negative smoke;
- viewer safety;
- stale rejection;
- diff check.

Ez marad a **proof content**.

CI később csak automatikus végrehajtási host.

---

# 3. Canonical acceptance runner – proposed

Egyetlen entry point:

```text
run_acceptance
```

logikai stage-ekkel:

```text
engine-debug
engine-tests-debug
engine-release
engine-tests-release
canonical-comparison
determinism
godot-build
godot-smoke-positive
godot-smoke-negative
package-validation
artifact-summary
```

Lehet PowerShell/.NET tool/script; a technológia implementationkor döntendő.

Output:
- machine-readable JSON;
- human Markdown summary.

---

# 4. AcceptanceProof schema – candidate

```text
ProofSchemaVersion
RepositoryCommit
DirtyWorktree?          # release módban false required
StartedAt
CompletedAt
Environment:
  OS
  DotNetSdk
  GodotVersion
Engine:
  TargetFramework
  BuildConfiguration
  TestPassed
  TestTotal
CanonicalFixture:
  Bytes
  Sha256
Determinism:
  Runs
  Passed
Godot:
  BuildPassed
  PositiveSmoke
  NegativeSmoke
Packages:
  CardDatabaseFingerprint
  RegistryFingerprint
OverallStatus
```

Nem kell minden logot a JSON-ba inline tenni; log artifact külön lehet.

---

# 5. CI policy – later implementation

## Pull request / branch
Gyors gate:
- compile;
- tests;
- static/schema validation.

## Main / release candidate
Full acceptance:
- Debug/Release;
- fixture;
- determinism;
- Godot smoke;
- package validation.

A repository jelenlegi workflow-hiánya miatt ez új infrastruktúra, nem „javítás”.

---

# 6. ReleaseManifest – candidate

```text
ReleaseManifest
- ReleaseId
- GitCommitSha
- EngineBuildVersion
- EngineContractVersion
- RulesBaseSourceVersion
- RulesExpansionSourceVersion
- CardDatabasePackageId/Version/Fingerprint
- RegistryPackageId/Version/Fingerprint
- RuntimePackageVersion/Fingerprint
- GodotClientBuildVersion
- SaveFormatVersion?
- ReplayFormatVersion?
- NetworkProtocolVersion?
- AcceptanceProofHash
- ArtifactHashes
```

Optional mezők csak amikor az adott subsystem létezik.

---

# 7. Build identity

A current csproj .NET 8 target frameworkje build input.

Később release build:
- SDK pinned;
- Godot version pinned;
- package inputs pinned.

`GeneratedAt` timestamp nem legyen determinism identity része, ha ugyanazt a contentet hasonlítjuk.

---

# 8. CompatibilityMatrix – candidate

```text
EngineContractVersion
SupportedCardSchemaRange
SupportedRegistrySchemaRange
SupportedRuntimePackageRange
SupportedSaveVersions
SupportedReplayVersions
SupportedNetworkProtocolVersions
```

A loader a tényleges persisted/package határokat enforcementolja.

---

# 9. Diagnostic layers

## EngineDiagnostic
Current public/internal request outcome.

## PublicDiagnostic
Future network-safe projection.

## PackageDiagnostic
Build/data.

## OperationalLog
Runtime process log.

## Metric
Aggregated observation.

## Trace
One causal request/resolution path.

## AcceptanceProof
Release evidence.

No shared catch-all type required.

---

# 10. PublicDiagnostic – proposed

```text
Code
Severity
Category
Blocking
SafeMessage
RetryPolicy
SafeDetails
```

Developer/internal:
- DeveloperMessage;
- exception;
- raw state/context;
- stack trace.

Godot local debug mode továbbra is hozzáférhet trusted diagnosticshoz explicit mode-ban.

---

# 11. Structured log fields

Minimum candidate:

```text
timestamp
level
category
code/event
match_id?
state_version?
request_id?
action_id?
resolution_id?
reaction_window_id?
event_sequence?
duration_ms?
```

Default:
- no hidden card identity;
- no deck order;
- no secret target candidate;
- no reconnect/auth token.

---

# 12. Trace correlation

Accepted action path:

```text
RequestId
→ ActionId
→ ResolutionId(s)
→ EngineEvent sequence(s)
→ Trigger/PendingWindow ID(s)
```

Trace sampling later.

Rules semantics nem függ tracing bekapcsolásától.

---

# 13. Metrics

Initial useful metrics:
- match create count;
- active matches;
- action submit count;
- action reject count by safe code;
- ListLegalActions duration;
- SubmitAction duration;
- effect resolution duration;
- event count/match;
- package load duration;
- snapshot projection duration;
- AI batch throughput later.

No player hidden content in labels.

---

# 14. Performance baseline

Separate benchmark project/tool later.

Baseline operations:
- create match;
- list legal actions;
- simple play;
- effect resolution;
- event projection;
- package load;
- 1000-transition synthetic run.

Compare relative regression across same controlled environment.

---

# 15. BugReportBundle

Candidate folder/archive:

```text
manifest.json
acceptance/release_identity.json
environment.json
diagnostics.jsonl
runtime_log.jsonl
replay_or_decision_suffix.jsonl
snapshot.json              # projection policy dependent
event_suffix.jsonl
```

Player export:
- viewer-safe only.

Developer internal:
- full state possible.

---

# 16. Crash policy

Expected rules reject:
- return diagnostic.

Unsupported mandatory content:
- controlled blocking.

Invariant/internal exception:
- capture;
- mark match faulted/abort according to host policy;
- preserve bug bundle;
- do not continue unknown state.

Exact host behavior later.

---

# 17. Release artifact composition

Candidate:
- Godot client build;
- engine assemblies;
- runtime/canonical package;
- release manifest;
- license/attribution;
- acceptance proof;
- optional symbols/debug package separate.

No development source XLSX required in end-user runtime.

---

# 18. Version boundaries

Version only externally persisted/consumed contracts:
- engine API/contract;
- package schema;
- ability/module persisted schema;
- save/replay;
- network protocol;
- release.

Internal refactor:
- no forced semantic version.

---

# 19. Migration rules

Persisted artifact:
```text
exact compatible
→ load

known migratable
→ explicit migration + validation

unsupported
→ fail with clear diagnostic
```

No silent field default that changes game semantics.

---

# 20. Documentation/proof relation

Checkpoint:
- historical accepted evidence.

AcceptanceProof:
- machine artifact.

Status doc:
- current interpretation.

Release manifest:
- shipped identity.

Egyik sem írja felül a rules source-t.

---

# 21. Implementation order

R1.1 acceptance runner  
R1.2 machine proof output  
R1.3 CI bind  
R1.4 release manifest  
R1.5 public diagnostic projection before network  
R1.6 structured logs  
R1.7 metrics/traces  
R1.8 bug bundle  
R1.9 performance baseline

Nem kell mind a Reaction implementation előtt.

---

# 22. Reaction dependency

Reaction v1 implementationhez közvetlenül csak:
- existing EngineDiagnostic;
- existing event correlation;
- current test/proof recipe

szükséges.

R1 full CI/observability nem prerequisite.

De Reaction milestone után a full acceptance runner jó első automatizálási cél.

---

# 23. Acceptance invariants

1. local/CI same core commands;
2. release from clean commit;
3. proof stores commit/hash;
4. package fingerprints included;
5. mismatch fails before match start;
6. public diagnostic no developer secrets;
7. logs no hidden info default;
8. metrics do not affect determinism;
9. replay/bug bundle versioned;
10. internal failure not silently converted to normal reject.

---

# 24. Non-goal

- cloud vendor selection;
- telemetry SaaS;
- crash-reporting service selection;
- release storefront;
- installer/updater;
- auto deployment;
- production server hosting;
- performance SLA.

---

# 25. Változásnapló

## 0.1 – 2026-08-15
- current acceptance proof formalizálva;
- CI és proof különválasztva;
- release manifest és compatibility matrix candidate;
- diagnostics/log/metric/trace külön rétegek;
- bug report bundle és public diagnostic boundary rögzítve.
