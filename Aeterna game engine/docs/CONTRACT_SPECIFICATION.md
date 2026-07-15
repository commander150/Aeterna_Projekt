# AETERNA Game Engine – Contract Specification

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív, technológiafüggetlen contract-specifikáció; a tényleges implementációs státuszt a current dokumentumokkal együtt kell olvasni  
**Aktuális Python technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum az AETERNA Game Engine contract-first rétegének aktív szerkezeti specifikációja.

Nem:

- teljes rules engine specifikáció;
- runtime package schema;
- ability module rendszerleírás;
- MatchState mezőszintű kóddokumentáció;
- valamely runtime-nyelv előzetes kiválasztása;
- minden jövőbeli mező kötelező sémává nyilvánítása.

A korábbi, 61 fejezetes tervezési változat a Git-történetben megmarad. Ez az aktív változat a migration map, a működő Python engine és a current státuszdokumentumok alapján konszolidált specifikáció.

Kapcsolódó aktív dokumentumok:

- `CURRENT_CONTRACT_STATUS.md` – tényleges implementációs státusz;
- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md` – történeti eltérés- és migrációs térkép;
- `CURRENT_OPEN_QUESTIONS.md` – nyitott döntési kapuk;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md` – runtime-összehasonlítás;
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md` – nyelvfüggetlen comparison scenario;
- `ARCHITECTURE.md` – rendszerhatárok;
- `CURRENT_RUNTIME_PACKAGE_STATUS.md` – statikus package-adatút;
- `ABILITY_MODULE_SYSTEM.md` – későbbi ability-contractok;
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md` – aktuális engine-checkpoint.

Eltérés esetén:

1. működő kód és tesztek;
2. `CURRENT_CONTRACT_STATUS.md`;
3. `CURRENT_OPEN_QUESTIONS.md` és az aktív döntési dokumentumok;
4. ez a specifikáció;
5. történeti tervek és sample dokumentumok

sorrend az irányadó.

---

## 1. Contract-first alapelv

Az AETERNA központi fejlesztési elve:

> **Előbb explicit contract, utána implementáció.**

A fő rétegek nem egymás belső objektumaira vagy UI-node-jaira, hanem ellenőrizhető határfelületekre épülnek.

Kötelező következmények:

- pontosan egy authoritative MatchState létezik;
- a frontend és az AI nem találgat legalitást;
- a frontend action requestet küld, nem módosít state-et;
- az authoritative engine validál és hajt végre transitiont;
- rejected request nem okozhat részleges mutationt;
- player-facing output nem teljes MatchState dump;
- hidden information nem szivároghat snapshotba, eventbe, legal actionbe vagy diagnosticsba;
- debug és player-visible contract fizikailag és szemantikailag elkülönül;
- azonos input és state esetén determinisztikus output szükséges;
- a contractoknak Python, C#, GDScript vagy más runtime-modell mellett is ugyanazt a játékjelentést kell hordozniuk.

A contract-rendszer egyik fő célja, hogy a működő Python referencia és bármely későbbi product runtime ugyanazon fixture-ön összehasonlítható legyen.

---

## 2. Contract-státuszok

| Státusz | Jelentés |
|---|---|
| `active_runtime` | A minimal authoritative engine ténylegesen használja. |
| `active_projection` | Player-facing vagy debug projekcióban ténylegesen használatos. |
| `active_isolated` | Megvalósított és tesztelt helpercontract, de még nincs MatchState/runtime integrációban. |
| `foundation_only` | Alapcontract létezik, de a teljes gameplay-lánc még hiányzik. |
| `planned` | Dokumentált jövőbeli contract; nincs aktív implementáció. |
| `superseded` | Korábbi séma vagy modell, amelyet újabb aktív változat felváltott. |
| `debug_fixture` | Parser-, loader- vagy UI-tesztadat; nem authoritative gameplay-contract. |

Szabály:

- javasolt mező nem válik kötelezővé implementáció és teszt nélkül;
- `active_isolated` nem nevezhető integrált runtime-funkciónak;
- `foundation_only` nem nevezhető teljes gameplay-támogatásnak;
- `debug_fixture` nem nevezhető production sémának.

