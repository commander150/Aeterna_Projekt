# AETERNA Game Engine – Open Questions Decisions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.2  
**Dátum:** 2026-08-15  
**Státusz:** review draft – az OQ-regiszter 2.2 párdokumentuma  
**Kapcsolódó kérdésregiszter:** `OPEN_QUESTIONS.md`  
**Dokumentációs remote bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`  
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95`

Ez a fájl az `OPEN_QUESTIONS.md` tételeihez tartozó current canonical/default,
részleges, deferred, extension és superseding döntéseket rögzíti.

## 1. Általános döntési elvek

1. A hivatalos játékszabályforrás az elsődleges rules authority.
2. Egy meccsnek pontosan egy authoritative state-je lehet.
3. Production authoritative runtime: C#/.NET.
4. Godot/GDScript: vizuális kliens/adapter/presentation.
5. Python: külső adat-, audit-, fixture-, AI-, batch-, build- és referencia-tooling.
6. UI és fair AI nem találgathat legalitást; a C# engine legal actiont ad és minden requestet újravalidál.
7. Player-facing output nem szivárogtathat hidden informationt.
8. Runtime package statikus, validált derived programadat, nem rules authority és nem MatchState.
9. Silent fallback/guessing/partial canonical commit tilos.
10. A dokumentáció elsősorban meglévő aktív fájl frissítésével és történetmegőrző verziózással fejlődik.

### 1.1 Evolving-design elv

Az elfogadott döntés **current canonical/default**, nem metafizikailag örök.

Playtest, Expansion, meta vagy bizonyított design hiba esetén még foundation-szintű döntés is
módosítható, de magasabb változtatási küszöbbel:

```text
new evidence
→ explicit human decision
→ impact analysis
→ rules/contract migration
→ implementation
→ regression/playtest/audit
→ history preserved
```

A korábbi döntés kapcsolatjelöléssel megmarad:

```text
EXTENDED
SCOPED
SUPERSEDED
REPLACED
```

Reserved future extension önmagában nem tesz egy current-default OQ-t `partly_answered` státuszúvá.

---

## 2. Decision coverage index

Minden OQ explicit módon visszakereshető ebben a dokumentumban.

