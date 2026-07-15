# AETERNA Game Engine – Current Prototype Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív prototípus- és fejlesztési bizonyíték státusztérkép  
**Technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum azt rögzíti, hogy:

- mely prototípusok készültek el;
- melyek váltak aktív rendszeralappá;
- melyek a közvetlen következő implementációs feladatok;
- mely technológiai prototípusok maradtak nyitott vizsgálati kapuk;
- mit nem szabad bizonyítás nélkül lezártnak vagy elutasítottnak tekinteni.

Az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó. Az utóbbi szerint a Python backend + Godot frontend erős hosszú távú jelölt, de a végleges runtime/backend döntéshez további prototípus és összehasonlító teszt szükséges.

---

## 1. Státuszjelölések

| Státusz | Jelentés |
|---|---|
| `completed_foundation` | A prototípus a célját bizonyította, alapként megtartandó. |
| `promoted_to_active_system` | A prototípusból aktív tooling-, runtime- vagy contract-réteg lett. |
| `active_next_step` | Közvetlen vagy közeli programozási feladat. |
| `current_working_basis` | Jelenleg használt és bizonyított fejlesztési alap, de nem feltétlenül végleges termékarchitektúra. |
| `pending_architecture_validation` | A végső döntéshez további technológiai bizonyítás kell. |
| `blocked_by_learning_project_audit` | Előbb a tanulóprogramok tényleges technológiai megoldásait kell átvizsgálni. |
| `blocked_by_comparison_design` | Előbb meg kell határozni, mit és milyen mélységben hasonlítunk össze. |
| `deferred` | Későbbi roadmap-szakaszra halasztott. |
| `historical_reference` | Történeti bizonyíték, de nem aktuális task queue. |
| `not_started` | Még nincs implementálva. |

---

## 2. A korai prototípus-szakasz eredménye

A runtime package–Godot alapozási szakasz bizonyította:

- Python runtime package build;
- valós kártya- és deckadatok feldolgozása;
- Godot package loader és registry;
- snapshot, legal action és event debug fixture-ek betöltése;
- card reference resolution;
- contract consistency smoke;
- unified debug dashboard;
- XLSX exporter migráció;
- candidate publish pipeline;
- Godot consumption copy.

Ez a szakasz elkészült alapozási mérföldkő, és nem lett eldobva.

---

## 3. Elkészült Godot- és adatpipeline-prototípusok

### 3.1 Runtime package generator és publish pipeline

**Státusz:** `promoted_to_active_system`

Bizonyított:

- package build;
- manifest és többfájlos package;
- cards/decks/lookups/aliases/diagnostics;
- candidate validation;
- Godot consumption copy frissítés;
- valós adatméret kezelése.

### 3.2 Godot runtime package loader

**Státusz:** `promoted_to_active_system`

Bizonyított:

- package betöltése;
- card/deck/lookup registry;
- ability és diagnostics adat olvasása;
- headless smoke.

Aktív consumption path:

- `res://runtime_package`

### 3.3 Sample contract loader és debug nézetek

**Státusz:** `completed_foundation`

Ide tartozik:

- sample snapshot;
- sample legal action;
- sample event log;
- snapshot viewer;
- legal action debug panel;
- event log debug view;
- unified dashboard;
- card reference resolver;
- consistency smoke.

Ezek jelenleg debug- és kliensintegrációs alapok. A Python minimal engine aktuális contractjai később külön integrálandók.

---

## 4. Elkészült Python rules-engine alapok

A Python rules engine jelenlegi státusza:

- `current_working_basis`;
- több rétege `promoted_to_active_system`.

Elkészült:

- MatchState és PlayerState;
- session és environment;
- expected state version guard;
- card instance registry;
- draw transition;
- end-turn transition;
- generic typed event envelope;
- `zone_move` és `turn_transition` event;
- player-visible snapshot v2;
- hidden-information redakció;
- AI episode trajectory;
- Domain topology;
- Domain occupancy;
- public board projection;
- structural Entity placement options;
- card instance activity state;
- izolált Wellspring state és resource summary.

A Python engine működése bizonyított. Ez indokolja, hogy a következő szabálymotoros feladatokat továbbra is ezen a bázison végezzük.

Ez azonban önmagában még nem bizonyítja a végleges Godot–Python termékarchitektúrát és packaginget.

---

## 5. Technológiai prototípusok helyes státusza

### 5.1 Minimal GDScript rules-service vizsgálat

**Státusz:**

