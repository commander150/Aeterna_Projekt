# AETERNA Game Engine – Current Open Questions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.8  
**Dátum:** 2026-07-15  
**Státusz:** aktív közeli döntési kapu-, OQ-triázs- és prioritáslista  
**Technikai referencia:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum a következő engine-, technológiai, termékruntime- és szabályintegrációs feladatokat közvetlenül befolyásoló kérdéseket tartalmazza.

Kapcsolódó aktív források:

- történeti kérdésregiszter: `OPEN_QUESTIONS.md`;
- történeti válaszregiszter: `OPEN_QUESTIONS_DECISIONS.md`;
- termékruntime-mérce: `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md`;
- runtime-nyelvi kapu és pontozás: `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`;
- comparison scenario: `RUNTIME_COMPARISON_FIXTURE_SPEC.md`;
- tanulóprogram-audit: `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md` és `LEARNING_PROJECT_AUDIT_QUEUE.md`;
- hivatalos szabályforrás: `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`.

Az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó. Ha régi státuszuk vagy megfogalmazásuk eltér ettől a current dokumentumtól, a jelen fájl aktuális triázsa az irányadó.

A Python minimal engine a jelenlegi működő referenciaimplementáció. A végleges authoritative termékruntime nyelve és futási modellje még nincs kiválasztva. A nyelvváltás nem önálló cél.

### Általános playtest-felülvizsgálati elv

Az AETERNA jelenlegi szabály- és balanszdöntései közül több elméleti tervezésre, szimulációra vagy részleges tesztre támaszkodik, mert még nem történt teljes, szabályhű valódi játékteszt.

Ezért:

- minden elfogadott döntés az aktuális rulesetben canonical és az engine számára kötelező;
- egy döntés nem válik opcionálissá pusztán azért, mert később tesztelni kell;
- szabályhű playtest alapján bármely szabály, balanszérték, Birodalom- vagy Klánidentitás felülvizsgálható;
- a playtest eredménye önmagában nem írja át a szabályt;
- módosításhoz explicit emberi döntés, döntésnapló és verziózott forrásátvezetés szükséges;
- az implementáció és az AI-teszt mindig az éppen hatályos canonical szabályt követi;
- a korábbi döntés és a változtatás oka visszakereshető marad.

---

## 1. Státuszok

| Státusz | Jelentés |
|---|---|
| `answered` | Megválaszolva és current döntésként rögzítve. |
| `partly_answered` | Van bizonyított rész, de maradt nyitott döntés. |
| `highest_priority_decision_gate` | A következő Codex-munkasáv elsődleges döntési feladata. |
| `needs_learning_project_audit` | Helyi tanulóprogram-audit szükséges. |
| `needs_comparison_fixture` | Canonical fixture-artifactok és összehasonlítás szükséges. |
| `needs_integration_prototype` | Működő runtime- vagy bridge-proof szükséges. |
| `needs_packaging_proof` | Portable Windows-csomagolási bizonyíték szükséges. |
| `needs_source_amendment` | A döntést a következő hivatalos szabályforrás-verzióba át kell vezetni. |
| `needs_lookup_audit` | Canonical runtime értékeket LOOKUPS-ból kell ellenőrizni. |
| `needs_engine_design` | Technikai contract-, state- vagy eventdöntés kell. |
| `queued_after_language_gate` | Definiált feladat, de a runtime-nyelvi döntés után folytatandó. |
| `deferred_non_blocking` | Nyitott, de a következő auditot vagy proofot nem blokkolja. |

---

## 2. Technológiai döntési kapu

