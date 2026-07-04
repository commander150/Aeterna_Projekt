# AETERNA Game Engine – Runtime Package Specification

Ez a dokumentum az AETERNA Game Engine runtime package rétegének fő specifikációs váza.

Nem hivatalos szabálykönyv.

Nem kártyaadatbázis.

Nem nyers exportleírás.

Nem teljes rules engine specifikáció.

Feladata, hogy leírja, hogyan lesz az ember által szerkesztett AETERNA adatforrásokból programbiztos, validált, Python és Godot/GDScript által fogyasztható runtime package.

Kapcsolódó fő dokumentumok:

- DECISION_MAP.md
- ARCHITECTURE.md
- TECHNOLOGY_DECISIONS.md
- CONTRACT_SPECIFICATION.md
- ABILITY_MODULE_SYSTEM.md
- OPEN_QUESTIONS.md
- CHECKPOINTS.md
- PROTOTYPE_PLANS.md

---

## 1. Alapelv

A runtime package az AETERNA digitális rendszer programfogyasztásra előkészített adatcsomagja.

Nem azonos:

- a Google Sheets szerkesztési forrással;
- a lokális XLSX fájlokkal;
- az exportáló program source másolataival;
- a nyers JSONL / CSV exportokkal;
- a hivatalos szabályforrásokkal;
- a Godot project belső scene-jeivel;
- a Python motor belső objektumaival.

A runtime package célja:

- stabil adatátadási forma;
- validált kártyaadatok;
- validált deckadatok;
- lookup és alias információk;
- ability registry;
- engine support információ;
- diagnostics;
- Godot/GDScript loader fogyasztás;
- Python tesztmotor / validátor / AI későbbi fogyasztás;
- reproducibilis fejlesztői és tesztkörnyezet.

---

## 2. Adatút áttekintése

A jelenlegi elfogadott adatút:

    Google Sheets
      ↓
    lokális XLSX export / letöltött munkaforrás
      ↓
    exportáló program
      ↓
    nyers exportok
      ↓
    validáció / normalizálás
      ↓
    runtime package build
      ↓
    Python / Godot / AI / debug / teszt fogyasztás

A runtime package tehát nem a szerkesztési forrás, hanem a szerkesztési forrásból származtatott futási adatcsomag.

---

## 3. Szerkesztési források

Jelenlegi elfogadott irány:

- A fő szerkesztés Google Sheetsben történik.
- A lokális XLSX fájl a Google Sheetsből letöltött helyi munkaforrás.
- Az XLSX export mappán belüli XLSX fájlok pipeline input másolatok.
- Az XLSX export mappában lévő XLSX fájlok nem elsődleges canonical szerkesztési források.
- Az exportáló később tudjon közvetlenül canonical lokális forrásmappából dolgozni.

Fontos következmény:

A runtime package builder ne abból induljon ki, hogy az XLSX export/source mappa a végleges forrás.

A hosszú távú cél az, hogy az exportáló konfigurálható bemeneti forrásból dolgozzon.

---

## 4. Szerkesztési forrás és runtime adat elválasztása

A szerkesztési forrás emberi munkára optimalizált.

Tartalmazhat:

- workflow mezőket;
- audit státuszokat;
- megjegyzéseket;
- részben feldolgozatlan structured értékeket;
- régi aliasokat;
- átmeneti értékeket;
- nyomdai / termék / pakli metaadatokat;
- javítás alatt álló kártyákat.

A runtime package programfutásra optimalizált.

Nem tartalmazhat tisztázatlanul:

- workflow-only értéket runtime mezőben;
- ismeretlen enum értéket;
- veszélyes legacy aliast;
- Aeternal/Pecsét HP-modellből származó régi hatáslogikát;
- hiányzó kötelező runtime mezőt;
- nem validált többértékű structured mezőt;
- olyan kártyahatást, amely engine-supported státusz nélkül futtatásra kerülne.

---

## 5. Nyers exportok szerepe

A nyers exportok köztes réteget képeznek.

Lehetséges formátumok:

- JSONL
- JSON
- CSV
- TSV

A jelenlegi gyakorlat alapján a runtime kártyaadatoknál a JSONL jól használható forma.

A nyers exportok célja:

- gépi feldolgozás előkészítése;
- ellenőrizhető pipeline output;
- exportáló hibáinak vizsgálata;
- runtime package build inputja;
- debug és audit támogatása.

A nyers export nem feltétlenül végleges runtime input.

Hosszú távú irány:

- a nyers export regenerálható legyen;
- a runtime package legyen a tényleges programinput;
- bizonyos nyers exportok maradhatnak referencia-outputként, ha hasznosak teszteléshez vagy auditáláshoz.

---

## 6. Runtime package célja

A runtime package célja, hogy egy adott AETERNA adatállapotot programbiztos, verziózott, validált formában adjon át.

A package legyen:

- determinisztikusan előállítható;
- schema-verziózott;
- géppel olvasható;
- Godot által betölthető;
- Python által feldolgozható;
- diagnostics-szal ellátott;
- smoke testelhető;
- lehetőség szerint reprodukálható;
- hosszú távon összehasonlítható más package verziókkal.