- `pending_architecture_validation`;
- `blocked_by_learning_project_audit`;
- `not_active_parallel_engine_build`.

Nem közvetlen programozási prioritás, mert:

- a Python engine már jelentős működő állapotban van;
- két teljes motor párhuzamos fejlesztése nagy duplikációs kockázat;
- előbb meg kell vizsgálni, milyen technológiai bizonyítékra van ténylegesen szükség.

Nem tekintendő végleg obsolete vagy elutasított iránynak.

A későbbi vizsgálat lehet kisebb, célzott GDScript proof-of-concept, nem szükségképpen teljes második engine.

### 5.2 Python–GDScript comparison scenario

**Státusz:**

- `blocked_by_learning_project_audit`;
- `blocked_by_comparison_design`;
- `pending_architecture_validation`.

A comparison kérdés továbbra is aktív döntési kapu.

A vizsgálat lehetséges formái:

- Python engine output Godot parser round-trip;
- azonos snapshot és action-response contract kezelése;
- egy minimal transition GDScript proof-of-concept;
- Python child process vagy service bridge;
- teljesítmény- és hibakezelési mérés;
- Windows packaging proof;
- működő tanulóprogram Python–Godot mintájának reprodukálása.

Nem szükséges előre kijelenteni, hogy két teljes authoritative engine készül.

### 5.3 Statikus action-response fixture

**Státusz:** `historical_reference`

Kliensparser- és Godot-integrációs teszthez továbbra is hasznos lehet.

### 5.4 Ability registry support viewer

**Státusz:** `deferred`

Hasznos későbbi debug-eszköz, de az ability execution előtt nem kritikus út.

---

## 6. Tanulóprogram-audit

**Státusz:** `active_documentation_and_research_gate`

A jelenlegi repositoryban biztosan megtalálható összefoglaló:

- `AETERNA – tanulóprojektekből kinyert legfontosabb fejlesztési irányok.md`

Ez a dokumentum többek között a következő referenciákat említi:

- Mage / XMage;
- Duelyst;
- RLCard;
- boardgame.io;
- több Godot kártyajáték- és UI-projekt.

A GitHub jelenlegi keresésében ezek teljes forrásfái nem azonosíthatók egyértelműen a repository részeként. Ezért külön leltár szükséges:

- mely tanulóprojektek vannak ténylegesen feltöltve;
- melyek külső referenciák;
- melyek használnak Python engine-t;
- melyek kapcsolják össze a Pythont Godottal;
- melyek csak UI- vagy contractminták;
- melyekből érdemes clean-room prototípust készíteni.

Az audit nélkül a végleges Python–Godot/GDScript runtime-döntés nem zárható le.

---

## 7. Aktív következő engine-implementációs lánc

A jelenlegi Python engine-alap fejlesztése továbbra is folytatható:

1. Wellspring PlayerState- és MatchState-integráció.
2. Player-visible Wellspring summary.
3. Beáramlás precondition.
4. Beáramlás transition és typed event.
5. Magnitúdó-preflight.
6. Aura-source és payment contract.
7. Activity mutation transition.
8. Entitás kijátszási precondition.
9. `play_card` action.
10. Hand → Domain transition.
11. Entry-state.
12. Teljesebb phase és priority rendszer.

Ez a lánc nem függ attól, hogy a végleges Godot–Python bridge pontosan milyen lesz.

---

## 8. Párhuzamos technológiai bizonyítási lánc

1. `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` közös triázsa.
2. Tanulóprogram-forrásleltár.
3. Python-engine/Godot minták azonosítása.
4. Comparison scope kialakítása.
5. Minimal Python–Godot bridge prototype.
6. Szükség esetén célzott GDScript transition proof.
7. Windows packaging prototype.
8. Végleges termékarchitektúra döntési kapu.

---

## 9. Amit jelenleg nem állítunk

Nem állítjuk, hogy:

- a végleges AETERNA termékarchitektúra már visszavonhatatlanul lezárult;
- GDScript biztosan alkalmatlan rules runtime-ra;
- a Python–GDScript comparison felesleges;
- két teljes rules engine-t most párhuzamosan fel kell építeni;
- a Godot–Python együttműködés packaging és teljesítmény szempontjából már bizonyított.

Jelenleg azt állítjuk, hogy:

- a Python minimal engine működő és legerősebb fejlesztési bázis;
- a Godot kliens- és loaderalap működik;
- a végleges összekapcsolás és runtime-technológia további bizonyítást igényel.
