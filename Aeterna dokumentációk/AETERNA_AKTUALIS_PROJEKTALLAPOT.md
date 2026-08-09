# AETERNA – Aktuális projektállapot

## DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 1.0
- **Dátum:** 2026-07-26
- **Státusz:** egyetlen aktív operatív projektállapot és folytatási pont
- **Repository:** `commander150/Aeterna_Projekt`
- **Ellenőrzött production kódbázis:** `5ee20cf199da53818e576726ed378be384d65df6` – `Add production Aura payment preflight foundation`
- **Learning-fájlkészlet ellenőrzött bázisa:** `78aa464a12eaa4b6c0c53fe042f528e2e82a5fab`
- **Távoli CI-bizonyíték:** nem áll rendelkezésre a vizsgált production commitokhoz

Ez a fájl rögzíti az AETERNA aktuális állapotát, a következő munkát és a fontos blokkolókat. Stabil fájlnevet használ, és elfogadott mérföldkő után ugyanitt frissül.

Nem szabályforrás és nem részletes technikai specifikáció.

---

## 1. Dokumentumelsőbbség

1. hivatalos alapjáték-főforrás 1.4v;
2. hivatalos kiegészítő-főforrás 1.4v;
3. explicit, verziózott emberi döntések;
4. ez az aktuális projektállapot;
5. elfogadott architektúra- és contractspecifikációk;
6. production C# implementáció és tesztbizonyíték;
7. Python reference engine;
8. learning anyagok és történeti dokumentumok.

Ellentmondás esetén az alacsonyabb szint nem írhatja felül a magasabbat.

---

## 2. Elfogadott architektúra

```text
Godot / GDScript
    = vizuális kliens, input, UI, animáció, presentation és debug

C# / .NET
    = egyetlen production authoritative rules engine

Python
    = adatpipeline, audit, fixture, reference engine, AI, batch és elemzőtooling
```

Kötelező határok:

- Godot nem módosíthat authoritative MatchState-et közvetlenül;
- Python nem lehet második production authority;
- production state mutation csak validált C# engine transitionön keresztül történhet;
- viewer-facing snapshot és event nem szivárogtathat rejtett információt;
- runtime package nem szabálymotor és nem mérkőzésállapot.

---

## 3. Bizonyított és elfogadott alapok

### Adat- és runtime package

- XLSX/LOOKUPS alapú Python build és publish pipeline;
- blocking candidate validation;
- Godot consumption copy;
- kártya-, deck-, lookup-, alias-, ability- és diagnostics fájlok;
- Godot loader és registry;
- headless smoke és debug nézetek.

A package identity és a végleges production schema még nem lezárt.

### Reference és runtime proofok

- Python minimal reference engine: aktív comparison oracle és toolingalap;
- Python–Godot sidecar: `COMPLETE_AND_FROZEN`;
- Godot .NET/C# candidate: `COMPLETE_AND_ACCEPTED`;
- C.5A production architecture: `COMPLETE_AND_ACCEPTED`;
- C.5B production C# foundation: `COMPLETE_AND_ACCEPTED`.

### C.5B production foundation

Commit:

```text
931bf5571d541c752aa421a9f0626768bd8ffbe7
```

Fő scope:

- `Aeterna.Engine`;
- `Aeterna.Engine.Headless`;
- `Aeterna.Engine.Tests`;
- `EngineSession`;
- minimum runtime package loader;
- draw és end-turn;
- stale request rejection;
- viewer-safe snapshot és eventprojekció;
- canonical fixture és Godot production bridge.

A C.5B saját lezárásakor rögzített bizonyítékai történetileg megmaradnak a mérföldkőnaplóban. Az ezt követő gameplay commitok aktuális build- és teszt-PASS állapotát külön újra kell futtatni.

---

## 4. C.5B után elkészült production gameplay-alapok

### 4.1 Wellspring state és projection

Commit:

```text
9c192abc64445577005e939075a4ab66272ece60
```

Forrásszinten elkészült:

- Wellspring player state;
- Wellspring invariánsok;
- aktív/kimerült forrásösszesítés;
- owner-visible és opponent-redacted projection;
- defensive és non-mutating snapshotkezelés;
- célzott tesztesetek hozzáadása.

### 4.2 Normál Beáramlás

Commit:

```text
3d1d24ac71b839ead7a8d6881237963db48304cb
```

Forrásszinten elkészült:

- `normal_inflow` legal action;
- typed payload és stabil disabled reasonök;
- Hand → Wellspring transition;
- egyszer használható körönkénti state;
- typed event és viewer-safe projection;
- immutable rejection és stale-request védelem;
- célzott tesztesetek hozzáadása.

### 4.3 Magnitúdó-preflight

Commit:

```text
c5a8d343b7f9bdb55d74404a89afdb8ceff51cdb
```

Forrásszinten elkészült:

- runtime card `magnitude` betöltés és validáció;
- immutable runtime card catalog;
- internal Magnitúdó-preflight;
- Wellspring forrásszám alapján történő küszöbvizsgálat;
- pure, deterministic és defensive preflight elv;
- célzott tesztesetek hozzáadása.

### 4.4 Aura-payment preflight

Commit:

```text
5ee20cf199da53818e576726ed378be384d65df6
```

Forrásszinten elkészült:

- runtime lookup catalog;
- Realm és card type normalizálás;
- nyomtatott Aura-költség betöltés és validáció;
- Aura-payment preflight;
- forrásválasztási és AETHER-policy alap;
- final-state recheckhez szükséges preflight/selection alapok;
- Magnitúdótól elkülönített payment modell;
- célzott tesztesetek hozzáadása.

### Bizonyítéki korlát

A repositoryban nem található kapcsolt GitHub Actions workflow run vagy status check ezekhez a gameplay commitokhoz. A forrás és a tesztek jelenléte ellenőrzött, a tényleges aktuális Debug/Release PASS állapot még újrafuttatandó.

---

## 5. Jelenlegi production scope

### Megvan

- authoritative C# MatchState;
- player/card instance alapok;
- deck, hand, discard és Wellspring state;
- draw;
- end turn;
- normál Beáramlás;
- viewer-safe snapshot/event boundary;
- runtime card definition alap: card ID, Magnitúdó, nyomtatott Aura-költség, Realm és card type;
- runtime lookup normalizálás;
- Magnitúdó-preflight;
- Aura-payment preflight és selection-alap.

### Nincs még production szinten

- `play_card` action;
- teljes Domain state és placement transition;
- entity entry-state;
- Aura-források tényleges kimerítése egy accepted kijátszás részeként;
- teljes phase és priority;
- reaction;
- combat;
- ability executor;
- win/loss;
- replay;
- production packaging véglegesítése.

---

## 6. Aktuális munkaszakasz

### Dokumentációs konszolidáció

Cél:

- egyetlen aktuális állapotdokumentum;
- append-only mérföldkőnapló;
- ritkán változó fájltérkép;
- navigációs README-k;
- a régi status/plan fájlok csak történeti átirányítók.

A konszolidáció után normál mérföldkőnél nem kell 8–12 dokumentumot frissíteni.

---

## 7. Következő production kódolási kapu

### Egyszerű Entitás-kijátszás vertical slice

A pontos scope-ot a kódolás előtt röviden rögzíteni kell, de a következő logikai kapu:

1. `play_card` action contract és typed payload;
2. aktív játékos, priority, ownership/controller és Hand membership validáció;
3. runtime card type = `entity`;
4. Magnitúdó-preflight;
5. Aura-payment preflight és forrásválasztás;
6. final revalidation közvetlenül commit előtt;
7. minimális production Domain destination/placement modell;
8. atomic Hand → Domain transition;
9. kiválasztott Aura-források `active → exhausted` módosítása ugyanabban a commitban;
10. typed, viewer-safe eventek;
11. reject-no-mutation és determinism tesztek.

Nem szabad egyszerre combatot, reactiont vagy általános ability executort hozzáadni.

---

## 8. Következő ellenőrzési kapu

A következő production kód előtt vagy azzal együtt:

1. `Aeterna.Engine.sln` Debug build;
2. Release build;
3. teljes `Aeterna.Engine.Tests`;
4. canonical fixture regresszió;
5. determinism ellenőrzés;
6. `git diff --check`;
7. eredmény rövid rögzítése a mérföldkőnaplóban.

Sikertelen futás esetén a jelen dokumentum nem állíthat PASS státuszt.

---

## 9. Párhuzamos, nem blokkoló munkasávok

### Learning

Következő kijelölt projekt:

```text
Valyreon/seven-card-game-godot
```

### Kártyamegjelenítés és fólia

A Simeydotme CSS-holografikus kutatás megőrzendő ötlet- és tudásforrás.

A benne felsorolt fóliaprofilok:

- nem véglegesek;
- később a rarityrendszerrel együtt tervezendők;
- támogatniuk kell általános és kártyaspecifikus profileltéréseket;
- támogatniuk kell artworkhöz illeszkedő egyedi maszkot és mintairányt;
- nem korlátozhatók előre rögzített profilnévlistára.

Példa a későbbi egyedi rétegre: az artworkön szereplő Hold köré rendezett koncentrikus fóliaminta.

---

## 10. Nyitott, de nem azonnali blokkolók

- production package identity és schema véglegesítése;
- Windows packaging;
- replay;
- hosszú soak teszt;
- production AI-vs-AI;
- teljes Godot player UI;
- fólia- és rarityrendszer részletes tervezése;
- learning kutatási sorozat folytatása.

---

## 11. Dokumentációs frissítési szabály

Elfogadott mérföldkő után normál esetben csak:

1. ez a fájl frissül;
2. a `CHECKPOINTS.md` végére új bejegyzés kerül.

Más dokumentum csak akkor módosul, ha a saját tartós szerepe változott.

Köztes javítócommit nem igényel automatikus dokumentációfrissítést.

---

## 12. Codex-használati szabály

- dokumentáció, elemzés és fájlkarbantartás: Codex nélkül;
- Codex: production programozásra vagy olyan technikai feladatra, amely másképp nem végezhető el hatékonyan;
- dokumentumcommitok külön kezelhetők a kódcommitoktól.

---

## 13. Következő folytatási utasítás

1. fejezd be és ellenőrizd a dokumentációs konszolidációt;
2. futtasd újra a production C# build- és tesztláncot;
3. rögzítsd a bizonyított eredményt a mérföldkőnaplóban;
4. utána indulhat az egyszerű Entitás-kijátszás legkisebb production vertical slice-a;
5. a külső learning sorozat a `Valyreon/seven-card-game-godot` projekttel folytatható.
