# AETERNA – Ggross98/Godot-CardPileFramework ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.4
- **Dátum:** 2026-07-23
- **Státusz:** előzetes, repository-forrásokra épülő elemzés
- **Fő elemzési fájl:** `learning/analyses/ggross98__godot-cardpileframework.md`
- **Későbbi részanyagok:** `learning/analyses/ggross98__godot-cardpileframework/`
- **Vizsgálati commit:** `0f65a62639d8fd8465ce7604fdac090bb6ab7dbd`
- **Vizsgálati korlát:** helyi build és futtatás ebben a körben nem történt
- **Besorolás:** Godot/C# kártya-UI és halomkezelő framework; nem teljes authoritative TCG/CCG szabálymotor

# 1. Projektazonosítás

| Mező | Érték |
|---|---|
| Repository | `Ggross98/Godot-CardPileFramework` |
| URL | https://github.com/Ggross98/Godot-CardPileFramework |
| Branch | `main` |
| Vizsgált commit | `0f65a62639d8fd8465ce7604fdac090bb6ab7dbd` |
| Motor | Godot 4.6.2 .NET |
| Target framework | .NET 8 (`net8.0`) |
| Nyelv | C# |
| Licenc | MIT |
| Repository állapot | nyilvános, nem archivált |
| AETERNA-prioritás | P0 – közvetlen Godot/C# presentation referencia |

A `.csproj` a `Godot.NET.Sdk/4.6.2` SDK-t és a `net8.0` targetet rögzíti. A
`project.godot` C#-os Godot 4.6 projektet deklarál. A solution egyetlen fő projektet
tartalmaz Debug, ExportDebug és ExportRelease konfigurációkkal.

# 2. Vezetői összefoglaló

A projekt könnyű C#-os Godot framework kártya-Control objektumok, kéz-, húzó- és
dobóhalmok, dropzone-ok, drag-and-drop, animált pozicionálás és JSON-alapú
kártyaadatok kezelésére.

A legfontosabb következtetés:

> **A framework jó Godot/C# kártya-UI és presentation referencia, de nem használható
> az AETERNA authoritative szabálymotorjának alapjaként.**

A repository saját zónaállapotként Godot `Card` UI-node-okat tárol `CardDropzone`
objektumokban. A példajáték energiát, HP-t és pajzsot scene node-ban kezel, a cost
ellenőrzés és effect végrehajtás pedig közvetlenül egy UI dropzone-ban történik.

Az AETERNA számára elsősorban ezek tanulságosak:

- CardView hover/click/drag signalok;
- curve-alapú kézelrendezés;
- stack/pile megjelenítés;
- face-up/face-down kezelés;
- top-card interaction;
- központi Godot presentation manager;
- könnyű, örökölhető vizuális CardData Resource.

Nem szabad átvenni:

- Godot node mint authoritative card instance;
- UI-lista mint authoritative zone;
- dropzone-ban számított legal action;
- UI-ban végrehajtott cost és effect;
- scene-tree bejárás mint rules lookup;
- nem seedelt shuffle;
- schema nélküli JSON és runtime script-path betöltés.

# 3. Előzetes értékelés

| Szempont | Pontszám | Indok |
|---|:---:|---|
| Technológiai illeszkedés | 5/5 | Godot 4.6.2, C#, .NET 8 |
| Godot UI tanulási érték | 5/5 | hand, pile, dropzone, drag, hover |
| Rules-engine érték | 2/5 | egyszerű demó, külön domain engine nélkül |
| Adatpipeline érték | 3/5 | JSON + Resource, de schema validation nélkül |
| Multiplayer | 0/5 | nem találtunk multiplayer réteget |
| AI/szimuláció | 0/5 | nincs headless vagy agent API |
| Determinizmus | 1/5 | shuffle van, seed/replay contract nincs |
| Tesztelhetőség | 1/5 | Godot node-okhoz erősen kötött |
| Dokumentáltság | 3/5 | README és részleges XML summary-k |
| Licenc | 5/5 | MIT |
| Összesített prioritás | **P0** | presentation layerben közvetlenül releváns |

# 4. Fő komponensek

