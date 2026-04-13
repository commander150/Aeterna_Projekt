# AETERNA - Tesztprogram Workflow es Tesztprofilok

Ez a dokumentum azt rogzitI, hogyan erdemes a jelenlegi AETERNA rendszert
tesztprogramkent hasznalni.

Nem uj gameplay-frontot nyit, es nem teljes QA-kezikonyv.
A celja az, hogy a mar meglevo motorbol, logokbol, AI-vs-AI futasokbol es backend
retegekbol minel tobb gyakorlati hasznot kapjunk:
- broken mechanikak felismeresere
- tul eros lapok vagy iranyok kiszuresere
- regressziok gyors eszrevetelere

## 1. Rov id cel

A program most elsosorban ezekre jo teszteszkozkent:
- altalanos AI-vs-AI smoke futasokra
- seedelt, ismetelheto matchup-vizsgalatra
- adott birodalom vagy irany viselkedesenek megfigyelesere
- egy-egy lap vagy mechanika regresszios ujraellenorzesere
- logok, meccssummaryk es statok alapjan gyanus viselkedesek kiszuresere

Rovid gyakorlati cel:
- gyorsan latszodjon, ha valami nyilvanvaloan nem mukodik
- gyorsan latszodjon, ha valami gyanusan dominans
- egy modositast lehessen szuk, ismetelheto korrel ujraellenorizni
- a log kulon jelezze a szabalyblokk miatt review-t igenylo lapokat (`SEAL_RULE_BLOCKED`, `LANE_SEAL_BLOCKED`, `REVIEW_NEEDED`)

## 2. Milyen tipusu teszteket erdemes futtatni

### 2.1 Altalanos AI-vs-AI smoke test
Erre valo:
- a motor egyaltalan vegigmegy-e meccseken
- van-e kritikus leallas
- latszik-e nagyon furcsa, egyoldalu vagy ures jatek

Mikor hasznos:
- kisebb runtime vagy backend valtoztatas utan
- loader / facade / apply_action / logging kor utan

### 2.2 Adott birodalom vs adott birodalom futas
Erre valo:
- matchup-szintu kepet adjon
- latszodjon, hogy egy adott birodalom gyanusan dominans-e
- egy adott reteg javitasa tenyleg megjelenik-e a valos futasban

### 2.3 Ugyanaz a matchup tobb seeddel
Erre valo:
- ne egyetlen random futasbol vonjunk le kovetkeztetest
- latszodjon, hogy egy tuno minta stabil-e vagy csak zaj

### 2.4 KonkreT lap vagy mechanika celzott vizsgalata
Erre valo:
- trap, summon, seal break, source placement, direkt sebzes vagy mas celzott viselkedes ellenorzese
- logban es meccsviselkedesben tenyleg elojon-e a javitott ag
- fontos szabaly: a direkt sebzes es a Pecset-feltores kulon jatekmuvelet; a sebzes nem torhet Pecsetet, csak explicit Pecset-toro hatas

### 2.5 Regresszios futas modositAs utan
Erre valo:
- a javitott mechanika mellett ne torjon el a szomszedos viselkedes
- pl. `play_entity`, `play_trap`, `end_turn`, legal-actions, state-context, action result

### 2.6 Hosszu futas / kifogyas kozeli megfigyeles
Erre valo:
- paklielfogyas
- overflow
- seal break tempo
- nagyon hosszu kontrollmeccsek

## 3. Minimalis tesztprofil-javaslatok

Az alábbi profilok mind kis szervezessel futtathatok a jelenlegi rendszerrel.

### Profil 1 - Veletlen altalanos smoke
- cel: gyors altalanos egeszsegellenorzes
- beallitas:
  - `games=3-5`
  - `player1_realm=None`
  - `player2_realm=None`
  - `random_seed` rogzitheto vagy random
- figyeld:
  - futas vegigmegy-e
  - van-e kritikus hiba
  - teljesen ures vagy nagyon torz meccsek vannak-e

