# AETERNA – jcbcn/card-game-engine ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-07-24
- **Státusz:** repository-struktúra-, kiadás-, csomag- és publikus API-szintű első elemzés
- **Fő elemzési fájl:** `learning/analyses/jcbcn__card-game-engine.md`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Repository:** `jcbcn/card-game-engine`
- **Stabil upstream URL:** `https://gitlab.com/jcbcn/card-game-engine`
- **Vizsgált branch:** `main`
- **Vizsgált HEAD:** `e5c9e468` rövid SHA
- **HEAD-üzenet:** `fix(engine): bundle private ProjectReference assemblies into NuGet package`
- **Kapcsolódó merge request:** `!41`
- **Merge request dátuma:** 2026-04-20
- **Vizsgált kiadás:** `CardGameEngine.Engine` 2.6.3 és `CardGameEngine.Abstractions` 2.6.3
- **Kiadás dátuma:** 2026-04-20
- **AETERNA összehasonlítási bázis:** `commander150/Aeterna_Projekt`, `main`
- **AETERNA repository HEAD az elemzés kezdetén:** `4bdade75d77b2229a562daa8bdc95462fc0aeee8`
- **AETERNA production engine technológia:** C#/.NET 8
- **Összehasonlítási szabály:** kizárólag az AETERNA aktuális engine-, contract-, runtime-package-, teszt- és Godot-határához mérve
- **Fontos korlát:** a GitLab teljes forrásfája és fájltartalma ebben a körben nem volt közvetlenül letölthető; ezért a konkrét belső rules-flow, state mutation, legal action, event, RNG és projection állítások helyi forráskód-auditig nyitottak

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Projekt | Card Game Engine |
| Tulajdonos | `jcbcn` / Jacob |
| Platform | GitLab |
| Default branch | `main` |
| Legutóbbi elérhető rövid commit | `e5c9e468` |
| Repository állapota | nyilvános, aktív |
| Fő nyelv és runtime | C# / .NET 10 |
| Publikált fő csomag | `CardGameEngine.Engine` 2.6.3 |
| Publikált contractcsomag | `CardGameEngine.Abstractions` 2.6.3 |
| Engine dependency | `CardGameEngine.Abstractions >= 2.6.3` |
| További engine dependency | `Microsoft.Extensions.ObjectPool >= 10.0.1` |
| Tesztek | külön `tests/` réteg |
| Benchmark | `benchmarks/CardGameEngine.Benchmarks` |
| Dokumentáció | külön `docs/` réteg |
| CI | `.gitlab-ci.yml` |
| API governance | `Microsoft.CodeAnalysis.PublicApiAnalyzers` |
| Release governance | semantic-release commit convention |
| Code coverage | Engine és Abstractions assemblykre konfigurálva |
| Publikált csomag licencmező | `GPL-3.0-only` |
| AETERNA-prioritás | P0 – API/csomaghatár és engine library hardening |
| Elemzés mélysége | első strukturális és package audit; belső forráskód-audit még szükséges |

# 2. Vezetői összefoglaló

A projekt legfontosabb AETERNA-releváns értéke nem egy bizonyított konkrét játékszabály,
hanem a **könyvtárként kiadott engine technikai termékesítése**:

- külön Abstractions és Engine csomag;
- semantic versioning alapú release-folyamat;
- publikus API-változások gépi nyilvántartása;
- teszt- és benchmarkréteg;
- code-coverage konfiguráció;
- GitLab CI;
- NuGet-csomagolási és transitive dependency problémák tényleges javítása;
- immutable state record irányra utaló refaktor;
- capability-szerű, scope-olt kontextusokra utaló `IInHandContext`.

Ez közvetlenül érinti az AETERNA production engine későbbi stabilizálását, mert az
AETERNA már rendelkezik:

- pure C# `Aeterna.Engine` class libraryvel;
- külön `Aeterna.Engine.Headless` futtatóval;
- külön `Aeterna.Engine.Tests` projekttel;
- explicit contractokkal;
- `EngineSession` authority-kapuval;
- runtime package loaderrel;
- Godot-bridge határral.

A külső projektből ezért nem új engine-alapot kell választani. A használható tanulság:

