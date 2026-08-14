# AETERNA Game Engine – Runtime Package Specification

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.0  
**Dátum:** 2026-07-20  
**Státusz:** aktív kanonikus runtime package-specifikáció  
**Aktuális státuszfájl:** `RUNTIME_PACKAGE_STATUS.md`  
**Aktuális repository-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Ez a dokumentum az AETERNA statikus runtime package rétegének kötelező jelentését, határait és buildelveit rögzíti.

Nem:

- hivatalos játékszabály;
- kártyaadatbázis;
- nyers exportleírás;
- MatchState;
- save game;
- snapshot;
- event log;
- rules engine;
- ability executor.

A runtime package az ember által szerkesztett forrásokból előállított, validált, verziózott és programfogyasztásra alkalmas statikus adatcsomag.

Kapcsolódó aktív dokumentumok:

- `RUNTIME_PACKAGE_STATUS.md`
- `ARCHITECTURE.md`
- `TECHNOLOGY_DECISIONS.md`
- `CONTRACT_SPECIFICATION.md`
- `CONTRACT_STATUS.md`
- `ABILITY_MODULE_SYSTEM.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `checkpoints/ENGINE_CHECKPOINT.md`

---

## 1. Authority és forráselsőbbség

A runtime package nem írhatja felül a hivatalos játékszabályokat.

Adat- és szabályi elsőbbség:

1. hivatalos 1.4v szabályfőforrások;
2. elfogadott, verziózott emberi döntések;
3. Google Sheets szerkesztési forrás;
4. lokális XLSX munkaforrás;
5. külön `LOOKUPS.xlsx`;
6. Python normalizálás és validáció;
7. runtime package;
8. Godot-, C#- és Python-fogyasztók.

Eltérés esetén a package build álljon meg vagy adjon blocking diagnosticot; a builder nem találgathat új szabályt.

---

## 2. Elfogadott adatút

```text
Google Sheets
        ↓
lokális XLSX munkaforrások
        ↓
Python export és source adapterek
        ↓
normalizálás és validáció
        ↓
runtime package candidate
        ↓
blocking publish gate
        ↓
Godot consumption copy / C# engine input
```

Aktív források:

- kártyák és decklisták:
  `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- runtime lookupok:
  `Aeterna dokumentációk/LOOKUPS.xlsx`;
- fő kártyalap:
  `7. EXPORT_RUNTIME`;
- aktív lookup-lapok:
  `RUNTIME_CORE`, `RUNTIME_ABILITY`;
- alias- és normalizációs forrás:
  `RUNTIME_LEGACY_ALIAS`.

A builder több külön forrásból dolgozhat. Nem feltételezheti, hogy minden adat egyetlen workbookban található.

---

## 3. Szerkesztési forrás és runtime adat elhatárolása

A szerkesztési forrás tartalmazhat:

- workflow mezőt;
- auditstátuszt;
- megjegyzést;
- részben feldolgozatlan structured értéket;
- legacy aliast;
- nyomdai vagy termékmetaadatot;
- javítás alatt álló kártyát.

A runtime package nem tartalmazhat tisztázatlanul:

- workflow-only értéket runtime mezőben;
- ismeretlen vagy inaktív enumértéket aktív runtime rekordban;
- veszélyes legacy aliast;
- régi Aeternal/Pecsét HP-modellt;
- hiányzó kötelező runtime mezőt;
- hibás többértékű delimitert;
- futtathatóként jelölt, de unsupported képességet;
- szerkesztési megjegyzést vagy belső auditjegyzetet gameplay-adatként.

A runtime package generált output. Nem kézzel szerkesztett canonical forrás.

---

## 4. Kötelező package-szerkezet

A jelenlegi többfájlos package fő elemei:

- `manifest.json`;
- `cards.jsonl`;
- `decks.jsonl`;
- `lookups.json`;
- `normalization_aliases.json`;
- `ability_registry.json`;
- `engine_support.json`;
- `diagnostics.json`;
- `build_report.md`.

További generált audit- és normalizációs reportok külön fájlban szerepelhetnek.

A package-fájlok pontos schema-verzióját a manifest rögzíti.

---

## 5. Manifest

A manifest minimuma:

