---
artifact_id: AET-DOC-TECHNOLOGY-DECISIONS
kind: document
type: decision-log
version: "2.6"
lifecycle: active
integration: current
authority: technical-architecture
generated: false
depends_on: []
supersedes: []
---

# AETERNA Game Engine – Technology Decisions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.6
**Dátum:** 2026-10-10
**Státusz:** aktív technológiai döntési nyilvántartás  
**Aktuális repository-bázis:** `c8e7e1854c3e054c8c0f59ba35196ae6d0ffdecd` – `feat: add read-only vscode document extension proof`

Ez a dokumentum az AETERNA elfogadott technológiai döntéseit, azok indokait, korlátait és újranyitási feltételeit rögzíti.

Kapcsolódó aktív dokumentumok:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `ARCHITECTURE.md`
- `DECISION_MAP.md`
- `PROTOTYPE_STATUS.md`
- `CONTRACT_STATUS.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `project/status/checkpoints/ENGINE_CHECKPOINT.md`
- `project/governance/DOCUMENT_GOVERNANCE.md`
- `project/governance/workflows/DOCUMENT_UPDATE_WORKFLOW.md`
- `project/requirements/DOCUMENT_EDITOR_SPECIFICATION.md`
- `project/planning/PROJECT_PLAN.md`

---

## 1. TD-001 – Contract-first fejlesztés

**Státusz:** ELFOGADVA  
**Hatály:** teljes digitális rendszer

Döntés:

- előbb contract, utána implementáció;
- a kliens action requestet küld;
- az engine action response-t, eventet és projectiont ad;
- player-visible és debug contract külön marad;
- rejtett információt projection véd;
- rejected action nem mutálhat state-et;
- eventek determinisztikusak és auditálhatók.

Indok:

Az AETERNA több fogyasztót támogat:

- Godot UI;
- AI;
- headless tesztek;
- replay;
- diagnostics;
- későbbi hálózati vagy autoritatív futás.

Újranyitás:

Nem tervezett. Csak teljes architektúraváltás esetén.

---

## 2. TD-002 – Egyetlen authoritative rules runtime

**Státusz:** ELFOGADVA  
**Hatály:** teljes gameplay

Döntés:

Egy meccsnek pontosan egy authoritative state-je és egy kanonikus szabálymotorja lehet.

A production authoritative runtime:

> **C#/.NET**

A Godot/GDScript és a Python nem tarthat külön kanonikus meccsállapotot.

Tiltott:

- ugyanazon szabály párhuzamos authoritative C# és Python implementációja;
- kliensoldali legalitásmintázás authoritative döntésként;
- GDScript által közvetlenül módosított MatchState;
- Python által a C# transition API megkerülésével módosított state.

Indok:

- elkerüli a rules driftet;
- javítja a determinisztikát;
- egyszerűsíti a replayt;
- támogatja az AI és az emberi kliens azonos szabálymotorát;
- csökkenti a kettős hibakeresést.

---

## 3. TD-003 – Godot/GDScript vizuális kliensréteg

**Státusz:** ELFOGADVA

A Godot/GDScript feladata:

- jelenetek;
- input;
- UI;
- animáció;
- hang;
- vizuális kártyaállapot;
- debugpanelek;
- snapshot- és eventmegjelenítés;
- action requestek előkészítése.

Nem feladata:

- legalitás;
- költség;
- effect resolution;
- turn transition;
- combat;
- hidden-information authority;
- győzelmi feltétel.

A Godot és a C# közvetlenül, ugyanazon processzen belül kommunikál.

Nem használunk közöttük:

- TCP-t;
- HTTP-t;
- gRPC-t;
- külön engine-processzt.

---

## 4. TD-004 – C# authoritative runtime kiválasztása

**Státusz:** ELFOGADVA  
**Döntési dátum:** 2026-07-20

Elfogadott modell:

- Godot/GDScript – vizuális kliens;
- C# – authoritative rules runtime;
- Python – külső tooling.

Bizonyító commit:

`8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Bizonyított:

- Godot 4.7.1 .NET;
- .NET 8;
- pure C# runtime;
- közvetlen in-process hívás;
- nincs külön engine-processz;
- nincs Python;
- nincs TCP;
- Debug és Release build;
- nulla warning/error;
- headless proof;
- visual proof;
- két manuális PASS;
- 100-run determinisztika;
- mutation negative proof;
- GDScript regressziók.

Közös canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

Indok:

A C# ugyanazt a kanonikus eredményt kisebb futási és lifecycle-összetettséggel állította elő, mint a Python sidecar.

Újranyitás:

Csak új, AETERNA-specifikus bizonyíték esetén, amely jelentős problémát mutat:

- production packaging;
- teljesítmény;
- karbantarthatóság;
- platformkompatibilitás;
- Godot-integráció.

---

## 5. TD-005 – Python–Godot sidecar lezárása

**Státusz:** COMPLETE AND FROZEN

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e` – `Fix Godot sidecar cancellation race warnings`

Bizonyított:

- localhost TCP;
- request/response framing;
- handshake;
- timeout;
- controlled shutdown;
- Emergency Shutdown;
- F8 parent watchdog;
- orphan cleanup;
- warning/error nélküli manuális futás;
- helyes canonical output.

Döntés:

A proof megmarad összehasonlítási és történeti referenciaként, de nem fejlesztjük production főmotorrá.

Nem készül hozzá jelenleg:

- packaging;
- új protokoll;
- új watchdog;
- új sidecar UI;
- további TCP funkció.

Indok:

A működő proof bizonyította a modell életképességét, de a külön processz, TCP, shutdown és watchdog infrastruktúra szükségtelen a közvetlen C# in-process modell mellett.

---

## 6. TD-006 – Python tartós szerepe

**Státusz:** ELFOGADVA

Python marad:

- adatpipeline;
- XLSX/JSON/JSONL feldolgozás;
- runtime package build;
- validáció;
- audit;
- fixture-generálás;
- scenario runner;
- AI-vs-AI koordináció;
- batch futtatás;
- balansz- és statisztikai tooling;
- riport;
- regression/reference oracle;
- differential testing.

A Python minimal engine:

- megőrzendő;
- nem törlendő automatikusan;
- referenciaimplementáció;
- expected-output forrás;
- migrációs ellenőrző alap.

A Python nem maradhat külön fejlődő production authoritative gameplay engine.

---

## 7. TD-007 – Python–C# kommunikáció

**Státusz:** ELFOGADVA ÉS IMPLEMENTÁLT ALAPHATÁR

Current forma:

```text
Python
  ↓ subprocess + JSON/JSONL / file / stdin
Aeterna.Engine.Headless
  ↓ canonical JSON/JSONL
