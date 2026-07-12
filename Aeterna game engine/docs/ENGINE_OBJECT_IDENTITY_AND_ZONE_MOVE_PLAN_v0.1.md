# Engine object identity és zone move terv v0.1

## 1. Rövid összegzés

Ez a terv azt rögzíti, hogyan vezessük át az AETERNA minimal engine jelenlegi Card_ID-alapú zónakezelését egy stabil, contract-first object identity és zone move modell felé.

A legfontosabb döntés: a `Card_ID` nem azonos a konkrét meccsbeli kártyapéldánnyal. A runtime package `Card_ID` rekordja kártyadefiníció. A meccs közbeni konkrét példányt `card_instance_id` azonosítja. Később ettől külön válhat a `permanent_id` és a `stack_object_id`.

Ez nem gameplay implementációs feladat. Nem vezet be új akciót, play_cardot, attackot, targetinget, paymentet, ability executort, stacket, replay rendszert vagy multiplayer rendszert. A cél egy kis, stabil architekturális irány kijelölése.

## 2. Miért kell ez a terv

A jelenlegi minimal engine már bizonyítja a contract-first útvonalat:

- runtime package betöltés;
- minimal `MatchState`;
- `draw_card` és `end_turn`;
- legal action list;
- action request és action response contract;
- `state_version`;
- `event_sequence`;
- `expected_state_version`;
- `debug_snapshot`;
- `player_visible_snapshot` stub;
- `engine_context_summary`;
- AI-vs-AI minimal runner;
- explicit `minimal_card_id_overlap_risk` guard.

A következő szabályrétegekhez viszont nem elég a Card_ID-listás modell. A tanulóprojektekből, különösen Mage/XMage, Duelyst, RLCard és boardgame.io mintáiból a fő tanulság az, hogy az engine-ben stabil objektumazonosság kell. A zónamozgás nem lehet ad hoc listaáthelyezés, mert később a célzás, replay, event log, UI projection, hidden information és AI observation mind ugyanarra az objektumazonosságra támaszkodik.

## 3. Jelenlegi probléma

Jelenleg a minimal state fő zónái:

- `deck_card_ids`;
- `hand`;
- `discard`.

Ezek Card_ID listák. A `draw_card` a `deck_card_ids` listából kiválaszt egy Card_ID-t, eltávolítja, majd a `hand` listába teszi. Ez a minimal smoke slice-hoz elég, de hosszabb távon veszélyes:

- egy deckben ugyanabból a `Card_ID`-ból több példány lehet;
- a `Card_ID` nem mondja meg, melyik konkrét példány mozgott;
- a kézben, deckben, discardban és későbbi board/stack zónákban ugyanazon Card_ID több példánya összemosódhat;
- a `minimal_card_id_overlap_risk` guard csak átmeneti védelem;
- Godot UI node nem tud stabilan egy konkrét meccsobjektumra hivatkozni;
- a player-visible snapshot később nem tudja biztonságosan kezelni a hidden informationt;
- replay és célzás esetén hiányzik az objektum történeti állapota.

## 4. Fogalmak

- `Card_ID`: runtime package kártyadefiníció azonosítója. Például egy lap rekordja a `cards.jsonl` fájlban.
- `card_instance_id`: egy konkrét meccsbeli kártyapéldány stabil azonosítója.
- `permanent_id`: későbbi, boardon lévő tartós objektum azonosítója. Nem azonos automatikusan a `card_instance_id` értékkel.
- `stack_object_id`: későbbi stacken vagy pending resolve térben lévő objektum azonosítója.
- `owner_player_id`: az a játékos, akinek a deckjéből vagy tulajdonából a példány származik.
- `controller_player_id`: az a játékos, aki az adott objektumot aktuálisan kontrollálja.
- `zone`: aktuális zóna, például `deck`, `hand`, `discard`, később `battlefield`, `stack`, `exile`.
- `zone_index`: a zónán belüli rendezett pozíció.
- `visibility`: láthatósági állapot, például `owner_only`, `public`, `hidden`, `debug_only`.
- `zone_sequence`: az adott objektum aktuális zónaállapotának verziója.
- `zone_change_counter`: alternatív vagy kiegészítő számláló az objektum zónaváltásainak követésére.
- `ObjectReference`: stabil hivatkozás egy engine objektumra.
- `ZoneMove`: zónamozgást leíró event/contract.
- `ZoneOperation`: zónamozgás előfeltételét és végrehajtási szándékát leíró engine művelet.
- `source_action_id`: az action request vagy legal action azonosítója, amelyből a zónamozgás származik.
- `event_sequence`: event logon belüli monoton növekvő eseménysorszám.
- `state_version`: elfogadott state transition utáni állapotverzió.
- `debug_snapshot`: teljesebb, debug-only állapotkép.
- `player_visible_snapshot`: játékosnak szánt, visibility-szűrt állapotkép.

