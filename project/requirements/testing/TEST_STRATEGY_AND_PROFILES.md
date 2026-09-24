---
artifact_id: AET-DOC-TEST-STRATEGY-PROFILES
kind: document
type: specification
version: "1.0"
lifecycle: active
integration: current
authority: operational-workflow
generated: false
depends_on:
  - AET-DOC-ENGINE-CHECKPOINT
supersedes: []
---

# AETERNA tesztstratégia és tesztprofilok

## 1. Cél

Ez a specifikáció az AETERNA current tesztstratégiáját és újrahasználható tesztprofiljait rögzíti. A cél a correctness-regressziók, broken mechanikák és balanszgyanúk szétválasztott, reprodukálható vizsgálata.

A dokumentum nem tesz történeti Python launchert current runtime-munkafolyamattá, és nem ad önmagában teljes balanszbizonyítékot.

## 2. Current architektúra és authority

- A C# engine az authoritative gameplay runtime.
- A Headless futtatás az automatizált authoritative meccs- és integrációs bizonyíték elsődleges útja.
- A Godot kliens a felhasználói és megjelenítési integrációt bizonyítja; önmagában nem helyettesíti a Headless correctness-vizsgálatot.
- A Python réteg reference/oracle szerepet tölthet be izolált összehasonlításban. Nem írhatja felül a C# authoritative engine eredményét.

Tesztparancs csak akkor tekinthető currentnek, ha a repository current, nem archív területén ténylegesen létezik és a feladat baseline-ján ellenőrizték. Történeti `simulation/test_launcher.py`, `simulation/interactive_match_cli.py` és `run_interactive_match_cli.py` útvonal nem current parancs.

## 3. Bizonyítéktípusok elválasztása

### 3.1 Correctness és regresszió

Determinista unit-, contract-, Headless- vagy integrációs teszt bizonyítja, hogy egy szabály, állapotátmenet vagy API-contract helyesen működik. Hibajel a crash, exception, illegal state, eltérő canonical eredmény, hiányzó vagy hibás action, illetve igazolt invariáns megsértése.

### 3.2 Smoke evidence

Néhány teljes meccs bizonyítja, hogy az adott build és konfiguráció elindul, halad és befejeződik, miközben alapvető actionök és logok megjelennek. A smoke PASS nem bizonyít balanszt, teljes mechanikai lefedettséget vagy statisztikai stabilitást.

### 3.3 Balansz- és broken-gyanú

Több seedet és megfelelő mintát használó futások mintázatot jelezhetnek. Egy kiugró meccs vagy egyetlen seed csak vizsgálati jelöltet ad. Balanszkövetkeztetéshez előre rögzített profil, összehasonlítható deckek, elegendő minta és a gameplay correctness külön PASS állapota kell.

## 4. Profile contract

Minden tesztprofil rögzítse:

- a stabil `test_profile_id`-t;
- a teszt célját és bizonyítási határát;
- a runner/runtime réteget;
- a matchup, realm, deck, mode, variant és scenario metadata-t;
- a seedet vagy seedlistát;
- az ismétlések számát;
- a build, ruleset, runtime package, policy és egyéb reprodukálhatósági identitást;
- az elvárt jeleket, mérőszámokat és PASS/FAIL feltételt.

A seed és a profilazonosító külön fogalom. Részletes contract: `project/requirements/testing/SEED_AND_REPRODUCIBILITY_CONVENTION.md`.

## 5. Nyolc current tesztprofil

### Profil 1 — általános Headless smoke

**Cél:** igazolni, hogy az authoritative runtime néhány normál teljes meccset kritikus hiba nélkül végigvisz.

**Beállítás:** 3–5 futás, explicit build/package identity, rögzített vagy naplózott seedek, támogatott random vagy kijelölt deckek.

**Figyelendő:** indulás, legal action előrehaladás, terminal result, kritikus exception, üres vagy megmagyarázhatatlanul elakadt játék. Ez smoke evidence, nem balanszkövetkeztetés.

### Profil 2 — azonos matchup több seeddel

**Cél:** elkülöníteni a stabil matchup-mintát az egyetlen seed zajától.

**Beállítás:** azonos build, ruleset, runtime package, deckek és policy; legalább több előre rögzített seed, seedenként azonos ismétlésszám.

**Figyelendő:** győzelmi eloszlás, meccshossz, döntő állapotok, első divergenciák és a célzott actionök gyakorisága. A kis minta csak gyanút jelez.

### Profil 3 — egy realm fókusz

**Cél:** egy realm tempójának, erőforrásmintájának és mechanikai elérhetőségének vizsgálata több ellenféllel.

**Beállítás:** a fókuszrealmhez rögzített valid deckek; több összehasonlítható matchup és seed.

**Figyelendő:** túl gyakori gyors győzelem, ismétlődő tempóminta, elmaradó vagy túlreprezentált summon, trap, source vagy más realmre jellemző esemény.

### Profil 4 — reakció/control kontra agresszió

**Cél:** a reakciók, trap/Jel viselkedés, védekezési ablakok és Pecsét-tempo gyakorlati ellenőrzése.

**Beállítás:** egy reakció- vagy control-orientált és egy gyorsabb támadó deck; több seed.

**Figyelendő:** legal reaction és priority ablakok, trap play/trigger, a védekező oldal tényleges válaszlehetősége, valamint a direkt sebzés és az explicit Pecsét-feltörés helyes elkülönítése.

