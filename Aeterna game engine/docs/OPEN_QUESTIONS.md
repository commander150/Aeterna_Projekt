# AETERNA Game Engine – Open Questions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.2  
**Dátum:** 2026-08-15  
**Státusz:** review draft – A0–A4 páros OQ-audit és a rugalmas current-default tervezési elv szerint újraszinkronizálva  
**Kapcsolódó válasznapló:** `OPEN_QUESTIONS_DECISIONS.md`  
**Dokumentációs remote bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96` – `docs: align active documentation with explicit phase foundation`  
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

Ez a fájl az AETERNA Game Engine 74 OQ-tételének központi kérdés- és döntésikapu-regisztere.

A részletes döntések, superseding/extension információk és indoklások az
`OPEN_QUESTIONS_DECISIONS.md` fájlban maradnak.

## 1. Státuszok

| Státusz | Jelentés |
|---|---|
| `open` | Aktív scope-ban nincs még használható döntés vagy elégséges bizonyíték. |
| `partly_answered` | Van current default/alapirány, de az aktív fejlesztéshez tényleges döntési kapu maradt. |
| `deferred` | Valós kérdés, de a jó döntéshez későbbi mérföldkő, playtest, meta, content vagy más bizonyíték szükséges. |
| `answered` | Van visszakereshető current canonical/default válasz. Ez nem jelenti, hogy a döntés örökre megváltoztathatatlan. |

## 2. Döntési állapotok és rugalmasság

Az OQ-státusz és a döntés permanenciája nem ugyanaz.

Használt döntési állapotok:

- `FOUNDATION_GUARDRAIL` – nagy stabilitásra tervezett alapelv; csak explicit redesign/impact/migration/audit útvonalon módosítandó.
- `CURRENT_CANONICAL_DEFAULT` – a jelenlegi ruleset/engine elfogadott működése; későbbi explicit döntéssel bővíthető vagy supersede-elhető.
- `CURRENT_DEFAULT + ACTIVE_GATE` – jelentős rész eldőlt, de current scope-ban még konkrét döntési kapu maradt.
- `DEFERRED_BY_EVIDENCE` – a jó döntéshez későbbi gameplay/playtest/meta/content bizonyíték kell.
- `RESERVED_EXTENSION_POINT` – jövőbeli bővítési hely; önmagában nem tart egy OQ-t nyitva, ha a current default elegendő.

A projekt célja nem egy örökre lefagyasztott architektúra, hanem:

```text
világos current canonical state
+ tesztelhetőség
+ visszakövethető döntéstörténet
+ kontrollált újratervezhetőség
```

Playtest, Expansion, meta vagy bizonyított design hiba indokolhat akár mély alapváltoztatást is.
Ilyenkor a régi döntés nem tűnik el: `EXTENDED`, `SCOPED`, `SUPERSEDED` vagy `REPLACED`
kapcsolattal történetileg megmarad.

## 3. Összesítés

- `open`: 0
- `partly_answered`: 17
- `deferred`: 7
- `answered`: 50
- összes OQ: 74

## 4. Használati szabály

1. Új kérdés csak egyedi OQ-azonosítóval vehető fel.
2. Minden OQ-nak legyen egyértelmű visszakereshető decision anchorja a válasznaplóban.
3. `answered` akkor adható, ha a **current scope számára** egyértelmű válasz van; future extension önmagában nem ok a `partly_answered` fenntartására.
4. Implementációs, audit-, migration- vagy cleanup-hiány nem nyitja újra automatikusan az eldöntött elvi kérdést.
5. Reserved extension point nem egyenlő aktív döntési kapuval.
6. Új playtest/meta/Expansion bizonyíték explicit review-t indíthat.
7. Canonical döntést csak explicit, verziózott emberi döntés módosíthat.
8. Ha egy korábbi döntés változik, az új döntés jelölje a kapcsolatot (`extends`, `supersedes`, `scopes`, `replaces`).
9. A végső dokumentumaudit során minden OQ-hivatkozást, célfájlt és státuszösszesítést ellenőrizni kell.

---

## 1. Projektirány és architektúra

### OQ-ARCH-001 – Régi és új Python motor szerepe

**Státusz:** `answered`  
**Döntési állapot:** `FOUNDATION_GUARDRAIL`  
**Aktuális válasz / fennmaradó kapu:** Production authority C#/.NET; Python referencia-, adat-, audit-, AI- és batch-tooling. Legacy motorból csak célzott, auditált logika emelhető át.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ARCH-001`

### OQ-ARCH-002 – Runtime nyelv és integrációs modell

