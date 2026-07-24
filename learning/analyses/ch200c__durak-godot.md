# AETERNA – ch200c/Durak.Godot ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.3
- **Dátum:** 2026-07-24
- **Státusz:** előzetes, repository-forrásokra épülő elemzés
- **Fő elemzési fájl:** `learning/analyses/ch200c__durak-godot.md`
- **Későbbi részanyagok:** `learning/analyses/ch200c__durak-godot/`
- **Kapcsolódó katalógus:** az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `45852153e1619d288806526380011e757dcd8083`
- **Commit üzenete:** `Update readme.md`
- **Vizsgálati korlát:** helyi build, tesztfuttatás, Godot-import és export ebben a körben nem történt
- **Besorolás:** Godot 4.3 / C# 3D kártyajáték külön pure C# gameplay libraryvel
- **Elsődleges AETERNA-érték:** Godot kliens és C# rules/domain réteg tényleges projekt-szintű elválasztása

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Projekt neve | Durak |
| Repository | `ch200c/Durak.Godot` |
| Eredeti URL | https://github.com/ch200c/Durak.Godot |
| Vizsgált branch | `master` |
| Vizsgált commit | `45852153e1619d288806526380011e757dcd8083` |
| Repository állapota | nyilvános, nem archivált |
| Utolsó vizsgált tartalmi állapot | 2024. október |
| Vizuális motor | Godot 4.3 |
| Godot-projekt target | .NET 8; Android esetén .NET 7 |
| Gameplay library | pure .NET 8 C# |
| Tesztframework | xUnit + FluentAssertions + coverlet |
| Játékmód | 2–6 játékos egyéni Durak |
| Hálózat | nem találtunk hálózati réteget |
| Licencfájl | MIT-szöveg, kitöltetlen copyright-helyőrzővel |
| AETERNA-prioritás | P0 – engine/Godot határ, tesztstruktúra és 3D presentation |

A README a projektet C#-ban, Godottal készült 3D Durak-kártyajátékként írja le,
2–6 játékos támogatással, kártyaanimációkkal, mozgatható kamerával és mini-map felülettel.

# 2. Vezetői összefoglaló

## 2.1 Miért különösen fontos ez a projekt?

A korábban vizsgált Godot/C# projektek többnyire a UI-, scene- és játékszabály-réteget
erősen összekeverték. A Durak.Godot ezzel szemben egy négyrétegű solutiont használ:

```text
Durak.Godot
Durak.Gameplay
Durak.Gameplay.UnitTests
Durak.Gameplay.FunctionalTests
```

A `Durak.Gameplay` projekt szabványos `Microsoft.NET.Sdk` alapú pure .NET 8 library,
Godot-függőség nélkül. A Godot kliens ezt ProjectReference-ként használja, miközben a
unit és functional tesztek szintén közvetlenül a gameplay libraryre hivatkoznak.

Ez az eddigi vizsgálatok közül a legközelebbi szerkezeti párhuzam az AETERNA kívánt
felosztásához:

```text
Aeterna.Engine
Aeterna.Engine.Tests
Aeterna Godot client / bridge
```

## 2.2 Rövid döntés

- **Mélyelemzés folytatása:** igen
- **Közvetlen technológiai illeszkedés:** magas
- **Közvetlen szabálymotor-átvétel:** nem
- **Architekturális minta:** igen
- **Godot-presentation minta:** igen
- **Tesztstruktúra-minta:** igen, korrekciókkal
- **Multiplayer referencia:** nem
- **Determinisztikus engine referencia:** nem
- **Elsődleges kockázat:** a teljes játék-orchestration túl nagy része a Godot `MainNode` osztályban marad
- **Licenckockázat:** a LICENSE MIT-szöveg, de a copyright sor kitöltetlen sablon

# 3. Előzetes értékelés

