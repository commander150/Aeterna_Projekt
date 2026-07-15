# AETERNA Game Engine – Contract Specification Migration Map

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív contract-dokumentációs konszolidációs térkép  
**Technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum a hosszú `CONTRACT_SPECIFICATION.md` és a jelenlegi Python engine tényleges contractjai közötti eltéréseket térképezi fel.

Feladata:

- megőrizni a hosszú specifikáció értékes jövőbeli ötleteit;
- megjelölni, mi vált már aktív runtime contracttá;
- megjelölni, mi maradt terv vagy kérdés;
- megakadályozni, hogy egy régi mezőjavaslatot aktív sémának tekintsünk;
- előkészíteni a későbbi, fokozatos tartalmi konszolidációt.

Nem módosít runtime kódot és nem hoz létre új sémát.

---

## 1. Elsődleges contract-források

Aktuális implementációs státusz:

- `CURRENT_CONTRACT_STATUS.md`

Aktuális engine-state és schema-határ:

- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

Aktuális architektúra:

- `ARCHITECTURE.md`

Közeli döntési kapuk:

- `CURRENT_OPEN_QUESTIONS.md`

Hosszú tervezési referencia:

- `CONTRACT_SPECIFICATION.md`

Eltérés esetén a current dokumentumok az elsődlegesek.

---

## 2. Státuszjelölések

| Státusz | Jelentés |
|---|---|
| `implemented` | Működő minimal engine-contract vagy projection. |
| `implemented_differently` | A cél megvalósult, de nem a hosszú dokumentum javasolt formájában. |
| `partially_implemented` | Alapcontract működik, a gazdagabb modell még hiányzik. |
| `planned` | Jövőbeli terv, nincs aktív runtime implementation. |
| `superseded` | Régi sample vagy technológiai irány felváltva. |
| `needs_spec_update` | A hosszú specifikációba később beépítendő aktív contract. |
| `open_question` | Szabályi vagy technikai döntés szükséges. |

---

## 3. Általános contract alapok

### Hosszú specifikáció állapota

**Státusz:** `partially_implemented`

Továbbra is érvényes:

- contract-first alapelv;
- frontend nem találgat szabályt;
- AI nem találgat szabályt;
- player-visible contract nem teljes MatchState dump;
- schema version szükséges;
- diagnostics strukturált;
- runtime package, state, projection és event külön réteg.

Frissítendő:

- a példák még főleg sample-sémákat használnak;
- a common field lista túl általános és több aktív contractra nem pontos;
- nem minden contract tartalmaz runtime package ID-t, snapshot ID-t vagy diagnostics listát;
- a tényleges minimal contractok kisebbek és célzottabbak.

Konszolidációs elv:

- közös kötelező mezőket csak akkor deklaráljunk, ha ténylegesen minden érintett schema használja;
- „ajánlott mező” ne váljon automatikusan runtime követelménnyé.

---

## 4. Snapshot fejezetek

### 4.1 Snapshot célja és MatchState-elhatárolás

**Státusz:** `implemented`

A jelenlegi player-visible snapshot:

- a MatchState-ből származtatott;
- viewer-specifikus;
- hidden-information védett;
- nem tartalmaz teljes registryt;
- nem tartalmaz teljes topology/occupancy state-et.

Aktív schema:

- `engine-player-visible-snapshot-v2`

### 4.2 Snapshot-típusok

**Státusz:** `implemented_differently`

A hosszú terv több külön snapshot-típust sorol:

- opponent-visible;
- spectator;
- ai-fair;
- ai-debug;
- replay.

Aktuális döntés:

- a canonical `player_visible_snapshot` viewer alapján működik;
- a fair AI ugyanezt használja;
- külön debug snapshot létezik;
- külön opponent snapshot jelenleg nem szükséges;
- spectator, replay és külön AI snapshot későbbi terv.

### 4.3 Snapshot mezőjelöltek

**Státusz:** `partially_implemented`

Aktív minimal snapshot már tartalmaz:

- schema és contract identity;
- match és state identity;
- viewer;
- active és priority player;
- player projectionök;
- public Domain board;
- visibility policy;
- metadata.

Még nincs teljesen implementálva:

- match finished;
- winner;
- victory reason;
- pending decision;
- legal action summary;
- recent event ablak;
- scenario context;
- Wellspring projection;
- Pecsét aktuális állapot.

### 4.4 Visibility

**Státusz:** `partially_implemented`

Bizonyított:

- saját kéz látható;
- ellenfél kéz redacted és count-only;
- deck count-only;
- discard public;
- Domain board public;
- Wellspring card record visibility értéke `owner_only`.

Még nyitott:

- player-visible Wellspring összesítés pontos policyje;
- face-down Jel;
- Pecsétlap láthatósága;
- spectator és replay visibility;
- player-facing activity state projection.

A hosszú dokumentum által felsorolt általános visibility mode értékek nem mind aktív canonical runtime enumok.

