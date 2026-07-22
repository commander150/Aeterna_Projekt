# AETERNA – Aktuális Projektterv és Prioritások

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 6.4  
**Dátum:** 2026-07-22  
**Státusz:** aktív projektirányító és prioritási dokumentum  
**Felváltott dokumentum:** `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.3.md`  
**Ellenőrzött repository-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`\
**C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Ez a dokumentum az AETERNA projekt aktuális munkasorrendjét rögzíti. Nem teljes technikai specifikáció, nem történeti napló és nem hivatalos játékszabályforrás.

---

## 1. Elfogadott technológiai irány

A runtime-nyelvi döntési kapu lezárult.

- **Godot / GDScript:** vizuális kliens, scene-ek, input, UI, animáció és debug.
- **C# / .NET:** az egyetlen tervezett production authoritative rules engine.
- **Python:** külső adat-, export-, audit-, fixture-, AI-, batch- és elemzőtooling, valamint referenciaimplementáció.

Kötelező elhatárolás:

- egy futásban egyetlen authoritative MatchState lehet;
- a Godot kliens nem módosíthat közvetlenül authoritative state-et;
- a Python nem lehet második production authority;
- az UI és az AI legal actionből választ;
- minden action requestet a C# engine validál;
- a player-facing projection nem szivárogtathat rejtett információt.

---

## 2. Bizonyított technikai bázis

### Python reference engine

Státusz: `REFERENCE_IMPLEMENTATION / COMPARISON_ORACLE / EXTERNAL_TOOLING_BASE`

Bizonyított fő elemek:

- MatchState és PlayerState;
- card instance registry;
- state version guard;
- draw és end-turn transition;
- typed eventek;
- player-visible snapshot;
- hidden-information projection;
- Domain topology és occupancy;
- activity state;
- izolált Wellspring state;
- determinisztikus AI trajectory.

### Python–Godot sidecar proof

Státusz: `COMPLETE_AND_FROZEN`

A proof megmarad regressziós és történeti bizonyítékként, de production főmotorként nem folytatandó.

### Godot .NET/C# in-process proof

Státusz: `COMPLETE_AND_ACCEPTED`

Bizonyította:

- pure C# runtime candidate;
- közvetlen Godot-processzen belüli futás;
- nincs Python-, TCP- vagy külön engine-processz;
- draw, stale reject és end-turn;
- snapshot, legal action és typed event;
- Debug és Release build;
- headless és visual PASS;
- 100 futásos determinisztika;
- mutation negative proof.

Canonical comparison SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

A RuntimeCandidate proof, nem production engine.

### Production C# engine foundation

Státusz: `COMPLETE_AND_ACCEPTED`

Megvalósult:

- `Aeterna.Engine.sln` production solution;
- `Aeterna.Engine` pure `net8.0` authoritative core;
- `Aeterna.Engine.Headless` és `Aeterna.Engine.Tests`;
- typed production contractok és `EngineSession`;
- minimum runtime package loader;
- draw, stale request rejection és end-turn;
- viewer-specifikus snapshot- és eventprojekció;
- canonical serializer és fixture adapter;
- Godot production bridge, gameplay-logika nélkül.

A production foundation és a RuntimeCandidate külön réteg marad. A foundation még nem teljes rules engine.

---

## 3. Dokumentációs rendezés állapota

A nagy dokumentációs és archiválási munkaszakasz lezárult.

Elkészült:

- engine-dokumentáció első konszolidációja;
- Open Questions kérdés–válasz rendszer;
- a projekttervek és projekt-térképek elődeinek archiválása;
- régi Python-backend és effect/trigger dokumentumok archiválása;
- újratervezési történeti anyagok archiválása;
- régi 1.8v adatauditok archiválása;
- generált kártyaexport-batch archiválása;
- a véletlenül duplikált aktuális adataudit kivezetése;
- az aktív `archive_review/` és `generated_review/` munkaterületek rendezése.

Az archívum tényleges fő útvonala:

`Archive/aeterna dokumentáciok/`

Ezt a dokumentációs munkaszakaszban nem rendezzük tovább. Újabb archív átszervezés csak valódi működési probléma esetén indokolt.

---

## 4. Aktív projektirányító dokumentumok

- `README.md`;
- `Aeterna dokumentációk/README.md`;
- jelen `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.4.md`;
- `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.7.md`;
- `Aeterna game engine/docs/checkpoints/ENGINE_CHECKPOINT.md`.

Technikai döntés és státusz:

- `Aeterna game engine/docs/ARCHITECTURE.md`;
- `Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`;
- `Aeterna game engine/docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- `Aeterna game engine/docs/DECISION_MAP.md`;
- `Aeterna game engine/docs/PROTOTYPE_STATUS.md`;
- `Aeterna game engine/docs/RUNTIME_PACKAGE_STATUS.md`;
- `Aeterna game engine/docs/CONTRACT_STATUS.md`.

