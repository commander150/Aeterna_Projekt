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

---

## OQ-EVENT-001 / OQ-EVENT-002 / OQ-EVENT-003 / OQ-EVENT-004 / OQ-EVENT-005 / OQ-EVENT-006 – Event log, explanation log, replay és balance eventek

**Forráskérdés:**

* `OPEN_QUESTIONS.md / OQ-EVENT-001`
* `OPEN_QUESTIONS.md / OQ-EVENT-002`
* `OPEN_QUESTIONS.md / OQ-EVENT-003`
* `OPEN_QUESTIONS.md / OQ-EVENT-004`
* `OPEN_QUESTIONS.md / OQ-EVENT-005`
* `OPEN_QUESTIONS.md / OQ-EVENT-006`

**Jelenlegi válasz / döntési irány:**

Az event log a játék történeti rétege.

Alapelv:

**A snapshot az állapot. Az event log a történet.**

MVP-ben az event log legyen gameplay-szinten olvasható, de ne tartalmazzon player-visible módban minden apró belső engine-lépést.

### Event layer modell

MVP-ben legyen három alap event layer:

* `gameplay`
* `debug`
* `system`

Későbbi bővítési lehetőségek:

* `explanation`
* `audit`
* `balance`
* `frontend`

A `gameplay` eventek azok, amelyek a játékosnak, UI-nak, fair AI-nak és későbbi visszajátszásnak is hasznosak lehetnek.

A `debug` eventek engine-fejlesztési, hibakeresési és belső vizsgálati célra szolgálnak.

A `system` eventek technikai folyamatokat jelölhetnek, például betöltést, validációt, unsupported feature kezelést vagy runtime figyelmeztetést.

### Event log részletesség

Player-visible módban ne készüljön esemény minden apró belső engine-lépésről.

Javasolt MVP eventek:

* körváltás;
* fázis / step váltás, ha játékosnak releváns;
* lap kijátszása;
* lap mozgása publikus zónák között;
* húzás / dobás, visibility szabályok szerint;
* Entitás sebződése / gyógyulása;
* Pecsét feltörése / visszaállítása;
* Jel lehelyezése / felfedése / aktiválása;
* reakcióablak megnyílása / lezárása;
* action reject, ha játékosnak látnia kell;
* győzelem / vereség;
* jelentős rendszeresemény debug módban.

A nagyon részletes belső lépések debug eventként vagy későbbi trace rétegként kezelhetők.

### Event mezők

Javasolt MVP event mezők:

* `event_id`
* `event_index`
* `event_type`
* `event_family`
* `event_layer`
* `match_id`
* `turn`
* `phase`
* `step`
* `actor_player_id`
* `source`
* `targets`
* `affected_objects`
* `visibility`
* `message_hu`
* `message_dev`
* `diagnostics`
* `caused_by`
* `parent_event_id`
* `correlation_id`
* `metadata`

MVP-ben nem mindegyik mező kötelező minden eventnél.

Fontos mezők:

* `event_index`: későbbi snapshot `last_event_index`, replay és diff miatt hasznos.
* `visibility`: player-visible / debug / fair AI szűréshez szükséges.
* `caused_by`: reakció, replacement, prevention és részleges feloldás követéséhez hasznos.
* `parent_event_id`: összetett eseményláncok követéséhez hasznos.
* `correlation_id`: egy actionből származó több event összekapcsolásához hasznos.

### Rejtett információ event logban

Legyen egy teljes belső event log, amelyből viewer szerint szűrt player-visible / fair AI / replay nézet készülhet.

Ne keletkezzen több párhuzamos „igazság”. A belső log lehet teljes, de a player-visible log csak azt tartalmazhatja, amit az adott játékos szabályosan láthat.

Javasolt irány:

* internal/debug log tartalmazhat teljes információt;
* player-visible log soha nem szivárogtathat rejtett információt;
* fair AI ugyanazt az event logot kapja, mint az adott játékos;
* debug AI kaphat debug logot;
* PvP előtt kötelező visibility audit kell.

### Face-down Jel eventek

Face-down Jel aktiválása előtt az ellenfél player-visible logja ne lássa a konkrét kártyaazonosságot.

Ellenfélnek aktiválás előtt csak ilyen jellegű event látszódjon:

* az ellenfél lehelyezett egy rejtett Jelet;
* egy rejtett Jel állapotot változtatott;
* rejtett Jelhez kapcsolódó publikus döntési ablak nyílt, ha szabály szerint látható.

Saját játékosnak és debug módban a konkrét kártyaazonosság látható lehet, ha a szabálymodell ezt engedi.

Felfedéskor / aktiváláskor már keletkezhet konkrét `sigil_revealed` vagy hasonló event, amely tartalmazhatja a kártyaazonosságot.

### Explanation log / játékosbarát magyarázat

Nem kell minden eventhez magyar magyarázat.

MVP-ben `message_hu` vagy magyarázó szöveg főleg ezeknél legyen fontos:

* komplex reakció;
* replacement;
* prevention;
* részleges feloldás;
* invalid / rejected action;
* unsupported / not_executable debug eset;
* győzelem / vereség;
* Pecsét feltörés / visszaállítás;
* olyan szabályhelyzet, amely játékosnak magyarázat nélkül zavaros lenne.

Rövid távon a `message_hu` engedett és hasznos debug / fejlesztői nézetben.

Hosszú távon tisztább irány:

* `explanation_key`
* `explanation_params`
* frontend / lokalizációs lookup

A rules engine ne magyar szöveg alapján vezéreljen szabályt.

### Diagnostics és event log kapcsolata

A diagnostics és az event log külön réteg.

Az event log történeti eseményeket rögzít.

A diagnostics strukturált problémát, hibát, figyelmeztetést, audit note-ot vagy balance suspiciont rögzít.

A két réteg hivatkozhat egymásra:

* event tartalmazhat `diagnostic_id` hivatkozást;
* diagnostics entry tartalmazhat `event_id` hivatkozást;
* egy action response tartalmazhat eventeket és diagnosticokat is.

Unsupported effect esetén:

* diagnostics bejegyzés kötelező;
* debug módban event is készülhet;
* player-visible normál módban az eventet óvatosan kell szűrni, hogy ne szivárogtasson rejtett vagy fejlesztői információt.

Engine warning önmagában ne generáljon automatikusan mindig player-visible eventet.

### Replay-kompatibilitás

A teljes replay-rendszer nem MVP-követelmény.

Az event log szerkezete viszont legyen később replayre alkalmassá tehető.

Javasolt előkészítő elemek:

* `event_index`;
* `state_version` kapcsolat;
* `caused_by`;
* `parent_event_id`;
* `correlation_id`;
* action history későbbi bevezetésének lehetősége;
* snapshot checkpoint későbbi optimalizációként.

MVP-ben nem kell teljes visszajátszó rendszer, de az event log ne zárja ki a későbbi replayt.

### Balance eventek és balance report

A `balance_suspicion` ne normál gameplay event legyen.

Balanszvizsgálathoz gyűjthetők gameplay és debug adatok, de a balanszgyanú inkább futás utáni elemzésben vagy külön `balance_report` contractban keletkezzen.

Később balanszvizsgálathoz hasznos event family-k / adatok:

* card usage;
* draw;
* discard;
* combat;
* Entitás-sebzés;
* Pecsét feltörés / visszaállítás;
* Aura költés;
* reakcióhasználat;
* token létrejötte / megszűnése;
* győzelmi feltétel;
* játék hossza;
* játékosonkénti döntésszám;
* kártyánkénti hatásgyakoriság.

A balance suspicion nem engine error.

### Aeternal / Pecsét eventek

Támogatandó event type jelöltek:

* `ward_broken`
* `ward_restored`
* `ward_break_prevented`
* `aeternal_unprotected`
* `direct_attack_victory`
* `player_defeated`