| Szempont | Pontszám | Indok |
|---|:---:|---|
| Godot/C# technológiai illeszkedés | 5/5 | Godot 4.3, C#, .NET 8 |
| Engine–UI rétegzett felépítés | 4/5 | külön pure C# gameplay library |
| Rules-engine tanulási érték | 4/5 | explicit domain osztályok, validáció és eventek |
| Godot kliens tanulási érték | 4/5 | 3D card node-ok, kézelrendezés, animáció |
| Tesztelési tanulási érték | 4/5 | unit + functional projektek, de hibás tesztminta is van |
| Determinizmus | 1/5 | `Random.Shared`, seed contract nélkül |
| Replay / event log | 1/5 | domain eventek vannak, de nincs tartós eseménynapló |
| Multiplayer | 0/5 | helyi AI-játék, hálózati authority nélkül |
| Hidden information | 2/5 | vizuális takarás van, viewer projection nincs |
| Adatpipeline | 1/5 | fix hagyományos kártyakészlet, nincs külső tartalomcsomag |
| Kódminőség | 3/5 | jó projekthatár, de nagy MainNode és több TODO |
| Dokumentáltság | 2/5 | rövid README, a kód beszédesebb |
| Licencelési biztonság | 3/5 | MIT-szöveg, de kitöltetlen copyright |
| Összesített prioritás | **P0** | közvetlen AETERNA engine/Godot szerkezeti referencia |

# 4. Solution- és projektstruktúra

A solution négy projektet tartalmaz:

```text
Durak.Godot.sln
├── Durak.Godot
├── src/
│   └── Durak.Gameplay
├── tests/
│   ├── Durak.Gameplay.UnitTests
│   └── Durak.Gameplay.FunctionalTests
└── Godot scene-ek és assetek
```

## 4.1 `Durak.Godot`

- `Godot.NET.Sdk/4.3.0`;
- `net8.0`;
- Android célon `net7.0`;
- nullable bekapcsolva;
- a `src/Durak.Gameplay/**` és `tests/**` forrásokat kizárja a Godot projekt saját
  compile-listájából;
- ProjectReference-szel hivatkozik a gameplay libraryre.

Ez tiszta és fontos minta: ugyanabban a repositoryban van a domain és a kliens, de nem
fordítják őket egyetlen Godot-kódhalmazként össze.

## 4.2 `Durak.Gameplay`

- szabványos `Microsoft.NET.Sdk`;
- `net8.0`;
- nincs Godot-csomaghivatkozás;
- implicit usings és nullable engedélyezve;
- a domain közvetlenül tesztelhető Godot nélkül.

## 4.3 Unit és functional tesztek

Mindkét tesztprojekt:

- `net8.0`;
- xUnit;
- FluentAssertions;
- Microsoft.NET.Test.Sdk;
- coverlet collector;
- közvetlenül a `Durak.Gameplay` libraryre hivatkozik.

Ez az AETERNA production engine tesztstruktúrájával közvetlenül összevethető.

# 5. Domainmodell

## 5.1 `Card`

A kártya immutable-szerű C# `record`:

```text
Card
- Rank
- Suit
```

A konstrukciókor és init-kor validálja:

- a rank 2–14 tartományt;
- a suit engedélyezett értékét.

### Erősség

- egyszerű értékobjektum;
- value equality;
- nincs Godot-függés;
- konstrukciókor érvényes állapot;
- könnyen tesztelhető.

### AETERNA-korlát

Az AETERNA kártyája nem puszta értékobjektum, ezért külön kell tartani:

- `RuntimeCardDefinition`;
- `CardInstanceId`;
- owner/controller;
- zone;
- activity state;
- modifier state;
- visibility state.

A Durak `Card` modell jó példa egyszerű immutable definition/value objectre, de nem
teljes TCG-instance modell.

## 5.2 `Player`

A Player:

- stabil string ID-t tart;
- saját `List<Card>` kézzel rendelkezik;
- `PickUp` és `Shed` műveleteket ad;
- `CardsAdded` és `CardRemoved` eventeket küld;
- kifelé read-only listát ad.

### Pozitívum

A UI nem közvetlenül módosítja a listát; domain metódusok végzik a változtatást.

### Kockázat

A `Shed` nem ellenőrzi, hogy a `Remove` sikeres volt-e. Ha nem létező kártyát kap,
akkor is kibocsáthat `CardRemoved` eventet. Az `Attack.CanPlay` normál útvonalon ezt
megelőzi, de a Player önálló invariánsai nem teljesek.

## 5.3 `Deck`

A Deck:

1. `ICardProvider` forrásból kártyákat kér;
2. `ICardShuffler` stratégiával kever;
3. az utolsó kártyából meghatározza a trump lapot és színt;
4. queue-ban tárolja a sorrendet;
5. sikeres eltávolításkor eventet küld.

Az `ICardProvider` és `ICardShuffler` interface jó dependency-injection pont.

## 5.4 `Dealer`

A Dealer:

- beállított kézméretig oszt;
- külön kezeli az első és a későbbi osztást;
- a korábbi támadás résztvevőinek sorrendjében tölt vissza;
- `IDeck` interfészre támaszkodik;
- bool eredménnyel jelzi, hogy teljes volt-e a feltöltés.

