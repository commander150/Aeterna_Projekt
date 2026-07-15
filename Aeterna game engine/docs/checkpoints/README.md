# AETERNA Game Engine – Checkpoint Index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív checkpoint-index és státusztérkép

Ez a dokumentum elválasztja:

- a történeti runtime package / Godot mérföldköveket;
- a jelenlegi Python rules-engine checkpointot;
- a termékmérföldkövet;
- a részletes történeti naplót.

Nem helyettesíti a részletes checkpointokat.

---

## 1. Melyik checkpoint mire való?

### Aktuális technikai folytatási pont

- `CURRENT_ENGINE_CHECKPOINT.md`

Ez az elsődleges dokumentum, ha a jelenlegi Python rules engine fejlesztését kell folytatni.

Tartalmazza:

- a jelenlegi MatchState és PlayerState modellt;
- card instance és zónaszabályokat;
- Domain topology és occupancy állapotot;
- player-visible snapshotot;
- eventeket;
- AI trajectoryt;
- activity state-et;
- Wellspring contractot;
- tesztállapotot;
- a következő biztonságos feladatot.

### Történeti technikai checkpointnapló

- `CHECKPOINTS.md`

Ez a fájl megőrzi a korábbi runtime package-, exporter- és Godot-prototípus mérföldköveket.

Nem az aktuális rules-engine folytatási pont.

### Hosszú távú termékmérföldkő

- `../AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

Ez nem technikai checkpoint, hanem a későbbi első zárt, játszható tesztkiadás célállapota.

---

## 2. Történeti checkpointok

### v0.1 – Python sample runtime package + Godot loader

**Státusz:** `completed_foundation`

Bizonyította:

- Python sample runtime package generálását;
- többfájlos package-et;
- Godot loader működését;
- registrybetöltést;
- headless package smoke tesztet.

Nem bizonyította:

- szabálymotort;
- action-végrehajtást;
- AI-t;
- játszható UI-t.

### v0.2 – Sample contracts + debug views

**Státusz:** `completed_foundation`

Bizonyította:

- statikus sample snapshot betöltését;
- statikus sample legal action betöltését;
- statikus sample event log betöltését;
- snapshot viewer működését;
- legal action debug panel működését;
- event log debug view működését.

Nem bizonyította:

- valós MatchState generálását;
- szabályból számított legal actiont;
- valódi action request/response végrehajtást.

### v0.3 – XLSX exporter migration smoke

**Státusz:** `completed_foundation`

Bizonyította:

- az exporter Python tooling alá migrálását;
- explicit source és output útvonalat;
- valódi XLSX → JSONL smoke futtatást;
- az exporter unit tesztelhetőségét.

### v0.4 – Runtime package publish pipeline és LOOKUPS source split

**Státusz:** `completed_foundation_active_pipeline`

Bizonyította:

- candidate build és validation gate használatát;
- Godot runtime package publish útvonalat;
- 1.9v kártyaadatbázis és LOOKUPS source splitet;
- runtime lookup reader működését;
- normalization alias és audit report package outputot;
- Godot consumption copy frissítését.

A v0.4 után a runtime package–Godot alapozás első önálló mérföldköve teljesült.

Ez az irány nem lett eldobva. Az aktív architecture része maradt, de a következő blokkoló feladat a valódi authoritative rules engine felépítése lett.

---

## 3. Jelenlegi rules-engine checkpoint

A jelenlegi technikai állapot bázisa:

- commit: `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`
- commit message: `Add minimal Wellspring resource contracts`

A történeti v0.1–v0.4 checkpointok után elkészült többek között:

- expected state version guard;
- card instance registry;
- deck/hand/discard authoritative zónák;
- draw transition;
- ZoneMove event;
- end-turn transition;
- generic event envelope;
- player-visible snapshot v2;
- canonical AI trajectory;
- Domain position contract;
- Domain topology MatchState-integráció;
- Domain occupancy contract;
- Domain occupancy MatchState-integráció;
- player-visible Domain board;
- structural Entity placement option;
- card instance activity state;
- Wellspring state és resource summary contract.

Részletesen:

- `CURRENT_ENGINE_CHECKPOINT.md`

---

## 4. Mérföldkő-folytonosság

A projekt technikai fejlődése nem irányváltások sorozata, hanem egymásra épülő rétegek lánca:

```text
v0.1 runtime package loader alap
        ↓
v0.2 sample contract és debug UI alap
        ↓
v0.3 exporter migration
        ↓
v0.4 publish pipeline és LOOKUPS source split
        ↓
minimal authoritative Python rules engine
        ↓
first playable vertical slice
        ↓
AETERNA 0.0.1
```

A runtime package–Godot tengely:

- elkészült alapozási szinten;
- aktív architektúrarész maradt;
- később player UI és Python–Godot integráció formájában folytatódik.

A jelenlegi közvetlen prioritás:

- a Python rules engine stabilizálása és első gameplay-láncának felépítése.

---

## 5. Aktuális mérföldkő-rétegek

### M1 – Minimal determinisztikus engine-alapok

**Állapot:** nagyrészt elkészült.

### M2 – Player view és board contract

**Állapot:** első jelentős szakasz elkészült.

### M3 – Első gameplay actionök

**Állapot:** előkészítés alatt.

Következő lánc:

1. Wellspring MatchState-integráció;
2. player-visible Wellspring summary;
3. Beáramlás precondition;
4. Beáramlás transition;
5. Magnitúdó-preflight;
6. Aura-payment;
7. Entity play precondition;
8. `play_card`.

### M4–M9

**Állapot:** későbbi roadmap.

---

## 6. Checkpointkészítési szabály

Új checkpoint akkor készüljön, ha egy érdemi technikai szakasz lezárult.

Minden új checkpoint tartalmazza:

- báziscommit;
- elkészült funkciók;
- contract- és schemaállapot;
- érintett state-rétegek;
- teszteredmények;
- smoke eredmények;
- ismert korlátok;
- nem implementált rendszerek;
- következő biztonságos lépés;
- dokumentációs adósság;
- worktree állapot.

Ne készüljön külön checkpoint minden apró commit után.

---

## 7. Dokumentumelsőbbség

Aktuális technikai folytatásnál:

1. `CURRENT_ENGINE_CHECKPOINT.md`
2. `../CURRENT_CONTRACT_STATUS.md`
3. `../CURRENT_OPEN_QUESTIONS.md`
4. `../ARCHITECTURE.md`
5. `CHECKPOINTS.md`

A `CHECKPOINTS.md` régi „következő lépés” megjegyzései történeti állapotot rögzítenek, és nem írják felül az aktuális checkpointot.