> hogyan lehet az AETERNA már elfogadott engine-jének publikus API-ját, csomagolását,
> verziózását, kompatibilitását, CI-jét és kiadási fegyelmét később megerősíteni.

## 2.1 Rövid döntés

- **Közvetlen NuGet-dependencyként:** nem javasolt
- **Kód beemelésére:** jelenleg nem javasolt
- **Architekturális és release-inspirációként:** igen
- **Legfontosabb terület:** public API governance és package boundary
- **Második terület:** scope-olt context interface-ek
- **Harmadik terület:** tests/benchmarks/coverage/release pipeline
- **Legnagyobb technikai akadály:** .NET 10 kontra AETERNA .NET 8
- **Legnagyobb jogi akadály:** a publikált csomag GPL-3.0-only jelölése
- **Legnagyobb bizonytalanság:** a belső authoritative state és transition contract még nem került fájlszintű audit alá
- **Javasolt felhasználás:** clean-room elvek, saját AETERNA-implementációval

# 3. Bizonyossági szintek

## 3.1 Megerősített

A nyilvánosan elérhető repository- és package-metaadat alapján megerősített:

- a repository `main` branche aktív;
- a rövid HEAD `e5c9e468`;
- a solution tartalmaz `src`, `tests`, `benchmarks` és `docs` réteget;
- van `.gitlab-ci.yml`;
- van `.runsettings`;
- a public API tracking gépesített;
- semantic-release konvenciót használ;
- az Engine és Abstractions 2.6.3 csomagok megjelentek;
- mindkét csomag .NET 10-et céloz;
- az Engine az Abstractions csomagtól és Microsoft object pooltól függ;
- a NuGet licencmező GPL-3.0-only;
- a code coverage az Engine és Abstractions assemblykre van konfigurálva;
- a legutóbbi javítás a private ProjectReference assemblyk csomagba kerülését oldotta meg.

## 3.2 Commit- és fájlnévjelekből származó, erős következtetés

A repository root commit-összefoglalói alapján erősen valószínű:

- a state recordok `IReadOnlyList` helyett `ImmutableArray` irányba mozdultak;
- külön GameState-réteg vagy assembly létezik;
- létezik `IInHandContext`;
- a scoped event signature-öket egyszerűsítették;
- a korábbi `gameManager.Events` publikus vagy központi eventfelületet eltávolították;
- a weapon callbacket `OnEquipped` eseménymintára cserélték;
- a csomag több belső engine assemblyből áll;
- a benchmarkok belső engine-típusokat is mérnek.

Ezeket a helyi forrásfával kell később osztály-, namespace- és contractszinten igazolni.

## 3.3 Még nem bizonyított

Nem állítható még biztosan:

- van-e pontosan egy authoritative MatchState;
- minden mutation egyetlen validált kapun halad-e át;
- van-e request/response contract;
- van-e state version és stale-request védelem;
- van-e legal action projection;
- van-e stabil card instance ID;
- card definition és instance külön modell-e;
- hogyan működik a turn/phase/priority;
- hogyan működik az effect, trigger és reaction ordering;
- van-e deterministic RNG;
- van-e replay vagy event log;
- hogyan védi a hidden informationt;
- van-e viewer-specifikus projection;
- milyen serialization és save contractot használ;
- támogat-e hálózati authorityt;
- milyen package/content modellel tölti a kártyákat;
- milyen tesztlefedettséget ér el ténylegesen.

# 4. Repository-struktúra

A root alapján:

```text
card-game-engine/
├── benchmarks/
│   └── CardGameEngine.Benchmarks/
├── docs/
├── src/
├── tests/
├── .gitlab-ci.yml
├── .releaserc
├── .runsettings
├── AGENTS.md
├── CardGameEngine.sln
├── CardGameEngine.sln.DotSettings
├── Directory.Build.props
├── Directory.Build.targets
├── LICENSE
├── README.md
└── global.json
```

Ez AETERNA-szempontból jó technikai termékstruktúrára utal:

- solution-szintű build policy;
- központi build props és targets;
- test és benchmark elkülönítés;
- docs a kód mellett;
- release automation;
- code coverage;
- explicit API governance.

Az AETERNA jelenlegi repositoryja már külön production Engine, Headless és Tests
projekteket tart. A külső projekt itt arra adhat mintát, hogyan erősítsük meg később:

- assembly boundarykat;
- publikus és internal API-kat;
- NuGet vagy más artifact előállítást;
- compatibility gate-et;
- benchmark gate-et;
- package-content tesztet.

# 5. Abstractions és Engine csomaghatár

A publikált csomagok:

```text
CardGameEngine.Abstractions 2.6.3
CardGameEngine.Engine       2.6.3
```

Az Abstractions csomagnak nincs NuGet dependencyje. Az Engine az Abstractions csomagot
és a Microsoft object poolt fogyasztja.

## 5.1 Hasznos AETERNA-elv

Az AETERNA-ban is érdemes hosszú távon eldönteni, hogy mi a stabil publikus contract:

```text
Aeterna.Engine.Contracts
- request DTO-k
- response DTO-k
- snapshot DTO-k
- legal action DTO-k
- event DTO-k
- diagnostics
- runtime package input contract

Aeterna.Engine
- internal MatchState
- rules
- transitionök
- projection builder
- invariant validator
```

Az AETERNA jelenleg egy assemblyben is megőrizheti ezt a namespace- és visibility-határt.
Külön NuGet package csak akkor szükséges, ha valódi külső fogyasztó vagy külön release
ciklus indokolja.

## 5.2 Fontos óvatosság

A külön Abstractions csomag önmagában nem bizonyít jó authority-modellt. Ha túl sok
mutable state vagy engine implementation type kerül az abstractions rétegbe, a határ
csak csomagolási, nem szabályi.

A helyi auditnak ezért külön ellenőriznie kell:

- mely public type-ok vannak az Abstractions package-ben;
- van-e mutable state interface;
- vannak-e engine-owned object reference-ek;
- milyen collection type-ok kerülnek ki;
- milyen event és context interface-ek publikusak;
- megkerülhető-e a központi game manager/session.

# 6. Public API governance

A repository PublicApiAnalyzers fájlokkal követi:

```text
PublicAPI.Shipped.txt
PublicAPI.Unshipped.txt
```

Új public API esetén analyzer tölti fel az unshipped listát, releasekor pedig külön build
target mozgatja az elfogadott API-t a shipped listába.

## 6.1 Közvetlen AETERNA-tanulság

Az AETERNA contract-first elve már erős, de a C# compiler/build szintjén még később
érdemes lehet public API gate-et bevezetni.

Lehetséges AETERNA-folyamat:

```text
contract döntés
→ C# public API változás
→ analyzer eltérés
→ dokumentáció és migration note
→ explicit review
→ shipped API snapshot
```

Hasznos lehet különösen:

- Godot bridge által hívott publikus API;
- Headless host által hívott API;
- Python JSON/JSONL adapter contract;
- public DTO-k;
- runtime package loader;
- plugin/ability module boundary, ha később publikus lesz.

## 6.2 Amit nem szabad automatikusan átvenni

Nem kell minden internal engine-típust public API-vá tenni.

Az AETERNA számára kívánatos:

- minimális public surface;
- internal MatchState;
- internal rules és transition service;
- publikus, immutable vagy read-only contract DTO;
- controlled friend assembly a Tests/Headless számára;
- Godot bridge számára csak a szükséges belépési pontok.

# 7. Immutable state record irány

A repository commit-összefoglalója szerint történt:

```text
Migrate from IReadOnlyList to ImmutableArray for state records
```

Ez AETERNA-szempontból értékes irány, mert az AETERNA contract és projection objecteknél:

- csökkenti a véletlen külső mutationt;
- stabilabb serializationt ad;
- könnyebbé teszi a snapshot comparisont;
- biztonságosabb thread- és consumer-határt ad;
- jól illik a record/with semanticshez.

## 7.1 AETERNA-alkalmazás

Jó jelöltek immutable collectionre:

- legal action lista;
- player snapshot entries;
- engine event output;
- diagnostics;
- runtime package catalog output;
- debug snapshot;
- public card/zone references.

Nem feltétlenül jó minden belső hot-path state-re, ha a profiling jelentős allocationt
vagy más költséget mutat. A belső MatchState lehet kontrollált mutable modell, miközben
minden kifelé adott projection immutable.

# 8. Scope-olt context interface-ek