Ez jó példa egy szűk, egyetlen felelősségű domain service-re.

# 6. Támadás és szabályvalidáció

## 6.1 `AttackState`

A támadás explicit állapotai:

- `InProgress`;
- `BeatenOff`;
- `Successful`.

Ez kicsi, de tiszta state machine.

## 6.2 `CanPlay`

Az `Attack.CanPlay` külön, nem mutáló ellenőrzést ad, és `CanPlayResult` rekordot ad:

```text
CanPlay
Error
```

A vizsgált ellenőrzések:

- a támadás még folyamatban van-e;
- a kártya a játékos kezében van-e;
- nem került-e már kijátszásra;
- támadóként a rank egyezik-e valamelyik asztali rankkel;
- van-e még támadási kapacitás;
- a védőnek van-e kártyája;
- az azonos színű védőlap rangja elegendő-e;
- eltérő szín esetén trump-e.

### Közvetlen AETERNA-tanulság

A mutation előtt külön preflight metódus létezik, és a `Play` ugyanazt a validációt
újra meghívja. Ez megfelel annak az AETERNA-elvnek, hogy:

```text
legal hint / preflight
→ request
→ execution-time revalidation
→ mutation
```

## 6.3 `Play`

A Play:

1. meghívja a `CanPlay` metódust;
2. sikertelenségnél `GameplayException`;
3. létrehozza az `AttackCard` rekordot;
4. hozzáadja a támadási listához;
5. eltávolítja a játékos kezéből;
6. domain eventet küld.

### Erősség

Az ellenőrzés a mutation előtt történik.

### Kockázat

A két mutation:

```text
_cards.Add(...)
player.Shed(...)
```

nem valódi tranzakció. Ha a második lépés vagy eventkezelő hibázik, nincs rollback.

Az AETERNA engine-ben:

- először teljes preflight;
- majd egyetlen kontrollált transition;
- csak sikeres mutation után eventanyag;
- exception esetén sem részállapot;
- state version csak commit után nőjön.

## 6.4 `End`

A támadás lezárása:

- páros számú asztali lapnál `BeatenOff`;
- páratlan számú lapnál a védő felveszi az összes lapot, és `Successful`;
- ezután `AttackEnded` event jön létre.

Egyszerű és áttekinthető, de az event payload üres, ezért a fogyasztónak vissza kell
olvasnia a mutable Attack objektum állapotát.

AETERNA-ban az event önálló, immutable payloadot tartalmazzon.

# 7. Körlogika

## 7.1 Első támadó

A `TurnLogic.FirstAttack`:

- megkeresi a legalacsonyabb trump lapot;
- annak tulajdonosa kezd;
- ha nincs trump a játékosok kezében, `Random.Shared` választ.

## 7.2 Következő támadás

A korábbi támadás állapotától függően választ új támadót és védőt:

- successful támadás után a korábbi védő kimarad;
- beaten-off támadás után a kör következő játékosa indul;
- üres kezű játékosokat kihagyja;
- egy vagy nulla aktív játékosnál lezár.

## 7.3 Fő kockázatok

- nincs injektált RNG;
- nincs seed;
- nincs decision event;
- `Stack<IAttack>` miatt az `Attacks` property fordított, stack-alapú nézetet ad;
- az attack limit ellenőrzése `> 100`, ezért a 101. elem még bekerülhet, és csak a következő
  hívás dob;
- a `NextIndex` egyik végállapota `NotImplementedException("TODO2")`;
- nincs explicit match state vagy state version;
- nincs player-facing projection;
- a körlogika közvetlen `Player` objektumreferenciákra épül.

# 8. Eseménymodell

Domain eventek:

- `Player.CardsAdded`;
- `Player.CardRemoved`;
- `Deck.CardRemoved`;
- `Attack.AttackCardAdded`;
- `Attack.AttackEnded`.

## 8.1 Erősség

A Godot layer a gameplay eventjeire reagálhat, ezért nem kell pollinggal újraolvasni
minden változást.

## 8.2 Korlát

Ezek .NET object eventek, nem tartós engine eventek:

- nincs sequence;
- nincs state version;
- nincs event ID;
- nincs request ID;
- nincs replay;
- nincs serializálható payload-contract;
- nincs viewer filtering;
- nincs hidden-information redaction;
- eventkezelő exception megszakíthatja a transitiont.

