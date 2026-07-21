# AETERNA – KÁRTYAADATBÁZIS AKTUÁLIS ADATAUDIT

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-21  
**Státusz:** aktív adatkonzisztencia- és átvezetési audit  
**Auditált munkaforrás:** `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`  
**Tervezett repository-útvonal:** `Aeterna dokumentációk/AETERNA – KÁRTYAADATBÁZIS AKTUÁLIS ADATAUDIT 1.0.md`  
**Hivatalos szabályforrás:** nem  
**Adatmódosítás történt:** nem  
**Kapcsolódó külön lookup-forrás:** `LOOKUPS.xlsx` – külön végső ellenőrzési kapu szükséges

Ez a dokumentum a jelenlegi 1.9v kártyaadatbázis szerkezeti, azonosító-, export-, decklista-, névprofil- és lookup-konzisztenciájának aktuális állapotát rögzíti.

A dokumentum:

- nem módosít kártyaadatot;
- nem véglegesít kártyanevet;
- nem javít automatikusan structured értéket;
- nem írja felül a hivatalos szabályfőforrásokat;
- nem helyettesíti az `AUDIT_LOG` vagy `DECISION_LOG` munkalapot;
- nem tekinti aktívnak a régi 1.8v auditok állításait újraellenőrzés nélkül;
- egyetlen aktuális utódként foglalja össze a még élő adatproblémákat.

---

## 1. Audit célja

1. Ellenőrizni, mely korábbi 1.8v hibák javultak az 1.9v munkaforrásban.
2. Elkülöníteni a jelenleg is fennálló problémákat.
3. Megkülönböztetni az adat-, dokumentációs, lookup-, contract- és halasztott tartalmakat.
4. Kijelölni a biztonságos javítási sorrendet.
5. Megőrizni a régi auditokat történeti archívumként, párhuzamos aktív igazságforrás nélkül.

---

## 2. Források és korlátok

### 2.1 Közvetlenül ellenőrzött források

- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`;
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`;
- `kartya_tabla_szabvany v1.2.md`;
- a három archivált 1.8v adataudit;
- az archivált LOOKUPS-bővítési terv.

### 2.2 Külön ellenőrzendő forrás

A canonical lookupok külön szerkesztési forrása a `LOOKUPS.xlsx`.

A jelen audit a munkaforrásban lévő:

- `5. LOOKUPS`;
- `5A. LOOKUPS_RUNTIME`;
- `5B. LOOKUPS_PRINT_PRODUCT`;
- `5C. LOOKUPS_WORKFLOW_AUDIT`;
- `5D. LOOKUPS_DESIGN_CATALOG`

lapokat ellenőrizte.

A külön `LOOKUPS.xlsx` teljes összevetése nélkül a structured lookup-hiányok darabszámai előzetesek. A végső minősítéshez a külön lookup-forrás ellenőrzése kötelező.

### 2.3 Nem része ennek az auditnak

- teljes kártyaszöveg- és szabályaudit;
- balanszaudit;
- kártyanév-véglegesítés;
- ability-support audit;
- production runtime package build;
- hivatalos főforrások módosítása;
- booster pool tervezése;
- teljes kártyaképesség-végrehajthatóság.

---

## 3. Munkafüzet szerkezete

A munkafüzet 21 lapot tartalmaz:

1. `1. VERZIÓ`;
2. `2. README`;
3. `3. CARDS_MASTER`;
4. `4. AUDIT_LOG`;
5. `5. LOOKUPS`;
6. `5A. LOOKUPS_RUNTIME`;
7. `5B. LOOKUPS_PRINT_PRODUCT`;
8. `5C. LOOKUPS_WORKFLOW_AUDIT`;
9. `5D. LOOKUPS_DESIGN_CATALOG`;
10. `6. RARITY_CODES`;
11. `7. EXPORT_RUNTIME`;
12. `8. EXPORT_NOTES`;
13. `9. DECISION_LOG`;
14. `10. IMPORT_ORIGINAL`;
15. `11. SETS`;
16. `12. PRODUCTS`;
17. `13. CARD_PRINTINGS`;
18. `14. GENERATION_PROFILES`;
19. `15. PRODUCT_DECKLISTS`;
20. `16. BOOSTER_POOLS`;
21. `17. NAME_PROFILE`.

A korábbi 1.8v audit egyik fő hiánya, a `7. EXPORT_RUNTIME` távolléte, már nem áll fenn.

