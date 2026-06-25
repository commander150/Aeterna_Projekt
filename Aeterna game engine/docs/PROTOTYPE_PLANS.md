# AETERNA Game Engine – Prototype Plans

Ez a dokumentum az AETERNA Game Engine prototípusainak és következő technikai fejlesztési lépéseinek munkaterve.

Nem checkpoint-napló.

Nem teljes architektúra.

Nem végleges rules engine specifikáció.

Nem Codex-feladatlista önmagában.

Feladata, hogy összefogja:

- mi készült már el prototípusként;
- milyen prototípusok következhetnek;
- melyik prototípus mit bizonyít;
- melyik prototípus mit nem bizonyít;
- milyen smoke test vagy ellenőrzés kell hozzá;
- mikor adható a feladat Codexnek;
- mikor kell előbb emberi döntés vagy ChatGPT-terv.

Kapcsolódó fő dokumentumok:

- DECISION_MAP.md
- ARCHITECTURE.md
- TECHNOLOGY_DECISIONS.md
- CONTRACT_SPECIFICATION.md
- RUNTIME_PACKAGE_SPECIFICATION.md
- ABILITY_MODULE_SYSTEM.md
- CHECKPOINTS.md
- OPEN_QUESTIONS.md

---

## 1. Prototípus-alapelv

Az AETERNA Game Engine fejlesztése kis, ellenőrizhető prototípusokkal haladjon.

Egy prototípus akkor hasznos, ha:

- pontosan megmondja, mit akar bizonyítani;
- kicsi és visszafordítható;
- nem kever több nagy döntést egybe;
- van hozzá smoke test vagy unit test;
- nem írja felül a hivatalos szabályforrásokat;
- nem indít tömeges refaktort;
- nem mozgat vagy töröl fájlokat előzetes döntés nélkül;
- nem zár le nyitott architektúra-kérdést emberi döntés nélkül.

A prototípus nem végleges rendszer.

A prototípus célja döntési bizonyíték gyűjtése.

---

## 2. Jelenlegi prototípus-állapot

A checkpointok alapján már bizonyított:

- Python sample runtime package generator működik.
- Python unit test zöld.
- sample_runtime_package generálás működik.
- Godot runtime package loader működik.
- Godot package loader smoke test zöld.
- Godot sample contracts loader működik.
- sample contracts smoke test zöld.
- Snapshot viewer debug nézet működik.
- Legal action debug panel működik.
- Event log debug view működik.
- Headless Godot smoke testek explicit logfájllal működnek.

Ez még nem bizonyítja:

- teljes szabálymotor működését;
- legal actionök szabályból történő kiszámítását;
- action request végrehajtását;
- kártyaképességek futtatását;
- ability execution rendszert;
- AI döntéshozatalt;
- AI-vs-AI batch tesztet;
- balansztesztet;
- végleges UI-t;
- PvP-t;
- teljes AETERNA kártyaadatbázis futtatását.

---

## 3. Már elkészült prototípusok

### 3.1 Python sample runtime package generator

Státusz: elkészült, v0.1 checkpointban rögzítve.

Bizonyítja:

- Python képes sample runtime package-et generálni;
- többfájlos package szerkezet előállítható;
- manifest, cards, decks, lookups, aliases, ability registry, engine support, diagnostics és build report létrehozható;
- unit test futtatható;
- determinisztikus sample adatút kialakítható.

Nem bizonyítja:

- teljes adatbázis feldolgozását;
- végleges runtime package schema-t;
- teljes exportvalidációt;
- ability executiont;
- rules engine-t.

Következő kapcsolódó lépések:

- sample package schema tisztítása;
- full package előkészítő vizsgálat;
- exportprofilok előkészítése;
- diagnostics erősítése.

---

### 3.2 Godot runtime package loader

Státusz: elkészült, v0.1 checkpointban rögzítve.

Bizonyítja:

- Godot képes betölteni a sample runtime package-et;
- cards, decks, lookups, ability registry és diagnostics adatok registry-szerűen kezelhetők;
- blocking_errors és warnings olvashatók;
- scene-alapú debug futtatás működik;
- headless smoke test működik.

Nem bizonyítja:

- Godot teljes rules engine alkalmasságát;
- action executiont;
- AI-t;
- teljes játék UI-t.

Következő kapcsolódó lépések:

- card reference resolution;
- package + sample contracts összekapcsolása;
- missing card reference diagnostics;
- unified dashboard.

---

### 3.3 Sample contracts loader

Státusz: elkészült, v0.2 checkpointban rögzítve.

Bizonyítja:

- Godot képes sample snapshot, legal actions és event log contractok betöltésére;
- match_id és snapshot_ref alapú ellenőrzés lehetséges;
- sample contracts smoke test futtatható;
- statikus contractok debug nézetekhez használhatók.

Nem bizonyítja:

- valódi match state generálását;
- legal actionök szabályból történő kiszámítását;
- event log valódi játékból történő előállítását;
- action request feldolgozást.

Következő kapcsolódó lépések:

- sample contracts és runtime package közötti card reference feloldás;
- contract consistency smoke test erősítése;
- action request sample hozzáadása.

---

### 3.4 Snapshot viewer

Státusz: elkészült, v0.2 checkpointban rögzítve.

Bizonyítja:

- statikus snapshot megjeleníthető Godot debug nézetben;
- snapshot smoke test futtatható;
- Godot képes snapshot contract adatait egyszerű UI-ban megmutatni.

Nem bizonyítja:

- player-visible visibility biztonságát;
- rejtett információ szűrését;
- valódi match state-ből generált snapshotot;
- végleges játék UI-t.

Következő kapcsolódó lépések:

- card name / type / realm / clan feloldás;
- visibility mezők megjelenítése;
- diagnostics summary megjelenítése;
- később player-visible snapshot teszt.

---

### 3.5 Legal action debug panel

Státusz: elkészült, v0.2 checkpointban rögzítve.

Bizonyítja:

- statikus legal action lista megjeleníthető Godot debug nézetben;
- enabled és disabled actionök száma ellenőrizhető;
- legal action debug panel smoke test futtatható.

Nem bizonyítja:

- legal actionök szabályból számítását;
- action request beküldését;
- action-végrehajtást;
- reaction window működését;
- fizetés vagy targeting tényleges validálását.

Következő kapcsolódó lépések:

- legal action source_card_id feloldás;
- target card_ref feloldás;
- disabled reason megjelenítés;
- action request smoke test.

---

### 3.6 Event log debug view

Státusz: elkészült, v0.2 checkpointban rögzítve.

Bizonyítja:

- statikus event log megjeleníthető Godot debug nézetben;
- event count, first_sequence és last_sequence ellenőrizhető;
- event log smoke test futtatható.

Nem bizonyítja:

- event log valódi rules engine-ből történő generálását;
- replayt;
- visibility szűrést;
- balance eventek működését.

Következő kapcsolódó lépések:

- card reference resolution event source és target mezőkön;
- event layer megjelenítés;
- diagnostics kapcsolás;
- action response minta eventjeinek megjelenítése.

---

## 3.7 Fejlesztői build pipeline rendezése

Státusz: tervezett következő technikai rendezési lépés.

Ez a lépés nem teljes rules engine, nem teljes runtime package builder és nem publikus release pipeline.

Célja az eddig külön kezelt technikai adatút egyszerűsítése és hosszabb távú fejlesztői használatra való előkészítése.

A jelenlegi adatút több kézi lépésből áll:

1. XLSX forrásokból export készül.
2. Az exportált adatokból runtime package készül.
3. A runtime package átkerül vagy elérhetővé válik a Godot által fogyasztott mappában.
4. A Godot loader ebből tölti be a sample package-et és a contract fixture-öket.

Ez a korai tesztfázisban hasznos volt, mert minden lépés külön ellenőrizhető volt.

Hosszabb távon viszont a fejlesztői használatban nem cél, hogy a runtime package frissítése több külön kézi folyamatból álljon.

A cél egy későbbi egylépéses vagy kevés lépéses fejlesztői build pipeline előkészítése.

### Bizonyítandó

A build pipeline rendezése azt bizonyítsa, hogy:

- az XLSX exportáló funkció beépíthető az `Aeterna game engine/python/` tooling rétegébe;
- az exportáló nem kötődik kötelezően saját `source/` és `exports/` mappához;
- explicit source és output útvonalak használhatók;
- nem kell újabb állandó XLSX input másolatot létrehozni az engine alatt;
- a Python oldali build output és a Godot oldali consumption copy szerepe tisztán elkülönül;
- a Godot továbbra is runtime package-et fogyaszt, nem XLSX-et;
- a későbbi változásérzékelés / cache beépíthető lesz;
- a korábbi Python és Godot smoke testek nem törnek el.

### Nem cél

Ebben a lépésben nem cél:

- teljes cache-rendszer;
- full card database package;
- publikus release pipeline;
- Godotból indítható Python rebuild gomb;
- runtime package titkosítás vagy integritásvédelem;
- régi Python engine beolvasztása;
- Godot közvetlen XLSX-betöltése;
- teljes rules engine;
- ability execution;
- AI-vs-AI teszt.

### Két sample_runtime_package mappa kezelése

Jelenleg két `sample_runtime_package` mappa létezik:

- Python oldali `sample_runtime_package`
- Godot oldali `sample_runtime_package`

Ezek nem egyenrangú canonical források.

Javasolt értelmezés:

- Python oldali `sample_runtime_package`: `GENERATED_TEST_FIXTURE`
- Godot oldali `sample_runtime_package`: `GODOT_CONSUMPTION_COPY`

A Python oldali mappa a build output / tesztfixture szerepét tölti be.

A Godot oldali mappa a Godot loader fogyasztási példánya.

A Godot oldali package ne legyen kézzel szerkesztett canonical adatforrás.

A Godot oldali package frissítése később a Python build pipeline feladata legyen.

### Kapcsolódó dokumentum

A részletes döntési irány a `RUNTIME_PACKAGE_SPECIFICATION.md` fájlban szerepel:

- `8.1. Fejlesztői build pipeline és sample package mappák kezelése`

### Elvárt ellenőrzés

A pipeline rendezése után legalább az alábbi ellenőrzések szükségesek:

- exporter unit test zöld;
- sample runtime package builder unit test zöld;
- Python sample package build működik;
- Godot consumption package frissíthető;
- Godot package loader smoke test zöld;
- sample contracts smoke test zöld;
- snapshot viewer smoke test zöld;
- legal action debug panel smoke test zöld;
- event log debug view smoke test zöld.

### Codexnek adható?

Igen, de csak célzott, kis lépésként.

Nem szabad úgy kiadni, hogy „rendezd át az egész pipeline-t”.

Első Codex-lépésként csak az exporter funkció új Python tooling alá migrálása és paraméterezése ajánlott, a régi `XLSX export/` mappa törlése nélkül.

---

## 4. Következő prototípusok áttekintése

Javasolt következő prototípusok és technikai rendezési lépések:

1. Fejlesztői build pipeline rendezése
2. Runtime package + sample contracts integration
3. Missing card reference diagnostics
4. Contract consistency smoke test erősítése
5. Unified debug dashboard
6. Action response smoke / action request extension
7. Ability registry support viewer
8. Simple effect module prototype
9. Minimal GDScript rules service
10. Python / GDScript comparison scenario
11. Full runtime package preparation audit

A sorrend nem teljesen merev, de az első lépés most a pipeline rendezése legyen.

Indok:

- az XLSX exportáló, a Python package builder és a Godot consumption package jelenleg még külön kézi láncként viselkedik;
- a két `sample_runtime_package` mappa státuszát tisztázni kell;
- a későbbi integration, dashboard és action response prototípusok stabilabbak lesznek, ha a build output és a Godot consumption copy szerepe előbb rendeződik;
- a Godot továbbra is runtime package-et fogyaszt, nem XLSX-et;
- az exporter funkció áthelyezése az új Python tooling alá előkészíti a későbbi egylépéses fejlesztői buildet.

A pipeline rendezése után érdemes visszatérni a runtime package + sample contracts integrációra.

---

## 5. Prototype 1 – Runtime package + sample contracts integration

### Cél

A runtime package card registry és a sample contracts között tényleges kapcsolat legyen.

A debug nézetek ne csak card_id-t mutassanak, hanem feloldott kártyaadatokat is.