**Státusz:** `answered`  
**Döntési állapot:** `FOUNDATION_GUARDRAIL`  
**Aktuális válasz / fennmaradó kapu:** Godot/GDScript vizuális kliens; C# az egyetlen authoritative runtime; Python külső tooling. Párhuzamos canonical motor nincs.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ARCH-002`

### OQ-ARCH-003 – UI és rules engine szétválasztása

**Státusz:** `answered`  
**Döntési állapot:** `FOUNDATION_GUARDRAIL`  
**Aktuális válasz / fennmaradó kapu:** A UI requestet küld; a C# engine validál és mutál. A bridge/presentation réteg nem tartalmaz rules authorityt.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ARCH-003`

## 2. Dokumentáció és fájlstátusz

### OQ-DOC-001 – DOCX → Markdown migráció

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Current default: official rules authority DOCX, engine/project docs Markdown. Külön reader/export DOCX/PDF csak konkrét publishing/use case esetén; nem tartunk kézzel párhuzamos canonical másolatokat.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DOC-001`

### OQ-DOC-002 – Checkpointok kezelése

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Egy aktív `ENGINE_CHECKPOINT.md` és külön történeti `CHECKPOINTS.md` modell.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DOC-002`

### OQ-DOC-003 – Dokumentumszaporodás elkerülése

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Elsődlegesen meglévő aktív dokumentum frissül; új canonical dokumentum csak önálló szerep esetén. Verzió/dátum/státusz kötelező.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DOC-003`

## 3. Runtime package és adatút

### OQ-DATA-001 – Compiled runtime package szükségessége

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** A validált manifestes runtime package kötelező statikus programadat; nyers export köztes/audit output.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-001`

### OQ-DATA-002 – Google Sheets → XLSX → runtime package adatút

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Current default: derived, validált, verziózott, rebuildelhető és fingerprintelt runtime package; release manifest/provenance külön réteg. Konkrét layout/hash algoritmus evolúciós.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-002`

### OQ-DATA-003 – Engine support státusz és blokkolás

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Engine capability és konkrét content coverage külön fogalom; unsupported/fail-closed és publish gate elve lezárt. A checker/coverage tooling implementációs feladat.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-003`

### OQ-DATA-004 – Legacy alias és canonical értékek

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Safe alias normalizálható; dangerous/ambiguous emberi review. Derived/runtime output nem ír automatikusan vissza a human authoring source-ba; korrekció explicit human edit vagy kontrollált migration.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-004`

### OQ-TECH-004B – Python build pipeline hosszú távú szerepe

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Python marad export/normalizálás/validáció/package build/diagnostics/fixture/AI/batch tooling.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-004B`

### OQ-DATA-005 – Build pipeline és változásérzékelés

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Full deterministic rebuild a correctness path; cache/delta/incremental optimalizáció. Fingerprint/hash provenance, identity, compatibility és reprodukálhatóság célra is használható.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-005`

### OQ-DATA-006 – Duplikált sample/runtime package mappák

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Historical/sample package nem authority; Godot `runtime_package/` consumption copy. Maradék archive/delete cleanup repository-task.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-006`

## 4. Snapshot és visibility

### OQ-SNAP-001 – Snapshot típusok

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Current contract: viewer-specifikus `PlayerSnapshot` + trusted `DebugSnapshot`. AI/spectator/replay külön projection lehet később.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-001`

### OQ-SNAP-002 – Pecsétmodell snapshotban

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Official Core már meghatározza a 6 face-down Pecsétet, Áramlat-kapcsolatot és fennáll/feltört állapotot. Nyitott: exact owner/opponent visibility és digitális snapshot schema.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-002`

### OQ-SNAP-003 – Ősforrás láthatóság és állapot

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Magnitúdó és Aktív/Kimerült forrásállapot publikus; saját forrásidentity owner-visible, ellenfélnek redacted.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-003`

### OQ-SNAP-004 – Rejtett információ és visibility

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Egy authoritative stateből viewer-specifikus projection készül; hidden information nem kerülhet player/fair-AI outputba. Spectator/replay új consumerként bővíthető.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-004`

### OQ-SNAP-005 – Pending decision és döntési ablak

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Reaction pending state iránya kialakult. Nyitott: compound target/payment/choice, cancel/back, combat és nested nem-reaction decision pontos schema/projection.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-005`

### OQ-SNAP-006 – Event log a snapshotban

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Snapshot=current projected state; teljes canonical event history külön stream/API. Recent visible summary/cursor opcionális presentation részlet.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-006`

## 5. Legal actions

