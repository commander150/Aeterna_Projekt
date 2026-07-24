# AETERNA – TheSchlote/Godot-4-Card-Game-CSharp ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.3
- **Dátum:** 2026-07-23
- **Státusz:** előzetes, repository-forrásokra épülő elemzés
- **Fő elemzési fájl:** `learning/analyses/theschlote__godot-4-card-game-csharp.md`
- **Későbbi részanyagok:** `learning/analyses/theschlote__godot-4-card-game-csharp/`
- **Vizsgált branch:** `main`
- **Vizsgált commit:** `bcea587d3d6536fbc19094445a0a1f84804a5f96`
- **Commit üzenete:** `Final Part done! of season 1`
- **Vizsgálati korlát:** helyi build, Godot-import és demófuttatás ebben a körben nem történt
- **Repository jelenlegi állapota:** archivált
- **Licencstátusz:** egyértelmű repository-licencet nem találtunk; kódátvétel nem engedélyezhető tisztázás nélkül
- **Besorolás:** Godot/C# egyjátékos deckbuilder/card-battle oktatási projekt

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Repository | `TheSchlote/Godot-4-Card-Game-CSharp` |
| URL | https://github.com/TheSchlote/Godot-4-Card-Game-CSharp |
| Vizsgált commit | `bcea587d3d6536fbc19094445a0a1f84804a5f96` |
| Alap | egy GDScript-oktatósorozat C#-os átültetése |
| Motor | Godot 4.2.1 .NET |
| Alap target | .NET 6 |
| Android target | .NET 7 |
| iOS target | .NET 8 |
| Nyelv | C# |
| Projekt típusa | egyjátékos, Slay the Spire-jellegű card battle |
| Multiplayer | nincs |
| Automatizált teszt | nem találtunk |
| CI | nem találtunk |
| Licenc | nem azonosított |
| AETERNA-prioritás | P0 UI/state-machine mintának; P2 rules-engine mintának |

A README saját architektúraábrája a `Battle`, `PlayerHandler`, `EnemyHandler`, `Player`
és UI rétegeket különíti el. A kártyákat, paklikat, effecteket, statokat és enemy intentet
Godot Resource-okkal és C# osztályokkal modellezi.

# 2. Vezetői összefoglaló

A projekt az elsőként elemzett `Godot-CardPileFramework` projektnél teljesebb játékciklust
mutat:

- játékos- és ellenfélkör;
- húzó-, dobó- és kezdőpakli;
- mana;
- HP és block;
- több célzási mód;
- drag, aiming és release alapú Card UI state machine;
- ellenfél-intentek;
- feltételes és súlyozott ellenfélakciók;
- győzelem és vereség;
- hangeffektek és animációk.

A legnagyobb értéke az AETERNA számára:

1. **Card UI állapotgép** – Base, Clicked, Dragging, Aiming és Released állapotok.
2. **Külön Card Resource és CardUI node** – jobb szétválasztás, mint az első frameworkben.
3. **Resource-alapú pakli és karakterstatisztika**.
4. **Effect-osztályok** – DamageEffect és BlockEffect közös interfésszel.
5. **Enemy intent és akcióválasztás** – feltételes akciók elsőbbsége, majd súlyozott választás.
6. **Globális eseményközpont** – a jelenetek lazább összekapcsolására.

A legfontosabb korlát:

> A játékszabály, az authoritative állapot, a Godot scene-fa, az animáció és az input
> továbbra is szorosan össze van kötve.

A kártya lejátszása közvetlenül:

- globális Godot signalt küld;
- levonja a manát;
- scene node-okból választ célokat;
- Player vagy Enemy node-okat módosít;
- végül törli a CardUI node-ot.

Ez egy jó egyjátékos oktatási játékmodell, de nem alkalmas az AETERNA determinisztikus,
UI-tól független production engine-jének alapjául.

# 3. Előzetes értékelés

