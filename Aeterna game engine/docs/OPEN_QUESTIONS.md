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
| `answered` | Megválaszolva és átvezetve. |
| `obsolete` | Már nem aktuális. |
| `blocked_by_prototype` | Prototípus vagy teszt kell a válaszhoz. |
| `blocked_by_godot_prototype` | Godot/GDScript prototípus vagy smoke test kell a válaszhoz. |
| `blocked_by_engine_test` | Engine vagy smoke test szükséges. |
| `blocked_by_data_audit` | Kártyaadat / LOOKUPS / structured audit szükséges. |
| `blocked_by_lookup_audit` | LOOKUPS audit szükséges. |
| `blocked_by_rules_audit` | Szabályforrás-audit szükséges. |
| `blocked_by_card_data_audit` | Kártyaadat-audit szükséges. |
| `blocked_by_runtime_package_builder` | Runtime package builder vagy package report szükséges. |
| `blocked_by_runtime_package_design` | Runtime package szerkezeti döntés szükséges. |
| `blocked_by_engine_support_checker` | Engine support checker / unsupported feature vizsgálat szükséges. |
| `blocked_by_ui_prototype` | UI vagy debug UI prototípus szükséges. |
| `blocked_by_ai_test_design` | AI-tesztelési terv szükséges. |
| `blocked_by_balance_test_design` | Balansztesztelési terv szükséges. |
| `blocked_by_validation_layer` | Validációs réteg szükséges. |
| `blocked_by_event_log_prototype` | Event log prototípus szükséges. |
| `blocked_by_event_viewer_test` | Event viewer / event debug test szükséges. |
| `blocked_by_diagnostics_design` | Diagnostics rendszerterv szükséges. |
| `blocked_by_visibility_rules` | Rejtett információ / visibility szabályok pontosítása szükséges. |
| `blocked_by_effect_module_prototype` | Ability/effect module prototípus szükséges. |
| `blocked_by_keyword_audit` | Keyword audit szükséges. |
| `blocked_by_structured_audit` | Structured mezők auditja szükséges. |
| `blocked_by_technology_decision` | Technológiai döntés szükséges. |
| `blocked_by_comparison_test` | Python ↔ GDScript összehasonlító teszt szükséges. |
| `blocked_by_combat_rules_spec` | Harci szabályspecifikáció szükséges. |
| `blocked_by_targeting_prototype` | Targeting prototípus szükséges. |
| `blocked_by_interactive_prototype` | Interaktív prototípus szükséges. |
| `blocked_by_reaction_prototype` | Reakcióablak prototípus szükséges. |
| `blocked_by_rules_examples` | Konkrét szabálypéldák szükségesek. |
| `deferred_until_interactive_ui` | Interaktív UI/prototípus fázisig halasztva. |
| `deferred_until_ai_test` | AI-tesztelési fázisig halasztva. |
| `ready_for_decision_later` | Később döntésre előkészíthető. |

---

## 1. Projektirány és célarchitektúra

### OQ-ARCH-001 – Régi Python motor sorsa

**Státusz:** `open`, `blocked_by_engine_test`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`, `ARCHITECTURE.md`

- A régi Python motor hosszú távon backenddé alakítható?
- Új tiszta Python backend készüljön?
- GDScript/Godot runtime irány legyen a fő?
- A Python csak adatpipeline / validáció / AI-vs-AI / referencia szerepben maradjon?
- Mely részek menthetők át a régi motorból?

### OQ-ARCH-002 – Python / GDScript / hibrid modell

**Státusz:** `open`, `blocked_by_prototype`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`

- GDScript alkalmas-e hosszú távú fő runtime engine-nek?
- Python maradjon-e AI-vs-AI tesztmotor?
- Legyen-e Python tesztmotor + GDScript játékengine hibrid?
- Ha két motor él, hogyan ellenőrizzük, hogy ugyanazt csinálják?
- Kell-e Python ↔ GDScript event log összehasonlító teszt?

---

### OQ-ARCH-003 – UI és rules engine szétválasztása

**Státusz:** `open`, `blocked_by_prototype`  
**Célfájl:** `ARCHITECTURE.md`, `TECHNOLOGY_DECISIONS.md`

Kérdések:

- Hogyan biztosítjuk, hogy a Godot UI ne tartalmazzon szabálylogikát?
- Milyen réteg legyen a `rules_service`?
- A Godot UI csak action requestet küldjön?
- Milyen contract választja el az inputot a szabálymotortól?

---

## 2. Dokumentáció és fájlstátusz

### OQ-DOC-001 – DOCX → Markdown migráció

**Státusz:** `partly_answered`  
**Célfájl:** `DECISION_MAP.md`

- Mely dokumentumok legyenek aktív Markdown fájlok?
- Mely DOCX-ek maradjanak archív eredetik?
- A hivatalos szabályfőforrások maradjanak-e DOCX-ben?
- Készüljön-e később exportált DOCX/PDF olvasói változat?
- A jövőbeli frissítések mindig meglévő MD fájlba kerüljenek-e új fájl helyett?

### OQ-DOC-002 – Checkpointok kezelése

**Státusz:** `partly_answered`  
**Célfájl:** `CHECKPOINTS.md`

- Minden checkpoint egyetlen `CHECKPOINTS.md` fájlba kerüljön?
- A checkpoint fájl a gyökérben vagy `docs/checkpoints/` alatt legyen?
- A régi checkpoint DOCX-ek státusza `MERGED_TO_MD` legyen-e?
- A checkpoint tartalmazzon-e csak rövid tényeket, vagy részletes technikai naplót is?

---

### OQ-DOC-003 – Dokumentumszaporodás elkerülése

**Státusz:** `partly_answered`  
**Célfájl:** `DECISION_MAP.md`

Kérdések:

- Milyen esetben készülhet új dokumentum?
- Mikor kell meglévő dokumentumba beépíteni az új tartalmat?
- Mi legyen az átmeneti munkatervek sorsa?
- Törölhetők-e az átmeneti merge-tervek, ha a tartalom átkerült?

---

## 3. Runtime package és adatút

