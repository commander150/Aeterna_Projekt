# AETERNA Game Engine – Current Open Questions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív közeli döntési kapu- és kérdéslista  
**Technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum a következő engine-, technológiai és dokumentációs feladatokat közvetlenül befolyásoló kérdéseket tartalmazza.

A teljes történeti kérdésregiszter:

- `OPEN_QUESTIONS.md`

A kérdésekhez tartozó részletes válasz- és döntési irányok:

- `OPEN_QUESTIONS_DECISIONS.md`

A két dokumentum együtt olvasandó. A válaszdokumentum szerint a Python backend + Godot frontend erős hosszú távú jelölt, de a végleges runtime/backend döntéshez további prototípus és összehasonlító vizsgálat szükséges.

---

## 1. Státuszok

| Státusz | Jelentés |
|---|---|
| `ready_for_implementation` | A szükséges irány már eldöntött, implementálható. |
| `partly_answered` | Van működő irány, de a végleges döntés még nyitott. |
| `needs_source_check` | Hivatalos szabályforrásból pontosítani kell. |
| `needs_engine_design` | Technikai contract- vagy state-döntés kell. |
| `needs_visibility_decision` | Player-visible és hidden-information policy kell. |
| `needs_learning_project_audit` | A tanulóprogramok tényleges technológiai megoldásait kell felmérni. |
| `needs_comparison_design` | Meg kell határozni az összehasonlító prototípus pontos célját. |
| `needs_integration_prototype` | Működő Python–Godot vagy más bridge proof szükséges. |
| `deferred` | Későbbi roadmap-szakaszra halasztva. |
| `answered` | Megválaszolva és aktív dokumentumba átvezetve. |

---

## 2. Architektúra és technológia

### CQ-ARCH-001 – Mi a jelenlegi authoritative engine?

**Státusz:** `partly_answered`

Biztos jelenlegi válasz:

- az aktívan fejlesztett és tesztelt authoritative implementáció a Python minimal engine;
- a Godot jelenleg loader-, registry-, debug- és későbbi UI-réteg;
- a frontend nem módosíthat közvetlenül state-et;
- a legalitást engine-contract adja.

Nyitott hosszú távú rész:

- a végleges termékben külön Python backend fut-e a Godot kliens mellett;
- beágyazott vagy sidecar Python runtime készül-e;
- szükséges-e részleges vagy teljes GDScript rules runtime;
- milyen packaging és process modell lesz használható.

Kapcsolódó eredeti kérdések:

- `OQ-ARCH-001`
- `OQ-ARCH-002`
- `OQ-TECH-001`
- `OQ-TECH-002`
- `OQ-TECH-003`

### CQ-ARCH-002 – Tanulóprogram-forrásaudit

**Státusz:** `needs_learning_project_audit`

Feladat:

- leltározni a ténylegesen elérhető tanulóprogramokat;
- elkülöníteni a repositoryban lévő forrásokat a külső referenciáktól;
- azonosítani, használ-e valamelyik Godot kliens Python engine-t;
- dokumentálni a bridge-, state-authority- és packaging mintát;
- megállapítani, mely projekt releváns rules engine, UI vagy AI szempontból.

Jelenlegi biztosan elérhető összefoglaló:

- `AETERNA – tanulóprojektekből kinyert legfontosabb fejlesztési irányok.md`

A jelenlegi GitHub-keresésben a hivatkozott tanulóprojektek teljes forrásfái nem azonosíthatók egyértelműen.

### CQ-ARCH-003 – Python–GDScript összehasonlítás scope

**Státusz:** `needs_comparison_design`

A comparison kérdés nem lezárt és nem obsolete.

Eldöntendő:

- teljes rules-engine összehasonlítás kell-e;
- elég-e egy minimal transition proof;
- Python output ↔ Godot parser round-trip legyen-e az első teszt;
- kell-e child process/service bridge prototype;
- milyen teljesítmény-, hibakezelési és packaging adat szükséges;
- mely tanulóprogram mintáját érdemes reprodukálni.

Nem cél automatikusan két teljes engine párhuzamos felépítése.

### CQ-ARCH-004 – Python–Godot integráció

**Státusz:** `needs_integration_prototype`

Vizsgálandó alternatívák:

- child process + stdin/stdout JSON;
- lokális socket vagy HTTP service;
- Python sidecar;
- natív vagy más bridge;
- szükség esetén GDScript runtime proof.

Kötelező elvek:

- explicit action request;
- state/version guard;
- atomikus mutation;
- player-visible response;
- debug információ elkülönítése;
- kontrollált process- és kapcsolatkezelés.

### CQ-ARCH-005 – Módosíthatja-e a frontend közvetlenül a state-et?

**Státusz:** `answered`

Döntés:

- nem;
- a frontend vagy AI action requestet küld;
- az authoritative engine validál és transitiont hajt végre;
- player-facing output projectionből származik.

### CQ-ARCH-006 – Mi a következő közvetlen engine-lépés?

**Státusz:** `answered`

Döntés:

- az izolált Wellspring contract production PlayerState- és MatchState-integrációja;
- még nincs Inflow, payment vagy `play_card`.

Ez a feladat a végleges Python–Godot bridge-döntés előtt is biztonságosan elvégezhető.

---

## 3. Wellspring runtime integráció

### CQ-WS-001 – PlayerState mező és authoritative tagság

**Státusz:** `ready_for_implementation`

Javasolt döntés:

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

## 4. Beáramlás

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

## 5. Magnitúdó és Aura

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

## 6. Prioritási összefoglaló

### Közvetlen programozási prioritás

1. Wellspring runtime integráció.
2. Player-visible Wellspring summary.
3. Beáramlás.
4. Magnitúdó és payment.
5. Első `play_card`.

### Párhuzamos technológiai/dokumentációs prioritás

1. `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` közös triázsa.
2. Tanulóprogram-forrásleltár.
3. Python–Godot technológiai minták auditja.
4. Comparison-prototípus scope.
5. Minimal bridge- és packaging proof.

A két munkasáv egymást támogatja. A belső engine-fejlesztés folytatható, miközben a végleges termékarchitektúra vizsgálata nyitva marad.
