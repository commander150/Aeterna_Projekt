# AETERNA – ProjectIgnis/CardScripts ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-26
- **Státusz:** repository-forrásokra épülő első teljes AETERNA-központú elemzés
- **Javasolt későbbi repository-útvonal:** `learning/analyses/projectignis__cardscripts.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Kapcsolódó forráslista:** az aktuális verziózott „AETERNA – LEARNING FORRÁSPROJEKTEK NYILVÁNTARTÁSA” dokumentum
- **Repository:** `ProjectIgnis/CardScripts`
- **Stabil upstream URL:** `https://github.com/ProjectIgnis/CardScripts`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `6b150b8471fbd713ad786ee3d8c1384a471c45f1`
- **Vizsgált commit dátuma:** 2026-07-26
- **Vizsgált commit címe:** `Update "Clear Wing Synchro Dragon (Anime)"`
- **Fő technológia:** Lua 5.3, beágyazott ocgcore-interpreter
- **Licenc:** GNU Affero General Public License 3.0 vagy újabb
- **AETERNA összehasonlítási bázis:** az aktuális hivatalos 1.4v szabályforrások, a C# authoritative engine, a contract-first rendszer, a runtime package, az ability-architektúra és a Godot klienshatár
- **Összehasonlítási szabály:** kizárólag az AETERNA rendszeréhez mérve
- **Vizsgálati korlát:** helyi checkout, ScriptChecker-futtatás, ocgcore-build, teljes duelszimuláció és dinamikus interaction-teszt ebben a körben nem történt
- **Elsődleges AETERNA-érték:** nagy mennyiségű kártyaképesség egységes effect-életciklusa, közös szabályprimitívek, eljárásmodulok, chain-local context, forrástulajdonság-snapshotok és hosszú távú scriptkarbantartás
- **Elsődleges AETERNA-kockázat:** a kártyaszkriptek közvetlenül globális `Duel`, `Card`, `Effect` és `Group` API-kon keresztül hajtanak végre állapotmódosítást, explicit tranzakciós, state-version-, viewer-projection- és rollback-határ nélkül

Ez a dokumentum nem AETERNA-szabályforrás, nem engine-specifikáció és nem engedély
külső kód vagy Yu-Gi-Oh-tartalom átvételére. A cél a bizonyítható technikai tanulságok
elkülönítése azoktól a megoldásoktól, amelyek az AETERNA authority-, licenc-,
determinism- vagy hidden-information követelményeivel nem egyeztethetők össze.

---

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Projekt neve | Project Ignis card scripts for EDOPro |
| Repository | `ProjectIgnis/CardScripts` |
| Default branch | `master` |
| Vizsgált commit | `6b150b8471fbd713ad786ee3d8c1384a471c45f1` |
| Repository állapot | nyilvános, nem archivált, aktívan karbantartott |
| Fő nyelv | Lua 5.3 |
| Futtatási környezet | beágyazott interpreter az ocgcore-ban |
| Fő tartalom | hivatalos és nem hivatalos Yu-Gi-Oh-kártyaszkriptek, közös konstansok, utilityk és summon/procedure modulok |
| Kapcsolódó adatprojekt | `ProjectIgnis/BabelCDB` |
| Kapcsolódó szabálymag | `edo9300/ygopro-core` / ocgcore |
| CI | GitHub Actions ScriptChecker + sorvég-normalizálás |
| Tartalomterítés | automatikus delta-repository generálás és kliensszinkron |
| Licenc | AGPL-3.0-or-later |
| AETERNA-prioritás | **P0 – ability- és content-architektúra tanulási forrás** |
| Közvetlen integráció | **elutasítandó** |
| Clean-room elvi újraimplementálás | **igen, szigorú forrásszétválasztással** |

## 1.1 Azonosítás bizonyossága

Az upstream eredet **megerősített**:

- a repository saját README-je kanonikus EDOPro-kártyaszkript-gyűjteményként azonosítja;
- a repository neve, szervezeti tulajdonosa és tartalma egyezik a learning
  nyilvántartásban szereplő rekorddal;
- a `CONTRIBUTING.md` a Project Ignis saját közreműködési és Greenlight-folyamatát írja le;
- a szkriptek az ocgcore Lua API-ját használják;
- a kapcsolódó BabelCDB és delta-repository workflow-k közvetlenül a Project Ignis
  ökoszisztémájához kötődnek.

Az `ORIGIN_IDENTIFICATION_BACKLOG` feloldása ehhez a projekthez nem szükséges.

---

# 2. Vezetői összefoglaló

## 2.1 Mi ez a projekt?

A `ProjectIgnis/CardScripts` nem önálló kártyajáték-motor és nem teljes alkalmazás.
Nagy, folyamatosan karbantartott Lua-szkriptgyűjtemény, amely az EDOPro/ocgcore által
biztosított szabályprimitívekre építve valósítja meg az egyes Yu-Gi-Oh-kártyák
képességeit és speciális eljárásait.

A rétegek lényegi felosztása:

```text
BabelCDB
    kártyaadat, szöveg, lokalizáció, passcode
        ↓
CardScripts
    kártyánkénti Lua effect-deklaráció és operation-logika
        ↓
ocgcore
    authoritative duel state, chain, zónák, kártyaobjektumok, szabályprimitívek
        ↓
EDOPro kliens
    játékosinterakció és megjelenítés
```

A repository gyökere egyszerre tartalmaz:

- központi konstansokat;
- általános utilityket;
- chain-segédréteget;
- közös költség- és kiválasztási segédeket;
- summon- és card-type procedure modulokat;
- deprecation-kompatibilitási réteget;
- `official/`, `unofficial/`, `rush/`, `goat/` és más tartalomcsoportokat;
- GitHub Actions validációt;
- delta-terítési workflow-t.

## 2.2 Miért érdekes az AETERNA számára?

A projekt öt kiemelkedő tanulási területet ad.

### 1. Nagy ability-tér egységes életciklussal

A legtöbb kártyaszkript ugyanarra a szerkezetre épül:

```text
initial_effect
    ↓
Effect létrehozása
    ↓
type / code / range / property / count limit
    ↓
condition
    ↓
cost
    ↓
target
    ↓
operation
    ↓
RegisterEffect
```

Ez erős gyakorlati bizonyíték arra, hogy több ezer egyedi kártya kezelhető közös
életciklussal és konvenciókkal.

### 2. Újrahasználható szabályprimitívek

A `utility.lua`, `chain.lua`, `proc_*.lua` és a közös `Cost` könyvtár nagy mennyiségű
ismétlődő logikát emel ki a kártyaszkriptekből.

Az AETERNA számára ennek megfelelője nem Lua helper, hanem:

- typed C# module;
- stabil module ID;
- validált parameter schema;
- preflight;
- atomikus transition;
- typed event;
- viewer-safe projection;
- diagnostics;
- positive/negative fixture.

### 3. Chain- és resolution-context megőrzése

A `Chain.Data`, a triggering/resolving/registering property-réteg és az effectenkénti
chain-adat azt kezeli, hogy a forráskártya tulajdonságai a chain különböző időpontjaiban
változhatnak.

Ez közvetlenül releváns az AETERNA számára:

- trigger pillanati snapshot;
- resolution előtti újraellenőrzés;
- source-leaves-zone szabály;
- delayed effect context;
- replacement/prevention correlation;
- pending decision payload;
- determinisztikus event causality.

### 4. Hosszú távú tartalomkarbantartás

A repository dokumentálja:

- a modernizálási szabályokat;
- az elavult API-k kivezetését;
- a stabil konstansneveket;
- az egységes fájlformátumot;
- az official/unofficial tartalom elválasztását;
- a kártyaadat és script kapcsolatát;
- a változásalapú kliensszinkront.

Ez az AETERNA kártyaadat-, LOOKUPS-, ability-registry- és support-status rendszerében
közvetlenül hasznos folyamatminta.

### 5. A tesztelés korlátainak jó ellenpéldája

A ScriptChecker hasznos, de főleg:

- Lua-szintaxist;
- fájlbetölthetőséget;
- `initial_effect` meglétét;
- `initial_effect` közben fellépő alap runtime hibát

ellenőriz.

Nem bizonyítja automatikusan:

- a card text helyes szemantikáját;
- a target újraellenőrzést;
- a chain ordering helyességét;
- az interactionök összes kombinációját;
- az állapot atomikusságát;
- a hidden-information védelmet;
- a replay/determinism tulajdonságokat.

