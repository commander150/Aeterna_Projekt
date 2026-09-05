# AETERNA Game Engine – Runtime Package Status

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.6
**Dátum:** 2026-09-05
**Státusz:** aktív runtime package-, lookup- és publish-pipeline státuszdokumentum
**Történeti előd:** `CURRENT_RUNTIME_PACKAGE_STATUS.md` (migráció lezárva)
**Szinkronizációs repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9`
**Production engine mérföldkő:** `0862e1002dbef81ee203852714d377592272a0e9` – `engine: add aeternal outcome and terminal match result`

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
- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.9.md`

---

## 1. Rövid státusz

A runtime package–Godot alapozási mérföldkő elkészült és működik.

Bizonyított adatút:

```text
Szerkesztési XLSX / LOOKUPS
        ↓
Python export, normalizálás és validáció
        ↓
canonical workbook / runtime package candidate
        ↓
blocking publish validation
        ↓
Godot consumption + production C# package/canonical loader
```

Aktuális minősítés:

- alap adatpipeline: `COMPLETED_FOUNDATION`;
- valós adatokból package build: `WORKING`;
- Godot consumption copy: `WORKING`;
- Godot loader és smoke: `WORKING`;
- canonical workbook export: `WORKING`;
- production C# canonical/package consumption: `WORKING`;
- canonical deck/deck-entry membership consumption: `WORKING`;
- package identity és production schema: `NOT_FINAL`;
- runtime package ability-support metadata: `DECLARED_ONLY / NOT_MIGRATED_TO_FULL_SUPPORT_MATRIX`;
- production C# ability/effect + Reaction + Combat/Pecsét runtime foundation: `IMPLEMENTED_AND_ACTIVE`;
- végleges player-facing kliensintegráció: `NOT_IMPLEMENTED`.

Fontos elhatárolás:

A statikus package `engine_support.json` metadata-állapota nem ugyanaz,
mint a production C# engine tényleges capability-je.

`EngineCapability != ContentCoverage`

A package support matrix külön migrációt/auditot igényel;
a metadata nem írható át automatikusan pusztán azért,
mert az engine-ben már létezik a szükséges foundation.

A runtime package továbbra sem szabálymotor és nem authoritative mérkőzésállapot.

### 1.1 Current package/data decision sync

Current OQ aggregate:

`52 answered / 15 partly_answered / 7 deferred / 0 open`.

Current default:

- full deterministic rebuild = correctness path;
- cache/delta = optional optimization;
- fingerprint/hash provenance/identity/compatibility/integrity szerepű is;
- derived/runtime/canonical output nem ír automatikusan vissza a human editing source-ba;
- unsupported/not-evaluated content nem futhat silent implicit fallbackkal;
- canonical többértékű structured delimiter: pontosvessző (`;`).

A `package identity = NOT_FINAL` az exact hash/layout/release identity contract nyitottságát jelenti,
nem az authority/provenance alapelvét.

A workbook/source delimiter migráció nem része ennek a dokumentációs syncnek.

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

1. hivatalos alapjáték-főforrás 1.5v;
2. hivatalos kiegészítő-főforrás 1.4.1v;
3. explicit emberi döntések és verziózott átvezetések;
4. aktív engine-contractok és fixture-ek;
5. Python referenciaimplementáció;
6. production C# implementáció.

---

### 2.4 Canonical workbook és production C# fogyasztási réteg

A szerkesztési munkaforrás és a statikus Godot runtime package mellett aktív derived/canonical programadat-réteg is létezik:

- `CARDDATABASE.xlsx`;
- `REGISTRY.xlsx`;
- canonical workbook exporter;
- production `CanonicalPackageLoader`;
- runtime lookup/card binding.

Szerepük:

- programfogyasztásra stabilabb canonical adatút;
- determinisztikus mapping;
- card/ability/runtime binding;
- production C# loader input.

Nem:

- új emberi szerkesztési authority;
- hivatalos játékszabályforrás;
- a `LOOKUPS.xlsx` automatikus felülírója.

Eltérés esetén a hivatalos szabályforrás és az elfogadott emberi adat-/contract-döntés az elsődleges.

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

A production C# engine validált package/canonical adatot fogyaszt, és nem olvas közvetlenül szerkesztési XLSX-et.

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

**Aktuális production megjegyzés – 2026-08-14:**
A base Magnitúdó-preflight és az Aura-payment preflight production C# foundationje megvalósult. A temporary Aura, card abilityből származó cost modifier, free cast, alternate cost és replacement továbbra sem tekintendő teljesen támogatottnak.

---

## 7. Ability és engine-support állapot

