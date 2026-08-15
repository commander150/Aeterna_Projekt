# AETERNA – DEVELOPMENT BLUEPRINT PROGRAM INDEX

## VERZIÓ / DOKUMENTUMSTÁTUSZ
- **Verzió:** 0.8
- **Dátum:** 2026-08-15
- **Státusz:** PRE-OQ ARCHITECTURE COVERAGE COMPLETE
- **Javasolt repository-útvonal:** `Aeterna game engine/docs/blueprints/BLUEPRINT_PROGRAM_INDEX_v0.8.md`

# 1. Hullámok

| Hullám | Terület | Státusz |
|---|---|---|
| 0 | method + inventory | COMPLETE FOUNDATION |
| A1 | authority/state | COMPLETE FIRST SYNTHESIS |
| A2 | reaction/trigger/resolution | SYNTHESIS + BLUEPRINT v0.2 |
| A3 | determinism/random | COMPLETE FIRST SYNTHESIS |
| A4 | serialization/save/replay | COMPLETE FIRST SYNTHESIS |
| A5 | action/validation/event | SYNTHESIS + BLUEPRINT v0.1 |
| A6 | ability/effect/continuous | SYNTHESIS + BLUEPRINT v0.1 |
| C1 | AI/headless | SYNTHESIS + BLUEPRINT v0.1 |
| B1 | multiplayer/session/reconnect | SYNTHESIS + BLUEPRINT v0.1 |
| D1 | data/content/runtime package | SYNTHESIS + BLUEPRINT v0.1 |
| R1 | release/diagnostics/compatibility | SYNTHESIS + BLUEPRINT v0.1 |
| E1 | Godot/client/UI | SYNTHESIS + BLUEPRINT v0.1 |
| A7 | combat | DEFERRED TO RULES/IMPLEMENTATION NEED |
| Q | full OPEN_QUESTIONS review | **NEXT MAJOR ANALYSIS TRACK** |

# 2. Program milestone

A nagyívű előretervezés első architecture-köre lefedi:
- engine authority;
- actions/events;
- timing;
- abilities;
- determinism/replay;
- AI;
- multiplayer;
- data/package;
- release;
- client/UI.

Ez nem azt jelenti, hogy minden implementation kész.

A blueprint:
- célarchitektúra;
- invariáns;
- dependency;
- anti-pattern;
- future gate.

# 3. Következő lépés

## 3.1 Registry maintenance
Aktuális Learning Catalog / Source Registry:
- projektszám;
- analysis count;
- pinned commits;
- új source-ok;
- ocgcore külön rekord;
- local path convention.

## 3.2 Blueprint consistency audit
Keresni:
- ellentmondó candidate;
- duplicated authority;
- stale version/base;
- accidental rules assertion;
- implementation overclaim.

## 3.3 Full OPEN_QUESTIONS
Minden OQ besorolása:

```text
ANSWERED_BY_OFFICIAL_RULES
ANSWERED_BY_PRODUCTION
ANSWERED_BY_ACCEPTED_DECISION
ANSWERABLE_BY_BLUEPRINT
RULES_CLARIFICATION_REQUIRED
IMPLEMENTATION_DECISION_REQUIRED
DEFERRED_FEATURE
OBSOLETE_OR_SUPERSEDED
STILL_OPEN
```

Blueprint önmagában még nem „accepted decision”, amíg külön nem fogadjuk el.

# 4. Reaction track

A Reaction/Priority marad a legközelebbi core implementation candidate.

Még:
- RC1 single-responder closure;
- RC2 reaction-created trigger boundary;
- v0.2 technikai proposalok explicit elfogadása.

Utána contract patch + Codex implementation.

# 5. Combat

Combatot nem tervezünk vakon előre a reaction rendszer előtt.

A reaction foundation után külön official combat rules audit + learning synthesis, ha szükséges.

# 6. Új learning project gate

Mostantól új source csak konkrét gapre.

Nincs általános „gyűjtsünk még több card engine-t” feladat.

# 7. Változásnapló
## 0.8 – 2026-08-15
- E1 lezárva;
- pre-OQ architecture coverage milestone complete;
- registry maintenance + consistency audit + full OQ lett következő fő track.
