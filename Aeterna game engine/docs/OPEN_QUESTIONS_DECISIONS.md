# AETERNA Game Engine – Open Questions Decisions

Ez a fájl az `OPEN_QUESTIONS.md` kérdéseire adott válaszok és döntési irányok külön nyilvántartása.

## Szerep

Az `OPEN_QUESTIONS.md` továbbra is a központi kérdésindex marad.

Ez a fájl nem helyettesíti és nem törli a kérdéseket. Feladata az, hogy a már megválaszolt, részben megválaszolt vagy döntésre előkészített open question tételekhez bővebb választ, indoklást és átvezetési javaslatot adjon.

## Használati elv

- Az eredeti kérdés az `OPEN_QUESTIONS.md` fájlban maradjon meg.
- Itt minden válasz az eredeti OQ-azonosítóra hivatkozzon.
- Ha egy kérdés teljesen megválaszolható, itt szerepeljen a döntés és az `OPEN_QUESTIONS.md` javasolt státuszfrissítése.
- Ha egy kérdés csak részben válaszolható meg, itt szerepeljen a jelenlegi irány és a fennmaradó döntési kapu.
- Ha egy válasz később bekerül egy célfájlba, itt jelölhető az átvezetés ténye.

## Bejegyzéssablon

```md
### OQ-... – cím

**Forráskérdés:** `OPEN_QUESTIONS.md / OQ-...`

**Jelenlegi válasz / döntési irány:**

...

**Indoklás:**

...

**Átvezetési célfájl:**

- `...`

**Javasolt OPEN_QUESTIONS státusz:** `...`

**Megjegyzés:**

...
```

---

## OQ-DOC-001 – DOCX → Markdown migráció

**Forráskérdés:** `OPEN_QUESTIONS.md / OQ-DOC-001`

**Jelenlegi válasz / döntési irány:**

Az engine dokumentáció hosszú távon Markdown-alapú legyen.

Az aktív engine-dokumentáció fő Markdown fájljai:

- `README.md`
- `CHECKPOINTS.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `DECISION_MAP.md`
- `ARCHITECTURE.md`
- `TECHNOLOGY_DECISIONS.md`
- `CONTRACT_SPECIFICATION.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `ABILITY_MODULE_SYSTEM.md`
- `PROTOTYPE_PLANS.md`

A hivatalos szabályfőforrások jelenleg maradhatnak DOCX formában:

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

Ezek automatikus Markdown-migrációja nem része az engine dokumentációs MD-migrációjának. Ha később játékosbarát szabálykönyv, engine-barát szabályspecifikáció, AI/Codex-barát rövid szabályspecifikáció vagy párhuzamos MD-alapú szabálymodell készül, az külön döntési kapu.

**Indoklás:**

A projekt jelenlegi dokumentációs iránya szerint az engine dokumentáció Markdownban legyen kezelve, mert így könnyebb a Git diff, az AI/Codex feldolgozás, a merge és a karbantartás. A hivatalos szabályfőforrások viszont külön dokumentumtípusú források, ezért azok formátumváltása külön döntést igényel.

**Átvezetési célfájl:**

- `DECISION_MAP.md`
- szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:** `answered`

**Megjegyzés:**

Az `OPEN_QUESTIONS.md` eredeti kérdéseit nem kell törölni. Elég a státuszt frissíteni, és hivatkozni erre a döntésnapló-bejegyzésre.

---

## OQ-DOC-002 – Checkpointok kezelése

**Forráskérdés:** `OPEN_QUESTIONS.md / OQ-DOC-002`

**Jelenlegi válasz / döntési irány:**

A checkpointok egyetlen központi `CHECKPOINTS.md` fájlban gyűljenek, a `docs/checkpoints/` mappa alatt.

A checkpoint célja rövid, időrendi és tényszerű állapotrögzítés. Tartalmazza:

- mi készült el;
- milyen tesztek vagy smoke testek futottak sikeresen;
- milyen ismert korlátok maradtak;
- mi a következő biztonságos lépés.

A checkpoint ne legyen teljes architektúra, részletes specifikáció, prototípusterv vagy dokumentumkezelési terv.

A régi checkpoint DOCX-ek és részanyagok státusza merge után `MERGED_TO_MD`, `ARCHIVE_REFERENCE` vagy hasonló archív státusz lehet, ha a tartalmuk már bekerült a központi Markdown checkpointba.

**Indoklás:**

A checkpoint-fájl szerepe nem az, hogy minden döntést vagy teljes technikai specifikációt tartalmazzon, hanem az, hogy időrendben, röviden és ellenőrizhetően rögzítse a fejlesztési mérföldköveket.

**Átvezetési célfájl:**

- `CHECKPOINTS.md`
- szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:** `answered`

**Megjegyzés:**

Az eredeti kérdés megtartható az `OPEN_QUESTIONS.md` fájlban, de a válasz itt legyen részletesen rögzítve.

---

## OQ-DOC-003 – Dokumentumszaporodás elkerülése