---

## 3. Contract-rétegek és felelősségük

### 3.1 Runtime package

Statikus programadat:

- card definition;
- deck definition;
- LOOKUPS és canonical értékek;
- aliasok és normalizációs adatok;
- ability registry foundation;
- engine-support és build diagnostics.

Nem:

- MatchState;
- save game;
- player-visible snapshot;
- legal action eredmény;
- authoritative mérkőzésállapot.

A runtime package nyelvfüggetlen adatforrás. Python tooling bármely product runtime mellett megmaradhat.

### 3.2 MatchState

Az authoritative belső igaz állapot.

Tartalmazhat:

- player state-eket;
- card instance registryt;
- zónatagságot és sorrendet;
- owner/controller adatot;
- activity state-et;
- Domain topológiát és occupancy state-et;
- turn, phase és priority alapot;
- state versiont;
- event logot;
- később pending decisiont, effect- és duration-state-et.

A MatchState nem player-facing contract.

### 3.3 Projection

A MatchState-ből származtatott, nézőpontfüggő output.

Fő típusok:

- player-visible snapshot;
- public Domain board;
- debug snapshot;
- később visible event ablak, spectator és replay projection.

### 3.4 Legal action

Az authoritative engine által számított, adott játékos számára elérhető döntések.

A legal action:

- nem frontend-találgatás;
- nem state mutation;
- tartalmazhat source-, target-, choice- és payment-contextet;
- később enabled/disabled vagy debug reason adatot adhat;
- csak player-visible információból épülhet fair AI számára.

### 3.5 Action request

A játékos, frontend vagy AI szándékának explicit kérése.

Kötelező elv:

- a request nem bizonyít legalitást;
- az engine újra validál;
- state-version guard védi a frissességet;
- a kliens nem küldhet rejtett vagy authoritative state-módosítást.

### 3.6 Action response

A validálás és transition strukturált eredménye.

Tartalmazhat:

- accepted/rejected státuszt;
- reason és diagnostics adatot;
- state version before/after értéket;
- transition summaryt;
- typed eventeket;
- később pending decisiont, payment-, target- és choice-resultot.

### 3.7 Event

A történeti transition-réteg.

> **A snapshot az állapot. Az event a megtörtént változás.**

Az eventek célja:

- UI animáció;
- magyarázat;
- audit és debug;
- AI trajectory;
- későbbi replay;
- state transition ellenőrzés.

### 3.8 Diagnostics

Strukturált hiba-, warning-, audit- és validációs réteg.

A diagnostics:

- nem egyszerű logszöveg;
- nem szivárogtathat hidden informationt;
- külön kezeli a severityt és a blocking státuszt;
- használható build-, loader-, state-, request-, visibility- és support-problémákhoz.

---

## 4. Aktív és izolált schema-index

### 4.1 Belső state és reference

| Contract | Schema / modell | Státusz | Rövid szerep |
|---|---|---|---|
| Card instance record | `minimal-card-instance-record-v1` | `active_runtime` | Authoritative meccsbeli kártyapéldány. |
| ObjectReference | `minimal-object-reference-v0` | `active_projection` | Rövid, kontrollált objektumhivatkozás; nem registry dump. |
| ZoneMove | minimal ZoneMove contract | `active_runtime` | Strukturált zónamozgás; jelenleg draw használja. |
| MatchState | belső authoritative modell | `active_runtime` | A mérkőzés igaz állapota. |
| Domain position | `minimal-domain-position-v0` | `active_runtime` | Horizon, zenith vagy seal pozíció. |
| Player Domain topology | `minimal-player-domain-topology-v0` | `active_runtime` | Játékosonként 6 Áramlat és stabil pozíciók. |
| Domain position occupancy | `minimal-domain-position-occupancy-v0` | `active_runtime` | Egy board slot foglaltsága. |
| Player Domain occupancy | `minimal-player-domain-occupancy-v0` | `active_runtime` | Játékos 12 horizon/zenith occupancy slotja. |

### 4.2 Projection

