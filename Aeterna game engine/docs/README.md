# AETERNA Game Engine – Dokumentációs index

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.9  
**Dátum:** 2026-07-21  
**Státusz:** aktív engine-dokumentációs index  
**Aktuális repository HEAD:** `32a0cbea24c82dda440f1a053b454ef03949d8ae` – `docs update 2`  
**Aktuális C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Ez a fájl az `Aeterna game engine/docs/` aktív dokumentumainak szerepét, elsőbbségét és kapcsolatát rögzíti.

## Aktuális főállítások

- A runtime-nyelvi döntési kapu lezárult.
- A production authoritative runtime C#/.NET.
- A Godot/GDScript a vizuális kliens- és adapterréteg.
- A Python külső adat-, audit-, fixture-, AI-, batch- és elemzőtooling, valamint referenciaimplementáció.
- A Python-sidecar proof `COMPLETE_AND_FROZEN`.
- A C# in-process runtime proof `COMPLETE_AND_ACCEPTED`.
- A production C# engine még nem létezik; a C.5B implementációra előkészített, Codex-keret miatt szünetelő feladat.
- Az `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` aktív kanonikus kérdés–válasz dokumentumpár.
- A korábbi `CURRENT_OPEN_QUESTIONS.md` tartalma a 2.0-s párba beolvadt.
- Az aktív dokumentumokból az indokolatlan `CURRENT_` előtag eltávolítandó; a pontos előd–utód lista elkészült.

---

## 1. Elsődleges folytatási és irányító dokumentumok

### 1.1 Aktív technikai checkpoint

- `checkpoints/ENGINE_CHECKPOINT.md`

Szerepe:

- elsődleges technikai folytatási pont;
- bizonyított Python-, sidecar- és C# állapot;
- lezárt architektúradöntés;
- C.5A/C.5B státusz;
- dokumentációs átadás és következő biztonságos lépés.

### 1.2 Aktuális projektterv

- `../../Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`
- `../../Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`

Szerepe:

- projektirány;
- prioritások;
- roadmap;
- Codex nélküli munkasáv;
- dokumentációs konszolidáció.

### 1.3 Hosszú távú termékcél

- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

Szerepe:

- az első zárt, használható és játszható tesztkiadás célállapota;
- nem napi tasklista;
- nem írja felül a hivatalos szabályforrásokat.

---

## 2. Kanonikus architektúra- és technológiai dokumentumok

### `ARCHITECTURE.md`

Az aktív rendszerarchitektúra:

- Godot/GDScript visual client;
- C# authoritative engine;
- Python external tooling;
- authority-, projection-, determinism- és packaging-határok.

### `TECHNOLOGY_DECISIONS.md`

Az elfogadott technológiai döntések nyilvántartása:

- contract-first;
- egyetlen authority;
- C# runtime;
- Python-sidecar befagyasztása;
- Python tartós tooling-szerepe;
- Python–C# headless kapcsolat;
- dokumentumkezelési szabály.

### `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

Lezárt technológiai döntési kapu:

- a két fő proof eredménye;
- canonical fixture és SHA;
- döntési indok;
- újranyitási feltételek;
- production C# migrációs szabályok.

### `DECISION_MAP.md`

Rövid operatív döntési és prioritástérkép.

---

## 3. Aktív státuszdokumentumok

### `PROTOTYPE_STATUS.md`

Elkülöníti:

- runtime package/Godot alap;
- Python reference engine;
- befagyasztott sidecar proof;
- elfogadott C# candidate proof;
- még nem létező production C# engine.

Felváltja:

- felváltott előd: `CURRENT_PROTOTYPE_STATUS.md` – eltávolítandó

### `RUNTIME_PACKAGE_STATUS.md`

Rögzíti:

- XLSX/LOOKUPS forrásokat;
- Python build/publish útvonalat;
- Godot consumption copyt;
- canonical `wellspring` és `infusion` értékeket;
- package identity és payment-adat nyitott feladatait.

Felváltja:

- felváltott előd: `CURRENT_RUNTIME_PACKAGE_STATUS.md` – eltávolítandó

### `CONTRACT_STATUS.md`

Rögzíti:

- Python reference contractokat;
- C# candidate proofban bizonyított contractokat;
- C.5B production contractokat;
- későbbi gameplay-contractokat.

Felváltja:

- felváltott előd: `CURRENT_CONTRACT_STATUS.md` – eltávolítandó

---

## 4. Open Questions kérdés–válasz rendszer

### `OPEN_QUESTIONS.md`

**Státusz:** aktív kanonikus kérdésregiszter  
**Verzió:** 2.0

Tartalmaz:

- 74 egyedi OQ-azonosítót;
- aktuális `open`, `partly_answered`, `deferred` vagy `answered` státuszt;
- rövid fennmaradó döntési kaput;
- hivatkozást a válasznaplóra.

### `OPEN_QUESTIONS_DECISIONS.md`

**Státusz:** aktív kanonikus válasz- és döntésnapló  
**Verzió:** 2.0

Tartalmaz:

- lezárt runtime-architektúradöntést;
- dokumentációs és pipeline-döntéseket;
- projection-, payment-, infusion-, event-, diagnostics-, ability-, AI- és rules-audit irányokat;
- a korábbi current triázs `CQ-*` döntéseit.

### Megszüntetendő átmeneti fájl

- beolvasztott előd: `CURRENT_OPEN_QUESTIONS.md` – eltávolítandó

