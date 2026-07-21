# AETERNA – tanulóprojektekből kinyert legfontosabb fejlesztési irányok

## 1. Rövid döntés

A következő fejlesztési szakaszban nem az a cél, hogy a tanulóprojektekből kódot vegyünk át, hanem hogy a legjobb mintákat AETERNA-saját, tiszta contract-first formára fordítsuk.

A legjobb stratégia:

1. előbb stabil engine-alapok;
2. utána objektumazonosság és zónamozgás;
3. utána player-visible snapshot és AI/environment;
4. utána minimális board/target/cost contract;
5. csak ezután Godot UI és komplex ability rendszer.

A legfontosabb alapelv:

A Godot UI, a bot, a fake UI és a későbbi multiplayer kliens ugyanazt az engine action contractot használja. Egyik sem lehet szabályforrás.

## 2. A leghasznosabb tanulóprojektek szerep szerint

### Komplex TCG rules engine

Legjobb referencia:

* Mage / XMage

Legfontosabb tanulság:

* Card_ID, card_instance_id, permanent_id, stack_object_id külön kezelése;
* zone transition nem sima listaáthelyezés;
* target, cost, stack, trigger, replacement, prevention külön alrendszer;
* event log és state mutation csak resolveren keresztül.

AETERNA-ra fordítva:

* előbb object identity + zone move contract;
* utána play_card;
* utána target/cost;
* sokkal később stack / replacement / prevention.

### Board + taktikai engine + modifier rendszer

Legjobb referencia:

* Duelyst

Legfontosabb tanulság:

* GameSession / Step / Action / Modifier / Replay modell;
* board helper;
* position, adjacency, radius, obstruction;
* action validation külön réteg;
* eventből trigger és modifier működés.

AETERNA-ra fordítva:

* minimal board position contract;
* később Áramlat / Horizont / Zenit modellezés;
* action_space bővítése target/precondition mezőkkel.

### AI-vs-AI / environment API

Legjobb referencia:

* RLCard

Legfontosabb tanulság:

* reset / step / run_episode;
* legal_actions;
* observation;
* player-visible state;
* hidden information;
* agent API;
* trajectory;
* deterministic seed.

AETERNA-ra fordítva:

* MinimalEngineEnvironment továbbtisztítása;
* episode trajectory contract;
* RandomLegalActionPolicy;
* RuleBasedSmokePolicy;
* player_visible_snapshot bővítés.

### Turn / phase / flow / client-server boundary

Legjobb referencia:

* boardgame.io

Legfontosabb tanulság:

* G + ctx szétválasztás;
* turn / phase / stage;
* move → reducer → log;
* expected stateID;
* playerView;
* hidden information filtering;
* bot simulation;
* deterministic random;
* scenario tests.

AETERNA-ra fordítva:

* engine_context summary;
* expected_state_version guard;
* minimal phase contract;
* player-visible snapshot szigorítás;
* scenario runner setup override.

### Godot UI / CardView / kéz / pakli / dropzone

Legjobb referenciák:

* simple-card-pile-ui;
* deckbuilder-framework;
* godot-card-game-framework-gd4;
* Godot4-Fake3D-Card-Game-UI-Demo;
* hackstone;
* Pali.

Legfontosabb tanulság:

* CardView legyen view, ne state;
* ZoneView legyen projection, ne authority;
* drag/drop csak action_requestet építsen;
* action_space mondja meg, mi engedélyezett;
* engine response alapján animáljon a UI;
* fake-3D / hover / hand fan későbbi vizuális polish.

AETERNA-ra fordítva:

* CardView v0.1;
* ZoneView / HandView / PileView;
* DebugEventLogView;
* EngineSnapshotTableView;
* később TargetingArrowView.

## 3. A legjobb fejlesztési ötletek érték szerint

### Legjobb hosszú távú alap

Object identity + zone move contract.

Ez kell ahhoz, hogy a mostani Card_ID problémát végleg megoldjuk.

Tartalom:

* Card_ID;
* card_instance_id;
* későbbi permanent_id;
* későbbi stack_object_id;
* zone;
* zone_index;
* owner;
* controller;
* visibility;
* zone_sequence vagy zone_change_counter;
* zone_move event.

