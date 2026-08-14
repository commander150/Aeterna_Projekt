# AETERNA Game Engine – Open Questions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.0  
**Dátum:** 2026-07-20  
**Státusz:** aktív kanonikus kérdés- és döntésikapu-regiszter  
**Kapcsolódó válasznapló:** `OPEN_QUESTIONS_DECISIONS.md`  
**Beolvasztott átmeneti fájl:** `CURRENT_OPEN_QUESTIONS.md`  
**Aktuális repository-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Ez a fájl az AETERNA Game Engine összes nyitott, részben megválaszolt, elhalasztott és már lezárt OQ-tételének központi indexe.

A részletes döntések az `OPEN_QUESTIONS_DECISIONS.md` fájlban maradnak. A lezárt kérdések nem törlődnek: `answered` státusszal megmaradnak a döntések visszakereshetősége érdekében.

A korábbi `CURRENT_OPEN_QUESTIONS.md` külön prioritásrétege megszűnik. A benne lévő:
- kérdések és fennmaradó kapuk ebbe a regiszterbe;
- elfogadott válaszok és döntések a válasznaplóba;
- elavult prioritások a Git-történetbe

kerülnek.

## Státuszok

| Státusz | Jelentés |
|---|---|
| `open` | Nincs még elégséges döntés vagy bizonyíték. |
| `partly_answered` | Az alapirány eldőlt, de maradt részletes döntési vagy implementációs kapu. |
| `deferred` | Valós kérdés, de későbbi mérföldkőhöz tartozik. |
| `answered` | Megválaszolva; a részletes döntés a válasznaplóban és/vagy célfájlban szerepel. |

## Összesítés

- `open`: 2
- `partly_answered`: 43
- `deferred`: 7
- `answered`: 22
- összes OQ: 74

## Használati szabály

1. Új kérdés csak egyedi OQ-azonosítóval vehető fel.
2. Az eredeti kérdés és a fennmaradó döntési kapu itt marad.
3. A döntés és indoklás az `OPEN_QUESTIONS_DECISIONS.md` fájlba kerül.
4. `answered` státusz csak akkor adható, ha a döntés visszakereshető.
5. Implementációs hiány nem nyitja újra automatikusan a már eldöntött szabályi vagy architektúrakérdést.
6. Playtest új bizonyíték alapján felülvizsgálatot indíthat, de csak explicit, verziózott emberi döntés módosít canonical szabályt.
7. A végső dokumentumaudit során minden OQ-hivatkozást és célfájlt újra ellenőrizni kell.

---

## 1. Projektirány és architektúra
### OQ-ARCH-001 – Régi és új Python motor szerepe

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** A production authoritative runtime C#; a Python referencia-, adat-, audit-, AI- és batch-tooling. A régi motorból csak célzott, auditált logika emelhető át.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ARCH-001`

### OQ-ARCH-002 – Runtime nyelv és integrációs modell

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Godot/GDScript vizuális kliens, C# egyetlen authority, Python külső tooling. Két párhuzamos kanonikus motor nem tartható fenn.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ARCH-002`

### OQ-ARCH-003 – UI és rules engine szétválasztása

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** A UI action requestet küld; a C# engine validál és mutál. A Godot bridge nem tartalmazhat játékszabályt.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ARCH-003`


## 2. Dokumentáció és fájlstátusz
### OQ-DOC-001 – DOCX → Markdown migráció

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Az engine-dokumentáció Markdown-alapú. A hivatalos szabályfőforrások egyelőre DOCX-ek. Hátralévő kapu: a másik dokumentummappa teljes auditja és az esetleges olvasói DOCX/PDF export.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DOC-001`

### OQ-DOC-002 – Checkpointok kezelése

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Egy aktív `ENGINE_CHECKPOINT.md` és külön történeti `CHECKPOINTS.md` marad a `docs/checkpoints/` mappában.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DOC-002`

