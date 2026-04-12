# AETERNA - Backend Readiness Audit

Ez a rovid audit a jelenlegi backend-elokeszito retegek gyakorlati allapotat rogzitI.

CeljA:
- megmondani, mire eleg a mostani backend-vaz
- kijelolni a kovetkezo egyetlen legjobb technikai lepest

Ez nem uj mechanikai batch, nem teljes API-terv, es nem hosszU elmeleti anyag.

## 1. Jelenlegi backend-lanc

### Snapshot
- mire jo most:
  - gepileg fogyaszthato allapotkepet ad a meccsrol es a ket jatekosrol
  - frontend oldalon mar kirajzolhato belole egy alap board + hand + seal allapot
- fo korlat:
  - nincs kulon event vagy delta reteg
  - csak allapotkepet ad, de nem mondja meg, mi valtozott ket snapshot kozott
- Godot-hasznalhatosag:
  - jo alap
  - onmagaban mar hasznalhato egyszeru allapot-megjeleniteshez

### Facade
- mire jo most:
  - van stabil backend-belepesi pont match letrehozasra, snapshotra, resultra, legal-actionsre, validaciora es minimalis apply-re
- fo korlat:
  - a vegrehajtas meg nagyon szuk
  - meg nincs valodi jatekos-akcio paletta
- Godot-hasznalhatosag:
  - jo szerkezeti alap
  - mar nem kell a frontendnek kozvetlenul a runtime belso objektumait ismernie

### Legal actions
- mire jo most:
  - vissza tudja adni a legegyszerubb, backend-kompatibilis akciokat
  - `end_turn`, egyszeru `play_entity`, egyszeru `play_trap`
- fo korlat:
  - nem teljes action-rendszer
  - nincs spell, targeting, combat vagy triggerelt dontes
- Godot-hasznalhatosag:
  - prototipus szinten hasznalhato
  - kezdeti UI-gombokhoz es egyszeru valaszthato akciokhoz eleg lehet

### State context
- mire jo most:
  - explicit `active_player`, `phase`, `match_finished` allapot van
  - a backend mar nem teljesen implicit kovetkeztetesekbol dolgozik
- fo korlat:
  - a phase csak fo fazis-szintu jelzes
  - nem teljes action-window modell
- Godot-hasznalhatosag:
  - fontos es hasznos
  - ezzel lehet kulturaltan tiltani vagy engedni frontend-akciokat

### Action request / validation
- mire jo most:
  - van stabil, gepileg fogyaszthato action-request forma
  - a frontend mar tud szabalyos requestet kiallitani
  - a backend meg tudja mondani, hogy egy request legalis-e
- fo korlat:
  - csak nehany action tipust fed le
  - meg nincs szorosan a vegrehajtasi reteggel osszekotve
- Godot-hasznalhatosag:
  - eros alap
  - mar van tiszta szerzodes a kesobbi action-submit iranyhoz

### apply_action
- mire jo most:
  - van elso valodi vegrehajtasi kapu
  - `end_turn` tenylegesen futtathato
- fo korlat:
  - a jatekos szamara erdemben fontos board-akciok meg nem vegrehajthatok
  - jelenleg a backend inkabb allapotot mutat es validal, mint jatszhato interakciot ad
- Godot-hasznalhatosag:
  - fontos alap, de meg nem eleg egy minimalis jatszhato klienshez

## 2. Mi hianyzik meg a minimalis jatszhato frontendhez

Az elso minimalis jatszhato frontendhez legalabb ezek kellenek:

1. egyszeru kezbol kijatszas tenyleges vegrehajtasa
   - ma ez a legnagyobb hiany
   - legal-actions es validation mar ismeri, de apply oldalon nincs bekotve

2. kovetkezetes action visszaigazolas
   - az apply mar ad eredmenyt, de ez meg csak az `end_turn`-re relevans

3. allapotfrissites akcio utan
   - ez mar jo iranyban megvan, mert az apply snapshotot ad vissza

4. jobb hibauzeneti konzisztencia
   - az alap mar megvan, de a valodi kijatszhato akcioknal lesz igazan fontos

5. kesobbi esemenykovetes
   - jelenleg nincs kulon event/delta buffer
   - ez hasznos lenne, de nem ez a legjobb azonnali kovetkezo lepes

## 3. Kovetkezo egyetlen legjobb technikai lepes

### Valasztott kovetkezo lepes
- `play_entity` execution boundary

### Miert ez a legjobb most

Ez adja most a legnagyobb hasznot a legjobb kockazat/ertek arannyal, mert:

1. mar minden elozo reteg elokeszitette:
   - van snapshot
   - van facade
   - van legal-actions
   - van state context
   - van action request / validation
   - van apply boundary

2. a `play_entity` mar ma is:
   - latszik a legal-actions listaban
   - validalhato requestkent
   - frontend-szempontbol termeszetes, alap akcio

3. a minimalis jatszhato klienshez ez tobbet ad, mint barmelyik masik mostani irany:
   - `play_trap` kevesebb azonnali frontend-haszon
   - event/delta buffer hasznos, de meg nem teszi jatszhatobba a klienst
   - action-result tisztitas onmagaban kevesebb gyakorlati nyereseg
   - spell action elokeszites nagyobb kockazat

### Mire kell figyelni a kovetkezo korben

A `play_entity` execution kort tovabbra is szuken kell tartani:
- csak egyszeru kezbol kijatszas
- csak egyertelmu `zone` + `lane`
- csak a shared summon/helper utakra tamaszkodva
- spell, targeting es trap execution nelkul

## 4. DONTESI OSSZEFOGLALO

Ha a cel egy kesobbi Godot-kompatibilis, kezdetben mar jatszhato rendszer, akkor a jelenlegi backend-vaz utan a legjobb kovetkezo egyetlen lepes:

- `play_entity` tenyleges execution-boundary bekotese az `apply_action(...)` ala

Ez az a pont, ahol a backend eloszor lep at a "meg tudja mondani, mi lehetseges" allapotbol a "a jatekos mar tenylegesen le tud rakni egy lapot" allapotba.

## 5. Statuszfrissites

Ez a kovetkezo lepes mar elkeszult:

- a minimalis `play_entity` execution-boundary bekotese megtortent

Az uj legjobb kovetkezo lepes emiatt mar valoszinuleg ezek kozul kerul ki:
- `play_trap` execution, ha tisztan megfogható marad
- action-result konzisztencia finomitasa
- kesobbi event/delta buffer elokeszites

De a sorrend tovabbra is csak kis-kockazatu, fokozatos backend-epites lehet.

## 6. Statuszfrissites 2

Az action-result konzisztencia finomitasa is megtortent:

- az `apply_action(...)` stabilabb, egysegesebb valaszszerzodest ad
- az `end_turn` es a `play_entity` most mar azonosabb `result` alakot hasznal

Ez csokkenti annak az eselyet, hogy a kesobbi frontend oldalon action-tipusonkent
kulon adhoc valaszfeldolgozasra legyen szukseg.

## 7. Statuszfrissites 3

A backend most mar minimalis action-utani esemenylistat is ad a mar mukodo akciokhoz.

Ez azt jelenti, hogy a frontend mar:
- nem csak teljes snapshotot kap
- hanem rovid, action-utani jelentest is arrol, hogy mi tortent

Ez meg nem teljes delta vagy event bus, de jo atmeneti reteg a kesobbi frontendhez.