---

## 7. Jelenlegi sample runtime package

A jelenlegi sample runtime package már működő technikai checkpointtal rendelkezik.

A sample package fájljai:

- manifest.json
- cards.jsonl
- decks.jsonl
- lookups.json
- aliases.json
- ability_registry.json
- engine_support.json
- diagnostics.json
- build_report.md

A sample package jelenlegi ismert összefoglalója:

- cards: 5
- decks: 1
- lookup_groups: 2
- ability_modules: 2
- warnings: 1
- blocking_errors: 0
- validation blocking: false

Ez a sample package nem teljes AETERNA runtime package.

A szerepe:

- adatút bizonyítása;
- Godot loader tesztelése;
- registry-k ellenőrzése;
- diagnostics minta;
- sample contracts kapcsolat előkészítése;
- későbbi smoke tesztek alapja.

---

## 8. Package mappahelyek

Jelenlegi működő Godot fogyasztási hely:

- Aeterna game engine/Godot/sample_runtime_package/

Godot loader útvonal:

- res://sample_runtime_package

Python oldalon a sample generator saját outputot is előállíthat.

Rövid távon elfogadható:

- Python oldali sample output;
- Godot oldali fogyasztási másolat.

Hosszú távú nyitott kérdés:

- a Python builder közvetlenül a Godot fogyasztási mappába írjon;
- vagy külön build output mappába írjon, ahonnan másolás történik;
- vagy package registry / release mappa legyen.

Ajánlott hosszú távú elv:

A Godot projectben lévő package fogyasztási példány ne legyen kézzel szerkesztett canonical adatforrás.

---

## 8.1. Fejlesztői build pipeline és sample package mappák kezelése

A jelenlegi AETERNA Game Engine prototípus több lépcsőben kezeli az adatutat:

1. XLSX forrásokból export készül.
2. Az exportált adatokból runtime package készül.
3. A runtime package átkerül vagy elérhetővé válik a Godot által fogyasztott mappában.
4. A Godot loader ebből tölti be a kártyákat, deckeket, lookupokat, ability registryt és diagnostics adatokat.

Ez a többfokozatú felépítés a korai tesztfázisban hasznos volt, mert minden lépés külön ellenőrizhető volt.

Hosszabb távon viszont a fejlesztői használatban nem cél, hogy minden alkalommal több külön kézi lépést kelljen futtatni.

A cél ezért nem az adatút eldobása, hanem annak egységesebb, automatizáltabb kezelése.

### Fejlesztői build pipeline irány

Hosszú távon az XLSX exportáló ne különálló aktív programként éljen tovább.

Az exportáló funkciói kerüljenek be az `Aeterna game engine/python/` alatti tooling / build pipeline rétegbe.

A Python build pipeline feladata legyen:

- XLSX források beolvasása;
- exportprofilok futtatása;
- nyers exportok előállítása;
- validáció;
- normalizálás;
- diagnostics generálás;
- runtime package build;
- szükség esetén a Godot által fogyasztott package-mappa frissítése.

A Godot továbbra se olvasson közvetlenül XLSX-et.

A Godot feladata a validált runtime package fogyasztása marad.

A runtime package maradjon a Python tooling és a Godot közötti tiszta adatcontract-határ.

### Miért ne a Godot olvassa az XLSX-et?

Az XLSX emberi szerkesztési forma, nem runtime formátum.

A Godot loadernek nem kell Excel-szerű adatforrásokat értelmeznie.

Ez több okból fontos:

- a Godot loader egyszerűbb marad;
- az XLSX-specifikus hibák a Python validációs rétegben kezelhetők;
- a runtime package ugyanúgy használható Godot, Python tesztek, AI és későbbi simulation számára;
- későbbi publikusabb verzióban nem kell nyers szerkesztési XLSX fájlokat a játék mellé adni;
- a package schema és diagnostics réteg tiszta határként működhet.

### Egylépéses fejlesztői build

A hosszabb távú fejlesztői cél egy olyan build pipeline, amely kívülről egyetlen műveletként használható.

Példa fejlesztői működés:

1. A fejlesztő frissíti vagy letölti az aktuális XLSX forrásokat.
2. Elindít egy build parancsot vagy BAT fájlt.
3. A Python build pipeline ellenőrzi, változott-e az input.
4. Ha szükséges, újragenerálja a nyers exportokat.
5. Validálja és normalizálja az adatokat.
6. Elkészíti a runtime package-et.
7. Frissíti a Godot által fogyasztott package-mappát.
8. Diagnostics / build report jelzi, hogy volt-e warning vagy blocking error.

Ez belsőleg továbbra is több lépésből állhat, de fejlesztői használatban egyetlen folyamatként jelenjen meg.

### Változásérzékelés és cache

A build pipeline később tartalmazhat változásérzékelést.

Cél:

- ha az XLSX input és a build konfiguráció érdemben nem változott, ne készüljön új export és új runtime package;
- ha az XLSX, LOOKUPS, exportprofil, schema vagy builder verzió változott, a pipeline automatikusan újrageneráljon.

Első egyszerű megoldásként használható fájl-időbélyeg vagy fájl-hash.

Hosszabb távon jobb megoldás lehet egy érdemi `source_fingerprint`, amely nem a teljes XLSX bináris fájlt, hanem az exportált szempontból fontos tartalmat azonosítja.

A fingerprint figyelembe veheti:

- releváns XLSX fájlok;
- releváns sheetek;
- használt oszlopok;
- cellaértékek;
- exportprofil verzió;
- LOOKUPS verzió;
- builder verzió;
- runtime package schema verzió.

A cache nem elsődleges MVP-követelmény, de a mappaszerkezetet úgy kell kialakítani, hogy később beépíthető legyen.

### Fejlesztői, baráti teszt és publikus mód

A projekt jelenlegi célja nem publikus kiadás, hanem saját és baráti tesztelés.

Ezért rövid távon nem elsődleges probléma, ha a tesztelők hozzáférnek bizonyos fájlokhoz vagy módosítani tudják őket.

Későbbi publikus verziónál viszont már fontosabb lesz a nyers szerkesztési források és a runtime package szétválasztása.

Javasolt módok:

| Mód | Javasolt működés |
|---|---|
| Fejlesztői mód | XLSX-ből automatikus runtime package build engedélyezett. |
| Baráti teszt mód | Előre generált runtime package használható, erős védelem nélkül. |
| Publikus mód | A játék ne tartalmazza a nyers szerkesztési XLSX forrásokat, csak verziózott runtime package-et. |
| Későbbi publikus mód | Package hash, integritás-ellenőrzés vagy read-only asset kezelés is bevezethető. |

### A két sample_runtime_package mappa kezelése

Jelenleg két `sample_runtime_package` mappa létezik:

- Python oldali `sample_runtime_package`
- Godot oldali `sample_runtime_package`

Ezek nem egyenrangú canonical források.

A javasolt hosszú távú értelmezés:

- a Python oldali `sample_runtime_package` a build pipeline által előállított generált output / tesztfixture;
- a Godot oldali `sample_runtime_package` a Godot loader által fogyasztott másolat / runtime fixture;
- egyik sem kézzel szerkesztendő canonical kártyaadatforrás;
- a canonical kártyaadatok továbbra is a szerkesztési forrásokból, például Google Sheetsből letöltött XLSX fájlokból származnak;
- a Godot oldali package frissítése a Python build pipeline feladata legyen.

Rövid távon elfogadható, hogy a két mappa egyszerre létezik, mert fejlesztés és smoke test szempontból külön szerepük van.

Hosszabb távon viszont dönteni kell, hogy:

1. a Python build output és a Godot fogyasztási mappa külön marad;
2. a Python builder közvetlenül a Godot fogyasztási mappába is tud írni;
3. vagy egy központi generated package mappa jön létre, ahonnan a Godot csak másolatot kap.

Ajánlott irány:

- maradjon külön a build output és a Godot consumption copy;
- a másolást / frissítést a build pipeline végezze;
- a Godot oldali `sample_runtime_package` ne legyen kézzel módosított adatforrás;
- a package manifest vagy build report jelezze, miből és mikor készült a package;
- később a pipeline ellenőrizze, hogy a Godot oldali másolat egyezik-e a Python build outputtal.

### Javasolt package-státuszok

A két package-mappa és a kapcsolódó outputok javasolt státuszai:

| Elem | Javasolt státusz |
|---|---|
| Python oldali `sample_runtime_package` | `GENERATED_TEST_FIXTURE` |
| Godot oldali `sample_runtime_package` | `GODOT_CONSUMPTION_COPY` |
| Godot oldali `sample_contracts` | `HAND_AUTHORED_TEST_FIXTURE` |
| XLSX exportból készült nyers JSONL outputok | `GENERATED_OUTPUT` |
| régi `XLSX export/source` másolatok | `PIPELINE_INPUT_COPY` |
| régi külön `XLSX export` program | `OBSOLETE_AFTER_MIGRATION`, ha a funkció átkerült az új Python tooling alá |

### Nem cél az első lépésben

Az első pipeline-rendezési lépésben még nem cél:

- teljes cache-rendszer;
- teljes publikus release pipeline;
- Godotból indítható Python rebuild gomb;
- runtime package titkosítás vagy védelem;
- teljes full card database package;
- a régi Python engine beolvasztása;
- a Godot közvetlen XLSX-betöltése.

Első cél:

- az exporter funkció áthelyezése az új Python tooling alá;
- explicit source és output útvonalak támogatása;
- újabb állandó input-másolatok elkerülése;
- Python oldali build output és Godot oldali consumption copy szerepének tisztázása;
- későbbi egylépéses build pipeline előkészítése.

---

## 9. Package típusok

Lehetséges runtime package típusok:

- sample runtime package;
- development runtime package;
- test runtime package;
- full card database runtime package;
- deck test package;
- balance simulation package;
- release candidate package;
- archived reference package.

