# AETERNA – CROSS-PROJECT SYNTHESIS: AUTHORITY AND STATE

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.2
- **Dátum:** 2026-08-15
- **Státusz:** első synthesis + későbbi blueprint-program státuszfrissítés
- **Javasolt repository-útvonal:** `learning/synthesis/topics/authority_and_state.md`
- **Kiinduló repository HEAD:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Módszertan:** `CROSS_PROJECT_METHOD_v0.1`
- **Nem AETERNA-szabályforrás.**
- **Nem új production contract.**

---

# 1. Vizsgálati kérdés

Milyen authority- és state-elválasztási minták bizonyíthatók a már elkészült learning auditokból, és ezek közül melyek:

- már megvalósult AETERNA-elvek;
- további megerősítést igénylő minták;
- kifejezetten kerülendő hibamódok;
- még bizonyítékhiányos területek?

A témában elsődlegesen használt auditok:

- `learning/analyses/ch200c__durak-godot.md`
- `learning/analyses/rametta__pali.md`
- `learning/analyses/lunartides__hearthstone-gd.md`
- `learning/analyses/db0__godot-card-game-framework.md`
- `learning/analyses/valyreon__seven-card-game-godot.md`

A jelenlegi AETERNA összevetési alap:

- `Aeterna game engine/docs/ARCHITECTURE.md`
- production C# `Aeterna.Engine`
- `EngineSession` / `SubmitAction`
- player-visible snapshot és event projection
- Godot C# bridge

---

# 2. AETERNA jelenlegi authority invariantjai

A jelenlegi aktív architektúra már rögzíti:

1. pontosan egy authoritative state lehet;
2. ez a C# belső `MatchState`;
3. a UI nem szabályforrás;
4. state mutation csak validált engine transitionön keresztül történhet;
5. a kliens requestet küld, az engine response/event/projection réteget ad;
6. hidden information projectionnel védett;
7. a Godot/GDScript nem módosíthat authoritative state-et;
8. a pure C# engine nem függ Godottól;
9. a headless host ugyanazt az engine-t futtatja.

Ezért a synthesis elsődleges feladata itt nem új authority modell keresése, hanem:

- a meglévő modell külső tapasztalatokkal való stresszelése;
- a hibamódok katalógusának felépítése;
- a későbbi multiplayer/reaction/replay rétegek authority-követelményeinek pontosítása.

---

# 3. Pattern A – Rules authority külön a presentation state-től

**Státusz:** `REPEATED_PATTERN`  
**AETERNA státusz:** `ADOPTED + IMPLEMENTED + VERIFIED`

## Bizonyíték

### Durak.Godot – pozitív szerkezeti példa

A projekt külön pure .NET gameplay libraryt, Godot klienst és külön unit/functional tesztprojekteket tart fenn.

A rules/domain réteg Godot-függőség nélkül tesztelhető.

Ez erős bizonyíték arra, hogy ugyanazon repositoryn belül is fenntartható tiszta domain–presentation határ.

### db0 framework – negatív ellenpélda

A dictionary effectrendszer szemantikailag gazdag, de a végrehajtás:

```text
task
→ ScriptingEngine
→ global autoload
→ Card/CardContainer scene-node
→ közvetlen mutation
```

A view, runtime state és rules actor összekeveredik.

### Pali – negatív network ellenpélda

A dedicated server léte ellenére a scene tree és node propertyk alkotják a canonical state-et, és a teljes objektumgráf több peerben is jelen van.

### Hearthstone.gd – negatív peer-simulation példa

A Card/Blueprint/Player és feature module rendszer erős, de a rules state scene/resource réteghez kötött, és a játékállapot peer-replikációval terjed.

### Seven Card Game – negatív state-representation példa

A Deck/Hand/Pile/Card scene-node-ok egyben rules state-ek.

## Synthesis

A domain–presentation elválasztás nem pusztán kódstílus.

Közvetlenül javítja:

- authority egyértelműségét;
- headless tesztelhetőséget;
- multiplayer biztonságot;
- replay/szimuláció lehetőségét;
- UI-cserélhetőséget;
- AI-hozzáférést.

## AETERNA következtetés

A jelenlegi pure C# `Aeterna.Engine` + Godot bridge felosztás erősen megtartandó.

**Nincs indok architecture reopeningre.**

---

# 4. Pattern B – A dedikált szerver önmagában nem jelent authoritative rendszert

**Státusz:** `REPEATED_PATTERN`  
**AETERNA státusz:** `AETERNA_CANDIDATE` mint későbbi multiplayer invariáns