Az AETERNA-nak ezért a CardScripts méretezhetőségét kell tanulnia, nem a minimális
tesztmélységet.

## 2.3 Rövid döntés

- **Mélyelemzés folytatása:** elkészült az első teljes source audit
- **Kódátvétel vizsgálható:** nem
- **Clean-room elvi minta:** igen
- **Elsődleges tanulási terület:** ability module lifecycle, közös szabályprimitívek,
  chain/pending context, tartalomkarbantartás
- **Legfontosabb kockázat:** közvetlen imperative mutation globális core API-n,
  explicit AETERNA-kompatibilis tranzakció és projection nélkül
- **Összesített prioritás:** **P0**
- **Ajánlás:** a CardScripts szemantikai mintáiból AETERNA-specifikus, typed,
  capability-korlátozott C# ability executor és module catalog tervezhető; a Lua-kód,
  a Yu-Gi-Oh-konkrét szabályok és az asset/adatállomány nem emelhető át

---

# 3. Előzetes minősítés

| Szempont | Pontszám | AETERNA-vonatkozás |
|---|:---:|---|
| Közvetlen technológiai illeszkedés | 1/5 | Lua/ocgcore eltér a C#/.NET authoritytól |
| Rules-engine tanulási érték | 4/5 | a repository nem core engine, de gazdag effect- és procedure-réteg |
| Ability-rendszer tanulási érték | 5/5 | több ezer kártya közös lifecycle és helper API fölött |
| Godot-kliens tanulási érték | 0/5 | nem Godot-projekt |
| Multiplayer tanulási érték | 1/5 | a script layer önmagában nem dokumentál server authorityt vagy projectiont |
| AI/szimuláció tanulási érték | 2/5 | effect-description konvenció támogat AI-azonosítást, de nincs AETERNA-szerű AI contract |
| Adatpipeline tanulási érték | 4/5 | passcode, BabelCDB-kapcsolat, delta-terítés, official/unofficial réteg |
| Kódminőség | 4/5 | közös utilityk, modernizálási szabályok, de dinamikus és globális API-függő |
| Dokumentáltság | 4/5 | README, contributing, modernizing, központi konvenciók |
| Tesztelhetőség | 2/5 | automatizált syntax/init checker, de korlátozott szemantikai bizonyíték |
| Determinizmus bizonyítottsága | 1/5 | a script repository nem rögzít replay/canonical state contractot |
| Hidden-information biztonság | 1/5 | a Lua API teljes duel state-hez kötődik; viewer projection nem e réteg feladata |
| Licencelési felhasználhatóság | 0/5 | AGPL és külön IP/provenance kockázat |
| Összesített learning-prioritás | **P0** | ability/content architektúra és maintenance tanulás |
| Közvetlen dependency | **nem** | licenc- és authority-ütközés |
| Clean-room elvi újraimplementálás | **igen** | kizárólag AETERNA-szabályokból és saját API-val |

---

# 4. Vizsgálati alap és reprodukálhatóság

## 4.1 Felhasznált upstream források

| Forrás | Útvonal | Vizsgált commit | Szerep |
|---|---|---|---|
| README | `README.md` | `6b150b8…` | projektcél, futtatási modell, CI-korlát, licenc |
| Közreműködés | `CONTRIBUTING.md` | `6b150b8…` | official/unofficial workflow és review |
| Modernizálás | `MODERNIZING.md` | `6b150b8…` | scriptkonvenciók és migrációs szabályok |
| Konstansok | `constant.lua` | `6b150b8…` | zóna-, típus-, reason-, phase- és summon bitsetek |
| Archetype-azonosítók | `archetype_setcode_constants.lua` | `6b150b8…` | stabil központi setcode-registry |
| Általános utility | `utility.lua` | `6b150b8…` | filterek, costok, kiválasztás, module loading |
| Chain réteg | `chain.lua` | `6b150b8…` | chain-local data és property snapshot |
| Kártyaspecifikus helper | `cards_specific_functions.lua` | `6b150b8…` | újrahasználható archetype- és card-family logika |
| Fusion procedure | `proc_fusion.lua` | `6b150b8…` | szabványosított summon-procedure |
| Ritual procedure | `proc_ritual.lua` | `6b150b8…` | condition/target/selection/operation pipeline |
| Skill procedure | `proc_skill.lua` | `6b150b8…` | szabályvariáns- és startup-effect eljárások |
| Deprecated API | `deprecated_functions.lua` | `6b150b8…` | migráció, warning és hard failure |
| Tipikus official script | `official/c816427.lua` | `6b150b8…` | condition/cost/target/operation minta |
| Összetettebb official script | `official/c71628381.lua` | `6b150b8…` | fusion, quick effect, negation és optional ág |
| Legutóbbi javítás | `unofficial/c511002034.lua` | `6b150b8…` | resolution-time relation/immunity bugfix |
| Script checker workflow | `.github/workflows/check-scripts.yml` | `6b150b8…` | automatizált validáció |
| Delta workflow | `.github/workflows/commit-delta-puppet-repo.yml` | `6b150b8…` | változásalapú kliensszinkron |
| Formátumszabály | `.editorconfig` | `6b150b8…` | UTF-8, LF, tab és whitespace-policy |

## 4.2 Felhasznált AETERNA-források

| Forrás | Szerep |
|---|---|
| `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx` | canonical timing, trigger, resolution, continuous/delayed effect és reaction szabály |
| `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx` | kiegészítő mechanikai és ability-korlátok |
| `Aeterna game engine/docs/ABILITY_MODULE_SYSTEM.md` | aktív hosszú távú ability-architektúra |
| `Aeterna game engine/docs/ARCHITECTURE.md` | authority- és réteghatárok |
| `Aeterna game engine/docs/CONTRACT_SPECIFICATION.md` | request, event, projection és state contract |
| `Aeterna game engine/docs/CONTRACT_STATUS.md` | tényleges implementációs státusz |
| `Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md` | C# authority, Python tooling, Godot visual client |
| `Aeterna game engine/docs/DECISION_MAP.md` | elfogadott és nyitott irányok |
| production C# engine | megvalósult state, Inflow, Magnitude és Aura-preflight összevetési alap |

## 4.3 Build- és futtatási környezet

A repository dokumentált futtatási környezete:

- Lua 5.3;
- beágyazott interpreter;
- ocgcore shared library;
- ScriptChecker;
- GitHub Actions Ubuntu runner;
- EDOPro/Project Ignis kliensökoszisztéma.

Ebben az auditkörben:

- a repository-fájlok GitHub connectoron keresztül olvashatók voltak;
- a vizsgált commit rögzítve lett;
- helyi teljes checkout nem készült;
- ocgcore és ScriptChecker nem futott;
- duel/replay/puzzle nem futott;
- a legutóbbi commitra nem volt connectoron keresztül elérhető olyan status context,
  amelyből PASS állapotot lehetne bizonyítani.

Ezért az elemzés source audit, nem dinamikus runtime certification.

## 4.4 Reprodukálási eredmény

| Ellenőrzés | Eredmény | Bizonyíték |
|---|---|---|
| Repository elérhető | PASS | GitHub repository és fájlok olvashatók |
| Vizsgált commit azonosítható | PASS | teljes SHA és commit diff elérhető |
| README és dokumentáció elérhető | PASS | repository-forrás |
| Lua-szkriptek olvashatók | PASS | official/unofficial/root helper fájlok |
| CI workflow létezik | PASS | `.github/workflows/check-scripts.yml` |
| Delta workflow létezik | PASS | `.github/workflows/commit-delta-puppet-repo.yml` |
| Lokális syntax checker | NOT RUN | nincs helyi checkout és ocgcore futás |
| Teljes build | NOT APPLICABLE / NOT RUN | a repository script collection |
| Duel runtime | NOT RUN | EDOPro/ocgcore környezet nem indult |
| Interaction fixture | NOT RUN | replay/puzzle nem futott |
| Determinism proof | NOT PROVEN | nincs AETERNA-szerű canonical fixture ebben a repositoryban |
| Hidden-information proof | NOT PROVEN | nincs viewer-specifikus projection audit ebben a rétegben |

---

# 5. Repository- és modulstruktúra

## 5.1 Rövidített logikai fa

