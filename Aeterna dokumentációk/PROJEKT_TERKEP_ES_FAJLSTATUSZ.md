# AETERNA – Projekt- és fájltérkép

## DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 1.0
- **Dátum:** 2026-07-26
- **Státusz:** stabil, ritkán változó projekt- és fájlszerep-térkép
- **Frissítési feltétel:** csak mappa-, fájlszerep- vagy authority-változáskor

Ez a fájl nem roadmap, nem aktuális tasklista és nem commitstátusz.

---

## 1. Hivatalos szabály- és adatforrások

### `Aeterna dokumentációk/`

Elsődleges források:

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`
- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`
- `LOOKUPS.xlsx`

Operatív dokumentumok:

- `AETERNA_AKTUALIS_PROJEKTALLAPOT.md`
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ.md`

A korábbi verziózott projekttervek és térképek történeti referenciák.

---

## 2. Game Engine

### `Aeterna game engine/C#/`

- `Aeterna.Engine` – pure C# authoritative engine;
- `Aeterna.Engine.Headless` – headless/fixture/batch host;
- `Aeterna.Engine.Tests` – production engine tesztek;
- `Aeterna.RuntimeCandidate*` – elfogadott történeti proofok.

### `Aeterna game engine/python/`

- runtime package build és publish;
- XLSX/JSON/JSONL tooling;
- audit és diagnostics;
- Python reference engine;
- fixture, AI, batch és elemzés.

Nem production authority.

### `Aeterna game engine/Godot/`

- visual client;
- runtime package fogyasztás;
- debug és bridge;
- későbbi játékos UI, input és animáció.

Nem szabályforrás és nem authoritative state-gazda.

### `Aeterna game engine/runtime_comparison/`

- canonical fixture-ek;
- expected/candidate artifactok;
- regressziós és determinism összehasonlítás.

### `Aeterna game engine/docs/`

Tartós dokumentumok:

- `ARCHITECTURE.md`
- `TECHNOLOGY_DECISIONS.md`
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `CONTRACT_SPECIFICATION.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `ABILITY_MODULE_SYSTEM.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`

Operatív történeti napló:

- `checkpoints/CHECKPOINTS.md`

A korábbi státusz-, döntéstérkép- és engine-checkpoint fájlok csak
linkfolytonossági/történeti átirányítók.

---

## 3. Learning

### `learning/`

- aktuális verziózott katalógus és forráslista;
- `analyses/` – stabil fájlnevű projektszintű elemzések;
- `sources/` – helyi forráskód, Git által figyelmen kívül hagyva.

A learning anyag nem szabályforrás és nem engine-specifikáció.

---

## 4. Archive

### `Archive/`

- régi dokumentumok;
- felváltott rendszerek;
- történeti auditok;
- korábbi motor- és exportpillanatok.

Az archívum nem aktív authority.

---

## 5. Aktív dokumentációs rendszer

| Dokumentum | Szerep | Mikor frissül? |
|---|---|---|
| `README.md` | repository-navigáció | csak szerkezeti változáskor |
| `AETERNA_AKTUALIS_PROJEKTALLAPOT.md` | aktuális állapot és következő lépés | elfogadott mérföldkőnél |
| `checkpoints/CHECKPOINTS.md` | append-only történeti napló | elfogadott mérföldkőnél |
| `PROJEKT_TERKEP_ES_FAJLSTATUSZ.md` | mappa- és fájlszerepek | csak szerepváltozáskor |
| `ARCHITECTURE.md` | tartós architektúra | architektúraváltozáskor |
| `TECHNOLOGY_DECISIONS.md` | elfogadott döntések | új vagy módosított döntéskor |
| contract/package specifikációk | technikai szerződések | contractváltozáskor |
| Open Questions pár | kérdés és döntésnyilvántartás | kérdés/döntés változásakor |

---

## 6. Tiltott dokumentációs minták

- ugyanazon aktuális állapot több aktív fájlban;
- minden commit után teljes dokumentációfrissítés;
- README-ben gyorsan avuló SHA vagy roadmap;
- státuszdokumentum és specifikáció összekeverése;
- új `CURRENT_*` vagy párhuzamos replacement fájl;
- új projektterv-verzió minden kisebb mérföldkőhöz;
- régi „következő lépés” aktív authorityként kezelése.

---

## 7. Következő állapot megkeresése

Minden új munkamenet első operatív dokumentuma:

```text
Aeterna dokumentációk/AETERNA_AKTUALIS_PROJEKTALLAPOT.md
```

Történeti ellenőrzéshez:

```text
Aeterna game engine/docs/checkpoints/CHECKPOINTS.md
```
