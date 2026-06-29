# Soft Cleanup Candidates

Ez a lista csak audit, nem torlesi utasitas.

Torles elott kotelezo bizonyitani, hogy:
- nincs import-hivatkozas
- nincs runtime-hivatkozas
- nincs tesztfugges
- nincs benne at nem emelt logika

| Fajl | Jelenlegi szerep | Mi valtja ki | Torolheto-e mar | Kockazat |
| --- | --- | --- | --- | --- |
| `xmain masolata.py` | regi/backup inditofajl | `main.py` | Nem | Magas |
| `engine/effect_diagnostics.py` | regi diagnosztikai hook | `engine/effect_diagnostics_v2.py` | Nem | Kozepes |
| `engine/game.py` | aktiv fo futasi reteg | kesobb `engine/phases.py` + `engine/combat.py` + `engine/game_state.py` | Nem | Nagyon magas |
| `engine/effects.py` | aktiv fo effektmotor | kesobb `engine/effects_core.py` + expansion handlerek | Nem | Nagyon magas |
| `engine/keywords.py` | kompatibilitasi reteg | kesobb `engine/keywords_core.py` | Nem | Magas |
| `engine/keyword_rules.py` | kompatibilitasi/re-export reteg | kesobb kozvetlen core importok | Nem | Magas |
| `engine/effects_core.py` | uj wrapper/public core entrypoint | nincs teljes atallas meg | Nem | Alacsony |
| `engine/keywords_core.py` | uj wrapper/public core entrypoint | nincs teljes atallas meg | Nem | Alacsony |
| `cards/resolver.py` | uj resolver-vaz | kesobbi lapnev -> handler mapping | Nem | Alacsony |

## Jelenlegi ellenorzesek

- `simulation/runner.py` az `engine/effect_diagnostics_v2.py`-t tolti be.
- `engine/game.py` mar hasznalja:
  - `engine.combat`
  - `engine.phases`
  - `engine.game_state`
- `xmain masolata.py` jelenleg nem latszik aktiv import-utvonalon.

## Soft cleanup kovetkezo lepesek

1. teljes import-audit a modularis atallas utan
2. deterministic simulation regresszio
3. tesztfuggesek ellenorzese
4. README/dokumentacio frissites
5. csak ezutan deprecated vagy hard cleanup
