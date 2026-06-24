# AETERNA Game Engine – Open Questions

Ez a fájl az AETERNA Game Engine dokumentációiban szereplő nyitott kérdések és döntési kapuk központi nyilvántartása.

Célja, hogy a DOCX → MD migráció és dokumentum-összevonás során egyetlen megválaszolandó kérdés se vesszen el.

Ez nem döntési dokumentum, hanem döntés-előkészítő kérdéslista.

---

## Státuszok

| Státusz | Jelentés |
|---|---|
| `open` | Még nincs megválaszolva. |
| `partly_answered` | Részben már van irány, de nincs végleges döntés. |
| `deferred` | Későbbi fázisra halasztva. |
| `blocked_by_prototype` | Prototípus vagy teszt kell a válaszhoz. |
| `blocked_by_rules_audit` | Szabályforrás-audit szükséges. |
| `blocked_by_data_audit` | Kártyaadat / LOOKUPS / structured audit szükséges. |
| `blocked_by_engine_test` | Engine vagy smoke test szükséges. |
| `answered` | Megválaszolva és átvezetve. |
| `obsolete` | Már nem aktuális. |

---

# 1. Projektirány és célarchitektúra

## OQ-ARCH-001 – Régi Python motor sorsa

**Státusz:** `open`, `blocked_by_engine_test`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`, `ARCHITECTURE.md`

Kérdések:

- A régi Python motor hosszú távon backenddé alakítható?
- Új tiszta Python backend készüljön?
- GDScript/Godot runtime irány legyen a fő?
- A Python csak adatpipeline / validáció / AI-vs-AI / referencia szerepben maradjon?
- Mely részek menthetők át a régi motorból?
- Milyen ponton jobb az újraírás, mint a refaktor?

---

## OQ-ARCH-002 – Python / GDScript / hibrid modell

**Státusz:** `open`, `blocked_by_prototype`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`

Kérdések:

- GDScript alkalmas-e hosszú távú fő runtime engine-nek?
- Python maradjon-e AI-vs-AI tesztmotor?
- Legyen-e Python tesztmotor + GDScript játékengine hibrid?
- Ha két motor él, hogyan ellenőrizzük, hogy ugyanazt csinálják?
- Kell-e Python ↔ GDScript event log összehasonlító teszt?

---

## OQ-ARCH-003 – UI és rules engine szétválasztása

**Státusz:** `open`, `blocked_by_prototype`  
**Célfájl:** `ARCHITECTURE.md`, `TECHNOLOGY_DECISIONS.md`

Kérdések:

- Hogyan biztosítjuk, hogy a Godot UI ne tartalmazzon szabálylogikát?
- Milyen réteg legyen a `rules_service`?
- A Godot UI csak action requestet küldjön?
- Milyen contract választja el az inputot a szabálymotortól?

---

# 2. Dokumentáció és fájlkezelés

## OQ-DOC-001 – DOCX → Markdown migráció

**Státusz:** `partly_answered`  
**Célfájl:** `DECISION_MAP.md`

Kérdések:

- Mely dokumentumok legyenek aktív Markdown fájlok?
- Mely DOCX-ek maradjanak archív eredetik?
- A hivatalos szabályfőforrások maradjanak-e DOCX-ben?
- Készüljön-e később exportált DOCX/PDF olvasói változat?
- A jövőbeli frissítések mindig meglévő MD fájlba kerüljenek-e új fájl helyett?

---

## OQ-DOC-002 – Checkpointok kezelése

**Státusz:** `partly_answered`  
**Célfájl:** `CHECKPOINTS.md`

Kérdések:

- Minden checkpoint egyetlen `CHECKPOINTS.md` fájlba kerüljön?
- A checkpoint fájl a gyökérben vagy `docs/checkpoints/` alatt legyen?
- A régi checkpoint DOCX-ek státusza `MERGED_TO_MD` legyen-e?
- A checkpoint tartalmazzon-e csak rövid tényeket, vagy részletes technikai naplót is?

---

## OQ-DOC-003 – Dokumentumszaporodás elkerülése

**Státusz:** `partly_answered`  
**Célfájl:** `DECISION_MAP.md`

Kérdések:

- Milyen esetben készülhet új dokumentum?
- Mikor kell meglévő dokumentumba beépíteni az új tartalmat?
- Mi legyen az átmeneti munkatervek sorsa?
- Törölhetők-e az átmeneti merge-tervek, ha a tartalom átkerült?

---

# 3. Runtime package és adatút