Kerülendő vagy tiltott event type jelöltek:

* `player_damage`
* `aeternal_damage`
* `heal_player`
* `heal_aeternal`
* `ward_damage`
* `seal_damage`

A `damage` event family csak Entitás-sebzésre vagy más szabályosan értelmezett sebzési eseményre használható, de nem Aeternal HP-sebzésre.

**Indoklás:**

Az event log célja, hogy visszakövethető legyen, mi történt a játékban, de ne váljon túl zajos belső engine dumpá player-visible módban.

A belső teljes event log és a viewer szerint szűrt event log együtt biztonságosabb modell, mint több egymástól eltérő történeti forrás fenntartása. Így a debug, fair AI, player-visible UI és későbbi replay ugyanabból az igaz belső történetből származtatható, miközben a player-visible nézet nem szivárogtat rejtett információt.

Az explanation log külön kezelése azért fontos, mert a játékosbarát magyarázat nem azonos a szabálymotor belső eseményével. Rövid távon a magyar `message_hu` hasznos, de hosszú távon lokalizációs kulcsokkal és paraméterekkel tisztább lesz a rendszer.

A diagnostics és event log szétválasztása azért szükséges, mert nem minden probléma gameplay esemény, és nem minden gameplay esemény probléma. A két réteg között viszont hasznos a hivatkozás, különösen unsupported effect, action reject, partial resolution és debug vizsgálat esetén.

**Átvezetési célfájl:**

* `CONTRACT_SPECIFICATION.md`
* `ARCHITECTURE.md`
* `DECISION_MAP.md`
* szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:**

* `OQ-EVENT-001`: `partly_answered`
* `OQ-EVENT-002`: `partly_answered`
* `OQ-EVENT-003`: `partly_answered`
* `OQ-EVENT-004`: `partly_answered`
* `OQ-EVENT-005`: `partly_answered`
* `OQ-EVENT-006`: `partly_answered`

**Megjegyzés:**

Az event log alapmodell elfogadott. A teljes replay rendszer, a részletes explanation/localization megoldás, a balance report pontos formátuma és a PvP előtti visibility audit későbbi döntési kapuk maradnak.

---

## OQ-DIAG-003 / OQ-DIAG-004 / OQ-DIAG-005 / OQ-DIAG-006 / OQ-DIAG-007 – Diagnostics report, runtime visibility, LOOKUPS diagnostics, balance suspicion és checkpoint kapcsolat

**Forráskérdés:**

* `OPEN_QUESTIONS.md / OQ-DIAG-003`
* `OPEN_QUESTIONS.md / OQ-DIAG-004`
* `OPEN_QUESTIONS.md / OQ-DIAG-005`
* `OPEN_QUESTIONS.md / OQ-DIAG-006`
* `OPEN_QUESTIONS.md / OQ-DIAG-007`

**Jelenlegi válasz / döntési irány:**

A diagnostics rendszer elsődleges célja, hogy strukturáltan jelezze az export, runtime package, LOOKUPS, engine support, action validation, hidden information, audit és balance problémákat.

A severity és blocking alapmodell már rögzített irány:

* `severity` jelöli a probléma súlyosságát vagy típusát;
* `blocking` jelöli, hogy a probléma megállítja-e az adott folyamatot.

Ez a döntési blokk azt rögzíti, hogy a diagnostics milyen reportokban, milyen nézetekben és milyen láthatósággal jelenjen meg.

### Diagnostics report formátum

A diagnostics elsődleges gépi formája JSON legyen.

Emberi olvasásra készüljön Markdown összefoglaló.

Javasolt alap outputok:

* `diagnostics.json`
* `diagnostics_summary.md`

Későbbi bővítési lehetőségek:

* `export_diagnostics.json`
* `runtime_diagnostics.json`
* `engine_support_report.json`
* `lookup_diagnostics.json`
* `balance_report.json`

A runtime package ne tartalmazza minden részletes diagnostics bejegyzés teljes dumpját.

A runtime package tartalmazzon:

* diagnostics summaryt;
* blocking státusz összegzést;
* report-hivatkozást;
* szükség esetén rövid package-load szintű diagnosztikai adatot.

A teljes részletes report külön regenerálható output legyen.

A report fájlok alapértelmezés szerint generált outputok, nem kézzel szerkesztett canonical források.

### Diagnostics report és entry mezők

Javasolt diagnostics report mezők:

* `schema_version`
* `report_id`
* `report_type`
* `runtime_package_id`
* `match_id`
* `source_file`
* `generated_at`
* `summary`
* `entries`
* `blocking_errors`
* `warnings`
* `audit_notes`
* `metadata`

Javasolt diagnostics entry mezők:

* `diagnostic_id`
* `category`
* `severity`
* `blocking`
* `code`
* `message_hu`
* `message_dev`
* `source_ref`
* `object_ref`
* `field`
* `value`
* `expected`
* `suggested_fix`
* `related_event_id`
* `related_action_id`
* `metadata`

Később hasznos kiegészítő mezők lehetnek:

* `phase`
* `scope`
* `can_auto_fix`
* `auto_fix_applied`
* `requires_human_review`

Ezek nem feltétlenül MVP-kötelezők, de export, LOOKUPS, structured mezők és runtime package build során hasznosak lehetnek.

### Runtime visibility

Normál játékos ne lásson fejlesztői diagnostics üzeneteket.

Player-visible módban csak játékosbarát, rövid, rejtett információt nem szivárogtató hibaüzenet jelenjen meg.

Példák player-safe üzenetekre:

* „Ezt a lapot most nem játszhatod ki.”
* „Nem választható ez a célpont.”
* „Nincs elég Aurád.”
* „Ez a döntés már nem érvényes, frissült a játékállapot.”

Debug / developer módban látszódhat a teljes diagnostics entry.

Tutorial módban később lehet játékosbarát magyarázat, de ez ne legyen MVP-követelmény.

Diagnostics üzenet soha nem szivárogtathat rejtett információt.

Ez különösen fontos:

* action rejected esetén;
* face-down Jel esetén;
* ellenfél kézlapjai esetén;
* fair AI snapshotnál;
* player-visible event lognál.

Javasolt visibility irány:

* `player_visible`: rövid, játékosbarát, safe üzenet;
* `debug_only`: fejlesztői részletek;
* `developer_only`: belső technikai információ;
* `ai_fair`: csak azt tartalmazhatja, amit a játékos is láthatna;
* `system_only`: belső pipeline / runtime üzenet.

### LOOKUPS diagnostics

A LOOKUPS és structured audit hibáknál külön severity / blocking értelmezés szükséges.

Alapértelmezett döntési irány:

| Eset                                                     | Javasolt kezelés                                                  |
| -------------------------------------------------------- | ----------------------------------------------------------------- |
| Unknown enum aktív runtime mezőben                       | `error`, publish/runtime blocking                                 |
| Unknown enum nem használt vagy nem aktív adaton          | `warning` vagy `audit_note`                                       |
| Inactive value aktív kártyán runtime mezőben             | `error`, publish blocking                                         |
| Workflow-only value runtime mezőben                      | `error`, publish blocking                                         |
| Label_HU és Value keveredése development módban          | `warning`                                                         |
| Label_HU és Value keveredése aktív runtime mezőben       | `error`                                                           |
| Known legacy alias biztonságos auto-fixszel              | `warning`, auto-normalizálható                                    |
| Dangerous legacy alias                                   | `error` vagy `audit_note`, emberi review                          |
| `audit_required` aktív runtime kártyán                   | legalább `audit_note`; futtathatóként jelölt lapon blocking lehet |
| Canonical mismatch development módban                    | `warning`                                                         |
| Canonical mismatch publish előtt                         | `error`                                                           |
| Többértékű mező delimiter hiba runtime parsingot érintve | `error`                                                           |

Javasolt irány:

* biztonságos, egyértelmű legacy alias automatikusan normalizálható;
* veszélyes vagy kétértelmű alias ne legyen automatikus javítás, hanem emberi audit;
* aktív runtime mezőben unknown / inactive / workflow-only érték publish előtt blokkoljon;
* development build lehet megengedőbb, de minden ilyen hibát reportoljon;
* runtime package-be ne kerülhessen ismeretlen aktív enum futtathatóként.

### Engine support diagnostics

Javasolt engine support status értékek:

* `supported`
* `partial`
* `unsupported`
* `not_checked`
* `fallback_required`
* `manual_review_required`

Értelmezés:

* `supported`: futtatható.
* `partial`: csak korlátozással vagy részlegesen futtatható.
* `unsupported`: normál runtime-ban nem futtatható.
* `not_checked`: még nincs engine support ellenőrzés.
* `fallback_required`: csak fejlesztői/debug módban elfogadható átmenetileg.
* `manual_review_required`: emberi audit kell.

Javasolt blocking irány:

* deckben szereplő `unsupported` kártya publish / Godot consumption copy előtt blokkoljon;
* deckben szereplő `not_checked` kártya publish előtt blokkoljon;
* nem deckben lévő unsupported kártya development módban warning lehet;
* `fallback_required` hosszú távon kivétel legyen, nem alapműködés;
* fair AI-vs-AI tesztben unsupported lap ne fusson csendben;
* debug tesztben unsupported lap kihagyható vagy `not_executable` státuszt kaphat, de reportolni kell.

### Balance suspicion

A `balance_suspicion` nem engine error.

A balance suspicion ne blokkoljon buildet, runtime-ot vagy action executiont.

Első körben ne legyen végleges, kemény winrate-küszöb, mert ehhez stabil engine, sok meccs, megbízható AI és ellenőrzött decklisták kellenek.

Ideiglenes értelmezési irány:

* 40–60% winrate: normál sáv, önmagában nem gyanús.
* 35–65% sávon kívül: figyelendő, ha elég sok minta van.
* 30–70% sávon kívül: erős gyanú, de csak ha engine / deck / test hiba kizárható.
* 25–75% sávon kívül: magas prioritású balance audit, megfelelő mintaszám mellett.

Balance suspicion vonatkozhat:

* kártyára;
* deckre;
* klánra;
* birodalomra;
* matchupra;
* kulcsszóra;
* mechanika-csomagra.

Javasolt irány:

* balance suspicion futás utáni elemzésben keletkezzen;
* ne gameplay event legyen;
* később külön `balance_report` contract készüljön;
* előbb engine, decklista és tesztkonfigurációs hibát kell kizárni;
* balance suspicion emberi auditot igénylő jelzés lehet, de nem automatikus szabálymódosítás.

### Diagnostics és checkpointok kapcsolata

Checkpointba ne kerüljön teljes diagnostics dump.

Checkpoint tartalmazzon rövid diagnostics összefoglalót:

* blocking errors száma;
* warnings száma;
* audit notes száma;
* ismert, nem blokkoló környezeti warningok;
* smoke test diagnostics summary;
* lényeges új probléma;
* megoldott korábbi probléma;
* ismert, nem blokkoló technikai jelzés.

A teljes részletes diagnostics report külön fájlban maradjon.

Javasolt irány:

* checkpoint csak összefoglalót tartalmazzon;
* checkpoint ne legyen diagnostics adatbázis;
* nem blokkoló Godot / Windows / környezeti warningok külön „known non-blocking environment warning” jelölést kapjanak;
* csak a tényleges AETERNA-hibák és fejlesztést befolyásoló jelzések kapjanak részletesebb checkpoint említést.

**Indoklás:**

A diagnostics rendszernek egyszerre kell gépileg feldolgozhatónak, fejlesztői szempontból hasznosnak és játékosnézetben biztonságosnak lennie.

A JSON elsődleges forma azért szükséges, mert a build pipeline, Godot loader, Python tesztek, AI futtatások és későbbi CI jellegű folyamatok gépi feldolgozásra támaszkodnak.

A Markdown summary azért szükséges, mert a fejlesztői áttekintés, checkpoint és emberi audit gyorsabban használható olvasmányos formában.

A runtime package nem válhat túl nagy diagnostics adattárrá. A package feladata a futtatható / betölthető runtime adat biztosítása, ezért csak summaryt és hivatkozást tartalmazzon, a részletes report pedig külön generált output legyen.

A player-visible diagnostics korlátozása azért kritikus, mert a hibaüzenetek is szivárogtathatnak rejtett információt. Ez különösen fontos fair AI, későbbi PvP, face-down Jel, ellenfél kézlap és action reject esetén.

A LOOKUPS diagnostics külön szabályozása azért szükséges, mert az enum, alias, workflow-only és canonical hibák közvetlenül veszélyeztetik a runtime package megbízhatóságát. Development módban lehet megengedőbb a rendszer, de publish / Godot consumption copy előtt az aktív runtime mezőknek tisztának kell lenniük.

A balance suspicion nem azonos engine-hibával. Balanszgyanút csak megfelelő mintaszám, stabil engine, ellenőrzött decklista és emberi értelmezés mellett szabad komolyan venni.

**Átvezetési célfájl:**

* `CONTRACT_SPECIFICATION.md`
* `RUNTIME_PACKAGE_SPECIFICATION.md`
* `DECISION_MAP.md`
* `CHECKPOINTS.md`
* szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:**

* `OQ-DIAG-003`: `partly_answered`
* `OQ-DIAG-004`: `partly_answered`
* `OQ-DIAG-005`: `partly_answered`
* `OQ-DIAG-006`: `partly_answered`
* `OQ-DIAG-007`: `partly_answered`

**Megjegyzés:**

A diagnostics report és runtime visibility alapmodell elfogadott. A pontos JSON schema, diagnostics code-lista, LOOKUPS hibamátrix részletes enumlistája, balance report contract és checkpoint summary formátum későbbi technikai specifikációs feladat marad.

---

## OQ-ABIL-001 / OQ-ABIL-002 / OQ-ABIL-003 / OQ-ABIL-004 / OQ-ABIL-005 / OQ-ABIL-006 / OQ-ABIL-007 / OQ-ABIL-008 – Ability module system, structured mezők, execution plan, fallback, keyword és ability registry

**Forráskérdés:**

* `OPEN_QUESTIONS.md / OQ-ABIL-001`
* `OPEN_QUESTIONS.md / OQ-ABIL-002`
* `OPEN_QUESTIONS.md / OQ-ABIL-003`
* `OPEN_QUESTIONS.md / OQ-ABIL-004`
* `OPEN_QUESTIONS.md / OQ-ABIL-005`
* `OPEN_QUESTIONS.md / OQ-ABIL-006`
* `OPEN_QUESTIONS.md / OQ-ABIL-007`
* `OPEN_QUESTIONS.md / OQ-ABIL-008`

**Jelenlegi válasz / döntési irány:**

Az ability module rendszer hosszú távú célja, hogy az AETERNA kártyaképességei ne egyedi, kártyánként kézzel írt szabálykóddal működjenek, hanem fokozatosan structured adatokból, ability registryből, újrahasználható trigger / condition / target / cost / effect modulokból, diagnosticsból és későbbi execution planből épüljenek fel.

Alapelv:

**A kártyaszöveg emberi szabályszöveg. A structured ability és az ability registry a programlogikai köztes réteg.**

Az MVP-ben azonban nem cél minden kártya, minden keyword és minden komplex képesség teljes futtatása.

### Structured mezők szerepe

A jelenlegi structured mezők maradjanak kiindulási adat- és audit rétegként.

Rövid távú szerepük:

* audit;
* kereshetőség;
* engine support becslés;
* diagnostics;
* ability registry előkészítés;
* későbbi execution plan alapozása.