### OQ-DATA-001 – Compiled runtime package szükségessége

**Státusz:** `open`  
**Célfájl:** `RUNTIME_PACKAGE_SPECIFICATION.md`

- A program hosszú távon csak compiled runtime package-ből dolgozzon?
- A nyers exportok közvetlenül is futtathatók legyenek?
- Mikor váljon kötelezővé a manifestes package?
- A nyers export csak köztes réteg legyen?

### OQ-DATA-002 – Google Sheets → XLSX → exportáló → package adatút

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

### OQ-DATA-003 – Engine support státusz

**Státusz:** `open`, `blocked_by_engine_test`  
**Célfájl:** `RUNTIME_PACKAGE_SPECIFICATION.md`, `ABILITY_MODULE_SYSTEM.md`

Kérdések:

- Az `unsupported` kártya blokkolja-e a package buildet?
- Csak akkor blokkoljon, ha deckben szerepel?
- `partial` státusz warning vagy audit note legyen?
- Card-local fallback megengedett-e AI-vs-AI tesztben?
- Godot runtime esetén unsupported effect mit okozzon?

---

### OQ-DATA-004 – Legacy alias és canonical értékek

**Státusz:** `open`, `blocked_by_data_audit`  
**Célfájl:** `RUNTIME_PACKAGE_SPECIFICATION.md`

Kérdések:

- A legacy alias automatikusan canonical értékre forduljon?
- A veszélyes alias mindig audit note legyen?
- Mikor legyen blocking error?
- A canonical javítás visszakerüljön-e a forrásadatba?
- Régi Aeternal/Pecsét HP-modellre utaló értékek automatikusan tiltottak legyenek?

---

## 4. Snapshot

### OQ-SNAP-001 – Snapshot típusok

**Státusz:** `open`, `blocked_by_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Kell-e külön `opponent_visible_snapshot`, vagy elég a `player_visible_snapshot` viewer alapján?
- Mikor váljon fontossá a `spectator_snapshot`?
- A debug snapshot tartalmazhat-e teljes kézlap-, pakli- és face-down információt?
- AI-hoz kell-e külön `ai_fair_snapshot` és `ai_debug_snapshot`?
- Replayhez külön `replay_snapshot` kell, vagy a debug/player snapshotokból származtatható?

---

### OQ-SNAP-002 – Pecsétmodell snapshotban

**Státusz:** `open`, `blocked_by_rules_audit`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `ARCHITECTURE.md`

Jelenlegi rögzített irány:

- A Pecsét nem HP-alapú objektum.
- A Pecsét feltörési / visszaállítási eseményként kezelendő.
- A snapshotban ne szerepeljen `ward_hp`, `seal_hp` vagy hasonló HP-mező.

Nyitott kérdések:

- A Pecsét snapshotban lapként, védelmi objektumként vagy mindkettőként jelenjen meg?
- A feltört Pecsét hová kerül pontosan a snapshotban?
- Kell-e `linked_current` minden Pecsétre?
- A Pecsétlapok nevei láthatók-e a játékosok számára?
- A Pecsét állapota `standing`, `broken`, `restored`, `removed` formában legyen?
- A Pecsétállapot játékosonként külön objektum legyen, vagy a board/current struktúrához kapcsolódjon?

---

### OQ-SNAP-003 – Ősforrás láthatóság és állapot

**Státusz:** `open`, `blocked_by_rules_audit`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Az Ősforrás lapjai publikusak vagy részben rejtettek?
- Az ellenfél mit lát az Ősforrásból?
- Kell-e külön `used`, `ready`, `exhausted` vagy hasonló állapot minden Ősforrás-lapra?
- Az Aura forrása látszódjon-e a snapshotban?
- A snapshotban elég az Ősforrás darabszáma, vagy kártyareferenciák is kellenek?
- Az AI fair snapshot ugyanazt lássa az Ősforrásból, mint egy játékos?

---

### OQ-SNAP-004 – Rejtett információ és visibility

**Státusz:** `open`, `blocked_by_prototype`, `blocked_by_rules_audit`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Mit lát pontosan az ellenfél a face-down Jelekből?
- Az ellenfél kézlapjai hogyan jelenjenek meg?
- A deck teteje debugon kívül soha nem látszik?
- A face-down Jel saját játékosnak ismert, ellenfélnek rejtett objektum legyen?
- A `known_to`, `visibility`, `face_down`, `revealed` mezők közül melyek legyenek kötelezőek?
- Fair AI pontosan ugyanazt lássa, mint az adott játékos?
- A debug snapshot minden rejtett információt tartalmazhat?

---

### OQ-SNAP-005 – Pending decision és döntési ablak

**Státusz:** `open`, `blocked_by_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- A snapshot tartalmazza-e mindig, hogy van-e folyamatban lévő döntés?
- A `pending` mező legyen kötelező minden snapshotban?
- A `window_type` milyen értékeket vehet fel MVP-ben?
- A `priority_player` mindig szerepeljen?
- A `prompt_hu` backendből jöjjön, vagy frontend generálja?
- A `can_pass` minden döntési ablaknál kötelező legyen?
- Az automatikusan feloldható helyzeteknél legyen-e pending állapot?

---

### OQ-SNAP-006 – Event log a snapshotban

**Státusz:** `open`, `blocked_by_event_viewer_test`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Mennyi esemény legyen közvetlenül a snapshotban?
- A snapshot csak `recent_events` rövid listát tartalmazzon?
- A teljes event log külön contract / endpoint / fájl legyen?
- Kell-e külön `visible_event_log` és `debug_event_log`?
- Kell-e `last_event_index` és `next_event_index` minden snapshotba?
- Az explanation log a snapshot része legyen, vagy külön event layer?

---

## 5. Legal actions

### OQ-LA-001 – Enabled és disabled actionök

**Státusz:** `open`, `blocked_by_ui_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Normál játékban csak enabled actionök jelenjenek meg?
- Debug módban jelenjenek meg disabled actionök is?
- Tutorial módban kell-e disabled reason?
- A disabled actionök ugyanabban a listában legyenek, vagy külön debug listában?
- A legal action lista tartalmazzon-e UI-segédadatokat?
- A frontend kapjon-e magyarázatot arra, hogy egy kártya miért nem játszható ki?

---

### OQ-LA-002 – Reakcióablak modell

**Státusz:** `open`, `blocked_by_rules_audit`, `blocked_by_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `ABILITY_MODULE_SYSTEM.md`

