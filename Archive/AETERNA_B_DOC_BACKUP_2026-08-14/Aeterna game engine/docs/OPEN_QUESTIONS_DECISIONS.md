# AETERNA Game Engine – Open Questions Decisions

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.0  
**Dátum:** 2026-07-20  
**Státusz:** aktív kanonikus válasz- és döntésnapló  
**Kapcsolódó kérdésregiszter:** `OPEN_QUESTIONS.md`  
**Beolvasztott átmeneti fájl:** `CURRENT_OPEN_QUESTIONS.md`  
**Aktuális repository-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Ez a fájl az `OPEN_QUESTIONS.md` OQ-tételeihez tartozó elfogadott, részleges vagy elhalasztó döntéseket rögzíti.

A 2.0-s konszolidáció:
- megőrzi a kérdés–válasz dokumentumpárt;
- beolvasztja a `CURRENT_OPEN_QUESTIONS.md` újabb döntéseit;
- felülírja a korábbi, már elavult Python–GDScript vagy nyitott runtime-jelölti irányokat;
- nem törli a történeti indoklást a Git-történetből;
- egyértelműen elválasztja az eldöntött irányt a még hiányzó implementációtól.

## Általános döntési elvek

1. A hivatalos játékszabályforrás az elsődleges.
2. Az aktuális canonical szabály az engine és a tesztek számára kötelező.
3. Playtesteredmény önmagában nem módosít szabályt; explicit, verziózott emberi döntés szükséges.
4. Egy meccsnek pontosan egy authoritative state-je lehet.
5. A production authoritative runtime C#/.NET.
6. A Godot/GDScript vizuális kliens- és adapterréteg.
7. A Python külső adat-, audit-, fixture-, AI-, batch- és elemzőtooling, valamint referenciaimplementáció.
8. A UI és az AI nem találgathat legalitást; a C# engine legal actiont ad és minden requestet újra validál.
9. A player-facing output nem szivárogtathat rejtett információt.
10. A runtime package statikus, validált programadat, nem MatchState és nem rules engine.
11. A dokumentációt meglévő aktív fájlok frissítésével, egységes verziózással és későbbi tartalomvesztés nélküli konszolidációval kell kezelni.

---

## OQ-ARCH-001 / OQ-ARCH-002 / OQ-ARCH-003 – Runtime és réteghatárok

**Aktív döntés – 2026-07-20:**

- `Aeterna.Engine` lesz az egyetlen production authoritative rules runtime.
- A Godot/GDScript feladata a scene, input, UI, animáció, hang, debugnézet és a C#-eredmények megjelenítése.
- A Python marad runtime package builder, validátor, audit-, AI-, batch-, scenario- és elemzőtooling.
- A Python minimal engine referencia és comparison oracle.
- A Python-sidecar proof `COMPLETE_AND_FROZEN`.
- A C# in-process proof `COMPLETE_AND_ACCEPTED`.
- A GDScript authoritative proof nem szükséges.
- A Godot és C# közvetlen in-process kapcsolatot használ; köztük nincs TCP/HTTP/gRPC.
- A Python a C# headless hostot kezdetben subprocess + JSON/JSONL interfészen használja.
- Két külön production authoritative rules engine fenntartása tilos.
- A bridge nem tartalmazhat játékszabályt.

**Státusz:** mindhárom OQ `answered`.

---

## OQ-DOC-001 / OQ-DOC-002 / OQ-DOC-003 – Dokumentáció

**Aktív döntés:**

- Az engine-dokumentáció aktív formátuma Markdown.
- A hivatalos 1.4v szabályfőforrások egyelőre DOCX formában maradnak.
- Egy aktív technikai checkpoint marad: `docs/checkpoints/ENGINE_CHECKPOINT.md`.
- A történeti mérföldkőnapló külön `CHECKPOINTS.md`.
- Új dokumentum csak önálló canonical szerep esetén készülhet.
- Minden aktív dokumentum kap verziót, dátumot, státuszt és egyértelmű szerepet.
- A `CURRENT_` előtag eltávolítandó, ha nincs indokolt párfájl.
- Párfájl esetén előbb tartalmi összevetés és merge-döntés szükséges.
- Törlés és archiválás csak teljes audit, érvényes utódfájl és felhasználói jóváhagyás után történhet.
- Az engine-dokumentáció után az `Aeterna dokumentációk/` mappa külön auditja, majd keresztmappa-ellenőrzés következik.

