# AETERNA – 0.0.1 MÉRFÖLDKŐ ÉS CÉLÁLLAPOT

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1
**Dátum:** 2026-09-05
**Státusz:** aktív irányadó cél- és mérföldkő-dokumentum
**Termékverzió-cél:** AETERNA digitális tesztprogram 0.0.1
**Elsődleges szerep:** hosszú távú termékcél és az első zárt tesztkiadás célállapotának rögzítése
**Current repository-bázis:** `0862e1002dbef81ee203852714d377592272a0e9`

A jelen dokumentum az AETERNA digitális programegységének első **zárt, használható termékjellegű tesztkiadását** határozza meg.

A dokumentumban szereplő `0.0.1` nem a jelenlegi technikai prototípusok, engine-checkpointok vagy contract-verziók folytatása, hanem a későbbi program első zárt, használható tesztkiadásának tervezett termékverziója.

A jelen dokumentum:

- nem írja felül az AETERNA korábban meghatározott projektcéljait;
- nem módosítja a hivatalos szabályforrásokat;
- nem helyettesíti az aktuális projekttervet és prioritási dokumentumokat;
- nem technikai implementációs specifikáció;
- nem jelenti azt, hogy minden itt felsorolt funkció azonnal fejlesztendő;
- nem teszi a teljes 0.0.1 scope-ot automatikusan VS1-blockerré.

Feladata, hogy világos hosszabb távú célpontot adjon a fejlesztésnek, és meghatározza,
milyen állapotot tekintünk az első olyan zárt kiadásnak, amely már nem pusztán technikai prototípus
vagy vertical slice, hanem könnyen indítható, játszható és szélesebben tesztelhető AETERNA program.

Current production base:

`0862e1002dbef81ee203852714d377592272a0e9`

Current engine state:

`COMBAT_AND_SEAL_FOUNDATION_C0_C6 = COMPLETE_AND_ACCEPTED`

Current next gate:

`VS1_READINESS_REQUIRED`

A 0.0.1 előtt a következő major product-facing mérföldkő:

`VS1 / M6 – első ténylegesen játszható vertical slice`

---

## 1. A DOKUMENTUM CÉLJA

A hosszú fejlesztési folyamat könnyebben követhető, ha nem kizárólag egymást követő technikai feladatokból áll, hanem van egy világosan meghatározott célállapot is, amely felé a projekt fokozatosan közeledik.

A `0.0.1` mérföldkő ezt a célállapotot jelöli.

A mérföldkő lényege:

> Az AETERNA digitális programegysége eljut egy olyan első zárt tesztverzióig, amely könnyen elindítható, teljes AI elleni mérkőzés lejátszására alkalmas, játékos- és tesztelői használati módot biztosít, kezeli a paklikat és a gyűjteményt, valamint részletesen naplózza a program működését.

A dokumentum nem azt mondja meg, hogy minden fejlesztési lépést pontosan milyen sorrendben vagy milyen technológiával kell elkészíteni. Ehelyett azt rögzíti, hogy hová szeretnénk eljutni.

---

## 2. KAPCSOLAT A KORÁBBI PROJEKTCÉLOKKAL

A `0.0.1` mérföldkő nem új projektirány, és nem írja felül a korábban rögzített célokat.

A korábbi technikai és stratégiai célok továbbra is érvényesek, különösen:

1. hivatalos szabályforrásokra és kártyaadatbázisra épülő validált adatpipeline;
2. runtime package és contract-first adatkapcsolat;
3. pontos, determinisztikus és szabályhű C# authoritative engine;
4. viewer-safe snapshot, legal action, action request és event rendszer;
5. Godot/GDScript product-facing kliens;
6. Python external tooling/reference/batch réteg;
7. AI-vs-AI és human-vs-AI tesztelési út;
8. későbbi teljesebb termékfunkciók.

A stabil engine foundation már nem pusztán jövőbeli cél.

Lezárt többek között:

- C.5B production C# foundation;
- korábbi production gameplay/ability foundation;
- Explicit Phase Foundation v1;
- Reaction / Priority Foundation v1;
- Combat + Pecsét Foundation C0–C6;
- terminal Aeternal / authoritative `MatchResult`.

A jelenlegi közvetlen projektgate:

> **`VS1_READINESS_REQUIRED`**

A következő major product-facing cél:

> **VS1 / M6 – első ténylegesen játszható vertical slice**

A `0.0.1` ennek későbbi kibővített termékcélja, nem a VS1 alternatívája.

## 3. A 0.0.1 HELYE A FEJLESZTÉSI ÚTVONALON

A current fejlesztési útvonal nagy vonalakban:

1. **Engine- és contract-foundation**
   - adat/runtime contractok;
   - C# authoritative engine;
   - phase/priority;
   - ability/effect foundation;
   - Combat + Pecsét;
   - terminal match outcome.

   **Current state:** a Combat + Pecsét C0–C6 foundationig lezárt.

2. **VS1 readiness**
   - canonical deckek:
     - `DECK-IGN-HAM-VS1-001`;
     - `DECK-AQU-MOR-VS1-001`;
   - card/mechanic requirement inventory;
   - existing engine capability mapping;
   - csak tényleges blockerre finite implementation.

3. **VS1 / M6 – első ténylegesen játszható vertical slice**
   - két teljes, ténylegesen játszható canonical pakli;
   - simple fair AI;
   - match orchestration;
   - minimal playable Godot UI;
   - human-vs-AI teljes meccs;
   - reproducible AI-vs-AI smoke;
   - viewer-safe hidden information;
   - determinism/regression green;
   - minimum log/diagnostics.

4. **Szükséges köztes mérföldkövek**
   - csak azok a további engine/content/product rétegek,
     amelyek a 0.0.1 teljes célállapotához ténylegesen szükségesek;
   - profile/save;
   - tutorial/starter flow;
   - collection/deck editor;
   - local test economy;
   - booster/duplicate conversion;
   - replay/bug-report/diagnostics;
   - tester-mode toolset;
   - release packaging.

5. **AETERNA 0.0.1**
   - első zárt, offline Windows tesztkiadás;
   - játékos- és tesztelői használati mód;
   - könnyen indítható product package;
   - szélesebb teljes termékteszt.

Rövid current roadmap:

```text
M5 / Combat + Victory Core
→ VS1 / M6 – first truly playable vertical slice
→ necessary intermediate milestones
→ AETERNA 0.0.1
```

A `0.0.1` tehát nem az első vertical slice neve.
A VS1/M6 és a 0.0.1 külön acceptance-szint.

## 4. A 0.0.1 MÉRFÖLDKŐ MEGHATÁROZÁSA

A `0.0.1` akkor tekinthető elért mérföldkőnek, ha az AETERNA digitális program:

- külön fejlesztői környezet nélkül, egyszerűen elindítható;
- rendelkezik játékos- és tesztelői használati móddal;
- rendelkezik működő főmenüvel;
- lehetővé teszi teljes AI elleni mérkőzés lejátszását;
- legalább három AI-nehézségi szintet biztosít;
- szabályosan kezeli a paklikat, kártyákat és kártyapéldányokat;
- rendelkezik pakliszerkesztővel;
- tartalmazza az alapjáték Birodalmainak kezdőpaklijait;
- minden alapjátékos Birodalomhoz külön tutorialt biztosít;
- kezeli az egyszeri ingyenes kezdőpakli-választást;
- tartalmaz helyi gyűjtemény- és tesztgazdasági rendszert;
- kezeli a kártyaritkaságokat és a több példányban megszerzett lapokat;
- támogatja a booster packok és paklik megszerzését;
- teljes körű mérkőzés- és rendszerlogot készít;
- rendelkezik a logokhoz kapcsolódó hibajelentővel;
- és legalább technikai szinten támogatja a mérkőzések visszajátszhatóságát vagy reprodukálhatóságát.

A `0.0.1` nem végleges kereskedelmi kiadás.

Ez egy zárt, fejlesztői és meghívott tesztelői használatra alkalmas első teljes tesztprogram.

---

## 5. INDÍTÁS ÉS PROGRAMCSOMAG

### 5.1 Elsődleges indítás

A cél egy könnyen indítható Windows program.

Elsődleges forma:

- önálló vagy csomagolt `.exe`.

Fejlesztői és diagnosztikai tartalék:

- `.bat` indító;
- külön teszt- és diagnosztikai futtatók;
- szükség esetén parancssori vagy headless futtatás.

A tesztelő számára az elsődleges használati út nem igényelhet Python-parancsot, Godot Editort vagy kézi mappakezelést.

### 5.2 Verzióazonosítás

