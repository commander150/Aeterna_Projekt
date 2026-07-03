# Aeterna Projekt

Az **AETERNA** egy saját fejlesztésű kártyajáték-projekt, amely jelenleg több egymástól elkülönített, de később összehangolható rétegből áll.

A projekt jelenlegi állapota hibrid:

- fizikai TCG / kártyajáték szabály- és kártyatervezési projekt;
- hivatalos főforrásokra épülő dokumentációs rendszer;
- Google Sheets / XLSX alapú kártyaadatbázis-munkaforrás;
- régi Python-alapú szimulációs motor, jelenleg review státuszban;
- új `Aeterna game engine/` contract-first digitális programegység;
- Godot alapú runtime package és sample contract fogyasztói prototípus.

A projektet nem nulláról újraépítendő rendszerként kezeljük.

A jelenlegi stratégia:

1. meglévő értékek feltérképezése;
2. régi és új technikai irányok szétválasztása;
3. hivatalos szabályforrások, kártyaadat-források és runtime package adatút elkülönítése;
4. dokumentációs és mappaszintű döntések rögzítése;
5. célzott, kis lépésű fejlesztések;
6. nagyobb refaktor vagy integráció csak külön döntés után.

---

## Fő projektállapot

### Hivatalos szabályi alap

Az AETERNA jelenlegi aktív szabályi alapját két hivatalos főforrás alkotja:

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

Ezek az elsődleges szabályi referenciák minden szabályértelmezési, kártyatervezési, kártyaauditálási és későbbi engine-kompatibilitási munkánál.

### Kártyaadatbázis

