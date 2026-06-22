# Aeterna – Projekt Térkép és Fájlstátusz v1

Ez a dokumentum az Aeterna projekt jelenlegi, gyakorlati feltérképezését szolgálja.

A célja:
- a projekt fő elemeinek azonosítása
- a fájlok és mappák jelenlegi szerepének rögzítése
- az aktív runtime, a dokumentációs réteg, a tesztréteg, az audit/report réteg és a lehetséges cleanup-jelöltek elkülönítése
- egy olyan közös referencia létrehozása, amely alapján később biztonságosan lehet cleanupot, refaktort vagy részleges újraszervezést végezni

Ez a dokumentum **nem törlési lista**, és **nem refaktor-parancs**.  
Elsődleges célja a pontosabb átláthatóság.

---

# 1. Állapotkép

A projekt jelenleg egy Python-alapú, szimuláció-orientált AETERNA motor.  
A fő belépési pont a `main.py`, amely a `cards.xlsx` fájlból tölti a kártyaadatokat, majd konfiguráció alapján meccseket futtat. A rendszer jelenlegi elsődleges használata AI-vs-AI tesztfuttatás, de a hosszabb távú cél egy használhatóbb játékeszköz, később akár ember vs AI, majd ember vs ember irányban.

A projekt nem nulláról újraépítendő rendszerként van kezelve, hanem olyan meglévő rendszerként, amelynek:
- már van működő magja
- van hivatalos futási útja
- van aktív core runtime-ja
- de a köré épült segéd-, audit-, report- és átmeneti rétegek miatt rendezésre és pontosabb feltérképezésre van szüksége

---

# 2. Hivatalos futási út

A jelenlegi hivatalos futási út külön dokumentumban is rögzített.

Entrypoint:
- `main.py`

Aktív futási lánc:
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

Forrás:
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

---

# 3. Főkönyvtár – jelenlegi feltérképezés

## 3.1 Gyökérszintű fájlok

### `.editorconfig`
- státusz: még nem feltérképezett
- szerep: valószínűleg szerkesztői formázási szabályok
- runtime szerep: nincs
- megjegyzés: később ellenőrizendő

### `.gitattributes`
- státusz: aktív repository meta
- szerep: szövegfájlok LF normalizálása
- runtime szerep: nincs
- haszon: verziókezelési konzisztencia
- megjegyzés: maradjon

### `.gitignore`
- státusz: aktív repository meta
- szerep: ideiglenes Python fájlok, virtuális környezetek és logok kizárása verziókezelésből
- runtime szerep: nincs
- haszon: repository tisztaság
- megjegyzés: maradjon

### `Aeterna Kártyajáték szabályrendszer.docx`
- státusz: aktív referencia-dokumentum
- szerep: hivatalos szabályrendszer és világkönyv referencia
- runtime szerep: közvetlenül nincs
- haszon: szabályértelmezési és engine-validációs alap
- megjegyzés: kiemelten fontos dokumentációs forrás

### `AETERNA_Seed_Convention_v1.docx`
- státusz: aktív dokumentáció
- szerep: seed-konvenció és tesztprofil-azonosítás leírása
- runtime szerep: jelenleg nincs közvetlen kódoldali szerepe
- haszon: tesztek reprodukálhatósága, logazonosítás
- megjegyzés: később opcionálisan integrálható a kódba

### `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`
- státusz: aktív dokumentáció
- szerep: a jelenlegi hivatalos futási út és core / wrapper elhatárolás rögzítése
- runtime szerep: nincs
- haszon: architektúra-tisztázás
- megjegyzés: megőrzendő, rövid referenciafájlként jó

### `cards.xlsx`
- státusz: aktív, elsődleges adatforrás
- szerep: a motor hivatalos kártyatáblája
- runtime szerep: közvetlen, elsődleges
- haszon: a teljes kártyaállomány és structured mezők forrása
- megjegyzés: kiemelt fontosságú, a jelenlegi rendszer központi inputja

### `cards_ertelmezett_v1.xlsx`
- státusz: feltérképezendő
- szerep: valószínűleg korábbi feldolgozott vagy átmeneti verzió
- runtime szerep: valószínűleg nincs a hivatalos futási útban
- megjegyzés: később tisztázni kell, hogy referencia, archív vagy cleanup-jelölt

