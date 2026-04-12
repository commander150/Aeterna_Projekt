# Warning Triage Tesztprogram Szempontbol

## Rov id helyzetkep

A jelenlegi logok szerint a `cards.xlsx` betoltesekor tovabbra is `145` validator
warning jelenik meg minden futas elejen. Ez onmagaban nem jelenti azt, hogy a
tesztprogram haszontalan, de eros jelzes arra, hogy a tesztfutas elott mar van egy
ertelezesi bizonytalansagi retege.

Tesztprogram-szempontbol nem minden warning egyforma:
- van, ami inkabb zaj vagy standardizacios adossag
- van, ami rontja a futasok ertelmezhetoseget
- es van, ami mar potencialisan felrevezeto gameplay-kepet is adhat

Ez a triage nem warning-cleanup terv, hanem priorizalt tesztprogram-nezopont.

## Jelenlegi warning kep roviden

Workbook + elo validator allapot alapjan:

- osszes warning: `145`
- `suspicious_field_combination`: `74`
- `unknown_enum_value`: `48`
- `legacy_internal_value`: `22`
- egyeb: `1`

Leggyakoribb konkret mintak:

1. `suspicious_field_combination:idotartam_hatascimke_nelkul` - `61`
2. `unknown_enum_value:idotartam_felismerve:trap` - `16`
3. `legacy_internal_value:trigger_felismerve:on_play` - `15`
4. `unknown_enum_value:zona_felismerve:burst` - `12`
5. `unknown_enum_value:kulcsszavak_felismerve:trap` - `8`
6. `unknown_enum_value:hatascimkek:trap` - `8`
7. `suspicious_field_combination:gyanus_target_tipus_kombinacio:own_hand` - `6`
8. `suspicious_field_combination:gyanus_target_tipus_kombinacio:enemy_hand` - `6`

## A) Artalmatlan vagy alacsony prioritAsu zaj

Ezek zavarok, de altalaban nem torzitjak drasztikusan a tesztfutasbol levont
kovetkeztetest:

- `legacy_internal_value:*` olyan esetben, amikor a runtime mar amugy is adaptereli
  a jelenseget
- elszort, ritka `unknown_enum_value`, ha a kartya amugy ritkan vagy egyaltalan nem
  jelenik meg a vizsgalt matchupban
- olyan `suspicious_field_combination`, ami inkabb dokumentacios kovetkezetlenseg,
  mint valodi runtime-elteres

Jelenlegi peldak:
- `legacy_internal_value:trigger_felismerve:on_play`
- `legacy_internal_value:trigger_felismerve:on_burst`

Tesztprogram-hatas:
- zajosabb indulasi log
- nehezebb elsore meglatni, mi uj es mi regi backlog
- de onmagaban nem biztos, hogy meghamisitja a meccs kimenetet

## B) Tesztelesi erteket ronto warning

Ezeknel nem feltetlen azonnali runtime-hiba a fo problema, hanem az, hogy
bizonytalanabba teszik, mit is tesztelunk valojaban.

Ide tartoznak:
- `suspicious_field_combination:idotartam_hatascimke_nelkul`
- `suspicious_field_combination:gyanus_target_tipus_kombinacio:own_hand`
- `suspicious_field_combination:gyanus_target_tipus_kombinacio:enemy_hand`
- egyes `legacy_internal_value` esetek, ha canonical helyett regi triggernev maradt

Miert fontos ez tesztprogramkent:
- ha van `idotartam`, de nincs melle `hatascimke`, nem egyertelmu, hogy a kartya
  tenyleg valami allapotot ad, vagy csak rosszul kitoltott sor
- ha egy `Entitas` sor `own_hand` / `enemy_hand` targetet kap, bizonytalan, hogy
  tenyleg egy card-in-hand jelenseget akarunk-e, vagy rossz target-felismeres
  tortent

Gyakorlati kar:
- nehezebb megbizni abban, hogy a logban latott viselkedes a kartya valodi terve
- broken-gyanu es balanszgyanu konnyen adatminosegi zavarral keveredhet

## C) Magas prioritasu, tenylegesen veszelyes warning

Ezek mar jo esellyel felreertelmezett vagy hianyosan ertelmezett mechanikahoz
vezethetnek.

Ide sorolhato:
- `unknown_enum_value:idotartam_felismerve:trap`
- `unknown_enum_value:zona_felismerve:burst`
- `unknown_enum_value:kulcsszavak_felismerve:trap`
- `unknown_enum_value:hatascimkek:trap`

Miert veszelyesek:
- ezeknel maga a canonical mezoszint serul
- a runtime vagy fallbackre esik, vagy egyszeruen nem azt a strukturalt jelentest
  latja, amit a tablatol varnank
- a tesztfutasban emiatt egy lap teljesen mas bucketbe kerulhet, mint ahova tartozna

Gyakorlati kar:
- felrevezeto mechanikai coverage-kep
- rossz prioritasok a broken / hianyzo mechanikaknal
- olyan lap tunhet gyengenek vagy hibasnak, ami valojaban csak rosszul van
  strukturalt mezokkel rogzitve

