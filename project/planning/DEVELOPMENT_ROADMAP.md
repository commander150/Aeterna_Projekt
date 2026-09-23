---
artifact_id: AET-DOC-DEVELOPMENT-ROADMAP
kind: document
type: roadmap
version: "1.0"
lifecycle: active
integration: pending_integration
authority: project-direction
generated: false
depends_on: []
supersedes: []
---

# AETERNA – FEJLESZTÉSI ROADMAP ÉS MÉRFÖLDKŐ-RENDSZER

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-09-13  
**Státusz:** elfogadott fejlesztési roadmap; repository governance-integráció folyamatban  
**Hatókör:** current canonical/data foundation → VS1–VS10 → 0.0.1 → 0.x → 1.0  
**Projekt:** AETERNA digitális kártyajáték / rules engine / kliens / tooling  

---

## 0. Vezetői összefoglaló

Ez a dokumentum az AETERNA digitális projekt fejlesztési útvonalát rögzíti a jelenlegi canonical/data és validation munkától az első teljes termékverzióig.

A roadmap nem merev menetrend. A mérföldkövek **célállapotok**, amelyekhez belépési feltétel, elfogadási feltétel, megengedett technikai adósság és tiltott technikai adósság tartozik. Új köztes gate, megálló vagy sorrendmódosítás bármikor beiktatható, ha azt új bizonyíték, dependency, kockázat, playtest vagy termékprioritás indokolja.

A fő stratégiai útvonal:

```text
CURRENT – Canonical / Validation / Cutover Foundation
→ VS1 READINESS GATE
→ VS1 – First Playable Vertical Slice
→ SOURCE & DATA ARCHITECTURE CONSOLIDATION GATE
→ VS2 – Ignis + Aqua Full Base Coverage
→ VS3–VS7 – Remaining Realm Expansion Cycles
→ VS8 – Functional Internal Alpha
→ VS9 – Closed-Test Infrastructure + UI System
→ VS10 – Polished Closed Human Playtest Candidate
→ HUMAN PLAYTEST / BALANCE / STABILIZATION CYCLES
→ 0.0.1 RELEASE READINESS GATE
→ 0.0.1 – First Product-Development Release
→ 0.x – Product Evolution
→ 1.0 – First Complete Product Release
```

A roadmap négy alapelve:

1. **Correctness előbb, polish később.** VS1–VS8 között a minimális funkcionális UI elegendő.
2. **Content-driven engine growth.** Új engine capability csak akkor válik kötelezővé, ha tényleges content vagy általános correctness-invariáns igényli.
3. **Fail-closed canonical út.** Nem lehet silent fallback, rejtett validation bypass vagy párhuzamos production authority.
4. **Evidence-driven product growth.** VS10 után a balansz- és product-prioritásokat egyre inkább valós emberi playtest-adat vezérli.

---

# 1. Kiinduló projektállapot

## 1.1 Repository és production foundation

A roadmap kialakításakor a repository elfogadott fő engine-foundationjei már tartalmazzák többek között:

- C# authoritative production engine foundation;
- canonical card/runtime binding;
- Wellspring / Aura-payment / placement / `play_card` foundation;
- canonical ability/effect runtime foundation;
- explicit öt-fázisú lifecycle;
- Reaction / Priority Foundation v1;
- Combat + Pecsét Foundation C0–C6;
- Aeternal terminal outcome és authoritative `MatchResult`;
- Godot production bridge/smoke foundation;
- Python external tooling/reference réteg.

A repository jelenlegi irányadó production baseline-ja a roadmap tervezésekor:

`eba58f4aceb2c1990ed58abe7e2e2c6c6d7e1bd8`

A Combat + Pecsét foundation lezáró production mérföldköve:

`0862e1002dbef81ee203852714d377592272a0e9`

## 1.2 Aktuális canonical / validation munka

A current munkaszakasz a REGISTRY + CARDDATABASE canonical programadat-út, package-set, validation és canonical-only runtime cutover megerősítése.

A roadmap lezárásakor az utolsó **elfogadott** validation állapot a Slice 3F-D1B utáni állapot:

- pre_export active rules: 286;
- blocking rules: 284;
- supported blocking: 182 / 284 = 64.1%;
- PASS: 181;
- blocking FAIL: 1;
- UNSUPPORTED: 41;
- NOT_EXECUTED blocking: 61;
- stage verdict: `BLOCKED`.

A D1C implementáció Codex-oldalon már elkészült, de a jelentés ezen dokumentum lezárásakor még nincs emberileg/ChatGPT-oldalon auditálva, ezért a roadmap baseline nem tekinti elfogadottnak.

## 1.3 Ismert canonical/data döntések és findingok

A jelenlegi irány fontosabb elvei:

- production package-set többkomponensű canonical artifact; kezdetben REGISTRY + CARDDATABASE;
- runtime oldalon csak canonical ID-k engedhetők; alias csak authoring/import/migration határon;
- `current` reserved external context identifier; local binding később tiltandó;
- validation fail-closed;
- production blocking szabály nem maradhat csendben kiértékeletlen;
- authoritative workbookokat tooling/Codex nem írhatja át automatikusan;
- legacy és canonical authority nem maradhat párhuzamosan production truth.