| OQ | Current status | Döntési blokk |
|---|---|---|
| `OQ-ARCH-001` | `answered` | Runtime és réteghatárok |
| `OQ-ARCH-002` | `answered` | Runtime és réteghatárok |
| `OQ-ARCH-003` | `answered` | Runtime és réteghatárok |
| `OQ-DOC-001` | `answered` | Dokumentáció |
| `OQ-DOC-002` | `answered` | Dokumentáció |
| `OQ-DOC-003` | `answered` | Dokumentáció |
| `OQ-DATA-001` | `answered` | Runtime package, build és provenance |
| `OQ-DATA-002` | `answered` | Runtime package, build és provenance |
| `OQ-DATA-003` | `answered` | Diagnostics, support és source correction |
| `OQ-DATA-004` | `answered` | Diagnostics, support és source correction |
| `OQ-TECH-004B` | `answered` | Runtime package, build és provenance |
| `OQ-DATA-005` | `answered` | Runtime package, build és provenance |
| `OQ-DATA-006` | `answered` | Runtime package, build és provenance |
| `OQ-SNAP-001` | `answered` | Projection és visibility |
| `OQ-SNAP-002` | `partly_answered` | Aeternal és Pecsét |
| `OQ-SNAP-003` | `answered` | Projection és visibility |
| `OQ-SNAP-004` | `answered` | Projection és visibility |
| `OQ-SNAP-005` | `partly_answered` | Reaction, timing és pending state |
| `OQ-SNAP-006` | `answered` | Projection és visibility |
| `OQ-LA-001` | `answered` | Legal action és request authority |
| `OQ-LA-002` | `partly_answered` | Reaction, timing és pending state |
| `OQ-LA-003` | `partly_answered` | Combat |
| `OQ-LA-004` | `partly_answered` | Aura és payment |
| `OQ-LA-005` | `partly_answered` | Targeting, choice és partial resolution |
| `OQ-LA-006` | `partly_answered` | Legal action és request authority |
| `OQ-LA-007` | `answered` | Legal action és request authority |
| `OQ-AR-001` | `partly_answered` | Legal action és request authority |
| `OQ-AR-002` | `answered` | Legal action és request authority |
| `OQ-AR-003` | `answered` | Legal action és request authority |
| `OQ-AR-004` | `partly_answered` | Targeting, choice és partial resolution |
| `OQ-AR-005` | `answered` | Reaction, timing és pending state |
| `OQ-AR-006` | `partly_answered` | Targeting, choice és partial resolution |
| `OQ-AR-007` | `answered` | Diagnostics, support és source correction |
| `OQ-EVENT-001` | `answered` | Event, replay és balance event |
| `OQ-EVENT-002` | `answered` | Event, replay és balance event |
| `OQ-EVENT-003` | `answered` | Event, replay és balance event |
| `OQ-EVENT-004` | `answered` | Event, replay és balance event |
| `OQ-EVENT-005` | `deferred` | Event, replay és balance event |
| `OQ-EVENT-006` | `deferred` | Event, replay és balance event |
| `OQ-DIAG-001` | `answered` | Diagnostics, support és source correction |
| `OQ-DIAG-002` | `answered` | Diagnostics, support és source correction |
| `OQ-DIAG-003` | `answered` | Diagnostics output |
| `OQ-DIAG-004` | `answered` | Diagnostics output |
| `OQ-DIAG-005` | `answered` | Diagnostics, support és source correction |
| `OQ-DIAG-006` | `deferred` | Diagnostics output |
| `OQ-DIAG-007` | `answered` | Diagnostics output |
| `OQ-ABIL-001` | `answered` | Ability/effect rendszer |
| `OQ-ABIL-002` | `answered` | Ability/effect rendszer |
| `OQ-ABIL-003` | `answered` | Ability/effect rendszer |
| `OQ-ABIL-004` | `partly_answered` | Reaction, timing és pending state |
| `OQ-ABIL-005` | `partly_answered` | Ability/effect rendszer |
| `OQ-ABIL-006` | `partly_answered` | Aeternal és Pecsét |
| `OQ-ABIL-007` | `answered` | Ability/effect rendszer |
| `OQ-ABIL-008` | `answered` | Ability/effect rendszer |
| `OQ-TECH-001` | `answered` | Technológia, acceptance és product runtime |
| `OQ-TECH-002` | `answered` | Technológia, acceptance és product runtime |
| `OQ-TECH-003` | `answered` | Technológia, acceptance és product runtime |
| `OQ-TECH-004` | `answered` | Technológia, acceptance és product runtime |
| `OQ-TECH-005` | `answered` | Technológia, acceptance és product runtime |
| `OQ-TECH-006` | `answered` | Technológia, acceptance és product runtime |
| `OQ-AI-001` | `answered` | AI, simulation és balance |
| `OQ-AI-002` | `answered` | AI, simulation és balance |
| `OQ-AI-003` | `answered` | AI, simulation és balance |
| `OQ-AI-004` | `partly_answered` | AI, simulation és balance |
| `OQ-AI-005` | `partly_answered` | AI, simulation és balance |
| `OQ-AI-006` | `deferred` | AI, simulation és balance |
| `OQ-AI-007` | `deferred` | AI, simulation és balance |
| `OQ-RULES-001` | `answered` | Rules- és kártyaaudit |
| `OQ-RULES-002` | `deferred` | Rules- és kártyaaudit |
| `OQ-RULES-003` | `partly_answered` | Rules- és kártyaaudit |
| `OQ-RULES-004` | `deferred` | Rules- és kártyaaudit |
| `OQ-RULES-005` | `answered` | Rules- és kártyaaudit |
| `OQ-RULES-006` | `answered` | Rules- és kártyaaudit |
| `OQ-RULES-007` | `partly_answered` | Aeternal és Pecsét |

