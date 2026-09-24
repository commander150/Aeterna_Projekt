# AETERNA Game Engine – Dokumentációs index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.4
**Dátum:** 2026-09-05
**Státusz:** aktív engine-dokumentációs index
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9` – Combat + Pecsét Foundation C0–C6

Ez a fájl az `Aeterna game engine/docs/` aktív dokumentumainak szerepét, elsőbbségét és kapcsolatát rögzíti.

## Aktuális főállítások

- C#/.NET = production authority;
- Godot/GDScript = visual client;
- Python = external tooling/reference;
- sidecar proof = `COMPLETE_AND_FROZEN`;
- C# RuntimeCandidate = `COMPLETE_AND_ACCEPTED`;
- C.5B = `COMPLETE_AND_ACCEPTED`;
- korábbi production gameplay foundation slice = `COMPLETE_AND_ACCEPTED`;
- Explicit Phase Foundation v1 = `COMPLETE_AND_ACCEPTED`;
- Reaction / Priority Foundation v1 = `COMPLETE_AND_ACCEPTED`;
- Combat + Pecsét Foundation C0–C6 = `COMPLETE_AND_ACCEPTED`;
- terminal Aeternal / `MatchResult` core = active production;
- OQ = `52 answered / 15 partly_answered / 7 deferred / 0 open`;
- current next gate = `VS1_READINESS_REQUIRED`;
- teljes product/runtime továbbra sincs kész.

## 1. Elsődleges folytatási dokumentumok

- `../../project/status/checkpoints/ENGINE_CHECKPOINT.md` v2.0;
- `../../project/planning/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.9.md`;
- `../../Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.12.md`;
- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`.

Az első három current folytatási authority; a 0.0.1 dokumentum hosszú távú termékcél.

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

Current OQ aggregate:

`52 answered / 15 partly_answered / 7 deferred / 0 open`.

Reaction/Priority és Combat/Pecsét current core már nem OQ blocker.
Fennmaradó részleges gate többek között generic prevention/replacement,
compound choice, special Seal restore/ward, ability/content coverage és Expansion-specifikus kérdések.

## 5. Contract/specification

- `REACTION_PRIORITY_CONTRACT.md` – lezárt Reaction/Priority v1 contract;
- `CONTRACT_SPECIFICATION.md` – current contract meaning;
- `CONTRACT_STATUS.md` – current implementation status;
- `RUNTIME_PACKAGE_SPECIFICATION.md`;
- `ABILITY_MODULE_SYSTEM.md`;
- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md` – történeti consolidation reference;
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`.

A `CONTRACT_SPECIFICATION_MIGRATION_MAP.md` current contract sync után archive-candidate,
de csak cross-reference audit után mozgatható.

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

1. `rules/sources/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.5v.docx`;
2. `rules/sources/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4.1v.docx`;
3. explicit emberi döntés;
4. Open Questions decision log;
5. contract/specification;
6. implementáció mint technikai bizonyíték.

Technikai folytatásban:

1. `../../project/status/checkpoints/ENGINE_CHECKPOINT.md`;
2. aktuális projektterv;
3. projekt-térkép;
4. architecture/technology;
5. status/contract;
6. Open Questions;
7. történeti checkpoint/proof.

Archive/learning/blueprint nem current authority.

## 8. Dokumentumkezelési szabály

- meglévő aktív fájlt frissítünk;
- új fájl csak új önálló szerephez;
- verzió/dátum/státusz kötelező;
- fájlnévben verziózott current dokumentum ugyanazon fájl rename-jével lép új verzióra;
- korábbi current verziót a Git history őrzi;
- Archive csak valódi historical/deprecated/replaced szerepre;
- párhuzamos active copy ugyanarra a szerepre nem maradhat;
- nyitott kérdés és fontos döntés nem veszhet el;
- nem frissítünk mindent minden kisebb commit után;
- targeted patch → diff/consistency review → human commit/push.

## 9. Aktuális technikai állapot

Production C#-ban már megvan többek között:

- Wellspring / Beáramlás;
- Magnitúdó / Aura preflight;
- Domain / `play_card`;
- canonical ability/effect foundation;
- damage/vitals;
- continuous effects / modifier / keyword / duration;
- draw/reference runtime;
- Explicit Phase Foundation v1;
- Reaction / Priority Foundation v1;
- Combat + Pecsét Foundation C0–C6;
- terminal Aeternal / `MatchResult`.

Current production base:

`0862e1002dbef81ee203852714d377592272a0e9`

C0–C6 final acceptance:

- Debug/Release C#: `301/301 PASS`;
- targeted C6: `8/8 PASS`;
- determinism/reference: `100/100 PASS`;
- canonical bytes: `210676`;
- canonical SHA:
  `97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`;
- Python isolated: `465/465 PASS` + 5 skip;
- exporter: `23/23 PASS`;
- Godot positive/negative smoke: PASS;
- unresolved P0/P1: `0/0`.

## 10. Aktuális technikai folytatás

Current next gate:

`VS1_READINESS_REQUIRED`

Következő major product-facing cél:

`VS1 / M6 – első ténylegesen játszható vertical slice`

Canonical VS1 deckek:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

Sequence:

```text
VS1 card/mechanic readiness audit
→ csak tényleges blockerre finite contract/implementation
→ simple fair AI + match orchestration
→ minimal playable Godot
→ human-vs-AI full match
→ reproducible AI-vs-AI smoke
→ VS1 acceptance
```

Reaction/Priority és Combat/Pecsét már lezárt foundation, nem következő implementációs slice.