### OQ-LA-001 – Enabled és disabled actionök

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Player/fair-AI nézet enabled actionöket kap; debug structured disabled-reason adatot is kaphat.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-001`

### OQ-LA-002 – Reakcióablak modell

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Official reaction alap, pass/LIFO/ordering és current RC1/RC2 default rögzített. Nyitott: prevention/replacement, complex nested choice, combat timing/integration és future explicit special timing policyk.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-002`

### OQ-LA-003 – Combat actionök

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Official Core már rögzíti attack/target/block/simultaneous damage/Pecsét/Aeternal alapot. Nyitott: production combat action/event/pending-state contract.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-003`

### OQ-LA-004 – Fizetés és Aura

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Base Magnitúdó/Aura payment production foundation megvan. Nyitott: temporary Aura, alternate/modifier/wildcard/replacement és compound payment choice.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-004`

### OQ-LA-005 – Targeting

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Basic target validation/revalidation és partial-resolution alap official. Nyitott: retarget, complex multi-step choice és card-specific complex semantics.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-005`

### OQ-LA-006 – UI mezők a legal actionben

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Engine authority és UI non-authority elv adott. Nyitott: végleges minimal UI hint/localization/presentation mezők és a külön consumer contract pontosítása.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-006`

### OQ-LA-007 – AI legal action mezők

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Fair AI ugyanazt az authoritative legal action surface-t használja, rejtett legalitási előny nélkül.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-007`

## 6. Action request és response

### OQ-AR-001 – Request azonosítás

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** `request_id` és `expected_state_version` current request contract része. Nyitott: future network idempotency/retry/correlation exact semantics.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-001`

### OQ-AR-002 – Snapshot frissesség és state_version

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** `state_version` authority guard; stale request state-mutation nélkül reject.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-002`

### OQ-AR-003 – Action ID élettartama

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Action ID csak az adott legal-action/state-version kontextusban érvényes.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-003`

### OQ-AR-004 – Többlépcsős targeting és pending állapot

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Authoritative pending state és engine-generated option elv adott. Nyitott: cancel/backtracking, invalidation, auto-collapse és nested choice semantics.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-004`

### OQ-AR-005 – Action response és reakcióablak

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Current default: submit→canonical transition→viewer-safe snapshot/events; Reaction esetén engine-owned pending state és `react`/`pass_priority` legal actions. Future transport nem változtatja ezt az authority-határt.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-005`

### OQ-AR-006 – Partial resolution státuszok

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Basic invalid-target/partial-resolution elv official. Nyitott: prevention/replacement/cancel és complex multi-part exact response semantics.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-006`

### OQ-AR-007 – Unsupported feature action közben

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Unsupported canonical requirement: no guess/no silent fallback/no partial commit; controlled reject/block + safe diagnostic. Code coverage tooling task.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-007`

## 7. Event log

### OQ-EVENT-001 – Event részletesség

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Typed deterministic canonical events, külön debug/system réteggel. Taxonomy és opcionális correlation mezők evolúciósak.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-001`

### OQ-EVENT-002 – Explanation log

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Canonical event semantic adat, nem presentation sentence; UI localization key+params/fallback külön projection/presentation réteg.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-002`

### OQ-EVENT-003 – Debug, audit és diagnostics kapcsolat

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Gameplay `EngineEvent` és diagnostic/log/trace külön fogalom; szükség esetén explicit correlation.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-003`

### OQ-EVENT-004 – Rejtett információ event logban

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Egy belső canonical event historyból viewer-specific redacted projection készül; hidden event-existence eset future explicit policyvel bővíthető.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-004`

### OQ-EVENT-005 – Replay-kompatibilitás

**Státusz:** `deferred`  
**Döntési állapot:** `DEFERRED_BY_EVIDENCE`  
**Aktuális válasz / fennmaradó kapu:** Replay architecture későbbi mérföldkő; current event/state identity ezt előkészíti, de teljes replay runner nem current blocker.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-005`

### OQ-EVENT-006 – Balance test eventek

**Státusz:** `deferred`  
**Döntési állapot:** `DEFERRED_BY_EVIDENCE`  
**Aktuális válasz / fennmaradó kapu:** Balance-specifikus event/report igény stabil gameplay és AI után döntendő.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-006`

## 8. Diagnostics

### OQ-DIAG-001 – Severity és blocking

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Severity és blocking külön mező/policy; `critical` alapból blocking, balance suspicion nem engine-hiba.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-001`

### OQ-DIAG-002 – Blocking szabályok futási módonként

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Development, publish/acceptance és runtime külön strictness profile; konkrét code-by-code matrix bővíthető.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-002`