### Profil 2 - Ugyanaz a matchup tobb seeddel
- cel: stabil matchup-kep
- beallitas:
  - pl. `Ignis vs Aqua`
  - `games=5-10`
  - tobb kulon `random_seed`
- figyeld:
  - nagyjabol stabil-e a gyozelmi arany
  - ugyanaz az irany minden seedben dominans-e

### Profil 3 - Egy konkret birodalom fokusz
- cel: egy birodalom altalanos erossegenek, tempojanak es hibaerzekenysegenek merese
- beallitas:
  - `player1_realm=Ignis`
  - `player2_realm=random`
  - `games=10`
- figyeld:
  - tul gyakori gyors gyozelem
  - ugyanaz a tempominta ujra es ujra
  - jel/trap/summon logok hianya vagy tulreprezentaltsaga

### Profil 4 - Trap-heavy kontroll vs agressziv irany
- cel: a csapdak, seal break tempo es vedekezesi reteg gyakorlati ellenorzese
- beallitas:
  - olyan matchup, ahol az egyik oldal varhatoan csapda- vagy lassabb kontroll irany
  - a masik oldal gyorsabb tamado irany
- figyeld:
  - tenylegesen latunk-e trap play / trap trigger mintat
  - a kontroll oldal csak tulel, vagy tenyleg erdemi megallitas is tortenik

### Profil 5 - Gyors swarm vs lassu kontroll
- cel: tempobalance
- beallitas:
  - gyors entitas-heavy oldal vs lassabb, eroforras-epito oldal
- figyeld:
  - tul gyors seal break
  - a lassu oldalnak van-e ertelmes jateka
  - irrealisan rovid meccsek

### Profil 6 - Hosszu meccs / kifogyas kozel
- cel: pakli, temeto, overflow es seal break hosszabb tavon
- beallitas:
  - nagyobb `games`
  - seedelt kontroll-jellegu matchup
- figyeld:
  - ujrakeveres
  - buntetesek
  - overflow
  - ismetlodo patthelyzet

### Profil 7 - Celzott mechanika-regresszio
- cel: egy javitott mechanika valos futasban is latszik-e
- beallitas:
  - ugyanaz a matchup tobb seed
  - logokban keresett jelenseg pl. summon, trap, source placement
- figyeld:
  - a javitott ag megjelenik-e a logban
  - nincs-e mellette uj blokkolo vagy fallback gyanus sor

### Profil 8 - Backend boundary smoke
- cel: backend oldali state/action szerzodes ne torjon
- beallitas:
  - unittest + kis facade smoke
- figyeld:
  - snapshot
  - legal-actions
  - validate_action
  - apply_action
  - event log

## 4. Mit kell figyelni a logokban es eredmenyekben

### 4.1 Tul gyakori egyoldalu gyozelem
Gyanus, ha:
- ugyanaz a birodalom vagy irany minden seedben nagyon hasonloan nyer
- a veres oldalon alig latszik board-jatek vagy seal pressure

### 4.2 Tul rovid vagy tul hosszu meccsek
Gyanus, ha:
- rendszeresen irrealisan gyors a seal break
- vagy a meccsek elhuzodnak es nincs ertelmes lezaro dinamika

### 4.3 Bizonyos actionok vagy zonak hianya
Gyanus, ha:
- vannak lapok, de nincs summon
- vannak jelek, de nincs trap play vagy trigger
- a zenit vagy source gyakorlatilag soha nem jelenik meg

### 4.4 Tul gyakori seal break tempo
Gyanus, ha:
- 1-2 kor alatt rendszeresen pecsettorés tortenik
- a vedekezesi retegek lathatoan nem kapnak szerepet

### 4.5 Gyanusan dominans lap vagy strategia
Gyanus, ha:
- ugyanaz a kartya vagy minta tobb seedben is lathatoan eldönti a jatekot
- ugyanaz a tempo vagy board-allapot rendszeresen megismetlődik

