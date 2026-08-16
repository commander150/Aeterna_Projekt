# AETERNA – REACTION / PRIORITY FOUNDATION CONTRACT

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0
**Dátum:** 2026-08-16
**Státusz:** `ACCEPTED_FOR_IMPLEMENTATION`
**Javasolt repository-útvonal:** `Aeterna game engine/docs/REACTION_PRIORITY_CONTRACT.md`
**Repository-bázis:** `7af5bf7fec7b762ec41d1368b072ff6a3d818f5e` – `docs: update project guidance after OQ and learning sync`
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95` – `engine: add explicit phase foundation`
**Rules authority:** `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4.3v.docx`
**Current decision authority:** `OPEN_QUESTIONS_DECISIONS.md` v2.2
**Technical evidence/proposal input:** `blueprints/REACTION_PRIORITY_FOUNDATION_v0.2.md`
**Implementation:** `NOT_STARTED / NEXT`

Ez a dokumentum a Reaction / Priority Foundation első production implementációs
slice-ának contractja.

Ez a dokumentum explicit emberi elfogadás után a Reaction / Priority Foundation v1
első production implementation slice-ának aktív contract-authorityja.

Elfogadott végrehajtási út:

```text
official rules
+ OQ current decisions
+ jelen contract
→ Codex production implementation
→ tests
→ adversarial audit
→ PASS
→ user commit/push
```

---

# 1. Cél

A Reaction / Priority v1 célja egy olyan minimális authoritative protocol,
amely:

- explicit reaction windowt tud nyitni;
- priorityt tud adni a megfelelő játékosnak;
- `react` és `pass_priority` public actiont ad;
- több reactiont egymásra tud helyezni;
- LIFO módon tud feloldani;
- resolutionkor újravalidál;
- ordinary trigger creationt nem aktivál túl korán;
- viewer-safe snapshotot és eventet ad;
- megőrzi a jelenlegi stale-request és atomic reject contractot;
- nem keveri össze a Reaction Foundationt a Combattal vagy a teljes pending-choice rendszerrel.

---

# 2. Authority és forráselsőbbség

Ha eltérés van:

1. official base-game rules source;
2. explicit current human decision / OQ decision;
3. jelen contract;
4. blueprint;
5. learning/synthesis;
6. implementation.

A blueprint proposal wordingje nem írhatja felül a frissebb OQ v2.2 döntést.

Különösen:

- D1–D5 current default;
- RC1 current default;
- RC2 current default

nem proposal státuszú ebben a contractban.

---

# 3. Official/current rules foundation

A v1 a következő már lezárt rules foundationre épül:

- reaction window meghatározott event és final resolution között nyílhat;
- nem minden event nyit reaction windowt;
- ha mindkét játékos eligible, a non-initiator kapja az első opportunityt;
- pass megengedett;
- mindkét játékos eligible esetén két egymást követő passz zárja a windowt;
- reaction reactionre épülhet;
- feloldás LIFO;
- target/condition/source relevance resolutionkor újraellenőrzendő;
- korábbi reaction módosíthatja vagy megakadályozhatja a későbbi resolutiont;
- closed event nem nyílik vissza retroaktívan;
- simultaneous trigger ordering általános alapja official;
- mandatory vs optional trigger semantics official.

A v1 nem importál globális Yu-Gi-Oh `when/if` vagy missed-timing nyelvi szabályt.

---

# 4. Current technical defaults

A contract current defaultként rögzíti:

```text
D1  public action:
    react
    pass_priority

D2  reaction identity:
    engine-issued reaction_option_id

D3  further-response:
    typed response_policy_id

D4  authoritative state:
    MatchState

D5  viewer projection:
    existing pending_decision_summary
