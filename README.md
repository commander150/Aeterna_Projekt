# Aeterna Projekt

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.7
**Dátum:** 2026-09-05
**Státusz:** aktív repository-szintű belépési dokumentum
**Előző aktív verzió:** 2.6 (Git history)
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9` – Combat + Pecsét Foundation C0–C6

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

Current szabályforrás:

- `rules/sources/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.5v.docx`;
- `rules/sources/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4.1v.docx`.

Aktív adatút:

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `LOOKUPS.xlsx`;
- `data/canonical/CARDDATABASE.xlsx`;
- `data/canonical/REGISTRY.xlsx`;
- validált canonical export/runtime package.

A rules authority DOCX, a runtime package derived programadat. Egyik sem helyettesíti a másikat.

## 3. Aktuális projektirány

Elsődleges current projektirányító réteg:

- `project/planning/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.9.md`;
- `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.12.md`;
- `project/status/checkpoints/ENGINE_CHECKPOINT.md` v2.0.

Aktuális engine-státusz és döntések:

- `ARCHITECTURE.md`;
- `TECHNOLOGY_DECISIONS.md`;
- `DECISION_MAP.md`;
- `PROTOTYPE_STATUS.md`;
- `RUNTIME_PACKAGE_STATUS.md`;
- `CONTRACT_STATUS.md`;
- `CONTRACT_SPECIFICATION.md`;
- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

Current OQ aggregate:

`52 answered / 15 partly_answered / 7 deferred / 0 open`.

## 4. Repository fő területei

- `rules/` – hivatalos szabályforrások.
- `design/` – kártyatervezési, koncepció-, névadási és kutatási tudásanyagok.
- `Aeterna dokumentációk/` – adat-, projekt- és munkafolyamat-források.
- `Aeterna game engine/` – C# engine, Python tooling/reference, Godot kliens, docs és fixture-ök.
- `learning/` – clean-room source registry, izolált project analyses és cross-project synthesis.
- `Aeterna game engine/docs/blueprints/` – AETERNA architecture proposal réteg.
- `Archive/` – történeti anyagok.

Az archívum és a learning réteg nem aktív authority.

---

## 5. Aktuális fejlesztési állapot

Lezárt production foundation többek között:

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
- Combat + Pecsét Foundation C0–C6;
- terminal Aeternal / `MatchResult` victory core.

Aktuális canonical phase flow:

`awakening -> infusion -> manifestation -> incursion -> distribution`

Current production mérföldkő:

`0862e1002dbef81ee203852714d377592272a0e9`

Combat + Pecsét C0–C6 final acceptance:

- Debug/Release C#: `301/301 PASS`;
- targeted C6: `8/8 PASS`;
- determinism/reference: `100/100 PASS`;
- canonical bytes: `210676`;
- canonical SHA:
  `97af60f42b78211bb35f235b5df81ddda48e72d74e8318b627893c86b16a1ee8`;
- Python isolated: `465/465 PASS` + 5 skip;
- exporter: `23/23 PASS`;
- Godot C# positive/negative smoke: PASS;
- unresolved P0/P1 debt: `0/0`.

Current state:

`COMBAT_AND_SEAL_FOUNDATION_C0_C6 = COMPLETE_AND_ACCEPTED`

Továbbra sem teljes többek között:

- Refresh Penalty;
- generic prevention/replacement;
- teljes compound non-Reaction choice;
- Hasítás runtime;
- full Burst/Jel runtime;
- teljes ability/content coverage;
- replay runner;
- production AI-vs-AI orchestration;
- minimal playable Godot UI;
- final Windows packaging;
- profile/save/tutorial/collection/economy.

Ezek közül nem mind VS1-blocker.

## 6. Dokumentációs szabály

A nagy tömegrendezés lezárult.

Current szerkesztési elv:

- meglévő aktív dokumentum célzottan frissül;
- párhuzamos új active copy nem készül ugyanarra a szerepre;
- fájlnévben verziózott current dokumentum ugyanazon fájl rename-jével lép új verzióra;
- Git history őrzi a korábbi current verziót;
- Archive történeti evidence, nem automatikus current authority;
- learning/synthesis/blueprint evidence/proposal, nem rules authority.

Current dokumentációs szinkron history-aware, célzott patch + diff review módszerrel történik.

## 7. Következő lépés

Következő major product-facing cél:

`VS1 / M6 – első ténylegesen játszható vertical slice`

Canonical VS1 deckek:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

Current sequence:

```text
VS1 card/mechanic readiness audit
→ csak tényleges blockerre finite contract/implementation
→ simple fair AI + match orchestration
→ minimal playable Godot
→ human-vs-AI teljes match
→ reproducible AI-vs-AI smoke
→ VS1 acceptance
→ szükséges köztes mérföldkövek
→ AETERNA 0.0.1
```

VS1 előtt csak az a capability kötelező, amelyet a két canonical VS1 deck ténylegesen igényel,
vagy amely általános rules-correct / deterministic / viewer-safe invariáns.

Reaction / Priority v1: `COMPLETE_AND_ACCEPTED`.

Combat + Pecsét Foundation C0–C6: `COMPLETE_AND_ACCEPTED`.