---

## 3. Runtime és réteghatárok

**OQ-ARCH-001 / OQ-ARCH-002 / OQ-ARCH-003**

**Döntési állapot:** `FOUNDATION_GUARDRAIL`

- `Aeterna.Engine` az egyetlen production authoritative rules runtime.
- Godot/GDScript scene/input/UI/animáció/hang/presentation/debug layer.
- Python runtime-package builder, validátor, audit/AI/batch/scenario tooling és referencia/oracle.
- Godot ↔ C# közvetlen in-process kapcsolat; Python headless use case külön külső interfész.
- Két párhuzamos production canonical rules engine nincs.
- Bridge/client nem tartalmaz rules authorityt.

Mindhárom OQ: `answered`.

---

## 4. Dokumentáció

**OQ-DOC-001 / OQ-DOC-002 / OQ-DOC-003**

- Official rules authority DOCX:
  - `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4.3v.docx`
  - `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`
- Engine/project docs aktív formátuma Markdown.
- Nem tartunk kézzel párhuzamos canonical MD + DOCX másolatot ugyanarról a technical tartalomról.
- Reader/export PDF/DOCX csak konkrét publishing/audience use case esetén készül; ez `RESERVED_EXTENSION_POINT`, nem current blocker.
- Egy aktív `ENGINE_CHECKPOINT.md` + történeti `CHECKPOINTS.md`.
- Új dokumentum csak önálló canonical szerep esetén; verzió/dátum/státusz kötelező.
- Cleanup/archive csak ellenőrzött utóddal.

**Státusz:** mindhárom `answered`.

---

## 5. Runtime package, build és provenance

**OQ-DATA-001 / OQ-DATA-002 / OQ-DATA-005 / OQ-DATA-006 / OQ-TECH-004B**

### Current default

- Validált manifestes runtime package a program kötelező statikus adatinputja.
- Godot és production C# nem olvas közvetlenül authoring XLSX-et.
- Python pipeline: export → normalize → validate → diagnostics → candidate package → publish.
- Godot `runtime_package/` consumption copy.
- Full deterministic rebuild = correctness path.
- Cache/delta/incremental build = opcionális performance optimization.
- Fingerprint/hash **nem pusztán optimalizáció**; provenance, package identity, compatibility, integrity, replay/save/bug reproduction és release manifest célja is lehet.
- Runtime package derived/rebuildable; nem human authoring authority.
- Historical/sample package mappák nem canonical források; konkrét cleanup repository-task.

### Reserved/evolúciós rész

- konkrét hash algorithm;
- manifest exact mezők;
- output folder layout;
- incremental caching;
- signing/rollback mechanika.

Ezek változhatnak anélkül, hogy az elvi OQ-k újranyílnának.

**Státusz:** minden felsorolt OQ `answered`.

---

## 6. Diagnostics, support és source correction

**OQ-DATA-003 / OQ-DATA-004 / OQ-DIAG-001 / OQ-DIAG-002 / OQ-DIAG-005 / OQ-AR-007**

### Capability vs coverage

```text
Engine Capability
!=
Content Coverage
```

A production C# executable semantics authority külön kezelendő a package support/coverage
metadata rétegtől.

### Diagnostics

- `severity` és `blocking` külön.
- Development, publish/acceptance és runtime külön strictness profile.
- Publish előtt schema/unknown enum/dangerous alias/visibility/mandatory unsupported tartalom blokkolhat.
- Runtime unsupported requirement: no guessing, no silent fallback, no partial commit; controlled reject/not_executable + safe diagnostic.
- Invariant/internal fault külön kategória.

### Alias/source correction – OQ-DATA-004 current default

- safe alias auto-normalizálható;
- dangerous/ambiguous emberi review;
- derived/runtime output **nem ír automatikusan vissza** a human authoring source-ba;
- correction diagnostic/proposal → explicit human edit vagy explicit migration tool → rebuild/revalidate.

### LOOKUPS

