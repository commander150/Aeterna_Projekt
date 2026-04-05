# Trap Validation: Ignis / Hamvaskezű

## Rulebook Baseline

- Szabálykönyv: a Jel lapok a Zenitbe kerülnek, lefordítva.
- Szabálykönyv: egyszerre legfeljebb 2 aktív Jel lehet a Zenitben.
- Szabálykönyv: egy játékos körönként legfeljebb 2 Jelet aktiválhat.
- Szabálykönyv: a Jel kétlépcsős lapforma, külön Aktiválás és külön Hatás résszel.

## Summary

- Trap cards validated: 8
- supported: 2
- partial: 1
- uncertain: 3
- missing: 2

## Forró Talaj

- raw_ability: Aktiválás: Amikor egy ellenséges Entitás támadást indít. Hatás: A támadó Entitás azonnal elszenved 2 sebzést a harc előtt.
- activation_condition: Amikor egy ellenséges Entitás támadást indít
- effect_resolution: A támadó Entitás azonnal elszenved 2 sebzést a harc előtt.
- trigger_support: metadata trigger: on_attack_declared; engine dispatch: engine/game.py harc_fazis -> trigger_engine.dispatch('on_attack_declared'); generic combat trap consumption path bizonyitott.
- dispatch_support: generic combat trap path: engine/game.py -> can_activate_trap(...) -> EffectEngine.trigger_on_trap(...); nincs explicit kartya-handler, de a generic trap adapter aktiv.
- effect_support: supported
- evidence_files: engine/game.py; engine/effect_diagnostics_v2.py; engine/structured_effects.py; LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt
- final_status: supported
- notes:
  - A logban tenylegesen lerakva, elfogyasztva es 2 sebzest okozva latszik.
  - Nincs explicit handler, de mind az Aktiválás, mind a Hatás bizonyitott a generic trap utvonalon.
  - rulebook_basis: Jel = Aktiválás + Hatás; csak akkor supported, ha mindkettő bizonyított.
  - trigger_metadata: on_attack_declared

## Robbanó Pajzs

- raw_ability: Aktiválás: Amikor az ellenfél megtámadja egy Oltalom (Aegis) kulcsszójú Entitásodat. Hatás: A támadó Entitás azonnal elszenved 3 sebzést.
- activation_condition: Amikor az ellenfél megtámadja egy Oltalom (Aegis) kulcsszójú Entitásodat
- effect_resolution: A támadó Entitás azonnal elszenved 3 sebzést.
- trigger_support: Nincs Trigger_Felismerve metadata; az Aegis-feltetel nincs explicit preview vagy trigger-kotes ala huzva.
- dispatch_support: Csak a generic combat trap utvonal latszik, amely nem bizonyitja az Aegis-specifikus aktivalasi feltetelt.
- effect_support: uncertain
- evidence_files: engine/game.py; cards/resolver.py; LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt
- final_status: uncertain
- notes:
  - A logban a Jel lerakasa latszik, de tenyleges aktivalasi/hatas-visszaigazolas nem.
  - A kartya csak akkor lehetne supported, ha az Aegishez kotott Aktiválás is bizonyitott lenne.
  - rulebook_basis: Jel = Aktiválás + Hatás; csak akkor supported, ha mindkettő bizonyított.
  - trigger_metadata: none

## Csapda a Füstben

- raw_ability: Aktiválás: Amikor az ellenfél megidéz egy 4-es vagy magasabb Magnitúdójú Entitást. Hatás: Az újonnan megidézett Entitás azonnal Kimerült állapotba kerül.
- activation_condition: Amikor az ellenfél megidéz egy 4-es vagy magasabb Magnitúdójú Entitást
- effect_resolution: Az újonnan megidézett Entitás azonnal Kimerült állapotba kerül.
- trigger_support: Metadata trigger: on_enemy_summon; engine dispatch: engine/game.py _resolve_summon_traps; resolver SUMMON_TRAP_HANDLERS registryben benne van.
- dispatch_support: summon trap dispatch explicit: cards/resolver.py SUMMON_TRAP_HANDLERS['csapda a fustben'] -> handle_csapda_a_fustben
- effect_support: supported
- evidence_files: cards/resolver.py; cards/priority_handlers.py; engine/game.py; tests/test_priority_handlers.py; LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt
- final_status: supported
- notes:
  - A handler, a summon dispatch, a teszt es a log is egy iranyba mutat.
  - Ez a Hamvaskezű Jel-reteg legjobban bizonyitott lapja.
  - rulebook_basis: Jel = Aktiválás + Hatás; csak akkor supported, ha mindkettő bizonyított.
  - trigger_metadata: on_enemy_summon

## Hamis Parancs

- raw_ability: Aktiválás: Amikor az ellenfél sikeres támadást deklarál a Pecséted ellen. Hatás: A támadást átirányítod az ellenfél egy másik, saját maga által uralt Entitására.
- activation_condition: Amikor az ellenfél sikeres támadást deklarál a Pecséted ellen
- effect_resolution: A támadást átirányítod az ellenfél egy másik, saját maga által uralt Entitására.
- trigger_support: Nincs Trigger_Felismerve metadata es nincs explicit trap preview/trigger-kotes a Pecsét elleni tamadas atiranyitasara.
- dispatch_support: Nincs trap handler, summon trap handler vagy preview-regisztracio.
- effect_support: missing
- evidence_files: cards/resolver.py; engine/game.py; LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt
- final_status: missing
- notes:
  - A logban a Jel lerakasa latszik, de nincs runtime bizonyitek az atiranyitasra.
  - A Hatás komplex direct-seal attack redirect, amire jelenleg nincs konkret implementacio.
  - rulebook_basis: Jel = Aktiválás + Hatás; csak akkor supported, ha mindkettő bizonyított.
  - trigger_metadata: none

