# AETERNA – GODOT CLIENT / UI BLUEPRINT

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** client architecture blueprint
- **Javasolt repository-útvonal:** `Aeterna game engine/docs/blueprints/GODOT_CLIENT_UI_v0.1.md`
- **Repository-bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Rules authority:** Aeterna.Engine
- **Nem vizuális art-direction dokumentum.**

---

# 1. Fő elv

Godot = presentation + input + animation.

C# Engine = rules authority.

```text
Aeterna.Engine
    ↓
GameEngineBridge
    ↓
Client DTO / State Store
    ↓
ViewModels / RenderModels
    ↓
Godot Scenes / Controls
```

Visszafelé:

```text
Input/Gesture
→ UI ActionIntent
→ selected engine LegalAction
→ ActionRequest
→ Bridge SubmitAction
→ engine response
```

---

# 2. Current bridge – megtartandó

`GameEngineBridge`:
- creates session;
- gets player snapshot;
- lists legal actions;
- submits action;
- gets events/result;
- JSON serializes DTOs;
- exposes canonical package diagnostics.

Nem tart rules state-et.

Ez jó boundary.

---

# 3. ClientStateStore – proposed

Godot-side, viewer-safe cache:

```text
ClientStateStore
- MatchId
- ViewerPlayerId
- StateVersion
- ActivePlayerId
- PriorityPlayerId
- Phase
- PlayerViewModels
- CardViewModels by CardInstanceId
- ZoneViewModels + ordered IDs
- LegalActionSpace
- PendingDecisionSummary
- LastEventSequence
```

## Fontos

Ez **cache/projection**, nem authority.

Bármikor teljes snapshotból újraépíthető.

---

# 4. Reconciliation

`ApplySnapshot(snapshot)`:

1. update match/state metadata;
2. diff visible cards by instance ID;
3. create/remove CardViewModel;
4. update zones/order;
5. update player/vitals/resources;
6. replace legal-action space;
7. replace pending summary;
8. notify views.

Reconnect/resync ugyanazt a pathot használja.

---

# 5. CardViewModel

Candidate:

```text
CardInstanceId
DefinitionId? if visible
DisplayName? if visible
ArtRef? if visible
Owner/Controller if visible/public
Zone presentation
Activity/ready state
Visible stats
Keyword badges
Selectable/ActionRefs
```

Hidden card:
- no hidden definition identity in fair DTO;
- generic card-back model.

---

# 6. CardView presentation state

Local ephemeral:

```text
Hover
Focus
Selected
Dragging
AnimationState
ScreenTransform
ZIndex
MaterialProfile
TemporaryHighlight
```

Nem kerül engine-be.

---

# 7. ZoneView

Reusable presentation component.

Input:
- ordered visible card IDs;
- zone metadata;
- layout profile.

Examples:
- HandView;
- DomainView;
- WellspringView;
- VoidView;
- Library summary;
- hidden opponent hand count.

ZoneView nem végez draw/move/discard rules mutationt.

---

# 8. Layout components

Candidate reusable:

```text
HandFanLayout
PileLayout
Grid/DomainLayout
Stack/OverlayLayout
```

Configurable:
- spacing;
- curve;
- scale;
- orientation;
- overlap;
- max width;
- hover expansion.

---

# 9. Input architecture

```text
Pointer/Touch/Gamepad/Keyboard
→ InputAdapter
→ Gesture/Selection
→ ActionIntent
```

`ActionIntent` még nem ActionRequest.

UI ActionResolver megkeresi a current engine LegalActiont.

---

# 10. Action selection

## Simple button action
Example: advance phase, pass priority.

```text
button
→ legal action ID
→ Submit
```

## Card action
```text
CardView selected
→ candidate LegalActions for CardInstanceId
→ choose action family
→ if no more choice, Submit
```

## Structured action
```text
legal action
→ target/payment/order schema
→ interaction flow
→ final ActionRequest
```

---

# 11. Drag/drop

Drag is optional UX shortcut.

```text
start drag
→ local visual lift
→ highlight engine-approved target zones/options
→ release
→ map to legal action + payload
→ submit
```

Reject:
- animate/reconcile back.

Accepted:
- authoritative event/snapshot drives final zone placement.

---

# 12. PendingDecisionController

Single UI coordinator:

```text
PendingDecisionController
```

Consumes:
- pending summary;
- legal actions.

Routes to:
- TriggerDecisionUI;
- ReactionPriorityUI;
- TargetSelectionUI;
- PaymentSelectionUI;
- OrderingChoiceUI.

Only active branch receives input.

---

# 13. Reaction UI

Display candidate:
- reaction/timing banner;
- current priority indicator;
- own enabled reaction options;
- pass button;
- stack depth/visible entries as allowed;
- waiting-for-opponent state.

No opponent hidden option count.

`pass_priority` explicit.

---

# 14. Target selection

Engine legal option supplies candidate identity/schema.

UI:
- highlight targetable CardViews/zones;
- keyboard/gamepad cycle;
- min/max selection;
- confirm/cancel if policy permits.

Final submit includes target IDs.

Engine revalidates.

---

# 15. Event → visual cue mapping