A programban jól láthatóan szerepeljen:

- programverzió;
- engine-verzió;
- runtime package verzió;
- kártyaadat-verzió;
- mentési formátum verziója.

Ez szükséges a hibák visszakereséséhez és a különböző tesztkiadások elhatárolásához.

---

## 6. HASZNÁLATI MÓDOK

A program indításakor vagy a profil létrehozásakor két fő használati mód legyen választható.

### 6.1 Játékos mód

A Játékos mód a későbbi normál játékélményt modellezi.

Fő jellemzői:

- csak a megszerzett kártyák és paklik használhatók;
- működik a gyűjtemény;
- működik a játékbeli pénz és a köztes beváltási erőforrás;
- elérhetők a tutorialok;
- megszerezhető az egyszeri ingyenes kezdőpakli;
- további paklik és booster packok játékbeli erőforrásért szerezhetők meg;
- a pakliszerkesztő figyelembe veszi a tulajdonolt példányszámokat;
- a program nem engedi a gyűjteményen túli normál paklihasználatot.

### 6.2 Tesztelő mód

A Tesztelő mód célja a kártyák, paklik, AI-k és játékszituációk gyors vizsgálata.

Fő jellemzői:

- minden kártya elérhető;
- minden hivatalos tesztpakli elérhető;
- nincs gyűjteményi vagy gazdasági hozzáférési korlátozás;
- részletesebb logok és diagnosztikai adatok jeleníthetők meg;
- elérhető lehet AI-vs-AI futtatás;
- elérhetők lehetnek előre elkészített tesztszituációk;
- könnyebb a hibák reprodukálása és jelentése.

A Tesztelő mód alapértelmezés szerint továbbra is tartsa be a játék szabályait.

### 6.3 Sandbox / fejlesztői felülírás

A szabálytalan paklik, mesterséges kezdőállapotok, tetszőleges lapok kézbe vagy Domíniumba helyezése és más fejlesztői beavatkozások külön Sandbox vagy Debug lehetőségként kezelendők.

A Tesztelő mód és a szabályfelülíró Sandbox ne legyen automatikusan ugyanaz.

---

## 7. FŐMENÜ ÉS PROGRAMNAVIGÁCIÓ

A módválasztás után külön főmenü szükséges.

### 7.1 Játékos mód főmenüje

Tervezett fő lehetőségek:

- AI elleni játék;
- Tutorialok;
- Paklik;
- Pakliszerkesztő;
- Gyűjtemény;
- Bolt;
- Booster bontás;
- Replayek;
- Statisztikák;
- Beállítások;
- Hibajelentés;
- Kilépés.

### 7.2 Tesztelő mód főmenüje

Tervezett fő lehetőségek:

- Gyors tesztmeccs;
- AI-vs-AI teszt;
- Pakliszerkesztő;
- Minden kártya böngészése;
- Tesztszituációk;
- Replay és event log;
- Diagnosztika;
- Hibajelentés;
- Beállítások;
- Kilépés.

A két mód lehetőleg ugyanazt a game engine-t és ugyanazokat az alapvető UI-elemeket használja. A különbség elsősorban a hozzáférési jogosultságokban és a megjelenített diagnosztikai lehetőségekben legyen.

---

## 8. GAME ENGINE KÖVETELMÉNY

A `0.0.1` csak stabil game engine-re épülhet.

A mérföldkő szempontjából a stabil engine legalább azt jelenti, hogy:

- egy mérkőzés szabályos kezdőállapotból létrehozható;
- a játékosok, paklik és kártyapéldányok egyértelmű azonosítót kapnak;
- minden kártyapéldány pontosan egy megfelelő zónában található;
- a játéktér és a zónák állapota követhető;
- a körök, fázisok, prioritások és reakciós ablakok kezelhetők;
- a legal action lista a tényleges szabályos lehetőségeket tartalmazza;
- az action request csak ellenőrzés után hajtható végre;
- az engine a végrehajtás eredményét eseményekkel rögzíti;
- a kártyaképességek szabályhűen működnek;
- a harc és a Pecsét-rendszer végigjátszható;
- a győzelmi és vereségi állapotok megbízhatóan felismerhetők;
- az engine determinisztikusan futtatható;
- ugyanaz a seed és ugyanaz az akciósor ugyanazt az eredményt adja;
- az invariáns- és validációs hibák láthatók;
- egy blokkoló engine-hiba nem maradhat csendben.