Miért ez a legfontosabb?

Mert nélküle a draw_card, play_card, target, discard, graveyard, token, ability és UI mapping mind rossz alapra épülne.

### Leggyorsabb biztonságos kódlépés

expected_state_version guard a MinimalEngineSession.step körül.

Tartalom:

* action request opcionálisan tartalmazza: expected_state_version;
* ha nem egyezik az aktuális state_versionnel, rejected response;
* reason például: stale_state_version;
* state nem módosul;
* event log nem nő;
* tesztek JSON-kompatibilis response-ra.

Miért gyors?

Mert nem igényel új gameplay szabályt, nem érinti a card modelt, és közvetlenül illeszkedik a már meglévő state_version rendszerhez.

### Leggyorsabb AI-vs-AI fejlesztési nyereség

Episode trajectory contract bővítése.

Tartalom:

* state_version_before;
* state_version_after;
* selected_action;
* response;
* events;
* diagnostics;
* stop_reason;
* final_summary;
* action_counts;
* rejected_count;
* accepted_count.

Miért hasznos?

Mert az AI-vs-AI futás már létezik, de így később mérhető, összehasonlítható és regressziótesztelhető lesz.

### Legjobb Godot-előkészítő lépés

Engine snapshot → Godot projection terv.

Tartalom:

* engine debug snapshot;
* player_visible_snapshot;
* CardViewModel;
* ZoneViewModel;
* action_space;
* selected action;
* action_response;
* DebugEventLogView.

Miért nem rögtön UI?

Mert a Godot UI-t nem szabad szabályforrássá tenni. Előbb tiszta adatáramlás kell.

### Legjobb rules-engine előkészítő lépés

Target / cost / precondition schema terv.

Tartalom:

* target_requirements;
* source_instance_id;
* target candidates;
* cost_preflight;
* payment_status;
* disabled_reason;
* validation_reason.

Miért később?

Mert előbb object identity és zone contract kell. Targetelni csak stabil objektumokra lehet.

## 4. Codex közbeni hasznos javaslatok, amelyeket nem szabad elfelejteni

### Engine / contract

* Add expected state version guard to minimal engine step
* Add minimal engine context summary to debug export
* Add minimal engine object reference and zone move contract plan
* Add minimal card instance reference fields to engine smoke state
* Add minimal board position contract and adjacency helpers
* Add minimal engine environment episode trajectory contract
* Add deterministic seed helper
* Add RandomLegalActionPolicy
* Add RuleBasedSmokePolicy
* Add scenario runner setup override
* Add player-visible snapshot visibility policy

### Godot / UI

* AETERNA Godot visual table projection plan
* AETERNA CardView v0.1 plan
* CardView / ZoneView / HandView / PileView clean-room design
* Engine snapshot → Godot projection mapping
* action_space → UI enabled/disabled mapping
* click/drag/drop → action_request flow
* TargetingArrowView based on engine legal targets
* DebugEventLogView
* EngineSnapshotTableView

### Rules / ability

* Card_ID / Card_Instance_ID final plan
* ObjectReference = id + zone/version
* ZoneMove / ZoneOperation contract
* target/cost preflight
* ability support diagnostics with trigger_window
* future trigger / replacement / prevention architecture
* event pipeline / event bus plan
* stack_object_id future model

### Testing / diagnostics

* scenario-style regression tests
* event log as transition proof
* deterministic smoke reports
* action response snapshot tests
* zone invariant tests before every new action
* fake UI and fake bot use same API
* debug snapshot and player snapshot must remain separate

## 5. Ajánlott fejlesztési sorrend

### 1. Expected state version guard

Ez a leggyorsabb, legkisebb és legbiztonságosabb lépés.

Miért most?

* state_version már van;
* response contract már van;
* rejected response már van;
* boardgame.io stateID tanulsága közvetlenül ide kapcsolódik;
* nem kell hozzá új játékszabály.

### 2. Engine context summary

Tartalom:

* match_id;
* turn;
* phase;
* active_player_id;
* priority_player_id;
* state_version;
* event_count;
* response_count;
* metadata.