### Profil 5 — gyors swarm kontra lassú control

**Cél:** tempó- és válaszablak-gyanúk feltárása.

**Beállítás:** validált, rögzített swarm és control deck, azonos policy, multi-seed kör.

**Figyelendő:** irreálisan gyors terminal result, korai Pecsét-feltörés, a lassú oldal érdemi legal actionjei és a board stabilizálhatósága.

### Profil 6 — hosszú meccs és erőforrás-kimerülés

**Cél:** deckfogyás, temető, overflow, ismétlődő állapot és hosszú távú terminal viselkedés ellenőrzése.

**Beállítás:** lassabb matchup vagy célzott scenario, magasabb turn budget, explicit timeout/termination policy.

**Figyelendő:** determinisztikus lezárás, kimerülési szabályok, overflow, újrakeverés ha a ruleset engedi, patthelyzet és ismétlődő action-ciklus.

### Profil 7 — célzott mechanika-regresszió

**Cél:** egy módosított mechanika és közvetlen szomszédos invariánsainak bizonyítása.

**Beállítás:** először szűk determinista unit/contract teszt, utána releváns Headless scenario vagy matchup azonos seedlistával pre-change és post-change állapotban.

**Figyelendő:** a javított ág tényleges végrehajtása, event/log evidence, blokkolt vagy fallback ág, szomszédos actionök és state transitionök. A profilnak konkrét PASS/FAIL oracle kell.

### Profil 8 — engine boundary és kliensintegráció smoke

**Cél:** a C# engine, Headless API és Godot kliens közötti state/action contract alapvető épségének ellenőrzése.

**Beállítás:** current contracttesztek, kis Headless facade-kör, majd a scope által indokolt Godot positive/negative smoke.

**Figyelendő:** snapshot/state, legal actions, action validation, action application, event stream, terminal result és hibás input kulturált elutasítása. Python oracle csak külön összehasonlító bizonyíték.

## 6. Multi-seed módszertan

1. Előre rögzítsd a profilt, matchupot, deckeket, policy-t, seedlistát és ismétlésszámot.
2. Ne cseréld a decket, buildet vagy policy-t ugyanazon aggregált kör közben.
3. Őrizd meg a futásonkénti eredményt; az összesítés ne rejtse el a seedhez kötött hibát.
4. A győzelmi arány mellett mérd legalább a meccshosszt, terminal okot, releváns action/event számot és a célzott mechanika előfordulását.
5. A statisztikai következtetés mellett közöld a mintanagyságot és a bizonytalanságot.

## 7. Pre-change/post-change regresszió

A változtatás előtt rögzített baseline ugyanazt a profilt, seedlistát és inputidentitást használja, mint a változtatás utáni kör. A két oldal között csak a vizsgált build vagy explicit adatváltozás térjen el.

Az összevetés sorrendje:

1. correctness és invariánsok;
2. terminal állapot és meccshossz;
3. célzott action/event evidence;
4. csak ezek PASS állapota után győzelmi vagy balanszminta.

Egy elvárt mechanikai változás okozhat szándékos divergenciát. Ilyenkor a review-nak meg kell neveznie az első várt eltérést és igazolnia kell, hogy a további eredmény a módosított contracttal konzisztens.

## 8. Broken- és balanszheurisztikák

Broken-gyanú többek között:

- crash, exception, hang vagy végtelen ciklus;
- az authoritative engine és a contractteszt igazolt eltérése;
- legal action végrehajthatatlansága vagy illegal action elfogadása;
- rossz zóna, hibás időzítés, hiányzó terminal result;
- egy mechanika több seedben következetesen kimarad vagy hibásan fut.

Balanszgyanú többek között:

- ugyanaz a deck, lap vagy stratégia sok összehasonlítható seedben aránytalanul dominál;
- rendszeresen túl rövid vagy túl hosszú meccs;
- tartósan hiányzó válaszablak;
- költség, kockázat és hatás feltűnően torz aránya;
- ugyanaz a board- vagy tempóminta több matchupban is döntő.

Ezek jelölők, nem automatikus ítéletek. Előbb ki kell zárni az adat-, ruleset-, AI-policy- és runtime-hibát.

## 9. Kötelező evidence és riportálás

Egy tesztkör riportja tartalmazza:

- a profil- és futásazonosítókat;
- a teljes reproducibility identity elérhető részeit;
- a parancsot vagy runner-verziót;
- futásszámot, seedlistát és exit code-ot;
- PASS/FAIL/SKIP számot;
- a nyers bizonyíték elérési helyét vagy hashét;
- a smoke, correctness és balance következtetést külön;
- minden ismert korlátot.

Review artifact a Git által ignorált `TEMP/` alatt tartható. A current következtetést azonban a megfelelő managed artifactban, issue-ban vagy jóváhagyott project recordban kell rögzíteni.

## 10. Minimális változtatási kapu

Runtime-változtatás után minimum:

1. a módosított réteg szűk determinista tesztje;
2. a közvetlen contract- és regressziós tesztek;
3. releváns Headless smoke;
4. szükség esetén Godot integrációs smoke;
5. pre-change/post-change vagy multi-seed kör, ha a változás gameplay-mintát érint;
6. diff-, scope- és source-integrity review.

Dokumentációs vagy tooling-only változásnál a gameplay suite elhagyható, ha engine/runtime/data implementáció nem változott; a dokumentum-, metadata-, generálási és path-kapukat akkor is teljesíteni kell.