```

RC1:

```text
single eligible responder
→ one opportunity
→ pass closes the window
```

RC2:

```text
committed gameplay event
→ trigger discovery/creation immediately
→ queued trigger batch
→ current reaction/effect cycle continues
→ entire current cycle unwinds
→ post-resolution trigger checkpoint
→ queued batches processed
```

Different-timing batch:

```text
FIFO by originating committed EngineEvent.event_sequence
```

Same-timing batch:

```text
official simultaneous ordering
```

---

# 5. V1 non-goals

Az első production slice NEM tartalmazza:

- combat;
- attack / block;
- Pecsét full model;
- Refresh Penalty;
- generic prevention/replacement subsystem;
- full optional-trigger UI;
- full simultaneous-trigger ordering-choice UI;
- full compound pending choice framework;
- reaction-specific új payment-selection framework;
- Burst teljes implementáció;
- Jel teljes implementáció;
- every future special timing policy;
- global strict-event-window / missed-timing rendszer;
- multiplayer retry/idempotency redesign;
- replay system redesign;
- event-sourcing architecture rewrite.

Ezek reserved vagy későbbi külön slice-ok.

---

# 6. Meglévő public contract megőrzése

A v1 nem hoz létre új public request API-családot.

Megmarad:

```text
EngineSession.CreateMatch
EngineSession.GetPlayerSnapshot
EngineSession.ListLegalActions
EngineSession.SubmitAction
EngineSession.GetEvents
EngineSession.GetMatchResult
```

Megmarad a jelenlegi:

```text
ActionRequest
ActionResponse
LegalAction
LegalActionSpace
PlayerSnapshot
EngineEvent
```

top-level struktúra.

## 6.1 Schema-version policy

A v1 első implementációjában nem szükséges top-level schema bump pusztán azért,
mert:

- új `action_type` jelenik meg;
- új `event_type` jelenik meg;
- a generikus `pending_decision_summary` új `pending_type` értéket kap.

Current target:

```text
ActionRequest       v1 – unchanged
ActionResponse      v0 – unchanged top-level shape
LegalActionSpace    v1 – unchanged top-level shape
PlayerSnapshot      v4 – unchanged top-level shape
EngineEvent         v0 – unchanged top-level shape
```

Ha implementation közben új top-level mező válik szükségessé,
schema bump kötelező.

---

# 7. MatchState bővítés

Current `MatchState` bővül:

```text
MatchState
├── PriorityPlayerId                     # existing
├── PendingTriggerWindow?                # existing
├── ReactionWindow?                      # new
├── ResolutionStack                      # new
├── QueuedTriggerBatches                 # new
├── NextReactionWindowSequence           # new deterministic counter
├── NextReactionSubjectSequence          # new deterministic counter
└── NextResolutionSequence               # new deterministic counter
```

A Reaction coordination külön service lehet:

```text
ReactionResolutionCoordinator
```

de nem tarthat külön authoritative state-et.

A timing/eligibility/response policy számítás külön typed service:

```text
ReactionPolicyResolver
```

Ez sem tarthat párhuzamos authoritative match state-et.

# 8. ReactionWindowState – minimum contract

```text
ReactionWindowState
- ReactionWindowId
- ReactionSubjectId
- OriginatingEventId?
- OriginatingEventSequence?
- UnderlyingResolutionId
- InitiatorPlayerId
- EligibleResponderPlayerIds
- CurrentResponsePolicyId
- ConsecutivePassCount
- OpenedAtStateVersion
```

## 8.1 ReactionWindowId

Követelmény:

- matchen belül unique;
- deterministic;
- clock/random/GUID nélkül generálható;
- monotonikus state-owned sequence-ből származik.

Candidate:

```text
reaction-window:<match-id>:<sequence>
```

Pontos string formátum internal detail lehet,
de determinisztikusnak kell maradnia.

## 8.2 ReactionSubjectId

A reaction window elsődleges korrelációs azonosítója.

Nem azonos a current `EngineEvent.EventId` fogalmával.

A rules source „esemény” fogalma tágabb annál, mint amit a jelenlegi
committed `EngineEvent` history objektum reprezentál. Egy még fel nem oldott
canonical ability resolution több gameplay EngineEventet is kibocsáthat.

Ezért v1-ben:

```text
ReactionSubjectId
!=
reserved future EngineEvent.EventId
```

Követelmény:

- unique és deterministic;
- a window teljes életciklusa és stackje erre hivatkozik;
- lezárás után nem használható új window megnyitására ugyanazon subjecthez,
  hacsak future explicit rule nem engedi.

Candidate:

```text
reaction-subject:<match-id>:<sequence>
```

## 8.3 OriginatingEventId / OriginatingEventSequence

Opcionális correlation.

Csak akkor töltött, ha a reaction timingot egy **már committed**
authoritative gameplay `EngineEvent` nyitotta.

Ha a subject egy még fel nem oldott ability/declaration:

```text
OriginatingEventId = null
OriginatingEventSequence = null
```

V1 nem foglal le előre későbbi `EngineEvent` ID-t.

## 8.4 UnderlyingResolutionId

A `ResolutionStack` bottom entryjének canonical resolution ID-ja.

Ennek kell reprezentálnia azt a még fel nem oldott authoritative resolutiont,
amely miatt a reaction window létrejött.

## 8.5 InitiatorPlayerId

Az underlying subject/ability kezdeményezője.

Both-player eligibility esetén az official default szerint
a másik játékos kapja az első priorityt.

## 8.6 EligibleResponderPlayerIds

Rules-derived responder set.

Ez **nem** a „kinél van tényleges reaction card?” lista.

V1:

- 1 vagy 2 player ID;
- public timing-derived eligibility;
- hidden eligibility rule nem része az első slice-nak.

A legal reaction option ettől külön viewer/player-specifikusan számítódik.

## 8.7 CurrentResponsePolicyId

A current priority lifecycle typed policy-ja.

Lásd 13. fejezet.

## 8.8 ConsecutivePassCount

- window nyitáskor `0`;
- accepted reaction után `0`;
- accepted pass után +1;
- closure után state-ből eltűnik a window.

## 8.9 OpenedAtStateVersion

A window létrejöttével eredményezett authoritative state verzió.

Ha a window egy accepted action N → N+1 transitionjében nyílik:

```text
OpenedAtStateVersion = N + 1
```

Nem helyettesíti az ActionRequest `expected_state_version` guardját.

# 9. ResolutionStack – alapmodell

A v1-ben a stack nem csak reaction entryket tartalmaz.

Minimum:

```text
bottom:
underlying canonical ability resolution

above it:
reaction resolution 1
reaction resolution 2
...
top
```

Ez kötelező, mert a reaction window több külön public `SubmitAction`
között is nyitva maradhat.

Az underlying unresolved **ability-resolution contextet**
authoritative state-ben persistálni kell.

A v1 nem épít általános „minden jövőbeli rules object” stack frameworköt.
A first slice executable resolution familyje canonical ability resolution.

# 10. ResolutionStackEntryState – minimum contract

```text
ResolutionStackEntryState
- ResolutionId
- Sequence
- EntryKindId
- ReactionWindowId
- ReactionSubjectId
- ParentResolutionId?
- AbilityResolution
- ReactionOptionId?
- NextResponsePolicyId?
```

Nested typed context:

```text
CanonicalAbilityResolutionState
- ResolutionOriginId
- SourceActionId?
- SourceActionType
- AbilityId
- SourceCardInstanceId
- SourceCardId
- SourceZoneSequenceAtDeclaration
- SourceRelevancePolicyId
- ControllerPlayerId
- DeclaredTargetSelections
- PendingTriggerId?
- TriggerId?
- DeclarationStateVersion
```

## 10.1 ResolutionId

Unique és deterministic.

A stack `ResolutionId` **ugyanaz az identity**, amelyet a current
`CanonicalAbilityResolutionContext.ResolutionId` használ.

Nem vezetünk be párhuzamos „stack entry ID” + „ability resolution ID” párost.

Candidate:

```text
resolution:<match-id>:<sequence>
```

## 10.2 Sequence

State-owned monotonic sequence.

A stack orderinget nem string sort és nem list-index identity határozza meg.

## 10.3 EntryKindId

V1:

```text
underlying_resolution
reaction
```

Más entry-kind csak külön contractbővítéssel.

## 10.4 ResolutionOriginId

V1 first-slice minimum:

```text
played_card
reaction
```

A current executor `CanonicalResolutionOrigin` enumja ezért `Reaction`
értékkel bővítendő.

`triggered_ability` mint reactable underlying subject külön későbbi integration,
mert a current `PendingTriggerWindow` + ReactionWindow compound lifecycle
nem része az első slice-nak.

## 10.5 ParentResolutionId

Reaction entrynél az a resolution,
amely a declaration pillanatában közvetlenül alatta volt.

Underlying entrynél `null`.

## 10.6 Source relevance – v1

A first slice egyetlen támogatott policy-ja:

```text
same_zone_presence
```

Ezért tárolandó:

```text
SourceCardInstanceId
SourceZoneSequenceAtDeclaration
```

Resolutionkor a source ugyanazon authoritative zone-presence objektum kell legyen.

Ez tudatos first-slice scope:

- public/in-play source ability;
- nincs Burst;
- nincs Jel;
- nincs hand-spell source-lifecycle;
- nincs olyan reaction source, amelynek szabályos működése declarationkor
  kötelező zónaváltást igényel.

Future source policies külön typed extensiont kapnak,
nem a `same_zone_presence` szabály lazításával.

# 11. Declared target state

A public payload továbbra is a meglévő:

```text
CanonicalTargetSelectionPayload
- target_id
- card_instance_ids
```

formát használhatja.

Authoritative internal stack entry viszont declarationkor snapshotolja:

```text
DeclaredTargetSelectionState
- TargetId
- SelectedObjects[]
    - CardInstanceId
    - ZoneSequenceAtDeclaration