**Státusz:** OQ-DOC-002 és OQ-DOC-003 `answered`; OQ-DOC-001 `partly_answered`.

---

## OQ-DATA-001 / OQ-DATA-002 / OQ-DATA-005 / OQ-DATA-006 / OQ-TECH-004B – Runtime package és pipeline

**Aktív döntés:**

- A validált, manifestes runtime package a program kötelező statikus adatinputja.
- Godot és a production C# engine nem olvas közvetlenül XLSX-et.
- A Python pipeline végzi az XLSX exportot, normalizálást, validációt, diagnosticsot, package buildet és publish-t.
- A nyers JSONL/CSV/TSV köztes vagy audit-output.
- A Godot `runtime_package/` consumption copy.
- A publish előtt candidate build és blocking validation szükséges.
- A teljes újragenerálás az elsődleges correctness-path; hash/cache/fingerprint csak későbbi optimalizáció.
- A TEMP staging rövid távon elfogadható, de nem végleges buildarchitektúra.
- A történeti sample package mappák nem canonical források; végleges archiválásuk/eltávolításuk dokumentumaudit része.

**Nyitva marad:**

- production package identity;
- schema/ruleset version policy;
- source fingerprint;
- release output mappaszerkezet;
- rollback és integritásvédelem.

---

## OQ-DATA-003 / OQ-DATA-004 / OQ-DIAG-001 / OQ-DIAG-002 / OQ-DIAG-005 / OQ-AR-007 – Diagnostics és support

**Aktív döntés:**

- A `severity` és a `blocking` külön mező.
- Alap severity-k: `info`, `audit_note`, `warning`, `error`, `critical`, `balance_suspicion`.
- `critical` alapból blocking.
- `warning` és `audit_note` alapból nem blocking.
- `balance_suspicion` nem engine-hiba és nem blokkol.
- Development, publish és runtime/action execution külön szigorúsági profil.
- Publish előtt blokkol az aktív runtime schemahiba, ismeretlen enum, veszélyes alias, visibility-hiba és futtathatóként jelölt unsupported tartalom.
- Runtime közben unsupported logikát az engine nem találgathat és nem hajthat végre részlegesen: reject/not_executable + diagnostics.
- Biztonságos alias auto-normalizálható; veszélyes vagy kétértelmű alias emberi review.
- Aktív runtime mezőben unknown/inactive/workflow-only érték publish előtt blocking.
- Engine support státuszok: `supported`, `partial`, `unsupported`, `not_checked`, `fallback_required`, `manual_review_required`.

**Nyitva marad:** a teljes production C# code-lista, coverage-policy és részletes hibamátrix.

---

## OQ-SNAP-001 / OQ-SNAP-003 / OQ-SNAP-004 / OQ-SNAP-005 / OQ-SNAP-006 – Projection és visibility

**Aktív döntés:**

- Az authoritative MatchState nem player-facing contract.
- Két alapnézet: viewer-specifikus `player_visible_snapshot` és külön `debug_snapshot`.
- A fair AI ugyanazt a player-visible snapshotot használja, mint az emberi játékos.
- Saját kéz owner-visible; ellenfél kéz count/redacted; deck count-only; discard és Domain public az aktív szabály szerint.
- A teljes Magnitúdó és az Ősforrás Aktív/Kimerült darabszáma publikus.
- A saját Ősforrás-lapok kártyaazonossága owner-visible.
- Az ellenfél nem láthatja a face-down Ősforrás-lapok kártyaazonosságát.
- Player-facing output nem tartalmaz technikai card instance ID-t.
- A snapshot külön pending/priority állapotot hordozhat.
- A snapshot nem tartalmazza a teljes event logot; rövid visible/recent ablak és index megengedett.
- A debug output teljesebb lehet, de egyértelműen elkülönített.

**Nyitva marad:** Pecsét-láthatóság, face-down Jel, spectator/replay és teljes pending-window schema.

