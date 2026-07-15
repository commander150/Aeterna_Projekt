# AETERNA Game Engine – Aktuális Engine Checkpoint

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív technikai folytatási checkpoint  
**Báziscommit:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`  
**Báziscommit üzenete:** `Add minimal Wellspring resource contracts`

Ez a dokumentum az új AETERNA Python rules engine jelenlegi tényleges állapotát rögzíti.

Feladata:

- biztonságos folytatási pont biztosítása;
- az elkészült contractok és runtime-rétegek összefoglalása;
- az implementált és nem implementált funkciók világos elhatárolása;
- a következő programozási függőségi lánc rögzítése;
- a tesztállapot és az ismert problémák megőrzése.

Ez nem teljes architektúra-specifikáció és nem hivatalos játékszabály.

---

## 1. Rövid állapot

Az új Python engine már nem pusztán statikus contractminta.

Jelenleg működik:

- minimal authoritative MatchState;
- card instance registry;
- deckből kézbe húzás;
- körátadás;
- typed eventek;
- state version guard;
- invariánsok;
- player-visible snapshot;
- Domain topológia és occupancy;
- public board projection;
- determinisztikus AI-vs-AI epizód;
- izolált Entitás-placement option;
- Aktív/Kimerült card-instance állapot;
- izolált Wellspring és erőforrás-summary contract.

Jelenleg még nem működik tényleges gameplayként:

- Beáramlás;
- Aura-payment;
- Magnitúdó-precondition;
- `play_card`;
- Entitás Domainba helyezése actionön keresztül;
- teljes fázis- és prioritásrendszer;
- harc;
- képességvégrehajtás;
- Pecsét-state;
- győzelmi feltétel.

---

## 2. Aktuális commitlánc

A jelen checkpoint szempontjából meghatározó egymásra épülő commitok:

- `68049205ad1453380f23fe9324af92f1a109e074` – `Add expected state version guard`
- `3874cb13316c6f119079536dd00f3ee6af586abe` – `Add minimal engine context summary`
- `36c64a03a198c23fee069d9fac121f3e36b980b8` – `Add engine object identity and zone move plan`
- `49e2606dd5c6b68101354244622cdc5f0cadae8d` – `Add minimal card instance record helper`
- `7c6649c578f09e7ac07fa144244497952dde5c05` – `Add minimal zone move record helper`
- `2159b0e994ef944188efe6ee80bf848610d94831` – `Migrate minimal draw state to card instances`
- `fd4cd726f5bfbc7cf335eeb3f7f731f5f3b4aeb4` – `Integrate zone move event for draw`
- `084b04a6fbb02f38bc3c2b41b01f6bc9d2c9af17` – `Extract generic engine event envelope helper`
- `0f547e3504a14f64cc20a828836ea7347ea7ff6a` – `Migrate end turn to typed transition event`
- `41b874ccb4a4a960143875c7816f7383f9d4430e` – `Add canonical AI episode trajectory`
- `0e06efa85387736054469ca2378aca7899a02538` – `Stabilize minimal player visible snapshot`
- `691df48f443c76f8b52f1587d1c0698562d4fa1d` – `Add minimal Domain position contracts`
- `9de3a45eb7d45e3dea55963db784b8d045f162fe` – `Integrate Domain topology into minimal match state`
- `54b16c6c396fe396e69c5dcacd1ca1399224a36d` – `Add minimal Domain occupancy contracts`
- `8f8fcd4dea0f2eacbf74cfea98f679353b8506d1` – `Integrate Domain occupancy into minimal match state`
- `1032323da6dde167fae33233bf0b3c3ba4740e5c` – `Add player visible Domain board projection`
- `00bbe273f70524d505aebce82936d8457d3b83dd` – `Add structural Entity Domain placement options`
- `11958d4952715275890f64cef4202ad1ace2bab9` – `Add canonical card instance activity state`
- `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b` – `Add minimal Wellspring resource contracts`

A 0.0.1 célállapotot rögzítő dokumentum külön commitban került be:

- `d3103d0eff6def49b75fced31cfb4204dc853a13` – `Add AETERNA 0.0.1 milestone target document`

---

## 3. Authoritative állapotmodell

### 3.1 MatchState

A minimal MatchState jelenleg többek között kezeli:

- match identity;
- state version;
- aktív játékos;
- priority player;
- minimal phase;
- event log;
- card instance registry;
- player state-ek;
- Domain topológiák;
- Domain occupancy state-ek.

A Wellspring state még nincs a MatchState-be integrálva.

### 3.2 PlayerState

A játékos jelenlegi instance-listás zónái:

- `deck_card_instance_ids`
- `hand_card_instance_ids`
- `discard_card_instance_ids`

Még hiányzik:

- `wellspring_card_instance_ids`

A Domain nem külön egyszerű instance-lista, hanem:

- statikus topológia;
- occupancy slotok;
- occupant `card_instance_id` kapcsolat.

### 3.3 Card instance registry

A card instance record aktív sémája:

- `minimal-card-instance-record-v1`

Fő mezők:

- `card_instance_id`
- `card_id`
- `owner_player_id`
- `controller_player_id`
- `zone`
- `zone_index`
- `visibility`
- `created_sequence`
- `zone_sequence`
- `activity_state`
- `metadata`

Az instance konkrét Domain-pozíciója nem a registry rekordban tárolódik.

A kapcsolat authoritative útja:

- Domain occupancy slot `position_id`
- `occupant_card_instance_id`
- card instance registry

---

## 4. Zónák és aktivitási állapot

### 4.1 Aktív zónák

A jelenlegi runtime és contract-réteg ismeri:

- `deck`
- `hand`
- `discard`
- `domain`
- `wellspring`

A Wellspring egyelőre csak izolált contract szinten ismert, nem production MatchState-zónaként.

### 4.2 Activity state

Támogatott értékek:

- `None`
- `active`
- `exhausted`

Canonical zone/activity kapcsolat:

- deck → `None`
- hand → `None`
- discard → `None`
- domain → `active` vagy `exhausted`
- wellspring → `active` vagy `exhausted`

Az activity state nem jelenti:

- az idézési betegséget;
- támadási jogosultságot;
- legal action státuszt;
- face-up/face-down állapotot;
- ownershipet vagy kontrollt.

### 4.3 Visibility

A Wellspring canonical rejtett visibility értéke:

- `owner_only`

A Domain occupant canonical visibility értéke:

- `public`

Az ObjectReference schema jelenleg nem tartalmaz `activity_state` mezőt.

---

## 5. Draw transition

A `draw_card` jelenlegi működése:

1. a deck első `card_instance_id` értékét kiválasztja;
2. eltávolítja a decklistából;
3. hozzáadja a hand listához;
4. frissíti a registry rekord zónáját;
5. újraindexeli az érintett listát;
6. növeli a state versiont;
7. typed `zone_move` eventet készít.

A húzott instance activity state-je:

- deckben `None`;
- kézben továbbra is `None`.

A draw nem módosít:

- Domain topológiát;
- Domain occupancyt;
- Wellspring state-et;
- Aura- vagy Magnitúdó-értéket.

---

## 6. End turn transition

Az `end_turn` jelenlegi működése:

- aktív játékost vált;
- priority playert frissít;
- state versiont növel;
- typed `turn_transition` eventet készít.

Az `end_turn` jelenleg nem:

- futtat teljes körstruktúrát;
- állít vissza Kimerült lapokat;
- kezel Ébredés fázist;
- kezel Beáramlást;
- indít reakciós ablakot.

---

## 7. Eventrendszer

### 7.1 Generic envelope

Aktív schema:

- `minimal-engine-event-v0`

### 7.2 Aktív typed eventek

- `zone_move`
- `turn_transition`

### 7.3 Jelenlegi elvek

- sikeres transition pontosan meghatározott typed eventet ad;
- event sequence determinisztikus;
- player projection nem kap teljes debug payloadot;
- nincs általános aktív `action_resolved` esemény.

Még hiányzik:

- Wellspring zónamozgási event;
- payment event;
- card played event;
- Entity entered Domain event;
- combat eventek;
- win/loss event.

---

## 8. Domain és board

### 8.1 Topológia

Aktív contractok:

- `minimal-domain-position-v0`
- `minimal-player-domain-topology-v0`

Játékosonként:

- 6 current;
- 6 Horizont-pozíció;
- 6 Zenit-pozíció;
- 6 Pecsét-pozíció;
- összesen 18 stabil pozícióreferencia.

### 8.2 Occupancy

Aktív contractok:

- `minimal-domain-position-occupancy-v0`
- `minimal-player-domain-occupancy-v0`

Játékosonként:

- 12 card occupancy slot;
- 6 Horizont;
- 6 Zenit;
- a Pecsét nem card occupancy slot.

Canonical modell:

- egy pozíció legfeljebb egy card instance-et tartalmaz;
- occupied slot `occupant_card_instance_id` értéket tárol;
- az occupant registry rekordjának zónája `domain`;
- `zone_index` Domainban `None`;
- visibility `public`;
- controller a Domain játékosa;
- owner eltérhet a controllertől.

### 8.3 Player-visible board

Aktív contract:

- `minimal-player-visible-domain-board-v0`

A player-visible snapshot mindkét játékos számára ugyanazt a public boardot mutatja.

Megjelenik:

- current 1–6;
- Horizont és Zenit slot;
- üres vagy foglalt állapot;
- occupied slotban canonical ObjectReference;
- statikus Pecsét-pozícióreferencia.

Nem jelenik meg:

- teljes topology;
- teljes occupancy;
- teljes registry;
- rejtett kéz- vagy deckadat;
- Pecsét aktuális állapot.

---

## 9. Player-visible snapshot

Aktív schema:

- `engine-player-visible-snapshot-v2`

Fő elvek:

- saját kéz owner-visible;
- ellenfél kéz count-only és redacted;
- deckek count-only;
- discard public;
- board public;
- nincs teljes MatchState;
- nincs teljes registry;
- nincs debug event payload.

A snapshot board modelje:

- `minimal-public-domain-board-v0`

A Wellspring még nem jelenik meg a player snapshotban.

---

## 10. Structural Entity placement

Aktív contractok:

- `minimal-entity-domain-placement-option-v0`
- `minimal-entity-domain-placement-options-v0`

Placement model:

- `structural-entity-domain-placement-v0`

A helper ellenőrzi:

- source instance létezik;
- source saját kézben van;
- controller egyezik;
- runtime card type canonical értéke `entity`;
- target saját Horizont vagy Zenit;
- target empty vagy occupied.

Eligible Entitás esetén:

- pontosan 12 target option;
- foglalt mező is megmarad;
- foglalt mező `structurally_available: false`;
- reason `position_occupied`.

Nem ellenőrzött rétegek:

- timing;
- priority;
- fázis;
- Magnitúdó;
- Aura-payment;
- kártyaszöveg-pozíciókorlátozás;
- ability support;
- entry state;
- idézési betegség.

Ezért a contract nem jelent teljes play legalityt és nincs bekötve a legal action listába.

---

## 11. Wellspring contract

### 11.1 Aktív izolált state contract

Schema:

- `minimal-player-wellspring-state-v0`

Fő mezők:

- player ID;
- zone `wellspring`;
- visibility mode `owner_only`;
- ordered instance ID-lista;
- card count;
- metadata.

Az izolált builder ellenőrzi:

- instance létezését;
- registry identityt;
- zone értéket;
- zone indexet;
- controllert;
- activity state-et;
- visibilityt;
- duplikációt.

### 11.2 Resource summary

Schema:

- `minimal-wellspring-resource-summary-v0`

Resource model:

- `base-wellspring-count-and-activity-v0`

Canonical számítás:

- `magnitude == wellspring_card_count`
- `available_aura == active_source_count`
- `active_source_count + exhausted_source_count == wellspring_card_count`

A Kimerült Ősforrás-lap:

- továbbra is növeli a Magnitúdót;
- nem biztosít elérhető Aurát.

Még nincs:

- typed Aura;
- payment;
- Rezonancia;
- temporary Aura;
- Aura-égés;
- Magnitúdó-override;
- MatchState-integráció;
- Beáramlás action.

---

## 12. Invariánsok

A state-invariant rendszer jelenleg többek között védi:

- playerhalmazt;
- aktív és priority playert;
- state versiont;
- event sequence-et;
- card instance registryt;
- Card_ID és instance ID elhatárolását;
- instance-listák duplikációját;
- instance orphan és multiple-zone állapotát;
- registry zone és container egyezését;
- zone indexeket;
- activity state és zone kapcsolatát;
- Domain topology contractot;
- Domain occupancy contractot;
- occupancy és registry kétirányú kapcsolatát;
- Domain occupant controllert és visibilityt.

A Wellspring még nincs a MatchState fő invariánsrendszerébe integrálva.

---

## 13. AI és trajectory

Aktív episode contract:

- `minimal-ai-vs-ai-episode-v1`

A trajectory:

- accepted és rejected stepeket kezel;
- player-visible observationre épül;
- deep-copyzott adatokat tárol;
- determinisztikus JSON outputot ad;
- replay előkészítés alapját biztosítja;
- jelenleg `replay_ready: false`.

A rövid AI-vs-AI bot jelenleg csak a minimal actiontérben működik.

Nem tekinthető még valódi, teljes AETERNA-játékos AI-nak.

---

## 14. Tesztállapot

A `84a7e8f4` bázisnál:

- 59 Python tesztmodul izolált futása zöld;
- összesen 333 izolált teszt zöld;
- minimal engine JSON smoke zöld;
- AI-vs-AI text smoke zöld;
- AI-vs-AI JSON smoke zöld;
- 8 step;
- 8 event;
- 0 diagnostic;
- két azonos AI JSON-futás byte-szinten azonos.

### 14.1 Ismert monolitikus discovery-probléma

A teljes monolitikus unittest discoveryben két sorrendfüggő XLSX mock-probléma marad:

- `test_finds_xlsx_files_only_in_source_directory`
- `test_lists_sheets_in_read_only_data_only_mode`

Jelenlegi eredmény:

- 1 failure;
- 1 error.

Ezek:

- izolált futásban zöldek;
- nem az új rules engine ismert regressziói;
- külön tesztizolációs és mock-cleanup feladatban javítandók.

---

## 15. Jelenlegi nem implementált rendszerek

A jelen checkpoint nem bizonyítja:

- teljes AETERNA körstruktúrát;
- phase és priority rendszert;
- reakciós ablakokat;
- Burst-rendszert;
- Beáramlást;
- Magnitúdó-preconditiont;
- Aura-paymentet;
- typed Aurát;
- `play_card` actiont;
- kézből Domainba végrehajtott Entitás-kijátszást;
- entry-state policyt;
- idézési betegséget;
- Gyorsaságot;
- támadást és blokkolást;
- sebzést;
- HP-t;
- Oltalmat;
- Pecsét-state-et és Pecsét feltörést;
- Aeternal-state-et;
- ability executort;
- teljes target legalityt;
- győzelmi feltételeket;
- replay-végrehajtást;
- emberi játékmenetet;
- végleges Godot UI-t.

---

## 16. Következő biztonságos programozási lépés

### 16.1 Feladat

Az izolált Wellspring contract integrálása a production PlayerState és MatchState állapotba.

### 16.2 Várt eredmény

- PlayerState új canonical listája:
  - `wellspring_card_instance_ids`
- minden production player üres Wellspringgel indul;
- MatchState JSON-kompatibilis marad;
- listás zónák authoritative tagsági modellje kiterjed Wellspringre;
- registry record `zone == "wellspring"` esetén pontosan egy Wellspring-listában szerepel;
- Wellspring-listás instance nem szerepelhet deckben, handben, discardban vagy Domain occupancyben;
- zone index egyezik a listaindexszel;
- visibility `owner_only`;
- activity active vagy exhausted;
- controller a Wellspring játékosa;
- resource summary canonical helperből készül;
- draw és end_turn változatlan.

### 16.3 Ebben a következő lépésben még ne készüljön

- Beáramlás action;
- hand → Wellspring transition;
- Aura-payment;
- Kimerítés/Visszaállítás action;
- player-visible Wellspring projection;
- új engine event;
- `play_card`.

---

## 17. Következő függőségi lánc

A javasolt fejlesztési sorrend:

1. Wellspring MatchState-integráció;
2. player-visible Wellspring summary;
3. Inflow precondition contract;
4. Inflow transition és typed event;
5. Magnitúdó-preflight;
6. Aura-source és payment contract;
7. activity mutation transition;
8. Entity play precondition;
9. `play_card` action;
10. hand → Domain transition;
11. Entity entry-state;
12. teljesebb phase és priority rendszer.

Nem szabad a lánc végét a korábbi függőségek nélkül implementálni.

---

## 18. Biztonságos folytatási szabályok

A következő programozási feladatnál:

- előbb olvasd el a releváns contract helpereket;
- ne duplikáld a canonical buildert vagy validátort;
- ne módosíts egyszerre több schema-réteget;
- ne készíts hallgatólagos gameplay-szabályt;
- bizonytalan szabályt ellenőrizz a hivatalos 1.4v főforrásban;
- minden state-mutation legyen atomikus;
- rejected action ne mutáljon state-et;
- minden sikeres transition növelje a state versiont;
- event sequence legyen determinisztikus;
- player-visible és debug output maradjon külön;
- rejtett információ ne szivárogjon;
- minden új helper legyen JSON-kompatibilis és deep-copy biztonságos;
- minden új működés kapjon célzott tesztet;
- a teljes Python készlet fusson izolált modulonként;
- smoke és determinisztikus AI epizód maradjon zöld.

---

## 19. Dokumentációs adósság

A jelen checkpoint létrejöttekor frissítendő vagy később rendezendő:

- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`
  - felváltva v6.0-val;
