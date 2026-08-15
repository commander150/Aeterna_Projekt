# AETERNA – REACTION / PRIORITY FOUNDATION BLUEPRINT

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.2
- **Dátum:** 2026-08-15
- **Státusz:** konkrét contract-ajánlásokkal pontosított implementation-előkészítő blueprint
- **Javasolt repository-útvonal:** `Aeterna game engine/docs/blueprints/REACTION_PRIORITY_FOUNDATION_v0.2.md`
- **Repository-bázis:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Production engine alap:** Explicit Phase Foundation `2608345b61526097fc0b118f05461f92cfed0a95`
- **Rules authority:** `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4.3v`
- **Learning input:** current cross-project synthesis; nem authority
- **Cél:** minimal Reaction/Priority v1 contract technikai döntéseinek leszűkítése
- **Még nem implementation spec.**
- **Codex csak elfogadott contract után használható implementationre.**

---

# 1. V0.2 fő döntési eredmény

Az előző D1–D5 kérdésekre a jelenlegi production contracthoz legjobban illeszkedő ajánlás:

| ID | Kérdés | V0.2 ajánlás | Státusz |
|---|---|---|---|
| D1 | public action type | `react` + `pass_priority` | `PROPOSED_ACCEPT` |
| D2 | reaction candidate identity | engine-issued `reaction_option_id` a `react` payloadban | `PROPOSED_ACCEPT` |
| D3 | further-response | explicit typed `response_policy_id`; nem globális auto-handoff | `PROPOSED_ACCEPT` |
| D4 | state ownership | v1-ben közvetlen typed mezők a `MatchState`-ben; coordinator service, nem coordinator state container | `PROPOSED_ACCEPT` |
| D5 | snapshot | meglévő `pending_decision_summary` bővítése, nem új top-level mező | `PROPOSED_ACCEPT` |

Ezek technikai ajánlások, még nem hivatalos elfogadott contract.

---

# 2. Miért ez illeszkedik a jelenlegi engine-hez?

A production contract már:

- egyetlen `LegalActionSpace` felületet használ;
- action type + action ID + payload schema modellt használ;
- request ID és expected state version guardot használ;
- viewer snapshotban `priority_player_id` mezőt ad;
- viewer snapshotban már létezik generikus `pending_decision_summary`;
- mandatory triggernél egyetlen `resolve_triggered_ability` actiont ad, amelynek payloadja engine-issued optionöket enumerál;
- phase actionöket pending trigger alatt blokkolja.

A Reaction Foundationnek ezt a mintát kell bővítenie, nem párhuzamos API-t létrehoznia.

---

# 3. D1 – `react` + `pass_priority`

## Ajánlás: ELFOGADANDÓ

### `react`

Egyetlen generic reaction-declaration action type.

Nem jelent egyetlen reaction mechanikát.

Azt jelenti:

> a priority player az engine által kiadott egyik current reaction optiont deklarálja.

Később ugyanazon action type mögött lehet:

- reaction-capable Ige;
- Jel activation;
- explicit reaction ability;
- Burst, ha az adott format/rules aktív;
- más explicit response permission.

A rules különbséget az option metadata/ability/timing policy tartja meg.

### `pass_priority`

Kifejezetten a current reaction decisionről való lemondás.

Nem:
- phase skip;
- turn pass;
- trigger decline;
- optional effect decline általános helyettese.

---

# 4. D2 – engine-issued `reaction_option_id`

## Ajánlás: ELFOGADANDÓ

A current pending-trigger contracttal analóg:

```text
LegalAction:
    action_type = react

Payload:
    reaction_option_id
    target_selections
    payment_selections?   # csak későbbi támogatásnál
```

A payload schema felsorolja az adott viewer számára legal optionöket.

## Előny

A kliens nem adhat meg tetszőleges:

- card ID-t;
- ability ID-t;
- timingot;
- hidden reactiont;
- target schema-t.

Az option state-version kötött.

## Option candidate belső identity

Javasolt:

```text
reaction_option_id =
reaction:<window-id>:<sequence-or-stable-option-key>
```

A pontos formátum internal/contract részlet.

Az ID ne támaszkodjon kizárólag list indexre.

---

# 5. D3 – `response_policy_id`

## Ajánlás: ELFOGADANDÓ