| Komponens | Felelősség | AETERNA-megfelelő |
|---|---|---|
| `CardData` | Godot Resource, vizuális és egyedi kártyaadat | visual metadata adapter |
| `Card` | UI, input, hover, drag, textúra, drop keresés | CardView |
| `CardDropzone` | Card node-ok listája, drop és layout | ZoneView / DropTargetView |
| `CardManager` | card scene létrehozás, signal relay | presentation coordinator |
| `SimpleCardHand` | kézelrendezés és interaction | HandView |
| `SimpleCardPile` | stack és top-card interaction | Deck/Discard View |
| `SimpleCardPileManager` | JSON, draw/hand/discard UI-kezelés | prototípus manager |
| `CardBattle` | demo turn state | demo controller |
| `SkillZone` | demo cost validation és effect | UI action prototype |

# 5. Kártyaadat és instance-modell

## 5.1 `CardData`

A `CardData` Godot `Resource`. Alapmezői:

- `nice_name`;
- frontface texture path;
- backface texture path;
- resource script path.

A `LoadProperties` minden JSON-kulcsot dinamikusan átad a Godot `Set` metódusnak.

### Erősség

- gyors prototípus;
- kevés boilerplate;
- örökölhető Resource;
- Inspector-kompatibilis;
- vizuális adatokhoz kényelmes.

### Kockázat

- nincs explicit schema;
- nincs kötelező mezőlista;
- nincs stabil diagnosztika;
- hibás típus és ismeretlen kulcs kezelése nem szigorú;
- a JSON `resource_script_path` mezőből C# scriptet választ;
- vizuális és játékmeneti adat keveredik.

Az AETERNA validated runtime package-je helyett ez nem használható.

## 5.2 Definition, instance és view összemosása

A frameworkben:

- `CardData` közelít a definitionhöz;
- `Card` egyszerre UI-node, inputkezelő és zónában tárolt kártyaobjektum.

Nincs külön:

- stabil card instance ID;
- owner;
- controller;
- authoritative zone;
- state version;
- viewer projection.

Az AETERNA helyes rétegei:

```text
RuntimeCardDefinition
CardInstance
CardProjection
CardView
```

A repositoryból csak a `CardView` és `ZoneView` minták használhatók közvetlenül.

# 6. UI és interaction

## 6.1 Card signalok

A `Card` külön signalokat ad hover, unhover, bal/jobb kattintás és felengedés esetére.
A `CardManager` ezeket központilag továbbítja.

Ez jó presentation minta, amennyiben a signal csak UI intent:

```text
CardView signal
→ Godot input adapter
→ engine request
→ validation
→ authoritative transition
→ snapshot/event
→ UI refresh
```

A CardView nem módosíthatja közvetlenül az engine állapotát.

## 6.2 Drag-and-drop

A `Card` kattintáskor az egérhez mozog. Felengedéskor a scene root alatt megkeresi az
összes `CardDropzone` node-ot, majd `CanDropCard` és `DropCard` hívást végez.

UI-demóként egyszerű és jól követhető. Production rendszerben azonban:

- a scene tree nem lehet legal-action forrás;
- a `CanDropCard` csak az engine legal action projectionját tükrözheti;
- a drop engine requestet küldjön;
- sikertelen request után authoritative snapshot állítsa vissza a nézetet;
- pending selection alatt csak engine által engedélyezett célok jelenjenek meg.

## 6.3 Kézelrendezés

A `SimpleCardHand`:

- maximális kézméretet tart;
- maximális szélességen osztja el a lapokat;
- Curve alapján függőleges ívet és forgatást ad;
- külön Z-indexet használ normál, hover és clicked állapotban;
- képpel felfelé vagy lefelé renderel.

Ez közvetlenül hasznos AETERNA UI-referencia.

## 6.4 Halomnézet

A `SimpleCardPile`:

- konfigurálható stack irányt;
- stack gapet;
- maximális látható mélységet;
- face-up/face-down állapotot;
- top-card-only interactiont támogat.

Ez Deck, Discard és más rendezett zónák vizualizációjához használható.

# 7. Zóna- és halomkezelés

A `CardDropzone` `_holdingCards` kollekciója `Godot.Collections.Array<Card>`.
A zónatagságot az jelenti, hogy mely UI-node van ebben a listában.

A `CardManager.SetCardDropzone`:

1. eltávolítja a kártyát a korábbi dropzone-ból;
2. hozzáadja az újhoz;
3. signalt küld;
4. frissíti a pozíciókat és Z-indexeket.

UI-frameworkként megfelelő. Authoritative engine-ként hiányzik:

- stabil instance ID;
- owner/controller;
- atomic request;
- state version;
- event sequence;
- rollback;
- hidden-information projection;
- determinisztikus transition.

A `SimpleCardPileManager` Draw, Hand és Discard halmot kezel, JSON-ból UI-kártyákat
hoz létre, kever, húz, discardol és üres draw pile esetén visszakeverheti a discardot.

A production AETERNA engine-ben ezek az engine state részei maradnak; a Godot manager
csak snapshotot renderelhet.

# 8. JSON és adatbiztonság

A `JsonUtils.LoadJsonAs<T>` teljes fájlt olvas, `Json.ParseString` hívást végez, majd
hiba esetén csak `GD.Print` üzenetet ad és default értéket küld vissza.

A `SimpleCardPileManager`:

- `nice_name` alapján keres;
- JSON-ból `resource_script_path` értéket olvas;
- C# scriptet tölt;
- abból `CardData` példányt készít;
- dinamikusan ráírja a mezőket.

Production környezetben kerülendő:

- silent/default hibakezelés;
- stabil diagnosztikai kód hiánya;
- schema validation hiánya;
- `nice_name` mint stabil ID;
- JSON-ból scriptválasztás;
- rules és visual data keverése.

A Godot réteg csak engine által validált, szűk visual contractot kapjon, például:

```text
CardVisualDefinition
- card_id
- localized_name
- art_asset_id
- frame_style_id
- icon_asset_ids
- animation_profile_id
```

# 9. Példajáték szabálylogikája

A `CardBattle : Node2D` közvetlenül tárolja az energiát, pajzsot és HP-t.
A `StartTurn` feltölti az energiát, nullázza a pajzsot, eldobja a teljes kezet és öt lapot húz.
Az `EndTurn` üres; nincs külön turn state machine.

A `SkillZone.CanDropCard`:

- konkrét C# runtime típust ellenőriz;
- kiolvassa a costot;
- abszolút `/root/CardBattle` node pathon kéri le az energiát;
- stringgel ellenőrzi a `"Skill"` típust;
- UI-szinten dönt a jogszerűségről.

A `OnCardDropped`:

- közvetlenül levonja az energiát;
- `"Block"` név esetén pajzsot növel;
- discard pile-ba mozgat.

Ez production rules mintának nem alkalmas, mert nincs:

- teljes preflight validation;
- atomic transition;
- state version;
- event;
- target/selection contract;
- rollback;
- engine-owned instance;
- általános effect dispatch.

A vizuális drop target mintája viszont használható, ha az engine legal action listája vezérli.

# 10. Determinizmus és tesztelés

A draw pile Godot `Shuffle()` hívást használ. A vizsgált kódban nincs:

- explicit seed;
- RNG abstraction;
- determinisztikus shuffle contract;
- random event log;
- replay;
- fixture.

A távoli vizsgálatban:

- a solution egyetlen fő projektet tartalmaz;
- nem találtunk külön test projektet;
- nem találtunk xUnit, NUnit vagy MSTest hivatkozást;
- nem találtunk CI build/test workflowt.

Ez negatív keresési eredmény, nem teljes helyi clone-audit.

# 11. Licenc

A repository MIT licencű. Kódátvétel megengedett, de a copyright- és licencszöveget
meg kell őrizni a szoftver lényeges részeiben.

A demó grafikai assetjeinek licence külön vizsgálandó.

Javasolt használat:

- architekturális inspiráció: igen;
- UI-algoritmus adaptálása: igen, dokumentáltan;
- közvetlen dependency: jelenleg nem;
- rules engine alap: nem;
- szelektív kódátvétel: csak tudatos attributionnel.

# 12. Erősségek

1. Godot 4.6.2 és C#/.NET 8.
2. Kis, áttekinthető framework.
3. Hasznos CardView signalok.
4. Jó kéz- és stack layout.
5. Örökölhető CardData.
6. JSON-alapú prototípus-adat.
7. Pile update signalok.
8. Pluginmappaként másolható.
9. MIT licenc.
10. Tartalmaz card-battle demót.

# 13. Gyengeségek

