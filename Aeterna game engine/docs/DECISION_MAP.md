# AETERNA Game Engine – Decision Map

Ez a fájl az AETERNA Game Engine fejlesztési irányainak, döntési kapuinak és munkarendi szabályainak központi összefoglalója.

Nem teljes architektúra-specifikáció.

Nem contract-specifikáció.

Nem checkpoint-napló.

Nem open questions lista.

Feladata, hogy röviden rögzítse:

- mi az elfogadott irány;
- mi csak munkahipotézis;
- mihez kell még prototípus vagy audit;
- mit nem szabad most összekeverni;
- milyen sorrendben érdemes továbbhaladni;
- milyen szerepet kap ChatGPT, Codex és az emberi döntés.

Kapcsolódó főfájlok:

CHECKPOINTS.md
OPEN_QUESTIONS.md
ARCHITECTURE.md
TECHNOLOGY_DECISIONS.md
CONTRACT_SPECIFICATION.md
RUNTIME_PACKAGE_SPECIFICATION.md
ABILITY_MODULE_SYSTEM.md
PROTOTYPE_PLANS.md

---

## 1. Projektcél

Az AETERNA Game Engine célja egy contract-first digitális programegység kialakítása az AETERNA kártyajátékhoz.

A digitális rendszer hosszú távú céljai:

* kártyaadatok programbiztos feldolgozása;
* exportvalidáció;
* runtime package előállítása;
* Godot/GDScript oldali betöltés;
* snapshot / legal action / event log / diagnostics contractok;
* későbbi szabálymotor;
* későbbi AI-vs-AI tesztelés;
* későbbi játékos-vs-AI és játékos-vs-játékos digitális kliens;
* hosszabb távon balanszteszt és fejlesztői debug környezet.

A jelenlegi cél nem a teljes digitális játék azonnali elkészítése.

A jelenlegi cél a stabil adatút, contract-réteg, dokumentációs rend és prototípus-alap megőrzése és fokozatos erősítése.

---

## 2. Fizikai TCG elsődlegessége

Elfogadott irány:

Az AETERNA elsődlegesen fizikai TCG.

A digitális engine nem helyettesíti a fizikai játéktervet.

A digitális engine szerepe:

* tesztelés;
* audit;
* adatvalidáció;
* balanszvizsgálat;
* szabálymodellezés;
* későbbi digitális játszhatóság;
* fejlesztői és AI segédrendszer.

A digitális rendszer nem írhatja felül a hivatalos szabályforrásokat emberi döntés nélkül.

---

## 3. Aktív hivatalos szabályforrások

Jelenlegi hivatalos aktív szabályforrások:

AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx
AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx

Ezek jelenleg maradhatnak DOCX formában.

Az engine dokumentáció átállhat Markdownra, de a hivatalos szabályfőforrások külön döntésig nem kerülnek automatikusan MD-re.

Későbbi lehetséges irányok:

* játékosbarát szabálykönyv;
* engine-barát szabályspecifikáció;
* Codex/AI-barát rövid szabályspecifikáció;
* párhuzamos MD-alapú szabálymodell.

Ezek külön döntési kapuk.

---

## 4. Új digitális programegység

Elfogadott irány:

Az Aeterna game engine önálló programegység.

Nem a régi Python program közvetlen folytatása.

Javasolt fő szerkezet:

Aeterna game engine/
  python/
  Godot/
  docs/
  README.md

A `python/` ág szerepe:

* runtime package generálás;
* exportvalidáció;
* package builder;
* tesztek;
* későbbi AI-vs-AI / batch tesztelési lehetőség;
* adatfeldolgozás;
* riportok.

A `Godot/` ág szerepe:

* Godot projekt;
* GDScript contract-loader;
* debug view-k;
* későbbi UI;
* későbbi játszható kliens;
* esetleges későbbi GDScript runtime.

---

## 5. Régi Python motor státusza