A root commitjel szerint bekerült:

```text
IInHandContext
```

A név alapján ez capability-szűkített kontextusra utal: az adott card/effect csak azokat
a műveleteket vagy adatokat érheti el, amelyek kézben lévő állapotban értelmesek.

## 8.1 AETERNA számára hasznos elv

Az AETERNA ability executorának nem szükséges minden esetben teljes MatchState vagy
EngineSession referenciát kapnia.

Lehetséges context-ek:

```text
IAbilityContext
IInHandContext
IInDomainContext
IInWellspringContext
ICombatContext
IPaymentContext
ITargetingContext
IReactionContext
IZoneMoveContext
```

Egy context csak kontrollált műveleteket engedhet:

- state query;
- target resolution;
- transition instruction készítés;
- diagnostic készítés;
- event payload előkészítés.

Nem engedhet:

- közvetlen listamódosítást;
- state version kézi írását;
- zónainvariáns megkerülését;
- rejtett adat jogosulatlan lekérését;
- nested public SubmitAction hívást.

## 8.2 Nyitott kérdés

Forráskód nélkül nem ismert, hogy az `IInHandContext` valóban capability boundary-e,
vagy csak convenience interface. Ezt a helyi audit első feladatai között kell vizsgálni.

# 9. Eventfelület refaktorjele

A root szerint a projekt:

```text
remove gameManager.Events
simplify scoped event signatures
```

irányú refaktort végzett.

AETERNA szempontjából ez azért érdekes, mert az AETERNA különválasztja:

- belső trigger/reaction jeleket;
- transition alatt használt instructionöket;
- commitált EngineEvent outputot;
- viewer-specifikus event projectiont;
- debug eventet.

A külső projekt helyi auditjában meg kell nézni:

- mi váltotta fel a `gameManager.Events` felületet;
- az eventek state-et mutálnak-e;
- event stream vagy callback;
- van-e ordering;
- scoped event alatt milyen scope értendő;
- van-e source/actor/target;
- eventek serializálhatók-e;
- van-e visibility;
- van-e correlation;
- van-e sequence.

# 10. State separation

A solution egyik korábbi strukturális commitja:

```text
refactor(state): Separation of GameState
```

A legutóbbi csomagolási javításból kiderül, hogy az Engine csomag belső
ProjectReference-eket használ, köztük:

```text
Engine.Shared
Engine.GameState
```

Ez megerősíti, hogy a monolit engine-t belső assemblykre bontották.

## 10.1 AETERNA-tanulság

Az AETERNA esetében egyelőre nem indokolt ugyanilyen assembly-számot létrehozni.
A meglévő `Aeterna.Engine` belső mappái és namespace-ei elegendők lehetnek.

Külön assembly akkor indokolt, ha:

- külön publikus compatibility boundary kell;
- eltérő release vagy reuse szükséges;
- dependency irányt compilerrel kell kikényszeríteni;
- buildidő és tesztelés javul;
- ability module sandbox külön assemblyt kíván.

A csomagolási hiba azt is mutatja, hogy a több belső assembly növeli a release-komplexitást.

# 11. NuGet packaging incidens

A 2.6.2 Engine package hibásan csak az `Engine.dll` fájlt tartalmazta. A private
ProjectReference-ek:

- nem jelentek meg transitive package dependencyként;
- de a csomagba sem kerültek be;
- runtime első engine-példányosításkor `FileNotFoundException` keletkezett.

A 2.6.3 javítás a private project assemblyket explicit build outputként tette a NuGet
csomagba.

## 11.1 Közvetlen AETERNA-tanulság

Ha az AETERNA később NuGet, Godot-addon vagy más artifact formában publikál engine-t:

- nem elég a solution build;
- a tényleges csomagot is smoke-testelni kell;
- tiszta consumer projektből kell instantiate-olni;
- a package file-listát auditálni kell;
- minden private assembly jelenlétét ellenőrizni kell;
- license és symbols csomagot is vizsgálni kell;
- runtime package és engine assembly ne keveredjen.

Javasolt AETERNA CI:

```text
build
→ unit tests
→ pack
→ csomag tartalmának ellenőrzése
→ új, üres consumer projekt
→ package install
→ EngineSession instantiate
→ minimal CreateMatch
→ snapshot/legal action smoke
```