**Forráskérdés:** `OPEN_QUESTIONS.md / OQ-DOC-003`

**Jelenlegi válasz / döntési irány:**

Új dokumentum csak akkor készüljön, ha:

- új fő témakört fed le;
- nem illeszthető be egy meglévő fődokumentumba;
- nem pusztán átmeneti munkaterv;
- nem duplikál már létező tartalmat.

Alapértelmezett működésként az új tartalom meglévő fődokumentumba kerüljön, ha annak már van természetes helye.

Átmeneti merge-tervek, munkatervek és ideiglenes döntés-előkészítő anyagok a tartalom átvezetése után törölhetők vagy archiválhatók. Ezek nem maradhatnak tartós párhuzamos dokumentációs forrásokként.

**Indoklás:**

A projektben már kialakult egy aktív engine-dokumentációs főfájl-készlet. Az új dokumentumok kontroll nélküli létrehozása rontaná az áttekinthetőséget, ezért minden új fájlnak világos szerepet kell kapnia.

**Átvezetési célfájl:**

- `DECISION_MAP.md`
- szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:** `answered`

**Megjegyzés:**

Ez a most létrehozott `OPEN_QUESTIONS_DECISIONS.md` kivételesen indokolt új dokumentum, mert nem duplikálja az `OPEN_QUESTIONS.md` tartalmát, hanem a kérdésindexhez kapcsolódó válasznaplóként működik.

---

## OQ-ARCH-001 / OQ-ARCH-002 / OQ-TECH-001 / OQ-TECH-002 / OQ-TECH-003 – Python, Godot és hibrid modell

**Forráskérdés:**

- `OPEN_QUESTIONS.md / OQ-ARCH-001`
- `OPEN_QUESTIONS.md / OQ-ARCH-002`
- `OPEN_QUESTIONS.md / OQ-TECH-001`
- `OPEN_QUESTIONS.md / OQ-TECH-002`
- `OPEN_QUESTIONS.md / OQ-TECH-003`

**Jelenlegi válasz / döntési irány:**

A projekt rövid és középtávú fejlesztési iránya a contract-first hibrid modell.

Ez azt jelenti, hogy:

- Python maradjon az adatpipeline, exportvalidáció, runtime package build, diagnostics, report és későbbi AI/batch tesztelés elsődleges technikai rétege.
- Godot/GDScript maradjon runtime package fogyasztó, debug UI, vizuális kliens és későbbi interaktív játékprototípus réteg.
- A runtime package, snapshot, legal action, action request/response, event log és diagnostics contractok legyenek a közös határfelületek.
- A régi Python motor maradjon referencia / archív review státuszban.
- A régi Python motor nem törlendő automatikusan, de nem is automatikusan továbbfejlesztendő fő backend.
- A régi motorból csak külön döntéssel, célzottan, contract-first rendszerbe illeszkedő és teszttel ellenőrizhető módon emelhető át logika.

**Hosszú távú célkép pontosítása:**

A felhasználói célkép alapján a végső forma jelenleg inkább A-szerű lehet: Python rules/backend + Godot frontend/kliens.

Ez azonban jelenleg nem végleges implementációs döntés, hanem hosszú távú célállapot-jelölt. A projekt addig contract-first hibrid modellben halad, amíg a Python-backend, GDScript-runtime vagy más hibrid végállapot technikailag nem bizonyított megfelelően.

Ezért a döntés időbeli rétegzése:

1. **Rövid táv:** contract-first adatút, runtime package, Godot loader/debug, Python build pipeline.
2. **Középtáv:** Python és Godot közötti contractok erősítése, sample contractok, legal action / event log / diagnostics alapok, későbbi AI/batch tesztelési előkészítés.
3. **Hosszú távú jelölt végállapot:** Python rules/backend + Godot frontend/kliens, ha ez technikailag, tesztelhetőségben és terjeszthetőségben megfelelőnek bizonyul.
4. **Fenntartott döntési kapu:** GDScript teljes rules runtime vagy tisztább hibrid modell csak prototípus és összehasonlító teszt után dönthető el.

**Indoklás:**

A hibrid modell nem ellentétes azzal, hogy a végső célkép Python-backend-közeli lehet. A jelenlegi fejlesztési fázisban túl korai lenne véglegesen kijelenteni, hogy a teljes rules runtime Pythonban vagy GDScriptben lesz, mert a Godot oldalon jelenleg a runtime package fogyasztás és debug nézetek bizonyítottak, nem a teljes szabálymotor.

A contract-first megközelítés azért biztonságos, mert a későbbi végleges technológiai döntéstől függetlenül hasznos marad. Ha a végállapot Python backend + Godot frontend lesz, a contractok akkor is tiszta határfelületet adnak. Ha később GDScript runtime erősödik, a contractok akkor is megvédik a rendszert a szabálylogika és UI összekeverésétől.

**Átvezetési célfájl:**

- `TECHNOLOGY_DECISIONS.md`
- `ARCHITECTURE.md`
- `DECISION_MAP.md`
- szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:**