```text
CardScripts/
├── README.md
├── CONTRIBUTING.md
├── MODERNIZING.md
├── .editorconfig
├── constant.lua
├── utility.lua
├── chain.lua
├── cards_specific_functions.lua
├── archetype_setcode_constants.lua
├── deprecated_functions.lua
├── proc_fusion.lua
├── proc_fusion_spell.lua
├── proc_ritual.lua
├── proc_synchro.lua
├── proc_xyz.lua
├── proc_pendulum.lua
├── proc_link.lua
├── proc_equip.lua
├── proc_persistent.lua
├── proc_normal.lua
├── proc_skill.lua
├── proc_rush.lua
├── proc_maximum.lua
├── proc_gemini.lua
├── proc_spirit.lua
├── official/
│   └── c<passcode>.lua
├── unofficial/
│   └── c<passcode>.lua
├── rush/
│   └── c<passcode>.lua
├── goat/
│   └── c<passcode>.lua
└── .github/
    ├── workflows/check-scripts.yml
    ├── workflows/commit-delta-puppet-repo.yml
    └── generate_mappings.py
```

A pontos teljes fájlszámot ez az audit nem számolta ki. A repository mérete és a
rendszeres kártyaszintű commitok azonban nagy, folyamatosan változó content codebase-re
utalnak.

## 5.2 Modulok és felelősségek

| Modul | Felelősség | AETERNA-megfelelő |
|---|---|---|
| `constant.lua` | központi core API konstansok | typed enum/flag ID-k, LOOKUPS canonical értékek |
| `archetype_setcode_constants.lua` | stabil archetype/setcode névtér | Birodalom/klán/vérvonal/keyword registry |
| `utility.lua` | közös filter, cost, select és card helper | C# module library és safe selector API |
| `chain.lua` | chain-local context, source property snapshot | pending context, correlation és trigger snapshot |
| `cards_specific_functions.lua` | card-family közös logika | újrahasználható family/module implementáció |
| `proc_*.lua` | summon és speciális card-type procedure | core rule module vagy procedure compiler |
| `deprecated_functions.lua` | API-migráció | schema/module alias és deprecation registry |
| `official/c*.lua` | hivatalos kártyaképesség | ability declaration + szükség esetén card-local fallback |
| `unofficial/c*.lua` | nem hivatalos tartalom | AETERNA-ban külön experimental/reference réteg lehetne |
| ScriptChecker workflow | syntax/init validity | schema + compile + semantic fixture gate |
| Delta workflow | változásalapú content-terítés | runtime package delta/publish, későbbi feladat |
| BabelCDB kapcsolat | adat/szöveg és script összerendelés | card definition, ability registry és lokalizáció különválasztása |

## 5.3 Függőségi irányok

A tényleges fő irány:

```text
card script
    ↓
utility / chain / procedure helper
    ↓
ocgcore global API
    ↓
authoritative duel state mutation
```

A script layer:

- nem tart saját teljes MatchState-et;
- nem tart külön UI state-et;
- nem tart viewer projectiont;
- nem fogad AETERNA-szerű action requestet;
- közvetlenül a core által adott runtime objektumokra és globális funkciókra támaszkodik.

A dependency inversion AETERNA-szempontból hiányzik:

```text
CardScripts:
card → global core API

AETERNA cél:
validated request/declaration
    → constrained AbilityExecutionContext
    → domain service
    → atomic MatchState transition
    → event/projection
```

---

# 6. Architektúra

## 6.1 Authoritative state

A CardScripts repositoryban nincs saját authoritative MatchState osztály vagy schema.
A kártyaszkriptek az ocgcore által kezelt objektumokat érik el:

- `Duel`;
- `Card`;
- `Effect`;
- `Group`;
- chain információ;
- player effect;
- zóna;
- reason;
- position;
- summon state;
- flag effect;
- counter;
- LP;
- card relation.

A script ezért **rules extension layer**, nem önálló authority.

### Erősség

A kártyaszkripteknek nem kell saját meccsállapotot szinkronizálniuk az engine mellett.
Egyetlen core hajtja végre a state mutationt.

### AETERNA-korlát

Az AETERNA ezt az elvet megtartja:

- egy authoritative engine;
- nincs párhuzamos kártyaszkript-state;
- a kliens és az AI nem mutál state-et.

Az API-forma azonban nem vehető át, mert a CardScripts callbackek túl széles
capabilityt kapnak. Egy script tetszőlegesen hívhat sok globális `Duel.*` műveletet.

A javasolt AETERNA-határ:

```text
IAbilityModule
    EvaluatePrecondition(ReadOnlyAbilityContext)
    BuildPendingDecision(ReadOnlyAbilityContext)
    Execute(ValidatedAbilityCommand, AbilityTransitionContext)
```

A `ReadOnlyAbilityContext` csak a szükséges, viewer-safe vagy authority-belső adatot
adja. Az `AbilityTransitionContext` csak engedélyezett domain transitionöket kínál,
nem teljes MatchState-írhatóságot.

## 6.2 State és projection

A CardScripts layer nem választja el explicit módon:

- authoritative internal state;
- owner-visible snapshot;
- opponent-visible snapshot;
- spectator view;
- replay view;
- debug view.

Ez érthető, mert a repository nem kliens-contract projekt. A kártyaszkriptek azonban
közvetlenül elérhetnek kéz-, pakli-, temető- és más zónacsoportokat.

Az AETERNA-ban minden module:

- belső authority contextből dolgozik;
- player-facing object referenceként nem ad ki technikai instance ID-t;
- event payloadját viewer-specifikusan kell redaktálni;
- hidden zónából keresésnél csak a jogosult játékosnak adhat választási lehetőséget;
- az ellenfélnek csak a szabály szerint szükséges információt mutatja.

## 6.3 Fő adatáramlás

A CardScripts tipikus áramlása:

```text
ocgcore event / free-chain opportunity
    ↓
Effect condition
    ↓
cost check
    ↓
target check és selection
    ↓
chain létrehozás
    ↓
operation
    ↓
közvetlen Duel/Card mutation
```

Az AETERNA céláramlása:

```text
EngineEvent / timing window
    ↓
trigger candidate collection
    ↓
module precondition
    ↓
legal action vagy pending decision
    ↓
state-version guarded request
    ↓
final validation
    ↓
atomikus cost + effect transition
    ↓
typed EngineEvent
    ↓
viewer-specific projection
    ↓
Godot / fair AI
```

## 6.4 Lifecycle

A CardScriptsben a duel lifecycle az ocgcore felelőssége. A script layer képes:

- startup effecteket;
- phase eventeket;
- free-chain activációt;
- triggered effecteket;
- quick effecteket;
- continuous effecteket;
- replacement effecteket;
- delayed operationöket;
- summon procedure-ket;
- rule-level special procedure-ket

regisztrálni.

Az AETERNA számára a fontos tanulság nem az eseménykódok másolása, hanem a callback
életciklus explicit modellezése.

---

# 7. Effect-deklaráció és ability-életciklus

## 7.1 Tipikus kártyaszkript

Egy tipikus official script:

```lua
local s,id=GetID()

function s.initial_effect(c)
    local e1=Effect.CreateEffect(c)
    e1:SetCategory(...)
    e1:SetType(...)
    e1:SetCode(...)
    e1:SetProperty(...)
    e1:SetRange(...)
    e1:SetCountLimit(...)
    e1:SetCost(s.cost)
    e1:SetTarget(s.target)
    e1:SetOperation(s.operation)
    c:RegisterEffect(e1)
end
```

A callbackek külön felelősségeket kapnak:

- **condition:** az activation/trigger speciális feltétele;
- **cost:** előellenőrzés és fizetés;
- **target:** legalitás, kiválasztás és operation metadata;
- **operation:** chain feloldásakor végrehajtott mutation.

Ez közel áll az AETERNA ability-fogalmaihoz:

| CardScripts | AETERNA |
|---|---|
| effect code/type/range | trigger/timing/source zone |
| condition | module precondition |
| cost `chk==0` | cost preflight |
| cost `chk!=0` | atomikus payment transition |
| target `chk==0` | target candidate validation |
| target selection | legal action payload vagy pending decision |
| operation | authoritative effect transition |
| category | event/UX hint, nem authority |
| count limit | usage state és deterministic guard |
| relation check | final target/source revalidation |
| `RegisterEffect` | ability registry/module binding |

## 7.2 Erős absztrakció

A lifecycle szabványos, ezért:

- a kártyaszkript olvashatóbb;
- a code review egységes;
- közös helper használható;
- az effect leíró része elkülönül a művelettől;
- a core tudja, mikor kell conditiont, targetet és operationt hívni.

