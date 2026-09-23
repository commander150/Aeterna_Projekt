---
artifact_id: AET-DOC-PROJECT-PLAN
kind: document
type: project-plan
version: "6.9"
lifecycle: active
integration: current
authority: project-direction
generated: false
depends_on: []
supersedes: []
---

# AETERNA – AKTUÁLIS PROJEKTTERV ÉS PRIORITÁSOK v6.9

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 6.9
**Dátum:** 2026-09-05
**Státusz:** aktív projektirányító és prioritási dokumentum
**Előző aktív verzió:** 6.8 (Git history)
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9` – `engine: add aeternal outcome and terminal match result`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9` – Combat + Pecsét Foundation C0–C6
**Előző technikai checkpoint-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`

Ez a dokumentum az AETERNA projekt aktuális irányát, prioritásait, dokumentumelsőbbségét és a következő biztonságos munkaszakaszokat rögzíti.

Nem teljes repository-inventár, nem szabálykönyv, nem contract-specifikáció és nem Codex-prompt.

---

## 1. Dokumentum- és tényelsőbbség

### 1.1 Játékszabályi kérdésben

Elsődleges authority:

1. `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.5v.docx`;
2. `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4.1v.docx`;
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

Következő tényleges szakmai lépés:

```text
VS1 content/mechanic readiness audit
→ emberi prioritásdöntés
→ szükséges finite contract/programozási slice-ok
→ simple fair AI + minimal playable Godot
→ VS1 end-to-end acceptance
```

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
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.8.md`;
- `Aeterna game engine/README.md`;
- `Aeterna game engine/docs/README.md`;
- `project/status/checkpoints/ENGINE_CHECKPOINT.md`;
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

Current default szerint Codex lokális technikai módosítást és validációt készít, de nem commitol és nem pushol. Külső audit és emberi jóváhagyás után a felhasználó commitol/pushol.

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
**VS1 / M6:** `NEXT MAJOR PRODUCT-FACING GOAL`
**0.0.1:** `ACTIVE_LONG_TERM_TARGET`

## 11. Következő szakmai munkasorrend

1. C0–C6 milestone dokumentációs current-truth sync lezárása;
2. VS1 readiness audit a két canonical VS1 paklira;
3. kártyánként/mechanikánként classification:
   `executable / data issue / engine gap / rules decision / UI-AI dependency / non-blocking future`;
4. emberi prioritásdöntés;
5. csak a tényleges VS1 blockerre finite contract;
6. Codex local implementation + build/test/smoke;
7. külső audit;
8. PASS után felhasználói commit/push;
9. simple fair AI / match orchestration;
10. minimal playable Godot;
11. VS1 end-to-end acceptance;
12. ezután szükséges köztes mérföldkövek a 0.0.1 felé.

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