| Szempont | Pontszám | Indok |
|---|:---:|---|
| Godot/C# technológiai illeszkedés | 5/5 | Godot 4.2.1 .NET és C# |
| Card UI tanulási érték | 5/5 | külön state machine és célzási réteg |
| Egyjátékos card-battle architektúra | 4/5 | teljes alap harci ciklus |
| TCG/CCG rules-engine érték | 2/5 | nincs authoritative, UI-független domain |
| Effect-rendszer | 3/5 | tiszta alaposztály, de scene-node célok |
| AI/ellenfél-intent | 3/5 | feltételes és súlyozott akciók |
| Determinizmus | 1/5 | `Random` és `GD.RandRange`, explicit seed nélkül |
| Tesztelhetőség | 1/5 | Godot API-hoz és scene-fához kötött |
| Multiplayer | 0/5 | nincs |
| Dokumentáltság | 3/5 | README-ábrák, de részletes technikai dokumentáció nincs |
| Karbantarthatóság | 2/5 | oktatási kód, több erős globális függőség |
| Licencelési felhasználhatóság | 0/5 | egyértelmű licenc nem található |
| Összesített besorolás | **P0/P2** | P0 UI-minta, P2 rules-engine minta |

# 4. Repository- és modulstruktúra

```text
Game/
├── CardGame.csproj
├── project.godot
├── Effects/
│   ├── DamageEffect.cs
│   └── BlockEffect.cs
├── custom_resources/
│   ├── Card.cs
│   ├── CardPile.cs
│   ├── Effect.cs
│   ├── Stats.cs
│   ├── CharacterStats.cs
│   ├── EnemyStats.cs
│   └── Intent.cs
├── characters/Warrior/
│   ├── Warrior.tres
│   ├── WarriorStartingDeck.tres
│   └── Cards/
│       ├── WarriorAxeAttack.cs
│       ├── WarriorBlock.cs
│       ├── WarriorSlash.cs
│       └── *.tres
├── enemies/
│   ├── bat/
│   └── crab/
├── global/
│   ├── Events.cs
│   ├── Shaker.cs
│   └── SoundPlayer.cs
└── scenes/
    ├── battle/
    ├── Player/
    ├── Enemy/
    ├── card_ui/
    ├── card_target_selector/
    └── ui/
```

## 4.1 Fő komponensek

| Komponens | Felelősség | AETERNA-megfelelő |
|---|---|---|
| `Card` | Resource definition, cost, target, effect indítása | részben CardDefinition, de nem production contract |
| `CardPile` | rendezett Card Resource tömb | prototípus zone/deck |
| `Stats` | HP, block és sebzés | combat state prototípus |
| `CharacterStats` | mana, deck, draw és discard | player combat state prototípus |
| `Effect` | effect alaposztály | effect dispatch prototípus |
| `Battle` | harc indítása és turn-signalok összekötése | match presentation coordinator |
| `PlayerHandler` | játékoskör, húzás és discard | turn controller prototípus |
| `EnemyHandler` | ellenfelek soros végrehajtása | enemy presentation scheduler |
| `EnemyActionPicker` | conditional/chance-based választás | AI intent prototípus |
| `CardUI` | kártyamegjelenítés, célok és Play | CardView + input adapter összekeverve |
| `CardStateMachine` | Card UI lifecycle | közvetlenül hasznos UI minta |
| `CardTargetSelector` | egér-alapú vizuális célzás | TargetingView |

# 5. Kártyamodell

## 5.1 `Card` Resource

A `Card` mezői:

- `Id`;
- `CardType`: Attack, Skill, Power;
- `TargetType`: Self, SingleEnemy, AllEnemies, Everyone;
- `Cost`;
- `Icon`;
- `ToolTipText`;
- `Sound`.

Ez jobb, mint a név-alapú prototípus-adat, mert van explicit `Id` és enumos kártya-,
valamint célzási típus.

## 5.2 Card definition és runtime instance

A Resource azonban egyszerre:

- kártyadefiníció;
- paklielem;
- lejátszott kártya;
- effect-dispatch objektum.

A `CardPile` közvetlenül `Card[]` tömböt tárol. Húzáskor ugyanaz a Resource referencia
kerül ki a pakliból és a CardUI-hoz. Nincs külön runtime instance:

- instance ID;
- owner;
- controller;
- zone;
- state;
- modifier;
- visibility;
- version.

Az AETERNA továbbra is tartsa külön:

```text
RuntimeCardDefinition
CardInstance
PlayerProjection
CardViewModel
CardView
```

## 5.3 Kártyánkénti C# osztály

A konkrét lapok külön `Card`-leszármazottak. Például a WarriorAxeAttack létrehoz egy
DamageEffectet, 6 sebzéssel.

A `.tres` Resource tárolja:

- scriptet;
- ID-t;
- típust;
- célt;
- költséget;
- ikont;
- tooltipet;
- hangot.

### Előny

