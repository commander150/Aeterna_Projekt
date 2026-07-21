# AETERNA – Aktuális Projektterv és Prioritások

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 6.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív projektirányító és prioritási dokumentum  
**Felváltott dokumentum:** `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.0.md`  
**Aktuális Python technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b` – `Add minimal Wellspring resource contracts`

Ez a dokumentum az AETERNA projekt aktuális, élő munkatervét tartalmazza.

A v6.1 fő változása:

> **a végleges vagy hosszú távon fenntartható authoritative rules runtime nyelvi és integrációs döntési kapuja megelőzi a további jelentős gameplay-engine bővítést.**

A Python minimal engine megmarad működő referenciaimplementációnak. A fő összehasonlítandó termékruntime-jelöltek:

- Python sidecar + Godot kliens;
- Godot .NET/C# authoritative runtime;
- szükség esetén szűk GDScript proof.

A Wellspring production integráció nem törlődött; a döntési kapu után a kiválasztott runtime-ág első gameplay-feladata.

---

## 1. Forrás- és dokumentumelsőbbség

A projekt döntéseinél az alábbi sorrendet kell követni.

1. **Hivatalos szabályforrások**
   - `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
   - `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`
2. **Hosszú távú termékcél**
   - `Aeterna game engine/docs/AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`
3. **Aktuális projektirány és prioritások**
   - jelen dokumentum, v6.1
