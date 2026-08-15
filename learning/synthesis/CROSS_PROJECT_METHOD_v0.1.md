# AETERNA – CROSS-PROJECT SYNTHESIS METHOD

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első használható módszertani alap
- **Szerep:** a projektenkénti learning auditok fölé épülő, elkülönített összehasonlító szint
- **Javasolt repository-útvonal:** `learning/synthesis/CROSS_PROJECT_METHOD_v0.1.md`
- **Kiinduló AETERNA repository HEAD:** `b7c5a51a921d11779e50a127171b49166dd80b96`
- **Nem AETERNA-szabályforrás.**
- **Nem production engine-specifikáció.**
- **Nem engedély külső kód átvételére.**

## 1. Cél

A cross-project synthesis célja, hogy a már elkészült, egymástól szándékosan izolált learning auditokból olyan közös technikai mintákat, alternatívákat, ellenpéldákat és bizonyítékhiányokat tárjon fel, amelyek segítik az AETERNA hosszú távú fejlesztési tervének kialakítását.

```text
külső projekt
    ↓
projektenkénti izolált audit
    ↓
cross-project synthesis
    ↓
közös minták / alternatívák / ellenpéldák
    ↓
AETERNA candidate
    ↓
AETERNA blueprint / contract döntés
    ↓
production implementáció
    ↓
verification
```

## 2. A projektenkénti audit és a synthesis szétválasztása

### 2.1 Projektenkénti audit

Az egyedi audit továbbra is:
- kizárólag az adott külső projektet vizsgálja;
- az AETERNA aktuális állapotához viszonyít;
- nem hivatkozik más learning projektre értékelési alapként;
- bizonyítékot, commitot, fájlútvonalat és reprodukálhatóságot rögzít;
- nem készít projekt-rangsort.

### 2.2 Cross-project synthesis

A synthesis külön dokumentumréteg, amely:
- több már auditált projekt eredményeit hasonlítja össze;
- problématerületenként szerveződik, nem repositorynként;
- felismeri a közös mintákat;
- elkülöníti a valóban független bizonyítékot a fork/port/lineage ismétlődéstől;
- rögzíti az alternatív megoldásokat és trade-offokat;
- azonosítja a bizonyítékhiányokat;
- AETERNA-candidate javaslatot készíthet;
- de önmagában nem változtat AETERNA-authorityt.

## 3. Kötelező authority-határ

```text
AETERNA hivatalos szabályforrás
    >
elfogadott AETERNA technikai döntés / contract
    >
production engine igazolt viselkedése
    >
AETERNA blueprint candidate
    >
cross-project synthesis
    >
egyedi learning audit
    >
külső projekt implementációja
```

Külső projekt gyakorlata nem írhat felül hivatalos AETERNA-szabályt.

## 4. Evidence strength

| Jel | Név | Jelentés |
|---|---|---|
| `P` | Primary | a projekt auditjának központi, bizonyított tanulási területe |
| `S` | Secondary | releváns és dokumentált, de nem a projekt fő bizonyítéka |
| `O` | Observed | megfigyelt, de még nem elég mély a synthesis-döntéshez |
| `—` | Not evidenced | a jelenlegi audit alapján nincs használható bizonyíték |

A `P` nem jelent „jó megoldást”. Kritikus negatív példa is lehet `P`.

## 5. Lineage és függetlenség

Minden projekthez `evidence_family` mezőt rendelünk. Forkok, portok és ugyanazon frameworkre épülő projektek nem számítanak automatikusan független bizonyítéknak.

Nem használható:

```text
5 projekt ezt csinálja → ezért ezt választjuk
```

Helyette:
- milyen problémát old meg;
- milyen invariánst őriz;
- milyen hibamódokat okoz;
- milyen költsége van;
- illeszkedik-e AETERNA szabályaihoz és architecture követelményeihez.

## 6. Pattern lifecycle

```text
OBSERVED
    ↓
REPEATED_PATTERN
    ↓
AETERNA_CANDIDATE
    ↓
PROPOSED
    ↓
ADOPTED
    ↓
IMPLEMENTED
    ↓
VERIFIED
```

