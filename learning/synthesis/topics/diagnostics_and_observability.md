# AETERNA – CROSS-PROJECT SYNTHESIS: RELEASE, DIAGNOSTICS AND OBSERVABILITY

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első release/diagnostics/observability synthesis
- **Javasolt repository-útvonal:** `learning/synthesis/topics/diagnostics_and_observability.md`
- **AETERNA production összevetési bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Nem AETERNA-authority.**

---

# 1. Evidence

AETERNA current:
- Debug/Release build proof;
- 222/222 tests;
- canonical fixture SHA;
- 100/100 determinism;
- Godot positive/negative smoke;
- `EngineDiagnostic`;
- package diagnostics/build report;
- package/schema/data version gates;
- checkpoint proof continuity;
- .NET 8 production engine;
- nincs jelenleg repository-szintű GitHub Actions workflow.

Learning:
- jcbcn/card-game-engine:
  - test projects;
  - benchmarks;
  - PublicApiAnalyzers;
  - NuGet packaging;
  - semantic-release;
  - artifact/release workflow;
- Nakama:
  - structured server runtime;
  - queues/backpressure;
  - operational lifecycle;
- Colyseus:
  - session lifecycle;
  - rate limiting;
  - schema rejection;
- boardgame.io:
  - state/log separation;
  - versioned sync.

---

# 2. P-REL-001 – Acceptance proof és CI két külön fogalom

AETERNA current proof nagyon erős, de manuálisan reprodukált.

```text
AcceptanceRecipe
→ deterministic commands
→ PASS evidence
```

CI:

```text
AcceptanceRecipe
→ automatically executed gate
```

## Következtetés

CI hiánya nem teszi érvénytelenné a meglévő proofot.

Viszont release readinesshez:
- emberi elfelejtés;
- platform drift;
- accidental regression

ellen automatizált gate értékes.

---

# 3. P-REL-002 – Egyetlen canonical acceptance recipe

Ne legyen:
- README-ben egy parancs;
- checkpointban másik;
- developer machine-en harmadik.

Candidate:

```text
build
unit/integration tests
canonical fixture comparison
determinism
Godot build
positive smoke
negative smoke
diff/format validation
```

ugyanaz a script/runner:
- local;
- CI;
- pre-release

módban.

---

# 4. P-REL-003 – Proof artifact versioned

Acceptance eredmény ne csak konzoltext legyen.

Candidate machine-readable:

```text
AcceptanceProof
- proof_schema_version
- commit_sha
- engine_version
- rules_source_version
- package fingerprints
- sdk/runtime versions
- build configuration
- test counts
- fixture bytes/hash
- determinism runs/hash
- Godot version/build
- smoke results
- started/completed time
- overall status
```

Markdown summary ebből generálható.

---

# 5. P-REL-004 – Release identity több komponensből áll

Egy „AETERNA v0.x” önmagában nem elég reprodukcióhoz.

Release identity candidate:

```text
ReleaseId
EngineBuildId
GitCommitSha
RulesSourceVersion
CardDatabaseFingerprint
RegistryFingerprint
RuntimePackageFingerprint
ContractVersion
Save/Replay compatibility version later
GodotClientBuildId
```

Nem minden mező player-facing.

---

# 6. P-REL-005 – Engine version és data version külön

Engine binary lehet ugyanaz több data builddel.

Data package frissülhet engine code nélkül.

Ezért:

```text
EngineVersion
!=
PackageDataVersion
!=
SchemaVersion
!=
RulesSourceVersion
```

A current CanonicalPackageLoader már jó alapot ad.

---

# 7. P-REL-006 – Compatibility gate explicit

Loader/runtime indulás előtt:

```text
engine supported package schema range
package required registry version
package/data fingerprint
contract compatibility
```

ellenőrzés.

Később save/replay:
- SaveFormatVersion;
- ReplayFormatVersion;
- minimum/maximum compatible engine version.

Mismatch:
- controlled error;
- no silent reinterpretation.

---

# 8. P-REL-007 – Diagnostic taxonomy külön a loggingtól

## EngineDiagnostic
Egy request/rules döntés strukturált eredménye.

## Build/PackageDiagnostic
Adat/package validitás.

## OperationalLog
Futó folyamat történése:
- startup;
- match create;
- disconnect;
- exception;
- package load.

## Metric
Aggregált szám:
- action latency;
- matches;
- rejects;
- queue depth;
- memory.

## Trace
Egy konkrét művelet causal pathja:
- request ID;
- action ID;
- resolution ID;
- event IDs.

## AcceptanceProof
Release/build evidence.

Ezek külön fogalmak.

---

# 9. P-REL-008 – Safe/public diagnostics külön internal diagnosticstól

Current EngineDiagnostic rich fields:
- safe message;
- developer message;
- details.

Local toolingnál hasznos.

Remote/untrusted client előtt:

```text
InternalDiagnostic
→ PublicDiagnosticProjection
```

Public:
- code;
- safe_message;
- retry policy;
- safe structured fields.

Internal:
- developer message;
- raw IDs/context;
- exception details;
- stack trace.

---

# 10. P-REL-009 – Correlation ID chain

Már vannak:
- request ID;
- action ID;
- event ID;
- resolution ID;
- pending trigger ID.

Később reaction/window ID.

Candidate trace:

```text
MatchId
RequestId
ActionId
ResolutionId
ReactionWindowId?
EventId/Sequence
```