---

# 2. Roadmap governance – alapmodell

## 2.1 A roadmap szerepe

A roadmap feladata nem a teljes jövő megjóslása. A feladata, hogy mindig egyértelmű legyen:

- mi a következő bizonyítható célállapot;
- miért az következik;
- milyen feltételekkel kezdhető;
- milyen bizonyítékkal zárható le;
- milyen adósság vihető tovább;
- milyen adósság tiltott.

## 2.2 Tervezési státuszok

### LOCKED DIRECTION

Elfogadott alapirány. Részletek változhatnak, de a fő irány csak erős indokkal.

### PLANNED

Valószínű fejlesztési cél, de scope-ja és részletei még módosíthatók.

### DRAFT INTENT

Távolabbi iránytű. Nem implementation commitment.

### DEFERRED

Tudatosan elhalasztott elem, újraaktiválási triggerrel.

### REJECTED / SUPERSEDED

Korábbi, de már nem aktuális irány. Történeti referenciaként megőrzendő.

## 2.3 Feladattípusok

- **BLOCKER** – nélküle a current milestone acceptance nem teljesíthető;
- **REQUIRED DEPENDENCY** – blocker előfeltétele;
- **QUALITY / HARDENING** – stabilitást és karbantarthatóságot javít;
- **FUTURE CAPABILITY** – későbbi milestone-hoz kell;
- **PRODUCT ENHANCEMENT** – játékosértéket ad, de nem correctness blocker;
- **RESEARCH** – döntéshez információt termel;
- **TECHNICAL DEBT** – tudatosan továbbvitt kompromisszum kezelése.

## 2.4 Új feladat öt kérdése

Minden új feladatnál meg kell válaszolni:

1. Melyik milestone acceptance-jét érinti?
2. Blocker vagy csak javítás?
3. Mi történik, ha most nem készül el?
4. Van-e más feladat, amely függ tőle?
5. Current milestone-hoz tartozik, vagy későbbihez?

Ha ezek alapján nem indokolt a current scope, az alapértelmezés: **backlog / későbbi milestone**.

---

# 3. Stratégiai roadmap

| Szakasz | Státusz | Elsődleges cél |
|---|---|---|
| CURRENT Canonical/Data Foundation | LOCKED DIRECTION | fail-closed canonical production út |
| VS1 Readiness Gate | LOCKED DIRECTION | két VS1 deck véges blockerlistája |
| VS1 | LOCKED DIRECTION | első teljes játszható vertical slice |
| Source/Data Architecture Gate | PLANNED | authoring és canonical modell skálázhatósága |
| VS2 | PLANNED | Ignis + Aqua teljes base coverage |
| VS3–VS7 | PLANNED | öt további Birodalom teljes base coverage |
| VS8 | DRAFT INTENT | stabil funkcionális internal alpha |
| VS9 | DRAFT INTENT | closed-test infrastructure és UI-rendszer |
| VS10 | DRAFT INTENT / erős irány | látványos closed human playtest candidate |
| Post-VS10 | DRAFT INTENT | human playtest, balance, stabilization |
| 0.0.1 Release Readiness Gate | DRAFT INTENT | szélesebb terjesztés előtti release clearance |
| 0.0.1 | DRAFT INTENT | első product-development release |
| 0.x | DRAFT INTENT | product feature growth |
| 1.0 | DRAFT INTENT | első teljes stabil termékverzió |

---

# 4. Munkasáv × mérföldkő mátrix

Jelölések:

- `—` nincs érdemi munka;
- `MIN` minimális fenntartás;
- `FND` foundation/alapozás;
- `MAJ` jelentős fejlesztés;
- `ACC` acceptance-szint / lezárási kritérium.

A mátrix terhelési térkép, nem időbecslés. A jobb olvashatóság érdekében két részre bontva jelenik meg.

## 4.1 CURRENT → VS7

| Munkasáv | CURRENT | VS1 Ready | VS1 | Data Gate | VS2 | VS3–7 |
|---|---:|---:|---:|---:|---:|---:|
| Rules governance | MIN | MAJ | ACC | MIN | MAJ | MAJ |
| Human authoring / főforrások | MIN | MIN | MIN | MAJ/ACC | FND | FND |
| REGISTRY / CARDDATABASE | MAJ | ACC | ACC | MAJ/ACC | MAJ | MAJ |
| Validation / compiler | MAJ/ACC | MAJ | ACC | MAJ | MAJ | MAJ |
| C# authoritative engine | FND | MAJ | MAJ/ACC | MIN | MAJ | MAJ |
| Card/content coverage | MIN | MAJ | MAJ/ACC | MIN | MAJ/ACC | MAJ/ACC |
| AI | MIN | FND | MAJ/ACC | MIN | MAJ | MAJ |
| UI / UX | MIN | MIN | MIN | — | MIN | MIN |
| Testing / regression | MAJ | MAJ | ACC | MAJ | ACC | ACC |
| Balance | — | MIN | MIN | — | FND | MAJ |
| Logging / diagnostics | FND | MIN | ACC | MIN | FND | FND |
| Technical reproduction | MIN | MIN | FND | — | FND | FND |
| Product replay | — | — | — | — | — | MIN |
| Packaging / distribution | MIN | — | MIN | — | MIN | MIN |
| Update / version management | — | — | — | — | — | MIN |
| Legal / asset provenance | MIN | MIN | MIN | MIN | MIN | MIN |
| Performance | MIN | MIN | MIN | — | MIN | MIN |
| Migration / compatibility | MAJ | MIN | ACC | MAJ | MIN | MIN |
| Security / privacy / integrity | FND | MIN | ACC | MIN | MIN | MIN |
| Documentation / status | MAJ | MAJ | ACC | MAJ | ACC | ACC |