### OQ-DOC-003 – Dokumentumszaporodás elkerülése

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Elsődlegesen meglévő aktív fájlt frissítünk. Új dokumentum csak önálló canonical szerep esetén készülhet. Minden aktív dokumentum verziót, dátumot és státuszt kap.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DOC-003`


## 3. Runtime package és adatút
### OQ-DATA-001 – Compiled runtime package szükségessége

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** A validált, manifestes runtime package a program kötelező adatinputja; a nyers export köztes, audit- vagy debug-output.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-001`

### OQ-DATA-002 – Google Sheets → XLSX → runtime package adatút

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Az adatút és publish pipeline működik. Hátralévő kapu: végleges package identity, build/output mappaszerkezet, source fingerprint és release policy.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-002`

### OQ-DATA-003 – Engine support státusz és blokkolás

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** A support státusz és futási mód szerinti blocking alapmodell elfogadott. Hátralévő kapu: production C# support checker és kártyacoverage-policy.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-003`

### OQ-DATA-004 – Legacy alias és canonical értékek

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** `normalization_aliases.json` és a LOOKUPS legacy réteg iránya rögzített. Hátralévő kapu: dangerous/audit_required esetek teljes auditja és visszavezetési policy.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-004`

### OQ-TECH-004B – Python build pipeline hosszú távú szerepe

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** A Python marad az export, normalizálás, validáció, package build, diagnostics, fixture-, AI- és batch-tooling elsődleges rétege.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-004B`

### OQ-DATA-005 – Build pipeline és változásérzékelés

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Az explicit teljes build helyes első lépés. Hash/fingerprint és cache csak későbbi optimalizáció; a correctness elsődleges.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-005`

### OQ-DATA-006 – Duplikált sample/runtime package mappák

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Canonical szerkesztési forrás egyik sem. A Godot-mappa consumption copy. Hátralévő kapu: a történeti sample mappák végleges archiválása vagy eltávolítása.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DATA-006`


## 4. Snapshot és visibility
### OQ-SNAP-001 – Snapshot típusok

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Aktív alap: viewer-specifikus player-visible snapshot és külön debug snapshot. Spectator-, replay- és külön AI-contract későbbi feladat.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-001`

### OQ-SNAP-002 – Pecsétmodell snapshotban

**Státusz:** `open`  
**Aktuális kérdés / fennmaradó kapu:** Döntendő a Pecsét létrehozási, láthatósági és állapotmodellje; HP-mező nem használható.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-002`

### OQ-SNAP-003 – Ősforrás láthatóság és állapot

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** A Magnitúdó, az Aktív/Kimerült darabszám és activity publikus; a saját kártyaazonosság owner-visible; az ellenfélnek redacted.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-003`

### OQ-SNAP-004 – Rejtett információ és visibility

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** A viewer-specifikus projection és fair-AI elv elfogadott. Hátralévő kapu: face-down Jel, spectator, replay és PvP visibility-audit.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-004`

### OQ-SNAP-005 – Pending decision és döntési ablak

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** A snapshot külön pending/priority állapotot hordozzon. A pontos reaction/targeting/payment/combat window schema későbbi gameplay-spec.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-005`

### OQ-SNAP-006 – Event log a snapshotban

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** A snapshot nem teljes történeti dump; csak rövid recent/visible event ablakot és indexet tartalmazhat. A teljes log külön contract.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-SNAP-006`


## 5. Legal actions
### OQ-LA-001 – Enabled és disabled actionök

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Player-facing és fair AI nézetben enabled actionök; debugban disabled actionök strukturált reasonnel is megjelenhetnek.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-001`

### OQ-LA-002 – Reakcióablak modell

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Core timing/priority + pending reaction window az irány. A stack/chain, prevention, replacement és trigger-sorrend későbbi szabálykapu.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-002`

### OQ-LA-003 – Combat actionök

