# Aeterna Projekt

## Projektstátusz

Az **AETERNA** egy saját fejlesztésű fizikai és digitális kártyajáték-projekt.

A repository fő rétegei:

- hivatalos alapjátékos és kiegészítői szabályforrások;
- Google Sheets / XLSX kártyaadatbázis és LOOKUPS;
- Python adatpipeline és runtime package tooling;
- működő determinisztikus Python rules-engine referencia;
- Godot loader-, debug- és kliensalap;
- vizsgálandó Godot .NET/C# termékruntime;
- vizsgálandó Python sidecar termékruntime;
- régi Python szimulációs motor referenciaágként;
- dokumentációs, audit- és kártyatervezési rendszer.

A jelenlegi működő authoritative referenciaimplementáció:

> **az `Aeterna game engine/python/` alatt elkészült contract-first, headless és determinisztikus Python minimal rules engine.**

A végleges termékruntime nyelve még nincs kiválasztva.

A következő Codex-prioritás:

> **Python sidecar + Godot és Godot .NET/C# összehasonlító proof, tanulóprogram-audittal és Windows packaging vizsgálattal.**

A jelentős gameplay-engine bővítés a döntési kapu után folytatódik.

---

## Hivatalos szabályi alap

Aktív főforrások:

- `Aeterna dokumentációk/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
- `Aeterna dokumentációk/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

Ezek az elsődleges referenciák:

- szabályértelmezésnél;
- engine-fejlesztésnél;
- kártyatervezésnél;
- kártyaauditnál;
- canonical értékek és mechanikák ellenőrzésénél.

Régi dokumentum vagy legacy kód nem írhatja felül a két aktív főforrást.

---

## Hosszú távú digitális cél

Első nagy termékmérföldkő:

- `Aeterna game engine/docs/AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

A `0.0.1` a későbbi első zárt, használható és játszható tesztkiadás célverziója, többek között:

- egyszerű Windows-indítással;
- teljes ember–AI mérkőzéssel;
- játékos- és tesztelői móddal;
- több AI-nehézséggel;
- pakliszerkesztővel és gyűjteménnyel;
- tutorialokkal;
- logokkal és hibajelentéssel;
- reprodukálhatósági és replay-alappal;
- használható Godot felülettel.

A runtime-nyelvi döntés azért került előre, mert közvetlenül befolyásolja a Windows-csomagolást, a Godot-integrációt és a teljes gameplay-engine migrációs költségét.

---

## Aktuális projektirányító dokumentumok

### Projektirány és repository-térkép

- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.1.md`
- `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.4.md`
- `Aeterna dokumentációk/README.md`

### Runtime-nyelvi döntési kapu

