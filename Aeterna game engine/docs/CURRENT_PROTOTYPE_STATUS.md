# AETERNA Game Engine – Current Prototype Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív prototípus- és fejlesztési bizonyíték státusztérkép  
**Technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum azt rögzíti, hogy a `PROTOTYPE_PLANS.md` történeti és jövőbeli tervlistájából mely prototípusok készültek el, melyek váltak az aktív rendszer részévé, melyek lettek felváltva, és melyek a valóban következő feladatok.

Nem helyettesíti:

- a részletes történeti prototípustervet;
- a current engine checkpointot;
- a v6.0 projekttervet;
- a szűk programozási task specifikációkat.

---

## 1. Státuszjelölések

| Státusz | Jelentés |
|---|---|
| `completed_foundation` | A prototípus célját bizonyította, alapként megtartandó. |
| `promoted_to_active_system` | A prototípusból aktív tooling-, runtime- vagy contract-réteg lett. |
| `active_next_step` | Közvetlen vagy közeli programozási feladat. |
| `deferred` | Későbbi roadmap-szakaszra halasztott. |
| `superseded_by_architecture` | Új architektúradöntés miatt már nem aktív irány. |
| `historical_reference` | Történeti bizonyíték, de nem aktuális task queue. |
| `not_started` | Még nincs implementálva. |

---

## 2. A prototípus-szakasz fő eredménye

A korai prototípus-szakasz sikeresen bizonyította, hogy:

- Python képes runtime package-et építeni;
- Godot képes azt betölteni;
- Godot registryk működnek;
- statikus snapshot, legal action és event contract megjeleníthető;
- card reference-ek feloldhatók;
- contract consistency smoke írható;
- unified debug dashboard működhet;
- XLSX exporter migrálható az új Python tooling alá;
- valós kártya- és deckadatból publisholható package készíthető;
- a normalizációs és diagnostics réteg külön kezelhető.

Ez a prototípus-szakasz nem lett lecserélve.

A sikeres eredményei az aktív rendszer alapjai lettek.

---

## 3. Elkészült runtime package és Godot prototípusok

### 3.1 Python sample runtime package generator

**Státusz:** `completed_foundation`

Bizonyította:

- többfájlos package előállítását;
- manifest és package-fájlok létrehozását;
- determinisztikus sample buildet;
- Python unit tesztelhetőséget.

Mai szerepe:

- történeti alap;
- tesztfixture;
- a valós package builder előzménye.

### 3.2 Godot runtime package loader

**Státusz:** `promoted_to_active_system`

Bizonyította és ma is ellátja:

- package betöltését;
- card, deck és lookup registryk felépítését;
- ability és diagnostics adatok olvasását;
- headless package smoke-ot.

Aktív consumption path:

- `res://runtime_package`

### 3.3 Sample contracts loader

**Státusz:** `completed_foundation`

Bizonyította:

- snapshot;
- legal action;
- event log

statikus contractok Godot-oldali betöltését.

Mai szerepe:

- debug- és UI-minta;
- történeti contract fixture;
- nem az aktuális Python player snapshot authoritative forrása.

### 3.4 Snapshot viewer

**Státusz:** `completed_foundation`

Bizonyította:

- snapshot-adatok egyszerű Godot debug megjelenítését;
- scene és headless smoke futtatását.

Nem a végleges player UI.

### 3.5 Legal action debug panel

**Státusz:** `completed_foundation`

Bizonyította:

- enabled és disabled sample actionök megjelenítését;
- debug panel és smoke működését.

A jelenlegi Python engine legal action contractja később külön integrálandó.

### 3.6 Event log debug view

**Státusz:** `completed_foundation`

Bizonyította:

- eventlista;
- sequence;
- debug megjelenítés

Godot-oldali kezelését.

### 3.7 Card reference resolver

**Státusz:** `completed_foundation`

Bizonyította:

- runtime package registryből történő card reference feloldást;
- snapshot, legal action és event debugadat olvashatóbbá tételét;
- missing reference kontrollált kezelésének alapját.

### 3.8 Contract consistency smoke

**Státusz:** `completed_foundation`

Bizonyította:

- schema-verziók ellenőrzését;
- `match_id` konzisztenciát;
- snapshot-reference kapcsolatot;
- card registry hivatkozásokat;
- diagnostics és package-contract együttműködést.

### 3.9 Unified debug dashboard

**Státusz:** `completed_foundation`

Bizonyította:

- package summary;
- snapshot;
- legal actions;
- event log;
- diagnostics;
- resolved card adatok

egy közös Godot debug nézetben történő összefogását.

### 3.10 XLSX exporter migráció

**Státusz:** `promoted_to_active_system`

Bizonyította:

- az exporter funkció áthelyezhető az új Python tooling alá;
- explicit source és output útvonalak működnek;
- nem szükséges a régi `XLSX export/source` kötelező útvonala;
- JSONL smoke futtatható.

### 3.11 Runtime package publish pipeline

**Státusz:** `promoted_to_active_system`

Bizonyította:

- candidate buildet;
- blocking validationt;
- Godot consumption copy frissítést;
- valós kártya-, deck- és lookupadatok publisholását;
- normalization alias és report outputokat.

Aktuális külön státuszdokumentum:

- `CURRENT_RUNTIME_PACKAGE_STATUS.md`

---

## 4. Elkészült Python rules-engine prototípusok

A rules engine szakaszban a „prototípus” több esetben már aktív minimal runtime-réteggé vált.

### 4.1 Minimal MatchState és session

**Státusz:** `promoted_to_active_system`

Elkészült:

- MatchState;
- PlayerState;
- session;
- environment;
- action request/response alap;
- state version guard.

### 4.2 Draw transition

**Státusz:** `promoted_to_active_system`

Elkészült:

- card instance deck → hand mozgatás;
- listák és indexek frissítése;
- state version növelése;
- typed `zone_move` event.

### 4.3 End-turn transition

**Státusz:** `promoted_to_active_system`

Elkészült:

- active player és priority player váltás;
- typed `turn_transition` event.

### 4.4 Typed event envelope

**Státusz:** `promoted_to_active_system`

Elkészült:

- generic engine event envelope;
- determinisztikus event sequence;
- debug és player projection elhatárolása.

### 4.5 Player-visible snapshot

**Státusz:** `promoted_to_active_system`

Elkészült:

- player snapshot v2;
- saját kéz láthatóság;
- ellenfél kéz redakció;
- deck count-only;
- discard public;
- public Domain board.

### 4.6 AI episode trajectory

**Státusz:** `promoted_to_active_system`

Elkészült:

- accepted és rejected step;
- player-visible observation;
- determinisztikus JSON;
- AI-vs-AI smoke;
- replay-alap.

### 4.7 Domain topology

**Státusz:** `promoted_to_active_system`

Elkészült:

- 6 Áramlat;
- Horizont;
- Zenit;
- Pecsét-pozícióreferencia;
- MatchState-integráció.

### 4.8 Domain occupancy

**Státusz:** `promoted_to_active_system`

Elkészült:

- 12 card slot játékosonként;
- occupancy és registry kétirányú invariáns;
- public board projection.

### 4.9 Structural Entity placement options

**Státusz:** `completed_foundation`

Elkészült:

- saját kézben lévő Entitás source-ellenőrzése;
- 12 saját Horizont/Zenit target;
- foglalt mező disabled structurális optionként;
- full play legality explicit kizárása.

Még nincs legal actionbe kötve.

### 4.10 Card instance activity state

**Státusz:** `promoted_to_active_system`

Elkészült:

- `activity_state`;
- `active`;
- `exhausted`;
- zone/activity invariáns.

### 4.11 Wellspring state és resource summary

