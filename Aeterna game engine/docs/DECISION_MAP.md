# AETERNA Game Engine – Decision Map

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.7
**Dátum:** 2026-08-16
**Státusz:** aktív rövid döntési és iránytérkép
**Szinkronizációs repository-bázis:** `743c00d85ddc60bbbc70715fefab8ffc9dacbdae` – `docs: synchronize open questions and current decisions`
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`

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
- `../../Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.5.md`

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

### Első production gameplay vertical slice
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

## 7. Következő production irány

### Reaction / Priority Foundation v1

**Státusz:** `NEXT – MINIMAL_CONTRACT_FINALIZATION`

A source/OQ/research előkészítés ehhez a v1 slice-hoz már megtörtént:

- hivatalos `1.4.3v` reaction/timing audit;
- OQ A0–A4 felülvizsgálat;
- `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md` v2.2;
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

Az első Reaction v1 contractnak még pontosítania kell:

- exact ReactionWindow/ResolutionStack minimum mezőket;
- eligible responder/current priority representationt;
- pass counter/reset semanticsot;
- event/correlation és viewer-safe projection mezőket;
- final revalidation result behavior;
- unsupported content behavior.

Az első slice nem oldja meg automatikusan:

- generic prevention/replacement;
- teljes compound non-reaction choice frameworköt;
- combat-specifikus Reaction integrációt;
- every future special timing policyt;
- teljes card/ability coverage-et.

---

## 8. További gameplay queue

A Reaction / Priority foundation után, külön döntési kapukkal:

1. combat contract;
2. attack/target/block;
3. Pecsétfeltörés;
4. teljes Pecsét state/visibility;
5. Refresh Penalty;
6. ability coverage bővítése;
7. victory/defeat;
8. replay;
9. production AI-vs-AI;
10. packaging/UI.

Ez iránysorrend, nem automatikus implementációs parancs.

---

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

## 11. Codex-szabály

Codex csak szükséges technikai feladathoz:

- programozás;
- build/test/smoke;
- lokális worktree/fájl elemzés, ha GitHubból nem érhető el.

Projekttervezés, dokumentáció és rules/contract döntés nem alapértelmezett Codex-feladat.

---

## 12. Dokumentációs állapot

A nagy dokumentációs/archív cleanup lezárult.

A `2608345b...` mérföldkőhöz tartozó célzott A+B aktív consistency pass szintén lezárult.

A 2026-08-15-i dokumentációs handoff:

- `ae7d284...` – learning registry + analysis corpus;
- `b0e4d9d...` – cross-project synthesis + AETERNA blueprints;
- `743c00d...` – Open Questions v2.2 szinkron.

Aktuális learning/OQ állapot:

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

Továbbra is tilos:

- indokolatlan párhuzamos authority-dokumentum;
- tartalomvesztés;
- nyitott kérdés elvesztése;
- aktív és történeti forrás összekeverése;
- learning/synthesis/blueprint automatikus rules authorityként kezelése.

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

**Most:** Reaction / Priority minimal v1 contract finalizálás.
**Ezután:** csak elfogadott contract alapján szükséges Codex implementation.
**Combat:** külön későbbi slice.
**Dokumentáció:** learning/synthesis/OQ handoff commitolva; current admin-sync célzott, history-aware szerkesztéssel folytatandó.