AETERNA esetén a belső domain notification és a player-facing typed engine event
külön réteg maradjon.

# 9. Godot-integráció

## 9.1 `MainNode`

A `MainNode : Node3D` a következőket egyszerre végzi:

- játékosok létrehozása;
- domain objektumok létrehozása;
- deck, dealer és turn logic összekötése;
- kéz- és kártyanode-ok kezelése;
- UI-gombok;
- kamera;
- támadás indítása és lezárása;
- egyszerű AI;
- animációs várakozások;
- asztali elhelyezés;
- game-over;
- scene reset;
- debug log.

A fájl több mint 600 soros, ezért a jó domain-határ ellenére a Godot oldalon
„god object” orchestration jött létre.

## 9.2 Pozitív bridge-minta

A Godot kliens nem implementálja újra a legtöbb kártyaszabályt. Kattintáskor és AI-nál
az `Attack.CanPlay` és `Attack.Play` domain metódusokat használja.

Ez fontos: a rules truth a gameplay libraryben marad.

## 9.3 Kockázatos orchestration

A kliens közvetlenül tartja:

- `_turnLogic`;
- `_currentAttack`;
- `_dealer`;
- `_deck`;

és közvetlenül hívja az `Attack.End`, `Dealer.Deal`, `TurnLogic.TryGetNextAttack`
metódusokat.

Nincs egyetlen engine session / application service, amely requestet fogad és snapshotot ad.

AETERNA-ban helyesebb:

```text
Godot input
→ EngineSession request
→ authoritative validation/transition
→ EngineResult
→ snapshot + events
→ Godot projection
```

# 10. `CardNode` és 3D presentation

A `CardNode : StaticBody3D` külön kezeli:

- `Card` domain objektumot;
- target pozíciót és rotációt;
- vizuális `CardState` értéket;
- animáció engedélyezését;
- kézbeli sorrendet;
- kattintási signalt;
- texture lookupot;
- lerp-alapú mozgást;
- sorting offsetet;
- discard és table placement műveleteket.

## 10.1 Hasznos minták

- külön domain Card és CardNode view;
- azonos domain card alapján texture lookup;
- target transform és actual transform különválasztása;
- animation on/off mód;
- CardState presentation enum;
- group-alapú scene lookup;
- front/back elrejtés más játékosoknál.

## 10.2 Kockázatok

- abszolút `/root/...` node path;
- `DateTime.UtcNow` presentation timing;
- a visual CardState részben duplikálja a domain zónaállapotot;
- nincs engine snapshotból rekonstruálható view model;
- a Card record value equalityje miatt azonos rank/suit lapoknál a scene lookup
  `SingleOrDefault` problémás lehet több azonos példányt használó TCG-ben;
- asset path hard-coded.

AETERNA-ban minden view stabil `CardInstanceId` alapján kapcsolódjon.

# 11. `PlayerNode`

A PlayerNode:

- létrehozza a saját domain `Player` objektumát;
- feliratkozik annak eventjeire;
- CardNode-okat példányosít vagy reparentel;
- kezeli a kézelrendezést;
- helyi `SortedList<int, Card>` sorrendet tart;
- signalokat továbbít a MainNode felé.

## 11.1 Fontos tanulság

A Godot node és a domain player párosítása világos, de a domain player létrehozása a
view node-ban történik. Production rendszerben fordított irány szükséges:

```text
engine player snapshot
→ PlayerViewModel
→ PlayerNode
```

## 11.2 Lehetséges hiba

A `RemoveCardFromOrder` ezt használja:

```text
_order.Remove(_order.IndexOfValue(card))
```

A `SortedList.Remove` kulcsot vár, miközben az `IndexOfValue` indexet ad. Ha a kulcsok
nem esnek egybe az aktuális indexekkel, hibás elemet törölhet vagy semmit sem törölhet.
Helyi teszttel ellenőrizendő.

# 12. Egyszerű AI

A `MainNode.PlayAsNonMainPlayer`:

- végigpróbálja a játékos kezének kártyáit;
- az első `Attack.CanPlay` szerint jogszerű lapot kijátssza;
- ha nincs ilyen, lezárja a támadást.

Ez szabályosan a domain validációt használja, de nem stratégiai AI:

- nincs scoring;
- nincs lookahead;
- nincs seedelt policy;
- nincs döntésnapló;
- nincs action space;
- nincs replayable decision.

Az AETERNA AI számára csak a legal-action fogyasztási minta hasznos.