A fő kártyaadatbázis-munkaforrás:

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`

A tényleges szerkesztési forrás Google Sheets / XLSX alapú.

A lokális XLSX, JSONL, TSV vagy exportált állományokat mindig szerepük szerint kell kezelni:

- canonical munkaforrás;
- pipeline input copy;
- generated output;
- régi motoros referencia;
- vagy audit / összevetési segédanyag.

### Régi Python szimulációs motor

A régi Python motor továbbra is értékes referencia.

Jelenlegi státusza:

- `OLD_ENGINE_REVIEW`
- `OLD_ENGINE_REFERENCE`

Ez azt jelenti, hogy nem törlendő és nem eldobandó, de nem is ez az elsődleges új fejlesztési irány.

A régi motor hasznos lehet:

- AI-vs-AI tesztelési tapasztalatokhoz;
- balanszfigyelési mintákhoz;
- effectlogikai előzményekhez;
- diagnosztikai és logging megoldásokhoz;
- régi runtime működés összevetéséhez;
- későbbi migrációs döntések előkészítéséhez.

A régi Python motor nagyobb refaktora vagy továbbfejlesztése csak külön döntés után induljon.

### Új Aeterna game engine

Az új digitális fejlesztési irány az `Aeterna game engine/` mappában található.

Ez contract-first szemléletű programegység.

Fő részei:

- `Aeterna game engine/python/`
- `Aeterna game engine/Godot/`

A Python ág szerepe:

- XLSX export tooling;
- validáció;
- runtime package build irány;
- tesztek;
- későbbi adat-előkészítés;
- későbbi AI / batch jellegű feldolgozás.

A Godot ág szerepe:

- runtime package fogyasztás;
- registry-k;
- sample contractok betöltése;
- debug nézetek;
- smoke testek;
- későbbi interaktív prototípus előkészítése.

Fontos döntés:

- Godot nem XLSX olvasó;
- Godot nem canonical adatforrás;
- Godot a runtime package-et és contractokat fogyasztja;
- Python végzi az exportálási, validálási és package-előkészítési feladatokat.

---

## Technikai adatpipeline aktuális döntései

Az XLSX exporter első migrációs fázisa lezárult.

Aktív exporter helye:

- `Aeterna game engine/python/tools/xlsx_export/`

Státuszok:

- `Aeterna game engine/python/tools/xlsx_export/`: `KEEP_ACTIVE_SOURCE`
- `Aeterna game engine/python/tests/test_xlsx_export.py`: `KEEP_ACTIVE_TEST`
- `Aeterna game engine/python/tests/test_xlsx_export_smoke.py`: `KEEP_ACTIVE_SMOKE_TEST`
- `Aeterna game engine/python/publish_runtime_package_to_godot.bat`: `KEEP_ACTIVE_PRIMARY_PIPELINE_RUNNER`
- `Aeterna game engine/python/run_xlsx_export.bat`: `KEEP_ACTIVE_RUNNER_MANUAL_RAW_EXPORT`
- `Aeterna game engine/python/run_xlsx_export_smoke.bat`: `KEEP_ACTIVE_RUNNER_NONINTERACTIVE`

A régi `XLSX export/` mappa státusza:

- `OBSOLETE_AFTER_MIGRATION_CANDIDATE`

Ez még nem törlendő és nem mozgatandó, de nem aktív pipeline input.

Elsődleges fejlesztői runtime package út:

- `Aeterna game engine/python/publish_runtime_package_to_godot.bat`

Ez a canonical kártyaadatbázis XLSX-ből TEMP alatti candidate runtime package-et épít, validál, és csak sikeres validáció után publikál a Godot `runtime_package/` mappába.

A `run_xlsx_export.bat` csak nyers/debug export runner. Nem ez a fő Godot pipeline.

A `sample_runtime_package` két külön szerepet tölt be:

- Python oldalon: `GENERATED_TEST_FIXTURE`
- Godot oldalon: `GODOT_CONSUMPTION_COPY`

A Godot oldali `sample_contracts/` státusza:

- `HAND_AUTHORED_TEST_FIXTURE`

---

## Futtatás és tesztelés

A projektben több technikai réteg van, ezért nincs egyetlen univerzális futtatási parancs az egész projektre.

### Régi Python motor

A régi Python motor jelenleg legacy / review jellegű referencia.

Jelenleg még megtalálható működő belépési pontként az új engine Python mappájában is:

- `Aeterna game engine/python/main.py`

Ez történeti okból maradt meg, mert a korábbi szimulációs program ezt használta belépési pontként.

Archív / összevetési másolata:

- `Archive/old python engine/`

Fontos: ez a `main.py` nem az új contract-first engine végleges belépési pontja. Új engine belépési pontot később külön, egyértelmű névvel kell létrehozni, hogy ne keveredjen a legacy szimulátorral.

### Új engine Python tooling

Az új Python tooling az `Aeterna game engine/python/` mappában található.

A konkrét futtatás és tesztelés az ottani runner BAT fájlokkal és unit tesztekkel történik.

Fontosabb ismert elemek:

- `publish_runtime_package_to_godot.bat`
- `run_xlsx_export.bat`
- `run_xlsx_export_smoke.bat`
- `run_build_sample_package.bat`
- `run_tests.bat`

A `publish_runtime_package_to_godot.bat` az elsődleges fejlesztői XLSX → runtime package → Godot publikáló út.

A `run_xlsx_export.bat` manuális nyers/debug export runner, nem a fő runtime package pipeline.

Audit / CI jellegű futtatáshoz a non-interaktív smoke runner előnyösebb.

### Godot ág

A Godot ág az `Aeterna game engine/Godot/` mappában található.

Jelenlegi szerepe:

- runtime package betöltés;
- sample contractok fogyasztása;
- debug nézetek;
- smoke tesztek.

A Godot ág nem közvetlen XLSX feldolgozó és nem canonical adatforrás.

---

## Projektirányító dokumentumok

A projekt fejlesztésénél, dokumentációs döntéseinél, Codex-feladatoknál és refaktor előtt az aktuális projektirányító dokumentumokat kell figyelembe venni.

Kiemelten fontos dokumentumok:

- `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`
- `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`
- `Aeterna dokumentációk/AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`
- `Aeterna dokumentációk/AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`
- `Aeterna dokumentációk/AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`
- `Aeterna game engine/docs/ARCHITECTURE.md`
- `Aeterna game engine/docs/RUNTIME_PACKAGE_SPECIFICATION.md`
- `Aeterna game engine/docs/CONTRACT_SPECIFICATION.md`
- `Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`
- `Aeterna game engine/docs/checkpoints/CHECKPOINTS.md`

Régi Python motorhoz kapcsolódó referencia:

- `Aeterna dokumentációk/reference/ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