Miért hasznos?

Ez elkezdi szétválasztani a boardgame.io-szerű ctx réteget a game state-től.

### 3. Card instance / object reference terv

Ez legyen előbb terv, nem rögtön nagy refactor.

Tartalom:

* Card_ID;
* card_instance_id;
* zone;
* owner;
* controller;
* zone_sequence;
* ObjectReference.

Miért terv először?

Mert ez sok későbbi rendszert érint: draw, play_card, discard, target, Godot UI, AI observation.

### 4. Minimal zone move contract

Tartalom:

* from_zone;
* to_zone;
* object_id;
* player_id;
* source_action_id;
* event_sequence;
* state_version;
* visibility.

Ez a draw_card új, véglegesebb alapja lehet.

### 5. Episode trajectory contract bővítése

Tartalom:

* steps;
* actions;
* responses;
* events;
* final observation;
* action counts;
* rejected count;
* diagnostics.

Ez az AI-vs-AI runnernek ad értéket.

### 6. Player-visible snapshot szigorítása

Tartalom:

* debug_snapshot nem azonos player_snapshottal;
* saját kéz látszik;
* ellenfél kéz count-only;
* deck count látszik;
* hidden card IDs nem mennek ki;
* metadata jelzi: hidden_information_model részleges.

### 7. Minimal board position contract

Csak ezután.

Tartalom:

* board dimensions;
* is_on_board;
* adjacency;
* occupied/free summary;
* későbbi Áramlat / Horizont / Zenit előkészítése.

### 8. Godot projection terv

Tartalom:

* CardViewModel;
* ZoneViewModel;
* ActionSpaceViewModel;
* DebugEventLogView;
* Godot nem szabályforrás.

## 6. Mit ne csináljunk most

Most még ne csináljuk:

* teljes play_card rendszer;
* attack rendszer;
* payment rendszer;
* stack rendszer;
* trigger/replacement/prevention rendszer;
* nagy Godot UI;
* multiplayer szerver;
* ML training;
* MCTS bot;
* teljes phase DSL;
* ability executor;
* CardView vizuális polish;
* fake-3D shader implementáció;
* deck builder.

Ezek hasznosak lesznek, de csak később.

## 7. Legjobb következő konkrét Codex-feladat

A legjobb következő kis kódfeladat:

`Add expected state version guard to minimal engine step`

Indok:

* kicsi;
* gyors;
* contract-first;
* boardgame.io tanulság közvetlen alkalmazása;
* nem igényel új gameplay szabályt;
* erősíti a későbbi client/server/Godot boundaryt;
* védi a state_version alapú action flow-t;
* jó regressziótesztelési pont.

Második legjobb:

`Add minimal engine context summary to debug export`

Harmadik legjobb:

`Create Card_ID / Card_Instance_ID / ZoneMove architecture plan`

## 8. Javasolt stratégiai döntés

A következő 3–5 Codex-feladat legyen engine-stabilizáló, ne látványos UI.

Javasolt mini-roadmap:

1. expected_state_version guard;
2. engine_context summary;
3. object identity + zone move terv;
4. minimal card instance reference mezők;
5. episode trajectory bővítés;
6. player-visible snapshot szigorítás;
7. minimal board position contract;
8. Godot projection terv.

Ez a sorrend gyors, biztonságos, és nem épít rossz alapra.

## 9. Végső összegzés

A tanulóprojektek alapján az AETERNA helyes útja nem az, hogy egy meglévő projektet átalakítunk, hanem hogy a legjobb mintákat saját, kicsi, stabil contractokra bontjuk.

A három legerősebb tanulság:

1. Mage / XMage: object identity és zone transition nélkül nincs komoly TCG engine.
2. RLCard: AI-vs-AI-hoz stabil environment / observation / legal action / trajectory kell.
3. boardgame.io: turn/phase/context/player-view/client-server boundary tisztán szervezhető, de nem kell túl korán nagy frameworköt építeni.

A következő legjobb lépés: `expected_state_version` guard, majd engine context, majd object identity / zone move terv.
