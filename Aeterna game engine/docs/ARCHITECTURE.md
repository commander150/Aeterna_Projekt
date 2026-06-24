# AETERNA Game Engine – Architecture

Ez a dokumentum az AETERNA Game Engine célarchitektúrájának fő technikai vázát rögzíti.

Nem teljes contract-specifikáció.

Nem runtime package részletes schema.

Nem ability module specifikáció.

Nem checkpoint-napló.

Feladata, hogy összefogja az engine fő rétegeit, azok kapcsolatát, felelősségi határait és a jelenlegi contract-first fejlesztési irányt.

Kapcsolódó fő dokumentumok:

DECISION_MAP.md
CHECKPOINTS.md
OPEN_QUESTIONS.md
TECHNOLOGY_DECISIONS.md
CONTRACT_SPECIFICATION.md
RUNTIME_PACKAGE_SPECIFICATION.md
ABILITY_MODULE_SYSTEM.md
PROTOTYPE_PLANS.md

---

## 1. Alapelv

Az AETERNA Game Engine architektúrájának alapelve:

előbb contract, utána implementáció

A rendszer ne egy konkrét programnyelv, motor vagy frontend belső objektumaira épüljön.

A fő komponensek közötti kapcsolatokat explicit adatcontractok írják le.

Ez azért fontos, mert az AETERNA digitális rendszere több rétegből állhat:

* Python adatpipeline;
* Python validáció;
* Python sample package builder;
* Godot/GDScript loader;
* Godot debug nézetek;
* későbbi rules engine;
* későbbi AI / simulation;
* későbbi játszható digitális kliens.

A contract-first határ biztosítja, hogy ezek a rétegek ne keveredjenek össze.

---

## 2. Magas szintű rendszerkép

A hosszú távú architektúra fő adat- és működési lánca:

Fizikai TCG szabály- és kártyaforrások
        ↓
Google Sheets / lokális XLSX szerkesztési források
        ↓
Exportáló / validációs pipeline
        ↓
Runtime package
        ↓
Rules engine / simulation / Godot loader
        ↓
Snapshot / legal actions / action request / event log / diagnostics
        ↓
Godot debug UI / későbbi játék UI / AI tesztek

A rendszer célja nem az, hogy egyetlen nagy, összefolyó program legyen.

A cél egy rétegezett, ellenőrizhető rendszer, ahol minden rétegnek világos feladata van.

---

## 3. Fizikai TCG réteg

Az AETERNA elsődlegesen fizikai TCG.

A digitális engine a fizikai játékot támogatja, modellezi és teszteli, de nem írja felül emberi döntés nélkül.

A fizikai TCG réteghez tartozik:

* hivatalos szabályforrás;
* kártyaadatbázis;
* LOOKUPS;
* kártyaszövegek;
* paklik;
* balansz- és auditdöntések;
* játékosbarát szabálymagyarázatok.

A digitális engine-nek tiszteletben kell tartania a hivatalos szabálymodellt.

---

## 4. Szerkesztési forrásréteg

A jelenlegi elfogadott adatkezelési irány:

Google Sheets = elsődleges szerkesztési felület
lokális XLSX = letöltött helyi forrásmásolat
XLSX export/source = pipeline input másolat, nem canonical szerkesztési forrás

A szerkesztési forrásréteg nem azonos a runtime package-dzsel.

A szerkesztési forrás célja:

* emberi szerkeszthetőség;
* kártyaadatok karbantartása;
* LOOKUPS kezelése;
* audit- és workflow mezők kezelése;
* későbbi export előkészítése.

A runtime engine közvetlenül hosszú távon ne a szerkesztési XLSX-ből dolgozzon.

---

## 5. Export és validációs réteg

Az export és validációs réteg feladata:

* a szerkesztési források beolvasása;
* nyers exportok előállítása;
* LOOKUPS ellenőrzése;
* canonical értékek kezelése;
* legacy aliasok felismerése;
* structured mezők ellenőrzése;
* veszélyes vagy régi modellből származó értékek jelzése;
* engine support státusz előkészítése;
* diagnostics reportok készítése.