Blocking policy answered; full enum/alias inventory és correction pass audit-task.

**Státusz:** a felsorolt OQ-k `answered`.

---

## 7. Projection és visibility

**OQ-SNAP-001 / OQ-SNAP-003 / OQ-SNAP-004 / OQ-SNAP-006**

### Current default

```text
one authoritative MatchState
→ viewer-specific PlayerSnapshot
→ trusted DebugSnapshot külön
```

- Fair AI player-visible projectiont használ.
- Saját hidden identity csak jogosult viewernek.
- Opponent hidden identity redacted.
- Snapshot current state, nem teljes historical event dump.
- Full event history külön stream/API.
- Optional recent-visible summary/cursor presentation use case lehet.

Future:
- `AIObservation`;
- `SpectatorProjection`;
- `ReplayProjection`

külön projectionként bővíthető; nem kell ugyanazt a DTO-t minden consumerre ráerőltetni.

**Státusz:** `OQ-SNAP-001`, `003`, `004`, `006` answered.

---

## 8. Aeternal és Pecsét

**OQ-SNAP-002 / OQ-ABIL-006 / OQ-RULES-007**

### Official Core már rögzíti

- Aeternal = játékos; nincs HP, nem damage/heal target.
- Kezdő Pecsét-réteg: pakli felső 6 lapja, face-down, a hat Áramlathoz kötve.
- Pecsét állapot: fennáll/feltört; nem HP-alapú.
- Feltörés/felfedés/Surge és védtelen Aeternal elleni direct victory Core szabályai léteznek.

### Active gates

- exact owner/opponent Seal identity visibility;
- snapshot schema;
- combat integration;
- special ward break/prevent/restore effect payload;
- Expansion interaction.

Ezért:
- `OQ-SNAP-002` `partly_answered`;
- `OQ-ABIL-006` `partly_answered`;
- `OQ-RULES-007` `partly_answered`.

A régi általános „Pecsét létrehozása nyitott” megfogalmazás **superseded** a Core source újraolvasása miatt.

---

## 9. Reaction, timing és pending state

**OQ-SNAP-005 / OQ-LA-002 / OQ-AR-005 / OQ-ABIL-004**

### Official reaction foundation

- reaction window esemény és final resolution között;
- nem minden event nyit windowt;
- mindkét játékos eligible esetén non-initiator first;
- pass;
- két egymást követő passz zárja a két-player windowt;
- reaction egymásra épülhet;
- LIFO resolution;
- resolution-time revalidation;
- lezárt event nem nyílik újra visszamenőleg;
- simultaneous-effect default ordering és mandatory/optional trigger semantics official 4.1-ben már definiált.

A korábbi decision-log `multi-trigger ordering` és `optional/mandatory trigger` általános
nyitott gate-je **stale és superseded**.

### Reaction current technical defaults – D1–D5

- public actions: `react`, `pass_priority`;
- engine-issued `reaction_option_id`;
- typed `response_policy_id`;
- authoritative reaction/pending state a `MatchState` része;
- snapshotban a meglévő `pending_decision_summary` bővül viewer-safe reaction adatokkal.

### RC1 current default

Single eligible responder:
- egy opportunity;
- `pass_priority` az ablakot lezárja;
- nincs fake második pass.

### RC2 current default – formálható

Ordinary trigger:

```text
committed event
→ trigger created/discovered immediately
→ pending queued trigger
→ current reaction/effect resolution cycle continues
→ current cycle fully unwinds
→ post-resolution trigger checkpoint
→ queued trigger processing
```

Different-timing trigger batch current default:

```text
chronological FIFO by originating committed-event sequence
```

Same-timing batch: official AETERNA simultaneous ordering.

### Reserved timing extensions

Az RC2 current default tudatosan nem zárja ki:

- `strict_event_window`;
- `reaction_window`;
- `delayed_effect`;
- explicit immediate timing override;
- future `TriggerActivationPolicy`;
- future `TriggerBatchOrderPolicy`.

