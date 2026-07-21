# Aeterna Projekt

Python alapú szimulátor és szabálymotor az **AETERNA** kártyajátékhoz.

A projekt jelenlegi elsődleges célja:
- az AETERNA kártyák és mechanikák szabályhű kezelése
- AI-vs-AI tesztmeccsek futtatása
- a structured kártyaadatok engine-oldali felhasználása
- a motor fokozatos stabilizálása, feltérképezése és későbbi bővíthetőségének előkészítése

---

## Futtatás

```bash
python main.py
```

---

## Tesztek futtatása

```bash
python -m unittest discover -s tests -v
```

---

## Projektirányító dokumentumok

A projekt jövőbeli módosításainál, refaktorainál, promptolásánál és fejlesztési döntéseinél az alábbi dokumentumok számítanak elsődleges referenciának.

### 1. `ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md`

Ez a dokumentum rögzíti:
- a jelenlegi hivatalos futási utat
- az aktív core runtime modulokat
- a wrapper / átmeneti rétegek fő elhatárolását

Ezt kell alapnak venni, ha az a kérdés, hogy:
- mi a tényleges futási lánc
- mely modulok számítanak elsődleges runtime rétegnek
- mi számít wrappernek vagy kompatibilitási rétegnek

### 2. `PROJEKT_TERKEP_ES_FAJLSTATUSZ_v1.md`

Ez a dokumentum rögzíti:
- a projekt fő mappáit és fájljait
- hogy mi micsoda
- melyik fájl mire szolgál
- mely elemek aktív runtime, dokumentáció, audit, report vagy cleanup-jelöltek

Ezt kell alapnak venni, ha az a kérdés, hogy:
- melyik fájl milyen szerepet tölt be
- mit szabad módosítani
- mit kell megtartani
- mit kell később refaktorálni vagy rendezni

### 3. `AKTUALIS_PROJEKTTERV_ES_PRIORITASOK.md`

Ez a dokumentum rögzíti:
- a projekt aktuális céljait
- a prioritási sorrendet
- a jelenlegi fókuszokat
- a GitHub-használat alapelveit
- a rövid, közép- és hosszú távú fejlesztési irányokat

Ezt kell alapnak venni, ha az a kérdés, hogy:
- min dolgozunk most
- mi a következő logikus lépés
- mit nem akarunk most csinálni
- hogyan kell a fejlesztést követhetően vinni

### 4. `GITHUB_MUNKAREND_ES_COMMIT_SZABALYOK.md`

Ez a dokumentum rögzíti:
- a GitHub-alapú munkarendet
- a commitok és branchek használatának alapelveit
- a különböző típusú változtatások elkülönítésének szabályait
- az egyszerű, követhető fejlesztési működés minimál szabályait

Ezt kell alapnak venni, ha az a kérdés, hogy:
- mit commitoljunk együtt és mit ne
- mikor kell külön branch
- hogyan legyen a GitHub történet követhető
- hogyan kell a projekt változtatásait rendezett formában vezetni

---

## Munkaszabály jövőbeli módosításokhoz

A jövőbeli fejlesztések, promptok, refaktorok és új feladatok esetén az alábbi alapelvet kell követni:

1. Először a projektirányító dokumentumokat kell figyelembe venni.
2. A módosításoknak igazodniuk kell a hivatalos futási úthoz és az aktuális projekttervhez.
3. Új feladat vagy változtatás előtt tisztázni kell, hogy:
   - érinti-e a core runtime-ot
   - dokumentációs, report vagy audit jellegű-e
   - cleanup / refaktor / mechanikai fejlesztés / tesztelési célból történik-e
4. A projektet nem teljes újrakezdésként kezeljük, hanem:
   - feltérképezés
   - stabilizáció
   - cleanup
   - célzott refaktor
   - későbbi bővítés
   logika szerint fejlesztjük tovább.

---

## Jelenlegi stratégiai irány

A projekt jelenlegi fő iránya:

1. a meglévő rendszer pontos feltérképezése
2. a fájlok és rétegek szerepének tisztázása
3. a túlterhelt részek (különösen a report / audit / historical rétegek) rendezése
4. a motor stabilizálása
5. a későbbi Godot-integráció előkészítése úgy, hogy a Python motor backendként használható maradjon

---

## Fontos megjegyzés

A projekt jelenlegi állapota hibrid:
- részben structured / canonical alapon működő runtime
- részben shared helper alapú runtime
- részben card-local név-alapú speciális logika

Ezért új feladatnál mindig tisztázni kell, hogy a kérdés:
- structured réteget érint
- shared runtime réteget érint
- card-local speciális handlert érint
- vagy csak dokumentációs / cleanup / logikai rendezési kérdés

---

## Későbbi cél

A hosszú távú cél az, hogy a jelenlegi Python motor olyan állapotba kerüljön, hogy később **Godot frontendhez kapcsolható backendként** működhessen.

Ez azt jelenti, hogy a mostani munkáknál is figyelembe kell venni:
- a tiszta állapotkezelést
- a világos futási határokat
- a későbbi frontend-integráció lehetőségét
- a túl szoros konzolos / belső kódhoz kötött megoldások elkerülését

---

## Ajánlott prompt-előtag jövőbeli munkákhoz

A jövőbeli asszisztensi vagy Codex-munkáknál ajánlott ezzel kezdeni a feladatot:

```text
Mielőtt a feladatra válaszolsz, igazodj az alábbi projektirányító dokumentumokhoz:
- ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md
- PROJEKT_TERKEP_ES_FAJLSTATUSZ_v1.md
- AKTUALIS_PROJEKTTERV_ES_PRIORITASOK.md
- GITHUB_MUNKAREND_ES_COMMIT_SZABALYOK.md

A választ ezek figyelembevételével add meg. Mindig tisztázd, hogy a kérés:
- core runtime,
- supporting runtime,
- wrapper,
- docs,
- tests,
- stats/report,
- vagy cleanup/refaktor kategóriába tartozik.

A projektet nem 0-ról újraépítendő rendszerként kezeljük, hanem feltérképezés → stabilizáció → cleanup → célzott refaktor logika szerint.
```

Rövidebb változat:

```text
Igazodj a projektirányító dokumentumokhoz:
- ARCHITEKTURA_ES_HIVATALOS_FUTASI_UT.md
- PROJEKT_TERKEP_ES_FAJLSTATUSZ_v1.md
- AKTUALIS_PROJEKTTERV_ES_PRIORITASOK.md
- GITHUB_MUNKAREND_ES_COMMIT_SZABALYOK.md

A feladatot ezekkel összhangban kezeld.
```

---

## Jelenlegi helyzet röviden

A projekt jelenleg nem teljes újrakezdésre váró rendszer, hanem olyan meglévő motor, amely:
- már rendelkezik működő maggal
- több rétegben részben rendezett
- részben átmeneti / hibrid állapotban van
- és most a következő fő fázisba lépett:
  **feltérképezés, rendezés, összekapcsolás és követhető fejlesztési működés**

---

## Fontos elv

A projekt jövőbeli fejlesztésében törekedni kell arra, hogy:
- a GitHub történet követhető legyen
- a változtatások ne keverjenek össze több különböző célt
- a dokumentáció, runtime, cleanup és report jellegű módosítások elkülöníthetők maradjanak
- a projektirányító dokumentumok naprakészek maradjanak
