# AETERNA Game Engine – Current Prototype Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2  
**Dátum:** 2026-07-15  
**Státusz:** aktív prototípus- és fejlesztési bizonyíték státusztérkép  
**Technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum azt rögzíti, hogy:

- mely prototípusok készültek el;
- melyek váltak aktív rendszeralappá;
- melyek a közvetlen következő implementációs feladatok;
- mely technológiai prototípusok maradtak nyitott vizsgálati kapuk;
- mit nem szabad bizonyítás nélkül lezártnak vagy elutasítottnak tekinteni.

Az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó.

A jelenlegi elsődleges technológiai proof terve:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

A Python engine működő referencia. A végleges termékruntime fő összehasonlítandó jelöltjei:

- Python sidecar + Godot;
- Godot .NET/C#;
- szükség esetén szűk GDScript proof.

---

## 1. Státuszjelölések

| Státusz | Jelentés |
|---|---|
| `completed_foundation` | A prototípus a célját bizonyította, alapként megtartandó. |
| `promoted_to_active_system` | A prototípusból aktív tooling-, runtime- vagy contract-réteg lett. |
| `highest_priority_next_proof` | A következő Codex-hozzáférés elsődleges prototípusfeladata. |
| `active_next_step` | Közvetlen vagy közeli programozási feladat. |
| `current_working_basis` | Jelenleg használt és bizonyított fejlesztési alap, de nem feltétlenül végleges termékarchitektúra. |
| `reference_oracle` | Összehasonlítási és regressziós referenciaimplementáció. |
| `pending_architecture_validation` | A végső döntéshez további technológiai bizonyítás kell. |
| `blocked_by_learning_project_audit` | Előbb a tanulóprogramok tényleges technológiai megoldásait kell átvizsgálni. |
| `blocked_by_comparison_design` | Előbb meg kell határozni, mit és milyen mélységben hasonlítunk össze. |
| `queued_after_language_gate` | A nyelvi/runtime döntési kapu után folytatandó. |
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

Ezek jelenleg debug- és kliensintegrációs alapok. A tényleges authoritative engine contractjai külön integrálandók a választott runtime-modell szerint.

---

## 4. Elkészült Python rules-engine alapok

A Python rules engine jelenlegi státusza:

- `current_working_basis`;
- `reference_oracle`;
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

A Python engine működése bizonyított. Ezért:

- nem törlendő;
- nem archiválandó;
- nem tekintendő elveszett munkának akkor sem, ha a végső runtime C# lesz;
- comparison fixture és expected output forrása;
- későbbi AI/batch és szabályregressziós orákulum lehet.

A jelenlegi Python engine azonban önmagában még nem bizonyítja a végleges Godot–Python termékarchitektúrát és packaginget.

---

## 5. Elsődleges következő technológiai proof

### 5.1 Runtime engine language comparison

**Státusz:** `highest_priority_next_proof`

Kötelező fő jelöltek:

1. Python sidecar + Godot kliens;
2. Godot .NET/C# authoritative runtime.

Opcionális harmadik jelölt:

3. minimal GDScript transition proof.

Részletes terv:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

Kötelező közös scenario:

- initial MatchState;
- `draw_card`;
- `end_turn`;
- második `draw_card`;
- player-visible snapshotok;
- typed event log;
- stale state version rejection;
- determinisztikus JSON ismétlés.

Kötelező összehasonlítás:

- contracthűség;
- tesztelhetőség;
- determinisztika;
- Godot-integráció;
- Windows packaging;
- hibatűrés;
- karbantarthatóság;
- Codex által készített kód minősége;
- portolási költség;
- AI/batch alkalmasság.

### 5.2 Python sidecar proof

**Státusz:** `highest_priority_next_proof`

Lehetséges első transport:

- stdin/stdout JSONL;
- vagy localhost TCP + JSON, ha a process pipe megoldás nem megfelelő.

Bizonyítandó:

- Godot és engine handshake;
- action request/response;
- snapshot és event átadás;
- process lifecycle;
- kontrollált shutdown;
- hibás version és kapcsolat kezelése;
- Windows csomagolás.

### 5.3 Godot .NET/C# rules proof

**Státusz:** `highest_priority_next_proof`

Bizonyítandó:

- UI-tól független C# rules library;
- ugyanazon scenario és contract;
- unit tesztek;
- Godot .NET fogyasztás;
- Windows build/export;
- Python outputtal való összevetés;
- state authority és hidden-information határ.

### 5.4 Minimal GDScript rules-service vizsgálat

**Státusz:**

- `pending_architecture_validation`;
- `blocked_by_learning_project_audit`;
- `not_active_parallel_engine_build`.

Nem elsődleges proof. Csak akkor készül, ha:

- az első két jelölt nem ad elég döntési információt;
- a tanulóprogram-audit konkrét GDScript előnyt talál;
- egyetlen transitionre korlátozható.

Nem tekintendő végleg obsolete vagy elutasított iránynak.

### 5.5 Embedded Python GDExtension

**Státusz:** `deferred`

Vizsgált közösségi irányok:

- py4godot;
- godot-python-extension;
- GodoPy;
- régi godot-python.

Jelenlegi minősítés:

- tanulásra és architektúra-vizsgálatra hasznos;
- több projekt experimental vagy WIP;
- első 0.0.1 proofnak magasabb kockázatú;
- később újraértékelhető.

### 5.6 Statikus action-response fixture

**Státusz:** `historical_reference`

Kliensparser- és comparison-fixture alapként továbbra is hasznos.

### 5.7 Ability registry support viewer

**Státusz:** `deferred`

Hasznos későbbi debug-eszköz, de az ability execution előtt nem kritikus út.

---

## 6. Tanulóprogram-audit

**Státusz:**

- `active_documentation_and_research_gate`;
- a következő Codex proof előfeltétele.

A tanulóprogramok nincsenek az AETERNA GitHub repositoryban licencbiztonsági okból.

A Codex később helyileg vizsgálja:

- mely programok használják a Pythont engine-ként;
- melyek kapcsolják össze a Pythont Godottal;
- melyek használnak C#/.NET runtime-ot;
- melyek csak UI- vagy contractminták;
- ki indít melyik processt;
- hol található az authoritative state;
- milyen transportot és packaginget használnak;
- milyen licenc- és attributionkötelezettségük van.

A repositoryban biztosan megtalálható összefoglaló:

- `AETERNA – tanulóprojektekből kinyert legfontosabb fejlesztési irányok.md`

Kiemelt online referenciák:

- Godot RL Agents;
- py4godot;
- godot-python-extension;
- GodoPy;
- régi godot-python.

Másolt kód alapértelmezetten ne kerüljön az AETERNA repositoryba. Elsődleges cél az architektúra- és működésminta clean-room elemzése.

---

## 7. Gameplay-engine implementációs queue

A következő gameplay-lánc továbbra is érvényes, de a runtime-nyelvi döntési kapu mögé került:

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

Státusz:

- `queued_after_language_gate`

A Wellspring feladat nem törlődött és nem vált hibássá. A választott runtime-ágon folytatandó.

---

## 8. Codex nélküli aktív munkasáv

1. `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` közös triázsa.
2. Tanulóprogram-forrás- és licencleltár előkészítése.
3. A runtime language comparison kritériumainak pontosítása.
4. `ABILITY_MODULE_SYSTEM.md` auditja.
5. A hosszú contract-specifikáció konszolidációja.
6. Hivatalos szabályforrásból megválaszolható engine-kérdések ellenőrzése.
7. Dokumentációs státuszok és hivatkozások karbantartása.

---

## 9. Amit jelenleg nem állítunk

Nem állítjuk, hogy:

- a Python sidecar biztosan a végleges megoldás;
- a C# biztosan jobb minden szempontból;
- a GDScript biztosan alkalmatlan;
- embedded Python biztosan használhatatlan;
- a jelenlegi Python engine-t el kell dobni;
- két teljes rules engine-t párhuzamosan fel kell építeni;
- a Godot–Python együttműködés packaging és teljesítmény szempontjából már teljesen bizonyított.

Jelenleg azt állítjuk, hogy:

- a Python minimal engine működő referencia;
- a Godot kliens- és loaderalap működik;
- a C# hivatalosan támogatott és komolyan vizsgálandó jelölt;
- a Python sidecar technikailag működőképes modell;
- a végleges runtime-technológia összehasonlító proofot igényel;
- ezt a döntést a teljes gameplay-engine előtt kell meghozni.