A Yu-Gi-Oh implicit `when/if` / missed-timing nyelvi szabálya nincs globálisan importálva.
Ha strict timing később szükséges, explicit typed policy legyen.

### Státusz

- `OQ-AR-005`: `answered` – action response + reaction pending authority current default lezárt.
- `OQ-SNAP-005`: `partly_answered` – compound non-reaction pending choices maradnak.
- `OQ-LA-002`: `partly_answered` – prevention/replacement, combat/special timing és komplex nested integration marad.
- `OQ-ABIL-004`: `partly_answered` – prevention/replacement, coverage és special timing integration marad.

---

## 10. Legal action és request authority

**OQ-LA-001 / OQ-LA-006 / OQ-LA-007 / OQ-AR-001 / OQ-AR-002 / OQ-AR-003**

### Current defaults

- legal action kizárólag engine authority;
- player/fair-AI enabled actions; debug structured disabled reason;
- fair AI nem kap hidden legality advantage;
- `expected_state_version` authority guard;
- stale request state-mutation nélkül reject;
- action ID csak current legal-action/state contextben él;
- frontend/AI nem küld authoritative cost/legality döntést.

### OQ-LA-006 explicit anchor

Current rule:
- UI/presentation metadata advisory, nem authority;
- legal action semantic mezők engine-owned;
- localization/presentation hints bővíthetők.

**Active gate:** végleges minimal presentation/UI hint mezők és consumer-specific projection.

### OQ-AR-001 explicit anchor

Current:
- `request_id` correlation része a request contractnak;
- `expected_state_version` kötelező;
- request ID nem azonos automatikusan network idempotency key-jel.

**Active gate:** future online/retry/idempotency exact policy.

### Státusz

- LA-001/LA-007/AR-002/AR-003 `answered`.
- LA-006 és AR-001 `partly_answered`.

---

## 11. Combat

**OQ-LA-003**

Az official 1.4.3 Core már szabályozza:
- attack eligibility;
- attacker Exhaust;
- target declaration;
- Oltalom;
- block;
- simultaneous combat damage;
- Pecsét break;
- Surge;
- unprotected Aeternal direct victory.

Ezért a régi `open` státusz **superseded**.

**Active gate:** production combat action/event/pending-state contract és Reaction-integráció.

**Státusz:** `partly_answered`.

---

## 12. Aura és payment

**OQ-LA-004**

Base current Core:
- Magnitúdó threshold, nem expenditure;
- Aktív Ősforrás Aura;
- payment = selected source Exhaust;
- engine validates ownership/activity/identity/exact cost;
- payment a `play_card` atomikus része;
- no partial mutation on reject.

**Active/future gate:**
- temporary Aura;
- alternate cost;
- modifier;
- wildcard/replacement;
- compound choice.

**Státusz:** `partly_answered`.

Ezeket nem kell előre mind implementálni; future content/Expansion igény aktiválhatja.

---

## 13. Targeting, choice és partial resolution

**OQ-LA-005 / OQ-AR-004 / OQ-AR-006**

Official/current alap:
- simple target requestben lehet;
- complex multi-step authoritative pending state;
- final resolution target/source/condition revalidation;
- ha effect teljesen invalid targetre épül, nincs érdemi resolution;
- önállóan végrehajtható részek a rule/card text szerint kezelendők.

A régi generic `invalid target` / `partial resolution` open gate **szűkítve**.

Active gates:
- retarget;
- cancel/backtracking;
- option invalidation;
- auto-collapse;
- nested target/payment;
- prevention/replacement;
- complex card-specific partial semantics.

Mindhárom `partly_answered`.

---

## 14. Event, replay és balance event

**OQ-EVENT-001…006**

### Current event architecture

- snapshot = current projected state;
- event stream = transition/history;
- typed deterministic internal canonical events;
- one internal history → viewer-specific event projection;
- fair AI player-visible event projectiont kap;
- diagnostics/log/trace külön réteg;
- optional correlation IDs csak tényleges use case esetén.

