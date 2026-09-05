# AETERNA Game Engine – Decision Map

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 3.1
**Dátum:** 2026-09-05
**Státusz:** aktív rövid döntési és iránytérkép
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9` – `engine: add aeternal outcome and terminal match result`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9` – Combat + Pecsét Foundation C0–C6

Ez a dokumentum röviden rögzíti:

- mi biztosan eldöntött;
- mi a működő referencia;
- mi a production runtime;
- mi lezárt, nyitott vagy elhalasztott;
- mi a következő fejlesztési sorrend;
- mit nem szabad összekeverni.

Kapcsolódó aktív dokumentumok:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `TECHNOLOGY_DECISIONS.md`
- `ARCHITECTURE.md`
- `PROTOTYPE_STATUS.md`
- `CONTRACT_STATUS.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `checkpoints/ENGINE_CHECKPOINT.md`
- `../../Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.9.md`

---

## 1. Biztos projektcél

Az AETERNA elsődlegesen fizikai TCG.

A digitális programegység célja:

- szabálymodellezés és tesztelés;
- programbiztos kártyaadat;
- determinisztikus meccsfuttatás;
- AI-vs-AI;
- későbbi ember–AI játék;
- Godot-alapú kliens;
- 0.0.1 zárt tesztkiadás.

A digitális rendszer nem írhatja felül a hivatalos szabályforrást emberi döntés nélkül.

### 1.1 Playtest, Expansion és szabályfelülvizsgálat

Ez az elv történetileg már a Decision Map korábbi v2.3/v2.5 változatában is szerepelt,
és továbbra is érvényes.

Projektirányítási szabály:

- az elfogadott döntés az aktuális rulesetben canonical/current default;
- az engine, AI és tesztek ezt kötelesek követni;
- a „playtestre vár” vagy „később bővíthető” megjelölés nem teszi a current szabályt opcionálissá;
- szabályhű playtest, Expansion-követelmény, meta vagy bizonyított design/architecture probléma alapján
  bármely szabály, számérték, identitás vagy akár foundation-szintű döntés felülvizsgálható;
- új bizonyíték önmagában nem módosít automatikusan szabályt;
- változtatáshoz explicit emberi döntés, hatásvizsgálat és szükség esetén migration/regression kell;
- a korábbi döntés, a bizonyíték és a módosítás indoka visszakereshető marad;
- stabil engine-contract csak az új canonical/current-default döntés elfogadása után módosítható.

Változási kapcsolatként használható:

```text
EXTENDED
SCOPED
SUPERSEDED
REPLACED
```

Az `answered` Open Question ezért current canonical/default választ jelent,
nem örök megváltoztathatatlanságot.

---

## 2. Végleges technológiai irány

### Godot/GDScript
`VISUAL_CLIENT`

### C#/.NET
`SOLE_PRODUCTION_RULES_AUTHORITY`

### Python
`EXTERNAL_TOOLING_REFERENCE_ORACLE`

A Python nem második production authority.

---

## 3. Runtime proofok lezárt státusza

### Python sidecar
`COMPLETE_AND_FROZEN`

Lezáró commit:
`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e`

### C# RuntimeCandidate
`COMPLETE_AND_ACCEPTED`

Lezáró commit:
`8e5ee64e42e1657e10f3413444bb870524ee07f9`

Történeti canonical SHA:
`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

### GDScript authoritative runtime
`REJECTED_AS_PRODUCTION_AUTHORITY`

### Embedded Python
`RESEARCH_ONLY_DEFERRED`

---

## 4. Stabil contract-first döntések

Elfogadott:

- előbb contract, utána implementáció;
- egy futásban egy authoritative state;
- frontend és AI nem találgat legalitást;
- kliens action requestet küld;
- engine validál és transitiont hajt végre;
- player-visible és debug projection külön;
- hidden information védett;
- mutation atomikus;
- rejected action nem mutál state-et;
- typed event és state version determinisztikus;
- runtime package statikus programadat.

---

## 5. Működő referencia

A Python minimal engine:

- reference implementation;
- comparison oracle;
- regressziós alap;
- AI/batch kutatási forrás.

A C# RuntimeCandidate:

- történeti accepted proof;
- regressziós bizonyíték.

A production authority:

- `Aeterna.Engine`.

---

## 6. Lezárt production mérföldkövek

### C.5A
`COMPLETE_AND_ACCEPTED`

### C.5B
`COMPLETE_AND_ACCEPTED`

Lezáró commit:
`931bf5571d541c752aa421a9f0626768bd8ffbe7`

### Korábbi production gameplay foundation slice
`COMPLETE_AND_ACCEPTED`

Megvalósult többek között:

- Wellspring;
- Beáramlás;
- Magnitúdó;
- Aura-payment;
- activity;
- Domain;
- `play_card`;
- canonical card/runtime binding;
- ability/effect execution foundation;
- damage/vitals;
- continuous effects;
- modifier/keyword/duration;
- draw/reference runtime.