- `OQ-ARCH-001`: `partly_answered`
- `OQ-ARCH-002`: `partly_answered`
- `OQ-TECH-001`: `partly_answered`
- `OQ-TECH-002`: `partly_answered`
- `OQ-TECH-003`: `partly_answered`

**Megjegyzés:**

Ezeket nem érdemes teljesen `answered` státuszra zárni, mert a végleges runtime/backend döntéshez későbbi prototípus, összehasonlító teszt és technológiai bizonyítás kell. A mostani döntés a munkairányt zárja le, nem a végleges engine-implementációt.

---

## OQ-DATA-001 / OQ-DATA-002 / OQ-DATA-005 / OQ-DATA-006 – Runtime package és adatút

**Forráskérdés:**

- `OPEN_QUESTIONS.md / OQ-DATA-001`
- `OPEN_QUESTIONS.md / OQ-DATA-002`
- `OPEN_QUESTIONS.md / OQ-DATA-005`
- `OPEN_QUESTIONS.md / OQ-DATA-006`

**Jelenlegi válasz / döntési irány:**

A runtime package legyen hosszú távon a kötelező programinput.

Ez azt jelenti, hogy:

- A Godot ne olvasson közvetlenül XLSX-et.
- A Python tesztmotor, AI/batch tesztek és validációs rétegek is lehetőleg runtime package-ből dolgozzanak.
- A nyers JSONL / CSV / TSV exportok maradjanak köztes, debug, audit vagy referencia-outputok.
- A manifestes, validált runtime package legyen a tényleges programfogyasztási forma.
- A Python build pipeline kezelje az XLSX beolvasást, exportot, validációt, normalizálást, diagnostics generálást és runtime package buildet.

**Lokális forrásmappák és névhasználat:**

A jelenlegi lokális dokumentum- és forráshely az `Aeterna dokumentációk/` mappa.

Ez rövid távon elfogadható, de később átnevezendő, mert az ékezetes és speciális karakteres mappanevek technikai problémákat okozhatnak. A későbbi mappa- és fájlneveknél ahol lehet, angol, ASCII-barát neveket kell használni.

Javasolt hosszú távú irány:

- ékezetmentes / ASCII-barát projektmappák;
- angol technikai mappanevek;
- magyar tartalom a dokumentumok szövegében maradhat;
- a pipeline és script útvonalak ne függjenek ékezetes mappanévtől;
- minden source és output útvonal legyen konfigurálható.

A pontos átnevezési célmappáról külön fájl- és mappaszerkezeti döntés kell. Addig a jelenlegi hely maradhat, de nem tekintendő végleges technikai névszabványnak.

**`TEMP/` candidate pipeline:**

A `TEMP/` alatti candidate runtime package rövid távon elfogadott fejlesztői staging megoldás, de nem végleges architektúra.

A felhasználói visszajelzés alapján a `TEMP/` mappában sok visszamaradt tesztfájl keletkezhet, ezért a `TEMP/` használata csak akkor elfogadható, ha később készül hozzá ürítési, törlési vagy takarítási megoldás.

Javasolt irány:

- `TEMP/` rövid távon maradhat átmeneti staging mappaként;
- a `TEMP/` nem lehet tartós build artifact vagy referencia-output hely;
- a pipeline később kapjon explicit clean / purge funkciót;
- a clean funkció csak ismert, generált pipeline-outputokat töröljön;
- kézzel szerkesztett vagy canonical forrást soha ne töröljön;
- középtávon a `TEMP/` szerepét váltsa ki tisztább build mappa, például `build/runtime_package_candidate/` és `build/reports/`.

**Két `sample_runtime_package` mappa kezelése:**

A Python oldali és Godot oldali `sample_runtime_package` mappák nem canonical szerkesztési források.

Javasolt státuszok:

- Python oldali `sample_runtime_package`: `GENERATED_TEST_FIXTURE`
- Godot oldali `sample_runtime_package`: `GODOT_CONSUMPTION_COPY`

A Godot oldali package frissítése hosszú távon a Python build pipeline feladata legyen. A pipeline később ellenőrizze, hogy a Godot oldali consumption copy egyezik-e a Python build outputtal.

**Build pipeline és változásérzékelés:**

A build cache és source fingerprint nem MVP-követelmény.

Javasolt időbeli irány:

1. **Rövid táv:** explicit build parancs vagy BAT, amely szükség esetén teljesen újragenerálja az outputokat.
2. **Középtáv:** fájl-hash alapú változásérzékelés.
3. **Hosszú táv:** `source_fingerprint`, amely figyelembe veszi a releváns XLSX fájlokat, sheeteket, oszlopokat, cellaértékeket, exportprofil-verziót, LOOKUPS-verziót, builder-verziót és runtime package schema-verziót.

A correctness fontosabb, mint a cache vagy a gyorsítás.

**Indoklás:**