### Bizonyítandó

- sample snapshot card_ref feloldható;
- legal action source_card_id feloldható;
- legal action target card_ref feloldható;
- event source / target card_ref feloldható;
- hiányzó card_id diagnostics bejegyzést generál;
- debug UI olvashatóbbá válik.

### Javasolt mezők megjelenítése

- card_id
- name_hu
- card_type
- realm
- clan
- support_status

### Nem cél

- rules engine;
- legal action számítás;
- action-végrehajtás;
- ability execution;
- AI;
- végleges UI.

### Elvárt ellenőrzés

- meglévő package loader smoke test továbbra is zöld;
- sample contracts smoke test továbbra is zöld;
- snapshot viewer smoke test továbbra is zöld;
- legal action debug panel smoke test továbbra is zöld;
- event log debug view smoke test továbbra is zöld;
- új integration smoke test zöld.

### Codexnek adható?

Igen, ha a feladat pontos fájllistával és tiltásokkal van megadva.

---

## 6. Prototype 2 – Missing card reference diagnostics

### Cél

A rendszer kezelje, ha egy sample contract card_id-ra hivatkozik, de az nincs jelen a runtime package card registryben.

### Bizonyítandó

- missing card reference felismerhető;
- diagnostics entry generálható;
- debug nézetben látható;
- blocking vagy warning státusz külön kezelhető;
- smoke test ellenőrzi a hiányt.

### Nem cél

- automatikus javítás;
- kártyaadatbázis módosítása;
- full validator;
- rules engine.

### Diagnostics jelölt mezők

- category: frontend_contract vagy runtime
- severity: warning vagy error
- blocking: true vagy false
- code: missing_card_reference
- object_ref
- field
- value
- suggested_fix

### Codexnek adható?

Igen, célzott technikai feladatként.

---

## 7. Prototype 3 – Unified debug dashboard

### Cél

Egy Godot debug nézetben egyszerre látható legyen:

- runtime package összefoglaló;
- snapshot összefoglaló;
- legal action lista;
- event log lista;
- diagnostics summary;
- card reference resolution eredménye.

### Bizonyítandó

- több contract egy nézetben összefogható;
- runtime package és sample contracts együtt használható;
- debug célú összesítő UI működik;
- smoke test futtatható.

### Nem cél

- végleges játék UI;
- szabálymotor;
- action végrehajtás;
- animáció;
- PvP;
- AI.

### Javasolt dashboard blokkok

- Package status
- Snapshot summary
- Legal actions
- Event log
- Diagnostics
- Missing references
- Resolved cards

### Elvárt ellenőrzés

- dashboard scene fut;
- dashboard headless smoke test zöld;
- nem töri el a korábbi smoke testeket.

### Codexnek adható?

Igen, de csak akkor, ha a card reference resolution előtte vagy vele együtt világosan definiált.

---

## 8. Prototype 4 – Action response smoke / action request extension

### Cél

A sample action request smoke már elkészült; a következő nyitott rész az action response minta és a request/response kör erősítése.

A statikus legal action listából egy action request minta és egy action response minta kezelése.

Ez még nem valódi rules engine.

### Bizonyítandó

- legal action alapján action request létrehozható;
- request_id és action_id kezelhető;
- validation stub működik;
- success és rejected minta kezelhető;
- action response tartalmazhat events és diagnostics adatot;
- smoke test ellenőrzi az alap contract consistencyt.

### Nem cél

- valódi action-végrehajtás;
- teljes target validáció;
- payment validáció;
- ability execution;
- reaction rendszer;
- match state módosítás.

### Javasolt sample fájlok

- sample_action_request.json
- sample_action_response_ok.json
- sample_action_response_rejected.json

### Elvárt ellenőrzés

- request match_id egyezik;
- snapshot_id egyezik;
- action_id létezik a legal action listában;
- rejected action reason olvasható;
- diagnostics mező olvasható;
- response events listája betölthető.

### Codexnek adható?

Igen, de előtte a CONTRACT_SPECIFICATION.md action request / response szakaszának stabilnak kell lennie.

---

## 9. Prototype 5 – Contract consistency smoke test erősítése

### Cél