MVP-ben elég:

- sample runtime package;
- development runtime package.

Később hasznos lehet:

- külön AI-vs-AI test package;
- külön starter deck test package;
- külön rules regression test package.

---

## 10. Manifest

A manifest a runtime package belépési pontja.

Feladata:

- package azonosítása;
- schema verzió jelölése;
- package verzió jelölése;
- fájlok felsorolása;
- generálási információk;
- kompatibilitási információk;
- diagnostics summary;
- blocking státusz jelzése.

Ajánlott manifest mezők:

- package_id
- package_version
- schema_version
- generated_at
- generated_by
- source_profile
- source_files
- files
- counts
- diagnostics_summary
- blocking
- compatibility
- metadata

MVP-ben nem minden mező kötelező.

---

## 11. Cards fájl

A cards fájl tartalmazza a runtime kártyaadatokat.

Jelenlegi sample forma:

- cards.jsonl

A JSONL előnye:

- soronként egy kártya;
- nagyobb adatállomány esetén jól kezelhető;
- diffelhetőbb, mint egy nagy JSON tömb;
- streaming feldolgozásra alkalmas;
- hiba esetén sorhoz köthető diagnostics.

Ajánlott card mezők:

- card_id
- print_id
- name_hu
- card_type
- realm
- clan
- rarity
- magnitude
- aura_cost
- atk
- hp
- keywords
- rules_text_hu
- structured_ability
- effect_tags
- target_tags
- timing
- zones
- engine_support_status
- diagnostics
- metadata

A pontos mezők a kártyaadatbázis és runtime contract fejlődésével változhatnak.

---

## 12. Card ID és print ID

A runtime kártya elsődleges szabályi azonosítója:

- card_id

A print vagy termék specifikus azonosító külön kezelendő.

Lehetséges mezők:

- card_id
- print_id
- product_id
- collector_number
- generated_print_id

Fontos elv:

A játéklogika elsődlegesen ne collector number alapján működjön.

A kártya szabályi azonosításának központi eleme a card_id legyen.

---

## 13. Card type canonical értékek

Aktív fő card type értékek:

- entity
- incantation
- ritual
- sigil
- plane

Magyar megfelelőik:

- Entitás
- Ige
- Rituálé
- Jel
- Sík

Fontos:

A spell ne legyen canonical card type.

A spell legfeljebb gyűjtőfogalom lehet Ige + Rituálé értelemben.

---

## 14. Realm, clan és LOOKUPS

A runtime package-ben a realm és clan mezők canonical értékeket használjanak.

A megjelenítési magyar címkék külön lookupból vagy label mezőből származzanak.

Elfogadott LOOKUPS irány:

- Value legyen kódbarát, lehetőleg angol vagy ASCII snake_case;
- Label_HU legyen magyar megjelenítési címke;
- active soroknál Canonical_Value általában egyezzen a Value mezővel;
- Value = Label_HU irány kerülendő;
- legacy aliasok külön rétegben kezelendők.

---

## 15. Numeric mezők

A runtime package-ben a numerikus mezők legyenek normalizáltak.

Példák:

- 1 helyett ne legyen 1.0, ha egész értékről van szó;
- 2 helyett ne legyen 2.0;
- magnitude, aura_cost, atk, hp egész formában jelenjen meg, ha egész érték.

Korábbi tanulság:

A 1.0 / 2.0 jellegű érték valószínűleg exportáló / Excel feldolgozási mellékhatás.

Ezt exportáló vagy normalizáló rétegben kell kezelni.

---

## 16. Üres értékek

Az üres értékek kezelése profilonként eldöntendő.

Általános irány:

- ne kerüljön minden üres cella automatikusan exportba;
- az üres érték, a hiányzó mező és a none nem mindig ugyanaz;
- fix szerkezetű exportoknál a hiányzó mező más jelentést kaphat;
- AETERNA runtime profile esetén érdemes külön szabályt definiálni.

Lehetséges értelmezések:

- missing field;
- explicit none;
- empty string;
- not_applicable;
- unknown;
- audit_required.

Nyitott kérdés:

- melyik mezőnél melyik üresérték-stratégia legyen hivatalos.

---

## 17. Többértékű structured mezők

Elfogadott hosszú távú delimiter irány:

- pontosvessző

A többértékű mezők runtime normalizáláskor listává alakíthatók.

Példa elvi működés:

- source value: "draw; discard"
- runtime value: ["draw", "discard"]

Nyitott kérdés:

- több párhuzamos structured mezőnél hogyan kapcsolódnak az első, második, harmadik értékek egymáshoz;
- mikor kell explicit parameter schema;
- mikor nem elég a delimiteres lista.

---

## 18. Decks fájl

A decks fájl tartalmazza a runtime decklistákat.

Jelenlegi sample forma:

- decks.jsonl

Lehetséges mezők:

- deck_id
- product_id
- deck_name_hu
- deck_type
- format
- cards
- card_id
- quantity
- diagnostics
- metadata