A runtime package tiszta contract-határt ad a Python tooling, Godot loader, későbbi AI/batch tesztek és debug nézetek között. Ha minden programréteg ugyanazt a validált package-et fogyasztja, kevesebb lesz az eltérés a nyers export, a Godot és a Python oldali értelmezés között.

Az XLSX emberi szerkesztési forma, ezért ne váljon közvetlen Godot runtime inputtá. Az ékezetes / speciális karakteres mappa- és fájlnevek elkerülése pedig csökkenti a későbbi script-, tooling-, Git- és platformfüggő hibák esélyét.

A `TEMP/` mappa csak akkor maradhat rövid távú segédmegoldás, ha nem válik szemétgyűjtővé: a pipeline-nak később tudnia kell, mely fájlokat generálta, és biztonságosan tudnia kell takarítani azokat.

**Átvezetési célfájl:**

- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `ARCHITECTURE.md`
- `DECISION_MAP.md`
- `PROTOTYPE_PLANS.md`
- szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:**

- `OQ-DATA-001`: `answered`
- `OQ-DATA-002`: `partly_answered`
- `OQ-DATA-005`: `partly_answered`
- `OQ-DATA-006`: `answered`

**Megjegyzés:**

Az elvi runtime package irány lezárható, de a pontos mappaátnevezési terv, a `TEMP/` takarító mechanizmus és a build/output mappaszerkezet még későbbi technikai döntést és implementációt igényel.

---

## OQ-DIAG-001 – Severity és blocking rendszer

**Forráskérdés:** `OPEN_QUESTIONS.md / OQ-DIAG-001`

**Jelenlegi válasz / döntési irány:**

A diagnostics rendszerben a `severity` és a `blocking` legyen két külön mező.

A `severity` azt jelöli, hogy a probléma mennyire súlyos vagy milyen jellegű.

A `blocking` azt jelöli, hogy az adott probléma megállítja-e a buildet, a package publish-t, a runtime betöltést vagy az adott action végrehajtását.

Javasolt alap severity értékek:

- `info`
- `audit_note`
- `warning`
- `error`
- `critical`
- `balance_suspicion`

Javasolt alapelv:

- `warning` alapból nem blokkoló.
- `audit_note` alapból nem blokkoló, de emberi áttekintést jelez.
- `error` lehet blokkoló vagy nem blokkoló, a kontextustól függően.
- `critical` alapból blokkoló.
- `balance_suspicion` ne blokkoljon buildet vagy runtime-ot, hanem későbbi audit / balance report kategória legyen.

Példák:

- `warning` + `blocking: false` → nem állít meg semmit.
- `error` + `blocking: true` → nem mehet tovább az érintett folyamat.
- `audit_note` + `blocking: false` → emberi átnézés kell, de a pipeline mehet tovább.
- `critical` + `blocking: true` → súlyos rendszerhiba vagy rejtett információs sérülés; a folyamat álljon meg.
- `balance_suspicion` + `blocking: false` → balanszvizsgálati jelzés, nem engine-hiba.

**Indoklás:**

A severity és a blocking különválasztása azért fontos, mert nem minden súlyosnak tűnő jelzés blokkol azonos módon minden futási módban. Ugyanaz a probléma development módban lehet warning vagy audit note, publish / release candidate módban viszont blocking error.

A külön mezők lehetővé teszik, hogy a diagnostics rendszer egyszerre legyen emberileg olvasható, gépileg feldolgozható és futási mód szerint szigorítható.

**Átvezetési célfájl:**

