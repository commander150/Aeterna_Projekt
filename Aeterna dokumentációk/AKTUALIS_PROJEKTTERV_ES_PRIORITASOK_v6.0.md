# AETERNA – Aktuális Projektterv és Prioritások

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 6.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív projektirányító és prioritási dokumentum  
**Felváltott dokumentum:** `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`  
**Aktuális technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b` – `Add minimal Wellspring resource contracts`

Ez a dokumentum az AETERNA projekt aktuális, élő munkatervét tartalmazza.

Feladata:

- a projekt jelenlegi elsődleges fejlesztési irányának rögzítése;
- az elkészült technikai alapok és a még hiányzó rendszerek elhatárolása;
- a rövid, közép- és hosszú távú célok összekapcsolása;
- a következő programozási függőségi lánc meghatározása;
- a dokumentációs, kártyaadat-, Godot- és régi engine munkasávok helyének tisztázása;
- annak megakadályozása, hogy egy korábbi projektállapotot leíró dokumentum felülírja a jelenlegi irányt.

Ez a dokumentum nem hivatalos játékszabály, nem technikai API-specifikáció és nem részletes commitnapló.

---

## 1. Forrás- és dokumentumelsőbbség

A projekt döntéseinél az alábbi sorrendet kell követni.

1. **Hivatalos szabályforrások**
   - `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
   - `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`
2. **Hosszú távú termékcél**
   - `Aeterna game engine/docs/AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`
3. **Aktuális projektirány és prioritások**
   - jelen dokumentum, v6.0
4. **Aktuális engine-checkpoint**
   - `Aeterna game engine/docs/checkpoints/CURRENT_ENGINE_CHECKPOINT.md`
5. **Technikai specifikációk és döntési dokumentumok**
   - architektúra;
   - runtime package;
   - contractok;
   - technológiai döntések;
   - nyitott kérdések.
6. **Régi dokumentumok és archív referenciák**
   - csak háttér- vagy összevetési forrásként használhatók.

Ha egy régebbi terv vagy dokumentum eltér a jelenlegi hivatalos főforrásoktól, a 0.0.1 célállapottól vagy a v6.0 projekttervtől, akkor a régebbi dokumentum nem irányadó.

---

## 2. A projekt jelenlegi iránya

Az AETERNA továbbra is több, elkülönített rétegből álló projekt:

- fizikai TCG és hivatalos szabályrendszer;
- kártyaadatbázis és strukturált adatforrások;
- új determinisztikus Python rules engine;
- runtime package és adatpipeline;
- Godot fogyasztói, debug- és későbbi kliensréteg;
- régi Python szimulációs motor referenciaágként;
- dokumentációs, audit- és tervezési rendszer.

### 2.1 Elsődleges aktív fejlesztési tengely

A jelenlegi elsődleges programozási irány:

> **az `Aeterna game engine/python/` alatt épülő determinisztikus, headless, contract-first szabálymotor stabilizálása és fokozatos bővítése.**

Ez az engine:

- authoritative MatchState-et kezel;
- card instance azonosságot használ;
- invariánsokkal védi az állapotot;
- legal action és action request contractokra épül;
- typed eventeket állít elő;
- player-visible és debug projekciókat választ szét;
- determinisztikus AI-vs-AI epizódokat támogat;
- fokozatosan közelít a teljes szabályhű játékmenethez.

### 2.2 Runtime package és Godot helye

A runtime package és a Godot ág továbbra is aktív és megtartandó.

Jelenlegi szerepük:

- a validált kártya- és lookup-adatok programbiztos közvetítése;
- Python és Godot közötti contract-határ;
- Godot loader, registry és debug nézetek;
- későbbi játékos UI és interaktív kliens alapja.

A Godot azonban jelenleg nem az elsődleges rules-engine fejlesztési hely.

A szabályok authoritative végrehajtási helye a jelenlegi irány szerint a Python engine. A Godot később action requesteket küld és player-visible állapotot jelenít meg; nem találgathat vagy duplikálhat szabálylogikát.

### 2.3 Régi Python szimulációs motor

A régi Python motor státusza:

- `OLD_ENGINE_REVIEW`
- `OLD_ENGINE_REFERENCE`

Megtartandó értékei:

- AI-vs-AI és batch tapasztalatok;
- balanszfigyelési minták;
- diagnosztikai és naplózási megoldások;
- régi effectlogikai előzmények;
- későbbi összevetési és migrációs forrás.

Nem elsődleges új fejlesztési alap, és nem szabad automatikusan összekeverni az új rules engine-nel.

---

## 3. Hosszú távú cél: AETERNA 0.0.1

Az AETERNA 0.0.1 nem a jelenlegi contract- vagy prototípusverzió folytatása.

A 0.0.1 az első zárt, használható, könnyen elindítható digitális tesztkiadás célverziója.

A célállapot főbb elemei:

- egyszerű Windows-indítás;
- játékos- és tesztelői mód;
- teljes ember–AI mérkőzés;
- több AI-nehézség;
- alapjátékos kezdőpaklik és tutorialok;
- pakliszerkesztő és gyűjtemény;
- helyi tesztgazdaság és booster rendszer;
- profil és mentés;
- részletes logok;
- reprodukálhatóság és replay-alap;
- hibajelentési csomag;
- használható Godot UI.

A közvetlen jelenlegi cél nem a 0.0.1 minden funkciójának párhuzamos fejlesztése, hanem az ehhez szükséges stabil szabálymotor felépítése.

---

## 4. Aktuális technikai bázis

A jelen dokumentum bázisa:

- commit: `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`
- commitüzenet: `Add minimal Wellspring resource contracts`
- dátum: 2026-07-14

### 4.1 Elkészült engine-alapok

Az új minimal engine jelenleg rendelkezik:

- expected state version guarddal;
- engine context summaryval;
- stabil card instance ID- és record-modellel;
- deck, hand és discard instance-listákkal;
- authoritative card instance registryvel;
- ZoneMove contracttal;
- draw transitionnel deckből kézbe;
- generic engine event envelope-pal;
- typed `zone_move` eseménnyel;
- typed `turn_transition` eseménnyel;
- determinisztikus state version és event sequence kezeléssel;
- canonical AI episode trajectoryval;
- rejected-step támogatással;
- determinisztikus JSON epizóddal;
- player-visible snapshot v2-vel;
- saját kéz és ellenfélkéz megfelelő láthatósági elhatárolásával;
- deck count-only projekcióval;
- public discard projekcióval;
- hat Áramlatos Domain topológiával;
- Horizont-, Zenit- és Pecsét-pozícióreferenciákkal;
- Domain occupancy contracttal;
- occupancy és card instance registry kétirányú invariánsával;
- public player-visible Domain board projekcióval;
- strukturális Entitás-elhelyezési option contracttal;
- canonical `activity_state` mezővel;
- `active` és `exhausted` állapottal;
- izolált Wellspring-state contracttal;
- izolált Magnitúdó- és elérhető Aura-összesítéssel.

### 4.2 Jelenlegi működő actionök

A minimal engine aktív runtime actionjei:

- `draw_card`
- `end_turn`

A strukturális Entitás-elhelyezési optionök még nem legal actionök, és nem hajtanak végre állapotváltozást.

### 4.3 Jelenlegi tesztállapot

A `84a7e8f4` checkpointnál:

- 59 Python tesztmodul futott izolált folyamatban;
- 333 teszt volt zöld;
- minimal engine smoke sikeres;
- 8 lépéses AI-vs-AI text és JSON smoke sikeres;
- a két azonos AI JSON-futás determinisztikusan azonos.

A monolitikus unittest discoveryben két ismert sorrendfüggő XLSX mock-probléma marad:

- `test_finds_xlsx_files_only_in_source_directory`
- `test_lists_sheets_in_read_only_data_only_mode`

Ezek külön tesztinfrastruktúra-feladatot jelentenek. Nem tekintendők az új rules engine aktuális regressziójának, amíg minden modul izoláltan zöld.

---

## 5. Mérföldkő-rétegek

A projekt három tervezési szinten működik.

