---
artifact_id: AET-DOC-PROJECT-PLAN
kind: document
type: project-plan
version: "6.16"
lifecycle: active
integration: current
authority: project-direction
generated: false
depends_on: []
supersedes: []
---

# AETERNA – AKTUÁLIS PROJEKTTERV ÉS PRIORITÁSOK v6.16

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 6.16
**Dátum:** 2026-10-09
**Státusz:** aktív projektirányító és prioritási dokumentum
**Előző aktív verzió:** 6.15 (Git history)
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9` – `engine: add aeternal outcome and terminal match result`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9` – Combat + Pecsét Foundation C0–C6
**Előző technikai checkpoint-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`

Ez a dokumentum az AETERNA projekt aktuális irányát, prioritásait, dokumentumelsőbbségét és a következő biztonságos munkaszakaszokat rögzíti.

Nem teljes repository-inventár, nem szabálykönyv, nem contract-specifikáció és nem Codex-prompt.

---

## 1. Dokumentum- és tényelsőbbség

### 1.1 Játékszabályi kérdésben

Elsődleges authority:

1. `rules/sources/OFFICIAL_BASE_GAME_RULES_SOURCE.docx`;
2. `rules/sources/OFFICIAL_EXPANSION_RULES_SOURCE.docx`;
3. explicit, verziózott emberi döntés, ha nem mond ellent a hivatalos forrásnak;
4. aktív Open Questions döntésnapló;
5. aktív engine-contract és specification;
6. működő implementáció és teszt mint technikai bizonyíték.

A kód, tanulóprojekt, régi dokumentum vagy runtime package nem írhatja felül a hivatalos játékszabályt.

### 1.2 Tényleges implementációs állapotban

Ha aktív státuszdokumentum és Git-történet eltér:

- az aktuális `main` története;
- az aktuális production C# kód;
- és a hozzá tartozó sikeres tesztbizonyíték

írja le a ténylegesen megvalósult technikai állapotot.

Régi checkpoint vagy státuszdokumentum nem írhatja felül a későbbi implementációt.

### 1.3 Projektprioritásban

Aktív irányító réteg:

1. jelen projektterv;
2. `project/status/checkpoints/ENGINE_CHECKPOINT.md`;
3. `project/status/PROJECT_MAP_FILE_STATUS.md`;
4. közvetlenül érintett aktív engine-státusz- és contractdokumentumok.

---

## 2. Elfogadott digitális architektúra

Az architektúradöntés változatlan:

- **Godot / GDScript:** vizuális kliens, UI, input, animáció és debug;
- **C# / .NET:** az egyetlen production authoritative rules engine;
- **Python:** adat-, export-, audit-, fixture-, AI-, batch-, reference- és elemzőtooling.

Kötelező elvek:

- egy meccsnek egy authoritative state-je van;
- state mutation csak validált C# engine transition útján történhet;
- a frontend és az AI nem találgathat legalitást;
- player-facing és debug projection külön marad;
- rejtett információt viewer-specifikus projection véd;
- determinisztikus, auditálható event- és transition-modell szükséges;
- a Python reference nem második production authority.

---

### 2.1 Evolving-design / kontrollált felülvizsgálat

A `project/decisions/DECISION_MAP.md` helyreállított governance-elve alapján:

- az elfogadott szabály vagy döntés az aktuális rulesetben canonical/current default;
- playtest, Expansion, meta vagy bizonyított design/architecture probléma indokolhat felülvizsgálatot;
- új bizonyíték nem módosít automatikusan szabályt;
- változtatás explicit emberi döntéssel, hatásvizsgálattal és szükség esetén migration/regression úton történik;
- a korábbi döntés és a módosítás indoka visszakereshető marad.

Használt változási kapcsolat: `EXTENDED / SCOPED / SUPERSEDED / REPLACED`.

## 3. A `931bf... → 2608345b...` production mérföldkő

A korábbi C.5B foundation checkpoint óta a `main` 39 committal haladt előre.

### 3.1 Hivatalos forrás- és adatváltozás

Megvalósult:

- az alapjáték hivatalos főforrása `1.4v` helyett `1.4.3v`;
- `CARDDATABASE.xlsx` és `REGISTRY.xlsx` canonical adatforrásként bekerült;
- a kártyaadatbázis munkaforrás és canonical workbook-export út frissült.

### 3.2 Production gameplay foundation

Megvalósult és tesztelt production C# rétegek:

- Wellspring / Ősforrás state és player-visible projection;
- normál Beáramlás (`normal_inflow`) és egyszer-per-kör állapot;
- Magnitúdó-preflight;
- Aura-payment preflight és forrásválasztás;
- activity state mutation;
- Domain state és placement;
- `play_card`;
- canonical zónatranzíciók;
- Void-kezelés;
- canonical card catalog és runtime binding.

### 3.3 Canonical ability és effect runtime

Megvalósult production foundation:

- canonical ability catalog;
- ability-template compiler;
- condition evaluator;
- target filter és target resolver;
- trigger resolver;
- effect executor;
- template / collection / zone effect runtime;
- continuous effect state;
- modifier / keyword / duration runtime;
- damage és vitals lifecycle;
- lethal transitionök;
- canonical draw/reference runtime.

Ez nem jelenti azt, hogy az összes AETERNA-kártya minden képessége teljes körűen támogatott.

### 3.4 Explicit Phase Foundation v1

Lezáró commit:

`2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

