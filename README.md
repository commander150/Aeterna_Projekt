# Aeterna Projekt

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.6
**Dátum:** 2026-08-30
**Státusz:** aktív repository-szintű belépési dokumentum
**Felváltott verzió:** `README.md` 2.3
**Szinkronizációs repository-bázis:** `f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`
**Production engine mérföldkő:** `f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`

Az **AETERNA** saját fejlesztésű fizikai és digitális gyűjtögetős kártyajáték-projekt.

---

## 1. Elfogadott digitális architektúra

- **Godot / GDScript:** vizuális kliens, UI, input, animáció és debug.
- **C# / .NET:** az egyetlen production authoritative rules engine.
- **Python:** adat-, export-, audit-, fixture-, AI-, batch- és elemzőtooling, valamint reference/oracle.

Bizonyított proofok:

- Python–Godot sidecar: `COMPLETE_AND_FROZEN`;
- Godot .NET/C# in-process candidate: `COMPLETE_AND_ACCEPTED`;
- production C# engine: aktív authoritative rendszer.

---

## 2. Hivatalos szabály- és adatforrások

Szabályforrás:

- `Aeterna dokumentációk/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4.3v.docx`;
- `Aeterna dokumentációk/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`.

Aktív adatút:

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `LOOKUPS.xlsx`;
- `CARDDATABASE.xlsx`;
- `REGISTRY.xlsx`;
- validált canonical export/runtime package.

---

## 3. Aktuális projektirány

- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.8.md`;
- `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.11.md`;
- `Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`.

Aktuális engine-státusz és döntések:

- `ARCHITECTURE.md`;
- `TECHNOLOGY_DECISIONS.md`;
- `DECISION_MAP.md`;
- `PROTOTYPE_STATUS.md`;
- `RUNTIME_PACKAGE_STATUS.md`;
- `CONTRACT_STATUS.md`;
- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

---

## 4. Repository fő területei

- `Aeterna dokumentációk/` – szabály-, adat-, projekt- és munkafolyamat-források.
- `Aeterna game engine/` – C# engine, Python tooling/reference, Godot kliens, docs és fixture-ök.
- `learning/` – clean-room source registry, izolált project analyses és cross-project synthesis.
- `Aeterna game engine/docs/blueprints/` – AETERNA architecture proposal réteg.
- `Archive/` – történeti anyagok.

Az archívum és a learning réteg nem aktív authority.

---

## 5. Aktuális fejlesztési állapot

Elkészült többek között:

- runtime package/publish foundation;
- Python reference és sidecar proof;
- C# in-process proof;
- C.5A és C.5B;
- Wellspring / Beáramlás;
- Magnitúdó / Aura preflight;
- Domain / `play_card`;
- canonical ability/effect foundation;
- damage/vitals;
- continuous effects és modifier/keyword/duration;
- draw/reference runtime;
- Explicit Phase Foundation v1;
- Reaction / Priority Foundation v1;
- Ige/egyszeri Rituálé shared `resolution` lifecycle.

Aktuális canonical phase flow:

`awakening -> infusion -> manifestation -> incursion -> distribution`

Aktuális mérföldkő:

`f4e035bb1b8a1b94840a180df7f9c24aa3cf302c`

Legutóbbi lezáró acceptance:

- Debug `246/246 PASS`;
- Release `246/246 PASS`;
- determinism `100/100 PASS`;
- Godot production build/smoke PASS.

Dokumentációs/evidence állapot: learning `59/58/30`, synthesis/blueprints committed, OQ v2.2 `50/17/7/0`, targeted governance recovery committed.

Reaction / Priority v1 production foundation elkészült. Még nincs teljes combat/Pecsétmodell, Refresh Penalty, victory/defeat, replay, production AI vagy végleges UI/packaging.

---

## 6. Dokumentációs szabály

A nagy tömegrendezés lezárult.

A továbbiakban célzottan frissítendő:

- projektterv;
- projekt-térkép;
- engine-checkpoint;
- releváns README;
- közvetlenül érintett contract/státuszdokumentum.

---

## 7. Következő lépés

1. Combat + Pecsét official Core célzott rules-audit;
2. minimal production contract;
3. Reaction-integrációs pontok;
4. Codex implementation csak a contract után;
5. tests / determinism / Godot smoke / adversarial audit.

Reaction / Priority v1: `COMPLETE_AND_ACCEPTED`.