## 5. Javasolt object identity modell

A meccs indulásakor a decklisták Card_ID bejegyzéseiből konkrét instance rekordokat kell létrehozni. Minden példány egyedi `card_instance_id` értéket kap. A zónák hosszú távon nem Card_ID listák, hanem `card_instance_id` listák.

Javasolt minimális card instance forma:

```json
{
  "card_instance_id": "ci:match-001:P1:deck:0001",
  "card_id": "IGN-HAM-001",
  "owner_player_id": "P1",
  "controller_player_id": "P1",
  "zone": "deck",
  "zone_index": 0,
  "visibility": "owner_only",
  "created_sequence": 1,
  "zone_sequence": 1,
  "metadata": {
    "source": "initial_deck_setup",
    "runtime_card_id_source": "runtime_package.cards"
  }
}
```

Fontos: a `Card_ID` továbbra is a kártyadefiníció. A `card_instance_id` a meccsbeli példány. Egy deckben ugyanabból a `Card_ID`-ból több instance is létrejöhet.

Később:

- `permanent_id` akkor jön létre, amikor egy instance board/permanent jellegű objektummá válik;
- `stack_object_id` akkor jön létre, amikor egy spell, ability vagy pending effect stack objektummá válik;
- ezek nem kötelezően azonosak a `card_instance_id` értékkel, mert más életciklust követhetnek.

## 6. Javasolt zone modell

Minden player rendelkezhet rendezett zónákkal:

- `deck`;
- `hand`;
- `discard`;
- később `battlefield`, `banished`, `stack`, `revealed`, `sideboard`.

Egy zóna tartalma hosszú távon:

```json
{
  "player_id": "P1",
  "zone": "hand",
  "visibility": "owner_only",
  "object_ids": [
    "ci:match-001:P1:deck:0007",
    "ci:match-001:P1:deck:0012"
  ],
  "metadata": {
    "ordered": true,
    "authority": "engine"
  }
}
```

A zóna listák csak instance azonosítókat tartalmazzanak. A Card_ID lookup mindig az instance registryn keresztül történjen.

## 7. Javasolt zone move contract

A `ZoneMove` minden sikeres zónamozgás elsődleges bizonyítéka legyen. Ez eventként is megjelenhet, és tartalmaznia kell a state transition és visibility információt.

Javasolt JSON-kompatibilis forma:

```json
{
  "event_type": "zone_move",
  "card_instance_id": "ci:match-001:P1:deck:0001",
  "card_id": "IGN-HAM-001",
  "owner_player_id": "P1",
  "controller_player_id": "P1",
  "from_zone": "deck",
  "from_zone_index": 0,
  "to_zone": "hand",
  "to_zone_index": 0,
  "source_action_id": "draw_card:1:0:P1",
  "source_action_type": "draw_card",
  "state_version": 1,
  "event_sequence": 1,
  "visibility_before": "owner_only",
  "visibility_after": "owner_only",
  "metadata": {
    "zone_operation": "move_top_or_selected_card",
    "authority": "rules_kernel",
    "applied": true
  }
}
```

Ez a forma nem jelenti azt, hogy most implementálni kell. A cél a későbbi draw átvezetés, play_card, discard, reveal, targeting és UI projection közös alapja.

## 8. Javasolt ObjectReference contract

Az `ObjectReference` egy stabil, JSON-kompatibilis hivatkozás, amely legal actionben, action requestben, targetingben, event logban és snapshotban is használható.

Javasolt forma:

```json
{
  "object_type": "card_instance",
  "object_id": "ci:match-001:P1:deck:0001",
  "card_instance_id": "ci:match-001:P1:deck:0001",
  "zone": "hand",
  "zone_sequence": 2,
  "controller_player_id": "P1",
  "visibility": "owner_only",
  "metadata": {
    "reference_scope": "legal_action_source",
    "lki_supported_later": true
  }
}
```

Az `id + zone_sequence` vagy `id + zone_change_counter` azért hasznos, mert később egy target vagy replay esemény nemcsak azt kérdezi, hogy létezik-e az objektum, hanem azt is, hogy ugyanabban a zónaállapotban létezik-e. Ha egy kártya kimegy a kézből, visszakerül, majd újra kézbe kerül, ugyanaz a `card_instance_id` lehet, de a `zone_sequence` már más. Ez segíthet LKI jellegű problémáknál, replay validációnál és stale target/action request elutasításnál.

## 9. Draw action jövőbeli átvezetése

Most:

- `deck_card_ids` Card_ID-kat tartalmaz;
- `hand` Card_ID-kat tartalmaz;
- a `draw_card` Card_ID-t vesz ki a deck listából és tesz át a hand listába;
- az event `card_id`, `from_zone`, `to_zone`, `event_sequence`, `state_version` mezőket tartalmaz;
- a `minimal_card_id_overlap_risk` guard védi a duplikált vagy nem egyértelmű Card_ID helyzeteket.

Jövő:

- a deck `card_instance_id` listát tartalmaz;
- a hand `card_instance_id` listát tartalmaz;
- az instance registryből jön a Card_ID lookup;
- a draw `ZoneOperation` előfeltétellel indul;
- a sikeres draw `ZoneMove` eventet ír;
- az event tartalmazza a `card_instance_id`, `card_id`, zónaindex, visibility, `event_sequence` és `state_version` mezőket;
- az overlap guard kiváltható instance invarianttal, mert ugyanaz a `card_instance_id` nem lehet egyszerre két zónában.

Javasolt átvezetési sorrend:

1. bevezetni az instance registryt a minimal state mellé;
2. deck setupkor létrehozni instance rekordokat;
3. a zónalistákat átvezetni instance ID-kra;
4. a debug snapshotban mindkét nézetet ideiglenesen jelölni;
5. a draw eventet `ZoneMove` formára bővíteni;
6. a Card_ID overlap guardot instance invarianttal leváltani.

## 10. Play_card előfeltételei

Play_card előtt szükséges:

- kézben lévő `card_instance_id`;
- `ObjectReference` a legal action source mezőjében;
- aktuális `zone_sequence` vagy `zone_change_counter`;
- player/priority ellenőrzés;
- cost/payment modell későbbi contractja;
- célzás előtti és utáni legality check;
- ZoneMove kézből boardra, stackre vagy más megfelelő zónába;
- rejected response, ha a request stale, az objektum nem a várt zónában van, vagy visibility/authority sérül.

Most még nem implementáljuk a play_cardot.

## 11. Targeting előfeltételei

Targeting előtt szükséges:

- stabil `ObjectReference`;
- object type megkülönböztetés: `card_instance`, `permanent`, `stack_object`, player, zone;
- visibility szabály;
- `id + zone_sequence` vagy `id + zone_change_counter` stale guard;
- target legality check a rules kernelben;
- player-visible snapshotban csak látható targetek;
- debug snapshotban teljesebb target lista, debug-only jelöléssel.

Most még nem implementáljuk a targetinget.

## 12. Godot UI mapping

Godot `CardView` node ne legyen authoritative state. A node csak engine projectiont renderel.

Renderelt mezők:

- `card_instance_id`;
- `card_id`;
- title/name a runtime package kártyaadatból;
- `zone`;
- `zone_index`;
- selected state;
- disabled state;
- hidden/revealed state;
- debug overlay, ha szükséges.

Godot drag/drop ne mozgasson engine state-et közvetlenül. A drag/drop action requestet épít. Az engine response után frissül a projection. Ha a response rejected, a UI visszaanimál vagy debugban jelzi a reject reason értéket.

Ez támogatja a későbbi Python, GDScript vagy hibrid runtime döntést is, mert a UI contractot használ, nem belső listákat.

## 13. AI-vs-AI / player-visible snapshot mapping

AI és bot ne Card_ID listából döntsön, ha már lesz instance model. A bot legal action listából választ.

Javasolt irány:

- a legal action source mezője instance referencia legyen;
- a bot `ObjectReference` alapú action requestet küld;
- player-visible observation ne tartalmazzon ellenfél hidden instance részleteket;
- hidden zone esetén csak count vagy ismeretlen objektum projection jelenjen meg;
- debug/evaluation futás használhat teljesebb snapshotot, de legyen `visibility_mode: "debug"` vagy hasonló jelzés;
- AI balance runner használhat teljes debug snapshotot, de ez külön mód legyen, ne player-facing default.

## 14. Invariantok

Javasolt új invariantok:

- egy `card_instance_id` egyszerre csak egy zónában lehet;
- egy zónán belül a `zone_index` rendezett és egyértelmű;
- minden `card_instance_id` létező `Card_ID`-ra mutat;
- `owner_player_id` mindig létező player;
- `controller_player_id` mindig létező player vagy `null`, ha az adott objektumnál nem releváns;
- private zone tartalma player-visible snapshotban ne szivárogjon;
- debug snapshot teljesebb lehet, de jelölje, hogy debug-only;
- `ZoneMove` után az instance `zone`, `zone_index`, `visibility` és `zone_sequence` frissül;
- event log `event_sequence` értékei monoton növekednek;
- accepted action után `state_version` növekszik;
- rejected action után zóna és `state_version` nem változik.