```text
Projected EngineEvent
→ PresentationEventMapper
→ VisualCue
```

Candidate cues:
- move card;
- reveal/hide;
- ready/exhaust;
- damage/heal number;
- modifier badge;
- phase transition;
- reaction declared;
- reaction resolved;
- invalidated resolution;
- match result.

Mapper is presentation-only.

---

# 16. Animation queue

Animation can be:
- sequential;
- grouped;
- skippable/fast-forward.

Rules state already committed.

If events arrive faster:
- queue or compress visual cues;
- never block server/engine rules indefinitely.

---

# 17. Snapshot reconciliation vs animation

If a fresh authoritative snapshot disagrees with pending visual animation:

**snapshot wins.**

UI may:
- cancel tween;
- snap/reconcile;
- log presentation desync diagnostic.

Never modify engine to match animation.

---

# 18. Hidden information

Fair player client receives only viewer-safe DTOs.

Presentation:
- unknown card = card back;
- hidden hand = count/backs;
- hidden library = count;
- no hidden art/name/definition loaded from engine payload.

Local asset database may physically contain all art files, but gameplay DTO does not reveal which hidden card uses which asset.

---

# 19. Tooltips

Tooltip derives from visible RenderModel/definition catalog.

If card hidden:
- no true card tooltip.

Rules explanation may use:
- public card definition;
- keyword glossary;
- engine safe diagnostic.

---

# 20. Disabled action UX

Engine `includeDisabled=true` can support:
- greyed action;
- tooltip reason.

Map stable reason code → localized UX text.

Do not display raw developer diagnostic.

---

# 21. Visual profile system

Candidate:

```text
CardVisualProfile
RarityVisualProfile
FoilProfile
AnimationProfile
```

Properties:
- shader/material;
- hover tilt;
- glare;
- outline;
- dissolve;
- shadow;
- particles.

No rules semantics.

---

# 22. Performance tier

Client option:

```text
LOW
MEDIUM
HIGH
```

Same gameplay.

Heavy visual effects adapt or disable.

---

# 23. Accessibility

Blueprint candidate:
- keyboard/gamepad complete action path;
- reduced motion;
- scalable UI/text;
- color + shape/icon redundancy;
- readable target highlight;
- explicit current priority/phase/pending text;
- focus order;
- optional confirmation on irreversible UX actions.

Accessibility feature must not alter rules legal action surface.

---

# 24. Client diagnostics

Presentation-only diagnostics:
- missing CardView for visible ID;
- duplicate view binding;
- impossible zone render;
- event animation mapping unknown;
- stale local cache;
- bridge deserialize error.

These are client bugs, not gameplay events.

---

# 25. Testing strategy

## Pure client state tests
- snapshot → ViewModels;
- hidden projection;
- reconciliation.

## Input mapping tests
- legal action to intent;
- target choice payload;
- disabled action.

## Godot smoke
- create match;
- render basic state;
- advance phase;
- play card;
- pending trigger;
- later reaction.

## Visual smoke
- card move animation;
- hand reorder;
- resize;
- reduced motion.

Rules correctness remains engine tests.

---

# 26. Suggested folder shape – PROVISIONAL

Nem végleges kötelező struktúra:

```text
Godot/
├── C#/                    # current bridge
├── client/
│   ├── state/
│   ├── actions/
│   ├── pending/
│   ├── events/
│   └── diagnostics/
├── ui/
│   ├── cards/
│   ├── zones/
│   ├── match/
│   ├── pending/
│   └── common/
├── visuals/
│   ├── materials/
│   ├── shaders/
│   └── profiles/
└── tests/
```

A tényleges mappafa implementationkor változhat.

---

# 27. Implementation order candidate

E1.1 ClientStateStore + snapshot reconciliation  
E1.2 basic CardView/ZoneView  
E1.3 legal-action-driven click actions  
E1.4 event → visual cue queue  
E1.5 hand layout/drag UX  
E1.6 pending trigger UI  
E1.7 Reaction/Priority UI  
E1.8 target/choice UI  
E1.9 visual profiles/performance/accessibility  
E1.10 network resync reuse later

---

# 28. Non-goal

- final card art direction;
- final screen mockup;
- shader implementation;
- complete accessibility spec;
- mobile port;
- multiplayer backend;
- UI framework dependency selection.

---

# 29. Acceptance invariants

1. Godot cannot mutate MatchState directly;
2. every gameplay action maps to engine legal action;
3. hidden identity not required by presentation;
4. UI rebuildable from snapshot;
5. CardView bound by stable instance ID;
6. drag/drop not authority;
7. engine reject leaves UI reconciled;
8. animation not rules completion;
9. pending UI tracks engine pending state;
10. same action possible without drag where accessibility requires;
11. visual tier does not change gameplay;
12. viewer-safe events only.

---

# 30. Változásnapló

## 0.1 – 2026-08-15
- current GameEngineBridge határa formalizálva;
- ClientStateStore/ViewModel layer proposed;
- legal-action driven input;
- pending/reaction/target UI boundaries;
- event-animation separation;
- reconciliation/hidden info/performance/accessibility irány rögzítve.