```

A target selection immutable declaration context.

Resolutionkor:

```text
revalidate
!=
automatic retarget
```

V1 nem választ új targetet automatikusan.

---

# 12. Underlying resolution nyitási contract

Reaction window csak explicit reactable timing checkpointnál nyitható.

Nyitási sorrend:

```text
1 validate underlying declaration/context
2 obtain explicit ReactionOpeningPlan from ReactionPolicyResolver
3 commit only those prerequisite transitions that rules szerint
  a reaction timing ELŐTT történnek
4 allocate ReactionSubjectId
5 allocate canonical ResolutionId
6 create bottom underlying ResolutionStackEntry
7 create ReactionWindowState
8 set PriorityPlayerId
9 commit reaction_window_opened technical event
10 return control to caller/client
```

Az underlying reactable ability FINAL effect mutationje
nem történhet meg a reaction window closure előtt.

Nem szabad:

```text
apply underlying ability effects
→ open reaction window afterward
```

ha a reaction szabály szerint a final resolution előtt történik.

A v1 nem foglal le előre egy jövőbeli gameplay `EngineEvent.EventId`-t.

# 13. Response policy registry – v1

V1 támogatott typed policyk:

```text
standard_alternating_response
single_responder_once
no_further_response
```

## 13.1 standard_alternating_response

V1 exact semantics:

- eligible responder set = mindkét match player;
- priority az egyik eligible playernél van;
- pass → másik player;
- két consecutive pass → closure;
- reaction accepted → pass count reset;
- ha egy reaction `NextResponsePolicyId` értéke ugyanez:
  - responder set mindkét player;
  - next priority = a reaction controllerének másik játékosa.

Ez csak olyan reaction optionnél adható ki,
amelynél rules/timing metadata mindkét játékos további válaszát engedi.

## 13.2 single_responder_once

Opening-window policy.

V1 exact semantics:

- exactly one eligible responder;
- priority = sole eligible responder;
- pass → closure;
- nincs fake second pass.

V1-ben egy accepted reaction **nem** használhat
`single_responder_once` értéket `NextResponsePolicyId`-ként,
mert az új sole responder meghatározása már restricted-responder extension lenne.

Single-responder reaction után v1 támogatott next policy:

```text
standard_alternating_response
no_further_response
```

## 13.3 no_further_response

Terminal post-declaration policy.

Accepted reaction után:

```text
window closes
→ full LIFO resolution cycle begins
```

Nem tárolható nyitott window `CurrentResponsePolicyId` értékeként
olyan állapotban, amely még external inputot vár.

## 13.4 Reserved future policy

Nem v1:

```text
restricted_responder
rule_defined
hidden_responder
```

Ezekhez explicit új responder-scope contract kell.

# 14. Reaction option contract

A `reaction_option_id` engine-issued és opaque client token.

Követelmény:

- window-bound;
- current-state-bound;
- viewer/player-bound legality;
- deterministic;
- unique a current windowban;
- nem kizárólag display/list indexből származik.

Candidate identity:

```text
reaction-option:<window-id>:<stable-candidate-key>
```

A kliens nem konstruálhat:

- arbitrary ability ID-t;
- arbitrary source cardot;
- arbitrary timingot;
- hidden optiont;
- arbitrary target contractot.

---

# 15. ReactionPolicyResolver és ReactionOption – v1 minimum

A Reaction Foundation **nem találhatja ki**:

- mely subject reactable;
- mely player jogosult;
- mely ability használható reactionként;
- mi a further-response policy.

Typed engine service:

```text
ReactionPolicyResolver
```

Minimum output openingkor:

```text
ReactionOpeningPlan
- InitiatorPlayerId
- EligibleResponderPlayerIds
- InitialResponsePolicyId
- ReactionProfileId
```

Minimum legal option:

```text
ReactionOption
- ReactionOptionId
- ReactionProfileId
- ControllerPlayerId
- SourceCardInstanceId
- SourceZoneSequenceAtDeclaration
- SourceAbilityId
- SourceRelevancePolicyId
- TargetContracts
- NextResponsePolicyId
```

V1 first-slice restrictions:

```text
SourceRelevancePolicyId = same_zone_presence

NextResponsePolicyId ∈ {
  standard_alternating_response,
  no_further_response
}
```

Nincs `NextEligibleResponderPlayerIds` mező v1-ben.

A responder set a támogatott policy explicit szemantikájából következik.

## 15.1 Metadata/binding authority

A current canonical ability model még nem ad teljes, production-ready
Reaction metadata contractot.

Ezért v1-ben tilos:

- ability/card ID alapján ad hoc hardcode-olt fallback;
- kártyaszöveg runtime string parsing;
- `TimingWindowId` tetszőleges implicit értelmezése;
- „ha reactionnek tűnik, engedjük” guessing.

A protocol implementation tesztelhető typed test fixture/profile bindinggel.

Production card/content csak akkor kap Reaction capabilityt,
ha külön validált explicit profile binding létezik.

A későbbi workbook/runtime-package schema migration külön data-contract task;
nem kell a protocol foundationbe erőltetni.

Ez követi:

```text
Engine Capability
!=
Content Coverage
```

# 16. Public legal action surface

ReactionWindow nélkül:

- current phase/legal-action behavior változatlan.

PendingTriggerWindow esetén:

- current narrow trigger gate változatlan.

ReactionWindow esetén:

## Priority player

Mindig enabled:

```text
pass_priority
```

Ha legal option létezik:

```text
react
```

Ha nincs legal option:

```text
react = disabled
disabled_reason = no_legal_reaction
```

## Nem-priority player

Enabled Reaction action nincs.

`includeDisabled=true` esetén:

```text
pass_priority → not_priority_player
react         → not_priority_player
```

## Base phase actionök

ReactionWindow alatt minden normal phase action disabled:

```text
disabled_reason = reaction_window_open
```

---

# 17. Action IDs – v1

Javasolt exact pattern:

```text
pass_priority:<reaction_window_id>:<state_version>:<player_id>

