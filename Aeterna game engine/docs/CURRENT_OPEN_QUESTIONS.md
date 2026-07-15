# AETERNA Game Engine – Current Open Questions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.3  
**Dátum:** 2026-07-15  
**Státusz:** aktív közeli döntési kapu- és kérdéslista  
**Technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum a következő engine-, technológiai, termékruntime- és dokumentációs feladatokat közvetlenül befolyásoló kérdéseket tartalmazza.

Kapcsolódó források:

- teljes történeti kérdésregiszter: `OPEN_QUESTIONS.md`;
- részletes válasz- és döntési irányok: `OPEN_QUESTIONS_DECISIONS.md`;
- termékruntime-mérce: `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`;
- runtime-nyelvi kapu: `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- tanulóprogram-audit sablon: `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`.

Az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó.

A Python minimal engine a jelenlegi működő referenciaimplementáció. A végleges authoritative termékruntime nyelve és futási modellje még nincs kiválasztva. A nyelvváltás nem önálló cél.

---

## 1. Státuszok

| Státusz | Jelentés |
|---|---|
| `ready_for_implementation` | A szükséges irány már eldöntött, implementálható. |
| `partly_answered` | Van működő irány, de a végleges döntés még nyitott. |
| `highest_priority_decision_gate` | A következő kódoló/Codex munkasáv elsődleges döntési feladata. |
| `needs_source_check` | Hivatalos szabályforrásból pontosítani kell. |
| `needs_engine_design` | Technikai contract- vagy state-döntés kell. |
| `needs_visibility_decision` | Player-visible és hidden-information policy kell. |
| `needs_learning_project_audit` | A tanulóprogramok tényleges technológiai megoldásait kell felmérni. |
| `needs_comparison_design` | Meg kell határozni az összehasonlító prototípus pontos célját. |
| `needs_integration_prototype` | Működő bridge/runtime proof szükséges. |
| `queued_after_language_gate` | Kész vagy jól definiált feladat, de a runtime-nyelvi döntés után folytatandó. |
| `deferred_non_blocking` | Nyitott, de a következő auditot vagy proofot nem blokkolja. |
| `answered` | Megválaszolva és aktív dokumentumba átvezetve. |

---

## 2. Termékruntime és telepítés

### CQ-PROD-001 – Mely Windows-rendszerek az elsődleges célok?

**Státusz:** `answered`

Döntés:

- 64 bites Windows 10 és minden ennél újabb támogatott Windows asztali rendszer;
- 32 bites Windows nem cél;
- a proofokat legalább Windows 10+ 64-bit környezetben kell ellenőrizni.

### CQ-PROD-002 – Portable vagy telepítő?

**Státusz:** `answered`

Döntés:

- a jelenlegi proof- és zárt tesztfázisban portable, kibontott mappa készül;
- jelenleg nem kell telepítő;
- a portable csomag egyértelmű fő executable-ből induljon;
- telepítő csak későbbi véglegesebb vagy szélesebb kiadáshoz szükséges.

### CQ-PROD-003 – Kellhet-e adminisztrátori jogosultság?

**Státusz:** `answered`

Döntés:

- normál futtatáshoz nem kellhet adminjog;
- a program saját portable mappájából induljon;
- mentések, beállítások és logok felhasználói írható mappába kerüljenek;
- a program ne írjon futás közben védett rendszerkönyvtárba.

### CQ-PROD-004 – Milyen külső komponensek fogadhatók el?

**Státusz:** `answered`

Döntés:

- a játékosnak ne kelljen külön Pythont, Godot Editort, .NET SDK-t vagy más fejlesztői környezetet telepítenie;
- ne kelljen package-eket, modulokat vagy környezeti változókat kezelnie;
- kevés számú, közismert és egyszerű prerequisite elfogadható;
- például szükséges .NET runtime vagy hasonló redistributable nem kizáró ok;
- self-contained csomagolás előny, de nem mindenáron kötelező.

### CQ-PROD-005 – Linux-támogatás

**Státusz:** `deferred_non_blocking`

Döntési irány:

- később vizsgálható;
- jelenleg nem prioritás;
- nem blokkolja a 0.0.1 Windows-runtime kiválasztását;
- előny, ha a választott technológia későbbi Linux-portja reális.

### CQ-PROD-006 – Maximális csomagméret

**Státusz:** `deferred_non_blocking`

Még mérendő:

- portable package mérete;
- beágyazott runtime mérete;
- C# self-contained és Python sidecar különbsége;
- a méret arányban áll-e a stabilitási és telepítési előnnyel.

Jelenleg nincs mesterséges felső limit. A méret önmagában nem fontosabb a stabilitásnál és az egyszerű futtatásnál.

### CQ-PROD-007 – Digitális kódaláírás

**Státusz:** `deferred_non_blocking`

Nyitott:

- kell-e a zárt 0.0.1 tesztcsomaghoz;
- mennyire okoz az aláíratlan executable antivírus vagy SmartScreen problémát;
- mikor válik szükségessé szélesebb terjesztésnél.

### CQ-PROD-008 – Mentések, logok és hibacsomagok pontos helye

**Státusz:** `needs_engine_design`

Lezárt elv:

- felhasználói írható mappába kerüljenek;
- ne igényeljenek adminjogot;
- ne a program portable mappája legyen az egyetlen kötelező adattár.

Később pontosítandó:

- `%APPDATA%`, `%LOCALAPPDATA%`, `Documents` vagy más Windows-hely;
- portable debug módban engedélyezett-e külön lokális log;
- log retention és maximális méret;
- hibacsomag összeállítása.

### CQ-PROD-009 – Tanulóprogram-audit módszere

**Státusz:** `answered`

Döntés:

- egységes read-only sablon készül;
- a helyi projektek nem kerülnek automatikusan az AETERNA GitHub repositoryba;
- minden projektnél verzió-, licenc-, dependency-, authority-, bridge-, packaging- és stabilitási leltár kell;
- közvetlen kódmásolás alapértelmezetten tilos;
- clean-room architektúraminta külön értékelhető.

Aktív sablon:

- `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`

---

## 3. Architektúra és technológia

### CQ-ARCH-001 – Mi a jelenlegi authoritative engine?

**Státusz:** `partly_answered`

Biztos jelenlegi válasz:

- az aktívan fejlesztett és tesztelt authoritative referenciaimplementáció a Python minimal engine;
- a Godot jelenleg loader-, registry-, debug- és későbbi UI-réteg;
- a frontend nem módosíthat közvetlenül state-et;
- a legalitást engine-contract adja.

Nyitott hosszú távú rész:

- külön Python backend/sidecar fut-e a Godot kliens mellett;
- Godot .NET/C# lesz-e az authoritative termékruntime;
- szükséges-e részleges vagy teljes GDScript rules runtime;
- beágyazott Pythonnak van-e elfogadható szerepe;
- más nyelv vagy GDExtension-modell ad-e lényegesen jobb eredményt;
- milyen packaging és process modell teljesíti a termékkövetelményeket.

Kapcsolódó eredeti kérdések:

- `OQ-ARCH-001`
- `OQ-ARCH-002`
- `OQ-TECH-001`
- `OQ-TECH-002`
- `OQ-TECH-003`

### CQ-ARCH-002 – Tanulóprogram-forrásaudit

**Státusz:** `needs_learning_project_audit`

Feladat:

- leltározni a felhasználó által helyileg letöltött tanulóprogramokat;
- elkülöníteni a helyi forrásokat a külső referenciáktól;
- projektenként ellenőrizni a licencet és a vizsgált verziót;
- azonosítani, használ-e valamelyik Godot kliens Python engine-t;
- azonosítani, mely projektek használnak C#/.NET, GDScript, C++, Rust vagy más runtime-ot;
- dokumentálni a bridge-, state-authority-, teszt- és packaging mintát;
- megállapítani, mely projekt releváns rules engine, UI, AI vagy kiadási csomagolás szempontjából.

A tanulóprogramok szándékosan nincsenek az AETERNA GitHub repositoryban. A Codex később helyileg vizsgálja őket.

Jelenlegi online referenciák többek között:

- Godot RL Agents;
- py4godot;
- godot-python-extension;
- GodoPy;
- régi godot-python.

### CQ-ARCH-003 – Python–C#–GDScript és más jelöltek összehasonlítási scope-ja

**Státusz:** `highest_priority_decision_gate`

A comparison kérdés nem lezárt és nem obsolete.

Kötelező első fő jelöltek:

1. Python sidecar + Godot kliens;
2. Godot .NET/C# authoritative runtime.

Feltételes jelöltek:

3. minimal GDScript transition proof;
4. C++ GDExtension vagy más nyelv, ha az audit erős indokot talál;
5. embedded Python, ha production-közeli packaging bizonyítható.

Eldöntendő:

- pontos közös minimal scenario;
- azonos contractok vagy explicit mapping;
- Python sidecar kommunikációs módja;
- C# rules library és Godot UI elhatárolása;
- Windows 10+ 64-bit portable indítás;
- prerequisite-ek száma és kezelése;
- teljesítmény, latency és processhiba;
- unit és integration tesztelhetőség;
- Codex által előállított kód minősége;
- emberi karbantarthatóság;
- portolási költség;
- AI-vs-AI és batch futtatás helye.

Nem cél:

- két teljes engine párhuzamos felépítése;
- teljes Python → C# port a döntés előtt;
- teljes GDScript motor;
- nyelvválasztás pusztán vélemény alapján.

Részletes scope:

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

### CQ-ARCH-004 – Python–Godot sidecar integráció

**Státusz:** `needs_integration_prototype`

Elsőként vizsgálandó alternatívák:

- child process + stdin/stdout JSONL;
- localhost TCP + JSON;
- csomagolt Python sidecar.

Kötelező elvek:

- explicit handshake;
- explicit action request;
- state/version guard;
- atomikus mutation;
- player-visible response;
- debug információ elkülönítése;
- kontrollált process- és kapcsolatkezelés;
- stdout/protokoll és logcsatorna elhatárolása;
- deterministic request/response napló;
- adminjog nélküli portable indítás;
- ne kelljen külön Pythont telepíteni.

### CQ-ARCH-005 – Godot .NET/C# runtime proof

**Státusz:** `needs_integration_prototype`

Vizsgálandó:

- tiszta C# rules library vagy elkülönített assembly;
- MatchState és transitionök UI-node-októl függetlenül;
- ugyanazon minimal scenario;
- kompatibilis JSON-contract;
- unit tesztek;
- Godot .NET indítás;
- Windows 10+ 64-bit portable export;
- build- és dependencykezelés;
- self-contained vagy egyszerű .NET runtime prerequisite;
- adminjog nélküli futás;
- a Python reference outputtal való összevetés.

### CQ-ARCH-006 – Embedded Python Godotban

**Státusz:** `deferred_non_blocking`

Jelenlegi kutatási állapot:

- több közösségi GDExtension/binding létezik;
- több projekt aktív vagy fejlődő;
- több projekt saját dokumentációja experimental/WIP státuszt jelez;
- jelenleg nem ez az első AETERNA proof.

Újraértékelhető, ha:

- valamely tanulóprogram production-közeli működő mintát mutat;
- a sidecar vagy C# megoldás súlyos problémába ütközik;
- Windows packaging és Godot-verzió kompatibilitás bizonyítható.

### CQ-ARCH-007 – Módosíthatja-e a frontend közvetlenül a state-et?

**Státusz:** `answered`

Döntés:

- nem;
- a frontend vagy AI action requestet küld;
- az authoritative engine validál és transitiont hajt végre;
- player-facing output projectionből származik.

Ez minden nyelvi jelöltnél kötelező.

### CQ-ARCH-008 – Mi a következő közvetlen Codex-feladat?

**Státusz:** `answered`

Döntés:

- tanulóprogramok read-only auditja és licencleltára;
- közös comparison fixture;
- minimal Python sidecar proof;
- minimal Godot .NET/C# proof;
- portable Windows- és stabilitási proof;
- összehasonlító döntési jelentés;
- csak szükség esetén minimal GDScript vagy más proof.

### CQ-ARCH-009 – Mi a következő gameplay-engine feladat?

**Státusz:** `queued_after_language_gate`

Feladat:

- az izolált Wellspring contract production PlayerState- és MatchState-integrációja;
- még nincs Inflow, payment vagy `play_card`.

Ez a feladat nem törlődött. A runtime-nyelvi döntési kapu után azon az engine-ágon folytatandó, amelyet a felhasználó jóváhagy.

---

## 4. Wellspring runtime integráció

### CQ-WS-001 – PlayerState mező és authoritative tagság

**Státusz:** `queued_after_language_gate`

Javasolt contract:

- új PlayerState mező: `wellspring_card_instance_ids`;
- listás authoritative zóna;
- sorrend a serialization és `zone_index` miatt stabil;
- gameplay-sorrend jelentősége jelenleg nincs.

Elfogadási feltételek:

- minden production player üres listával indul;
- minden Wellspring instance pontosan egy player listájában szerepel;
- nem szerepelhet másik listás zónában vagy Domain occupancyben;
- registry zone `wellspring`;
- zone index egyezik;
- activity active vagy exhausted;
- visibility `owner_only`;
- controller a Wellspring játékosa.

### CQ-WS-002 – Owner és controller Wellspringben

**Státusz:** `needs_engine_design`

Jelenlegi technikai konvenció:

- a zónához való tartozást a controller és a player listája jelöli;
- owner eltérhet.

Közeli implementációban:

- owner-egyezést ne követeljünk;
- kontrollváltó gameplay ne készüljön.

Később tisztázandó:

- kerülhet-e kontrollált, de nem tulajdonolt kártya Ősforrásba;
- milyen ownership helyreállítás kell zónaelhagyáskor.

### CQ-WS-003 – Resource summary tárolás vagy számítás

**Státusz:** `answered`

Döntés:

- Magnitúdó és elérhető Aura származtatott érték;
- ne legyen külön authoritative `magnitude`, `spent_aura` vagy `remaining_aura` state;
- summary mindig a Wellspring listából és activity state-ből készüljön.

### CQ-WS-004 – Player-visible Wellspring policy

**Státusz:** `needs_visibility_decision`

Kérdések:

- mindkét játékos látja-e a teljes Magnitúdót;
- mindkét játékos látja-e az Aktív/Kimerült források számát;
- a saját játékos látja-e a Wellspring Card_ID-kat;
- az ellenfél csak countot lát-e;
- instance ID soha ne szivárogjon-e player-facing outputba;
- a face-down források saját játékos számára is rejtett Card_ID-júak-e.

---

## 5. Beáramlás

### CQ-INFLOW-001 – Belépési activity state

**Státusz:** `needs_source_check`

Kérdés:

- a normál Beáramlással Ősforrásba helyezett lap Aktív vagy Kimerült állapotban érkezik-e.

Nem szabad hallgatólagos defaulttal implementálni.

### CQ-INFLOW-002 – Pontos timing és priority

**Státusz:** `needs_source_check`

Rögzítendő:

- mely fázisban használható;
- a játékosnak kell-e priority;
- automatikusan felkínált opcionális döntés-e;
- a fázis mely pontján történik;
- reakciózható-e.

### CQ-INFLOW-003 – Körönkénti maximum nyilvántartása

**Státusz:** `needs_engine_design`

Hivatalos alap:

- normál Beáramlás körönként legfeljebb egyszer.

Javasolt technikai irány:

- explicit, könnyen validálható per-turn state;
- ne event log visszakereséséből kelljen számolni.

### CQ-INFLOW-004 – Eventmodell

**Státusz:** `needs_engine_design`

Kérdés:

- elegendő-e a generic `zone_move` event hand → wellspring adatokkal;
- vagy készüljön külön `inflow` typed event is.

---

## 6. Magnitúdó és Aura

### CQ-RES-001 – Magnitúdó-preflight contract

**Státusz:** `needs_engine_design`

Első verzió:

- base Wellspring count;
- override és modifier nélkül;
- exact runtime Magnitúdó-mezőből;
- strukturált success/failure resulttal.

### CQ-RES-002 – Typed Aura canonical modell

**Státusz:** `needs_source_check`

Rögzítendő:

- Aura canonical típusai;
- Birodalmi Aura és Aether/Semleges szerepe;
- Entitás és nem-Entitás eltérő fizetési szabályai;
- pontos runtime lookupértékek.

### CQ-RES-003 – Payment source selection

**Státusz:** `needs_engine_design`

Kérdések:

- automatikus vagy kézi forrásválasztás;
- több azonos eredményű payment közül kell-e választás;
- payment request külön action vagy a play request része;
- determinisztikus rendezés;
- atomikus kimerítés és rollback.

### CQ-RES-004 – Activity mutation event

**Státusz:** `needs_engine_design`

Kérdés:

- a Kimerítés/Visszaállítás önálló typed event legyen-e;
- vagy a fizetési és fázistransition event payloadjába kerüljön.

---

## 7. Prioritási összefoglaló

### Lezárt Codex nélküli előkészítés

1. Termékruntime- és telepítési követelményspecifikáció.
2. Windows 10+ 64-bit cél.
3. Portable-first tesztmodell.
4. Adminjog nélküli futás.
5. Kevés közismert prerequisite elfogadási elve.
6. Tanulóprogram-audit és licencleltár-sablon.

### Következő Codex-prioritás

1. Helyi tanulóprogramok read-only auditja és licencleltára.
2. Közös minimal comparison scenario és fixture.
3. Python sidecar + Godot proof.
4. Godot .NET/C# rules-runtime proof.
5. Portable Windows-, contract-, teszt-, packaging- és karbantarthatósági összevetés.
6. Szükség esetén minimal GDScript vagy más proof.
7. A/B/C döntési jelentés és emberi jóváhagyás.

### Gameplay-engine queue a döntés után

1. Wellspring runtime integráció.
2. Player-visible Wellspring summary.
3. Beáramlás.
4. Magnitúdó és payment.
5. Első `play_card`.

### Codex nélküli aktív munkasáv

1. `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` technológiai OQ-triázsa.
2. Helyi tanulóprogram-leltár kitöltési sorrendje és auditbatch-ek.
3. Nyelvfüggetlen comparison fixture specifikáció.
4. Ability module dokumentációs audit.
5. Contract-specifikáció konszolidációja.
6. Hivatalos szabályforrásból megválaszolható nyitott kérdések ellenőrzése.

A Python engine megmarad működő referenciának. Jelentős új gameplay-réteg a nyelvi/runtime döntési kapu lezárása előtt ne induljon.