---

## OQ-SNAP-002 / OQ-ABIL-006 / OQ-RULES-007 – Aeternal és Pecsét

**Rögzített szabályi döntés:**

- Az Aeternal maga a játékos.
- Az Aeternalnak nincs HP-ja.
- Nem kaphat sebzést és nem gyógyítható.
- A Pecsét nem HP-alapú objektum.
- A Pecsét feltörési/visszaállítási eseményként kezelendő.
- Ha sem Entitás, sem fennálló Pecsét nem véd, egy célba érő támadás azonnali vereséget okoz.
- Aeternal nem általános damage/heal target.
- Pecsétre csak explicit ward effectek alkalmazhatók.
- Kerülendő: `player_damage`, `aeternal_damage`, `heal_aeternal`, `seal_damage`, `ward_damage`.
- Preferált események: `ward_broken`, `ward_restored`, `ward_break_prevented`, `aeternal_unprotected`, `direct_attack_victory`, `player_defeated`.

**Nyitva marad:** Pecsét létrehozása, visibility, snapshot-state, combat/effect payload és restore actionmodell.

---

## OQ-LA-001 / OQ-LA-007 / OQ-AR-002 / OQ-AR-003 – Legal action authority

**Aktív döntés:**

- A legal action listát kizárólag az authoritative engine számítja.
- Normál player-facing és fair AI nézetben enabled actionök jelennek meg.
- Debug nézet disabled actiont is adhat strukturált reasonnel.
- A fair AI nem kap rejtett információt vagy külön authoritative legalitást.
- Minden action request tartalmaz match/player/request/action/state contextet.
- Az expected state version kötelező authority-guard.
- Stale request reject; nem változik state version, event sequence vagy request.
- Az action ID csak az adott state version/legal action lista kontextusában érvényes.
- A frontend és AI nem küld authoritative költséget vagy legalitásdöntést.

---

## OQ-LA-004 / CQ-RES-002 / CQ-RES-003 – Aura és payment

**Aktív Core-döntés:**

- Magnitúdó küszöb, nem költődik el.
- Alapesetben a Magnitúdó az Ősforrás-lapok száma.
- Minden Aktív Ősforrás-lap 1 Aurát ad; Kimerült nem.
- Aura fizetése Aktív forráslapok Kimerítésével történik.
- A forrás Aura-identitása alapesetben a forráslap Birodalma.
- Entitás saját Birodalmi és AETHER támogató Aurából vagy kombinációból fizethető.
- Ige, Rituálé, Jel és Sík alapból csak saját Birodalmi Aurából fizethető.
- AETHER más Birodalom nem-Entitását alapból nem fizeti.
- Soft Penalty nem aktív Core-szabály.

**Engine-döntés:**

- A payment a `play_card` request atomikus része.
- A legal action payment contextet ad.
- Selection mode: `none`, `forced`, `choice`.
- `choice` módban játékosi megerősítés szükséges.
- Az engine validálja a források tulajdonát, activityjét, egyediségét, Aura-identitását és pontos költségét.
- Az első implementációban túlfizetés nem engedélyezett.
- Hiba esetén nincs részleges Kimerítés, mozgás, state-version növekedés vagy gameplay event.

**Nyitva marad:** cost modifier, temporary Aura, alternate cost, wildcard és teljes Magnitúdó-preflight result.

---

## CQ-INFLOW-001…006 – Normál Beáramlás

A `CURRENT_OPEN_QUESTIONS.md` CQ-azonosítói e válasznaplóban megőrzött, már elfogadott döntések. A kérdésregiszterben nem kapnak új párhuzamos OQ-azonosítót; a production gameplay-spec során a megfelelő phase/action contracthoz kapcsolódnak.

**Aktív döntések:**

