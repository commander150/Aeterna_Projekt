# AETERNA Game Engine – Current Open Questions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.5  
**Dátum:** 2026-07-15  
**Státusz:** aktív közeli döntési kapu-, OQ-triázs- és prioritáslista  
**Technikai referencia:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum a következő engine-, technológiai, termékruntime- és szabályintegrációs feladatokat közvetlenül befolyásoló kérdéseket tartalmazza.

Kapcsolódó források:

- teljes történeti kérdésregiszter: `OPEN_QUESTIONS.md`;
- részletes történeti válasz- és döntési irányok: `OPEN_QUESTIONS_DECISIONS.md`;
- termékruntime-mérce: `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`;
- runtime-nyelvi kapu és pontozás: `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- comparison scenario: `RUNTIME_COMPARISON_FIXTURE_SPEC.md`;
- tanulóprogram-audit sablon: `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`;
- tanulóprogram-audit sorrend: `LEARNING_PROJECT_AUDIT_QUEUE.md`;
- hivatalos szabályforrás: `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`.

Az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó. A két hosszú dokumentum eredeti kérdései és válaszai megmaradnak történeti nyilvántartásként. Ha régi státuszuk vagy megfogalmazásuk eltér ettől a current dokumentumtól, a jelen fájl aktuális triázsa az irányadó.

A Python minimal engine a jelenlegi működő referenciaimplementáció. A végleges authoritative termékruntime nyelve és futási modellje még nincs kiválasztva. A nyelvváltás nem önálló cél.

---

## 1. Státuszok

| Státusz | Jelentés |
|---|---|
| `answered` | Megválaszolva és aktív dokumentumba átvezetve. |
| `partly_answered` | Van bizonyított vagy elfogadott rész, de maradt nyitott döntés. |
| `highest_priority_decision_gate` | A következő Codex-munkasáv elsődleges döntési feladata. |
| `needs_learning_project_audit` | A helyi tanulóprogramok tényleges megoldásait kell felmérni. |
| `needs_comparison_fixture` | A közös scenario implementációja és canonical artifactjai szükségesek. |
| `needs_integration_prototype` | Működő bridge- vagy runtime-proof szükséges. |
| `needs_packaging_proof` | Portable Windows-csomagolási és indítási bizonyíték szükséges. |
| `needs_source_decision` | A forrás nem ad elég egyértelmű választ; emberi szabálydöntés kell. |
| `needs_lookup_audit` | A canonical runtime értékeket LOOKUPS-ból kell ellenőrizni. |
| `needs_engine_design` | Technikai contract-, state- vagy eventdöntés kell. |
| `needs_visibility_decision` | Player-visible és hidden-information policy kell. |
| `queued_after_language_gate` | Definiált feladat, de a runtime-nyelvi döntés után folytatandó. |
| `deferred_non_blocking` | Nyitott, de a következő auditot vagy proofot nem blokkolja. |

---

## 2. Történeti Open Questions – aktuális technológiai triázs

| Eredeti OQ | Aktuális státusz | Aktuális értelmezés |
|---|---|---|
| `OQ-ARCH-001` | `partly_answered` | A régi Python motor referencia/review. Az új Python minimal engine működő comparison-reference. A végleges termékruntime nyitott. |
| `OQ-ARCH-002` | `highest_priority_decision_gate` | A régi Python–GDScript kérdés kibővült Python sidecar, Godot .NET/C#, GDScript és indokolt más jelöltek összehasonlítására. |
| `OQ-ARCH-003` | `answered` | A UI nem lehet szabályforrás. A frontend action requestet küld, az authoritative engine validál és transitiont hajt végre. |
| `OQ-TECH-001` | `partly_answered` | Python biztosan megmarad adatpipeline-, audit-, AI- és batch-toolingként. A termékruntime-szerepe proof után dönthető el. |
| `OQ-TECH-002` | `partly_answered` | A Godot loader/debug/UI szerepe bizonyított. A teljes GDScript rules runtime csak indokolt, szűk proof után értékelendő. |
| `OQ-TECH-003` | `highest_priority_decision_gate` | A fő proof-jelöltek Python sidecar és Godot .NET/C#. GDScript vagy más nyelv feltételes harmadik jelölt. |
| `OQ-TECH-004` | `answered` elvi szinten | A validált runtime package kötelező statikus programadat-contract. Nem MatchState és nem dönt a runtime nyelvéről. |
| `OQ-TECH-005` | `partly_answered` | Godot headless smoke működik. A végleges CI-, warning- és portable exportpolicy későbbi technikai részlet. |
| `OQ-TECH-006` | `answered` munkarendi szinten | Codex szűk, explicit scope-ú, tesztelhető feladatokat kap. A következő feladat read-only audittal indul. |
| `OQ-AI-001` | `partly_answered` | A Python AI/batch tooling megtartandó akkor is, ha a termékruntime más nyelvű lesz. A végleges adapter proof után dönthető el. |

Továbbra is érvényes:

- contract-first fejlesztés;
- runtime package, action request/response, snapshot, legal action, event és diagnostics mint határfelületek;
- a régi Python motor nem törlendő automatikusan;
- a régi motorból logika csak célzott audit és új teszt után emelhető át;
- a Godot UI nem tartalmazhat rejtett szabálylogikát;
- két teljes authoritative motor tartós párhuzamos fenntartása kerülendő;
- a végleges technológiai döntéshez prototípus, packaging proof és emberi jóváhagyás szükséges.

A Python leváltása csak akkor indokolt, ha bizonyítottan akadályozza a stabil portable futtatást, a Godot-integrációt, a lifecycle-kezelést vagy a hosszú távú karbantarthatóságot, illetve ha más jelölt lényegesen jobb összeredményt ad.

---

## 3. Lezárt termékruntime-döntések

### CQ-PROD-001 – Elsődleges operációs rendszer

**Státusz:** `answered`

- 64 bites Windows 10 és minden ennél újabb támogatott Windows asztali rendszer;
- 32 bites Windows nem cél;
- Linux később vizsgálható, de jelenleg nem prioritás.

### CQ-PROD-002 – Jelenlegi kiadási forma

**Státusz:** `answered`

- proofhoz és zárt teszthez portable, kibontott mappa;
- jelenleg nem kell telepítő;
- egyértelmű fő executable szükséges;
- telepítő csak későbbi, véglegesebb vagy szélesebb kiadásnál kell.

### CQ-PROD-003 – Jogosultság és írható adatok

**Státusz:** `answered` elvi szinten

- normál futtatáshoz ne kelljen adminjog;
- a program saját portable mappájából indulhasson;
- mentések, beállítások, logok és hibacsomagok felhasználói írható helyre kerüljenek;
- a pontos Windows-könyvtár későbbi technikai döntés.

### CQ-PROD-004 – Külső prerequisite-ek

**Státusz:** `answered`

- ne kelljen külön Pythont, Godot Editort, .NET SDK-t vagy fejlesztői toolchaint telepíteni;
- ne kelljen package-eket, modulokat vagy környezeti változókat kezelni;
- kevés számú, közismert és egyszerű prerequisite elfogadható;
- például szükséges .NET runtime vagy hasonló redistributable nem kizáró ok;
- self-contained csomagolás előny, de nem mindenáron kötelező.

### CQ-PROD-005 – Nem blokkoló későbbi termékkérdések

**Státusz:** `deferred_non_blocking`

- Linux-port;
- csomagméret optimalizálása;
- digitális kódaláírás;
- `%APPDATA%`, `%LOCALAPPDATA%`, `Documents` vagy más mentési/loghely;
- log retention és hibacsomag formátuma.

---

## 4. Aktuális architektúra- és runtime-kérdések

### CQ-ARCH-001 – Jelenlegi engine-reference

**Státusz:** `partly_answered`

Biztos:

- az új Python minimal engine a működő és tesztelt reference implementation;
- a Godot loader-, registry-, debug- és későbbi UI-réteg;
- a frontend nem módosít authoritative state-et;
- a legalitást engine-contract adja.

Nyitott:

- Python sidecar lesz-e a termékruntime;
- Godot .NET/C# lesz-e a termékruntime;
- szükséges-e GDScript vagy más proof;
- melyik modell teljesíti legjobban a portable Windows-termékkövetelményeket.

### CQ-ARCH-002 – `fourth turn` tanulóprogram-audit

**Státusz:** `needs_learning_project_audit`

Első Codex-feladat:

- read-only Batch 0 leltár;
- pontos helyi útvonal és projekthatárok;
- repository URL, commit/tag/verzió;
- kód-, asset- és dependencylicencek;
- nyelvek, Godot-verzió és runtime-ok;
- authoritative state helye;
- bridge, process lifecycle és packaging;
- tesztek és stabilitási bizonyíték;
- clean-room módon használható minta.

### CQ-ARCH-003 – Közös comparison fixture

**Státusz:** `needs_comparison_fixture`

A specifikáció elkészült a `RUNTIME_COMPARISON_FIXTURE_SPEC.md` fájlban. Codexnek canonical Python artifactokat kell generálnia, majd azonos jelentéssel futtatnia a Python sidecar és C# proofban.

### CQ-ARCH-004 – Python sidecar proof

**Státusz:** `needs_integration_prototype`, `needs_packaging_proof`

Vizsgálandó:

- stdin/stdout JSONL vagy localhost TCP;
- verziózott handshake;
- action request/response és state-version guard;
- timeout, kapcsolatvesztés és kontrollált shutdown;
- protokoll és logcsatorna elválasztása;
- külön Python-telepítés nélküli portable Windows-csomag;
- elárvult processz és antivírus false positive kockázata.

### CQ-ARCH-005 – Godot .NET/C# proof

**Státusz:** `needs_integration_prototype`, `needs_packaging_proof`

Vizsgálandó:

- tiszta C# rules library vagy elkülönített assembly;
- UI-node-októl független MatchState és transitionök;
- azonos comparison scenario és kompatibilis JSON-contract;
- unit és integration tesztek;
- Godot .NET portable Windows 10+ export;
- self-contained vagy egyszerű .NET runtime prerequisite;
- Python reference outputtal való differential comparison.

### CQ-ARCH-006 – GDScript és más nyelvek

**Státusz:** `deferred_non_blocking`

- minimal GDScript proof csak akkor, ha az audit vagy az első két proof indokolja;
- C++ GDExtension, Rust vagy más nyelv csak erős, reprodukálható előny esetén kerül fő scope-ba;
- embedded Python jelenleg kutatási irány, nem első proof.

### CQ-ARCH-007 – Következő gameplay-engine feladat

**Státusz:** `queued_after_language_gate`

- Wellspring production PlayerState- és MatchState-integráció;
- utána player-visible Wellspring summary;
- majd Beáramlás, Magnitúdó/Aura, payment és `play_card`.

---

## 5. Runtime package, AI és ability-rendszer

### CQ-RUNTIME-001 – Runtime package szerepe

**Státusz:** `answered`

- kötelező validált statikus programadat-contract;
- Godot nem olvas közvetlenül XLSX-et;
- a builder/tooling Pythonban maradhat bármely termékruntime mellett;
- a runtime package nem MatchState és nem szabálymotor;
- schema és package identity véglegesítése külön későbbi feladat.

### CQ-AI-001 – Python AI/batch tooling jövője

**Státusz:** `partly_answered`

Biztos:

- a Python AI-, audit-, batch- és balansztooling megtartandó;
- a működő Python engine differential reference marad;
- fair AI nem kaphat több információt, mint a játékos;
- az AI nem mutálhat state-et közvetlenül.

Nyitott:

- a termékruntime ugyanazt az engine-t használja-e, mint a Python batch;
- sidecar, C# vagy más runtime esetén milyen adapter szükséges;
- hol fut a későbbi tanuló vagy nagyobb erőforrású AI.

### CQ-ABIL-001 – Ability-rendszer tényleges current állapota

**Státusz:** `answered` státuszszinten, `queued_after_language_gate` implementációszinten

Bizonyított current állapot:

- `ability_registry.json` létezik, de deklaratív foundation;
- jelenleg 2 modul szerepel `declared_only` állapotban;
- `engine_support.json` szerint a kártyák supportja még `not_evaluated`;
- `runtime_executes_abilities: false`;
- nincs működő ability executor;
- a 814 runtime-kártya jelenléte nem jelenti a képességeik engine-támogatását.

Következmény:

- ability executor nem előzheti meg a runtime-nyelvi döntést;
- előbb Wellspring, erőforrás, `play_card`, timing, phase és priority alap kell;
- az `ABILITY_MODULE_SYSTEM.md` részletes történeti tervként megmarad;
- a benne szereplő Python–GDScript executor-kérdést Python–C#–GDScript–más jelöltekre kell érteni;
- új párhuzamos ability current dokumentum nem készül.

---

## 6. Hivatalos szabályforrásból ellenőrzött gameplay-kérdések

Forrás: `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`, különösen az Aktív állapot, Aura, Beáramlás, Ébredés, Kimerítés, Kimerült állapot, Költség és Magnitúdó fogalmi pontjai.

### CQ-WS-001 – Ősforrás authoritative tagság

**Státusz:** `queued_after_language_gate`

Technikai irány:

- `wellspring_card_instance_ids` listás PlayerState-zóna;
- stabil serialization-sorrend;
- registry zone `wellspring`;
- activity `active` vagy `exhausted`;
- visibility `owner_only`;
- listás zóna és registry kétirányú invariáns.

### CQ-WS-002 – Resource summary

**Státusz:** `answered`

A szabályforrás alapján:

- a játékos Magnitúdója alapesetben az Ősforrásban lévő lapok száma;
- a Magnitúdó kijátszási küszöb, nem költődik el;
- az elérhető Aura az Aktív Ősforrás-lapokból származik;
- minden Aktív Ősforrás-lap 1 Aurát biztosít;
- a Kimerült Ősforrás-lap nem biztosít Aurát;
- az Aura fizetése Aktív forráslapok Kimerítésével történik.

Engine-következmény:

- ne legyen külön authoritative `magnitude`, `spent_aura` vagy `remaining_aura` mező;
- a summary a Wellspring-listából és activity state-ből származzon;
- a Magnitúdó változása zónatagságból következzen, ne külön számlálómódosításból.

### CQ-WS-003 – Ősforrás visibility

**Státusz:** `needs_visibility_decision`

A forrás a normál Beáramlás lapját képpel lefelé helyezi az Ősforrásba, de a player-facing digitális információs policy nincs teljesen meghatározva.

Eldöntendő:

- mindkét játékos látja-e a teljes Magnitúdót;
- mindkét játékos látja-e az Aktív/Kimerült forrásszámot;
- a saját játékos látja-e a saját face-down forrás Card_ID-ját;
- az ellenfél csak countot lát-e;
- instance ID soha ne szivárogjon player-facing outputba.

### CQ-INFLOW-001 – Normál Beáramlás alapműködése

**Státusz:** `answered`

A szabályforrás alapján:

- a Beáramlás a kör második fázisa;
- opcionális;
- a játékos legfeljebb 1 lapot helyezhet a kezéből az Ősforrásba;
- a lap képpel lefelé kerül;
- a normál Beáramlás azonnal növeli a Magnitúdót, mert nő az Ősforrás lapszáma;
- külön kártyahatással történő további Ősforrásba helyezés nem számít bele a normál legfeljebb 1 lapba, hacsak a hatás másként nem rendelkezik.

### CQ-INFLOW-002 – Beáramláskor belépő lap activity state-je

**Státusz:** `needs_source_decision`

A forrás ezt mondja:

- a lap növeli a Magnitúdót;
- „későbbi körökben Aktív állapotban Aurát biztosíthat”.

Ez nem mondja ki elég egyértelműen:

- Aktív vagy Kimerült állapotban érkezik-e;
- használható-e Aura fizetésére ugyanabban a körben;
- ha Kimerülten érkezik, az Ébredés fázisban áll-e először vissza;
- ha Aktívan érkezik, miért szerepel a „későbbi körökben” korlátozó megfogalmazás.

Ezt nem szabad hallgatólagos engine-defaulttal eldönteni. Külön emberi Core-szabálydöntés szükséges.

### CQ-INFLOW-003 – Timing, priority és reakció

**Státusz:** `partly_answered`, `needs_engine_design`

Lezárt:

- a normál Beáramlás a külön Beáramlás fázisban történik;
- opcionális fáziscselekvés;
- nem a Manifesztáció vagy Eloszlás normál cselekvése.

Nyitott:

- kell-e formális priority a végrehajtásához;
- nyílik-e reakcióablak a lap kiválasztása vagy elhelyezése előtt/után;
- a „nem helyezek lapot” külön pass action legyen-e;
- a phase controller automatikusan kínálja-e fel a döntést.

### CQ-INFLOW-004 – Körönkénti maximum technikai nyilvántartása

**Státusz:** `partly_answered`, `needs_engine_design`

Szabályi rész lezárt:

- normál Beáramlással legfeljebb 1 lap helyezhető körönként;
- külön kártyahatásból származó Ősforrás-bővítés ettől elkülönül.

Engine-rész nyitott:

- explicit per-turn flag vagy counter;
- ne event log visszakereséséből kelljen kiszámolni;
- normál Beáramlás és effect-alapú `move_to_wellspring` külön cause/reason értéket kapjon.

### CQ-INFLOW-005 – Eventmodell

**Státusz:** `needs_engine_design`

Kötelező legalább:

- hand → wellspring `zone_move`;
- face-down/visibility és cause adatok;
- state-version és event-sequence konzisztencia.

Eldöntendő:

- elegendő-e a generic `zone_move` `cause: normal_inflow` értékkel;
- vagy külön `inflow` typed event is szükséges UI-, replay- és diagnostics-célra.

### CQ-RES-001 – Magnitúdó-preflight

**Státusz:** `partly_answered`, `needs_engine_design`

Szabályi rész lezárt:

- `magnitude = wellspring_card_count` alapesetben;
- Magnitúdó nem költődik el;
- egy lap csak akkor játszható ki, ha a játékos Magnitúdója eléri a lap követelményét és az Aura-költség is fizethető.

Engine-rész nyitott:

- strukturált success/failure result;
- modifier és override későbbi támogatása;
- a runtime-kártya Magnitúdó-mezőjének canonical olvasása;
- pontos diagnostics reason code-ok.

### CQ-RES-002 – Aura-típusok és laptípus szerinti fizetés

**Státusz:** `partly_answered`, `needs_lookup_audit`

Szabályi rész lezárt:

- Entitás saját Birodalmi Aurából, Aether/Semleges Aurából vagy ezek kombinációjából fizethető;
- Ige, Rituálé, Jel és Sík alapértelmezés szerint saját Birodalmi Aurához kötött;
- nem-Entitás lap Aether/Semleges Aurával csak explicit kivétel alapján fizethető;
- Soft Penalty nem aktív Core-szabály.

Még ellenőrizendő:

- canonical runtime Aura-type értékek;
- Birodalomértékek és Aether/Semleges pontos LOOKUPS reprezentációja;
- többértékű vagy wildcard költségek formája;
- explicit kártyaszöveges kivételek structured reprezentációja.

### CQ-RES-003 – Payment source selection

**Státusz:** `partly_answered`, `needs_engine_design`

Lezárt szabályi alap:

- csak Aktív Ősforrás-lap használható fizetésre;
- a kiválasztott forráslap Kimerül;
- Kimerült forrás nem fizethet újra visszaállításig.

Nyitott technikai kérdések:

- automatikus vagy kézi forrásválasztás;
- több azonos eredményű payment kezelése;
- külön payment action vagy a play request payloadja;
- determinisztikus rendezés;
- atomikus kimerítés és rollback.

### CQ-RES-004 – Ébredés és forrás-Visszaállítás

**Státusz:** `answered` szabályi szinten

- az Ébredés fázisban a játékos minden Kimerült lapját visszaállítja, hacsak szabály vagy kártyahatás másként nem rendelkezik;
- ez az Ősforrásban lévő lapokra is vonatkozik;
- a Visszaállítás Kimerült → Aktív állapotváltozás.

Engine-következmény:

- a turn/phase rendszernek az Ősforrás activity state-jét is frissítenie kell;
- az eventmodell még külön technikai döntés.

### CQ-RES-005 – Activity mutation event

**Státusz:** `needs_engine_design`

Eldöntendő:

- önálló typed `activity_state_changed` event;
- vagy payment-, attack-, block- és awakening-event payload;
- azonos kártya több activity változásának sorrendje;
- player-facing és debug payload elhatárolása.

---

## 7. Prioritási összefoglaló

### Lezárt Codex nélküli előkészítés

1. Termékruntime- és telepítési követelmények.
2. Windows 10+ 64-bit, portable-first és adminjog nélküli futás.
3. Runtime-nyelvi döntési kapu, kizáró feltételek és pontozás.
4. Tanulóprogram-audit sablon és `fourth turn` auditqueue.
5. Nyelvfüggetlen comparison fixture specifikáció.
6. Történeti Open Questions és Decisions technológiai triázsa.
7. Ability-rendszer tényleges current státuszának ellenőrzése.
8. Beáramlás–Ősforrás–Magnitúdó–Aura szabályforrás-auditja.

### Következő Codex-prioritás

1. `fourth turn` read-only Batch 0 leltár és licencleltár.
2. Canonical comparison fixture artifactok.
3. Python sidecar + Godot proof.
4. Godot .NET/C# rules-runtime proof.
5. Portable Windows-, contract-, stabilitási és karbantarthatósági összevetés.
6. Szükség esetén minimal GDScript vagy más proof.
7. A/B/C/D döntési jelentés és emberi jóváhagyás.

### Codex nélküli következő munkasáv

1. Az `ABILITY_MODULE_SYSTEM.md` elejének és technológiai szakaszainak aktualizálása ugyanabban a fájlban.
2. A hosszú `CONTRACT_SPECIFICATION.md` további konszolidációja a meglévő migration map alapján.
3. A Beáramlás activity-state kérdés emberi szabálydöntésének előkészítése.
4. Wellspring visibility-policy döntési lehetőségeinek előkészítése.
5. A LOOKUPS Aura-type és fizetési értékeinek későbbi célzott auditja.

A Python engine megmarad működő referenciának. Jelentős új gameplay-réteg a nyelvi/runtime döntési kapu lezárása előtt ne induljon. Új dokumentum csak akkor készülhet, ha a tartalomnak nincs természetes helye meglévő aktív főfájlban.