### `cards_ertelmezett_v2.xlsx`
- státusz: feltérképezendő
- szerep: valószínűleg korábbi vagy alternatív értelmezett kártyatáblázat
- runtime szerep: valószínűleg nincs a hivatalos futási útban
- megjegyzés: később tisztázni kell, hogy referencia, archív vagy cleanup-jelölt

### `cleanup_candidates.md`
- státusz: aktív audit-dokumentum
- szerep: soft cleanup jelöltek listája
- runtime szerep: nincs
- haszon: takarítási döntések előkészítése
- megjegyzés: nem törlési lista, hanem audit

### `EFFECT_RETEG_AKTIV_UTVONAL.md`
- státusz: aktív dokumentáció
- szerep: a jelenlegi effect-runtime hivatalos útjának rögzítése
- runtime szerep: nincs közvetlen
- haszon: effect-lánc pontosítása
- megjegyzés: fontos technikai referencia

### `EFFECT_TRIGGER_HATAROK.md`
- státusz: aktív dokumentáció
- szerep: trigger belépési pontok és diagnostics adapter API határainak rögzítése
- runtime szerep: nincs közvetlen
- haszon: trigger-architektúra tisztázása
- megjegyzés: fontos technikai referencia

### `ELEMZES_ES_FEJLESZTESI_TERV.md`
- státusz: aktív háttérdokumentáció
- szerep: általános elemzés és fejlesztési terv
- runtime szerep: nincs
- haszon: stratégiai referencia
- megjegyzés: felülvizsgálandó, hogy mennyire aktuális még

### `kartya_tabla_szabvany_frissett.md`
- státusz: aktív dokumentáció
- szerep: a 22 oszlopos kártyatáblázat szabványának rögzítése
- runtime szerep: közvetlenül nincs, de a loader és engine illesztésének alapja
- haszon: structured rendszer központi referenciafájlja
- megjegyzés: kiemelten fontos

### `main.py`
- státusz: aktív core runtime
- szerep: fő belépési pont, konfiguráció és futtatásindítás
- runtime szerep: közvetlen
- haszon: hivatalos indítófájl
- megjegyzés: megőrzendő

### `README.md`
- státusz: aktív dokumentáció
- szerep: rövid projektleírás és futtatási alapinformációk
- runtime szerep: nincs
- haszon: gyors belépési dokumentáció
- megjegyzés: később érdemes bővíteni

---

## 3.2 Gyökérszintű mappák

### `.git`
- státusz: verziókezelési rendszer
- runtime szerep: nincs
- megjegyzés: nem projektlogikai elem

### `Archive`
- státusz: jelenleg nem használt / archív jellegű mappa
- runtime szerep: nincs a hivatalos útban
- megjegyzés: később részletesen fel kell térképezni, mi maradjon és mi archivált történeti anyag

### `cards`
- státusz: aktív runtime mappa
- szerep: név-alapú kártyahandler és resolver réteg
- runtime szerep: közvetlen
- megjegyzés: fontos, de később tisztítandó, mert erősen név-alapú logikát hordoz

### `data`
- státusz: aktív runtime mappa
- szerep: adatbetöltés, munkafüzet-kezelés
- runtime szerep: közvetlen
- megjegyzés: a structured inputrendszer kulcsrésze

### `engine`
- státusz: aktív runtime mappa
- szerep: a motor fő magja
- runtime szerep: közvetlen
- megjegyzés: a legfontosabb technikai mappa, részletes feltérképezés szükséges

### `expansions`
- státusz: jelenleg inkább placeholder / jövőbeli réteg
- runtime szerep: korlátozott vagy jelenleg nem elsődleges
- megjegyzés: később tisztázandó

### `LOG`
- státusz: futási kimenet
- szerep: generált logok tárolása
- runtime szerep: kimeneti adat
- megjegyzés: nem core kód, de hibakereséshez fontos

### `simulation`
- státusz: aktív runtime mappa
- szerep: szimulációs konfiguráció és futtatás
- runtime szerep: közvetlen
- megjegyzés: a hivatalos futási lánc része

### `stats`
- státusz: részben aktív runtime, részben report/audit mappa
- szerep: statisztikák, diagnosztika, compliance és batch reportok
- runtime szerep: vegyes
- megjegyzés: különösen fontos lesz később az aktív és történeti reportok szétválasztása

### `test_logs_workspace`
- státusz: feltérképezendő
- szerep: valószínűleg ideiglenes logmunka-mappa
- runtime szerep: valószínűleg nincs közvetlen
- megjegyzés: később tisztázni kell

