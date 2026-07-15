# AETERNA Game Engine – Decision Map

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív rövid döntési és iránytérkép  
**Aktuális technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum röviden rögzíti:

- mi biztosan eldöntött;
- mi a jelenlegi munkairány;
- mi maradt nyitott technológiai kapu;
- milyen sorrendben halad a fejlesztés;
- mit nem szabad összekeverni.

Kapcsolódó dokumentumok:

- `TECHNOLOGY_DECISIONS.md`
- `ARCHITECTURE.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `CURRENT_OPEN_QUESTIONS.md`
- `CURRENT_PROTOTYPE_STATUS.md`
- `CURRENT_CONTRACT_STATUS.md`
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

---

## 1. Biztos projektcél

Az AETERNA elsődlegesen fizikai TCG.

A digitális programegység célja:

- szabálymodellezés és tesztelés;
- programbiztos kártyaadat;
- determinisztikus meccsfuttatás;
- AI-vs-AI;
- későbbi ember–AI játék;
- Godot-alapú kliens;
- végül a 0.0.1 zárt tesztkiadás.

A digitális rendszer nem írhatja felül a hivatalos 1.4v szabályforrásokat emberi döntés nélkül.

---

## 2. Jelenlegi munkairány

Biztos jelenlegi állítás:

> **Az aktívan fejlesztett és tesztelt authoritative szabálymotor a Python minimal engine.**

Biztos Godot-szerep:

- runtime package loader;
- registry;
- debug nézetek;
- input és UI;
- animáció;
- későbbi kliens;
- contract-fogyasztás.

Ez a jelenlegi működő fejlesztési modell.

Nem tekintendő még végleges termékarchitektúra-döntésnek.

---

## 3. Végleges technológiai döntés státusza

### Erős jelenlegi jelölt

- Python rules/backend + Godot frontend/kliens.

### Még bizonyítandó

- Python–Godot bridge;
- Windows packaging;
- process lifecycle;
- teljesítmény;
- hibatűrés;
- verziókezelés;
- tanulóprogramok technológiai mintái;
- szükséges Python–GDScript comparison scope.

### Nem aktív, de nem végleg elutasított alternatívák

- teljes GDScript rules runtime;
- részleges GDScript runtime;
- más hibrid megosztás.

Két teljes engine párhuzamos fejlesztése jelenleg nem indokolt, de az összehasonlító vizsgálat nem obsolete.

---

## 4. Stabil contract-first döntések

Elfogadott:

- előbb contract, utána implementáció;
- egy futásban egy authoritative state;
- frontend és AI nem találgat legalitást;
- kliens nem módosít MatchState-et;
- kliens action requestet küld;
- engine validál és transitiont hajt végre;
- player-visible és debug projection külön;
- hidden information védett;
- state mutation atomikus;
- rejected action nem mutál state-et;
- typed event és state version determinisztikus.

Ezek a végleges nyelvi/runtimedöntéstől függetlenek.

---

## 5. Elkészült alapozási mérföldkövek

### Runtime package–Godot alap

**Állapot:** `completed_foundation`

Elkészült:

- Python runtime package build;
- XLSX exporter migráció;
- valós card/deck/lookup publish;
- Godot loader;
- registryk;
- sample contract loader;
- card reference resolver;
- consistency smoke;
- debug dashboard;
- Godot headless smoke.

### Python minimal rules engine

**Állapot:** `current_working_basis`

Elkészült:

- state version guard;
- card instance registry;
- draw és end-turn;
- typed eventek;
- player-visible snapshot;
- Domain topology és occupancy;
- board projection;
- structural Entity placement;
- activity state;
- izolált Wellspring resource contract;
- deterministic AI trajectory.

---

## 6. Aktuális engine-prioritás

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
12. Teljesebb phase és priority.

A végleges bridge-döntés nem blokkolja ezeket a belső engine-alapokat.

---

## 7. Aktuális technológiai bizonyítási prioritás

1. `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` közös triázsa.
2. Tanulóprogram-forrásleltár.
3. Python-engine/Godot minták auditja.
4. Python–GDScript comparison céljának pontosítása.
5. Minimal Python–Godot bridge proof.
6. Szükség esetén minimal GDScript transition proof.
7. Windows packaging proof.
8. Végleges runtime/backend döntés.

---

## 8. Tanulóprogram-audit döntési kapu

Vizsgálandó:

- mely tanulóprogramok forrása érhető el;
- melyik használ Python engine-t;
- van-e Godot + Python működő minta;
- hol van az authoritative state;
- milyen bridge és packaging készül;
- melyik csak UI-minta;
- melyik minta alkalmazható clean-room módon AETERNA-ra.

Jelenleg a repositoryban biztosan elérhető a tanulságokat összefoglaló dokumentum, de a hivatkozott projektek teljes forrásfái nem azonosíthatók egyértelműen.

---

## 9. Python–GDScript comparison

**Státusz:** nyitott, későbbi technológiai bizonyítás.

Nem feltétlenül jelent két teljes engine-t.

Lehetséges scope:

- contract parser round-trip;
- azonos snapshot;
- azonos minimal transition;
- deterministic JSON;
- bridge latency;
- process failure;
- Windows packaging;
- tanulóprogram-minta reprodukciója.

A scope a tanulóprogram-audit után véglegesítendő.

---

## 10. Runtime package döntések

Lezárt:

- Godot nem olvas közvetlenül XLSX-et;
- Python végzi az exportot és validációt;
- runtime package statikus programadat;
- Godot `runtime_package/` consumption copy;
- publish előtt validation gate.

Nyitott:

- végleges package identity és schema;
- build/output könyvtár;
- release/version registry;
- TEMP staging kiváltása;
- publikus build integritásvédelem.

---

## 11. Mérföldkő-térkép

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

- M1 nagyrészt elkészült;
- M2 első jelentős szakasza elkészült;
- M3 előkészítés alatt;
- technológiai bridge és packaging bizonyítás párhuzamos kapu.

---

## 12. Amit biztosan nem keverünk össze

- jelenlegi Python implementációs authority ≠ végleges termékarchitektúra;
- Godot UI ≠ authoritative state;
- runtime package ≠ MatchState;
- sample contract ≠ production contract;
- structural placement ≠ teljes play legality;
- Magnitúdó ≠ elérhető Aura;
- activity state ≠ idézési betegség;
- tanulóprogram-minta ≠ automatikusan átvehető kód;
- comparison prototype ≠ két teljes engine kötelező felépítése.

---

## 13. Rövid jelenlegi döntés

- A Python minimal engine fejlesztése folytatódik.
- A Godot kliens- és loaderalap megmarad.
- A Python backend + Godot frontend a legerősebb jelenlegi jelölt.
- A végleges runtime/backend döntés még nyitott.
- A tanulóprogram-audit és a Python–GDScript comparison nem lett törölve vagy obsolete-té nyilvánítva.