A további dokumentumfrissítés nem önálló projektprioritás. Csak akkor kell dokumentumhoz nyúlni, ha:

- technikai mérföldkő teljesül;
- contract vagy authority döntés változik;
- fontos nyitott kérdés lezárul;
- biztonságos folytatási checkpoint szükséges.

---

## 5. Aktuális elsődleges prioritás

### P1 – C.5B mérföldkő dokumentációs lezárása

Státusz: `COMPLETE`

A C.5B kódcommit után a következő négy elsődleges dokumentum állapota összhangba került:

1. jelen projektterv v6.4;
2. projekt-térkép v1.7;
3. engine-checkpoint v1.5;
4. root README v2.2.

A lezáró ellenőrzés igazolta:

- a négy célfájl létezik;
- csak egy aktív projektterv és projekt-térkép van;
- nincs aktív adataudit-duplikáció;
- az archív mozgatások megtörténtek;
- nincs runtime kód a dokumentációs commitban;
- `git status --short` és `git diff --check` rendben van.

A közvetlenül érintett engine- és contract-státuszfájlok C.5B-re vonatkozó téves állításai frissültek. Új dokumentum nem készült.

### P2 – C.5B Production C# Engine Foundation

Státusz: `COMPLETE_AND_ACCEPTED`

Lezáró commit:

`931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`

Első scope:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- `Aeterna.Engine.sln`;
- pure C# production MatchState és PlayerState alap;
- typed core contractok;
- EngineSession;
- minimum runtime package loader;
- draw;
- stale request rejection;
- end-turn;
- canonical serializer;
- fixture adapter;
- Godot production bridge;
- RuntimeCandidate és Python fixture regresszió.

Nem része:

- Wellspring production integráció;
- Beáramlás;
- Magnitúdó;
- Aura-payment;
- `play_card`;
- Domain placement;
- reakció;
- harc;
- effect engine;
- HTTP vagy gRPC;
- production Windows packaging.

Ellenőrzött bizonyíték:

- production solution Debug és Release: PASS, 0 warning, 0 error;
- production tesztek: Debug `13/13`, Release `13/13`;
- canonical expected és actual SHA: `650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`;
- canonical artifact: `210730` byte;
- production determinisztika: `100/100`;
- Godot Debug és ExportRelease build: PASS;
- pozitív és negatív production bridge smoke: PASS.

### P3 – Első production gameplay migráció

Státusz: `NEXT`

A C.5B elfogadása után a meglévő sorrend szerint:

1. Wellspring production state;
2. player-visible Wellspring;
3. Beáramlás precondition és transition;
4. Magnitúdó-preflight;
5. Aura-source és payment;
6. egyszerű Entitás `play_card`;
7. Hand → Domain transition;
8. entry-state és eventek.

---

## 6. Párhuzamos adat- és kártyamunka

A következő tételek fontosak, de nem blokkolják az első production gameplay-migrációt:

- külön `LOOKUPS.xlsx` teljes auditja;
- `Card_ID` és `Szabályi_Kártya_ID` contractdöntés;
- `AET-` prefix kezelése;
- structured többértékű delimiter;
- `blank` és `none`;
- NAME_PROFILE-eltérések;
- decklista-segédnevek;
- master–export parity;
- booster poolok;
- további kártyaaudit és balanszteszt.

Ezeket külön munkasávban kell kezelni, nem az első gameplay-migráció kódscope-jában.

---

## 7. Dokumentumkezelési szabály

- Elsődlegesen meglévő aktív dokumentum frissítendő.
- Új dokumentum csak új, önálló szerep esetén készülhet.
- Az aktív technikai checkpoint az `ENGINE_CHECKPOINT.md`.
- Történeti előd archívumba kerül, nem marad párhuzamos authority.
- Generált output nem canonical szerkesztési forrás.
- Dokumentációs és runtime kódmódosítás ne kerüljön ugyanabba a commitba.
- A dokumentációs szerkesztés és a kizárólag dokumentációt érintő commit nem igényel külön programozási Codex-kört; a Codexet elsősorban programkódhoz és az ahhoz szükséges futtatási ellenőrzésekhez tartjuk fenn.
- A dokumentációt nem kell minden kisebb technikai lépés után tömegesen frissíteni.

---

## 8. Rövid folytatási állapot

**Repository-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7`\
**Authoritative runtime döntés:** C#/.NET  
**Godot szerepe:** visual client  
**Python szerepe:** external tooling és reference  
**C# proof:** kész és elfogadott  
**Production C# engine foundation:** kész és elfogadott\
**C.5A:** kész  
**C.5B:** kész és elfogadott\
**Következő lépés:** P3 első eleme: Wellspring production state és player-visible Wellspring.