Production canonical fázisok:

1. `awakening` – Ébredés;
2. `infusion` – Beáramlás;
3. `manifestation` – Manifesztáció;
4. `incursion` – Betörés;
5. `distribution` – Eloszlás.

Megvalósult:

- authoritative öt-fázisú state machine;
- public `advance_phase`;
- phase-specifikus legal action tér;
- explicit `StartingPlayerId`;
- első kezdőjátékosi Awakening 0 húzás;
- későbbi Awakening: ready + 2 húzás;
- kötelező húzás atomikus hibakezelése;
- `incursion -> distribution` cleanup boundary;
- `distribution -> awakening` játékosváltás;
- public `draw_card` és `end_turn` kivonása a normál production action space-ből;
- viewer-safe `ActionResponse.Events`;
- internal full-fidelity event store megőrzése;
- Godot production bridge canonical phase flow-ra átvezetése.

Legutóbbi lezáró acceptance:

- Engine Debug build: PASS;
- Engine Release build: PASS;
- Debug tesztek: `222/222 PASS`;
- Release tesztek: `222/222 PASS`;
- headless oracle/reference: PASS;
- determinisztika: `100/100 PASS`;
- Godot C# build: PASS;
- pozitív Godot smoke: PASS;
- negatív Godot smoke: PASS;
- `git diff --check`: PASS.

---

## 4. Aktuális production státusz

### COMPLETE / ACTIVE

- runtime package és publish foundation;
- C# authoritative engine foundation;
- Wellspring / Beáramlás / payment foundation;
- Domain és `play_card`;
- canonical card/runtime binding;
- canonical ability/effect execution foundation;
- damage/vitals;
- continuous effects;
- modifier/keyword/duration foundation;
- draw/reference runtime;
- explicit öt-fázisú turn lifecycle;
- Reaction / Priority Foundation v1;
- shared `resolution` lifecycle;
- canonical setup + Jóslat;
- hat stabil Pecsét-slot és viewer-safe visibility;
- `attack` / AttackCommit;
- intervention / DefenseCommit;
- két Combat ReactionWindow;
- Entity Combat és simultaneous damage;
- SealBreak / reveal / Surge;
- Gondviselés Surge opportunity;
- Aeternal outcome;
- terminal `MatchResult v2`;
- Godot production bridge és smoke foundation.

### RÉSZLEGES / TOVÁBB BŐVÍTENDŐ

- ability coverage a teljes kártyaállományra;
- compound target/payment/choice;
- generic prevention/replacement;
- trigger-sorrend speciális esetei;
- temporary/alternate payment;
- special Seal restore/ward-effect runtime;
- diagnostics és release support policy;
- player-facing UI;
- AI/headless orchestration;
- replay.

### TUDATOSAN KÜLÖN KÉSŐBBI SLICE / PRODUCT LAYER

- Refresh Penalty;
- Hasítás runtime;
- teljes Burst/Jel runtime;
- Kényszerítés;
- Token runtime;
- replay runner;
- production AI-vs-AI;
- végleges Windows packaging;
- profile/save;
- tutorial/collection/economy;
- teljes player UI.

Ezek közül nem mind VS1-blocker.

## 5. Következő biztonságos engine-/product-szakasz

### Combat + Pecsét Foundation C0–C6 – LEZÁRVA

Rules migration:

`61ad2605dd1aa3d7ea95444f0bb66cebf819014e`

Production slice-ok:

- `ca55bc3714de2692753fccc18a8f11d9dac1beea` – C0 setup + Seal foundation;
- `558d4453a1604c0ebe76065df08a207192c21c8b` – C1+C2 attack + első Combat ReactionWindow;
- `d236f0e3c36994f65e7d00d25972660baac2a842` – C3 intervention + DefenseCommit;
- `68b07dd6906fc8c37245325a855322d48f5f2635` – C4 Entity Combat;
- `d30f8a4c42383a0200e416acb7148facc3bbbc11` – C5 SealBreak + Surge + Gondviselés;
- `0862e1002dbef81ee203852714d377592272a0e9` – C6 Aeternal + terminal MatchResult.

Final acceptance:

- Debug/Release C#: `301/301 PASS`;
- targeted C6: `8/8 PASS`;
- determinism/reference: `100/100 PASS`;
- canonical SHA:
  `97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`;