react:<reaction_window_id>:<state_version>:<player_id>
```

A client opaque ID-ként kezeli.

Action ID current legal-action/state contexthez kötött.

---

# 18. `pass_priority` payload

Payload:

```json
{}
```

Nincs extra player-supplied policy vagy window ID.

A window identity az `action_id` és current authoritative state alapján ellenőrzött.

---

# 19. `react` payload

V1:

```json
{
  "reaction_option_id": "reaction-option:...",
  "target_selections": []
}
```

Required:

```text
reaction_option_id
target_selections
```

`additional_properties = false`.

V1 NEM tartalmaz:

```text
payment_selections
nested_choice_payload
response_policy_id supplied by client
source_card_id supplied as authority
ability_id supplied as authority
```

A response policy engine-owned option metadata.

---

# 20. `react` payload_schema metadata

A priority player LegalAction `payload_schema` mezője
viewer-safe módon enumerálhat:

```text
reaction_options[]
- reaction_option_id
- source_card_instance_id
- source_card_id
- ability_id
- target_contracts[]
- next_response_policy_id
```

Csak az adott viewer számára legal és látható option kerülhet ide.

Opponent hidden candidate nem jelenhet meg.

---

# 21. SubmitAction validation order

Megmarad a current request validation order:

```text
1 request exists
2 schema
3 request_id
4 match_id
5 player_id
6 expected_state_version
7 action_id current legal actionban létezik
8 action_type egyezik
9 payload schema
10 action enabled
11 reaction-specific full validation
12 transition
```

Reaction-specific:

```text
13 ReactionWindow még current
14 request player = PriorityPlayerId
15 reaction_option_id current legal option
16 source relevance current
17 target declaration legal
18 response policy supported
19 v1 pending-family invariant megtartható
20 transition
```

---

# 22. Stale / invalid option behavior

Ha `expected_state_version` stale:

- current generic `STALE_STATE_VERSION`;
- semmilyen reaction-specific mutation nem történik.

Ha state version current, de option ID nem current legal:

Reason candidate:

```text
reaction_option_invalid
```

Diagnostic:

```text
REACTION_OPTION_INVALID
```

Retry:

```text
refresh_projection
```

Kötelező:

- PriorityPlayerId unchanged;
- pass count unchanged;
- window unchanged;
- stack unchanged;
- queued triggers unchanged;
- event history unchanged;
- state version unchanged.

---

# 23. Target declaration validation

A `react` requestnél:

- target schema current optionból;
- target count;
- candidate identity;
- object visibility;
- controller/owner restrictions;
- zone/relation restrictions

declarationkor validálandó.

Invalid declaration:

```text
reaction_target_invalid
REACTION_TARGET_INVALID
```

No mutation.

---

# 24. Priority lifecycle – both players

Nyitás:

```text
eligible = [A, B]
initiator = A
priority = B
pass_count = 0
policy = standard_alternating_response
```

### B pass

```text
pass_count = 1
priority = A
```

### A pass

```text
pass_count = 2
close
resolve
```

### B react

```text
push reaction entry
pass_count = 0
apply option next-response policy
```

Ha next:

```text
standard_alternating_response
```

akkor:

```text
eligible = both players
priority = A
window stays open
```

Ha:

```text
no_further_response
```

akkor:

```text
close
resolve
```

---

# 25. RC1 – single responder lifecycle

Példa:

```text
eligible = [B]
priority = B
policy = single_responder_once
```

### B pass

```text
close immediately
resolve
```

### B react

```text
push reaction entry
pass_count = 0
apply reaction option NextResponsePolicy
```

Ha:

```text
NextResponsePolicyId = standard_alternating_response
```

akkor v1-ben:

```text
eligible = [A, B]
priority = A   # reaction controllerének másik játékosa
window stays open
```

Ha:

```text
NextResponsePolicyId = no_further_response
```

akkor:

```text
close
resolve
```

`single_responder_once` nem v1-supported next policy.

Nincs fake A-pass.

Ez current RC1 default.

# 26. Accepted reaction transition

Accepted `react`:

```text
1 allocate ResolutionEntryId
2 freeze declaration source/target context
3 push entry to ResolutionStack
4 ConsecutivePassCount = 0
5 emit reaction_declared
6 apply NextResponsePolicy
7 either:
   a) set next PriorityPlayerId and return with window open
   b) close window and resolve cycle in same SubmitAction