| Contract | Schema / modell | Státusz | Rövid szerep |
|---|---|---|---|
| Player-visible snapshot | `engine-player-visible-snapshot-v2` | `active_projection` | Viewer-specifikus, hidden-information-védett állapotkép. |
| Player-visible Domain board | `minimal-player-visible-domain-board-v0` | `active_projection` | Két játékos public Domain boardja. |
| Public Domain board model | `minimal-public-domain-board-v0` | `active_projection` | Horizon/zenith slotok és static seal reference. |
| Debug snapshot | aktuális debug modell | `active_projection` | Fejlesztői többletadat; nem player-facing. |

### 4.3 Action és event

| Contract | Schema / modell | Státusz | Rövid szerep |
|---|---|---|---|
| Minimal legal action space | aktuális minimal action modell | `foundation_only` | Aktív actionök: `draw_card`, `end_turn`. |
| Minimal action request | aktuális request contract | `active_runtime` | Match, player, action type és expected state version. |
| Action response | aktuális response contract | `active_runtime` / részben foundation | Accepted/rejected eredmény és transition summary. |
| Engine event envelope | `minimal-engine-event-v0` | `active_runtime` | Typed eventek közös borítéka. |
| Zone move event | `zone_move` | `active_runtime` | Draw során deck → hand transition. |
| Turn transition event | `turn_transition` | `active_runtime` | `end_turn` transition. |

### 4.4 AI és trajectory

| Contract | Schema / modell | Státusz | Rövid szerep |
|---|---|---|---|
| AI-vs-AI episode | `minimal-ai-vs-ai-episode-v1` | `active_runtime` | Determinisztikus accepted/rejected trajectory. |
| Replay readiness | `replay_ready: false` | `foundation_only` | Replay-alap, de még nem teljes replay. |

### 4.5 Izolált következő alapok

| Contract | Schema / modell | Státusz | Rövid szerep |
|---|---|---|---|
| Entity Domain placement option | `minimal-entity-domain-placement-option-v0` | `active_isolated` | Egy strukturális placement target. |
| Entity Domain placement options | `minimal-entity-domain-placement-options-v0` | `active_isolated` | Pontosan 12 saját horizon/zenith opció. |
| Placement model | `structural-entity-domain-placement-v0` | `active_isolated` | Nem teljes play legality. |
| Player Wellspring state | `minimal-player-wellspring-state-v0` | `active_isolated` | Ősforrás instance-lista és count. |
| Wellspring resource summary | `minimal-wellspring-resource-summary-v0` | `active_isolated` | Magnitúdó és elérhető Aura összesítés. |
| Wellspring model | `base-wellspring-count-and-activity-v0` | `active_isolated` | Count- és activity-alapú erőforrásmodell. |

---

## 5. Card instance és zóna-invariánsok

A `minimal-card-instance-record-v1` fő jelentése:

- stabil `card_instance_id`;
- statikus `card_id` hivatkozás;
- `owner_player_id` és `controller_player_id` külön kezelése;
- pontos `zone` és `zone_index`;
- visibility;
- created és zone sequence;
- activity state;
- metadata.

Activity értékek:

- `None`;
- `active`;
- `exhausted`.

Jelenlegi zóna/activity alap:

- deck, hand, discard → `None`;
- Domain és Wellspring → `active` vagy `exhausted`.

Kötelező invariánsok:

- egy card instance pontosan egy authoritative zónában legyen;
- PlayerState listák és registry zónaadata egyezzen;
- Domain occupancy és registry position egyezzen;
- stabil sorrend és egyedi instance ID szükséges;
- rejected transition nem hagyhat félkész listás vagy registry állapotot.

Az activity state nem summoning sickness és nem helyettesíti a későbbi entry-state vagy attack-eligibility szabályt.

---

## 6. Domain topology, occupancy és projection

Játékosonként:

- 6 Áramlat;
- 6 horizon slot;
- 6 zenith slot;
- 6 statikus seal position;
- 18 stabil position reference;
- 12 foglalható horizon/zenith slot.

A seal position nem általános occupancy slot.

Canonical kapcsolat:

- occupancy `position_id`;
- `occupant_card_instance_id`;
- card instance registry;
- kétirányú invariáns.

A player-visible Domain board:

- mindkét játékos public boardját tartalmazza;
- empty vagy occupied slotot mutat;
- occupied slotban ObjectReference-et ad;
- nem ad teljes card instance rekordot;
- a Pecsét aktuális állapota még nincs implementálva.

A structural Entity placement:

- 12 saját horizon/zenith opciót generál;
- foglalt targetet disabled structurális optionként megőriz;
- nem ellenőrzi a timingot, priorityt, Magnitúdót, paymentet, kártyaszöveget vagy entry-state-et;
- ezért nem nevezhető `play_card` legalitásnak.

---

## 7. Snapshot és visibility

### 7.1 Player-visible snapshot

Aktív schema:

- `engine-player-visible-snapshot-v2`.

Aktív visibility-policy:

- saját kéz: owner-visible;
- ellenfél kéz: redacted és count-only;
- deck: count-only;
- discard: public;
- Domain board: public;
- teljes registry, paklisorrend és belső topology/occupancy nem kerül player-facing outputba.

A fair AI ugyanazt a canonical player-visible observationt használja, mint a játékos.

### 7.2 Debug snapshot

A debug snapshot:

- tartalmazhat többletinformációt;
- nem használható fair AI observationként;
- nem kerülhet normál player-facing csatornába;
- külön visibility- és tesztpolicy alá tartozik.

### 7.3 Még tervezett projectionök

- Wellspring player-visible summary;
- Pecsét állapot;
- match finished, winner és victory reason;
- pending decision;
- recent visible event ablak;
- spectator projection;
- replay projection.

A külön opponent snapshot jelenleg nem kötelező: a canonical player snapshot viewer ID alapján készül.

---

## 8. Legal action

### 8.1 Aktív minimal actiontér

Jelenlegi actionök:

- `draw_card`;
- `end_turn`.

Ez foundation, nem teljes AETERNA actiontér.

### 8.2 Kötelező legal-action elvek

- csak az authoritative engine generálhat legal actiont;
- fair AI és normál UI ugyanazon legalitási eredményre épül;
- action ID vagy payload nem jogosít state mutationre engine-validáció nélkül;
- hidden source vagy target identity nem szivároghat;
- stabil, determinisztikus rendezés szükséges;
- debug disabled reason nem válhat player-facing hidden-information csatornává.

### 8.3 Későbbi actioncsaládok

- turn flow;
- Inflow;
- play card;
- targeting és choice;
- payment;
- ability;
- combat;
- reaction;
- system/debug.

Ezek nem aktív canonical enumok mindaddig, amíg implementáció és teszt nem rögzíti őket.

### 8.4 Pending decision

Később külön pending-decision contract szükséges többek között:

- célpontválasztás;
- payment source választás;
- mód- vagy mennyiségválasztás;
- optional trigger;
- replacement/prevention;
- reaction pass.

A pending decision nem lehet frontend-lokális szabályállapot.

---

## 9. Action request és response

### 9.1 Minimal request

A jelenlegi request többek között:

- match identityt;
- player identityt;
- action type-ot;
- expected state versiont

hordoz.

A stale vagy hibás state version kontrollált rejectet ad.

### 9.2 Reject policy

Reject esetén:

- nincs state mutation;
- nincs event-log növekedés, ha transition nem történt;
- strukturált reason és diagnostics készül;
- active/priority player és zónaállapot változatlan;
- rejected trajectory step megőrizhető.

### 9.3 Későbbi request-mezők

Csak szükség és proof után:

- client request ID;
- snapshot ID;
- idempotencia és duplicate policy;
- action token;
- source/targets/choices/payment payload;
- PvP security metadata.

### 9.4 Későbbi response-rétegek

- normalized action;
- részletes validation result;
- target-, choice- és payment result;
- pending decision;
- prevented/replaced/partially resolved státusz;
- opcionális új snapshot vagy snapshot reference.

Ezek nem tekinthetők jelenlegi kötelező mezőknek.

---

## 10. Event-contractok

### 10.1 Generic envelope

Aktív schema:

- `minimal-engine-event-v0`.

Aktív typed eventek:

- `zone_move`;
- `turn_transition`.

A draw `zone_move`, az end turn `turn_transition` eventet ad.

Nincs szükség általános `action_resolved` eventre, ha a transition pontosabb typed eventtel kifejezhető.

