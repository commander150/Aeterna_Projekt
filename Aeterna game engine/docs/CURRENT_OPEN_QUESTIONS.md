# AETERNA Game Engine – Current Open Questions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.4  
**Dátum:** 2026-07-15  
**Státusz:** aktív közeli döntési kapu-, OQ-triázs- és prioritáslista  
**Technikai referencia:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum a következő engine-, technológiai, termékruntime- és dokumentációs feladatokat közvetlenül befolyásoló kérdéseket tartalmazza.

Kapcsolódó források:

- teljes történeti kérdésregiszter: `OPEN_QUESTIONS.md`;
- részletes történeti válasz- és döntési irányok: `OPEN_QUESTIONS_DECISIONS.md`;
- termékruntime-mérce: `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`;
- runtime-nyelvi kapu: `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- tanulóprogram-audit sablon: `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`.

Az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó.

A két hosszú dokumentum eredeti kérdései és válaszai megmaradnak történeti nyilvántartásként. Ha a bennük szereplő régi státusz vagy megfogalmazás eltér ettől a current dokumentumtól, a jelen dokumentum aktuális OQ-triázsa az irányadó.

A Python minimal engine a jelenlegi működő referenciaimplementáció. A végleges authoritative termékruntime nyelve és futási modellje még nincs kiválasztva. A nyelvváltás nem önálló cél.

---

## 1. Státuszok

| Státusz | Jelentés |
|---|---|
| `answered` | Megválaszolva és aktív dokumentumba átvezetve. |
| `partly_answered` | Van elfogadott irány, de a végleges döntés még nyitott. |
| `highest_priority_decision_gate` | A következő Codex-munkasáv elsődleges döntési feladata. |
| `needs_learning_project_audit` | A helyi tanulóprogramok tényleges technológiai megoldásait kell felmérni. |
| `needs_comparison_fixture` | Közös, nyelvfüggetlen scenario és expected output szükséges. |
| `needs_integration_prototype` | Működő bridge- vagy runtime-proof szükséges. |
| `needs_packaging_proof` | Portable Windows-csomagolási és indítási bizonyíték szükséges. |
| `needs_source_check` | Hivatalos szabályforrásból pontosítani kell. |
| `needs_engine_design` | Technikai contract- vagy state-döntés kell. |
| `needs_visibility_decision` | Player-visible és hidden-information policy kell. |
| `queued_after_language_gate` | Kész vagy jól definiált feladat, de a runtime-nyelvi döntés után folytatandó. |
| `deferred_non_blocking` | Nyitott, de a következő auditot vagy proofot nem blokkolja. |

---

## 2. Az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` közös technológiai triázsa

### 2.1 Összefoglaló megfeleltetés

| Eredeti OQ | Aktuális státusz | Aktuális értelmezés |
|---|---|---|
| `OQ-ARCH-001` | `partly_answered` | A régi Python motor referencia/review. Az új Python minimal engine a működő comparison-reference. A végleges termékruntime nyitott. |
| `OQ-ARCH-002` | `highest_priority_decision_gate` | A régi Python–GDScript kérdés kibővült Python sidecar, Godot .NET/C#, GDScript és indokolt más jelöltek összehasonlítására. |
| `OQ-ARCH-003` | `answered` | A UI nem lehet szabályforrás. A frontend action requestet küld, az authoritative engine validál és transitiont hajt végre. |
| `OQ-TECH-001` | `partly_answered` | Python biztosan megmarad adatpipeline-, audit-, AI- és batch-toolingként. A termékruntime-szerepe proof után dönthető el. |
| `OQ-TECH-002` | `partly_answered` | A Godot loader/debug/UI szerepe bizonyított. A teljes GDScript rules runtime csak indokolt, szűk proof után értékelendő. |
| `OQ-TECH-003` | `highest_priority_decision_gate` | A comparison már nem csak Python–GDScript. A fő proof-jelöltek Python sidecar és Godot .NET/C#. |
| `OQ-TECH-004` | `answered` elvi szinten | A validált runtime package kötelező statikus programadat-contract. Nem azonos a MatchState-tel és nem dönt a runtime nyelvéről. |
| `OQ-TECH-005` | `partly_answered` | Godot headless smoke működik. A végleges CI-, warning- és portable exportpolicy későbbi technikai részlet. |
| `OQ-TECH-006` | `answered` munkarendi szinten | Codex szűk, explicit scope-ú, tesztelhető feladatokat kap. A következő feladat read-only audittal indul. |
| `OQ-AI-001` | `partly_answered` | A Python AI/batch tooling megtartandó akkor is, ha a termékruntime más nyelvű lesz. A végleges product runtime és AI-kapcsolat proof után dönthető el. |