# 13. Determinizmus

Nem determinisztikus pontok:

- `DefaultCardShuffler` → `Random.Shared.Next()`;
- `TurnLogic.FirstAttack` fallback → `Random.Shared.Next(...)`;
- functional szimuláció a default shufflert használja;
- nincs seed vagy RNG interface a TurnLogicban;
- nincs random-decision event.

Pozitívum, hogy az `ICardShuffler` már létezik, ezért a paklikeverés könnyen cserélhető
seedelt implementációra. A TurnLogic RNG-je azonban még közvetlen függőség.

Javasolt minta:

```text
IRandomSource
- NextInt(...)
- Shuffle(...)
- State/seed metadata
```

Minden random döntésből typed event készüljön.

# 14. Tesztstruktúra

## 14.1 Unit tesztek

Külön unit project vizsgálja többek között:

- Attack;
- Deck;
- Dealer;
- TurnLogic;
- FrenchSuited36CardProvider.

Az AttackTests ellenőrzi:

- constructor state;
- attacker hozzáadás;
- első lap kijátszás;
- védő nélküli/érvénytelen helyzet;
- hibás védekező lap;
- hibás rankű új támadás.

## 14.2 Functional tesztek

Az `IndividualGameTests` 2–6 játékossal teljes játékot szimulál.

Ez erős elv, mert Godot nélkül vizsgálja a teljes domain folyamatot.

## 14.3 Kritikus teszthiba

A teszt:

```text
try
{
    gameSimulator.Simulate();
}
catch (Exception ex)
{
    log...
}
```

minden exceptiont elkap, de nem dobja újra és nem fail-el. Így a szimuláció hibával
megszakadhat, miközben a teszt később akár még PASS-t is adhat.

Ez hamis zöld eredmény veszélye.

Helyes megoldás:

- ne kapja el a kivételt;
- vagy logolás után `throw`;
- vagy `Record.Exception` + explicit assertion.

## 14.4 GameSimulator korlátai

- `NotImplementedException("TODO3")`;
- exception message stringre épülő flow;
- csak principal attacker és defender;
- nincs több támadó tényleges AI-ja;
- nincs seedelt ismételhetőség;
- nincs max step/time guard;
- nincs trajectory artifact;
- nincs state hash.

# 15. Build és CI

A solution Debug, Release, ExportDebug és ExportRelease konfigurációkat tartalmaz.

A távoli forrásvizsgálat során nem találtunk:

- GitHub Actions workflowt;
- CI buildet;
- automatikus Godot exportot;
- artifact publicationt;
- release pipeline-t.

A README TODO szerint a tesztek javítása és bővítése még nyitott feladat.

# 16. Hidden information és projection

A 3D kliens vizuálisan elrejti az ellenfél lapjainak elejét, de a domain állapotban:

- minden Player objektum teljes keze elérhető;
- a MainNode minden játékost ismer;
- nincs viewer-specific snapshot;
- nincs redacted CardProjection;
- nincs authoritative server boundary.

Ez helyi egyjátékos alkalmazásban elfogadható, multiplayer AETERNA esetén nem.

# 17. Multiplayer

A README-ben szereplő „2–6 player” helyi, egyéni játékosfelállást jelent. A vizsgált
forrásban nem találtunk:

- hálózati transportot;
- lobbyt;
- szervert;
- reconnectet;
- state syncet;
- client request contractot;
- anti-cheat réteget.

Ezért a projekt multiplayer engine-referenciának nem használható.

# 18. Licenc

A repository `LICENSE.txt` fájlja MIT licencszöveget tartalmaz, de a copyright sor:

```text
Copyright (c) [year] [fullname]
```

kitöltetlen sablon maradt.

Következmény:

- architekturális tanulás biztonságosan végezhető;
- közvetlen kódátvételnél külön licencértékelés ajánlott;
- assetek licence külön ellenőrzendő;
- a README külső 3D table model forrást is megnevez;
- az MIT attribution szövegét kódátvételnél meg kell őrizni;
- a hiányos szerzői sor miatt saját újraimplementálás a tisztább irány.

# 19. Erősségek

1. Tényleges pure C# gameplay library.
2. Godot project csak ProjectReference-szel kapcsolódik.
3. Unit és functional tesztprojekt különválasztva.
4. Explicit domain interface-ek.
5. Injektálható card provider és shuffler.
6. Immutable-szerű Card record.
7. Konstrukciós validáció.
8. `CanPlayResult` alapú preflight.
9. Execution-time revalidation.
10. Domain eventek.
11. Külön CardNode view.
12. 3D hand/table presentation.
13. 2–6 játékos functional szimuláció.
14. Nullable és magas warning level.
15. Kis, áttekinthető domainréteg.