- Elég reaction queue, vagy kell stack / chain jellegű modell?
- Burst és Jel ugyanabban a reaction rendszerben legyen?
- Prevention és replacement hatások ugyanabba a rendszerbe tartozzanak?
- Pass reaction külön legal action legyen?
- Reakcióablak automatikusan átugorható, ha nincs valódi döntés?
- Több lehetséges reakció esetén ki választ sorrendet?
- A reaction window a snapshot `pending` mezőjében, a legal action listában vagy mindkettőben jelenjen meg?

---

### OQ-LA-003 – Combat actionök

**Státusz:** `open`, `blocked_by_combat_rules_spec`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `ARCHITECTURE.md`

- Mikor kerüljön be a `declare_attack` action?
- Kell-e külön `choose_attack_target` action?
- A blokkolás választás legyen vagy automatikus szabály?
- Kell-e külön `choose_blocker` action?
- A Pecsét feltörése attack action után hogyan jelenjen meg?
- A Pecsétre támadás targetként, eventként vagy mindkettőként jelenjen meg?
- A combat legal actionök MVP-ben szerepeljenek, vagy későbbi fázisra kerüljenek?

---

### OQ-LA-004 – Fizetés és Aura

**Státusz:** `open`, `blocked_by_rules_audit`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `RUNTIME_PACKAGE_SPECIFICATION.md`

- Meddig legyen automatikus Aura-fizetés?
- Mikor kell kézi forrásválasztás?
- Ideiglenes Aura elsőként vagy utolsóként költődjön?
- Alternatív költségek mikor kerüljenek be?
- A fizetés külön legal action legyen?
- Több fizetési forrásnál kell-e payment window?
- A legal action tartalmazza-e a `cost_summary` mellett a konkrét fizetési lehetőségeket is?

---

### OQ-LA-005 – Targeting

**Státusz:** `open`, `blocked_by_targeting_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `ABILITY_MODULE_SYSTEM.md`

- Célpontválasztás külön action legyen?
- Vagy a play action része?
- Több célpontnál hogyan kezeljük a sorrendet?
- Invalid target esetén teljes vagy részleges feloldás legyen?
- A legal action tartalmazzon target preview-t?
- A debug UI mutassa az invalid targeteket is?
- A frontend kiemeléseit teljesen a legal action targeting adatokból építsük?
- A célpont-érvényesség végső döntése mindig a rules engine-ben maradjon?

---

### OQ-LA-006 – UI mezők a legal actionben

**Státusz:** `open`, `blocked_by_ui_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- A legal action tartalmazzon magyar `label_hu` mezőt?
- A legal action tartalmazzon `prompt_hu` mezőt?
- Vagy a frontend lookupból generálja ezeket?
- Mennyi UI-segédadat legyen a contract része?
- A promptok később lokalizálhatók legyenek?
- A debug UI és a végleges játék UI ugyanazt a legal action mezőkészletet használja?

---

### OQ-LA-007 – AI legal action mezők

**Státusz:** `open`, `blocked_by_ai_test_design`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `TECHNOLOGY_DECISIONS.md`

- Kell-e az actionökhöz AI heuristic tag?
- Vagy az AI külön értékelje a legal actionöket?
- Fair AI és debug AI külön legal action listát kapjon?
- AI kaphat-e becsült értékeket?
- Balance tesztnél fair vagy debug AI legyen az alap?
- Az AI legal action listája tartalmazhat-e olyan információt, amit játékos nem látna?

---

## 6. Action request / response

### OQ-AR-001 – Request azonosítás

**Státusz:** `open`, `deferred_until_interactive_ui`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Kötelező legyen-e a `client_request_id`?
- Backend vagy frontend generálja a request ID-t?
- Hogyan kezeljük a duplicate requestet?
- Kell-e idempotencia már MVP-ben?
- Hálózati / későbbi PvP működéshez milyen azonosítás kell?
- Lokális debug módban egyszerűbb request modell is elég?

---

### OQ-AR-002 – Snapshot frissesség és state_version

**Státusz:** `open`, `blocked_by_interactive_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Kell-e `state_version` már MVP-ben?
- Elavult snapshot esetén mindig reject legyen?
- Vagy a backend próbálja újravalidálni az actiont az aktuális állapotban?
- PvP előtt mennyire legyen szigorú?
- Lokális single-player módban lazább lehet?
- A stale snapshot warning, error vagy blocking legyen?

---

### OQ-AR-003 – Action ID élettartama

**Státusz:** `open`, `deferred`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Az action ID csak snapshoton belül stabil?
- Hosszabb életű action token kell?
- Kell-e signed / opaque action token később?
- Ha a legal action lista frissül, mikor érvénytelenedik a régi action ID?
- AI-vs-AI tesztnél kell-e stabil action ID?
- Debug UI-ban elég-e egyszerű `action_id`?

---

### OQ-AR-004 – Többlépcsős targeting és pending állapot

**Státusz:** `open`, `blocked_by_targeting_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- A célpontválasztás külön request legyen?
- Vagy a play action már tartalmazza a célpontot?
- Többlépcsős célzásnál hogyan tároljuk a pending állapotot?
- Target invalidáció után visszakérdezzen a motor?
- Partial resolution és invalid target hogyan különüljön el?
- A target selection snapshotot generáljon?

---

### OQ-AR-005 – Action response és reakcióablak

