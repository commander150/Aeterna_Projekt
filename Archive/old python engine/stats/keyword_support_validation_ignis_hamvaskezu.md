# Keyword Support Validation: Ignis / Hamvaskezű

## Scope

- Realm: `Ignis`
- Clan: `Hamvaskezű`
- Source audit: `stats/keyword_support_audit_ignis_hamvaskezu.csv`
- Validation mode: manual spot-check with concrete code evidence

## Method

Each selected card was reviewed against four evidence layers:

1. parsing / keyword detection
2. metadata / registry support
3. runtime gameplay execution
4. test or other logic evidence

The validation is intentionally conservative:

- `supported`: strong runtime path exists and is meaningfully evidenced
- `partial`: parsing/registry exists and there is some runtime path, but coverage is card-specific, weakly evidenced, or incomplete
- `uncertain`: parsing/registry exists, but runtime hookup is not clearly active
- `missing`: no convincing support found

## Validated Cards

### 1. Hamvaskezű Újonc

- card_name: `Hamvaskezű Újonc`
- raw_ability: `[HORIZONT] Gyorsaság (Celerity)`
- detected_keywords: `celerity`
- parsing / detection:
  - `engine/keyword_registry.py` registers `celerity`
  - `engine/card.py` stores `keywords_normalized`
- metadata / registry:
  - canonical alias support exists for `celerity` / `gyorsaság`
- runtime gameplay:
  - `engine/keyword_engine.py` -> `KeywordEngine.on_summon()` sets `kimerult = False`
  - `_register_keyword_trigger_handlers()` binds this to `on_summon`
- tests / logic evidence:
  - `tests/test_card_model.py` -> `test_celerity_unit_starts_not_exhausted`
  - runtime logs already show `Celerity: ... azonnal tamadhat.`
- final status: `supported`
- justification:
  - parsing, registry, summon-time runtime execution, and direct test evidence all exist.

### 2. Lángszárnyú Hiéna

- card_name: `Lángszárnyú Hiéna`
- raw_ability: `[HORIZONT] Légies (Ethereal). Gyorsaság (Celerity).`
- detected_keywords: `ethereal`, `celerity`
- parsing / detection:
  - `engine/keyword_registry.py` registers both keywords
  - `engine/card.py` and `engine/keyword_engine.py` can read both
- metadata / registry:
  - aliases exist for `ethereal` / `légies` and `celerity` / `gyorsaság`
- runtime gameplay:
  - `celerity`: `engine/keyword_engine.py` -> `on_summon`
  - `ethereal`: `engine/keyword_engine.py` -> `filter_blockers_for_attacker()` only allows ethereal blockers
  - `engine/game.py` actively calls `KeywordEngine.filter_blockers_for_attacker(...)`
- tests / logic evidence:
  - `tests/test_keywords.py` -> `test_filter_blockers_for_ethereal_attacker`
  - `tests/test_card_model.py` -> `test_celerity_unit_starts_not_exhausted`
- final status: `supported`
- justification:
  - both keywords have clear runtime effects and direct test evidence.

### 3. Vörösréz Pajzsos

- card_name: `Vörösréz Pajzsos`
- raw_ability: `[HORIZONT] Oltalom (Aegis). Ha sikeresen blokkol egy támadást és túléli, az ellenséges támadó kap 1 sebzést a forró pajzstól.`
- detected_keywords: `aegis`
- parsing / detection:
  - `engine/keyword_registry.py` registers `aegis`
  - `engine/card.py` stores keyword metadata
- metadata / registry:
  - alias support exists for `aegis` / `oltalom`
- runtime gameplay:
  - `engine/keyword_engine.py` -> `get_blockers()` prioritizes Aegis blockers
  - `engine/game.py` calls `KeywordEngine.get_blockers(...)` in combat
- tests / logic evidence:
  - no dedicated `Aegis` blocker test found in the current suite
  - the extra “return damage” sentence is not part of generic keyword support
- final status: `partial`
- justification:
  - the keyword is clearly implemented in combat selection, but current proof is weaker than the strongest keywords and lacks direct validation tests.

### 4. Hamvaskezű Seregvezér

