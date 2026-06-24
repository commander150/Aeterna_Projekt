# AETERNA Game Engine

Az **AETERNA Game Engine** az AETERNA kártyajáték új, contract-first digitális programegysége.

A projekt célja nem a régi Python program közvetlen folytatása, és nem is azonnali teljes digitális játékprogram.

A jelenlegi cél egy tiszta, fokozatosan bővíthető Python / Godot alap kialakítása, amelyben:

- a Python oldal runtime package-et tud generálni;
- a Godot / GDScript oldal contract-loaderként be tudja tölteni a package-et;
- a két oldal JSON / JSONL alapú contractokon keresztül kapcsolódik;
- a snapshot, legal actions, action request / response, event log és diagnostics rétegek fokozatosan épülnek rá;
- a fizikai AETERNA TCG szabályi logikája továbbra is elsődleges marad.

---

## Projektstátusz

A jelenlegi dokumentált irány:

- contract-first architektúra;
- külön Python és Godot ág;
- runtime package alapú adatátadás;
- Godot oldali loader és debug nézetek;
- fokozatosan erősített sample contract réteg;
- későbbi rules engine, AI és digitális kliens.

A jelenlegi prototípus már bizonyította:

- Python sample runtime package generator működését;
- többfájlos sample runtime package előállítását;
- Godot runtime package loader működését;
- Godot sample contracts loader működését;
- Snapshot viewer debug nézet működését;
- Legal action debug panel működését;
- Event log debug view működését;
- kapcsolódó smoke testek futtathatóságát.

A pontos technikai checkpoint állapot helye:

- `CHECKPOINTS.md`

---

## Mit nem bizonyít még a jelenlegi állapot?

A jelenlegi prototípus még nem teljes engine.

Még nem bizonyított:

- teljes szabálymotor;
- valódi legal action számítás szabályból;
- action request teljes feldolgozása;
- action-végrehajtás;
- kártyaképességek teljes futtatása;
- AI döntéshozatal;
- AI-vs-AI balanszteszt;
- végleges játék UI;
- PvP;
- teljes AETERNA kártyaadatbázis futtatása.

---

## Mappaszerkezet

A fő projektmappa:

- `Aeterna game engine/`

Javasolt fő szerkezet:

- `python/`
- `Godot/`
- `docs/`
- `README.md`
- `CHECKPOINTS.md`

A `python/` ág feladata:

- sample runtime package generálás;
- későbbi exportvalidáció;
- későbbi runtime package builder;
- Python oldali tesztek;
- későbbi AI-vs-AI / batch tesztelés lehetősége;
- diagnostics és riportkészítés.

A `Godot/` ág feladata:

- Godot projekt;
- GDScript contract-loader;
- registry-k;
- debug nézetek;
- headless smoke testek;
- későbbi játékos UI;
- későbbi rules runtime lehetőség.

A `docs/` ág feladata:

- architektúra;
- technológiai döntések;
- contract-specifikáció;
- runtime package specifikáció;
- ability module rendszer;
- prototípustervek;
- nyitott kérdések;
- checkpointok.

---

## Fő dokumentumok

A projekt fő dokumentációs fájljai:

- `CHECKPOINTS.md`
- `OPEN_QUESTIONS.md`
- `docs/DECISION_MAP.md`
- `docs/ARCHITECTURE.md`
- `docs/TECHNOLOGY_DECISIONS.md`
- `docs/CONTRACT_SPECIFICATION.md`
- `docs/RUNTIME_PACKAGE_SPECIFICATION.md`
- `docs/ABILITY_MODULE_SYSTEM.md`
- `docs/PROTOTYPE_PLANS.md`

### CHECKPOINTS.md

Időrendi technikai checkpoint-napló.

Tartalmazza:

- mi készült el;
- milyen smoke testek futottak;
- milyen korlátok maradtak;
- mi a következő biztonságos lépés.

Ez a fájl a technikai állapot elsődleges rövid forrása.

### OPEN_QUESTIONS.md

A nyitott kérdések és döntési kapuk központi listája.

Tartalmazza:

- architektúra-kérdéseket;
- runtime package kérdéseket;
- snapshot / legal action / event log / diagnostics kérdéseket;
- ability module kérdéseket;
- AI / balance kérdéseket;
- szabály- és kártyaaudit időzítési kérdéseket.

### DECISION_MAP.md

A projektirány és döntési térkép rövid összefoglalója.

Tartalmazza:

- elfogadott irányokat;
- munkahipotéziseket;
- mit nem csinálunk most;
- ChatGPT / Codex / emberi döntés munkamegosztást;
- dokumentációs rendet;
- következő lépéseket.

### ARCHITECTURE.md

A technikai célarchitektúra fő térképe.

Tartalmazza:

- fő rétegeket;
- adatútvonalat;
- runtime package szerepét;
- contract-réteget;
- rules engine és ability engine helyét;
- Godot és Python rétegét;
- Aeternal / Pecsét engine-modell alapját.

### TECHNOLOGY_DECISIONS.md

A Python / GDScript / hibrid technológiai döntési tér.

Tartalmazza:

- Python lehetséges szerepeit;
- Godot / GDScript lehetséges szerepeit;
- hibrid modelleket;
- döntési kapukat;
- prototípusigényeket.

### CONTRACT_SPECIFICATION.md

A contract-first adatcsere fő specifikációs váza.

Tartalmazza:

- snapshot contract;
- legal actions contract;
- action request / response;
- event log;
- diagnostics;
- sample contracts;
- contract consistency irányokat.

### RUNTIME_PACKAGE_SPECIFICATION.md

A runtime package adatcsomag specifikációs váza.

Tartalmazza:

- Google Sheets → XLSX → exportáló → package adatútvonalat;
- manifestet;
- cards / decks / lookups / aliases / ability registry / engine support / diagnostics fájlokat;
- validációs szinteket;
- sample és full package elválasztását.

### ABILITY_MODULE_SYSTEM.md

Az ability / effect module rendszer tervezési váza.

Tartalmazza:

- structured ability irányt;
- trigger / condition / cost / target / effect modulokat;
- keyword rendszer kérdéseit;
- execution plan kérdéseit;
- card-local fallback szabályait;
- Pecsét / Aeternal effect modell korlátait.

### PROTOTYPE_PLANS.md

A prototípusok és következő technikai lépések munkaterve.

Tartalmazza:

- már elkészült prototípusokat;
- következő prototípusjelölteket;
- mit bizonyítanak;
- mit nem bizonyítanak;
- smoke test elvárásokat;
- Codex-kompatibilis feladattípusokat.

---

## Runtime package

A runtime package a program által fogyasztható, validált adatcsomag.

Nem azonos:

- a Google Sheets forrással;
- a lokális XLSX fájlokkal;
- a nyers exportokkal;
- a hivatalos szabályforrásokkal.

Jelenlegi sample runtime package fájlok:

- `manifest.json`
- `cards.jsonl`
- `decks.jsonl`
- `lookups.json`
- `aliases.json`
- `ability_registry.json`
- `engine_support.json`
- `diagnostics.json`
- `build_report.md`

A Godot által fogyasztott sample package jelenlegi helye:

- `Godot/sample_runtime_package/`

A Godot loader útvonala:

- `res://sample_runtime_package`

---

## Godot projekt

A Godot projekt helye:

- `Godot/`

A Godot oldal jelenlegi szerepe:

- runtime package betöltés;
- sample contractok betöltése;
- registry-k kezelése;
- debug nézetek;
- headless smoke testek;
- későbbi játékos UI alapja.

A Godot oldal nem végleges szabálymotor.

A debug nézetek nem végleges játék UI-elemek.

---

## Python oldal

A Python oldal jelenlegi szerepe:

- sample runtime package generálás;
- unit teszt;
- későbbi exportvalidáció;
- későbbi full runtime package builder;
- diagnostics és build report;
- későbbi AI-vs-AI / batch tesztelés lehetősége.

A Python oldal jelenleg nem végleges backend-döntés.

A régi Python motor nem kerül automatikusan beolvasztásra az új Aeterna game engine-be.

---

## Headless smoke testek

A Godot headless smoke testeknél Windows / Godot környezetben explicit logfájl használata ajánlott.

