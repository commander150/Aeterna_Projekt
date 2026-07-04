# AETERNA Game Engine – Checkpoints

    Ez a fájl az AETERNA Game Engine technikai checkpointjainak időrendi összefoglalója.

    A célja nem a teljes architektúra vagy contract-specifikáció rögzítése, hanem annak követése, hogy egy-egy fejlesztési szakasz végén mi készült el, milyen tesztek futottak sikeresen, milyen korlátok maradtak nyitva, és mi volt a következő biztonságos lépés.

## v0.1 – Python sample runtime package + Godot loader 

### Elkészült

    A v0.1 checkpoint elsődleges célja annak bizonyítása volt, hogy működőképes-e az alábbi minimális contract-first adatút:

    Python sample runtime package generator
        ↓
    sample_runtime_package
        ↓
    Godot/GDScript contract-loader
        ↓
    scene-alapú debug futtatás + headless smoke test

    A checkpoint sikeres lett.

    Elkészült és működött:

    Python sample runtime package generator;
    Python oldali unit test;
    sample_runtime_package generálás;
    többfájlos sample runtime package;
    Godot/GDScript runtime package loader;
    Godot oldali card/deck/lookup/ability registry betöltés;
    scene-alapú package loader debug futtatás;
    headless package loader smoke test;
    explicit logfájlos headless Godot futtatási minta.

    A sample runtime package tartalma:

    manifest.json
    cards.jsonl
    decks.jsonl
    lookups.json
    aliases.json
    ability_registry.json
    engine_support.json
    diagnostics.json
    build_report.md

    A package összefoglalója:

    cards: 5
    decks: 1
    lookup_groups: 2
    ability_modules: 2
    warnings: 1
    blocking_errors: 0
    validation blocking: false

    A Godot által használt package helye:

    Aeterna game engine/Godot/sample_runtime_package/

    A Godot loader útvonala:

    res://sample_runtime_package

### Smoke testek 

    Python unit test:

    python -m unittest tests.test_build_sample_runtime_package

    Sikeres eredmény:

    Ran 1 test in 0.022s

    OK

    Godot scene-alapú loader debug output:

    AETERNA package loader debug
    package_id: aeterna.sample_runtime_package
    package_version: 0.1.0
    schema_version: sample-runtime-package-v1
    cards: 5
    decks: 1
    lookup_groups: 2
    ability_modules: 2
    warnings: 1
    blocking_errors: 0
    ok: true

    Godot headless smoke test output:

    Running AETERNA package loader smoke test...
    package_id: aeterna.sample_runtime_package
    package_version: 0.1.0
    schema_version: sample-runtime-package-v1
    cards: 5
    decks: 1
    lookup_groups: 2
    ability_modules: 2
    warnings: 1
    blocking_errors: 0
    AETERNA package loader smoke test: OK

    A stabil headless futtatáshoz Windows / Godot 4.7 környezetben explicit logfájl használata szükséges lehet:

    --log-file "headless_smoke.log"

### Ismert korlátok 

    A v0.1 checkpoint még nem bizonyítja:

    Godot alkalmasságát teljes szabálymotornak;
    kártyaképességek futtatását;
    teljes AETERNA adatbázis betöltését;
    AI-vs-AI tesztelést;
    AI-vs-játékos módot;
    játékos-vs-játékos módot;
    snapshot viewer működését;
    legal action UI működését;
    event log playback működését;
    régi Python motor kiváltását.

    Ismert technikai tanulságok:

    Godot headless futtatásnál explicit --log-file szükséges lehet;
    a Godot / Windows root certificate store warning nem blokkoló, ha az OK output után jelenik meg;
    GDScriptben a := típus-inferencia kerülendő nem egyértelmű visszatérési típusnál.

    Javított GDScript minta:

    var deck_errors = loader.deck_registry.validate_deck_card_refs(loader.card_registry)

    vagy később explicit típussal:

    var deck_errors: Array = loader.deck_registry.validate_deck_card_refs(loader.card_registry)

### Következő lépés 

    A v0.1 után a következő biztonságos fejlesztési lépés:

    sample snapshot / legal action / event log contract package v0.1

    Tervezett új sample fájlok:

    sample_snapshot.json
    sample_legal_actions.json
    sample_events.json

    Nem cél még:

    teljes meccsfuttatás;
    action-végrehajtás;
    kártyaképesség-futtatás;
    AI;
    végleges UI.