## 15. Event log hatás

A zónamozgás az event logban legyen elsőosztályú esemény, ne csak mellékes mező.

Későbbi event forma lehet:

- `event_type: "zone_move"`;
- source action információ;
- object reference;
- from/to zóna;
- visibility előtte és utána;
- `event_sequence`;
- `state_version`;
- debug és player-visible projection jelölések.

Ez segíti:

- replay és regressziós tesztelés;
- Godot projection frissítés;
- AI trajectory log;
- bugreport olvashatóság;
- későbbi client/server authority boundary kialakítása.

Most még nem implementálunk replay rendszert.

## 16. Migrációs lépések

Javasolt biztonságos sorrend:

1. Card instance record helper csak teszttel, state refactor nélkül.
2. Initial deck setup instance registry preview a minimal match state mellé.
3. Invariant helper, amely ellenőrzi az instance registry és zónalisták konzisztenciáját.
4. Draw action ZoneMove event contract bővítése úgy, hogy még visszafelé olvasható maradjon.
5. Deck/hand zónák átvezetése `card_instance_id` listákra.
6. Snapshot projection frissítése Card_ID lookup mezőkkel.
7. Player-visible snapshot hidden zone szabályok tesztje.
8. ObjectReference helper legal action source mezőkhöz.

Minden lépés legyen külön commit, zöld tesztekkel, új gameplay szabály nélkül, amíg az identity alap stabil nem lesz.

## 17. Mit ne implementáljunk még

Most még ne implementáljuk:

- teljes card instance refactort;
- play_cardot;
- attackot;
- targetinget;
- paymentet;
- stacket;
- permanent rendszert;
- ability executort;
- replacement/prevention rendszert;
- Godot CardView UI-t;
- multiplayer szervert;
- replay rendszert;
- teljes hidden information modellt.

## 18. Javasolt következő Codex-feladatok

### 1. Add minimal card instance record helper

Cél: legyen egy JSON-kompatibilis helper, amely Card_ID deck entryből instance rekordot készít.

Érint: új kis Python helper és unit teszt.

Nem érint: rules kernel, draw, Godot, runtime package output.

Miért biztonságos: még nem változtat state szerkezetet, csak contract-formát stabilizál.

### 2. Add minimal card instance deck setup for smoke state

Cél: a minimal match state létrehozásakor készüljön instance registry preview.

Érint: `create_initial_match_state` környéke és teszt.

Nem érint: play_card, targeting, Godot UI.

Miért biztonságos: a régi Card_ID zónák ideiglenesen maradhatnak, az instance registry csak párhuzamosan jelenik meg.

### 3. Add zone move event contract for draw

Cél: a `draw_card` response event tartalmazzon ZoneMove-kompatibilis mezőket.

Érint: draw event contract és tesztek.

Nem érint: új action type, play_card, attack, payment.

Miért biztonságos: a meglévő draw viselkedés megmarad, csak az event bizonyítóereje nő.

### 4. Migrate minimal draw to card_instance_id

Cél: a minimal draw már instance ID-t mozgasson deckből handbe.

Érint: `PlayerState` zónák, draw, invariantok, snapshotok.

Nem érint: play_card, targeting, Godot UI.

Miért biztonságos: csak a meglévő draw vertical slice átvezetése történik, új szabály nélkül.

### 5. Add player-visible zone visibility tests

Cél: player-visible snapshot ne szivárogtasson hidden zóna részleteket.

Érint: snapshot helper és tesztek.

Nem érint: teljes hidden information rendszer vagy multiplayer.

Miért biztonságos: contract szinten védi a későbbi UI/AI observation boundaryt.

### 6. Add minimal object reference helper

Cél: legyen stabil `ObjectReference` forma legal action source és future targeting mezőkhöz.

Érint: kis helper és unit teszt.

Nem érint: valódi targeting szabály, ability executor.

Miért biztonságos: csak hivatkozási contract, nem gameplay.

### 7. Add minimal board position contract

Cél: előkészíteni a későbbi board/permanent projectiont pozícióval és zónával.

Érint: dokumentált vagy tesztelt contract helper.

Nem érint: permanent rendszer, attack, targeting.

Miért biztonságos: még nem dönt szabályt, csak adatmodellt készít elő.

### 8. Add Godot projection mapping plan

Cél: külön terv arról, hogy Godot CardView hogyan kap `card_instance_id` projectiont.

Érint: docs-only vagy később debug loader smoke.

Nem érint: Godot UI implementáció vagy engine state authority.

Miért biztonságos: tisztázza a UI boundaryt kódátírás nélkül.
