# AETERNA – CROSS-PROJECT SYNTHESIS: REACTIONS, TRIGGERS AND RESOLUTION

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.2
- **Dátum:** 2026-08-15
- **Státusz:** hivatalos 1.4.3v rules-visszaellenőrzéssel korrigált synthesis
- **Javasolt repository-útvonal:** `learning/synthesis/topics/reactions_triggers_resolution.md`
- **Kiinduló AETERNA repository HEAD:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Módszertan:** az aktuális `CROSS_PROJECT_METHOD`
- **Nem AETERNA-szabályforrás.**
- **Nem végleges Reaction/Priority contract.**

---

# 1. Felhasznált izolált auditok

## Új célzott auditok

- `learning/analyses/card-forge__forge.md`
- `learning/analyses/magefree__mage.md`
- `learning/analyses/edo9300__ygopro-core.md`

## Korábban elkészült auditok

- `learning/analyses/finkmoritz__csbcgf.md`
- `learning/analyses/ProjectIgnis_cardscripts.md`

## Evidence family

| Forrás | Family |
|---|---|
| Card-Forge/forge | `FORGE` |
| magefree/mage | `MAGE` |
| finkmoritz/csbcgf | `CSBCGF` |
| edo9300/ygopro-core | `IGNIS_CORE` |
| ProjectIgnis/CardScripts | `IGNIS_CORE` |

Az ocgcore és CardScripts ugyanazon rules/content ökoszisztéma két rétege, ezért ismétlődő pattern bizonyításakor nem számítanak két teljesen független forrásnak.

---

# 2. AETERNA authoritative rules boundary

A cross-project synthesis csak architecture-tanulságot adhat.

A Reaction/Priority és simultaneous-effect szabályokat az AETERNA hivatalos 1.4.3v alapjátékforrás határozza meg.

## 2.1 Már eldöntött AETERNA rules

1. reakciós ablak csak akkor nyílik, ha szabály, kártyaszöveg vagy az esemény természete engedi;
2. a reakciós ablak nem általános szabad kijátszási fázis;
3. a reaction eligibility az adott szabály/kártyaszöveg/esemény függvénye;
4. ha mindkét játékos reagálhat, az eseményt nem kezdeményező játékos kap első válaszlehetőséget, majd a másik;
5. pass lehetséges;
6. két egymást követő passz lezárja a reakciós ablakot;
7. a kötelező hatást fel kell oldani, ha végrehajtható;
8. az opcionális hatás használatáról a jogosult játékos az adott reakciós ablakban dönt;
9. reakcióra újabb reakció érkezhet;
10. minden új reakció a már függőben lévő esemény/reakció fölé kerül;
11. további válaszlehetőség akkor adható, ha azt szabály vagy kártyaszöveg megengedi;
12. a reaction chain alapértelmezett feloldása LIFO;
13. resolution előtt target/condition/source/relevancia és korábbi reaction hatása újraellenőrzendő;
14. lezárt event normálisan nem nyitható újra retroaktívan;
15. event csak stabil állapotban zárható le;
16. simultaneous effect esetén először az összes kiváltott hatást azonosítani kell;
17. külön sorrend hiányában az aktív játékos hatásai kerülnek előre, majd az ellenfél hatásai;
18. ha egy játékosnak több saját egyidejű hatása van, saját sorrendjüket ő választja meg, hacsak más szabály nem mond mást;
19. simultaneous feldolgozásnál külön vizsgálandó a kötelező/opcionális státusz és hogy nyílik-e reaction window.

## 2.2 Fontos korrekció az előző 0.1 synthesishez

Nem helyes a teljes multi-trigger orderinget „nyitott szabálykérdésként” kezelni.

A **base default ordering szabályszinten rögzített**.

Nyitva maradhat viszont:

- a választás pontos public contractja, ha egy játékos több saját simultaneous effectet rendez;
- optional effect és ordering interaction pontos engine-folyama;
- reaction resolution közben újonnan keletkező trigger batch ütemezése;
- külön szabály által felülírt ordering mechanikai reprezentációja.

---

# 3. P-RT-001 – Event creation és trigger detection külön lifecycle

**Pattern státusz:** `REPEATED_PATTERN`  
**Független family:** FORGE, MAGE, IGNIS_CORE  
**AETERNA státusz:** `AETERNA_CANDIDATE`

Általános lifecycle:

```text
EventCreated
    ↓
TriggerCandidatesCollected
    ↓
EligibilityChecked
    ↓
PendingTriggerBatch
    ↓
Ordering / optional decision
    ↓
Resolution entry
```

Az event bekövetkezése nem jelent azonnali effect executiont.

---

# 4. P-RT-002 – Pending state legyen explicit és folytatható

**Pattern státusz:** `REPEATED_PATTERN`  
**Family:** MAGE, IGNIS_CORE; FORGE részleges  
**AETERNA státusz:** `AETERNA_CANDIDATE`

A rules engine ne a call stackből vagy UI callbackből tudja, mire vár.

