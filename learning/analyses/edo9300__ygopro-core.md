# AETERNA – edo9300/ygopro-core ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott processor/chain source audit
- **Javasolt repository-útvonal:** `learning/analyses/edo9300__ygopro-core.md`
- **Repository:** `edo9300/ygopro-core`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `9a0c558c2d686542f7914a6d529fd7aa57746aed`
- **Commit dátuma:** 2026-08-12
- **Fő technológia:** C++ + beágyazott Lua
- **Licenc:** a vizsgált core source-ok SPDX fejléce `AGPL-3.0-or-later`
- **Elsődleges AETERNA-érték:** explicit resumable processor state machine, typed pending-input processzek, event/chain context, priority player és chain resolution
- **Vizsgálati korlát:** teljes rules audit, build, Lua integration teljes audit és kliensprotokoll audit ebben a körben nem történt
- **Kapcsolódó, külön auditált source family:** ProjectIgnis/CardScripts
- **Nem AETERNA-szabályforrás.**

---

# 1. Vizsgálati cél

A cél annak feltárása volt, hogy a rules core hogyan reprezentálja:

- a hosszú, több lépéses szabályfolyamatokat;
- a játékosválaszra váró pending state-et;
- priority/quick-effect folyamatot;
- eventeket;
- chain contextet;
- chain construction/resolutiont;
- cost/target/operation continuationt.

Az elemzés csak az AETERNA engine-tervezési tanulságokat rögzíti.

---

# 2. Vizsgált fő source-ok

| Terület | Fájl |
|---|---|
| typed process state | `processor_unit.h` |
| process execution | `processor.cpp` |
| processor/event/chain state | `field.h` |
| effect/card core | `effect.h/.cpp`, `card.h/.cpp` |
| Lua execution boundary | `interpreter.h/.cpp`, `lib*.cpp` |

---

# 3. Typed resumable process modell

A `processor_unit.h` sok külön process-típust definiál.

A közös alap:

- explicit `step`;
- compile-time `needs_answer` jelleg;
- move-olható process state.

Példák játékosinputra váró processzekre:

- `SelectEffectYesNo`;
- `SelectYesNo`;
- `SelectOption`;
- `SelectCard`;
- `SelectChain`;
- `SelectPosition`;
- `SortCard`.

Példák belső orchestration processzekre:

- `PointEvent`;
- `QuickEffect`;
- `PhaseEvent`;
- `AddChain`;
- `SolveChain`;
- `SolveContinuous`;
- `ExecuteCost`;
- `ExecuteTarget`;
- `ExecuteOperation`.

## AETERNA-következtetés

A rules engine működhet:

```text
advance
→ advance
→ advance
→ INPUT NEEDED
→ explicit pending state
→ answer
→ resume from exact step
```

Ez sokkal alkalmasabb:

- headless futásra;
- networkre;
- AI-ra;
- replayre;
- snapshotra

mint implicit callback/coroutine control flow.

---

# 4. Priority explicit process state

A `QuickEffect` process külön tart:

- `priority_player`;
- opponent-related state-et.

A `PhaseEvent` külön `priority_passed` állapotot tart.

A `field_info` priority-adatokat tart.

Ez azt mutatja, hogy a response-jogosultság és pass-progress rules-state.

## AETERNA-következtetés

A ReactionWindowben a priority owner és a pass progress explicit state legyen.

Az AETERNA pontos első priority és kétpasszos closure szabályát természetesen a saját 1.4.3v forrás adja.

---

# 5. Event mint first-class context

A `tevent` strukturált adatként tartalmaz:

- triggering card;
- event cardok;
- reason effect;
- event code;
- event value;
- reason;
- event player;
- reason player;
- global event ID.

A `raise_event` és `raise_single_event` ilyen objektumokat hoz létre, majd event queue-ba teszi őket.

Ez közvetlen tanulság:

> a kiváltó esemény identity/context ne vesszen el, amikor trigger vagy reaction születik belőle.

AETERNA számára az underlying event ID kulcsfontosságú lehet:

- reaction correlation;
- trigger correlation;
- diagnostics;
- replay;
- event closure.

---

# 6. Több külön event queue

A processor state több eventlistát tart:

- `point_event`;
- `instant_event`;
- `queue_event`;
- `delayed_activate_event`;
- `full_event`;
- `used_event`;
- `single_event`;
- `solving_event`;
- `sub_solving_event`.

A konkrét Yu-Gi-Oh jelentéseket nem szabad AETERNA-ra másolni.

A szerkezeti tanulság:

> event lifecycle több fázisú lehet, és a „megtörtént esemény” nem azonos a „jelenleg feloldott event contexttel”.

---

# 7. Chain context snapshot

A `chain` struktúra külön tárolja többek között:

- triggering state snapshot;
- triggering event;
- chain count;
- triggering player/controller;
- triggering location/position/sequence;
- event ID;
- triggering effect;
- target cards;
- operation information.

Ez nagyon erős evidence arra, hogy egy reaction/chain entrynek saját resolution-contextet kell hordoznia.

A forráskártya későbbi állapotából nem szabad minden adatot újrakövetkeztetni.

## AETERNA-candidate

Egy reaction stack entry legalább:

- source identity;
- controller;
- originating event;
- declared targets/choices;
- trigger/declaration-time snapshot, ha szabály szerint szükséges;
- effect/module identity;
- causality parent

adatot tarthat.

A pontos mezőket az AETERNA contract dönti el.

---

# 8. Chain construction és chain solving külön process

Külön typed process létezik:

- `SelectChain`;
- `SortChain`;
- `AddChain`;
- `SolveChain`.

Ez világos lifecycle-határt jelez:

```text
candidate responses
→ player selection
→ ordering
→ chain construction
→ chain solving
```

Az AETERNA mechanikája nem Yu-Gi-Oh chain, ezért a konkrét szabály nem másolható.

A külön lifecycle azonban erős architecture-minta.

---

# 9. Cost / target / operation continuation

Külön process:

- `ExecuteCost`;
- `ExecuteTarget`;
- `ExecuteOperation`.

Mindegyik:

- explicit stepet tart;
- az event contextből tölti a Lua paramétereket;
- coroutine yield esetén megáll;
- completion esetén tisztít és folytat.

Ez azt mutatja, hogy egy ability execution belsejében is lehet input/pending boundary.

## AETERNA-következtetés

Későbbi összetett abilitykhez a ReactionWindow önmagában nem elég.

Szükség lehet külön:

- PendingChoice;
- PendingTargetSelection;
- PendingPaymentSelection

typed state-ekre.

---

# 10. Core processor state gazdagsága

A `processor` külön tárol:

- main units;
- subunits;
- reserved unit;
- selection state-ek;
- event queue-k;
- current chain;
- külön forced/optional chain gyűjtemények;
- continuous solving állapot;
- delayed quick effectek;
- chain limits;
- chain-solving flag;
- reason effect/player;
- activity counterek;
- battle state;
- phase-related state.

## Pozitív tanulság

A komplex szabálymotorhoz rengeteg explicit intermediate state szükséges lehet.

## Negatív tanulság

A nagy shared mutable processor struktúra könnyen monolitikussá válhat.

AETERNA-nál ugyanez typed kisebb subsystem state-ekkel és coordinatorral tisztábban kezelhető.

---

# 11. Amit érdemes átvenni elvi mintaként

1. state machine advance-until-input;
2. typed pending process;
3. explicit continuation step;
4. priority owner mint state;
5. event identity és reason context;
6. chain/reaction entry context snapshot;
7. construction és resolution különválasztása;
8. cost/target/operation külön pending boundary lehet;
9. nested process/subprocess támogatás;
10. determinisztikusan folytatható orchestration.

---

# 12. Amit nem szabad átvenni

1. Yu-Gi-Oh timing/chain szabályokat;
2. numeric protocol ID-ket;
3. globális/masszív mutable core state szerkezetet;
4. C++ pointer-alapú domain object referenciákat;
5. Lua global API mint AETERNA ability contract;
6. AGPL kódot.

A tanulságot clean-room, typed C# formában kell újraalkotni.

---

# 13. AETERNA Reaction/Priority következtetés

A jelen source alapján erős architecture candidate:

```text
ResolutionCoordinator
    ├── PendingTriggerBatch
    ├── ReactionWindow
    ├── ResolutionStack
    ├── PendingChoice
    ├── PendingTargetSelection
    └── PendingPaymentSelection
```

Ezek nem feltétlen külön osztályok vagy publikus contractok; a lényeg, hogy a state-típusok szemantikailag elkülönüljenek és explicit módon folytathatók legyenek.

Replacement/prevention külön vizsgálati réteg marad.

---

# 14. Döntés

- **State-machine synthesis érték:** P0
- **Pending-input model érték:** P0
- **Reaction/priority relevancia:** P0
- **Resolution-context relevancia:** P0
- **Közvetlen kódátvétel:** nem
- **Clean-room architecture inspiráció:** igen
- **Teljes későbbi audit:** indokolt.
