# AETERNA – AKTUÁLIS PROJEKTTERV ÉS PRIORITÁSOK v6.6

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 6.6
**Dátum:** 2026-08-16
**Státusz:** aktív projektirányító és prioritási dokumentum
**Felváltott dokumentum:** `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.5.md`
**Szinkronizációs repository-bázis:** `14e315d3f04f5baddb547dcb767c8b156b02551f` – `docs: recover governance and sync current engine decisions`
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`
**Előző technikai checkpoint-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`

Ez a dokumentum az AETERNA projekt aktuális irányát, prioritásait, dokumentumelsőbbségét és a következő biztonságos munkaszakaszokat rögzíti.

Nem teljes repository-inventár, nem szabálykönyv, nem contract-specifikáció és nem Codex-prompt.

---

## 1. Dokumentum- és tényelsőbbség

### 1.1 Játékszabályi kérdésben

Elsődleges authority:

1. `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4.3v.docx`;
2. `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`;
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
2. `Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`;
3. `PROJEKT_TERKEP_ES_FAJLSTATUSZ` aktuális verziója;
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

A `DECISION_MAP.md` helyreállított governance-elve alapján:

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
- Wellspring;
- Beáramlás;
- Magnitúdó- és Aura-preflight;
- Domain és egyszerű `play_card`;
- canonical card/runtime binding;
- canonical ability/effect execution foundation;
- damage/vitals;
- continuous effects;
- modifier/keyword/duration foundation;
- draw/reference runtime;
- explicit öt-fázisú turn lifecycle;
- Godot production bridge és smoke foundation.

### RÉSZLEGES / TOVÁBB BŐVÍTENDŐ

- ability coverage a teljes kártyaállományra;
- target/choice komplexebb pending modell;
- trigger-sorrend;
- temporary/alternate payment;
- diagnostics és release support policy;
- player-facing UI;
- AI/headless orchestration;
- replay-előkészítés.

### NINCS MÉG TELJES PRODUCTION IMPLEMENTÁCIÓ

- teljes Reaction / Priority runtime;
- combat / attack / block / Pecsétfeltörés;
- teljes Pecsét state- és visibility-modell;
- Refresh Penalty;
- teljes victory/defeat lifecycle;
- production AI-vs-AI;
- replay runner;
- végleges Windows packaging;
- teljes player UI.

---

## 5. Következő biztonságos engine-szakasz

### Reaction / Priority Foundation v1 – MINIMAL CONTRACT FINALIZATION

**Státusz:** `NEXT – HUMAN/ASSISTANT CONTRACT WORK FIRST`

A v1-hez szükséges source/OQ/research előkészítés elkészült: official 1.4.3v audit, OQ A0–A4, OQ v2.2, Reaction/Priority blueprint és cross-engine clean-room research.

Current technical default:

```text
react
pass_priority
reaction_option_id
response_policy_id
MatchState-owned reaction state
viewer-safe pending_decision_summary
```

RC1: egy eligible responder passza lezárja az adott reaction windowt.

RC2: ordinary trigger az eventnél létrejön/felfedeződik, queue-ba kerül, a jelenlegi resolution cycle kifut, majd post-resolution trigger checkpointnál kerül feldolgozásra.

Different-timing batch current default: chronological FIFO by originating committed-event sequence. Same-timing batch: official simultaneous ordering.

A minimal v1 contractban még pontosítandó a ReactionWindow/ResolutionStack minimum contract, priority/eligibility, pass-reset, event/correlation, viewer-safe projection, final revalidation és unsupported paths.

Csak az elfogadott contract után indul production C# implementáció. Combat, teljes Pecsétmodell, Refresh Penalty, generic prevention/replacement és every-future-timing-policy nincs ebben az első slice-ban.

---

## 6. Aktuális döntési kapuk és Open Questions

OQ v2.2: `50 answered / 17 partly_answered / 7 deferred / 0 open` (74 total).

Az `answered` current canonical/default választ jelent, nem örök megváltoztathatatlanságot.

### OQ-SNAP-002 – Pecsétmodell

`partly_answered`. Official Core már rögzíti a 6 face-down Pecsét, standing/broken, break/reveal/Surge és Aeternal-védelem alapját. Fennmaradó digitális gate: exact visibility, snapshot schema, special interaction/event payload.

### OQ-LA-003 – Combat actionök