A pending állapot legyen:

- explicit;
- snapshotolható;
- determinisztikusan folytatható;
- headless/API szempontból lekérdezhető;
- viewer-safe módon projektálható.

---

# 5. P-RT-003 – Simultaneous trigger batch külön a resolution stacktől

**Pattern státusz:** `REPEATED_PATTERN`  
**Family:** FORGE, MAGE, IGNIS_CORE  
**AETERNA rules státusz:** `BASE_ORDERING_DECIDED`
**AETERNA engine státusz:** `NOT_FULLY_IMPLEMENTED`

## Rules oldal

Base default:

```text
identify all simultaneous effects
→ apply explicit mandatory ordering if any
→ active player's effects
→ opponent's effects
→ within one player's group: that player chooses own order
```

Emellett meg kell határozni:

- melyek optional/mandatory;
- megnyílik-e reaction window.

## Engine oldal

Ez erősen támogat egy külön:

```text
PendingTriggerBatchState
```

réteget, amely nem azonos a ReactionWindowval és nem azonos a ResolutionStackkel.

---

# 6. P-RT-004 – Priority owner authoritative state

**Pattern státusz:** `REPEATED_PATTERN`  
**Family:** MAGE, IGNIS_CORE, FORGE  
**AETERNA rules státusz:** `FIRST_PRIORITY_DECIDED`
**AETERNA production foundation:** `FIELD_ALREADY_EXISTS`

A jelenlegi AETERNA `MatchState` már tartalmaz `PriorityPlayerId` mezőt.

Reaction window nyitásakor:

- ha mindkét játékos jogosult, a non-initiator kapja;
- ha csak egy jogosult, az eligibility szabály határozza meg;
- a priority változása state transition.

---

# 7. P-RT-005 – Reaction declaration külön a resolutiontől

**Pattern státusz:** `REPEATED_PATTERN`  
**Family:** FORGE, IGNIS_CORE, CSBCGF részleges  
**AETERNA státusz:** `AETERNA_CANDIDATE`

```text
reaction candidate
→ declaration/action validation
→ resolution entry creation
→ további response opportunity, ha szabály/policy engedi
→ window closure
→ LIFO resolution
```

A reaction action beadása nem közvetlen effect mutation.

---

# 8. P-RT-006 – LIFO explicit resolution structure

**Pattern státusz:** `SUPPORTING`  
**AETERNA rules státusz:** `DECIDED`

AETERNA saját forrása rögzíti a reverse/LIFO feloldást.

Architecture követelmény:

- explicit ordered resolution entries;
- deterministic top-of-stack selection;
- stable entry identity;
- viewer-safe projection.

---

# 9. P-RT-007 – Resolution-time revalidation

**Pattern státusz:** `REPEATED_PATTERN`  
**AETERNA rules státusz:** `DECIDED`

Minimal pipeline:

```text
declaration validation
→ reaction window / pending layer
→ resolution entry selected
→ resolution-time revalidation
→ resolve as far as rules permit
→ no invented fallback
```

A revalidation legalitás, nem optional UI extra.

---

# 10. P-RT-008 – Resolution entry saját causality/context adatot hordozzon

**Pattern státusz:** `REPEATED_PATTERN`  
**Family:** MAGE, IGNIS_CORE, FORGE  
**AETERNA státusz:** `AETERNA_CANDIDATE`

Candidate mezők:

- entry ID;
- source instance/reference;
- controller;
- originating event ID;
- parent/correlation ID;
- effect/ability identity;
- declared target/choice context;
- trigger/declaration-time snapshot, ha a rules megköveteli;
- deterministic sequence.

A pontos contract későbbi döntés.

---

# 11. P-RT-009 – Replacement/prevention nem reaction és nem trigger

**Pattern státusz:** `REPEATED_PATTERN`  
**Family:** FORGE, MAGE  
**AETERNA státusz:** `HIGH_CONFIDENCE_ARCHITECTURE_CANDIDATE`
**AETERNA exact rules:** `DEFERRED_SEPARATE_GATE`

Általános candidate:

```text
proposed event/transition
→ replacement/prevention evaluation
→ modified / prevented / unchanged event
→ normal event lifecycle
```

A konkrét ordering/layer/choice szabályt nem szabad külső engine-ből importálni.

---

# 12. P-RT-010 – Continuous/static effect külön lifecycle

**Pattern státusz:** `REPEATED_PATTERN`  
**AETERNA státusz:** `ALREADY_SEPARATE_PRODUCTION_FOUNDATION`

A Reaction/Priority foundation nem veheti át a continuous/modifier authorityt.

---

# 13. P-RT-011 – Egyetlen Generic Pending List túl gyenge

**Pattern státusz:** `SYNTHESIZED_CANDIDATE`  
**AETERNA státusz:** `PROPOSED`

Szemantikailag eltér:

- trigger ordering;
- reaction response;
- optional decision;
- target choice;
- payment selection;
- replacement choice;
- resolution stack.

