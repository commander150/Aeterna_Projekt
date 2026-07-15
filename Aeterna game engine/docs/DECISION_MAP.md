# AETERNA Game Engine – Decision Map

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív rövid döntési és iránytérkép  
**Aktuális technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum röviden rögzíti:

- mi az elfogadott projektirány;
- mely döntések zárultak le;
- mely kérdések maradtak nyitva;
- milyen sorrendben halad a fejlesztés;
- mit nem szabad összekeverni.

Nem teljes projektterv, architektúra, contract-specifikáció vagy checkpointnapló.

Kapcsolódó elsődleges dokumentumok:

- `../../Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`
- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`
- `ARCHITECTURE.md`
- `TECHNOLOGY_DECISIONS.md`
- `CURRENT_CONTRACT_STATUS.md`
- `CURRENT_OPEN_QUESTIONS.md`
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

---

## 1. Projektcél

Az AETERNA elsődlegesen fizikai TCG.

A digitális programegység célja:

- a szabályok modellezése és tesztelése;
- a kártyaadatok programbiztos kezelése;
- determinisztikus meccsfuttatás;
- AI-vs-AI tesztelés;
- későbbi ember–AI játék;
- Godot-alapú kliens és UI;
- végül az AETERNA 0.0.1 zárt tesztkiadás.

A digitális engine nem írhatja felül a hivatalos 1.4v szabályforrásokat emberi döntés nélkül.

---

## 2. Elsődleges fejlesztési irány

Elfogadott döntés:

> **A jelenlegi authoritative szabálymotor a Python rules engine.**

A Godot szerepe:

- runtime package fogyasztás;
- registry;
- debug nézetek;
- játékos UI;
- input és animáció;
- későbbi kliens;
- action requestek elküldése;
- player-visible válaszok megjelenítése.

Nem készül külön GDScript authoritative szabálymotor.

A régi Python motor:

- review és referencia;
- nem automatikus migrációs forrás;
- csak célzott audit után használható fel.

---

## 3. Fő rendszerrétegek

```text
Hivatalos szabályforrások
        ↓
Kártyaadatbázis és LOOKUPS
        ↓
Python export / validáció / runtime package
        ↓
Python authoritative rules engine
        ↓
Snapshot / legal actions / action response / events
        ↓