**Státusz:** `open`, `blocked_by_reaction_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Az eredeti action response `pending_reaction` státuszt kapjon?
- Vagy az action előbb teljesen rögzül, majd külön reaction window event nyílik?
- Burst és Jel válasz ugyanabban a rendszerben legyen?
- Az action response tartalmazza a reaction window legal actions hintjét?
- A reakcióablak külön snapshotot generáljon?
- A reaction pass külön action request legyen?

---

### OQ-AR-006 – Partial resolution státuszok

**Státusz:** `open`, `blocked_by_rules_examples`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Mikor legyen `partially_resolved`?
- Mikor legyen `failed`?
- Mikor legyen `cancelled`?
- Mikor legyen `prevented`?
- Mikor legyen `replaced`?
- Feltételes ág kimaradása normál result, info vagy warning?
- Részleges feloldás mikor jelent valódi hibát?

---

### OQ-AR-007 – Unsupported engine feature action közben

**Státusz:** `open`, `blocked_by_engine_support_checker`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `ABILITY_MODULE_SYSTEM.md`

- Engine unsupported mindig blocking error legyen?
- Fejlesztési módban lehet-e warning?
- Card-local fallback normál játékban engedett legyen?
- AI-vs-AI tesztben unsupported lap kihagyható legyen?
- Action response mikor legyen `not_executable`?
- Unsupported effect esetén generálódjon event, diagnostics entry vagy mindkettő?

## 7. Event log

### OQ-EVENT-001 – Event részletesség

**Státusz:** `open`, `blocked_by_event_log_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Mennyire legyen részletes az MVP event log?
- Minden apró belső engine-lépésről készüljön event?
- Vagy csak gameplay-szinten látható események kerüljenek az event logba?
- A debug eventek külön layerben legyenek?
- A frontend eventek külön generált rétegként jelenjenek meg?
- A gameplay event és debug event ugyanabban a logban legyen szűrhető módon, vagy külön fájlban / contractban?
- Az event log mennyire legyen alkalmas későbbi replayre már MVP-ben?

---

### OQ-EVENT-002 – Explanation log és játékosbarát magyarázat

**Státusz:** `open`, `blocked_by_ui_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Minden komplex eseményhez kell magyar magyarázat?
- Vagy csak reakció, replacement, prevention, részleges feloldás és hibás action esetén?
- A `message_hu` backendből jöjjön?
- Vagy a frontend lookupból / lokalizációs rétegből generálja?
- Az explanation log külön event layer legyen?
- A játékosbarát magyarázat tartalmazhat-e szabályértelmező szöveget?
- Debug módban külön részletesebb magyarázat kell?

---

### OQ-EVENT-003 – Debug eventek, audit eventek és diagnostics kapcsolat

**Státusz:** `open`, `blocked_by_diagnostics_design`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Debug eventek bekerüljenek a normál event logba szűrhető rétegként?
- Vagy teljesen külön debug log legyen?
- Audit eventek a gameplay event log részei legyenek?
- Card-local fallback eventként is jelenjen meg?
- Unsupported effect event legyen, diagnostics entry legyen, vagy mindkettő?
- Engine warning esetén készüljön event is?
- A diagnostics és event log között legyen-e kötelező hivatkozás?

---

### OQ-EVENT-004 – Rejtett információ event logban

**Státusz:** `open`, `blocked_by_visibility_rules`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- Egyetlen belső teljes event logból szűrjünk viewer szerint?
- Vagy eleve több event log készüljön nézőpontonként?
- PvP előtt kell-e külön biztonsági szűrő?
- Fair AI event log hogyan különüljön el a debug event logtól?
- Debug log tartalmazhat-e minden rejtett információt?
- A face-down Jel aktiválása előtt milyen event látszódjon az ellenfélnek?
- Az event log soha ne szivárogtasson rejtett információt player-visible módban?

---

### OQ-EVENT-005 – Replay-kompatibilitás

**Státusz:** `deferred`, `open`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- MVP-ben kell-e replay-kompatibilitás?
- Vagy elég, ha az event log szerkezete később replayre alkalmassá tehető?
- Kell-e action history külön az event log mellé?
- Kell-e időnként snapshot checkpoint a replay gyorsításához?
- Replayhez teljes belső event log kell?
- Vagy player-visible replay log is elég?
- A replay rendszer mikor váljon fejlesztési prioritássá?

---

### OQ-EVENT-006 – Balance test eventek

**Státusz:** `open`, `blocked_by_balance_test_design`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `DECISION_MAP.md`

- A balance suspicion eventek meccs közben keletkezzenek?
- Vagy csak futás utáni elemzésben?
- Kell-e külön `balance_report` contract?
- Mely eventeket kell gyűjteni balanszvizsgálathoz?
- Card usage, damage, ward break, draw, discard és win condition eventek külön jelölendők?
- Balance eventek normál gameplay logban legyenek vagy külön reportban?
- Hogyan különítjük el a balanszgyanút az engine-hibától vagy decklista-hibától?

---

## 8. Diagnostics

### OQ-DIAG-001 – Severity és blocking rendszer

**Státusz:** `open`, `ready_for_decision_later`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `RUNTIME_PACKAGE_SPECIFICATION.md`

- Kell-e külön `critical` severity?
- Vagy elég az `error` + `blocking: true` kombináció?
- A `warning` mindig nem blokkoló legyen?
- Az `audit_note` severity legyen, vagy külön workflow kategória?
- A `balance_suspicion` severity legyen, vagy külön category?
- A severity és a blocking külön mezőként maradjon?
- Mely severity látszódjon runtime közben, és melyik csak fejlesztői reportban?

---

### OQ-DIAG-002 – Blocking szabályok development és runtime módban

**Státusz:** `open`, `blocked_by_engine_support_checker`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `RUNTIME_PACKAGE_SPECIFICATION.md`

- Mely engine-hiányok blokkoljanak development mode-ban?
- Aktív runtime kártyán unsupported effect mindig blokkoljon?
- Card-local fallback lehet warning normál futásban?
- Hidden information violation mindig critical/blocking legyen?
- Legacy alias mikor blocking?
- Workflow érték runtime mezőben mikor warning és mikor error?
- Deckben szereplő unsupported kártya blokkolja-e a package betöltést?
- Nem deckben szereplő unsupported kártya elég warning legyen?

---

### OQ-DIAG-003 – Diagnostics report formátum

**Státusz:** `open`, `blocked_by_runtime_package_builder`  
**Célfájl:** `RUNTIME_PACKAGE_SPECIFICATION.md`, `CONTRACT_SPECIFICATION.md`

- Egy nagy diagnostics report legyen?
- Vagy külön export, runtime, engine, audit és balance report?
- JSON, JSONL vagy Markdown formátum legyen az elsődleges?
- Kell-e emberi olvasásra alkalmas Markdown összefoglaló?
- Kell-e gépi fogyasztásra alkalmas JSON diagnostics fájl?
- A runtime package tartalmazza az összes diagnosticot?
- Vagy csak diagnostics summaryt és hivatkozást adjon külön report fájlra?
- A report fájlok regenerálható outputok vagy verziózott referenciafájlok legyenek?

---

### OQ-DIAG-004 – Runtime visibility

**Státusz:** `open`, `blocked_by_ui_prototype`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`

