# AETERNA Game Engine – Runtime Package Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2  
**Dátum:** 2026-07-20  
**Státusz:** aktív runtime package-, lookup- és publish-pipeline státuszdokumentum  
**Felváltott fájl:** `CURRENT_RUNTIME_PACKAGE_STATUS.md`  
**Aktuális repository-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Ez a dokumentum a runtime package, a kártyaadatforrás, a külön LOOKUPS-forrás és a Godot-fogyasztási út tényleges állapotát rögzíti.

Nem szabályforrás, nem MatchState-specifikáció és nem ability executor dokumentáció.

Kapcsolódó aktív dokumentumok:

- `CONTRACT_STATUS.md`
- `CONTRACT_SPECIFICATION.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `PROTOTYPE_STATUS.md`
- `checkpoints/ENGINE_CHECKPOINT.md`
- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.2.md`

---

## 1. Rövid státusz

A runtime package–Godot alapozási mérföldkő elkészült és működik.

Bizonyított adatút:

```text
Google Sheets / lokális XLSX
        ↓
Python export és adapterek
        ↓
validáció és normalizáció
        ↓
runtime package candidate
        ↓
publish validation
        ↓
Godot/runtime_package consumption copy
        ↓
Godot loader, registry, debug nézet és smoke teszt
```

Aktuális minősítés:

- alap adatpipeline: `COMPLETED_FOUNDATION`;
- valós adatokból package build: `WORKING`;
- Godot consumption copy: `WORKING`;
- Godot loader és smoke: `WORKING`;
- package identity és production schema: `NOT_FINAL`;
- ability execution: `NOT_IMPLEMENTED`;
- production C# engine package consumption: `PLANNED_FOR_C5B`;
- végleges player-facing kliensintegráció: `NOT_IMPLEMENTED`.

A runtime package nem szabálymotor és nem authoritative mérkőzésállapot.

---

## 2. Aktív források

### 2.1 Kártyák és decklisták

Aktív szerkesztési forrás:

- `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`

Fő runtime card sheet:

- `7. EXPORT_RUNTIME`

A package ebből veszi többek között:

- Card_ID;
- kártyanév és típus;
- Birodalom és Klán;
- nyomtatott Magnitúdó- és Aura-érték;
- természetes kártyaszöveg;
- structured auditmezők;
- set- és printing-adatok.

### 2.2 Runtime lookupok

Aktív lookupforrás:

- `Aeterna dokumentációk/LOOKUPS.xlsx`

Aktív runtime sheetek:

- `RUNTIME_CORE`;
- `RUNTIME_ABILITY`.

Legacy alias és normalizációs forrás:

- `RUNTIME_LEGACY_ALIAS`.

Publikált runtime kimenet:

- `Aeterna game engine/Godot/runtime_package/lookups.json`.

A kártyaadatbázis munkaforrás saját `5A. LOOKUPS_RUNTIME` lapja munkafájl-validációs és történeti segédforrás. Nem írhatja felül automatikusan a külön `LOOKUPS.xlsx` aktív canonical runtime értékeit.

### 2.3 Szabályforrások

Szabályi elsőbbség:

1. hivatalos alapjáték-főforrás 1.4v;
2. hivatalos kiegészítő-főforrás 1.4v;
3. explicit emberi döntések és verziózott átvezetések;
4. aktív engine-contractok és fixture-ek;
5. Python referenciaimplementáció;
6. production C# implementáció.

---

## 3. Package- és publish-út

Aktív Python tooling:

- `Aeterna game engine/python/`

Fő szerepek:

- XLSX export;
- JSONL előállítás;
- runtime card- és deckadapter;
- LOOKUPS- és legacy alias reader;
- normalizációs preview és report;
- candidate package build;
- blocking validation;
- Godot consumption copy publikálása;
- smoke és unit tesztek.

Elsődleges fejlesztői publish runner:

- `Aeterna game engine/python/publish_runtime_package_to_godot.bat`

Publish-elv:

1. ideiglenes candidate készül;
2. blocking validation lefut;
3. blocking hiba esetén nincs publish;
4. sikeres validáció után frissül a Godot consumption copy;
5. diagnostics és build report készül.

Aktív Godot fogyasztási mappa:

- `Aeterna game engine/Godot/runtime_package/`

Godot útvonal:

- `res://runtime_package`

A későbbi production C# engine ugyanezt a validált package-et fogyasztja, és nem olvas közvetlenül XLSX-et.

---

## 4. Package identity és fájlok

A jelenlegi manifest még történeti sample identityt használ:

- `package_id: aeterna.sample_runtime_package`;
- `package_version: 0.1.0`;
- `schema_version: sample-runtime-package-v1`;
- `ruleset_version: sample-ruleset-v0`;
- `production_export: false`.

Ez technikailag működő fejlesztői package, de nem production-final identity.

Fő package-fájlok:

- `manifest.json`;
- `cards.jsonl`;
- `decks.jsonl`;
- `lookups.json`;
- `normalization_aliases.json`;
- normalizációs audit-, preview- és apply reportok;
- `ability_registry.json`;
- `engine_support.json`;
- `diagnostics.json`;
- `build_report.md`.

A legutóbbi rögzített mennyiségek:

- kártyák: 814;
- deckek: 28;
- source decklist sorok: 754;
- runtime lookup rekordok: 2080;
- Godot lookup groupok: 32;
- normalization aliasok: 1011;
- automatikusan normalizálható aliasok: 903;
- auditot igénylő aliasok: 108;
- ability modulok: 2;
- ability státusz: `declared_only`;
- blocking diagnostics: 0;
- warningok: 0;
- hibák: 0.

Ezek történeti buildértékek; új publish után újra ellenőrzendők.

---

## 5. Runtime LOOKUPS-audit

### 5.1 Birodalom

Az aktív `lookups.json` hét canonical Birodalmat tartalmaz:

- `ignis`;
- `aqua`;
- `terra`;
- `lux`;
- `umbra`;
- `ventus`;
- `aether`.

Az uppercase és magyar vagy forrásszöveges változatok normalizálható bemenetek lehetnek, de a canonical runtime érték lowercase ASCII.

Payment-következmény:

- egy normál Ősforrás-lap alap Aura-identitása a kártya canonical `realm` értéke;
- nem szükséges külön párhuzamos `Aura_Type` mező csak az alap Wellspring-forrásokhoz;
- az AETHER kettős fizetési szerepét a payment validator kezeli, nem új Birodalomérték.

### 5.2 Ősforrás-zóna

Aktív canonical runtime zóna:

- `wellspring` – Ősforrás.

A kártyaadatbázis beágyazott `5A. LOOKUPS_RUNTIME` lapján előforduló `source` régebbi structured érték, nem az engine canonical zónaneve.

Következmény:

- MatchState-, event-, snapshot- és action-contractban `wellspring` használandó;
- `source` legfeljebb legacy alias vagy régi auditmező lehet;
- a kártyaadatbázis structured mezőinek későbbi migrációja külön, naplózott adatjavítás;
- a munkaforrás XLSX-et ez a státuszdokumentum nem módosítja.

A `source_card` külön `game_object` értékként továbbra is használható egy Ősforrásban lévő lap fogalmi megnevezésére. Ez nem zónanév.

### 5.3 Beáramlás-fázis

Aktív canonical runtime phase érték:

- `infusion` – Beáramlás.

Ezért:

- phase state-ben `infusion` használandó;
- korábbi dokumentumokban szereplő `inflow` technikai megnevezések terminológiai migrációt igényelnek;
- ez nem szabályváltozás, csak canonical runtime névegységesítés;
- action-, status- és eventneveket a contractkonszolidáció során egységesíteni kell.

### 5.4 Activity state

Aktív canonical card state-ek többek között:

- `active`;
- `exhausted`;
- `face_down`;
- `face_up`;
- `revealed`;
- `hidden`.

A Wellspring payment-contract `active → exhausted` állapotváltása összhangban van az aktív LOOKUPS-szal.

---

## 6. Aura- és payment-adat audit