---

## 4. Sikeres integritási ellenőrzések

### 4.1 Kártyaállomány

- `CARDS_MASTER`: **814** kártyasor;
- egyedi `Card_ID`: **814**;
- `EXPORT_RUNTIME`: **814** kártyasor;
- egyedi export `Card_ID`: **814**;
- `NAME_PROFILE`: **814** sor;
- egyedi névprofil `Card_ID`: **814**.

Nem talált:

- duplikált `Card_ID`;
- duplikált `Print_ID`;
- duplikált `Collector_Number`;
- ismeretlen decklista-`Card_ID`;
- hiányzó kártyát az export runtime állományban.

### 4.2 Paklik

- decklistarekordok: **754**;
- egyedi deckek: **28**;
- minden deck pontosan **40 lapos**;
- ismeretlen `Product_ID`-re hivatkozó deck nincs;
- ismeretlen kártyára hivatkozó deck nincs.

A korábbi három, 41 lapos deck problémája javítva.

### 4.3 Ritkaságok

| Ritkaság | Kártyák |
|---|---:|
| C | 203 |
| UC | 219 |
| R | 290 |
| SR | 73 |
| UR | 29 |
| **Összesen** | **814** |

Minden használt ritkaságkód szerepel a `RARITY_CODES` lapon.

A korábbi **58 darab `U` kód** problémája javítva; az aktív állomány `UC` kódot használ.

### 4.4 Lookup-szerkezet

Létrejöttek a külön funkcionális lookup-lapok:

- runtime;
- print és product;
- workflow és audit;
- design catalog.

Ez a korábbi LOOKUPS-bővítési terv egyik fő szerkezeti célját teljesíti.

---

## 5. Az 1.8v óta lezárt problémák

| Korábbi probléma | 1.9v állapot |
|---|---|
| `U` ritkaságkód az AETHER-lapokon | javítva |
| nem 40 lapos deckek | javítva |
| hiányzó `7. EXPORT_RUNTIME` | javítva |
| hiányzó split lookup-lapok | javítva |
| ismeretlen decklista-kártyák | nincs ilyen |
| duplikált fő azonosítók | nincs ilyen |
| `16. BOOSTER_POOLS` lap hiánya | a lap létezik, de tartalmilag még üres |

A három 1.8v audit történeti állapotforrás, nem aktuális hibajegyzék.

---

## 6. Aktuális P1 – contract- és runtime-konzisztencia

### P1.1 – Az 1.9v VERZIÓ-bejegyzés hiányos

Az `1. VERZIÓ` lapon az `1.9v` sorban csak a verzióérték szerepel.

Hiányzik:

- dátum;
- módosítás típusa;
- érintett munkalapok;
- státusz;
- változás leírása;
- megjegyzés.

Az 1.9v kiadás tényleges változásai alapján teljes, egy soros verzióbejegyzés szükséges.

---

### P1.2 – A munkafüzet README-lapja elavult

A `2. README` jelenleg azt állítja, hogy:

- a program tiszta runtime fájlja továbbra is a `cards.xlsx`;
- az `EXPORT_RUNTIME` csak 22 oszlopos export;
- a LOOKUPS egyetlen lap.

Ez nem felel meg a jelenlegi rendszernek.

Aktuális irány:

- a munkafüzet szerkesztési és auditforrás;
- a program validált runtime package-et fogyaszt;
- a `7. EXPORT_RUNTIME` a programoldali kártyaadat egyik fő exportforrása;
- a lookupok több funkcionális lapra és külön `LOOKUPS.xlsx` forrásra tagolódnak;
- a régi `cards.xlsx` legacy vagy összehasonlító forrás, nem production runtime authority.

A `2. README` teljes aktualizálása szükséges.

---

### P1.3 – Az elsődleges kártyaazonosító neve nincs egységesítve

Az aktív dokumentációs szabvány több helyen ezt írja elő:

- elsődleges stabil azonosító: `Szabályi_Kártya_ID`.

A jelenlegi munkafüzet több aktív lapja ezt használja:

- `Card_ID`.

A `CARD_PRINTINGS` és `BOOSTER_POOLS` továbbra is `Szabályi_Kártya_ID` fejlécet használ.

További eltérés:

- a jelenlegi `Card_ID` értékek például `IGN-HAM-023`;
- a `CARD_PRINTINGS` régi értékei például `AET-IGN-HAM-023`.