Az engine működése elsődleges a felülethez képest.

A UI nem találhat ki szabályokat, nem módosíthatja közvetlenül a játékállapotot, és nem kerülheti meg az engine action request útvonalát.

---

## 9. JÁTÉKMÓDOK ÉS AI

### 9.1 Ember–AI

A `0.0.1` elsődleges tényleges játékmódja:

- egy emberi játékos egy AI ellen.

A játékos a saját paklijával vagy kiválasztott tesztpaklival játszik.

### 9.2 AI-vs-AI

Tesztelő módban elérhető legyen az AI-vs-AI futtatás.

Ennek célja:

- engine-stabilitás ellenőrzése;
- hosszabb mérkőzéssorozatok futtatása;
- kártyák és paklik viselkedésének vizsgálata;
- AI-döntési problémák felismerése;
- balanszadatok gyűjtése;
- hibák reprodukálása.

### 9.3 AI-nehézségek

Legalább három nehézségi szint szükséges:

#### Könnyű

- szabályosan játszik;
- felismerhető alapstratégiát követ;
- egyszerűbb értékelést használ;
- időnként szándékosan gyengébb, de nem értelmetlen döntést választ.

#### Normál

- követi a pakli és a Birodalom fő játéktervét;
- megfelelő célpontokat választ;
- figyelembe veszi az erőforrásokat és a pályaállapotot;
- általános tesztelésre alkalmas ellenfél.

#### Nehéz

- jobb erőforrás-tervezést használ;
- több akciót vagy várható következményt értékel;
- jobban kezeli a reakciókat és a fenyegetéseket;
- a pakli saját stratégiáját következetesebben alkalmazza.

A nehézségi szintek lehetőleg ugyanarra a szabályos legal action térre épüljenek. A nehézség ne csalással, rejtett információk jogtalan megismerésével vagy szabályfelülírással növekedjen.

### 9.4 Nem cél a 0.0.1-ben

A `0.0.1`-ben nem szükséges:

- ember–ember helyi mód;
- online többjátékos mód;
- matchmaking;
- ranglista;
- hálózati szinkronizáció.

---

## 10. BIRODALMI KEZDŐPAKLIK ÉS TUTORIALOK

### 10.1 Kezdőpaklik

Minden alapjátékos Birodalomhoz tartozzon külön kezdőpakli.

Az alapjátékos Birodalmak:

- IGNIS;
- AQUA;
- TERRA;
- LUX;
- UMBRA;
- VENTUS;
- AETHER.

A kezdőpaklik célja:

- a Birodalom alapidentitásának bemutatása;
- a játék fő szabályainak tanítása;
- az adott Birodalom erősségeinek és korlátainak megmutatása;
- játszható, de nem feltétlenül végleges versenypakli biztosítása.

### 10.2 Külön tutorial minden Birodalomhoz

Minden Birodalom saját tutorialt kapjon.

A tutorial:

- bemutatja a Birodalom játékstílusát;
- irányított vagy részben irányított mérkőzést használ;
- kiemeli a Birodalom természetes erősségeit;
- megmutatja a jellemző kártyaszerepeket;
- bemutat legalább néhány fontos döntési helyzetet;
- nem kizárólag általános szabálymagyarázat;
- újrajátszható.

### 10.3 Egyszeri ingyenes kezdőpakli

A játékos az első sikeresen teljesített tutorial után egyszeri lehetőséget kap egy kezdőpakli ingyenes kiválasztására.

Alapszabályok:

- a választási lehetőség csak egyszer jár;
- a játékos a rendelkezésre álló kezdőpaklik közül választ;
- nem kötelező azonnal választania;
- a tutorialok a választás előtt és után is ismételhetők;
- második ingyenes kezdőpakli nem szerezhető újabb tutorial teljesítésével;
- az egyszeri jutalom állapotát a profilban tartósan tárolni kell;
- ugyanaz a jutalom programhiba vagy újratöltés miatt sem adható oda kétszer.

Javasolt mentési mezők:

- tutorialonkénti teljesítési állapot;
- `starter_reward_unlocked`;
- `starter_reward_claimed`;
- `selected_starter_deck_id`.

---

## 11. PAKLISZERKESZTŐ

A program mindkét fő használati módban tartalmazzon pakliszerkesztőt.