- egyszerűen érthető;
- C# fordítási ellenőrzést kap;
- komplex egyedi viselkedés könnyen írható;
- Godot Inspectorból konfigurálható.

### Hátrány

- minden új laphoz C# osztály kellhet;
- a content és executable code szorosan kapcsolódik;
- nagy TCG-adatbázisnál nehezen auditálható;
- nincs schema-validált, engine-független ability contract;
- hot data update nehéz;
- replay és determinisztika szempontjából gyenge.

**AETERNA-javaslat:** az általános effectek legyenek adatvezéreltek; külön C# override csak
ellenőrzött, ritka engine-kivételhez használható.

# 6. Card UI state machine

## 6.1 Állapotok

A `CardStateMachine` gyermeknode-okból regisztrálja az állapotokat, és
`TransitionRequested` signal alapján vált.

A state-ek:

- Base;
- Clicked;
- Dragging;
- Aiming;
- Released.

Ez a projekt legerősebb, közvetlenül tanulmányozható mintája.

## 6.2 Base state

A Base state:

- visszaállítja a vizuális stílust;
- visszakéri a kártyát a Hand szülőhöz;
- kezeli a kattintást;
- hover esetén tooltipet kér;
- figyelembe veszi a `Playable` és `Disabled` jelzőket.

## 6.3 Dragging state

A Dragging state:

- UI layerbe reparenteli a kártyát;
- drag stílust állít;
- globális drag-start/end signalokat küld;
- minimum drag időt használ;
- kezeli a cancel és confirm inputot;
- egycélú lapnál Aiming állapotba vált.

## 6.4 Aiming state

Az Aiming state:

- kiüríti a célhalmazt;
- a kéz fölé animálja a kártyát;
- letiltja a kártya saját drop detectorát;
- globális aim-start/end signalokat küld;
- jobb kattintással vagy alsó egérpozíciónál visszalép;
- bal gombbal megerősít.

## 6.5 Released state

A Released state akkor játssza ki a lapot, ha a `Targets` nem üres. Ezután a CardUI
meghívja a `Card.Play` metódust és törli önmagát.

### AETERNA számára átvehető

- a vizuális állapotgép;
- explicit cancel/confirm;
- drag és aim különválasztása;
- más kártyák letiltása aktív interakció alatt;
- reparent a felső UI layerbe;
- snapshot után visszaállítható Base state.

### Nem átvehető

- a Released state közvetlenül ne hajtsa végre a szabályt;
- a CardUI `Targets` ne legyen authoritative target selection;
- a CardUI ne vonjon le erőforrást;
- a CardUI ne törlődjön engine-visszaigazolás előtt.

Javasolt AETERNA-folyamat:

```text
Base
→ Dragging / Aiming
→ selection intent
→ engine request
→ pending UI
→ accepted: snapshot + animation
→ rejected: Base + authoritative refresh
```

# 7. Célzási rendszer

A `CardTargetSelector`:

- CardAimStarted/Ended signalokra reagál;
- a kurzorhoz mozgat egy Area2D-t;
- ívelt Line2D célzóvonalat rajzol;
- collision alapján ad és vesz el célokat a CardUI `Targets` listájából.

Vizuálisan erős és közvetlenül adaptálható.

Rules szempontból azonban a collision nem bizonyítja a cél jogszerűségét. Production
rendszerben a célként megjelenő node-ok engine által kiadott, stabil target ID-hoz
kapcsolódjanak.

# 8. Pakli- és zónakezelés

## 8.1 `CardPile`

A CardPile:

- `Card[]` Resource tömböt tart;
- az első elemet húzza;
- a végére ad hozzá;
- saját méretváltozás-signalt küld;
- Fisher–Yates jellegű shuffle-t használ;
- minden shuffle alkalmával új `System.Random` példányt hoz létre.

## 8.2 Problémák production engine esetén

- nincs explicit RNG seed;
- nincs RNG abstraction;
- nincs random event;
- nincs replay;
- azonos időben létrehozott Random példányok korrelációja vizsgálandó;
- a Card Resource nem card instance;
- nincs zone transition event;
- nincs hidden information;
- nincs immutable definition/runtime instance különválasztás.

## 8.3 PlayerHandler

A PlayerHandler:

1. duplikálja a kezdőpaklit;
2. keveri a DrawPile-t;
3. új Discard pile-t hoz létre;
4. kör elején nullázza a Blockot;
5. visszatölti a manát;
6. tweenekkel húz;
7. kör végén tweenekkel discardolja a teljes kezet;
8. üres DrawPile esetén a Discardot visszakeveri.

Ez jó UX sequencing minta, de a rules transition az animációs tweenek időzítéséhez kötődik.

## 8.4 Üres pakli kockázata

A `CardPile.DrawCard` exceptiont dob üres paklinál. A `PlayerHandler.DrawCard` egyszer
visszakeverés előtt és egyszer húzás után ellenőriz, de ha Draw és Discard is üres,
a húzás továbbra is exceptiont okozhat.

Ez helyi futtatással igazolandó, de a forrás alapján valós hibakockázat.

# 9. Erőforrás és kártyakijátszás

A `CharacterStats.CanPlayCard` kizárólag azt ellenőrzi, hogy:

```text
Mana >= Card.Cost
```

A CardUI ezt használja a vizuális `Playable` állapothoz.

A `Card.Play`:

1. `CardPlayed` signalt küld;
2. levonja a manát;
3. célokat választ;
4. effectet hajt végre.

Hiányzik:

- turn/phase ellenőrzés;
- ownership/control;
- hand membership;
- card instance validáció;
- target count;
- target identity;
- legal target;
- exact request contract;
- state version;
- atomicity;
- rollback;
- duplicate request protection;
- event sequence.

**AETERNA-következtetés:** a `Playable` csak vizuális hint legyen. Minden requestet az
engine-nek kell újraellenőriznie.

# 10. Effect-rendszer

Az `Effect` egy `RefCounted` alaposztály, `Execute(Array<Node> targets)` metódussal.

Megvalósított általános effectek:

- `DamageEffect`;
- `BlockEffect`.

A konkrét kártya ezekből példányosít és Amountot állít.

### Erősség

- a kártya és az általános effect részben különválik;
- egy effect több lapon használható;
- egyszerű kompozíció kialakítható;
- a card class rövid marad.

### Korlát

Az effect targetje Godot `Node`. A DamageEffect és BlockEffect runtime type alapján
külön kezeli a `Player` és `Enemy` scene node-okat, majd közvetlenül módosítja statjaikat.

Ez összeköti:

- rules logikát;
- scene node típust;
- hangot;
- animációt;
- combat state-et.

A production engine effectje stabil entity/card/player ID-val, pure state transitionnel és
külön presentation eventtel működjön.

# 11. Játékos- és ellenfélállapot

## 11.1 Stats Resource

A Stats:

- MaxHealth;
- Health;
- Block;
- Art;
- StatsChanged signal;
- sebzés és gyógyítás.

A `CreateInstance` duplikálja a Resource-t, feltölti a HP-t és nullázza a Blockot.

Ez jó prototípus arra, hogyan különíthető el a Godotban szerkesztett alap Resource és a
futásidejű másolat.

Production engine-ben ugyanakkor a state ne Godot Resource legyen.

## 11.2 Player

A Player node:

- Stats Resource-t tart;
- signal alapján frissíti a UI-t;
- sebzéskor animációt és shake-et futtat;
- a tényleges `Stats.TakeDamage` hívást tween callbackbe teszi;
- halálkor signalt küld és törli magát.

A szabályállapot változása így animációs időponthoz kötött.

## 11.3 Enemy

Az Enemy node:

- saját Stats instance-t hoz létre;
- AI scene-t példányosít;
- intentet jelenít meg;
- actiont választ;
- sebzésnél animáció közben módosítja a statot;
- halálkor törli a node-ot.

Ez használható presentation patternként, de production engine-ben a halál és sebzés
előbb authoritative transition legyen, az animáció csak kövesse.

# 12. Kör- és eseményvezérlés

## 12.1 Battle

A Battle node globális signalokkal kapcsolja össze:

- játékoskör végét;
- kéz discard végét;
- ellenfélkör végét;
- player death;
- enemy child count változását.

A turn flow lényegében:

```text
StartBattle
→ PlayerHandler.StartTurn
→ PlayerTurnEnded
→ PlayerHandler.EndTurn
→ PlayerHandDiscarded
→ EnemyHandler.StartTurn
→ EnemyActionCompleted...
→ EnemyTurnEnded
→ PlayerHandler.StartTurn
```

Ez áttekinthető oktatási flow.

## 12.2 EnemyHandler