Ez azonosító-contract, prefix-policy, cross-sheet kapcsolás és kompatibilitási kérdés.

Külön dönteni kell:

1. a canonical mezőnévről;
2. az `AET-` prefix státuszáról;
3. a legacy alias kezeléséről;
4. a dokumentáció és munkafüzet összehangolásáról;
5. a migráció backward compatibility szabályáról.

Automatikus tömeges átnevezés nem végezhető a loader- és exportfüggőségek ellenőrzése nélkül.

---

### P1.4 – Structured többértékű delimiter nincs egységesítve

Az elfogadott újabb projektirány szerint a structured többértékű mezők delimiterje pontosvessző.

A jelenlegi munkafüzet tömegesen vesszőt használ:

| Mező | Vesszőt tartalmazó kártyasor |
|---|---:|
| `Zóna_Felismerve` | 443 |
| `Kulcsszavak_Felismerve` | 70 |
| `Trigger_Felismerve` | 25 |
| `Célpont_Felismerve` | 136 |
| `Hatáscímkék` | 348 |
| `Időtartam_Felismerve` | 45 |

A jelenlegi `kartya_tabla_szabvany v1.2.md` a pontosvesszőt kifejezetten a `Képesség_Canonical` több részes hatásainál említi, de nem rögzíti egyértelműen minden többértékű structured mező közös delimiterét.

Szükséges sorrend:

1. dokumentációs döntés;
2. szabványverzió-emelés;
3. exporter/parser kompatibilitás;
4. külön LOOKUPS ellenőrzése;
5. kontrollált adatmigráció;
6. runtime package regresszió.

Tömeges delimitercsere addig nem végezhető.

---

### P1.5 – Structured lookup-lefedettség részleges

A munkafüzet `5A. LOOKUPS_RUNTIME` lapját a `CARDS_MASTER` ténylegesen használt értékeivel összevetve:

| Structured terület | Használt egyedi érték | A beágyazott runtime lookupból hiányzó |
|---|---:|---:|
| Típus | 5 | 0 |
| Birodalom | 7 | 0 |
| Klán | 14 | 0 |
| Faj | 21 | 0 |
| Kaszt | 20 | 0 |
| Zóna | 12 | 0 |
| Kulcsszó | 11 | 0 |
| Trigger | 108 | 68 |
| Célpont | 80 | 49 |
| Hatáscímke | 118 | 62 |
| Időtartam | 33 | 23 |
| Értelmezési státusz | 25 | 15 |

Ez a munkafüzet beágyazott `5A. LOOKUPS_RUNTIME` lapjára vonatkozik.

A külön canonical `LOOKUPS.xlsx` teljes vizsgálata nélkül nem állítható, hogy ugyanezek az értékek a tényleges elsődleges lookup-forrásból is hiányoznak.

Minden hiányzónak látszó értéket triázsolni kell:

- active canonical;
- új canonical jelölt;
- biztonságos legacy alias;
- auditot igénylő alias;
- workflow-only státusz;
- hibás vagy elírt érték;
- túl részletes kártyaspecifikus érték;
- ability-module paraméter;
- nem lookupba való condition/payload elem.

---

### P1.6 – CARDS_MASTER és EXPORT_RUNTIME között két eltérés van

Mindkettő ugyanazon a kártyán:

**Kártya:** `IGN-HAM-001`

| Mező | CARDS_MASTER | EXPORT_RUNTIME |
|---|---|---|
| `Hatáscímkék` | `keyword` | `none` |
| `Értelmezési_Státusz` | `tiszta` | `passziv_vagy_egyszeru` |

Előbb meg kell állapítani a jóváhagyott canonical adatot, majd a mastert vagy az exportelőállítást javítani, új exportot készíteni és parity tesztet futtatni.

Kézi exportjavítás nem javasolt.

---

### P1.7 – A külön `LOOKUPS.xlsx` összevetése hiányzik

Kötelező ellenőrzések:

- laplista és schema;
- `Value`, `Label_HU`, `Canonical_Value`;
- active/inactive/legacy státusz;
- duplikált értékek;
- azonos Value több csoportban;
- delimiter-policy;
- munkaforrás 5A–5D lapjaihoz képesti eltérés;
- builder által ténylegesen fogyasztott forrás;
- trigger/target/effect/duration/status coverage;
- veszélyes aliasok;
- `source`, `graveyard`, `trap`, `sign` és más legacy értékek.

