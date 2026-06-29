## AETERNA — Python motor / új architektúra hatékonysági vizsgálat v0.1

Ez még **nem végleges technológiai döntés**, hanem első diagnózis. A mostani vizsgálat alapján már lehet dolgozni, de **nem javaslom még kimondani**, hogy „Python marad” vagy „újraírjuk az egészet”.

A rövid eredmény:

**A jelenlegi Python motor értékes referencia és működő tesztalap, de jelen formájában nem tekinteném végleges játékprogram-architektúrának.**
A legjobb következő lépés nem az azonnali újraírás, hanem egy célarchitektúra-terv + összehasonlító technikai vizsgálat: mit érdemes megtartani, mit kell átalakítani, és mit lenne jobb új alapokra írni.

---

# 1. Mit néztem most?

Három forrásréteget vettem figyelembe:

1. A v0.2 döntési térképet és a válaszaidat.
2. A projektirányító dokumentumokat.
3. A GitHubon lévő jelenlegi Python kódszerkezetet.

A README szerint a jelenlegi projekt Python alapú szimulátor és szabálymotor, amelynek fő céljai között szerepel az AI-vs-AI teszt, a structured kártyaadatok engine-oldali használata és a motor stabilizálása.  Ez jól illik a jelenlegi állapothoz, de nem teljesen ugyanaz, mint a te új célod: **játékprogram-architektúra Godot-kompatibilis irányban**.

---

# 2. Jelenlegi motor állapota

## 2.1 Van működő hivatalos futási út

A projekt architektúra-dokumentuma szerint a jelenlegi aktív futási lánc:

`main.py → simulation/config.py → engine/logging_utils.py → simulation/runner.py → engine/effect_diagnostics_v2.py → data/loader.py → engine/game.py`

Ez azt jelenti, hogy nem szétesett, teljesen azonosíthatatlan rendszerről beszélünk. Van egy dokumentált, működő mag.

**Következtetés:**
Ez erős érv amellett, hogy a jelenlegi rendszert ne dobjuk ki vakon.

---

## 2.2 A motor már elindult az exportalapú működés felé

A `main.py` már két adatforrással számol: `cards.xlsx` és `EXPORT_RUNTIME.jsonl`.  A program induláskor a JSONL fájlt választja, ha létezik, különben visszaesik az XLSX-re.

Ez nagyon fontos, mert a te új irányod egyik alapja az, hogy a program ne közvetlenül a régi `cards.xlsx`-ből, hanem exportokból dolgozzon.

**Következtetés:**
Az exportalapú adatút nem nulláról indul. Már van működő alap, amit vagy tovább lehet vinni, vagy át lehet emelni egy új architektúrába.

---

## 2.3 Van kezdeti backend/frontend contract

Külön pozitívum, hogy már létezik `BACKEND_FRONTEND_MINIMAL_CONTRACT.md`. Ez kifejezetten azt rögzíti, hogy a jelenlegi minimális backend-felületet egy későbbi Godot vagy más frontend fogyaszthassa.

A dokumentum szerint a jelenlegi minimális backend képes:

* új meccset indítani,
* gépileg fogyasztható snapshotot adni,
* legal actionöket visszaadni,
* action requestet validálni,
* néhány actiont végrehajtani,
* rövid event logot adni.

Ez pontosan abba az irányba mutat, amit a v0.2-ben megfogalmaztunk: snapshot, legal actions, apply action, event log, AI step.

**Következtetés:**
A Python motor nem csak régi szimulátor; már van benne egy kezdeti frontend-kompatibilis backend-váz.

---

# 3. Fő problémák és korlátok

## 3.1 A backend-contract még nagyon minimális

A meglévő contract hasznos, de nem teljes játékprogram-alap. A dokumentáció szerint jelenleg a legal action és execution szinten támogatott actionök:

* `end_turn`,
* `play_entity`,
* `play_trap`.

Az `action_request.py` is ezt erősíti meg: a támogatott action típusok csak `end_turn`, `play_entity`, `play_trap`.

**Ez nem hiba**, hanem állapotjelzés.

**Következtetés:**
A backend-váz jó prototípus, de még nem elég AI vs játékos vagy játékos vs játékos alapnak. Spell execution, targeting, combat action, teljes trap aktiválás és részletes event-rendszer még külön fejlesztési kérdés.

---

## 3.2 A legal action rendszer jelenleg szűk

A `legal_actions.py` alapján a rendszer jelenleg főleg az alap kijátszási lehetőségeket kezeli: kör vége, Entitás kijátszása Horizontba vagy Zenitbe, Jel lerakása Zenitbe.

Ez AI vs AI alapteszthez és frontend-prototípushoz jó, de még nem elég egy teljes játékhoz.

**Következtetés:**
Ez az egyik legfontosabb döntési pont: ha a Python motor marad, akkor a legal action rendszert jelentősen bővíteni kell. Ha új architektúra készül, akkor ezt a meglévő rendszert referencia-mintaként érdemes használni.