### 11.1 Játékos mód

A pakliszerkesztő:

- csak a játékos által birtokolt kártyákat engedi használni;
- figyelembe veszi a tulajdonolt példányszámot;
- ellenőrzi a pakliméretet;
- ellenőrzi a másolati korlátokat;
- ellenőrzi a Birodalmi és egyéb pakliépítési szabályokat;
- jelzi a szabálytalan vagy hiányos paklit;
- csak érvényes paklival enged normál mérkőzést indítani.

### 11.2 Tesztelő mód

A pakliszerkesztő:

- minden kártyához hozzáférést ad;
- nem korlátoz a megszerzett példányszám;
- alapértelmezés szerint továbbra is ellenőrzi a pakli legalitását;
- külön Sandbox opcióval engedhet szabálytalan tesztpaklit.

### 11.3 Keresés és szűrés

Legalább az alábbi szűrések szükségesek:

- Birodalom;
- Klán;
- laptípus;
- Faj;
- Kaszt;
- Magnitúdó;
- Aura;
- ritkaság;
- kulcsszó;
- kártyanév;
- tulajdonolt példányszám;
- használható / nem használható státusz.

---

## 12. GYŰJTEMÉNY ÉS KÁRTYAPÉLDÁNYOK

A Játékos mód helyi gyűjteményt kezel.

A rendszer különböztesse meg:

- a kártya szabályi definícióját;
- a kártya nyomtatási vagy kiadási változatát;
- a játékos tulajdonában lévő példányok számát;
- és a mérkőzés közben létrejövő konkrét kártyapéldányokat.

A gyűjteményben látható legyen:

- a kártya neve;
- Birodalma és Klánja;
- típusa;
- ritkasága;
- megszerzett példányszáma;
- paklikban jelenleg használt példányszáma;
- felesleges vagy beváltható példányszáma;
- szükség esetén art, foil vagy más kiadási változata.

A 0.0.1-ben a gyűjtemény lehet teljesen helyi, offline profilhoz kötött rendszer.

---

## 13. RITKASÁGI RENDSZER

A program jelenítse meg és használja a kártyaadatbázis hivatalos ritkasági rendszerét.

A ritkaság kapcsolódhat:

- a booster packból történő nyitási esélyhez;
- a vizuális megjelenítéshez;
- a beváltási értékhez;
- a későbbi készítési vagy megszerzési költséghez;
- a gyűjtemény szűréséhez;
- a pakli és booster tartalmi struktúrájához.

A 0.0.1-ben a cél nem a végleges gazdasági balansz, hanem:

- a helyes rarity-adat használata;
- a helyes megjelenítés;
- a booster-generálás működése;
- a megszerzett példányok helyes nyilvántartása.

---

## 14. JÁTÉKBELI GAZDASÁG

A 0.0.1 tartalmazzon egyszerű, helyi tesztgazdaságot.

### 14.1 Játékbeli pénz

Játékbeli pénz szerezhető legalább:

- AI elleni győzelemért.

Később mérlegelhető:

- első napi győzelem;
- tutorial-jutalom;
- kihívások;
- vesztes mérkőzés kisebb jutalma;
- teljesítmények.

A 0.0.1-ben nem szükséges valós pénzes vásárlás.

### 14.2 Megvásárolható tartalmak

Játékbeli pénzért megszerezhető lehet:

- további kezdő- vagy tematikus pakli;
- booster pack;
- később más, nem szabályi előnyt adó tartalom.

### 14.3 Felesleges példányok beváltása

A több példányban megszerzett, már nem szükséges kártyák beválthatók.

Javasolt köztes modell:

> felesleges kártyapéldány → külön köztes erőforrás → későbbi kártyaszerzés, készítés vagy korlátozott átváltás

A köztes erőforrás munkaneve később határozható meg.

Ennek előnye, hogy a booster vásárlására használt pénz és a kártyák beváltási értéke külön szabályozható.

### 14.4 Gazdasági elhatárolás

A 0.0.1 gazdasága:

- helyi;
- tesztcélú;
- módosítható;
- nem valódi pénzes;
- nem szerver által hitelesített;
- nem tekintendő végleges balansznak.

---

## 15. BOOSTER PACKOK

A program támogassa a booster packok megszerzését és felbontását.

A booster-rendszernek kezelnie kell:

- a booster termékazonosítóját;
- a hozzá tartozó kártyapoolt;
- a ritkasági slotokat vagy húzási szabályokat;
- a véletlengenerálás seedjét;
- a kibontott kártyákat;
- a gyűjtemény frissítését;
- a duplikált példányokat;
- a nyitás naplózását.

A booster pack nem azonos az Expansion vagy kiegészítő szabályi egységgel.

A 0.0.1-ben elsődlegesen az alapjátékos vagy kifejezetten engedélyezett tesztpoolok használhatók.

---

## 16. PROFIL ÉS MENTÉS

A 0.0.1-ben helyi játékosprofil elegendő.

A profil kezelje:

- a játékos nevét vagy profilazonosítóját;
- a választott használati módot;
- tutorialállapotokat;
- az egyszeri kezdőpakli-jutalmat;
- játékbeli pénzt;
- köztes beváltási erőforrást;
- gyűjteményt;
- saját paklikat;
- meccsstatisztikákat;
- beállításokat;
- replayeket;
- hibajelentéseket vagy azok helyi hivatkozásait.

Szükséges funkciók:

- automatikus mentés;
- mentési hiba felismerése;
- profilreset;
- új tesztprofil létrehozása;
- lehetőleg profil export és import;
- mentési formátum verziózása.

A játékosprofil és a Tesztelő mód állapota lehetőleg külön kezelhető legyen, hogy a fejlesztői tesztelés ne rontsa el a normál játékosprofilt.

---

## 17. TELJES KÖRŰ NAPLÓZÁS

A 0.0.1 egyik legfontosabb követelménye a részletes és strukturált naplózás.

### 17.1 Mérkőzésazonosító adatok

Minden mérkőzéshez rögzíteni kell:

- programverzió;
- engine-verzió;
- runtime package verzió;
- kártyaadat-verzió;
- match ID;
- seed;
- dátum és idő;
- használt játékmód;
- AI-nehézség;
- használt paklik;
- játékosprofil azonosítója, ha releváns.

### 17.2 Játékmenetnapló

Rögzítendő:

- kezdeti állapot;
- minden action request;
- minden elfogadott és elutasított action response;
- minden engine-esemény;
- állapotverziók;
- zónamozgások;
- véletlen eredmények;
- prioritás- és fázisváltások;
- triggerelt képességek;
- célpontválasztások;
- fizetések;
- harci eredmények;
- győzelmi vagy vereségi esemény;
- warningok;
- invariáns- és validációs hibák.

### 17.3 Rendszerlog

A program külön rendszerlogban kezelje:

- indítási hibákat;
- adatbetöltési hibákat;
- runtime package validációt;
- mentési és betöltési hibákat;
- UI-hibákat;
- nem kezelt kivételeket;
- teljesítményproblémák alapadatait;
- hibajelentő csomag készítését.

### 17.4 Olvasható és gépi log

Lehetőleg két réteg készüljön:

- ember számára olvasható összefoglaló log;
- strukturált JSON vagy JSONL eseménynapló.

---

## 18. REPLAY ÉS REPRODUKÁLHATÓSÁG

A replay elsődlegesen ne videofelvétel legyen.

A tervezett replay-alap:

- kezdeti mérkőzésállapot vagy annak biztonságos referenciája;
- runtime package és szabályverzió;
- seed;
- elfogadott akciók sorrendje;
- engine-események;
- állapotverziók;
- végállapot és eredmény.

A replay céljai:

- mérkőzés visszanézése;
- hibák reprodukálása;
- engine-változások összehasonlítása;
- AI-döntések vizsgálata;
- tesztesetek készítése.

A `0.0.1` minimális elfogadási szintje lehet:

- a mérkőzés eseményei lépésenként visszaolvashatók;
- a replay technikai adatai elmenthetők;
- ugyanazzal a kompatibilis engine- és adatverzióval a mérkőzés reprodukálható.

A végleges, animált replay UI későbbi mérföldkőre maradhat, amennyiben a technikai replay-adat már megbízhatóan elkészül.

---

## 19. HIBAJELENTŐ

A program tartalmazzon beépített hibajelentő funkciót.

A hibajelentő kapcsolódjon a napló- és replay-rendszerhez.

A játékos vagy tesztelő megadhat:

- rövid címet;
- szöveges leírást;
- a hiba észlelésének körülményeit;
- opcionális reprodukciós lépéseket;
- hibakategóriát;
- súlyossági becslést.

