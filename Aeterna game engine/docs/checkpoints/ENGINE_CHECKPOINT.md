# AETERNA Game Engine – Engine Checkpoint

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.5\
**Dátum:** 2026-07-22  
**Státusz:** aktív elsődleges technikai folytatási checkpoint  
**Felváltott verzió:** `ENGINE_CHECKPOINT.md` 1.4\
**Ellenőrzött repository-bázis:** `931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`\
**C# proof-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9` – `Add minimal C# runtime candidate proof`

Ez a dokumentum az AETERNA Game Engine biztonságos technikai folytatási pontja. Nem hivatalos játékszabály és nem teljes production engine-specifikáció.

---

## 1. Elfogadott architektúra

- **Godot/GDScript:** vizuális kliens.
- **C#/.NET:** az egyetlen production authoritative rules engine.
- **Python:** external tooling, reference, AI és batch controller.

A runtime-nyelvi döntési kapu lezárult. Nem készül új GDScript-authority vagy production Python-sidecar irány.

---

## 2. Bizonyított proofok

### Python reference engine

Státusz: `REFERENCE_IMPLEMENTATION / COMPARISON_ORACLE`

Bizonyított:

- MatchState és PlayerState;
- state version guard;
- card instance registry;
- deck, hand és discard instance-zónák;
- draw és end-turn;
- typed eventek;
- player-visible snapshot;
- hidden-information projection;
- Domain topology és occupancy;
- activity state;
- izolált Wellspring;
- deterministic AI trajectory.

A Python nem production authority.

### Python–Godot sidecar

Státusz: `COMPLETE_AND_FROZEN`

Lezáró commit:

`d1fb7aaa23d58f166a30f9e0241799f35f5ac14e`

Megmarad regressziós és történeti proofként.

### C# in-process candidate

Státusz: `COMPLETE_AND_ACCEPTED`

Proof-bázis:

`8e5ee64e42e1657e10f3413444bb870524ee07f9`

Bizonyított:

- pure C# runtime candidate;
- Godot .NET in-process bridge;
- nincs Python, TCP vagy külön engine-processz;
- draw, stale reject és end-turn;
- snapshot, legal action és typed event;
- canonical JSON és SHA;
- 100 futásos determinisztika;
- mutation negative proof;
- Debug és Release;
- headless és visual PASS.

Canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

A RuntimeCandidate proofként megmarad; nem nevezendő át production motorrá.

---

## 3. Production C# foundation

Aktív projektek:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- `Aeterna.Engine.sln`.

Publikus `EngineSession`-határ:

- `CreateMatch`;
- `GetPlayerSnapshot`;
- `ListLegalActions`;
- `SubmitAction`;
- `GetEvents(string viewerPlayerId, int afterSequence = 0)`;
- `GetMatchResult`.

State mutation csak a C# authorityn keresztül történhet.

A teljes, nem redaktált event- és debugállapot csak internal headless/teszt felület. A Godot production bridge kizárólag a viewer-safe publikus API-t delegálja.

Draw eventnél a tulajdonos nézete tartalmazhat kártyaazonosságot, az ellenfél nézete nem tartalmazhat sem `card_instance_id`, sem `card_id` értéket.

---

## 4. C.5A és C.5B

### C.5A – Production architecture plan

Státusz: `COMPLETE_AND_ACCEPTED`

### C.5B – Production Engine Foundation

Státusz: `COMPLETE_AND_ACCEPTED`

Lezáró commit:

`931bf5571d541c752aa421a9f0626768bd8ffbe7` – `Add production C# engine foundation`

Megvalósult scope:

- pure C# production engine;
- headless host;
- test project;
- typed core contractok;
- EngineSession;
- minimum runtime package loader;
- draw;
- stale rejection;
- end-turn;
- canonical serializer;
- fixture adapter;
- Godot production bridge;
- RuntimeCandidate és Python reference regresszió.

Ellenőrzött bizonyíték:

- production solution Debug és Release: PASS, 0 warning, 0 error;
- production tesztek: Debug `13/13`, Release `13/13`;
- expected és actual canonical SHA: `650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`;
- canonical artifact: `210730` byte;
- determinisztika: `100/100`;
- a canonical snapshot és eventösszegzés a production player projectionből és viewer-safe event API-ból származik;
- Godot Debug és ExportRelease: PASS;
- pozitív és negatív production bridge smoke: PASS;
- canonical fixture, Python reference és hivatalos szabályforrások változatlanok.

Nem része:

- Wellspring production gameplay;
- Beáramlás;
- Magnitúdó;
- Aura;
- `play_card`;
- Domain placement;
- reaction;
- combat;
- effect engine;
- HTTP vagy gRPC;
- production packaging.

---

## 5. C.5B utáni gameplay-sorrend

1. Wellspring production state;
2. player-visible Wellspring;
3. Beáramlás;
4. Magnitúdó-preflight;
5. Aura-source és payment;
6. simple Entity `play_card`;
7. Hand → Domain transition;
8. entry-state és eventek;
9. phase és priority;
10. reaction;
11. combat;
12. ability execution;
13. victory és defeat.

---

## 6. Dokumentációs és repository-állapot

A dokumentációs archív rendezés elkészült a következő commitban:

`66a206c6e3bf9155fb9f71a354236fb5b6ab3b90`

Elkészült:

- régi projekttervek és projekt-térképek archiválása;
- régi Python-backend és effect/trigger anyagok archiválása;
- újratervezési történeti csoport archiválása;
- 1.8v adatauditok archiválása;
- generált exportbatch archiválása;
- object identity / zone move terv archiválása;
- gyökérszintű régi engine-összefoglalók archiválása;
- véletlen adataudit-duplikáció kivezetése.

A tényleges archív útvonalak dokumentálva vannak a projekt-térkép v1.7-ben.

A dokumentációs munka nem folytatódik teljes repository-szintű tömeges frissítésként. A továbbiakban csak technikai mérföldkő esetén frissítendő:

- jelen checkpoint;
- aktuális projektterv;
- szükség esetén projekt-térkép;
- érintett contract vagy státuszdokumentum.

---

## 7. Aktuális forráselsőbbség

1. hivatalos 1.4v szabályfőforrások;
2. elfogadott emberi döntések;
3. 0.0.1 termékcél;
4. projektterv v6.4;
5. projekt-térkép v1.7;
6. jelen checkpoint;
7. runtime language decision gate;
8. architecture és technology decisions;
9. aktuális status és contract dokumentumok;
10. Open Questions kérdés–válasz pár;
11. Python reference és comparison fixture;
12. történeti archívum.

---

## 8. Biztonságos folytatási utasítás

Új beszélgetés vagy hosszabb megszakítás után:

1. olvasd el ezt a checkpointot;
2. ellenőrizd a repository aktuális HEAD-jét;
3. ne nyisd újra a runtime-nyelvi döntést;
4. a production C# foundationt tekintsd késznek, de ne a teljes rules engine-t;
5. a RuntimeCandidate és a Python reference maradjon regressziós bizonyíték;
6. ne nyisd újra a lezárt C.5B foundation scope-ját általános refaktorral;
7. a következő gameplay-szakasz kizárólag Wellspring production state-tel és player-visible Wellspringgel induljon;
8. Beáramlás csak a Wellspring-szakasz külön elfogadása után következzen.

---

## 9. Rövid aktuális összefoglaló

- Ellenőrzött repository-bázis: `931bf5571d541c752aa421a9f0626768bd8ffbe7`.
- Python sidecar: kész és befagyasztva.
- C# candidate: kész és elfogadva.
- Production C# engine foundation: kész és elfogadott.
- C.5A: kész.
- C.5B: kész és elfogadott.
- Dokumentációs archív rendezés: kész.
- C.5B dokumentációs lezárás: kész.
- Következő tényleges fejlesztési feladat: Wellspring production state és player-visible Wellspring.