## 4.2 VS8 → 0.0.1

| Munkasáv | VS8 | VS9 | VS10 | Playtest | Release Gate | 0.0.1 |
|---|---:|---:|---:|---:|---:|---:|
| Rules governance | MIN | MIN | ACC | MAJ | MIN | ACC |
| Human authoring / főforrások | MIN | MIN | MIN | MIN | MIN | ACC |
| REGISTRY / CARDDATABASE | MIN | MIN | MIN | MIN | MIN | ACC |
| Validation / compiler | FND | MIN | ACC | MIN | MIN | ACC |
| C# authoritative engine | FND | MIN | ACC | MAJ | — | ACC |
| Card/content coverage | FND | MIN | ACC | MAJ | — | ACC |
| AI | FND | MAJ | ACC | MAJ | — | ACC |
| UI / UX | MIN | MAJ | MAJ/ACC | MAJ | FND | ACC |
| Testing / regression | MAJ | MAJ | ACC | MAJ | MIN | ACC |
| Balance | MAJ | MAJ | FND | MAJ | — | FND |
| Logging / diagnostics | MAJ | MAJ/ACC | ACC | MAJ | MIN | ACC |
| Technical reproduction | FND | MAJ | ACC | MAJ | — | ACC |
| Product replay | MIN | FND | FND | MAJ | — | FND |
| Packaging / distribution | FND | MAJ | ACC | FND | MAJ | ACC |
| Update / version management | MIN | MAJ | ACC | MAJ | FND | ACC |
| Legal / asset provenance | MIN | FND | MAJ | MAJ | MAJ/ACC | ACC |
| Performance | FND | MAJ | ACC | MAJ | MIN | ACC |
| Migration / compatibility | FND | FND | ACC | MAJ | MAJ | ACC |
| Security / privacy / integrity | FND | MAJ | ACC | MAJ | MAJ/ACC | ACC |
| Documentation / status | ACC | ACC | ACC | MAJ | ACC | ACC |

---

# 5. UI-érettségi modell

## UI-0 – Debug

Csak fejlesztői/debug nézet.

## UI-1 – Functional

Minden szükséges elem látható, megkülönböztethető és használható. Nem kell szépnek lennie.

**Roadmap:** VS1–VS8.

Elfogadható:

- egyszerű gombok;
- placeholder kártyák;
- nyers panelek;
- egyszerű státuszszövegek;
- minimális menü.

## UI-2 – Coherent Prototype

Egységes layout, vizuális hierarchy, alap UX-rendszer.

**Roadmap:** VS9.

## UI-3 – Playtest Polished

Látványos, koherens, külső embernek megmutatható closed-test kliens.

**Roadmap:** VS10.

## UI-4 – Release Clean

Product-szintű, jogtisztán terjeszthető UI és asset-réteg.

**Roadmap:** 0.0.1+.

---

# 6. Release profilok

## Developer Profile

Jellemző: CURRENT → VS8.

Megengedett:

- részletes debug diagnostics;
- fejlesztői state viewer;
- fixture/smoke tooling;
- funkcionális placeholder UI.

## Closed Test Profile

Jellemző: VS9 → VS10 → post-VS10.

Követel:

- self-contained tesztelői futás;
- kontrollált diagnostics;
- log/bug-report csomag;
- verzióazonosítás;
- tester-safe state/projection;
- tiszta update path.

## Wider Distribution / Product Development Profile

Jellemző: 0.0.1+.

Követel:

- release-cleared assetek;
- privacy és integrity policy;
- compatibility/migration;
- szélesebb terjesztésre alkalmas package;
- jogilag tiszta harmadik fél tartalmak.

Az AETERNA core product alapértelmezett iránya **offline-first**. Updater, crash reporting vagy későbbi online szolgáltatás nem teheti az alapjátékot szükségtelenül internetfüggővé.

---

# 7. Milestone Acceptance Cardok

## 7.1 CURRENT – Canonical/Data Foundation

**Státusz:** LOCKED DIRECTION

### Goal

Deterministic, validált, fail-closed programadat-út kialakítása a human-maintained forrásoktól a production C# engine-ig.

### Entry Gate

Teljesült: canonical workbooks, exporter/loader foundation, C# ingestion és validation architecture létezik.

### Must Have

