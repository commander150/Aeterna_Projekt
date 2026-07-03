# Aeterna – Projekt Térkép és Fájlstátusz v1.2

Ez a dokumentum az Aeterna projekt jelenlegi, gyakorlati feltérképezését szolgálja.

A célja:
- a projekt fő elemeinek azonosítása
- a fájlok és mappák jelenlegi szerepének rögzítése
- az aktív runtime, a dokumentációs réteg, a tesztréteg, az audit/report réteg és a lehetséges cleanup-jelöltek elkülönítése
- egy olyan közös referencia létrehozása, amely alapján később biztonságosan lehet cleanupot, refaktort vagy részleges újraszervezést végezni

Ez a dokumentum **nem törlési lista**, és **nem refaktor-parancs**.  
Elsődleges célja a pontosabb átláthatóság.

---

## Frissítési megjegyzés – 2026-06

Ez a dokumentum eredetileg a régi Python-alapú AETERNA szimulációs motor és a köré épült fájlrétegek feltérképezésére készült.

A dokumentum továbbra is hasznos projekt-térkép és fájlstátusz referencia, de az AETERNA digitális programegység közben új contract-first irányt kapott az `Aeterna game engine/` mappában.

Ezért a dokumentum korábbi, régi Python motorra vonatkozó részei nem törlendők, hanem pontosított státusszal kezelendők.

Jelenlegi értelmezés:

- a régi Python motor feltárása továbbra is hasznos referencia;
- az új `Aeterna game engine/python/` ág az aktív technikai tooling és runtime package build irány;
- az új `Aeterna game engine/Godot/` ág runtime package és sample contract fogyasztó;
- a régi Python motor maradványai `OLD_ENGINE_REVIEW` státuszban maradnak;
- a dokumentum új szakaszokkal bővíthető, de a régi részeket nem szabad csendben átírni vagy törlési listává alakítani.

Ez a dokumentum továbbra sem törlési lista és nem refaktor-parancs.

## 1. Állapotkép

Az AETERNA projekt jelenlegi állapota hibrid.

A dokumentum eredeti állapotképe a régi Python-alapú, szimuláció-orientált AETERNA motorra vonatkozott. Ennek fő belépési pontja a `main.py`, amely a régi motor adatútján keresztül XLSX-alapú kártyaadatokból dolgozik, majd konfiguráció alapján meccseket futtat.

Ez a régi motor továbbra is értékes referencia, mert:

- működő szimulációs és AI-vs-AI tesztalapot ad;
- sok kártya- és effectlogikát már futtatható formában tartalmaz;
- fontos runtime, audit, diagnostics és report tapasztalatokat hordoz;
- segít megérteni, hogy mely megoldások menthetők át később.

Ugyanakkor a projekt új digitális iránya már nem azonos ezzel a régi motorral.

Az új irány az `Aeterna game engine/` mappában futó contract-first fejlesztés:

- Python oldalon runtime package build, exportvalidáció, tooling, tesztek és későbbi AI/batch feldolgozás;
- Godot oldalon runtime package loader, registry-k, sample contractok, debug nézetek és smoke testek;
- hosszú távon a runtime package legyen a programbiztos adatközvetítő réteg;
- Godot ne közvetlenül XLSX-ből dolgozzon;
- a régi Python motor maradványai egyelőre `OLD_ENGINE_REVIEW` státuszban maradnak.

A projektet továbbra sem nulláról újraépítendő rendszerként kezeljük.

A jelenlegi stratégia:

1. meglévő értékek feltérképezése;
2. régi és új adatút szétválasztása;
3. aktív, generált, referencia, régi motor és archív jelölt státuszok tisztázása;
4. dokumentációs és mappaszintű döntések rögzítése;
5. csak ezután célzott fejlesztés vagy refaktor.

Ez a dokumentum ezért egyszerre tartalmaz:

- régi Python motorra vonatkozó fájlstátuszokat;
- új technikai adatpipeline döntéseket;
- dokumentációs rendezési megjegyzéseket;
- későbbi cleanup / archive / review jelölteket.

---

## 2. Régi Python szimulációs motor hivatalos futási útja

Ez a szakasz a régi Python-alapú szimulációs motor hivatalos futási útját rögzíti.

Nem az új `Aeterna game engine/` contract-first architektúra teljes futási útja.

A régi Python motor entrypointja:

- `main.py`

Aktív futási lánc a régi motorban:

1. `main.py`
2. `simulation/config.py`
3. `engine/logging_utils.py`
4. `simulation/runner.py`
5. `engine/effect_diagnostics_v2.py` explicit `install_effect_diagnostics()` hívással
6. `data/loader.py`
7. `engine/game.py`

A meccsfuttatás közben a hivatalos core modulok közül jellemzően ezek kapcsolódnak be:

- `engine/player.py`
- `engine/card.py`
- `engine/actions.py`
- `engine/board_utils.py`
- `engine/triggers.py`
- `engine/keyword_engine.py`
- `engine/effects.py`
- `engine/structured_effects.py`
- `engine/targeting.py`
- `cards/resolver.py`
- `cards/priority_handlers.py`
- `stats/analyzer.py`
- `utils/logger.py`
- `utils/text.py`

Státusz:

- régi Python szimulációs motor: `OLD_ENGINE_REVIEW`
- régi hivatalos futási út: `KEEP_ACTIVE_REFERENCE`
- új contract-first engine által nem automatikusan kiváltott, de hosszú távon összevetendő referencia

Forrás:

- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

Megjegyzés:

A régi futási út továbbra is hasznos, mert megmutatja, milyen működő Python megoldások léteznek már. Ugyanakkor nem szabad automatikusan az új Godot / runtime package / contract-first célarchitektúra végleges futási útjának tekinteni.

---

## 3. Főkönyvtár – jelenlegi feltérképezés

### 3.1 Gyökérszintű fájlok

#### `.editorconfig`
- státusz: még nem feltérképezett
- szerep: valószínűleg szerkesztői formázási szabályok
- runtime szerep: nincs
- megjegyzés: később ellenőrizendő

#### `.gitattributes`
- státusz: aktív repository meta
- szerep: szövegfájlok LF normalizálása
- runtime szerep: nincs
- haszon: verziókezelési konzisztencia
- megjegyzés: maradjon

#### `.gitignore`
- státusz: aktív repository meta
- szerep: ideiglenes Python fájlok, virtuális környezetek és logok kizárása verziókezelésből
- runtime szerep: nincs
- haszon: repository tisztaság
- megjegyzés: maradjon

#### `Aeterna Kártyajáték szabályrendszer.docx`
- státusz: aktív referencia-dokumentum
- szerep: hivatalos szabályrendszer és világkönyv referencia
- runtime szerep: közvetlenül nincs
- haszon: szabályértelmezési és engine-validációs alap
- megjegyzés: kiemelten fontos dokumentációs forrás

#### `AETERNA_Seed_Convention_v1.docx`
- státusz: `KEEP_ACTIVE_REFERENCE`
- szerep: seed-konvenció és tesztprofil-azonosítási referencia
- runtime szerep: jelenleg nincs közvetlen kódoldali szerepe
- haszon: tesztek reprodukálhatósága, logazonosítás
- megjegyzés: később opcionálisan integrálható a kódba

#### `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

- státusz: `KEEP_ACTIVE_REFERENCE` / `OLD_ENGINE_REVIEW_REFERENCE`
- szerep: a régi Python szimulációs motor hivatalos futási útjának és core / wrapper elhatárolásának rögzítése
- runtime szerep: nincs közvetlen
- haszon:
  - segít megérteni a régi motor tényleges futási láncát;
  - fontos referencia a régi Python motor későbbi archiválási vagy átmentési döntéseihez;
  - összevetési alap lehet az új contract-first architektúrával
- megjegyzés:
  - megőrzendő referencia;
  - nem az új `Aeterna game engine/` teljes célarchitektúrájának végleges leírása;
  - később össze kell vetni az `Aeterna game engine/docs/ARCHITECTURE.md` dokumentummal

#### `cards.xlsx`

- státusz: `OLD_ENGINE_INPUT_REVIEW`
- szerep: a régi Python szimulációs motor kártyaadat-inputja
- runtime szerep: a régi motorban közvetlen, az új contract-first adatútban nem elsődleges
- haszon:
  - fontos történeti és működési referencia;
  - segít megérteni a régi loader és szimulációs motor adatútját;
  - összevetési alap lehet az újabb kártyaadatbázis és exportfolyamat ellenőrzéséhez
- megjegyzés:
  - nem törlendő és nem mozgatandó most;
  - nem tekintendő az új teljes projekt canonical kártyaadatbázisának;
  - szerepét külön össze kell vetni az `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx` fájllal;
  - az új technikai adatpipeline hosszú távon runtime package-et használjon programinputként, nem közvetlen XLSX-et

#### `cards_ertelmezett_v1.xlsx`
- státusz: feltérképezendő
- szerep: valószínűleg korábbi feldolgozott vagy átmeneti verzió
- runtime szerep: valószínűleg nincs a hivatalos futási útban
- megjegyzés: később tisztázni kell, hogy referencia, archív vagy cleanup-jelölt

#### `cards_ertelmezett_v2.xlsx`
- státusz: feltérképezendő
- szerep: valószínűleg korábbi vagy alternatív értelmezett kártyatáblázat
- runtime szerep: valószínűleg nincs a hivatalos futási útban
- megjegyzés: később tisztázni kell, hogy referencia, archív vagy cleanup-jelölt

#### `cleanup_candidates.md`
- státusz: `ARCHIVE_REVIEW`
- szerep: korábbi cleanup-jelölt lista / történeti rendezési nyom
- runtime szerep: nincs
- haszon: takarítási döntések előkészítése
- megjegyzés: nem törlési lista, hanem audit

#### `EFFECT_RETEG_AKTIV_UTVONAL.md`
- státusz: aktív dokumentáció
- szerep: a jelenlegi effect-runtime hivatalos útjának rögzítése
- runtime szerep: nincs közvetlen
- haszon: effect-lánc pontosítása
- megjegyzés: fontos technikai referencia

#### `EFFECT_TRIGGER_HATAROK.md`
- státusz: aktív dokumentáció
- szerep: trigger belépési pontok és diagnostics adapter API határainak rögzítése
- runtime szerep: nincs közvetlen
- haszon: trigger-architektúra tisztázása
- megjegyzés: fontos technikai referencia

#### `ELEMZES_ES_FEJLESZTESI_TERV.md`
- státusz: aktív háttérdokumentáció
- szerep: általános elemzés és fejlesztési terv
- runtime szerep: nincs
- haszon: stratégiai referencia
- megjegyzés: felülvizsgálandó, hogy mennyire aktuális még

#### `kartya_tabla_szabvany_frissett.md`
- státusz: aktív dokumentáció
- szerep: a 22 oszlopos kártyatáblázat szabványának rögzítése
- runtime szerep: közvetlenül nincs, de a loader és engine illesztésének alapja
- haszon: structured rendszer központi referenciafájlja
- megjegyzés: kiemelten fontos

#### `main.py`
- státusz: aktív core runtime
- szerep: fő belépési pont, konfiguráció és futtatásindítás
- runtime szerep: közvetlen
- haszon: hivatalos indítófájl
- megjegyzés: megőrzendő

#### `README.md`
- státusz: aktív dokumentáció
- szerep: rövid projektleírás és futtatási alapinformációk
- runtime szerep: nincs
- haszon: gyors belépési dokumentáció
- megjegyzés: később érdemes bővíteni

---

### 3.2 Gyökérszintű mappák

#### `.git`
- státusz: verziókezelési rendszer
- runtime szerep: nincs
- megjegyzés: nem projektlogikai elem

