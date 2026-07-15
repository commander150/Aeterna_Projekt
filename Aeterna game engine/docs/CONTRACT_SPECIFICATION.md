# AETERNA Game Engine – Contract Specification

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2  
**Dátum:** 2026-07-15  
**Státusz:** aktív, technológiafüggetlen contract-specifikáció  
**Aktuális Python technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum az AETERNA Game Engine contract-first rétegének aktív szerkezeti specifikációja.

Nem:

- teljes rules engine specifikáció;
- runtime package mezőszintű schema;
- ability module rendszerleírás;
- MatchState kóddokumentáció;
- valamely runtime-nyelv előzetes kiválasztása;
- minden jövőbeli mező kötelező sémává nyilvánítása.

Kapcsolódó aktív dokumentumok:

- `CURRENT_CONTRACT_STATUS.md` – tényleges implementációs státusz;
- `CURRENT_OPEN_QUESTIONS.md` – nyitott és lezárt döntések;
- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md` – történeti migration-reference;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md` – runtime-összehasonlítás;
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md` – közös comparison scenario;
- `ARCHITECTURE.md` – rendszerhatárok;
- `CURRENT_RUNTIME_PACKAGE_STATUS.md` – statikus package-adatút;
- `ABILITY_MODULE_SYSTEM.md` – későbbi ability-contractok;
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md` – aktuális engine-checkpoint.

Eltérés esetén az irányadó sorrend:

1. működő kód és tesztek;
2. `CURRENT_CONTRACT_STATUS.md`;
3. `CURRENT_OPEN_QUESTIONS.md` és aktív döntési dokumentumok;
4. ez a specifikáció;
5. történeti tervek és sample dokumentumok.

---

## 1. Contract-first alapelv

> **Előbb explicit contract, utána implementáció.**

Kötelező következmények:

- pontosan egy authoritative MatchState létezik;
- a frontend és az AI nem találgat legalitást;
- a frontend action requestet küld, nem módosít state-et;
- az authoritative engine validál és hajt végre transitiont;
- rejected request nem okozhat részleges mutationt;
- player-facing output nem teljes MatchState dump;
- hidden information nem szivároghat snapshotba, eventbe, legal actionbe vagy diagnosticsba;
- debug és player-visible contract elkülönül;
- azonos input és state esetén determinisztikus output szükséges;
- a contractoknak Python, C#, GDScript vagy más runtime mellett ugyanazt a játékjelentést kell hordozniuk.

A működő Python referencia és bármely későbbi product runtime ugyanazon fixture-ön legyen összehasonlítható.

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

## 3. Contract-rétegek

### 3.1 Runtime package

Statikus programadat:

- card és deck definition;
- LOOKUPS és canonical értékek;
- aliasok és normalizációs adatok;
- ability registry foundation;
- engine-support és build diagnostics.

Nem MatchState, save game, snapshot, legal action vagy authoritative mérkőzésállapot.

### 3.2 MatchState

Az authoritative belső igaz állapot. Tartalmazhat:

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

A MatchState-ből származtatott, viewer-specifikus output:

- player-visible snapshot;
- public Domain board;
- Wellspring summary;
- debug snapshot;
- később visible event ablak, spectator és replay projection.

### 3.4 Legal action

Az authoritative engine által számított döntési lehetőség.

- nem frontend-találgatás;
- nem state mutation;
- tartalmazhat source-, target-, choice- és payment-contextet;
- fair AI számára csak player-visible információból épülhet.

### 3.5 Action request és response

A request a játékos, frontend vagy AI szándéka. Nem bizonyít legalitást; az engine újra validál.

A response a validálás és transition strukturált eredménye, például:

- accepted/rejected;
- reason és diagnostics;
- state version before/after;
- transition summary;
- typed eventek;
- később pending decision, payment-, target- és choice-result.

### 3.6 Event

A state transition történeti, strukturált leírása.

Az event:

- nem authoritative state;
- determinisztikus sorrendű;
- state versionhöz és matchhez kapcsolódik;
- player-facing formában visibility-szűrt;
- UI-animációhoz, replayhez, AI-elemzéshez és diagnosticshez használható.

### 3.7 Diagnostics

Strukturált hiba-, warning- és auditadat.

- normál hibás inputra lehetőleg non-throwing validator result;
- severity és blocking külön fogalom;
- player-facing diagnostics nem szivárogtathat hidden informationt;
- developer/debug diagnostics külön csatorna.

---

## 4. Aktív schema-index

### Belső state

- `minimal-card-instance-record-v1` – `active_runtime`;
- `minimal-object-reference-v0` – `active_projection`;
- minimal ZoneMove – `active_runtime`;
- MatchState – `active_runtime`;
- `minimal-domain-position-v0` – `active_runtime`;
- `minimal-player-domain-topology-v0` – `active_runtime`;
- `minimal-domain-position-occupancy-v0` – `active_runtime`;
- `minimal-player-domain-occupancy-v0` – `active_runtime`.

