# AETERNA dokumentációk – mappaszintű rend

Ez a mappa az AETERNA projekt fő dokumentációs és adatforrás-jellegű anyagait tartalmazza.

A főszint célja, hogy csak aktív vagy kiemelten fontos projektirányító források maradjanak itt.  
Régi auditok, átmeneti tervek, generált exportok és háttéranyagok külön almappákba kerülnek.

---

## Főszinten maradhat

A fő `Aeterna dokumentációk/` szinten csak ezek a típusok maradjanak:

- hivatalos szabályforrások
- aktív kártyaadatbázis / LOOKUPS munkaforrás
- aktuális projektterv
- aktuális projekt-térkép / fájlstátusz
- aktív munkafolyamat- és adatkezelési szabványok
- aktív Excel / kártyatábla szabványok
- aktív kártyaauditálási munkarend

Jelenlegi főszinti védett fájlok:

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`
- `AETERNA – KÁRTYAADATBÁZIS MUNKAFORRÁS 1.9v.xlsx`
- `LOOKUPS.xlsx`
- `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v5.1.md`
- `PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.2.md`
- `AETERNA_MUNKAFOLYAMAT_ES_ADATKEZELES_1.2.md`
- `AETERNA_EXCEL_STRUKTURA_ES_OSZLOPSZABVANY_1.2.md`
- `AETERNA – KÁRTYAÁLLOMÁNY AUDITÁLÁSI MUNKAREND ÉS HIBAKATEGÓRIÁK 1.2v.md`
- `kartya_tabla_szabvany v1.2.md`

---

## Almappák

### `reference/`

Ide kerülnek azok az anyagok, amelyek nem aktív főforrások, de hosszabb távon hasznos háttér- vagy referenciaanyagok.

Példák:

- design jegyzetek
- ötletládák
- régi technikai referenciaanyagok
- tesztelési workflow-dokumentumok
- névprofil-sablonok
- régi architektúra- vagy backend referenciaanyagok

Ezeket nem kell törölni, de nem is kell a főszinten tartani.

---

### `archive_review/`

Ide kerülnek azok az anyagok, amelyek korábbi auditok, átmeneti tervek, állapotjelentések vagy cleanup-nyomok.

Példák:

- régi auditjelentések
- régi exportellenőrzések
- átmeneti README / guidance fájlok
- cleanup candidate listák
- régi backend readiness auditok
- korábbi LOOKUPS bővítési tervek

Ezek nem törlendők automatikusan.  
Később külön archívum- vagy törlési döntéssel lehet őket véglegesen rendezni.

---

### `generated_review/`

Ide kerülnek generált, exportált vagy gépi feldolgozásból származó review-anyagok.

Példák:

- TSV exportok
- generált LOOKUPS oszlopkimenetek
- régi exportcsomagok
- ideiglenes gépi outputok

Ezek nem canonical források.  
Feladatuk az ellenőrzés, összevetés és későbbi audit.

---

### `active/`

Ez a mappa jelenleg fenntartott, de a fő aktív forrásokat egyelőre nem mozgattuk ide.

Ennek oka:

- több dokumentum és tooling még név vagy útvonal alapján hivatkozik a főszinti fájlokra;
- a hivatalos szabályforrások és adatforrások mozgatása csak hivatkozásfrissítési tervvel történhet;
- a főszint jelenleg maga tölti be az aktív források szerepét.

Későbbi döntési pont:
- ha minden hivatkozás frissíthető,
- és a dokumentációs útvonalak stabilak,
- akkor az aktív főforrások átkerülhetnek `active/` alá.

---

## Munkaszabály

Új fájl elhelyezésekor:

1. először el kell dönteni, hogy aktív forrás, referencia, auditnyom vagy generált output;
2. aktív főforrás csak indokolt esetben kerüljön főszintre;
3. átmeneti audit vagy report ne maradjon főszinten;
4. generált export ne maradjon főszinten;
5. törlés előtt mindig legyen külön döntés vagy archive_review ellenőrzés.

---

## Jelenlegi státusz

Az `Aeterna dokumentációk/` első mappatisztítási köre lezárva.

A főszinten csak a védett aktív dokumentumok, adatforrások és szabványok maradtak.