### 4.5 Domain board

**Státusz:** `needs_spec_update`

Aktív, de a hosszú specifikációban még nincs megfelelő pontossággal rögzítve:

- 6 current játékosonként;
- horizon és zenith slot;
- static seal position;
- occupancy;
- canonical ObjectReference;
- public board model;
- board player-set validáció.

Aktív schema:

- `minimal-player-visible-domain-board-v0`

### 4.6 Pecsét és Aeternal

**Státusz:** `planned` / `open_question`

Továbbra is érvényes tiltás:

- nincs Pecsét HP;
- nincs Aeternal HP;
- nincs Aeternal sebzés vagy gyógyítás.

Még nincs runtime:

- Pecsét állapot;
- Pecsét feltörés/visszaállítás;
- Aeternal védtelenség;
- victory projection.

---

## 5. Legal action fejezetek

### 5.1 Legal action alapelv

**Státusz:** `implemented`

A frontend és AI a rules engine legal action outputját használja.

### 5.2 Aktív minimal actiontér

**Státusz:** `implemented_differently`

A hosszú dokumentum MVP-jelöltjei között több későbbi action szerepel, de a tényleges minimal engine aktív actionjei:

- `draw_card`
- `end_turn`

A `draw_card` a hosszú MVP-jelölt listából hiányzik, ezért a lista nem tekinthető aktív enum-specifikációnak.

### 5.3 Structural Entity placement

**Státusz:** `needs_spec_update`

Aktív izolált contract:

- `minimal-entity-domain-placement-option-v0`
- `minimal-entity-domain-placement-options-v0`

Ez:

- pontosan 12 saját targetet ad;
- foglalt targetet disabled structurális optionként megőrzi;
- nem teljes play legality;
- nincs legal actionbe integrálva.

### 5.4 Enabled és disabled actionök

**Státusz:** `partially_implemented`

A debug sample contract bizonyította az enabled/disabled megjelenítést.

A production minimal legal action policy még nem végleges normál UI, tutorial és debug módra.

### 5.5 Targeting, payment és reaction

**Státusz:** `planned`

Még nincs teljes runtime:

- target választás;
- manual payment;
- Aura source selection;
- reaction window;
- stack/queue;
- Burst és Jel reakciókezelés.

A strukturális placement nem helyettesíti a target vagy play legality contractot.

---

## 6. Action request fejezetek

### 6.1 Minimal action request

**Státusz:** `implemented`

Aktív minimal request támogat:

- match identity;
- player identity;
- action type;
- expected state version;
- request validáció.

### 6.2 Snapshot/state frissesség

**Státusz:** `implemented_differently`

A hosszú dokumentum ezt még nyitott kérdésként tárgyalja.

Aktív döntés:

- expected state version guard létezik;
- stale vagy hibás state version rejectet ad;
- rejected request nem mutál state-et.

A későbbi snapshot ID/token/idempotencia továbbra is nyitott transport- és klienskérdés.

### 6.3 Request ID és action token

**Státusz:** `planned`

Még nincs teljes:

- idempotencia;
- duplicate request policy;
- signed/opaque token;
- network/PvP request security.

---

## 7. Action response fejezetek

### 7.1 Minimal action response

**Státusz:** `partially_implemented`

Működik:

- accepted response;
- rejected response;
- structured reason/diagnostics;
- state version és transition summary;
- eseménykapcsolat;
- response history/session használat;
- trajectory integráció.

### 7.2 Gazdag response-mezők

**Státusz:** `planned`

A hosszú dokumentum által felsorolt mezők közül nem mind aktív:

- normalized action;
- teljes validation objektum;
- pending decision;
- response-ba ágyazott teljes új snapshot;
- payment/target/choice result;
- prevented/replaced/partially resolved státuszok.

Ezek későbbi gameplay és reaction layer részei.

### 7.3 Reject policy

**Státusz:** `implemented`

Aktív alapelv:

- reject esetén nincs state mutation;
- structured reason és diagnostics készül;
- rejected step trajectoryban megőrizhető;
- expected state version hiba kontrollált.

---

## 8. Event fejezetek

### 8.1 Generic envelope

**Státusz:** `implemented`

Aktív schema:

- `minimal-engine-event-v0`

### 8.2 Aktív typed eventek

**Státusz:** `implemented`

- `zone_move`
- `turn_transition`

A draw typed `zone_move` eseményt ad.

Az end turn typed `turn_transition` eseményt ad.

### 8.3 Felváltott általános event

**Státusz:** `superseded`

Nincs aktív általános `action_resolved` event, ha a transition pontosabb typed eventtel leírható.

### 8.4 Tervezett eventek

**Státusz:** `planned`

- Inflow/Wellspring transition;
- activity change;
- payment;
- card played;
- Entity entered Domain;
- attack/block/damage;
- seal break/restore;
- victory/defeat.

### 8.5 Player-visible event projection

**Státusz:** `partially_implemented`

Bizonyított:

- debug teljesebb adatot kaphat;
- player projection nem kap teljes internal payloadot.

A teljes visible event log, event window és replay projection még nincs kész.

---

## 9. Diagnostics fejezetek

### 9.1 Strukturált diagnostics

**Státusz:** `implemented`

A current engine és contract validatorok strukturált:

- code;
- message/részletek;
- valid/errors;
- parent és nested error

mintákat használnak.

### 9.2 Egységes globális diagnostics schema

**Státusz:** `partially_implemented`

Sok contract saját error recordot használ.

Még nincs minden engine-, package-, UI- és ability-rétegre egyetlen végleges globális diagnostics schema.

### 9.3 Player-visible diagnostics

**Státusz:** `open_question`

Nem szivároghat:

- hidden card identity;
- opponent hand/deck adat;
- internal invariant detail;
- debug-only payload.

A végleges player-facing reason/localization policy későbbi feladat.

---

## 10. A hosszú specifikációból hiányzó aktív contractok

A következő működő contractokat a későbbi konszolidáció során külön fejezetként kell beépíteni.

### 10.1 Card instance

- `minimal-card-instance-record-v1`
- owner/controller;
- zone/index;
- visibility;
- sequence;
- activity state.

### 10.2 ObjectReference

- `minimal-object-reference-v0`
- biztonságos rövid reference;
- nem teljes registry dump.

### 10.3 ZoneMove

- draw során aktív;
- későbbi általános zónatransition alap.

### 10.4 Domain topology és occupancy

- position;
- player topology;
- position occupancy;
- player occupancy;
- registry cross-validation.

### 10.5 Domain board projection

- public board;
- current 1–6;
- horizon/zenith;
- static seal reference.

### 10.6 Activity state

- `active`;
- `exhausted`;
- zone/activity invariant;
- nem summoning sickness.

### 10.7 Wellspring

- `minimal-player-wellspring-state-v0`;
- `minimal-wellspring-resource-summary-v0`;
- Magnitúdó = lapok száma;
- available Aura = active count;
- jelenleg isolated.

### 10.8 AI episode trajectory

- `minimal-ai-vs-ai-episode-v1`;
- accepted/rejected step;
- player-visible observation;
- deterministic JSON;
- `replay_ready: false`.

---

## 11. Sample contractok helye

A Godot sample snapshot, legal action és event contractok:

- `debug_fixture`;
- korai parser/UI bizonyítékok;
- nem a current Python engine authoritative schema-jai.

Nem törlendők automatikusan.

Későbbi feladat:

- aktualizált Python player snapshot fixture export;
- Godot parser compatibility test;
- sample contractok explicit historical/compatibility státusza.

---

## 12. Konszolidációs sorrend

A hosszú `CONTRACT_SPECIFICATION.md` teljes átírása helyett fokozatos frissítés szükséges.

### 12.1 Első szakasz

- dokumentumstátusz és first-source hivatkozások;
- sample vs active schema elhatárolás;
- current schema index;
- felváltott technológiai állítások jelölése.

### 12.2 Második szakasz

- card instance;
- MatchState;
- Domain topology/occupancy;
- activity state;
- Wellspring

fejezetek hozzáadása.

### 12.3 Harmadik szakasz

- snapshot szakasz frissítése v2-re;
- board projection;
- visibility policy;
- debug/player elhatárolás.

### 12.4 Negyedik szakasz

- minimal legal action/request/response;
- state version guard;
- typed eventek;
- rejected action;
- trajectory.

### 12.5 Ötödik szakasz

- jövőbeli mezőjelöltek külön appendixbe;
- payment, reaction, combat, Pecsét és victory tervek;
- nyitott kérdések kapcsolása a `CURRENT_OPEN_QUESTIONS.md` és `OPEN_QUESTIONS.md` fájlokhoz.

---

## 13. Amit a konszolidáció nem tehet

Nem szabad:

- a current runtime sémát dokumentációból megváltoztatni;
- javasolt mezőt kötelezővé nyilvánítani teszt és implementáció nélkül;
- régi kérdést elveszíteni;
- sample fixture-t production sémának nevezni;
- teljes MatchState-et player snapshotként leírni;
- GDScriptet második authoritative rules engine-ként visszahozni;
- Wellspring isolated contractot már integráltnak állítani;
- structural placementet teljes play legalityként leírni;
- replay foundationt kész replayként nevezni.

---

## 14. Rövid összefoglaló

**Hosszú contract-specifikáció értéke:** megőrzendő  
**Aktuális runtime-státusz forrása:** `CURRENT_CONTRACT_STATUS.md`  
**Fő eltérés:** sok korábbi javaslat már vagy megvalósult más formában, vagy továbbra is csak terv  
**Hiányzó aktív fejezetek:** card instance, Domain, activity, Wellspring, trajectory  
**Felváltott sample-sémák:** Godot debug fixture-ként maradnak  
**Konszolidáció módja:** fokozatos, nem tömeges átírás
