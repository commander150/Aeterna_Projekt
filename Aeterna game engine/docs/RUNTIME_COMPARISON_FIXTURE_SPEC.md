# AETERNA Game Engine – Nyelvfüggetlen runtime comparison fixture specifikáció

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.0  
**Dátum:** 2026-07-15  
**Státusz:** aktív, implementáció előtti comparison fixture-specifikáció  
**Kapcsolódó prioritás:** runtime engine language decision gate / P2 közös fixture

Ez a dokumentum meghatározza azt a közös, minimális és nyelvfüggetlen scenario-t, amelyet ugyanazzal a jelentéssel kell végrehajtani:

- a jelenlegi Python referenciaengine-ben;
- a Python sidecar + Godot proofban;
- a Godot .NET/C# rules-runtime proofban;
- szükség esetén egy szűk GDScript vagy más runtime proofban.

A dokumentum nem írja elő, hogy a belső osztályok, fájlok vagy nyelvi konstrukciók azonosak legyenek.

Kötelezően azonosnak vagy explicit módon kompatibilisnek kell lennie:

- az input jelentésének;
- az action requesteknek;
- az elfogadási és elutasítási eredményeknek;
- a state version alakulásának;
- a typed eventeknek;
- a player-visible snapshot jelentésének;
- a rejtett információ kezelésének;
- a determinisztikus kimenetnek.

---

## 1. A fixture célja

A fixture nem teljes játékmotor-port.

Azt kell bizonyítania, hogy a jelölt runtime képes:

1. determinisztikus MatchState létrehozására;
2. action request fogadására;
3. expected state version ellenőrzésére;
4. elfogadott transition végrehajtására;
5. elutasított action esetén változatlan state megtartására;
6. typed event előállítására;
7. player-visible snapshot készítésére;
8. rejtett információ redakciójára;
9. JSON-kompatibilis serializationre;
10. ugyanazon inputból ismételten azonos eredmény előállítására.

A fixture eredménye a runtime-nyelvi döntés egyik bizonyítéka. Önmagában nem választ győztest, mert a packaging, stabilitás, karbantarthatóság és Godot-integráció külön is mérendő.

---

## 2. Kapcsolódó aktív contractok

A fixture a jelenlegi Python referenciaengine következő működő alapjaira épül:

- `minimal-card-instance-record-v1`;
- MatchState és PlayerState;
- minimal action request;
- expected state version guard;
- rejected action response;
- `minimal-engine-event-v0`;
- `zone_move` event;
- `turn_transition` event;
- `engine-player-visible-snapshot-v2`;
- minimal public Domain board;
- `minimal-ai-vs-ai-episode-v1` determinisztikus JSON-tanulságai.

A comparison fixture nem követeli meg:

- Wellspring production integrációt;
- Beáramlást;
- Magnitúdót vagy Aura-paymentet;
- `play_card` actiont;
- combatot;
- ability executort;
- Pecsét- vagy győzelmi rendszert.

---

## 3. Fixture envelope

Javasolt felső szintű contract:

- `schema_version`: `aeterna-runtime-comparison-fixture-v1`;
- `fixture_id`: stabil azonosító;
- `description`;
- `reference_engine`;
- `runtime_package_ref`;
- `seed`;
- `initial_state_ref`;
- `step_plan`;
- `expected_artifacts`;
- `canonicalization_profile`;
- `comparison_profile`;
- `metadata`.

### Kötelező elv

A végleges `initial_state.json` és expected outputok ne kézzel kitalált, a Python implementációtól eltérő fixture-ök legyenek.

A Codex első implementációs lépésében:

1. a jelenlegi Python reference engine canonical builderével létre kell hozni a minimal állapotot;
2. az outputot validálni kell;
3. az állapotot és az expected artifactokat verziózott comparison fixture-ként rögzíteni kell;
4. a C# és más proof ezt a rögzített jelentést implementálja;
5. eltérés esetén nem szabad automatikusan a Python byteszerkezetét helyesnek tekinteni, ha a contract jelentése hibás vagy nyelvspecifikus;
6. contracteltérésnél külön emberi döntés szükséges.

---

## 4. Minimal initial state

### 4.1 Meccs

Kötelező:

- stabil `match_id`;
- két játékos: `player_1`, `player_2`;
- `state_version = 0`;
- active player: `player_1`;
- priority player: `player_1`;
- minimal jelenlegi phase;
- üres event log;
- determinisztikus event sequence kezdőérték;
- mindkét játékoshoz üres Domain occupancy;
- canonical hat Áramlatos Domain topológia.

### 4.2 Kártyapéldányok