### 7.1 Runtime package support metadata

A jelenlegi statikus package továbbra is:

- deklarál ability modulokat;
- `ability_registry.json` és `engine_support.json` fájlt tartalmaz;
- a modulok metadata-státuszát `declared_only` formában hordozhatja;
- card supportot `not_evaluated` állapotban tarthat;
- korábbi sample/metadata rétegben `runtime_executes_abilities: false` érték szerepelhet.

Ez package-support metadata, nem production engine capability statement.

### 7.2 Production C# ability/effect capability

A production C# engine-ben aktív foundation többek között:

- canonical ability catalog;
- ability-template compiler;
- effect condition evaluator;
- target filter/resolver;
- trigger resolver foundation;
- effect executor;
- template/collection/zone effect runtime;
- continuous effects;
- modifier/keyword/duration;
- damage/vitals;
- draw/reference integration;
- Reaction / Priority Foundation v1;
- Combat + Pecsét Foundation C0–C6;
- terminal Aeternal / `MatchResult`.

**Státusz:** `IMPLEMENTED_AND_ACTIVE`

### 7.3 Fontos elhatárolás

A következő állítások egyszerre igazak:

1. a statikus runtime package support metadata még nem deklarál teljes ability-execution supportot;
2. a production C# engine capability már lényegesen előrébb tart;
3. a package-ben lévő összes kártya jelenléte nem jelent teljes executable content coverage-et.

Nyitott:

- package support matrix migráció;
- teljes card coverage;
- teljes keyword coverage;
- generic prevention/replacement;
- teljes trigger-ordering coverage;
- komplex compound choice/target support;
- special Seal restore/ward payload;
- további Expansion-specifikus coverage.

Reaction/Priority és Combat/Pecsét current core nem nyitott package-support blocker többé.

### 7.4 VS1 content-coverage gate

Canonical VS1 deckek:

- `DECK-IGN-HAM-VS1-001`;
- `DECK-AQU-MOR-VS1-001`.

VS1 előtt nem kell a teljes kártyaadatbázis supportját lezárni.

Kötelező:

- mindkét deck canonical/active package-membershipje;
- minden hivatkozott card definition feloldása;
- minden ténylegesen használt ability/mechanic executable coverage-je;
- unsupported/not-evaluated blocker hiánya a két VS1 deck scope-jában.

## 8. Godot-oldali bizonyított alapok

Megőrzendő működő elemek:

- runtime package loader;
- card és deck registry;
- lookup registry;
- ability registry betöltése;
- diagnostics reader;
- normalization alias betöltése;
- card reference resolver;
- debug snapshot/legal action/event nézetek;
- unified debug dashboard;
- package loader és contract smoke tesztek;
- production C# bridge/smoke.

Current elhatárolás:

- Godot nem rules authority;
- Godot nem számít külön legalitást;
- Godot nem ír authoritative `MatchState`-et;
- Godot player-facing projectiont, legal actiont, action response-t és eventet fogyaszt;
- production bridge ugyanazt az `Aeterna.Engine` authorityt használja.

Továbbra sincs kész:

- minimal playable product-facing UI;
- teljes human-vs-AI interaction UX;
- final portable Windows package.

A korábbi C# minimal runtime candidate proof történeti bizonyíték;
a current production Godot–C# package/canonical consumption ennél már továbblépett.

## 9. Production C# kapcsolódás

A runtime-nyelvi döntés lezárult:

- C#/.NET az authoritative production runtime;
- Godot/GDScript a vizuális kliens;
- Python külső tooling és adatpipeline.

### Történeti C.5B minimum package-feladat

A C.5B minimum loader többek között validálta:

- szükséges fájlok létezését;
- manifest package ID-t;
- egyedi `card_id`-t;
- egyedi `deck_id`-t;
- pozitív deck countot;
- deck → card referenciákat;
- kért deckek létezését;
- biztonságos relatív útvonalakat.

Ez történeti minimum scope.

### Current production consumption

Current production base:

`0862e1002dbef81ee203852714d377592272a0e9`

Aktív többek között:

- `CanonicalPackageLoader`;
- canonical card catalog;
- runtime lookup catalog;
- canonical runtime binding;
- canonical ability catalog;
- deck/deck-entry membership consumption;
- production smoke/readiness deck resolution.

A runtime package statikus definition/input.
A Combat/Pecsét/Reaction/Surge/MatchResult futó state az authoritative `MatchState` része,
nem package-adat.

## 10. Nyitott package- és data-contract feladatok

### 10.1 Package identity

Továbbra is nyitott:

- sample package ID leváltása;
- production/development package type;
- schema- és ruleset-version policy;
- source fingerprint;
- package hash;
- engine/package compatibility.

### 10.2 Lookup és card data

Továbbra is nyitott vagy auditálandó:

- legacy `source` structured értékek `wellspring` migrációja/aliasolása;
- printed vs normalized cost további payload-egységesítése;
- teljes ability/payment payload coverage;
- unsupported-card/content coverage policy;
- executable effect coverage fokozatos felépítése;
- semicolon delimiter-policy és authoring/workbook legacy drift kompatibilitási auditja.

Nincs vak workbook-migráció.

### 10.3 Godot- és engine-integráció

Már működő foundation:

- production C# canonical/package loader;
- viewer-safe snapshot és event API;
- legal action/action request/response engine-határ;
- Godot production C# bridge és smoke.

Továbbra is nyitott:

- minimal/final player-facing UI-integráció;
- package support/coverage metadata megjelenítése és diagnosztikája;
- save/replay/bug-report package;
- release diagnostics és support workflow;
- final packaging/compatibility UX.

### 10.4 Release és integritás

- development és release package elkülönítése;
- Windows exportban package-elhelyezés;
- package frissítési elv;
- későbbi tamper resistance;
- verzióütközés kezelése.

### 10.5 VS1-specifikus package gate

Csak akkor szükséges package-módosítás a VS1 előtt,
ha a readiness audit tényleges blockert talál:

- hiányzó/hibás VS1 deck membership;
- hiányzó card definition;
- hibás canonical lookup/alias;
- szükséges card/ability unsupported/not-evaluated;
- loader/compatibility hiba.

A teljes package identity/release/tamper-resistance nem automatikus VS1-blocker.

## 11. Aktuális prioritás

A runtime package alapozás nem önmagában a jelenlegi kritikus blokkoló.

Current next gate:

`VS1_READINESS_REQUIRED`

A projekt aktuális szakmai sorrendje:

1. canonical VS1 deck/card/mechanic readiness audit;
2. package/content/engine blocker azonosítás;
3. csak tényleges blockerre finite contract + implementáció;
4. simple fair AI + match orchestration;
5. minimal playable Godot;
6. human-vs-AI full match;
7. reproducible AI-vs-AI smoke;
8. VS1 acceptance.

Runtime-package-specifikus későbbi prioritások:

- package support/coverage matrix migráció;
- production package identity;
- engine/package compatibility policy;
- source fingerprint/hash;
- development/release profile;
- Windows release packaging.

Ezek közül csak a tényleges VS1 blocker válik VS1 előfeltétellé.

A kártyaadatbázis és a külön LOOKUPS munkaforrás e dokumentumfrissítés során nem módosul.

## 12. Dokumentumkezelési hatás

A `RUNTIME_PACKAGE_STATUS.md` már a történeti
`CURRENT_RUNTIME_PACKAGE_STATUS.md` elfogadott utódja.

A korábbi migration feladat lezárt történeti lépés, nem current teendő.

Current szabály:

- az aktív fájl neve `RUNTIME_PACKAGE_STATUS.md`;
- `CURRENT_RUNTIME_PACKAGE_STATUS.md` nem current authority;
- újabb verziók ezt az aktív fájlt frissítik;
- korábbi verziót a Git history őrzi;
- Archive csak valódi historical/deprecated szerep esetén szükséges.

## 13. Rövid összefoglaló

**Runtime package build:** működik
**Godot consumption copy:** működik
**Production C# canonical/package consumption:** `WORKING`
**Canonical deck/deck-entry membership consumption:** `WORKING`
**Történeti rögzített kártyaszám:** 814
**Történeti rögzített deckszám:** 28
**Aktív canonical Wellspring-zóna:** `wellspring`
**Aktív canonical Beáramlás-fázis:** `infusion`
**Canonical Realm formátum:** lowercase ASCII
**Canonical multi-value delimiter:** pontosvessző (`;`)
**Nyomtatott Aura-költségforrás:** card definition `Aura` mező
**Executable payment override schema:** még nem teljes
**Runtime package ability-support metadata:** declared-only / nem teljes support matrix
**Production C# ability/effect + Reaction + Combat/Pecsét foundation:** `IMPLEMENTED_AND_ACTIVE`
**Current production base:** `0862e1002dbef81ee203852714d377592272a0e9`
**Current next gate:** `VS1_READINESS_REQUIRED`
**Canonical VS1 deckek:** `DECK-IGN-HAM-VS1-001`, `DECK-AQU-MOR-VS1-001`
**LOOKUPS/workbook módosítás:** e dokumentációs körben nem történt
