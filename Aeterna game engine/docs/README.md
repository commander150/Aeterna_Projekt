# AETERNA Game Engine – Dokumentációs index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.3
**Dátum:** 2026-08-16
**Státusz:** aktív engine-dokumentációs index
**Szinkronizációs repository-bázis:** `14e315d3f04f5baddb547dcb767c8b156b02551f`
**Production engine mérföldkő:** `2608345b61526097fc0b118f05461f92cfed0a95`

Ez a fájl az `Aeterna game engine/docs/` aktív dokumentumainak szerepét, elsőbbségét és kapcsolatát rögzíti.

## Aktuális főállítások

- C#/.NET = production authority;
- Godot/GDScript = visual client;
- Python = external tooling/reference;
- sidecar proof = `COMPLETE_AND_FROZEN`;
- C# RuntimeCandidate = `COMPLETE_AND_ACCEPTED`;
- C.5B = `COMPLETE_AND_ACCEPTED`;
- első production gameplay vertical slice = elkészült;
- Explicit Phase Foundation v1 = `COMPLETE_AND_ACCEPTED`;
- learning/synthesis/blueprint handoff = committed;
- OQ v2.2 = `50/17/7/0`;
- Reaction contract = `ACCEPTED_FOR_IMPLEMENTATION`; Reaction implementation = `NOT_STARTED / NEXT`;
- teljes gameplay-engine még nincs kész.

---

## 1. Elsődleges folytatási dokumentumok

- `checkpoints/ENGINE_CHECKPOINT.md`;
- `../../Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.7.md`;
- `../../Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.10.md`;
- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`.

Az első három aktuális folytatás; a 0.0.1 dokumentum hosszú távú termékcél.

---

## 2. Architektúra és döntések

- `ARCHITECTURE.md`;
- `TECHNOLOGY_DECISIONS.md`;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `DECISION_MAP.md`.

---

## 3. Aktív státusz

- `PROTOTYPE_STATUS.md`;
- `RUNTIME_PACKAGE_STATUS.md`;
- `CONTRACT_STATUS.md`.

---

## 4. Open Questions

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

A Reaction/Priority OQ-réteg a hivatalos 1.4.3v alapelveihez igazítva lett. Current OQ: `50/17/7/0`. A minimal Reaction/Priority v1 contract elfogadott; következő lépés a production C# implementation.

---

## 5. Contract/specification

- `REACTION_PRIORITY_CONTRACT.md` – accepted Reaction/Priority v1 implementation contract.
- `CONTRACT_SPECIFICATION.md`;
- `RUNTIME_PACKAGE_SPECIFICATION.md`;
- `ABILITY_MODULE_SYSTEM.md`;
- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`;
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`.

Az `ABILITY_MODULE_SYSTEM.md` implementációs státusza frissítve lett a meglévő production ability/effect foundationhöz.

---

## 6. Proof- és történeti réteg

Megmarad:

- Python reference;
- sidecar proof;
- C# RuntimeCandidate proof;
- runtime comparison artifactok;
- `checkpoints/CHECKPOINTS.md`.

A történeti proof nem írhatja felül az aktív checkpointot.

---

## 7. Dokumentumelsőbbség

Szabályi kérdésben:

1. hivatalos 1.4.3v alapjáték-forrás;
2. kiegészítő főforrás;
3. explicit emberi döntés;
4. Open Questions decision log;
5. contract/specification;
6. implementáció mint technikai bizonyíték.

Technikai folytatásban:

1. `checkpoints/ENGINE_CHECKPOINT.md`;
2. aktuális projektterv;
3. projekt-térkép;
4. architecture/technology;
5. status/contract;
6. Open Questions;
7. történeti checkpoint/proof.

---

## 8. Dokumentumkezelési szabály

- meglévő aktív fájlt frissítünk;
- új fájl csak új önálló szerephez;
- verzió/dátum/státusz kötelező;
- párhuzamos fájl előtt tartalmi összevetés;
- nyitott kérdés és fontos döntés nem veszhet el;
- nem frissítünk mindent minden kisebb commit után.

---

## 9. Aktuális technikai állapot

Production C#-ban már megvan:

- Wellspring / Beáramlás;
- Magnitúdó / Aura preflight;
- Domain / `play_card`;
- canonical ability/effect foundation;
- damage/vitals;
- continuous effects / modifier / keyword / duration;
- draw/reference runtime;
- explicit phase lifecycle.

Szinkronizációs documentation/evidence base:

`14e315d3f04f5baddb547dcb767c8b156b02551f`

Production implementation base:

`2608345b61526097fc0b118f05461f92cfed0a95`

Lezáró tesztállapot:

- Debug `222/222 PASS`;
- Release `222/222 PASS`;
- determinism `100/100 PASS`;
- Godot smoke PASS.

---

## 10. Aktuális technikai folytatás

**Reaction / Priority Foundation v1 – production implementation**

Nem közvetlen Codex-kódolással indul.

Combat külön későbbi slice.