| Eredeti OQ | Aktuális státusz | Aktuális értelmezés |
|---|---|---|
| `OQ-ARCH-001` | `partly_answered` | Az új Python minimal engine működő comparison-reference; a végleges termékruntime nyitott. |
| `OQ-ARCH-002` | `highest_priority_decision_gate` | Python sidecar, Godot .NET/C#, valamint indokolt esetben GDScript vagy más runtime összehasonlítása. |
| `OQ-ARCH-003` | `answered` | A UI nem szabályforrás; action requestet küld, az authoritative engine validál és mutál. |
| `OQ-TECH-001` | `partly_answered` | Python biztosan megmarad adatpipeline-, audit-, AI- és batch-toolingként. |
| `OQ-TECH-002` | `partly_answered` | A Godot loader/debug/UI szerepe bizonyított; teljes GDScript runtime csak célzott proof után értékelhető. |
| `OQ-TECH-003` | `highest_priority_decision_gate` | Kötelező fő proof-jelöltek: Python sidecar és Godot .NET/C#. |
| `OQ-TECH-004` | `answered` elvi szinten | A runtime package statikus programadat-contract, nem MatchState és nem rules engine. |
| `OQ-TECH-005` | `partly_answered` | Godot headless smoke működik; végleges CI- és exportpolicy későbbi részlet. |
| `OQ-TECH-006` | `answered` munkarendi szinten | Codex szűk, tesztelhető feladatot kap; a következő munka read-only audittal indul. |
| `OQ-AI-001` | `partly_answered` | Python AI/batch tooling megtartandó; a product runtime adaptere proof után dönthető el. |

Kötelező elvek:

- contract-first fejlesztés;
- pontosan egy authoritative MatchState;
- a Godot UI nem tartalmazhat rejtett szabálylogikát;
- két teljes authoritative motor tartós párhuzamos fenntartása kerülendő;
- a Python leváltása csak bizonyított termékakadály vagy lényegesen jobb alternatíva miatt indokolt;
- a végleges döntéshez audit, azonos fixture, packaging proof és emberi jóváhagyás kell.

Aktuális proof-sorrend:

1. `fourth turn` read-only Batch 0 leltár és licencleltár;
2. canonical comparison fixture-artifactok;
3. Python sidecar + Godot proof;
4. Godot .NET/C# rules-runtime proof;
5. portable Windows-, contract-, stabilitási és karbantarthatósági összevetés;
6. szükség esetén minimal GDScript vagy más célzott proof;
7. A/B/C/D döntési jelentés és emberi jóváhagyás.

---

## 3. Lezárt termékruntime-döntések

### CQ-PROD-001 – Platform

**Státusz:** `answered`

- 64 bites Windows 10 és újabb támogatott Windows asztali rendszer;
- 32 bites Windows nem cél;
- Linux később vizsgálható, de jelenleg nem prioritás.

### CQ-PROD-002 – Kiadási forma

**Státusz:** `answered`

- proofhoz és zárt teszthez portable, kibontott mappa;
- jelenleg nem kell telepítő;
- egyértelmű fő executable szükséges;
- telepítő csak későbbi, véglegesebb kiadásnál kell.

### CQ-PROD-003 – Jogosultság és prerequisite

**Státusz:** `answered` elvi szinten

- normál futtatáshoz ne kelljen adminjog;
- ne kelljen külön Python, Godot Editor, .NET SDK vagy fejlesztői toolchain;
- kevés közismert prerequisite, például szükséges .NET runtime elfogadható;
- mentések, beállítások és logok felhasználói írható helyre kerüljenek;
- a pontos Windows-könyvtár későbbi technikai döntés.

### CQ-PROD-004 – Nem blokkoló későbbi termékkérdések

**Státusz:** `deferred_non_blocking`

- Linux-port;
- csomagméret optimalizálása;
- digitális kódaláírás;
- mentési és logkönyvtár pontos helye;
- log retention és hibacsomag formátuma.

---

## 4. Aktuális architektúra- és runtime-kérdések

### CQ-ARCH-001 – Jelenlegi reference

**Státusz:** `partly_answered`

Biztos:

- Python minimal engine a működő és tesztelt reference implementation;
- Godot a loader-, registry-, debug- és későbbi UI-réteg;
- a frontend nem módosít authoritative state-et;
- a legalitást engine-contract adja.

Nyitott:

- Python sidecar vagy Godot .NET/C# lesz-e a product runtime;
- szükséges-e GDScript vagy más proof;
- melyik modell teljesíti legjobban a portable Windows-követelményeket.

### CQ-ARCH-002 – `fourth turn` audit

**Státusz:** `needs_learning_project_audit`

Első Codex-lépés kizárólag read-only leltár:

- projekthatárok és helyi útvonalak;
- repository URL, commit/tag/verzió;
- kód-, asset- és dependencylicencek;
- nyelvek, Godot-verzió és runtime-ok;
- authoritative state és engine/UI-határ;
- bridge, lifecycle, packaging és tesztek;
- clean-room módon használható minták.