# 12. Semantic release

A repository semantic-release commit conventiont használ.

AETERNA számára ez később hasznos lehet, de csak akkor, amikor:

- a public API valóban külső fogyasztókhoz kerül;
- van stabil release cadence;
- contract migration policy készült;
- package publication szükséges.

Jelenleg az AETERNA belső repository commitjai és dokumentumverziói elegendők.
Automatikus semantic release bevezetése nem prioritás a gameplay foundation előtt.

# 13. Teszt-, coverage- és benchmarkstruktúra

Megerősített rétegek:

```text
tests/
benchmarks/CardGameEngine.Benchmarks/
.runsettings
.gitlab-ci.yml
```

A `.runsettings` a következő assemblyket méri:

- `CardGameEngine.Engine.dll`;
- `CardGameEngine.Abstractions.dll`.

Static és dynamic managed instrumentation is engedélyezett.

## 13.1 AETERNA-tanulság

Az AETERNA tesztprojektje később külön reportálhatja:

- contracts coverage;
- transition coverage;
- rejection coverage;
- invariant coverage;
- projection/redaction coverage;
- runtime package coverage;
- ability module coverage.

A százalékos code coverage önmagában nem elég. Kötelező funkcionális proofok:

- accepted transition;
- rejected transition;
- reject-no-mutation;
- stale request;
- duplicate request, ha lesz idempotency;
- hidden information;
- deterministic seed;
- identical input → identical output;
- event sequence;
- snapshot/event parity;
- malformed JSON;
- corrupt runtime package;
- ability unsupported path.

## 13.2 Benchmarkok

A benchmarkprojekt arra utal, hogy a fejlesztő teljesítményt is mér.

AETERNA-ban csak stabil gameplay path után érdemes benchmark gate-et bevezetni:

- CreateMatch;
- ListLegalActions;
- GetPlayerSnapshot;
- SubmitAction;
- event projection;
- runtime package load;
- large card registry;
- reaction queue;
- batch AI simulation.

Nem szabad object poolt vagy más optimalizációt átvenni profiling nélkül.

# 14. Object pooling dependency

Az Engine csomag függ:

```text
Microsoft.Extensions.ObjectPool >= 10.0.1
```

Ez arra utal, hogy bizonyos engine-objektumokat újrahasznosít.

AETERNA-szempontból:

- teljesítményoptimalizálás lehet;
- de state- és request-object pooling veszélyes lehet, ha referencia kiszivárog;
- immutable outputokat nem célszerű újrahasznosítani;
- pooled mutable object resetje teljes és bizonyított legyen;
- debug/replay adat soha ne változzon utólag pooling miatt;
- concurrency policy explicit legyen.

Az AETERNA jelenlegi fázisában object pool bevezetése nem indokolt mérés nélkül.

# 15. .NET 10 kontra AETERNA .NET 8

A publikált csomagok `net10.0` targetet használnak.

Az AETERNA production foundation `net8.0`.

Következmény:

- a package közvetlenül nem illeszthető a jelenlegi AETERNA engine-be;
- egy dependency kedvéért nem szabad runtime-upgrade-et végrehajtani;
- Godot C# kompatibilitást külön kellene ellenőrizni;
- CI, deployment és fejlesztői környezet változna;
- a hosszú távú támogatási döntés külön technology decision lenne.

Az AETERNA csak saját indokból, önálló audit és Godot-kompatibilitási proof után válthat
újabb .NET targetre.

# 16. Licenc

A `CardGameEngine.Engine` és `CardGameEngine.Abstractions` publikált NuGet oldala
`GPL-3.0-only` licencet jelez.

Ez az AETERNA számára kritikus korlát.

## 16.1 Jelenlegi döntés

- közvetlen package dependency: nem;
- forráskód másolása: nem;
- részleges kód beemelése: jogi döntés nélkül nem;
- általános architekturális elvek tanulmányozása: igen;
- saját clean-room implementáció: igen;
- repository LICENSE helyi ellenőrzése: kötelező;
- package metadata és repository LICENSE egyezésének ellenőrzése: kötelező.