`partly_answered`. Official Core már rögzíti az attack eligibility, attacker Exhaust, target declaration, block, simultaneous damage és Pecsét break/Surge alapot. Fennmaradó production gate: action/event/pending-state contract és Reaction integráció.

### Reaction

Nem nyitandó újra általános kérdésként a simultaneous trigger ordering és a mandatory/optional trigger semantics. A fennmaradó v1 contractmunka az 5. fejezetben szerepel.

### Refresh Penalty

Külön későbbi rules/implementation slice; a production draw runtime nem találhat ki placeholder-szabályt.

---

## 7. Dokumentációs konzisztencia-helyreállítás

**Státusz:** `COMPLETE`

A `2608345b...` mérföldkőhöz tartozó célzott aktív dokumentációs consistency pass 2026-08-14-én elkészült.

### A kör – projektirány és checkpoint

Frissítve és összehangolva:

- root `README.md`;
- `Aeterna dokumentációk/README.md`;
- jelen projektterv v6.5;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.8.md`;
- `Aeterna game engine/README.md`;
- `Aeterna game engine/docs/README.md`;
- `checkpoints/ENGINE_CHECKPOINT.md`;
- `checkpoints/CHECKPOINTS.md`;
- `checkpoints/README.md`;
- `DECISION_MAP.md`;
- `PROTOTYPE_STATUS.md`.

### B kör – contract, runtime és OQ konzisztencia

Frissítve és összehangolva:

- `CONTRACT_STATUS.md`;
- `CONTRACT_SPECIFICATION.md`;
- `RUNTIME_PACKAGE_STATUS.md`;
- `RUNTIME_PACKAGE_SPECIFICATION.md`;
- `ABILITY_MODULE_SYSTEM.md`;
- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`;
- `ARCHITECTURE.md`.

### Tudatosan nem frissített történeti/lezárt proofok

Megmarad:

- `PROTOTYPE_PLANS.md`;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`;
- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`;
- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`.

A `TECHNOLOGY_DECISIONS.md` továbbra is csak valódi technológiai döntés változásakor kap új verziót.

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

---

## 9. Párhuzamos nem programozási prioritások

Továbbra is aktív:

1. kártyaadat- és szabályaudit;
2. LOOKUPS- és ID-contract munka;
3. kártyadizájn- és vizuális workflow;
4. learning projektek célzott clean-room vizsgálata, amikor közvetlenül segít egy következő AETERNA-döntésben.

A learning projekt nem szabályforrás és nem közvetlen kódforrás.

---

## 10. Rövid aktuális állapot

**Szinkronizációs repository-bázis:** `14e315d3f04f5baddb547dcb767c8b156b02551f`
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95`
**Production authority:** C#/.NET
**Visual client:** Godot/GDScript
**External tooling/reference:** Python
**C.5B foundation:** `COMPLETE_AND_ACCEPTED`
**Első production gameplay vertical slice:** `COMPLETE_AND_ACCEPTED`
**Explicit Phase Foundation v1:** `COMPLETE_AND_ACCEPTED`
**Learning registry:** `59 registry / 58 local`
**Project analyses:** `30`
**Synthesis/blueprint program:** `COMMITTED`
**Open Questions:** `50 answered / 17 partly_answered / 7 deferred / 0 open`
**Reaction preparation:** `COMPLETE_FOR_V1_CONTRACT_DRAFTING`
**Reaction implementation:** `NOT_STARTED`
**Következő engine-fókusz:** Reaction / Priority minimal v1 contract finalizálás
**Combat:** külön későbbi implementation slice

---

## 11. Következő szakmai munkasorrend

1. Reaction / Priority minimal v1 contract véglegesítése;
2. contract ↔ OQ ↔ blueprint consistency review;
3. explicit non-goals és unsupported paths;
4. csak ezután Codex production C# implementation;
5. Debug/Release teszt, determinism/reference és Godot smoke;
6. adversarial audit;
7. PASS után felhasználói commit/push;
8. következő production mérföldkőnél checkpoint-frissítés;
9. ezután külön Combat rules/contract slice.

Combat, Pecsét és Refresh Penalty külön későbbi rules/contract kapu marad. További learning/source bővítés csak konkrét AETERNA-döntési igény esetén szükséges.

A dokumentációt nem kell minden kisebb technikai commit után tömegesen frissíteni.
