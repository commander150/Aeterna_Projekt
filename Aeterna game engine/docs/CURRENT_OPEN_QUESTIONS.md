# AETERNA Game Engine – Current Open Questions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.0  
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

### CQ-INFLOW-001 – Normál Beáramlás szabályi alap

**Státusz:** `answered`

- a kör második fázisa;
- opcionális;
- legfeljebb 1 lap helyezhető a kézből az Ősforrásba;
- a lap képpel lefelé kerül;
- effect-alapú további Ősforrásba helyezés nem fogyasztja el a normál Beáramlás keretét, hacsak a hatás másként nem rendelkezik.

### CQ-INFLOW-002 – Belépési activity és azonnali Aura

**Státusz:** `answered`, `needs_source_amendment`

**Emberi Core-döntés – 2026-07-15:**

- a normál Beáramlással az Ősforrásba kerülő lap Aktív állapotban érkezik;
- már ugyanabban a körben használható Aura fizetésére;
- azonnal növeli a Magnitúdót és az elérhető Aurát;
- fizetéskor Kimerül;
- a döntést a hivatalos főforrás következő verziójában egyértelműen át kell vezetni.

### CQ-INFLOW-003 – Timing, priority és phase controller

**Státusz:** `answered` tervezési szinten, `queued_after_language_gate` implementációszinten

**Engine-döntés – 2026-07-15:**

- a normál Beáramlás az aktív játékos saját, egyszeri fázisdöntése;
- nem váltakozó priority-ablak;
- nem nyit automatikusan reakciós ablakot;
- csak explicit szabály, kártyaszöveg vagy trigger nyithat reakciós ablakot;
- a kihagyás action neve `skip_inflow`, nem `pass_priority`;
- a normál legal actionök: `perform_inflow` minden jogosult saját kézlaphoz, valamint `skip_inflow`;
- ha nincs jogosult kézlap és nincs külön fázisdöntés, a phase controller automatikusan kihagyhatja;
- elfogadott döntés után újabb normál Beáramlás nem választható;
- a phase controller stabil állapotban, a kötelező trigger/pending/reaction rendezése után Manifesztációra lép.

### CQ-INFLOW-004 – Körönkénti állapot és legalitás

**Státusz:** `answered` tervezési szinten, `queued_after_language_gate` implementációszinten

Turn-scoped authoritative állapot:

- `normal_inflow_status: pending | performed | skipped`;
- a saját Beáramlás fázis elején `pending`;
- sikeres `perform_inflow` után `performed`;
- sikeres vagy automatikus kihagyás után `skipped`;
- a következő saját kör Beáramlás fázisához új döntési állapot jön létre.

### CQ-INFLOW-005 – Action és atomikus transition

**Státusz:** `answered` tervezési szinten, `queued_after_language_gate` implementációszinten

`perform_inflow` minimális preconditionjei:

- helyes match és expected state version;
- a kérelmező az aktív játékos;
- current phase `inflow`;
- `normal_inflow_status == pending`;
- a kiválasztott card instance a játékos saját kezében van;
- nincs explicit tiltó szabály vagy effect.

Elfogadott transition:

1. hand → wellspring;
2. face-down, belső `owner_only` visibility;
3. `activity_state: active`;
4. `normal_inflow_status: performed`;
5. resource summary újraszámítása;
6. state version pontosan egyszeri növelése;
7. determinisztikus eventek.

Reject esetén nincs részleges mutation vagy gameplay event.

### CQ-INFLOW-006 – Eventmodell

**Státusz:** `answered` első implementációs irányként

Első körben nem készül külön, tartalmilag duplikált `inflow` typed event.

Sikeres `perform_inflow`:

1. `zone_move` `cause: normal_inflow`, `activity_state_after: active`;
2. `phase_transition` `cause: normal_inflow_performed`.

Sikeres `skip_inflow`:

- csak `phase_transition`, `cause: normal_inflow_skipped`.

Egy accepted action egyszer növeli a state versiont; több ordered event tartozhat ugyanahhoz a resulting verzióhoz.

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

- ha a forrás Birodalma megegyezik a kijátszandó lap Birodalmával, saját Birodalmi Auraként használható;
- Entitás saját Birodalmi Aurából, AETHER/Aether-Semleges támogató Aurából vagy ezek kombinációjából fizethető;
- Ige, Rituálé, Jel és Sík alapértelmezés szerint csak saját Birodalmi Aurából fizethető;
- AETHER forrás saját AETHER Entitást és AETHER nem-Entitást saját Birodalmi Auraként fizethet;
- AETHER forrás más Birodalom Entitását Aether/Semleges támogató Auraként fizetheti;
- AETHER forrás más Birodalom nem-Entitását alapértelmezés szerint nem fizetheti;
- ettől csak explicit szabály- vagy kártyahatás térhet el;
- Soft Penalty nem aktív Core-szabály.

A korlátozott modell jelenlegi canonical szabály, de szabályhű playtest után explicit, verziózott emberi döntéssel felülvizsgálható.

### CQ-RES-003 – Payment source selection

**Státusz:** `answered` tervezési szinten, `queued_after_language_gate` implementációszinten

**Engine-döntés – 2026-07-15:**

#### Contract és UX elhatárolása

- a fizetési contract mindig explicit, végleges forráslistát tartalmaz;
- az első implementációban a payment a `play_card` request része, nem külön action;
- a kliens nem küld authoritative költséget, csak az engine által kiadott legal action alapján kiválasztott forrásreferenciákat;
- az engine minden requestnél újra ellenőrzi a tényleges költséget és a források jogosultságát.

