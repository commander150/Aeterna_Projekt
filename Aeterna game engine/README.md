# AETERNA game engine

Az **AETERNA game engine** az AETERNA kártyajáték új, contract-first digitális programegysége.

A projekt célja nem a régi Python szimulátor közvetlen folytatása és nem is azonnali teljes játékprogram. A jelenlegi cél egy tiszta, fokozatosan bővíthető Python/Godot alap kialakítása, amelyben:

* a Python oldal runtime package-et tud generálni;
* a Godot/GDScript oldal contract-loaderként be tudja tölteni a package-et;
* a két oldal JSON / JSONL alapú contractokon keresztül kommunikál;
* a későbbi snapshot, legal action, action request, event log és diagnostics rétegek fokozatosan építhetők rá;
* a fizikai TCG szabályi logikája továbbra is elsődleges marad.

---

## 1. Projektstátusz

Jelenlegi checkpoint:

```text
v0.1 — Python builder → sample runtime package → Godot loader
```

Ez a checkpoint sikeresen működik.

A jelenlegi v0.1 állapot bizonyítja, hogy:

```text
1. Python képes kontrollált sample runtime package-et generálni.
2. A package többfájlos contract-szerkezete működőképes.
3. Godot képes a package betöltésére.
4. Godot képes a kártya-, pakli-, lookup- és ability-adatok registry-kbe rendezésére.
5. A warning diagnostics nem blokkolja a betöltést.
6. A blocking error logika első szinten kezelhető.
7. A Python builder és a Godot loader külön rétegként együtt tud működni.
```

A jelenlegi v0.1 állapot még nem teljes szabálymotor, nem teljes játékprogram, nem képességfuttatás és nem teljes AETERNA adatbázis.

---

## 2. Javasolt mappaszerkezet

Az új programegység gyökere:

```text
Aeterna game engine\
```

Javasolt belső szerkezet:

```text
Aeterna game engine\
  README.md
  CHECKPOINT_v0.1.md

  python\
    tools\
      runtime_package\
        build_sample_runtime_package.py

    tests\
      test_build_sample_runtime_package.py

  Godot\
    project.godot

    sample_runtime_package\
      manifest.json
      cards.jsonl
      decks.jsonl
      lookups.json
      aliases.json
      ability_registry.json
      engine_support.json
      diagnostics.json
      build_report.md

    scripts\
      contract_loader\
        runtime_package_loader.gd
        json_file_loader.gd
        jsonl_file_loader.gd
        schema_checker.gd
        diagnostics_reader.gd

      registries\
        card_registry.gd
        deck_registry.gd
        lookup_registry.gd
        ability_registry.gd

      debug\
        package_debug_view.gd
        package_loader_smoke_test.gd

    scenes\
      package_loader_test.tscn
```

A Godot által fogyasztott sample runtime package hivatalos helye:

```text
Aeterna game engine\Godot\sample_runtime_package\
```

A Godot loader ennek megfelelően ezt az útvonalat használja:

```text
res://sample_runtime_package
```

---

## 3. Python oldal

A Python oldal jelenlegi feladata:

```text
sample runtime package generálása
alap validáció
unit test futtatása
```

Jelenlegi futtatási mód:

```powershell
cd "E:\Letöltések\Aeterna\Aeterna_Projekt\Aeterna game engine\python"

python tools/runtime_package/build_sample_runtime_package.py
python -m unittest tests.test_build_sample_runtime_package
```

A Python generator jelenleg nem éles exportáló.

Nem csinálja még:

```text
XLSX olvasás
teljes AETERNA adatbázis feldolgozása
szabálymotor futtatása
képességfuttatás
AI tesztfuttatás
production package build
```

Későbbi kényelmi cél:

```text
A Python generator ne csak parancssorból legyen futtatható.
```

Első egyszerű megoldási lehetőség:

```text
run_build_sample_package.bat
run_tests.bat
```

