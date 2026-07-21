# Aeterna Projekt

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.0  
**Dátum:** 2026-07-21  
**Státusz:** aktív repository-szintű belépési dokumentum  
**Aktuális repository HEAD:** `32a0cbea24c82dda440f1a053b454ef03949d8ae` – `docs update 2`  
**Aktuális C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Az **AETERNA** saját fejlesztésű fizikai és digitális gyűjtögetős kártyajáték-projekt.

A repository fő rétegei:

- hivatalos alapjátékos és kiegészítői szabályforrások;
- Google Sheets / XLSX kártyaadatbázis és LOOKUPS;
- Python adat-, export-, audit-, AI- és batch-tooling;
- Python minimal rules-engine referencia;
- Godot loader-, debug-, vizuális és későbbi player-client réteg;
- elfogadott Godot .NET/C# in-process runtime proof;
- tervezett production C# authoritative engine;
- dokumentációs, kártyatervezési és auditfolyamatok;
- archív és generált referenciaanyagok.

---

## 1. Elfogadott digitális architektúra

```text
Godot / GDScript
    = vizuális kliens, scene, input, UI, animáció és debug

C# / .NET
    = egyetlen production authoritative rules engine

Python
    = adatpipeline, audit, fixture, AI, batch, simulation és elemzőtooling
```

Következmények:

- a Godot UI nem lehet szabályforrás;
- a Python nem marad második production authoritative motor;
- a C# engine birtokolja a kanonikus MatchState-et;
- a UI és az AI legal actionből választ és action requestet küld;
- az engine minden requestet újra validál;
- player-facing output nem szivárogtathat rejtett információt.

Bizonyított proofok:

- Python–Godot sidecar: `COMPLETE_AND_FROZEN`;
- Godot .NET/C# in-process candidate: `COMPLETE_AND_ACCEPTED`.

Közös canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

A production `Aeterna.Engine` még nem létezik.

---

## 2. Hivatalos szabályi és adatforrások

Aktív főforrások:

- `Aeterna dokumentációk/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`;
- `Aeterna dokumentációk/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`;
- `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `Aeterna dokumentációk/LOOKUPS.xlsx`.

A két DOCX az elsődleges szabályforrás. A kód, a runtime package, a Python referencia és a régi dokumentumok nem írhatják felül őket.

---

## 3. Aktuális projektirányító dokumentumok

### Projekt- és fájlszint

- `Aeterna dokumentációk/README.md`;
- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`;
- `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`.

### Engine-szint

- `Aeterna game engine/README.md`;
- `Aeterna game engine/docs/README.md`;
- `Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`;
- `Aeterna game engine/docs/ARCHITECTURE.md`;
- `Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`;
- `Aeterna game engine/docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `Aeterna game engine/docs/DECISION_MAP.md`.

### Aktuális technikai státusz

- `Aeterna game engine/docs/PROTOTYPE_STATUS.md`;
- `Aeterna game engine/docs/RUNTIME_PACKAGE_STATUS.md`;
- `Aeterna game engine/docs/CONTRACT_STATUS.md`.

### Open Questions kérdés–válasz pár

- `Aeterna game engine/docs/OPEN_QUESTIONS.md`;
- `Aeterna game engine/docs/OPEN_QUESTIONS_DECISIONS.md`.

A két Open Questions-fájl szándékosan külön marad.

---

## 4. Repository fő területei

### `Aeterna dokumentációk/`

Tartalma:

- hivatalos szabályforrások;
- kártyaadatbázis és LOOKUPS;
- projektterv és projekt-térkép;
- munkafolyamat-, Excel- és auditstandardok;
- reference-, archive_review- és generated_review-anyagok.

### `Aeterna game engine/`

Az új digitális programegység.

Fő részei:

- `C#/` – elfogadott proof és későbbi production projektek;
- `python/` – reference engine és külső tooling;
- `Godot/` – vizuális kliens, loader, debug és C# bridge;
- `docs/` – aktív engine-dokumentáció;
- `runtime_comparison/` – comparison fixture és artifactok.

### `Archive/`

Régi motorok és történeti anyagok. Nem aktív production forrás, de audit- és referenciaértéke lehet.

---

## 5. Aktuális fejlesztési állapot

### Elkészült

- runtime package build és publish pipeline;
- Godot package loader és registry;
- snapshot/legal action/event debug foundation;
- Python minimal reference engine;
- card instance, zone move, state version és hidden-information alap;
- Python-sidecar proof;
- C# in-process proof;
- runtime-nyelvi döntés;
- C.5A production architecture;
- engine-dokumentáció első nagy konszolidációs köre.

### Következő kódolási szakasz

**C.5B – Production C# Engine Foundation**

Státusz:

- `READY_FOR_IMPLEMENTATION`;
- `PAUSED_CODEX_QUOTA`.

Nem tartalmaz új gameplayt; a proof draw/end-turn contractját viszi át production projektekbe.

### C.5B utáni gameplay-sorrend

1. Wellspring;
2. player-visible Wellspring;
3. `infusion` / Beáramlás;
4. Magnitúdó;
5. Aura-payment;
6. simple Entity `play_card`;
7. Domain placement;
8. phase/priority;
9. reaction;
10. combat;
11. ability execution;
12. victory/defeat.

---

## 6. Dokumentációs cleanup

Az aktuális dokumentációs munkaszakasz célja:

- a régi `CURRENT_*` elődök eltávolítása;
- a három checkpointváltozat egyetlen aktív `ENGINE_CHECKPOINT.md` fájlra szűkítése;
- a projektterv egyetlen helyen tartása;
- a projekt-térkép v1.5 kialakítása;
- gyökérszintű, elavult állapotösszefoglalók eltávolítása;
- hivatkozások és verzióblokkok végső ellenőrzése;
- az `Aeterna dokumentációk/` teljes következő auditja.

A pontos megtartási és törlési lista:

- `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`.

---

## 7. Dokumentumelsőbbség

1. hivatalos szabályfőforrások;
2. `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`;
3. aktuális projektterv és projekt-térkép;
4. aktív engine-checkpoint;
5. architektúra- és technológiai döntések;
6. aktuális státuszdokumentumok;
7. Open Questions kérdés–válasz pár;
8. hosszú specificationök;
9. történeti, reference és archive anyagok.

A működő kód technikai tényt bizonyíthat, de játékszabályt nem írhat felül.

---

## 8. Futtatás és tesztelés

A repository több elkülönített technikai réteget tartalmaz; nincs egyetlen mindenre érvényes gyökérszintű `python main.py` futási út.

Az aktuális futtatási és tesztelési útvonalakat az engine README és a megfelelő részrendszer dokumentációja tartalmazza:

- `Aeterna game engine/README.md`;
- `Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`.

A production C# engine létrejöttéig a Python és C# proof futtatási útvonalai referencia- és fejlesztői célúak.
