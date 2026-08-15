# AETERNA – CROSS-PROJECT SYNTHESIS: GODOT CLIENT AND UI

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első Godot/client/UI synthesis
- **Javasolt repository-útvonal:** `learning/synthesis/topics/godot_client_and_ui.md`
- **AETERNA production összevetési bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Nem AETERNA-szabályforrás.**

---

# 1. Evidence

Fő learning auditok:
- Ggross98/Godot-CardPileFramework;
- insideout-andrew/deckbuilder-framework;
- insideout-andrew/simple-card-pile-ui;
- Fulafu-ai/Fake3D Card UI Demo;
- TheSchlote/Godot-4-Card-Game-CSharp;
- Hearthstone.gd;
- Pali;
- Arcomage.

AETERNA current:
- Godot C# project;
- `GameEngineBridge`;
- JSON DTO boundary;
- `EngineSession` authoritative C# core;
- viewer-safe snapshot/events/legal actions.

---

# 2. P-UI-001 – Presentation state külön rules state-től

**Státusz:** `REPEATED_PATTERN`  
**AETERNA:** `HIGH_CONFIDENCE / CURRENT BOUNDARY`

Godot birtokolhat:
- hover;
- focus;
- drag state;
- selected visual;
- animation progress;
- card screen transform;
- z-index;
- tween;
- visual material/shader;
- tooltip open state.

Godot **nem** birtokolhat authoritative módon:
- zone;
- owner/controller;
- phase;
- priority;
- activity/exhausted rules state;
- legal target;
- payment legality;
- damage/vitals;
- trigger/reaction legality.

---

# 3. P-UI-002 – CardView stabil engine identityhoz kötődjön

UI card node:

```text
CardView
- CardInstanceId
- RenderModel
- PresentationState
```

A rules identity nem:
- scene node path;
- child index;
- current screen order;
- texture filename.

Engine snapshotból érkező `card_instance_id` a binding kulcs.

---

# 4. P-UI-003 – Child order layout, nem rules order

Több Godot UI framework scene child ordert használ pile/hand sorrendnek.

Ez presentationre kényelmes, rules authorityként veszélyes.

AETERNA:
- engine explicit ordered zone/list;
- UI ebből render ordert képez;
- UI child reordering nem változtat engine zone ordert submit nélkül.

---

# 5. P-UI-004 – Drag/drop = intent, nem commit

Jó interaction flow:

```text
pointer down
→ drag visual
→ candidate drop/target highlight
→ user releases
→ build engine ActionRequest
→ submit
→ accepted/rejected
→ reconcile presentation
```

Nem:

```text
drop
→ UI azonnal átparenteli canonical zónába
→ majd engine-t értesít
```

Optimistic visual preview lehet, de nem authoritative state.

---

# 6. P-UI-005 – Engine legal actions hajtják a UI affordance-et

UI:
- `ListLegalActions` alapján tudja, mi kattintható;
- disabled reasonből tud UX feedbacket adni;
- action payload schema/option list alapján építhet target/payment/choice UI-t.

Ne implementálja újra:
- phase rules;
- reaction timing;
- target validity;
- cost availability.

---

# 7. P-UI-006 – Pending decision külön UI mode

A `pending_decision_summary` és legal action surface alapján a UI explicit mode-ba léphet:

```text
NORMAL
TRIGGER_DECISION
REACTION_PRIORITY
TARGET_SELECTION
PAYMENT_SELECTION
ORDERING_CHOICE
```

A konkrét mode-lista bővíthető.

## Invariant

Mode state csak a current engine pending state projectionje.

UI nem tarthat fenn „még mindig reactionben vagyunk” állapotot engine confirmation nélkül.

---

# 8. P-UI-007 – Reaction/Priority UI

Candidate presentation:
- current priority player highlight;
- available reaction options;
- `pass_priority` explicit control;
- stack/resolution summary;
- opponent response-wait state;
- window close/resolve animation.

Hidden reaction candidates soha nem jelennek meg opponentnek.

UI nem tudja megjósolni, hogy opponentnek van-e reactionje, ha az hidden info.

---

# 9. P-UI-008 – Target selection two-stage

```text
engine legal action
→ option/schema says target selection required
→ UI visual candidate highlighting
→ user chooses target IDs
→ submit
→ engine final revalidation
```

Highlight candidate lista lehet engine-issued.

UI raycast önmagában nem rules filter.

---

# 10. P-UI-009 – Animation event/state következmény

Animation forrás:
- ActionResponse projected events;
- GetEvents continuation;
- snapshot diff/reconciliation.

Ne animation callback döntse el rules completiont.

Kivétel:
- UI lokálisan várhat animation végét következő vizuális lépés előtt,
- de engine authoritative state már eldőlt.

---

# 11. P-UI-010 – Visual event queue külön engine event store-tól

Candidate:

```text
Projected EngineEvent
→ PresentationEventMapper
→ VisualCue/AnimationCommand
→ AnimationQueue
```

Példa:
- `zone_move` → card fly animation;
- `card_readied` → ready pose;
- `phase_transition` → phase banner;
- `damage` → hit/vital animation.

A visual cue nem kerül vissza engine rules state-be.