Ez jelenleg a régi Python szimulációs motor futási útjának referenciája, nem az új contract-first engine teljes célarchitektúrája.

---

## Jelenlegi elsődleges fókusz

A jelenlegi elsődleges fókusz nem egyetlen nagy fejlesztési lépés.

Aktuális munkairányok:

1. dokumentációs és mappaszintű rendezés;
2. aktív, elavult, átvezetett és review státuszú dokumentumok elkülönítése;
3. technikai adatpipeline döntések rögzítése;
4. új contract-first engine adatútjának tisztán tartása;
5. kártyaadatbázis és hivatalos főforrások kapcsolatának tisztítása;
6. következő programfejlesztési döntési kapu előkészítése.

A következő programfejlesztési jelölt:

- exporter output contract mapping terv

Ez még nem runtime package builder integráció.

---

## Amit most nem csinálunk

Jelenlegi nem-célok:

- régi Python motor nagy refaktora;
- régi `XLSX export/` mappa törlése vagy mozgatása;
- Godot közvetlen XLSX olvasóvá alakítása;
- teljes runtime package builder integráció előzetes mapping nélkül;
- teljes Godot játék-UI fejlesztés;
- tömeges kártyaátírás előzetes audit nélkül;
- dokumentumok tömeges átírása fenntartási stratégia nélkül;
- sok nagy irány egyidejű összekeverése.

---

## Dokumentációs fenntartási megjegyzés

A projektben sok dokumentum jött létre.

Ez önmagában hasznos, mert megőrizte a döntéseket, auditokat, státuszokat és korábbi munkafázisokat, de hosszú távon fenntartási kockázatot is jelent.

Nem cél, hogy minden dokumentum folyamatosan, párhuzamosan frissüljön.

Későbbi dokumentációs rendezési cél:

- kevés aktív irányító dokumentum kijelölése;
- régi vagy átvezetett dokumentumok referencia státuszba tétele;
- archiválási jelöltek kijelölése törlés nélkül;
- dokumentumszerepek tisztázása;
- duplikált tartalmak csökkentése;
- csak a valóban aktív dokumentumok folyamatos karbantartása.

Ez a dokumentációs fenntartási kérdés külön projektfeladatként kezelendő.

---

## Codex és fejlesztési munkarend

Codex vagy más asszisztensi munka előtt mindig tisztázni kell:

- melyik mappát érinti;
- melyik technikai réteget érinti;
- régi Python motoros referencia-e;
- új contract-first engine fejlesztés-e;
- dokumentációs audit-e;
- kártyaadatbázis-munka-e;
- cleanup / refaktor / törlési javaslat-e;
- generated output vagy canonical forrás érintett-e.

Általános szabályok:

- ne legyen túl nagy, általános „nézd át az egész projektet” feladat;
- előbb read-only audit, utána döntés, utána célzott módosítás;
- minden Git parancs legyen `git --no-pager`;
- interaktív runner ne fusson audit/CI célra;
- törlés, mozgatás, archiválás csak külön jóváhagyással;
- régi motor és új engine ne keveredjen egy feladatban;
- dokumentáció és programfejlesztés ne fusson össze kontroll nélkül.

---

## Rövid prompt-előtag Codex feladatokhoz

Igazodj az aktuális AETERNA projektirányító dokumentumokhoz.

A projekt jelenleg hibrid:

- hivatalos TCG szabály- és kártyatervezési dokumentáció;
- régi Python szimulációs motor review státuszban;
- új `Aeterna game engine/` contract-first Python tooling + Godot fogyasztói ág;
- runtime package alapú adatcontract.

A feladat előtt tisztázd, hogy a kérés:

- dokumentációs audit;
- kártyaadatbázis-munka;
- régi Python motor review;
- új engine Python tooling;
- Godot fogyasztói réteg;
- runtime package / contract;
- teszt;
- generated output;
- cleanup / refaktor;
- vagy archiválási javaslat.

Ne módosíts, törölj, mozgass vagy commitolj külön engedély nélkül.

Ha módosítás kell, előbb pontosítsd, mely fájlokra korlátozódik.
