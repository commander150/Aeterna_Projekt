# AETERNA – CROSS-PROJECT SYNTHESIS: SERIALIZATION, SAVE AND REPLAY

## DOKUMENTUMSTÁTUSZ

- **Verzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** első replay/state-history synthesis
- **Javasolt repository-útvonal:** `learning/synthesis/topics/serialization_save_replay.md`
- **Nem AETERNA-authority.**

---

# 1. Fő evidence

- boardgame.io: authoritative current state + deltalog + initial state + sync
- PokerKit: typed operation history + portable hand notation + state reconstruction
- MAGE: copy/restore-capable GameState
- AETERNA: current ordered internal events, state version, canonical determinism proof

---

# 2. P-REP-001 – State és history külön réteg

**Státusz:** `REPEATED_PATTERN`

```text
current state
≠
transition history
```

Boardgame.io ezt state + deltalog/storage formában mutatja.

PokerKit State + Operations/HandHistory formában.

---

# 3. P-REP-002 – Replay nem igényel strict event sourcingot

**Státusz:** `REPEATED_PATTERN`

Mindkét vizsgált rendszer mutál authoritative/domain state-et, miközben külön historyt is fenntart.

AETERNA számára:

> ne vezessünk be event-sourced aggregate-et csak azért, mert replayt akarunk.

---

# 4. P-REP-003 – Replaynek reprodukálható initial context kell

Candidate header:

```text
ReplayFormatVersion
EngineVersion
RulesVersion
CanonicalDataFingerprint
InitialSetupFingerprint
StartingPlayerId
Players / Deck fingerprints
RandomSeed / RNGVersion
```

A command log önmagában nem elég, ha a kezdeti context nincs rögzítve.

---

# 5. P-REP-004 – Accepted decision stream legyen stabil

A replay input ne nyers UI gesture legyen.

Tárolandó:

- normalized action/command type;
- actor;
- state version;
- canonical option/target choice;
- request correlation ahol szükséges.

Nem tárolandó authoritative inputként:

- drag coordinate;
- UI node path;
- animáció;
- tooltip state.

---

# 6. P-REP-005 – Canonical outcome/event history külön proof layer

Az accepted command újrajátszása mellett tárolható:

- canonical event sequence;
- random outcomes;
- resolution correlation;
- state hash/checkpoint.

Replay verification:

```text
command
→ recompute
→ compare expected canonical events / hash
```

Eltérés:
`REPLAY_DIVERGENCE`.

---

# 7. P-REP-006 – Snapshot checkpoint + log hibrid

Boardgame.io undo/sync és MAGE copy/restore alapján erős candidate:

```text
periodic canonical snapshot
+ event/command suffix
```

Előny:

- gyors seek;
- reconnect;
- debug reproduction;
- hosszú replay gyorsabb betöltése.

Nem szükséges minden transition teljes state snapshotja.

---

# 8. P-REP-007 – Viewer replay külön projection

Boardgame.io playerView + log redaction alapján:

```text
internal replay
≠
player replay
≠
spectator replay
```

A full authoritative replay hidden data lehet.

A player-export csak a számára jogos időbeli információt adhatja.

---

# 9. P-REP-008 – Save és replay külön contract

## Replay

Cél:
- történet visszajátszása;
- verification;
- bug reproduction;
- AI dataset.

## Save

Cél:
- futó match pontos folytatása.

Save-hoz minden pending state kell:

- phase;
- priority;
- reaction window;
- resolution stack;
- pending target/choice/payment;
- random continuation state;
- trigger state;
- modifier durations.

Ez szigorúbb, mint egy viewer replay.

---

# 10. Schema/version migration

Hosszú távon külön szükséges:

```text
ReplayFormatVersion
SaveFormatVersion
CanonicalDataVersion/Fingerprint
EngineContractVersion
```

A replay kompatibilitás lehet:
- strict same-version;
- migrált;
- best-effort historical runner.

Ezt később kell eldönteni.

---

# 11. Projection-risk tanulság

Boardgame.io jelen vizsgált sync filtere a current state-et és logot filterezi, de az `initialState` mezőre nem látszik ugyanaz a playerView alkalmazás.

AETERNA invariáns:

> minden persisted/baseline/history state viewer projection-köteles, ha klienshez kerül.

---

# 12. Anti-patternök

| ID | Név |
|---|---|
| `A-REP-001` | UI gesture replay inputként |
| `A-REP-002` | replay initial data fingerprint nélkül |
| `A-REP-003` | hidden authoritative replay publicként elküldve |
| `A-REP-004` | save nem serializál pending state-et |
| `A-REP-005` | replay log és debug log fogalmának összemosása |
| `A-REP-006` | engine upgrade után silent replay reinterpretation |
| `A-REP-007` | random output/state nincs replay contractban |
| `A-REP-008` | event sourcing bevezetése szükséglet nélkül |

---

# 13. AETERNA Replay Blueprint – későbbi candidate

```text
ReplayFile
├── Header
├── InitialCanonicalSetup
├── DecisionStream
├── CanonicalOutcomeStream
├── OptionalCheckpoints
└── FinalVerification
```

A konkrét fájlformátum még nem döntendő.

---

# 14. Verdict

A replay architecture fő határai már előretervezhetők.

A tényleges implementationt azonban csak:
- Reaction/Priority;
- combat;
- pending choice model;
- RNG policy

stabilizálása után érdemes elkezdeni, mert a save/replay schema ezeket mind serializálni fogja.