Python
```

Használat:

- fixture;
- scenario;
- AI/batch tooling;
- balanszelemzés;
- CI;
- regresszió;
- canonical/reference comparison.

A Python csak viewer-safe snapshotból és a C# engine által kiadott legal actionökből dolgozhat.

A state mutation a C# engine transition API-ján, illetve az azt vékonyan exponáló Headless határon keresztül történik.

A Python nem:

- írhat közvetlenül authoritative `MatchState`-et;
- implementálhat külön gameplay legality authorityt;
- kerülheti meg a `SubmitAction`/engine transition határt.

Későbbi localhost HTTP vagy gRPC:

- csak teljesítménymérés alapján;
- csak hosszú életű batch/service igény esetén;
- nem a Godot normál runtime részeként.

Ez reserved extension point, nem current architecture requirement.

## 8. TD-008 – Embedded Python elhalasztása

**Státusz:** RESEARCH_ONLY_DEFERRED

Jelenleg nem választott:

- Python.NET;
- py4godot;
- godot-python-extension;
- GodoPy;
- egyéb CPython/GDExtension binding.

Fő kockázatok:

- CPython DLL és verzió;
- natív build;
- GIL;
- típuskonverzió;
- packaging;
- platformkompatibilitás;
- közös processzben bekövetkező crash;
- három nyelv szoros runtime-csatolása.

Újranyitás:

Csak nélkülözhetetlen, elkülöníthető és nem authoritative Python-funkció esetén.

---

## 9. TD-009 – Runtime package és adatpipeline

**Státusz:** ELFOGADVA

Döntések:

- a fő szerkesztés Google Sheetsben történik;
- a lokális XLSX forrásmásolat;
- Godot nem olvas közvetlenül XLSX-et;
- C# engine nem olvas közvetlenül XLSX-et;
- Python végzi az exportot, validációt és package buildet;
- a runtime package statikus programadat;
- publish előtt validation gate kell;
- a Godot `runtime_package/` consumption copy;
- a generált output nem canonical szerkesztési forrás.

Még nyitott:

- package identity;
- release versioning;
- final build/output struktúra;
- integritásvédelem;
- publikus kiadásnál tamper resistance.

---

## 10. TD-010 – Production C# project-határok

**Státusz:** ELFOGADVA ÉS IMPLEMENTÁLVA
**Foundation implementáció:** C.5B, `931bf5571d541c752aa421a9f0626768bd8ffbe7`
**Current production base:** `0862e1002dbef81ee203852714d377592272a0e9`

Production projektek:

```text
Aeterna.Engine
Aeterna.Engine.Headless
Aeterna.Engine.Tests
Aeterna.Engine.sln
```

### Aeterna.Engine

- pure C#;
- Godot nélkül buildelhető;
- nincs Python runtime dependency;
- nincs processzkezelés;
- nincs TCP/HTTP/gRPC rules path;
- authoritative state és rules.

Current authoritative core már tartalmazza többek között:

- phase/turn lifecycle;
- Wellspring/Infusion;
- Domain/`play_card`;
- ability/effect foundation;
- Reaction/Priority;
- Combat/Pecsét C0–C6;
- terminal Aeternal / `MatchResult`.

### Aeterna.Engine.Headless

- vékony console/headless host;
- fixture/scenario;
- Python tooling kapcsolat;
- JSON/JSONL boundary;
- nincs saját gameplay-logika.

### Aeterna.Engine.Tests

- contract;
- invariant;
- transition;
- determinism;
- hidden information;
- reference/canonical comparison;
- headless regresszió.

Az `Aeterna.RuntimeCandidate` státusza:

`ACCEPTED_PROOF`

Nem production authority és nem nevezendő át közvetlenül production motorrá.

Megvalósított határ:

- az `Aeterna.Engine` pure `net8.0` core;
- a Headless és a Godot production bridge ugyanazt az engine authorityt használja;
- a bridge csak boundary/delegáció, gameplay-logika nélkül;
- a publikus event/snapshot projection viewer-safe;
- teljes debug/full-fidelity state és event hozzáférés csak trusted/internal teszt/diagnostic réteg;
- malformed/null boundary input strukturált rejectiont vagy diagnosticot ad.

## 11. TD-011 – Tesztelési minimum

**Státusz:** ELFOGADVA

Minden production gameplay-migrációhoz szükséges:

- hivatalos szabályforrás-ellenőrzés;
- typed contract;
- pozitív és negatív fixture;
- success és rejection teszt;
- rejected action state-immutability;
- request immutability;
- state invariants;
- hidden-information;
- deterministic output;
- canonical SHA;
- Python reference comparison;
- C# candidate regression;
- Godot in-process proof;
- GDScript regresszió;
- Debug és Release build;
- warning/error audit;
- process/listener audit.

A fair AI ugyanazt a player-visible snapshotot és legal action listát használja, mint az emberi játékos.

---

## 12. TD-012 – Production packaging

**Státusz:** NYITOTT, NEM BLOKKOLJA A NYELVI DÖNTÉST

Bizonyítandó:

- Windows Godot .NET export;
- szükséges .NET runtime kezelése;
- self-contained vagy prerequisite modell;
- tiszta tesztgépes indítás;
- egyszerű felhasználói indítás;
- log- és crashcsomag;
- verzió- és runtime package compatibility;
- hosszabb soak teszt.

Normál játék tervezett processztopológiája:

```text
Godot .NET application
    └── C# authoritative engine