A smoke log fájlok generált melléktermékek.

Nem kell őket aktív dokumentációnak tekinteni.

A checkpointokban csak a fontos eredményt kell rögzíteni:

- melyik smoke test futott;
- sikeres volt-e;
- volt-e blokkoló hiba;
- milyen ismert nem blokkoló warning jelent meg.

---

## Aeternal / Pecsét engine-modell

A jelenlegi rögzített szabályi irány:

- Az Aeternal maga a játékos.
- Az Aeternal nem rendelkezik HP-val.
- Az Aeternal nem kaphat sebzést.
- Az Aeternal nem gyógyítható.
- A Pecsét nem HP-alapú objektum.
- A Pecsét feltörési / visszaállítási eseményként kezelendő.
- Ha nincs Entitás és Pecsét, ami véd, egy célba érő támadás azonnali vereséget jelent.

Kerülendő régi runtime fogalmak:

- `player_damage`
- `aeternal_damage`
- `heal_player`
- `heal_aeternal`
- `ward_hp`
- `seal_hp`
- `seal_damage`
- `ward_damage`

Támogatandó modern fogalmak:

- `ward_break`
- `ward_restore`
- `ward_break_prevent`
- `aeternal_unprotected`
- `direct_attack_victory`
- `player_defeated`

---

## Fejlesztési alapelv

A fejlesztés kis, ellenőrizhető lépésekben történjen.

Egy jó technikai lépés:

- kicsi;
- jól tesztelhető;
- nem kever szabályi döntést technikai implementációval;
- nem mozgat vagy töröl fájlokat előzetes döntés nélkül;
- nem írja felül a hivatalos szabályforrásokat;
- nem tesz végleges technológiai ítéletet prototípus nélkül.

---

## Codex szerepe

Codex használható célzott technikai feladatokra.

Codexnek adható:

- konkrét loader módosítás;
- konkrét smoke test;
- konkrét debug view;
- card reference resolver;
- missing reference diagnostics;
- sample JSON bővítés;
- Python unit test;
- GDScript smoke test;
- manifest ellenőrzés.

Codexnek ne adjunk:

- teljes projektirányítást;
- szabályi döntést;
- balanszdöntést;
- nagy homályos refaktort;
- automatikus törlést;
- mappák tömeges mozgatását;
- végleges dokumentációs döntést;
- hivatalos szabályforrás átírását emberi döntés nélkül.

---

## Következő ajánlott technikai lépés

A jelenlegi dokumentációs irány alapján a következő biztonságos technikai fejlesztési lépés:

**Runtime package + sample contracts integration**

Cél:

- snapshot / legal actions / event log card_id hivatkozásai oldódjanak fel a runtime package card registryből;
- debug nézetekben jelenjen meg a card name, card type, realm és clan;
- missing card reference diagnostics keletkezzen;
- minden korábbi smoke test maradjon zöld;
- készüljön új integration smoke test.

Ez még nem rules engine.

Ez még nem action-végrehajtás.

Ez még nem AI.

---

## Mit ne csináljunk most?

Most nem cél:

- teljes rules engine;
- teljes digitális kliens;
- teljes ability execution;
- AI-vs-AI balanszteszt;
- PvP;
- régi Python motor beolvasztása;
- mappák tömeges mozgatása;
- DOCX-ek törlése;
- új teljes kártyaaudit;
- hivatalos szabályforrások átírása.

---

## Rövid munkasorrend

Javasolt sorrend:

1. Dokumentációs főfájlok ellenőrzése.
2. Nyitott kérdések státuszolása.
3. Checkpointok és README összhangjának ellenőrzése.
4. Runtime package + sample contracts integration technikai feladat előkészítése.
5. Codexnek célzott technikai prompt adása.
6. Smoke testek futtatása.
7. Sikeres eredmény esetén CHECKPOINTS.md frissítése.

---

## Státusz

Ez a README az Aeterna game engine belépő dokumentuma.

A részletek nem itt, hanem a kapcsolódó fő dokumentumokban találhatók.

A README célja:

- gyors eligazítás;
- fő irányok megmutatása;
- dokumentumok közötti navigáció;
- jelenlegi óvatos projektállapot rögzítése.