- card_name: `Hamvaskezű Seregvezér`
- raw_ability: `[HORIZONT] Oltalom (Aegis). A mögötte lévő Zenit mezőn tartózkodó Entitások "Harmonizálás" képessége kétszeres szorzóval adódik hozzá a Seregvezér erejéhez.`
- detected_keywords: `aegis`, `harmonize`
- parsing / detection:
  - both keywords are registered in `engine/keyword_registry.py`
- metadata / registry:
  - `engine/card.py` stores them as normalized metadata
- runtime gameplay:
  - `aegis`: same runtime path as above (`get_blockers` in combat)
  - `harmonize`: `engine/game.py` calls `KeywordEngine.get_harmonize_bonus(...)` for Zenit support
- tests / logic evidence:
  - `tests/test_keywords.py` -> `test_get_harmonize_bonus_depends_on_support_magnitude`
  - no direct dedicated test for Aegis blocker precedence
  - the “double multiplier” text is not generic keyword support
- final status: `partial`
- justification:
  - `harmonize` itself is strongly supported, but the combined card still depends on partially evidenced `aegis` and on a card-specific extra rule.

### 5. Pokoltűz Sárkány

- card_name: `Pokoltűz Sárkány`
- raw_ability: `[HORIZONT] Hasítás (Sundering). Métely (Bane).`
- detected_keywords: `sundering`, `bane`
- parsing / detection:
  - both registered in `engine/keyword_registry.py`
- metadata / registry:
  - both are normalized and readable via `engine/card.py` / `engine/keyword_engine.py`
- runtime gameplay:
  - `bane`: `engine/keyword_engine.py` -> `on_damage_dealt()` marks target, `resolve_bane()` destroys marked defender
  - `engine/game.py` calls `KeywordEngine.resolve_bane(...)`
  - `sundering`: `engine/keyword_engine.py` -> `resolve_sundering()`
  - `engine/game.py` calls `KeywordEngine.resolve_sundering(...)`
- tests / logic evidence:
  - `tests/test_keywords.py` -> `test_resolve_bane_destroys_marked_target`
  - no dedicated `sundering` test found
- final status: `partial`
- justification:
  - `bane` is strongly evidenced, but `sundering` is less directly validated, so the combined card is better classified conservatively as partial.

### 6. Élő Meteor

- card_name: `Élő Meteor`
- raw_ability: `[DOMÍNIUM] Riadó (Clarion): Becsapódáskor az Élő Meteor azonnal elszenved 3 sebzést, és a saját Horizontodon lévő összes többi Entitás is kap 1 sebzést.`
- detected_keywords: `clarion`
- parsing / detection:
  - `engine/keyword_registry.py` registers `clarion`
  - `engine/card.py` stores normalized keywords
- metadata / registry:
  - alias support exists for `clarion` / `riadó`
- runtime gameplay:
  - there is no generic Clarion executor in `engine/keyword_engine.py`
  - actual Clarion gameplay in the repo is usually card-specific via `cards/resolver.py` handlers
- tests / logic evidence:
  - no dedicated generic Clarion runtime test exists
  - several Clarion cards are custom handlers, which shows the keyword is not fully generic
- final status: `partial`
- justification:
  - the keyword is parsed and recognized, but runtime execution is mostly card-specific.

### 7. Goblin Robbanómester

- card_name: `Goblin Robbanómester`
- raw_ability: `[DOMÍNIUM] Riadó (Clarion): Okoz 2 sebzést egy ellenséges Entitásnak, de a Robbanómester is elszenved 1 sebzést.`
- detected_keywords: `clarion`
- parsing / detection:
  - same `clarion` parsing/registry support as above
- metadata / registry:
  - recognized in registry and metadata
- runtime gameplay:
  - still depends on a concrete card handler or structured resolution
  - no generic “all Clarion cards execute their payload” support exists
- tests / logic evidence:
  - no dedicated handler/test was found for this exact card
- final status: `partial`
- justification:
  - the keyword is real and recognized, but runtime support is not guaranteed just from the keyword.

### 8. Perzselő Csapás

