# AETERNA – Dokumentációs cleanup checkpoint

Dátum: 2026-07-03
Státusz: első dokumentációs cleanup kör lezárva

## Cél

Ez a checkpoint az AETERNA projekt dokumentációs és mappaszerkezeti rendezésének első lezárt körét rögzíti.

A cél nem tartalmi szabálymódosítás, nem kártyaaudit és nem kódrefaktor volt, hanem:

* a dokumentációs főszint tisztítása;
* aktív, referencia, archív és generált anyagok elkülönítése;
* elavult útvonalak javítása;
* a régi Python motor és az új contract-first `Aeterna game engine/` irány szétválasztásának dokumentálása;
* a későbbi munkákhoz biztonságosabb projektkép kialakítása.

## Elkészült főbb rendezések

### `Aeterna dokumentációk/`

Létrejött és használatba került az alábbi szereposztás:

* `reference/` – hasznos, de nem elsődleges aktív szabályforrások és háttéranyagok;
* `archive_review/` – régi auditok, átmeneti munkadokumentumok, korábbi állapotjelentések;
* `generated_review/` – generált vagy exportált anyagok, amelyek nem kézi canonical források;
* `active/` – fenntartott hely későbbi aktív rendezési döntésekhez.

A főszinten maradtak az aktív, védett vagy projektirányító források.

### Root és régi inventár

A régi `mappaszerkezet v0.2.md` kikerült a projektgyökérből, mert történeti állapotfelmérő fájl, nem aktuális projektigazság.

### Engine dokumentáció

Az `Aeterna game engine/docs/` mappa áttekintésre került. A dokumentáció alapvetően rendezettnek minősült.

Fontos aktív engine-dokumentumok:

* `Aeterna game engine/docs/DECISION_MAP.md`
* `Aeterna game engine/docs/ARCHITECTURE.md`
* `Aeterna game engine/docs/TECHNOLOGY_DECISIONS.md`
* `Aeterna game engine/docs/CONTRACT_SPECIFICATION.md`
* `Aeterna game engine/docs/RUNTIME_PACKAGE_SPECIFICATION.md`
* `Aeterna game engine/docs/ABILITY_MODULE_SYSTEM.md`
* `Aeterna game engine/docs/PROTOTYPE_PLANS.md`
* `Aeterna game engine/docs/OPEN_QUESTIONS.md`
* `Aeterna game engine/docs/checkpoints/CHECKPOINTS.md`

Nem indokolt további engine docs mappamozgatás.

## Frissített hivatkozások

Frissítésre került több élő projektirányító dokumentum útvonala és megfogalmazása:

* root `README.md`;
* `Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`;
* `Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`.

A frissítések célja az volt, hogy:

* a `reference/` alá mozgatott dokumentumok ne főszinti fájlként szerepeljenek;
* a két `1.4v` hivatalos főforrás legyen a mérvadó szabályi alap;
* a régi Python motor ne jelenjen meg új fejlesztési főirányként;
* a legacy `main.py` ne keveredjen a későbbi új contract-first engine belépési ponttal.

## Aktív szabályi alap

A jelenlegi aktív hivatalos szabályforrások:

* `Aeterna dokumentációk/AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
* `Aeterna dokumentációk/AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

Minden szabályértelmezési, kártyatervezési, kártyaauditálási és engine-kompatibilitási döntésnél ezek az elsődleges források.

## Régi Python motor státusza

A régi Python motor továbbra is értékes referencia, de nem az új fejlesztési főirány.

Státusza:

* `OLD_ENGINE_REVIEW`
* `OLD_ENGINE_REFERENCE`
* `LEGACY_SIMULATOR_REFERENCE`

Fontos: az `Aeterna game engine/python/main.py` jelenleg még legacy szimulátoros belépési pontként létezhet, mert a korábbi program ezt használta. Ez nem az új contract-first engine végleges belépési pontja.

Későbbi új belépési pontot egyértelmű, nem félrevezető névvel kell létrehozni.

## Amit most nem csináltunk

Ebben a cleanup körben nem történt:

* kódrefaktor;
* kártyaadat-tömegjavítás;
* hivatalos szabályforrás-módosítás;
* `LOOKUPS.xlsx` vagy kártyaadatbázis szerkezeti módosítás;
* engine runtime átnevezés;
* régi Python motor törlése;
* `Archive/` mélyrendezése;
* `XLSX export/` végleges archiválása.

Ezek mind külön döntési körhöz tartoznak.

## Következő javasolt munkakör

A dokumentációs cleanup első köre lezárható.

Következő javasolt fő munkairány:

1. `XLSX export/` és az új `Aeterna game engine/python/tools/xlsx_export/` viszonyának áttekintése;
2. a régi exporter szerepének végleges státuszolása;
3. annak eldöntése, hogy mikor és hogyan lehet az `XLSX export/` mappát review vagy archive státuszba tenni;
4. csak ezután Codex-feladat az exporter / runtime package pipeline konkrét módosítására.

## Lezáró megjegyzés

A jelenlegi cleanup kör célja teljesült: az aktív dokumentációs kép tisztább, a projektirányító fájlok pontosabbak, és a régi Python motor / új contract-first engine szétválasztása világosabban dokumentált.
