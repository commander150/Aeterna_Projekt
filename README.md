# Aeterna Projekt

## Projektstátusz

Az **AETERNA** egy saját fejlesztésű fizikai és digitális kártyajáték-projekt.

A repository több, egymástól elválasztott, de hosszú távon összehangolt réteget tartalmaz:

- hivatalos alapjátékos és kiegészítői szabályforrások;
- Google Sheets / XLSX alapú kártyaadatbázis és LOOKUPS;
- új determinisztikus Python rules engine;
- runtime package és exportpipeline;
- Godot loader, debug- és későbbi kliensréteg;
- régi Python szimulációs motor referenciaágként;
- dokumentációs, audit- és kártyatervezési rendszer.

A projekt jelenlegi elsődleges programozási iránya:

> **az `Aeterna game engine/python/` alatt épülő contract-first, headless és determinisztikus AETERNA rules engine.**

A Godot ág továbbra is megtartandó fogyasztói és későbbi kliensréteg, de jelenleg nem az authoritative szabálymotor.

---

## Hivatalos szabályi alap

Az AETERNA aktív szabályi alapját két hivatalos főforrás alkotja:

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

A digitális programegység első nagy termékmérföldköve:

- `Aeterna game engine/docs/AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

A `0.0.1` nem a jelenlegi technikai schema- vagy prototípusverzió.

Ez a későbbi első zárt, használható és játszható tesztkiadás célverziója, többek között:

- egyszerű Windows-indítással;
- teljes ember–AI mérkőzéssel;
- játékos- és tesztelői móddal;
- több AI-nehézséggel;
- pakliszerkesztővel és gyűjteménnyel;
- tutorialokkal;
- logokkal és hibajelentéssel;
- reprodukálhatósági és replay-alappal;
- használható Godot felülettel.

A közvetlen jelenlegi cél továbbra is a stabil game engine.

---

## Aktuális projektirányító dokumentumok

Elsődleges projektterv:

- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`

Aktuális engine-folytatási pont:

- `Aeterna game engine/docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

További fontos dokumentumok:

- `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`
- `Aeterna dokumentációk/AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`
- `Aeterna dokumentációk/AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`
- `Aeterna dokumentációk/AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`
- `Aeterna game engine/docs/ARCHITECTURE.md`
- `Aeterna game engine/docs/CONTRACT_SPECIFICATION.md`
- `Aeterna game engine/docs/RUNTIME_PACKAGE_SPECIFICATION.md`
- `Aeterna game engine/docs/OPEN_QUESTIONS.md`
- `Aeterna game engine/docs/checkpoints/CHECKPOINTS.md`

A korábbi `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md` státusza:

- `SUPERSEDED_REFERENCE`

---

## Repository fő rétegei

### `Aeterna dokumentációk/`

Tartalma:

- hivatalos szabályforrások;
- kártyaadatbázis;
- LOOKUPS;
- aktuális projektterv;
- projekt-térkép;
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

### `Archive/`

Történeti, régi vagy összevetési anyagok helye.

Az archív tartalom nem automatikusan törlendő, de nem tekintendő aktív canonical forrásnak.

---

## Új Python rules engine

Az aktív engine jelenlegi technikai bázisa:

- `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`
- `Add minimal Wellspring resource contracts`

A minimal engine jelenleg már tartalmaz:

- MatchState-et és PlayerState-et;
- state version guardot;
- card instance registryt;
- deck, hand és discard instance-listákat;
- draw transitiont;
- end-turn transitiont;
- typed `zone_move` eseményt;
- typed `turn_transition` eseményt;
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

Még nincs runtime gameplayként:

- Beáramlás;
- Aura-payment;
- `play_card`;
- teljes phase és priority;
- combat;
- ability executor;
- Pecsét-state;
- győzelmi feltétel.

---

## Következő engine-fejlesztési lánc

A javasolt sorrend:

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

A lánc végét nem szabad a korábbi függőségek nélkül implementálni.

---

## Runtime package és adatpipeline

Az adatút fő elve:

1. Google Sheets / XLSX szerkesztési forrás;
2. Python export és validáció;
3. runtime package;
4. Godot loader és registry;
5. player-facing és debug contractok;
6. későbbi interaktív kliens.

Fontos szabályok:

- Godot nem olvas közvetlenül XLSX-et;
- Godot nem canonical adatforrás;
- a validált runtime package a Python és Godot közötti adatcontract;
- kártyák és decklisták az 1.9v kártyaadatbázisból származnak;
- runtime lookupok a `LOOKUPS.xlsx` fájlból származnak.

Elsődleges fejlesztői publish runner:

- `Aeterna game engine/python/publish_runtime_package_to_godot.bat`

Az exporter és runtime package pipeline aktív, de nem ez a jelenlegi rules-engine feladatsor közvetlen fő prioritása.

---

## Godot ág

A Godot projekt helye:

- `Aeterna game engine/Godot/`

Jelenlegi szerepe:

- runtime package betöltés;
- registry-k;
- sample és debug contractok;
- snapshot, legal action és event log debug nézetek;
- headless smoke tesztek;
- későbbi játékos UI alapja.

Jelenlegi elhatárolás:

- a Python rules engine authoritative;
- a Godot később player-visible állapotot jelenít meg;
- a Godot action requestet küld;
- a Godot nem duplikálhat szabálylegalitást.

---

## Kártyaadatbázis

Aktív munkaforrás:

- `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`

Runtime lookupforrás:

- `Aeterna dokumentációk/LOOKUPS.xlsx`

A kártyaaudit külön munkasáv.

Külön kell kezelni:

- kártyaadat-hibát;
- structured mezőhibát;
- szabályértelmezési hibát;
- engine-hiányt;
- balanszgyanút.

Kártyaadat-javítás és engine-contract módosítás ne keveredjen ugyanabba a commitba.

---

## Tesztelés

A `84a7e8f4` technikai bázisnál:

- 59 Python tesztmodul futott izoláltan;
- 333 teszt volt zöld;
- minimal engine smoke zöld;
- AI-vs-AI text és JSON smoke zöld;
- két azonos JSON-epizód byte-szinten azonos.

A monolitikus unittest discoveryben két ismert sorrendfüggő XLSX mock-probléma marad:

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

Minden engine-lépéshez tartozzon:

- célzott teszt;
- regressziós kör;
- izolált teljes tesztfutás;
- smoke futás;
- determinisztikus AI-ellenőrzés;
- git status ellenőrzés.

---

## Jelenlegi rövid összefoglaló

**Elsődleges programozási irány:** determinisztikus Python rules engine  
**Hosszú távú cél:** AETERNA 0.0.1 zárt tesztkiadás  
**Aktuális projektterv:** v6.0  
**Aktuális engine-checkpoint:** `CURRENT_ENGINE_CHECKPOINT.md`  
**Legutóbbi technikai bázis:** `84a7e8f4`  
**Következő programozási feladat:** Wellspring runtime integráció  
**Godot:** fogyasztói és későbbi kliensréteg  
**Régi engine:** review és referencia  
**Ismert tesztprobléma:** két sorrendfüggő XLSX mock-eltérés