- card_name: `Perzselő Csapás`
- raw_ability: `Egy választott saját Entitásod kap +3 ATK-t a harc idejére. Reakció (Burst): Ingyen elsüthető.`
- detected_keywords: `burst`
- parsing / detection:
  - `engine/keyword_registry.py` registers `burst`
  - `engine/card.py` marks `reakcio_e` from keyword/text
- metadata / registry:
  - alias support exists for `burst` / `reakció`
- runtime gameplay:
  - `engine/keyword_engine.py` has `has_burst()`
  - `cards/resolver.py` has separate burst category handling
  - but the actual “harc idejére +3 ATK” effect is not generic keyword runtime
- tests / logic evidence:
  - no direct generic burst-only execution test
  - keyword support exists, exact card effect still wants explicit gameplay closure
- final status: `partial`
- justification:
  - burst recognition is real, but effect execution is not automatically guaranteed by the keyword alone.

### 9. A Megperzselt Küzdőtér

- card_name: `A Megperzselt Küzdőtér`
- raw_ability: `Amíg aktív, egyik játékos sem idézhet Entitást a Zenitbe, kivéve, ha az rendelkezik Harmonizálás vagy Rezonancia kulcsszóval.`
- detected_keywords: `harmonize`, `resonance`
- parsing / detection:
  - both are registered in `engine/keyword_registry.py`
- metadata / registry:
  - both are recognized and normalized correctly
- runtime gameplay:
  - `harmonize`: clear runtime usage exists in `engine/game.py`
  - `resonance`: `engine/keyword_engine.py` contains `modify_attack()`, but current code search did not show a live call site for that helper
- tests / logic evidence:
  - `harmonize` has a direct test in `tests/test_keywords.py`
  - no direct resonance runtime test found
- final status: `uncertain`
- justification:
  - because the card explicitly relies on `resonance`, and the current runtime hookup for resonance is not clearly active in the main combat path.

### 10. Tűzgyűrű

- card_name: `Tűzgyűrű`
- raw_ability: `Egy saját Entitásod megkapja az Oltalom (Aegis) kulcsszót a kör végéig. Bármely ellenség, ami megtámadja őt ebben a körben, kap 2 sebzést.`
- detected_keywords: `aegis`
- parsing / detection:
  - `aegis` registered in `engine/keyword_registry.py`
- metadata / registry:
  - keyword readable via metadata and runtime keyword helpers
- runtime gameplay:
  - temporary keyword grant is supported in `cards/priority_handlers.py` via `_grant_keyword(...)`
  - combat blocker preference for Aegis exists in `engine/keyword_engine.py`
- tests / logic evidence:
  - no dedicated test found for the generic Aegis blocker rule itself
  - the “attacker takes 2 damage” rider is not generic keyword support
- final status: `partial`
- justification:
  - the temporary grant path is real, but the card’s full combat consequence is beyond pure keyword support, and Aegis is still better treated conservatively as partial.

## Validation Summary (10 cards)

- supported: `3`
- partial: `6`
- uncertain: `1`
- missing: `0`

## Corrected Full-Scope Summary (after conservative audit logic update)

For the full `Ignis / Hamvaskezű` keyword-only scope:

- supported: `5`
- partial: `15`
- uncertain: `1`
- missing: `0`

## Status Changes Observed

The main optimistic statuses that were corrected downward:

- `aegis`: `supported -> partial`
- `sundering`: `supported -> partial`
- `resonance`: `supported -> uncertain`

Representative card-level changes:

- `Vörösréz Pajzsos`: `supported -> partial`
- `Hamvaskezű Seregvezér`: `supported -> partial`
- `Pokoltűz Sárkány`: `supported -> partial`
- `Perzselt-páncélos Ork`: `supported -> partial`
- `A Megperzselt Küzdőtér`: `supported -> uncertain`

## Conclusion

The first audit was directionally useful, but too optimistic for a few keywords that had registry support and some runtime code, yet did not have equally strong proof of active gameplay execution.

After conservative correction:

- `celerity`, `ethereal`, `harmonize`, and `bane` remain the strongest validated keywords in this scope
- `clarion`, `burst`, `aegis`, and `sundering` are better treated as `partial`
- `resonance` is currently best treated as `uncertain` until a clearly active runtime call path is demonstrated