### OQ-DIAG-003 – Diagnostics report formátum

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Machine-primary structured JSON/JSONL diagnostics + human Markdown/text summary; konkrét artifact layout evolúciós.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-003`

### OQ-DIAG-004 – Runtime visibility

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Public-safe diagnostic és trusted developer diagnostic külön projection; production UI nem kap automatikusan belső részletet.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-004`

### OQ-DIAG-005 – LOOKUPS diagnostics

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** LOOKUPS blocking/alias policy lezárt; teljes enum/alias inventory és javítás audit-task.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-005`

### OQ-DIAG-006 – Balance suspicion

**Státusz:** `deferred`  
**Döntési állapot:** `DEFERRED_BY_EVIDENCE`  
**Aktuális válasz / fennmaradó kapu:** Balance suspicion metrikák/statisztikai policy stabil gameplay/AI után.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-006`

### OQ-DIAG-007 – Diagnostics és checkpointok kapcsolata

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Checkpoint összesítést és lényeges problémát tartalmaz; teljes diagnostic dump külön report.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-007`

## 9. Ability module rendszer

### OQ-ABIL-001 – Structured mezők részletessége

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Structured mező csak ismétlődő semantic/runtime/validation/test igény esetén bővül. Nem minden kártyaszöveghez új oszlop.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-001`

### OQ-ABIL-002 – Execution plan

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Current default: `CanonicalAbilityGraph` + runtime `ResolutionContext` + szükség esetén ephemeral typed execution/transition plan; nincs kötelező persisted univerzális execution-plan artifact.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-002`

### OQ-ABIL-003 – Card-local fallback

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Silent fallback tilos. Ritka explicit typed `exception_module` production-supported lehet azonos validation/atomicity/event/projection/test contracttal.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-003`

### OQ-ABIL-004 – Reaction system ability szinten

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Reaction ability-hook nem timing authority. Current default trigger/reaction processing rögzített; nyitott: prevention/replacement, complex nested choice, combat/special timing és coverage.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-004`

### OQ-ABIL-005 – Keywordök MVP-támogatása

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Keyword registry/support policy szükséges; konkrét támogatási sorrend Base card coverage és gameplay priority függő.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-005`

### OQ-ABIL-006 – Pecsét/Aeternal targetek

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Aeternal/Pecsét no-HP és Core target/combat szabály jelentős része official. Nyitott: exact special effect/event payload és future interaction contract.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-006`

### OQ-ABIL-007 – Hatáscímkék szerepe

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Effect tag metadata/classification, nem executable semantics. Mapping/migration/coverage task.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-007`

### OQ-ABIL-008 – Ability registry és runtime package

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Ability definition/registry, engine capability és content coverage külön réteg; package metadata nem írja felül a C# executable authorityt.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-008`

## 10. Technológiai döntések

### OQ-TECH-001 – Python hosszú távú szerepe

**Státusz:** `answered`  
**Döntési állapot:** `FOUNDATION_GUARDRAIL`  
**Aktuális válasz / fennmaradó kapu:** Python external tooling/reference szerep canonical.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-001`

### OQ-TECH-002 – GDScript/Godot runtime alkalmassága

**Státusz:** `answered`  
**Döntési állapot:** `FOUNDATION_GUARDRAIL`  
**Aktuális válasz / fennmaradó kapu:** Godot/GDScript visual/client layer canonical; nem rules authority.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-002`

### OQ-TECH-003 – Python + GDScript/C# hibrid modell

**Státusz:** `answered`  
**Döntési állapot:** `FOUNDATION_GUARDRAIL`  
**Aktuális válasz / fennmaradó kapu:** Godot + C# + Python hibrid, egyetlen C# authority.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-003`

### OQ-TECH-004 – Runtime package mint technológiai határ

**Státusz:** `answered`  
**Döntési állapot:** `FOUNDATION_GUARDRAIL`  
**Aktuális válasz / fennmaradó kapu:** Runtime package statikus technológiai adatboundary.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-004`

### OQ-TECH-005 – Godot headless/smoke stratégia

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Current default: canonical local acceptance runner/pipeline először; CI később ugyanennek automation hostja. Export/signing/installer külön release maturity.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-005`

### OQ-TECH-006 – Codex-feladatok bontása

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Codex csak szükséges implementation/execution vagy GitHubról nem látható local worktree feladatra; rules/project/document döntés nem Codex authority.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-006`

## 11. AI, simulation és balance

### OQ-AI-001 – AI-vs-AI helye

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Python koordinálhat C# headless AI-vs-AI futásokat; C# marad authority.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-001`