Az AETERNA potenciálisan kereskedelmi és saját licencelési igénye miatt GPL-dependency
csak tudatos, külön projekt- és jogi döntés után jöhetne szóba.

# 17. Activity és karbantartás

A repository 2026-ban aktív:

- package kiadások 2026 januárjában és áprilisában;
- 2.6.1, 2.6.2 és 2.6.3 egymást követő javítások;
- MR !41 runtime packaging hibát javított;
- docs, src, tests és CI két hónapon belül frissült;
- benchmark és API hardening öt hónapon belül frissült.

Ez azt jelzi, hogy a projektet nem történeti, hanem aktuális technikai forrásként kell
vizsgálni. Az AETERNA számára ettől még nem válik authorityvá vagy dependencyvé.

# 18. AETERNA authority és contract összevetés

Az AETERNA aktív követelményei:

- egy authoritative MatchState;
- UI nem szabályforrás;
- state mutation csak validált engine transition;
- ActionRequest;
- LegalAction;
- ActionResponse;
- typed EngineEvent;
- viewer-specific projection;
- stable diagnostics;
- state version;
- hidden-information redaction;
- deterministic random;
- replay-alap.

A külső projektnél ezek létezése vagy minősége még nincs megerősítve.

A helyi forráskód-audit során minden pont külön PASS/PARTIAL/FAIL/UNKNOWN státuszt kapjon.

# 19. Javasolt helyi auditmátrix

| Terület | AETERNA-követelmény | Jelenlegi státusz |
|---|---|:---:|
| Authority | egyetlen EngineSession/MatchState | UNKNOWN |
| Mutation gate | minden mutation validált kapun át | UNKNOWN |
| State version | stale request védelem | UNKNOWN |
| Legal action | engine-calculated legal space | UNKNOWN |
| Request | schema + IDs + payload | UNKNOWN |
| Response | accepted/rejected + diagnostics | UNKNOWN |
| Event | typed + sequence + visibility | UNKNOWN |
| Projection | viewer-specific snapshot | UNKNOWN |
| Hidden info | redacted opponent state | UNKNOWN |
| Card instance | stable ID + registry | UNKNOWN |
| Zones | kétirányú invariant | UNKNOWN |
| Turn/phase | explicit state machine | UNKNOWN |
| Reaction | deterministic ordering + budget | UNKNOWN |
| RNG | seedelt és auditálható | UNKNOWN |
| Replay | event/input reprodukció | UNKNOWN |
| Runtime data | package/definition model | UNKNOWN |
| Godot boundary | UI nem mutál state-et | N/A / adapter szükséges |
| Public API | tracked and versioned | PASS – metadata alapján |
| Packaging | published and tested | PARTIAL – 2.6.2 incidens, 2.6.3 fix |
| Tests | külön test layer | PASS – struktúra |
| Benchmarks | külön benchmark layer | PASS – struktúra |
| Coverage | Engine + Abstractions | PASS – konfiguráció |
| License | AETERNA-kompatibilis | FAIL jelenlegi dependency-döntéshez |
| Runtime target | AETERNA net8 kompatibilis | FAIL közvetlen dependencyhez |

# 20. Közvetlenül használható AETERNA-elvek

1. Public API snapshot és analyzer gate.
2. Abstractions és implementation tudatos elválasztása.
3. Minimális public surface.
4. Immutable public state/projection collectionök.
5. Scope-olt ability/effect context interface-ek.
6. Központi Directory.Build policy.
7. Test és benchmark külön projekt.
8. Assemblynkénti coverage.
9. Semantic version és compatibility note.
10. Package-content smoke test.
11. Clean consumer-install test.
12. Private assembly csomagolás ellenőrzése.
13. Public API változás csak explicit reviewval.
14. Package license metadata auditja.
15. Release artifact reprodukálhatóság.

# 21. Amit nem szabad átvenni vagy közvetlenül bekötni

1. A NuGet package közvetlen dependencyként.
2. .NET 10 upgrade csak e projekt miatt.
3. GPL-kód jogi döntés nélkül.
4. Object pooling profiling nélkül.
5. Belső multi-assembly bontás valódi szükséglet nélkül.
6. Public interface-ek automatikus szaporítása.
7. Kliensnek kiadott mutable engine context.
8. Feltételezett event vagy state modell forrásaudit nélkül.
9. Package release eredményének elfogadása consumer smoke nélkül.
10. Külső engine saját AETERNA-authorityként.