A jelen audit csak e kapu lezárása után tekinthető teljes lookup-auditnak.

---

## 7. Aktuális P2 – adatszinkron és workflow

### P2.1 – NAME_PROFILE és CARDS_MASTER eltérések

Az azonos kártyák összevetett kontextusmezőiben **78 eltérés** található:

- jelenlegi név;
- Birodalom;
- Klán;
- Faj;
- Kaszt.

Példák:

- `IGN-HAM-009` – Faj: `Ember vagy Ork` → `Ember`;
- `IGN-HAM-010` – Faj: `Ember vagy Ork` → `Ember`;
- `IGN-HAM-010` – Kaszt: `Orgyilkos / Harcos` → `Orgyilkos`;
- `IGN-HAM-012` – Kaszt: `Harcos vagy Őrző` → `Őrző`;
- több LUX kártyán `Alap` → konkrét Kaszt;
- néhány VENTUS kártyán eltérő Kaszt vagy Klánírásmód.

Javítási irány:

- ID-alapú szinkron;
- csak a kontextusmezők frissítése;
- névjavaslatok és névstátuszok változatlanul hagyása;
- névváltoztatás csak emberi döntéssel.

---

### P2.2 – Decklista segédnevek eltérnek a mastertől

A `PRODUCT_DECKLISTS` lapon **24** `Kártya_Név` nem egyezik a `CARDS_MASTER` jelenlegi nevével.

A `Card_ID` hivatkozások helyesek, ezért ez segédnév-szinkronprobléma.

Példák:

- `Árnyközvetítő` → `Árnyék-közvetítő`;
- `Árnylépés` → `Árnyék-Ugrás`;
- `Feltámadt Csontzúzó` → `Feltámadt Csonttörő`;
- `Sírvermi Sírásó` → `Temetői Sírásó`.

A neveket ID-alapú szinkronizálással kell frissíteni.

---

### P2.3 – Üres PRODUCTS sorok

A `12. PRODUCTS` lapon három teljesen üres adatsor maradt:

- 19. sor;
- 20. sor;
- 21. sor.

A forrásból eltávolítandók vagy az exportálóban szűrendők. Ellenőrizni kell, hogy képlet, formázás vagy adatvalidáció miatt maradtak-e.

---

### P2.4 – CARD_PRINTINGS részben elavult

A `CARD_PRINTINGS` csak három rekordot tartalmaz.

Kiemelt eltérések:

- `AET-` prefixet használ;
- az `IGN-HAM-023` és `IGN-HAM-031` `Play_Legal_Status` értéke régi:
  - `CORE01_needs_token_rules`;
  - a `CARDS_MASTER` jelenleg `CORE01_test_required`;
- a `Product_ID` érték `TBD`.

El kell dönteni, hogy a lap:

- aktív print-master;
- részleges pilot;
- vagy történeti előkészítő lap.

Aktív státusz esetén teljes szinkron szükséges; pilot esetén ezt egyértelműen dokumentálni kell.

---

## 8. Aktuális P3 – halasztott vagy nem blokkoló

### P3.1 – Productok decklista nélkül

Nincs decklistája:

- `BP-CORE01`;
- `KLP-IGN-HAM01`;
- `KZK-CORE01`.

Ez nem feltétlenül hiba, mert nem minden product fix pakli. Producttípus és distribution policy alapján kell státuszolni.

### P3.2 – BOOSTER_POOLS előkészített, de üres

A lap létezik, de a 21 előkészített adatsor üres.

Az aktív Excel-struktúradokumentum szerint a lap későbbi boosterkezeléshez van előkészítve.

Jelenleg:

- nem blocking adatbázishiba;
- nem kész booster-adat;
- production runtime poolként nem használható;
- az üres sorokat exportkor szűrni kell.

### P3.3 – `blank` és `none` policy

Ajánlott értelmezés:

- `blank`: nem alkalmazható vagy nincs structured adat;
- `none`: az adott kategóriából kifejezetten nincs további elem.

A mezőnkénti policy külön schema-döntést igényel.

### P3.4 – Legacy terminológia és aliasok

Külön ellenőrzendő:

- `graveyard` ↔ `void`;
- `source` ↔ `wellspring`;
- `trap` / `sign` ↔ `sigil`;
- régi magyar és angol zónanevek;
- korábbi `spell` gyűjtőfogalom;
- régi Aeternal/Pecsét HP-nyelv;
- `aethereal` és más elírások;
- workflow státuszok semantic mezőben.