### Explicit Phase Foundation v1
`COMPLETE_AND_ACCEPTED`

Lezáró commit:
`2608345b61526097fc0b118f05461f92cfed0a95`

Production fázisok:
`awakening -> infusion -> manifestation -> incursion -> distribution`

Public progression:
`advance_phase`

---

## 7. Reaction / Priority Foundation v1

**Lezáró production commit:** `f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`
**Acceptance:** Debug/Release `246/246 PASS`; determinism `100/100`; oracle + Godot smoke PASS; external re-audit PASS.

**Reaction contract:** `REACTION_PRIORITY_CONTRACT.md` v1.2 – `COMPLETE_AND_ACCEPTED`

**Státusz:** `COMPLETE_AND_ACCEPTED`

A source/OQ/research előkészítés ehhez a v1 slice-hoz már megtörtént:

- hivatalos `1.4.3v` reaction/timing audit;
- OQ A0–A4 felülvizsgálat;
- `OPEN_QUESTIONS.md` v2.2 + `OPEN_QUESTIONS_DECISIONS.md` v2.3;
- Reaction/Priority blueprint és cross-engine clean-room research.

Hivatalos/current alap:

- csak meghatározott esemény nyit reaction windowt;
- ha mindkét játékos eligible, a non-initiator kapja az első lehetőséget;
- pass;
- két egymást követő passz zárja a két-player windowt;
- reakciók egymásra épülhetnek;
- LIFO feloldás;
- resolution-time target/condition/source revalidation;
- lezárt eseményre nincs visszamenőleges reakció;
- simultaneous trigger ordering általános szabálya official;
- mandatory/optional trigger semantics official.

Current technical default:

```text
react
pass_priority
engine-issued reaction_option_id
typed response_policy_id
authoritative reaction state in MatchState
viewer-safe pending_decision_summary
```

Played Ige / egyszeri Rituálé current lifecycle:

```text
hand
→ shared `resolution` zone
→ own resolution attempt
→ void
```

- a fizikai „Feloldási Sáv” csak munkanév, nem végleges elnevezés;
- `resolution` nem Domain/Zenit/Horizont/Ősforrás/Üresség;
- current default szerint nincs külön resolution-slot capacity legality gate;
- a döntés `CURRENT_CANONICAL_DEFAULT / PLAYTEST_REVIEWABLE`;
- tartós Rituálé külön future decision.

RC1:

```text
1 eligible responder
→ one opportunity
→ pass closes that window
```

RC2 ordinary trigger:

```text
committed event
→ trigger created/discovered immediately
→ queued pending trigger
→ current reaction/effect resolution cycle fully unwinds
→ post-resolution trigger checkpoint
→ queued trigger processing
```

Külön timing batch current default:
chronological FIFO by originating committed-event sequence.

Same-timing batch:
az official simultaneous-ordering szabály.

Reserved extension point:

- `strict_event_window`;
- delayed effect;
- explicit immediate timing override;
- future `TriggerActivationPolicy`;
- future `TriggerBatchOrderPolicy`.

A Reaction / Priority Foundation v1 exact minimum contractja és production runtime-ja lezárult.

Current lezárt elemek többek között:

- authoritative `ReactionWindow`;
- `ResolutionStack`;
- `QueuedTriggerBatches`;
- eligible responder/current priority representation;
- pass counter/reset semantics;
- event/correlation;
- viewer-safe pending projection;
- final revalidation;
- unsupported-path behavior a v1 scope szerint;
- Combat declaration-window integráció.

Továbbra is future extension / külön scope:

- generic prevention/replacement;
- teljes compound non-reaction choice framework;
- every future special timing policy;
- teljes card/ability coverage;
- reserved `strict_event_window`;
- delayed/immediate special timing;
- future `TriggerActivationPolicy`;
- future `TriggerBatchOrderPolicy`.

Reaction / Priority v1:

`COMPLETE_AND_ACCEPTED`

---

## 8. Combat + Pecsét C0–C6 és current roadmap

### Combat + Pecsét Foundation C0–C6

**Státusz:** `COMPLETE_AND_ACCEPTED`

Rules migration:

`61ad2605dd1aa3d7ea95444f0bb66cebf819014e`

Lezáró production commit:

`0862e1002dbef81ee203852714d377592272a0e9`

Current core:

- canonical setup + Jóslat;
- hat stabil Pecsét-slot és viewer-safe visibility;
- `attack` / AttackCommit;
- intervention / DefenseCommit;
- két Combat ReactionWindow;
- participant continuity/revalidation;
- Entity Combat simultaneous damage;
- SealBreak / public reveal / Surge;
- Gondviselés Surge opportunity;
- Aeternal outcome;
- terminal `MatchResult v2`.