Az EnemyHandler a scene child sorrendjében hajtja végre az ellenfeleket. Az action
befejezése után a következő child kap kört.

Ez determinisztikus lehetne, ha a child sorrend és az akciók determinisztikusak lennének,
de az akcióválasztás random.

## 12.3 Globális Events singleton

Az Events autoload lazítja a közvetlen node-hivatkozásokat, de:

- globális mutable dependency;
- nincs event sequence;
- nincs payload-verzió;
- nincs replay;
- nincs viewer filtering;
- nincs event log;
- stringes signalnevek vegyesen szerepelnek a typed `nameof` használattal.

# 13. Eseményszerződés-eltérések

A forrásban több deklaráció és tényleges használat nem egyezik.

## 13.1 Tooltip

Az Events ezt deklarálja:

```text
CardTooltipRequested(Card card)
```

A Base state viszont két argumentumot küld:

```text
Icon, ToolTipText
```

A Tooltip fogadó metódusa szintén két paramétert vár:

```text
ShowTooltip(Texture icon, string text)
```

## 13.2 EnemyActionCompleted

Az Events delegate nem deklarál argumentumot, miközben az enemy actionök `Enemy` node-ot
küldenek, és az EnemyHandler `OnEnemyActionCompleted(Enemy enemy)` metódust vár.

## 13.3 BattleOverScreenRequested

Az Events delegate nem deklarál argumentumot, miközben a Battle szöveget és screen type-ot
küld, a BattleOverPanel pedig két argumentumot vár.

### Minősítés

Ez **forrásszintű signal contract eltérés**. Helyi build és futtatás nélkül nem állítjuk,
hogy minden útvonal biztosan hibát okoz, de kiemelt blocker-közeli ellenőrzési pont.

AETERNA-ban az engine event contractok:

- typed modellek legyenek;
- legyen payload schema;
- legyen stabil event type;
- legyen sequence és state version;
- a Godot signal csak adapter legyen.

# 14. Ellenfél-intent és AI

## 14.1 EnemyAction

Az actionök:

- Conditional vagy ChanceBased típusúak;
- Intent Resource-t tartanak;
- hangot;
- chance weightet;
- Enemy és Target node-hivatkozást.

## 14.2 EnemyActionPicker

A picker:

1. először az első végrehajtható conditional actiont választja;
2. ha nincs, súlyozott random chance-based actiont választ;
3. a conditional prioritást a scene child sorrendje adja;
4. a célpontot a `"Player"` node groupból keresi.

### Tanulási érték

- az intent előre megjeleníthető;
- conditional action felülírhatja a random választást;
- a chance weight szerkeszthető;
- az AI scene-ben kompozícióként építhető fel.

### Korlát

- `GD.RandRange` explicit seed nélkül;
- nincs decision event;
- nincs AI state snapshot;
- nincs action reason;
- child order implicit priority;
- scene node hivatkozások;
- action és animáció egy osztályban;
- enemy completion az animáció végétől függ.

AETERNA számára egy későbbi AI/teszt rendszerben hasznosabb:

```text
EnemyDecisionInput
→ deterministic policy / seeded RNG
→ EnemyDecision
→ engine validation
→ state transition
→ presentation intent
```

# 15. Determinizmus és replay

Nem találtunk:

- seed contractot;
- RNG service-t;
- random eventet;
- state hash-t;
- replay logot;
- fixture-t;
- snapshot serializációt;
- action request ID-t.

Random források:

- `new System.Random()` a CardPile shuffle-ben;
- `GD.RandRange` az enemy action pickerben.

Az animációs tween callbackekben történő state mutation tovább nehezíti a reprodukálást.

# 16. Tesztek, CI és build

A teljes, korai commit és a vizsgált HEAD közötti file listában nem találtunk:

- külön test projektet;
- xUnit/NUnit/MSTest fájlokat;
- `.github/workflows` mappát;
- CI konfigurációt;
- benchmarkot;
- headless test harness-t.

A projektfájl:

- `Godot.NET.Sdk/4.2.1`;
- alap `net6.0`;
- Android `net7.0`;
- iOS `net8.0`.

A repository jelenleg archivált. A helyi build külön szükséges, mert az eltérő target
frameworkek és a régi Godot 4.2.1 környezet kompatibilitási problémát okozhatnak.

# 17. Licenc és felhasználhatóság

A repository teljes file listájában nem találtunk LICENSE fájlt, és a szokásos
`LICENSE` valamint `LICENSE.md` útvonalak sem érhetők el.