- A játékos lásson-e bármilyen diagnostics üzenetet normál játékban?
- Vagy diagnostics csak fejlesztői / debug módban jelenjen meg?
- Tutorial módban lehet-e warning jellegű magyarázat?
- Diagnostics üzenet soha ne szivárogtasson rejtett információt?
- Player-visible diagnostics és debug diagnostics külön nézet legyen?
- UI-ban hogyan különüljön el a játékosbarát hibaüzenet és a fejlesztői diagnostics?
- Action rejected esetén mennyit kell elmondani a játékosnak?

---

### OQ-DIAG-005 – LOOKUPS diagnostics

**Státusz:** `open`, `blocked_by_lookup_audit`  
**Célfájl:** `RUNTIME_PACKAGE_SPECIFICATION.md`, `CONTRACT_SPECIFICATION.md`

- `audit_required` érték aktív runtime kártyán mikor blokkoljon?
- Legacy alias automatikusan javítható legyen export közben?
- Veszélyes legacy alias esetén mindig kártyaaudit kell?
- Inactive érték aktív kártyán mikor error?
- Label_HU és Value keveredése warning vagy blocking legyen?
- Workflow-only érték runtime mezőben mikor blokkoljon?
- Unknown enum value development mode-ban warning vagy error?
- Runtime-supported és unsupported-but-known értékek hogyan különüljenek el?

---

### OQ-DIAG-006 – Balance suspicion

**Státusz:** `open`, `blocked_by_balance_test_design`  
**Célfájl:** `DECISION_MAP.md`, `CONTRACT_SPECIFICATION.md`

- Mikortól számít winrate gyanúsnak?
- Mennyi meccs kell egy balance suspicionhöz?
- Balance suspicion kártyára, deckre, klánra vagy matchupra vonatkozzon első körben?
- Mit jelent a 40–60 winrate-sáv?
- Hogyan kezeljük az erős, de identitásból fakadó előnyöket?
- Hogyan különítjük el a valódi balanszhibát az engine- vagy paklihibától?
- Balance suspicion blokkoljon valamit, vagy csak reportban jelenjen meg?
- Balance suspicion emberi döntést igénylő audit note-ot generáljon?

---

### OQ-DIAG-007 – Diagnostics és checkpointok kapcsolata

**Státusz:** `open`, `deferred`  
**Célfájl:** `CHECKPOINTS.md`, `CONTRACT_SPECIFICATION.md`

- A checkpointok tartalmazzanak diagnostics összefoglalót?
- A smoke testek diagnostics warningjai bekerüljenek a checkpointba?
- Nem blokkoló Godot / Windows warningokat külön listázzuk?
- Mikor tekinthető egy warning ismert, nem blokkoló technikai környezeti jelzésnek?
- A checkpoint csak tényleges AETERNA hibát tartalmazzon, vagy környezeti warningokat is?

---

## 9. Ability module system

### OQ-ABIL-001 – Structured mezők részletessége

**Státusz:** `open`, `blocked_by_card_data_audit`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`, `RUNTIME_PACKAGE_SPECIFICATION.md`

- A mostani structured oszlopok elég részletesek-e?
- Kell-e külön `parameter` mező?
- Kell-e külön `secondary_target` mező?
- Kell-e külön `secondary_effect` mező?
- A többértékű mezők hogyan kapcsolódjanak össze sorrend szerint?
- A Hatáscímkék elégségesek-e végrehajtási logikához?
- Mikor kell új structured oszlop?
- Mikor kell egy structured értéket csak auditcímkeként kezelni?

---

### OQ-ABIL-002 – Execution plan

**Státusz:** `open`, `blocked_by_effect_module_prototype`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`

- A runtime package tartalmazzon előre generált execution plant?
- Vagy a motor futáskor építse?
- GDScripthez hasznosabb lenne-e előre fordított plan?
- Pythonban és GDScriptben ugyanaz a plan legyen?
- Execution plan legyen debugolható?
- Execution plan event loghoz köthető legyen?
- Ha az execution plan hibás, az package build error vagy runtime error legyen?

---

### OQ-ABIL-003 – Card-local fallback

**Státusz:** `open`, `blocked_by_engine_support_checker`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`, `CONTRACT_SPECIFICATION.md`

- Normál játékban engedjük-e a card-local fallbacket?
- AI-vs-AI tesztben engedjük-e?
- Godot/GDScript játékmotorban engedjük-e?
- Minden fallback warning legyen?
- Fallback migrációs lista készüljön?
- Fallback mikor váljon blockinggá?
- Card-local fallback eventként, diagnostics entryként vagy mindkettőként jelenjen meg?
- A fallback hosszú távon kivétel legyen, nem alapműködés?

---

### OQ-ABIL-004 – Reaction system ability szinten

**Státusz:** `open`, `blocked_by_rules_audit`, `blocked_by_effect_module_prototype`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`, `CONTRACT_SPECIFICATION.md`

- Elég reaction queue?
- Kell stack / chain jellegű modell?
- Burst és Jel ugyanazon reaction rendszerben fusson?
- Prevention és replacement ugyanabba a rendszerbe tartozzon?
- Trigger-sorrend választás mikor kell?
- Automatikus és opcionális trigger hogyan különüljön el?
- A reaction rendszer ability module szinten vagy core rules engine szinten legyen?
- A reaction ablakok event logban hogyan jelenjenek meg?