A hivatalos forrás miatt **tilos** általános szabályként ezt hardcode-olni:

```text
minden reaction után a másik játékos automatikusan új response-t kap
```

A reaction/timing source mondja meg, hogy további response opportunity engedett-e.

## V1 támogatott policyk

Javasolt minimum:

```text
no_further_response
standard_alternating_response
```

Később:

```text
rule_defined
restricted_responder
```

## Hol éljen?

V1-ben:

- a ReactionWindow tart `CurrentResponsePolicyId` mezőt;
- reaction option deklarációja meghatározza a következő policyt;
- accepted reaction transition után a policy alapján vagy:
  - új decision opportunity jön;
  - vagy a window lezár/resolution indul.

---

# 6. ÚJ RULES CLARIFICATION – RC1

A hivatalos 4.5 szerint előfordulhat, hogy:

- csak a védekező;
- csak az érintett;
- csak a target owner;
- vagy más egyetlen játékos

reagálhat.

A **két egymást követő passzos closure** viszont explicit módon a „mindkét játékos reagálhat” eset után van definiálva.

## Nincs explicit official mondat erre:

```text
ha pontosan egy játékos jogosult,
annak egy passza lezárja a windowt
```

### Technikai ajánlás

Ez lenne a legtermészetesebb closure policy:

```text
required_passes = current eligible responder cycle size
```

tehát egyetlen eligible responder esetén egy pass.

### Státusz

`RULES_CLARIFICATION_REQUIRED`

Ezt a forrásba/OQ-ba később külön döntésként kell bevezetni, nem implementation assumptionként.

**V1 implementation csak a tisztázás után induljon**, ha single-responder windowt is támogatni akar.

Alternatíva a legelső v1 proofban:
- csak `both_players_eligible` window támogatott;
- single-responder timing kontrollált unsupported diagnostic.

---

# 7. D4 – state ownership

## Ajánlás: közvetlen typed MatchState mezők

V1-ben ne hozzunk létre új nagy `ResolutionCoordinatorState` konténert.

Javasolt:

```text
MatchState
├── PriorityPlayerId                 # már létezik
├── PendingTriggerWindow             # már létezik
├── ReactionWindow?                  # új
└── ResolutionStack                  # új
```

A coordination **service/code ownership** lehet külön:

```text
ReactionResolutionCoordinator
```

de az authoritative data ne legyen fölöslegesen új wrapper mögé rejtve.

## Miért?

- kisebb migration;
- kevesebb snapshot/debug refactor;
- könnyebb invariant validation;
- később még mindig összevonható coordinator state-be, ha tényleges igény lesz.

---

# 8. ReactionWindowState – V0.2 ajánlás

```text
ReactionWindowState
- ReactionWindowId
- UnderlyingEventId
- InitiatorPlayerId
- EligibleResponderPlayerIds
- CurrentResponsePolicyId
- ConsecutivePassCount
- OpenedAtStateVersion
- Status
```

## `EligibleResponderPlayerIds`

Ez nem a „kinél van tényleges reaction card?” lista.

Ez a rules által jogosult responder-kör.

A konkrét legal reaction option viewer-specifikusan számítódik.

Ez segít:
- first priority;
- pass rotation;
- RC1 closure későbbi kezelésében;
- restricted reaction permissionben.

## Hidden information

Ha a responder-jogosultság maga hidden rule-source-ból eredhetne, projection policy kell.

V1-ben csak public timing-derived responder set támogatása javasolt.

---

# 9. ResolutionStackEntryState – V0.2 ajánlás

```text
ResolutionStackEntryState
- ResolutionEntryId
- Sequence
- ReactionWindowId
- OriginatingEventId
- ParentResolutionEntryId?
- ControllerPlayerId
- SourceCardInstanceId?
- SourceAbilityId?
- SourceEffectId?
- ReactionOptionId
- DeclaredTargetSelections
- DeclarationStateVersion
- NextResponsePolicyId
```

A target selection immutable declaration contextként tárolandó.

Resolutionkor újra validáljuk, nem újraválasztjuk automatikusan.

---

# 10. D5 – snapshot/pending contract

## Ajánlás: meglévő `pending_decision_summary`

A production `PlayerSnapshot` már:

```text
pending_decision_summary: JsonElement
```

mezőt tart.

