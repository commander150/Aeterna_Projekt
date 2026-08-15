# AETERNA – magefree/mage ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott rules-engine source audit
- **Javasolt repository-útvonal:** `learning/analyses/magefree__mage.md`
- **Repository:** `magefree/mage`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `28fb5f005b60ecbaf10eecd69ced168a09866835`
- **Commit dátuma:** 2026-08-14
- **Fő technológia:** Java / többmodulos Maven projekt
- **Licenc:** MIT (`LICENSE.txt`)
- **Elsődleges AETERNA-érték:** explicit authoritative GameState, priority state, stack, trigger/delayed trigger állapot, rollback/copy, replacement külön effect type
- **Vizsgálati korlát:** build, teljes tesztfuttatás, teljes UI/server audit és teljes rules flow audit ebben a körben nem történt
- **Nem AETERNA-szabályforrás.**

---

# 1. Vizsgálati cél

A cél annak feltárása volt, hogy egy nagy TCG motor:

- hol tárolja az authoritative runtime state-et;
- hogyan reprezentálja a priorityt;
- hogyan választja szét a stacket, triggereket és delayed triggereket;
- hogyan kezeli a raised-but-not-resolved triggereket;
- hogyan tárol trigger contextet;
- hogyan ellenőriz újra resolutionkor;
- hogyan különíti el a replacement effectet a normál effect executiontől.

---

# 2. Vizsgált fő source-ok

| Terület | Fájl |
|---|---|
| authoritative state | `Mage/src/main/java/mage/game/GameState.java` |
| trigger lifecycle | `Mage/src/main/java/mage/abilities/TriggeredAbilityImpl.java` |
| replacement type | `Mage/src/main/java/mage/abilities/effects/ReplacementEffectImpl.java` |
| game orchestration | `Mage/src/main/java/mage/game/GameImpl.java` |
| tests | `Mage.Tests/` |

---

# 3. Explicit authoritative GameState

A `GameState` explicit, másolható/restore-olható állapotobjektum.

A source megjegyzése külön figyelmeztet arra, hogy a state másolható és visszaállítható, ezért objektum-instance identityra nem szabad stabil referenciaként építeni; stabil ID szükséges.

A state többek között tartalmazza:

- players;
- turn order;
- active player;
- **priority player**;
- player-by-order;
- turn/phase;
- stack;
- continuous effects;
- normal triggers;
- delayed triggers;
- már felismert, resolutionre váró triggered abilityk;
- simultaneous events;
- combat;
- zónák;
- card state;
- zone-change counter;
- copied-card state.

Ez AETERNA számára erős minta:

> priority, stack, pending trigger és lifecycle state authoritative adat, nem UI- vagy call-stack állapot.

---

# 4. State copy / restore

A `GameState`:

- copy constructort;
- `restore`;
- `restoreForRollBack`

mechanizmust tartalmaz.

A teljes részletes rollback-modell nem került auditálásra, de a szerkezetből biztosan látható, hogy a rules state másolhatóságát elsőrendű követelményként kezeli.

AETERNA szempontból ez megerősíti:

- stable identity;
- explicit serializálható/klónozható pending state;
- replay/simulation irány előkészítése

fontosságát.

---

# 5. Explicit priority state

A `GameState` külön:

```text
priorityPlayerId
```

mezőt tart, getter/setterrel.

A priority tehát a canonical state része.

Az AI state-value képzés is beleszámolja:

- active player;
- priority player;
- pass state;
- stack state;
- target state.

Ez erős bizonyíték arra, hogy a priority változása rules-releváns state változásként kezelhető.

## AETERNA-következtetés

A Reaction/Priority foundationben az aktuális response-jogosult játékost explicit state-ként kell tárolni.

Nem elég a hívási sorrendből vagy controller callbackből következtetni.

---

# 6. Trigger létrejötte és resolution különválik

A `TriggeredAbilityImpl.trigger(...)`:

1. ellenőrzi az intervening-if feltételt;
2. ellenőrzi a trigger conditiont;
3. frissíti a per-turn/per-game trigger countot;
4. átadja a triggered abilityt a game state/orchestration rétegnek a triggering eventtel.

A trigger ekkor még nem azonos a végleges effect resolutionnel.

A trigger object explicit tárolja a triggering eventet.

AETERNA-következtetés:

A pending triggernek meg kell őriznie legalább:

- source/ability identity;
- triggering event identity/context;
- controller/decision owner;
- mandatory/optional jelleg;
- szükséges trigger-time snapshotot.

---

# 7. Resolution-time revalidation

Az intervening-if condition:

- trigger pillanatban;
- majd `resolve(...)` során újra

ellenőrzésre kerül.

Ez különösen értékes AETERNA számára, mert a hivatalos szabály szerint reactionök után a feloldás előtt újra kell ellenőrizni a releváns feltételeket/célokat/forrást.

A pontos AETERNA revalidation policy természetesen saját szabályból származik.

---

# 8. Optional trigger explicit state

A triggered ability külön `optional` állapotot tart.

Resolutionkor:

- megkeresi a döntésre jogosult playert;
- az opcionális döntést kéri;
- csak elfogadás után folytatja.

AETERNA-következtetés:

Az optional/mandatory jelleg contractadat, és a pending choice ownerének explicitnek kell lennie.

---

# 9. Normal / delayed / raised trigger állapot szétválasztása

A `GameState` külön tart:

- registered normal triggers;
- delayed triggers;
- `triggered` listát, amely már raised, resolutionre váró triggereket tartalmaz.

Ez fontos rendszerhatár:

```text
registered trigger
→ event megfelel
→ raised pending trigger
→ ordering / stack
→ resolve
```

Az AETERNA `PendingTriggerWindow` továbbfejlesztésénél ezt a lifecycle-szétválasztást érdemes megőrizni.

---

# 10. Replacement effect külön semantic type

A `ReplacementEffectImpl`:

- continuous-effect alapra épül;
- `EffectType.REPLACEMENT`;
- a normál `apply()` hívást kifejezetten hibának tekinti és exceptiont dob.

Ez azt bizonyítja, hogy a replacement nem egyszerűen „egy effect, ami korábban fut”.

Saját evaluation path szükséges.

A repositoryban a `replaceEvent(...)` contract széles körben használt.

## AETERNA-következtetés

A prevention/replacement réteg külön event-interception szemantikát igényel.

Nem érdemes ReactionWindow entryként modellezni.

---

# 11. Stable identity és zone-change identity

A state:

- UUID-kat;
- zone-change countert;
- object reference modellt

használ.

A részletes object-lifecycle szabály nem került teljes auditálásra, de a state copy/restore cél miatt a stabil azonosítás elsőrendű.

AETERNA current instance-ID és zone-move iránya ezzel kompatibilis.

---

# 12. Tesztelési jel

A vizsgált HEAD maga is tesztmódosítást tartalmaz, és a repository külön `Mage.Tests` modult tart fenn.

A legutóbbi commit egyik tesztje konkrét játékszituációt állít fel, fázisig futtatja a motort, majd state-et assertál.

Ez erős candidate a későbbi `testing_and_scenarios` synthesishez.

---

# 13. Amit érdemes átvenni elvi mintaként

1. priority mint explicit state;
2. registered / delayed / raised trigger különállás;
3. trigger event context tárolása;
4. resolution-time condition revalidation;
5. optional/mandatory explicit jelleg;
6. stable ID és zone-change identity;
7. copy/restore-barát rules state;
8. replacement külön semantic execution path;
9. scenario-szintű rules test.

---

# 14. Amit nem szabad közvetlenül átvenni

1. Magic-specifikus priority/stack szabályok;
2. Java osztályhierarchia;
3. teljes mutable object graph;
4. konkrét effect API;
5. konkrét event classok és card implementationök.

AETERNA saját szabálya és typed C# contractja az authority.

---

# 15. AETERNA Reaction/Priority következtetés

A minimal foundation számára különösen erős javaslat:

```text
MatchState
├── CurrentPhase
├── PendingTriggerBatch?
├── ReactionWindow?
│   └── PriorityPlayerId
├── ResolutionStack
└── PendingChoice?
```

Ez csak architecture candidate, nem végleges contract.

A fő elv:

> minden externally observable vagy executiont blokkoló pending state legyen explicit, másolható és determinisztikusan folytatható.

---

# 16. Döntés

- **Rules-engine synthesis érték:** P0
- **Priority state érték:** P0
- **Trigger lifecycle érték:** P0
- **Replacement érték:** P0
- **Közvetlen kódátvétel:** nem szükséges
- **Clean-room elvi használat:** igen
- **Teljes későbbi audit:** indokolt.
