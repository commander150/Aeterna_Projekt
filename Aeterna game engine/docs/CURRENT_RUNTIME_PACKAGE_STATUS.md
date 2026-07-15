# AETERNA Game Engine – Current Runtime Package Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív runtime package-, lookup- és publish-pipeline státuszdokumentum  
**Rules-engine technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum a runtime package, a kártyaadatforrás, a külön LOOKUPS-forrás és a Godot-fogyasztási út tényleges current állapotát rögzíti.

Nem szabályforrás, nem MatchState-specifikáció és nem ability executor dokumentáció.

Kapcsolódó aktív dokumentumok:

- `CURRENT_CONTRACT_STATUS.md`;
- `CONTRACT_SPECIFICATION.md`;
- `CURRENT_OPEN_QUESTIONS.md`;
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `RUNTIME_PACKAGE_SPECIFICATION.md`;
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`.

---

## 1. Rövid státusz

A runtime package–Godot alapozási mérföldkő elkészült és működik.

Bizonyított adatút:

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

Current minősítés:

- alap adatpipeline: `completed_foundation`;
- valós adatokból package build: `working`;
- Godot consumption copy: `working`;
- Godot loader és smoke: `working`;
- package identity és production schema: `not_final`;
- ability execution: `not_implemented`;
- rules-engine state transport a Godot felé: `not_implemented`;
- végleges kliensintegráció: `not_implemented`.

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

A szabályi elsőbbség:

- hivatalos alapjáték-főforrás 1.4v;
- hivatalos kiegészítő-főforrás 1.4v;
- explicit current emberi döntések és verziózott átvezetések.

---

## 3. Jelenlegi package- és publish-út

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

Current mennyiségek:

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

---

## 5. Runtime LOOKUPS-audit – Birodalom, zóna és fázis

### 5.1 Birodalom

Az aktív `lookups.json` hét canonical Birodalmat tartalmaz:

- `ignis`;
- `aqua`;
- `terra`;
- `lux`;
- `umbra`;
- `ventus`;
- `aether`.

Az uppercase és magyar/forrásszöveges változatok normalizálható bemeneti értékek lehetnek, de a canonical runtime érték lowercase ASCII.

Payment-következmény:

- egy normál Ősforrás-lap alap Aura-identitása a kártya canonical `realm` értéke;
- nem szükséges külön párhuzamos `Aura_Type` mező csak az alap Wellspring-forrásokhoz;
- az AETHER kettős fizetési szerepét a payment validator kezeli, nem új Birodalomérték.

### 5.2 Ősforrás-zóna

Az aktív canonical runtime zóna:

- `wellspring` – Ősforrás.

A kártyaadatbázis beágyazott `5A. LOOKUPS_RUNTIME` lapján előforduló `source` régebbi structured érték, nem az engine current canonical zónaneve.

Következmény:

- MatchState-, event-, snapshot- és action-contractban `wellspring` használandó;
- `source` legfeljebb legacy alias vagy régi auditmező lehet;
- a kártyaadatbázis structured mezőinek későbbi migrációja külön, naplózott adatjavítás;
- a munkaforrás XLSX-et ez az audit nem módosította.

A `source_card` külön `game_object` értékként továbbra is használható egy Ősforrásban lévő lap fogalmi megnevezésére. Ez nem zónanév.

### 5.3 Beáramlás-fázis

Az aktív canonical runtime phase érték:

- `infusion` – Beáramlás.

Ezért:

- phase state-ben `infusion` használandó;
- a korábbi current dokumentumokban szereplő `inflow` technikai megnevezések terminológiai migrációt igényelnek;
- ez nem szabályváltozás, csak canonical runtime névegységesítés;
- az action-, status- és eventneveket a következő szinkronizáló dokumentumfrissítésben kell egységesíteni.

### 5.4 Activity state

Az aktív canonical card state-ek többek között:

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

A jelenlegi 814 soros `EXPORT_RUNTIME` tényleges Aura-értékei:

- 1–9;
- 0 nyomtatott alapköltségű runtime-kártya jelenleg nincs;
- 10-es Aura-költségű runtime-kártya jelenleg nincs.

Ez nem jelenti azt, hogy a normalizált fizetendő költség nem lehet 0.

Több kártya:

- költséget csökkent;
- minimum 1 vagy minimum 0 korlátot használ;
- Aura-költség fizetése nélkül játszik ki lapot.

Ezért külön kell kezelni:

- `printed_aura_cost` vagy base cost – a card definitionből;
- `normalized_payable_aura_cost` – az engine preflight eredménye.

A 0 értéket nem szükséges nyomtatott `Aura` LOOKUPS-értékként felvenni csak azért, mert modifier után a fizetendő költség 0 lehet.

### 6.2 Meglévő structured jelölések

A kártyaadatbázisban már vannak aktív, leíró jelölések:

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

Nem elegendők önmagukban az authoritative végrehajtáshoz.

### 6.3 Mi hiányzik az executable paymenthez?

A jelenlegi card row nem tartalmaz általános, végrehajtható sémát az alábbiakhoz:

- költségmódosítás összege;
- növelés, csökkentés, set-to-zero vagy free-cast mód;
- minimum költség 0 vagy 1;
- érintett Birodalom-, laptípus-, Faj-, Kaszt- vagy konkrét lapkör;
- duration és stack/non-stack policy;
- ideiglenes Aura mennyisége, identitása és lejárata;
- aktivált képesség Aura-költsége;
- közvetlen forráslap-Kimerítés mint költség;
- AETHER vagy más explicit payment override;
- replacement/prevention és alternatív költség.

A `Hatáscímkék` és a `Feltétel_Felismerve` jelenleg runtime-előkészítő, leíró réteg. A `Feltétel_Felismerve` szabadabb snake_case leírása nem tekinthető stabil executor-payloadnak.

### 6.4 Döntés: nem bővítjük találomra a LOOKUPS-ot

Az audit alapján most nem szükséges új globális lookup-csoportokat vagy új CARDS_MASTER/EXPORT_RUNTIME oszlopokat létrehozni.

Current irány:

- a `Realm` marad a base Aura-identitás forrása;
- az `Aura` marad a nyomtatott numerikus alapköltség;
- a `Hatáscímkék` megmarad mechanikai osztályozásnak;
- az executable költségmódosító, temporary Aura és payment override a későbbi ability/payment module normalizált payloadjába kerül;
- új lookup csak akkor készül, ha az executable schema tényleges, ismétlődő enumértéket igényel;
- az engine nem próbálhatja a teljes hatást pusztán a természetes szövegből vagy a `Feltétel_Felismerve` mezőből futás közben újraértelmezni.

### 6.5 Első payment implementation határa

Az első payment-réteg kezelheti:

- printed base Aura cost;
- Realm-alapú source identity;
- AETHER Core payment policy;
- explicit Wellspring source selection;
- `none | forced | choice` selection mode;
- exact payment;
- atomikus `active → exhausted` mutation.

Nem kell még kezelnie:

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
- minden kártya supportja jelenleg `not_evaluated`.

Ezért a 814 kártya package-ben való jelenléte nem jelent 814 működő kártyaképességet.

A lookup- és structured audit nem változtatott ezen a státuszon.

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

- valódi MatchState-et;
- teljes rules engine-t;
- végleges player UI-t;
- interaktív engine–Godot kommunikációt;
- portable release buildet.

---

## 9. Nyitott package- és data-contract feladatok

### 9.1 Runtime-nyelvi döntéshez kapcsolódó

- Python sidecar vagy más process modell;
- Godot .NET/C# runtime;
- portable Windows build;
- state transport és lifecycle.

### 9.2 Package identity

- sample package ID leváltása;
- production/development package type;
- schema- és ruleset-version policy;
- source fingerprint és package hash.

### 9.3 Lookup és card data

- `infusion` terminológia szinkronizálása a current contract-dokumentumokban;
- régi `source` structured értékek későbbi `wellspring` migrációja vagy aliasolása;
- printed és normalized cost egyértelmű elhatárolása;
- ability/payment payload schema létrehozása a tényleges executor előtt;
- unsupported-card és coverage policy.

### 9.4 Godot-integráció

- valódi player-visible snapshot;
- legal action megjelenítés;
- action request transport;
- action response és event stream;
- save/replay/bug-report package.

---

## 10. Aktuális prioritás

A runtime package alapozás nem a jelenlegi kritikus blokkoló.

Kritikus sorrend:

1. `fourth turn` learning-project audit;
2. runtime language comparison fixture és proofok;
3. emberi runtime-döntés;
4. Wellspring production integráció;
5. player-visible Wellspring projection;
6. `infusion` action és phase transition;
7. Magnitúdó-preflight;
8. base payment source selection;
9. `play_card`;
10. későbbi ability/effect execution.

A kártyaadatbázis és a külön LOOKUPS munkaforrás ebben az auditban nem módosult.

---

## 11. Rövid összefoglaló

**Runtime package build:** működik  
**Godot consumption copy:** működik  
**Kártyák:** 814  
**Deckek:** 28  
**Aktív canonical Wellspring-zóna:** `wellspring`  
**Aktív canonical Beáramlás-fázis:** `infusion`  
**Canonical Realm formátum:** lowercase ASCII  
**Nyomtatott Aura-költségforrás:** card definition `Aura` mező  
**Executable payment override schema:** még nincs  
**Ability execution:** nincs  
**LOOKUPS/workbook módosítás:** nem történt  
**Következő adat-szinkron:** `inflow` → `infusion` current contract-terminológia.