# Target Compliance Audit

Scope: `Célpont_Felismerve`

Method:
- Canonical target list comes from [kartya_tabla_szabvany_frissett.md](/e:/Letöltések/Aeterna/Aeterna_Projekt/kartya_tabla_szabvany_frissett.md).
- Loader/validator acceptance is checked against [data/loader.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/data/loader.py) and [engine/card_metadata.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/engine/card_metadata.py).
- Runtime support is judged conservatively from the shared target layer in [engine/targeting.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/engine/targeting.py), generic action helpers in [engine/actions.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/engine/actions.py), effect resolution in [engine/structured_effects.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/engine/structured_effects.py) and [engine/effects.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/engine/effects.py), plus local handlers in [cards/priority_handlers.py](/e:/Letöltések/Aeterna/Aeterna_Projekt/cards/priority_handlers.py) and tests.
- Fresh logs were used only as secondary evidence; they still show many cards as `structured_deferred` or `fallback_text_resolved`, which supports conservative statuses for long-tail target types.

Note: the standard document also allows `blank` as an explicit placeholder, but this audit only covers the actual canonical target types themselves.

| target | in_standard_doc | accepted_by_loader | accepted_by_validator | aliases | runtime_supported | implementation_location | test_coverage | cards_using_it | current_status | exact_runtime_meaning | missing_parts | recommended_next_step |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `self` | yes | yes | yes | `self_entity` | yes | `engine/card.py`, `engine/structured_effects.py`, `engine/effects.py`, `cards/priority_handlers.py` | good | `270 cards; examples: Hamvaskezű Újonc, Lángoló Öklű Bajnok, Lángoló Pörölyös, Parázsfarkas` | `fully_working` | The source card or source unit can reliably modify itself through both structured and local effect paths without extra target selection. | No major target-type gap. | Keep as a reference self-target type. |
| `own_entity` | yes | yes | yes | `sajat_entitas` | yes | `engine/actions.py`, `engine/structured_effects.py`, `engine/effects.py`, `cards/priority_handlers.py`, `tests/test_card_model.py` | good | `126 cards; examples: Vér és Hamu, A Lángok Haragja, Perzselő Csapás, Tűzgyűrű` | `fully_working` | Shared helpers can choose allied board entities, and many spells/buffs already operate on a generic allied entity target. | No major target-type gap. | Keep as a core board-target reference. |
| `other_own_entity` | yes | yes | yes | `masik_sajat_entitas` | partial | `cards/priority_handlers.py`, `engine/actions.py`, `engine/structured_effects.py` | partial | `9 cards; examples: Lángsörényű Oroszlán, Gyöngy-Kovács, Fényhozó Apród, Tükröződő Remény` | `partially_implemented` | Runtime can often pick another allied unit through local logic. | There is no generic selector that excludes the source entity by default. | Add a small shared allied-target helper with `exclude_source=True`. |
| `enemy_entity` | yes | yes | yes | `ellenseges_entitas` | yes | `engine/actions.py`, `engine/structured_effects.py`, `engine/effects.py`, `cards/priority_handlers.py`, `tests/test_card_model.py`, `tests/test_structured_effects.py` | good | `137 cards; examples: Vörösréz Pajzsos, Lángköpő Gyík, Goblin Robbanómester, Pokol-kutyák Ura` | `fully_working` | Shared logic can select enemy entities and validate spell/trap targeting against them. | No major target-type gap. | Keep as a core board-target reference. |
| `own_horizont_entity` | yes | yes | yes | `none` | partial | `engine/structured_effects.py`, `engine/effects.py`, `cards/priority_handlers.py` | partial | `53 cards; examples: Kirobbanó Erő, Pusztító Roham, A Hamvaskezűek Arénája, Tűzfal-Kántáló` | `partially_implemented` | Runtime can often prefer or filter the allied front row through local checks and zone-aware selectors. | No generic canonical selector exists for "allied front entity only" across all effects. | Add reusable allied-zone selectors in `ActionLibrary`. |
| `enemy_horizont_entity` | yes | yes | yes | `none` | partial | `engine/structured_effects.py`, `engine/effects.py`, `cards/priority_handlers.py`, `tests/test_structured_effects.py` | partial | `44 cards; examples: Ignis Csonttörő, Vakító Szikra, Csapda a Hamuban, A Végtelen Harc Mezeje` | `partially_implemented` | Runtime already supports many enemy front-row effects through prefer-zone logic and lane-aware handlers. | Target resolution still depends too often on text/handler-specific zone preference instead of one canonical selector. | Add a direct shared `enemy_horizont_entity` selector. |
| `own_zenit_entity` | yes | yes | yes | `none` | partial | `engine/actions.py`, `engine/structured_effects.py`, `cards/priority_handlers.py` | partial | `11 cards; examples: A Főnix Könnye, Perzselő Akarat, Tengeri Császár, Áramlat-szellem` | `partially_implemented` | Allied back-row interactions already exist through zone-specific local logic. | No generic allied Zenit selector is exposed as a canonical target primitive. | Add a reusable `own_zenit_entity` helper next to the Horizont selectors. |
| `enemy_zenit_entity` | yes | yes | yes | `none` | partial | `engine/game.py`, `engine/structured_effects.py`, `engine/effects.py`, `cards/priority_handlers.py`, `tests/test_structured_effects.py` | partial | `20 cards; examples: Füstkéses Nindzsa, Hamuba Fojtás, Inferno Leviatán, Hamis Menedék` | `partially_implemented` | Runtime can hit or move attackable Zenit entities in several proven places. | The shared target layer does not yet offer a fully generic "enemy back-row entity" selector independent of effect-specific code. | Add a dedicated enemy-Zenit selector with consistent attackability rules. |
| `own_entities` | yes | yes | yes | `none` | partial | `engine/structured_effects.py`, `engine/effects.py`, `cards/priority_handlers.py` | partial | `64 cards; examples: Hamvaskezű Bestia-lovas, Vérforraló Üvöltés, Ork Tábor, Megperzselt Föld` | `partially_implemented` | The engine can iterate over allied board entities in many effects. | There is no single canonical "all allied entities" selector reused everywhere. | Add collection helpers for grouped allied targets. |
| `enemy_entities` | yes | yes | yes | `none` | partial | `engine/structured_effects.py`, `engine/effects.py`, `cards/priority_handlers.py` | partial | `20 cards; examples: Ignatar a Hamvaskezű, Lángnyelvek Tánca, Megperzselt Föld, Nagy Áramlás` | `partially_implemented` | The engine can iterate enemy board entities for area effects. | The grouped enemy-entity selector is not centralized and often effect-local. | Add collection helpers for grouped enemy targets. |
| `own_horizont_entities` | yes | yes | yes | `none` | partial | `engine/structured_effects.py`, `cards/priority_handlers.py` | partial | `29 cards; examples: Tűzvihar Bajnoka, Élő Meteor, Hamvaskezű Toborzó, Ork Hadúr` | `partially_implemented` | Allied front-row iteration exists in several local handlers. | No generic grouped front-row selector is exposed. | Add grouped zone selectors once single-unit zone selectors exist. |
| `enemy_horizont_entities` | yes | yes | yes | `none` | partial | `engine/structured_effects.py`, `cards/priority_handlers.py` | partial | `23 cards; examples: Ork Csatakiáltás, Démoni Lángidéző, Tűzeső, Cunami Idézése` | `partially_implemented` | Many multi-target damage and debuff cards already iterate over enemy front-row units. | The grouped selector is still effect-local rather than canonical. | Add grouped enemy-front selectors after `enemy_horizont_entity`. |
| `own_zenit_entities` | yes | yes | yes | `none` | partial | `cards/priority_handlers.py`, `engine/actions.py` | none | `7 cards; examples: Pernye-Fátyol, A Lángok Szentélye, Tengeristen Megtestesülése, Smaragd Pikkelyes Őr` | `partially_implemented` | Allied back-row iteration exists in some local handlers. | No generic grouped Zenit selector exists. | Add only after single Zenit target helpers are in place. |
| `enemy_zenit_entities` | yes | yes | yes | `none` | partial | `cards/priority_handlers.py`, `engine/game.py` | none | `4 cards; examples: Napkitörés Sárkány, Égő Visszhang, Viharos Menekülés, A Sivatag Ura` | `partially_implemented` | Enemy back-row iteration exists in some local handlers and combat flow. | No canonical grouped selector exists. | Add after `enemy_zenit_entity` is canonicalized. |
| `own_seal` | yes | yes | yes | `sajat_pecset` | partial | `engine/effects.py`, `cards/priority_handlers.py` | partial | `13 cards; examples: Démoni Lángidéző, Aeterna Prófétája, Seraphiel az Élet Fénye, Bűnbánó Inkvizítor` | `partially_implemented` | Own-seal interactions exist, including breaking or protecting own seals, but usually through local or effect-specific logic. | No generic explicit own-seal selector exists. | Add a tiny seal-target helper shared by own/enemy seal effects. |
| `enemy_seal` | yes | yes | yes | `pecset`, `ellenseges_pecset` | partial | `engine/structured_effects.py`, `engine/effects.py`, `cards/priority_handlers.py`, `tests/test_structured_effects.py` | partial | `27 cards; examples: Páncéltörő Csapás, Vér és Hamu, Utolsó Szikra, Hamis Parancs` | `partially_implemented` | Enemy seal damage and seal-related traps clearly work at runtime. | The engine usually treats seals as an aggregate stack rather than a precise chosen seal target, so target specificity is weak. | Add canonical seal-target semantics only if individual seal selection becomes important. |
| `own_seals` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `0 cards` | `recognized_only` | The target type is standard and accepted by the data layer. | No observed current-card use and no runtime selection path. | Leave as recognized-only until the dataset needs it. |
| `enemy_seals` | yes | yes | yes | `pecsetek` | no | `engine/card_metadata.py`, `data/loader.py` | none | `0 cards` | `recognized_only` | The target type is structurally valid but currently unused. | No runtime selection path exists. | Leave as recognized-only until cards require multi-seal targeting. |
| `own_aeternal` | yes | yes | yes | `none` | partial | `engine/effects.py`, `cards/priority_handlers.py` | partial | `9 cards; examples: Fagyos Tükröződés, Bűnbánó Inkvizítor, Fényhozó Láng, Szent Menedék` | `partially_implemented` | Aeternal-side protection/healing semantics exist in local runtime paths. | No generic canonical Aeternal target abstraction is exposed. | Add once Aeternal-targeted cards become a larger group. |
| `enemy_aeternal` | yes | yes | yes | `none` | partial | `engine/effects.py`, `cards/priority_handlers.py` | partial | `10 cards; examples: Füstbeburkolt Illúzió, Lángoló Tükör, Tengeri Császár, Zátony-Lopakodó` | `partially_implemented` | Enemy direct-damage and redirection effects can already reach the enemy Aeternal domain in local logic. | No generic enemy-Aeternal target helper exists. | Fold into the same helper family as `enemy_seal`. |
| `own_hand` | yes | yes | yes | `none` | partial | `engine/effects.py`, `cards/priority_handlers.py` | partial | `13 cards; examples: Ignis Varázsszövő, A Katlan Őrzője, Tűzkatlan Főmágusa, Az Örök Tűz Szentélye` | `partially_implemented` | Runtime can inspect or manipulate the owner's hand in some local/fallback paths. | No generic hand-target selection layer exists beyond coarse list access. | Add after discard/search/tutor cleanup if needed. |
| `enemy_hand` | yes | yes | yes | `none` | partial | `engine/effects.py`, `cards/priority_handlers.py` | partial | `13 cards; examples: Túlhevült Mana, Árapály-visszacsapás, Pecsétvédő Csapda, Városi Patkányraj` | `partially_implemented` | Opponent hand inspection and some discard effects already exist. | There is no generic canonical enemy-hand selection API. | Add only once hand-disruption cards are prioritized. |
| `own_deck` | yes | yes | yes | `none` | partial | `engine/actions.py`, `engine/effects.py`, `cards/priority_handlers.py` | partial | `21 cards; examples: Mélységi Behívó, A Földanya Hangja, A Természet Szava, Farkasvérű Nyomkereső` | `partially_implemented` | Search and top-card inspection of the owner deck already work in several places. | No generic deck-target abstraction exists beyond search predicates and direct list access. | Good medium-cost target family to standardize together with `tutor`. |
| `own_graveyard_entity` | yes | yes | yes | `none` | partial | `engine/actions.py`, `engine/effects.py`, `cards/priority_handlers.py` | partial | `18 cards; examples: Tűzkatlan Főmágusa, Sámán a Hamuból, Hamvakból Felszálló, Életadó Főpap` | `partially_implemented` | Graveyard-to-hand and graveyard-to-board effects already exist with entity filtering. | No generic canonical graveyard entity selector is exposed. | Standardize with graveyard recursion cleanup. |
| `enemy_spell` | yes | yes | yes | `none` | partial | `engine/targeting.py`, `cards/resolver.py`, `cards/priority_handlers.py`, `engine/effects.py`, `tests/test_card_model.py` | partial | `4 cards; examples: Megtört Áramlat, Váratlan Adóellenőrzés, Megcsapolt Erő, Köd-Alak` | `partially_implemented` | Enemy spell targeting exists during spell-target reaction resolution and counterspell-style handlers. | There is no broad persistent target object model for spells outside those local windows. | Keep on the existing reaction path; do not over-generalize yet. |
| `enemy_spell_or_ritual` | yes | yes | yes | `none` | partial | `cards/resolver.py`, `cards/priority_handlers.py`, `engine/effects.py` | partial | `5 cards; examples: Láng-Pajzs, Fagyos Tükröződés, Váratlan Virágzás, Ragyogó Csapda` | `partially_implemented` | Runtime can already intercept enemy spell-like actions in several reaction handlers. | Spell and ritual targeting is not yet unified under one persistent target family. | Standardize together with the `on_enemy_spell_or_ritual_played` trigger family if needed. |
| `enemy_hand_card` | yes | yes | yes | `none` | partial | `engine/effects.py`, `cards/priority_handlers.py` | none | `3 cards; examples: Információszivárogtatás, Zsarolás, Kínok Hálója` | `partially_implemented` | Some effects can single out or refer to a just-drawn or selected enemy hand card. | There is no generic object-level representation for cards in enemy hand. | Add only if single-card hand targeting becomes more common. |
| `enemy_face_down_trap` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `1 card; example: Titkos Találkozó` | `missing_implementation` | The target type is recognized structurally only. | Missing runtime inspection/selection logic for enemy face-down traps. | Defer; this likely needs hidden-information target rules. |
| `own_face_down_trap` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `1 card; example: Megtévesztő Manőver` | `missing_implementation` | The target type is metadata-only at present. | Missing runtime selection logic for own face-down traps as explicit targets. | Defer with the same hidden-information target family as enemy face-down traps. |
| `own_graveyard` | yes | yes | yes | `none` | partial | `engine/actions.py`, `engine/effects.py`, `cards/priority_handlers.py` | none | `1 card; example: Kórus Dala` | `partially_implemented` | The engine can inspect and move cards from the owner's graveyard as a zone. | There is no generic canonical zone-target abstraction separate from entity-only graveyard effects. | Fold into graveyard target cleanup when graveyard_recursion is standardized. |
| `opponent` | yes | yes | yes | `jatekos`, `opponent_player` | partial | `engine/effects.py`, `cards/priority_handlers.py` | partial | `6 cards; examples: Árnyékpárduc, Felderítő Bagoly, Piaci Koldus, Fogadó a Keresztútnál` | `partially_implemented` | Player/opponent-directed resource or choice effects already exist in local handlers. | No generic player-target object layer is exposed to the structured system. | Add a tiny player-target abstraction once more opponent-only cards rely on it. |
| `lane` | yes | yes | yes | `none` | partial | `engine/game.py`, `cards/priority_handlers.py`, `engine/actions.py`, `tests/test_priority_handlers.py` | partial | `4 cards; examples: Tűzvihar Megidézése, Szeizmikus Lökés, Zárt Alakzat, Ciklon Söprés` | `partially_implemented` | Lane-based reasoning already exists in combat and some local spell/trap handlers. | There is no generic lane target abstraction exposed as a reusable canonical selector. | Add only after board movement and opposing-lane helpers are more centralized. |
| `source_card` | yes | yes | yes | `none` | no | `engine/card_metadata.py`, `data/loader.py` | none | `1 card; example: Szindikátusi Zsaroló` | `recognized_only` | The target type is accepted by the data layer. | No general runtime concept exists for selecting an arbitrary source card as a target object. | Defer until source mechanics are formalized. |
| `own_source_card` | yes | yes | yes | `none` | partial | `cards/priority_handlers.py`, `engine/effects.py` | none | `2 cards; examples: Pangea Őssárkány, Az Ősforrás Őrzője` | `partially_implemented` | Source-card interactions exist in some local handlers. | No generic canonical selector exists for own source cards. | Fold into future source target cleanup. |
| `enemy_source_card` | yes | yes | yes | `none` | partial | `cards/priority_handlers.py`, `engine/effects.py` | none | `2 cards; examples: A Hallgatás Ára, Feketepiaci Sikátor` | `partially_implemented` | Enemy source-card interactions exist in a few local effects. | No generic selector or visibility rule exists for source cards. | Fold into future source target cleanup. |
| `opposing_entity` | yes | yes | yes | `none` | partial | `engine/game.py`, `cards/priority_handlers.py` | partial | `2 cards; examples: Fojtóinda, Villámszarvú Rénszarvas` | `partially_implemented` | The engine already knows the opposing lane in combat and lane-based handlers. | There is no generic canonical "entity directly across from this lane" selector. | Add a reusable opposing-lane helper; this is a cheap medium-value target improvement. |

