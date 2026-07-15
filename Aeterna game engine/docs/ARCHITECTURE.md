# AETERNA Game Engine – Architecture

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 2.1  
**Dátum:** 2026-07-15  
**Státusz:** aktív működési architektúra és nyitott termékarchitektúra-dokumentum  
**Aktuális technikai bázis:** `84a7e8f42d313ed58689bbb975c7d6c85ab6e87b`

Ez a dokumentum külön kezeli:

- a jelenleg működő fejlesztési architektúrát;
- az elfogadott contract- és réteghatárokat;
- a végleges Python–Godot/GDScript termékarchitektúra még nyitott részeit.

Kapcsolódó dokumentumok:

- `TECHNOLOGY_DECISIONS.md`
- `DECISION_MAP.md`
- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`
- `CURRENT_OPEN_QUESTIONS.md`
- `CURRENT_PROTOTYPE_STATUS.md`
- `CURRENT_CONTRACT_STATUS.md`
- `checkpoints/CURRENT_ENGINE_CHECKPOINT.md`

Az `OPEN_QUESTIONS.md` és az `OPEN_QUESTIONS_DECISIONS.md` együtt olvasandó. Ezek alapján a Python backend + Godot frontend erős hosszú távú jelölt, de a végleges runtime- és packaging-architektúra még technológiai bizonyítást igényel.

---

## 1. Stabil architektúra-alapelvek

A következő elvek a végleges technológiai modelltől függetlenül érvényesek:

- előbb contract, utána implementáció;
- egy adott futásban pontosan egy authoritative state legyen;
- a UI nem lehet szabályforrás;
- a frontend és az AI nem találgat legalitást;
- state mutation csak validált engine transition útján történhet;
- a kliens action requestet küld;
- az engine action response-t, eventet és projectiont ad;
- player-visible és debug contract külön marad;
- rejtett információt projection véd;
- eventek determinisztikusak és auditálhatók;
- runtime package statikus programadat, nem szabálymotor.

---

## 2. Jelenleg működő architektúra

A jelenlegi fejlesztési és tesztelési rendszer:

    Hivatalos szabályforrások
            ↓
    Google Sheets / XLSX kártyaadat és LOOKUPS
            ↓
    Python export, normalizálás és validáció
            ↓
    Validált runtime package
            ↓
    Python minimal rules engine
            ↓
    MatchState + invariánsok
            ↓
    Legal actions / action request / transition
            ↓
    Typed events + új state version
            ↓
    Player-visible / debug / AI projection
            ↓
    Godot loader, debug UI és későbbi kliensintegráció

Ez a lánc a jelenlegi bizonyított munkamodell.

Nem jelenti automatikusan, hogy a végleges termék pontosan külön Python process + Godot process formában készül.

---

## 3. Hivatalos szabályréteg

Elsődleges források:

- `AETERNA – HIVATALOS ALAPJÁTÉK FŐFORRÁS 1.4v.docx`
- `AETERNA – HIVATALOS KIEGÉSZÍTŐ FŐFORRÁS 1.4v.docx`

A kód, structured mező vagy tanulóprojekt nem írhatja felül ezeket emberi döntés nélkül.

---

## 4. Szerkesztési adatforrás és runtime package

### Szerkesztési forrás

- Google Sheets;
- abból letöltött XLSX munkaforrások;
- aktív kártyaadatbázis;
- `LOOKUPS.xlsx`.

### Python adatpipeline

Feladata:

- XLSX beolvasás;
- export;
- canonical normalizálás;
- legacy alias audit;
- validáció;
- runtime package build;
- diagnostics és report;
- Godot consumption copy publikálása.

### Runtime package

Statikus adatcontract:

- kártyák;
- deckek;
- lookupok;
- aliasok;
- ability registry;
- engine-support;
- diagnostics;
- build report.

Nem tartalmaz futó authoritative MatchState-et.

---

## 5. Python minimal rules engine

A jelenlegi aktív szabálymotor-implementáció helye:

- `Aeterna game engine/python/`

Bizonyított felelőssége:

- MatchState és PlayerState;
- state version;
- card instance registry;
- state invariantok;
- legal action alap;
- action request/response;
- atomikus transitionök;
- typed eventek;
- player-visible és debug projection;
- AI-vs-AI és trajectory;
- determinisztikus headless tesztelés.

A Python engine jelenleg authoritative a saját futásaiban és tesztjeiben.

Ez a legerősebb fejlesztési bázis, ezért a következő belső szabálymotoros feladatok itt készülnek.

A végleges termékbe történő beágyazás, sidecar-futtatás vagy más integráció még nyitott.

---

## 6. Godot réteg

Bizonyított jelenlegi szerepek:

- runtime package loader;
- registryk;
- debug contractok betöltése;
- snapshot viewer;
- legal action debug panel;
- event log view;
- unified dashboard;
- headless smoke;
- későbbi player UI alap.

Biztos réteghatár:

- Godot UI node nem tartalmazhat rejtett, ellenőrizetlen szabálylogikát;
- a kliens nem módosíthat authoritative state-et;
- a Godot a kapott contractokból épít megjelenítést és input requestet.

Nyitott kérdés:

- a végleges termékben a teljes rules runtime Pythonban marad-e;
- készül-e részleges vagy teljes GDScript runtime;
- milyen bridge és packaging modell működik megfelelően.

A GDScript runtime-alkalmasság nincs végleg elutasítva, de jelenleg nem épül párhuzamos teljes engine.

---

## 7. MatchState és PlayerState

A jelenlegi Python MatchState kezeli:

- match identity;
- state version;
- aktív és priority player;
- minimal phase;
- event log;
- player state-ek;
- card instance registry;
- Domain topológiák;
- Domain occupancy state-ek.

PlayerState listás zónák:

- deck;
- hand;
- discard.

Következő bővítés:

- Wellspring.

A MatchState belső authoritative adat, normál kliensnek nem exportálható közvetlenül.

---

## 8. Card instance és zónák

A card definition és a meccsbeli card instance külön objektum.

Card instance fő adatai:

- instance ID;
- Card_ID;
- owner;
- controller;
- zone;
- zone index;
- visibility;
- activity state;
- sequence adatok.

Jelenlegi zónák:

- deck;
- hand;
- discard;
- domain;
- wellspring.

A Wellspring jelenleg izolált contract; production integrációja a következő engine-feladat.

---

## 9. Domain és board

Játékosonként:

- 6 Áramlat;
- 6 Horizont;
- 6 Zenit;
- 6 Pecsét-pozícióreferencia;
- 12 card occupancy slot.

Az occupancy és a card instance registry kapcsolata kétirányúan validált.

A player-visible board public projection, nem teljes MatchState-dump.

---

## 10. Player-visible és debug projection

Jelenlegi player snapshot:

- saját kéz látható;
- ellenfél kéz redacted;
- deck count-only;
- discard public;
- Domain board public;
- Wellspring még nincs projektálva.

A fair AI ugyanazt a player-visible observationt használja, mint az emberi játékos.

Debug mód külön contracton adhat több információt.

---

## 11. Event- és action-architektúra

Aktív actionök:

- `draw_card`
- `end_turn`

Aktív typed eventek:

- `zone_move`
- `turn_transition`

Későbbi sorrend:

- Wellspring integráció;
- Beáramlás;
- Magnitúdó;
- Aura-payment;
- activity mutation;
- `play_card`;
- phase és priority;
- combat;
- ability execution.

---

## 12. Tanulóprogramok architektúra-auditja

A tanulóprogramok vizsgálata külön technológiai kapu.

Ellenőrizendő:

- tényleges forrás elérhető-e;
- rules engine nyelve;
- Godot és Python együttműködés;
- process/bridge modell;
- state authority;
- kliens–engine határ;
- packaging;
- hidden information;
- replay és determinisztika;
- AETERNA-ra átfordítható clean-room minta.

A repositoryban jelenleg az összefoglaló dokumentum biztosan elérhető, a teljes hivatkozott forrásfák nem azonosíthatók egyértelműen.

---

## 13. Lehetséges végleges termékarchitektúrák

### Jelölt A – Python backend + Godot frontend

Jelenleg a legerősebb jelölt.

Bizonyítandó:

- bridge;
- packaging;
- process lifecycle;
- latency;
- crash recovery;
- versioning;
- Windows launch.

### Jelölt B – GDScript rules runtime + Godot frontend

Nem aktív implementációs főág, de nem végleg elutasított.

Bizonyítandó:

- maintainability;
- headless és batch tesztelés;
- AI-vs-AI;
- determinisztika;
- adatpipeline-integráció;
- Python modellekkel való összevetés.

### Jelölt C – Megosztott/hibrid runtime

Nagyobb duplikációs és eltérési kockázat.

Csak explicit határral és összehasonlító bizonyítékkal fogadható el.

---

## 14. Python–GDScript comparison

A comparison kérdés nyitott.

Nem szükséges első lépésként két teljes engine-t építeni.

Lehetséges vizsgálat:

- azonos contract parser;
- azonos minimal transition;
- determinisztikus JSON összevetés;
- Python–Godot bridge;
- teljesítmény és hibakezelés;
- packaging proof;
- tanulóprogram-minta reprodukciója.

A pontos scope a tanulóprogram-audit után döntendő el.

---

## 15. Következő két párhuzamos munkasáv

### Engine-sáv

1. Wellspring production integráció.
2. Player-visible Wellspring.
3. Beáramlás.
4. Magnitúdó és payment.
5. Első `play_card`.
6. Vertical slice.

### Technológiai bizonyítási sáv

1. Open Questions és Decisions közös triázs.
2. Tanulóprogram-leltár.
3. Python–Godot minták auditja.
4. Comparison scope.
5. Minimal bridge prototype.
6. Packaging proof.
7. Végleges termékarchitektúra döntés.

---

## 16. Jelenlegi rövid összefoglaló

- A Python minimal engine a jelenlegi működő authoritative fejlesztési bázis.
- A Godot loader-, registry-, debug- és UI-alap működik.
- A contract-first réteghatár stabil döntés.
- A frontend nem lehet szabályforrás.
- A belső Python engine-fejlesztés folytatható.
- A végleges Python–Godot/GDScript runtime- és packaging-architektúra még nyitott.
- A tanulóprogram-audit és a Python–GDScript comparison továbbra is szükséges döntési kapu.