#### `Archive`
- státusz: jelenleg nem használt / archív jellegű mappa
- runtime szerep: nincs a hivatalos útban
- megjegyzés: később részletesen fel kell térképezni, mi maradjon és mi archivált történeti anyag

#### `cards`
- státusz: aktív runtime mappa
- szerep: név-alapú kártyahandler és resolver réteg
- runtime szerep: közvetlen
- megjegyzés: fontos, de később tisztítandó, mert erősen név-alapú logikát hordoz

#### `data`
- státusz: aktív runtime mappa
- szerep: adatbetöltés, munkafüzet-kezelés
- runtime szerep: közvetlen
- megjegyzés: a structured inputrendszer kulcsrésze

#### `engine`
- státusz: aktív runtime mappa
- szerep: a motor fő magja
- runtime szerep: közvetlen
- megjegyzés: a legfontosabb technikai mappa, részletes feltérképezés szükséges

#### `expansions`
- státusz: jelenleg inkább placeholder / jövőbeli réteg
- runtime szerep: korlátozott vagy jelenleg nem elsődleges
- megjegyzés: később tisztázandó

#### `LOG`
- státusz: futási kimenet
- szerep: generált logok tárolása
- runtime szerep: kimeneti adat
- megjegyzés: nem core kód, de hibakereséshez fontos

#### `simulation`
- státusz: aktív runtime mappa
- szerep: szimulációs konfiguráció és futtatás
- runtime szerep: közvetlen
- megjegyzés: a hivatalos futási lánc része

#### `stats`
- státusz: részben aktív runtime, részben report/audit mappa
- szerep: statisztikák, diagnosztika, compliance és batch reportok
- runtime szerep: vegyes
- megjegyzés: különösen fontos lesz később az aktív és történeti reportok szétválasztása

#### `test_logs_workspace`
- státusz: feltérképezendő
- szerep: valószínűleg ideiglenes logmunka-mappa
- runtime szerep: valószínűleg nincs közvetlen
- megjegyzés: később tisztázni kell

#### `tests`
- státusz: aktív tesztréteg
- szerep: unittest alapú tesztfájlok
- runtime szerep: nem meccsfuttatás, hanem ellenőrzés
- megjegyzés: kulcsfontosságú a stabilizációhoz

#### `utils`
- státusz: aktív támogató mappa
- szerep: segédfüggvények, logger, szöveg-normalizáció
- runtime szerep: közvetlen támogató
- megjegyzés: aktív és hasznos

---

## 4. Jelenlegi kategóriák

### 4.1 Core runtime
Azok az elemek, amelyek a jelenlegi hivatalos meccsfuttatás tényleges részei.

- `main.py`
- `simulation/runner.py`
- `simulation/config.py`
- `data/loader.py`
- `engine/game.py`
- `engine/player.py`
- `engine/card.py`
- `engine/actions.py`
- `engine/board_utils.py`
- `engine/effects.py`
- `engine/structured_effects.py`
- `engine/effect_diagnostics_v2.py`
- `engine/triggers.py`
- `engine/targeting.py`
- `engine/keyword_engine.py`
- `engine/keyword_registry.py`
- `engine/config.py`
- `cards/resolver.py`
- `cards/priority_handlers.py`
- `stats/analyzer.py`
- `utils/logger.py`
- `utils/text.py`

Forrás:
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

---

### 4.2 Wrapper / átmeneti modulok
Azok az elemek, amelyek jelenleg inkább adapterek, re-exportok vagy vékony kompatibilitási rétegek.

- `engine/game_state.py`
- `engine/phases.py`
- `engine/combat.py`
- `engine/keywords_core.py`
- `engine/effects_expansions.py`
- `expansions/` alatti placeholder modulok
- `engine/keywords.py` – kompatibilitási wrapper
- `engine/keyword_rules.py` – kompatibilitási / régi elnevezésű réteg

Forrás:
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`
- `cleanup_candidates.md`

Megjegyzés:
ezek nem automatikus törlési jelöltek. Egy részük átmenetileg hasznos kompatibilitási réteg.

---

### 4.3 Dokumentációs és referenciafájlok
- `Aeterna Kártyajáték szabályrendszer.docx`
- `AETERNA_Seed_Convention_v1.docx`
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`
- `EFFECT_RETEG_AKTIV_UTVONAL.md`
- `EFFECT_TRIGGER_HATAROK.md`
- `ELEMZES_ES_FEJLESZTESI_TERV.md`
- `kartya_tabla_szabvany_frissett.md`
- `README.md`

---

### 4.4 Audit / report / diagnosztikai réteg
- `cleanup_candidates.md`
- `stats/` mappa jelentős része
- compliance audit fájlok
- runtime batch summary fájlok
- standard / keyword / trigger / target / effect tag auditok

Megjegyzés:
ennek a rétegnek a pontos bontása még későbbi feladat.

---

### 4.5 Feltérképezendő / bizonytalan elemek
- `cards_ertelmezett_v1.xlsx`
- `cards_ertelmezett_v2.xlsx`
- `test_logs_workspace/`
- `Archive/` részletes tartalma
- `stats/` teljes belső bontása
- `expansions/` teljes belső tartalma

---

## 5. Jelenlegi fő kockázatok

A jelenlegi dokumentumok és eddigi feltárás alapján:

### 5.1 `engine/effects.py` túl nagy
Ez a fájl több korszak logikáját hordozza, és a projekt egyik fő technikai kockázata.

### 5.2 Név-alapú párhuzamos effect-megoldások
A `cards/resolver.py` + `cards/priority_handlers.py` működőképes, de erősen név-alapú réteg, ezért későbbi tisztításnál figyelni kell a párhuzamos effect-megoldásokra.

### 5.3 Wrapper-rétegek még nem véglegesek
A `game_state / phases / combat` szétválasztás még nem valódi moduláris szeletelés.

### 5.4 A projekt köré sok audit és segédfájl nőtt
Ez nem önmagában baj, de átláthatatlanságot okozhat, ha nincs pontosan elkülönítve:
- mi aktív runtime
- mi csak dokumentáció
- mi csak report
- mi archive-jellegű

---

## 6. Stratégiai döntés

A jelenlegi állapot alapján **nem javasolt a teljes projekt 0-ról újrakezdése**.

A javasolt irány:

1. teljesebb feltérképezés
2. fájlstátuszok pontosítása
3. aktív / wrapper / report / archive rétegek elkülönítése
4. csak ezután célzott cleanup és refaktor
5. részleges újraírás csak ott, ahol ezt a feltérképezés ténylegesen indokolja

---

## 7. Következő bővítési és rendezési feladatok

Ez a dokumentum részben már teljesítette az eredeti bővítési célját: több fő mappa részletesebb feltérképezése elkészült.

A korábbi „következő bővítési feladatok” lista ezért frissítendő.

Jelenlegi értelmezés:

- az `engine/` mappa első részletes feltérképezése elkészült;
- a `cards/` mappa első részletes feltérképezése elkészült;
- a `data/` mappa első részletes feltérképezése elkészült;
- a `simulation/` mappa első részletes feltérképezése elkészült;
- a `utils/` mappa első részletes feltérképezése elkészült;
- a `stats/` mappa első részletes feltérképezése elkészült;
- a dokumentumot most az új `Aeterna game engine/` és a dokumentációs mappa rendezési döntéseivel kell bővíteni.

### 7.1 Már elkészült mappaszintű bontások

Első körben feltérképezett mappák:

- `engine/`
- `cards/`
- `data/`
- `simulation/`
- `utils/`
- `stats/`

Ezek a szakaszok nem végleges architektúradöntések, hanem hasznos fájlstátusz- és szereptérképek.

Nem törlési listák.

### 7.2 Még nyitott vagy frissítendő mappaszintű kérdések

További vizsgálatot igényel:

- régi Python motor maradványainak sorsa;
- `Archive/` részletes tartalma;
- `test_logs_workspace/` szerepe;
- `expansions/` tényleges használata;
- `Aeterna game engine/` új contract-first programágának státusza;
- `XLSX export/` régi exporter mappa státusza;
- `Aeterna dokumentációk/` teljes dokumentumauditja;
- `cards.xlsx` és az újabb kártyaadatbázis munkaforrás viszonya.

### 7.3 Javasolt státuszkategóriák

A dokumentumban a korábbi egyszerű státuszok mellett az újabb projektállapot miatt bővített státuszkészletet érdemes használni.

Javasolt státuszok:

- `KEEP_ACTIVE_SOURCE`
- `KEEP_ACTIVE_REFERENCE`
- `KEEP_DOCS_ACTIVE`
- `KEEP_ACTIVE_TEST`
- `KEEP_ACTIVE_SMOKE_TEST`
- `KEEP_ACTIVE_RUNNER_MANUAL`
- `KEEP_ACTIVE_RUNNER_NONINTERACTIVE`
- `OFFICIAL_SOURCE`
- `CANONICAL_DATA_SOURCE`
- `PIPELINE_INPUT_COPY`
- `GENERATED_OUTPUT`
- `GENERATED_TEST_FIXTURE`
- `GODOT_CONSUMPTION_COPY`
- `HAND_AUTHORED_TEST_FIXTURE`
- `OLD_ENGINE_REVIEW`
- `OLD_ENGINE_INPUT_REVIEW`
- `OLD_ENGINE_REVIEW_REFERENCE`
- `MIGRATED_REPLACED_BY_ENGINE_TOOLING`
- `OBSOLETE_AFTER_MIGRATION_CANDIDATE`
- `DUPLICATE_REVIEW`
- `OBSOLETE_REVIEW`
- `ARCHIVE_CANDIDATE_AFTER_APPROVAL`
- `CACHE_IGNORE`
- `LOG_IGNORE`
- `DO_NOT_TOUCH_YET`
- `INSPECT_FURTHER`

Fontos:

Ezek a státuszok nem automatikus törlési vagy mozgatási utasítások. Minden archiválási, törlési vagy mappamozgatási lépés külön emberi jóváhagyást igényel.

---

## 7.4 `engine/` mappa – részletesebb feltérképezés v1

Az `engine/` mappa a projekt technikai magja.  
Itt található a jelenlegi hivatalos runtime legnagyobb része: játékmenet, zónakezelés, entitás- és játékosállapot, effect-feldolgozás, triggerelés, targeting, kulcsszókezelés és több shared helper.

A jelenlegi architektúra szerint nem minden `engine/` fájl azonos státuszú:
- van, ami tényleges core runtime
- van, ami wrapper / kompatibilitási vagy átmeneti réteg
- van, ami előkészített vagy placeholder jellegű

Forrás:
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

---

### 7.4.1 `engine/` – összkép

#### Core runtime jellegű elemek
A jelenlegi hivatalos futási út szerint az alábbi `engine/` modulok a core motor részei:
- `game.py`
- `player.py`
- `card.py`
- `actions.py`
- `board_utils.py`
- `effects.py`
- `structured_effects.py`
- `effect_diagnostics_v2.py`
- `triggers.py`
- `targeting.py`
- `keyword_engine.py`
- `keyword_registry.py`
- `config.py`

#### Wrapper / átmeneti modulok
A dokumentált wrapper vagy átmeneti modulok:
- `game_state.py`
- `phases.py`
- `combat.py`
- `keywords_core.py`
- `effects_expansions.py`
- `keywords.py`

Megjegyzés:
ezek nem automatikusan törlendő fájlok. Több közülük kompatibilitási, delegáló vagy előkészített modulhely.

---

### 7.4.2 Fájlonkénti bontás

#### `engine/__init__.py`
- státusz: technikai csomagfájl
- szerep: Python package marker
- aktív runtime: technikai értelemben igen, de nincs benne üzleti logika
- haszon: lehetővé teszi az `engine` csomagként való használatát
- megjegyzés: üres, de normális és megtartandó