Ez kifejezetten jó bővítési pont.

## Reaction window summary

Candidate:

```json
{
  "has_pending": true,
  "pending_type": "reaction_window",
  "pending_window_id": "...",
  "underlying_event_id": "...",
  "priority_player_id": "...",
  "consecutive_pass_count": 0,
  "stack_depth": 2
}
```

## Existing trigger summary

Megmarad:

```text
pending_type = triggered_ability
```

## V1 invariant

Egyszerre egy externally blocking pending decision family legyen authoritative.

Tehát az első v1-ben:

```text
PendingTriggerWindow != null && ReactionWindow != null
```

tiltott state.

---

# 11. Legal action surface

## Normal phase

Változatlan.

## PendingTriggerWindow

Változatlan narrow mandatory-trigger gate.

## ReactionWindow

### Priority player

Enabled:

```text
pass_priority
react
```

`react` csak akkor enabled, ha legal option létezik.

**Pass akkor is enabled**, ha nincs reaction option, mert a window progressziójához szükséges.

### Másik player

Enabled action nincs.

### includeDisabled=true

Stable reasonök:

```text
reaction_window_open
not_priority_player
no_legal_reaction
```

A konkrét diagnostics nomenclature contract-specben rögzítendő.

---

# 12. `react` payload – V0.2 candidate

```json
{
  "reaction_option_id": "reaction:...",
  "target_selections": []
}
```

Később:

```json
{
  "reaction_option_id": "reaction:...",
  "target_selections": [],
  "payment_selections": []
}
```

A v1 lehetőleg olyan first vertical slice-t válasszon, ahol nincs új komplex payment selection.

---

# 13. Priority lifecycle – mindkét játékos jogosult eset

Official rules + proposed contract:

```text
window opens
→ PriorityPlayerId = non-initiator
→ pass OR react

pass
→ pass_count = 1
→ priority = other player

other pass
→ window closes
→ resolve top stack entry / underlying event

react
→ create stack entry
→ pass_count = 0
→ apply NextResponsePolicy
```

Ha `standard_alternating_response`:
- priority a másik eligible playerre kerül.

Ha `no_further_response`:
- window lezár;
- resolution indul.

---

# 14. Single-responder lifecycle

## V0.2 státusz

NEM végleges.

A blueprint két utat rögzít:

### A – rules clarification után
Ha elfogadjuk:
```text
single responder pass -> close
```
akkor ezt külön official decisionként rögzíteni kell.

### B – első implementationben nem támogatott
Single-responder window:
```text
CONTROLLED_UNSUPPORTED_REACTION_RESPONDER_POLICY
```

A foundation architektúrája viszont már képes legyen később támogatni.

---

# 15. Simultaneous trigger default ordering

Official default:

```text
identify all
→ special mandatory order if defined
→ active player group
→ opponent group
→ player orders own simultaneous effects
```

## V1 implementation scope

Nem kell full generic batch UI.

A state-designben fenntartjuk:

```text
PendingTriggerBatchState
```

mint későbbi typed layer.

A jelenlegi `PendingTriggerWindow` nem kerül tömeges refactorra csak azért, mert a későbbi modell már ismert.

---

# 16. Optional trigger

Rules státusz nagyrészt lezárt.

Engine/public contract nincs lezárva.

## V0.2 ajánlás

Full optional-trigger migration:
`DEFERRED_AFTER_REACTION_FOUNDATION`

Indok:
- ne keverjük a reaction core első proofját a simultaneous ordering + optional trigger UI problémával;
- a foundation tegye lehetővé későbbi `PendingChoice` vagy optional reaction option integrációját.

---

# 17. Reaction-created trigger – RC2

Továbbra is valódi nyitott ordering kérdés:

```text
reaction resolves
→ event emitted
→ new trigger(s) discovered
→ mikor kerülnek ordering/pending batchbe?
```

Lehetséges modellek:

A. current top entry után azonnal batch;  
B. teljes current reaction stack után batch;  
C. event-closure barrier szabály alapján.

Ezt nem szabad external engine alapján eldönteni.

`RULES_TO_CONTRACT_CLARIFICATION_REQUIRED`

---

# 18. Replacement/prevention

Külön subsystem.

V1 hard rule:

- nem `react`;
- nem ResolutionStack reaction entry;
- nem trigger;
- nem utólagos event correction.