### 2.2 Amit a korábbi válaszdokumentumból megtartunk

Továbbra is érvényes:

- contract-first fejlesztés;
- runtime package, action request/response, snapshot, legal action, event és diagnostics mint határfelületek;
- a régi Python motor nem törlendő automatikusan;
- a régi motorból logika csak célzott audit és új teszt után emelhető át;
- a Godot UI nem tartalmazhat rejtett szabálylogikát;
- két teljes authoritative motor tartós párhuzamos fenntartása kerülendő;
- a végleges technológiai döntéshez prototípus és összehasonlító teszt szükséges.

### 2.3 Amit a korábbi válaszdokumentumhoz hozzá kell érteni

A jelenlegi döntési kapu már nem szűkíthető Python és GDScript kettősére.

Kötelező fő proof-jelöltek:

1. Python sidecar engine + Godot kliens;
2. Godot .NET/C# authoritative runtime.

Feltételes jelöltek:

3. minimal GDScript rules proof;
4. C++ GDExtension vagy más nyelv, ha a tanulóprogram-audit erős indokot talál;
5. embedded Python, ha production-közeli stabilitás és packaging bizonyítható.

A Python leváltása nem cél. Csak akkor indokolt, ha:

- akadályozza a stabil portable Windows-futtatást;
- túl sok kézi runtime- vagy programtelepítést igényel;
- a Godot-integráció tartósan törékeny;
- a process lifecycle vagy hibakezelés nem tehető megbízhatóvá;
- vagy más megoldás bizonyítottan lényegesen jobb összeredményt ad.

---

## 3. Lezárt termékruntime-döntések

### CQ-PROD-001 – Elsődleges operációs rendszer

**Státusz:** `answered`

- 64 bites Windows 10 és minden ennél újabb támogatott Windows asztali rendszer;
- 32 bites Windows nem cél;
- Linux később vizsgálható, de nem blokkolja a 0.0.1 Windows-kiadást.

### CQ-PROD-002 – Jelenlegi kiadási forma

**Státusz:** `answered`

- proofhoz és zárt teszthez portable, kibontott mappa;
- jelenleg nem kell telepítő;
- egyértelmű fő executable szükséges;
- telepítő csak későbbi, véglegesebb vagy szélesebb kiadásnál kell.

### CQ-PROD-003 – Jogosultság

**Státusz:** `answered`

- normál futtatáshoz ne kelljen adminjog;
- a program saját portable mappájából induljon;
- mentések, beállítások, logok és hibacsomagok felhasználói írható mappába kerüljenek;
- futás közben ne írjon védett rendszerkönyvtárba.

### CQ-PROD-004 – Külső prerequisite-ek

**Státusz:** `answered`

- ne kelljen külön Pythont, Godot Editort, .NET SDK-t vagy más fejlesztői környezetet telepíteni;
- ne kelljen package-eket, modulokat vagy környezeti változókat kezelni;
- kevés számú, közismert és egyszerű prerequisite elfogadható;
- például szükséges .NET runtime vagy hasonló redistributable nem kizáró ok;
- self-contained csomagolás előny, de nem mindenáron kötelező.