## v0.2 – Sample contracts + debug views 

### Elkészült 

    A v0.2 checkpoint a v0.1 runtime package loaderre épült rá.

    Célja annak bizonyítása volt, hogy a Godot oldal nemcsak a runtime package-et képes betölteni, hanem külön statikus játékállapot-, döntéslista- és eseménylog-contractokat is tud olvasni, ellenőrizni és egyszerű debug nézetekben megjeleníteni.

    Új sample contract mappa:

    Aeterna game engine/Godot/sample_contracts/

    Új sample contract fájlok:

    sample_snapshot.json
    sample_legal_actions.json
    sample_events.json

    A vizsgált új contract-réteg:

    statikus snapshot;
    statikus legal action lista;
    statikus event log.

    A vizsgált új Godot debug nézetek:

    Snapshot viewer;
    Legal action debug panel;
    Event log debug view.

    Elkészült Godot oldali fő elemek:

    Godot/scripts/contract_loader/sample_contracts_loader.gd
    Godot/scripts/debug/sample_contracts_debug_view.gd
    Godot/scripts/debug/sample_contracts_smoke_test.gd
    Godot/scenes/sample_contracts_test.tscn
    Godot/run_sample_contracts_smoke_test.bat

    Snapshot viewer fájlok:

    Godot/scripts/debug/snapshot_viewer.gd
    Godot/scripts/debug/snapshot_viewer_smoke_test.gd
    Godot/scenes/snapshot_viewer_test.tscn
    Godot/run_snapshot_viewer_smoke_test.bat

    Legal action debug panel fájlok:

    Godot/scripts/debug/legal_action_debug_panel.gd
    Godot/scripts/debug/legal_action_debug_panel_smoke_test.gd
    Godot/scenes/legal_action_debug_panel_test.tscn
    Godot/run_legal_action_debug_panel_smoke_test.bat

    Event log debug view fájlok:

    Godot/scripts/debug/event_log_debug_view.gd
    Godot/scripts/debug/event_log_debug_view_smoke_test.gd
    Godot/scenes/event_log_debug_view_test.tscn
    Godot/run_event_log_debug_view_smoke_test.bat

    A sample snapshot főbb adatai:

    schema_version: sample-snapshot-v1
    match_id: sample-match-001
    snapshot_id: sample-snapshot-001
    players: 2

    A sample legal actions főbb adatai:

    schema_version: sample-legal-actions-v1
    match_id: sample-match-001
    generated_for_snapshot_id: sample-snapshot-001
    actions: 3
    enabled actions: 2
    disabled actions: 1

    A sample events főbb adatai:

    schema_version: sample-events-v1
    match_id: sample-match-001
    events: 4
    first_sequence: 1
    last_sequence: 4

### Smoke testek 

    A v0.2 végére az alábbi smoke testek zöldek:

    AETERNA package loader smoke test: OK
    AETERNA sample contracts smoke test: OK
    AETERNA snapshot viewer smoke test: OK
    AETERNA legal action debug panel smoke test: OK
    AETERNA event log debug view smoke test: OK

    Sample contracts scene output:

    AETERNA sample contracts debug
    snapshot_schema: sample-snapshot-v1
    legal_actions_schema: sample-legal-actions-v1
    events_schema: sample-events-v1
    match_id: sample-match-001
    players: 2
    actions: 3
    events: 4
    warnings: 0
    blocking_errors: 0
    ok: true

    Sample contracts headless smoke test:

    Running AETERNA sample contracts smoke test...
    snapshot_schema: sample-snapshot-v1
    legal_actions_schema: sample-legal-actions-v1
    events_schema: sample-events-v1
    actions: 3
    events: 4
    blocking_errors: 0
    AETERNA sample contracts smoke test: OK

    Snapshot viewer smoke test:

    Running AETERNA snapshot viewer smoke test...
    match_id: sample-match-001
    snapshot_id: sample-snapshot-001
    players: 2
    blocking_errors: 0
    AETERNA snapshot viewer smoke test: OK

    Legal action debug panel smoke test:

    Running AETERNA legal action debug panel smoke test...
    actions: 3
    enabled: 2
    disabled: 1
    blocking_errors: 0
    AETERNA legal action debug panel smoke test: OK

    Event log debug view smoke test:

    Running AETERNA event log debug view smoke test...
    events: 4
    first_sequence: 1
    last_sequence: 4
    blocking_errors: 0
    AETERNA event log debug view smoke test: OK