Ez a réteg választja el az emberi szerkesztési formát a programbiztos futási adattól.

---

## 6. Runtime package réteg

A runtime package az engine által fogyasztható programbiztos adatcsomag.

Nem azonos:

* az XLSX szerkesztési forrással;
* a nyers exporttal;
* a dokumentációval;
* a szabálykönyvvel.

A jelenlegi sample runtime package fájlcsoport:

manifest.json
cards.jsonl
decks.jsonl
lookups.json
aliases.json
ability_registry.json
engine_support.json
diagnostics.json
build_report.md

A runtime package célja:

* kártyaadatok egységes átadása;
* paklik átadása;
* lookup és alias adatok átadása;
* ability registry átadása;
* engine support információ átadása;
* diagnostics átadása;
* Python és Godot közös adatforrása.

Hosszú távú cél:

a runtime package legyen a Python és Godot közötti közös, stabil adatcontract

---

## 7. Contract-réteg

A contract-réteg írja le, hogyan kommunikálnak a fő rendszerrészek.

Fő contractok:

runtime package
snapshot
legal actions
action request
action response
event log
diagnostics
ability registry
engine support report

A contract-réteg célja:

* a frontend ne találgasson szabályokat;
* az AI ne találgasson szabályokat;
* a rules engine adja meg a szabályos actionöket;
* az action request validálható legyen;
* az event logból érthető legyen, mi történt;
* a diagnostics strukturáltan jelezze a problémákat;
* a rejtett információ ne szivárogjon ki player-visible nézetben.

A contractok részletes leírása külön fájlba tartozik:

CONTRACT_SPECIFICATION.md

---

## 8. Core rules engine réteg

A core rules engine hosszú távú feladata:

* fázisok kezelése;
* körszerkezet kezelése;
* prioritás / döntési ablak kezelése;
* legal actionök kiszámítása;
* action request validálása;
* action végrehajtása;
* alap harci szabályok kezelése;
* Pecsét / Aeternal szabálymodell kezelése;
* győzelmi és vereségi feltételek kezelése;
* event log generálása;
* diagnostics generálása.

A core rules engine jelenleg még nem készült el.

A jelenlegi prototípusok csak adatbetöltést, sample contract kezelést és debug nézeteket bizonyítanak.

---

## 9. Ability / effect engine réteg

Az ability / effect engine hosszú távú feladata:

* structured abilityk értelmezése;
* trigger modulok kezelése;
* condition modulok kezelése;
* target selector modulok kezelése;
* cost modulok kezelése;
* effect modulok futtatása;
* duration és limit kezelése;
* replacement és prevention kezelése;
* keywordök engine supportja;
* card-local fallback kontrollált kezelése;
* event log és diagnostics előállítása.

Az ability / effect engine részletes terve külön fájlba tartozik:

ABILITY_MODULE_SYSTEM.md

Fontos alapelv:

A kártyaszöveg nem közvetlen runtime parser-forrás.
A structured ability / ability registry a programlogikai köztes réteg.

---

## 10. Match state réteg

A match state a játék belső igaz állapota.

Ez nem azonos a snapshot contracttal.

A match state tartalmazhat teljes, belső, nem player-visible információt is.

Hosszú távon a match state-ből származhatnak:

* player-visible snapshotok;
* debug snapshotok;
* AI snapshotok;
* spectator snapshotok;
* replay snapshotok;
* legal action listák;
* event log frissítések.

A match state belső szerkezetét nem szabad közvetlenül a Godot UI-ra kötni.

A Godot UI snapshotot és legal action contractot fogyasszon, ne belső engine állapotot.

---

## 11. Snapshot réteg

A snapshot a match state nézőpontfüggő kivetítése.

Lehetséges snapshot típusok:

debug_snapshot
player_visible_snapshot
spectator_snapshot
ai_fair_snapshot
ai_debug_snapshot

A snapshot célja:

* UI megjelenítés;
* AI döntés-előkészítés;
* debug nézet;
* tesztelés;
* későbbi replay támogatás.

Fontos szabály:

player-visible snapshot nem szivárogtathat rejtett információt