Elfogadott irány:

A régi Python motor működő referencia és archív előzmény.

Nem törlendő automatikusan.

Nem aktív új fejlesztési főág.

Nem szabad vakon átemelni az új engine-be.

Későbbi felhasználási lehetőségei:

* szabálylogikai referencia;
* AI-vs-AI előzmény;
* loader/export tanulságok;
* validációs ötletek;
* tesztelési tapasztalatok.

Áthozás csak akkor történhet, ha:

* pontosan tudjuk, mire szolgál;
* illeszkedik a contract-first rendszerbe;
* nem húzza vissza az új engine-t a régi architektúrába;
* teszttel vagy smoke testtel ellenőrizhető;
* külön munkalépésben történik.

---

## 6. Contract-first alapelv

Elfogadott irány:

Előbb contract, utána implementáció.

A szabálymotor, frontend, AI, debug UI és tesztrendszer ne egymás belső objektumaira épüljön, hanem explicit contractokra.

Fő contract-rétegek:

runtime package
snapshot
legal actions
action request
action response
event log
diagnostics
ability registry
engine support report

A frontend ne találgasson szabályokat.

Az AI ne találgasson szabályokat.

A szabályos lépéseket a rules engine / legal action contract adja vissza.

---

## 7. Jelenlegi bizonyított technikai állapot

A CHECKPOINTS.md alapján jelenleg bizonyított:

Python sample runtime package generator működik.
Python unit test zöld.
sample_runtime_package generálás működik.
Godot runtime package loader működik.
Godot package loader smoke test zöld.
sample contracts loader működik.
sample contracts smoke test zöld.
Snapshot viewer debug nézet működik.
Legal action debug panel működik.
Event log debug view működik.
A kapcsolódó smoke testek zöldek.

Ez még nem bizonyítja:

teljes szabálymotor
valódi legal action számítás
action-végrehajtás
kártyaképesség-futtatás
AI döntéshozatal
teljes játék UI
event playback
PvP
teljes AETERNA adatbázis futtatása

---

## 8. Runtime package irány

Elfogadott irány:

A runtime package legyen a Python és Godot közötti közös adatcsomag.

A runtime package nem azonos az XLSX szerkesztési forrással.

A runtime package nem egyszerű nyers export.

A runtime package a programfogyasztásra előkészített, validált adatcsomag.

Jelenlegi működő sample package fájlcsoport:

manifest.json
cards.jsonl
decks.jsonl
lookups.json
aliases.json
ability_registry.json
engine_support.json
diagnostics.json
build_report.md

Nyitott kérdések:

* Mikortól legyen kötelező a compiled runtime package?
* Meddig maradhat közvetlen raw export betöltés?
* Egyfájlos vagy többfájlos package legyen hosszú távon?
* A package tartalmazzon-e előre generált execution plant?
* A runtime package legyen-e minden motor kötelező közös inputja?

Részletes kérdések:

OPEN_QUESTIONS.md / Runtime package és adatút

---

## 9. Google Sheets → XLSX → exportáló → package adatút

Elfogadott irány:

A fő szerkesztés Google Sheetsben történik.

A Google Sheetsből letöltött lokális XLSX a helyi forrásmásolat.

Az `XLSX export/` mappán belüli `.xlsx` fájlok pipeline input másolatok, nem elsődleges szerkesztési források.

Az exportáló program hosszú távon kaphat olyan input-módot, hogy közvetlenül a canonical lokális forrásmappából dolgozzon.

Jelenlegi adatút:

Google Sheets
  ↓
lokális XLSX
  ↓
exportáló program
  ↓
nyers exportok / JSONL
  ↓
runtime package
  ↓
Python / Godot fogyasztás

Nyitott kérdések:

* pontos canonical lokális XLSX hely;
* `XLSX export/source/` hosszú távú szerepe;
* generated outputok státusza;
* direct-source exportmód implementálása.