---

# 12. P-UI-011 – Reconciliation first-class

Network/reconnect vagy rejected optimistic visual után:

```text
current authoritative PlayerSnapshot
→ reconcile CardViews/zones/vitals/pending UI
```

Minden CardView instance ID alapján:
- create;
- move;
- update;
- hide/reveal;
- remove.

A UI képes legyen teljes snapshotból újraépülni.

Ez reconnect és bug recovery miatt kulcsfontosságú.

---

# 13. P-UI-012 – Hidden info presentation projectionből

UI ne kapjon hidden definition/card identityt, majd csak hátlapot rajzoljon rá.

Ha snapshot szerint csak count/unknown card:
- generic hidden CardBackView;
- no hidden tooltip/name/art resource preload from authoritative payload.

Ez security és accidental leak ellen is fontos.

---

# 14. P-UI-013 – Hand/pile layout tiszta presentation component

Jó tanulságok a learning forrásokból:
- fan/curve layout;
- hover separation;
- drag lift;
- z-order management;
- smooth reparent/tween;
- multiple pile directions;
- card front/back transform.

Ezek külön reusable UI componentek lehetnek.

Nem kell rules-specific scriptet tartalmazniuk.

---

# 15. P-UI-014 – Card visual state machine hasznos, de csak presentation

Candidate visual states:

```text
Hidden
Idle
Hovered
Selected
Dragging
Disabled
Resolving
EnteringZone
LeavingZone
```

TheSchlote-féle state-machine szemlélet UI interakcióra értékes.

De:
- `Disabled` oka engine legal actionból jön;
- `Targetable` nem saját rules calculation.

---

# 16. P-UI-015 – Fake3D / shader profile külön material system

Fake3D és holographic források alapján:
- perspective tilt;
- shadow;
- glare;
- flash;
- dissolve;
- foil profile

külön visual/material layerként kezelhető.

Candidate:

```text
CardVisualProfile
CardRarityVisualProfile
FoilProfile
PerformanceTier
```

Nem card rules data.

---

# 17. P-UI-016 – Performance tier

Kártya shader/animation drága lehet.

Candidate client setting:
- LOW;
- MEDIUM;
- HIGH.

Gameplay ugyanaz.

Low tier:
- simplified shadow;
- no continuous glare;
- reduced particle/dissolve;
- lower animation complexity.

---

# 18. P-UI-017 – Accessibility külön presentation policy

Candidate:
- keyboard/gamepad navigation;
- reduced motion;
- color-independent state cues;
- scalable text;
- tooltip/readability mode;
- explicit disabled reason;
- confirmation for destructive/irreversible action where UX indokolja.

Ez termékdesign, nem learning source authority.

---

# 19. P-UI-018 – Input device adapter külön action intenttől

```text
Mouse/Touch/Gamepad/Keyboard
→ UI gesture
→ ActionIntent
→ engine action selection/request
```

Ne írjuk a rules UI-t kizárólag drag/dropra.

Ez később mobil/gamepad/accessibility miatt fontos.

---

# 20. P-UI-019 – Error/reject UX

Engine reject után:
- local visual preview rollback/reconcile;
- safe diagnostic display where useful;
- no state mutation retry guessing.

Stale request:
- refresh snapshot/actions;
- user-facing generic state-changed message lehet.

Developer message nem player UX text.

---

# 21. P-UI-020 – ViewModel/RenderModel candidate

A raw snapshot JSON-t ne minden Godot node külön parse-olja.

Candidate client layer:

```text
Bridge DTO
→ ClientStateStore / ViewModelBuilder
→ RenderModels
→ Scenes/Controls
```

StateStore:
- viewer-safe only;
- current state version;
- cards by instance ID;
- zones/order;
- legal actions;
- pending summary.

Nem authoritative rules state.

---

# 22. Anti-patternök

| ID | Név |
|---|---|
| `A-UI-001` | scene tree rules authority |
| `A-UI-002` | card node identity = rules identity |
| `A-UI-003` | child order = canonical zone order |
| `A-UI-004` | drop mutál state-et engine accept előtt |
| `A-UI-005` | UI újraszámolja legal actiont |
| `A-UI-006` | targetability raycastból |
| `A-UI-007` | animation callback completes rules effect |
| `A-UI-008` | hidden identity kliensben, csak hátlap mögött |
| `A-UI-009` | UI pending state drift engine-től |
| `A-UI-010` | raw snapshot JSON parsing szétszórva scene-ekben |
| `A-UI-011` | card visual shader rules fieldként |
| `A-UI-012` | drag/drop az egyetlen action modality |
| `A-UI-013` | rejected action silent UI correction |
| `A-UI-014` | visual event visszamutál engine state-et |

---

# 23. Verdict

Az E1-hez forráscoverage elegendő.

A jelenlegi AETERNA bridge határa jó és megtartandó.

A következő UI architecture feladat:
- client state/view-model layer;
- reusable CardView/ZoneView/HandLayout;
- legal-action driven interaction;
- pending/reaction/target UI;
- projected event animation mapping;
- reconciliation;
- visual/accessibility/performance profile.

Új UI framework keresése nem indokolt.