- production blocking validation végrehajtható;
- package-set contract;
- production export/publish gate;
- canonical C# consumption;
- VS1 deck/card data canonical úton;
- legacy production authority megszüntetése;
- szükséges authoritative data correctionök explicit emberi kezelésben.

### Explicit Non-Goals

- teljes authoring redesign;
- teljes Content Compiler;
- teljes 814 lapos content production coverage;
- UI polish.

### Exit / Acceptance

- nincs silent blocking NOT_EXECUTED a production útban;
- canonical package/set determinisztikus;
- C# VS1 contentet canonical-only útról betölt;
- legacy többé nem production authority;
- parity/smoke evidence zöld.

### Allowed Debt

- régi authoring XLSX átmenetileg megmaradhat;
- legacy artefact összehasonlításra megmaradhat;
- nem production-blocking future validation későbbre maradhat.

### Forbidden Debt

- silent fallback;
- runtime alias normalization;
- két production authority;
- derived output visszaírása human authorityként;
- nondeterministic canonical identity.

### Evidence

Canonical tests, validation corpus, hash/provenance, C# ingestion, parity, VS1 deck load smoke.

---

## 7.2 VS1 READINESS GATE

**Státusz:** LOCKED DIRECTION

### Goal

A két canonical VS1 deck teljes végrehajtási dependency-inventoryja és véges blockerlistája.

### Must Have

Minden érintett card/mechanic:

`SUPPORTED / PARTIAL / MISSING / DATA ISSUE / RULES DECISION REQUIRED`.

### Exit

- nincs ismeretlen critical dependency;
- blockerlista véges;
- minden required decision vagy lezárt, vagy explicit decision task.

### Forbidden Debt

- unknown support status VS1 cardnál;
- silent fallback;
- bizonytalan szabályszemantika critical flowban.

### Evidence

Deck/card/mechanic readiness matrix és capability mapping.

---

## 7.3 VS1 – First Playable Vertical Slice

**Státusz:** LOCKED DIRECTION

### Goal

Első ténylegesen teljes human-vs-AI és AI-vs-AI AETERNA-meccs két canonical deckkel.

### Must Have

- setup;
- teljes phase lifecycle;
- card play;
- szükséges payment/target/choice;
- abilities/effects;
- reaction/priority;
- combat;
- Pecsét;
- terminal MatchResult;
- viewer-safe hidden info;
- simple fair AI;
- UI-1 functional Godot;
- human-vs-AI;
- reproducible AI-vs-AI smoke.

### Non-Goals

- teljes Ignis/Aqua set;
- szép UI;
- economy/collection/tutorial;
- végleges balance.

### Exit

- több teljes match végigfut;
- P0 rules-correctness = 0;
- VS1 silent fallback = 0;
- minden szükséges emberi döntés UI-ból megadható.

### Allowed Debt

- placeholder visual;
- simple AI;
- nyersebb diagnostics.

### Forbidden Debt

- hidden-info leak;
- nondeterministic authority;
- manual state edit normál flowban;
- unsupported VS1 execution.

---

## 7.4 SOURCE & DATA ARCHITECTURE CONSOLIDATION GATE

**Státusz:** PLANNED

### Goal

A VS2–VS7 tömeges content-expanzió előtt skálázható authoring/canonical adatarchitektúra.

### Must Have

- REGISTRY structural audit;
- CARDDATABASE structural audit;
- authoritative főforrások strukturális felülvizsgálata;
- schema/provenance/authority tisztázás;
- modular authoring target;
- Content Compiler minimum contract;
- legacy/duplicate source status.

### Exit

VS2 content wave nem igényel minden új mechanicnál alapvető adatmodell-redesignt.

### Allowed Debt

- authoring maradhat részben XLSX;
- compiler lehet kezdetben CLI.

### Forbidden Debt

- több helyen kézzel duplikált authority;
- undocumented ID mapping;
- derived-as-authority visszaírás.

---

## 7.5 VS2 – Ignis + Aqua Full Base Coverage

**Státusz:** PLANNED

### Goal

A VS1 két Birodalmának teljes base-set production coverage-e.

### Exit

- Ignis/Aqua base card coverage = 100%;
- silent fallback = 0;
- több valid deckkombináció;
- AI legal support;
- functional UI support;
- regression zöld.

### Allowed Debt

- UI-1;
- simple AI heuristic;
- nem kritikus balance probléma.

### Forbidden Debt

- unsupported Ignis/Aqua base card;
- card-ID special-case canonical contract megkerülésével.

---

## 7.6 VS3–VS7 – Realm Expansion Cycle

**Státusz:** PLANNED

Mind az öt mérföldkő ugyanazt a sablont használja.

### Goal

Mérföldkövenként egy további Birodalom teljes base-set production coverage-e.

### Entry

Realm Readiness Audit.

### Exit

- új Realm 100% base coverage;
- AI legal support;
- functional UI;
- korábbi Realmek regressionje zöld;
- matchup smoke lefut.

A konkrét Realm-sorrend nincs befagyasztva; mindig readiness/risk/value alapján választandó.

---

