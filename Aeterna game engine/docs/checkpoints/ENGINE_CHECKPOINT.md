# AETERNA Game Engine – Engine Checkpoint

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.0
**Dátum:** 2026-09-05
**Státusz:** aktív elsődleges technikai folytatási checkpoint
**Előző aktív verzió:** 1.9 (Git history)
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9` – `engine: add aeternal outcome and terminal match result`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9` – Combat + Pecsét Foundation C0–C6
**Előző checkpoint-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`
**C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`
**Történeti gameplay-foundation span:** `931bf557... -> 2608345b...` = 39 commit

Ez a dokumentum az AETERNA Game Engine biztonságos technikai folytatási pontja. Nem hivatalos játékszabály és nem teljes production engine-specifikáció.

Ha a repository `main` ága később ennél a commitnál előrébb jár, először a Git-történetet, az aktuális production kódot és a hozzá tartozó tesztbizonyítékot kell ellenőrizni. Ez a checkpoint nem írhatja felül a későbbi implementációt.

---

## 1. Elfogadott architektúra

Az elfogadott runtime-architektúra változatlan:

- **Godot/GDScript:** vizuális kliens, UI, input, animáció és adapterréteg.
- **C#/.NET:** az egyetlen production authoritative rules engine.
- **Python:** external tooling, reference/oracle, adatpipeline, AI és batch controller.

A runtime-nyelvi döntési kapu lezárult.

Nem készül új:

- GDScript rules authority;
- production Python-sidecar authority;
- párhuzamos második production rules engine.

A Python-sidecar és a RuntimeCandidate proofok történeti/regressziós bizonyítékként megmaradnak.

---

## 2. Bizonyított proof-folytonosság

### Python reference engine

Státusz:

`REFERENCE_IMPLEMENTATION / COMPARISON_ORACLE`

Bizonyított alapok:

- MatchState és PlayerState;
- state version guard;
- card instance registry;
- deck, hand és történeti discard/Void zónakezelés;
- draw és korábbi end-turn reference flow;
- typed eventek;
- player-visible snapshot;
- hidden-information projection;
- Domain topology és occupancy;
- activity state;
- izolált Wellspring;
- deterministic AI trajectory.

A Python nem production authority.

A reference út szerepe:

- regressziós összehasonlítás;
- fixture/oracle;
- AI/batch és elemzőtooling;
- történeti proof-folytonosság.

### Python–Godot sidecar

Státusz:

`COMPLETE_AND_FROZEN`

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e`

Bizonyította:

- localhost TCP;
- request/response;
- shutdown és emergency shutdown;
- parent watchdog;
- orphan cleanup;
- canonical comparison.

Nem production főmotor.

### C# in-process candidate

Státusz:

`COMPLETE_AND_ACCEPTED`

Proof-bázis:

`8e5ee64e42e1657e10f3413444bb870524ee07f9`

Bizonyította:

- pure C# runtime candidate;
- Godot .NET in-process bridge;
- nincs Python, TCP vagy külön engine-processz;
- draw, stale reject és történeti end-turn proof;
- snapshot, legal action és typed event;
- canonical JSON és SHA;
- 100 futásos determinisztika;
- mutation negative proof;
- Debug és Release;
- headless és visual PASS.

Történeti candidate canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

A RuntimeCandidate proofként megmarad; nem nevezendő át production motorrá.

---

## 3. Production C# engine authority

Aktív projektek:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- `Aeterna.Engine.sln`.

Publikus `EngineSession`-határ:

- `CreateMatch`;
- `GetPlayerSnapshot`;
- `ListLegalActions`;
- `SubmitAction`;
- `GetEvents(string viewerPlayerId, int afterSequence = 0)`;
- `GetMatchResult`.

Alapelvek:

- state mutation csak a C# authorityn keresztül történhet;
- rejected action nem hagyhat részleges state mutationt;
- stale request guard aktív;
- legal actiont a core számolja;
- frontend és AI nem találgathat rules legalityt;
- a teljes, nem redaktált event- és debugállapot internal;
- player-facing snapshot és event viewer-specifikus;
- hidden information nem szivároghat opponent nézetbe;
- a Godot production bridge nem rules authority.

Az Explicit Phase Foundation utáni public `ActionResponse.Events` is a requestet beküldő játékos viewer-identitásával projektált, miközben az internal event store full-fidelity marad.

---

## 4. C.5A és C.5B – lezárt foundation mérföldkövek

### C.5A – Production architecture plan

Státusz:

`COMPLETE_AND_ACCEPTED`

### C.5B – Production Engine Foundation

Státusz:

`COMPLETE_AND_ACCEPTED`

Lezáró commit:

`931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`

Megvalósult eredeti scope:

- pure C# production engine;
- headless host;
- test project;
- typed core contractok;
- `EngineSession`;
- minimum runtime package loader;
- draw;
- stale rejection;
- történeti `end_turn`;
- canonical serializer;
- fixture adapter;
- Godot production bridge;
- RuntimeCandidate és Python reference regresszió.

Az akkori acceptance-bizonyíték:

- production solution Debug és Release: PASS, 0 warning, 0 error;
- production tesztek: Debug `13/13`, Release `13/13`;
- expected és actual canonical SHA: `650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`;
- canonical artifact: `210730` byte;
- determinisztika: `100/100`;
- Godot Debug és ExportRelease: PASS;
- pozitív és negatív production bridge smoke: PASS.

A C.5B checkpoint idején még nem volt production Wellspring, Beáramlás, `play_card`, ability execution, explicit phase engine, reaction vagy combat.

Ez a hiánylista történeti állapot; a következő fejezetek rögzítik, mi készült el azóta.

---

## 5. Korábbi production gameplay foundation slice

A `931bf557... -> 2608345b...` szakasz 39 commit.

### 5.1 Forrás- és canonical adatfrissítés

Megvalósult:

- az alapjáték hivatalos főforrása `1.4.3v` lett;
- `CARDDATABASE.xlsx` bekerült;
- `REGISTRY.xlsx` bekerült;
- canonical workbook export út létrejött/frissült;
- a kártyaadatbázis munkaforrás és runtime data flow tovább fejlődött.

### 5.2 Wellspring / Beáramlás / payment / play

Production C#-ban megvalósult:

- Wellspring state;
- player-visible Wellspring;
- normál Beáramlás (`normal_inflow`);
- egyszer-per-kör Beáramlás guard;
- Magnitúdó-preflight;
- Aura-payment preflight;
- activity state mutation;
- Domain state és placement;
- `play_card`;
- canonical zone transition;
- Void zone.

### 5.3 Canonical card / ability / effect runtime foundation

Megvalósult:

- canonical package loader;
- runtime lookup catalog;
- canonical card catalog;
- runtime binding;
- canonical ability catalog;
- ability-template compiler;
- effect condition evaluator;
- target filter evaluator;
- target resolver;
- trigger resolver;
- effect executor;
- template / collection / zone effect runtime;
- continuous effect state;
- modifier / keyword / duration foundation;
- damage és vitals lifecycle;
- lethal transitionök;
- canonical draw/reference runtime.

Ez production foundation, nem a teljes kártyaállomány teljes ability coverage-e.

---

## 6. Explicit Phase Foundation v1

Lezáró commit:

`2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

Státusz:

`COMPLETE_AND_ACCEPTED`

Canonical phase vocabulary:

1. `awakening` – Ébredés;
2. `infusion` – Beáramlás;
3. `manifestation` – Manifesztáció;
4. `incursion` – Betörés;
5. `distribution` – Eloszlás.

Megvalósult:

- authoritative öt-fázisú turn lifecycle;
- explicit `StartingPlayerId`;
- public `advance_phase`;
- az engine maga választja a következő canonical fázist;
- kliens által megadott tetszőleges célfázis nem része a canonical flow-nak;
- phase-specifikus legal action tér;
- Awakening entry automatikus;
- kezdő játékos első Awakeningje 0 lapot húz;
- későbbi normál Awakening ready + 2 húzás;
- kötelező draw failure atomikus;
- `incursion -> distribution` a turn-end cleanup boundary;
- Distribution külön megfigyelhető canonical state;
- `distribution -> awakening` váltja az aktív játékost;
- public `draw_card` és `end_turn` kivonva a normál production legal action space-ből;
- historical runtime-comparison adapterben a régi reference út izoláltan megmarad;
- pending-trigger gating megmaradt;
- viewer-safe `ActionResponse.Events`;
- Godot production bridge canonical phase flow-ra migrálva.

### Jelenlegi minimum public phase/action flow

**Awakening**
- `advance_phase`

**Infusion**
- `normal_inflow`, ha legális;
- `advance_phase`

**Manifestation**
- `play_card`, ha legális;
- `advance_phase`

**Incursion**
- `attack`, ha current state szerint legális;
- `advance_phase`

**Distribution**
- `advance_phase`

Ez a minimum phase-flow eredetileg Combat nélkül zárult; a Combat + Pecsét Foundation C0–C6 azóta productionben `COMPLETE_AND_ACCEPTED`.

---

## 7. Legutóbbi bizonyított acceptance

Az Explicit Phase Foundation implementáció adversarial auditon, javítási körön és lezáró pre-commit auditon ment át.

Legutóbbi bizonyíték:

- Engine Debug build: PASS, 0 warning, 0 error;
- Engine Debug tests: `222/222 PASS`;
- Engine Release build: PASS, 0 warning, 0 error;
- Engine Release tests: `222/222 PASS`;
- headless oracle/reference: PASS;
- canonical byte count: `210676`;
- actual/expected SHA-256:
  `97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`;
- determinism: `100/100 PASS`;
- Godot C# Debug build: PASS;
- pozitív Godot production smoke: PASS;
- negatív Godot production smoke: PASS;
- `git diff --check`: PASS.

Lezáró audit verdict:

`PASS – READY FOR COMMIT`

A változás ezt követően commitolva és pusholva lett a `main` ágra.

### 7.1 2026-08-15 learning / synthesis / OQ handoff

A production gameplay mérföldkő után három dokumentációs/evidence commit került a `main` ágra:

- `ae7d2841673a800cd73e5dee337c87ce025cf67e` – learning registry + analysis corpus;
- `b0e4d9ded4eeabdc63beb44fd05c6a2b89bcd3dd` – cross-project synthesis + AETERNA blueprints;
- `743c00d85ddc60bbbc70715fefab8ffc9dacbdae` – Open Questions v2.2 szinkron.

A 2026-08-15-i evidence/admin snapshot:

```text
59 registry project record
58 current local source
30 project analysis

50 answered
17 partly_answered
7 deferred
0 open
74 total
```

A learning/synthesis/blueprint réteg nem rules authority.
A fenti commitok akkor nem módosították a production gameplay kódot;
ez a mondat a 2026-08-15-i történeti handoff állapotát rögzíti, nem a current HEAD-et.

---

### 7.2 Reaction / Priority Foundation v1

Lezáró production commit:

`f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`

Státusz:

`COMPLETE_AND_ACCEPTED`

Productionben aktív többek között:

- authoritative `ReactionWindow`;
- `react` / `pass_priority`;
- canonical resolution stack;
- LIFO;
- RC1;
- RC2 queued-trigger checkpoint/FIFO;
- viewer-safe pending projection.

Acceptance:

- Debug/Release `246/246 PASS`;
- determinism `100/100 PASS`;
- oracle/reference PASS;
- Python isolated `465/465 PASS` + 5 skip;
- Godot C# build + positive/negative smoke PASS;
- unresolved P0/P1: `0/0`.

### 7.3 Combat + Pecsét Foundation C0–C6

Rules migration:

`61ad2605dd1aa3d7ea95444f0bb66cebf819014e`