#### `engine/actions.py`
- státusz: aktív core runtime
- szerep: shared action / helper könyvtár
- aktív runtime: igen
- fő funkciók:
  - célpontgyűjtés és target-key kezelés
  - zónák közti mozgatás
  - horizont / zenit summon helper-ek
  - source placement helper
  - return / deck / source mozgatási helper-ek
  - exhaust / heal / ready / keyword grant / lock jellegű shared műveletek
  - trap consume / restore és több közös runtime helper
- haszon:
  - csökkenti a card-local és ad hoc zónaműveleteket
  - közös canonical helper-réteget ad
  - fontos konszolidációs pont
- megjegyzés:
  - ez a fájl jelenleg az egyik legfontosabb shared runtime réteg
  - későbbi refaktorban külön helper-családokra bontható lehet, de jelenleg kifejezetten hasznos és aktív

#### `engine/board_utils.py`
- státusz: aktív támogató runtime
- szerep: játéktéri objektum- és zónaműveleti segédfüggvények
- aktív runtime: igen
- fő funkciók:
  - entitás / trap / zenit objektum felismerés
  - zónába írások debug-logolása
  - egységes `set_zone_slot(...)`
- haszon:
  - központi zónaírás és zónalogolás
  - segít a debugolhatóságban
- megjegyzés:
  - jelenleg kis, de hasznos utility réteg
  - a zónakezelési debuglogok miatt fontos hibakeresési pont

#### `engine/card.py`
- státusz: aktív core runtime
- szerep: kártya- és csataegység-adatszerkezetek
- aktív runtime: igen
- megjegyzés:
  - a hivatalos core része
  - a teljes rendszer egyik alapmodell-fájlja
  - részletesebb fájltartalom-feltérképezés még szükséges

#### `engine/card_metadata.py`
- státusz: aktív vagy aktívhoz közeli támogató runtime
- szerep: strukturált kártyametadata-kezelés
- aktív runtime: valószínűleg igen
- megjegyzés:
  - a structured mezők és normalizált metadata-réteg miatt fontos lehet
  - részletes ellenőrzés később szükséges

#### `engine/combat.py`
- státusz: wrapper / átmeneti modul
- szerep: delegáló vagy vékony kompatibilitási harcréteg
- aktív runtime: nem elsődleges
- megjegyzés:
  - az architektúra-dokumentum szerint jelenleg kivezethető később
  - nem teljes harci moduláris szelet, csak vékony delegáló réteg

#### `engine/config.py`
- státusz: aktív core runtime
- szerep: engine-konfiguráció és futási mód beállítások
- aktív runtime: igen
- haszon:
  - run mode / expansion flags / module állapotok kezelése
- megjegyzés:
  - hivatalos futási út része
  - fontos stabilizációs pont

#### `engine/effect_diagnostics_v2.py`
- státusz: aktív core runtime közeli diagnosztikai réteg
- szerep: diagnostics adapter bekötése az effect trigger belépési pontokra
- aktív runtime: igen, explicit `install_effect_diagnostics()` hívással
- haszon:
  - structured / custom handler / fallback útvonalak összerendezése
  - runtime diagnosztika
- megjegyzés:
  - nem pusztán reportfájl, hanem ténylegesen bekötött runtime diagnosztikai réteg

#### `engine/effects.py`
- státusz: aktív core runtime
- szerep: fő effectmotor és fallback/common effect réteg
- aktív runtime: igen
- haszon:
  - alapvető effect-primitívek
  - trigger belépési pontok
  - direct / common effect logika
- fő kockázat:
  - a projekt egyik legnagyobb és legösszetettebb fájlja
  - több korszak logikáját hordozza
- megjegyzés:
  - nem törlendő
  - későbbi célzott refaktor egyik fő jelöltje

#### `engine/effects_expansions.py`
- státusz: wrapper / előkészített modul
- szerep: expansion effect-réteg helye
- aktív runtime: nem elsődleges
- megjegyzés:
  - jelenleg inkább előkészített vagy átmeneti hely
  - részletes ellenőrzés szükséges

#### `engine/game.py`
- státusz: aktív core runtime
- szerep: a játékmenet fő vezérlőrétege
- aktív runtime: igen
- fő funkciók:
  - körkezelés
  - kijátszás
  - harc
  - pecséttörés
  - győzelmi logika
  - meccsállapot és fő folyamatvezérlés
- megjegyzés:
  - a jelenlegi motor egyik központi fájlja
  - nem törlendő
  - hosszabb távon részben szeletelhető lehet, de jelenleg ez a hivatalos fő runtime réteg

#### `engine/game_state.py`
- státusz: wrapper / átmeneti modul
- szerep: vékony állapot-adapter
- aktív runtime: nem elsődleges
- megjegyzés:
  - az architektúra-dokumentum szerint wrapper marad átmenetileg
  - nem teljes értékű külön állapotszelet

#### `engine/keyword_engine.py`
- státusz: aktív core runtime
- szerep: hivatalos kulcsszó-runtime réteg
- aktív runtime: igen
- megjegyzés:
  - ez a hivatalos keyword-útvonal
  - megőrzendő, fontos core elem

#### `engine/keyword_registry.py`
- státusz: aktív core runtime
- szerep: kulcsszavak regisztrációs / leképezési rétege
- aktív runtime: igen
- megjegyzés:
  - a keyword rendszer része
  - részletesebb bontás később kell

#### `engine/keywords.py`
- státusz: kompatibilitási wrapper
- szerep: re-export / compatibility layer a keyword engine fölött
- aktív runtime: csak másodlagosan
- megjegyzés:
  - nem elsődleges kulcsszóútvonal
  - átmenetileg maradhat

#### `engine/keywords_core.py`
- státusz: wrapper / kompatibilitási réteg
- szerep: re-export jellegű köztes réteg
- aktív runtime: nem elsődleges
- megjegyzés:
  - az architektúra-dokumentum szerint wrapper marad átmenetileg
  - később kivezethető lehet

#### `engine/logging_utils.py`
- státusz: aktív támogató runtime
- szerep: központi log helper-ek és logindítási segédréteg
- aktív runtime: igen
- haszon:
  - logger inicializálás
  - log header
  - technikai log helper-ek
- megjegyzés:
  - aktívan használt támogató modul
  - a friss logfejlesztések miatt fontos

#### `engine/phases.py`
- státusz: wrapper / átmeneti modul
- szerep: delegáló fázisréteg
- aktív runtime: nem elsődleges
- megjegyzés:
  - az architektúra-dokumentum szerint később kivezethető
  - jelenleg nem valódi külön fázismotor

#### `engine/player.py`
- státusz: aktív core runtime
- szerep: játékosállapot és játékos-műveletek
- aktív runtime: igen
- megjegyzés:
  - pakli, kéz, temető, pecsétek, erőforrás stb. miatt központi elem
  - részletes bontás később szükséges

#### `engine/structured_effects.py`
- státusz: aktív core runtime
- szerep: structured, metadata-driven effect feldolgozás
- aktív runtime: igen
- haszon:
  - canonical mezőkből induló effectpróbálkozások
  - structured routing
- megjegyzés:
  - a modernizált effect-réteg kulcseleme
  - fontos, megőrzendő

#### `engine/targeting.py`
- státusz: aktív core runtime
- szerep: célpont-validáció és targeting állapotkezelés
- aktív runtime: igen
- megjegyzés:
  - untargetable / spell target / validity logika miatt fontos központi elem

#### `engine/triggers.py`
- státusz: aktív core runtime
- szerep: trigger dispatch és eseménykezelési réteg
- aktív runtime: igen
- megjegyzés:
  - a triggeres képességek és runtime események kulcseleme

---

### 7.4.3 `engine/` – elsődleges státuszdöntések v1

#### Egyértelműen megtartandó core
- `actions.py`
- `board_utils.py`
- `card.py`
- `config.py`
- `effect_diagnostics_v2.py`
- `effects.py`
- `game.py`
- `keyword_engine.py`
- `keyword_registry.py`
- `logging_utils.py`
- `player.py`
- `structured_effects.py`
- `targeting.py`
- `triggers.py`

#### Megtartandó, de később refaktor / újraszervezés alatt vizsgálandó
- `effects.py`
- `game.py`
- `actions.py`
- `cards` réteggel együtt a teljes effect-lánc kapcsolata

#### Wrapper / kompatibilitási vagy átmeneti elemek
- `combat.py`
- `game_state.py`
- `keywords.py`
- `keywords_core.py`
- `phases.py`
- `effects_expansions.py`

#### További feltérképezést igényel
- `card_metadata.py`

---

### 7.4.4 `engine/` – fő megfigyelések

1. Az `engine/` mappa nem egységesen “kusza”, hanem világosan elkülöníthető benne:
   - core runtime
   - shared helper-réteg
   - wrapper / kompatibilitási réteg

2. Az `actions.py` már most is fontos konszolidációs központ:
   - célpontkezelés
   - summon
   - source placement
   - return / move / deck / hand helper-ek
   - lock / keyword / trap helper-ek

3. A `board_utils.py` kicsi, de fontos technikai stabilizáló elem, főleg a zónakezelési debug-logok miatt.

4. A legnagyobb technikai kockázat továbbra is az `effects.py`, amely nagy, történeti rétegeket hordozó fájl.

5. A wrapper-modulok jelenléte önmagában nem bizonyítja, hogy a projektet újra kell kezdeni; inkább azt mutatja, hogy a rendszer fokozatos átmeneti refaktor alatt állt vagy áll.

---

### 7.4.5 Következő feladat az `engine/` mappához

A következő körben részletesíteni kell:
- `card.py`
- `player.py`
- `game.py`
- `effects.py`
- `structured_effects.py`
- `targeting.py`
- `triggers.py`
- `config.py`

Ezek adják az `engine/` mappa valódi működési gerincét.

---

### 7.5 `cards/` mappa – részletesebb feltérképezés v1

A `cards/` mappa a jelenlegi motor név-alapú, kártyaspecifikus feloldási rétegét tartalmazza.  
Ez a structured effect-réteg mellett és után működő, konkrét lapnevekre épülő handler-rendszer.

A jelenlegi architektúra szerint a `cards/` mappa aktív része a hivatalos runtime-nak, különösen:
- `cards/resolver.py`
- `cards/priority_handlers.py`

Forrás:
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

---

#### `cards/__init__.py`
- státusz: technikai csomagfájl
- szerep: rövid leírás alapján „lapfeloldási segédmodulok” csomagjelölője
- aktív runtime: technikai értelemben igen, üzleti logika szempontból minimális
- haszon: package marker és rövid modulazonosítás
- megjegyzés: megtartandó, de nem hordoz tényleges runtime logikát

#### `cards/resolver.py`
- státusz: aktív core-közeli runtime
- szerep: központi név-alapú handler-router és trigger-regisztrációs réteg
- aktív runtime: igen
- fő funkciók:
  - lapnév → handler leképezés
  - kategóriák szerinti szétválasztás:
    - `on_play`
    - `trap`
    - `summon_trap`
    - `burst`
  - trap preview / aktiválhatósági előnézet
  - spell redirect / lethal trap útvonalak
  - runtime trigger regisztráció:
    - `on_awakening_phase`
    - `on_destroyed`
    - `on_summon`
    - `on_spell_targeted`
    - `on_damage_taken`
    - `on_turn_end`
- haszon:
  - a jelenlegi név-alapú kártyalogika fő belépési pontja
  - a `priority_handlers.py` felé központi irányító és router
  - összeköti a trap / burst / on_play / triggeres speciális laplogikákat