Mindkét játékoshoz szükséges:

- legalább két lap a deckben;
- legalább egy lap a handben;
- üres discard;
- stabil, emberileg olvasható card instance ID-k;
- stabil card ID-k;
- helyes owner/controller;
- helyes zone és zone index;
- deck/hand/discard esetén `activity_state = null` vagy a canonical nyelvi megfelelő;
- canonical visibility;
- determinisztikus created és zone sequence.

### 4.3 Hidden information

Az initial state belső debugfixture lehet teljes.

A player-visible outputban azonban:

- saját kéz azonosítható;
- ellenfél kéz redacted és count-only;
- deck csak count;
- deck instance ID-k nem szivároghatnak;
- ellenfél kéz card ID és instance ID nem szivároghat;
- Domain board public és üres;
- debug-only metadata nem kerülhet player-facing outputba.

---

## 5. Kötelező step plan

### Step 0 – Initial state validation

Input:

- a canonical initial state.

Elvárt:

- state valid;
- `state_version = 0`;
- event log üres;
- legal action listában `player_1` számára a jelenlegi szabályok szerint elérhető actionök jelennek meg;
- nincs state mutation.

### Step 1 – `draw_card` player_1

Request:

- `match_id`: fixture match;
- `player_id`: `player_1`;
- `action_type`: `draw_card`;
- `expected_state_version = 0`;
- üres vagy canonical payload.

Elvárt:

- accepted response;
- pontosan egy kártya deckből handbe kerül;
- deck és hand listák frissülnek;
- registry zone és zone index konzisztens;
- `state_version = 1`;
- pontosan egy új `zone_move` event;
- event sequence determinisztikus;
- input request nem módosul.

### Step 2 – Stale request rejection

Request:

- `player_id`: `player_1`;
- `action_type`: `end_turn`;
- szándékosan stale `expected_state_version = 0`.

Elvárt:

- rejected response;
- strukturált stale-version reason/diagnostics;
- `state_version` továbbra is `1`;
- active és priority player változatlan;
- event log változatlan;
- MatchState szemantikailag változatlan;
- nincs részleges mutation;
- nincs új gameplay event.

### Step 3 – `end_turn` player_1

Request:

- `player_id`: `player_1`;
- `action_type`: `end_turn`;
- `expected_state_version = 1`.

Elvárt:

- accepted response;
- active player `player_2`;
- priority player a current minimal szabály szerint `player_2`;
- `state_version = 2`;
- pontosan egy új `turn_transition` event;
- az előző `zone_move` event változatlan marad.

### Step 4 – `draw_card` player_2

Request:

- `player_id`: `player_2`;
- `action_type`: `draw_card`;
- `expected_state_version = 2`.

Elvárt:

- accepted response;
- pontosan egy player_2 decklap handbe kerül;
- `state_version = 3`;
- új `zone_move` event;
- event sequence folytonos és determinisztikus.

### Step 5 – Player-visible snapshot player_1

Elvárt:

- `engine-player-visible-snapshot-v2` jelentésével kompatibilis output;
- player_1 saját handje látható;
- player_2 handje redacted;
- mindkét deck count-only;
- discard public;
- Domain board public;
- nincs internal registry dump;
- nincs deck instance ID-szivárgás;
- snapshot készítése nem mutál state-et.

### Step 6 – Player-visible snapshot player_2

Elvárt:

- ugyanaz a visibility-policy player_2 nézőpontjából;
- player_2 saját handje látható;
- player_1 handje redacted;
- snapshot készítése nem mutál state-et.

### Step 7 – Legal actions ellenőrzése

Kötelező legal-action snapshot legalább:

- Step 0 előtt;
- Step 1 után;
- Step 3 után;
- Step 4 után.

Elvárt:

- csak az aktuális játékos és state alapján engedélyezett actionök;
- stabil action ordering;
- legal action generation nem mutál state-et;
- player-facing legal action nem szivárogtat rejtett adatot.

### Step 8 – Teljes artifact export

Exportálandó:

- final debug state;
- request sequence;
- response sequence;
- legal action sequence;
- event log;
- player_1 snapshot;
- player_2 snapshot;
- diagnostics;
- run report.

### Step 9 – Ismételt futás

A teljes fixture-t új, tiszta processben vagy új, tiszta runtime instance-ban másodszor is le kell futtatni.

Elvárt:

- azonos semantic output;
- canonical serialization után byte-azonos kötelező artifactok;
- nincs előző futásból megmaradt state, port, tempfájl vagy processzfüggés.

---

## 6. Kötelező artifactkészlet

Javasolt mappaszerkezet:

- `fixture.json`;
- `initial_state.json`;
- `requests.jsonl`;
- `responses.jsonl`;
- `legal_actions.jsonl`;
- `events.jsonl`;
- `snapshot_player_1.json`;
- `snapshot_player_2.json`;
- `final_debug_state.json`;
- `diagnostics.json`;
- `run_manifest.json`;
- `comparison_report.md`;
- `comparison_report.json`.

### Run manifest minimális mezők

- runtime candidate;
- implementation language;
- Godot version, ha releváns;
- Python/.NET/egyéb runtime-verzió;
- operating system;
- architecture;
- fixture schema;
- contract/schema mapping;
- build identifier;
- start/end result;
- artifact hashes;
- known deviations.

---

## 7. Canonical serialization profile

### 7.1 Általános

- UTF-8;
- LF line ending;
- JSON vagy JSONL;
- egész szám ne legyen lebegőpontos formára alakítva;
- boolean valódi boolean;
- nincs nyelvspecifikus object repr;
- nincs memória-cím;
- nincs process ID a kötelező byte-összehasonlítási artifactban;
- nincs aktuális időbélyeg a canonical gameplay outputban;
- nincs véletlen UUID;
- stabil property naming;
- stabil enumértékek;
- nincs NaN vagy Infinity.

### 7.2 Objektumkulcsok

A canonical összehasonlítás előtt:

- objektumkulcsok lexikografikusan rendezhetők;
- vagy a fixture külön canonical property orderinget írhat elő;
- a két módszer közül egyet kötelezően és egységesen kell használni.

Első proofhoz ajánlott:

- lexikografikusan rendezett JSON object key;
- szemantikailag rendezett listák változatlan sorrenddel.

### 7.3 Listák

Nem rendezhető automatikusan minden lista.

Sorrendjelentős:

- deck;
- hand;
- discard;
- event log;
- request/response sequence;
- legal action ordering;
- Domain position ordering;
- trajectory steps.

Csak explicit contract alapján rendezhető:

- hibakódlista;
- diagnostics, ha a contract sorrendfüggetlennek jelöli;
- metadata entryk.

### 7.4 Hiányzó érték és `null`

A proof előtt mezőnként rögzíteni kell:

- kötelező mező;
- opcionálisan elhagyható mező;
- explicit `null` mező.

A C# default value, Python `None` és GDScript `null` nem okozhat önkényes schemaeltérést.

---

## 8. Összehasonlítási szintek

### 8.1 Szemantikai egyezés – kötelező

Kötelezően egyezzen:

- accepted/rejected sorrend;
- reason category;
- state version;
- active/priority player;
- zónatagság;
- event type és sequence;
- snapshot visibility;
- legal action jelentés;
- hidden-information tiltások;
- final state jelentése.

### 8.2 Canonical JSON-egyezés – kötelező a kiválasztott artifactokra

Kötelező byte-összehasonlítási jelöltek:

- requests;
- responses;
- events;
- player snapshots;
- final debug state;
- legal actions, ha a contract ordering lezárt.

### 8.3 Implementációspecifikus eltérés – megengedhető

Megengedhető különbség:

- stack trace;
- belső class/type név;
- build path;
- process ID;
- runtime startup log;
- memory profiling output;
- platformfüggő diagnosztikai kiegészítés.

Ezek nem kerülhetnek a canonical gameplay artifactokba.

---

## 9. Jelöltenkénti adapterelv

### 9.1 Python reference

- a jelenlegi canonical buildereket és validatorokat használja;
- ez állítja elő az első expected fixture-t;
- a reference output sem mentes az audittól;
- nyelvspecifikus belső rész nem válhat indoklás nélkül kötelező cross-language contracttá.

### 9.2 Python sidecar + Godot

A fixture fusson:

- közvetlen Python headless módban;
- majd Godotból a bridge-en keresztül.

A két Python eredménynek is egyeznie kell. Ezzel különválasztható:

- engine-hiba;
- bridge-hiba;
- Godot parser/projection hiba.

### 9.3 Godot .NET/C#

- a rules library Godot UI nélkül is fusson;
- a fixture unit/integration tesztből közvetlenül futtatható legyen;
- külön Godot wrapperrel is fusson;
- a két C# út outputja egyezzen;
- a Godot UI ne tartalmazzon extra rules logikát.

### 9.4 GDScript vagy más proof

- csak a rögzített minimal scope;
- nem teljes engine-port;
- az eltérő nyelvi forma ellenére azonos contractjelentés;
- külön jelölni kell, ha valamely kötelező teszt technológiai okból nem futtatható headless módon.