### 4.6 Furcsa uresseg vagy kihagyott jatek
Gyanus, ha:
- sok kor megy el keves actionnel
- legalisnak tuno lapok nem jelennek meg a jatekban
- a board-hasznalat feltunoen szegenyes

## 5. Mi szamit "broken" gyAnunak

Gyakorlati broken-gyanus jelek:
- a meccs logikailag elakad vagy ertelmetlenul ismetlodik
- egy actiontipus lathatoan eltunik a jatekbol
- a jatek egy adott reteg utan rendszeresen felborul
- valami kovetkezetesen rossz zónába, rossz időben vagy rossz allapotban jelenik meg
- ugyanaz a mechanika tobb seedben lathatoan hibas vagy kimarad
- a backend szerint legalis action a runtime-ban megsem tud kulturaltan lefutni

## 6. Mi szamit "tul eros lap" gyAnunak

Gyakorlati tul eros lap/irany jelek:
- ugyanaz a lap rendszeresen koran, kis valaszablakkal meccset dönt
- ugyanaz a lap vagy kis lapcsomag aranytalanul sok seedben jelenik meg a gyoztes oldalon
- a lap hatasa utan a masik oldal lathatoan elveszti a jatek lehetoseget
- a laphoz kepest a koltseg / kockazat / valaszolhatosag aranytalan
- egy adott irany minden mas tesztprofilban torz gyozelmi aranyt mutat

## 7. A jelenlegi rendszer korlatai tesztelesi szempontbol

### Mire jo most
- AI-vs-AI smoke es matchup tesztre
- celzott mechanika- vagy lapgyanus viselkedes figyelesere
- logalapu broken-gyanu azonositasra
- seedelt regresszios ujrafuttatasra
- backend boundary smoke ellenorzesre

### Mire nem eleg meg
- teljes balanszkovetkeztetesre nagy mintan
- teljes deckepites- vagy metaelemzesre
- minden actiontipus fedett, frontend- vagy backend-vezerelt tesztelesere
- teljes spell/targeting/combat finomdontesi szimulaciora kulon tesztkeret nelkul

## 8. Gyakorlati ajanlott workflow

### 8.1 Modositas elott
- tisztazd, mit akarsz ellenorizni
- valassz 1 fo tesztprofilt es 1 regresszios profilt

### 8.2 Modositas utan
- futtasd a szuk unittest kort
- futtasd a valasztott AI-vs-AI smoke vagy matchup kort
- ne egyszerre sok kulonbozo tesztcelra probalj valaszolni

### 8.3 KiErtekeles
- eloszor a kritikus hibakat nezd
- utana a gyozelmi mintat
- utana a logokban a celzott mechanikat
- csak ezutan vonj le kovetkeztetest laperossegrol vagy broken allapotrol

## 9. Jelenlegi legjobb haszon/kockazat irany

A maradek idoben a legnagyobb gyakorlati hasznot ezek adjak:
- seedelt, kis mintas matchup-ellenorzes
- egy-egy mechanika celzott regresszios futasa
- logokbol es meccssummarybol gyanus mintak kiszurese
- backend smoke regresszio, hogy a jovo frontend-integracio se torjon

Ez illeszkedik a projekt eredeti celjahoz:
- broken mechanikak felismerese
- tul eros lapok/iranyok kiszurese
- AI-vs-AI tesztprogramkent hasznalhato rendszer fenntartasa

## 10. Konnyu tesztlauncher

A jelenlegi workflow hasznalhatosagat egy nagyon konnyu launcher segiti:

- `simulation/test_launcher.py`

Celja:
- ne kelljen minden futast kezzel parameterezni
- gyorsabban lehessen smoke, seedelt matchup es ismEtelt matchup kort inditani
- egyszerubb legyen seedet, futasszamot es P1/P2 birodalmat megadni

Hasznalat:

```bash
python -m simulation.test_launcher
```