## 7.7 VS8 – Functional Internal Alpha

**Státusz:** DRAFT INTENT

### Goal

A működő engine/content rendszerből stabil belső program.

### Must Have

- stability pass;
- performance baseline;
- packaging foundation;
- diagnostics hardening;
- content soft freeze;
- UI továbbra is csak UI-1 functional.

### Exit

- normál használatban rendszeresen végigjátszható;
- P0 rendszerhiba = 0;
- core flow nem igényel kézi developer beavatkozást.

### Non-Goal

Nem kell szépnek lennie.

---

## 7.8 VS9 – Closed-Test Infrastructure + UI System

**Státusz:** DRAFT INTENT

### Goal

A rendszer másik gépen/másik embernél diagnosztizálható és reprodukálható legyen, valamint kialakuljon a koherens UI-rendszer.

### Must Have

- structured logging;
- build/version identity;
- match/run identity;
- seed/action/event reproduction metadata;
- bug-report package;
- updater/update-path foundation;
- package/update integrity;
- tester-safe diagnostics;
- privacy-safe report export;
- UI-2 coherent prototype;
- asset provenance ledger formalizálása.

### Exit

Egy távoli tesztelő hibajelentéséből a konkrét futás technikailag visszakereshető/reprodukálható.

---

## 7.9 VS10 – Polished Closed Human Playtest Candidate

**Státusz:** DRAFT INTENT / erős irány

### Goal

Az első build, amelyet rajtunk kívüli, megbízható emberi tesztelőknek tényleges játékprogramként oda lehet adni.

### Technical Playtest Acceptance

- self-contained futás;
- clean-machine launch;
- stable update path;
- log/bug report;
- version/provenance;
- AI használható;
- P0 crash/data loss = 0;
- normál flow rules-correct.

### Presentation Playtest Acceptance

- UI-3 Playtest Polished;
- koherens battlefield;
- felismerhető kártyák;
- világos feedback;
- Realm-identitások érzékelhetők;
- normál játék nem debug-tool érzetű.

### Asset policy

VS10-ben használható ideiglenes `PLAYTEST_TEMP` asset, **ha jogszerűen használható**. Minden asset eredete/provenance státusza követett.

---

## 7.10 POST-VS10 – Human Playtest / Balance / Stabilization

**Státusz:** DRAFT INTENT

Iterációs ciklus:

```text
Playtest
→ evidence collection
→ triage
→ reproduction
→ bug/rules/UX/balance classification
→ fix/rebalance
→ regression
→ next playtest
```

A fő újdonság: a projekt prioritását ettől kezdve egyre inkább valós emberi használati adatok befolyásolják.

---

## 7.11 0.0.1 RELEASE READINESS GATE

**Státusz:** DRAFT INTENT

A VS10 és a szélesebben terjeszthető product-development release közötti clearance.

### A. Asset Clearance

- unknown source = 0;
- unauthorized = 0;
- unclear redistribution = 0;
- required replacement = 0.

### B. Privacy / Diagnostics Clearance

- nincs szükségtelen személyes adat;
- nincs hidden-info leakage player-facing reportban;
- automatikus internetes logküldés csak explicit policy/consent mellett.

### C. Package / Update Integrity

- build identity;
- compatibility check;
- package integrity;
- controlled failure/recovery.

### D. Licensing / Third-Party Notices

- library/font/audio/art licencek és attribúciók rendezve.

### E. Compatibility

Ha addigra van persisted user data, migration/compatibility bizonyított.

### F. Distribution Proof

Clean-machine launch, offline core működés, megfelelő package.

---

## 7.12 0.0.1 – First Product-Development Release

**Státusz:** DRAFT INTENT

### Goal

Az emberileg már tesztelt, stabil core game első tudatosan verziózott product-development állomása.

### Fontos scope-elv

A 0.0.1 **nem** követeli automatikusan az összes későbbi product feature-t.

Nem automatikus 0.0.1 blocker például:

- teljes collection;
- teljes economy;
- minden tutorial;
- teljes booster rendszer;
- minden későbbi product menu.

Ezek 0.x során fokozatosan épülhetnek be.

### Kötelező

- release-clean asset és legal állapot;
- stabil core;
- wider-distribution profile követelményei;
- a milestone tényleges scope-jának megfelelő acceptance.

---

## 7.13 0.x – Product Evolution

**Státusz:** DRAFT INTENT

A feature-ek verzióhoz rendelése később történik a következő prioritási tengelyek szerint:

- dependency;
- player value;
- playtest evidence.

---

## 7.14 1.0 – First Complete Product Release

**Státusz:** DRAFT INTENT

1.0 nem azt jelenti, hogy minden valaha elképzelt feature kész.

Azt jelenti, hogy a kiválasztott core product scope teljes, stabil, fenntartható és termékszintű.

Első vázlatos pillérek:

1. stable core game;
2. player persistence;
3. deck/collection management;
4. onboarding;
5. progression/acquisition loop;
6. product UI;
7. diagnostics/support;
8. distribution/update/recovery;
9. legal cleanliness;
10. quality/performance/compatibility/human playtest evidence.

