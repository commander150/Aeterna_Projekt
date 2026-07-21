# Aeterna Projekt

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.1  
**Dátum:** 2026-07-22  
**Státusz:** aktív repository-szintű belépési dokumentum  
**Felváltott verzió:** `README.md` 2.0  
**Ellenőrzött repository-bázis:** `66a206c6e3bf9155fb9f71a354236fb5b6ab3b90` – `docs update 2026.07.22`  
**C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Az **AETERNA** saját fejlesztésű fizikai és digitális gyűjtögetős kártyajáték-projekt.

---

## 1. Elfogadott digitális architektúra

- **Godot / GDScript:** vizuális kliens, UI, input, animáció és debug.
- **C# / .NET:** az egyetlen tervezett production authoritative rules engine.
- **Python:** adat-, export-, audit-, fixture-, AI-, batch- és elemzőtooling, valamint reference engine.

A Godot nem szabályforrás. A Python nem marad második production authority. A production C# engine még nem létezik.

Bizonyított proofok:

- Python–Godot sidecar: `COMPLETE_AND_FROZEN`;
- Godot .NET/C# in-process candidate: `COMPLETE_AND_ACCEPTED`.

Canonical comparison SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

---

## 2. Hivatalos szabály- és adatforrások

- `Aeterna dokumentációk/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`;
- `Aeterna dokumentációk/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`;
- `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `Aeterna dokumentációk/LOOKUPS.xlsx`.

A két DOCX az elsődleges játékszabályforrás. A kód, a runtime package és a régi dokumentumok nem írhatják felül őket.

---

## 3. Aktuális projektirány

- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.4.md`;
- `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.7.md`;
- `Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`.

Engine-architektúra és döntések:

- `Aeterna game engine/docs/ARCHITECTURE.md`;
- `Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`;
- `Aeterna game engine/docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `Aeterna game engine/docs/DECISION_MAP.md`.

Aktuális technikai státusz:

- `Aeterna game engine/docs/PROTOTYPE_STATUS.md`;
- `Aeterna game engine/docs/RUNTIME_PACKAGE_STATUS.md`;
- `Aeterna game engine/docs/CONTRACT_STATUS.md`.

Open Questions:

- `Aeterna game engine/docs/OPEN_QUESTIONS.md`;
- `Aeterna game engine/docs/OPEN_QUESTIONS_DECISIONS.md`.

---

## 4. Repository fő területei

### `Aeterna dokumentációk/`

Hivatalos szabályforrások, kártyaadatbázis, LOOKUPS, projektirányítás, auditstandardok és aktív reference dokumentumok.

### `Aeterna game engine/`

Az új digitális programegység:

- `C#/` – proof és production C# projektek;
- `python/` – reference engine és külső tooling;
- `Godot/` – visual client, loader és debug;
- `docs/` – aktív engine-dokumentáció;
- `runtime_comparison/` – regressziós fixture és artifactok.

### `Archive/`

Történeti dokumentumok, régi motorok, korábbi auditok és generált exportpillanatok.

Az archívum nem aktív authority.

---

## 5. Aktuális fejlesztési állapot

Elkészült:

- runtime package build és publish pipeline;
- Godot package loader és registry;
- snapshot/legal action/event debug foundation;
- Python minimal reference engine;
- card instance, zone move és state version alap;
- Python-sidecar proof;
- C# in-process proof;
- runtime-nyelvi döntés;
- C.5A production architecture;
- dokumentációs és archív rendezés.

Következő kódolási feladat:

**C.5B – Production C# Engine Foundation**

Státusz:

`READY_FOR_IMPLEMENTATION`

Első scope:

- production C# engine;
- headless host;
- tests;
- EngineSession;
- minimum runtime package loader;
- draw, stale reject és end-turn;
- canonical fixture;
- Godot production bridge.

Új gameplay nem része ennek a szakasznak.

---

## 6. Dokumentációs szabály

A dokumentációs tömegrendezés lezárult.

A továbbiakban csak a következőket kell rendszeresen karbantartani:

- aktuális projektterv;
- projekt-térkép, ha a fájlszerepek változnak;
- engine-checkpoint;
- közvetlenül érintett contract vagy státuszdokumentum.

Nem szükséges minden technikai lépés után a teljes dokumentációs réteget frissíteni.

---

## 7. Következő lépés

1. A négy kritikus dokumentum rövid visszaellenőrzése.
2. Dokumentációs commit.
3. C.5B Production C# Engine Foundation implementáció Codexszel.
