# AETERNA Game Engine – Runtime Comparison Fixture Specification

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-20  
**Státusz:** elfogadott comparison fixture és aktív regressziós referencia  
**Fixture:** `minimal_draw_end_turn_v1`  
**Canonical SHA-256:** `650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`  
**Aktuális repository-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Ez a dokumentum a runtime-nyelvi döntési kapuban használt közös, minimális fixture jelentését és jövőbeli regressziós szerepét rögzíti.

A fixture már nem implementáció előtti terv.

Bizonyított felhasználások:

- Python direct reference;
- Python sidecar headless;
- Godot–Python sidecar proof;
- pure C# RuntimeCandidate;
- Godot .NET/C# in-process proof.

A production C# engine C.5B szakaszában ugyanezt a fixture-t újra kell reprodukálni.

---

## 1. Cél

A fixture bizonyítja, hogy egy runtime képes:

1. determinisztikus initial state létrehozására;
2. action request fogadására;
3. expected state version ellenőrzésére;
4. accepted transition végrehajtására;
5. stale request elutasítására mutation nélkül;
6. typed event előállítására;
7. viewer-specifikus snapshot készítésére;
8. hidden-information redakcióra;
9. legal action generálására;
10. canonical JSON előállítására;
11. azonos inputból byte-szinten azonos eredményre.

Nem bizonyít teljes AETERNA gameplayt.

---

## 2. Nem része a fixture-nek

- Wellspring production integráció;
- Beáramlás/`infusion`;
- Magnitúdó;
- Aura-payment;
- `play_card`;
- Domain placement action;
- reaction;
- combat;
- ability executor;
- Pecsét teljes state;
- victory/defeat;
- production packaging.

---

## 3. Kötelező fixture-lépések

A canonical sequence:

1. initial state;
2. player 1 `draw_card`;
3. stale expected-state-version action rejection;
4. player 1 `end_turn`;
5. player 2 `draw_card`;
6. player 1 snapshot;
7. player 2 snapshot;
8. legal action checkpointok;
9. ordered typed event log;
10. canonical result serialization;
11. SHA-256.

A stale request:

- rejected;
- nem változtat state-et;
- nem növeli state versiont;
- nem növeli event sequence-et;
- nem módosítja a request objektumot;
- stabil reason/diagnostic eredményt ad.

---

## 4. Kötelező contractjelentés

A belső osztály- és fájlszerkezet eltérhet.

Azonos jelentés szükséges:

- match identity;
- player identity;
- request identity;
- expected state version;
- action type;
- accepted/rejected;
- reason;
- state version before/after;
- zone transition;
- turn transition;
- event order;
- legal action;
- player-visible snapshot;
- hidden-information redaction.

---

## 5. Fixture input

A fixture envelope minimuma:

- `schema_version`;
- `fixture_id`;
- `description`;
- `runtime_package_ref`;
- `seed`;
- `initial_state_ref` vagy determinisztikus deckdefiníció;
- `step_plan`;
- `expected_artifacts`;
- `canonicalization_profile`;
- `comparison_profile`;
- metadata.

A fixture nem tartalmazhat runtime-jelöltre szabott szabálylogikát.

---

## 6. Initial state

Minimum:

- stabil match ID;
- két játékos;
- stabil deck ID-k;
- determinisztikus deck sorrend;
- state version;
- active player;
- priority player;
- minimal phase;
- üres event log;
- card instance registry vagy azonos jelentésű state;
- hidden deck contents player-facing redakciója.

A pontos card instance ID-k determinisztikusak.

---

## 7. Action requestek

Minimum mezők:

- schema version;
- request ID;
- match ID;
- player ID;
- expected state version;
- action ID vagy action type;
- payload.

A fixture request ID-k stabilak, de nem válhatnak az általános production EngineSession hardcoded logikájává.

---

## 8. Draw transition

Accepted draw:

- a deck következő lapja kézbe kerül;
- zónatagság és registry konzisztens;
- state version növekszik;
- typed `zone_move` event készül;
- legal action és snapshot frissül.

Player-facing:

- saját húzott lap látható;
- ellenfélnek csak a kéz count változása;
- deck tartalma rejtett.

---

## 9. Stale rejection

A stale action olyan expected state versiont használ, amely már nem az aktuális.

Kötelező eredmény:

- `accepted: false`;
- stabil reason/diagnostic;
- state byte-szinten vagy szemantikailag változatlan;
- event log változatlan;
- request változatlan;
- nincs részleges transition.

Ez a fixture egyik legfontosabb authority-bizonyítéka.

---

## 10. End-turn transition

Accepted end-turn:

- active player vált;
- priority player a minimal modell szerint frissül;
- state version növekszik;
- typed `turn_transition` event készül;
- legal action lista frissül.

