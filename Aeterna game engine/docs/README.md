# AETERNA Game Engine – Dokumentációs index és működési szabály

## 1. Operatív dokumentumok

### Aktuális állapot

```text
../../Aeterna dokumentációk/AETERNA_AKTUALIS_PROJEKTALLAPOT.md
```

Ez az egyetlen aktív dokumentum, amely aktuális repository-bázist, elkészült scope-ot,
következő feladatot és blokkolókat tartalmazhat.

### Mérföldkőnapló

```text
checkpoints/CHECKPOINTS.md
```

Append-only történeti összefoglaló. Nem tasklista.

### Projekt- és fájltérkép

```text
../../Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ.md
```

Csak mappa- és fájlszerepeket tartalmaz. Nem roadmap.

---

## 2. Tartós architektúra és döntések

- `ARCHITECTURE.md`
- `TECHNOLOGY_DECISIONS.md`
- `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`
- `AETERNA_0.0.1_MERFOLDKO_ES_CELALLAPOT_v1.0.md`

Ezek csak valódi architektúra-, technológia- vagy termékcél-változáskor frissülnek.

---

## 3. Contract- és runtime package specifikáció

- `CONTRACT_SPECIFICATION.md`
- `CONTRACT_SPECIFICATION_MIGRATION_MAP.md`
- `RUNTIME_PACKAGE_SPECIFICATION.md`
- `ABILITY_MODULE_SYSTEM.md`
- `RUNTIME_COMPARISON_FIXTURE_SPEC.md`

A specifikáció nem státusznapló. Egy implementáció elkészülése önmagában nem indokolja
a specifikáció átírását, ha a contract nem változott.

---

## 4. Kérdés–válasz rendszer

- `OPEN_QUESTIONS.md`
- `OPEN_QUESTIONS_DECISIONS.md`

Csak új kérdés, státuszváltozás vagy elfogadott döntés esetén módosul.

---

## 5. Felváltott operatív dokumentumok

A következő fájlok régi hivatkozások megtartása miatt maradnak meg, de nem aktív
authority-k:

- `PROTOTYPE_STATUS.md`
- `CONTRACT_STATUS.md`
- `RUNTIME_PACKAGE_STATUS.md`
- `DECISION_MAP.md`
- `checkpoints/ENGINE_CHECKPOINT.md`
- `../../Aeterna dokumentációk/AKTUALIS_PROJEKTTERV_ES_PRIORITASOK_v6.4.md`
- `../../Aeterna dokumentációk/PROJEKT_TERKEP_ES_FAJLSTATUSZ v1.7.md`

Aktuális állapotért mindig az
`AETERNA_AKTUALIS_PROJEKTALLAPOT.md` fájlt kell megnyitni.

---

## 6. Frissítési kapu

Elfogadott mérföldkőnél normál esetben:

1. az aktuális projektállapot frissül;
2. a checkpointnapló végére új bejegyzés kerül.

Más dokumentum csak akkor módosul, ha a saját tartós szerepe változott.

Nem kell dokumentációt frissíteni:

- minden köztes commitnál;
- kizárólag belső refactornál;
- whitespace vagy formázási javításnál;
- learning elemzés hozzáadásakor, ha a production állapot nem változott.

---

## 7. Authority-szabály

Dokumentációs ellentmondás esetén:

1. hivatalos szabályforrás;
2. aktuális projektállapot;
3. aktív architektúra és contractspecifikáció;
4. production code és bizonyított teszt;
5. történeti dokumentum.

A történeti fájl régi „következő lépése” nem lehet aktív utasítás.