### Projection

- `engine-player-visible-snapshot-v2` – `active_projection`;
- `minimal-player-visible-domain-board-v0` – `active_projection`;
- `minimal-public-domain-board-v0` – `active_projection`;
- debug snapshot – `active_projection`.

### Action, event és AI

- minimal legal action space – `foundation_only`;
- minimal action request/response – `active_runtime`;
- `minimal-engine-event-v0` – `active_runtime`;
- `minimal-ai-vs-ai-episode-v1` – `active_runtime`.

### Izolált következő alapok

- `minimal-entity-domain-placement-option-v0` – `active_isolated`;
- `minimal-entity-domain-placement-options-v0` – `active_isolated`;
- `minimal-player-wellspring-state-v0` – `active_isolated`;
- `minimal-wellspring-resource-summary-v0` – `active_isolated`.

### Felváltott vagy fixture

- `engine-player-visible-snapshot-v1` – `superseded`;
- `minimal-card-instance-record-v0` – `superseded`;
- Godot sample snapshot, legal action és event – `debug_fixture`.

---

## 5. Card instance, activity és zónák

A card instance record fő fogalmai:

- stabil `card_instance_id`;
- `card_id`;
- owner és controller;
- zone és zone index;
- visibility;
- created és zone sequence;
- activity state;
- metadata.

Activity:

- deck, hand és discard: `None`;
- Domain és Wellspring: `active` vagy `exhausted`.

Az activity nem summoning sickness és nem támadási jogosultság.

A listás player-zónák és a registry tagsága kétirányú invariáns. Ugyanez érvényes a Domain occupancy és registry kapcsolatára.

---

## 6. Domain topology és placement

Játékosonként:

- 6 Áramlat;
- 6 horizon slot;
- 6 zenith slot;
- 6 statikus seal position;
- 18 stabil position reference;
- 12 foglalható horizon/zenith slot.

A seal position nem általános occupancy slot.

A structural Entity placement:

- 12 saját horizon/zenith opciót generál;
- foglalt targetet disabled structurális optionként megőriz;
- nem ellenőrzi a timingot, priorityt, Magnitúdót, paymentet, kártyaszöveget vagy entry-state-et;
- ezért nem teljes `play_card` legalitás.

---

## 7. Snapshot és visibility

### 7.1 Általános policy

Aktív alapok:

- saját kéz: owner-visible;
- ellenfél kéz: redacted és count-only;
- deck: count-only;
- discard: public;
- Domain board: public;
- teljes registry, paklisorrend és belső topology/occupancy nem kerül player-facing outputba;
- fair AI ugyanazt a canonical player-visible observationt használja, mint az azonos oldalon játszó emberi játékos.

### 7.2 Ősforrás visibility-policy

**Emberi döntés – 2026-07-15:**

- a teljes Magnitúdó mindkét játékos számára nyilvános;
- az Aktív és Kimerült Ősforrás-lapok száma és activity state-je nyilvános;
- a saját játékos a saját képpel lefelé lévő Ősforrás-lapjainak kártyaazonosságát később is visszanézheti;
- az ellenfél nem láthatja ezek kártyaazonosságát;
- opponent projection csak count- és activity-adatot ad;
- technikai `card_instance_id` egyik játékos számára sem jelenhet meg;
- owner projection biztonságos reference-en keresztül Card_ID-t és megjelenítési adatot adhat;
- debug projection ettől elkülönítve tartalmazhat technikai azonosítót.

Következmény:

- a frontend nem számolja ki önállóan a Magnitúdót vagy activity countot rejtett rekordokból;
- az engine viewer-specifikus Wellspring projectiont ad;
- ugyanazon belső state-ből owner és opponent számára eltérő identity-tartalmú snapshot készül;
- fair AI pontosan ugyanazt látja, amit az adott játékos láthat.

### 7.3 Debug snapshot

A debug snapshot többletinformációt tartalmazhat, de nem használható fair AI observationként és nem kerülhet normál player-facing csatornába.

### 7.4 Tervezett projectionök

- Wellspring summary tényleges runtime-integrációja;
- Pecsét állapot;
- match finished, winner és victory reason;
- pending decision;
- recent visible event ablak;
- spectator és replay projection.

---

## 8. Legal action, request és response

Aktív minimal actionök:

- `draw_card`;
- `end_turn`.

Kötelező legal-action elvek:

- csak az authoritative engine generálhat legal actiont;
- fair AI és normál UI ugyanazon legalitási eredményre épül;
- hidden source vagy target identity nem szivároghat;
- stabil, determinisztikus rendezés szükséges;
- debug disabled reason nem válhat hidden-information csatornává.

A current request match-, player-, action- és expected-state-version adatot hordoz. Stale vagy hibás state version kontrollált rejectet ad.