A hibajelentő automatikusan csatolhatja:

- program- és engine-verziót;
- runtime package verziót;
- mérkőzésazonosítót;
- releváns logokat;
- replay fájlt;
- utolsó érvényes snapshotot;
- használt paklikat;
- seedet;
- utolsó action requesteket és eseményeket;
- diagnosztikai összefoglalót.

A 0.0.1-ben elegendő lehet egy helyi hibacsomag létrehozása, például ZIP formában.

Automatikus online beküldés nem kötelező.

---

## 20. FELHASZNÁLÓI FELÜLET

A 0.0.1-ben nem szükséges végleges grafikai minőség, de a teljes alapvető használati út működjön.

A UI legalább az alábbiakat tegye lehetővé:

- program indítása;
- használati mód kiválasztása;
- főmenü használata;
- profil kezelése;
- tutorial kiválasztása;
- pakli kiválasztása;
- pakliszerkesztés;
- AI-nehézség kiválasztása;
- mérkőzés lejátszása;
- kéz, pakli, Ősforrás, Domínium, Pecsétek és más szükséges zónák megjelenítése;
- kártyák adatainak megtekintése;
- szabályos akciók kiválasztása;
- célpontok kiválasztása;
- reakciós döntések kezelése;
- eredményképernyő megjelenítése;
- jutalmak átvétele;
- gyűjtemény és bolt használata;
- hibajelentés létrehozása.

A UI kizárólag az engine által engedélyezett akciókat kínálja fel.

A játékos elől rejtett információt a normál UI nem jelenítheti meg.

A Tesztelő mód külön, jól látható diagnosztikai nézetben megmutathat többletinformációt.

---

## 21. 0.0.1 KIADÁSI KAPUK

A `0.0.1` nem tekinthető elkészültnek pusztán attól, hogy a felsorolt menüpontok megjelennek.

### 21.1 Kötelező engine-kapu

- teljes mérkőzés lejátszható;
- nincs ismert, gyakran előforduló blokkoló engine-hiba;
- a legal action rendszer nem kínál rendszeresen illegális akciót;
- a végrehajtott akciók után az invariánsok ellenőrizhetők;
- a mérkőzés befejezése megbízható;
- a log elegendő a hibák visszakereséséhez.

### 21.2 Kötelező használhatósági kapu

- a program tiszta tesztgépen elindítható;
- nem szükséges fejlesztői környezet;
- a menükből elérhető a teljes alapvető használati út;
- új játékos tutorial segítségével el tud kezdeni játszani;
- a pakliszerkesztő és a gyűjtemény használható;
- a program nem veszti el csendben a mentést.

### 21.3 Kötelező tartalmi kapu

- minden alapjátékos Birodalomhoz van kezdőpakli;
- minden alapjátékos Birodalomhoz van tutorial;
- a kezdőpakli-választás működik;
- a kártyák ritkasága megjelenik;
- booster pack nyitható;
- több kártyapéldány helyesen kezelhető.

### 21.4 Kötelező tesztelési kapu

- legalább három AI-nehézség elérhető;
- AI-vs-AI teszt futtatható;
- replay- vagy reprodukciós adat létrejön;
- hibajelentő csomag készíthető;
- a program- és adatverziók minden jelentésből azonosíthatók.

---

## 22. NEM CÉL A 0.0.1-BEN

A mérföldkő terjedelmének védelme érdekében a következők nem kötelező részei a `0.0.1`-nek:

- ember–ember játékmód;
- online multiplayer;
- szerveroldali profil;
- felhőmentés;
- matchmaking;
- ranglista;
- versenyrendszer;
- valódi pénzes vásárlás;
- játékosok közötti kereskedés;
- csalásvédelem;
- végleges gazdasági balansz;
- végleges vizuális polish;
- minden animáció és hanghatás;
- mobilverzió;
- konzolverzió;
- publikus kereskedelmi kiadás.

Ezek későbbi mérföldkövek lehetnek.

---

## 23. TECHNIKAI DÖNTÉSI KAPUK

A dokumentum eredeti 1.0 változatának több technikai kérdése azóta lezárult.

### 23.1 Lezárt döntések

1. **Authoritative rules runtime**
   - C#/.NET;
   - current authority: `Aeterna.Engine`.