---

# 8. Product Evolution Trackek – 0.0.1 → 1.0

A következő területek nem kapnak most fix verziószámot.

## A. Profile / Save / Settings

- local profile;
- settings;
- save schema;
- backup/recovery;
- corruption handling;
- migration.

**Trigger rule:** az első persisted user data ugyanabban a slice-ban schema version + compatibility/migration policy-t igényel.

## B. Deck Management

- create/edit/delete;
- legality;
- ownership-aware restrictions;
- deck naming/duplicate;
- statistics később.

## C. Collection

- owned cards/counts;
- search/filter;
- rarity/Realm/Clan;
- deck editor integration.

## D. Tutorial / Starter / Onboarding

- basic gameplay tutorial;
- Realm tutorial;
- starter flow;
- guided first match.

A VS10 playtestekből származó UX evidence fontos input.

## E. Local Economy

- offline/local currency;
- rewards/unlocks;
- starter acquisition;
- pack/deck purchase;
- duplicate conversion.

Nem automatikus cél a valódi pénzes/live-service economy.

## F. Booster / Reward Experience

- pack definition/generation;
- rarity distribution;
- opening UI;
- duplicate handling;
- deterministic debug reproduction.

## G. AI Evolution

- AI-0 legal action;
- AI-1 simple fair VS1;
- AI-2 basic tactical;
- AI-3 deck-aware;
- AI-4 matchup-aware / stronger.

1.0-hoz legalább érdemben eltérő könnyű/normál/nehezebb profil indokolt.

## H. Replay / Match History / Statistics

A technikai reproductiontól külön product réteg:

- replay browser;
- timeline/playback;
- match history;
- stats.

## I. Tester / Debug Mode

Tester Mode = szabályos játék több diagnosztikával.  
Sandbox = szándékosan manipulálható developer state.

## J. UI / Visual Productisation

- main menu;
- deck/collection UI;
- settings;
- tutorials;
- shop/booster;
- replay/stats;
- accessibility.

## K. Audio

- UI feedback;
- card/combat/seal events;
- music/ambience;
- volume controls.

## L. Localization

VS9-től localization-ready architecture ajánlott. További nyelvek későbbi product prioritások.

## M. Accessibility

- text scaling;
- contrast;
- color-independent state;
- reduced animation;
- keyboard/input remapping;
- tooltip/help.

## N. Packaging / Update / Recovery

- portable/installer;
- updater;
- rollback/repair;
- compatibility;
- code signing később, ha indokolt.

## O. Privacy / Data Handling

Online telemetry/crash reporting csak explicit külön döntéssel és megfelelő consent/policy mellett.

## P. Asset / Licensing / Credits

- provenance;
- licenses;
- attribution;
- third-party notices;
- replacement tracking.

## Q. Performance / Compatibility

- supported Windows versions;
- min hardware;
- startup/load;
- AI latency;
- memory;
- resolution/aspect ratio;
- large logs/replay.

## R. Modding / Extensibility

Future direction, nem current kötelező roadmap. A data-driven architektúra maradjon bővíthető, de most nem tervezünk mod API-t.

---

# 9. Technical debt és blocker policy

## 9.1 Allowed Debt

Dokumentált kompromisszum, amely:

- nem veszélyezteti correctness-et;
- nem bizonytalanít authorityt;
- nem okoz adatvesztést;
- később kontrolláltan rendezhető.

Példák:

- VS1–VS8 minimal/ronda UI;
- simple AI;
- temporary playtest art megfelelő provenance-szal.

## 9.2 Forbidden Debt

Soha nem vihető tovább:

- silent fallback;
- hidden validation bypass;
- két production authority;
- bizonytalan canonical identity;
- nondeterministic state mutation;
- known hidden-info leak;
- known data loss;
- unauthorized/unknown release asset;
- production rules logic UI-ban;
- ismert rules violation teszttel elfedve.

## 9.3 Technical Debt Ledger

Minden tudatos debt kapjon:

- ID;
- leírás;
- keletkezési milestone;
- indok;
- kockázat;
- legkésőbbi rendezési milestone;
- early trigger.

---

# 10. Blocker severity

## P0

Authority, state corruption, data loss, critical hidden-info leak, core-flow crash.

Milestone nem zárható P0-val.

## P1

Lényegi milestone-funkció hibás vagy megbízhatatlan.

Milestone normál esetben nem zárható P1-gyel.

## P2

Jelentős, de workarounddal kezelhető; acceptance card dönt.

## P3

Kisebb bug/polish/convenience; általában továbbvihető.

---

# 11. Scope creep és milestone freeze

## 11.1 Scope creep

Scope creep az a feladat, amely:

- nem kell current acceptance-hez;
- nem általános correctness/security/data-integrity dependency;
- nem old fel közvetlen blockert;
- csak azért kerülne előre, mert később „úgyis kell”.

**Future usefulness ≠ current priority.**

## 11.2 Milestone Freeze

Acceptance-közeli állapotban új feature csak akkor kerülhet be, ha:

- P0/P1-et old meg;
- acceptance blockert old fel;
- data-loss/security/correctness problémát javít;
- bizonyítottan szükséges az acceptance-hez.

---

# 12. Köztes gate-ek beszúrása

Új gate indokolt, ha:

- több dependency-t kell együtt lezárni;
- risk reduction szükséges;
- migration/parity bizonyítás kell;
- audit/döntés kell implementáció előtt;
- prototípus és release között külön clearance kell.

Technikai gate-ek nem kapnak automatikusan VS-számot.

Ajánlott nevek:

- Readiness Gate;
- Migration Gate;
- Data Gate;
- Architecture Gate;
- Hardening Gate;
- Release Gate.

---

# 13. Replanning policy

## Replanning trigger

- architecture bizonyítottan nem tud required feature-t biztonságosan;
- canonical modell alapvetően hiányos több content familyre;
- rules/implementation conflict;
- scale probléma;
- human playtest cáfol alapfeltevést;
- maintenance cost rendszeresen szétesik;
- performance acceptance előtt eléri a limitet.

## Nem replanning trigger önmagában

- egy bug;
- egy nehéz card;
- új divatos technológia;
- kódstílus-preferencia;
- kisebb optimalizáció.

---

# 14. Change Impact Review

Nagyobb módosítás előtt vizsgálandó:

- rules;
- data/schema;
- migration;
- engine;
- content;
- AI;
- UI;
- regression;
- compatibility;
- documentation;
- később save/user-data;
- legal/licensing;
- distribution.

---

# 15. Authority modell

## Game/Product Design

Emberi authority:

- szabályváltoztatás;
- balance cél;
- Realm identity;
- feature priority;
- product scope;
- economy design;
- UX-cél.

## Technical Design

Engineering/evidence alapján javasolható, de nem írhatja felül a rules authorityt.

## Data Correction

Authoritative human-maintained source módosítása explicit emberi kontrollt igényel; tooling csak auditálhat/javasolhat, nem javíthat csendben.

---

# 16. Evidence hierarchy

## Rules

Official rules source → accepted human decision → current contract → implementation/test evidence.

## Implementation State

Current repository state → production implementation → tests → status documentation.

## Product Priority

Current roadmap/governance → playtest evidence → dependency/risk analysis.

## Balance

Human playtest + statisztika → simulation → intuition.

---

# 17. Acceptance evidence

Milestone nem lesz kész attól, hogy „a kód elkészült”.

Lehetséges evidence:

### Static

Schema, audit, validation, build.

### Dynamic

Tests, deterministic scenario, match run, regression, smoke.

### Product

User flow, clean-machine install, tester use, playtest.

Acceptance eredmény:

- `PASS`;
- `CONDITIONAL PASS` – csak dokumentált Allowed Debttel, P0/P1 nélkül;
- `FAIL`.

---

# 18. Balance és human playtest policy

VS2–VS7: balance signals.  
VS8–VS10: preliminary balance.  
Post-VS10: evidence-based balance.

Balance change előtt vizsgálandó:

- bug vagy valódi balance issue;
- card-specific vagy system-level;
- sample size;
- matchup;
- player skill;
- AI bias;
- unintended interaction.

Egyetlen tesztelő véleménye nem automatikusan balance truth.

---

# 19. Asset és legal policy

## 19.1 Korai development

Asset provenance tracking már az első külső asset bekerülésekor induljon minimális formában.

Minimum:

- asset/path;
- source;
- license/status;
- temporary?;
- replacement required?.

## 19.2 VS10

Lehetnek `PLAYTEST_TEMP` assetek, ha jogszerű használatuk igazolható.

## 19.3 0.0.1+

Csak `RELEASE_CLEARED` asset maradhat.

A wider-distribution buildben:

- unknown source = 0;
- unauthorized = 0;
- unclear redistribution = 0.

---

# 20. Biztonság, privacy és release integrity

VS9–VS10 előtt:

- log ne tartalmazzon szükségtelen személyes adatot;
- player-facing report ne szivárogtasson hidden game informationt;
- automatikus online logküldés ne legyen explicit döntés nélkül;
- update csak azonosítható/integritás-ellenőrzött buildet fogadjon;
- corrupted package kontrollált hibát adjon.

0.0.1+ esetén privacy/integrity követelmények a tényleges terjesztési modellhez igazítandók.

---

# 21. Definition of Ready / Done

## Definition of Ready

Implementation slice csak akkor induljon, ha:

- goal ismert;
- authority ismert;
- input contract ismert;
- acceptance ismert;
- scope/non-goals ismert;
- nincs lényegi emberi decision gap.

Ha nincs Ready: audit/decision slice következik.

## Definition of Done

- implementált;
- szükséges tesztek zöldek;
- regression tiszta;
- edge cases kezeltek;
- diagnostics megfelelő;
- scope creep nem történt;
- authority sértetlen;
- nincs rejtett fallback;
- szükséges status/docs frissítve.

---

# 22. Roadmap review cadence

Event-driven review szükséges:

- milestone lezárásakor;
- új milestone előtt;
- replanning trigger esetén;
- jelentős human playtest batch után;
- nagy data/rules migration előtt;
- release candidate előtt.