- Python isolated regression: `465/465 PASS`, `5 skip`;
- exporter: `23/23 PASS`;
- Godot build + positive/negative smoke: PASS;
- unresolved P0/P1: `0/0`.

Státusz:

`COMBAT_AND_SEAL_FOUNDATION_C0_C6 = COMPLETE_AND_ACCEPTED`

### Current roadmap

A hosszabb projektút current kerete:

```text
M5 / Combat + victory core
→ M6 / VS1 – első ténylegesen játszható vertical slice
→ szükséges köztes mérföldkövek
→ AETERNA 0.0.1
```

A VS1 nem azonos a korábbi, már lezárt production gameplay foundation slice-szal.

Canonical VS1 deckek:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

VS1 előtt csak az a capability válik kötelező blockerré, amely a két VS1 pakli
szabályos, elejétől `MatchResult`-ig tartó játékához ténylegesen szükséges, vagy
olyan általános engine-invariáns, amely nélkül a VS1 nem tekinthető korrektnek.

Következő engine/product lépés a runtime-fejlesztés folytatásakor:

```text
VS1 content/mechanic readiness audit
→ emberi prioritásdöntés
→ szükséges finite contract/programozási slice-ok
→ simple fair AI + minimal playable Godot
→ VS1 end-to-end acceptance
```

A current repository-level priority a dokumentumkezelési workstream marad a tervezett closeout- és editor-foundation lépések befejezéséig.

## 6. Aktuális döntési kapuk és Open Questions

C0–C6 utáni OQ állapot:

`52 answered / 15 partly_answered / 7 deferred / 0 open` (74 total).

Az `answered` current canonical/default választ jelent, nem örök megváltoztathatatlanságot.

### OQ-SNAP-002 – Pecsétmodell

`answered`.

Current production default:

- playerenként 6 stabil public Seal slot;
- lane + `standing|broken` public;
- standing Seal card identity mindkét player-facing viewer előtt hidden, owner előtt is;
- break után public reveal;
- Surge után hand identity ismét owner-only;
- reveal history public marad.

### OQ-LA-003 – Combat actionök

`answered`.

C0–C6 productionben rögzítette:

- `attack`;
- AttackCommit;
- intervention / decline;
- DefenseCommit;
- két Combat ReactionWindow;
- `PendingCombat`;
- participant/incarnation/contact revalidation;
- Entity / Seal / Aeternal outcome;
- deterministic cleanup.

### Továbbra is részleges kapuk

Többek között:

- generic prevention/replacement;
- compound non-reaction choice;
- explicit special Seal restore/ward-effect ability contract;
- C0–C6 scope-on túli Expansion-interakciók;
- teljes ability coverage.

### Refresh Penalty

Külön későbbi rules/implementation slice; a production draw runtime nem találhat ki placeholder-szabályt.

## 7. Dokumentációs konzisztencia-helyreállítás

**Státusz:** `COMPLETE`

A `2608345b...` mérföldkőhöz tartozó célzott aktív dokumentációs consistency pass 2026-08-14-én elkészült.

### A kör – projektirány és checkpoint

Frissítve és összehangolva:

- root `README.md`;
- `Aeterna dokumentációk/README.md`;
- jelen projektterv v6.5;
- `project/status/PROJECT_MAP_FILE_STATUS.md`;
- `Aeterna game engine/README.md`;
- `Aeterna game engine/docs/README.md`;
- `project/status/checkpoints/ENGINE_CHECKPOINT.md`;
- `checkpoints/CHECKPOINTS.md`;
- `checkpoints/README.md`;
- `project/decisions/DECISION_MAP.md`;
- `project/status/PROTOTYPE_STATUS.md`.

### B kör – contract, runtime és OQ konzisztencia

Frissítve és összehangolva:

- `src/engine/docs/CONTRACT_STATUS.md`;
- `src/engine/docs/CONTRACT_SPECIFICATION.md`;
- `data/status/RUNTIME_PACKAGE_STATUS.md`;
- `data/specifications/RUNTIME_PACKAGE_SPECIFICATION.md`;
- `src/engine/docs/ABILITY_MODULE_SYSTEM.md`;
- `project/planning/OPEN_QUESTIONS.md`;
- `project/decisions/OPEN_QUESTIONS_DECISIONS.md`;
- `project/architecture/ARCHITECTURE.md`.

### Tudatosan nem frissített történeti/lezárt proofok

Megmarad:

- `PROTOTYPE_PLANS.md`;
- `project/decisions/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `tests/fixtures/runtime_comparison/RUNTIME_COMPARISON_FIXTURE_SPEC.md`;
- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`;
- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`.

A `project/decisions/TECHNOLOGY_DECISIONS.md` továbbra is csak valódi technológiai döntés változásakor kap új verziót.

### C kör – learning, synthesis, OQ és history-recovery handoff

Commitolt: `ae7d284...` learning registry/analyses, `b0e4d9d...` synthesis/blueprints, `743c00d...` OQ v2.2, `14e315d...` governance/ability/checkpoint targeted recovery.

Current evidence: `59 registry / 58 local / 30 analyses`. Learning/synthesis/blueprint evidence/proposal, nem rules authority.

Dokumentációs munkaszabály:

```text
current committed file
→ Git/Archive history comparison
→ targeted edit
→ GitHub Desktop diff review
```

Aktív checkpoint/status/decision dokumentumot alapértelmezésben nem generálunk újra nulláról.

## 8. Codex-használati munkaszabály

Az AETERNA projektben Codexet csak akkor használunk, ha a feladat ténylegesen igényli.

### Codexre bízandó tipikus feladat

- programozás;
- build/test/smoke futtatás;
- helyi dirty worktree vagy olyan lokális fájl elemzése, amely GitHubon vagy feltöltött forrásként nem érhető el megbízhatóan;
- nagy helyi kód/fájlhalmaz technikai ellenőrzése, ha az innen nem reprodukálható.

### Nem Codex-feladat alapértelmezésben

- projekttervezés;
- dokumentációs szerkesztés;
- szabályelemzés;
- döntési kapuk feloldása;
- learning tanulságok értékelése;
- Codex-prompt előkészítése;
- commit/push/PR rutinművelet, ha a felhasználó maga el tudja végezni.

A Codex nem hoz önálló játékszabályi vagy projektirányítási döntést.

Current default szerint Codex lokális technikai módosítást és validációt készít, de nem commitol és nem pushol. Külső audit és emberi jóváhagyás után a felhasználó commitol/pushol.

---

## 9. Párhuzamos nem programozási prioritások

Továbbra is aktív:

1. kártyaadat- és szabályaudit;
2. LOOKUPS- és ID-contract munka;
3. kártyadizájn- és vizuális workflow;
4. learning projektek célzott clean-room vizsgálata, amikor közvetlenül segít egy következő AETERNA-döntésben.

A learning projekt nem szabályforrás és nem közvetlen kódforrás.

### 9.1 Current dokumentum-governance fázis

A PILOT-6 stable filename migration `COMPLETE`; mind a 29 managed artifact stabil
artifact ID-val, stabil current fájlnévvel és natív metadata-authorityvel rendelkezik.
A PILOT-7A editor/updater design audit `COMPLETE`.

Az elfogadott foundation-lépések:

- PILOT-7B document update workflow contract: `COMPLETE_AND_REMOTE_VERIFIED`;
- PILOT-7C read-only workflow foundation: `COMPLETE_AND_REMOTE_VERIFIED`;
- PILOT-7D safe Markdown update MVP: `COMPLETE_AND_REMOTE_VERIFIED`;
- PILOT-7D.1 transaction hardening: `COMPLETE_AND_REMOTE_VERIFIED`;
- PILOT-7E first real governed managed-document update: `COMPLETE_AND_REMOTE_VERIFIED`;
- PILOT-7F workflow integration/self-hosting activation: `COMPLETE_AND_REMOTE_VERIFIED`;
- PILOT-7G current filename normalization: `COMPLETE_AND_REMOTE_VERIFIED`;
- PILOT-7G.1 remaining current source filename normalization: `COMPLETE_AND_REMOTE_VERIFIED`;
- PILOT-8A CREATE design audit: `COMPLETE`;
- PILOT-8B CREATE governance contract: `COMPLETE_AND_REMOTE_VERIFIED`, remote commit
  `edf86260e40370538f7f32835972d661f2894a85`;
- PILOT-8C read-only `plan-create`: `COMPLETE_AND_REMOTE_VERIFIED`, remote commit
  `591facbc06668d33bc669a37a699250a97535da6`;
- PILOT-8D minimal transactional explicit CREATE:
  `COMPLETE_AND_REMOTE_VERIFIED`, remote commit
  `860cbf7fda03d67c953982a7d0be0c5cfd05542a`.

`PILOT-8D = COMPLETE_AND_REMOTE_VERIFIED`
`PILOT-8D_REMOTE_COMMIT = 860cbf7fda03d67c953982a7d0be0c5cfd05542a`

Az `AET-DOC-DOCUMENT-UPDATE-WORKFLOW` verziója `1.0`, integration státusza
`current`.

```text
UPDATE_WORKFLOW = IMPLEMENTED_AND_ACCEPTED
UPDATE_0_1_BACKWARD_COMPATIBLE = YES
CREATE_PLAN_SCHEMA = aeterna-document-create-plan/0.1
CREATE_REVIEW_SCHEMA = aeterna-document-create-review/0.1
PLAN_CREATE = IMPLEMENTED_AND_ACCEPTED
CREATE_APPLY = IMPLEMENTED_AND_ACCEPTED
CREATE_REVIEW = IMPLEMENTED_AND_ACCEPTED
CREATE_NEW_TARGET_ROLLBACK = VERIFIED
AUTONOMOUS_DOCUMENT_GENERATION = OUT_OF_SCOPE
```

Az elfogadott current CLI surface:
`resolve → impact → plan-update → plan-create → apply → verify-review`.
Ezek közül a `resolve`, `impact`, `plan-update`, `plan-create` és `verify-review`
read-only; kizárólag az explicit `apply` mutating. Az `apply` az elfogadott UPDATE
és CREATE plan sémákat dispatch-eli. A Git staging, commit és push továbbra is
ember által kontrollált handoff.

`DOCUMENT_GOVERNANCE_FOUNDATION = COMPLETE_AND_CURRENT`

Ez a foundation lezárását jelenti, nem minden jövőbeli dokumentumkezelési képesség
elkészültét. A current implementáció nem támogatja a következőket:
`retire/archive intake`, `move/rename`, authority change, batch editing, XLSX
editing, DOCX editing, source-bundle editing és package-manifest editing. A
PILOT-7G/7G.1 bounded structural migration volt, ezért nem bizonyít generic
move/rename támogatást.

A current managed/document technical filename normalization `COMPLETE`. Az elfogadott
migrációkkal lefedett current réteg stabil English/ASCII fájlneveket használ; az
Archive/history történeti fájlnevei szándékosan megmaradhatnak.

A ChatGPT Library manuális auditja és refresh-e elkészült. A Library egy
`completed structural/context snapshot`: cross-chat retrieval-, struktúra- és
kontextustámpont, amely új beszélgetésben segíti a projektmodell rekonstruálását és a
korábbi beszélgetések, történeti snapshotok visszakeresését.

`CHATGPT_LIBRARY_REFRESH = COMPLETE`

A ChatGPT Library nem a repository automatikusan szinkronizált current másolata.
`continuous repository synchronization = NOT REQUIRED`; a `canonical latest source =
GitHub main`, ezért eltérés esetén GitHub `main` az irányadó. A pontos aktuális
dokumentumverziót, HEAD-et, státuszt és implementációt GitHubról kell ellenőrizni.

`LIBRARY_ROLE = STRUCTURE_AND_CONTEXT_SNAPSHOT`
`CANONICAL_CURRENT_SOURCE = GITHUB_MAIN`
`CONTINUOUS_LIBRARY_SYNC_REQUIRED = NO`

`DOCUMENT_SYSTEM_SCOPE_FREEZE = ACCEPTED`

A következő projektlépés:
`PILOT-8E = NEXT / FIRST_REAL_GOVERNED_CREATE_ACCEPTANCE`.
Ennek célja az ember által jóváhagyott `AETERNA Document Editor – MVP
Specification`; ez a dokumentum még nem létezik, és a CREATE apply még nem történt
meg.

Az `AETERNA Document Editor` lesz a governed document workflow fölötti dedikált
authoring/editing réteg. Koncepcionális felelőssége a human/AI-assisted content
authoring, a structured target selection, a candidate generation és a diff/review;
validáláshoz és alkalmazáshoz a meglévő governed workflow-t használja.


### 9.2 Document System Scope Freeze – 2026-10-08

Az elfogadott AETERNA Document System:

```text
HUMAN-DIRECTED
LOCAL-FIRST
GOVERNED
REVIEW-FIRST
```

Célja az AETERNA dokumentumok létrehozásának, szerkesztésének, validálásának,
review-jának és megőrzésének egyszerűsítése anélkül, hogy visszatérne a
verziózott fájlmásolatokhoz vagy kontrollálatlan dokumentumszaporulathoz.

Az ember dönti el, milyen dokumentum és mikor szükséges, milyen tartalom válik
canonical állapottá, mely artifact identity/path/authority fogadható el, mikor
alkalmazható egy változás, és mikor történhet Git staging, commit vagy push. Az
automatizálás és az AI segítheti az előkészítést és validálást, de nem döntési
authority.

Az első Document System / Editor MVP kötelező alapjai:

- stabil artifact identity és current fájlnevek;
- natív metadata, belső dokumentumverzió és Git history;
- meglévő managed Markdown dokumentum biztonságos governed UPDATE művelete;
- új managed Markdown dokumentum explicit, ember által indított CREATE művelete;
- pre-write, dependency- és impact-validáció;
- generált registry/index konzisztencia;
- canonical elfogadás előtti diff, plan és review;
- ember által kontrollált apply, staging, commit és push határ;
- AETERNA Document Editor MVP.

Az Editor MVP fogalmi felhasználói folyamata:

```text
document list/open
→ Markdown editing
→ preview
→ metadata assistance
→ validation
→ diff/review
→ explicit save/apply