---

## 10. GDScript / Python technológiai munkahipotézis

Jelenlegi munkahipotézis:

Python erős adatpipeline, validáció, package build, AI-vs-AI és riport oldalon.
Godot/GDScript erős vizuális kliens, debug UI, játékos felület és későbbi runtime oldalon.

Nem eldöntött véglegesen:

* Python marad-e hosszú távú backend;
* GDScript lesz-e a fő rules runtime;
* hibrid modell marad-e;
* kell-e két motor összehasonlító tesztelése;
* melyik rendszer lesz referencia, ha eltérés van.

Biztonságos jelenlegi irány:

Contract-first + runtime package közös határ.

Ez akkor is hasznos, ha később Python, GDScript vagy hibrid irány lesz a végleges.

---

## 11. Godot / GDScript jelenlegi szerepe

Bizonyított:

Godot képes runtime package-et betölteni.
Godot képes sample contractokat betölteni.
Godot képes snapshot / legal action / event log debug nézeteket futtatni.
Godot headless smoke testek működnek explicit logfájllal.

Nem bizonyított:

Godot teljes szabálymotorként működik.
Godot AI-vs-AI batch tesztre alkalmas.
Godot hosszú távon kényelmes teljes rules engine lesz.

Nyitott döntési kapu:

GDScript runtime alkalmassága.

---

## 12. AI / simulation / balance irány

Jelenlegi irány:

AI-vs-AI és balance tesztelés későbbi fázis.

Nem most következő fő feladat.

Előfeltételek:

* stabil adatút;
* runtime package;
* legal action contract;
* action request / response modell;
* event log;
* diagnostics;
* legalább részleges ability support;
* fair snapshot / visibility modell.

Balanszfilozófiai munkahipotézis:

A cél nem steril 50/50 balansz.
A klánidentitás fontos.
A 40–60 winrate-sáv csak kezdeti figyelési elv, nem végleges matematikai szabály.

A korábbi kártyajavításokat később vissza kell ellenőrizni, hogy:

* nem lettek-e túlgyengítve;
* megmaradt-e az egyediségük;
* megmaradt-e a klánidentitásuk;
* működnek-e játék közben.

---

## 13. Kártyaaudit időzítése

Elfogadott irány:

Most nem indul új teljes kártyaaudit.

Előbb stabilizálandó:

* adatút;
* LOOKUPS;
* structured mezők;
* runtime package;
* diagnostics;
* engine support report;
* legal action / event log alapok.

Új kártyaaudit később indulhat:

* birodalmonként;
* klánonként;
* hibakategóriánként;
* engine support alapján;
* balanszteszt után;
* vagy korábbi javított lapok visszaellenőrzéseként.

---

## 14. Aeternal / Pecsét rögzített irány

Elfogadott szabálymodell:

Az Aeternal maga a játékos.
Az Aeternal nem rendelkezik HP-val.
Az Aeternal nem kaphat sebzést.
Az Aeternal nem gyógyítható.
A Pecsét nem HP-alapú objektum.
A Pecsét feltörési / visszaállítási eseményként kezelendő.
Ha nincs Entitás és Pecsét, ami véd, egy célba érő támadás azonnali vereséget jelent.

Engine-dokumentációs következmény:

* ne legyen `player_damage`;
* ne legyen `aeternal_damage`;
* ne legyen `heal_aeternal`;
* ne legyen `ward_hp`;
* ne legyen `seal_damage`;
* legyen `ward_break`;
* legyen `ward_restore`;
* legyen `ward_break_prevent`.

Nyitott kérdések:

OPEN_QUESTIONS.md / Rules audit and card audit timing / OQ-RULES-007
OPEN_QUESTIONS.md / Ability module system / OQ-ABIL-006

---

## 15. Dokumentációs rend

Elfogadott irány:

Az engine dokumentáció hosszú távon Markdown alapú legyen.