Tervezett request-mező:

- `payment_source_refs: []` – state-versionhöz kötött, player-safe forrásreferenciák rendezett listája.

Technikai `card_instance_id` player-facing requestben nem használható.

#### Payment selection mode

A legal action három mód egyikét adja:

- `none` – a fizetendő Aura 0; a forráslista üres;
- `forced` – pontosan egy jogszerű forráskészlet van; a frontend automatikusan kitöltheti és elküldi az explicit listát;
- `choice` – több jogszerű forráskészlet van; a játékosnak ki kell választania a végleges forrásokat.

A `choice` módban a felület adhat engine által számított javaslatot, de nem fizethet automatikusan játékosi megerősítés nélkül. Ennek oka, hogy a konkrétan Kimerített forrás identitása későbbi hatások, triggerek, visszaállítások vagy playtest során jelentős lehet.

#### Legal action payment-context

A `play_card` legal action legalább a következő származtatott adatot adja:

- Aura-költség;
- `payment_selection_mode`;
- szükséges forrásszám;
- determinisztikusan rendezett `eligible_payment_source_refs`;
- `forced_payment_source_refs`, ha a mód `forced`;
- strukturált disabled reason, ha nincs jogszerű fizetés.

Nem kötelező minden lehetséges kombinációt előre felsorolni, mert ez kombinatorikus növekedést okozhat.

#### Determinisztika

- eligible források canonical sorrendje: Wellspring zone index, majd stabil player-safe reference;
- a requestben kapott forráslistát az engine canonical sorrendre normalizálja;
- duplikált reference invalid;
- azonos state és választás azonos normalizált payment resultot ad;
- a deterministic baseline AI `choice` esetén az első jogszerű kombinációt választja canonical sorrendben;
- fejlettebb AI ettől eltérhet, de csak legal actionből és saját látható információból választhat.

#### Minimális payment-validáció

Az engine mutation előtt ellenőrzi:

1. helyes match, player, action és expected state version;
2. a kijátszandó lap current state-ben továbbra is kijátszható;
3. a Magnitúdó-küszöb teljesül;
4. minden payment reference feloldható és a fizető játékos saját Ősforrás-lapjára mutat;
5. minden forrás `active`;
6. minden forrás egyszer szerepel;
7. minden forrás Aura-identitása jogosult a CQ-RES-002 szerint;
8. a forrásszám és az összesített Aura pontosan megfelel a normalizált költségnek;
9. 0 költségnél csak üres forráslista érvényes;
10. az első implementációban túlfizetés nem engedélyezett.

Kedvezmény, alternatív költség, ideiglenes Aura vagy explicit override esetén előbb az engine normalizálja a fizetendő költséget, és csak utána validálja a forráslistát.

#### Atomikus transition

A payment nem külön előzetes mutation.

Sikeres `play_card` actionben egyetlen atomikus tranzakció része:

1. teljes preflight és payment-validáció;
2. kiválasztott Ősforrás-lapok `active → exhausted` állapotváltása;
3. a kijátszandó lap megfelelő zónatransitionje;
4. szükséges entry/placement state;
5. state version pontosan egyszeri növelése;
6. determinisztikus payment-, zone- és play eventek.

Bármely hiba esetén:

- nincs részleges Kimerítés;
- nincs kártyamozgás;
- nincs költségvesztés;
- nincs state-version növekedés;
- nincs gameplay event.

#### Response és visibility

A normalizált `payment_result` tartalmazhatja:

- kifizetett Aura mennyiségét;
- normalizált source reference listát;
- forrásszámot;
- felhasznált Aura-identitások összegzését;
- `selection_mode` értéket.

Owner-facing output láthatja a saját források Card_ID-ját. Opponent-facing output csak a nyilvános forráspozíciót vagy activity-változást láthatja, a face-down kártyaazonosságot nem.

### CQ-RES-004 – Activity mutation event

**Státusz:** `answered` szabályi szinten, `needs_engine_design` event szinten

- Ébredéskor minden Kimerült lap visszaáll, így a Kimerült Ősforrás-lapok is;
- Visszaállítás: `exhausted → active`;
- eldöntendő az önálló `activity_state_changed` event és a cause-specifikus payment/attack/awakening eventek pontos viszonya.

### CQ-RES-005 – LOOKUPS és explicit payment override

**Státusz:** `needs_lookup_audit`

Ellenőrizendő:

- canonical Birodalomértékek;
- az `Aura` mező mint numerikus költség;
- AETHER és Aether/Semleges fizetési szerep reprezentációja;
- ideiglenes vagy generált Aura identitása;
- kedvezmény, alternatív költség és wildcard;
- explicit nem-Entitás payment override structured értékei.

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
11. Normál Beáramlás timing-, priority-, phase-controller- és eventmodellje.
12. Payment source selection contract-, UX-, determinisztikai és atomikus transition modellje.

### Következő Codex nélküli munkasáv

1. LOOKUPS Birodalom-, Aura-költség- és explicit kivételértékeinek célzott ellenőrzése.
2. Magnitúdó-preflight strukturált result és diagnostics iránya.
3. Activity mutation event általános policyje.
4. `play_card` precondition és transition előkészítése csak a runtime-nyelvi kapu sorrendjének megtartásával.
5. Current contract státusz frissítése csak akkor, amikor új implementáció készül.

A Python engine megmarad működő referenciának. Jelentős új gameplay-réteg a nyelvi/runtime döntési kapu lezárása előtt ne induljon. Új dokumentum csak akkor készülhet, ha a tartalomnak nincs természetes helye meglévő aktív főfájlban.