- `CONTRACT_SPECIFICATION.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:** `answered`

**Megjegyzés:**

A severity/blocking alapmodell ezzel eldőlt. A következő külön döntési réteg az, hogy development, publish, runtime és action execution módban mely hibatípusok legyenek blokkolók.

---

## OQ-DIAG-002 / OQ-DATA-003 / OQ-AR-007 – Blocking szabályok development, publish és runtime módban

**Forráskérdés:**

- `OPEN_QUESTIONS.md / OQ-DIAG-002`
- `OPEN_QUESTIONS.md / OQ-DATA-003`
- `OPEN_QUESTIONS.md / OQ-AR-007`

**Jelenlegi válasz / döntési irány:**

A blocking szabályokat futási mód szerint kell értelmezni.

Három alapmód különüljön el:

1. development build;
2. publish / Godot consumption copy frissítés;
3. runtime / action execution.

### Development build

A development build legyen megengedőbb, de ne engedjen át olyan hibát, amely a loader, a schema, a visibility vagy a minimális package-integritás szintjén veszélyes.

Development buildben blokkoljon:

- hibás vagy hiányzó manifest;
- betölthetetlen package fájl;
- sérült JSON / JSONL;
- kötelező mező hiánya aktív runtime rekordban;
- rejtett információ szivárgását okozó contract-hiba;
- olyan hiba, amitől a Godot vagy Python loader összeomlana.

Development buildben ne blokkoljon, csak warning / audit note legyen:

- nem deckben lévő unsupported kártya;
- partial engine support;
- balance suspicion;
- ismert, nem használt legacy alias;
- még audit alatt álló, de nem futtatott kártyahatás.

### Publish / Godot consumption copy frissítés

Publish vagy Godot consumption copy frissítés előtt szigorúbb szabályok legyenek érvényesek, mert a Godot fogyasztási mappába csak validált package kerülhet.

Publish / Godot copy frissítés előtt blokkoljon:

- bármilyen manifest vagy schema hiba;
- bármilyen `blocking: true` diagnostics;
- deckben szereplő unsupported kártya;
- aktív package-ben futtathatóként jelölt unsupported effect;
- ismeretlen enum aktív runtime mezőben;
- veszélyes legacy alias automatikus javítás nélkül;
- Aeternal / Pecsét régi HP-modellre utaló runtime érték;
- rejtett információs / visibility contract hiba.

Publish / Godot copy frissítés előtt ne blokkoljon:

- nem használt, nem deckben lévő unsupported lap, ha diagnostics jelöli;
- balance suspicion;
- audit note;
- emberi ellenőrzésre váró, de runtime-ban nem aktivált adat.

### Runtime / action execution

Runtime és action execution közben a motor ne találgasson, és ne próbáljon unsupported logikát részben végrehajtani.

Runtime / action execution közben blokkoljon vagy action rejectet okozzon:

- unsupported effect végrehajtási kísérlete;
- invalid target;
- stale snapshotból érkező action, ha már van `state_version`;
- rejtett információt igénylő vagy szivárogtató action;
- olyan kártya actionje, amelynek nincs engine-supported végrehajtása;
- hiányzó required payload.

Fejlesztői módban ezek mellé részletes diagnostics készüljön. Játékosbarát módban csak egyszerű elutasítás és rövid magyarázat jelenjen meg.

**Indoklás:**

A development build célja a gyors fejlesztői visszajelzés, ezért nem minden hiányosság blokkoló. A publish / Godot copy frissítés már stabilabb package-et igényel, ezért szigorúbb. A runtime / action execution a legérzékenyebb réteg, mert ott a motor nem találgathat és nem hajthat végre nem támogatott vagy hiányos szabálylogikát.

A visibility és rejtett információs hibák minden módban kiemelt kockázatot jelentenek, mert későbbi fair AI, PvP és játékosfelület esetén ezek szabálytalan információszivárgást okozhatnak.

**Átvezetési célfájl:**

- `CONTRACT_SPECIFICATION.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `ABILITY_MODULE_SYSTEM.md`
- szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:**

- `OQ-DIAG-002`: `partly_answered`
- `OQ-DATA-003`: `partly_answered`
- `OQ-AR-007`: `partly_answered`

**Megjegyzés:**

Az alap blocking modell elfogadott, de később külön részletes diagnostics mátrix kellhet az egyes hibatípusokra, LOOKUPS értékekre, engine support kategóriákra és action response státuszokra.

---

## OQ-SNAP-001 / OQ-SNAP-002 / OQ-SNAP-003 / OQ-SNAP-004 / OQ-SNAP-005 / OQ-SNAP-006 – Snapshot, visibility és rejtett információ

**Forráskérdés:**

- `OPEN_QUESTIONS.md / OQ-SNAP-001`
- `OPEN_QUESTIONS.md / OQ-SNAP-002`
- `OPEN_QUESTIONS.md / OQ-SNAP-003`
- `OPEN_QUESTIONS.md / OQ-SNAP-004`
- `OPEN_QUESTIONS.md / OQ-SNAP-005`
- `OPEN_QUESTIONS.md / OQ-SNAP-006`

**Jelenlegi válasz / döntési irány:**

A snapshot nem a teljes belső match state, hanem annak nézőpontfüggő kivetítése.

MVP-ben két fő snapshot típus legyen:

- `debug_snapshot`
- `player_visible_snapshot`

Az `opponent_visible_snapshot` ne legyen külön alap snapshot típus az első fázisban. A `player_visible_snapshot` mindig `viewer_id` alapján készüljön; ami az egyik játékosnak ellenféloldal, az a másik játékos saját player-visible nézőpontjából származtatható.

Később külön típus vagy mód lehet:

- `ai_fair_snapshot`
- `ai_debug_snapshot`
- `spectator_snapshot`
- `replay_snapshot`

**Visibility alapelv:**

A player-visible snapshot, player-visible legal action, player-visible event log és player-visible diagnostics soha nem szivárogtathat rejtett információt.

A debug nézet tartalmazhat teljes belső állapotot, de mindig egyértelmű `visibility_mode: debug` vagy hasonló jelöléssel különüljön el.

Javasolt mezők rejtett vagy részben rejtett objektumokra:

- `visibility`
- `known_to`
- `face_down`
- `revealed`

Nem kell minden objektumon minden mezőnek kötelezőnek lennie, de kézlap, pakli, face-down Jel, Pecsét és más rejtett objektum esetén explicit visibility kezelés kell.

**Fair AI és debug AI:**