## Mit mutat a konkret log tesztprogram-szempontbol

Az `AETERNA_LOG_2026-04-12_15-54-59.txt` alapjan:

- a motor tenylegesen sok mindent futtat: summon, trap, spell, seal break,
  target block, structured effect, shared pathok
- a tesztprogram mar most erdemben hasznalhato broken vagy dominans mintak
  keresere
- viszont a `145` warning minden futas elejen zajt rak a kep ele

A live logban a legnagyobb gyakorlati gond nem az, hogy minden warning veszelyes,
hanem az, hogy elsore nem latszik:
- melyik csak backlog-zaj
- melyik tesztelesi bizonytalansag
- es melyik valodi veszely a mechanikai kepre

## Melyik warning-tipus a leggyakoribb

Leggyakoribb tipusu warning most:

- `suspicious_field_combination` - `74`
- ezen belul messze a legnagyobb resz:
  - `idotartam_hatascimke_nelkul` - `61`

Ez darabra a legnagyobb blokk.

## Melyik a legzavarobb tesztprogram-szempontbol

Legzavarobb tesztprogram-szempontbol:

- `suspicious_field_combination:idotartam_hatascimke_nelkul`

Miert:
- nem feltetlen konkret runtime crash vagy rossz token
- de nagy mennyisegben bizonytalanna teszi, hogy egy kartya strukturalt leirasa
  mennyire megbizhato
- ettol a tesztfutasokbol levont kovetkeztetesek is puhabba valnak

## Melyiket kellene eloszor kezelni

Elso celzott kezelesre ezt erdemes valasztani:

1. `suspicious_field_combination:idotartam_hatascimke_nelkul`

Nem azert, mert ez a legveszelyesebb runtime-hiba, hanem mert:
- ez a legnagyobb tomegu warning
- direkt rontja a strukturalt adatokba vetett bizalmat
- minden futas elejen zajosan ujra megjelenik

Masodik hullamban:

2. `unknown_enum_value:idotartam_felismerve:trap`
3. `unknown_enum_value:zona_felismerve:burst`
4. `unknown_enum_value:kulcsszavak_felismerve:trap`
5. `unknown_enum_value:hatascimkek:trap`

Ezek mar kifejezetten standard-fidelity problemak.

## Top 5 prioritasi lista

### 1. `suspicious_field_combination:idotartam_hatascimke_nelkul`
- darab: `61`
- prioritasi ok: a legnagyobb tomegu, kozvetlenul rontja a strukturalt tesztkepbe
  vetett bizalmat
- gyakorlati kar: nem egyertelmu, hogy a kartya valodi tartamos hatast hordoz-e

### 2. `unknown_enum_value:idotartam_felismerve:trap`
- darab: `16`
- prioritasi ok: nyers standard-hiba az `idotartam` mezoben
- gyakorlati kar: a kartya strukturalt olvasata felrecsuszhat

### 3. `legacy_internal_value:trigger_felismerve:on_play`
- darab: `15`
- prioritasi ok: runtime-kompatibilis lehet, de canonical szemszogbol regi trigger
- gyakorlati kar: bizonytalan, hogy teszt kozben a canonical vagy a legacy kepet
  nezzuk

### 4. `unknown_enum_value:zona_felismerve:burst`
- darab: `12`
- prioritasi ok: hibas zonaval a kartya rossz mechanikai bucketbe kerulhet
- gyakorlati kar: coverage-es feature-prioritas torzulhat

### 5. `unknown_enum_value:kulcsszavak_felismerve:trap` / `hatascimkek:trap`
- darab: `8 + 8`
- prioritasi ok: a `trap` rossz mezobe kerulve felrevezeti a strukturalt
  mechanikai kepet
- gyakorlati kar: tesztprogramban rossz kep alakulhat ki arrol, hogy mi keyword,
  mi effect, es mi triggerelt csapda-viselkedes

## Gyakorlati dontes

Ha a cel a tesztprogram hasznanak novelesE kis munkaval, akkor:

- eloszor a `duration without effect tag` zajt kell kivezetni vagy legalabb
  kulon, alacsonyabb prioritasu bucketbe tenni
- utana a tenylegesen veszelyes `unknown_enum_value` tokeneket kell kezdeni
  tisztazni

Nem erdemes most mindent egyszerre javitani.
A tesztprogram-szempontu sorrend fontosabb, mint a teljes adatminosegi
nagytakaritas.

## Friss allapot - celzott pontositas

Egy szuk validator-pontositas mar bekerult erre a blokkra:

- a `keyword-only static entity` minta mar nem kap
  `idotartam_hatascimke_nelkul` warningot

Ez a minta a gyakorlatban ilyen volt:
- `Entitas`
- `trigger_felismerve=static`
- `idotartam_felismerve=static_while_on_board`
- van `kulcsszavak_felismerve`
- nincs `hatascimkek`

Tesztprogram-szempontbol ez inkabb passziv keyword-leiras volt, nem valodi hibas
mezokombinacio. Emiatt ez a warning-blokk jelentosen csokkent anelkul, hogy a
valodi `duration without effect tag` eseteket elengednenk.