Nem szükséges mechanikus heti/havi roadmap-adminisztráció.

---

# 23. Feature Parking Lot

Nem aktuális ötlet nem vész el.

`PARKED / FUTURE` rekord minimum:

- ötlet;
- potenciális érték;
- dependency;
- lehetséges milestone;
- activation trigger.

Így az ötlet megmarad, de nem okoz scope creep-et.

---

# 24. Project health indicators

## Jó jelek

- blockerlista csökken;
- supported content nő;
- regresszió stabil;
- új Realm implementációja kiszámíthatóbb;
- architecture change ritkul;
- playtest bug reprodukálható.

## Rossz jelek

- minden új card új frameworköt igényel;
- special-case-ek nőnek;
- ugyanazokat a data problémákat ismételten javítjuk;
- acceptance új feature-ök miatt folyamatosan kitolódik;
- UI/AI saját rules logicot kezd tartalmazni;
- testszám nő, de confidence nem;
- docs és implementation truth rendszeresen eltér.

Több rossz jel együtt replanning triggert jelenthet.

---

# 25. Ismert dokumentációs migrációs kötelezettség

A jelenlegi repository 0.0.1 célállapot-dokumentumai a régebbi terv szerint a 0.0.1-be már többek között profile/save, tutorial, collection/economy, tester tooling és széles product runtime követelményeket is automatikusan beemelnek.

A jelen roadmap elfogadott iránya ettől eltér:

> **0.0.1 a VS10 + human playtest stabilizáció után induló product-development release line első állomása, nem az összes későbbi product feature kötelező gyűjtőpontja.**

Ezért a roadmap repository-governance-be való átvezetésekor külön dokumentációs migration szükséges legalább az alábbi rétegekben:

- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT`;
- `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS`;
- aktuális projektterv/prioritások;
- érintett README/status dokumentumok.

A régi dokumentumok addig történeti/current-repo authorityként még eltérhetnek a most elfogadott planning directiontől. Ezt explicit konfliktusként kell kezelni, nem csendben figyelmen kívül hagyni.

---

# 26. Roadmap használati szabály röviden

Minden jelentősebb munka előtt:

```text
1. Melyik milestone?
2. Mi a blocker?
3. Mi az acceptance?
4. Mi a non-goal?
5. Mi vihető tovább debtként?
6. Mi tiltott debt?
7. Milyen evidence kell?
```

Ha ezek nem válaszolhatók meg, előbb audit/döntés szükséges.

---

# 27. Végső roadmap-összefoglaló

```text
CURRENT
Canonical / Validation / Cutover Foundation
        ↓
VS1 READINESS GATE
        ↓
VS1
First Playable Vertical Slice
        ↓
SOURCE & DATA ARCHITECTURE CONSOLIDATION GATE
        ↓
VS2
Ignis + Aqua Full Base Coverage
        ↓
VS3–VS7
Five Remaining Realm Expansion Cycles
        ↓
VS8
Functional Internal Alpha
        ↓
VS9
Closed-Test Infrastructure
+ UI System
+ Logging/Reproduction
+ Update/Security Foundation
        ↓
VS10
Polished Closed Human Playtest Candidate
        ↓
HUMAN PLAYTEST / BALANCE / STABILIZATION CYCLES
        ↓
0.0.1 RELEASE READINESS GATE
├─ asset clearance
├─ privacy/diagnostics clearance
├─ package/update integrity
├─ licensing/third-party notices
├─ compatibility where applicable
└─ distribution proof
        ↓
0.0.1
First Product-Development Release
        ↓
0.x
Product Evolution
        ↓
1.0
First Complete Product Release
```

---

# 28. Forrásalap és kapcsolódó aktív projektanyagok

A roadmap tervezése során figyelembe vett főbb projektanyagok:

- `project/planning/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.9.md`;
- `Aeterna game engine/docs/PROTOTYPE_STATUS.md` v1.6;
- `Aeterna game engine/docs/RUNTIME_PACKAGE_STATUS.md` v1.6;
- `Aeterna game engine/docs/ABILITY_MODULE_SYSTEM.md` v1.5;
- `Aeterna game engine/docs/PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md` v1.3;
- `Aeterna game engine/docs/AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.1.md`;
- `Aeterna game engine/docs/checkpoints/*` aktív réteg;
- manifest-driven REGISTRY/CARDDATABASE export és C# ingestion korábbi terv;
- current canonical package-set / validation / cutover munkafolyamat;
- a roadmap-tervezési beszélgetés során elfogadott emberi product/roadmap döntések.

---

# 29. Dokumentumstátusz

**ROADMAP DESIGN: ACCEPTED**  
**STRUCTURAL CONSISTENCY AUDIT: PASS WITH INTEGRATED CORRECTIONS**  
**REPOSITORY GOVERNANCE MIGRATION: IN PROGRESS**  

A dokumentum a további AETERNA-tervezés stabil kiindulási alapja, de dinamikus roadmap: indokolt esetben módosítható a jelen dokumentumban rögzített governance-szabályok szerint.