### CQ-PROD-005 – Linux

**Státusz:** `deferred_non_blocking`

- később vizsgálható;
- jelenleg nem prioritás;
- előny, ha a választott technológia későbbi Linux-portja reális.

### CQ-PROD-006 – Csomagméret

**Státusz:** `deferred_non_blocking`

- nincs mesterséges felső limit a proof előtt;
- mérni kell a portable package méretét;
- a stabilitás és az egyszerű futtatás fontosabb a minimális méretnél.

### CQ-PROD-007 – Digitális kódaláírás

**Státusz:** `deferred_non_blocking`

- a zárt 0.0.1 proofot nem blokkolja;
- mérni kell az aláíratlan executable SmartScreen- és antivírus-viselkedését;
- szélesebb terjesztés előtt újraértékelendő.

### CQ-PROD-008 – Mentések és logok pontos Windows-helye

**Státusz:** `needs_engine_design`

Lezárt elv:

- felhasználói írható mappa;
- adminjog nélkül;
- ne a program portable mappája legyen az egyetlen kötelező adattár.

Később eldöntendő:

- `%APPDATA%`, `%LOCALAPPDATA%`, `Documents` vagy más hely;
- portable debug log engedélyezése;
- log retention és maximális méret;
- hibacsomag összeállítása.

### CQ-PROD-009 – Tanulóprogram-audit módszere

**Státusz:** `answered`

- egységes read-only audit;
- a helyi projektek nem kerülnek automatikusan az AETERNA GitHub repositoryba;
- verzió-, licenc-, dependency-, authority-, bridge-, packaging- és stabilitási leltár;
- közvetlen kódmásolás alapértelmezetten tilos;
- clean-room architektúraminta külön értékelhető;
- aktív sablon: `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`.

---

## 4. Aktuális architektúra- és technológiai kérdések

### CQ-ARCH-001 – Mi a jelenlegi engine-reference?

**Státusz:** `partly_answered`

Biztos:

- az új Python minimal engine a működő és tesztelt reference implementation;
- a Godot loader-, registry-, debug- és későbbi UI-réteg;
- a frontend nem módosít authoritative state-et;
- a legalitást engine-contract adja.

Nyitott:

- Python sidecar lesz-e a termékruntime;
- Godot .NET/C# lesz-e a termékruntime;
- szükséges-e GDScript vagy más proof;
- melyik modell teljesíti legjobban a portable Windows-termékkövetelményeket.

### CQ-ARCH-002 – Tanulóprogram-forrásaudit

**Státusz:** `needs_learning_project_audit`

Kötelező feladat:

- helyi projektek leltározása;
- vizsgált commit/tag/verzió;
- kód- és assetlicencek;
- nyelvek és runtime-ok;
- Godot-verzió;
- authoritative state helye;
- bridge és process lifecycle;
- packaging és Windows-támogatás;
- tesztek és stabilitási bizonyíték;
- clean-room módon használható minta.

### CQ-ARCH-003 – Közös comparison fixture

**Státusz:** `needs_comparison_fixture`

Kötelező közös scenario:

1. determinisztikus initial state;
2. `draw_card` P1;
3. `end_turn` P1 → P2;
4. `draw_card` P2;
5. player-visible snapshot P1;
6. player-visible snapshot P2;
7. typed event export;
8. stale `expected_state_version` rejection;
9. második azonos futás;
10. canonical JSON összevetés.

### CQ-ARCH-004 – Python sidecar proof

**Státusz:** `needs_integration_prototype`, `needs_packaging_proof`

Vizsgálandó:

- stdin/stdout JSONL és localhost TCP közül melyik az első proof;
- verziózott handshake;
- explicit action request/response;
- state/version guard;
- timeout és kapcsolatvesztés;
- kontrollált shutdown;
- stdout/protokoll és logcsatorna elhatárolása;
- adminjog nélküli portable Windows 10+ indítás;
- külön Python-telepítés nélküli csomag;
- elárvult processz és antivírus false positive kockázata.