### Ismert korlátok 

    A v0.2 checkpoint még nem bizonyítja:

    valódi játékállapot generálását;
    legal actionök szabályból történő kiszámítását;
    action request feldolgozását;
    action-végrehajtást;
    event log valódi játékmenetből történő előállítását;
    event playback rendszert;
    kártyaképesség-futtatást;
    AI döntéshozatalt;
    snapshot viewer végleges UI működését;
    legal action UI végleges működését;
    event log playback végleges működését;
    teljes szabálymotor működését.

    Fontos elhatárolás:

    A sample contractok statikus minták.
    A legal action lista nem szabálymotor által számolt eredmény.
    Az event log nem valódi szabálymotor-futtatásból származik.
    A debug nézetek nem végleges játék UI-elemek.

    A headless Godot futások végén továbbra is megjelenhet:

    ERROR: Failed to read the root certificate store.

    Ez az OK után nem blokkoló warning.

### Következő lépés 

    A v0.2 után javasolt következő fejlesztési lépés:

    Runtime package + sample contracts kapcsolat erősítése

    Cél:

    card_id mellett kártyanév megjelenítése;
    kártyatípus megjelenítése;
    Birodalom / Klán megjelenítése;
    source_card_id és target card_ref olvashatóbbá tétele;
    hiányzó kártyahivatkozások első diagnosztikai kezelése.

    Nem cél:

    szabálymotor;
    action-végrehajtás;
    legal action számítás;
    AI;
    végleges UI.

## v0.3 – XLSX exporter migration smoke

### Elkészült

Ez a checkpoint az XLSX exportáló funkció első sikeres migrációját rögzíti az új AETERNA Game Engine Python tooling alá.

A cél nem teljes build pipeline volt, hanem az első biztonságos lépés:

- az exporter funkció áthelyezése az `Aeterna game engine/python/` alá;
- explicit source és output útvonalak támogatása;
- a régi `XLSX export/source` kötelező használatának megszüntetése;
- exporter unit test átvitele;
- valódi XLSX → JSONL smoke teszt hozzáadása;
- non-interaktív smoke runner létrehozása.

Létrejött fájlok:

- `Aeterna game engine/python/tools/xlsx_export/xlsx_export.py`
- `Aeterna game engine/python/tests/test_xlsx_export.py`
- `Aeterna game engine/python/tests/test_xlsx_export_smoke.py`
- `Aeterna game engine/python/run_xlsx_export.bat`
- `Aeterna game engine/python/run_xlsx_export_smoke.bat`

Az exporter új képességei:

- explicit `--source-dir` opció;
- explicit `--output-dir` opció;
- alapértelmezett engine Python oldali export output;
- régi exportprofilok megtartása;
- új modulhelyről importálható működés;
- XLSX inputból kontrollált JSONL output előállítása.

A smoke teszt programozottan létrehoz egy minimális temporary XLSX fixture-t, majd a `lookups_runtime` profillal exportál.

A smoke teszt ellenőrzi:

- az exporter importálható az új helyről;
- explicit source directory használható;
- explicit output directory használható;
- a `lookups_runtime` profil lefut;
- létrejön a `LOOKUPS_RUNTIME.jsonl`;
- az output nem üres;
- az output soronként JSON-ként olvasható;
- nem használja a régi `XLSX export/exports` mappát.

### Smoke testek

A tesztek az `Aeterna game engine/python` mappából futottak.

Sikeres parancsok:

- `python -m unittest tests.test_xlsx_export`
- `python -m unittest tests.test_xlsx_export_smoke`
- `python -m unittest tests.test_build_sample_runtime_package`
- `run_xlsx_export_smoke.bat`

Eredmények:

- `tests.test_xlsx_export`: `Ran 18 tests ... OK`
- `tests.test_xlsx_export_smoke`: `Ran 1 test ... OK`
- `tests.test_build_sample_runtime_package`: `Ran 1 test ... OK`
- `run_xlsx_export_smoke.bat`: `Ran 1 test ... OK`