Közös coordinator megengedett, de typed state-ek szükségesek.

---

# 14. P-RT-012 – Engine advance-until-input

**Pattern státusz:** `REPEATED_PATTERN`  
**AETERNA státusz:** `AETERNA_CANDIDATE`

```text
advance deterministic internal rules
→ stop only at authoritative input boundary
→ expose legal actions / pending projection
→ accept version-guarded request
→ resume
```

Ez illeszkedik az AETERNA jelenlegi `ListLegalActions` + `SubmitAction` modelljéhez.

---

# 15. Optional/mandatory – korrigált státusz

## Rules szinten eldöntött

- explicit választási szöveg → optional;
- választási szöveg hiányában a teljesülő trigger alapértelmezés szerint mandatory;
- optional/mandatory státuszt nem lehet utólag engine-heurisztikával eldönteni;
- mandatory effect feloldandó, ha végrehajtható;
- optional effect használatáról a jogosult játékos az adott reaction windowban dönt.

## Contract szinten még eldöntendő

- optional trigger külön legal actionként jelenjen-e meg;
- vagy `PendingChoice` formájában;
- hogyan kapcsolódjon simultaneous orderinghez;
- hogyan jelenjen meg a viewer-safe pending summaryban.

---

# 16. Event closure – authoritative criteria

Az event closure nem pusztán „üres a stack”.

Closure csak akkor:

1. minden kapcsolódó mandatory effect létrejött és feloldódott;
2. minden megnyílt reaction window lezárult;
3. minden pending reaction/effect feloldódott vagy érvénytelenné vált;
4. zone transitionök végpontja meghatározott;
5. a game state újra egyértelmű/stabil.

Ez a későbbi coordinator egyik fő invariantja.

---

# 17. Minimal Reaction/Priority v1 – synthesis által támogatott határ

## V1-be javasolt

- explicit ReactionWindow state;
- existing `PriorityPlayerId` authority felhasználása;
- reaction candidate legal actions;
- pass action;
- two-pass closure;
- explicit LIFO resolution stack;
- resolution entry identity/context;
- resolution-time revalidation;
- deterministic state/event ordering;
- viewer-safe window/stack summary;
- existing `request_id` + `expected_state_version` megtartása;
- existing mandatory PendingTriggerWindow megtartása.

## Tudatosan V1-en kívül

- full generic multi-trigger batch runtime;
- replacement/prevention runtime;
- combat;
- Pecsét/Burst/Jel full special cases;
- generic nested target/payment/choice framework;
- replay persistence;
- networking/reconnect;
- spectator/debug policy véglegesítése.

A base simultaneous-ordering szabály ismert, de teljes runtime-ja külön slice lehet.

---

# 18. Fennmaradó valódi contract/rules-to-engine kapuk

## C1 – Further-response policy

A forrás szerint új reaction után a játékosok újabb válaszlehetőséget **kaphatnak, ha szabály vagy kártyaszöveg engedi**.

Ezért nem helyes univerzálisan feltételezni:

```text
minden reaction után automatikusan új teljes priority kör
```

A contractnak explicit policyból/legal-action generationből kell levezetnie, nyílik-e további response opportunity.

## C2 – Reaction resolution által létrehozott új trigger

Döntendő:

- az új trigger azonnal külön batchbe kerül;
- a jelenlegi top entry lezárása után;
- vagy a teljes current resolution stack után?

Ehhez további source/rules audit indokolt.

## C3 – Optional trigger public representation

A rules ismert, a contract schema nem.

## C4 – Simultaneous own-effect ordering public choice

A default rules ismert; a legal action/pending choice contract még nincs.

## C5 – Replacement/prevention

Külön későbbi rules gate.

---

# 19. Synthesis verdict

### Rulesból már eldöntött

- reaction window alapja;
- eligibility keret;
- non-initiator first;
- pass;
- two-pass closure;
- optional/mandatory alap;
- reaction stacking;
- LIFO;
- revalidation;
- event closure;
- base simultaneous-effect ordering;
- own simultaneous effects player-selected ordering.

### Architecture által erősen támogatott

- explicit priority;
- explicit reaction window;
- explicit resolution stack;
- typed pending state;
- causality/context ID;
- event/trigger/reaction/resolution külön lifecycle;
- replacement külön subsystem.

### Valóban nyitott

- further-response policy exact encoding;
- trigger generation during nested resolution;
- public optional-trigger representation;
- public own-trigger-order choice representation;
- replacement/prevention exact model.

---

# 20. Változásnapló

## 0.2 – 2026-08-15

- hivatalos 1.4.3v alapján korrigálva a simultaneous-effect ordering státusza;
- optional/mandatory rules státusz pontosítva;
- event closure authoritative invariantként rögzítve;
- further-response policy szűk, valódi contract-kérdésként elkülönítve;
- full multi-trigger runtime és base ordering rule különválasztva;
- current AETERNA priority/action/pending foundationhöz igazítva.

## 0.1 – 2026-08-15

- első öt-auditos synthesis.