Reject esetén:

- nincs state mutation;
- nincs transitionből származó event-log növekedés;
- active/priority player és zónaállapot változatlan;
- strukturált reason és diagnostics készül.

Később szükséges:

- Inflow action;
- `play_card`;
- target és choice;
- payment;
- pending decision;
- ability;
- combat;
- reaction;
- idempotencia és duplicate policy csak tényleges kliens/PvP igénynél.

---

## 9. Event-contractok

Aktív typed eventek:

- `zone_move`;
- `turn_transition`.

A draw `zone_move`, az end turn `turn_transition` eventet ad.

Nincs szükség általános `action_resolved` eventre, ha a transition pontosabb typed eventtel kifejezhető.

Tervezett eventek:

- Inflow/Wellspring transition;
- activity state change;
- Aura payment;
- card played;
- Entity entered Domain;
- attack, block és Entity-sebzés;
- Pecsét feltörés/visszaállítás;
- victory és defeat;
- ability trigger és resolution.

---

## 10. Ősforrás, Beáramlás és erőforrás

### 10.1 Wellspring-state és resource summary

Canonical alapszámítás:

- `magnitude == wellspring_card_count`;
- `available_aura == active_source_count`;
- `active_source_count + exhausted_source_count == total_source_count`.

Ne legyen külön authoritative `magnitude`, `spent_aura` vagy `remaining_aura` számláló, ha az érték zónából és activity state-ből származtatható.

### 10.2 Beáramlás Core-döntés

A normál Beáramlás:

- a kör második fázisának opcionális művelete;
- legfeljebb 1 kézlapot helyez az Ősforrásba;
- a lap képpel lefelé kerül;
- `active` activity state-et kap;
- azonnal növeli a Magnitúdót;
- azonnal növeli az elérhető Aurát;
- ugyanabban a körben használható Aura fizetésére;
- fizetéskor `exhausted` állapotba kerül;
- külön kártyahatásból történő Ősforrás-bővítés nem fogyasztja el a normál Beáramlás lehetőségét, hacsak a hatás másként nem rendelkezik.

A szabályi döntés dokumentált; a transition contract még `planned`.

### 10.3 Következő erőforrás-contractok

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

Nem implementált:

- typed Aura;
- payment;
- temporary Aura;
- Rezonancia;
- Aura-égés;
- Magnitúdó modifier vagy override;
- automatic/manual payment policy.

---

## 11. AI és trajectory

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

Replay readiness jelenleg `false`.

---

## 12. Ability registry és support

A registry jelenleg foundation, nem executor.

Bizonyított állapot:

- 2 modul `declared_only`;
- kártyák supportja `not_evaluated`;
- `runtime_executes_abilities: false`;
- card-local fallback csak átmeneti, diagnosztizált és migrációs jelölt lehet.

Ability executor csak a Wellspring, Beáramlás, erőforrás, `play_card`, timing, phase, priority, target, choice és event alapok után indulhat.

---

## 13. Validációs alapelvek

- JSON-kompatibilis dict/list output;
- schema version és contract type;
- non-throwing validator normál hibás inputra;
- strukturált `{valid, errors}` eredmény;
- kontrollált builder exception invalid state/query esetén;
- deep-copy és inputváltozatlanság;
- determinisztikus sorrend és azonosítók;
- runtime state leak és tiltott mezők ellenőrzése;
- canonical builder/validator újrahasználata;
- hidden-information audit.

---

## 14. Tiltott vagy félrevezető modellek

Nem használható:

- teljes MatchState player snapshotként;
- UI mint rules engine;
- sample fixture production schemaként;
- structural placement teljes play legalityként;
- replay foundation kész replayként;
- Pecsét HP;
- Aeternal HP, sebzés vagy gyógyítás;
- `player_damage`, `aeternal_damage`, `heal_player`, `heal_aeternal`, `ward_hp`, `seal_hp`, `ward_damage`, `seal_damage` mint aktív canonical gameplay-fogalom.

Modern irány:

- Pecsét standing/broken/restored/removed állapot;
- `ward_break`, `ward_restore`, `ward_break_prevent`;
- `aeternal_unprotected`;
- `direct_attack_victory`;
- `player_defeated`.

---

## 15. Következő contract-lánc

A runtime-nyelvi döntési kapu után:

1. Wellspring production integráció;
2. viewer-specifikus Wellspring projection;
3. Inflow precondition és transition;
4. Magnitúdó-preflight;
5. typed Aura és payment;
6. activity mutation;
7. Entity play precondition;
8. `play_card` action és response;
9. Entity entry event;
10. phase/priority/reaction contractok;
11. combat;
12. ability execution.

A contract-specifikáció csak új működő contract vagy elfogadott emberi döntés után frissítendő. Új javasolt mező nem válik canonical követelménnyé pusztán dokumentációs megjelenéstől.