### 10.2 Eventkövetelmények

- stabil event sequence;
- match és state-version kapcsolat;
- determinisztikus sorrend;
- source/cause és transition-adat;
- belső és player-visible payload elhatárolása;
- event nem lehet önmagában authoritative state;
- player-visible event nem szivárogtathat rejtett adatot.

### 10.3 Tervezett eventek

- Inflow/Wellspring transition;
- activity state change;
- Aura payment;
- card played;
- Entity entered Domain;
- attack, block és entity damage;
- Pecsét feltörés/visszaállítás;
- victory és defeat;
- ability trigger és resolution.

Az új typed event csak stabil state transition után vezethető be.

---

## 11. Wellspring, Beáramlás és erőforrás-contractok

### 11.1 Izolált Wellspring-state

Aktív izolált schema:

- `minimal-player-wellspring-state-v0`.

Fő jelentése:

- player ID;
- zone `wellspring`;
- visibility `owner_only` belső recordszinten;
- stabil instance ID-lista;
- card count;
- metadata.

Még nincs production PlayerState/MatchState integrációban.

### 11.2 Resource summary

Aktív izolált schema:

- `minimal-wellspring-resource-summary-v0`;
- modell: `base-wellspring-count-and-activity-v0`.

Canonical alapszámítás:

- `magnitude == wellspring_card_count`;
- `available_aura == active_source_count`;
- `active_source_count + exhausted_source_count == total_source_count`.

Ne legyen külön authoritative `magnitude`, `spent_aura` vagy `remaining_aura` számláló, ha az érték a zónából és activity state-ből származtatható.

### 11.3 Beáramlás Core-döntés

A normál Beáramlás:

- a kör második fázisának opcionális művelete;
- legfeljebb 1 kézlapot helyez az Ősforrásba;
- a lap képpel lefelé kerül;
- a bekerülő lap `active` activity state-et kap;
- azonnal növeli a Magnitúdót;
- azonnal növeli az elérhető Aurát;
- ugyanabban a körben használható Aura fizetésére;
- fizetéskor `exhausted` állapotba kerül;
- külön kártyahatásból történő Ősforrás-bővítés nem fogyasztja el a normál Beáramlás lehetőségét, hacsak a hatás másként nem rendelkezik.

Ez a szabályi döntés dokumentált, de a transition contract még `planned`.

### 11.4 Következő erőforrás-contractok

1. Wellspring PlayerState- és MatchState-integráció;
2. player-visible Wellspring summary;
3. Inflow precondition;
4. Inflow transition és event;
5. per-turn Inflow usage state;
6. Magnitúdó-preflight;
7. typed Aura és LOOKUPS mapping;
8. Aura source selection;
9. payment és atomikus activity mutation;
10. `play_card` precondition és transition.

### 11.5 Nem implementált erőforrásrétegek

- typed Aura;
- payment;
- temporary Aura;
- Rezonancia;
- Aura-égés;
- Magnitúdó modifier vagy override;
- automatic/manual payment policy.

---

## 12. AI és trajectory

Aktív schema:

- `minimal-ai-vs-ai-episode-v1`.

Támogatott:

- deterministic bot policy;
- accepted és rejected step;
- player-visible observation;
- action request/response;
- typed eventek;
- trajectory validation;
- determinisztikus JSON output.

Kötelező AI-elv:

- fair AI nem kaphat több információt, mint a játékos;
- AI nem mutálhat state-et közvetlenül;
- AI csak legal actionből választhat;
- debug AI külön, explicit módban kaphat többletinformációt.

Replay readiness jelenleg `false`. A trajectory replay-alapot ad, de nem teljes replay runner.

---

## 13. Diagnostics és validáció

### 13.1 Általános validátorminta

A jelenlegi contract helperek elvei:

- JSON-kompatibilis dict/list output;
- schema version és contract type;
- normál hibás inputra non-throwing validator;
- strukturált `{valid, errors}` eredmény;
- kontrollált builder exception invalid authoritative state/query esetén;
- deep-copy és inputváltozatlanság;
- determinisztikus sorrend és azonosítók;
- tiltott field és state leak ellenőrzése;
- canonical builder/validator újrahasználata.