### OQ-AI-002 – Fair AI és debug AI

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Fair AI player-visible observationt használ; trusted/debug analyzer külön explicit capability.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-002`

### OQ-AI-003 – AI heurisztika és legal actions

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** AI csak engine legal actionsből választ; heuristic/policy külön verziózott layer.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-003`

### OQ-AI-004 – Balance suspicion forrása

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Elv: balance suspicion több metrikából, nem puszta winrateből. Nyitott: konkrét metrikák/küszöbök/sample size stabil gameplay és adatok után.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-004`

### OQ-AI-005 – Winrate és klánidentitás

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Nem cél steril 50/50; klánidentitás és matchup/meta distribution számít. Nyitott: elfogadható sávok emberi playtest/AI/meta alapján.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-005`

### OQ-AI-006 – Balance report

**Státusz:** `deferred`  
**Döntési állapot:** `DEFERRED_BY_EVIDENCE`  
**Aktuális válasz / fennmaradó kapu:** Balance report teljes contractja stabil AI/gameplay után.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-006`

### OQ-AI-007 – Korábbi kártyajavítások visszaellenőrzése

**Státusz:** `deferred`  
**Döntési állapot:** `DEFERRED_BY_EVIDENCE`  
**Aktuális válasz / fennmaradó kapu:** Korábbi kártyajavítások teljes visszaellenőrzése későbbi full audit/fair-AI szakasz.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-007`

## 12. Rules- és kártyaaudit

### OQ-RULES-001 – Hivatalos főforrás-audit

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Official main-source audit szükséges, rétegezett authority-preserving workflowval. Fennmaradó audit végrehajtási workstream.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-001`

### OQ-RULES-002 – Játékosbarát szabálykönyv

**Státusz:** `deferred`  
**Döntési állapot:** `DEFERRED_BY_EVIDENCE`  
**Aktuális válasz / fennmaradó kapu:** Játékosbarát rulebook stabil szabály/gameplay után.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-002`

### OQ-RULES-003 – Engine/AI-barát szabályspecifikáció

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Külön engine/AI-friendly derived rules spec szükséges. Nyitott: tényleges schema/authoring/version-sync modell.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-003`

### OQ-RULES-004 – Új teljes kártyaaudit időzítése

**Státusz:** `deferred`  
**Döntési állapot:** `DEFERRED_BY_EVIDENCE`  
**Aktuális válasz / fennmaradó kapu:** Új teljes card audit feltételekhez kötött későbbi mérföldkő.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-004`

### OQ-RULES-005 – LOOKUPS és structured audit

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** LOOKUPS/structured critical audit korai külön lépcső; teljes worklist végrehajtási feladat.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-005`

### OQ-RULES-006 – Kártyaszöveg és structured eltérés

**Státusz:** `answered`  
**Döntési állapot:** `CURRENT_CANONICAL_DEFAULT`  
**Aktuális válasz / fennmaradó kapu:** Text/structured mismatchnél engine nem találgat; diagnostic/block + explicit human correction + rebuild/revalidation. Nincs silent derived→human backwrite.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-006`

### OQ-RULES-007 – Aeternal/Pecsét engine-spec

**Státusz:** `partly_answered`  
**Döntési állapot:** `CURRENT_DEFAULT + ACTIVE_GATE`  
**Aktuális válasz / fennmaradó kapu:** Official Core jelentős Aeternal/Pecsét szabályt ad. Nyitott: combat integration, special break/restore, snapshot/event/action payload és Expansion-interakciók.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-007`


---

## 13. Változásnapló

### 2.2 – 2026-08-15

- A `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` páros Stage-1/Stage-2 auditja alapján újraszinkronizálva.
- A0: stale official-rules gate-ek szűkítve; `OQ-SNAP-002` és `OQ-LA-003` `open` → `partly_answered`.
- A1: öt elvi kérdés `answered`, a maradék munka task/audit rétegbe választva.
- A2: data/ability current defaults, Reaction D1–D5, RC1 és formálható RC2 current-default irány rögzítve.
- RC2: ordinary trigger default immediate discovery + post-resolution processing; different-timing batch default FIFO; future strict timing reserved extension.
- A3: projection/event/diagnostics/package témák jelentős része current-default szinten lezárva.
- A4: structured ability, registry és text/structured mismatch current-default lezárva; balance/playtest/content kérdések tudatosan nyitva/deferred állapotban maradnak.
- Új rugalmassági elv: `answered` nem jelent örök változtathatatlanságot.
- Repository-bázis mező kettéválasztva dokumentációs remote bázisra és production engine mérföldkőre.
- Új összesítés: 50 answered / 17 partly_answered / 7 deferred / 0 open.

A 2.1 és korábbi verziók történeti tartalma a Git-történetben megmarad.