- root `README.md`
  - még részben exporter/Godot-first projektképet mutat;
- `Aeterna game engine/README.md`
  - még nem tükrözi teljesen az aktív rules engine állapotot;
- `docs/checkpoints/CHECKPOINTS.md`
  - a korábbi runtime package és Godot checkpointok dominálják;
  - később időrendben be kell olvasztani a jelen rules-engine checkpointot;
- `docs/ARCHITECTURE.md`
  - összevetendő az authoritative Python rules-engine iránnyal;
- `docs/CONTRACT_SPECIFICATION.md`
  - frissítendő a tényleges v2 snapshot, Domain, activity és Wellspring contractokkal;
- `docs/OPEN_QUESTIONS.md`
  - megőrizendők és bővítendők az új döntési kapuk.

A dokumentációs adósság nem blokkolja az izolált engine-fejlesztést, de nem maradhat tartósan rendezetlen.

---

## 20. Rövid folytatási összefoglaló

**Báziscommit:** `84a7e8f4`  
**Engine állapot:** determinisztikus minimal rules engine, boarddal és izolált erőforráscontracttal  
**Aktív actionök:** `draw_card`, `end_turn`  
**Aktív typed eventek:** `zone_move`, `turn_transition`  
**Player snapshot:** v2, public Domain boarddal  
**Card instance schema:** v1, `activity_state` mezővel  
**Wellspring:** izolált state és summary kész, MatchState-integráció hiányzik  
**Tesztállapot:** 59 izolált modul, 333 zöld teszt  
**Ismert tesztprobléma:** két sorrendfüggő XLSX mock-eltérés a monolitikus discoveryben  
**Következő feladat:** Wellspring runtime integráció  
**Tiltott ugrás:** közvetlen `play_card` vagy payment implementáció az előfeltételek nélkül