## OQ-DATA-001 – Compiled runtime package szükségessége

**Státusz:** `open`  
**Célfájl:** `RUNTIME_PACKAGE_SPECIFICATION.md`

Kérdések:

- A program hosszú távon csak compiled runtime package-ből dolgozzon?
- A nyers exportok közvetlenül is futtathatók legyenek?
- Mikor váljon kötelezővé a manifestes package?
- A nyers export csak köztes réteg legyen?

---

## OQ-DATA-002 – Google Sheets → XLSX → exportáló → package adatút

**Státusz:** `partly_answered`  
**Célfájl:** `RUNTIME_PACKAGE_SPECIFICATION.md`

Jelenlegi irány:

- A fő szerkesztés Google Sheetsben történik.
- A lokális XLSX a Google Sheetsből letöltött forrás.
- Az `XLSX export/` mappán belüli `.xlsx` fájlok másolatok / pipeline inputok.
- Az exportáló később közvetlenül is olvashat canonical lokális forrásmappából.

Nyitott kérdések:

- Pontosan hol legyen a canonical lokális XLSX helye?
- Kell-e hosszú távon `XLSX export/source/` másolat?
- Az exportáló által készített outputok regenerálható fájlok vagy verziózott referencia-outputok legyenek?
- Mikor épül be az új input-mód az exportálóba?

---

## OQ-DATA-003 – Engine support státusz

**Státusz:** `open`, `blocked_by_engine_test`  
**Célfájl:** `RUNTIME_PACKAGE_SPECIFICATION.md`, `ABILITY_MODULE_SYSTEM.md`

Kérdések:

- Az `unsupported` kártya blokkolja-e a package buildet?
- Csak akkor blokkoljon, ha deckben szerepel?
- `partial` státusz warning vagy audit note legyen?
- Card-local fallback megengedett-e AI-vs-AI tesztben?
- Godot runtime esetén unsupported effect mit okozzon?

---

## OQ-DATA-004 – Legacy alias és canonical értékek

**Státusz:** `open`, `blocked_by_data_audit`  
**Célfájl:** `RUNTIME_PACKAGE_SPECIFICATION.md`

Kérdések:

- A legacy alias automatikusan canonical értékre forduljon?
- A veszélyes alias mindig audit note legyen?
- Mikor legyen blocking error?
- A canonical javítás visszakerüljön-e a forrásadatba?
- Régi Aeternal/Pecsét HP-modellre utaló értékek automatikusan tiltottak legyenek?

---

# 4. Snapshot contract

## OQ-SNAP-001 – Snapshot típusok

**Státusz:** `open`, `blocked_by_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Kell-e külön `opponent_visible_snapshot`?
- Elég-e a `player_visible_snapshot` viewer alapján?
- Mikor kell `spectator_snapshot`?
- A debug snapshot tartalmazhat-e teljes paklisorrendet?
- AI-hoz kell-e külön `ai_fair_snapshot` és `ai_debug_snapshot`?

---

## OQ-SNAP-002 – Pecsétmodell snapshotban

**Státusz:** `open`, `blocked_by_rules_audit`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- A Pecsét snapshotban lapként, védelmi objektumként vagy mindkettőként jelenjen meg?
- A feltört Pecsét hová kerül?
- Kell-e `linked_current` minden Pecsétre?
- A Pecsét neve látható-e?
- A Pecsét soha ne kapjon HP mezőt?

---

## OQ-SNAP-003 – Ősforrás láthatóság

**Státusz:** `open`, `blocked_by_rules_audit`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Az Ősforrás lapjai publikusak?
- Az ellenfél mit lát az Ősforrásból?
- Kell-e used/exhausted állapot minden Ősforrás-lapra?
- Az Aura forrása látszódjon-e?

---

## OQ-SNAP-004 – Rejtett információ

**Státusz:** `open`, `blocked_by_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Mit lát az ellenfél a face-down Jelekből?
- Ellenfél kézlapjai hogyan jelenjenek meg?
- Deck teteje debugon kívül soha nem látható?
- Fair AI pontosan ugyanazt lássa, mint egy játékos?

---

# 5. Legal action contract

## OQ-LA-001 – Enabled és disabled actionök