### Event presentation

Canonical event semantic data; localization/explanation külön presentation projection.

### Current statuses

- `OQ-EVENT-001` answered – taxonomy evolúciós.
- `OQ-EVENT-002` answered – semantic event != presentation sentence.
- `OQ-EVENT-003` answered – event vs diagnostic boundary.
- `OQ-EVENT-004` answered – hidden-info viewer projection current default.
- `OQ-EVENT-005` deferred – full replay runner későbbi.
- `OQ-EVENT-006` deferred – balance-event/report needs stable gameplay/AI.

---

## 15. Diagnostics output

**OQ-DIAG-003 / OQ-DIAG-004 / OQ-DIAG-006 / OQ-DIAG-007**

- machine-primary diagnostics: JSON/JSONL structured;
- human summary: Markdown/text;
- player/public safe diagnostic külön;
- trusted developer detail külön;
- hidden information protection kötelező;
- checkpoint summary, full report külön artifact;
- balance suspicion nem gameplay event és nem automatikus rules change.

Státusz:
- DIAG-003 `answered`
- DIAG-004 `answered`
- DIAG-006 `deferred`
- DIAG-007 `answered`

---

## 16. Ability/effect rendszer

**OQ-ABIL-001 / 002 / 003 / 005 / 007 / 008**

### Current model

```text
structured canonical ability/effect graph
→ compiled typed template/executor
→ rare explicit typed exception_module
→ unsupported/fail-closed
```

- Kártyaszöveg emberi rules text.
- Effect tag metadata/classification, nem executable semantics.
- Structured field csak repeated semantic/runtime/validation/test need esetén.
- Nincs kötelező universal persisted `AbilityExecutionPlan`.
- `CanonicalAbilityGraph` + runtime context + szükség esetén ephemeral typed plan.
- Silent fallback tilos.
- Ritka explicit typed `exception_module` production-supported lehet azonos safety contracttal.
- Ability registry/definition, EngineCapability és ContentCoverage külön layer.
- Package support metadata nem írja felül a production C# executable authorityt.

### Státusz

- ABIL-001 answered
- ABIL-002 answered
- ABIL-003 answered – korábbi „csak átmeneti card-local fallback” megfogalmazást a typed exception-module current default **supersede-eli**
- ABIL-005 partly_answered – concrete keyword support priority content/gameplay függő
- ABIL-007 answered
- ABIL-008 answered

---

## 17. Technológia, acceptance és product runtime

**OQ-TECH-001…006**

- TECH-001 answered – Python external tooling/reference.
- TECH-002 answered – Godot/GDScript visual layer.
- TECH-003 answered – Godot+C#+Python hybrid, one authority.
- TECH-004 answered – runtime package static boundary.
- TECH-005 answered current default:
  - canonical local acceptance pipeline first;
  - build/tests/determinism/package/bridge/client/smoke ugyanabban a proofban;
  - CI később ugyanennek automation hostja;
  - export/signing/installer külön release maturity.
- TECH-006 answered – minimal Codex policy.

### Korábbi orphan „Termékruntime-döntések” áthelyezése

Ezek most **OQ-TECH-005 release/product runtime current-default** alatt élnek:

- primary desktop target: 64-bit Windows 10+;
- proof/closed test portable folder elfogadható;
- normal runhoz ne kelljen admin, Python, Godot Editor, .NET SDK;
- kevés ismert runtime prerequisite elfogadható;
- saves/logs/settings user-writable helyre;
- Linux/signing/installer/log-retention későbbi;
- packaging proof hiánya nem nyitja újra a C# authority döntést.

Így nincs OQ-ID nélküli orphan decision block.

---

## 18. AI, simulation és balance

**OQ-AI-001…007**

Current guardrails:
- Python koordinál C# headless futásokat;
- AI legal actionből választ;
- fair AI player-visible observation;
- trusted/debug AI explicit külön capability;
- AI policy verziózott és nem rules authority;
- balance suspicion több metrikából;
- nem cél steril minden-matchup 50/50;
- faction/clan identity és meta számít;
- AI nem módosíthat szabályt/adatot.