A fair AI pontosan ugyanazt lássa, mint az adott játékos.

A debug AI láthat teljesebb belső állapotot engine-hibakereséshez, de balanszméréshez ne legyen alapértelmezett.

**Ősforrás láthatósága:**

Az Ősforrás lapazonossága csak az adott játékos számára legyen látható.

Az ellenfél az Ősforrásból csak azt lássa:

- hány lap van ott;
- milyen állapotban vannak a lapok, például `ready` / `exhausted`;
- szükség esetén összesített fizetési / aura-releváns információt.

Az ellenfél ne lássa az Ősforrás konkrét kártyaazonosságait player-visible módban.

A fair AI ugyanazt lássa az Ősforrásból, mint az adott játékos láthatna.

**Pecsétmodell snapshotban:**

A Pecsét továbbra sem HP-objektum.

Tiltott / kerülendő mezők:

- `ward_hp`
- `seal_hp`
- `seal_damage`
- `ward_damage`

A Pecsét javasolt állapotértékei:

- `standing`
- `broken`
- `restored`
- `removed`

A Pecsét snapshot-modellje azonban nem zárható le teljesen, mert előbb el kell dönteni a Pecsét létrehozási modelljét.

Nyitott Pecsét-létrehozási modellek:

1. **Játékos által választott Pecsétlapok:** a játékos tudja, mely lapokat és hová helyezte le; ebben a modellben saját Pecsétjei teljesen ismertek számára.
2. **Random húzott Pecsétlapok:** a Pecsétlapok véletlenszerűen kerülnek le; ebben a modellben dönteni kell, hogy a játékos nem látja őket, vagy lehelyezés után megnézheti.
3. **Hibrid modell:** a játékos több lapot húz / kap, majd azokból választ Pecsétet; ebben a modellben a játékos saját Pecsétjei ismertek, de a választási tér véletlen elemet tartalmaz.

A Pecsét láthatósága és snapshotbeli kártyareferenciája attól függ, melyik Pecsét-létrehozási modell lesz végleges.

Addig rögzített irány:

- Pecsét HP nincs;
- Pecsétállapot kell;
- `linked_current` valószínűleg szükséges;
- a Pecsét konkrét lapazonosságának láthatósága nyitott szabálydöntés;
- a Pecsét létrehozási modellje külön döntési kapu.

**Pending decision snapshotban:**

A `pending` mező legyen jelen minden snapshotban, de lehet üres vagy false állapotú.

Ha nincs döntés:

```json
"pending": {
  "has_pending_decision": false
}
```

Ha van döntés:

```json
"pending": {
  "has_pending_decision": true,
  "window_type": "reaction",
  "priority_player_id": "player_1",
  "can_pass": true,
  "expected_action_family": "reaction"
}
```

MVP `window_type` jelöltek:

- `main`
- `reaction`
- `targeting`
- `choice`
- `payment`
- `combat`
- `system`

A `prompt_hu` rövid távon jöhet backendből vagy debug contractból, de hosszú távon lokalizációs / UI rétegre érdemes vinni. A rules engine ne magyar promptszöveg alapján vezéreljen szabályt.

**Event log snapshotban:**

A snapshot ne tartalmazza a teljes event logot.

A snapshot tartalmazhat:

- `recent_events` rövid listát;
- `last_event_index` értéket;
- később esetleg `next_event_index` értéket.

A teljes event log külön contract / fájl / endpoint legyen.

Később szükséges lehet külön szűrés:

- `debug_event_log`
- `player_visible_event_log`
- `ai_fair_event_log`
- `replay_event_log`

**Indoklás:**

A snapshot nézőpontfüggő contract. Ha a snapshot a belső match state közvetlen dumpja lenne, az könnyen rejtett információt szivárogtatna. A `viewer_id` alapú `player_visible_snapshot` egyszerűbb és biztonságosabb, mint több korai, párhuzamos snapshot típus fenntartása.

Az Ősforrás lapazonosságának rejtése csökkenti az információszivárgást és összhangban van azzal, hogy az ellenfél csak a lapok számát és állapotát lássa. A Pecsétmodellnél viszont nem lehet végleges visibility döntést hozni a létrehozási modell eldöntése előtt.

A `pending` mező állandó jelenléte egyszerűsíti a frontend, AI és debug réteg kezelését. A teljes event log különválasztása pedig megakadályozza, hogy a snapshot túl nagy, nehezen szűrhető vagy rejtett információt tartalmazó történeti dumpá váljon.

**Átvezetési célfájl:**

- `CONTRACT_SPECIFICATION.md`
- `ARCHITECTURE.md`
- szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:**

- `OQ-SNAP-001`: `partly_answered`
- `OQ-SNAP-002`: `partly_answered`
- `OQ-SNAP-003`: `answered`
- `OQ-SNAP-004`: `partly_answered`
- `OQ-SNAP-005`: `partly_answered`
- `OQ-SNAP-006`: `partly_answered`

**Megjegyzés:**