# 22. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | PublicApiAnalyzers proof az `Aeterna.Engine` publikus API-ra | Build | P1 |
| 2 | PublicAPI shipped/unshipped policy dokumentálása | Docs/Build | P1 |
| 3 | Engine public és internal surface audit | Engine | P0 |
| 4 | Scope-olt ability context tervezési proof | Engine | P1 |
| 5 | `IInHandContext` helyi forrásaudit után fogalmi összevetés | Learning | P1 |
| 6 | Package-content smoke test sablon | CI | P1 |
| 7 | Empty consumer project integration test | CI | P1 |
| 8 | Contract assembly különválasztásának későbbi decision gate-je | Architecture | P2 |
| 9 | ImmutableArray használat public projectionökben fenntartása | Contracts | P0 |
| 10 | Internal state immutable/mutable döntés profilinggal | Engine | P2 |
| 11 | Benchmarks csak stabil gameplay után | Performance | P2 |
| 12 | Object pooling csak mérés után | Performance | P2 |
| 13 | GPL dependency tiltás külön dokumentálása | License | P0 |
| 14 | .NET target upgrade külön technology decision legyen | Architecture | P0 |
| 15 | Local source tree audit a downloaded copy alapján | Learning | P0 |
| 16 | Full SHA és local origin rögzítése | Learning | P0 |
| 17 | Repository LICENSE és NuGet license parity audit | License | P0 |
| 18 | Authority/contract auditmátrix kitöltése | Learning/Engine | P0 |
| 19 | CI pipeline tartalmi audit | CI | P1 |
| 20 | Package 2.6.3 local consumer smoke | Learning | P1 |

# 23. Bizonyítékjegyzék

| ID | Állítás | Forrás | Bizonyosság |
|---|---|---|---|
| E-001 | Aktív main branch és rövid HEAD `e5c9e468` | GitLab root | megerősített |
| E-002 | `src`, `tests`, `benchmarks`, `docs` struktúra | GitLab root | megerősített |
| E-003 | GitLab CI, runsettings, build props/targets | GitLab root | megerősített |
| E-004 | Semantic release convention | README/NuGet README | megerősített |
| E-005 | PublicApiAnalyzers használat | README/NuGet README | megerősített |
| E-006 | `ShipPublicApi` build target | README/NuGet README | megerősített |
| E-007 | Engine 2.6.3, net10.0 | NuGet | megerősített |
| E-008 | Abstractions 2.6.3, net10.0 | NuGet | megerősített |
| E-009 | Engine → Abstractions dependency | NuGet | megerősített |
| E-010 | Engine → ObjectPool dependency | NuGet | megerősített |
| E-011 | NuGet GPL-3.0-only jelölés | NuGet | megerősített |
| E-012 | Engine és Abstractions coverage | `.runsettings` publikus nézete | megerősített |
| E-013 | ImmutableArray state refactor | GitLab root commit summary | erős jel |
| E-014 | `IInHandContext` és scoped event refactor | GitLab root commit summary | erős jel |
| E-015 | GameState separation | GitLab root commit summary | erős jel |
| E-016 | Engine.Shared és Engine.GameState belső assembly | MR !41 | megerősített |
| E-017 | 2.6.2 hiányos package és runtime FileNotFound | MR !41 | megerősített |
| E-018 | 2.6.3 package fix | MR !41 és NuGet | megerősített |
| E-019 | AETERNA net8 production foundation | AETERNA Architecture | megerősített |
| E-020 | AETERNA EngineSession authority és request gate | AETERNA kód/contract | megerősített |

# 24. Nyitott kérdések