---

## 10. Rejection és immutability ellenőrzés

A stale request előtt és után kötelező:

- canonical debug state hash;
- event log hash;
- player zone-listák;
- registry;
- active/priority player;
- state version.

Elvárt:

- minden state-hash azonos;
- csak a külön response/diagnostics artifact bővülhet;
- a rejected action nem kap gameplay eventet;
- az input request és fixture változatlan marad.

A runtime jelölt elutasítandó vagy javítandó, ha a rejection részleges mutationt hagy maga után.

---

## 11. Hidden-information kötelező negatív tesztek

Mindkét player snapshotban keresendő tiltott adat:

- ellenfél hand card ID;
- ellenfél hand card instance ID;
- deck card instance ID;
- teljes internal registry;
- debug metadata;
- másik játékosnak nem ismert object reference;
- teljes debug event payload, ha player-facing szűrés szükséges.

A comparison runner külön tiltott mező- és értékkeresést végezzen, ne csak a top-level schema validációjára támaszkodjon.

Hidden-information szivárgás blocking failure.

---

## 12. Teljesítmény és packaging kapcsolata

Ez a fixture elsősorban correctness-proof.

Külön mérendő ugyanennek a fixture-nek:

- első runtime-indítási idő;
- első requestig eltelt idő;
- action round-trip idő;
- snapshot serialization idő;
- process memória;
- package méret;
- szükséges prerequisite-ek;
- 20 indítás/leállítás eredménye;
- elárvult processz;
- offline futás.

Ezek a `PRODUCT_RUNTIME_AND_INSTALLATION_REQUIREMENTS.md` alapján értékelendők.

---

## 13. Elfogadási feltételek

Egy runtime proof fixture-szinten sikeres, ha:

- az initial state valid;
- minden elfogadott action helyes transitiont ad;
- a stale request strukturáltan elutasított;
- rejectionkor nincs mutation;
- state version pontosan a meghatározott módon változik;
- event type, sequence és payload jelentése kompatibilis;
- a két player snapshot visibility-policyja helyes;
- nincs hidden-information leak;
- legal action generation determinisztikus és non-mutating;
- a második futás canonical artifactjai azonosak;
- a runtime UI nélkül is futtatható legalább tesztmódban;
- a build- és futási környezet dokumentált;
- minden eltérés strukturált reportba kerül.

Nem sikeres, ha:

- valamely jelölt csak kézi UI-kattintással futtatható;
- a state mutation és UI összekeveredik;
- rejection után state változik;
- azonos inputból eltérő event vagy snapshot jön létre indok nélkül;
- rejtett információ szivárog;
- a contract mapping csak kézi, nem ellenőrizhető átalakítással működik;
- a runtime környezet nem reprodukálható.

---

## 14. Első Codex-implementációs bontás

### Szakasz A – Read-only referenciaaudit

- azonosítsa a jelenlegi Python builder-, validator-, action-, snapshot- és event-entrypointokat;
- ne módosítson kódot;
- készítsen pontos fájlscope-ot;
- jelezze a fixture-spec és a jelenlegi implementáció esetleges eltéréseit.

### Szakasz B – Python fixture exporter

- canonical initial state;
- request sequence;
- expected artifactok;
- validator;
- második futás determinisztika;
- célzott tesztek;
- külön commit.

### Szakasz C – Nyelvfüggetlen comparator

- canonical JSON;
- semantic comparison;
- forbidden hidden field scan;
- structured diff report;
- runtime-candidate metadata;
- külön commit.

### Szakasz D – Python sidecar proof

- ugyanaz a fixture bridge-en keresztül;
- direct Python vs sidecar-Godot comparison;
- lifecycle és packaging mérés.

### Szakasz E – C# proof

- minimal rules library;
- ugyanaz a fixture;
- direct C# test és Godot .NET wrapper;
- Python reference comparison;
- packaging mérés.

### Szakasz F – Feltételes proof

- minimal GDScript vagy más jelölt csak emberi döntés után.

---

## 15. Nem célok

Ez a fixture nem:

- teljes Python → C# migráció;
- teljes GDScript engine;
- teljes játékmenet;
- teljes runtime package schema-migráció;
- teljes Godot UI;
- teljes AI;
- balanszteszt;
- teljes replay runner;
- teljes save rendszer.

Feladata egyetlen kérdés megbízható megválaszolásának előkészítése:

> Képes-e a runtime-jelölt ugyanazt a minimális AETERNA szabályi állapotát és contractfolyamát helyesen, determinisztikusan, tesztelhetően és később portable Windows-termékként használható módon kezelni?