### 6.1 Nyomtatott alapköltség

A kártyaadatbázis `Aura` mezője a lap nyomtatott vagy alap kijátszási Aura-költsége.

A munkaforrás beágyazott validációs listája:

- 1–10 Aura.

A legutóbbi 814 soros `EXPORT_RUNTIME` tényleges Aura-értékei:

- 1–9;
- 0 nyomtatott alapköltségű runtime-kártya nem volt;
- 10-es Aura-költségű runtime-kártya nem volt.

Ez nem jelenti azt, hogy a normalizált fizetendő költség nem lehet 0.

Külön kell kezelni:

- `printed_aura_cost` vagy base cost – a card definitionből;
- `normalized_payable_aura_cost` – az engine preflight eredménye.

A 0 értéket nem szükséges nyomtatott `Aura` LOOKUPS-értékként felvenni csak azért, mert modifier után a fizetendő költség 0 lehet.

### 6.2 Meglévő structured jelölések

A legutóbbi auditban szereplő leíró jelölések:

- `cost_mod` – 28 runtime-kártya;
- `resource_gain` – 37;
- `resource_spend` – 8;
- `resource_drain` – 2;
- `resource_acceleration` – 1;
- `move_to_source` – 6;
- `source_manipulation` – 5;
- `exhaust` – 61;
- `free_cast` – 6.

Ezek alkalmasak:

- auditálásra;
- keresésre;
- coverage-csoportosításra;
- ability-modul jelöltek képzésére.

Nem elegendők önmagukban authoritative végrehajtáshoz.

### 6.3 Mi hiányzik az executable paymenthez?

A jelenlegi card row nem tartalmaz általános, végrehajtható sémát többek között:

- költségmódosítás összege;
- növelés, csökkentés, set-to-zero vagy free-cast mód;
- minimum költség 0 vagy 1;
- érintett Birodalom-, laptípus-, Faj-, Kaszt- vagy konkrét lapkör;
- duration és stack/non-stack policy;
- ideiglenes Aura mennyisége, identitása és lejárata;
- aktivált képesség Aura-költsége;
- közvetlen forráslap-Kimerítés mint költség.

A `Hatáscímkék` és a `Feltétel_Felismerve` runtime-előkészítő, leíró réteg. Nem stabil executor-payload.

### 6.4 LOOKUPS-bővítési döntés

Nem hozunk létre találomra új globális lookup-csoportokat vagy új adatbázisoszlopokat.

Aktív irány:

- `Realm` marad a base Aura-identitás forrása;
- `Aura` marad a nyomtatott numerikus alapköltség;
- `Hatáscímkék` megmarad mechanikai osztályozásnak;
- executable költségmódosító, temporary Aura és payment override a későbbi ability/payment module normalizált payloadjába kerül;
- új lookup csak tényleges, ismétlődő executable enumértékhez készül;
- az engine nem értelmezheti újra futás közben a teljes hatást pusztán természetes szövegből.

### 6.5 Első payment implementation határa

Az első payment-réteg kezelheti:

- printed base Aura cost;
- Realm-alapú source identity;
- AETHER Core payment policy;
- explicit Wellspring source selection;
- `none | forced | choice` selection mode;
- exact payment;
- atomikus `active → exhausted` mutation.

Még nem kell kezelnie:

- temporary Aura poolt;
- card abilityből származó költségmódosítást;
- free castot;
- alternatív képességköltséget;
- resource drain vagy replacement mechanikát.

Ezek ability executor és effect-state nélkül nem nevezhetők támogatottnak.

---

## 7. Ability és engine-support állapot

A jelenlegi package:

- deklarál ability modulokat;
- jelzi a support státuszt;
- nem futtatja a kártyaképességeket;
- `runtime_executes_abilities: false`;
- a kártyák supportja jelenleg `not_evaluated`.

A 814 kártya package-ben való jelenléte nem jelent 814 működő kártyaképességet.

---

## 8. Godot-oldali bizonyított alapok

Megőrzendő működő elemek:

- runtime package loader;
- card és deck registry;
- lookup registry;
- ability registry betöltése;
- diagnostics reader;
- normalization alias betöltése;
- card reference resolver;
- sample snapshot, legal action és event debug nézetek;
- unified debug dashboard;
- package loader és contract smoke tesztek.

Nem bizonyítják önmagukban:

- production C# MatchState-et;
- teljes rules engine-t;
- végleges player UI-t;
- teljes interaktív gameplay-kapcsolatot;
- portable release buildet.

A C# minimal runtime proof külön bizonyította a Godot .NET in-process kapcsolatot, de még nem production package consumer.

---

## 9. Production C# kapcsolódás

A runtime-nyelvi döntés lezárult:

- C#/.NET az authoritative production runtime;
- Godot/GDScript a vizuális kliens;
- Python külső tooling és adatpipeline.

### C.5B minimum package-feladata

A production C# engine minimum loaderének validálnia kell:

- szükséges fájlok létezése;
- manifest package ID;
- egyedi `card_id`;
- egyedi `deck_id`;
- pozitív deck count;
- minden deckkártya létezése;
- kért deckek létezése;
- biztonságos relatív útvonalak.

A C.5B nem változtatja meg a package teljes production identityját, és nem implementál ability executiont.

---

## 10. Nyitott package- és data-contract feladatok

### 10.1 Package identity

- sample package ID leváltása;
- production/development package type;
- schema- és ruleset-version policy;
- source fingerprint;
- package hash;
- engine/package compatibility.

### 10.2 Lookup és card data

- `infusion` terminológia szinkronizálása;
- régi `source` structured értékek `wellspring` migrációja vagy aliasolása;
- printed és normalized cost elhatárolása;
- ability/payment payload schema;
- unsupported-card és coverage policy;
- executable effect coverage fokozatos felépítése.

### 10.3 Godot- és engine-integráció

- production C# package loader;
- valódi player-visible snapshot;
- legal action megjelenítés;
- action request bridge;
- action response és event stream;
- save/replay/bug-report package;
- production diagnostics.

### 10.4 Release és integritás

- development és release package elkülönítése;
- Windows exportban package-elhelyezés;
- package frissítési elv;
- későbbi tamper resistance;
- verzióütközés kezelése.

---

## 11. Aktuális prioritás

A runtime package alapozás nem a jelenlegi kritikus blokkoló.

Sorrend:

1. engine-dokumentáció rendezése és átnevezése;
2. C.5B production C# engine foundation;
3. C# minimum runtime package loader;
4. Wellspring production integráció;
5. player-visible Wellspring;
6. `infusion` action és phase transition;
7. Magnitúdó-preflight;
8. base payment source selection;
9. `play_card`;
10. későbbi ability/effect execution;
11. production package identity és release packaging.

A kártyaadatbázis és a külön LOOKUPS munkaforrás e dokumentumfrissítés során nem módosult.

---

## 12. Dokumentumkezelési hatás

Ez a fájl a `CURRENT_RUNTIME_PACKAGE_STATUS.md` utódja.

Repository alkalmazásakor:

1. az új aktív név `RUNTIME_PACKAGE_STATUS.md`;
2. a régi `CURRENT_RUNTIME_PACKAGE_STATUS.md` eltávolítandó;
3. minden rá mutató hivatkozást frissíteni kell;
4. az eltávolítás csak az új fájl beillesztése és a hivatkozások ellenőrzése után történhet.

---

## 13. Rövid összefoglaló

**Runtime package build:** működik  
**Godot consumption copy:** működik  
**Legutóbbi rögzített kártyaszám:** 814  
**Legutóbbi rögzített deckszám:** 28  
**Aktív canonical Wellspring-zóna:** `wellspring`  
**Aktív canonical Beáramlás-fázis:** `infusion`  
**Canonical Realm formátum:** lowercase ASCII  
**Nyomtatott Aura-költségforrás:** card definition `Aura` mező  
**Executable payment override schema:** még nincs  
**Ability execution:** nincs  
**Production C# package loader:** C.5B scope  
**LOOKUPS/workbook módosítás:** nem történt