A snapshot részletes kérdései az `OPEN_QUESTIONS.md` fájlban vannak.

---

## 12. Legal action réteg

A legal action réteg mondja meg, hogy egy adott pillanatban milyen döntéseket hozhat a játékos vagy AI.

Alapelv:

A frontend és az AI nem találgat szabályos lépéseket.
A legal action listát a rules engine adja vissza.

A legal action tartalmazhat:

* action azonosítót;
* action típust;
* forráskártyát;
* target információkat;
* cost summaryt;
* enabled / disabled állapotot;
* disabled reason mezőt;
* UI/debug segédadatokat;
* diagnostics blokkot;
* AI számára később opcionális segédadatokat.

A legal action részletes szerkezete a `CONTRACT_SPECIFICATION.md` fájlba tartozik.

---

## 13. Action request / response réteg

Az action request a frontend vagy AI által küldött döntési kérés.

Alapelv:

A kliens nem módosít állapotot.
A kliens action requestet küld.
A rules engine validál és válaszol.

Az action request / response réteg feladata:

* request azonosítás;
* snapshot frissesség ellenőrzése;
* action_id ellenőrzése;
* targetek ellenőrzése;
* payment ellenőrzése;
* validáció;
* végrehajtás vagy elutasítás;
* eventek generálása;
* új snapshot visszaadása;
* diagnostics visszaadása.

Ez a réteg különösen fontos későbbi interaktív UI, AI és PvP esetén.

---

## 14. Event log réteg

Az event log a játék történeti rétege.

Alapelv:

A snapshot az állapot.
Az event log a történet.

Az event log célja:

* frontend animáció;
* játékosbarát magyarázat;
* debug;
* AI elemzés;
* replay előkészítés;
* audit;
* balanszvizsgálat;
* diagnostics kapcsolat.

Lehetséges event layer-ek:

gameplay
frontend
explanation
debug
audit
balance
system

Az event log nem szivárogtathat rejtett információt player-visible nézetben.

---

## 15. Diagnostics réteg

A diagnostics réteg strukturált problémanyilvántartás.

Nem egyszerű hibalista.

Lehetséges diagnostics kategóriák:

export_validation
lookup
legacy_alias
structured
engine
rules
card_data
decklist
runtime
frontend_contract
ai
event_log
snapshot
action_validation
action_execution
hidden_information
audit
balance
test
system

Lehetséges severity értékek:

critical
error
warning
audit_note
balance_suspicion
info
debug

Fontos alapelv:

severity és blocking külön mező legyen

Egy warning általában nem blokkoló.

Egy error lehet blokkoló vagy nem blokkoló, a `blocking` mezőtől függően.

A diagnostics részletes szabályai a `CONTRACT_SPECIFICATION.md` és `RUNTIME_PACKAGE_SPECIFICATION.md` fájlokba tartoznak.

---

## 16. Godot frontend / debug adapter réteg

A Godot jelenlegi bizonyított szerepe:

* runtime package betöltése;
* sample contractok betöltése;
* snapshot viewer debug nézet;
* legal action debug panel;
* event log debug view;
* headless smoke testek futtatása.

Godot hosszú távú lehetséges szerepei:

* debug UI;
* fejlesztői viewer;
* játékos UI;
* digitális kliens;
* esetleges GDScript runtime;
* későbbi játékos-vs-AI és játékos-vs-játékos felület.

Fontos elhatárolás:

A debug nézet nem szabálymotor.
A UI ne találgasson szabályokat.
A Godot node-ok ne váljanak rejtett szabálylogikává.

---

## 17. Python réteg

A Python jelenlegi és lehetséges szerepei:

* sample runtime package generator;
* exportvalidáció;
* runtime package build;
* diagnostics report;
* adatfeldolgozás;
* AI-vs-AI batch tesztelés;
* statisztika;
* régi motor referenciaelemzése;
* összehasonlító tesztek.

Nyitott kérdés:

Python marad-e hosszú távon szabálymotor / backend, vagy inkább data pipeline és tesztréteg lesz?

Ezt a `TECHNOLOGY_DECISIONS.md` dokumentumban kell részletesen kezelni.