A structured mezők nem tekintendők automatikusan végleges execution modellnek.

Nem minden structured érték futtatható effect module.

Javasolt irány:

* ne vezessünk be azonnal sok új structured oszlopot;
* előbb structured audit + diagnostics készüljön;
* új `parameter`, `secondary_target`, `secondary_effect` vagy hasonló mező csak akkor kerüljön be, ha ismétlődő, tényleges execution igény igazolja;
* többértékű structured mezők sorrendi kapcsolata csak akkor számítson, ha explicit `ability_group`, `effect_order`, `target_ref` vagy hasonló kötés jelöli;
* általános Hatáscímke önmagában ne legyen futtatható logika;
* egy structured érték lehet csak auditcímke, ha túl általános vagy nem elég pontos engine-végrehajtáshoz.

### Execution plan

MVP-ben ne legyen kötelező minden kártyához teljes, előre generált execution plan.

Legyen három szint:

1. **Nincs execution plan** – csak structured adat / audit / support státusz.
2. **Simple execution plan minta** – néhány egyszerű abilityhez.
3. **Generated execution plan** – későbbi fázisban, ha a modulrendszer stabilabb.

Az execution plan hosszú távú szerepe:

* effect sorrend rögzítése;
* target és condition kapcsolat rögzítése;
* optional branch jelzése;
* partial resolution előkészítése;
* event log előkészítése;
* diagnostics előkészítése;
* Python és GDScript összehasonlítható végrehajtási alapja.

Javasolt irány:

* Python builder később generálhat execution plant;
* MVP-ben csak simple plan / plan stub kell;
* Godot első körben betölti és megjeleníti, nem feltétlenül futtatja teljes szabálymotorral;
* ha egy `supported` ability execution planje hibás, az build / publish error;
* ha egy `unsupported` abilityhez nincs plan, az nem plan-hiba, hanem support státusz;
* Python és GDScript hosszú távon ugyanazt a plan contractot használja, ha mindkét oldalon lesz executor.

### Card-local fallback

A card-local fallback azt jelenti, hogy egy kártya képessége nem általános modulokból, hanem egyedi kártyaspecifikus logikával futna.

A fallback átmeneti eszköz, nem hosszú távú alapműködés.

Javasolt irány:

* normál játékban / release candidate-ben ne legyen csendben engedett;
* Godot/GDScript normál runtime-ban ne fusson észrevétlenül;
* development/debug módban lehet `fallback_required`;
* AI-vs-AI fair tesztben fallback torzíthat, ezért alapból ne fusson, vagy külön jelölt debug AI mód kell hozzá;
* minden fallback legyen diagnostics entry;
* minden fallback jelenjen meg engine support reportban;
* debug módban fallback event is készülhet;
* készüljön fallback migrációs lista;
* hosszú távon minden fallback vagy modularizálandó, vagy explicit unsupported/manual státuszú.

### Reaction system ability szinten

A reaction rendszer ne tisztán ability module szinten éljen, hanem core rules timing / priority rendszer + ability hook modellben.

Javasolt modell:

* a core rules engine nyitja és zárja a reaction windowt;
* az ability module jelzi, milyen trigger / reaction / prevention / replacement lehetőséget ad;
* a legal action lista mutatja a játékosnak a választható reakciókat;
* az event log rögzíti a reaction window megnyílását, pass-t, választást és resolutiont.

MVP irány:

* reaction queue / pending reaction window;
* stack / chain nem MVP;
* Burst és Jel ugyanabba a reaction keretrendszerbe kerülhet, de külön subtype-pal;
* prevention és replacement ugyanahhoz a timing rendszerhez kapcsolódjon, de részletes szabály későbbi döntési kapu;
* trigger-sorrend és opcionális trigger kezelése későbbi rules audit / prototype feladat.

### Keywordök MVP-támogatása

MVP-ben ne próbáljuk mind a 10 alap keywordöt teljesen futtathatóvá tenni.

Első lépésben legyen keyword registry, amely:

* tárolja a keyword nevét;
* canonical ID-t ad;
* jelzi a support státuszt;
* jelzi, hogy statikus, combat, reaction, triggered vagy más jellegű;
* megmondja, kell-e külön event window;
* diagnosticsot ad unsupported vagy hiányos keyword esetén.

Alap keyword jelöltek:

* Gyorsaság
* Oltalom
* Hasítás
* Légies
* Métely
* Harmonizálás
* Rezonancia
* Visszhang
* Riadó
* Kényszerítés

Nem biztos, hogy mind MVP-supported legyen.

Javasolt irány:

* MVP: keyword registry + support_status;
* nem minden keyword kap teljes runtime supportot;
* combatfüggő keywordök későbbi combat prototype után;
* reactionfüggő keywordök reaction prototype után;
* unsupported keyword aktív deckben publish előtt blokkolhat;
* nem deckben lévő unsupported keyword development módban warning lehet.

### Pecsét / Aeternal ability targetek

A rögzített Aeternal / Pecsét modell maradjon szigorú.

Rögzített irány:

* Aeternal nem HP objektum.
* Aeternal nem kaphat sebzést.
* Aeternal nem gyógyítható.
* Pecsét nem HP objektum.
* Pecsét feltörési / visszaállítási eseményként kezelendő.
* Ha nincs védelem, egy célba érő támadás azonnali vereség.

Javasolt ability target irány:

* `own_aeternal` és `enemy_aeternal` ne legyen általános MVP target;
* Aeternalra csak explicit, nagyon speciális, szabályilag engedélyezett hatás mehessen;
* Aeternal soha nem damage / heal target;
* Pecsét target csak ward típusú effecteknél legyen engedett;
* támogatandó ward effectek:

  * `ward_break`
  * `ward_restore`
  * `ward_break_prevent`
* Pecsét targetnél `linked_current` kell, ha az Áramlat-kapcsolat szabályilag számít;
* régi HP-modellből származó effect aktív runtime-ban blocking diagnostics legyen.

Tiltott vagy kerülendő effect fogalmak:

* `damage_player`
* `player_damage`
* `damage_aeternal`
* `aeternal_damage`
* `heal_player`
* `heal_aeternal`
* `seal_damage`
* `ward_damage`
* `ward_hp_change`
* `seal_hp_change`

Helyettük támogatandó fogalmak:

* `ward_break`
* `ward_restore`
* `ward_break_prevent`
* `aeternal_unprotected`
* `direct_attack_victory`
* `player_defeated`

### Hatáscímkék szerepe

A Hatáscímkék rövid távon maradjanak audit / keresési / balance / engine support előjelző címkék.

Ne indítsanak önmagukban végrehajtási modult.

Egy Hatáscímke csak akkor válhat engine-supported effect module-lá, ha van hozzá:

* canonical `module_id`;
* input parameter schema;
* target / condition szabály;
* diagnostics szabály;
* event output minta;
* legal action kapcsolat, ha döntést igényel;
* legalább smoke test.

Javasolt irány:

* Effect_Tag nem azonos automatikus effect module-lal;
* túl általános Hatáscímke audit note legyen;
* effect tag sorrendje ne számítson szabálysorrendnek;
* végrehajtási sorrendet structured ability group / execution plan adja;
* effect tag alapján készülhet engine support report;
* Hatáscímke később module mapping alapja lehet, de csak külön validálás után.

### Ability registry és runtime package kapcsolat

Az ability registry legyen a runtime package része vagy közvetlenül ahhoz tartozó fájl.

Javasolt fájl:

* `ability_registry.json`

Az ability registry MVP-ben ne tartalmazzon teljes végrehajtási logikát.

MVP-ben elég, ha jelzi:

* melyik kártyán milyen ability van;
* `ability_id`;
* `source_card_id`;
* `ability_index`;
* `module_id` vagy structured hivatkozás;
* `support_status`;
* `execution_mode`;
* diagnostics hivatkozás;
* `fallback_required`;
* `manual_review_required`.

