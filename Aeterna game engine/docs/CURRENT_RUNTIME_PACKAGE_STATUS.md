# AETERNA Game Engine – Current Runtime Package Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív runtime package- és publish-pipeline státuszdokumentum  
**Rules-engine technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum a runtime package és a Godot-fogyasztási út jelenlegi tényleges állapotát rögzíti.

Nem helyettesíti:

- a hosszú `RUNTIME_PACKAGE_SPECIFICATION.md` tervezési anyagát;
- a történeti `checkpoints/CHECKPOINTS.md` részletes mérföldköveit;
- a Python rules engine aktuális checkpointját.

Feladata annak egyértelmű megválaszolása, hogy a korábbi runtime package–Godot munkasávból mi készült el, mi működik ma, és mi maradt későbbi feladat.

---

## 1. Rövid státusz

A runtime package–Godot alapozási mérföldkő **sikeresen elkészült**.

Bizonyított adatút:

    Google Sheets / lokális XLSX
        ↓
    Python XLSX export és adapterek
        ↓
    validáció és normalizációs reportok
        ↓
    runtime package candidate
        ↓
    publish validation
        ↓
    Godot/runtime_package consumption copy
        ↓
    Godot loader, registry, debug nézet és smoke teszt

Ez az alapozás nem lett leváltva vagy eldobva.

A jelenlegi authoritative Python rules engine erre a statikus adat- és kliensalapra épül rá.

A runtime package–Godot munkasáv jelenlegi minősítése:

- alap adatpipeline: `completed_foundation`;
- valós adatokból történő package build: `working`;
- Godot consumption copy: `working`;
- Godot loader és smoke: `working`;
- végleges production package identity és schema: `not_final`;
- rules-engine state transport a Godot felé: `not_implemented`;
- végleges kliensintegráció: `not_implemented`.

---

## 2. Aktív források

### 2.1 Kártyák és decklisták

Aktív szerkesztési forrás:

- `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`

A runtime package ebből veszi többek között:

- kártyákat;
- Card_ID-kat;
- decklistákat;
- termék- és deckkapcsolatokat.

### 2.2 Runtime lookupok

Aktív lookupforrás:

- `Aeterna dokumentációk/LOOKUPS.xlsx`

Aktív runtime sheetek:

- `RUNTIME_CORE`
- `RUNTIME_ABILITY`

Legacy alias és normalizációs forrás:

- `RUNTIME_LEGACY_ALIAS`

### 2.3 Hivatalos szabályforrások

A runtime package nem szabályforrás.

A szabályi elsőbbség továbbra is:

- hivatalos alapjáték főforrás 1.4v;
- hivatalos kiegészítő főforrás 1.4v.

---

## 3. Python tooling és publish út

Az aktív Python tooling az `Aeterna game engine/python/` alatt található.

Fő szerepek:

- XLSX export;
- JSONL előállítás;
- runtime card adapter;
- runtime deck adapter;
- LOOKUPS reader;
- legacy alias reader;
- normalizációs preview és reportok;
- package build;
- candidate-validáció;
- Godot consumption copy publikálása;
- smoke és unit tesztek.

Elsődleges fejlesztői publish runner:

- `Aeterna game engine/python/publish_runtime_package_to_godot.bat`

Elvi publish folyamat:

1. ideiglenes candidate package készül;
2. a candidate validációja lefut;
3. blocking hiba esetén nincs publish;
4. sikeres validáció esetén frissül a Godot consumption copy;
5. diagnostics és build report jelzi az eredményt.

A TEMP candidate réteg jelenleg elfogadott átmeneti staging megoldás, de nem végleges release-package architektúra.

---

## 4. Godot consumption package

Aktív fogyasztási mappa:

- `Aeterna game engine/Godot/runtime_package/`

Aktív Godot loader útvonal:

- `res://runtime_package`

A Godot package loader smoke teszt jelenleg explicit módon ezt ellenőrzi.

A Godot consumption copy:

- generált vagy publikált adatpéldány;
- nem kézzel szerkesztett canonical forrás;
- nem szabálymotor;
- nem MatchState;
- nem player save;
- nem release package registry.

---

## 5. Jelenlegi manifest-állapot

Az aktuális Godot consumption manifest fő identity mezői:

- `package_id: "aeterna.sample_runtime_package"`
- `package_version: "0.1.0"`
- `schema_version: "sample-runtime-package-v1"`
- `ruleset_version: "sample-ruleset-v0"`
- `production_export: false`