Nem követeli meg:

- teljes phase reset;
- awakening;
- activity refresh;
- trigger window;
- turn-start effects.

---

## 11. Snapshot

Mindkét játékos számára külön player-visible snapshot készül.

Kötelező visibility:

- saját kéz látható;
- ellenfél kéz redacted/count-only;
- deck count-only;
- public state látható;
- technikai belső registry nem szivárog;
- debug-only adatok nem kerülnek player snapshotba.

A snapshot ugyanahhoz a state versionhöz kötött.

---

## 12. Eventek

Aktív fixture-eventek:

- `zone_move`;
- `turn_transition`.

Minimum event tulajdonságok:

- stabil event ID vagy sequence;
- event type;
- match ID;
- state version;
- actor/cause;
- structured payload;
- visibility-safe projection;
- determinisztikus sorrend.

A fixture nem követel általános `action_resolved` eventet.

---

## 13. Legal actionök

A runtime számítja.

A fixture ellenőrzi:

- az aktív játékos lépéseit;
- state-versionhöz kötött legal action listát;
- accepted transition utáni frissülést;
- stale/invalid action elutasítását;
- determinisztikus sorrendet.

A frontend vagy bot nem találhat ki külön legalitást.

---

## 14. Canonical serialization

Kötelező profile:

- UTF-8;
- BOM nélkül;
- LF;
- ordinal key ordering;
- stabil array-sorrend;
- egész számok egész formában;
- stabil null/hiány policy;
- canonical JSON;
- SHA-256 lowercase hex.

A dictionary természetes enumerációs sorrendje nem elegendő.

---

## 15. Elfogadott eredmény

Canonical SHA:

`650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d`

Rögzített canonical result méret:

`210730` byte.

A konkrét artifactok repositorybeli expected/candidate mappákban találhatók.

A SHA önmagában nem elég: semantic és negative teszt is szükséges.

---

## 16. Mutation negative proof

A C# proofban a fixture seed módosítása:

- `1 → 2`

eltérő canonical eredményt adott, és a validator elvárt:

- `CANONICAL_SHA_MISMATCH`

eredménnyel állt meg.

Ez bizonyítja, hogy a runtime nem egyszerűen előre tárolt SHA-t ad vissza.

A production C# regresszióban hasonló negative proof megőrzendő.

---

## 17. Elfogadott proofok

### Python reference

Szerep:

- expected-output oracle;
- contractjelentés;
- comparison alap.

### Python sidecar

Státusz:

- `COMPLETE_AND_FROZEN`.

Bizonyította:

- process/TCP integráció;
- lifecycle;
- canonical output.

### C# RuntimeCandidate

Státusz:

- `COMPLETE_AND_ACCEPTED`.

Bizonyította:

- pure C# futás;
- Godot .NET in-process bridge;
- nincs Python/TCP/külön engine-processz;
- canonical output;
- 100-run determinisztika;
- negative proof;
- Debug/Release és visual/headless PASS.

---

## 18. Production C# követelmény

A C.5B production `Aeterna.Engine`:

- nem hivatkozhat a candidate hardcoded fixture-lépéseire szabálylogikaként;
- általános EngineSession API-t használ;
- külön fixture adapterrel futtatja a sequence-et;
- ugyanazt a canonical SHA-t reprodukálja;
- megtartja az invalid fixture és stale request negative teszteket;
- Godot nélkül is futtatható;
- Godotból in-process elérhető;
- headless hoston JSON/JSONL interfészt ad.

A candidate proof zöld marad a migráció alatt.

---

## 19. Regressziós szabály

A fixture futtatandó:

- contractmódosításkor;
- serializer-módosításkor;
- state model módosításkor;
- action request/response módosításkor;
- player snapshot módosításkor;
- Godot bridge módosításkor;
- Python–C# adapter módosításkor;
- production engine foundation elfogadásakor.

Canonical SHA csak explicit, reviewzott contractváltozás után frissíthető.

---

## 20. Korlát

A fixture PASS nem jelenti, hogy:

- a teljes játék szabályhű;
- a gameplay complete;
- a packaging kész;
- a performance megfelelő;
- a hidden information minden jövőbeli zónánál kész;
- az AI játékosszerű;
- a kártyák képességei működnek.

A fixture minimális authority-, determinism- és integration proof.

---

## 21. Kapcsolódó dokumentumok

- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `ARCHITECTURE.md`
- `TECHNOLOGY_DECISIONS.md`
- `CONTRACT_STATUS.md`
- `PROTOTYPE_STATUS.md`
- `checkpoints/ENGINE_CHECKPOINT.md`

A korábbi 1.0-s, implementáció előtti megfogalmazás a Git-történetben megmarad. Az 1.1-es dokumentum a proof utáni aktív regressziós specifikáció.
