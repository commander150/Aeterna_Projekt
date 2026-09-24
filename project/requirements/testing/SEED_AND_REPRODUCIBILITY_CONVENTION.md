---
artifact_id: AET-DOC-SEED-REPRODUCIBILITY
kind: document
type: specification
version: "1.0"
lifecycle: active
integration: current
authority: operational-workflow
generated: false
depends_on:
  - AET-DOC-ENGINE-CHECKPOINT
  - AET-DOC-TEST-STRATEGY-PROFILES
supersedes: []
---

# AETERNA seed- és reprodukálhatósági konvenció

## 1. Döntés és hatókör

Ez a specifikáció a tesztfutások azonosítását és reprodukálhatósági adatait választja szét. A kötelező döntés:

```text
RNG seed != test_profile_id
```

A `seed` kizárólag a véletlenszám-generátor bemenete. A `test_profile_id` egy külön, stabil tesztprofil-azonosító. A matchup, realm, mode, variant, scenario és futási cél külön metadata. Egyik sem kódolható kötelező jelentésként a seed számjegyeibe.

Ez dokumentációs és testing-requirements contract. Nem módosít engine-implementációt.

## 2. Elkülönített fogalmak

### 2.1 RNG seed

Az RNG seed egy egész szám vagy a runtime által elfogadott ekvivalens érték, amely inicializálja a meghatározott RNG-folyamatot. A seedből nem következik a tesztprofil, a két játékos realmje, a matchup, a mód, a variáns vagy a scenario.

Ugyanaz a seed eltérő build, ruleset, runtime package, deck, AI policy vagy bemenetsor mellett eltérő eredményhez vezethet. A seed önmagában ezért nem replay-azonosító és nem teljes reprodukálhatósági garancia.

### 2.2 `test_profile_id`

A `test_profile_id` ember és tooling által olvasható stabil azonosító egy teszt szándékához és alapbeállításához. Példák:

```text
SMOKE-RANDOM
MATCHUP-MULTI-SEED
MECHANIC-REGRESSION-TRAP
BOUNDARY-HEADLESS
```

A profil azonosítója nem egy konkrét futást azonosít. Egy profilhoz több seed, matchup-variáns és ismétlés tartozhat.

### 2.3 Tesztmetadata

A futás jelentését külön mezők adják meg. A releváns mezők:

- `player1_realm` és `player2_realm`;
- `matchup_id`, ha a matchupnak stabil neve van;
- `mode`;
- `variant`;
- `scenario_id`, vagy explicit `null` normál teljes meccsnél;
- `run_purpose`;
- `games` vagy az ismétlési policy;
- a használt deckek és test/AI policy-k azonosítója.

A realm-azonosítók szöveges canonical értékek. Ha tooling numerikus realm-kódot is használ, az külön lookup-adat; nem változtatja a seed jelentését.

### 2.4 Reproducibility identity

Egy futás megismétléséhez vagy bizonyító erejű összehasonlításához legalább conceptually rögzíteni kell:

- engine/build identity;
- ruleset identity;
- runtime-package identity és/vagy hash;
- mindkét deck identityje vagy tartalmi hash-e;
- test policy és AI policy identity;
- RNG seed;
- a szükséges RNG stream identity és stream-hozzárendelés;
- full replay esetén az action/input history.

Ha ezek közül egy releváns elem hiányzik, az eredmény legfeljebb az elérhető adatok szintjén ismételhető; nem állítható teljes replay-egyezés.

## 3. Reprodukálhatósági szintek

### 3.1 Diagnosztikai újrafuttatás

Azonos profil, build, ruleset, package, deck, policy és seed használata. Célja egy megfigyelt hiba vagy minta visszaidézése. Ez erős bizonyíték lehet, de külön RNG streamek vagy külső bemenetek eltérése még megváltoztathatja az eredményt.

### 3.2 Determinisztikus összehasonlítás

A pre-change és post-change futás minden releváns identitása azonos, kivéve a vizsgált változtatást. A rögzített action/input history vagy egy bizonyítottan determinisztikus policy lehetővé teszi a divergencia első pontjának meghatározását.