- A Beáramlás a kör második, opcionális fázisa.
- Normál Beáramlással körönként legfeljebb 1 kézlap kerül az Ősforrásba.
- A lap face-down és Aktív állapotban érkezik.
- Már ugyanabban a körben használható Aura fizetésére.
- Azonnal növeli a Magnitúdót és az elérhető Aurát.
- Fizetéskor Kimerül.
- Ez az aktív állapotra vonatkozó Core-döntés a hivatalos főforrás következő verziójába átvezetendő.
- A normál Beáramlás nem váltakozó priority-ablak és nem nyit automatikusan reakciót.
- Legal actionök: `perform_inflow` és `skip_inflow`.
- Turn-scoped státusz: `pending | performed | skipped`.
- Accepted action atomikus: hand → wellspring, owner-only visibility, active state, status update, summary recalc, egyszeri state-version növekedés, determinisztikus eventek.
- Első eventmodell: `zone_move` + `phase_transition`; külön duplikált inflow event nem szükséges.

**Megjegyzés:** a canonical technikai fázisnév `infusion`; a korábbi `inflow` contractnevek terminológiai migrációt igényelnek.

---

## OQ-LA-002 / OQ-AR-005 / OQ-ABIL-004 – Reaction

**Aktív irány:**

- A core rules engine nyitja/zárja a reaction windowt.
- Az ability hook jelzi az elérhető reaction/trigger/prevention/replacement lehetőséget.
- A snapshot pending state és a legal action lista együtt írja le a döntést.
- Nincs valódi döntés esetén az ablak automatikusan átugorható.
- Burst és Jel ugyanabba a reaction keretrendszerbe kerülhet külön subtype-pal.
- A stack/chain, prevention/replacement és trigger-sorrend nem lezárt; rules audit és prototype szükséges.

---

## OQ-LA-005 / OQ-AR-004 / OQ-AR-006 – Targeting és részleges feloldás

**Aktív irány:**

- Egyszerű target a play/action request payload része lehet.
- Többlépcsős vagy többcélpontos választás authoritative pending state.
- A frontend csak az engine targeting adataiból emel ki; nem dönt legalitásról.
- Alap response fogalmak használhatók: accepted, rejected, resolved, partially_resolved, pending_decision, pending_reaction, prevented, replaced, cancelled, failed, not_executable.

**Nyitva marad:** retarget, invalid target, partial resolution, prevention és replacement pontos szabálypéldái.

---

## OQ-EVENT-001…006 – Event log

**Aktív döntés:**

- A snapshot az állapot; az event log a történet.
- Typed, determinisztikus eventek szükségesek.
- Player-visible módban gameplay-szintű, visibility-szűrt események.
- Debug/system részletek külön réteg.
- Egy belső történetből viewer-specifikus event projection készül.
- Fair AI ugyanazt a visible logot kapja, mint a játékos.
- Diagnostics és event külön réteg, opcionális kölcsönös hivatkozással.
- A teljes replay nem MVP-követelmény, de event index/state version/correlation előkészítendő.
- A balance suspicion nem gameplay event; futás utáni report.

**Nyitva marad:** teljes taxonomy, explanation/localization schema, replay runner és balance report.

---

## OQ-DIAG-003 / OQ-DIAG-004 / OQ-DIAG-006 / OQ-DIAG-007 – Diagnostics output

**Aktív döntés:**

- Elsődleges gépi forma JSON.
- Emberi olvasásra Markdown summary.
- Player-facing csak safe, rövid üzenet.
- Debug/developer részlet elkülönítve.
- Diagnostics nem szivárogtathat hidden informationt.
- Checkpoint csak összesítést és lényeges problémát tartalmaz; teljes dump külön report.
- Balance suspicion nem automatikus szabálymódosítás.

---

## OQ-ABIL-001…008 – Ability module rendszer

**Aktív döntés:**

- A kártyaszöveg emberi szabályszöveg.
- A structured ability és ability registry programlogikai köztes réteg.
- Hatáscímke önmagában nem executable modul.
- Új structured mező csak ismétlődő végrehajtási igény alapján.
- Nem kell korán minden kártyához teljes execution plan.
- Card-local fallback csak explicit, diagnosztizált átmeneti kivétel.
- Reaction core timing + ability hook modellben működik.
- Keyword registry és support státusz szükséges; nem minden keyword korai support.
- `ability_registry.json` a runtime package része/foundationje.
- Unsupported modul szerepelhet registryben, de nem futhat csendben.
- A production executor C#-ban készül.