# 20. Gyengeségek és technikai adósság

1. Nincs EngineSession/application service.
2. Nincs központi MatchState.
3. Nincs state version.
4. Nincs request contract.
5. Nincs immutable engine event log.
6. Nincs replay.
7. Nincs viewer projection.
8. Nincs seedelt RNG.
9. `Random.Shared` közvetlen függőség.
10. MainNode túl sok felelősséget tart.
11. Async void eventkezelők és Task.Delay orchestration.
12. Animation és domain flow időben összekapcsolódik.
13. Abszolút scene pathok.
14. Godot group keresések domain Card value equality alapján.
15. `Player.Shed` nem igazolja a sikeres eltávolítást.
16. Attack mutation nem tranzakciós.
17. AttackEnded event payload nélküli.
18. Attack limit off-by-one gyanú.
19. `TODO2` és `TODO3` NotImplementedException.
20. Functional teszt elnyelhet exceptiont.
21. Exception message-ek vezérlik a GameSimulatort.
22. Nincs CI.
23. Nincs network authority.
24. A license copyright sora kitöltetlen.
25. A README maga is refaktort és tesztjavítást jelöl TODO-ként.

# 21. AETERNA számára közvetlenül átvehető elvek

## 21.1 Projekthatár

```text
Aeterna.Engine
Aeterna.Engine.Tests
Aeterna.Engine.FunctionalTests
Aeterna.Godot
```

A pure C# engine soha ne hivatkozzon Godotra.

## 21.2 Preflight és execution revalidation

A `CanPlay` + `Play` minta jó alapelv:

- UI kérhet előzetes lehetőséget;
- az engine executionkor újraellenőriz;
- csak teljes validáció után mutál.

## 21.3 Szűk domain service-ek

A Dealer-szerű objektumok egy jól meghatározott feladatot végezzenek.

## 21.4 Interface-en keresztüli külső viselkedés

- random;
- package loader;
- clock;
- ID generator;
- serializer;
- projection policy;

mind injektálható interface legyen.

## 21.5 Unit + functional tesztek

Az AETERNA-nak is szüksége van:

- osztályszintű unit tesztekre;
- teljes headless match scenario tesztekre;
- deterministic fixturesre;
- failure-path tesztekre;
- Godot nélküli engine tesztekre.

# 22. Amit nem szabad átvenni

1. Godot MainNode mint teljes application service.
2. `Random.Shared` production engine-ben.
3. domain object reference-ek publikus request payloadként.
4. event payload nélküli utólagos state-read.
5. async animation után indított domain transition.
6. exception message string mint vezérlési API.
7. minden exceptiont elnyelő functional teszt.
8. presentation CardState authoritative state-ként.
9. scene-tree lookup card value equality alapján.
10. abszolút `/root/...` pathok bridge contractként.
11. stabil card instance ID nélküli TCG-modell.
12. kitöltetlen licencsablonból közvetlen kódátvétel.

# 23. Javasolt AETERNA-integrációs architektúra

```text
Aeterna.Engine
├── MatchState
├── PlayerState
├── CardInstance
├── ZoneState
├── EngineSession
├── LegalActionService
├── RequestValidator
├── TransitionService
├── EngineEvent
├── ProjectionService
└── IRandomSource

Aeterna.Engine.Tests
├── unit
├── scenario
├── determinism
├── fixture
└── replay

Aeterna.Godot
├── EngineBridge
├── SnapshotProjector
├── CardView
├── PlayerView
├── HandView
├── TableView
├── AnimationCoordinator
└── InputAdapter
```

