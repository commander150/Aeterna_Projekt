# Keyword Compliance Audit

Scope: `Kulcsszavak_Felismerve`

Note: the standard document also allows `blank` as an explicit placeholder, but this audit only covers the actual canonical keywords themselves.

| keyword | in_standard_doc | accepted_by_loader | accepted_by_validator | aliases | runtime_supported | implementation_location | test_coverage | cards_using_it | current_status | exact_runtime_meaning | missing_parts | recommended_next_step |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `aegis` | yes | yes | yes | `oltalom` | yes | `engine/keyword_registry.py`, `engine/keyword_engine.py`, `engine/game.py`, `cards/priority_handlers.py` | good | `87 cards; examples: Vörösréz Pajzsos, Hamvaskezű Seregvezér, Tűzhegy Titánja, Robbanó Pajzs` | `fully_working` | Forces Aegis-capable blocking through `get_blockers`, and many card handlers can grant/remove temporary or permanent Aegis. | No major engine-side gap found at keyword level. | Keep as reference implementation for passive defensive keywords. |
| `bane` | yes | yes | yes | `metely`, `métely` | yes | `engine/keyword_registry.py`, `engine/keyword_engine.py`, `engine/game.py` | good | `16 cards; examples: Pokoltűz Sárkány, Húsevő Növény, Tőrtáncos Orgyilkos` | `fully_working` | On combat damage, the defender is marked with `bane_target`, then `resolve_bane` destroys the marked defender if the attacker has Bane. | Test coverage is combat-focused; no extra missing runtime branch is visible for the base keyword. | Keep as reference implementation for combat-result keywords. |
| `burst` | yes | yes | yes | `reakcio`, `reakció` | partial | `engine/keyword_registry.py`, `engine/keyword_engine.py`, `engine/effects.py`, `engine/effect_diagnostics_v2.py`, `cards/resolver.py` | good | `41 cards; examples: Vakító Szikra, Utolsó Szikra, Perzselő Csapás, Lángok Védelme` | `partially_implemented` | Sets burst readiness in targeting state, participates in seal-break reaction flow, and has dedicated burst dispatch/diagnostics paths with many card-specific handlers. | The keyword itself is recognized and burst dispatch exists, but the full rules meaning is still spread between core combat/seal flow and many card-local handlers instead of one generic keyword layer. | Continue consolidating burst handling behind shared trigger/runtime helpers instead of new per-card branches where possible. |
| `celerity` | yes | yes | yes | `gyorsasag`, `gyorsaság` | yes | `engine/keyword_registry.py`, `engine/keyword_engine.py`, `engine/card.py` | good | `51 cards; examples: Hamvaskezű Újonc, Lángszárnyú Hiéna, Lángnyelvű Sárkányfi, Viharmadár` | `fully_working` | On summon, units with Celerity become immediately ready and can attack; unit construction also respects the keyword in battle-unit setup. | No major engine-side gap found at keyword level. | Keep as a clean example of simple summon-time keyword execution. |
| `clarion` | yes | yes | yes | `riado`, `riadó` | partial | `engine/keyword_registry.py`, `engine/keyword_engine.py`, `engine/effects.py`, `engine/structured_effects.py`, `cards/resolver.py`, `cards/priority_handlers.py` | partial | `82 cards; examples: Parázsfarkas, Ignis Csonttörő, Élő Meteor, Hamvaskezű Toborzó` | `partially_implemented` | The runtime treats Clarion as an on-play/on-summon-style signal, and many concrete Clarion cards are implemented through resolver/priority handlers. | Clarion is not yet a fully generic metadata-driven keyword effect layer; support is still strongly card-specific. | Build a shared Clarion resolution adapter for the simplest damage/draw/heal/buff Clarion patterns. |
| `echo` | yes | yes | yes | `visszhang` | partial | `engine/keyword_registry.py`, `engine/keyword_engine.py`, `engine/effects.py`, `engine/effect_diagnostics_v2.py`, `cards/priority_handlers.py` | partial | `25 cards; examples: Lángköpő Gyík, Hamufőnix, Rügyező Csemete, Szentjánosbogár-raj` | `partially_implemented` | The engine recognizes Echo, has death-side parsing/dispatch hooks, and several Echo cards are implemented through explicit death handlers. | Echo semantics are not yet unified into one generic keyword resolver; much of the real behavior still lives in card-specific death handlers. | Next improvement should target a shared `on_death/echo` adapter for the simplest recurring Echo patterns. |
| `ethereal` | yes | yes | yes | `legies`, `légies` | yes | `engine/keyword_registry.py`, `engine/keyword_engine.py`, `engine/game.py` | good | `65 cards; examples: Lángszárnyú Hiéna, Parázs-Szellem, Viharmadár, Óriás Sas` | `fully_working` | Ethereal attackers can only be blocked by Ethereal blockers through `filter_blockers_for_attacker`; the targeting state also marks related protection behavior. | The runtime meaning implemented is mostly combat/blocking-oriented; if the full rules later require more than this, that would be an extension, not a missing base implementation. | Keep as reference implementation for passive combat-filter keywords. |
| `harmonize` | yes | yes | yes | `harmonizalas`, `harmonizálás` | yes | `engine/keyword_registry.py`, `engine/keyword_engine.py`, `engine/game.py` | good | `32 cards; examples: A Megperzselt Küzdőtér, Lángnyelv Adeptus, Láng-Dajka, Vadonjáró Őrszem` | `fully_working` | `get_harmonize_bonus` computes support-based ATK bonus from the support unit's magnitude, and combat flow uses it. | The base keyword effect is implemented, though many Harmonize cards also add extra card-specific text beyond the keyword. | Keep as a reference implementation for magnitude-dependent support keywords. |
| `resonance` | yes | yes | yes | `rezonancia` | partial | `engine/keyword_registry.py`, `engine/keyword_engine.py`, `engine/game.py`, `engine/targeting.py` | partial | `45 cards; examples: Parázsló Tanítvány, Hamuszájú Próféta, Parázs-Szellem, Tünde Pyromanta` | `partially_implemented` | Resonance currently modifies attack through owner aura (`modify_attack`), and static targeting state also flags some related allowances. | The keyword is recognized and has real combat impact, but its full rules meaning appears broader than the current generic runtime behavior. Many Resonance cards still rely on extra local logic. | Treat Resonance as a real shared mechanic, then incrementally widen the generic runtime meaning beyond ATK modification. |
| `sundering` | yes | yes | yes | `hasitas`, `hasítás` | yes | `engine/keyword_registry.py`, `engine/keyword_engine.py`, `engine/game.py` | good | `52 cards; examples: Lángoló Öklű Bajnok, Pokoltűz Sárkány, Inferno Leviatán, Izzó Elementál` | `fully_working` | After lethal combat damage, `resolve_sundering` breaks an extra seal for attackers with Sundering. | No major engine-side gap found at keyword level. | Keep as reference implementation for combat-follow-up keywords. |
| `taunt` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `2 cards; examples: Pokol-kutyák Ura, Ork Csatakiáltás` | `missing_implementation` | The canonical keyword is accepted by the structured data pipeline, but there is no registry definition, no keyword-engine behavior, and no targeting/combat enforcement tied to Taunt. | Missing keyword registry entry, missing runtime meaning, missing blocker/attacker target restriction logic, and missing direct tests. | This is the cleanest next keyword-level implementation target: add registry support, define targeting/combat meaning, and add focused tests. |

## Summary

### Actually working

- `aegis`
- `bane`
- `celerity`
- `ethereal`
- `harmonize`
- `sundering`

### Recognized only

- none in a strict sense; the closest case is `taunt`, but it is more accurate to call it missing than merely recognized because it has no meaningful runtime behavior.

### Partial

- `burst`
- `clarion`
- `echo`
- `resonance`

### Missing

- `taunt`

## Best implementation order

1. `taunt`
   Reason: fully missing at runtime, very small keyword set usage, clean isolated target-rule candidate.
2. `clarion`
   Reason: many cards use it, and a shared adapter would likely reduce a lot of card-local resolver work.
3. `echo`
   Reason: death-side shared routing would unlock several partially-implemented cards at once.
4. `resonance`
   Reason: already has a base mechanic, but needs clearer generic semantics beyond the current ATK-centric behavior.
5. `burst`
   Reason: it already works in many places, but consolidating it is more of a medium cleanup than the cheapest next keyword win.