Nem kell egyetlen mega-ID.

A kapcsolat legyen visszakereshető.

---

# 11. P-REL-010 – Structured operational logs

Player-visible textlog helyett machine-readable log fields:

```text
timestamp
severity
category
match_id?
player/session?
request_id?
state_version?
event_sequence?
code
message
```

Sensitive payload ne kerüljön default logba.

Hidden hand/card identity csak debug-redaction policyval.

---

# 12. P-REL-011 – Metrics ne legyen rules authority

Példák:
- submit latency;
- legal-action enumeration latency;
- effect resolution latency;
- event count;
- reject reason counts;
- memory;
- package load time.

Metric instrumentation:
- nem változtat orderinget;
- nem mutál state-et;
- determinism proof mellett kikapcsolható/semleges.

---

# 13. P-REL-012 – Performance baseline, nem premature optimization

jcbcn benchmark layer jó minta.

AETERNA későbbi baseline:
- match creation;
- legal action enumeration;
- canonical effect execution;
- 1000-turn synthetic run;
- package load;
- snapshot/event projection;
- AI batch matches.

Csak regressziódetektálásra.

Nem kell fix performance SLA most.

---

# 14. P-REL-013 – CI stage-ek

Candidate:

```text
CI-1 formatting/static validation
CI-2 C# Debug build
CI-3 C# tests
CI-4 C# Release build/tests
CI-5 canonical fixture/determinism
CI-6 Godot C# build
CI-7 positive/negative smoke
CI-8 documentation/package schema check
```

PR-nél lehet részleges/gyors.

Main/release candidate teljes.

---

# 15. P-REL-014 – Release csak immutable inputból

Release ne local uncommitted working treeből készüljön.

Candidate:
- clean Git commit/tag;
- pinned SDK/tool versions;
- verified package fingerprints;
- proof PASS;
- artifact hash.

Artifact:
- engine binaries;
- Godot client;
- runtime package;
- release manifest;
- license/attribution bundle.

---

# 16. P-REL-015 – Semantic version csak publikus contractokra

Nem kell minden internal refactorhoz version bump.

Version boundary, ha változik:
- public API/contract;
- package schema;
- save/replay schema;
- content module contract;
- network protocol;
- player-facing release.

Internal class/method refactor nem feltétlen semantic change.

---

# 17. P-REL-016 – Backward compatibility policy explicit

Minden persisted/external artifactnál:

```text
same-version only
backward compatible
migration supported
unsupported
```

legyen eldöntve.

Ne legyen implicit „majd biztos betöltődik”.

---

# 18. P-REL-017 – Bug report bundle reprodukálható

Candidate:

```text
BugReportBundle
- release manifest
- engine/package versions
- player-safe or trusted replay
- latest snapshot/checkpoint
- event suffix
- diagnostics
- recent structured logs
- environment info
```

Player-submitted bundle:
- hidden/private data redaction policy.

Developer trusted bundle:
- full state only explicit opt-in/internal environment.

---

# 19. P-REL-018 – Crash/exception külön rules rejecttől

## Rules reject
Expected:
- diagnostic;
- state unchanged.

## Unsupported content
Controlled blocking diagnostic.

## Internal invariant failure
Bug:
- exception;
- crash/abort match as policy;
- bug bundle.

Ne konvertáljunk minden internal exceptiont `action_rejected`-dé.

---

# 20. P-REL-019 – Release notes generálhatók proofból és commitsból

Human release notes:
- gameplay changes;
- content changes;
- compatibility.

Machine manifest:
- exact hashes/versions.

A kettő külön artifact.

---

# 21. P-REL-020 – No workflow ≠ no provenance

A jelen repositoryban nincs GitHub Actions workflow.

Ezért current proof provenance:
- checkpoint docs;
- recorded commits;
- deterministic hashes;
- user-run command output.

R1 recommendation:
- később CI automatizálja ugyanazt;
- a régi proof history nem törlendő vagy átnevezendő „nem validnak”.

---

# 22. Anti-patternök

| ID | Név |
|---|---|
| `A-REL-001` | CI result = rules authority |
| `A-REL-002` | release local dirty worktreeből |
| `A-REL-003` | engine/data/rules version egyetlen homályos verzióban |
| `A-REL-004` | package compatibility silent best-effort |
| `A-REL-005` | developer diagnostic raw clientnek |
| `A-REL-006` | log tartalmaz hidden card data defaultként |
| `A-REL-007` | metrics mutál rules state-et |
| `A-REL-008` | benchmark egyetlen dev gép abszolút számát SLA-nak tekinti |
| `A-REL-009` | manual proof és CI eltérő recipe |
| `A-REL-010` | exception normál rules rejectként elnyelve |
| `A-REL-011` | release notes = exact manifest |
| `A-REL-012` | save/replay/network version implicit |
| `A-REL-013` | bug report reprodukciós state/fingerprint nélkül |
| `A-REL-014` | observability eventet gameplay eventként tárolja |

---

# 23. Verdict

R1 architecture blueprinthez nincs szükség új külső forrásra.

AETERNA-nak:
- proof foundation már erős;
- structured diagnostics már erős;
- package version gates részben megvannak.

A fő következő maturity lépések:
1. canonical acceptance runner;
2. CI binding;
3. release manifest/fingerprints;
4. public diagnostic projection;
5. structured operational logging/metrics/tracing;
6. bug report bundle;
7. explicit compatibility matrix.