---

## 18. AI / simulation / balance réteg

Az AI / simulation / balance réteg későbbi fejlesztési fázis.

Előfeltételek:

* stabil runtime package;
* legal action contract;
* action request / response modell;
* event log;
* diagnostics;
* ability support;
* fair snapshot visibility modell.

Lehetséges jövőbeli funkciók:

* AI-vs-AI futtatás;
* AI-vs-játékos mód;
* balance report;
* winrate elemzés;
* card usage statisztika;
* matchup elemzés;
* korábbi kártyajavítások visszaellenőrzése.

Balanszfilozófiai munkahipotézis:

A cél nem steril 50/50 balansz.
A klánidentitás fontos.
A 40–60 winrate-sáv csak figyelési elv, nem végleges matematikai szabály.

---

## 19. Aeternal / Pecsét engine modell

Rögzített irány:

Az Aeternal maga a játékos.
Az Aeternal nem rendelkezik HP-val.
Az Aeternal nem kaphat sebzést.
Az Aeternal nem gyógyítható.
A Pecsét nem HP-alapú objektum.
A Pecsét feltörési / visszaállítási eseményként kezelendő.
Ha nincs Entitás és Pecsét, ami véd, egy célba érő támadás azonnali vereséget jelent.

Tiltandó vagy kerülendő régi engine-fogalmak:

player_damage
aeternal_damage
heal_player
heal_aeternal
ward_hp
seal_damage

Támogatandó modern fogalmak:

ward_break
ward_restore
ward_break_prevent
aeternal_unprotected
direct_attack_victory

A részletes kérdések az `OPEN_QUESTIONS.md` fájlban szerepelnek.

---

## 20. Jelenlegi bizonyított állapot

A CHECKPOINTS.md alapján jelenleg bizonyított:

Python sample runtime package generator működik.
Python unit test zöld.
sample_runtime_package generálás működik.
Godot runtime package loader működik.
Godot package loader smoke test zöld.
Godot sample contracts loader működik.
Godot sample contracts smoke test zöld.
Snapshot viewer debug nézet működik.
Legal action debug panel működik.
Event log debug view működik.
Kapcsolódó smoke testek zöldek.

Ez még nem bizonyítja:

teljes szabálymotor
valódi match state generálás
legal action számítás szabályból
action-végrehajtás
kártyaképesség-futtatás
AI döntéshozatal
teljes játék UI
PvP
teljes AETERNA adatbázis futtatása

---

## 21. Nyitott architektúra-kérdések

A részletes nyitott kérdések központi helye:

OPEN_QUESTIONS.md

Kiemelt architektúra-kérdések:

* régi Python motor sorsa;
* GDScript runtime alkalmassága;
* Python + GDScript hibrid modell;
* runtime package kötelező szerepe;
* match state és snapshot elválasztása;
* reaction queue / stack modell;
* fair AI és debug AI elválasztása;
* diagnostics blocking szabályok;
* ability execution plan helye;
* card-local fallback kezelése;
* Pecsét / Aeternal végleges engine modellje.

---

## 22. Nem cél most

Most nem cél:

teljes szabálymotor implementálása
teljes digitális kliens megírása
AI-vs-AI balanszteszt
új teljes kártyaaudit
PvP
booster / collection / economy rendszer
régi Python motor automatikus beolvasztása
nagy mappamozgatás
DOCX fájlok törlése

A jelenlegi fókusz:

dokumentációs konszolidáció
runtime package specifikáció tisztítása
contract-specifikáció egységesítése
Godot/Python prototípus fokozatos erősítése
open questions megőrzése és státuszolása

---

## 23. Következő kapcsolódó dokumentumok

Az architektúra után a következő fő dokumentumok részletezik a rétegeket:

TECHNOLOGY_DECISIONS.md
CONTRACT_SPECIFICATION.md
RUNTIME_PACKAGE_SPECIFICATION.md
ABILITY_MODULE_SYSTEM.md
PROTOTYPE_PLANS.md
README.md

A README csak akkor frissüljön véglegesen, amikor a fő dokumentációs térkép stabil.