## Bizonyíték

### Pali

Van:

- dedicated server export;
- server-side turn validation;
- server-side score calculation;
- ENet lifecycle.

Mégis:

- a teljes paklisorrend és hidden identity eljut a kliensekhez;
- nincs state version;
- nincs request ID;
- hiányos ownership validation;
- a teljes scene tree több peerben canonical-like state-ként él.

### Hearthstone.gd

Van:

- ENet;
- packet dispatcher;
- anticheat;
- module-level validation;
- authority RPC.

Mégis a modell alapja:

```text
azonos vagy közel azonos szimuláció minden peer-en
```

nem pedig egyetlen viewer-projected authoritative state.

## Synthesis

A process/topology és az authority két külön kérdés.

```text
dedicated server != secure authority
in-process engine != weak authority
```

Az authority minőségét az dönti el, hogy:

- ki birtokolja a canonical state-et;
- hol történik a validáció;
- ki mutálhat;
- mit lát a kliens;
- van-e request/state-version contract;
- van-e reprodukálható transition history.

## AETERNA következtetés

A jelenlegi in-process C# engine authority modellje semmivel sem gyengébb pusztán azért, mert nincs külön szerverprocessz.

Későbbi online multiplayer esetén is a C# `MatchState` authorityt kell megtartani, és csak a transport/topology változhat.

---

# 5. Pattern C – Hidden information: projection, nem vizuális takarás

**Státusz:** `REPEATED_PATTERN`  
**AETERNA státusz:** `ADOPTED + IMPLEMENTED`

## Pozitív bizonyíték – Seven Card Game

A host:

- mindkét valódi kezet tárolja.

A kliens:

- saját valódi kézidentitást kap;
- az ellenfélről csak dummy hand/count információt kap.

Ez egyszerű, de valódi adat-szintű projection.

## Negatív bizonyíték – Pali

A kliens megkapja a teljes deck ordert és hidden card identityt; csak a presentation rejti el.

## Negatív bizonyíték – Hearthstone.gd

A teljes opponent deckcode/Blueprint eljut a klienshez, és a hidden modell vizuális.

## Synthesis

```text
face-down rendering != hidden information security
```

A rejtett információ csak akkor védett, ha a kliens adatmodellje sem tartalmazza a titkos identityt.

## AETERNA következtetés

A player-specific snapshot/event projection nem opcionális UI feature, hanem authority security boundary.

Későbbi multiplayer, replay és spectator rendszerben ezt külön invariánsként kell megőrizni.

---

# 6. Pattern D – Egyetlen validált mutation gate

**Státusz:** `REPEATED_PATTERN / strong negative evidence`  
**AETERNA státusz:** `ADOPTED + IMPLEMENTED + VERIFIED`

## Negatív bizonyíték

### Pali

Több `any_peer` RPC közvetlenül állapotot léptethet; nincs:

- state version;
- request ID;
- legal-action ID;
- teljes ownership/context validation.

### Seven Card Game

A kliens szerverelfogadás előtt optimistán módosíthatja saját kéz/pile state-jét.

### db0 framework

Effect execution közvetlenül scene-node state-et mutál.

### Hearthstone.gd

A packet/module rendszer ellenére state mutation és effectlogika több peerben és Godot objektumokon fut.

## Pozitív részpélda – Durak

A pure domain library explicit validációt és domain eventeket használ, bár a teljes orchestration egy része a Godot `MainNode`-ban marad.

## Synthesis

A helyes authority nem attól áll fenn, hogy „általában a szerver dönt”, hanem attól, hogy nincs megkerülő mutation út.

Szükséges invariáns:

```text
request
→ validation/preflight
→ final validation
→ atomic transition
→ state version
→ event
→ projection
```

## AETERNA következtetés

A `SubmitAction(ActionRequest)` vagy azzal egyenértékű belső transition gate kötelezően megőrzendő.

Reaction/Priority, Combat és későbbi multiplayer sem vezethet be párhuzamos mutation API-t.

---

# 7. Pattern E – Explicit state jobb, mint implicit kódpozíció vagy scene-tree állapot

**Státusz:** `REPEATED_PATTERN`  
**AETERNA státusz:** `ADOPTED + IMPLEMENTED`

## Bizonyíték

### Seven Card Game

A game state részben a futó `while`/`yield` coroutine aktuális kódpozíciójából következik.

Ez megnehezíti:

- snapshotot;
- reconnectet;
- replayt;
- state inspectiont;
- determinisztikus reprodukciót.

### Pali / db0 / Hearthstone.gd