Az exporter help ellenőrzése is sikeres volt:

- `python tools\xlsx_export\xlsx_export.py --help`

A help listázza az új `--source-dir` és `--output-dir` opciókat.

Smoke exporter output:

- `Exportált sorok száma: 1`
- `LOOKUPS_RUNTIME.jsonl`
- `Warningok: 0`

### Érintetlenül hagyott részek

A checkpoint során nem módosult:

- `XLSX export/`
- `Aeterna game engine/Godot/`
- `Aeterna game engine/python/tools/runtime_package/build_sample_runtime_package.py`
- `Aeterna game engine/python/main.py`
- `Aeterna game engine/python/data/loader.py`
- `Aeterna game engine/python/data/decklist_loader.py`

A runtime package builder még nincs összekötve az új exporterrel.

A Godot oldali `sample_runtime_package` továbbra is Godot consumption copy.

A Python oldali `sample_runtime_package` továbbra is generated test fixture.

### Ismert korlátok

Ez a checkpoint még nem bizonyítja:

- teljes fejlesztői build pipeline működését;
- full runtime package buildet;
- cache vagy `source_fingerprint` működését;
- Godot consumption copy automatikus frissítését;
- runtime package builder és exporter összekötését;
- Godotból indítható rebuildet;
- rules engine működését;
- ability executiont;
- AI-vs-AI tesztelést.

Ismert technikai kockázat:

A Codex sandboxban a Python temporary cleanup nem tudta minden esetben azonnal törölni a `xlsx_export_smoke_tmp_*` mappát, ezért a smoke teszt warningot adhat pontos útvonallal.

A végső ellenőrzéskor nem maradt temp könyvtár.

Normál fejlesztői környezetben ezt újra kell figyelni. Ha helyben is megmarad temp könyvtár, a cleanup kezelést tovább kell erősíteni.

### Git státusz a checkpoint idején

Releváns új, untracked fájlok:

- `Aeterna game engine/python/run_xlsx_export.bat`
- `Aeterna game engine/python/run_xlsx_export_smoke.bat`
- `Aeterna game engine/python/tests/test_xlsx_export.py`
- `Aeterna game engine/python/tests/test_xlsx_export_smoke.py`
- `Aeterna game engine/python/tools/xlsx_export/`

Tracked tartalmi diff nem maradt.

A `git diff` csak meglévő sample package fájlokra adott line-ending warningot, tartalmi módosítást nem listázott.

### Státusz

Az XLSX exporter migráció első fázisa sikeres.

Jelenlegi státuszok:

- új engine Python exporter: `KEEP_ACTIVE_SOURCE`
- exporter unit test: `KEEP_ACTIVE_TEST`
- exporter smoke test: `KEEP_ACTIVE_SMOKE_TEST`
- `run_xlsx_export.bat`: `KEEP_ACTIVE_RUNNER`
- `run_xlsx_export_smoke.bat`: `KEEP_ACTIVE_RUNNER`
- régi `XLSX export/`: `OBSOLETE_AFTER_MIGRATION_CANDIDATE`
- régi `XLSX export/source`: `PIPELINE_INPUT_COPY`
- régi `XLSX export/exports`: `GENERATED_OUTPUT`

A régi `XLSX export/` mappa még nem törlendő.

### Következő lépés

A következő biztonságos lépés nem a rules engine és nem a runtime package builder bekötése.

Javasolt következő lépés:

- a checkpoint dokumentálása;
- az új exporter fájlok áttekintése;
- szükség esetén a README / PROTOTYPE_PLANS rövid státuszfrissítése;
- csak ezután döntés arról, mikor kössük össze az exportert a runtime package build folyamattal.

A runtime package builderrel való összekötés külön, későbbi prototípus legyen.

## v0.4 – Runtime package publish pipeline és LOOKUPS source split

### Elkészült

A v0.4 checkpoint célja az volt, hogy az XLSX exporter migráció után a runtime package build és Godot publish irány is biztonságosabb, dokumentáltabb adatútra kerüljön.

A checkpoint során elkészült:

* elsődleges runtime package publish runner kijelölése;
* `publish_runtime_package_to_godot.bat` elsődleges fejlesztői pipeline runnerként kezelése;
* kétlépcsős TEMP candidate pipeline megtartása:

  * runtime package candidate build;
  * validáció;
  * csak sikeres validáció után Godot `runtime_package/` frissítés;