### CQ-ARCH-003 – Comparison fixture

**Státusz:** `needs_comparison_fixture`

A specifikáció elkészült. Codexnek canonical Python artifactokat kell generálnia, majd azonos jelentéssel futtatnia a Python sidecar és C# proofban.

### CQ-ARCH-004 – Python sidecar proof

**Státusz:** `needs_integration_prototype`, `needs_packaging_proof`

- stdin/stdout JSONL vagy localhost TCP;
- verziózott handshake;
- action request/response és state-version guard;
- timeout, kapcsolatvesztés és kontrollált shutdown;
- külön Python-telepítés nélküli portable Windows-csomag;
- elárvult processz és antivírus false positive kockázata.

### CQ-ARCH-005 – Godot .NET/C# proof

**Státusz:** `needs_integration_prototype`, `needs_packaging_proof`

- tiszta C# rules library vagy elkülönített assembly;
- Godot-node-októl független MatchState és transitionök;
- azonos fixture és kompatibilis JSON-contract;
- unit és integration tesztek;
- portable Windows 10+ export;
- self-contained vagy egyszerű .NET runtime prerequisite;
- differential comparison a Python reference outputtal.

### CQ-ARCH-006 – Feltételes további nyelvek

**Státusz:** `deferred_non_blocking`

- GDScript csak akkor kap proofot, ha az audit vagy a két fő proof indokolja;
- C++ GDExtension, Rust vagy más nyelv csak erős, reprodukálható előny esetén kerül fő scope-ba;
- embedded Python jelenleg kutatási irány.

---

## 5. Runtime package, AI és ability-rendszer

### CQ-RUNTIME-001 – Runtime package

**Státusz:** `answered`

- validált statikus programadat-contract;
- Godot nem olvas közvetlenül XLSX-et;
- a builder/tooling Pythonban maradhat bármely product runtime mellett;
- a runtime package nem MatchState és nem szabálymotor;
- schema és package identity véglegesítése későbbi feladat.

### CQ-AI-001 – Python AI/batch tooling

**Státusz:** `partly_answered`

Biztos:

- Python AI-, audit-, batch- és balansztooling megtartandó;
- a Python engine differential reference marad;
- fair AI nem kaphat több információt, mint a játékos;
- az AI nem mutálhat state-et közvetlenül.

Nyitott:

- ugyanazt az engine-t használja-e a product runtime és a batch;
- más runtime esetén milyen adapter szükséges;
- hol fut a későbbi tanuló vagy nagyobb erőforrású AI.

### CQ-ABIL-001 – Ability-rendszer current állapota

**Státusz:** `answered` státuszszinten, `queued_after_language_gate` implementációszinten

- `ability_registry.json` deklaratív foundation;
- jelenleg 2 modul `declared_only` állapotban;
- a kártyák supportja `not_evaluated`;
- `runtime_executes_abilities: false`;
- nincs működő ability executor;
- a 814 runtime-kártya jelenléte nem jelent engine-támogatást;
- ability executor előtt Wellspring, Beáramlás, erőforrás, `play_card`, timing, phase és priority alap kell.

---

## 6. Ősforrás, Beáramlás, Magnitúdó és Aura

### CQ-WS-001 – Ősforrás authoritative state

**Státusz:** `queued_after_language_gate`

- listás PlayerState-zóna;
- registry zone `wellspring`;
- activity `active` vagy `exhausted`;
- stabil serialization-sorrend;
- belső card record visibility `owner_only`;
- listás zóna és registry kétirányú invariáns.

### CQ-WS-002 – Resource summary

**Státusz:** `answered`

- `magnitude = wellspring_card_count` alapesetben;
- a Magnitúdó küszöb, nem költődik el;
- minden Aktív Ősforrás-lap 1 Aurát biztosít;
- Kimerült forrás nem biztosít Aurát;
- Aura fizetése Aktív forráslapok Kimerítésével történik;
- ne legyen külön authoritative `magnitude`, `spent_aura` vagy `remaining_aura` mező.

### CQ-WS-003 – Ősforrás player-visible policy

**Státusz:** `answered`

**Emberi döntés – 2026-07-15:**