### 5.1 Hosszú távú termékmérföldkő

- AETERNA 0.0.1

### 5.2 Technikai roadmap

- M1 – minimális determinisztikus engine-alapok
- M2 – player view és board contract
- M3 – első tényleges gameplay actionök
- M4 – fázisok, prioritás és reakciók
- M5 – harc és győzelmi feltételek
- M6 – első játszható vertical slice
- M7 – teljes alapjátékos tesztprogram
- M8 – meta- és termékrendszerek
- M9 – 0.0.1 release candidate

### 5.3 Szűk aktuális feladatsor

A tényleges fejlesztés egyszerre csak egy kis, tesztelhető contractot vagy transitiont módosítson.

---

## 6. Mérföldkő-státusz

### M1 – Minimális determinisztikus engine-alapok

**Állapot:** nagyrészt elkészült, további erőforrás- és zónaalapokkal bővül.

Elkészült:

- state identity és version guard;
- card instance registry;
- zónatagság és húzás;
- typed event alap;
- session és environment;
- state invariant rendszer;
- AI trajectory és determinisztikus smoke.

Még szükséges:

- Wellspring runtime integráció;
- Beáramlás;
- további canonical zónák;
- stabil resource preflight;
- általánosabb transition pattern.

### M2 – Player view és board contract

**Állapot:** első jelentős szakasza elkészült.

Elkészült:

- player-visible snapshot v2;
- hidden-information alap;
- hat Áramlatos Domain topológia;
- occupancy;
- public board projection;
- strukturális Entitás-placement optionök.

Még szükséges:

- player-visible Wellspring projection;
- activity state board-projekció;
- Pecsét aktuális állapotmodell;
- teljes legal placement és action integration.

### M3 – Első tényleges gameplay actionök

**Állapot:** előkészítés alatt.

A következő első gameplay-lánc:

1. Wellspring runtime integráció;
2. Beáramlás precondition;
3. Beáramlás transition és event;
4. Magnitúdó-preflight;
5. Aura-payment contract;
6. Entitás kijátszási precondition;
7. `play_card` action;
8. Entitás Domainba helyezése;
9. entry-state és kapcsolódó eventek.

M4–M9 jelenleg későbbi roadmap-szakasz.

---

## 7. Aktuális prioritási sorrend

### P1 – Wellspring runtime integráció

Következő közvetlen programozási feladat:

- `wellspring_card_instance_ids` bevezetése PlayerState-be;
- initial üres Wellspring setup;
- MatchState és state-invariant integráció;
- listás zónák és Wellspring közös authoritative tagsági ellenőrzése;
- resource summary canonical elérése;
- továbbra is Beáramlás action nélkül.

### P2 – Player-visible Wellspring summary

A játékos számára látható legyen:

- saját és ellenfél Magnitúdója;
- saját és ellenfél Ősforrás-lapszáma;
- Aktív és Kimerült források publikus összesítése a hivatalos láthatósági szabály szerint;
- Card_ID- és instance-lista szivárgása nélkül.

A pontos láthatósági policy külön ellenőrzendő a hivatalos főforrásból.

### P3 – Beáramlás precondition contract

Ellenőrizendő:

- megfelelő fázis és prioritás;
- körönkénti maximum;
- source saját kézben;
- opcionális döntés;
- cél saját Ősforrás;
- belépési activity state;
- hidden visibility.

Ez még nem transition.

### P4 – Beáramlás transition és typed event

A precondition után:

- hand → Wellspring zónamozgás;
- listák és zone indexek frissítése;
- visibility és activity state beállítása;
- typed ZoneMove vagy specializált transition event;
- state version és event sequence;
- player-visible és debug projekció.

### P5 – Erőforrás-preflight és Aura-payment

Külön rétegekben:

- Magnitúdó-küszöb;
- elérhető Aura;
- typed Aura;
- Entitás és nem-Entitás eltérő fizetési szabályai;
- payment source selection;
- kimerítés;
- payment eventek;
- Rezonancia és más speciális rétegek később.

### P6 – Entitás kijátszási legalitás és `play_card`

Csak akkor induljon, amikor:

- placement option;
- timing;
- Magnitúdó;
- Aura-payment;
- entry state;
- hand → Domain transition

külön contractként vagy stabil preconditionként rendelkezésre áll.

### P7 – Fázisok, prioritás és reakciós ablakok

A jelenlegi minimal turn-modell nem teljes AETERNA körstruktúra.

Később szükséges:

- Ébredés;
- Húzás;
- Főfázis;
- Harc;
- körzárás;
- prioritásváltás;
- reakciós és Burst-ablakok.

### P8 – Harc és győzelmi feltételek

Csak stabil Entitás-state és fázisrendszer után.

---

## 8. Párhuzamos munkasávok

### 8.1 Dokumentáció

Aktív feladatok:

- a v5.1 projektterv felváltása v6.0-val;
- aktuális engine-checkpoint fenntartása;
- root és engine README frissítése;
- `CHECKPOINTS.md` későbbi összevonása és időrendi tisztítása;
- elavult Godot-first vagy exporter-first állítások státuszolása;
- nyitott kérdések megőrzése.

### 8.2 Kártyaadatbázis és audit

Továbbra is fontos, de külön munkasáv:

- hivatalos főforrás-alapú kártyaaudit;
- structured és természetes kártyaszöveg összevetése;
- kártyaadat-, engine-, szabályértelmezési és balanszhiba elkülönítése;
- runtime package és lookupok fenntartása.

A tömeges kártyaátírás nem keverhető az engine-contract fejlesztéssel.

### 8.3 Runtime package és Godot

Fenntartandó:

- exporter és publish pipeline;
- runtime package validáció;
- Godot loader és registry;
- debug nézetek;
- smoke tesztek.

Nagy Godot UI-fejlesztés csak stabilabb rules engine és player-facing contract után induljon.

### 8.4 Régi engine review

A régi motorból csak külön döntéssel emelhető át:

- algoritmus;
- AI-minta;
- diagnosztika;
- balanszmetrika;
- effectlogika.

A régi kód nem automatikusan canonical.

---

## 9. Amit most nem csinálunk

A jelenlegi fázisban nem cél:

- teljes UI/UX;
- teljes Godot játékprogram;
- online vagy hálózati mód;
- ember–ember játék;
- felhőmentés;
- ranglista vagy matchmaking;
- valós pénzes gazdaság;
- teljes booster- és collection-rendszer;
- minden kártyaképesség egyidejű implementálása;
- nagy, általános engine-refaktor;
- régi motor automatikus migrálása;
- egyetlen nagy `play_card` implementáció minden előfeltétel nélkül;
- timing, payment és card-text ellenőrzés összekeverése;
- runtime kód, dokumentációs cleanup és kártyaaudit egy commitban;
- tesztek törlése pusztán a darabszám csökkentése miatt.

---

## 10. Tesztelési és minőségi alapelvek

### 10.1 Kötelező regressziós védelem

Minden kis engine-lépésnél:

- célzott unit vagy contract teszt;
- közvetlen regressziós kör;
- minden Python tesztmodul izolált futtatása;
- minimal engine smoke;
- AI-vs-AI text és JSON smoke;
- determinisztikus ismétlés;
- git status ellenőrzés.

### 10.2 Monolitikus discovery

A monolitikus discovery továbbra is futtatandó és jelentendő.

A két ismert XLSX mock-hiba külön backlog:

- ne legyen elhallgatva;
- ne blokkolja az engine-commitot, ha csak ez a két ismert sorrendfüggő eltérés marad;
- később külön tesztinfrastruktúra-feladatban javítandó.

### 10.3 Tesztfájlok

A tesztek alapértelmezés szerint regressziós védelemként maradnak.

Törlés csak akkor indokolt, ha:

- a teszt kizárólag eltávolított viselkedést vizsgál;
- bizonyíthatóan teljes duplikáció;
- értelmetlen no-op;
- hibás vagy félrevezető contractot rögzít.

A későbbi rendezési cél:

- `tests/unit/contracts/`
- `tests/unit/engine/`
- `tests/unit/invariants/`
- `tests/integration/ai/`
- `tests/smoke/`
- közös fixtures és helpers.