---

### OQ-ABIL-005 – Keywordök MVP-támogatása

**Státusz:** `open`, `blocked_by_keyword_audit`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`

- Mely keywordök legyenek MVP-supported?
- Mely keywordök igényelnek külön event window-t?
- Mely keywordök csak statikus módosítók?
- Kulcsszavak ability module-ként vagy külön keyword registryként működjenek?
- A kártyaszövegben ne kelljen kiírni a kulcsszó teljes jelentését, de az engine hol tárolja?
- A keyword definíciók runtime package-ben, rules specben vagy külön registryben legyenek?
- Unsupported keyword aktív kártyán mikor blokkoljon?

---

### OQ-ABIL-006 – Pecsét / Aeternal ability targetek

**Státusz:** `partly_answered`, `blocked_by_rules_audit`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`, `CONTRACT_SPECIFICATION.md`

Jelenlegi rögzített irány:

- Aeternal nem HP objektum.
- Aeternal nem kaphat sebzést.
- Aeternal nem gyógyítható.
- Pecsét nem HP objektum.
- Pecsét feltörési / visszaállítási eseményként kezelendő.

Nyitott kérdések:

- Aeternal target érték egyáltalán bekerüljön-e MVP-be?
- `own_aeternal` és `enemy_aeternal` mikor legyenek érvényes targetek?
- Pecsét targeteknél minden esetben `linked_current` is kell?
- A `ward_break` eventet combat és effect külön payloadban jelölje?
- Mely effect modulok engedélyezettek Pecsétre?
- Mely effect modulok soha nem engedélyezettek Pecsétre?
- Aeternalra csak nagyon speciális, explicit engedélyezett hatások mehessenek?

---

### OQ-ABIL-007 – Hatáscímkék szerepe

**Státusz:** `open`, `blocked_by_structured_audit`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`, `RUNTIME_PACKAGE_SPECIFICATION.md`

- A Hatáscímkék maradjanak diagnosztikai / auditcímkék?
- Vagy később végrehajtási modulokat is indíthatnak?
- Mikor válik egy Effect_Tag engine-supported effect module-lá?
- Túl általános hatáscímke esetén audit note kell?
- A Hatáscímkék és structured ability mezők hogyan kapcsolódjanak?
- Egy kártyán több effect tag sorrendje számítson?
- Effect tag alapján készüljön engine support report?

---

### OQ-ABIL-008 – Ability registry és runtime package kapcsolat

**Státusz:** `open`, `blocked_by_runtime_package_design`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`, `RUNTIME_PACKAGE_SPECIFICATION.md`

- Az ability registry a runtime package része legyen?
- Külön fájl legyen, például `ability_registry.json`?
- Minden module_id tartalmazzon support_status értéket?
- Ability module-hoz kell input parameter schema?
- Ability module-hoz kell output event lista?
- Unsupported module szerepelhet registryben?
- Godot loader csak betölti a registryt, vagy már validálja is?
- Python builder számolja az ability support státuszokat?

## 10. Technology decisions

### OQ-TECH-001 – Python hosszú távú szerepe

**Státusz:** `open`, `blocked_by_technology_decision`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`, `ARCHITECTURE.md`

- Python maradjon-e hosszú távon szabálymotor / backend?
- Python csak adatpipeline, exportvalidáció, runtime package build és riportkészítés szerepben maradjon?
- Python maradjon-e AI-vs-AI tesztmotor?
- A régi Python motorból mely modulok menthetők át?
- Új tiszta Python backend készüljön, vagy a jelenlegi motor refaktorálódjon?
- Milyen technikai bizonyíték kell ahhoz, hogy Python backendként maradjon?
- Milyen kockázatokkal járna, ha a végleges Godot játék Python backendtől függne?

---

### OQ-TECH-002 – GDScript / Godot runtime alkalmassága

**Státusz:** `open`, `blocked_by_godot_prototype`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`, `PROTOTYPE_PLANS.md`

- GDScript alkalmas-e hosszú távú AETERNA rules engine-nek?
- GDScriptben tisztán elkülöníthető-e a rules service az UI node-októl?
- Godot/GDScript képes-e kényelmesen fogyasztani a runtime package-et?
- GDScript alkalmas-e legal action, action request, event log és diagnostics contract kezelésére?
- GDScriptben megoldható-e automatizált smoke test / headless tesztelés hosszú távon?
- GDScriptben megoldható-e AI-vs-AI futtatás?
- Vagy Godot/GDScript maradjon inkább UI, debug viewer és későbbi kliensréteg?

---

### OQ-TECH-003 – Python + GDScript hibrid modell

**Státusz:** `open`, `blocked_by_comparison_test`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`, `ARCHITECTURE.md`

- Maradjon-e hosszú távon Python package builder + GDScript runtime modell?
- Python legyen-e a tesztmotor, GDScript pedig a játszható kliens?
- Ha két rendszer él párhuzamosan, hogyan akadályozzuk meg a szabályeltérést?
- Kell-e Python ↔ GDScript összehasonlító event log teszt?
- Melyik rendszer legyen a referencia, ha eltérő eredményt adnak?
- A runtime package legyen-e a közös, kötelező adatforrás mindkét oldalnak?
- Mennyi duplikált szabálylogika fogadható el átmenetileg?

---

### OQ-TECH-004 – Runtime package mint technológiai határ

**Státusz:** `partly_answered`, `open`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`, `RUNTIME_PACKAGE_SPECIFICATION.md`

Jelenlegi irány:

- A runtime package legyen a Python és Godot közötti közös adatcsomag.
- Python erős jelölt a package build, validáció és riportkészítés területén.
- Godot/GDScript elsődlegesen package fogyasztóként és debug / kliens oldalon bizonyított.

Nyitott kérdések:

- A runtime package legyen-e az egyetlen hivatalos programinput?
- A Godot runtime közvetlenül csak package-ből dolgozzon?
- Python AI-vs-AI teszt is ugyanebből a package-ből fusson?
- A package tartalmazzon-e előre generált ability execution plant?
- A package schema verziózás mikor váljon szigorúvá?

---