**Nyitva marad:** C# module schema, első támogatott effectek/keywordök, execution plan és coverage.

---

## OQ-TECH-001…006 – Technológiai döntések

- OQ-TECH-001: `answered` – Python external tooling/reference.
- OQ-TECH-002: `answered` – Godot/GDScript visual layer.
- OQ-TECH-003: `answered` – Godot + C# + Python hibrid, egyetlen authority.
- OQ-TECH-004: `answered` – runtime package statikus adatcontract.
- OQ-TECH-005: `partly_answered` – headless/visual proof működik; CI/export/release policy későbbi.
- OQ-TECH-006: `answered` – Codex szűk, tesztelhető scope-ot kap; szabályi és projektirányítási döntést nem hoz.

---

## OQ-AI-001…007 – AI, simulation és balance

**Aktív döntés:**

- A Python koordinálja a C# headless engine futásait.
- A C# engine az authority; az AI csak legal actionből választ.
- Fair AI játékosnézetet használ; debug AI külön fejlesztői mód.
- AI decision policy külön, verziózott réteg.
- Nehézség nem jelenthet hidden-information hozzáférést.
- Balance suspicion több metrikából és futás utáni elemzésből keletkezik.
- Nem cél minden matchup 50/50-re húzása; a klánidentitás védendő.
- Tanuló AI csak későbbi kutatás, nem módosíthat szabályt vagy kártyaadatot.
- Valódi balanszméréshez stabil gameplay, deckvalidáció, visibility, diagnostics, event log és fair AI szükséges.

---

## OQ-RULES-001…007 – Rules- és kártyaaudit

**Aktív döntés:**

- A teljes főforrás- és kártyaaudit rétegezve történik.
- LOOKUPS/structured critical audit megelőzheti a teljes kártyaauditot.
- Később külön, MD-alapú engine/AI-barát szabályspec szükséges, a hivatalos főforrásból származtatva.
- A játékosbarát szabálykönyv külön, későbbi magyarázó dokumentum.
- A motor nem találgathat kártyaszöveg és structured adat eltérésekor.
- Runtime-supported státusz csak auditált, konzisztens adatnál adható.
- Az Aeternal/Pecsét HP nélküli alapmodell canonical; a részletes engine-spec későbbi.

**Aktuális auditirány:**

1. runtime package és source-inventory;
2. LOOKUPS/structured critical audit;
3. diagnostics és support report;
4. ability registry;
5. engine-barát rules spec;
6. Aeternal/Pecsét/timing/target/payment részspec;
7. scenario és smoke;
8. korábbi javítások visszaellenőrzése;
9. teljes kártyaaudit;
10. játékosbarát szabálykönyv.

---

## Termékruntime-döntések a korábbi current triázsból

- Elsődleges platform: 64 bites Windows 10+ asztali rendszer.
- Proof és zárt teszt: portable, kibontott mappa; telepítő nem szükséges.
- Normál futtatáshoz ne kelljen adminjog, Python, Godot Editor vagy .NET SDK.
- Kevés, közismert runtime prerequisite elfogadható.
- Mentések, logok és beállítások felhasználói írható helyre kerülnek.
- Linux, kódaláírás, pontos log retention és installer későbbi, nem blokkoló feladat.
- A production Windows packaging még bizonyítandó; ez nem nyitja újra automatikusan a C# nyelvi döntést.

---

## Dokumentumkezelési hatás

A repositoryba történő beillesztéskor:

1. ez a fájl lecseréli a meglévő `OPEN_QUESTIONS_DECISIONS.md` tartalmát;
2. az új `OPEN_QUESTIONS.md` vele együtt kerül be;
3. a `CURRENT_OPEN_QUESTIONS.md` csak a két fájl és minden hivatkozás ellenőrzése után távolítható el;
4. a régi, részletes döntésnapló a Git-történetben megmarad;
5. új döntés mindig meglévő OQ-azonosítóhoz vagy új, egyedi OQ-azonosítóhoz kerüljön;
6. ugyanahhoz az OQ-hoz későbbi felülíró döntés dátummal és indoklással kerüljön be, a korábbi döntés nyomának elvesztése nélkül.