**Státusz:** `open`, `blocked_by_ui_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Normál játékban csak enabled actionök jelenjenek meg?
- Debug módban jelenjenek meg disabled actionök is?
- Tutorial módban kell-e disabled reason?
- A legal action lista tartalmazzon-e UI-segédadatokat?

---

## OQ-LA-002 – Reakcióablak modell

**Státusz:** `open`, `blocked_by_rules_audit`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `ABILITY_MODULE_SYSTEM.md`

Kérdések:

- Elég reaction queue?
- Kell stack / chain jellegű modell?
- Burst és Jel ugyanabban a reaction rendszerben legyen?
- Pass reaction külön action legyen?
- Reakcióablak automatikusan átugorható, ha nincs valódi döntés?

---

## OQ-LA-003 – Fizetés és Aura

**Státusz:** `open`, `blocked_by_rules_audit`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Meddig legyen automatikus Aura-fizetés?
- Mikor kell kézi forrásválasztás?
- Ideiglenes Aura elsőként vagy utolsóként költődjön?
- Alternatív költségek mikor kerüljenek be?

---

## OQ-LA-004 – Targeting

**Státusz:** `open`, `blocked_by_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Célpontválasztás külön action legyen?
- Vagy a play action része?
- Több célpontnál hogyan kezeljük a sorrendet?
- Invalid target esetén teljes vagy részleges feloldás legyen?

---

# 6. Action request / response

## OQ-AR-001 – Request azonosítás és stale snapshot

**Státusz:** `open`, `deferred`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Kötelező legyen-e a `client_request_id`?
- Kell-e `state_version` már MVP-ben?
- Elavult snapshot esetén mindig reject legyen?
- Vagy a backend próbálja újravalidálni az actiont?

---

## OQ-AR-002 – Action ID élettartama

**Státusz:** `open`, `deferred`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Az action ID csak snapshoton belül stabil?
- Hosszabb életű action token kell?
- Ha a legal action lista frissül, mikor érvénytelenedik a régi action ID?

---

## OQ-AR-003 – Partial resolution

**Státusz:** `open`, `blocked_by_rules_examples`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Mikor legyen `partially_resolved`?
- Mikor legyen `failed`, `cancelled`, `prevented`, `replaced`?
- Feltételes ág kimaradása normál result, info vagy warning?
- Részleges feloldás mikor jelent valódi hibát?

---

# 7. Event log contract

## OQ-EVENT-001 – Event részletesség

**Státusz:** `open`, `blocked_by_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Mennyire legyen részletes az MVP event log?
- Minden belső engine lépés event legyen?
- Csak gameplay szintű események legyenek?
- Debug eventek külön rétegben legyenek?

---

## OQ-EVENT-002 – Explanation log

**Státusz:** `open`, `blocked_by_ui_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Minden komplex eseményhez kell magyar magyarázat?
- Csak reakció / replacement / prevention / részleges feloldás esetén?
- `message_hu` backendben készüljön?
- Vagy frontend lookup generálja?

---

## OQ-EVENT-003 – Event log és rejtett információ

**Státusz:** `open`, `blocked_by_visibility_rules`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Egyetlen belső event logból szűrjünk viewer szerint?
- Vagy külön event log készüljön nézőpontonként?
- PvP előtt kell-e külön biztonsági szűrő?
- AI fair event log hogyan különüljön el?

---

## OQ-EVENT-004 – Replay

**Státusz:** `deferred`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- MVP-ben kell replay-kompatibilitás?
- Kell-e action history az event log mellé?
- Kell-e snapshot checkpoint replay gyorsításhoz?
- Replayhez teljes vagy szűrt event log kell?

---

# 8. Diagnostics contract

## OQ-DIAG-001 – Severity és blocking rendszer

**Státusz:** `open`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

Kérdések:

- Kell külön `critical`, vagy elég az `error + blocking = true`?
- A `balance_suspicion` severity vagy category legyen?
- Az `audit_note` severity vagy workflow státusz?
- Mely severity látszódjon runtime közben?

---

## OQ-DIAG-002 – Report formátum

**Státusz:** `open`, `blocked_by_runtime_package_builder`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `RUNTIME_PACKAGE_SPECIFICATION.md`

Kérdések:

- Egy nagy diagnostics report legyen?
- Vagy külön export, runtime, engine, audit és balance report?
- JSON, JSONL vagy Markdown formátum kell?
- Runtime package tartalmazza az összes diagnosticot vagy csak summaryt?

---

## OQ-DIAG-003 – LOOKUPS diagnostics

**Státusz:** `open`, `blocked_by_data_audit`  
**Célfájl:** `RUNTIME_PACKAGE_SPECIFICATION.md`

Kérdések:

- `audit_required` érték aktív runtime kártyán mikor blokkoljon?
- Legacy alias automatikusan javítható?
- Inactive érték aktív kártyán warning vagy error?
- Label_HU és Value keveredése mikor blocking?

---

# 9. Ability module system

## OQ-ABIL-001 – Structured mezők részletessége

**Státusz:** `open`, `blocked_by_data_audit`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`

Kérdések:

- A mostani structured mezők elég részletesek?
- Kell külön parameter mező?
- Kell secondary target / secondary effect?
- Többértékű mezők hogyan kapcsolódjanak össze?
- Mikor kell új structured oszlop?

---

## OQ-ABIL-002 – Execution plan

**Státusz:** `open`, `blocked_by_effect_module_prototype`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`

Kérdések:

- Runtime package tartalmazzon előre generált execution plant?
- Vagy a motor futáskor építse?
- Pythonban és GDScriptben ugyanaz a plan legyen?
- Execution plan debugolható legyen?

---

## OQ-ABIL-003 – Card-local fallback

**Státusz:** `open`, `blocked_by_engine_support_checker`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`

Kérdések:

- Normál játékban engedjük-e a fallbacket?
- AI-vs-AI tesztben engedjük-e?
- Godot/GDScript runtime-ban engedjük-e?
- Minden fallback warning legyen?
- Fallback mikor váljon blockinggá?

---

## OQ-ABIL-004 – Keywordök MVP-támogatása

**Státusz:** `open`, `blocked_by_keyword_audit`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`

Kérdések:

- Mely keywordök legyenek MVP-supported?
- Melyek igényelnek event window-t?
- Melyek statikus módosítók?
- Kulcsszavak ability module-ként vagy külön keyword registryként működjenek?

---

## OQ-ABIL-005 – Pecsét / Aeternal ability targetek

**Státusz:** `partly_answered`, `blocked_by_rules_audit`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`, `CONTRACT_SPECIFICATION.md`

Jelenlegi rögzített irány:

- Aeternal nem HP objektum.
- Aeternal nem kaphat damage/heal hatást.
- Pecsét nem HP objektum.
- Pecsét feltörési / visszaállítási eseményként kezelendő.

Nyitott kérdések:

- Aeternal target érték bekerüljön-e MVP-be?
- Mely effect modulok engedélyezettek Pecsétre?
- Pecsét targeteknél mindig kell-e `linked_current`?
- `ward_break` combatból és effectből azonos event legyen vagy külön payload?

---

# 10. AI, simulation és balance

## OQ-AI-001 – AI-vs-AI helye

**Státusz:** `open`, `blocked_by_technology_decision`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`

Kérdések:

- AI-vs-AI Pythonban maradjon?
- GDScriptben újraépüljön?
- Mindkettő legyen?
- Python AI vezérelje a GDScript motort?
- Balance tesztnél melyik motor legyen hiteles?

---

## OQ-AI-002 – Balance suspicion

**Státusz:** `open`, `blocked_by_balance_test_design`  
**Célfájl:** `DECISION_MAP.md`, `CONTRACT_SPECIFICATION.md`

Kérdések:

- Balance suspicion milyen adatokból keletkezik?
- Hány meccs után értelmezhető?
- Kártyára, deckre, klánra vagy matchupra vonatkozzon?
- Mit jelent a 40–60 winrate-sáv?
- Hogyan különítjük el a balanszhibát az engine- vagy deckhibától?

---

# 11. Szabályforrás és kártyaaudit

## OQ-RULES-001 – Főforrás-audit

**Státusz:** `deferred`, `blocked_by_data_pipeline`  
**Célfájl:** `DECISION_MAP.md`

Kérdések:

- Mikor induljon külön főforrás-audit?
- Mi kell a játékosbarát szabálykönyv előtt?
- Mi kell az engine / AI / Codex-barát szabályspecifikáció előtt?
- A hivatalos főforrások maradjanak DOCX-ben?
- Készüljön-e párhuzamos MD-alapú engine-spec?

---

## OQ-RULES-002 – Új kártyaaudit időzítése

**Státusz:** `deferred`, `blocked_by_validation_layer`  
**Célfájl:** `DECISION_MAP.md`

Kérdések:

- Mikor indulhat új kártyaaudit?
- Előbb kell-e stabil adatút?
- Előbb kell-e LOOKUPS / structured / validation rendezés?
- Kell-e működő AI-vs-AI teszt?
- Mikor ellenőrizzük vissza, hogy a korábbi javítások nem gyengítették-e túl a lapokat?