```

Python nem kötelező játékosoldali runtime-komponens.

---

## 13. TD-013 – C# formázási megfigyelés

**Státusz:** OBSERVE_ONLY – NON_BLOCKING

A `CsharpMinimalRuntimeProof.cs` összehasonlított változatai logikailag azonosak voltak.

Eltérés:

- 4 szóköz;
- tabulátor.

Döntés:

- most nincs `.editorconfig` módosítás;
- nincs whitespace-only commit;
- ismétlődés esetén egységes szabály készül.

---

## 14. TD-014 – Dokumentumkezelés és verziózás

**Státusz:** ELFOGADVA

Current döntések:

- elsődlegesen meglévő aktív dokumentumot frissítünk;
- új dokumentum csak önálló canonical szerep esetén készül;
- minden aktív dokumentumnak legyen verzióblokkja, dátuma és státusza;
- fájlnévben verziózott current dokumentum ugyanazon fájl frissítésével + rename-jével lép új verzióra;
- korábbi current verziót normál esetben a Git history őrzi;
- verzióemelés önmagában nem indok külön Archive-példányra;
- Archive csak valódi historical/deprecated/replaced szerepre szolgál;
- azonos szerepű párhuzamos current dokumentum nem maradhat;
- nyitott kérdés vagy korábbi döntés nem veszhet el merge/migration során;
- archiválás vagy törlés csak utód- és cross-reference audit után történhet;
- current dokumentációs szinkron targeted patch + diff/consistency review módszerrel történik.

A current dokumentum-governance authority tisztázása:

- a dokumentum-governance, a canonical fájlnév- és verziókezelés current authorityja
  az `AET-DOC-DOCUMENT-GOVERNANCE`;
- a governed dokumentumműveletek current authorityja az
  `AET-DOC-DOCUMENT-UPDATE-WORKFLOW`;
- a TD-014 korábbi, verziózott current fájlnevek verziónkénti rename-jére
  vonatkozó mondata nem current policy;
- a current policy stabil canonical fájlnevet használ, a verziót a dokumentum
  metadata- és tartalomrétege rögzíti, a történeti verziókat a Git history őrzi;
- a canonical materializációt a governed UPDATE/CREATE workflow kontrollálja.

A TD-014 nem második dokumentum-governance authority; a fenti current authority
dokumentumok az irányadók. Az eredeti tartós célok – a párhuzamos current
dokumentumok elkerülése, az információvesztés megelőzése, a Git history
verziómegőrzése, az Archive történeti szerepe és az ellenőrzött
archiválás/törlés – változatlanul érvényesek.

A nagy repository-dokumentációs cleanup már lezárult.

A további dokumentumaudit célzott:

- current authority drift;
- stale roadmap/status;
- régi rules source reference;
- verzió-/cross-reference inkonzisztencia;
- Archive/current szerepzavar.

Nem indul automatikusan új teljes repository-cleanup minden mérföldkőnél.

## 15. TD-015 – AETERNA Document Editor host és governance-integráció

**Státusz:** ELFOGADVA ÉS PROOF-FAL IGAZOLVA
**Döntési dátum:** 2026-10-10

Bizonyító commit:

`c8e7e1854c3e054c8c0f59ba35196ae6d0ffdecd` – `feat: add read-only vscode document extension proof`

Elfogadott döntés:

```text
DOCUMENT_EDITOR_IMPLEMENTATION_APPROACH = EXISTING_EDITOR_PLUS_AETERNA_TOOLING
DOCUMENT_EDITOR_HOST = VISUAL_STUDIO_CODE
DOCUMENT_EDITOR_CUSTOM_COMPONENT = THIN_VSCODE_EXTENSION_FIRST
DOCUMENT_EDITOR_GOVERNANCE_BACKEND = EXISTING_AETERNA_DOCUMENT_WORKFLOW
```

A Visual Studio Code hostdöntése elfogadott. A thin extension AETERNA-specifikus
integrációs réteg, nem második governance engine. A meglévő AETERNA document
workflow marad canonical a validációhoz, planninghez, review-hoz és apply-hoz.
A generált artifact registry az Editor read-only navigációs/adatforrása, nem
válhat writable authorityvá.

A proof jelenlegi read-only foundationje bizonyítja:

- repository detection;
- managed document listing;
- artifact ID, title, canonical path és version inspection;
- managed Markdown dokumentum megnyitását a normál VS Code text editorban;
- Refresh;
- governed workflow `resolve`;
- diagnostics.

Proof evidence:

- TypeScript compile: `PASS`;
- extension unit tests: `9/9 PASS`;
- real repository proof smoke: `PASS`;
- artifact regression: `66/66 PASS`;
- document workflow regression: `86/86 PASS`;
- human VS Code activation/interaction acceptance: `PASS`;
- canonical write path a proofban: `NONE`;
- Git mutation: `NONE`;
- AI integration: `NONE`;
- custom editor: `NONE`;
- webview: `NONE`.

### Editing UX boundary

```text
EDITOR_UI_ARCHITECTURE = NOT_YET_DECIDED
EDITOR_UX_REQUIREMENTS_DISCOVERY = REQUIRED_BEFORE_EDITING_SURFACE_LOCK
NATIVE_MARKDOWN_EDITOR_ROLE = INITIAL_PROOF_BASELINE_NOT_FINAL_CONSTRAINT
CUSTOM_EDITOR = ALLOWED_IF_REQUIREMENTS_JUSTIFY
WEBVIEW = ALLOWED_IF_REQUIREMENTS_JUSTIFY
CUSTOM_METADATA_OR_REVIEW_UI = ALLOWED_IF_REQUIREMENTS_JUSTIFY
FULLY_CUSTOM_STANDALONE_APPLICATION = DEFERRED_UNLESS_PROVEN_NECESSARY
```

A TD-015 nem zárja le a végleges editing surface-t. Meglévő VS Code
képesség vagy kompatibilis plugin/component használható, ha megfelel a
követelményeknek és megőrzi az AETERNA governance-t. Bespoke implementáció nem
előny csak azért, mert bespoke; custom komponens csak valós AETERNA-követelmény
alapján indokolt.

### Authoring- és AI-határ

```text
DOCUMENT_EDITOR_MVP_AI = NOT_REQUIRED
DOCUMENT_EDITOR_AUTHORING = MANUAL_FIRST
AUTHORING_AI_INDEPENDENCE = REQUIRED
DOCUMENT_EDITOR_CONTENT_AI_STRATEGY = PROVIDER_AGNOSTIC
CODEX_IS_DEFAULT_CONTENT_AUTHOR = NO
CODEX_PRIMARY_ROLE = PROGRAMMING_AND_TECHNICAL_VALIDATION
DOCUMENT_EDITOR_MUST_NOT_REQUIRE_CODEX_FOR_AUTHORING = YES
AUTONOMOUS_DOCUMENT_GENERATION = OUT_OF_SCOPE
```

AI provider nincs kiválasztva, és a döntés nem vezet be AI-integrációt.

### Future write-path boundary

```text
human edit/new intent
→ candidate
→ validation
→ deterministic plan/diff/review
→ explicit human approval
→ governed apply
→ Git review
→ human-controlled commit/push
```

A jövőbeli Editor write pathnak meg kell őriznie ezt az elfogadott governed
workflow-t. A canonical fájl közönséges közvetlen mentése nem kezelhető governed
write pathként. A TD-015 ezt a write pathot nem implementálja.

### Development-host boundary

Az Extension Development Host a proof fejlesztési/tesztmechanizmusa volt, nem a
végleges felhasználói indítási vagy disztribúciós modell. A normál használat nem
követelheti meg developer PowerShell parancsok megjegyzését. A pontos
installation/distribution/launch megoldás az Editor UX és implementációs munkára
halasztott; a TD-015 nem választ packaging mechanizmust.

### Újranyitás

A VS Code host/integrációs döntés csak valós implementáció vagy használat során
bizonyított material blocker esetén nyitható újra, például ha:

- a szükséges editing UX nem implementálható biztonságosan VS Code-ban;
- a governed candidate/review/apply flow megkerülése lenne szükséges;
- a local-first működés nem tartható fenn;
- a karbantarthatóság érdemben rosszabbá válik egy alternatívánál;
- a distribution vagy normal-use korlátok a megoldást gyakorlatban
  használhatatlanná teszik;
- valós használat bizonyítja, hogy az elfogadott host nem teljesíti a Document
  Editor specificationt.

A döntés nem nyitható újra pusztán azért, mert fully custom standalone
alkalmazás is készíthető.

---

## 16. Aktuális végrehajtási sorrend

### Lezárt proof és foundation rétegek

- Python reference engine;
- runtime package/Godot alap;
- Python sidecar proof – `COMPLETE_AND_FROZEN`;
- C# in-process proof – `COMPLETE_AND_ACCEPTED`;
- runtime language decision gate;
- C.5A;
- C.5B;
- korábbi production gameplay/ability foundation slice;
- Explicit Phase Foundation v1;
- Reaction / Priority Foundation v1;
- Combat + Pecsét Foundation C0–C6;
- terminal Aeternal / `MatchResult` core.

Current production base:

`0862e1002dbef81ee203852714d377592272a0e9`

Current state:

`COMBAT_AND_SEAL_FOUNDATION_C0_C6 = COMPLETE_AND_ACCEPTED`

### Következő technikai/product gate

`VS1_READINESS_REQUIRED`

Következő major product-facing cél:

`VS1 / M6 – első ténylegesen játszható vertical slice`

Canonical VS1 deckek:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

Current sorrend:

```text
VS1 card/mechanic readiness audit
→ csak tényleges blockerre finite contract
→ C# implementation + regression
→ simple fair AI + match orchestration
→ minimal playable Godot
→ human-vs-AI full match
→ reproducible AI-vs-AI smoke
→ VS1 acceptance
```

Nem programozási aktív sáv továbbra is lehet:

- kártyaadat- és szabályaudit;
- LOOKUPS- és ID-contract munka;
- kártyadizájn-workflow;
- célzott dokumentációs sync.

A főforrás-dokumentumok későbbi szerkezeti újratervezése külön dokumentációs/design feladat,
nem technológiai döntés és nem módosítja ezt a végrehajtási sorrendet.

## 17. Rövid döntési összefoglaló

- A contract-first modell kötelező.
- Egyetlen authoritative state lehet.
- A Godot/GDScript a vizuális kliens és presentation layer.
- A C#/.NET az authoritative production rules runtime.
- A Python külső tooling, AI/batch koordináció és reference/oracle.
- A Python sidecar proof lezárt és befagyasztott.
- A C# in-process proof elfogadott.
- A Godot–C# kapcsolat közvetlen same-process.
- A Python–C# headless JSON/JSONL alapkapcsolat implementált.
- Embedded Python és service API csak későbbi bizonyíték/mérés alapján vizsgálható.
- A Document Editor elfogadott hostja a Visual Studio Code; az AETERNA-specifikus
  réteg thin extension, a canonical backend a meglévő governed document workflow.
- A TD-015 proof-fal igazolt, a végleges editing UI architektúra továbbra sincs
  lezárva.
- C.5B, Explicit Phase, Reaction/Priority és Combat/Pecsét C0–C6 lezárt foundation.
- Current production base:
  `0862e1002dbef81ee203852714d377592272a0e9`.
- Current OQ:
  `52 answered / 15 partly_answered / 7 deferred / 0 open`.
- Következő gate:
  `VS1_READINESS_REQUIRED`.
- Következő major product-facing cél:
  `VS1 / M6 – első ténylegesen játszható vertical slice`.
- A TD-015 formalizálja a proof-fal igazolt Document Editor host- és governance-integrációs döntést.