Fontos validációk:

- létező card_id;
- pozitív quantity;
- pakliméret;
- formátum szabály;
- termékhez tartozás;
- duplikációk;
- unsupported kártyák jelzése.

---

## 19. Lookups fájl

A lookups fájl tartalmazza a runtime értékkészleteket.

Jelenlegi sample forma:

- lookups.json

Feladata:

- canonical értékek;
- magyar címkék;
- aktív / inaktív státusz;
- runtime támogatás;
- workflow-only értékek elkülönítése;
- kategóriák;
- validációs szabályok.

Lehetséges lookup mezők:

- group
- value
- label_hu
- canonical_value
- status
- runtime_status
- description_hu
- notes
- metadata

Fontos:

Workflow érték ne keveredjen aktív runtime enumként, ha nem oda tartozik.

---

## 20. Aliases fájl és legacy normalizáció

Az aliases réteg a legacy, alternatív vagy korábbi adatértékek kezelésére szolgál.

Jelenlegi sample forma:

* aliases.json

Fontos aktuális státusz:

A jelenlegi `aliases.json` még nem végleges runtime contract.

Jelenleg:

* sample / fixture eredetű fájl;
* a builder belső mintadataiból készül;
* nem a `LOOKUPS.xlsx` fájlból származik;
* nem a `RUNTIME_LEGACY_ALIAS` sheetből készül;
* a Godot loader jelenleg csak betölti és számszerűsíti;
* tényleges runtime alias-normalizáció még nincs bekötve.

Ezért az `aliases.json` jelenleg nem tekinthető canonical normalizációs forrásnak.

A hosszú távú normalizációs forrásjelölt:

* `Aeterna dokumentációk/LOOKUPS.xlsx`
* sheet: `RUNTIME_LEGACY_ALIAS`

A `RUNTIME_LEGACY_ALIAS` célja:

* legacy értékek felismerése;
* korábbi terminológia kezelése;
* alternatív vagy régi exportértékek azonosítása;
* canonical értékre normalizálható sorok elkülönítése;
* auditot igénylő sorok jelzése;
* veszélyes vagy nem automatikusan javítható értékek kiszűrése.

Fontos szabály:

A `RUNTIME_LEGACY_ALIAS` tartalmát nem szabad vakon az `aliases.json` fájlba önteni.

Különösen fontos, hogy az `audit_required` canonical értékű sorok nem automatikus runtime mappingek. Ezek emberi ellenőrzést, döntést vagy diagnostics jelzést igényelnek.

Jelenlegi fejlesztői állapot:

* a `runtime_legacy_aliases_reader.py` külön olvassa a `RUNTIME_LEGACY_ALIAS` sheetet;
* a reader külön jelöli, hogy egy alias automatikusan normalizálható-e;
* a reader külön jelöli, ha audit szükséges;
* a reader még nem ír runtime package outputot;
* a reader még nincs bekötve a publish pipeline-ba;
* a reader kimenete még nem váltja ki az `aliases.json` fájlt.

Lehetséges jövőbeli alias / normalizációs mezők:

* lookup_group
* alias_value
* label_hu
* canonical_value
* status
* used_for
* sort_order
* source
* notes
* requires_audit
* normalization_allowed
* diagnostic_code
* danger_level

Nyitott döntési pont:

* maradjon-e az `aliases.json` név, de új sémával;
* vagy készüljön külön `normalization_aliases.json`;
* vagy készüljön külön `legacy_aliases.json`;
* vagy a legacy alias adat részben diagnostics / audit input legyen;
* mikor javíthat automatikusan a pipeline;
* mikor kell emberi audit;
* mikor legyen blocking error.

Előzetes ajánlott irány:

* az `aliases.json` jelenlegi formája maradjon sample / placeholder státuszban;
* a valódi legacy normalizációhoz később külön, egyértelműbb nevű runtime package fájl készüljön, például `normalization_aliases.json`;
* a publish pipeline-ba csak akkor kerüljön be, ha a séma és az auditkezelés eldőlt.

---

## 21. Ability registry fájl

Az ability registry az ability/effect module rendszer előkészítő rétege.

Jelenlegi sample forma:

- ability_registry.json

Feladata:

- ability module-ok azonosítása;
- support státusz jelzése;
- engine által támogatott és nem támogatott hatások elválasztása;
- card-local fallback jelzése;
- effect module mapping előkészítése;
- Godot és Python közös ability support információja.

Lehetséges mezők:

- ability_id
- source_card_id
- module_id
- ability_type
- trigger
- conditions
- targets
- cost
- effects
- duration
- limits
- support_status
- execution_mode
- diagnostics

A részletes ability logic az ABILITY_MODULE_SYSTEM.md fájlba tartozik.

---

## 22. Engine support fájl

Az engine_support fájl megmondja, hogy az adott kártya vagy ability mennyire futtatható a jelenlegi engine állapotban.

Jelenlegi sample forma:

- engine_support.json

Lehetséges support státuszok:

- supported
- partial
- unsupported
- not_checked
- fallback_required
- manual_review_required