## Summary

### Actually working

- `self`
- `own_entity`
- `enemy_entity`

### Recognized only

- `own_seals`
- `enemy_seals`
- `source_card`

### Partial

- `other_own_entity`
- `own_horizont_entity`
- `enemy_horizont_entity`
- `own_zenit_entity`
- `enemy_zenit_entity`
- `own_entities`
- `enemy_entities`
- `own_horizont_entities`
- `enemy_horizont_entities`
- `own_zenit_entities`
- `enemy_zenit_entities`
- `own_seal`
- `enemy_seal`
- `own_aeternal`
- `enemy_aeternal`
- `own_hand`
- `enemy_hand`
- `own_deck`
- `own_graveyard_entity`
- `enemy_spell`
- `enemy_spell_or_ritual`
- `enemy_hand_card`
- `own_graveyard`
- `opponent`
- `lane`
- `own_source_card`
- `enemy_source_card`
- `opposing_entity`

### Missing

- `enemy_face_down_trap`
- `own_face_down_trap`

## Best implementation order

1. `enemy_horizont_entity`
   Reason: already half-generic, heavily used, and many effects depend on it.
2. `own_horizont_entity`
   Reason: same shape as the previous one, and many buffs/protections need it.
3. `enemy_zenit_entity`
   Reason: the engine already has partial Zenit attackability rules, so this is a plausible small cleanup.
4. `other_own_entity`
   Reason: a simple `exclude_source` helper would unlock several cards cheaply.
5. `opposing_entity`
   Reason: lane knowledge already exists in combat flow, so this is a contained improvement.
6. `enemy_spell` / `enemy_spell_or_ritual`
   Reason: already proven in reaction paths, but still too local.
7. `enemy_face_down_trap` / `own_face_down_trap`
   Reason: these are the cleanest truly missing target families, but they involve hidden-information rules and are therefore not the cheapest immediate win.