- fő kockázat:
  - erősen név-alapú
  - nagy mennyiségű konkrét lapnév van kézzel felvezetve
  - párhuzamos effect-megoldásokat hordozhat a structured réteg mellett
- megjegyzés:
  - jelenleg fontos és aktív
  - nem törlendő
  - későbbi refaktorban ez az egyik legfontosabb rendezendő pont

#### `cards/priority_handlers.py`
- státusz: aktív core-közeli runtime
- szerep: konkrét kártyaspecifikus handler-implementációk nagy gyűjtőfájlja
- aktív runtime: igen
- fő funkciók:
  - konkrét lapokhoz tartozó egyedi logikák
  - trap-aktiválás és trap-visszaállítás
  - summon / death / spell target / damage taken / turn end priority logikák
  - card-local speciális viselkedések
  - ActionLibrary-re és EffectEngine-re támaszkodó kombinált végrehajtás
  - runtime státusz- és diagnosztikai rögzítés bizonyos esetekben
- haszon:
  - a structured réteg által még nem teljesen lefedett vagy külön logikát igénylő lapok valódi működését biztosítja
  - sok speciális trap, burst, summon-react és priority viselkedés innen él
  - a jelenlegi motor gyakorlati működésének nagyon fontos része
- fő kockázat:
  - nagyon nagy fájl
  - erősen card-local és név-alapú
  - hosszú távon nehezebben karbantartható
  - több korszak logikája és többféle stílusú megoldás együtt élhet benne
- megjegyzés:
  - jelenleg nem kerülhető meg
  - nem törlendő
  - későbbi célzott refaktor fő jelöltje
  - különösen fontos lesz a structured / shared / card-local felelősségek tisztázása

---

### 7.5.1 `cards/` – összkép

A `cards/` mappa jelenleg nem segéd- vagy mellékréteg, hanem a működő motor része.

A mostani állapot alapján a szerepe:
1. a structured runtime után vagy mellett speciális laplogikák biztosítása
2. trap, burst és egyes triggeres lapok konkrét feloldása
3. olyan card-local viselkedések kezelése, amelyeket a shared effect-primitívek még nem fednek le teljesen

Ez a mappa tehát a jelenlegi rendszerben **nem opcionális**, még akkor sem, ha hosszabb távon részben kiváltható vagy csökkenthető a szerepe.

---

### 7.5.2 `cards/` – elsődleges státuszdöntések v1

#### Egyértelműen megtartandó
- `resolver.py`
- `priority_handlers.py`

#### Megtartandó, de később refaktorálandó
- `resolver.py`
- `priority_handlers.py`

#### Technikai csomagfájl
- `__init__.py`

---

### 7.5.3 `cards/` – fő megfigyelések

1. A `cards/` mappa kicsi, de hatásában nagyon nagy:
   - csak két valódi runtime-fájl van benne
   - de ezek nagy mennyiségű special-case logikát hordoznak

2. A `resolver.py` a név-alapú kártyafeloldás központi routere:
   - a jelenlegi motorban ez a card-local logika fő belépési pontja

3. A `priority_handlers.py` jelenleg egy nagy gyűjtőfájl:
   - konkrét laplogikák
   - trap viselkedések
   - priority hookok
   - eseményvezérelt utóhatások
   - több shared helperre épülő, de mégis card-local végrehajtás

4. A `cards/` réteg létezése önmagában nem bizonyítja, hogy a projektet újra kell kezdeni.
   Inkább azt mutatja, hogy:
   - a shared / structured rendszer még nem fedi le teljesen a speciális lapokat
   - ezért a projekt jelenleg hibrid állapotban van:
     - részben shared / canonical
     - részben név-alapú card-local

5. A későbbi refaktor egyik fő kérdése lesz:
   - miből maradjon tartósan card-local handler
   - mi emelhető át shared helperre
   - mi fedhető le teljesebben structured módon

---

### 7.5.4 Következő feladat a `cards/` mappához

A következő körökben érdemes részletesebben feltárni:
- a `resolver.py` pontos runtime szerepét az effect-láncban
- a `priority_handlers.py` belső logikai csoportjait, például:
  - on_play lapok
  - trap lapok
  - summon trap lapok
  - burst lapok
  - runtime event hookok
- azt, hogy mely részek támaszkodnak már jól a shared `ActionLibrary` / `EffectEngine` helper-ekre
- és mely részek maradtak tisztán card-local speciális megoldások

---

### 7.6 `data/` mappa – részletesebb feltérképezés v1

A `data/` mappa a projekt bemeneti adatkezelési rétegét tartalmazza.  
Jelenleg kicsi, de kulcsszerepű mappa, mert itt történik a `cards.xlsx` munkafüzet beolvasása, normalizálása, validálása és a runtime által használható kártyaobjektumok előállítása.

A jelenlegi hivatalos futási út szerint a `data/loader.py` az aktív motor része.

Forrás:
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

---

#### `data/__init__.py`
- státusz: technikai csomagfájl
- szerep: Python package marker
- aktív runtime: technikai értelemben igen, üzleti logika szempontból nincs
- haszon: lehetővé teszi a `data` csomagként való importálását
- megjegyzés: üres, normális, megtartandó

#### `data/loader.py`
- státusz: aktív core runtime
- szerep: Excel alapú kártyabetöltő és validációs / normalizációs réteg
- aktív runtime: igen
- fő funkciók:
  - `cards.xlsx` betöltése `openpyxl` segítségével
  - oszlopnevek normalizálása és alias-kezelése
  - a 22 oszlopos standard oszlopsorrend kezelése
  - lista- és skalármezők normalizálása
  - enum típusú mezők standard / alias / legacy / unknown kategorizálása
  - soronkénti validáció
  - `Kartya` objektumok előállítása
  - validációs figyelmeztetések logolása
- fontos kezelt structured mezők:
  - `Képesség_Canonical`
  - `Zóna_Felismerve`
  - `Kulcsszavak_Felismerve`
  - `Trigger_Felismerve`
  - `Célpont_Felismerve`
  - `Hatáscímkék`
  - `Időtartam_Felismerve`
  - `Feltétel_Felismerve`
  - `Gépi_Leírás`
  - `Értelmezési_Státusz`
  - `Engine_Megjegyzés`
- haszon:
  - a structured szabvány és a runtime közti elsődleges kapocs
  - egységes bemenetet ad a motor további rétegeinek
  - kiszűri az adatkonzisztencia-problémák jelentős részét
- megjegyzés:
  - a jelenlegi projekt egyik kulcsfájlja
  - nem csak betöltő, hanem részben standardizáló és validáló réteg is
  - a 22 oszlopos rendszerhez való igazítás egyik fő technikai eredménye

---

### 7.6.1 `data/` – összkép

A `data/` mappa jelenleg nagyon koncentrált szerepet tölt be:
1. bemeneti adatfájl elérése
2. munkafüzet beolvasása
3. mezőnormalizálás
4. validáció
5. runtime-kompatibilis kártyaobjektumok előállítása

Ez azt jelenti, hogy a `data/` réteg jelenleg nem szétszórt és nem túlméretezett, hanem éppen ellenkezőleg:
- kicsi
- koncentrált
- és jól meghatározható funkciója van

---

### 7.6.2 `data/` – elsődleges státuszdöntések v1

#### Egyértelműen megtartandó
- `loader.py`

#### Technikai csomagfájl
- `__init__.py`

---

### 7.6.3 `data/` – fő megfigyelések

1. A `data/loader.py` a structured szabvány gyakorlati belépési pontja:
   - nem csak olvas
   - hanem normalizál
   - validál
   - és a runtime számára használható formára alakít

2. A loader már név-alapú header aliasokat, enum normalizálást és validation issue kategorizálást is kezel.
   Ez arra utal, hogy a projekt adatoldalon már jóval rendezettebb, mint amennyire első ránézésre tűnhet.

3. A validációs logika beépítése azért fontos, mert a projekt egyik hosszú távú célja éppen az volt, hogy a kártyák dokumentuma a program számára jobban használható legyen.

4. A `data/` mappa alapján nem az látszik, hogy a projektet újra kell kezdeni, hanem az, hogy az inputrendszer már komolyan szabványosított irányba lett eltolva.

---

### 7.6.4 Kockázatok és későbbi figyelendő pontok

1. A loader jelenleg sok felelősséget hordoz egyszerre:
   - Excel olvasás
   - header alias
   - mezőnormalizálás
   - enum kategorizálás
   - validáció
   - objektum-előállítás

2. Ez jelenleg nem feltétlenül probléma, mert a projekt méretéhez képest még átlátható maradt, de később érdemes lehet elválasztani:
   - workbook reading
   - normalization
   - validation
   - object factory

3. A `loader.py` jelenleg szorosan a `cards.xlsx` és a 22 oszlopos szabvány jelenlegi alakjára épít.
   Ez jó, mert a projekt célja most ez a standard volt, de későbbi bővítéseknél figyelni kell arra, hogy a bemeneti szerződések ne lazuljanak fel újra.

---

### 7.6.5 Következő feladat a `data/` mappához

A következő körökben érdemes külön dokumentálni:
- a `Kartya` objektummá alakítás pontos menetét
- a `card_metadata` és a loader kapcsolatát
- a validation issue kategóriák jelentését
- azt, hogy mely warning típusok tekinthetők:
  - alias-normalizálható zajnak
  - legacy kompatibilitási jelnek
  - valódi adatminőségi problémának

---

### 7.7 `simulation/` mappa – részletesebb feltérképezés v1

A `simulation/` mappa a projekt futtatási és meccssorozat-kezelési rétege.  
Itt dől el, hogy a program milyen konfigurációval indul, milyen birodalmakat használ, hogyan inicializálja az engine-konfigurációt, és hogyan futtat le több egymást követő meccset.

A jelenlegi hivatalos futási út szerint a `simulation/config.py` és a `simulation/runner.py` az aktív runtime részei.

Forrás:
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

---

#### `simulation/__init__.py`
- státusz: technikai csomagfájl
- szerep: Python package marker
- aktív runtime: technikai értelemben igen, üzleti logika szempontból nincs
- haszon: lehetővé teszi a `simulation` csomagként való importálását
- megjegyzés: üres, normális, megtartandó

#### `simulation/config.py`
- státusz: aktív core runtime
- szerep: szimulációs konfigurációs objektum definíciója
- aktív runtime: igen
- fő funkciók:
  - `SimulationConfig` dataclass
  - meccsszám, seed, P1/P2 birodalom, véletlen fallback kezelés
  - későbbi bővítési helyek:
    - `player1_deck`
    - `player2_deck`
    - `scenario`
    - `scripted_opening_hands`
    - `scripted_board_state`
  - engine run mode és expansion beállítások átadása
  - log alapmappa kezelése
  - `to_engine_config()` → engine konfigurációs objektum előállítása
  - `describe()` → emberileg olvasható konfigurációs összegzés
- haszon:
  - tiszta konfigurációs szerződést ad a futtatási rétegnek
  - jól bővíthető jövőbeli teszt- és scenario-rendszerhez
- megjegyzés:
  - kis fájl, de nagyon jó szervezőpont
  - az egyik legtisztább réteg a projektben

#### `simulation/runner.py`
- státusz: aktív core runtime
- szerep: a meccssorozat-futtatás központi vezérlője
- aktív runtime: igen
- fő funkciók:
  - effekt-diagnostics bekapcsolása
  - konfiguráció feloldása
  - engine konfiguráció aktiválása
  - random seed kezelése
  - `cards.xlsx` betöltése a loaderen át
  - elérhető birodalmak meghatározása
  - birodalomválasztás
  - meccsek tömeges futtatása
  - `AeternaSzimulacio` példányok létrehozása
  - meccsenkénti log metric számlálók inicializálása
  - meccsvégi summary és futásvégi summary logolás
  - statisztikai összesítés mentése