A sample runtime package és sample contracts közötti összefüggések gépi ellenőrzése.

### Ellenőrizendő

- manifest olvasható;
- schema_version ismert;
- match_id egyezik snapshot / legal actions / events között;
- legal actions generated_for_snapshot_id snapshotra mutat;
- card references léteznek;
- event indexes rendezettek;
- blocking_errors összesítés helyes;
- diagnostics entries olvashatók;
- missing reference külön tesztelhető.

### Nem cél

- teljes validator;
- full runtime package validáció;
- teljes rules engine validáció.

### Codexnek adható?

Igen.

Ez kifejezetten jó Codex-feladat, ha pontos input/output van megadva.

---

## 10. Prototype 6 – Ability registry support viewer

### Cél

A Godot debug nézet vagy dashboard meg tudja jeleníteni az ability registry és engine support alapinformációkat.

### Bizonyítandó

- ability_registry betölthető;
- ability source_card_id feloldható;
- support_status megjeleníthető;
- unsupported / partial / fallback_required látható;
- diagnostics kapcsolható.

### Nem cél

- ability execution;
- effect futtatás;
- legal action generálás abilityből;
- AI értékelés.

### Javasolt megjelenítés

- ability_id
- source_card_id
- source card name
- module_id
- support_status
- execution_mode
- diagnostics count

### Codexnek adható?

Igen, ha az ability registry jelenlegi sample szerkezete ismert és stabil.

---

## 11. Prototype 7 – Simple effect module prototype

### Cél

Egyetlen vagy néhány nagyon egyszerű effect module demonstrálása.

Ez már közelebb van a rules engine-hez, ezért óvatosan kezelendő.

### Lehetséges első effectek

- draw_cards
- deal_damage_to_entity
- heal_entity
- ward_restore
- ward_break_prevent
- grant_keyword_until_end_of_turn
- create_token_simple

### Bizonyítandó

- structured effect értelmezhető;
- target ellenőrizhető;
- effect végrehajtási stub készíthető;
- event log entry generálható;
- diagnostics generálható;
- snapshot változás minta előállítható.

### Nem cél

- teljes combat;
- teljes reaction rendszer;
- minden keyword;
- teljes kártyaképesség-futtatás;
- Aeternal damage/heal modell;
- teljes AI.

### Kiemelt szabály

Aeternal és Pecsét HP-modell nem térhet vissza.

### Codexnek adható?

Csak részletes előterv után.

Nem szabad homályosan úgy kiadni, hogy „implementáld az ability rendszert”.

---

## 12. Prototype 8 – Minimal GDScript rules service

### Cél

Kideríteni, hogy GDScriptben kialakítható-e UI-tól elkülönített, minimális rules service réteg.

### Bizonyítandó

- rules service nem Godot UI node-ba kevert logika;
- legal action listát tud adni egy nagyon egyszerű állapotra;
- action requestet tud validálni;
- action response mintát tud adni;
- event log stubot tud generálni;
- diagnostics stubot tud generálni;
- headless smoke testtel ellenőrizhető.

### Nem cél

- teljes szabálymotor;
- teljes AETERNA körszerkezet;
- teljes combat;
- ability execution;
- AI;
- PvP.

### Javasolt első minta

- egy játékos aktív;
- egy egyszerű kézben lévő Entitás;
- play_entity legal action;
- end_turn action;
- rejected action rossz phase vagy wrong player esetén.

### Codexnek adható?

Csak akkor, ha előtte elkészül a részletes minimál scenario és contract input/output.

---

## 13. Prototype 9 – Python / GDScript comparison scenario

### Cél

Ha Python és GDScript oldalon is van minimális action execution, ugyanazt a scenario-t futtassuk le mindkét oldalon, és hasonlítsuk össze az outputot.

### Bizonyítandó

- ugyanaz az input package használható;
- ugyanaz az action request használható;
- event log összevethető;
- snapshot változás összevethető;
- diagnostics összevethető;
- eltérések reportolhatók.

### Nem cél

- teljes engine összehasonlítás;
- balanszteszt;
- teljes AI-vs-AI.

### Mikor aktuális?

Csak azután, hogy:

- van minimális GDScript rules service;
- van Python oldali referencia vagy executor;
- van közös contract input;
- van összevethető event log.

### Codexnek adható?

Később igen, de most még nem ez a következő lépés.

---

## 14. Prototype 10 – Full runtime package preparation audit

### Cél

Előkészíteni, hogy a sample package után később teljes AETERNA runtime package is épülhessen.

### Vizsgálandó

- teljes kártyaadatbázis runtime mezői;
- LOOKUPS állapot;
- structured mezők;
- aliases;
- engine support státusz;
- decklisták;
- generated outputok;
- unknown enum warningok;
- dangerous legacy value-k;
- Aeternal/Pecsét HP-modell nyomai.

### Nem cél

- teljes kártyaaudit;
- minden kártya javítása;
- balanszteszt;
- release package.

### Eredmény

- audit report;
- blocking kategóriák;
- warning kategóriák;
- előkészítő javítási sorrend;
- full package build readiness döntés.

### Codexnek adható?

Részben.

A technikai listázás Codexnek adható, de a szabályi értékelés emberi döntést igényel.

---

## 15. Prototípusok ajánlott sorrendje

Ajánlott sorrend:

1. Fejlesztői build pipeline rendezése.
2. Runtime package + sample contracts integration.
3. Missing card reference diagnostics.
4. Contract consistency smoke test erősítése.
5. Unified debug dashboard.
6. Action response smoke / action request extension.
7. Ability registry support viewer.
8. Simple effect module prototype.
9. Minimal GDScript rules service.
10. Python / GDScript comparison scenario.
11. Full runtime package preparation audit.

Indok:

Előbb a meglévő adat- és build-láncot kell tisztázni.

A pipeline rendezése nem rules engine fejlesztés, hanem előkészítő technikai tisztítás.

Ez segít abban, hogy:

- az exporter ne külön aktív programként éljen tovább;
- ne legyen szükség több kézzel karbantartott input/source másolatra;
- a Python oldali build output és a Godot oldali consumption copy szerepe elkülönüljön;
- a Godot sample package ne legyen kézzel szerkesztett adatforrás;
- később egyetlen fejlesztői buildfolyamat frissíthesse a runtime package-et.

Csak ezután érdemes a runtime package + sample contracts integrációt, a missing reference diagnosticsot, a dashboardot és az action response kört tovább erősíteni.

---

## 16. Codex-kompatibilis feladattípusok

Codexnek jól adható feladatok:

- konkrét loader módosítás;
- konkrét smoke test;
- konkrét debug view;
- card reference resolver;
- missing reference diagnostics;
- dashboard mező hozzáadás;
- sample JSON bővítés;
- Python unit test;
- GDScript smoke test;
- manifest ellenőrzés;
- konkrét schema field kezelés.

Codexnek nem adható homályosan:

- „építsd meg a rules engine-t”;
- „refaktoráld az egész projektet”;
- „rakd rendbe a dokumentációt”;
- „döntsd el, Python vagy GDScript legyen”;
- „töröld a felesleges fájlokat”;
- „mozgasd át a mappákat”;
- „javítsd a kártyákat”;
- „balanszold a játékot”.

---

## 17. Codex prompt alapelvek

Codex prompt legyen:

- rövid;
- konkrét;
- célzott;
- fájlokra hivatkozó;
- tiltásokat tartalmazó;
- elvárt teszteket tartalmazó;
- nem szabályi döntést kérő;
- nem projektirányító;
- nem dokumentációs fődöntést meghozó.

Ajánlott prompt szerkezet:

- Feladat
- Cél
- Érintett fájlok
- Ne módosítsd
- Elvárt működés
- Elvárt smoke test / unit test
- Output / riport
- Ne commitolj

---

## 18. Prototípus sikerességi feltételei

Egy prototípus akkor sikeres, ha:

- a célját bizonyítja;
- a meglévő smoke testeket nem töri el;
- új smoke vagy unit test tartozik hozzá;
- ismert korlátokat rögzít;
- diagnostics vagy report jelzi a hibákat;
- nem keveri össze a debug nézetet a rules engine-nel;
- nem hoz be rejtett szabálylogikát a UI-ba;
- nem zár le nyitott döntést emberi jóváhagyás nélkül.