### 13.2 Diagnostics-elhatárolás

A diagnostics tartalmazhat:

- code;
- severity;
- blocking;
- message vagy details;
- field/object/source reference;
- nested vagy parent error;
- metadata.

Nem kötelező egyetlen globális diagnostics schema minden rétegre addig, amíg a külön contractok következetes, strukturált hibát adnak.

### 13.3 Player-facing diagnostics

Nem szivároghat:

- hidden card identity;
- ellenfél kéz- vagy deckadat;
- teljes internal invariant detail;
- debug-only payload;
- nem látható target vagy source létezése.

A fejlesztői reason code és a későbbi lokalizált játékosüzenet külön réteg lehet.

---

## 14. Ability- és support-contract határ

A runtime package jelenleg:

- tartalmaz `ability_registry.json` fájlt;
- tartalmaz `engine_support.json` fájlt;
- két ability modult `declared_only` állapotban kezel;
- a kártyák supportját `not_evaluated` értéken tartja;
- `runtime_executes_abilities: false`.

Ezért:

- ability registry nem executor;
- support report nem teljes szabályhűségi garancia;
- 814 runtime-kártya jelenléte nem jelent 814 működő képességet;
- ability definition és ability execution külön contract-réteg;
- card-local fallback csak diagnosztizált, átmeneti és külön jóváhagyott megoldás lehet.

Részletes ability-architektúra:

- `ABILITY_MODULE_SYSTEM.md`.

Ability executor csak a runtime-nyelvi döntés, Wellspring, Beáramlás, payment, `play_card`, timing/priority, target/choice és typed event alapok után indulhat.

---

## 15. Sample és debug fixture contractok

A Godot sample fájlok:

- `sample_snapshot.json`;
- `sample_legal_actions.json`;
- `sample_events.json`

státusza `debug_fixture`.

Értékük:

- loader és parser bizonyíték;
- debug nézetek;
- card reference resolution;
- contract consistency smoke;
- korai compatibility fixture.

Nem bizonyítják:

- valódi MatchState-generálást;
- production legal action számítást;
- action request feldolgozást;
- valós gameplay eventeket;
- ability executiont;
- current Python schema-egyezést minden mezőben.

Nem törlendők automatikusan, de explicit fixture/compatibility státuszban maradnak.

---

## 16. Superseded modellek

### 16.1 Player-visible snapshot v1

- schema: `engine-player-visible-snapshot-v1`;
- státusz: `superseded`;
- felváltotta a v2 public Domain boarddal.

### 16.2 Card instance record v0

- schema: `minimal-card-instance-record-v0`;
- státusz: `superseded`;
- felváltotta a v1 `activity_state` mezővel.

### 16.3 Felváltott általános eventmodell

Általános `action_resolved` event nem aktív, ha a transition pontosabb typed eventtel leírható.

---

## 17. Tiltott vagy kerülendő modellek

### 17.1 Hidden-information hibák

Tilos:

- teljes registry player snapshotban;
- deck instance ID-k player-facing outputban;
- opponent hidden card ID vagy instance ID;
- debug diagnostics normál UI-ban;
- legal actionbe kódolt rejtett információ.

### 17.2 Aeternal és Pecsét HP-modell

Kerülendő vagy tiltott:

- `player_damage`;
- `aeternal_damage`;
- `heal_player`;
- `heal_aeternal`;
- `aeternal_hp`;
- `player_hp`;
- `ward_hp`;
- `seal_hp`;
- `ward_damage`;
- `seal_damage`.

Támogatandó fogalmi irány:

- Pecsét feltörés;
- Pecsét visszaállítás;
- feltörés megelőzése;
- Aeternal védtelenség;
- közvetlen támadásból eredő győzelem;
- játékos veresége.

### 17.3 Dokumentációból létrehozott álcontract

Tilos:

- javasolt mezőt implementáció nélkül kötelezővé tenni;
- sample fixture-t production sémának nevezni;
- isolated Wellspringet integráltnak állítani;
- structural placementet teljes play legalityként leírni;
- trajectory foundationt kész replayként nevezni;
- UI-t authoritative rules service-ként használni.