Production slice-ok:

- `ca55bc3714de2692753fccc18a8f11d9dac1beea` – C0 setup + Seal foundation;
- `558d4453a1604c0ebe76065df08a207192c21c8b` – C1+C2 attack + első Combat ReactionWindow;
- `d236f0e3c36994f65e7d00d25972660baac2a842` – C3 intervention + DefenseCommit;
- `68b07dd6906fc8c37245325a855322d48f5f2635` – C4 Entity Combat;
- `d30f8a4c42383a0200e416acb7148facc3bbbc11` – C5 SealBreak + Surge + Gondviselés;
- `0862e1002dbef81ee203852714d377592272a0e9` – C6 Aeternal + terminal MatchResult.

Státusz:

`COMBAT_AND_SEAL_FOUNDATION_C0_C6 = COMPLETE_AND_ACCEPTED`

Current production core:

- canonical setup + Jóslat;
- hat stabil Pecsét-slot és viewer-safe visibility;
- `attack` / AttackCommit;
- intervention / DefenseCommit;
- két Combat ReactionWindow;
- Entity Combat simultaneous damage;
- SealBreak / public reveal / Surge;
- Gondviselés Surge opportunity;
- Aeternal outcome;
- authoritative terminal `MatchResult v2`.

Final acceptance:

- Debug/Release C#: `301/301 PASS`;
- targeted C6: `8/8 PASS`;
- determinism/reference: `100/100 PASS`;
- canonical byte count: `210676`;
- canonical SHA:
  `97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`;
- Python isolated regression: `465/465 PASS`, `5 skip`;
- exporter: `23/23 PASS`;
- Godot C# consumer build + positive/negative smoke: PASS;
- `git diff --check`: PASS;
- unresolved P0/P1: `0/0`.

---

## 8. Megőrzendő technikai invariánsok

A további fejlesztés nem törheti meg:

- C# authoritative state ownership;
- state-version és stale-request guard;
- rejected action atomicitás;
- deterministic transition és event ordering;
- viewer-safe snapshot;
- viewer-safe public event projection;
- internal full-fidelity event store;
- hidden-information védelem;
- canonical zone transition szemantika;
- `EnteredDomainTurnNumber` jelentése;
- continuous effect és modifier/keyword/duration lifecycle;
- Distribution turn-end cleanup boundary;
- Python reference és RuntimeCandidate regressziós proof-folytonossága;
- Godot kliens / engine authority szétválasztása.

A runtime-nyelvi döntést és a C.5B foundation scope-ját nem kell újranyitni általános refaktorral.

Ezek current `FOUNDATION_GUARDRAIL` jellegű elvek:
bizonyított playtest/Expansion/meta/design/architecture szükség esetén
explicit redesign + impact analysis + migration + regression mellett módosíthatók,
de néma vagy implicit drift nem megengedett.

---

## 9. Aktuális forrás- és dokumentumelsőbbség

### 9.1 Játékszabályi kérdésben

1. `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.5v.docx`;
2. `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4.1v.docx`;
3. explicit, verziózott emberi döntés;
4. `OPEN_QUESTIONS_DECISIONS.md`;
5. aktív contract/specification;
6. implementáció és teszt mint technikai bizonyíték.

A kód nem írhatja felül a hivatalos szabályt.

### 9.2 Projektirány és technikai folytatás

1. jelen `ENGINE_CHECKPOINT.md`;
2. aktuális `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK`;
3. aktuális `PROJEKT_TERKEP_ES_FAJLSTATUSZ`;
4. `ARCHITECTURE.md` és `TECHNOLOGY_DECISIONS.md`;
5. aktuális status- és contractdokumentumok;
6. `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md`;
7. `CHECKPOINTS.md` történeti napló;
8. történeti proofok és archívum.

A `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md` a hosszabb távú első zárt, játszható termékcél; nem napi technikai tasklista.

---

## 10. Jelenlegi fő hiányok és döntési kapuk

C0–C6 után már productionben aktív:

- Reaction / Priority;
- attack / intervention / DefenseCommit;
- Entity Combat;
- Pecsét core state/visibility;
- SealBreak / reveal / Surge;
- Gondviselés;
- Aeternal terminal victory;
- authoritative `MatchResult v2`.

Továbbra sem teljes többek között:

- Refresh Penalty;
- generic prevention/replacement;
- compound non-reaction choice;
- speciális timing/activation-policy kivételek;
- teljes ability/content coverage;
- special Seal restore/ward-effect runtime;
- Hasítás runtime;
- full Burst/Jel runtime;
- replay runner;
- production AI-vs-AI orchestration;
- final Windows packaging;
- teljes player UI.

Ezek közül nem mind VS1-blocker.

### OQ-SNAP-002 – Pecsét

Státusz: `answered`.

Exact current Seal visibility/snapshot core C0–C6-ban lezárt:

- playerenként 6 stabil public slot;
- lane + `standing|broken` public;
- standing Seal identity owner előtt is hidden;
- break után public reveal;
- Surge után hand identity ismét viewer-private;
- reveal history public marad.

### OQ-LA-003 – Combat

Státusz: `answered`.

Production action/event/pending-state/Reaction integration C0–C6-ban lezárt.

### Továbbra is részleges kapuk

Többek között:

- `OQ-SNAP-005`: generic compound target/payment/choice, cancel/back, nested non-Reaction decision;
- `OQ-LA-002`: generic prevention/replacement, complex nested choice, future special timing;
- `OQ-ABIL-004`: generic prevention/choice ability-level extension;
- `OQ-ABIL-006`: ability/ward targeting + restore/payload;
- `OQ-RULES-007`: special Seal restore/ward és további Expansion-interakciók.

Current OQ aggregate:

`52 answered / 15 partly_answered / 7 deferred / 0 open`.

## 11. Dokumentációs és repository-folytonosság

A korábbi dokumentációs archív rendezés lezáró commitja:

`66a206c6e3bf9155fb9f71a354236fb5b6ab3b90`

Elkészült többek között:

- régi projekttervek és projekt-térképek archiválása;
- régi Python-backend és effect/trigger anyagok archiválása;
- történeti újratervezési réteg rendezése;
- régi adataudit- és exportanyagok archiválása;
- object identity / zone move történeti tervek rendezése.

A `2608345b...` mérföldkőhöz tartozó célzott active-document consistency pass 2026-08-14-én tartalmilag lezárult.

A pass összehangolta:

- projektirányító dokumentumokat;
- checkpoint-indexet és checkpointnaplót;
- aktív README-ket;
- status/contract dokumentumokat;
- Open Questions és ability/runtime státuszt;
- architecture és runtime-package státuszt.

Történeti proofdokumentumokat nem írtunk át pusztán az új HEAD miatt.

A repository-dokumentáció továbbra sem kap tömeges frissítést minden kisebb commit után.

A 2026-08-15-i learning/synthesis/OQ handoff után history-recovery audit indult,
mert a korábbi teljes dokumentum-újragenerálásoknál érvényes tartalom is elveszhetett.
Current dokumentációs szabály:

```text
committed current file
→ Git/Archive history comparison
→ targeted edit
→ GitHub Desktop diff review
```

Aktív checkpoint/status/decision dokumentumot nem generálunk újra nulláról
alapértelmezésben.

## 12. Biztonságos folytatási utasítás

Új beszélgetés vagy hosszabb megszakítás után:

1. ellenőrizd a repository aktuális `main` HEAD-jét;
2. olvasd el ezt a checkpointot;
3. olvasd el az aktuális projekttervet és projekt-térképet;
4. olvasd el az `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md` aktuális párt;
5. rules kérdésben Core `1.5v` + Expansion `1.4.1v` authority-ból indulj;
6. ne nyisd újra automatikusan a runtime-nyelvi döntést;
7. Python sidecar = `COMPLETE_AND_FROZEN` proof;
8. C# RuntimeCandidate = `COMPLETE_AND_ACCEPTED` proof;
9. C.5B = lezárt foundation;
10. a `931bf... -> 2608345b...` szakaszt korábbi production gameplay foundation slice-ként kezeld, ne current VS1-ként;
11. Explicit Phase Foundation v1 = `COMPLETE_AND_ACCEPTED`;
12. Reaction / Priority Foundation v1 = `COMPLETE_AND_ACCEPTED`;
13. Combat + Pecsét Foundation C0–C6 = `COMPLETE_AND_ACCEPTED`;
14. learning/synthesis/blueprint = evidence/proposal, nem rules authority;
15. Archive = történeti bizonyíték, nem automatikus recovery source;
16. repository `TEMP/` = `DISPOSABLE_WORKSPACE`;
17. current következő major product-facing cél = VS1 / M6;
18. VS1 előtt ne implementálj future capabilityt pusztán azért, mert egyszer majd kellhet;
19. előbb a két canonical VS1 deck readiness auditja szükséges;
20. új gameplay szabályt a kód ne találjon ki;
21. current default csak explicit reviewed emberi döntéssel módosítható.

## 13. Következő biztonságos technikai lépés

**VS1 / M6 readiness audit**

Előfeltétel:

- Reaction / Priority Foundation v1: `COMPLETE_AND_ACCEPTED`;
- Combat + Pecsét Foundation C0–C6: `COMPLETE_AND_ACCEPTED`;
- terminal victory core: `COMPLETE_AND_ACCEPTED`.

Canonical VS1 deckek:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

Audit-output card/mechanic szinten:

```text
executable now
data issue
engine gap
rules decision required
UI/AI dependency
non-blocking future feature
```

Csak a tényleges VS1 blockerből készül következő finite contract és Codex slice.

Current sequence:

```text
VS1 readiness audit
→ emberi scope/prioritásdöntés
→ required finite engine/content slice
→ simple fair AI / match orchestration
→ minimal playable Godot client
→ human-vs-AI + reproducible AI-vs-AI smoke
→ VS1 end-to-end acceptance
```

Refresh Penalty, Hasítás, prevention/replacement vagy más future mechanika csak akkor
kerül VS1 elé, ha a readiness audit tényleges blockerként azonosítja.

Known follow-up:
a `resolution → void` played-card event Visszhang/full keyword coveragehez
később canonical trigger-source integrációt igényel.

## 14. Rövid aktuális összefoglaló

- Szinkronizációs repository-bázis: `0862e1002dbef81ee203852714d377592272a0e9`.
- Production engine mérföldkő: `0862e1002dbef81ee203852714d377592272a0e9`.
- Python reference: aktív comparison oracle/tooling.
- Python sidecar: `COMPLETE_AND_FROZEN`.
- C# RuntimeCandidate proof: `COMPLETE_AND_ACCEPTED`.
- C.5A: `COMPLETE_AND_ACCEPTED`.
- C.5B: `COMPLETE_AND_ACCEPTED`.
- Korábbi production gameplay foundation slice: `COMPLETE_AND_ACCEPTED`.
- Canonical ability/effect runtime foundation: aktív és tovább bővítendő.
- Explicit Phase Foundation v1: `COMPLETE_AND_ACCEPTED`.
- Reaction / Priority Foundation v1: `COMPLETE_AND_ACCEPTED`.
- Combat + Pecsét Foundation C0–C6: `COMPLETE_AND_ACCEPTED`.
- Production tesztállapot: Debug/Release `301/301 PASS`.
- Determinism/reference: `100/100 PASS`.
- Godot production bridge smoke: PASS.
- Learning registry: `59 registry / 58 local`.
- Project analyses: `30`.
- Synthesis/blueprint program: `COMMITTED`.
- OQ: `52 answered / 15 partly_answered / 7 deferred / 0 open`.
- Current következő major goal: VS1 / M6 readiness.
- 0.0.1: active long-term product target.