# 24. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | A pure C# engine projekt maradjon Godot-független | Engine | P0 |
| 2 | Külön headless functional test project | Tests | P0 |
| 3 | `CanPlay`/preflight és execution revalidation fenntartása | Engine | P0 |
| 4 | `IRandomSource` minden random döntéshez | Engine | P0 |
| 5 | Seed és random event metadata | Engine | P0 |
| 6 | EngineSession a Godot MainNode helyett | Engine/Bridge | P0 |
| 7 | Immutable typed EngineResult és EngineEvent | Engine | P0 |
| 8 | State version és stale-request guard | Engine | P0 |
| 9 | CardInstanceId-alapú Godot view lookup | Bridge | P0 |
| 10 | Snapshot-alapú view reconstruction | Bridge | P1 |
| 11 | Presentation animation külön az engine transitiontől | Godot | P0 |
| 12 | Unit és functional teszt külön projektben | Tests | P1 |
| 13 | Functional tesztekben exception swallowing tiltása | Tests | P0 |
| 14 | Scenario step-limit és state hash | Tests | P1 |
| 15 | 3D CardView target transform minta adaptálása | Godot | P1 |
| 16 | MainNode felbontása coordinátorokra | Godot | P1 |
| 17 | Viewer-specific projection multiplayer előtt | Engine | P0 |
| 18 | Licenc miatt saját újraimplementálás előnyben | Projekt | P1 |

# 25. Bizonyítékjegyzék

| ID | Állítás | Forrásfájl | Sorok |
|---|---|---|---|
| E-001 | 3D C# Godot játék, 2–6 játékos | `readme.md` | 5–15 |
| E-002 | Nyitott refaktor- és teszt-TODO-k | `readme.md` | 23–36 |
| E-003 | Godot 4.3, C#, GL Compatibility | `project.godot` | 15–25 |
| E-004 | Godot .NET 8 project és gameplay reference | `Durak.Godot.csproj` | 5–30 |
| E-005 | Pure net8.0 gameplay library | `Durak.Gameplay.csproj` | 5–18 |
| E-006 | Négy külön solution project | `Durak.Godot.sln` | 10–16 |
| E-007 | Card record és konstrukciós validáció | `Cards.cs` | 7–46 |
| E-008 | Player ID, kéz és eventek | `Player.cs` | 7–36 |
| E-009 | Deck queue, shuffler és trump | `Deck.cs` | 9–40 |
| E-010 | Injektált card provider és shuffler | `Deck.cs` | 21–29 |
| E-011 | Nem seedelt Random.Shared shuffle | `DefaultCardShuffler.cs` | 7–12 |
| E-012 | Dealer első és későbbi osztás | `Dealer.cs` | 23–73 |
| E-013 | Attack state és domain eventek | `Attack.cs` | 7–35 |
| E-014 | Mutation előtti CanPlay | `Attack.cs` | 58–71 |
| E-015 | Attack End és pickup | `Attack.cs` | 74–91 |
| E-016 | CanPlay ellenőrzések | `Attack.cs` | 94–133 |
| E-017 | CanPlayResult typed eredmény | `IAttack.cs` | 24–38 |
| E-018 | TurnLogic és attack history | `TurnLogic.cs` | 9–64 |
| E-019 | Lowest trump / Random.Shared first player | `TurnLogic.cs` | 66–88 |
| E-020 | TODO2 végállapot | `TurnLogic.cs` | 135–147 |
| E-021 | Godot MainNode engine-object orchestration | `MainNode.cs` | fájl eleje és fő game flow |
| E-022 | CardNode külön Godot view | `CardNode.cs` | 12–60 |
| E-023 | CardNode animation és input | `CardNode.cs` | 63–111 |
| E-024 | CardNode state és table/discard presentation | `CardNode.cs` | 113–170 |
| E-025 | PlayerNode domain event → CardNode | `PlayerNode.cs` | 37–105 |
| E-026 | Scene-tree card lookup | `PlayerNode.cs` | 112–132 |
| E-027 | Unit test projektcsomagok | `Durak.Gameplay.UnitTests.csproj` | 7–40 |
| E-028 | Functional test projektcsomagok | `Durak.Gameplay.FunctionalTests.csproj` | 7–40 |
| E-029 | 2–6 játékos functional teszt | `IndividualGameTests.cs` | 18–35 |
| E-030 | Functional teszt exception swallowing | `IndividualGameTests.cs` | 39–48 |
| E-031 | Functional simulator és TODO3 | `GameSimulator.cs` | 23–40 |
| E-032 | Exception message alapú simulator flow | `GameSimulator.cs` | 81–99 |
| E-033 | Attack unit tesztek | `AttackTests.cs` | 9–150 |
| E-034 | MIT-szöveg kitöltetlen copyrighttal | `LICENSE.txt` | 5–17 |

# 26. Nyitott kérdések