- haszon:
  - ez a tényleges szimulációs irányítóközpont
  - itt találkozik a config, a loader, a logger, a stats és a game runtime
  - a jelenlegi AI-vs-AI tesztprogram szempontjából kulcselem
- megjegyzés:
  - a friss logfejlesztések és summaryk nagy része itt jelent meg
  - jelenleg fontos, hasznos és aktív
  - nem törlendő

---

### 7.7.1 `simulation/` – összkép

A `simulation/` mappa jelenleg három jól elkülönülő szerepet tölt be:

1. konfigurációs szerződés (`config.py`)
2. futtatási orchestration (`runner.py`)
3. technikai package marker (`__init__.py`)

Ez a mappa jelen állapotában nem tűnik túlburjánzottnak vagy kuszának.  
Épp ellenkezőleg: a projekt egyik rendezettebb és jól értelmezhető része.

---

### 7.7.2 `simulation/` – elsődleges státuszdöntések v1

#### Egyértelműen megtartandó
- `config.py`
- `runner.py`

#### Technikai csomagfájl
- `__init__.py`

---

### 7.7.3 `simulation/` – fő megfigyelések

1. A `SimulationConfig` jó irányba mutat:
   - nem csak az aktuális AI-vs-AI futásokat támogatja
   - hanem előkészíti a későbbi scenario / scripted / deck-alapú bővítéseket is :contentReference[oaicite:4]{index=4}

2. A `runner.py` jelenleg valóban a futtatási orchestration réteg:
   - nem próbálja a teljes játékszabályt magába húzni
   - inkább összekapcsolja a megfelelő modulokat :contentReference[oaicite:5]{index=5}

3. A `runner.py` most már fontos diagnosztikai és tesztelési értéket is hordoz:
   - seed log
   - match log
   - meccssummary
   - futásvégi summary
   - log metric számlálók :contentReference[oaicite:6]{index=6}

4. A `simulation/` mappa alapján a projekt futtatási oldala nem indokol teljes újrakezdést.  
   Ez a réteg inkább stabilizálható és továbbfejleszthető.

---

### 7.7.4 Kockázatok és későbbi figyelendő pontok

1. A `runner.py` jelenleg többféle szerepet hordoz egyszerre:
   - futtatásindítás
   - birodalomválasztás
   - seed-kezelés
   - log összegzés
   - meccsszintű metric inicializálás

2. Ez most még kezelhető méretű, de később érdemes lehet különválasztani:
   - profile selection
   - run orchestration
   - summary / report generation

3. A `SimulationConfig` már most előre tartalmaz olyan mezőket, amelyek még nem teljesen kiaknázottak:
   - scenario
   - scripted opening hands
   - scripted board state
   - deck-specifikus futtatás

4. Ez nem hiba, inkább jelzés arra, hogy a projekt hosszabb távon túlmutat a jelenlegi egyszerű random AI-vs-AI szimuláción.

---

### 7.7.5 Következő feladat a `simulation/` mappához

A következő körökben érdemes külön dokumentálni:
- a `main.py` és a `SimulationConfig` kapcsolatát
- a seed-konvenció és a tényleges futtatási konfiguráció viszonyát
- a log metric-ek szerepét
- a jövőbeli scenario / scripted tesztprofil támogatás pontos helyét a futtatási láncban

---

### 7.8 `utils/` mappa – részletesebb feltérképezés v1

A `utils/` mappa a projekt általános segédfüggvényeit tartalmazza.  
Jelenleg kicsi, de a gyakorlatban nagyon fontos támogató réteg, mert:
- a teljes runtime logolása támaszkodik rá
- a szöveg-normalizálás és karakterhelyreállítás is innen jön

A jelenlegi projektben a `utils/` nem mellékes kényelmi réteg, hanem több core modul által használt aktív segédréteg.

---

#### `utils/__init__.py`
- státusz: technikai csomagfájl
- szerep: Python package marker
- aktív runtime: technikai értelemben igen, üzleti logika szempontból nincs
- haszon: lehetővé teszi a `utils` csomagként való importálását
- megjegyzés: üres, normális, megtartandó

#### `utils/logger.py`
- státusz: aktív támogató runtime
- szerep: központi logoló osztály és globális logger objektum
- aktív runtime: igen
- fő funkciók:
  - logfájl indítása
  - logfájl elérési út beállítása
  - konzol + fájl logolás
  - timestampelt sorok írása
  - technikai kategóriás logok:
    - `tech(...)`
    - `skip(...)`
    - `summary(...)`
    - `separator(...)`
  - UTF-8 és hibás karakteres kimenet toleráns kezelése
- haszon:
  - a projekt jelenlegi logrétegének alapja
  - meccslogok, summaryk és technikai diagnosztikai sorok mind erre épülnek
- megjegyzés:
  - a friss logfejlesztési körök után ez a fájl fontosabb lett, mint korábban
  - megőrzendő
  - jelenleg jó központi logger-réteg

#### `utils/text.py`
- státusz: aktív támogató runtime
- szerep: szöveg-helyreállítási és normalizációs segédfüggvények
- aktív runtime: igen
- fő funkciók:
  - hibás karakterkódolásból származó mojibake javítása
  - keresési / összehasonlítási célú normalizált szöveg előállítása
  - ékezetmentesített, lowercased lookup stringek gyártása
- haszon:
  - kulcsfontosságú a lapnevek, mezőértékek, aliasok és kulcsszavak stabil összehasonlításához
  - csökkenti a hibás karakterkódolásból eredő problémákat
- megjegyzés:
  - kis méretű, de nagyon fontos utility
  - a loader, resolver és több egyéb modul számára alapvető

---

### 7.8.1 `utils/` – összkép

A `utils/` mappa jelenleg két valódi funkcionális alapelemre épül:

1. központi logolás (`logger.py`)
2. szöveg-normalizálás (`text.py`)

Ez a mappa jelen formájában nem tűnik túl nagyra nőttnek vagy kuszának.  
Inkább tipikus kis utility-réteg, amelyet a projekt több aktív része használ.

---

### 7.8.2 `utils/` – elsődleges státuszdöntések v1

#### Egyértelműen megtartandó
- `logger.py`
- `text.py`

#### Technikai csomagfájl
- `__init__.py`

---

### 7.8.3 `utils/` – fő megfigyelések

1. A `logger.py` jelenleg valódi infrastruktúra-fájl:
   - nem csak print-wrapper
   - hanem a projekt egységes logrétegének alapja :contentReference[oaicite:3]{index=3}

2. A `text.py` a projektben a vártnál fontosabb:
   - a név-alapú és alias-alapú rendszerek miatt a normalizált szöveg-összehasonlítás alapvető
   - a hibás karakterkódolási állapotok miatt a mojibake-javítás is praktikus, nem csak kényelmi funkció :contentReference[oaicite:4]{index=4}

3. A `utils/` mappa alapján sem az látszik, hogy a projektet újra kellene kezdeni.
   Ez a réteg inkább tiszta, stabil és jól használható.

---

### 7.8.4 Kockázatok és későbbi figyelendő pontok

1. A `logger.py` további bővítéseknél figyelni kell arra, hogy:
   - ne váljon túl sok speciális projektlogika hordozójává
   - maradjon inkább általános logger-réteg

2. A `text.py` normalizálási szabályai a név-alapú rendszer miatt érzékenyek lehetnek:
   - ha később változik a szövegkezelés vagy az aliasrendszer, ezt is újra kell nézni

3. Jelenleg azonban egyik fájl sem tűnik refaktor-sürgős vagy problémás pontnak.

---

### 7.8.5 Következő feladat a `utils/` mappához

A következő körökben érdemes külön dokumentálni:
- mely modulok támaszkodnak közvetlenül a `normalize_lookup_text(...)` függvényre
- és hogy a logger mely pontokon működik csak nyers naplózóként, illetve hol kapott már projekt-specifikus technikai logkategóriákat

---

### 7.9 `stats/` mappa – részletesebb feltérképezés v1

A `stats/` mappa jelenleg vegyes szerepű terület:
- van benne aktív runtime-hoz kapcsolódó elem
- vannak audit script-ek
- vannak batch summaryk
- vannak compliance reportok
- vannak történeti vagy egyszeri elemzési fájlok is

Ez az a mappa, amely a legerősebben mutatja, hogy a projekt köré idővel sok diagnosztikai és fejlesztéstámogató réteg nőtt.

A felhasználói megjegyzés alapján ez a mappa az egyik fő oka annak az érzésnek, hogy a projekt túl nagyra nőtt és karbantartást igényel. Ez a megfigyelés a jelenlegi fájllista alapján indokoltnak tűnik.

---

#### `stats/__init__.py`
- státusz: technikai csomagfájl
- szerep: Python package marker
- aktív runtime: technikai értelemben igen, üzleti logika szempontból nincs
- megjegyzés: megtartandó, de önálló funkcionális szerepe nincs

#### `stats/analyzer.py`
- státusz: aktív támogató runtime
- szerep: statisztikai és diagnosztikai gyűjtőréteg
- aktív runtime: igen
- feltételezett szerep:
  - meccsek, körök, pecséttörések, effektek vagy runtime státuszok könyvelése
  - összesített statisztikai kimenetek előállítása
  - a `runner.py` és egyes effect / handler rétegek támogatása
- megjegyzés:
  - a `stats/` mappa jelenlegi állapotában ez az egyetlen egyértelműen aktív runtime-közeli fájl
  - részletes fájltartalom-feltárás később szükséges

---

### 7.9.1 Audit / script jellegű fájlok

#### `cards_xlsx_audit.py`
- státusz: fejlesztői audit script
- szerep: a `cards.xlsx` vagy kapcsolódó táblák auditálása
- aktív runtime: valószínűleg nem
- megjegyzés: diagnosztikai / ellenőrző segédfájl

#### `full_card_analysis.py`
- státusz: fejlesztői elemző script
- szerep: teljes kártyaelemzés vagy táblázati átvilágítás
- aktív runtime: valószínűleg nem
- megjegyzés: fejlesztéstámogató script, nem meccsfuttatási mag

#### `standard_cleanup_audit.py`
- státusz: audit script
- szerep: standard-cleanup átvilágítás
- aktív runtime: nem
- megjegyzés: egyszeri vagy időszakos standardizációs segédfájl

#### `standard_engine_audit.py`
- státusz: audit script
- szerep: szabvány ↔ engine audit előállítása
- aktív runtime: nem
- megjegyzés: fejlesztői ellenőrzéshez hasznos, nem futtatási mag

---

### 7.9.2 Batch summary és compliance report fájlok

#### Canonical runtime batch summaryk
- `canonical_runtime_batch_1_summary.md`
- `canonical_runtime_batch_2_summary.md`
- `canonical_runtime_batch_3_summary.md`
- `canonical_runtime_batch_4_summary.md`
- `canonical_runtime_batch_5_summary.md`
- `canonical_runtime_batch_6_summary.md`
- `canonical_runtime_batch_7_summary.md`

- státusz: történeti fejlesztési reportok
- szerep: az egyes canonical runtime batch-ek eredményeinek rögzítése
- aktív runtime: nem
- haszon:
  - fejlesztéstörténet követése
  - mi lett implementálva / mi maradt deferred dokumentálása
- megjegyzés:
  - fontos történeti anyagok
  - valószínűleg nem a fő `stats/` gyökérszintjén kellene hosszú távon maradniuk
  - később külön archive vagy batch_reports alcsoportba rendezhetők