Az Ősforrás láthatósága eldőlt: ellenfél csak darabszámot és állapotot lát, konkrét kártyaazonosságot nem. A Pecsétmodell nem zárható le, amíg nincs külön döntés arról, hogy a Pecsétlapok választással, random húzással vagy hibrid módon jönnek létre.

---

## OQ-LA-001 / OQ-LA-002 / OQ-LA-003 / OQ-LA-004 / OQ-LA-005 / OQ-LA-006 / OQ-LA-007 / OQ-AR-001 / OQ-AR-002 / OQ-AR-003 / OQ-AR-004 / OQ-AR-005 / OQ-AR-006 / OQ-AR-007 – Legal actions, action request és action response

**Forráskérdés:**

- `OPEN_QUESTIONS.md / OQ-LA-001`
- `OPEN_QUESTIONS.md / OQ-LA-002`
- `OPEN_QUESTIONS.md / OQ-LA-003`
- `OPEN_QUESTIONS.md / OQ-LA-004`
- `OPEN_QUESTIONS.md / OQ-LA-005`
- `OPEN_QUESTIONS.md / OQ-LA-006`
- `OPEN_QUESTIONS.md / OQ-LA-007`
- `OPEN_QUESTIONS.md / OQ-AR-001`
- `OPEN_QUESTIONS.md / OQ-AR-002`
- `OPEN_QUESTIONS.md / OQ-AR-003`
- `OPEN_QUESTIONS.md / OQ-AR-004`
- `OPEN_QUESTIONS.md / OQ-AR-005`
- `OPEN_QUESTIONS.md / OQ-AR-006`
- `OPEN_QUESTIONS.md / OQ-AR-007`

**Jelenlegi válasz / döntési irány:**

A frontend és az AI ne számolja ki önállóan a szabályos lépéseket.

A legal action listát a rules engine vagy későbbi rules service adja vissza. A frontend és az AI ebből dolgozik, action requestet küld, majd az action response alapján frissül a snapshot / event log / diagnostics.

**Enabled és disabled actionök:**

Normál player-visible módban csak az `enabled` actionök jelenjenek meg.

Debug módban láthatók lehetnek a `disabled` actionök is, `disabled_reason` mezővel.

Tutorial mód később kaphat játékosbarát disabled reason / magyarázat mezőt, de ez ne legyen MVP-követelmény.

Javasolt irány:

- `player_visible`: csak enabled actionök;
- `debug`: enabled + disabled actionök;
- `tutorial`: későbbi mód, disabled reason játékosbarát szöveggel;
- fair AI alapból csak enabled actionöket kapjon.

**Reaction window / Burst / Jel:**

MVP-ben legyen `reaction` action family és pending reaction window modell.

A `pass_priority` / `pass_reaction` legyen külön legal action.

Ha nincs valódi reakciólehetőség, a reaction window automatikusan átugorható.

A reaction window jelenjen meg mindkét helyen:

- snapshot `pending` mezőben;
- legal action listában.

A stack / chain jellegű modellről még ne legyen végleges döntés. Rövid távon elég a reaction queue / pending reaction window modell.

Burst és Jel egyelőre ugyanabba a reaction keretrendszerbe kerülhet, de a részletes timing / priority / prevention / replacement modell későbbi ability- és rules audit döntési kapu.

**Combat actionök:**

A teljes combat legal action rendszer ne legyen MVP-zárás.

A contract tartsa fenn a későbbi action family / action type helyét, például:

- `declare_attack`
- `choose_attack_target`
- `choose_blocker`

A combat részletes bevezetése a Pecsétmodell és combat rules spec után történjen.

A Pecsét feltörése attack után később eventként és szükség esetén target-kapcsolatként is megjelenhet, de ezt most nem kell véglegesen lezárni.

**Fizetés / Aura:**

MVP-ben az Aura-fizetés legyen automatikus, ha egyértelmű.

Kézi payment window csak akkor kell, ha:

- több szabályosan választható fizetési forrás van;
- ideiglenes Aura / különleges forrás később bekerül;
- alternatív költség van;
- a választás stratégiai jelentőségű.

A legal action tartalmazzon `cost_summary` mezőt.

A konkrét payment választék csak akkor legyen része a legal actionnek vagy pending payment ablaknak, ha tényleg van döntés.

**Targeting:**

Egyszerű célzásnál a play action payload már tartalmazhatja a célpontot.

Többlépcsős vagy többcélpontos célzásnál legyen külön `targeting` action / pending state.

A célpont érvényességének végső döntése mindig a rules engine-ben maradjon.

A frontend kiemelhet célpontokat, de csak a legal action targeting adatai alapján.

Javasolt irány:

- simple target: play action payloadban lehet;
- complex target: külön targeting pending/action;
- invalid target: runtime reject vagy partial resolution csak külön szabálypéldák után;
- frontend nem validál véglegesen, csak megjelenít.

**UI mezők a legal actionben:**