* a régi `XLSX export/source` aktív pipeline input szerepének megszüntetése;
* `run_xlsx_export.bat` debug / raw export runner szerepének pontosítása;
* `LOOKUPS.xlsx` runtime lookup reader létrehozása;
* `LOOKUPS.xlsx` bekötése runtime lookup forrásként;
* `RUNTIME_CORE` és `RUNTIME_ABILITY` sheetek használata runtime lookup inputként;
* `RUNTIME_LEGACY_ALIAS` külön legacy alias / normalizációs reader előkészítése;
* `aliases.json` sample / placeholder státuszának tisztázása;
* a két aktív XLSX-forrás szerepének dokumentálása.

Jelenlegi elfogadott source split:

* kártyaadatok és decklisták:

  * `Aeterna dokumentációk/AETERNA – KÁRTYAÁLLOMÁNY MUNKAFORRÁS 1.9v.xlsx`
  * illetve az aktuális fájlnév szerint: `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`
* runtime lookupok:

  * `Aeterna dokumentációk/LOOKUPS.xlsx`
  * sheetek: `RUNTIME_CORE`, `RUNTIME_ABILITY`
* legacy alias / normalizációs forrásjelölt:

  * `Aeterna dokumentációk/LOOKUPS.xlsx`
  * sheet: `RUNTIME_LEGACY_ALIAS`

Fontos döntések:

* A Godot továbbra sem olvas közvetlenül XLSX-et.
* A Godot a validált runtime package-et fogyasztja.
* A kártyák és decklisták továbbra is az 1.9v kártyaadatbázis workbookból jönnek.
* A runtime lookupok már a külön `LOOKUPS.xlsx` fájlból jönnek.
* A `RUNTIME_ABILITY` jelenleg controlled vocabulary / runtime lookup input, nem executable `ability_registry.json` forrás.
* A `RUNTIME_LEGACY_ALIAS` még nincs runtime package outputba kötve.
* Az `aliases.json` jelenleg sample / placeholder runtime package fájl, nem canonical normalizációs forrás.

### Létrejött vagy érintett fő elemek

Új vagy frissített Python tooling elemek:

* `tools/runtime_package/lookups_xlsx_reader.py`
* `tools/runtime_package/runtime_legacy_aliases_reader.py`
* `tools/runtime_package/publish_runtime_package_to_godot.py`
* `tools/runtime_package/smoke_real_export_runtime_package.py`
* `publish_runtime_package_to_godot.bat`
* `run_xlsx_export.bat`

Új vagy frissített tesztek:

* `tests.test_lookups_xlsx_reader`
* `tests.test_runtime_legacy_aliases_reader`
* `tests.test_runtime_lookups_builder_adapter`
* `tests.test_smoke_real_export_runtime_package`
* `tests.test_publish_runtime_package_to_godot`
* `tests.test_xlsx_export_smoke`
* `tests.test_build_sample_runtime_package`
* `tests.test_runtime_cards_builder_adapter`

Frissített dokumentációs területek:

* `README.md`
* `Aeterna game engine/README.md`
* `docs/RUNTIME_PACKAGE_SPECIFICATION.md`
* `docs/OPEN_QUESTIONS.md`

### Sikeres tesztek

A checkpoint alatt sikeresen futott tesztek és ellenőrzések:

* `python -m unittest tests.test_xlsx_export_smoke`
* `python -m unittest tests.test_publish_runtime_package_to_godot`
* `python -m unittest tests.test_build_sample_runtime_package`
* `python -m unittest tests.test_runtime_cards_builder_adapter`
* `python -m unittest tests.test_runtime_lookups_builder_adapter`
* `python -m unittest tests.test_lookups_xlsx_reader`
* `python -m unittest tests.test_runtime_legacy_aliases_reader`
* `python -m unittest tests.test_smoke_real_export_runtime_package`
* `publish_runtime_package_to_godot.bat --dry-run`

A sikeres dry-run főbb eredményei:

* cards: 814
* runtime lookup source: `LOOKUPS.xlsx:RUNTIME_CORE+RUNTIME_ABILITY`
* validation blocking: false
* diagnostic_count: 0
* deck_reference_errors: 0
* unknown_realm_errors: 0
* unknown_card_type_errors: 0
* dry_run: true
* published: false

