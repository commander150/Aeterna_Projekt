# Standard cleanup summary

## What was cleaned

- Loader validation now distinguishes canonical values, normalizable aliases, legacy/internal runtime names, invalid formatting, and true unknown enum values.
- Structured canonicalization was pulled back toward the spreadsheet standard for triggers, effect tags, and durations.
- Final audit outputs are now split: canonical-only compliance stays separate from alias/legacy observations.

## Latest log signal

- Latest log files inspected: `AETERNA_LOG_2026-04-10_19-17-46.txt`, `AETERNA_LOG_2026-04-10_19-17-40.txt`, `AETERNA_LOG_2026-04-10_19-17-36.txt`, `AETERNA_LOG_2026-04-10_19-16-49.txt`, `AETERNA_LOG_2026-04-10_19-15-50.txt`
- Every inspected log still reports `471` validation warnings before this cleanup pass.

## Remaining non-standard values

- Legacy/runtime-heavy: `on_play`, `on_destroyed`, `grant_attack`, `grant_hp`, `reactivate`, `until_end_of_turn`, `until_end_of_combat`.
- True standard-fidelity problems: `burst` in `Zona_Felismerve`, `trap` in `Kulcsszavak_Felismerve`, `trap` in `Idotartam_Felismerve`, `from hand` formatting in `Zona_Felismerve`.

## Warning split

- Reproduced workbook-backed triage rows from the `471` log backlog: `458`
- Remaining log-vs-workbook delta: `13`
- Alias-like or legacy-normalizable: `4`
- Real data / format problems: `48`
- Engine support gaps on standard values: `338`
- New validator warning count after cleanup rules: `145`

## Next 5 best steps

1. Clean the data rows that still use `on_play` where no safe canonical trigger exists yet, instead of letting it leak into final audits.
2. Add small runtime adapters for standard effect tags with the highest frequency: `summon`, `resource_gain`, `ability_lock`, `sacrifice`, `untargetable`.
3. Fix the clearly invalid standard-fidelity rows: zone=`burst`, keyword=`trap`, duration=`trap`, zone=`from hand`.
4. Add one shared deferred-expiry helper for `until_next_enemy_turn`, `next_own_awakening`, and `next_own_turn_start`.
5. Re-run the same latest-log comparison after the next cleanup so we can measure how much of the old `471` backlog was alias noise versus real engine debt.

## Top findings

- The latest 5 log files all repeat the same `471` validation backlog, so the problem is structural, not sample noise.
- A large part of the old `ismeretlen_ertek` noise is not actually unknown data anymore: many tokens are valid standard values whose runtime support is only partial.
- The previous loader was canonicalizing several structured fields toward runtime names; the cleanup pulls canonical storage back toward the spreadsheet standard.
- `grant_attack`/`grant_hp`/`reactivate` are now treated as legacy/runtime names behind canonical `atk_mod`/`hp_mod`/`ready`.
- `until_end_of_turn`/`until_end_of_combat` style names are now normalized toward standard `until_turn_end`/`during_combat`.
- `on_play` remains a real legacy hotspot: it is heavily used by runtime code, but it is not a final canonical trigger value in the current standard.
- Several effect tags that looked invalid under the old validator are actually standard spreadsheet values, but still need runtime adapters or explicit support.
- `burst` in zone fields and `trap` in keyword/duration fields remain true standard-fidelity problems, not just alias issues.
- The validator now distinguishes alias-normalizable values, legacy/internal values, invalid formatting, and truly unknown enum values.
- The next best wins are small adapters for standard effect tags such as `summon`, `resource_gain`, `counterspell`, and `damage_bonus`, plus data cleanup around `on_play`.