Ez történeti sample identity, miközben a package már valós, teljes méretű adatokat tartalmaz.

Ezért a jelenlegi állapot:

- technikailag működő;
- tesztelt;
- fejlesztői használatra alkalmas;
- elnevezésében és verziózásában még nem production-final.

Külön későbbi migráció szükséges:

- package ID;
- package schema név;
- package version policy;
- ruleset version;
- production/development package type;
- manifest source path és reprodukálhatósági metadata.

Ezt nem szabad az aktuális rules-engine feladattal összekeverni.

---

## 6. Aktuális package-fájlok

A jelenlegi manifest az alábbi fájlokat listázza:

- `manifest.json`
- `cards.jsonl`
- `decks.jsonl`
- `lookups.json`
- `aliases.json`
- `normalization_aliases.json`
- `normalization_audit_report.json`
- `normalization_preview_report.json`
- `normalization_patch_plan.json`
- `normalization_apply_report.json`
- `ability_registry.json`
- `engine_support.json`
- `diagnostics.json`
- `build_report.md`

### 6.1 Fontos státuszok

`cards.jsonl`

- valós kártyaadatokat tartalmaz;
- jelenlegi package-ben 814 rekord;
- runtime card definition forrás.

`decks.jsonl`

- valós deckadatokat tartalmaz;
- jelenlegi package-ben 28 deck;
- source decklist feldolgozás során 754 sor olvasva.

`lookups.json`

- a külön `LOOKUPS.xlsx` runtime sheetjeiből származik;
- runtime controlled vocabulary és megjelenítési alap.

`aliases.json`

- történeti sample/placeholder fájl;
- nem a canonical normalizációs mapping elsődleges forrása.

`normalization_aliases.json`

- a `RUNTIME_LEGACY_ALIAS` feldolgozott runtime outputja;
- jelenlegi package-ben 1011 alias;
- 903 normalizálható;
- 108 auditot igényel.

`normalization_audit_report.json`

- diagnostics- és auditcélú;
- nem írja át automatikusan a canonical forrást.

`normalization_preview_report.json`

- változtatás előtti preview;
- nem authoritative kártyaadat.

`normalization_patch_plan.json`

- tervezett normalizációs műveletek leírása;
- nem önálló canonical source.

`normalization_apply_report.json`

- alkalmazási eredmény és auditnyom;
- nem szabálymotor-adat.

`ability_registry.json`

- jelenleg deklaratív sample/foundation réteg;
- nem bizonyít ability executiont.

`engine_support.json`

- support státusz és coverage-információ;
- a jelenlegi package szerint minden kártya `not_evaluated`.

`diagnostics.json`

- strukturált build- és adatdiagnosztika.

`build_report.md`

- ember által olvasható buildösszefoglaló.

---

## 7. Aktuális mennyiségi állapot

A jelenlegi Godot consumption package manifestje alapján:

- kártyák: 814;
- deckek: 28;
- runtime lookup rekordok a build source summaryban: 2080;
- normalization aliasok: 1011;
- auditot igénylő aliasok: 108;
- automatikus normalizációra engedett aliasok: 903;
- ability modulok: 2;
- ability státusz: `declared_only`;
- blocking diagnostics: 0;
- warningok: 0;
- hibák: 0.

Godot loader smoke elvárás:

- cards: 814;
- decks: 28;
- lookup groups: 32;
- ability modules: 2;
- normalization aliases: 1011;
- warnings: 0;
- blocking errors: 0.

A `runtime lookup records` és a Godot `lookup groups` két külön szám:

- az első rekordmennyiség;
- a második a Godotban létrejött csoportok száma.

---

## 8. Ability és engine-support állapot

A jelenlegi package:

- deklarál ability modulokat;
- jelzi a support státuszt;
- nem futtatja a kártyaképességeket.

Aktuális manifestállítás:

- `runtime_executes_abilities: false`

Ezért:

- az ability registry nem executor;
- az engine support report nem garancia a teljes szabályhűségre;
- a 814 kártya package-ben való jelenléte nem jelenti, hogy mind a 814 kártya működik a rules engine-ben;
- az ability implementation külön későbbi roadmap.

---

## 9. Godot-oldali bizonyított alapok

Elkészült és megőrzendő:

- runtime package loader;
- card registry;
- deck registry;
- lookup registry;
- ability registry betöltése;
- diagnostics olvasás;
- normalization alias count betöltés;
- card reference resolver;
- sample snapshot viewer;
- sample legal action debug panel;
- sample event log debug view;
- unified debug dashboard;
- package loader smoke;
- sample contract smoke;
- contract consistency smoke.

Ezek a későbbi kliensintegráció alapjai.

Nem bizonyítják önmagukban:

- valódi játékállapotot;
- teljes rules engine-t;
- végleges player UI-t;
- interaktív Python–Godot kommunikációt;
- release buildet.

---

## 10. Kapcsolat a Python rules engine-nel

A runtime package feladata:

- statikus card definition;
- deck definition;
- lookup;
- normalizációs adat;
- support- és diagnostics-információ.

A Python rules engine feladata:

- MatchState;
- card instance;
- legal action;
- action request validálása;
- state transition;
- typed event;
- player-visible projection;
- rejtett információ védelme;
- AI-vs-AI végrehajtás.

A runtime package nem tartalmazhat authoritative mérkőzésállapotot.

A MatchState nem írhatja át a runtime package statikus card definitionjeit.

---

## 11. Mi készült el a korábbi munkasávból?

Elkészült:

- exporter migráció az új Python tooling alá;
- explicit source és output útvonalak;
- runtime card adapter;
- runtime deck adapter;
- LOOKUPS source split;
- legacy alias reader;
- candidate package build;
- blocking validation;
- Godot publish;
- valós kártya- és deckadat package;
- normalization alias output;
- audit- és preview reportok;
- Godot loader;
- registryk;
- debug nézetek;
- headless smoke.

Ez a korábbi alapozási feladat lényegi célját teljesíti.

---

## 12. Mi maradt nyitva?

### 12.1 Package identity és schema

- sample package ID leváltása;
- sample schema név leváltása;
- development/test/release package-típus;
- szabályos semantic vagy saját package-verziózás;
- ruleset-version kapcsolat.

### 12.2 Reprodukálhatóság

- source fingerprint;
- builder version;
- normalizált source list;
- determinisztikus generated timestamp policy;
- package hash;
- package comparison report.

### 12.3 Output és staging

- TEMP candidate hosszú távú státusza;
- központi build vagy generated mappa;
- package registry;
- archivált package-ek;
- release candidate output.

### 12.4 Ability support

- ability registry canonical production schema;
- engine-support automatikus coverage;
- executable ability module layer;
- unsupported card policy;
- blocking vs warning policy.

### 12.5 Godot-integráció

- valódi player-visible snapshot fogadása;
- legal action megjelenítés az aktuális Python engine-ből;
- action request transport;
- action response és event stream;
- local process vagy más transport döntés;
- save/replay/bug-report package.

### 12.6 Release

- Windows packaging;
- Python runtime csomagolása;
- integritás-ellenőrzés;
- nyers XLSX kizárása;
- verziózott release package.

---

## 13. Aktuális prioritás

A runtime package pipeline jelenleg nem a kritikus blokkoló fejlesztési pont.

A közvetlen kritikus út:

1. Wellspring MatchState-integráció;
2. player-visible Wellspring summary;
3. Beáramlás;
4. erőforrás-preflight és payment;
5. Entitás kijátszása;
6. teljesebb phase/priority;
7. későbbi Python–Godot kliensintegráció.

A package identity és release-rendezés később külön munkasávban végezhető.

---

## 14. Dokumentumkapcsolatok

Aktuális projektirány:

- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`

Aktuális engine-state:

- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

Aktuális contract-state:

- `CURRENT_CONTRACT_STATUS.md`

Aktuális prototípus-state:

- `CURRENT_PROTOTYPE_STATUS.md`

Hosszú runtime package terv:

- `RUNTIME_PACKAGE_SPECIFICATION.md`

Történeti package és Godot mérföldkövek:

- `checkpoints/CHECKPOINTS.md`
- `checkpoints/README.md`

---

## 15. Rövid összefoglaló

**Korábbi runtime package–Godot alapozási cél:** teljesítve  
**Valós adatokkal build:** működik  
**Godot consumption copy:** működik  
**Godot loader és smoke:** működik  
**Aktuális card count:** 814  
**Aktuális deck count:** 28  
**Aktuális normalization alias count:** 1011  
**Blocking diagnostics:** 0  
**Ability execution:** nincs  
**Package identity:** még sample jellegű  
**Végleges production schema:** nincs  
**Következő kritikus programozási irány:** Python rules engine folytatása