Ezért:

- **kódrészlet közvetlen átvétele:** nem engedélyezett tisztázás nélkül;
- **repository dependencyként használata:** nem ajánlott;
- **architekturális tanulás:** igen;
- **viselkedési minta saját újraimplementálása:** igen, önálló kóddal;
- **assetek használata:** nem engedélyezett külön licencvizsgálat nélkül.

A tutorial eredeti forrásának és assetcsomagjainak licenceit is külön kellene vizsgálni.

# 18. Erősségek

1. Áttekinthető README-architektúra.
2. Godot/C# Card Resource és CardUI különválasztás.
3. Jól strukturált Card UI state machine.
4. Külön Dragging és Aiming állapot.
5. Vizuálisan használható célzóív.
6. Resource-alapú CardPile és CharacterStats.
7. Általános DamageEffect és BlockEffect.
8. Egyértelmű player/enemy handler réteg.
9. Enemy intent és súlyozott akcióválasztás.
10. Teljes alap battle loop.
11. Script template-ek új card/effect/enemy action készítéséhez.
12. Kis méret, oktatási célra áttekinthető.

# 19. Gyengeségek és kockázatok

1. Nincs authoritative, Godot-független game state.
2. A Card Resource egyben definition és paklielem.
3. Nincs stabil card instance ID.
4. A Card.Play közvetlenül levonja a manát.
5. A CardUI közvetlenül hívja a Card.Play metódust.
6. Targetek Godot node-ok.
7. Céljogszerűség collision-alapú.
8. Effectek Player/Enemy node típusokra kapcsolódnak.
9. State mutation tween callbackekben történik.
10. Globális Events singleton erős rejtett függőség.
11. Több signal payload eltér a deklarációtól.
12. Nincs explicit RNG seed.
13. Nincs replay.
14. Nincs testprojekt.
15. Nincs CI.
16. Üres draw/discard esetén draw exception kockázat.
17. Kártyánkénti C# osztály nagy adatbázisnál nehezen skálázódik.
18. A repository archivált.
19. Egyértelmű licenc nem található.
20. Az assetjogok nincsenek dokumentálva.

# 20. AETERNA számára átvehető elvek

## 20.1 Card UI state machine

Közvetlenül hasznos koncepció:

- Base;
- Pressed/Clicked;
- Dragging;
- Aiming;
- Pending;
- Accepted/Rejected;
- Returning.

Az AETERNA-változatba kerüljön külön Pending állapot az engine válaszáig.

## 20.2 Vizuális célzási réteg

A célzóív, kurzorkövető Area2D és kiemelés jó UX-minta, de a lehetséges célokat az engine
adja ID-listaként.

## 20.3 Card Resource mint visual authoring asset

Godot Resource használható:

- ikonhoz;
- tooltip layouthez;
- hanghoz;
- animációprofilhoz;
- frame style-hoz.

A Cost, Target és Effect authoritative forrása azonban az engine runtime package maradjon.

## 20.4 Effect-kompozíció

A DamageEffect/BlockEffect szerű általános effectek hasznosak, ha:

- Godot Node helyett engine target ID-t kapnak;
- pure transitiont hoznak létre;
- nem játszanak le hangot;
- presentation event külön készül.

## 20.5 Enemy intent

Az intent preview jó játékosi UX:

- akciótípus;
- várható érték;
- cél;
- bizonytalanság;
- ikon.

Ez az AETERNA későbbi AI/PvE rétegében használható lehet.

# 21. Amit nem szabad átvenni

1. UI node-ból indított authoritative Card.Play.
2. Mana közvetlen levonása Card Resource-ban.
3. Godot Node targetek a rules layerben.
4. Collision mint legal-target igazság.
5. Tweenhez kötött state transition.
6. Globális signalbusz engine event log helyett.
7. `new Random()` és `GD.RandRange` production RNG-ként.
8. Resource referencia card instance-ként.
9. Kártyánként kötelező C# osztály.
10. Licenc nélküli kód közvetlen átvétele.

# 22. Javasolt AETERNA-integrációs minta

```text
Aeterna.Engine
    MatchState
    CardInstance
    LegalAction
    SelectionContract
    RequestResult
    EngineEvent
    PlayerSnapshot
          │
          ▼
Godot Bridge
    CardViewModel
    TargetViewModel
    InteractionSession
    PendingRequest
          │
          ▼
Godot UI
    CardStateMachine
    CardView
    HandView
    TargetingArc
    IntentView
    AnimationCoordinator
```