---

## 19. Prototípus eredményének dokumentálása

Minden komolyabb sikeres prototípus után frissítendő:

- CHECKPOINTS.md
- szükség esetén PROTOTYPE_PLANS.md
- ha contract változott, CONTRACT_SPECIFICATION.md
- ha runtime package változott, RUNTIME_PACKAGE_SPECIFICATION.md
- ha ability support változott, ABILITY_MODULE_SYSTEM.md
- ha döntési kaput érint, TECHNOLOGY_DECISIONS.md vagy DECISION_MAP.md
- ha nyitott kérdésre választ adott, OPEN_QUESTIONS.md

Nem kell minden apró módosításból új dokumentumot készíteni.

---

## 20. Következő ajánlott konkrét fejlesztési lépés

A jelenlegi projektállapot alapján a legjobb következő technikai lépés:

Fejlesztői build pipeline rendezése

Konkrét cél:

- az XLSX exportáló funkció átkerüljön az `Aeterna game engine/python/` tooling rétegébe;
- az exporter explicit source és output útvonalakat tudjon kezelni;
- ne legyen kötelező újabb állandó XLSX input másolatot létrehozni az engine alatt;
- a régi `XLSX export/` mappa ne legyen az aktív hosszú távú programhely;
- a Python oldali `sample_runtime_package` státusza `GENERATED_TEST_FIXTURE` legyen;
- a Godot oldali `sample_runtime_package` státusza `GODOT_CONSUMPTION_COPY` legyen;
- a Godot oldali package frissítését később a Python build pipeline végezze;
- a meglévő Python és Godot smoke testek maradjanak zöldek.

Ez még nem rules engine.

Ez még nem action-végrehajtás.

Ez még nem ability execution.

Ez még nem publikus release pipeline.

Ez jó alap a következő prototípusokhoz, mert:

- csökkenti a kézi lépések számát;
- megszünteti vagy előkészíti a duplikált source/import mappák megszüntetését;
- tisztázza, melyik package generált output és melyik Godot consumption copy;
- előkészíti a runtime package + sample contracts integrációt;
- később lehetővé teszi az egylépéses fejlesztői rebuildet;
- később cache / source_fingerprint rendszerrel bővíthető.

A pipeline rendezése után a következő ajánlott prototípus:

Runtime package + sample contracts integration

Ennek célja:

- snapshot / legal actions / event log card_id hivatkozásai a runtime package card registryből oldódjanak fel;
- debug nézetekben megjelenjen a card name, card type, realm és clan;
- missing card reference diagnostics keletkezzen;
- minden korábbi smoke test zöld maradjon;
- új integration smoke test készüljön.

---

## 21. Nem cél most

Most nem cél:

- teljes rules engine;
- teljes ability execution;
- teljes AI-vs-AI;
- balanszteszt;
- PvP;
- végleges UI;
- teljes kártyaadatbázis futtatása;
- teljes GDScript runtime döntés;
- Python backend végleges eldöntése;
- régi Python motor beolvasztása;
- dokumentumok vagy mappák tömeges mozgatása;
- régi DOCX-ek törlése.

---

## 22. Nyitott kérdések

A prototípusokkal kapcsolatos nyitott kérdések helye:

- OPEN_QUESTIONS.md

Kiemelt témák:

- GDScript rules service alkalmassága;
- Python hosszú távú szerepe;
- hibrid modell fenntarthatósága;
- runtime package kötelező input szerepe;
- action request smoke határa;
- ability execution első moduljai;
- comparison scenario szükségessége;
- AI-vs-AI technológiai helye;
- full runtime package előkészítése.

---

## 23. Záró állapot

A prototípusréteg jelenlegi állapota:

- A v0.1 és v0.2 technikai alapok sikeresek.
- A runtime package és sample contracts adatút működik.
- A debug nézetek működnek.
- A következő biztonságos lépés a fejlesztői build pipeline rendezése.
- A pipeline rendezése után következhet a runtime package + sample contracts integráció erősítése.
- A prototípusok célja döntési bizonyíték gyűjtése.
- Codex használható célzott technikai feladatokra, de nem projektirányításra vagy szabályi döntésekre.