### Ismert korlátok

Ez a checkpoint még nem bizonyítja:

* teljes rules engine működését;
* ability execution működését;
* `ability_registry.json` végleges előállítását;
* `aliases.json` végleges runtime contract szerepét;
* `RUNTIME_LEGACY_ALIAS` runtime package outputba kötését;
* `normalization_aliases.json` vagy más végleges alias output séma létét;
* Godot oldali alias-normalizációt;
* cache vagy source fingerprint működését;
* végleges build output / package registry struktúrát;
* TEMP candidate pipeline végleges architektúraként való elfogadását.

Fontos nyitott döntések:

* Maradjon-e a TEMP candidate pipeline hosszú távon?
* Legyen-e külön `build/` vagy `generated/` runtime package output mappa?
* Legyen-e verziózott package registry / release mappa?
* Mi legyen a valódi legacy normalizációs output neve:

  * `normalization_aliases.json`
  * `legacy_aliases.json`
  * új sémájú `aliases.json`
  * vagy diagnostics input?
* Mikor javíthat automatikusan a pipeline legacy alias alapján?
* Mikor kell emberi audit?
* Mikor legyen blocking error?

### Godot consumption copy frissítése

A v0.4 checkpoint későbbi részlépéseként a validált publish pipeline ténylegesen frissítette a Godot által fogyasztott runtime package mappát.

Publikált célmappa:

* `Aeterna game engine/Godot/runtime_package/`

A publish eredménye:

* `validation_blocking: false`
* `diagnostic_count: 0`
* `deck_reference_errors: 0`
* `unknown_realm_errors: 0`
* `unknown_card_type_errors: 0`
* `published: true`

A Godot consumption copy most már tartalmazza:

* `normalization_aliases.json`

A manifest is tartalmazza:

* `normalization_aliases.json`

A `normalization_aliases.json` aktuális összefoglalója:

* összes rekord: 1011
* `requires_audit`: 108
* `normalization_allowed`: 903

Godot smoke eredmény:

* Package loader smoke: OK
* debug outputban megjelent: `normalization_aliases: 1011`

Fontos elhatárolás:

* a Godot továbbra sem végez alias-normalizációt;
* a `normalization_aliases.json` jelenleg count-only módon látható Godot oldalon;
* az `aliases.json` továbbra is sample / placeholder státuszú fájl;
* a tényleges alias-normalizáció későbbi külön döntési és implementációs lépés marad.

### Státusz

A v0.4 checkpoint sikeres.

Jelenlegi státuszok:

* `publish_runtime_package_to_godot.bat`: `KEEP_ACTIVE_PRIMARY_PIPELINE_RUNNER`
* `run_xlsx_export.bat`: `KEEP_ACTIVE_RUNNER_MANUAL_RAW_EXPORT`
* `LOOKUPS.xlsx / RUNTIME_CORE`: `KEEP_ACTIVE_RUNTIME_LOOKUP_SOURCE`
* `LOOKUPS.xlsx / RUNTIME_ABILITY`: `KEEP_ACTIVE_RUNTIME_LOOKUP_SOURCE`
* `LOOKUPS.xlsx / RUNTIME_LEGACY_ALIAS`: `PREPARED_NORMALIZATION_SOURCE`
* `aliases.json`: `SAMPLE_PLACEHOLDER_RUNTIME_FILE`
* Godot `runtime_package/`: `GODOT_CONSUMPTION_COPY`
* TEMP candidate pipeline: `ACCEPTED_TRANSITIONAL_STAGING`

### Következő lépés

A következő biztonságos lépés nem a rules engine és nem az ability execution.

Javasolt következő lépés:

* döntés a legacy alias / normalizációs runtime output nevéről és sémájáról;
* előzetes ajánlott irány: `normalization_aliases.json`;
* csak ezután érdemes a `runtime_legacy_aliases_reader.py` kimenetét runtime package outputba kötni.

Nem cél a következő lépésben:

* teljes szabálymotor;
* Godot alias-normalizáció;
* ability execution;
* AI-vs-AI teszt;
* publikus release pipeline;
* TEMP candidate végleges architektúrává nyilvánítása.