- a teljes Magnitúdó mindkét játékos számára nyilvános;
- az Aktív és Kimerült Ősforrás-lapok száma és activity state-je mindkét játékos számára nyilvános;
- a saját játékos a saját Ősforrás-lapjainak kártyaazonosságát később is visszanézheti;
- az ellenfél nem láthatja a képpel lefelé lévő Ősforrás-lapok kártyaazonosságát;
- az ellenfél csak a nyilvános count- és activity-információt kapja;
- technikai `card_instance_id` egyik játékos számára sem jelenhet meg player-facing outputban;
- player-visible outputhoz biztonságos, viewer-specifikus object reference vagy redacted rekord szükséges;
- debug output ettől elkülönítve tartalmazhat technikai azonosítókat.

Engine-következmény:

- owner snapshotban a saját forrás Card_ID-ja és megjelenítési adatai elérhetők;
- opponent snapshotban a forrás identity redacted;
- a nyilvános Magnitúdó és active/exhausted count nem származhat rejtett identity-adatból a frontendben, azt az engine projection adja;
- fair AI ugyanazt a visibility-policyt kapja, mint az azonos oldalon játszó emberi játékos.

### CQ-INFLOW-001 – Normál Beáramlás

**Státusz:** `answered`

- a kör második fázisa;
- opcionális;
- legfeljebb 1 lap helyezhető a kézből az Ősforrásba;
- a lap képpel lefelé kerül;
- azonnal növeli a Magnitúdót;
- effect-alapú további Ősforrásba helyezés nem fogyasztja el a normál Beáramlás keretét, hacsak a hatás másként nem rendelkezik.

### CQ-INFLOW-002 – Belépési activity és azonnali Aura

**Státusz:** `answered`, `needs_source_amendment`

**Emberi Core-döntés – 2026-07-15:**

- a normál Beáramlással az Ősforrásba kerülő lap Aktív állapotban érkezik;
- már ugyanabban a körben használható Aura fizetésére;
- azonnal növeli a Magnitúdót és az elérhető Aurát;
- fizetéskor Kimerül;
- a döntést a hivatalos főforrás következő verziójában egyértelműen át kell vezetni.

### CQ-INFLOW-003 – Timing, priority és reakció

**Státusz:** `partly_answered`, `needs_engine_design`

Lezárt:

- külön Beáramlás fázis;
- opcionális fáziscselekvés;
- nem Manifesztáció- vagy Eloszlás-cselekvés.

Nyitott:

- kell-e formális priority;
- nyílik-e reakcióablak;
- a kihagyás külön pass action legyen-e;
- a phase controller hogyan kínálja fel és zárja le a döntést.

### CQ-INFLOW-004 – Körönkénti maximum és event

**Státusz:** `partly_answered`, `needs_engine_design`

- normál Beáramlással legfeljebb 1 lap helyezhető körönként;
- effect-alapú Ősforrás-bővítés elkülönül;
- explicit per-turn flag vagy counter szükséges;
- hand → wellspring `zone_move`, `activity_state: active`, face-down visibility és `cause: normal_inflow` szükséges;
- eldöntendő, kell-e külön `inflow` typed event.

### CQ-RES-001 – Magnitúdó-preflight

**Státusz:** `partly_answered`, `needs_engine_design`

- Magnitúdó alapesetben a Wellspring lapszáma;
- nem költődik el;
- a lap Magnitúdó-küszöbének és Aura-fizethetőségének is teljesülnie kell;
- nyitott a strukturált result, modifier/override és diagnostics reason code.

### CQ-RES-002 – Aura-identitás és AETHER fizetési modell

**Státusz:** `answered`, `needs_source_amendment`, `needs_lookup_audit`

**Emberi Core-döntés – 2026-07-15:**

Az Aura forrásidentitása alapesetben az Ősforrás-lap Birodalma.

- ha a forrás Birodalma megegyezik a kijátszandó lap Birodalmával, a forrás saját Birodalmi Auraként használható;
- Entitás saját Birodalmi Aurából, AETHER/Aether-Semleges támogató Aurából vagy ezek kombinációjából fizethető;
- Ige, Rituálé, Jel és Sík alapértelmezés szerint csak saját Birodalmi Aurából fizethető;
- AETHER Birodalmi forrás AETHER Entitást és AETHER nem-Entitást saját Birodalmi Auraként fizethet;
- AETHER Birodalmi forrás más Birodalom Entitását Aether/Semleges támogató Auraként fizetheti;
- AETHER Birodalmi forrás más Birodalom Igéjét, Rituáléját, Jelét vagy Síkját alapértelmezés szerint nem fizetheti;
- ettől csak explicit szabály- vagy kártyahatás térhet el;
- Soft Penalty nem aktív Core-szabály.