A legal action tartalmazhat minimális UI-segédadatot, de az UI mezők nem lehetnek szabályforrások.

Rövid távon használható:

- `label_hu`
- `prompt_hu`
- `disabled_reason_hu`
- `highlight_hint`

Hosszú távon ezek kerüljenek lokalizációs / lookup / UI rétegbe.

A rules engine ne magyar szövegből vezéreljen szabályt.

**AI mezők:**

Fair AI ugyanazt a legal action listát kapja, mint a játékos, csak gépileg feldolgozhatóbb formában.

A fair AI ne kapjon olyan információt, amit a játékos nem látna.

Debug AI kaphat extra mezőket és teljesebb információt, de ne ez legyen balanszmérés alapja.

AI heuristic tag vagy becsült érték később bevezethető, de ne legyen MVP-követelmény. Az AI alapból külön értékelje a legal actionöket.

**Action request azonosítás:**

MVP lokális debug módban elég egyszerű request modell, de már legyen opcionális `client_request_id`.

Későbbi interaktív UI / PvP előtt legyen kötelező vagy erősen ajánlott:

- `client_request_id`
- `snapshot_id`
- `state_version`
- `action_id`

MVP local/debug módban a `client_request_id` opcionális lehet.

Interaktív UI-tól ajánlott.

PvP / hálózati működés előtt kötelező.

**Snapshot frissesség és state_version:**

Legyen `state_version` már MVP-ben, akár egyszerű számlálóként.

Ha az action request régi `state_version` alapján érkezik:

- local debug módban lehet warning + újravalidálás;
- normál interaktív módban inkább reject;
- PvP előtt mindig reject.

**Action ID élettartama:**

Az `action_id` csak az adott snapshot / state_version kontextusában legyen stabil.

Új legal action lista vagy új state_version érvényteleníti a régi action ID-kat.

Hosszú életű signed / opaque action token ne legyen MVP-követelmény.

AI-vs-AI tesztnél elég, ha az action ID egy adott legal action listán belül stabil.

**Action response és részleges feloldás:**

Javasolt alap action response státuszok:

- `accepted`
- `rejected`
- `resolved`
- `partially_resolved`
- `pending_decision`
- `pending_reaction`
- `prevented`
- `replaced`
- `cancelled`
- `failed`
- `not_executable`

Reaction window esetén az action response adhat `pending_reaction` státuszt, és az új snapshot `pending` mezője mutassa a döntési helyzetet.

Partial resolution részletes szabályai még ne legyenek lezárva. Ehhez konkrét szabálypéldák kellenek.

Unsupported effect esetén az action response legyen `not_executable`, és készüljön diagnostics bejegyzés. Fejlesztői/debug módban generálható event is, hogy az event logban látszódjon a kísérlet; player-visible normál módban ezt óvatosan kell szűrni, hogy ne szivárogtasson rejtett információt.

**Indoklás:**

A legal action contract lényege, hogy a szabálylogika ne szivárogjon át a frontendbe vagy az AI-ba. Ha a frontend és az AI csak a rules engine által adott action listából dolgozik, akkor a játékosfelület, debug UI, fair AI és későbbi PvP is ugyanarra a szabályforrásra épül.

Az enabled/disabled elválasztás fejlesztésben és tutorialban hasznos, de normál játékban nem kell minden tiltott lehetőséget megmutatni. A fair AI rejtett információtól való elzárása különösen fontos, mert későbbi balanszmérésnél csak így kapunk játékosszerű döntési helyzeteket.

A `state_version` és snapshot-scope action ID már MVP-ben is olcsó védelmet ad a stale actionök ellen, miközben később szigorítható PvP / hálózati működéshez.

A combat, stack/chain timing, prevention/replacement és partial resolution részletei túl szabályfüggők ahhoz, hogy most véglegesen lezárjuk őket. Ezek külön példák és prototípus után zárhatók.

**Átvezetési célfájl:**

- `CONTRACT_SPECIFICATION.md`
- `ABILITY_MODULE_SYSTEM.md`
- `ARCHITECTURE.md`
- szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:**

- `OQ-LA-001`: `answered`
- `OQ-LA-002`: `partly_answered`
- `OQ-LA-003`: `partly_answered`
- `OQ-LA-004`: `partly_answered`
- `OQ-LA-005`: `partly_answered`
- `OQ-LA-006`: `partly_answered`
- `OQ-LA-007`: `partly_answered`
- `OQ-AR-001`: `partly_answered`
- `OQ-AR-002`: `partly_answered`
- `OQ-AR-003`: `answered`
- `OQ-AR-004`: `partly_answered`
- `OQ-AR-005`: `partly_answered`
- `OQ-AR-006`: `partly_answered`
- `OQ-AR-007`: `partly_answered`

**Megjegyzés:**

Az alap legal action / action request / action response modell elfogadott. A combat, stack/chain timing, prevention/replacement, komplex payment, complex targeting és partial resolution részletei későbbi szabálypéldákhoz és prototípushoz kötött döntési kapuk maradnak.