### OQ-TECH-005 – Godot headless / smoke test stratégia

**Státusz:** `partly_answered`, `open`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`, `CHECKPOINTS.md`

Jelenlegi tanulság:

- Godot headless smoke test explicit `--log-file` használatával stabilabban fut Windows / Godot 4.7 környezetben.
- A root certificate store warning jelenleg nem blokkoló, ha az `OK` output után jelenik meg.

Nyitott kérdések:

- Minden Godot smoke testhez külön `.bat` futtató legyen?
- A headless smoke logok mindig ignorált fájlok legyenek?
- Milyen Godot warning számít AETERNA hibának?
- Milyen Godot warning számít környezeti, nem blokkoló jelzésnek?
- Később CI-ben is futtathatók legyenek-e ezek a smoke tesztek?

---

### OQ-TECH-006 – Codex-feladatok technológiai bontása

**Státusz:** `partly_answered`, `open`  
**Célfájl:** `DECISION_MAP.md`, `TECHNOLOGY_DECISIONS.md`

Jelenlegi irány:

- Codex rövid, célzott technikai feladatokat kapjon.
- Ne kapjon teljes projektirányítást.
- Ne kapjon nagy, homályos refaktort.
- Ne döntsön szabályi vagy balanszkérdésben.

Nyitott kérdések:

- Milyen méretű Codex-feladat számít biztonságosnak?
- Mikor kell előbb ChatGPT-vel tervet készíteni Codex előtt?
- Codex készíthet-e dokumentációt, vagy csak technikai riportot?
- Codex implementálhat-e GDScript rules service prototípust?
- Codex módosíthat-e mappaszerkezetet, vagy csak explicit fájllista alapján?

---

## 11. AI / simulation / balance

### OQ-AI-001 – AI-vs-AI helye

**Státusz:** `open`, `blocked_by_technology_decision`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`, `ARCHITECTURE.md`

- AI-vs-AI tesztelés Pythonban maradjon?
- GDScriptben is újra kell építeni az AI-vs-AI futtatást?
- Mindkét oldalon legyen AI-vs-AI?
- Python AI vezérelheti-e később a GDScript motort?
- Balance tesztnél melyik motor eredménye legyen hiteles?
- A régi Python AI-vs-AI tapasztalatok hogyan menthetők át?
- Mikor mondhatjuk, hogy az új engine alkalmas balansztesztelésre?

---

### OQ-AI-002 – Fair AI és debug AI

**Státusz:** `open`, `blocked_by_ai_test_design`  
**Célfájl:** `TECHNOLOGY_DECISIONS.md`, `CONTRACT_SPECIFICATION.md`

- Kell-e külön fair AI és debug AI mód?
- Fair AI pontosan ugyanazt lássa, mint egy játékos?
- Debug AI láthat-e rejtett információt tesztelési célból?
- Balance méréshez csak fair AI használható?
- Debug AI használható-e engine-hibakereséshez?
- A snapshot contract külön támogassa-e az AI nézőpontokat?
- AI event log szűrése ugyanaz legyen, mint player-visible módban?

---

### OQ-AI-003 – AI döntési heurisztika és legal actions

**Státusz:** `open`, `blocked_by_ai_test_design`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `ARCHITECTURE.md`

- Az AI ugyanazt a legal action listát kapja, mint a játékos?
- A legal action tartalmazzon AI heuristic mezőket?
- Vagy az AI külön értékelje az actionöket?
- Az AI kaphat-e előszűrt actionlistát?
- Az AI döntési hibája hogyan különüljön el az engine hibájától?
- Az AI ne hajthasson végre szabálytalan actiont akkor sem, ha rosszul dönt?
- Kell-e AI decision log?

---

### OQ-AI-004 – Balance suspicion forrása

**Státusz:** `open`, `blocked_by_balance_test_design`  
**Célfájl:** `DECISION_MAP.md`, `CONTRACT_SPECIFICATION.md`

- Balance suspicion milyen adatokból keletkezzen?
- Winrate alapján?
- Card usage alapján?
- Matchup alapján?
- Deck pattern alapján?
- Túl gyakori ward break / túl gyors győzelem alapján?
- Hány meccs után értelmezhető egy balance suspicion?
- A balance suspicion kártyára, deckre, klánra vagy matchupra vonatkozzon?

---

### OQ-AI-005 – Winrate és klánidentitás

**Státusz:** `open`, `blocked_by_balance_test_design`  
**Célfájl:** `DECISION_MAP.md`

Jelenlegi munkahipotézis:

- A cél nem steril 50/50 balansz.
- A klánidentitás fontos.
- Az erős, karakteres klánirány önmagában nem hiba.
- A 40–60 winrate-sáv csak kezdeti figyelési elv, nem végleges matematikai szabály.

Nyitott kérdések:

- Pontosan mit jelent a 40–60 winrate-sáv?
- Hány meccs után tekinthető relevánsnak?
- Hogyan kezeljük az erős, de identitásból fakadó matchup előnyöket?
- Mikor lesz egy matchup túl egyoldalú?
- Hogyan kerülhető el a kő-papír-olló rendszer?
- Hogyan különítjük el a valódi balanszhibát az engine-, AI- vagy decklistahibától?

---

### OQ-AI-006 – Balance report

**Státusz:** `open`, `deferred_until_ai_test`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `RUNTIME_PACKAGE_SPECIFICATION.md`

- Kell-e külön `balance_report` contract?
- A balance report JSON, Markdown vagy mindkettő legyen?
- Meccsenkénti és összesített riport különüljön el?
- Card usage statisztika kell-e?
- Deck matchup statisztika kell-e?
- Milyen eventeket kell gyűjteni balanszhoz?
- Balance report regenerálható output legyen vagy verziózott referencia?

---

### OQ-AI-007 – Korábbi kártyajavítások visszaellenőrzése

**Státusz:** `open`, `blocked_by_balance_test_design`  
**Célfájl:** `DECISION_MAP.md`