Tervezési előzmény és playtest-státusz:

- az eredeti elképzelés szerint az AETHER Aura bármilyen laptípust fizethetett volna;
- ezt elméleti balansz alapján túl erősnek ítéltük és szűkítettük;
- az AETHER Birodalomnak a fizetési rugalmasságon kívül más identitása is van, ezért a korlátozott modell a jelenlegi canonical szabály;
- teljes, szabályhű valódi játékteszt hiányában ez különösen playtest-érzékeny döntés;
- ha az AETHER a gyakorlatban túl erősnek, túl gyengének vagy identitásában problémásnak bizonyul, explicit emberi döntéssel felülvizsgálható;
- felülvizsgálatig az engine és minden teszt a jelenlegi korlátozott modellt használja.

LOOKUPS- és engine-következmény:

- az `Aura` mező jelenleg numerikus Aura-költségként értelmezendő;
- első körben nem szükséges külön párhuzamos erőforráskészlet vagy önálló `Aura_Type` mező csak az AETHER kettős szerepe miatt;
- központi payment validator alkalmazza a forrás Birodalma, a fizetendő lap Birodalma és laptípusa szerinti szabályt;
- explicit kivételekhez később structured override szükséges;
- ideiglenes vagy generált Aura esetén az Aura-identitást külön, canonical módon meg kell adni;
- a LOOKUPS-ban ellenőrizendő a Birodalomértékek, költségmezők és explicit kivételek reprezentációja.

### CQ-RES-003 – Payment source selection

**Státusz:** `partly_answered`, `needs_engine_design`

Lezárt:

- csak Aktív Ősforrás-lap fizethet;
- a kiválasztott forrás Kimerül;
- Kimerült forrás nem fizethet újra Visszaállításig;
- a frissen Beáramlott Aktív lap ugyanabban a körben választható payment source-ként;
- a forrás fizetési jogosultságát a CQ-RES-002 szerinti Birodalom- és laptípus-policy határozza meg.

Nyitott:

- automatikus vagy kézi forrásválasztás;
- külön payment action vagy play request payload;
- determinisztikus rendezés;
- atomikus kimerítés és rollback.

### CQ-RES-004 – Ébredés és activity event

**Státusz:** `answered` szabályi szinten, `needs_engine_design` event szinten

- Ébredéskor minden Kimerült lap visszaáll, így a Kimerült Ősforrás-lapok is;
- Visszaállítás: `exhausted → active`;
- eldöntendő az önálló `activity_state_changed` event vagy a cause-specifikus event payload használata.

---

## 7. Prioritási összefoglaló

### Lezárt Codex nélküli előkészítés

1. Termékruntime- és telepítési követelmények.
2. Runtime-nyelvi döntési kapu és pontozás.
3. `fourth turn` auditqueue.
4. Nyelvfüggetlen fixture-specifikáció.
5. Történeti OQ-triázs.
6. Ability-rendszer current konszolidációja.
7. Contract-specifikáció első konszolidációs köre.
8. Beáramlás Core-döntése.
9. Ősforrás player-visible policy.
10. AETHER Aura fizetési modell és általános playtest-felülvizsgálati elv.

### Következő Codex nélküli munkasáv

1. A Beáramlás timing/priority/event kérdéseinek engine-tervezési előkészítése.
2. A payment source selection döntési lehetőségeinek előkészítése.
3. A LOOKUPS Birodalom-, Aura-költség- és explicit kivételértékeinek célzott ellenőrzése.
4. A current contract státusz frissítése csak akkor, amikor új implementáció készül.

A Python engine megmarad működő referenciának. Jelentős új gameplay-réteg a nyelvi/runtime döntési kapu lezárása előtt ne induljon. Új dokumentum csak akkor készülhet, ha a tartalomnak nincs természetes helye meglévő aktív főfájlban.