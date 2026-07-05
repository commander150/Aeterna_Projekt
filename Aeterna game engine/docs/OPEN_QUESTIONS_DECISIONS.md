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