```

Accepted reaction nem oldódhat fel a stackre helyezés előtt.

---

# 27. Window closure

Closure reason v1:

```text
passes_complete
no_further_response
```

Future reason reserved:

```text
rule_forced_close
```

Closurekor:

```text
1 emit reaction_window_closed
2 external ReactionWindow input state megszűnik
3 ResolutionStack LIFO unwind indul
```

A `ResolutionStack` internal resolution közben még nem üres.

Public action boundarynál nem maradhat:

```text
ReactionWindow == null
AND
ResolutionStack.Count > 0
```

kivéve controlled fatal/internal error state,
amely nem normál accepted response.

---

# 28. LIFO resolution

Példa:

```text
bottom U
R1
top R2
```

Order:

```text
R2
R1
U
```

Entrynként:

```text
1 resolution_entry_started
2 source relevance revalidation
3 condition revalidation
4 target/object revalidation
5 execute supported canonical ability semantics
6 commit zero or more gameplay EngineEvent
7 discover triggers immediately for each committed trigger-source event
8 queue discovered trigger batch(es)
9 resolution_entry_resolved OR resolution_entry_invalidated
10 pop entry
```

A canonical ability resolution egyetlen stack entry,
akkor is, ha több effect/mutationt hajt végre.

# 29. Final revalidation semantics

Resolutionkor kötelező:

- source still relevant;
- source object context still same where required;
- conditions still true;
- declared target object context still legal;
- mandatory/optional semantics;
- exact effect contract.

V1 target identity check használja:

```text
CardInstanceId
+
ZoneSequenceAtDeclaration
```

ahol az object-identity szabály ezt megköveteli.

---

# 30. Invalidated resolution

Ha a teljes supported effect invalid target/source/condition miatt
nem tud érdemben feloldódni:

```text
resolution_entry_invalidated
```

és nincs illegal fallback.

Ha az effectnek vannak önállóan végrehajtható részei:

- csak akkor hajthatók végre, ha current canonical executor
  explicit módon támogatja az adott partial semanticsot.

V1 nem talál ki:

- retargetet;
- default targetet;
- hidden fallbackot;
- guessed partial resolutiont.

Unsupported complex partial semantics:

```text
NOT_EXECUTABLE / controlled diagnostic
```

és production support/coverage policynek lehetőleg publish előtt blokkolnia kell.

---

# 31. Underlying resolution

Az underlying entry ugyanazon LIFO cycle legalsó eleme.

Reactions után:

```text
- revalidate underlying source/condition/targets
- execute the persisted canonical ability resolution
- commit zero or more gameplay EngineEvent
- correlate emitted ability events with ResolutionId where their current payload contract supports it
- discover/queue triggers at event creation/commit time
- pop underlying entry
```

Nincs előre lefoglalt „final underlying EngineEvent ID”.

Egy canonical ability resolution:

```text
0..N gameplay EngineEvent
```

kimenetet is adhat.

Ha reactions miatt az underlying teljesen invalid:

- final gameplay effect mutation nincs;
- `resolution_entry_invalidated` technical lifecycle event jelzi a kimenetet;
- a `ReactionSubjectId` lezárható, de nem használható új window újranyitására.

# 32. Technical Reaction lifecycle event types – v1

V1 minimum typed event vocabulary:

```text
reaction_window_opened
priority_passed
reaction_declared
reaction_window_closed
resolution_entry_started
resolution_entry_resolved
resolution_entry_invalidated
```

Ezek engine lifecycle eventek.

Nem automatikus AETERNA card-trigger source-ok.

V1 hard requirement:

```text
CanonicalTriggerResolver.MapEngineEventType(
    reaction_window_opened |
    priority_passed |
    reaction_declared |
    reaction_window_closed |
    resolution_entry_started |
    resolution_entry_resolved |
    resolution_entry_invalidated
)
= null
```

Későbbi explicit canonical mapping csak külön rules/data decision után adható.

A technical lifecycle eventek bekerülhetnek a full-fidelity internal event historyba,
de gameplay trigger discovery nem indul belőlük.

# 33. Reaction event correlation

Minimum payload correlation:

## reaction_window_opened

```text
reaction_window_id
reaction_subject_id
originating_event_id?
originating_event_sequence?
underlying_resolution_id
initiator_player_id
priority_player_id
response_policy_id
```

## priority_passed

```text
reaction_window_id
reaction_subject_id
passing_player_id
consecutive_pass_count
next_priority_player_id?
window_closed
```

## reaction_declared

```text
reaction_window_id
reaction_subject_id
resolution_id
parent_resolution_id
controller_player_id
reaction_option_id
source_card_instance_id
source_ability_id
next_response_policy_id
```

## reaction_window_closed

```text
reaction_window_id
reaction_subject_id
closure_reason
stack_depth
```

## resolution_entry_started

```text
reaction_window_id
reaction_subject_id
resolution_id
entry_kind_id
```

## resolution_entry_resolved

```text
reaction_window_id
reaction_subject_id
resolution_id
entry_kind_id
result = resolved
```

## resolution_entry_invalidated

```text
reaction_window_id
reaction_subject_id
resolution_id
entry_kind_id
safe_reason_code
```

Internal payload több detailt tarthat,
viewer projection csak public-safe mezőt ad.

# 34. Viewer-safe event projection

Internal full-fidelity event store megmarad.

Public `ActionResponse.Events` és `GetEvents(viewer)`:

- ugyanazt a viewer-safe projection elvet használja;
- hidden reaction candidate nem szivároghat;
- opponent nem kap undisclosed source identityt;
- internal `reaction_option_id` csak akkor projektálható,
  ha a declaration után public-safe;
- developer-only reason/detail nem kerül safe payloadba.

V1 first slice lehetőleg public/in-play reaction source-t használ,
hogy hidden-source reveal policy ne legyen új blocker.

---

# 35. PlayerSnapshot pending_decision_summary

ReactionWindow esetén:

```json
{
  "has_pending": true,
  "pending_type": "reaction_window",
  "pending_window_id": "reaction-window:...",
  "reaction_subject_id": "reaction-subject:...",
  "originating_event_id": null,
  "priority_player_id": "player-b",
  "viewer_is_priority_player": true,
  "viewer_is_eligible_responder": true,
  "response_policy_id": "standard_alternating_response",
  "consecutive_pass_count": 0,
  "stack_depth": 2
}
```

`originating_event_id` csak akkor nem null,
ha a subjectet már committed gameplay event nyitotta.

Nem kerül ide:

- opponent hidden options;
- full stack source identity;
- full internal target declarations;
- queued hidden triggers.

Reaction options a legal action payload schema felületén jelennek meg
csak a priority viewernek.

# 36. Pending decision family invariant

V1 externally blocking family:

```text
PendingTriggerWindow
ReactionWindow
```

Future:

```text
PendingChoice
CombatDecision
...
```

V1 public action boundary invariant:

```text
NOT (
  PendingTriggerWindow != null
  AND ReactionWindow != null
)
```

Egyszerre egy externally blocking decision family.

---

# 37. Compound non-reaction choice – v1 döntés

A v1 nem támogat reaction windowon belül később felbukkanó
új external compound choice-ot.

Reaction option csak akkor legal/listázható,
ha minden v1-hez szükséges client choice:

- declarationkor;
- a `react` payloadban

megadható.

Nem v1-supported például:

```text
react
→ utána válassz új paymentet
→ utána válassz új mode-ot
→ utána válassz új targetet
```

Ezek későbbi `PendingChoice` integration slice.

Ez scope restriction, nem végleges AETERNA rules tilalom.

---

# 38. Existing PendingTriggerWindow integration

A current `PendingTriggerWindow` narrow mandatory-trigger gate megmarad.

Reaction v1 nem refaktorálja tömegesen.

Kötelező:

- PendingTriggerWindow alatt phase action blokkolva marad;
- ReactionWindow nem nyílhat egyszerre vele external boundaryn;
- trigger discovery Reaction resolution közben queue-ba kerül, nem aktiválódik azonnal.

---

# 39. QueuedTriggerBatchState – RC2 minimum

MatchState internal queue:

```text
QueuedTriggerBatchState
- TriggerBatchId
- OriginatingEventId
- OriginatingEventSequence
- BatchOrderPolicyId
- Triggers[]
```

`Triggers[]` felhasználhatja a jelenlegi
`PendingTriggeredAbilityState` typed adatát.

## TriggerBatchId

Candidate:

```text
trigger-batch:<originating-event-id>
```

Egy committed gameplay eventhez egy same-timing discovery batch.

---

# 40. Trigger discovery Reaction cycle alatt

Minden committed gameplay EngineEvent után:

```text
discover immediately
```

de ha current Reaction/Resolution cycle aktív:

```text
DO NOT activate PendingTriggerWindow
DO queue batch
```

Ez a különbség:

```text
trigger occurrence/discovery
!=
trigger activation checkpoint
```

---

# 41. Post-resolution trigger checkpoint

Checkpoint akkor fut:

```text
ReactionWindow == null
AND
ResolutionStack empty
```

Algorithm:

```text
1 sort queued batches by OriginatingEventSequence ascending
2 take earliest batch
3 validate that the batch is supported by the current v1 trigger-activation coverage
4 materialize the earliest supported batch into PendingTriggerWindow
5 stop for external input
6 after that pending window fully clears, resume with the next FIFO batch
```

V1 first-slice acceptance legalább a `single-trigger batch` esetet támogatja.

A full same-time / multi-controller activation layer nem szükséges ehhez a proofhoz.

# 42. Different-timing FIFO

Ha:

```text
R2 event sequence = 101 → B1
R1 event sequence = 105 → B2
U  event sequence = 109 → B3
```

checkpoint order:

```text
B1
B2
B3
```

Nem:

- reverse stack order;
- ability ID sort;
- card ID sort;
- controller sort.

A primary key a committed originating `event_sequence`.

---

# 43. Same-timing batch – v1 coverage boundary

Egy committed gameplay event több simultaneous triggert hozhat létre.

Official general order már létezik, de a teljes digital activation UI
nem része a Reaction v1 first slice-nak.

V1 guaranteed production/proof coverage:

```text
one committed trigger-source event
→ zero or one discovered trigger
```

Ez elegendő az RC2:

```text
discover now
activate later
FIFO
```

bizonyítására.

Több same-time trigger esetén csak olyan path támogatható,
amelyet a current trigger contract már input nélkül teljesen determinisztikusan kezel.

Ha player ordering, controller-group handoff vagy új batch-choice contract kell:

```text
REACTION_TRIGGER_BATCH_ORDERING_UNSUPPORTED
```

Ez **nem** lehet post-mutation silent fallback.

Production contentnél publish/support validationnak előre kell blokkolnia.
Ha mégis elérhető accepted runtime pathban jelenik meg,
az invariant/engine-support hiba, és az atomic transition guardot meg kell őrizni.

A full simultaneous trigger activation külön későbbi slice.

# 44. Queue és PendingTriggerWindow coexistence

Allowed:

```text
PendingTriggerWindow != null
QueuedTriggerBatches.Count > 0
```

Jelentése:

- earliest batch már external resolutiont vár;
- későbbi FIFO batches megőrzendők.

A current pending trigger teljes feldolgozása után:

```text
if no ReactionWindow
and no current PendingTriggerWindow
→ resume queued trigger checkpoint
```

---

# 45. Complex nesting v1 limit

## 45.1 PendingTrigger → Reaction

Ha current `PendingTriggerWindow` több unresolved triggerét megtartva
egy kiválasztott triggered ability resolutionje ReactionWindowt akarna nyitni,
az compound integration.

V1 first slice:

```text
NOT_SUPPORTED
```

A foundation később bővíthető.

## 45.2 Új ReactionWindow stack unwind közben

A window closure után a current `ResolutionStack` teljes LIFO cycle-ja
internal módon fut ki.

V1 közben **nem nyithat új external ReactionWindow** egy resolution által
kibocsátott új event miatt.

Ha egy effect ilyen timingot igényel:

```text
REACTION_NESTED_WINDOW_DURING_RESOLUTION_UNSUPPORTED
```

Ez nem ugyanaz, mint a declaration-time further response:

```text
standard_alternating_response
```

A further response még a current window nyitott állapotában történik.

Első acceptance fixture egyik compound esetet sem használja.

# 46. Reaction subject closure contract

A `ReactionSubjectId` akkor tekinthető lezártnak, ha:

```text
ReactionWindow == null
AND ResolutionStack empty
AND related mandatory reaction/effect processing stable
AND RC2 trigger checkpoint eljutott:
    - stable queue-empty állapotig
    VAGY
    - explicit blocking PendingTriggerWindowig