#### Compliance audit reportok
- `keyword_compliance_audit.md`
- `trigger_compliance_audit.md`
- `effect_tag_compliance_audit.md`
- `target_compliance_audit.md`
- `standard_engine_compliance_audit.md`
- `standard_only_engine_compliance_audit.md`

- státusz: fejlesztői compliance reportok
- szerep: canonical szabványelemek engine támogatottságának felmérése
- aktív runtime: nem
- haszon:
  - szabvány ↔ engine illeszkedés nyomon követése
  - fejlesztési prioritások meghatározása
- megjegyzés:
  - hasznosak, de erősen report-jellegűek
  - később külön `stats/reports/compliance/` jellegű helyre rendezhetők

#### Standard / cleanup / triage reportok
- `canonical_alias_map.md`
- `standard_cleanup_summary.md`
- `standard_integration_summary.md`
- `warning_triage_report.md`
- `top_20_standardization_gaps.md`

- státusz: fejlesztői diagnosztikai reportok
- szerep: aliasok, warning backlogok, cleanup hiányok és integration állapot rögzítése
- aktív runtime: nem
- megjegyzés:
  - hasznosak a fejlesztéshez
  - de nem core runtime részek
  - később report-architektúrában rendezendők

---

### 7.9.3 Témaspecifikus audit / elemzési fájlok

#### Ignis / Hamvaskezű fókuszú fájlok
- `clan_audit_ignis_hamvaskez_by_card_type.md`
- `clan_audit_ignis_hamvaskezu_by_card_type.md`
- `effect_support_audit_ignis_hamvaskezu_simple.csv`
- `keyword_support_audit_ignis_hamvaskezu.csv`
- `keyword_support_audit_ignis_hamvaskezű.csv`
- `keyword_support_validation_ignis_hamvaskezu.md`
- `trap_validation_ignis_hamvaskezu.md`

- státusz: témaspecifikus vagy birodalomspecifikus auditfájlok
- szerep: célzott klán- és képességellenőrzések
- aktív runtime: nem
- megjegyzés:
  - értékes fejlesztési mellékanyagok lehetnek
  - de egyértelműen nem a futó program részei
  - a kétféle írásmód (`hamvaskez`, `hamvaskezu`, `hamvaskezű`) külön figyelmet igényel a későbbi tisztításnál

#### Általános kártyaelemzési fájlok
- `cards_per_card_analysis.md`
- `cards_metadata_enrichment.csv`

- státusz: elemzési / adatgazdagítási mellékfájlok
- szerep: kártyaszintű elemzés és metadata enrichment
- aktív runtime: valószínűleg nem
- megjegyzés:
  - hasznos segédanyag lehet
  - tisztázni kell, hogy jelenleg melyik tekinthető élő fejlesztői referenciának

---

### 7.9.4 `stats/` – összkép

A `stats/` mappa jelenleg nem egységes.

Nagy valószínűséggel négyféle szerep keveredik benne:
1. aktív statisztikai runtime réteg (`analyzer.py`)
2. audit-generáló script-ek
3. egyszeri vagy időszakos compliance / cleanup reportok
4. történeti fejlesztési batch-summaryk

Ez pontosan az a mappa, ahol a későbbi cleanup és karbantartási igény a legerősebben indokolt.

---

### 7.9.5 `stats/` – elsődleges státuszdöntések v1

#### Egyértelműen megtartandó aktív elem
- `analyzer.py`

#### Megtartandó, de report / audit kategóriába szervezendő elemek
- `canonical_alias_map.md`
- `canonical_runtime_batch_1_summary.md`
- `canonical_runtime_batch_2_summary.md`
- `canonical_runtime_batch_3_summary.md`
- `canonical_runtime_batch_4_summary.md`
- `canonical_runtime_batch_5_summary.md`
- `canonical_runtime_batch_6_summary.md`
- `canonical_runtime_batch_7_summary.md`
- `effect_tag_compliance_audit.md`
- `keyword_compliance_audit.md`
- `standard_cleanup_summary.md`
- `standard_engine_compliance_audit.md`
- `standard_integration_summary.md`
- `standard_only_engine_compliance_audit.md`
- `target_compliance_audit.md`
- `top_20_standardization_gaps.md`
- `trigger_compliance_audit.md`
- `warning_triage_report.md`
- `cards_per_card_analysis.md`
- `cards_metadata_enrichment.csv`
- témaspecifikus Ignis / Hamvaskezű auditfájlok

#### Megtartandó, de script / tooling kategóriába rendezendő elemek
- `cards_xlsx_audit.py`
- `full_card_analysis.py`
- `standard_cleanup_audit.py`
- `standard_engine_audit.py`

#### Technikai csomagfájl
- `__init__.py`

---

### 7.9.6 `stats/` – fő megfigyelések

1. A `stats/` mappa jelenlegi állapota valóban erősen támogatja azt az érzést, hogy a projekt köré sok fejlesztési mellékréteg nőtt.

2. Ez azonban nem feltétlenül azt jelenti, hogy a projektet újra kell kezdeni, hanem inkább azt, hogy:
   - a `stats/` mappa túl sokféle célt szolgál egy helyen
   - az aktív runtime elem és a történeti / audit anyagok nincsenek eléggé szétválasztva

3. A fájlnevek alapján a `stats/` elsősorban nem “hibás”, hanem “túlterhelt” mappa:
   - túl sok report és audit egy szinten
   - kevés explicit szerkezeti különválasztás

4. Ez a mappa jó jelölt egy későbbi biztonságos strukturális cleanupra.

---

### 7.9.7 Javasolt későbbi rendezési irány a `stats/` mappához

A jelenlegi lista alapján hosszabb távon érdemes lehet különválasztani legalább ezeket:

#### `stats/runtime/`
- aktív runtime-közeli statisztikai elemek
- pl. `analyzer.py`

#### `stats/scripts/`
- audit-generáló vagy elemző Python scriptek
- pl. `cards_xlsx_audit.py`, `full_card_analysis.py`, `standard_cleanup_audit.py`, `standard_engine_audit.py`

#### `stats/reports/compliance/`
- keyword / trigger / target / effect / standard compliance reportok

#### `stats/reports/batches/`
- canonical runtime batch summaryk

#### `stats/reports/domain_specific/`
- birodalom- vagy klánspecifikus auditok
- pl. Ignis / Hamvaskezű fókuszú reportok

#### `stats/reports/cleanup/`
- triage, alias-map, standardization gaps, warning backlog reportok

Ez jelenleg még csak javasolt szerkezeti irány, nem azonnali végrehajtási terv.

---

### 7.9.8 Következő feladat a `stats/` mappához

A következő körökben érdemes külön feltárni:
- `analyzer.py` pontos szerepét és függőségeit
- mely reportok számítanak még aktív fejlesztői referenciának
- mely reportok tisztán történeti anyagok
- mely script-ek futnak még ténylegesen
- a duplikátumgyanús és vegyes elnevezésű fájlok sorsát

Ez a mappa külön karbantartási / cleanup tervet érdemel.

---

## 7.10 Technikai adatpipeline rendezés – első kör lezárása

Státusz: első körben lezárva.

Ez a szakasz az új AETERNA Game Engine technikai adatpipeline döntéseit rögzíti, és nem írja felül a dokumentum korábbi, régi Python szimulációs motorra vonatkozó státuszait.

Érintett mappák:

- `Aeterna game engine/python/`
- `Aeterna game engine/Godot/`
- `XLSX export/`

A hárommappás rendezés első köre lezárható.

Nincs olyan mappaszintű blokkoló tényező, amely akadályozná a későbbi programfejlesztést.

Ez a lezárás nem jelenti az `Aeterna dokumentációk/` mappa teljes rendezésének lezárását. Az `Aeterna dokumentációk/` mappa továbbra is külön dokumentumauditot és későbbi tartalmi összevetést igényel.

### 7.10.1 Python mappa döntései

Az új aktív XLSX exporter helye:

- `Aeterna game engine/python/tools/xlsx_export/`

A migrált exporter első fázisa elfogadható.

Státuszok:

| Útvonal | Státusz | Megjegyzés |
|---|---|---|
| `python/tools/xlsx_export/` | `KEEP_ACTIVE_SOURCE` | Az új aktív XLSX exporter tooling helye. |
| `python/tools/xlsx_export/xlsx_export.py` | `KEEP_ACTIVE_SOURCE` | Migrált exporter. Támogatja az explicit `--source-dir` és `--output-dir` opciókat. |
| `python/tests/test_xlsx_export.py` | `KEEP_ACTIVE_TEST` | Exporter unit tesztek az új modulhelyhez. |
| `python/tests/test_xlsx_export_smoke.py` | `KEEP_ACTIVE_SMOKE_TEST` | Valódi temporary XLSX → JSONL smoke teszt. |
| `python/run_xlsx_export.bat` | `KEEP_ACTIVE_RUNNER_MANUAL` | Manuális fejlesztői runner. Interaktív, `pause` van benne, audit/CI célra nem futtatandó. |
| `python/run_xlsx_export_smoke.bat` | `KEEP_ACTIVE_RUNNER_NONINTERACTIVE` | Non-interaktív smoke runner. |
| `python/tools/runtime_package/build_sample_runtime_package.py` | `KEEP_ACTIVE_SOURCE` | Sample runtime package builder. Még nincs összekötve az exporterrel. |
| `python/tests/test_build_sample_runtime_package.py` | `KEEP_ACTIVE_TEST` | Runtime package builder teszt, temp outputtal. |
| `python/sample_runtime_package/` | `GENERATED_TEST_FIXTURE` | Python oldali generated package / tesztfixture. Nem canonical adatforrás. |
| `python/main.py` | `OLD_ENGINE_REVIEW` | Régi Python engine belépési maradvány. |
| `python/data/loader.py` | `OLD_ENGINE_REVIEW` | Régi kártyabetöltő / normalizáló logika. |
| `python/data/decklist_loader.py` | `OLD_ENGINE_REVIEW` | Régi decklist loader / validator. |
| `python/engine/` | `OLD_ENGINE_REVIEW` | Régi engine maradvány. |
| `python/launcher/` | `OLD_ENGINE_REVIEW` | Régi launcher maradvány. |
| `python/simulation/` | `OLD_ENGINE_REVIEW` | Régi szimulációs maradvány. |

Az exporter jelenlegi bizonyított képességei:

- az új engine Python tooling helyről importálható;
- támogatja az explicit `--source-dir` opciót;
- támogatja az explicit `--output-dir` opciót;
- nem kötődik kötelezően a régi `XLSX export/source/` mappához;
- unit tesztekkel ellenőrzött;
- valódi temporary XLSX → JSONL smoke teszttel ellenőrzött;
- a smoke teszt nem ír tartós outputot a repository alá;
- a runtime package builder teszt nem módosítja a tracked `sample_runtime_package/manifest.json` fájlt.

A `python/input/xlsx` jelenleg nem hivatalos input mappa.

Döntés:

- most nem hozunk létre új állandó XLSX input copyt az engine alatt;
- az exporter explicit `--source-dir` paraméterrel dolgozzon;
- az XLSX input másolat jelenleg maradhat a régi `XLSX export/source/` mappában;
- a `python/input/xlsx` legfeljebb technikai fallback / későbbi döntési pont, nem aktív projektforrás.

### 7.10.2 Godot mappa döntései

A Godot ág továbbra is runtime package-et és sample contractokat fogyaszt.

Godot nem XLSX olvasó.

Godot nem canonical adatforrás.

Godot nem közvetlenül a Google Sheets / XLSX rétegből dolgozik.

Státuszok:

| Útvonal | Státusz | Megjegyzés |
|---|---|---|
| `Godot/project.godot` | `KEEP_ACTIVE_SOURCE` | Aktív Godot projekt. |
| `Godot/scripts/contract_loader/` | `KEEP_ACTIVE_SOURCE` | Runtime package és contract loader réteg. |
| `Godot/scripts/registries/` | `KEEP_ACTIVE_SOURCE` | Registry réteg. |
| `Godot/scripts/debug/` | `KEEP_ACTIVE_SOURCE` | Debug nézetek és smoke teszt scriptek. |
| `Godot/scenes/` | `HAND_AUTHORED_TEST_FIXTURE` | Debug / teszt scene-ek. |
| `Godot/sample_runtime_package/` | `GODOT_CONSUMPTION_COPY` | Godot fogyasztási másolat, nem canonical forrás. |
| `Godot/sample_contracts/` | `HAND_AUTHORED_TEST_FIXTURE` | Kézzel írt sample snapshot / action / event contractok. |
| `Godot/run_*_smoke_test.bat` | `KEEP_ACTIVE_RUNNER_NONINTERACTIVE` | Godot headless smoke futtatók. |
| `Godot/.godot/` | `CACHE_IGNORE` | Godot cache / editor / import állapot. |
| `Godot/log/` | `LOG_IGNORE` | Futási logok. |
| `Godot/*.gd.uid` | `DO_NOT_TOUCH_YET` | Godot UID meta fájlok, kézzel nem törlendők. |

A Godot oldali `sample_runtime_package/` nem kézzel szerkesztett canonical adatforrás.

Később a Python build pipeline feladata lehet a Godot consumption copy frissítése.

### 7.10.3 Régi XLSX export mappa döntései

A régi `XLSX export/` mappa jelenleg még nem törlendő és nem mozgatandó.

Státuszok:

| Útvonal | Státusz | Megjegyzés |
|---|---|---|
| `XLSX export/` | `OBSOLETE_AFTER_MIGRATION_CANDIDATE` | Régi exporter mappa. Még nem törlendő, nem mozgatandó. |
| `XLSX export/xlsx_export.py` | `MIGRATED_REPLACED_BY_ENGINE_TOOLING` | Funkciója átkerült az új engine Python tooling alá. |
| `XLSX export/test_xlsx_export.py` | `MIGRATED_REPLACED_BY_ENGINE_TOOLING` | Tesztje átkerült az engine Python tesztek közé. |
| `XLSX export/XLSX export indítása.bat` | `OBSOLETE_AFTER_MIGRATION_CANDIDATE` | Régi kézi runner. |
| `XLSX export/README.md` | `OBSOLETE_AFTER_MIGRATION_CANDIDATE` | Régi exporter dokumentáció, összevetéshez még hasznos lehet. |
| `XLSX export/source/` | `PIPELINE_INPUT_COPY` | XLSX input copy-k. Nem canonical szerkesztési forrás. |
| `XLSX export/exports/` | `GENERATED_OUTPUT` | Régi exporter outputok. |
| `XLSX export/__pycache__/` | `CACHE_IGNORE` | Python cache. |

A régi `XLSX export/` mappa csak később, külön jóváhagyással archiválható.

Archiválás feltétele:

- minden szükséges funkciója dokumentáltan átkerült az új engine Python tooling alá;
- vagy az adott funkció feleslegessé vált;
- a régi outputok és source copyk szerepe külön el lett döntve;
- nincs már szükség összevetési vagy visszakeresési referenciaként a régi mappára.

### 7.10.4 Elfogadott átmeneti duplikációk

A következő duplikációk átmenetileg elfogadhatók:

| Duplikáció | Státusz | Megjegyzés |
|---|---|---|
| `python/tools/xlsx_export/` és `XLSX export/` | Elfogadható átmeneti duplikáció | Az új tooling aktív, a régi mappa migrációs referencia. |
| `python/sample_runtime_package/` és `Godot/sample_runtime_package/` | Elfogadható átmeneti duplikáció | Python oldalon generated test fixture, Godot oldalon consumption copy. |
| `XLSX export/exports/` és későbbi engine oldali export output | Későbbi rendezési pont | Engine oldali végleges export output mappa még nincs lezárva. |
| régi Python engine fájlok és új tooling | `OLD_ENGINE_REVIEW` | Nem most rendezendő. |

Ezek a duplikációk nem blokkolják a programfejlesztést, de később külön rendezési döntést igényelnek.

### 7.10.5 Régi Python engine maradványok

A régi Python engine maradványok jelenlegi státusza:

- `OLD_ENGINE_REVIEW`

Ide tartozik többek között:

- `Aeterna game engine/python/main.py`
- `Aeterna game engine/python/data/loader.py`
- `Aeterna game engine/python/data/decklist_loader.py`
- `Aeterna game engine/python/engine/`
- `Aeterna game engine/python/launcher/`
- `Aeterna game engine/python/simulation/`

Ezeket most nem töröljük, nem mozgatjuk és nem refaktoráljuk.

Később külön döntési körben kell eldönteni, hogy:

- archiválandók;
- dokumentációs referenciaként megtartandók;
- részben migrálandók;
- vagy teljesen kiválthatók az új runtime package / contract-first pipeline által.

### 7.10.6 Aeterna dokumentációk mappa állapota

Ez a technikai adatpipeline lezárás nem jelenti az `Aeterna dokumentációk/` mappa teljes rendezésének lezárását.

Az `Aeterna dokumentációk/` mappa állapota vegyes, de kezelhető.

A dokumentációs audit alapján vannak benne:

- hivatalos szabályforrások;
- aktív adatforrások;
- élő munkadokumentumok;
- régi auditjelentések;
- átvezetett vagy részben kiváltott dokumentumok;
- régi verziójú dokumentumok;
- duplikált szerepű dokumentumok;
- később archiválható jelöltek.

A `PROJEKT_TERKEP_ES_FAJLSTATUSZ.md` jelenlegi státusza:

- `KEEP_DOCS_ACTIVE`
- frissítendő

Ez a fájl továbbra is használható aktív státuszdokumentumként, de tartalmazhat régi Python motor-központú állapotokat is.

Ezért az új technikai adatpipeline döntéseket külön szakaszban kell rögzíteni, nem a régi részek csendes átírásával.

Későbbi külön dokumentációs rendezési körben össze kell vetni többek között:

- `PROJEKT_TERKEP_ES_FAJLSTATUSZ.md` és `Aeterna game engine/docs/*`;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.md` és az új contract-first fejlesztési irány;
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md` és az új Godot/Python engine mappa;
- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md` és az új exporter / 1.9v XLSX munkaforrás;
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md` és `kartya_tabla_szabvany v1.2.md`;
- `cards.xlsx` és `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`.

### 7.10.7 Lezáró döntés

A technikai adatpipeline hárommappás rendezésének első köre lezárható.

A programfejlesztés a dokumentációs rögzítés után folytatható.

A következő programfejlesztési lépés külön döntéssel induljon.

Javasolt későbbi fejlesztési irány:

- exporter output contract mapping terv;
- később runtime package builder integráció;
- később Godot consumption copy automatikus frissítése.

Ezek közül egyik sem része ennek a mappadöntési lezárásnak.

A következő dokumentációs rendezési irány:

- az `Aeterna dokumentációk/` mappa részletes tartalmi összevetése;
- elavult és átvezetett dokumentumok jelölése;
- duplikált dokumentumszerepek tisztázása;
- későbbi archiválási javaslatok előkészítése, de törlés vagy mozgatás nélkül.

# 7.11 Dokumentációs fenntarthatósági rend

Státusz: aktív dokumentációs rendezési döntés.

Az AETERNA projektben sok dokumentációs, audit-, report-, checkpoint-, specifikációs és draftjellegű fájl jött létre.

Ez önmagában nem hiba, mert ezek a dokumentumok sok korábbi döntést, munkafázist, auditot, Codex-vizsgálatot, technikai tervet és projektállapotot őriznek meg.

Ugyanakkor a dokumentációs rendszer hosszú távon nem fenntartható, ha minden dokumentumot aktív, folyamatosan karbantartandó forrásként kezelünk.

A cél ezért nem az, hogy minden dokumentumot állandóan átírjunk, hanem az, hogy világos dokumentumszerepek és karbantartási szintek legyenek.

## 7.11.1 Alapelv

Nem minden dokumentum aktív fődokumentum.

A projekt dokumentumait szerep szerint kell kezelni:

- hivatalos forrás;
- aktív irányító dokumentum;
- aktív munkadokumentum;
- technikai specifikáció;
- checkpoint / napló;
- referencia;
- átvezetett vagy kiváltott dokumentum;
- draft / Codex-jegyzet;
- archív jelölt;
- generált riport.

A dokumentációs rend célja, hogy a tényleges projektmunka ne vesszen el a túl sok párhuzamos dokumentum kézi karbantartásában.

## 7.11.2 Dokumentum-tier rendszer

A projektben az alábbi dokumentumstátuszokat kell használni.

| Tier | Státusz | Jelentés |
|---|---|---|
| `TIER_0_OFFICIAL_SOURCE` | Hivatalos forrás | Hivatalos szabályforrás vagy canonical adatforrás. Ritkán módosul, verziózott, emberi döntéssel. |
| `TIER_1_ACTIVE_CONTROL_DOC` | Aktív irányító dokumentum | Kevés legyen belőle. Ezek határozzák meg a projekt aktuális irányát, prioritását és státuszát. |
| `TIER_2_ACTIVE_WORKDOC` | Aktív munkadokumentum | Egy konkrét munkafolyamatot támogat. Nem feltétlen projektirányító dokumentum. |
| `TIER_3_ACTIVE_SPEC` | Aktív specifikáció | Technikai specifikáció, contract, architektúra vagy runtime package dokumentum. |
| `TIER_4_CHECKPOINT_LOG` | Checkpoint / napló | Haladási napló. Nem kell visszamenőleg folyamatosan átírni, új checkpointtal bővül. |
| `TIER_5_REFERENCE` | Referencia | Hasznos visszakeresési forrás, de nem napi karbantartású dokumentum. |
| `TIER_6_MIGRATED_OR_SUPERSEDED` | Átvezetett / kiváltott | Tartalma részben vagy egészben átkerült máshová. Nem aktív főforrás. |
| `TIER_7_DRAFT_OR_CODEX_NOTE` | Draft / Codex-jegyzet | AI-válasz, Codex-draft, előkészítő jegyzet. Nem hivatalos dokumentum. |
| `TIER_8_ARCHIVE_CANDIDATE_AFTER_APPROVAL` | Archiválási jelölt | Később archiválható, de most nem törlendő és nem mozgatandó. |
| `GENERATED_REPORT` | Generált riport | Audit-, stats-, triage- vagy exportált riport. Nem kézi fődokumentum. |

Ezek a státuszok nem törlési vagy mozgatási utasítások.

Archiválás, törlés vagy mappamozgatás csak külön jóváhagyással történhet.

## 7.11.3 Minimális aktívan karbantartandó dokumentumkészlet

A projektben törekedni kell arra, hogy legfeljebb kb. 8–10 dokumentum legyen ténylegesen aktív, rendszeresen karbantartandó fődokumentum.

Javasolt aktív készlet:

| Szerep | Dokumentum | Javasolt tier |
|---|---|---|
| Gyökér projektbelépő | `README.md` | `TIER_1_ACTIVE_CONTROL_DOC` |
| Projektirányító dokumentum | `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md` | `TIER_1_ACTIVE_CONTROL_DOC` |
| Projekt-térkép / fájlstátusz | `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md` | `TIER_1_ACTIVE_CONTROL_DOC` |
| Alapjáték főforrás | `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx` | `TIER_0_OFFICIAL_SOURCE` |
| Kiegészítő főforrás | `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx` | `TIER_0_OFFICIAL_SOURCE` |
| Kártyaadatbázis munkaforrás | `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx` | `TIER_0_OFFICIAL_SOURCE` |
| Engine architektúra | `Aeterna game engine/docs/ARCHITECTURE.md` | `TIER_3_ACTIVE_SPEC` |
| Engine döntési térkép | `Aeterna game engine/docs/DECISION_MAP.md` | `TIER_3_ACTIVE_SPEC` |
| Nyitott kérdések | `Aeterna game engine/docs/OPEN_QUESTIONS.md` | `TIER_2_ACTIVE_WORKDOC` |
| Prototípus terv | `Aeterna game engine/docs/PROTOTYPE_PLANS.md` | `TIER_2_ACTIVE_WORKDOC` |
| Checkpoint napló | `Aeterna game engine/docs/checkpoints/CHECKPOINTS.md` | `TIER_4_CHECKPOINT_LOG` |

A fenti lista nem jelenti azt, hogy minden más dokumentum értéktelen.

A többi dokumentum lehet referencia, specifikáció, munkadokumentum, draft, archív jelölt vagy generált riport.

## 7.11.4 Karbantartási szabály

A dokumentumokat nem azonos gyakorisággal kell frissíteni.

### Minden nagy projektirány-változás után frissítendő

- `README.md`, ha a belépési projektkép változik;
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`, ha prioritás vagy projektirány változik;
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`, ha mappa-, fájl- vagy státuszdöntés változik;
- `DECISION_MAP.md`, ha technikai döntési kapu vagy engine irány változik.

### Csak checkpointkor frissítendő

- `CHECKPOINTS.md`

A checkpoint dokumentum napló.

Nem kell minden korábbi bejegyzést visszamenőleg átírni.

### Csak specifikáció-változáskor frissítendő

- `ARCHITECTURE.md`
- `CONTRACT_SPECIFICATION.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `ABILITY_MODULE_SYSTEM.md`
- `TECHNOLOGY_DECISIONS.md`

Ezek nem általános projektállapot-naplók, hanem technikai specifikációk.

### Csak forrásverzió-váltáskor frissítendő

- hivatalos főforrások;
- kártyaadatbázis munkaforrás;
- Excel / Google Sheets struktúra- és oszlopszabvány dokumentumok;
- kártyaaudit munkarendi dokumentumok, ha az auditmódszertan változik.

### Nem folyamatosan karbantartandó

- régi auditjelentések;
- régi reportok;
- stats riportok;
- Codex / AI draftok;
- archív dokumentumok;
- régi Python motor futási út dokumentumai;
- régi contract docx-ek, ha már MD specifikációba migráltak;
- mappaszerkezet-pillanatképek.

Ezek megőrizhetők, de nem kell minden projektváltozás után átírni őket.

## 7.11.5 Duplikált dokumentumcsoportok kezelése

A következő témákban több dokumentum is hasonló szerepet tölthet be.

Ezeket nem szabad automatikusan törölni, de státuszolni kell őket.

| Dokumentumcsoport | Kezelési elv |
|---|---|
| Projektirány / prioritások | Egy aktív projektterv legyen. A régi verziók referencia vagy archív jelöltek. |
| Projekt-térkép / fájlstátusz | Egy aktív fájlstátusz-dokumentum legyen. A mappaszerkezet-listák pillanatképek. |
| Architektúra | Régi Python motor architektúra és új game engine architektúra külön kezelendő. |
| Runtime package / contract | Aktív MD specifikációk legyenek elsődlegesek. Régi docx contract anyagok migrált referenciák lehetnek. |
| Checkpointok | Egy aktív checkpoint napló legyen. Régi checkpoint docx-ek referencia vagy archive candidate státuszúak. |
| Excel / kártyaadat szabvány | Aktív munkaforrás és oszlopszabvány legyen kijelölve. Régi verziók referencia státuszúak. |
| Audit / report | Generált riportok nem élő fődokumentumok. |
| Codex-draftok | Nem hivatalos dokumentumok, amíg külön döntés nem emeli át őket. |

## 7.11.6 Régi Python motor dokumentumai

A régi Python motorhoz kapcsolódó dokumentumok nem törlendők automatikusan.

Státuszuk jellemzően:

- `TIER_5_REFERENCE`
- `OLD_ENGINE_REFERENCE`
- `OLD_ENGINE_REVIEW`

Ezek hasznosak lehetnek:

- régi futási út megértéséhez;
- régi effectlogika feltárásához;
- AI-vs-AI és balanszfigyelési mintákhoz;
- migrálható vagy archiválható elemek eldöntéséhez.

Ugyanakkor ezek nem az új `Aeterna game engine/` contract-first irány elsődleges architektúra-dokumentumai.

## 7.11.7 Codex-draftok és AI-válaszok státusza

A Codex-draftok, AI-válaszok és újratervezési nyersanyagok nem automatikusan hivatalos dokumentumok.

Javasolt státuszuk:

- `TIER_7_DRAFT_OR_CODEX_NOTE`

Csak akkor válhatnak aktív dokumentációvá, ha:

1. külön át lettek nézve;
2. döntés született a beemelésükről;
3. megfelelő dokumentumba kerültek;
4. státuszuk és forrásszerepük rögzítve lett.

A draft nem szabályforrás.

A draft nem projektirányító dokumentum.

A draft nem automatikus fejlesztési utasítás.

## 7.11.8 Checkpoint és specifikáció elválasztása

A checkpoint napló és a technikai specifikáció nem ugyanaz.

A checkpoint feladata:

- rögzíteni, mi történt;
- milyen állapot zárult le;
- milyen teszt futott;
- milyen döntés született;
- mi a következő lépés.

A specifikáció feladata:

- leírni, hogyan kell működnie egy rendszernek;
- milyen contractok, mezők, schema-k vagy adatútvonalak érvényesek;
- milyen implementációs határok vannak.

Ezért checkpointot nem kell specifikációként kezelni, és specifikációt nem kell minden checkpoint után teljesen átírni.

## 7.11.9 Dokumentációs fenntartási kockázat

A dokumentációs rendszer legnagyobb kockázatai:

- túl sok aktívnak látszó dokumentum;
- ugyanaz az információ sok helyen;
- régi Python motor és új game engine összekeverése;
- Codex-draft hivatalos dokumentumnak látszik;
- checkpoint és specifikáció összekeverése;
- README-k vagy projektirányító dokumentumok ellentmondása;
- generált report kézi fődokumentummá válása;
- a dokumentáció fenntartása több időt vesz el, mint a tényleges kártya- vagy programfejlesztés.

Ezeket a kockázatokat úgy kell csökkenteni, hogy kevesebb aktív dokumentum maradjon, a többi pedig pontos státuszt kapjon.

## 7.11.10 Lezáró döntés

A dokumentációs rendszer első fenntarthatósági döntése:

- nem hozunk létre új dokumentumot pusztán a dokumentációs rend miatt;
- a dokumentációs fenntartási szabály a projekt-térkép / fájlstátusz dokumentumba kerül;
- ténylegesen aktívan karbantartandó dokumentumból kb. 8–10 maradjon;
- a többi dokumentum referencia, munkadokumentum, specifikáció, checkpoint, draft, archív jelölt vagy generated report státuszt kapjon;
- törlés, mozgatás vagy archiválás csak későbbi külön jóváhagyással történhet.

Ez a döntés lehetővé teszi, hogy a programfejlesztés és a kártyamunka folytatható legyen anélkül, hogy minden fejlesztési kör után a teljes dokumentumrendszert újra kellene írni.

---

## 8. Források

A dokumentum jelenlegi verziója két forrásrétegre támaszkodik.

### 8.1 Régi Python motor és korábbi projektirány forrásai

- `Aeterna dokumentációk/reference/ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`
- `Aeterna dokumentációk/archive_review/cleanup_candidates.md`
- `EFFECT_RETEG_AKTIV_UTVONAL.md`
- `EFFECT_TRIGGER_HATAROK.md`
- `kartya_tabla_szabvany_frissett.md`
- `ELEMZES_ES_FEJLESZTESI_TERV.md`
- `README.md`
- `main.py`
- `Aeterna Kártyajáték szabályrendszer.docx`
- `Aeterna dokumentációk/reference/AETERNA_Seed_Convention_v1.docx`

Ezek elsősorban a régi Python szimulációs motor, a structured runtime és a korábbi projektfeltérképezés szempontjából hasznosak.

### 8.2 Új contract-first engine és technikai adatpipeline forrásai

- `Aeterna game engine/docs/ARCHITECTURE.md`
- `Aeterna game engine/docs/RUNTIME_PACKAGE_SPECIFICATION.md`
- `Aeterna game engine/docs/CONTRACT_SPECIFICATION.md`
- `Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`
- `Aeterna game engine/docs/DECISION_MAP.md`
- `Aeterna game engine/docs/PROTOTYPE_PLANS.md`
- `Aeterna game engine/docs/OPEN_QUESTIONS.md`
- `Aeterna game engine/CHECKPOINTS.md`
- `Aeterna game engine/python/tools/xlsx_export/`
- `Aeterna game engine/python/tests/test_xlsx_export.py`
- `Aeterna game engine/python/tests/test_xlsx_export_smoke.py`
- `Aeterna game engine/python/run_xlsx_export_smoke.bat`

Ezek az új AETERNA Game Engine contract-first irányához, runtime package adatútjához, Godot fogyasztási rétegéhez és az XLSX exporter migrációhoz kapcsolódnak.

### 8.3 Dokumentációs mappa auditforrásai

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`
- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`
- `LOOKUPS.xlsx`
- `cards.xlsx`
- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`
- `kartya_tabla_szabvany v1.2.md`
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.md`

Ezek a teljes `Aeterna dokumentációk/` mappa későbbi tartalmi összevetéséhez szükségesek.

---

# 9. Verziózás

## v1

- gyökérszintű feltérképezés elkészült;
- a régi Python motor hivatalos futási útja beemelve;
- a core / wrapper / dokumentáció / audit rétegek első szintű elkülönítése megtörtént;
- a részletes mappaszintű bontás megkezdődött.

## v1.1

- `engine/` mappa részletesebb feltérképezése bekerült;
- `cards/` mappa részletesebb feltérképezése bekerült;
- `data/` mappa részletesebb feltérképezése bekerült;
- `simulation/` mappa részletesebb feltérképezése bekerült;
- `utils/` mappa részletesebb feltérképezése bekerült;
- `stats/` mappa részletesebb feltérképezése bekerült.

## v1.2

- a dokumentum értelmezése pontosítva lett a régi Python motor és az új `Aeterna game engine/` contract-first irány szétválasztásával;
- a `# 1. Állapotkép` frissítve lett hibrid projektállapotra;
- a `# 2. Hivatalos futási út` szakasz pontosítva lett régi Python szimulációs motor futási útjára;
- a `cards.xlsx` státusza régi motor input / review státuszra pontosítva;
- az `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md` régi motor referencia státusza pontosítva;
- a `# 7. Következő bővítési és rendezési feladatok` szakasz frissítve lett;
- bekerült a `# 7.10 Technikai adatpipeline rendezés – első kör lezárása` szakasz;
- rögzítve lett az új `python/tools/xlsx_export/` aktív exporter státusza;
- rögzítve lett a régi `XLSX export/` átmeneti migrációs jelölt státusza;
- rögzítve lett, hogy Godot nem XLSX olvasó és nem canonical adatforrás;
- rögzítve lett, hogy a Python oldali `sample_runtime_package/` generated test fixture, a Godot oldali `sample_runtime_package/` pedig consumption copy;
- rögzítve lett, hogy az `Aeterna dokumentációk/` mappa teljes rendezése külön későbbi dokumentumauditot igényel.