- `Aeterna game engine/docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

### Aktuális engine- és technológiai állapot

- `Aeterna game engine/docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`
- `Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`
- `Aeterna game engine/docs/DECISION_MAP.md`
- `Aeterna game engine/docs/CURRENT_PROTOTYPE_STATUS.md`
- `Aeterna game engine/docs/CURRENT_CONTRACT_STATUS.md`
- `Aeterna game engine/docs/CURRENT_OPEN_QUESTIONS.md`

### Open Questions dokumentumpár

- `Aeterna game engine/docs/OPEN_QUESTIONS.md`
- `Aeterna game engine/docs/OPEN_QUESTIONS_DECISIONS.md`

A két fájl együtt olvasandó.

### Hosszú formájú háttérdokumentumok

- `Aeterna game engine/docs/CONTRACT_SPECIFICATION.md`
- `Aeterna game engine/docs/RUNTIME_PACKAGE_SPECIFICATION.md`
- `Aeterna game engine/docs/ABILITY_MODULE_SYSTEM.md`
- `Aeterna game engine/docs/PROTOTYPE_PLANS.md`
- `Aeterna game engine/docs/checkpoints/CHECKPOINTS.md`

Felváltott referenciák:

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.3.md`
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`

Státuszuk:

- `SUPERSEDED_REFERENCE`

---

## Repository fő területei

### `Aeterna dokumentációk/`

Tartalma:

- hivatalos szabályforrások;
- kártyaadatbázis;
- LOOKUPS;
- aktuális projektterv és projekt-térkép;
- munkafolyamat- és adatszabványok;
- kártyaaudit-dokumentumok;
- referencia- és archív review anyagok.

### `Aeterna game engine/`

Az új digitális programegység.

Fő részei:

- `python/`
- `Godot/`
- `docs/`

### Régi Python szimulációs motor

Státusza:

- `OLD_ENGINE_REVIEW`
- `OLD_ENGINE_REFERENCE`

Hasznos lehet:

- AI-vs-AI tapasztalatokhoz;
- balanszfigyeléshez;
- régi effectlogika összevetéséhez;
- diagnosztikai és naplózási mintákhoz.

Nem elsődleges új fejlesztési alap.

### Tanulóprogramok

A felhasználó által letöltött külső tanulóprogramok szándékosan nincsenek az AETERNA GitHub repositoryban licencbiztonsági okból.

A következő Codex-audit helyileg vizsgálja:

- licenceket;
- vizsgált verziókat;
- Python/C#/GDScript szerepeket;
- state authorityt;
- bridge-et;
- packaginget;
- clean-room módon felhasználható mintákat.

---

## Működő Python rules-engine referencia

Aktuális technikai bázis:

- `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`
- `Add minimal Wellspring resource contracts`

A minimal engine jelenleg tartalmaz:

- MatchState-et és PlayerState-et;
- state version guardot;
- card instance registryt;
- deck, hand és discard instance-listákat;
- draw és end-turn transitiont;
- typed `zone_move` és `turn_transition` eseményt;
- generic event envelope-ot;
- state invariant rendszert;
- determinisztikus AI episode trajectoryt;
- player-visible snapshot v2-t;
- hidden-information alapot;
- hat Áramlatos Domain topológiát;
- Domain occupancyt;
- player-visible public boardot;
- strukturális Entitás-placement optionöket;
- canonical `activity_state` mezőt;
- izolált Wellspring state-et;
- Magnitúdó- és elérhető Aura-summary contractot.

Aktív minimal actionök:

- `draw_card`
- `end_turn`

A Python engine megmarad:

- reference oracle;
- differential testing alap;
- AI/batch és tooling réteg;
- lehetséges termékruntime-jelölt.

---

## Runtime engine language decision gate

Kötelező fő jelöltek:

### Python sidecar + Godot

Bizonyítandó:

- stdin/stdout JSONL vagy localhost TCP;
- handshake;
- action request/response;
- process lifecycle;
- crash/version mismatch;
- Windows packaging.

### Godot .NET/C# authoritative runtime

Bizonyítandó:

- UI-tól független rules library;
- ugyanazon comparison scenario;
- unit tesztek;
- Godot .NET integráció;
- Windows export;
- Python reference outputtal való összevetés.

### Opcionális GDScript proof

Csak akkor készül, ha az audit vagy az első két proof eredménye indokolja.

### Embedded Python

Kutatási irány; jelenleg nem elsődleges 0.0.1 proof.

---

## Gameplay-engine queue a döntés után

1. Wellspring PlayerState- és MatchState-integráció;
2. player-visible Wellspring summary;
3. Beáramlás precondition;
4. Beáramlás transition és typed event;
5. Magnitúdó-preflight;
6. Aura-source és payment contract;
7. activity mutation transition;
8. Entitás kijátszási precondition;
9. `play_card` action;
10. hand → Domain transition;
11. entry-state;
12. teljesebb phase és priority rendszer.

A Wellspring feladat nem törlődött; a választott runtime-ágon folytatandó.

---

## Runtime package és adatpipeline

Adatút:

1. Google Sheets / XLSX szerkesztési forrás;
2. Python export és validáció;
3. runtime package;
4. rules engine és Godot loader;
5. player-facing és debug contractok;
6. későbbi interaktív kliens.

Lezárt elvek:

- Godot nem olvas közvetlenül XLSX-et;
- Godot nem canonical adatforrás;
- a validált runtime package a programadat-contract;
- kártyák és decklisták az 1.9v kártyaadatbázisból származnak;
- runtime lookupok a `LOOKUPS.xlsx` fájlból származnak;
- a Python adatpipeline a runtime-nyelvi döntéstől függetlenül megtartható.

Elsődleges publish runner:

- `Aeterna game engine/python/publish_runtime_package_to_godot.bat`

---

## Codex nélküli aktív munkasáv

- dokumentációs konszolidáció;
- `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` közös triázsa;
- tanulóprogram-forrás- és licencleltár előkészítése;
- comparison kritériumok pontosítása;
- `ABILITY_MODULE_SYSTEM.md` auditja;
- contract-specifikáció konszolidációja;
- hivatalos szabályforrásból megválaszolható kérdések ellenőrzése.

---

## Tesztelés

A `84a7e8f4` bázisnál:

- 59 Python tesztmodul futott izoláltan;
- 333 teszt volt zöld;
- minimal engine smoke zöld;
- AI-vs-AI text és JSON smoke zöld;
- két azonos JSON-epizód byte-szinten azonos.

Ismert monolitikus discovery-problémák:

- `test_finds_xlsx_files_only_in_source_directory`
- `test_lists_sheets_in_read_only_data_only_mode`

Ezek külön tesztinfrastruktúra-feladatként kezelendők.

---

## GitHub-munkarend

Alapelv:

- egy commit egy jól körülírható célt szolgáljon.

Ne keveredjen egy commitba:

- runtime implementáció;
- dokumentációs cleanup;
- kártyaadat-javítás;
- Godot UI-fejlesztés;
- generált output;
- általános tesztrendezés.

Külső kód vagy tanulóprogram esetén:

- licencellenőrzés;
- forrás és verzió rögzítése;
- attribution;
- alapértelmezetten clean-room megvalósítás.

---

## Jelenlegi rövid összefoglaló

**Hosszú távú cél:** AETERNA 0.0.1 zárt tesztkiadás  
**Aktuális projektterv:** v6.1  
**Aktuális projekt-térkép:** v1.4  
**Működő referencia:** Python minimal rules engine  
**Következő Codex-prioritás:** Python sidecar vs Godot .NET/C# comparison  
**Opcionális proof:** minimal GDScript transition  
**Gameplay queue első eleme a döntés után:** Wellspring runtime integráció  
**Codex nélküli aktív sáv:** dokumentáció, audit és döntés-előkészítés  
**Legutóbbi technikai bázis:** `84a7e8f4`  
**Ismert tesztprobléma:** két sorrendfüggő XLSX mock-eltérés