AND zone transitions settled
```

V1 nem vezet be full event-sourcing aggregate-et.

Internal helper ajánlott:

```text
CanCloseReactionSubject(reactionSubjectId)
```

vagy equivalens invariant/coordinator check.

Closed subjectre későbbi reaction:

```text
reject
```

A committed `EngineEvent` saját history identityja ettől külön marad.

# 47. State-version semantics

Reaction nem kap külön concurrency modellt.

Megmarad:

```text
request_id
expected_state_version
```

Minden accepted external Reaction action a jelenlegi public action/state-version
modell szerint egyetlen final state transitiont ad a caller felé.

Belső:

- stack pop;
- effect resolution;
- trigger discovery;
- queue activation

nem hoz létre köztes client-submit state versionöket ugyanazon `SubmitAction`
közepén.

---

# 48. Atomic reject invariant

Bármely rejected `react` / `pass_priority`:

```text
PriorityPlayerId unchanged
ReactionWindow unchanged
ResolutionStack unchanged
QueuedTriggerBatches unchanged
PendingTriggerWindow unchanged
Card state unchanged
Events unchanged
StateVersion unchanged
```

Ez foundation guardrail.

---

# 49. Accepted pass semantics

Accepted `pass_priority`:

```text
1 validate current priority/window
2 increment pass count
3 emit priority_passed
4 if closure threshold not met:
   rotate priority
   finish request
5 else:
   close window
   unwind stack
   process RC2 checkpoint
   finish request
```

Closure threshold current responder cycle mérete:

```text
2 for standard_alternating_response
1 for single_responder_once
```

---

# 50. Accepted react semantics

Accepted `react`:

```text
1 validate current option + declaration
2 push reaction stack entry
3 reset pass count
4 emit reaction_declared
5 resolve option next-response policy
6 if external response opportunity remains:
   update eligible set + priority
   finish request
7 else:
   close window
   unwind stack
   process RC2 checkpoint
   finish request
```

---

# 51. Unsupported response policy

Unknown/unsupported policy:

Reason:

```text
reaction_response_policy_unsupported
```

Diagnostic:

```text
REACTION_RESPONSE_POLICY_UNSUPPORTED
```

No silent fallback to alternating priority.

---

# 52. Closed event / invalid window

Reaction request against old/closed window normally already elbukik:

- stale state;
- action not found.

Ha internal correlation validation külön detektálja:

```text
REACTION_SUBJECT_CLOSED
```

No mutation.

---

# 53. Determinism requirements

Nem használható gameplay determinismhez:

- wall clock;
- random GUID;
- unordered dictionary enumeration;
- client ordering;
- unstable reflection ordering.

Deterministic ordering minimum:

- player order = match player order;
- option order = explicit stable sort;
- stack = Sequence;
- queued batches = originating event sequence;
- same-time deterministic subset = official ordering + stable explicit tiebreak csak ott,
  ahol nincs player choice.

Player choice-t stable sorttal pótolni tilos.

---

# 54. Legal option ordering

Reaction options public listje determinisztikus.

Ajánlott stable key:

```text
source card created sequence
source card instance id
ability id
effect id
reaction option stable key
```

Ez presentation order.

Nem rules priority.

---

# 55. Diagnostics / disabled reason minimum

Stable disabled reasons:

```text
reaction_window_open
not_priority_player
no_legal_reaction
```

Reaction-specific rejection/diagnostic candidates:

```text
REACTION_OPTION_INVALID
REACTION_TARGET_INVALID
REACTION_RESPONSE_POLICY_UNSUPPORTED
REACTION_POLICY_BINDING_UNSUPPORTED
REACTION_PENDING_CONFLICT
REACTION_SUBJECT_CLOSED
REACTION_RESOLUTION_UNSUPPORTED
REACTION_TRIGGER_BATCH_ORDERING_UNSUPPORTED
REACTION_NESTED_WINDOW_DURING_RESOLUTION_UNSUPPORTED
```

A current generic guards továbbra is elsődlegesek, ahol alkalmazhatók:

```text
STALE_STATE_VERSION
ACTION_NOT_FOUND
ACTION_DISABLED
ACTION_PAYLOAD_INVALID
```

No silent fallback.

# 56. Hidden information

Fair AI és UI ugyanazt a viewer-safe surface-t használja.

Tilos:

- opponent reaction candidate count leak, ha nem public;
- hidden source card identity leak;
- hidden target candidate leak;
- developer diagnostic leak;
- full internal stack payload leak.

V1 public timing responder setet használ.

Hidden responder eligibility reserved extension.

---

# 57. PriorityPlayerId invariant

ReactionWindow nélkül:

- existing engine semantics.

ReactionWindow esetén:

```text
PriorityPlayerId ∈ EligibleResponderPlayerIds
```

`no_further_response` transition után nincs observable open window.

---

# 58. Stack invariants

Public action boundarynál, ha ReactionWindow open:

```text
ResolutionStack.Count >= 1
bottom.EntryKindId == underlying_resolution
bottom.ResolutionId == ReactionWindow.UnderlyingResolutionId