Csak az új kérdés–válasz pár és minden belső hivatkozás ellenőrzése után távolítható el.

---

## 5. Contract- és specification dokumentumok

### `CONTRACT_SPECIFICATION.md`

Technológiafüggetlen, hosszú formájú contract-specifikáció.

Aktuális megvalósítási státusz:

- `CONTRACT_STATUS.md`

### `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`

Történeti konszolidációs és migrációs referencia.

A végső dokumentumauditban újra ellenőrizendő, hogy maradt-e aktív szerepe vagy történeti státuszt kapjon.

### `RUNTIME_PACKAGE_SPECIFICATION.md`

A statikus runtime package hosszú formájú specifikációja.

Aktuális státusz:

- `RUNTIME_PACKAGE_STATUS.md`

### `ABILITY_MODULE_SYSTEM.md`

A későbbi ability registry, support, module és execution plan rendszer referenciája.

Jelenleg nincs production ability executor.

### `RUNTIME_COMPARISON_FIXTURE_SPEC.md`

A lezárt runtime comparison közös fixture-specifikációja.

Megmarad regressziós és production C# migrációs referenciaként.

---

## 6. Proof-, audit- és történeti dokumentumok

### Runtime proofok

- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`
- Python-sidecar proof dokumentumok és artifactok
- C# RuntimeCandidate proof dokumentumok és artifactok

### Tanulóprogram-audit

- `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`
- `LEARNING_PROJECT_AUDIT_QUEUE.md`

A runtime-nyelvi döntés lezárult, ezért ezek nem blokkolják a C.5B-t. Történeti, licenc- és clean-room referenciaértékük megmarad.

### Checkpointnapló

- `checkpoints/CHECKPOINTS.md`

Történeti mérföldkőnapló; nem írhatja felül az aktív `ENGINE_CHECKPOINT.md` fájlt.

---

## 7. Dokumentumelsőbbség

Technikai folytatásnál:

1. hivatalos 1.4v szabályforrások;
2. `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`;
3. `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
4. `checkpoints/ENGINE_CHECKPOINT.md`;
5. `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`;
6. `ARCHITECTURE.md`;
7. `TECHNOLOGY_DECISIONS.md`;
8. `DECISION_MAP.md`;
9. `CONTRACT_STATUS.md`;
10. `RUNTIME_PACKAGE_STATUS.md`;
11. `PROTOTYPE_STATUS.md`;
12. `OPEN_QUESTIONS.md` + `OPEN_QUESTIONS_DECISIONS.md`;
13. hosszú specificationök;
14. történeti checkpointok, prooftervek és régi dokumentumok.

A működő kód és tesztek technikai tényt bizonyíthatnak, de nem írhatják felül a hivatalos játékszabályt.

---

## 8. Dokumentumkezelési szabály

- Meglévő aktív fájlt frissítünk.
- Új fájl csak önálló canonical szerep esetén készül.
- Minden aktív fájlnak van verziója, dátuma és státusza.
- `CURRENT_` előtag nem marad aktív fájlnévben indokolatlanul.
- Párhuzamos fájloknál előbb tartalmi összevetés és merge-döntés kell.
- Nyitott kérdés vagy korábbi döntés nem veszhet el.
- Törlés/archiválás csak teljes audit és jóváhagyás után.
- Az engine-dokumentáció után az `Aeterna dokumentációk/` mappát is auditálni kell.
- A két mappa után keresztmappa-ellenőrzés szükséges.

---

## 9. Aktuális dokumentációs munkasorrend

Elkészült helyi utódfájlok:

- `ARCHITECTURE.md`
- `TECHNOLOGY_DECISIONS.md`
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `DECISION_MAP.md`
- `PROTOTYPE_STATUS.md`
- `RUNTIME_PACKAGE_STATUS.md`
- `CONTRACT_STATUS.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `checkpoints/ENGINE_CHECKPOINT.md`
- `checkpoints/README.md`
- jelen `docs/README.md`

Következik:

1. további docs-fájlok verzió- és tartalmi auditja;
2. specificationök belső hivatkozásainak frissítése;
3. engine-dokumentációs teljes inventory;
4. eltávolítandó/archiválandó fájlok listája;
5. `Aeterna dokumentációk/` külön auditja;
6. keresztmappa-ellenőrzés;
7. végső commit előtti teljes átadási audit.

---

## 10. Végső cleanup-jelöltek

A következő fájlok a kijelölt utódok és hivatkozások ellenőrzése után eltávolítandók:

- `CURRENT_PROTOTYPE_STATUS.md`;
- `CURRENT_RUNTIME_PACKAGE_STATUS.md`;
- `CURRENT_CONTRACT_STATUS.md`;
- `CURRENT_OPEN_QUESTIONS.md`;
- `ENGINE_OBJECT_IDENTITY_AND_ZONE_MOVE_PLAN_v0.1.md`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md` ebből a mappából;
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`;
- `checkpoints/AETERNA_CURRENT_ENGINE_CHECKPOINT_v1.1_2026-07-20.md`.

Megtartandó történeti, de nem közvetlen duplikátum:

- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`;
- `PROTOTYPE_PLANS.md`;
- `LEARNING_PROJECT_AUDIT_QUEUE.md`;
- `checkpoints/CHECKPOINTS.md`;
- `checkpoints/README.md`.

A teljes repository cleanup-térkép:

- `../../Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.5.md`.