explicit New Document
→ candidate
→ validation
→ review
→ explicit apply
```

Ez scope-döntés, nem részletes Editor UI-specifikáció, és nem választ
frameworköt vagy GUI-technológiát.

```text
AUTONOMOUS_DOCUMENT_GENERATION = OUT_OF_SCOPE
```

Az AI draftolhat, átírhat, összefoglalhat, metadata- és dependency-javaslatot
adhat, consistency problémát jelezhet és candidate tartalmat készíthet. Nem
döntheti el autonóm módon, hogy új canonical dokumentum szükséges; nem hozhat
létre canonical dokumentumot explicit emberi kezdeményezés nélkül; nem
választhat végleges artifact ID-t, canonical pathot vagy authorityt emberi
elfogadás nélkül; nem írhat át automatikusan dependent human-maintained
dokumentumokat; és nem stage-elhet, commitolhat vagy pusholhat. Az AI-output
explicit emberi workflow-elfogadásig candidate/proposal.

Magas értékű, de az első Editor MVP-t nem blokkoló post-MVP képesség:

- dokumentumkeresés és navigáció;
- dependency/impact vizualizáció;
- Git history/diff megjelenítés;
- dokumentumsablonok;
- AI-assisted authoring és consistency review;
- DOCX → governed Markdown import.

Ezek a core editor után, vagy csak közvetlen implementációs szükség esetén
korábban adhatók hozzá; nem PILOT-8D követelmények.

Explicit deferred képesség: generic batch editing, generic move/rename, general
retirement/archive UI, XLSX editing az Editorban, source-bundle és
package-manifest editing, repository-wide automatic reference rewriting és
automatic dependent-document rewriting. Ezek nem végleg elutasítottak; valós
use case esetén válhatnak munkává.

Új fejlesztési elv:

```text
No new document-management capability is added merely because it would be
technically useful.