all entries:
ReactionWindowId == current window id
ReactionSubjectId == current reaction subject id
unique ResolutionId
strictly increasing Sequence by push history
```

Ability-resolution invariant:

```text
ResolutionStackEntry.ResolutionId
==
AbilityResolution runtime ResolutionId
```

V1 first slice source invariant:

```text
SourceRelevancePolicyId == same_zone_presence
```

# 59. Pending-family invariants

Normál external boundary:

```text
PendingTriggerWindow != null
XOR
ReactionWindow != null
XOR
neither
```

Queue nem externally blocking family,
ezért PendingTriggerWindow mellett maradhat.

---

# 60. Opening failure / pending conflict

Ha reactable timing checkpointhez érünk,
de más externally blocking family current:

```text
do not silently open nested ReactionWindow
```

V1:

```text
REACTION_PENDING_CONFLICT
```

A production supported contentnek ilyen kombinációt nem szabad igényelnie.

---

# 61. First vertical slice

Első proof tudatosan egyszerű:

```text
played_card-origin canonical ability
→ explicit test/profile binding says reactable
→ prerequisite card-play transition completes
→ ability final effects DO NOT resolve yet
→ underlying canonical ability resolution persists on stack
→ both players timing-eligible
→ non-initiator gets priority
→ pass OR one supported public/in-play reaction ability
→ optional standard further response
→ two-pass closure
→ full LIFO
→ target/source revalidation
→ underlying ability resolution
→ RC2 zero-or-one trigger batch/checkpoint
→ stable state
```

Resolution origins in this proof:

```text
underlying = played_card
reaction   = reaction
```

Kerülendő:

- triggered_ability underlying Reaction integration;
- combat;
- Burst;
- Jel;
- hand-spell source lifecycle;
- extra payment selection;
- simultaneous multi-trigger player-order choice;
- compound post-declaration choice;
- prevention/replacement;
- nested new ReactionWindow during stack unwind.

# 62. First slice content / fixture selection

A protocol proof olyan canonical ability fixture-t használjon, amely:

- current `CanonicalEffectExecutor` által támogatott ability graph;
- `played_card` resolution origin;
- public/in-play source a reactable checkpoint után;
- explicit typed Reaction profile binding;
- source relevance = `same_zone_presence`;
- nincs új payment choice;
- nincs hidden-opponent option leak;
- nincs combat dependency;
- nincs special partial-resolution requirement;
- RC2 tesztnél legfeljebb egy releváns trigger keletkezik egy eventből.

Reaction option fixture:

- public/in-play source ability;
- current executorral támogatott graph;
- `reaction` resolution origin;
- explicit profile binding;
- `NextResponsePolicyId` standard vagy no-further.

Ha megfelelő production card még nincs stabilan strukturálva,
teszt-only canonical fixture/profile használható a protocol proofhoz.

Teszt-only fixture/profile:

- nem official card/rule;
- nem rules authority;
- nem kerül production runtime package-be;
- nem hoz létre card-ID hardcoded fallbackot.

A production Reaction **content coverage** külön data/profile binding után aktiválható.

# 63. Positive acceptance tests – core protocol

Minimum:

1. supported reactable checkpoint opens window;
2. underlying effect final mutation nem történik meg korán;
3. underlying entry bottom stackon persistál;
4. both eligible → non-initiator first;
5. priority player sees `pass_priority`;
6. legal reaction option esetén sees `react`;
7. non-priority player has no enabled reaction action;
8. phase actions blocked;
9. first pass transfers priority;
10. second consecutive pass closes;
11. accepted reaction pushes entry;
12. accepted reaction resets pass count;
13. standard response policy hands priority correctly;
14. no-further-response closes immediately;
15. two reaction entries resolve LIFO;
16. underlying resolves after reactions;
17. source revalidation happens;
18. target revalidation happens;
19. invalid resolution does not retarget;
20. correct technical events emitted.

---

# 64. Positive acceptance tests – RC1

21. single responder gets priority;
22. single responder pass closes immediately;
23. no fake second pass;
24. single responder reaction can transition by typed next policy;
25. no-further-response from single responder resolves immediately.

---

# 65. Positive acceptance tests – RC2

26. reaction resolution gameplay event discovers trigger immediately;
27. trigger does not activate while stack still resolving;
28. trigger enters queued batch;
29. later reaction event creates later batch;
30. underlying event creates later batch;
31. post-resolution checkpoint runs only after stack empty;
32. different-timing batches activate FIFO by event_sequence;
33. existing PendingTriggerWindow can receive supported earliest batch;
34. later batches survive while pending trigger awaits external input;
35. after pending trigger clears, queue processing resumes.

---

# 66. Positive acceptance tests – projection

36. reaction pending summary visible;
37. viewer priority boolean correct;
38. stack depth correct;
39. reaction options only priority viewer legal surface-en;
40. opponent hidden option not leaked;
41. ActionResponse reaction events viewer-safe;
42. GetEvents projection viewer-safe.

---

# 67. Negative acceptance tests

Minimum:

1. `react` outside window;
2. `pass_priority` outside window;
3. wrong player pass;
4. wrong player react;
5. invalid action ID;
6. stale state version;
7. invalid reaction option ID;
8. option from previous window;
9. illegal target count;
10. illegal target identity;
11. source object context changed before submit;
12. target object context changed before submit;
13. phase advance during ReactionWindow;
14. PendingTriggerWindow bypass attempt;
15. unsupported response policy;
16. unsupported post-declaration choice reaction;
17. unsupported reaction payment selection;
18. closed reaction subject reaction attempt;
19. same-time trigger batch requiring unsupported player order;
20. pending-family conflict.

Minden rejected public action:

```text
NO MUTATION
NO EVENT
NO STATE VERSION CHANGE
```

---

# 68. Regression acceptance

A Reaction implementation nem törheti:

- current production phase flow;
- Wellspring;
- Beáramlás;
- Magnitúdó/Aura preflight;
- play_card;
- Domain;
- canonical ability/effect current tests;
- damage/vitals;
- continuous effects;
- modifier/keyword/duration;
- draw/reference;
- existing PendingTriggerWindow;
- viewer-safe event projection;
- Python/reference regression;
- Godot production bridge.

Current pre-Reaction baseline:

```text
Debug   222/222 PASS
Release 222/222 PASS
determinism 100/100
Godot smoke PASS
```

Az új suite száma természetesen nőhet.

---

# 69. Build / test acceptance

Implementation után minimum:

```text
dotnet build Debug
dotnet test Debug
dotnet build Release
dotnet test Release

headless/reference/oracle regression
determinism 100/100

