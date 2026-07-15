# AETERNA Game Engine – Current Open Questions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív közeli döntési kapu- és kérdéslista  
**Technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum a következő engine-feladatokat közvetlenül blokkoló vagy befolyásoló kérdéseket tartalmazza.

A teljes történeti és hosszú távú kérdésregiszter továbbra is:

- `OPEN_QUESTIONS.md`

Ez a rövid lista nem töröl és nem helyettesít régi kérdést. Feladata, hogy a napi fejlesztésnél egyértelmű legyen, mely döntések szükségesek először.

---

## 1. Státuszok

| Státusz | Jelentés |
|---|---|
| `ready_for_implementation` | A szükséges irány már eldöntött, implementálható. |
| `needs_source_check` | Hivatalos szabályforrásból pontosítani kell. |
| `needs_engine_design` | Technikai contract- vagy state-döntés kell. |
| `needs_visibility_decision` | Player-visible és hidden-information policy kell. |
| `deferred` | Későbbi roadmap-szakaszra halasztva. |
| `answered` | Megválaszolva és aktív dokumentumba átvezetve. |

---

## 2. Már megválaszolt fő architektúra-kérdések

### CQ-ARCH-001 – Melyik az authoritative rules engine?

**Státusz:** `answered`

Döntés:

- a jelenlegi authoritative szabálymotor a Python engine;
- a Godot kliens-, loader-, registry- és debugréteg;
- nem tartunk fenn két külön authoritative szabálymotort;
- a régi Python motor referencia/review státuszban marad.

Átvezetve:

- `ARCHITECTURE.md`
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`
- `CURRENT_ENGINE_CHECKPOINT.md`

### CQ-ARCH-002 – Módosíthatja-e a frontend közvetlenül a state-et?

**Státusz:** `answered`

Döntés:

- nem;
- a frontend vagy AI action requestet küld;
- a rules engine validál és transitiont hajt végre;
- player-facing output projectionből származik.

### CQ-ARCH-003 – Mi az aktuális következő engine-lépés?

**Státusz:** `answered`

Döntés:

- az izolált Wellspring contract production PlayerState- és MatchState-integrációja;
- még nincs Inflow, payment vagy `play_card`.

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

Döntési kérdés:

- maradjon-e ez általános engine-konvenció a kézhez és Domainhoz hasonlóan;
- szükséges-e később külön szabály a kontrollált, de nem tulajdonolt lap Ősforrásba kerülésére.

Közeli implementációban:

- owner-egyezést ne követeljünk;
- kontrollváltó gameplay ne készüljön.

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
- a face-down források saját játékos számára is rejtett Card_ID-júak-e, vagy csak az ellenfél számára.

A player-visible Wellspring projection előtt ezt a hivatalos főforrásból és játékszabályi szándékból rögzíteni kell.

---

## 4. Beáramlás

### CQ-INFLOW-001 – Belépési activity state

**Státusz:** `needs_source_check`

Kérdés:

- a normál Beáramlással Ősforrásba helyezett lap Aktív vagy Kimerült állapotban érkezik-e.

Ez közvetlenül meghatározza:

- az azonnal elérhető Aurát;
- a transition outputot;
- a ZoneMove/event payloadot;
- a player-visible resource summaryt.

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

Technikai kérdés:

- PlayerState turn marker;
- MatchState per-turn usage registry;
- action historyből származtatott érték;
- vagy külön turn-state contract legyen-e.

Javasolt irány:

- explicit, könnyen validálható per-turn state;
- ne event log visszakereséséből kelljen minden alkalommal számolni.

### CQ-INFLOW-004 – Eventmodell

**Státusz:** `needs_engine_design`

Kérdés:

- elegendő-e a generic `zone_move` event hand → wellspring adatokkal;
- vagy készüljön külön `inflow` typed event is.

Javasolt vizsgálat:

- a ZoneMove maradjon az objektummozgás canonical eseménye;
- külön Inflow event csak akkor szükséges, ha a szabályi jelentést, usage limitet vagy UI-magyarázatot a ZoneMove nem hordozza megfelelően.

---

## 5. Magnitúdó és Aura

### CQ-RES-001 – Magnitúdó-preflight contract

**Státusz:** `needs_engine_design`

Kérdések:

- milyen inputból oldjuk fel a kártya Magnitúdó-követelményét;
- exact runtime mező és canonical típus;
- hogyan jelenjen meg success/failure result;
- része legyen-e a legal action availabilitynek;
- hogyan kezeljük a Magnitúdó-módosító hatásokat később.

Első verzió:

- csak base Wellspring count;
- override és modifier nélkül.

### CQ-RES-002 – Typed Aura canonical modell

**Státusz:** `needs_source_check`

Rögzítendő:

- Aura canonical típusai;
- Birodalmi Aura és Aether/Semleges forrás szerepe;
- Entitás és nem-Entitás eltérő fizetési szabályai;
- többértékű Aura-forrás reprezentációja;
- pontos runtime lookupértékek.

### CQ-RES-003 – Payment source selection

**Státusz:** `needs_engine_design`

Kérdések:

- automatikus vagy kézi forrásválasztás;
- több azonos eredményű payment közül kell-e választás;
- payment request külön action vagy a play request része;
- források determinisztikus rendezése;
- insufficient Aura reject reason;
- atomikus kimerítés és rollback.

### CQ-RES-004 – Activity mutation event

**Státusz:** `needs_engine_design`

Kérdés:

- a payment során több Wellspring instance kimerítése egyetlen payment event vagy több activity-change event legyen-e.

Elvárás:

- state mutation atomikus;
- részleges payment nem maradhat state-ben;
- player-facing event ne szivárogtasson rejtett Card_ID-t.

### CQ-RES-005 – Rezonancia és ideiglenes Aura

**Státusz:** `deferred`

Csak a base payment stabilizálása után.

---

## 6. Entitás kijátszása

### CQ-PLAY-001 – Mikor válhat structural placement legal actionné?

**Státusz:** `needs_engine_design`

Szükséges előfeltételek:

- source kéz- és típusellenőrzés;
- timing és priority;
- Magnitúdó;
- Aura-payment;
- üres target;
- card-text restriction policy;
- entry-state;
- hand → Domain transition.

A jelenlegi structural option önmagában nem elegendő.

### CQ-PLAY-002 – Entity entry activity state

**Státusz:** `needs_source_check`

Kérdések:

- az Entitás Aktív állapotban lép-e be;
- milyen szabály korlátozza az azonnali támadást;
- a Gyorsaság hogyan módosítja ezt;
- külön `summoning_sickness` vagy turn-entry marker szükséges-e.

Az activity state és a támadási korlátozás külön modell maradjon.

### CQ-PLAY-003 – Card-text position restriction

**Státusz:** `deferred`

Első `play_card` vertical slice-ban:

- csak olyan Entitás használható, amelynek nincs egyedi Horizont/Zenit korlátozása;
- vagy külön explicit structured restriction kell.

A természetes szöveg parserként nem használható.

### CQ-PLAY-004 – Atomic hand → Domain transition

**Státusz:** `needs_engine_design`

Egy sikeres transitionben szükséges:

- hand listából eltávolítás;
- hand reindex;
- registry zone/domain frissítés;
- zone index null;
- visibility public;
- controller;
- activity/entry state;
- occupancy slot foglalása;
- state version;
- typed eventek;
- invariant check.

Bármely hiba esetén teljes rollback vagy előzetes precondition szükséges.

---

## 7. Player-visible state

### CQ-VIS-001 – Activity state board projection

**Státusz:** `needs_visibility_decision`

Kérdés:

- a Domainban lévő Entitás Aktív/Kimerült állapota kerüljön-e az ObjectReference-be;
- vagy külön slot/occupant state mező legyen.

Javasolt irány:

- ne bővítsük túl általánosan az ObjectReference-et, ha az activity csak board-contextben szükséges;
- külön public occupant state vagy kibővített board occupant projection mérlegelendő.

### CQ-VIS-002 – Event projection

**Státusz:** `needs_engine_design`

Kérdések:

- ugyanaz a typed event kapjon debug és player projectiont;
- vagy külön event contract készüljön;
- hidden Wellspring mozgásnál mely mezők láthatók az ellenfélnek.

### CQ-VIS-003 – Debug snapshot tartalma

**Státusz:** `deferred`

A jelenlegi debug schema maradjon stabil, amíg a player-facing layer épül.

---

## 8. Turn, phase és priority

### CQ-TURN-001 – Minimal turn modell kiváltása

**Státusz:** `deferred`

A teljes fázisrendszer csak az első gameplay vertical slice után bővüljön, de a Beáramlás és `play_card` timingjához minimális precondition layer szükséges.

### CQ-TURN-002 – Ébredés és automatikus Visszaállítás

**Státusz:** `needs_source_check`

Rögzítendő:

- mely objektumok állnak vissza;
- pontos fázis;
- eventmodell;
- triggerablakok;
- Wellspring és Domain activity mutation sorrendje.

### CQ-TURN-003 – Reakcióablak / queue / stack

**Státusz:** `deferred`

Csak a normál `play_card` és egyszerű transition stabilizálása után.

---

## 9. Tesztinfrastruktúra

### CQ-TEST-001 – Két sorrendfüggő XLSX mock-hiba

**Státusz:** `needs_engine_design`

Érintett tesztek:

- `test_finds_xlsx_files_only_in_source_directory`
- `test_lists_sheets_in_read_only_data_only_mode`

Jelenlegi policy:

- minden modul izoláltan zöld;
- monolitikus discoveryben 1 failure és 1 error;
- ez nem blokkolja a rules-engine commitot, ha nincs más regresszió;
- külön tesztizolációs feladatban javítandó.

Vizsgálati cél:

- mock/patch cleanup;
- module-global state;
- import order;
- openpyxl mock reset;
- tempfile és environment isolation.

### CQ-TEST-002 – Tesztmappák rendezése

**Státusz:** `deferred`

Előbb read-only audit szükséges.

Tervezett cél:

- `tests/unit/contracts/`
- `tests/unit/engine/`
- `tests/unit/invariants/`
- `tests/integration/ai/`
- `tests/smoke/`
- fixtures és helpers.

Tesztet nem törlünk pusztán a darabszám miatt.

---

## 10. Dokumentáció

### CQ-DOC-001 – Hosszú CONTRACT_SPECIFICATION és aktuális státusz

**Státusz:** `answered`

Döntés:

- a hosszú `CONTRACT_SPECIFICATION.md` megőrzi a tervezési hátteret;
- `CURRENT_CONTRACT_STATUS.md` rögzíti a tényleges aktív implementációt;
- később külön merge/refaktor során egységesíthetők.

### CQ-DOC-002 – Teljes OPEN_QUESTIONS és napi döntési lista

**Státusz:** `answered`

Döntés:

- `OPEN_QUESTIONS.md` teljes regiszter marad;
- jelen dokumentum a közeli aktív döntési kapu;
- kérdést csak akkor lehet `answered` státuszba tenni, ha a döntés aktív célfájlba átvezetésre került.

### CQ-DOC-003 – CHECKPOINTS.md konszolidáció

**Státusz:** `needs_engine_design`

Kérdés:

- a régi Godot/runtime package checkpointok és az új rules-engine commitlánc egyetlen időrendi fájlban maradjanak-e;
- vagy a `CURRENT_ENGINE_CHECKPOINT.md` legyen a gördülő aktuális checkpoint, míg a `CHECKPOINTS.md` történeti napló.

Javasolt irány:

- `CURRENT_ENGINE_CHECKPOINT.md` gördülő aktív állapot;
- `CHECKPOINTS.md` lezárt történeti mérföldkövek;
- nagy commitonként ne készüljön külön új checkpointfájl.

---

## 11. Következő döntési sorrend

A következő implementációk előtt ebben a sorrendben szükséges döntés:

1. Wellspring PlayerState-integráció technikai részletei;
2. Wellspring player-visible policy;
3. Inflow entry activity state;
4. Inflow timing és per-turn usage state;
5. Magnitúdó-preflight input contract;
6. typed Aura canonical modell;
7. payment source selection;
8. Entity entry-state;
9. atomic `play_card` transition;
10. activity board/event projection.

---

## 12. Rövid aktív lista

**Implementálható most:** Wellspring production state-integráció  
**Forrásellenőrzés kell hamarosan:** Inflow entry state és timing  
**Visibility-döntés kell:** Wellspring player projection  
**Payment előtt kell:** typed Aura és source-selection modell  
**`play_card` előtt kell:** timing, Magnitúdó, payment, entry-state  
**Külön technikai adósság:** két XLSX mock discovery-hiba  
**Későbbre halasztva:** reaction stack, combat, ability execution, teljes phase rendszer