- `package_id`;
- `package_version`;
- `schema_version`;
- `ruleset_version`;
- `build_profile`;
- `production_export`;
- forrásfájlok vagy forrásazonosítók;
- fájllista;
- fájlonkénti record count;
- compatibility információ;
- blocking diagnostics summary;
- opcionális source fingerprint;
- opcionális package hash.

A jelenlegi sample identity nem production-final.

Nyitott production döntések:

- végleges `package_id`;
- development/test/release profile;
- package és engine compatibility policy;
- ruleset-version policy;
- source fingerprint;
- package hash;
- rollback és frissítési policy.

---

## 6. Kártyák

A `cards.jsonl` minden sora egy statikus card definition.

Kötelező elvek:

- egyedi `card_id`;
- canonical card type;
- canonical realm;
- nyomtatott Magnitúdó;
- nyomtatott Aura-költség;
- kártyanév;
- szabályszöveg;
- set/printing kapcsolat, ha szükséges;
- structured és support hivatkozások csak validált formában.

A card definition nem meccsbeli card instance.

Nem tartalmaz:

- owner;
- controller;
- aktuális zone;
- activity state;
- damage;
- counter;
- meccsspecifikus visibility;
- runtime instance ID.

---

## 7. Deckek

A `decks.jsonl` statikus deck definitionöket tartalmaz.

Minimum:

- egyedi `deck_id`;
- megjelenítési név;
- termék- vagy profilkapcsolat;
- card ID és count;
- opcionális realm/clan/metaadat;
- schema version.

Blocking validáció:

- duplikált deck ID;
- nem pozitív count;
- ismeretlen card ID;
- hibás decklista;
- hiányzó kért deck;
- tiltott vagy unsupported kártya a választott buildprofil szerint.

---

## 8. Lookupok és canonical értékek

A `lookups.json` gépi canonical értéket és emberi címkét választ szét.

Alapelv:

- `Value`: angol/ASCII snake_case canonical runtime érték;
- `Label_HU`: magyar megjelenítési címke;
- `Canonical_Value`: aktív runtime sornál egyezzen a `Value` mezővel;
- többértékű structured mező delimiterje: pontosvessző.

Aktív példák:

- realm:
  `ignis`, `aqua`, `terra`, `lux`, `umbra`, `ventus`, `aether`;
- Ősforrás-zóna:
  `wellspring`;
- Beáramlás-fázis:
  `infusion`;
- activity:
  `active`, `exhausted`.

A `source` régi structured zónaérték legacy alias lehet, nem active canonical zónanév.

---

## 9. Alias és normalizáció

A `normalization_aliases.json` feladata:

- ismert régi érték → canonical érték mapping;
- biztonságosan automatikus normalizáció;
- auditot igénylő alias jelölése;
- dangerous alias blokkolása;
- forráshely és indok megőrzése.

Alapkategóriák:

- safe automatic;
- known legacy;
- audit required;
- dangerous;
- inactive;
- workflow only;
- unknown.

Automatikus javítás csak egyértelmű és visszakövethető mappingnél engedett.

A builder a forrásfájlt nem írja vissza automatikusan emberi jóváhagyás nélkül.

---

## 10. Ability registry és engine support

Az `ability_registry.json` és `engine_support.json` nem jelent működő ability executort.

Minimum szerep:

- ability és module ID;
- source card;
- ability index;
- structured hivatkozás;
- `support_status`;
- `execution_mode`;
- diagnostics hivatkozás;
- fallback és manual review jelölés.

Javasolt support státuszok:

- `supported`;
- `partial`;
- `unsupported`;
- `not_checked`;
- `fallback_required`;
- `manual_review_required`.

A production executor C#-ban készül.

Aktív deckben szereplő unsupported vagy not-checked tartalom a buildprofil szerint blocking lehet.

---

## 11. Diagnostics

A package-level gépi diagnostics elsődleges formája JSON.

Minimum:

- schema version;
- summary;
- entries;
- severity;
- blocking;
- code;
- category;
- source reference;
- suggested fix;
- human review jelölés.

A `severity` és a `blocking` külön mező.

Alapelvek:

- `critical`: alapból blocking;
- `warning`: alapból nem blocking;
- `audit_note`: emberi review, alapból nem blocking;
- `balance_suspicion`: nem engine-hiba, nem blocking.

A `build_report.md` emberi összefoglaló, nem canonical adatforrás.

---

## 12. Build- és publish-gate

Kötelező folyamat:

1. candidate mappa létrehozása;
2. minden fájl generálása;
3. schema és referenciális validáció;
4. normalizációs és diagnostics report;
5. blocking státusz kiértékelése;
6. csak PASS esetén consumption copy frissítése;
7. publish utáni loader/smoke teszt;
8. sikertelen publish esetén az előző működő consumption copy megőrzése.

A TEMP/staging mappa csak ismert generált fájlokat tartalmazhat.

Takarításkor canonical vagy kézzel szerkesztett forrás nem törölhető.

---

## 13. Godot-fogyasztás

Aktív consumption path:

- `Aeterna game engine/Godot/runtime_package/`;
- Godot útvonal: `res://runtime_package`.

A Godot:

- betölti a package-et;
- registryket épít;
- diagnosticsot jelenít meg;
- debug- és player UI adatot fogyaszt.

A Godot:

- nem olvas XLSX-et;
- nem javít canonical adatot;
- nem találgat ability-logikát;
- nem válik package builderré;
- nem módosít authoritative meccsállapotot package-adat alapján.

---

## 14. Production C# engine-fogyasztás

A production `Aeterna.Engine` ugyanazt a validált package-et fogyasztja.

C.5B minimum loader:

- kötelező fájlok;
- biztonságos relatív path;
- manifest és package identity;
- egyedi card/deck ID;
- deck count;
- deck → card referenciák;
- kért deckek létezése;
- stabil diagnostics.

A C# engine:

- nem olvas közvetlenül XLSX-et;
- nem írja át a runtime package-et;
- statikus definitionből saját authoritative card instance-eket hoz létre;
- nem kezeli a package-et MatchState-ként.

---

## 15. Python-fogyasztás

A Python továbbra is használhatja a package-et:

- fixture- és scenario-generálásra;
- reference engine futásra;
- AI/batch controllerként;
- audit- és coverage-riporthoz;
- differential testinghez;
- balanszadatok előkészítéséhez.

A Python AI nem módosíthatja közvetlenül a C# MatchState-et.

---

## 16. Determinizmus

Kötelező:

- stabil rekordsorrend;
- stabil key-sorrend a canonical outputban;
- UTF-8;
- BOM nélkül;
- LF;
- egész értékek egész formában;
- explicit null/hiány policy;
- azonos forrás és buildverzió esetén azonos package-output;
- hash vagy fingerprint esetén dokumentált canonicalization profile.

---

## 17. Development és release package

### Development

Tartalmazhat:

- részletes diagnosticsot;
- support reportot;
- debug metaadatot;
- nem használt unsupported kártyát warninggal.

### Release vagy zárt teszt

Nem tartalmazhat:

- blocking diagnosticot;
- aktív deckben unsupported/not-checked kártyát;
- ismeretlen canonical értéket;
- dangerous aliast;
- workflow-only runtime adatot;
- rejtett fejlesztői forrásinformációt szükségtelenül.

A release packaging még külön production proofot igényel.

---

## 18. Biztonság és integritás

Baráti tesztben a package olvasható fejlesztői adat maradhat.

Nyilvánosabb kiadásnál később vizsgálandó:

- package hash;
- engine/package compatibility;
- tamper detection;
- signing;
- encrypted vagy packed distribution;
- hibás módosítás player-safe kezelése.

Ez nem korai C.5B-követelmény.

---

## 19. Státusz és következő lépések

Működik:

- valós card/deck/lookup package build;
- blocking validation;
- Godot consumption copy;
- loader és registry;
- diagnostics;
- publish pipeline.

Nem végleges:

- package identity;
- source fingerprint;
- release policy;
- production C# loader;
- ability coverage;
- tamper resistance.

Következő technikai kapcsolat:

- C.5B minimum C# runtime package loader;
- utána Wellspring és player-facing gameplay-contractok.

---

## 20. Dokumentumkapcsolat

A tényleges mennyiségeket, aktív forrásokat és aktuális nyitott feladatokat a `RUNTIME_PACKAGE_STATUS.md` tartalmazza.

A részletes kérdések és döntések:

- `OPEN_QUESTIONS.md`;
- `OPEN_QUESTIONS_DECISIONS.md`.

A korábbi, részletesebb és sample-központú specifikáció a Git-történetben megmarad. A 2.0-s dokumentum az aktív, konszolidált package-contract.