Exact AETERNA rules:
`DEFERRED`.

---

# 19. Event closure

Official invariant:

Underlying event csak akkor close, ha:

```text
all related mandatory effects processed
AND all opened reaction windows closed
AND all pending reactions/effects resolved or invalid
AND zone transition endpoints settled
AND state unambiguous/stable
```

## V1 implementation recommendation

Ne vezessünk még full event-sourcing aggregate-et.

Legyen internal helper/invariant:

```text
CanCloseEvent(eventId)
```

vagy equivalens coordinator check.

A closed event ID ellen reaction request később determinisztikusan rejectelhető.

---

# 20. Technical event candidate

V1 minimum:

```text
reaction_window_opened
priority_passed
reaction_declared
reaction_window_closed
reaction_resolution_started
reaction_resolved
reaction_resolution_invalidated
```

Nem mind canonical gameplay event.

Kötelező correlation:

- window ID;
- underlying event ID;
- resolution entry ID ahol releváns.

ActionResponse viewer-safety current invariantját meg kell őrizni.

---

# 21. Atomicity / stale safety

Már meglévő contract:

- `request_id`;
- `expected_state_version`.

Reaction nem kap új concurrency modellt.

Reject esetén semmi nem változik:

- PriorityPlayerId;
- pass count;
- ReactionWindow;
- ResolutionStack;
- target/payment state;
- events;
- state version.

---

# 22. Implementation acceptance matrix

## Positive

1. supported event opens window;
2. non-initiator first when both eligible;
3. priority player sees `pass_priority`;
4. legal reaction option visible only to correct viewer;
5. wrong player cannot pass/react;
6. first pass transfers priority;
7. second consecutive pass closes;
8. accepted reaction creates entry, does not resolve early;
9. further-response policy respected;
10. two reaction entries resolve LIFO;
11. revalidation before each resolution;
12. invalidated target follows official partial/no-op semantics;
13. stale pass rejected atomically;
14. stale react rejected atomically;
15. phase actions blocked during window;
16. hidden opponent candidates not leaked;
17. deterministic event/action ordering;
18. existing pending trigger flow remains green;
19. existing 222-test suite remains green;
20. determinism 100/100 remains green.

## Negative

- reaction outside window;
- wrong responder;
- invalid option ID;
- option from previous state version;
- illegal target;
- option no longer legal at submit;
- phase advance during window;
- pending-trigger authority bypass attempt;
- closed event reaction;
- unsupported single-responder policy if RC1 not yet closed.

---

# 23. Recommended first vertical slice

A first proof should avoid:

- combat;
- Burst;
- Jel;
- replacement;
- extra payment choice;
- simultaneous own-order choice.

Javasolt proof shape:

```text
reactable canonical ability/event
→ both players reaction-eligible
→ player B first
→ B may pass or use one supported reaction option
→ optional further response policy
→ two-pass closure
→ LIFO resolution
→ target revalidation
→ stable event closure
```

A konkrét kártya/ability kiválasztása implementation előkészítéskor történjen a canonical database-ből.

---

# 24. Következő döntési lista

A D1–D5-re a v0.2 már konkrét ajánlást ad.

Implementation előtt még csak:

- **RC1** – single-responder pass closure;
- **RC2** – reaction resolution közben keletkező trigger batch boundary

igényel valódi rules/contract tisztázást a minimal design teljes általánosságához.

Ha az első vertical slice tudatosan kizárja ezeket, a foundation implementálható úgy is, hogy:

- csak both-player response policyt támogat;
- nested trigger creation esetén kontrollált unsupported pathot használ.

Ez nem végleges production coverage, hanem biztonságos first slice.

---

# 25. Változásnapló

## 0.2 – 2026-08-15

- D1–D5 konkrét ajánlással lezárva proposal szinten;
- `react` + `pass_priority` ajánlott;
- engine-issued `reaction_option_id` ajánlott;
- typed response policy ajánlott;
- direct MatchState state ownership ajánlott;
- existing `pending_decision_summary` bővítése ajánlott;
- új RC1 single-responder rules gap azonosítva;
- RC2 nested trigger boundary különválasztva;
- current public contract tényleges mezőihez igazítva.

## 0.1 – 2026-08-15

- első Reaction/Priority blueprint.
