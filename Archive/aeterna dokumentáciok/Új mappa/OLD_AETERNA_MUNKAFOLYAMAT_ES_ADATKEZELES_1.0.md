# AETERNA – kártyaadatbázis audit munkafolyamat

Verzió: 1.0  
Státusz: aktív munkarend-javaslat  
Cél: a kártyaadatbázis javítását, auditját, névprofilozását és tesztpakli-előkészítését követhető, fájlalapú munkafolyamatba rendezni.

## 1. Miért kellett ezt létrehozni?

A korábbi munkafolyamatban túl sok hosszú, 22 oszlopos sor került közvetlenül chatválaszba. Ez több hibát okozhat:

- hosszú sorok elvágódhatnak;
- egy sor csak részben generálódhat ki;
- oszlopcsúszás keletkezhet;
- a válasz túl nagy lesz;
- nehéz ellenőrizni, hogy a chatben adott blokk teljes-e;
- a forrás Excel és az általam adott javítási blokk szétcsúszhat.

Ezért a további munka alapelve:

**A teljes kártyaadatot nem chatben újrageneráljuk, hanem szöveges exportfájlokból olvassuk, és a chatben csak a konkrét javításokat, döntéseket és auditbejegyzéseket adjuk meg.**

## 2. Használt fájlok

### 2.1 Excel-munkafájl

Az Excel / Google Sheets marad a végső szerkesztési és nyilvántartási hely.

Ebben történik:

- a tényleges kártyasorok módosítása;
- az auditlog és decision log vezetése;
- a névprofil munkalap kitöltése;
- a products és product_decklists lapok kezelése;
- a verzióbejegyzés rögzítése.

### 2.2 Szöveges munkakivonat

A `cards.xlsx` fájlból készül egy TSV / JSONL export.

Ennek célja:

- könnyebb olvashatóság;
- pontos sorazonosítás;
- Birodalmonkénti és Klánonkénti szűrés;
- gyorsabb ellenőrzés;
- kevesebb Excel-olvasási hiba;
- kisebb chatválaszok.

A javasolt fő formátum:

- `.md` a munkarendhez és magyarázatokhoz;
- `.tsv` a táblázatos kártyaadatokhoz;
- `.jsonl` opcionális gépi ellenőrzéshez.

## 3. Általános munkafolyamat

### 3.1 Előkészítés

1. Feltöltésre kerül a legfrissebb Excel vagy cards.xlsx.
2. Készül vagy frissül a szöveges export.
3. Ellenőrzésre kerül:
   - lapok száma;
   - oszlopok száma;
   - sorok száma;
   - Birodalom / Klán / Típus bontás;
   - hiányzó vagy extra sorok;
   - ismert eltérések.

### 3.2 Birodalomindítás

Egy új Birodalom indításakor először nem javítunk kártyát.

Először rögzítjük:

- hány lap van az adott Birodalomban;
- melyik két Klán szerepel;
- Klánonként hány lap van;
- Típusonként milyen eloszlás van;
- van-e többlet vagy hiány;
- melyik Klánnal kezdünk;
- van-e előzetes döntési pont.

Példa aktuális AQUA állapot:

- Mélység Őrző / Mélység Őrzői: 58 lap;
- Áramlat-táncos: 60 lap;
- az Áramlat-táncos +2 lapja CORE01-többletként kezelendő;
- a +2 lap sorsa későbbi döntési pont, valószínűleg CORE01-ből kikerül.

### 3.3 Klánfeldolgozás

Egy Klánt nem egyszerre dolgozunk fel.

Javasolt új bontás:

- nem 10 teljes 22 oszlopos sor egyszerre;
- hanem 5 kártyás auditblokkok;
- vagy 10 kártyás blokk csak rövid auditösszefoglalóval, teljes sorok nélkül.

Minden kártyánál először ezeket nézzük:

1. alapadatok;
2. Birodalom;
3. Klán;
4. Faj;
5. Kaszt;
6. Típus;
7. Magnitúdó / Aura / ATK / HP;
8. természetes kártyaszöveg;
9. canonical / structured mezők;
10. státusz;
11. balanszgyanú;
12. engine-gyanú;
13. döntést igényel-e.

### 3.4 Javítási kimenet

A chatben nem teljes 22 oszlopos táblát adunk vissza alapértelmezés szerint.

Helyette háromféle kimenet lehetséges:

#### A) Auditösszefoglaló

Rövid lista:

- Kártya;
- Probléma;
- Javasolt javítás;
- Státusz;
- Kell-e structured javítás;
- Kell-e decision log.

#### B) Mezőszintű javítólista

Csak a módosítandó mezőket tartalmazza.

Példa:

```tsv
Forrás_lap	Forrás_sor	Kártya név	Mező	Régi érték	Új érték	Indoklás
AQUA	4	Zafírszemű Dajka	Faj	Elemi Lény	Elementál	Az Elementál a hivatalos Faj-név.
```

#### C) Teljes soros csere

Csak akkor használjuk, ha a kártya teljes sora tényleg újraírandó.

Szabály:

- maximum 3–5 teljes sor egy válaszban;
- minden sor 22 mezős ellenőrzéssel;
- chatválaszban darabszám-ellenőrzés kötelező.

## 4. Klánvégi audit

Minden Klán végén külön auditot tartunk.

Ellenőrzendő:

- minden kártya kapott státuszt;
- nincs döntetlen / homályos lap;
- a structured mezők nem mondanak ellent a természetes szövegnek;
- a Faj / Kaszt mezők nem keverednek;
- nincs kiegészítői mechanika CORE01 lapokon;
- a balanszgyanúk jelölve vannak;
- az engine-gyanúk jelölve vannak;
- a törlendő / kivételre jelölt lapok külön listán vannak;
- auditlog / decision log készült, ahol kell.

## 5. Birodalomzárás

Egy Birodalom akkor zárható munkaszinten, ha:

1. mindkét Klán első javítóköre kész;
2. mindkét Klán klánauditja kész;
3. birodalomszintű eltérések rendezve vannak;
4. névprofil első köre elkészült;
5. tesztpaklik elkészültek;
6. product / decklist kapcsolatok rendezve vannak;
7. verzióbejegyzés elkészült;
8. nincs ismert blokkoló hiba.

## 6. Jelenlegi állapot

### IGNIS

Munkaszinten lezárva.

Elkészült:

- Hamvaskezű klán első javítóköre;
- Lángidéző klán első javítóköre;
- klánszintű auditok;
- névprofil első köre;
- első IGNIS tesztpaklik;
- Product_ID rendezés;
- 1.2v verzióbejegyzés.

### AQUA

Munkafázis: előkészítés / újraindítás tisztább folyamattal.

Ismert állapot:

- Mélység Őrző / Mélység Őrzői: 58 lap;
- Áramlat-táncos: 60 lap;
- az Áramlat-táncos +2 lapja valószínűleg nem marad CORE01-ben;
- a Mélység Őrzői első 10 lapjának korábbi chatgenerálása nem tekinthető végleges javítóblokknak, mert a kimenet nem volt workflow-szinten biztonságos.

## 7. Új alapelv

A továbbiakban minden nagyobb kártyaadat-javítás előtt:

1. előbb forráskivonat;
2. utána auditösszefoglaló;
3. utána mezőszintű javítólista;
4. csak külön indokkal teljes soros csere.

Ez lesz a munkafolyamat új alapja.