### 3.3 Full replay

Full replay csak akkor állítható, ha a build- és adatidentitások mellett az összes szükséges RNG stream és az action/input history is rögzített, és a runtime igazoltan képes ezeket ugyanabban a sorrendben visszajátszani. Azonos seed önmagában nem full replay.

## 4. Ajánlott futásrekord

```yaml
test_profile_id: MATCHUP-MULTI-SEED
seed: 548721
player1_realm: AQUA
player2_realm: AETHER
matchup_id: AQUA-AETHER-RESOURCE
mode: normal
variant: resource-observation
scenario_id: null
run_purpose: deck-hand-source-resource regression
games: 5
engine_build: <commit-or-build-id>
ruleset_id: <ruleset-id>
runtime_package_sha256: <sha256>
player1_deck_id: <deck-id-or-hash>
player2_deck_id: <deck-id-or-hash>
test_policy_id: <policy-id>
ai_policy_id: <policy-id>
rng_streams: <stream-manifest-or-null>
action_history: <replay-reference-or-null>
```

Az egyes futásokhoz a `seed` és a `test_profile_id` is kötelező, ha RNG-t használó profilról van szó. A `variant` a profil értelmes alváltozatát nevezi meg; egy puszta futássorszám külön `run_id` vagy ismétlési index legyen.

## 5. Profilek, scenario és futási cél

A test profile a mérési szándékot és az alapbeállítást adja meg. A matchup metadata megnevezi a résztvevő oldalakat és deckeket. A `mode` a futtatási mód, a `variant` a profil értelmes változata, a `scenario_id` pedig egy előkészített állapot vagy forgatókönyv azonosítója.

`scenario_id: null` normál teljes meccset jelent: nincs előre beállított különleges board state. Ez nem jelenti azt, hogy a run identity többi része elhagyható.

A `run_purpose` röviden rögzíti, mit bizonyít vagy figyel a futás, például resource flow, heal/buff/lock, destroy/discard/graveyard, reaction/trap vagy célzott mechanika-regresszió.

## 6. Multi-seed és regresszió

Multi-seed vizsgálatnál ugyanazt a profilt és metadata-készletet több, külön rögzített seed mellett kell futtatni. Egy seedhez tartozó ismétlések és a külön seedek eredményei ne mosódjanak össze. A pre-change/post-change összehasonlítás ugyanazt a seedlistát és ugyanazokat az identitásokat használja, és külön rögzíti a vizsgált buildváltozást.

## 7. SUPERSEDED PROPOSAL: `PPQQMVV`

A korábbi `PPQQMVV` javaslat a seed számjegyeibe kódolta a P1 és P2 realmet, a futási módot és a variánst. Például a `0207001` értéket AQUA–AETHER normál futás első variánsaként értelmezte.

Ez a modell **SUPERSEDED PROPOSAL**. Nem canonical RNG seed formátum, nem használható a tesztmetadata kizárólagos hordozójaként, és új tooling nem építhet rá kötelező jelentést.

A javaslat hasznos szándéka megmarad külön mezőkben:

- a realm és matchup explicit metadata;
- a mode, variant és scenario explicit metadata;
- az emberileg kereshető profilnév `test_profile_id`;
- a futás visszakereshetősége külön run record;
- az RNG bemenet a jelentés nélküli `seed` mező.

Korábbi logban vagy történeti dokumentumban előforduló `PPQQMVV` értéket historical/proposal evidence-ként lehet értelmezni, current contractként nem.

## 8. Felelősségi határ

Az authoritative C# engine felel a tényleges RNG-használatért és a runtime-viselkedésért. A Headless futtatásnak, a Godot kliensnek és a Python reference/oracle rétegnek ugyanazokat a különválasztott identitásokat kell átadnia vagy rögzítenie, amikor az adott teszt ezt igényli. A Python réteg nem helyettesítheti a C# authoritative eredményt.

A szükséges serializálás, stream-kezelés vagy replay-motor későbbi implementációs feladat. Ez a dokumentum a fogalmi és metadata-contractot rögzíti.