- A korábban javított lapok nem lettek-e túlgyengítve?
- Megmaradt-e az egyediségük?
- Megmaradt-e a klánidentitásuk?
- Működnek-e játék közben?
- Nem lettek-e túl steril vagy túl óvatos lapok?
- A kártyajavítások visszatesztelése mikor induljon?
- Előbb szükséges-e stabil AI-vs-AI tesztmotor?

---

## 12. Rules audit and card audit timing

### OQ-RULES-001 – Hivatalos főforrás-audit

**Státusz:** `deferred`, `blocked_by_validation_layer`  
**Célfájl:** `DECISION_MAP.md`, `ARCHITECTURE.md`

- Mikor induljon külön főforrás-audit?
- A két 1.4v hivatalos főforrásban maradtak-e ellentmondások?
- Milyen hibákat kell még keresni a főforrásokban?
- A főforrás-audit előtt kell-e stabilabb engine/adatút?
- A főforrás-audit célja szabálytisztítás, játékosbarát szöveg vagy engine-barát specifikáció legyen?
- A főforrás-audit eredménye új DOCX, MD vagy mindkettő legyen?

---

### OQ-RULES-002 – Játékosbarát szabálykönyv időzítése

**Státusz:** `deferred`, `blocked_by_rules_audit`  
**Célfájl:** `DECISION_MAP.md`

- Mikor készülhet játékosbarát szabálykönyv?
- Előtte kötelező-e a főforrás-audit?
- A játékosbarát szabálykönyv külön dokumentum legyen?
- Milyen mélységben magyarázza a kezdőknek a szabályokat?
- Tartalmazzon-e példákat?
- Tartalmazzon-e vizuális pályamagyarázatot?
- A játékosbarát szabálykönyv DOCX, MD vagy később PDF legyen?

---

### OQ-RULES-003 – Engine / AI / Codex-barát szabályspecifikáció

**Státusz:** `deferred`, `blocked_by_rules_audit`  
**Célfájl:** `ARCHITECTURE.md`, `CONTRACT_SPECIFICATION.md`

- Készüljön-e külön engine-barát szabályspecifikáció?
- Ez a hivatalos főforrásból származzon?
- Tartalmazza-e a fázisokat, akcióablakokat, célpontválasztást, triggerablakokat és győzelmi feltételeket?
- Codex számára külön rövidebb szabályspecifikáció készüljön?
- Az engine-barát szabályspecifikáció legyen MD-alapú?
- Ez váljon-e később a rules engine implementáció egyik fő forrásává?

---

### OQ-RULES-004 – Új kártyaaudit időzítése

**Státusz:** `deferred`, `blocked_by_validation_layer`  
**Célfájl:** `DECISION_MAP.md`

Jelenlegi irány:

- Nem most indul új teljes kártyaaudit.
- Előbb stabilabb adatút, LOOKUPS, structured és diagnostics rendszer kell.
- A balanszaudit előtt legalább részben működő tesztelési / validációs réteg szükséges.

Nyitott kérdések:

- Mikor indulhat új kártyaaudit?
- Előbb kell-e stabil runtime package?
- Előbb kell-e LOOKUPS / structured / validation rendezés?
- Kell-e működő AI-vs-AI teszt?
- Kell-e engine support report?
- Mikor ellenőrizzük vissza a korábbi kártyajavításokat?
- A kártyaaudit birodalmonként, klánonként vagy hibakategóriánként induljon újra?

---

### OQ-RULES-005 – LOOKUPS és structured audit időzítése

**Státusz:** `open`, `blocked_by_data_audit`  
**Célfájl:** `RUNTIME_PACKAGE_SPECIFICATION.md`, `ABILITY_MODULE_SYSTEM.md`

- Mikor induljon a LOOKUPS/structured teljes audit?
- Előbb a runtime package buildernek kell-e stabilnak lennie?
- A Value / Label_HU / Canonical_Value irány már véglegesnek tekinthető?
- A legacy alias réteg mikor zárható?
- A dangerous / audit_required structured értékek listája mikor készüljön el?
- A structured értékek programlogikai mappingje mikor kezdődjön?
- Mely structured mezők a legfontosabbak az első engine támogatáshoz?

---

### OQ-RULES-006 – Kártyaszöveg és structured adat eltérései

**Státusz:** `open`, `blocked_by_card_data_audit`  
**Célfájl:** `ABILITY_MODULE_SYSTEM.md`, `RUNTIME_PACKAGE_SPECIFICATION.md`

- Mi történjen, ha a kártyaszöveg jó, de a structured mező hiányos?
- Mi történjen, ha a structured mező jó, de a kártyaszöveg félrevezető?
- Melyik számít elsődlegesnek engine szempontból?
- A structured adat audit note-ot vagy warningot generáljon eltérés esetén?
- Kártyaszöveg és structured adat eltérése blokkolja-e a runtime package-et?
- A javítás a kártyaszövegben, structured mezőben vagy mindkettőben történjen?

---

### OQ-RULES-007 – Aeternal / Pecsét szabálymodell végleges engine-specifikációja

**Státusz:** `partly_answered`, `blocked_by_rules_audit`  
**Célfájl:** `CONTRACT_SPECIFICATION.md`, `ABILITY_MODULE_SYSTEM.md`, `ARCHITECTURE.md`

Jelenlegi rögzített irány:

- Az Aeternal maga a játékos.
- Az Aeternal nem rendelkezik HP-val.
- Az Aeternal nem kaphat sebzést.
- Az Aeternal nem gyógyítható.
- A Pecsét nem HP-alapú objektum.
- A Pecsét feltörési / visszaállítási eseményként kezelendő.
- Ha nincs Entitás és Pecsét, ami véd, egy célba érő támadás azonnali vereséget jelent.

Nyitott kérdések:

- Az Aeternal target érték milyen korlátozással létezhet engine szinten?
- A Pecsét feltörése pontosan milyen event payloadot kapjon?
- A Pecsét visszaállítása milyen action/effect/event modellben szerepeljen?
- A combatból származó Pecsétfeltörés és effectből származó Pecsétfeltörés közös event_type legyen?
- Azonnali vereség triggerelése milyen eventként jelenjen meg?
- A snapshotban hogyan jelenjen meg, hogy egy játékos Aeternalja védtelen?