### CQ-ARCH-005 – Godot .NET/C# proof

**Státusz:** `needs_integration_prototype`, `needs_packaging_proof`

Vizsgálandó:

- tiszta C# rules library vagy elkülönített assembly;
- UI-node-októl független MatchState és transitionök;
- azonos comparison scenario;
- kompatibilis JSON-contract;
- unit és integration tesztek;
- Godot .NET portable Windows 10+ export;
- self-contained vagy egyszerű .NET runtime prerequisite;
- adminjog nélküli futás;
- Python reference outputtal való differential comparison.

### CQ-ARCH-006 – GDScript és más nyelvek

**Státusz:** `deferred_non_blocking`

- minimal GDScript proof csak akkor, ha az audit vagy az első két proof indokolja;
- C++ GDExtension, Rust vagy más nyelv csak erős, bizonyított előny esetén kerül fő scope-ba;
- embedded Python jelenleg kutatási irány, nem első proof.

### CQ-ARCH-007 – UI és rules engine szétválasztása

**Státusz:** `answered`

- a UI nem szabályforrás;
- a frontend action requestet küld;
- az authoritative engine validál és mutál;
- player-facing output projectionből származik;
- ez minden nyelvi jelöltnél kötelező.

### CQ-ARCH-008 – Következő Codex-feladat

**Státusz:** `answered`

1. helyi tanulóprogramok read-only auditja;
2. közös comparison fixture;
3. minimal Python sidecar proof;
4. minimal Godot .NET/C# proof;
5. portable Windows- és stabilitási proof;
6. összehasonlító döntési jelentés;
7. csak szükség esetén GDScript vagy más proof.

### CQ-ARCH-009 – Következő gameplay-engine feladat

**Státusz:** `queued_after_language_gate`

- Wellspring production PlayerState- és MatchState-integráció;
- utána player-visible Wellspring summary;
- még nincs Beáramlás, payment vagy `play_card`.

---

## 5. Runtime package és AI – a nyelvi kaput befolyásoló döntések

### CQ-RUNTIME-001 – Runtime package szerepe

**Státusz:** `answered`

- kötelező validált statikus programadat-contract;
- Godot nem olvas közvetlenül XLSX-et;
- a builder/tooling Pythonban maradhat bármely termékruntime mellett;
- a runtime package nem MatchState és nem szabálymotor;
- schema és package identity véglegesítése külön későbbi feladat.

### CQ-AI-001 – Python AI/batch tooling jövője

**Státusz:** `partly_answered`

Biztos:

- a Python AI-, audit-, batch- és balansztooling megtartandó;
- a működő Python engine differential reference marad;
- fair AI nem kaphat több információt, mint a játékos;
- az AI nem mutálhat state-et közvetlenül.

Nyitott:

- a termékruntime ugyanazt az engine-t használja-e, mint a Python batch;
- sidecar, C# vagy más runtime esetén milyen adapter szükséges;
- hol fut a későbbi tanuló vagy nagyobb erőforrású AI.

---

## 6. Gameplay-kérdések a runtime-nyelvi döntés után

### CQ-WS-001 – Wellspring authoritative tagság

**Státusz:** `queued_after_language_gate`

- `wellspring_card_instance_ids` listás PlayerState-zóna;
- stabil serialization-sorrend;
- registry zone `wellspring`;
- activity `active` vagy `exhausted`;
- visibility `owner_only`;
- listás zóna és registry kétirányú invariáns.

### CQ-WS-002 – Owner/controller Wellspringben

**Státusz:** `needs_engine_design`

- közeli implementációban controller és player-zónatagság legyen irányadó;
- owner eltérhet;
- kontrollváltó gameplay még ne készüljön.

### CQ-WS-003 – Resource summary

**Státusz:** `answered`