1. UI-node egyben card instance.
2. Dropzone-lista egyben zone state.
3. Nincs authoritative domain state.
4. Nincs legal action contract.
5. Nincs request validation pipeline.
6. Nincs state version.
7. Nincs event/replay.
8. Nincs hidden-information model.
9. Nincs multiplayer authority.
10. Nincs seedelt determinisztika.
11. Nem találtunk automatizált teszteket.
12. A JSON nem schema-validált.
13. JSON-ból C# script tölthető.
14. `nice_name` lookup-kulcs.
15. Stringes card type/effect dispatch.
16. Scene-root bejárás és abszolút node path.
17. Hiba esetén default visszatérés.
18. A README szerint rapid iteration alatt áll.

# 14. AETERNA számára átvehető elvek

## Közvetlenül hasznos

- CardView hover/click/drag signalok;
- curve-alapú HandView;
- stack gap és max visible depth;
- top-card-only interaction;
- face-up/face-down presentation;
- központi presentation coordinator;
- vizuális CardData Resource.

## Feltételesen hasznos

- JSON visual metadata, de csak engine-validáció után;
- dropzone interaction, de kizárólag engine legal action alapján;
- signal relay, de rules mutation nélkül.

## Nem átvehető

- Godot node authoritative instance-ként;
- UI-lista authoritative zónaként;
- dropzone-ban végzett rules validation;
- UI-ban cost levonás és effect resolution;
- scene-tree rules lookup;
- runtime JSON script path;
- nem seedelt shuffle.

# 15. Javasolt AETERNA-integrációs határ

```text
Aeterna.Engine
    RuntimeCardDefinition
    CardInstance
    MatchState
    LegalAction
    EngineEvent
    PlayerSnapshot
          │
          ▼
Godot Bridge / Projection Adapter
    CardViewModel
    ZoneViewModel
    InteractionPolicy
          │
          ▼
Godot UI
    CardView
    HandView
    PileView
    DropTargetView
    AnimationCoordinator
```

# 16. Konkrét AETERNA-javaslatok

| # | Javaslat | Réteg | Prioritás |
|---:|---|---|:---:|
| 1 | CardView hover/click/drag signal API | Godot | P1 |
| 2 | Curve-alapú HandView prototípus | Godot | P1 |
| 3 | PileView stack gap és max-depth | Godot | P1 |
| 4 | CardView-k snapshotból történő frissítése | Bridge | P0 |
| 5 | Drop targetek engedélyezése `legal_actions` alapján | Bridge | P0 |
| 6 | Drop után engine request, majd snapshot refresh | Bridge | P0 |
| 7 | Külön visual metadata contract | Runtime/Godot | P1 |
| 8 | Runtime JSON scriptválasztás tiltása | Runtime | P0 |
| 9 | Engine-seedelt zónasorrend | Engine | P0 |
| 10 | Hand/Pile Godot smoke tesztek | Tests | P2 |

# 17. Bizonyítékjegyzék

| ID | Állítás | Forrás | Sorok |
|---|---|---|---|
| E-001 | Godot 4.6.2 és net8.0 | `CardPileFramework.csproj` | 3–7 |
| E-002 | C# Godot projekt | `project.godot` | 17–32 |
| E-003 | MIT licenc | `LICENSE` | 3–22 |
| E-004 | CardData Godot Resource | `CardData.cs` | 9–27 |
| E-005 | dinamikus JSON `Set` | `CardData.cs` | 19–26 |
| E-006 | Card signalok és drag | `Card.cs` | 8–89 |
| E-007 | scene-tree dropzone keresés | `Card.cs` | 191–249 |
| E-008 | card scene és signal relay | `CardManager.cs` | 96–126 |
| E-009 | dropzone-váltás | `CardManager.cs` | 150–167 |
| E-010 | `Array<Card>` zónaállapot | `CardDropzone.cs` | 24–30, 98–172 |
| E-011 | hand layout és Z-index | `SimpleCardHand.cs` | 13–63 |
| E-012 | stack és top-card interaction | `SimpleCardPile.cs` | 8–77 |
| E-013 | draw/hand/discard manager | `SimpleCardPileManager.cs` | 10–76 |
| E-014 | JSON betöltés | `SimpleCardPileManager.cs` | 210–226 |
| E-015 | shuffle és draw | `SimpleCardPileManager.cs` | 275–300 |
| E-016 | JSON-ból C# script | `SimpleCardPileManager.cs` | 328–340 |
| E-017 | hiba esetén log + default | `JsonUtils.cs` | 9–26 |
| E-018 | demo state | `CardBattle.cs` | 7–64 |
| E-019 | demo start turn | `CardBattle.cs` | 112–132 |
| E-020 | UI cost/type validation | `SkillZone.cs` | 7–29 |
| E-021 | UI direct mutation | `SkillZone.cs` | 31–45 |
| E-022 | példa kártyaadatok | `example_card_database.json` | 3–58 |
| E-023 | egyetlen solution project | `CardPileFramework.sln` | 3–20 |

