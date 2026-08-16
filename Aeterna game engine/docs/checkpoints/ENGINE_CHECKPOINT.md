# AETERNA Game Engine – Engine Checkpoint

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.7
**Dátum:** 2026-08-16
**Státusz:** aktív elsődleges technikai folytatási checkpoint
**Felváltott verzió:** `ENGINE_CHECKPOINT.md` 1.6
**Szinkronizációs repository-bázis:** `743c00d85ddc60bbbc70715fefab8ffc9dacbdae` – `docs: synchronize open questions and current decisions`
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`
**Előző checkpoint-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`
**C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`
**Előrelépés a C.5B checkpoint-bázishoz képest a production engine mérföldkőig:** 39 commit

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

## 5. Az előző checkpoint óta elkészült production gameplay vertical slice

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
- `advance_phase`

**Distribution**
- `advance_phase`

Combat még nincs productionben.

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

Aktuális evidence/admin állapot:

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
A fenti commitok nem módosították a production gameplay kódot,
ezért a legutóbbi production acceptance továbbra is a `2608345b...` mérföldkőhöz tartozik.

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

1. `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4.3v.docx`;
2. `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`;
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

Még nincs teljes production:

- Reaction / Priority runtime;
- combat;
- attack/block;
- Pecsétfeltörés;
- teljes Pecsét state/visibility;
- Refresh Penalty;
- teljes compound pending choice/reaction modell;
- generic prevention/replacement runtime;
- speciális timing/activation-policy kivételek;
- teljes ability coverage;
- victory/defeat lifecycle;
- replay runner;
- production AI-vs-AI;
- final Windows packaging;
- teljes player UI.

### OQ-SNAP-002 – Pecsét

Státusz: `partly_answered`.

Az official Core már rögzíti többek között:

- 6 face-down Pecsét;
- standing/broken állapot;
- Áramlatkapcsolat;
- break/reveal/Surge;
- Aeternal támadhatóságát 0 álló Pecsét mellett.

Fennmaradó digitális gate:

- exact visibility;
- snapshot schema;
- special interaction/event payload.

### OQ-LA-003 – Combat

Státusz: `partly_answered`.

Az official Core már rögzíti többek között:

- attack eligibility;
- attacker Exhaust;
- target declaration;
- Oltalom-priority;
- block;
- simultaneous damage;
- Pecsét break/Surge;
- Aeternal direkt győzelmi alapot.

Fennmaradó production gate:

- action/event/pending-state contract;
- Reaction integráció.

### Reaction / Priority

A source audit és OQ-frissítés elkészült.

Official/current alap:

- event-specific reaction window;
- non-initiator first, ha mindkét játékos eligible;
- pass;
- két egymást követő passz zárja a két-player windowt;
- nested reactions;
- LIFO resolution;
- final revalidation;
- lezárt esemény nem nyílik vissza;
- simultaneous trigger ordering official;
- mandatory/optional trigger semantics official.

Current defaults:

```text
react
pass_priority
reaction_option_id
response_policy_id
MatchState-owned reaction state
pending_decision_summary projection
```

RC1:
single eligible responder passza azonnal zárja az adott windowt.

RC2 ordinary trigger:
immediate discovery/creation → queued trigger → current cycle unwind →
post-resolution trigger checkpoint.

Different-timing batch:
chronological FIFO by originating committed-event sequence.

Reserved extension:
`strict_event_window`, delayed/immediate special timing és további activation/order policy.

Fennmaradó v1 contract-gate:

- exact state/stack mezők;
- pass counter/reset;
- event/correlation;
- exact viewer-safe projection;
- final revalidation result behavior;
- unsupported path.

---

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
5. szabályi kérdésben az aktuális hivatalos főforrásból indulj;
6. ne nyisd újra automatikusan a runtime-nyelvi döntést;
7. a Python sidecart tekintsd `COMPLETE_AND_FROZEN` proofnak;
8. a C# RuntimeCandidate-et tekintsd `COMPLETE_AND_ACCEPTED` proofnak;
9. a C.5B production foundationt tekintsd lezárt mérföldkőnek;
10. a `931bf... -> 2608345b...` gameplay vertical slice-t tekintsd elkészült production alapnak;
11. az Explicit Phase Foundation v1-et tekintsd `COMPLETE_AND_ACCEPTED` állapotúnak;
12. a learning/synthesis/blueprint réteget evidence/proposal layerként kezeld, ne rules authorityként;
13. az OQ A0–A4 teljes auditját új bizonyíték nélkül ne ismételd meg;
14. generic simultaneous trigger orderinget és mandatory/optional trigger semanticsot ne nyisd újra;
15. Reaction implementation még nem indult;
16. a következő engine-lépés a minimal Reaction/Priority v1 contract finalizálása;
17. combatot ne implementáld az első Reaction v1 slice részeként;
18. Refresh Penaltyt ne találd ki technikai placeholderként;
19. a RuntimeCandidate és Python reference regressziós proof maradjon meg;
20. új gameplay szabályt a kód ne találjon ki;
21. current default csak explicit reviewed döntéssel módosítható.

---

## 13. Következő biztonságos technikai lépés

**Reaction / Priority Foundation v1 – minimal production contract finalizálás**

A rules/source/OQ/research előkészítés már elkészült.

A contractnak current v1-re explicit módon rögzítenie kell:

1. `ReactionWindowState` minimum contract;
2. `ResolutionStackEntry` minimum contract;
3. eligible responder/current priority;
4. `react`;
5. `pass_priority`;
6. `reaction_option_id`;
7. `response_policy_id`;
8. RC1 single-responder closure;
9. two-player pass lifecycle;
10. LIFO resolution;
11. final revalidation;
12. RC2 ordinary trigger queue;
13. post-resolution trigger checkpoint;
14. different-timing FIFO batch default;
15. event/correlation és viewer-safe projection;
16. unsupported/non-goal behavior.

Az első slice-ba nem kerül:

- combat;
- attack/block;
- teljes Pecsétmodell;
- Refresh Penalty;
- generic prevention/replacement;
- teljes compound choice framework;
- every future timing policy;
- általános architecture rewrite.

A contract consistency review után:
Codex implementation → Debug/Release tests → determinism/reference/Godot smoke →
adversarial audit → PASS → felhasználói commit/push.

---

## 14. Rövid aktuális összefoglaló

- Szinkronizációs repository-bázis: `743c00d85ddc60bbbc70715fefab8ffc9dacbdae`.
- Production engine mérföldkő: `2608345b61526097fc0b118f05461f92cfed0a95`.
- Python reference: aktív comparison oracle/tooling.
- Python sidecar: `COMPLETE_AND_FROZEN`.
- C# RuntimeCandidate proof: `COMPLETE_AND_ACCEPTED`.
- C.5A: `COMPLETE_AND_ACCEPTED`.
- C.5B: `COMPLETE_AND_ACCEPTED`.
- Első production gameplay vertical slice: elkészült.
- Canonical ability/effect runtime foundation: elkészült és tovább bővítendő.
- Explicit Phase Foundation v1: `COMPLETE_AND_ACCEPTED`.
- Production tesztállapot: Debug/Release `222/222 PASS`.
- Godot production bridge smoke: PASS.
- Learning registry: `59 registry / 58 local`.
- Project analyses: `30`.
- Synthesis/blueprint program: `COMMITTED`.
- OQ: `50 answered / 17 partly_answered / 7 deferred / 0 open`.
- Reaction source/OQ/research preparation: `COMPLETE_FOR_V1_CONTRACT_DRAFTING`.
- Reaction implementation: `NOT_STARTED`.
- Következő engine-fókusz: Reaction / Priority minimal v1 contract finalizálás.
- Combat: külön későbbi implementation slice.