### `tests`
- státusz: aktív tesztréteg
- szerep: unittest alapú tesztfájlok
- runtime szerep: nem meccsfuttatás, hanem ellenőrzés
- megjegyzés: kulcsfontosságú a stabilizációhoz

### `utils`
- státusz: aktív támogató mappa
- szerep: segédfüggvények, logger, szöveg-normalizáció
- runtime szerep: közvetlen támogató
- megjegyzés: aktív és hasznos

---

# 4. Jelenlegi kategóriák

## 4.1 Core runtime
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

## 4.2 Wrapper / átmeneti modulok
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

## 4.3 Dokumentációs és referenciafájlok
- `Aeterna Kártyajáték szabályrendszer.docx`
- `AETERNA_Seed_Convention_v1.docx`
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`
- `EFFECT_RETEG_AKTIV_UTVONAL.md`
- `EFFECT_TRIGGER_HATAROK.md`
- `ELEMZES_ES_FEJLESZTESI_TERV.md`
- `kartya_tabla_szabvany_frissett.md`
- `README.md`

---

## 4.4 Audit / report / diagnosztikai réteg
- `cleanup_candidates.md`
- `stats/` mappa jelentős része
- compliance audit fájlok
- runtime batch summary fájlok
- standard / keyword / trigger / target / effect tag auditok

Megjegyzés:
ennek a rétegnek a pontos bontása még későbbi feladat.

---

## 4.5 Feltérképezendő / bizonytalan elemek
- `cards_ertelmezett_v1.xlsx`
- `cards_ertelmezett_v2.xlsx`
- `test_logs_workspace/`
- `Archive/` részletes tartalma
- `stats/` teljes belső bontása
- `expansions/` teljes belső tartalma

---

# 5. Jelenlegi fő kockázatok

A jelenlegi dokumentumok és eddigi feltárás alapján:

## 5.1 `engine/effects.py` túl nagy
Ez a fájl több korszak logikáját hordozza, és a projekt egyik fő technikai kockázata.

## 5.2 Név-alapú párhuzamos effect-megoldások
A `cards/resolver.py` + `cards/priority_handlers.py` működőképes, de erősen név-alapú réteg, ezért későbbi tisztításnál figyelni kell a párhuzamos effect-megoldásokra.

## 5.3 Wrapper-rétegek még nem véglegesek
A `game_state / phases / combat` szétválasztás még nem valódi moduláris szeletelés.

## 5.4 A projekt köré sok audit és segédfájl nőtt
Ez nem önmagában baj, de átláthatatlanságot okozhat, ha nincs pontosan elkülönítve:
- mi aktív runtime
- mi csak dokumentáció
- mi csak report
- mi archive-jellegű

---

# 6. Stratégiai döntés

A jelenlegi állapot alapján **nem javasolt a teljes projekt 0-ról újrakezdése**.

A javasolt irány:

1. teljesebb feltérképezés
2. fájlstátuszok pontosítása
3. aktív / wrapper / report / archive rétegek elkülönítése
4. csak ezután célzott cleanup és refaktor
5. részleges újraírás csak ott, ahol ezt a feltérképezés ténylegesen indokolja

---

# 7. Következő bővítési feladatok

Ez a dokumentum még nem teljes. A következő körökben ki kell egészíteni legalább ezekkel:

## 7.1 Mappánkénti részletes bontás
- `engine/`
- `cards/`
- `data/`
- `simulation/`
- `stats/`
- `tests/`
- `utils/`

## 7.2 Minden fájlhoz státusz
Javasolt mezők:
- fájlnév
- szerep
- aktív runtime?
- wrapper?
- teszt?
- dokumentáció?
- report?
- cleanup candidate?
- megjegyzés

## 7.3 Döntési státusz
Javasolt kategóriák:
- `keep`
- `keep_but_refactor_later`
- `archive_later`
- `remove_candidate`
- `inspect_further`

---

# 7.4 `engine/` mappa – részletesebb feltérképezés v1

Az `engine/` mappa a projekt technikai magja.  
Itt található a jelenlegi hivatalos runtime legnagyobb része: játékmenet, zónakezelés, entitás- és játékosállapot, effect-feldolgozás, triggerelés, targeting, kulcsszókezelés és több shared helper.

A jelenlegi architektúra szerint nem minden `engine/` fájl azonos státuszú:
- van, ami tényleges core runtime
- van, ami wrapper / kompatibilitási vagy átmeneti réteg
- van, ami előkészített vagy placeholder jellegű

Forrás:
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

---

## 7.4.1 `engine/` – összkép

### Core runtime jellegű elemek
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

### Wrapper / átmeneti modulok
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

## 7.4.2 Fájlonkénti bontás

### `engine/__init__.py`
- státusz: technikai csomagfájl
- szerep: Python package marker
- aktív runtime: technikai értelemben igen, de nincs benne üzleti logika
- haszon: lehetővé teszi az `engine` csomagként való használatát
- megjegyzés: üres, de normális és megtartandó

### `engine/actions.py`
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

### `engine/board_utils.py`
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

### `engine/card.py`
- státusz: aktív core runtime
- szerep: kártya- és csataegység-adatszerkezetek
- aktív runtime: igen
- megjegyzés:
  - a hivatalos core része
  - a teljes rendszer egyik alapmodell-fájlja
  - részletesebb fájltartalom-feltérképezés még szükséges

### `engine/card_metadata.py`
- státusz: aktív vagy aktívhoz közeli támogató runtime
- szerep: strukturált kártyametadata-kezelés
- aktív runtime: valószínűleg igen
- megjegyzés:
  - a structured mezők és normalizált metadata-réteg miatt fontos lehet
  - részletes ellenőrzés később szükséges

### `engine/combat.py`
- státusz: wrapper / átmeneti modul
- szerep: delegáló vagy vékony kompatibilitási harcréteg
- aktív runtime: nem elsődleges
- megjegyzés:
  - az architektúra-dokumentum szerint jelenleg kivezethető később
  - nem teljes harci moduláris szelet, csak vékony delegáló réteg

### `engine/config.py`
- státusz: aktív core runtime
- szerep: engine-konfiguráció és futási mód beállítások
- aktív runtime: igen
- haszon:
  - run mode / expansion flags / module állapotok kezelése
- megjegyzés:
  - hivatalos futási út része
  - fontos stabilizációs pont

### `engine/effect_diagnostics_v2.py`
- státusz: aktív core runtime közeli diagnosztikai réteg
- szerep: diagnostics adapter bekötése az effect trigger belépési pontokra
- aktív runtime: igen, explicit `install_effect_diagnostics()` hívással
- haszon:
  - structured / custom handler / fallback útvonalak összerendezése
  - runtime diagnosztika
- megjegyzés:
  - nem pusztán reportfájl, hanem ténylegesen bekötött runtime diagnosztikai réteg

### `engine/effects.py`
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

### `engine/effects_expansions.py`
- státusz: wrapper / előkészített modul
- szerep: expansion effect-réteg helye
- aktív runtime: nem elsődleges
- megjegyzés:
  - jelenleg inkább előkészített vagy átmeneti hely
  - részletes ellenőrzés szükséges

### `engine/game.py`
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

### `engine/game_state.py`
- státusz: wrapper / átmeneti modul
- szerep: vékony állapot-adapter
- aktív runtime: nem elsődleges
- megjegyzés:
  - az architektúra-dokumentum szerint wrapper marad átmenetileg
  - nem teljes értékű külön állapotszelet

### `engine/keyword_engine.py`
- státusz: aktív core runtime
- szerep: hivatalos kulcsszó-runtime réteg
- aktív runtime: igen
- megjegyzés:
  - ez a hivatalos keyword-útvonal
  - megőrzendő, fontos core elem

### `engine/keyword_registry.py`
- státusz: aktív core runtime
- szerep: kulcsszavak regisztrációs / leképezési rétege
- aktív runtime: igen
- megjegyzés:
  - a keyword rendszer része
  - részletesebb bontás később kell

### `engine/keywords.py`
- státusz: kompatibilitási wrapper
- szerep: re-export / compatibility layer a keyword engine fölött
- aktív runtime: csak másodlagosan
- megjegyzés:
  - nem elsődleges kulcsszóútvonal
  - átmenetileg maradhat

### `engine/keywords_core.py`
- státusz: wrapper / kompatibilitási réteg
- szerep: re-export jellegű köztes réteg
- aktív runtime: nem elsődleges
- megjegyzés:
  - az architektúra-dokumentum szerint wrapper marad átmenetileg
  - később kivezethető lehet

### `engine/logging_utils.py`
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

### `engine/phases.py`
- státusz: wrapper / átmeneti modul
- szerep: delegáló fázisréteg
- aktív runtime: nem elsődleges
- megjegyzés:
  - az architektúra-dokumentum szerint később kivezethető
  - jelenleg nem valódi külön fázismotor

### `engine/player.py`
- státusz: aktív core runtime
- szerep: játékosállapot és játékos-műveletek
- aktív runtime: igen
- megjegyzés:
  - pakli, kéz, temető, pecsétek, erőforrás stb. miatt központi elem
  - részletes bontás később szükséges

### `engine/structured_effects.py`
- státusz: aktív core runtime
- szerep: structured, metadata-driven effect feldolgozás
- aktív runtime: igen
- haszon:
  - canonical mezőkből induló effectpróbálkozások
  - structured routing
- megjegyzés:
  - a modernizált effect-réteg kulcseleme
  - fontos, megőrzendő

### `engine/targeting.py`
- státusz: aktív core runtime
- szerep: célpont-validáció és targeting állapotkezelés
- aktív runtime: igen
- megjegyzés:
  - untargetable / spell target / validity logika miatt fontos központi elem

### `engine/triggers.py`
- státusz: aktív core runtime
- szerep: trigger dispatch és eseménykezelési réteg
- aktív runtime: igen
- megjegyzés:
  - a triggeres képességek és runtime események kulcseleme

---

## 7.4.3 `engine/` – elsődleges státuszdöntések v1

### Egyértelműen megtartandó core
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

### Megtartandó, de később refaktor / újraszervezés alatt vizsgálandó
- `effects.py`
- `game.py`
- `actions.py`
- `cards` réteggel együtt a teljes effect-lánc kapcsolata

### Wrapper / kompatibilitási vagy átmeneti elemek
- `combat.py`
- `game_state.py`
- `keywords.py`
- `keywords_core.py`
- `phases.py`
- `effects_expansions.py`

### További feltérképezést igényel
- `card_metadata.py`

---

## 7.4.4 `engine/` – fő megfigyelések

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

## 7.4.5 Következő feladat az `engine/` mappához

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

## 7.5 `cards/` mappa – részletesebb feltérképezés v1

A `cards/` mappa a jelenlegi motor név-alapú, kártyaspecifikus feloldási rétegét tartalmazza.  
Ez a structured effect-réteg mellett és után működő, konkrét lapnevekre épülő handler-rendszer.

A jelenlegi architektúra szerint a `cards/` mappa aktív része a hivatalos runtime-nak, különösen:
- `cards/resolver.py`
- `cards/priority_handlers.py`

Forrás:
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

---

### `cards/__init__.py`
- státusz: technikai csomagfájl
- szerep: rövid leírás alapján „lapfeloldási segédmodulok” csomagjelölője
- aktív runtime: technikai értelemben igen, üzleti logika szempontból minimális
- haszon: package marker és rövid modulazonosítás
- megjegyzés: megtartandó, de nem hordoz tényleges runtime logikát

### `cards/resolver.py`
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

### `cards/priority_handlers.py`
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

## 7.5.1 `cards/` – összkép

A `cards/` mappa jelenleg nem segéd- vagy mellékréteg, hanem a működő motor része.

A mostani állapot alapján a szerepe:
1. a structured runtime után vagy mellett speciális laplogikák biztosítása
2. trap, burst és egyes triggeres lapok konkrét feloldása
3. olyan card-local viselkedések kezelése, amelyeket a shared effect-primitívek még nem fednek le teljesen

Ez a mappa tehát a jelenlegi rendszerben **nem opcionális**, még akkor sem, ha hosszabb távon részben kiváltható vagy csökkenthető a szerepe.

---

## 7.5.2 `cards/` – elsődleges státuszdöntések v1

### Egyértelműen megtartandó
- `resolver.py`
- `priority_handlers.py`

### Megtartandó, de később refaktorálandó
- `resolver.py`
- `priority_handlers.py`

### Technikai csomagfájl
- `__init__.py`

---

## 7.5.3 `cards/` – fő megfigyelések

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

## 7.5.4 Következő feladat a `cards/` mappához

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

## 7.6 `data/` mappa – részletesebb feltérképezés v1

A `data/` mappa a projekt bemeneti adatkezelési rétegét tartalmazza.  
Jelenleg kicsi, de kulcsszerepű mappa, mert itt történik a `cards.xlsx` munkafüzet beolvasása, normalizálása, validálása és a runtime által használható kártyaobjektumok előállítása.

A jelenlegi hivatalos futási út szerint a `data/loader.py` az aktív motor része.

Forrás:
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

---

### `data/__init__.py`
- státusz: technikai csomagfájl
- szerep: Python package marker
- aktív runtime: technikai értelemben igen, üzleti logika szempontból nincs
- haszon: lehetővé teszi a `data` csomagként való importálását
- megjegyzés: üres, normális, megtartandó

### `data/loader.py`
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

## 7.6.1 `data/` – összkép

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

## 7.6.2 `data/` – elsődleges státuszdöntések v1

### Egyértelműen megtartandó
- `loader.py`

### Technikai csomagfájl
- `__init__.py`

---

## 7.6.3 `data/` – fő megfigyelések

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

## 7.6.4 Kockázatok és későbbi figyelendő pontok

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

## 7.6.5 Következő feladat a `data/` mappához

A következő körökben érdemes külön dokumentálni:
- a `Kartya` objektummá alakítás pontos menetét
- a `card_metadata` és a loader kapcsolatát
- a validation issue kategóriák jelentését
- azt, hogy mely warning típusok tekinthetők:
  - alias-normalizálható zajnak
  - legacy kompatibilitási jelnek
  - valódi adatminőségi problémának

---

## 7.7 `simulation/` mappa – részletesebb feltérképezés v1

A `simulation/` mappa a projekt futtatási és meccssorozat-kezelési rétege.  
Itt dől el, hogy a program milyen konfigurációval indul, milyen birodalmakat használ, hogyan inicializálja az engine-konfigurációt, és hogyan futtat le több egymást követő meccset.

A jelenlegi hivatalos futási út szerint a `simulation/config.py` és a `simulation/runner.py` az aktív runtime részei.

Forrás:
- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

---

### `simulation/__init__.py`
- státusz: technikai csomagfájl
- szerep: Python package marker
- aktív runtime: technikai értelemben igen, üzleti logika szempontból nincs
- haszon: lehetővé teszi a `simulation` csomagként való importálását
- megjegyzés: üres, normális, megtartandó

### `simulation/config.py`
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

### `simulation/runner.py`
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

## 7.7.1 `simulation/` – összkép

A `simulation/` mappa jelenleg három jól elkülönülő szerepet tölt be:

1. konfigurációs szerződés (`config.py`)
2. futtatási orchestration (`runner.py`)
3. technikai package marker (`__init__.py`)

Ez a mappa jelen állapotában nem tűnik túlburjánzottnak vagy kuszának.  
Épp ellenkezőleg: a projekt egyik rendezettebb és jól értelmezhető része.

---

## 7.7.2 `simulation/` – elsődleges státuszdöntések v1

### Egyértelműen megtartandó
- `config.py`
- `runner.py`

### Technikai csomagfájl
- `__init__.py`

---

## 7.7.3 `simulation/` – fő megfigyelések

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

## 7.7.4 Kockázatok és későbbi figyelendő pontok

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

## 7.7.5 Következő feladat a `simulation/` mappához

A következő körökben érdemes külön dokumentálni:
- a `main.py` és a `SimulationConfig` kapcsolatát
- a seed-konvenció és a tényleges futtatási konfiguráció viszonyát
- a log metric-ek szerepét
- a jövőbeli scenario / scripted tesztprofil támogatás pontos helyét a futtatási láncban

---

## 7.8 `utils/` mappa – részletesebb feltérképezés v1

A `utils/` mappa a projekt általános segédfüggvényeit tartalmazza.  
Jelenleg kicsi, de a gyakorlatban nagyon fontos támogató réteg, mert:
- a teljes runtime logolása támaszkodik rá
- a szöveg-normalizálás és karakterhelyreállítás is innen jön

A jelenlegi projektben a `utils/` nem mellékes kényelmi réteg, hanem több core modul által használt aktív segédréteg.

---

### `utils/__init__.py`
- státusz: technikai csomagfájl
- szerep: Python package marker
- aktív runtime: technikai értelemben igen, üzleti logika szempontból nincs
- haszon: lehetővé teszi a `utils` csomagként való importálását
- megjegyzés: üres, normális, megtartandó

### `utils/logger.py`
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

### `utils/text.py`
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

## 7.8.1 `utils/` – összkép

A `utils/` mappa jelenleg két valódi funkcionális alapelemre épül:

1. központi logolás (`logger.py`)
2. szöveg-normalizálás (`text.py`)

Ez a mappa jelen formájában nem tűnik túl nagyra nőttnek vagy kuszának.  
Inkább tipikus kis utility-réteg, amelyet a projekt több aktív része használ.

---

## 7.8.2 `utils/` – elsődleges státuszdöntések v1

### Egyértelműen megtartandó
- `logger.py`
- `text.py`

### Technikai csomagfájl
- `__init__.py`

---

## 7.8.3 `utils/` – fő megfigyelések

1. A `logger.py` jelenleg valódi infrastruktúra-fájl:
   - nem csak print-wrapper
   - hanem a projekt egységes logrétegének alapja :contentReference[oaicite:3]{index=3}

2. A `text.py` a projektben a vártnál fontosabb:
   - a név-alapú és alias-alapú rendszerek miatt a normalizált szöveg-összehasonlítás alapvető
   - a hibás karakterkódolási állapotok miatt a mojibake-javítás is praktikus, nem csak kényelmi funkció :contentReference[oaicite:4]{index=4}

3. A `utils/` mappa alapján sem az látszik, hogy a projektet újra kellene kezdeni.
   Ez a réteg inkább tiszta, stabil és jól használható.

---

## 7.8.4 Kockázatok és későbbi figyelendő pontok

1. A `logger.py` további bővítéseknél figyelni kell arra, hogy:
   - ne váljon túl sok speciális projektlogika hordozójává
   - maradjon inkább általános logger-réteg

2. A `text.py` normalizálási szabályai a név-alapú rendszer miatt érzékenyek lehetnek:
   - ha később változik a szövegkezelés vagy az aliasrendszer, ezt is újra kell nézni

3. Jelenleg azonban egyik fájl sem tűnik refaktor-sürgős vagy problémás pontnak.

---

## 7.8.5 Következő feladat a `utils/` mappához

A következő körökben érdemes külön dokumentálni:
- mely modulok támaszkodnak közvetlenül a `normalize_lookup_text(...)` függvényre
- és hogy a logger mely pontokon működik csak nyers naplózóként, illetve hol kapott már projekt-specifikus technikai logkategóriákat

---

## 7.9 `stats/` mappa – részletesebb feltérképezés v1

A `stats/` mappa jelenleg vegyes szerepű terület:
- van benne aktív runtime-hoz kapcsolódó elem
- vannak audit script-ek
- vannak batch summaryk
- vannak compliance reportok
- vannak történeti vagy egyszeri elemzési fájlok is

Ez az a mappa, amely a legerősebben mutatja, hogy a projekt köré idővel sok diagnosztikai és fejlesztéstámogató réteg nőtt.

A felhasználói megjegyzés alapján ez a mappa az egyik fő oka annak az érzésnek, hogy a projekt túl nagyra nőtt és karbantartást igényel. Ez a megfigyelés a jelenlegi fájllista alapján indokoltnak tűnik.

---

### `stats/__init__.py`
- státusz: technikai csomagfájl
- szerep: Python package marker
- aktív runtime: technikai értelemben igen, üzleti logika szempontból nincs
- megjegyzés: megtartandó, de önálló funkcionális szerepe nincs

### `stats/analyzer.py`
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

## 7.9.1 Audit / script jellegű fájlok

### `cards_xlsx_audit.py`
- státusz: fejlesztői audit script
- szerep: a `cards.xlsx` vagy kapcsolódó táblák auditálása
- aktív runtime: valószínűleg nem
- megjegyzés: diagnosztikai / ellenőrző segédfájl

### `full_card_analysis.py`
- státusz: fejlesztői elemző script
- szerep: teljes kártyaelemzés vagy táblázati átvilágítás
- aktív runtime: valószínűleg nem
- megjegyzés: fejlesztéstámogató script, nem meccsfuttatási mag

### `standard_cleanup_audit.py`
- státusz: audit script
- szerep: standard-cleanup átvilágítás
- aktív runtime: nem
- megjegyzés: egyszeri vagy időszakos standardizációs segédfájl

### `standard_engine_audit.py`
- státusz: audit script
- szerep: szabvány ↔ engine audit előállítása
- aktív runtime: nem
- megjegyzés: fejlesztői ellenőrzéshez hasznos, nem futtatási mag

---

## 7.9.2 Batch summary és compliance report fájlok

### Canonical runtime batch summaryk
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

### Compliance audit reportok
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

### Standard / cleanup / triage reportok
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

## 7.9.3 Témaspecifikus audit / elemzési fájlok

### Ignis / Hamvaskezű fókuszú fájlok
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

### Általános kártyaelemzési fájlok
- `cards_per_card_analysis.md`
- `cards_metadata_enrichment.csv`

- státusz: elemzési / adatgazdagítási mellékfájlok
- szerep: kártyaszintű elemzés és metadata enrichment
- aktív runtime: valószínűleg nem
- megjegyzés:
  - hasznos segédanyag lehet
  - tisztázni kell, hogy jelenleg melyik tekinthető élő fejlesztői referenciának

---

## 7.9.4 `stats/` – összkép

A `stats/` mappa jelenleg nem egységes.

Nagy valószínűséggel négyféle szerep keveredik benne:
1. aktív statisztikai runtime réteg (`analyzer.py`)
2. audit-generáló script-ek
3. egyszeri vagy időszakos compliance / cleanup reportok
4. történeti fejlesztési batch-summaryk

Ez pontosan az a mappa, ahol a későbbi cleanup és karbantartási igény a legerősebben indokolt.

---

## 7.9.5 `stats/` – elsődleges státuszdöntések v1

### Egyértelműen megtartandó aktív elem
- `analyzer.py`

### Megtartandó, de report / audit kategóriába szervezendő elemek
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

### Megtartandó, de script / tooling kategóriába rendezendő elemek
- `cards_xlsx_audit.py`
- `full_card_analysis.py`
- `standard_cleanup_audit.py`
- `standard_engine_audit.py`

### Technikai csomagfájl
- `__init__.py`

---

## 7.9.6 `stats/` – fő megfigyelések

1. A `stats/` mappa jelenlegi állapota valóban erősen támogatja azt az érzést, hogy a projekt köré sok fejlesztési mellékréteg nőtt.

2. Ez azonban nem feltétlenül azt jelenti, hogy a projektet újra kell kezdeni, hanem inkább azt, hogy:
   - a `stats/` mappa túl sokféle célt szolgál egy helyen
   - az aktív runtime elem és a történeti / audit anyagok nincsenek eléggé szétválasztva

3. A fájlnevek alapján a `stats/` elsősorban nem “hibás”, hanem “túlterhelt” mappa:
   - túl sok report és audit egy szinten
   - kevés explicit szerkezeti különválasztás

4. Ez a mappa jó jelölt egy későbbi biztonságos strukturális cleanupra.

---

## 7.9.7 Javasolt későbbi rendezési irány a `stats/` mappához

A jelenlegi lista alapján hosszabb távon érdemes lehet különválasztani legalább ezeket:

### `stats/runtime/`
- aktív runtime-közeli statisztikai elemek
- pl. `analyzer.py`

### `stats/scripts/`
- audit-generáló vagy elemző Python scriptek
- pl. `cards_xlsx_audit.py`, `full_card_analysis.py`, `standard_cleanup_audit.py`, `standard_engine_audit.py`

### `stats/reports/compliance/`
- keyword / trigger / target / effect / standard compliance reportok

### `stats/reports/batches/`
- canonical runtime batch summaryk

### `stats/reports/domain_specific/`
- birodalom- vagy klánspecifikus auditok
- pl. Ignis / Hamvaskezű fókuszú reportok

### `stats/reports/cleanup/`
- triage, alias-map, standardization gaps, warning backlog reportok

Ez jelenleg még csak javasolt szerkezeti irány, nem azonnali végrehajtási terv.

---

## 7.9.8 Következő feladat a `stats/` mappához

A következő körökben érdemes külön feltárni:
- `analyzer.py` pontos szerepét és függőségeit
- mely reportok számítanak még aktív fejlesztői referenciának
- mely reportok tisztán történeti anyagok
- mely script-ek futnak még ténylegesen
- a duplikátumgyanús és vegyes elnevezésű fájlok sorsát

Ez a mappa külön karbantartási / cleanup tervet érdemel.

---


# 8. Források

A dokumentum jelenlegi verziója ezekre az anyagokra támaszkodik:

- `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`
- `cleanup_candidates.md`
- `EFFECT_RETEG_AKTIV_UTVONAL.md`
- `EFFECT_TRIGGER_HATAROK.md`
- `kartya_tabla_szabvany_frissett.md`
- `ELEMZES_ES_FEJLESZTESI_TERV.md`
- `README.md`
- `main.py`
- `Aeterna Kártyajáték szabályrendszer.docx`
- `AETERNA_Seed_Convention_v1.docx`

---

# 9. Verziózás

## v1
- gyökérszintű feltérképezés elkészült
- a hivatalos futási út beemelve
- a core / wrapper / dokumentáció / audit rétegek első szintű elkülönítése megtörtént
- a teljes mappaszintű bontás még hátravan