# 18. Nyitott kérdések

1. Tisztán buildelhető-e a vizsgált commit Godot 4.6.2 .NET alatt?
2. A demó minden lapot helyesen kezel-e?
3. Van-e nem indexelt teszt vagy CI?
4. A `GetCards().Shuffle()` a belső arrayt vagy másolatot kever?
5. A `SortHand` LINQ hívása ténylegesen módosítja-e a sorrendet?
6. Vannak-e event-leak vagy lifecycle problémák?
7. Milyen assetlicencek vonatkoznak a demóra?
8. Mely UI-algoritmusok adaptálhatók attributionnel?
9. Érdemes-e inkább újraimplementálni az interaction mintát?
10. Hogyan illeszthető a jelenlegi AETERNA Godot bridge-hez?

# 19. Következő lépések

## Codex nélkül elvégezhető

1. Repository letöltése `learning/sources/` alá.
2. Origin URL és commit rögzítése.
3. Godot 4.6.2 .NET import.
4. Debug és ExportRelease build.
5. Card-battle kézi smoke.
6. Hand, pile és drag viselkedés dokumentálása.
7. Scene-ek és assetlicencek vizsgálata.
8. AETERNA snapshot-alapú UI proof-of-concept tervezése.

## Később Codexszel gyorsítható

1. teljes C# call graph;
2. scene–script kapcsolatok;
3. null/lifecycle/event hibák;
4. automatikus build/test javaslat;
5. gépi összevetés az AETERNA Godot réteggel.

# 20. Végső előzetes minősítés

- **Tanulási érték:** magas a Godot/C# UI területén
- **Rules-engine érték:** alacsony–közepes
- **AETERNA-illeszkedés:** presentation layerben magas
- **Production engine-alapként:** nem alkalmas
- **Licenc:** kedvező
- **Mélyelemzés folytatása:** igen
- **Elsődleges következő cél:** helyi build és UI-viselkedési audit

# 21. Változásnapló

## Katalógushivatkozás-korrekció – 2026-07-24

- a kapcsolódó katalógus útvonala az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum értékre frissült;
- a korábbi konkrét vagy verziótlan fájlhivatkozás megszűnt.


## 0.1 – 2026-07-23

- elkészült az első repository-forrásokra épülő projektszintű elemzés;
- elkülönült a UI-framework és az authoritative rules engine szerepe;
- rögzítésre kerültek az átvehető UI-minták;
- rögzítésre kerültek a kerülendő architekturális megoldások;
- létrejött a helyi reprodukálási és későbbi Codex-mélyítés munkalistája.

## Stabil katalógushivatkozás – 2026-07-24

- a kapcsolódó katalógus logikai dokumentumszerepe az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum;
- a katalógus új verziója miatt ezt az elemzést a jövőben nem kell módosítani;
- a vizsgált repository-állapotot továbbra is az elemzés saját commit SHA-ja rögzíti.

## Hivatkozási modell javítása – 2026-07-24

- a kapcsolódó katalógus hivatkozása mostantól: az aktuális verziózott „AETERNA – LEARNING PROJECT CATALOG” dokumentum;
- az elemzés nem tartalmaz konkrét katalógusfájlnevet vagy katalógusverziót;
- új központi katalógusverzió miatt ezt a projektdokumentumot nem kell módosítani;
- a projekt vizsgált állapotának reprodukálhatóságát továbbra is a saját branch/tag,
  commit SHA és vizsgálati dátum biztosítja;
- a korábbi verziótlan központi fájlmodell felváltásra került.