Final acceptance:

- Debug/Release C#: `301/301 PASS`;
- targeted C6: `8/8 PASS`;
- determinism/reference: `100/100 PASS`;
- canonical SHA:
  `97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`;
- Python isolated `465/465 PASS` + 5 skip;
- exporter `23/23 PASS`;
- Godot positive/negative smoke PASS;
- unresolved P0/P1: `0/0`.

### VS1 / M6

**Státusz:** `NEXT MAJOR PRODUCT-FACING GOAL`

A VS1 nem azonos a korábbi production gameplay foundation slice-szal.

Canonical VS1 deckek:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

Current sequence:

```text
VS1 card/mechanic readiness audit
→ human scope/prioritásdöntés
→ csak tényleges blockerre finite contract/implementation
→ simple fair AI + match orchestration
→ minimal playable Godot
→ human-vs-AI + reproducible AI-vs-AI smoke
→ VS1 end-to-end acceptance
→ szükséges köztes mérföldkövek
→ AETERNA 0.0.1
```

VS1 előtt csak az a capability kötelező, amelyet a két canonical VS1 deck ténylegesen igényel,
vagy amely általános engine-invariánsként szükséges a rules-correct, deterministic,
viewer-safe lejátszáshoz.

Current rules authority:

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.5v.docx`;
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4.1v.docx`.

## 9. Python–C# kommunikáció

Elfogadott headless irány:

```text
Python
  ↓ JSON/JSONL / subprocess vagy később indokolt adapter
Aeterna.Engine.Headless
  ↓ canonical output
Python
```

Felhasználás:

- fixture;
- scenario;
- AI-vs-AI;
- batch;
- balanszelemzés;
- CI;
- regresszió.

HTTP/gRPC:
`DEFERRED_UNTIL_MEASURED_NEED`

---

## 10. Nem programozási aktív prioritás

- kártyaadat- és szabályaudit;
- LOOKUPS- és ID-contract;
- kártyadizájn-workflow;
- célzott learning/clean-room elemzés.

---

## 11. Codex / ChatGPT / ember munkamegosztás

### Ember

Végső project/rules/design/balance/priority/acceptance authority.

### ChatGPT + ember

- project-state reconstruction;
- rules/OQ munka;
- learning/synthesis értelmezés;
- contract/scope;
- Codex prompt;
- Codex report/diff/test audit;
- dokumentáció;
- milestone acceptance.

### Codex

- programozás;
- build/test/smoke;
- szükséges célzott lokális technikai vizsgálat.

Current programming workflow:

```text
Codex local edit + validation
→ NO COMMIT / NO PUSH
→ external audit
→ human approval
→ user commit/push
→ remote verification
```

Codex nem hoz önálló rules- vagy projektirányítási döntést.

## 12. Dokumentációs állapot

A nagy dokumentációs/archív cleanup történeti köre lezárult.

A C0–C6 mérföldkő után targeted current-truth sync fut, history-aware szerkesztéssel.

Aktuális learning/OQ állapot:

```text
59 registry project record
58 current local source
30 project analysis

52 answered
15 partly_answered
7 deferred
0 open
74 total
```

OQ current változás C0–C6 után:

- `OQ-SNAP-002`: `answered`;
- `OQ-LA-003`: `answered`;
- a fennmaradó részleges gate-ek scope-ja szűkült, de nem lett túlzárva.

Továbbra is tilos:

- indokolatlan párhuzamos authority-dokumentum;
- tartalomvesztés;
- nyitott kérdés elvesztése;
- aktív és történeti forrás összekeverése;
- Archive automatikus visszaállítási forrásként kezelése;
- learning/synthesis/blueprint automatikus rules authorityként kezelése.

Current documentation rule:

```text
committed current file
→ Git/Archive history comparison
→ targeted patch
→ diff review
```

Aktív current dokumentum verzióemelésekor ugyanaz a fájl frissül;
ha a verzió a fájlnév része, ugyanaz a fájl rename-elődik az új verzióra.
Régi active copy nem marad párhuzamosan.

## 13. Nyitott, de nem blokkoló tételek

- production Windows packaging;
- self-contained/prerequisite modell;
- runtime diagnostic log;
- hosszabb soak teszt;
- production AI-vs-AI;
- replay;
- Godot window policy;
- Python test-discovery adósság;
- sidecar proof archiválási stratégia;
- whitespace/formázási policy.

---

## 14. Rövid irány

**Most:** C0–C6 milestone documentation sync.
**Ezután:** VS1 / M6 readiness audit.
**Következő code:** csak readiness alapján azonosított tényleges blocker finite slice.
**VS1 után:** szükséges köztes mérföldkövek → 0.0.1.
**Dokumentáció:** history-aware targeted patch; meglévő current dokumentumból nem készül párhuzamos új active copy.