Javasolt irány:

* minden ability kapjon determinisztikus `ability_id` értéket;
* az `ability_id` ne függjön véletlenszerűen vagy gyakran változó mezőtől;
* minden `module_id` kapjon support státuszt;
* unsupported module szerepelhet registryben, de nem futhat csendben;
* Python builder számolja / validálja a support státuszokat;
* Godot loader első körben betölti és megjeleníti, később validálhat is;
* input parameter schema és output event lista későbbi bővítés.

### Execution mode és support status

Javasolt `execution_mode` értékek:

* `fully_modular`
* `partially_modular`
* `card_local_fallback`
* `manual_only`
* `unsupported`
* `not_checked`

Javasolt `support_status` értékek:

* `supported`
* `partial`
* `unsupported`
* `not_checked`
* `fallback_required`
* `manual_review_required`

Értelmezés:

* `fully_modular`: a képesség modulokból futtatható.
* `partially_modular`: részben futtatható, de van hiányzó vagy kézi rész.
* `card_local_fallback`: külön kártyaspecifikus logikát igényel.
* `manual_only`: engine nem futtatja, emberi játékban értelmezhető.
* `unsupported`: jelenlegi engine nem támogatja.
* `not_checked`: még nincs kiértékelve.

### MVP ability module scope

Az első MVP ability module rendszer ne próbáljon mindent lefedni.

Javasolt MVP cél:

* ability registry betöltése;
* support_status megjelenítése;
* unsupported / partial / fallback diagnostics;
* néhány egyszerű effect module;
* card reference resolution;
* simple legal action kapcsolat;
* event log stub;
* smoke test.

Lehetséges első effect module jelöltek:

* `draw_cards`
* `deal_damage_to_entity`
* `heal_entity`
* `ward_restore`
* `ward_break_prevent`
* `grant_keyword_until_end_of_turn`
* `create_token_simple`

Nem kell mindet egyszerre bevezetni.

Első biztonságos implementációs irány:

1. Ability registry pontosítása.
2. Engine support státuszok stabilizálása.
3. Diagnostics output javítása.
4. Egy-két egyszerű effect module kiválasztása.
5. Simple execution plan minta.
6. Event log stub.
7. Action request / response smoke kapcsolat.
8. Godot debug megjelenítés.
9. Python builder validáció.
10. Smoke test.

### Nem cél az MVP-ben

Nem cél első körben:

* teljes kártyaképesség rendszer;
* minden keyword teljes futtatása;
* minden trigger;
* teljes combat rendszer;
* teljes reaction stack;
* minden replacement / prevention;
* Síkok teljes folyamatos hatásrendszere;
* teljes AI értékelés;
* teljes balanszteszt;
* minden AETERNA kártya futtathatósága;
* card-local fallback véglegesítése.

**Indoklás:**

Az AETERNA kártyarendszere túl összetett ahhoz, hogy minden képesség azonnal futtatható modullá váljon. A túl korai teljes modularizálás valószínűleg sok hibás vagy túl általános modult eredményezne.

A biztonságosabb út az, ha először a registry, support státusz, diagnostics, fallback jelölés és néhány egyszerű effect module készül el. Így már mérhető lesz, mely kártyák futtathatók, melyek partial állapotúak, melyek unsupportedek, és melyek igényelnek kártyaauditot vagy új effect modult.

A structured mezők és Hatáscímkék megőrzik audit- és keresési értéküket akkor is, ha még nem futtathatók közvetlenül. Az ability registry pedig köztes réteget ad a kártyaadatbázis, runtime package, Godot loader, Python builder, diagnostics és későbbi rules executor között.

A card-local fallback átmenetileg hasznos, de ha csendben normál működéssé válna, akkor a rendszer elveszítené a modularizálás, tesztelhetőség és AI-vs-AI megbízhatóság előnyét.

Az Aeternal / Pecsét modell szigorú védelme azért fontos, mert a régi HP-alapú modell visszaszivárgása alapvető szabályhibákat okozna.

**Átvezetési célfájl:**

* `ABILITY_MODULE_SYSTEM.md`
* `RUNTIME_PACKAGE_SPECIFICATION.md`
* `CONTRACT_SPECIFICATION.md`
* `DECISION_MAP.md`
* szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:**

* `OQ-ABIL-001`: `partly_answered`
* `OQ-ABIL-002`: `partly_answered`
* `OQ-ABIL-003`: `partly_answered`
* `OQ-ABIL-004`: `partly_answered`
* `OQ-ABIL-005`: `partly_answered`
* `OQ-ABIL-006`: `partly_answered`
* `OQ-ABIL-007`: `partly_answered`
* `OQ-ABIL-008`: `partly_answered`

**Megjegyzés:**

Az ability module system alapmodell elfogadott. A pontos ability JSON schema, module_id lista, keyword registry mezők, első támogatott keywordök, első smoke effect module-ok és execution plan schema későbbi technikai specifikációs feladat marad.

---

## OQ-AI-001 / OQ-AI-002 / OQ-AI-003 / OQ-AI-004 / OQ-AI-005 / OQ-AI-006 / OQ-AI-007 – AI-vs-AI, fair AI, debug AI, balance testing és későbbi AI ellenfelek

**Forráskérdés:**

* `OPEN_QUESTIONS.md / OQ-AI-001`
* `OPEN_QUESTIONS.md / OQ-AI-002`
* `OPEN_QUESTIONS.md / OQ-AI-003`
* `OPEN_QUESTIONS.md / OQ-AI-004`
* `OPEN_QUESTIONS.md / OQ-AI-005`
* `OPEN_QUESTIONS.md / OQ-AI-006`
* `OPEN_QUESTIONS.md / OQ-AI-007`

**Jelenlegi válasz / döntési irány:**

Az AI-vs-AI és balance testing rendszert időben rétegezve kell kezelni.

Rövid távon a cél nem teljes játékosszerű mesterséges intelligencia, hanem rules-first, headless / smoke jellegű scenario és engine validation.

Hosszú távon viszont a cél valódi játékosszerű AI-vs-AI tesztelés, később különböző nehézségű AI ellenfelekkel, majd akár tanuló / önfejlesztő AI iránnyal.

### AI-vs-AI helye

Rövid és középtávon az AI-vs-AI tesztelés elsődleges helye Python legyen.

Indok:

* Python alkalmasabb batch futtatásra;
* könnyebb reportot, diagnosticsot és balance summaryt generálni;
* a runtime package build és validáció is Python oldalon erős;
* a Godot jelenleg inkább runtime package fogyasztó, debug UI és későbbi kliensréteg.

Godot / GDScript oldalon ne épüljön rögtön teljes párhuzamos AI-vs-AI rendszer.

Godot rövid távú szerepe:

* runtime package fogyasztás;
* debug UI;
* snapshot / legal action / event log megjelenítés;
* smoke test;
* későbbi játszható kliens.

Későbbi lehetőségek:

* Godot smoke AI;
* Godot debug bot;
* Python AI → GDScript rules service vezérlés;
* Python vs GDScript comparison test.

Javasolt irány:

* rövid táv: Python AI-vs-AI / scenario runner;
* Godot: debug megjelenítés, smoke, későbbi kliens;
* hosszú táv: Python backend + Godot kliens irány továbbra is lehetséges;
* hiteles balance csak akkor, ha a rules engine, legal action, event log, diagnostics és fair AI nézet stabil.

### Fair AI és debug AI

Legyen külön fair AI és debug AI mód.

Fair AI:

* ugyanazt a snapshotot látja, mint a játékos;
* ugyanazt a player-visible event logot látja;
* ugyanazt az enabled legal action listát kapja;
* nem lát rejtett információt;
* balanszméréshez ez az alap.

Debug AI:

* láthat teljesebb belső állapotot;
* használható engine-hibakeresésre;
* használható döntési heurisztika tesztelésére;
* használható comparison / smoke / debug futásokhoz;
* nem használható alapértelmezett balanszmérésre.

Javasolt irány:

* fair AI = játékosnézetű AI;
* debug AI = fejlesztői eszköz;
* balance report csak fair AI eredményt használjon alapértelmezésként;
* debug AI eredmények külön jelölést kapjanak.

### AI döntési heurisztika és legal actions

Az AI ugyanazt az enabled legal action listát kapja, mint a játékos.

Az AI ne hajthasson végre szabálytalan actiont akkor sem, ha rosszul dönt.

Az engine minden action requestet validál.

AI heuristic mező ne legyen MVP-követelmény a legal action contractban.

Az AI policy külön értékelje az actionöket.

Később lehet opcionális AI-segédadat, de csak akkor, ha:

* nem szivárogtat rejtett információt;
* fair / debug módban elkülönül;
* nem válik szabályforrássá;
* nem torzítja a balance mérést.

Javasolt irány:

* AI bemenet: snapshot + enabled legal actions + visible event log;
* AI döntés: action_id választás;
* engine validál;
* AI-hiba = rossz, de szabályos döntés;
* engine-hiba = szabálytalan action elfogadása vagy rossz állapotváltozás;
* kell AI decision log.

Javasolt `ai_decision_log` mezők:

* `decision_id`
* `match_id`
* `turn`
* `phase`
* `state_version`
* `snapshot_id`
* `ai_mode`
* `policy_id`
* `visible_inputs_ref`
* `candidate_action_ids`
* `chosen_action_id`
* `score_summary`
* `reason`
* `random_seed`
* `result_status`
* `diagnostics_ref`

### AI nehézségi szintek

Hosszú távon szükség lesz különböző nehézségű AI ellenfelekre.

Ez nem MVP-követelmény, de már most érdemes irányként rögzíteni.

Lehetséges AI nehézségi szintek:

* `tutorial_ai`
* `easy_ai`
* `normal_ai`
* `hard_ai`
* `expert_ai`
* `debug_ai`
* `fair_balance_ai`

Lehetséges különbségek a szintek között:

* mennyire néz előre;
* mennyire értékeli jól a board state-et;
* mennyire kezeli jól a kézben lévő lapokat;
* mennyire használja jól az Aurát;
* mennyire agresszív vagy defenzív;
* mennyire kerüli a rossz cseréket;
* felismeri-e a lethal / direct attack victory lehetőséget;
* mennyire használja jól a reakciókat;
* használ-e deck- vagy klánspecifikus stratégiát;
* véletlenszerűséggel gyengíthető-e;
* szándékosan kihagyhat-e bonyolult döntéseket kezdő szinten.

Fontos korlátozás:

A nehézség növelése nem jelenthet rejtett információhoz való hozzáférést fair módban.

A nehéz AI is csak azt láthatja, amit egy játékos szabályosan láthatna, kivéve külön debug AI módban.

### Tanuló / önfejlesztő AI hosszú távon

Hosszú távú irányként elképzelhető olyan AI, amely tanul a saját hibáiból, elemzi korábbi döntéseit, és javítja a policy-ját.

Ez későbbi kutatási / prototípus téma, nem MVP és nem korai balance pipeline követelmény.

Lehetséges későbbi irányok:

* meccs utáni döntéselemzés;
* rossz döntések megjelölése;
* AI decision log alapján policy tuning;
* matchup-specifikus tanulás;
* deck-specifikus tanulás;
* reinforcement learning jellegű kísérlet;
* self-play alapú stratégiafejlesztés;
* emberi review által javított döntési minták.

Korlátozások:

* a tanuló AI nem módosíthatja a szabályokat;
* a tanuló AI nem írhatja felül a kártyaadatokat;
* a tanulás eredménye külön policy / model / config réteg legyen;
* balance reportban mindig jelölni kell, milyen AI policy futott;
* tanuló AI eredményei nem keverhetők össze determinisztikus smoke tesztekkel;
* fair balance mérésnél csak rögzített, verziózott AI policy eredménye legyen összehasonlítható.

Javasolt későbbi policy mezők:

* `policy_id`
* `policy_version`
* `difficulty_level`
* `learning_enabled`
* `training_source`
* `random_seed`
* `evaluation_profile`
* `allowed_information_mode`
* `deck_strategy_profile`
* `risk_profile`

### Balance suspicion forrása

Balance suspicion ne csak winrate alapján keletkezzen.

Forrásai lehetnek:

* winrate;
* matchup eredmény;
* deck pattern;
* card usage;
* túl gyakori ward break;
* túl gyors győzelem;
* túl sok vagy túl kevés húzás / dobás;
* túl domináns keyword;
* túl gyakori reaction lock;
* túl sok `not_executable` / fallback / unsupported eset;
* játék hossza;
* victory reason;
* player decision count;
* card-specific impact.

Javasolt irány:

* balance suspicion több adatból álljon;
* winrate önmagában csak jelzés;
* előbb engine / deck / AI / support hiba kizárása kell;
* suspicion vonatkozhat kártyára, deckre, klánra, birodalomra, matchupra vagy mechanikára.

### Winrate és klánidentitás

A cél nem steril 50/50 balansz.

A klánidentitás fontos.

Az erős, karakteres klánirány önmagában nem hiba.

A 40–60 winrate-sáv csak kezdeti figyelési elv, nem végleges matematikai szabály.

Javasolt ideiglenes értelmezés:

* 40–60%: normál figyelési sáv;
* 35–65% kívül: figyelendő;
* 30–70% kívül: erős gyanú;
* 25–75% kívül: magas prioritású audit, ha a minta elég nagy és engine / deck / AI hiba kizárható.

Identitásalapú előny önmagában nem hiba.

Egy klán lehet természetesen erős bizonyos lassú kontroll ellen, ha közben más matchupban sebezhető.

Javasolt irány:

* nem cél minden matchup 50/50-re húzása;
* klánidentitás védendő;
* túl egyoldalú matchup csak akkor hiba, ha nincs ellenjáték, túl gyakori vagy identitást rombol;
* kerülni kell a tiszta kő-papír-olló rendszert;
* balance suspicion mindig emberi értelmezést igényel.

### Balance report

Legyen később külön `balance_report` contract.

Ez ne legyen teljes MVP-követelmény.

A balance report formája hosszú távon:

* gépi JSON;
* emberi Markdown summary.

Javasolt fájlok:

* `balance_report.json`
* `balance_summary.md`

Különüljön el:

* meccsenkénti raw / stat report;
* összesített report;
* matchup summary;
* card usage summary;
* deck performance summary;
* suspicion list;
* AI policy / difficulty / seed adatok;
* unsupported / fallback torzítás jelzése.

Javasolt irány:

* `balance_report.json` későbbi gépi output;
* `balance_summary.md` későbbi emberi összefoglaló;
* report regenerálható output legyen;
* fontosabb eredmények később checkpointban röviden hivatkozhatók;
* ne legyen kézzel szerkesztett canonical forrás.

### Korábbi kártyajavítások visszaellenőrzése

A korábbi kártyajavítások teljes visszaellenőrzése ne induljon el most.

Előfeltételek:

* stabil runtime package;
* legal action rendszer;
* event log;
* diagnostics;
* ability support report;
* legalább részben fair AI-vs-AI;
* decklisták validálása;
* unsupported / fallback lapok elkülönítése.

Javasolt irány:

* visszaellenőrzés későbbi balance / audit fázis;
* addig a korábbi javított lapok kapjanak `review_candidate` vagy hasonló jelölést;
* első körben csak engine support / structured / diagnostics ellenőrzés;
* balance visszateszt csak fair AI-vs-AI után.

### Mikor alkalmas az engine balansztesztre?

Az engine akkor tekinthető balance-test ready állapotúnak, ha legalább ezek teljesülnek:

* minden tesztdeck validált;
* runtime package stabil;
* legal actions engine-oldalon készülnek;
* fair AI nem lát rejtett információt;
* event logból kinyerhető a match history;
* diagnostics elkülöníti engine / deck / AI / support hibákat;
* unsupported / fallback lapok nem torzítják csendben a tesztet;
* legalább alap victory condition működik;
* legalább alap combat / ward / draw / play card folyamat működik;
* AI decision log készül;
* ismételhető futás van seed alapján;
* az AI policy verziózott és az eredményekben hivatkozott.

Addig az eredmények inkább simulation smoke / scenario validation eredmények, nem valódi balanszmérések.

**Indoklás:**

Az AI-vs-AI rendszer hosszú távon kulcsfontosságú lesz az AETERNA tesztelésében, de csak akkor ad értelmes balanszadatot, ha az engine, a legal action rendszer, a visibility, az event log és a diagnostics stabil.

A fair AI és debug AI szétválasztása azért fontos, mert a debug AI hasznos hibakeresésre, de ha rejtett információt lát, akkor nem modellezi a valódi játékoshelyzetet. A balanszméréshez játékosnézetű fair AI kell.

A különböző nehézségű AI ellenfelek később a játszható digitális klienshez is fontosak lesznek, de nem keverendők össze az engine-validációval. Egy könnyű AI szándékosan hozhat gyengébb döntéseket, míg egy balance AI-nak konzisztens, fair és verziózott policy alapján kell játszania.

A tanuló / önfejlesztő AI érdekes hosszú távú irány, de csak akkor kezelhető biztonságosan, ha a tanulási eredmény külön policy rétegben marad, és nem módosítja sem a szabályokat, sem a kártyaadatokat. A tanuló AI eredményeit külön kell kezelni a determinisztikus smoke tesztektől és a reprodukálható balance reportoktól.

A winrate önmagában nem elég balanszítélethez. A klánidentitás, matchup jelleg, card usage, játékidő, victory reason, event log és diagnostics együtt adhatnak értelmezhető képet.

**Átvezetési célfájl:**

* `DECISION_MAP.md`
* `TECHNOLOGY_DECISIONS.md`
* `CONTRACT_SPECIFICATION.md`
* `RUNTIME_PACKAGE_SPECIFICATION.md`
* `PROTOTYPE_PLANS.md`
* szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:**

* `OQ-AI-001`: `partly_answered`
* `OQ-AI-002`: `answered`
* `OQ-AI-003`: `partly_answered`
* `OQ-AI-004`: `partly_answered`
* `OQ-AI-005`: `partly_answered`
* `OQ-AI-006`: `partly_answered`
* `OQ-AI-007`: `partly_answered`

**Megjegyzés:**

Az AI / simulation / balance testing alapmodell elfogadott. A pontos AI policy schema, AI difficulty profilok, bot-szintek, tanuló AI prototípus, mintaszámküszöbök, balance report schema és első fair AI-vs-AI benchmark későbbi technikai specifikációs feladat marad.

---

## OQ-RULES-001 / OQ-RULES-002 / OQ-RULES-003 / OQ-RULES-004 / OQ-RULES-005 / OQ-RULES-006 / OQ-RULES-007 – Rules audit, főforrás-audit, structured audit és kártyaaudit időzítése

**Forráskérdés:**

* `OPEN_QUESTIONS.md / OQ-RULES-001`
* `OPEN_QUESTIONS.md / OQ-RULES-002`
* `OPEN_QUESTIONS.md / OQ-RULES-003`
* `OPEN_QUESTIONS.md / OQ-RULES-004`
* `OPEN_QUESTIONS.md / OQ-RULES-005`
* `OPEN_QUESTIONS.md / OQ-RULES-006`
* `OPEN_QUESTIONS.md / OQ-RULES-007`

**Jelenlegi válasz / döntési irány:**

Most ne induljon teljes főforrás-audit vagy új teljes kártyaaudit.

Előbb stabilabb validációs, runtime package, LOOKUPS, structured, diagnostics, ability registry és engine support réteg kell.

A rules audit és card audit munkákat rétegezve kell kezelni:

1. adatút és runtime package stabilizálás;
2. LOOKUPS / structured critical audit;
3. diagnostics és engine support report;
4. ability registry és support státuszok;
5. engine-barát szabályspecifikáció;
6. célzott Aeternal / Pecsét / timing / target / payment rules audit;
7. scenario runner / smoke test;
8. korábbi javított lapok visszaellenőrzése;
9. később teljes kártyaaudit;
10. még később játékosbarát szabálykönyv.

### Hivatalos főforrás-audit

A két hivatalos 1.4v főforrás teljes auditja ne most induljon el nagy munkaként.

Előtte szükséges:

* stabil runtime package adatút;
* LOOKUPS / structured normalizálás;
* diagnostics report;
* ability support report;
* legal action / event log / snapshot contract;
* Aeternal / Pecsét engine-modell;
* legalább részleges rules validation layer.

Javasolt irány:

* rövid távon nincs teljes főforrás-audit;
* kisebb célzott szabályi kérdések továbbra is vizsgálhatók;
* teljes audit csak validation layer után;
* audit elsődleges célja: engine-barát tisztázás és szabályellentmondások feltárása;
* játékosbarát szöveg csak későbbi réteg legyen;
* a hivatalos DOCX főforrások egyelőre maradhatnak hivatalos szabályforrásként.

### Játékosbarát szabálykönyv időzítése

A játékosbarát szabálykönyv ne most készüljön végleges formában.

Előtte szükséges:

* főforrás-audit;
* engine-barát szabályspecifikáció;
* pályamodell és Pecsétmodell lezárása;
* fázisok / akcióablakok / reakciók tisztázása;
* legalább minimális játszható prototípus vagy debug flow;
* alap példák és vizuális pályamagyarázat előkészítése.

Javasolt irány:

* játékosbarát szabálykönyv későbbi dokumentum;
* külön dokumentum legyen;
* tartalmazzon példákat;
* tartalmazzon vizuális pályamagyarázatot;
* kezdőknek is érthető, de szabályilag pontos legyen;
* először MD alap, később DOCX / PDF export lehet;
* ne váljon engine-spec forrássá.

### Engine / AI / Codex-barát szabályspecifikáció

Később készüljön külön engine-barát szabályspecifikáció.

Ez MD-alapú legyen.

A hivatalos főforrásból származzon, de ne helyettesítse a hivatalos főforrást.

Tartalmaznia kell majd:

* fázisokat;
* stepeket;
* prioritást;
* akcióablakokat;
* reakcióablakokat;
* célpontválasztást;
* fizetést;
* triggerablakokat;
* Pecsét / Aeternal állapotot;
* győzelmi feltételeket;
* legal action generálás szabályait;
* action request / response szabályi kapcsolatát;
* event loghoz kötött szabályi eseményeket;
* diagnostics szempontból kritikus szabályi hibákat.

Javasolt irány:

* igen, kell engine-barát rules spec;
* MD alapú legyen;
* hivatalos főforrásból származzon;
* Codex számára később készülhet rövidebb implementációs kivonat;
* csak auditált / elfogadott szabálypont kerüljön bele végleges formában;
* később a rules engine egyik fő implementációs forrása lehet;
* ne legyen játékosbarát magyarázó szabálykönyvvel összekeverve.

### Új teljes kártyaaudit időzítése

Ne induljon most új teljes kártyaaudit.

Előfeltételek:

* stabil runtime package builder;
* LOOKUPS / structured audit első köre;
* diagnostics report;
* engine support report;
* ability registry;
* decklist validáció;
* legal action / event log alap;
* legalább részleges fair AI-vs-AI vagy scenario runner;
* korábbi javítások listája `review_candidate` vagy hasonló jelöléssel.

Javasolt irány:

* teljes kártyaaudit később;
* elsőként structured / support / diagnostics alapú előszűrés legyen;
* utána hibakategóriánként vagy engine-risk alapján induljon;
* nem birodalmonkénti nagy manuális audit legyen az első lépés;
* birodalom / klán audit később jöhet, ha a validációs réteg már jelzi a problémákat;
* balanszaudit előtt működő tesztelési / validációs réteg szükséges.

### LOOKUPS és structured audit időzítése

A LOOKUPS / structured audit indulhat hamarabb, mint a teljes kártyaaudit.

Ez a runtime package és ability module rendszer alapja.

Ne „mindent egyszerre” audit legyen, hanem lépcsőzetes munka.

Javasolt sorrend:

1. **Critical runtime enums**

   * card type;
   * realm;
   * clan;
   * cost;
   * magnitude;
   * zone;
   * rarity;
   * target;
   * effect;
   * trigger.

2. **Dangerous / legacy / workflow-only értékek**

   * legacy alias;
   * inactive;
   * workflow-only;
   * audit_required;
   * dangerous alias;
   * Label_HU / Value keveredés;
   * Canonical_Value eltérés.

3. **Structured engine mapping**

   * trigger;
   * target;
   * effect;
   * cost;
   * condition;
   * duration;
   * keyword.

Javasolt irány:

* LOOKUPS / structured audit első köre indulhat a teljes kártyaaudit előtt;
* a Value / Label_HU / Canonical_Value irány alapvetően elfogadott;
* aktív runtime értékeknél Canonical_Value egyezzen a Value-val;
* legacy alias réteg csak fokozatosan zárható;
* dangerous / audit_required lista legyen korai feladat;
* első engine támogatáshoz legfontosabb structured mezők:

  * trigger;
  * target;
  * effect;
  * cost;
  * condition;
  * keyword.

### Kártyaszöveg és structured adat eltérései

Engine szempontból a structured / runtime adat csak akkor lehet végrehajtási forrás, ha auditált és konzisztens a kártyaszöveggel.

Alapértelmezett irány:

* hivatalos emberi szabályszöveg a design / szabályi forrás;
* structured adat a programlogikai köztes réteg;
* runtime engine csak validált structured / ability registry adatból dolgozhat;
* eltérés esetén a motor ne találgasson.

Javasolt hibakezelés:

| Eltérés                                             | Javasolt kezelés                                               |
| --------------------------------------------------- | -------------------------------------------------------------- |
| Kártyaszöveg jó, structured hiányos                 | `audit_note` vagy `warning`; engine-supported nem lehet teljes |
| Structured jó, kártyaszöveg félrevezető             | kártyaaudit szükséges; publish előtt javítandó                 |
| Structured runtime-critical mező hibás              | `error`, publish blocking                                      |
| Nem futtatott / nem deckben lévő structured eltérés | development warning                                            |
| Hatáscímke túl általános                            | audit note                                                     |
| Runtime engine nem tudja eldönteni                  | `manual_review_required`                                       |

Javasolt irány:

* engine nem találgat;
* kártyaszöveg és structured eltérés mindig diagnostics;
* runtime-supported státusz csak konzisztens adatnál adható;
* javítás történhet kártyaszövegben, structured mezőben vagy mindkettőben;
* active deck / publish esetén runtime-critical eltérés blokkolhat;
* ha a structured adat csak auditcímke, nem szabad futtatható effectként kezelni.

### Aeternal / Pecsét engine-specifikáció

Az alapmodell már elfogadott, de a részletes engine-spec még külön feladat.

Rögzített irány:

* Az Aeternal maga a játékos.
* Az Aeternal nem rendelkezik HP-val.
* Az Aeternal nem kaphat sebzést.
* Az Aeternal nem gyógyítható.
* A Pecsét nem HP-alapú objektum.
* A Pecsét feltörési / visszaállítási eseményként kezelendő.
* Ha nincs Entitás és Pecsét, ami véd, egy célba érő támadás azonnali vereséget jelent.

Javasolt engine irány:

* `own_aeternal` / `enemy_aeternal` csak erősen korlátozott target lehet;
* Aeternal nem damage / heal target;
* Pecsét event type-ok:

  * `ward_broken`
  * `ward_restored`
  * `ward_break_prevented`
  * `aeternal_unprotected`
  * `direct_attack_victory`
  * `player_defeated`
* combatból és effectből származó `ward_break` ugyanazt az alap event type-ot használhatja, de payloadban jelölje az eredetet:

  * `source_context: combat`
  * `source_context: effect`
* Pecsét visszaállítás effect / action / event modellje későbbi részspec;
* snapshotban legyen jelölhető, ha egy játékos Aeternálja védtelen, például:

  * `aeternal_unprotected: true`
  * vagy `direct_attack_victory_available: true`.

### Javasolt audit sorrend

A javasolt munka- és audit sorrend:

1. Runtime package builder stabilizálás.
2. LOOKUPS / structured critical audit.
3. Diagnostics report és engine support report.
4. Ability registry / support_status pontosítása.
5. Engine-barát rules spec váz.
6. Aeternal / Pecsét engine-spec részletezés.
7. Fázis / action window / reaction / target / payment rules spec.
8. Scenario runner / smoke tesztek.
9. Korábbi javított lapok engine-support visszaellenőrzése.
10. Később teljes kártyaaudit.
11. Még később játékosbarát szabálykönyv.

**Indoklás:**

A teljes főforrás-audit és teljes kártyaaudit túl nagy és túl korai lenne a jelenlegi állapotban. Ha ezek stabil runtime package, LOOKUPS, structured, diagnostics és engine support nélkül indulnak, akkor sok manuális munka keletkezne, amelyet később újra kellene ellenőrizni.

A LOOKUPS / structured audit viszont közvetlenül támogatja a runtime package-et, az ability registryt, az engine support reportot és a diagnostics rendszert, ezért ezt érdemes korábban, de lépcsőzetesen indítani.

Az engine-barát szabályspec azért kell külön, mert a hivatalos főforrás emberi szabálydokumentum, nem közvetlen implementációs specifikáció. A rules engine, Codex, AI és diagnostics számára pontosabb, strukturáltabb, MD-alapú szabályspec kell majd.

A játékosbarát szabálykönyv ezzel szemben nem implementációs forrás, hanem későbbi magyarázó dokumentum. Akkor lesz hasznos, ha a szabálymodell már stabilabb, és a pálya, fázisok, reakciók, Pecsétmodell és győzelmi feltételek már tiszták.

A kártyaszöveg és structured adat eltéréseit nem szabad runtime találgatással kezelni. A motor csak validált structured / ability registry adatból dolgozhat, eltérés esetén diagnostics és szükség esetén emberi audit kell.

**Átvezetési célfájl:**

* `DECISION_MAP.md`
* `ARCHITECTURE.md`
* `RUNTIME_PACKAGE_SPECIFICATION.md`
* `ABILITY_MODULE_SYSTEM.md`
* `CONTRACT_SPECIFICATION.md`
* később: engine-barát rules spec dokumentum
* szükség esetén később: `OPEN_QUESTIONS.md`

**Javasolt OPEN_QUESTIONS státusz:**

* `OQ-RULES-001`: `partly_answered`
* `OQ-RULES-002`: `partly_answered`
* `OQ-RULES-003`: `partly_answered`
* `OQ-RULES-004`: `partly_answered`
* `OQ-RULES-005`: `partly_answered`
* `OQ-RULES-006`: `partly_answered`
* `OQ-RULES-007`: `partly_answered`

**Megjegyzés:**

A rules audit és card audit timing alapmodell elfogadott. A teljes főforrás-audit, játékosbarát szabálykönyv, engine-barát rules spec részletes tartalomjegyzéke, structured audit konkrét munkalistája és új teljes kártyaaudit későbbi külön tervezési feladat marad.