Későbbi lehetőség:

```text
egyszerű Python launcher ablak
```

például két gombbal:

```text
1. Sample package generálása
2. Teszt futtatása
```

---

## 4. Godot oldal

A Godot projekt helye:

```text
Aeterna game engine\Godot\project.godot
```

A Godot program elsődleges használati módja:

```text
Godot editorből történő futtatás
```

Jelenlegi fő scene:

```text
res://scenes/package_loader_test.tscn
```

A scene-alapú loader futtatás sikeres.

Elvárt debug output:

```text
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
```

A headless smoke test fejlesztői / automatizált ellenőrzésre használható, de nem ez az elsődleges felhasználói futtatási mód.

Headless futtatás:

```powershell
godot --headless --path "E:/Letöltések/Aeterna/Aeterna_Projekt/Aeterna game engine/Godot" --script "res://scripts/debug/package_loader_smoke_test.gd"
```

Ha a `godot` nincs PATH-ban, akkor a Godot exe teljes útvonalát kell használni.

---

## 5. Sikeres v0.1 smoke test

Sikeres headless smoke test kimenet:

```text
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
```

A korábbi parse hiba oka GDScript típus-inferencia volt olyan visszatérési értéknél, amelynek típusa nem volt egyértelmű.

Hibás minta:

```gdscript
var deck_errors := loader.deck_registry.validate_deck_card_refs(loader.card_registry)
```

Biztonságosabb forma:

```gdscript
var deck_errors = loader.deck_registry.validate_deck_card_refs(loader.card_registry)
```

vagy később, ha a visszatérési típus rögzített:

```gdscript
var deck_errors: Array = loader.deck_registry.validate_deck_card_refs(loader.card_registry)
```

---

## 6. Mi nem része még a v0.1 állapotnak?

A jelenlegi checkpoint még nem tartalmazza:

```text
teljes szabálymotor
kártyaképességek végrehajtása
teljes AETERNA kártyaadatbázis
AI-vs-AI tesztmotor
AI-vs-játékos mód
játékos-vs-játékos mód
snapshot viewer
legal action UI
action request végrehajtás
event log playback
deckbuilder
booster opening
digitális gyűjtemény
```

Ezek későbbi fejlesztési fázisok.

---

## 7. Régi Python program státusza

A régi Python program jelenleg:

```text
működő referencia
átmeneti előzmény
később archiválandó állapot
```

Nem kell azonnal törölni.

Nem kell automatikusan átemelni az új `Aeterna game engine` alá.

Később archív vagy referencia szerepben megőrizhető:

```text
szabálylogikai előzményként
AI-vs-AI tapasztalatként
adatbetöltési és exportálási tanulságként
tesztelési és diagnosztikai előzményként
```

---

## 8. Következő fejlesztési irány

A v0.1 checkpoint után a következő fejlesztési lépcső:

```text
sample snapshot / legal action / event log contract package v0.1
```

Ez várhatóan három statikus sample fájlt jelent:

```text
sample_snapshot.json
sample_legal_actions.json
sample_events.json
```

A cél nem teljes meccsfuttatás, hanem az, hogy Godot oldalon statikus contract adatokat lehessen betölteni és megjeleníteni.

Ez készíti elő a későbbi:

```text
snapshot viewer
legal action debug panel
event log playback
```

irányt.

---

## 9. Záró alapelv

Az AETERNA game engine jelenlegi v0.1 célja:

```text
a contract-first Python/Godot adatút működőképességének bizonyítása és stabilizálása
```

Nem cél még:

```text
a teljes játékprogram elkészítése
a régi Python engine teljes átemelése
a szabálymotor Godotba portolása
```

A következő munkák során a működő v0.1 állapotot meg kell őrizni, a mappaszerkezetet tisztítani kell, és csak ezután érdemes továbblépni a snapshot / legal action / event log prototípusra.