---

## 3.3 A snapshot jó irány, de még nem végleges frontend-modell

A `snapshot.py` már exportál gépileg fogyasztható játékállapotot: játékosállapotot, kézméretet, pakliméretet, Pecsét-számot, Ősforrás-lapokat, Horizontot és Zenitet.

Ez Godot felé hasznos alap.

Viszont még kérdéses, hogy ez a snapshot:

* elég-e teljes UI-hoz,
* mennyire stabil a mezőnevezése,
* mennyire kezeli a rejtett információkat,
* alkalmas-e replay / log / PvP állapot-szinkron alapnak,
* elég részletes-e targetinghez és reakcióablakokhoz.

**Következtetés:**
A snapshot-réteget nem kidobni kell, hanem contract-szinten felülvizsgálni.

---

## 3.4 A logolás létezik, de nem azonos a kívánt Error / Warn / Audit rendszerrel

Van logkönyvtár-kezelés és futási log. A `logging_utils.py` év/hónap alapú `LOG` mappát hoz létre, időbélyeges logfájllal.  A log header tartalmazza a startup konfigurációt, engine konfigurációt, run mode-ot, modulokat és flageket.

Ez jó alap, de nem ugyanaz, mint amit a v0.2-ben megfogalmaztunk:

* export validation log,
* runtime error log,
* engine warning log,
* audit warning log,
* balance/test report.

**Következtetés:**
A meglévő logolás megtartható, de fölé vagy mellé kell egy strukturált diagnosztikai rendszer.

---

## 3.5 A jelenlegi architektúra dokumentáltan hibrid

A projekt saját dokumentációja is kimondja a fő kockázatokat: az `engine/effects.py` nagy és több korszak logikáját hordozza; a `game_state/phases/combat` szétválasztás még vékony wrapper-szintű; a `cards/resolver.py` + `cards/priority_handlers.py` működőképes, de erősen név-alapú.

Ez nagyon fontos, mert alátámasztja a te félelmedet: valóban fennáll a veszély, hogy ha csak foltozgatjuk, „szörny” lesz belőle.

**Következtetés:**
A meglévő rendszer értékes, de nem szabad korlátlanul ráépíteni. Kell célarchitektúra, és utána kell eldönteni, mely részek menthetők.

---

# 4. Első hatékonysági értékelés

## 4.1 Ami megtartandó vagy átmentendő jelölt

Ezeket első ránézésre értékesnek tartom:

| Elem                                | Miért értékes?                            | Javasolt státusz               |
| ----------------------------------- | ----------------------------------------- | ------------------------------ |
| JSONL loader / exportalapú betöltés | Illik az új adatút-célhoz                 | átmentendő / továbbvizsgálandó |
| XLSX fallback                       | Fejlesztés alatt hasznos biztonsági réteg | ideiglenesen megtartható       |
| backend facade                      | Már Godot/frontend irányba mutat          | erős átmentési jelölt          |
| snapshot export                     | Kliensoldali alap                         | bővítendő                      |
| legal action alap                   | Jó kezdeti minta                          | jelentősen bővítendő           |
| event log alap                      | Jó irány                                  | strukturálandó                 |
| runtime warningok / enum-validáció  | Illik a Log/Warn/Error célhoz             | bővítendő                      |
| tesztek                             | Fontos biztonsági háló                    | megtartandó                    |

---

## 4.2 Ami refaktor- vagy újraírás-jelölt

| Elem                                 | Probléma                                  | Javasolt státusz                               |
| ------------------------------------ | ----------------------------------------- | ---------------------------------------------- |
| `engine/game.py` központi szerepe    | túl sok felelősség egy helyen             | célzott szétválasztás vagy új engine-core terv |
| `engine/effects.py`                  | dokumentáltan nagy, több korszak logikája | audit + refaktor / részleges újraírás          |
| card-local handlerek                 | név-alapú, nehezen skálázható             | structured/moduláris átvezetés                 |
| spell/targeting/combat action hiánya | frontendhez kevés                         | új action-rendszer-terv                        |
| log rendszer                         | nem elég strukturált diagnosztikához      | új Log/Warn/Error terv                         |
| mixed magyar/angol runtime fogalmak  | Godot/API szinten nehézkes lehet          | canonical contract terv                        |

---

# 5. Előzetes döntés: újraírás vagy megtartás?

Most még nem dönteném el véglegesen.

Viszont a vizsgálat alapján ezt mondanám:

## Nem javasolt út

**Nem javaslom, hogy most azonnal teljes újraírást kezdjünk.**

Indok:

* van működő futási út;
* van JSONL/export irány;
* van minimális backend-contract;
* van snapshot;
* van legal action alap;
* vannak tesztek;
* ezekből sok tanulság és rész menthető.

## Szintén nem javasolt út

**Nem javaslom, hogy a jelenlegi motort automatikusan végleges backendnek tekintsük.**

Indok:

* a rendszer hibrid;
* több wrapper és átmeneti réteg van;
* a card-local handler modell hosszú távon nem skálázható;
* a legal action rendszer még túl szűk;
* a frontend-contract még minimális;
* a log/warn/error rendszer nincs a kívánt szinten.

## Javasolt út

**Célarchitektúra-terv + összehasonlító technikai vizsgálat.**

Ez azt jelenti:

1. Megtervezzük, milyen lenne az ideális AETERNA backend Godot-kompatibilis szemmel.
2. Ezt összevetjük a jelenlegi Python motorral.
3. Megjelöljük:

   * mi menthető át,
   * mi refaktorálandó,
   * mi maradhat ideiglenes referenciának,
   * mit érdemes újraírni.
4. Csak ezután döntünk Python megtartásról, részleges újraírásról vagy új architektúráról.

---

# 6. Első vizsgálati eredmény státuszokkal

| Kérdés                               | Első válasz                                        | Státusz         |
| ------------------------------------ | -------------------------------------------------- | --------------- |
| Van működő motor?                    | Igen                                               | biztos          |
| Van exportalapú irány?               | Igen, JSONL-first már megjelent                    | biztos          |
| Van Godot/frontend irányú kezdemény? | Igen, minimális backend-contract van               | biztos          |
| Elég ez teljes játékprogramhoz?      | Nem                                                | biztos          |
| Érdemes mindent kidobni?             | Nem vakon                                          | biztos          |
| Érdemes mindent megtartani?          | Nem                                                | biztos          |
| Python maradhat?                     | Lehetséges                                         | vizsgálati kapu |
| Újraírás lehet jobb?                 | Lehetséges                                         | vizsgálati kapu |
| Következő lépés kódolás?             | Nem nagy refaktor, hanem célarchitektúra-vizsgálat | javasolt        |

---

# 7. Javasolt következő konkrét munka

A következő lépés szerintem ez legyen:

## AETERNA — Célarchitektúra összehasonlító vizsgálat v0.1

Ebben 4 modellt hasonlítanánk össze:

### A modell — Python motor megtartása backendként

A jelenlegi motort fokozatosan backenddé alakítjuk.

Előny:

* kevesebb azonnali újraírás;
* meglévő működés megmarad;
* tesztek és loader-réteg használhatók.

Kockázat:

* tovább nőhet a hibrid szerkezet;
* nehéz lehet tiszta Godot-contractot építeni rá;
* card-local és régi effect logika tovább húzhatja.

---

### B modell — Python motor mint referencia, új backend-architektúra Pythonban

Új, tisztább Python backend készül, a régiből átmentett modulokkal.

Előny:

* tisztább szerkezet;
* megmaradhat Python és a meglévő tudás;
* könnyebb célarchitektúrához igazítani.

Kockázat:

* több munka;
* átmenetileg két rendszer létezhet;
* pontos migrációs terv kell.

---

### C modell — Új backend más technológiával, Python referencia mellett

A Python motor referencia és tesztmotor marad, de a hosszú távú backend más technológiával készül.

Előny:

* lehet, hogy jobban illik Godothoz vagy játékprogramhoz;
* tiszta új alap.

Kockázat:

* nagy újraírás;
* több ismeretlen;
* több Codex- és tesztmunka;
* könnyű elveszteni a már működő szabályrészleteket.

---

### D modell — Hibrid átmenet

Rövid távon Python motor marad AI-vs-AI tesztre, közben új backend-contract / adatút / validation rendszer épül.

Előny:

* biztonságos;
* nem áll meg a tesztelés;
* közben tervezhető az új rendszer.

Kockázat:

* ha túl sokáig tart, fenntartja a hibrid állapotot.

---

# 8. Első ajánlás

Mostani állapot alapján én **D → B irányt** tartanék a legbiztonságosabbnak.

Vagyis:

1. **Rövid távon:** a Python motor marad működő referencia és AI-vs-AI tesztalap.
2. **Közben:** megtervezzük a tiszta célarchitektúrát.
3. **Utána:** eldöntjük, hogy az új célarchitektúra:

   * a jelenlegi Python motor refaktorából,
   * vagy egy új, tisztább Python backendből,
   * vagy más technológiából épüljön.
4. **Semmit nem törlünk / írunk újra vakon.**

Ez jobban illik ahhoz, amit mondtál: ne foltozzunk szörnyet, de ne is dobjunk el hasznos működő részeket.

---

# 9. Következő döntési pont

A következő munkához ezt a kérdést kell eldönteni:

**Készítsek-e egy részletes „Célarchitektúra összehasonlító vizsgálat v0.1” dokumentumot, amelyben a fenti A/B/C/D modelleket pontról pontra összevetjük Godot, exportok, LOOKUPS, Log/Warn/Error, modularitás, Codex-kezelhetőség és kártyaaudit szempontból?**

Szerintem ez legyen a következő lépés, mert ez vezet el ahhoz, hogy ne érzés alapján döntsünk az újraírásról, hanem összehasonlítható szempontok alapján.