A scene tree és node state jelentős rules-state szerepet kap.

## Synthesis

A game lifecycle állapotát adatként kell reprezentálni.

Példák:

- phase;
- active player;
- pending window;
- priority owner;
- pending choice;
- resolution stack;
- turn/round counter.

## AETERNA következtetés

Az Explicit Phase Foundation jó irány.

A Reaction/Priority Foundationnek szintén explicit state-et kell adnia; nem elég callback-, signal- vagy call-stack állapotként reprezentálni.

---

# 8. Pattern F – Pure domain library közvetlenül növeli a proof minőségét

**Státusz:** `OBSERVED`, erős pozitív bizonyíték  
**AETERNA státusz:** `ADOPTED + IMPLEMENTED`

## Bizonyíték – Durak

A pure .NET gameplay libraryre közvetlenül hivatkozik:

- unit test projekt;
- functional test projekt;
- Godot client.

Ez ugyanazt a rules kódot teszi elérhetővé presentation nélkül.

## AETERNA megfelelő

```text
Aeterna.Engine
├── Aeterna.Engine.Tests
├── Aeterna.Engine.Headless
└── Godot C# bridge
```

## Következtetés

A headless és Godot belépési pontnak ugyanazt az engine libraryt kell futtatnia.

Külön „UI rules” vagy külön „AI rules” réteg nem jöhet létre.

---

# 9. Első authority anti-pattern katalógus

| ID | Anti-pattern | Következmény |
|---|---|---|
| AUTH-A01 | scene tree mint canonical rules state | UI/rules csatolás, nehéz headless proof |
| AUTH-A02 | hidden data minden kliensen, csak vizuálisan rejtve | információszivárgás |
| AUTH-A03 | több peer ugyanazt a rules logicot mutálja | desync és authority bizonytalanság |
| AUTH-A04 | mutation közvetlen RPC-ből | validation megkerülhető |
| AUTH-A05 | nincs expected state version | stale request felismerése gyenge |
| AUTH-A06 | nincs request identity/idempotency | duplicate/replay request kockázat |
| AUTH-A07 | optimistic client rules mutation | rollback/desync kockázat |
| AUTH-A08 | implicit coroutine/call-stack game state | snapshot/reconnect/replay nehéz |
| AUTH-A09 | viewer projection helyett visual hiding | hidden-info boundary sérül |
| AUTH-A10 | domain orchestration visszacsúszik Godot node-ba | pure-engine határ erodálódik |

---

# 10. AETERNA-ra illesztett aktuális állapot

A korábbi authority synthesis alapmodellje változatlanul helyes:

```text
Authoritative MatchState
        ↓
single validated action gate
        ↓
atomic transition
        ↓
state version
        ↓
ordered internal events
        ↓
viewer-specific snapshot/event projection
        ↓
Godot / AI / network adapters
```

### Aktuális státusz a teljes pre-OQ blueprint-kör után

- `Authoritative MatchState` → `VERIFIED`
- `single mutation gate` → `VERIFIED`
- `viewer projection` → `IMPLEMENTED/VERIFIED`
- `explicit phase state` → `VERIFIED`
- `Reaction/Priority explicit pending state` → `BLUEPRINT_PROPOSED`, production implementation még nincs
- `persistent replay/event recovery` → `FIRST_SYNTHESIS_COMPLETE`, implementation deferred
- `reconnect/resync contract` → `BLUEPRINT_PROPOSED`, backend/implementation deferred
- `deterministic RNG state` → `FIRST_SYNTHESIS_COMPLETE`, konkrét RNG policy deferred
- `network request idempotency` → `BLUEPRINT_PROPOSED`, current local `request_id` még csak correlation identity
- `replacement/prevention authority boundary` → `ARCHITECTURE_CANDIDATE`, exact rules deferred
- `spectator/debug projection` → `DEFERRED_FEATURE`

---

# 11. A korábbi 18-auditos bizonyítékhiány státuszfrissítése

A 0.1 verzió idején valóban nyitott volt, hogy:

1. hogyan skálázódik a modell nagy rules engine-re;
2. hogyan kezelhető explicit pending/reaction/choice állapot;
3. hogyan épülhet replay/recovery;
4. hogyan működjön reconnect/resync;
5. hogyan váljon külön replacement/prevention/continuous dependency;
6. hogyan serializálható determinisztikus RNG;
7. hogyan különüljön player/debug/spectator projection.

A későbbi targeted auditok és synthesis hullámok ezek közül többet **architecture-szinten már megválaszoltak**, de nem mind implementation-szinten:

- rules-engine scale → Forge / MAGE / ocgcore;
- explicit pending/reaction → Reaction/Trigger/Resolution synthesis + blueprint;
- replay/RNG → boardgame.io + PokerKit + determinism/replay synthesis;
- AI/headless → OpenSpiel + RLCard;
- reconnect/session → Colyseus + Nakama + multiplayer blueprint;
- data/package → BabelCDB + Distribution + LorcanaJSON;
- release/diagnostics → R1 synthesis/blueprint;
- Godot/client projection → E1 synthesis/blueprint.

Tehát a régi `INSUFFICIENT_EVIDENCE` megállapítások **történeti állapotként maradnak fontosak**, de nem írják le a jelenlegi teljes learning programot.

---

# 12. Follow-up evidence és kapcsolódó dokumentumok

Az authority/state témát a következő aktív synthesis/blueprint rétegek egészítik ki:

- `reactions_triggers_resolution.md`
- `determinism_and_random.md`
- `serialization_save_replay.md`
- `ai_and_simulation.md`
- `multiplayer.md`
- `actions_and_validation.md`
- `events_and_projection.md`
- `data_and_content_pipeline.md`
- `ability_effect_systems.md`
- `diagnostics_and_observability.md`
- `godot_client_and_ui.md`

A teljes program állapotát a `PROJECT_CAPABILITY_MATRIX_v1.0.md` és `PATTERN_CATALOG_v1.0.md` foglalja össze.

Új learning projektet ezen a ponton már nem általános gyűjtési céllal, hanem konkrét capability/rules gap alapján érdemes felvenni.

---

# 13. Reaction/Priority kapcsolat – státuszfrissítés

A 0.1 authority synthesis már helyesen kizárta, hogy a Reaction/Priority:

- UI callback state legyen;
- Godot signal-lánc legyen az authority;
- process call-stackból következtetett állapot legyen;
- külön, az `EngineSession`-t megkerülő mutation API-t kapjon;
- implicit „most reagálhat” flagként több helyen éljen.

Azóta a `REACTION_PRIORITY_FOUNDATION_v0.2.md` ezt külön blueprintté konkretizálta.

Aktuális proposal-szintű state/contract irány:

```text
MatchState.PriorityPlayerId          # már létezik
ReactionWindowState?                 # proposed
ResolutionStackState                 # proposed
engine-issued reaction option        # proposed
react / pass_priority                # proposed
state-versioned submit               # existing foundation
viewer-safe pending projection       # existing + proposed extension
```

A Reaction blueprint továbbra sem elfogadott production contract automatikusan.

Nyitott kapuk:
- `RC1` – single-responder window closure;
- `RC2` – reaction resolution közben létrejövő trigger batch boundary;
- a D1–D5 technikai proposalok explicit emberi elfogadása.

---

# 14. Synthesis eredmény – aktuális

Az authority/state témában a teljes pre-OQ learning program továbbra sem indokol AETERNA architecture-irányváltást.

A már megvalósított:

- pure C# authoritative engine;
- single mutation gate;
- explicit MatchState;
- player-specific projection;
- Godot presentation boundary;
- headless ugyanazon engine fölött

külső pozitív és negatív evidence alapján is erős alap marad.

A 0.1-ben felsorolt follow-up területek közül a nagy rules-engine scale, replay/determinism, AI/headless, multiplayer/reconnect, data/package, release/diagnostics és Godot/client témákra azóta külön synthesis vagy blueprint készült.

A következő munka ezért már nem authority-evidence gyűjtés, hanem:

1. local source provenance manuális ellenőrzése és registry maintenance;
2. teljes blueprint consistency audit lezárása;
3. full `OPEN_QUESTIONS` review;
4. Reaction/Priority RC1/RC2 + D1–D5 döntési zárás;
5. elfogadott contract után implementation.

---

# 15. Változásnapló

## 0.2 – 2026-08-15

- a korábbi 18-auditos bizonyítékhiány történeti státuszra pontosítva;
- replay/RNG/network/AI/data/release/UI follow-up synthesis eredményei beemelve;
- az authority alapmodell változatlanul megtartva.


## 0.1 – 2026-08-15

- elkészült az első gyakorlati cross-project synthesis;
- elkülönült pozitív minta és negatív authority ellenpélda;
- létrejött az első authority anti-pattern lista;
- az AETERNA jelenlegi authority modellje megerősítést kapott;
- azonosításra kerültek a replay/network/rules-scale bizonyítékhiányok;
- Reaction/Priority számára authority-szintű szerkezeti követelmények készültek.