Godot C# build
positive production smoke
negative production smoke
```

Majd:

```text
adversarial read-only audit
```

Commit csak PASS után.

---

# 70. Implementation sequence

Ajánlott Codex implementation sorrend:

```text
A. typed state + invariants
B. legal actions + payload schemas
C. opening coordinator
D. pass lifecycle
E. reaction declaration + option resolver
F. LIFO resolution
G. final revalidation
H. technical event projection
I. RC2 queue/checkpoint
J. first vertical slice fixture
K. tests
L. Godot smoke
M. adversarial audit
```

Nem szabad Combatot közben „mellékesen” beépíteni.

---

# 71. Expected production code touchpoints

Várhatóan érintett:

```text
Aeterna.Engine/State/MatchState.cs
Aeterna.Engine/Contracts/EngineContracts.cs
Aeterna.Engine/EngineSession.cs
Aeterna.Engine/Runtime/CanonicalEffectExecutor.cs
Aeterna.Engine/Runtime/CanonicalTriggerResolver.cs
Aeterna.Engine/Runtime/... ReactionResolutionCoordinator
Aeterna.Engine/Runtime/... ReactionPolicyResolver
Aeterna.Engine.Tests/...
Godot production bridge smoke/tests
```

Expected executor change:

```text
CanonicalResolutionOrigin.Reaction
```

Pontos file split implementation decision.

Nem kötelező egyetlen óriási coordinator class.

# 72. Reserved extension points

V1 után explicit bővíthető:

```text
strict_event_window
delayed_effect
immediate special timing
restricted hidden responder
compound pending choice
reaction payment choice
optional trigger UI
simultaneous player ordering UI
prevention/replacement
combat reaction checkpoints
Burst
Jel
TriggerActivationPolicy
TriggerBatchOrderPolicy
```

Ezek reserved extension pointok,
nem current open OQ-k automatikusan.

---

# 73. Superseded blueprint proposal states

A blueprint v0.2 következő státuszai a current OQ v2.2 miatt supersededek:

```text
D1–D5 PROPOSED_ACCEPT
→ CURRENT_DEFAULT

RC1 RULES_CLARIFICATION_REQUIRED
→ CURRENT_DEFAULT: single responder pass closes

RC2 RULES_TO_CONTRACT_CLARIFICATION_REQUIRED
→ CURRENT_DEFAULT:
   queue until post-resolution checkpoint,
   different-timing FIFO
```

A blueprint történeti evidence marad.

---

# 74. Contract decision summary

A v1 RC1 freeze-jelölt:

```text
Public API:
react
pass_priority

Option identity:
reaction_option_id

Timing/eligibility authority:
typed ReactionPolicyResolver
no guessing

Further-response:
typed response_policy_id

State:
MatchState.ReactionWindow
MatchState.ResolutionStack
MatchState.QueuedTriggerBatches

Subject correlation:
ReactionSubjectId
not reserved future EngineEvent ID

Underlying:
persisted bottom canonical ability resolution

Resolution identity:
stack ResolutionId == canonical ability ResolutionId

First-slice origins:
played_card
reaction

Source relevance:
same_zone_presence

Closure:
RC1 = 1 pass
both-player = 2 consecutive passes

Resolution:
full LIFO after closure
final revalidation
no auto-retarget

Triggers:
discover at committed gameplay event
activate at post-resolution checkpoint
different-timing FIFO
first proof = zero/one trigger per event

Projection:
existing pending_decision_summary

Concurrency:
existing expected_state_version
no new model

Compound choice:
not in v1

Nested new window during unwind:
not in v1

Combat:
not in v1
```

# 75. Review gates before implementation

A contract emberileg elfogadott. Az implementation során az alábbi nyolc freeze-gate
kötelezően megtartandó:

1. underlying canonical ability resolution bottom stack entry;
2. `ReactionSubjectId` különválasztása a committed `EngineEvent.EventId` fogalomtól;
3. exact `ReactionWindowState` minimum fields;
4. exact canonical ability stack-entry minimum fields;
5. response policy registry;
6. RC1 lifecycle;
7. RC2 queue/checkpoint lifecycle + first-slice single-trigger boundary;
8. v1 compound/nested-choice és nested-window exclusion.

További technikai audit eredmény:

```text
ReactionPolicyResolver explicit authority required
silent/card-ID fallback forbidden
```

Ezek elfogadott freeze-gate-ek.
Új általános Reaction rules research kör nem szükséges az első implementation slice előtt.

# 76. Dokumentációs átvezetés elfogadás után

Az elfogadás handoff során célzottan frissítendő:

- jelen contract státusza `ACCEPTED_FOR_IMPLEMENTATION`;
- `ENGINE_CHECKPOINT.md` next step → implementation;
- `DECISION_MAP.md` Reaction contract status;
- projektterv current Reaction status;
- `CONTRACT_SPECIFICATION.md` csak a közvetlenül érintett interface-ekkel.

Nem kell újraírni teljes dokumentumokat.

---

# 77. Változásnapló

## 1.0-rc1 – 2026-08-16

- pre-implementation semantic audit completed;
- `UnderlyingEventId` conflation replaced by deterministic `ReactionSubjectId` + optional committed-event correlation;
- stack entry aligned to whole canonical ability resolution and existing `ResolutionId` identity;
- first-slice origins narrowed to `played_card` + `reaction`;
- source relevance narrowed to typed `same_zone_presence` policy;
- `ReactionPolicyResolver` made explicit; guessing/card-ID fallback forbidden;
- response-policy model simplified; no v1 `NextEligibleResponderPlayerIds`;
- technical resolution lifecycle event names generalized to entry-level events;
- technical Reaction events explicitly non-trigger-source in v1;
- RC2 first-slice coverage narrowed to zero/one trigger per event;
- nested new ReactionWindow during stack unwind explicitly excluded;
- review gate list expanded to eight items.

## 1.0-draft – 2026-08-16

- official Reaction foundation és OQ v2.2 egyesítve;
- D1–D5 current defaultként rögzítve;
- RC1 current defaultként rögzítve;
- RC2 queue + post-resolution checkpoint + FIFO rögzítve;
- underlying effect persisted bottom stack entryként rögzítve;
- response policy registry konkretizálva;
- single/both responder lifecycle konkretizálva;
- public legal action és payload contract konkretizálva;
- stale/invalid option atomic behavior rögzítve;
- final revalidation object-identity detaillel pontosítva;
- queued trigger batch minimum state rögzítve;
- compound non-reaction choice v1-ből kizárva;
- technical event vocabulary és correlation rögzítve;
- viewer-safe pending summary rögzítve;
- acceptance matrix rögzítve;
- Combat/prevention/full choice explicit non-goal.

## Elfogadási státusz – 2026-08-16

- human acceptance: `ACCEPTED`;
- implementation authority: `ACTIVE_FOR_V1_FIRST_SLICE`;
- implementation: `NOT_STARTED / NEXT`;
- pre-implementation audit: `PASS_WITH_RC1_CORRECTIONS`;
- P0/P1/P2 unresolved blocker: `0 / 0 / 0`.