A capability enters the active MVP only when it directly supports creation,
editing, validation, preservation, review, or safe human-controlled
application of AETERNA documents.
```

Az első használható Document Editor után a további képességeket lehetőleg valós
használat igazolja.

`PILOT_8D_SCOPE = MINIMAL_TRANSACTIONAL_EXPLICIT_CREATE`

PILOT-8D kizárólag egy már emberileg szándékolt, materializált és valid CREATE
plant revalidálhat; tranzakciósan pontosan egy új managed Markdown dokumentumot
hozhat létre; szükség esetén frissítheti a registry/index nézeteket; post-write
validációt és CREATE review evidence-et készíthet; hiba esetén pedig teljesen
rollbackol.

PILOT-8D nem tartalmaz automatikus dokumentumgenerálást vagy szükségletdöntést,
Editor UI-t, AI authoring rendszert, sablont, keresést, DOCX/XLSX munkát,
move/rename-et, retirement/archive-ot, batch műveletet, authority-change
műveletet, Git staginget, commitot vagy pusht. Explicit emberi CREATE akció
infrastruktúrája marad.

PILOT-8E `FIRST_REAL_GOVERNED_CREATE_ACCEPTANCE`; célja az `AETERNA Document
Editor v0.1 specification`. Artifact ID-ját, canonical pathját, metadatáját,
authorityjét, dependencyit, initial versionjét és body/contentjét az első valós
CREATE apply előtt embernek kell review-znia. A rendszer ezt a specifikációt nem
találhatja ki autonóm módon.

Elfogadott roadmap:

```text
PILOT-8C = COMPLETE_AND_REMOTE_VERIFIED
→ DOCUMENT_SYSTEM_SCOPE_FREEZE = ACCEPTED
→ PILOT-8D = MINIMAL_TRANSACTIONAL_EXPLICIT_CREATE
→ PILOT-8E = FIRST_REAL_GOVERNED_CREATE_ACCEPTANCE
  (AETERNA Document Editor v0.1 specification)
→ AETERNA DOCUMENT EDITOR MVP specification + implementation
→ REAL USAGE
→ only justified follow-up document capabilities
```

Runtime / VS1 a current dokumentumkezelési prioritás után marad.


### 9.3 PILOT-8E – első valós governed CREATE acceptance

```text
PILOT-8E = NEXT
PILOT_8E_MEANING = FIRST_REAL_GOVERNED_CREATE_ACCEPTANCE
PILOT_8E_EDITOR_SPEC_IDENTITY = HUMAN_APPROVED
PILOT_8E_CREATE_APPLY = NOT_YET_EXECUTED
```

A következő CREATE művelet ember által jóváhagyott identity-je:

```text
ARTIFACT_ID = AET-DOC-DOCUMENT-EDITOR-SPECIFICATION
CANONICAL_PATH = project/requirements/DOCUMENT_EDITOR_SPECIFICATION.md
TYPE = specification
INITIAL_VERSION = 0.1
AUTHORITY = technical-contract
DEPENDENCIES = AET-DOC-DOCUMENT-GOVERNANCE;
               AET-DOC-DOCUMENT-UPDATE-WORKFLOW;
               AET-DOC-PROJECT-PLAN