**Státusz:** `completed_foundation`

Elkészült izolált helperként:

- Wellspring instance-lista contract;
- active/exhausted forrás;
- Magnitúdó;
- elérhető Aura;
- deep-copy és validáció.

Még nincs PlayerState/MatchState-integráció.

---

## 5. Felváltott vagy már nem aktív prototípusirányok

### 5.1 Minimal GDScript rules service

**Státusz:** `superseded_by_architecture`

A korábbi terv célja annak vizsgálata volt, hogy a Godot/GDScript lehet-e authoritative rules engine.

A jelenlegi döntés:

- a Python rules engine authoritative;
- Godot nem kap párhuzamos rules runtime-ot;
- UI node-okban nem lehet szabálylogika.

Ezért külön authoritative GDScript rules-service prototípus jelenleg nem aktív feladat.

Godotban később készülhet:

- kliensadapter;
- request builder;
- response consumer;
- presentation state;

de nem második szabálymotor.

### 5.2 Python–GDScript rules comparison scenario

**Státusz:** `superseded_by_architecture`

Mivel nem készül két authoritative szabálymotor, nincs szükség teljes szabályeredmény-összehasonlításra.

Később szükség lehet:

- transport contract tesztre;
- serialization round-trip tesztre;
- Python output ↔ Godot parser compatibility tesztre.

Ez nem rules-engine comparison.

### 5.3 Statikus action response sample mint elsődleges irány

**Státusz:** `historical_reference`

A Python minimal engine már valódi action response és rejected response contractot használ.

A statikus Godot action-response fixture később kliensparser-teszthez hasznos lehet, de nem a rules engine következő bizonyítási feladata.

### 5.4 Ability registry support viewer mint közeli prioritás

**Státusz:** `deferred`

A viewer hasznos lehet, de az ability execution még nincs implementálva.

A jelenlegi kritikus út erősebb prioritású:

- Wellspring;
- Beáramlás;
- payment;
- Entitás kijátszása.

---

## 6. Aktív következő prototípus- és implementációs lánc

### 6.1 Wellspring runtime integráció

**Státusz:** `active_next_step`

Cél:

- `wellspring_card_instance_ids` PlayerState-be;
- initial üres Wellspring;
- MatchState-integráció;
- authoritative zónatagság;
- registry cross-validation;
- resource summary elérés.

Nem cél még:

- Beáramlás;
- payment;
- player-visible Wellspring;
- új event.

### 6.2 Player-visible Wellspring summary

**Státusz:** `not_started`

Cél:

- Magnitúdó;
- available Aura;
- active/exhausted count;
- hidden Card_ID és instance-lista szivárgásának tiltása.

### 6.3 Inflow precondition

**Státusz:** `not_started`

Cél:

- source saját kéz;
- timing;
- priority;
- körönkénti limit;
- target saját Wellspring;
- belépési state.

### 6.4 Inflow transition és event

**Státusz:** `not_started`

Cél:

- hand → Wellspring;
- zone index;
- owner-only visibility;
- activity state;
- state version;
- typed event;
- player projection.

### 6.5 Magnitude preflight

**Státusz:** `not_started`

Cél:

- kártya Magnitúdó-követelményének ellenőrzése;
- paymenttől külön réteg.

### 6.6 Aura payment contract

**Státusz:** `not_started`

Cél:

- source selection;
- active Wellspring források;
- typed Aura;
- atomikus Kimerítés;
- rollback és eventek.

### 6.7 Entity play precondition és `play_card`

**Státusz:** `not_started`

Csak az előző rétegek után.

Követelmények:

- source eligibility;
- timing;
- Magnitúdó;
- payment;
- structural placement;
- entry state;
- atomic hand → Domain transition.

---

## 7. Későbbi prototípusok

### 7.1 Python–Godot transport

**Státusz:** `deferred`

Vizsgálandó modellek:

- lokális subprocess;
- localhost service;
- fájlalapú fejlesztői híd;
- beágyazott vagy csomagolt Python runtime.

Ez kliensintegrációs prototípus, nem rules-engine döntés.

### 7.2 Godot player UI vertical slice

**Státusz:** `deferred`

Csak stabilabb player-facing snapshot, legal action és action response után.

### 7.3 Ability executor

**Státusz:** `deferred`

Előfeltételek:

- stabil action/event/state alap;
- phase/priority;
- target contract;
- payment;
- support policy.

### 7.4 Combat vertical slice

**Státusz:** `deferred`

Előfeltételek:

- Entity entry;
- activity mutation;
- attack legality;
- target/current kapcsolat;
- block és damage model.

### 7.5 Windows packaging prototype

**Státusz:** `deferred`

Vizsgálandó:

- Python runtime csomagolás;
- Godot kliens;
- runtime package;
- indítás;
- log és bug-report output.

---

## 8. A régi `PROTOTYPE_PLANS.md` helyes értelmezése

A `PROTOTYPE_PLANS.md`:

- megőrzendő hosszú történeti és jövőbeli referencia;
- dokumentálja a korai döntési bizonyítékokat;
- nem aktuális prioritási lista;
- több „következő prototípus” szakasza már elkészült;
- több GDScript-rules tervét felváltotta az authoritative Python-engine döntés;
- több statikus sample tervét felváltotta a működő minimal engine.

Aktuális task queue-ként ezt kell használni:

- v6.0 projektterv;
- `CURRENT_ENGINE_CHECKPOINT.md`;
- `CURRENT_OPEN_QUESTIONS.md`;
- jelen `CURRENT_PROTOTYPE_STATUS.md`.

---

## 9. Prototípus-munkarend

Minden új prototípus:

- egyetlen döntést vagy contractot bizonyítson;
- legyen kicsi;
- legyen visszafordítható;
- kapjon célzott tesztet;
- ne találjon ki szabályt;
- ne változtasson több schema-réteget egyszerre;
- ne keverjen dokumentációs cleanupot runtime implementációval;
- ne hozzon létre második authoritative szabálymotort;
- jelezze, mit nem bizonyít.

---

## 10. Rövid státusztábla

| Terület | Státusz |
|---|---|
| Python sample package generator | `completed_foundation` |
| Godot package loader | `promoted_to_active_system` |
| Sample contract loader | `completed_foundation` |
| Snapshot viewer | `completed_foundation` |
| Legal action debug panel | `completed_foundation` |
| Event log debug view | `completed_foundation` |
| Card reference resolver | `completed_foundation` |
| Contract consistency smoke | `completed_foundation` |
| Unified dashboard | `completed_foundation` |
| XLSX exporter migration | `promoted_to_active_system` |
| Runtime package publish | `promoted_to_active_system` |
| Minimal Python rules engine | `promoted_to_active_system` |
| Domain board | `promoted_to_active_system` |
| Structural Entity placement | `completed_foundation` |
| Activity state | `promoted_to_active_system` |
| Wellspring isolated contract | `completed_foundation` |
| Wellspring runtime integration | `active_next_step` |
| GDScript authoritative rules service | `superseded_by_architecture` |
| Python–GDScript rules comparison | `superseded_by_architecture` |
| Python–Godot transport | `deferred` |
| Godot player UI | `deferred` |
| Ability executor | `deferred` |
| Combat vertical slice | `deferred` |

---

## 11. Rövid összefoglaló

**Korai package/Godot prototípusok:** sikeresek  
**Azok eredménye:** aktív alaprétegek lettek  
**Authoritative rules engine:** Python  
**GDScript rules-engine prototípus:** felváltva  
**Aktuális közvetlen feladat:** Wellspring runtime integráció  
**Következő gameplay-lánc:** Wellspring → Beáramlás → Magnitúdó → Aura-payment → Entitás kijátszása