1. Mi a `main` teljes commit SHA-ja?
2. A helyi letöltött mappa pontosan az `e5c9e468` állapot-e?
3. Mi a repository LICENSE teljes tartalma?
4. Egyezik-e a repository LICENSE a NuGet `GPL-3.0-only` mezővel?
5. Mely projektek vannak ténylegesen a `src/` alatt?
6. Mi van az Abstractions public API-ban?
7. Milyen GameState rekordok használnak ImmutableArrayt?
8. Ki birtokolja és mutálja a GameState-et?
9. Van-e egyetlen GameManager vagy EngineSession authority?
10. A caller kap-e mutable state referenciát?
11. Mit enged pontosan az `IInHandContext`?
12. Van-e legal action vagy validation service?
13. Milyen card instance és zone modell van?
14. Hogyan történik a draw, play, attack és end turn?
15. Milyen effect/reaction modellel dolgozik?
16. Hogyan garantált a reaction ordering?
17. Van-e recursion/loop budget?
18. Milyen eventtípusok vannak a `gameManager.Events` eltávolítása után?
19. Van-e event log és sequence?
20. Van-e player-specific event visibility?
21. Van-e deterministic RNG és seed?
22. Van-e replay?
23. Van-e serialization/save?
24. Van-e multiplayer vagy network contract?
25. Milyen card library/plugin boundary van?
26. Hogyan használja a VanillaHS package az Abstractions API-t?
27. Milyen coverage és tesztszám érhető el?
28. Mit mérnek a benchmarkok?
29. A GitLab CI milyen stage-eket és gate-eket futtat?
30. A 2.6.3 package tiszta consumer projektből hibamentes-e?

# 25. Következő helyi vizsgálati lépések

## 25.1 Codex nélkül

1. Helyi `.git/config` ellenőrzése.
2. `git rev-parse HEAD`.
3. `git remote -v`.
4. `git status`.
5. solution projectlista.
6. repository LICENSE megnyitása.
7. `global.json` és target frameworkek.
8. `dotnet restore`.
9. `dotnet build`.
10. `dotnet test`.
11. coverage futtatása.
12. benchmarklista futtatás nélkül.
13. PublicAPI fájlok listázása.
14. Abstractions public type lista.
15. GameState és manager/session belépési pontok.
16. mutation surface lista.
17. RNG keresés.
18. serialization keresés.
19. event/context type lista.
20. package build.
21. package content lista.
22. clean consumer smoke.
23. NuGet license és repository license egyeztetés.
24. auditmátrix kitöltése.

## 25.2 Később Codexszel gyorsítható

1. teljes source graph;
2. public API inventory;
3. mutation call graph;
4. authority bypass audit;
5. event/reaction ordering audit;
6. deterministic RNG audit;
7. card instance és zone invariant audit;
8. tests-to-contract mapping;
9. benchmark relevanciaelemzés;
10. AETERNA context-interface proof-of-concept.

# 26. Végső előzetes minősítés

- **Aktivitás:** magas
- **Technológiai modernség:** magas
- **AETERNA target compatibility:** közvetlenül nem megfelelő
- **Public API governance érték:** nagyon magas
- **Packaging/release érték:** magas
- **Teszt/benchmark struktúraérték:** magas
- **Rules-engine érték:** még nem bizonyított
- **Authority és projection érték:** még nem bizonyított
- **Licenc kompatibilitás közvetlen dependencyhez:** nem megfelelő jelenlegi döntés szerint
- **Közvetlen dependencyként:** elutasítandó
- **Clean-room tanulási forrásként:** elfogadható
- **Elemzés státusza:** első strukturális/package audit lezárva; belső forráskód-audit nyitott
- **AETERNA-ban következő hasznos alkalmazás:** public API és package hardening backlog, de csak a gameplay foundation prioritásainak megőrzésével

# 27. Változásnapló

## 0.1 – 2026-07-24

- elkészült a repository-struktúra- és package-szintű első elemzés;
- rögzítésre került a `main` rövid HEAD és a 2.6.3 kiadás;
- feldolgozásra került az Abstractions/Engine csomaghatár;
- feldolgozásra került a PublicApiAnalyzers és semantic-release folyamat;
- rögzítésre került az immutable state és scope-olt context irány;
- feldolgozásra került a 2.6.2 package incidens és a 2.6.3 javítás;
- elkészült az AETERNA package consumer smoke javaslat;
- rögzítésre került a .NET 10 és AETERNA .NET 8 inkompatibilitás;
- rögzítésre került a NuGet GPL-3.0-only licenckorlát;
- elkészült a részletes helyi forráskód-auditmátrix;
- az összehasonlítás kizárólag az AETERNA aktív rendszeréhez történt.