```

Ezek a PILOT-8E bemenetei explicit emberi jóváhagyást kaptak. Ez a projektterv
csak a jóváhagyott identity-t és scope-ot rögzíti; a specifikációt nem hozza létre.

`DOCUMENT_EDITOR_IMPLEMENTATION_STRATEGY = BUILD_VS_ADOPT_NOT_YET_DECIDED`

A Document Editor funkcionális cél, nem előre eldöntött custom alkalmazás. Az
implementáció előtt értékelni kell, hogy az MVP-t kielégíti-e egy meglévő
alkalmazás; meglévő alkalmazás plugin vagy konfiguráció kiegészítéssel; meglévő
editor AETERNA-specifikus toolinggal; hybrid megoldás; vagy teljesen custom
alkalmazás. A teljesen custom alkalmazás nem alapértelmezett követelmény.

A döntési szempontok: az MVP-követelmények lefedése, local-first működés, a
governed workflow integrációja, karbantarthatóság és a szükséges custom fejlesztési
ráfordítás. Konkrét termék vagy framework még nincs kiválasztva.

Az ember által jóváhagyott v0.1 specifikáció scope-ja:

- cél és határok;
- `HUMAN-DIRECTED / LOCAL-FIRST / GOVERNED / REVIEW-FIRST` elvek;
- managed Markdown UPDATE;
- explicit, ember által kezdeményezett CREATE;
- dokumentumlista és megnyitás;
- Markdown szerkesztés és preview;
- metadata assistance és validáció;
- diff/review és explicit save/apply;
- New Document workflow;
- governed workflow integráció;
- AI mint opcionális segítség, nem döntési authority;
- autonomous document generation kizárása;
- automatikus Git staging/commit/push kizárása;
- build-vs-adopt értékelés az implementáció előtt;
- deferred/post-MVP képességek;
- MVP acceptance criteria.


---

## 10. Rövid aktuális állapot

**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9`
**Production authority:** C#/.NET
**Visual client:** Godot/GDScript
**External tooling/reference:** Python
**C.5B foundation:** `COMPLETE_AND_ACCEPTED`
**Korábbi production gameplay foundation slice:** `COMPLETE_AND_ACCEPTED`
**Explicit Phase Foundation v1:** `COMPLETE_AND_ACCEPTED`
**Reaction / Priority Foundation v1:** `COMPLETE_AND_ACCEPTED`
**Combat + Pecsét Foundation C0–C6:** `COMPLETE_AND_ACCEPTED`
**Terminal victory core:** `COMPLETE_AND_ACCEPTED`
**Learning registry:** `59 registry / 58 local`
**Project analyses:** `30`
**Synthesis/blueprint program:** `COMMITTED`
**Open Questions:** `52 answered / 15 partly_answered / 7 deferred / 0 open`
**Managed artifacts:** `29`
**PILOT-6 stable filename migration:** `COMPLETE`
**PILOT-7A editor/updater design audit:** `COMPLETE`
**PILOT-7B document update workflow contract:** `COMPLETE_AND_REMOTE_VERIFIED`
**PILOT-7C read-only workflow foundation:** `COMPLETE_AND_REMOTE_VERIFIED`
**PILOT-7D safe Markdown update MVP:** `COMPLETE_AND_REMOTE_VERIFIED`
**PILOT-7D.1 transaction hardening:** `COMPLETE_AND_REMOTE_VERIFIED`
**PILOT-7E first real governed managed-document update:** `COMPLETE_AND_REMOTE_VERIFIED`
**PILOT-7F workflow integration/self-hosting activation:** `COMPLETE_AND_REMOTE_VERIFIED`
**PILOT-7G current filename normalization:** `COMPLETE_AND_REMOTE_VERIFIED`
**PILOT-7G.1 remaining current source filename normalization:** `COMPLETE_AND_REMOTE_VERIFIED`
**Document update workflow:** `1.0 / current`
**UPDATE workflow:** `IMPLEMENTED_AND_ACCEPTED`
**UPDATE 0.1 backward compatibility:** `YES`
**CREATE plan schema:** `aeterna-document-create-plan/0.1`
**CREATE review schema:** `aeterna-document-create-review/0.1`
**PLAN-CREATE:** `IMPLEMENTED_AND_ACCEPTED`
**CREATE apply:** `IMPLEMENTED_AND_ACCEPTED`
**CREATE review:** `IMPLEMENTED_AND_ACCEPTED`
**CREATE new-target rollback:** `VERIFIED`
**PILOT-8A CREATE design audit:** `COMPLETE`
**PILOT-8B CREATE governance contract:** `COMPLETE_AND_REMOTE_VERIFIED`
**PILOT-8B remote commit:** `edf86260e40370538f7f32835972d661f2894a85`
**PILOT-8C read-only plan-create:** `COMPLETE_AND_REMOTE_VERIFIED`
**PILOT-8C remote commit:** `591facbc06668d33bc669a37a699250a97535da6`
**PILOT-8D minimal transactional explicit CREATE:** `COMPLETE_AND_REMOTE_VERIFIED`
**PILOT-8D remote commit:** `860cbf7fda03d67c953982a7d0be0c5cfd05542a`
**Document System Scope Freeze:** `ACCEPTED`
**Autonomous document generation:** `OUT_OF_SCOPE`
**Document governance foundation:** `COMPLETE_AND_CURRENT`
**Current filename normalization:** `COMPLETE`
**ChatGPT Library refresh:** `COMPLETE`
**PILOT-8E first real governed CREATE acceptance:** `NEXT`
**PILOT-8E editor specification identity:** `HUMAN_APPROVED`
**PILOT-8E CREATE apply:** `NOT_YET_EXECUTED`
**Document Editor implementation strategy:** `BUILD_VS_ADOPT_NOT_YET_DECIDED`
**AETERNA Document Editor MVP specification:** `NEXT GOVERNED CREATE TARGET`
**AETERNA Document Editor implementation:** `PLANNED`
**VS1 / M6:** `NEXT MAJOR PRODUCT-FACING GOAL AFTER DOCUMENT-MANAGEMENT PRIORITY`
**0.0.1:** `ACTIVE_LONG_TERM_TARGET`