# 23. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | CardView state machine saját újraimplementálása | Godot | P1 |
| 2 | `PendingEngineResponse` állapot hozzáadása | Godot Bridge | P0 |
| 3 | Engine által kiadott target ID-lista vizuális leképezése | Bridge | P0 |
| 4 | Ívelt targeting line és target highlight | Godot | P1 |
| 5 | Resource-alapú visual metadata | Godot | P1 |
| 6 | Effect és presentation event szétválasztása | Engine | P0 |
| 7 | Typed signal adapter a Godot oldalon | Bridge | P0 |
| 8 | Signal payload contract tesztek | Tests | P1 |
| 9 | Seedelt RNG az AI és shuffle számára | Engine | P0 |
| 10 | Enemy intent projection kialakítása későbbi PvE-hez | Engine/Godot | P2 |
| 11 | Draw exhaustion explicit szabály és teszt | Engine | P1 |
| 12 | Kódátvétel helyett saját implementáció a licenc hiánya miatt | Projekt | P0 |

# 24. Bizonyítékjegyzék

| ID | Állítás | Forrásfájl | Sorok |
|---|---|---|---|
| E-001 | Tutorial C# átültetés | `README.md` | 5–6 |
| E-002 | Magas szintű architektúra | `README.md` | 8–28 |
| E-003 | Resource adatmodell | `README.md` | 30–52 |
| E-004 | Godot 4.2.1 és target frameworkök | `Game/CardGame.csproj` | 3–8 |
| E-005 | Godot 4.2 és autoloadok | `Game/project.godot` | 13–25 |
| E-006 | Card mezők és target enumok | `custom_resources/Card.cs` | 7–29 |
| E-007 | Scene group alapú célválasztás | `custom_resources/Card.cs` | 31–65 |
| E-008 | Card.Play mana és effect | `custom_resources/Card.cs` | 66–83 |
| E-009 | CardPile Resource és draw | `custom_resources/CardPile.cs` | 8–35 |
| E-010 | Nem seedelt shuffle | `custom_resources/CardPile.cs` | 44–54 |
| E-011 | Stats sebzésmodell | `custom_resources/Stats.cs` | 32–60 |
| E-012 | Character mana és pile-ok | `CharacterStats.cs` | 7–38 |
| E-013 | CanPlayCard csak mana | `CharacterStats.cs` | 48–51 |
| E-014 | Runtime Resource-példányok | `CharacterStats.cs` | 53–62 |
| E-015 | Battle signal-orchestration | `Battle.cs` | 20–49 |
| E-016 | Win/lose signalok | `Battle.cs` | 51–68 |
| E-017 | Player draw/discard tween flow | `PlayerHandler.cs` | 21–79 |
| E-018 | Discard visszakeverése | `PlayerHandler.cs` | 81–92 |
| E-019 | Enemy sorrendi végrehajtás | `EnemyHandler.cs` | 22–43 |
| E-020 | CardUI state és target lista | `CardUI.cs` | 6–45 |
| E-021 | CardUI közvetlen Play | `CardUI.cs` | 75–79 |
| E-022 | Mana-alapú Playable UI | `CardUI.cs` | 143–161 |
| E-023 | State machine registry | `CardStateMachine.cs` | 6–30 |
| E-024 | State transition guard | `CardStateMachine.cs` | 64–75 |
| E-025 | Drag lifecycle | `CardDraggingState.cs` | 5–58 |
| E-026 | Aim lifecycle | `CardAimingState.cs` | 6–39 |
| E-027 | Released közvetlen play | `CardReleasedState.cs` | 5–28 |
| E-028 | Targeting arc és collision | `CardTargetSelector.cs` | 6–92 |
| E-029 | Hand CardUI példányosítás | `Hand.cs` | 5–20 |
| E-030 | Effect alaposztály | `Effect.cs` | 6–12 |
| E-031 | Damage scene-node dispatch | `DamageEffect.cs` | 6–29 |
| E-032 | Block scene-node dispatch | `BlockEffect.cs` | 6–28 |
| E-033 | Kártyánkénti C# subclass | `WarriorAxeAttack.cs` | 7–17 |
| E-034 | Card `.tres` metadata | `warrior_axe_attack.tres` | 3–17 |
| E-035 | Enemy action type és weight | `EnemyAction.cs` | 6–28 |
| E-036 | Conditional majd weighted random AI | `EnemyActionPicker.cs` | 32–89 |
| E-037 | Player state mutation tweenben | `Player.cs` | 54–75 |
| E-038 | Enemy state és AI scene | `Enemy.cs` | 48–115 |
| E-039 | Enemy damage tweenben | `Enemy.cs` | 116–136 |
| E-040 | Events signal deklarációk | `global/Events.cs` | 6–49 |
| E-041 | Tooltip kétparaméteres fogadó | `Tooltip.cs` | 21–38 |
| E-042 | BattleOver kétparaméteres fogadó | `BattleOverPanel.cs` | 18–45 |