A launcher:
- elore definialt profilokat ad
- enged egyszeru felulirast
- es kis kockazattal ujra tudja futtatni az utolso hasznalt beallitasokat is
- egy futas utan visszater a fomenube, igy nem kell minden kor utan ujrainditani
- interaktiv modban beszedesebb segitszovegeket ad a seedhez, futasszamhoz es birodalomvalasztashoz
- deck preseteket is tud kezelni, ha ugyanazt a tesztpaklit akarod ujrafuttatni

Nem-interaktiv, gyorsabb hasznalat is van:

```bash
python -m simulation.test_launcher --profile smoke_random
python -m simulation.test_launcher --profile seeded_matchup --seed 123 --runs 5 --p1 Ignis --p2 Aqua
python -m simulation.test_launcher --profile seeded_matchup --seed 123 --runs 5 --p1 terra --p2 VENTUS
python -m simulation.test_launcher --profile seeded_matchup --p1-preset ignis_tempo_test --p2-preset aqua_control_test --seed 123 --runs 5
python -m simulation.test_launcher --last-run
python -m simulation.test_launcher --list-profiles
python -m simulation.test_launcher --list-deck-presets
```

Megjegyzes:
- a launcher a birodalomneveket case-insensitive kezeli
- pl. `terra`, `Terra` es `TERRA` ugyanugy mukodik
- ismeretlen birodalomnevnel kulturalt hiba uzenetet ad az elerheto opciokkal
- deck presetnel a futas realm + preset nevvel egyutt jelenik meg a summaryban
- preset hasznalatkor a pakliepites nem random realm poolbol, hanem a rogzitett tesztpaklibol tortenik

Batch seed futtatas is van, ha ugyanazt a matchupot gyorsan tobb seeddel akarod ujraellenorizni:

```bash
python -m simulation.test_launcher --profile seeded_matchup --seed-list 101,102,103 --runs 3 --p1 Ignis --p2 Aqua
python -m simulation.test_launcher --profile repeated_matchup --seed-start 200 --seed-count 5 --runs 4 --p1 Ignis --p2 Aqua
```

A batch futas vegen a launcher rovid, emberileg gyorsan olvashato osszesitot is kiir:
- hany futas ment le
- mely seedek futottak
- hogyan oszlottak meg a gyozelmek
- mekkora volt az atlagos korszam
- mennyi summon / spell / trap / seal break aktivitas latszott
- mely lapok jelentek meg leggyakrabban a gyoztes oldalon
- ha egyszeru launcher-szintu gyanus minta latszik, kulon figyelmeztetest is ad

Ez kulonosen hasznos:
- seedelt matchupok gyors ujrafuttatasara
- regresszios korok ismetlesere
- kevesebb kezi parameterezessel vegzett smoke futasokra
- a visszatero, meccsformalo lapok gyors kiszurasara batch vegen

## 11. Kulon felvezerelt CLI prototipus

A tesztlauncher mellett most mar van egy kulon, facade-alapu technikai CLI mod is:

- `simulation/interactive_match_cli.py`
- kulon indito: `run_interactive_match_cli.py`

Celja nem a teljes ember-vs-AI rendszer, hanem egy szuk, oszinte technikai MVP:
- uj meccset indit
- rovid snapshotot jelenit meg
- kilistazza a jelenlegi legal actionoket
- engedi egy tamogatott action kivalasztasat
- vegrehajtja az akciot a backend facade-n at
- megmutatja az eredmenyt es a rovid event listat

Hasznalat:

```bash
python run_interactive_match_cli.py
python -m simulation.interactive_match_cli --p1 Ignis --p2 Aqua --seed 123
```

Fontos korlat:
- ez meg nem teljes ember-vs-AI jatekmod
- csak azt tudja emberileg kiprobalhato modon, amit a jelenlegi backend mar formalizalt
- jelenleg kulonosen az `end_turn`, `play_entity` es `play_trap` akciokra hasznos technikai prototipus