---

## 18. Jövőbeli contract-kapuk

A következő contractok csak a megfelelő gameplay-réteg előtt készüljenek.

### 18.1 Wellspring és Inflow

- zónatagság;
- visibility summary;
- precondition;
- transition;
- per-turn usage;
- typed event.

### 18.2 Magnitúdó és Aura

- preflight result;
- typed cost;
- canonical Aura mapping;
- source selection;
- atomic payment;
- activity change.

### 18.3 `play_card`

- source card reference;
- timing és priority;
- Magnitúdó és payment;
- placement/target/choice;
- atomikus zone transition;
- card played és entry event;
- structured rejection.

### 18.4 Timing, phase és reaction

- phase controller;
- priority;
- pass;
- pending decision;
- Burst és Jel reaction;
- replacement és prevention;
- queue/stack/chain döntés.

### 18.5 Combat

- attacker és target;
- blocker;
- damage csak Entitásra;
- Pecsét interaction;
- Aeternal védtelenség és victory;
- typed combat eventek.

### 18.6 Ability execution

- trigger;
- condition;
- cost;
- target;
- choice;
- effect;
- duration és limit;
- replacement/prevention;
- support és fallback.

### 18.7 Replay és spectator

- action history;
- snapshot checkpoint;
- event visibility;
- deterministic reconstruction;
- spectator policy.

Ezek a témák nem aktív schema mezőlisták. A részletes nyitott döntések helye a `CURRENT_OPEN_QUESTIONS.md` és a történeti `OPEN_QUESTIONS.md` / `OPEN_QUESTIONS_DECISIONS.md` dokumentumpár.

---

## 19. Contract-validációs minimum minden új rétegnél

Minden új contracthoz szükséges:

1. explicit cél és authority-határ;
2. schema vagy contract identity;
3. builder és validator;
4. valid és invalid fixture;
5. determinisztikus serialization;
6. deep-copy/inputváltozatlanság teszt;
7. hidden-information audit;
8. state-version és mutation-policy;
9. accepted és rejected út;
10. typed event vagy indokolt eventhiány;
11. player-facing és debug payload elhatárolása;
12. current státuszdokumentum frissítése;
13. nyelvfüggetlen jelentés, ha comparison scope-ba kerül.

Jelentős transition-contract csak akkor tekinthető integráltnak, ha a state-invariánsok, request/response, event és projection együtt bizonyítottak.

---

## 20. Jelenlegi prioritási lánc

### 20.1 Runtime-döntési kapu

A következő Codex-prioritás:

1. `fourth turn` read-only audit;
2. canonical comparison fixture-artifactok;
3. Python sidecar proof;
4. Godot .NET/C# proof;
5. portable Windows és stabilitási összevetés;
6. szükség esetén GDScript vagy más proof;
7. emberi runtime-döntés.

### 20.2 Döntés utáni gameplay-contract lánc

1. Wellspring MatchState-integráció;
2. player-visible Wellspring summary;
3. Inflow precondition és transition;
4. Magnitúdó-preflight;
5. Aura source selection és payment;
6. activity mutation;
7. Entity play precondition;
8. `play_card` request/response;
9. Entity entry event;
10. phase/priority/reaction alap;
11. csak ezután ability executor.

---

## 21. Rövid current státusz

**Authoritative referencia:** Python minimal engine.  
**Aktív belső state:** card instance v1, MatchState, Domain topology és occupancy.  
**Aktív projection:** snapshot v2 és public Domain board.  
**Aktív runtime action:** `draw_card`, `end_turn`.  
**Aktív typed event:** `zone_move`, `turn_transition`.  
**Aktív AI contract:** episode v1.  
**Izolált következő alap:** Wellspring state, resource summary és structural Entity placement.  
**Dokumentált Core-döntés:** a normál Beáramlással bekerülő lap Aktív és ugyanabban a körben Aura fizetésére használható.  
**Nem aktív még:** Inflow transition, payment, `play_card`, combat, reaction és ability execution.  
**Dokumentációs szabály:** új contract-dokumentum csak akkor készülhet, ha a tartalomnak nincs természetes helye meglévő aktív főfájlban.