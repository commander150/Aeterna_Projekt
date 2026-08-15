# AETERNA – CROSS-PROJECT SYNTHESIS: DETERMINISM AND RANDOM

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első determinism/RNG synthesis
- **Javasolt repository-útvonal:** `learning/synthesis/topics/determinism_and_random.md`
- **Nem AETERNA-authority.**

---

# 1. Fő evidence

Elsődleges:

- `learning/analyses/boardgameio__boardgame.io.md`
- `learning/analyses/uoftcprg__pokerkit.md`

Korábbi támogató auditok:

- db0 framework – seedelt RNG jel;
- AETERNA saját production determinism proof – 100/100 current milestone.

---

# 2. P-DET-001 – RNG continuation state first-class

**Evidence:** boardgame.io  
**Státusz:** `AETERNA_CANDIDATE`

A seed önmagában nem feltétlen elég egy már megkezdett random stream folytatásához.

Erős candidate:

```text
RandomState
- seed
- generator continuation state / counter
```

---

# 3. P-DET-002 – Random state ne legyen viewer-visible

**Evidence:** boardgame.io  
**Státusz:** `AETERNA_CANDIDATE`

A player view nem kapja meg a random plugin belső state-jét.

A random state stratégiai információvá válhat, ha a következő érték előrejelezhető.

---

# 4. P-DET-003 – Random-dependent client prediction kerülendő

**Evidence:** boardgame.io  
**Státusz:** `AETERNA_CANDIDATE`

Randomot használó transition ne legyen authoritative client-side optimistic mutation.

AETERNA online modellben random outcome az authoritative engineből jöjjön.

---

# 5. P-DET-004 – Random outcome materializálható historyban

**Evidence:** PokerKit  
**Státusz:** `AETERNA_CANDIDATE`

PokerKit HandHistory konkrét dealt cardokat tud tárolni.

Ez azt mutatja, hogy replayben a random outcome:

- újraszámolható seedből;
- vagy explicit canonical outcome-ként tárolható.

---

# 6. Két replay-stratégia trade-off

## Seed replay

```text
seed + commands → same random stream
```

Előny:
- tömör;
- teljes determinism proof.

Kockázat:
- RNG algoritmus/migráció megváltozhat;
- call-count változás replay divergence-et okoz.

## Outcome replay

```text
commands + stored random outcomes
```

Előny:
- robusztusabb engine-verzió változás ellen;
- auditálható.

Kockázat:
- nagyobb log;
- az outcome validitását is ellenőrizni kell.

## AETERNA candidate: dual-proof

```text
seed/PRNG state
+
canonical random outcome events
```

Replay verification mindkettőt ellenőrizheti.

---

# 7. P-DET-005 – Determinism contract versioned legyen

Replayhez rögzítendő:

- engine version;
- rules version;
- data fingerprint;
- RNG algorithm/version;
- seed;
- initial setup fingerprint.

Különben egy régi replayről nem tudható, milyen semantics szerint kell futtatni.

---

# 8. Anti-patternök

| ID | Név |
|---|---|
| `A-DET-001` | process-global RNG authoritative state-ben |
| `A-DET-002` | seed nincs perzisztálva |
| `A-DET-003` | RNG continuation/call position elveszik |
| `A-DET-004` | client megkapja future-predictive RNG state-et |
| `A-DET-005` | random outcome nincs auditálható eventtel korrelálva |
| `A-DET-006` | replay engine/data version nélkül |
| `A-DET-007` | implicit container iteration határozza meg random call ordert |

---

# 9. AETERNA következő design kérdés

A jelen production 100/100 determinism proof már jó milestone proof.

A hosszú távú blueprinthez még döntendő:

- RNG szükséges-e az alapjáték runtime-ban és mely mechanikák használhatják;
- milyen generator;
- hogyan serializáljuk state-jét;
- random event payload mennyit árul el;
- replay compatibility milyen verzióhatárt vállal.

---

# 10. Verdict

A determinism témában már van elég evidence ahhoz, hogy az AETERNA későbbi RNG/replay rendszerének fő invariánsait előre rögzítsük, de konkrét RNG implementation választás még nem indokolt.