## 7.3 AETERNA-korlát

Az elválasztás nem tranzakciós szerződés.

A `cost` callback:

- `chk==0` módban csak ellenőriz;
- végrehajtási módban közvetlenül mutál.

Az `operation` további közvetlen mutationöket végez.

Nincs a Lua layerben általános:

- immutable command;
- transaction object;
- rollback;
- mutation journal;
- expected state version;
- request ID;
- idempotency;
- invariant gate;
- typed result;
- typed diagnostics.

Az AETERNA-ban ugyanaz a fogalmi lifecycle csak erősebb contracttal használható.

---

# 8. Condition, target és final revalidation

## 8.1 Condition

A condition callback rendszerint tiszta lekérdezés:

- phase;
- turn player;
- chain state;
- source status;
- opponent/owner;
- trigger effect típusa;
- reason;
- summon method;
- zóna;
- archetype;
- card property.

Ez jó module-precondition minta.

## 8.2 Target check és selection

A target callback két feladatot egyesít:

1. `chk==0` módban megállapítja, hogy létezik-e érvényes cél;
2. activationkor játékosi kiválasztást hajt végre, target relationt regisztrál és
   operation infot állít be.

A CardScriptsben a target kiválasztása gyakran a chain létrehozásakor megtörténik.

Az AETERNA-ban:

- egyszerű, egy-lépéses target a legal action payload része lehet;
- komplex target külön authoritative pending decision;
- a kliens csak az engine által kiadott candidate reference-ekből választhat;
- a request state-version guarded;
- a választás után final validation szükséges.

## 8.3 Final revalidation

A modernizálási dokumentum és a példaszkriptek hangsúlyozzák:

- a célpont `IsRelateToEffect` ellenőrzését;
- summon/attach/zone feltételek újbóli vizsgálatát;
- source relation és face-up státusz vizsgálatát;
- optional rész csak fennálló feltételek mellett történhet.

Ez egybeesik a hivatalos AETERNA szabályforrás 4.1 és 4.5 logikájával:

- trigger/activation és resolution külön pillanat;
- a célpont érvényessége resolutionkor újraellenőrzendő;
- a reactionök után változhat az állapot;
- csak az akkor még jogszerű rész oldható fel.

## 8.4 Ajánlott AETERNA-szerződés

```csharp
public interface ITargetSelector
{
    TargetCandidateSet ListCandidates(
        ReadOnlyMatchState state,
        AbilitySource source,
        ViewerContext viewer);

    TargetValidationResult ValidateFinalTargets(
        ReadOnlyMatchState state,
        ValidatedAbilityRequest request);
}
```

Kötelező:

- stabil player-safe target reference;
- source/controller/zone check;
- state version;
- minimum/maximum count;
- uniqueness;
- ordering;
- cancellation policy;
- partial resolution policy;
- hidden-information policy;
- final revalidation;
- deterministic candidate ordering.

---

# 9. Cost-rendszer

## 9.1 Közös cost library

A `utility.lua` központi `Cost` névteret ad, többek között:

- self banish;
- self tribute/release;
- self to grave;
- self to hand;
- self to deck/extra;
- reveal;
- discard;
- counter removal;
- detach;
- LP payment;
- usage-limit cost;
- kombinált `Cost.AND`;
- választható `Cost.Choice`;
- helyettesíthető `Cost.Replaceable`.

Ez erős bizonyíték arra, hogy a költségeket érdemes:

- stabil névvel;
- újrahasználható paraméterezéssel;
- önálló preconditionnel;
- egységes UI/interaction logikával

modellezni.

## 9.2 Kétfázisú callback

A cost convention:

```lua
if chk==0 then
    return fizethető-e
end

-- tényleges mutation
```

Ez fogalmilag preflight + commit.

## 9.3 `Cost.AND`

A `Cost.AND`:

1. check módban minden cost-komponenst ellenőriz;
2. végrehajtáskor sorrendben meghívja a komponenseket;
3. explicit `false` esetén leáll.

Hasznos tanulság:

- kombinálható cost-modulok;
- egységes előellenőrzés;
- stabil komponenssorrend;
- cost metadata/introspection;
- replacement hook.

Kritikus AETERNA-korlát:

- a komponensek közvetlenül mutálnak;
- nincs általános rollback;
- nincs bizonyíték arra, hogy minden végrehajtási callback a check után biztosan sikerül;
- egy korábbi komponens mutationje megmaradhat, ha későbbi komponens hibázik;
- a Lua layer nem ad immutable payment plan-t.

## 9.4 AETERNA-javaslat: payment plan

```text
Cost module declaration
    ↓
preflight
    ↓
PaymentPlan
    - source references
    - amounts
    - ordering
    - replacement choice
    - expected state version
    - diagnostics
    ↓
final validation
    ↓
single atomic transition
```

A `PaymentPlan` nem mutálhat létrehozáskor.

A tényleges transition:

- vagy teljes egészében sikerül;
- vagy semmit nem módosít;
- typed eventet bocsát ki;
- növeli a state versiont;
- invariant checket futtat;
- viewer-safe projectiont eredményez.

## 9.5 LOOKUPS-kapcsolat

A CardScripts közös cost-nevei arra utalnak, hogy az AETERNA-ban is szükséges
kanonikus, normalizált névtér.

A LOOKUPS-normalizálás előtt legalább a következő csoportokat kell egyértelműsíteni:

```text
ability_trigger
timing_window
condition_type
cost_type
cost_source_type
target_selector
target_zone
choice_type
effect_module
duration_type
failure_policy
replacement_type
prevention_type
usage_limit_type
event_type
visibility_policy
support_status
execution_mode
```

Ezek:

- canonical value;
- aktív alias;
- inaktív/legacy érték;
- workflow-only érték;
- magyar label;
- gépi ID;
- schema version;
- blocking policy

szerint kezelendők.

A LOOKUPS-normalizálás ezért nem adminisztratív mellékfeladat, hanem az ability- és
payment-rendszer előfeltétele.

---

# 10. Chain-local context

## 10.1 `Chain.Data`

A `chain.lua` chain linkhez társított adatot tart:

- chain ID alapján;
- opcionálisan effectenként külön kulccsal;
- a chain végén automatikus reset mellett.

Az effecthez kapcsolódó helper:

```lua
e:GetChainData()
```

alkalmas például:

- választott ágra;
- cost során leválasztott anyagokra;
- optional subeffect állapotára;
- target és operation közötti contextre;
- korábbi property snapshotra.

## 10.2 Erős tanulság

A complex ability executionnek szüksége van olyan contextre, amely:

- activation és resolution között megmarad;
- nem általános globális változó;
- correlationnel azonosítható;
- nested resolution közben elkülönül;
- időben automatikusan lezárható.

## 10.3 AETERNA-korlát

A `Chain.Data`:

- dinamikus Lua table;
- nincs schema;
- nincs explicit version;
- nincs immutable boundary;
- nincs typed serialization;
- nincs replay contract;
- nincs viewer redaction;
- nincs per-step invariant;
- a chain-end global resetre támaszkodik.

## 10.4 AETERNA-javaslat

```csharp
public sealed record PendingEffectContext(
    string PendingEffectId,
    string CorrelationId,
    string AbilityId,
    string SourceObjectRef,
    string ControllerPlayerId,
    int CreatedAtStateVersion,
    ImmutableArray<string> TargetRefs,
    ImmutableDictionary<string, ContractValue> Choices,
    ImmutableArray<PaymentReservation> ReservedCosts,
    TriggerSnapshot TriggerSnapshot,
    ResolutionPolicy ResolutionPolicy);
```

Követelmények:

- authoritative MatchState-ben él;
- schema-verziózott;
- determinisztikusan serializálható;
- player projectionben redaktálható;
- cancel/expire/resolve eventet kap;
- loop/depth guard kapcsolható hozzá;
- nem hordhat tetszőleges runtime objektumreferenciát;
- a source és target reference final revalidationön megy át.

---

# 11. Triggering, resolving és registering property snapshot

## 11.1 A probléma

Egy effect forráskártyája a chain során:

- zónát válthat;
- face-downná válhat;
- másolatként megszűnhet;
- tulajdonságot válthat;
- kontrollert válthat;
- elhagyhatja a fieldet;
- új objektumként térhet vissza.

A resolutionnek gyakran tudnia kell:

- a trigger pillanatában fennálló adatot;
- a resolution elején fennálló adatot;
- az aktuális adatot;
- a Duel/global effect regisztrálásakor fennálló adatot.

## 11.2 CardScripts-megoldás

A `chain.lua`:

- lekéri a triggering propertyket a core chain infóból;
- resolution kezdetén elmenti a forrás aktuális propertyjeit;
- Duel effect regisztrálásakor elmenti a registering propertyket;
- dinamikusan választ current, resolving, triggering vagy registering nézetet.

Ez az audit egyik legerősebb technikai tanulsága.

## 11.3 AETERNA-megfelelő

Az AETERNA typed snapshotjai lehetnek:

```text
TriggerSourceSnapshot
ResolutionSourceSnapshot
RegisteredContinuousSourceSnapshot
LastKnownObjectState
```

Lehetséges mezők:

- card ID;
- owner;
- controller;
- zone;
- domain position;
- face/activity state;
- card type;
- realm;
- class/race/bloodline;
- current stats;
- keyword set;
- source object identity;
- created-at sequence;
- last-known state version.

## 11.4 Kötelező szabály

Nem minden effect ugyanazt a snapshotot használja.

A module schema deklarálja:

```text
source_property_policy:
    current
    trigger_snapshot
    resolution_start_snapshot
    last_known
    registering_snapshot
```

A policy nem kártyaszkriptben találgatott implicit viselkedés, hanem:

- szabályforrásból levezetett;
- module-specifikus;
- tesztelt;
- eventben auditálható.

---

# 12. Procedure modulok

## 12.1 Fusion

A `proc_fusion.lua`:

- anyagdefiníciókat filterekké alakít;
- substitute és extra material eseteket kezel;
- kötelező anyagcsoportot vizsgál;
- condition és operation callbacket generál;
- effectként regisztrálja a summon procedure-t.

## 12.2 Ritual

A `proc_ritual.lua`:

- named argument wrapperrel konfigurálható;
- ritual monster filtert és szintkövetelményt kezel;
- extra material és forced selection hookot ad;
- target fázisban előellenőriz;
- operation fázisban újra összegyűjti az anyagokat;
- játékosi material selectiont hajt végre;
- count limitet használ;
- anyagot beállít;
- release/summon/complete procedure lépéseket végez;
- custom operation és stage hookot enged.

## 12.3 További procedure-k

A root utility betölti:

- fusion;
- fusion spell;
- ritual;
- synchro;
- union;
- xyz;
- pendulum;
- link;
- equip;
- persistent;
- normal;
- skill;
- rush;
- maximum;
- gemini;
- spirit;
- unofficial;
- workaround

module-okat.

Ez rétegzett rules extension ecosystem.

## 12.4 AETERNA-tanulság

Az AETERNA-ban a hasonló, ismétlődő folyamatok ne kártyánkénti egyedi C# kódban
ismétlődjenek.

Lehetséges core/module családok:

- normal Entity play;
- alternate Entity play;
- token creation;
- return-to-hand;
- sacrifice;
- discard cost;
- exhaust source;
- draw;
- search;
- reveal;
- move zone;
- attach/link;
- temporary keyword;
- stat modifier;
- delayed return;
- continuous aura;
- prevention;
- replacement;
- ward restore/break prevention.

Minden module:

- saját schema;
- stabil ID;
- explicit target és source policy;
- typed failure;
- event;
- diagnostics;
- fixture;
- version.

## 12.5 Mit nem szabad átvenni?

- dynamic function table mint production contract;
- globális mutable procedure state;
- arbitrary callback extension korlátlan core hozzáféréssel;
- module-paraméterek runtime típusellenőrzés nélkül;
- implicit mutation order;
- replay nélkül nem serializálható closure/context.

---

# 13. Konstans- és registry-kezelés

## 13.1 Bitset konstansok

A `constant.lua` központilag rögzíti:

- location;
- position;
- card type;
- attribute;
- race;
- reason;
- summon type;
- status;
- phase;
- player;
- event;
- effect;
- reset és más core értékeket.

A modernizálási dokumentum bitwise OR/AND használatot ír elő az összeadás és kivonás
helyett.

## 13.2 Archetype registry

Az `archetype_setcode_constants.lua`:

- stabil `SET_*` neveket ad;
- kezeli a fő és al-archetype kapcsolatokat;
- hardcoded hex érték helyett beszédes konstansokat preferál;
- új érték felvételét központi helyre tereli.

## 13.3 AETERNA-tanulság

A LOOKUPS és registry értékek ne legyenek:

- magyar labelből runtime közben származtatva;
- kártyaszövegből találgatva;
- több oszlopban eltérő alias formában;
- hardcoded számmal ismételve;
- engine és adatpipeline között külön authorityként fenntartva.

Javasolt forma:

```json
{
  "lookup_group": "ability_trigger",
  "canonical_value": "on_entity_enters_domain",
  "label_hu": "Entitás Domainra érkezésekor",
  "status": "active",
  "aliases": [
    "belépéskor",
    "Domainra kerülésekor"
  ],
  "runtime_allowed": true,
  "blocking_if_unknown": true,
  "schema_version": "1.0"
}
```

A label és alias nem válhat executable szabállyá. A runtime csak canonical értéket kap.

---

# 14. Kártyaazonosítás és definition/script kapcsolat

## 14.1 Passcode-alapú fájlnév

A kártyaszkriptek tipikus fájlneve:

```text
c<integer passcode>.lua
```

A script:

```lua
local s,id=GetID()
```

formával kapja meg saját script table-jét és kódját.

A script metadata gyakran rögzít:

- `listed_names`;
- `listed_series`;
- material setcode;
- xyz number;
- más, kereshető card-family adatot.

## 14.2 Külön adatprojekt

Az unofficial contribution workflow előírja a BabelCDB rekordot. Ez bizonyítja a
definition és executable script elkülönítését.

## 14.3 AETERNA-megfelelő

```text
CardDefinition
    card_id
    rules_card_id
    localized fields
    type/realm/clan/class/race/bloodline
    printed costs/stats
    ability references
        ↓
AbilityRegistry
    ability_id
    source_card_id
    module_id
    parameters
    trigger/timing
    support status
    schema version
        ↓
C# module catalog
```

A kártya és ability azonosító:

- determinisztikus;
- buildtől független;
- verziókövethető;
- aliasoktól független;
- nem instance ID;
- nem lokalizált név;
- nem Excel-sorszám.

---

# 15. Continuous, delayed és special rule logika

## 15.1 Continuous effect

A CardScripts effect API támogat:

- field;
- single;
- continuous;
- grant;
- equip;
- persistent;
- rule-level effecteket.

A source sokszor effect objectet regisztrál reset-, range-, condition- és value-
függvényekkel.

## 15.2 Delayed operation

Az `Auxiliary.DelayedOperation`:

- érintett csoportot tárol;
- phase-t és resetet rögzít;
- unique flag/contextet használ;
- későbbi eventre effectet regisztrál;
- csak még érintett kártyákkal fut;
- expiration és reset után megszűnik.

Ez erős minta a hivatalos AETERNA 4.4 szabályához, amely delayed effectnél megköveteli:

- creation time;
- resolution time;
- duration;
- source dependence;
- target validity;
- failure policy.

## 15.3 AETERNA-javaslat

A delayed effect ne runtime closure legyen.

```csharp
public sealed record ScheduledEffect(
    string ScheduledEffectId,
    string AbilityId,
    string SourceRef,
    string ControllerPlayerId,
    TimingPoint ResolveAt,
    int CreatedAtSequence,
    int CreatedAtStateVersion,
    ImmutableArray<string> ObjectRefs,
    ContractValue Parameters,
    SourceDependencyPolicy SourceDependency,
    InvalidTargetPolicy InvalidTargetPolicy,
    ExpirationPolicy ExpirationPolicy);
```

Kötelező:

- serializálható;
- replay-kompatibilis;
- deterministic ordering;
- max depth/loop guard;
- cancel/expire/resolve event;
- viewer-safe summary.

---

# 16. Reaction és chain

## 16.1 CardScripts modell

A Yu-Gi-Oh chain a core által biztosított. A script:

- `EVENT_CHAINING`;
- chain current link;
- triggering effect;
- target cards;
- chain negate/disable;
- chain data;
- operation info;
- relation checks

segítségével csatlakozik hozzá.

A repository nagy mennyiségű valódi chain interaction kezelését mutatja.