- Magnitúdó és elérhető Aura származtatott érték;
- ne legyen külön authoritative `magnitude`, `spent_aura` vagy `remaining_aura` mező;
- summary a Wellspring-listából és activity state-ből készüljön.

### CQ-WS-004 – Wellspring visibility

**Státusz:** `needs_visibility_decision`

- ki látja a teljes Magnitúdót;
- ki látja az active/exhausted forrásszámot;
- saját játékos látja-e a face-down Card_ID-t;
- ellenfél csak countot lát-e;
- instance ID ne szivárogjon player-facing outputba.

### CQ-INFLOW-001 – Belépési activity state

**Státusz:** `needs_source_check`

- hivatalos szabályforrásból rögzíteni kell, hogy normál Beáramláskor Aktív vagy Kimerült állapotban érkezik-e a lap.

### CQ-INFLOW-002 – Timing és priority

**Státusz:** `needs_source_check`

- használható fázis;
- priority-követelmény;
- pontos fázispont;
- opcionális döntés kezelése;
- reakciózhatóság.

### CQ-INFLOW-003 – Körönkénti maximum

**Státusz:** `needs_engine_design`

- explicit per-turn state;
- ne event log visszakereséséből számoljuk.

### CQ-INFLOW-004 – Eventmodell

**Státusz:** `needs_engine_design`

- generic hand → wellspring `zone_move`;
- vagy külön `inflow` typed event.

### CQ-RES-001 – Magnitúdó-preflight

**Státusz:** `needs_engine_design`

- base Wellspring count;
- modifier és override nélkül az első verzióban;
- runtime Magnitúdó-mező;
- strukturált success/failure result.

### CQ-RES-002 – Typed Aura

**Státusz:** `needs_source_check`

- canonical Aura-típusok;
- Birodalmi és Aether/Semleges szerep;
- Entitás és nem-Entitás eltérő fizetése;
- runtime lookupértékek.

### CQ-RES-003 – Payment source selection

**Státusz:** `needs_engine_design`

- automatikus vagy kézi forrásválasztás;
- több azonos payment kezelése;
- külön payment action vagy play request payload;
- determinisztikus rendezés;
- atomikus kimerítés és rollback.

### CQ-RES-004 – Activity mutation event

**Státusz:** `needs_engine_design`

- önálló typed activity event;
- vagy payment/phase event payload.

---

## 7. Prioritási összefoglaló

### Lezárt Codex nélküli előkészítés

1. Termékruntime- és telepítési követelményspecifikáció.
2. Windows 10+ 64-bit cél.
3. Portable-first tesztmodell.
4. Adminjog nélküli futás.
5. Kevés közismert prerequisite elfogadási elve.
6. Tanulóprogram-audit és licencleltár-sablon.
7. Az eredeti Open Questions és Decisions technológiai OQ-inak közös current triázsa.

### Következő Codex-prioritás

1. Helyi tanulóprogramok read-only auditja és licencleltára.
2. Közös minimal comparison scenario és fixture.
3. Python sidecar + Godot proof.
4. Godot .NET/C# rules-runtime proof.
5. Portable Windows-, contract-, teszt-, packaging- és karbantarthatósági összevetés.
6. Szükség esetén minimal GDScript vagy más proof.
7. A/B/C döntési jelentés és emberi jóváhagyás.

### Codex nélküli következő munkasáv

1. Helyi tanulóprogram-leltár kitöltési sorrendje és auditbatch-ek.
2. Nyelvfüggetlen comparison fixture specifikáció.
3. Licenc- és attributionjegyzék szerkezete.
4. Ability module dokumentációs audit.
5. Contract-specifikáció konszolidációja.
6. Hivatalos szabályforrásból megválaszolható nyitott gameplay-kérdések ellenőrzése.

A Python engine megmarad működő referenciának. Jelentős új gameplay-réteg a nyelvi/runtime döntési kapu lezárása előtt ne induljon.