Státusz:
- AI-001/002/003 `answered`;
- AI-004/005 `partly_answered` – konkrét metrikák/küszöbök playtest/AI/meta után;
- AI-006/007 `deferred`.

---

## 19. Rules- és kártyaaudit

**OQ-RULES-001…006**

- Official main source audit szükséges és rétegezett.
- LOOKUPS/structured critical audit külön korai lépcső.
- Motor nem találgathat text/structured mismatchnél.
- Derived/runtime nem ír silent módon vissza human authorityba.
- Runtime-supported csak auditált konzisztens tartalomnál.
- Engine/AI-friendly derived rules spec szükséges, de exact schema/authoring/version-sync még aktív kérdés.
- Player-friendly rulebook későbbi, stabil gameplay után.
- Full card audit feltételekhez kötött későbbi mérföldkő.

Text/structured mismatch current flow:

```text
authority source
→ structured comparison
→ diagnostic/block
→ explicit human correction
→ rebuild
→ revalidation
```

Státusz:
- RULES-001 answered
- RULES-002 deferred
- RULES-003 partly_answered
- RULES-004 deferred
- RULES-005 answered
- RULES-006 answered

---

## 20. Historical CQ-INFLOW decision IDs

A `CQ-INFLOW-001…006` történeti decision IDs továbbra is megmaradnak, nem kapnak
párhuzamos OQ-ID-t.

Canonical technical mapping:
- phase `infusion`;
- public actions `normal_inflow`, `advance_phase`;
- no separate `skip_inflow`;
- max 1 normal inflow per turn;
- hand → Wellspring, face-down + active;
- same turn usable;
- phase stays `infusion` until explicit `advance_phase`.

A régi `perform_inflow` / `skip_inflow` tri-state technikai contract történeti előzmény.

---

## 21. Aktív nyitott döntési kapuk összefoglalása

A 17 `partly_answered` OQ:

```text
OQ-SNAP-002
OQ-SNAP-005
OQ-LA-002
OQ-LA-003
OQ-LA-004
OQ-LA-005
OQ-LA-006
OQ-AR-001
OQ-AR-004
OQ-AR-006
OQ-ABIL-004
OQ-ABIL-005
OQ-ABIL-006
OQ-AI-004
OQ-AI-005
OQ-RULES-003
OQ-RULES-007
```

A 7 `deferred`:

```text
OQ-EVENT-005
OQ-EVENT-006
OQ-DIAG-006
OQ-AI-006
OQ-AI-007
OQ-RULES-002
OQ-RULES-004
```

`open`: 0.

---

## 22. Változásnapló

### 2.2 – 2026-08-15

- Az OQ-regiszterrel együtt teljes páros consistency review.
- Minden 74 OQ explicit decision coverage indexet kapott.
- Három korábban hiányzó explicit anchor rendezve: `OQ-LA-003`, `OQ-LA-006`, `OQ-AR-001`.
- Reaction stale multi-trigger/mandatory-optional gate eltávolítva az official 4.1 alapján.
- Target/partial-resolution stale gate szűkítve.
- Pecsét Core creation/state scope pontosítva.
- Data build/fingerprint policy pontosítva.
- Derived→human source automatic backwrite tiltás current defaultként rögzítve.
- Typed exception-module current default rögzítve; silent fallback továbbra is tiltott.
- Reaction D1–D5, RC1 és formálható RC2 default adminisztrálva.
- RC2 strict timing/missed timing future explicit extension pointként fenntartva.
- Event/projection/diagnostic current defaults lezárva.
- Product runtime orphan blokk TECH-005 alá visszakötve.
- `answered` fogalom current-default jelentése és superseding/evolving-design elv bevezetve.
- Új státuszösszesítés: 50 answered / 17 partly_answered / 7 deferred / 0 open.

A 2.1 tartalma és korábbi indoklásai a Git-történetben megmaradnak.