**Státusz:** `open`  
**Aktuális kérdés / fennmaradó kapu:** A támadás, célpont, blokkolás és Pecsétfeltörés action/event modellje combat rules spec után dönthető el.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-003`

### OQ-LA-004 – Fizetés és Aura

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Az explicit, engine-validált payment source selection és `none|forced|choice` modell elfogadott. Temporary Aura, alternate cost és modifier-rendszer nyitott.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-004`

### OQ-LA-005 – Targeting

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Egyszerű target a play request része lehet; komplex target külön pending döntés. A partial resolution és retarget szabályok nyitottak.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-005`

### OQ-LA-006 – UI mezők a legal actionben

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Minimális UI-hint megengedett, de nem szabályforrás. Hosszú távon lokalizációs kulcs és paraméterezés szükséges.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-006`

### OQ-LA-007 – AI legal action mezők

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** A fair AI ugyanazt az enabled legal action listát kapja. Heurisztika külön policy-réteg, nem canonical rules mező.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-LA-007`


## 6. Action request / response
### OQ-AR-001 – Request azonosítás

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Request ID szükséges; a pontos idempotencia és hálózati policy a későbbi interaktív/PvP réteghez tartozik.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-001`

### OQ-AR-002 – Snapshot frissesség és state_version

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Az expected state version kötelező authority-guard; stale request reject és nem mutálhat állapotot.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-002`

### OQ-AR-003 – Action ID élettartama

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Az action ID az adott state version/legal action lista kontextusában érvényes; állapotváltozáskor érvénytelen.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-003`

### OQ-AR-004 – Többlépcsős targeting és pending állapot

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** A komplex választás authoritative pending state-ben tárolandó. Invalidáció, cancel és visszakérdezés részletes szabályai nyitottak.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-004`

### OQ-AR-005 – Action response és reakcióablak

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** A response és az új snapshot jelezheti a pending reactiont; a teljes reaction resolution contract későbbi feladat.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-005`

### OQ-AR-006 – Partial resolution státuszok

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Alap státuszszókészlet rögzített, de a `partially_resolved`, `prevented`, `replaced`, `cancelled` pontos szabálypéldái hiányoznak.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-006`

### OQ-AR-007 – Unsupported feature action közben

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Az engine nem találgathat; reject/not_executable és diagnostics szükséges. A player-safe event és release blocking részletes policy későbbi.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AR-007`


## 7. Event log
### OQ-EVENT-001 – Event részletesség

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Typed, gameplay-szintű eventek és külön debug/system réteg az irány. A teljes event taxonomy gameplay-migrációval bővül.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-001`

### OQ-EVENT-002 – Explanation log

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Rövid távon player-safe message használható; hosszú távon localization key + params. Nem minden event igényel magyarázatot.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-002`

### OQ-EVENT-003 – Debug, audit és diagnostics kapcsolat

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Az event és diagnostics külön réteg, kölcsönös hivatkozással. A teljes correlation/schema még nyitott.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-003`

### OQ-EVENT-004 – Rejtett információ event logban

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Egy belső történetből viewer-specifikus, szűrt nézet készül. PvP előtt külön visibility-audit szükséges.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-004`

### OQ-EVENT-005 – Replay-kompatibilitás

**Státusz:** `deferred`  
**Aktuális kérdés / fennmaradó kapu:** Az eventek készítsék elő a replayt, de teljes replay-rendszer nem korai mérföldkő.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-005`

### OQ-EVENT-006 – Balance test eventek

**Státusz:** `deferred`  
**Aktuális kérdés / fennmaradó kapu:** A balanszgyanú futás utáni elemzés és külön report; a szükséges metrikák a stabil gameplay után véglegesíthetők.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-EVENT-006`


## 8. Diagnostics
### OQ-DIAG-001 – Severity és blocking

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** A severity és blocking külön mező. A critical alapból blokkoló; warning/audit_note alapból nem; balance_suspicion nem engine-hiba.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-001`

### OQ-DIAG-002 – Blocking szabályok futási módonként

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Development, publish és runtime külön szigorúságú. A production C# és release policy részletes kódmátrixa még hátra van.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-002`