Cél:

* kevesebb DOCX;
* kevesebb duplikált részverzió;
* könnyebb Git diff;
* könnyebb AI/Codex feldolgozás;
* könnyebb merge;
* könnyebb karbantartás.

Az aktív engine dokumentáció főfájljai:

README.md
CHECKPOINTS.md
OPEN_QUESTIONS.md
DECISION_MAP.md
ARCHITECTURE.md
TECHNOLOGY_DECISIONS.md
CONTRACT_SPECIFICATION.md
RUNTIME_PACKAGE_SPECIFICATION.md
ABILITY_MODULE_SYSTEM.md
PROTOTYPE_PLANS.md

Új dokumentum csak akkor készüljön, ha:

* új fő témakört fed le;
* nem illeszthető meglévő fődokumentumba;
* nem csak átmeneti munkaterv;
* nem duplikál már létező tartalmat.

Átmeneti munkatervek a merge után törölhetők vagy archiválhatók.

---

## 16. Checkpoint dokumentációs szabály

Elfogadott irány:

A checkpointok egyetlen CHECKPOINTS.md fájlban gyűljenek.

A checkpoint legyen:

* időrendi;
* rövid;
* tényszerű;
* teszteredményekre épülő;
* ismert korlátokat tartalmazó;
* következő lépést jelölő.

A checkpoint ne legyen:

* teljes architektúra;
* részletes specifikáció;
* prototípusterv;
* dokumentumkezelési terv.

---

## 17. Open questions szabály

Elfogadott irány:

A nyitott kérdések nem veszhetnek el a merge során.

Minden nyitott kérdés kerüljön:

OPEN_QUESTIONS.md

vagy az adott fődokumentum saját „Nyitott kérdések” szakaszába.

A központi `OPEN_QUESTIONS.md` feladata:

* kérdések indexelése;
* státuszolás;
* célfájl jelölése;
* döntési kapuk megőrzése;
* későbbi válaszok átvezetése.

---

## 18. ChatGPT / Codex / emberi döntés munkamegosztás

Elfogadott irány:

Komplex projektvizsgálat, dokumentációs szerkezet, döntési térkép és munkarend: ChatGPT + emberi döntés.
Célzott technikai implementáció: Codex.
Szabályi, balansz és projektirányú végső döntés: emberi döntés.

Codex kapjon:

* rövid;
* célzott;
* konkrét;
* ellenőrizhető;
* technikai promptokat.

Codex ne kapjon:

* teljes projektirányítást;
* homályos refaktort;
* nagy dokumentációs döntést;
* szabályi/balanszdöntést;
* automatikus törlési/mappamozgatási feladatot részletes lista nélkül.

---

## 19. Mit nem csinálunk most?

Most nem cél:

teljes szabálymotor
teljes digitális kliens
AI-vs-AI balanszteszt
új teljes kártyaaudit
főforrás teljes újraírása
régi Python motor automatikus átemelése
mappák tömeges mozgatása
DOCX-ek törlése
újabb párhuzamos dokumentumverziók gyártása

Mostani helyes fókusz:

dokumentáció konszolidáció
open questions megőrzés
runtime package és contract specifikáció tisztítása
Godot/Python prototípus biztonságos erősítése

---

## 20. Következő javasolt dokumentációs lépés

A jelenlegi sorrend:

CHECKPOINTS.md – elkészült
OPEN_QUESTIONS.md – összevonva / javítandó
DECISION_MAP.md – ez a fájl
ARCHITECTURE.md – következő nagy fődokumentum
TECHNOLOGY_DECISIONS.md
CONTRACT_SPECIFICATION.md
RUNTIME_PACKAGE_SPECIFICATION.md
ABILITY_MODULE_SYSTEM.md
PROTOTYPE_PLANS.md
README.md frissítés

A README csak akkor frissüljön véglegesen, ha a fő dokumentációs térkép már stabil.