2. **Godot ↔ engine kapcsolat**
   - same-process Godot .NET / C# bridge;
   - nincs production HTTP/TCP/gRPC rules path.

3. **Player build processztopológia**
   - normál játékban nem szükséges külön engine-processz;
   - Python nem player-runtime prerequisite.

4. **Python szerepe**
   - external tooling/reference/batch/AI-controller;
   - Headless C# határon viewer-safe snapshot + legal action alapján dolgozik;
   - nem külön authoritative rules engine.

Ezek nem current nyitott kapuk.

### 23.2 Továbbra is nyitott vagy későbbi döntések

1. save schema és migrációs policy;
2. replay végleges formátuma és product UX-e;
3. bug-report package végleges struktúrája;
4. duplicate-conversion köztes erőforrás neve és pontos szerepe;
5. tesztgazdasági értékek;
6. booster rarity/slot policy;
7. tutorialok kötöttsége és tutorial-AI policy;
8. Tester mode és Sandbox pontos UX-határa;
9. final Windows packaging:
   - self-contained vagy prerequisite modell;
   - clean-machine acceptance;
10. release package identity/compatibility/integrity;
11. 0.0.1 végső content cut a VS1 utáni köztes mérföldkövek alapján.

Ezek a kérdések nem akadályozzák a 0.0.1 dokumentum irányadó szerepét,
és nem válnak automatikusan VS1-blockerré.

## 24. VERZIÓZÁSI ELHATÁROLÁS

A `0.0.1` termékverzió nem azonos:

- a dokumentum `1.0` verziójával;
- a runtime package verziójával;
- a contract schema verzióival;
- a Python vagy Godot technikai checkpointok `v0.1`, `v0.2` vagy más jelöléseivel;
- az engine belső modulverzióival;
- a kártyaadatbázis verziójával.

A dokumentációban mindig egyértelműen jelezni kell, hogy:

- dokumentumverzióról;
- technikai checkpointról;
- schema-verzióról;
- vagy kiadási termékverzióról van szó.

---

## 25. A DOKUMENTUM HASZNÁLATI ELVE

A jelen dokumentum iránytűként használható:

- projekttervezésnél;
- mérföldkövek felállításánál;
- új engine-funkciók indoklásánál;
- Godot UI-fejlesztésnél;
- AI-fejlesztésnél;
- log- és replay-rendszer tervezésénél;
- pakli-, tutorial- és gyűjteményrendszer előkészítésénél;
- későbbi programozási feladatok product-contextjeként.

Nem szabad azonban úgy használni, hogy minden felsorolt 0.0.1 funkció
azonnal első prioritássá vagy VS1-blockerré váljon.

Current scope rule:

VS1 előtt mandatory csak az, ami:

1. a két canonical VS1 deck tényleges működéséhez kell; vagy
2. általános rules-correct / deterministic / viewer-safe VS1 invariáns.

Minden fejlesztési feladatnál továbbra is figyelembe kell venni:

- az aktuális projekttervet;
- a jelenlegi technikai állapotot;
- a függőségeket;
- az aktuális milestone acceptance-szintet;
- a kis, tesztelhető lépések elvét.

A jelen dokumentum nem írhatja felül az aktuális projektterv prioritási sorrendjét.

## 26. ZÁRÓ ALAPELV

Az AETERNA `0.0.1` mérföldkő nem a fejlesztés végét jelenti.

Azt jelzi, hogy a projekt eljutott egy fontos fordulóponthoz:

> a szabályforrásokból, kártyaadatokból, runtime contractokból, authoritative engine-ből,
> AI-ból és Godot felületből összeállt egy könnyen indítható, végigjátszható,
> offline és részletesen tesztelhető zárt AETERNA program.

Current sorrend:

```text
Combat + Pecsét C0–C6 COMPLETE_AND_ACCEPTED
→ VS1_READINESS_REQUIRED
→ VS1 / M6
→ szükséges köztes mérföldkövek
→ AETERNA 0.0.1
```

A közvetlen product-facing cél tehát most a VS1/M6, nem maga a 0.0.1.

A 0.0.1 ennek kibővített első zárt tesztkiadási célállapota:
akkor teljesül, amikor már nemcsak különálló technikai elemek vagy egy minimal vertical slice működik,
hanem ezek együtt egy használható AETERNA tesztprogramot alkotnak.