## 16.2 AETERNA hivatalos alap

Az AETERNA hivatalos forrása szerint:

- reaction window az esemény létrejötte és végleges feloldása között nyílik;
- csak explicit engedélyezett reakció játszható;
- ha mindkét játékos reagálhat, a nem kezdeményező játékos kap első lehetőséget;
- pass/pass lezárja az ablakot;
- a reakciók stack-szerűen, LIFO sorrendben oldódnak;
- resolutionkor feltétel-, source- és target-újraellenőrzés szükséges;
- az esemény csak stabil állapotban zárható le.

## 16.3 Nem másolható a Yu-Gi-Oh chain

A CardScripts:

- más játék timingját;
- más event taxonomyját;
- más card type rendszerét;
- más priority és chain szabályait

implementálja.

Az AETERNA nem veheti át:

- event code-okat;
- chain speedet;
- summon procedure-t;
- damage step kivételeket;
- Yu-Gi-Oh target/chain rulingsot;
- card-category szemantikát.

## 16.4 Átvehető elv

- explicit timing point;
- trigger candidate;
- source snapshot;
- player ordering;
- pass;
- pending context;
- final revalidation;
- LIFO vagy más explicit resolution order;
- event close invariant.

Az AETERNA pontos orderingje továbbra is saját szabályforrásból következik.

---

# 17. API-karbantartás és deprecation

## 17.1 Modernizálási dokumentum

A `MODERNIZING.md` valódi maintenance playbook:

- encoding és line ending;
- kártyanév;
- effect description;
- kommentminőség;
- central setcode;
- timing hint;
- redundant property eltávolítás;
- target check;
- possible operation metadata;
- helyes zone count API;
- választási helper;
- közös cost helper;
- material validation;
- összetett kiválasztó helper;
- magic value → named constant;
- bitset művelet;
- core-változás miatt redundánssá vált check kivezetése.

Ez nem puszta stíluslista: a script ecosystem folyamatos rules/core evolúcióját kezeli.

## 17.2 Deprecated function layer

A `deprecated_functions.lua` három szintet különít el:

1. deprecated alias warninggal és stacktrace-szel;
2. deleted/replaced API hard errorral és új név megadásával;
3. eltávolított API hard errorral és migrációs üzenettel.

## 17.3 AETERNA-megfelelő

A runtime package és ability schema migrációja használhat:

```text
active
deprecated
legacy_alias
inactive
removed
workflow_only
audit_required
```

Szabályok:

- active alias normalizálható;
- deprecated alias diagnosticsot ad;
- dangerous ambiguity blocking;
- removed runtime value hard failure;
- migration mapping verziózott;
- source file megőrzött;
- normalizált output csak canonical értéket tartalmaz;
- a C# engine nem értelmez szabad aliasokat.

## 17.4 LOOKUPS-következtetés

A CardScripts maintenance modellje megerősíti, hogy az AETERNA LOOKUPS-normalizálása
Codex-folytatás előtti kapu.

Mielőtt új gameplay-kód készül:

- Realm;
- card type;
- activity;
- ability trigger;
- timing;
- cost;
- target;
- duration;
- effect;
- event;
- support status

értékeknek egyértelmű canonical authorityt kell kapniuk.

---

# 18. CI, teszt és release workflow

## 18.1 Script validity checker

A GitHub Actions:

1. checkout;
2. line ending renormalization és diff check;
3. ScriptChecker letöltés;
4. ocgcore shared library letöltés;
5. teljes repository script syntax check.

Erősség:

- minden push/PR kap alap automatikus validációt;
- a core valódi interpreterével tölt;
- az `initial_effect` hibákat korán észlelheti;
- a line ending drift blokkolható.

## 18.2 Korlát

A README explicit kimondja, hogy nem statikus analizátor és nem fogja általában
megtalálni:

- más callbackek runtime hibáit;
- helytelen API-paramétereket;
- teljes interaction hibát;
- szemantikai rules mismatch-et.

A vizsgált commiton connectoron keresztül nem volt bizonyítható status context, ezért
e jelentés nem állítja, hogy a HEAD CI PASS.

## 18.3 Delta repository generator

A workflow:

- master pushra fut;
- base/version SHA alapján az új vagy módosult Lua-fájlokat másolja;
- törölt fájlokat eltávolít;
- rename mappinget generál;
- eredeti author/committer metadata mellett commitol;
- `VERSION` fájlba írja a source SHA-t;
- destination repositoryba pushol.

Erős tanulság:

- content source és kliensfogyasztói csomag elkülönül;
- delta trace-elhető source commitra;
- törlés és rename explicit;
- kliensszinkron automatizált.

## 18.4 AETERNA-megfelelő

Későbbi runtime package publish:

```text
editing source
    ↓
normalization
    ↓
schema validation
    ↓
support/coverage validation
    ↓
candidate package
    ↓
semantic fixtures
    ↓
manifest + source fingerprint
    ↓
versioned publish
    ↓
Godot consumption copy
```

A delta publish csak stabil package identity és rollback után javasolt.

---

# 19. Kódminőségi megfigyelések

## 19.1 Erősségek

- egységes `initial_effect`;
- közös helper névterek;
- moduláris procedure-k;
- beszédes konstansok;
- central archetype registry;
- külön modernizálási szabály;
- explicit deprecated API;
- official/unofficial content separation;
- effect description és komment policy;
- source relation újraellenőrzés;
- chain-local context;
- common cost functions;
- named argument helper bizonyos procedure-knél;
- rendszeres kis kártyaszintű bugfix commitok;
- automatizált syntax/init checker;
- source SHA-val követett delta-terítés.

## 19.2 Gyengeségek az AETERNA mércéje szerint

- dinamikus Lua és implicit callback signature;
- globális core API;
- széles mutation capability;
- nincs typed module parameter schema;
- nincs state-version request guard;
- nincs immutable request;
- nincs központi legal action contract;
- nincs explicit atomic transaction;
- nincs általános rollback;
- nincs typed result/diagnostics contract;
- nincs viewer projection;
- nincs replay/canonical serialization contract;
- nincs bizonyított deterministic ordering a script layerben;
- nincs per-card teljes semantic fixture követelmény;
- closure- és runtime object context nem serializálható;
- official content és executable logic erős IP/provenance kötése.

## 19.3 Legacy és compatibility teher

A modernizálási és deprecated réteg bizonyítja:

- a helper API fejlődik;
- régi scriptek fennmaradnak;
- egy átállás nem végezhető egyszerre;
- hosszú ideig szükség lehet compatibility mappingre;
- az új core-viselkedés redundánssá tehet régi script checkeket.

Az AETERNA-nak ezt korán kell kezelnie:

- schema version;
- module version;
- ruleset version;
- migration map;
- compatibility window;
- explicit unsupported;
- coverage report.

---

# 20. Licenc és provenance

## 20.1 Repository-licenc

A README szerint a program:

- AGPL-3.0 vagy újabb;
- Project Ignis contributors szerzői joga alatt;
- fájlonként version history és author credit kapcsolódhat hozzá.

## 20.2 Közvetlen integráció

Elutasítandó:

- Lua helper másolása;
- procedure file másolása;
- card script átemelése;
- részleges forráskód-port;
- API-szerkezet közeli transliterációja;
- executable Yu-Gi-Oh card logic importja.

## 20.3 További IP-kockázat

A repository:

- Yu-Gi-Oh kártyaneveket;
- card texthez igazodó behavior logikát;
- archetype neveket;
- passcode-okat;
- anime/manga/video-game-exclusive tartalmat

kezel.

Még permissive licenc esetén is külön content/IP audit lenne szükséges. Az AGPL
további közvetlen integrációs akadály.

## 20.4 Engedélyezett használat

- magas szintű architekturális tanulság;
- lifecycle felismerése;
- saját AETERNA-szabályokra épülő clean-room design;
- saját elnevezés;
- saját C# interface;
- saját schema;
- saját teszt;
- saját algoritmus és kód;
- forrás és inspiráció dokumentálása.

A clean-room implementáció során a fejlesztési specifikáció AETERNA-forrásból készüljön,
ne CardScripts kódátírásból.

---

# 21. Összevetés az AETERNA hivatalos timing- és effect-szabályaival

## 21.1 Egyező alapelvek

A CardScripts gyakorlata támogatja az AETERNA következő hivatalos elveit:

- trigger és resolution külön kezelése;
- timing feltétel explicit;
- target érvényesség resolutionkor újraellenőrzendő;
- optional és mandatory effect eltér;
- continuous effect külön lifecycle;
- delayed effect külön időzítés és expiration;
- reaction/chain közben source és target változhat;
- effect csak stabil lezárás után tekinthető befejezettnek.

## 21.2 Eltérő játékmodell

A konkrét implementáció azonban Yu-Gi-Oh-specifikus:

- event code-ok;
- chain;
- summon típusok;
- monster/spell/trap;
- grave/banish/extra deck;
- LP;
- archetype setcode;
- damage step;
- fusion/ritual/synchro/xyz/link;
- Rush/GOAT/Skill rules.

Ezek nem írhatják felül az AETERNA:

- Birodalom;
- klán;
- Entitás/Ige/Rituálé/Jel/Sík;
- Ősforrás;
- Magnitúdó;
- Aura;
- Beáramlás;
- Pecsét;
- Aeternal;
- saját reaction;
- saját combat;
- saját timing

szabályait.

## 21.3 Következtetés

A CardScripts **szoftveres szervezési minta**, nem rules design forrás.

---

# 22. AETERNA ability-architektúra javaslatok

## 22.1 Négy réteg

```text
1. CardDefinition
2. AbilityDeclaration / ExecutionPlan
3. C# AbilityModule
4. Engine timing, transition, event és projection
```

### CardDefinition

- statikus card data;
- ability ID-k;
- nem tart executable closure-t;
- runtime package-ből jön.

### AbilityDeclaration

- trigger;
- timing;
- condition;
- cost;
- target/choice;
- effect;
- duration;
- optional;
- failure policy;
- module parameters.

### C# AbilityModule

- typed schema;
- preflight;
- final validation;
- atomic transition;
- event;
- diagnostics.

### Core engine

- candidate collection;
- ordering;
- pending state;
- reaction;
- pass;
- resolution;
- invariant;
- projection.

## 22.2 Capability-korlátozott module context

Tiltott:

```csharp
module.Execute(MatchState mutableState)
```

Javasolt:

```csharp
module.Preflight(ReadOnlyAbilityContext context)
module.Execute(ValidatedAbilityCommand command, AbilityTransitionContext tx)
```

A `tx` csak engedélyezett műveleteket ad:

- move card;
- change activity;
- modify entity stat;
- create token;
- add/remove keyword;
- draw;
- reveal;
- restore/break ward explicit szabállyal;
- schedule effect;
- emit typed domain event.

Nem ad:

- tetszőleges listamódosítást;
- közvetlen event history írást;
- state version kézi átírást;
- opponent hidden zone dumpot;
- arbitrary reflectiont;
- Godot callbacket;
- fájl- vagy hálózati I/O-t.

## 22.3 Module descriptor

```json
{
  "schema_version": "1.0",
  "module_id": "draw_cards",
  "module_version": "1.0",
  "parameters": {
    "count": 1,
    "player": "controller"
  },
  "trigger": "on_play_resolved",
  "timing_window": "post_entry",
  "optional": false,
  "failure_policy": "resolve_as_much_as_possible",
  "support_status": "supported"
}
```

## 22.4 Card-local fallback

A CardScripts kártyánkénti fájlmodellje mutatja, hogy mindig lesznek egyedi kivételek.

Az AETERNA-ban a fallback:

- C#;
- stabil ability ID;
- explicit `card_local_fallback`;
- külön support report;
- licencileg saját;
- positive/negative fixture;
- hidden-info audit;
- migration backlog;
- release-ben nem csendes.

---

# 23. Tesztstratégia a CardScripts tanulságai alapján

## 23.1 Minimum module fixture

Minden module:

- schema valid;
- schema invalid;
- source valid;
- source invalid;
- controller valid/invalid;
- timing valid/invalid;
- target valid/invalid;
- cost success/fail;
- replacement/no replacement;
- state version current/stale;
- accepted transition;
- rejected transition immutable;
- event payload;
- viewer redaction;
- deterministic ordering;
- state invariant;
- serialization round-trip.

## 23.2 Kártyaszintű fixture

Az official contribution replay/puzzle ajánlása AETERNA-ban kötelezőbb formát kaphat:

```text
CardScenarioFixture
    initial state
    viewer
    legal actions
    request
    expected response
    expected events
    expected snapshot
    hidden-info assertions
    final invariant
```

## 23.3 Interaction matrix

A kártya önmagában való tesztje nem elég.

Kell:

- source removed before resolution;
- target leaves zone;
- target changes controller;
- target becomes invalid;
- replacement;
- prevention;
- simultaneous trigger;
- optional pass;
- nested reaction;
- delayed expiration;
- cost replacement;
- insufficient resource;
- duplicate request;
- stale request;
- unsupported module;
- loop/depth limit.

## 23.4 Coverage

```text
cards_total
abilities_total
supported
partial
fallback
manual_only
unsupported
not_checked
positive_fixture
negative_fixture
visibility_audited
determinism_audited
```

Publish gate csak kijelölt tesztdeckre legyen kezdetben szigorú, ne a teljes kártyaállományra.

---

# 24. Közvetlenül alkalmazható elvek

## A. Egységes ability lifecycle

**Átvehető:** igen.

AETERNA-forma:

```text
declaration
→ precondition
→ cost preflight
→ target/choice
→ final validation
→ atomic resolution
→ event
→ projection
```

## B. Közös cost helper library

**Átvehető:** elvi szinten.

Feltétel:

- typed plan;
- no mutation during preflight;
- atomic commit;
- rollbackmentes, mert részmutation eleve nem történhet;
- diagnostics és event.

## C. Procedure module család

**Átvehető:** igen.

A kártyánkénti boilerplate csökkenthető core/module procedure-kkel.

## D. Chain/pending-local context

**Átvehető:** igen.

Typed, serializálható MatchState recordként, nem dinamikus global table-ként.

## E. Trigger/resolution property snapshot

**Átvehető:** kiemelten igen.

A source snapshot policy legyen module-schema része.

## F. Stabil konstans és registry

**Átvehető:** igen.

A LOOKUPS-normalizálásba és ability registrybe építendő.

## G. Modernization/deprecation workflow

**Átvehető:** igen.

Schema/module alias, diagnostics és migration map szükséges.

## H. Delta content publish

**Átvehető:** később, feltételesen.

Előbb package identity, fingerprint, versioning, rollback és integrity.

## I. Official/unofficial elkülönítés

**Átvehető:** igen.

AETERNA megfelelő:

- canonical;
- experimental;
- reference;
- disabled;
- expansion-planned;
- test-only.

---

# 25. Kerülendő megoldások

## 25.1 Globális rules API közvetlenül a kártyakódból

Kerülendő:

```text
card-local code
→ arbitrary MatchState mutation
```

## 25.2 Tetszőleges callback closure runtime package-ben

Nem serializálható, nem verziózható és nem auditálható megfelelően.

## 25.3 Check és mutation összekeverése

A `chk` convention ötlete használható, de AETERNA-ban külön típusú preflight és execute
API szükséges.

## 25.4 Sequential multi-cost rollback nélkül

A több cost-komponens fizetése egyetlen tranzakció.

## 25.5 Viewer projection hiánya

Minden ability target, event és choice explicit visibility policyt kap.

## 25.6 Szintaxischecker szemantikai proofként

A build PASS nem jelenti, hogy a szabály helyesen működik.

## 25.7 Magic value és szabad alias

Minden executable érték canonical lookupból jön.

## 25.8 Card-local fallback alapmodellként

Csak kivétel és migrációs állapot.

## 25.9 Yu-Gi-Oh timing vagy szabály átvétele

Az AETERNA saját canonical forrása elsődleges.

## 25.10 Közvetlen AGPL-kódhasználat

Elutasítandó.

---

# 26. Konkrét AETERNA-következtetések

## AC-001 – Ability lifecycle szerződés

Az AETERNA production ability module kötelező lifecycle-je:

```text
trigger candidate
→ condition
→ activation legality
→ target/choice
→ cost plan
→ reaction window
→ final revalidation
→ atomic resolution
→ typed event
→ viewer projection
→ invariant
```

## AC-002 – Source snapshot policy

Minden module deklarálja, mely source property állapotot használja:

- current;
- trigger;
- resolution start;
- last known;
- registration.

## AC-003 – Typed pending context

A complex choice és reaction authoritative, serializálható pending state.