Feladata:

- futtathatóság jelzése;
- kártyák blokkolási státusza;
- ability modulok támogatottsága;
- későbbi AI-vs-AI és Godot runtime előszűrés;
- diagnostics és audit támogatása.

Nyitott kérdések:

- unsupported kártya mikor blokkolja a package buildet;
- deckben szereplő unsupported kártya szigorúbb legyen-e;
- partial státusz warning, audit_note vagy non-blocking error legyen-e;
- fallback mikor engedhető.

---

## 23. Diagnostics fájl

A diagnostics fájl a package build, validáció és runtime előkészítés strukturált problémalistája.

Jelenlegi sample forma:

- diagnostics.json

Feladata:

- warningok;
- blocking errorok;
- audit note-ok;
- engine support problémák;
- lookup hibák;
- legacy alias figyelmeztetések;
- structured problémák;
- decklist problémák;
- export problémák;
- dangerous value jelzések.

Lehetséges diagnostics mezők:

- diagnostic_id
- category
- severity
- blocking
- code
- message_hu
- message_dev
- source_ref
- object_ref
- field
- value
- expected
- suggested_fix
- metadata

Fontos elv:

A severity és a blocking külön mező legyen.

---

## 24. Build report

A build_report.md emberi olvasásra szánt összefoglaló.

Feladata:

- package build összefoglalása;
- counts;
- warnings;
- blocking errors;
- ismert korlátok;
- források;
- következő javasolt lépések.

A build report nem helyettesíti a gépi diagnostics fájlt.

---

## 25. Package validációs szintek

Lehetséges validációs szintek:

1. File existence validation
2. Schema validation
3. Type validation
4. Enum validation
5. Reference validation
6. Cross-file consistency validation
7. Engine support validation
8. Hidden legacy model validation
9. Deck legality validation
10. Runtime readiness validation

MVP-ben legalább szükséges:

- fájlok létezése;
- JSON / JSONL olvashatóság;
- manifest ellenőrzés;
- card_id egyediség;
- deck card reference ellenőrzés;
- blocking_errors összesítés;
- schema_version ellenőrzés;
- basic diagnostics.

---

## 26. Reference validáció

A runtime package-en belül ellenőrizni kell:

- deck card_id létezik-e a cards fájlban;
- ability source_card_id létezik-e;
- sample contract source_card_id létezik-e;
- event source card létezik-e;
- target card reference létezik-e;
- lookup értékek léteznek-e;
- alias canonical value létezik-e;
- engine support hivatkozott card_id létezik-e.

Hiányzó referencia esetén diagnostics entry szükséges.

Blocking státusz attól függ, hogy a hiányzó referencia futási szempontból kritikus-e.

---

## 27. Cross-file consistency

A package fájljai között összhang szükséges.

Ellenőrizendő példák:

- manifest felsorolja a tényleges fájlokat;
- manifest counts egyeznek a fájlokkal;
- diagnostics summary egyezik a diagnostics fájllal;
- card_id egyedi;
- decklisták csak létező card_id-t használnak;
- ability registry csak létező source_card_id-t használ;
- engine_support csak létező card_id-t vagy ability_id-t használ;
- aliases canonical_value lookupban létezik;
- lookup active értékek használhatók runtime mezőkben.

---

## 28. Dangerous legacy model validation

A validáció külön figyeljen a régi vagy hibás Aeternal/Pecsét HP-modellre.

Kerülendő értékek és fogalmak:

- player_damage
- aeternal_damage
- heal_player
- heal_aeternal
- ward_hp
- seal_hp
- ward_damage
- seal_damage

Támogatandó modern fogalmak:

- ward_break
- ward_restore
- ward_break_prevent
- aeternal_unprotected
- direct_attack_victory
- player_defeated

Ha régi HP-modell aktív runtime hatásként jelenik meg, az legalább error, bizonyos esetekben blocking error legyen.

---

## 29. Runtime readiness

A runtime readiness azt jelzi, hogy a package futtatható-e egy adott engine célra.

Lehetséges readiness célok:

- godot_loader_ready
- debug_view_ready
- contract_sample_ready
- rules_engine_ready
- ai_test_ready
- balance_test_ready
- release_candidate_ready

Egy package lehet Godot loader ready, de még nem rules engine ready.

Ez fontos megkülönböztetés.

---

## 30. Godot loader kompatibilitás

A Godot loader számára fontos:

- egyszerű JSON / JSONL formátum;
- ismert schema_version;
- manifest alapú fájlfelsorolás;
- card registry építhetősége;
- deck registry építhetősége;
- lookup registry építhetősége;
- ability registry olvashatósága;
- diagnostics summary;
- blocking_errors felismerése.

Jelenleg bizonyított:

- sample package betöltés;
- cards betöltés;
- decks betöltés;
- lookups betöltés;
- ability_registry betöltés;
- diagnostics summary;
- blocking_errors kezelése;
- headless smoke test.

---

## 31. Python builder kompatibilitás

A Python builder feladata:

- sample vagy teljes package előállítása;
- forrásfájlok beolvasása;
- normalizálás;
- validáció;
- diagnostics generálás;
- manifest generálás;
- build report generálás;
- determinisztikus output;
- unit tesztelhetőség.

Hosszú távon a Python builder lehet:

- sample package builder;
- development package builder;
- full card database package builder;
- balance test package builder;
- release package builder.

---

## 32. Determinisztikus output

A package builder outputja legyen determinisztikus.

Ez azt jelenti:

- azonos inputból azonos output jöjjön létre;
- fájlok sorrendje stabil legyen;
- JSON kulcsok sorrendje lehetőség szerint stabil legyen;
- JSONL sorok rendezése stabil legyen;
- generated_at mező kezelése ne zavarja a diffet, vagy kontrollált legyen;
- build report ismételhető legyen;
- tesztek ne véletlenszerű outputra épüljenek.

Ez fontos Git diff, audit és regressziós teszt miatt.

---

## 33. Verziózás

A runtime package verziózása több szinten történhet.

Lehetséges verziók:

- package_version
- schema_version
- ruleset_version
- source_data_version
- build_tool_version
- export_profile_version
- lookup_version
- ability_registry_version

Nem minden MVP-ben kötelező, de hosszú távon tisztázni kell.

Fontos:

A package schema verzió és a kártyaadat verzió nem ugyanaz.

---

## 34. Export profilok

Az exportáló program hosszú távon profilokat használhat.

Lehetséges profilok:

- cards_runtime
- product_decklists
- lookups_runtime_core
- lookups_runtime_ability
- lookups_legacy_alias
- print_product
- workflow_audit
- design_catalog
- sample_runtime_package
- full_runtime_package

Az exportprofil határozhatja meg:

- melyik input sheetet olvassa;
- milyen oszlopokat exportál;
- hogyan kezeli az üres cellákat;
- milyen formátumot ír;
- milyen mezőnormalizálást végez;
- milyen diagnostics szabályt használ.

---

## 35. Üres cellák exportprofil szerint

Az üres cellák kezelése ne legyen globális egyetlen szabály.

Lehetséges stratégia profilonként:

- omit_empty_fields;
- emit_none;
- emit_empty_string;
- emit_null;
- require_value;
- infer_not_applicable;
- audit_if_empty.

A runtime profile-oknál sok esetben jobb lehet az üres mezők kihagyása, de kötelező mezőknél ez blocking error lehet.

---

## 36. Build modes

Lehetséges build mode-ok:

- sample
- development
- strict
- audit
- release_candidate
- debug
- ai_test
- balance_test

Példák:

- sample mode engedhet egyszerűbb adatot;
- development mode sok warningot enged;
- strict mode több hibát blokkol;
- release_candidate mode nem enged unknown enum értékeket;
- ai_test mode deckben lévő unsupported kártyákat blokkolhat;
- debug mode több diagnostics információt tartalmazhat.

---

## 37. Blocking szabályok

A blocking szabályok build mode-tól függhetnek.

Általános blocking jelöltek:

- nem olvasható JSON / JSONL;
- hiányzó manifest;
- ismeretlen schema_version;
- hiányzó kötelező fájl;
- duplicate card_id;
- deckben hiányzó card_id;
- aktív runtime mezőben unknown enum;
- dangerous legacy Aeternal/Pecsét HP-modell;
- hidden information violation;
- critical unsupported effect deckben;
- invalid lookup canonical value.

Nem feltétlenül blocking:

- nem használt kártyán unsupported ability;
- audit note;
- balance suspicion;
- ismert környezeti Godot warning;
- nem kritikus legacy alias, ha canonical normalizálható.

---

## 38. Generated output státusz

A runtime package és az exportok általában generated outputok.

De nem minden generated output törölhető automatikusan.

Lehetséges státuszok:

- regeneratable;
- keep_generated_reference;
- active_test_fixture;
- sample_package_source;
- godot_consumption_copy;
- release_candidate;
- archive_snapshot.

Fontos:

Egy sample package lehet generated, de mégis aktív tesztfixture.

Ezért törlés előtt mindig státuszt kell adni.

---

## 39. Sample package és full package elválasztása

A sample package célja:

- kis méret;
- determinisztikus tesztadat;
- Godot loader próbája;
- debug nézetek próbája;
- smoke testek;
- contract consistency ellenőrzés.

A full package célja:

- teljes kártyaadatbázis;
- teljes decklista;
- teljes lookup rendszer;
- teljes diagnostics;
- későbbi rules engine és AI teszt.

A kettőt nem szabad összekeverni.

A sample package ne próbálja lefedni a teljes játékot.

---

## 40. Sample package MVP minimum

A sample package minimum tartalmazzon:

- legalább néhány kártyát;
- legalább egy decket;
- legalább néhány lookup groupot;
- ability registry mintát;
- diagnostics mintát;
- manifestet;
- blocking_errors értéket;
- warnings értéket;
- build reportot.

A jelenlegi sample már ezt az irányt bizonyítja.

---