Godot kliens és UI
```

### Hivatalos szabályforrások

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

### Statikus adatréteg

- Google Sheets / XLSX szerkesztési forrás;
- kártyaadatbázis;
- LOOKUPS;
- export és validáció;
- runtime package.

### Rules engine

- MatchState;
- PlayerState;
- card instance registry;
- invariánsok;
- legal action;
- action request és response;
- transitionök;
- typed eventek;
- projectionök;
- AI trajectory.

### Godot kliens

- loader;
- registry;
- debug UI;
- player-facing UI;
- későbbi interaktív játékprogram.

---

## 4. Elkészült alapozási mérföldkövek

### Runtime package–Godot alap

**Állapot:** elkészült alapozási szinten.

Bizonyított:

- Python runtime package build;
- XLSX exporter migration;
- LOOKUPS source split;
- candidate publish pipeline;
- Godot runtime package loader;
- Godot registryk;
- sample snapshot, legal action és event contractok;
- debug nézetek;
- Godot headless smoke tesztek.

Ez az irány továbbra is aktív architektúrarész, nem eldobott prototípus.

### Minimal Python rules engine

**Állapot:** aktív fejlesztés, jelentős alapok elkészültek.

Elkészült:

- state version guard;
- card instance registry;
- deck/hand/discard zónák;
- draw és end-turn;
- typed eventek;
- player-visible snapshot v2;
- Domain topológia és occupancy;
- public board projection;
- structural Entity placement;
- activity state;
- izolált Wellspring resource contract;
- deterministic AI trajectory.

---

## 5. Contract-first döntések

Elfogadott:

- előbb contract, utána implementáció;
- a frontend nem találgat szabályt;
- az AI nem találgat szabályt;
- a kliens nem módosít MatchState-et;
- legal actiont az engine ad;
- action requestet az engine validál;
- player-visible és debug projection külön;
- rejtett információ nem szivároghat;
- minden state mutation atomikus;
- rejected action nem mutál state-et;
- eventek typed és determinisztikusak.

Aktuális megvalósítási státusz:

- `CURRENT_CONTRACT_STATUS.md`

A hosszú `CONTRACT_SPECIFICATION.md` tervezési és referenciaanyag; nem minden benne szereplő mező aktív runtime contract.

---

## 6. Runtime package döntések

Elfogadott:

- Godot nem olvas közvetlenül XLSX-et;
- Python végzi az exportot és validációt;
- a runtime package statikus programfogyasztási forma;
- kártyák és deckek az aktív 1.9v adatbázisból jönnek;
- lookupok a `LOOKUPS.xlsx` fájlból jönnek;
- Godot `runtime_package/` consumption copy;
- publish előtt validation gate szükséges;
- a TEMP candidate pipeline átmenetileg elfogadott.

Még nyitott:

- végleges build/output könyvtár;
- package registry és release versioning;
- TEMP staging későbbi kiváltása;
- publikus build integritásvédelem.

---

## 7. Aktuális engine-prioritás

Következő fejlesztési lánc:

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

Nem szabad közvetlenül a `play_card` implementációra ugrani a szükséges erőforrás-, timing- és transition-rétegek nélkül.

---

## 8. Mérföldkő-térkép

- M1 – minimal determinisztikus engine-alapok
- M2 – player view és board contract
- M3 – első gameplay actionök
- M4 – phase, priority és reakciók
- M5 – combat és győzelmi feltételek
- M6 – első játszható vertical slice
- M7 – teljes alapjátékos tesztprogram
- M8 – meta- és termékrendszerek
- M9 – 0.0.1 release candidate

Jelenlegi állapot:

- M1: nagyrészt elkészült;
- M2: első jelentős szakasza elkészült;
- M3: előkészítés alatt;
- M4–M9: későbbi roadmap.

---

## 9. Fő nyitott döntési kapuk

### Közeli engine-kapuk

- Wellspring PlayerState schema;
- Wellspring invariantok;
- player-visible Wellspring policy;
- Beáramlás belépési activity state;
- körönkénti Beáramlás nyilvántartása;
- Magnitúdó-preflight szerkezete;
- typed Aura és payment source selection;
- atomic payment és rollback;
- activity state player-facing projection.

Részletesen:

- `CURRENT_OPEN_QUESTIONS.md`

### Későbbi technológiai kapuk

- Python–Godot transport;
- Windows packaging;
- save/load;
- replay execution;
- CI;
- performance és AI batch infrastructure.

### Későbbi szabályi kapuk

- teljes phase/priority;
- reaction model;
- combat;
- Pecsét-state;
- Aeternal győzelmi modell;
- ability execution;
- keyword support.

---

## 10. Párhuzamos munkasávok

### Engine

Elsődleges aktív fejlesztési sáv.

### Dokumentáció

Feladata:

- aktuális státusz megőrzése;
- történeti tartalom elkülönítése;
- nyitott kérdések megőrzése;
- contractok és implementation státusz szétválasztása.

### Kártyaadat és audit

Külön kezelendő:

- kártyaadat-hiba;
- structured hiba;
- engine-hiány;
- szabályértelmezési kérdés;
- balanszgyanú.

### Runtime package és Godot

Aktív, de jelenleg nem a közvetlen kritikus út.

A Python–Godot interaktív integráció az első stabil rules-engine vertical slice után válik újra elsődleges prioritássá.

### Régi motor review

Külön audit- és referenciafeladat.

---

## 11. Amit nem csinálunk most

- két authoritative rules engine;
- teljes Godot rules runtime;
- nagy homályos refaktor;
- teljes UI a szabálymotor előtt;
- `play_card` az előfeltételek nélkül;
- teljes ability engine egyetlen lépésben;
- online/PvP infrastruktúra;
- booster és economy rendszer;
- régi motor automatikus migrációja;
- dokumentáció, runtime és kártyaadat keverése egy commitban;
- tesztek törlése csak a darabszám csökkentéséért.

---

## 12. Munkamegosztás

### Emberi döntés

Szükséges:

- szabályértelmezés;
- gameplay- és termékdöntés;
- prioritás;
- balanszdöntés;
- nyitott kérdések lezárása.

### ChatGPT

Feladata:

- projekt- és függőségelemzés;
- dokumentáció;
- feladatbontás;
- Codex-prompt vagy közvetlen GitHub-munka;
- jelentések ellenőrzése;
- szabályforrások összevetése;
- következő biztonságos lépés kijelölése.

### Codex vagy más kódoló agent

Feladata:

- szűk, ellenőrizhető implementáció;
- célzott tesztek;
- smoke futtatás;
- commit és technikai jelentés.

Nem kap önálló szabályi vagy projektirányítási döntést.

---

## 13. Dokumentumelsőbbség

1. Hivatalos 1.4v szabályforrások.
2. AETERNA 0.0.1 célállapot.
3. Aktuális projektterv v6.0.
4. `CURRENT_ENGINE_CHECKPOINT.md`.
5. `ARCHITECTURE.md`.
6. `TECHNOLOGY_DECISIONS.md`.
7. `CURRENT_CONTRACT_STATUS.md`.
8. `CURRENT_OPEN_QUESTIONS.md`.
9. Hosszú specifikációk és történeti checkpointok.
10. Régi dokumentumok és archív referenciák.

---

## 14. Rövid összefoglaló

**Authoritative rules engine:** Python  
**Godot:** kliens-, loader-, debug- és UI-réteg  
**Runtime package:** statikus adatcontract  
**Régi Python motor:** review és referencia  
**Jelenlegi engine-bázis:** `84a7e8f4`  
**Következő feladat:** Wellspring runtime integráció  
**Hosszú távú cél:** AETERNA 0.0.1  
**Aktuális kritikus út:** resource state → Beáramlás → payment → `play_card`