Mellékstátuszok:
`DEFERRED`, `REJECTED`, `SUPERSEDED`, `INSUFFICIENT_EVIDENCE`, `RULE_CONFLICT`, `LICENSE_BLOCKED`.

## 7. Synthesis értékelési tengelyek

1. rules compatibility;
2. authoritative state;
3. atomic transition;
4. validation;
5. state-version/stale safety;
6. determinism;
7. hidden information;
8. viewer projection;
9. replay/audit;
10. testability;
11. rollback/failure mode;
12. extensibility;
13. performance;
14. diagnostics;
15. C#/.NET fit;
16. Godot boundary;
17. AI/headless;
18. multiplayer;
19. schema/versioning;
20. license/provenance;
21. complexity;
22. maintainability.

## 8. Első témakatalógus

- repository/module structure
- authoritative state/domain model
- action/request/legal actions
- validation/preflight
- atomic transition
- turn/phase/state machine
- pending decision
- reaction/priority/stack/chain
- trigger/resolution
- target/choice
- prevention/replacement
- ability/effect architecture
- modifier/continuous effect
- object identity/zone lifecycle
- resources/payment
- combat
- events/projection
- hidden information
- determinism/RNG
- serialization/save/replay
- multiplayer/session/reconnect
- AI/headless simulation
- data/content/runtime package
- Godot/client/UI
- testing/scenario/fixture
- diagnostics/profiling
- CI/build/release
- extensibility/modding
- backward compatibility

## 9. Javasolt repository-szerkezet

```text
learning/
└── synthesis/
    ├── CROSS_PROJECT_METHOD_vX.Y.md
    ├── PROJECT_CAPABILITY_MATRIX_vX.Y.md
    ├── PATTERN_CATALOG_vX.Y.md
    └── topics/
```

A későbbi AETERNA-döntési réteg külön marad:

```text
Aeterna game engine/docs/blueprints/
```

## 10. Új learning source lokális útvonala

```text
learning/sources/<owner>__<repository>/
```

Minden új projekthez dokumentálandó:
- local path;
- upstream URL;
- default branch;
- vizsgált branch/tag;
- commit SHA;
- ellenőrzés dátuma;
- licenc;
- evidence family;
- analysis dokumentum.

A korábban letöltött mappákat nem kell tömegesen átnevezni.

## 11. Új projekt felvételének kapuja

Új projektet akkor érdemes hozzáadni, ha:
1. capability gapet fed;
2. más architecture familyből ad független bizonyítékot;
3. a következő AETERNA subsystemhez P0/P1 relevanciájú;
4. erős ellenpéldával próbára tesz egy candidate-et;
5. production-scale mintát ad;
6. speciális területet fed.

## 12. Blueprint promotion gate

Synthesis eredmény csak akkor kerülhet AETERNA blueprintbe, ha:
- a bizonyíték visszavezethető;
- lineage-hatást figyelembe vettük;
- nincs rules conflict;
- összevetettük a production architecture-rel;
- alternatívák és trade-offok dokumentáltak;
- legalább `AETERNA_CANDIDATE`;
- emberi döntés elfogadta.

## 13. Első munkahullám

### Wave A – Rules Engine Core Architecture
authoritative state → domain model → action/request → legal actions → validation → atomic transition → eventmodell → turn/phase → pending → reaction/priority → trigger/resolution → ability/effect → identity/zones → determinism → testing/scenario.

### Wave B – Multiplayer
### Wave C – AI / simulation
### Wave D – Data / content / tooling
### Wave E – Godot / client / UI

## 14. Változásnapló

### 0.1 – 2026-08-15
- létrejött a külön synthesis-réteg;
- megmaradt az egyedi audit izolációs szabálya;
- bevezetésre került az evidence-strength és evidence-family modell;
- létrejött a pattern lifecycle és blueprint promotion gate;
- rögzítésre került az új source-path konvenció;
- kijelölésre került az első rules-engine hullám.