## 41. Full package jövőbeli minimum

A full runtime package jövőbeli minimuma:

- minden aktív runtime kártya;
- minden aktív tesztpakli vagy kijelölt deck;
- runtime LOOKUPS;
- legacy alias mapping;
- engine support report;
- ability registry;
- diagnostics;
- build report;
- schema version;
- source data version;
- package manifest;
- reference validation;
- deck validation;
- structured validation.

---

## 42. Runtime package és sample contracts kapcsolata

A runtime package és sample contracts jelenleg külön réteg.

A következő erősítési cél:

- sample snapshotban szereplő card_id feloldása a runtime package card registryből;
- legal action source_card_id feloldása;
- event source / target card_ref feloldása;
- kártyanév megjelenítése debug nézetben;
- card type megjelenítése;
- Birodalom / Klán megjelenítése;
- missing card reference diagnostics.

Ez a kapcsolat még nem rules engine, csak contract és data resolution.

---

## 43. Runtime package és contract-specifikáció kapcsolata

A runtime package adja a statikus adatokat.

A contract-specifikáció adja a játékállapot, döntés, esemény és diagnostics adatcseréjét.

Kapcsolat:

- snapshot card_ref runtime card_id-ra mutat;
- legal action source runtime card_id-ra mutat;
- event source runtime card_id-ra mutat;
- ability_registry source_card_id runtime card_id-ra mutat;
- diagnostics object_ref runtime objektumra mutathat;
- UI card display runtime card registryből származik.

---

## 44. Runtime package és ability module system kapcsolata

A runtime package tartalmazhatja vagy hivatkozhatja:

- ability registryt;
- support státuszokat;
- structured ability adatokat;
- effect module mappinget;
- fallback_required jelzést;
- unsupported module listát;
- diagnostics bejegyzéseket.

A részletes működés az ABILITY_MODULE_SYSTEM.md fájlban szerepel.

---

## 45. Runtime package és AI / balance

AI-vs-AI és balance teszt később ugyanebből az adatcsomagból induljon.

Fontos:

- AI ne saját, eltérő kártyaadatbázisból dolgozzon;
- balance test ugyanazt a runtime package-et fogyassza;
- fair AI visibility snapshotot kapjon;
- diagnostics jelezze az unsupported lapokat;
- balance report hivatkozzon package_id-ra és package_versionre.

Nyitott kérdés:

- AI-vs-AI Pythonban, GDScriptben vagy mindkettőben fusson-e.

---

## 46. Runtime package és README / dokumentáció

A runtime package nem helyettesíti a README-t.

A README csak hivatkozzon rá röviden.

Részletes leírás:

- ez a dokumentum.

Fejlesztői checkpoint:

- CHECKPOINTS.md

Nyitott döntések:

- OPEN_QUESTIONS.md

---

## 47. Nyitott kérdések

A runtime package réteg nyitott kérdései a központi kérdéslistában szerepelnek.

Kiemelt témák:

- compiled runtime package kötelező szerepe;
- egyfájlos vagy többfájlos package;
- canonical lokális XLSX helye;
- XLSX export/source hosszú távú szerepe;
- outputok generated/reference státusza;
- engine support blocking szabályai;
- legacy alias automatikus normalizálása;
- dangerous alias kezelése;
- empty cell kezelés profilonként;
- ability execution plan helye;
- full package minimuma;
- release candidate package szabályai.

---

## 48. Nem cél most

Most nem cél:

- teljes full package véglegesítése;
- teljes AETERNA kártyaadatbázis engine-ready állapotba hozása;
- minden ability module támogatása;
- AI-vs-AI futtatás;
- release package kiadása;
- XLSX source mappák törlése;
- nyers exportok tömeges törlése;
- generated outputok automatikus archiválása.

Mostani fókusz:

- sample package tisztítása;
- package + sample contracts kapcsolat erősítése;
- manifest és diagnostics stabilizálása;
- runtime package schema vázának pontosítása;
- exportprofilok előkészítése;
- full package későbbi útjának megtervezése.

---

## 49. Következő fejlesztési irányok

Ajánlott következő technikai lépések:

1. Runtime package + sample contracts card reference resolution.
2. Missing card reference diagnostics.
3. Unified debug dashboard.
4. Action request smoke test.
5. Exportprofilok előkészítése.
6. Engine support report pontosítása.
7. LOOKUPS runtime validation erősítése.
8. Full runtime package build előkészítő vizsgálat.
9. Ability registry schema tisztítása.
10. Build mode-ok és blocking szabályok pontosítása.

---

## 50. Záró állapot

A runtime package jelenlegi döntési állapota:

- A runtime package a Python és Godot közötti közös adatcsomag.
- A sample runtime package technikailag már bizonyított.
- A Godot loader képes a sample package fogyasztására.
- A runtime package még nem teljes AETERNA adatcsomag.
- A runtime package nem helyettesíti a szabálymotort.
- A runtime package nem helyettesíti a contract-specifikációt.
- A következő helyes lépés a package és a sample contractok kapcsolatának erősítése.