1. A vizsgált commit buildelhető-e jelenlegi .NET 8 és Godot 4.3 környezetben?
2. Hány unit és functional teszt fut, és melyik hibás?
3. A functional teszt exception swallowing miatt vannak-e hamis PASS eredmények?
4. A `TurnLogic.NextIndex` TODO2 útvonal reprodukálható-e?
5. A GameSimulator TODO3 útvonal reprodukálható-e?
6. Az attack limit ellenőrzés off-by-one hibás-e?
7. A PlayerNode `RemoveCardFromOrder` megfelelő kulcsot töröl-e?
8. Azonos rank/suit Card recordok scene lookupja okoz-e `SingleOrDefault` hibát?
9. A MainNode async void eventkezelői okoznak-e race conditiont vagy duplázott flowt?
10. A back-to-menu cleanup exception TODO reprodukálható-e?
11. Az animation disabled/enabled mód domain szempontból azonos eredményt ad-e?
12. Milyen licence van minden kártya- és 3D assetnek?
13. A kitöltetlen MIT copyright sor jogilag hogyan kezelendő?
14. A projekt exportálható-e Windowsra hibamentesen?
15. Mely Godot 3D presentation részek implementálhatók újra AETERNA-specifikusan?

# 27. Következő vizsgálati lépések

## Codex nélkül elvégezhető

1. Helyi origin és commit SHA rögzítése.
2. `dotnet restore`.
3. `dotnet build Durak.Godot.sln`.
4. `dotnet test`.
5. Functional test exception swallowing ideiglenes javítása külön munkamásolatban.
6. Többszöri seedelt headless futás saját test shufflerrel.
7. TODO2 és TODO3 reprodukció.
8. Attack limit boundary teszt.
9. Player order teszt.
10. Godot 4.3 import és visual smoke.
11. Animation enabled/disabled parity.
12. Asset- és licencaudit.

## Később Codexszel gyorsítható

1. teljes call graph;
2. MainNode felelősségi bontás;
3. scene–script gráf;
4. event subscription lifecycle audit;
5. race és async-void vizsgálat;
6. tesztlefedettség;
7. mutation path audit;
8. deterministic RNG refaktorjavaslat;
9. AETERNA EngineSession bridge összevetés;
10. CardInstanceId-alapú view adapter proof.

# 28. Végső előzetes minősítés

- **Technológiai illeszkedés:** nagyon magas
- **Engine–Godot elválasztási érték:** magas
- **Rules-engine érték:** magasabb az előző két Godot/C# projektnél
- **Godot presentation érték:** magas
- **Tesztelési érték:** magas, de a functional teszt kritikus korrekciót igényel
- **Determinizmus:** gyenge
- **Multiplayer érték:** nincs
- **Production engine-alapként:** közvetlenül nem
- **Szerkezeti inspirációként:** igen
- **Kódátvétel:** licenc- és assettisztázás után is inkább szelektív; saját újraimplementálás ajánlott
- **Mélyelemzés folytatása:** igen
- **Elsődleges következő cél:** helyi build, tesztfuttatás és determinisztikus functional audit

# 29. Változásnapló

## 0.1 – 2026-07-24

- elkészült a repository-forrásokra épülő első teljes elemzés;
- rögzítésre került a négyprojekt-es solution;
- elkülönítésre került a Godot kliens és a pure C# gameplay library;
- vizsgálat készült a Card, Player, Deck, Dealer, Attack és TurnLogic rétegről;
- feldolgozásra kerültek a Godot CardNode, PlayerNode és MainNode minták;
- rögzítésre kerültek a unit és functional tesztstruktúrák;
- azonosításra került a functional teszt exception swallowing kockázata;
- rögzítésre kerültek a nem seedelt RNG és replay hiányosságai;
- elkészült az AETERNA számára használható és kerülendő minták listája.

## Stabil katalógushivatkozás – 2026-07-24

- a kapcsolódó katalógus logikai dokumentumszerepe az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum;
- a katalógus új verziója miatt ezt az elemzést a jövőben nem kell módosítani;
- a vizsgált repository-állapotot továbbra is az elemzés saját commit SHA-ja rögzíti.

## Hivatkozási modell javítása – 2026-07-24

- a kapcsolódó katalógus hivatkozása mostantól: az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum;
- az elemzés nem tartalmaz konkrét katalógusfájlnevet vagy katalógusverziót;
- új központi katalógusverzió miatt ezt a projektdokumentumot nem kell módosítani;
- a projekt vizsgált állapotának reprodukálhatóságát továbbra is a saját branch/tag,
  commit SHA és vizsgálati dátum biztosítja;
- a korábbi verziótlan központi fájlmodell felváltásra került.