## 11. Következő szakmai munkasorrend

1. PILOT-8E: az első valós governed CREATE acceptance, az ember által jóváhagyott
   `AETERNA Document Editor – MVP Specification` létrehozása;
2. AETERNA Document Editor build-vs-adopt értékelés;
3. AETERNA Document Editor MVP implementation;
4. valós használat;
5. csak valós használattal igazolt további dokumentumképességek;
6. runtime / VS1 munka később, a projektprioritás szerint.

Elfogadott roadmap:

```text
PILOT-8C = COMPLETE_AND_REMOTE_VERIFIED
→ DOCUMENT_SYSTEM_SCOPE_FREEZE = ACCEPTED
→ PILOT-8D = COMPLETE_AND_REMOTE_VERIFIED
→ PILOT-8E = NEXT / FIRST_REAL_GOVERNED_CREATE_ACCEPTANCE
→ AETERNA Document Editor build-vs-adopt evaluation
→ AETERNA Document Editor MVP implementation
→ REAL USAGE
→ only justified follow-up document capabilities
```

Runtime / VS1 prioritása a current dokumentumkezelési prioritás után marad.

Elfogadott státusz:

- `ChatGPT Library refresh = COMPLETE`;
- `PILOT-8A = COMPLETE`;
- `PILOT-8B = COMPLETE_AND_REMOTE_VERIFIED`;
- `PILOT-8C = COMPLETE_AND_REMOTE_VERIFIED`;
- `DOCUMENT_SYSTEM_SCOPE_FREEZE = ACCEPTED`;
- `PILOT-8D = COMPLETE_AND_REMOTE_VERIFIED`;
- `PILOT-8E = FIRST_REAL_GOVERNED_CREATE_ACCEPTANCE / NEXT`;
- `PILOT_8E_EDITOR_SPEC_IDENTITY = HUMAN_APPROVED`;
- `PILOT_8E_CREATE_APPLY = NOT_YET_EXECUTED`;
- `DOCUMENT_EDITOR_IMPLEMENTATION_STRATEGY = BUILD_VS_ADOPT_NOT_YET_DECIDED`;
- `AETERNA Document Editor MVP specification = NEXT GOVERNED CREATE TARGET`;
- `AETERNA Document Editor implementation = PLANNED`.

Reaction / Priority v1: `COMPLETE_AND_ACCEPTED`.

Combat + Pecsét C0–C6: `COMPLETE_AND_ACCEPTED`.

---

## 12. Archive recovery szabály

Az `Archive/` történeti bizonyítéktár, nem current authority és nem automatikus
visszaállítási forrás.

Archív információ csak akkor emelhető vissza current dokumentumba, ha:

1. kompatibilis a current official rules/architecture réteggel;
2. nincs újabb/current jobb megfelelője;
3. a VS1 → 0.0.1 út szempontjából ténylegesen fontos;
4. emberi review megerősíti, hogy a korábbi archiválás nem tartalmi elutasítás volt;
5. az új current szerepe explicit.

Nem állítunk vissza pusztán történeti részletesség miatt régi Python-authority modellt,
régi rules authority-t, mappaszerkezet-pillanatképet, régi Codex commit/push policyt
vagy más felváltott current állapotot.