4. **Aktuális runtime-nyelvi döntési kapu**
   - `Aeterna game engine/docs/RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
5. **Aktuális engine-checkpoint**
   - `Aeterna game engine/docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`
6. **Technikai státusz- és döntési dokumentumok**
   - `TECHNOLOGY_DECISIONS.md`
   - `DECISION_MAP.md`
   - `CURRENT_PROTOTYPE_STATUS.md`
   - `CURRENT_CONTRACT_STATUS.md`
   - `CURRENT_OPEN_QUESTIONS.md`
7. **Open Questions dokumentumpár**
   - `OPEN_QUESTIONS.md`
   - `OPEN_QUESTIONS_DECISIONS.md`
8. **Hosszú specifikációk és történeti referenciák**

Eltérés esetén az aktív v6.1 projektterv és a runtime-nyelvi döntési kapu felülírja a v6.0 korábbi prioritási sorrendjét, de nem írhatja felül a hivatalos játékszabályokat.

---

## 2. Projektirány

Az AETERNA több elkülönített rétegből áll:

- fizikai TCG és hivatalos szabályrendszer;
- kártyaadatbázis és strukturált adatforrások;
- Python adatpipeline és runtime package tooling;
- működő Python minimal rules-engine referencia;
- Godot loader-, debug- és kliensalap;
- lehetséges Godot .NET/C# termékruntime;
- lehetséges Python sidecar termékruntime;
- régi Python motor referenciaágként;
- dokumentációs, audit- és tervezési rendszer.

### 2.1 Jelenlegi biztos implementációs bázis

A Python minimal engine jelenleg bizonyítottan működik és tartalmaz:

- authoritative MatchState-et;
- card instance registryt;
- state invariantokat;
- action request/response alapot;
- draw és end-turn transitiont;
- typed eventeket;
- player-visible snapshotot;
- Domain topológiát és occupancyt;
- structural Entity placementet;
- activity state-et;
- izolált Wellspring resource contractot;
- determinisztikus AI trajectoryt.

Ez a bázis:

- nem törlendő;
- nem archiválandó;
- comparison reference és expected-output orákulum;
- későbbi AI/batch és differential testing alap;
- akkor is értékes, ha a termékruntime C# lesz.

### 2.2 Ami még nyitott

Nem dőlt el véglegesen, hogy a 0.0.1 authoritative játék-runtime-ja:

- Python sidecar lesz;
- C#/.NET lesz Godoton belül;
- GDScript vagy más hibrid modell lesz.

A döntést nem pusztán vélemény, hanem azonos scenario, tesztek, Windows packaging és karbantarthatósági összevetés alapján kell meghozni.

### 2.3 Runtime package és Godot

A runtime package–Godot alapozási szakasz elkészült:

- Python package build;
- validáció;
- valós card/deck/lookup adat;
- Godot loader és registry;
- sample snapshot/legal action/event fixture;
- debug nézetek;
- smoke tesztek.

Ez a réteg minden vizsgált runtime-modellnél megtartandó lehet.

---

## 3. Hosszú távú cél: AETERNA 0.0.1

A 0.0.1 az első zárt, használható, könnyen elindítható digitális tesztkiadás célverziója.

Fő elemei:

- egyszerű Windows-indítás;
- játékos- és tesztelői mód;
- teljes ember–AI mérkőzés;
- több AI-nehézség;
- kezdőpaklik és tutorialok;
- pakliszerkesztő és gyűjtemény;
- helyi tesztgazdaság és booster rendszer;
- profil és mentés;
- részletes logok;
- replay- és reprodukálhatósági alap;
- hibajelentési csomag;
- használható Godot UI.

A runtime-nyelvi döntés azért kritikus, mert közvetlenül befolyásolja:

- a Windows-csomagolást;
- az egyszerű indítást;
- a Godot-integrációt;
- a crash- és processkezelést;
- a teljes gameplay-engine migrációs költségét;
- a hosszú távú karbantarthatóságot.

---

## 4. Aktuális technikai bázis

Báziscommit:

- `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`
- `Add minimal Wellspring resource contracts`

Tesztállapot a checkpointnál:

- 59 Python tesztmodul izolált futása zöld;
- 333 izolált teszt zöld;
- minimal engine smoke zöld;
- AI-vs-AI text és JSON smoke zöld;
- két azonos JSON-futás determinisztikusan azonos.

Ismert külön tesztinfrastruktúra-adósság:

- `test_finds_xlsx_files_only_in_source_directory`
- `test_lists_sheets_in_read_only_data_only_mode`

Ezek a monolitikus discovery két ismert sorrendfüggő mock-eltérései.

---

## 5. Roadmap és új döntési kapu

### M1 – Minimal determinisztikus engine-alapok

**Állapot:** jelentős Python referenciaalap elkészült.

### M2 – Player view és board contract

**Állapot:** első jelentős szakasz elkészült.

### TG1 – Runtime engine language decision gate

**Állapot:** új elsődleges technológiai prioritás.

Feladata:

- tanulóprogram-audit;
- Python sidecar proof;
- Godot .NET/C# proof;
- szükség esetén GDScript proof;
- Windows packaging;
- közös scenario és differential comparison;
- emberi döntés.

### M3 – Első tényleges gameplay actionök

**Állapot:** a TG1 döntési kapu után folytatandó.

Első gameplay-lánc:

1. Wellspring runtime integráció;
2. player-visible Wellspring summary;
3. Beáramlás precondition;
4. Beáramlás transition és event;
5. Magnitúdó-preflight;
6. Aura-payment;
7. Entitás kijátszási precondition;
8. `play_card`;
9. Entitás Domainba helyezése;
10. entry-state és eventek.

További roadmap:

- M4 – fázisok, prioritás és reakciók;
- M5 – harc és győzelmi feltételek;
- M6 – első játszható vertical slice;
- M7 – teljes alapjátékos tesztprogram;
- M8 – meta- és termékrendszerek;
- M9 – 0.0.1 release candidate.

---

## 6. Aktuális prioritási sorrend

### P1 – Tanulóprogramok read-only auditja

A következő Codex-feladat első szakasza.

Kötelezően rögzítendő:

- projekt és forrás;
- commit/tag/verzió;
- licenc;
- nyelvek;
- Godot-verzió;
- state authority;
- rules runtime;
- Python/C#/GDScript szerep;
- bridge;
- process lifecycle;
- packaging;
- Windows támogatás;
- tesztek;
- clean-room módon használható minta;
- attribution.

A tanulóprogramok nem kerülnek automatikusan az AETERNA GitHub repositoryba.

### P2 – Közös comparison scenario

Kötelező lépések:

1. initial state;
2. `draw_card` P1;
3. `end_turn`;
4. `draw_card` P2;
5. player-visible snapshotok;
6. typed event log;
7. stale state version rejection;
8. determinisztikus ismétlés;
9. canonical JSON összevetés.

### P3 – Python sidecar + Godot proof

Vizsgálandó:

- stdin/stdout JSONL;
- vagy localhost TCP + JSON;
- handshake;
- request/response;
- process lifecycle;
- kontrollált shutdown;
- crash/version mismatch;
- Windows packaging.

### P4 – Godot .NET/C# rules proof

Vizsgálandó:

- UI-tól független C# rules library;
- ugyanazon scenario;
- kompatibilis contractok;
- unit tesztek;
- Godot .NET integráció;
- Windows export;
- Python outputtal való differential comparison.

### P5 – Opcionális GDScript proof

Csak akkor:

- ha az audit indokolja;
- ha az első két proof nem elég;
- ha egyetlen transitionre korlátozható.

### P6 – Döntési jelentés

A jelentés értékelje:

- szabályhelyesség;
- contracthűség;
- determinisztika;
- tesztelhetőség;
- hidden-information;
- Godot-integráció;
- Windows packaging;
- crash- és processkezelés;
- teljesítmény és latency;
- build reprodukálhatóság;
- emberi karbantarthatóság;
- Codex kódminőség;
- portolási költség;
- AI/batch alkalmasság;
- licenc.

A végleges döntés emberi jóváhagyással történik.

### P7 – Wellspring runtime integráció

**Státusz:** `queued_after_language_gate`

Változatlan cél:

- `wellspring_card_instance_ids`;
- üres initial Wellspring;
- MatchState és invariant integráció;
- authoritative zónatagság;
- resource summary elérés;
- még nincs Beáramlás action.

---

## 7. Párhuzamos munkasávok

### 7.1 Codex nélküli dokumentációs és elemzési sáv

Aktív:

- `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` közös triázsa;
- tanulóprogram-forrás- és licencleltár előkészítése;
- comparison mátrix pontosítása;
- `ABILITY_MODULE_SYSTEM.md` auditja;
- contract-specifikáció konszolidációja;
- dokumentációs státuszok rendezése;
- hivatalos szabályforrásból megválaszolható kérdések ellenőrzése.

### 7.2 Kártyaadatbázis és audit

Továbbra is külön munkasáv:

- főforrás-alapú kártyaaudit;
- structured és természetes szöveg összevetése;
- adat-, engine-, szabályértelmezési és balanszhiba elkülönítése;
- runtime package és lookupok fenntartása.

### 7.3 Runtime package és Godot

Fenntartandó:

- exporter és publish pipeline;
- package validáció;
- loader és registry;
- debug nézetek;
- smoke tesztek.

Nagy player UI-fejlesztés csak a runtime-nyelvi döntés és stabilabb player-facing contractok után induljon.

### 7.4 Régi engine review

Csak külön döntéssel emelhető át:

- algoritmus;
- AI-minta;
- diagnostics;
- balanszmetrika;
- effectlogika.

---

## 8. Amit most nem csinálunk

- teljes Python → C# port a comparison előtt;
- teljes GDScript engine;
- két teljes rules engine párhuzamos építése;
- jelentős új gameplay-réteg kizárólag Pythonban a döntés előtt;
- végleges nyelvválasztás proof nélkül;
- tanulóprogram-kód automatikus bemásolása;
- teljes UI/UX;
- online mód;
- felhőmentés;
- minden kártyaképesség implementálása;
- nagy általános refaktor;
- dokumentációs cleanup és runtime kód keverése egy commitban.

---

## 9. Licenc- és forráskezelés

A letöltött tanulóprogramok külön helyi kutatási források.

Alapelvek:

- ne kerüljenek automatikusan az AETERNA repositoryba;
- auditálni kell a licencet;
- rögzíteni kell a vizsgált verziót;
- alapértelmezetten clean-room architektúraminta készüljön;
- kódátvétel csak külön döntéssel;
- attribution és license notice kötelezettség megőrzendő;
- assetlicenc külön ellenőrzendő.

---

## 10. Tesztelési alapelvek

A comparison során:

- közös fixture;
- common expected semantics;
- Python reference output;
- C# unit tests;
- bridge lifecycle tests;
- deterministic JSON;
- hidden-information tests;
- stale state rejection;
- structured differential report;
- Windows launch proof;
- Git státusz és scope ellenőrzés.

A Python referencia tesztkészlete megmarad.

---

## 11. Döntési kapu elfogadási feltételei

A TG1 csak akkor zárható le, ha:

- a tanulóprogram-audit elkészült;
- a közös scenario rögzített;
- a Python reference futás reprodukálható;
- a Python sidecar proof elkészült;
- a C# proof elkészült;
- Windows-indítás és packaging legalább prototípusszinten bizonyított;
- contract- és teszteredmények összevethetők;
- korlátok és licencek dokumentáltak;
- A/B/C javaslat készült;
- a felhasználó jóváhagyta a végleges irányt.

---

## 12. Következő dokumentációs feladatok

1. `OPEN_QUESTIONS.md` és `OPEN_QUESTIONS_DECISIONS.md` OQ-azonosítós közös triázsa.
2. Tanulóprogram-audit sablon és helyi leltárstruktúra.
3. Ability module system aktuális státusza.
4. Contract-specifikáció fokozatos konszolidációja.
5. Történeti checkpointnapló formázási tisztítása.
6. Projekt-térkép és README-k frissítése a v6.1-re.

---

## 13. Rövid aktuális összefoglaló

**Hosszú távú cél:** AETERNA 0.0.1 zárt tesztkiadás.  
**Működő referencia:** Python minimal rules engine.  
**Következő Codex-prioritás:** Python sidecar vs Godot .NET/C# comparison.  
**Opcionális proof:** minimal GDScript transition.  
**Embedded Python:** kutatási, későbbi irány.  
**Gameplay-fejlesztés:** a nyelvi/runtime döntési kapu után folytatódik.  
**Első utána következő gameplay-feladat:** Wellspring production integráció.  
**Codex nélküli aktív sáv:** dokumentáció, audit, szabály- és contract-előkészítés.