# 25. Nyitott kérdések

1. Buildelhető-e a projekt a rögzített Godot 4.2.1/.NET környezettel?
2. A signal payload eltérések build- vagy runtime hibát okoznak-e?
3. Az összes kártyatípus játszható-e?
4. Mi történik teljesen üres Draw és Discard pile esetén?
5. Az EnemyActionPicker totalWeight 0 állapotot hogyan kezeli?
6. Van-e action, amely nem küld EnemyActionCompleted signalt?
7. A tweenek pause vagy scene reload esetén hagynak-e félállapotot?
8. A Resource duplikálás deep/shallow viselkedése minden paklinál megfelelő-e?
9. A kártya Resource referenciák megosztása okozhat-e közös mutable state-et?
10. Az assetek és a tutorial forrásának licence mi?
11. A repository tulajdonosa ad-e külön engedélyt kódrészlet használatára?
12. Mely UI mintákat érdemes teljesen saját kóddal újraimplementálni?

# 26. Következő vizsgálati lépések

## Codex nélkül elvégezhető

1. Repository letöltése `learning/sources/` alá.
2. Origin és commit rögzítése.
3. Godot 4.2.1 .NET vagy kompatibilis verzió telepítési auditja.
4. Debug build.
5. Card play, targeting, cancel és turn smoke.
6. Signal payload eltérések reprodukálása.
7. Üres pakli teszt.
8. RNG viselkedés vizsgálata.
9. Asset- és tutoriallicenc kutatása.
10. UI state machine AETERNA-specifikus újratervezése.

## Később Codexszel gyorsítható

1. teljes call graph;
2. signal connect/emit szerződések automatikus összevetése;
3. nullability és lifecycle audit;
4. tweenhez kötött mutationök listázása;
5. Godot scene–script gráf;
6. minimális headless tesztharness javaslat;
7. AETERNA UI adapter proof-of-concept implementáció.

# 27. Végső előzetes minősítés

- **Tanulási érték:** magas Card UI és egyjátékos card-battle UX terén
- **Rules-engine érték:** alacsony–közepes
- **Godot/C# illeszkedés:** közvetlen
- **Production engine-alapként:** nem alkalmas
- **Kódátvétel:** licenc tisztázásáig nem
- **Saját újraimplementálás:** ajánlott
- **Mélyelemzés folytatása:** igen, helyi builddel
- **Elsődleges AETERNA-tanulság:** UI state machine és targeting UX, szigorú engine-határ mögött

# 28. Változásnapló

## Katalógushivatkozás-korrekció – 2026-07-24

- a kapcsolódó katalógus útvonala `learning/LEARNING_CATALOG.md` értékre frissült;
- a korábbi üres, verziótlan katalógusfájlra való hivatkozás megszűnt.


## 0.1 – 2026-07-23

- elkészült a repository-forrásokra épülő első elemzés;
- megtörtént a Card, CardPile, Stats, Effect és handler rétegek vizsgálata;
- feldolgozásra került a Card UI state machine és targeting rendszer;
- külön elemzés készült az enemy intent és action picker mintáról;
- rögzítésre kerültek a signal contract eltérések;
- rögzítésre került a determinizmus, tesztelés és licenc hiánya;
- elkészült az AETERNA-integrációs és saját újraimplementálási javaslatlista.

## Stabil katalógushivatkozás – 2026-07-24

- a kapcsolódó katalógus stabil útvonala `learning/LEARNING_CATALOG.md`;
- a katalógus új verziója miatt ezt az elemzést a jövőben nem kell módosítani;
- a vizsgált repository-állapotot továbbra is az elemzés saját commit SHA-ja rögzíti.