Legacy érték nem válhat automatikusan active canonical értékké.

---

## 9. Dokumentációs eltérések

Összehangolandó:

1. `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`
   - tényleges `Card_ID` / `Szabályi_Kártya_ID`;
   - külön `LOOKUPS.xlsx`;
   - aktuális `EXPORT_RUNTIME`;
   - delimiter-policy.

2. `kartya_tabla_szabvany v1.2.md`
   - többértékű mezők delimiterje;
   - `void` / `wellspring`;
   - aktív runtime mezők;
   - `blank` / `none`.

3. Munkafüzet `2. README`
   - runtime adatút;
   - szerkesztési authority;
   - runtime package;
   - split lookup-források;
   - legacy `cards.xlsx`.

4. `RUNTIME_PACKAGE_SPECIFICATION.md`
   - csak tényleges builder- vagy package-contract változáskor.

---

## 10. Javasolt javítási sorrend

1. **Contract-döntések**
   - ID mezőnév;
   - `AET-` prefix;
   - delimiter;
   - `blank` / `none`;
   - canonical terminológia;
   - külön LOOKUPS authority.

2. **Külön `LOOKUPS.xlsx` teljes audit**

3. **Kis kockázatú forrásjavítások**
   - VERZIÓ 1.9v sor;
   - README-lap;
   - három üres PRODUCTS sor;
   - 24 decklista segédnév;
   - 78 NAME_PROFILE kontextusmező.

4. **Master–export parity**
   - `IGN-HAM-001`;
   - új export;
   - parity teszt.

5. **Structured migráció**
   - lookup-triázs;
   - delimiter-migráció;
   - parser/exporter regresszió;
   - diagnostics.

6. **Print és product réteg**
   - CARD_PRINTINGS státusz;
   - Product_ID-k;
   - booster poolok;
   - generation policy.

7. **Utóellenőrzés**
   - ID-k;
   - deckméret;
   - referenciák;
   - parity;
   - lookup coverage;
   - üres sorok;
   - verziólap;
   - README;
   - runtime package build;
   - diagnostics;
   - Git diff.

---

## 11. Archív elődök kezelése

Történeti archívumként megmarad:

- `aeterna_1_8v_teljes_jsonl_audit_jelentes.md`;
- `aeterna_1_8v_ujraellenorzes_reszleges_audit.md`;
- `aeterna_1_8v_javitott_export_lookup_audit.md`;
- `aeterna_LOOKUPS_bovitesi_terv.md`.

Státuszuk:

- `ARCHIVED_HISTORICAL_AUDIT`;
- nem aktív hibajegyzék;
- nem törlendők;
- nem írják felül a jelen 1.0-s auditot;
- a korábbi állapot, javítások és döntési folyamat visszakeresésére szolgálnak.

A jelen dokumentum az aktív 1.9v adataudit-utód.

---

## 12. Elfogadási feltételek

Az audit akkor zárható le, ha:

- az 1.9v VERZIÓ-sor teljes;
- a munkafüzet README naprakész;
- az ID-contract döntött és dokumentált;
- a delimiter-policy döntött és verziózott;
- a külön `LOOKUPS.xlsx` auditja elkészült;
- a master/export két eltérése megszűnt vagy elfogadott;
- a 78 NAME_PROFILE eltérés rendezett;
- a 24 decklistanév szinkronizált;
- az üres PRODUCTS sorok kezelve;
- a CARD_PRINTINGS státusza tisztázott;
- a runtime package build és diagnostics zöld;
- az utóellenőrzés bekerült a verzió-, audit- és döntésnaplóba.

---

## 13. Rövid aktuális állapot

**Kártyaazonosító-egyediség:** zöld.  
**Runtime export teljessége:** zöld, két mezőeltéréssel.  
**Deckméret és kártyahivatkozások:** zöld.  
**Ritkaságkódok:** zöld.  
**Névprofil-szinkron:** javítandó.  
**Decklista segédnevek:** javítandók.  
**Lookup-szerkezet:** létrejött, coverage-audit szükséges.  
**Külön LOOKUPS-forrás:** végső ellenőrzésre vár.  
**Delimiter-policy:** döntési és migrációs feladat.  
**Munkafüzet README és verziólap:** frissítendő.  
**Booster pool:** előkészített, halasztott.  
**Régi 1.8v auditok:** archivált történeti források.