Általános tesztrendezés csak külön, read-only audit után induljon.

---

## 11. GitHub és munkarend

### 11.1 Commit-elv

Egy commit egy jól körülírható célt szolgáljon.

Ne keveredjen egy commitba:

- runtime implementáció;
- dokumentációs nagytakarítás;
- kártyaadat-javítás;
- Godot UI-fejlesztés;
- generált output;
- általános tesztrendezés.

### 11.2 Fejlesztési feladatok

A programozási feladat legyen:

- szűk;
- contract-first;
- explicit scope-pal;
- explicit nem-célokkal;
- tesztekkel;
- smoke elvárásokkal;
- commitfeltételekkel;
- végső jelentési követelményekkel.

### 11.3 Dokumentáció

Dokumentációs változás külön commitban történjen.

A dokumentum:

- jelölje a verzióját és státuszát;
- ne írja felül a hivatalos szabályforrást;
- őrizze meg a nyitott kérdéseket;
- különítse el a kész, tervezett és nem implementált állapotokat.

---

## 12. Következő döntési kapuk

### 12.1 Wellspring-integráció előtt

Ellenőrizendő:

- PlayerState canonical mező neve;
- owner/controller szabály Wellspringben;
- hidden visibility és player projection;
- zone index szerepe;
- initial üres setup;
- Magnitúdó és Aura summary elérési helye.

### 12.2 Beáramlás előtt

Hivatalos forrásból explicit rögzítendő:

- belépési Aktív/Kimerült állapot;
- körönkénti használat nyilvántartása;
- pontos fázis és prioritás;
- event- és projection-policy.

### 12.3 Aura-payment előtt

Rögzítendő:

- canonical Aura-típusok;
- Entitások Aether/Semleges fizetése;
- nem-Entitások Birodalmi Aura-korlátja;
- payment source selection;
- atomikus kimerítés és rollback;
- Rezonancia és ideiglenes Aura későbbi rétege.

### 12.4 `play_card` előtt

Kötelezően rendelkezésre kell állnia:

- source eligibility;
- timing és priority;
- Magnitúdó-preflight;
- Aura-payment;
- structural placement;
- card-text restriction policy;
- entry-state policy;
- atomic state transition;
- typed eventek;
- player-visible projection.

---

## 13. Következő checkpoint elfogadási feltételei

A következő engine-checkpoint akkor zárható le, ha:

- Wellspring integrálva van PlayerState-be és MatchState-be;
- minden production player üres Wellspringgel indul;
- a state-invariánsok kétirányúan védik a Wellspring-lista és registry kapcsolatát;
- Magnitúdó és elérhető Aura canonical summaryként lekérhető;
- draw és end_turn változatlan marad;
- nincs Beáramlás action;
- nincs Aura-payment;
- nincs `play_card`;
- minden Python tesztmodul izoláltan zöld;
- smoke és determinisztikus AI epizód zöld;
- a két ismert XLSX discovery-eltérésen kívül nincs új regresszió;
- dokumentáció és munkafa tiszta.

---

## 14. Rövid aktuális összefoglaló

**Elsődleges cél:** stabil, determinisztikus és szabályhű Python game engine.  
**Hosszú távú cél:** AETERNA 0.0.1 zárt, játszható tesztkiadás.  
**Aktuális mérföldkő:** M1 vége / M2 első szakasza / M3 előkészítése.  
**Legutóbbi technikai bázis:** `84a7e8f4`.  
**Következő programozási feladat:** Wellspring runtime integráció.  
**Következő gameplay-lánc:** Wellspring → Beáramlás → erőforrás-preflight → payment → Entitás kijátszása.  
**Godot státusza:** megtartandó fogyasztói és későbbi kliensréteg, nem jelenlegi authoritative szabálymotor.  
**Régi engine státusza:** review és referencia.  
**Tesztelési alap:** izolált modulok + smoke + determinisztikus AI epizód.  
**Jelenlegi ismert tesztinfrastruktúra-hiba:** két sorrendfüggő XLSX mock-eltérés.
