# Warning triage report

Baseline warning backlog from the latest logs: `471`.
Triage rows reproduced from workbook + baseline normalization rules: `458`.
Unreproduced delta against the log baseline: `13`.

## Counts by category

| category | count |
| --- | ---: |
| `unknown_enum_value` | 47 |
| `alias_normalizable` | 4 |
| `missing_explicit_blank_or_none` | 0 |
| `suspicious_field_combination` | 61 |
| `invalid_delimiter_or_format` | 1 |
| `unsupported_runtime_semantics` | 338 |
| `ambiguous_card_text` | 0 |
| `other` | 7 |

## Examples by category

### unknown_enum_value

| card_name | field | current value | why it is here | recommended fix |
| --- | --- | --- | --- | --- |
| `Gyors Nyílzápor` | `zona_felismerve` | `burst` | `burst` is not part of the final standard and has no safe canonical mapping. | Treat as data cleanup or document it as uncertain until a real canonical mapping exists. |
| `Ösztönös Kitérés` | `zona_felismerve` | `burst` | `burst` is not part of the final standard and has no safe canonical mapping. | Treat as data cleanup or document it as uncertain until a real canonical mapping exists. |
| `Vérszomj` | `zona_felismerve` | `burst` | `burst` is not part of the final standard and has no safe canonical mapping. | Treat as data cleanup or document it as uncertain until a real canonical mapping exists. |
| `Rejtett Verem` | `kulcsszavak_felismerve` | `trap` | `trap` is not part of the final standard and has no safe canonical mapping. | Treat as data cleanup or document it as uncertain until a real canonical mapping exists. |
| `Rejtett Verem` | `hatascimkek` | `trap` | `trap` is not part of the final standard and has no safe canonical mapping. | Treat as data cleanup or document it as uncertain until a real canonical mapping exists. |

### alias_normalizable

| card_name | field | current value | why it is here | recommended fix |
| --- | --- | --- | --- | --- |
| `Visszaverő Tükör` | `hatascimkek` | `reflect_damage` | `reflect_damage` can be normalized to canonical `damage_bonus`. | Normalize `reflect_damage` to `damage_bonus` in loader/reporting; keep alias only in the alias map. |
| `Megtorló Fény` | `hatascimkek` | `retaliation_damage` | `retaliation_damage` can be normalized to canonical `damage_bonus`. | Normalize `retaliation_damage` to `damage_bonus` in loader/reporting; keep alias only in the alias map. |
| `Rejtett Csapóajtó` | `hatascimkek` | `return_to_deck_bottom` | `return_to_deck_bottom` can be normalized to canonical `deck_bottom`. | Normalize `return_to_deck_bottom` to `deck_bottom` in loader/reporting; keep alias only in the alias map. |
| `Rövidzárlat` | `trigger_felismerve` | `on_ready` | `on_ready` can be normalized to canonical `on_ready_from_exhausted`. | Normalize `on_ready` to `on_ready_from_exhausted` in loader/reporting; keep alias only in the alias map. |

### missing_explicit_blank_or_none

No baseline examples fell into this category.

### suspicious_field_combination

| card_name | field | current value | why it is here | recommended fix |
| --- | --- | --- | --- | --- |
| `Hamvaskezű Újonc` | `idotartam_felismerve` | `static` | duration present without effect tag | Review the row semantics; keep the canonical value but fix the inconsistent field combination. |
| `Pokoltűz Sárkány` | `idotartam_felismerve` | `static` | duration present without effect tag | Review the row semantics; keep the canonical value but fix the inconsistent field combination. |
| `Lángszárnyú Hiéna` | `idotartam_felismerve` | `static` | duration present without effect tag | Review the row semantics; keep the canonical value but fix the inconsistent field combination. |
| `Hamuszájú Próféta` | `idotartam_felismerve` | `static` | duration present without effect tag | Review the row semantics; keep the canonical value but fix the inconsistent field combination. |
| `Parázs-Szellem` | `idotartam_felismerve` | `static` | duration present without effect tag | Review the row semantics; keep the canonical value but fix the inconsistent field combination. |

### invalid_delimiter_or_format

| card_name | field | current value | why it is here | recommended fix |
| --- | --- | --- | --- | --- |
| `Viharos Visszhang` | `zona_felismerve` | `from hand` | `from hand` looks like a format/delimiter issue instead of a valid canonical token. | Fix the cell formatting and rewrite it to a canonical standard token. |

### unsupported_runtime_semantics

| card_name | field | current value | why it is here | recommended fix |
| --- | --- | --- | --- | --- |
| `Hamvaskezű Toborzó` | `hatascimkek` | `summon` | `summon` is a standard `hatascimkek` value, but its current engine support is only `small_change_needed`. | Add or tighten runtime support for canonical `summon` without inventing a new standard value. |
| `Pokol-kutyák Ura` | `idotartam_felismerve` | `until_next_enemy_turn` | `until_next_enemy_turn` is a standard `idotartam_felismerve` value, but its current engine support is only `small_change_needed`. | Add or tighten runtime support for canonical `until_next_enemy_turn` without inventing a new standard value. |
| `Goblin Taktika` | `hatascimkek` | `summon` | `summon` is a standard `hatascimkek` value, but its current engine support is only `small_change_needed`. | Add or tighten runtime support for canonical `summon` without inventing a new standard value. |
| `Ork Csatakiáltás` | `idotartam_felismerve` | `until_next_enemy_turn` | `until_next_enemy_turn` is a standard `idotartam_felismerve` value, but its current engine support is only `small_change_needed`. | Add or tighten runtime support for canonical `until_next_enemy_turn` without inventing a new standard value. |
| `Kirobbanó Erő` | `hatascimkek` | `sacrifice` | `sacrifice` is a standard `hatascimkek` value, but its current engine support is only `small_change_needed`. | Add or tighten runtime support for canonical `sacrifice` without inventing a new standard value. |

### ambiguous_card_text

No baseline examples fell into this category.

### other

| card_name | field | current value | why it is here | recommended fix |
| --- | --- | --- | --- | --- |
| `Gyors Nyílzápor` | `trigger_felismerve` | `on_burst` | Needs manual follow-up. | Manual review. |
| `Vérszomj` | `trigger_felismerve` | `on_burst` | Needs manual follow-up. | Manual review. |
| `A Falka Dühöngése` | `trigger_felismerve` | `on_burst` | Needs manual follow-up. | Manual review. |
| `A Hajnal Katedrálisa` | `trigger_felismerve` | `on_lane_filled` | Needs manual follow-up. | Manual review. |
| `A Végtelen Temető` | `trigger_felismerve` | `on_graveyard_recursion` | Needs manual follow-up. | Manual review. |