## Tüzes Megtorlás

- raw_ability: Aktiválás: Amikor egy saját, támadó Entitásodat az ellenfél elpusztítja Blokkolás során. Hatás: A megsemmisült Entitásod ATK-jának felét azonnal megkapja az ellenfél blokkoló Entitása mögötti Pecsét.
- activation_condition: Amikor egy saját, támadó Entitásodat az ellenfél elpusztítja Blokkolás során
- effect_resolution: A megsemmisült Entitásod ATK-jának felét azonnal megkapja az ellenfél blokkoló Entitása mögötti Pecsét.
- trigger_support: Nincs Trigger_Felismerve metadata; a blokkolas soran meghalo tamado sajat egyseg feltetele nincs explicit modellezve.
- dispatch_support: A log szerint a generic combat trap utvonal elfogyasztja, de ez nem ugyanaz, mint a szabaly szerinti Aktiválás.
- effect_support: uncertain
- evidence_files: engine/game.py; engine/effect_diagnostics_v2.py; engine/structured_effects.py; LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt
- final_status: uncertain
- notes:
  - Van logbeli aktivalas/elfogyasztas es fallback_text_resolved summary, de a hatas a logban hibasan +ATK iranyba csuszik.
  - Ez pont tipikus pelda arra, amikor van runtime zaj, de a szabalyhuseg nincs bizonyitva.
  - rulebook_basis: Jel = Aktiválás + Hatás; csak akkor supported, ha mindkettő bizonyított.
  - trigger_metadata: none

## Lángoló Visszavágás

- raw_ability: Aktiválás: Amikor az ellenfél megtámadja az egyik Entitásodat a Horizonton. Hatás: A támadó Entitás azonnal kap 4 sebzést (a harc előtt).
- activation_condition: Amikor az ellenfél megtámadja az egyik Entitásodat a Horizonton
- effect_resolution: A támadó Entitás azonnal kap 4 sebzést (a harc előtt).
- trigger_support: Nincs Trigger_Felismerve metadata es nincs explicit trap preview a sajat Horizont-entitas elleni tamadasra.
- dispatch_support: Nincs trap handler-regisztracio; legfeljebb a generic combat trap utvonal tudna probalkozni.
- effect_support: uncertain
- evidence_files: cards/resolver.py; engine/game.py; LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt
- final_status: uncertain
- notes:
  - A logban a lap lerakasa latszik, de tenyleges aktivalasi/hatas-bizonyitek nem.
  - A 4 sebzeses Hatás egyszeru lenne, de jelenleg nincs bekotve.
  - rulebook_basis: Jel = Aktiválás + Hatás; csak akkor supported, ha mindkettő bizonyított.
  - trigger_metadata: none

## Csapda a Hamuban

- raw_ability: Aktiválás: Amikor az ellenfél megidéz egy 3-as vagy magasabb Magnitúdójú Entitást a Horizontra. Hatás: Az újonnan megidézett Entitás azonnal kap 3 sebzést.
- activation_condition: Amikor az ellenfél megidéz egy 3-as vagy magasabb Magnitúdójú Entitást a Horizontra
- effect_resolution: Az újonnan megidézett Entitás azonnal kap 3 sebzést.
- trigger_support: Metadata trigger: on_enemy_summon; az engine summon dispatch utvonala biztosan letezik.
- dispatch_support: A summon trap dispatch letezik, de a kartya nincs benne a SUMMON_TRAP_HANDLERS registryben.
- effect_support: missing
- evidence_files: engine/game.py; cards/resolver.py; LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt
- final_status: partial
- notes:
  - Az Aktiválás oldala bizonyitott, de a 3 sebzeses Hatásra nincs konkret runtime vegrehajtas.
  - Ez tipikus 'trigger megvan, effect hianyzik' allapot.
  - rulebook_basis: Jel = Aktiválás + Hatás; csak akkor supported, ha mindkettő bizonyított.
  - trigger_metadata: on_enemy_summon

## Izzó Aura

- raw_ability: Aktiválás: Amikor az ellenfél Rituáléval vagy Igével célba veszi egy Hamvaskezűdet. Hatás: Semlegesíted a varázslatot, és a célba vett Entitásod kap +2 ATK-t a következő köröd végéig.
- activation_condition: Amikor az ellenfél Rituáléval vagy Igével célba veszi egy Hamvaskezűdet
- effect_resolution: Semlegesíted a varázslatot, és a célba vett Entitásod kap +2 ATK-t a következő köröd végéig.
- trigger_support: Nincs Trigger_Felismerve metadata; az enemy spell targetingre van ugyan engine event, de ez nincs ehhez a traphez kotve.
- dispatch_support: Nincs trap handler vagy spell-trap regisztracio erre a lapra.
- effect_support: missing
- evidence_files: cards/resolver.py; engine/effects.py; cards/priority_handlers.py; LOG/2026/04/AETERNA_LOG_2026-04-05_17-50-46.txt
- final_status: missing
- notes:
  - A lap szovege spell-negalast es kovetkezo korig tarto buffot ker.
  - Ehhez jelenleg nincs bizonyitott Aktiválás + Hatás par a Hamvaskezű Jel retegben.
  - rulebook_basis: Jel = Aktiválás + Hatás; csak akkor supported, ha mindkettő bizonyított.
  - trigger_metadata: none

