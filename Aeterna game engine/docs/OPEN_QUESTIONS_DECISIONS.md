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