### OQ-DIAG-003 – Diagnostics report formátum

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Elsődleges gépi JSON és emberi Markdown summary. A végleges schema és output-elhelyezés nyitott.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-003`

### OQ-DIAG-004 – Runtime visibility

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Player-facing csak rövid, safe hiba; developer/debug részlet külön. A konkrét UI és localization policy későbbi.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-004`

### OQ-DIAG-005 – LOOKUPS diagnostics

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Unknown/inactive/workflow-only aktív runtime érték publish előtt blokkol. A teljes enum- és alias-hibamátrix auditálandó.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-005`

### OQ-DIAG-006 – Balance suspicion

**Státusz:** `deferred`  
**Aktuális kérdés / fennmaradó kapu:** Nem blokkoló, emberi review-t igénylő futás utáni jelzés. Mintaszámok és küszöbök stabil AI/gameplay után.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-006`

### OQ-DIAG-007 – Diagnostics és checkpointok kapcsolata

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Checkpoint csak rövid summaryt és lényeges hibákat tartalmaz; a teljes diagnostics külön generált report.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-DIAG-007`


## 9. Ability module system
### OQ-ABIL-001 – Structured mezők részletessége

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** A structured mezők audit- és köztes réteg. Új oszlop csak ismétlődő executable igény alapján.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-001`

### OQ-ABIL-002 – Execution plan

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Nem kötelező minden laphoz korán. Előbb simple plan néhány képességhez; később generált, verziózott plan.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-002`

### OQ-ABIL-003 – Card-local fallback

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Csak átmeneti, explicit diagnostics/support státusszal; release-ben nem futhat csendben.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-003`

### OQ-ABIL-004 – Reaction system ability szinten

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Core timing engine nyitja az ablakot, ability hook ad lehetőséget. Stack/chain és trigger-sorrend nyitott.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-004`

### OQ-ABIL-005 – Keywordök MVP-támogatása

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Keyword registry és support státusz szükséges; a támogatott első keyword-készlet gameplay-prioritás alapján döntendő.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-005`

### OQ-ABIL-006 – Pecsét/Aeternal targetek

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Aeternal nem damage/heal target; Pecsét csak explicit ward effectekhez. A részletes target és event payload nyitott.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-006`

### OQ-ABIL-007 – Hatáscímkék szerepe

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Effect tag önmagában nem executable modul. Modul csak schema, target/condition, diagnostics, event és teszt után.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-007`

### OQ-ABIL-008 – Ability registry és runtime package

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** `ability_registry.json` foundation létezik. A production C# executor, module schema és coverage-policy későbbi.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-ABIL-008`


## 10. Technology decisions
### OQ-TECH-001 – Python hosszú távú szerepe

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Python külső tooling, referencia és AI/batch controller; nem production gameplay authority.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-001`

### OQ-TECH-002 – GDScript/Godot runtime alkalmassága

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Godot/GDScript vizuális kliens- és adapterréteg; nem authoritative rules runtime.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-002`

### OQ-TECH-003 – Python + GDScript/C# hibrid modell

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Elfogadott hibrid: Godot visual + C# authority + Python external tooling. Nincs megosztott kanonikus szabálymotor.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-003`

### OQ-TECH-004 – Runtime package mint technológiai határ

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Statikus, validált programadat; nem MatchState és nem rules engine. A Python és C# is ezt fogyasztja.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-004`

### OQ-TECH-005 – Godot headless/smoke stratégia

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Headless és visual proof működik. A végleges CI, export és warning policy production szakaszban zárandó.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-005`

### OQ-TECH-006 – Codex-feladatok bontása

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Rövid, célzott, tesztelhető scope; döntés és dokumentációs irányítás az asszisztens/felhasználó feladata; commit csak teljes PASS után.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-TECH-006`