## AC-004 – Cost module catalog

A common costok stabil module ID-t és schema-t kapnak.

## AC-005 – Capability-safe execution

A module nem kap írható MatchState-et.

## AC-006 – LOOKUPS first

Az ability/cost/target/event canonical értékei normalizálandók a további Codex
gameplay munka előtt.

## AC-007 – Support és coverage

A kártya nem tekinthető támogatottnak pusztán azért, mert szerepel a runtime package-ben.

## AC-008 – Semantic fixture

Minden első production module positive és negative fixture-t kap.

## AC-009 – Deprecation

Alias és schema migráció diagnostics-szal és hard failure fokozattal.

## AC-010 – Clean-room only

A CardScriptsből csak dokumentált magas szintű elvek használhatók.

---

# 27. Javasolt későbbi döntési lista

Ezek nem blokkolják a jelen elemzés lezárását, de az ability executor előtt döntendők.

1. Mi az első production ability vertical slice?
2. Mi legyen a module parameter serialization típusrendszere?
3. Mely targetek férnek bele egy legal action payloadba?
4. Mikor kötelező külön pending decision?
5. Milyen source snapshot policy-k támogatottak az első verzióban?
6. Hogyan reprezentáljuk a simultaneous trigger orderinget?
7. Milyen maximum nested reaction/effect depth szükséges?
8. Mi az invalid target alap failure policy?
9. Hogyan kezeljük az optional partial resolutiont?
10. Mi legyen a cost replacement szerződése?
11. Hogyan kapcsolódik az ability registry a Card_ID és Szabályi_Kártya_ID döntéshez?
12. Milyen LOOKUPS-csoportok blockingek production package publishkor?
13. Mi a card-local fallback release policy?
14. Hogyan készül a module coverage report?
15. Mi a module és ruleset version compatibility policy?

---

# 28. Ajánlott implementációs sorrend

Ez a sorrend nem új projektterv, hanem az elemzésből következő technikai függőség.

## Előfeltétel

1. **LOOKUPS-normalizálás lezárása**
2. canonical Realm/card type/activity/payment értékek ellenőrzése
3. ability-hez szükséges új lookup-csoportok döntése
4. loader, diagnostics és blocking policy tesztje

## Core gameplay

5. activity mutation
6. simple Entity `play_card`
7. Hand → Domain transition
8. entry event és projection
9. minimum phase/priority
10. target/choice contract minimum

## Ability foundation

11. ability registry schema
12. module descriptor
13. constrained execution context
14. pending effect context
15. első simple module
16. semantic fixtures
17. support/coverage report

A Codex következő programozási körét csak az első négy pont dokumentált és tesztelt
állapota után célszerű folytatni.

---

# 29. Repository-frissítési igény

A jelen elemzés elkészült, de **nem került a GitHub repositoryba**.

Későbbi, külön jóváhagyott dokumentációs körben szükséges lehet:

1. `learning/analyses/projectignis__cardscripts.md` létrehozása;
2. az aktuális learning katalog új verziójának elkészítése;
3. az aktuális sources list új verziójának elkészítése;
4. a projektrekord státuszának frissítése:
   - vizsgált commit;
   - AGPL;
   - source audit kész;
   - P0 learning;
   - direct integration rejected;
5. a következő projekt kijelölése csak az átszervezett prioritások után;
6. a már elkészült, de még fel nem töltött `LunarTides/Hearthstone.gd` elemzés
   repository-integrációja külön dokumentációs körben.

A központi learning dokumentumok szabálya szerint:

- új verziózott fájl készül;
- a korábbi elfogadott változat történeti snapshot;
- projektenkénti elemzés állandó fájlnevet használ;
- konkrét katalógusverziót nem kell az elemzésbe égetni.

---

# 30. Feladatmegállási és átadási pont

## 30.1 CardScripts learning-feladat

**Státusz: COMPLETE_FOR_REVIEW**

Elkészült:

- upstream azonosítás;
- commit rögzítés;
- repository- és dokumentációaudit;
- effect lifecycle;
- cost;
- target;
- chain context;
- property snapshot;
- procedure module;
- registry;
- CI;
- delta workflow;
- licenc;
- AETERNA authority összevetés;
- clean-room következtetések;
- LOOKUPS-kapcsolat;
- következő döntési kapuk.

Nem történt:

- repository-módosítás;
- commit;
- push;
- branchművelet;
- PR;
- helyi ScriptChecker;
- ocgcore futtatás;
- duel interaction teszt.

## 30.2 Következő projektátadás

A learning-sorozat ezen a ponton megáll.

A következő munkaszakasz előtt a feladatokat újra kell osztani:

### Codexre alkalmas

1. LOOKUPS-normalizálás implementációja és tesztje;
2. kapcsolódó C# runtime loader/diagnostics frissítése;
3. branch-diff és merge conflict technikai kezelése;
4. production engine következő kódmérföldköve;
5. build, test, determinism és bridge ellenőrzések.

### ChatGPT-vel Codex nélkül végezhető

1. CardScripts elemzés végleges szövegauditja;
2. LunarTides elemzés repository-előkészítése;
3. learning katalog és sources list új verziójának előállítása;
4. dokumentumelsőbbség és stale branch tartalmi összevetése;
5. döntési és nyitottkérdés-dokumentumok tartalmi aktualizálása;
6. felhasználónak átadható fájlok elkészítése.

### Sorrendi kapu

```text
LOOKUPS-normalizálás
    ↓
stale guidance branch és main összevezetési terv
    ↓
Codex production kódscope kijelölése
    ↓
Codex implementáció és teszt
    ↓
dokumentációs mérföldkő-frissítés
```

---

# 31. Végső minősítés

A `ProjectIgnis/CardScripts` az eddig vizsgált külső projektek között kiemelkedően
értékes forrás annak megértéséhez, hogyan tartható fenn nagy, hosszú életű,
kártyánként változó ability codebase:

- közös lifecycle;
- helper library;
- procedure module;
- chain-local context;
- source snapshot;
- stable constants;
- modernization;
- deprecation;
- content delta;
- official/unofficial governance.

Az AETERNA számára azonban nem az imperative Lua scripting a követendő architektúra.

A helyes következtetés:

```text
CardScripts szemantikai tapasztalat
    ≠
CardScripts kód vagy API átvétele

CardScripts szemantikai tapasztalat
    →
AETERNA-specifikus typed C# module system
    →
schema-validált runtime package
    →
state-version guarded request
    →
atomic MatchState transition
    →
typed event
    →
viewer-specific projection
    →
deterministic fixtures
```

**Végső döntés:**

- **Learning-prioritás:** P0
- **Első teljes source audit:** elkészült
- **Közvetlen integráció:** elutasítva
- **Kódmásolás vagy port:** elutasítva
- **Yu-Gi-Oh content import:** elutasítva
- **Clean-room elvi újraimplementálás:** ajánlott
- **Legfontosabb közvetlen projektkövetkezmény:** a LOOKUPS-normalizálás és a typed
  ability/cost/target/event névtér lezárása a következő Codex gameplay-szakasz előtt

---

# 32. Változásnapló

## 0.1 – 2026-07-26

- rögzítésre került a `ProjectIgnis/CardScripts` upstream és a vizsgált commit;
- feldolgozásra került a repository célja, Lua 5.3/ocgcore futtatási modellje;
- elkülönítésre került a BabelCDB adat- és a CardScripts végrehajtási réteg;
- feldolgozásra került az effect condition/cost/target/operation lifecycle;
- feldolgozásra került a közös `Cost` rendszer és az atomikussági kockázat;
- feldolgozásra került a `Chain.Data` és a triggering/resolving/registering snapshot;
- feldolgozásra kerültek a fusion/ritual és további procedure modulok;
- feldolgozásra került a konstans-, setcode-, modernization- és deprecation-rendszer;
- feldolgozásra került a ScriptChecker és a delta repository workflow;
- rögzítésre került a syntax/init checker szemantikai korlátja;
- rögzítésre került az AGPL-3.0-or-later és a Yu-Gi-Oh provenance kockázat;
- közvetlen integráció és kódmásolás elutasítva;
- meghatározásra került az AETERNA clean-room typed C# module iránya;
- meghatározásra került a source snapshot és pending context javaslat;
- meghatározásra kerültek a LOOKUPS-normalizálás ability-kapcsolatai;
- rögzítésre került a feladatmegállási és Codex-átadási pont.