## 11. AI / simulation / balance
### OQ-AI-001 – AI-vs-AI helye

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** A Python vezérli a C# headless authoritative engine-t; Godot nem kap külön párhuzamos AI rules motort.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-001`

### OQ-AI-002 – Fair AI és debug AI

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** Fair AI játékosnézetet kap és balanszmérés alapja; debug AI külön fejlesztői mód.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-002`

### OQ-AI-003 – AI heurisztika és legal actions

**Státusz:** `answered`  
**Aktuális kérdés / fennmaradó kapu:** AI a C# legal action listából választ; policy külön réteg; engine minden requestet validál.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-003`

### OQ-AI-004 – Balance suspicion forrása

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Több metrikából, nem csak winrate-ből. A konkrét modellek stabil gameplay és adatgyűjtés után.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-004`

### OQ-AI-005 – Winrate és klánidentitás

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Nem cél steril 50/50; identitás védendő. Mintaszámok és auditküszöbök később.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-005`

### OQ-AI-006 – Balance report

**Státusz:** `deferred`  
**Aktuális kérdés / fennmaradó kapu:** Később gépi JSON + emberi Markdown summary, stabil fair AI és gameplay után.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-006`

### OQ-AI-007 – Korábbi kártyajavítások visszaellenőrzése

**Státusz:** `deferred`  
**Aktuális kérdés / fennmaradó kapu:** Fair AI-vs-AI, deckvalidáció, support report és teljesebb gameplay után.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-AI-007`


## 12. Rules- és kártyaaudit
### OQ-RULES-001 – Hivatalos főforrás-audit

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Szükséges, de rétegezett és célzott formában. A teljes audit előtt stabilabb validation és engine-barát rules spec kell.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-001`

### OQ-RULES-002 – Játékosbarát szabálykönyv

**Státusz:** `deferred`  
**Aktuális kérdés / fennmaradó kapu:** Külön, későbbi magyarázó dokumentum; főforrás-audit és stabil gameplay után.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-002`

### OQ-RULES-003 – Engine/AI-barát szabályspecifikáció

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Kell külön MD-alapú, hivatalos forrásból származtatott spec. A részletes szerkezet és elkészítés időzítése nyitott.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-003`

### OQ-RULES-004 – Új teljes kártyaaudit időzítése

**Státusz:** `deferred`  
**Aktuális kérdés / fennmaradó kapu:** Előbb structured/LOOKUPS, diagnostics, support report, deckvalidáció és legalább részleges tesztmotor.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-004`

### OQ-RULES-005 – LOOKUPS és structured audit

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** Lépcsőzetesen indítható critical enumokkal és dangerous/legacy értékekkel. A teljes munkalista későbbi auditfeladat.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-005`

### OQ-RULES-006 – Kártyaszöveg és structured eltérés

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** A motor nem találgathat; eltérés diagnostics és szükség esetén blocking audit. A konkrét javítási workflow részletezendő.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-006`

### OQ-RULES-007 – Aeternal/Pecsét engine-spec

**Státusz:** `partly_answered`  
**Aktuális kérdés / fennmaradó kapu:** A HP nélküli alapmodell rögzített. A snapshot, combat, target, ward-break/restore és victory event payloadok részletesítendők.

**Döntésnapló:** `OPEN_QUESTIONS_DECISIONS.md / OQ-RULES-007`

---

## Dokumentumkezelési hatás

A repositoryba történő beillesztéskor:

1. ez a fájl lecseréli a meglévő `OPEN_QUESTIONS.md` tartalmát;
2. az új `OPEN_QUESTIONS_DECISIONS.md` vele együtt kerül be;
3. a `CURRENT_OPEN_QUESTIONS.md` csak a két új fájl és minden hivatkozás ellenőrzése után távolítható el;
4. az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` szándékos kérdés–válasz dokumentumpárként megmarad;
5. új `CURRENT_OPEN_QUESTIONS.md` vagy más párhuzamos current OQ-fájl nem készülhet.
